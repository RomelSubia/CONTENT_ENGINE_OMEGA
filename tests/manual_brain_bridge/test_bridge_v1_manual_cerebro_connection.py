from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).resolve().parents[2] / "04_SCRIPTS/python/manual_brain_bridge/bridge_v1_manual_cerebro_connection.py"
spec = importlib.util.spec_from_file_location("bridge_v1", MODULE_PATH)
bridge = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(bridge)


def make_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    return root


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def write_v37_closure(root: Path) -> None:
    write_json(root / "00_SYSTEM/bridge/reports/AUXILIARY_LAYER_FREEZE_CLOSURE_V3_7.json", {
        "system": "CONTENT_ENGINE_OMEGA",
        "v3_7_status": "CLOSED_AS_AUXILIARY_READINESS_GATE",
        "does_replace_bridge_v1": False,
        "next_safe_step": "BLOQUE_AUTOMATICO_V1_CAPA_CONEXION_MANUAL_CEREBRO_PRODUCTION_REAL",
    })
    write_json(root / "00_SYSTEM/bridge/reports/DEVIATION_RETURN_MAP_V3_7.json", {
        "system": "CONTENT_ENGINE_OMEGA",
        "does_replace_bridge_v1": False,
        "bridge_v1_implemented": False,
    })
    write_json(root / "00_SYSTEM/bridge/reports/NEXT_STEP_RETURN_TO_ORIGINAL_PLAN_V3_7.json", {
        "system": "CONTENT_ENGINE_OMEGA",
        "allowed_next_command": "BLOQUE_AUTOMATICO_V1_CAPA_CONEXION_MANUAL_CEREBRO",
    })


def write_manual(root: Path, text: str = "# Manual\n\nRegla: NO CAPA 9\n") -> str:
    manual = root / bridge.MANUAL_PATH
    manual.parent.mkdir(parents=True, exist_ok=True)
    manual.write_text(text, encoding="utf-8")
    return bridge.sha256_file(manual)


def write_manual_manifest(root: Path, manual_hash: str) -> None:
    write_json(root / bridge.MANUAL_MANIFEST_PATH, {
        "system": "CONTENT_ENGINE_OMEGA",
        "manual_sha256": manual_hash,
        "status": "CURRENT_VALID",
    })


def valid_runtime_root(tmp_path: Path) -> Path:
    root = make_root(tmp_path)
    write_v37_closure(root)
    h = write_manual(root)
    write_manual_manifest(root, h)
    return root


def test_stable_json_is_deterministic():
    assert bridge.stable_json({"b": 1, "a": 2}) == bridge.stable_json({"a": 2, "b": 1})


def test_sha256_text_is_stable():
    assert bridge.sha256_text("abc") == bridge.sha256_text("abc")


@pytest.mark.parametrize("key,value", bridge.NO_WRITE_FLAGS.items())
def test_base_report_security_flags_false(key, value):
    report = bridge.base_report("X")
    assert report[key] is value


def test_validate_v37_closure_pass(tmp_path):
    root = make_root(tmp_path)
    write_v37_closure(root)
    assert bridge.validate_v37_closure(root)["status"] == "PASS"


def test_validate_v37_closure_blocks_missing(tmp_path):
    root = make_root(tmp_path)
    assert bridge.validate_v37_closure(root)["status"] == "BLOCK"


def test_source_resolver_current_valid(tmp_path):
    root = valid_runtime_root(tmp_path)
    report = bridge.source_resolver(root)
    assert report["status"] == "PASS"
    assert report["source_status"] == "CURRENT_VALID"


def test_source_resolver_manual_missing_requires_review(tmp_path):
    root = make_root(tmp_path)
    write_v37_closure(root)
    report = bridge.source_resolver(root)
    assert report["status"] == "REQUIRE_REVIEW"


def test_source_resolver_manifest_missing_requires_review(tmp_path):
    root = make_root(tmp_path)
    write_v37_closure(root)
    write_manual(root)
    report = bridge.source_resolver(root)
    assert report["status"] == "REQUIRE_REVIEW"


def test_source_resolver_hash_mismatch_requires_review(tmp_path):
    root = make_root(tmp_path)
    write_v37_closure(root)
    write_manual(root)
    write_manual_manifest(root, "bad")
    report = bridge.source_resolver(root)
    assert report["status"] == "REQUIRE_REVIEW"


def test_manual_integrity_pass(tmp_path):
    root = valid_runtime_root(tmp_path)
    source = bridge.source_resolver(root)
    report = bridge.manual_integrity_guard(root, source)
    assert report["status"] == "PASS"


def test_manual_integrity_detects_chat_noise(tmp_path):
    root = make_root(tmp_path)
    write_v37_closure(root)
    h = write_manual(root, "PS D:\\CONTENT_ENGINE_OMEGA> git status")
    write_manual_manifest(root, h)
    source = bridge.source_resolver(root)
    report = bridge.manual_integrity_guard(root, source)
    assert report["status"] == "REQUIRE_REVIEW"
    assert report["runtime_manual_review_required"] is True


def test_rule_extractor_has_required_rules(tmp_path):
    root = make_root(tmp_path)
    registry, extraction = bridge.rule_extractor(root)
    assert registry["rule_count"] >= 8
    assert extraction["status"] == "PASS"


