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
