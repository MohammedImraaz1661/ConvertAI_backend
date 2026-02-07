from ingestion.pdf.extractor import extract_text_from_pdf
from ingestion.pdf.normalizer import normalize_text
from parsing.subjects.pdf_subjects import run_regex_pipeline

TARGET_USN = "4DM23AI039"


def parse_vtu_pdf(pdf_path: str) -> dict:
    raw_text = extract_text_from_pdf(pdf_path)
    clean_text = normalize_text(raw_text)

    parsed = run_regex_pipeline(clean_text)

    # ✅ FIX: subject_code already exists — DO NOT use "code"
    subjects = []
    for s in parsed.get("subjects", []):
        subjects.append({
            "subject_code": s.get("subject_code"),
            "internal": s.get("internal"),
            "external": s.get("external"),
            "total": s.get("total"),
            "result": s.get("result"),
        })

    result = {
        "header": {
            "usn": parsed["header"]["usn"],
            "name": parsed["header"]["name"]
        },
        "subjects": subjects
    }

    return result
