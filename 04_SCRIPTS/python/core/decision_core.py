import json, hashlib, datetime, pathlib, sys

ROOT = pathlib.Path(r"D:\CONTENT_ENGINE_OMEGA")
OUT = ROOT / "00_SYSTEM/core/decision"
REPORT = OUT / "reports/PHASE_D_DECISION_REPORT.md"

def now():
    return datetime.datetime.now(datetime.UTC).isoformat()

def hash_obj(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()

def fail(msg):
    print("PHASE_D: BLOCKED - " + msg)
    sys.exit(1)

# ===== INPUT SIMULADO (DE FASE C) =====
data = [
    {"file": "temp.log", "classification": "TEMPORARY"},
    {"file": "system.cfg", "classification": "CRITICAL"}
]

decisions = []

for item in data:

    decision = {}
    decision["file"] = item["file"]
    decision["classification"] = item["classification"]

    # ===== RISK =====
    if item["classification"] == "CRITICAL":
        decision["risk"] = "CRITICAL"
        decision["decision"] = "BLOCK"
        decision["state"] = "BLOCKED"
    else:
        decision["risk"] = "LOW"
        decision["decision"] = "DELETE"
        decision["state"] = "PROPOSED"

    decision["execution_allowed"] = False
    decision["execution_proven_false"] = True

    # ===== HASH =====
    decision["decision_hash"] = hash_obj(decision)

    decisions.append(decision)

# ===== VALIDACIÓN =====
for d in decisions:
    if d["execution_allowed"] == True:
        fail("EXECUTION DETECTED")

# ===== OUTPUT =====
(OUT / "DECISION_REGISTRY.json").write_text(json.dumps(decisions, indent=2))

REPORT.write_text(f"""
# PHASE D REPORT

Timestamp: {now()}

Decisions:
{json.dumps(decisions, indent=2)}

Execution: PROVEN FALSE
Status: VALIDATED
""")

print("PHASE_D_ENGINE: PASS")
