# CONTENT ENGINE Ω — POST-BUILD AUDIT v3.5

STATUS: PASS_WITH_WARNINGS  
REASON: POST_BUILD_AUDIT_PASS_WITH_INHERITED_WARNINGS

Audited layer:
- Controlled Action Handoff
- Non-Executable Action Review Queue

Evidence:
- Runtime validator: PASS_WITH_WARNINGS
- Test harness: T001-T150 PASS
- Tests total: 150
- Tests passed: 150
- Manifest + seal audit: PASS
- Source runtime scan: PASS
- No-touch audit: PASS

Safety confirmed:
- execution_allowed: false
- external_execution_allowed: false
- manual_write_allowed: false
- brain_write_allowed: false
- reports_brain_write_allowed: false
- auto_action_allowed: false
- queue_operational: false
- queue_executable: false
- queue_runtime_binding: false
- approved_by_human: false
- approval_processing_supported: false
- CAPA 9 created: false

Warnings:
- warnings_inherited_visible: 5
- warnings_hidden: 0
- warnings_resolved_by_v3_5: 0
- production_clean_pass: false
- production_with_warnings: true

Next official step:
- WARNING_REVIEW_OR_ACCEPTANCE_GATE_V3_5