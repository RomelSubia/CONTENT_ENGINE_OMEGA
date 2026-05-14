from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.strategy_foundation.channel_registry import (
    CANONICAL_CHANNEL_IDS,
    build_channel_registry,
    validate_channel_id,
    validate_channel_registry,
)


def test_registry_passes():
    assert validate_channel_registry(build_channel_registry())["status"] == "PASS"


def test_registry_has_four_canonical_channels():
    assert len(CANONICAL_CHANNEL_IDS) == 4


def test_unknown_channel_blocks_negative():
    assert validate_channel_id("UNKNOWN")["status"] == "BLOCK"


def test_ambiguous_alias_blocks_negative():
    assert validate_channel_id("money")["status"] == "BLOCK"


def test_channel_1_alias_blocks_negative():
    assert validate_channel_id("channel_1")["status"] == "BLOCK"


def test_registry_blocks_missing_purpose_negative():
    registry = build_channel_registry()
    key = list(registry["channels"].keys())[0]
    registry["channels"][key]["core_purpose"] = ""
    assert validate_channel_registry(registry)["status"] == "BLOCK"


def test_all_channel_ids_start_with_channel_prefix():
    assert all(channel_id.startswith("CHANNEL_") for channel_id in CANONICAL_CHANNEL_IDS)
