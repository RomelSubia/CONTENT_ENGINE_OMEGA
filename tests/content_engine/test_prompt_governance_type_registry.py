from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.prompt_governance import build_prompt_type_registry, validate_prompt_type


def test_type_registry_passes():
    assert build_prompt_type_registry()["status"] == "PASS"


def test_conceptual_type_passes():
    assert validate_prompt_type("IDEA_PROMPT_TEMPLATE_CONCEPTUAL")["status"] == "PASS"


def test_final_script_type_blocks_negative():
    assert validate_prompt_type("FINAL_SCRIPT_PROMPT")["status"] == "BLOCK"


def test_ready_publish_type_blocks_negative():
    assert validate_prompt_type("READY_TO_PUBLISH_PROMPT")["status"] == "BLOCK"


def test_classification_mismatch_blocks_negative():
    assert validate_prompt_type("IDEA_PROMPT_TEMPLATE_CONCEPTUAL", "PRODUCTIVE_PROMPT")["status"] == "BLOCK"
