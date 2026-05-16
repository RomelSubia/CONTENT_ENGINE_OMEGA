from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.prompt_governance import REQUIRED_CRITERIA, validate_prompt_quality, validate_quality_result


def test_quality_passes():
    assert validate_prompt_quality({key: True for key in REQUIRED_CRITERIA})["status"] == "PASS"


def test_quality_missing_channel_blocks_negative():
    payload = {key: True for key in REQUIRED_CRITERIA}
    payload["channel_alignment"] = False
    assert validate_prompt_quality(payload)["status"] == "BLOCK"


def test_quality_pass_result_allowed():
    assert validate_quality_result("PASS")["status"] == "PASS"


def test_quality_needs_review_allowed():
    assert validate_quality_result("NEEDS_REVIEW")["status"] == "PASS"


def test_quality_unknown_blocks_negative():
    assert validate_quality_result("MAYBE")["status"] == "BLOCK"
