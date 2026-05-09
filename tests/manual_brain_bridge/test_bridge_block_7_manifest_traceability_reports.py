from __future__ import annotations

import json
from pathlib import Path

import pytest

from manual_brain_bridge import bridge_block_7_manifest_traceability_reports as b7


VALID_SHA = "a" * 64
OTHER_SHA = "b" * 64


def permissions():
    return {
        "post_build_audit_allowed_next": True,
        "validation_map_allowed_now": False,
        "validation_allowed_now": False,
        "gate_closure_allowed_now": False,
        "bloque_8_blueprint_allowed_now": False,
        "execution_allowed_now": False,
        "manual_write_allowed_now": False,
        "brain_write_allowed_now": False,
        "reports_brain_write_allowed_now": False,
        "n8n_allowed_now": False,
        "webhook_allowed_now": False,
        "publishing_allowed_now": False,
        "capa9_allowed_now": False,
    }


def artifact(path="00_SYSTEM/bridge/reports/a.json", sha=VALID_SHA, artifact_type="technical_report_json"):
    return b7.make_artifact_record(
        artifact_id="a1",
        artifact_path=path,
        artifact_type=artifact_type,
        block_owner="BLOQUE_7_MANIFEST_TRACEABILITY_REPORTS",
        lifecycle_gate="BUILD",
        sha256=sha,
        status="BUILT_PENDING_POST_AUDIT",
        result=b7.PASS,
        generated_by_commit_short="3ef85e4",
        generated_by_commit_subject="Close MANUAL-CEREBRO bridge block 6 decision mapper controlled plan builder",
        consumed_by_gate="BLOQUE_7_POST_BUILD_AUDIT",
        is_human_readable=False,
        is_machine_readable=True,
        created_by_current_block=True,
    )


def manifest(artifacts=None, perms=None, next_step="BLOQUE_7_POST_BUILD_AUDIT"):
    return b7.make_manifest_contract(
        project="CONTENT_ENGINE_OMEGA",
        subsystem="MANUAL_CEREBRO_BRIDGE",
        block="BLOQUE_7_MANIFEST_TRACEABILITY_REPORTS",
        gate="BUILD",
        status="BUILT_PENDING_POST_AUDIT",
        result=b7.PASS,
        consumed_commit_short="3ef85e4",
        consumed_commit_subject="Close MANUAL-CEREBRO bridge block 6 decision mapper controlled plan builder",
        produced_artifacts=artifacts if artifacts is not None else [artifact()],
        permissions=perms if perms is not None else permissions(),
        next_safe_step=next_step,
        blocked_actions=sorted(b7.BLOCKED_ACTIONS_REQUIRED),
    )


def node(node_id="B07-build", block_id="BLOQUE_7", gate="BUILD", next_step="BLOQUE_7_POST_BUILD_AUDIT", status="BUILT_PENDING_POST_AUDIT"):
    return b7.make_traceability_node(
        node_id=node_id,
        block_id=block_id,
        block_name="Manifest + traceability + reports",
        gate=gate,
        commit_short="3ef85e4",
        commit_subject="Close MANUAL-CEREBRO bridge block 6 decision mapper controlled plan builder",
        status=status,
        result=b7.PASS,
        consumed_evidence=["x"],
        produced_evidence=["y"],
        next_safe_step=next_step,
        blocked_actions=sorted(b7.BLOCKED_ACTIONS_REQUIRED),
        permissions_digest=b7.sha256_text(b7.canonical_json(permissions())),
    )


def test_canonical_json_is_stable():
    assert b7.canonical_json({"b": 1, "a": 2}).splitlines()[1].strip().startswith('"a"')


def test_sha256_text_is_valid():
    assert b7.is_valid_sha256(b7.sha256_text("abc"))


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("a\\b\\c", "a/b/c"),
        ("./a/b", "a/b"),
        ("a//b", "a/b"),
        (Path("a") / "b", "a/b"),
        ("00_SYSTEM\\bridge\\reports\\x.json", "00_SYSTEM/bridge/reports/x.json"),
        ("./00_SYSTEM//bridge\\reports/x.json", "00_SYSTEM/bridge/reports/x.json"),
    ],
)
def test_normalize_path(raw, expected):
    assert b7.normalize_path(raw) == expected


