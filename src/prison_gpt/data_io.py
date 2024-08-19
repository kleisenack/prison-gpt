import csv
from pathlib import Path

from own_types import Turn


def write_rounds_to_csv(turns: list[Turn], path: Path):
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
