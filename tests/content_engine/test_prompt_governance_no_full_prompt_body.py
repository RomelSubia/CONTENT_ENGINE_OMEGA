from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.prompt_governance import validate_no_full_prompt_body


def test_schema_passes():
    assert validate_no_full_prompt_body("schema")["status"] == "PASS"


def test_complete_prompt_body_blocks_negative():
    assert validate_no_full_prompt_body("complete_prompt_body")["status"] == "BLOCK"


def test_copy_paste_ready_prompt_blocks_negative():
    assert validate_no_full_prompt_body("copy_paste_ready_prompt")["status"] == "BLOCK"


def test_complete_caption_prompt_blocks_negative():
    assert validate_no_full_prompt_body("complete_caption_prompt")["status"] == "BLOCK"


def test_production_prompt_pack_blocks_negative():
    assert validate_no_full_prompt_body("production_prompt_pack")["status"] == "BLOCK"
