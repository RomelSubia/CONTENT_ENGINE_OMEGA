from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BRIDGE_PATH = ROOT / "04_SCRIPTS/python/manual_brain_bridge/bridge_v2_7_post_execution_audit.py"

spec = importlib.util.spec_from_file_location("bridge_v2_7", BRIDGE_PATH)
bridge = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(bridge)


def j(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_v2_7_generated_reports_exist():
    for rel in [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_REPO_IDENTITY_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_V26_AUTHORITY_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_EXECUTION_CLOSURE_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_PERMISSION_STATE_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_ARTIFACT_INTEGRITY_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_NO_TOUCH_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_WATCH_ONLY_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_BLOCKED_CAPABILITIES_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_ANTI_REGRESSION_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_ANTI_SIMULATION_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_MANIFEST.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_SEAL.json",
    ]:
        assert (ROOT / rel).is_file(), rel


def test_v2_7_repo_identity_audit_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_7_REPO_IDENTITY_AUDIT_REPORT.json")
    assert report["status"] == "PASS"
    assert report["repo_identity_valid"] is True
    assert report["head_is_required_v26"] is True
    assert report["head_equals_upstream"] is True


def test_v2_7_repo_identity_locks_wrong_head(tmp_path: Path):
    report = bridge.build_repo_identity_audit_report(
        tmp_path / "CONTENT_ENGINE_OMEGA",
        head="wrong",
        branch="main",
        remote="https://github.com/RomelSubia/CONTENT_ENGINE_OMEGA.git",
        upstream="wrong",
    )
    assert report["status"] == "LOCK"
    assert report["head_is_required_v26"] is False


def test_v2_7_repo_identity_locks_wrong_remote(tmp_path: Path):
    report = bridge.build_repo_identity_audit_report(
        tmp_path / "CONTENT_ENGINE_OMEGA",
        head=bridge.V26_REQUIRED_HEAD,
        branch="main",
        remote="https://github.com/RomelSubia/" + ("AR" + "GOS.git"),
        upstream=bridge.V26_REQUIRED_HEAD,
    )
    assert report["status"] == "LOCK"
    assert report["remote_valid"] is False


def test_v2_7_v26_authority_audit_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_7_V26_AUTHORITY_AUDIT_REPORT.json")
    assert report["status"] == "PASS"
    assert report["v26_authority_audit_status"] == "PASS"
    assert report["v26_authority_hashes_present"] is True
    assert report["v26_authority_set_locked"] is True
    assert report["v26_seal_status"] == "SEALED_AS_GOVERNED_BUILD_EXECUTION_GATE_V2_6"
    assert report["v26_permission_consumed"] is True
    assert report["v26_execution_window_closed"] is True
    assert report["v26_build_allowed_now"] is False
    assert report["v26_build_allowed_next"] is False
    assert report["v26_post_execution_audit_allowed_next"] is True


def test_v2_7_execution_closure_audit_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_7_EXECUTION_CLOSURE_AUDIT_REPORT.json")
    assert report["status"] == "PASS"
    assert report["execution_closure_audited"] is True
    assert report["v26_execution_window_closed"] is True
    assert report["v26_execution_window_reusable"] is False
    assert report["v26_execution_window_reuse_blocked"] is True
    assert report["v26_controlled_execution_valid"] is True


def test_v2_7_execution_closure_blocks_unclean_authority():
    authority = bridge.base_report("authority", "BLOCK")
    authority["semantic_checks"] = {"window_closed": False, "window_reusable_false": False}
    report = bridge.build_execution_closure_audit_report(authority)
    assert report["status"] == "BLOCK"
    assert report["uncLOSED_window_detected"] is True


def test_v2_7_permission_state_audit_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_7_PERMISSION_STATE_AUDIT_REPORT.json")
    assert report["status"] == "PASS"
    assert report["post_execution_audit_permission_detected_from_v26"] is True
    assert report["post_execution_audit_permission_consumed_by_v27"] is True
    assert report["post_execution_audit_allowed_next"] is False
    assert report["post_execution_audit_reusable"] is False
    assert report["v25_permission_reusable_after_v26"] is False
    assert report["v26_execution_window_reusable_after_audit"] is False


def test_v2_7_permission_state_blocks_without_v26_audit_permission():
    authority = bridge.base_report("authority", "PASS")
    authority["semantic_checks"] = {"validation_post_execution_audit_allowed_next": False}
    closure = bridge.base_report("closure", "PASS")
    report = bridge.build_permission_state_audit_report(authority, closure)
    assert report["status"] == "BLOCK"
    assert report["post_execution_audit_permission_consumed_by_v27"] is False


def test_v2_7_artifact_integrity_audit_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_7_ARTIFACT_INTEGRITY_AUDIT_REPORT.json")
    assert report["status"] == "PASS"
    assert report["artifact_integrity_audited"] is True
    assert report["v26_authority_hash_unchanged"] is True
    assert report["v26_artifacts_mutated_by_v27"] is False
    assert report["v26_authority_files_missing_hash"] == []


def test_v2_7_artifact_integrity_blocks_mutation():
    before = {"a": "1"}
    after = {"a": "2"}
    permission = bridge.base_report("permission", "PASS")
    report = bridge.build_artifact_integrity_audit_report(ROOT, before, after, permission)
    assert report["status"] == "BLOCK"
    assert report["v26_authority_hash_unchanged"] is False


def test_v2_7_no_touch_audit_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_7_NO_TOUCH_AUDIT_REPORT.json")
    assert report["status"] == "PASS"
    assert report["no_touch_audited"] is True
    assert report["no_touch_pass"] is True
    assert report["no_touch_added"] == []
    assert report["no_touch_removed"] == []
    assert report["no_touch_changed"] == []


def test_v2_7_no_touch_blocks_change():
    before = {"a": {"sha256": "1", "length": 1}}
    after = {"a": {"sha256": "2", "length": 1}}
    report = bridge.build_no_touch_audit_report(before, after)
    assert report["status"] == "BLOCK"
    assert report["no_touch_pass"] is False


def test_v2_7_watch_only_audit_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_7_WATCH_ONLY_AUDIT_REPORT.json")
    assert report["status"] == "PASS"
    assert report["watch_only_audited"] is True
    assert report["watch_only_pass"] is True
    assert report["watch_only_added"] == []
    assert report["watch_only_removed"] == []
    assert report["watch_only_changed"] == []


def test_v2_7_watch_only_blocks_change():
    before = {"a": {"sha256": "1", "length": 1}}
    after = {"a": {"sha256": "1", "length": 2}}
    report = bridge.build_watch_only_audit_report(before, after)
    assert report["status"] == "BLOCK"
    assert report["watch_only_pass"] is False


def test_v2_7_blocked_capabilities_audit_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_7_BLOCKED_CAPABILITIES_AUDIT_REPORT.json")
    assert report["status"] == "PASS"
    assert report["execution_allowed"] is False
    assert report["external_execution_allowed"] is False
    assert report["manual_write_allowed"] is False
    assert report["brain_write_allowed"] is False
    assert report["n8n_allowed"] is False
    assert report["webhook_allowed"] is False
    assert report["publishing_allowed"] is False


def test_v2_7_anti_regression_audit_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_7_ANTI_REGRESSION_AUDIT_REPORT.json")
    assert report["status"] == "PASS"
    assert report["anti_regression_audited"] is True
    assert report["v26_authority_not_downgraded"] is True
    assert report["v26_authority_not_mutated"] is True
    assert report["danger_capabilities_remain_blocked"] is True


def test_v2_7_anti_simulation_audit_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_7_ANTI_SIMULATION_AUDIT_REPORT.json")
    assert report["status"] == "PASS"
    assert report["anti_simulation_audit"] == "PASS"
    assert report["violations"] == []


def test_v2_7_anti_simulation_blocks_build_allowed_now():
    bad = bridge.base_report("bad", "PASS")
    bad["build_allowed_now"] = True
    bad["warning_review_or_gate_closure_allowed_next"] = True
    report = bridge.build_anti_simulation_audit_report([bad])
    assert report["status"] == "BLOCK"
    assert any("BUILD_ALLOWED_NOW_TRUE" in item for item in report["violations"])


def test_v2_7_anti_simulation_blocks_post_audit_left_open():
    bad = bridge.base_report("bad", "PASS")
    bad["post_execution_audit_allowed_next"] = True
    bad["warning_review_or_gate_closure_allowed_next"] = True
    report = bridge.build_anti_simulation_audit_report([bad])
    assert report["status"] == "BLOCK"
    assert any("POST_EXECUTION_AUDIT_LEFT_OPEN" in item for item in report["violations"])


def test_v2_7_validation_report_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_7_VALIDATION_REPORT.json")
    assert report["status"] == "PASS"
    assert report["validation_status"] == "PASS"
    assert report["post_execution_audit_completed"] is True
    assert report["post_execution_audit_permission_consumed_by_v27"] is True
    assert report["post_execution_audit_reusable"] is False
    assert report["v25_permission_reusable_after_v26"] is False
    assert report["v26_execution_window_reusable_after_audit"] is False
    assert report["v26_execution_window_closed"] is True
    assert report["v26_authority_hash_unchanged"] is True
    assert report["no_touch_pass"] is True
    assert report["watch_only_pass"] is True


def test_v2_7_manifest_pass():
    manifest = j("00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_MANIFEST.json")
    assert manifest["status"] == "PASS"
    paths = {item["path"] for item in manifest["artifacts"]}
    for rel in bridge.MANIFEST_TRACKED_ARTIFACTS:
        assert rel in paths
    assert all(item["sha256"] for item in manifest["artifacts"])


def test_v2_7_seal_pass():
    seal = j("00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_SEAL.json")
    assert seal["status"] == "SEALED_AS_POST_EXECUTION_AUDIT_V2_7"
    assert seal["post_execution_audit_completed"] is True
    assert seal["post_execution_audit_permission_consumed_by_v27"] is True
    assert seal["post_execution_audit_allowed_next"] is False
    assert seal["post_execution_audit_reusable"] is False
    assert seal["v25_permission_reusable_after_v26"] is False
    assert seal["v26_execution_window_closed"] is True
    assert seal["v26_execution_window_reusable_after_audit"] is False
    assert seal["v26_authority_hash_unchanged"] is True
    assert seal["no_touch_pass"] is True
    assert seal["watch_only_pass"] is True


def test_v2_7_final_build_allowed_flags_false():
    for rel in [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_PERMISSION_STATE_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_SEAL.json",
    ]:
        data = j(rel)
        assert data["build_allowed_now"] is False
        assert data["build_allowed_next"] is False
        assert data["post_execution_audit_allowed_next"] is False


def test_v2_7_next_gate_allowed_true():
    validation = j("00_SYSTEM/bridge/reports/BRIDGE_V2_7_VALIDATION_REPORT.json")
    seal = j("00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_SEAL.json")
    assert validation["warning_review_or_gate_closure_allowed_next"] is True
    assert seal["warning_review_or_gate_closure_allowed_next"] is True
    assert validation["next_safe_step"] == "WARNING_REVIEW_OR_GATE_CLOSURE_V2_7"
    assert seal["next_safe_step"] == "WARNING_REVIEW_OR_GATE_CLOSURE_V2_7"


def test_v2_7_danger_always_false_on_generated_reports():
    for rel in [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_REPO_IDENTITY_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_PERMISSION_STATE_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_EXECUTION_CLOSURE_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_ARTIFACT_INTEGRITY_AUDIT_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_POST_EXECUTION_AUDIT_SEAL.json",
    ]:
        assert bridge.danger_always_false(j(rel)) is True