from __future__ import annotations

from enum import Enum

from pydantic.dataclasses import dataclass


class SuccessStatus(Enum):
    SUCCESS = 1
    INCOMPLETE = 2  # no start/finish time or start >= finish
    MISSES = 3  # or wrong order


@dataclass(frozen=True)
class OutputData:
    course_name: str
    success_status: SuccessStatus
    missed_checkpoints: list[int]
