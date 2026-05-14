from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.strategy_foundation.strategy_quality_contract import REQUIRED_CRITERIA, build_quality_contract, evaluate_quality, validate_quality_result


def test_quality_contract_passes():
    assert build_quality_contract()["status"] == "PASS"


def test_quality_item_passes():
    item = {criterion: True for criterion in REQUIRED_CRITERIA}
    assert evaluate_quality(item)["status"] == "PASS"


def test_quality_missing_channel_alignment_blocks_negative():
    item = {criterion: True for criterion in REQUIRED_CRITERIA}
    item["channel_alignment"] = False
    assert evaluate_quality(item)["status"] == "BLOCK"


def test_quality_unknown_result_blocks_negative():
    assert validate_quality_result("UNKNOWN")["status"] == "BLOCK"


def test_quality_needs_review_allowed():
    assert validate_quality_result("NEEDS_REVIEW")["status"] == "PASS"


def test_quality_block_allowed():
    assert validate_quality_result("BLOCK")["status"] == "PASS"
