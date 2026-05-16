from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.prompt_governance import validate_prompt_intent


def test_allowed_intent_passes():
    assert validate_prompt_intent("DEFINE_STRUCTURE")["status"] == "PASS"


def test_generate_final_script_blocks_negative():
    assert validate_prompt_intent("GENERATE_FINAL_SCRIPT")["status"] == "BLOCK"


def test_publish_now_blocks_negative():
    assert validate_prompt_intent("PUBLISH_NOW")["status"] == "BLOCK"


def test_call_webhook_blocks_negative():
    assert validate_prompt_intent("CALL_WEBHOOK")["status"] == "BLOCK"


def test_unknown_intent_blocks_negative():
    assert validate_prompt_intent("DO_ANYTHING")["status"] == "BLOCK"
