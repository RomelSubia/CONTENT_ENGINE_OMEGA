from __future__ import annotations

from typing import Any

FAMILY_PATTERNS = {
    "GENERATION_FINAL_OUTPUT": ["guion final", "caption final", "post final", "contenido final", "listo para grabar"],
    "QUEUE_OPERATION": ["cola", "queue", "programar publicacion"],
    "METRICS_OPERATION": ["metricas reales", "actualiza metricas", "leer analytics"],
    "ASSET_OPERATION": ["crea asset", "genera video", "sube video", "thumbnail final"],
    "PUBLISHING_OPERATION": ["publica ahora", "listo para publicar", "subelo", "upload"],
    "AUTOMATION_OPERATION": ["activa el flujo", "trigger workflow", "ejecuta automatizacion"],
    "WEBHOOK_OPERATION": ["webhook", "call webhook", "dispara webhook"],
    "CAPA9_OPERATION": ["activa capa9", "capa9"],
    "MANUAL_WRITE_OPERATION": ["actualiza el manual", "write manual"],
    "BRAIN_WRITE_OPERATION": ["escribe en el cerebro", "write brain"],
    "REPORTS_BRAIN_WRITE_OPERATION": ["reports brain", "reportes brain"],
    "POLICY_OVERRIDE_OPERATION": ["ignora las reglas", "omite evidencia", "simula aprobacion"],
}


def normalize(text: str) -> str:
    return text.lower().replace("_", " ").replace("-", " ")


def classify_semantic_safety(text: str) -> dict[str, Any]:
    normalized = normalize(text)
    matched = []
    for family, patterns in FAMILY_PATTERNS.items():
        if any(pattern in normalized for pattern in patterns):
            matched.append(family)
    if matched:
        return {"status": "BLOCK", "reason": "PROMPT_SEMANTIC_SAFETY_VIOLATION", "families": matched}
    return {"status": "PASS", "families": []}
