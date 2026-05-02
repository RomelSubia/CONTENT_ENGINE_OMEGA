# CONTENT ENGINE Ω — v3.2.6 WARNING REVIEW OR ACCEPTANCE GATE

STATUS: WARNING_ACCEPTANCE_GATE_ACCEPTED

Audited HEAD before gate:
- 65636b5

Scope:
- Rule Extractor v3.2.6
- Conflict Detector v3.2.6
- Warning acceptance only
- No source mutation
- No manual mutation
- No brain mutation
- No reports/brain mutation
- No external execution

Results:
- Build status: PASS_WITH_WARNINGS
- Post-build audit status: PASS_WITH_WARNINGS_AUDITED
- Runtime validator: PASS_WITH_WARNINGS
- Rules count: 54
- Conflicts count: 0
- Warnings count: 5
- Review required count: 0
- Max rule risk: 70
- Critical rules: 0
- High rules: 34

Warning groups:
- : 5

Accepted warnings:
- WARN-GATE-001: PRODUCTION_CLAIM_WITH_EVIDENCE | risk=30 | decision=PASS_WITH_WARNINGS | acceptance=ACCEPTED_WITH_EVIDENCE_TRACE
- WARN-GATE-002: PRODUCTION_CLAIM_WITH_EVIDENCE | risk=30 | decision=PASS_WITH_WARNINGS | acceptance=ACCEPTED_WITH_EVIDENCE_TRACE
- WARN-GATE-003: PRODUCTION_CLAIM_WITH_EVIDENCE | risk=30 | decision=PASS_WITH_WARNINGS | acceptance=ACCEPTED_WITH_EVIDENCE_TRACE
- WARN-GATE-004: PRODUCTION_CLAIM_WITH_EVIDENCE | risk=30 | decision=PASS_WITH_WARNINGS | acceptance=ACCEPTED_WITH_EVIDENCE_TRACE
- WARN-GATE-005: DUPLICATE_SAME_MEANING | risk=35 | decision=PASS_WITH_WARNINGS | acceptance=ACCEPTED_AS_NON_BLOCKING_DUPLICATE

Gate decision:
- Warnings accepted: true
- Production clean pass: false
- Production with warnings accepted: true
- Hardening required now: false
- Optional clean-pass hardening available: true

Safety:
- Manual current modified: false
- Manual manifest modified: false
- Brain files modified: false
- reports/brain modified: false
- CAPA 9 created: false
- External execution: false
- Test harness: PASS
- Runtime validator: PASS_WITH_WARNINGS

Next:
- V3_2_6_GATE_CLOSURE_OR_NEXT_LAYER_READINESS_MAP