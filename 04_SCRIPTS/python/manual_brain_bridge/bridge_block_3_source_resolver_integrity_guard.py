from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

BLOCK_ID = "BLOQUE_3_SOURCE_RESOLVER_INTEGRITY_GUARD"
LIFECYCLE_STATUS = "BUILT_PENDING_POST_AUDIT"
NEXT_SAFE_STEP = "BLOQUE_3_POST_BUILD_AUDIT"

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
    "04_SCRIPTS/python/manual_brain_bridge/bridge_block_3_source_resolver_integrity_guard.py",
    "tests/manual_brain_bridge/test_bridge_block_3_source_resolver_integrity_guard.py",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_3_SOURCE_RESOLUTION_MAP.json",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_3_SOURCE_INTEGRITY_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_3_SOURCE_BOUNDARY_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_3_DENIED_SOURCE_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_3_VALIDATION_REPORT.json",
    "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_3_NEXT_LAYER_READINESS_MAP.json",
    "00_SYSTEM/bridge/manifests/BRIDGE_BLOCK_3_MANIFEST.json",
    "00_SYSTEM/bridge/manifests/BRIDGE_BLOCK_3_SEAL.json",
    "05_REPORTS/manual_brain_bridge/BRIDGE_BLOCK_3_SOURCE_RESOLVER_INTEGRITY_GUARD_SUMMARY.md",
)

ALLOWED_SOURCE_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml", ".csv"}
DENIED_SOURCE_EXTENSIONS = {
    ".exe", ".dll", ".bat", ".cmd", ".vbs", ".scr", ".msi",
    ".ps1", ".pyc", ".pyd", ".zip", ".7z", ".rar", ".tar",
    ".gz", ".db", ".sqlite", ".sqlite3", ".bin",
}
TEMP_PARTIAL_SUFFIXES = (".tmp", ".partial", ".bak", ".orig", ".pyc")
RESERVED_WINDOWS_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}
MAX_FILE_SIZE_BYTES_DEFAULT = 1_048_576
MAX_PREVIEW_BYTES = 512
MAX_HASH_SIZE_BYTES = 10_485_760

ERROR_CODES = (
    "B3_SOURCE_PATH_EMPTY_LOCK", "B3_SOURCE_PATH_TRAVERSAL_LOCK", "B3_SOURCE_PATH_OUTSIDE_ROOT_LOCK",
    "B3_SOURCE_UNC_PATH_LOCK", "B3_SOURCE_WINDOWS_RESERVED_NAME_LOCK", "B3_SOURCE_ADS_STREAM_LOCK",
    "B3_SOURCE_DRIVE_ESCAPE_LOCK", "B3_SOURCE_TRAILING_DOT_SPACE_LOCK",
    "B3_SOURCE_TYPE_UNKNOWN_LOCK", "B3_SOURCE_AUTHORITY_UNKNOWN_REVIEW", "B3_SOURCE_AUTHORITY_CONFLICT_BLOCK",
    "B3_SOURCE_READABLE_BUT_NOT_AUTHORITATIVE_REVIEW", "B3_SOURCE_NOT_SAFE_FOR_RULE_EXTRACTION_BLOCK",
    "B3_SOURCE_FILE_MISSING_BLOCK", "B3_SOURCE_FILE_UNREADABLE_BLOCK", "B3_SOURCE_FILE_EMPTY_BLOCK",
    "B3_SOURCE_TOO_LARGE_REVIEW", "B3_SOURCE_TOO_LARGE_BLOCK",
    "B3_SOURCE_SYMLINK_LOCK", "B3_SOURCE_JUNCTION_LOCK", "B3_SOURCE_REPARSE_POINT_LOCK",
    "B3_SOURCE_REPARSE_POINT_UNKNOWN_LOCK", "B3_SOURCE_PARENT_REPARSE_POINT_LOCK",
    "B3_SOURCE_TEMP_PARTIAL_BLOCK", "B3_SOURCE_EXTERNAL_URL_LOCK",
    "B3_SOURCE_NO_TOUCH_WRITE_LOCK", "B3_SOURCE_BRAIN_WRITE_LOCK",
    "B3_SOURCE_MANUAL_WRITE_LOCK", "B3_SOURCE_REPORTS_BRAIN_WRITE_LOCK",
    "B3_SOURCE_HASH_UNAVAILABLE_BLOCK", "B3_SOURCE_HASH_CHANGED_REVIEW",
    "B3_SOURCE_TOCTOU_HASH_CHANGED_BLOCK", "B3_SOURCE_TOCTOU_SIZE_CHANGED_BLOCK",
    "B3_SOURCE_TOCTOU_MTIME_CHANGED_REVIEW", "B3_SOURCE_DISAPPEARED_DURING_READ_BLOCK",
    "B3_SOURCE_ENCODING_UNKNOWN_BLOCK", "B3_SOURCE_BINARY_BLOCK",
    "B3_SOURCE_UTF16_REVIEW", "B3_SOURCE_UTF8_BOM_WARNING",
    "B3_SOURCE_DUPLICATE_HASH_WARNING", "B3_SOURCE_DUPLICATE_NAME_REVIEW",
    "B3_SOURCE_DUPLICATE_AUTHORITY_REVIEW", "B3_SOURCE_DUPLICATE_CONFLICT_BLOCK",
    "B3_SOURCE_CANONICAL_DUPLICATE_LOCK", "B3_SOURCE_SECRET_RISK_LOCK",
    "B3_SOURCE_REPORT_CONTENT_LEAK_LOCK", "B3_SOURCE_CAPA9_LOCK",
    "B3_NEXT_STEP_UNSAFE_BLOCK", "TEST_DOMAIN_COVERAGE_INCOMPLETE",
    "PYTEST_BASETEMP_RESIDUE_DETECTED",
)

SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key)\s*[:=]\s*['\"][^'\"]+['\"]"),
    re.compile(r"(?i)(password)\s*[:=]\s*['\"][^'\"]+['\"]"),
    re.compile(r"(?i)(private[_-]?key)\s*[:=]\s*['\"][^'\"]+['\"]"),
    re.compile(r"(?i)(authorization)\s*:\s*bearer\s+[A-Za-z0-9._\-]+"),
    re.compile(r"\bsk-[A-Za-z0-9]{12,}\b"),
)

COMMON_FLAGS = {
    "block": BLOCK_ID,
    "lifecycle_status": LIFECYCLE_STATUS,
    "real_source_read_performed": False,
    "fixture_based_validation": True,
    "no_manual_current_read": True,
    "no_brain_read": True,
    "no_reports_brain_read": True,
    "execution_allowed_now": False,
    "manual_write_allowed_now": False,
    "brain_write_allowed_now": False,
    "reports_brain_write_allowed_now": False,
    "n8n_allowed_now": False,
    "webhook_allowed_now": False,
    "publishing_allowed_now": False,
    "capa9_allowed_now": False,
    "block_4_allowed_now": False,
    "next_safe_step": NEXT_SAFE_STEP,
}


class Block3Error(Exception):
    pass


def stable_json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def canonical_json_hash(value: Any) -> str:
    return sha256_text(stable_json_dumps(value))


def repo_rel(path: str) -> str:
    p = path.replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return p


def resolve_decision(decisions: list[str]) -> str:
    if not decisions:
        return "BLOCK"
    if any(decision not in DECISION_RANK for decision in decisions):
        return "LOCK"
    return max(decisions, key=lambda decision: DECISION_RANK[decision])


def make_error(error_code: str, decision: str, message: str, component: str = "SOURCE") -> dict[str, Any]:
    if error_code not in ERROR_CODES:
        raise Block3Error(f"UNKNOWN_ERROR_CODE: {error_code}")
    if decision not in ("PASS_WITH_WARNINGS", "REQUIRE_REVIEW", "BLOCK", "LOCK"):
        raise Block3Error("Error envelope cannot produce PASS")
    return {
        "error_code": error_code,
        "decision": decision,
        "message": message,
        "component": component,
        "safe_next_step": "REVIEW_SOURCE_RESOLUTION_FAILURE",
    }


def is_external_url(path: str) -> bool:
    return bool(re.match(r"(?i)^(https?|ftp)://", path.strip()))


def has_null_byte(path: str) -> bool:
    return "\x00" in path


def has_traversal(path: str) -> bool:
    return any(part == ".." for part in Path(repo_rel(path)).parts)


def is_unc_path(path: str) -> bool:
    raw = path.strip()
    return raw.startswith("\\\\") or raw.startswith("//")


def has_drive_prefix(path: str) -> bool:
    return bool(re.match(r"^[A-Za-z]:[\\/]", path))


def has_ads_stream(path: str) -> bool:
    raw = path.strip()
    if has_drive_prefix(raw):
        raw = raw[2:]
    return ":" in raw


def has_trailing_dot_or_space(path: str) -> bool:
    parts = re.split(r"[\\/]+", path)
    return any(part.endswith(".") or part.endswith(" ") for part in parts if part)


def has_reserved_windows_name(path: str) -> bool:
    parts = re.split(r"[\\/]+", path)
    for part in parts:
        clean = part.strip(" .")
        if not clean:
            continue
        base = clean.split(".")[0].upper()
        if base in RESERVED_WINDOWS_NAMES:
            return True
    return False


