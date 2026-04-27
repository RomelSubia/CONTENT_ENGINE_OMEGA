from __future__ import annotations

import argparse
import hashlib
import json
import os
import zipfile
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


def load_baseline_index() -> dict[str, dict[str, Any]]:
    if not BASELINE_PATH.exists():
        return {}
    baseline = read_json(BASELINE_PATH)
    entries = baseline.get("entries", [])
    return {str(entry["path"]): entry for entry in entries if isinstance(entry, dict) and "path" in entry}


def collect_candidates(rules: dict[str, Any]) -> list[Path]:
    excluded_paths = list(rules.get("excluded_paths", []))
    candidates: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relpath = normalize_relpath(path)
        if is_excluded(relpath, excluded_paths):
            continue
        candidates.append(path)
    return sorted(candidates, key=lambda item: normalize_relpath(item))


def build_entries(rules: dict[str, Any], baseline_index: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    max_hash_size = int(rules.get("max_hash_size_bytes", MAX_HASH_SIZE_DEFAULT))
    candidates = collect_candidates(rules)
    entries: list[dict[str, Any]] = []
    metrics = {
        "hashed_files": 0,
        "reused_hashes": 0,
        "skipped_oversize": 0,
    }
    for path in candidates:
        relpath = normalize_relpath(path)
        stat = path.stat()
        size = stat.st_size
        modified_time = int(stat.st_mtime_ns)
        baseline_entry = baseline_index.get(relpath)
        if size <= max_hash_size:
            reusable = (
                baseline_entry is not None
                and int(baseline_entry.get("size", -1)) == size
                and int(baseline_entry.get("modified_time", -2)) == modified_time
                and baseline_entry.get("sha256") is not None
            )
            if reusable:
                hash_status = "REUSED"
                sha256 = baseline_entry.get("sha256")
                metrics["reused_hashes"] += 1
            else:
                hash_status = "HASHED"
                sha256 = hash_file_streaming(path)
                metrics["hashed_files"] += 1
        else:
            hash_status = "SKIPPED_OVERSIZE"
            sha256 = None
            metrics["skipped_oversize"] += 1
        entries.append(
            {
                "path": relpath,
                "size": size,
                "modified_time": modified_time,
                "hash_status": hash_status,
                "sha256": sha256,
            }
        )
    return entries, metrics


def build_snapshot(role: str, rules: dict[str, Any]) -> dict[str, Any]:
    baseline_index = load_baseline_index()
    entries, metrics = build_entries(rules, baseline_index)
    total_bytes = sum(int(item["size"]) for item in entries)
    canonical_hash_entries = [
        {
            "path": item["path"],
            "size": item["size"],
            "modified_time": item["modified_time"],
            "sha256": item["sha256"],
        }
        for item in entries
    ]
    canonical_entries = json.dumps(canonical_hash_entries, sort_keys=True, separators=(",", ":"))
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
        "hash_metrics": metrics,
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
    existing = read_json(MANIFEST_PATH) if MANIFEST_PATH.exists() else {}
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
        "archived_snapshots": existing.get("archived_snapshots", []),
    }
    write_json_atomic(MANIFEST_PATH, manifest)


def archive_snapshot_copies(current_snapshot_id: str) -> None:
    archive_dir = SNAPSHOT_DIR / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    manifest = read_json(MANIFEST_PATH) if MANIFEST_PATH.exists() else {"archived_snapshots": []}
    archived_snapshots = list(manifest.get("archived_snapshots", []))
    known_archives = {item.get("snapshot_id"): item for item in archived_snapshots if isinstance(item, dict)}

    for snapshot_path in sorted(SNAPSHOT_DIR.glob("*.json")):
        if snapshot_path.stem == current_snapshot_id:
            continue
        archive_zip = archive_dir / f"{snapshot_path.stem}.zip"
        if not archive_zip.exists():
            with zipfile.ZipFile(archive_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as archive_handle:
                archive_handle.write(snapshot_path, arcname=snapshot_path.name)
            try:
                with zipfile.ZipFile(archive_zip, mode="r") as archive_handle:
                    if snapshot_path.name not in archive_handle.namelist():
                        fail(f"Archive validation failed: {archive_zip}")
                    archived_content = archive_handle.read(snapshot_path.name).decode("utf-8")
                original_content = snapshot_path.read_text(encoding="utf-8")
                if archived_content != original_content:
                    fail(f"Archive content mismatch: {archive_zip}")
            except Exception as exc:
                fail(f"Archive validation failed: {archive_zip} :: {exc}")

        known_archives[snapshot_path.stem] = {
            "snapshot_id": snapshot_path.stem,
            "json_file": f"00_SYSTEM/core/change_awareness/snapshots/{snapshot_path.name}",
            "zip_file": f"00_SYSTEM/core/change_awareness/snapshots/archive/{archive_zip.name}",
            "zip_validated": True,
            "original_preserved": True,
        }

    manifest["archived_snapshots"] = sorted(known_archives.values(), key=lambda item: item["snapshot_id"])
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
        archive_snapshot_copies(snapshot["snapshot_id"])
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
