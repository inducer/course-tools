from __future__ import annotations

import pathlib

import typed_argparse as tap

from . import input as inp, output as out, query as qry
from .data import Database
from .grade import make_letter_grade


class Args(tap.TypedArgs):
    moodle_csv: list[str] | None = tap.arg(metavar="CSV", nargs="*", default=None)
    relate_csv: list[str] | None = tap.arg(metavar="CSV", nargs="*", default=None)
    my_cs_html_roster: list[str] | None = tap.arg(
        metavar="HTML", nargs="*", default=None)
    course_rules: str | None = tap.arg(metavar="RULES_PY", default=None)
    warn_level: int = tap.arg("-w", default=4)
    limit_to_section: list[str] = tap.arg(metavar="SECTION", nargs="+", default=[])
    limit_to_scale: str | None = tap.arg(metavar="SCALE", default=None)
    limit_to_standing: str | None = tap.arg(metavar="STANDING", default=None)
    print_scales: bool = tap.arg(default=False)
    print_grade_list: bool = tap.arg("-g", default=False)
    print_student_report: str | None = tap.arg("-s", metavar="NETWORK_ID", default=None)
    print_letter_histogram: bool = tap.arg(default=False)
    plot_histogram: bool = tap.arg(default=False)
    histogram_undiff: bool = tap.arg(default=False)
    print_emails: bool = tap.arg(default=False)
    print_roster_csv: bool = tap.arg(default=False)
    email_suffix: str = tap.arg(default="@illinois.edu")
    print_banner_csv: bool = tap.arg(default=False)
    update_banner_xlsx: str | None = tap.arg(metavar="FILENAME", default=None)
    print_relate_csv: bool = tap.arg(default=False)
    print_preliminary_relate_csv: bool = tap.arg(default=False)
    print_relate_not_in_roster_query: bool = tap.arg(default=False)
    print_warnings: bool = tap.arg(default=False)
    print_random_group_csv: bool = tap.arg(default=False)
    random_group_size: int = tap.arg(default=6)
    remove_students_without_section: bool = tap.arg(default=False)


def main():
    # {{{ frontend

    args = tap.Parser(Args).parse_args()

    if args.course_rules is None:
        raise RuntimeError("course rules module needed")

    course_rules = {}
    rules_file_contents = pathlib.Path(args.course_rules).read_text()

    exec(compile(rules_file_contents, args.course_rules, "exec"), course_rules)  # noqa: S102

    database = Database(course_rules)

    if args.moodle_csv:
        for csv_name in args.moodle_csv:
            inp.read_moodle_csv(database, csv_name)

    if args.relate_csv:
        for csv_name in args.relate_csv:
            inp.read_relate_csv(database, csv_name)

    if args.my_cs_html_roster:
        for html_name in args.my_cs_html_roster:
            inp.read_my_engr_html_roster(database, html_name)

    # }}}

    if args.print_scales:
        out.print_scales(database)

    if args.remove_students_without_section:
        database = qry.limit_to_has_section(database)

    if args.limit_to_section:
        database = qry.limit_to_section(database, args.limit_to_section)

    if args.limit_to_standing:
        database = qry.limit_to_standing(database, args.limit_to_standing)

    if args.limit_to_scale:
        database = qry.limit_to_scale(database, args.limit_to_scale)

    # {{{ grading loop

    for student in database.students.values():
        log = student.__dict__.setdefault("log", [])

        def add_log(severity, msg):
            """severity: 0-5"""
            log.append((severity, msg))  # noqa: B023

        grade = database.course_rules["MAKE_GRADE"](student, add_log)
        student.set_attribute("grade", grade)

        if grade is not None:
            rounded_grade = round(100*grade)
            letter_grade = make_letter_grade(database, student, add_log)
        else:
            rounded_grade = None
            letter_grade = None

        student.set_attribute("rounded_grade", rounded_grade)
        student.set_attribute("letter_grade", letter_grade)

    # }}}

    if args.print_student_report:
        out.print_student_report(database, args.print_student_report)

    if args.print_grade_list:
        out.print_warnings(database, args.warn_level)
        out.print_grade_list(database)

    if args.plot_histogram:
        out.plot_histogram(database, not args.histogram_undiff)

    if args.print_letter_histogram:
        out.print_letter_histogram(database)

    if args.print_emails:
        out.print_emails(database, args.email_suffix)

    if args.print_roster_csv:
        out.print_roster_csv(database)

    if args.print_banner_csv:
        out.print_banner_csv(database)

    if args.update_banner_xlsx:
        out.update_banner_xlsx(database, args.update_banner_xlsx)

    if args.print_relate_csv:
        out.print_relate_csv(database)

    if args.print_preliminary_relate_csv:
        out.print_preliminary_relate_csv(database)

    if args.print_relate_not_in_roster_query:
        out.print_relate_not_in_roster_query(database, args.email_suffix)

    if args.print_random_group_csv:
        out.print_random_group_csv(database, args.random_group_size)

    if args.print_warnings:
        out.print_warnings(database, args.warn_level)
