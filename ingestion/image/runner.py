import cv2
import tempfile
from backend.ingestion.image.ocr import run_doctr_ocr
from app.core.ocr_variant_selector import score_ocr_text


def run_best_ocr_variant(image_path: str, variants):
    """
    Runs OCR on selected enhancement variants
    and returns the best OCR text.
    """

    best_score = -1
    best_text = ""

    for name, img in variants:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            cv2.imwrite(tmp.name, img)
            text = run_doctr_ocr(tmp.name)

        score = score_ocr_text(text)

        # Debug hook (optional)
        # print(f"    OCR variant={name:8s} score={score}")

        if score > best_score:
            best_score = score
            best_text = text

    return best_text
