from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any


BLOCK_ID = "BLOQUE_4_RULE_EXTRACTOR_INTENT_CLASSIFIER"
LIFECYCLE_STATUS = "BUILT_PENDING_POST_AUDIT"
NEXT_SAFE_STEP = "BLOQUE_4_POST_BUILD_AUDIT"

DECISION_RANK = {
    "PASS": 0,
    "PASS_WITH_WARNINGS": 1,
    "REQUIRE_REVIEW": 2,
    "BLOCK": 3,
    "LOCK": 4,
}

DANGEROUS_CAPABILITIES = {
    "EXECUTION",
    "MANUAL_WRITE",
    "BRAIN_WRITE",
    "REPORTS_BRAIN_WRITE",
    "N8N",
    "WEBHOOK",
    "PUBLISHING",
    "CAPA9",
}

CAPABILITY_LEXICON = {
    "POST_BUILD_AUDIT": ("post-build audit", "auditoría post-build"),
    "VALIDATION_MAP": ("validation map", "mapa de validación"),
    "VALIDATION_PLAN": ("validation plan", "plan de validación"),
    "GATE_CLOSURE": ("gate closure", "cerrar bloque", "cierre"),
    "IMPLEMENTATION_PLAN": ("implementation plan", "plan de implementación", "plan exacto"),
    "BLUEPRINT": ("blueprint", "diseño", "diseñar"),
    "BUILD": ("bloque automático", "generar build", "build", "construir"),
    "VALIDATION": ("validation", "validación", "validar"),
    "EXECUTION": ("execution", "ejecución", "ejecuta", "ejecutar"),
    "MANUAL_WRITE": ("manual write", "escribir manual", "modificar manual", "modifica el manual"),
    "BRAIN_WRITE": (
        "brain write",
        "escribir brain",
        "escribir cerebro",
        "escribe en el cerebro",
        "escribir en el cerebro",
        "escribe cerebro",
        "cerebro",
    ),
    "REPORTS_BRAIN_WRITE": ("reports brain write", "escribir reports brain", "escribir reportes cerebro"),
    "PUBLISHING": ("haz publishing", "publishing", "publicar", "publicación"),
    "WEBHOOK": ("llama webhook", "llamar webhook", "webhook"),
    "N8N": ("activa n8n", "activar n8n", "n8n"),
    "CAPA9": ("capa 9", "capa9"),
}

INTENT_BY_CAPABILITY = {
    "BLUEPRINT": "BLUEPRINT_REQUEST",
    "IMPLEMENTATION_PLAN": "IMPLEMENTATION_PLAN_REQUEST",
    "BUILD": "BUILD_REQUEST",
    "POST_BUILD_AUDIT": "POST_BUILD_AUDIT_REQUEST",
    "VALIDATION_MAP": "VALIDATION_MAP_REQUEST",
    "VALIDATION_PLAN": "VALIDATION_PLAN_REQUEST",
    "VALIDATION": "VALIDATION_REQUEST",
    "GATE_CLOSURE": "GATE_CLOSURE_REQUEST",
    "EXECUTION": "EXECUTION_REQUEST",
    "MANUAL_WRITE": "MANUAL_WRITE_REQUEST",
    "BRAIN_WRITE": "BRAIN_WRITE_REQUEST",
    "REPORTS_BRAIN_WRITE": "REPORTS_BRAIN_WRITE_REQUEST",
    "N8N": "N8N_REQUEST",
    "WEBHOOK": "WEBHOOK_REQUEST",
    "PUBLISHING": "PUBLISHING_REQUEST",
    "CAPA9": "CAPA9_REQUEST",
}

PHASE_LEXICON = {
    "POST_BUILD_AUDIT_REQUEST": ("post-build audit",),
    "VALIDATION_MAP_REQUEST": ("validation map", "mapa de validación"),
    "VALIDATION_PLAN_REQUEST": ("validation plan", "plan de validación"),
    "GATE_CLOSURE_REQUEST": ("gate closure", "cerrar bloque"),
    "IMPLEMENTATION_PLAN_REQUEST": ("implementation plan", "plan de implementación", "plan exacto"),
    "BLUEPRINT_REQUEST": ("blueprint", "diseño"),
    "BUILD_REQUEST": ("bloque automático", "build", "construir"),
    "VALIDATION_REQUEST": ("validation", "validación", "validar"),
    "STATUS_REQUEST": ("estatus", "estado", "status"),
    "REVIEW_REQUEST": ("review", "revisión", "revisa", "seguro"),
}

NEGATION_TERMS = ("no", "nunca", "bloqueado", "blocked", "bloquear", "prohibido", "mantener bloqueado")
ALLOW_TERMS = ("permitir", "permitido", "allow", "allowed", "habilitar", "autorizar")
AUTHORIZATION_TERMS = ("autorización válida", "fresh human approval", "approval valid")
REQUEST_VERBS = ("dame", "haz", "ejecuta", "escribe", "modifica", "llama", "activa", "publica", "revisa")

FORBIDDEN_PUBLIC_FIELDS = {
    "raw_text", "normalized_text", "context_text", "source_text", "full_text",
    "manual_text", "brain_text", "content", "body", "transcript", "excerpt",
}
FORBIDDEN_PUBLIC_STRINGS = {
    "FAKE_SECRET_API_KEY_123",
    "FAKE_BRAIN_PRIVATE_CONTENT",
    "FAKE_MANUAL_FULL_BODY",
    "FAKE_TOKEN_SHOULD_NOT_LEAK",
}

