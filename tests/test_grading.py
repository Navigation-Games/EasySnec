from __future__ import annotations
from easysnec.utils.grading import InputData, Grade, COURSES, OutputData, SuccessStatus, ScoreType, typed_function



def test_correct_score_o(example_course, example_input_success):
    grade = Grade(example_input_success, example_course, ScoreType.SCORE_O)

    assert (grade.status is SuccessStatus.SUCCESS)

    assert (grade.score is 3)