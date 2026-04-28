from __future__ import annotations

from typing import Dict, Tuple

from .constants import SEALED_PHASES


def sealed_phase_guard(recommendation: Dict) -> Tuple[bool, str]:
    affected = set(recommendation.get("affects_phase", []))
    if affected.intersection(SEALED_PHASES):
        return False, "SEALED_PHASE_TOUCH_BLOCKED"
    return True, "SEALED_PHASE_OK"
