"""
⚠️ OCR / IMAGE PIPELINE MODULE
Not used in PDF-only V1 deployment.
Safe to ignore.
"""


def dedupe_subjects(subjects):
    """
    Deduplicate subjects by subject code.
    Last occurrence wins (safe for continuations).
    """
    seen = {}
    for s in subjects:
        code = s.get("code")
        if code:
            seen[code] = s
    return list(seen.values())


def merge_page_results(page_results):
    """
    Merge page-level OCR results into final VTU results.

    Rule:
    - Page WITH header.usn → start new document
    - Page WITHOUT header.usn → continuation of previous document
    """

    merged_results = []
    current_doc = None

    for page in page_results:
        data = page.get("data", {})
        header = data.get("header")
        subjects = data.get("subjects", [])

        # New document starts when header + USN is present
        if header and header.get("usn"):
            current_doc = {
                "header": header,
                "subjects": []
            }
            merged_results.append(current_doc)

        # Safety: orphan continuation page
        if current_doc is None:
            continue

        # Append subjects
        current_doc["subjects"].extend(subjects)

    # De-duplicate subjects in each merged doc
    for doc in merged_results:
        doc["subjects"] = dedupe_subjects(doc["subjects"])

    return merged_results
