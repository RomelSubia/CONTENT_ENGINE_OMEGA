from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.strategy_foundation.channel_registry import CHANNEL_A, CHANNEL_B, CHANNEL_C, CHANNEL_D
from content_engine.strategy_foundation.channel_separation_matrix import build_separation_matrix, validate_channel_mix


def test_matrix_passes():
    assert build_separation_matrix()["status"] == "PASS"


def test_same_channel_passes():
    assert validate_channel_mix(CHANNEL_A, CHANNEL_A)["status"] == "PASS"


def test_blocked_mix_blocks_negative():
    assert validate_channel_mix(CHANNEL_A, CHANNEL_B)["status"] == "BLOCK"


def test_allowed_bridge_requires_rule_negative():
    assert validate_channel_mix(CHANNEL_A, CHANNEL_C, has_bridge_rule=False)["status"] == "BLOCK"


def test_allowed_bridge_passes_with_rule():
    assert validate_channel_mix(CHANNEL_A, CHANNEL_C, has_bridge_rule=True)["status"] == "PASS"


def test_d_to_c_blocks_negative():
    assert validate_channel_mix(CHANNEL_D, CHANNEL_C)["status"] == "BLOCK"
