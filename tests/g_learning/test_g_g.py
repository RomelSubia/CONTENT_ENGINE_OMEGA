import sys
from pathlib import Path

root = Path(r"D:\CONTENT_ENGINE_OMEGA\00_SYSTEM")
sys.path.insert(0, str(root))

from core.g_learning.g_g import run_g_g


def gf_input():
    plan = {
        "plan_id": "plan-1",
        "allowed_scope": "READ_ONLY_ANALYSIS_AND_PLAN_ONLY",
        "execution_allowed": False,
        "steps": [{"step_id": "s1"}],
        "diff_preview": {"description": "preview"},
    }
    validation = {
        "checks": [
            "py_compile",
            "pytest",
            "determinism_check",
            "repo_clean_check",
            "cache_clean_check",
            "HEAD_equals_upstream",
            "audit_verification",
        ]
    }
    rollback = {
        "rollback_strategy": "NO_RUNTIME_CHANGE_PLAN_ONLY",
        "restore_point": "current_git_HEAD",
        "validation_after_rollback": ["pytest"],
        "human_review_required": True,
    }
    return {
        "phase": "G",
        "subphase": "G-F",
        "status": "PLAN_READY_FOR_REVIEW",
        "controlled_plan": plan,
        "validation_plan": validation,
        "rollback_plan": rollback,
        "review_package": {"summary": "review"},
        "decision": "PLAN_READY_FOR_REVIEW",
        "deterministic": True,
        "plan_hash": "plan-hash",
        "steps_hash": "steps-hash",
        "diff_hash": "diff-hash",
        "rollback_hash": "rollback-hash",
        "validation_hash": "validation-hash",
        "review_hash": "review-hash",
        "output_hash": "output-hash",
    }


def approval(**overrides):
    base = {
        "final_approval_id": "final-approval-1",
        "approval_version": "v1.3",
        "final_approval": True,
        "approved_by": "Romel",
        "identity_verified": True,
        "approval_statement": "Aprobación final consciente para evaluación previa a ejecución controlada.",
        "approval_scope": "EXECUTION_GATE_REVIEW_ONLY",
        "understands_execution_risk": True,
        "rollback_acknowledged": True,
        "snapshot_acknowledged": True,
        "multi_step_confirmed": True,
        "revocation_status": "ACTIVE",
        "approval_timestamp": "2026-04-28T00:00:00Z",
        "approval_expiration": "2026-04-29T00:00:00Z",
        "source_plan_hash": "plan-hash",
        "source_repo_head": "repo-head",
        "source_snapshot_hash": "snapshot-hash",
    }
    base.update(overrides)
    return base


def snapshot(**overrides):
    base = {
        "snapshot_id": "snapshot-1",
        "snapshot_hash": "snapshot-hash",
        "snapshot_strategy": "FULL_REPO_STATE",
        "snapshot_target": "git_HEAD",
    }
    base.update(overrides)
    return base


def repo_state(**overrides):
    base = {
        "repo_clean": True,
        "cache_clean": True,
        "head_equals_upstream": True,
        "no_pycache_tracked": True,
        "repo_head": "repo-head",
    }
    base.update(overrides)
    return base


def test_missing_approval_review_required():
    result = run_g_g(gf_input(), None, snapshot(), repo_state(), now_iso="2026-04-28T01:00:00Z")
    assert result["status"] == "REVIEW_REQUIRED"


def test_valid_gate_ready_review_only():
    result = run_g_g(gf_input(), approval(), snapshot(), repo_state(), now_iso="2026-04-28T01:00:00Z")
    assert result["status"] == "READY_FOR_FINAL_EXECUTION_REVIEW"
    assert result["execution_permission"] is False
    assert result["execution_gate"]["execution_permission"] is False


def test_expired_approval_blocks():
    result = run_g_g(gf_input(), approval(approval_expiration="2026-04-27T00:00:00Z"), snapshot(), repo_state(), now_iso="2026-04-28T01:00:00Z")
    assert result["status"] == "BLOCKED"


def test_revoked_approval_blocks():
    result = run_g_g(gf_input(), approval(revocation_status="REVOKED"), snapshot(), repo_state(), now_iso="2026-04-28T01:00:00Z")
    assert result["status"] == "BLOCKED"


def test_missing_snapshot_blocks():
    result = run_g_g(gf_input(), approval(), None, repo_state(), now_iso="2026-04-28T01:00:00Z")
    assert result["status"] == "BLOCKED"


def test_drift_blocks():
    result = run_g_g(gf_input(), approval(source_plan_hash="changed"), snapshot(), repo_state(), now_iso="2026-04-28T01:00:00Z")
    assert result["status"] == "BLOCKED"


def test_repo_dirty_blocks():
    result = run_g_g(gf_input(), approval(), snapshot(), repo_state(repo_clean=False), now_iso="2026-04-28T01:00:00Z")
    assert result["status"] == "BLOCKED"


def test_emergency_stop_blocks():
    result = run_g_g(gf_input(), approval(), snapshot(), repo_state(), emergency_stop_status="ACTIVE", now_iso="2026-04-28T01:00:00Z")
    assert result["status"] == "BLOCKED"


def test_plan_execution_allowed_blocks():
    data = gf_input()
    data["controlled_plan"]["execution_allowed"] = True
    result = run_g_g(data, approval(), snapshot(), repo_state(), now_iso="2026-04-28T01:00:00Z")
    assert result["status"] == "BLOCKED"


def test_deterministic_output():
    data = gf_input()
    app = approval()
    snap = snapshot()
    repo = repo_state()
    a = run_g_g(data, app, snap, repo, now_iso="2026-04-28T01:00:00Z")
    b = run_g_g(data, app, snap, repo, now_iso="2026-04-28T01:00:00Z")
    assert a["output_hash"] == b["output_hash"]
    assert a["gate_hash"] == b["gate_hash"]
