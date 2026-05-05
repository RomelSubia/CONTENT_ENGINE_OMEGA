from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BRIDGE_PATH = ROOT / "04_SCRIPTS/python/manual_brain_bridge/bridge_v2_6_governed_build_execution_gate.py"

spec = importlib.util.spec_from_file_location("bridge_v2_6", BRIDGE_PATH)
bridge = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(bridge)


def j(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_v2_6_generated_reports_exist():
    for rel in [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_REPO_IDENTITY_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_V25_AUTHORITY_CONSUMPTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_V25_PERMISSION_CONSUMPTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_EXECUTION_SCOPE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_EXECUTION_WINDOW_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_CONTROLLED_BUILD_EXECUTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_AUTHORITY_INTEGRITY_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_BLOCKED_CAPABILITIES_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_NO_TOUCH_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_WATCH_ONLY_INTEGRITY_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_ANTI_SIMULATION_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_ARTIFACT_MANIFEST.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_GOVERNED_BUILD_EXECUTION_GATE_SEAL.json",
    ]:
        assert (ROOT / rel).is_file(), rel


def test_v2_6_repo_identity_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_6_REPO_IDENTITY_REPORT.json")
    assert report["status"] == "PASS"
    assert report["repo_identity_valid"] is True
    assert report["root_valid"] is True
    assert report["branch_valid"] is True
    assert report["remote_valid"] is True
    assert report["head_is_required_v25"] is True


def test_v2_6_repo_identity_locks_wrong_head(tmp_path: Path):
    report = bridge.build_repo_identity_report(
        tmp_path / "CONTENT_ENGINE_OMEGA",
        head="wrong",
        branch="main",
        remote="https://github.com/RomelSubia/CONTENT_ENGINE_OMEGA.git",
        upstream="wrong",
    )
    assert report["status"] == "LOCK"
    assert report["head_is_required_v25"] is False


def test_v2_6_repo_identity_locks_wrong_remote(tmp_path: Path):
    report = bridge.build_repo_identity_report(
        tmp_path / "CONTENT_ENGINE_OMEGA",
        head=bridge.V25_REQUIRED_HEAD,
        branch="main",
        remote="https://github.com/RomelSubia/" + ("AR" + "GOS.git"),
        upstream=bridge.V25_REQUIRED_HEAD,
    )
    assert report["status"] == "LOCK"
    assert report["remote_valid"] is False


def test_v2_6_v25_authority_consumption_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_6_V25_AUTHORITY_CONSUMPTION_REPORT.json")
    assert report["status"] == "PASS"
    assert report["v25_authority_status"] == "PASS"
    assert report["v25_authority_hashes_present"] is True
    assert report["v25_authority_set_locked"] is True
    assert report["v25_approval_consumed"] is True
    assert report["v25_build_allowed_next"] is True
    assert report["v25_build_allowed_now"] is False


def test_v2_6_v25_permission_consumption_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_6_V25_PERMISSION_CONSUMPTION_REPORT.json")
    assert report["status"] == "PASS"
    assert report["v25_permission_detected"] is True
    assert report["v25_build_allowed_next_found"] is True
    assert report["v25_approval_consumed"] is True
    assert report["v25_permission_consumed_by_v26"] is True
    assert report["v25_permission_consumption_count"] == 1
    assert report["v25_permission_reusable_after_v26"] is False


def test_v2_6_permission_blocks_without_authority():
    authority = bridge.base_report("fake", "BLOCK")
    repo = bridge.base_report("repo", "PASS")
    report = bridge.build_v25_permission_consumption_report(authority, repo)
    assert report["status"] == "BLOCK"
    assert report["v25_permission_consumed_by_v26"] is False


def test_v2_6_permission_blocks_without_repo():
    authority = bridge.base_report("authority", "PASS")
    authority["v25_build_allowed_next"] = True
    authority["v25_approval_consumed"] = True
    repo = bridge.base_report("repo", "LOCK")
    report = bridge.build_v25_permission_consumption_report(authority, repo)
    assert report["status"] == "BLOCK"


def test_v2_6_execution_scope_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_6_EXECUTION_SCOPE_REPORT.json")
    assert report["status"] == "PASS"
    assert report["controlled_internal_build_scope_declared"] is True
    assert report["external_execution_allowed"] is False
    assert report["manual_write_allowed"] is False
    assert report["brain_write_allowed"] is False


def test_v2_6_execution_window_closed_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_6_EXECUTION_WINDOW_REPORT.json")
    assert report["status"] == "PASS"
    assert report["execution_window_created"] is True
    assert report["execution_window_opened"] is True
    assert report["execution_window_consumed"] is True
    assert report["execution_window_closed"] is True
    assert report["execution_window_reusable"] is False


def test_v2_6_execution_window_blocks_without_scope():
    scope = bridge.base_report("scope", "BLOCK")
    report = bridge.build_execution_window_report(scope)
    assert report["status"] == "BLOCK"
    assert report["execution_window_closed"] is False


def test_v2_6_controlled_build_execution_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_6_CONTROLLED_BUILD_EXECUTION_REPORT.json")
    assert report["status"] == "PASS"
    assert report["controlled_build_execution_performed"] is True
    assert report["controlled_build_execution_valid"] is True
    assert report["controlled_build_execution_type"] == "INTERNAL_ARTIFACT_BUILD_ONLY"
    assert report["external_execution_performed"] is False
    assert report["manual_mutation_performed"] is False
    assert report["brain_mutation_performed"] is False


def test_v2_6_controlled_execution_blocks_open_window():
    window = bridge.base_report("window", "PASS")
    window["execution_window_closed"] = False
    report = bridge.build_controlled_build_execution_report(window)
    assert report["status"] == "BLOCK"
    assert report["controlled_build_execution_performed"] is False


def test_v2_6_authority_integrity_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_6_AUTHORITY_INTEGRITY_REPORT.json")
    assert report["status"] == "PASS"
    assert report["authority_hash_unchanged"] is True
    assert report["v25_authority_mutated"] is False


def test_v2_6_authority_integrity_blocks_drift():
    before = {"a": "1"}
    after = {"a": "2"}
    controlled = bridge.base_report("controlled", "PASS")
    report = bridge.build_authority_integrity_report(before, after, controlled)
    assert report["status"] == "BLOCK"
    assert report["authority_hash_unchanged"] is False


def test_v2_6_blocked_capabilities_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_6_BLOCKED_CAPABILITIES_REPORT.json")
    assert report["status"] == "PASS"
    assert report["v25_permission_reuse_allowed"] is False
    assert report["uncLOSED_execution_window_allowed"] is False
    assert report["build_chain_without_post_audit_allowed"] is False


def test_v2_6_no_touch_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_6_NO_TOUCH_REPORT.json")
    assert report["status"] == "PASS"
    assert report["no_touch_checked"] is True
    assert report["no_touch_pass"] is True
    assert report["no_touch_added"] == []
    assert report["no_touch_removed"] == []
    assert report["no_touch_changed"] == []


def test_v2_6_no_touch_diff_blocks():
    before = {"a": {"sha256": "1", "length": 1}}
    after = {"a": {"sha256": "2", "length": 1}}
    report = bridge.build_no_touch_report(before, after)
    assert report["status"] == "BLOCK"
    assert report["no_touch_pass"] is False
    assert report["no_touch_changed"] == ["a"]


def test_v2_6_watch_only_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_6_WATCH_ONLY_INTEGRITY_REPORT.json")
    assert report["status"] == "PASS"
    assert report["watch_only_integrity_checked"] is True
    assert report["watch_only_changed"] is False
    assert report["watch_only_pass"] is True


def test_v2_6_watch_only_diff_blocks():
    before = {"a": {"sha256": "1", "length": 1}}
    after = {"a": {"sha256": "1", "length": 2}}
    report = bridge.build_watch_only_integrity_report(before, after)
    assert report["status"] == "BLOCK"
    assert report["watch_only_changed"] is True
    assert report["watch_only_changed_paths"] == ["a"]


def test_v2_6_anti_simulation_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_6_ANTI_SIMULATION_GATE_REPORT.json")
    assert report["status"] == "PASS"
    assert report["anti_simulation_gate"] == "PASS"
    assert report["violations"] == []


def test_v2_6_anti_simulation_blocks_build_allowed_next():
    bad = bridge.base_report("bad", "PASS")
    bad["build_allowed_next"] = True
    report = bridge.build_anti_simulation_gate_report([bad])
    assert report["status"] == "BLOCK"
    assert any("BUILD_ALLOWED_NEXT_TRUE" in item for item in report["violations"])


def test_v2_6_validation_report_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_6_VALIDATION_REPORT.json")
    assert report["status"] == "PASS"
    assert report["validation_status"] == "PASS"
    assert report["v25_permission_consumed_by_v26"] is True
    assert report["v25_permission_reusable_after_v26"] is False
    assert report["execution_window_closed"] is True
    assert report["execution_window_reusable"] is False
    assert report["controlled_build_execution_performed"] is True
    assert report["authority_hash_unchanged"] is True
    assert report["no_touch_pass"] is True
    assert report["watch_only_pass"] is True


def test_v2_6_manifest_pass():
    manifest = j("00_SYSTEM/bridge/manifests/BRIDGE_V2_6_ARTIFACT_MANIFEST.json")
    assert manifest["status"] == "PASS"
    paths = {item["path"] for item in manifest["artifacts"]}
    for rel in bridge.MANIFEST_TRACKED_ARTIFACTS:
        assert rel in paths
    assert all(item["sha256"] for item in manifest["artifacts"])


def test_v2_6_seal_pass():
    seal = j("00_SYSTEM/bridge/manifests/BRIDGE_V2_6_GOVERNED_BUILD_EXECUTION_GATE_SEAL.json")
    assert seal["status"] == "SEALED_AS_GOVERNED_BUILD_EXECUTION_GATE_V2_6"
    assert seal["v25_authority_valid"] is True
    assert seal["v25_permission_consumed_by_v26"] is True
    assert seal["v25_permission_reusable_after_v26"] is False
    assert seal["execution_window_closed"] is True
    assert seal["execution_window_reusable"] is False
    assert seal["controlled_build_execution_performed"] is True
    assert seal["controlled_build_execution_valid"] is True
    assert seal["authority_hash_unchanged"] is True
    assert seal["no_touch_pass"] is True
    assert seal["watch_only_pass"] is True


def test_v2_6_final_build_allowed_next_false():
    for rel in [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_V25_PERMISSION_CONSUMPTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_EXECUTION_WINDOW_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_GOVERNED_BUILD_EXECUTION_GATE_SEAL.json",
    ]:
        assert j(rel)["build_allowed_next"] is False


def test_v2_6_final_build_allowed_now_false():
    for rel in [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_V25_PERMISSION_CONSUMPTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_EXECUTION_WINDOW_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_GOVERNED_BUILD_EXECUTION_GATE_SEAL.json",
    ]:
        assert j(rel)["build_allowed_now"] is False


def test_v2_6_post_execution_audit_allowed_next_true():
    validation = j("00_SYSTEM/bridge/reports/BRIDGE_V2_6_VALIDATION_REPORT.json")
    seal = j("00_SYSTEM/bridge/manifests/BRIDGE_V2_6_GOVERNED_BUILD_EXECUTION_GATE_SEAL.json")
    assert validation["post_execution_audit_allowed_next"] is True
    assert seal["post_execution_audit_allowed_next"] is True
    assert validation["next_safe_step"] == "POST_EXECUTION_AUDIT_V2_7"
    assert seal["next_safe_step"] == "POST_EXECUTION_AUDIT_V2_7"


def test_v2_6_danger_always_false_on_generated_reports():
    for rel in [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_REPO_IDENTITY_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_V25_PERMISSION_CONSUMPTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_EXECUTION_WINDOW_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_CONTROLLED_BUILD_EXECUTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_6_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_6_GOVERNED_BUILD_EXECUTION_GATE_SEAL.json",
    ]:
        assert bridge.danger_always_false(j(rel)) is True