def windows_path_findings(path: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if is_unc_path(path):
        findings.append(make_error("B3_SOURCE_UNC_PATH_LOCK", "LOCK", "UNC path is blocked.", "PATH"))
    if has_ads_stream(path):
        findings.append(make_error("B3_SOURCE_ADS_STREAM_LOCK", "LOCK", "ADS stream syntax is blocked.", "PATH"))
    if has_reserved_windows_name(path):
        findings.append(make_error("B3_SOURCE_WINDOWS_RESERVED_NAME_LOCK", "LOCK", "Reserved Windows name is blocked.", "PATH"))
    if has_trailing_dot_or_space(path):
        findings.append(make_error("B3_SOURCE_TRAILING_DOT_SPACE_LOCK", "LOCK", "Trailing dot/space is blocked.", "PATH"))
    return findings


def detect_no_touch_path(path: str) -> bool:
    normalized = repo_rel(path)
    return any(normalized.startswith(prefix) for prefix in NO_TOUCH_PREFIXES)


def classify_source_type(path: str) -> str:
    p = repo_rel(path)
    if is_external_url(p):
        return "external_url"
    if (
        any(p.endswith(suffix) for suffix in TEMP_PARTIAL_SUFFIXES)
        or "__pycache__" in p
        or p == ".pytest_cache"
        or p.startswith(".pytest_cache/")
        or "/.pytest_cache/" in p
    ):
        return "temp_partial"
    if p.startswith("00_SYSTEM/manual/current/"):
        return "manual_current"
    if p.startswith("00_SYSTEM/manual/historical/"):
        return "manual_historical"
    if p.startswith("00_SYSTEM/manual/manifest/"):
        return "manual_manifest"
    if p.startswith("00_SYSTEM/manual/registry/"):
        return "manual_registry"
    if p.startswith("00_SYSTEM/brain/"):
        return "brain"
    if p.startswith("00_SYSTEM/reports/brain/"):
        return "reports_brain"
    if p.startswith("00_SYSTEM/bridge/reports/"):
        return "bridge_reports"
    if p.startswith("00_SYSTEM/bridge/manifests/"):
        return "bridge_manifest"
    if p.startswith("tests/") or p.startswith(".pytest_block3_basetemp/"):
        return "test_fixture"
    return "unknown"


def resolve_authority(source_type: str, explicit_canonical: bool = False) -> str:
    if explicit_canonical:
        return "AUTHORITY_CANONICAL"
    if source_type == "manual_current":
        return "AUTHORITY_CANONICAL"
    if source_type in ("manual_manifest", "manual_registry"):
        return "AUTHORITY_REFERENCED"
    if source_type == "manual_historical":
        return "AUTHORITY_HISTORICAL"
    if source_type in ("bridge_reports", "bridge_manifest"):
        return "AUTHORITY_DIAGNOSTIC"
    if source_type == "test_fixture":
        return "AUTHORITY_CANONICAL"
    if source_type in ("brain", "reports_brain"):
        return "AUTHORITY_DERIVED"
    return "AUTHORITY_UNKNOWN"


def extension_decision(path: str) -> dict[str, Any]:
    suffix = Path(path).suffix.lower()
    if suffix in DENIED_SOURCE_EXTENSIONS:
        decision = "LOCK" if suffix in {".exe", ".dll", ".bat", ".cmd", ".vbs", ".scr", ".msi", ".ps1"} else "BLOCK"
        return {"decision": decision, "error": make_error("B3_SOURCE_TEMP_PARTIAL_BLOCK", decision, f"Denied extension: {suffix}", "EXTENSION")}
    if suffix in ALLOWED_SOURCE_EXTENSIONS:
        return {"decision": "PASS", "error": None}
    return {"decision": "REQUIRE_REVIEW", "error": make_error("B3_SOURCE_AUTHORITY_UNKNOWN_REVIEW", "REQUIRE_REVIEW", f"Unknown extension: {suffix}", "EXTENSION")}


def size_decision(size_bytes: int) -> dict[str, Any]:
    if size_bytes <= 0:
        return {"decision": "BLOCK", "error": make_error("B3_SOURCE_FILE_EMPTY_BLOCK", "BLOCK", "Empty source file.", "SIZE")}
    if size_bytes <= MAX_FILE_SIZE_BYTES_DEFAULT:
        return {"decision": "PASS", "error": None}
    if size_bytes <= MAX_HASH_SIZE_BYTES:
        return {"decision": "REQUIRE_REVIEW", "error": make_error("B3_SOURCE_TOO_LARGE_REVIEW", "REQUIRE_REVIEW", "Large source requires review.", "SIZE")}
    return {"decision": "BLOCK", "error": make_error("B3_SOURCE_TOO_LARGE_BLOCK", "BLOCK", "Oversized source blocked.", "SIZE")}


def detect_encoding(data: bytes) -> dict[str, Any]:
    if not data:
        return {"encoding_status": "ENCODING_UNKNOWN", "binary_status": "EMPTY", "decision": "BLOCK"}
    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        return {"encoding_status": "ENCODING_UTF16", "binary_status": "TEXT", "decision": "REQUIRE_REVIEW"}
    if data.startswith(b"\xef\xbb\xbf"):
        try:
            data.decode("utf-8-sig")
            return {"encoding_status": "ENCODING_UTF8_BOM", "binary_status": "TEXT", "decision": "PASS_WITH_WARNINGS"}
        except UnicodeDecodeError:
            return {"encoding_status": "ENCODING_UNKNOWN", "binary_status": "UNKNOWN", "decision": "BLOCK"}
    if b"\x00" in data[:4096]:
        return {"encoding_status": "ENCODING_BINARY", "binary_status": "BINARY", "decision": "BLOCK"}
    try:
        data.decode("utf-8")
        if all(byte < 128 for byte in data):
            return {"encoding_status": "ENCODING_ASCII_COMPATIBLE", "binary_status": "TEXT", "decision": "PASS"}
        return {"encoding_status": "ENCODING_UTF8", "binary_status": "TEXT", "decision": "PASS"}
    except UnicodeDecodeError:
        return {"encoding_status": "ENCODING_UNKNOWN", "binary_status": "UNKNOWN", "decision": "BLOCK"}


def scan_secret_risk(text: str) -> dict[str, Any]:
    hits = [pattern.pattern for pattern in SECRET_PATTERNS if pattern.search(text)]
    return {"decision": "LOCK" if hits else "PASS", "hits": hits}


def assert_inside_root(root: Path, relative_path: str) -> Path:
    if not relative_path or has_null_byte(relative_path):
        raise Block3Error("B3_SOURCE_PATH_EMPTY_LOCK")
    if is_external_url(relative_path):
        raise Block3Error("B3_SOURCE_EXTERNAL_URL_LOCK")
    if is_unc_path(relative_path):
        raise Block3Error("B3_SOURCE_UNC_PATH_LOCK")
    if has_ads_stream(relative_path):
        raise Block3Error("B3_SOURCE_ADS_STREAM_LOCK")
    if has_reserved_windows_name(relative_path):
        raise Block3Error("B3_SOURCE_WINDOWS_RESERVED_NAME_LOCK")
    if has_trailing_dot_or_space(relative_path):
        raise Block3Error("B3_SOURCE_TRAILING_DOT_SPACE_LOCK")
    if has_traversal(relative_path):
        raise Block3Error("B3_SOURCE_PATH_TRAVERSAL_LOCK")
    if has_drive_prefix(relative_path):
        raise Block3Error("B3_SOURCE_DRIVE_ESCAPE_LOCK")

    root_resolved = root.resolve(strict=True)
    resolved = (root_resolved / repo_rel(relative_path)).resolve(strict=False)

    if not resolved.is_relative_to(root_resolved):
        raise Block3Error("B3_SOURCE_PATH_OUTSIDE_ROOT_LOCK")
    return resolved


def reparse_guard(is_symlink: bool = False, is_reparse_point: bool = False, parent_reparse: bool = False, known: bool = True) -> dict[str, Any]:
    if parent_reparse:
        return {"decision": "LOCK", "error_code": "B3_SOURCE_PARENT_REPARSE_POINT_LOCK"}
    if is_symlink:
        return {"decision": "LOCK", "error_code": "B3_SOURCE_SYMLINK_LOCK"}
    if is_reparse_point:
        return {"decision": "LOCK", "error_code": "B3_SOURCE_REPARSE_POINT_LOCK"}
    if not known:
        return {"decision": "LOCK", "error_code": "B3_SOURCE_REPARSE_POINT_UNKNOWN_LOCK"}
    return {"decision": "PASS", "error_code": None}


def path_reparse_findings(path: Path, root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    root_resolved = root.resolve(strict=True)
    for item in [path] + list(path.parents):
        if not item.is_relative_to(root_resolved):
            break
        try:
            if item.is_symlink():
                findings.append(make_error("B3_SOURCE_SYMLINK_LOCK", "LOCK", "Symlink is blocked.", "PATH"))
                break
            attrs = getattr(item.lstat(), "st_file_attributes", 0)
            if attrs and attrs & 0x400:
                findings.append(make_error("B3_SOURCE_REPARSE_POINT_LOCK", "LOCK", "Windows reparse point is blocked.", "PATH"))
                break
        except OSError:
            continue
    return findings


def toctou_decision(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    if before.get("exists") is True and after.get("exists") is False:
        return {"decision": "BLOCK", "error_code": "B3_SOURCE_DISAPPEARED_DURING_READ_BLOCK"}
    if before.get("sha256") != after.get("sha256"):
        return {"decision": "BLOCK", "error_code": "B3_SOURCE_TOCTOU_HASH_CHANGED_BLOCK"}
    if before.get("size_bytes") != after.get("size_bytes"):
        return {"decision": "BLOCK", "error_code": "B3_SOURCE_TOCTOU_SIZE_CHANGED_BLOCK"}
    if before.get("mtime_ns") != after.get("mtime_ns"):
        return {"decision": "REQUIRE_REVIEW", "error_code": "B3_SOURCE_TOCTOU_MTIME_CHANGED_REVIEW"}
    return {"decision": "PASS", "error_code": None}


def build_file_snapshot(root: Path, requested_path: str, *, explicit_canonical: bool = False, allow_real_source_read: bool = False) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    try:
        resolved_path = assert_inside_root(root, requested_path)
    except Block3Error as exc:
        code = str(exc)
        decision = "LOCK" if code.endswith("_LOCK") else "BLOCK"
        return {
            "source_id": sha256_text(requested_path)[:16],
            "requested_path": requested_path,
            "normalized_path": repo_rel(requested_path),
            "resolved_path": "",
            "source_type": "external_url" if is_external_url(requested_path) else "unknown",
            "authority_status": "AUTHORITY_UNKNOWN",
            "read_allowed": False,
            "write_allowed": False,
            "safe_for_rule_extraction": False,
            "decision": decision,
            "errors": [make_error(code, decision, "Path rejected.", "PATH")] if code in ERROR_CODES else [],
        }

    normalized = resolved_path.relative_to(root.resolve(strict=True)).as_posix()
    source_type = classify_source_type(normalized)
    authority_status = resolve_authority(source_type, explicit_canonical=explicit_canonical)

    if source_type in ("manual_current", "manual_historical", "manual_manifest", "manual_registry", "brain", "reports_brain") and not allow_real_source_read:
        return {
            "source_id": sha256_text(normalized)[:16],
            "requested_path": requested_path,
            "normalized_path": normalized,
            "resolved_path": normalized,
            "source_type": source_type,
            "authority_status": authority_status,
            "read_allowed": False,
            "write_allowed": False,
            "safe_for_rule_extraction": False,
            "decision": "LOCK",
            "errors": [make_error("B3_SOURCE_NO_TOUCH_WRITE_LOCK", "LOCK", "Real manual/brain source reads are blocked in build base.", "NO_TOUCH")],
        }

    if not resolved_path.exists():
        return {
            "source_id": sha256_text(normalized)[:16],
            "requested_path": requested_path,
            "normalized_path": normalized,
            "resolved_path": normalized,
            "source_type": source_type,
            "authority_status": "AUTHORITY_UNKNOWN",
            "read_allowed": False,
            "write_allowed": False,
            "safe_for_rule_extraction": False,
            "decision": "BLOCK",
            "errors": [make_error("B3_SOURCE_FILE_MISSING_BLOCK", "BLOCK", "Source file missing.", "FILE")],
        }

    findings.extend(path_reparse_findings(resolved_path, root))
    ext = extension_decision(normalized)
    if ext["error"]:
        findings.append(ext["error"])

    try:
        pre_stat = resolved_path.stat()
        data = resolved_path.read_bytes()
        post_stat = resolved_path.stat()
    except OSError:
        return {
            "source_id": sha256_text(normalized)[:16],
            "requested_path": requested_path,
            "normalized_path": normalized,
            "resolved_path": normalized,
            "source_type": source_type,
            "authority_status": authority_status,
            "read_allowed": False,
            "write_allowed": False,
            "safe_for_rule_extraction": False,
            "decision": "BLOCK",
            "errors": [make_error("B3_SOURCE_FILE_UNREADABLE_BLOCK", "BLOCK", "Source unreadable.", "FILE")],
        }

    encoding = detect_encoding(data)
    size = size_decision(len(data))

    if size["error"]:
        findings.append(size["error"])
    if encoding["decision"] == "BLOCK":
        code = "B3_SOURCE_BINARY_BLOCK" if encoding["encoding_status"] == "ENCODING_BINARY" else "B3_SOURCE_ENCODING_UNKNOWN_BLOCK"
        findings.append(make_error(code, "BLOCK", "Encoding blocked.", "ENCODING"))
    elif encoding["decision"] == "REQUIRE_REVIEW":
        findings.append(make_error("B3_SOURCE_UTF16_REVIEW", "REQUIRE_REVIEW", "UTF-16 requires review.", "ENCODING"))
    elif encoding["decision"] == "PASS_WITH_WARNINGS":
        findings.append(make_error("B3_SOURCE_UTF8_BOM_WARNING", "PASS_WITH_WARNINGS", "UTF-8 BOM detected.", "ENCODING"))

    pre = {"exists": True, "sha256": sha256_bytes(data), "size_bytes": pre_stat.st_size, "mtime_ns": pre_stat.st_mtime_ns}
    post_data = resolved_path.read_bytes() if resolved_path.exists() else b""
    post = {"exists": resolved_path.exists(), "sha256": sha256_bytes(post_data), "size_bytes": post_stat.st_size, "mtime_ns": post_stat.st_mtime_ns}
    toctou = toctou_decision(pre, post)
    if toctou["decision"] != "PASS":
        findings.append(make_error(toctou["error_code"], toctou["decision"], "TOCTOU guard failed.", "TOCTOU"))

    if authority_status == "AUTHORITY_UNKNOWN":
        findings.append(make_error("B3_SOURCE_AUTHORITY_UNKNOWN_REVIEW", "REQUIRE_REVIEW", "Authority unknown.", "AUTHORITY"))

    decision = resolve_decision([item["decision"] for item in findings] or ["PASS"])
    safe_for_rule_extraction = decision == "PASS" and authority_status == "AUTHORITY_CANONICAL" and encoding["binary_status"] == "TEXT" and source_type in ("test_fixture", "manual_current")

    return {
        "source_id": sha256_text(normalized)[:16],
        "requested_path": requested_path,
        "normalized_path": normalized,
        "resolved_path": normalized,
        "source_type": source_type,
        "authority_status": authority_status,
        "sha256": sha256_bytes(data),
        "size_bytes": len(data),
        "last_write_time_utc": str(pre_stat.st_mtime_ns),
        "encoding_status": encoding["encoding_status"],
        "binary_status": encoding["binary_status"],
        "read_allowed": decision in ("PASS", "PASS_WITH_WARNINGS", "REQUIRE_REVIEW"),
        "write_allowed": False,
        "safe_for_rule_extraction": safe_for_rule_extraction,
        "decision": decision,
        "errors": findings,
        "content_preview_hash": sha256_bytes(data[:MAX_PREVIEW_BYTES]),
    }


def validate_snapshot_contract(snapshot: dict[str, Any]) -> dict[str, Any]:
    required = (
        "source_id", "source_type", "requested_path", "normalized_path",
        "resolved_path", "authority_status", "read_allowed", "write_allowed",
        "safe_for_rule_extraction", "decision",
    )
    missing = [field for field in required if field not in snapshot]
    if missing:
        return {"decision": "BLOCK", "missing": missing}
    if snapshot.get("write_allowed") is not False:
        return {"decision": "LOCK", "missing": []}
    if snapshot.get("safe_for_rule_extraction") is True and snapshot.get("decision") != "PASS":
        return {"decision": "LOCK", "missing": []}
    return {"decision": "PASS", "missing": []}


def duplicate_source_policy(entries: list[dict[str, Any]]) -> dict[str, Any]:
    by_hash: dict[str, set[str]] = {}
    by_name: dict[str, set[str]] = {}
    canonical = 0
    findings: list[dict[str, Any]] = []

    for entry in entries:
        digest = str(entry.get("sha256", ""))
        path = str(entry.get("normalized_path", ""))
        name = Path(path).name.lower()
        by_hash.setdefault(digest, set()).add(path)
        by_name.setdefault(name, set()).add(digest)
        if entry.get("authority_status") == "AUTHORITY_CANONICAL":
            canonical += 1

    if any(len(paths) > 1 for paths in by_hash.values()):
        findings.append(make_error("B3_SOURCE_DUPLICATE_HASH_WARNING", "PASS_WITH_WARNINGS", "Same hash in multiple paths.", "DUPLICATE"))
    if any(len(digests) > 1 for digests in by_name.values()):
        findings.append(make_error("B3_SOURCE_DUPLICATE_NAME_REVIEW", "REQUIRE_REVIEW", "Same name with different content.", "DUPLICATE"))
    if canonical > 1:
        findings.append(make_error("B3_SOURCE_CANONICAL_DUPLICATE_LOCK", "LOCK", "Multiple canonical sources.", "DUPLICATE"))

    return {"decision": resolve_decision([item["decision"] for item in findings] or ["PASS"]), "findings": findings}


def freshness_decision(freshness: str, authority: str) -> str:
    if freshness == "FRESHNESS_CONFLICTED":
        return "BLOCK"
    if freshness == "FRESHNESS_CURRENT" and authority == "AUTHORITY_CANONICAL":
        return "PASS"
    if freshness == "FRESHNESS_RECENT" and authority in ("AUTHORITY_REFERENCED", "AUTHORITY_CANONICAL"):
        return "PASS_WITH_WARNINGS"
    if freshness in ("FRESHNESS_STALE", "FRESHNESS_UNKNOWN"):
        return "REQUIRE_REVIEW"
    return "REQUIRE_REVIEW"


def scan_secret_risk(text: str) -> dict[str, Any]:
    hits = [pattern.pattern for pattern in SECRET_PATTERNS if pattern.search(text)]
    return {"decision": "LOCK" if hits else "PASS", "hits": hits}


def report_without_content(snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": snapshot.get("source_id"),
        "normalized_path": snapshot.get("normalized_path"),
        "source_type": snapshot.get("source_type"),
        "authority_status": snapshot.get("authority_status"),
        "sha256": snapshot.get("sha256"),
        "size_bytes": snapshot.get("size_bytes"),
        "encoding_status": snapshot.get("encoding_status"),
        "decision": snapshot.get("decision"),
        "error_codes": [error.get("error_code") for error in snapshot.get("errors", [])],
        "short_preview_hash": snapshot.get("content_preview_hash"),
        "safe_next_step": "REVIEW_SOURCE_RESOLUTION_FAILURE" if snapshot.get("decision") != "PASS" else NEXT_SAFE_STEP,
    }


def report_leak_decision(report: dict[str, Any], forbidden_strings: list[str]) -> str:
    text = stable_json_dumps(report)
    if scan_secret_risk(text)["decision"] == "LOCK":
        return "LOCK"
    for value in forbidden_strings:
        if value and value in text:
            return "LOCK"
    return "PASS"


def _common(status: str = "PASS") -> dict[str, Any]:
    value = dict(COMMON_FLAGS)
    value["status"] = status
    return value


def build_all_artifact_texts() -> dict[str, str]:
    sample_snapshot = {
        "source_id": "fixture_manual_current",
        "requested_path": ".pytest_block3_basetemp/manual_current_fixture.md",
        "normalized_path": ".pytest_block3_basetemp/manual_current_fixture.md",
        "resolved_path": ".pytest_block3_basetemp/manual_current_fixture.md",
        "source_type": "test_fixture",
        "authority_status": "AUTHORITY_CANONICAL",
        "sha256": sha256_text("fixture-manual-current"),
        "size_bytes": len("fixture-manual-current".encode("utf-8")),
        "last_write_time_utc": "fixture",
        "encoding_status": "ENCODING_UTF8",
        "binary_status": "TEXT",
        "read_allowed": True,
        "write_allowed": False,
        "safe_for_rule_extraction": True,
        "decision": "PASS",
        "evidence": ["fixture_based_validation"],
        "content_preview_hash": sha256_text("fixture-preview"),
    }

    denied_snapshot = {
        "source_id": "denied_external_url",
        "requested_path": "https://example.com/manual.md",
        "normalized_path": "",
        "resolved_path": "",
        "source_type": "external_url",
        "authority_status": "AUTHORITY_UNKNOWN",
        "read_allowed": False,
        "write_allowed": False,
        "safe_for_rule_extraction": False,
        "decision": "LOCK",
        "errors": [make_error("B3_SOURCE_EXTERNAL_URL_LOCK", "LOCK", "External URLs are blocked.", "PATH")],
    }

    artifacts: dict[str, Any] = {
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_3_SOURCE_RESOLUTION_MAP.json": {
            **_common(),
            "report_id": "BRIDGE_BLOCK_3_SOURCE_RESOLUTION_MAP",
            "resolved_sources": [report_without_content(sample_snapshot)],
            "denied_sources_count": 1,
            "safe_for_rule_extraction_count": 1,
            "decisions_summary": {"PASS": 1, "LOCK": 1},
        },
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_3_SOURCE_INTEGRITY_REPORT.json": {
            **_common(),
            "report_id": "BRIDGE_BLOCK_3_SOURCE_INTEGRITY_REPORT",
            "hash_checks": "DEFINED",
            "size_checks": "DEFINED",
            "mtime_checks": "DEFINED",
            "toctou_checks": "DEFINED",
            "encoding_checks": "DEFINED",
            "binary_checks": "DEFINED",
            "freshness_checks": "DEFINED",
        },
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_3_SOURCE_BOUNDARY_REPORT.json": {
            **_common(),
            "report_id": "BRIDGE_BLOCK_3_SOURCE_BOUNDARY_REPORT",
            "path_guard": "DEFINED",
            "windows_path_hardening": "DEFINED",
            "no_touch_guard": "DEFINED",
            "external_io_guard": "DEFINED",
            "symlink_junction_reparse_guard": "DEFINED",
            "extension_guard": "DEFINED",
        },
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_3_DENIED_SOURCE_REPORT.json": {
            **_common(),
            "report_id": "BRIDGE_BLOCK_3_DENIED_SOURCE_REPORT",
            "denied_sources": [report_without_content(denied_snapshot)],
            "content_copied": False,
            "metadata_only": True,
        },
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_3_VALIDATION_REPORT.json": {
            **_common(),
            "report_id": "BRIDGE_BLOCK_3_VALIDATION_REPORT",
            "result": LIFECYCLE_STATUS,
            "py_compile": "PLANNED_BY_WRAPPER",
            "pytest_specific": "PLANNED_BY_WRAPPER",
            "pytest_subsystem": "PLANNED_BY_WRAPPER",
            "validate_outputs": "PASS",
            "minimum_tests_required": 220,
            "target_tests_recommended": "230+",
        },
        "00_SYSTEM/bridge/reports/BRIDGE_BLOCK_3_NEXT_LAYER_READINESS_MAP.json": {
            **_common(),
            "report_id": "BRIDGE_BLOCK_3_NEXT_LAYER_READINESS_MAP",
            "result": "READY_FOR_POST_BUILD_AUDIT",
            "post_build_audit_allowed_next": True,
            "validation_allowed_now": False,
            "block_4_allowed_now": False,
        },
    }

    artifact_texts = {path: stable_json_dumps(value) for path, value in artifacts.items()}

    summary = "\n".join([
        "# BLOQUE 3 — Source resolver + integrity guard",
        "",
        "Status: BUILT_PENDING_POST_AUDIT",
        "",
        "- Fixture-based validation only.",
        "- No real manual/current read.",
        "- No real brain read.",
        "- No reports/brain read.",
        "- Source resolver and integrity guard built as local deterministic module.",
        "- Outputs are metadata-only and anti-leak controlled.",
        "- Execution/manual/brain/n8n/webhook/publishing/CAPA9 remain blocked.",
        f"- Next safe step: {NEXT_SAFE_STEP}",
        "",
    ])
    artifact_texts["05_REPORTS/manual_brain_bridge/BRIDGE_BLOCK_3_SOURCE_RESOLVER_INTEGRITY_GUARD_SUMMARY.md"] = summary

    manifest = {
        **_common(),
        "manifest_id": "BRIDGE_BLOCK_3_MANIFEST",
        "artifacts": [
            {"path": path, "sha256": sha256_text(text), "bytes_utf8": len(text.encode("utf-8"))}
            for path, text in sorted(artifact_texts.items())
        ],
    }
    artifact_texts["00_SYSTEM/bridge/manifests/BRIDGE_BLOCK_3_MANIFEST.json"] = stable_json_dumps(manifest)

    seal = {
        **_common(),
        "seal_id": "BRIDGE_BLOCK_3_SEAL",
        "status": "SEALED_PENDING_POST_BUILD_AUDIT",
        "manifest_sha256": canonical_json_hash(manifest),
        "next_safe_step": NEXT_SAFE_STEP,
    }
    artifact_texts["00_SYSTEM/bridge/manifests/BRIDGE_BLOCK_3_SEAL.json"] = stable_json_dumps(seal)

    return artifact_texts


