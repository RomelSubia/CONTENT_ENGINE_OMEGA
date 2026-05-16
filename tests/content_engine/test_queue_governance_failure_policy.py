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


def test_failure_report_validates():
    report = qg.build_queue_failure_report("QUEUE_REAL_WRITE_BLOCKED", "test_gate")
    assert qg.validate_queue_failure_report(report)["status"] == "PASS"


def test_failure_report_unknown_reason_normalized():
    report = qg.build_queue_failure_report("UNKNOWN", "test_gate")
    assert report["reason"] == "QUEUE_FAILURE_POLICY_REQUIRED"


def test_failure_report_status_required():
    report = qg.build_queue_failure_report("QUEUE_REAL_WRITE_BLOCKED", "test_gate")
    report["status"] = "PASS"
    assert qg.validate_queue_failure_report(report)["status"] == "FAILED_BLOCKED"


def test_failure_report_false_flags_required():
    report = qg.build_queue_failure_report("QUEUE_REAL_WRITE_BLOCKED", "test_gate")
    report["commit_created"] = True
    assert qg.validate_queue_failure_report(report)["status"] == "FAILED_BLOCKED"

def _make_failure_reasons_build_reports_test(value):
    def _test():
        result = qg.validate_queue_failure_report(qg.build_queue_failure_report(value, "gate"))
        assert result["status"] == "PASS"
        assert result.get("queue_write_performed", False) is False
    return _test


for _idx, _value in enumerate(['QUEUE_SCHEMA_VERSION_INVALID', 'QUEUE_REAL_WRITE_BLOCKED', 'QUEUE_NO_TOUCH_VIOLATION', 'QUEUE_IDEMPOTENCY_VIOLATION', 'QUEUE_MANIFEST_SEAL_MISMATCH']):
    globals()[f"test_failure_reasons_build_reports_{_idx}"] = _make_failure_reasons_build_reports_test(_value)

