from openpyxl import load_workbook
import re

SUBJECT_CODE_PATTERN = re.compile(r"^[A-Z]{3,5}\d{3,4}[A-Z]?$")


def is_activity_header(text: str) -> bool:
    """
    Detect headers like:
    BPEK559 / BNSK559
    """
    if "/" not in text:
        return False

    parts = [p.strip() for p in text.split("/")]
    if len(parts) != 2:
        return False

    return all(
        SUBJECT_CODE_PATTERN.match(p) and p[-1] == "9"
        for p in parts
    )


def load_template(template_path: str):
    wb = load_workbook(template_path)
    if "Student Result" in wb.sheetnames:
        ws = wb["Student Result"]
    else:
        ws = wb.worksheets[0]

    subject_column_map = {}
    HEADER_ROWS = [3, 4]   # rows where subject headers exist

    max_col = ws.max_column
    col = 1

    while col <= max_col:
        header_value = None

        # Scan header rows for subject text
        for r in HEADER_ROWS:
            val = ws.cell(row=r, column=col).value
            if isinstance(val, str):
                header_value = val.strip()
                break

        if header_value:
            # ✅ Activity subject (PE / NSS combined)
            if is_activity_header(header_value):
                subject_column_map[header_value] = {
                    "INTERNAL": col,
                    "EXTERNAL": col + 1,
                    "TOTAL": col + 2,
                }
                col += 3
                continue

            # ✅ Normal subject
            if SUBJECT_CODE_PATTERN.match(header_value):
                subject_column_map[header_value] = {
                    "INTERNAL": col,
                    "EXTERNAL": col + 1,
                    "TOTAL": col + 2,
                }
                col += 3
                continue

        col += 1

    return wb, ws, subject_column_map
