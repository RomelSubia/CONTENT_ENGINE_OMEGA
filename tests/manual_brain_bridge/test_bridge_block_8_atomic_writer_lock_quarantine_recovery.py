from __future__ import annotations

import json
from pathlib import Path

import pytest

from manual_brain_bridge import bridge_block_8_atomic_writer_lock_quarantine_recovery as b8


VALID_SHA = "a" * 64
OTHER_SHA = "b" * 64


def permissions():
    return {
        "post_build_audit_allowed_next": True,
        "validation_map_allowed_now": False,
        "validation_plan_allowed_now": False,
        "validation_allowed_now": False,
        "gate_closure_allowed_now": False,
        "bloque_9_allowed_now": False,
        "manual_write_allowed_now": False,
        "brain_write_allowed_now": False,
        "reports_brain_write_allowed_now": False,
        "execution_allowed_now": False,
        "n8n_allowed_now": False,
        "webhook_allowed_now": False,
        "publishing_allowed_now": False,
        "capa9_allowed_now": False,
        "rollback_execution_allowed": False,
    }


def valid_tx(outputs=None):
    return b8.build_atomic_write_transaction(
        "B8-TX-001",
        "ATOMIC_WRITE",
        "1ba759a",
        "BLOQUE_8",
        outputs or ["00_SYSTEM/bridge/reports/x.json"],
        permissions(),
    )


def staged(path="stage/x.json", dest="00_SYSTEM/bridge/reports/x.json", sha=VALID_SHA, size=10):
    return {
        "staged_path": path,
        "destination_path": dest,
        "sha256": sha,
        "size_bytes": size,
        "canonical_json": True,
    }


def destination(path="00_SYSTEM/bridge/reports/x.json", allowlist=None):
    allowlist = allowlist or [path]
    return b8.canonicalize_destination_path(path, ".", allowlist)["record"]


def test_canonical_json_and_hash_are_stable():
    text = b8.canonical_json({"b": 1, "a": 2})
    assert '"a"' in text.splitlines()[1]
    assert b8.is_valid_sha256(b8.sha256_text(text))
    assert b8.is_valid_sha256(b8.sha256_bytes(b"x"))


@pytest.mark.parametrize("raw,expected", [
    ("a\\b\\c", "a/b/c"),
    ("./a/b", "a/b"),
    ("a//b", "a/b"),
    (Path("a") / "b", "a/b"),
])
def test_normalize_path(raw, expected):
    assert b8.normalize_path(raw) == expected


@pytest.mark.parametrize("status_list,expected", [
    ([b8.PASS, b8.BLOCK], b8.BLOCK),
    ([b8.PASS, b8.LOCK], b8.LOCK),
    ([b8.REVIEW], b8.REVIEW_REQUIRED),
    (["UNKNOWN"], b8.LOCK),
])
def test_choose_worst_status(status_list, expected):
    assert b8.choose_worst_status(status_list) == expected


def test_valid_transaction_passes():
    assert b8.validate_atomic_write_transaction(valid_tx())["status"] == b8.PASS


@pytest.mark.parametrize("field", ["transaction_id", "operation_type", "repo_head", "planned_outputs"])
def test_transaction_required_fields_block(field):
    tx = valid_tx()
    tx[field] = "" if field != "planned_outputs" else []
    assert b8.validate_atomic_write_transaction(tx)["status"] == b8.BLOCK


@pytest.mark.parametrize("key", [
    "manual_write_allowed_now",
    "brain_write_allowed_now",
    "reports_brain_write_allowed_now",
    "execution_allowed_now",
    "n8n_allowed_now",
    "webhook_allowed_now",
    "publishing_allowed_now",
    "capa9_allowed_now",
    "bloque_9_allowed_now",
    "rollback_execution_allowed",
])
def test_transaction_unsafe_permissions_lock(key):
    tx = valid_tx()
    tx["permissions"][key] = True
    assert b8.validate_atomic_write_transaction(tx)["status"] == b8.LOCK


def test_transaction_unknown_operation_blocks():
    tx = valid_tx()
    tx["operation_type"] = "WRITE_FREELY"
    assert b8.validate_atomic_write_transaction(tx)["status"] == b8.BLOCK


