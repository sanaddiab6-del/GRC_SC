# AI Asset Extractor Step 3 Design

## 1. Executive Summary

Step 3 introduces the next controlled stage in the AI onboarding workflow: extracting, classifying, reviewing, and eventually creating or reusing `Asset` records from an already accepted case context.

The accepted workflow before Step 3 is:

- Step 1: `POST /api/ai/onboarding/case-intake/`
  - advisory-only
  - no database writes
  - returns draft JSON that may include early `asset_drafts`
- Step 2: `POST /api/ai/onboarding/case-setup/`
  - supports `dry_run`
  - supports approved create
  - creates or reuses only `Folder`, `Perimeter`, `ComplianceAssessment`, and optional `RiskAssessment`

Step 3 should begin only after Step 2 has established the real platform context, because the platform `Asset` model is folder-scoped and because the case should already have an approved `Folder`, `Perimeter`, `ComplianceAssessment`, and optional `RiskAssessment` before asset creation is considered.

Step 3 is advisory-first. The AI may suggest candidate assets from:

- the Step 1 case intake draft
- the Step 2 created or reused setup objects
- the original scenario text
- organization and domain context
- perimeter and scope context
- selected framework context
- audit context
- optional risk assessment context

Step 3 must not create assets automatically. Every candidate asset must remain human-reviewed and human-approved before any write path is allowed.

### Recommended split

Step 3 should be split into two endpoints:

1. an advisory suggestion endpoint
2. a separate approved commit endpoint

Recommended future routes:

- `POST /api/ai/onboarding/assets/suggest/`
- `POST /api/ai/onboarding/assets/commit/`

### Safest architecture recommendation

The safest design is a new Step 3 pair of endpoints under `ai_onboarding`, following the Step 1 and Step 2 pattern:

- thin API view
- strict serializer contract
- provider or deterministic fallback for suggestions
- explicit guardrails
- orchestration service
- `transaction.atomic()` in commit write mode only

The public `Asset` CRUD API at `/api/assets/` should remain the underlying object creation mechanism later, but Step 3 should not expose raw CRUD semantics directly as its user-facing contract.

This recommendation is anchored in the inspected codebase:

- `Asset` is folder-scoped in `backend/core/models.py`
- `AssetWriteSerializer` already enforces folder RBAC and M2M visibility in `backend/core/serializers.py`
- `AssetViewSet` already exposes `autocomplete` and `batch-create` helpers in `backend/core/views.py`
- existing write helpers do not provide Step 3 needs such as AI rationale, human approval gating, dry-run, idempotency, or out-of-scope rejection

## 2. Step 3 Scope

### In scope

- analyze approved case context and extract candidate `Asset` suggestions
- classify candidates into platform-aligned asset types or categories when possible
- detect likely duplicates against existing folder-scoped assets
- return rationale, source text traceability, ambiguity flags, and confidence
- allow the user to accept, edit, reuse, reject, or defer candidate assets
- support a future commit flow that creates or reuses only approved `Asset` records
- support `dry_run` for the future commit flow

### Out of scope

- `AppliedControl` creation
- `Vulnerability` creation
- `RiskScenario` creation
- `Evidence` creation
- `RequirementAssessment` result updates
- `Finding` or `FindingsAssessment` generation
- remediation or action plan generation
- `RiskAcceptance`
- audit closure
- final compliance decisions
- final risk decisions
- framework loading or library import
- mandatory `WorkflowCase` persistence

### Objects Step 3 may suggest

- `Asset`
- existing `Asset` matches for possible reuse
- non-asset ambiguity classifications in advisory form only, such as:
  - likely evidence item
  - likely control item
  - likely vulnerability item

### Objects Step 3 must not suggest as create targets

- `AppliedControl`
- `Vulnerability`
- `RiskScenario`
- `Evidence`
- `Finding`
- `RiskAcceptance`
- any invented platform entity

### Safety boundaries

- suggestion mode must never write to the database
- commit write mode must require explicit user approval
- commit write mode must create or reuse only `Asset`
- Step 3 must not mutate `ComplianceAssessment`, `RiskAssessment`, `AppliedControl`, `Vulnerability`, `Evidence`, or `RiskScenario` records in v1
- Step 3 should treat perimeter and audit relevance as advisory metadata because `Asset` has no direct `perimeter` field
- Step 3 should not populate complex asset graph fields by default in v1, such as broad M2M links to controls, vulnerabilities, incidents, or evidence

### Human review requirements

- every candidate asset must surface AI rationale
- every candidate asset must surface confidence
- every candidate asset must surface source text references
- every ambiguous candidate must be flagged rather than forced into `Asset`
- every create or reuse decision must be human-approved before write mode

## 3. Business-to-Platform Mapping

Step 3 must translate business terms into the platform `Asset` model carefully. Not everything described in a scenario is a true asset create target.

### Mapping guidance

#### Core Banking Application

- likely true platform asset: yes
- recommended mapping: `Asset`
- typical classification: application or system asset
- likely `type`: `PR` primary

#### User Accounts

- ambiguous
- may be a valid `Asset` if the organization tracks account populations, identity stores, or account estates as governed assets
- should not default to one asset per person or one asset per login account
- recommended treatment: suggest as a grouped or scoped asset candidate, for example `Production User Accounts`

#### Privileged Admin Accounts

- often a valid candidate asset when the scenario concerns privileged identity scope
- may be represented as an account estate, privileged access surface, or administrative identity domain
- also overlaps with future vulnerability and control work
- recommended treatment: suggest as asset only with an ambiguity note

#### Access Review Records

- ambiguous
- may be a true information asset if the organization treats the record set or register as a managed asset
- may instead be future `Evidence`
- recommended default: suggest as ambiguous and allow reviewer to reclassify to evidence

#### VPN / Remote Access

- often a true platform asset
- recommended mapping: service or infrastructure `Asset`
- may later also connect to `AppliedControl` or `Vulnerability` work

#### IAM System

- likely true platform asset: yes
- recommended mapping: service, platform, or system `Asset`

#### MFA Service

