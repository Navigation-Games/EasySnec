from __future__ import annotations

import datetime as dt

import pytest

from easysnec.utils.grading import Course
from easysnec.utils.grading import InputData
from easysnec.utils.grading import OutputData, SuccessStatus
import uuid


@pytest.fixture
def example_course() -> Course:
    return Course(
        course_name="tutorial-O",
        is_score_o=False,
        stations=[42, 43, 49],
    )


@pytest.fixture
def example_input_success(example_course: Course) -> InputData:
    start = dt.datetime(2025, 3, 14, 9, 30, 17)
    finish = dt.datetime(2025, 3, 14, 10, 22, 47)
    punches = [
        (42, dt.datetime(2025, 3, 14, 9, 37, 2)),
        (43, dt.datetime(2025, 3, 14, 9, 57, 8)),
        (49, dt.datetime(2025, 3, 14, 10, 9, 44)),
    ]
    return InputData(
        card_id=123,
        start_time=start,
        finish_time=finish,
        punches=punches,
        reading_id=uuid.uuid4()
        # "202503140930170000000123",
    )


@pytest.fixture
def example_output_success(example_course: Course) -> OutputData:
    return OutputData(
        course_name=example_course.course_name,
        success_status=SuccessStatus.SUCCESS,
        missed_checkpoints=[],
    )


@pytest.fixture
def example_input_incomplete(example_course: Course) -> InputData:
    start = dt.datetime(2025, 3, 14, 9, 30, 17)
    finish = dt.datetime.min  # finish time precedes start time
    punches = [
        (42, dt.datetime(2025, 3, 14, 9, 37, 2)),
        (43, dt.datetime(2025, 3, 14, 9, 57, 8)),
        (49, dt.datetime(2025, 3, 14, 10, 9, 44)),
    ]
    return InputData(
        card_id=123,
        start_time=start,
        finish_time=finish,
        punches=punches,
        reading_id=uuid.uuid4()
        # reading_id="202503140930170000000123",
    )


@pytest.fixture
def example_output_incomplete(example_course: Course) -> OutputData:
    return OutputData(
        course_name=example_course.course_name,
        success_status=SuccessStatus.INCOMPLETE,
        missed_checkpoints=[],
    )


@pytest.fixture
def example_input_misses(example_course: Course) -> InputData:
    start = dt.datetime(2025, 3, 14, 9, 30, 17)
    finish = dt.datetime(2025, 3, 14, 10, 22, 47)
    punches = [
        (43, dt.datetime(2025, 3, 14, 9, 57, 8)),
        (42, dt.datetime(2025, 3, 14, 9, 37, 2)),  # out of order
    ]
    return InputData(
        card_id=123,
        start_time=start,
        finish_time=finish,
        punches=punches,
        reading_id=uuid.uuid4()
        # reading_id="202503140930170000000123",
    )


@pytest.fixture
def example_output_misses(example_course: Course) -> OutputData:
    return OutputData(
        course_name=example_course.course_name,
        success_status=SuccessStatus.MISSES,
        missed_checkpoints=[42, 49],
    )


@pytest.fixture
def example_input_wrong_order(example_course: Course) -> InputData:
    start = dt.datetime(2025, 3, 14, 9, 30, 17)
    finish = dt.datetime(2025, 3, 14, 10, 22, 47)
    punches = [
        (49, dt.datetime(2025, 3, 14, 10, 9, 44)),
        (42, dt.datetime(2025, 3, 14, 9, 37, 2)),
        (43, dt.datetime(2025, 3, 14, 9, 57, 8)),
    ]
    return InputData(
        card_id=123,
        start_time=start,
        finish_time=finish,
        punches=punches,
        reading_id=uuid.uuid4()
        # reading_id="202503140930170000000123",
    )


@pytest.fixture
def example_output_wrong_order(example_course: Course) -> OutputData:
    return OutputData(
        course_name=example_course.course_name,
        success_status=SuccessStatus.MISSES,
        missed_checkpoints=[49],
    )


@pytest.fixture
def example_input_not_started(example_course: Course) -> InputData:
    start = dt.datetime.max  # after the finish time
    finish = dt.datetime(2025, 3, 14, 10, 22, 47)
    punches = [
        (42, dt.datetime(2025, 3, 14, 9, 37, 2)),
        (43, dt.datetime(2025, 3, 14, 9, 57, 8)),
        (49, dt.datetime(2025, 3, 14, 10, 9, 44)),
    ]
    return InputData(
        card_id=123,
        start_time=start,
        finish_time=finish,
        punches=punches,
        reading_id=uuid.uuid4()
        # reading_id="202503140930170000000123",
    )


@pytest.fixture
def example_output_not_started(example_course: Course) -> OutputData:
    return OutputData(
        course_name=example_course.course_name,
        success_status=SuccessStatus.INCOMPLETE,
        missed_checkpoints=[],
    )
