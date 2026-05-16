from __future__ import annotations

import re

from .queue_failure_policy import PASS, BLOCK

_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)")
_SECRET_RE = re.compile(r"(api[_-]?key|secret|token|password|passwd|bearer)\s*[:=]\s*[A-Za-z0-9_\-]{8,}", re.IGNORECASE)
_EXACT_ADDRESS_RE = re.compile(r"\b\d{1,6}\s+[A-Za-zÁÉÍÓÚáéíóúÑñ0-9 .'-]{2,}\s+(street|st|avenue|ave|road|rd|calle|avenida|av\.|drive|dr)\b", re.IGNORECASE)
_PATH_TRAVERSAL_RE = re.compile(r"(\.\./|\.\.\\|%2e%2e)", re.IGNORECASE)
_PATH_LIKE_RE = re.compile(r"(^[A-Za-z]:\\|^/mnt/|^/home/|^\\\\|[A-Za-z]:/)")

HUMAN_TEXT_FIELDS = frozenset({
    "idea_title",
    "idea_summary",
    "content_intent",
    "blocked_reason",
})

TECHNICAL_FIELDS = frozenset({
    "schema_version",
    "queue_item_id",
    "created_at_utc",
    "source_type",
    "channel_id",
    "pillar_id",
    "audience_profile_id",
    "lifecycle_state",
    "priority_band",
    "readiness_status",
    "risk_level",
    "evidence_status",
    "traceability",
})


def _block(reason: str, sample: str = "") -> dict:
    return {
        "status": BLOCK,
        "reason": reason,
        "sample": sample[:80],
        "queue_write_performed": False,
        "real_queue_mutation_performed": False,
    }


def _walk_field_strings(value, path: tuple[str, ...] = ()):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk_field_strings(child, (*path, str(key)))
    elif isinstance(value, (list, tuple, set)):
        for idx, child in enumerate(value):
            yield from _walk_field_strings(child, (*path, str(idx)))
    elif isinstance(value, str):
        field = path[-1] if path else ""
        yield field, value


def _is_human_text_field(field: str) -> bool:
    return field in HUMAN_TEXT_FIELDS


def _is_technical_field(field: str) -> bool:
    return field in TECHNICAL_FIELDS


def detect_sensitive_payload(payload: dict) -> dict:
    for field, text in _walk_field_strings(payload):
        if not _is_human_text_field(field):
            continue

        if _EMAIL_RE.search(text):
            return _block("QUEUE_PII_EMAIL_DETECTED", text)
        if _PHONE_RE.search(text):
            return _block("QUEUE_PII_PHONE_DETECTED", text)
        if _EXACT_ADDRESS_RE.search(text):
            return _block("QUEUE_EXACT_ADDRESS_DETECTED", text)

    return {"status": PASS, "reason": "NO_SENSITIVE_DATA_DETECTED"}


def detect_secret_payload(payload: dict) -> dict:
    for field, text in _walk_field_strings(payload):
        if _is_technical_field(field) and field not in HUMAN_TEXT_FIELDS:
            continue

        if _SECRET_RE.search(text):
            return _block("QUEUE_SECRET_TOKEN_DETECTED", text)

    return {"status": PASS, "reason": "NO_SECRET_DETECTED"}


def detect_path_like_payload(payload: dict) -> dict:
    for field, text in _walk_field_strings(payload):
        stripped = text.strip()

        if _PATH_TRAVERSAL_RE.search(stripped):
            return _block("QUEUE_PATH_TRAVERSAL_DETECTED", stripped)

        if _is_technical_field(field):
            continue

        if _PATH_LIKE_RE.search(stripped):
            return _block("QUEUE_ITEM_ID_PATH_LIKE", stripped)

    return {"status": PASS, "reason": "NO_PATH_LIKE_PAYLOAD_DETECTED"}


def validate_payload_safety(payload: dict) -> dict:
    for check in (
        detect_sensitive_payload(payload),
        detect_secret_payload(payload),
        detect_path_like_payload(payload),
    ):
        if check.get("status") == BLOCK:
            return check
    return {"status": PASS, "reason": "PAYLOAD_SAFE"}
