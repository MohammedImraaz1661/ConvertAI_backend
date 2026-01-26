from pathlib import Path
import json
import re

from app.utils.pdf_to_text import extract_text_from_pdf
from app.utils.text_normalizer import normalize_text
from app.regex_engine.parser import run_regex_pipeline


# -------- CONFIG --------
BASE_DIR = Path(__file__).resolve().parent.parent
PDF_NAME = "039.pdf"   # change this to test other PDFs
PDF_PATH = BASE_DIR / "tests" / "samples" / "039.pdf"
# ------------------------


def main():
    print(f"\n📄 Testing PDF: {PDF_NAME}\n")

    # 1. Extract raw text
    raw_text = extract_text_from_pdf(str(PDF_PATH))

    # 2. Normalize text
    clean_text = normalize_text(raw_text)

    # 3. Run regex pipeline
    result = run_regex_pipeline(clean_text)

    # 4. Reduce output to ONLY what we care about (v1 contract)
    clean_output = {
        "usn": result["header"]["usn"],
        "name": result["header"]["name"],
        "subjects": [
            {
                "subject_code": s["subject_code"],
                "internal": s["internal"],
                "external": s["external"],
                "total": s["total"],
                "result": s["result"],
            }
            for s in result["subjects"]
        ]
    }

    # 5. Print JSON nicely
    print("✅ JSON OUTPUT:\n")
    print(json.dumps(clean_output, indent=2))


if __name__ == "__main__":
    main()
