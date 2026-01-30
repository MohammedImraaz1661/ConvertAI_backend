from openpyxl.workbook.workbook import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import PatternFill
import re


TOTAL_SUM_COL = 31      # AE
PERCENTAGE_COL = 32     # AF

# Colours
FAIL_FILL = PatternFill(start_color="FFD60A", end_color="FFD60A", fill_type="solid")
PE_FILL = PatternFill(start_color="CFE2F3", end_color="CFE2F3", fill_type="solid")
NSS_FILL = PatternFill(start_color="EAD1DC", end_color="EAD1DC", fill_type="solid")
TOPPER_FILL = PatternFill(start_color="FCE5CD", end_color="FCE5CD", fill_type="solid")

IGNORE_FAIL_COLOR_SUBJECTS = {"BAI586"}  # Mini Project


def is_activity_subject(code: str) -> bool:
    return bool(code) and code[-1] == "9"


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
    row_index: int,
    sl_no: int,
):
    header = result_data["header"]
    subjects = sorted(
        result_data["subjects"],
        key=lambda s: subject_sort_key(s.get("subject_code", ""))
    )

    # Basic info
    ws.cell(row=row_index, column=1).value = sl_no
    ws.cell(row=row_index, column=2).value = header["usn"]
    ws.cell(row=row_index, column=3).value = header["name"]

    activity_subject = None
    total_columns = []
    numeric_total = 0   # ✅ IMPORTANT

    # ── Normal subjects ─────────────────────────────
    for subject in subjects:
        code = subject.get("subject_code")
        if not code:
            continue

        if is_activity_subject(code):
            activity_subject = subject
            continue

        if code not in subject_column_map:
            continue

        cols = subject_column_map[code]

        int_marks = subject["internal"]
        ext_marks = subject["external"]
        tot_marks = subject["total"]

        int_cell = ws.cell(row=row_index, column=cols["INTERNAL"])
        ext_cell = ws.cell(row=row_index, column=cols["EXTERNAL"])
        tot_cell = ws.cell(row=row_index, column=cols["TOTAL"])

        int_cell.value = int_marks
        ext_cell.value = ext_marks
        tot_cell.value = tot_marks

        if code not in IGNORE_FAIL_COLOR_SUBJECTS:
            if int_marks < 18 or ext_marks < 18 or tot_marks < 36:
                int_cell.fill = FAIL_FILL
                ext_cell.fill = FAIL_FILL
                tot_cell.fill = FAIL_FILL

        total_columns.append(cols["TOTAL"])
        numeric_total += tot_marks

    # ── PE / NSS ────────────────────────────────────
    activity_key = next((k for k in subject_column_map if "/" in k), None)

    if activity_subject and activity_key:
        cols = subject_column_map[activity_key]

        int_cell = ws.cell(row=row_index, column=cols["INTERNAL"])
        ext_cell = ws.cell(row=row_index, column=cols["EXTERNAL"])
        tot_cell = ws.cell(row=row_index, column=cols["TOTAL"])

        int_cell.value = activity_subject["internal"]
        ext_cell.value = activity_subject["external"]
        tot_cell.value = activity_subject["total"]

        if activity_subject["subject_code"] == "BPEK559":
            fill = PE_FILL
        elif activity_subject["subject_code"] == "BNSK559":
            fill = NSS_FILL
        else:
            fill = None

        if fill:
            int_cell.fill = fill
            ext_cell.fill = fill
            tot_cell.fill = fill

        total_columns.append(cols["TOTAL"])
        numeric_total += activity_subject["total"]

    # ── TOTAL + PERCENTAGE ───────────────────────────
    if total_columns:
        total_formula = "=" + "+".join(
            f"{get_column_letter(col)}{row_index}" for col in total_columns
        )
        ws.cell(row=row_index, column=TOTAL_SUM_COL).value = total_formula

        subject_count = len(total_columns)
        percentage_formula = (
            f"=ROUND(({get_column_letter(TOTAL_SUM_COL)}{row_index}"
            f"/({subject_count}*100))*100, 1)"
        )
        ws.cell(row=row_index, column=PERCENTAGE_COL).value = percentage_formula

    return wb, numeric_total
