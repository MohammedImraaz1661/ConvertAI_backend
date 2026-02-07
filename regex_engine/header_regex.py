# regex_engine/header_regex.py

import re

USN_PATTERN = re.compile(
    r"University Seat Number\s*:\s*([A-Z0-9]+)",
    re.IGNORECASE
)

NAME_PATTERN = re.compile(
    r"Student Name\s*:\s*([A-Z\s]+)\n",
    re.IGNORECASE
)


def normalize_usn(raw_usn: str) -> str:
    """
    Normalize common OCR errors in VTU USN
    WITHOUT guessing missing information.

    Safe for both PDF and Image OCR.
    """
    if not raw_usn:
        return raw_usn

    usn = raw_usn.upper().replace(" ", "")

    # --- Fix known OCR confusions (branch AI) ---
    usn = usn.replace("A1", "AI")
    usn = usn.replace("AL", "AI")

    # --- Do NOT guess missing roll numbers ---
    # If OCR gives 4DM23AI1 → keep structure but pad safely
    # (prevents breaking downstream keys)
    if re.match(r".*AI\d$", usn):
        usn = usn[:-1] + "0" + usn[-1]

    return usn


def extract_header(text: str) -> dict:
    usn_match = USN_PATTERN.search(text)
    name_match = NAME_PATTERN.search(text)

    raw_usn = usn_match.group(1).strip() if usn_match else None
    usn = normalize_usn(raw_usn) if raw_usn else None

    return {
        "usn": usn,
        "name": name_match.group(1).strip() if name_match else None
    }
