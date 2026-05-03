from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).resolve().parents[2] / "04_SCRIPTS/python/manual_brain_bridge/v3_7_controlled_execution_readiness_gate.py"
spec = importlib.util.spec_from_file_location("v3_7_gate", MODULE_PATH)
gate = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(gate)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def make_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    return root


def valid_v36_payload() -> dict:
    return {
        "system": "CONTENT_ENGINE_OMEGA",
        "final_status": "CLOSED",
        "no_touch_status": "PASS",
        "warnings_accepted": 5,
        "warnings_inherited_visible": 5,
        "warnings_hidden": 0,
        "warnings_suppressed": 0,
        "warnings_resolved_by_v3_6": 0,
        "production_clean_pass": False,
        "production_with_warnings": True,
        "authorization_contract_created": True,
        "authorization_record_created": False,
        "human_authorization_input_received": False,
        "human_authorization_recorded": False,
        "human_authorization_valid": False,
        "execution_permission_granted": False,
        "execution_ready": False,
        "execution_performed": False,
        "external_execution_permission": False,
        "manual_write_permission": False,
        "brain_write_permission": False,
        "reports_brain_write_permission": False,
        "n8n_permission": False,
        "webhook_permission": False,
        "publishing_permission": False,
        "capa9_permission": False,
    }


def create_v36_artifacts(root: Path, payload: dict | None = None) -> None:
    data = payload or valid_v36_payload()
    for rel in gate.REQUIRED_V36_ARTIFACTS:
        write_json(root / rel, data)


def create_no_touch_files(root: Path) -> None:
    for rel in gate.NO_TOUCH_ROOTS:
        p = root / rel / "KEEP.txt"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("stable", encoding="utf-8")


def create_pre_baseline(root: Path) -> Path:
    pre = gate.capture_no_touch_baseline(root, "NO_TOUCH_HASH_BASELINE_PRE_V3_7")
    path = root / "00_SYSTEM/bridge/reports/NO_TOUCH_HASH_BASELINE_PRE_V3_7.json"
    gate.atomic_write_json(root, path, pre)
    return path


def valid_root(tmp_path: Path) -> tuple[Path, Path]:
    root = make_root(tmp_path)
    create_no_touch_files(root)
    create_v36_artifacts(root)
    pre = create_pre_baseline(root)
    return root, pre


def test_stable_json_deterministic():
    assert gate.stable_json_dumps({"b": 1, "a": 2}) == gate.stable_json_dumps({"a": 2, "b": 1})


def test_base_report_false_permissions():
    r = gate.base_report("X")
    assert r["execution_allowed"] is False
    assert r["manual_write_allowed"] is False
    assert r["brain_write_allowed"] is False
    assert r["reports_brain_write_allowed"] is False
    assert r["n8n_allowed"] is False
    assert r["webhook_allowed"] is False
    assert r["publishing_allowed"] is False
    assert r["capa9_allowed"] is False


def test_validate_v36_closed_pass():
    assert gate.validate_v3_6_closed({"a": valid_v36_payload()})["status"] == "PASS"


@pytest.mark.parametrize("field", ["final_status", "no_touch_status"])
def test_validate_v36_closed_blocks_missing_required_semantics(field):
    p = valid_v36_payload()
    p[field] = "FAIL"
    assert gate.validate_v3_6_closed({"a": p})["status"] == "BLOCK"


@pytest.mark.parametrize("field", gate.PERMISSION_FALSE_FIELDS)
def test_permission_elevation_locks(field):
    p = valid_v36_payload()
    p[field] = True
    result = gate.evaluate_permission_elevation({"a": p})
    assert result["status"] == "LOCK"
    assert field in result["elevated_fields"]


def test_permission_false_state_passes():
    assert gate.evaluate_permission_elevation({"a": valid_v36_payload()})["status"] == "PASS"


def test_permission_missing_blocks():
    p = valid_v36_payload()
    p.pop("execution_ready")
    assert gate.evaluate_permission_elevation({"a": p})["status"] == "BLOCK"


