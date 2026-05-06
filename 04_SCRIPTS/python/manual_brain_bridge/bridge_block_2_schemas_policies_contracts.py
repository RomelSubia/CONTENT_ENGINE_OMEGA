from __future__ import annotations

import ast
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

BLOCK_ID = "BLOQUE_2_SCHEMAS_POLICIES_CONTRACTS"
NEXT_SAFE_STEP = "BLOQUE_2_POST_BUILD_AUDIT"

DECISION_RANK = {
    "PASS": 0,
    "PASS_WITH_WARNINGS": 1,
    "REQUIRE_REVIEW": 2,
    "BLOCK": 3,
    "LOCK": 4,
}

NO_TOUCH_PREFIXES = (
    "00_SYSTEM/brain/",
    "00_SYSTEM/reports/brain/",
    "00_SYSTEM/manual/current/",
    "00_SYSTEM/manual/historical/",
    "00_SYSTEM/manual/manifest/",
    "00_SYSTEM/manual/registry/",
)

ALLOWED_OUTPUTS = (
    "04_SCRIPTS/python/manual_brain_bridge/bridge_block_2_schemas_policies_contracts.py",
    "tests/manual_brain_bridge/test_bridge_block_2_schemas_policies_contracts.py",
    "00_SYSTEM/bridge/schemas/BRIDGE_BLOCK_2_SCHEMA_REGISTRY.json",
    "00_SYSTEM/bridge/policies/BRIDGE_BLOCK_2_POLICY_REGISTRY.json",
    "00_SYSTEM/bridge/contracts/BRIDGE_BLOCK_2_CONTRACT_REGISTRY.json",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_2_SCHEMA_REGISTRY_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_2_POLICY_REGISTRY_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_2_CONTRACT_REGISTRY_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_2_PERMISSION_MODEL_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_2_SECURITY_GUARDS_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_2_VALIDATION_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_2_NEXT_LAYER_READINESS_MAP.json",
    "00_SYSTEM/bridge/manifests/BRIDGE_BLOCK_2_MANIFEST.json",
    "00_SYSTEM/bridge/manifests/BRIDGE_BLOCK_2_SEAL.json",
    "05_REPORTS/manual_brain_bridge/BRIDGE_BLOCK_2_SCHEMAS_POLICIES_CONTRACTS_SUMMARY.md",
)

DANGEROUS_IMPORTS = {
    "subprocess",
    "requests",
    "httpx",
    "socket",
    "webbrowser",
    "ftplib",
    "smtplib",
}

DANGEROUS_CALLS = {
    "os.system",
    "shutil.rmtree",
    "Path.unlink",
}

EXTERNAL_CALL_NAMES = {
    "urlopen",
    "sendmail",
    "connect",
    "request",
}

SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key)\s*[:=]\s*['\"][^'\"]+['\"]"),
    re.compile(r"(?i)(password)\s*[:=]\s*['\"][^'\"]+['\"]"),
    re.compile(r"(?i)(private[_-]?key)\s*[:=]\s*['\"][^'\"]+['\"]"),
    re.compile(r"(?i)(authorization)\s*:\s*bearer\s+[A-Za-z0-9._\-]+"),
    re.compile(r"\bsk-[A-Za-z0-9]{12,}\b"),
)

SCHEMA_IDS = (
    "BridgeSystemStateSchema",
    "BridgeLayerStateSchema",
    "ManualSourceRefSchema",
    "BrainSourceRefSchema",
    "PolicyRuleSchema",
    "GovernancePolicySchema",
    "PermissionStateSchema",
    "HumanApprovalStateSchema",
    "ExecutionBoundarySchema",
    "EvidencePointerSchema",
    "TraceabilityRecordSchema",
    "ContractInputSchema",
    "ContractOutputSchema",
    "ErrorEnvelopeSchema",
    "DecisionEnvelopeSchema",
    "NextStepRecommendationSchema",
    "PathPolicySchema",
    "StaticImportScanSchema",
    "ExternalIOPolicySchema",
    "RegistrySelfValidationSchema",
    "DeveloperDiagnosticSchema",
    "StableErrorCodeSchema",
)

