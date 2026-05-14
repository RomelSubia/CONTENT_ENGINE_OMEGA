from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.strategy_foundation.strategy_state_contract import build_strategy_state, validate_strategy_state


def test_state_passes():
    assert validate_strategy_state(build_strategy_state())["status"] == "PASS"


def test_state_blocks_content_generation_negative():
    state = build_strategy_state()
    state["content_generation_started"] = True
    assert validate_strategy_state(state)["status"] == "BLOCK"


def test_state_blocks_prompt_generation_negative():
    state = build_strategy_state()
    state["prompt_generation_started"] = True
    assert validate_strategy_state(state)["status"] == "BLOCK"


def test_state_blocks_queue_write_negative():
    state = build_strategy_state()
    state["queue_write_started"] = True
    assert validate_strategy_state(state)["status"] == "BLOCK"


def test_state_blocks_publishing_negative():
    state = build_strategy_state()
    state["publishing_started"] = True
    assert validate_strategy_state(state)["status"] == "BLOCK"


def test_state_next_safe_step():
    assert build_strategy_state()["next_safe_step"] == "CONTENT_ENGINE_STRATEGY_FOUNDATION_POST_BUILD_AUDIT"
