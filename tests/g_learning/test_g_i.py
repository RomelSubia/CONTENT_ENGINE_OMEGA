import sys
from pathlib import Path

root = Path(r"D:\CONTENT_ENGINE_OMEGA\00_SYSTEM")
sys.path.insert(0, str(root))

from core.g_learning.g_i import run_g_i


def gh_input(**overrides):
    base = {
        "phase": "G",
        "subphase": "G-H",
        "status": "EXECUTION_PERMISSION_READY",
        "logical_execution_permission_ready": True,
        "execution_permission": False,
        "permission_package": {
            "permission_id": "permission-1",
            "execution_permission": False,
            "execution_runner_target": "G-I",
        },
        "constraints": {"constraints_hash": "constraints-hash"},
        "trace_chain": {"trace_id": "trace-id"},
        "risk_analysis": {"risk_score": 0.1, "confidence_score": 0.95, "risk_level": "LOW"},
        "execution_runner_target": "G-I",
        "permission_hash": "permission-hash",
        "output_hash": "output-hash",
        "deterministic": True,
    }
    base.update(overrides)
    return base


def request(**overrides):
    base = {
        "execution_request_id": "exec-1",
        "request_version": "v1.3",
        "requested_by": "Romel",
        "identity_verified": True,
        "execution_mode": "DRY_RUN_ONLY",
        "runner_capability_mode": "REPORT_ONLY",
        "controlled_run_unlocked": False,
        "physical_mutation_allowed": False,
        "emergency_stop_status": "INACTIVE",
        "allowed_operations": [
            {
                "operation_id": "op-1",
                "operation_type": "CONTROLLED_REPORT_GENERATION",
                "target_path": "00_SYSTEM/reports/g_learning/dry_run_report.txt",
                "max_bytes": 1024,
                "file_type": ".txt",
            }
        ],
        "idempotency_key": "idem-1",
    }
    base.update(overrides)
    return base


def test_valid_dry_run_completed():
    result = run_g_i(gh_input(), request())
    assert result["status"] == "DRY_RUN_COMPLETED"
    assert result["physical_mutation_allowed"] is False
    assert result["permission_state"] == "UNUSED"
    assert result["mutation_ledger"][0]["status"] == "SIMULATED"


def test_controlled_run_blocked():
    result = run_g_i(gh_input(), request(execution_mode="CONTROLLED_RUN"))
    assert result["status"] == "EXECUTION_BLOCKED"


def test_physical_mutation_blocked():
    result = run_g_i(gh_input(), request(physical_mutation_allowed=True))
    assert result["status"] == "EXECUTION_BLOCKED"


def test_emergency_stop_blocks():
    result = run_g_i(gh_input(), request(emergency_stop_status="ACTIVE"))
    assert result["status"] == "EXECUTION_BLOCKED"


def test_path_traversal_blocks():
    bad = request()
    bad["allowed_operations"][0]["target_path"] = "../evil.txt"
    result = run_g_i(gh_input(), bad)
    assert result["status"] == "EXECUTION_BLOCKED"


def test_out_of_sandbox_blocks():
    bad = request()
    bad["allowed_operations"][0]["target_path"] = "00_SYSTEM/core/g_learning/evil.txt"
    result = run_g_i(gh_input(), bad)
    assert result["status"] == "EXECUTION_BLOCKED"


def test_blocked_operation_type_blocks():
    bad = request()
    bad["allowed_operations"][0]["operation_type"] = "DELETE"
    result = run_g_i(gh_input(), bad)
    assert result["status"] == "EXECUTION_BLOCKED"


def test_risk_high_blocks():
    result = run_g_i(gh_input(risk_analysis={"risk_score": 0.9, "confidence_score": 0.7, "risk_level": "HIGH"}), request())
    assert result["status"] == "EXECUTION_BLOCKED"


def test_risk_medium_review_required():
    result = run_g_i(gh_input(risk_analysis={"risk_score": 0.5, "confidence_score": 0.8, "risk_level": "MEDIUM"}), request())
    assert result["status"] == "REVIEW_REQUIRED"


def test_shell_token_blocks():
    bad = request()
    bad["allowed_operations"][0]["target_path"] = "00_SYSTEM/reports/g_learning/powershell.txt"
    result = run_g_i(gh_input(), bad)
    assert result["status"] == "EXECUTION_BLOCKED"


def test_deterministic_output():
    a = run_g_i(gh_input(), request())
    b = run_g_i(gh_input(), request())
    assert a["output_hash"] == b["output_hash"]
    assert a["evidence_hash"] == b["evidence_hash"]
    assert a["journal_hash"] == b["journal_hash"]