@pytest.mark.parametrize(
    "path",
    [
        "00_SYSTEM/brain/x.json",
        "00_SYSTEM/reports/brain/x.json",
        "00_SYSTEM/manual/current/x.md",
        "00_SYSTEM/manual/historical/x.md",
        "00_SYSTEM/manual/manifest/x.json",
        "00_SYSTEM/manual/registry/x.json",
        "n8n/workflow.json",
        "workflows/a.json",
        "publication/a.json",
    ],
)
def test_protected_paths_detected(path):
    assert b7.is_protected_path(path)


@pytest.mark.parametrize(
    "path",
    [
        "00_SYSTEM/bridge/reports/x.json",
        "00_SYSTEM/bridge/manifests/x.json",
        "05_REPORTS/manual_brain_bridge/x.md",
        "04_SCRIPTS/python/manual_brain_bridge/x.py",
    ],
)
def test_allowed_paths_not_protected(path):
    assert not b7.is_protected_path(path)


@pytest.mark.parametrize("value", [VALID_SHA, OTHER_SHA, "0" * 64])
def test_valid_sha256(value):
    assert b7.is_valid_sha256(value)


@pytest.mark.parametrize("value", ["", "g" * 64, "a" * 63, "A" * 64, None, 123])
def test_invalid_sha256(value):
    assert not b7.is_valid_sha256(value)


def test_valid_artifact_record_passes():
    assert b7.validate_artifact_record(artifact())["status"] == b7.PASS


@pytest.mark.parametrize("field", list(b7.ArtifactRecord.__dataclass_fields__.keys()))
def test_artifact_record_missing_fields_block(field):
    record = artifact()
    record.pop(field)
    assert b7.validate_artifact_record(record)["status"] == b7.BLOCK


def test_artifact_invalid_hash_blocks():
    record = artifact(sha="bad")
    assert b7.validate_artifact_record(record)["status"] == b7.BLOCK


def test_artifact_hash_mismatch_locks(tmp_path):
    file_path = tmp_path / "x.json"
    file_path.write_text("hello", encoding="utf-8")
    record = artifact(path="x.json", sha=OTHER_SHA)
    assert b7.validate_artifact_record(record, tmp_path)["status"] == b7.LOCK


def test_artifact_missing_blocks(tmp_path):
    record = artifact(path="missing.json")
    assert b7.validate_artifact_record(record, tmp_path)["status"] == b7.BLOCK


def test_artifact_in_protected_root_locks():
    record = artifact(path="00_SYSTEM/brain/x.json")
    assert b7.validate_artifact_record(record)["status"] == b7.LOCK


@pytest.mark.parametrize(
    "artifact_type",
    [
        "manual_current",
        "brain_state",
        "reports_brain",
        "workflow_runtime",
        "webhook_payload",
        "publishing_payload",
        "external_execution_log",
    ],
)
def test_prohibited_artifact_types_lock(artifact_type):
    assert b7.validate_artifact_record(artifact(artifact_type=artifact_type))["status"] == b7.LOCK


def test_manifest_valid_passes():
    assert b7.validate_manifest_contract(manifest())["status"] == b7.PASS


@pytest.mark.parametrize(
    "field",
    [
        "project",
        "subsystem",
        "block",
        "gate",
        "status",
        "result",
        "canonical_json",
        "hash_algorithm",
        "consumed_commit_short",
        "consumed_commit_subject",
        "produced_artifacts",
        "permissions",
        "next_safe_step",
        "blocked_actions",
    ],
)
def test_manifest_missing_fields_block(field):
    payload = manifest()
    payload.pop(field)
    assert b7.validate_manifest_contract(payload)["status"] == b7.BLOCK


def test_manifest_without_artifacts_blocks():
    payload = manifest(artifacts=[])
    assert b7.validate_manifest_contract(payload)["status"] == b7.BLOCK


def test_manifest_invalid_next_safe_step_locks():
    payload = manifest(next_step="BLOQUE_8_BUILD")
    assert b7.validate_manifest_contract(payload)["status"] == b7.LOCK


