# AI Asset Commit Step 3B Design

## 1. Executive Summary

Step 3B is the approved transition from Step 3A advisory asset suggestions to controlled `Asset` creation or reuse inside the Sanadcom platform.

It sits after:

- Step 1 `POST /api/ai/onboarding/case-intake/`, which is advisory-only and no-write.
- Step 2 `POST /api/ai/onboarding/case-setup/`, which creates or reuses the case setup context.
- Step 3A `POST /api/ai/onboarding/assets/suggest/`, which is advisory-only and returns `AiAssetSuggestionDraft` with candidate assets, ambiguity flags, and duplicate warnings.

Step 3B must be intentionally narrower than the surrounding workflow:

- it may write `Asset` records only
- it may do so only after explicit human approval
- it must support `dry_run=true`
- it must support approved write mode
- it must never create or mutate controls, vulnerabilities, evidence, risks, findings, remediation records, requirement results, workflow cases, or final decisions

The safest endpoint structure is a new AI-specific commit endpoint under the existing onboarding namespace:

- `POST /api/ai/onboarding/assets/commit/`

This keeps Step 3A advisory-only, preserves Step 2 boundaries, and avoids exposing raw `/api/assets/` CRUD semantics as the user-facing AI workflow contract.

## 2. Step 3B Scope

### In scope

- validate a reviewed Step 3A asset suggestion set against a real Step 2 case context
- support human decisions per candidate asset: create, reuse, reject, defer
- perform duplicate checks before create
- support `dry_run` planning with zero writes
- create new `Asset` records in write mode when explicitly approved
- acknowledge explicit reuse of existing visible `Asset` records
- return traceable summaries of created, reused, rejected, deferred, skipped, blocked, or rolled back items

### Out of scope

- `AppliedControl` creation or reuse
- `Vulnerability` creation or reuse
- `RiskScenario` creation or reuse
- `Evidence` or `EvidenceRevision` creation
- `RequirementAssessment` creation or result mutation
- `Finding` or `FindingsAssessment` creation
- remediation or action-plan generation
- `RiskAcceptance`
- final compliance decisions
- final risk decisions
- audit closure
- `WorkflowCase` creation as a hard dependency
- framework import or library loading
- automatic classification of non-assets into other object types

### Allowed objects

- `Asset`

### Forbidden objects

- `AppliedControl`
- `Vulnerability`
- `RiskScenario`
- `Evidence`
- `EvidenceRevision`
- `RequirementAssessment`
- `Finding`
- `FindingsAssessment`
- remediation or action-plan records
- `RiskAcceptance`
- `WorkflowCase`
- any invented entity type

### Allowed actions

- create `Asset`
- reuse existing `Asset`
- reject suggested asset
- defer suggested asset

### Forbidden actions

- auto-create from Step 3A without human approval
- auto-reuse based only on duplicate detection
- mutate existing reused assets
- attach assets to non-asset objects in v1
- create labels, controls, evidence, risks, or findings as side effects
- write final decisions or closure states

### Human approval boundaries

- Step 3A output is never executable by itself.
- Every Step 3A candidate must receive an explicit human decision before write mode.
- `approved_by_user=true` is required for write mode.
- Each decision item must be explicitly reviewed and marked approved for its chosen action.
- Ambiguous candidates require explicit human resolution before create or reuse.
- Duplicate candidates require explicit human create or reuse resolution before write mode.

### Dry-run boundaries

- `dry_run=true` must perform validation, permission checks, and duplicate analysis.
- `dry_run=true` must not create, update, delete, or mutate any record.
- `dry_run=true` must leave database counts unchanged.
- `dry_run=true` may return planned create and reuse actions, warnings, and blocking errors.

## 3. Recommended Architecture

### Option A: Reuse existing Asset CRUD API directly

Pros:

- reuses `AssetWriteSerializer` and existing `/api/assets/` behavior
- already benefits from folder-scoped RBAC and visibility checks

Cons:

- `/api/assets/` is raw CRUD, not a reviewed AI workflow contract
- no first-class `dry_run`
- no top-level approval gate
- no structured `temporary_id` to final object mapping
- no Step 3A provenance contract
- no asset-decision list semantics

Risks:

- users can bypass human-review boundaries
- duplicate handling becomes client-specific and inconsistent
- no single place to reject out-of-scope AI payload fields

Fit with human approval:

- weak

Fit with dry-run:

- weak

Fit with idempotency:

- weak

Fit with auditability and provenance:

- weak

Fit with future Step 4 controls and Step 5 vulnerabilities:

- weak because later AI steps need a stable reviewed orchestration contract, not raw CRUD calls

### Option B: Frontend-only orchestration calling Asset CRUD API

Pros:

- no new backend orchestration endpoint required
- frontend can present a review experience quickly

Cons:

- no single transaction across multiple create decisions
- no server-enforced write gate around the full reviewed draft
- no authoritative server-side duplicate conflict contract
- business rules become split between browser and serializer

Risks:

- partial success if several create calls are issued and later ones fail
- stale duplicate checks between preview and final submit
- harder regression safety across future AI steps

Fit with human approval:

- moderate in UX only, weak in backend enforcement

Fit with dry-run:

- weak

Fit with idempotency:

- weak

Fit with auditability and provenance:

- weak

Fit with future Step 4 controls and Step 5 vulnerabilities:

- weak due to fragmented orchestration

### Option C: Add commit behavior into Step 3A suggestion endpoint

Pros:

- keeps suggest and commit conceptually adjacent
- may reduce route count

Cons:

- breaks the accepted Step 3A contract that it is advisory-only and no-write
- mixes read-only extraction with write behavior
- makes schema, testing, and documentation less clear

Risks:

- accidental writes through an endpoint users already understand as no-write
- regression risk to an accepted runtime-verified Step 3A contract

Fit with human approval:

- poor because approval and suggestion boundaries blur

Fit with dry-run:

- poor because the endpoint would carry two incompatible semantics

Fit with idempotency:

- poor

Fit with auditability and provenance:

- moderate at best, but contract clarity becomes worse

Fit with future Step 4 controls and Step 5 vulnerabilities:

- poor separation of concerns

