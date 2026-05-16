from __future__ import annotations

from typing import Any

RISK_POLICY = {
    "LOW": "ALLOW_WITH_EVIDENCE",
    "MEDIUM": "ALLOW_WITH_BOUNDARY_CHECKS",
    "HIGH": "ALLOW_ONLY_AS_CONCEPTUAL_STRUCTURE",
    "CRITICAL": "BLOCK",
}

CRITICAL_PHRASES = {
    "final script",
    "script final",
    "publishable content",
    "ready to publish",
    "ready publish",
    "ready post",
    "ready caption",
    "ready metadata",
    "ready upload",
    "queue item",
    "production prompt",
    "production pack",
    "asset ready",
    "ready asset",
}

CRITICAL_TOKENS = {"publish", "queue", "asset", "automation", "webhook", "capa9"}


def _normalize(value: str) -> str:
    return " ".join(
        value.lower()
        .replace("_", " ")
        .replace("-", " ")
        .replace("/", " ")
        .split()
    )


def _has_non_final_marker(material: str) -> bool:
    return any(
        marker in material
        for marker in [
            "non final",
            "not final",
            "nonfinal",
            "conceptual",
            "structure",
            "structural",
            "template",
            "outline",
            "schema",
        ]
    )


def classify_prompt_risk(prompt_type: str, expected_output: str, automation_trigger: bool = False) -> dict[str, Any]:
    material = _normalize(f"{prompt_type} {expected_output}")

    if automation_trigger:
        level = "CRITICAL"
    elif any(phrase in material for phrase in CRITICAL_PHRASES):
        level = "CRITICAL"
    elif "final" in material and not _has_non_final_marker(material):
        level = "CRITICAL"
    elif any(token in material.split() for token in CRITICAL_TOKENS):
        level = "CRITICAL"
    elif "script" in material or "cta" in material or "conversion" in material:
        level = "HIGH"
    elif "hook" in material or "metadata" in material or "adaptation" in material:
        level = "MEDIUM"
    else:
        level = "LOW"

    policy = RISK_POLICY[level]
    return {"status": "BLOCK" if policy == "BLOCK" else "PASS", "risk_level": level, "policy": policy}
