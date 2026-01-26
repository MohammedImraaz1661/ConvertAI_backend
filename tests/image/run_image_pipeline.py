"""
Image-based OCR testing pipeline

Flow:
Image
 -> quality check
 -> enhance if needed
 -> DocTR OCR
 -> raw text dump
 -> page-level structuring
 -> multi-page merge
 -> final structured output (JSON)

NOTE:
- No Excel
- No API
- Testing only
"""

import os
import json
import cv2
import tempfile
from pathlib import Path

# ==============================
# CONFIG
# ==============================

BASE_DIR = Path(__file__).parent

INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

RAW_TEXT_DIR = OUTPUT_DIR / "raw_text"
STRUCTURED_DIR = OUTPUT_DIR / "structured"

RAW_TEXT_DIR.mkdir(parents=True, exist_ok=True)
STRUCTURED_DIR.mkdir(parents=True, exist_ok=True)

# ==============================
# IMPORT EXISTING LOGIC
# ==============================

from app.doctr_test.ocr import run_doctr_ocr
from app.core.image_enhancer import ImageEnhancer
from app.doctr_test.vtu_table_parser_test import parse_vtu_table
from app.regex_engine.header_regex import extract_header
from app.core.ocr_runner import run_best_ocr_variant
from app.image_pipeline_test.compose_result import export_results_to_excel

# ==============================
# QUALITY CHECK (V1 SIMPLE)
# ==============================

def is_good_quality(image_path: Path) -> bool:
    return "good" in image_path.parts


# ==============================
# PAGE PROCESSOR
# ==============================

def process_image(image_path: Path):
    print(f"\n🖼 Processing: {image_path.name}")

    enhancer = ImageEnhancer(debug=False)

    # ---------- OCR ----------
    if is_good_quality(image_path):
        print("  → Using original image")
        raw_text = run_doctr_ocr(str(image_path))

    else:
        print("  → Enhancing image (multi-variant OCR)")

        variants = enhancer.process_image(str(image_path))

        # Use only DocTR-safe variants
        selected_variants = [
            (name, img)
            for name, img in variants
            if name in ("original", "clahe", "gray")
        ]

        raw_text = run_best_ocr_variant(
            image_path=str(image_path),
            variants=selected_variants
        )

    # ---------- Save raw OCR ----------
    raw_text_file = RAW_TEXT_DIR / f"{image_path.stem}.txt"
    with open(raw_text_file, "w", encoding="utf-8") as f:
        f.write(raw_text)

    # ---------- PAGE STRUCTURING ----------
    header = extract_header(raw_text)
    subjects = parse_vtu_table(raw_text)

    return {
        "image": image_path.name,
        "header": header,
        "subjects": subjects
    }


# ==============================
# MULTI-PAGE MERGER
# ==============================

def merge_pages(page_results):
    final_results = []
    current_doc = None

    for page in page_results:
        header = page.get("header")
        subjects = page.get("subjects", [])

        # New document starts when header with USN exists
        if header and header.get("usn"):
            current_doc = {
                "header": header,
                "subjects": []
            }
            final_results.append(current_doc)

        if current_doc is None:
            continue

        current_doc["subjects"].extend(subjects)

    # Deduplicate subjects by code
    for doc in final_results:
        deduped = {}
        for s in doc["subjects"]:
            deduped[s["code"]] = s
        doc["subjects"] = list(deduped.values())

    return final_results


# ==============================
# ENTRY POINT
# ==============================

def main():
    print("🚀 Starting Image OCR Pipeline Test")

    image_files = (
        list(INPUT_DIR.rglob("*.jpg")) +
        list(INPUT_DIR.rglob("*.png")) +
        list(INPUT_DIR.rglob("*.jpeg"))
    )

    if not image_files:
        print("❌ No images found in input/")
        return

    # IMPORTANT: ensure correct page order
    image_files = sorted(image_files)

    page_results = []

    for image_path in image_files:
        page_result = process_image(image_path)
        page_results.append(page_result)

    # ---------- MERGE MULTI-PAGE RESULTS ----------
    final_results = merge_pages(page_results)
    template_path = Path("tests/samples/results_template.xlsx")
    output_excel = OUTPUT_DIR / "combo_2.xlsx"

    export_results_to_excel(final_results, template_path, output_excel)

    print(f"Excel written to {output_excel}")

    # ---------- WRITE FINAL OUTPUT ----------
    for result in final_results:
        usn = result["header"].get("usn", "unknown")
        out_file = STRUCTURED_DIR / f"{usn}.json"

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

    print("\n✅ All results processed and merged successfully")


if __name__ == "__main__":
    main()
