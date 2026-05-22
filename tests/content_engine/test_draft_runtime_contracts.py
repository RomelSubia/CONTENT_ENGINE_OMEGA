from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY_ROOT = ROOT / "04_SCRIPTS" / "python"
if str(PY_ROOT) not in sys.path:
    sys.path.insert(0, str(PY_ROOT))


from content_engine.content_draft_runtime_governance.runtime_contracts import ALLOWED_RUNTIME_MODES, BLOCKED_RUNTIME_MODES, PRODUCTIVE_FLAGS, RUNTIME_STATES, hard_false_flags

def test_allowed_modes_are_non_productive():
    assert {"PREVIEW_ONLY", "DRY_RUN_ONLY", "VALIDATION_ONLY", "NO_OP_AUDIT_ONLY"}.issubset(ALLOWED_RUNTIME_MODES)

def test_blocked_modes_are_productive():
    assert {"CREATE_DRAFT", "GENERATE_CONTENT", "WRITE_QUEUE", "PUBLISH", "AUTOMATE"}.issubset(BLOCKED_RUNTIME_MODES)

def test_productive_flags_all_hard_false():
    assert all(value is False for value in hard_false_flags().values())

def test_runtime_states_include_failed_closed():
    assert "RUNTIME_FAILED_CLOSED" in RUNTIME_STATES

def test_runtime_states_do_not_include_productive_created():
    assert "DRAFT_CREATED" not in RUNTIME_STATES

def test_productive_flags_include_queue_publish_automation():
    assert {"queue_write_performed", "publishing_performed", "automation_performed"}.issubset(set(PRODUCTIVE_FLAGS))

def test_hard_false_flags_complete():
    flags = hard_false_flags()
    assert "draft_creation_performed" in flags
    assert "content_generation_performed" in flags

def test_contracts_no_side_effect_baseline():
    assert hard_false_flags()["side_effects_performed"] is False
