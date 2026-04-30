from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Tuple

from .constants import APPROVAL_SCOPE, APPROVAL_VERSION, REQUIRED_APPROVAL_KEYS
from .hashing import stable_hash


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def expected_unlock_approval_id(evidence: Dict, approval: Dict, unlock_scope: Dict) -> str:
    window = approval["unlock_window"]
    return stable_hash(
        {
            "evidence_hash": evidence["evidence_hash"],
            "commit_hash": evidence["commit_hash"],
            "approval_statement": approval["approval_statement"],
            "unlock_scope": unlock_scope,
            "unlock_window_start": window["start"],
            "unlock_window_end": window["end"],
        }
    )


def validate_unlock_approval(evidence: Dict, approval: Dict, unlock_scope: Dict, now_iso: str | None = None) -> Tuple[bool, str]:
    if approval is None:
        return False, "APPROVAL_MISSING"

    if not isinstance(approval, dict):
        return False, "APPROVAL_NOT_DICT"

    missing = [key for key in REQUIRED_APPROVAL_KEYS if key not in approval]
    if missing:
        return False, "MISSING_APPROVAL_KEYS:" + ",".join(missing)

    if approval["approval_version"] != APPROVAL_VERSION:
        return False, "INVALID_APPROVAL_VERSION"

    if approval["approved_by"] != "Romel":
        return False, "INVALID_APPROVER"

    if approval["identity_verified"] is not True:
        return False, "IDENTITY_NOT_VERIFIED"

    if approval["approval_scope"] != APPROVAL_SCOPE:
        return False, "INVALID_APPROVAL_SCOPE"

    if approval["understands_mutation_risk"] is not True:
        return False, "MUTATION_RISK_NOT_ACKNOWLEDGED"

    if approval["understands_rollback_risk"] is not True:
        return False, "ROLLBACK_RISK_NOT_ACKNOWLEDGED"

    if approval["dry_run_evidence_reviewed"] is not True:
        return False, "DRY_RUN_EVIDENCE_NOT_REVIEWED"

    if approval["secondary_confirmation"] is not True:
        return False, "SECONDARY_CONFIRMATION_REQUIRED"

    if approval["revocation_status"] != "ACTIVE":
        return False, "APPROVAL_REVOKED_OR_INACTIVE"

    if approval["reuse_status"] != "UNUSED":
        return False, "APPROVAL_REUSE_BLOCKED"

    statement = str(approval["approval_statement"]).strip()
    if len(statement) < 45:
        return False, "APPROVAL_STATEMENT_TOO_WEAK"

    window = approval["unlock_window"]
    if not isinstance(window, dict):
        return False, "UNLOCK_WINDOW_NOT_DICT"

    if "start" not in window or "end" not in window:
        return False, "UNLOCK_WINDOW_INCOMPLETE"

    now = parse_iso(now_iso) if now_iso else datetime.now(timezone.utc)
    expiration = parse_iso(approval["approval_expiration"])
    start = parse_iso(window["start"])
    end = parse_iso(window["end"])

    if now > expiration:
        return False, "APPROVAL_EXPIRED"

    if now < start:
        return False, "UNLOCK_WINDOW_NOT_STARTED"

    if now > end:
        return False, "UNLOCK_WINDOW_EXPIRED"

    expected_id = expected_unlock_approval_id(evidence, approval, unlock_scope)
    if approval["unlock_approval_id"] != expected_id:
        return False, "UNLOCK_APPROVAL_ID_MISMATCH"

    return True, "APPROVAL_OK"
