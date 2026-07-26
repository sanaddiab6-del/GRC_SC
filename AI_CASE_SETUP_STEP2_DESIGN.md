# AI Case Setup Step 2 Design

## 1. Executive Summary

Step 2 is the first controlled transition from AI advisory output to approved platform object setup. Its job is to take a human-approved subset of the Step 1 `AiCaseIntakeDraft` and either create or reuse the initial case setup objects needed to start work in Sanadcom:

- framework resolution
- `Folder` domain creation or reuse
- `Perimeter` creation or reuse
- `ComplianceAssessment` creation or reuse
- optional `RiskAssessment` creation or reuse

Step 2 is intentionally different from Step 1:

- Step 1 is advisory-only and returns draft JSON with `schema_version: 0.2.0`
- Step 1 must remain side-effect free
- Step 2 may write to the database, but only after explicit human approval
- Step 2 must support `dry_run=true` before any write mode is allowed
- Step 2 must be transactional, idempotent for write mode, and safe against partial object creation

The platform must never auto-create setup objects just because Step 1 produced a draft. Human approval is the gate between draft interpretation and database mutation.

### Recommendation

Step 2 should introduce a new AI-specific approved-create endpoint under `ai_onboarding`, not reuse `/api/quick-start/` directly and not extend Step 1 into a write action.

Recommended future endpoint:

- `POST /api/ai/onboarding/case-setup/`

Reasoning anchored in the current codebase:

- `QuickStartSerializer` is a write path, not a review path
- it ignores the submitted `folder` field and always reuses or creates a `Starter` domain and `Starter` perimeter
- it accepts stored-library URNs, auto-loads missing libraries, then creates objects immediately
- it directly creates `ComplianceAssessment` and calls `create_requirement_assessments()`
- it can return partial success because the optional `RiskAssessment` branch occurs after folder, perimeter, and audit creation
- its frontend modal is a submit-and-redirect flow, not a dry-run plus approval flow

That makes `/api/quick-start/` a poor fit for Step 2's human approval, dry-run, and atomic rollback requirements.

## 2. Step 2 Scope

### In scope

- resolve the approved target `Framework`
- create or reuse a `Folder` that represents the business domain
- create or reuse a `Perimeter`
- create or reuse a `ComplianceAssessment`
- optionally create or reuse a `RiskAssessment`
- validate permissions, duplicate risks, and framework availability before write mode
- provide a `dry_run` plan that reports what would be created or reused
- perform one atomic write transaction when the user confirms final creation

### Out of scope

- `Asset` creation
- `AppliedControl` creation
- `Vulnerability` creation
- `RiskScenario` creation
- `Evidence` creation
- `RequirementAssessment` result updates
- `Finding` or `FindingsAssessment` generation
- remediation or action-plan generation
- `RiskAcceptance`
- audit closure
- final compliance decisions
- library preset application
- `WorkflowCase` creation as a required dependency

### Explicit safety boundaries

- Step 2 must not write anything when `dry_run=true`
- Step 2 must not write anything when `approved_by_user=false`
- Step 2 must reject payloads that attempt to smuggle out-of-scope object fields into the approved create request
- Step 2 must not silently load or apply a framework library during the default approved-create flow
- Step 2 must not mutate an existing `ComplianceAssessment` or `RiskAssessment` beyond reuse selection
- Step 2 must not create `RequirementAssessment` records directly; the allowed side effect is only the platform's existing auto-generation when a new `ComplianceAssessment` is created
- Step 2 must not depend on `WorkflowCase`

### Objects Step 2 is allowed to create or reuse

- `Folder`
- `Perimeter`
- `ComplianceAssessment`
- `RiskAssessment` when explicitly requested

### Objects Step 2 is allowed to resolve but not create in v1

- `Framework`
- `StoredLibrary`
- `LoadedLibrary`
- `RiskMatrix`

### Objects Step 2 is forbidden to create or update

- `Asset`
- `AppliedControl`
- `Vulnerability`
- `RiskScenario`
- `Evidence`
- `RequirementNode`
- `RequirementAssessment` result fields
- `Finding`
- `FindingsAssessment`
- `RiskAcceptance`
- `ValidationFlow`
- `WorkflowCase`
- audit final result fields
- audit closure fields
- risk acceptance state

## 3. Recommended Architecture

### Option A: Reuse existing `/api/quick-start/` directly

**Pros**

- existing route already creates domain bootstrap objects
- already uses `FolderWriteSerializer`, `PerimeterWriteSerializer`, `ComplianceAssessmentWriteSerializer`, and `RiskAssessmentWriteSerializer`

**Cons**

- current serializer ignores the submitted `folder` field and always targets `Starter`
- current flow uses stored-library URNs, not explicit approved `Framework` and `RiskMatrix` IDs
- current flow auto-loads missing framework and matrix libraries
- current flow creates objects immediately, with no dry-run stage
- current flow has no idempotency contract
- current flow can partially succeed before the optional risk-assessment branch completes
- current response is object output only, not a review or validation report

**Risks**

- accidental record creation before human approval
- silent library imports at root scope
- partial object creation if a later step fails
- reviewer confusion because `quick-start` implies bootstrap convenience, not AI-approved execution

**Fit with existing Sanadcom architecture**

- weak fit
- it uses real serializers, but its behavior is intentionally convenience-oriented rather than review-first

**Fit with human approval model**

- poor fit

**Fit with dry-run and idempotency needs**

- poor fit

### Option B: Extend QuickStart with AI-approved payload support

**Pros**

- reuses some existing creation plumbing
- might reduce duplicate service code if heavily refactored

**Cons**

- mixes two different semantics into one endpoint family: convenience bootstrap and approved AI execution
- would require major behavioral branching to add dry-run, idempotency, reusable object selection, and strict scope boundaries
- risks preserving legacy assumptions such as auto-loading libraries and hardcoded starter defaults

**Risks**

- endpoint contract drift
- fragile code paths with large conditional branches
- increased chance of regression for existing quick-start users

