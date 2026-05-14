from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.strategy_foundation.channel_registry import CHANNEL_A, CHANNEL_B, CHANNEL_C
from content_engine.strategy_foundation.channel_rule_engine import block_productive_prompt, validate_channel_payload


def test_channel_payload_passes():
    assert validate_channel_payload(CHANNEL_A)["status"] == "PASS"


def test_channel_payload_unknown_blocks_negative():
    assert validate_channel_payload("UNKNOWN")["status"] == "BLOCK"


def test_cross_channel_without_rule_blocks_negative():
    assert validate_channel_payload(CHANNEL_A, CHANNEL_B)["status"] == "BLOCK"


def test_cross_channel_with_bridge_passes():
    assert validate_channel_payload(CHANNEL_A, CHANNEL_C, has_bridge_rule=True)["status"] == "PASS"


def test_final_prompt_blocks_negative():
    assert block_productive_prompt("final_script_prompt")["status"] == "BLOCK"


def test_strategy_prompt_rule_passes():
    assert block_productive_prompt("prompt_strategy_rules")["status"] == "PASS"
