import re


def normalize_name(raw_name: str) -> str | None:
    """
    Cleans OCR-extracted student names by removing leading
    non-alphabetic noise while preserving the actual name.

    Examples:
        "-MOHAMMAD SAMSHEER" -> "MOHAMMAD SAMSHEER"
        ": MOHAMMAD ASHIN"   -> "MOHAMMAD ASHIN"
        "MOHAMMAD"          -> "MOHAMMAD"
    """

    if not raw_name:
        return None

    name = raw_name.strip()

    # Remove leading non-alphabetic characters
    name = re.sub(r'^[^A-Z]+', '', name.upper())

    # Normalize internal whitespace
    name = re.sub(r'\s+', ' ', name).strip()

    # Final sanity check: name must contain letters
    if not re.search(r'[A-Z]', name):
        return None

    return name
