from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BRIDGE_PATH = ROOT / "04_SCRIPTS/python/manual_brain_bridge/bridge_v2_7_warning_review_gate_closure.py"

spec = importlib.util.spec_from_file_location("bridge_v2_7_closure", BRIDGE_PATH)
bridge = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(bridge)


def j(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_v2_7_closure_generated_reports_exist():
    for rel in [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_WARNING_REVIEW_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_GATE_CLOSURE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_NEXT_LAYER_READINESS_MAP.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_NO_TOUCH_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_WATCH_ONLY_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_ANTI_SIMULATION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_MANIFEST.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_SEAL.json",
    ]:
        assert (ROOT / rel).is_file(), rel


def test_v2_7_warning_review_pass_no_warnings():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_7_WARNING_REVIEW_REPORT.json")
    assert report["status"] == "PASS"
    assert report["warning_review_completed"] is True
    assert report["warning_review_status"] == "NO_WARNINGS_FOUND"
    assert report["visible_warning_count"] == 0
    assert report["hidden_warning_count"] == 0
    assert report["critical_warning_count"] == 0
    assert report["warning_acceptance_required"] is False
    assert report["warning_suppression_performed"] is False


def test_v2_7_warning_review_blocks_missing_authority(tmp_path: Path):
    root = tmp_path / "CONTENT_ENGINE_OMEGA"
    root.mkdir()
    report = bridge.build_warning_review_report(root)
    assert report["status"] == "BLOCK"
    assert report["critical_warning_count"] > 0


def test_v2_7_gate_closure_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_7_GATE_CLOSURE_REPORT.json")
    assert report["status"] == "PASS"
    assert report["gate_closure_completed"] is True
    assert report["gate_closure_status"] == "CLOSED_WITH_NO_WARNINGS"
    assert report["post_execution_audit_allowed_next"] is False
    assert report["warning_review_or_gate_closure_allowed_next"] is False
    assert report["next_layer_blueprint_allowed_next"] is True


def test_v2_7_gate_closure_blocks_failed_warning_review():
    warning = bridge.base_report("warning", "BLOCK")
    report = bridge.build_gate_closure_report(warning)
    assert report["status"] == "BLOCK"
    assert report["gate_closure_completed"] is False


def test_v2_7_next_layer_readiness_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_7_NEXT_LAYER_READINESS_MAP.json")
    assert report["status"] == "PASS"
    assert report["next_layer_readiness_map_defined"] is True
    assert report["previous_gate_closed"] is True
    assert report["next_safe_step"] == "NEXT_BRIDGE_LAYER_BLUEPRINT"
    assert report["next_layer_blueprint_allowed_next"] is True
    assert report["next_layer_build_allowed_now"] is False


def test_v2_7_next_layer_readiness_blocks_unclosed_gate():
    closure = bridge.base_report("closure", "BLOCK")
    report = bridge.build_next_layer_readiness_map(closure)
    assert report["status"] == "BLOCK"
    assert report["next_layer_blueprint_allowed_next"] is False


def test_v2_7_no_touch_closure_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_NO_TOUCH_REPORT.json")
    assert report["status"] == "PASS"
    assert report["no_touch_pass"] is True
    assert report["no_touch_added"] == []
    assert report["no_touch_removed"] == []
    assert report["no_touch_changed"] == []


def test_v2_7_no_touch_closure_blocks_change():
    before = {"a": {"sha256": "1", "length": 1}}
    after = {"a": {"sha256": "2", "length": 1}}
    closure = bridge.base_report("closure", "PASS")
    report = bridge.build_no_touch_closure_report(before, after, closure)
    assert report["status"] == "BLOCK"
    assert report["no_touch_pass"] is False


def test_v2_7_watch_only_closure_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_WATCH_ONLY_REPORT.json")
    assert report["status"] == "PASS"
    assert report["watch_only_pass"] is True
    assert report["watch_only_added"] == []
    assert report["watch_only_removed"] == []
    assert report["watch_only_changed"] == []


def test_v2_7_watch_only_closure_blocks_change():
    before = {"a": {"sha256": "1", "length": 1}}
    after = {"a": {"sha256": "1", "length": 2}}
    closure = bridge.base_report("closure", "PASS")
    report = bridge.build_watch_only_closure_report(before, after, closure)
    assert report["status"] == "BLOCK"
    assert report["watch_only_pass"] is False


def test_v2_7_anti_simulation_closure_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_ANTI_SIMULATION_REPORT.json")
    assert report["status"] == "PASS"
    assert report["anti_simulation_closure"] == "PASS"
    assert report["violations"] == []


def test_v2_7_anti_simulation_blocks_build_allowed_next():
    bad = bridge.base_report("bad", "PASS")
    bad["build_allowed_next"] = True
    report = bridge.build_anti_simulation_closure_report([bad])
    assert report["status"] == "BLOCK"
    assert any("BUILD_ALLOWED_NEXT_TRUE" in item for item in report["violations"])


def test_v2_7_anti_simulation_blocks_warning_review_left_open():
    bad = bridge.base_report("bad", "PASS")
    bad["warning_review_or_gate_closure_allowed_next"] = True
    report = bridge.build_anti_simulation_closure_report([bad])
    assert report["status"] == "BLOCK"
    assert any("WARNING_REVIEW_LEFT_OPEN" in item for item in report["violations"])


def test_v2_7_closure_validation_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_VALIDATION_REPORT.json")
    assert report["status"] == "PASS"
    assert report["validation_status"] == "PASS"
    assert report["v2_7_gate_closed"] is True
    assert report["closure_status"] == "CLOSED_WITH_NO_WARNINGS"
    assert report["next_layer_blueprint_allowed_next"] is True
    assert report["next_layer_build_allowed_now"] is False


def test_v2_7_closure_manifest_pass():
    manifest = j("00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_MANIFEST.json")
    assert manifest["status"] == "PASS"
    paths = {item["path"] for item in manifest["artifacts"]}
    for rel in bridge.MANIFEST_TRACKED_ARTIFACTS:
        assert rel in paths
    assert all(item["sha256"] for item in manifest["artifacts"])


def test_v2_7_closure_seal_pass():
    seal = j("00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_SEAL.json")
    assert seal["status"] == "SEALED_AS_V2_7_GATE_CLOSED_AFTER_WARNING_REVIEW"
    assert seal["v2_7_gate_closed"] is True
    assert seal["gate_closure_status"] == "CLOSED_WITH_NO_WARNINGS"
    assert seal["post_execution_audit_allowed_next"] is False
    assert seal["warning_review_or_gate_closure_allowed_next"] is False
    assert seal["next_layer_blueprint_allowed_next"] is True


def test_v2_7_final_current_permissions_closed():
    for rel in [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_GATE_CLOSURE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_SEAL.json",
    ]:
        data = j(rel)
        assert data["build_allowed_now"] is False
        assert data["build_allowed_next"] is False
        assert data["post_execution_audit_allowed_next"] is False
        assert data["warning_review_or_gate_closure_allowed_next"] is False


def test_v2_7_next_blueprint_allowed_only():
    validation = j("00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_VALIDATION_REPORT.json")
    seal = j("00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_SEAL.json")
    assert validation["next_layer_blueprint_allowed_next"] is True
    assert seal["next_layer_blueprint_allowed_next"] is True
    assert validation["next_layer_build_allowed_now"] is False
    assert seal["next_layer_build_allowed_now"] is False
    assert validation["next_safe_step"] == "NEXT_BRIDGE_LAYER_BLUEPRINT"
    assert seal["next_safe_step"] == "NEXT_BRIDGE_LAYER_BLUEPRINT"


def test_v2_7_danger_always_false_on_generated_reports():
    for rel in [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_WARNING_REVIEW_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_GATE_CLOSURE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_7_CLOSURE_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_7_GATE_CLOSURE_SEAL.json",
    ]:
        assert bridge.danger_always_false(j(rel)) is True