@pytest.mark.parametrize(
    "key",
    [
        "execution_allowed_now",
        "manual_write_allowed_now",
        "brain_write_allowed_now",
        "reports_brain_write_allowed_now",
        "n8n_allowed_now",
        "webhook_allowed_now",
        "publishing_allowed_now",
        "capa9_allowed_now",
        "bloque_8_blueprint_allowed_now",
    ],
)
def test_manifest_unsafe_permissions_lock(key):
    perms = permissions()
    perms[key] = True
    assert b7.validate_manifest_contract(manifest(perms=perms))["status"] == b7.LOCK


def test_manifest_unknown_permission_blocks():
    perms = permissions()
    perms["unknown_allowed_now"] = False
    assert b7.validate_manifest_contract(manifest(perms=perms))["status"] == b7.BLOCK


def test_manifest_missing_permission_blocks():
    perms = permissions()
    perms.pop("capa9_allowed_now")
    assert b7.validate_manifest_contract(manifest(perms=perms))["status"] == b7.BLOCK


def test_evidence_index_validates():
    index = b7.build_evidence_index([artifact()])
    assert b7.validate_evidence_index(index)["status"] == b7.PASS


def test_evidence_index_duplicate_same_path_same_hash_passes():
    index = b7.build_evidence_index([artifact(), artifact()])
    assert b7.validate_evidence_index(index)["status"] == b7.PASS


def test_evidence_index_duplicate_same_path_different_hash_locks():
    index = b7.build_evidence_index([artifact(), artifact(sha=OTHER_SHA)])
    assert index["status"] == b7.LOCK


def test_evidence_index_missing_entries_blocks():
    assert b7.validate_evidence_index({})["status"] == b7.BLOCK


def test_evidence_index_protected_root_locks():
    index = {"entries": [{"artifact_path": "00_SYSTEM/brain/a.json", "sha256": VALID_SHA, "integrity_status": "VERIFIED"}]}
    assert b7.validate_evidence_index(index)["status"] == b7.LOCK


@pytest.mark.parametrize(
    "integrity,status",
    [
        ("VERIFIED", b7.PASS),
        ("MISSING", b7.BLOCK),
        ("HASH_INVALID", b7.BLOCK),
        ("HASH_MISMATCH", b7.LOCK),
        ("STATUS_CONFLICT", b7.LOCK),
        ("PERMISSION_CONFLICT", b7.LOCK),
        ("OUT_OF_SCOPE", b7.BLOCK),
        ("PROTECTED_ROOT_BLOCKED", b7.LOCK),
    ],
)
def test_evidence_index_integrity_statuses(integrity, status):
    index = {"entries": [{"artifact_path": "a.json", "sha256": VALID_SHA, "integrity_status": integrity}]}
    assert b7.validate_evidence_index(index)["status"] == status


def test_traceability_node_valid_passes():
    assert b7.validate_traceability_node(node())["status"] == b7.PASS


@pytest.mark.parametrize(
    "field",
    [
        "node_id",
        "block_id",
        "block_name",
        "gate",
        "commit_short",
        "commit_subject",
        "status",
        "result",
        "consumed_evidence",
        "produced_evidence",
        "next_safe_step",
        "blocked_actions",
        "permissions_digest",
    ],
)
def test_traceability_node_missing_fields_block(field):
    payload = node()
    payload.pop(field)
    assert b7.validate_traceability_node(payload)["status"] == b7.BLOCK


def test_traceability_chain_valid_passes():
    chain = b7.build_traceability_chain([node("B06-closure", "BLOQUE_6"), node("B07-build", "BLOQUE_7")])
    assert b7.validate_traceability_chain(chain)["status"] == b7.PASS


def test_traceability_chain_missing_nodes_blocks():
    assert b7.validate_traceability_chain({"nodes": []})["status"] == b7.BLOCK


def test_traceability_chain_unsorted_nodes_blocks():
    chain = {"nodes": [node("B07-build"), node("B06-closure")]}
    assert b7.validate_traceability_chain(chain)["status"] == b7.BLOCK