**Fit with existing Sanadcom architecture**

- only moderate fit if QuickStart were heavily reworked, which is unnecessary for Step 2

**Fit with human approval model**

- moderate to poor fit

**Fit with dry-run and idempotency needs**

- moderate only after substantial redesign

### Option C: Create a new endpoint under `ai_onboarding`

**Pros**

- preserves the Step 1 principle that AI onboarding endpoints have explicit contracts
- keeps advisory parsing separate from approved creation
- allows a purpose-built `dry_run` and `write` flow using the same payload shape
- avoids QuickStart assumptions such as `Starter` defaults and silent library imports
- allows a dedicated response contract that reports create versus reuse decisions per object
- keeps `WorkflowCase` optional

**Cons**

- requires new serializer and service files
- requires explicit orchestration logic for atomic create or reuse

**Risks**

- duplicate business logic if object creation is not cleanly delegated to existing serializers
- temptation to widen the endpoint beyond Step 2 scope if not held to contract boundaries

**Fit with existing Sanadcom architecture**

- strong fit
- matches the existing `ai_onboarding` namespace and keeps orchestration out of generic CRUD endpoints

**Fit with human approval model**

- strong fit

**Fit with dry-run and idempotency needs**

- strong fit

### Option D: Create a new action on the Step 1 endpoint

**Pros**

- keeps Step 1 and Step 2 conceptually adjacent

**Cons**

- weakens the clear no-write contract of `/api/ai/onboarding/case-intake/`
- increases the chance that Step 1 and Step 2 semantics become entangled
- makes it harder to reason about Swagger, permissions, throttling, and auditability

**Risks**

- advisory and write behaviors drift into one resource boundary
- future maintainers may treat Step 1 output as executable by default

**Fit with existing Sanadcom architecture**

- weak fit

**Fit with human approval model**

- poor fit

**Fit with dry-run and idempotency needs**

- poor fit

### Option E: Frontend-only orchestration calling existing CRUD APIs

**Pros**

- reuses existing CRUD endpoints without backend orchestration work
- UI could show dry-run-like previews before sending writes

**Cons**

- cannot provide one database transaction across multiple API calls
- cannot safely guarantee rollback if folder creation succeeds and audit creation fails later
- idempotency becomes difficult across multiple endpoints
- object creation logic becomes split between UI and backend serializers

**Risks**

- partial success and orphan setup objects
- inconsistent duplicate handling across calls
- brittle permission error recovery

**Fit with existing Sanadcom architecture**

- weak fit for a transactional setup wizard

**Fit with human approval model**

- moderate fit in UX only, weak fit in backend safety

**Fit with dry-run and idempotency needs**

- poor fit

### Safest recommendation

Create a new AI-specific approved-create endpoint under `ai_onboarding`.

Recommended shape:

- `POST /api/ai/onboarding/case-setup/`

Recommended implementation split later:

- thin API view in `backend/ai_onboarding/views.py`
- request and response serializers in `backend/ai_onboarding/case_setup_serializers.py`
- orchestration service in `backend/ai_onboarding/case_setup_service.py`
- one transaction-scoped write path that delegates actual object creation to existing core serializers where safe

## 4. Proposed Endpoint Contract

### Endpoint definition

| Property | Recommendation |
| --- | --- |
| HTTP method | `POST` |
| URL path | `/api/ai/onboarding/case-setup/` |
| Authentication | Required |
| Default mode | `dry_run=true` recommended from the frontend before any final create |
| Write mode | Same endpoint, `dry_run=false`, `approved_by_user=true`, `idempotency_key` required |
| Side effects in dry-run | None |
| Side effects in write mode | Allowed only within one atomic transaction |

### Authentication requirements

- authenticated user required
- support the platform's existing authenticated API mechanisms
- no anonymous access

### Permission requirements

The endpoint should not rely only on `IsAuthenticated`. It should enforce the underlying folder-scoped RBAC and root-scope library permissions implied by the approved decision set.

Minimum permission rules:

- dry-run must validate whether the caller would be allowed to perform the requested create or reuse
- write mode must fail before writing if any required permission is missing
- folder create requires permission equivalent to `add_folder` on the parent scope, normally the root folder
- folder reuse requires view access to that folder
- perimeter create requires `add_perimeter` in the target folder
- perimeter reuse requires view access to that perimeter
- compliance assessment create requires `add_complianceassessment` in the target folder
- compliance assessment reuse requires view access to that assessment
- risk assessment create requires `add_riskassessment` in the target folder
- risk assessment reuse requires view access to that assessment
- framework reuse requires view access to the selected `Framework`
- if future versions allow loading a framework library, that must require root-scope `add_loadedlibrary` and explicit confirmation

### Request payload

The request must represent a human-approved case setup decision derived from Step 1. It must be narrower than the full `AiCaseIntakeDraft` and must include only Step 2 fields.

Recommended request shape:

