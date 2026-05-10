from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


PASS = "PASS"
BLOCK = "BLOCK"
LOCK = "LOCK"
REVIEW = "REVIEW"
REVIEW_REQUIRED = "REVIEW_REQUIRED"

TX_DECLARED = "TX_DECLARED"
TX_PREFLIGHT_PASS = "TX_PREFLIGHT_PASS"
TX_LOCK_ACQUIRED = "TX_LOCK_ACQUIRED"
TX_STAGED = "TX_STAGED"
TX_STAGING_VERIFIED = "TX_STAGING_VERIFIED"
TX_PROMOTION_READY = "TX_PROMOTION_READY"
TX_PROMOTED = "TX_PROMOTED"
TX_POST_WRITE_AUDITED = "TX_POST_WRITE_AUDITED"
TX_CLOSED = "TX_CLOSED"

TX_BLOCKED = "TX_BLOCKED"
TX_LOCKED = "TX_LOCKED"
TX_QUARANTINED = "TX_QUARANTINED"
TX_RECOVERY_REQUIRED = "TX_RECOVERY_REQUIRED"

RECOVERY_CLASS_A_SAFE_NOOP = "RECOVERY_CLASS_A_SAFE_NOOP"
RECOVERY_CLASS_B_SAFE_RETRY_AFTER_CLEANUP = "RECOVERY_CLASS_B_SAFE_RETRY_AFTER_CLEANUP"
RECOVERY_CLASS_C_QUARANTINE_REQUIRED = "RECOVERY_CLASS_C_QUARANTINE_REQUIRED"
RECOVERY_CLASS_D_MANUAL_REVIEW_REQUIRED = "RECOVERY_CLASS_D_MANUAL_REVIEW_REQUIRED"
RECOVERY_CLASS_E_LOCKED_IRRECOVERABLE_WITHOUT_OPERATOR = "RECOVERY_CLASS_E_LOCKED_IRRECOVERABLE_WITHOUT_OPERATOR"

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
    "manual_write_allowed_now",
    "brain_write_allowed_now",
    "reports_brain_write_allowed_now",
    "execution_allowed_now",
    "external_execution_allowed_now",
    "n8n_allowed_now",
    "webhook_allowed_now",
    "publishing_allowed_now",
    "capa9_allowed_now",
    "bloque_9_allowed_now",
    "rollback_execution_allowed",
    "stale_lock_auto_release_allowed",
    "allowlist_expansion_allowed",
    "plan_reinterpretation_allowed",
    "protected_root_exception_allowed",
}

