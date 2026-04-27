import json, pathlib, sys, subprocess

ROOT=pathlib.Path(r"D:\CONTENT_ENGINE_OMEGA")
C=ROOT/"00_SYSTEM/core/classification"

def fail(m):
    print("PHASE_C_VALIDATION: BLOCKED - "+m)
    sys.exit(1)

def load(p):
    if not p.exists(): fail(f"missing {p}")
    if p.stat().st_size == 0: fail(f"empty {p}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"invalid json {p}: {e}")

rules=load(C/"CLASSIFICATION_RULES.json")
result=load(C/"CLASSIFICATION_RESULT.json")
reg=load(C/"CLASSIFICATION_REGISTRY.json")
log=load(C/"CLASSIFICATION_CHANGE_LOG.json")
matrix=load(C/"EVIDENCE_WEIGHT_MATRIX.json")

if rules.get("mode")!="DRY_RUN": fail("mode not DRY_RUN")
if result.get("action_taken")!="NONE": fail("action_taken not NONE")
if not result.get("classification_hash"): fail("missing classification_hash")
if result.get("deterministic") is not True: fail("not deterministic")

for it in result.get("items",[]):
    if "confidence" not in it: fail("missing confidence")
    if not it.get("evidence"): fail("missing evidence")
    if it.get("protected") and it.get("label")=="POSSIBLE_GARBAGE":
        fail("protected item marked garbage")
    p=it.get("path","").lower()
    if ("audit" in p or "report" in p or "snapshot" in p) and it.get("label")=="POSSIBLE_GARBAGE":
        fail("false positive garbage")

print("PHASE_C_VALIDATION: PASS")
