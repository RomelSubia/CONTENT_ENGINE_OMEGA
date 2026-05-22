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

from content_engine.content_draft_runtime_governance.runtime_decision import decide_runtime_governance
from content_engine.content_draft_runtime_governance.runtime_output import make_runtime_output

def test_output_passes_safe_decision():
    out = make_runtime_output(decide_runtime_governance(sample_request()))
    assert out["status"] == "PASS"

def test_output_all_productive_flags_false():
    out = make_runtime_output(decide_runtime_governance(sample_request()))
    for key in ["side_effects_performed", "draft_creation_performed", "content_generation_performed", "queue_write_performed", "publishing_performed", "automation_performed"]:
        assert out[key] is False

def test_output_non_publishable():
    assert make_runtime_output(decide_runtime_governance(sample_request()))["non_publishable"] is True

def test_output_human_review_required():
    assert make_runtime_output(decide_runtime_governance(sample_request()))["human_review_required"] is True

def test_output_no_manifest_side_effect_refs():
    assert make_runtime_output(decide_runtime_governance(sample_request()))["manifest_refs"] == []

def test_output_no_seal_side_effect_refs():
    assert make_runtime_output(decide_runtime_governance(sample_request()))["seal_refs"] == []

def test_failed_output_still_hard_false():
    out = make_runtime_output(decide_runtime_governance(sample_request(runtime_mode="PUBLISH")))
    assert out["status"] == "FAILED_BLOCKED"
    assert out["publishing_performed"] is False

def test_output_carries_evidence():
    assert make_runtime_output(decide_runtime_governance(sample_request()))["evidence_refs"] == ["ev-1"]
