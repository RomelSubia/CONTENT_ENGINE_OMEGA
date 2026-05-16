from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.prompt_governance import validate_language_tone


def test_channel_a_tone_passes():
    assert validate_language_tone("CHANNEL_A_MONEY_MINDSET_CONVERSION", "es-LatAm", "directo")["status"] == "PASS"


def test_wrong_language_blocks_negative():
    assert validate_language_tone("CHANNEL_A_MONEY_MINDSET_CONVERSION", "en-US", "directo")["status"] == "BLOCK"


def test_wrong_tone_blocks_negative():
    assert validate_language_tone("CHANNEL_D_AI_TECH_PERSONAL_BRAND", "es-LatAm", "motivacional_generico")["status"] == "BLOCK"


def test_cross_channel_tone_blocks_negative():
    assert validate_language_tone("CHANNEL_B_CURIOSITIES_MASS_TRAFFIC", "es-LatAm", "conversion_agresiva")["status"] == "BLOCK"


def test_unknown_channel_blocks_negative():
    assert validate_language_tone("UNKNOWN", "es-LatAm", "directo")["status"] == "BLOCK"
