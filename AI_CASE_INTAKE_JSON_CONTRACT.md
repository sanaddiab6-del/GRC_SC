# AI Case Intake JSON Contract

## 1. Executive Summary

Step 0.2 defines the structured JSON contract for the first AI feature: `AI Case Intake / Scenario Parser`.

This feature will accept a natural-language GRC scenario and return a validated draft that uses the canonical internal vocabulary defined in `AI_CANONICAL_WORKFLOW_DICTIONARY.md`. Its purpose is to turn ambiguous business-language intake text into a reviewable, implementation-ready draft that later workflow steps can confirm, edit, reject, or use as input for controlled object creation.

This feature will do the following:

- parse a natural-language GRC scenario
- normalize business terms into canonical Sanadcom platform entities
- suggest a likely framework resolution path
- propose draft `Folder`, `Perimeter`, `ComplianceAssessment`, `Asset`, `AppliedControl`, `Vulnerability`, `RiskAssessment`, `RiskScenario`, `RequirementNode` focus areas, and evidence expectations
- return confidence, rationale, and source-text traceability for every suggested object
- produce human-review questions and warnings before any future creation step

This feature will **not** do the following:

- it will not write to the database
- it will not create `Folder`, `Perimeter`, `ComplianceAssessment`, `RequirementAssessment`, `Asset`, `AppliedControl`, `Vulnerability`, `RiskAssessment`, `RiskScenario`, `Evidence`, `FindingsAssessment`, `Finding`, `RiskAcceptance`, or `ValidationFlow` records
- it will not load libraries
- it will not create audits or requirements
- it will not generate final compliance decisions
- it will not perform final risk acceptance
- it will not close audits, findings, or workflow objects

This step produces **draft JSON only**. It is an advisory, review-first contract and must remain side-effect free.

Canonical source-of-truth anchors used by this contract:

- `AI_CANONICAL_WORKFLOW_DICTIONARY.md`
- `backend/iam/models.py` for `Folder`
- `backend/core/models.py` for `ComplianceAssessment`, `RequirementNode`, `RequirementAssessment`, `Asset`, `AppliedControl`, `Evidence`, `EvidenceRevision`, `RiskAssessment`, `RiskScenario`, `Vulnerability`, `Threat`, `FindingsAssessment`, `Finding`, `RiskAcceptance`, and `ValidationFlow`
- `backend/library/views.py` and `backend/library/serializers.py` for `StoredLibrary` and `LoadedLibrary`
- `backend/core/views.py` for `FolderViewSet.ai_recommendations()` and `QuickStartView`
- `backend/core/serializers.py` for `QuickStartSerializer`
- `frontend/src/lib/utils/crud.ts`, `frontend/src/lib/utils/schemas.ts`, and `frontend/src/lib/utils/types.ts` for frontend naming and CRUD keys

## 2. Input Contract

The future AI case intake endpoint should accept a JSON object with the following fields.

| Field | Type | Required | Description | Example value | Validation rule |
| --- | --- | --- | --- | --- | --- |
| `scenario_text` | `string` | Yes | Natural-language GRC case description to parse. This is the primary source text. | `"Al-Rawasi Fintech is preparing for an ECC-1:2018 readiness review for its payment platform before Saudi launch..."` | Must be a non-empty UTF-8 string after trim. Minimum 50 chars recommended. Maximum 20,000 chars recommended for Step 1. |
| `preferred_framework` | `string \| null` | No | User-supplied framework hint in business language. Used as a preference, not a final resolved ID. | `"ECC-1:2018"` | Trimmed string up to 255 chars. Must not be treated as a final `Framework.id` or `StoredLibrary.urn` without lookup. |
| `assessment_period` | `object \| null` | No | Optional structured assessment period hint. | `{ "label": "Q4 2026 readiness review", "start_date": "2026-10-01", "end_date": "2026-12-15" }` | If provided, must be an object with optional `label`, `start_date`, and `end_date`. Dates must be ISO `YYYY-MM-DD`. If both dates are present, `start_date <= end_date`. |
| `organization_hint` | `string \| null` | No | Optional organization name or shorthand to help naming and matching. | `"Al-Rawasi Fintech"` | Trimmed string up to 255 chars. Must not be assumed to match an existing `Folder` without lookup. |
| `scope_hint` | `string \| null` | No | Optional human-entered scope note that narrows the case. | `"Core payment platform, IAM, cloud operations, and supporting evidence for KSA launch"` | Trimmed string up to 2,000 chars. Treated as supplementary context only. |
| `known_deadline` | `string \| null` | No | Optional deadline known at intake time. | `"2026-12-15"` | Must be ISO date `YYYY-MM-DD` if provided. No timezone allowed. |
| `known_trigger` | `string \| null` | No | Optional trigger event or business reason. | `"pre-regulatory-readiness review"` | Trimmed string up to 255 chars. May later normalize to a suggested trigger category, but input remains free text. |
| `user_locale` | `string` | No | Locale for parsing and frontend display expectations. | `"en"` | Default `en`. Recommended pattern `^[a-z]{2}(-[A-Z]{2})?$`. Unsupported locales should fall back to `en`. |
| `strict_mode` | `boolean` | No | When true, the parser should avoid silent inference and instead emit blocking questions or `needs_review=true` more aggressively. | `true` | Default `false`. If `true`, low-confidence suggestions must either become blocking questions or remain explicitly review-gated. |

Recommended future request shape:

```json
{
  "scenario_text": "string",
  "preferred_framework": "string or null",
  "assessment_period": {
    "label": "string optional",
    "start_date": "YYYY-MM-DD optional",
    "end_date": "YYYY-MM-DD optional"
  },
  "organization_hint": "string or null",
  "scope_hint": "string or null",
  "known_deadline": "YYYY-MM-DD or null",
  "known_trigger": "string or null",
  "user_locale": "en",
  "strict_mode": true
}
```

## 3. Output Contract Overview

The AI must return one top-level draft object. It is a **draft-only** object and must not claim that any database records were created.

Recommended top-level fixed shape:

```json
{
  "draft_type": "AiCaseIntakeDraft",
  "schema_version": "0.2.0",
  "source_summary": {},
  "overall_confidence": 0.0,
  "needs_human_review": true,
  "blocking_questions": [],
  "warnings": [],
  "canonical_mappings_used": [],
  "case_context": {},
  "framework_resolution": {},
  "case_setup_draft": {},
  "asset_drafts": [],
  "applied_control_drafts": [],
  "vulnerability_drafts": [],
  "risk_assessment_draft": null,
  "risk_scenario_drafts": [],
  "requirement_focus_drafts": [],
  "evidence_expectation_drafts": [],
  "human_review_checklist": [],
  "next_system_actions": []
}
```

| Top-level field | Type | Required | Description |
| --- | --- | --- | --- |
| `draft_type` | `string` | Yes | Fixed value: `AiCaseIntakeDraft`. |
| `schema_version` | `string` | Yes | Contract version. Recommended initial value: `0.2.0`. |
| `source_summary` | `object` | Yes | Metadata about the input scenario and parser behavior. |
| `overall_confidence` | `number` | Yes | Overall parser confidence in range `0.0..1.0`. |
| `needs_human_review` | `boolean` | Yes | Must always be `true` for Step 1. The output is never self-executing. |
| `blocking_questions` | `array` | Yes | Questions that must be answered before future create flows are allowed. |
| `warnings` | `array` | Yes | Non-blocking warnings, ambiguities, or unsupported assumptions. |
| `canonical_mappings_used` | `array` | Yes | Record of business-term to platform-entity mappings actually used by the parser. |
| `case_context` | `AiCaseContextDraft` | Yes | Normalized business context extracted from the scenario. |
| `framework_resolution` | `AiFrameworkResolutionDraft` | Yes | Framework resolution and lookup plan. |
| `case_setup_draft` | `AiCaseSetupDraft` | Yes | Suggested draft setup for folder, perimeter, audit, and optional risk assessment. |
| `asset_drafts` | `AiAssetDraft[]` | Yes | Proposed asset drafts. Can be empty. |
| `applied_control_drafts` | `AiAppliedControlDraft[]` | Yes | Proposed applied-control drafts. Can be empty. |
| `vulnerability_drafts` | `AiVulnerabilityDraft[]` | Yes | Proposed vulnerability drafts. Can be empty. |
| `risk_assessment_draft` | `AiRiskAssessmentDraft \| null` | Yes | Draft risk-assessment proposal if a risk workflow is inferred. |
| `risk_scenario_drafts` | `AiRiskScenarioDraft[]` | Yes | Proposed risk-scenario drafts. Can be empty. |
| `requirement_focus_drafts` | `AiRequirementFocusDraft[]` | Yes | Requirement nodes or requirement areas that deserve focus after audit creation. |
| `evidence_expectation_drafts` | `AiEvidenceExpectationDraft[]` | Yes | Expected evidence items inferred from the scenario. |
| `human_review_checklist` | `array` | Yes | Explicit checklist the reviewer must approve before any future create step. |
| `next_system_actions` | `array` | Yes | Safe, side-effect-free next steps the system may perform after review, such as lookups or draft rendering. |

