from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.prompt_governance import validate_prompt_safety_action


def test_safe_action_passes():
    assert validate_prompt_safety_action("define_conceptual_structure")["status"] == "PASS"


def test_write_final_script_blocks_negative():
    assert validate_prompt_safety_action("write_final_script")["status"] == "BLOCK"


def test_send_to_queue_blocks_negative():
    assert validate_prompt_safety_action("send_to_queue")["status"] == "BLOCK"


def test_trigger_n8n_blocks_negative():
    assert validate_prompt_safety_action("trigger_n8n")["status"] == "BLOCK"


def test_activate_capa9_blocks_negative():
    assert validate_prompt_safety_action("activate_capa9")["status"] == "BLOCK"