```json
{
  "draft_type": "AiCaseSetupApprovalRequest",
  "schema_version": "0.1.0",
  "approved_by_user": false,
  "source_step1_draft_hash": "sha256:4f2d7d6b4f0a6c4d3c5c0f2f8e9a1b7d3f8e9c1a2b3c4d5e6f7081920a1b2c3d",
  "source_step1_schema_version": "0.2.0",
  "dry_run": true,
  "idempotency_key": null,
  "framework_resolution": {
    "requested_framework_name": "SAMA ECC-1:2018",
    "selected_framework_id": "9cf41d84-b56d-4d03-9641-bf77e0ff9f6e",
    "selected_loaded_library_id": "3b51e0bb-4a27-44e2-a923-53edebd8a8f9",
    "selected_stored_library_urn": "urn:intuitem:library:sama:ecc-1-2018",
    "user_confirmed": true,
    "allow_auto_load": false,
    "candidate_framework_ids": [
      "9cf41d84-b56d-4d03-9641-bf77e0ff9f6e"
    ]
  },
  "folder_domain_decision": {
    "action": "create",
    "existing_folder_id": null,
    "create_payload": {
      "name": "Al Rawasi Fintech KSA Launch",
      "description": "Domain for the KSA launch readiness case",
      "parent_folder_id": "00000000-0000-0000-0000-000000000001",
      "create_iam_groups": true
    }
  },
  "perimeter_decision": {
    "action": "create",
    "existing_perimeter_id": null,
    "create_payload": {
      "name": "Core Payment Platform",
      "ref_id": "PER-KSA-PAY-01",
      "description": "Customer onboarding, IAM, and cloud operations in scope",
      "lc_status": "in_prod"
    }
  },
  "compliance_assessment_decision": {
    "action": "create",
    "existing_compliance_assessment_id": null,
    "create_payload": {
      "name": "ECC-1 2018 Readiness Review",
      "ref_id": "AUD-ECC1-2026-Q4",
      "version": "1.0",
      "status": "planned"
    }
  },
  "risk_assessment_decision": {
    "action": "create",
    "existing_risk_assessment_id": null,
    "create_payload": {
      "name": "KSA Launch Risk Assessment",
      "ref_id": "RA-KSA-2026-Q4",
      "version": "1.0",
      "status": "planned",
      "selected_risk_matrix_id": "4a6df7bc-9b9f-46ac-bf54-c1c3b7c4f260"
    }
  }
}
```

### Required fields

- `approved_by_user`
- `source_step1_draft_hash`
- `framework_resolution`
- `folder_domain_decision`
- `perimeter_decision`
- `compliance_assessment_decision`
- `risk_assessment_decision`
- `dry_run`
- `idempotency_key` required only when `dry_run=false`

### Safe hash and idempotency design when Step 1 drafts are not persisted

Because Step 1 drafts are currently not persisted, Step 2 should use two distinct safety concepts:

1. `source_step1_draft_hash`
   - client includes a SHA-256 hash of the exact Step 1 draft the user reviewed
   - hash should be generated from a canonical JSON serialization with sorted keys
   - this protects against stale or modified review state between Step 1 and Step 2

2. `idempotency_key`
   - client generates a unique key for each explicit final-create click
   - required only for `dry_run=false`
   - write mode should persist the key, normalized approval payload hash, user id, and response summary in a dedicated idempotency receipt store

If a persistent Step 2 idempotency receipt store does not exist yet, the fallback should be documented as weaker and temporary:

- require `idempotency_key`
- compute a normalized approval payload hash server-side
- on retry, attempt duplicate reconciliation by scoped object lookup rules and return `idempotent_replay` only when the existing object set matches the same user-approved payload exactly

This fallback is acceptable only as an interim implementation. The safer long-term design is a persistent idempotency receipt record. `WorkflowCase` must not be used as the required storage mechanism for this.

### Response payload

Recommended success and dry-run response shape:

```json
{
  "draft_type": "AiCaseSetupExecutionResult",
  "schema_version": "0.1.0",
  "dry_run": true,
  "mode": "dry_run",
  "status": "validated",
  "approved_by_user": false,
  "source_step1_draft_hash": "sha256:4f2d7d6b4f0a6c4d3c5c0f2f8e9a1b7d3f8e9c1a2b3c4d5e6f7081920a1b2c3d",
  "idempotency_key": null,
  "transaction_applied": false,
  "summary": {
    "would_create": [
      "Folder",
      "Perimeter",
      "ComplianceAssessment",
      "RiskAssessment"
    ],
    "would_reuse": [
      "Framework"
    ],
    "would_skip": []
  },
  "framework_resolution": {
    "status": "resolved",
    "framework_id": "9cf41d84-b56d-4d03-9641-bf77e0ff9f6e",
    "loaded_library_id": "3b51e0bb-4a27-44e2-a923-53edebd8a8f9"
  },
  "results": {
    "folder": {
      "action": "create",
      "status": "ok"
    },
    "perimeter": {
      "action": "create",
      "status": "ok"
    },
    "compliance_assessment": {
      "action": "create",
      "status": "ok",
      "note": "RequirementAssessment children will be auto-generated if created."
    },
    "risk_assessment": {
      "action": "create",
      "status": "ok"
    }
  },
  "warnings": [],
  "blocking_errors": []
}
```

### Response semantics

- `status=validated`: dry-run succeeded and the plan is executable
- `status=blocked`: dry-run completed but write mode would be rejected until blocking issues are resolved
- `status=created`: write mode completed and new objects were created
- `status=reused`: write mode completed using only existing objects
- `status=mixed_created_and_reused`: write mode completed with a mix of new and existing objects
- `status=idempotent_replay`: the same write request was already committed and the saved result is being replayed

### Error response format

Recommended non-2xx error shape:

```json
{
  "error": {
    "code": "framework_not_loaded",
    "message": "The selected framework library exists in StoredLibrary but is not loaded as a Framework.",
    "retryable": false
  },
  "field_errors": {
    "framework_resolution.selected_framework_id": [
      "Select a loaded Framework or explicitly confirm a separate library load step."
    ]
  },
  "object_errors": [
    {
      "object": "Framework",
      "action": "resolve",
      "status": "blocked"
    }
  ]
}
```

Recommended status codes:

- `200 OK` for dry-run responses, including blocked dry-run validation reports
- `201 Created` for successful write mode that created at least one new object
- `200 OK` for successful write mode that only reused existing objects or returned an idempotent replay
- `400 Bad Request` for request schema violations
- `401 Unauthorized` for missing authentication
- `403 Forbidden` for permission failures
- `409 Conflict` for idempotency-key collisions with a different payload hash or irreconcilable duplicate selection conflicts
- `422 Unprocessable Entity` for executable business-rule blockers in write mode

## 5. Human Approval Model

### What the user must approve

- the chosen `Framework`
- whether the domain is a new `Folder` or an existing one
- whether the `Perimeter` is new or existing
- whether the `ComplianceAssessment` is new or existing
- whether the optional `RiskAssessment` is skipped, new, or existing
- the final names, reference ids, and statuses that will be written
- any IAM side effect for a new domain, especially `create_iam_groups`