def test_permission_consistency_passes():
    p = permissions()
    assert b7.validate_permission_consistency([{"permissions": p}, {"permissions": dict(p)}])["status"] == b7.PASS


def test_permission_mismatch_locks():
    p1 = permissions()
    p2 = permissions()
    p2["validation_allowed_now"] = True
    assert b7.validate_permission_consistency([{"permissions": p1}, {"permissions": p2}])["status"] == b7.LOCK


@pytest.mark.parametrize(
    "key",
    [
        "execution_allowed_now",
        "manual_write_allowed_now",
        "brain_write_allowed_now",
        "reports_brain_write_allowed_now",
        "n8n_allowed_now",
        "webhook_allowed_now",
        "publishing_allowed_now",
        "capa9_allowed_now",
        "bloque_8_blueprint_allowed_now",
    ],
)
def test_unsafe_permissions_lock(key):
    p = permissions()
    p[key] = True
    assert b7.validate_permission_consistency([{"permissions": p}])["status"] == b7.LOCK


def test_unknown_permission_blocks():
    p = permissions()
    p["new_permission"] = False
    assert b7.validate_permission_consistency([{"permissions": p}])["status"] == b7.BLOCK


def test_missing_permission_blocks():
    p = permissions()
    p.pop("post_build_audit_allowed_next")
    assert b7.validate_permission_consistency([{"permissions": p}])["status"] == b7.BLOCK


def test_source_of_truth_valid_passes():
    payloads = {
        "seal": {"status": "SEALED_BUILT_PENDING_POST_AUDIT", "next_safe_step": "BLOQUE_7_POST_BUILD_AUDIT"},
        "manifest": {"status": "BUILT_PENDING_POST_AUDIT", "next_safe_step": "BLOQUE_7_POST_BUILD_AUDIT"},
        "technical_report": {"status": "BUILT_PENDING_POST_AUDIT", "next_safe_step": "BLOQUE_7_POST_BUILD_AUDIT"},
    }
    assert b7.validate_source_of_truth_hierarchy(payloads)["status"] == b7.PASS


def test_source_of_truth_next_step_contradiction_locks():
    payloads = {
        "seal": {"status": "BUILT_PENDING_POST_AUDIT", "next_safe_step": "BLOQUE_7_POST_BUILD_AUDIT"},
        "manifest": {"status": "BUILT_PENDING_POST_AUDIT", "next_safe_step": "BLOQUE_8_BLUEPRINT"},
    }
    assert b7.validate_source_of_truth_hierarchy(payloads)["status"] == b7.LOCK


def test_source_of_truth_status_contradiction_locks():
    payloads = {
        "seal": {"status": "SEALED_CLOSED_VALIDATED", "next_safe_step": "BLOQUE_7_POST_BUILD_AUDIT"},
        "manifest": {"status": "BUILT_PENDING_POST_AUDIT", "next_safe_step": "BLOQUE_7_POST_BUILD_AUDIT"},
    }
    assert b7.validate_source_of_truth_hierarchy(payloads)["status"] == b7.LOCK


def test_cross_block_integrity_passes():
    chain = b7.build_traceability_chain([node("B06-closure", "BLOQUE_6"), node("B07-build", "BLOQUE_7")])
    assert b7.validate_cross_block_integrity(chain)["status"] == b7.PASS


def test_cross_block_bloque8_premature_locks():
    chain = {"nodes": [node("B08-build", "BLOQUE_8")]}
    assert b7.validate_cross_block_integrity(chain)["status"] == b7.LOCK


def test_cross_block_bloque8_in_blocked_actions_not_false_positive():
    safe_node = node("B07-build", "BLOQUE_7")
    safe_node["blocked_actions"] = ["BLOQUE_8_BLUEPRINT", "BLOQUE_8_BUILD"]
    chain = {"nodes": [safe_node]}
    assert b7.validate_cross_block_integrity(chain)["status"] == b7.PASS


def test_cross_block_build_without_plan_locks():
    chain = {"nodes": [node("B07-build", "BLOQUE_7_BUILD")]}
    assert b7.validate_cross_block_integrity(chain)["status"] == b7.LOCK


