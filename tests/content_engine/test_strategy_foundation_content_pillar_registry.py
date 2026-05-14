from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.strategy_foundation.content_pillar_registry import PILLARS, build_pillar_registry, validate_pillars


def test_pillars_pass():
    assert validate_pillars(PILLARS)["status"] == "PASS"


def test_registry_status_pass():
    assert build_pillar_registry()["status"] == "PASS"


def test_pillar_without_channel_blocks_negative():
    pillars = list(PILLARS)
    pillars[0] = dict(pillars[0], channel_id="UNKNOWN")
    assert validate_pillars(pillars)["status"] == "BLOCK"


def test_duplicate_pillar_id_blocks_negative():
    pillars = list(PILLARS) + [dict(PILLARS[0])]
    assert validate_pillars(pillars)["status"] == "BLOCK"


def test_missing_purpose_blocks_negative():
    pillars = list(PILLARS)
    pillars[0] = dict(pillars[0], pillar_purpose="")
    assert validate_pillars(pillars)["status"] == "BLOCK"


def test_each_channel_has_minimum_pillars():
    assert validate_pillars(PILLARS)["count_failures"] == {}
