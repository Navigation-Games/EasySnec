from __future__ import annotations
import datetime as dt
from easysnec.utils.grading import InputData, Grade, Course, SuccessStatus, ScoreType
import uuid
import pytest


def generate_input_from_station_list(stations):
    dates = [
        dt.datetime(2025, 3, 14, 9, 37, 2),
        dt.datetime(2025, 3, 14, 9, 57, 8),
        dt.datetime(2025, 3, 14, 10, 9, 44),
        dt.datetime(2025, 3, 14, 10, 10, 44),
        dt.datetime(2025, 3, 14, 10, 11, 44),
        dt.datetime(2025, 3, 14, 10, 12, 44),
        dt.datetime(2025, 3, 14, 10, 13, 44),
        dt.datetime(2025, 3, 14, 10, 14, 44),
        dt.datetime(2025, 3, 14, 10, 15, 44),
        dt.datetime(2025, 3, 14, 10, 16, 44),
        dt.datetime(2025, 3, 14, 10, 17, 44),
        dt.datetime(2025, 3, 14, 10, 18, 44),
        dt.datetime(2025, 3, 14, 10, 19, 44),
        dt.datetime(2025, 3, 14, 10, 20, 44),
        dt.datetime(2025, 3, 14, 10, 21, 44),
    ]

    punches = [(station, dates[i]) for i, station in enumerate(stations)]

    return InputData(
        card_id=123,
        start_time=dt.datetime(2025, 3, 14, 9, 30, 17),
        finish_time=dt.datetime(2025, 3, 14, 10, 22, 47),
        punches=punches,
        reading_id=uuid.uuid4(),
    )


def test_get_closest_course():
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

    def assert_helper(list):
        return (
            generate_input_from_station_list(list).get_closest_course(COURSES)
            == COURSES[9]
        )

    assert assert_helper([39, 31, 32, 35, 37])
    assert assert_helper([39, 31, 32, 35, 36])
    assert assert_helper([39, 31, 2001, 35, 37])
    assert assert_helper([39, 32, 35, 37])
    assert assert_helper([39, 31, 32, 35, 37])
    assert assert_helper([38, 31, 32, 36, 37])
    assert not assert_helper([40, 36, 34, 31, 32, 33, 35, 37, 38, 39])


@pytest.mark.xfail
def test_classic_o():
    _course = [1, 2, 3, 4, 5, 6]

    # TODO: (input, expected score)?
    _cases = [
        [1, 2, 3, 4, 5, 6],  # -> time
        [1, 2, 3, 4, 5],  # -> 0
        [1, 2, 3, 4, 5, "5"],  # -> 0
        [1, 2, 4, 3, 5, 6],  # -> 0
        [6, 5, 4, 3, 2, 1],  # -> 0
        [1, 3, 2, 6, 7, 4, 5],  # -> 0
        [2, 3, 4, 5, 6],  # -> 0
        [3, 2, 6, 4, 5, 1][6],  # -> 0  # -> 0
        [],  # -> 0
        [8],  # -> 0
        [2, 2, 2, 2, 2, 2, 2],  # -> 0
    ]

    raise NotImplementedError()


@pytest.mark.xfail
def test_score_o():
    _course = [1, 2, 3, 4, 5, 6]

    # TODO: (input, expected score)?
    _cases = [
        [1, 2, 3, 4, 5, 6],  # -> 6
        [1, 2, 3, 4, 5],  # -> 5
        [1, 2, 3, 4, 5, 5],  # -> 5
        [1, 2, 4, 3, 5, 6],  # -> 6
        [6, 5, 4, 3, 2, 1],  # -> 6
        [1, 3, 2, 6, 7, 4, 5],  # -> 6
        [2, 3, 4, 5, 6],  # -> 5
        [3, 2, 6, 4, 5, 1][6],  # -> 6  # -> 1
        [],  # -> 0
        [8],  # -> 0
        [2, 2, 2, 2, 2, 2, 2],  # -> 1
    ]
    raise NotImplementedError()


def test_correct(example_course, example_input_success):
    grade = Grade(example_input_success, example_course, ScoreType.SCORE_O)

    assert grade.status == SuccessStatus.SUCCESS


def test_missing(example_course, example_input_misses):
    grade = Grade(example_input_misses, example_course, ScoreType.SCORE_O)

    assert grade.status == SuccessStatus.MISSES


def test_incomplete(example_course, example_input_incomplete):
    grade = Grade(example_input_incomplete, example_course, ScoreType.SCORE_O)

    assert grade.status == SuccessStatus.INCOMPLETE


def test_no_start(example_course, example_input_no_start):
    grade = Grade(example_input_no_start, example_course, ScoreType.SCORE_O)

    assert grade.status == SuccessStatus.INCOMPLETE


def test_no_finish(example_course, example_input_no_finish):
    grade = Grade(example_input_no_finish, example_course, ScoreType.SCORE_O)

    assert grade.status == SuccessStatus.INCOMPLETE
