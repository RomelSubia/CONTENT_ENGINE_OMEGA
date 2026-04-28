from __future__ import annotations

from typing import Dict, Tuple


def security_guard(recommendation: Dict) -> Tuple[bool, str]:
    if recommendation.get("auto_apply_allowed") is not False:
        return False, "SECURITY_AUTO_APPLY_BLOCKED"
    if recommendation.get("touch_scope") != "READ_ONLY":
        return False, "SECURITY_TOUCH_SCOPE_BLOCKED"
    if recommendation.get("rollback_required") is not True:
        return False, "SECURITY_ROLLBACK_BLOCKED"
    if recommendation.get("requires_human_approval") is not True:
        return False, "SECURITY_APPROVAL_BLOCKED"
    if recommendation.get("reversible") is not True:
        return False, "SECURITY_REVERSIBILITY_BLOCKED"
    return True, "SECURITY_OK"
