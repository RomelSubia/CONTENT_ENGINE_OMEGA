from __future__ import annotations

from typing import Dict


def no_action_output(input_data: Dict) -> Dict:
    return {
        "phase": "G",
        "subphase": "G-D",
        "status": "VALID",
        "approved_for_review": [],
        "quarantined": [],
        "blocked": [],
        "risk_summary": {"state": "NO_RISK_ACTION_REQUIRED"},
        "reason_registry": [],
        "decision": "NO_ACTION",
        "deterministic": True,
    }
