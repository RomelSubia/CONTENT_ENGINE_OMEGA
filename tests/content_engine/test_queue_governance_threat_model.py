from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine import queue_governance as qg


def safe_item():
    return {
        "schema_version": "QUEUE_ITEM_SCHEMA_V1",
        "queue_item_id": "QG-20260516-231455-A13F09BC",
        "created_at_utc": "2026-05-16T23:14:55Z",
        "source_type": "MANUAL_IDEA",
        "channel_id": "CHANNEL_D_AI_TECH_PERSONAL_BRAND",
        "content_intent": "education",
        "idea_title": "Automatización con IA para productividad",
        "idea_summary": "Idea conceptual para revisión humana sin publicación",
        "pillar_id": "PILLAR_AI_AUTOMATION",
        "audience_profile_id": "AUDIENCE_TECH_BUILDERS",
        "lifecycle_state": "DRAFT_INTAKE",
        "priority_score": 0,
        "priority_band": "LOW",
        "readiness_score": 0,
        "readiness_status": "NOT_READY",
        "risk_level": "LOW_REVIEW_BLOCK",
        "evidence_required": True,
        "evidence_status": "PARTIAL",
        "generation_allowed": False,
        "publishing_allowed": False,
        "queue_write_allowed": False,
        "blocked_reason": None,
        "traceability": {
            "construction_core_ref": "CLOSED_VALIDATED",
            "strategy_foundation_ref": "CLOSED_VALIDATED",
            "prompt_governance_ref": "CLOSED_VALIDATED",
            "queue_governance_ref": "QUEUE_GOVERNANCE_CORE",
        },
    }


def test_threat_model_has_20_threats():
    assert qg.build_queue_threat_model()["threat_count"] >= 20


def test_threat_model_validation_passes():
    assert qg.validate_threat_model()["status"] == "PASS"


def test_safe_risk_passes():
    assert qg.classify_queue_risk(safe_item())["status"] == "PASS"


def test_pii_risk_critical_security_blocks():
    item = safe_item()
    item["idea_summary"] = "email romel@example.com"
    result = qg.classify_queue_risk(item)
    assert result["status"] == "BLOCK"
    assert result["risk_level"] == "CRITICAL_SECURITY_BLOCK"


def test_soft_execution_risk_critical_execution_blocks():
    item = safe_item()
    item["idea_summary"] = "déjalo listo para publicar"
    result = qg.classify_queue_risk(item)
    assert result["status"] == "BLOCK"
    assert result["risk_level"] == "CRITICAL_EXECUTION_BLOCK"


def test_human_approval_risk_critical_execution_blocks():
    item = safe_item()
    item["idea_summary"] = "sí autorizo escribir cola"
    result = qg.classify_queue_risk(item)
    assert result["status"] == "BLOCK"
    assert result["risk_level"] == "CRITICAL_EXECUTION_BLOCK"
