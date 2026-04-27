import json, pathlib, sys

ROOT=pathlib.Path(r"D:\CONTENT_ENGINE_OMEGA")
LOOP=ROOT/"00_SYSTEM/core/loop"

def fail(m):
    print("PHASE_F_VALIDATION: BLOCKED - " + m)
    sys.exit(1)

def load(p):
    p=pathlib.Path(p)
    if not p.exists(): fail(f"missing {p}")
    if p.stat().st_size == 0: fail(f"empty {p}")
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception as e:
        fail(f"invalid_json {p}: {e}")

rules=load(LOOP/"LOOP_RULES.json")
state=load(LOOP/"LOOP_STATE.json")
chain=load(LOOP/"LOOP_SNAPSHOT_CHAIN.json")
log=load(LOOP/"LOOP_CYCLE_LOG.json")

if rules.get("allow_infinite_loop") is not False: fail("infinite_loop_allowed")
if rules.get("allow_autonomy_escalation") is not False: fail("autonomy_escalation_allowed")
if rules.get("allow_full_auto") is not False: fail("full_auto_allowed")
if rules.get("allow_outside_root") is not False: fail("outside_root_allowed")
if rules.get("allow_argos_scope") is not False: fail("argos_allowed")
if rules.get("max_cycles") != 1: fail("max_cycles not initial safe value")
if state.get("state") != "VALIDATED": fail("loop state not validated")
if state.get("stability_score",0) < 0.9: fail("stability_score too low")
if state.get("drift_detected") is not False: fail("drift detected")
if not chain.get("chain"): fail("empty hash chain")
if not pathlib.Path(ROOT/"00_SYSTEM/core/loop/reports/PHASE_F_LOOP_REPORT.md").exists(): fail("missing loop report")
if not pathlib.Path(ROOT/"00_SYSTEM/core/reports/PHASE_F_AUDIT_REPORT.md").exists(): fail("missing audit report")

print("PHASE_F_VALIDATION: PASS")
