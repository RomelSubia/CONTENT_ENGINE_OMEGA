# CONTENT ENGINE Ω — HUMAN AUTHORIZATION CONTRACT EXPLANATION v3.6

What v3.6 does:
- Creates a Human Authorization Contract.
- Separates contract from authorization record.
- Sets default state to NO_AUTHORIZATION_INPUT.
- Defines exact phrase contract.
- Defines challenge confirmation contract.
- Defines permission-evaluation-only model.
- Blocks self, implied, memory-based, delegated, global, future, and dangerous authorization attempts.
- Preserves inherited warnings honestly.

Hotfixes:
- Empty authorization text remains REVIEW_REQUIRED at parser level, but no longer blocks build aggregation when it represents safe NO_AUTHORIZATION_INPUT default.
- no_execution=true is treated as a safe token inside the exact phrase contract, not as an execution request.
- Test harness now contains 220 real executed assertions.
- no_execution=false is explicitly expected to LOCK because it is unsafe.
- no_execution=true is treated as safe even when the phrase is incomplete; incomplete phrase remains REVIEW_REQUIRED.

What v3.6 does NOT do:
- No execution.
- No authorization record by default.
- No execution permission.
- No external automation.
- No webhook.
- No n8n.
- No publishing.
- No manual mutation.
- No brain mutation.
- No reports/brain mutation.
- No CAPA 9.
- No production-clean claim.

Final status:
- PASS_WITH_WARNINGS

Next:
- POST_BUILD_AUDIT_V3_6