### Option D: Create a new AI-specific asset commit endpoint

Pros:

- preserves Step 3A as advisory-only
- allows strict Step 3B request and response contracts
- supports dry-run and write mode under one reviewed payload shape
- allows per-candidate create, reuse, reject, and defer decisions
- provides a clean place for duplicate rules, idempotency rules, and guardrails
- keeps provenance close to the AI onboarding workflow

Cons:

- requires new serializer, service, and guardrail files later
- duplicates some orchestration logic rather than exposing raw CRUD directly

Risks:

- scope drift if later versions try to create non-asset objects here
- temptation to allow broad `AssetWriteSerializer` fields that exceed Step 3B safety

Fit with human approval:

- strong

Fit with dry-run:

- strong

Fit with idempotency:

- strong for contract design, with known persistence limitations in v1

Fit with auditability and provenance:

- strong

Fit with future Step 4 controls and Step 5 vulnerabilities:

- strong because downstream steps can consume reviewed asset outputs without changing Step 3A semantics

### Option E: Extend Step 2 case-setup endpoint to include assets

Pros:

- Step 2 already owns the approved case context
- may seem to reduce one extra API call

Cons:

- Step 2 is already accepted and should remain about setup objects only
- assets have different duplicate, ambiguity, and review rules than setup objects
- overloading Step 2 increases regression risk across accepted behavior

Risks:

- Step 2 contract drift
- harder rollback semantics and harder focused testing

Fit with human approval:

- moderate, but too coupled

Fit with dry-run:

- moderate, but now Step 2 dry-run would cover two separate object families

Fit with idempotency:

- moderate

Fit with auditability and provenance:

- moderate

Fit with future Step 4 controls and Step 5 vulnerabilities:

- weak due to poor separation of steps

### Recommended safest option

Create a new AI-specific endpoint:

- `POST /api/ai/onboarding/assets/commit/`

Implementation structure later should mirror the accepted Step 2 and Step 3A pattern:

- thin API view
- strict input serializer
- guardrail layer
- orchestration service
- `transaction.atomic()` in write mode only

## 4. Proposed Endpoint Contract

### Endpoint definition

| Property | Recommendation |
| --- | --- |
| HTTP method | `POST` |
| URL path | `/api/ai/onboarding/assets/commit/` |
| Authentication | Required |
| Permission requirement | authenticated user plus folder-scoped asset create or view access checks depending on decision type |
| Writes to DB | yes when `dry_run=false` and approved create decisions exist; otherwise no |
| Operation types | `dry_run` and `create` |

### Authentication requirements

- require the same platform authentication families already used by Step 1, Step 2, and Step 3A
- unauthenticated requests should return `401`

### Permission requirements

- user must be authenticated
- user must be able to view the referenced `Folder`, `Perimeter`, and `ComplianceAssessment`
- if `risk_assessment_id` is provided, user must be able to view it
- create decisions require folder-scoped `add_asset` permission
- reuse decisions require visibility of the selected existing asset
- permission failures should return `403`

### Recommended high-level contract

- use one request payload shape for both dry-run and write mode
- `dry_run=true` validates everything and returns planned actions only
- `dry_run=false` executes only after explicit top-level and item-level approval

### Error response format

Two layers are recommended:

1. serializer contract errors

- HTTP `400`
- field-based validation errors
- unknown fields should use the same strict pattern as Step 2 and Step 3A, but with Step 3B wording

2. business-rule blocking errors

- HTTP `403`, `409`, or `422` depending on the condition
- structured response envelope with `status`, `blocking_errors`, `warnings`, and decision summaries where possible

Recommended structured blocking envelope:

```json
{
  "operation_type": "dry_run",
  "status": "blocked",
  "source_step1_draft_hash": "sha256:...",
  "source_asset_draft_hash": "sha256:...",
  "idempotency_key": null,
  "created_assets": [],
  "reused_assets": [],
  "rejected_assets": [],
  "deferred_assets": [],
  "skipped_assets": [],
  "planned_actions": [],
  "warnings": [],
  "blocking_errors": [
    {
      "code": "permission_denied",
      "field": "asset_decisions[1].selected_existing_asset_id",
      "detail": "You do not have permission to reuse this asset in the selected scope."
    }
  ],
  "needs_human_review": true,
  "next_allowed_steps": [
    "Resolve the blocking errors and rerun Step 3B dry-run."
  ]
}
```

## 5. Request Payload Design

### Top-level request fields

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `dry_run` | `boolean` | yes | `true` means validate and plan only; `false` means execute write mode |
| `approved_by_user` | `boolean` | yes | must be `true` when `dry_run=false` |
| `idempotency_key` | `string or null` | yes | required when `dry_run=false`; optional for dry-run |
| `source_step1_draft_hash` | `string` | yes | `sha256:<64 lowercase hex>` |
| `source_asset_draft_hash` | `string` | yes | hash of the reviewed Step 3A draft snapshot |
| `case_setup_reference` | `object` | yes | approved Step 2 context references |
| `asset_decisions` | `array` | yes | one reviewed decision per candidate or explicitly skipped candidate |

### Important source hash rule

Step 3A must remain unchanged. Since the accepted Step 3A response does not currently emit `source_asset_draft_hash`, the Step 3B design should assume the client computes it from the exact Step 3A response payload it asked the reviewer to approve.

Recommended rule:

- client computes canonical JSON for the full reviewed Step 3A draft snapshot
- client computes `sha256:<64 lowercase hex>`
- client submits that value as `source_asset_draft_hash`

This preserves the Step 3A contract while still giving Step 3B a stable provenance anchor.

### `case_setup_reference`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `folder_id` | `uuid` | yes | authoritative asset scope |
| `perimeter_id` | `uuid` | yes | used for context validation only |
| `compliance_assessment_id` | `uuid` | yes | used for context validation only |
| `risk_assessment_id` | `uuid or null` | no | used for context validation only |
| `selected_framework_id` | `uuid or null` | no | used for context validation and provenance only |

### `asset_decisions`

Each item must represent one human-reviewed Step 3A candidate.

