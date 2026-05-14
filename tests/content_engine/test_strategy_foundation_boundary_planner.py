from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.strategy_foundation.strategy_boundary_planner import (
    build_boundary_plan,
    validate_action_allowed,
    validate_permissions,
)


def test_boundary_plan_passes():
    assert build_boundary_plan()["status"] == "PASS"


def test_dangerous_permissions_false():
    assert validate_permissions()["status"] == "PASS"


def test_dangerous_permission_true_blocks_negative():
    matrix = build_boundary_plan()["dangerous_permissions"]
    matrix["content_generation_allowed_now"] = True
    assert validate_permissions(matrix)["status"] == "BLOCK"


def test_generate_script_blocks_negative():
    assert validate_action_allowed("generate_script")["status"] == "BLOCK"


def test_publish_blocks_negative():
    assert validate_action_allowed("publish")["status"] == "BLOCK"


def test_n8n_blocks_negative():
    assert validate_action_allowed("trigger_n8n")["status"] == "BLOCK"


def test_webhook_blocks_negative():
    assert validate_action_allowed("send_webhook")["status"] == "BLOCK"


def test_safe_strategy_action_passes():
    assert validate_action_allowed("define_strategy_rule")["status"] == "PASS"