- ambiguous
- if the wording refers to an actual service or platform, it may be an `Asset`
- if the wording refers to a missing security capability, it is more likely a control gap than an asset
- recommended default: flag ambiguity when the scenario says the organization lacks MFA rather than naming a concrete MFA system

#### PAM Process or PAM System

- ambiguous
- a concrete PAM tool may be an `Asset`
- a PAM operating process may also be modeled as an asset if the organization catalogs critical processes as assets
- if the text only says "no PAM", it may be better treated later as a control gap

#### Policy / Procedure Documents

- often not a default Step 3 create target
- may be future evidence or control documentation rather than `Asset`
- may be a true information asset only if the organization explicitly catalogs policy sets as managed assets
- recommended default: classify as ambiguous and allow reclassification to evidence or control documentation

### Business case mapping example

For the example case:

- `Core Banking Application`: strong asset candidate
- `Production User Accounts`: possible asset candidate with ambiguity flag
- `Privileged Admin Accounts`: possible asset candidate with ambiguity flag
- `Access Review Records`: ambiguous, often evidence later
- `Remote Access / VPN Service`: strong asset candidate
- `Identity Provider / IAM System`: strong asset candidate
- `PAM Solution or PAM Process Placeholder`: ambiguous, depends on wording and actual implementation
- `MFA Service or MFA Control Surface`: ambiguous, depends on whether a concrete system exists
- `IAM Policies and Procedures`: likely evidence or control documentation later
- `User Provisioning Records`: ambiguous, often evidence or record asset depending on governance model

### Design rule

If a candidate can reasonably be an asset, evidence item, or control concept, Step 3 must not force it into `Asset`. It must either:

- mark it ambiguous
- place it in `rejected_candidates`
- allow reviewer reclassification

## 4. Recommended Architecture

### Option A: Add asset suggestions to Step 1 response

#### Pros

- no new endpoint required
- Step 1 already returns advisory `asset_drafts`
- can give an early preview before setup is approved

#### Cons

- Step 1 runs before real folder, perimeter, and assessment IDs exist
- Step 1 suggestions are intentionally broad and speculative
- duplicate detection is weaker before real folder scope exists
- cannot safely anchor candidate assets to approved case setup objects

#### Risks

- users may mistake early Step 1 asset drafts for Step 3-ready suggestions
- increased pressure to overload Step 1 with post-setup logic

#### Fit with human approval model

- partial fit only

#### Fit with dry-run

- weak fit

#### Fit with future Step 4 and Step 5

- weak fit because downstream controls and vulnerabilities need approved asset context, not speculative intake-only asset ideas

### Option B: Add asset suggestions to Step 2 response

#### Pros

- Step 2 has access to approved setup decisions and real object IDs
- could reduce one frontend round trip

#### Cons

- mixes case setup and asset extraction into one endpoint
- Step 2 is accepted and should remain narrowly focused
- increases the blast radius of future Step 2 changes
- makes Step 2 harder to reason about and harder to regression test

#### Risks

- Step 2 contract drift
- future asset logic accidentally mutates Step 2 semantics

#### Fit with human approval model

- moderate fit, but too coupled

#### Fit with dry-run

- moderate fit, but Step 2 dry-run should stay about setup objects only

#### Fit with future Step 4 and Step 5

- poor separation of concerns

### Option C: Create a new Step 3 advisory endpoint under `ai_onboarding`

#### Pros

- clean separation from Step 1 and Step 2
- can use approved case setup context as input
- can follow the existing Step 1 provider or fallback and validation pattern
- can remain read-only
- can return asset-specific ambiguity and duplicate information without write semantics

#### Cons

- requires a new serializer and service layer
- requires new response contract design

#### Risks

- possible duplication of some extraction logic already sketched in Step 1 asset drafts

#### Fit with human approval model

- strong fit

#### Fit with dry-run

- strong fit because suggestion is inherently read-only

#### Fit with future Step 4 and Step 5

- strong fit because downstream steps can consume approved assets cleanly

### Option D: Create a new approved-create endpoint for assets

#### Pros

- allows explicit review to write transition
- can support `dry_run`, approval gating, and idempotency
- can keep commit logic asset-only

#### Cons

- requires orchestration logic on top of existing `AssetWriteSerializer`
- requires explicit guardrails and duplicate logic

#### Risks

- if not carefully scoped, it could grow into a general graph creation endpoint

#### Fit with human approval model

- strong fit

#### Fit with dry-run

- strong fit

#### Fit with future Step 4 and Step 5

- strong fit because it yields approved asset IDs for later control and vulnerability workflows

### Option E: Use frontend-only orchestration with existing Asset CRUD APIs

#### Pros

- can reuse existing UI CRUD patterns
- can call existing `/api/assets/` endpoint directly

#### Cons

- no unified backend contract for AI rationale or ambiguity handling
- no backend dry-run semantics
- no backend idempotency semantics
- no transaction boundary across multi-asset create or reuse decisions

#### Risks

- inconsistent behavior across clients
- accidental scope drift into direct raw CRUD

#### Fit with human approval model

- moderate UX fit, weak backend fit

#### Fit with dry-run

- poor fit

#### Fit with future Step 4 and Step 5

- weak fit because later steps need a stable reviewed draft contract

### Option F: Reuse existing Asset CRUD API directly

#### Pros

- no new endpoint family
- existing serializers already enforce folder RBAC and graph validation

#### Cons

- raw CRUD knows nothing about Step 1 or Step 2 provenance
- raw CRUD has no AI-specific request or response contract
- raw CRUD has no suggestion, duplicate candidate, ambiguity, or approval workflow semantics
- raw CRUD does not support Step 3-specific `dry_run`

#### Risks

- direct writes without a review-first contract
- frontend has to invent business logic that belongs in backend orchestration

#### Fit with human approval model

- poor fit

#### Fit with dry-run

- poor fit

#### Fit with future Step 4 and Step 5

- poor fit as a primary API contract

### Safest recommendation

Use two new Step 3 endpoints under `ai_onboarding`:

- advisory suggestion endpoint
- approved commit endpoint

