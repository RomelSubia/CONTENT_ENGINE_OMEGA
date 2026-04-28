import sys
from pathlib import Path

root = Path(r"D:\CONTENT_ENGINE_OMEGA\00_SYSTEM")
sys.path.insert(0, str(root))

from core.g_learning.g_c import run_g_c


def valid_input(confidence=0.90):
    return {
        "phase": "G",
        "subphase": "G-B",
        "status": "VALID",
        "pattern_state": "VALID",
        "confidence_score": confidence,
        "patterns": [
            {"pattern_key": "logs:event:run_started", "pattern_type": "REPEATED_EVENT", "count": 2}
        ],
        "signals": [
            {"pattern_key": "logs:event:run_started", "strength": 0.9, "level": "HIGH"}
        ],
        "hypotheses": [
            {"pattern_key": "logs:event:run_started", "hypothesis_type": "ASSOCIATION_ONLY"}
        ],
        "false_learning_flags": [],
        "deterministic": True,
        "input_hash": "input-hash",
        "records_hash": "records-hash",
        "config_hash": "config-hash",
        "output_hash": "output-hash",
    }


def test_valid_input_ready_for_review():
    result = run_g_c(valid_input())
    assert result["status"] == "VALID"
    assert result["decision"] == "READY_FOR_REVIEW"
    assert result["recommendation_count"] == 1
    assert result["recommendations"][0]["auto_apply_allowed"] is False


def test_invalid_input_blocks():
    payload = valid_input()
    del payload["input_hash"]
    result = run_g_c(payload)
    assert result["status"] == "BLOCKED"
    assert "MISSING_INPUT_KEYS" in result["decision"]


def test_low_confidence_no_recommendation():
    result = run_g_c(valid_input(confidence=0.50))
    assert result["status"] == "NO_RECOMMENDATION"
    assert result["decision"] == "NO_RECOMMENDATION"


def test_false_learning_flags_block():
    payload = valid_input()
    payload["false_learning_flags"] = [{"type": "BAD"}]
    result = run_g_c(payload)
    assert result["status"] == "BLOCKED"
    assert result["decision"] == "FALSE_LEARNING_FLAGS_PRESENT"


def test_not_deterministic_blocks():
    payload = valid_input()
    payload["deterministic"] = False
    result = run_g_c(payload)
    assert result["status"] == "BLOCKED"
    assert result["decision"] == "SOURCE_NOT_DETERMINISTIC"


def test_no_patterns_no_recommendation():
    payload = valid_input()
    payload["patterns"] = []
    result = run_g_c(payload)
    assert result["status"] == "NO_RECOMMENDATION"


def test_deterministic_output_hash():
    payload = valid_input()
    a = run_g_c(payload)
    b = run_g_c(payload)
    assert a["output_hash"] == b["output_hash"]
    assert a["recommendation_hash"] == b["recommendation_hash"]


def test_recommendation_contract_enforced():
    result = run_g_c(valid_input())
    rec = result["recommendations"][0]
    assert rec["requires_human_approval"] is True
    assert rec["rollback_required"] is True
    assert rec["reversible"] is True
    assert rec["touch_scope"] == "READ_ONLY"
