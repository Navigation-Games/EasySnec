from __future__ import annotations

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Course:
    course_name: str
    is_score_o: bool
    stations: list[int]
