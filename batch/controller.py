from pathlib import Path
from services.vtu_pdf_parser import parse_vtu_pdf
from services.vtu_ocr_parser import parse_vtu_image

TARGET_USN = "4DM23AI039"

# NOTE: In V1 deployment, this is used in PDF-only mode.


def collect_batch_results(input_path: str) -> list[dict]:
    results = []
    base = Path(input_path)

    for item in sorted(base.iterdir()):
        if item.is_file() and item.suffix.lower() == ".pdf":
            print(f"Processing PDF: {item.name}")
            result = parse_vtu_pdf(str(item))
            results.append(result)

        elif item.is_dir():
            print(f"Processing images: {item.name}")
            images = sorted(
                str(p) for p in item.iterdir()
                if p.suffix.lower() in [".jpg", ".png", ".jpeg"]
            )
            if images:
                result = parse_vtu_image(images)
                results.append(result)

    return results
