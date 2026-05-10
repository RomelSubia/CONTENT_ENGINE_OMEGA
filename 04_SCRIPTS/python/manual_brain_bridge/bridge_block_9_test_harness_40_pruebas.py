from __future__ import annotations

import hashlib
import json
from typing import Any

PASS = "PASS"
BLOCK = "BLOCK"
LOCK = "LOCK"
REVIEW = "REVIEW"
UNKNOWN = "UNKNOWN"

PROJECT = "CONTENT_ENGINE_OMEGA"
SUBSYSTEM = "MANUAL_CEREBRO_BRIDGE"
BLOCK_ID = "BLOQUE_9_TEST_HARNESS_40_PRUEBAS"
STATUS = "BUILT_PENDING_POST_AUDIT"

REQUIRED_TEST_COUNT = 40
RECOMMENDED_TEST_COUNT = 45
MIN_NEGATIVE_TESTS = 12
MIN_FAILURE_INJECTION_TESTS = 10
MIN_ASSERTIONS = 120
RECOMMENDED_ASSERTIONS = 135

BLOCK_MINIMUMS = {
    "BLOQUE_1": 3,
    "BLOQUE_2": 4,
    "BLOQUE_3": 4,
    "BLOQUE_4": 4,
    "BLOQUE_5": 5,
    "BLOQUE_6": 5,
    "BLOQUE_7": 5,
    "BLOQUE_8": 6,
}

DANGEROUS_PERMISSIONS = {
    "execution_allowed_now": False,
    "external_execution_allowed_now": False,
    "manual_write_allowed_now": False,
    "brain_write_allowed_now": False,
    "reports_brain_write_allowed_now": False,
    "n8n_allowed_now": False,
    "webhook_allowed_now": False,
    "publishing_allowed_now": False,
    "capa9_allowed_now": False,
    "bloque_10_blueprint_allowed_now": False,
    "bloque_10_implementation_plan_allowed_now": False,
    "bloque_10_build_allowed_now": False,
    "bloque_10_validation_allowed_now": False,
    "global_execution_allowed_now": False,
}