Recommended supporting top-level helper objects:

- `source_summary`
  - `detected_language: string`
  - `input_char_count: integer`
  - `strict_mode_applied: boolean`
  - `scenario_excerpt: string`
  - `parser_notes: string[]`

- `blocking_questions[]`
  - `question_id: string`
  - `question_text: string`
  - `reason: string`
  - `affected_fields: string[]`
  - `severity: "blocking"`

- `warnings[]`
  - `code: string`
  - `message: string`
  - `affected_fields: string[]`
  - `needs_review: boolean`

- `canonical_mappings_used[]`
  - `business_term: string`
  - `platform_entity: string`
  - `api_endpoint: string`
  - `note: string`

- `human_review_checklist[]`
  - `check_id: string`
  - `label: string`
  - `required: boolean`
  - `related_sections: string[]`

- `next_system_actions[]`
  - `action_code: string`
  - `description: string`
  - `requires_human_confirmation: boolean`
  - `may_write_database: boolean`

## 4. Field-Level Schema Design

### Common Conventions

The following shared conventions should apply across all draft objects.

| Field / concept | Type | Rule |
| --- | --- | --- |
| `platform_entity` | `string` | Must be one of the canonical internal entity names from `AI_CANONICAL_WORKFLOW_DICTIONARY.md`. |
| `confidence` | `number` | Range `0.0..1.0`, inclusive. Recommended precision: 2 decimals. |
| `needs_review` | `boolean` | Must be `true` when confidence is below threshold, when a lookup has not been performed, or when a business-to-platform mapping remains ambiguous. |
| `rationale` | `string` | Human-readable explanation for the suggestion. Required for every draft object. |
| `source_text_refs` | `AiSourceTextRef[]` | Required for every object inferred from user text. |
| `suggested_action` | `string` | Allowed values: `lookup_existing`, `propose_create`, `propose_reuse`, `propose_update_after_create`, `defer_until_human_review`, `no_action`. |

Recommended supporting schema:

```json
{
  "AiSourceTextRef": {
    "ref_id": "T1",
    "excerpt": "payment platform handling card processing and customer onboarding",
    "char_start": 118,
    "char_end": 182
  }
}
```

### A. `AiCaseContextDraft`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `organization_name` | `string \| null` | Yes | Human-readable organization name inferred from text or hint. |
| `industry` | `string \| null` | Yes | Business industry label, not a controlled platform enum. |
| `geography` | `string[]` | Yes | One or more geography hints. Use array to support multi-country scope. |
| `regulatory_context` | `string[]` | Yes | Free-text or canonical regulatory phrases inferred from input. |
| `assessment_period` | `object \| null` | Yes | Echo normalized assessment-period object if known. |
| `deadline` | `string \| null` | Yes | ISO date if known. |
| `trigger` | `string \| null` | Yes | Business trigger or intake reason. |
| `business_objective` | `string \| null` | Yes | High-level goal for the case. |
| `source_text_refs` | `AiSourceTextRef[]` | Yes | Must cite the scenario text that supports the context. |
| `confidence` | `number` | Yes | `0.0..1.0`. |
| `needs_review` | `boolean` | Yes | `true` if any core context field is uncertain. |

### B. `AiFrameworkResolutionDraft`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `requested_framework_name` | `string \| null` | Yes | User-entered framework text or parser-detected framework phrase. |
| `canonical_framework_name` | `string \| null` | Yes | Best canonical business label for the framework after normalization. |
| `stored_library_lookup_required` | `boolean` | Yes | Must be `true` when the parser has not resolved a stored-library object. |
| `loaded_library_lookup_required` | `boolean` | Yes | Must be `true` when the parser has not verified a corresponding loaded library. |
| `framework_lookup_required` | `boolean` | Yes | Must be `true` when no `Framework.id` has been verified. |
| `candidate_frameworks` | `array` | Yes | Candidate objects with `candidate_label`, `stored_library_urn`, `loaded_library_urn_or_id`, `framework_id`, `match_confidence`, `needs_review`, and `rationale`. |
| `selected_framework_id` | `string \| null` | Yes | Only populate after an actual lookup. Otherwise `null`. |
| `needs_review` | `boolean` | Yes | Must remain `true` until the framework path is confirmed. |
| `rationale` | `string` | Yes | Why the framework candidates were suggested. |

### C. `AiCaseSetupDraft`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `folder_domain_draft` | `AiFolderDomainDraft` | Yes | Canonical domain draft using `Folder`. |
| `perimeter_draft` | `AiPerimeterDraft` | Yes | Canonical perimeter draft. |
| `compliance_assessment_draft` | `AiComplianceAssessmentDraft` | Yes | Canonical audit draft using `ComplianceAssessment`. |
| `optional_risk_assessment_draft` | `AiRiskAssessmentDraft \| null` | Yes | Inline reference copy of the top-level risk assessment draft if risk work is inferred. |
| `creation_order` | `string[]` | Yes | Canonical entity or phase names in the approved setup sequence. |
| `dependency_notes` | `string[]` | Yes | Notes such as requirement auto-generation and framework lookups. |
| `needs_review` | `boolean` | Yes | Must be `true` because Step 1 is advisory-only. |

### D. `AiFolderDomainDraft`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `platform_entity` | `string` | Yes | Fixed value: `Folder`. |
| `display_label` | `string` | Yes | Business-facing label, usually `Domain`. |
| `name` | `string \| null` | Yes | Suggested folder/domain name. |
| `description` | `string \| null` | Yes | Suggested folder description. |
| `content_type` | `string` | Yes | For a business domain draft this should be `DO`. |
| `existing_record_lookup_required` | `boolean` | Yes | Must be `true` unless a prior lookup already proved reuse. |
| `suggested_action` | `string` | Yes | Usually `lookup_existing` or `propose_create`. |
| `confidence` | `number` | Yes | `0.0..1.0`. |
| `rationale` | `string` | Yes | Why this folder name/scope was suggested. |
| `source_text_refs` | `AiSourceTextRef[]` | Yes | Traceability to source text. |
| `needs_review` | `boolean` | Yes | Must be `true` if folder reuse vs create is unresolved. |

### E. `AiPerimeterDraft`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `platform_entity` | `string` | Yes | Fixed value: `Perimeter`. |
| `name` | `string \| null` | Yes | Suggested perimeter name. |
| `reference_id` | `string \| null` | Yes | Optional AI-suggested perimeter ref ID. Must remain a draft only. |
| `description` | `string \| null` | Yes | Suggested perimeter description. |
| `folder_dependency` | `string` | Yes | Reference to the folder-domain draft key or local draft alias. |
| `lifecycle_status_if_known` | `string \| null` | Yes | If inferred, use `Perimeter.lc_status` values such as `in_design`, `in_dev`, `in_prod`, `eol`, `dropped`, or `undefined`. |
| `suggested_action` | `string` | Yes | Usually `propose_create` after folder confirmation. |
| `confidence` | `number` | Yes | `0.0..1.0`. |
| `rationale` | `string` | Yes | Why this perimeter scope/name was suggested. |
| `source_text_refs` | `AiSourceTextRef[]` | Yes | Traceability to source text. |
| `needs_review` | `boolean` | Yes | Must be `true` until the perimeter name and scope are approved. |

### F. `AiComplianceAssessmentDraft`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `platform_entity` | `string` | Yes | Fixed value: `ComplianceAssessment`. |
| `name` | `string \| null` | Yes | Suggested audit name. |
| `reference_id` | `string \| null` | Yes | Optional draft ref ID suggestion. |
| `folder_dependency` | `string` | Yes | Draft key or alias for the target folder. |
| `perimeter_dependency` | `string` | Yes | Draft key or alias for the target perimeter. |
| `framework_dependency` | `string` | Yes | Reference to the chosen framework-resolution candidate or final framework ID. |
| `assessment_period` | `object \| null` | Yes | Echo normalized assessment period if known. |
| `status` | `string \| null` | Yes | Recommended initial status. Use platform values such as `planned` unless the reviewer overrides. |
| `auto_requirement_assessment_expected` | `boolean` | Yes | Must typically be `true` because compliance assessment creation auto-generates requirement assessments. |
| `suggested_action` | `string` | Yes | Usually `propose_create` after framework/folder/perimeter confirmation. |
| `confidence` | `number` | Yes | `0.0..1.0`. |
| `rationale` | `string` | Yes | Why this audit draft was proposed. |
| `source_text_refs` | `AiSourceTextRef[]` | Yes | Traceability to source text. |
| `needs_review` | `boolean` | Yes | Must be `true` until naming and framework selection are approved. |

