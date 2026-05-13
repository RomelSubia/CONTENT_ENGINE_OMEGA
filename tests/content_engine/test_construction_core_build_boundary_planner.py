from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.construction_core.build_boundary_planner import (
    build_boundary_plan,
    detect_scope_violations,
    is_allowed_output,
    is_protected_output,
)


def test_boundary_plan_passes():
    plan = build_boundary_plan()
    assert plan["status"] == "PASS"


def test_allowed_output_accepts_content_engine_source():
    assert is_allowed_output("04_SCRIPTS/python/content_engine/construction_core/state_contract.py") is True


def test_allowed_output_rejects_random_path_negative():
    assert is_allowed_output("random/file.txt") is False


def test_protected_output_detects_brain_negative():
    assert is_protected_output("00_SYSTEM/brain/state.json") is True


def test_scope_violation_blocks_protected_negative():
    result = detect_scope_violations(["00_SYSTEM/brain/state.json"])
    assert result["status"] == "BLOCK"


def test_scope_violation_passes_allowed_paths():
    result = detect_scope_violations(["tests/content_engine/test_x.py"])
    assert result["status"] == "PASS"