POLICY_IDS = (
    "NO_TOUCH_POLICY",
    "NO_EXECUTION_POLICY",
    "NO_EXTERNAL_ACTION_POLICY",
    "NO_CAPA9_POLICY",
    "EVIDENCE_REQUIRED_POLICY",
    "PERMISSION_FALSE_BY_DEFAULT_POLICY",
    "HUMAN_AUTH_REQUIRED_POLICY",
    "WARNING_VISIBILITY_POLICY",
    "STATE_MACHINE_POLICY",
    "COMMIT_PUSH_GATE_POLICY",
    "TEST_GATE_POLICY",
    "UNKNOWN_STATE_LOCK_POLICY",
    "PATH_CANONICALIZATION_POLICY",
    "STATIC_IMPORT_POLICY",
    "EXTERNAL_IO_BAN_POLICY",
    "SECRET_LEAKAGE_POLICY",
    "DETERMINISM_POLICY",
    "FAILURE_ARTIFACT_POLICY",
    "PERFORMANCE_BOUNDARY_POLICY",
    "DEVELOPER_DIAGNOSTICS_POLICY",
)

POLICY_PRECEDENCE = (
    "NO_TOUCH_POLICY",
    "NO_CAPA9_POLICY",
    "NO_EXECUTION_POLICY",
    "NO_EXTERNAL_ACTION_POLICY",
    "STATIC_IMPORT_POLICY",
    "EXTERNAL_IO_BAN_POLICY",
    "PATH_CANONICALIZATION_POLICY",
    "PERMISSION_FALSE_BY_DEFAULT_POLICY",
    "HUMAN_AUTH_REQUIRED_POLICY",
    "UNKNOWN_STATE_LOCK_POLICY",
    "EVIDENCE_REQUIRED_POLICY",
    "DETERMINISM_POLICY",
    "WARNING_VISIBILITY_POLICY",
    "COMMIT_PUSH_GATE_POLICY",
    "TEST_GATE_POLICY",
    "DEVELOPER_DIAGNOSTICS_POLICY",
)

CONTRACT_IDS = (
    "BlueprintRequestContract",
    "BlueprintOutputContract",
    "ReviewHardeningContract",
    "FinalApprovalContract",
    "ImplementationPlanRequestContract",
    "BuildRequestContract",
    "ValidationRequestContract",
    "AuditRequestContract",
    "ClosureRequestContract",
    "NextLayerRecommendationContract",
    "HumanApprovalContract",
    "PermissionContract",
    "NoTouchContract",
    "EvidenceContract",
    "ErrorContract",
    "DecisionContract",
    "PathSafetyContract",
    "StaticImportScanContract",
    "ExternalIOBanContract",
    "FailureArtifactContract",
    "DeveloperDiagnosticsContract",
)

STABLE_ERROR_CODES = (
    "B2_SCHEMA_MISSING_ID",
    "B2_SCHEMA_INVALID_VERSION",
    "B2_SCHEMA_DOWNGRADE_LOCK",
    "B2_SCHEMA_UNKNOWN_FIELD_LOCK",
    "B2_POLICY_MISSING_ID",
    "B2_POLICY_CONFLICT_LOCK",
    "B2_CONTRACT_INCOMPATIBLE_OUTPUT_LOCK",
    "B2_PERMISSION_INJECTION_LOCK",
    "B2_PATH_OUTSIDE_ROOT_LOCK",
    "B2_PATH_NO_TOUCH_LOCK",
    "B2_IMPORT_DANGEROUS_LOCK",
    "B2_EXTERNAL_IO_LOCK",
    "B2_SECRET_LEAKAGE_LOCK",
    "B2_JSON_NON_CANONICAL_BLOCK",
    "B2_HASH_UNSTABLE_BLOCK",
    "B2_REGISTRY_SELF_VALIDATION_BLOCK",
    "B2_SCOPE_ESCALATION_LOCK",
    "B2_NEXT_STEP_UNSAFE_BLOCK",
    "B2_CAPA9_LOCK",
)

