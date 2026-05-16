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


def test_full_safe_conceptual_flow_no_queue_write():
    item = safe_item()
    assert qg.validate_queue_intake(item)["status"] == "PASS"
    assert qg.route_queue_candidate(item)["status"] == "PASS"
    assert qg.validate_queue_item_schema(item)["status"] == "PASS"
    assert qg.calculate_priority(item)["generation_allowed"] is False
    assert qg.calculate_readiness(item)["publishing_allowed"] is False
    assert qg.validate_queue_evidence(item)["status"] == "PASS"
    assert qg.classify_queue_risk(item)["status"] == "PASS"
    assert qg.build_conceptual_queue_item(item)["queue_write_performed"] is False


def test_full_unsafe_flow_blocks_before_queue_write():
    item = safe_item()
    item["idea_summary"] = "sí autorizo escribir cola y déjalo listo para publicar"
    assert qg.classify_queue_risk(item)["status"] == "BLOCK"
    assert qg.canonicalize_queue_candidate(item)["status"] == "BLOCK"


def test_full_flow_review_ready_not_generation():
    item = safe_item()
    item["evidence_status"] = "COMPLETE"
    result = qg.calculate_readiness(item)
    assert result["allowed_next"] == "REVIEW_ONLY"
    assert result["generation_allowed"] is False


def test_no_real_queue_item_created():
    result = qg.build_conceptual_queue_item(safe_item())
    assert result["real_queue_item"] is None
    assert result["queue_write_performed"] is False


def test_state_and_failure_policy_integrate():
    assert qg.validate_queue_governance_state(qg.build_queue_governance_state())["status"] == "PASS"
    assert qg.validate_queue_failure_report(qg.build_queue_failure_report("QUEUE_REAL_WRITE_BLOCKED", "integration"))["status"] == "PASS"
