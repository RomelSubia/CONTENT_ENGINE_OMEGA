from __future__ import annotations

from typing import Dict, Tuple

from .constants import REQUIRED_EVIDENCE_KEYS


def validate_dry_run_evidence(evidence: Dict) -> Tuple[bool, str]:
    if not isinstance(evidence, dict):
        return False, "EVIDENCE_NOT_DICT"

    missing = [key for key in REQUIRED_EVIDENCE_KEYS if key not in evidence]
    if missing:
        return False, "MISSING_EVIDENCE_KEYS:" + ",".join(missing)

    if evidence["g_i_v13_audit_exists"] is not True:
        return False, "GI_V13_AUDIT_MISSING"

    if evidence["pytest_passed"] is not True:
        return False, "PYTEST_NOT_PASSED"

    if evidence["pytest_count"] != 84:
        return False, "INVALID_PYTEST_COUNT"

    if evidence["no_mutation_pass"] is not True:
        return False, "NO_MUTATION_NOT_PROVEN"

    if evidence["controlled_run_locked"] is not True:
        return False, "CONTROLLED_RUN_NOT_LOCKED"

    if evidence["repo_sync_valid"] is not True:
        return False, "REPO_SYNC_INVALID"

    for key in ("commit_hash", "evidence_hash"):
        if not isinstance(evidence[key], str) or not evidence[key]:
            return False, f"INVALID_{key.upper()}"

    return True, "EVIDENCE_OK"
