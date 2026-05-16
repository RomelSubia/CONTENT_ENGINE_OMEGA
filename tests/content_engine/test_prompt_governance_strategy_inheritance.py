from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.prompt_governance import build_required_inheritance, validate_strategy_foundation_inheritance


def test_inheritance_passes():
    assert validate_strategy_foundation_inheritance(build_required_inheritance())["status"] == "PASS"


def test_inheritance_blocks_wrong_strategy_status_negative():
    evidence = build_required_inheritance()
    evidence["strategy_foundation_core_status"] = "BUILT"
    assert validate_strategy_foundation_inheritance(evidence)["status"] == "BLOCK"


def test_inheritance_blocks_wrong_seal_negative():
    evidence = build_required_inheritance()
    evidence["strategy_foundation_seal"] = "BAD"
    assert validate_strategy_foundation_inheritance(evidence)["status"] == "BLOCK"


def test_inheritance_has_four_channels():
    assert len(build_required_inheritance()["canonical_channel_ids"]) == 4


def test_inheritance_blocks_missing_boundary_negative():
    evidence = build_required_inheritance()
    evidence["boundary_rules_available"] = False
    assert validate_strategy_foundation_inheritance(evidence)["status"] == "BLOCK"
