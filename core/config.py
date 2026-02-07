# core/config.py

SUBJECT_CODE_REGEX = r"[A-Z]{3,5}\d{3,4}[A-Z]?"
RESULT_REGEX = r"[PFAXW]"

CONFIDENCE_THRESHOLDS = {
    "OK": 0.85,
    "PARTIAL": 0.6
}
