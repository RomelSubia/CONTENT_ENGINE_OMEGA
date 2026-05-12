from __future__ import annotations

from manual_brain_bridge import bridge_block_10_validation_audit_commit_push_sync as b10


def test_state_matrix_contains_allowed_states_and_blocks_ambiguous_states():
    matrix = b10.build_state_matrix()
    assert matrix["status"] == b10.PASS
    assert "BLOQUE_10_BUILT_PENDING_POST_AUDIT" in matrix["allowed_states"]
    assert "MANUAL_CEREBRO_BRIDGE_CLOSED_VALIDATED" in matrix["allowed_states"]
    assert "READY" in matrix["ambiguous_states_blocked"]
    assert b10.evaluate_state_transition("READY", artifact=True, manifest=True, seal=True, hash_valid=True)["status"] == b10.BLOCK


def test_valid_state_requires_artifact_manifest_seal_and_hash():
    assert b10.evaluate_state_transition("BLOQUE_10_BUILT_PENDING_POST_AUDIT", artifact=True, manifest=True, seal=True, hash_valid=True)["status"] == b10.PASS
    assert b10.evaluate_state_transition("BLOQUE_10_BUILT_PENDING_POST_AUDIT", artifact=False, manifest=True, seal=True, hash_valid=True)["status"] == b10.BLOCK
    assert b10.evaluate_state_transition("BLOQUE_10_BUILT_PENDING_POST_AUDIT", artifact=True, manifest=False, seal=True, hash_valid=True)["status"] == b10.BLOCK
    assert b10.evaluate_state_transition("BLOQUE_10_BUILT_PENDING_POST_AUDIT", artifact=True, manifest=True, seal=False, hash_valid=True)["status"] == b10.BLOCK
    assert b10.evaluate_state_transition("BLOQUE_10_BUILT_PENDING_POST_AUDIT", artifact=True, manifest=True, seal=True, hash_valid=False)["status"] == b10.BLOCK


def test_permission_boundary_keeps_dangerous_permissions_false():
    boundary = b10.build_permission_boundary()
    assert boundary["status"] == b10.PASS
    assert boundary["post_build_audit_allowed_next"] is True
    assert boundary["dangerous_permissions_all_false"] is True
    for key, value in boundary["permissions"].items():
        if key != "bloque_10_post_build_audit_allowed_next":
            assert value is False


def test_failure_recovery_policy_blocks_dirty_out_of_scope_and_remote_divergence():
    policy = b10.build_failure_recovery_policy()
    assert policy["status"] == b10.PASS
    assert policy["rules"]["dirty_out_of_scope"]["status"] == b10.BLOCK
    assert policy["rules"]["remote_divergence"]["status"] == b10.BLOCK
    assert policy["rules"]["protected_root_changed"]["status"] == "CRITICAL_BLOCK"
    assert policy["rules"]["hash_mismatch"]["commit"] is False


def test_evidence_policy_blocks_missing_real_and_requires_block9_direct():
    policy = b10.build_evidence_discovery_policy()
    assert policy["status"] == b10.PASS
    assert policy["rules"]["MISSING_REAL"] == b10.BLOCK
    assert b10.evaluate_evidence_resolution(9, "DIRECT_ARTIFACTS")["status"] == b10.PASS
    assert b10.evaluate_evidence_resolution(9, "SEMANTIC_ARTIFACTS")["status"] == b10.BLOCK
    assert b10.evaluate_evidence_resolution(1, "TRACEABILITY_ANCHORED")["status"] == b10.PASS
    assert b10.evaluate_evidence_resolution(8, "TRACEABILITY_ANCHORED")["status"] == b10.BLOCK


def test_git_chain_and_push_sync_contracts_are_strict():
    git_chain = b10.build_git_chain_contract()
    sync = b10.build_push_sync_contract()
    assert git_chain["status"] == b10.PASS
    assert git_chain["requirements"]["head_parent_short"] == "4832275"
    assert git_chain["requirements"]["head_equals_upstream"] is True
    assert sync["status"] == b10.PASS
    assert sync["requirements"]["remote_divergence"] is False
    assert sync["requirements"]["unpushed_commits"] == 0
    assert sync["requirements"]["unpulled_commits"] == 0


