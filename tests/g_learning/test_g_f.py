import sys
from pathlib import Path

root = Path(r"D:\CONTENT_ENGINE_OMEGA\00_SYSTEM")
sys.path.insert(0, str(root))

from core.g_learning.g_f import run_g_f


def ge_input(items=None, status="AUTHORIZED_FOR_CONTROLLED_PLAN", decision="AUTHORIZED_FOR_CONTROLLED_PLAN"):
    if items is None:
        items = [{"recommendation_id": "rec-1", "risk_level": "LOW", "confidence_score": 0.9}]

    return {
        "phase": "G",
        "subphase": "G-E",
        "status": status,
        "authorized_items": items,
        "pending_items": [],
        "blocked_items": [],
        "decision": decision,
        "deterministic": True,
        "approval_hash": "approval-hash",
        "scope_hash": "scope-hash",
        "lineage_hash": "lineage-hash",
        "intent_hash": "intent-hash",
        "authorization_hash": "authorization-hash",
        "output_hash": "output-hash",
    }


def test_valid_plan_ready_for_review():
    result = run_g_f(ge_input())
    assert result["status"] == "PLAN_READY_FOR_REVIEW"
    assert result["decision"] == "PLAN_READY_FOR_REVIEW"
    assert result["controlled_plan"]["execution_allowed"] is False


def test_invalid_source_blocks():
    result = run_g_f(ge_input(status="BLOCKED", decision="BLOCK"))
    assert result["status"] == "BLOCKED"


def test_empty_authorized_items_blocks():
    result = run_g_f(ge_input(items=[]))
    assert result["status"] == "BLOCKED"


def test_high_risk_blocks():
    result = run_g_f(ge_input(items=[{"recommendation_id": "rec-1", "risk_level": "HIGH"}]))
    assert result["status"] == "BLOCKED"


def test_deterministic_output():
    data = ge_input()
    a = run_g_f(data)
    b = run_g_f(data)
    assert a["output_hash"] == b["output_hash"]
    assert a["plan_hash"] == b["plan_hash"]
    assert a["review_hash"] == b["review_hash"]


def test_plan_contains_validation_and_rollback():
    result = run_g_f(ge_input())
    assert "pytest" in result["validation_plan"]["checks"]
    assert result["rollback_plan"]["human_review_required"] is True


def test_steps_are_read_only():
    result = run_g_f(ge_input())
    step = result["controlled_plan"]["steps"][0]
    assert step["allowed_scope"] == "READ_ONLY"
    assert step["execution_allowed"] is False
    assert step["action_type"] in {"READ_ANALYZE", "INSPECT", "VALIDATE", "SIMULATE"}
