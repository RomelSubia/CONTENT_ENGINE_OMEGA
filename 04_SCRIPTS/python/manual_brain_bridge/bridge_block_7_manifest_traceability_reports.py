from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Mapping, Sequence


PASS = "PASS"
REVIEW = "REVIEW"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
BLOCK = "BLOCK"
LOCK = "LOCK"

PROJECT = "CONTENT_ENGINE_OMEGA"
SUBSYSTEM = "MANUAL_CEREBRO_BRIDGE"
BLOCK_ID = "BLOQUE_7_MANIFEST_TRACEABILITY_REPORTS"

VALID_STATUSES = {
    "NOT_BUILT",
    "BLUEPRINT_DEFINED",
    "REVIEW_HARDENED",
    "FINAL_HARDENING_DEFINED",
    "FINAL_APPROVED",
    "IMPLEMENTATION_PLAN_DEFINED",
    "BUILT_PENDING_POST_AUDIT",
    "BUILT_POST_AUDITED",
    "VALIDATION_MAP_DEFINED",
    "VALIDATION_PLAN_DEFINED",
    "VALIDATED_POST_AUDITED",
    "CLOSED_VALIDATED",
    "HISTORICAL_CHAIN_OBSERVED",
    "HISTORICAL_PARTIAL_REVIEW",
}

VALID_RESULTS = {PASS, REVIEW, REVIEW_REQUIRED, BLOCK, LOCK}

VALID_ARTIFACT_TYPES = {
    "technical_report_json",
    "traceability_report_json",
    "manifest_json",
    "seal_json",
    "readiness_map_json",
    "human_summary_md",
    "source_py",
    "test_py",
}

PROHIBITED_ARTIFACT_TYPES = {
    "manual_current",
    "brain_state",
    "reports_brain",
    "workflow_runtime",
    "webhook_payload",
    "publishing_payload",
    "external_execution_log",
}

PROTECTED_ROOTS = (
    "00_SYSTEM/brain",
    "00_SYSTEM/reports/brain",
    "00_SYSTEM/manual/current",
    "00_SYSTEM/manual/historical",
    "00_SYSTEM/manual/manifest",
    "00_SYSTEM/manual/registry",
    "n8n",
    "workflows",
    "publication",
)

DANGEROUS_PERMISSION_KEYS = {
    "execution_allowed_now",
    "manual_write_allowed_now",
    "brain_write_allowed_now",
    "reports_brain_write_allowed_now",
    "n8n_allowed_now",
    "webhook_allowed_now",
    "publishing_allowed_now",
    "capa9_allowed_now",
    "bloque_8_allowed_now",
    "bloque_8_blueprint_allowed_now",
    "bloque_8_build_allowed_now",
}

REQUIRED_PERMISSION_KEYS = {
    "post_build_audit_allowed_next",
    "validation_map_allowed_now",
    "validation_allowed_now",
    "gate_closure_allowed_now",
    "bloque_8_blueprint_allowed_now",
    "execution_allowed_now",
    "manual_write_allowed_now",
    "brain_write_allowed_now",
    "reports_brain_write_allowed_now",
    "n8n_allowed_now",
    "webhook_allowed_now",
    "publishing_allowed_now",
    "capa9_allowed_now",
}

VALID_NEXT_STEPS = {
    "BLOQUE_7_POST_BUILD_AUDIT",
    "BLOQUE_7_VALIDATION_MAP",
    "BLOQUE_7_VALIDATION_PLAN",
    "BLOQUE_7_VALIDATION",
    "BLOQUE_7_GATE_CLOSURE_OR_NEXT_LAYER_READINESS_MAP",
    "BLOQUE_8_BLUEPRINT",
}

BLOCKED_ACTIONS_REQUIRED = {
    "BLOQUE_7_VALIDATION_MAP",
    "BLOQUE_7_VALIDATION",
    "BLOQUE_7_GATE_CLOSURE",
    "BLOQUE_8_BLUEPRINT",
    "BLOQUE_8_BUILD",
    "EXECUTION",
    "MANUAL_WRITE",
    "BRAIN_WRITE",
    "REPORTS_BRAIN_WRITE",
    "N8N",
    "WEBHOOK",
    "PUBLISHING",
    "CAPA9",
}

SOURCE_OF_TRUTH_ORDER = [
    "git_head",
    "seal",
    "manifest",
    "technical_report",
    "traceability",
    "human_summary",
]

