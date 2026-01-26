# backend/services/vtu_ocr_parser.py

from backend.ingestion.image.enhancer import ImageEnhancer
from backend.ingestion.image.runner import run_best_ocr_variant

from backend.parsing.header.ocr_header import extract_usn_and_name
from backend.parsing.subjects.ocr_subjects import parse_vtu_table

from backend.aggregation.accumulator import ResultAccumulator


def parse_vtu_image(image_paths: list[str]) -> dict:
    """
    Public OCR API:
    Parses one or more VTU result images and returns
    dict-based structured output.
    """

    enhancer = ImageEnhancer(debug=False)
    accumulator = ResultAccumulator()

    for image_path in image_paths:
        # -----------------------------
        # OCR (best variant)
        # -----------------------------
        variants = enhancer.process_image(image_path)

        ocr_text = run_best_ocr_variant(
            image_path=image_path,
            variants=variants
        )

        # -----------------------------
        # HEADER (dict-based)
        # -----------------------------
        header = extract_usn_and_name(ocr_text)

        # -----------------------------
        # SUBJECTS (dict-based ✅)
        # -----------------------------
        raw_subjects = parse_vtu_table(ocr_text)

        subjects = []
        for s in raw_subjects:
            subjects.append({
            "subject_code": s.get("code"),   # 🔑 normalize key
            "internal": s.get("internal"),
            "external": s.get("external"),
            "total": s.get("total"),
            "result": s.get("result"),
        })


        # subjects = [
        #   { "code", "internal", "external", "total", "result" }
        # ]

        # -----------------------------
        # ACCUMULATE PAGE
        # -----------------------------
        accumulator.process_page({
            "usn": header.get("usn"),
            "name": header.get("name"),
            "subjects": subjects
        })

    # -----------------------------
    # FINAL MERGE (multi-page)
    # -----------------------------
    results = accumulator.finalize()


    return results[0] if results else {}
