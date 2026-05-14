from __future__ import annotations

from typing import Any

from .channel_registry import CHANNEL_A, CHANNEL_B, CHANNEL_C, CHANNEL_D, CANONICAL_CHANNEL_IDS

ALLOWED_BRIDGES = {
    (CHANNEL_A, CHANNEL_C): "disciplina económica sin promesa financiera",
    (CHANNEL_D, CHANNEL_A): "IA aplicada a negocio sin venta directa prematura",
    (CHANNEL_B, CHANNEL_D): "curiosidad tecnológica verificada sin autoridad falsa",
}

BLOCKED_MIXES = {
    (CHANNEL_A, CHANNEL_B): "conversión financiera no debe volverse curiosidad genérica",
    (CHANNEL_B, CHANNEL_A): "tráfico masivo no debe activar conversión agresiva",
    (CHANNEL_C, CHANNEL_A): "motivación no debe prometer resultados financieros",
    (CHANNEL_D, CHANNEL_C): "autoridad técnica no debe diluirse en motivación genérica",
}


def build_separation_matrix() -> dict[str, Any]:
    return {"status": "PASS", "canonical_channels": list(CANONICAL_CHANNEL_IDS), "allowed_bridges": {f"{a}->{b}": v for (a, b), v in ALLOWED_BRIDGES.items()}, "blocked_mixes": {f"{a}->{b}": v for (a, b), v in BLOCKED_MIXES.items()}}


def validate_channel_mix(source_channel: str, target_channel: str, has_bridge_rule: bool = False) -> dict[str, Any]:
    if source_channel == target_channel:
        return {"status": "PASS", "reason": "SAME_CHANNEL"}
    if (source_channel, target_channel) in BLOCKED_MIXES and not has_bridge_rule:
        return {"status": "BLOCK", "reason": "CHANNEL_CONTAMINATION_BLOCKED"}
    if (source_channel, target_channel) in ALLOWED_BRIDGES and has_bridge_rule:
        return {"status": "PASS", "reason": "ALLOWED_BRIDGE"}
    if not has_bridge_rule:
        return {"status": "BLOCK", "reason": "MISSING_BRIDGE_RULE"}
    return {"status": "PASS", "reason": "EXPLICIT_BRIDGE_REVIEW"}