Internally, later implementation may delegate actual creates to the existing `AssetWriteSerializer`, but Step 3 should own its own AI-facing contract.

## 5. Proposed Step 3 Endpoint Strategy

### A. Advisory endpoint

#### Method

- `POST`

#### Recommended URL path

- `POST /api/ai/onboarding/assets/suggest/`

#### Authentication

- required
- support existing platform token and JWT mechanisms

#### Permission requirements

- authenticated user required
- caller must be able to view the referenced `Folder`, `Perimeter`, `ComplianceAssessment`, and optional `RiskAssessment`
- endpoint may use `IsAuthenticated` at the view layer and perform object visibility checks in the service layer

#### Database writes

- none

#### Request payload summary

- case provenance
- step2 object IDs
- original scenario and scope text
- known weaknesses
- optional framework and risk context
- locale and strict mode

#### Response payload summary

- advisory draft only
- candidate assets
- duplicate candidates
- rejected candidates
- warnings
- blocking questions
- needs human review

#### Error response format

- `400` for request contract validation errors
- `401` for unauthenticated calls
- `403` for referenced object visibility failures
- `404` if referenced objects are not found
- `422` for provider output validation failure or guardrail failure

### B. Approved commit endpoint

#### Method

- `POST`

#### Recommended URL path

- `POST /api/ai/onboarding/assets/commit/`

#### Authentication

- required

#### Permission requirements

- authenticated user required
- dry-run must validate whether the caller can create assets in the selected folder
- write mode must require actual `add_asset` permission in the target folder
- any reused asset selected must be visible to the caller

#### Database writes

- none when `dry_run=true`
- allowed only when `dry_run=false`, `approved_by_user=true`, and the payload passes all validations

#### Request payload summary

- approved asset decisions only
- `source_asset_draft_hash`
- `approved_by_user`
- `idempotency_key`
- same case setup context used by the suggestion stage

#### Response payload summary

- `operation_type`: `dry_run` or `commit`
- created assets
- reused assets
- rejected assets
- deferred assets
- duplicate conflicts
- warnings
- blocking errors

#### Error response format

- `400` for contract validation errors such as missing approval or idempotency key
- `401` for unauthenticated calls
- `403` for folder permission failures
- `404` for selected existing asset not found or not visible
- `409` for duplicate or idempotency conflict if future receipt persistence is added
- `422` for guardrail failure or out-of-scope asset payloads

## 6. Advisory Asset Suggestion Contract

### Request contract

Recommended request shape:

```json
{
  "source_step1_draft_hash": "sha256:...",
  "case_setup_reference": {
    "source": "step2_case_setup",
    "step2_schema_version": "0.1.0",
    "folder_id": "uuid",
    "perimeter_id": "uuid",
    "compliance_assessment_id": "uuid",
    "risk_assessment_id": "uuid or null",
    "framework_id": "uuid or null"
  },
  "folder_id": "uuid",
  "perimeter_id": "uuid",
  "compliance_assessment_id": "uuid",
  "risk_assessment_id": "uuid or null",
  "scenario_text": "string",
  "scope_summary": "string",
  "known_weaknesses": ["string"],
  "selected_framework_id": "uuid or null",
  "user_locale": "en",
  "strict_mode": true
}
```

### Required request fields

- `source_step1_draft_hash`
- `case_setup_reference`
- `folder_id`
- `perimeter_id`
- `compliance_assessment_id`
- `scenario_text` or `scope_summary`
- `user_locale`
- `strict_mode`

### Response contract

Recommended success shape:

```json
{
  "draft_type": "AiAssetSuggestionDraft",
  "schema_version": "0.1.0",
  "source_asset_draft_hash": "sha256:...",
  "source_summary": {},
  "candidate_assets": [],
  "duplicate_candidates": [],
  "rejected_candidates": [],
  "warnings": [],
  "blocking_questions": [],
  "needs_human_review": true,
  "confidence": 0.0
}
```

### Candidate asset structure

Each `candidate_assets[]` item should include:

- `temporary_id`
- `proposed_name`
- `proposed_description`
- `proposed_reference_id`
- `proposed_asset_type`
- `proposed_asset_class`
- `criticality`
- `folder_link`
- `perimeter_scope_relevance`
- `audit_relevance`
- `risk_relevance`
- `source_text_references`
- `rationale`
- `confidence`
- `human_review_status`
- `allowed_next_actions`
- `ambiguity_flags`

Recommended example shape:

```json
{
  "temporary_id": "AST-CAND-001",
  "proposed_name": "Core Banking Application",
  "proposed_description": "Primary business application in scope for user access management review.",
  "proposed_reference_id": null,
  "proposed_asset_type": {
    "value": "PR",
    "label": "Primary"
  },
  "proposed_asset_class": {
    "asset_class_id": null,
    "asset_class_name": "Application",
    "needs_review": true
  },
  "criticality": {
    "value": "high",
    "is_platform_writable": false,
    "mapping_note": "Advisory only until mapped to verified Asset fields."
  },
  "folder_link": {
    "folder_id": "uuid",
    "folder_name": "Al-Rawasi Fintech",
    "resolution_mode": "step2_existing_or_created"
  },
  "perimeter_scope_relevance": {
    "perimeter_id": "uuid",
    "summary": "Directly in scope for user access management review.",
    "scope_strength": "direct"
  },
  "audit_relevance": {
    "compliance_assessment_id": "uuid",
    "summary": "Likely evidence and control target for ECC review."
  },
  "risk_relevance": {
    "risk_assessment_id": null,
    "summary": null
  },
  "source_text_references": [
    {
      "ref_id": "T1",
      "excerpt": "Core Banking Platform - User Access Management",
      "char_start": 0,
      "char_end": 45
    }
  ],
  "rationale": "The scenario explicitly names the core banking platform as the assessed scope, which maps cleanly to a business application asset.",
  "confidence": 0.94,
  "human_review_status": "pending_review",
  "allowed_next_actions": [
    "accept_as_asset",
    "edit_then_accept",
    "reuse_existing_asset",
    "reject",
    "defer"
  ],
  "ambiguity_flags": []
}
```

