from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.prompt_governance import classify_prompt_risk


def test_low_risk_passes():
    assert classify_prompt_risk("review", "quality checklist")["status"] == "PASS"


def test_medium_risk_passes():
    assert classify_prompt_risk("hook", "structure")["status"] == "PASS"


def test_high_risk_structural_passes():
    assert classify_prompt_risk("script structure", "non final structure")["status"] == "PASS"


def test_critical_final_blocks_negative():
    assert classify_prompt_risk("script", "final script")["status"] == "BLOCK"


def test_critical_automation_blocks_negative():
    assert classify_prompt_risk("workflow", "structure", automation_trigger=True)["status"] == "BLOCK"
