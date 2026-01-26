"""
OCR Adapter for Convert.ai

Purpose:
- Deterministic extraction of header fields (USN, Student Name)
- Robust extraction of subject rows
- Designed specifically for VTU result layouts (future-safe)
"""

import re
from typing import Dict, List, Optional


# --------------------------------
# 1. Header Extraction (Option A)
# --------------------------------

def extract_usn_and_name(ocr_text: str) -> Dict[str, Optional[str]]:
    """
    Extracts USN and Student Name using key–value line pairing.

    Expected OCR pattern:
        University Seat Number
        : 4DM23AI028
        Student Name
        : MOHAMMAD ASHIN IMRAAZ
    """

    usn = None
    name = None

    # Clean and normalize lines
    lines = [line.strip() for line in ocr_text.splitlines() if line.strip()]

    i = 0
    while i < len(lines):
        line = lines[i].upper()

        # ---- USN ----
        if "UNIVERSITY SEAT NUMBER" in line and i + 1 < len(lines):
            value_line = lines[i + 1].lstrip(": ").strip()
            if value_line:
                usn = value_line

        # ---- STUDENT NAME ----
        if "STUDENT NAME" in line and i + 1 < len(lines):
            value_line = lines[i + 1].lstrip(": ").strip()
            if value_line:
                name = value_line

        if usn and name:
            break

        i += 1

    return {
        "usn": usn,
        "name": name
    }


# --------------------------------
# 2. Subject Row Extraction
# --------------------------------

def extract_subject_rows(ocr_text: str) -> List[str]:
    """
    Extracts unique subject rows like:
    BCS401 44 38 82 P
    """

    rows: List[str] = []
    seen = set()

    for line in ocr_text.splitlines():
        line = line.strip()

        # Subject code + numeric marks
        if re.match(r'^[A-Z]{2,4}\d{3}[A-Z]?\s+\d+', line):
            if line not in seen:
                seen.add(line)
                rows.append(line)

    return rows


# --------------------------------
# 3. Adapter Output Builder
# --------------------------------

def build_regex_input(ocr_text: str) -> Dict[str, object]:
    """
    Final adapter function used by Convert.ai pipeline.
    """

    header = extract_usn_and_name(ocr_text)
    subjects = extract_subject_rows(ocr_text)

    return {
        "usn": header["usn"],
        "name": header["name"],
        "text": "\n".join(subjects)
    }
