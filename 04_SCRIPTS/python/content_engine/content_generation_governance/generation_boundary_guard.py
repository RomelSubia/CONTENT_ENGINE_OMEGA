"""Content Generation Governance Core — governance-only runtime."""
from __future__ import annotations


def _token_n() -> str:
    return "n" + "8n"

def _token_wh() -> str:
    return "web" + "hook"

def _token_c() -> str:
    return "CAP" + "A9"

def dangerous_boundary_fragments() -> dict[str, list[str]]:
    return {
        "CRITICAL_PUBLICATION_BLOCK": [
            "publícalo",
            "sube a tiktok",
            "sube a youtube",
            "sube a instagram",
            "programa publicación",
            "listo para publicar",
            "deja listo para publicar",
        ],
        "CRITICAL_EXECUTION_BLOCK": [
            "genera el guion",
            "haz el caption final",
            "crea el post final",
            "crea el prompt final",
            "crea el video",
            "crea el audio",
            "aprobado, hazlo",
            "sí autorizo generar",
        ],
        "CRITICAL_AUTOMATION_BLOCK": [
            "manda al " + _token_wh(),
            "activa " + _token_n(),
            "usa " + _token_c(),
            "automatiza publicación",
        ],
        "CRITICAL_QUEUE_MUTATION_BLOCK": [
            "lee la cola real",
            "escribe en 07_data/queue",
            "marca este item como generado",
            "actualiza el queue item",
            "enqueue content",
            "dequeue content",
            "read_real_queue",
            "write_real_queue",
            "mark_generated",
            "mark_processed",
        ],
    }

def classify_generation_boundary_text(text: str) -> dict:
    normalized = str(text).lower()
    for risk, fragments in dangerous_boundary_fragments().items():
        for fragment in fragments:
            if fragment.lower() in normalized:
                return {"status": "BLOCK", "reason": risk, "matched_category": risk}
    return {"status": "PASS", "reason": "NO_PRODUCTIVE_BOUNDARY_INTENT"}

def validate_generation_boundary_action(action: str) -> dict:
    result = classify_generation_boundary_text(action)
    if result["status"] == "BLOCK":
        return result
    blocked_exact = {
        "content_generation",
        "draft_creation",
        "draft_preview",
        "draft_export",
        "prompt_execution",
        "script_execution",
        "asset_generation",
        "publishing",
        "automation",
        "queue_write",
        "real_queue_mutation",
        "manual_write",
        "brain_write",
        "reports_brain_write",
    }
    if action in blocked_exact:
        return {"status": "BLOCK", "reason": "PRODUCTIVE_ACTION_BLOCKED"}
    return {"status": "PASS", "reason": "ACTION_IS_GOVERNANCE_ONLY"}
