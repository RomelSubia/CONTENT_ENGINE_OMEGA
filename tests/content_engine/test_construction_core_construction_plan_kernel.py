from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.construction_core.construction_plan_kernel import (
    build_construction_plan,
    deterministic_plan_hash,
    validate_construction_plan,
)


def test_construction_plan_passes():
    plan = build_construction_plan()
    assert validate_construction_plan(plan)["status"] == "PASS"


def test_construction_plan_target():
    assert build_construction_plan()["target"] == "CONTENT_ENGINE_CONSTRUCTION_CORE"


def test_construction_plan_execution_false():
    assert build_construction_plan()["execution_allowed_now"] is False


def test_construction_plan_hash_deterministic():
    assert deterministic_plan_hash() != "NON_DETERMINISTIC"


def test_construction_plan_blocks_wrong_target_negative():
    plan = build_construction_plan()
    plan["target"] = "FULL_CONTENT_ENGINE"
    assert validate_construction_plan(plan)["status"] == "BLOCK"