@pytest.mark.parametrize(
    "token",
    [
        "AtomicWriter",
        "LockManager",
        "QuarantineWriter",
        "RecoveryExecutor",
        "RollbackExecutor",
        "WriteTransaction",
        "PendingWriteSet",
        "MutationQueue",
        "FilesystemMutationPlan",
        "PatchApplier",
        "ManualWriter",
        "BrainWriter",
        "ReportsBrainWriter",
        "ManualMutation",
        "BrainMutation",
        "AtomicCommitQueue",
    ],
)
def test_block8_tokens_as_implementation_lock(token):
    payload = {"implementation": f"Create {token} now"}
    assert b7.scan_for_runtime_or_writer_intent(payload)["status"] == b7.LOCK


@pytest.mark.parametrize(
    "token",
    [
        "AtomicWriter",
        "LockManager",
        "QuarantineWriter",
        "RecoveryExecutor",
        "PatchApplier",
        "ManualWriter",
        "BrainWriter",
    ],
)
def test_block8_tokens_in_blocked_actions_pass(token):
    payload = {"blocked_actions": [token], "description": "safe description only"}
    assert b7.scan_for_runtime_or_writer_intent(payload)["status"] == b7.PASS


@pytest.mark.parametrize(
    "token",
    [
        "git commit",
        "git push",
        "powershell",
        "pwsh",
        "cmd.exe",
        "webhook",
        "publish",
        "upload",
        "manual_write",
        "brain_write",
        "reports_brain_write",
        "capa9",
        "subprocess.run",
    ],
)
def test_runtime_tokens_as_actionable_lock(token):
    payload = {"description": f"please run {token}"}
    assert b7.scan_for_runtime_or_writer_intent(payload)["status"] == b7.LOCK


def test_report_materialization_safe_passes():
    assert b7.validate_report_materialization({"description": "safe report metadata only"})["status"] == b7.PASS


def test_report_materialization_terminal_transcript_blocks():
    assert b7.validate_report_materialization({"description": "PS D:\\repo\n================ PRECHECK"})["status"] == b7.BLOCK


def test_report_materialization_executable_content_locks():
    assert b7.validate_report_materialization({"description": "git push now"})["status"] == b7.LOCK


def test_report_materialization_huge_report_blocks():
    assert b7.validate_report_materialization({"description": "\n".join(["safe"] * 4000)})["status"] == b7.BLOCK


def test_nested_report_materialization_huge_report_blocks():
    payload = {"outer": {"description": "\n".join(["safe"] * 4000)}}
    assert b7.validate_report_materialization(payload)["status"] == b7.BLOCK


def test_next_layer_readiness_valid_passes():
    payload = {
        "current_status": "BUILT_PENDING_POST_AUDIT",
        "next_safe_step": "BLOQUE_7_POST_BUILD_AUDIT",
        "post_build_audit_allowed_next": True,
        "permissions": permissions(),
    }
    assert b7.validate_next_layer_readiness(payload)["status"] == b7.PASS


def test_next_layer_readiness_wrong_step_locks():
    payload = {
        "current_status": "BUILT_PENDING_POST_AUDIT",
        "next_safe_step": "BLOQUE_8_BLUEPRINT",
        "post_build_audit_allowed_next": True,
        "permissions": permissions(),
    }
    assert b7.validate_next_layer_readiness(payload)["status"] == b7.LOCK


def test_next_layer_readiness_wrong_status_blocks():
    payload = {
        "current_status": "VALIDATED_POST_AUDITED",
        "next_safe_step": "BLOQUE_7_POST_BUILD_AUDIT",
        "post_build_audit_allowed_next": True,
        "permissions": permissions(),
    }
    assert b7.validate_next_layer_readiness(payload)["status"] == b7.BLOCK


