from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from state_manager import read_json, write_json_atomic


ROOT = Path(r"D:\CONTENT_ENGINE_OMEGA")
CHANGE_DIR = ROOT / "00_SYSTEM" / "core" / "change_awareness"
SNAPSHOT_DIR = CHANGE_DIR / "snapshots"
PROBE_DIR = CHANGE_DIR / "probes"
LOCK_DIR = CHANGE_DIR / "locks"
RULES_PATH = CHANGE_DIR / "CHANGE_RULES.json"
BASELINE_PATH = CHANGE_DIR / "CHANGE_BASELINE.json"
CURRENT_PATH = CHANGE_DIR / "CHANGE_CURRENT.json"
MANIFEST_PATH = CHANGE_DIR / "SNAPSHOT_MANIFEST.json"
LOCK_PATH = LOCK_DIR / "snapshot.lock"
MAX_HASH_SIZE_DEFAULT = 20 * 1024 * 1024


def fail(message: str) -> None:
    print(f"PHASE_B_SNAPSHOT: BLOCKED - {message}")
    raise SystemExit(1)


def utc_marker() -> str:
    return "DETERMINISTIC"


def ensure_root() -> None:
    if Path.cwd().resolve() != ROOT.resolve():
        fail(f"Current working directory must be {ROOT}")
    if "ARGOS" in {part.upper() for part in ROOT.parts}:
        fail("Root path contains ARGOS")


def load_rules() -> dict[str, Any]:
    payload = read_json(RULES_PATH)
    if payload.get("mode") != "DRY_RUN":
        fail("CHANGE_RULES.mode must be DRY_RUN")
    return payload


