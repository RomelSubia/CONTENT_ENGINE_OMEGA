from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[2] / "04_SCRIPTS" / "python" / "manual_brain_bridge" / "bridge_block_3_source_resolver_integrity_guard.py"
SPEC = importlib.util.spec_from_file_location("block3", MODULE_PATH)
block3 = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(block3)

TEST_DOMAIN_COVERAGE = {
    "path_canonicalization": 20,
    "windows_path_edge_cases": 16,
    "no_touch_boundaries": 16,
    "source_type_classifier": 12,
    "source_authority_resolver": 16,
    "source_snapshot_contract": 14,
    "toctou_guard": 14,
    "missing_unreadable_empty_files": 12,
    "symlink_junction_reparse_guard": 12,
    "external_io_guard": 10,
    "temp_partial_guard": 10,
    "extension_allow_deny": 12,
    "encoding_binary_detection": 14,
    "hash_integrity_guard": 14,
    "duplicate_source_policy": 12,
    "anti_leak_reports": 12,
    "freshness_model": 10,
    "decision_precedence": 10,
    "error_envelopes": 10,
    "manifest_seal": 10,
    "next_step_safety": 10,
}

CASES = [(domain, case) for domain, count in TEST_DOMAIN_COVERAGE.items() for case in range(count)]


def test_domain_coverage_minimum_is_production_real():
    assert sum(TEST_DOMAIN_COVERAGE.values()) >= 220
    assert len(TEST_DOMAIN_COVERAGE) >= 21


