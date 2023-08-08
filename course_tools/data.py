from dataclasses import dataclass, field
from typing import List, Mapping, Optional


_no_value = object()


@dataclass
class Student:
    network_id: Optional[str]
    university_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    section: Optional[str] = None
    credit_hours: Optional[int] = None
    standing: Optional[str] = None
    csv_row: Mapping[str, Optional[float]] = field(default_factory=dict)
    roster_row: Mapping[str, str] = field(default_factory=dict)

    grade: Optional[float] = None
    rounded_grade: Optional[int] = None
    letter_grade: Optional[str] = None

    log: List[str] = field(default_factory=list)

    def set_attribute(self, name, value):
        old_value = getattr(self, name, _no_value)

        if old_value is not _no_value and old_value:
            if isinstance(value, str) and isinstance(old_value, str):
                similar = old_value.lower().strip() == value.lower().strip()
            else:
                similar = old_value == value

            if not similar:
                if name not in ["first_name", "last_name"]:
                    raise ValueError(
                        "trying to change already set "
                        "attribute '%s' of student '%s' "
                        "from '%s' to '%s'"
                        % (name, self.network_id, old_value, value))

            # unchanged
            return

        setattr(self, name, value)


class Database:
    """
    .. attribute:: students
    .. attribute:: course_rules
    """

    def __init__(self, course_rules, students=None):
        if students is None:
            self.students = {}
        else:
            self.students = students

        self.course_rules = course_rules

    def get_student(self, network_id):
        assert network_id == network_id.lower()
        return self.students.setdefault(
            network_id, Student(network_id=network_id))
