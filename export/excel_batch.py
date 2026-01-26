from backend.export.template_loader import load_template
from backend.export.writer import write_student_result


def write_batch_results_excel(
    results: list[dict],
    template_path: str,
    output_path: str,
    start_row: int = 3
):
    """
    Writes multiple VTU results into a single Excel file.
    """

    wb, ws, subject_column_map = load_template(template_path)

    row = start_row
    for result in results:
        write_student_result(
            wb=wb,
            ws=ws,
            subject_column_map=subject_column_map,
            result_data={
                "header": result["header"],
                "subjects": result["subjects"]
            },
            row_index=row
        )
        row += 1

    wb.save(output_path)