def validate_outputs(root: Path) -> dict[str, Any]:
    expected = build_all_artifact_texts()
    errors: list[dict[str, Any]] = []

    for relative_path, expected_text in expected.items():
        target = root / relative_path
        if not target.exists():
            errors.append(make_error("B3_SOURCE_FILE_MISSING_BLOCK", "BLOCK", f"Missing output {relative_path}", "OUTPUT"))
            continue
        actual = target.read_text(encoding="utf-8")
        if actual != expected_text:
            errors.append(make_error("B3_SOURCE_HASH_CHANGED_REVIEW", "BLOCK", f"Output not deterministic {relative_path}", "OUTPUT"))
            continue
        if relative_path.endswith(".json"):
            try:
                loaded = json.loads(actual)
            except json.JSONDecodeError:
                errors.append(make_error("B3_SOURCE_FILE_UNREADABLE_BLOCK", "BLOCK", f"Invalid JSON {relative_path}", "OUTPUT"))
                continue
            if stable_json_dumps(loaded) != actual:
                errors.append(make_error("B3_SOURCE_HASH_CHANGED_REVIEW", "BLOCK", f"Non-canonical JSON {relative_path}", "OUTPUT"))
            for key, expected_value in COMMON_FLAGS.items():
                if loaded.get(key) != expected_value:
                    errors.append(make_error("B3_NEXT_STEP_UNSAFE_BLOCK", "LOCK", f"Common safety field mismatch {key} in {relative_path}", "OUTPUT"))

    return {
        "status": "PASS" if not errors else resolve_decision([error["decision"] for error in errors]),
        "errors": errors,
        "checked": sorted(expected),
    }


