from __future__ import annotations

from copy import deepcopy
from typing import Any

CHANNEL_A = "CHANNEL_A_MONEY_MINDSET_CONVERSION"
CHANNEL_D = "CHANNEL_D_AI_TECH_PERSONAL_BRAND"
CHANNEL_B = "CHANNEL_B_CURIOSITIES_MASS_TRAFFIC"
CHANNEL_C = "CHANNEL_C_MOTIVATION_DISCIPLINE_RETENTION"

CANONICAL_CHANNEL_IDS = [CHANNEL_A, CHANNEL_D, CHANNEL_B, CHANNEL_C]

AMBIGUOUS_ALIASES = {"channel_1", "money", "viral", "tech", "motivation", "main_channel", "general_channel"}

CHANNELS: dict[str, dict[str, Any]] = {
    CHANNEL_A: {
        "channel_id": CHANNEL_A,
        "channel_name": "Canal A — Dinero / Mentalidad / Conversión",
        "core_purpose": "convertir aprendizaje financiero y mentalidad en autoridad comercial futura",
        "primary_audience": "personas que quieren mejorar hábitos económicos y oportunidades digitales",
        "allowed_tone": ["directo", "práctico", "disciplinado"],
        "blocked_tone": ["promesa de riqueza rápida", "curiosidad genérica sin conversión"],
        "main_goal": "conversión futura gobernada",
        "risk_profile": "alto si promete resultados financieros sin evidencia",
    },
    CHANNEL_D: {
        "channel_id": CHANNEL_D,
        "channel_name": "Canal D — IA / Tech / Marca personal / Autoridad",
        "core_purpose": "construir autoridad profesional en IA, automatización y sistemas",
        "primary_audience": "profesionales y emprendedores interesados en tecnología aplicada",
        "allowed_tone": ["técnico claro", "autoridad", "evidencia"],
        "blocked_tone": ["motivación genérica", "venta técnica prematura"],
        "main_goal": "autoridad y venta futura",
        "risk_profile": "medio si promete resultados técnicos sin evidencia",
    },
    CHANNEL_B: {
        "channel_id": CHANNEL_B,
        "channel_name": "Canal B — Curiosidades / Tráfico masivo",
        "core_purpose": "captar atención masiva con curiosidad verificable",
        "primary_audience": "audiencia amplia de consumo rápido",
        "allowed_tone": ["curioso", "entretenido", "simple"],
        "blocked_tone": ["conversión agresiva", "monetización directa"],
        "main_goal": "tráfico masivo futuro",
        "risk_profile": "medio si usa datos no verificados",
    },
    CHANNEL_C: {
        "channel_id": CHANNEL_C,
        "channel_name": "Canal C — Motivación / Disciplina / Retención emocional",
        "core_purpose": "retener emocionalmente con disciplina, enfoque y resiliencia",
        "primary_audience": "personas que buscan motivación estructurada",
        "allowed_tone": ["emocional moderado", "disciplinado", "esperanzador"],
        "blocked_tone": ["presión emocional extrema", "promesas financieras"],
        "main_goal": "retención emocional futura",
        "risk_profile": "medio si invade Canal A con promesas económicas",
    },
}


def get_channels() -> dict[str, dict[str, Any]]:
    return deepcopy(CHANNELS)


def validate_channel_id(channel_id: str) -> dict[str, Any]:
    if channel_id in AMBIGUOUS_ALIASES:
        return {"status": "BLOCK", "reason": "AMBIGUOUS_CHANNEL_ALIAS", "channel_id": channel_id}
    if channel_id not in CHANNELS:
        return {"status": "BLOCK", "reason": "UNKNOWN_CHANNEL_ID", "channel_id": channel_id}
    return {"status": "PASS", "channel_id": channel_id}


def build_channel_registry() -> dict[str, Any]:
    return {"status": "PASS", "channels": get_channels(), "canonical_ids": list(CANONICAL_CHANNEL_IDS)}


def validate_channel_registry(registry: dict[str, Any] | None = None) -> dict[str, Any]:
    registry = registry or build_channel_registry()
    ids = list(registry.get("channels", {}).keys())
    missing = [channel_id for channel_id in CANONICAL_CHANNEL_IDS if channel_id not in ids]
    duplicates = len(ids) != len(set(ids))
    ambiguous = [channel_id for channel_id in ids if channel_id in AMBIGUOUS_ALIASES]
    missing_purpose = [channel_id for channel_id, data in registry.get("channels", {}).items() if not data.get("core_purpose")]
    ok = not missing and not duplicates and not ambiguous and not missing_purpose and len(ids) == 4
    return {"status": "PASS" if ok else "BLOCK", "missing": missing, "duplicates": duplicates, "ambiguous": ambiguous, "missing_purpose": missing_purpose}
