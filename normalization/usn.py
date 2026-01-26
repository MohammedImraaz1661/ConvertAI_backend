import re

# OCR confusion maps
DIGIT_TO_ALPHA = {
    "1": "I",
    "0": "O",
    "5": "S",
    "8": "B",
}

ALPHA_TO_DIGIT = {
    "I": "1",
    "O": "0",
    "S": "5",
    "B": "8",
}


def normalize_usn(raw_usn: str) -> str | None:
    """
    Safely normalizes VTU USN extracted via OCR.

    Returns:
        normalized USN string if valid
        None if invalid / unfixable
    """

    if not raw_usn:
        return None

    usn = raw_usn.strip().upper()

    # Rule 1: Length check
    if len(usn) != 10:
        return None

    # Split into semantic parts
    region = usn[0]          # digit
    college = usn[1:3]       # letters
    year = usn[3:5]          # digits
    branch = usn[5:7]        # letters (OCR mess happens here)
    roll = usn[7:10]         # digits

    # Fix branch: digits → letters
    fixed_branch = ""
    for ch in branch:
        if ch.isdigit():
            fixed_branch += DIGIT_TO_ALPHA.get(ch, ch)
        else:
            fixed_branch += ch

    # Fix roll number: letters → digits
    fixed_roll = ""
    for ch in roll:
        if ch.isalpha():
            fixed_roll += ALPHA_TO_DIGIT.get(ch, ch)
        else:
            fixed_roll += ch

    normalized = region + college + year + fixed_branch + fixed_roll

    # Final validation
    if re.match(r'^[0-9][A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{3}$', normalized):
        return normalized

    return None