### Notes from current code inspection

- `Asset` currently supports `folder`, `name`, `description`, `ref_id`, `type`, `reference_link`, `owner`, `asset_class`, `observation`, parent and support asset relations, objective JSON fields, and several advanced fields
- `AssetWriteSerializer` excludes `business_value`, so Step 3 should not rely on it
- no direct `perimeter` field exists on `Asset`
- `ComplianceAssessment` has an `assets` M2M, but Step 3 v1 should not mutate that relation automatically

## 7. Asset Classification Rules

### Application assets

- examples: core banking application, identity provider platform, PAM system
- preferred mapping: `Asset`
- common `type`: `PR`

### Account or user assets

- examples: production user accounts, privileged admin accounts
- allowed as asset candidates when the scope is about account estates, identity populations, or entitlement surfaces
- do not default to one record per named human account
- mark ambiguity when the phrase could instead represent a control, process, or vulnerability scope

### Privileged account assets

- allowed as asset candidates
- mark with elevated ambiguity if the text really describes lack of governance rather than a managed asset

### Record or document assets

- examples: access review records, provisioning records
- often ambiguous between `Asset` and future `Evidence`
- suggest only when the scenario implies the record set itself is a governed business information asset

### Infrastructure or service assets

- examples: VPN service, remote access gateway, IAM platform, MFA service
- strong candidates when a real system or service is named
- ambiguous when the wording describes a capability gap rather than a concrete service

### Process or policy assets

- examples: PAM process, IAM procedures, access governance policies
- only suggest as assets when the organization catalogs operational processes or information sets as assets
- otherwise mark as likely evidence or control documentation

### Ambiguous candidates

If the phrase can describe more than one of the following, Step 3 must mark ambiguity:

- asset
- evidence
- control
- vulnerability

Examples:

- `Access Review Records`: asset or evidence or both
- `IAM Policy`: documentation or evidence; not necessarily asset
- `MFA`: control capability or concrete service
- `PAM`: control capability, process, or platform

### Classification rule

The AI should flag ambiguity instead of forcing a category. That is safer than over-creating assets that later need to be re-modeled.

## 8. Duplicate Detection and Reuse Design

Step 3 should detect duplicates before any create path is proposed.

### Current codebase signals

- `Asset.fields_to_check = ["name"]` in the model, which existing import logic uses as the minimal existing-record identity surface
- `AssetViewSet.batch_create()` already reuses existing assets by exact `name` plus `folder`
- `AssetAutocompleteSerializer` exposes `id`, `name`, `ref_id`, `type`, and `folder`
- the platform already supports permission-aware search and autocomplete

### Recommended duplicate checks

1. exact name match in the selected folder
2. normalized name match in the selected folder
3. exact `ref_id` match in the selected folder
4. normalized `ref_id` match when present
5. same folder plus same type
6. indirect scope relevance comparison using selected perimeter and audit context
7. optional future similarity scoring if embeddings or better fuzzy matching are added

### Folder scope rule

Duplicate detection should be folder-first. The existing platform is folder-scoped for asset creation permissions and already treats folder context as the main ownership boundary.

### Perimeter scope rule

Because `Asset` has no direct `perimeter` field, perimeter relevance must remain advisory. Duplicate detection may mention that an existing asset appears more or less relevant to the selected perimeter, but it should not treat perimeter as a hard identity key.

### Human decision outcomes

For each duplicate candidate, the reviewer must be able to choose:

- create new asset anyway
- reuse existing asset
- merge conceptually and reuse existing asset
- reject candidate
- defer

### Duplicate candidate structure

Recommended shape:

```json
{
  "temporary_id": "AST-CAND-002",
  "matches": [
    {
      "existing_asset_id": "uuid",
      "existing_name": "Remote Access VPN Service",
      "existing_ref_id": "AST-VPN-01",
      "existing_type": "SP",
      "folder_id": "uuid",
      "folder_name": "Al-Rawasi Fintech",
      "match_type": "normalized_name_same_folder",
      "match_score": 0.92,
      "scope_relevance": "high",
      "warning": "Potential duplicate within the selected folder."
    }
  ],
  "recommended_human_action": "review_reuse_before_create"
}
```

## 9. Human Review Model

The Step 3 UI and contract should support the following reviewer actions per candidate:

- accept suggested asset
- edit suggested asset
- reuse existing asset
- reject suggested asset
- mark as evidence instead
- mark as control instead
- mark as vulnerability instead
- defer decision

### UI must show

- AI rationale
- source text excerpts
- confidence score
- duplicate warnings
- ambiguity warnings
- selected folder and scope context
- whether the action is only a suggestion or a real create path

### Review status values

Recommended advisory statuses:

- `pending_review`
- `accepted_for_create`
- `accepted_for_reuse`
- `edited_pending_create`
- `rejected`
- `reclassified_to_evidence`
- `reclassified_to_control`
- `reclassified_to_vulnerability`
- `deferred`

### Human approval rule

No candidate may reach commit write mode unless:

- the overall request sets `approved_by_user=true`
- each create or reuse decision is individually human-approved

## 10. Approved Asset Commit Design

Step 3 should describe, but not implement now, a future asset commit endpoint.

### Commit behavior goals

- support `dry_run`
- require `approved_by_user=true` for write mode
- require `idempotency_key` for write mode
- require `source_asset_draft_hash`
- use one atomic transaction in write mode
- create or reuse only human-approved assets
- do not create controls, vulnerabilities, risks, evidence, or findings
- return created, reused, rejected, and deferred assets

### Recommended commit request shape

```json
{
  "draft_type": "AiAssetCommitApprovalRequest",
  "schema_version": "0.1.0",
  "source_step1_draft_hash": "sha256:...",
  "source_asset_draft_hash": "sha256:...",
  "case_setup_reference": {
    "folder_id": "uuid",
    "perimeter_id": "uuid",
    "compliance_assessment_id": "uuid",
    "risk_assessment_id": "uuid or null"
  },
  "folder_id": "uuid",
  "perimeter_id": "uuid",
  "compliance_assessment_id": "uuid",
  "risk_assessment_id": "uuid or null",
  "dry_run": true,
  "approved_by_user": false,
  "idempotency_key": null,
  "asset_decisions": []
}
```