| Field | Type | Required | Rule |
| --- | --- | --- | --- |
| `temporary_id` | `string` | yes | must match a Step 3A `candidate_assets[].temporary_id` |
| `action` | `string` | yes | one of `create`, `reuse`, `reject`, `defer` |
| `human_approved` | `boolean` | yes | must be `true` for write mode; recommended `true` for all reviewed decisions |
| `selected_existing_asset_id` | `uuid or null` | conditional | required when `action=reuse`, forbidden otherwise |
| `approved_fields` | `object or null` | conditional | required when `action=create`, forbidden otherwise |
| `original_suggestion_summary` | `object` | yes | review snapshot of the original Step 3A candidate |
| `reviewer_notes` | `string or null` | no | optional human commentary |
| `ambiguity_resolution` | `object or null` | conditional | required when the Step 3A candidate was ambiguous and action is `create` or `reuse` |
| `duplicate_resolution` | `object or null` | conditional | required when Step 3A duplicate warnings or Step 3B duplicate checks apply |

### Recommended `approved_fields` whitelist

`approved_fields` should use real platform asset field names only, but Step 3B v1 should intentionally allow only the safe subset below:

| Field | Supported in platform | Allow in Step 3B v1 | Notes |
| --- | --- | --- | --- |
| `name` | yes | yes, required | from `NameDescriptionMixin`; unique in folder scope by model validation |
| `type` | yes | yes, required | must be `PR` or `SP`; require explicit value to avoid silent defaults |
| `description` | yes | yes, optional | maps to model field directly |
| `ref_id` | yes | yes, optional | actual platform field name; response may echo it as `reference_id` |
| `asset_class` | yes | yes, optional | should be an existing visible `AssetClass` id, not free-text category |
| `owner` | yes | yes, optional | list of existing visible `Actor` ids |
| `reference_link` | yes | yes, optional | URL |
| `observation` | yes | yes, optional | reviewer note persisted on the asset if explicitly approved |

### Platform-supported but intentionally excluded from Step 3B v1

- `parent_assets`
- `support_assets`
- `filtering_labels`
- `security_objectives`
- `disaster_recovery_objectives`
- `security_capabilities`
- `recovery_capabilities`
- `security_exceptions`
- `solutions`
- `applied_controls`
- `vulnerabilities`
- `incidents`
- `organisation_objectives`
- `overridden_children_capabilities`
- `ebios_rm_studies`
- `is_business_function`
- DORA fields

These fields either introduce graph complexity, link to non-asset objects, or create scope that Step 3A does not currently review.

### Unsupported Step 3A-style business fields

The following should not be accepted in `approved_fields` because they are not direct writable Step 3B asset fields:

- `criticality`
- `proposed_asset_category`
- free-text `category`
- `status`
- generic `tags`
- `is_critical`

Notes:

- the backend `Asset` model has no dedicated generic `criticality` field
- the nearest platform concept for category is `asset_class`, which is a foreign key, not a free-text field
- the frontend shows `is_critical`, but no backend writable `Asset.is_critical` field was found in the inspected model or serializer
- generic tags are not first-class asset fields; the closest concept is `filtering_labels`, which should remain out of Step 3B v1

### Recommended request shape

```json
{
  "dry_run": true,
  "approved_by_user": false,
  "idempotency_key": null,
  "source_step1_draft_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
  "source_asset_draft_hash": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
  "case_setup_reference": {
    "folder_id": "uuid",
    "perimeter_id": "uuid",
    "compliance_assessment_id": "uuid",
    "risk_assessment_id": "uuid or null",
    "selected_framework_id": "uuid or null"
  },
  "asset_decisions": [
    {
      "temporary_id": "AST-CAND-001",
      "action": "create",
      "human_approved": true,
      "selected_existing_asset_id": null,
      "approved_fields": {
        "name": "Core Banking Application",
        "type": "PR",
        "description": "Primary banking application in approved scope.",
        "ref_id": "AST-CB-001",
        "reference_link": "https://example.local/assets/core-banking",
        "observation": "Approved after Step 3A review."
      },
      "original_suggestion_summary": {
        "proposed_name": "Core Banking Application",
        "proposed_asset_type": "PR",
        "confidence": 0.92
      },
      "reviewer_notes": "Confirmed as a primary asset.",
      "ambiguity_resolution": null,
      "duplicate_resolution": {
        "decision": "no_duplicate_found",
        "reviewed_match_ids": []
      }
    }
  ]
}
```

## 6. Response Payload Design

### Top-level response fields

| Field | Type | Notes |
| --- | --- | --- |
| `operation_type` | `string` | `dry_run` or `create` |
| `status` | `string` | recommended values: `validated`, `passed_with_warnings`, `blocked`, `created`, `reused_only`, `created_and_reused`, `completed`, `rolled_back` |
| `source_step1_draft_hash` | `string` | echo request provenance |
| `source_asset_draft_hash` | `string` | echo request provenance |
| `idempotency_key` | `string or null` | echo request |
| `created_assets` | `array` | empty in dry-run |
| `reused_assets` | `array` | summary of explicit reuse decisions |
| `rejected_assets` | `array` | summary of reviewed rejects |
| `deferred_assets` | `array` | summary of reviewed defers |
| `skipped_assets` | `array` | items not attempted because of blocking errors or rollback |
| `planned_actions` | `array` | especially important in dry-run |
| `warnings` | `array` | duplicate warnings, trace-only idempotency warnings, unsupported field removals, etc. |
| `blocking_errors` | `array` | validation or business-rule blockers |
| `needs_human_review` | `boolean` | true when unresolved blocking or review items remain |
| `next_allowed_steps` | `array` | safe workflow guidance |

### Asset summary shape for created and reused assets

Each created or reused summary should include:

- `asset_id`
- `name`
- `reference_id` if available
- `folder_id`
- `action`
- `source_temporary_id`

Recommended additional fields:

- `type`
- `ref_id` as the exact platform field echo
- `reused_existing_name` for reuse paths when helpful

### Recommended response summary shape

```json
{
  "asset_id": "uuid",
  "name": "Core Banking Application",
  "reference_id": "AST-CB-001",
  "ref_id": "AST-CB-001",
  "folder_id": "uuid",
  "action": "create",
  "source_temporary_id": "AST-CAND-001",
  "type": "PR"
}
```

