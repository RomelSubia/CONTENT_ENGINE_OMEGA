from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[2] / "04_SCRIPTS" / "python" / "manual_brain_bridge" / "bridge_block_2_schemas_policies_contracts.py"
SPEC = importlib.util.spec_from_file_location("block2", MODULE_PATH)
block2 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(block2)


@pytest.mark.parametrize("schema_id", block2.SCHEMA_IDS)
def test_required_schema_ids_exist(schema_id):
    assert schema_id in {schema["schema_id"] for schema in block2.build_schema_registry()["schemas"]}


@pytest.mark.parametrize("policy_id", block2.POLICY_IDS)
def test_required_policy_ids_exist(policy_id):
    assert policy_id in {policy["policy_id"] for policy in block2.build_policy_registry()["policies"]}


@pytest.mark.parametrize("contract_id", block2.CONTRACT_IDS)
def test_required_contract_ids_exist(contract_id):
    assert contract_id in {contract["contract_id"] for contract in block2.build_contract_registry()["contracts"]}


@pytest.mark.parametrize("error_code", block2.STABLE_ERROR_CODES)
def test_stable_error_codes_are_accepted(error_code):
    assert block2.make_error(error_code, "HIGH", "BLOCK", "STATE", "h", "t", "safe")["error_code"] == error_code


@pytest.mark.parametrize("version", ["1.0.0", "0.1.2", "10.20.30", "2.0.1", "3.4.5"])
def test_valid_semver(version):
    assert block2.is_semver(version)


@pytest.mark.parametrize("version", ["", "1", "1.0", "v1.0.0", "01.0.0", "1.0.x", "1.0.0-beta"])
def test_invalid_semver(version):
    assert not block2.is_semver(version)


@pytest.mark.parametrize("decisions,expected", [
    (["PASS", "BLOCK"], "BLOCK"),
    (["PASS_WITH_WARNINGS", "REQUIRE_REVIEW"], "REQUIRE_REVIEW"),
    (["LOCK", "PASS"], "LOCK"),
    (["PASS"], "PASS"),
    ([], "BLOCK"),
    (["UNKNOWN"], "LOCK"),
])
def test_policy_precedence(decisions, expected):
    assert block2.resolve_policy_precedence(decisions) == expected


def test_schema_registry_self_validation_passes():
    assert block2.validate_schema_registry(block2.build_schema_registry())["status"] == "PASS"


def test_schema_registry_missing_id_blocks():
    registry = block2.build_schema_registry()
    registry["schemas"][0] = dict(registry["schemas"][0])
    registry["schemas"][0].pop("schema_id")
    assert block2.validate_schema_registry(registry)["status"] in {"BLOCK", "LOCK"}


def test_schema_registry_invalid_unknown_policy_locks():
    registry = block2.build_schema_registry()
    registry["schemas"][0] = dict(registry["schemas"][0])
    registry["schemas"][0]["unknown_field_policy"] = "ALLOW"
    assert block2.validate_schema_registry(registry)["status"] == "LOCK"


def test_policy_registry_self_validation_passes():
    assert block2.validate_policy_registry(block2.build_policy_registry())["status"] == "PASS"


def test_policy_registry_not_fail_closed_locks():
    registry = block2.build_policy_registry()
    registry["policies"][0] = dict(registry["policies"][0])
    registry["policies"][0]["fail_closed"] = False
    assert block2.validate_policy_registry(registry)["status"] == "LOCK"


def test_contract_registry_self_validation_passes():
    assert block2.validate_contract_registry(block2.build_contract_registry())["status"] == "PASS"


def test_contract_forbidden_output_locks():
    contract = block2.build_contract_registry()["contracts"][0]
    assert block2.validate_contract_compatibility(contract, "ExecutionOutputContract")["status"] == "LOCK"


