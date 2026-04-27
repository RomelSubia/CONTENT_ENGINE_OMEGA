# PHASE 0 v3 - Implementation Governance Lock

## Purpose
This contract establishes the governance boundary for CONTENT_ENGINE_OMEGA before any operational core is built. The implementation is fail-closed and defaults to `DRY_RUN`.

## Mandatory Controls
- Root scope is fixed to `D:\CONTENT_ENGINE_OMEGA`.
- Destructive actions are forbidden.
- Direct delete is forbidden.
- Quarantine is the only allowed removal path in future phases.
- ARGOS access is explicitly forbidden.
- Evidence is required for validation-sensitive transitions.
- Idempotency is required for repeated execution.

## Phase 0 Engines
- Governance Contract Engine
- System State Engine
- State Transition Engine
- Dry Run Enforcement Engine
- Evidence Engine
- Error Severity Engine
- Idempotency Guard
- Root Scope Guard
- ARGOS Isolation Guard
- Action Enforcement Engine
- Quarantine Enforcement Engine
- Phase Validator Engine
- Audit Engine

## Exit Criteria
- JSON governance files exist and are valid.
- `validate_phase0.py` returns `PHASE_0_VALIDATION: PASS`.
- `Validate-Phase0.ps1` returns `PHASE 0 AUDIT: PASS`.
- Repository sync is verified, or the system is placed into `REVIEW_REQUIRED` if `origin` is not configured.