### G. `AiAssetDraft`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `platform_entity` | `string` | Yes | Fixed value: `Asset`. |
| `proposed_ref_id` | `string \| null` | Yes | Optional draft ref ID suggestion. |
| `name` | `string \| null` | Yes | Suggested asset name. |
| `asset_type` | `string \| null` | Yes | Suggested value aligned to asset type semantics, such as `PR` or `SP`, if known. |
| `folder_dependency` | `string` | Yes | Draft key or alias for the target folder. |
| `perimeter_relevance` | `string \| null` | Yes | Human-readable explanation of why the asset belongs in scope. |
| `business_role` | `string \| null` | Yes | What business role this asset plays. |
| `criticality_if_inferred` | `string \| null` | Yes | Free-text or normalized criticality statement. |
| `suggested_action` | `string` | Yes | Usually `propose_create` or `defer_until_human_review`. |
| `confidence` | `number` | Yes | `0.0..1.0`. |
| `rationale` | `string` | Yes | Why the asset was inferred. |
| `source_text_refs` | `AiSourceTextRef[]` | Yes | Traceability to source text. |
| `needs_review` | `boolean` | Yes | Must be `true` unless the asset is explicitly named and unambiguous. |

### H. `AiAppliedControlDraft`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `platform_entity` | `string` | Yes | Fixed value: `AppliedControl`. |
| `proposed_ref_id` | `string \| null` | Yes | Optional draft ref ID suggestion. |
| `name` | `string \| null` | Yes | Suggested control name. |
| `control_category` | `string \| null` | Yes | Suggested category label. Must not be confused with `ReferenceControl`. |
| `implementation_status` | `string \| null` | Yes | Suggested applied-control status aligned to platform values such as `to_do`, `in_progress`, `active`, `on_hold`, `deprecated`, or `--`. |
| `linked_asset_refs` | `string[]` | Yes | Draft references to related asset drafts. |
| `related_requirement_refs_if_inferred` | `string[]` | Yes | Requirement refs, not requirement-assessment IDs, unless a later lookup resolves them. |
| `control_type` | `string \| null` | Yes | Human-readable type such as preventive, detective, corrective, or governance. |
| `suggested_action` | `string` | Yes | Usually `propose_create`, `propose_reuse`, or `defer_until_human_review`. |
| `confidence` | `number` | Yes | `0.0..1.0`. |
| `rationale` | `string` | Yes | Why the control was suggested. |
| `source_text_refs` | `AiSourceTextRef[]` | Yes | Traceability to source text. |
| `needs_review` | `boolean` | Yes | Must be `true` if existing-control reuse is unresolved. |

### I. `AiVulnerabilityDraft`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `platform_entity` | `string` | Yes | Fixed value: `Vulnerability`. |
| `proposed_ref_id` | `string \| null` | Yes | Optional draft ref ID suggestion. |
| `name` | `string \| null` | Yes | Suggested vulnerability name. |
| `severity` | `integer \| null` | Yes | Recommended numeric severity aligned to platform expectations. Suggested values: `-1, 0, 1, 2, 3, 4`. |
| `linked_asset_refs` | `string[]` | Yes | Draft references to related asset drafts. |
| `related_control_gap_refs` | `string[]` | Yes | Draft references to control drafts or missing-control indicators. |
| `weakness_type` | `string \| null` | Yes | Human-readable weakness label, such as IAM weakness or logging gap. |
| `suggested_action` | `string` | Yes | Usually `propose_create` or `defer_until_human_review`. |
| `confidence` | `number` | Yes | `0.0..1.0`. |
| `rationale` | `string` | Yes | Why the vulnerability was inferred. |
| `source_text_refs` | `AiSourceTextRef[]` | Yes | Traceability to source text. |
| `needs_review` | `boolean` | Yes | Must be `true` if severity or control linkage is uncertain. |

### J. `AiRiskAssessmentDraft`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `platform_entity` | `string` | Yes | Fixed value: `RiskAssessment`. |
| `name` | `string \| null` | Yes | Suggested risk-assessment name. |
| `reference_id` | `string \| null` | Yes | Optional draft ref ID suggestion. |
| `folder_dependency` | `string` | Yes | Draft key or alias for the target folder. |
| `perimeter_dependency` | `string` | Yes | Draft key or alias for the target perimeter. |
| `risk_matrix_preference` | `string \| null` | Yes | Free-text or library-like hint. Must not be treated as a final matrix ID without lookup. |
| `tolerance_preference` | `number \| null` | Yes | Optional suggested risk tolerance. Use `null` when not inferable. |
| `suggested_action` | `string` | Yes | Usually `propose_create` or `defer_until_human_review`. |
| `confidence` | `number` | Yes | `0.0..1.0`. |
| `rationale` | `string` | Yes | Why a risk assessment is suggested. |
| `source_text_refs` | `AiSourceTextRef[]` | Yes | Traceability to source text. |
| `needs_review` | `boolean` | Yes | Must be `true` until the reviewer confirms matrix and tolerance preferences. |

### K. `AiRiskScenarioDraft`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `platform_entity` | `string` | Yes | Fixed value: `RiskScenario`. |
| `proposed_ref_id` | `string \| null` | Yes | Optional draft ref ID suggestion. |
| `title` | `string \| null` | Yes | Short scenario title. |
| `description` | `string \| null` | Yes | Narrative risk scenario description. |
| `linked_asset_refs` | `string[]` | Yes | Draft asset references. |
| `linked_vulnerability_refs` | `string[]` | Yes | Draft vulnerability references. |
| `linked_existing_control_refs` | `string[]` | Yes | Draft references to controls believed to exist already. |
| `linked_extra_control_refs` | `string[]` | Yes | Draft references to suggested additional controls. |
| `candidate_threats` | `string[]` | Yes | Threat labels or threat draft references. |
| `current_probability` | `integer \| null` | Yes | Suggested probability level only if inferable. |
| `current_impact` | `integer \| null` | Yes | Suggested impact level only if inferable. |
| `residual_probability` | `integer \| null` | Yes | Suggested residual probability after extra controls, if inferable. |
| `residual_impact` | `integer \| null` | Yes | Suggested residual impact after extra controls, if inferable. |
| `scoring_is_ai_suggested` | `boolean` | Yes | Must be `true` whenever any probability/impact values are AI-inferred. |
| `treatment_direction` | `string \| null` | Yes | Suggested direction using platform semantics such as `mitigate`, `accept`, `avoid`, `transfer`, or `open`. For Step 1 this is advisory only. |
| `suggested_action` | `string` | Yes | Usually `propose_create` or `defer_until_human_review`. |
| `confidence` | `number` | Yes | `0.0..1.0`. |
| `rationale` | `string` | Yes | Why the risk scenario was inferred. |
| `source_text_refs` | `AiSourceTextRef[]` | Yes | Traceability to source text. |
| `needs_review` | `boolean` | Yes | Must be `true` whenever any score or treatment is inferred. |

### L. `AiRequirementFocusDraft`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `platform_entity` | `string` | Yes | Fixed value: `RequirementNode`. |
| `requirement_ref` | `string \| null` | Yes | Suggested requirement reference, such as a framework control or clause reference. |
| `requirement_lookup_required` | `boolean` | Yes | Must be `true` until a real requirement-node lookup confirms a match. |
| `requirement_node_endpoint_note` | `string` | Yes | Must note that backend uses `/api/requirement-nodes/` while frontend uses `requirements`. |
| `reason_for_focus` | `string` | Yes | Why the parser highlighted this requirement area. |
| `related_control_refs` | `string[]` | Yes | Draft references to suggested applied controls. |
| `related_asset_refs` | `string[]` | Yes | Draft references to related assets. |
| `expected_evidence` | `string[]` | Yes | Free-text evidence expectations tied to this requirement focus. |
| `confidence` | `number` | Yes | `0.0..1.0`. |
| `rationale` | `string` | Yes | Why this requirement focus belongs in the draft. |
| `source_text_refs` | `AiSourceTextRef[]` | Yes | Traceability to source text. |
| `needs_review` | `boolean` | Yes | Must be `true` until a real requirement-node match is confirmed. |

