"""
⚠️ OCR / IMAGE PIPELINE MODULE
Not used in PDF-only V1 deployment.
Safe to ignore.
"""


class ResultAccumulator:
    def __init__(self):
        self.current_result = None
        self.final_results = []

    def process_page(self, extracted_data: dict):
        """
        extracted_data can be EITHER:

        OLD (regex/PDF):
        {
            "usn": "4DM23AI039",
            "name": "MUHAMMAD THASHREEF",
            "text": "BCS401 40 25 65 P\n..."
        }

        NEW (OCR):
        {
            "usn": "4DM23AI039",
            "name": "MUHAMMAD THASHREEF",
            "subjects": [
                {
                    "subject_code": "BCS401",
                    "internal": 40,
                    "external": 25,
                    "total": 65,
                    "result": "P"
                }
            ]
        }
        """

        subjects = self._extract_subjects(extracted_data)

        # 🔹 New result starts
        if extracted_data.get("usn"):
            # Finalize previous result if exists
            if self.current_result:
                self._finalize_current()

            self.current_result = {
                "usn": extracted_data["usn"],
                "name": extracted_data.get("name"),
                "subjects": subjects.copy()
            }

        # 🔹 Continuation page
        else:
            if not self.current_result:
                # Orphan continuation page — ignore
                return

            self.current_result["subjects"].extend(subjects)

    def finalize(self):
        """Call once after all pages are processed"""
        if self.current_result:
            self._finalize_current()

        return self.final_results

    # -----------------------
    # Internal helpers
    # -----------------------

    def _finalize_current(self):
        # Deduplicate subjects by subject_code (dict-safe)
        seen = set()
        unique_subjects = []

        for s in self.current_result["subjects"]:
            key = s.get("subject_code")
            if not key or key in seen:
                continue
            seen.add(key)
            unique_subjects.append(s)

        self.current_result["subjects"] = unique_subjects
        self.final_results.append(self.current_result)
        self.current_result = None

    def _extract_subjects(self, extracted_data: dict):
        """
        Handles BOTH text-based and dict-based subjects.
        """

        # ✅ OCR path (dict-based)
        if "subjects" in extracted_data and isinstance(extracted_data["subjects"], list):
            return extracted_data["subjects"]

        # ✅ Legacy path (regex/text-based)
        text = extracted_data.get("text", "")
        if not text:
            return []

        subjects = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) < 5:
                continue

            subjects.append({
                "subject_code": parts[0],
                "internal": int(parts[1]),
                "external": int(parts[2]),
                "total": int(parts[3]),
                "result": parts[4]
            })

        return subjects
