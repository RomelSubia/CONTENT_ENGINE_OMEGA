from __future__ import annotations

import json
from pathlib import Path
import zipfile


ROOT = Path(r"D:\CONTENT_ENGINE_OMEGA")
CHANGE_DIR = ROOT / "00_SYSTEM" / "core" / "change_awareness"

REQUIRED_JSON = [
    CHANGE_DIR / "CHANGE_RULES.json",
    CHANGE_DIR / "CHANGE_BASELINE.json",
    CHANGE_DIR / "CHANGE_CURRENT.json",
    CHANGE_DIR / "CHANGE_DELTA.json",
    CHANGE_DIR / "SNAPSHOT_MANIFEST.json",
]

REQUIRED_SCRIPTS = [
    ROOT / "04_SCRIPTS" / "python" / "core" / "change_snapshot.py",
    ROOT / "04_SCRIPTS" / "python" / "core" / "change_detector.py",
    ROOT / "04_SCRIPTS" / "python" / "core" / "validate_phase_b.py",
    ROOT / "04_SCRIPTS" / "powershell" / "Run-ChangeAwareness.ps1",
    ROOT / "04_SCRIPTS" / "powershell" / "Validate-PhaseB.ps1",
]


def fail(message: str) -> None:
    print(f"PHASE_B_VALIDATION: FAIL - {message}")
    raise SystemExit(1)


def load_json(path: Path):
    if not path.exists():
        fail(f"Missing required file: {path}")
    if path.stat().st_size == 0:
        fail(f"Empty JSON file: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {path}: {exc}")


def main() -> None:
    if Path.cwd().resolve() != ROOT.resolve():
        fail(f"Current working directory must be {ROOT}")
    if "ARGOS" in {part.upper() for part in ROOT.parts}:
        fail("Root path contains ARGOS")

    payloads = {str(path): load_json(path) for path in REQUIRED_JSON}
    rules = payloads[str(CHANGE_DIR / "CHANGE_RULES.json")]
    baseline = payloads[str(CHANGE_DIR / "CHANGE_BASELINE.json")]
    current = payloads[str(CHANGE_DIR / "CHANGE_CURRENT.json")]
    delta = payloads[str(CHANGE_DIR / "CHANGE_DELTA.json")]
    manifest = payloads[str(CHANGE_DIR / "SNAPSHOT_MANIFEST.json")]

    if rules.get("mode") != "DRY_RUN":
        fail("CHANGE_RULES.mode must be DRY_RUN")
    if rules.get("debug_mode") not in {True, False}:
        fail("CHANGE_RULES.debug_mode must be boolean")
    if rules.get("no_delete") is not True or rules.get("no_move") is not True:
        fail("CHANGE_RULES must enforce no_delete and no_move")
    if "D:\\ARGOS" not in [str(item).upper() for item in rules.get("excluded_paths", []) if "ARGOS" in str(item).upper()] and "ARGOS" in json.dumps(rules):
        pass
    if current.get("mode") != "DRY_RUN" or baseline.get("mode") != "DRY_RUN":
        fail("Snapshots must remain in DRY_RUN mode")
    if current.get("snapshot_status") != "COMPLETE":
        fail("CHANGE_CURRENT.snapshot_status must be COMPLETE")
    if baseline.get("snapshot_status") != "COMPLETE":
        fail("CHANGE_BASELINE.snapshot_status must be COMPLETE")
    if "hash_metrics" not in current or "hash_metrics" not in baseline:
        fail("Snapshots must include hash_metrics")
    if not current.get("snapshot_hash") or not manifest.get("snapshot_hash"):
        fail("Snapshot hash is missing")
    if current.get("snapshot_hash") != manifest.get("snapshot_hash"):
        fail("Manifest snapshot hash does not match current snapshot")
    if delta.get("risk_score") not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
        fail("Delta risk_score is invalid")
    if not isinstance(delta.get("folder_index"), dict):
        fail("Delta folder_index must be an object")
    for key in ["new_paths", "modified_paths", "deleted_paths", "git_status", "snapshot_conflicts"]:
        if delta.get(key) != sorted(delta.get(key, [])):
            fail(f"Delta array must be sorted: {key}")

    archive_entries = manifest.get("archived_snapshots", [])
    if not isinstance(archive_entries, list):
        fail("Manifest archived_snapshots must be a list")
    for archive_entry in archive_entries:
        zip_path = ROOT / archive_entry["zip_file"]
        if not zip_path.exists():
            fail(f"Archived snapshot zip is missing: {zip_path}")
        try:
            with zipfile.ZipFile(zip_path, mode="r") as archive_handle:
                if archive_handle.testzip() is not None:
                    fail(f"Archived snapshot zip is corrupt: {zip_path}")
        except zipfile.BadZipFile as exc:
            fail(f"Archived snapshot zip is invalid: {zip_path} :: {exc}")

    for script_path in REQUIRED_SCRIPTS:
        if not script_path.exists():
            fail(f"Missing required script: {script_path}")

    for path in ROOT.rglob("*"):
        if "ARGOS" in {part.upper() for part in path.parts}:
            fail(f"ARGOS path detected inside root: {path}")

    print("PHASE_B_VALIDATION: PASS")


if __name__ == "__main__":
    main()
