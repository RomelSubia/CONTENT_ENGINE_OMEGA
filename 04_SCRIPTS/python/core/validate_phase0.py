from __future__ import annotations

import json
import sys
from pathlib import Path


EXPECTED_ROOT = Path(r"D:\CONTENT_ENGINE_OMEGA")
CORE_DIR = EXPECTED_ROOT / "00_SYSTEM" / "core"
PYTHON_FILE = EXPECTED_ROOT / "04_SCRIPTS" / "python" / "core" / "validate_phase0.py"
REQUIRED_JSON = [
    "GOVERNANCE_RULES.json",
    "SYSTEM_STATE.json",
    "STATE_TRANSITIONS.json",
    "EVIDENCE_SCHEMA.json",
    "ERROR_SEVERITY_MODEL.json",
    "ACTION_POLICY.json",
    "ACTION_LOG.json",
    "QUARANTINE_LOG.json",
]


def fail(message: str) -> None:
    print(f"PHASE_0_VALIDATION: FAIL - {message}")
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    if not path.exists():
        fail(f"Missing required file: {path}")
    if path.stat().st_size == 0:
        fail(f"Empty JSON file: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {path}: {exc}")
    return {}


def validate_root() -> None:
    resolved_root = EXPECTED_ROOT.resolve()
    script_root = PYTHON_FILE.resolve().parents[3]
    cwd_root = Path.cwd().resolve()
    if script_root != resolved_root:
        fail(f"Script is outside expected root: {script_root}")
    if cwd_root != resolved_root:
        fail(f"Current working directory must be {resolved_root}, got {cwd_root}")
    if not CORE_DIR.exists():
        fail(f"Missing required directory: {CORE_DIR}")


def validate_argos_isolation() -> None:
    forbidden_hits = []
    for path in EXPECTED_ROOT.rglob("*"):
        parts_upper = {part.upper() for part in path.parts}
        if "ARGOS" in parts_upper:
            forbidden_hits.append(str(path))
    if forbidden_hits:
        fail(f"ARGOS path detected inside root: {forbidden_hits[0]}")


def main() -> None:
    validate_root()

    payloads = {}
    for file_name in REQUIRED_JSON:
        payloads[file_name] = load_json(CORE_DIR / file_name)

    governance = payloads["GOVERNANCE_RULES.json"]
    system_state = payloads["SYSTEM_STATE.json"]
    transitions = payloads["STATE_TRANSITIONS.json"]
    action_policy = payloads["ACTION_POLICY.json"]

    if governance.get("no_delete") is not True:
        fail("GOVERNANCE_RULES.no_delete must be true")
    if governance.get("mode") != "DRY_RUN":
        fail("GOVERNANCE_RULES.mode must be DRY_RUN")
    if governance.get("argos_isolation") is not True:
        fail("GOVERNANCE_RULES.argos_isolation must be true")

    prohibited_actions = action_policy.get("prohibited_actions", [])
    if "DELETE" not in prohibited_actions:
        fail("ACTION_POLICY must prohibit DELETE")

    direct_blocked_to_valid = any(
        item.get("from") == "BLOCKED" and item.get("to") == "VALID"
        for item in transitions.get("allowed_transitions", [])
    )
    if direct_blocked_to_valid:
        fail("STATE_TRANSITIONS must not allow BLOCKED -> VALID directly")

    if system_state.get("current_phase") != "0":
        fail('SYSTEM_STATE.current_phase must be "0"')
    if system_state.get("mode") != "DRY_RUN":
        fail('SYSTEM_STATE.mode must be "DRY_RUN"')

    env_profile_path = EXPECTED_ROOT / ".env_profile.ps1"
    if env_profile_path.exists() and env_profile_path.is_dir():
        fail(".env_profile.ps1 must not exist as a directory")

    validate_argos_isolation()
    print("PHASE_0_VALIDATION: PASS")


if __name__ == "__main__":
    main()
