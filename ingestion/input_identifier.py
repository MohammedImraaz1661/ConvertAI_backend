from pathlib import Path

IMAGE_EXTS = {".jpg", ".jpeg", ".png",}
PDF_EXTS = {".pdf"}
ZIP_EXTS = {".zip"}


def identify_input(paths: list[str]) -> dict:
    """
    Identify user input type and mode.

    Returns:
    {
        "type": "pdf" | "image" | "invalid",
        "mode": "single" | "batch" | None,
        "reason": str | None
    }
    """

    if not paths:
        return {
            "type": "invalid",
            "mode": None,
            "reason": "No files provided"
        }

    extensions = set()
    has_folder = False

    for p in paths:
        path = Path(p)
        if path.is_dir():
            has_folder = True
            for file in path.rglob("*"):
                if file.is_file():
                    extensions.add(file.suffix.lower())
        else:
            extensions.add(path.suffix.lower())

    # ---------------- PDF ----------------
    if extensions.issubset(PDF_EXTS):
        return {
            "type": "pdf",
            "mode": "single" if len(paths) == 1 else "batch",
            "reason": None
        }

    # ---------------- IMAGE ----------------
    if extensions.issubset(IMAGE_EXTS):
        return {
            "type": "image",
            "mode": "single" if len(paths) == 1 and not has_folder else "batch",
            "reason": None
        }

    # ---------------- ZIP ----------------
    if extensions.issubset(ZIP_EXTS):
        return {
            "type": "image",
            "mode": "batch",
            "reason": None
        }

    # ---------------- INVALID ----------------
    return {
        "type": "invalid",
        "mode": None,
        "reason": "Mixed or unsupported file types"
    }