### Recommended `asset_decisions[]` item shape

```json
{
  "temporary_id": "AST-CAND-001",
  "decision": "create",
  "selected_existing_asset_id": null,
  "proposed_fields": {
    "name": "Core Banking Application",
    "description": "Primary business application in scope for the ECC user access review.",
    "ref_id": "AST-CBK-001",
    "type": "PR",
    "asset_class_id": null,
    "observation": "Created from Step 3 reviewed AI asset draft."
  },
  "human_approved": true,
  "rationale": "Reviewer accepted the AI suggestion after checking duplicates."
}
```

### Commit response goals

- explicit `operation_type`
- clear list of `created_assets`
- clear list of `reused_assets`
- clear list of `rejected_assets`
- clear list of `deferred_assets`
- no side effects beyond assets

### Important v1 constraint

Step 3 v1 commit should create or reuse plain assets only. It should not also auto-link them to:

- `ComplianceAssessment.assets`
- `RiskScenario.assets`
- `AppliedControl.assets`
- `Vulnerability.assets`

Those relationships can be introduced later in a narrower follow-up once the asset-only path is stable.

## 11. Guardrails

Step 3 must reject or flag payloads that attempt to escape asset-only scope.

### Guardrails to reject

- final compliance decisions
- final risk decisions
- audit closure attempts
- risk acceptance attempts
- vulnerability creation disguised as assets
- control creation disguised as assets
- evidence creation disguised as assets without explicit review
- assets outside the selected folder or domain
- assets outside the selected perimeter or scope unless explicitly approved as supporting context
- unapproved database writes
- invented platform entity types

### Specific recommendations

- reject `platform_entity` values other than `Asset` in commit create paths
- reject fields that belong to `AppliedControl`, `Vulnerability`, `Evidence`, `RiskScenario`, or `RiskAcceptance`
- reject compliance result fields such as `result`, `status=closed`, `approved`, or risk treatment acceptance fields
- reject advanced `Asset` M2M fields in v1 commit, such as `applied_controls`, `vulnerabilities`, `incidents`, and `security_exceptions`
- reject out-of-folder reuse choices

### Scope guardrail

If the reviewer wants to create an asset outside the Step 2 folder or clearly outside the declared scope, Step 3 should block it unless the API explicitly adds an override pattern later.

## 12. AI Provider and Fallback Behavior

Step 3 should mirror the accepted Step 1 pattern.

### Configured AI provider

- if a provider is configured, the suggestion endpoint may ask it to generate a candidate asset draft
- provider output must still pass strict serializer validation and Step 3 guardrails before response

### No provider configured

- use deterministic fallback
- return a warning such as `provider_not_configured_fallback`
- include provider mode in `source_summary`

### Deterministic fallback behavior

Fallback should use transparent heuristics based on:

- Step 1 asset drafts if available
- selected folder and scope names
- known weaknesses
- scenario text keyword extraction
- known business-to-platform mapping rules
- basic duplicate lookup using current folder-scoped assets

Fallback should not pretend to be more certain than it is.

### Malformed AI output

Recommended default behavior:

- reject with `422`
- return `error_code: ai_provider_invalid_output`
- do not silently fall back after malformed provider output in v1

Reasoning:

- silent fallback hides provider quality issues
- Step 1 currently treats malformed provider output as an error

Optional future enhancement:

- explicit feature flag for `fallback_on_provider_error`

### Low confidence output

- keep `needs_human_review=true`
- increase `blocking_questions`
- increase ambiguity flags
- in `strict_mode=true`, require at least one blocking question when confidence is too low

### Unsafe output

- reject on guardrail failure
- do not pass through final decisions, closures, risk acceptance, or foreign entity types

### Ambiguous candidates

- keep in `candidate_assets` only if the user can still review them safely
- otherwise place in `rejected_candidates` with `recommended_reclassification`

## 13. Validation Rules

### Suggestion endpoint validation

- `folder_id` required
- `perimeter_id` required
- `compliance_assessment_id` required
- `source_step1_draft_hash` required
- `scenario_text` or `scope_summary` required
- strict rejection of unknown fields
- referenced objects must exist and be visible to the caller
- `selected_framework_id` optional
- `risk_assessment_id` optional
- no write in suggestion endpoint

### Commit endpoint validation

- strict rejection of unknown fields
- `folder_id` required
- `perimeter_id` required
- `compliance_assessment_id` required
- `source_step1_draft_hash` required
- `source_asset_draft_hash` required
- `approved_by_user` required for write mode
- `idempotency_key` required for write mode
- `asset_decisions` required
- only allowed asset fields accepted in `proposed_fields`
- forbidden foreign fields rejected
- write mode must reject any decision item where `human_approved=false`

### Allowed `proposed_fields` in v1 commit

Recommended allow-list:

- `name`
- `description`
- `ref_id`
- `type`
- `asset_class_id`
- `observation`

### Explicitly forbidden in v1 commit

- `applied_controls`
- `vulnerabilities`
- `incidents`
- `security_exceptions`
- `security_objectives`
- `disaster_recovery_objectives`
- `security_capabilities`
- `recovery_capabilities`
- audit result fields
- risk treatment fields

## 14. Transaction and Rollback Strategy

The future commit endpoint should use one database transaction in write mode.

### Atomic write behavior

- wrap write mode in `transaction.atomic()`
- if any approved create or reuse validation fails mid-flight, roll back the entire write

### Partial failure handling

- dry-run may report item-level issues without writing
- write mode must not partially create some assets and then stop

### Duplicate detected after dry-run

- if an asset becomes a duplicate between dry-run and write mode, return a blocking conflict response
- require the user to rerun dry-run or explicitly choose reuse

### Permission failure

- fail before creating any asset
- return `403` with folder permission details

### Invalid asset category or type

- fail validation before entering write mode
- if the asset class ID no longer exists or is not visible, block the request

### Out-of-scope asset

