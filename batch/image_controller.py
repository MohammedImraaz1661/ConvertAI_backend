from pathlib import Path
import re
from backend.services.vtu_ocr_parser import parse_vtu_image

IMAGE_EXTS = {".jpg", ".jpeg", ".png"}


import re


USN_PATTERN = re.compile(r"\d[A-Z]{2}\d{2}[A-Z]{2}\d{3}")


def normalize_ai_usn(usn: str | None) -> str | None:
    """
    V1 AI-only USN normalizer.
    Fixes common OCR issue: A1 → AI
    Examples:
    - 4DM23A1039 -> 4DM23AI039
    - 4DM23AI039 -> 4DM23AI039 (unchanged)
    """

    if not usn:
        return None

    # Clean input
    cleaned = "".join(ch for ch in usn.upper() if ch.isalnum())

    # Pattern:
    # 4DM23A1039  -> group1=4DM23, group2=039
    match = re.match(r"^(\d[A-Z]{2}\d{2})A1(\d{3})$", cleaned)
    if match:
        return f"{match.group(1)}AI{match.group(2)}"

    # Already-correct AI USN
    if re.match(r"^\d[A-Z]{2}\d{2}AI\d{3}$", cleaned):
        return cleaned

    # Otherwise: leave as-is (do NOT guess)
    return cleaned


def collect_image_batch_results(image_root: str) -> list[dict]:
    """
    V1 Image batch rules:
    - Single image file = single student
    - Folder of images = multi-page student
    """

    results = []
    base = Path(image_root)

    for item in sorted(base.iterdir()):

        # 🖼️ CASE 1: Single image = single-page student
        if item.is_file() and item.suffix.lower() in IMAGE_EXTS:
            try:
                raw = parse_vtu_image([str(item)])

                normalized_usn = normalize_ai_usn(raw.get("usn"))
                if not normalized_usn:
                    print(f"⚠️ Skipping image (no USN): {item.name}")
                    continue

                result = {
                    "header": {
                        "usn": normalized_usn,
                        "name": raw.get("name"),
                    },
                    "subjects": raw.get("subjects", [])
                }

                results.append(result)

            except Exception as e:
                print(f"❌ Failed {item.name}: {e}")

        # 📂 CASE 2: Folder = multi-page student
        elif item.is_dir():
            images = sorted(
                str(p)
                for p in item.iterdir()
                if p.suffix.lower() in IMAGE_EXTS
            )

            if not images:
                continue

            try:
                raw = parse_vtu_image(images)

                normalized_usn = normalize_ai_usn(raw.get("usn"))
                if not normalized_usn:
                    print(f"⚠️ Skipping folder (no USN): {item.name}")
                    continue

                result = {
                    "header": {
                        "usn": normalized_usn,
                        "name": raw.get("name"),
                    },
                    "subjects": raw.get("subjects", [])
                }

                results.append(result)

            except Exception as e:
                print(f"❌ Failed folder {item.name}: {e}")

        # Ignore everything else
        else:
            continue

    return results
