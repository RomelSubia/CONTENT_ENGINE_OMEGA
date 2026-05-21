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


def _cdg_original_inspect_boundary_text(text: str) -> dict[str, object]:
    lowered = text.lower()
    matches = sorted({pattern for pattern in BLOCKED_BOUNDARY_PATTERNS if pattern in lowered})
    return {
        "blocked": bool(matches),
        "matched_patterns": matches,
        "reason": "BOUNDARY_BLOCK" if matches else "BOUNDARY_CLEAR",
    }


def assert_boundary_clear(text: str) -> bool:
    return inspect_boundary_text(text)["blocked"] is False

# --- CONTENT_ENGINE_CONTENT_DRAFTING_GOVERNANCE_VALIDATION_FIX_3_BOUNDARY_QUEUE_SOURCE_HARDENING ---
_CDG_QUEUE_WRITE_BOUNDARY_PHRASES = (
    "escribir en la cola real",
    "escribir cola real",
    "cola real",
    "escribir en cola",
    "guardar en cola",
    "agregar a la cola",
    "agregar a cola",
    "insertar en cola",
    "mutar cola",
    "cola de publicación",
    "escribir en 07_data/queue",
    "write queue",
    "write to queue",
    "queue write",
    "real queue mutation",
    "append to queue",
    "enqueue",
    "queue mutation",
)

_CDG_QUEUE_WRITE_BOUNDARY_COMPOSITES = (
    ("queue", "write"),
    ("queue", "mutation"),
    ("real", "queue", "mutation"),
    ("append", "queue"),
    ("write", "queue"),
    ("cola", "real"),
    ("escribir", "cola"),
    ("guardar", "cola"),
    ("agregar", "cola"),
    ("insertar", "cola"),
    ("mutar", "cola"),
)


def _cdg_queue_write_boundary_guard(text: object) -> bool:
    normalized = str(text or "").lower()
    collapsed = " ".join(normalized.replace("_", " ").replace("-", " ").split())
    if any(phrase in normalized for phrase in _CDG_QUEUE_WRITE_BOUNDARY_PHRASES):
        return True
    if "07_data/queue" in normalized or "07_data\\queue" in normalized or "07 data queue" in collapsed:
        return True
    return any(all(part in collapsed for part in parts) for parts in _CDG_QUEUE_WRITE_BOUNDARY_COMPOSITES)


def _cdg_queue_write_blocked_result(text: object) -> dict:
    return {
        "blocked": True,
        "reason": "QUEUE_WRITE_BOUNDARY_BLOCKED",
        "matched_boundary": "queue_write",
        "matched_text": str(text or ""),
        "human_review_required": True,
        "draft_creation_allowed": False,
        "content_generation_allowed": False,
        "queue_write_allowed": False,
        "real_queue_mutation_allowed": False,
        "publishing_allowed": False,
        "automation_allowed": False,
    }


def inspect_boundary_text(text: object) -> dict:
    if _cdg_queue_write_boundary_guard(text):
        return _cdg_queue_write_blocked_result(text)
    return _cdg_original_inspect_boundary_text(text)
# --- END CONTENT_ENGINE_CONTENT_DRAFTING_GOVERNANCE_VALIDATION_FIX_3_BOUNDARY_QUEUE_SOURCE_HARDENING ---