- block if the asset is clearly outside the selected folder or declared scope
- optionally allow `deferred` in dry-run mode if the reviewer wants to postpone the item

### Optional deferred assets

- allow decisions marked `defer`
- return them in `deferred_assets`
- do not write them

### Idempotency limitations

Recommended v1 behavior:

- require `idempotency_key` in write mode
- combine that key with duplicate detection and request hash checks for traceability
- if receipts are not persisted yet, return a warning similar to Step 2 that idempotency is trace-only rather than durable receipt replay

## 15. Frontend UX Design

The future Step 3 review screen should start from an accepted Step 2 case setup.

### UX goals

- show candidate assets grouped by type or category
- show duplicate matches inline
- show confidence and rationale per candidate
- allow accept, edit, reuse, reject, reclassify, or defer
- show a dry-run summary before any creation
- show final created and reused assets after commit
- clearly separate assets from controls, vulnerabilities, evidence, and risks

### Recommended layout

- case context summary header
- selected folder, perimeter, audit, framework, and optional risk assessment summary
- candidate asset list grouped by category
- duplicate review drawer or side panel
- ambiguity or reclassification banner
- dry-run results panel
- final commit result summary

### UX safety expectations

- never label a suggestion as already created
- clearly mark provider mode or fallback mode
- clearly show that perimeter relevance is contextual, not a direct Asset field
- clearly show when criticality is advisory only

## 16. API Payload Examples

### A. Asset suggestion request

```json
{
  "source_step1_draft_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
  "case_setup_reference": {
    "source": "step2_case_setup",
    "step2_schema_version": "0.1.0",
    "folder_id": "8a6f2bdb-fb7d-412d-9fb6-c99409a19909",
    "perimeter_id": "1da46d44-1f0d-4b52-81ef-1991ae0866b2",
    "compliance_assessment_id": "2ab9d352-b443-4592-9e8b-87a85df2fa4d",
    "risk_assessment_id": "a26b14b5-716a-45cc-a99e-febee2fca63c",
    "framework_id": "02d48ef4-00de-4134-b954-5a1ada2a9833"
  },
  "folder_id": "8a6f2bdb-fb7d-412d-9fb6-c99409a19909",
  "perimeter_id": "1da46d44-1f0d-4b52-81ef-1991ae0866b2",
  "compliance_assessment_id": "2ab9d352-b443-4592-9e8b-87a85df2fa4d",
  "risk_assessment_id": "a26b14b5-716a-45cc-a99e-febee2fca63c",
  "scenario_text": "Al-Rawasi Fintech is preparing for an annual NCA ECC-1:2018 compliance assessment in Q4 2026. The scope is Core Banking Platform - User Access Management. Known weaknesses include no MFA for remote access, no PAM for privileged admin accounts, no periodic access review records, and no formal documented access review.",
  "scope_summary": "Core Banking Platform user access management scope for the Q4 2026 ECC review.",
  "known_weaknesses": [
    "no MFA for remote access",
    "no PAM for privileged admin accounts",
    "no periodic access review records",
    "access review has never been formally reviewed or documented"
  ],
  "selected_framework_id": "02d48ef4-00de-4134-b954-5a1ada2a9833",
  "user_locale": "en",
  "strict_mode": true
}
```

### B. Asset suggestion response

```json
{
  "draft_type": "AiAssetSuggestionDraft",
  "schema_version": "0.1.0",
  "source_asset_draft_hash": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
  "source_summary": {
    "provider_mode": "provider_not_configured_fallback",
    "strict_mode_applied": true,
    "scenario_excerpt": "Al-Rawasi Fintech is preparing for an annual NCA ECC-1:2018 compliance assessment...",
    "folder_id": "8a6f2bdb-fb7d-412d-9fb6-c99409a19909",
    "perimeter_id": "1da46d44-1f0d-4b52-81ef-1991ae0866b2",
    "compliance_assessment_id": "2ab9d352-b443-4592-9e8b-87a85df2fa4d",
    "risk_assessment_id": "a26b14b5-716a-45cc-a99e-febee2fca63c"
  },
  "candidate_assets": [
    {
      "temporary_id": "AST-CAND-001",
      "proposed_name": "Core Banking Application",
      "proposed_description": "Primary business application in scope for user access management review.",
      "proposed_reference_id": null,
      "proposed_asset_type": { "value": "PR", "label": "Primary" },
      "proposed_asset_class": { "asset_class_id": null, "asset_class_name": "Application", "needs_review": true },
      "criticality": { "value": "high", "is_platform_writable": false, "mapping_note": "Advisory only." },
      "folder_link": { "folder_id": "8a6f2bdb-fb7d-412d-9fb6-c99409a19909", "folder_name": "Al-Rawasi Fintech", "resolution_mode": "step2_existing_or_created" },
      "perimeter_scope_relevance": { "perimeter_id": "1da46d44-1f0d-4b52-81ef-1991ae0866b2", "summary": "Directly in scope.", "scope_strength": "direct" },
      "audit_relevance": { "compliance_assessment_id": "2ab9d352-b443-4592-9e8b-87a85df2fa4d", "summary": "Likely target of ECC user access review evidence and control mapping." },
      "risk_relevance": { "risk_assessment_id": "a26b14b5-716a-45cc-a99e-febee2fca63c", "summary": "Supports IAM risk context." },
      "source_text_references": [
        { "ref_id": "T1", "excerpt": "Core Banking Platform - User Access Management", "char_start": 95, "char_end": 140 }
      ],
      "rationale": "The named platform is the primary system under review and maps directly to an application asset.",
      "confidence": 0.94,
      "human_review_status": "pending_review",
      "allowed_next_actions": ["accept_as_asset", "edit_then_accept", "reuse_existing_asset", "reject", "defer"],
      "ambiguity_flags": []
    }
  ],
  "duplicate_candidates": [],
  "rejected_candidates": [
    {
      "source_label": "IAM Policies and Procedures",
      "recommended_reclassification": "control_or_evidence",
      "reason": "The phrase describes documentation more naturally than a standalone asset.",
      "confidence": 0.78
    }
  ],
  "warnings": [
    {
      "code": "provider_not_configured_fallback",
      "message": "No AI provider is configured; a deterministic fallback parser generated the candidate asset draft.",
      "needs_review": true
    }
  ],
  "blocking_questions": [],
  "needs_human_review": true,
  "confidence": 0.84
}
```