### Dry-run versus write mode

- dry-run returns `planned_actions`, warnings, and blocking errors without creating assets
- write mode returns created and reused summaries and may still include warnings
- reject and defer decisions appear in both modes because they are review outcomes even when no write occurs

## 7. Human Approval Model

### Core approval rules

- User must review every suggested asset.
- AI cannot approve assets.
- User may edit name, description, `ref_id`, type, and other explicitly whitelisted asset fields before commit.
- User may reuse an existing asset instead of creating one.
- User may reject a candidate.
- User may defer a candidate.
- User may mark an ambiguous item as not an asset and reject or defer it.

### Explicit approval gates

- `approved_by_user=true` is required for write mode.
- every `asset_decisions[]` item must be explicitly reviewed
- each create or reuse item must have `human_approved=true`
- safest v1 rule: all decision items should have `human_approved=true` before write mode so the reviewed set is complete

### Ambiguity rules

- If Step 3A surfaced ambiguity flags, Step 3B must require `ambiguity_resolution` before create or reuse.
- If the reviewer concludes the item is really evidence, a control, or a vulnerability, Step 3B must not create anything and should require `action=reject` or `action=defer`.

### Duplicate rules

- If Step 3A or Step 3B surfaces duplicates, Step 3B must require `duplicate_resolution`.
- Step 3B must never auto-reuse based on duplicate matching alone.

## 8. Dry-Run Behavior

Dry-run must:

- validate the full payload
- validate `source_step1_draft_hash`
- validate `source_asset_draft_hash`
- validate `case_setup_reference`
- validate user permissions
- validate each `asset_decisions[]` item
- validate allowed asset fields only
- validate selected existing asset visibility for reuse
- validate folder-scoped uniqueness and duplicate risks for create decisions
- validate ambiguity and duplicate resolutions
- return planned actions, warnings, and blocking errors
- create no records
- update no records
- delete no records
- leave all database counts unchanged

Dry-run should also:

- normalize duplicate checks using exact name, normalized name, and `ref_id`
- warn if a reused asset falls outside the authoritative `folder_id`
- block if a create decision would violate folder-scoped uniqueness

## 9. Write Behavior

Write mode must:

- require `dry_run=false`
- require `approved_by_user=true`
- require `idempotency_key`
- require `source_asset_draft_hash`
- require `source_step1_draft_hash`
- require all reviewed items to be fully resolved
- require create and reuse items to have `human_approved=true`
- use a single atomic transaction
- create only approved `Asset` records
- reuse only explicitly selected existing assets
- return created, reused, rejected, deferred, and skipped summaries
- roll back all writes if any required create or reuse operation fails

Important nuance:

- a write request may legitimately create zero assets if every reviewed decision is `reuse`, `reject`, or `defer`
- reuse does not mutate the existing asset in v1
- reject and defer are outcome records in the response only, not database writes

## 10. Asset Creation Rules

### Real platform asset model facts from inspected code

- `Asset` is folder-scoped through `FolderMixin`
- `name` comes from `NameDescriptionMixin`
- `description` is optional
- `type` is a real platform field with choices `PR` and `SP`
- `ref_id` is supported
- `reference_link` is supported
- `owner` is supported as M2M to `Actor`
- `asset_class` is supported as a foreign key
- `observation` is supported
- no direct `perimeter` field exists on `Asset`
- no direct generic `status` field exists on `Asset`
- no dedicated generic `criticality` field exists on `Asset`
- no backend `is_critical` asset field was found

### Required fields for Step 3B create decisions

Recommended v1 required fields:

- `name`
- `type`

Derived and not directly user-editable in `approved_fields`:

- `folder` must always come from `case_setup_reference.folder_id`

### Optional Step 3B create fields

- `description`
- `ref_id`
- `asset_class`
- `owner`
- `reference_link`
- `observation`

### Folder or domain assignment rules

- Every created asset must use `case_setup_reference.folder_id`.
- `approved_fields` must not override folder per asset in v1.
- Because `Asset` has no direct `perimeter` field, folder is the authoritative creation scope.

### Reference ID rules

- platform field name is `ref_id`
- optional, max length 100
- should be trimmed
- duplicate checks should compare it case-insensitively within the selected folder
- response summaries may expose `reference_id` as a convenience alias backed by `ref_id`

### Asset type and category rules

- `type` must be one of `PR` or `SP`
- do not accept free-text type labels in write mode
- free-text category from Step 3A must not be written directly
- if the reviewer wants category mapping, map it explicitly to visible `asset_class` or leave unset

### Criticality rules

- generic criticality is advisory only in Step 3B v1
- do not persist Step 3A `criticality` directly because no dedicated generic backend field exists

### Description rules

- optional
- may be edited by the reviewer
- should be trimmed

### Owner, status, and tags rules

- `owner` may be accepted only as existing visible `Actor` ids
- generic `status` is unsupported for `Asset` and should be rejected
- generic `tags` are unsupported; the closest platform concept is `filtering_labels`, but Step 3B v1 should reject them to avoid label side effects

### Unsupported field handling

- reject unsupported fields rather than silently dropping them
- unknown top-level or nested fields should return strict serializer errors
- business-only suggestion fields such as `criticality` or free-text `category` should return Step 3B-specific validation errors when submitted in `approved_fields`

### Ambiguous category handling

- if the reviewer cannot confidently map the candidate to an asset, Step 3B must not create it
- the candidate should be rejected or deferred with `ambiguity_resolution`

### Candidate marked as evidence, control, or vulnerability

- Step 3B must not create any non-asset object
- valid outcomes are `reject` or `defer`
- response should preserve reviewer notes so the next step can act later

## 11. Asset Reuse Rules

- `selected_existing_asset_id` is required when `action=reuse`
- the selected asset must be visible to the current user
- the selected asset should be inside the authoritative folder scope by default
- if future cross-folder reuse is ever allowed, it should require an explicit design change; v1 should block it
- Step 3B must never auto-reuse based on duplicate matching alone
- Step 3B must never auto-merge assets
- Step 3B must never update the reused asset in v1
- reused assets must be returned in the response
- reuse is a reviewed selection outcome, not an asset mutation

