from __future__ import annotations

from typing import Any, Dict

from .approval_guard import validate_unlock_approval
from .evidence_guard import validate_dry_run_evidence
from .hashing import stable_hash
from .reason_registry import reason
from .repo_state_guard import validate_repo_state
from .risk_guard import validate_risk
from .scope_guard import build_unlock_scope, validate_capability_mode, validate_invariants


def _finalize(output: Dict[str, Any]) -> Dict[str, Any]:
    output["unlock_hash"] = stable_hash(
        {
            "unlock_scope": output.get("unlock_scope", {}),
            "dry_run_evidence": output.get("dry_run_evidence", {}),
            "unlock_approval": output.get("unlock_approval", {}),
            "repo_state": output.get("repo_state", {}),
            "risk_analysis": output.get("risk_analysis", {}),
        }
    )
    output["output_hash"] = stable_hash(output)
    return output


def _blocked(reason_code: str) -> Dict[str, Any]:
    return _finalize(
        {
            "phase": "G",
            "subphase": "G-I",
            "protocol": "G-I v1.4.1 FINAL UNLOCK PROTOCOL HARDENING",
            "status": "UNLOCK_BLOCKED",
            "controlled_run_unlocked": False,
            "physical_mutation_allowed": False,
            "unlock_scope": {},
            "dry_run_evidence": {},
            "unlock_approval": {},
            "repo_state": {},
            "risk_analysis": {},
            "reason_registry": [reason(reason_code)],
            "next_phase_required": "G-I v1.5",
            "deterministic": True,
        }
    )


def _review_required(reason_code: str) -> Dict[str, Any]:
    return _finalize(
        {
            "phase": "G",
            "subphase": "G-I",
            "protocol": "G-I v1.4.1 FINAL UNLOCK PROTOCOL HARDENING",
            "status": "REVIEW_REQUIRED",
            "controlled_run_unlocked": False,
            "physical_mutation_allowed": False,
            "unlock_scope": {},
            "dry_run_evidence": {},
            "unlock_approval": {},
            "repo_state": {},
            "risk_analysis": {},
            "reason_registry": [reason(reason_code)],
            "next_phase_required": "G-I v1.5",
            "deterministic": True,
        }
    )


def run_g_i_unlock(
    dry_run_evidence: Dict[str, Any],
    unlock_approval: Dict[str, Any] | None,
    repo_state: Dict[str, Any],
    risk_analysis: Dict[str, Any],
    capability_mode: str,
    controlled_run_unlocked: bool = False,
    physical_mutation_allowed: bool = False,
    now_iso: str | None = None,
) -> Dict[str, Any]:
    unlock_scope = build_unlock_scope()

    ok, reason_code = validate_invariants(controlled_run_unlocked, physical_mutation_allowed)
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = validate_dry_run_evidence(dry_run_evidence)
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = validate_capability_mode(capability_mode)
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = validate_repo_state(repo_state, dry_run_evidence)
    if not ok:
        return _blocked(reason_code)

    ok, reason_code = validate_risk(risk_analysis)
    if not ok:
        if reason_code == "RISK_MEDIUM_REVIEW_REQUIRED":
            return _review_required(reason_code)
        return _blocked(reason_code)

    ok, reason_code = validate_unlock_approval(dry_run_evidence, unlock_approval, unlock_scope, now_iso)
    if not ok:
        if reason_code in {"APPROVAL_MISSING", "UNLOCK_WINDOW_NOT_STARTED"}:
            return _review_required(reason_code)
        return _blocked(reason_code)

    output = {
        "phase": "G",
        "subphase": "G-I",
        "protocol": "G-I v1.4.1 FINAL UNLOCK PROTOCOL HARDENING",
        "status": "CONTROLLED_RUN_UNLOCK_READY",
        "controlled_run_unlocked": False,
        "physical_mutation_allowed": False,
        "unlock_scope": unlock_scope,
        "dry_run_evidence": dry_run_evidence,
        "unlock_approval": unlock_approval,
        "repo_state": repo_state,
        "risk_analysis": risk_analysis,
        "reason_registry": [
            reason(
                "UNLOCK_READY_REVIEW_ONLY",
                "Ready for limited controlled-run review. No execution unlocked.",
            )
        ],
        "next_phase_required": "G-I v1.5",
        "deterministic": True,
    }

    return _finalize(output)