### C. Duplicate asset candidate response

```json
{
  "temporary_id": "AST-CAND-003",
  "matches": [
    {
      "existing_asset_id": "cb6fc622-f2b0-4f3a-b8a3-e5fe8dbdd0ae",
      "existing_name": "Identity Provider",
      "existing_ref_id": "IAM-IDP-001",
      "existing_type": "SP",
      "folder_id": "8a6f2bdb-fb7d-412d-9fb6-c99409a19909",
      "folder_name": "Al-Rawasi Fintech",
      "match_type": "exact_name_same_folder",
      "match_score": 0.99,
      "scope_relevance": "high",
      "warning": "Existing folder-scoped asset already appears to represent this system."
    }
  ],
  "recommended_human_action": "reuse_existing_asset"
}
```

### D. Ambiguous candidate response

```json
{
  "temporary_id": "AST-CAND-006",
  "proposed_name": "Access Review Records",
  "human_review_status": "pending_review",
  "ambiguity_flags": [
    {
      "code": "asset_or_evidence",
      "message": "This candidate may be a governed information asset or future evidence rather than a new asset record."
    }
  ],
  "allowed_next_actions": [
    "accept_as_asset",
    "mark_as_evidence",
    "reject",
    "defer"
  ]
}
```

### E. Approved asset commit dry-run request

```json
{
  "draft_type": "AiAssetCommitApprovalRequest",
  "schema_version": "0.1.0",
  "source_step1_draft_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
  "source_asset_draft_hash": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
  "case_setup_reference": {
    "folder_id": "8a6f2bdb-fb7d-412d-9fb6-c99409a19909",
    "perimeter_id": "1da46d44-1f0d-4b52-81ef-1991ae0866b2",
    "compliance_assessment_id": "2ab9d352-b443-4592-9e8b-87a85df2fa4d",
    "risk_assessment_id": "a26b14b5-716a-45cc-a99e-febee2fca63c"
  },
  "folder_id": "8a6f2bdb-fb7d-412d-9fb6-c99409a19909",
  "perimeter_id": "1da46d44-1f0d-4b52-81ef-1991ae0866b2",
  "compliance_assessment_id": "2ab9d352-b443-4592-9e8b-87a85df2fa4d",
  "risk_assessment_id": "a26b14b5-716a-45cc-a99e-febee2fca63c",
  "dry_run": true,
  "approved_by_user": false,
  "idempotency_key": null,
  "asset_decisions": [
    {
      "temporary_id": "AST-CAND-001",
      "decision": "create",
      "selected_existing_asset_id": null,
      "proposed_fields": {
        "name": "Core Banking Application",
        "description": "Primary business application in scope for the ECC user access review.",
        "ref_id": "AST-CBK-001",
        "type": "PR",
        "asset_class_id": null,
        "observation": "Prepared from reviewed Step 3 draft."
      },
      "human_approved": false,
      "rationale": "Dry-run only."
    }
  ]
}
```

### F. Approved asset commit dry-run response

```json
{
  "operation_type": "dry_run",
  "status": "validated",
  "planned_actions": [
    {
      "temporary_id": "AST-CAND-001",
      "platform_entity": "Asset",
      "action": "create",
      "status": "ok",
      "detail": "Asset 'Core Banking Application' would be created in folder 'Al-Rawasi Fintech'."
    }
  ],
  "created_assets": [],
  "reused_assets": [],
  "rejected_assets": [],
  "deferred_assets": [],
  "duplicate_conflicts": [],
  "warnings": [],
  "blocking_errors": []
}
```

### G. Approved asset commit write request

```json
{
  "draft_type": "AiAssetCommitApprovalRequest",
  "schema_version": "0.1.0",
  "source_step1_draft_hash": "sha256:1111111111111111111111111111111111111111111111111111111111111111",
  "source_asset_draft_hash": "sha256:2222222222222222222222222222222222222222222222222222222222222222",
  "case_setup_reference": {
    "folder_id": "8a6f2bdb-fb7d-412d-9fb6-c99409a19909",
    "perimeter_id": "1da46d44-1f0d-4b52-81ef-1991ae0866b2",
    "compliance_assessment_id": "2ab9d352-b443-4592-9e8b-87a85df2fa4d",
    "risk_assessment_id": "a26b14b5-716a-45cc-a99e-febee2fca63c"
  },
  "folder_id": "8a6f2bdb-fb7d-412d-9fb6-c99409a19909",
  "perimeter_id": "1da46d44-1f0d-4b52-81ef-1991ae0866b2",
  "compliance_assessment_id": "2ab9d352-b443-4592-9e8b-87a85df2fa4d",
  "risk_assessment_id": "a26b14b5-716a-45cc-a99e-febee2fca63c",
  "dry_run": false,
  "approved_by_user": true,
  "idempotency_key": "step3-asset-commit-20260711-0001",
  "asset_decisions": [
    {
      "temporary_id": "AST-CAND-001",
      "decision": "create",
      "selected_existing_asset_id": null,
      "proposed_fields": {
        "name": "Core Banking Application",
        "description": "Primary business application in scope for the ECC user access review.",
        "ref_id": "AST-CBK-001",
        "type": "PR",
        "asset_class_id": null,
        "observation": "Created from reviewed Step 3 AI asset draft."
      },
      "human_approved": true,
      "rationale": "Reviewer approved create after dry-run."
    },
    {
      "temporary_id": "AST-CAND-003",
      "decision": "reuse",
      "selected_existing_asset_id": "cb6fc622-f2b0-4f3a-b8a3-e5fe8dbdd0ae",
      "proposed_fields": null,
      "human_approved": true,
      "rationale": "Existing identity provider asset already matches the scope."
    },
    {
      "temporary_id": "AST-CAND-006",
      "decision": "defer",
      "selected_existing_asset_id": null,
      "proposed_fields": null,
      "human_approved": true,
      "rationale": "The team needs to decide whether access review records should be treated as assets or evidence."
    }
  ]
}
```

