from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.prompt_governance import validate_indirect_generation


def test_non_final_outline_passes():
    assert validate_indirect_generation(["non_final_outline"])["status"] == "PASS"


def test_final_hook_blocks_negative():
    assert validate_indirect_generation(["final_hook"])["status"] == "BLOCK"


def test_final_cta_blocks_negative():
    assert validate_indirect_generation(["final_cta"])["status"] == "BLOCK"


def test_final_caption_blocks_negative():
    assert validate_indirect_generation(["final_caption"])["status"] == "BLOCK"


def test_ready_publish_structure_blocks_negative():
    assert validate_indirect_generation(["ready_publish_structure"])["status"] == "BLOCK"
