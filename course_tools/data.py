from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Mapping


_no_value = object()


@dataclass
class Student:
    network_id: str | None
    university_id: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    section: str | None = None
    credit_hours: int | None = None
    standing: str | None = None
    csv_row: Mapping[str, float | None] = field(default_factory=dict)
    roster_row: Mapping[str, str] = field(default_factory=dict)

    grade: float | None = None
    rounded_grade: int | None = None
    letter_grade: str | None = None

    log: list[str] = field(default_factory=list)

    def set_attribute(self, name, value):
        old_value = getattr(self, name, _no_value)

        if old_value is not _no_value and old_value:
            if isinstance(value, str) and isinstance(old_value, str):
                similar = old_value.lower().strip() == value.lower().strip()
            else:
                similar = old_value == value

            if not similar and name not in ["first_name", "last_name"]:
                raise ValueError(
                    "trying to change already set "
                    "attribute '%s' of student '%s' "
                    "from '%s' to '%s'"
                    % (name, self.network_id, old_value, value))

            # unchanged
            return

        setattr(self, name, value)


@dataclass
class Database:
    """
    .. attribute:: students
    .. attribute:: course_rules
    """

    course_rules: dict | None = None
    students: dict[str, Student] = field(default_factory=dict)

    def get_student(self, network_id):
        assert network_id == network_id.lower()
        return self.students.setdefault(
            network_id, Student(network_id=network_id))
