from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from logger_engine import append_event
from state_manager import read_json, write_json_atomic


ROOT = Path(r"D:\CONTENT_ENGINE_OMEGA")
RUNTIME_DIR = ROOT / "00_SYSTEM" / "core" / "runtime"
SYSTEM_RUNTIME_PATH = RUNTIME_DIR / "SYSTEM_RUNTIME.json"
EXECUTION_CONTEXT_PATH = RUNTIME_DIR / "EXECUTION_CONTEXT.json"
HEARTBEAT_PATH = RUNTIME_DIR / "HEARTBEAT.json"
LOCK_PATH = RUNTIME_DIR / "runtime.lock"
MAX_RUNTIME_SECONDS = 60
ALLOWED_STATES = ["IDLE", "STARTING", "VALIDATING", "RUNNING", "STOPPED"]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fail(message: str, exit_code: int = 1) -> None:
    print(f"PHASE_A_SELF_TEST: BLOCKED - {message}")
    raise SystemExit(exit_code)


def ensure_root() -> None:
    if Path.cwd().resolve() != ROOT.resolve():
        fail(f"Current working directory must be {ROOT}")
    if "ARGOS" in {part.upper() for part in ROOT.parts}:
        fail("Root path contains ARGOS")


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


def acquire_lock() -> None:
    if LOCK_PATH.exists():
        lock_data = read_json(LOCK_PATH)
        pid = int(lock_data.get("pid", 0))
        if is_process_alive(pid):
            fail(f"runtime.lock is active for pid {pid}")
        fail("runtime.lock exists for a dead process; recovery required")

    lock_data = {
        "timestamp": utc_now(),
        "pid": os.getpid(),
    }
    write_json_atomic(LOCK_PATH, lock_data)


def release_lock() -> None:
    if LOCK_PATH.exists():
        LOCK_PATH.unlink()


def load_runtime() -> dict[str, Any]:
    payload = read_json(SYSTEM_RUNTIME_PATH)
    if payload.get("mode") != "DRY_RUN":
        fail("SYSTEM_RUNTIME.mode must remain DRY_RUN")
    if payload.get("current_phase") != "A":
        fail('SYSTEM_RUNTIME.current_phase must be "A"')
    return payload


def load_context() -> dict[str, Any]:
    payload = read_json(EXECUTION_CONTEXT_PATH)
    if payload.get("execution_mode") != "DRY_RUN":
        fail("EXECUTION_CONTEXT.execution_mode must remain DRY_RUN")
    blocked = [str(item).upper() for item in payload.get("blocked_scopes", [])]
    if "D:\\ARGOS" not in blocked:
        fail("ARGOS block scope is missing")
    return payload


def load_heartbeat() -> dict[str, Any]:
    return read_json(HEARTBEAT_PATH)


def persist_runtime(runtime: dict[str, Any]) -> None:
    write_json_atomic(SYSTEM_RUNTIME_PATH, runtime)


def persist_heartbeat(heartbeat: dict[str, Any]) -> None:
    write_json_atomic(HEARTBEAT_PATH, heartbeat)


def transition(runtime: dict[str, Any], new_state: str, message: str, evidence: dict[str, Any]) -> dict[str, Any]:
    if new_state not in ALLOWED_STATES:
        fail(f"Invalid runtime state: {new_state}")
    previous_state = runtime.get("runtime_status")
    runtime["runtime_status"] = new_state
    runtime["last_transition"] = utc_now()
    runtime["lock_active"] = LOCK_PATH.exists()
    if new_state == "STARTING":
        runtime["last_start"] = runtime["last_transition"]
    if new_state == "STOPPED":
        runtime["last_stop"] = runtime["last_transition"]
    append_event(
        {
            "type": "STATE_TRANSITION",
            "phase": "A",
            "message": message,
            "state_before": previous_state,
            "state_after": new_state,
            "evidence": evidence,
        }
    )
    persist_runtime(runtime)
    return runtime