### M. `AiEvidenceExpectationDraft`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `expected_evidence_name` | `string` | Yes | Human-readable evidence item expected by the parser. |
| `evidence_type` | `string` | Yes | Suggested evidence type such as document, screenshot, report, log export, ticket, or policy artifact. |
| `related_requirement_refs` | `string[]` | Yes | Requirement references, not IDs, unless later resolved. |
| `related_control_refs` | `string[]` | Yes | Draft references to related control drafts. |
| `related_asset_refs` | `string[]` | Yes | Draft references to related asset drafts. |
| `why_needed` | `string` | Yes | Explanation of why this evidence would matter. |
| `suggested_validation_status` | `string \| null` | Yes | Suggested future evidence status, usually `draft` or `missing` for a new object. This is advisory only. |
| `confidence` | `number` | Yes | `0.0..1.0`. |
| `rationale` | `string` | Yes | Why the evidence expectation was suggested. |
| `source_text_refs` | `AiSourceTextRef[]` | Yes | Traceability to source text. |
| `needs_review` | `boolean` | Yes | Must be `true` because evidence sufficiency always requires human validation. |

## 5. Validation Rules

The future implementation must validate the draft contract before returning it to the frontend.

### Required fields

- Top-level required fields:
  - `draft_type`
  - `schema_version`
  - `source_summary`
  - `overall_confidence`
  - `needs_human_review`
  - `blocking_questions`
  - `warnings`
  - `canonical_mappings_used`
  - `case_context`
  - `framework_resolution`
  - `case_setup_draft`
  - `asset_drafts`
  - `applied_control_drafts`
  - `vulnerability_drafts`
  - `risk_assessment_draft`
  - `risk_scenario_drafts`
  - `requirement_focus_drafts`
  - `evidence_expectation_drafts`
  - `human_review_checklist`
  - `next_system_actions`
- Every nested draft object must include:
  - `confidence`
  - `rationale`
  - `needs_review`
- Every inferred object draft except purely administrative helper objects must include `source_text_refs`.

### Allowed enum values

- `draft_type`: must equal `AiCaseIntakeDraft`
- `suggested_action`: `lookup_existing`, `propose_create`, `propose_reuse`, `propose_update_after_create`, `defer_until_human_review`, `no_action`
- `AiFolderDomainDraft.content_type`: for Step 1 domain use, only `DO` is valid. If any other value is proposed, `needs_review` must be `true` and a warning must be emitted.
- `AiPerimeterDraft.lifecycle_status_if_known`: if provided, should align with `Perimeter.lc_status` values: `undefined`, `in_design`, `in_dev`, `in_prod`, `eol`, `dropped`
- `AiComplianceAssessmentDraft.status`: if provided, should align with assessment status values such as `planned`, `in_progress`, `in_review`, `done`, `deprecated`
- `AiAppliedControlDraft.implementation_status`: if provided, should align with `AppliedControl.Status` values such as `to_do`, `in_progress`, `on_hold`, `active`, `deprecated`, `--`
- `AiRiskScenarioDraft.treatment_direction`: if provided, should align with `RiskScenario` treatment options `open`, `mitigate`, `accept`, `avoid`, `transfer`
- `AiEvidenceExpectationDraft.suggested_validation_status`: if provided, it must be advisory only and should align to future `Evidence.Status` values such as `draft`, `missing`, `in_review`, `approved`, `rejected`, `expired`

### Confidence range

- Every `confidence` field must be numeric in the range `0.0..1.0`
- `overall_confidence` must also be `0.0..1.0`
- Suggested future frontend bands:
  - `0.85..1.00`: high
  - `0.60..0.84`: medium
  - `0.00..0.59`: low

### `needs_review` behavior

- For Step 1, `needs_human_review` at the top level must always be `true`
- For any draft object, `needs_review` must be `true` if:
  - confidence is below `0.85`
  - the parser had to infer a platform-native mapping from ambiguous business language
  - an existing-record lookup is still required
  - the suggested action depends on later confirmation
  - probability, impact, severity, or treatment were inferred rather than confirmed
  - framework, folder reuse, or requirement-node matching is unresolved

### Internal entity name restrictions

- `platform_entity` must only use canonical names verified in `AI_CANONICAL_WORKFLOW_DICTIONARY.md`
- The parser must not emit invented types such as:
  - `DomainRecord`
  - `AuditRecord`
  - `RemediationPlan`
  - `FrameworkLoadRequest`
  - `ComplianceGapCase`
- The parser must not use business labels as internal entity identifiers
  - invalid: `platform_entity: "Domain"`
  - valid: `platform_entity: "Folder"`

### Ref ID format expectations

- Any AI-suggested `reference_id` or `proposed_ref_id` is a draft suggestion only
- Suggested format should follow `^[A-Z0-9._:-]{3,100}$`
- If the parser cannot produce a clean ref ID, it should return `null` rather than inventing a low-quality identifier
- The implementation must not claim uniqueness until a later write-time validation step

### No database write rule

- The endpoint must not create, update, delete, load, import, submit, approve, revoke, or close any persisted object
- It must not call `QuickStartSerializer.create()` or any write serializer `save()` method
- It must not trigger `StoredLibrary.load()`, `FolderWriteSerializer.save()`, `ComplianceAssessmentWriteSerializer.save()`, or any equivalent write path

### No final compliance decision rule

- The parser must not produce final `RequirementAssessment.result` decisions
- It may only suggest requirement focus areas and evidence expectations
- It must not claim that an audit is compliant, partially compliant, non-compliant, or complete

### No final risk acceptance rule

- The parser must not create `RiskAcceptance` drafts as executable state changes
- It may mention that future risk acceptance may be needed, but it must not emit approval-ready acceptance state or approver decisions as final outcomes

### No audit closure rule

- The parser must not close audits, findings, validation flows, or workflow cases
- It must not emit final closure or approval state claims

## 6. Human Review Rules

The human reviewer must approve the following before any later object-creation workflow is allowed.

1. **Framework selection**
   - Confirm the intended framework path
   - Confirm whether a `StoredLibrary`, `LoadedLibrary`, and final `Framework` lookup will be required

2. **Domain / folder creation or reuse**
   - Confirm whether to reuse an existing `Folder`
   - Confirm the suggested domain name
   - Confirm that the business concept truly maps to a domain-level folder and not an enclave or other scope

3. **Perimeter name and scope**
   - Confirm the perimeter label
   - Confirm the systems, processes, or business unit included in scope

4. **Audit / compliance assessment name and period**
   - Confirm the `ComplianceAssessment` name
   - Confirm dates or period labels
   - Confirm whether a baseline audit is involved

5. **Asset list**
   - Approve, edit, merge, or remove proposed `Asset` drafts
   - Confirm criticality and scope relevance

6. **Applied control list**
   - Confirm whether a proposed control should become an `AppliedControl` draft or should instead be matched to an existing control later

7. **Vulnerability list**
   - Confirm inferred weaknesses, severity assumptions, and asset linkages

8. **Risk assessment settings**
   - Confirm whether a `RiskAssessment` should exist at all
   - Confirm matrix preference and tolerance preference

9. **Risk scenario scoring**
   - Confirm current and residual probability and impact suggestions
   - Confirm proposed treatment direction

10. **Requirement focus**
    - Confirm the targeted requirement areas
    - Confirm the requirement-node lookup strategy because frontend uses `requirements` while backend uses `/api/requirement-nodes/`

11. **Evidence expectations**
    - Confirm which evidence artifacts are truly expected and whether they belong to control, audit, or risk workflows

Human review principle for Step 1:

- the parser output is a draft
- every draft object may be accepted, edited, or rejected individually
- no object may be auto-created by default

## 7. Example Input

The repository does not contain a pre-existing `Al-Rawasi Fintech ECC-1:2018` scenario file. The following example input is therefore a self-contained intake example for contract design purposes.

```json
{
  "scenario_text": "Al-Rawasi Fintech is preparing for an ECC-1:2018 readiness review before launching its Saudi payment services expansion. The scope should cover the core payment platform, customer onboarding portal, IAM administration, cloud operations, security monitoring, and incident handling processes. Management wants a review completed before 2026-12-15. The team believes access control governance, privileged access monitoring, log retention, incident response evidence, and third-party access management may need attention. They also want likely assets, control gaps, and risk scenarios drafted for human review, but they do not want any records created automatically.",
  "preferred_framework": "ECC-1:2018",
  "assessment_period": {
    "label": "Q4 2026 readiness review",
    "start_date": "2026-10-01",
    "end_date": "2026-12-15"
  },
  "organization_hint": "Al-Rawasi Fintech",
  "scope_hint": "Core payment platform, onboarding portal, IAM, cloud operations, SOC monitoring, and incident handling",
  "known_deadline": "2026-12-15",
  "known_trigger": "pre-regulatory-readiness review",
  "user_locale": "en",
  "strict_mode": true
}
```

