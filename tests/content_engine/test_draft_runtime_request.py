from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY_ROOT = ROOT / "04_SCRIPTS" / "python"
if str(PY_ROOT) not in sys.path:
    sys.path.insert(0, str(PY_ROOT))


def sample_request(**updates):
    data = {
        "runtime_request_id": "rr-001",
        "draft_candidate_id": "dc-001",
        "channel_or_domain_id": "digital_a",
        "runtime_mode": "PREVIEW_ONLY",
        "requested_action": "preview",
        "maturity_level": 0,
        "evidence_refs": ["ev-1"],
        "traceability_refs": ["tr-1"],
        "human_review_required": True,
        "actor_context": {"actor": "human"},
        "created_at": "2026-05-22T00:00:00Z",
        "schema_version": "1.0",
    }
    data.update(updates)
    return data

import pytest
from content_engine.content_draft_runtime_governance.runtime_request import validate_runtime_request

def test_valid_request_passes():
    assert validate_runtime_request(sample_request())["status"] == "PASS"

@pytest.mark.parametrize("field", ["runtime_request_id", "draft_candidate_id", "channel_or_domain_id", "runtime_mode", "evidence_refs", "traceability_refs", "human_review_required", "schema_version"])
def test_missing_required_field_blocks(field):
    req = sample_request()
    req.pop(field)
    assert validate_runtime_request(req)["status"] == "FAILED_BLOCKED"

@pytest.mark.parametrize("mode", ["CREATE_DRAFT", "GENERATE_CONTENT", "WRITE_QUEUE", "PUBLISH", "AUTOMATE", "UNKNOWN"])
def test_blocked_runtime_modes_fail_closed(mode):
    assert validate_runtime_request(sample_request(runtime_mode=mode))["status"] == "FAILED_BLOCKED"

def test_missing_evidence_blocks():
    assert validate_runtime_request(sample_request(evidence_refs=[]))["blocked_reason_code"] == "MISSING_EVIDENCE"

def test_missing_traceability_blocks():
    assert validate_runtime_request(sample_request(traceability_refs=[]))["blocked_reason_code"] == "MISSING_TRACEABILITY"

def test_human_review_false_blocks():
    assert validate_runtime_request(sample_request(human_review_required=False))["blocked_reason_code"] == "HUMAN_REVIEW_MISSING"

def test_bad_domain_blocks():
    assert validate_runtime_request(sample_request(channel_or_domain_id="other"))["blocked_reason_code"] == "UNSUPPORTED_DOMAIN_OR_CHANNEL"

def test_maturity_non_zero_blocks():
    assert validate_runtime_request(sample_request(maturity_level=1))["blocked_reason_code"] == "INVALID_MATURITY_LEVEL"