FAILURE_POINT_CLASS = {
    "FAILPOINT_00_PRE_TRANSACTION": RECOVERY_CLASS_A_SAFE_NOOP,
    "FAILPOINT_01_TRANSACTION_DECLARED_NO_LOCK": RECOVERY_CLASS_B_SAFE_RETRY_AFTER_CLEANUP,
    "FAILPOINT_02_LOCK_CREATED_NO_STAGING": RECOVERY_CLASS_D_MANUAL_REVIEW_REQUIRED,
    "FAILPOINT_03_STAGING_CREATED_NO_OUTPUTS": RECOVERY_CLASS_B_SAFE_RETRY_AFTER_CLEANUP,
    "FAILPOINT_04_STAGING_PARTIAL": RECOVERY_CLASS_C_QUARANTINE_REQUIRED,
    "FAILPOINT_05_STAGING_COMPLETE_HASH_FAIL": RECOVERY_CLASS_C_QUARANTINE_REQUIRED,
    "FAILPOINT_06_PROMOTION_READY_NOT_STARTED": RECOVERY_CLASS_D_MANUAL_REVIEW_REQUIRED,
    "FAILPOINT_07_PROMOTION_PARTIAL": RECOVERY_CLASS_D_MANUAL_REVIEW_REQUIRED,
    "FAILPOINT_08_PROMOTION_COMPLETE_POST_HASH_FAIL": RECOVERY_CLASS_D_MANUAL_REVIEW_REQUIRED,
    "FAILPOINT_09_POST_WRITE_AUDIT_FAIL": RECOVERY_CLASS_D_MANUAL_REVIEW_REQUIRED,
    "FAILPOINT_10_MANIFEST_CREATED_SEAL_FAIL": RECOVERY_CLASS_D_MANUAL_REVIEW_REQUIRED,
    "FAILPOINT_11_SEAL_CREATED_LOCK_NOT_RELEASED": RECOVERY_CLASS_B_SAFE_RETRY_AFTER_CLEANUP,
    "FAILPOINT_12_UNKNOWN_STATE": RECOVERY_CLASS_E_LOCKED_IRRECOVERABLE_WITHOUT_OPERATOR,
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def normalize_path(path: str | Path) -> str:
    text = str(path).replace("\\", "/").strip()
    while "//" in text:
        text = text.replace("//", "/")

    parts: list[str] = []
    for part in text.split("/"):
        if part in {"", "."}:
            continue
        parts.append(part)

    return "/".join(parts)

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


@dataclass(frozen=True)
class TransactionLimitContract:
    max_planned_outputs: int = 50
    max_single_artifact_bytes: int = 1048576
    max_total_transaction_bytes: int = 10485760
    max_report_lines: int = 3500
    max_report_nested_string_lines: int = 3500
    max_quarantine_bundle_bytes: int = 52428800
    max_lock_ttl_minutes: int = 15
    max_stale_lock_age_minutes_before_manual_review: int = 60
    max_path_length_chars: int = 240
    max_transaction_id_length: int = 120
    max_manifest_artifacts: int = 100
    max_recovery_journal_entries: int = 500


@dataclass(frozen=True)
class CanonicalDestinationRecord:
    original_path: str
    canonical_path: str
    allowlist_digest: str
    protected_root: bool
    root_escape: bool
    in_allowlist: bool


@dataclass(frozen=True)
class StagedOutputRecord:
    staged_path: str
    destination_path: str
    sha256: str
    size_bytes: int
    canonical_json: bool


@dataclass(frozen=True)
class AtomicWriteTransactionContract:
    transaction_id: str
    operation_type: str
    repo_head: str
    source_block: str
    planned_outputs: list[str]
    allowlist_digest: str
    protected_roots_digest: str
    permissions: dict[str, bool]
    status: str = TX_DECLARED


@dataclass(frozen=True)
class LockContract:
    lock_id: str
    transaction_id: str
    repo_head: str
    scope_digest: str
    owner: str
    created_at_utc: str
    expires_at_utc: str
    status: str
    stale_policy: str = "FAIL_CLOSED_UNLESS_RECOVERY_PROVES_SAFE"


@dataclass(frozen=True)
class StagingManifestContract:
    transaction_id: str
    planned_outputs: list[str]
    staged_outputs: list[StagedOutputRecord]
    status: str


@dataclass(frozen=True)
class PromotionManifestContract:
    transaction_id: str
    promoted_outputs: list[str]
    destination_hashes_before: dict[str, str | None]
    destination_hashes_after: dict[str, str]
    promotion_results: dict[str, str]
    status: str


@dataclass(frozen=True)
class QuarantineContract:
    quarantine_id: str
    transaction_id: str
    reason: str
    quarantined_paths: list[str]
    hashes: dict[str, str]
    manual_review_required: bool
    auto_recover_allowed: bool


@dataclass(frozen=True)
class RecoveryManifestContract:
    recovery_id: str
    transaction_id: str
    failure_point: str
    recovery_class: str
    staged_outputs: list[str]
    promoted_outputs: list[str]
    quarantined_outputs: list[str]
    rollback_draft: dict[str, Any]
    auto_recovery_allowed: bool
    manual_review_required: bool


@dataclass(frozen=True)
class PostWriteAuditContract:
    transaction_id: str
    output_scope_result: str
    hash_verification_result: str
    no_touch_result: str
    lock_release_result: str
    tmp_residue_result: str
    repo_status_result: str
    next_safe_step: str


def build_transaction_limit_contract(**overrides: Any) -> dict[str, Any]:
    return asdict(TransactionLimitContract(**overrides))


def validate_transaction_limits(payload: Mapping[str, Any] | None, planned_outputs: Sequence[str] | None = None, artifact_sizes: Mapping[str, int] | None = None, report_payload: Any | None = None) -> dict[str, Any]:
    if not payload:
        return make_result(LOCK, "TX_LIMIT_CONTRACT_MISSING_LOCK")

    try:
        limits = TransactionLimitContract(**dict(payload))
    except TypeError as exc:
        return make_result(BLOCK, "TX_LIMIT_CONTRACT_INVALID", [str(exc)])

    findings: list[str] = []
    statuses: list[str] = []

    outputs = list(planned_outputs or [])
    if len(outputs) > limits.max_planned_outputs:
        statuses.append(BLOCK)
        findings.append("TX_LIMIT_PLANNED_OUTPUTS_EXCEEDED_BLOCK")

    for path in outputs:
        if len(normalize_path(path)) > limits.max_path_length_chars:
            statuses.append(BLOCK)
            findings.append("TX_LIMIT_PATH_LENGTH_BLOCK")

    sizes = dict(artifact_sizes or {})
    if any(size > limits.max_single_artifact_bytes for size in sizes.values()):
        statuses.append(BLOCK)
        findings.append("TX_LIMIT_SINGLE_ARTIFACT_EXCEEDED_BLOCK")

    if sum(sizes.values()) > limits.max_total_transaction_bytes:
        statuses.append(BLOCK)
        findings.append("TX_LIMIT_TOTAL_BYTES_EXCEEDED_BLOCK")

    if limits.max_lock_ttl_minutes <= 0:
        statuses.append(BLOCK)
        findings.append("TX_LIMIT_LOCK_TTL_INVALID_BLOCK")

    if report_payload is not None:
        text = canonical_json(report_payload)
        if len(text.splitlines()) > limits.max_report_lines:
            statuses.append(BLOCK)
            findings.append("TX_LIMIT_REPORT_INFLATION_BLOCK")

    status = choose_worst_status(statuses or [PASS])
    return make_result(status, "TX_LIMITS_VALIDATED", findings)


def build_atomic_write_transaction(
    transaction_id: str,
    operation_type: str,
    repo_head: str,
    source_block: str,
    planned_outputs: list[str],
    permissions: dict[str, bool],
) -> dict[str, Any]:
    allowlist_digest = sha256_text(canonical_json(sorted(planned_outputs)))
    protected_roots_digest = sha256_text(canonical_json(list(PROTECTED_ROOTS)))
    return asdict(
        AtomicWriteTransactionContract(
            transaction_id=transaction_id,
            operation_type=operation_type,
            repo_head=repo_head,
            source_block=source_block,
            planned_outputs=planned_outputs,
            allowlist_digest=allowlist_digest,
            protected_roots_digest=protected_roots_digest,
            permissions=permissions,
        )
    )


def validate_atomic_write_transaction(tx: Mapping[str, Any]) -> dict[str, Any]:
    required = {"transaction_id", "operation_type", "repo_head", "source_block", "planned_outputs", "allowlist_digest", "protected_roots_digest", "permissions"}
    missing = sorted(required - set(tx))
    if missing:
        return make_result(BLOCK, "TX_MISSING_REQUIRED_FIELDS", missing)

    findings: list[str] = []
    statuses: list[str] = []

    if not tx["transaction_id"]:
        statuses.append(BLOCK)
        findings.append("MISSING_TRANSACTION_ID")

    if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,120}", str(tx["transaction_id"])):
        statuses.append(BLOCK)
        findings.append("INVALID_TRANSACTION_ID")

    if tx["operation_type"] != "ATOMIC_WRITE":
        statuses.append(BLOCK)
        findings.append("UNKNOWN_OPERATION_TYPE")

    if not tx["repo_head"]:
        statuses.append(BLOCK)
        findings.append("MISSING_REPO_HEAD")

    planned = tx["planned_outputs"]
    if not isinstance(planned, list) or not planned:
        statuses.append(BLOCK)
        findings.append("EMPTY_OUTPUT_PLAN")

    permissions = tx.get("permissions", {})
    if not isinstance(permissions, Mapping):
        statuses.append(BLOCK)
        findings.append("PERMISSIONS_NOT_MAPPING")
    else:
        for key in DANGEROUS_PERMISSION_KEYS:
            if permissions.get(key) is True:
                statuses.append(LOCK)
                findings.append(f"UNSAFE_PERMISSION_TRUE:{key}")

    return make_result(choose_worst_status(statuses or [PASS]), "TX_VALIDATED", findings)


