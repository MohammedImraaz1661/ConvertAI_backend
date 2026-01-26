from pathlib import Path
from app.excel_engine.template_loader import load_template
from app.excel_engine.writer import write_student_result


def export_results_to_excel(final_results, template_path, output_path):
    wb, ws, subject_column_map = load_template(template_path)

    row_index = 3  # as per your template design

    for result in final_results:
        # 🔧 Normalize subject key for Excel writer
        subjects = []
        for s in result["subjects"]:
            subjects.append({
                "subject_code": s["code"],   # FIX HERE
                "internal": s.get("internal"),
                "external": s.get("external"),
                "total": s.get("total"),
                "result": s.get("result"),
            })

        result_data = {
            "header": result["header"],
            "subjects": subjects
        }

        wb = write_student_result(
            wb,
            ws,
            subject_column_map,
            result_data,
            row_index=row_index
        )

        row_index += 1

    wb.save(output_path)