def test_limits_valid_pass():
    limits = b8.build_transaction_limit_contract()
    result = b8.validate_transaction_limits(limits, ["a"], {"a": 1})
    assert result["status"] == b8.PASS


def test_limits_missing_lock():
    assert b8.validate_transaction_limits(None)["status"] == b8.LOCK


@pytest.mark.parametrize("count", [51, 60, 100])
def test_limits_too_many_outputs_block(count):
    limits = b8.build_transaction_limit_contract(max_planned_outputs=50)
    outputs = [f"00_SYSTEM/bridge/reports/{i}.json" for i in range(count)]
    assert b8.validate_transaction_limits(limits, outputs, {})["status"] == b8.BLOCK


@pytest.mark.parametrize("size", [1048577, 2000000, 9999999])
def test_limits_single_artifact_too_large_blocks(size):
    limits = b8.build_transaction_limit_contract(max_single_artifact_bytes=1048576)
    assert b8.validate_transaction_limits(limits, ["a"], {"a": size})["status"] == b8.BLOCK


def test_limits_total_bytes_too_large_blocks():
    limits = b8.build_transaction_limit_contract(max_total_transaction_bytes=100)
    assert b8.validate_transaction_limits(limits, ["a", "b"], {"a": 60, "b": 60})["status"] == b8.BLOCK


def test_limits_lock_ttl_invalid_blocks():
    limits = b8.build_transaction_limit_contract(max_lock_ttl_minutes=0)
    assert b8.validate_transaction_limits(limits, [], {})["status"] == b8.BLOCK


@pytest.mark.parametrize("protected", [
    "00_SYSTEM/brain/x.json",
    "00_SYSTEM/brain/nested/x.json",
    "00_SYSTEM/reports/brain/x.json",
    "00_SYSTEM/manual/current/a.md",
    "00_SYSTEM/manual/historical/a.md",
    "00_SYSTEM/manual/manifest/a.json",
    "00_SYSTEM/manual/registry/a.json",
    "n8n/workflow.json",
    "workflows/a.json",
    "publication/a.json",
])
def test_protected_paths_detected(protected):
    assert b8.is_protected_path(protected)


@pytest.mark.parametrize("safe", [
    "00_SYSTEM/bridge/reports/a.json",
    "00_SYSTEM/bridge/manifests/a.json",
    "05_REPORTS/manual_brain_bridge/a.md",
    "04_SCRIPTS/python/manual_brain_bridge/a.py",
])
def test_safe_paths_not_protected(safe):
    assert not b8.is_protected_path(safe)


def test_path_boundary_valid_passes():
    record = destination()
    assert b8.validate_path_boundary(record)["status"] == b8.PASS


@pytest.mark.parametrize("path", [
    "00_SYSTEM/manual/current/x.md",
    "00_SYSTEM/brain/x.json",
    "00_SYSTEM/reports/brain/x.json",
    "n8n/x.json",
    "workflows/x.json",
    "publication/x.json",
])
def test_path_boundary_protected_locks(path):
    record = b8.canonicalize_destination_path(path, ".", [path])["record"]
    assert b8.validate_path_boundary(record)["status"] == b8.LOCK


@pytest.mark.parametrize("path", [
    "../escape.json",
    "../../escape.json",
    "00_SYSTEM/bridge/../brain/x.json",
])
def test_path_traversal_locks(path):
    result = b8.canonicalize_destination_path(path, ".", [path])
    assert result["validation"]["status"] == b8.LOCK


def test_path_not_in_allowlist_blocks():
    record = b8.canonicalize_destination_path("00_SYSTEM/bridge/reports/x.json", ".", ["00_SYSTEM/bridge/reports/y.json"])["record"]
    assert b8.validate_path_boundary(record)["status"] == b8.BLOCK


def test_output_allowlist_exact_match_passes():
    outputs = ["a", "b"]
    assert b8.validate_output_allowlist(outputs, outputs)["status"] == b8.PASS


def test_output_allowlist_unexpected_locks():
    assert b8.validate_output_allowlist(["a", "b"], ["a"])["status"] == b8.LOCK


def test_output_allowlist_missing_blocks():
    assert b8.validate_output_allowlist(["a"], ["a", "b"])["status"] == b8.BLOCK


