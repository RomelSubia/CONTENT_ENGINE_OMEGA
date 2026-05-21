from __future__ import annotations

ETHICAL_MARKETING_BLOCK_PATTERNS = (
    "última oportunidad falsa",
    "escasez falsa",
    "miedo a perderlo todo",
    "manipula",
    "engaña",
    "presiona",
    "false scarcity",
    "false urgency",
    "exploit fear",
)


def _cdg_original_inspect_marketing_ethics(text: str) -> dict[str, object]:
    lowered = text.lower()
    matches = sorted({pattern for pattern in ETHICAL_MARKETING_BLOCK_PATTERNS if pattern in lowered})
    return {
        "blocked": bool(matches),
        "matched_patterns": matches,
        "ethical_persuasion_allowed": not bool(matches),
        "reason": "MARKETING_ETHICS_BLOCK" if matches else "MARKETING_ETHICS_CLEAR",
    }

# --- CONTENT_ENGINE_CONTENT_DRAFTING_GOVERNANCE_VALIDATION_FIX_5_MARKETING_ETHICS_FALSE_URGENCY_SOURCE_HARDENING ---
_CDG_FALSE_URGENCY_MARKETING_PHRASES = (
    "urgencia falsa",
    "crear urgencia falsa",
    "usar urgencia falsa",
    "presionar con urgencia falsa",
    "falsa urgencia",
    "crear falsa urgencia",
    "usar falsa urgencia",
    "false urgency",
    "fake urgency",
    "artificial urgency",
    "manufactured urgency",
    "create false urgency",
    "use false urgency",
    "pressure with false urgency",
)

_CDG_FALSE_URGENCY_MARKETING_COMPOSITES = (
    ("urgencia", "falsa"),
    ("falsa", "urgencia"),
    ("presionar", "urgencia"),
    ("crear", "urgencia", "falsa"),
    ("usar", "urgencia", "falsa"),
    ("false", "urgency"),
    ("fake", "urgency"),
    ("artificial", "urgency"),
    ("manufactured", "urgency"),
    ("pressure", "false", "urgency"),
)


def _cdg_false_urgency_marketing_ethics_guard(text: object) -> bool:
    normalized = str(text or "").lower()
    collapsed = " ".join(normalized.replace("_", " ").replace("-", " ").split())
    if any(phrase in normalized for phrase in _CDG_FALSE_URGENCY_MARKETING_PHRASES):
        return True
    return any(all(part in collapsed for part in parts) for parts in _CDG_FALSE_URGENCY_MARKETING_COMPOSITES)


def _cdg_false_urgency_blocked_result(text: object) -> dict:
    return {
        "blocked": True,
        "reason": "FALSE_URGENCY_MARKETING_ETHICS_BLOCKED",
        "matched_ethics_boundary": "false_urgency",
        "matched_text": str(text or ""),
        "human_review_required": True,
        "draft_creation_allowed": False,
        "content_generation_allowed": False,
        "queue_write_allowed": False,
        "publishing_allowed": False,
        "automation_allowed": False,
        "final_output_allowed": False,
    }


def inspect_marketing_ethics(text: object) -> dict:
    if _cdg_false_urgency_marketing_ethics_guard(text):
        return _cdg_false_urgency_blocked_result(text)
    return _cdg_original_inspect_marketing_ethics(text)
# --- END CONTENT_ENGINE_CONTENT_DRAFTING_GOVERNANCE_VALIDATION_FIX_5_MARKETING_ETHICS_FALSE_URGENCY_SOURCE_HARDENING ---
