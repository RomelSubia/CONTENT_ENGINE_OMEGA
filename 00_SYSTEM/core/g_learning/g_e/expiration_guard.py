from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Tuple


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def expiration_guard(approval: Dict, now_iso: str | None = None) -> Tuple[bool, str]:
    now = parse_iso(now_iso) if now_iso else datetime.now(timezone.utc)
    expiration = parse_iso(approval["approval_expiration"])

    if now > expiration:
        return False, "EXPIRED_APPROVAL"

    return True, "APPROVAL_NOT_EXPIRED"
