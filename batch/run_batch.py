from pathlib import Path
from datetime import datetime

from batch.controller import collect_batch_results
from export.excel_batch import write_batch_results_excel

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def run_pdf_batch(input_dir: Path, template_path: Path) -> Path:
    """
    Runs PDF batch pipeline and returns output Excel path.
    """

    output_dir = PROJECT_ROOT / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_excel = output_dir / f"batch_result_{timestamp}.xlsx"

    results = collect_batch_results(str(input_dir))

    if not results:
        raise ValueError("No valid PDF results found")

    results.sort(key=lambda r: r["header"].get("usn") or "ZZZZZZZZ")

    write_batch_results_excel(
        results=results,
        template_path=str(template_path),
        output_path=str(output_excel),
        start_row=6
    )

    return output_excel