@pytest.mark.parametrize(
    "field,value,expected",
    [
        ("warnings_accepted", 4, "BLOCK"),
        ("warnings_inherited_visible", 4, "BLOCK"),
        ("production_clean_pass", True, "BLOCK"),
        ("production_with_warnings", False, "BLOCK"),
        ("warnings_hidden", 1, "LOCK"),
        ("warnings_suppressed", 1, "LOCK"),
    ],
)
def test_warning_integrity(field, value, expected):
    p = valid_v36_payload()
    p[field] = value
    assert gate.evaluate_warning_integrity({"a": p})["status"] == expected


def test_warning_integrity_passes():
    assert gate.evaluate_warning_integrity({"a": valid_v36_payload()})["status"] == "PASS"


def test_surface_map_future_not_allowed_now():
    s = gate.build_surface_map()["surface_map"]
    assert s["SURFACE_1_LOCAL_DRY_RUN"]["allowed_now"] is False
    assert s["SURFACE_5_EXTERNAL_API_CALL"]["blocked"] is True


def test_risk_tier_r10_locked():
    assert gate.build_risk_tier_map()["rules"]["R10"] == "locked"


def test_dry_run_not_executable():
    req = gate.build_dry_run_requirements()["requirements"]
    assert req["dry_run_required"] is True
    assert req["dry_run_execution_allowed"] is False


def test_rollback_not_executable():
    req = gate.build_rollback_requirements()["requirements"]
    assert req["rollback_required"] is True
    assert req["rollback_execution_allowed"] is False


def test_auth_readiness_not_valid_auth():
    auth = gate.build_auth_readiness_report()["authorization"]
    assert auth["authorization_ready_for_future_design"] is True
    assert auth["authorization_valid_now"] is False


def test_atomic_write_text(tmp_path):
    root = make_root(tmp_path)
    target = root / "00_SYSTEM/bridge/reports/x.txt"
    h = gate.atomic_write_text(root, target, "hello\n")
    assert target.exists()
    assert gate.sha256_file(target) == h


def test_atomic_write_json(tmp_path):
    root = make_root(tmp_path)
    target = root / "00_SYSTEM/bridge/reports/x.json"
    gate.atomic_write_json(root, target, {"b": 1, "a": 2})
    assert json.loads(target.read_text(encoding="utf-8")) == {"a": 2, "b": 1}


@pytest.mark.parametrize(
    "target_rel",
    [
        "00_SYSTEM/brain/x.json",
        "00_SYSTEM/reports/brain/x.json",
        "00_SYSTEM/manual/current/x.md",
        "00_SYSTEM/manual/historical/x.md",
        "00_SYSTEM/manual/manifest/x.json",
        "00_SYSTEM/manual/registry/x.json",
    ],
)
def test_atomic_write_blocks_no_touch_roots(tmp_path, target_rel):
    root = make_root(tmp_path)
    target = root / target_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    with pytest.raises(gate.GateError):
        gate.atomic_write_text(root, target, "x")


@pytest.mark.parametrize("bad_rel", ["../outside.json", "..\\outside.json"])
def test_path_traversal_locks(tmp_path, bad_rel):
    root = make_root(tmp_path)
    with pytest.raises(gate.GateError):
        gate.assert_path_inside_root(root, root / bad_rel)


def test_no_touch_compare_passes(tmp_path):
    root = make_root(tmp_path)
    create_no_touch_files(root)
    pre = gate.capture_no_touch_baseline(root, "PRE")
    post = gate.capture_no_touch_baseline(root, "POST")
    assert gate.compare_no_touch_baselines(pre, post)["status"] == "PASS"


@pytest.mark.parametrize("mode", ["changed", "added", "removed"])
def test_no_touch_compare_locks_changes(tmp_path, mode):
    root = make_root(tmp_path)
    create_no_touch_files(root)
    pre = gate.capture_no_touch_baseline(root, "PRE")

    if mode == "changed":
        (root / "00_SYSTEM/brain/KEEP.txt").write_text("changed", encoding="utf-8")
    elif mode == "added":
        (root / "00_SYSTEM/brain/NEW.txt").write_text("new", encoding="utf-8")
    else:
        (root / "00_SYSTEM/brain/KEEP.txt").unlink()

    post = gate.capture_no_touch_baseline(root, "POST")
    assert gate.compare_no_touch_baselines(pre, post)["status"] == "LOCK"


