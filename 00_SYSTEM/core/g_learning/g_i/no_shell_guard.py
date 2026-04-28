from __future__ import annotations

from typing import Any, Tuple

from .constants import FORBIDDEN_CODE_TERMS


def scan_no_shell(data: Any) -> Tuple[bool, str]:
    text = str(data).lower()
    if any(term in text for term in FORBIDDEN_CODE_TERMS):
        return False, "FORBIDDEN_SHELL_TOKEN_DETECTED"
    return True, "NO_SHELL_OK"