@pytest.mark.parametrize("permission,term", [
    ("execution_allowed", "execute"),
    ("manual_write_allowed", "patch_manual"),
    ("brain_write_allowed", "mutate_brain"),
    ("reports_brain_write_allowed", "reports_brain_write"),
    ("n8n_allowed", "call_n8n"),
    ("webhook_allowed", "call_webhook"),
    ("publishing_allowed", "publish"),
    ("capa9_allowed", "capa9"),
])
def test_false_permission_injection_locks(permission, term):
    permissions = block2.permission_model_false_by_default()
    payload = {"permissions": permissions, "capabilities": [term]}
    assert block2.detect_false_permission_injection(payload)["status"] == "LOCK"


def test_false_permission_injection_passes_for_safe_payload():
    permissions = block2.permission_model_false_by_default()
    payload = {"permissions": permissions, "capabilities": ["validate_schema"]}
    assert block2.detect_false_permission_injection(payload)["status"] == "PASS"


@pytest.mark.parametrize("path", [
    "../escape.json",
    "..\\escape.json",
    "/tmp/escape.json",
    "C:/Windows/system32/file.txt",
])
def test_path_escape_rejected(tmp_path, path):
    with pytest.raises(block2.Block2Error):
        block2.assert_inside_root(tmp_path, path)


@pytest.mark.parametrize("path", [
    "00_SYSTEM/brain/x.json",
    "00_SYSTEM/reports/brain/x.json",
    "00_SYSTEM/manual/current/x.md",
    "00_SYSTEM/manual/historical/x.md",
    "00_SYSTEM/manual/manifest/x.json",
    "00_SYSTEM/manual/registry/x.json",
])
def test_no_touch_path_detected(path):
    assert block2.detect_no_touch_path(path)


@pytest.mark.parametrize("path", [
    "00_SYSTEM/bridge/schemas/x.json",
    "04_SCRIPTS/python/manual_brain_bridge/x.py",
    "tests/manual_brain_bridge/x.py",
])
def test_safe_paths_normalize(tmp_path, path):
    assert block2.normalize_relative_path(tmp_path, path) == path


@pytest.mark.parametrize("source", [
    "import subprocess\n",
    "from requests import get\n",
    "import httpx\n",
    "import socket\n",
    "import webbrowser\n",
    "import ftplib\n",
    "import smtplib\n",
    "__import__('os')\n",
])
def test_dangerous_imports_lock(source):
    assert block2.scan_for_dangerous_imports(source)["status"] == "LOCK"


@pytest.mark.parametrize("source", [
    "import json\n",
    "from pathlib import Path\n",
    "def f():\n    return 1\n",
])
def test_safe_imports_pass(source):
    assert block2.scan_for_dangerous_imports(source)["status"] == "PASS"


@pytest.mark.parametrize("source", [
    "def f(x):\n    return urlopen(x)\n",
    "def f(x):\n    return client.sendmail(x)\n",
    "def f(s):\n    return s.connect(('localhost', 80))\n",
    "def f(c):\n    return c.request('GET', '/')\n",
])
def test_external_io_calls_lock(source):
    assert block2.scan_for_external_io(source)["status"] == "LOCK"


def test_no_external_io_in_safe_source():
    assert block2.scan_for_external_io("def f():\n    return 'safe'\n")["status"] == "PASS"


@pytest.mark.parametrize("text", [
    "api_key='abc123456'",
    "password = \"letmein\"",
    "private_key='-----BEGIN KEY-----'",
    "Authorization: Bearer abc.def.ghi",
    "sk-1234567890abcdef",
])
def test_secret_leakage_locks(text):
    assert block2.scan_for_secret_leakage(text)["status"] == "LOCK"


def test_safe_text_has_no_secret_leakage():
    assert block2.scan_for_secret_leakage("schema registry report")["status"] == "PASS"


def test_stable_json_has_final_newline_and_sorted_keys():
    text = block2.stable_json_dumps({"b": 1, "a": 2})
    assert text.endswith("\n")
    assert text.splitlines()[1].strip().startswith('"a"')
    assert block2.validate_canonical_json(text)