def test_lock_valid_passes():
    tx = valid_tx()
    lock = b8.build_lock_contract("L1", "B8-TX-001", "1ba759a", tx["allowlist_digest"])
    assert b8.validate_lock_contract(lock, "1ba759a", tx["allowlist_digest"])["status"] == b8.PASS


@pytest.mark.parametrize("status", ["LOCK_ACTIVE", "LOCK_CORRUPT"])
def test_active_or_corrupt_lock_locks(status):
    tx = valid_tx()
    lock = b8.build_lock_contract("L1", "B8-TX-001", "1ba759a", tx["allowlist_digest"], status=status)
    assert b8.validate_lock_contract(lock, "1ba759a", tx["allowlist_digest"])["status"] == b8.LOCK


def test_lock_head_mismatch_locks():
    tx = valid_tx()
    lock = b8.build_lock_contract("L1", "B8-TX-001", "badhead", tx["allowlist_digest"])
    assert b8.validate_lock_contract(lock, "1ba759a", tx["allowlist_digest"])["status"] == b8.LOCK


def test_lock_scope_mismatch_locks():
    tx = valid_tx()
    lock = b8.build_lock_contract("L1", "B8-TX-001", "1ba759a", "bad")
    assert b8.validate_lock_contract(lock, "1ba759a", tx["allowlist_digest"])["status"] == b8.LOCK


def test_stale_lock_requires_audit():
    lock = b8.build_lock_contract("L1", "B8-TX-001", "1ba759a", "scope", status="LOCK_STALE")
    assert b8.classify_stale_lock(lock, audit_passed=False)["status"] == b8.LOCK
    assert b8.classify_stale_lock(lock, audit_passed=True)["status"] == b8.PASS


@pytest.mark.parametrize("failure_point,recovery_class", sorted(b8.FAILURE_POINT_CLASS.items()))
def test_failure_points_classify(failure_point, recovery_class):
    result = b8.classify_failure_point(failure_point)
    assert result["status"] == b8.PASS
    assert result["recovery_class"] == recovery_class


def test_unknown_failure_point_locks():
    assert b8.classify_failure_point("UNKNOWN")["status"] == b8.LOCK


def test_failure_point_matrix_validates():
    assert b8.validate_failure_point_matrix(b8.build_failure_point_matrix())["status"] == b8.PASS


def test_failure_point_matrix_missing_key_locks():
    matrix = b8.build_failure_point_matrix()
    matrix.pop("FAILPOINT_12_UNKNOWN_STATE")
    assert b8.validate_failure_point_matrix(matrix)["status"] == b8.LOCK


def test_staging_manifest_valid_passes():
    manifest = b8.build_staging_manifest("B8-TX-001", ["00_SYSTEM/bridge/reports/x.json"], [staged()])
    assert b8.validate_staging_manifest(manifest)["status"] == b8.PASS


def test_staging_missing_output_blocks():
    manifest = b8.build_staging_manifest("B8-TX-001", ["a", "b"], [staged(dest="a")])
    assert b8.validate_staging_manifest(manifest)["status"] == b8.BLOCK


def test_staging_unplanned_output_locks():
    manifest = b8.build_staging_manifest("B8-TX-001", ["a"], [staged(dest="a"), staged(dest="b")])
    assert b8.validate_staging_manifest(manifest)["status"] == b8.LOCK


def test_staging_bad_hash_locks():
    manifest = b8.build_staging_manifest("B8-TX-001", ["a"], [staged(dest="a", sha="bad")])
    assert b8.validate_staging_manifest(manifest)["status"] == b8.LOCK


def test_privileged_promotion_scope_valid_passes():
    req = b8.build_privileged_promotion_request(staged(), destination())
    assert b8.validate_privileged_promotion_scope(req)["status"] == b8.PASS


def test_privileged_promotion_raw_wrong_helper_locks():
    req = b8.build_privileged_promotion_request(staged(), destination())
    req["helper"] = "unsafe_helper"
    assert b8.validate_privileged_promotion_scope(req)["status"] == b8.LOCK


