from openpyxl.workbook.workbook import Workbook
import re


def subject_sort_key(code: str):
    if not code:
        return ("", 0, "")

    match = re.match(r"([A-Z]+)(\d+)([A-Z]?)", code)
    if not match:
        return (code, 0, "")

    prefix, number, suffix = match.groups()
    return (prefix, int(number), suffix)


def write_student_result(
    wb: Workbook,
    ws,
    subject_column_map: dict,
    result_data: dict,
    row_index: int
):
    header = result_data["header"]
    subjects = result_data["subjects"]

    # ✅ VTU-aware subject sorting
    subjects = sorted(
        subjects,
        key=lambda s: subject_sort_key(s.get("subject_code", ""))
    )

    ws.cell(row=row_index, column=1).value = row_index - 2
    ws.cell(row=row_index, column=2).value = header["usn"]
    ws.cell(row=row_index, column=3).value = header["name"]

    for subject in subjects:
        code = subject["subject_code"]

        if code not in subject_column_map:
            continue

        cols = subject_column_map[code]

        ws.cell(row=row_index, column=cols["INTERNAL"]).value = subject["internal"]
        ws.cell(row=row_index, column=cols["EXTERNAL"]).value = subject["external"]
        ws.cell(row=row_index, column=cols["TOTAL"]).value = subject["total"]
        ws.cell(row=row_index, column=cols["RESULT"]).value = subject["result"]

    return wb
