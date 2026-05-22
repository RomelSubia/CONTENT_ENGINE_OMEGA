# CONTENT ENGINE Ω — Content Draft Runtime Governance Core Build

## Resultado

`CONTENT_ENGINE_CONTENT_DRAFT_RUNTIME_GOVERNANCE_CORE_AUTOMATIC_BLOCK_BUILD_FIX_1_PYTEST_BASETEMP_DIRTY_AWARE = PASSED`

## Estado

`CONTENT_DRAFT_RUNTIME_GOVERNANCE_CORE = BUILT_PENDING_POST_AUDIT`

## Fix aplicado

`FIX_1_PYTEST_BASETEMP_DIRTY_AWARE`

## Motivo

El build anterior falló en content_engine suite por PermissionError de pytest temp en Windows.
Este fix usa `--basetemp` repo-local único y limpia `.pytest_runtime`.

## Validado

- dirty allowlist consumida
- source/tests preservados
- static scan
- py_compile
- targeted pytest
- content_engine suite con basetemp repo-local
- runtime contract smoke
- no-touch protected roots
- output scope exact
- manifest/seal

## Sigue bloqueado

- runtime execution
- draft creation
- content generation
- queue write
- publishing
- automation
- n8n / webhook / CAPA9
- manual current
- brain
- reports-brain
- ARGOS bridge build

## Siguiente paso seguro

`CONTENT_ENGINE_CONTENT_DRAFT_RUNTIME_GOVERNANCE_CORE_POST_BUILD_AUDIT`
