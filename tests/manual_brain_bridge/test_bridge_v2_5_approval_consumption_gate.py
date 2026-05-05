from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BRIDGE_PATH = ROOT / "04_SCRIPTS/python/manual_brain_bridge/bridge_v2_5_approval_consumption_gate.py"

spec = importlib.util.spec_from_file_location("bridge_v2_5", BRIDGE_PATH)
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


def test_v2_5_generated_reports_exist():
    for rel in [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_REPO_IDENTITY_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_ARGOS_CONTAMINATION_GATE_REPORT.json",
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


def test_v2_5_repo_identity_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_5_REPO_IDENTITY_REPORT.json")
    assert report["status"] == "PASS"
    assert report["repo_identity_valid"] is True
    assert report["root_valid"] is True
    assert report["branch_valid"] is True
    assert report["remote_valid"] is True
    assert report["foreign_remote_detected"] is False
    assert report["foreign_path_detected"] is False


def test_v2_5_repo_identity_locks_wrong_remote(tmp_path: Path):
    report = bridge.build_repo_identity_report(
        tmp_path / "CONTENT_ENGINE_OMEGA",
        head="abc",
        branch="main",
        remote="https://github.com/RomelSubia/" + ("AR" + "GOS.git"),
        upstream="abc",
    )
    assert report["status"] == "LOCK"
    assert report["repo_identity_valid"] is False


def test_v2_5_repo_identity_locks_wrong_branch(tmp_path: Path):
    report = bridge.build_repo_identity_report(
        tmp_path / "CONTENT_ENGINE_OMEGA",
        head="abc",
        branch="wrong",
        remote="https://github.com/RomelSubia/CONTENT_ENGINE_OMEGA.git",
        upstream="abc",
    )
    assert report["status"] == "LOCK"
    assert report["branch_valid"] is False


def test_v2_5_repo_identity_locks_dirty_repo(tmp_path: Path):
    report = bridge.build_repo_identity_report(
        tmp_path / "CONTENT_ENGINE_OMEGA",
        head="abc",
        branch="main",
        remote="https://github.com/RomelSubia/CONTENT_ENGINE_OMEGA.git",
        upstream="abc",
        repo_clean=False,
    )
    assert report["status"] == "LOCK"
    assert report["repo_clean"] is False


def test_v2_5_repo_identity_locks_head_mismatch(tmp_path: Path):
    report = bridge.build_repo_identity_report(
        tmp_path / "CONTENT_ENGINE_OMEGA",
        head="abc",
        branch="main",
        remote="https://github.com/RomelSubia/CONTENT_ENGINE_OMEGA.git",
        upstream="def",
    )
    assert report["status"] == "LOCK"
    assert report["head_equals_upstream"] is False


def test_v2_5_contamination_gate_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_5_ARGOS_CONTAMINATION_GATE_REPORT.json")
    assert report["status"] == "PASS"
    assert report["contamination_detected"] is False
    assert report["critical_marker_findings_count"] == 0
    assert report["critical_path_findings_count"] == 0


def test_v2_5_contamination_gate_blocks_marker(tmp_path: Path):
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


def test_v2_5_v24_authority_consumption_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_5_V24_AUTHORITY_CONSUMPTION_REPORT.json")
    assert report["status"] == "PASS"
    assert report["v24_authority_status"] == "PASS"
    assert report["v24_authority_hashes_present"] is True
    assert report["v24_authority_hashes_valid"] is True
    assert report["v24_authority_set_locked"] is True
    assert report["build_request_id"] == "BRIDGE_V2_4_2_BUILD_REQUEST"
    assert report["human_approval_required"] is True
    assert report["human_approval_received_before_v25"] is False


def test_v2_5_v24_authority_fails_closed_when_missing(tmp_path: Path):
    root = tmp_path / "CONTENT_ENGINE_OMEGA"
    root.mkdir()
    report = bridge.build_v24_authority_consumption_report(root)
    assert report["status"] == "BLOCK"
    assert report["missing_authority_files"]


def test_v2_5_challenge_deterministic():
    first = challenge()
    second = challenge()
    assert first["approval_challenge_hash"] == second["approval_challenge_hash"]
    assert first["required_approval_phrase"] == second["required_approval_phrase"]
    assert first["expected_approval_hash"] == second["expected_approval_hash"]


def test_v2_5_challenge_contains_no_plaintext_storage():
    c = challenge()
    assert c["approval_plaintext_storage_allowed"] is False
    assert c["approval_plaintext_stored"] is False
    assert c["required_approval_phrase"].startswith("APRUEBO CONSUMIR")


def test_v2_5_receipt_passes_with_required_phrase():
    c = challenge()
    report = bridge.build_approval_input_receipt_report(c["required_approval_phrase"], c)
    assert report["status"] == "PASS"
    assert report["human_approval_received"] is True
    assert report["approval_match"] is True
    assert report["approval_plaintext_stored"] is False


def test_v2_5_receipt_blocks_empty_approval():
    c = challenge()
    report = bridge.build_approval_input_receipt_report("", c)
    assert report["status"] == "BLOCK"
    assert report["approval_match"] is False


def test_v2_5_receipt_blocks_generic_approval():
    c = challenge()
    for text in ["ok", "dale", "continua", "continúa", "aprobado", "hazlo", "sí"]:
        report = bridge.build_approval_input_receipt_report(text, c)
        assert report["status"] == "BLOCK"
        assert report["approval_match"] is False


def test_v2_5_receipt_blocks_wrong_phrase():
    c = challenge()
    report = bridge.build_approval_input_receipt_report(c["required_approval_phrase"] + " X", c)
    assert report["status"] == "BLOCK"
    assert report["approval_match"] is False


def test_v2_5_resolve_blocks_forbidden_sources():
    c = challenge()
    phrase = c["required_approval_phrase"]
    expected = c["expected_approval_hash"]
    for source in ["HISTORY", "REPORT", "COMMIT", "MANUAL", "BRAIN", "OLD_SEAL", "PREVIOUS_LAYER", "GLOBAL", "SELF"]:
        result = bridge.resolve_approval_attempt(source, phrase, expected)
        assert result["allowed"] is False
        assert result["approval_granted"] is False
        assert result["approval_consumed"] is False
        assert result["build_allowed_next"] is False


def test_v2_5_resolve_blocks_reuse_old_head_wrong_authority_wrong_scope():
    c = challenge()
    phrase = c["required_approval_phrase"]
    expected = c["expected_approval_hash"]

    assert bridge.resolve_approval_attempt("FRESH_HUMAN_TERMINAL_INPUT", phrase, expected, already_consumed=True)["decision"] == "BLOCK_APPROVAL_REUSE"
    assert bridge.resolve_approval_attempt("FRESH_HUMAN_TERMINAL_INPUT", phrase, expected, head_matches=False)["decision"] == "BLOCK_APPROVAL_FROM_OLD_HEAD"
    assert bridge.resolve_approval_attempt("FRESH_HUMAN_TERMINAL_INPUT", phrase, expected, authority_matches=False)["decision"] == "BLOCK_APPROVAL_FROM_WRONG_AUTHORITY"
    assert bridge.resolve_approval_attempt("FRESH_HUMAN_TERMINAL_INPUT", phrase, expected, scope_matches=False)["decision"] == "BLOCK_APPROVAL_FROM_WRONG_SCOPE"


def test_v2_5_resolve_allows_fresh_exact_phrase():
    c = challenge()
    result = bridge.resolve_approval_attempt(
        "FRESH_HUMAN_TERMINAL_INPUT",
        c["required_approval_phrase"],
        c["expected_approval_hash"],
    )
    assert result["allowed"] is True
    assert result["approval_granted"] is True
    assert result["approval_consumed"] is True
    assert result["build_allowed_next"] is True
    assert result["build_allowed_now"] is False


def test_v2_5_approval_binding_pass():
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


def test_v2_5_approval_consumption_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_CONSUMPTION_REPORT.json")
    assert report["status"] == "PASS"
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


def test_v2_5_anti_replay_consumption_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_5_ANTI_REPLAY_CONSUMPTION_REPORT.json")
    assert report["status"] == "PASS"
    assert report["approval_replay_blocked"] is True
    assert report["approval_self_grant_blocked"] is True
    assert report["approval_from_history_blocked"] is True
    assert report["approval_from_report_blocked"] is True
    assert report["approval_from_commit_blocked"] is True
    assert report["approval_from_manual_blocked"] is True
    assert report["approval_from_brain_blocked"] is True
    assert report["approval_reuse_blocked"] is True
    assert report["valid_case_allowed"] is True


def test_v2_5_expiration_policy_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_EXPIRATION_REPORT.json")
    assert report["status"] == "PASS"
    assert report["approval_expires_on_head_change"] is True
    assert report["approval_expires_on_branch_change"] is True
    assert report["approval_expires_on_remote_change"] is True
    assert report["approval_expires_on_v24_seal_hash_change"] is True
    assert report["approval_expires_after_single_consumption"] is True
    assert report["permanent_approval_allowed"] is False


def test_v2_5_blocked_capabilities_preserve_runtime_blocks():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_5_BLOCKED_CAPABILITIES_REPORT.json")
    blocked = set(report["blocked_capabilities"])
    for item in [
        "AUTO_EXECUTION",
        "DIRECT_BUILD_EXECUTION",
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
    ]:
        assert item in blocked
    assert report["approval_granted"] is True
    assert report["approval_consumed"] is True
    assert report["build_allowed_next"] is True
    assert report["build_allowed_now"] is False
    assert report["execution_allowed"] is False


def test_v2_5_transition_gate_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_5_TRANSITION_GATE_REPORT.json")
    assert report["status"] == "PASS"
    assert report["approval_consumed"] is True
    assert report["build_allowed_next"] is True
    assert report["build_allowed_now"] is False
    assert report["execution_allowed"] is False
    assert report["next_safe_step"] == "BLUEPRINT_V2_6_GOVERNED_BUILD_EXECUTION_GATE"


def test_v2_5_anti_simulation_gate_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_5_ANTI_SIMULATION_GATE_REPORT.json")
    assert report["status"] == "PASS"
    assert report["anti_simulation_gate"] == "PASS"
    assert report["violations"] == []


def test_v2_5_validation_report_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_5_VALIDATION_REPORT.json")
    assert report["status"] == "PASS"
    assert report["validation_status"] == "PASS"
    assert report["human_approval_required"] is True
    assert report["human_approval_received"] is True
    assert report["human_approval_valid"] is True
    assert report["approval_match"] is True
    assert report["approval_granted"] is True
    assert report["approval_consumed"] is True
    assert report["approval_reuse_allowed"] is False
    assert report["approval_plaintext_stored"] is False
    assert report["build_allowed_next"] is True
    assert report["build_allowed_now"] is False
    assert report["external_execution"] == "DISABLED"
    assert report["brain_mutation"] == "BLOCKED"
    assert report["manual_mutation"] == "BLOCKED"


def test_v2_5_manifest_tracks_generated_artifacts_without_self_reference():
    manifest = j("00_SYSTEM/bridge/manifests/BRIDGE_V2_5_ARTIFACT_MANIFEST.json")
    assert manifest["status"] == "PASS"
    paths = {item["path"] for item in manifest["artifacts"]}
    for rel in bridge.MANIFEST_TRACKED_ARTIFACTS:
        assert rel in paths
    omitted = set(manifest["omitted_self_referential_artifacts"])
    assert "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_ARTIFACT_MANIFEST.json" in omitted
    assert "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_APPROVAL_CONSUMPTION_GATE_SEAL.json" in omitted
    assert all(item["sha256"] for item in manifest["artifacts"])


def test_v2_5_seal_is_final_approval_consumption_gate_seal():
    seal = j("00_SYSTEM/bridge/manifests/BRIDGE_V2_5_APPROVAL_CONSUMPTION_GATE_SEAL.json")
    assert seal["status"] == "SEALED_AS_APPROVAL_CONSUMPTION_GATE_V2_5"
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


def test_v2_5_danger_always_false_on_generated_reports():
    for rel in [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_REPO_IDENTITY_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_ARGOS_CONTAMINATION_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_INPUT_RECEIPT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_APPROVAL_CONSUMPTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_5_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_5_APPROVAL_CONSUMPTION_GATE_SEAL.json",
    ]:
        assert bridge.danger_always_false(j(rel)) is True


def test_v2_5_challenge_hash_changes_with_head():
    repo = j("00_SYSTEM/bridge/reports/BRIDGE_V2_5_REPO_IDENTITY_REPORT.json")
    first = bridge.build_challenge(ROOT, "head_a", repo["branch"], repo["remote"], "head_a")
    second = bridge.build_challenge(ROOT, "head_b", repo["branch"], repo["remote"], "head_b")
    assert first["approval_challenge_hash"] != second["approval_challenge_hash"]


def test_v2_5_challenge_hash_changes_with_remote():
    repo = j("00_SYSTEM/bridge/reports/BRIDGE_V2_5_REPO_IDENTITY_REPORT.json")
    first = bridge.build_challenge(ROOT, repo["head"], repo["branch"], "remote_a", repo["upstream"])
    second = bridge.build_challenge(ROOT, repo["head"], repo["branch"], "remote_b", repo["upstream"])
    assert first["approval_challenge_hash"] != second["approval_challenge_hash"]