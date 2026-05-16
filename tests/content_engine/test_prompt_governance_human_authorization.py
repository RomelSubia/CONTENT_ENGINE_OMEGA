from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.prompt_governance import validate_human_authorization_prompt


def test_safe_authorization_reference_passes():
    assert validate_human_authorization_prompt("require_real_human_authorization_later")["status"] == "PASS"


def test_simulate_authorization_blocks_negative():
    assert validate_human_authorization_prompt("simulate_human_authorization")["status"] == "BLOCK"


def test_assume_approval_blocks_negative():
    assert validate_human_authorization_prompt("assume_romel_approved")["status"] == "BLOCK"


def test_continue_without_approval_blocks_negative():
    assert validate_human_authorization_prompt("continue_without_approval")["status"] == "BLOCK"


def test_act_as_authorized_blocks_negative():
    assert validate_human_authorization_prompt("act_as_if_authorized")["status"] == "BLOCK"