### What the user can edit

- selected framework candidate
- folder name and description
- whether to reuse an existing folder instead of creating a new one
- perimeter name, description, ref id, and lifecycle status
- compliance assessment name, ref id, version, and initial status
- risk assessment name, ref id, version, initial status, and selected risk matrix
- whether optional risk assessment creation should be skipped

### What the user can reject

- the entire Step 2 plan
- any individual object proposal
- any low-confidence framework match
- any proposed create action in favor of an explicit reuse selection

### What must remain locked from AI

- final compliance result fields
- `RequirementAssessment` results or answers
- `AppliedControl` creation flags such as `create_applied_controls_from_suggestions`
- `EbiosRMStudy` linkage that could auto-create `RiskScenario` records
- final risk acceptance decisions
- audit closure and final completion states
- any asset, evidence, finding, remediation, or workflow closure instructions

### How to show Step 1 warnings and confidence

- carry Step 1 `overall_confidence`, `warnings`, `blocking_questions`, and per-object `needs_review` flags into the review screen
- visually separate AI inference from final approved values
- highlight any framework candidate ambiguity, missing matrix resolution, or duplicate risk in dry-run output

### How to prevent accidental auto-create

- Step 2 UI must have a distinct review screen, not a single submit modal
- the final create button must be separate from dry-run validation
- the final create button must require explicit human confirmation
- write mode must still be rejected server-side unless `approved_by_user=true`
- Step 1 responses must never contain an executable auto-follow action to Step 2

### How dry-run should be presented

- first stage: review Step 1 draft grouped by object type
- second stage: run dry-run validation and show create versus reuse outcomes, permission issues, duplicates, and framework blockers
- third stage: after the user confirms the exact plan, send write mode with `approved_by_user=true` and `idempotency_key`

## 6. Object Creation / Reuse Rules

### Framework

| Rule | Design |
| --- | --- |
| When to create | Not allowed in Step 2 v1. Step 2 resolves and reuses an existing loaded `Framework`. |
| When to reuse | When the user explicitly selects an accessible `Framework` and the framework is already backed by `LoadedLibrary`. |
| Required fields | `selected_framework_id` or a future equivalent that resolves to one loaded `Framework`. |
| Optional fields | `selected_loaded_library_id`, `selected_stored_library_urn`, candidate list for traceability. |
| Lookup logic | Prefer exact `Framework.id`. If only Step 1 candidate labels are present, dry-run resolves candidates but write mode requires an explicit final selection. |
| Duplicate detection | Not a create path in Step 2 v1. |
| Permission checks | View access to the selected framework. If future auto-load is allowed, root-scope `add_loadedlibrary` is also required. |
| Failure behavior | Missing or inaccessible framework blocks Step 2 before any write. |
| Rollback behavior | No write should start until framework resolution is complete. |

### Folder / Domain

| Rule | Design |
| --- | --- |
| When to create | When `folder_domain_decision.action=create` and no approved existing folder is selected. |
| When to reuse | When `folder_domain_decision.action=reuse` and `existing_folder_id` is provided. |
| Required fields | Create: `name`. Reuse: `existing_folder_id`. |
| Optional fields | `description`, `parent_folder_id`, `create_iam_groups`. |
| Lookup logic | Reuse should be by explicit folder id, not fuzzy name match. Dry-run may propose candidates by name but must not auto-bind to one without user selection. |
| Duplicate detection | Use the platform's folder-scoped uniqueness rules. `Folder` uses `fields_to_check=["name"]` and scopes uniqueness by `parent_folder`. |
| Permission checks | Create requires `add_folder` in the target parent scope. Reuse requires folder visibility. |
| Failure behavior | If create fails, block or abort the whole request. |
| Rollback behavior | On write-mode failure later in the transaction, the created folder and any IAM side effects must roll back. |

Additional folder notes:

- a new Step 2 domain should default to `Folder.ContentType.DOMAIN`
- `create_iam_groups` must be explicit because it creates default user groups and role assignments
- dry-run must surface that IAM side effect clearly

### Perimeter

| Rule | Design |
| --- | --- |
| When to create | When `perimeter_decision.action=create`. |
| When to reuse | When `perimeter_decision.action=reuse` and `existing_perimeter_id` is provided. |
| Required fields | Create: `name`. Reuse: `existing_perimeter_id`. |
| Optional fields | `ref_id`, `description`, `lc_status`. |
| Lookup logic | Reuse must be by explicit perimeter id in the approved folder. |
| Duplicate detection | Use `Perimeter.fields_to_check=["name"]` in folder scope. |
| Permission checks | Create requires `add_perimeter` in the folder. Reuse requires visibility on the perimeter and folder consistency with the approved folder decision. |
| Failure behavior | If the selected perimeter belongs to a different folder than the approved folder decision, block the request. |
| Rollback behavior | Any failure after perimeter creation rolls the whole transaction back. |

Additional perimeter notes:

- `PerimeterWriteSerializer.update()` forbids changing the perimeter domain after creation
- therefore reuse must validate folder compatibility up front

### ComplianceAssessment / Audit

| Rule | Design |
| --- | --- |
| When to create | When `compliance_assessment_decision.action=create`. |
| When to reuse | When `compliance_assessment_decision.action=reuse` and `existing_compliance_assessment_id` is provided. |
| Required fields | Create: `name`, resolved `framework`, resolved `folder`, resolved `perimeter`. Reuse: existing assessment id. |
| Optional fields | `ref_id`, `version`, `status`. |
| Lookup logic | Reuse must be by explicit assessment id. It must already belong to the approved folder and perimeter and use the approved framework. |
| Duplicate detection | Use `ComplianceAssessment.fields_to_check=["name", "version"]` in perimeter scope. |
| Permission checks | Create requires `add_complianceassessment` in folder scope and framework visibility. Reuse requires assessment visibility. |
| Failure behavior | Mismatched perimeter or framework on a reused assessment blocks the request. |
| Rollback behavior | Audit creation and auto-generated `RequirementAssessment` records must roll back together if any later step fails. |

