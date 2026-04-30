from __future__ import annotations

from typing import Dict, Tuple

from .constants import ALLOWED_CAPABILITY_MODES, BLOCKED_CAPABILITY_MODES


def validate_capability_mode(capability_mode: str) -> Tuple[bool, str]:
    if capability_mode in BLOCKED_CAPABILITY_MODES:
        return False, "CAPABILITY_MODE_BLOCKED"

    if capability_mode not in ALLOWED_CAPABILITY_MODES:
        return False, "CAPABILITY_MODE_NOT_ALLOWED"

    return True, "CAPABILITY_MODE_OK"


def validate_invariants(controlled_run_unlocked: bool, physical_mutation_allowed: bool) -> Tuple[bool, str]:
    if controlled_run_unlocked is not False:
        return False, "CONTROLLED_RUN_UNLOCK_FORBIDDEN"

    if physical_mutation_allowed is not False:
        return False, "PHYSICAL_MUTATION_FORBIDDEN"

    return True, "INVARIANTS_OK"


def build_unlock_scope() -> Dict:
    return {
        "level": "LIMITED_REPORT_AUDIT_ONLY",
        "future_allowed_operations": [
            "CONTROLLED_REPORT_GENERATION",
            "CONTROLLED_AUDIT_WRITE",
        ],
        "future_denied_operations": [
            "CONTROLLED_FILE_WRITE",
            "CONTROLLED_METADATA_UPDATE",
            "CONTROLLED_STATE_MARK_USED",
            "DELETE",
            "MOVE",
            "SHELL_EXECUTION",
            "SYSTEM_COMMAND",
        ],
    }