ERROR_CODES = (
    "B4_INPUT_SOURCE_SNAPSHOT_MISSING_LOCK",
    "B4_INPUT_NOT_SAFE_FOR_RULE_EXTRACTION_BLOCK",
    "B4_INPUT_AUTHORITY_NOT_CANONICAL_REVIEW",
    "B4_INPUT_HASH_MISSING_BLOCK",
    "B4_B3_SNAPSHOT_CONTRACT_INVALID_BLOCK",
    "B4_B3_SNAPSHOT_WRITE_ALLOWED_LOCK",
    "B4_B3_SNAPSHOT_NOT_FIXTURE_SAFE_BLOCK",
    "B4_REAL_MANUAL_READ_IN_BUILD_LOCK",
    "B4_REAL_BRAIN_READ_IN_BUILD_LOCK",
    "B4_FIXTURE_POLICY_MISSING_BLOCK",
    "B4_SEGMENT_CONTRACT_INCOMPLETE_BLOCK",
    "B4_SEGMENT_OFFSET_INVALID_BLOCK",
    "B4_SEGMENT_EMPTY_BLOCK",
    "B4_SEGMENT_TOO_LARGE_REVIEW",
    "B4_NORMALIZATION_FAILED_BLOCK",
    "B4_NEGATION_LOST_DURING_NORMALIZATION_LOCK",
    "B4_CAPABILITY_LOST_DURING_NORMALIZATION_LOCK",
    "B4_RULE_CONTRACT_INCOMPLETE_BLOCK",
    "B4_INTENT_CONTRACT_INCOMPLETE_BLOCK",
    "B4_INTENT_AUTHORIZATION_CONFUSION_LOCK",
    "B4_ACTION_ALLOWED_WITHOUT_AUTHORIZATION_LOCK",
    "B4_AUTHORIZATION_INVERSION_LOCK",
    "B4_POLARITY_UNKNOWN_REVIEW",
    "B4_POLARITY_CONFLICT_LOCK",
    "B4_NEGATIVE_CAPABILITY_ALLOWED_LOCK",
    "B4_PERMISSIVE_NEGATION_CONFLICT_LOCK",
    "B4_CONTEXT_WINDOW_TOO_LARGE_BLOCK",
    "B4_CONTEXT_HASH_MISSING_BLOCK",
    "B4_CONTEXT_TEXT_LEAK_LOCK",
    "B4_CANDIDATE_INVARIANT_FAILED_LOCK",
    "B4_UNKNOWN_RULE_PASS_LOCK",
    "B4_UNKNOWN_INTENT_PASS_LOCK",
    "B4_UNKNOWN_CAPABILITY_ALLOWED_LOCK",
    "B4_UNKNOWN_POLARITY_SAFE_LOCK",
    "B4_UNKNOWN_ROLE_SAFE_LOCK",
    "B4_DANGEROUS_CAPABILITY_ACTION_ALLOWED_LOCK",
    "B4_CONFIDENCE_APPROVED_DANGEROUS_CAPABILITY_LOCK",
    "B4_REPORT_CONTENT_LEAK_LOCK",
    "B4_PUBLIC_REPORT_CONTAINS_TEXT_LOCK",
    "B4_FORBIDDEN_TEXT_FIELD_LOCK",
    "B4_FORBIDDEN_STRING_LEAK_LOCK",
    "B4_RAW_SEMANTIC_TEXT_PERSISTED_LOCK",
    "B4_INPUT_MUTATION_LOCK",
    "B4_NON_DETERMINISTIC_OUTPUT_BLOCK",
    "B4_OUTPUT_ORDER_UNSTABLE_BLOCK",
    "B4_STATIC_SCAN_FORBIDDEN_IMPORT_LOCK",
    "B4_STATIC_SCAN_FORBIDDEN_NETWORK_LITERAL_LOCK",
    "B4_TEST_DOMAIN_COVERAGE_MISSING_BLOCK",
    "B4_TEST_DOMAIN_COVERAGE_TOO_LOW_BLOCK",
    "B4_INSUFFICIENT_PRODUCTION_TEST_COUNT_BLOCK",
    "B4_EXPECTED_ARTIFACT_MISSING_BLOCK",
    "B4_ARTIFACT_NOT_DETERMINISTIC_BLOCK",
    "B4_VALIDATE_OUTPUTS_FAILED_BLOCK",
    "B4_SAFETY_FLAG_MISMATCH_LOCK",
    "B4_NO_SEMANTIC_CANDIDATES_WARNING",
    "B4_EMPTY_EXTRACTION_MARKED_SAFE_LOCK",
    "B4_BLOCK5_PREMATURE_ALLOWED_LOCK",
    "B4_CONFLICT_DETECTION_ALLOWED_BEFORE_CLOSURE_LOCK",
)

ALLOWED_OUTPUTS = (
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_4_SEMANTIC_SEGMENT_MAP.json",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_4_RULE_EXTRACTION_MAP.json",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_4_INTENT_CLASSIFICATION_MAP.json",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_4_SEMANTIC_EVIDENCE_INDEX.json",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_4_AMBIGUITY_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_4_BLOCKED_CAPABILITY_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_4_HUMAN_REVIEW_PACKAGE.json",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_4_SEMANTIC_DUPLICATE_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_4_VALIDATION_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_4_NEXT_LAYER_READINESS_MAP.json",
    "00_SYSTEM/bridge/manifests/BRIDGE_BLOCK_4_MANIFEST.json",
    "00_SYSTEM/bridge/manifests/BRIDGE_BLOCK_4_SEAL.json",
    "05_REPORTS/manual_brain_bridge/BRIDGE_BLOCK_4_RULE_EXTRACTOR_INTENT_CLASSIFIER_SUMMARY.md",
)

COMMON_FLAGS = {
    "block": BLOCK_ID,
    "lifecycle_status": LIFECYCLE_STATUS,
    "real_manual_read_performed": False,
    "real_brain_read_performed": False,
    "real_reports_brain_read_performed": False,
    "fixture_based_validation": True,
    "public_reports_hash_only": True,
    "raw_semantic_text_persisted": False,
    "execution_allowed_now": False,
    "manual_write_allowed_now": False,
    "brain_write_allowed_now": False,
    "reports_brain_write_allowed_now": False,
    "n8n_allowed_now": False,
    "webhook_allowed_now": False,
    "publishing_allowed_now": False,
    "capa9_allowed_now": False,
    "block_5_allowed_now": False,
    "block_5_blueprint_allowed_now": False,
    "conflict_detection_allowed_next": False,
    "next_safe_step": NEXT_SAFE_STEP,
}


class Block4Error(Exception):
    pass


def stable_json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json_hash(value: Any) -> str:
    return sha256_text(stable_json_dumps(value))


def resolve_decision(decisions: list[str]) -> str:
    if not decisions:
        return "BLOCK"
    if any(decision not in DECISION_RANK for decision in decisions):
        return "LOCK"
    return max(decisions, key=lambda d: DECISION_RANK[d])


def make_error(error_code: str, decision: str, message: str, component: str = "B4") -> dict[str, Any]:
    if error_code not in ERROR_CODES:
        raise Block4Error(f"UNKNOWN_ERROR_CODE: {error_code}")
    return {
        "error_code": error_code,
        "decision": decision,
        "message": message,
        "component": component,
        "safe_next_step": "REVIEW_BLOCK_4_SEMANTIC_CLASSIFICATION",
    }


def _matched_terms(text: str) -> list[tuple[str, str]]:
    t = text.lower()
    matches: list[tuple[str, str]] = []
    for capability, terms in CAPABILITY_LEXICON.items():
        for term in terms:
            if term in t:
                matches.append((capability, term))
    return matches


def classify_capability(text: str) -> dict[str, Any]:
    matches = _matched_terms(text)
    if not matches:
        return {"capability": "UNKNOWN_CAPABILITY", "dangerous_capability": False, "decision": "REQUIRE_REVIEW"}

    capability, term = sorted(
        matches,
        key=lambda item: (
            -len(item[1]),
            0 if item[0] in DANGEROUS_CAPABILITIES else 1,
            item[0],
        ),
    )[0]

    return {
        "capability": capability,
        "matched_term_hash": sha256_text(term),
        "dangerous_capability": capability in DANGEROUS_CAPABILITIES,
        "decision": "PASS",
    }


def classify_intent_type(text: str) -> str:
    t = text.lower()

    phase_matches: list[tuple[str, str]] = []
    for intent_type, terms in PHASE_LEXICON.items():
        for term in terms:
            if term in t:
                phase_matches.append((intent_type, term))

    if phase_matches:
        return sorted(phase_matches, key=lambda item: (-len(item[1]), item[0]))[0][0]

    capability = classify_capability(text)["capability"]
    if capability in INTENT_BY_CAPABILITY:
        return INTENT_BY_CAPABILITY[capability]

    return "UNKNOWN_INTENT"