Additional compliance assessment notes:

- creating a new `ComplianceAssessment` is allowed even though it auto-generates `RequirementAssessment` rows; that is an existing platform side effect and is within Step 2 scope only as a downstream consequence of creating the audit itself
- Step 2 must not expose or permit `baseline`
- Step 2 must not expose or permit `create_applied_controls_from_suggestions`
- Step 2 must not update requirement results after creation

### Optional RiskAssessment

| Rule | Design |
| --- | --- |
| When to create | When `risk_assessment_decision.action=create`. |
| When to reuse | When `risk_assessment_decision.action=reuse` and `existing_risk_assessment_id` is provided. |
| When to skip | When `risk_assessment_decision.action=skip`. |
| Required fields | Create: `name`, resolved `folder`, resolved `perimeter`, resolved `selected_risk_matrix_id`. Reuse: existing risk assessment id. |
| Optional fields | `ref_id`, `version`, `status`. |
| Lookup logic | Reuse must be by explicit risk assessment id. It must already belong to the approved folder and perimeter. |
| Duplicate detection | Use `RiskAssessment.fields_to_check=["name", "version"]` in perimeter scope. |
| Permission checks | Create requires `add_riskassessment` in folder scope and visibility of the chosen risk matrix. Reuse requires visibility on the risk assessment. |
| Failure behavior | Missing risk matrix resolution blocks creation. Mismatched perimeter or folder on a reused assessment blocks reuse. |
| Rollback behavior | If risk assessment creation or reuse validation fails in write mode, the entire transaction must roll back. |

Additional risk assessment notes:

- Step 1 only provides a `risk_matrix_preference`, not a resolved matrix id
- Step 2 must require explicit matrix selection before creating a new `RiskAssessment`
- Step 2 must not accept `ebios_rm_study` in v1 because existing `RiskAssessmentViewSet.perform_create()` can auto-create `RiskScenario` records for selected EBIOS studies, which is out of scope

## 7. Framework Resolution Design

### Canonical object model

- `StoredLibrary` is the importable source package
- `LoadedLibrary` is the imported runtime library
- `Framework` is the usable compliance framework object linked to a `LoadedLibrary`

### Recommended Step 2 behavior

1. Step 1 may suggest one or more framework candidates by business label or library hint.
2. Dry-run resolves those hints against the currently available `Framework`, `LoadedLibrary`, and `StoredLibrary` records.
3. The user must explicitly confirm the final framework selection.
4. Write mode must use one resolved, accessible `Framework`.
5. If no framework is loaded, Step 2 should block and instruct the user to complete a separate framework-load step.

### Candidate framework matching

Dry-run may use the following lookup order:

1. exact `Framework.id` if provided
2. exact `LoadedLibrary.id` plus its associated `Framework`
3. exact `StoredLibrary.urn` only to report availability state
4. label or normalized business-name matching to produce candidate suggestions only

### User-selected framework

Write mode should require one of the following:

- `framework_resolution.selected_framework_id`
- or a future explicit separate library-load confirmation flow that results in a new `selected_framework_id` before Step 2 write proceeds

### Missing framework

If no matching `StoredLibrary`, `LoadedLibrary`, or `Framework` exists:

- dry-run returns `status=blocked`
- write mode returns `422 Unprocessable Entity`
- no objects are written

### Framework not loaded

If a matching `StoredLibrary` exists but no corresponding `LoadedLibrary` and `Framework` exist:

- default Step 2 behavior is to block
- response should state that the library exists but is not currently loaded
- do not auto-call `/api/stored-libraries/{id-or-urn}/import/` during the default approved-create flow

### Multiple candidate frameworks

If multiple candidates match the Step 1 hint:

- dry-run returns all candidates with confidence metadata
- user must explicitly choose one
- write mode must reject ambiguous framework selection

### Permission or availability issues

- if the user can see the Step 1 draft but not the chosen framework, dry-run should return a permission blocker before write mode
- if library import would be needed later, root-scope permissions must be evaluated separately

### Should Step 2 auto-load or auto-apply a library?

Recommendation for v1:

- no automatic library load
- no automatic library preset apply
- no silent framework activation inside the approved-create endpoint

Reasoning:

- current QuickStart auto-load behavior is convenient but too implicit for the first write-capable AI step
- loading libraries is root-scoped and materially different from creating case setup objects
- automatic preset application is even broader and is not part of the Step 2 object scope

If the product later wants a one-click experience, library loading should still require explicit human confirmation and should be modeled as a separate approved preflight action before final Step 2 object creation.

## 8. Transaction and Rollback Strategy

### Atomicity

All write-mode operations must run in one database transaction.

Recommended rule:

- one request
- one approved payload
- one transaction
- zero partial success

### Failure scenarios

#### Folder created but Perimeter fails

- entire transaction rolls back
- no new folder, IAM group, or role-assignment side effect remains

#### ComplianceAssessment creation fails

- folder and perimeter creation must roll back
- no `RequirementAssessment` children remain

#### Optional RiskAssessment creation fails

- if `risk_assessment_decision.action=skip`, no problem
- if the request explicitly asked to create or reuse a risk assessment and that step fails, the whole transaction must roll back
- Step 2 must not return partial success such as "audit created, risk assessment failed"

### Partial success policy

- dry-run may report mixed create or reuse intent
- write mode must not commit mixed success and failure
- either all approved objects are resolved or created successfully, or nothing is committed

### Dry-run behavior

Dry-run should validate without writing. Recommended validation work:

- request schema validation
- out-of-scope field rejection
- framework and risk-matrix resolution
- permission checks
- duplicate checks aligned to model scope rules
- create-versus-reuse feasibility checks
- compatibility checks between folder, perimeter, assessments, and framework

Dry-run should not:

- save any model
- call `StoredLibrary.load()`
- call `apply_preset`
- create `RequirementAssessment`
- create IAM groups

### Idempotency

Idempotency is required for write mode.

Recommended behavior:

