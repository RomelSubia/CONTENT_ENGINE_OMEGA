# CONTENT ENGINE Ω — MVP1 READ-ONLY HUD TECHNICAL PLAN V5.1-R2

## 1. Formal status

Status: TECHNICAL_PLAN_PREPARED_NO_BUILD  
Version: V5.1-R2  
Scope: MVP1_READ_ONLY_HUD_TECHNICAL_PLAN  
Construction status: NOT_STARTED  
Runtime status: NOT_EXECUTED  
ARGOS status: NOT_ACTIVATED  
Productive actions: NOT_AUTHORIZED  
Credentials: NOT_ACCESSED  

This document defines the technical plan for the future controlled construction of the Content Engine Ω MVP1 read-only HUD.

This plan does not authorize implementation, build, runtime, ARGOS activation, productive actions, credential access, commit, amend, or push.

---

## 2. Objective

Prepare the safe technical path for the MVP1 read-only HUD.

The MVP1 read-only HUD must display controlled system status without mutating project state.

The MVP1 must remain a visibility layer only.

It must not act as an execution engine.

It must not become ARGOS.

It must not trigger runtime behavior.

It must not connect to credentials, publishing tools, payment systems, external production integrations, or destructive scripts.

---

## 3. MVP1 read-only HUD purpose

The MVP1 HUD exists to show:

1. Current system identity.
2. Current blueprint status.
3. Current guard status.
4. Evidence status.
5. Main blocker or risk.
6. Reality level.
7. Next safe step.
8. Required authorization.
9. Communication mode.
10. Basic audit trail.

The HUD must help the user understand the state of Content Engine Ω without allowing accidental execution.

---

## 4. Proposed MVP1 modules

### 4.1 State Reader Module

Purpose:
Read approved local state documents and expose a normalized status object.

Allowed read sources:
- 00_MANUAL/content_engine/blueprints/CURRENT_BLUEPRINT_STATUS.json
- 00_MANUAL/content_engine/build_transition/CURRENT_PRE_BUILD_TRANSITION_GUARD_STATUS.json
- Future approved read-only status files.

Blocked:
- No environment variables.
- No credentials.
- No external APIs.
- No runtime activation.
- No ARGOS paths.

### 4.2 Blueprint Status Panel

Purpose:
Display the current blueprint identity, status, manual status, version, and hash if available.

Required behavior:
- Read-only.
- Fail closed if status file is missing or malformed.
- Show "UNKNOWN / REVIEW_REQUIRED" instead of guessing.

### 4.3 Guard Status Panel

Purpose:
Display the current pre-build guard state.

Required behavior:
- Show build authorization status.
- Show runtime authorization status.
- Show ARGOS authorization status.
- Show productive-action authorization status.
- Show credential authorization status.
- Treat any missing authorization flag as blocked.

### 4.4 Evidence Status Panel

Purpose:
Display whether expected evidence directories and reports exist.

Required behavior:
- Read-only filesystem check.
- No deletion.
- No creation during runtime.
- No cleanup.
- No archival mutation.

### 4.5 Risk / Blocker Panel

Purpose:
Show the most important active blocker or risk.

Initial expected risks:
- Future source boundary not yet applied.
- Patch preview not yet executed.
- Rollback not yet executed.

Required behavior:
- Show risk as planning state, not failure, until build preparation begins.

### 4.6 Next Safe Step Panel

Purpose:
Display the next allowed gate.

Expected next safe steps after this plan:
- REVIEW_MVP1_READ_ONLY_HUD_TECHNICAL_PLAN_AND_DECIDE_IF_COMMIT_IS_REQUIRED
- Later, only if authorized: PATCH_PREVIEW_MVP1_READ_ONLY_HUD_V5_1_R2_NO_APPLY
- Later, only if authorized: APPLY_CONTROLLED_PATCH_MVP1_READ_ONLY_HUD_V5_1_R2

### 4.7 Authorization Banner

Purpose:
Clearly show what is authorized and what is blocked.

Required behavior:
- Default: everything is blocked unless explicitly authorized.
- Never interpret "ready" as "authorized".
- Never interpret "planned" as "executed".

### 4.8 Audit Record Panel

Purpose:
Display last known audit/seal references.

Required behavior:
- Read-only.
- No git mutation.
- No commit.
- No push.

---

## 5. Candidate implementation paths for future build

The technical plan recommends the following future candidate source boundary.

Future source boundary candidate:
- src/content_engine_omega/mvp1_read_only_hud/

Future test boundary candidate:
- tests/content_engine_omega/mvp1_read_only_hud/

Future documentation boundary candidate:
- 00_MANUAL/content_engine/mvp1_read_only_hud/

Future evidence boundary candidate:
- 05_REPORTS/content_engine/mvp1_read_only_hud/

Important:
These paths are only candidates at this stage.

No source code is created by this plan.

No tests are created by this plan.

No build is executed by this plan.

---

