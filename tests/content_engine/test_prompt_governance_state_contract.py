from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.prompt_governance import build_prompt_governance_state, validate_prompt_governance_state


def test_state_passes():
    assert validate_prompt_governance_state(build_prompt_governance_state())["status"] == "PASS"


def test_state_blocks_prompt_production_negative():
    state = build_prompt_governance_state()
    state["prompt_production_started"] = True
    assert validate_prompt_governance_state(state)["status"] == "BLOCK"


def test_state_blocks_final_prompt_negative():
    state = build_prompt_governance_state()
    state["final_prompt_generation_started"] = True
    assert validate_prompt_governance_state(state)["status"] == "BLOCK"


def test_state_blocks_content_generation_negative():
    state = build_prompt_governance_state()
    state["content_generation_started"] = True
    assert validate_prompt_governance_state(state)["status"] == "BLOCK"


def test_state_blocks_human_authorization_simulation_negative():
    state = build_prompt_governance_state()
    state["human_authorization_simulated"] = True
    assert validate_prompt_governance_state(state)["status"] == "BLOCK"