Important v1 constraint:

- because Step 3B is asset-only and must not mutate non-asset objects, reuse does not create a persisted link to `ComplianceAssessment`, `RiskAssessment`, or other context objects in this step

## 12. Duplicate Detection Design

### Duplicate checks in both dry-run and write mode

Step 3B should run duplicate checks for every create decision using the selected folder scope.

Recommended checks:

1. exact name match in the same folder
2. normalized name match in the same folder
3. `ref_id` match in the same folder when `ref_id` is provided
4. folder-scoped visibility-aware duplicate search only
5. future similarity matching only as advisory when embeddings exist later

### Why folder scope is authoritative

- the inspected `Asset` model is folder-scoped
- model uniqueness checking uses scope-based validation and `fields_to_check = ["name"]`
- Step 3A duplicate detection already works folder-first for the same reason
- no direct `perimeter` field exists on `Asset`

### Blocking versus non-blocking duplicates

Blocking duplicates:

- exact same name in the same folder
- normalized same name in the same folder
- same `ref_id` in the same folder unless the reviewer changes the create payload or chooses reuse

Non-blocking duplicates:

- future low-confidence similarity-only matches
- weak lexical similarity without exact or normalized collision

### Reviewer choices

If a duplicate is found, the reviewer must choose one of:

- `reuse` an existing visible asset
- edit the create payload to remove the collision and rerun dry-run
- reject or defer the candidate

`create anyway` should not be allowed for exact folder-scoped name collisions because the platform model already enforces name uniqueness in scope. If future similarity-only matching is added, `create anyway` may be acceptable only for non-blocking similarity matches with reviewer rationale.

## 13. Guardrails

Step 3B must reject payloads that attempt any out-of-scope behavior.

Guardrails should reject:

- final compliance decisions
- final risk decisions
- audit closure
- risk acceptance
- evidence creation
- control creation
- vulnerability creation
- risk scenario creation
- finding creation
- remediation creation
- requirement assessment update
- unknown platform entity types
- unapproved write mode
- write mode without `idempotency_key`
- write mode without `source_step1_draft_hash`
- write mode without `source_asset_draft_hash`
- create or reuse items without human approval
- ambiguous assets without resolution
- duplicate candidates without decision
- unknown top-level fields
- unknown nested fields

Recommended examples of forbidden fields to reject at the serializer or guardrail layer:

- `applied_control_drafts`
- `vulnerability_drafts`
- `evidence_drafts`
- `risk_scenario_drafts`
- `compliance_result`
- `risk_acceptance`
- `audit_closure`
- `workflow_case_id`

## 14. Idempotency Strategy

### Required contract

- `idempotency_key` is required for write mode
- `idempotency_key` may be omitted in dry-run
- `source_asset_draft_hash` and `source_step1_draft_hash` should travel with the same request

### Recommended key interpretation

The effective write intent is the combination of:

- `idempotency_key`
- `source_asset_draft_hash`
- `source_step1_draft_hash`
- authoritative `folder_id`

### Current platform limitation

No inspected persistent idempotency receipt table exists for this workflow.

Therefore v1 should explicitly document a trace-only limitation:

- the endpoint can require an `idempotency_key`
- the endpoint can log or echo it for traceability
- the endpoint cannot guarantee durable replay-safe receipts across process restarts unless a persistent idempotency store is added later

### Practical v1 safety behavior

- use duplicate detection to prevent obvious accidental duplicate creations
- if a retry occurs after a partial network failure but the original transaction committed, a later retry may surface as duplicate conflict rather than a replayed success receipt
- clients should first query or rerun dry-run before blindly retrying create after an uncertain network failure

### Future improvement

- add a persistent idempotency receipt table keyed by `idempotency_key` and source hashes
- store normalized request hash and final response summary

## 15. Transaction and Rollback Strategy

### Recommended rule

- use one atomic transaction for write mode
- partial success is not allowed for create or reuse failures

### Failure cases

If asset 1 creates and asset 2 fails:

- roll back asset 1
- return `status=rolled_back`
- place attempted items into `skipped_assets` or `blocking_errors` with explanation

If a reuse permission check fails:

- treat the whole write as failed
- roll back any earlier creates

If a duplicate appears between dry-run and commit:

- block the write
- roll back any earlier creates in that transaction
- return a duplicate conflict response and require another dry-run or decision edit

If one candidate is rejected or deferred:

- that is not a failure
- no asset is created for that item
- other create or reuse decisions may proceed if no blocking errors exist

### Recommended response after rollback

- HTTP `409` for duplicate race or idempotency conflict-like outcomes
- HTTP `422` for validation blockers discovered during write preparation
- structured response with `status=rolled_back`, created lists empty, and `blocking_errors` populated

## 16. Permission and RBAC Design

### Core rules

- authentication required
- folder or domain visibility checks required
- case context visibility checks required
- create decisions require folder-scoped `add_asset`
- reuse decisions require visibility of the selected asset within the allowed scope

### Context checks

Step 3B should validate that:

- `folder_id` is visible to the current user
- `perimeter_id` is visible and belongs to the same folder context
- `compliance_assessment_id` is visible and belongs to the same folder and perimeter context
- `risk_assessment_id`, if supplied, is visible and belongs to the same folder and perimeter context
- `selected_framework_id`, if supplied, is visible if the implementation chooses to validate it

### Reuse scope rules

- v1 should require the reused asset to belong to the same `folder_id`
- cross-folder reuse should be rejected as out of scope for this step

### Superuser and admin behavior

- superusers or admin users may pass permission checks more broadly
- they are still bound by Step 3B guardrails and asset-only scope

### Permission denied format

Recommended pattern:

```json
{
  "operation_type": "create",
  "status": "blocked",
  "source_step1_draft_hash": "sha256:...",
  "source_asset_draft_hash": "sha256:...",
  "idempotency_key": "asset-commit-001",
  "created_assets": [],
  "reused_assets": [],
  "rejected_assets": [],
  "deferred_assets": [],
  "skipped_assets": [],
  "planned_actions": [],
  "warnings": [],
  "blocking_errors": [
    {
      "code": "permission_denied",
      "field": "asset_decisions[0].approved_fields",
      "detail": "You do not have permission to add assets in the selected folder."
    }
  ],
  "needs_human_review": true,
  "next_allowed_steps": [
    "Request the required folder permission or choose reuse/reject/defer."
  ]
}
```

