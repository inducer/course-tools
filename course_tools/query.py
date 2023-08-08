from course_tools.data import Database


def limit_to_section(database: Database, section: str) -> Database:
    new_students = {}
    for student in database.students.values():
        if student.section == section:
            new_students[student.network_id] = student

    return Database(database.course_rules, new_students)


def limit_to_scale(database: Database, scale: str) -> Database:
    new_students = {}
    for student in database.students.values():
        student_scale = database.course_rules["GET_SCALE"](student)
        if student_scale == scale:
            new_students[student.network_id] = student

    return Database(database.course_rules, new_students)


def limit_to_has_section(database: Database) -> Database:
    new_students = {}
    for student in database.students.values():
        if student.section:
            new_students[student.network_id] = student

    return Database(database.course_rules, new_students)
