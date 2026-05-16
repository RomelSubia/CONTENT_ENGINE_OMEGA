from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.prompt_governance import (
    REQUIRED_CRITERIA,
    build_prompt_governance_state,
    build_prompt_type_registry,
    build_required_inheritance,
    build_prompt_evidence_contract,
    build_prompt_failure_report,
    classify_prompt_risk,
    classify_semantic_safety,
    validate_channel_prompt_binding,
    validate_human_authorization_prompt,
    validate_indirect_generation,
    validate_language_tone,
    validate_manifest_completeness,
    validate_no_final_output,
    validate_no_full_prompt_body,
    validate_policy_override,
    validate_prompt_execution_boundary,
    validate_prompt_governance_idempotency,
    validate_prompt_governance_state,
    validate_prompt_intent,
    validate_prompt_quality,
    validate_prompt_safety_action,
    validate_prompt_type,
    validate_prompt_version,
    validate_prompt_failure_report,
    validate_strategy_foundation_inheritance,
    validate_test_fixture_boundary,
)

VALID_PAYLOAD = {
        "prompt_id": "PG_CONCEPTUAL_001",
        "prompt_type": "IDEA_PROMPT_TEMPLATE_CONCEPTUAL",
        "channel_id": "CHANNEL_A_MONEY_MINDSET_CONVERSION",
        "prompt_intent": "DEFINE_STRUCTURE",
        "allowed_tone": ["directo"],
        "blocked_tone": ["venta_agresiva"],
        "allowed_output_shape": ["structure_schema"],
        "blocked_output_shape": ["final_script"],
        "pillar_reference": "A_MENTALIDAD_FINANCIERA",
        "audience_reference": "AUD_A_DISCIPLINA_ECONOMICA",
        "quality_rules": ["channel_alignment"],
        "safety_rules": ["no_generation_trigger"],
    }


def valid_version():
    return {
        "prompt_id": "PG-001",
        "prompt_version": "v1",
        "channel_id": "CHANNEL_A_MONEY_MINDSET_CONVERSION",
        "prompt_type": "IDEA_PROMPT_TEMPLATE_CONCEPTUAL",
        "classification": "CONCEPTUAL_ONLY",
        "status": "CONCEPTUAL_DRAFT",
        "created_by_layer": "CONTENT_ENGINE_PROMPT_GOVERNANCE_CORE",
        "previous_version": "NONE",
        "change_reason": "initial",
        "content_hash": "abc123",
        "evidence_reference": "report.json",
        "created_at_layer_step": "BUILD",
    }


def test_integration_core_contracts_pass():
    assert validate_prompt_governance_state(build_prompt_governance_state())["status"] == "PASS"
    assert validate_strategy_foundation_inheritance(build_required_inheritance())["status"] == "PASS"
    assert build_prompt_type_registry()["status"] == "PASS"
    assert validate_channel_prompt_binding(VALID_PAYLOAD)["status"] == "PASS"
    assert build_prompt_evidence_contract()["status"] == "PASS"


def test_integration_balance_contracts_pass():
    assert validate_prompt_type("IDEA_PROMPT_TEMPLATE_CONCEPTUAL")["status"] == "PASS"
    assert validate_prompt_intent("DEFINE_STRUCTURE")["status"] == "PASS"
    assert validate_prompt_execution_boundary({"classification": "CONCEPTUAL_ONLY"})["status"] == "PASS"
    assert validate_no_final_output("structure_schema")["status"] == "PASS"
    assert validate_no_full_prompt_body("schema")["status"] == "PASS"


def test_integration_safety_blocks_negative():
    assert validate_prompt_safety_action("publish_now")["status"] == "BLOCK"
    assert classify_semantic_safety("publica ahora")["status"] == "BLOCK"
    assert classify_prompt_risk("script", "final script")["status"] == "BLOCK"


def test_integration_policy_authorization_blocks_negative():
    assert validate_policy_override("bypass_governance")["status"] == "BLOCK"
    assert validate_human_authorization_prompt("simulate_human_authorization")["status"] == "BLOCK"


def test_integration_version_failure_idempotency():
    assert validate_prompt_version(valid_version())["status"] == "PASS"
    assert validate_prompt_failure_report(build_prompt_failure_report("x", "g"))["status"] == "PASS"
    assert validate_prompt_governance_idempotency("CLOSED_VALIDATED")["status"] == "BLOCK"


def test_integration_language_and_indirect_generation():
    assert validate_language_tone("CHANNEL_A_MONEY_MINDSET_CONVERSION", "es-LatAm", "directo")["status"] == "PASS"
    assert validate_indirect_generation(["final_caption"])["status"] == "BLOCK"


def test_integration_fixture_boundary():
    assert validate_test_fixture_boundary("negative_test_fixture", True)["status"] == "PASS"
    assert validate_test_fixture_boundary("production_template", True)["status"] == "BLOCK"


def test_integration_manifest_completeness():
    assert validate_manifest_completeness(["a"], ["a"])["status"] == "PASS"


def test_integration_quality_passes():
    assert validate_prompt_quality({key: True for key in REQUIRED_CRITERIA})["status"] == "PASS"


def test_integration_queue_webhook_capa9_blocks_negative():
    assert validate_prompt_safety_action("send_to_queue")["status"] == "BLOCK"
    assert validate_prompt_safety_action("call_webhook")["status"] == "BLOCK"
    assert validate_prompt_safety_action("activate_capa9")["status"] == "BLOCK"
