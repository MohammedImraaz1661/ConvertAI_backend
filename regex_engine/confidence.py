# regex_engine/confidence.py

def compute_confidence(subject: dict) -> float:
    score = 0.0

    if subject.get("subject_code"):
        score += 0.4
    if subject.get("internal") is not None:
        score += 0.2
    if subject.get("external") is not None:
        score += 0.2
    if subject.get("total") is not None:
        score += 0.1
    if subject.get("result"):
        score += 0.1

    return round(score, 2)


def flag_from_confidence(confidence: float) -> str:
    if confidence >= 0.85:
        return "OK"
    elif confidence >= 0.6:
        return "PARTIAL"
    return "REVIEW"
