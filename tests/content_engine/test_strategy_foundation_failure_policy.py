from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "04_SCRIPTS" / "python"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from content_engine.strategy_foundation.strategy_failure_policy import build_failure_report, validate_failure_report


def test_failure_report_passes():
    assert validate_failure_report(build_failure_report("x", "g"))["status"] == "PASS"


def test_failure_report_failed_blocked():
    assert build_failure_report("x", "g")["status"] == "FAILED_BLOCKED"


def test_failure_report_no_commit_no_push():
    report = build_failure_report("x", "g")
    assert report["commit_created"] is False
    assert report["push_performed"] is False


def test_failure_report_blocks_generation():
    report = build_failure_report("x", "g")
    assert report["content_generation_started"] is False
    assert report["prompt_generation_started"] is False


def test_failure_report_blocks_capa9():
    assert build_failure_report("x", "g")["capa9_performed"] is False


def test_failure_report_mutated_commit_blocks_negative():
    report = build_failure_report("x", "g")
    report["commit_created"] = True
    assert validate_failure_report(report)["status"] == "BLOCK"
