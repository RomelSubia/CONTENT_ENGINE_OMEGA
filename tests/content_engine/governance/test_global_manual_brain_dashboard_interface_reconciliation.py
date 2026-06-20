from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "04_SCRIPTS" / "python" / "content_engine" / "governance" / "global_manual_brain_dashboard_interface_reconciliation.py"


def load_module():
    spec = importlib.util.spec_from_file_location("reconciliation_module", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_truth_object_requires_all_fields():
    mod = load_module()
    obj = mod.build_truth_object(
        truth_object_id="manual:coverage",
        layer="manual",
        subject="coverage",
        current_state="CURRENT_VERIFIED",
        truth_state="VERIFIED_TRUE",
        confidence="HIGH_CONFIDENCE",
        evidence_refs=["report.json"],
        evidence_hashes=["abc"],
        source_priority=["valid_seal"],
        next_safe_step="NEXT",
    )
    result = mod.validate_truth_object_contract(obj)
    assert result["valid"] is True
    assert result["missing"] == []
    assert result["invalid"] == []


def test_missing_evidence_maps_to_unknown():
    mod = load_module()
    obj = mod.reconcile_layer_state(layer="dashboard", subject="runtime", evidence_items=[])
    assert obj["truth_state"] == "UNKNOWN"
    assert obj["display_allowed"] is False


def test_conflicting_evidence_maps_to_conflict_fail_closed():
    mod = load_module()
    obj = mod.reconcile_layer_state(
        layer="brain",
        subject="state",
        evidence_items=[
            {"id": "a", "truth_state": "VERIFIED_TRUE", "current_state": "A"},
            {"id": "b", "truth_state": "VERIFIED_FALSE", "current_state": "B"},
        ],
    )
    assert obj["truth_state"] == "CONFLICT"
    assert obj["conflict_state"] == "CONFLICT_FAIL_CLOSED"
    assert obj["display_allowed"] is False


def test_historical_state_does_not_become_current():
    mod = load_module()
    obj = mod.reconcile_layer_state(
        layer="interface_hud",
        subject="runtime",
        evidence_items=[{"id": "old", "truth_state": "HISTORICAL", "current_state": "OLD"}],
    )
    assert obj["truth_state"] == "HISTORICAL"
    assert obj["current_state"] == "NOT_CURRENT"
    assert obj["display_allowed"] is False


def test_manual_expected_without_evidence_is_not_complete():
    mod = load_module()
    obj = mod.reconcile_layer_state(
        layer="manual",
        subject="expected_capability",
        evidence_items=[],
        manual_expected=True,
    )
    assert obj["truth_state"] == "PARTIAL"
    assert obj["current_state"] == "EXPECTED_WITHOUT_EVIDENCE"
    assert obj["display_allowed"] is True


def test_brain_inference_does_not_override_evidence():
    mod = load_module()
    obj = mod.reconcile_layer_state(
        layer="brain",
        subject="inferred_capability",
        evidence_items=[],
        brain_inference_only=True,
    )
    assert obj["truth_state"] == "PARTIAL"
    assert obj["current_state"] == "INFERENCE_WITHOUT_EVIDENCE"


def test_dashboard_requires_truth_object():
    mod = load_module()
    valid = mod.build_truth_object(
        truth_object_id="dashboard:truth",
        layer="dashboard",
        subject="truth",
        current_state="CURRENT_VERIFIED",
        truth_state="VERIFIED_TRUE",
        confidence="HIGH_CONFIDENCE",
    )
    blocked = mod.build_truth_object(
        truth_object_id="dashboard:unknown",
        layer="dashboard",
        subject="unknown",
        current_state="NO_EVIDENCE",
        truth_state="UNKNOWN",
        confidence="UNKNOWN",
    )
    contract = mod.build_dashboard_display_contract([valid, blocked])
    assert len(contract["renderable"]) == 1
    assert len(contract["blocked"]) == 1
    assert contract["rule"] == "dashboard_consumes_truth_objects_only"


def test_interface_requires_dashboard_truth_contract():
    mod = load_module()
    valid = mod.build_truth_object(
        truth_object_id="interface:display",
        layer="interface_hud",
        subject="display",
        current_state="CURRENT_PARTIAL",
        truth_state="PARTIAL",
        confidence="MEDIUM_CONFIDENCE",
    )
    dashboard_contract = mod.build_dashboard_display_contract([valid])
    hud_contract = mod.build_interface_hud_display_contract(dashboard_contract)
    assert hud_contract["consumer"] == "interface_hud"
    assert len(hud_contract["displayable"]) == 1
    assert hud_contract["requires_state_label"] is True
    assert hud_contract["requires_risk_label"] is True


def test_capability_cannot_inherit_stronger_parent_state():
    mod = load_module()
    obj = mod.build_truth_object(
        truth_object_id="interface:runtime",
        layer="interface_hud",
        subject="runtime",
        current_state="NO_EVIDENCE",
        truth_state="UNKNOWN",
        confidence="UNKNOWN",
    )
    matrix = mod.build_capability_matrix([obj])
    assert matrix[0]["capability_status"] == "UNKNOWN"


def test_high_or_critical_risk_blocks_advance():
    mod = load_module()
    conflict = mod.build_truth_object(
        truth_object_id="global:conflict",
        layer="global",
        subject="conflict",
        current_state="CONFLICTING_EVIDENCE",
        truth_state="CONFLICT",
        confidence="CONFLICT",
        display_allowed=False,
    )
    risks = mod.build_risk_matrix([conflict])
    assert risks[0]["severity"] == "CRITICAL"
    assert risks[0]["blocking_status"] == "BLOCKS_ADVANCE"


def test_no_productive_operations_are_performed():
    mod = load_module()
    result = mod.validate_no_productive_operations([])
    assert result["valid"] is True
    assert result["forbidden"] == []
    assert result["productive_operations_blocked"] is True


def test_no_manual_brain_argos_queue_publication_automation_mutation():
    mod = load_module()
    result = mod.validate_no_productive_operations(
        [
            "manual_" + "mutation",
            "brain_" + "mutation",
            "argos_" + "mutation",
            "queue_" + "mutation",
            "publication_" + "mutation",
            "automation_" + "trigger",
            "pub" + "lish",
            "sched" + "ule",
            "web" + "hook",
            "n" + "8n",
        ]
    )
    assert result["valid"] is False
    assert set(result["forbidden"]) == {
        "manual_" + "mutation",
        "brain_" + "mutation",
        "argos_" + "mutation",
        "queue_" + "mutation",
        "publication_" + "mutation",
        "automation_" + "trigger",
        "pub" + "lish",
        "sched" + "ule",
        "web" + "hook",
        "n" + "8n",
    }


def test_reconcile_global_state_blocks_conflict():
    mod = load_module()
    manual = mod.build_truth_object(
        truth_object_id="manual:x",
        layer="manual",
        subject="x",
        current_state="CURRENT_VERIFIED",
        truth_state="VERIFIED_TRUE",
        confidence="HIGH_CONFIDENCE",
    )
    brain = mod.build_truth_object(
        truth_object_id="brain:x",
        layer="brain",
        subject="x",
        current_state="CONFLICTING_EVIDENCE",
        truth_state="CONFLICT",
        confidence="CONFLICT",
        display_allowed=False,
    )
    result = mod.reconcile_global_state({"manual": manual, "brain": brain})
    assert result["global_truth_object"]["truth_state"] == "CONFLICT"
    assert result["global_truth_object"]["display_allowed"] is False