## 17. Provenance and Auditability

### Required trace fields

Step 3B responses and internal logs should preserve:

- `source_step1_draft_hash`
- `source_asset_draft_hash`
- Step 3A `temporary_id`
- original suggestion summary
- reviewer notes
- `idempotency_key`
- approving user identity from the authenticated request
- server timestamp on execution

### Recommended v1 provenance approach

- keep provenance in the request, response, server logs, and any future audit trail hooks
- do not make `WorkflowCase` a hard dependency now

### Future options

- store Step 3B provenance in `WorkflowCase` later if the platform decides AI workflow state belongs there
- or add a dedicated onboarding receipt model later

For v1, provenance must be traceable without introducing a new persistent dependency.

## 18. Frontend UX Design

The future Step 3B review screen should begin from the accepted Step 3A suggestion response.

Recommended UX flow:

1. show Step 3A candidate assets grouped by suggested category or reviewer bucket
2. show ambiguity warnings prominently
3. show duplicate matches inline per candidate
4. require the user to choose one action per candidate: create, reuse, reject, defer
5. when create is chosen, allow editing only approved asset fields
6. when reuse is chosen, require selecting one visible existing asset
7. show a dry-run preview before write mode
8. require final confirmation before submit with `approved_by_user=true`
9. show a success screen with created and reused assets only

Required messaging:

- clear label that only `Asset` records are created in this step
- clear separation from controls, vulnerabilities, evidence, and risk workflows
- clear note that ambiguous non-assets must be rejected or deferred here and handled by later steps

## 19. API Payload Examples

### A. Dry-run request with create, reuse, reject, and defer decisions

```json
{
  "dry_run": true,
  "approved_by_user": false,
  "idempotency_key": null,
  "source_step1_draft_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
  "source_asset_draft_hash": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
  "case_setup_reference": {
    "folder_id": "8a6f2bdb-fb7d-412d-9fb6-c99409a19909",
    "perimeter_id": "1da46d44-1f0d-4b52-81ef-1991ae0866b2",
    "compliance_assessment_id": "2ab9d352-b443-4592-9e8b-87a85df2fa4d",
    "risk_assessment_id": "a26b14b5-716a-45cc-a99e-febee2fca63c",
    "selected_framework_id": "02d48ef4-00de-4134-b954-5a1ada2a9833"
  },
  "asset_decisions": [
    {
      "temporary_id": "AST-CAND-001",
      "action": "create",
      "human_approved": true,
      "selected_existing_asset_id": null,
      "approved_fields": {
        "name": "Core Banking Application",
        "type": "PR",
        "description": "Primary banking application in approved scope.",
        "ref_id": "AST-CB-001"
      },
      "original_suggestion_summary": {
        "proposed_name": "Core Banking Application",
        "confidence": 0.92
      },
      "reviewer_notes": "Confirmed.",
      "ambiguity_resolution": null,
      "duplicate_resolution": {
        "decision": "no_duplicate_found",
        "reviewed_match_ids": []
      }
    },
    {
      "temporary_id": "AST-CAND-006",
      "action": "reuse",
      "human_approved": true,
      "selected_existing_asset_id": "0c7cc9ad-95c4-4932-a4fb-2718f8392bca",
      "approved_fields": null,
      "original_suggestion_summary": {
        "proposed_name": "Identity Provider / IAM System",
        "confidence": 0.88
      },
      "reviewer_notes": "Existing IAM asset should be reused.",
      "ambiguity_resolution": null,
      "duplicate_resolution": {
        "decision": "reuse_existing",
        "reviewed_match_ids": [
          "0c7cc9ad-95c4-4932-a4fb-2718f8392bca"
        ]
      }
    },
    {
      "temporary_id": "AST-CAND-004",
      "action": "reject",
      "human_approved": true,
      "selected_existing_asset_id": null,
      "approved_fields": null,
      "original_suggestion_summary": {
        "proposed_name": "Access Review Records",
        "confidence": 0.72
      },
      "reviewer_notes": "Treat later as evidence, not as an asset.",
      "ambiguity_resolution": {
        "resolution_type": "reclassified_not_asset",
        "resolution_note": "Evidence candidate"
      },
      "duplicate_resolution": null
    },
    {
      "temporary_id": "AST-CAND-007",
      "action": "defer",
      "human_approved": true,
      "selected_existing_asset_id": null,
      "approved_fields": null,
      "original_suggestion_summary": {
        "proposed_name": "IAM Policies and Procedures",
        "confidence": 0.63
      },
      "reviewer_notes": "Need governance decision first.",
      "ambiguity_resolution": {
        "resolution_type": "deferred_for_manual_classification",
        "resolution_note": "May be documentation rather than asset"
      },
      "duplicate_resolution": null
    }
  ]
}
```

### B. Dry-run success response

```json
{
  "operation_type": "dry_run",
  "status": "validated",
  "source_step1_draft_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
  "source_asset_draft_hash": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
  "idempotency_key": null,
  "created_assets": [],
  "reused_assets": [],
  "rejected_assets": [
    {
      "source_temporary_id": "AST-CAND-004",
      "action": "reject",
      "name": "Access Review Records"
    }
  ],
  "deferred_assets": [
    {
      "source_temporary_id": "AST-CAND-007",
      "action": "defer",
      "name": "IAM Policies and Procedures"
    }
  ],
  "skipped_assets": [],
  "planned_actions": [
    {
      "source_temporary_id": "AST-CAND-001",
      "action": "create",
      "target_name": "Core Banking Application",
      "status": "planned"
    },
    {
      "source_temporary_id": "AST-CAND-006",
      "action": "reuse",
      "target_name": "Identity Provider / IAM System",
      "status": "planned"
    }
  ],
  "warnings": [],
  "blocking_errors": [],
  "needs_human_review": false,
  "next_allowed_steps": [
    "Submit the same reviewed payload with dry_run=false and approved_by_user=true."
  ]
}
```

### C. Dry-run duplicate warning response