def test_canonical_hash_is_stable():
    value = {"z": [3, 2, 1], "a": {"b": True}}
    assert block2.canonical_json_hash(value) == block2.canonical_json_hash(value)


def test_non_canonical_json_rejected():
    assert not block2.validate_canonical_json('{"b":1,"a":2}')


def test_all_artifact_texts_are_allowlisted():
    assert set(block2.build_all_artifact_texts()).issubset(set(block2.ALLOWED_OUTPUTS))


def test_all_json_artifact_texts_are_canonical():
    for path, text in block2.build_all_artifact_texts().items():
        if path.endswith(".json"):
            assert block2.validate_canonical_json(text)


def test_artifact_texts_have_no_secret_leakage():
    for text in block2.build_all_artifact_texts().values():
        assert block2.scan_for_secret_leakage(text)["status"] == "PASS"


def test_manifest_and_seal_are_reproducible():
    first = block2.build_all_artifact_texts()
    second = block2.build_all_artifact_texts()
    assert first["00_SYSTEM/bridge/manifests/BRIDGE_BLOCK_2_MANIFEST.json"] == second["00_SYSTEM/bridge/manifests/BRIDGE_BLOCK_2_MANIFEST.json"]
    assert first["00_SYSTEM/bridge/manifests/BRIDGE_BLOCK_2_SEAL.json"] == second["00_SYSTEM/bridge/manifests/BRIDGE_BLOCK_2_SEAL.json"]


def test_write_and_validate_outputs(tmp_path):
    assert block2.write_all_allowed_artifacts(tmp_path)["status"] == "PASS"
    assert block2.validate_outputs(tmp_path)["status"] == "PASS"


def test_validate_outputs_detects_tampering(tmp_path):
    block2.write_all_allowed_artifacts(tmp_path)
    target = tmp_path / "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_2_VALIDATION_REPORT.json"
    target.write_text('{"tampered": true}\n', encoding="utf-8")
    assert block2.validate_outputs(tmp_path)["status"] in {"BLOCK", "LOCK"}


def test_decision_envelope_has_forbidden_actions():
    decision = block2.make_decision("PASS", "TEST")
    assert "execution" in decision["forbidden_actions"]
    assert decision["next_safe_step"] == block2.NEXT_SAFE_STEP


def test_error_envelope_cannot_pass():
    with pytest.raises(block2.Block2Error):
        block2.make_error("B2_CAPA9_LOCK", "CRITICAL", "PASS", "STATE", "bad", "bad", "stop")


def test_unknown_error_code_rejected():
    with pytest.raises(block2.Block2Error):
        block2.make_error("UNKNOWN", "CRITICAL", "LOCK", "STATE", "bad", "bad", "stop")


def test_permission_model_false_by_default():
    model = block2.permission_model_false_by_default()
    assert model
    assert all(value is False for value in model.values())


def test_next_layer_readiness_does_not_allow_block_3():
    report = block2.build_all_artifact_texts()["00_SYSTEM/bridge/reports/BRIDGE_BLOCK_2_NEXT_LAYER_READINESS_MAP.json"]
    loaded = json.loads(report)
    assert loaded["block_3_allowed_now"] is False
    assert loaded["next_safe_step"] == block2.NEXT_SAFE_STEP


def test_security_report_keeps_capa9_locked():
    report = block2.build_all_artifact_texts()["00_SYSTEM/bridge/reports/BRIDGE_BLOCK_2_SECURITY_GUARDS_REPORT.json"]
    loaded = json.loads(report)
    assert loaded["guards"]["capa9"] == "LOCKED"


def test_current_module_has_no_dangerous_imports():
    assert block2.scan_for_dangerous_imports(MODULE_PATH.read_text(encoding="utf-8"))["status"] == "PASS"


def test_current_module_has_no_external_io_calls():
    assert block2.scan_for_external_io(MODULE_PATH.read_text(encoding="utf-8"))["status"] == "PASS"