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


def test_manual_idea_allowed():
    assert qg.classify_source_type("MANUAL_IDEA")["status"] == "PASS"


def test_observation_allowed():
    assert qg.classify_source_type("OBSERVATION")["status"] == "PASS"


def test_validate_intake_passes():
    assert qg.validate_queue_intake(safe_item())["status"] == "PASS"


def test_validate_intake_missing_channel_blocks():
    item = safe_item()
    item["channel_id"] = ""
    assert qg.validate_queue_intake(item)["status"] == "BLOCK"

def _make_blocked_source_type_test(value):
    def _test():
        result = qg.classify_source_type(value)
        assert result["status"] == "BLOCK"
        assert result.get("queue_write_performed", False) is False
    return _test


for _idx, _value in enumerate(['TREND_CANDIDATE', 'METRIC_DERIVED_CANDIDATE', 'FUTURE_API', 'SCRAPED_SOURCE', 'PLATFORM_IMPORT', 'AUTOMATION_IMPORT', 'WEBHOOK_IMPORT', 'N8N_IMPORT']):
    globals()[f"test_blocked_source_type_{_idx}"] = _make_blocked_source_type_test(_value)

