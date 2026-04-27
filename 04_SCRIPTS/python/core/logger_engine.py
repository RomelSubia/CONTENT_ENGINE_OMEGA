from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from state_manager import read_json, write_json_atomic


ROOT = Path(r"D:\CONTENT_ENGINE_OMEGA")
LOG_PATH = ROOT / "00_SYSTEM" / "core" / "logs" / "RUNTIME_LOG.json"
ARCHIVE_DIR = ROOT / "00_SYSTEM" / "core" / "logs" / "archive"
MANIFEST_PATH = ROOT / "00_SYSTEM" / "core" / "logs" / "manifest.json"
MAX_LOG_SIZE_BYTES = 5 * 1024 * 1024


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_events() -> list[dict[str, Any]]:
    if not LOG_PATH.exists():
        return []
    payload = read_json(LOG_PATH)
    if not isinstance(payload, list):
        raise RuntimeError("RUNTIME_LOG.json must contain a list")
    return payload


def _load_manifest() -> dict[str, Any]:
    payload = read_json(MANIFEST_PATH)
    if not isinstance(payload, dict):
        raise RuntimeError("manifest.json must contain an object")
    payload.setdefault("archived_files", [])
    payload.setdefault("max_files", 10)
    return payload


def rotate_logs_if_needed() -> None:
    if not LOG_PATH.exists() or LOG_PATH.stat().st_size <= MAX_LOG_SIZE_BYTES:
        return

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    manifest = _load_manifest()
    archive_name = f"RUNTIME_LOG_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    archive_path = ARCHIVE_DIR / archive_name
    LOG_PATH.replace(archive_path)

    archived_files = manifest.get("archived_files", [])
    archived_files.append(str(archive_path.relative_to(ROOT)).replace("\\", "/"))
    manifest["archived_files"] = archived_files[-int(manifest.get("max_files", 10)) :]
    write_json_atomic(MANIFEST_PATH, manifest)
    write_json_atomic(LOG_PATH, [])


def append_event(event: dict[str, Any]) -> dict[str, Any]:
    rotate_logs_if_needed()

    normalized = {
        "timestamp": event.get("timestamp", _utc_now()),
        "type": event["type"],
        "phase": event["phase"],
        "message": event["message"],
        "state_before": event.get("state_before"),
        "state_after": event.get("state_after"),
        "evidence": event.get("evidence", {}),
    }

    events = _load_events()
    events.append(normalized)
    write_json_atomic(LOG_PATH, events)
    return normalized
