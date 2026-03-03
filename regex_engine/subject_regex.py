# regex_engine/subject_regex.py

import re
from core.config import SUBJECT_CODE_REGEX, RESULT_REGEX

# 1️⃣ Subject code pattern (order matters)
SUBJECT_CODE_PATTERN = re.compile(
    SUBJECT_CODE_REGEX,
    re.IGNORECASE
)

# 2️⃣ Marks line pattern (THIS is the reliable part)
MARKS_PATTERN = re.compile(
    rf"(\d{{1,3}})\s+(\d{{1,3}})\s+(\d{{1,3}})\s+({RESULT_REGEX})",
    re.IGNORECASE
)


def extract_subjects(text: str) -> list:
    subjects = []

    codes = SUBJECT_CODE_PATTERN.findall(text)
    marks = MARKS_PATTERN.findall(text)

    # 🔍 DEBUG (keep temporarily if you want)
    # print("CODES FOUND:", codes)
    # print("MARKS FOUND:", marks)

    count = min(len(codes), len(marks))

    for i in range(count):
        internal, external, total, result = marks[i]

        subjects.append({
            "subject_code": codes[i],
            "internal": int(internal),
            "external": int(external),
            "total": int(total),
            "result": result
        })

    return subjects
