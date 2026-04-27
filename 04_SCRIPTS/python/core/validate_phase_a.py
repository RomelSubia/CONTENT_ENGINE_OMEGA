from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(r"D:\CONTENT_ENGINE_OMEGA")
RUNTIME_DIR = ROOT / "00_SYSTEM" / "core" / "runtime"
LOG_DIR = ROOT / "00_SYSTEM" / "core" / "logs"

REQUIRED_JSON = [
    RUNTIME_DIR / "SYSTEM_RUNTIME.json",
    RUNTIME_DIR / "EXECUTION_CONTEXT.json",
    RUNTIME_DIR / "HEARTBEAT.json",
    LOG_DIR / "RUNTIME_LOG.json",
    LOG_DIR / "manifest.json",
]

REQUIRED_SCRIPTS = [
    ROOT / "04_SCRIPTS" / "python" / "core" / "validate_phase_a.py",
    ROOT / "04_SCRIPTS" / "python" / "core" / "state_manager.py",
    ROOT / "04_SCRIPTS" / "python" / "core" / "logger_engine.py",
    ROOT / "04_SCRIPTS" / "python" / "core" / "runtime_engine.py",
    ROOT / "04_SCRIPTS" / "powershell" / "Validate-PhaseA.ps1",
    ROOT / "04_SCRIPTS" / "powershell" / "Run-ContentEngine.ps1",
]


def fail(message: str) -> None:
    print(f"PHASE_A_VALIDATION: FAIL - {message}")
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


def ensure_no_argos() -> None:
    for path in ROOT.rglob("*"):
        if "ARGOS" in {part.upper() for part in path.parts}:
            fail(f"ARGOS path detected inside root: {path}")


def main() -> None:
    if Path.cwd().resolve() != ROOT.resolve():
        fail(f"Current working directory must be {ROOT}")
    if "ARGOS" in {part.upper() for part in ROOT.parts}:
        fail("Root path contains ARGOS")
    if not RUNTIME_DIR.exists():
        fail(f"Missing runtime directory: {RUNTIME_DIR}")

    payloads = {str(path): load_json(path) for path in REQUIRED_JSON}

    runtime = payloads[str(RUNTIME_DIR / "SYSTEM_RUNTIME.json")]
    context = payloads[str(RUNTIME_DIR / "EXECUTION_CONTEXT.json")]
    heartbeat = payloads[str(RUNTIME_DIR / "HEARTBEAT.json")]

    if runtime.get("mode") != "DRY_RUN":
        fail("SYSTEM_RUNTIME.mode must be DRY_RUN")
    if runtime.get("current_phase") != "A":
        fail('SYSTEM_RUNTIME.current_phase must be "A"')
    if context.get("execution_mode") != "DRY_RUN":
        fail("EXECUTION_CONTEXT.execution_mode must be DRY_RUN")
    if context.get("allowed_scope") != str(ROOT):
        fail("EXECUTION_CONTEXT.allowed_scope must match the root")
    blocked_scopes = [str(item).upper() for item in context.get("blocked_scopes", [])]
    if "D:\\ARGOS" not in blocked_scopes:
        fail("EXECUTION_CONTEXT must block ARGOS")
    if heartbeat.get("system") != "CONTENT_ENGINE_OMEGA":
        fail("HEARTBEAT.system is invalid")

    for script_path in REQUIRED_SCRIPTS:
        if not script_path.exists():
            fail(f"Missing required script: {script_path}")

    ensure_no_argos()
    print("PHASE_A_VALIDATION: PASS")


if __name__ == "__main__":
    main()
