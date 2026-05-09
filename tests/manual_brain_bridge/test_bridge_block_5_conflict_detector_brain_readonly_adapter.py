from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = ROOT / "04_SCRIPTS" / "python" / "manual_brain_bridge"
sys.path.insert(0, str(MODULE_DIR))

import bridge_block_5_conflict_detector_brain_readonly_adapter as b5


GOOD_HASH = "a" * 64
OTHER_HASH = "b" * 64


def claim(**overrides):
    base = dict(
        claim_id="c1",
        raw_claim="Brain write is denied",
        claim_type="POLICY",
        polarity="DENY",
        subject="brain",
        predicate="write",
        object="content",
        scope="manual_cerebro_bridge",
        authority_level="SEALED",
        confidence="HIGH",
        evidence_pointer="evidence://sealed/policy",
        content_hash=GOOD_HASH,
    )
    base.update(overrides)
    status, normalized = b5.normalize_claim(**base)
    assert status["status"] == b5.PASS
    assert normalized is not None
    return normalized


@pytest.mark.parametrize("decision", [b5.PASS, b5.PASS_WITH_WARNINGS, b5.REQUIRE_REVIEW, b5.BLOCK, b5.LOCK])
def test_most_restrictive_understands_all_valid_decisions(decision):
    assert b5.most_restrictive(b5.PASS, decision) == decision


@pytest.mark.parametrize(
    "payload,expected",
    [
        (dict(result_count=1, query_depth=1, requested_full_scan=False, requested_raw_dump=False, requested_directory_walk=False), b5.PASS),
        (dict(result_count=11, query_depth=1, requested_full_scan=False, requested_raw_dump=False, requested_directory_walk=False), b5.BLOCK),
        (dict(result_count=1, query_depth=3, requested_full_scan=False, requested_raw_dump=False, requested_directory_walk=False), b5.BLOCK),
        (dict(result_count=1, query_depth=1, requested_full_scan=True, requested_raw_dump=False, requested_directory_walk=False), b5.LOCK),
        (dict(result_count=1, query_depth=1, requested_full_scan=False, requested_raw_dump=True, requested_directory_walk=False), b5.LOCK),
        (dict(result_count=1, query_depth=1, requested_full_scan=False, requested_raw_dump=False, requested_directory_walk=True), b5.LOCK),
    ],
)
def test_brain_read_scope_limiter(payload, expected):
    assert b5.validate_scope_request(**payload)["status"] == expected


@pytest.mark.parametrize(
    "summary,evidence,hash_value,raw,full,expected",
    [
        ("safe", "evidence://x", GOOD_HASH, False, False, b5.PASS),
        ("safe", "", GOOD_HASH, False, False, b5.BLOCK),
        ("safe", "evidence://x", "bad", False, False, b5.BLOCK),
        ("safe", "evidence://x", GOOD_HASH, True, False, b5.LOCK),
        ("safe", "evidence://x", GOOD_HASH, False, True, b5.LOCK),
        ("x" * 801, "evidence://x", GOOD_HASH, False, False, b5.BLOCK),
    ],
)
def test_raw_content_leakage_guard(summary, evidence, hash_value, raw, full, expected):
    result = b5.validate_summary_output(
        summary=summary,
        evidence_pointer=evidence,
        content_hash=hash_value,
        raw_content_returned=raw,
        full_document_returned=full,
    )
    assert result["status"] == expected


@pytest.mark.parametrize(
    "before,after,expected",
    [
        ("abc", "abc", b5.PASS),
        ("abc", "xyz", b5.LOCK),
        ("", "xyz", b5.BLOCK),
        ("abc", "", b5.BLOCK),
    ],
)
def test_brain_mutation_proof_guard(before, after, expected):
    assert b5.verify_brain_not_mutated(before, after)["status"] == expected


