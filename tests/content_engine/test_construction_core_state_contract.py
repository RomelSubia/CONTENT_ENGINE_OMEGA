from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.construction_core.state_contract import build_state, validate_state


def test_state_contract_passes():
    state = build_state()
    assert state["current_status"] == "BUILT_PENDING_POST_AUDIT"
    assert validate_state(state)["status"] == "PASS"


def test_state_blocks_execution_started_negative():
    state = build_state()
    state["execution_started"] = True
    assert validate_state(state)["status"] == "BLOCK"


def test_state_blocks_wrong_bridge_status_negative():
    state = build_state()
    state["consumed_bridge_status"] = "WRONG"
    assert validate_state(state)["status"] == "BLOCK"


def test_state_next_safe_step_is_post_build_audit():
    state = build_state()
    assert state["next_safe_step"] == "CONTENT_ENGINE_CONSTRUCTION_POST_BUILD_AUDIT"


def test_state_blocks_all_sensitive_actions():
    state = build_state()
    assert "N8N" in state["blocked_actions"]
    assert "CAPA9" in state["blocked_actions"]
    assert "BRAIN_WRITE" in state["blocked_actions"]