- require `idempotency_key` when `dry_run=false`
- store `user_id + idempotency_key + normalized_payload_hash + response_snapshot + committed_object_ids`
- if the same key and same hash are replayed, return the saved response as `status=idempotent_replay`
- if the same key is replayed with a different normalized payload hash, return `409 Conflict`

### Duplicate request handling

Duplicate requests without the same idempotency key must still be handled safely:

- scoped duplicate checks should prevent accidental name collisions in the same folder or perimeter
- reuse decisions should prefer explicit existing object ids over heuristic matching
- when duplicate ambiguity exists, block and require user action rather than guessing

## 9. API Payload Examples

### A. Dry-run request

```json
{
  "draft_type": "AiCaseSetupApprovalRequest",
  "schema_version": "0.1.0",
  "approved_by_user": false,
  "source_step1_draft_hash": "sha256:8f9f1e2e5a4d3d8a6d5a9d0f7e9b0c1d2a3b4c5d6e7f8091a2b3c4d5e6f70819",
  "source_step1_schema_version": "0.2.0",
  "dry_run": true,
  "idempotency_key": null,
  "framework_resolution": {
    "requested_framework_name": "SAMA ECC-1:2018",
    "selected_framework_id": "9cf41d84-b56d-4d03-9641-bf77e0ff9f6e",
    "selected_loaded_library_id": "3b51e0bb-4a27-44e2-a923-53edebd8a8f9",
    "selected_stored_library_urn": "urn:intuitem:library:sama:ecc-1-2018",
    "user_confirmed": true,
    "allow_auto_load": false
  },
  "folder_domain_decision": {
    "action": "create",
    "existing_folder_id": null,
    "create_payload": {
      "name": "Al Rawasi Fintech KSA Launch",
      "description": "Domain for KSA launch readiness",
      "create_iam_groups": true
    }
  },
  "perimeter_decision": {
    "action": "create",
    "existing_perimeter_id": null,
    "create_payload": {
      "name": "Core Payment Platform",
      "ref_id": "PER-KSA-PAY-01",
      "lc_status": "in_prod"
    }
  },
  "compliance_assessment_decision": {
    "action": "create",
    "existing_compliance_assessment_id": null,
    "create_payload": {
      "name": "ECC-1 2018 Readiness Review",
      "version": "1.0",
      "status": "planned"
    }
  },
  "risk_assessment_decision": {
    "action": "skip",
    "existing_risk_assessment_id": null,
    "create_payload": null
  }
}
```

### B. Dry-run response

```json
{
  "draft_type": "AiCaseSetupExecutionResult",
  "schema_version": "0.1.0",
  "dry_run": true,
  "mode": "dry_run",
  "status": "validated",
  "approved_by_user": false,
  "source_step1_draft_hash": "sha256:8f9f1e2e5a4d3d8a6d5a9d0f7e9b0c1d2a3b4c5d6e7f8091a2b3c4d5e6f70819",
  "idempotency_key": null,
  "transaction_applied": false,
  "summary": {
    "would_create": [
      "Folder",
      "Perimeter",
      "ComplianceAssessment"
    ],
    "would_reuse": [
      "Framework"
    ],
    "would_skip": [
      "RiskAssessment"
    ]
  },
  "results": {
    "framework": {
      "action": "reuse",
      "status": "ok",
      "target": {
        "id": "9cf41d84-b56d-4d03-9641-bf77e0ff9f6e",
        "name": "SAMA ECC-1:2018"
      }
    },
    "folder": {
      "action": "create",
      "status": "ok"
    },
    "perimeter": {
      "action": "create",
      "status": "ok"
    },
    "compliance_assessment": {
      "action": "create",
      "status": "ok",
      "note": "RequirementAssessment children will be auto-generated on create."
    },
    "risk_assessment": {
      "action": "skip",
      "status": "ok"
    }
  },
  "warnings": [],
  "blocking_errors": []
}
```

### C. Approved create request

```json
{
  "draft_type": "AiCaseSetupApprovalRequest",
  "schema_version": "0.1.0",
  "approved_by_user": true,
  "source_step1_draft_hash": "sha256:8f9f1e2e5a4d3d8a6d5a9d0f7e9b0c1d2a3b4c5d6e7f8091a2b3c4d5e6f70819",
  "source_step1_schema_version": "0.2.0",
  "dry_run": false,
  "idempotency_key": "b7fbd9ae-68fe-4c6f-b502-5bc7b43c14b3",
  "framework_resolution": {
    "requested_framework_name": "SAMA ECC-1:2018",
    "selected_framework_id": "9cf41d84-b56d-4d03-9641-bf77e0ff9f6e",
    "selected_loaded_library_id": "3b51e0bb-4a27-44e2-a923-53edebd8a8f9",
    "selected_stored_library_urn": "urn:intuitem:library:sama:ecc-1-2018",
    "user_confirmed": true,
    "allow_auto_load": false
  },
  "folder_domain_decision": {
    "action": "reuse",
    "existing_folder_id": "32c3082b-8eb6-4a47-97d8-7d98547e52de",
    "create_payload": null
  },
  "perimeter_decision": {
    "action": "create",
    "existing_perimeter_id": null,
    "create_payload": {
      "name": "Core Payment Platform",
      "ref_id": "PER-KSA-PAY-01",
      "description": "Customer onboarding, IAM, and cloud operations in scope",
      "lc_status": "in_prod"
    }
  },
  "compliance_assessment_decision": {
    "action": "create",
    "existing_compliance_assessment_id": null,
    "create_payload": {
      "name": "ECC-1 2018 Readiness Review",
      "ref_id": "AUD-ECC1-2026-Q4",
      "version": "1.0",
      "status": "planned"
    }
  },
  "risk_assessment_decision": {
    "action": "create",
    "existing_risk_assessment_id": null,
    "create_payload": {
      "name": "KSA Launch Risk Assessment",
      "ref_id": "RA-KSA-2026-Q4",
      "version": "1.0",
      "status": "planned",
      "selected_risk_matrix_id": "4a6df7bc-9b9f-46ac-bf54-c1c3b7c4f260"
    }
  }
}
```

