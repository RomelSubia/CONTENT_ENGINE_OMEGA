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


def test_valid_channel_passes():
    assert qg.validate_channel_id("CHANNEL_D_AI_TECH_PERSONAL_BRAND")["status"] == "PASS"


def test_unknown_channel_blocks():
    assert qg.validate_channel_id("CHANNEL_X")["status"] == "BLOCK"


def test_route_safe_candidate_passes():
    assert qg.route_queue_candidate(safe_item())["status"] == "PASS"


def test_b_channel_aggressive_conversion_blocks():
    item = safe_item()
    item["channel_id"] = "CHANNEL_B_CURIOSITIES_MASS_TRAFFIC"
    item["idea_summary"] = "compra ahora y cierra venta"
    assert qg.detect_cross_channel_contamination(item)["status"] == "BLOCK"


def test_c_channel_financial_promise_blocks():
    item = safe_item()
    item["channel_id"] = "CHANNEL_C_MOTIVATION_DISCIPLINE_RETENTION"
    item["idea_summary"] = "ganar dinero garantizado"
    assert qg.detect_cross_channel_contamination(item)["status"] == "BLOCK"


def test_d_channel_generic_motivation_blocks():
    item = safe_item()
    item["channel_id"] = "CHANNEL_D_AI_TECH_PERSONAL_BRAND"
    item["idea_summary"] = "motivación genérica"
    assert qg.detect_cross_channel_contamination(item)["status"] == "BLOCK"


def test_a_channel_empty_curiosity_blocks():
    item = safe_item()
    item["channel_id"] = "CHANNEL_A_MONEY_MINDSET_CONVERSION"
    item["idea_summary"] = "dato curioso sin conversión"
    assert qg.detect_cross_channel_contamination(item)["status"] == "BLOCK"
