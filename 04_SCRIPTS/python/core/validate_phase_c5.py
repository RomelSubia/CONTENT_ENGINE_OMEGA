import json, pathlib, sys

ROOT = pathlib.Path(r"D:\CONTENT_ENGINE_OMEGA")
C5 = ROOT / "00_SYSTEM/core/dev_self_governance"

def fail(m):
    print("PHASE_C5_VALIDATION: BLOCKED - " + m)
    sys.exit(1)

def load(p):
    p = pathlib.Path(p)
    if not p.exists(): fail(f"missing {p}")
    if p.stat().st_size == 0: fail(f"empty {p}")
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception as e:
        fail(f"invalid_json {p}: {e}")

rules = load(C5 / "DEV_GOVERNANCE_RULES.json")
state = load(C5 / "DEV_RECOVERY_STATE.json")
errors = load(C5 / "DEV_ERROR_LOG.json")
fixes = load(C5 / "DEV_FIX_LOG.json")

if rules.get("allow_delete") is not False: fail("delete allowed")
if rules.get("allow_git_clean") is not False: fail("git clean allowed")
if rules.get("allow_reset_hard") is not False: fail("reset hard allowed")
if rules.get("allow_force_push") is not False: fail("force push allowed")
if rules.get("allow_argos_scope") is not False: fail("ARGOS allowed")
if rules.get("fail_closed") is not True: fail("fail_closed disabled")

if state.get("state") not in ["VALID","IDLE"]:
    fail("state not valid")

if state.get("completion_score",0) < 85 and state.get("state") == "VALID":
    fail("completion score too low")

if not (C5 / "reports/PHASE_C5_DEV_GOVERNANCE_REPORT.md").exists():
    fail("missing dev report")
if not (ROOT / "00_SYSTEM/core/reports/PHASE_C5_AUDIT_REPORT.md").exists():
    fail("missing audit report")

print("PHASE_C5_VALIDATION: PASS")