### D. Successful create response

```json
{
  "draft_type": "AiCaseSetupExecutionResult",
  "schema_version": "0.1.0",
  "dry_run": false,
  "mode": "write",
  "status": "mixed_created_and_reused",
  "approved_by_user": true,
  "source_step1_draft_hash": "sha256:8f9f1e2e5a4d3d8a6d5a9d0f7e9b0c1d2a3b4c5d6e7f8091a2b3c4d5e6f70819",
  "idempotency_key": "b7fbd9ae-68fe-4c6f-b502-5bc7b43c14b3",
  "transaction_applied": true,
  "summary": {
    "created": [
      "Perimeter",
      "ComplianceAssessment",
      "RiskAssessment"
    ],
    "reused": [
      "Framework",
      "Folder"
    ],
    "skipped": []
  },
  "results": {
    "framework": {
      "action": "reuse",
      "status": "ok",
      "target": {
        "id": "9cf41d84-b56d-4d03-9641-bf77e0ff9f6e",
        "name": "SAMA ECC-1:2018"
      }
    },
    "folder": {
      "action": "reuse",
      "status": "ok",
      "target": {
        "id": "32c3082b-8eb6-4a47-97d8-7d98547e52de",
        "name": "Al Rawasi Fintech KSA Launch"
      }
    },
    "perimeter": {
      "action": "create",
      "status": "ok",
      "target": {
        "id": "0d7c93a4-1167-4efe-bd76-17ee1ac91bf0",
        "name": "Core Payment Platform"
      }
    },
    "compliance_assessment": {
      "action": "create",
      "status": "ok",
      "target": {
        "id": "5f766b1f-26a7-47c0-8a9a-230f49db1f07",
        "name": "ECC-1 2018 Readiness Review"
      },
      "generated_side_effects": {
        "requirement_assessments_created": true
      }
    },
    "risk_assessment": {
      "action": "create",
      "status": "ok",
      "target": {
        "id": "11bbca4e-02a4-4e5f-ad50-43d8098a33d1",
        "name": "KSA Launch Risk Assessment"
      }
    }
  },
  "warnings": []
}
```

### E. Duplicate or reuse response

```json
{
  "draft_type": "AiCaseSetupExecutionResult",
  "schema_version": "0.1.0",
  "dry_run": false,
  "mode": "write",
  "status": "idempotent_replay",
  "approved_by_user": true,
  "source_step1_draft_hash": "sha256:8f9f1e2e5a4d3d8a6d5a9d0f7e9b0c1d2a3b4c5d6e7f8091a2b3c4d5e6f70819",
  "idempotency_key": "b7fbd9ae-68fe-4c6f-b502-5bc7b43c14b3",
  "transaction_applied": false,
  "summary": {
    "created": [],
    "reused": [
      "Framework",
      "Folder",
      "Perimeter",
      "ComplianceAssessment",
      "RiskAssessment"
    ],
    "skipped": []
  },
  "results": {
    "message": "The same approved create request was already committed. Returning the saved result."
  },
  "warnings": []
}
```

### F. Framework not found response

```json
{
  "error": {
    "code": "framework_not_found",
    "message": "No matching Framework could be resolved from the approved Step 1 draft.",
    "retryable": false
  },
  "field_errors": {
    "framework_resolution.selected_framework_id": [
      "Select an existing loaded Framework before continuing."
    ]
  },
  "object_errors": [
    {
      "object": "Framework",
      "action": "resolve",
      "status": "blocked"
    }
  ]
}
```

### G. Permission denied response

```json
{
  "error": {
    "code": "permission_denied",
    "message": "You do not have permission to create objects in the selected folder.",
    "retryable": false
  },
  "field_errors": {
    "folder_domain_decision": [
      "Missing add_folder permission in the selected parent scope."
    ],
    "perimeter_decision": [
      "Missing add_perimeter permission in the approved folder."
    ]
  },
  "object_errors": []
}
```

### H. Partial failure prevented by transaction response

```json
{
  "error": {
    "code": "transaction_aborted",
    "message": "RiskAssessment validation failed. No objects were created.",
    "retryable": true
  },
  "field_errors": {
    "risk_assessment_decision.create_payload.selected_risk_matrix_id": [
      "Selected risk matrix is not accessible in the current scope."
    ]
  },
  "object_errors": [
    {
      "object": "RiskAssessment",
      "action": "create",
      "status": "failed"
    },
    {
      "object": "Folder",
      "action": "create",
      "status": "rolled_back"
    },
    {
      "object": "Perimeter",
      "action": "create",
      "status": "rolled_back"
    },
    {
      "object": "ComplianceAssessment",
      "action": "create",
      "status": "rolled_back"
    }
  ]
}
```

## 10. Validation Rules

- `approved_by_user` must be `true` for write mode
- `dry_run=true` must not write any records
- `idempotency_key` is required for write mode
- `source_step1_draft_hash` is required for both dry-run and write mode
- canonical entity names only; the Step 2 payload must refer to `Folder`, `Perimeter`, `ComplianceAssessment`, `RiskAssessment`, `Framework`, `StoredLibrary`, `LoadedLibrary`, and `RiskMatrix` using platform-native vocabulary
- no `Asset`, `AppliedControl`, `Vulnerability`, `RiskScenario`, `Evidence`, `Finding`, `FindingsAssessment`, remediation, or action-plan creation fields are allowed in the Step 2 write payload
- no final compliance result fields are allowed
- no `RiskAcceptance` fields are allowed
- no audit closure fields are allowed
- no `WorkflowCase` hard dependency is allowed
- strict permission checks must run before write mode begins
- duplicate detection must follow scoped model rules already used by the platform
- framework must be explicitly selected or resolved with high confidence and then confirmed by the user
- if multiple framework candidates exist, write mode must reject until the user selects one
- if a new `RiskAssessment` is requested, a resolved `selected_risk_matrix_id` is required
- `baseline`, `create_applied_controls_from_suggestions`, and `ebios_rm_study` must be rejected in Step 2 v1
- reused objects must be validated for compatibility with the approved folder, perimeter, and framework selections
- `requirements` versus `/api/requirement-nodes/` naming mismatch remains an implementation constraint for later steps but must not affect Step 2 payload design

