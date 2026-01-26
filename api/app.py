from flask import Flask, request, send_file, jsonify
from pathlib import Path
import tempfile
import shutil
import zipfile
from flask_cors import CORS

# -------------------------
# IMPORT YOUR LOGIC
# -------------------------
from backend.ingestion.input_identifier import identify_input
from backend.batch.run_image_batch import run_image_batch
from backend.batch.run_batch import run_pdf_batch

app = Flask(__name__)
CORS(app)

# -------------------------
# TEMP UPLOAD DIR
# -------------------------
BASE_TEMP = Path(tempfile.gettempdir()) / "convert_ai"
BASE_TEMP.mkdir(exist_ok=True)


@app.route("/upload", methods=["POST"])
def upload():
    # 1️⃣ Validate input
    if "files" not in request.files:
        return jsonify({"error": "No files field found"}), 400

    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    # 2️⃣ Create session directory
    session_dir = BASE_TEMP / next(tempfile._get_candidate_names())
    session_dir.mkdir()

    saved_paths = []

    try:
        # 3️⃣ Save uploaded files
        for f in files:
            save_path = session_dir / f.filename
            f.save(save_path)
            saved_paths.append(save_path)

        # 4️⃣ HANDLE ZIP FILES (NEW)
        extracted_paths = []

        for path in saved_paths:
            if path.suffix.lower() == ".zip":
                extract_dir = session_dir / path.stem
                extract_dir.mkdir(exist_ok=True)

                with zipfile.ZipFile(path, "r") as zip_ref:
                    zip_ref.extractall(extract_dir)

                extracted_paths.append(str(extract_dir))
            else:
                extracted_paths.append(str(path))

        # 5️⃣ Identify input (AFTER extraction)
        identification = identify_input(extracted_paths)

        if identification["type"] == "invalid":
            return jsonify({
                "error": identification["reason"]
            }), 400

        # 6️⃣ Route pipeline
        if identification["type"] == "image":
            output_excel = run_image_batch(session_dir)

        elif identification["type"] == "pdf":
            output_excel = run_pdf_batch(session_dir)

        else:
            return jsonify({"error": "Unsupported input"}), 400

        # 7️⃣ Auto-download Excel
        return send_file(
            output_excel,
            as_attachment=True,
            download_name="results.xlsx"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Cleanup (disable temporarily if debugging)
        shutil.rmtree(session_dir, ignore_errors=True)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
