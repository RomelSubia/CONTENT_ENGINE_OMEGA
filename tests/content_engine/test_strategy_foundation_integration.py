from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.strategy_foundation import (
    block_productive_prompt,
    build_audience_registry,
    build_boundary_plan,
    build_channel_registry,
    build_evidence_contract,
    build_failure_report,
    build_identity_contracts,
    build_learning_placeholder,
    build_lifecycle_contract,
    build_pillar_registry,
    build_quality_contract,
    build_separation_matrix,
    build_strategy_state,
    validate_action_allowed,
    validate_audiences,
    validate_channel_payload,
    validate_channel_registry,
    validate_failure_report,
    validate_identity_contracts,
    validate_learning_action,
    validate_lifecycle_state,
    validate_permissions,
    validate_pillars,
    validate_strategy_state,
)


def test_integration_all_core_contracts_pass():
    assert validate_strategy_state(build_strategy_state())["status"] == "PASS"
    assert validate_channel_registry(build_channel_registry())["status"] == "PASS"
    assert validate_identity_contracts(build_identity_contracts())["status"] == "PASS"
    assert validate_pillars(build_pillar_registry()["pillars"])["status"] == "PASS"
    assert validate_audiences(build_audience_registry()["audiences"])["status"] == "PASS"


def test_integration_boundary_and_learning_pass():
    assert validate_permissions(build_boundary_plan()["dangerous_permissions"])["status"] == "PASS"
    assert build_learning_placeholder()["status"] == "PASS"


def test_integration_evidence_quality_lifecycle_pass():
    assert build_evidence_contract()["status"] == "PASS"
    assert build_quality_contract()["status"] == "PASS"
    assert build_lifecycle_contract()["status"] == "PASS"


def test_integration_separation_matrix_pass():
    assert build_separation_matrix()["status"] == "PASS"


def test_integration_productive_prompt_blocked_negative():
    assert block_productive_prompt("ready_to_publish_script")["status"] == "BLOCK"


def test_integration_generate_script_blocked_negative():
    assert validate_action_allowed("generate_script")["status"] == "BLOCK"


def test_integration_publish_blocked_negative():
    assert validate_action_allowed("publish")["status"] == "BLOCK"


def test_integration_metrics_api_blocked_negative():
    assert validate_learning_action("connect_api")["status"] == "BLOCK"


def test_integration_execution_lifecycle_blocked_negative():
    assert validate_lifecycle_state("WEBHOOK_REAL")["status"] == "BLOCK"


def test_integration_failure_policy_blocks_execution():
    report = build_failure_report("x", "g")
    assert validate_failure_report(report)["status"] == "PASS"
    assert report["execution_started"] is False
