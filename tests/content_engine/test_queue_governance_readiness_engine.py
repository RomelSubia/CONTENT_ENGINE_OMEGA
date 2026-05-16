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


def test_readiness_passes_safe_payload():
    result = qg.calculate_readiness(safe_item())
    assert result["status"] == "PASS"
    assert result["generation_allowed"] is False


def test_review_ready_does_not_enable_generation():
    item = safe_item()
    item["evidence_status"] = "COMPLETE"
    result = qg.calculate_readiness(item)
    assert result["generation_allowed"] is False
    assert result["publishing_allowed"] is False
    assert result["queue_write_allowed"] is False


def test_critical_readiness_blocks():
    item = safe_item()
    item["risk_level"] = "CRITICAL_EXECUTION_BLOCK"
    assert qg.calculate_readiness(item)["status"] == "BLOCK"


def test_readiness_validation_blocks_generation_true():
    result = qg.calculate_readiness(safe_item())
    result["generation_allowed"] = True
    assert qg.validate_readiness_output(result)["status"] == "BLOCK"


def test_readiness_validation_blocks_queue_write_true():
    result = qg.calculate_readiness(safe_item())
    result["queue_write_allowed"] = True
    assert qg.validate_readiness_output(result)["status"] == "BLOCK"