def test_build_block7_report_payloads_returns_expected_reports(tmp_path):
    payloads = b7.build_block7_report_payloads(
        tmp_path,
        {
            "head_short": "3ef85e4",
            "head_subject": "Close MANUAL-CEREBRO bridge block 6 decision mapper controlled plan builder",
            "block6_closure_head": "3ef85e4",
        },
    )
    assert set(payloads) == {
        "BRIDGE_BLOCK_7_MANIFEST_REPORT.json",
        "BRIDGE_BLOCK_7_TRACEABILITY_CHAIN_REPORT.json",
        "BRIDGE_BLOCK_7_REPORTS_MATERIALIZATION_REPORT.json",
        "BRIDGE_BLOCK_7_EVIDENCE_INDEX_REPORT.json",
        "BRIDGE_BLOCK_7_PERMISSION_CONSISTENCY_REPORT.json",
        "BRIDGE_BLOCK_7_CROSS_BLOCK_INTEGRITY_REPORT.json",
        "BRIDGE_BLOCK_7_NEXT_LAYER_READINESS_MAP.json",
    }


@pytest.mark.parametrize(
    "report_name",
    [
        "BRIDGE_BLOCK_7_MANIFEST_REPORT.json",
        "BRIDGE_BLOCK_7_TRACEABILITY_CHAIN_REPORT.json",
        "BRIDGE_BLOCK_7_REPORTS_MATERIALIZATION_REPORT.json",
        "BRIDGE_BLOCK_7_EVIDENCE_INDEX_REPORT.json",
        "BRIDGE_BLOCK_7_PERMISSION_CONSISTENCY_REPORT.json",
        "BRIDGE_BLOCK_7_CROSS_BLOCK_INTEGRITY_REPORT.json",
        "BRIDGE_BLOCK_7_NEXT_LAYER_READINESS_MAP.json",
    ],
)
def test_block7_reports_have_safe_permissions(tmp_path, report_name):
    payloads = b7.build_block7_report_payloads(
        tmp_path,
        {
            "head_short": "3ef85e4",
            "head_subject": "Close MANUAL-CEREBRO bridge block 6 decision mapper controlled plan builder",
            "block6_closure_head": "3ef85e4",
        },
    )
    payload = payloads[report_name]
    assert payload["status"] == "BUILT_PENDING_POST_AUDIT"
    assert payload["permissions"]["post_build_audit_allowed_next"] is True
    for key, value in payload["permissions"].items():
        if key != "post_build_audit_allowed_next":
            assert value is False


def test_json_canonical_roundtrip(tmp_path):
    path = tmp_path / "x.json"
    text = b7.canonical_json({"b": 1, "a": 2})
    path.write_text(text, encoding="utf-8")
    assert path.read_text(encoding="utf-8") == b7.canonical_json(json.loads(path.read_text(encoding="utf-8")))


@pytest.mark.parametrize(
    "statuses,expected",
    [
        ([b7.PASS, b7.BLOCK, b7.LOCK], b7.LOCK),
        ([b7.PASS, b7.REVIEW, b7.BLOCK], b7.BLOCK),
        ([b7.PASS, b7.REVIEW], b7.REVIEW_REQUIRED),
        (["UNKNOWN"], b7.LOCK),
    ],
)
def test_choose_worst_status(statuses, expected):
    assert b7.choose_worst_status(statuses) == expected


@pytest.mark.parametrize("summary_line_count", [10, 100, 499])
def test_reasonable_summary_sizes_are_not_runtime_intent(summary_line_count):
    payload = {"description": "\n".join(["safe summary"] * summary_line_count)}
    assert b7.validate_report_materialization(payload)["status"] == b7.PASS


def test_safe_replace_normalization_does_not_indicate_writer_intent():
    assert b7.normalize_path("a\\b//c") == "a/b/c"


@pytest.mark.parametrize("i", range(100))
def test_many_distinct_valid_artifact_records_pass(i):
    record = artifact(path=f"00_SYSTEM/bridge/reports/generated_{i}.json")
    assert b7.validate_artifact_record(record)["status"] == b7.PASS


@pytest.mark.parametrize("i", range(40))
def test_many_valid_traceability_nodes_pass(i):
    payload = node(node_id=f"B07-node-{i:03d}")
    assert b7.validate_traceability_node(payload)["status"] == b7.PASS


@pytest.mark.parametrize("i", range(40))
def test_many_safe_report_payloads_pass(i):
    payload = {"description": f"safe report metadata only {i}"}
    assert b7.validate_report_materialization(payload)["status"] == b7.PASS
