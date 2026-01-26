from openpyxl import load_workbook
import re


# Strict subject code pattern (VTU-safe)
SUBJECT_CODE_PATTERN = re.compile(r"^[A-Z]{3,5}\d{3,4}[A-Z]?$")


def load_template(template_path: str):
    wb = load_workbook(template_path)
    ws = wb.active

    subject_column_map = {}
    header_row = 1

    col = 1
    max_col = ws.max_column

    while col <= max_col:
        cell_value = ws.cell(row=header_row, column=col).value

        if cell_value and isinstance(cell_value, str):
            value = cell_value.strip()

            # ✅ Only treat real subject codes as subject blocks
            if SUBJECT_CODE_PATTERN.match(value):
                subject_column_map[value] = {
                    "INTERNAL": col,
                    "EXTERNAL": col + 1,
                    "TOTAL": col + 2,
                    "RESULT": col + 3,
                }

                # Subject block is exactly 4 columns wide
                col += 4
                continue

        # Default: move to next column
        col += 1

    return wb, ws, subject_column_map
