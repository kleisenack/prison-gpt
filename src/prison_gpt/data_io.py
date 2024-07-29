import csv
from typing import Literal

from pydantic import BaseModel


class Turn(BaseModel):
    game_id: int
    turn: int
    text1: str
    text2: str
    decision1: Literal["CCC", "DDD"]
    decision2: Literal["CCC", "DDD"]
    points1: int
    points2: int
    public_good: bool


def write_rounds_to_csv(turns: list[Turn], path: str):
    with open(path, "w", newline="", encoding='utf-8') as f:
        writer = csv.DictWriter(f, delimiter=";", fieldnames=Turn.__fields__)
        writer.writeheader()
        writer.writerows([dict(turn) for turn in turns])


if __name__ == "__main__":
    rounds = [
        Turn(
            game_id=1,
            turn=1,
            text1="text1",
            text2="text2",
            decision1="C",
            decision2="D",
            points1=1,
            points2=2,
            public_good=True,
        ),
        Turn(
            game_id=1,
            turn=1,
            text1="text1",
            text2="text2",
            decision1="C",
            decision2="D",
            points1=1,
            points2=2,
            public_good=True,
        )
    ]
    write_rounds_to_csv(rounds, "test.csv")
