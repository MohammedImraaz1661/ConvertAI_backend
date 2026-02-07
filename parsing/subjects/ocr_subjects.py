# NOTE: OCR pipeline uses `code`; PDF pipeline uses `subject_code`
# Do not mix without normalization

import re
from typing import List, Dict
from itertools import permutations
from pathlib import Path


SUBJECT_CODE_REGEX = re.compile(r"\b[A-Z]{3,4}L?\d{3}[A-Z]?\b")
DATE_REGEX = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
RESULT_REGEX = re.compile(r"\b[PFAW]\b")
FOOTER_CUTOFF = re.compile(
    r"(NOMENCLATURE|NOTE\s*:|RESULTS OF|REGISTRAR|PAGE\s+\d+)",
    re.IGNORECASE
)


def split_into_subject_blocks(ocr_text: str) -> List[str]:
    """
    Splits OCR text into blocks using subject codes as anchors.
    """
    lines = [l.strip() for l in ocr_text.splitlines() if l.strip()]
    blocks = []
    current_block = []

    for line in lines:
        if SUBJECT_CODE_REGEX.search(line):
            if current_block:
                blocks.append(" ".join(current_block))
                current_block = []
        current_block.append(line)

    if current_block:
        blocks.append(" ".join(current_block))

    return blocks


def extract_marks(block: str) -> Dict:
    """
    Extraction-only marks logic with candidate filtering.
    """

    result = {
        "internal": None,
        "external": None,
        "total": None,
        "result": None,
        "date": None
    }

    # =================================================
    # PE FAST-PATH (MUST BE FIRST)
    # =================================================
    # Pattern: internal, 'U', total
    if "BPEK" in block or "PHYSICAL EDUCATION" in block.upper():
        nums = [int(n) for n in re.findall(r"\b\d{1,3}\b", block)
                if 0 <= int(n) <=100 ]
        if nums:
            pe_mark = max(nums)
            result["internal"] = pe_mark
            result["external"] = 0
            result["total"] = pe_mark
        # DO NOT return — allow result/date extraction below

    # -------------------------------
    # FOOTER CUT
    # -------------------------------
    fm = FOOTER_CUTOFF.search(block)
    if fm:
        block = block[:fm.start()]

    # -------------------------------
    # DATE
    # -------------------------------
    dm = DATE_REGEX.search(block)
    if dm:
        result["date"] = dm.group()
        block = block[:dm.start()]

    # -------------------------------
    # RESULT LETTER
    # -------------------------------
    rm = RESULT_REGEX.search(block)
    if rm:
        result["result"] = rm.group()
        block = block[:rm.start()]

    # -------------------------------
    # MERGED NUMBERS (5040 → 50,40)
    # -------------------------------
    merged_numbers = re.findall(r"\b\d{4}\b", block)
    split_numbers = []

    for m in merged_numbers:
        a, b = int(m[:2]), int(m[2:])
        if 0 <= a <= 50 and 0 <= b <= 50:
            split_numbers.extend([a, b])

    block = re.sub(r"\b\d{4}\b", "", block)

    # -------------------------------
    # CANDIDATE NUMBERS
    # -------------------------------
    numbers = [int(n) for n in re.findall(r"\b\d{1,3}\b", block)]

    # Candidate filtering: ignore single-digit noise except 0
    numbers = [
        n for n in numbers
        if (n == 0 or n >= 10) and n <= 100
    ]

    numbers.extend(split_numbers)

    # -------------------------------
    # PICK BEST (i, e, t)
    # -------------------------------
    # Skip if PE already resolved
    if result["internal"] is None:
        best_score = -1
        best_triplet = None

        for i, e, t in permutations(numbers, 3):
            if t > 100:
                continue
            if abs((i + e) - t) > 2:
                continue

            score = 0
            if t >= 36:
                score += 2
            if result["result"] == "P" and t >= 36:
                score += 2

            if score > best_score:
                best_score = score
                best_triplet = (i, e, t)

        if best_triplet:
            result["internal"], result["external"], result["total"] = best_triplet

    return result



def normalize_subject_block(block: str) -> Dict:
    """
    Extracts structured fields from a single subject block.
    """
    result = {
        "code": None,
        "internal": None,
        "external": None,
        "total": None,
        "result": None,
        "date": None
    }

    # ---------- Subject Code ----------
    code_match = SUBJECT_CODE_REGEX.search(block)
    if not code_match:
        return None

    result["code"] = code_match.group()

    # ---------- Marks ----------
    marks = extract_marks(block)
    result.update(marks)

    return result


def parse_vtu_table(ocr_text: str) -> List[Dict]:
    """
    Full VTU table parse (experimental).
    """
    rows = []
    blocks = split_into_subject_blocks(ocr_text)

    for block in blocks:
        row = normalize_subject_block(block)
        if row and row["code"]:
            rows.append(row)

    return rows


if __name__ == "__main__":
    ocr_text = (Path(__file__).parent / "sample_ocr_output.txt").read_text(
        encoding="utf-8"
    )

    rows = parse_vtu_table(ocr_text)

    for r in rows:
        print("--------------------------------------------------")
        for k, v in r.items():
            print(f"{k:10}: {v}")
