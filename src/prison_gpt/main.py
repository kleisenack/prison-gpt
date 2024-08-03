import asyncio
import pathlib
from os import getenv
from time import time
from typing import Iterable

from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from data_io import write_rounds_to_csv
from own_types import Turn, Decision

load_dotenv()
OPENAI_API_KEY = getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")

ROOT_PATH = pathlib.Path(__file__).parent.parent.resolve()


async def main():
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    turns: list[Turn] = []

    # Get the bot personalities
    personalities = []
    for i in range(8):
        with open(ROOT_PATH / "messages" / f"role-{i + 1}.md") as f:
            personalities.append(f.read())

    with open(ROOT_PATH / "messages" / "system.md") as f:
        general_system_messasge = f.read()

    system_message_bot1 = general_system_messasge.replace("{ role }", personalities[1])
    system_message_bot2 = general_system_messasge.replace("{ role }", personalities[6])

    # Asynchronously play games
    queue = asyncio.Queue()
    for game_id in range(100):
        await queue.put((system_message_bot1, system_message_bot2, game_id))

    workers = []
    for i in range(25):
        workers.append(asyncio.create_task(_worker(i, queue, client, turns)))

    await queue.join()

    for worker in workers:
        worker.cancel()

    # Write the results to a CSV file
    write_rounds_to_csv(turns, "games.csv")


async def _worker(w_id: int, queue: asyncio.Queue, client: AsyncOpenAI, turns: list[Turn]):
    while True:
        system_message_bot1, system_message_bot2, game_id = await queue.get()
        print(f"Worker {w_id} started playing game #{game_id}")
        turns += await _play_game(client, system_message_bot1, system_message_bot2, game_id)
        queue.task_done()
        print(f"Worker {w_id} finished game #{game_id}")


async def _play_game(
    client: AsyncOpenAI,
    system_message_bot1: str,
    system_message_bot2: str,
    game_id: int
) -> list[Turn]:
    turns: list[Turn] = []
    messages_from_bot1: list[str] = []
    decisions_from_bot1: list[Decision] = []
    messages_from_bot2: list[str] = []
    decisions_from_bot2: list[Decision] = []

    for i in range(4):
        # textmessage
        bot1_chat = _generate_chat(system_message_bot1, messages_from_bot1, decisions_from_bot1, messages_from_bot2,
                                   decisions_from_bot2)
        bot1_message = await _generate_completions(client, bot1_chat)

        bot2_chat = _generate_chat(system_message_bot2, messages_from_bot2, decisions_from_bot2, messages_from_bot1,
                                   decisions_from_bot1)
        bot2_message = await _generate_completions(client, bot2_chat)

        messages_from_bot1.append(bot1_message["content"])
        messages_from_bot2.append(bot2_message["content"])

        # decision
        bot1_chat = _generate_chat(system_message_bot1, messages_from_bot1, decisions_from_bot1, messages_from_bot2,
                                   decisions_from_bot2)
        bot1_decision_message = (await _generate_completions(client, bot1_chat))["content"]
        if "C" in bot1_decision_message:
            bot1_decision = "CCC"
        elif "D" in bot1_decision_message:
            bot1_decision = "DDD"
        else:
            raise ValueError(f"Invalid decision: {bot1_decision_message}")

        bot2_chat = _generate_chat(system_message_bot2, messages_from_bot2, decisions_from_bot2, messages_from_bot1,
                                   decisions_from_bot1)
        bot2_decision_message = (await _generate_completions(client, bot2_chat))["content"]
        if "C" in bot2_decision_message:
            bot2_decision = "CCC"
        elif "D" in bot2_decision_message:
            bot2_decision = "DDD"
        else:
            raise ValueError(f"Invalid decision: {bot2_decision_message}")

        decisions_from_bot1.append(bot1_decision)
        decisions_from_bot2.append(bot2_decision)

        # tracking result
        bot1_points, bot2_points = _game_matrix(decisions_from_bot1[i], decisions_from_bot2[i])
        turns.append(Turn(
            game_id=game_id,
            turn=i,
            text1=messages_from_bot1[i],
            text2=messages_from_bot2[i],
            decision1=decisions_from_bot1[i],
            decision2=decisions_from_bot2[i],
            points1=bot1_points,
            points2=bot2_points,
            public_good=(bot1_points == 3 and bot2_points == 3),
        ))

    return turns


def _generate_chat(
    system_message: str,
    me_bot_messages: list[str],
    me_bot_decisions: list[Decision],
    you_bot_messages: list[str],
    you_bot_decisions: list[Decision],
) -> list[ChatCompletionMessageParam]:
    with open(ROOT_PATH / "messages" / "message_instruction_forget.md") as f:
        message_instruction_forget = f.read()
    with open(ROOT_PATH / "messages" / "decision_instruction_forget.md") as f:
        decision_instruction_forget = f.read()
    with open(ROOT_PATH / "messages" / "message_instruction_keep.md") as f:
        message_instruction_keep = f.read()

    chat: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": system_message,
        },
    ]

    i = 0
    while True:
        # Messages
        if i < len(me_bot_messages):
            chat.append({"role": "assistant", "content": me_bot_messages[i]})
            chat.append(
                {"role": "user", "content": message_instruction_keep.replace("[ message ]", you_bot_messages[i])})

        # Decisions
        if i < len(me_bot_decisions):
            chat.append({"role": "assistant", "content": me_bot_decisions[i]})
            chat.append({"role": "user", "content": _game_feedback(me_bot_decisions[i], you_bot_decisions[i])})

        i += 1
        if i >= len(me_bot_messages) and i >= len(me_bot_decisions):
            break

    if len(me_bot_messages) > len(me_bot_decisions):
        chat.append({"role": "user", "content": decision_instruction_forget})
    else:
        chat.append({"role": "user", "content": message_instruction_forget})

    return chat


def _game_feedback(me_bot_decision: Decision, you_bot_decision: Decision) -> str:
    with open(ROOT_PATH / "messages" / "decision_instruction_keep.md") as f:
        decision_instruction_keep = f.read()

    decision_instruction_keep = decision_instruction_keep.replace("[me_decision]", me_bot_decision)
    decision_instruction_keep = decision_instruction_keep.replace("[you_decision]", you_bot_decision)

    me_bot_points, _ = _game_matrix(me_bot_decision, you_bot_decision)
    return decision_instruction_keep.replace("[me_points]", str(me_bot_points))


def _game_matrix(bot1_decision: Decision, bot2_decision: Decision) -> tuple[int, int]:
    if "CCC" in bot1_decision and "CCC" in bot2_decision:
        return 3, 3
    if "DDD" in bot1_decision and "DDD" in bot2_decision:
        return 2, 2
    if "DDD" in bot1_decision and "CCC" in bot2_decision:
        return 4, 1
    if "CCC" in bot1_decision and "DDD" in bot2_decision:
        return 1, 4

    raise ValueError(f"Invalid decision: {bot1_decision} | {bot2_decision}")


async def _generate_completions(client: AsyncOpenAI, chat: Iterable[ChatCompletionMessageParam]) -> dict:
    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=chat
    )
    message = completion.choices[0].message

    return {"role": message.role, "content": message.content}


if __name__ == "__main__":
    start_time = time()
    asyncio.run(main())
    print((time() - start_time) / 60)
