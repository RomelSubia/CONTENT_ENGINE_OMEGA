import sys
from pathlib import Path

root = Path(r"D:\CONTENT_ENGINE_OMEGA\00_SYSTEM")
sys.path.insert(0, str(root))

from core.g_learning.g_e import run_g_e


def rec():
    return {
        "recommendation_id": "rec-1",
        "risk_level": "LOW",
        "confidence_score": 0.9,
    }


def gd_input(decision="ALLOW_REVIEW", status="VALID"):
    return {
        "phase": "G",
        "subphase": "G-D",
        "status": status,
        "approved_for_review": [rec()],
        "quarantined": [],
        "blocked": [],
        "decision": decision,
        "deterministic": True,
        "input_hash": "input-hash",
        "risk_hash": "risk-hash",
        "decision_hash": "decision-hash",
        "output_hash": "output-hash",
    }


def approval(**overrides):
    base = {
        "approval_id": "approval-1",
        "approval_version": "v1.3",
        "human_approval": True,
        "approved_by": "Romel",
        "identity_verified": True,
        "approval_statement": "Aprobación explícita consciente con conocimiento del riesgo y rollback.",
        "approval_intent": "CONTROLLED_PLAN_ONLY",
        "approved_items": ["rec-1"],
        "approval_scope": "CONTROLLED_PLAN_ONLY",
        "understands_risk": True,
        "rollback_acknowledged": True,
        "multi_step_confirmed": True,
        "approval_timestamp": "2026-04-28T00:00:00Z",
        "approval_expiration": "2026-04-29T00:00:00Z",
        "revocation_status": "ACTIVE",
        "source_input_hash": "input-hash",
        "source_risk_hash": "risk-hash",
        "source_decision_hash": "decision-hash",
    }
    base.update(overrides)
    return base


def test_no_approval_pending():
    result = run_g_e(gd_input(), None, now_iso="2026-04-28T01:00:00Z")
    assert result["status"] == "PENDING_HUMAN_APPROVAL"


def test_valid_approval_authorizes_controlled_plan():
    result = run_g_e(gd_input(), approval(), now_iso="2026-04-28T01:00:00Z")
    assert result["status"] == "AUTHORIZED_FOR_CONTROLLED_PLAN"
    assert result["decision"] == "AUTHORIZED_FOR_CONTROLLED_PLAN"
    assert len(result["authorized_items"]) == 1


def test_ambiguous_approval_pending():
    result = run_g_e(gd_input(), approval(approval_statement="ok"), now_iso="2026-04-28T01:00:00Z")
    assert result["status"] == "PENDING_HUMAN_APPROVAL"


def test_expired_approval_blocks():
    result = run_g_e(gd_input(), approval(approval_expiration="2026-04-27T00:00:00Z"), now_iso="2026-04-28T01:00:00Z")
    assert result["status"] == "BLOCKED"


def test_revoked_approval_blocks():
    result = run_g_e(gd_input(), approval(revocation_status="REVOKED"), now_iso="2026-04-28T01:00:00Z")
    assert result["status"] == "BLOCKED"


def test_scope_mismatch_blocks():
    result = run_g_e(gd_input(), approval(approved_items=["other-rec"]), now_iso="2026-04-28T01:00:00Z")
    assert result["status"] == "BLOCKED"


def test_lineage_mismatch_blocks():
    result = run_g_e(gd_input(), approval(source_risk_hash="changed"), now_iso="2026-04-28T01:00:00Z")
    assert result["status"] == "BLOCKED"


def test_execution_attempt_blocks():
    result = run_g_e(gd_input(), approval(approval_statement="Aprobación explícita para execute now con riesgo."), now_iso="2026-04-28T01:00:00Z")
    assert result["status"] == "BLOCKED"


def test_source_blocked_blocks():
    result = run_g_e(gd_input(decision="BLOCK", status="BLOCKED"), approval(), now_iso="2026-04-28T01:00:00Z")
    assert result["status"] == "BLOCKED"


def test_source_review_required_pending():
    result = run_g_e(gd_input(decision="REVIEW_REQUIRED", status="REVIEW_REQUIRED"), approval(), now_iso="2026-04-28T01:00:00Z")
    assert result["status"] == "PENDING_HUMAN_APPROVAL"


def test_deterministic_output():
    data = gd_input()
    app = approval()
    a = run_g_e(data, app, now_iso="2026-04-28T01:00:00Z")
    b = run_g_e(data, app, now_iso="2026-04-28T01:00:00Z")
    assert a["output_hash"] == b["output_hash"]
    assert a["authorization_hash"] == b["authorization_hash"]
    assert a["approval_hash"] == b["approval_hash"]
