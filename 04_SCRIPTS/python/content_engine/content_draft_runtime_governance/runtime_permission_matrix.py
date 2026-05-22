from __future__ import annotations

from .runtime_contracts import RUNTIME_STATES

_MATRIX = {
    state: {"draft": False, "content": False, "queue": False, "publish": False, "automation": False}
    for state in RUNTIME_STATES
}
_MATRIX["RUNTIME_PREVIEW_READY"]["preview"] = "conceptual_limited"
_MATRIX["RUNTIME_REQUIRES_HUMAN_REVIEW"]["preview"] = "read_only"
_MATRIX["RUNTIME_SEALED_NO_OP"]["preview"] = "evidence_only"

def permission_matrix() -> dict[str, dict[str, object]]:
    return {state: dict(value) for state, value in _MATRIX.items()}

def state_allows_productive_action(state: str) -> bool:
    row = _MATRIX.get(state, {})
    return any(row.get(key) is not False for key in ("draft", "content", "queue", "publish", "automation"))
