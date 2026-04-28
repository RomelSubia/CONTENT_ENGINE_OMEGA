from __future__ import annotations

from typing import Dict


def reason(reason_code: str, detail: str = "") -> Dict:
    return {
        "reason_code": reason_code,
        "reason_detail": detail or reason_code,
    }
