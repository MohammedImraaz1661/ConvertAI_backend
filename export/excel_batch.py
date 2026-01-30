from backend.export.template_loader import load_template
from openpyxl.styles import Font, PatternFill
from backend.export.writer import write_student_result, TOPPER_FILL


def write_batch_results_excel(
    results: list[dict],
    template_path: str,
    output_path: str,
    start_row: int = 6
):
    wb, ws, subject_column_map = load_template(template_path)

    row = start_row
    sl_no = 1
    topper_tracker = []

    for result in results:
        wb, numeric_total = write_student_result(
            wb=wb,
            ws=ws,
            subject_column_map=subject_column_map,
            result_data={
                "header": result["header"],
                "subjects": result["subjects"]
            },
            row_index=row,
            sl_no=sl_no
        )

        topper_tracker.append((row, numeric_total))

        row += 1
        sl_no += 1

    # 🏆 Highlight class topper
    if topper_tracker:
        topper_row, _ = max(topper_tracker, key=lambda x: x[1])
        for col in range(1, ws.max_column + 1):
            ws.cell(row=topper_row, column=col).fill = TOPPER_FILL

    for col in range(1, ws.max_column + 1):
        ws.cell(row=topper_row, column=col).fill = TOPPER_FILL

    bold_font = Font(bold=True)

    # Fixed columns to bold
    BOLD_COLUMNS = {1, 2, 3, 31, 32}  # SL No, USN, Name, Grand Total, Percentage

    # Add all subject TOTAL columns dynamically
    for cols in subject_column_map.values():
        if "TOTAL" in cols:
            BOLD_COLUMNS.add(cols["TOTAL"])

    # Apply bold styling
    for row in ws.iter_rows():
        for cell in row:
            if cell.column in BOLD_COLUMNS:
                cell.font = bold_font

    LEGEND_FAIL = PatternFill(start_color="FFD60A", end_color="FFD60A", fill_type="solid")
    LEGEND_PE = PatternFill(start_color="CFE2F3", end_color="CFE2F3", fill_type="solid")
    LEGEND_NSS = PatternFill(start_color="EAD1DC", end_color="EAD1DC", fill_type="solid")
    LEGEND_TOPPER = PatternFill(start_color="FCE5CD", end_color="FCE5CD", fill_type="solid")

    bold_font = Font(bold=True)

    #Legend Position
    legend_col = 37 #AI
    legend_row = 61

    #Title
    title_cell = ws.cell(row=legend_row, column=legend_col)
    title_cell.value = "LEGEND"
    title_cell.font = bold_font

    # Subject fail
    cell = ws.cell(row=legend_row + 2, column=legend_col)
    cell.value = "Subject Fail"
    cell.fill = LEGEND_FAIL

    # PE
    cell = ws.cell(row=legend_row + 3, column=legend_col)
    cell.value = "(BPEK559)"
    cell.fill = LEGEND_PE

    # NSS
    cell = ws.cell(row=legend_row + 4, column=legend_col)
    cell.value = "(BNSK559)"
    cell.fill = LEGEND_NSS

    # Topper
    cell = ws.cell(row=legend_row + 5, column=legend_col)
    cell.value = "Class Topper"
    cell.fill = LEGEND_TOPPER

    wb.save(output_path)
