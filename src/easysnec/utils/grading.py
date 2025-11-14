from __future__ import annotations
# from pydantic.dataclasses import dataclass
from dataclasses import dataclass
from functools import cached_property
from enum import Enum
import datetime as dt

import uuid
from pyxdameraulevenshtein import damerau_levenshtein_distance
from typing import Iterable


class SuccessStatus(Enum):
    SUCCESS = 1
    INCOMPLETE = 2  # no start/finish time or start >= finish
    MISSES = 3  # or wrong order

@dataclass(frozen=True)
class InputData:
    card_id: int
    start_time: dt.datetime
    finish_time: dt.datetime
    punches: list[tuple[int, dt.datetime]]  # TODO: split into punches and times???
    reading_id: uuid.UUID # TODO: this should be generated internally, and not taken as an arg

    @classmethod
    def from_si_result(self, si_result:dict):
        # TODO: this seems like exactly the sort of thing Pydantic is well suited for
        return InputData(
            card_id = si_result['card_number'],
            start_time = si_result['start'],
            finish_time = si_result['finish'],
            punches = si_result['punches'],
            reading_id = uuid.uuid4(),
            # other keys: 'check' (datetime), 'clear' (usually None)
        )

    def get_closest_course(self, courses:Iterable[Course]):
        punch_ids = [ punch[0] for punch in self.punches ]

        # return the course most similar to what the user did, according to damerau_levenshtein
        return min(courses, key=lambda course: damerau_levenshtein_distance(punch_ids, course.stations))

    
    def score_against(self, course:Course):
        #TODO: make buffer array that helps display which stations are wrong compared to correct course 
        # See: triResultatsScore() and getMissed() in ResultatPuce.java from EasyGecNG
        punches = [ punch[0] for punch in self.punches ]

        # temp solution
        return course.stations == punches

        # actual solution
        return Grade(self, course)


@dataclass(frozen=True)
class Grade:
    input: InputData
    course: Course

    @cached_property
    def status(self) -> SuccessStatus:
        if not (self.input.finish_time and self.input.start_time):
            return SuccessStatus.INCOMPLETE
        elif self.course.stations == self.input.punches:
            return SuccessStatus.SUCCESS
        else:
            return SuccessStatus.MISSES

    @cached_property
    def missed_checkpoints(self) -> list[int]:
        if self.status is SuccessStatus.SUCCESS:
            return []
        # find missed checkpoints
        raise NotImplementedError
        
        # find missed checkpoints

        # buffer_string = ""
        # bufferBool = True
        # unsorted = True

        # while (unsorted):
        #     unsorted = False
        #     for i in range(len(punches)):
        #         if (punches[i] != punches[i + 1]):
        #             buffer_string = punches[i]
        #             punches[i] = punches[i + 1]
        #             punches[i + 1] = buffer_string
        #             unsorted = True


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
    Course('Frog',      False,  [32, 40, 39, 38, 35, 34, 36, 37, 31, 33]),
    Course('Octopus',   False,  [34, 36, 39, 40, 32, 33, 37, 38, 31, 35]),
    Course('Penguin',   False,  [38, 39, 32, 34, 35, 36, 37, 33, 31, 40]),
    Course('Sheep',     False,  [40, 36, 34, 31, 32, 33, 35, 37, 38, 39]),
    Course('Lion',      False,  [31, 33, 36, 38, 39]),
    Course('Dog',       False,  [33, 32, 40, 38, 34]),
    Course('Bee',       False,  [35, 37, 38, 40, 33]),
    Course('Bird',      False,  [36, 34, 31, 38, 37]),
    Course('Elephant',  False,  [37, 34, 31, 40, 39]),
    Course('Crab',      False,  [39, 31, 32, 35, 37]),
]

ANIMAL_MAPPING = {
    'Frog': 32,
    'Octopus': 34,
    'Penguin': 38,
    'Sheep': 40,
    'Lion': 31,
    'Dog': 33,
    'Bee': 35,
    'Bird': 36,
    'Elephant': 37,
    'Crab': 39,
}

# This isnt real lol
CURRENT_COURSE = COURSES[9] # Crab