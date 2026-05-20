from __future__ import annotations

MONETIZATION_RISK_PATTERNS = (
    "ingresos garantizados",
    "clientes asegurados",
    "ventas garantizadas",
    "dinero seguro",
    "hazte rico",
    "sin riesgo",
    "resultado garantizado",
    "guaranteed income",
)


def classify_monetization_claim_risk(text: str, *, has_evidence: bool = False) -> dict[str, object]:
    lowered = text.lower()
    matches = sorted({pattern for pattern in MONETIZATION_RISK_PATTERNS if pattern in lowered})
    blocked = bool(matches) and not has_evidence
    return {
        "blocked": blocked,
        "matched_patterns": matches,
        "requires_evidence": bool(matches),
        "human_review_required": True,
        "reason": "MONETIZATION_CLAIM_BLOCK" if blocked else "MONETIZATION_CLAIM_REVIEW",
    }