## 6. File boundary rules for future patch preview

A future patch preview may only propose files inside these boundaries:

Allowed future build paths:
- src/content_engine_omega/mvp1_read_only_hud/
- tests/content_engine_omega/mvp1_read_only_hud/
- 00_MANUAL/content_engine/mvp1_read_only_hud/
- 05_REPORTS/content_engine/mvp1_read_only_hud/

Blocked paths unless separately authorized:
- ARGOS runtime paths.
- Credential files.
- Environment secret files.
- External publishing integrations.
- Payment or monetization execution files.
- Production deployment files.
- Destructive cleanup scripts.
- Unrelated project paths.
- Existing blueprint source files.
- Existing sealed guard files.

---

## 7. No-runtime criteria

The MVP1 technical plan and future patch preview must satisfy:

1. No application server start.
2. No background process.
3. No daemon.
4. No watcher.
5. No scheduler.
6. No browser launch.
7. No external service call.
8. No API call.
9. No live user interface execution.
10. No automatic command execution.

A future implementation may contain code, but it must not be run unless a separate runtime authorization is issued.

---

## 8. No-ARGOS criteria

The MVP1 read-only HUD is not ARGOS.

The MVP1 must not:
- Activate ARGOS.
- Import ARGOS runtime modules.
- Execute ARGOS commands.
- Read ARGOS credentials.
- Control the computer.
- Trigger voice, wake word, command routing, or administrator authorization flows.
- Present itself as ARGOS.

The MVP1 may reference ARGOS only as a blocked external system if relevant to system governance.

---

## 9. No-productive-actions criteria

The MVP1 must not:
- Publish content.
- Send messages.
- Modify external systems.
- Access client data.
- Trigger monetization workflows.
- Delete files.
- Move files.
- Rename files.
- Modify sealed source-of-truth documents.
- Push to Git.
- Commit to Git.
- Amend commits.
- Force push.

---

## 10. Credential safety criteria

The MVP1 must not:
- Read .env files.
- Read credential stores.
- Request tokens.
- Print secrets.
- Access browser sessions.
- Access cloud secrets.
- Access GitHub tokens.
- Access payment credentials.
- Access email credentials.

Any credential-related requirement must be treated as blocked and moved to a separate future authorization gate.

---

## 11. Patch preview strategy

Before any future implementation is applied:

1. Generate a patch preview only.
2. Do not apply the patch in the preview gate.
3. Validate that every file path is inside the allowed boundary.
4. Validate that no ARGOS, credential, production, destructive, or unrelated path is touched.
5. Run a patch apply check only if authorized.
6. Produce a summary of intended changes.
7. Produce rollback notes.
8. Wait for explicit authorization before applying.

Required future preview classification:
PATCH_PREVIEW_READY_FOR_USER_REVIEW_NO_APPLY_NO_BUILD_NO_RUNTIME_NO_ARGOS

---

## 12. Preliminary rollback strategy

Before any future controlled patch apply:

1. Record current HEAD.
2. Record git status.
3. Record list of files that will be created or modified.
4. Confirm no unrelated working tree changes exist.
5. Prepare rollback command notes.
6. Avoid destructive rollback unless explicitly authorized.
7. Prefer git-based rollback for files introduced by the patch.
8. If new files are created, rollback must list each new file path.

Rollback must be documented before build mutation begins.

---

## 13. Evidence requirements

Future gates should preserve evidence for:

1. Authorization record.
2. Repository state before action.
3. Blueprint hash.
4. Guard hash.
5. File boundary validation.
6. Patch preview summary.
7. Rollback plan.
8. Hard limit confirmation.
9. Final classification.
10. Next safe step.

---

## 14. Entry criteria for future patch preview gate

The future patch preview gate may be prepared only if:

1. Repository is on main.
2. HEAD is synced with origin/main.
3. Working tree is clean.
4. Blueprint is CURRENT.
5. Pre-build guard is CLOSED_SYNCED.
6. MVP1 technical plan is reviewed.
7. File boundaries are accepted.
8. No build/runtime/ARGOS authorization is implied.
9. User provides explicit authorization for patch preview.

---

## 15. Current resolved risks

The BUILD READINESS REVIEW detected:

1. No clear future source boundary yet.
2. No patch preview yet.
3. No rollback yet.

This technical plan resolves them at planning level:

1. Future source/test/doc/evidence boundaries are proposed.
2. Patch preview strategy is defined.
3. Preliminary rollback strategy is defined.

Implementation is still not started.

---

## 16. Final technical plan decision

Decision:
READY_FOR_REVIEW_MVP1_READ_ONLY_HUD_TECHNICAL_PLAN_V5_1_R2

This plan prepares the next safe design-to-build transition step, but does not authorize construction.

Next safe step:
REVIEW_MVP1_READ_ONLY_HUD_TECHNICAL_PLAN_AND_DECIDE_IF_COMMIT_IS_REQUIRED
