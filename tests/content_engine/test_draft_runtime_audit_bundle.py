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

from content_engine.content_draft_runtime_governance.runtime_governance_envelope import build_runtime_governance_envelope
from content_engine.content_draft_runtime_governance.runtime_audit_bundle import build_runtime_audit_bundle

def test_audit_bundle_passes():
    assert build_runtime_audit_bundle(build_runtime_governance_envelope(sample_request()))["status"] == "PASS"

def test_audit_bundle_canonical_required():
    assert build_runtime_audit_bundle(build_runtime_governance_envelope(sample_request()))["canonical_json_required"] is True

def test_audit_bundle_has_manifest():
    assert build_runtime_audit_bundle(build_runtime_governance_envelope(sample_request()))["runtime_manifest"] is True

def test_audit_bundle_has_seal():
    assert build_runtime_audit_bundle(build_runtime_governance_envelope(sample_request()))["runtime_seal"] is True

def test_audit_bundle_human_review_marker():
    assert build_runtime_audit_bundle(build_runtime_governance_envelope(sample_request()))["runtime_human_review_marker"] is True

def test_audit_bundle_no_productive_claims():
    assert build_runtime_audit_bundle(build_runtime_governance_envelope(sample_request()))["productive_effect_claims"] is False

def test_audit_bundle_failure_flag_for_bad_preview():
    envelope = build_runtime_governance_envelope(sample_request(), "final caption")
    assert build_runtime_audit_bundle(envelope)["runtime_failure_report"] is True

def test_audit_bundle_hash_algorithm():
    assert build_runtime_audit_bundle(build_runtime_governance_envelope(sample_request()))["hash_algorithm"] == "sha256"
