from backend.parsing.header.pdf_header import extract_header
from app.regex_engine.confidence import (
    compute_confidence,
    flag_from_confidence
)

TARGET_USN = "4DM23AI039"  # 👈 change if needed


def run_regex_pipeline(text: str) -> dict:
    header = extract_header(text)
    subjects = extract_subjects(text)

    processed_subjects = []

    for subj in subjects:
        confidence = compute_confidence(subj)
        processed_subjects.append({
            **subj,
            "confidence": confidence,
            "flag": flag_from_confidence(confidence)
        })

    return {
        "header": header,
        "subjects": processed_subjects
    }

# regex_engine/subject_regex.py

import re
from app.core.config import SUBJECT_CODE_REGEX, RESULT_REGEX

SUBJECT_ROW_PATTERN = re.compile(
    rf"({SUBJECT_CODE_REGEX})\s+(\d+)\s+(\d+)\s+(\d+)\s+({RESULT_REGEX})",
    re.MULTILINE
)


def extract_subjects(text: str) -> list:
    subjects = []

    for match in SUBJECT_ROW_PATTERN.finditer(text):
        subjects.append({
            "subject_code": match.group(1),
            "internal": int(match.group(2)),
            "external": int(match.group(3)),
            "total": int(match.group(4)),
            "result": match.group(5)
        })

    return subjects