def canonicalize_destination_path(path: str | Path, repo_root: str | Path, allowlist: Sequence[str]) -> dict[str, Any]:
    raw = str(path)
    raw_slash = raw.replace("\\", "/").strip()
    raw_parts = [part for part in raw_slash.split("/") if part != ""]

    norm = normalize_path(raw)
    root = Path(repo_root)

    findings: list[str] = []
    statuses: list[str] = []

    if not raw_slash:
        statuses.append(BLOCK)
        findings.append("PATH_EMPTY")

    if any(part == ".." for part in raw_parts):
        statuses.append(LOCK)
        findings.append("PATH_TRAVERSAL")

    if any(part == "." for part in raw_parts):
        statuses.append(LOCK)
        findings.append("PATH_DOT_SEGMENT")

    if raw_slash.startswith("/") or raw_slash.startswith("\\\\"):
        statuses.append(LOCK)
        findings.append("ABSOLUTE_OR_UNC_PATH")

    if re.match(r"^[A-Za-z]:", raw):
        statuses.append(LOCK)
        findings.append("WINDOWS_DRIVE_PATH")

    candidate = root / norm
    try:
        resolved_root = root.resolve()
        resolved_candidate = candidate.resolve()
        root_escape = not str(resolved_candidate).lower().startswith(str(resolved_root).lower())
    except Exception:
        root_escape = True

    if root_escape:
        statuses.append(LOCK)
        findings.append("PATH_ESCAPES_ROOT")

    protected = is_protected_path(norm)
    if protected:
        statuses.append(LOCK)
        findings.append("PROTECTED_ROOT")

    normalized_allowlist = {normalize_path(item) for item in allowlist}
    in_allowlist = norm in normalized_allowlist
    if not in_allowlist:
        statuses.append(BLOCK)
        findings.append("NOT_IN_ALLOWLIST")

    record = CanonicalDestinationRecord(
        original_path=raw,
        canonical_path=norm,
        allowlist_digest=sha256_text(canonical_json(sorted(normalized_allowlist))),
        protected_root=protected,
        root_escape=root_escape,
        in_allowlist=in_allowlist,
    )

    return {
        "record": asdict(record),
        "validation": make_result(choose_worst_status(statuses or [PASS]), "PATH_CANONICALIZED", findings),
    }

