from typing import Literal, TypeAlias

from pydantic import BaseModel

Decision: TypeAlias = Literal["CCC", "DDD"]


class Turn(BaseModel):
    game_id: int
    turn: int
    decision1: Decision
    decision2: Decision
    points1: int
    points2: int
    public_good: bool
    text1: str
    text2: str