def test_anti_simulation_blocks_common_false_claims():
    contract = b10.build_anti_simulation_contract()
    assert contract["status"] == b10.PASS
    assert "report_pass_without_manifest" in contract["blocked_risks"]
    result = b10.detect_simulation_risks({
        "report_has_manifest": False,
        "manifest_has_seal": True,
        "seal_hash_valid": True,
    })
    assert result["status"] == b10.BLOCK
    assert result["simulation_risk_count"] == 1


def test_no_touch_contract_requires_unchanged_fingerprints():
    before = {"00_SYSTEM/brain": "abc", "n8n": "missing"}
    after = {"00_SYSTEM/brain": "abc", "n8n": "missing"}
    assert b10.build_no_touch_contract()["status"] == b10.PASS
    assert b10.evaluate_no_touch(before, after)["status"] == b10.PASS
    changed = {"00_SYSTEM/brain": "changed", "n8n": "missing"}
    assert b10.evaluate_no_touch(before, changed)["status"] == b10.BLOCK


def test_validation_domains_gates_items_meet_minimums():
    assert len(b10.build_validation_domains()) >= 22
    assert len(b10.build_validation_gates()) >= 40
    assert len(b10.build_validation_items()) >= 60


def test_negative_and_failure_injection_minimums():
    items = b10.build_validation_items()
    negatives = [item for item in items if item["mode"] == "NEGATIVE"]
    failures = [item for item in items if item["mode"] == "FAILURE_INJECTION"]
    assert len(negatives) >= 18
    assert len(failures) >= 15
    assert all(item["expected"] == "LOCK_OR_BLOCK" for item in negatives + failures)


def test_validate_block10_contracts_passes():
    validation = b10.validate_block10_contracts()
    assert validation["status"] == b10.PASS
    assert validation["domain_count"] >= 22
    assert validation["gate_count"] >= 40
    assert validation["validation_item_count"] >= 60
    assert validation["negative_check_count"] >= 18
    assert validation["failure_injection_check_count"] >= 15


def test_report_payloads_are_complete_and_safe():
    payloads = b10.build_block10_report_payloads(
        git_context={"head_short": "x", "head_subject": "Close MANUAL-CEREBRO bridge block 9 test harness 40 pruebas"},
        chain_discovery={"status": b10.PASS, "missing_real_count": 0, "blocks": {}},
        git_audit={"status": b10.PASS, "commit_chain": {}, "push_sync": {}},
        evidence_integrity={"status": b10.PASS},
        no_touch_audit={"status": b10.PASS, "changed_roots": {}},
        anti_simulation_audit={"status": b10.PASS, "simulation_risk_count": 0},
    )
    expected = {
        "BRIDGE_BLOCK_10_BUILD_REPORT.json",
        "BRIDGE_BLOCK_10_CHAIN_VALIDATION_MAP.json",
        "BRIDGE_BLOCK_10_COMMIT_AUDIT_MAP.json",
        "BRIDGE_BLOCK_10_PUSH_SYNC_AUDIT_MAP.json",
        "BRIDGE_BLOCK_10_EVIDENCE_INTEGRITY_MAP.json",
        "BRIDGE_BLOCK_10_CHAIN_EVIDENCE_DISCOVERY_REPORT.json",
        "BRIDGE_BLOCK_10_GIT_CHAIN_AND_SYNC_AUDIT.json",
        "BRIDGE_BLOCK_10_FAILURE_RECOVERY_POLICY.json",
        "BRIDGE_BLOCK_10_ANTI_SIMULATION_AUDIT.json",
        "BRIDGE_BLOCK_10_NO_TOUCH_FINGERPRINT_AUDIT.json",
        "BRIDGE_BLOCK_10_PERMISSION_BOUNDARY_MAP.json",
        "BRIDGE_BLOCK_10_STATE_MATRIX.json",
        "BRIDGE_BLOCK_10_FINAL_READINESS_MAP.json",
        "MANUAL_CEREBRO_BRIDGE_FINAL_READINESS_MAP.json",
    }
    assert set(payloads) == expected
    for payload in payloads.values():
        assert payload["status"] == "BUILT_PENDING_POST_AUDIT"
        assert payload["result"] == b10.PASS
        assert payload["fixed_issue"] == "TARGETED_PYTEST_COUNT_TOO_LOW"
        assert payload["previous_issue_fixed"] == "PYTEST_RUNTIME_ENV_MISSING"
        assert payload["next_safe_step"] == "BLOQUE_10_POST_BUILD_AUDIT"
        assert payload["permissions"]["bloque_10_post_build_audit_allowed_next"] is True
        assert payload["permissions"]["execution_allowed_now"] is False
        assert payload["permissions"]["brain_write_allowed_now"] is False


