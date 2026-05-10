from __future__ import annotations

import pytest

from manual_brain_bridge import bridge_block_9_test_harness_40_pruebas as b9


REGISTRY = b9.build_test_registry()


@pytest.mark.parametrize("case", REGISTRY, ids=lambda case: case["test_id"])
def test_each_block9_case_has_complete_contract(case):
    assert case["test_id"].startswith("B9-T")
    assert case["test_name"]
    assert case["domain_id"].startswith("B9-D-")
    assert case["block_coverage"]
    assert case["fixture_id"].startswith("FX-B9-T")
    assert len(case["fixture_hash"]) == 64
    assert len(case["input_payload_hash"]) == 64
    assert case["minimum_assertions"] >= 3
    assert case["expected_no_touch"] is True
    assert all(value is False for value in case["expected_permissions"].values())


def test_block9_registry_has_45_tests():
    assert len(REGISTRY) == 45
    assert len({case["test_id"] for case in REGISTRY}) == 45


def test_block9_negative_and_failure_injection_thresholds():
    negative = [case for case in REGISTRY if case["negative"]]
    failure = [case for case in REGISTRY if case["failure_injection"]]
    assert len(negative) >= 12
    assert len(failure) >= 10
    assert all(case["expected_status"] == b9.LOCK for case in failure)


def test_block9_assertion_matrix_thresholds():
    results = b9.execute_test_registry(REGISTRY)
    matrix = b9.build_assertion_matrix(REGISTRY, results)
    assert matrix["status"] == b9.PASS
    assert matrix["total_assertions"] >= 135
    assert all(count >= 3 for count in matrix["per_test"].values())


def test_block9_coverage_report_meets_block_minimums():
    coverage = b9.build_coverage_report(REGISTRY)
    assert coverage["status"] == b9.PASS
    assert coverage["cross_block_e2e_count"] >= 4
    for block, minimum in coverage["minimums"].items():
        assert coverage["coverage_by_block"][block] >= minimum


def test_block9_deterministic_replay_passes():
    replay = b9.build_deterministic_replay_report()
    assert replay["status"] == b9.PASS
    assert replay["first_hash"] == replay["second_hash"]
    assert replay["deterministic_replay_pass"] is True


def test_block9_permission_boundary_blocks_all_dangerous_permissions():
    report = b9.build_permission_boundary_report()
    assert report["status"] == b9.PASS
    assert report["post_build_audit_allowed_next"] is True
    assert report["dangerous_permissions_all_false"] is True
    assert report["blocked_next_layers"] is True


def test_block9_registry_immutability_passes():
    report = b9.build_registry_immutability_report()
    assert report["status"] == b9.PASS
    assert report["registry_hash_before"] == report["registry_hash_after"]
    assert report["registry_immutable_during_execution"] is True


def test_block9_execution_results_separate_from_registry():
    registry_hash = b9.sha256_text(b9.canonical_json(REGISTRY))
    results = b9.execute_test_registry(REGISTRY)
    after_hash = b9.sha256_text(b9.canonical_json(REGISTRY))
    assert registry_hash == after_hash
    assert len(results) == len(REGISTRY)
    assert all(row["result"] == b9.PASS for row in results)


def test_block9_harness_validation_passes():
    validation = b9.validate_harness()
    assert validation["status"] == b9.PASS
    assert validation["test_count"] == 45
    assert validation["negative_test_count"] >= 12
    assert validation["failure_injection_count"] >= 10
    assert validation["total_assertions"] >= 135
    assert validation["unknown_count"] == 0
    assert validation["fail_unexpected_count"] == 0
    assert validation["gate_count"] == 22
    assert validation["passed_gate_count"] == 22


def test_block9_next_layer_readiness_only_allows_post_build_audit():
    readiness = b9.build_next_layer_readiness_map()
    assert readiness["status"] == b9.PASS
    assert readiness["post_build_audit_allowed_next"] is True
    assert readiness["validation_map_allowed_now"] is False
    assert readiness["validation_plan_allowed_now"] is False
    assert readiness["validation_allowed_now"] is False
    assert readiness["gate_closure_allowed_now"] is False
    assert readiness["bloque_10_blueprint_allowed_now"] is False
    assert readiness["bloque_10_build_allowed_now"] is False
    assert readiness["execution_allowed_now"] is False
    assert readiness["manual_write_allowed_now"] is False
    assert readiness["brain_write_allowed_now"] is False
    assert readiness["reports_brain_write_allowed_now"] is False


def test_block9_report_payload_set_is_complete():
    payloads = b9.build_block9_report_payloads(
        git_context={"head_short": "311cc15", "head_subject": "Close MANUAL-CEREBRO bridge block 8 atomic writer lock quarantine recovery"},
        consumed_chain_discovery={"status": b9.PASS, "blocks": {}, "resolver_mode": "test"},
        consumed_chain_summary={"status": b9.PASS, "blocks": {}, "artifact_count": 0},
        protected_before={},
        protected_after={},
    )
    expected = {
        "BRIDGE_BLOCK_9_TEST_HARNESS_REPORT.json",
        "BRIDGE_BLOCK_9_TEST_CASES_REGISTRY.json",
        "BRIDGE_BLOCK_9_SCENARIO_MATRIX.json",
        "BRIDGE_BLOCK_9_ASSERTION_MATRIX.json",
        "BRIDGE_BLOCK_9_FAILURE_INJECTION_MATRIX.json",
        "BRIDGE_BLOCK_9_EXECUTION_RESULTS.json",
        "BRIDGE_BLOCK_9_COVERAGE_REPORT.json",
        "BRIDGE_BLOCK_9_DETERMINISTIC_REPLAY_REPORT.json",
        "BRIDGE_BLOCK_9_PERMISSION_BOUNDARY_REPORT.json",
        "BRIDGE_BLOCK_9_NO_TOUCH_REPORT.json",
        "BRIDGE_BLOCK_9_CONSUMED_CHAIN_DISCOVERY_REPORT.json",
        "BRIDGE_BLOCK_9_CONSUMED_CHAIN_ARTIFACTS_REPORT.json",
        "BRIDGE_BLOCK_9_REGISTRY_IMMUTABILITY_REPORT.json",
        "BRIDGE_BLOCK_9_NEXT_LAYER_READINESS_MAP.json",
    }
    assert set(payloads) == expected
    assert all(payload["status"] == "BUILT_PENDING_POST_AUDIT" for payload in payloads.values())
    assert all(payload["result"] == b9.PASS for payload in payloads.values())
