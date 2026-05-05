from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BRIDGE_PATH = ROOT / "04_SCRIPTS/python/manual_brain_bridge/bridge_v2_5_approval_consumption_gate.py"

spec = importlib.util.spec_from_file_location("bridge_v2_5_BUILD_FIX_3", BRIDGE_PATH)
bridge = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(bridge)


def j(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def challenge() -> dict:
    repo = j("00_SYSTEM/bridge/reports/BRIDGE_V2_5_REPO_IDENTITY_REPORT.json")
    return bridge.build_challenge(
        root=ROOT,
        head=repo["head"],
        branch=repo["branch"],
        remote=repo["remote"],
        upstream=repo["upstream"],
    )


def test_v2_5_BUILD_FIX_3_generated_reports_exist():
    for rel in [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_REPO_IDENTITY_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_CONTAMINATION_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_V24_AUTHORITY_CONSUMPTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_INPUT_RECEIPT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_BINDING_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_CONSUMPTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_ANTI_REPLAY_CONSUMPTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_EXPIRATION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_BLOCKED_CAPABILITIES_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_TRANSITION_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_ANTI_SIMULATION_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_ARTIFACT_MANIFEST.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_APPROVAL_CONSUMPTION_GATE_SEAL.json",
    ]:
        assert (ROOT / rel).is_file(), rel


def test_v2_5_BUILD_FIX_3_repo_identity_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_5_REPO_IDENTITY_REPORT.json")
    assert report["status"] == "PASS"
    assert report["repo_identity_valid"] is True
    assert report["root_valid"] is True
    assert report["branch_valid"] is True
    assert report["remote_valid"] is True
    assert report["foreign_remote_detected"] is False
    assert report["foreign_path_detected"] is False


def test_v2_5_BUILD_FIX_3_contamination_gate_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_5_CONTAMINATION_GATE_REPORT.json")
    assert report["status"] == "PASS"
    assert report["contamination_detected"] is False
    assert report["critical_marker_findings_count"] == 0
    assert report["critical_path_findings_count"] == 0


def test_v2_5_BUILD_FIX_3_v24_authority_consumption_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_5_V24_AUTHORITY_CONSUMPTION_REPORT.json")
    assert report["status"] == "PASS"
    assert report["v24_authority_status"] == "PASS"
    assert report["v24_authority_hashes_present"] is True
    assert report["v24_authority_hashes_valid"] is True
    assert report["v24_authority_set_locked"] is True
    assert report["build_request_id"] == "BRIDGE_V2_4_2_BUILD_REQUEST"


def test_v2_5_BUILD_FIX_3_challenge_deterministic():
    first = challenge()
    second = challenge()
    assert first["approval_challenge_hash"] == second["approval_challenge_hash"]
    assert first["required_approval_phrase"] == second["required_approval_phrase"]
    assert first["expected_approval_hash"] == second["expected_approval_hash"]


def test_v2_5_BUILD_FIX_3_receipt_passes_with_hash_only():
    c = challenge()
    report = bridge.build_approval_input_receipt_report(True, c["expected_approval_hash"], c["expected_approval_hash"])
    assert report["status"] == "PASS"
    assert report["hash_first_approval_transfer"] is True
    assert report["python_received_approval_plaintext"] is False
    assert report["approval_match"] is True
    assert report["approval_plaintext_stored"] is False


def test_v2_5_BUILD_FIX_3_receipt_blocks_absent_hash():
    c = challenge()
    report = bridge.build_approval_input_receipt_report(False, "", c["expected_approval_hash"])
    assert report["status"] == "BLOCK"
    assert report["approval_match"] is False


def test_v2_5_BUILD_FIX_3_receipt_blocks_wrong_hash():
    c = challenge()
    wrong = bridge.sha256_text("wrong")
    report = bridge.build_approval_input_receipt_report(True, wrong, c["expected_approval_hash"])
    assert report["status"] == "BLOCK"
    assert report["approval_match"] is False


def test_v2_5_BUILD_FIX_3_receipt_blocks_bad_hash_shape():
    c = challenge()
    report = bridge.build_approval_input_receipt_report(True, "abc", c["expected_approval_hash"])
    assert report["status"] == "BLOCK"
    assert report["approval_hash_shape_valid"] is False


def test_v2_5_BUILD_FIX_3_approval_binding_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_BINDING_REPORT.json")
    assert report["status"] == "PASS"
    assert report["approval_bound_to_repo"] is True
    assert report["approval_bound_to_branch"] is True
    assert report["approval_bound_to_remote"] is True
    assert report["approval_bound_to_head"] is True
    assert report["approval_bound_to_v24_seal_hash"] is True
    assert report["approval_bound_to_build_request_hash"] is True
    assert report["approval_bound_to_authority_hash"] is True
    assert report["approval_bound_to_scope_hash"] is True


def test_v2_5_BUILD_FIX_3_approval_consumption_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_CONSUMPTION_REPORT.json")
    assert report["status"] == "PASS"
    assert report["hash_first_approval_transfer"] is True
    assert report["python_received_approval_plaintext"] is False
    assert report["human_approval_required"] is True
    assert report["human_approval_received"] is True
    assert report["human_approval_valid"] is True
    assert report["approval_match"] is True
    assert report["approval_granted"] is True
    assert report["approval_consumed"] is True
    assert report["approval_consumption_count"] == 1
    assert report["approval_reuse_allowed"] is False
    assert report["build_allowed_next"] is True
    assert report["build_allowed_now"] is False
    assert report["execution_allowed"] is False


def test_v2_5_BUILD_FIX_3_anti_replay_consumption_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_5_ANTI_REPLAY_CONSUMPTION_REPORT.json")
    assert report["status"] == "PASS"
    assert report["plaintext_to_python_blocked"] is True
    assert report["approval_replay_blocked"] is True
    assert report["approval_self_grant_blocked"] is True
    assert report["approval_from_history_blocked"] is True
    assert report["approval_from_report_blocked"] is True
    assert report["approval_from_commit_blocked"] is True
    assert report["approval_from_manual_blocked"] is True
    assert report["approval_from_brain_blocked"] is True
    assert report["approval_reuse_blocked"] is True
    assert report["valid_case_allowed"] is True


def test_v2_5_BUILD_FIX_3_transition_gate_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_5_TRANSITION_GATE_REPORT.json")
    assert report["status"] == "PASS"
    assert report["approval_consumed"] is True
    assert report["build_allowed_next"] is True
    assert report["build_allowed_now"] is False
    assert report["execution_allowed"] is False
    assert report["next_safe_step"] == "BLUEPRINT_V2_6_GOVERNED_BUILD_EXECUTION_GATE"


def test_v2_5_BUILD_FIX_3_validation_report_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_5_VALIDATION_REPORT.json")
    assert report["status"] == "PASS"
    assert report["validation_status"] == "PASS"
    assert report["hash_first_approval_transfer"] is True
    assert report["python_received_approval_plaintext"] is False
    assert report["human_approval_required"] is True
    assert report["human_approval_received"] is True
    assert report["human_approval_valid"] is True
    assert report["approval_granted"] is True
    assert report["approval_consumed"] is True
    assert report["approval_reuse_allowed"] is False
    assert report["approval_plaintext_stored"] is False
    assert report["build_allowed_next"] is True
    assert report["build_allowed_now"] is False
    assert report["external_execution"] == "DISABLED"
    assert report["brain_mutation"] == "BLOCKED"
    assert report["manual_mutation"] == "BLOCKED"


def test_v2_5_BUILD_FIX_3_manifest_pass():
    manifest = j("00_SYSTEM/bridge/manifests/BRIDGE_V2_5_ARTIFACT_MANIFEST.json")
    assert manifest["status"] == "PASS"
    paths = {item["path"] for item in manifest["artifacts"]}
    for rel in bridge.MANIFEST_TRACKED_ARTIFACTS:
        assert rel in paths
    assert all(item["sha256"] for item in manifest["artifacts"])


def test_v2_5_BUILD_FIX_3_seal_pass():
    seal = j("00_SYSTEM/bridge/manifests/BRIDGE_V2_5_APPROVAL_CONSUMPTION_GATE_SEAL.json")
    assert seal["status"] == "SEALED_AS_APPROVAL_CONSUMPTION_GATE_V2_5_BUILD_FIX_3"
    assert seal["hash_first_approval_transfer"] is True
    assert seal["python_received_approval_plaintext"] is False
    assert seal["v24_authority_valid"] is True
    assert seal["repo_identity_valid"] is True
    assert seal["contamination_gate_pass"] is True
    assert seal["human_approval_required"] is True
    assert seal["human_approval_received"] is True
    assert seal["human_approval_valid"] is True
    assert seal["approval_granted"] is True
    assert seal["approval_consumed"] is True
    assert seal["approval_reuse_allowed"] is False
    assert seal["approval_plaintext_stored"] is False
    assert seal["build_allowed_next"] is True
    assert seal["build_allowed_now"] is False
    assert seal["execution_allowed"] is False


def test_v2_5_BUILD_FIX_3_danger_always_false_on_generated_reports():
    for rel in [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_REPO_IDENTITY_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_CONTAMINATION_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_INPUT_RECEIPT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_CONSUMPTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_APPROVAL_CONSUMPTION_GATE_SEAL.json",
    ]:
        assert bridge.danger_always_false(j(rel)) is True


def test_v2_5_BUILD_FIX_3_wrong_remote_locks(tmp_path: Path):
    report = bridge.build_repo_identity_report(
        tmp_path / "CONTENT_ENGINE_OMEGA",
        head="abc",
        branch="main",
        remote="https://github.com/RomelSubia/" + ("AR" + "GOS.git"),
        upstream="abc",
    )
    assert report["status"] == "LOCK"


def test_v2_5_BUILD_FIX_3_contamination_blocks_marker(tmp_path: Path):
    root = tmp_path / "CONTENT_ENGINE_OMEGA"
    root.mkdir()
    (root / "bad.md").write_text("bad marker: " + ("AR" + "GOS_CORE"), encoding="utf-8")
    identity = bridge.build_repo_identity_report(
        root,
        head="abc",
        branch="main",
        remote="https://github.com/RomelSubia/CONTENT_ENGINE_OMEGA.git",
        upstream="abc",
    )
    report = bridge.build_contamination_gate_report(root, identity)
    assert report["status"] == "BLOCK"
    assert report["contamination_detected"] is True