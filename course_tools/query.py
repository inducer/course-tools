from typing import cast

from course_tools.data import Database


def limit_to_section(database: Database, section: str) -> Database:
    return Database(database.course_rules, {
        cast(str, student.network_id): student
        for student in database.students.values()
        if student.section == section
        })


def limit_to_scale(database: Database, scale: str) -> Database:
    assert database.course_rules is not None

    return Database(database.course_rules, {
        cast(str, student.network_id): student
        for student in database.students.values()
        if database.course_rules["GET_SCALE"](student) == scale
        })


def limit_to_has_section(database: Database) -> Database:
    return Database(database.course_rules, {
        cast(str, student.network_id): student
        for student in database.students.values()
        if student.section
        })


def limit_to_standing(database: Database, standing: str) -> Database:
    return Database(database.course_rules, {
        cast(str, student.network_id): student
        for student in database.students.values()
        if student.standing is not None
        and student.standing.startswith(standing)
        })
