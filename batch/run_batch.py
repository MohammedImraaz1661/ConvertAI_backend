from pathlib import Path
from backend.batch.controller import collect_batch_results
from backend.export.excel_batch import write_batch_results_excel

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def run_pdf_batch(input_dir: Path) -> Path:
    """
    Runs PDF batch pipeline and returns output Excel path.
    """
    template = PROJECT_ROOT / "backend" / "templates" / "results_template.xlsx"
    output_dir = PROJECT_ROOT / "backend" / "output"
    output_dir.mkdir(exist_ok=True)

    output_excel = output_dir / "pdf_batch_results.xlsx"

    results = collect_batch_results(str(input_dir))

    if not results:
        raise ValueError("No valid PDF results found")

    # Sort by USN
    results.sort(key=lambda r: r["header"].get("usn") or "ZZZZZZZZZZ")

    write_batch_results_excel(
        results=results,
        template_path=str(template),
        output_path=str(output_excel),
        start_row=3
    )

    return output_excel


def main():
    input_dir = Path("backend/batch/input/pdf")
    output_excel = run_pdf_batch(input_dir)
    print(f"✅ PDF batch Excel generated: {output_excel}")


if __name__ == "__main__":
    main()