@pytest.mark.parametrize(
    "source",
    [
        "path.write_text('x')",
        "path.write_bytes(b'x')",
        "open('x', 'w')",
        "open('x', 'a')",
        "Path('x').unlink()",
        "item.rename('y')",
        "item.replace('y')",
        "shutil.rmtree('x')",
        "os.remove('x')",
        "os.system('x')",
        "subprocess.run(['x'])",
        "requests.get('x')",
        "httpx.get('x')",
        "socket.socket()",
        "ftplib.FTP('x')",
        "smtplib.SMTP('x')",
        "webbrowser.open('x')",
        "sqlite connect write mode",
    ],
)
def test_adapter_capability_denylist_blocks_dangerous_patterns(source):
    assert b5.validate_no_dangerous_capabilities(source)["status"] == b5.LOCK


@pytest.mark.parametrize(
    "source",
    [
        "data = {'safe': True}",
        "Path('x').read_text()",
        "hashlib.sha256(b'x').hexdigest()",
        "json.dumps({'x': 1})",
        "sorted([3, 2, 1])",
    ],
)
def test_adapter_capability_denylist_allows_safe_patterns(source):
    assert b5.validate_no_dangerous_capabilities(source)["status"] == b5.PASS


@pytest.mark.parametrize(
    "field,value,expected",
    [
        ("claim_id", "", b5.BLOCK),
        ("raw_claim", "", b5.BLOCK),
        ("claim_type", "BAD", b5.BLOCK),
        ("polarity", "BAD", b5.BLOCK),
        ("authority_level", "BAD", b5.BLOCK),
        ("confidence", "BAD", b5.BLOCK),
        ("evidence_pointer", "", b5.BLOCK),
        ("content_hash", "bad", b5.BLOCK),
        ("polarity", "UNKNOWN", b5.BLOCK),
    ],
)
def test_claim_normalization_fail_closed(field, value, expected):
    kwargs = dict(
        claim_id="c1",
        raw_claim="x",
        claim_type="POLICY",
        polarity="DENY",
        subject="s",
        predicate="p",
        object="o",
        scope="scope",
        authority_level="SEALED",
        confidence="HIGH",
        evidence_pointer="evidence://x",
        content_hash=GOOD_HASH,
    )
    kwargs[field] = value
    status, normalized = b5.normalize_claim(**kwargs)
    assert status["status"] == expected
    assert normalized is None


def test_claim_normalization_outputs_stable_normalized_claim():
    normalized = claim(raw_claim="  Brain   WRITE is   DENIED  ")
    assert normalized.normalized_claim == "brain write is denied"


@pytest.mark.parametrize(
    "left_kwargs,right_kwargs,expected",
    [
        ({}, {"content_hash": OTHER_HASH, "evidence_pointer": ""}, b5.BLOCK),
        ({}, {"content_hash": "bad"}, b5.BLOCK),
        ({"authority_level": "SEALED"}, {"authority_level": "SEALED", "content_hash": OTHER_HASH}, b5.LOCK),
        ({"authority_level": "HIGH"}, {"authority_level": "CANONICAL", "content_hash": OTHER_HASH}, b5.PASS),
    ],
)
def test_conflict_evidence_pairing(left_kwargs, right_kwargs, expected):
    left = claim(**left_kwargs)
    right = claim(claim_id="c2", **right_kwargs)
    assert b5.validate_conflict_evidence(left, right)["status"] == expected


@pytest.mark.parametrize(
    "conflict_type,decision,expected",
    [
        ("PERMISSION_CONFLICT", b5.BLOCK, b5.LOCK),
        ("BRAIN_WRITE_CONFLICT", b5.BLOCK, b5.LOCK),
        ("NO_TOUCH_CONFLICT", b5.BLOCK, b5.LOCK),
        ("CAPA9_CONFLICT", b5.BLOCK, b5.LOCK),
        ("SOURCE_AUTHORITY_CONFLICT", b5.REQUIRE_REVIEW, b5.LOCK),
        ("EVIDENCE_CONFLICT", b5.REQUIRE_REVIEW, b5.LOCK),
        ("DUPLICATE_RULE_CONFLICT", b5.PASS, b5.LOCK),
        ("SEMANTIC_CONFLICT", b5.PASS_WITH_WARNINGS, b5.LOCK),
        ("UNKNOWN_CONFLICT", b5.REQUIRE_REVIEW, b5.PASS),
        ("BAD_CONFLICT", b5.PASS, b5.LOCK),
    ],
)
def test_severity_anti_downgrade(conflict_type, decision, expected):
    assert b5.enforce_severity_anti_downgrade(conflict_type, decision)["status"] == expected