def update_heartbeat(heartbeat: dict[str, Any], status: str, start_monotonic: float) -> dict[str, Any]:
    heartbeat["status"] = status
    heartbeat["timestamp"] = utc_now()
    heartbeat["sequence"] = int(heartbeat.get("sequence", 0)) + 1
    heartbeat["uptime_seconds"] = int(time.monotonic() - start_monotonic)
    persist_heartbeat(heartbeat)
    return heartbeat


def run_self_test() -> None:
    ensure_root()
    runtime = load_runtime()
    context = load_context()
    heartbeat = load_heartbeat()
    start_monotonic = time.monotonic()

    if time.monotonic() - start_monotonic > MAX_RUNTIME_SECONDS:
        fail("Runtime timeout exceeded before execution")

    runtime["active_task"] = "PHASE_A_SELF_TEST"
    runtime["last_result"] = None
    persist_runtime(runtime)

    acquire_lock()
    runtime["lock_active"] = True
    persist_runtime(runtime)

    try:
        runtime = transition(
            runtime,
            "STARTING",
            "Runtime engine acquired the lock",
            {"lock_path": str(LOCK_PATH), "mode": runtime.get("mode")},
        )
        runtime = transition(
            runtime,
            "VALIDATING",
            "Runtime engine started validation",
            {"execution_mode": context.get("execution_mode"), "requires_evidence": context.get("requires_evidence")},
        )

        heartbeat = update_heartbeat(heartbeat, "VALIDATING", start_monotonic)
        runtime["last_heartbeat"] = heartbeat["timestamp"]
        persist_runtime(runtime)

        runtime_roundtrip = read_json(SYSTEM_RUNTIME_PATH)
        heartbeat_roundtrip = read_json(HEARTBEAT_PATH)
        if runtime_roundtrip.get("runtime_status") != runtime.get("runtime_status"):
            fail("Runtime state round-trip validation failed")
        if heartbeat_roundtrip.get("sequence") != heartbeat.get("sequence"):
            fail("Heartbeat round-trip validation failed")

        append_event(
            {
                "type": "SELF_TEST",
                "phase": "A",
                "message": "Self-test validated atomic JSON writes, logger, and heartbeat",
                "state_before": "VALIDATING",
                "state_after": "VALIDATING",
                "evidence": {
                    "runtime_path": str(SYSTEM_RUNTIME_PATH),
                    "heartbeat_path": str(HEARTBEAT_PATH),
                    "heartbeat_sequence": heartbeat["sequence"],
                },
            }
        )

        runtime = transition(
            runtime,
            "RUNNING",
            "Runtime engine entered DRY_RUN execution",
            {"max_runtime_seconds": MAX_RUNTIME_SECONDS, "active_task": runtime.get("active_task")},
        )
        heartbeat = update_heartbeat(heartbeat, "RUNNING", start_monotonic)
        runtime["last_heartbeat"] = heartbeat["timestamp"]
        runtime["last_result"] = "PASS"
        persist_runtime(runtime)

        runtime = transition(
            runtime,
            "STOPPED",
            "Runtime engine finished DRY_RUN execution",
            {"result": "PASS", "sequence": heartbeat["sequence"]},
        )
        heartbeat = update_heartbeat(heartbeat, "STOPPED", start_monotonic)
        runtime["last_heartbeat"] = heartbeat["timestamp"]
        runtime["active_task"] = None
        runtime["last_result"] = "PASS"
        persist_runtime(runtime)
    finally:
        release_lock()
        runtime = load_runtime()
        runtime["lock_active"] = False
        persist_runtime(runtime)

    print("PHASE_A_SELF_TEST: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description="CONTENT_ENGINE_OMEGA runtime engine")
    parser.add_argument("--self-test", action="store_true", help="Run the dry-run self-test")
    args = parser.parse_args()

    if not args.self_test:
        fail("Only --self-test is allowed in DRY_RUN mode")

    run_self_test()


if __name__ == "__main__":
    main()
