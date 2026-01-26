from __future__ import annotations

from typing import TYPE_CHECKING

from .grade_tools import format_frac


if TYPE_CHECKING:
    from collections.abc import Callable

    from .data import Database, Student


def make_letter_grade(database: Database, student: Student,
                      add_log: Callable[[int | float, str], None]) -> str | None:
    if student.grade is None:
        return None

    assert database.course_rules is not None

    letters = database.course_rules["LETTER_GRADES"]
    letter = letters[-1]

    scale_name = database.course_rules["GET_SCALE"](student)

    add_log(0, "Scale: %s" % scale_name)

    grade = 100*student.grade
    rounded_grade = round(grade)

    cutoffs = database.course_rules["SCALE_CUTOFFS"][scale_name]

    for potential_letter, cutoff in zip(letters, cutoffs, strict=False):
        if cutoff > rounded_grade >= cutoff-1:
            add_log(5, "Close call: %s (has: %s -> %s, cutoff: %s)"
                    % (potential_letter, format_frac(student.grade),
                        rounded_grade, cutoff))
        if rounded_grade >= cutoff:
            letter = potential_letter
            break

    override = database.course_rules.get("OVERRIDE_LETTER_GRADE")
    if override is not None:
        letter = override(student, grade, rounded_grade, letter, add_log)

    return letter
