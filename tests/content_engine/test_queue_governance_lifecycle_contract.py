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


def test_draft_state_allowed():
    assert qg.validate_lifecycle_state("DRAFT_INTAKE")["status"] == "PASS"


def test_transition_allowed():
    assert qg.validate_lifecycle_transition("DRAFT_INTAKE", "CLASSIFIED")["status"] == "PASS"


def test_unlisted_transition_blocks():
    assert qg.validate_lifecycle_transition("DRAFT_INTAKE", "REVIEW_READY")["status"] == "BLOCK"

def _make_blocked_lifecycle_states_test(value):
    def _test():
        result = qg.validate_lifecycle_state(value)
        assert result["status"] == "BLOCK"
        assert result.get("queue_write_performed", False) is False
    return _test


for _idx, _value in enumerate(['READY_FOR_GENERATION', 'PROMPT_READY', 'SCRIPT_READY', 'ASSET_READY', 'READY_TO_PUBLISH', 'PUBLISHED', 'AUTOMATED', 'N8N_TRIGGERED', 'WEBHOOK_SENT', 'CAPA9_ACTIVE']):
    globals()[f"test_blocked_lifecycle_states_{_idx}"] = _make_blocked_lifecycle_states_test(_value)