def test_privileged_promotion_protected_root_locks():
    dest = b8.canonicalize_destination_path("00_SYSTEM/brain/x.json", ".", ["00_SYSTEM/brain/x.json"])["record"]
    req = b8.build_privileged_promotion_request(staged(dest="00_SYSTEM/brain/x.json"), dest)
    assert b8.validate_privileged_promotion_scope(req)["status"] == b8.LOCK


def test_privileged_promotion_bad_hash_locks():
    req = b8.build_privileged_promotion_request(staged(sha="bad"), destination())
    assert b8.validate_privileged_promotion_scope(req)["status"] == b8.LOCK


def test_privileged_promote_staged_output_happy_path(tmp_path):
    source = tmp_path / "stage.json"
    dest_path = tmp_path / "dest.json"
    source.write_bytes(b"hello")
    sha = b8.sha256_bytes(b"hello")
    st = staged(path=str(source), dest=str(dest_path), sha=sha, size=5)
    dest = {
        "original_path": str(dest_path),
        "canonical_path": str(dest_path),
        "allowlist_digest": VALID_SHA,
        "protected_root": False,
        "root_escape": False,
        "in_allowlist": True,
    }
    result = b8.privileged_promote_staged_output(st, dest)
    assert result["status"] == b8.PASS
    assert dest_path.exists()


def test_promotion_manifest_valid_passes():
    manifest = b8.build_promotion_manifest("B8-TX-001", ["a"], {"a": None}, {"a": VALID_SHA}, {"a": b8.PASS})
    assert b8.validate_promotion_manifest(manifest)["status"] == b8.PASS


def test_promotion_manifest_bad_result_locks():
    manifest = b8.build_promotion_manifest("B8-TX-001", ["a"], {"a": None}, {"a": VALID_SHA}, {"a": b8.LOCK})
    assert b8.validate_promotion_manifest(manifest)["status"] == b8.LOCK


def test_promotion_manifest_bad_hash_locks():
    manifest = b8.build_promotion_manifest("B8-TX-001", ["a"], {"a": None}, {"a": "bad"}, {"a": b8.PASS})
    assert b8.validate_promotion_manifest(manifest)["status"] == b8.LOCK


def test_quarantine_valid_passes():
    q = b8.build_quarantine_contract("Q1", "B8-TX-001", "HASH_MISMATCH", ["00_SYSTEM/bridge/q/x"], {"x": VALID_SHA}, True, False)
    assert b8.validate_quarantine_contract(q)["status"] == b8.PASS


@pytest.mark.parametrize("missing", ["quarantine_id", "transaction_id", "reason"])
def test_quarantine_missing_required_blocks(missing):
    q = b8.build_quarantine_contract("Q1", "B8-TX-001", "HASH_MISMATCH", [], {}, True, False)
    q[missing] = ""
    assert b8.validate_quarantine_contract(q)["status"] == b8.BLOCK


def test_quarantine_auto_recover_dangerous_locks():
    q = b8.build_quarantine_contract("Q1", "B8-TX-001", "PARTIAL_PROMOTION", [], {}, True, True)
    assert b8.validate_quarantine_contract(q)["status"] == b8.LOCK


def test_quarantine_manual_review_false_locks():
    q = b8.build_quarantine_contract("Q1", "B8-TX-001", "PARTIAL_PROMOTION", [], {}, False, False)
    assert b8.validate_quarantine_contract(q)["status"] == b8.LOCK


def test_recovery_manifest_valid_for_partial_promotion_passes():
    draft = b8.build_rollback_draft("B8-TX-001", [{"operation": "candidate"}])
    r = b8.build_recovery_manifest("R1", "B8-TX-001", "FAILPOINT_07_PROMOTION_PARTIAL", [], ["a"], [], draft)
    assert b8.validate_recovery_manifest(r)["status"] == b8.PASS
    assert r["manual_review_required"] is True
    assert r["auto_recovery_allowed"] is False


def test_recovery_unknown_failure_point_locks():
    r = b8.build_recovery_manifest("R1", "B8-TX-001", "UNKNOWN", [], [], [], {})
    assert b8.validate_recovery_manifest(r)["status"] == b8.LOCK


def test_recovery_class_b_allows_auto_retry():
    r = b8.build_recovery_manifest("R1", "B8-TX-001", "FAILPOINT_03_STAGING_CREATED_NO_OUTPUTS", [], [], [], {})
    assert r["auto_recovery_allowed"] is True