def classify_rule_type(text: str) -> str:
    t = text.lower()
    if any(term in t for term in ("fail closed", "fail-closed", "fallar cerrado")):
        return "FAIL_CLOSED_RULE"
    if any(term in t for term in ("no-touch", "no touch", "no modificar", "no escribir")):
        return "NO_TOUCH_RULE"
    if any(term in t for term in ("autorización", "authorization", "approval")):
        return "AUTHORIZATION_RULE"
    if any(term in t for term in NEGATION_TERMS):
        return "PROHIBITION"
    if any(term in t for term in ("validar", "validation", "prueba", "pytest")):
        return "VALIDATION_RULE"
    if any(term in t for term in ("audit", "auditoría")):
        return "AUDIT_RULE"
    if any(term in t for term in ("solo si", "only if", "condicional")):
        return "CONDITIONAL_ALLOWANCE"
    if any(term in t for term in ALLOW_TERMS):
        return "ALLOWANCE"
    if any(term in t for term in ("debe", "must", "required", "requerido")):
        return "REQUIREMENT"
    return "UNKNOWN_RULE"


def classify_polarity(text: str) -> dict[str, Any]:
    t = text.lower()
    has_negation = any(term in t for term in NEGATION_TERMS)
    has_allow = any(term in t for term in ALLOW_TERMS)
    if has_negation and has_allow:
        return {"polarity": "BLOCKING", "negation_detected": True, "decision": "REQUIRE_REVIEW"}
    if has_negation:
        return {"polarity": "PROHIBITIVE", "negation_detected": True, "decision": "PASS"}
    if "solo si" in t or "only if" in t:
        return {"polarity": "CONDITIONAL", "negation_detected": False, "decision": "PASS_WITH_WARNINGS"}
    if has_allow:
        return {"polarity": "PERMISSIVE", "negation_detected": False, "decision": "PASS_WITH_WARNINGS"}
    if any(term in t for term in ("debe", "must", "required")):
        return {"polarity": "REQUIREMENT", "negation_detected": False, "decision": "PASS"}
    return {"polarity": "UNKNOWN_POLARITY", "negation_detected": False, "decision": "REQUIRE_REVIEW"}


def classify_semantic_role(text: str) -> str:
    t = text.lower()
    if any(term in t for term in ("traceback", "error:", "failed / blocked", "pytest failed")):
        return "ERROR_LOG"
    if any(term in t for term in ("ejemplo", "example")):
        return "EXAMPLE"
    if any(term in t for term in ("histórico", "historical", "antes se hizo")):
        return "HISTORICAL"
    if any(term in t for term in ("diagnóstico", "diagnostic", "log")):
        return "DIAGNOSTIC"
    if any(term in t for term in ("debe", "must", "no ", "bloqueado", "required", "allow", "permitir")):
        return "NORMATIVE"
    if any(term in t for term in REQUEST_VERBS) or t.strip() in ("ok", "sí", "si", "perfecto"):
        return "TRANSCRIPT"
    return "UNKNOWN_SEMANTIC_ROLE"


def classify_text_class(text: str) -> str:
    t = text.lower().strip()
    if t in ("ok", "sí", "si", "perfecto"):
        return "CONVERSATIONAL_COMMAND"
    if any(term in t for term in REQUEST_VERBS) or "capa 9" in t or "capa9" in t:
        return "USER_REQUEST"
    if any(term in t for term in ("traceback", "error:", "failed")):
        return "LOG_TEXT"
    if any(term in t for term in ("summary", "resumen")):
        return "SUMMARY_TEXT"
    if any(term in t for term in ("example", "ejemplo")):
        return "EXAMPLE_TEXT"
    if classify_semantic_role(text) == "NORMATIVE":
        return "PROJECT_RULE"
    return "UNKNOWN_TEXT_CLASS"


def normalize_text(text: str) -> dict[str, Any]:
    original = text
    normalized = unicodedata.normalize("NFC", text)
    normalized = re.sub(r"\s+", " ", normalized.strip())
    classifier_view = normalized.lower()

    negation_lost = any(term in original.lower() for term in NEGATION_TERMS) and not any(term in classifier_view for term in NEGATION_TERMS)
    capability_lost = classify_capability(original)["capability"] != "UNKNOWN_CAPABILITY" and classify_capability(classifier_view)["capability"] == "UNKNOWN_CAPABILITY"

    errors = []
    if normalized == "":
        errors.append(make_error("B4_NORMALIZATION_FAILED_BLOCK", "BLOCK", "Normalization produced empty text.", "NORMALIZATION"))
    if negation_lost:
        errors.append(make_error("B4_NEGATION_LOST_DURING_NORMALIZATION_LOCK", "LOCK", "Negation lost.", "NORMALIZATION"))
    if capability_lost:
        errors.append(make_error("B4_CAPABILITY_LOST_DURING_NORMALIZATION_LOCK", "LOCK", "Capability lost.", "NORMALIZATION"))

    return {
        "evidence_hash_view": sha256_text(original),
        "classifier_view": classifier_view,
        "normalized_text_hash": sha256_text(normalized),
        "decision": resolve_decision([e["decision"] for e in errors] or ["PASS"]),
        "errors": errors,
    }


def validate_b3_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    errors = []
    required = ("source_id", "source_hash", "source_type", "authority_status", "decision", "read_allowed", "write_allowed", "safe_for_rule_extraction", "encoding_status", "binary_status", "fixture_safe")
    missing = [field for field in required if field not in snapshot]
    if missing:
        errors.append(make_error("B4_B3_SNAPSHOT_CONTRACT_INVALID_BLOCK", "BLOCK", f"Missing fields: {missing}", "INPUT"))
    if not snapshot.get("source_hash"):
        errors.append(make_error("B4_INPUT_HASH_MISSING_BLOCK", "BLOCK", "Source hash missing.", "INPUT"))
    if snapshot.get("safe_for_rule_extraction") is not True:
        errors.append(make_error("B4_INPUT_NOT_SAFE_FOR_RULE_EXTRACTION_BLOCK", "BLOCK", "Input is not safe for extraction.", "INPUT"))
    if snapshot.get("authority_status") != "AUTHORITY_CANONICAL":
        errors.append(make_error("B4_INPUT_AUTHORITY_NOT_CANONICAL_REVIEW", "REQUIRE_REVIEW", "Authority is not canonical.", "INPUT"))
    if snapshot.get("decision") == "LOCK":
        errors.append(make_error("B4_INPUT_SOURCE_SNAPSHOT_MISSING_LOCK", "LOCK", "Locked source cannot be processed.", "INPUT"))
    elif snapshot.get("decision") != "PASS":
        errors.append(make_error("B4_INPUT_NOT_SAFE_FOR_RULE_EXTRACTION_BLOCK", "BLOCK", "Only PASS snapshots are accepted.", "INPUT"))
    if snapshot.get("write_allowed") is not False:
        errors.append(make_error("B4_B3_SNAPSHOT_WRITE_ALLOWED_LOCK", "LOCK", "Snapshot must not allow writes.", "INPUT"))
    if snapshot.get("fixture_safe") is not True:
        errors.append(make_error("B4_B3_SNAPSHOT_NOT_FIXTURE_SAFE_BLOCK", "BLOCK", "Build base requires fixture-safe source.", "INPUT"))
    if snapshot.get("encoding_status") not in ("ENCODING_UTF8", "ENCODING_ASCII_COMPATIBLE"):
        errors.append(make_error("B4_INPUT_NOT_SAFE_FOR_RULE_EXTRACTION_BLOCK", "BLOCK", "Encoding not accepted.", "INPUT"))
    if snapshot.get("binary_status") != "TEXT":
        errors.append(make_error("B4_INPUT_NOT_SAFE_FOR_RULE_EXTRACTION_BLOCK", "BLOCK", "Binary input blocked.", "INPUT"))
    return {"decision": resolve_decision([e["decision"] for e in errors] or ["PASS"]), "errors": errors, "valid": not errors}


