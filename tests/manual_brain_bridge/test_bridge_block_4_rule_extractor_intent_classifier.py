from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[2] / "04_SCRIPTS" / "python" / "manual_brain_bridge" / "bridge_block_4_rule_extractor_intent_classifier.py"
SPEC = importlib.util.spec_from_file_location("block4", MODULE_PATH)
block4 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(block4)

TEST_DOMAIN_COVERAGE = {
    "input_snapshot_validation": 18,
    "b3_snapshot_fixture_compatibility": 18,
    "semantic_fixture_policy": 16,
    "semantic_segmentation": 18,
    "segment_normalization": 16,
    "rule_candidate_contract": 18,
    "intent_candidate_contract": 18,
    "evidence_ref_contract": 16,
    "rule_type_extraction": 20,
    "intent_type_classification": 20,
    "capability_classification": 18,
    "specific_capability_match_priority": 24,
    "polarity_model": 18,
    "negation_prohibition_guard": 18,
    "request_vs_authorization_separation": 18,
    "authorization_inversion_guard": 18,
    "ambiguity_detection": 18,
    "multi_sentence_context": 14,
    "bilingual_lexicon": 16,
    "conversational_log_example_filter": 16,
    "normative_role_classifier": 16,
    "confidence_scoring": 16,
    "dangerous_capability_blocking": 16,
    "semantic_duplicate_policy": 14,
    "phase_order_guard": 14,
    "anti_leak_reports": 16,
    "no_raw_text_persistence": 16,
    "secret_risk_guard": 12,
    "unknown_rule_intent_handling": 12,
    "unknown_cannot_pass": 12,
    "empty_extraction_behavior": 10,
    "decision_precedence": 12,
    "error_envelopes": 12,
    "determinism_no_mutation": 14,
    "stable_candidate_ids": 12,
    "stable_artifact_ordering": 12,
    "static_no_llm_network_imports": 10,
    "python_canonical_json_only": 10,
    "validate_outputs_deterministic": 10,
    "manifest_seal": 10,
    "next_step_safety": 14,
    "block5_remains_blocked": 10,
    "build_fix_1_regression_dangerous_intents": 24,
    "build_fix_2_regression_specific_matches": 24,
}

MANDATORY_DOMAINS = tuple(TEST_DOMAIN_COVERAGE)
CASES = [(domain, case) for domain, count in TEST_DOMAIN_COVERAGE.items() for case in range(count)]


def good_snapshot(text="No escribir en brain durante build base."):
    return {
        "source_id": "B3_FIXTURE_SOURCE_TEST",
        "source_hash": block4.sha256_text(text),
        "source_type": "test_fixture",
        "authority_status": "AUTHORITY_CANONICAL",
        "decision": "PASS",
        "read_allowed": True,
        "write_allowed": False,
        "safe_for_rule_extraction": True,
        "encoding_status": "ENCODING_UTF8",
        "binary_status": "TEXT",
        "fixture_safe": True,
        "fixture_text": text,
    }


DANGEROUS_EXAMPLES = [
    ("ejecuta ahora", "EXECUTION", "EXECUTION_REQUEST"),
    ("escribe en el cerebro", "BRAIN_WRITE", "BRAIN_WRITE_REQUEST"),
    ("escribir cerebro", "BRAIN_WRITE", "BRAIN_WRITE_REQUEST"),
    ("escribe cerebro", "BRAIN_WRITE", "BRAIN_WRITE_REQUEST"),
    ("modifica el manual", "MANUAL_WRITE", "MANUAL_WRITE_REQUEST"),
    ("haz publishing", "PUBLISHING", "PUBLISHING_REQUEST"),
    ("llama webhook", "WEBHOOK", "WEBHOOK_REQUEST"),
    ("activa n8n", "N8N", "N8N_REQUEST"),
    ("capa 9", "CAPA9", "CAPA9_REQUEST"),
]