@pytest.mark.parametrize(
    "user_request,expected",
    [
        ("crear capa 9", "BLOCK"),
        ("usar webhook externo", "BLOCK"),
        ("modifica cerebro", "BLOCK"),
        ("skip validation", "BLOCK"),
        ("build bridge v1", "PASS"),
    ],
)
def test_intent_classifier(user_request, expected):
    assert bridge.classify_intent(user_request)["status"] == expected


def test_conflict_detector_passes_allowed_request():
    intent = bridge.classify_intent("build bridge v1")
    assert bridge.conflict_detector(intent)["status"] == "PASS"


def test_conflict_detector_blocks_bad_request():
    intent = bridge.classify_intent("crear capa 9")
    assert bridge.conflict_detector(intent)["status"] == "BLOCK"


def test_brain_read_only_check_never_writes(tmp_path):
    root = make_root(tmp_path)
    report = bridge.brain_read_only_check(root)
    assert report["brain_write_attempted"] is False
    assert report["status"] == "PASS"


def test_decision_mapper_allows_safe_intent():
    intent = bridge.classify_intent("build bridge v1")
    conflict = bridge.conflict_detector(intent)
    report = bridge.decision_mapper(intent, conflict)
    assert report["decision"] == "ALLOW_IMPLEMENTATION_PLAN"


def test_decision_mapper_blocks_conflict():
    intent = bridge.classify_intent("crear capa 9")
    conflict = bridge.conflict_detector(intent)
    report = bridge.decision_mapper(intent, conflict)
    assert report["decision"] == "BLOCK"


def test_plan_builder_never_allows_action():
    decision = {"decision": "ALLOW_IMPLEMENTATION_PLAN"}
    report = bridge.controlled_plan_builder(decision)
    assert report["PLAN_ALLOWED"] is True
    assert report["ACTION_ALLOWED"] is False
    assert report["EXECUTION_ALLOWED"] is False


def test_traceability_matrix_complete():
    matrix = bridge.traceability_matrix({"A": bridge.base_report("A")})
    assert matrix["traceability_complete"] is True
    assert "USER_REQUEST" in matrix["chain"]


def test_build_readiness_passes_without_block():
    readiness = bridge.build_readiness_report({"A": bridge.base_report("A")})
    assert readiness["build_allowed"] is True
    assert readiness["status"] == "PASS"


def test_validation_report_disables_execution():
    report = bridge.validation_report({"A": bridge.base_report("A")})
    assert report["EXTERNAL_EXECUTION"] == "DISABLED"
    assert report["BRAIN_MUTATION"] == "BLOCKED"


@pytest.mark.parametrize(
    "key",
    [
        "execution_allowed",
        "external_execution_allowed",
        "manual_write_allowed",
        "brain_write_allowed",
        "reports_brain_write_allowed",
        "n8n_allowed",
        "webhook_allowed",
        "publishing_allowed",
        "capa9_allowed",
        "auto_action_allowed",
    ],
)
def test_contract_validation_rejects_true_security_flags(key):
    report = bridge.base_report("X")
    report[key] = True
    assert bridge.validate_contract(report)


@pytest.mark.parametrize("bad_path", ["../x.json", "..\\x.json"])
def test_path_traversal_locks(tmp_path, bad_path):
    root = make_root(tmp_path)
    with pytest.raises(bridge.BridgeError):
        bridge.assert_inside_root(root, root / bad_path)


@pytest.mark.parametrize(
    "blocked_rel",
    [
        "00_SYSTEM/brain/x.json",
        "00_SYSTEM/reports/brain/x.json",
        "00_SYSTEM/manual/current/x.md",
        "00_SYSTEM/manual/historical/x.md",
        "00_SYSTEM/manual/manifest/x.json",
        "00_SYSTEM/manual/registry/x.json",
    ],
)
def test_atomic_write_blocks_protected_paths(tmp_path, blocked_rel):
    root = make_root(tmp_path)
    target = root / blocked_rel
    target.parent.mkdir(parents=True, exist_ok=True)
    with pytest.raises(bridge.BridgeError):
        bridge.atomic_write_text(root, target, "x")


def test_atomic_write_allowed_bridge_report(tmp_path):
    root = make_root(tmp_path)
    target = root / "00_SYSTEM/bridge/reports/x.json"
    bridge.atomic_write_text(root, target, "{}\n")
    assert target.exists()


def test_generate_reports_success_valid_runtime(tmp_path):
    root = valid_runtime_root(tmp_path)
    code = bridge.generate(root, "build bridge v1")
    assert code == bridge.EXIT_PASS
    assert (root / "00_SYSTEM/bridge/reports/BRIDGE_BUILD_READINESS_REPORT.json").exists()


def test_generate_blocks_when_v37_missing(tmp_path):
    root = make_root(tmp_path)
    assert bridge.generate(root, "build bridge v1") == bridge.EXIT_BLOCK


def test_validate_outputs_after_generation(tmp_path):
    root = valid_runtime_root(tmp_path)
    assert bridge.generate(root, "build bridge v1") == bridge.EXIT_PASS
    assert bridge.validate_outputs(root) == bridge.EXIT_PASS