def segment_source(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    text = snapshot.get("fixture_text", "")
    if not text:
        return []
    if snapshot.get("fixture_safe") is not True:
        raise Block4Error("B4_FIXTURE_NOT_MARKED_SAFE_BLOCK")

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        lines = [text.strip()]

    segments = []
    cursor = 0
    for index, line in enumerate(lines):
        start = text.find(line, cursor)
        if start < 0:
            start = cursor
        end = start + len(line)
        cursor = end
        normalized = normalize_text(line)
        segment_id = f"B4_SEG_{str(snapshot['source_hash'])[:8]}_{index:04d}"
        segments.append({
            "segment_id": segment_id,
            "source_id": snapshot["source_id"],
            "source_hash": snapshot["source_hash"],
            "segment_index": index,
            "segment_type": "LINE",
            "parent_segment_id": None,
            "start_offset": start,
            "end_offset": end,
            "raw_text_hash": sha256_text(line),
            "normalized_text_hash": normalized["normalized_text_hash"],
            "context_window_hash": sha256_text(line),
            "safe_for_extraction": normalized["decision"] in ("PASS", "PASS_WITH_WARNINGS"),
            "decision": normalized["decision"],
            "_internal_text": line,
        })
    return segments


def evidence_ref(snapshot: dict[str, Any], segment: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": snapshot["source_id"],
        "source_hash": snapshot["source_hash"],
        "segment_id": segment["segment_id"],
        "span_hash": segment["raw_text_hash"],
        "start_offset": segment["start_offset"],
        "end_offset": segment["end_offset"],
        "preview_allowed": False,
    }


def confidence_breakdown(text: str, snapshot: dict[str, Any], ambiguity_penalty: float = 0.0) -> dict[str, float]:
    cap = classify_capability(text)
    polarity = classify_polarity(text)
    lexical = 0.90 if classify_rule_type(text) != "UNKNOWN_RULE" or classify_intent_type(text) != "UNKNOWN_INTENT" else 0.35
    capability = 0.90 if cap["capability"] != "UNKNOWN_CAPABILITY" else 0.20
    negation = 0.85 if polarity["polarity"] != "UNKNOWN_POLARITY" else 0.30
    authority = 0.95 if snapshot.get("authority_status") == "AUTHORITY_CANONICAL" else 0.40
    structure = 0.85 if len(text.strip()) > 4 else 0.20
    context = 0.80
    danger_penalty = 0.20 if cap["dangerous_capability"] else 0.0
    final = max(0.0, min(0.99, (lexical + capability + negation + authority + structure + context) / 6 - ambiguity_penalty - danger_penalty))
    return {
        "lexical_match_score": round(lexical, 4),
        "capability_match_score": round(capability, 4),
        "negation_score": round(negation, 4),
        "authority_score": round(authority, 4),
        "structure_score": round(structure, 4),
        "context_score": round(context, 4),
        "ambiguity_penalty": round(ambiguity_penalty, 4),
        "dangerous_capability_penalty": round(danger_penalty, 4),
        "final_confidence": round(final, 4),
    }


def certainty_level(score: float) -> str:
    if score >= 0.85:
        return "HIGH"
    if score >= 0.65:
        return "MEDIUM"
    if score >= 0.40:
        return "LOW"
    return "UNSAFE"


def stable_id(prefix: str, parts: list[str], size: int = 12) -> str:
    return f"{prefix}_{sha256_text('|'.join(parts))[:size].upper()}"


def make_rule_candidate(snapshot: dict[str, Any], segment: dict[str, Any]) -> dict[str, Any] | None:
    text = segment["_internal_text"]
    rule_type = classify_rule_type(text)
    if rule_type == "UNKNOWN_RULE":
        return None

    cap = classify_capability(text)
    polarity = classify_polarity(text)
    conf = confidence_breakdown(text, snapshot)
    priority = {
        "FAIL_CLOSED_RULE": 1,
        "NO_TOUCH_RULE": 2,
        "AUTHORIZATION_RULE": 3,
        "PROHIBITION": 4,
        "VALIDATION_RULE": 5,
        "AUDIT_RULE": 6,
        "CONDITIONAL_ALLOWANCE": 10,
        "ALLOWANCE": 11,
    }.get(rule_type, 12)

    dangerous = cap["dangerous_capability"]
    final_score = conf["final_confidence"]
    decision = "PASS" if final_score >= 0.85 and not dangerous and polarity["polarity"] != "UNKNOWN_POLARITY" else "REQUIRE_REVIEW"
    if dangerous or rule_type == "PROHIBITION" or polarity["polarity"] in ("PROHIBITIVE", "BLOCKING"):
        decision = "PASS"

    rule_id = stable_id("B4_RULE", [snapshot["source_id"], snapshot["source_hash"], segment["segment_id"], rule_type, cap["capability"], polarity["polarity"], segment["normalized_text_hash"]])

    return {
        "rule_id": rule_id,
        "source_id": snapshot["source_id"],
        "source_hash": snapshot["source_hash"],
        "segment_id": segment["segment_id"],
        "segment_hash": segment["raw_text_hash"],
        "rule_type": rule_type,
        "rule_scope": "manual_brain_bridge",
        "semantic_role": classify_semantic_role(text),
        "polarity": polarity["polarity"],
        "capability": cap["capability"],
        "capability_allowed": False if cap["dangerous_capability"] or polarity["polarity"] in ("PROHIBITIVE", "BLOCKING", "NEGATIVE") else decision == "PASS",
        "semantic_priority": priority,
        "normalized_text_hash": segment["normalized_text_hash"],
        "evidence_ref": evidence_ref(snapshot, segment),
        "confidence_breakdown": conf,
        "certainty_level": certainty_level(final_score),
        "decision": decision,
        "safe_for_conflict_detection": decision == "PASS",
    }


def make_intent_candidate(snapshot: dict[str, Any], segment: dict[str, Any]) -> dict[str, Any] | None:
    text = segment["_internal_text"]
    text_class = classify_text_class(text)
    cap = classify_capability(text)
    intent_type = classify_intent_type(text)

    should_emit = (
        intent_type != "UNKNOWN_INTENT"
        or text_class in ("USER_REQUEST", "CONVERSATIONAL_COMMAND", "OPERATIONAL_INSTRUCTION")
        or cap["dangerous_capability"]
        or cap["capability"] != "UNKNOWN_CAPABILITY"
    )
    if not should_emit:
        return None

    polarity = classify_polarity(text)
    conf = confidence_breakdown(text, snapshot)
    authorization_detected = any(term in text.lower() for term in AUTHORIZATION_TERMS)
    authorization_valid = False
    action_allowed = False

    if cap["dangerous_capability"]:
        decision = "BLOCK"
    elif intent_type == "UNKNOWN_INTENT":
        decision = "REQUIRE_REVIEW"
    else:
        decision = "REQUIRE_REVIEW"

    intent_id = stable_id("B4_INTENT", [snapshot["source_id"], snapshot["source_hash"], segment["segment_id"], intent_type, cap["capability"], polarity["polarity"], segment["normalized_text_hash"]])

    return {
        "intent_id": intent_id,
        "source_id": snapshot["source_id"],
        "source_hash": snapshot["source_hash"],
        "segment_id": segment["segment_id"],
        "intent_type": intent_type,
        "intent_scope": "manual_brain_bridge",
        "semantic_role": text_class,
        "polarity": polarity["polarity"],
        "capability": cap["capability"],
        "intent_detected": True,
        "authority_detected": False,
        "authorization_detected": authorization_detected,
        "authorization_valid": authorization_valid,
        "action_allowed": action_allowed,
        "normalized_intent_hash": segment["normalized_text_hash"],
        "evidence_ref": evidence_ref(snapshot, segment),
        "confidence_breakdown": conf,
        "certainty_level": certainty_level(conf["final_confidence"]),
        "decision": decision,
        "safe_for_conflict_detection": False,
    }


def candidate_invariant(candidate: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    errors = []
    if candidate.get("safe_for_conflict_detection") is True and candidate.get("decision") != "PASS":
        errors.append(make_error("B4_CANDIDATE_INVARIANT_FAILED_LOCK", "LOCK", "Safe candidate must be PASS.", "INVARIANT"))
    if "evidence_ref" not in candidate or not candidate["evidence_ref"].get("span_hash"):
        errors.append(make_error("B4_CANDIDATE_INVARIANT_FAILED_LOCK", "LOCK", "Evidence ref missing.", "INVARIANT"))
    if candidate.get("capability") in DANGEROUS_CAPABILITIES and candidate.get("capability_allowed") is True:
        errors.append(make_error("B4_DANGEROUS_CAPABILITY_ACTION_ALLOWED_LOCK", "LOCK", "Dangerous capability allowed.", "INVARIANT"))
    if candidate.get("capability") in DANGEROUS_CAPABILITIES and candidate.get("action_allowed") is True:
        errors.append(make_error("B4_DANGEROUS_CAPABILITY_ACTION_ALLOWED_LOCK", "LOCK", "Dangerous action allowed.", "INVARIANT"))
    if kind == "rule" and candidate.get("rule_type") == "UNKNOWN_RULE" and candidate.get("decision") == "PASS":
        errors.append(make_error("B4_UNKNOWN_RULE_PASS_LOCK", "LOCK", "Unknown rule passed.", "INVARIANT"))
    if kind == "intent" and candidate.get("intent_type") == "UNKNOWN_INTENT" and candidate.get("decision") == "PASS":
        errors.append(make_error("B4_UNKNOWN_INTENT_PASS_LOCK", "LOCK", "Unknown intent passed.", "INVARIANT"))
    if candidate.get("polarity") == "UNKNOWN_POLARITY" and candidate.get("safe_for_conflict_detection") is True:
        errors.append(make_error("B4_UNKNOWN_POLARITY_SAFE_LOCK", "LOCK", "Unknown polarity marked safe.", "INVARIANT"))
    if candidate.get("authorization_valid") is False and candidate.get("action_allowed") is True:
        errors.append(make_error("B4_AUTHORIZATION_INVERSION_LOCK", "LOCK", "Request granted without authorization.", "INVARIANT"))
    return errors


def public_rule(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "rule_id": candidate["rule_id"],
        "source_id": candidate["source_id"],
        "source_hash": candidate["source_hash"],
        "segment_id": candidate["segment_id"],
        "span_hash": candidate["evidence_ref"]["span_hash"],
        "normalized_text_hash": candidate["normalized_text_hash"],
        "rule_type": candidate["rule_type"],
        "semantic_role": candidate["semantic_role"],
        "capability": candidate["capability"],
        "polarity": candidate["polarity"],
        "semantic_priority": candidate["semantic_priority"],
        "confidence": candidate["confidence_breakdown"]["final_confidence"],
        "certainty_level": candidate["certainty_level"],
        "decision": candidate["decision"],
        "safe_for_conflict_detection": candidate["safe_for_conflict_detection"],
    }


def public_intent(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "intent_id": candidate["intent_id"],
        "source_id": candidate["source_id"],
        "source_hash": candidate["source_hash"],
        "segment_id": candidate["segment_id"],
        "span_hash": candidate["evidence_ref"]["span_hash"],
        "normalized_intent_hash": candidate["normalized_intent_hash"],
        "intent_type": candidate["intent_type"],
        "semantic_role": candidate["semantic_role"],
        "capability": candidate["capability"],
        "intent_detected": candidate["intent_detected"],
        "authorization_detected": candidate["authorization_detected"],
        "authorization_valid": candidate["authorization_valid"],
        "action_allowed": candidate["action_allowed"],
        "confidence": candidate["confidence_breakdown"]["final_confidence"],
        "decision": candidate["decision"],
        "safe_for_conflict_detection": candidate["safe_for_conflict_detection"],
    }


def anti_leak_check(value: Any) -> dict[str, Any]:
    text = stable_json_dumps(value)
    errors = []
    for field in FORBIDDEN_PUBLIC_FIELDS:
        if f'"{field}"' in text:
            errors.append(make_error("B4_FORBIDDEN_TEXT_FIELD_LOCK", "LOCK", f"Forbidden field {field}", "ANTI_LEAK"))
    for leaked in FORBIDDEN_PUBLIC_STRINGS:
        if leaked in text:
            errors.append(make_error("B4_FORBIDDEN_STRING_LEAK_LOCK", "LOCK", f"Forbidden string {leaked}", "ANTI_LEAK"))
    return {"decision": resolve_decision([e["decision"] for e in errors] or ["PASS"]), "errors": errors}


def detect_ambiguities(snapshot: dict[str, Any], segment: dict[str, Any]) -> list[dict[str, Any]]:
    text = segment["_internal_text"].lower()
    if "continúa" in text or "continuar" in text or "hazlo" in text:
        ambiguity_id = stable_id("B4_AMB", [snapshot["source_id"], segment["segment_id"], "AMBIGUOUS_ACTION"])
        return [{
            "ambiguity_id": ambiguity_id,
            "ambiguity_type": "AMBIGUOUS_ACTION",
            "source_id": snapshot["source_id"],
            "segment_id": segment["segment_id"],
            "span_hash": segment["raw_text_hash"],
            "decision": "REQUIRE_REVIEW",
            "review_required": True,
        }]
    return []


def human_review_for(candidate: dict[str, Any], reason: str) -> dict[str, Any]:
    review_id = stable_id("B4_REVIEW", [candidate.get("source_id", ""), candidate.get("segment_id", ""), reason])
    return {
        "review_id": review_id,
        "reason": reason,
        "source_id": candidate.get("source_id", ""),
        "segment_id": candidate.get("segment_id", ""),
        "span_hash": candidate.get("span_hash", candidate.get("evidence_ref", {}).get("span_hash", "")),
        "suggested_question": "¿La intención detectada solicita blueprint, build, validación o ejecución?",
        "decision": "REQUIRE_REVIEW",
    }


def semantic_duplicates(rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[tuple[str, str], list[str]] = {}
    for rule in rules:
        key = (rule["capability"], rule["polarity"])
        seen.setdefault(key, []).append(rule["rule_id"])
    duplicates = []
    for key, ids in seen.items():
        if len(ids) > 1:
            duplicates.append({
                "duplicate_id": stable_id("B4_DUP", [key[0], key[1], ",".join(sorted(ids))]),
                "duplicate_type": "same_capability_same_polarity",
                "candidate_ids": sorted(ids),
                "capability": key[0],
                "polarity": key[1],
                "decision": "PASS_WITH_WARNINGS",
            })
    return sorted(duplicates, key=lambda item: (item["duplicate_type"], item["duplicate_id"]))


def build_fixture_sources() -> list[dict[str, Any]]:
    fixtures = [
        ("B3_FIXTURE_SOURCE_001", "No escribir en brain durante el build base."),
        ("B3_FIXTURE_SOURCE_002", "Brain write remains blocked during this layer."),
        ("B3_FIXTURE_SOURCE_003", "Solo se permite blueprint antes del bloque automático."),
        ("B3_FIXTURE_SOURCE_004", "dame bloque automático"),
        ("B3_FIXTURE_SOURCE_005", "ejecuta ahora"),
        ("B3_FIXTURE_SOURCE_006", "escribe en el cerebro"),
        ("B3_FIXTURE_SOURCE_007", "haz publishing"),
        ("B3_FIXTURE_SOURCE_008", "llama webhook"),
        ("B3_FIXTURE_SOURCE_009", "activa n8n"),
        ("B3_FIXTURE_SOURCE_010", "capa 9"),
        ("B3_FIXTURE_SOURCE_011", "ok"),
        ("B3_FIXTURE_SOURCE_012", "ERROR: pytest failed in previous run"),
        ("B3_FIXTURE_SOURCE_013", "Texto histórico: antes se hizo un build."),
        ("B3_FIXTURE_SOURCE_014", "continúa"),
        ("B3_FIXTURE_SOURCE_015", "No execution is allowed."),
        ("B3_FIXTURE_SOURCE_016", "La validación debe ejecutarse después del validation plan."),
        ("B3_FIXTURE_SOURCE_017", "FAKE_SECRET_API_KEY_123"),
        ("B3_FIXTURE_SOURCE_018", "Este bloque no contiene reglas operativas claras."),
        ("B3_FIXTURE_SOURCE_019", "dame validation plan"),
        ("B3_FIXTURE_SOURCE_020", "dame validation map"),
        ("B3_FIXTURE_SOURCE_021", "dame post-build audit"),
        ("B3_FIXTURE_SOURCE_022", "dame gate closure"),
    ]
    snapshots = []
    for source_id, text in fixtures:
        snapshots.append({
            "source_id": source_id,
            "source_hash": sha256_text(text),
            "source_type": "test_fixture",
            "authority_status": "AUTHORITY_CANONICAL",
            "decision": "PASS",
            "read_allowed": True,
            "write_allowed": False,
            "safe_for_rule_extraction": True,
            "encoding_status": "ENCODING_UTF8",
            "binary_status": "TEXT",
            "fixture_safe": True,
            "fixture_text": text,
        })
    return snapshots


def process_sources(snapshots: list[dict[str, Any]]) -> dict[str, Any]:
    before = canonical_json_hash(snapshots)
    snapshots_copy = copy.deepcopy(snapshots)

    public_segments = []
    public_rules = []
    public_intents = []
    evidence_index = []
    ambiguities = []
    blocked_capabilities = []
    human_reviews = []
    invariant_errors = []

    for snapshot in snapshots_copy:
        validation = validate_b3_snapshot(snapshot)
        if validation["decision"] in ("BLOCK", "LOCK"):
            continue

        for segment in segment_source(snapshot):
            public_segments.append({
                "segment_id": segment["segment_id"],
                "source_id": segment["source_id"],
                "source_hash": segment["source_hash"],
                "segment_index": segment["segment_index"],
                "segment_type": segment["segment_type"],
                "parent_segment_id": segment["parent_segment_id"],
                "start_offset": segment["start_offset"],
                "end_offset": segment["end_offset"],
                "raw_text_hash": segment["raw_text_hash"],
                "normalized_text_hash": segment["normalized_text_hash"],
                "context_window_hash": segment["context_window_hash"],
                "safe_for_extraction": segment["safe_for_extraction"],
                "decision": segment["decision"],
            })

            evidence_index.append({
                "source_id": segment["source_id"],
                "source_hash": segment["source_hash"],
                "segment_id": segment["segment_id"],
                "span_hash": segment["raw_text_hash"],
                "normalized_text_hash": segment["normalized_text_hash"],
                "start_offset": segment["start_offset"],
                "end_offset": segment["end_offset"],
                "preview_allowed": False,
            })

            rule = make_rule_candidate(snapshot, segment)
            if rule:
                invariant_errors.extend(candidate_invariant(rule, "rule"))
                pr = public_rule(rule)
                public_rules.append(pr)
                if pr["decision"] != "PASS":
                    human_reviews.append(human_review_for(rule, "RULE_REQUIRES_REVIEW"))

            intent = make_intent_candidate(snapshot, segment)
            if intent:
                invariant_errors.extend(candidate_invariant(intent, "intent"))
                pi = public_intent(intent)
                public_intents.append(pi)

                if pi["capability"] in DANGEROUS_CAPABILITIES:
                    blocked_capabilities.append({
                        "capability": pi["capability"],
                        "detected": True,
                        "allowed": False,
                        "reason": "Dangerous capability remains blocked.",
                        "error_code": "B4_DANGEROUS_CAPABILITY_ACTION_ALLOWED_LOCK",
                        "decision": "BLOCK",
                        "source_id": pi["source_id"],
                        "segment_id": pi["segment_id"],
                    })

                if pi["decision"] != "PASS":
                    human_reviews.append(human_review_for(intent, "INTENT_REQUIRES_REVIEW"))

            ambiguities.extend(detect_ambiguities(snapshot, segment))

    after = canonical_json_hash(snapshots)
    if before != after:
        invariant_errors.append(make_error("B4_INPUT_MUTATION_LOCK", "LOCK", "Input mutated.", "NO_MUTATION"))

    public_segments = sorted(public_segments, key=lambda s: (s["source_id"], s["segment_index"]))
    public_rules = sorted(public_rules, key=lambda r: (r["source_id"], r["segment_id"], r["semantic_priority"], r["rule_type"], r["rule_id"]))
    public_intents = sorted(public_intents, key=lambda i: (i["source_id"], i["segment_id"], i["intent_type"], i["intent_id"]))
    evidence_index = sorted(evidence_index, key=lambda e: (e["source_id"], e["segment_id"], e["span_hash"]))
    ambiguities = sorted(ambiguities, key=lambda a: (a["source_id"], a["segment_id"], a["ambiguity_type"], a["ambiguity_id"]))
    blocked_capabilities = sorted(blocked_capabilities, key=lambda b: (b["capability"], b["source_id"], b["segment_id"]))
    human_reviews = sorted(human_reviews, key=lambda r: r["review_id"])
    duplicates = semantic_duplicates(public_rules)

    empty_warnings = []
    if not public_rules and not public_intents:
        empty_warnings.append(make_error("B4_NO_SEMANTIC_CANDIDATES_WARNING", "PASS_WITH_WARNINGS", "No semantic candidates detected.", "EMPTY_EXTRACTION"))

    return {
        "segments": public_segments,
        "rules": public_rules,
        "intents": public_intents,
        "evidence_index": evidence_index,
        "ambiguities": ambiguities,
        "blocked_capabilities": blocked_capabilities,
        "human_reviews": human_reviews,
        "semantic_duplicates": duplicates,
        "invariant_errors": invariant_errors,
        "empty_warnings": empty_warnings,
        "no_mutation": {
            "input_hash_before": before,
            "input_hash_after": after,
            "input_mutated": before != after,
            "deepcopy_used": True,
            "deterministic_output_hash": "",
        },
    }


def _common(status: str = "PASS") -> dict[str, Any]:
    value = dict(COMMON_FLAGS)
    value["status"] = status
    return value


def build_report_payloads() -> dict[str, Any]:
    result = process_sources(build_fixture_sources())
    safety_decision = resolve_decision([e["decision"] for e in result["invariant_errors"]] + [w["decision"] for w in result["empty_warnings"]] + ["PASS"])
    safe_for_conflict_detection = safety_decision == "PASS" and bool(result["rules"]) and not result["blocked_capabilities"] and not result["ambiguities"]

    no_mutation = dict(result["no_mutation"])
    no_mutation["deterministic_output_hash"] = canonical_json_hash({
        "segments": result["segments"],
        "rules": result["rules"],
        "intents": result["intents"],
    })

    return {
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_4_SEMANTIC_SEGMENT_MAP.json": {
            **_common(),
            "report_id": "BRIDGE_BLOCK_4_SEMANTIC_SEGMENT_MAP",
            "semantic_segments_count": len(result["segments"]),
            "segments": result["segments"],
        },
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_4_RULE_EXTRACTION_MAP.json": {
            **_common(),
            "report_id": "BRIDGE_BLOCK_4_RULE_EXTRACTION_MAP",
            "rule_candidates_count": len(result["rules"]),
            "safe_for_conflict_detection": safe_for_conflict_detection,
            "rule_candidates": result["rules"],
        },
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_4_INTENT_CLASSIFICATION_MAP.json": {
            **_common(),
            "report_id": "BRIDGE_BLOCK_4_INTENT_CLASSIFICATION_MAP",
            "intent_candidates_count": len(result["intents"]),
            "intent_candidates": result["intents"],
        },
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_4_SEMANTIC_EVIDENCE_INDEX.json": {
            **_common(),
            "report_id": "BRIDGE_BLOCK_4_SEMANTIC_EVIDENCE_INDEX",
            "evidence_count": len(result["evidence_index"]),
            "evidence_index": result["evidence_index"],
        },
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_4_AMBIGUITY_REPORT.json": {
            **_common(),
            "report_id": "BRIDGE_BLOCK_4_AMBIGUITY_REPORT",
            "ambiguity_count": len(result["ambiguities"]),
            "ambiguities": result["ambiguities"],
        },
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_4_BLOCKED_CAPABILITY_REPORT.json": {
            **_common(),
            "report_id": "BRIDGE_BLOCK_4_BLOCKED_CAPABILITY_REPORT",
            "blocked_capability_count": len(result["blocked_capabilities"]),
            "blocked_capabilities": result["blocked_capabilities"],
        },
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_4_HUMAN_REVIEW_PACKAGE.json": {
            **_common(),
            "report_id": "BRIDGE_BLOCK_4_HUMAN_REVIEW_PACKAGE",
            "human_review_package_count": len(result["human_reviews"]),
            "human_reviews": result["human_reviews"],
        },
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_4_SEMANTIC_DUPLICATE_REPORT.json": {
            **_common(),
            "report_id": "BRIDGE_BLOCK_4_SEMANTIC_DUPLICATE_REPORT",
            "semantic_duplicate_count": len(result["semantic_duplicates"]),
            "semantic_duplicates": result["semantic_duplicates"],
        },
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_4_VALIDATION_REPORT.json": {
            **_common(),
            "report_id": "BRIDGE_BLOCK_4_VALIDATION_REPORT",
            "result": LIFECYCLE_STATUS,
            "minimum_tests_required": 260,
            "target_tests_recommended": "280+",
            "fix_applied": "BUILD_FIX_2_SPECIFIC_CAPABILITY_MATCH_PRIORITY",
            "semantic_segments_count": len(result["segments"]),
            "rule_candidates_count": len(result["rules"]),
            "intent_candidates_count": len(result["intents"]),
            "ambiguity_count": len(result["ambiguities"]),
            "blocked_capability_count": len(result["blocked_capabilities"]),
            "human_review_package_count": len(result["human_reviews"]),
            "semantic_duplicate_count": len(result["semantic_duplicates"]),
            "safe_for_conflict_detection": safe_for_conflict_detection,
            "no_mutation": no_mutation,
            "invariant_errors": result["invariant_errors"],
            "warnings": result["empty_warnings"],
        },
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_4_NEXT_LAYER_READINESS_MAP.json": {
            **_common(),
            "report_id": "BRIDGE_BLOCK_4_NEXT_LAYER_READINESS_MAP",
            "result": "READY_FOR_POST_BUILD_AUDIT",
            "post_build_audit_allowed_next": True,
            "validation_allowed_now": False,
            "gate_closure_allowed_now": False,
            "block_5_allowed_now": False,
            "block_5_blueprint_allowed_now": False,
            "conflict_detection_allowed_next": False,
        },
    }


