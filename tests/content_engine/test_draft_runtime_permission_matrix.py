from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY_ROOT = ROOT / "04_SCRIPTS" / "python"
if str(PY_ROOT) not in sys.path:
    sys.path.insert(0, str(PY_ROOT))


from content_engine.content_draft_runtime_governance.runtime_permission_matrix import permission_matrix, state_allows_productive_action

def test_matrix_no_state_allows_productive_actions():
    for state in permission_matrix():
        assert state_allows_productive_action(state) is False

def test_preview_ready_only_conceptual_preview():
    assert permission_matrix()["RUNTIME_PREVIEW_READY"]["preview"] == "conceptual_limited"

def test_requires_human_review_read_only():
    assert permission_matrix()["RUNTIME_REQUIRES_HUMAN_REVIEW"]["preview"] == "read_only"

def test_sealed_no_op_evidence_only():
    assert permission_matrix()["RUNTIME_SEALED_NO_OP"]["preview"] == "evidence_only"

def test_queue_false_everywhere():
    assert all(row["queue"] is False for row in permission_matrix().values())

def test_publish_false_everywhere():
    assert all(row["publish"] is False for row in permission_matrix().values())

def test_automation_false_everywhere():
    assert all(row["automation"] is False for row in permission_matrix().values())

def test_draft_false_everywhere():
    assert all(row["draft"] is False for row in permission_matrix().values())