## 8. Example Output JSON

The following example output is a complete draft-only payload. It uses platform-native entity names internally, keeps uncertain items under review, and does not claim that any database record was created.

```json
{
  "draft_type": "AiCaseIntakeDraft",
  "schema_version": "0.2.0",
  "source_summary": {
    "detected_language": "en",
    "input_char_count": 686,
    "strict_mode_applied": true,
    "scenario_excerpt": "Al-Rawasi Fintech is preparing for an ECC-1:2018 readiness review before launching its Saudi payment services expansion.",
    "parser_notes": [
      "Framework hint supplied by user text and preferred_framework.",
      "No database lookup was performed.",
      "All object suggestions remain advisory-only."
    ]
  },
  "overall_confidence": 0.78,
  "needs_human_review": true,
  "blocking_questions": [
    {
      "question_id": "BQ-001",
      "question_text": "Should the draft reuse an existing Folder for Al-Rawasi Fintech or propose a new domain Folder?",
      "reason": "Folder reuse versus creation cannot be confirmed without a lookup.",
      "affected_fields": [
        "case_setup_draft.folder_domain_draft"
      ],
      "severity": "blocking"
    },
    {
      "question_id": "BQ-002",
      "question_text": "Which exact ECC-1:2018 library artifact should be used if multiple StoredLibrary entries match the request?",
      "reason": "Framework selection must resolve through StoredLibrary, LoadedLibrary, and Framework lookups.",
      "affected_fields": [
        "framework_resolution"
      ],
      "severity": "blocking"
    },
    {
      "question_id": "BQ-003",
      "question_text": "Should a RiskAssessment be created alongside the ComplianceAssessment in the first approved creation step?",
      "reason": "The scenario suggests risk work, but the user may want audit-only onboarding first.",
      "affected_fields": [
        "risk_assessment_draft",
        "case_setup_draft.optional_risk_assessment_draft"
      ],
      "severity": "blocking"
    }
  ],
  "warnings": [
    {
      "code": "W-REQ-ENDPOINT-MISMATCH",
      "message": "Requirement lookup must account for frontend key 'requirements' versus backend route '/api/requirement-nodes/'.",
      "affected_fields": [
        "requirement_focus_drafts"
      ],
      "needs_review": true
    },
    {
      "code": "W-WORKFLOWCASE-DEFERRED",
      "message": "WorkflowCase is intentionally not a hard dependency until serializer verification is completed.",
      "affected_fields": [
        "next_system_actions"
      ],
      "needs_review": true
    },
    {
      "code": "W-FRAMEWORK-LOOKUP-PENDING",
      "message": "No StoredLibrary, LoadedLibrary, or Framework object was resolved during intake.",
      "affected_fields": [
        "framework_resolution.selected_framework_id"
      ],
      "needs_review": true
    }
  ],
  "canonical_mappings_used": [
    {
      "business_term": "Domain",
      "platform_entity": "Folder",
      "api_endpoint": "/api/folders/",
      "note": "Business domain maps to Folder with domain content semantics."
    },
    {
      "business_term": "Audit",
      "platform_entity": "ComplianceAssessment",
      "api_endpoint": "/api/compliance-assessments/",
      "note": "Audit is represented by ComplianceAssessment."
    },
    {
      "business_term": "Framework",
      "platform_entity": "StoredLibrary -> LoadedLibrary -> Framework",
      "api_endpoint": "/api/stored-libraries/ then /api/loaded-libraries/ then /api/frameworks/",
      "note": "Framework resolution is a multi-step lookup path."
    },
    {
      "business_term": "Requirement",
      "platform_entity": "RequirementNode",
      "api_endpoint": "/api/requirement-nodes/",
      "note": "Frontend CRUD key is 'requirements' while backend route is '/api/requirement-nodes/'."
    },
    {
      "business_term": "Remediation",
      "platform_entity": "AppliedControl",
      "api_endpoint": "/api/applied-controls/",
      "note": "Action plan is reporting, not a standalone model."
    }
  ],
  "case_context": {
    "organization_name": "Al-Rawasi Fintech",
    "industry": "fintech",
    "geography": [
      "Saudi Arabia"
    ],
    "regulatory_context": [
      "ECC-1:2018 readiness",
      "payment services launch readiness"
    ],
    "assessment_period": {
      "label": "Q4 2026 readiness review",
      "start_date": "2026-10-01",
      "end_date": "2026-12-15"
    },
    "deadline": "2026-12-15",
    "trigger": "pre-regulatory-readiness review",
    "business_objective": "Prepare a human-reviewed readiness draft for an ECC-1:2018-aligned launch assessment covering payment operations and supporting security processes.",
    "source_text_refs": [
      {
        "ref_id": "T1",
        "excerpt": "preparing for an ECC-1:2018 readiness review before launching its Saudi payment services expansion",
        "char_start": 31,
        "char_end": 128
      },
      {
        "ref_id": "T2",
        "excerpt": "Management wants a review completed before 2026-12-15.",
        "char_start": 307,
        "char_end": 362
      }
    ],
    "confidence": 0.9,
    "needs_review": true
  },
  "framework_resolution": {
    "requested_framework_name": "ECC-1:2018",
    "canonical_framework_name": "ECC-1:2018",
    "stored_library_lookup_required": true,
    "loaded_library_lookup_required": true,
    "framework_lookup_required": true,
    "candidate_frameworks": [
      {
        "candidate_label": "ECC-1:2018",
        "stored_library_urn": null,
        "loaded_library_urn_or_id": null,
        "framework_id": null,
        "match_confidence": 0.86,
        "needs_review": true,
        "rationale": "The scenario explicitly names ECC-1:2018, but no library lookup has been executed."
      },
      {
        "candidate_label": "ECC-aligned national cybersecurity control framework",
        "stored_library_urn": null,
        "loaded_library_urn_or_id": null,
        "framework_id": null,
        "match_confidence": 0.52,
        "needs_review": true,
        "rationale": "Fallback generic candidate retained because the exact stored library match is unresolved."
      }
    ],
    "selected_framework_id": null,
    "needs_review": true,
    "rationale": "Framework resolution must follow the StoredLibrary -> LoadedLibrary -> Framework lookup chain before any create flow."
  },
  "case_setup_draft": {
    "folder_domain_draft": {
      "platform_entity": "Folder",
      "display_label": "Domain",
      "name": "Al-Rawasi Fintech",
      "description": "Proposed domain for ECC-1:2018 readiness work covering payment platform operations and supporting security processes.",
      "content_type": "DO",
      "existing_record_lookup_required": true,
      "suggested_action": "lookup_existing",
      "confidence": 0.81,
      "rationale": "The organization hint strongly suggests a domain-level Folder, but reuse versus creation is unresolved.",
      "source_text_refs": [
        {
          "ref_id": "T3",
          "excerpt": "Al-Rawasi Fintech",
          "char_start": 0,
          "char_end": 18
        }
      ],
      "needs_review": true
    },
    "perimeter_draft": {
      "platform_entity": "Perimeter",
      "name": "KSA Payment Services Launch Scope",
      "reference_id": "PER.RAWASI.KSA.2026",
      "description": "Suggested perimeter covering the payment platform, customer onboarding portal, IAM administration, cloud operations, security monitoring, and incident handling.",
      "folder_dependency": "folder_domain_draft",
      "lifecycle_status_if_known": "in_design",
      "suggested_action": "propose_create",
      "confidence": 0.79,
      "rationale": "The scenario defines a concrete launch-readiness scope broad enough to justify a named perimeter.",
      "source_text_refs": [
        {
          "ref_id": "T4",
          "excerpt": "The scope should cover the core payment platform, customer onboarding portal, IAM administration, cloud operations, security monitoring, and incident handling processes.",
          "char_start": 130,
          "char_end": 304
        }
      ],
      "needs_review": true
    },
    "compliance_assessment_draft": {
      "platform_entity": "ComplianceAssessment",
      "name": "Al-Rawasi Fintech ECC-1:2018 Readiness Review 2026",
      "reference_id": "AUD.RAWASI.ECC.2026",
      "folder_dependency": "folder_domain_draft",
      "perimeter_dependency": "perimeter_draft",
      "framework_dependency": "framework_resolution.candidate_frameworks[0]",
      "assessment_period": {
        "label": "Q4 2026 readiness review",
        "start_date": "2026-10-01",
        "end_date": "2026-12-15"
      },
      "status": "planned",
      "auto_requirement_assessment_expected": true,
      "suggested_action": "propose_create",
      "confidence": 0.88,
      "rationale": "The scenario is clearly framed as a readiness review and maps canonically to ComplianceAssessment.",
      "source_text_refs": [
        {
          "ref_id": "T1",
          "excerpt": "preparing for an ECC-1:2018 readiness review",
          "char_start": 31,
          "char_end": 75
        },
        {
          "ref_id": "T2",
          "excerpt": "Management wants a review completed before 2026-12-15.",
          "char_start": 307,
          "char_end": 362
        }
      ],
      "needs_review": true
    },
    "optional_risk_assessment_draft": {
      "platform_entity": "RiskAssessment",
      "name": "Al-Rawasi Fintech Launch Risk Assessment 2026",
      "reference_id": "RA.RAWASI.KSA.2026",
      "folder_dependency": "folder_domain_draft",
      "perimeter_dependency": "perimeter_draft",
      "risk_matrix_preference": "KSA launch operational risk matrix - lookup required",
      "tolerance_preference": null,
      "suggested_action": "defer_until_human_review",
      "confidence": 0.67,
      "rationale": "The scenario requests likely risk scenarios, but it does not confirm whether a formal RiskAssessment should be created in the first approved step.",
      "source_text_refs": [
        {
          "ref_id": "T5",
          "excerpt": "They also want likely assets, control gaps, and risk scenarios drafted for human review",
          "char_start": 477,
          "char_end": 561
        }
      ],
      "needs_review": true
    },
    "creation_order": [
      "StoredLibrary lookup",
      "LoadedLibrary lookup",
      "Framework lookup",
      "Folder lookup or create decision",
      "Perimeter draft approval",
      "ComplianceAssessment draft approval",
      "RequirementAssessment auto-generation expected",
      "Optional RiskAssessment decision"
    ],
    "dependency_notes": [
      "ComplianceAssessment creation is expected to auto-create RequirementAssessment records.",
      "Framework resolution must not be skipped.",
      "RiskAssessment is optional at intake time and should not be auto-created from this draft."
    ],
    "needs_review": true
  },
  "asset_drafts": [
    {
      "platform_entity": "Asset",
      "proposed_ref_id": "AST.RAWASI.PAYMENT.PLATFORM",
      "name": "Core Payment Platform",
      "asset_type": "PR",
      "folder_dependency": "folder_domain_draft",
      "perimeter_relevance": "Primary transaction-processing system in the proposed perimeter.",
      "business_role": "Processes payment transactions and related service workflows.",
      "criticality_if_inferred": "high",
      "suggested_action": "propose_create",
      "confidence": 0.91,
      "rationale": "The scenario explicitly names the core payment platform as in-scope.",
      "source_text_refs": [
        {
          "ref_id": "T4A",
          "excerpt": "core payment platform",
          "char_start": 157,
          "char_end": 178
        }
      ],
      "needs_review": true
    },
    {
      "platform_entity": "Asset",
      "proposed_ref_id": "AST.RAWASI.ONBOARDING.PORTAL",
      "name": "Customer Onboarding Portal",
      "asset_type": "PR",
      "folder_dependency": "folder_domain_draft",
      "perimeter_relevance": "User-facing onboarding component named directly in the scenario.",
      "business_role": "Supports customer onboarding and account setup.",
      "criticality_if_inferred": "medium",
      "suggested_action": "propose_create",
      "confidence": 0.88,
      "rationale": "The scenario explicitly calls out the onboarding portal within scope.",
      "source_text_refs": [
        {
          "ref_id": "T4B",
          "excerpt": "customer onboarding portal",
          "char_start": 180,
          "char_end": 206
        }
      ],
      "needs_review": true
    },
    {
      "platform_entity": "Asset",
      "proposed_ref_id": "AST.RAWASI.IAM.ADMIN",
      "name": "IAM Administration Service",
      "asset_type": "SP",
      "folder_dependency": "folder_domain_draft",
      "perimeter_relevance": "Administrative support service explicitly included in scope.",
      "business_role": "Supports privileged and identity administration.",
      "criticality_if_inferred": "high",
      "suggested_action": "propose_create",
      "confidence": 0.83,
      "rationale": "IAM administration is directly named and later linked to access-control concerns.",
      "source_text_refs": [
        {
          "ref_id": "T4C",
          "excerpt": "IAM administration",
          "char_start": 208,
          "char_end": 226
        },
        {
          "ref_id": "T6",
          "excerpt": "access control governance, privileged access monitoring",
          "char_start": 385,
          "char_end": 440
        }
      ],
      "needs_review": true
    }
  ],
  "applied_control_drafts": [
    {
      "platform_entity": "AppliedControl",
      "proposed_ref_id": "CTL.RAWASI.ACCESS.GOV",
      "name": "Access Control Governance Review",
      "control_category": "governance",
      "implementation_status": "to_do",
      "linked_asset_refs": [
        "AST.RAWASI.IAM.ADMIN",
        "AST.RAWASI.PAYMENT.PLATFORM"
      ],
      "related_requirement_refs_if_inferred": [
        "ECC.ACCESS_CONTROL",
        "ECC.PRIVILEGED_ACCESS"
      ],
      "control_type": "preventive",
      "suggested_action": "propose_create",
      "confidence": 0.8,
      "rationale": "The scenario explicitly signals likely attention on access control governance and privileged access monitoring.",
      "source_text_refs": [
        {
          "ref_id": "T6",
          "excerpt": "access control governance, privileged access monitoring",
          "char_start": 385,
          "char_end": 440
        }
      ],
      "needs_review": true
    },
    {
      "platform_entity": "AppliedControl",
      "proposed_ref_id": "CTL.RAWASI.LOG.RETENTION",
      "name": "Security Log Retention and Monitoring Control",
      "control_category": "operations",
      "implementation_status": "to_do",
      "linked_asset_refs": [
        "AST.RAWASI.PAYMENT.PLATFORM"
      ],
      "related_requirement_refs_if_inferred": [
        "ECC.LOGGING_MONITORING"
      ],
      "control_type": "detective",
      "suggested_action": "propose_create",
      "confidence": 0.77,
      "rationale": "The scenario calls out log retention as a likely control-gap area.",
      "source_text_refs": [
        {
          "ref_id": "T7",
          "excerpt": "log retention",
          "char_start": 442,
          "char_end": 455
        }
      ],
      "needs_review": true
    },
    {
      "platform_entity": "AppliedControl",
      "proposed_ref_id": "CTL.RAWASI.THIRD.PARTY.ACCESS",
      "name": "Third-Party Access Management Control",
      "control_category": "third_party",
      "implementation_status": "to_do",
      "linked_asset_refs": [
        "AST.RAWASI.ONBOARDING.PORTAL",
        "AST.RAWASI.IAM.ADMIN"
      ],
      "related_requirement_refs_if_inferred": [
        "ECC.THIRD_PARTY_ACCESS"
      ],
      "control_type": "preventive",
      "suggested_action": "propose_create",
      "confidence": 0.74,
      "rationale": "Third-party access management is called out directly but specific integration assets are not yet known.",
      "source_text_refs": [
        {
          "ref_id": "T8",
          "excerpt": "third-party access management",
          "char_start": 489,
          "char_end": 516
        }
      ],
      "needs_review": true
    }
  ],
  "vulnerability_drafts": [
    {
      "platform_entity": "Vulnerability",
      "proposed_ref_id": "VULN.RAWASI.PAM.GAP",
      "name": "Privileged Access Monitoring Gap",
      "severity": 3,
      "linked_asset_refs": [
        "AST.RAWASI.IAM.ADMIN"
      ],
      "related_control_gap_refs": [
        "CTL.RAWASI.ACCESS.GOV"
      ],
      "weakness_type": "IAM monitoring weakness",
      "suggested_action": "propose_create",
      "confidence": 0.73,
      "rationale": "The scenario hints that privileged access monitoring needs attention but does not confirm whether a current control exists.",
      "source_text_refs": [
        {
          "ref_id": "T6",
          "excerpt": "privileged access monitoring",
          "char_start": 413,
          "char_end": 440
        }
      ],
      "needs_review": true
    }
  ],
  "risk_assessment_draft": {
    "platform_entity": "RiskAssessment",
    "name": "Al-Rawasi Fintech Launch Risk Assessment 2026",
    "reference_id": "RA.RAWASI.KSA.2026",
    "folder_dependency": "folder_domain_draft",
    "perimeter_dependency": "perimeter_draft",
    "risk_matrix_preference": "Lookup required for an approved risk matrix library",
    "tolerance_preference": null,
    "suggested_action": "defer_until_human_review",
    "confidence": 0.67,
    "rationale": "Risk scenarios were requested, but the user did not explicitly authorize parallel risk-assessment creation.",
    "source_text_refs": [
      {
        "ref_id": "T5",
        "excerpt": "they also want likely assets, control gaps, and risk scenarios drafted for human review",
        "char_start": 477,
        "char_end": 561
      }
    ],
    "needs_review": true
  },
  "risk_scenario_drafts": [
    {
      "platform_entity": "RiskScenario",
      "proposed_ref_id": "RS.RAWASI.PAM.ABUSE",
      "title": "Abuse of privileged access impacts payment operations",
      "description": "A privileged user or compromised admin path could be misused to alter platform configuration, weaken controls, or disrupt payment operations before launch.",
      "linked_asset_refs": [
        "AST.RAWASI.PAYMENT.PLATFORM",
        "AST.RAWASI.IAM.ADMIN"
      ],
      "linked_vulnerability_refs": [
        "VULN.RAWASI.PAM.GAP"
      ],
      "linked_existing_control_refs": [],
      "linked_extra_control_refs": [
        "CTL.RAWASI.ACCESS.GOV"
      ],
      "candidate_threats": [
        "privileged misuse",
        "credential compromise"
      ],
      "current_probability": 3,
      "current_impact": 4,
      "residual_probability": 2,
      "residual_impact": 3,
      "scoring_is_ai_suggested": true,
      "treatment_direction": "mitigate",
      "suggested_action": "defer_until_human_review",
      "confidence": 0.64,
      "rationale": "The scenario strongly implies IAM-related launch risk, but matrix-specific scoring is still heuristic at intake time.",
      "source_text_refs": [
        {
          "ref_id": "T6",
          "excerpt": "access control governance, privileged access monitoring",
          "char_start": 385,
          "char_end": 440
        }
      ],
      "needs_review": true
    },
    {
      "platform_entity": "RiskScenario",
      "proposed_ref_id": "RS.RAWASI.LOG.EVIDENCE.FAILURE",
      "title": "Insufficient log retention weakens monitoring and incident evidence",
      "description": "If security logs are incomplete or not retained adequately, the organization may be unable to detect, investigate, or evidence incidents during readiness review and early operations.",
      "linked_asset_refs": [
        "AST.RAWASI.PAYMENT.PLATFORM"
      ],
      "linked_vulnerability_refs": [],
      "linked_existing_control_refs": [],
      "linked_extra_control_refs": [
        "CTL.RAWASI.LOG.RETENTION"
      ],
      "candidate_threats": [
        "undetected malicious activity",
        "insufficient audit trail"
      ],
      "current_probability": 3,
      "current_impact": 3,
      "residual_probability": 2,
      "residual_impact": 2,
      "scoring_is_ai_suggested": true,
      "treatment_direction": "mitigate",
      "suggested_action": "defer_until_human_review",
      "confidence": 0.62,
      "rationale": "The scenario names log retention and incident response evidence as likely areas of concern.",
      "source_text_refs": [
        {
          "ref_id": "T7",
          "excerpt": "log retention, incident response evidence",
          "char_start": 442,
          "char_end": 482
        }
      ],
      "needs_review": true
    }
  ],
  "requirement_focus_drafts": [
    {
      "platform_entity": "RequirementNode",
      "requirement_ref": "ECC.ACCESS_CONTROL",
      "requirement_lookup_required": true,
      "requirement_node_endpoint_note": "Use backend '/api/requirement-nodes/' for lookup; frontend CRUD key is 'requirements'.",
      "reason_for_focus": "The scenario explicitly highlights access control governance and privileged access monitoring.",
      "related_control_refs": [
        "CTL.RAWASI.ACCESS.GOV"
      ],
      "related_asset_refs": [
        "AST.RAWASI.IAM.ADMIN"
      ],
      "expected_evidence": [
        "access review records",
        "privileged account inventory",
        "approval workflow evidence"
      ],
      "confidence": 0.76,
      "rationale": "High-likelihood requirement area based on explicit scenario wording, but exact RequirementNode match is unresolved.",
      "source_text_refs": [
        {
          "ref_id": "T6",
          "excerpt": "access control governance, privileged access monitoring",
          "char_start": 385,
          "char_end": 440
        }
      ],
      "needs_review": true
    },
    {
      "platform_entity": "RequirementNode",
      "requirement_ref": "ECC.LOGGING_MONITORING",
      "requirement_lookup_required": true,
      "requirement_node_endpoint_note": "Use backend '/api/requirement-nodes/' for lookup; frontend CRUD key is 'requirements'.",
      "reason_for_focus": "The scenario names log retention and security monitoring as likely attention areas.",
      "related_control_refs": [
        "CTL.RAWASI.LOG.RETENTION"
      ],
      "related_asset_refs": [
        "AST.RAWASI.PAYMENT.PLATFORM"
      ],
      "expected_evidence": [
        "log retention policy",
        "SIEM retention configuration",
        "monitoring alert samples"
      ],
      "confidence": 0.74,
      "rationale": "Directly grounded in scenario wording but still requires real RequirementNode lookup.",
      "source_text_refs": [
        {
          "ref_id": "T7A",
          "excerpt": "log retention",
          "char_start": 442,
          "char_end": 455
        },
        {
          "ref_id": "T4D",
          "excerpt": "security monitoring",
          "char_start": 258,
          "char_end": 277
        }
      ],
      "needs_review": true
    },
    {
      "platform_entity": "RequirementNode",
      "requirement_ref": "ECC.INCIDENT_RESPONSE",
      "requirement_lookup_required": true,
      "requirement_node_endpoint_note": "Use backend '/api/requirement-nodes/' for lookup; frontend CRUD key is 'requirements'.",
      "reason_for_focus": "The scenario explicitly mentions incident handling and incident response evidence.",
      "related_control_refs": [],
      "related_asset_refs": [
        "AST.RAWASI.PAYMENT.PLATFORM"
      ],
      "expected_evidence": [
        "incident response plan",
        "incident exercise evidence",
        "incident ticket samples"
      ],
      "confidence": 0.81,
      "rationale": "The focus area is explicit in the scenario even if exact requirement mapping remains pending.",
      "source_text_refs": [
        {
          "ref_id": "T4E",
          "excerpt": "incident handling processes",
          "char_start": 279,
          "char_end": 304
        },
        {
          "ref_id": "T7B",
          "excerpt": "incident response evidence",
          "char_start": 457,
          "char_end": 482
        }
      ],
      "needs_review": true
    }
  ],
  "evidence_expectation_drafts": [
    {
      "expected_evidence_name": "Privileged access review records",
      "evidence_type": "document",
      "related_requirement_refs": [
        "ECC.ACCESS_CONTROL"
      ],
      "related_control_refs": [
        "CTL.RAWASI.ACCESS.GOV"
      ],
      "related_asset_refs": [
        "AST.RAWASI.IAM.ADMIN"
      ],
      "why_needed": "Likely needed to support access governance and privileged monitoring assertions during readiness review.",
      "suggested_validation_status": "missing",
      "confidence": 0.82,
      "rationale": "The scenario names privileged access monitoring as a likely concern.",
      "source_text_refs": [
        {
          "ref_id": "T6",
          "excerpt": "privileged access monitoring",
          "char_start": 413,
          "char_end": 440
        }
      ],
      "needs_review": true
    },
    {
      "expected_evidence_name": "Security log retention configuration export",
      "evidence_type": "log export",
      "related_requirement_refs": [
        "ECC.LOGGING_MONITORING"
      ],
      "related_control_refs": [
        "CTL.RAWASI.LOG.RETENTION"
      ],
      "related_asset_refs": [
        "AST.RAWASI.PAYMENT.PLATFORM"
      ],
      "why_needed": "Likely needed to demonstrate monitoring and retention coverage.",
      "suggested_validation_status": "missing",
      "confidence": 0.79,
      "rationale": "The scenario explicitly names log retention as a likely attention area.",
      "source_text_refs": [
        {
          "ref_id": "T7A",
          "excerpt": "log retention",
          "char_start": 442,
          "char_end": 455
        }
      ],
      "needs_review": true
    },
    {
      "expected_evidence_name": "Incident response exercise or case evidence",
      "evidence_type": "report",
      "related_requirement_refs": [
        "ECC.INCIDENT_RESPONSE"
      ],
      "related_control_refs": [],
      "related_asset_refs": [
        "AST.RAWASI.PAYMENT.PLATFORM"
      ],
      "why_needed": "Likely needed to support incident-handling capability claims during the review.",
      "suggested_validation_status": "missing",
      "confidence": 0.83,
      "rationale": "The scenario explicitly highlights incident handling and incident response evidence.",
      "source_text_refs": [
        {
          "ref_id": "T7B",
          "excerpt": "incident response evidence",
          "char_start": 457,
          "char_end": 482
        }
      ],
      "needs_review": true
    }
  ],
  "human_review_checklist": [
    {
      "check_id": "HR-001",
      "label": "Approve framework resolution path",
      "required": true,
      "related_sections": [
        "framework_resolution"
      ]
    },
    {
      "check_id": "HR-002",
      "label": "Approve Folder reuse or creation decision",
      "required": true,
      "related_sections": [
        "case_setup_draft.folder_domain_draft"
      ]
    },
    {
      "check_id": "HR-003",
      "label": "Approve Perimeter name and scope",
      "required": true,
      "related_sections": [
        "case_setup_draft.perimeter_draft"
      ]
    },
    {
      "check_id": "HR-004",
      "label": "Approve ComplianceAssessment naming and period",
      "required": true,
      "related_sections": [
        "case_setup_draft.compliance_assessment_draft"
      ]
    },
    {
      "check_id": "HR-005",
      "label": "Approve asset drafts",
      "required": true,
      "related_sections": [
        "asset_drafts"
      ]
    },
    {
      "check_id": "HR-006",
      "label": "Approve applied-control drafts",
      "required": true,
      "related_sections": [
        "applied_control_drafts"
      ]
    },
    {
      "check_id": "HR-007",
      "label": "Approve vulnerability and risk scenario drafts",
      "required": true,
      "related_sections": [
        "vulnerability_drafts",
        "risk_scenario_drafts"
      ]
    },
    {
      "check_id": "HR-008",
      "label": "Approve requirement focus and evidence expectations",
      "required": true,
      "related_sections": [
        "requirement_focus_drafts",
        "evidence_expectation_drafts"
      ]
    }
  ],
  "next_system_actions": [
    {
      "action_code": "render_review_draft",
      "description": "Display the intake draft in a human review screen grouped by entity type.",
      "requires_human_confirmation": false,
      "may_write_database": false
    },
    {
      "action_code": "lookup_candidate_frameworks",
      "description": "After reviewer approval, query StoredLibrary, LoadedLibrary, and Framework candidates without creating records.",
      "requires_human_confirmation": true,
      "may_write_database": false
    },
    {
      "action_code": "lookup_existing_folder_candidates",
      "description": "Search for existing Folder records that may match the suggested domain name.",
      "requires_human_confirmation": true,
      "may_write_database": false
    },
    {
      "action_code": "lookup_requirement_nodes",
      "description": "Resolve requirement references through '/api/requirement-nodes/' while preserving the frontend 'requirements' naming note.",
      "requires_human_confirmation": true,
      "may_write_database": false
    },
    {
      "action_code": "prepare_create_payloads_for_later_step",
      "description": "Transform approved draft objects into future create payloads in a later step only.",
      "requires_human_confirmation": true,
      "may_write_database": false
    }
  ]
}
```