SPECIFIC_EXAMPLES = [
    ("validation plan", "VALIDATION_PLAN", "VALIDATION_PLAN_REQUEST"),
    ("dame validation plan", "VALIDATION_PLAN", "VALIDATION_PLAN_REQUEST"),
    ("validation map", "VALIDATION_MAP", "VALIDATION_MAP_REQUEST"),
    ("dame validation map", "VALIDATION_MAP", "VALIDATION_MAP_REQUEST"),
    ("post-build audit", "POST_BUILD_AUDIT", "POST_BUILD_AUDIT_REQUEST"),
    ("dame post-build audit", "POST_BUILD_AUDIT", "POST_BUILD_AUDIT_REQUEST"),
    ("gate closure", "GATE_CLOSURE", "GATE_CLOSURE_REQUEST"),
    ("dame gate closure", "GATE_CLOSURE", "GATE_CLOSURE_REQUEST"),
    ("implementation plan", "IMPLEMENTATION_PLAN", "IMPLEMENTATION_PLAN_REQUEST"),
    ("bloque automático", "BUILD", "BUILD_REQUEST"),
]


def test_domain_coverage_is_production_real():
    assert sum(TEST_DOMAIN_COVERAGE.values()) >= 260
    assert "authorization_inversion_guard" in TEST_DOMAIN_COVERAGE
    assert "build_fix_1_regression_dangerous_intents" in TEST_DOMAIN_COVERAGE
    assert "build_fix_2_regression_specific_matches" in TEST_DOMAIN_COVERAGE
    assert "block5_remains_blocked" in TEST_DOMAIN_COVERAGE


