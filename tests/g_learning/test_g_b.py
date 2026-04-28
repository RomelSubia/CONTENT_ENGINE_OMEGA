import sys
from pathlib import Path

root = Path(r"D:\CONTENT_ENGINE_OMEGA\00_SYSTEM")
sys.path.insert(0, str(root))

from core.g_learning.g_b import run_g_b


def valid_record(record_type, index, data):
    return {
        "type": record_type,
        "index": index,
        "data": data,
        "source_hash": f"hash-{record_type}-{index}",
        "origin": "F",
        "timestamp": "2026-04-28T00:00:00Z",
    }


def valid_input(records=None, evidence_quality=1.0, evidence_count=5):
    if records is None:
        records = [
            valid_record("logs", 0, {"event": "run_started"}),
            valid_record("logs", 1, {"event": "run_started"}),
            valid_record("metrics", 2, {"runtime": 1.2}),
            valid_record("outcomes", 3, {"status": "ok"}),
            valid_record("outcomes", 4, {"status": "ok"}),
        ]

    return {
        "phase": "G",
        "source_subphase": "G-A",
        "status": "VALID",
        "evidence_quality": evidence_quality,
        "evidence_count": evidence_count,
        "records": records,
        "input_hash": "input-hash",
        "output_hash": "output-hash",
    }


def test_valid_input_returns_learning_report():
    result = run_g_b(valid_input())
    assert result["status"] == "VALID"
    assert result["final_decision"] == "LEARNING_REPORT_READY"
    assert result["deterministic"] is True
    assert result["confidence_score"] <= 1.0


def test_missing_contract_blocks():
    payload = valid_input()
    del payload["input_hash"]
    result = run_g_b(payload)
    assert result["status"] == "BLOCKED"
    assert "MISSING_INPUT_KEYS" in result["final_decision"]


def test_corrupt_record_blocks():
    payload = valid_input()
    del payload["records"][0]["source_hash"]
    result = run_g_b(payload)
    assert result["status"] == "BLOCKED"
    assert "MISSING_RECORD_KEYS" in result["final_decision"]


def test_no_pattern_found():
    records = [
        valid_record("logs", 0, {"event": "a"}),
        valid_record("metrics", 1, {"runtime": 1}),
        valid_record("decisions", 2, {"decision": "x"}),
        valid_record("outcomes", 3, {"status": "ok"}),
        valid_record("logs", 4, {"event": "b"}),
    ]
    result = run_g_b(valid_input(records=records))
    assert result["status"] == "NO_PATTERN_FOUND"


def test_contradiction_returns_review_required():
    records = [
        valid_record("outcomes", 0, {"status": "ok"}),
        valid_record("outcomes", 1, {"status": "ok"}),
        valid_record("logs", 2, {"error": "failure"}),
        valid_record("logs", 3, {"error": "failure"}),
        valid_record("metrics", 4, {"runtime": 1}),
    ]
    result = run_g_b(valid_input(records=records))
    assert result["status"] == "REVIEW_REQUIRED"
    assert result["pattern_state"] == "CONFLICTING_PATTERN"


def test_confidence_never_exceeds_evidence_quality():
    result = run_g_b(valid_input(evidence_quality=0.85))
    assert result["confidence_score"] <= 0.85


def test_deterministic_hash():
    payload = valid_input()
    a = run_g_b(payload)
    b = run_g_b(payload)
    assert a["output_hash"] == b["output_hash"]
    assert a["input_hash"] == b["input_hash"]


def test_low_evidence_quality_blocks():
    result = run_g_b(valid_input(evidence_quality=0.50))
    assert result["status"] == "BLOCKED"
    assert result["final_decision"] == "EVIDENCE_QUALITY_TOO_LOW"