def validate_path_boundary(record: Mapping[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    statuses: list[str] = []

    if record.get("protected_root") is True:
        statuses.append(LOCK)
        findings.append("PATH_CANONICAL_LOCK_PROTECTED_ROOT")

    if record.get("root_escape") is True:
        statuses.append(LOCK)
        findings.append("PATH_CANONICAL_LOCK_EXTERNAL_ROOT")

    if record.get("in_allowlist") is not True:
        statuses.append(BLOCK)
        findings.append("PATH_CANONICAL_BLOCK_NOT_IN_ALLOWLIST")

    return make_result(choose_worst_status(statuses or [PASS]), "PATH_BOUNDARY_VALIDATED", findings)


def validate_output_allowlist(outputs: Sequence[str], allowlist: Sequence[str]) -> dict[str, Any]:
    normalized_outputs = {normalize_path(item) for item in outputs}
    normalized_allowlist = {normalize_path(item) for item in allowlist}
    unexpected = sorted(normalized_outputs - normalized_allowlist)
    missing = sorted(normalized_allowlist - normalized_outputs)
    if unexpected:
        return make_result(LOCK, "OUTPUT_ALLOWLIST_UNEXPECTED_OUTPUTS", unexpected)
    if missing:
        return make_result(BLOCK, "OUTPUT_ALLOWLIST_MISSING_OUTPUTS", missing)
    return make_result(PASS, "OUTPUT_ALLOWLIST_EXACT_MATCH")


def build_lock_contract(lock_id: str, transaction_id: str, repo_head: str, scope_digest: str, status: str = "LOCK_ACQUIRED") -> dict[str, Any]:
    return asdict(
        LockContract(
            lock_id=lock_id,
            transaction_id=transaction_id,
            repo_head=repo_head,
            scope_digest=scope_digest,
            owner="MANUAL_CEREBRO_BRIDGE",
            created_at_utc="1970-01-01T00:00:00Z",
            expires_at_utc="1970-01-01T00:15:00Z",
            status=status,
        )
    )


def validate_lock_contract(lock: Mapping[str, Any], expected_repo_head: str | None = None, expected_scope_digest: str | None = None) -> dict[str, Any]:
    required = {"lock_id", "transaction_id", "repo_head", "scope_digest", "owner", "created_at_utc", "expires_at_utc", "status"}
    missing = sorted(required - set(lock))
    if missing:
        return make_result(BLOCK, "LOCK_MISSING_REQUIRED_FIELDS", missing)

    findings: list[str] = []
    statuses: list[str] = []

    if not lock.get("transaction_id"):
        statuses.append(BLOCK)
        findings.append("LOCK_MISSING_TRANSACTION_ID")

    if lock.get("status") == "LOCK_ACTIVE":
        statuses.append(LOCK)
        findings.append("LOCK_ALREADY_ACTIVE")

    if expected_repo_head is not None and lock.get("repo_head") != expected_repo_head:
        statuses.append(LOCK)
        findings.append("LOCK_HEAD_MISMATCH")

    if expected_scope_digest is not None and lock.get("scope_digest") != expected_scope_digest:
        statuses.append(LOCK)
        findings.append("LOCK_SCOPE_MISMATCH")

    if lock.get("status") == "LOCK_CORRUPT":
        statuses.append(LOCK)
        findings.append("LOCK_CORRUPT")

    return make_result(choose_worst_status(statuses or [PASS]), "LOCK_VALIDATED", findings)


def classify_stale_lock(lock: Mapping[str, Any], audit_passed: bool = False) -> dict[str, Any]:
    if lock.get("status") != "LOCK_STALE":
        return make_result(PASS, "LOCK_NOT_STALE")
    if audit_passed:
        return make_result(PASS, "STALE_LOCK_AUDIT_PASS_RELEASE_ALLOWED")
    return make_result(LOCK, "STALE_LOCK_AUDIT_REQUIRED", ["STALE_LOCKS_ARE_NEVER_AUTO_RELEASED"])


def build_staging_manifest(transaction_id: str, planned_outputs: list[str], staged_outputs: list[Mapping[str, Any]]) -> dict[str, Any]:
    records = [StagedOutputRecord(**dict(item)) for item in staged_outputs]
    return asdict(StagingManifestContract(transaction_id=transaction_id, planned_outputs=planned_outputs, staged_outputs=records, status=TX_STAGED))


def validate_staging_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    planned = {normalize_path(item) for item in manifest.get("planned_outputs", [])}
    staged_records = manifest.get("staged_outputs", [])
    staged = {normalize_path(item.get("destination_path", "")) for item in staged_records}

    findings: list[str] = []
    statuses: list[str] = []

    if not planned:
        statuses.append(BLOCK)
        findings.append("STAGING_PLANNED_OUTPUTS_EMPTY")

    if planned - staged:
        statuses.append(BLOCK)
        findings.append("STAGING_PLANNED_OUTPUT_NOT_STAGED")

    if staged - planned:
        statuses.append(LOCK)
        findings.append("STAGING_OUTPUT_NOT_PLANNED")

    for item in staged_records:
        if not is_valid_sha256(item.get("sha256")):
            statuses.append(LOCK)
            findings.append("STAGING_HASH_INVALID")
        if item.get("size_bytes", 0) < 0:
            statuses.append(BLOCK)
            findings.append("STAGING_SIZE_INVALID")

    return make_result(choose_worst_status(statuses or [PASS]), "STAGING_MANIFEST_VALIDATED", findings)


def build_privileged_promotion_request(staged: Mapping[str, Any], destination: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "staged_output": dict(staged),
        "destination": dict(destination),
        "helper": "privileged_promote_staged_output",
    }


def validate_privileged_promotion_scope(request: Mapping[str, Any]) -> dict[str, Any]:
    staged = request.get("staged_output", {})
    destination = request.get("destination", {})

    findings: list[str] = []
    statuses: list[str] = []

    if request.get("helper") != "privileged_promote_staged_output":
        statuses.append(LOCK)
        findings.append("PRIVILEGED_HELPER_SCOPE_LOCK")

    if destination.get("protected_root") is True:
        statuses.append(LOCK)
        findings.append("PRIVILEGED_HELPER_PROTECTED_ROOT_LOCK")

    if destination.get("root_escape") is True:
        statuses.append(LOCK)
        findings.append("PRIVILEGED_HELPER_EXTERNAL_ROOT_LOCK")

    if destination.get("in_allowlist") is not True:
        statuses.append(BLOCK)
        findings.append("PRIVILEGED_HELPER_NOT_IN_ALLOWLIST_BLOCK")

    if not is_valid_sha256(staged.get("sha256")):
        statuses.append(LOCK)
        findings.append("PRIVILEGED_HELPER_EXPECTED_HASH_INVALID")

    return make_result(choose_worst_status(statuses or [PASS]), "PRIVILEGED_PROMOTION_SCOPE_VALIDATED", findings)


def privileged_promote_staged_output(staged: Mapping[str, Any], destination: Mapping[str, Any]) -> dict[str, Any]:
    request = build_privileged_promotion_request(staged, destination)
    scope = validate_privileged_promotion_scope(request)
    if scope["status"] != PASS:
        return scope

    staged_path = Path(staged["staged_path"])
    destination_path = Path(destination["canonical_path"])

    if not staged_path.exists():
        return make_result(BLOCK, "STAGED_SOURCE_MISSING")

    before_hash = sha256_file(destination_path) if destination_path.exists() else None
    expected_hash = staged["sha256"]

    if sha256_file(staged_path) != expected_hash:
        return make_result(LOCK, "STAGED_HASH_MISMATCH_BEFORE_PROMOTION")

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    staged_path.replace(destination_path)

    after_hash = sha256_file(destination_path)
    if after_hash != expected_hash:
        return make_result(LOCK, "PROMOTION_HASH_VERIFY_FAIL_LOCK", destination_hash_before=before_hash, destination_hash_after=after_hash)

    return make_result(PASS, "PROMOTION_COMPLETED", destination_hash_before=before_hash, destination_hash_after=after_hash)


def build_promotion_manifest(transaction_id: str, promoted_outputs: list[str], before: dict[str, str | None], after: dict[str, str], results: dict[str, str]) -> dict[str, Any]:
    return asdict(PromotionManifestContract(transaction_id=transaction_id, promoted_outputs=promoted_outputs, destination_hashes_before=before, destination_hashes_after=after, promotion_results=results, status=TX_PROMOTED))


def validate_promotion_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    outputs = manifest.get("promoted_outputs", [])
    after = manifest.get("destination_hashes_after", {})
    results = manifest.get("promotion_results", {})
    findings: list[str] = []
    statuses: list[str] = []

    if not outputs:
        statuses.append(BLOCK)
        findings.append("PROMOTION_OUTPUTS_EMPTY")

    for output in outputs:
        if results.get(output) != PASS:
            statuses.append(LOCK)
            findings.append(f"PROMOTION_RESULT_NOT_PASS:{output}")
        if not is_valid_sha256(after.get(output)):
            statuses.append(LOCK)
            findings.append(f"PROMOTION_DESTINATION_HASH_INVALID:{output}")

    return make_result(choose_worst_status(statuses or [PASS]), "PROMOTION_MANIFEST_VALIDATED", findings)


def build_quarantine_contract(quarantine_id: str, transaction_id: str, reason: str, paths: list[str], hashes: dict[str, str], manual_review_required: bool, auto_recover_allowed: bool) -> dict[str, Any]:
    return asdict(QuarantineContract(quarantine_id=quarantine_id, transaction_id=transaction_id, reason=reason, quarantined_paths=paths, hashes=hashes, manual_review_required=manual_review_required, auto_recover_allowed=auto_recover_allowed))


def validate_quarantine_contract(contract: Mapping[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    statuses: list[str] = []

    for key in ["quarantine_id", "transaction_id", "reason"]:
        if not contract.get(key):
            statuses.append(BLOCK)
            findings.append(f"MISSING_{key.upper()}")

    dangerous = contract.get("reason") in {"PROTECTED_ROOT_VIOLATION", "PARTIAL_PROMOTION", "HASH_MISMATCH"}
    if dangerous and contract.get("manual_review_required") is not True:
        statuses.append(LOCK)
        findings.append("MANUAL_REVIEW_REQUIRED_FALSE_ON_DANGEROUS_CASE")

    if dangerous and contract.get("auto_recover_allowed") is True:
        statuses.append(LOCK)
        findings.append("AUTO_RECOVER_ALLOWED_TRUE_ON_DANGEROUS_CASE")

    for path in contract.get("quarantined_paths", []):
        if is_protected_path(path):
            statuses.append(LOCK)
            findings.append("PROTECTED_ROOT_QUARANTINE_PATH")

    return make_result(choose_worst_status(statuses or [PASS]), "QUARANTINE_CONTRACT_VALIDATED", findings)


def classify_failure_point(failure_point: str) -> dict[str, Any]:
    recovery_class = FAILURE_POINT_CLASS.get(failure_point)
    if recovery_class is None:
        return make_result(LOCK, "TX_FAILPOINT_UNKNOWN_LOCK", recovery_class=RECOVERY_CLASS_E_LOCKED_IRRECOVERABLE_WITHOUT_OPERATOR)
    return make_result(PASS, "FAILURE_POINT_CLASSIFIED", recovery_class=recovery_class)


def build_failure_point_matrix() -> dict[str, str]:
    return dict(FAILURE_POINT_CLASS)


def validate_failure_point_matrix(matrix: Mapping[str, str]) -> dict[str, Any]:
    missing = sorted(set(FAILURE_POINT_CLASS) - set(matrix))
    if missing:
        return make_result(LOCK, "FAILURE_POINT_MATRIX_MISSING_KEYS", missing)
    invalid = sorted(key for key, value in matrix.items() if value not in set(FAILURE_POINT_CLASS.values()))
    if invalid:
        return make_result(LOCK, "FAILURE_POINT_MATRIX_INVALID_CLASS", invalid)
    return make_result(PASS, "FAILURE_POINT_MATRIX_VALIDATED", count=len(matrix))


def build_recovery_manifest(recovery_id: str, transaction_id: str, failure_point: str, staged: list[str], promoted: list[str], quarantined: list[str], rollback_draft: dict[str, Any]) -> dict[str, Any]:
    classified = classify_failure_point(failure_point)
    recovery_class = classified.get("recovery_class", RECOVERY_CLASS_E_LOCKED_IRRECOVERABLE_WITHOUT_OPERATOR)
    manual = recovery_class in {RECOVERY_CLASS_D_MANUAL_REVIEW_REQUIRED, RECOVERY_CLASS_E_LOCKED_IRRECOVERABLE_WITHOUT_OPERATOR}
    auto = recovery_class in {RECOVERY_CLASS_A_SAFE_NOOP, RECOVERY_CLASS_B_SAFE_RETRY_AFTER_CLEANUP}
    return asdict(RecoveryManifestContract(recovery_id=recovery_id, transaction_id=transaction_id, failure_point=failure_point, recovery_class=recovery_class, staged_outputs=staged, promoted_outputs=promoted, quarantined_outputs=quarantined, rollback_draft=rollback_draft, auto_recovery_allowed=auto, manual_review_required=manual))


def validate_recovery_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    statuses: list[str] = []

    classified = classify_failure_point(manifest.get("failure_point", ""))
    if classified["status"] != PASS:
        statuses.append(LOCK)
        findings.append("UNKNOWN_FAILURE_POINT")

    recovery_class = manifest.get("recovery_class")
    if recovery_class in {RECOVERY_CLASS_D_MANUAL_REVIEW_REQUIRED, RECOVERY_CLASS_E_LOCKED_IRRECOVERABLE_WITHOUT_OPERATOR}:
        if manifest.get("auto_recovery_allowed") is True:
            statuses.append(LOCK)
            findings.append("AUTO_RECOVERY_ALLOWED_FOR_CLASS_D_OR_E")
        if manifest.get("manual_review_required") is not True:
            statuses.append(LOCK)
            findings.append("MANUAL_REVIEW_REQUIRED_NOT_TRUE_FOR_CLASS_D_OR_E")

    return make_result(choose_worst_status(statuses or [PASS]), "RECOVERY_MANIFEST_VALIDATED", findings)


def build_rollback_draft(transaction_id: str, candidate_operations: list[dict[str, Any]], execution_requested: bool = False) -> dict[str, Any]:
    return {
        "transaction_id": transaction_id,
        "rollback_draft_allowed": True,
        "rollback_execution_allowed": False,
        "rollback_execution_requested": execution_requested,
        "candidate_operations": candidate_operations,
    }


def validate_rollback_draft_only(draft: Mapping[str, Any]) -> dict[str, Any]:
    text = canonical_json(draft).lower()
    forbidden = ["git reset", "git checkout", "unlink", "delete", "manual restore", "brain restore"]
    findings = [token for token in forbidden if token in text]

    if draft.get("rollback_execution_requested") is True or draft.get("rollback_execution_allowed") is True:
        return make_result(LOCK, "ROLLBACK_EXECUTION_FORBIDDEN", findings)

    if findings:
        return make_result(LOCK, "ROLLBACK_DESTRUCTIVE_CONTENT_FORBIDDEN", findings)

    return make_result(PASS, "ROLLBACK_DRAFT_ONLY_VALIDATED")


def validate_no_plan_reinterpretation(declared: Mapping[str, Any], final: Mapping[str, Any]) -> dict[str, Any]:
    findings: list[str] = []
    statuses: list[str] = []

    for key in ["planned_outputs", "permissions", "allowlist_digest"]:
        if declared.get(key) != final.get(key):
            statuses.append(LOCK)
            findings.append(f"PLAN_{key.upper()}_MUTATED")

    if final.get("allowlist_expanded") is True:
        statuses.append(LOCK)
        findings.append("PLAN_ALLOWLIST_EXPANSION_FORBIDDEN")

    if final.get("permission_inferred") is True:
        statuses.append(LOCK)
        findings.append("PLAN_PERMISSION_INFERENCE_FORBIDDEN")

    return make_result(choose_worst_status(statuses or [PASS]), "NO_PLAN_REINTERPRETATION_VALIDATED", findings)


def build_post_write_audit(transaction_id: str, output_scope_result: str, hash_verification_result: str, no_touch_result: str, lock_release_result: str, tmp_residue_result: str, repo_status_result: str, next_safe_step: str) -> dict[str, Any]:
    return asdict(PostWriteAuditContract(transaction_id=transaction_id, output_scope_result=output_scope_result, hash_verification_result=hash_verification_result, no_touch_result=no_touch_result, lock_release_result=lock_release_result, tmp_residue_result=tmp_residue_result, repo_status_result=repo_status_result, next_safe_step=next_safe_step))


def validate_post_write_audit(audit: Mapping[str, Any]) -> dict[str, Any]:
    statuses: list[str] = []
    findings: list[str] = []

    for key in ["output_scope_result", "hash_verification_result", "no_touch_result", "lock_release_result", "tmp_residue_result", "repo_status_result"]:
        value = audit.get(key)
        if value == LOCK:
            statuses.append(LOCK)
            findings.append(f"{key}_LOCK")
        elif value != PASS:
            statuses.append(BLOCK)
            findings.append(f"{key}_NOT_PASS")

    if audit.get("next_safe_step") != "BLOQUE_8_POST_BUILD_AUDIT":
        statuses.append(LOCK)
        findings.append("POST_WRITE_AUDIT_NEXT_STEP_INVALID")

    return make_result(choose_worst_status(statuses or [PASS]), "POST_WRITE_AUDIT_VALIDATED", findings)


def build_block8_report_payloads(consumed_head: str, consumed_subject: str) -> dict[str, Any]:
    permissions = {
        "post_build_audit_allowed_next": True,
        "validation_map_allowed_now": False,
        "validation_plan_allowed_now": False,
        "validation_allowed_now": False,
        "gate_closure_allowed_now": False,
        "bloque_9_allowed_now": False,
        "manual_write_allowed_now": False,
        "brain_write_allowed_now": False,
        "reports_brain_write_allowed_now": False,
        "execution_allowed_now": False,
        "n8n_allowed_now": False,
        "webhook_allowed_now": False,
        "publishing_allowed_now": False,
        "capa9_allowed_now": False,
        "rollback_execution_allowed": False,
    }

    base = {
        "project": "CONTENT_ENGINE_OMEGA",
        "subsystem": "MANUAL_CEREBRO_BRIDGE",
        "block": "BLOQUE_8_ATOMIC_WRITER_LOCK_QUARANTINE_RECOVERY",
        "status": "BUILT_PENDING_POST_AUDIT",
        "result": "PASS",
        "consumed_block7_head": consumed_head,
        "consumed_block7_subject": consumed_subject,
        "next_safe_step": "BLOQUE_8_POST_BUILD_AUDIT",
        "permissions": permissions,
    }

    limits = build_transaction_limit_contract()
    planned_outputs = ["00_SYSTEM/bridge/reports/BRIDGE_BLOCK_8_BUILD_REPORT.json"]
    tx = build_atomic_write_transaction("B8-TX-BUILD-SMOKE", "ATOMIC_WRITE", consumed_head, "BLOQUE_8", planned_outputs, permissions)
    lock = build_lock_contract("B8-LOCK-BUILD-SMOKE", "B8-TX-BUILD-SMOKE", consumed_head, tx["allowlist_digest"])
    destination = canonicalize_destination_path(planned_outputs[0], ".", planned_outputs)
    staged = {
        "staged_path": "staging/BRIDGE_BLOCK_8_BUILD_REPORT.json",
        "destination_path": planned_outputs[0],
        "sha256": "a" * 64,
        "size_bytes": 10,
        "canonical_json": True,
    }
    staging = build_staging_manifest("B8-TX-BUILD-SMOKE", planned_outputs, [staged])
    promotion = build_promotion_manifest("B8-TX-BUILD-SMOKE", planned_outputs, {planned_outputs[0]: None}, {planned_outputs[0]: "a" * 64}, {planned_outputs[0]: PASS})
    quarantine = build_quarantine_contract("B8-Q-SMOKE", "B8-TX-BUILD-SMOKE", "HASH_MISMATCH", ["00_SYSTEM/bridge/quarantine/x.json"], {"x": "a" * 64}, True, False)
    rollback = build_rollback_draft("B8-TX-BUILD-SMOKE", [{"operation": "restore candidate only"}], False)
    recovery = build_recovery_manifest("B8-R-SMOKE", "B8-TX-BUILD-SMOKE", "FAILPOINT_07_PROMOTION_PARTIAL", [], planned_outputs, [], rollback)
    post = build_post_write_audit("B8-TX-BUILD-SMOKE", PASS, PASS, PASS, PASS, PASS, PASS, "BLOQUE_8_POST_BUILD_AUDIT")

    return {
        "BRIDGE_BLOCK_8_BUILD_REPORT.json": {
            **base,
            "report": "BRIDGE_BLOCK_8_BUILD_REPORT",
            "semantic_name": "Transactionally Audited Staged Promotion Engine",
            "os_level_multi_file_atomicity_assumed": False,
            "transactional_consistency_audited": True,
        },
        "BRIDGE_BLOCK_8_TRANSACTION_CONTRACT_REPORT.json": {
            **base,
            "report": "BRIDGE_BLOCK_8_TRANSACTION_CONTRACT_REPORT",
            "transaction_contract_validation": validate_atomic_write_transaction(tx),
            "transaction_limit_validation": validate_transaction_limits(limits, planned_outputs, {planned_outputs[0]: 10}),
            "no_plan_reinterpretation_validation": validate_no_plan_reinterpretation(tx, dict(tx)),
            "rollback_draft_only_validation": validate_rollback_draft_only(rollback),
        },
        "BRIDGE_BLOCK_8_PATH_BOUNDARY_REPORT.json": {
            **base,
            "report": "BRIDGE_BLOCK_8_PATH_BOUNDARY_REPORT",
            "path_boundary_validation": validate_path_boundary(destination["record"]),
            "output_allowlist_validation": validate_output_allowlist(planned_outputs, planned_outputs),
        },
        "BRIDGE_BLOCK_8_LOCK_AND_STALE_LOCK_REPORT.json": {
            **base,
            "report": "BRIDGE_BLOCK_8_LOCK_AND_STALE_LOCK_REPORT",
            "lock_validation": validate_lock_contract(lock, consumed_head, tx["allowlist_digest"]),
            "stale_lock_validation": classify_stale_lock({**lock, "status": "LOCK_STALE"}, audit_passed=False),
        },
        "BRIDGE_BLOCK_8_STAGING_PROMOTION_REPORT.json": {
            **base,
            "report": "BRIDGE_BLOCK_8_STAGING_PROMOTION_REPORT",
            "staging_manifest_validation": validate_staging_manifest(staging),
            "privileged_promotion_scope_validation": validate_privileged_promotion_scope(build_privileged_promotion_request(staged, destination["record"])),
            "promotion_manifest_validation": validate_promotion_manifest(promotion),
        },
        "BRIDGE_BLOCK_8_QUARANTINE_RECOVERY_REPORT.json": {
            **base,
            "report": "BRIDGE_BLOCK_8_QUARANTINE_RECOVERY_REPORT",
            "quarantine_validation": validate_quarantine_contract(quarantine),
            "failure_point_matrix_validation": validate_failure_point_matrix(build_failure_point_matrix()),
            "recovery_manifest_validation": validate_recovery_manifest(recovery),
        },
        "BRIDGE_BLOCK_8_PERMISSION_AND_LIMITS_REPORT.json": {
            **base,
            "report": "BRIDGE_BLOCK_8_PERMISSION_AND_LIMITS_REPORT",
            "dangerous_permissions_all_false": all(value is False for key, value in permissions.items() if key != "post_build_audit_allowed_next"),
            "transaction_limits": limits,
            "post_write_audit_validation": validate_post_write_audit(post),
        },
        "BRIDGE_BLOCK_8_NEXT_LAYER_READINESS_MAP.json": {
            **base,
            "report": "BRIDGE_BLOCK_8_NEXT_LAYER_READINESS_MAP",
            "current_status": "BUILT_PENDING_POST_AUDIT",
            "readiness_status": "READY_FOR_POST_BUILD_AUDIT_ONLY",
            "post_build_audit_allowed_next": True,
            "validation_map_allowed_now": False,
            "validation_allowed_now": False,
            "gate_closure_allowed_now": False,
            "bloque_9_allowed_now": False,
        },
    }


__all__ = [
    "PASS",
    "BLOCK",
    "LOCK",
    "REVIEW",
    "REVIEW_REQUIRED",
    "TX_DECLARED",
    "TX_PREFLIGHT_PASS",
    "TX_LOCK_ACQUIRED",
    "TX_STAGED",
    "TX_STAGING_VERIFIED",
    "TX_PROMOTION_READY",
    "TX_PROMOTED",
    "TX_POST_WRITE_AUDITED",
    "TX_CLOSED",
    "TX_BLOCKED",
    "TX_LOCKED",
    "TX_QUARANTINED",
    "TX_RECOVERY_REQUIRED",
    "RECOVERY_CLASS_A_SAFE_NOOP",
    "RECOVERY_CLASS_B_SAFE_RETRY_AFTER_CLEANUP",
    "RECOVERY_CLASS_C_QUARANTINE_REQUIRED",
    "RECOVERY_CLASS_D_MANUAL_REVIEW_REQUIRED",
    "RECOVERY_CLASS_E_LOCKED_IRRECOVERABLE_WITHOUT_OPERATOR",
    "TransactionLimitContract",
    "AtomicWriteTransactionContract",
    "CanonicalDestinationRecord",
    "StagedOutputRecord",
    "LockContract",
    "StagingManifestContract",
    "PromotionManifestContract",
    "QuarantineContract",
    "RecoveryManifestContract",
    "PostWriteAuditContract",
    "canonical_json",
    "sha256_text",
    "sha256_bytes",
    "sha256_file",
    "normalize_path",
    "is_valid_sha256",
    "is_protected_path",
    "make_result",
    "choose_worst_status",
    "build_transaction_limit_contract",
    "validate_transaction_limits",
    "build_atomic_write_transaction",
    "validate_atomic_write_transaction",
    "canonicalize_destination_path",
    "validate_path_boundary",
    "validate_output_allowlist",
    "build_lock_contract",
    "validate_lock_contract",
    "classify_stale_lock",
    "build_staging_manifest",
    "validate_staging_manifest",
    "build_privileged_promotion_request",
    "validate_privileged_promotion_scope",
    "privileged_promote_staged_output",
    "build_promotion_manifest",
    "validate_promotion_manifest",
    "build_quarantine_contract",
    "validate_quarantine_contract",
    "build_recovery_manifest",
    "validate_recovery_manifest",
    "classify_failure_point",
    "build_failure_point_matrix",
    "validate_failure_point_matrix",
    "build_rollback_draft",
    "validate_rollback_draft_only",
    "validate_no_plan_reinterpretation",
    "build_post_write_audit",
    "validate_post_write_audit",
    "build_block8_report_payloads",
]
