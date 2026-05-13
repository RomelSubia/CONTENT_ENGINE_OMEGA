from __future__ import annotations

from typing import Any

ALLOWED_ROOTS = [
    "00_SYSTEM/content_engine/contracts",
    "00_SYSTEM/content_engine/reports",
    "00_SYSTEM/content_engine/manifests",
    "04_SCRIPTS/python/content_engine",
    "tests/content_engine",
    "05_REPORTS/content_engine",
]

PROTECTED_ROOTS = [
    "00_SYSTEM/brain",
    "00_SYSTEM/reports/brain",
    "00_SYSTEM/manual/current",
    "00_SYSTEM/manual/historical",
    "00_SYSTEM/manual/manifest",
    "00_SYSTEM/manual/registry",
    "n8n",
    "workflows",
    "publication",
    "09_PUBLICATION",
    "14_EXPORTS",
    "13_BACKUPS",
    "12_LOGS/runtime",
]


def normalize(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def is_allowed_output(path: str) -> bool:
    norm = normalize(path)
    return any(norm == root or norm.startswith(root + "/") for root in ALLOWED_ROOTS)


def is_protected_output(path: str) -> bool:
    norm = normalize(path)
    return any(norm == root or norm.startswith(root + "/") for root in PROTECTED_ROOTS)


def detect_scope_violations(paths: list[str]) -> dict[str, Any]:
    out_of_scope = [path for path in paths if not is_allowed_output(path)]
    protected = [path for path in paths if is_protected_output(path)]
    return {
        "status": "PASS" if not out_of_scope and not protected else "BLOCK",
        "out_of_scope": out_of_scope,
        "protected": protected,
    }


def build_boundary_plan() -> dict[str, Any]:
    return {
        "status": "PASS",
        "allowed_roots": list(ALLOWED_ROOTS),
        "protected_roots": list(PROTECTED_ROOTS),
        "git_add_dot_allowed": False,
        "commit_out_of_scope_allowed": False,
    }
