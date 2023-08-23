from . import input as inp, output as out, query as qry
from .data import Database
from .grade import make_letter_grade


def main():
    # {{{ frontend

    from argparse import ArgumentParser
    parser = ArgumentParser(usage="%(prog)s [options]")
    parser.add_argument("--moodle-csv", metavar="CSV", nargs="*")
    parser.add_argument("--relate-csv", metavar="CSV", nargs="*")
    parser.add_argument("--my-cs-html-roster", metavar="HTML", nargs="*")
    parser.add_argument("--course-rules", metavar="RULES_PY")
    parser.add_argument("-w", "--warn-level", type=int, default=4)
    parser.add_argument("--limit-to-section", metavar="SECTION")
    parser.add_argument("--limit-to-scale", metavar="SCALE")
    parser.add_argument("--limit-to-standing", metavar="STANDING")
    parser.add_argument("--print-scales", action="store_true")
    parser.add_argument("-g", "--print-grade-list", action="store_true")
    parser.add_argument("-s", "--print-student-report", metavar="NETWORK_ID")
    parser.add_argument("--print-letter-histogram", action="store_true")
    parser.add_argument("--plot-histogram", action="store_true")
    parser.add_argument("--histogram-undiff", action="store_true")
    parser.add_argument("--print-emails", action="store_true")
    parser.add_argument("--email-suffix", default="@illinois.edu")
    parser.add_argument("--print-banner-csv", action="store_true")
    parser.add_argument("--print-relate-csv", action="store_true")
    parser.add_argument("--print-preliminary-relate-csv", action="store_true")
    parser.add_argument("--print-warnings", action="store_true")
    parser.add_argument(
        "--remove-students-without-section", action="store_true")
    args = parser.parse_args()

    if args.course_rules is None:
        raise RuntimeError("course rules module needed")

    course_rules = {}
    with open(args.course_rules) as rulesf:
        rules_file_contents = rulesf.read()

    exec(compile(rules_file_contents, args.course_rules, "exec"), course_rules)

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

    if args.print_banner_csv:
        out.print_banner_csv(database)

    if args.print_relate_csv:
        out.print_relate_csv(database)

    if args.print_preliminary_relate_csv:
        out.print_preliminary_relate_csv(database)

    if args.print_warnings:
        out.print_warnings(database, args.warn_level)
