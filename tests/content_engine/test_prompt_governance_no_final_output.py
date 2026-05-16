from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.prompt_governance import validate_no_final_output


def test_structure_schema_passes():
    assert validate_no_final_output("structure_schema")["status"] == "PASS"


def test_final_script_blocks_negative():
    assert validate_no_final_output("final_script")["status"] == "BLOCK"


def test_ready_caption_blocks_negative():
    assert validate_no_final_output("ready_caption")["status"] == "BLOCK"


def test_ready_publish_pack_blocks_negative():
    assert validate_no_final_output("ready_publish_pack")["status"] == "BLOCK"


def test_ready_queue_item_blocks_negative():
    assert validate_no_final_output("ready_queue_item")["status"] == "BLOCK"
