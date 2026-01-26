import re

SUBJECT_CODE = r"[A-Z]{3,5}\d{3,4}[A-Z]?"
RESULT = r"[PFAXW]"

def normalize_text(text: str) -> str:
    # 1. Remove non-breaking spaces
    text = text.replace("\u00a0", " ")

    # 2. Collapse multiple spaces
    text = re.sub(r"[ \t]+", " ", text)

    # 3. Collapse subject blocks:
    # SUBJECT_CODE <any text> IM EM TOTAL RESULT DATE
    text = re.sub(
        rf"({SUBJECT_CODE})(.*?)\n?\s*(\d+)\s+(\d+)\s+(\d+)\s+({RESULT})",
        r"\1 \3 \4 \5 \6",
        text,
        flags=re.DOTALL
    )

    # 4. Remove dates (not needed for regex)
    text = re.sub(r"\d{4}-\d{2}-\d{2}", "", text)

    return text
