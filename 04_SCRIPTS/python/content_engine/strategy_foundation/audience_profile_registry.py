from __future__ import annotations

from typing import Any

from .channel_registry import CHANNEL_A, CHANNEL_B, CHANNEL_C, CHANNEL_D, CANONICAL_CHANNEL_IDS

SENSITIVE_MARKERS = {
    "cedula",
    "ssn",
    "religion",
    "ethnicity",
    "health diagnosis",
    "exact address",
    "exact_address",
    "exact-address",
    "phone",
}

AUDIENCES = [
    {"audience_id": "AUD_A_DISCIPLINA_ECONOMICA", "channel_id": CHANNEL_A, "awareness_level": "problem-aware", "pain_points": ["desorden financiero"], "desires": ["mejor control"], "objections": ["miedo a empezar"], "language_style": "directo", "attention_span": "medio", "content_depth": "práctico", "trust_level_required": "medio", "conversion_readiness_future": "media"},
    {"audience_id": "AUD_D_PROFESIONAL_TECH", "channel_id": CHANNEL_D, "awareness_level": "solution-aware", "pain_points": ["falta de sistemas"], "desires": ["automatizar"], "objections": ["complejidad técnica"], "language_style": "claro técnico", "attention_span": "alto", "content_depth": "medio-alto", "trust_level_required": "alto", "conversion_readiness_future": "media"},
    {"audience_id": "AUD_B_CURIOSIDAD_RAPIDA", "channel_id": CHANNEL_B, "awareness_level": "unaware", "pain_points": ["aburrimiento"], "desires": ["aprender rápido"], "objections": ["poco tiempo"], "language_style": "simple", "attention_span": "bajo", "content_depth": "ligero", "trust_level_required": "bajo", "conversion_readiness_future": "baja"},
    {"audience_id": "AUD_C_DISCIPLINA_PERSONAL", "channel_id": CHANNEL_C, "awareness_level": "problem-aware", "pain_points": ["falta de constancia"], "desires": ["disciplina"], "objections": ["cansancio"], "language_style": "emocional moderado", "attention_span": "medio", "content_depth": "medio", "trust_level_required": "medio", "conversion_readiness_future": "baja"},
]


def _normalized_text(value: object) -> str:
    text = str(value).lower()
    return text.replace("_", " ").replace("-", " ")


def _contains_sensitive_marker(audience: dict[str, Any]) -> bool:
    raw = str(audience).lower()
    normalized = _normalized_text(audience)
    normalized_markers = {_normalized_text(marker) for marker in SENSITIVE_MARKERS}
    return any(marker in raw or marker in normalized for marker in normalized_markers)


def build_audience_registry() -> dict[str, Any]:
    return {"status": "PASS", "audiences": list(AUDIENCES), "personal_data_allowed": False}


def validate_audiences(audiences: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    audiences = audiences or list(AUDIENCES)
    without_channel = [aud for aud in audiences if aud.get("channel_id") not in CANONICAL_CHANNEL_IDS]
    invasive = [aud.get("audience_id") for aud in audiences if _contains_sensitive_marker(aud)]
    missing = [aud.get("audience_id") for aud in audiences if not aud.get("pain_points") or not aud.get("desires")]
    return {"status": "PASS" if not without_channel and not invasive and not missing else "BLOCK", "without_channel": without_channel, "invasive": invasive, "missing": missing}
