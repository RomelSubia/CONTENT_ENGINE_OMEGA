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


def _make_sensitive_payload_blocks_test(value):
    def _test():
        result = qg.validate_payload_safety({"idea_summary": value})
        assert result["status"] == "BLOCK"
        assert result.get("queue_write_performed", False) is False
    return _test


for _idx, _value in enumerate(['romel@example.com', '+1 305 555 1234', '123 Main Street', 'api_key=ABCDEF123456', '../secret', 'C:\\secret\\file.txt']):
    globals()[f"test_sensitive_payload_blocks_{_idx}"] = _make_sensitive_payload_blocks_test(_value)


def test_safe_payload_safety_passes():
    assert qg.validate_payload_safety(safe_item())["status"] == "PASS"


def test_secret_detector_passes_safe_payload():
    assert qg.detect_secret_payload(safe_item())["status"] == "PASS"


def test_sensitive_detector_passes_safe_payload():
    assert qg.detect_sensitive_payload(safe_item())["status"] == "PASS"


def test_path_detector_passes_safe_payload():
    assert qg.detect_path_like_payload(safe_item())["status"] == "PASS"
