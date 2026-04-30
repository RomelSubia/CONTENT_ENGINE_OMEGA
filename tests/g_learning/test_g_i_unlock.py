import sys
from pathlib import Path

root = Path(r"D:\CONTENT_ENGINE_OMEGA\00_SYSTEM")
sys.path.insert(0, str(root))

from core.g_learning.g_i_unlock import run_g_i_unlock
from core.g_learning.g_i_unlock.approval_guard import expected_unlock_approval_id
from core.g_learning.g_i_unlock.scope_guard import build_unlock_scope


def evidence(**overrides):
    base = {
        "g_i_v13_audit_exists": True,
        "pytest_passed": True,
        "pytest_count": 84,
        "no_mutation_pass": True,
        "controlled_run_locked": True,
        "repo_sync_valid": True,
        "commit_hash": "commit-gi-v13",
        "evidence_hash": "evidence-gi-v13",
    }
    base.update(overrides)
    return base


def repo_state(**overrides):
    base = {
        "repo_clean": True,
        "cache_clean": True,
        "head_equals_upstream": True,
        "no_pycache_tracked": True,
        "commit_hash": "commit-gi-v13",
    }
    base.update(overrides)
    return base


def risk(**overrides):
    base = {
        "risk_score": 0.1,
        "confidence_score": 0.98,
        "risk_level": "LOW",
    }
    base.update(overrides)
    return base


def approval(**overrides):
    ev = evidence()
    scope = build_unlock_scope()
    statement = "Autorizo revisar el desbloqueo limitado de ejecución controlada; no autorizo ejecutar ahora."
    base = {
        "unlock_approval_id": "",
        "approval_version": "v1.4.1",
        "approved_by": "Romel",
        "identity_verified": True,
        "approval_scope": "CONTROLLED_RUN_LIMITED_UNLOCK_REVIEW_ONLY",
        "approval_statement": statement,
        "understands_mutation_risk": True,
        "understands_rollback_risk": True,
        "dry_run_evidence_reviewed": True,
        "secondary_confirmation": True,
        "revocation_status": "ACTIVE",
        "reuse_status": "UNUSED",
        "approval_timestamp": "2026-04-28T00:00:00Z",
        "approval_expiration": "2026-04-29T00:00:00Z",
        "unlock_window": {
            "start": "2026-04-28T00:00:00Z",
            "end": "2026-04-29T00:00:00Z",
        },
    }
    base["unlock_approval_id"] = expected_unlock_approval_id(ev, base, scope)
    base.update(overrides)
    return base


def valid_call(**overrides):
    args = {
        "dry_run_evidence": evidence(),
        "unlock_approval": approval(),
        "repo_state": repo_state(),
        "risk_analysis": risk(),
        "capability_mode": "REPORT_ONLY",
        "controlled_run_unlocked": False,
        "physical_mutation_allowed": False,
        "now_iso": "2026-04-28T01:00:00Z",
    }
    args.update(overrides)
    return run_g_i_unlock(**args)


def test_valid_unlock_ready_review_only():
    result = valid_call()
    assert result["status"] == "CONTROLLED_RUN_UNLOCK_READY"
    assert result["controlled_run_unlocked"] is False
    assert result["physical_mutation_allowed"] is False
    assert result["next_phase_required"] == "G-I v1.5"


def test_controlled_run_unlocked_true_blocks():
    result = valid_call(controlled_run_unlocked=True)
    assert result["status"] == "UNLOCK_BLOCKED"


def test_physical_mutation_true_blocks():
    result = valid_call(physical_mutation_allowed=True)
    assert result["status"] == "UNLOCK_BLOCKED"


def test_missing_approval_review_required():
    result = valid_call(unlock_approval=None)
    assert result["status"] == "REVIEW_REQUIRED"


def test_missing_evidence_hash_blocks():
    bad = evidence(evidence_hash="")
    result = valid_call(dry_run_evidence=bad)
    assert result["status"] == "UNLOCK_BLOCKED"


def test_invalid_pytest_count_blocks():
    result = valid_call(dry_run_evidence=evidence(pytest_count=83))
    assert result["status"] == "UNLOCK_BLOCKED"


def test_no_mutation_false_blocks():
    result = valid_call(dry_run_evidence=evidence(no_mutation_pass=False))
    assert result["status"] == "UNLOCK_BLOCKED"


def test_approval_reuse_blocks():
    result = valid_call(unlock_approval=approval(reuse_status="USED"))
    assert result["status"] == "UNLOCK_BLOCKED"


def test_approval_revoked_blocks():
    result = valid_call(unlock_approval=approval(revocation_status="REVOKED"))
    assert result["status"] == "UNLOCK_BLOCKED"


def test_approval_expired_blocks():
    result = valid_call(now_iso="2026-04-30T00:00:00Z")
    assert result["status"] == "UNLOCK_BLOCKED"


def test_window_not_started_review_required():
    result = valid_call(now_iso="2026-04-27T00:00:00Z")
    assert result["status"] == "REVIEW_REQUIRED"


def test_capability_state_only_blocks():
    result = valid_call(capability_mode="STATE_ONLY")
    assert result["status"] == "UNLOCK_BLOCKED"


def test_repo_dirty_blocks():
    result = valid_call(repo_state=repo_state(repo_clean=False))
    assert result["status"] == "UNLOCK_BLOCKED"


def test_commit_mismatch_blocks():
    result = valid_call(repo_state=repo_state(commit_hash="other"))
    assert result["status"] == "UNLOCK_BLOCKED"


def test_risk_medium_review_required():
    result = valid_call(risk_analysis=risk(risk_level="MEDIUM"))
    assert result["status"] == "REVIEW_REQUIRED"


def test_risk_high_blocks():
    result = valid_call(risk_analysis=risk(risk_level="HIGH"))
    assert result["status"] == "UNLOCK_BLOCKED"


def test_unlock_approval_id_mismatch_blocks():
    result = valid_call(unlock_approval=approval(unlock_approval_id="bad-id"))
    assert result["status"] == "UNLOCK_BLOCKED"


def test_determinism():
    a = valid_call()
    b = valid_call()
    assert a["output_hash"] == b["output_hash"]
    assert a["unlock_hash"] == b["unlock_hash"]
