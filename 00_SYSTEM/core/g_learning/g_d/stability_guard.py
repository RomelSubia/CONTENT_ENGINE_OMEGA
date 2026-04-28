from __future__ import annotations

from typing import Dict, Tuple


def stability_guard(recommendation: Dict) -> Tuple[bool, str]:
    if recommendation.get("stability_impact") == "HIGH":
        return False, "STABILITY_DEGRADATION_BLOCKED"
    return True, "STABILITY_OK"
