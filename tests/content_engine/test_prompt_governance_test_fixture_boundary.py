from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.prompt_governance import validate_test_fixture_boundary


def test_negative_fixture_passes():
    assert validate_test_fixture_boundary("negative_test_fixture", True)["status"] == "PASS"


def test_operational_prompt_with_danger_blocks_negative():
    assert validate_test_fixture_boundary("operational_prompt", True)["status"] == "BLOCK"


def test_production_template_with_danger_blocks_negative():
    assert validate_test_fixture_boundary("production_template", True)["status"] == "BLOCK"


def test_active_prompt_with_danger_blocks_negative():
    assert validate_test_fixture_boundary("active_prompt", True)["status"] == "BLOCK"


def test_safe_context_without_danger_passes():
    assert validate_test_fixture_boundary("operational_prompt", False)["status"] == "PASS"
