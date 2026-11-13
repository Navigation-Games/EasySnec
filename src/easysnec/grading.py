from __future__ import annotations

import datetime as dt
import uuid

# from pydantic.dataclasses import dataclass
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from pyxdameraulevenshtein import damerau_levenshtein_distance
from collections.abc import Iterable
from easysnec.courses import Course, ANIMAL_MAPPING, EMOJI_MAPPING

import slint


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

    def get_courses_sorted(self, courses: Iterable[Course]) -> Iterable[Course]:
        return sorted(
            courses,
            key=lambda course: damerau_levenshtein_distance(
                self.stations, course.stations
            ),
        )

    def score_against(
        self, course: Course, score_type: ScoreType = ScoreType.ANIMAL_O
    ) -> Grade:
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
        elif (
            set(self.course.stations) == set(self.input_data.stations)
            and self.score_type is ScoreType.SCORE_O
        ):
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
    def missed_checkpoints(self) -> list[int]:
        if self.status is SuccessStatus.SUCCESS:
            return []

        # TODO - make sure this is ordered correctly!
        return [
            station
            for station in self.course.stations
            if station not in self.input_data.stations
        ]
        # return [
        #     EMOJI_MAPPING.get(checkpoint, str(checkpoint))
        #     for checkpoint in missed_checkpoints
        # ]

    @cached_property
    def missed_checkpoint_indices(self) -> list[int]:
        return [
            index
            for index, station in enumerate(self.course.stations)
            if station not in self.input_data.stations
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
                        + ", ".join(map(str, self.missed_checkpoints))
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

    def to_slint(self, SlintGrade, SlintMistake, SlintMistakeType):
        mistakes = [
            SlintMistake(checkpoint=c + 1, type=SlintMistakeType.missed)
            for c in self.missed_checkpoint_indices
        ]

        if not self.input_data.start_time:
            mistakes.insert(
                0,
                SlintMistake(
                    checkpoint=-1,  # This is a hack. Type should be sufficient but for whatever reason slint is struggling to detect it
                    type=SlintMistakeType.no_start,
                ),
            )
        if not self.input_data.finish_time:
            mistakes.append(
                SlintMistake(
                    checkpoint=-2,  # This is a hack. Type should be sufficient but for whatever reason slint is struggling to detect it
                    type=SlintMistakeType.no_finish,
                )
            )

        if (
            self.status != SuccessStatus.SUCCESS
            and len(self.missed_checkpoint_indices) == 0
            and self.input_data.start_time
            and self.input_data.finish_time
        ):
            mistakes.append(SlintMistake(checkpoint=-3, type=SlintMistakeType.shuffle))

        # TODO: There ought to be some sort of mapping from slint's enums to ours
        if self.status == SuccessStatus.SUCCESS:
            status = "success"
        if self.status == SuccessStatus.INCOMPLETE:
            status = "incomplete"
        if self.status == SuccessStatus.MISSES:
            status = "misses"

        if not self.input_data.start_time or not self.input_data.finish_time:
            time_text = ""
        else:
            time_delta = self.input_data.finish_time - self.input_data.start_time
            minutes = int(time_delta.seconds / 60)
            seconds = time_delta.seconds % 60
            time_text = f"{minutes:02}:{seconds:02}"

        return SlintGrade(
            course=self.course.course_name,
            result=status,
            time=time_text,
            mistakes=slint.ListModel(mistakes),
        )


@dataclass(frozen=True)
class OutputData:
    # this is your test result - what you got right, what you got wrong
    course_name: str
    success_status: SuccessStatus
    missed_checkpoints: list[int]