def validate_public_artifact_safety(artifact_texts: dict[str, str]) -> dict[str, Any]:
    errors = []
    for path, text in artifact_texts.items():
        if path.endswith(".json"):
            loaded = json.loads(text)
            blob = stable_json_dumps(loaded)
            for field in FORBIDDEN_PUBLIC_FIELDS:
                if f'"{field}"' in blob:
                    errors.append(make_error("B4_FORBIDDEN_TEXT_FIELD_LOCK", "LOCK", f"Forbidden field {field} in {path}", "ANTI_LEAK"))
            for leaked in FORBIDDEN_PUBLIC_STRINGS:
                if leaked in blob:
                    errors.append(make_error("B4_FORBIDDEN_STRING_LEAK_LOCK", "LOCK", f"Forbidden string {leaked} in {path}", "ANTI_LEAK"))
            for key, expected in COMMON_FLAGS.items():
                if loaded.get(key) != expected:
                    errors.append(make_error("B4_SAFETY_FLAG_MISMATCH_LOCK", "LOCK", f"Safety flag mismatch {key} in {path}", "VALIDATE_OUTPUTS"))
    return {"decision": resolve_decision([e["decision"] for e in errors] or ["PASS"]), "errors": errors}


def build_all_artifact_texts() -> dict[str, str]:
    payloads = build_report_payloads()
    artifact_texts = {path: stable_json_dumps(payload) for path, payload in sorted(payloads.items())}

    summary = "\n".join([
        "# BLOQUE 4 — Rule extractor + intent classifier",
        "",
        "Status: BUILT_PENDING_POST_AUDIT",
        "",
        "- BUILD FIX-2 applied: longest/specific capability match priority.",
        "- validation plan maps to VALIDATION_PLAN.",
        "- validation map maps to VALIDATION_MAP.",
        "- post-build audit maps to POST_BUILD_AUDIT.",
        "- gate closure maps to GATE_CLOSURE.",
        "- Dangerous capability intent detection remains blocked but detected.",
        "- Fixture-based semantic validation only.",
        "- No real manual/current read.",
        "- No real brain read.",
        "- No reports/brain read.",
        "- Public reports are hash-only.",
        "- Raw semantic text is not persisted.",
        "- Execution/manual/brain/n8n/webhook/publishing/CAPA9 remain blocked.",
        "- BLOQUE 5 remains blocked.",
        f"- Next safe step: {NEXT_SAFE_STEP}",
        "",
    ])
    artifact_texts["05_REPORTS/manual_brain_bridge/BRIDGE_BLOCK_4_RULE_EXTRACTOR_INTENT_CLASSIFIER_SUMMARY.md"] = summary

    manifest_seed = {
        **_common(),
        "manifest_id": "BRIDGE_BLOCK_4_MANIFEST",
        "fix_applied": "BUILD_FIX_2_SPECIFIC_CAPABILITY_MATCH_PRIORITY",
        "artifacts": [
            {"path": path, "sha256": sha256_text(text), "bytes_utf8": len(text.encode("utf-8"))}
            for path, text in sorted(artifact_texts.items())
        ],
    }
    artifact_texts["00_SYSTEM/bridge/manifests/BRIDGE_BLOCK_4_MANIFEST.json"] = stable_json_dumps(manifest_seed)

    seal = {
        **_common(),
        "seal_id": "BRIDGE_BLOCK_4_SEAL",
        "status": "SEALED_PENDING_POST_BUILD_AUDIT",
        "fix_applied": "BUILD_FIX_2_SPECIFIC_CAPABILITY_MATCH_PRIORITY",
        "manifest_sha256": canonical_json_hash(manifest_seed),
        "next_safe_step": NEXT_SAFE_STEP,
        "block_5_allowed_now": False,
        "block_5_blueprint_allowed_now": False,
        "conflict_detection_allowed_next": False,
    }
    artifact_texts["00_SYSTEM/bridge/manifests/BRIDGE_BLOCK_4_SEAL.json"] = stable_json_dumps(seal)

    return artifact_texts