def test_rollback_draft_only_passes():
    draft = b8.build_rollback_draft("B8-TX-001", [{"operation": "restore candidate only"}])
    assert b8.validate_rollback_draft_only(draft)["status"] == b8.PASS


@pytest.mark.parametrize("bad", ["git reset --hard", "delete file", "manual restore", "brain restore"])
def test_rollback_destructive_content_locks(bad):
    draft = b8.build_rollback_draft("B8-TX-001", [{"operation": bad}])
    assert b8.validate_rollback_draft_only(draft)["status"] == b8.LOCK


def test_rollback_execution_requested_locks():
    draft = b8.build_rollback_draft("B8-TX-001", [], execution_requested=True)
    assert b8.validate_rollback_draft_only(draft)["status"] == b8.LOCK


def test_no_plan_reinterpretation_passes():
    tx = valid_tx()
    assert b8.validate_no_plan_reinterpretation(tx, dict(tx))["status"] == b8.PASS


@pytest.mark.parametrize("mutation", ["planned_outputs", "permissions", "allowlist_digest"])
def test_no_plan_reinterpretation_mutation_locks(mutation):
    tx = valid_tx()
    final = dict(tx)
    final[mutation] = "changed"
    assert b8.validate_no_plan_reinterpretation(tx, final)["status"] == b8.LOCK


def test_no_plan_reinterpretation_allowlist_expansion_locks():
    tx = valid_tx()
    final = dict(tx)
    final["allowlist_expanded"] = True
    assert b8.validate_no_plan_reinterpretation(tx, final)["status"] == b8.LOCK


def test_no_plan_reinterpretation_permission_inference_locks():
    tx = valid_tx()
    final = dict(tx)
    final["permission_inferred"] = True
    assert b8.validate_no_plan_reinterpretation(tx, final)["status"] == b8.LOCK


def test_post_write_audit_valid_passes():
    audit = b8.build_post_write_audit("B8-TX-001", b8.PASS, b8.PASS, b8.PASS, b8.PASS, b8.PASS, b8.PASS, "BLOQUE_8_POST_BUILD_AUDIT")
    assert b8.validate_post_write_audit(audit)["status"] == b8.PASS


@pytest.mark.parametrize("field", ["output_scope_result", "hash_verification_result", "no_touch_result", "lock_release_result", "tmp_residue_result", "repo_status_result"])
def test_post_write_audit_lock_results_lock(field):
    audit = b8.build_post_write_audit("B8-TX-001", b8.PASS, b8.PASS, b8.PASS, b8.PASS, b8.PASS, b8.PASS, "BLOQUE_8_POST_BUILD_AUDIT")
    audit[field] = b8.LOCK
    assert b8.validate_post_write_audit(audit)["status"] == b8.LOCK


def test_post_write_audit_wrong_next_step_locks():
    audit = b8.build_post_write_audit("B8-TX-001", b8.PASS, b8.PASS, b8.PASS, b8.PASS, b8.PASS, b8.PASS, "BLOQUE_9")
    assert b8.validate_post_write_audit(audit)["status"] == b8.LOCK


def test_build_report_payloads_have_expected_reports():
    payloads = b8.build_block8_report_payloads("1ba759a", "Close MANUAL-CEREBRO bridge block 7 manifest traceability reports")
    assert set(payloads) == {
        "BRIDGE_BLOCK_8_BUILD_REPORT.json",
        "BRIDGE_BLOCK_8_TRANSACTION_CONTRACT_REPORT.json",
        "BRIDGE_BLOCK_8_PATH_BOUNDARY_REPORT.json",
        "BRIDGE_BLOCK_8_LOCK_AND_STALE_LOCK_REPORT.json",
        "BRIDGE_BLOCK_8_STAGING_PROMOTION_REPORT.json",
        "BRIDGE_BLOCK_8_QUARANTINE_RECOVERY_REPORT.json",
        "BRIDGE_BLOCK_8_PERMISSION_AND_LIMITS_REPORT.json",
        "BRIDGE_BLOCK_8_NEXT_LAYER_READINESS_MAP.json",
    }