def test_detect_conflict_finds_policy_contradiction():
    left = claim(polarity="DENY")
    right = claim(claim_id="c2", polarity="ALLOW", content_hash=OTHER_HASH, evidence_pointer="evidence://y", authority_level="HIGH")
    conflict = b5.detect_conflict(left, right)
    assert conflict.conflict_type == "POLICY_CONFLICT"
    assert conflict.decision == b5.BLOCK


def test_detect_conflict_merges_duplicate_hashes():
    left = claim()
    right = claim(claim_id="c2", evidence_pointer="evidence://y")
    conflict = b5.detect_conflict(left, right)
    assert conflict.conflict_type in {"DUPLICATE_RULE_CONFLICT", "EVIDENCE_CONFLICT"}


def test_conflict_deduplication_merges_same_pair():
    left = claim()
    right = claim(claim_id="c2", content_hash=OTHER_HASH, evidence_pointer="evidence://y", authority_level="HIGH")
    c1 = b5.make_conflict("SEMANTIC_CONFLICT", "MEDIUM", left, right, "x")
    c2 = b5.make_conflict("SEMANTIC_CONFLICT", "MEDIUM", right, left, "x")
    assert len(b5.deduplicate_conflicts([c1, c2])) == 1


def test_deterministic_conflict_ordering_prioritizes_critical():
    left = claim()
    right = claim(claim_id="c2", content_hash=OTHER_HASH, evidence_pointer="evidence://y", authority_level="HIGH")
    low = b5.make_conflict("DUPLICATE_RULE_CONFLICT", "LOW", left, right, "low")
    critical = b5.make_conflict("PERMISSION_CONFLICT", "CRITICAL", left, right, "critical")
    ordered = b5.sort_conflicts([low, critical])
    assert ordered[0].severity == "CRITICAL"


@pytest.mark.parametrize(
    "action",
    [
        "cache_write",
        "index_rebuild",
        "embedding_update",
        "brain_index_mutation",
        "derived_brain_store_write",
        "temporary_brain_copy_write",
        "brain_normalization_write",
    ],
)
def test_no_cache_no_index_mutation_guard(action):
    assert b5.validate_cache_index_action(action)["status"] == b5.LOCK


@pytest.mark.parametrize(
    "action",
    [
        "auto_merge",
        "auto_patch",
        "auto_delete",
        "auto_promote_source",
        "auto_select_winner",
        "auto_update_manual",
        "auto_update_brain",
        "auto_create_plan",
        "auto_execute_recovery",
    ],
)
def test_automatic_conflict_resolution_prohibition(action):
    assert b5.validate_automatic_resolution_action(action)["status"] == b5.LOCK


@pytest.mark.parametrize(
    "action",
    [
        "decision_mapper",
        "controlled_plan_builder",
        "plan_execution_model",
        "automatic_resolution_engine",
        "bloque_6_build",
        "bloque_6_prebuild",
    ],
)
def test_bloque_6_boundary_guard(action):
    assert b5.validate_block6_boundary(action)["status"] == b5.LOCK


@pytest.mark.parametrize(
    "payload,expected",
    [
        ({}, b5.PASS),
        ({"grant_build_directly": True}, b5.LOCK),
        ({"execute": True}, b5.LOCK),
        ({"write_manual": True}, b5.LOCK),
        ({"write_brain": True}, b5.LOCK),
        ({"write_reports_brain": True}, b5.LOCK),
        ({"skip_implementation_plan": True}, b5.BLOCK),
        ({"skip_build_approval": True}, b5.LOCK),
    ],
)
def test_human_review_boundary(payload, expected):
    assert b5.validate_human_review_boundary(payload)["status"] == expected


