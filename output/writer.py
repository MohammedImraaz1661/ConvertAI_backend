# backend/output/writer.py

import json
from pathlib import Path
from datetime import datetime


BASE_OUTPUT_DIR = Path(__file__).parent


def write_json(data: dict, subdir: str, filename: str):
    """
    Writes JSON output to backend/output/<subdir>/<filename>.json
    """
    out_dir = BASE_OUTPUT_DIR / subdir
    out_dir.mkdir(parents=True, exist_ok=True)

    path = out_dir / f"{filename}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return path
