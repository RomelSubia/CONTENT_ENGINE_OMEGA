from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.construction_core.failure_report_contract import build_failure_report, validate_failure_report


def test_failure_report_passes():
    report = build_failure_report("reason", "gate")
    assert validate_failure_report(report)["status"] == "PASS"


def test_failure_report_status_failed_blocked():
    report = build_failure_report("reason", "gate")
    assert report["status"] == "FAILED_BLOCKED"


def test_failure_report_no_commit_no_push():
    report = build_failure_report("reason", "gate")
    assert report["commit_created"] is False
    assert report["push_performed"] is False


def test_failure_report_blocks_execution():
    report = build_failure_report("reason", "gate")
    assert report["execution_started"] is False
    assert report["capa9_performed"] is False


def test_failure_report_blocks_mutated_commit_negative():
    report = build_failure_report("reason", "gate")
    report["commit_created"] = True
    assert validate_failure_report(report)["status"] == "BLOCK"
