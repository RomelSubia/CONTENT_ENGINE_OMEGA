from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Any

from state_manager import read_json, write_json_atomic


ROOT = Path(r"D:\CONTENT_ENGINE_OMEGA")
CHANGE_DIR = ROOT / "00_SYSTEM" / "core" / "change_awareness"
BASELINE_PATH = CHANGE_DIR / "CHANGE_BASELINE.json"
CURRENT_PATH = CHANGE_DIR / "CHANGE_CURRENT.json"
DELTA_PATH = CHANGE_DIR / "CHANGE_DELTA.json"
MANIFEST_PATH = CHANGE_DIR / "SNAPSHOT_MANIFEST.json"


def fail(message: str) -> None:
    print(f"PHASE_B_DELTA: BLOCKED - {message}")
    raise SystemExit(1)


def load_snapshot(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    if payload.get("snapshot_status") != "COMPLETE":
        fail(f"Snapshot is not complete: {path}")
    if payload.get("mode") != "DRY_RUN":
        fail(f"Snapshot mode must be DRY_RUN: {path}")
    return payload


def normalize_entries(entries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    normalized = {}
    for entry in entries:
        normalized[str(entry["path"])] = {
            "size": int(entry["size"]),
            "modified_time": int(entry.get("modified_time", 0)),
            "sha256": entry.get("sha256"),
        }
    return normalized


def get_git_status() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        fail("git status --short failed")
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return sorted(lines)


def build_folder_index(new_paths: list[str], modified_paths: list[str], deleted_paths: list[str]) -> dict[str, dict[str, int]]:
    folder_index: dict[str, dict[str, int]] = {}

    def increment(paths: list[str], key: str) -> None:
        for item in paths:
            folder = str(Path(item).parent).replace("\\", "/")
            if folder == ".":
                folder = "."
            folder_index.setdefault(folder, {"new": 0, "modified": 0, "deleted": 0})
            folder_index[folder][key] += 1

    increment(new_paths, "new")
    increment(modified_paths, "modified")
    increment(deleted_paths, "deleted")
    return dict(sorted(folder_index.items(), key=lambda item: item[0]))


def calculate_risk_score(paths: list[str]) -> str:
    if any("ARGOS" in path.upper() for path in paths):
        return "CRITICAL"
    if any(path.startswith("00_SYSTEM/core/") for path in paths):
        return "HIGH"
    if any(path.startswith("04_SCRIPTS/") for path in paths):
        return "MEDIUM"
    if any("/logs/" in path or "/reports/" in path or path.startswith("00_SYSTEM/core/logs/") or path.startswith("00_SYSTEM/core/reports/") for path in paths):
        return "LOW"
    return "LOW"


def build_delta(baseline: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    baseline_entries = normalize_entries(baseline.get("entries", []))
    current_entries = normalize_entries(current.get("entries", []))

    baseline_paths = set(baseline_entries)
    current_paths = set(current_entries)

    new_paths = sorted(current_paths - baseline_paths)
    deleted_paths = sorted(baseline_paths - current_paths)
    modified_paths = sorted(
        path
        for path in baseline_paths & current_paths
        if baseline_entries[path] != current_entries[path]
    )

    git_status = get_git_status()
    git_conflicts = sorted(line for line in git_status if "00_SYSTEM/core/change_awareness/" not in line.replace("\\", "/"))

    snapshot_conflicts = []
    for path in new_paths:
        snapshot_conflicts.append(f"SNAPSHOT_NEW:{path}")
    for path in modified_paths:
        snapshot_conflicts.append(f"SNAPSHOT_MODIFIED:{path}")
    for path in deleted_paths:
        snapshot_conflicts.append(f"SNAPSHOT_DELETED:{path}")

    if new_paths or modified_paths or deleted_paths:
        delta_status = "CHANGES_DETECTED"
    else:
        delta_status = "NO_CHANGES"

    changed_paths = sorted(set(new_paths + modified_paths + deleted_paths))

    return {
        "system": "CONTENT_ENGINE_OMEGA",
        "phase": "B",
        "mode": "DRY_RUN",
        "delta_status": delta_status,
        "baseline_snapshot_id": baseline["snapshot_id"],
        "current_snapshot_id": current["snapshot_id"],
        "summary": {
            "new": len(new_paths),
            "modified": len(modified_paths),
            "deleted": len(deleted_paths),
            "git_conflicts": len(git_conflicts),
        },
        "folder_index": build_folder_index(new_paths, modified_paths, deleted_paths),
        "risk_score": calculate_risk_score(changed_paths),
        "new_paths": new_paths,
        "modified_paths": modified_paths,
        "deleted_paths": deleted_paths,
        "git_status": git_status,
        "snapshot_conflicts": sorted(snapshot_conflicts),
    }


def update_manifest(delta: dict[str, Any], current: dict[str, Any], baseline: dict[str, Any]) -> None:
    manifest = read_json(MANIFEST_PATH)
    manifest["baseline_snapshot_id"] = baseline["snapshot_id"]
    manifest["current_snapshot_id"] = current["snapshot_id"]
    manifest["snapshot_hash"] = current["snapshot_hash"]
    manifest["snapshot_file"] = f"00_SYSTEM/core/change_awareness/snapshots/{current['snapshot_id']}.json"
    manifest["last_delta_status"] = delta["delta_status"]
    write_json_atomic(MANIFEST_PATH, manifest)


def main() -> None:
    parser = argparse.ArgumentParser(description="CONTENT_ENGINE_OMEGA delta engine")
    parser.add_argument("--baseline-path", default=str(BASELINE_PATH))
    parser.add_argument("--current-path", default=str(CURRENT_PATH))
    parser.add_argument("--output-path", default=str(DELTA_PATH))
    args = parser.parse_args()

    baseline = load_snapshot(Path(args.baseline_path))
    current = load_snapshot(Path(args.current_path))
    delta = build_delta(baseline, current)
    write_json_atomic(Path(args.output_path), delta)

    if Path(args.output_path).resolve() == DELTA_PATH.resolve():
        update_manifest(delta, current, baseline)

    print(f"PHASE_B_DELTA: PASS {delta['delta_status']}")


if __name__ == "__main__":
    main()
