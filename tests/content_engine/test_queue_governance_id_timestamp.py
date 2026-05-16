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


def test_valid_id_passes():
    assert qg.validate_queue_item_id("QG-20260516-231455-A13F09BC")["status"] == "PASS"


def test_valid_utc_passes():
    assert qg.validate_created_at_utc("2026-05-16T23:14:55Z")["status"] == "PASS"


def test_utc_without_z_blocks():
    assert qg.validate_created_at_utc("2026-05-16T23:14:55")["status"] == "BLOCK"


def test_date_only_blocks():
    assert qg.validate_created_at_utc("2026-05-16")["status"] == "BLOCK"

def _make_id_timestamp_rejects_test(value):
    def _test():
        result = qg.validate_queue_item_id(value)
        assert result["status"] == "BLOCK"
        assert result.get("queue_write_performed", False) is False
    return _test


for _idx, _value in enumerate(['QG-20260516-231455-A13F09B', 'QG-20260516-231455-a13f09bc', 'QG-20260516-231455-A13F09BC\\x', 'me@x.com']):
    globals()[f"test_id_timestamp_rejects_{_idx}"] = _make_id_timestamp_rejects_test(_value)