## 9. API Design Recommendation for Future Step 1

Future Step 1 needs an endpoint that remains advisory-only and does not inherit object-creation side effects.

### Option comparison

| Option | Pros | Cons | Recommendation |
| --- | --- | --- | --- |
| New endpoint under existing AI/onboarding area | Reuses the current advisory-only service direction already visible in `backend/ai_onboarding/service.py`, `backend/core/views.py` `FolderViewSet.ai_recommendations()`, and `backend/core/debug_views.py`. Keeps AI parsing separate from object writes. Easy to test as pure draft generation. | Requires adding a new route and thin orchestration layer. | **Safest option. Recommended.** |
| New action on quick-start | Reuses a visible onboarding entry point and related frontend flow. | `QuickStartView` and `QuickStartSerializer.create()` are write paths that create `Folder`, `Perimeter`, `ComplianceAssessment`, and optionally `RiskAssessment`. Mixing draft-only intake with this path creates semantic risk and implementation confusion. | Not recommended for Step 1. |
| New endpoint near workflow-cases | Could align with future orchestration concepts. | `WorkflowCase` serializer definitions remain unresolved in the inspected code. Making it a dependency now violates the Step 0.1 caution. | Not recommended until serializer verification is complete. |
| Frontend-only prototype | Fast UX experimentation and no backend route changes. | No authoritative server-side validation, no shared contract enforcement, and too easy to drift from canonical backend vocabulary. | Acceptable only as throwaway UX exploration, not as the Step 1 contract implementation. |

