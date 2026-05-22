from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY_ROOT = ROOT / "04_SCRIPTS" / "python"
if str(PY_ROOT) not in sys.path:
    sys.path.insert(0, str(PY_ROOT))


from content_engine.content_draft_runtime_governance.runtime_failure_policy import fail_closed

def test_fail_closed_status():
    assert fail_closed("MISSING_EVIDENCE")["status"] == "FAILED_BLOCKED"

def test_fail_closed_state():
    assert fail_closed("MISSING_EVIDENCE")["runtime_state"] == "RUNTIME_FAILED_CLOSED"

def test_fail_closed_human_review():
    assert fail_closed("MISSING_EVIDENCE")["human_review_required"] is True

def test_fail_closed_flags_false():
    out = fail_closed("MISSING_EVIDENCE")
    for key in ["side_effects_performed", "draft_creation_performed", "content_generation_performed", "queue_write_performed", "publishing_performed", "automation_performed"]:
        assert out[key] is False

def test_fail_closed_refs():
    out = fail_closed("MISSING_EVIDENCE", evidence_refs=["ev"], traceability_refs=["tr"])
    assert out["evidence_refs"] == ["ev"]
    assert out["traceability_refs"] == ["tr"]

def test_unknown_reason_maps_runtime_state_drift():
    assert fail_closed("OTHER")["blocked_reason_code"] == "RUNTIME_STATE_DRIFT"

def test_manifest_refs_empty():
    assert fail_closed("MISSING_EVIDENCE")["manifest_refs"] == []

def test_seal_refs_empty():
    assert fail_closed("MISSING_EVIDENCE")["seal_refs"] == []
