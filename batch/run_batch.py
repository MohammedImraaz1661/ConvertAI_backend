from pathlib import Path
from datetime import datetime

from parsing.pdf_parser import parse_pdf_by_page
from segmentation.student_segmenter import segment_students_from_pages
from regex_engine.parser import run_regex_pipeline
from export.excel_batch import write_batch_results_excel

PROJECT_ROOT = Path(__file__).resolve().parents[1]

def run_pdf_batch(input_dir: Path, template_path: Path) -> Path:
    output_dir = PROJECT_ROOT / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_excel = output_dir / f"batch_result_{timestamp}.xlsx"

    all_results = []

    pdf_files = sorted(input_dir.glob("*.pdf"))
    # print(f"### DEBUG: PDFs found = {len(pdf_files)}")

    if not pdf_files:
        raise ValueError("No PDF files found in input directory")

    for pdf_path in pdf_files:
        # print(f"\n### DEBUG: Processing PDF = {pdf_path.name}")

        pages = parse_pdf_by_page(str(pdf_path))
        # print(f"### DEBUG: Pages extracted = {len(pages)}")

        student_texts = segment_students_from_pages(pages)
        # print(f"### DEBUG: Students detected = {len(student_texts)}")

        for idx, student_text in enumerate(student_texts, start=1):
            # print(f"\n### DEBUG: Student block #{idx}")
            # print(student_text[:300])  # first 300 chars only

            try:
                result = run_regex_pipeline(student_text)

                if not result:
                    # print("### DEBUG: run_regex_pipeline returned None")
                    continue

                header = result.get("header", {})
                subjects = result.get("subjects", [])

                # print(
                #     f"### DEBUG: USN = {header.get('usn')}, "
                #     f"Subjects extracted = {len(subjects)}"
                # )

                if not header or not header.get("usn"):
                    # print("### DEBUG: Missing USN, skipping")
                    continue

                all_results.append(result)

            except Exception as e:
                # print(f"### DEBUG: Exception in regex pipeline: {e}")
                continue

    # print(f"\n### DEBUG: Total valid students = {len(all_results)}")

    if not all_results:
        raise ValueError("No valid student results found in uploaded PDFs")

    all_results.sort(key=lambda r: r["header"].get("usn") or "ZZZZZZZZ")

    write_batch_results_excel(
        results=all_results,
        template_path=str(template_path),
        output_path=str(output_excel),
        start_row=6
    )

    return output_excel
