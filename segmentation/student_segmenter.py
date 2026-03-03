# backend/segmentation/student_segmenter.py

import re
from typing import List

# Use YOUR existing USN regex here
USN_REGEX = re.compile(
    r"\b\d{1,2}[A-Z]{2}\d{2}[A-Z]{2}\d{3}\b",  # example VTU pattern
    re.IGNORECASE
)

MAX_PAGES_PER_STUDENT = 2


def contains_usn(text: str) -> bool:
    """
    Checks whether a page contains a USN.
    This marks the start of a new student.
    """
    if not text:
        return False
    return bool(USN_REGEX.search(text))


def segment_students_from_pages(pages_text: List[str]) -> List[str]:
    """
    Segments merged PDF page texts into student-wise text blocks.

    Input:
        pages_text -> list of page-level extracted text

    Output:
        list of student-wise combined text (1 student per item)
    """

    students: List[str] = []
    current_student_pages: List[str] = []

    for page_text in pages_text:

        # Detect start of a new student
        if contains_usn(page_text):
            if current_student_pages:
                students.append("\n".join(current_student_pages))
                current_student_pages = []

        current_student_pages.append(page_text)

        # Safety cap: VTU results span max 2 pages
        if len(current_student_pages) >= MAX_PAGES_PER_STUDENT:
            students.append("\n".join(current_student_pages))
            current_student_pages = []

    # Flush last student
    if current_student_pages:
        students.append("\n".join(current_student_pages))

    return students
