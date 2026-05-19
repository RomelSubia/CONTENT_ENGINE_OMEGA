"""Content Generation Governance Core — governance-only runtime."""
from __future__ import annotations


def near_final_fragments() -> list[str]:
    return [
        "ejemplo de hook",
        "ejemplo de caption",
        "ejemplo de guion",
        "texto sugerido",
        "copy sugerido",
        "borrador no final",
        "muestra tentativa",
        "haz el caption",
        "cta final",
        "hashtags",
        "estructura de video",
        "guion completo",
        "prompt final",
        "texto listo para copiar",
        "abrir con hook",
        "dar tres consejos",
        "cerrar con cta",
        "introducción, desarrollo y cierre",
    ]

def validate_no_near_final_content(text: str) -> dict:
    normalized = str(text).lower()
    matched = [fragment for fragment in near_final_fragments() if fragment.lower() in normalized]
    if matched:
        return {"status": "BLOCK", "reason": "NEAR_FINAL_OR_SAMPLE_CONTENT_BLOCKED", "matched": matched[:5]}
    return {"status": "PASS", "reason": "NO_NEAR_FINAL_CONTENT_DETECTED"}

def validate_checklist_non_creative(items: list[str]) -> dict:
    violations = []
    for item in items:
        result = validate_no_near_final_content(item)
        if result["status"] == "BLOCK":
            violations.append(item)
    if violations:
        return {"status": "BLOCK", "reason": "CREATIVE_CHECKLIST_BLOCKED", "violations": violations}
    return {"status": "PASS", "reason": "CHECKLIST_NON_CREATIVE"}
