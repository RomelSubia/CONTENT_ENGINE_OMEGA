from __future__ import annotations

from .runtime_contracts import PASS
from .runtime_failure_policy import fail_closed

LEVELS = {
    0: "Governance blueprint/build only",
    1: "Runtime preview governance",
    2: "Runtime dry-run evidence",
    3: "Controlled draft creation",
    4: "Controlled content generation",
    5: "Queue staging",
    6: "Assisted publishing",
    7: "Partial automation",
    8: "Advanced controlled autonomy",
}

def validate_maturity_level(level: int) -> dict[str, object]:
    if int(level) != 0:
        return fail_closed("INVALID_MATURITY_LEVEL")
    return {
        "status": PASS,
        "runtime_autonomy_level_now": 0,
        "autonomy_escalation_allowed": False,
        "levels": LEVELS,
    }
