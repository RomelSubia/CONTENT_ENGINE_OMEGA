from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.construction_core import (
    build_construction_plan,
    build_domain_registry,
    build_failure_report,
    build_permission_matrix,
    build_state,
    compare_fingerprints,
    deterministic_plan_hash,
    validate_construction_plan,
    validate_domain_registry,
    validate_failure_report,
    validate_permission_matrix,
    validate_state,
)


def test_integration_state_permission_plan_pass():
    assert validate_state(build_state())["status"] == "PASS"
    assert validate_permission_matrix(build_permission_matrix())["status"] == "PASS"
    assert validate_construction_plan(build_construction_plan())["status"] == "PASS"


def test_integration_domain_registry_pass():
    assert validate_domain_registry(build_domain_registry())["status"] == "PASS"


def test_integration_failure_report_pass():
    assert validate_failure_report(build_failure_report("x", "g"))["status"] == "PASS"


def test_integration_no_touch_pass():
    assert compare_fingerprints({"brain": "A"}, {"brain": "A"})["status"] == "PASS"


def test_integration_no_touch_blocks_negative():
    assert compare_fingerprints({"brain": "A"}, {"brain": "B"})["status"] == "BLOCK"


def test_integration_plan_hash_exists():
    assert len(deterministic_plan_hash()) == 64


def test_integration_permissions_block_generation():
    matrix = build_permission_matrix()
    assert matrix["content_generation_allowed_now"] is False
    assert matrix["publishing_execution_allowed_now"] is False


def test_integration_next_step_only_post_build_audit():
    matrix = build_permission_matrix()
    assert matrix["content_engine_construction_post_build_audit_allowed_next"] is True
    assert matrix["content_engine_construction_validation_map_allowed_now"] is False
