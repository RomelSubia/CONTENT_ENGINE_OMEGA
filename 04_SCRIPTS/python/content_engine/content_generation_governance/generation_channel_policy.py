"""Content Generation Governance Core — governance-only runtime."""
from __future__ import annotations


CHANNEL_REQUIRED_REVIEWS = {
    "CHANNEL_A_MONEY_MINDSET_CONVERSION": ["claim_review", "conversion_ethics_review", "policy_review", "risk_review"],
    "CHANNEL_D_AI_TECH_PERSONAL_BRAND": ["technical_accuracy_review", "tool_claim_review", "risk_review"],
    "CHANNEL_B_CURIOSITIES_MASS_TRAFFIC": ["fact_check_review", "source_review"],
    "CHANNEL_C_MOTIVATION_DISCIPLINE_RETENTION": ["human_safety_review", "tone_review"],
}

def validate_channel_specific_policy(candidate: dict) -> dict:
    channel = candidate.get("channel_id")
    text = f"{candidate.get('idea_title','')} {candidate.get('idea_summary','')}".lower()
    if channel not in CHANNEL_REQUIRED_REVIEWS:
        return {"status": "BLOCK", "reason": "UNKNOWN_CHANNEL"}

    if channel == "CHANNEL_A_MONEY_MINDSET_CONVERSION" and any(x in text for x in ["dinero garantizado", "ingresos asegurados", "promesa absoluta"]):
        return {"status": "BLOCK", "reason": "CHANNEL_A_UNSAFE_FINANCIAL_CLAIM"}
    if channel == "CHANNEL_D_AI_TECH_PERSONAL_BRAND" and any(x in text for x in ["motivación genérica", "herramienta no verificada", "ia garantiza"]):
        return {"status": "BLOCK", "reason": "CHANNEL_D_GENERIC_OR_UNVERIFIED_TECH"}
    if channel == "CHANNEL_B_CURIOSITIES_MASS_TRAFFIC" and any(x in text for x in ["hecho no verificable", "miedo engañoso", "desinformación"]):
        return {"status": "BLOCK", "reason": "CHANNEL_B_UNVERIFIABLE_OR_MISLEADING"}
    if channel == "CHANNEL_C_MOTIVATION_DISCIPLINE_RETENTION" and any(x in text for x in ["disciplina tóxica", "culpa extrema", "valor personal"]):
        return {"status": "BLOCK", "reason": "CHANNEL_C_SAFETY_RISK"}

    return {"status": "PASS", "reason": "CHANNEL_POLICY_VALID", "required_reviews": CHANNEL_REQUIRED_REVIEWS[channel]}
