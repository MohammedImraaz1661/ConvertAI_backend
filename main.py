from backend.services.vtu_pdf_parser import parse_vtu_pdf
from backend.export.excel import write_result_excel


def main():
    result = parse_vtu_pdf("backend/tests/fixtures/039.pdf")

    write_result_excel(
        result=result,
        template_path="backend/templates/results_template.xlsx",
        output_path="backend/output/pdf/039.xlsx",
        row_index=3
    )

    print("✅ PDF Excel generated")

if __name__ == "__main__":
    main()
