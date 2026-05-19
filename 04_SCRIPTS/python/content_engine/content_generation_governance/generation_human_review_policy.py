"""Content Generation Governance Core — governance-only runtime."""
from __future__ import annotations


from .generation_boundary_guard import classify_generation_boundary_text

def require_human_review(payload: dict | None = None) -> dict:
    return {
        "status": "PASS",
        "reason": "HUMAN_REVIEW_REQUIRED",
        "human_review_required": True,
        "generation_allowed_now": False,
    }

def validate_human_review_not_authorization(text: str) -> dict:
    lowered = str(text).lower()
    bypasses = ["sí autorizo generar", "aprobado", "hazlo", "puedes generar", "sin revisión humana", "omite policy review", "omite risk review"]
    if any(item in lowered for item in bypasses):
        return {"status": "BLOCK", "reason": "HUMAN_REVIEW_IS_NOT_AUTHORIZATION"}
    boundary = classify_generation_boundary_text(text)
    if boundary["status"] == "BLOCK":
        return boundary
    return require_human_review()
