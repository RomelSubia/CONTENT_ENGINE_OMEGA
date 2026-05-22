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

def test_envelope_passes_safe_request():
    assert build_runtime_governance_envelope(sample_request())["output"]["status"] == "PASS"

def test_envelope_side_effects_not_allowed():
    assert build_runtime_governance_envelope(sample_request())["side_effects_allowed"] is False

def test_envelope_requires_evidence():
    assert build_runtime_governance_envelope(sample_request())["evidence_required"] is True

def test_envelope_requires_traceability():
    assert build_runtime_governance_envelope(sample_request())["traceability_required"] is True

def test_envelope_requires_manifest():
    assert build_runtime_governance_envelope(sample_request())["manifest_required"] is True

def test_envelope_requires_seal():
    assert build_runtime_governance_envelope(sample_request())["seal_required"] is True

def test_envelope_blocks_final_output():
    assert build_runtime_governance_envelope(sample_request(), "final script")["output"]["status"] == "FAILED_BLOCKED"

def test_envelope_no_draft_created():
    assert build_runtime_governance_envelope(sample_request())["output"]["draft_creation_performed"] is False