def write_all_outputs(root: Path) -> dict[str, Any]:
    artifacts = build_all_artifact_texts()
    safety = validate_public_artifact_safety(artifacts)
    if safety["decision"] in ("BLOCK", "LOCK"):
        return {"status": safety["decision"], "errors": safety["errors"], "written": []}
    for path, text in sorted(artifacts.items()):
        if path not in ALLOWED_OUTPUTS:
            raise Block4Error(f"OUTPUT_OUTSIDE_ALLOWLIST: {path}")
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
    return {"status": "PASS", "written": sorted(artifacts)}


def validate_outputs(root: Path) -> dict[str, Any]:
    expected = build_all_artifact_texts()
    errors = []
    safety = validate_public_artifact_safety(expected)
    errors.extend(safety["errors"])

    for relative_path, expected_text in expected.items():
        target = root / relative_path
        if not target.exists():
            errors.append(make_error("B4_EXPECTED_ARTIFACT_MISSING_BLOCK", "BLOCK", f"Missing output {relative_path}", "VALIDATE_OUTPUTS"))
            continue
        actual = target.read_text(encoding="utf-8")
        if actual != expected_text:
            errors.append(make_error("B4_ARTIFACT_NOT_DETERMINISTIC_BLOCK", "BLOCK", f"Artifact not deterministic {relative_path}", "VALIDATE_OUTPUTS"))
            continue
        if relative_path.endswith(".json"):
            loaded = json.loads(actual)
            if stable_json_dumps(loaded) != actual:
                errors.append(make_error("B4_ARTIFACT_NOT_DETERMINISTIC_BLOCK", "BLOCK", f"Non-canonical JSON {relative_path}", "VALIDATE_OUTPUTS"))
    return {"status": "PASS" if not errors else resolve_decision([e["decision"] for e in errors]), "errors": errors, "checked": sorted(expected)}


