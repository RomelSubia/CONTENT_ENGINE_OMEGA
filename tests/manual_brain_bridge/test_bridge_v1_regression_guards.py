from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BRIDGE_PATH = ROOT / "04_SCRIPTS/python/manual_brain_bridge/bridge_v1_manual_cerebro_connection.py"
READINESS_PATH = ROOT / "00_SYSTEM/bridge/reports/BRIDGE_BUILD_READINESS_REPORT.json"
VALIDATION_PATH = ROOT / "00_SYSTEM/bridge/reports/BRIDGE_VALIDATION_REPORT.json"
MANUAL_INTEGRITY_PATH = ROOT / "00_SYSTEM/bridge/reports/BRIDGE_MANUAL_INTEGRITY_REPORT.json"

spec = importlib.util.spec_from_file_location("bridge_v1", BRIDGE_PATH)
bridge = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(bridge)


def read_source() -> str:
    return BRIDGE_PATH.read_text(encoding="utf-8")


def function_block(name: str) -> str:
    source = read_source()
    start = source.index(f"def {name}(")
    next_start = source.find("\ndef ", start + 1)
    if next_start == -1:
        return source[start:]
    return source[start:next_start]


def json_file(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_regression_no_powershell_convertto_json_depth_over_100():
    violations = []
    for suffix in {".ps1", ".psm1", ".psd1"}:
        for path in ROOT.rglob(f"*{suffix}"):
            rel = path.relative_to(ROOT).as_posix()
            if ".git/" in rel or ".venv/" in rel:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for match in re.finditer(r"ConvertTo-Json[^\r\n]*?-Depth\s+(\d+)", text, flags=re.IGNORECASE):
                depth = int(match.group(1))
                if depth > 100:
                    violations.append((rel, depth, match.group(0)))
    assert violations == []


def test_regression_pytest_parametrize_does_not_use_reserved_request_name():
    violations = []
    for path in (ROOT / "tests").rglob("*.py"):
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"@pytest\.mark\.parametrize\(\s*['\"]([^'\"]+)['\"]", text):
            names = [part.strip() for part in match.group(1).split(",")]
            if "request" in names:
                violations.append((rel, match.group(1)))
    assert violations == []


def test_regression_validate_v37_uses_exact_fields_not_global_blob_search():
    block = function_block("validate_v37_closure")
    assert "freeze_path" in block
    assert "deviation_path" in block
    assert "next_path" in block
    assert "does_not_replace" in block
    assert "return_to_original_plan" in block
    assert "stable_json(loaded).upper" not in block


def test_regression_readiness_blocking_has_diagnostics_fields_in_source():
    block = function_block("build_readiness_report")
    assert "blocking_report_ids" in block
    assert "review_report_ids" in block
    assert "hard_block_report_ids" in block
    assert "blocking_status_present" in block


def test_regression_pass_with_warnings_only_for_foundation_return_policy():
    source = read_source()
    assert 'readiness.get("status") in {"PASS", "PASS_WITH_WARNINGS"}' in source
    assert "external_execution_allowed" in source
    assert "manual_write_allowed" in source
    assert "brain_write_allowed" in source


def test_regression_manual_runtime_review_does_not_block_foundation_build():
    block = function_block("manual_integrity_guard")
    assert '"REQUIRE_REVIEW"' in block
    assert "RUNTIME_MANUAL_REVIEW_REQUIRED" in block
    assert "Bridge foundation remains buildable" in block


def test_actual_readiness_status_is_pass_or_pass_with_warnings():
    readiness = json_file(READINESS_PATH)
    assert readiness["status"] in {"PASS", "PASS_WITH_WARNINGS"}


def test_actual_pass_with_warnings_has_review_ids_and_no_hard_block():
    readiness = json_file(READINESS_PATH)
    if readiness["status"] == "PASS_WITH_WARNINGS":
        assert readiness["build_allowed"] is True
        assert readiness["blocking_status_present"] is False
        assert readiness.get("review_report_ids")


def test_actual_validation_report_blocks_side_effects():
    validation = json_file(VALIDATION_PATH)
    assert validation["EXTERNAL_EXECUTION"] == "DISABLED"
    assert validation["BRAIN_MUTATION"] == "BLOCKED"
    assert validation["MANUAL_MUTATION"] == "BLOCKED"
    assert validation["AUTO_ACTION"] is False


def test_actual_manual_integrity_is_not_build_blocking():
    report = json_file(MANUAL_INTEGRITY_PATH)
    assert report["status"] in {"PASS", "REQUIRE_REVIEW", "PASS_WITH_WARNINGS"}
    assert report["status"] != "BLOCK"


def test_dynamic_manual_chat_noise_becomes_require_review(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()

    manual = root / bridge.MANUAL_PATH
    manual.parent.mkdir(parents=True, exist_ok=True)
    manual.write_text("PS D:\\CONTENT_ENGINE_OMEGA> git status", encoding="utf-8")

    source = bridge.source_resolver(root)
    report = bridge.manual_integrity_guard(root, source)

    assert report["status"] == "REQUIRE_REVIEW"
    assert report["runtime_manual_review_required"] is True

def test_regression_manual_runtime_allows_legitimate_powershell_instruction_tokens(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()

    manual = root / bridge.MANUAL_PATH
    manual.parent.mkdir(parents=True, exist_ok=True)
    manual.write_text(
        "\n".join([
            "Set-StrictMode -Version Latest",
            "$ErrorActionPreference = \"Stop\"",
            "Write-Host \"Repo check\"",
            "git status --short",
        ]),
        encoding="utf-8",
    )

    source = bridge.source_resolver(root)
    report = bridge.manual_integrity_guard(root, source)

    assert report["status"] == "PASS"
    assert report["runtime_manual_review_required"] is False
    assert "NO_CHAT_NOISE_CHECK" not in report["failed_checks"]
    assert "NO_TERMINAL_TRANSCRIPT_PROMPT_CHECK" not in report["failed_checks"]


def test_regression_manual_runtime_still_blocks_terminal_prompt_transcript(tmp_path: Path):
    root = tmp_path / "repo"
    root.mkdir()

    manual = root / bridge.MANUAL_PATH
    manual.parent.mkdir(parents=True, exist_ok=True)
    manual.write_text("PS D:\\CONTENT_ENGINE_OMEGA> git status", encoding="utf-8")

    source = bridge.source_resolver(root)
    report = bridge.manual_integrity_guard(root, source)

    assert report["status"] == "REQUIRE_REVIEW"
    assert report["runtime_manual_review_required"] is True
    assert "NO_TERMINAL_TRANSCRIPT_PROMPT_CHECK" in report["failed_checks"]