FORBIDDEN_ACTION_TERMS = {
    "execution_allowed": ("execute", "auto_execute", "run_command", "shell"),
    "manual_write_allowed": ("patch_manual", "write_manual", "manual_write"),
    "brain_write_allowed": ("mutate_brain", "write_brain", "brain_write"),
    "reports_brain_write_allowed": ("write_reports_brain", "reports_brain_write"),
    "n8n_allowed": ("call_n8n", "n8n"),
    "webhook_allowed": ("call_webhook", "webhook"),
    "publishing_allowed": ("publish", "publishing"),
    "capa9_allowed": ("capa9", "capa_9"),
}


class Block2Error(Exception):
    """Fail-closed exception for block 2 validation."""


def stable_json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json_hash(value: Any) -> str:
    return sha256_text(stable_json_dumps(value))


def is_semver(value: str) -> bool:
    return bool(re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", value))


def make_error(
    error_code: str,
    severity: str,
    decision: str,
    failed_component: str,
    message_human: str,
    message_technical: str,
    safe_next_step: str,
) -> dict[str, Any]:
    if error_code not in STABLE_ERROR_CODES:
        raise Block2Error(f"Unknown error code: {error_code}")
    if decision not in ("REQUIRE_REVIEW", "BLOCK", "LOCK"):
        raise Block2Error("Error envelope cannot produce PASS")
    return {
        "error_code": error_code,
        "severity": severity,
        "decision": decision,
        "failed_component": failed_component,
        "message_human": message_human,
        "message_technical": message_technical,
        "safe_next_step": safe_next_step,
    }


def make_decision(status: str, reason: str, evidence: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    if status not in DECISION_RANK:
        raise Block2Error(f"Unknown decision status: {status}")
    return {
        "block": BLOCK_ID,
        "status": status,
        "reason": reason,
        "evidence": evidence or [],
        "next_safe_step": NEXT_SAFE_STEP,
        "forbidden_actions": [
            "execution",
            "manual_write",
            "brain_write",
            "reports_brain_write",
            "n8n",
            "webhook",
            "publishing",
            "capa9",
        ],
    }


def resolve_policy_precedence(decisions: list[str]) -> str:
    if not decisions:
        return "BLOCK"
    if any(decision not in DECISION_RANK for decision in decisions):
        return "LOCK"
    return max(decisions, key=lambda decision: DECISION_RANK[decision])


def assert_inside_root(root: Path, relative_path: str) -> Path:
    if not relative_path or "\x00" in relative_path:
        raise Block2Error("Invalid empty or null path")
    raw = relative_path.replace("\\", "/")
    if raw.startswith("/") or re.match(r"^[A-Za-z]:/", raw):
        raise Block2Error("Absolute paths are forbidden")
    if any(part == ".." for part in Path(raw).parts):
        raise Block2Error("Path traversal is forbidden")
    root_resolved = root.resolve(strict=True)
    candidate = (root_resolved / raw).resolve(strict=False)
    if not candidate.is_relative_to(root_resolved):
        raise Block2Error("Resolved path escapes root")
    return candidate


def detect_no_touch_path(relative_path: str) -> bool:
    normalized = relative_path.replace("\\", "/").lstrip("./")
    return any(normalized.startswith(prefix) for prefix in NO_TOUCH_PREFIXES)


def normalize_relative_path(root: Path, relative_path: str) -> str:
    candidate = assert_inside_root(root, relative_path)
    root_resolved = root.resolve(strict=True)
    normalized = candidate.relative_to(root_resolved).as_posix()
    if detect_no_touch_path(normalized):
        raise Block2Error("No-touch path is forbidden")
    return normalized


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _call_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def scan_for_dangerous_imports(source_text: str) -> dict[str, Any]:
    source_text = source_text.lstrip("\ufeff")
    tree = ast.parse(source_text)
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top in DANGEROUS_IMPORTS:
                    hits.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            top = (node.module or "").split(".")[0]
            if top in DANGEROUS_IMPORTS:
                hits.append(node.module or "")
        elif isinstance(node, ast.Call):
            name = _call_name(node.func)
            if name in DANGEROUS_CALLS or name == "__import__":
                hits.append(name)
    return {"status": "LOCK" if hits else "PASS", "hits": sorted(set(hits))}


def scan_for_external_io(source_text: str) -> dict[str, Any]:
    source_text = source_text.lstrip("\ufeff")
    tree = ast.parse(source_text)
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = _call_name(node.func)
            leaf = name.split(".")[-1]
            if leaf in EXTERNAL_CALL_NAMES:
                hits.append(name)
    return {"status": "LOCK" if hits else "PASS", "hits": sorted(set(hits))}


def scan_for_secret_leakage(text: str) -> dict[str, Any]:
    hits = [pattern.pattern for pattern in SECRET_PATTERNS if pattern.search(text)]
    return {"status": "LOCK" if hits else "PASS", "hits": hits}


def validate_canonical_json(text: str) -> bool:
    try:
        loaded = json.loads(text)
    except json.JSONDecodeError:
        return False
    return text == stable_json_dumps(loaded)


def _schema_record(schema_id: str) -> dict[str, Any]:
    return {
        "schema_id": schema_id,
        "schema_version": "1.0.0",
        "compatibility": "STRICT",
        "required_fields": ["schema_id", "schema_version"],
        "optional_fields": [],
        "forbidden_fields": [],
        "allowed_values": {},
        "blocked_values": {},
        "unknown_field_policy": "LOCK",
        "fail_closed_on_missing": True,
        "fail_closed_on_unknown": True,
        "governance_validation_required": True,
    }


def build_schema_registry() -> dict[str, Any]:
    return {
        "registry_id": "BRIDGE_BLOCK_2_SCHEMA_REGISTRY",
        "block": BLOCK_ID,
        "registry_version": "1.0.0",
        "authority_active_now": True,
        "schemas": [_schema_record(schema_id) for schema_id in SCHEMA_IDS],
    }


def build_policy_registry() -> dict[str, Any]:
    policies = []
    for index, policy_id in enumerate(POLICY_IDS):
        policies.append({
            "policy_id": policy_id,
            "policy_version": "1.0.0",
            "scope": "BLOQUE_2",
            "precedence": POLICY_PRECEDENCE.index(policy_id) if policy_id in POLICY_PRECEDENCE else 999,
            "default_decision": "BLOCK",
            "lock_conditions": [],
            "block_conditions": [],
            "review_conditions": [],
            "pass_conditions": ["explicitly_validated"],
            "evidence_required": True,
            "fail_closed": True,
            "stable_order": index,
        })
    return {
        "registry_id": "BRIDGE_BLOCK_2_POLICY_REGISTRY",
        "block": BLOCK_ID,
        "registry_version": "1.0.0",
        "decision_precedence": list(DECISION_RANK.keys()),
        "policy_precedence": list(POLICY_PRECEDENCE),
        "policies": policies,
    }


def build_contract_registry() -> dict[str, Any]:
    contracts = []
    for contract_id in CONTRACT_IDS:
        contracts.append({
            "contract_id": contract_id,
            "contract_version": "1.0.0",
            "input_schema": "ContractInputSchema",
            "output_schema": "ContractOutputSchema",
            "forbidden_outputs": ["ExecutionOutputContract", "ExternalActionGrant", "ManualWriteGrant"],
            "required_evidence": ["EvidencePointerSchema"],
            "required_permissions": [],
            "forbidden_permissions": [
                "execution_allowed",
                "manual_write_allowed",
                "brain_write_allowed",
                "reports_brain_write_allowed",
                "n8n_allowed",
                "webhook_allowed",
                "publishing_allowed",
                "capa9_allowed",
            ],
            "compatible_next_steps": [NEXT_SAFE_STEP],
            "incompatible_next_steps": ["BLOQUE_3", "EXECUTION", "CAPA9"],
            "fail_closed": True,
        })
    return {
        "registry_id": "BRIDGE_BLOCK_2_CONTRACT_REGISTRY",
        "block": BLOCK_ID,
        "registry_version": "1.0.0",
        "contracts": contracts,
    }


def validate_schema_registry(registry: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    seen: set[str] = set()
    for schema in registry.get("schemas", []):
        schema_id = schema.get("schema_id")
        version = schema.get("schema_version")
        if not schema_id:
            errors.append(make_error("B2_SCHEMA_MISSING_ID", "HIGH", "BLOCK", "SCHEMA", "Schema without id.", "schema_id missing", "Fix schema registry."))
        if schema_id in seen:
            errors.append(make_error("B2_REGISTRY_SELF_VALIDATION_BLOCK", "HIGH", "BLOCK", "SCHEMA", "Duplicate schema id.", f"duplicate schema_id {schema_id}", "Deduplicate registry."))
        seen.add(schema_id)
        if not isinstance(version, str) or not is_semver(version):
            errors.append(make_error("B2_SCHEMA_INVALID_VERSION", "HIGH", "BLOCK", "SCHEMA", "Invalid schema version.", f"invalid schema_version {version}", "Fix semantic version."))
        if schema.get("unknown_field_policy") not in ("LOCK", "BLOCK", "REQUIRE_REVIEW"):
            errors.append(make_error("B2_SCHEMA_UNKNOWN_FIELD_LOCK", "CRITICAL", "LOCK", "SCHEMA", "Invalid unknown field policy.", "unknown_field_policy invalid", "Lock and review schema."))
    expected = set(SCHEMA_IDS)
    actual = {schema.get("schema_id") for schema in registry.get("schemas", [])}
    missing = sorted(expected - actual)
    if missing:
        errors.append(make_error("B2_REGISTRY_SELF_VALIDATION_BLOCK", "HIGH", "BLOCK", "SCHEMA", "Missing required schemas.", f"missing={missing}", "Complete schema registry."))
    return {"status": "PASS" if not errors else resolve_policy_precedence([e["decision"] for e in errors]), "errors": errors}


def validate_policy_registry(registry: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    actual = {policy.get("policy_id") for policy in registry.get("policies", [])}
    for policy_id in POLICY_IDS:
        if policy_id not in actual:
            errors.append(make_error("B2_POLICY_MISSING_ID", "HIGH", "BLOCK", "POLICY", "Missing required policy.", policy_id, "Complete policy registry."))
    for policy in registry.get("policies", []):
        if policy.get("evidence_required") is not True or policy.get("fail_closed") is not True:
            errors.append(make_error("B2_POLICY_CONFLICT_LOCK", "CRITICAL", "LOCK", "POLICY", "Policy is not fail-closed.", str(policy), "Lock policy."))
    return {"status": "PASS" if not errors else resolve_policy_precedence([e["decision"] for e in errors]), "errors": errors}


def validate_contract_compatibility(contract: dict[str, Any], output_name: str | None = None) -> dict[str, Any]:
    forbidden = set(contract.get("forbidden_outputs", []))
    if output_name and output_name in forbidden:
        return {
            "status": "LOCK",
            "error": make_error(
                "B2_CONTRACT_INCOMPATIBLE_OUTPUT_LOCK",
                "CRITICAL",
                "LOCK",
                "CONTRACT",
                "Contract produced a forbidden output.",
                f"{contract.get('contract_id')} -> {output_name}",
                "Fix contract compatibility matrix.",
            ),
        }
    if not contract.get("input_schema") or not contract.get("output_schema"):
        return {
            "status": "BLOCK",
            "error": make_error(
                "B2_CONTRACT_INCOMPATIBLE_OUTPUT_LOCK",
                "HIGH",
                "BLOCK",
                "CONTRACT",
                "Contract lacks schema binding.",
                str(contract),
                "Add input/output schema.",
            ),
        }
    return {"status": "PASS", "error": None}


def validate_contract_registry(registry: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    actual = {contract.get("contract_id") for contract in registry.get("contracts", [])}
    missing = sorted(set(CONTRACT_IDS) - actual)
    if missing:
        errors.append(make_error("B2_CONTRACT_INCOMPATIBLE_OUTPUT_LOCK", "HIGH", "BLOCK", "CONTRACT", "Missing required contracts.", f"missing={missing}", "Complete contract registry."))
    for contract in registry.get("contracts", []):
        result = validate_contract_compatibility(contract)
        if result["error"]:
            errors.append(result["error"])
    return {"status": "PASS" if not errors else resolve_policy_precedence([e["decision"] for e in errors]), "errors": errors}


def permission_model_false_by_default() -> dict[str, bool]:
    return {
        "manual_write_allowed": False,
        "brain_write_allowed": False,
        "reports_brain_write_allowed": False,
        "execution_allowed": False,
        "external_execution_allowed": False,
        "n8n_allowed": False,
        "webhook_allowed": False,
        "publishing_allowed": False,
        "capa9_allowed": False,
        "build_allowed_now": False,
        "automatic_block_allowed_now": False,
    }


def _collect_terms(value: Any) -> list[str]:
    terms: list[str] = []
    if isinstance(value, str):
        terms.append(value.lower())
    elif isinstance(value, dict):
        for child in value.values():
            terms.extend(_collect_terms(child))
    elif isinstance(value, list):
        for child in value:
            terms.extend(_collect_terms(child))
    return terms


def detect_false_permission_injection(payload: dict[str, Any]) -> dict[str, Any]:
    permissions = payload.get("permissions", {})
    terms = _collect_terms({
        "capabilities": payload.get("capabilities", []),
        "actions": payload.get("actions", []),
        "allowed_actions": payload.get("allowed_actions", []),
        "next_safe_step": payload.get("next_safe_step", ""),
        "contract_outputs": payload.get("contract_outputs", []),
        "recommendations": payload.get("recommendations", []),
        "surface_map": payload.get("surface_map", {}),
        "risk_map": payload.get("risk_map", {}),
    })
    joined = " ".join(terms)
    hits: list[str] = []
    for permission, forbidden_terms in FORBIDDEN_ACTION_TERMS.items():
        if permissions.get(permission) is False:
            for term in forbidden_terms:
                if term.lower() in joined:
                    hits.append(f"{permission}:{term}")
    return {"status": "LOCK" if hits else "PASS", "hits": sorted(set(hits))}


def validate_registry_self_consistency(
    schema_registry: dict[str, Any],
    policy_registry: dict[str, Any],
    contract_registry: dict[str, Any],
) -> dict[str, Any]:
    results = [
        validate_schema_registry(schema_registry),
        validate_policy_registry(policy_registry),
        validate_contract_registry(contract_registry),
    ]
    status = resolve_policy_precedence([result["status"] for result in results])
    errors: list[dict[str, Any]] = []
    for result in results:
        errors.extend(result.get("errors", []))
    return {"status": status, "errors": errors}


def build_manifest(artifact_texts: dict[str, str]) -> dict[str, Any]:
    return {
        "manifest_id": "BRIDGE_BLOCK_2_MANIFEST",
        "block": BLOCK_ID,
        "canonical_json": True,
        "artifacts": [
            {
                "path": path,
                "sha256": sha256_text(text),
                "bytes_utf8": len(text.encode("utf-8")),
            }
            for path, text in sorted(artifact_texts.items())
        ],
    }


def build_seal(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "seal_id": "BRIDGE_BLOCK_2_SEAL",
        "block": BLOCK_ID,
        "manifest_sha256": canonical_json_hash(manifest),
        "status": "SEALED_PENDING_POST_BUILD_AUDIT",
        "next_safe_step": NEXT_SAFE_STEP,
    }


def build_all_artifact_texts() -> dict[str, str]:
    schema_registry = build_schema_registry()
    policy_registry = build_policy_registry()
    contract_registry = build_contract_registry()
    permission_model = permission_model_false_by_default()
    self_validation = validate_registry_self_consistency(schema_registry, policy_registry, contract_registry)

    reports: dict[str, Any] = {
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_2_SCHEMA_REGISTRY_REPORT.json": {
            "report_id": "BRIDGE_BLOCK_2_SCHEMA_REGISTRY_REPORT",
            "status": validate_schema_registry(schema_registry)["status"],
            "schema_count": len(schema_registry["schemas"]),
            "next_safe_step": NEXT_SAFE_STEP,
        },
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_2_POLICY_REGISTRY_REPORT.json": {
            "report_id": "BRIDGE_BLOCK_2_POLICY_REGISTRY_REPORT",
            "status": validate_policy_registry(policy_registry)["status"],
            "policy_count": len(policy_registry["policies"]),
            "policy_precedence": list(POLICY_PRECEDENCE),
            "next_safe_step": NEXT_SAFE_STEP,
        },
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_2_CONTRACT_REGISTRY_REPORT.json": {
            "report_id": "BRIDGE_BLOCK_2_CONTRACT_REGISTRY_REPORT",
            "status": validate_contract_registry(contract_registry)["status"],
            "contract_count": len(contract_registry["contracts"]),
            "next_safe_step": NEXT_SAFE_STEP,
        },
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_2_PERMISSION_MODEL_REPORT.json": {
            "report_id": "BRIDGE_BLOCK_2_PERMISSION_MODEL_REPORT",
            "status": "PASS",
            "permissions": permission_model,
            "next_safe_step": NEXT_SAFE_STEP,
        },
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_2_SECURITY_GUARDS_REPORT.json": {
            "report_id": "BRIDGE_BLOCK_2_SECURITY_GUARDS_REPORT",
            "status": "PASS",
            "guards": {
                "path_canonicalization": "DEFINED",
                "dangerous_import_scan": "DEFINED",
                "external_io_ban": "DEFINED",
                "secret_leakage_scan": "DEFINED",
                "false_permission_injection": "DEFINED",
                "no_touch": "DEFINED",
                "capa9": "LOCKED",
            },
            "next_safe_step": NEXT_SAFE_STEP,
        },
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_2_VALIDATION_REPORT.json": {
            "report_id": "BRIDGE_BLOCK_2_VALIDATION_REPORT",
            "status": self_validation["status"],
            "self_validation_errors": self_validation["errors"],
            "canonical_json": True,
            "next_safe_step": NEXT_SAFE_STEP,
        },
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_2_NEXT_LAYER_READINESS_MAP.json": {
            "report_id": "BRIDGE_BLOCK_2_NEXT_LAYER_READINESS_MAP",
            "status": "READY_FOR_POST_BUILD_AUDIT",
            "next_safe_step": NEXT_SAFE_STEP,
            "block_3_allowed_now": False,
            "execution_allowed_now": False,
            "manual_write_allowed_now": False,
            "brain_write_allowed_now": False,
            "n8n_allowed_now": False,
            "webhook_allowed_now": False,
            "publishing_allowed_now": False,
            "capa9_allowed_now": False,
        },
    }

    artifact_texts: dict[str, str] = {
        "00_SYSTEM/bridge/schemas/BRIDGE_BLOCK_2_SCHEMA_REGISTRY.json": stable_json_dumps(schema_registry),
        "00_SYSTEM/bridge/policies/BRIDGE_BLOCK_2_POLICY_REGISTRY.json": stable_json_dumps(policy_registry),
        "00_SYSTEM/bridge/contracts/BRIDGE_BLOCK_2_CONTRACT_REGISTRY.json": stable_json_dumps(contract_registry),
    }

    for path, report in reports.items():
        artifact_texts[path] = stable_json_dumps(report)

    summary = "\n".join([
        "# BRIDGE BLOCK 2 — Schemas + Policies + Contracts",
        "",
        "Status: BUILT_PENDING_POST_BUILD_AUDIT",
        "",
        "- Hardened schema registry generated.",
        "- Policy registry with precedence generated.",
        "- Contract registry with compatibility checks generated.",
        "- Permissions remain false by default.",
        "- No execution, no external IO, no manual write, no brain write.",
        f"- Next safe step: {NEXT_SAFE_STEP}",
        "",
    ])
    artifact_texts["05_REPORTS/manual_brain_bridge/BRIDGE_BLOCK_2_SCHEMAS_POLICIES_CONTRACTS_SUMMARY.md"] = summary

    manifest_inputs = copy.deepcopy(artifact_texts)
    manifest = build_manifest(manifest_inputs)
    seal = build_seal(manifest)
    artifact_texts["00_SYSTEM/bridge/manifests/BRIDGE_BLOCK_2_MANIFEST.json"] = stable_json_dumps(manifest)
    artifact_texts["00_SYSTEM/bridge/manifests/BRIDGE_BLOCK_2_SEAL.json"] = stable_json_dumps(seal)

    return artifact_texts


