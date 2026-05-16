from __future__ import annotations

from .queue_failure_policy import PASS, BLOCK

VALID_CHANNEL_IDS = frozenset({
    "CHANNEL_A_MONEY_MINDSET_CONVERSION",
    "CHANNEL_D_AI_TECH_PERSONAL_BRAND",
    "CHANNEL_B_CURIOSITIES_MASS_TRAFFIC",
    "CHANNEL_C_MOTIVATION_DISCIPLINE_RETENTION",
})

CHANNEL_KEYWORDS = {
    "CHANNEL_A_MONEY_MINDSET_CONVERSION": ("dinero", "venta", "conversión", "conversion", "negocio", "ingresos"),
    "CHANNEL_D_AI_TECH_PERSONAL_BRAND": ("ia", "ai", "automatización", "automatizacion", "tech", "marca personal"),
    "CHANNEL_B_CURIOSITIES_MASS_TRAFFIC": ("curiosidad", "dato curioso", "viral", "historia sorprendente"),
    "CHANNEL_C_MOTIVATION_DISCIPLINE_RETENTION": ("motivación", "motivacion", "disciplina", "hábitos", "habitos"),
}


def validate_channel_id(channel_id: str) -> dict:
    normalized = str(channel_id or "").strip().upper()
    if normalized in VALID_CHANNEL_IDS:
        return {"status": PASS, "channel_id": normalized}
    return {"status": BLOCK, "reason": "QUEUE_CHANNEL_UNKNOWN", "channel_id": normalized}


def _field_text(payload: dict, key: str) -> str:
    return str(payload.get(key, "")).lower()


def _combined_text(payload: dict) -> str:
    return " ".join(
        str(payload.get(key, ""))
        for key in ("idea_title", "idea_summary", "content_intent")
    ).lower()


def detect_cross_channel_contamination(payload: dict) -> dict:
    channel = str(payload.get("channel_id", "")).strip().upper()
    validation = validate_channel_id(channel)
    if validation.get("status") == BLOCK:
        return validation

    text = _combined_text(payload)
    summary = _field_text(payload, "idea_summary")

    if channel == "CHANNEL_B_CURIOSITIES_MASS_TRAFFIC" and any(token in text for token in ("compra ahora", "vende", "cierra venta", "conversión agresiva")):
        return {"status": BLOCK, "reason": "QUEUE_CHANNEL_CONTAMINATION"}

    if channel == "CHANNEL_C_MOTIVATION_DISCIPLINE_RETENTION" and any(token in text for token in ("ganar dinero garantizado", "hazte rico", "ingresos garantizados")):
        return {"status": BLOCK, "reason": "QUEUE_CHANNEL_CONTAMINATION"}

    if channel == "CHANNEL_D_AI_TECH_PERSONAL_BRAND":
        if "motivación genérica" in summary or "motivacion generica" in summary:
            return {"status": BLOCK, "reason": "QUEUE_CHANNEL_CONTAMINATION"}

    if channel == "CHANNEL_A_MONEY_MINDSET_CONVERSION" and "dato curioso sin conversión" in text:
        return {"status": BLOCK, "reason": "QUEUE_CHANNEL_CONTAMINATION"}

    return {"status": PASS, "reason": "NO_CHANNEL_CONTAMINATION"}


def route_queue_candidate(payload: dict) -> dict:
    channel_result = validate_channel_id(payload.get("channel_id", ""))
    if channel_result.get("status") == BLOCK:
        return channel_result
    contamination = detect_cross_channel_contamination(payload)
    if contamination.get("status") == BLOCK:
        return contamination
    return {"status": PASS, "channel_id": channel_result["channel_id"], "routing": "ROUTED_TO_CHANNEL"}
