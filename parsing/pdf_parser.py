# backend/parsing/pdf_parser.py

import pdfplumber
from typing import List


def parse_pdf_by_page(pdf_path: str) -> List[str]:
    pages_text = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages_text.append(text)

    return pages_text