### Recommended Step 1 endpoint strategy

Use a **new endpoint under the existing AI/onboarding area**.

Recommended shape:

- service layer in `backend/ai_onboarding/`
- thin API view exposed through `backend/core/urls.py`
- suggested route: `POST /api/ai/case-intake/`

Reasoning:

- it matches the existing advisory-only pattern seen in `FolderViewSet.ai_recommendations()`
- it avoids the write-side behavior of `QuickStartView`
- it avoids premature dependency on `WorkflowCase`
- it is a clean place to enforce the JSON contract and validation rules before any later Step 1.5 or Step 2 creation workflow

## 10. Frontend Review UX Recommendation

The future frontend should treat the AI result as a review artifact, not an auto-submit form.

Recommended UX behavior:

1. **Case summary panel**
   - Show organization, inferred framework, scope summary, deadline, trigger, and overall confidence.

2. **Draft objects grouped by entity type**
   - Group by:
     - setup
     - assets
     - controls
     - vulnerabilities
     - risk
     - requirement focus
     - evidence expectations

3. **Confidence badges**
   - Every object card should display a confidence badge such as high, medium, or low.

4. **Needs-review flags**
   - Every object card should show a visible `Needs review` flag when `needs_review=true`.

5. **Accept / edit / reject per object**
   - Each draft object should support:
     - accept as-is
     - edit draft values
     - reject from downstream create preparation