```json
{
  "operation_type": "dry_run",
  "status": "passed_with_warnings",
  "source_step1_draft_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
  "source_asset_draft_hash": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
  "idempotency_key": null,
  "created_assets": [],
  "reused_assets": [],
  "rejected_assets": [],
  "deferred_assets": [],
  "skipped_assets": [],
  "planned_actions": [
    {
      "source_temporary_id": "AST-CAND-006",
      "action": "reuse",
      "target_name": "Identity Provider / IAM System",
      "status": "planned"
    }
  ],
  "warnings": [
    {
      "code": "duplicate_candidate_detected",
      "field": "asset_decisions[0]",
      "detail": "A folder-scoped duplicate exists for Identity Provider / IAM System. Reuse is recommended."
    }
  ],
  "blocking_errors": [],
  "needs_human_review": true,
  "next_allowed_steps": [
    "Confirm reuse or change the create decision and rerun dry-run."
  ]
}
```

### D. Dry-run blocking ambiguity response

```json
{
  "operation_type": "dry_run",
  "status": "blocked",
  "source_step1_draft_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
  "source_asset_draft_hash": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
  "idempotency_key": null,
  "created_assets": [],
  "reused_assets": [],
  "rejected_assets": [],
  "deferred_assets": [],
  "skipped_assets": [],
  "planned_actions": [],
  "warnings": [],
  "blocking_errors": [
    {
      "code": "ambiguity_resolution_required",
      "field": "asset_decisions[2].ambiguity_resolution",
      "detail": "Ambiguous candidate Access Review Records must be resolved before create or reuse."
    }
  ],
  "needs_human_review": true,
  "next_allowed_steps": [
    "Reject, defer, or explicitly resolve the ambiguous candidate and rerun dry-run."
  ]
}
```

### E. Write request success

```json
{
  "dry_run": false,
  "approved_by_user": true,
  "idempotency_key": "asset-commit-2026-07-11-001",
  "source_step1_draft_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
  "source_asset_draft_hash": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
  "case_setup_reference": {
    "folder_id": "8a6f2bdb-fb7d-412d-9fb6-c99409a19909",
    "perimeter_id": "1da46d44-1f0d-4b52-81ef-1991ae0866b2",
    "compliance_assessment_id": "2ab9d352-b443-4592-9e8b-87a85df2fa4d",
    "risk_assessment_id": "a26b14b5-716a-45cc-a99e-febee2fca63c",
    "selected_framework_id": "02d48ef4-00de-4134-b954-5a1ada2a9833"
  },
  "asset_decisions": [
    {
      "temporary_id": "AST-CAND-001",
      "action": "create",
      "human_approved": true,
      "selected_existing_asset_id": null,
      "approved_fields": {
        "name": "Core Banking Application",
        "type": "PR",
        "description": "Primary banking application in approved scope.",
        "ref_id": "AST-CB-001"
      },
      "original_suggestion_summary": {
        "proposed_name": "Core Banking Application",
        "confidence": 0.92
      },
      "reviewer_notes": "Confirmed.",
      "ambiguity_resolution": null,
      "duplicate_resolution": {
        "decision": "no_duplicate_found",
        "reviewed_match_ids": []
      }
    },
    {
      "temporary_id": "AST-CAND-006",
      "action": "reuse",
      "human_approved": true,
      "selected_existing_asset_id": "0c7cc9ad-95c4-4932-a4fb-2718f8392bca",
      "approved_fields": null,
      "original_suggestion_summary": {
        "proposed_name": "Identity Provider / IAM System",
        "confidence": 0.88
      },
      "reviewer_notes": "Reuse existing IAM asset.",
      "ambiguity_resolution": null,
      "duplicate_resolution": {
        "decision": "reuse_existing",
        "reviewed_match_ids": [
          "0c7cc9ad-95c4-4932-a4fb-2718f8392bca"
        ]
      }
    }
  ]
}
```

### F. Write success response

```json
{
  "operation_type": "create",
  "status": "created_and_reused",
  "source_step1_draft_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
  "source_asset_draft_hash": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
  "idempotency_key": "asset-commit-2026-07-11-001",
  "created_assets": [
    {
      "asset_id": "6d11fb76-4025-4c6c-bf32-7a8260fe05a2",
      "name": "Core Banking Application",
      "reference_id": "AST-CB-001",
      "ref_id": "AST-CB-001",
      "folder_id": "8a6f2bdb-fb7d-412d-9fb6-c99409a19909",
      "action": "create",
      "source_temporary_id": "AST-CAND-001",
      "type": "PR"
    }
  ],
  "reused_assets": [
    {
      "asset_id": "0c7cc9ad-95c4-4932-a4fb-2718f8392bca",
      "name": "Identity Provider / IAM System",
      "reference_id": null,
      "ref_id": null,
      "folder_id": "8a6f2bdb-fb7d-412d-9fb6-c99409a19909",
      "action": "reuse",
      "source_temporary_id": "AST-CAND-006",
      "type": "SP"
    }
  ],
  "rejected_assets": [],
  "deferred_assets": [],
  "skipped_assets": [],
  "planned_actions": [],
  "warnings": [
    {
      "code": "idempotency_trace_only",
      "detail": "Idempotency is trace-only in v1 because no persistent receipt store exists."
    }
  ],
  "blocking_errors": [],
  "needs_human_review": false,
  "next_allowed_steps": [
    "Proceed to later AI-assisted control or vulnerability review steps using the approved asset set."
  ]
}
```

### G. Missing approval error

```json
{
  "approved_by_user": [
    "approved_by_user must be true when dry_run is false."
  ]
}
```

### H. Missing idempotency key error

```json
{
  "idempotency_key": [
    "idempotency_key is required when dry_run is false."
  ]
}
```

### I. Forbidden evidence, control, or vulnerability payload error

```json
{
  "asset_decisions": [
    {
      "approved_fields": {
        "evidence_id": [
          "This field is not allowed in Step 3B."
        ],
        "applied_control_id": [
          "This field is not allowed in Step 3B."
        ],
        "vulnerability_id": [
          "This field is not allowed in Step 3B."
        ]
      }
    }
  ]
}
```