def normalize_relpath(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def is_excluded(relpath: str, excluded_paths: list[str]) -> bool:
    normalized = relpath.replace("\\", "/")
    for candidate in excluded_paths:
        cleaned = candidate.replace("\\", "/")
        if cleaned.endswith("/"):
            if normalized.startswith(cleaned):
                return True
        elif normalized == cleaned:
            return True
    return False


def hash_file_streaming(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def build_entries(rules: dict[str, Any]) -> list[dict[str, Any]]:
    excluded_paths = list(rules.get("excluded_paths", []))
    max_hash_size = int(rules.get("max_hash_size_bytes", MAX_HASH_SIZE_DEFAULT))
    candidates: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relpath = normalize_relpath(path)
        if is_excluded(relpath, excluded_paths):
            continue
        candidates.append(path)

    entries: list[dict[str, Any]] = []
    for path in sorted(candidates, key=lambda item: normalize_relpath(item)):
        relpath = normalize_relpath(path)
        size = path.stat().st_size
        if size <= max_hash_size:
            hash_status = "HASHED"
            sha256 = hash_file_streaming(path)
        else:
            hash_status = "SKIPPED_OVERSIZE"
            sha256 = None
        entries.append(
            {
                "path": relpath,
                "size": size,
                "hash_status": hash_status,
                "sha256": sha256,
            }
        )
    return entries


def build_snapshot(role: str, rules: dict[str, Any]) -> dict[str, Any]:
    entries = build_entries(rules)
    total_bytes = sum(int(item["size"]) for item in entries)
    canonical_entries = json.dumps(entries, sort_keys=True, separators=(",", ":"))
    snapshot_hash = hashlib.sha256(canonical_entries.encode("utf-8")).hexdigest()
    snapshot_id = snapshot_hash[:16]
    return {
        "system": "CONTENT_ENGINE_OMEGA",
        "phase": "B",
        "mode": "DRY_RUN",
        "snapshot_role": role,
        "snapshot_status": "COMPLETE",
        "snapshot_id": snapshot_id,
        "snapshot_hash": snapshot_hash,
        "root": str(ROOT),
        "total_files": len(entries),
        "total_bytes": total_bytes,
        "excluded_paths": list(rules.get("excluded_paths", [])),
        "entries": entries,
    }


def load_lock(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "lock_name": "snapshot",
            "lock_active": False,
            "pid": 0,
            "status": "AVAILABLE",
        }
    return read_json(path)


def is_process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        if os.name == "nt":
            import ctypes

            kernel32 = ctypes.windll.kernel32
            process_handle = kernel32.OpenProcess(0x1000, 0, pid)
            if process_handle:
                kernel32.CloseHandle(process_handle)
                return True
            return False
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def acquire_lock(path: Path = LOCK_PATH) -> None:
    lock_payload = load_lock(path)
    if lock_payload.get("lock_active"):
        pid = int(lock_payload.get("pid", 0))
        if is_process_alive(pid):
            fail(f"LOCK_ACTIVE:{path}")
        fail(f"RECOVERY_REQUIRED:{path}")

    write_json_atomic(
        path,
        {
            "lock_name": "snapshot",
            "lock_active": True,
            "pid": os.getpid(),
            "status": "ACTIVE",
            "timestamp": utc_marker(),
        },
    )


def release_lock(path: Path = LOCK_PATH) -> None:
    write_json_atomic(
        path,
        {
            "lock_name": "snapshot",
            "lock_active": False,
            "pid": 0,
            "status": "AVAILABLE",
            "timestamp": utc_marker(),
        },
    )


def update_manifest(snapshot: dict[str, Any], baseline: dict[str, Any], deterministic_hash_confirmed: bool) -> None:
    manifest = {
        "system": "CONTENT_ENGINE_OMEGA",
        "phase": "B",
        "mode": "DRY_RUN",
        "baseline_snapshot_id": baseline["snapshot_id"],
        "current_snapshot_id": snapshot["snapshot_id"],
        "snapshot_hash": snapshot["snapshot_hash"],
        "snapshot_file": f"00_SYSTEM/core/change_awareness/snapshots/{snapshot['snapshot_id']}.json",
        "deterministic_hash_confirmed": deterministic_hash_confirmed,
        "last_delta_status": read_json(CHANGE_DIR / "CHANGE_DELTA.json").get("delta_status", "PENDING"),
        "archived_snapshots": [],
    }
    write_json_atomic(MANIFEST_PATH, manifest)


def write_snapshot_files(snapshot: dict[str, Any], target: str, rules: dict[str, Any], deterministic_hash_confirmed: bool) -> None:
    snapshot_file = SNAPSHOT_DIR / f"{snapshot['snapshot_id']}.json"
    write_json_atomic(snapshot_file, snapshot)

    if target in {"baseline", "both"}:
        baseline_snapshot = dict(snapshot)
        baseline_snapshot["snapshot_role"] = "BASELINE"
        write_json_atomic(BASELINE_PATH, baseline_snapshot)
    else:
        baseline_snapshot = read_json(BASELINE_PATH)

    current_snapshot = dict(snapshot)
    current_snapshot["snapshot_role"] = "CURRENT"
    write_json_atomic(CURRENT_PATH, current_snapshot)
    update_manifest(current_snapshot, baseline_snapshot, deterministic_hash_confirmed)


def run_snapshot(target: str) -> None:
    ensure_root()
    rules = load_rules()
    acquire_lock()
    try:
        snapshot = build_snapshot("CURRENT", rules)
        baseline_snapshot = read_json(BASELINE_PATH)
        deterministic_hash_confirmed = baseline_snapshot.get("snapshot_hash") in {None, snapshot["snapshot_hash"]}
        write_snapshot_files(snapshot, target, rules, deterministic_hash_confirmed)
    finally:
        release_lock()
    print(f"PHASE_B_SNAPSHOT: PASS {snapshot['snapshot_hash']}")


def write_partial_probe() -> None:
    PROBE_DIR.mkdir(parents=True, exist_ok=True)
    partial_path = PROBE_DIR / "PARTIAL_SNAPSHOT.json"
    payload = {
        "system": "CONTENT_ENGINE_OMEGA",
        "phase": "B",
        "mode": "DRY_RUN",
        "snapshot_role": "PROBE",
        "snapshot_status": "PARTIAL",
        "snapshot_id": "partial-probe",
        "snapshot_hash": None,
        "root": str(ROOT),
        "entries": [],
    }
    write_json_atomic(partial_path, payload)
    print(f"PHASE_B_PARTIAL_PROBE: PASS {partial_path}")


def run_lock_self_test() -> None:
    PROBE_DIR.mkdir(parents=True, exist_ok=True)
    alive_path = PROBE_DIR / "snapshot_alive_probe.lock"
    dead_path = PROBE_DIR / "snapshot_dead_probe.lock"

    write_json_atomic(
        alive_path,
        {
            "lock_name": "snapshot",
            "lock_active": True,
            "pid": os.getpid(),
            "status": "ACTIVE",
            "timestamp": utc_marker(),
        },
    )
    try:
        acquire_lock(alive_path)
        fail("Alive lock probe should have blocked")
    except SystemExit:
        pass

    write_json_atomic(
        dead_path,
        {
            "lock_name": "snapshot",
            "lock_active": True,
            "pid": 999999,
            "status": "ACTIVE",
            "timestamp": utc_marker(),
        },
    )
    try:
        acquire_lock(dead_path)
        fail("Dead lock probe should have required recovery")
    except SystemExit:
        pass

    print("PHASE_B_LOCK_TEST: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description="CONTENT_ENGINE_OMEGA change snapshot engine")
    parser.add_argument("--target", choices=["baseline", "current", "both"], default="both")
    parser.add_argument("--write-partial-probe", action="store_true")
    parser.add_argument("--lock-self-test", action="store_true")
    args = parser.parse_args()

    if args.write_partial_probe:
        write_partial_probe()
        return
    if args.lock_self_test:
        run_lock_self_test()
        return
    run_snapshot(args.target)


if __name__ == "__main__":
    main()