## 11. Frontend UX Design

### Review flow

1. user starts from the Step 1 `AiCaseIntakeDraft`
2. frontend shows grouped case setup objects only:
   - framework
   - domain folder
   - perimeter
   - compliance assessment
   - optional risk assessment
3. each group shows:
   - AI suggestion
   - confidence and warnings
   - create versus reuse choice
   - editable approved values
4. user can accept, edit, or reject each setup object
5. user runs dry-run validation
6. frontend displays dry-run results with blocking issues and create or reuse summary
7. user explicitly confirms final create
8. success screen shows created and reused objects with links to resulting records

### UX requirements

- the screen must clearly state that Step 1 was advisory-only and Step 2 may write records
- dry-run and final create must be separate user actions
- no assets, controls, vulnerabilities, risks, evidence, findings, or remediation objects are created in this step
- the final confirmation must show exactly which objects will be created and which will be reused
- if a framework is not loaded, the UI must present that as a blocker, not silently resolve it
- if a risk matrix is missing for optional risk assessment creation, the UI must require user selection before final create

### Suggested frontend structure

- a dedicated Step 2 review page or drawer is safer than reusing the current QuickStart modal
- the current QuickStart modal is optimized for submit-and-redirect, not staged review
- the Step 2 UI should preserve Step 1 traceability, including warnings and rationale

## 12. Test Plan for Future Step 2 Implementation

### API behavior tests

- dry-run creates nothing
- write mode requires approval
- write mode requires idempotency key
- write mode requires source Step 1 draft hash
- auth required
- permission denied for missing folder or assessment permissions
- framework missing returns blocker
- framework not loaded returns blocker
- multiple framework candidates require user selection
- risk matrix required for new optional risk assessment

### Folder and perimeter tests

- folder creation succeeds when approved
- folder reuse succeeds when explicit existing folder id is selected
- folder duplicate detection blocks ambiguous create
- perimeter creation succeeds when approved
- perimeter reuse succeeds when explicit existing perimeter id is selected
- perimeter reuse fails when it belongs to a different folder than the approved folder decision

### Assessment tests

- compliance assessment creation succeeds and auto-generates requirement assessments
- compliance assessment reuse succeeds when perimeter and framework are compatible
- optional risk assessment creation succeeds when a valid risk matrix is selected
- optional risk assessment skip mode writes no risk assessment
- risk assessment reuse succeeds when perimeter matches
- Step 2 rejects `ebios_rm_study`

### Idempotency and duplicate tests

- exact idempotency retry returns saved response
- same idempotency key with different payload hash returns conflict
- duplicate detection without idempotency key still blocks unsafe create attempts

### Transaction tests

- if folder creation succeeds but perimeter validation fails, nothing is committed
- if compliance assessment creation fails, nothing is committed
- if optional risk assessment creation fails, nothing is committed
- IAM side effects from a new folder roll back when the transaction aborts

### Scope guardrail tests

- no out-of-scope objects are created
- no final compliance decision can be submitted
- no risk acceptance fields are accepted
- no audit closure fields are accepted
- no `WorkflowCase` dependency is required

## 13. Files Expected to Change During Step 2 Implementation

These files are likely to be created or modified later. They should not be changed as part of this design-only step.

### Likely backend changes

- `backend/ai_onboarding/views.py`
- `backend/ai_onboarding/urls.py`
- `backend/ai_onboarding/case_setup_serializers.py` new
- `backend/ai_onboarding/case_setup_service.py` new
- `backend/ai_onboarding/case_setup_permissions.py` new or a shared permission helper
- `backend/app_tests/api/test_api_ai_case_setup.py` new
- possible shared helper extraction if idempotency receipts or dry-run duplicate checks are centralized

### Likely frontend changes

- a new Step 2 review screen under the onboarding or AI routes
- new components for framework selection, create versus reuse decisions, and dry-run result presentation
- Step 1 to Step 2 state handoff code
- success-screen routing to created or reused `ComplianceAssessment` and optional `RiskAssessment`

### Files likely not to be reused directly for Step 2 logic

- `backend/core/views.py` QuickStart path should remain separate
- `frontend/src/lib/components/SideBar/QuickStart/QuickStartModal.svelte` is not a suitable direct host for the Step 2 review flow

## 14. Open Questions / Needs Verification

- whether `/api/quick-start/` should remain completely separate from Step 2: recommendation is yes
- whether framework loading should ever be automatic: recommendation is no for v1
- whether idempotency can be implemented safely without a persistent receipt store: possible only as a weaker temporary fallback
- whether Step 1 drafts should be persisted later for stronger provenance and auditability: likely yes
- whether `WorkflowCase` should eventually store provenance metadata without becoming a hard dependency now: likely yes
- whether Step 2 should expose `create_iam_groups` directly or default it to `true` for new domains after explicit disclosure in the UI
- whether a dedicated Step 2 response audit log should be retained independently of any future `WorkflowCase`

## 15. Step 2 Design Acceptance Criteria

Step 2 design is ready for implementation only when all of the following are true:

- the approved implementation target is a new AI-specific endpoint under `ai_onboarding`
- Step 1 remains advisory-only and side-effect free
- Step 2 dry-run is defined and guaranteed to be no-write
- write mode requires explicit human approval
- write mode requires idempotency
- framework resolution requires an explicit final user-confirmed selection
- risk assessment creation requires explicit risk-matrix resolution
- all approved writes run in one atomic transaction
- no partial success is allowed in write mode
- out-of-scope object creation is impossible by contract validation
- no `WorkflowCase` hard dependency exists
- response contracts for dry-run, success, reuse, and error cases are defined
- the future test plan covers permission checks, duplicates, dry-run, idempotency, rollback, and scope boundaries
