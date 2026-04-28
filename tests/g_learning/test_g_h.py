import sys
from pathlib import Path

root = Path(r"D:\CONTENT_ENGINE_OMEGA\00_SYSTEM")
sys.path.insert(0, str(root))

from core.g_learning.g_h import run_g_h
from core.g_learning.g_h.hashing import stable_hash


def gg_input():
    gate = {
        "execution_gate_id": "gate-1",
        "status": "READY_FOR_FINAL_EXECUTION_REVIEW",
        "validated_plan": {"plan_id": "plan-1"},
        "validated_snapshot": {"snapshot_hash": "snapshot-hash"},
        "validated_rollback": {"rollback_strategy": "NO_RUNTIME_CHANGE_PLAN_ONLY"},
        "validated_validation": {"checks": ["pytest"]},
        "drift_baseline": {"repo_head": "repo-head"},
        "execution_permission": False,
        "handoff_target": "G-H",
    }

    return {
        "phase": "G",
        "subphase": "G-G",
        "status": "READY_FOR_FINAL_EXECUTION_REVIEW",
        "execution_gate": gate,
        "execution_permission": False,
        "gate_hash": "gate-hash",
        "snapshot_hash": "snapshot-hash",
        "validation_hash": "validation-hash",
        "rollback_hash": "rollback-hash",
        "drift_hash": "drift-hash",
        "output_hash": "output-hash",
        "deterministic": True,
    }


def constraints():
    return {
        "constraints_hash": "constraints-hash",
        "immutable": True,
        "enforced": True,
    }


def trace_chain():
    return {
        "trace_id": "trace-id",
        "g_e": "g-e-hash",
        "g_f": "g-f-hash",
        "g_g": "g-g-hash",
    }


def snapshot():
    return {
        "snapshot_id": "snapshot-id",
        "snapshot_hash": "snapshot-hash",
        "immutable": True,
        "content_addressed": True,
    }


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


def permission_usage(**overrides):
    base = {
        "used": False,
        "single_use": True,
        "usage_hash": "usage-hash",
    }
    base.update(overrides)
    return base


def risk_analysis(**overrides):
    base = {
        "risk_score": 0.12,
        "confidence_score": 0.95,
        "risk_level": "LOW",
    }
    base.update(overrides)
    return base


def permission_contract(**overrides):
    data = gg_input()
    cons = constraints()
    trace = trace_chain()

    permission_id = stable_hash(
        {
            "gate_hash": data["gate_hash"],
            "execution_gate_id": data["execution_gate"]["execution_gate_id"],
            "snapshot_hash": data["snapshot_hash"],
            "repo_head": "repo-head",
            "constraints_hash": cons["constraints_hash"],
            "trace_chain_id": trace["trace_id"],
            "permission_statement": "Permiso final consciente para habilitar ejecución controlada futura.",
        }
    )

    base = {
        "permission_id": permission_id,
        "permission_version": "v1.3",
        "requested_by": "Romel",
        "identity_verified": True,
        "permission_statement": "Permiso final consciente para habilitar ejecución controlada futura.",
        "permission_scope": "CONTROLLED_EXECUTION_PERMISSION_ONLY",
        "dual_consent": True,
        "secondary_confirmation": True,
        "revocation_status": "ACTIVE",
        "permission_timestamp": "2026-04-28T00:00:00Z",
        "permission_expiration": "2026-04-29T00:00:00Z",
        "execution_window": {
            "start": "2026-04-28T00:00:00Z",
            "end": "2026-04-29T00:00:00Z",
        },
        "environment": {
            "expected": "PROD",
            "current": "PROD",
            "locked": True,
        },
        "source_gate_hash": "gate-hash",
        "source_snapshot_hash": "snapshot-hash",
        "source_repo_head": "repo-head",
        "constraints_hash": cons["constraints_hash"],
        "trace_chain_id": trace["trace_id"],
    }
    base.update(overrides)
    return base


def valid_call(**overrides):
    args = {
        "input_data": gg_input(),
        "permission_contract": permission_contract(),
        "permission_usage": permission_usage(),
        "snapshot": snapshot(),
        "repo_state": repo_state(),
        "constraints": constraints(),
        "trace_chain": trace_chain(),
        "risk_analysis": risk_analysis(),
        "execution_runner_target": "G-I",
        "now_iso": "2026-04-28T01:00:00Z",
    }
    args.update(overrides)
    return run_g_h(**args)


def test_valid_permission_ready():
    result = valid_call()
    assert result["status"] == "EXECUTION_PERMISSION_READY"
    assert result["logical_execution_permission_ready"] is True
    assert result["execution_permission"] is False
    assert result["execution_runner_target"] == "G-I"


def test_missing_permission_review_required():
    result = valid_call(permission_contract=None)
    assert result["status"] == "REVIEW_REQUIRED"


def test_reuse_permission_blocks():
    result = valid_call(permission_usage=permission_usage(used=True))
    assert result["status"] == "BLOCKED"


def test_outside_window_blocks():
    result = valid_call(now_iso="2026-04-30T01:00:00Z")
    assert result["status"] == "BLOCKED"


def test_environment_mismatch_blocks():
    bad = permission_contract(environment={"expected": "PROD", "current": "DEV", "locked": True})
    result = valid_call(permission_contract=bad)
    assert result["status"] == "BLOCKED"


def test_snapshot_invalid_blocks():
    result = valid_call(snapshot={"snapshot_id": "x", "snapshot_hash": "snapshot-hash", "immutable": False, "content_addressed": True})
    assert result["status"] == "BLOCKED"


def test_drift_blocks():
    bad = permission_contract(source_gate_hash="changed")
    result = valid_call(permission_contract=bad)
    assert result["status"] == "BLOCKED"


def test_repo_dirty_blocks():
    result = valid_call(repo_state=repo_state(repo_clean=False))
    assert result["status"] == "BLOCKED"


def test_risk_high_blocks():
    result = valid_call(risk_analysis=risk_analysis(risk_level="HIGH"))
    assert result["status"] == "BLOCKED"


def test_risk_medium_review_required():
    result = valid_call(risk_analysis=risk_analysis(risk_level="MEDIUM"))
    assert result["status"] == "REVIEW_REQUIRED"


def test_runner_not_g_i_blocks():
    result = valid_call(execution_runner_target="OTHER")
    assert result["status"] == "BLOCKED"


def test_deterministic_output():
    a = valid_call()
    b = valid_call()
    assert a["output_hash"] == b["output_hash"]
    assert a["permission_hash"] == b["permission_hash"]


def test_permission_id_mismatch_blocks():
    bad = permission_contract(permission_id="bad-id")
    result = valid_call(permission_contract=bad)
    assert result["status"] == "BLOCKED"