def test_dual_readiness_does_not_close_bridge_during_build():
    payloads = b10.build_block10_report_payloads(
        git_context={},
        chain_discovery={"status": b10.PASS, "missing_real_count": 0, "blocks": {}},
        git_audit={"status": b10.PASS, "commit_chain": {}, "push_sync": {}},
        evidence_integrity={"status": b10.PASS},
        no_touch_audit={"status": b10.PASS, "changed_roots": {}},
        anti_simulation_audit={"status": b10.PASS, "simulation_risk_count": 0},
    )
    block_ready = payloads["BRIDGE_BLOCK_10_FINAL_READINESS_MAP.json"]["readiness"]
    bridge_ready = payloads["MANUAL_CEREBRO_BRIDGE_FINAL_READINESS_MAP.json"]["readiness"]
    assert block_ready["bloque_10_status"] == "BUILT_PENDING_POST_AUDIT"
    assert bridge_ready["manual_cerebro_bridge_status"] == "NOT_CLOSED_YET"
    assert bridge_ready["content_engine_build_allowed_now"] is False


def test_canonical_json_is_deterministic_and_sorted():
    left = b10.canonical_json({"b": 2, "a": 1})
    right = b10.canonical_json({"a": 1, "b": 2})
    assert left == right
    assert left.endswith("\n")
    assert '"a": 1' in left


def test_sha256_text_is_deterministic_and_changes_with_input():
    one = b10.sha256_text("block10")
    two = b10.sha256_text("block10")
    three = b10.sha256_text("block10-x")
    assert one == two
    assert one != three
    assert len(one) == 64


def test_missing_real_is_explicitly_blocked_for_every_block_class():
    for block_number in range(1, 10):
        result = b10.evaluate_evidence_resolution(block_number, "MISSING_REAL")
        assert result["status"] == b10.BLOCK
        assert result["reason"] == "MISSING_REAL"


def test_unknown_block_is_blocked_even_with_direct_artifacts():
    result = b10.evaluate_evidence_resolution(99, "DIRECT_ARTIFACTS")
    assert result["status"] == b10.BLOCK
    assert result["reason"] == "UNKNOWN_BLOCK"


def test_content_engine_construction_stays_blocked_during_build_readiness():
    payloads = b10.build_block10_report_payloads(
        git_context={},
        chain_discovery={"status": b10.PASS, "missing_real_count": 0, "blocks": {}},
        git_audit={"status": b10.PASS, "commit_chain": {}, "push_sync": {}},
        evidence_integrity={"status": b10.PASS},
        no_touch_audit={"status": b10.PASS, "changed_roots": {}},
        anti_simulation_audit={"status": b10.PASS, "simulation_risk_count": 0},
    )
    readiness = payloads["MANUAL_CEREBRO_BRIDGE_FINAL_READINESS_MAP.json"]["readiness"]
    assert readiness["content_engine_operational_construction_blueprint_allowed_next"] is False
    assert readiness["content_engine_build_allowed_now"] is False
    assert readiness["execution_allowed_now"] is False


def test_failure_policy_never_allows_commit_or_push_on_core_failures():
    rules = b10.build_failure_recovery_policy()["rules"]
    for name in ["dirty_out_of_scope", "remote_divergence", "hash_mismatch", "artifact_missing"]:
        assert rules[name]["commit"] is False
        assert rules[name]["push"] is False
