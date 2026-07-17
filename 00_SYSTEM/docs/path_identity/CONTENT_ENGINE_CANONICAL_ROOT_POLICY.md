# Content Engine Omega - Canonical Root and INITIUM Volume Identity Policy

## Status

Implemented by:

CONTENT_ENGINE_OMEGA_INITIUM_VOLUME_IDENTITY_HARDENING_RECOVERY_AND_COMPLETION_GATE_NO_RUNTIME_NO_ARGOS

## Purpose

This policy prevents Content Engine Omega from being damaged again by Windows drive-letter drift.

## Current canonical root

E:\CONTENT_ENGINE_OMEGA

## Invalid damaged roots

D:\CONTENT_ENGINE_OMEGA
D:/CONTENT_ENGINE_OMEGA

These roots are not valid canonical roots. They are classified as INITIUM drive-letter drift damage.

## Core rule

Content Engine Omega must not trust a drive letter alone.

A valid local root requires all of the following:

1. The root exists.
2. The root contains CONTENT_ENGINE_VOLUME_IDENTITY.json.
3. The identity manifest declares system = CONTENT_ENGINE_OMEGA.
4. The identity manifest declares volume_identity_name = INITIUM.
5. The identity manifest declares drive_letter_is_not_identity = true.
6. The root is not D:\CONTENT_ENGINE_OMEGA or D:/CONTENT_ENGINE_OMEGA.
7. The root does not resolve into ARGOS_BACKCUP.
8. Git branch, upstream and head-family match expected identity.
9. Runtime, ARGOS activation, external interoperability, productive actions and credential access remain blocked unless separately authorized.

## Fail-closed behavior

Content Engine Omega must block operation if:

- INITIUM identity cannot be validated.
- The root is ambiguous.
- The candidate root is D:\CONTENT_ENGINE_OMEGA.
- The candidate root points into ARGOS_BACKCUP.
- Git identity does not match.
- A future script attempts runtime or interop before safe birth authorization.

## Historical evidence exception

Historical evidence may preserve D:\CONTENT_ENGINE_OMEGA references only as non-canonical historical evidence.

Historical evidence must not be rewritten directly during path repair.

## Current permitted hardening files

CONTENT_ENGINE_VOLUME_IDENTITY.json
04_SCRIPTS\powershell\path_identity\Resolve-ContentEngineRoot.ps1
04_SCRIPTS\powershell\path_identity\Test-ContentEnginePathIdentity.ps1
00_SYSTEM\docs\path_identity\CONTENT_ENGINE_CANONICAL_ROOT_POLICY.md
tests\path_identity\test_content_engine_path_identity.ps1

## Remaining gates

1. Static hardening validation gate.
2. Git diff review gate.
3. Commit gate only after explicit authorization.
4. Safe functional birth remains blocked until hardening validates and is committed.