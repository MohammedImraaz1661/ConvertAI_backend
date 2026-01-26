from pathlib import Path
from backend.batch.image_controller import collect_image_batch_results
from backend.export.excel_batch import write_batch_results_excel

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def run_image_batch(input_dir: Path) -> Path:
    """
    Runs image batch pipeline and returns output Excel path.
    """
    template = PROJECT_ROOT / "backend" / "templates" / "results_template.xlsx"
    output_dir = PROJECT_ROOT / "backend" / "output"
    output_dir.mkdir(exist_ok=True)

    output_excel = output_dir / "image_batch_results.xlsx"

    results = collect_image_batch_results(str(input_dir))

    if not results:
        raise ValueError("No valid image results found")

    # Sort by USN (already normalized)
    results.sort(key=lambda r: r["header"].get("usn") or "ZZZZZZZZZZ")

    write_batch_results_excel(
        results=results,
        template_path=str(template),
        output_path=str(output_excel),
        start_row=3
    )

    return output_excel


def main():
    input_dir = Path("backend/batch/input/images")
    output_excel = run_image_batch(input_dir)
    print(f"✅ Image batch Excel generated: {output_excel}")


if __name__ == "__main__":
    main()
