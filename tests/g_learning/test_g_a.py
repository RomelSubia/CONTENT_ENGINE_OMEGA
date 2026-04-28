from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(PROJECT_ROOT))

from core.g_learning.g_a import run_g_a


def test_g_a_valid_evidence_is_deterministic():
    payload = {
        "execution_id": "F-RUN-001",
        "timestamp": "2026-04-28T00:00:00Z",
        "source_phase": "F",
        "logs": [{"event": "run_started"}, {"event": "run_finished"}],
        "metrics": [{"runtime": 1.2}],
        "decisions": [{"decision": "NO_ACTION"}],
        "outcomes": [{"status": "ok"}],
    }

    first = run_g_a(payload)
    second = run_g_a(payload)

    assert first["status"] == "VALID"
    assert first["deterministic"] is True
    assert first["output_hash"] == second["output_hash"]
    assert first["input_hash"] == second["input_hash"]


def test_g_a_empty_evidence_blocks_learning():
    payload = {
        "execution_id": "F-RUN-EMPTY",
        "timestamp": "2026-04-28T00:00:00Z",
        "source_phase": "F",
        "logs": [],
        "metrics": [],
        "decisions": [],
        "outcomes": [],
    }

    result = run_g_a(payload)

    assert result["status"] == "NO_LEARNING_ALLOWED"
    assert result["final_decision"] == "NO_LEARNING_ALLOWED"


def test_g_a_invalid_source_phase_blocks():
    payload = {
        "execution_id": "BAD-RUN",
        "timestamp": "2026-04-28T00:00:00Z",
        "source_phase": "X",
        "logs": [{"event": "bad"}],
        "metrics": [],
        "decisions": [],
        "outcomes": [],
    }

    result = run_g_a(payload)

    assert result["status"] == "BLOCKED"
    assert "INVALID_SOURCE_PHASE" in result["final_decision"]


if __name__ == "__main__":
    sample = {
        "execution_id": "F-RUN-SMOKE",
        "timestamp": "2026-04-28T00:00:00Z",
        "source_phase": "F",
        "logs": [{"event": "smoke"}],
        "metrics": [{"runtime": 1.0}],
        "decisions": [{"decision": "NO_ACTION"}],
        "outcomes": [{"status": "ok"}],
    }

    print(json.dumps(run_g_a(sample), indent=2, ensure_ascii=False))
