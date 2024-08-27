from typing import Iterable, cast

from course_tools.data import Database


# {{{ moodle

def read_moodle_csv(database: Database, csv_name: str) -> None:
    import csv

    with open(csv_name, "rt", encoding="utf-8") as csvfile:
        data = [ln for ln in csvfile.readlines() if not ln.startswith("#")]

    data = list(cast(Iterable[str], csv.reader(data)))

    col_names = data[0]

    def proc_colname(cn):
        colon_idx = cn.rfind(":")
        if colon_idx != -1:
            return cn[colon_idx+1:]
        else:
            return cn

    def proc_value(v):
        if v == "-":
            return None
        elif not v:
            return 0

        if v.lower().strip() == "nan":
            return v

        try:
            return float(v)
        except Exception:
            return v

    for row in data[1:]:
        row_dict = {
            proc_colname(colname): proc_value(value)
            for colname, value in zip(col_names, row)}
        netid = row_dict["Username"]
        student = database.get_student(netid)
        student.set_attribute("network_id", netid)
        student.set_attribute("last_name", row_dict["Last name"])
        student.set_attribute("first_name", row_dict["First name"])
        student.set_attribute("csv_row", row_dict)

# }}}


# {{{ relate

def read_relate_csv(database: Database, csv_name: str) -> None:
    import csv

    with open(csv_name, "rt", encoding="utf-8") as csvfile:
        data = [ln for ln in csvfile.readlines() if not ln.startswith("#")]

    data = list(cast(Iterable[str], csv.reader(data)))

    col_names = data[0]

    def proc_value(v):
        if v == "NONE":
            return None

        if v.lower().strip() == "nan":
            return v

        try:
            return float(v)
        except Exception:
            return v

    for row in data[1:]:
        row_dict = {colname: proc_value(value)
            for colname, value in zip(col_names, row)}
        email = row_dict["user_name"]
        netid = email[:email.find("@")].lower()
        student = database.get_student(netid)
        student.set_attribute("network_id", netid)
        student.set_attribute("last_name", row_dict["last_name"])
        student.set_attribute("first_name", row_dict["first_name"])
        student.set_attribute("csv_row", row_dict)

# }}}


# {{{ my.engr html

def read_my_engr_html_roster(database: Database, html_name: str) -> None:
    from bs4 import BeautifulSoup
    with open(
            html_name, "rt", encoding="utf-8", errors="replace") as html_file:
        soup = BeautifulSoup(html_file.read(), "lxml")

    for child in soup.find(
            "div", attrs={"class": "module_content"}).find_all("div"):
        if "id" in child.attrs and child["id"].startswith("rostertable"):
            rostertable_div = child
            section_head = rostertable_div.find("h5").string.split()[1]
            rostertable = rostertable_div.find("table")
            if rostertable is None:
                # empty section
                continue

            rosterhead = rostertable_div.find("table").find("thead")
            rosterbody = rostertable_div.find("table").find("tbody")

            columns = [span.string for span in rosterhead.find_all("span")]
            for tr in rosterbody.find_all("tr"):
                row = dict(zip(columns, [
                    td.get_text().strip() for td in tr.find_all("td")]))

                netid = row["Net ID"]
                student = database.get_student(netid)
                last_name, first_name = row["Name"].split(",", 1)
                last_name = last_name.strip()
                first_name = first_name.strip()

                section_tbl = row["Class"].split()[-1]

                if section_head != section_tbl:
                    from warnings import warn
                    warn(
                        f"student {netid} in section {section_tbl} found under "
                        f"section heading {section_head}, ignoring heading")

                student.set_attribute("standing", row["Year"])
                student.set_attribute("section", section_tbl)
                student.set_attribute("credit_hours", int(row["Credit"]))
                student.set_attribute("university_id", row["UIN"])
                student.set_attribute("roster_row", row)
                student.set_attribute("last_name", last_name)
                student.set_attribute("first_name", first_name)

# }}}

# vim: foldmethod=marker
