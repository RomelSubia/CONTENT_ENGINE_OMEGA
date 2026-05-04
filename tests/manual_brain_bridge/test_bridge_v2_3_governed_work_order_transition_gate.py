from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BRIDGE_PATH = ROOT / "04_SCRIPTS/python/manual_brain_bridge/bridge_v2_3_governed_work_order_transition_gate.py"

spec = importlib.util.spec_from_file_location("bridge_v2_3", BRIDGE_PATH)
bridge = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(bridge)


def j(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_v2_3_generated_reports_exist():
    for rel in [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_AUTHORITY_HASH_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_HISTORICAL_AUTHORITY_RESOLUTION_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_RECOVERY_READINESS_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_ANTI_SIMULATION_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_GOVERNED_WORK_ORDER_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_TRANSITION_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_BLOCKED_CAPABILITIES_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_3_ARTIFACT_MANIFEST.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_3_GOVERNED_WORK_ORDER_SEAL.json",
    ]:
        assert (ROOT / rel).is_file(), rel


def test_v2_3_authority_hash_report_is_pass_with_hashes():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_3_AUTHORITY_HASH_REPORT.json")
    assert report["status"] == "PASS"
    assert report["authority_hash_check"] == "PASS"
    assert report["authority_hashes"]
    assert all(report["authority_hashes"].values())


def test_v2_3_historical_authority_cannot_override_current_state():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_3_HISTORICAL_AUTHORITY_RESOLUTION_REPORT.json")
    assert report["status"] == "PASS"
    classes = {item["authority_id"]: item["classification"] for item in report["historical_authority_resolution"]}
    assert classes["BRIDGE_V1_GATE_CLOSURE_REPORT"] == "HISTORICAL_SUPERSEDED"
    assert classes["BRIDGE_V2_2_CONTEXT_ALIGNMENT_SEAL"] == "CURRENT_PRIMARY_AUTHORITY"
    assert report["historical_override_allowed"] is False


def test_v2_3_recovery_report_is_closable():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_3_RECOVERY_READINESS_REPORT.json")
    assert report["status"] == "PASS"
    assert report["recovery_state"] in {"NO_PARTIAL_STATE", "PARTIAL_ALLOWED_RECOVERY"}


def test_v2_3_anti_simulation_gate_is_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_3_ANTI_SIMULATION_GATE_REPORT.json")
    assert report["status"] == "PASS"
    assert report["violations"] == []


def test_v2_3_work_order_separates_next_from_now():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_3_GOVERNED_WORK_ORDER_REPORT.json")
    assert report["status"] == "PASS"
    assert report["blueprint_allowed"] is True
    assert report["implementation_plan_allowed"] is True
    assert report["build_block_allowed_next"] is True
    assert report["build_allowed_next"] is True
    assert report["build_allowed_now"] is False
    assert report["execution_allowed"] is False


def test_v2_3_transition_gate_is_safe():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_3_TRANSITION_GATE_REPORT.json")
    assert report["status"] == "PASS"
    assert report["transition_allowed"] is True
    assert report["next_bridge_layer_build_block_allowed_next"] is True
    assert report["next_bridge_layer_build_allowed_now"] is False
    assert report["brain_write_allowed"] is False
    assert report["manual_write_allowed"] is False
    assert report["capa9_allowed"] is False


def test_v2_3_blocked_capabilities_include_manual_auto_update_and_external_runtime():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_3_BLOCKED_CAPABILITIES_REPORT.json")
    blocked = set(report["blocked_capabilities"])
    for item in [
        "MANUAL_AUTO_UPDATE",
        "MANUAL_CURRENT_MUTATION",
        "MANUAL_MANIFEST_MUTATION",
        "BRAIN_WRITE",
        "N8N_EXECUTION",
        "WEBHOOK_EXECUTION",
        "PUBLISHING",
        "OPENAI_API_RUNTIME",
        "CAPA9",
    ]:
        assert item in blocked
    assert report["manual_auto_update_allowed"] is False
    assert report["manual_current_mutation_allowed"] is False
    assert report["manual_manifest_mutation_allowed"] is False


def test_v2_3_validation_report_is_pass():
    report = j("00_SYSTEM/bridge/reports/BRIDGE_V2_3_VALIDATION_REPORT.json")
    assert report["status"] == "PASS"
    assert report["validation_status"] == "PASS"
    assert report["build_allowed_next"] is True
    assert report["build_allowed_now"] is False
    assert report["external_execution"] == "DISABLED"
    assert report["brain_mutation"] == "BLOCKED"
    assert report["manual_mutation"] == "BLOCKED"
    assert report["auto_action"] is False


def test_v2_3_manifest_tracks_generated_artifacts_without_self_reference():
    manifest = j("00_SYSTEM/bridge/manifests/BRIDGE_V2_3_ARTIFACT_MANIFEST.json")
    assert manifest["status"] == "PASS"
    paths = {item["path"] for item in manifest["artifacts"]}
    for rel in bridge.MANIFEST_TRACKED_ARTIFACTS:
        assert rel in paths
    omitted = set(manifest["omitted_self_referential_artifacts"])
    assert "00_SYSTEM/bridge/manifests/BRIDGE_V2_3_ARTIFACT_MANIFEST.json" in omitted
    assert "00_SYSTEM/bridge/manifests/BRIDGE_V2_3_GOVERNED_WORK_ORDER_SEAL.json" in omitted
    assert all(item["sha256"] for item in manifest["artifacts"])


def test_v2_3_seal_is_final_transition_gate_seal():
    seal = j("00_SYSTEM/bridge/manifests/BRIDGE_V2_3_GOVERNED_WORK_ORDER_SEAL.json")
    assert seal["status"] == "SEALED_AS_GOVERNED_WORK_ORDER_TRANSITION_GATE_V2_3"
    assert seal["bridge_v2_2_context_alignment_authority"] is True
    assert seal["runtime_warning_closed_clean"] is True
    assert seal["build_allowed_next"] is True
    assert seal["build_allowed_now"] is False
    assert seal["execution_allowed"] is False


def test_v2_3_negative_intents_are_blocked():
    cases = {
        "crear el bloque y ejecutarlo": "BLOCK_AUTO_ACTION_REQUEST",
        "activa n8n después": "BLOCK_N8N_REQUEST",
        "publicar automáticamente": "BLOCK_PUBLISHING_REQUEST",
        "usar OpenAI API runtime": "BLOCK_OPENAI_API_RUNTIME_REQUEST",
        "modificar el cerebro si hace falta": "LOCK_BRAIN_MUTATION_REQUEST",
        "actualiza el manual current": "BLOCK_MANUAL_MUTATION_REQUEST",
        "corrige el manual automáticamente": "BLOCK_MANUAL_MUTATION_REQUEST",
        "crear capa 9": "LOCK_CAPA9_REQUEST",
        "ejecutar webhook": "BLOCK_WEBHOOK_REQUEST",
        "subir contenido a redes": "BLOCK_PUBLISHING_REQUEST",
    }

    for text, decision in cases.items():
        result = bridge.resolve_request_intent(text)
        assert result["allowed"] is False
        assert result["decision"] == decision


def test_v2_3_current_controlled_build_request_is_allowed():
    result = bridge.resolve_request_intent("BLOQUE AUTOMÁTICO v2.3 governed work order transition gate")
    assert result["allowed"] is True
    assert result["decision"] == "ALLOW_GOVERNED_WORK_ORDER_BUILD"


def test_v2_3_authority_report_fails_closed_when_authority_missing(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()
    report = bridge.build_authority_hash_report(root)
    assert report["status"] == "BLOCK"
    assert report["missing_authority_files"]


def test_v2_3_danger_flags_false_on_generated_reports():
    for rel in [
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_AUTHORITY_HASH_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_GOVERNED_WORK_ORDER_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_TRANSITION_GATE_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_BLOCKED_CAPABILITIES_REPORT.json",
        "00_SYSTEM/bridge/reports/BRIDGE_V2_3_VALIDATION_REPORT.json",
        "00_SYSTEM/bridge/manifests/BRIDGE_V2_3_GOVERNED_WORK_ORDER_SEAL.json",
    ]:
        assert bridge.danger_flags_false(j(rel)) is True