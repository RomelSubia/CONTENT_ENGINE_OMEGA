# CONTENT ENGINE Ω — MANUAL ↔ CEREBRO BRIDGE v3.2.6

STATUS: PASS_WITH_WARNINGS
REASON: PASS_WITH_WARNINGS_STATE

Correction:
- Fixed contamination false positive caused by PowerShell -like wildcard matching.
- Replaced wildcard pattern matching with literal IndexOf comparison.
- Preserves valid governance tokens such as [FAIL CLOSED], BLOCK, LOCK, PASS, CURRENT_VALID, READ_ONLY.
- Preserves real console-noise blocking.
- Preserved v3.2.5 extractor, detector and risk scoring logic.
- Preserved v2.1.3 baseline and no-touch gates.

Safety:
- Dry run: true
- Brain mutation: false
- Manual mutation: false
- reports/brain write: false
- CAPA 9 creation: false
- External execution: false

Counts:
- Rules: 54
- Conflicts: 0
- Warnings: 5
- Review required: 0
- Max rule risk: 70
- Critical rules: 0
- High rules: 34

Commit allowed:
- True

Next:
- Analyze v3.2.6 output before advancing.