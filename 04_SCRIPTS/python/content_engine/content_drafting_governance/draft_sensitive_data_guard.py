from __future__ import annotations

import re

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?\d[\d\s-]{7,}\d)")
SECRET_RE = re.compile(r"(?:api[_-]?key|secret|token)\s*[:=]", re.IGNORECASE)
LOCAL_PATH_RE = re.compile(r"[A-Za-z]:\\[^\s]+")


def inspect_sensitive_human_field(text: str) -> dict[str, object]:
    matches = []
    if EMAIL_RE.search(text):
        matches.append("email")
    if PHONE_RE.search(text):
        matches.append("phone")
    if SECRET_RE.search(text):
        matches.append("secret")
    if LOCAL_PATH_RE.search(text):
        matches.append("local_path")
    return {
        "blocked": bool(matches),
        "matched_types": sorted(set(matches)),
        "reason": "SENSITIVE_DATA_BLOCK" if matches else "SENSITIVE_DATA_CLEAR",
    }