def write_all_allowed_artifacts(root: Path) -> dict[str, Any]:
    artifact_texts = build_all_artifact_texts()
    allowed = set(ALLOWED_OUTPUTS)
    written: list[str] = []
    for relative_path, text in artifact_texts.items():
        if relative_path not in allowed:
            raise Block2Error(f"Output outside allowlist: {relative_path}")
        if detect_no_touch_path(relative_path):
            raise Block2Error(f"No-touch output path: {relative_path}")
        target = assert_inside_root(root, relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name(target.name + ".tmp")
        tmp.write_text(text, encoding="utf-8", newline="\n")
        tmp.replace(target)
        written.append(relative_path)
    return {"status": "PASS", "written": sorted(written)}


def validate_outputs(root: Path) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    artifact_texts = build_all_artifact_texts()
    for relative_path, expected_text in artifact_texts.items():
        try:
            path = assert_inside_root(root, relative_path)
        except Block2Error as exc:
            errors.append(make_error("B2_PATH_OUTSIDE_ROOT_LOCK", "CRITICAL", "LOCK", "PATH", "Path escaped root.", str(exc), "Review path allowlist."))
            continue
        if not path.exists():
            errors.append(make_error("B2_REGISTRY_SELF_VALIDATION_BLOCK", "HIGH", "BLOCK", "EVIDENCE", "Expected artifact missing.", relative_path, "Rebuild block 2."))
            continue
        actual_text = path.read_text(encoding="utf-8")
        if relative_path.endswith(".json") and not validate_canonical_json(actual_text):
            errors.append(make_error("B2_JSON_NON_CANONICAL_BLOCK", "HIGH", "BLOCK", "EVIDENCE", "JSON is not canonical.", relative_path, "Regenerate canonical JSON."))
        if actual_text != expected_text:
            errors.append(make_error("B2_HASH_UNSTABLE_BLOCK", "HIGH", "BLOCK", "EVIDENCE", "Artifact content is not reproducible.", relative_path, "Regenerate deterministic artifacts."))
        secret_scan = scan_for_secret_leakage(actual_text)
        if secret_scan["status"] != "PASS":
            errors.append(make_error("B2_SECRET_LEAKAGE_LOCK", "CRITICAL", "LOCK", "EVIDENCE", "Secret-like content detected.", relative_path, "Remove secret-like output."))
    status = "PASS" if not errors else resolve_policy_precedence([error["decision"] for error in errors])
    return {"status": status, "errors": errors, "checked": sorted(artifact_texts)}


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    root = Path.cwd()

    if "--build-artifacts" in args:
        result = write_all_allowed_artifacts(root)
        print(stable_json_dumps(result), end="")
        return 0

    if "--validate-outputs" in args:
        result = validate_outputs(root)
        print(stable_json_dumps(result), end="")
        return 0 if result["status"] == "PASS" else 2

    print(stable_json_dumps({
        "block": BLOCK_ID,
        "status": "READY",
        "commands": ["--build-artifacts", "--validate-outputs"],
        "next_safe_step": NEXT_SAFE_STEP,
    }), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())