6. **Blocking questions panel**
   - Show blocking questions at the top before any approval action is enabled.

7. **Canonical mapping panel**
   - Show business term -> platform entity mappings used in this parse so reviewers can catch vocabulary mistakes early.

8. **No auto-create by default**
   - The first review screen must not create anything automatically.

9. **Deferred final creation action**
   - A final `Create approved objects` action may exist in a later step, but **not** in Step 1.

10. **Requirement lookup warning**
    - When showing requirement focus drafts, display the note that frontend uses `requirements` while backend lookup is `/api/requirement-nodes/`.

Recommended frontend implementation direction for Step 1 review UX:

- use a dedicated review page, not the existing quick-start modal
- use cards or collapsible sections per entity type
- show rationale and source-text evidence inline for every object
- support manual text edits before any future transformation into create payloads

## 11. Step 0.2 Acceptance Criteria

Step 0.2 is complete only when all of the following are true:

1. A single Markdown contract exists for the AI Case Intake draft output.
2. The contract uses the canonical vocabulary from `AI_CANONICAL_WORKFLOW_DICTIONARY.md`.
3. The contract explicitly states that the feature is draft-only and does not write to the database.
4. The contract defines the input payload for the future endpoint, including validation rules.
5. The contract defines the complete top-level output JSON shape.
6. The contract defines field-level schema structures for:
   - `AiCaseContextDraft`
   - `AiFrameworkResolutionDraft`
   - `AiCaseSetupDraft`
   - `AiFolderDomainDraft`
   - `AiPerimeterDraft`
   - `AiComplianceAssessmentDraft`
   - `AiAssetDraft`
   - `AiAppliedControlDraft`
   - `AiVulnerabilityDraft`
   - `AiRiskAssessmentDraft`
   - `AiRiskScenarioDraft`
   - `AiRequirementFocusDraft`
   - `AiEvidenceExpectationDraft`
7. The contract defines cross-cutting validation rules for confidence, enum values, `needs_review`, ref IDs, and canonical entity restrictions.
8. The contract explicitly forbids:
   - database writes
   - final compliance results
   - final risk acceptance
   - audit closure
9. The contract includes a complete example input and complete example output JSON.
10. The example output uses platform-native internal names and does not claim any records were created.
11. The contract records the following unresolved items rather than guessing:
    - `WorkflowCase` remains a non-required dependency until serializer verification is complete
    - requirement lookup must account for frontend `requirements` versus backend `/api/requirement-nodes/`
12. The contract recommends a Step 1 endpoint placement and explains why it is safer than quick-start, workflow-case-first, or frontend-only approaches.
13. The contract recommends a review-first frontend UX where object creation is deferred to a later step.
14. No application code, migrations, dependencies, prompts, external API calls, or AI endpoint implementations were added as part of Step 0.2.
