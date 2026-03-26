from __future__ import annotations

import datetime as dt
import uuid

# from pydantic.dataclasses import dataclass
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from pyxdameraulevenshtein import damerau_levenshtein_distance
from collections.abc import Iterable


def typed_function(a: int, b: str, c: bool) -> None:
    print(a, b, c)


class SuccessStatus(Enum):
    SUCCESS = 1
    INCOMPLETE = 2  # no start/finish time or start >= finish
    MISSES = 3  # or wrong order


class ScoreType(Enum):
    SCORE_O = 1
    CLASSIC_O = 2
    ANIMAL_O = 3


@dataclass(frozen=True)
class InputData:
    card_id: int
    start_time: dt.datetime | None
    finish_time: dt.datetime | None
    punches: list[tuple[int, dt.datetime]]  # TODO: split into punches and times???
    reading_id: (
        uuid.UUID
    )  # TODO: this should be generated internally, and not taken as an arg

    @classmethod
    def from_si_result(self, si_result: dict) -> InputData:
        # TODO: this seems like exactly the sort of thing Pydantic is well suited for
        return InputData(
            card_id=si_result["card_number"],
            start_time=si_result["start"],
            finish_time=si_result["finish"],
            punches=si_result["punches"],
            reading_id=uuid.uuid4(),
            # other keys: 'check' (datetime), 'clear' (usually None)
        )

    @cached_property
    def stations(self) -> list[int]:
        return [punch[0] for punch in self.punches]

    def get_closest_course(self, courses: Iterable[Course]) -> Course:
        # return the course most similar to what the user did, according to damerau_levenshtein
        return min(
            courses,
            key=lambda course: damerau_levenshtein_distance(
                self.stations, course.stations
            ),
        )

    def score_against(self, course: Course, score_type: ScoreType = ScoreType.ANIMAL_O):
        return Grade(self, course, score_type)


@dataclass(frozen=True)
class Grade:
    input_data: InputData
    course: Course
    score_type: ScoreType

    @cached_property
    def status(self) -> SuccessStatus:
        if (
            not (self.input_data.finish_time and self.input_data.start_time)
            or self.input_data.finish_time < self.input_data.start_time
        ):
            return SuccessStatus.INCOMPLETE
        elif self.course.stations == self.input_data.stations:
            return SuccessStatus.SUCCESS
        else:
            return SuccessStatus.MISSES

    @cached_property
    def score(self) -> float:
        if self.status is SuccessStatus.INCOMPLETE:
            return 0

        match self.score_type:
            case ScoreType.SCORE_O:
                # return the number of visited stations that are also in the course description
                return len(
                    set(self.course.stations).intersection(
                        set(self.input_data.stations)
                    )
                )
            case ScoreType.CLASSIC_O | ScoreType.ANIMAL_O:
                # we care about order. Score is time if you did the course correctly, else 0
                if self.course.stations == self.input_data.stations:
                    d = self.input_data
                    assert d.finish_time is not None and d.start_time is not None
                    return 1 / (d.finish_time - d.start_time).seconds
                else:
                    # TODO: see triResultatsScore() and getMissed() in ResultatPuce.java from EasyGecNG
                    return 0

        raise ValueError(f"I don't know how to score {self.score_type}")

    @cached_property
    def missed_checkpoints(self) -> list[str]:
        if self.status is SuccessStatus.SUCCESS:
            return []
        missed_checkpoints = [
            station
            for station in self.course.stations
            if station not in self.input_data.stations
        ]
        return [
            EMOJI_MAPPING.get(checkpoint, str(checkpoint))
            for checkpoint in missed_checkpoints
        ]

    @cached_property
    def extra_checkpoints(self) -> list[str]:
        if self.status is SuccessStatus.SUCCESS:
            return []
        extra_checkpoints = [
            station
            for station in self.input_data.stations
            if station not in self.course.stations
        ]
        return [
            EMOJI_MAPPING.get(checkpoint, str(checkpoint))
            for checkpoint in extra_checkpoints
        ]

    @cached_property
    def scoring_output(self) -> str:
        match self.status:
            case SuccessStatus.SUCCESS:
                scoring_output = ""
            case SuccessStatus.MISSES:
                scoring_output = ""
                if self.missed_checkpoints:
                    scoring_output += (
                        "Missing checkpoints: "
                        + ", ".join(self.missed_checkpoints)
                        + "\n"
                    )
                if self.extra_checkpoints:
                    scoring_output += "Extra checkpoints: " + ", ".join(
                        self.extra_checkpoints
                    )
            case SuccessStatus.INCOMPLETE:
                scoring_output = "Missing start or finish checkpoint!"
            case _:
                scoring_output = ""

        return scoring_output


@dataclass(frozen=True)
class OutputData:
    # this is your test result - what you got right, what you got wrong
    course_name: str
    success_status: SuccessStatus
    missed_checkpoints: list[int]


@dataclass(frozen=True)
class Course:
    course_name: str
    is_score_o: bool
    stations: list[int]


COURSES = [
    Course("Frog", False, [32, 40, 39, 38, 35, 34, 36, 37, 31, 33]),
    Course("Octopus", False, [34, 36, 39, 40, 32, 33, 37, 38, 31, 35]),
    Course("Penguin", False, [38, 39, 32, 34, 35, 36, 37, 33, 31, 40]),
    Course("Sheep", False, [40, 36, 34, 31, 32, 33, 35, 37, 38, 39]),
    Course("Lion", False, [31, 33, 36, 38, 39]),
    Course("Dog", False, [33, 32, 40, 38, 34]),
    Course("Bee", False, [35, 37, 38, 40, 33]),
    Course("Bird", False, [36, 34, 31, 38, 37]),
    Course("Elephant", False, [37, 34, 31, 40, 39]),
    Course("Crab", False, [39, 31, 32, 35, 37]),
]

ANIMAL_MAPPING = {
    "Frog": 32,
    "Octopus": 34,
    "Penguin": 38,
    "Sheep": 40,
    "Lion": 31,
    "Dog": 33,
    "Bee": 35,
    "Bird": 36,
    "Elephant": 37,
    "Crab": 39,
}

EMOJI_MAPPING = {
    32: "🐸",
    34: "🐙",
    38: "🐧",
    40: "🐑",
    31: "🦁",
    33: "🐕",
    35: "🐝",
    36: "🐦",
    37: "🐘",
    39: "🦀",
}

CURRENT_COURSE = COURSES[9]  # Crab
