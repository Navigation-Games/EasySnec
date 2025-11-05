from __future__ import annotations

import datetime as dt

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class InputData:
    card_id: int
    start_time: dt.datetime
    finish_time: dt.datetime
    punches: list[tuple[int, dt.datetime]]
    reading_id: str
