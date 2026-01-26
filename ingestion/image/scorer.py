import re


class OCRScorer:
    """
    Scores OCR text quality specifically for VTU result PDFs.
    Higher score = better OCR.
    """

    def score(self, text: str) -> int:
        if not text or len(text.strip()) < 50:
            return 0

        t = text.upper()
        score = 0

        # --------------------------------------------------
        # 1. CORE ANCHORS (VERY IMPORTANT)
        # --------------------------------------------------
        if "UNIVERSITY SEAT NUMBER" in t:
            score += 15

        if "STUDENT NAME" in t:
            score += 12

        if "SEMESTER" in t:
            score += 8

        if "VTU" in t or "VISVESVARAYA" in t:
            score += 5

        # --------------------------------------------------
        # 2. SUBJECT CODES (TABLE DETECTION)
        # Examples: BCS401, BAD402, BCSL404
        # --------------------------------------------------
        subject_codes = re.findall(r"\b[A-Z]{3,4}L?\d{3}\b", t)
        score += min(len(subject_codes) * 4, 40)

        # --------------------------------------------------
        # 3. MARKS & NUMERIC DENSITY
        # --------------------------------------------------
        marks = re.findall(r"\b\d{1,3}\b", t)
        score += min(len(marks), 30)

        # --------------------------------------------------
        # 4. PASS / FAIL / RESULT COLUMN
        # --------------------------------------------------
        if re.search(r"\bP\b", t):
            score += 5

        if "RESULT" in t:
            score += 4

        # --------------------------------------------------
        # 5. DATE DETECTION (ANNOUNCED ON)
        # --------------------------------------------------
        if re.search(r"\b20\d{2}[-/]\d{2}[-/]\d{2}\b", t):
            score += 5

        # --------------------------------------------------
        # 6. ALPHANUMERIC RATIO (GARBAGE FILTER)
        # --------------------------------------------------
        alnum_ratio = sum(c.isalnum() for c in text) / max(len(text), 1)

        if alnum_ratio > 0.75:
            score += 10
        elif alnum_ratio > 0.65:
            score += 5
        else:
            score -= 10  # noisy OCR

        # --------------------------------------------------
        # 7. LINE STRUCTURE BONUS
        # --------------------------------------------------
        lines = [l for l in text.splitlines() if len(l.strip()) > 3]

        if len(lines) > 25:
            score += 10
        elif len(lines) > 15:
            score += 5

        # --------------------------------------------------
        # 8. HARD PENALTIES (BROKEN OCR)
        # --------------------------------------------------
        if re.search(r"[~^|<>]{3,}", text):
            score -= 15

        if score < 0:
            score = 0

        return score