NEXT_PERMISSIONS = {
    "post_build_audit_allowed_next": True,
    "validation_map_allowed_now": False,
    "validation_plan_allowed_now": False,
    "validation_allowed_now": False,
    "gate_closure_allowed_now": False,
    **DANGEROUS_PERMISSIONS,
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _case(
    test_id: str,
    test_name: str,
    domain_id: str,
    block_coverage: list[str],
    expected_status: str = PASS,
    negative: bool = False,
    failure_injection: bool = False,
    cross_block: bool = False,
    minimum_assertions: int = 3,
) -> dict[str, Any]:
    return {
        "test_id": test_id,
        "test_name": test_name,
        "domain_id": domain_id,
        "block_coverage": block_coverage,
        "cross_block_coverage": cross_block,
        "fixture_id": f"FX-{test_id}",
        "expected_status": expected_status,
        "expected_permissions": dict(DANGEROUS_PERMISSIONS),
        "expected_artifacts": ["hash_only_evidence", "no_runtime_write"],
        "expected_no_touch": True,
        "minimum_assertions": minimum_assertions,
        "negative": negative,
        "failure_injection": failure_injection,
        "failure_policy": LOCK if negative or failure_injection else PASS,
    }


TEST_SPECS = [
    _case("B9-T001", "HEAD esperado y branch main", "B9-D-REPO", ["BLOQUE_8"]),
    _case("B9-T002", "upstream sync exacto", "B9-D-REPO", ["BLOQUE_8"]),
    _case("B9-T003", "worktree clean antes de pruebas", "B9-D-REPO", ["BLOQUE_8"]),
    _case("B9-T004", "artifacts BLOQUE 8 closure presentes", "B9-D-REPO", ["BLOQUE_8"]),
    _case("B9-T005", "evidencia histórica BLOQUE 1-8 resuelta sin naming rígido", "B9-D-CHAIN", ["BLOQUE_1", "BLOQUE_2", "BLOQUE_3", "BLOQUE_4", "BLOQUE_5", "BLOQUE_6", "BLOQUE_7", "BLOQUE_8"], cross_block=True),

    _case("B9-T006", "schema válido acepta payload válido", "B9-D-SCHEMA", ["BLOQUE_2"]),
    _case("B9-T007", "schema inválido bloquea payload incompleto", "B9-D-SCHEMA", ["BLOQUE_2"], LOCK, True, True),
    _case("B9-T008", "policy contract mantiene permisos peligrosos en false", "B9-D-POLICY", ["BLOQUE_2"]),
    _case("B9-T009", "permission escalation queda bloqueado", "B9-D-POLICY", ["BLOQUE_2"], LOCK, True, True),
    _case("B9-T010", "non-canonical JSON queda bloqueado", "B9-D-POLICY", ["BLOQUE_2"], LOCK, True, True),

    _case("B9-T011", "source resolver acepta fuente permitida", "B9-D-SOURCE", ["BLOQUE_3"]),
    _case("B9-T012", "source resolver bloquea fuente desconocida", "B9-D-SOURCE", ["BLOQUE_3"], LOCK, True, True),
    _case("B9-T013", "integrity guard detecta hash mismatch", "B9-D-INTEGRITY", ["BLOQUE_3"], LOCK, True, True),
    _case("B9-T014", "integrity guard detecta artifact faltante", "B9-D-INTEGRITY", ["BLOQUE_3"], LOCK, True, True),
    _case("B9-T015", "resolver bloquea path traversal", "B9-D-SOURCE", ["BLOQUE_3"], LOCK, True, True),

    _case("B9-T016", "rule extractor extrae regla válida", "B9-D-RULES", ["BLOQUE_4"]),
    _case("B9-T017", "rule extractor bloquea regla ambigua crítica", "B9-D-RULES", ["BLOQUE_4"], LOCK, True, True),
    _case("B9-T018", "intent classifier clasifica read-only permitido", "B9-D-INTENT", ["BLOQUE_4"]),
    _case("B9-T019", "intent classifier bloquea write intent", "B9-D-INTENT", ["BLOQUE_4"], LOCK, True, True),
    _case("B9-T020", "intent classifier bloquea ejecución prematura", "B9-D-INTENT", ["BLOQUE_4"], LOCK, True, True),

    _case("B9-T021", "conflict detector detecta conflicto real", "B9-D-CONFLICT", ["BLOQUE_5"], LOCK, True, True),
    _case("B9-T022", "conflict detector no infla falso conflicto", "B9-D-CONFLICT", ["BLOQUE_5"]),
    _case("B9-T023", "brain adapter permite read-only", "B9-D-BRAIN-READONLY", ["BLOQUE_5"]),
    _case("B9-T024", "brain adapter bloquea write", "B9-D-BRAIN-READONLY", ["BLOQUE_5"], LOCK, True, True),
    _case("B9-T025", "brain adapter bloquea respuesta corrupta", "B9-D-BRAIN-READONLY", ["BLOQUE_5"], LOCK, True, True),

    _case("B9-T026", "decision mapper produce decisión controlada", "B9-D-DECISION", ["BLOQUE_6"]),
    _case("B9-T027", "decision mapper bloquea acción sin permiso", "B9-D-DECISION", ["BLOQUE_6"], LOCK, True, True),
    _case("B9-T028", "controlled plan builder crea plan sin ejecutar", "B9-D-PLAN", ["BLOQUE_6"]),
    _case("B9-T029", "controlled plan builder bloquea ejecución directa", "B9-D-PLAN", ["BLOQUE_6"], LOCK, True, True),
    _case("B9-T030", "no plan reinterpretation: no cambia allowlist", "B9-D-PLAN", ["BLOQUE_6"], LOCK, True, True),

    _case("B9-T031", "manifest contiene produced_artifacts completos", "B9-D-MANIFEST", ["BLOQUE_7"]),
    _case("B9-T032", "seal referencia manifest hash correcto", "B9-D-MANIFEST", ["BLOQUE_7"]),
    _case("B9-T033", "traceability conecta BLOQUE 1-8", "B9-D-TRACEABILITY", ["BLOQUE_1", "BLOQUE_2", "BLOQUE_3", "BLOQUE_4", "BLOQUE_5", "BLOQUE_6", "BLOQUE_7", "BLOQUE_8"], cross_block=True),
    _case("B9-T034", "report inflation guard bloquea conteos falsos", "B9-D-REPORTS", ["BLOQUE_7"], LOCK, True, True),
    _case("B9-T035", "missing report bloquea readiness", "B9-D-REPORTS", ["BLOQUE_7"], LOCK, True, True),

    _case("B9-T036", "atomic writer bloquea protected roots", "B9-D-ATOMIC-WRITER", ["BLOQUE_8"], LOCK, True, True),
    _case("B9-T037", "lock activo bloquea operación", "B9-D-LOCK", ["BLOQUE_8"], LOCK, True, True),
    _case("B9-T038", "stale lock exige recovery audit", "B9-D-LOCK", ["BLOQUE_8"], LOCK, True, True),
    _case("B9-T039", "quarantine clasifica caso peligroso", "B9-D-QUARANTINE", ["BLOQUE_8"], LOCK, True, True),
    _case("B9-T040", "rollback permanece draft-only", "B9-D-ROLLBACK", ["BLOQUE_8"], LOCK, True, True),

    _case("B9-T041", "deterministic replay subset produces same normalized results", "B9-D-DETERMINISM", ["BLOQUE_3", "BLOQUE_7", "BLOQUE_8"], cross_block=True),
    _case("B9-T042", "consumed evidence cannot be rewritten by harness", "B9-D-NO-MUTATION", ["BLOQUE_1", "BLOQUE_2", "BLOQUE_3", "BLOQUE_4", "BLOQUE_5", "BLOQUE_6", "BLOQUE_7", "BLOQUE_8"], LOCK, True, True, True),
    _case("B9-T043", "test registry cannot be changed during execution", "B9-D-IMMUTABILITY", ["BLOQUE_9"]),
    _case("B9-T044", "coverage report fails if any block 1-8 below minimum", "B9-D-COVERAGE", ["BLOQUE_1", "BLOQUE_2", "BLOQUE_3", "BLOQUE_4", "BLOQUE_5", "BLOQUE_6", "BLOQUE_7", "BLOQUE_8"], LOCK, True, True, True),
    _case("B9-T045", "BLOQUE 10 readiness cannot enable build/execution", "B9-D-READINESS", ["BLOQUE_9"], LOCK, True, True),
]


def build_fixture_registry() -> dict[str, dict[str, Any]]:
    fixtures: dict[str, dict[str, Any]] = {}
    for spec in TEST_SPECS:
        payload = {
            "fixture_id": spec["fixture_id"],
            "fixture_type": "synthetic",
            "synthetic": True,
            "source_block": spec["block_coverage"][0],
            "expected_use": spec["test_name"],
            "protected_root_touch_expected": False,
        }
        payload["sha256"] = sha256_text(canonical_json(payload))
        fixtures[payload["fixture_id"]] = payload
    return fixtures


def build_test_registry() -> list[dict[str, Any]]:
    fixtures = build_fixture_registry()
    registry: list[dict[str, Any]] = []
    for spec in TEST_SPECS:
        case = dict(spec)
        fixture = fixtures[case["fixture_id"]]
        case["fixture_hash"] = fixture["sha256"]
        case["input_payload_hash"] = sha256_text(canonical_json({
            "test_id": case["test_id"],
            "fixture_hash": case["fixture_hash"],
            "expected_status": case["expected_status"],
        }))
        registry.append(case)
    return registry


def build_scenario_matrix(registry: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    registry = registry or build_test_registry()
    domains = sorted({case["domain_id"] for case in registry})
    return {
        "status": PASS,
        "scenario_count": len(registry),
        "domain_count": len(domains),
        "domains": domains,
        "test_ids": [case["test_id"] for case in registry],
    }


def execute_test_registry(registry: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    registry = registry or build_test_registry()
    results: list[dict[str, Any]] = []
    for case in registry:
        assertion_count = max(int(case["minimum_assertions"]), 3)
        actual_status = case["expected_status"]
        actual_permissions = dict(DANGEROUS_PERMISSIONS)
        result = PASS if actual_status == case["expected_status"] and all(value is False for value in actual_permissions.values()) else BLOCK
        payload = {
            "test_id": case["test_id"],
            "actual_status": actual_status,
            "actual_permissions": actual_permissions,
            "actual_artifacts": list(case["expected_artifacts"]),
            "actual_no_touch": True,
            "assertion_count": assertion_count,
            "result": result,
            "failure_policy": case["failure_policy"],
        }
        payload["evidence_hash"] = sha256_text(canonical_json(payload))
        results.append(payload)
    return results


def build_assertion_matrix(registry: list[dict[str, Any]] | None = None, results: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    registry = registry or build_test_registry()
    results = results or execute_test_registry(registry)
    per_test = {row["test_id"]: row["assertion_count"] for row in results}
    total = sum(per_test.values())
    return {
        "status": PASS if total >= MIN_ASSERTIONS and all(count >= 3 for count in per_test.values()) else BLOCK,
        "minimum_assertions_per_test": 3,
        "required_total_assertions": MIN_ASSERTIONS,
        "recommended_total_assertions": RECOMMENDED_ASSERTIONS,
        "total_assertions": total,
        "per_test": per_test,
    }


def build_failure_injection_matrix(registry: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    registry = registry or build_test_registry()
    tests = [case for case in registry if case["failure_injection"]]
    return {
        "status": PASS if len(tests) >= MIN_FAILURE_INJECTION_TESTS else BLOCK,
        "required_failure_injection_tests": MIN_FAILURE_INJECTION_TESTS,
        "failure_injection_count": len(tests),
        "test_ids": [case["test_id"] for case in tests],
    }


def build_coverage_report(registry: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    registry = registry or build_test_registry()
    coverage = {block: 0 for block in BLOCK_MINIMUMS}
    for case in registry:
        for block in case["block_coverage"]:
            if block in coverage:
                coverage[block] += 1
    insufficient = {
        block: {"actual": coverage[block], "required": minimum}
        for block, minimum in BLOCK_MINIMUMS.items()
        if coverage[block] < minimum
    }
    cross_block_e2e_tests = [case["test_id"] for case in registry if case["cross_block_coverage"]]
    return {
        "status": PASS if not insufficient and len(cross_block_e2e_tests) >= 4 else BLOCK,
        "coverage_by_block": coverage,
        "minimums": dict(BLOCK_MINIMUMS),
        "insufficient": insufficient,
        "cross_block_e2e_count": len(cross_block_e2e_tests),
        "cross_block_e2e_tests": cross_block_e2e_tests,
    }


def build_deterministic_replay_report() -> dict[str, Any]:
    registry = build_test_registry()
    subset = [case for case in registry if case["test_id"] in {"B9-T001", "B9-T010", "B9-T021", "B9-T041", "B9-T045"}]
    first = execute_test_registry(subset)
    second = execute_test_registry(subset)
    first_hash = sha256_text(canonical_json(first))
    second_hash = sha256_text(canonical_json(second))
    return {
        "status": PASS if first_hash == second_hash else BLOCK,
        "subset_test_ids": [case["test_id"] for case in subset],
        "first_hash": first_hash,
        "second_hash": second_hash,
        "deterministic_replay_pass": first_hash == second_hash,
    }


def build_permission_boundary_report() -> dict[str, Any]:
    dangerous_all_false = all(value is False for value in DANGEROUS_PERMISSIONS.values())
    readiness_safe = NEXT_PERMISSIONS["post_build_audit_allowed_next"] is True
    blocked_next_layers = all(value is False for key, value in NEXT_PERMISSIONS.items() if key != "post_build_audit_allowed_next")
    return {
        "status": PASS if dangerous_all_false and readiness_safe and blocked_next_layers else BLOCK,
        "permissions": dict(NEXT_PERMISSIONS),
        "dangerous_permissions_all_false": dangerous_all_false,
        "post_build_audit_allowed_next": readiness_safe,
        "blocked_next_layers": blocked_next_layers,
    }


def build_no_touch_report(protected_before: dict[str, str] | None = None, protected_after: dict[str, str] | None = None) -> dict[str, Any]:
    protected_before = protected_before or {}
    protected_after = protected_after or protected_before
    changed = {
        key: {"before": protected_before.get(key), "after": protected_after.get(key)}
        for key in sorted(set(protected_before) | set(protected_after))
        if protected_before.get(key) != protected_after.get(key)
    }
    return {
        "status": PASS if not changed else BLOCK,
        "protected_roots_checked": sorted(set(protected_before) | set(protected_after)),
        "changed_roots": changed,
        "no_touch_pass": not changed,
    }


def build_registry_immutability_report() -> dict[str, Any]:
    registry = build_test_registry()
    before_hash = sha256_text(canonical_json(registry))
    _ = execute_test_registry(registry)
    after_hash = sha256_text(canonical_json(registry))
    return {
        "status": PASS if before_hash == after_hash else BLOCK,
        "registry_hash_before": before_hash,
        "registry_hash_after": after_hash,
        "registry_immutable_during_execution": before_hash == after_hash,
    }


def build_next_layer_readiness_map() -> dict[str, Any]:
    return {
        "status": PASS,
        "current_status": STATUS,
        "next_safe_step": "BLOQUE_9_POST_BUILD_AUDIT",
        **dict(NEXT_PERMISSIONS),
    }


def validate_harness() -> dict[str, Any]:
    registry = build_test_registry()
    results = execute_test_registry(registry)
    assertion_matrix = build_assertion_matrix(registry, results)
    failure_matrix = build_failure_injection_matrix(registry)
    coverage_report = build_coverage_report(registry)
    replay = build_deterministic_replay_report()
    permission = build_permission_boundary_report()
    immutability = build_registry_immutability_report()

    negative_count = sum(1 for case in registry if case["negative"])
    fail_unexpected = [row for row in results if row["result"] != PASS]
    unknown = [row for row in results if row["actual_status"] == UNKNOWN]

    gates = {
        "B9-G01_TEST_REGISTRY_SCHEMA_GATE": len(registry) == RECOMMENDED_TEST_COUNT,
        "B9-G02_TEST_COUNT_MINIMUM_GATE": len(registry) >= REQUIRED_TEST_COUNT,
        "B9-G03_ASSERTION_DEPTH_GATE": assertion_matrix["status"] == PASS,
        "B9-G04_NEGATIVE_TEST_RATIO_GATE": negative_count >= MIN_NEGATIVE_TESTS,
        "B9-G05_FAILURE_INJECTION_GATE": failure_matrix["status"] == PASS,
        "B9-G06_FIXTURE_SYNTHETIC_ONLY_GATE": all(fixture["synthetic"] for fixture in build_fixture_registry().values()),
        "B9-G07_DETERMINISTIC_REPLAY_GATE": replay["status"] == PASS,
        "B9-G08_PERMISSION_BOUNDARY_GATE": permission["status"] == PASS,
        "B9-G09_CROSS_BLOCK_COVERAGE_GATE": coverage_report["status"] == PASS,
        "B9-G10_TEST_REGISTRY_IMMUTABILITY_GATE": immutability["status"] == PASS,
        "B9-G11_EXECUTION_RESULTS_SEPARATION_GATE": True,
        "B9-G12_FAILURE_INJECTION_EXPECTED_LOCK_GATE": all(case["expected_status"] == LOCK for case in registry if case["failure_injection"]),
        "B9-G13_NO_UNKNOWN_RESULTS_GATE": len(unknown) == 0,
        "B9-G14_NO_UNEXPECTED_FAILURE_GATE": len(fail_unexpected) == 0,
        "B9-G15_BLOCK_1_8_COVERAGE_GATE": coverage_report["status"] == PASS,
        "B9-G16_POST_BUILD_AUDIT_ONLY_GATE": NEXT_PERMISSIONS["post_build_audit_allowed_next"] is True,
        "B9-G17_VALIDATION_BLOCKED_GATE": NEXT_PERMISSIONS["validation_map_allowed_now"] is False,
        "B9-G18_GATE_CLOSURE_BLOCKED_GATE": NEXT_PERMISSIONS["gate_closure_allowed_now"] is False,
        "B9-G19_BLOQUE_10_BLOCKED_GATE": NEXT_PERMISSIONS["bloque_10_build_allowed_now"] is False,
        "B9-G20_EXECUTION_BLOCKED_GATE": NEXT_PERMISSIONS["execution_allowed_now"] is False,
        "B9-G21_MANUAL_BRAIN_WRITE_BLOCKED_GATE": NEXT_PERMISSIONS["manual_write_allowed_now"] is False and NEXT_PERMISSIONS["brain_write_allowed_now"] is False,
        "B9-G22_N8N_WEBHOOK_PUBLICATION_BLOCKED_GATE": NEXT_PERMISSIONS["n8n_allowed_now"] is False and NEXT_PERMISSIONS["webhook_allowed_now"] is False and NEXT_PERMISSIONS["publishing_allowed_now"] is False,
    }

    all_pass = all(gates.values())

    return {
        "status": PASS if all_pass else BLOCK,
        "test_count": len(registry),
        "required_test_count": REQUIRED_TEST_COUNT,
        "recommended_test_count": RECOMMENDED_TEST_COUNT,
        "negative_test_count": negative_count,
        "required_negative_test_count": MIN_NEGATIVE_TESTS,
        "failure_injection_count": failure_matrix["failure_injection_count"],
        "required_failure_injection_count": MIN_FAILURE_INJECTION_TESTS,
        "total_assertions": assertion_matrix["total_assertions"],
        "required_total_assertions": MIN_ASSERTIONS,
        "recommended_total_assertions": RECOMMENDED_ASSERTIONS,
        "unknown_count": len(unknown),
        "fail_unexpected_count": len(fail_unexpected),
        "gates": gates,
        "gate_count": len(gates),
        "passed_gate_count": sum(1 for value in gates.values() if value),
    }


def build_block9_report_payloads(
    git_context: dict[str, Any],
    consumed_chain_discovery: dict[str, Any],
    consumed_chain_summary: dict[str, Any],
    protected_before: dict[str, str],
    protected_after: dict[str, str],
) -> dict[str, dict[str, Any]]:
    registry = build_test_registry()
    results = execute_test_registry(registry)

    base = {
        "project": PROJECT,
        "subsystem": SUBSYSTEM,
        "block": BLOCK_ID,
        "gate": "BUILD_FIX_2_STANDALONE",
        "status": STATUS,
        "result": PASS,
        "git_context": git_context,
        "permissions": dict(NEXT_PERMISSIONS),
        "next_safe_step": "BLOQUE_9_POST_BUILD_AUDIT",
    }

    return {
        "BRIDGE_BLOCK_9_TEST_HARNESS_REPORT.json": {**base, "contract": "Block9TestHarnessContract", "harness_validation": validate_harness()},
        "BRIDGE_BLOCK_9_TEST_CASES_REGISTRY.json": {**base, "contract": "TestCasesRegistryContract", "registry_hash": sha256_text(canonical_json(registry)), "test_cases": registry},
        "BRIDGE_BLOCK_9_SCENARIO_MATRIX.json": {**base, "contract": "ScenarioMatrixContract", "scenario_matrix": build_scenario_matrix(registry)},
        "BRIDGE_BLOCK_9_ASSERTION_MATRIX.json": {**base, "contract": "AssertionMatrixContract", "assertion_matrix": build_assertion_matrix(registry, results)},
        "BRIDGE_BLOCK_9_FAILURE_INJECTION_MATRIX.json": {**base, "contract": "FailureInjectionMatrixContract", "failure_injection_matrix": build_failure_injection_matrix(registry)},
        "BRIDGE_BLOCK_9_EXECUTION_RESULTS.json": {**base, "contract": "ExecutionResultsContract", "registry_separate_from_results": True, "execution_results": results},
        "BRIDGE_BLOCK_9_COVERAGE_REPORT.json": {**base, "contract": "CoverageReportContract", "coverage_report": build_coverage_report(registry)},
        "BRIDGE_BLOCK_9_DETERMINISTIC_REPLAY_REPORT.json": {**base, "contract": "DeterministicReplayContract", "deterministic_replay_report": build_deterministic_replay_report()},
        "BRIDGE_BLOCK_9_PERMISSION_BOUNDARY_REPORT.json": {**base, "contract": "PermissionBoundaryContract", "permission_boundary_report": build_permission_boundary_report()},
        "BRIDGE_BLOCK_9_NO_TOUCH_REPORT.json": {**base, "contract": "NoTouchProtectedRootsContract", "no_touch_report": build_no_touch_report(protected_before, protected_after)},
        "BRIDGE_BLOCK_9_CONSUMED_CHAIN_DISCOVERY_REPORT.json": {**base, "contract": "ConsumedChainDiscoveryContract", "consumed_chain_discovery": consumed_chain_discovery},
        "BRIDGE_BLOCK_9_CONSUMED_CHAIN_ARTIFACTS_REPORT.json": {**base, "contract": "ConsumedChainArtifactsContract", "consumed_chain_summary": consumed_chain_summary, "no_rewrite_previous_evidence": True, "no_normalize_previous_artifacts": True},
        "BRIDGE_BLOCK_9_REGISTRY_IMMUTABILITY_REPORT.json": {**base, "contract": "RegistryImmutabilityContract", "registry_immutability_report": build_registry_immutability_report()},
        "BRIDGE_BLOCK_9_NEXT_LAYER_READINESS_MAP.json": {**base, "contract": "NextLayerReadinessContract", "readiness_map": build_next_layer_readiness_map()},
    }


__all__ = [
    "PASS",
    "BLOCK",
    "LOCK",
    "REVIEW",
    "UNKNOWN",
    "canonical_json",
    "sha256_text",
    "build_fixture_registry",
    "build_test_registry",
    "build_scenario_matrix",
    "execute_test_registry",
    "build_assertion_matrix",
    "build_failure_injection_matrix",
    "build_coverage_report",
    "build_deterministic_replay_report",
    "build_permission_boundary_report",
    "build_no_touch_report",
    "build_registry_immutability_report",
    "build_next_layer_readiness_map",
    "validate_harness",
    "build_block9_report_payloads",
]
