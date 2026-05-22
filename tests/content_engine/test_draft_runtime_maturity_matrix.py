from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY_ROOT = ROOT / "04_SCRIPTS" / "python"
if str(PY_ROOT) not in sys.path:
    sys.path.insert(0, str(PY_ROOT))


from content_engine.content_draft_runtime_governance.runtime_maturity_matrix import validate_maturity_level

def test_level_zero_passes():
    assert validate_maturity_level(0)["status"] == "PASS"

def test_level_one_blocks():
    assert validate_maturity_level(1)["status"] == "FAILED_BLOCKED"

def test_autonomy_zero():
    assert validate_maturity_level(0)["runtime_autonomy_level_now"] == 0

def test_escalation_false():
    assert validate_maturity_level(0)["autonomy_escalation_allowed"] is False

def test_levels_include_advanced():
    assert 8 in validate_maturity_level(0)["levels"]

def test_negative_blocks():
    assert validate_maturity_level(-1)["status"] == "FAILED_BLOCKED"

def test_string_zero_passes():
    assert validate_maturity_level("0")["status"] == "PASS"

def test_string_one_blocks():
    assert validate_maturity_level("1")["status"] == "FAILED_BLOCKED"
