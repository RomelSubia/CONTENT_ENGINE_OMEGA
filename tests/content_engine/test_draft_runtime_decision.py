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

def test_safe_preview_decision_passes():
    result = decide_runtime_governance(sample_request(), "concept only")
    assert result["status"] == "PASS"

def test_final_caption_blocks():
    assert decide_runtime_governance(sample_request(), "final caption")["status"] == "FAILED_BLOCKED"

def test_publish_now_blocks():
    assert decide_runtime_governance(sample_request(), "publish now")["status"] == "FAILED_BLOCKED"

def test_queue_mode_blocks():
    assert decide_runtime_governance(sample_request(runtime_mode="WRITE_QUEUE"))["status"] == "FAILED_BLOCKED"

def test_decision_is_preview_only():
    assert decide_runtime_governance(sample_request())["preview_only"] is True

def test_decision_is_non_publishable():
    assert decide_runtime_governance(sample_request())["non_publishable"] is True

def test_decision_requires_human_review():
    assert decide_runtime_governance(sample_request())["human_review_required"] is True

def test_decision_carries_refs():
    result = decide_runtime_governance(sample_request())
    assert result["evidence_refs"] == ["ev-1"]
    assert result["traceability_refs"] == ["tr-1"]