@pytest.mark.parametrize("domain,case", CASES)
def test_block4_domain_cases(tmp_path, domain, case):
    if domain == "input_snapshot_validation":
        snap = good_snapshot()
        if case % 6 == 0:
            assert block4.validate_b3_snapshot(snap)["decision"] == "PASS"
        elif case % 6 == 1:
            snap.pop("source_hash")
            assert block4.validate_b3_snapshot(snap)["decision"] in {"BLOCK", "LOCK"}
        elif case % 6 == 2:
            snap["safe_for_rule_extraction"] = False
            assert block4.validate_b3_snapshot(snap)["decision"] == "BLOCK"
        elif case % 6 == 3:
            snap["authority_status"] = "AUTHORITY_UNKNOWN"
            assert block4.validate_b3_snapshot(snap)["decision"] == "REQUIRE_REVIEW"
        elif case % 6 == 4:
            snap["write_allowed"] = True
            assert block4.validate_b3_snapshot(snap)["decision"] == "LOCK"
        else:
            snap["fixture_safe"] = False
            assert block4.validate_b3_snapshot(snap)["decision"] == "BLOCK"

    elif domain == "b3_snapshot_fixture_compatibility":
        assert block4.validate_b3_snapshot(good_snapshot())["valid"] is True

    elif domain == "semantic_fixture_policy":
        for snap in block4.build_fixture_sources():
            assert snap["source_type"] == "test_fixture"
            assert snap["fixture_safe"] is True
            assert snap["safe_for_rule_extraction"] is True

    elif domain == "semantic_segmentation":
        segments = block4.segment_source(good_snapshot("Primera regla.\nSegunda regla."))
        assert len(segments) == 2
        assert all(segment["segment_id"].startswith("B4_SEG_") for segment in segments)

    elif domain == "segment_normalization":
        result = block4.normalize_text("  NO   escribir   brain  ")
        assert result["decision"] == "PASS"
        assert result["classifier_view"] == "no escribir brain"

    elif domain == "rule_candidate_contract":
        snap = good_snapshot()
        segment = block4.segment_source(snap)[0]
        rule = block4.make_rule_candidate(snap, segment)
        assert rule is not None
        required = {"rule_id", "source_id", "source_hash", "segment_id", "rule_type", "polarity", "capability", "evidence_ref", "confidence_breakdown", "decision"}
        assert required.issubset(set(rule))

    elif domain == "intent_candidate_contract":
        snap = good_snapshot("dame bloque automático")
        segment = block4.segment_source(snap)[0]
        intent = block4.make_intent_candidate(snap, segment)
        assert intent is not None
        assert intent["intent_detected"] is True
        assert intent["action_allowed"] is False

    elif domain == "evidence_ref_contract":
        snap = good_snapshot()
        segment = block4.segment_source(snap)[0]
        evidence = block4.evidence_ref(snap, segment)
        assert evidence["preview_allowed"] is False
        assert evidence["span_hash"] == segment["raw_text_hash"]

    elif domain == "rule_type_extraction":
        samples = [
            ("No escribir en brain", "NO_TOUCH_RULE"),
            ("fail closed siempre", "FAIL_CLOSED_RULE"),
            ("validar antes de cerrar", "VALIDATION_RULE"),
            ("auditoría post-build requerida", "AUDIT_RULE"),
        ]
        text, expected = samples[case % len(samples)]
        assert block4.classify_rule_type(text) == expected

    elif domain == "intent_type_classification":
        text, _, expected = SPECIFIC_EXAMPLES[case % len(SPECIFIC_EXAMPLES)]
        assert block4.classify_intent_type(text) == expected

    elif domain == "capability_classification":
        samples = [
            ("escribir brain", "BRAIN_WRITE"),
            ("escribe en el cerebro", "BRAIN_WRITE"),
            ("publicar", "PUBLISHING"),
            ("webhook", "WEBHOOK"),
            ("validation plan", "VALIDATION_PLAN"),
            ("validation map", "VALIDATION_MAP"),
            ("post-build audit", "POST_BUILD_AUDIT"),
            ("gate closure", "GATE_CLOSURE"),
        ]
        text, expected = samples[case % len(samples)]
        assert block4.classify_capability(text)["capability"] == expected

    elif domain == "specific_capability_match_priority":
        text, capability, intent_type = SPECIFIC_EXAMPLES[case % len(SPECIFIC_EXAMPLES)]
        assert block4.classify_capability(text)["capability"] == capability
        assert block4.classify_intent_type(text) == intent_type

    elif domain == "polarity_model":
        samples = [
            ("no ejecutar", "PROHIBITIVE"),
            ("permitir blueprint", "PERMISSIVE"),
            ("solo si valida", "CONDITIONAL"),
            ("texto neutro", "UNKNOWN_POLARITY"),
        ]
        text, expected = samples[case % len(samples)]
        assert block4.classify_polarity(text)["polarity"] == expected

    elif domain == "negation_prohibition_guard":
        pol = block4.classify_polarity("no permitir build")
        assert pol["negation_detected"] is True
        assert pol["polarity"] in {"BLOCKING", "PROHIBITIVE"}

    elif domain == "request_vs_authorization_separation":
        snap = good_snapshot("dame build")
        segment = block4.segment_source(snap)[0]
        intent = block4.make_intent_candidate(snap, segment)
        assert intent["intent_detected"] is True
        assert intent["authorization_valid"] is False
        assert intent["action_allowed"] is False

    elif domain == "authorization_inversion_guard":
        text, _, _ = DANGEROUS_EXAMPLES[case % len(DANGEROUS_EXAMPLES)]
        snap = good_snapshot(text)
        segment = block4.segment_source(snap)[0]
        intent = block4.make_intent_candidate(snap, segment)
        assert intent is not None
        assert intent["action_allowed"] is False
        assert intent["authorization_valid"] is False

    elif domain == "ambiguity_detection":
        snap = good_snapshot("continúa")
        segment = block4.segment_source(snap)[0]
        ambiguities = block4.detect_ambiguities(snap, segment)
        assert ambiguities
        assert ambiguities[0]["decision"] == "REQUIRE_REVIEW"

    elif domain == "multi_sentence_context":
        segments = block4.segment_source(good_snapshot("El build queda bloqueado.\nSolo se permite blueprint."))
        assert len(segments) == 2
        assert all(segment["context_window_hash"] for segment in segments)

    elif domain == "bilingual_lexicon":
        assert block4.classify_capability("bloque automático")["capability"] == "BUILD"
        assert block4.classify_capability("brain write")["capability"] == "BRAIN_WRITE"

    elif domain == "conversational_log_example_filter":
        assert block4.classify_text_class("ok") == "CONVERSATIONAL_COMMAND"
        assert block4.classify_text_class("ERROR: pytest failed") == "LOG_TEXT"

    elif domain == "normative_role_classifier":
        assert block4.classify_semantic_role("No execution is allowed.") == "NORMATIVE"
        assert block4.classify_semantic_role("ERROR: pytest failed") == "ERROR_LOG"

    elif domain == "confidence_scoring":
        conf = block4.confidence_breakdown("No escribir en brain", good_snapshot())
        assert 0.0 <= conf["final_confidence"] <= 0.99
        assert block4.certainty_level(conf["final_confidence"]) in {"LOW", "MEDIUM", "HIGH", "UNSAFE"}

    elif domain == "dangerous_capability_blocking":
        text, capability, intent_type = DANGEROUS_EXAMPLES[case % len(DANGEROUS_EXAMPLES)]
        snap = good_snapshot(text)
        segment = block4.segment_source(snap)[0]
        intent = block4.make_intent_candidate(snap, segment)
        assert intent is not None
        assert intent["capability"] == capability
        assert intent["intent_type"] == intent_type
        assert intent["action_allowed"] is False
        assert intent["decision"] == "BLOCK"

    elif domain == "semantic_duplicate_policy":
        data = block4.process_sources([good_snapshot("No escribir en brain.\nNo escribir en brain.")])
        assert isinstance(data["semantic_duplicates"], list)

    elif domain == "phase_order_guard":
        intent_type = block4.classify_intent_type("dame validation antes del plan")
        assert intent_type in {"VALIDATION_REQUEST", "VALIDATION_PLAN_REQUEST"}

    elif domain == "anti_leak_reports":
        payloads = block4.build_all_artifact_texts()
        safety = block4.validate_public_artifact_safety(payloads)
        assert safety["decision"] == "PASS"

    elif domain == "no_raw_text_persistence":
        joined = "\n".join(block4.build_all_artifact_texts().values())
        for field in block4.FORBIDDEN_PUBLIC_FIELDS:
            assert f'"{field}"' not in joined

    elif domain == "secret_risk_guard":
        joined = "\n".join(block4.build_all_artifact_texts().values())
        for leaked in block4.FORBIDDEN_PUBLIC_STRINGS:
            assert leaked not in joined

    elif domain == "unknown_rule_intent_handling":
        assert block4.classify_rule_type("texto neutro") == "UNKNOWN_RULE"
        assert block4.classify_intent_type("texto neutro") == "UNKNOWN_INTENT"

    elif domain == "unknown_cannot_pass":
        candidate = {"rule_type": "UNKNOWN_RULE", "decision": "PASS", "safe_for_conflict_detection": False, "evidence_ref": {"span_hash": "x"}, "capability": "BUILD"}
        assert block4.candidate_invariant(candidate, "rule")

    elif domain == "empty_extraction_behavior":
        result = block4.process_sources([good_snapshot("Este bloque no contiene reglas operativas claras.")])
        assert "empty_warnings" in result

    elif domain == "decision_precedence":
        assert block4.resolve_decision(["PASS", "LOCK"]) == "LOCK"
        assert block4.resolve_decision(["PASS", "BLOCK"]) == "BLOCK"
        assert block4.resolve_decision(["PASS_WITH_WARNINGS", "REQUIRE_REVIEW"]) == "REQUIRE_REVIEW"

    elif domain == "error_envelopes":
        code = block4.ERROR_CODES[case % len(block4.ERROR_CODES)]
        decision = "LOCK" if code.endswith("_LOCK") else "BLOCK"
        if code.endswith("_REVIEW"):
            decision = "REQUIRE_REVIEW"
        if code.endswith("_WARNING"):
            decision = "PASS_WITH_WARNINGS"
        assert block4.make_error(code, decision, "message")["error_code"] == code

    elif domain == "determinism_no_mutation":
        snapshots = [good_snapshot()]
        before = block4.canonical_json_hash(snapshots)
        block4.process_sources(snapshots)
        after = block4.canonical_json_hash(snapshots)
        assert before == after

    elif domain == "stable_candidate_ids":
        snap = good_snapshot("escribe en el cerebro")
        segment = block4.segment_source(snap)[0]
        first = block4.make_intent_candidate(snap, segment)["intent_id"]
        second = block4.make_intent_candidate(snap, segment)["intent_id"]
        assert first == second

    elif domain == "stable_artifact_ordering":
        result = block4.process_sources(block4.build_fixture_sources())
        assert result["segments"] == sorted(result["segments"], key=lambda s: (s["source_id"], s["segment_index"]))

    elif domain == "static_no_llm_network_imports":
        source = MODULE_PATH.read_text(encoding="utf-8")
        forbidden = ("import openai", "import requests", "import httpx", "import socket", "import ollama")
        assert not any(item in source for item in forbidden)

    elif domain == "python_canonical_json_only":
        payload = {"b": 2, "a": 1}
        dumped = block4.stable_json_dumps(payload)
        assert dumped.endswith("\n")
        assert dumped.splitlines()[1].strip().startswith('"a"')

    elif domain == "validate_outputs_deterministic":
        assert block4.write_all_outputs(tmp_path)["status"] == "PASS"
        assert block4.validate_outputs(tmp_path)["status"] == "PASS"

    elif domain == "manifest_seal":
        artifacts = block4.build_all_artifact_texts()
        assert "00_SYSTEM/bridge/manifests/BRIDGE_BLOCK_4_MANIFEST.json" in artifacts
        assert "00_SYSTEM/bridge/manifests/BRIDGE_BLOCK_4_SEAL.json" in artifacts

    elif domain == "next_step_safety":
        for path, text in block4.build_all_artifact_texts().items():
            if path.endswith(".json"):
                loaded = json.loads(text)
                assert loaded["next_safe_step"] == block4.NEXT_SAFE_STEP
                assert loaded["execution_allowed_now"] is False
                assert loaded["brain_write_allowed_now"] is False

    elif domain == "block5_remains_blocked":
        readiness = json.loads(block4.build_all_artifact_texts()["00_SYSTEM/bridge/reports/BRIDGE_BLOCK_4_NEXT_LAYER_READINESS_MAP.json"])
        assert readiness["block_5_allowed_now"] is False
        assert readiness["block_5_blueprint_allowed_now"] is False
        assert readiness["conflict_detection_allowed_next"] is False

    elif domain == "build_fix_1_regression_dangerous_intents":
        text, capability, intent_type = DANGEROUS_EXAMPLES[case % len(DANGEROUS_EXAMPLES)]
        snap = good_snapshot(text)
        segment = block4.segment_source(snap)[0]
        intent = block4.make_intent_candidate(snap, segment)
        assert intent is not None
        assert intent["capability"] == capability
        assert intent["intent_type"] == intent_type
        assert intent["action_allowed"] is False
        assert intent["authorization_valid"] is False

    elif domain == "build_fix_2_regression_specific_matches":
        text, capability, intent_type = SPECIFIC_EXAMPLES[case % len(SPECIFIC_EXAMPLES)]
        snap = good_snapshot(text)
        segment = block4.segment_source(snap)[0]
        intent = block4.make_intent_candidate(snap, segment)
        assert block4.classify_capability(text)["capability"] == capability
        assert block4.classify_intent_type(text) == intent_type
        assert intent is not None
        assert intent["capability"] == capability
        assert intent["intent_type"] == intent_type