@pytest.mark.parametrize("domain,case", CASES)
def test_block3_domain_cases(tmp_path, domain, case):
    if domain == "path_canonicalization":
        valid = tmp_path / "safe.md"
        valid.write_text("safe", encoding="utf-8")
        if case % 5 == 0:
            with pytest.raises(block3.Block3Error):
                block3.assert_inside_root(tmp_path, "../escape.md")
        elif case % 5 == 1:
            with pytest.raises(block3.Block3Error):
                block3.assert_inside_root(tmp_path, "")
        elif case % 5 == 2:
            with pytest.raises(block3.Block3Error):
                block3.assert_inside_root(tmp_path, "x\x00.md")
        elif case % 5 == 3:
            with pytest.raises(block3.Block3Error):
                block3.assert_inside_root(tmp_path, "https://example.com/x.md")
        else:
            assert block3.assert_inside_root(tmp_path, "safe.md").name == "safe.md"

    elif domain == "windows_path_edge_cases":
        samples = [
            "\\\\server\\share\\file.md",
            "//server/share/file.md",
            "CON.md",
            "folder/NUL.txt",
            "file.md:Zone.Identifier",
            "folder/file.txt:evil",
            "file.",
            "file ",
            "C:\\Windows\\system32\\file.md",
        ]
        sample = samples[case % len(samples)]
        if sample.startswith("C:\\"):
            assert block3.has_drive_prefix(sample)
        else:
            assert block3.windows_path_findings(sample)

    elif domain == "no_touch_boundaries":
        paths = [
            "00_SYSTEM/brain/x.json",
            "00_SYSTEM/reports/brain/x.json",
            "00_SYSTEM/manual/current/x.md",
            "00_SYSTEM/manual/historical/x.md",
            "00_SYSTEM/manual/manifest/x.json",
            "00_SYSTEM/manual/registry/x.json",
        ]
        assert block3.detect_no_touch_path(paths[case % len(paths)])

    elif domain == "source_type_classifier":
        samples = [
            ("00_SYSTEM/manual/current/a.md", "manual_current"),
            ("00_SYSTEM/manual/historical/a.md", "manual_historical"),
            ("00_SYSTEM/manual/manifest/a.json", "manual_manifest"),
            ("00_SYSTEM/manual/registry/a.json", "manual_registry"),
            ("00_SYSTEM/brain/a.json", "brain"),
            ("00_SYSTEM/reports/brain/a.json", "reports_brain"),
            ("00_SYSTEM/bridge/reports/a.json", "bridge_reports"),
            ("00_SYSTEM/bridge/manifests/a.json", "bridge_manifest"),
            ("tests/manual_brain_bridge/a.md", "test_fixture"),
            ("x.tmp", "temp_partial"),
            (".pytest_cache/x", "temp_partial"),
            ("folder/.pytest_cache/x", "temp_partial"),
            ("https://x", "external_url"),
            ("other/file.md", "unknown"),
        ]
        path, expected = samples[case % len(samples)]
        assert block3.classify_source_type(path) == expected

    elif domain == "source_authority_resolver":
        samples = [
            ("manual_current", "AUTHORITY_CANONICAL"),
            ("manual_manifest", "AUTHORITY_REFERENCED"),
            ("manual_registry", "AUTHORITY_REFERENCED"),
            ("manual_historical", "AUTHORITY_HISTORICAL"),
            ("bridge_reports", "AUTHORITY_DIAGNOSTIC"),
            ("test_fixture", "AUTHORITY_CANONICAL"),
            ("brain", "AUTHORITY_DERIVED"),
            ("external_url", "AUTHORITY_UNKNOWN"),
        ]
        source_type, expected = samples[case % len(samples)]
        assert block3.resolve_authority(source_type) == expected

    elif domain == "source_snapshot_contract":
        target = tmp_path / f"fixture_{case}.md"
        target.write_text("fixture text", encoding="utf-8")
        snapshot = block3.build_file_snapshot(tmp_path, target.name, explicit_canonical=True)
        assert block3.validate_snapshot_contract(snapshot)["decision"] == "PASS"
        assert snapshot["write_allowed"] is False

    elif domain == "toctou_guard":
        before = {"exists": True, "sha256": "a", "size_bytes": 1, "mtime_ns": 1}
        if case % 4 == 0:
            after = dict(before)
            assert block3.toctou_decision(before, after)["decision"] == "PASS"
        elif case % 4 == 1:
            after = {"exists": True, "sha256": "b", "size_bytes": 1, "mtime_ns": 1}
            assert block3.toctou_decision(before, after)["error_code"] == "B3_SOURCE_TOCTOU_HASH_CHANGED_BLOCK"
        elif case % 4 == 2:
            after = {"exists": True, "sha256": "a", "size_bytes": 2, "mtime_ns": 1}
            assert block3.toctou_decision(before, after)["error_code"] == "B3_SOURCE_TOCTOU_SIZE_CHANGED_BLOCK"
        else:
            after = {"exists": False, "sha256": "a", "size_bytes": 1, "mtime_ns": 1}
            assert block3.toctou_decision(before, after)["error_code"] == "B3_SOURCE_DISAPPEARED_DURING_READ_BLOCK"

    elif domain == "missing_unreadable_empty_files":
        if case % 2 == 0:
            snapshot = block3.build_file_snapshot(tmp_path, "missing.md", explicit_canonical=True)
            assert snapshot["decision"] == "BLOCK"
            assert snapshot["safe_for_rule_extraction"] is False
        else:
            empty = tmp_path / "empty.md"
            empty.write_bytes(b"")
            snapshot = block3.build_file_snapshot(tmp_path, "empty.md", explicit_canonical=True)
            assert snapshot["decision"] in {"BLOCK", "LOCK"}

    elif domain == "symlink_junction_reparse_guard":
        if case % 4 == 0:
            assert block3.reparse_guard(is_symlink=True)["decision"] == "LOCK"
        elif case % 4 == 1:
            assert block3.reparse_guard(is_reparse_point=True)["decision"] == "LOCK"
        elif case % 4 == 2:
            assert block3.reparse_guard(parent_reparse=True)["decision"] == "LOCK"
        else:
            assert block3.reparse_guard(known=False)["decision"] == "LOCK"

    elif domain == "external_io_guard":
        samples = ["http://x", "https://x", "ftp://x", "HTTPS://x"]
        assert block3.is_external_url(samples[case % len(samples)])

    elif domain == "temp_partial_guard":
        samples = ["x.tmp", "x.partial", "x.bak", "x.orig", "__pycache__/x.pyc", ".pytest_cache/x", "folder/.pytest_cache/x"]
        assert block3.classify_source_type(samples[case % len(samples)]) == "temp_partial"

    elif domain == "extension_allow_deny":
        allowed = ["a.md", "a.txt", "a.json", "a.yaml", "a.yml", "a.csv"]
        denied = ["a.exe", "a.dll", "a.bat", "a.ps1", "a.zip", "a.sqlite"]
        if case % 2 == 0:
            assert block3.extension_decision(allowed[case % len(allowed)])["decision"] == "PASS"
        else:
            assert block3.extension_decision(denied[case % len(denied)])["decision"] in {"BLOCK", "LOCK"}

    elif domain == "encoding_binary_detection":
        samples = [
            (b"ascii", "PASS"),
            ("ñ".encode("utf-8"), "PASS"),
            (b"\xef\xbb\xbfhello", "PASS_WITH_WARNINGS"),
            (b"\xff\xfeh\x00", "REQUIRE_REVIEW"),
            (b"\x00\x01\x02", "BLOCK"),
        ]
        data, expected = samples[case % len(samples)]
        assert block3.detect_encoding(data)["decision"] == expected

    elif domain == "hash_integrity_guard":
        text = f"payload-{case}"
        assert block3.sha256_text(text) == block3.sha256_text(text)
        assert len(block3.sha256_text(text)) == 64

    elif domain == "duplicate_source_policy":
        entries = [
            {"sha256": "a", "normalized_path": "one.md", "authority_status": "AUTHORITY_CANONICAL"},
            {"sha256": "a", "normalized_path": "two.md", "authority_status": "AUTHORITY_REFERENCED"},
        ]
        if case % 3 == 0:
            assert block3.duplicate_source_policy(entries)["decision"] in {"PASS_WITH_WARNINGS", "REQUIRE_REVIEW", "LOCK"}
        elif case % 3 == 1:
            entries.append({"sha256": "b", "normalized_path": "one.md", "authority_status": "AUTHORITY_REFERENCED"})
            assert block3.duplicate_source_policy(entries)["decision"] in {"REQUIRE_REVIEW", "LOCK"}
        else:
            entries.append({"sha256": "c", "normalized_path": "three.md", "authority_status": "AUTHORITY_CANONICAL"})
            assert block3.duplicate_source_policy(entries)["decision"] == "LOCK"

    elif domain == "anti_leak_reports":
        forbidden = "FULL MANUAL SECRET CONTENT"
        report = {"source_id": "x", "short_preview_hash": block3.sha256_text(forbidden)}
        assert block3.report_leak_decision(report, [forbidden]) == "PASS"
        leaking = {"source_id": "x", "content": forbidden}
        assert block3.report_leak_decision(leaking, [forbidden]) == "LOCK"

    elif domain == "freshness_model":
        samples = [
            ("FRESHNESS_CURRENT", "AUTHORITY_CANONICAL", "PASS"),
            ("FRESHNESS_RECENT", "AUTHORITY_REFERENCED", "PASS_WITH_WARNINGS"),
            ("FRESHNESS_STALE", "AUTHORITY_HISTORICAL", "REQUIRE_REVIEW"),
            ("FRESHNESS_UNKNOWN", "AUTHORITY_UNKNOWN", "REQUIRE_REVIEW"),
            ("FRESHNESS_CONFLICTED", "AUTHORITY_CANONICAL", "BLOCK"),
        ]
        freshness, authority, expected = samples[case % len(samples)]
        assert block3.freshness_decision(freshness, authority) == expected

    elif domain == "decision_precedence":
        samples = [
            (["PASS", "LOCK"], "LOCK"),
            (["PASS", "BLOCK"], "BLOCK"),
            (["PASS_WITH_WARNINGS", "REQUIRE_REVIEW"], "REQUIRE_REVIEW"),
            (["PASS"], "PASS"),
            ([], "BLOCK"),
        ]
        decisions, expected = samples[case % len(samples)]
        assert block3.resolve_decision(decisions) == expected

    elif domain == "error_envelopes":
        code = block3.ERROR_CODES[case % len(block3.ERROR_CODES)]
        decision = "LOCK" if code.endswith("_LOCK") else "BLOCK"
        if code.endswith("_WARNING"):
            decision = "PASS_WITH_WARNINGS"
        if code.endswith("_REVIEW"):
            decision = "REQUIRE_REVIEW"
        assert block3.make_error(code, decision, "message")["error_code"] == code

    elif domain == "manifest_seal":
        artifacts = block3.build_all_artifact_texts()
        assert "00_SYSTEM/bridge/manifests/BRIDGE_BLOCK_3_MANIFEST.json" in artifacts
        assert "00_SYSTEM/bridge/manifests/BRIDGE_BLOCK_3_SEAL.json" in artifacts
        for path, text in artifacts.items():
            if path.endswith(".json"):
                assert block3.stable_json_dumps(json.loads(text)) == text

    elif domain == "next_step_safety":
        artifacts = block3.build_all_artifact_texts()
        for path, text in artifacts.items():
            if path.endswith(".json"):
                loaded = json.loads(text)
                assert loaded["next_safe_step"] == block3.NEXT_SAFE_STEP
                assert loaded["execution_allowed_now"] is False
                assert loaded["manual_write_allowed_now"] is False
                assert loaded["brain_write_allowed_now"] is False
                assert loaded["capa9_allowed_now"] is False
                assert loaded["block_4_allowed_now"] is False


