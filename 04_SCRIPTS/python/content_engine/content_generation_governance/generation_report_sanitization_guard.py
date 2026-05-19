"""Content Generation Governance Core — governance-only runtime."""
from __future__ import annotations


from .generation_near_final_content_guard import validate_no_near_final_content

def validate_report_payload_sanitized(payload: dict) -> dict:
    violations = []
    def walk(value, path="root"):
        if isinstance(value, dict):
            for key, item in value.items():
                walk(item, f"{path}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{path}[{index}]")
        elif isinstance(value, str):
            result = validate_no_near_final_content(value)
            if result["status"] == "BLOCK":
                violations.append({"path": path, "reason": result["reason"]})
    walk(payload)
    if violations:
        return {"status": "BLOCK", "reason": "REPORT_CONTENT_SANITIZATION_REQUIRED", "violations": violations[:5]}
    return {"status": "PASS", "reason": "REPORT_PAYLOAD_SANITIZED"}
