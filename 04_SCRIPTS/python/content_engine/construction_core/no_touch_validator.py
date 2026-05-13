from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint_tree(root: Path) -> str:
    if not root.exists():
        return "MISSING"
    files = sorted(path for path in root.rglob("*") if path.is_file())
    if not files:
        return "EMPTY"
    material = []
    for path in files:
        material.append(f"{path.relative_to(root).as_posix()}::{sha256_file(path)}")
    return hashlib.sha256(("\n".join(material) + "\n").encode("utf-8")).hexdigest()


def compare_fingerprints(before: dict[str, str], after: dict[str, str]) -> dict[str, Any]:
    changed = {
        key: {"before": before.get(key), "after": after.get(key)}
        for key in sorted(set(before) | set(after))
        if before.get(key) != after.get(key)
    }
    return {"status": "PASS" if not changed else "BLOCK", "changed": changed}
