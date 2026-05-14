from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.strategy_foundation.audience_profile_registry import AUDIENCES, build_audience_registry, validate_audiences


def test_audience_registry_passes():
    assert validate_audiences(AUDIENCES)["status"] == "PASS"


def test_audience_registry_disallows_personal_data():
    assert build_audience_registry()["personal_data_allowed"] is False


def test_audience_without_channel_blocks_negative():
    audiences = list(AUDIENCES)
    audiences[0] = dict(audiences[0], channel_id="UNKNOWN")
    assert validate_audiences(audiences)["status"] == "BLOCK"


def test_audience_with_personal_data_blocks_negative():
    audiences = list(AUDIENCES)
    audiences[0] = dict(audiences[0], exact_address="x")
    assert validate_audiences(audiences)["status"] == "BLOCK"


def test_audience_missing_pain_points_blocks_negative():
    audiences = list(AUDIENCES)
    audiences[0] = dict(audiences[0], pain_points=[])
    assert validate_audiences(audiences)["status"] == "BLOCK"


def test_audience_has_abstract_profiles():
    assert all("AUD_" in audience["audience_id"] for audience in AUDIENCES)
