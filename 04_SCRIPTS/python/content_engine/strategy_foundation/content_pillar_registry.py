from __future__ import annotations

from typing import Any

from .channel_registry import CHANNEL_A, CHANNEL_B, CHANNEL_C, CHANNEL_D, CANONICAL_CHANNEL_IDS

PILLARS = [
    {"pillar_id": "A_MENTALIDAD_FINANCIERA", "channel_id": CHANNEL_A, "pillar_name": "Mentalidad financiera", "pillar_purpose": "disciplina económica", "blocked_channel_ids": [CHANNEL_B, CHANNEL_C]},
    {"pillar_id": "A_HABITOS_DINERO", "channel_id": CHANNEL_A, "pillar_name": "Hábitos de dinero", "pillar_purpose": "hábitos prácticos", "blocked_channel_ids": [CHANNEL_B]},
    {"pillar_id": "A_OPORTUNIDADES_DIGITALES", "channel_id": CHANNEL_A, "pillar_name": "Oportunidades digitales", "pillar_purpose": "oportunidades futuras sin promesas", "blocked_channel_ids": [CHANNEL_B, CHANNEL_C]},
    {"pillar_id": "A_CONVERSION_FUTURA", "channel_id": CHANNEL_A, "pillar_name": "Conversión futura", "pillar_purpose": "monetización futura no ejecutable", "blocked_channel_ids": [CHANNEL_B, CHANNEL_C]},
    {"pillar_id": "D_IA_APLICADA", "channel_id": CHANNEL_D, "pillar_name": "IA aplicada", "pillar_purpose": "autoridad técnica", "blocked_channel_ids": [CHANNEL_C]},
    {"pillar_id": "D_AUTOMATIZACION", "channel_id": CHANNEL_D, "pillar_name": "Automatización", "pillar_purpose": "sistemas digitales", "blocked_channel_ids": [CHANNEL_C]},
    {"pillar_id": "D_MARCA_PERSONAL", "channel_id": CHANNEL_D, "pillar_name": "Marca personal tech", "pillar_purpose": "autoridad", "blocked_channel_ids": [CHANNEL_B]},
    {"pillar_id": "D_SISTEMAS", "channel_id": CHANNEL_D, "pillar_name": "Sistemas", "pillar_purpose": "arquitectura y procesos", "blocked_channel_ids": [CHANNEL_C]},
    {"pillar_id": "B_CURIOSIDADES", "channel_id": CHANNEL_B, "pillar_name": "Curiosidades", "pillar_purpose": "tráfico masivo", "blocked_channel_ids": [CHANNEL_A]},
    {"pillar_id": "B_DATOS_SORPRENDENTES", "channel_id": CHANNEL_B, "pillar_name": "Datos sorprendentes", "pillar_purpose": "retención inicial", "blocked_channel_ids": [CHANNEL_A]},
    {"pillar_id": "B_HISTORIAS_BREVES", "channel_id": CHANNEL_B, "pillar_name": "Historias breves", "pillar_purpose": "aprendizaje entretenido", "blocked_channel_ids": [CHANNEL_A]},
    {"pillar_id": "B_APRENDIZAJE_ENTRETENIDO", "channel_id": CHANNEL_B, "pillar_name": "Aprendizaje entretenido", "pillar_purpose": "educación simple", "blocked_channel_ids": [CHANNEL_A]},
    {"pillar_id": "C_DISCIPLINA", "channel_id": CHANNEL_C, "pillar_name": "Disciplina", "pillar_purpose": "retención emocional", "blocked_channel_ids": [CHANNEL_A]},
    {"pillar_id": "C_RESILIENCIA", "channel_id": CHANNEL_C, "pillar_name": "Resiliencia", "pillar_purpose": "fortaleza emocional", "blocked_channel_ids": [CHANNEL_A]},
    {"pillar_id": "C_ENFOQUE", "channel_id": CHANNEL_C, "pillar_name": "Enfoque", "pillar_purpose": "claridad personal", "blocked_channel_ids": [CHANNEL_A]},
    {"pillar_id": "C_MOTIVACION_ESTRUCTURADA", "channel_id": CHANNEL_C, "pillar_name": "Motivación estructurada", "pillar_purpose": "motivación sin presión extrema", "blocked_channel_ids": [CHANNEL_A]},
]


def build_pillar_registry() -> dict[str, Any]:
    return {"status": "PASS", "pillars": list(PILLARS)}


def validate_pillars(pillars: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    pillars = pillars or list(PILLARS)
    ids = [pillar.get("pillar_id") for pillar in pillars]
    duplicate = len(ids) != len(set(ids))
    without_channel = [pillar for pillar in pillars if pillar.get("channel_id") not in CANONICAL_CHANNEL_IDS]
    missing_purpose = [pillar for pillar in pillars if not pillar.get("pillar_purpose")]
    counts = {channel: 0 for channel in CANONICAL_CHANNEL_IDS}
    for pillar in pillars:
        if pillar.get("channel_id") in counts:
            counts[pillar["channel_id"]] += 1
    count_failures = {channel: count for channel, count in counts.items() if count < 4 or count > 8}
    ok = not duplicate and not without_channel and not missing_purpose and not count_failures
    return {"status": "PASS" if ok else "BLOCK", "duplicate": duplicate, "without_channel": without_channel, "missing_purpose": missing_purpose, "count_failures": count_failures}
