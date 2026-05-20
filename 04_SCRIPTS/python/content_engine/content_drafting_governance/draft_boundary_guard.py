from __future__ import annotations

BLOCKED_BOUNDARY_PATTERNS = (
    "publish",
    "publicar",
    "postear",
    "schedule post",
    "queue write",
    "write queue",
    "webhook",
    "external api",
    "run script",
    "execute script",
    "bypass review",
    "human override",
    "auto approve",
)


def inspect_boundary_text(text: str) -> dict[str, object]:
    lowered = text.lower()
    matches = sorted({pattern for pattern in BLOCKED_BOUNDARY_PATTERNS if pattern in lowered})
    return {
        "blocked": bool(matches),
        "matched_patterns": matches,
        "reason": "BOUNDARY_BLOCK" if matches else "BOUNDARY_CLEAR",
    }


def assert_boundary_clear(text: str) -> bool:
    return inspect_boundary_text(text)["blocked"] is False