### H. Approved asset commit success response

```json
{
  "operation_type": "commit",
  "status": "created_and_reused",
  "created_assets": [
    {
      "temporary_id": "AST-CAND-001",
      "platform_entity": "Asset",
      "id": "f9dfe5ab-7f7d-485d-a863-d149888bcd3f",
      "name": "Core Banking Application",
      "ref_id": "AST-CBK-001"
    }
  ],
  "reused_assets": [
    {
      "temporary_id": "AST-CAND-003",
      "platform_entity": "Asset",
      "id": "cb6fc622-f2b0-4f3a-b8a3-e5fe8dbdd0ae",
      "name": "Identity Provider",
      "ref_id": "IAM-IDP-001"
    }
  ],
  "rejected_assets": [],
  "deferred_assets": [
    {
      "temporary_id": "AST-CAND-006",
      "reason": "Deferred by reviewer pending asset versus evidence decision."
    }
  ],
  "duplicate_conflicts": [],
  "warnings": [
    {
      "code": "idempotency_trace_only",
      "detail": "The Step 3 implementation requires idempotency_key for traceability but does not yet persist replay receipts."
    }
  ],
  "blocking_errors": []
}
```

### I. Forbidden control or vulnerability or evidence payload response

```json
{
  "error_code": "ai_asset_commit_guardrails_failed",
  "detail": "The approved Step 3 payload contains out-of-scope or non-asset fields.",
  "blocking_errors": [
    {
      "code": "foreign_entity_forbidden",
      "field": "asset_decisions[0].proposed_fields.applied_controls",
      "detail": "AppliedControl links must not be created in Step 3 asset commit."
    },
    {
      "code": "reclassification_required",
      "field": "asset_decisions[1].decision",
      "detail": "This candidate was classified as likely evidence and cannot be committed as an asset without explicit reviewer override rules."
    }
  ],
  "warnings": []
}
```

### J. Permission denied response

```json
{
  "folder": "You do not have permission to add objects in this folder"
}
```

## 17. Test Plan for Future Step 3 Implementation

Future Step 3 implementation should cover at least the following tests:

- auth required for suggestion endpoint
- auth required for commit endpoint
- suggestion endpoint creates no records
- fallback suggestion works with no provider configured
- malformed provider output rejected with `422`
- unknown fields rejected on suggestion request
- unknown fields rejected on commit request
- candidate assets returned with confidence and rationale
- duplicate assets detected in folder scope
- ambiguous candidates flagged
- controls not created as assets
- vulnerabilities not created as assets
- evidence not created as assets without review
- commit dry-run creates no records
- commit write requires `approved_by_user=true`
- commit write requires `idempotency_key`
- commit write requires `source_asset_draft_hash`
- commit write creates only assets
- commit write does not create controls, vulnerabilities, risks, evidence, findings, or risk acceptances
- transaction rollback when one approved asset fails validation
- permission denied when caller lacks `add_asset` on folder
- selected existing asset must be visible to the caller
- Step 1 regression tests still pass unchanged
- Step 2 regression tests still pass unchanged

## 18. Files Expected to Change During Step 3 Implementation

Likely backend files:

- `backend/ai_onboarding/asset_suggestion_serializers.py`
- `backend/ai_onboarding/asset_suggestion_provider.py`
- `backend/ai_onboarding/asset_suggestion_guardrails.py`
- `backend/ai_onboarding/asset_suggestion_service.py`
- `backend/ai_onboarding/views.py`
- `backend/ai_onboarding/urls.py`
- `backend/app_tests/api/test_api_ai_asset_suggestion.py`
- `backend/app_tests/api/test_api_ai_asset_commit.py`

Possible optional frontend files later:

- future Step 3 review screen files under the existing app routes
- shared asset review components if the UX is not embedded into the existing onboarding flow

Files that should not need Step 3 contract changes:

- Step 1 request and response contract files
- Step 2 request and response contract files

## 19. Open Questions / Needs Verification

- exact required `Asset` fields in live create flows beyond `folder`, `name`, and `type`
- whether `asset_class` is required or optional in real customer usage patterns
- whether records and documents such as access review records should usually be modeled as assets or evidence
- whether user account populations should be modeled as assets in the product guidance
- whether Step 3 should ever write `ComplianceAssessment.assets` in v1 or keep that out of scope
- whether Step 3 should ever support parent or support asset graph creation in v1
- whether the frontend `is_critical` display field is derived or otherwise writable through a verified backend path
- whether `AssetClass` taxonomy is sufficiently stable for AI-assisted mapping
- duplicate detection limitations when no `ref_id` exists
- whether the existing `/api/assets/batch-create` semantics should inspire an internal helper, without exposing its public contract as Step 3
- whether bulk asset creation utilities already exist outside `batch-create` and `data_wizard`
- whether Step 3 should persist AI drafts in a later phase
- whether `WorkflowCase` should eventually store Step 3 provenance, while remaining optional now

## 20. Step 3 Design Acceptance Criteria

Step 3 is ready for implementation planning only if all of the following remain true:

- Step 1 and Step 2 contracts remain unchanged
- Step 3 is split into advisory suggestion and approved commit responsibilities
- suggestion mode is guaranteed no-write
- commit mode supports `dry_run`
- commit write mode requires human approval and idempotency key
- commit write mode creates or reuses only `Asset`
- no controls, vulnerabilities, evidence, findings, risk acceptances, or closure decisions are created by Step 3
- duplicate detection is folder-scoped and human-reviewed
- ambiguous candidates are flagged rather than forced into asset creation
- provider and deterministic fallback behavior are explicit and transparent
- strict serializer validation and guardrails are defined before implementation starts
- transaction and rollback behavior are defined for the future commit path
- WorkflowCase remains optional
- the known requirements versus requirement-nodes mismatch remains an acknowledged general platform constraint but Step 3 does not depend on it
- the design remains precise enough that backend implementation can begin without reopening Step 1 or Step 2 semantics