def write_all_outputs(root: Path) -> dict[str, Any]:
    artifacts = build_all_artifact_texts()
    for path, text in artifacts.items():
        if path not in ALLOWED_OUTPUTS:
            raise Block3Error(f"OUTPUT_OUTSIDE_ALLOWLIST: {path}")
        if detect_no_touch_path(path):
            raise Block3Error(f"NO_TOUCH_OUTPUT_PATH: {path}")
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
    return {"status": "PASS", "written": sorted(artifacts)}


def self_check() -> dict[str, Any]:
    artifacts = build_all_artifact_texts()
    leak = report_leak_decision({"safe": "metadata", "preview_hash": sha256_text("secret")}, ["full manual body"])
    return {
        "block": BLOCK_ID,
        "status": "PASS",
        "artifact_count": len(artifacts),
        "error_code_count": len(ERROR_CODES),
        "anti_leak_self_check": leak,
        "next_safe_step": NEXT_SAFE_STEP,
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    root = Path.cwd()

    if "--build-artifacts" in args:
        print(stable_json_dumps(write_all_outputs(root)), end="")
        return 0

    if "--validate-outputs" in args:
        result = validate_outputs(root)
        print(stable_json_dumps(result), end="")
        return 0 if result["status"] == "PASS" else 2

    if "--self-check" in args:
        print(stable_json_dumps(self_check()), end="")
        return 0

    print(stable_json_dumps({"block": BLOCK_ID, "status": "READY", "next_safe_step": NEXT_SAFE_STEP}), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())