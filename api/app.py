from flask import Flask, request, jsonify, send_file
from pathlib import Path
from flask_cors import CORS
import shutil
import uuid
import os
import traceback

from batch.run_batch import run_pdf_batch

# --------------------
# App setup
# --------------------
app = Flask(__name__)

# 🔒 Strong CORS (works even on errors)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=False
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend/
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Safe temp directory
TEMP_ROOT = Path(BASE_DIR) / "temp"
TEMP_ROOT.mkdir(exist_ok=True)

TEMPLATE_MAP = {
    "3": "3rd Sem.xlsx",
    "4": "4th Sem.xlsx",
    "5": "5th Sem.xlsx",
    "7": "7th Sem.xlsx",
}

# --------------------
# Routes
# --------------------
@app.route("/upload", methods=["POST"])
def upload():
    session_dir = None

    try:
        files = request.files.getlist("files")
        semester = request.form.get("semester")

        if not files:
            return jsonify({"error": "No files uploaded"}), 400

        if not semester:
            return jsonify({"error": "Semester not selected"}), 400

        # PDF ONLY (V1)
        for f in files:
            if not f.filename.lower().endswith(".pdf"):
                return jsonify({
                    "error": "Only PDF files are supported in V1"
                }), 400

        template_name = TEMPLATE_MAP.get(semester)
        if not template_name:
            return jsonify({"error": "Invalid semester selected"}), 400

        template_path = os.path.join(TEMPLATES_DIR, template_name)
        if not os.path.exists(template_path):
            return jsonify({"error": "Template file not found"}), 500

        # Create session folder
        session_dir = TEMP_ROOT / str(uuid.uuid4())
        session_dir.mkdir(parents=True, exist_ok=True)

        # Save PDFs
        for file in files:
            file.save(session_dir / file.filename)

        # Run batch processor
        output_excel = run_pdf_batch(session_dir, template_path)

        # ✅ Return file cleanly
        return send_file(
            output_excel,
            as_attachment=True,
            download_name="VTU_Result.xlsx"
        )

    except Exception as e:
        # 🔥 CRITICAL: log full traceback in Render
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    finally:
        # Cleanup AFTER response is prepared
        if session_dir and session_dir.exists():
            shutil.rmtree(session_dir, ignore_errors=True)


if __name__ == "__main__":
    app.run(debug=True)