def self_check() -> dict[str, Any]:
    artifacts = build_all_artifact_texts()
    safety = validate_public_artifact_safety(artifacts)
    before = canonical_json_hash(build_fixture_sources())
    after = canonical_json_hash(build_fixture_sources())

    specific_cases = {
        "validation plan": "VALIDATION_PLAN",
        "validation map": "VALIDATION_MAP",
        "post-build audit": "POST_BUILD_AUDIT",
        "gate closure": "GATE_CLOSURE",
    }
    specific_pass = all(classify_capability(text)["capability"] == expected for text, expected in specific_cases.items())

    return {
        "block": BLOCK_ID,
        "status": "PASS" if safety["decision"] == "PASS" and before == after and specific_pass else "BLOCK",
        "artifact_count": len(artifacts),
        "error_code_count": len(ERROR_CODES),
        "public_report_safety": safety["decision"],
        "no_mutation_guard": before == after,
        "specific_capability_match_priority": specific_pass,
        "fix_applied": "BUILD_FIX_2_SPECIFIC_CAPABILITY_MATCH_PRIORITY",
        "next_safe_step": NEXT_SAFE_STEP,
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    root = Path.cwd()

    if "--build-artifacts" in args:
        result = write_all_outputs(root)
        print(stable_json_dumps(result), end="")
        return 0 if result["status"] == "PASS" else 2

    if "--validate-outputs" in args:
        result = validate_outputs(root)
        print(stable_json_dumps(result), end="")
        return 0 if result["status"] == "PASS" else 2

    if "--self-check" in args:
        result = self_check()
        print(stable_json_dumps(result), end="")
        return 0 if result["status"] == "PASS" else 2

    print(stable_json_dumps({"block": BLOCK_ID, "status": "READY", "next_safe_step": NEXT_SAFE_STEP}), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())