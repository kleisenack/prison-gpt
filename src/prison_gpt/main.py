from os import getenv
import pathlib
from typing import Literal
from time import time

from dotenv import load_dotenv
from openai import OpenAI
from beartype import beartype

from data_io import Turn, write_rounds_to_csv


load_dotenv()
OPENAI_API_KEY = getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")


ROOT_PATH = pathlib.Path(__file__).parent.parent.resolve()


@beartype
def main():
    client = OpenAI(api_key=OPENAI_API_KEY)

    turns: list[Turn] = []

    personalities = []
    for i in range(7):
        with open(ROOT_PATH / "messages" / f"role-{i+1}.md") as f:
            personalities.append(f.read())

    with open(ROOT_PATH / "messages" / "system.md") as f:
        general_system_messasge = f.read()

    system_message_bot1 = general_system_messasge.replace("{ role }", personalities[3])
    system_message_bot2 = general_system_messasge.replace("{ role }", personalities[6])

    for games_number in range(100):
        messages_from_bot1: list[str] = []
        messages_from_bot2: list[str] = []

        for i in range(4):
            print("#", games_number)

            # textmessage
            bot1_chat = _generate_chat(system_message_bot1, messages_from_bot1, messages_from_bot2)
            bot1_message = _generate_completions(client, bot1_chat)

            bot2_chat = _generate_chat(system_message_bot2, messages_from_bot2, messages_from_bot1)
            bot2_message = _generate_completions(client, bot2_chat)

            messages_from_bot1.append(bot1_message["content"])
            messages_from_bot2.append(bot2_message["content"])

            # decision
            bot1_chat = _generate_chat(system_message_bot1, messages_from_bot1, messages_from_bot2)
            bot1_message = _generate_completions(client, bot1_chat)
            if "C" in bot1_message:
                bot1_message = "CCC"
            if "D" in bot1_message:
                bot1_message = "DDD"

            bot2_chat = _generate_chat(system_message_bot2, messages_from_bot2, messages_from_bot1)
            bot2_message = _generate_completions(client, bot2_chat)
            if "C" in bot2_message:
                bot2_message = "CCC"
            if "D" in bot2_message:
                bot2_message = "DDD"

            messages_from_bot1.append(bot1_message["content"])
            messages_from_bot2.append(bot2_message["content"])

            # tracking result
            bot1_points, bot2_points = _game_matrix(messages_from_bot1[2*i+1], messages_from_bot2[2*i+1])
            turns.append(Turn(
                game_id=games_number,
                turn=i,
                text1=messages_from_bot1[2*i],
                text2=messages_from_bot2[2*i],
                decision1=messages_from_bot1[2*i+1],
                decision2=messages_from_bot2[2*i+1],
                points1=bot1_points,
                points2=bot2_points,
                public_good=(bot1_points == 3 and bot2_points == 3),
            ))

    write_rounds_to_csv(turns, "games.csv")


@beartype
def _generate_chat(system_message: str, me_bot_messages: list[str], you_bot_messages: list[str]) -> list[dict[str, str]]:
    with open(ROOT_PATH / "messages" / "message_instruction_forget.md") as f:
        message_instruction_forget = f.read()
    with open(ROOT_PATH / "messages" / "decision_instruction_forget.md") as f:
        decision_instruction_forget = f.read()
    with open(ROOT_PATH / "messages" / "message_instruction_keep.md") as f:
        message_instruction_keep = f.read()

    chat: list[dict[str, str]] = [
        {
            "role": "system",
            "content": system_message,
        },
    ]

    for i in range(0, len(me_bot_messages)-1, 2):
        # Message
        chat.append({"role": "assistant", "content": me_bot_messages[i]})
        chat.append({"role": "user", "content": message_instruction_keep.replace("[ message ]", you_bot_messages[i])})

        # Decision
        if i == len(me_bot_messages) - 1:
            break
        chat.append({"role": "assistant", "content": me_bot_messages[i+1]})
        chat.append({"role": "user", "content": _game_feedback(me_bot_messages[i+1], you_bot_messages[i+1])})

    if len(me_bot_messages) % 2 == 1:
        chat.append({"role": "user", "content": decision_instruction_forget})
    else:
        chat.append({"role": "user", "content": message_instruction_forget})

    return chat


def _game_feedback(me_bot_message: str, you_bot_message: str) -> str:
    with open(ROOT_PATH / "messages" / "decision_instruction_keep.md") as f:
        decision_instruction_keep = f.read()

    decision_instruction_keep = decision_instruction_keep.replace("[me_decision]", me_bot_message)
    decision_instruction_keep = decision_instruction_keep.replace("[you_decision]", you_bot_message)

    me_bot_points, _ = _game_matrix(me_bot_message, you_bot_message)
    return decision_instruction_keep.replace("[me_points]", str(me_bot_points))


def _game_matrix(bot1_decision: Literal["CCC", "DDD"], bot2_decision: Literal["CCC", "DDD"]) -> tuple[int, int]:
    if "CCC" in bot1_decision and "CCC" in bot2_decision:
        return 3, 3
    if "DDD" in bot1_decision and "DDD" in bot2_decision:
        return 2, 2
    if "DDD" in bot1_decision and "CCC" in bot2_decision:
        return 4, 1
    if "CCC" in bot1_decision and "DDD" in bot2_decision:
        return 1, 4

    raise ValueError(f"Invalid decision: {bot1_decision} | {bot2_decision}")


@beartype
def _generate_completions(client: OpenAI, chat: list[dict[str, str]]) -> dict:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=chat
    )
    message = completion.choices[0].message

    return {"role": message.role, "content": message.content}


@beartype
def _nice_chat_print(chat: list[dict]):
    for messsage in chat:
        print(f"{messsage['role'].upper()}:")
        print(messsage["content"], end="\n\n")


if __name__ == "__main__":
    start_time = time()
    main()
    print((time()-start_time) / 60)

