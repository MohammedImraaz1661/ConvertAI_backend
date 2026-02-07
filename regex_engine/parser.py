from app.regex_engine.header_regex import extract_header
from app.regex_engine.subject_regex import extract_subjects
from app.regex_engine.confidence import (
    compute_confidence,
    flag_from_confidence
)


def run_regex_pipeline(text: str) -> dict:
    header = extract_header(text)
    subjects = extract_subjects(text)

    processed_subjects = []

    for subj in subjects:
        confidence = compute_confidence(subj)
        processed_subjects.append({
            **subj,
            "confidence": confidence,
            "flag": flag_from_confidence(confidence)
        })

    return {
        "header": header,
        "subjects": processed_subjects
    }
