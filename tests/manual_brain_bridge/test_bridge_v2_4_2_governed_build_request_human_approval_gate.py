from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BRIDGE_PATH = ROOT / "04_SCRIPTS/python/manual_brain_bridge/bridge_v2_4_2_governed_build_request_human_approval_gate.py"

spec = importlib.util.spec_from_file_location("bridge_v2_4_2", BRIDGE_PATH)
bridge = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(bridge)


def j(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_v2_4_generated_reports_exist():
    for rel in [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_REPO_IDENTITY_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_ARGOS_CONTAMINATION_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_AUTHORITY_BINDING_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_SCOPE_BINDING_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_BUILD_REQUEST_CONTRACT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_APPROVAL_EXPIRATION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_ANTI_REPLAY_APPROVAL_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_BLOCKED_CAPABILITIES_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_ANTI_SIMULATION_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_4_ARTIFACT_MANIFEST.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_SEAL.json",
    ]:
        assert (ROOT / rel).is_file(), rel


def test_v2_4_repo_identity_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_4_REPO_IDENTITY_REPORT.json")
    assert report["status"] == "PASS"
    assert report["repo_identity_valid"] is True
    assert report["root_valid"] is True
    assert report["branch_valid"] is True
    assert report["remote_valid"] is True
    assert report["argos_remote_detected"] is False
    assert report["argos_path_detected"] is False


def test_v2_4_repo_identity_locks_wrong_remote(tmp_path: Path):
    report = bridge.build_repo_identity_report(
        tmp_path / "CONTENT_ENGINE_OMEGA",
        head="abc",
        branch="main",
        remote="https://github.com/RomelSubia/" + "ARGOS.git",
        upstream="abc",
    )
    assert report["status"] == "LOCK"
    assert report["repo_identity_valid"] is False
    assert report["argos_remote_detected"] is True


def test_v2_4_repo_identity_locks_wrong_root(tmp_path: Path):
    root = tmp_path / ("AR" + "GOS_CLEAN")
    root.mkdir()
    report = bridge.build_repo_identity_report(
        root,
        head="abc",
        branch="main",
        remote="https://github.com/RomelSubia/CONTENT_ENGINE_OMEGA.git",
        upstream="abc",
    )
    assert report["status"] == "LOCK"
    assert report["root_valid"] is False
    assert report["argos_path_detected"] is True


def test_v2_4_contamination_gate_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_4_ARGOS_CONTAMINATION_GATE_REPORT.json")
    assert report["status"] == "PASS"
    assert report["contamination_detected"] is False
    assert report["critical_marker_findings_count"] == 0
    assert report["critical_path_findings_count"] == 0


def test_v2_4_contamination_gate_blocks_marker(tmp_path: Path):
    root = tmp_path / "CONTENT_ENGINE_OMEGA"
    root.mkdir()
    (root / "bad.md").write_text("bad marker: " + "AR" + "GOS_CORE", encoding="utf-8")
    identity = bridge.build_repo_identity_report(
        root,
        head="abc",
        branch="main",
        remote="https://github.com/RomelSubia/CONTENT_ENGINE_OMEGA.git",
        upstream="abc",
    )
    report = bridge.build_argos_contamination_gate_report(root, identity)
    assert report["status"] == "BLOCK"
    assert report["contamination_detected"] is True
    assert report["critical_marker_findings_count"] == 1


def test_v2_4_authority_binding_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_4_AUTHORITY_BINDING_REPORT.json")
    assert report["status"] == "PASS"
    assert report["authority_set_status"] == "PASS"
    assert report["authority_hashes_present"] is True
    assert report["authority_hashes_valid"] is True
    assert report["authority_set_locked"] is True
    assert report["authority_set_can_be_reused_after_head_change"] is False
    assert report["authority_set_can_be_reused_after_scope_change"] is False


def test_v2_4_authority_binding_fails_closed_when_missing(tmp_path: Path):
    root = tmp_path / "CONTENT_ENGINE_OMEGA"
    root.mkdir()
    report = bridge.build_authority_binding_report(root)
    assert report["status"] == "BLOCK"
    assert report["missing_authority_files"]


def test_v2_4_scope_binding_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_4_SCOPE_BINDING_REPORT.json")
    assert report["status"] == "PASS"
    assert report["scope_locked"] is True
    assert report["scope_hash_present"] is True
    assert report["scope_hash_valid"] is True
    assert report["scope_change_invalidates_approval"] is True
    assert "execute_next_build" in report["prohibited_scope"]


def test_v2_4_build_request_contract_created_but_not_allowed_now():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_4_BUILD_REQUEST_CONTRACT_REPORT.json")
    assert report["status"] == "PASS"
    assert report["build_request_id"] == "BRIDGE_V2_4_2_BUILD_REQUEST"
    assert report["request_created"] is True
    assert report["request_valid"] is True
    assert report["human_approval_required"] is True
    assert report["human_approval_received"] is False
    assert report["approval_granted"] is False
    assert report["approval_consumed"] is False
    assert report["build_allowed_next"] is False
    assert report["build_allowed_now"] is False


def test_v2_4_human_approval_gate_requires_but_does_not_consume():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_REPORT.json")
    assert report["status"] == "PASS"
    assert report["human_approval_required"] is True
    assert report["human_approval_received"] is False
    assert report["human_approval_valid"] is False
    assert report["approval_granted"] is False
    assert report["approval_consumed"] is False
    assert report["approval_can_be_consumed_by_this_layer"] is False
    assert report["approval_consumption_deferred_to_next_layer"] is True
    assert report["approval_phrase_plaintext_storage_allowed"] is False
    assert report["approval_phrase_expected_hash_present"] is True
    assert report["approval_phrase_received"] is None
    assert report["approval_phrase_received_hash"] is None


def test_v2_4_approval_expiration_policy_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_4_APPROVAL_EXPIRATION_REPORT.json")
    assert report["status"] == "PASS"
    assert report["approval_expires_on_head_change"] is True
    assert report["approval_expires_on_authority_change"] is True
    assert report["approval_expires_on_scope_change"] is True
    assert report["approval_expires_on_repo_identity_change"] is True
    assert report["approval_expires_after_single_consumption"] is True
    assert report["permanent_approval_allowed"] is False


def test_v2_4_anti_replay_approval_report_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_4_ANTI_REPLAY_APPROVAL_REPORT.json")
    assert report["status"] == "PASS"
    assert report["approval_replay_blocked"] is True
    assert report["approval_self_grant_blocked"] is True
    assert report["approval_from_history_blocked"] is True
    assert report["approval_from_report_blocked"] is True
    assert report["approval_from_commit_blocked"] is True
    assert report["approval_from_manual_blocked"] is True
    assert report["generic_approval_blocked"] is True
    assert report["fresh_human_input_consumption_deferred"] is True
    assert report["approval_granted"] is False
    assert report["approval_consumed"] is False


def test_v2_4_resolve_approval_blocks_history_report_commit_manual():
    for source in ["HISTORY", "REPORT", "COMMIT", "MANUAL", "OLD_SEAL", "PREVIOUS_LAYER"]:
        result = bridge.resolve_approval_attempt(source, "approved")
        assert result["allowed"] is False
        assert result["approval_granted"] is False
        assert result["approval_consumed"] is False
        assert result["build_allowed_now"] is False


def test_v2_4_resolve_approval_blocks_generic_ok():
    for text in ["ok", "dale", "continua", "continúa", "aprobado", "ya lo aprobé", "aprueba tú"]:
        result = bridge.resolve_approval_attempt("NONE", text)
        assert result["allowed"] is False
        assert result["decision"] == "BLOCK_GENERIC_APPROVAL"


def test_v2_4_resolve_fresh_human_input_is_deferred_not_consumed():
    result = bridge.resolve_approval_attempt("FRESH_HUMAN_INPUT", "candidate phrase")
    assert result["allowed"] is False
    assert result["decision"] == "DEFER_TO_NEXT_LAYER_APPROVAL_CONSUMPTION_GATE"
    assert result["approval_granted"] is False
    assert result["approval_consumed"] is False
    assert result["build_allowed_now"] is False


def test_v2_4_blocked_capabilities_include_approval_and_runtime_blocks():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_4_BLOCKED_CAPABILITIES_REPORT.json")
    blocked = set(report["blocked_capabilities"])
    for item in [
        "AUTO_EXECUTION",
        "BRAIN_WRITE",
        "REPORTS_BRAIN_WRITE",
        "MANUAL_WRITE",
        "MANUAL_AUTO_UPDATE",
        "N8N_EXECUTION",
        "WEBHOOK_EXECUTION",
        "PUBLISHING",
        "OPENAI_API_RUNTIME",
        "CAPA9",
        "APPROVAL_REUSE",
        "APPROVAL_SELF_GRANT",
        "APPROVAL_FROM_HISTORY",
        "APPROVAL_CONSUMPTION_IN_SAME_LAYER",
    ]:
        assert item in blocked
    assert report["build_allowed_now"] is False
    assert report["build_allowed_next"] is False


def test_v2_4_anti_simulation_gate_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_4_ANTI_SIMULATION_GATE_REPORT.json")
    assert report["status"] == "PASS"
    assert report["anti_simulation_gate"] == "PASS"
    assert report["violations"] == []


def test_v2_4_validation_report_pass_and_safe():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_4_VALIDATION_REPORT.json")
    assert report["status"] == "PASS"
    assert report["validation_status"] == "PASS"
    assert report["build_request_created"] is True
    assert report["human_approval_required"] is True
    assert report["human_approval_received"] is False
    assert report["approval_granted"] is False
    assert report["approval_consumed"] is False
    assert report["build_allowed_next"] is False
    assert report["build_allowed_now"] is False
    assert report["external_execution"] == "DISABLED"
    assert report["brain_mutation"] == "BLOCKED"
    assert report["manual_mutation"] == "BLOCKED"
    assert report["auto_action"] is False


def test_v2_4_manifest_tracks_generated_artifacts_without_self_reference():
    manifest = j("00_SYSTEM/bridge/manifests/BRIDGE_V2_4_ARTIFACT_MANIFEST.json")
    assert manifest["status"] == "PASS"
    paths = {item["path"] for item in manifest["artifacts"]}
    for rel in bridge.MANIFEST_TRACKED_ARTIFACTS:
        assert rel in paths
    omitted = set(manifest["omitted_self_referential_artifacts"])
    assert "00_SYSTEM/bridge/manifests/BRIDGE_V2_4_ARTIFACT_MANIFEST.json" in omitted
    assert "00_SYSTEM/bridge/manifests/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_SEAL.json" in omitted
    assert all(item["sha256"] for item in manifest["artifacts"])


def test_v2_4_seal_is_final_human_approval_gate_seal():
    seal = j("00_SYSTEM/bridge/manifests/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_SEAL.json")
    assert seal["status"] == "SEALED_AS_GOVERNED_BUILD_REQUEST_CONTRACT_AND_HUMAN_APPROVAL_GATE_V2_4_2"
    assert seal["bridge_v2_3_authority_valid"] is True
    assert seal["repo_identity_valid"] is True
    assert seal["argos_contamination_gate_pass"] is True
    assert seal["build_request_contract_created"] is True
    assert seal["human_approval_required"] is True
    assert seal["human_approval_received"] is False
    assert seal["approval_granted"] is False
    assert seal["approval_consumed"] is False
    assert seal["build_allowed_now"] is False
    assert seal["build_allowed_next"] is False


def test_v2_4_danger_flags_false_on_generated_reports():
    for rel in [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_REPO_IDENTITY_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_ARGOS_CONTAMINATION_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_AUTHORITY_BINDING_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_SCOPE_BINDING_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_BUILD_REQUEST_CONTRACT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_4_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_4_HUMAN_APPROVAL_GATE_SEAL.json",
    ]:
        assert bridge.danger_flags_false(j(rel)) is True


def test_v2_4_expected_approval_hash_changes_with_head():
    first = bridge.expected_approval_hash(
        root=ROOT,
        head="head_a",
        branch="main",
        remote="https://github.com/RomelSubia/CONTENT_ENGINE_OMEGA.git",
        authority_set_hash="authority",
        scope_hash="scope",
    )
    second = bridge.expected_approval_hash(
        root=ROOT,
        head="head_b",
        branch="main",
        remote="https://github.com/RomelSubia/CONTENT_ENGINE_OMEGA.git",
        authority_set_hash="authority",
        scope_hash="scope",
    )
    assert first != second


def test_v2_4_expected_approval_hash_changes_with_authority():
    first = bridge.expected_approval_hash(
        root=ROOT,
        head="head",
        branch="main",
        remote="https://github.com/RomelSubia/CONTENT_ENGINE_OMEGA.git",
        authority_set_hash="authority_a",
        scope_hash="scope",
    )
    second = bridge.expected_approval_hash(
        root=ROOT,
        head="head",
        branch="main",
        remote="https://github.com/RomelSubia/CONTENT_ENGINE_OMEGA.git",
        authority_set_hash="authority_b",
        scope_hash="scope",
    )
    assert first != second


def test_v2_4_expected_approval_hash_changes_with_scope():
    first = bridge.expected_approval_hash(
        root=ROOT,
        head="head",
        branch="main",
        remote="https://github.com/RomelSubia/CONTENT_ENGINE_OMEGA.git",
        authority_set_hash="authority",
        scope_hash="scope_a",
    )
    second = bridge.expected_approval_hash(
        root=ROOT,
        head="head",
        branch="main",
        remote="https://github.com/RomelSubia/CONTENT_ENGINE_OMEGA.git",
        authority_set_hash="authority",
        scope_hash="scope_b",
    )
    assert first != second