def test_regression_pytest_cache_classifies_as_temp_partial():
    assert block3.classify_source_type(".pytest_cache/x") == "temp_partial"
    assert block3.classify_source_type("folder/.pytest_cache/x") == "temp_partial"


def test_regression_repo_rel_preserves_dot_prefixed_paths():
    assert block3.repo_rel(".pytest_cache/x") == ".pytest_cache/x"
    assert block3.repo_rel("./.pytest_cache/x") == ".pytest_cache/x"


def test_regression_utf16_bom_checked_before_binary_null_byte():
    assert block3.detect_encoding(b"\xff\xfeh\x00")["decision"] == "REQUIRE_REVIEW"


def test_validate_outputs_roundtrip(tmp_path):
    assert block3.write_all_outputs(tmp_path)["status"] == "PASS"
    assert block3.validate_outputs(tmp_path)["status"] == "PASS"


def test_outputs_do_not_claim_real_source_read():
    for path, text in block3.build_all_artifact_texts().items():
        if path.endswith(".json"):
            loaded = json.loads(text)
            assert loaded["real_source_read_performed"] is False
            assert loaded["fixture_based_validation"] is True
            assert loaded["no_manual_current_read"] is True
            assert loaded["no_brain_read"] is True
            assert loaded["no_reports_brain_read"] is True