@pytest.mark.parametrize("name", [
    "BRIDGE_BLOCK_8_BUILD_REPORT.json",
    "BRIDGE_BLOCK_8_TRANSACTION_CONTRACT_REPORT.json",
    "BRIDGE_BLOCK_8_PATH_BOUNDARY_REPORT.json",
    "BRIDGE_BLOCK_8_LOCK_AND_STALE_LOCK_REPORT.json",
    "BRIDGE_BLOCK_8_STAGING_PROMOTION_REPORT.json",
    "BRIDGE_BLOCK_8_QUARANTINE_RECOVERY_REPORT.json",
    "BRIDGE_BLOCK_8_PERMISSION_AND_LIMITS_REPORT.json",
    "BRIDGE_BLOCK_8_NEXT_LAYER_READINESS_MAP.json",
])
def test_build_report_payload_permissions_safe(name):
    payload = b8.build_block8_report_payloads("1ba759a", "Close MANUAL-CEREBRO bridge block 7 manifest traceability reports")[name]
    assert payload["status"] == "BUILT_PENDING_POST_AUDIT"
    assert payload["next_safe_step"] == "BLOQUE_8_POST_BUILD_AUDIT"
    assert payload["permissions"]["post_build_audit_allowed_next"] is True
    for key, value in payload["permissions"].items():
        if key != "post_build_audit_allowed_next":
            assert value is False


@pytest.mark.parametrize("i", range(60))
def test_many_valid_transactions_pass(i):
    tx = b8.build_atomic_write_transaction(f"B8-TX-{i:03d}", "ATOMIC_WRITE", "1ba759a", "BLOQUE_8", [f"00_SYSTEM/bridge/reports/{i}.json"], permissions())
    assert b8.validate_atomic_write_transaction(tx)["status"] == b8.PASS


@pytest.mark.parametrize("i", range(50))
def test_many_valid_limit_cases_pass(i):
    limits = b8.build_transaction_limit_contract(max_planned_outputs=100)
    outputs = [f"00_SYSTEM/bridge/reports/{i}.json"]
    assert b8.validate_transaction_limits(limits, outputs, {outputs[0]: i})["status"] == b8.PASS


@pytest.mark.parametrize("i", range(50))
def test_many_valid_locks_pass(i):
    tx = valid_tx([f"00_SYSTEM/bridge/reports/{i}.json"])
    lock = b8.build_lock_contract(f"L{i}", tx["transaction_id"], "1ba759a", tx["allowlist_digest"])
    assert b8.validate_lock_contract(lock, "1ba759a", tx["allowlist_digest"])["status"] == b8.PASS


@pytest.mark.parametrize("i", range(50))
def test_many_safe_path_records_pass(i):
    path = f"00_SYSTEM/bridge/reports/safe_{i}.json"
    record = b8.canonicalize_destination_path(path, ".", [path])["record"]
    assert b8.validate_path_boundary(record)["status"] == b8.PASS


def test_build_fix_1_1_raw_parent_traversal_locked():
    for path in ["../escape.json", "../../escape.json", "00_SYSTEM/bridge/../brain/x.json"]:
        result = b8.canonicalize_destination_path(path, ".", [path])
        assert result["validation"]["status"] == b8.LOCK
        assert any(
            finding in result["validation"]["findings"]
            for finding in ["PATH_TRAVERSAL", "PATH_ESCAPES_ROOT"]
        )


def test_build_fix_1_1_dot_segments_locked_in_destination_canonicalization():
    for path in ["./escape.json", "././escape.json", "00_SYSTEM/bridge/./brain/x.json"]:
        result = b8.canonicalize_destination_path(path, ".", [path])
        assert result["validation"]["status"] == b8.LOCK
        assert "PATH_DOT_SEGMENT" in result["validation"]["findings"]


def test_build_fix_1_1_absolute_unc_or_drive_paths_lock():
    for path in ["/tmp/escape.json", "//server/share/file.json", "C:/Windows/system32/file.txt"]:
        result = b8.canonicalize_destination_path(path, ".", [path])
        assert result["validation"]["status"] == b8.LOCK


def test_build_fix_1_1_normalize_path_no_longer_strips_parent_segments():
    assert b8.normalize_path("../escape.json").startswith("..")
    assert b8.normalize_path("../../escape.json").startswith("../..")