@pytest.mark.parametrize(
    "claim_count,pairs,brain_results,depth,expected",
    [
        (10, 10, 1, 1, b5.PASS),
        (201, 10, 1, 1, b5.BLOCK),
        (10, 5001, 1, 1, b5.BLOCK),
        (10, 10, 11, 1, b5.BLOCK),
        (10, 10, 1, 3, b5.BLOCK),
    ],
)
def test_performance_bound(claim_count, pairs, brain_results, depth, expected):
    assert b5.validate_performance_bounds(
        claim_count=claim_count,
        pairwise_comparisons=pairs,
        brain_results=brain_results,
        query_depth=depth,
    )["status"] == expected


@pytest.mark.parametrize(
    "read_only,write,mutation,evidence,hash_value,expected",
    [
        (True, False, False, ["e"], GOOD_HASH, b5.PASS),
        (False, False, False, ["e"], GOOD_HASH, b5.LOCK),
        (True, True, False, ["e"], GOOD_HASH, b5.LOCK),
        (True, False, True, ["e"], GOOD_HASH, b5.LOCK),
        (True, False, False, [], GOOD_HASH, b5.BLOCK),
        (True, False, False, ["e"], "bad", b5.BLOCK),
    ],
)
def test_read_only_result_envelope(read_only, write, mutation, evidence, hash_value, expected):
    result = b5.BrainReadOnlyResultEnvelope(
        result_id="r",
        query_id="q",
        status="FOUND",
        read_only=read_only,
        brain_write_performed=write,
        brain_mutation_performed=mutation,
        evidence_refs=evidence,
        content_summary="summary",
        content_hash=hash_value,
        confidence="HIGH",
        limitations=[],
    )
    assert b5.validate_read_only_result(result)["status"] == expected


def test_tree_fingerprint_detects_fixture_mutation(tmp_path):
    f = tmp_path / "brain.txt"
    f.write_text("a", encoding="utf-8")
    before = b5.tree_fingerprint(tmp_path)
    f.write_text("b", encoding="utf-8")
    after = b5.tree_fingerprint(tmp_path)
    assert b5.verify_brain_not_mutated(before, after)["status"] == b5.LOCK


def test_tree_fingerprint_passes_when_fixture_unchanged(tmp_path):
    f = tmp_path / "brain.txt"
    f.write_text("a", encoding="utf-8")
    before = b5.tree_fingerprint(tmp_path)
    after = b5.tree_fingerprint(tmp_path)
    assert b5.verify_brain_not_mutated(before, after)["status"] == b5.PASS


def test_reports_payloads_are_built_pending_post_audit():
    reports = b5.build_block5_report_payloads()
    assert len(reports) == 6
    for payload in reports.values():
        assert payload["status"] == "BUILT_PENDING_POST_AUDIT"


def test_readiness_map_blocks_bloque_6_and_execution():
    reports = b5.build_block5_report_payloads()
    readiness = reports["BRIDGE_BLOCK_5_NEXT_LAYER_READINESS_MAP.json"]
    assert readiness["post_build_audit_allowed_next"] is True
    assert readiness["bloque_6_blueprint_allowed_now"] is False
    assert readiness["hard_blocks"]["execution"] == "BLOCKED"


def test_canonical_json_is_stable():
    left = b5.canonical_json({"b": 2, "a": 1})
    right = b5.canonical_json({"a": 1, "b": 2})
    assert left == right
    assert left.endswith("\n")


def test_sha256_validator_accepts_only_lowercase_sha256():
    assert b5.is_sha256("a" * 64)
    assert not b5.is_sha256("A" * 64)
    assert not b5.is_sha256("bad")


@pytest.mark.parametrize("safe_action", ["read_summary", "compare_claims", "request_review", "emit_report"])
def test_safe_actions_not_blocked_by_boundary_guards(safe_action):
    assert b5.validate_cache_index_action(safe_action)["status"] == b5.PASS
    assert b5.validate_automatic_resolution_action(safe_action)["status"] == b5.PASS
    assert b5.validate_block6_boundary(safe_action)["status"] == b5.PASS
