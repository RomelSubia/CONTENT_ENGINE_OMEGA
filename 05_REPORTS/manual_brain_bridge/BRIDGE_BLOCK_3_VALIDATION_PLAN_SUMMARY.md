# BLOQUE 3 VALIDATION PLAN — Source resolver + integrity guard

Status: PASS  
Result: VALIDATION_PLAN_DEFINED

## Base consumed

- HEAD: a1f9a2af70ef79f0eaf86b88e6ccd863d1bc78c9
- Short HEAD: a1f9a2a
- Subject: Define validation map MANUAL-CEREBRO bridge block 3 source resolver integrity guard
- Required previous status: VALIDATION_MAP_DEFINED

## Validation plan

Validation plan item count: 20

The next validation execution must run:

- py_compile
- pytest collect-only with controlled basetemp
- pytest specific BLOQUE 3
- pytest subsystem manual_brain_bridge
- self-check
- validate-outputs
- canonical JSON/no BOM/final newline audit
- no-touch/no residue audit
- validation result contract audit

## Lifecycle

BLOQUE 3 pasa de:

VALIDATION_MAP_DEFINED

a:

VALIDATION_PLAN_DEFINED

## Not performed yet

Validation execution was NOT performed in this step.

## Still blocked

- validation execution until next step
- execution
- manual/current write
- brain write
- reports/brain write
- n8n
- webhook
- publishing
- CAPA9
- BLOQUE 4

## Next safe step

BLOQUE_3_VALIDATION

Recommended user command:

dame BLOQUE 3 VALIDATION — Source resolver + integrity guard