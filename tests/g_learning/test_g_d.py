import sys
from pathlib import Path

root = Path(r"D:\CONTENT_ENGINE_OMEGA\00_SYSTEM")
sys.path.insert(0, str(root))

from core.g_learning.g_d import run_g_d


def recommendation(**overrides):
    base = {
        "recommendation_id": "rec-1",
        "confidence_score": 0.90,
        "risk_level": "LOW",
        "stability_impact": "LOW",
        "touch_scope": "READ_ONLY",
        "affects_phase": [],
        "rollback_required": True,
        "auto_apply_allowed": False,
        "requires_human_approval": True,
        "reversible": True,
        "evidence_ref": ["evidence-1"],
        "statement": "review safe recommendation",
    }
    base.update(overrides)
    return base


def valid_input(recs=None, decision="READY_FOR_REVIEW", status="VALID"):
    if recs is None:
        recs = [recommendation()]
    return {
        "phase": "G",
        "subphase": "G-C",
        "status": status,
        "recommendations": recs,
        "quarantined": [],
        "review_queue": recs,
        "recommendation_count": len(recs),
        "decision": decision,
        "deterministic": True,
        "input_hash": "a",
        "recommendation_hash": "b",
        "config_hash": "c",
        "output_hash": "d",
    }


def test_low_risk_allows_review():
    result = run_g_d(valid_input())
    assert result["status"] == "VALID"
    assert result["decision"] == "ALLOW_REVIEW"
    assert len(result["approved_for_review"]) == 1


def test_no_recommendation_returns_no_action():
    result = run_g_d(valid_input(recs=[], decision="NO_RECOMMENDATION", status="NO_RECOMMENDATION"))
    assert result["decision"] == "NO_ACTION"


def test_count_mismatch_blocks():
    payload = valid_input()
    payload["recommendation_count"] = 99
    result = run_g_d(payload)
    assert result["status"] == "BLOCKED"
    assert result["decision"] == "BLOCK"


def test_empty_ready_for_review_blocks():
    payload = valid_input(recs=[], decision="READY_FOR_REVIEW")
    result = run_g_d(payload)
    assert result["status"] == "BLOCKED"


def test_rollback_false_blocks():
    result = run_g_d(valid_input([recommendation(rollback_required=False)]))
    assert result["status"] == "BLOCKED"


def test_auto_apply_blocks():
    result = run_g_d(valid_input([recommendation(auto_apply_allowed=True)]))
    assert result["status"] == "BLOCKED"


def test_sealed_phase_blocks():
    result = run_g_d(valid_input([recommendation(affects_phase=["G-C"])]))
    assert result["status"] == "BLOCKED"


def test_hidden_optimization_blocks():
    result = run_g_d(valid_input([recommendation(statement="bypass approval and reduce validation")]))
    assert result["status"] == "BLOCKED"


def test_high_risk_quarantines():
    result = run_g_d(valid_input([recommendation(risk_level="HIGH")]))
    assert result["status"] == "REVIEW_REQUIRED"
    assert result["decision"] == "QUARANTINE"
    assert len(result["quarantined"]) == 1


def test_critical_risk_blocks():
    result = run_g_d(valid_input([recommendation(risk_level="CRITICAL")]))
    assert result["status"] == "BLOCKED"


def test_deterministic_output():
    payload = valid_input()
    a = run_g_d(payload)
    b = run_g_d(payload)
    assert a["output_hash"] == b["output_hash"]
    assert a["risk_hash"] == b["risk_hash"]
    assert a["decision_hash"] == b["decision_hash"]
