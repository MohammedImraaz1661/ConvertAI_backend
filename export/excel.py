# backend/export/excel.py

from backend.export.template_loader import load_template
from backend.export.writer import write_student_result


def write_result_excel(
    result: dict,
    template_path: str,
    output_path: str,
    row_index: int = 6
):
    """
    Writes a single VTU result into the Excel template.
    """

    # 1️⃣ Load template & subject map
    wb, ws, subject_column_map, total_col, percentage_col = load_template(template_path)

    # 2️⃣ Write student result
    write_student_result(
        wb=wb,
        ws=ws,
        subject_column_map=subject_column_map,
        result_data={
            "header": {
                "usn": result["usn"],
                "name": result["name"]
            },
            "subjects": result["subjects"]
        },
        row_index=row_index,
        sl_no=1,
        total_sum_col=total_col,
        percentage_col=percentage_col
    )

    # 3️⃣ Save output
    wb.save(output_path)