### J. Duplicate conflict during write response

```json
{
  "operation_type": "create",
  "status": "rolled_back",
  "source_step1_draft_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
  "source_asset_draft_hash": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
  "idempotency_key": "asset-commit-2026-07-11-001",
  "created_assets": [],
  "reused_assets": [],
  "rejected_assets": [],
  "deferred_assets": [],
  "skipped_assets": [
    {
      "source_temporary_id": "AST-CAND-001",
      "action": "create",
      "skip_reason": "transaction_rolled_back"
    }
  ],
  "planned_actions": [],
  "warnings": [],
  "blocking_errors": [
    {
      "code": "duplicate_conflict_during_write",
      "field": "asset_decisions[0].approved_fields.name",
      "detail": "An asset with the same folder-scoped name appeared between dry-run and commit."
    }
  ],
  "needs_human_review": true,
  "next_allowed_steps": [
    "Rerun Step 3B dry-run and choose reuse, rename, reject, or defer."
  ]
}
```

### K. Permission denied response

```json
{
  "operation_type": "dry_run",
  "status": "blocked",
  "source_step1_draft_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
  "source_asset_draft_hash": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
  "idempotency_key": null,
  "created_assets": [],
  "reused_assets": [],
  "rejected_assets": [],
  "deferred_assets": [],
  "skipped_assets": [],
  "planned_actions": [],
  "warnings": [],
  "blocking_errors": [
    {
      "code": "permission_denied",
      "field": "asset_decisions[0].approved_fields",
      "detail": "You do not have permission to add assets in the selected folder."
    }
  ],
  "needs_human_review": true,
  "next_allowed_steps": [
    "Request the required permission or change the decision."
  ]
}
```

### L. Transaction rollback response

```json
{
  "operation_type": "create",
  "status": "rolled_back",
  "source_step1_draft_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
  "source_asset_draft_hash": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
  "idempotency_key": "asset-commit-2026-07-11-001",
  "created_assets": [],
  "reused_assets": [],
  "rejected_assets": [],
  "deferred_assets": [],
  "skipped_assets": [
    {
      "source_temporary_id": "AST-CAND-001",
      "action": "create",
      "skip_reason": "transaction_rolled_back"
    },
    {
      "source_temporary_id": "AST-CAND-006",
      "action": "reuse",
      "skip_reason": "transaction_rolled_back"
    }
  ],
  "planned_actions": [],
  "warnings": [],
  "blocking_errors": [
    {
      "code": "write_transaction_failed",
      "field": "asset_decisions[1]",
      "detail": "The write transaction was rolled back because one required operation failed."
    }
  ],
  "needs_human_review": true,
  "next_allowed_steps": [
    "Review the failure, rerun dry-run, and resubmit only after the blocking issue is resolved."
  ]
}
```

## 20. Test Plan for Future Step 3B Implementation

Future implementation should include focused tests for:

- auth required
- dry-run success
- dry-run no-write proof
- write mode requires `approved_by_user`
- write mode requires `idempotency_key`
- write mode requires `source_asset_draft_hash`
- write mode requires `source_step1_draft_hash`
- create approved `Asset`
- reuse existing asset
- reject decision creates nothing
- defer decision creates nothing
- duplicate detection for exact name
- duplicate detection for normalized name
- duplicate detection for `ref_id`
- duplicate blocking behavior
- ambiguous candidate requires resolution
- permission denied on create
- permission denied on reuse
- invalid existing asset reuse id
- cross-folder reuse blocked
- unknown top-level fields rejected
- unknown nested fields rejected
- forbidden controls, evidence, vulnerabilities, risks rejected
- final compliance decision rejected
- risk acceptance rejected
- audit closure rejected
- transaction rollback on second create failure
- transaction rollback on reuse permission failure
- no out-of-scope objects created
- Step 1 regression
- Step 2 regression
- Step 3A regression

## 21. Files Expected to Change During Step 3B Implementation

Likely backend files for future implementation:

- `backend/ai_onboarding/asset_commit_serializers.py`
- `backend/ai_onboarding/asset_commit_guardrails.py`
- `backend/ai_onboarding/asset_commit_service.py`
- `backend/ai_onboarding/views.py`
- `backend/ai_onboarding/urls.py`
- `backend/app_tests/api/test_api_ai_asset_commit.py`

Possible later frontend files:

- review and submit screens that consume Step 3A suggestions and Step 3B dry-run and write responses

No files beyond this design document should change now.

## 22. Open Questions / Needs Verification

- exact final Step 3B whitelist for optional asset fields such as `asset_class`, `owner`, and `observation`
- whether Step 3B v1 should permit `owner` assignment immediately or defer it for simplicity
- whether `asset_class` should be optional by visible id only or omitted from v1
- whether the frontend should compute `source_asset_draft_hash` or whether a later Step 3A enhancement should echo it without changing current accepted behavior
- whether similarity-based duplicate warnings should be added later
- whether `create_anyway` should ever be allowed for non-blocking similarity matches
- whether a persistent idempotency store should be introduced before Step 3B write mode goes live
- whether provenance should later be stored in `WorkflowCase` or a dedicated onboarding receipt model
- whether a later step should persist reviewed asset selections onto another orchestration object without making that a Step 3B dependency

## 23. Step 3B Design Acceptance Criteria

Before implementation begins, the following should be true:

- the design keeps Step 1, Step 2, and Step 3A contracts unchanged
- Step 3B is clearly asset-only
- Step 3B never creates or mutates controls, vulnerabilities, evidence, risks, findings, remediation, requirement results, risk acceptance, final decisions, or closure state
- Step 3B supports both `dry_run` and approved write mode
- Step 3B requires explicit human approval
- Step 3B uses a dedicated endpoint under `ai_onboarding`
- the request payload is strict and rejects unknown fields
- the approved asset field whitelist is explicit and grounded in the real platform model
- duplicate detection and ambiguity handling are defined for both dry-run and write mode
- atomic rollback behavior is defined
- idempotency behavior and limitations are documented honestly
- permission and folder-scope rules are defined
- provenance is preserved without making `WorkflowCase` mandatory
- future implementation can be tested with focused API tests and without widening scope into non-asset GRC objects
