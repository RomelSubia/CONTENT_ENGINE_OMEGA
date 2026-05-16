from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.prompt_governance import validate_prompt_execution_boundary


def test_conceptual_boundary_passes():
    assert validate_prompt_execution_boundary({"classification": "CONCEPTUAL_ONLY"})["status"] == "PASS"


def test_productive_prompt_blocks_negative():
    assert validate_prompt_execution_boundary({"classification": "PRODUCTIVE_PROMPT"})["status"] == "BLOCK"


def test_executable_prompt_blocks_negative():
    assert validate_prompt_execution_boundary({"classification": "EXECUTABLE_PROMPT"})["status"] == "BLOCK"


def test_can_generate_final_content_blocks_negative():
    assert validate_prompt_execution_boundary({"classification": "STRUCTURAL_TEMPLATE", "can_generate_final_content": True})["status"] == "BLOCK"


def test_can_publish_blocks_negative():
    assert validate_prompt_execution_boundary({"classification": "STRUCTURAL_TEMPLATE", "can_publish": True})["status"] == "BLOCK"