@pytest.mark.parametrize(
    "field",
    [
        "execution_allowed",
        "manual_write_allowed",
        "brain_write_allowed",
        "reports_brain_write_allowed",
        "n8n_allowed",
        "webhook_allowed",
        "publishing_allowed",
        "capa9_allowed",
    ],
)
def test_validate_contract_rejects_true_permissions(field):
    r = gate.base_report("X")
    r[field] = True
    assert any(field in e for e in gate.validate_contract(r))


def test_validate_contract_rejects_execution_next_step():
    r = gate.base_report("X")
    r["next_safe_step"] = "EXECUTION"
    assert "next_safe_step_points_to_execution" in gate.validate_contract(r)


def test_ast_scan_current_module_passes():
    assert gate.ast_security_scan(MODULE_PATH)["status"] == "PASS"


@pytest.mark.parametrize("source", ["import subprocess\n", "import requests\n", "import socket\n", "import urllib\n", "import http\n"])
def test_ast_scan_locks_forbidden_imports(tmp_path, source):
    f = tmp_path / "bad.py"
    f.write_text(source, encoding="utf-8")
    assert gate.ast_security_scan(f)["status"] == "LOCK"


@pytest.mark.parametrize("source", ["eval('1')\n", "exec('x=1')\n", "compile('1','x','exec')\n", "__import__('os')\n"])
def test_ast_scan_locks_forbidden_calls(tmp_path, source):
    f = tmp_path / "bad.py"
    f.write_text(source, encoding="utf-8")
    assert gate.ast_security_scan(f)["status"] == "LOCK"


@pytest.mark.parametrize("source", ["import random\n", "import uuid\n", "import secrets\n"])
def test_ast_scan_locks_nondeterminism(tmp_path, source):
    f = tmp_path / "bad.py"
    f.write_text(source, encoding="utf-8")
    assert gate.ast_security_scan(f)["status"] == "LOCK"


def test_load_v36_evidence_missing_blocks(tmp_path):
    with pytest.raises(gate.GateError):
        gate.load_v3_6_evidence(make_root(tmp_path))


def test_load_v36_evidence_present(tmp_path):
    root = make_root(tmp_path)
    create_v36_artifacts(root)
    assert len(gate.load_v3_6_evidence(root)) == len(gate.REQUIRED_V36_ARTIFACTS)


def test_generate_reports_success(tmp_path):
    root, pre = valid_root(tmp_path)
    assert gate.generate_reports(root, pre) == gate.EXIT_PASS
    assert (root / gate.REPORTS["main"]).exists()
    assert (root / gate.REPORTS["no_touch_diff"]).exists()


def test_generate_reports_locks_permission(tmp_path):
    root = make_root(tmp_path)
    create_no_touch_files(root)
    p = valid_v36_payload()
    p["execution_permission_granted"] = True
    create_v36_artifacts(root, p)
    pre = create_pre_baseline(root)
    assert gate.generate_reports(root, pre) == gate.EXIT_LOCK


def test_generate_reports_blocks_false_clean(tmp_path):
    root = make_root(tmp_path)
    create_no_touch_files(root)
    p = valid_v36_payload()
    p["production_clean_pass"] = True
    create_v36_artifacts(root, p)
    pre = create_pre_baseline(root)
    assert gate.generate_reports(root, pre) == gate.EXIT_BLOCK


def test_validate_outputs_passes_after_generation(tmp_path):
    root, pre = valid_root(tmp_path)
    assert gate.generate_reports(root, pre) == gate.EXIT_PASS
    assert gate.validate_outputs(root) == gate.EXIT_PASS


def test_finalize_manifest_and_seal_blocks_missing_expected(tmp_path):
    root = make_root(tmp_path)
    with pytest.raises(gate.GateError):
        gate.finalize_manifest_and_seal(root)