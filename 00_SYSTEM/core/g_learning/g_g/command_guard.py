from __future__ import annotations

import re
from typing import Any

FORBIDDEN_COMMAND_PATTERNS = (
    r"\bpowershell\b",
    r"\bbash\b",
    r"\bcmd\.exe\b",
    r"\bexecute\b",
    r"\brun\b",
    r"\bapply\b",
    r"\bpatch\b",
    r"\bdeploy\b",
    r"\bdelete\b",
    r"\bmove\b",
    r"\bwrite\b",
    r"\bmodify\s+code\b",
    r"\bgit\s+push\b",
    r"\bgit\s+commit\b",
)


def contains_command_token(data: Any) -> bool:
    text = str(data).lower()
    return any(re.search(pattern, text) for pattern in FORBIDDEN_COMMAND_PATTERNS)
