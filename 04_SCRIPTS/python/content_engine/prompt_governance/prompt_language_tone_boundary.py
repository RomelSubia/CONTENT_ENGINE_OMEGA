from __future__ import annotations

from typing import Any

CHANNEL_LANGUAGE_TONE = {
    "CHANNEL_A_MONEY_MINDSET_CONVERSION": {
        "allowed_language": ["es-LatAm"],
        "allowed_tone": ["directo", "practico", "disciplinado"],
        "blocked_tone": ["venta_agresiva", "curiosidad_generica"],
    },
    "CHANNEL_D_AI_TECH_PERSONAL_BRAND": {
        "allowed_language": ["es-LatAm", "en-US"],
        "allowed_tone": ["tecnico_claro", "autoridad", "evidencia"],
        "blocked_tone": ["motivacional_generico", "venta_tecnica_prematura"],
    },
    "CHANNEL_B_CURIOSITIES_MASS_TRAFFIC": {
        "allowed_language": ["es-LatAm"],
        "allowed_tone": ["curioso", "entretenido", "simple"],
        "blocked_tone": ["conversion_agresiva", "monetizacion_directa"],
    },
    "CHANNEL_C_MOTIVATION_DISCIPLINE_RETENTION": {
        "allowed_language": ["es-LatAm"],
        "allowed_tone": ["emocional_moderado", "disciplinado", "esperanzador"],
        "blocked_tone": ["presion_extrema", "promesas_financieras"],
    },
}


def validate_language_tone(channel_id: str, language: str, tone: str) -> dict[str, Any]:
    profile = CHANNEL_LANGUAGE_TONE.get(channel_id)
    if not profile:
        return {"status": "BLOCK", "reason": "UNKNOWN_CHANNEL_ID"}
    if language not in profile["allowed_language"]:
        return {"status": "BLOCK", "reason": "LANGUAGE_NOT_ALLOWED_FOR_CHANNEL"}
    if tone in profile["blocked_tone"]:
        return {"status": "BLOCK", "reason": "TONE_BLOCKED_FOR_CHANNEL"}
    if tone not in profile["allowed_tone"]:
        return {"status": "BLOCK", "reason": "TONE_NOT_ALLOWED_FOR_CHANNEL"}
    return {"status": "PASS", "channel_id": channel_id, "language": language, "tone": tone}
