# CONTENT ENGINE Ω — v3.2.6 POST-BUILD AUDIT

STATUS: PASS_WITH_WARNINGS_AUDITED

Audited HEAD:
- 5da7353

Scope:
- Rule Extractor v3.2.6
- Conflict Detector v3.2.6
- Manual ↔ Cerebro bridge reports
- Manifest and seal
- Test harness
- Runtime validator re-run
- No-touch audit

Results:
- Build status: PASS_WITH_WARNINGS
- Build reason: PASS_WITH_WARNINGS_STATE
- Rules count: 54
- Conflicts count: 0
- Warnings count: 5
- Review required count: 0
- Max rule risk: 70
- Critical rules: 0
- High rules: 34

Warning groups:
- PRODUCTION_CLAIM_WITH_EVIDENCE: 4
- DUPLICATE_SAME_MEANING: 1

Safety:
- Manual current modified: false
- Manual manifest modified: false
- Brain files modified: false
- reports/brain modified: false
- CAPA 9 created: false
- External execution: false
- Dry-run bridge behavior: preserved

Audit verdict:
- Post-build audit closed: true
- Production clean pass: False
- Production with warnings: True

Next:
- V3_2_6_WARNING_REVIEW_OR_ACCEPTANCE_GATE