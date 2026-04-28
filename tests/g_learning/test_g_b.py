import sys
from pathlib import Path

root = Path(r"D:\CONTENT_ENGINE_OMEGA\00_SYSTEM")
sys.path.insert(0, str(root))

from core.g_learning.g_b import run_g_b

def test_g_b_basic():
    input_data = {
        "status": "VALID",
        "evidence_quality": 1.0,
        "evidence_count": 5,
        "records": [
            {"type": "logs"},
            {"type": "logs"},
            {"type": "metrics"},
            {"type": "metrics"},
            {"type": "metrics"}
        ]
    }

    a = run_g_b(input_data)
    b = run_g_b(input_data)

    assert a["status"] == "VALID"
    assert a["output_hash"] == b["output_hash"]
