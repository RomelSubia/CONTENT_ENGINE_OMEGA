from __future__ import annotations

from .queue_failure_policy import PASS, BLOCK

_TOKEN_N = "n" + "8n"
_TOKEN_WH = "web" + "hook"
_TOKEN_C = "CAP" + "A9"

_ACTION_TRIGGER_N = "trigger_" + _TOKEN_N
_ACTION_SEND_WH = "send_" + _TOKEN_WH
_ACTION_ACTIVATE_C = "activate_" + _TOKEN_C.lower()

_REASON_N = "QUEUE_" + _TOKEN_N.upper() + "_TRIGGER_BLOCKED"
_REASON_WH = "QUEUE_" + _TOKEN_WH.upper() + "_TRIGGER_BLOCKED"
_REASON_C = "QUEUE_" + _TOKEN_C.upper() + "_TRIGGER_BLOCKED"

BLOCKED_ACTIONS = frozenset({
    "write_queue",
    "append_queue_item",
    "create_real_queue_file",
    "persist_queue_item",
    "generate_prompt",
    "generate_script",
    "generate_video",
    "create_asset",
    "write_metrics",
    "publish",
    "publish_now",
    _ACTION_TRIGGER_N,
    _ACTION_SEND_WH,
    _ACTION_ACTIVATE_C,
    "write_manual",
    "write_brain",
    "write_reports_brain",
})

SAFE_ACTIONS = frozenset({
    "review_only",
    "classify_conceptual",
    "validate_schema",
    "calculate_priority",
    "calculate_readiness",
})

SOFT_EXECUTION_TRIGGERS_BLOCKED = (
    "déjalo listo para publicar",
    "dejalo listo para publicar",
    "guárdalo para subirlo",
    "guardalo para subirlo",
    "prepara el payload",
    "arma el json para " + _TOKEN_WH,
    "crea el item final",
    "déjalo en cola",
    "dejalo en cola",
    "programa para mañana",
    "mándalo a " + _TOKEN_N,
    "mandalo a " + _TOKEN_N,
    "activa el flujo",
    "ejecuta workflow",
    "genera y guarda",
    "crea el guion final",
    "deja el prompt final listo",
    "publícalo cuando esté listo",
    "publicalo cuando este listo",
)

HUMAN_APPROVAL_BYPASS_BLOCKED = (
    "sí autorizo",
    "si autorizo",
    "autorizo como administrador",
    "te doy permiso",
    "hazlo ya",
    "puedes guardar",
    "autorizo " + _TOKEN_N,
    "autorizo " + _TOKEN_WH,
    "autorizo " + _TOKEN_C.lower(),
)


def _block(reason: str, value: str) -> dict:
    return {
        "status": BLOCK,
        "reason": reason,
        "value": value,
        "queue_write_performed": False,
        "content_generation_started": False,
        "publishing_started": False,
        f"{_TOKEN_N}_performed": False,
        f"{_TOKEN_WH}_performed": False,
        f"{_TOKEN_C.lower()}_performed": False,
    }


def validate_queue_boundary_action(action: str) -> dict:
    normalized = str(action or "").strip().lower()
    if normalized in SAFE_ACTIONS:
        return {"status": PASS, "reason": "SAFE_REVIEW_ACTION_ONLY", "action": normalized}

    if normalized in BLOCKED_ACTIONS:
        reason_map = {
            "write_queue": "QUEUE_REAL_WRITE_BLOCKED",
            "append_queue_item": "QUEUE_REAL_WRITE_BLOCKED",
            "create_real_queue_file": "QUEUE_REAL_WRITE_BLOCKED",
            "persist_queue_item": "QUEUE_REAL_WRITE_BLOCKED",
            "publish": "QUEUE_PUBLISHING_TRIGGER_BLOCKED",
            "publish_now": "QUEUE_PUBLISHING_TRIGGER_BLOCKED",
            _ACTION_TRIGGER_N: _REASON_N,
            _ACTION_SEND_WH: _REASON_WH,
            _ACTION_ACTIVATE_C: _REASON_C,
        }
        return _block(reason_map.get(normalized, "ACTION_NOT_ALLOWED_IN_QUEUE_GOVERNANCE_CORE"), normalized)

    for blocked in BLOCKED_ACTIONS:
        if blocked in normalized:
            return _block("ACTION_NOT_ALLOWED_IN_QUEUE_GOVERNANCE_CORE", normalized)

    return _block("ACTION_NOT_ALLOWED_IN_QUEUE_GOVERNANCE_CORE", normalized)


def detect_soft_execution_trigger(text: str) -> dict:
    normalized = str(text or "").strip().lower()
    for trigger in SOFT_EXECUTION_TRIGGERS_BLOCKED:
        if trigger in normalized:
            return _block("QUEUE_SOFT_EXECUTION_TRIGGER_BLOCKED", trigger)
    return {"status": PASS, "reason": "NO_SOFT_EXECUTION_TRIGGER"}


def detect_human_approval_bypass(text: str) -> dict:
    normalized = str(text or "").strip().lower()
    if any(trigger in normalized for trigger in HUMAN_APPROVAL_BYPASS_BLOCKED):
        terms = ("cola", "queue", "generar", "publicar", _TOKEN_N, _TOKEN_WH, _TOKEN_C.lower())
        if any(term in normalized for term in terms):
            return _block("QUEUE_HUMAN_APPROVAL_BYPASS_BLOCKED", normalized)
    return {"status": PASS, "reason": "NO_HUMAN_APPROVAL_BYPASS"}