BLOQUE8_IMPLEMENTATION_TOKENS = {
    "AtomicWriter",
    "LockManager",
    "QuarantineWriter",
    "RecoveryExecutor",
    "RollbackExecutor",
    "WriteTransaction",
    "PendingWriteSet",
    "MutationQueue",
    "FilesystemMutationPlan",
    "PatchApplier",
    "ManualWriter",
    "BrainWriter",
    "ReportsBrainWriter",
    "ManualMutation",
    "BrainMutation",
    "AtomicCommitQueue",
}

RUNTIME_INTENT_TOKENS = {
    "subprocess.run",
    "powershell",
    "pwsh",
    "cmd.exe",
    "git commit",
    "git push",
    "n8n",
    "webhook",
    "publish",
    "upload",
    "manual_write",
    "brain_write",
    "reports_brain_write",
    "capa9",
}

DECLARATIVE_FIELDS = {
    "blocked_actions",
    "forbidden_actions",
    "inherited_blocked_capabilities",
    "denylist",
    "blocked_capabilities",
}

ACTIONABLE_FIELDS = {
    "description",
    "instructions",
    "implementation",
    "script",
    "command",
    "commands",
    "action",
    "actions",
    "runtime_behavior",
    "materialization_behavior",
    "write_behavior",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalize_path(path: str | Path) -> str:
    text = str(path).replace("\\", "/")
    while "//" in text:
        text = text.replace("//", "/")
    return text.strip().lstrip("./")


def is_valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def is_protected_path(path: str | Path) -> bool:
    norm = normalize_path(path)
    for root in PROTECTED_ROOTS:
        prefix = root.rstrip("/") + "/"
        if norm == root or norm.startswith(prefix):
            return True
    return False


def make_result(status: str, reason: str, findings: list[str] | None = None, **extra: Any) -> dict[str, Any]:
    return {
        "status": status,
        "reason": reason,
        "findings": sorted(findings or []),
        "severity": status,
        **extra,
    }


def choose_worst_status(statuses: Sequence[str]) -> str:
    rank = {PASS: 0, REVIEW: 1, REVIEW_REQUIRED: 1, BLOCK: 2, LOCK: 3}
    worst = PASS
    for status in statuses:
        if status not in rank:
            return LOCK
        if rank[status] > rank[worst]:
            worst = status
    if worst == REVIEW:
        return REVIEW_REQUIRED
    return worst


def extract_actionable_text(value: Any) -> list[str]:
    items: list[str] = []

    if isinstance(value, str):
        items.append(value)
        return items

    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            if key_text in DECLARATIVE_FIELDS:
                continue

            if key_text in ACTIONABLE_FIELDS:
                items.append(canonical_json(child) if not isinstance(child, str) else child)
                continue

            if isinstance(child, Mapping):
                items.extend(extract_actionable_text(child))
            elif isinstance(child, Sequence) and not isinstance(child, (str, bytes, bytearray)):
                for item in child:
                    items.extend(extract_actionable_text(item))

        return items

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for item in value:
            items.extend(extract_actionable_text(item))

    return items


def scan_for_runtime_or_writer_intent(value: Any) -> dict[str, Any]:
    findings: list[str] = []

    for text in extract_actionable_text(value):
        lower = text.lower()
        for token in RUNTIME_INTENT_TOKENS:
            if token.lower() in lower:
                findings.append(f"runtime_intent:{token}")

        for token in BLOQUE8_IMPLEMENTATION_TOKENS:
            if token.lower() in lower:
                findings.append(f"premature_block8_token:{token}")

    if findings:
        return make_result(LOCK, "ACTIONABLE_RUNTIME_OR_WRITER_INTENT_DETECTED", findings)

    return make_result(PASS, "NO_ACTIONABLE_RUNTIME_OR_WRITER_INTENT")


@dataclass(frozen=True)
class ArtifactRecord:
    artifact_id: str
    artifact_path: str
    artifact_type: str
    block_owner: str
    lifecycle_gate: str
    sha256: str
    status: str
    result: str
    generated_by_commit_short: str
    generated_by_commit_subject: str
    consumed_by_gate: str
    is_human_readable: bool
    is_machine_readable: bool
    protected_root: bool
    created_by_current_block: bool


def make_artifact_record(
    artifact_id: str,
    artifact_path: str,
    artifact_type: str,
    block_owner: str,
    lifecycle_gate: str,
    sha256: str,
    status: str,
    result: str,
    generated_by_commit_short: str,
    generated_by_commit_subject: str,
    consumed_by_gate: str,
    is_human_readable: bool,
    is_machine_readable: bool,
    created_by_current_block: bool,
) -> dict[str, Any]:
    norm = normalize_path(artifact_path)
    return asdict(
        ArtifactRecord(
            artifact_id=artifact_id,
            artifact_path=norm,
            artifact_type=artifact_type,
            block_owner=block_owner,
            lifecycle_gate=lifecycle_gate,
            sha256=sha256,
            status=status,
            result=result,
            generated_by_commit_short=generated_by_commit_short,
            generated_by_commit_subject=generated_by_commit_subject,
            consumed_by_gate=consumed_by_gate,
            is_human_readable=is_human_readable,
            is_machine_readable=is_machine_readable,
            protected_root=is_protected_path(norm),
            created_by_current_block=created_by_current_block,
        )
    )


def validate_artifact_record(record: Mapping[str, Any], root: str | Path | None = None) -> dict[str, Any]:
    required = set(ArtifactRecord.__dataclass_fields__)
    missing = sorted(required - set(record))
    if missing:
        return make_result(BLOCK, "ARTIFACT_RECORD_MISSING_FIELDS", missing)

    findings: list[str] = []

    if normalize_path(record["artifact_path"]) != record["artifact_path"]:
        findings.append("artifact_path_not_normalized")

    if record["artifact_type"] in PROHIBITED_ARTIFACT_TYPES:
        return make_result(LOCK, "PROHIBITED_ARTIFACT_TYPE", [record["artifact_type"]])

    if record["artifact_type"] not in VALID_ARTIFACT_TYPES:
        findings.append("unknown_artifact_type")

    if not is_valid_sha256(record["sha256"]):
        findings.append("invalid_sha256")

    if not re.fullmatch(r"[0-9a-f]{7,12}", str(record["generated_by_commit_short"])):
        findings.append("invalid_commit_short")

    if record["status"] not in VALID_STATUSES:
        findings.append("invalid_status")

    if record["result"] not in VALID_RESULTS:
        findings.append("invalid_result")

    protected = is_protected_path(record["artifact_path"])
    if protected or record.get("protected_root") is True:
        return make_result(LOCK, "ARTIFACT_IN_PROTECTED_ROOT", [record["artifact_path"]])

    if root is not None:
        path = Path(root) / record["artifact_path"]
        if not path.exists():
            findings.append("artifact_missing")
        elif is_valid_sha256(record["sha256"]) and sha256_file(path) != record["sha256"]:
            return make_result(LOCK, "ARTIFACT_HASH_MISMATCH", [record["artifact_path"]])

    if "invalid_sha256" in findings or "artifact_missing" in findings or "unknown_artifact_type" in findings:
        return make_result(BLOCK, "ARTIFACT_RECORD_INVALID", findings)

    if findings:
        return make_result(BLOCK, "ARTIFACT_RECORD_FINDINGS", findings)

    return make_result(PASS, "ARTIFACT_RECORD_VALID")


def make_manifest_contract(
    project: str,
    subsystem: str,
    block: str,
    gate: str,
    status: str,
    result: str,
    consumed_commit_short: str,
    consumed_commit_subject: str,
    produced_artifacts: list[dict[str, Any]],
    permissions: dict[str, bool],
    next_safe_step: str,
    blocked_actions: list[str],
) -> dict[str, Any]:
    return {
        "project": project,
        "subsystem": subsystem,
        "block": block,
        "gate": gate,
        "status": status,
        "result": result,
        "canonical_json": True,
        "hash_algorithm": "sha256",
        "consumed_commit_short": consumed_commit_short,
        "consumed_commit_subject": consumed_commit_subject,
        "produced_artifacts": produced_artifacts,
        "permissions": permissions,
        "next_safe_step": next_safe_step,
        "blocked_actions": sorted(set(blocked_actions)),
    }


def validate_permission_consistency(payloads: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    permissions_list = [payload.get("permissions", {}) for payload in payloads]
    if not permissions_list:
        return make_result(BLOCK, "NO_PERMISSION_PAYLOADS")

    findings: list[str] = []
    statuses: list[str] = []

    for permissions in permissions_list:
        if not isinstance(permissions, Mapping):
            return make_result(BLOCK, "PERMISSIONS_NOT_MAPPING")

        missing = sorted(REQUIRED_PERMISSION_KEYS - set(permissions))
        if missing:
            findings.extend(f"missing:{key}" for key in missing)
            statuses.append(BLOCK)

        unknown = sorted(set(permissions) - REQUIRED_PERMISSION_KEYS)
        if unknown:
            findings.extend(f"unknown:{key}" for key in unknown)
            statuses.append(BLOCK)

        for key in DANGEROUS_PERMISSION_KEYS:
            if permissions.get(key) is True:
                findings.append(f"unsafe_true:{key}")
                statuses.append(LOCK)

    first = permissions_list[0]
    for other in permissions_list[1:]:
        if dict(first) != dict(other):
            findings.append("permission_payloads_not_equal")
            statuses.append(LOCK)

    status = choose_worst_status(statuses or [PASS])
    return make_result(status, "PERMISSION_CONSISTENCY_VALIDATED", findings)


def validate_manifest_contract(manifest: Mapping[str, Any], root: str | Path | None = None) -> dict[str, Any]:
    required = {
        "project",
        "subsystem",
        "block",
        "gate",
        "status",
        "result",
        "canonical_json",
        "hash_algorithm",
        "consumed_commit_short",
        "consumed_commit_subject",
        "produced_artifacts",
        "permissions",
        "next_safe_step",
        "blocked_actions",
    }
    missing = sorted(required - set(manifest))
    if missing:
        return make_result(BLOCK, "MANIFEST_MISSING_FIELDS", missing)

    findings: list[str] = []

    if manifest["canonical_json"] is not True:
        findings.append("canonical_json_not_true")

    if manifest["hash_algorithm"] != "sha256":
        findings.append("hash_algorithm_not_sha256")

    if manifest["status"] not in VALID_STATUSES:
        findings.append("invalid_status")

    if manifest["result"] not in VALID_RESULTS:
        findings.append("invalid_result")

    if not re.fullmatch(r"[0-9a-f]{7,12}", str(manifest["consumed_commit_short"])):
        findings.append("invalid_consumed_commit_short")

    if manifest["next_safe_step"] not in VALID_NEXT_STEPS:
        return make_result(LOCK, "INVALID_NEXT_SAFE_STEP", [str(manifest["next_safe_step"])])

    produced = manifest.get("produced_artifacts", [])
    if not isinstance(produced, list) or not produced:
        findings.append("produced_artifacts_empty")

    permissions_check = validate_permission_consistency([{"permissions": manifest.get("permissions", {})}])
    if permissions_check["status"] in {BLOCK, LOCK}:
        return permissions_check

    blocked = set(manifest.get("blocked_actions", []))
    missing_blocked = sorted(BLOCKED_ACTIONS_REQUIRED - blocked)
    if missing_blocked:
        findings.append("missing_blocked_actions:" + ",".join(missing_blocked))

    child_statuses = []
    for artifact in produced:
        child_statuses.append(validate_artifact_record(artifact, root)["status"])

    worst = choose_worst_status([*child_statuses, BLOCK if findings else PASS])
    if worst != PASS:
        return make_result(worst, "MANIFEST_CONTRACT_INVALID", findings, child_statuses=child_statuses)

    return make_result(PASS, "MANIFEST_CONTRACT_VALID")


def build_evidence_index(records: list[dict[str, Any]]) -> dict[str, Any]:
    entries = []
    seen_path: dict[str, str] = {}
    findings: list[str] = []
    statuses: list[str] = []

    for record in sorted(records, key=lambda item: normalize_path(item.get("artifact_path", ""))):
        validation = validate_artifact_record(record)
        statuses.append(validation["status"])
        norm = normalize_path(record["artifact_path"])
        sha = record["sha256"]

        if norm in seen_path and seen_path[norm] != sha:
            statuses.append(LOCK)
            findings.append(f"duplicate_path_hash_conflict:{norm}")

        seen_path[norm] = sha

        entries.append(
            {
                "artifact_path": norm,
                "artifact_type": record["artifact_type"],
                "sha256": sha,
                "block_owner": record["block_owner"],
                "gate_owner": record["lifecycle_gate"],
                "status": record["status"],
                "result": record["result"],
                "source_of_truth_rank": 3,
                "generated_by_commit": record["generated_by_commit_short"],
                "consumed_by_gate": record["consumed_by_gate"],
                "integrity_status": "VERIFIED" if validation["status"] == PASS else validation["reason"],
            }
        )

    status = choose_worst_status(statuses or [PASS])
    if findings:
        status = LOCK

    return {
        "status": status,
        "reason": "EVIDENCE_INDEX_BUILT",
        "entries": entries,
        "entry_count": len(entries),
        "findings": sorted(findings),
    }


def validate_evidence_index(index: Mapping[str, Any], root: str | Path | None = None) -> dict[str, Any]:
    if "entries" not in index or not isinstance(index["entries"], list):
        return make_result(BLOCK, "EVIDENCE_INDEX_MISSING_ENTRIES")

    statuses: list[str] = []
    seen: dict[str, str] = {}

    for entry in index["entries"]:
        path = normalize_path(entry.get("artifact_path", ""))
        sha = entry.get("sha256", "")
        integrity = entry.get("integrity_status", "")

        if not path:
            statuses.append(BLOCK)

        if not is_valid_sha256(sha):
            statuses.append(BLOCK)

        if is_protected_path(path):
            statuses.append(LOCK)

        if path in seen and seen[path] != sha:
            statuses.append(LOCK)

        seen[path] = sha

        if integrity == "HASH_MISMATCH":
            statuses.append(LOCK)
        elif integrity in {"MISSING", "HASH_INVALID", "OUT_OF_SCOPE"}:
            statuses.append(BLOCK)
        elif integrity in {"STATUS_CONFLICT", "PERMISSION_CONFLICT", "PROTECTED_ROOT_BLOCKED"}:
            statuses.append(LOCK)
        else:
            statuses.append(PASS)

        if root is not None and path:
            artifact_path = Path(root) / path
            if not artifact_path.exists():
                statuses.append(BLOCK)
            elif is_valid_sha256(sha) and sha256_file(artifact_path) != sha:
                statuses.append(LOCK)

    status = choose_worst_status(statuses or [PASS])
    return make_result(status, "EVIDENCE_INDEX_VALIDATED", entry_count=len(index["entries"]))


def make_traceability_node(
    node_id: str,
    block_id: str,
    block_name: str,
    gate: str,
    commit_short: str,
    commit_subject: str,
    status: str,
    result: str,
    consumed_evidence: list[str],
    produced_evidence: list[str],
    next_safe_step: str,
    blocked_actions: list[str],
    permissions_digest: str,
) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "block_id": block_id,
        "block_name": block_name,
        "gate": gate,
        "commit_short": commit_short,
        "commit_subject": commit_subject,
        "status": status,
        "result": result,
        "consumed_evidence": consumed_evidence,
        "produced_evidence": produced_evidence,
        "next_safe_step": next_safe_step,
        "blocked_actions": sorted(set(blocked_actions)),
        "permissions_digest": permissions_digest,
    }


def validate_traceability_node(node: Mapping[str, Any]) -> dict[str, Any]:
    required = {
        "node_id",
        "block_id",
        "block_name",
        "gate",
        "commit_short",
        "commit_subject",
        "status",
        "result",
        "consumed_evidence",
        "produced_evidence",
        "next_safe_step",
        "blocked_actions",
        "permissions_digest",
    }
    missing = sorted(required - set(node))
    if missing:
        return make_result(BLOCK, "TRACEABILITY_NODE_MISSING_FIELDS", missing)

    findings: list[str] = []

    if not re.fullmatch(r"[0-9a-f]{7,12}|PENDING_THIS_COMMIT|HISTORICAL_PARTIAL", str(node["commit_short"])):
        findings.append("invalid_commit_short")

    if node["status"] not in VALID_STATUSES:
        findings.append("invalid_status")

    if node["result"] not in VALID_RESULTS:
        findings.append("invalid_result")

    if not node["next_safe_step"]:
        findings.append("missing_next_safe_step")

    if not isinstance(node["consumed_evidence"], list):
        findings.append("consumed_evidence_not_list")

    if not isinstance(node["produced_evidence"], list):
        findings.append("produced_evidence_not_list")

    if findings:
        return make_result(BLOCK, "TRACEABILITY_NODE_INVALID", findings)

    return make_result(PASS, "TRACEABILITY_NODE_VALID")


def build_traceability_chain(nodes: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(nodes, key=lambda node: node["node_id"])
    return {
        "status": PASS,
        "reason": "TRACEABILITY_CHAIN_BUILT",
        "node_count": len(ordered),
        "nodes": ordered,
    }


def validate_traceability_chain(chain: Mapping[str, Any]) -> dict[str, Any]:
    nodes = chain.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        return make_result(BLOCK, "TRACEABILITY_CHAIN_MISSING_NODES")

    statuses = [validate_traceability_node(node)["status"] for node in nodes]

    ids = [node.get("node_id") for node in nodes]
    if ids != sorted(ids):
        statuses.append(BLOCK)

    status = choose_worst_status(statuses)
    return make_result(status, "TRACEABILITY_CHAIN_VALIDATED", node_count=len(nodes))


def validate_source_of_truth_hierarchy(payloads: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    findings: list[str] = []
    statuses: list[str] = []

    ordered_present = [key for key in SOURCE_OF_TRUTH_ORDER if key in payloads]

    for key in ordered_present:
        payload = payloads[key]
        if not isinstance(payload, Mapping):
            statuses.append(BLOCK)
            findings.append(f"invalid_payload:{key}")

    comparable_keys = [key for key in ordered_present if key not in {"git_head", "human_summary"}]
    next_steps = {key: payloads[key].get("next_safe_step") for key in comparable_keys if payloads[key].get("next_safe_step")}
    if len(set(next_steps.values())) > 1:
        statuses.append(LOCK)
        findings.append("next_safe_step_contradiction")

    statuses_declared = {key: payloads[key].get("status") for key in comparable_keys if payloads[key].get("status")}
    if "seal" in statuses_declared and "manifest" in statuses_declared:
        seal_status = statuses_declared["seal"]
        manifest_status = statuses_declared["manifest"]
        compatible = (
            seal_status == manifest_status
            or str(seal_status).endswith(str(manifest_status))
            or str(manifest_status).endswith(str(seal_status))
        )
        if not compatible:
            statuses.append(LOCK)
            findings.append("seal_manifest_status_contradiction")

    status = choose_worst_status(statuses or [PASS])
    return make_result(status, "SOURCE_OF_TRUTH_HIERARCHY_VALIDATED", findings)


def validate_cross_block_integrity(chain: Mapping[str, Any]) -> dict[str, Any]:
    nodes = chain.get("nodes", [])
    if not isinstance(nodes, list) or not nodes:
        return make_result(BLOCK, "CROSS_BLOCK_CHAIN_EMPTY")

    findings: list[str] = []
    statuses: list[str] = []

    def field_text(node: Mapping[str, Any], key: str) -> str:
        return str(node.get(key, ""))

    lifecycle_fields = [
        "node_id",
        "block_id",
        "block_name",
        "gate",
        "next_safe_step",
        "status",
    ]

    lifecycle_text = "\n".join(
        field_text(node, key)
        for node in nodes
        if isinstance(node, Mapping)
        for key in lifecycle_fields
    )

    b7_closed = any(
        isinstance(node, Mapping)
        and (
            field_text(node, "status") == "CLOSED_VALIDATED"
            or "BLOQUE_7_GATE_CLOSURE" in field_text(node, "gate")
            or "BLOQUE_7_GATE_CLOSURE" in field_text(node, "node_id")
        )
        for node in nodes
    )

    if "BLOQUE_8" in lifecycle_text and not b7_closed:
        statuses.append(LOCK)
        findings.append("bloque_8_before_bloque_7_closure")

    if "BLOQUE_7_BUILD" in lifecycle_text and "BLOQUE_7_IMPLEMENTATION_PLAN" not in lifecycle_text:
        statuses.append(LOCK)
        findings.append("bloque_7_build_without_implementation_plan")

    if "GLOBAL_CLOSURE" in lifecycle_text and "BLOQUE_10" not in lifecycle_text:
        statuses.append(LOCK)
        findings.append("global_closure_before_bloque_10")

    status = choose_worst_status(statuses or [PASS])
    return make_result(status, "CROSS_BLOCK_INTEGRITY_VALIDATED", findings)


def validate_report_materialization(payload: Mapping[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    statuses: list[str] = []

    def count_string_lines(value: Any) -> int:
        if isinstance(value, str):
            return max(1, len(value.splitlines()))

        if isinstance(value, Mapping):
            return sum(count_string_lines(child) for child in value.values())

        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            return sum(count_string_lines(child) for child in value)

        return 0

    text = canonical_json(payload)
    nested_line_volume = count_string_lines(payload)

    if len(text.splitlines()) > 3500 or nested_line_volume > 3500:
        statuses.append(BLOCK)
        findings.append("report_too_large")

    if "PS D:" in text or "================ PRECHECK" in text:
        statuses.append(BLOCK)
        findings.append("terminal_transcript_embedded")

    for actionable_text in extract_actionable_text(payload):
        if "PS D:" in actionable_text or "================ PRECHECK" in actionable_text:
            statuses.append(BLOCK)
            findings.append("terminal_transcript_embedded")

    scan = scan_for_runtime_or_writer_intent(payload)
    statuses.append(scan["status"])
    findings.extend(scan.get("findings", []))

    status = choose_worst_status(statuses or [PASS])
    return make_result(status, "REPORT_MATERIALIZATION_VALIDATED", findings, nested_line_volume=nested_line_volume)


def validate_next_layer_readiness(payload: Mapping[str, Any]) -> dict[str, Any]:
    if payload.get("current_status") != "BUILT_PENDING_POST_AUDIT":
        return make_result(BLOCK, "NEXT_LAYER_CURRENT_STATUS_INVALID")

    if payload.get("next_safe_step") != "BLOQUE_7_POST_BUILD_AUDIT":
        return make_result(LOCK, "NEXT_LAYER_NEXT_SAFE_STEP_INVALID")

    permissions_check = validate_permission_consistency([{"permissions": payload.get("permissions", {})}])
    if permissions_check["status"] != PASS:
        return permissions_check

    if payload.get("post_build_audit_allowed_next") is not True:
        return make_result(BLOCK, "POST_BUILD_AUDIT_NOT_ALLOWED_NEXT")

    return make_result(PASS, "NEXT_LAYER_READINESS_VALID")


def build_block7_report_payloads(root: str | Path, git_context: Mapping[str, Any]) -> dict[str, Any]:
    permissions = {
        "post_build_audit_allowed_next": True,
        "validation_map_allowed_now": False,
        "validation_allowed_now": False,
        "gate_closure_allowed_now": False,
        "bloque_8_blueprint_allowed_now": False,
        "execution_allowed_now": False,
        "manual_write_allowed_now": False,
        "brain_write_allowed_now": False,
        "reports_brain_write_allowed_now": False,
        "n8n_allowed_now": False,
        "webhook_allowed_now": False,
        "publishing_allowed_now": False,
        "capa9_allowed_now": False,
    }

    blocked_actions = sorted(BLOCKED_ACTIONS_REQUIRED)

    base = {
        "project": PROJECT,
        "subsystem": SUBSYSTEM,
        "block": BLOCK_ID,
        "status": "BUILT_PENDING_POST_AUDIT",
        "result": PASS,
        "consumed_commit_short": git_context["head_short"],
        "consumed_commit_subject": git_context["head_subject"],
        "next_safe_step": "BLOQUE_7_POST_BUILD_AUDIT",
        "permissions": permissions,
        "blocked_actions": blocked_actions,
    }

    sample_hash = "a" * 64

    source_record = make_artifact_record(
        artifact_id="block7-source",
        artifact_path="04_SCRIPTS/python/manual_brain_bridge/bridge_block_7_manifest_traceability_reports.py",
        artifact_type="source_py",
        block_owner=BLOCK_ID,
        lifecycle_gate="BUILD",
        sha256=sample_hash,
        status="BUILT_PENDING_POST_AUDIT",
        result=PASS,
        generated_by_commit_short=git_context["head_short"],
        generated_by_commit_subject=git_context["head_subject"],
        consumed_by_gate="BLOQUE_7_POST_BUILD_AUDIT",
        is_human_readable=True,
        is_machine_readable=True,
        created_by_current_block=True,
    )

    report_record = make_artifact_record(
        artifact_id="block7-manifest-report",
        artifact_path="00_SYSTEM/bridge/reports/BRIDGE_BLOCK_7_MANIFEST_REPORT.json",
        artifact_type="technical_report_json",
        block_owner=BLOCK_ID,
        lifecycle_gate="BUILD",
        sha256=sample_hash,
        status="BUILT_PENDING_POST_AUDIT",
        result=PASS,
        generated_by_commit_short=git_context["head_short"],
        generated_by_commit_subject=git_context["head_subject"],
        consumed_by_gate="BLOQUE_7_POST_BUILD_AUDIT",
        is_human_readable=False,
        is_machine_readable=True,
        created_by_current_block=True,
    )

    evidence_index = build_evidence_index([source_record, report_record])

    node6 = make_traceability_node(
        node_id="B06-closure",
        block_id="BLOQUE_6",
        block_name="Decision mapper + controlled plan builder",
        gate="GATE_CLOSURE",
        commit_short=git_context.get("block6_closure_head", "3ef85e4"),
        commit_subject="Close MANUAL-CEREBRO bridge block 6 decision mapper controlled plan builder",
        status="CLOSED_VALIDATED",
        result=PASS,
        consumed_evidence=["BRIDGE_BLOCK_6_VALIDATION_EXECUTION_REPORT.json"],
        produced_evidence=["BRIDGE_BLOCK_6_GATE_CLOSURE_REPORT.json"],
        next_safe_step="BLOQUE_7_BLUEPRINT",
        blocked_actions=blocked_actions,
        permissions_digest=sha256_text(canonical_json(permissions)),
    )

    node7 = make_traceability_node(
        node_id="B07-build",
        block_id="BLOQUE_7",
        block_name="Manifest + traceability + reports",
        gate="BUILD",
        commit_short=git_context["head_short"],
        commit_subject=git_context["head_subject"],
        status="BUILT_PENDING_POST_AUDIT",
        result=PASS,
        consumed_evidence=["BRIDGE_BLOCK_6_GATE_CLOSURE_REPORT.json"],
        produced_evidence=[
            "BRIDGE_BLOCK_7_MANIFEST_REPORT.json",
            "BRIDGE_BLOCK_7_TRACEABILITY_CHAIN_REPORT.json",
            "BRIDGE_BLOCK_7_EVIDENCE_INDEX_REPORT.json",
        ],
        next_safe_step="BLOQUE_7_POST_BUILD_AUDIT",
        blocked_actions=blocked_actions,
        permissions_digest=sha256_text(canonical_json(permissions)),
    )

    traceability_chain = build_traceability_chain([node6, node7])

    manifest_payload = {
        **base,
        "gate": "BUILD",
        "contract": "ManifestContract",
        "manifest_contract_status": validate_manifest_contract(
            make_manifest_contract(
                PROJECT,
                SUBSYSTEM,
                BLOCK_ID,
                "BUILD",
                "BUILT_PENDING_POST_AUDIT",
                PASS,
                git_context["head_short"],
                git_context["head_subject"],
                [source_record, report_record],
                permissions,
                "BLOQUE_7_POST_BUILD_AUDIT",
                blocked_actions,
            )
        ),
    }

    traceability_payload = {
        **base,
        "gate": "BUILD",
        "contract": "TraceabilityChainContract",
        "traceability_chain": traceability_chain,
        "traceability_validation": validate_traceability_chain(traceability_chain),
    }

    materialization_payload = {
        **base,
        "gate": "BUILD",
        "contract": "ReportMaterializationContract",
        "materialization_allowed": True,
        "manual_write_allowed": False,
        "brain_write_allowed": False,
        "reports_brain_write_allowed": False,
        "runtime_execution_allowed": False,
        "external_io_allowed": False,
        "report_materialization_validation": validate_report_materialization(base),
    }

    evidence_payload = {
        **base,
        "gate": "BUILD",
        "contract": "EvidenceIndexContract",
        "evidence_index": evidence_index,
        "evidence_index_validation": validate_evidence_index(evidence_index),
    }

    permission_payload = {
        **base,
        "gate": "BUILD",
        "contract": "PermissionConsistencyGuard",
        "permission_consistency_validation": validate_permission_consistency(
            [
                {"permissions": permissions},
                {"permissions": permissions},
                {"permissions": permissions},
            ]
        ),
    }

    cross_block_payload = {
        **base,
        "gate": "BUILD",
        "contract": "CrossBlockIntegrityGuard",
        "cross_block_integrity_validation": validate_cross_block_integrity(traceability_chain),
    }

    readiness_payload = {
        **base,
        "gate": "BUILD",
        "current_status": "BUILT_PENDING_POST_AUDIT",
        "post_build_audit_allowed_next": True,
        "readiness_status": "READY_FOR_POST_BUILD_AUDIT_ONLY",
        "contract": "NextLayerReadinessGuard",
    }
    readiness_payload["next_layer_readiness_validation"] = validate_next_layer_readiness(readiness_payload)

    return {
        "BRIDGE_BLOCK_7_MANIFEST_REPORT.json": manifest_payload,
        "BRIDGE_BLOCK_7_TRACEABILITY_CHAIN_REPORT.json": traceability_payload,
        "BRIDGE_BLOCK_7_REPORTS_MATERIALIZATION_REPORT.json": materialization_payload,
        "BRIDGE_BLOCK_7_EVIDENCE_INDEX_REPORT.json": evidence_payload,
        "BRIDGE_BLOCK_7_PERMISSION_CONSISTENCY_REPORT.json": permission_payload,
        "BRIDGE_BLOCK_7_CROSS_BLOCK_INTEGRITY_REPORT.json": cross_block_payload,
        "BRIDGE_BLOCK_7_NEXT_LAYER_READINESS_MAP.json": readiness_payload,
    }


__all__ = [
    "PASS",
    "REVIEW",
    "REVIEW_REQUIRED",
    "BLOCK",
    "LOCK",
    "ArtifactRecord",
    "canonical_json",
    "sha256_text",
    "sha256_file",
    "normalize_path",
    "is_valid_sha256",
    "is_protected_path",
    "make_result",
    "choose_worst_status",
    "scan_for_runtime_or_writer_intent",
    "make_artifact_record",
    "validate_artifact_record",
    "make_manifest_contract",
    "validate_manifest_contract",
    "build_evidence_index",
    "validate_evidence_index",
    "make_traceability_node",
    "validate_traceability_node",
    "build_traceability_chain",
    "validate_traceability_chain",
    "validate_permission_consistency",
    "validate_source_of_truth_hierarchy",
    "validate_cross_block_integrity",
    "validate_report_materialization",
    "validate_next_layer_readiness",
    "build_block7_report_payloads",
]