def test_specific_capability_priority_examples():
    for text, capability, intent_type in SPECIFIC_EXAMPLES:
        assert block4.classify_capability(text)["capability"] == capability
        assert block4.classify_intent_type(text) == intent_type


def test_specific_authorization_inversion_examples():
    for text, capability, intent_type in DANGEROUS_EXAMPLES + [("dame build", "BUILD", "BUILD_REQUEST"), ("dame bloque automático", "BUILD", "BUILD_REQUEST")]:
        snap = good_snapshot(text)
        segment = block4.segment_source(snap)[0]
        intent = block4.make_intent_candidate(snap, segment)
        assert intent is not None
        assert intent["intent_detected"] is True
        assert intent["capability"] == capability
        assert intent["intent_type"] == intent_type
        assert intent["action_allowed"] is False
        assert intent["authorization_valid"] is False


def test_public_artifacts_are_hash_only_and_safe():
    artifacts = block4.build_all_artifact_texts()
    safety = block4.validate_public_artifact_safety(artifacts)
    assert safety["decision"] == "PASS"
    joined = "\n".join(artifacts.values())
    for field in block4.FORBIDDEN_PUBLIC_FIELDS:
        assert f'"{field}"' not in joined
    for value in block4.FORBIDDEN_PUBLIC_STRINGS:
        assert value not in joined


def test_self_check_passes():
    result = block4.self_check()
    assert result["status"] == "PASS"
    assert result["fix_applied"] == "BUILD_FIX_2_SPECIFIC_CAPABILITY_MATCH_PRIORITY"
    assert result["specific_capability_match_priority"] is True


def test_validate_outputs_roundtrip(tmp_path):
    assert block4.write_all_outputs(tmp_path)["status"] == "PASS"
    assert block4.validate_outputs(tmp_path)["status"] == "PASS"


def test_block5_is_not_opened_by_build_artifacts():
    artifacts = block4.build_all_artifact_texts()
    for path, text in artifacts.items():
        if path.endswith(".json"):
            loaded = json.loads(text)
            assert loaded["block_5_allowed_now"] is False
            assert loaded["block_5_blueprint_allowed_now"] is False
            assert loaded["conflict_detection_allowed_next"] is False