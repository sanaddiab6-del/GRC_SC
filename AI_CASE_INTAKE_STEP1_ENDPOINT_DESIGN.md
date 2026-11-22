# AI Case Intake Step 1 Endpoint Design

## 1. Executive Summary

Step 1 should introduce the first advisory-only AI endpoint for the platform: an `AI Case Intake / Scenario Parser` endpoint that accepts a natural-language GRC scenario and returns a structured draft JSON aligned to `AI_CASE_INTAKE_JSON_CONTRACT.md`.

The endpoint is intended to:

- parse natural-language intake text
- normalize business terms into canonical Sanadcom platform entities from `AI_CANONICAL_WORKFLOW_DICTIONARY.md`
- propose a reviewable draft for folder/domain, perimeter, compliance assessment, asset, control, vulnerability, risk, requirement focus, and evidence expectations
- return confidence, rationale, source references, warnings, and blocking questions

The endpoint is **advisory-only** and **draft-only**. It must not:

- write to the database
- create or update `Folder`, `Perimeter`, `ComplianceAssessment`, `RequirementAssessment`, `Asset`, `AppliedControl`, `Vulnerability`, `RiskAssessment`, `RiskScenario`, `Evidence`, `Finding`, `FindingsAssessment`, `RiskAcceptance`, or `ValidationFlow`
- load libraries
- make final compliance decisions
- make final risk-acceptance decisions
- make audit or workflow closure decisions

Recommendation: implement Step 1 as a **new endpoint under the existing AI/onboarding area**, backed by a thin API view in the API layer and a read-only service in `backend/ai_onboarding/`.

Reasoning:

- the repository already contains an `ai_onboarding` service package
- `FolderViewSet.ai_recommendations()` already demonstrates an advisory-only AI pattern in `backend/core/views.py`
- `QuickStartView` is a write path and should not be reused for draft-only parsing
- `WorkflowCase` should remain optional until the unresolved serializer gap is verified

## 2. Recommended Endpoint Location

### Option A: New endpoint under existing AI/onboarding area

**Pros**

- Reuses the existing advisory AI service direction already present in `backend/ai_onboarding/service.py`
- Matches the advisory-only style of `FolderViewSet.ai_recommendations()` in `backend/core/views.py`
- Keeps AI intake separate from object-creation flows
- Cleanly fits the Step 0.2 contract, which is draft-only and non-persistent
- Allows future AI endpoints to be grouped under one API namespace

**Cons**

- Requires a new route and thin view layer
- Requires new serializer and guardrail files because the current onboarding package only supports framework and scope recommendations

**Risks**

- The team could accidentally let the new endpoint drift into a generic AI hub without strong contract boundaries
- If provider logic is mixed directly into the view, future maintainability will degrade

**Fit with Step 0.2 contract**

- Strong fit
- Best option for enforcing the new intake JSON contract as a standalone read-only service

### Option B: New action on quick-start

**Pros**

- Reuses a visible onboarding route already present at `/api/quick-start/`
- Shares business context with onboarding flows

**Cons**

- `QuickStartView` and `QuickStartSerializer.create()` are explicitly write-oriented
- Quick-start creates `Folder`, `Perimeter`, and `ComplianceAssessment`, and may also create `RiskAssessment`
- The semantics are opposite to Step 1's no-write rule

**Risks**

- High risk of accidental reuse of write logic
- High risk of reviewer confusion because `quick-start` implies record creation

**Fit with Step 0.2 contract**

- Poor fit
- Conflicts with the requirement that Step 1 produce draft JSON only

### Option C: New action on folders

**Pros**

- `FolderViewSet.ai_recommendations()` already exists and is advisory-only
- Permission style is already simplified to `IsAuthenticated` for advisory recommendations

**Cons**

- The case intake draft is broader than folder creation
- Output includes audits, assets, controls, vulnerabilities, risk, requirements, and evidence expectations, not just domain/folder advice
- Semantically anchoring the feature under `folders` is too narrow

**Risks**

- Endpoint ownership becomes misleading
- Future broad intake logic may become coupled to folder-only onboarding assumptions

**Fit with Step 0.2 contract**

- Partial fit only
- Good inspiration for permission model, but wrong resource boundary

### Option D: New endpoint near workflow-cases

**Pros**

- Could align with future orchestration once case workflows mature
- May later become a natural home for approved, cross-object case setup

**Cons**

- `WorkflowCase` backend serializer definitions remain unresolved from Step 0.1
- The Step 0.2 contract explicitly avoids making `WorkflowCase` a hard dependency
- Intake parsing does not need a persisted workflow-case abstraction yet

**Risks**

- Premature coupling to an unresolved backend surface
- Risk of designing around an object that may not be ready for draft orchestration

**Fit with Step 0.2 contract**

- Weak fit for Step 1
- Acceptable only after serializer verification and after the draft-only path is already stable

### Option E: Frontend-only prototype

**Pros**

- Fast UX experimentation
- No backend route work in the first spike

**Cons**

- No authoritative backend contract enforcement
- No consistent server-side validation of canonical entity names
- Harder to guarantee no-write behavior once the prototype evolves

**Risks**

- High risk of frontend-only schema drift
- High risk of inconsistent behavior across clients

**Fit with Step 0.2 contract**

- Poor fit for real implementation
- Acceptable only for throwaway UX exploration, not for Step 1 delivery

### Recommended safest option for Step 1

Implement Step 1 as a **new endpoint under the existing AI/onboarding area**.

Recommended route family:

- `POST /api/ai/onboarding/case-intake/`

Recommended structural split:

- API view and URL wiring in the normal API layer
- service, provider abstraction, and guardrails in `backend/ai_onboarding/`

This preserves the no-write boundary, aligns with existing advisory AI patterns, and avoids coupling to quick-start or workflow-case behavior.

## 3. Proposed Endpoint Contract

### Endpoint definition

| Property | Recommendation |
| --- | --- |
| HTTP method | `POST` |
| URL path | `/api/ai/onboarding/case-intake/` |
| Authentication | Required |
| Permission requirement | `IsAuthenticated` only for Step 1, with optional feature flag or future custom permission gate |
| Throttling | Add a dedicated DRF throttle scope later, e.g. `ai_case_intake` |
| Side effects | None. Read-only, draft-only |

### Authentication requirements

Current platform defaults in `backend/ciso_assistant/settings.py`:

- `DEFAULT_AUTHENTICATION_CLASSES` includes Knox token auth and JWT auth
- `DEFAULT_PERMISSION_CLASSES` includes `IsAuthenticated` and `core.permissions.RBACPermissions`

Recommendation for Step 1 endpoint:

- explicitly set `permission_classes = [permissions.IsAuthenticated]`
- do **not** inherit `RBACPermissions` for this endpoint because it is not a model-bound CRUD resource

This mirrors the existing advisory pattern used by `FolderViewSet.ai_recommendations()` in `backend/core/views.py`.

### Permission requirements

Recommended Step 1 permission policy:

- user must be authenticated
- endpoint must not require `add_folder`, `add_complianceassessment`, or any other write permission
- endpoint should be optionally guarded later by a feature flag or custom `CanUseAiAdvisoryEndpoints` permission if needed

### Request payload

The request payload must align exactly with the `Input Contract` in `AI_CASE_INTAKE_JSON_CONTRACT.md`.

Recommended shape:

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

### Response payload

The success response payload must align exactly with the top-level output contract in `AI_CASE_INTAKE_JSON_CONTRACT.md`.

Recommended success status:

- `200 OK`

Recommended response shape:

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

### Error response format

Recommendation: follow existing DRF error conventions where possible.

#### Input validation errors

- `400 Bad Request`
- DRF serializer field-error format

Example:

```json
{
  "scenario_text": [
    "This field is required."
  ],
  "non_field_errors": [
    "assessment_period.end_date must be on or after assessment_period.start_date"
  ]
}
```

#### Authentication failure

- `401 Unauthorized`

Example:

```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### Permission failure

- `403 Forbidden`

Example:

```json
{
  "detail": "You do not have permission to perform this action."
}
```

#### Throttle failure

- `429 Too Many Requests`

Example:

```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

#### AI/provider or output-validation failure

Recommendation:

- `422 Unprocessable Entity` if a draft was generated but failed contract/guardrail validation
- `503 Service Unavailable` if no AI provider is available and no safe fallback path exists

Example `422`:

```json
{
  "error_code": "ai_draft_validation_failed",
  "detail": "Generated advisory draft did not pass contract validation.",
  "non_field_errors": [
    "risk_scenario_drafts[0].platform_entity must be 'RiskScenario'"
  ]
}
```

Example `503`:

```json
{
  "error_code": "ai_provider_unavailable",
  "detail": "No advisory AI provider is currently available and no safe fallback response could be produced."
}
```

### Rate-limit or abuse considerations

The platform already uses `ScopedRateThrottle` globally and defines a `registration` throttle scope in `backend/ciso_assistant/settings.py`.

Recommendation for later Step 1 implementation:

- add a dedicated throttle scope such as `ai_case_intake`
- recommended starting rate: `20/hour` per authenticated user
- consider a tighter rate for very large scenarios
- reject oversize payloads before any provider call or heavy processing

## 4. Backend Design

The Step 1 implementation should be thin at the API layer and explicit at the service/validation layer.

### Proposed components

| Suggested file path | Suggested class/function name | Responsibility | Why it belongs there |
| --- | --- | --- | --- |
| `backend/core/views.py` | `AiCaseIntakeView` | HTTP endpoint view. Parse request, validate input, call read-only service, validate output, return response. | Existing API views and route-facing logic live in `core.views`. This keeps URL wiring consistent with `QuickStartView` and `ContentTypeListView`. |
| `backend/core/urls.py` | `path("ai/onboarding/case-intake/", AiCaseIntakeView.as_view(), name="ai-case-intake")` | Route registration. | The API surface is already centralized here. |
| `backend/ai_onboarding/case_intake_serializers.py` | `AiCaseIntakeInputSerializer` | Validate request payload against the Step 0.2 input contract. | This is AI-specific, non-model serializer logic and should stay out of the large generic `core/serializers.py` file. |
| `backend/ai_onboarding/case_intake_serializers.py` | `AiCaseIntakeDraftSerializer` and nested serializers | Validate the generated advisory draft JSON shape. | Keeps output schema explicit and reusable in tests. |
| `backend/ai_onboarding/case_intake_service.py` | `build_case_intake_draft()` | Main orchestration function for parsing, heuristic normalization, optional provider invocation, fallback handling, and draft assembly. | Fits the current `ai_onboarding` service-layer pattern seen in `service.py`, `framework_recommender.py`, and `scope_recommender.py`. |
| `backend/ai_onboarding/case_intake_types.py` | `CaseIntakeRequest`, `CaseIntakeDraftResult` | Internal typed objects or dataclass-style structures for service boundary clarity. | Keeps service I/O explicit without forcing model dependencies. |
| `backend/ai_onboarding/case_intake_guardrails.py` | `validate_case_intake_guardrails()` | Enforce semantic rules not covered by serializer shape validation. | Needed for no-final-decision rules, canonical entity restrictions, `needs_review` enforcement, and source-reference requirements. |
| `backend/ai_onboarding/case_intake_provider.py` | `CaseIntakeProvider`, `CaseIntakeProviderResult`, `get_case_intake_provider()` | Provider abstraction for future LLM integration. | Keeps provider choice out of views and makes it possible to swap implementations without changing the contract. |
| `backend/ai_onboarding/case_intake_fallbacks.py` | `build_rules_only_case_intake_fallback()` | Produce a valid minimal draft when the provider is unavailable or malformed. | Advisory endpoints should degrade safely when possible. |
| `backend/app_tests/test_ai_case_intake.py` | test module | Contract, permission, no-write, and fallback tests. | Existing `backend/app_tests/test_ai_onboarding.py` shows the right test neighborhood. |
| `backend/ciso_assistant/settings.py` | `REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["ai_case_intake"]` | Add throttle scope later. | Existing throttle configuration already lives here. |

### Serializer for input validation

Recommended component:

- file: `backend/ai_onboarding/case_intake_serializers.py`
- class: `AiCaseIntakeInputSerializer`

Suggested nested serializer:

- class: `AssessmentPeriodInputSerializer`

Responsibility:

- validate `scenario_text`, `preferred_framework`, `assessment_period`, `organization_hint`, `scope_hint`, `known_deadline`, `known_trigger`, `user_locale`, `strict_mode`
- normalize empty strings to `null` where appropriate
- reject oversize input early

### Output validator for AI draft JSON

Recommended component:

- file: `backend/ai_onboarding/case_intake_serializers.py`
- class: `AiCaseIntakeDraftSerializer`

Responsibility:

- validate the exact top-level structure from `AI_CASE_INTAKE_JSON_CONTRACT.md`
- validate nested draft objects
- ensure required fields such as `confidence`, `rationale`, `required_human_action`, and `source_text_refs` are present where required

### Service class/function responsible for scenario parsing

Recommended component:

- file: `backend/ai_onboarding/case_intake_service.py`
- function: `build_case_intake_draft(request_data: dict, *, base_dir: str) -> dict`

Responsibility:

- normalize input
- derive deterministic hints
- optionally call a future provider abstraction
- merge AI output with rule-based or heuristic safety defaults
- ensure the final result is a valid advisory draft before returning it

### Provider abstraction for future AI model integration

Recommended component:

- file: `backend/ai_onboarding/case_intake_provider.py`
- interface: `CaseIntakeProvider`
- factory: `get_case_intake_provider()`

Responsibility:

- receive a canonical prompt/input object
- return either structured JSON or a provider error object
- keep vendor-specific transport out of the service layer

Why it belongs there:

- current `ai_onboarding/llm_engine.py` is a low-level adapter with Qwen-oriented behavior
- Step 1 should not hardcode the endpoint to a single provider implementation

### Guardrail validator

Recommended component:

- file: `backend/ai_onboarding/case_intake_guardrails.py`
- function: `validate_case_intake_guardrails(draft: dict, request_data: dict) -> list[str]`

Responsibility:

- reject invented entity types
- reject final compliance decisions
- reject final risk acceptance or closure decisions
- enforce `needs_review` conditions
- enforce `required_human_action` presence
- enforce `source_text_refs` presence on inferred suggestions

### Permission handling

Recommended view behavior:

- `permission_classes = [permissions.IsAuthenticated]`
- optional later feature flag or custom permission gate if product wants rollout control

Why:

- advisory-only endpoint is not model CRUD
- aligns with `FolderViewSet.ai_recommendations()`
- avoids accidental coupling to add/change/delete model permissions

### Logging / audit event recommendation

Recommendation for Step 1:

- allow structured application logging only
- log request metadata such as request id, user id, locale, strict mode, scenario length, and provider mode
- avoid storing the full scenario text or full draft JSON in a database audit model during Step 1
- defer persistent AI audit logging until governance and privacy handling are explicitly approved

### No-database-write enforcement strategy

Use defense-in-depth:

1. keep the endpoint outside write serializers and model viewsets
2. keep the service layer free of model `save()`, `create()`, `update()`, and `delete()` calls
3. explicitly ban calls to known write-oriented APIs and services
4. execute the request handler inside an atomic transaction and mark it for rollback before returning as an extra safety net
5. test that object counts and SQL write operations remain unchanged

## 5. No-Database-Write Enforcement

The Step 1 implementation must guarantee that no GRC records are created or updated.

### Which functions must be read-only

The following Step 1 functions should be read-only by design:

- `AiCaseIntakeView.post()`
- `AiCaseIntakeInputSerializer.validate()`
- `build_case_intake_draft()`
- any provider adapter used by Step 1
- any output validator or guardrail validator

These functions may:

- parse input
- inspect configuration
- optionally perform read-only lookups if explicitly approved in the design
- return draft JSON

They may not:

- call model `.save()`
- call model `.create()`
- call `.delete()`
- call write serializers `.save()`
- call write-oriented helper flows such as quick-start or library load

### Which existing APIs must not be called by Step 1

The Step 1 implementation must not call or reuse the following write paths:

- `QuickStartSerializer.create()` in `backend/core/serializers.py`
- `QuickStartView.post()` in `backend/core/views.py`
- `StoredLibraryViewSet.import_library()` in `backend/library/views.py`
- `StoredLibrary.load()` when triggered as a write action
- `FolderWriteSerializer.save()`
- `PerimeterWriteSerializer.save()`
- `ComplianceAssessmentWriteSerializer.save()`
- `RiskAssessmentWriteSerializer.save()`
- `EvidenceWriteSerializer.save()`
- `EvidenceRevisionWriteSerializer.save()`
- any `perform_create()` or `perform_update()` method on the core write viewsets

### How to test that no records were created

Future tests should:

1. capture counts before and after calling the endpoint for at least:
   - `Folder`
   - `Perimeter`
   - `ComplianceAssessment`
   - `RequirementAssessment`
   - `Asset`
   - `AppliedControl`
   - `Vulnerability`
   - `RiskAssessment`
   - `RiskScenario`
   - `Evidence`
   - `EvidenceRevision`
   - `FindingsAssessment`
   - `Finding`
   - `RiskAcceptance`
2. assert all counts are unchanged
3. optionally capture SQL and assert no `INSERT`, `UPDATE`, or `DELETE` statements occurred
4. monkeypatch known write functions like `QuickStartSerializer.create()` and `StoredLibrary.load()` to fail if called

### Whether logging AI requests is allowed or should be deferred

Recommendation:

- application logging is allowed
- persistent model-based logging should be deferred

Allowed in Step 1:

- structured log events with request id, user id, scenario length, timing, provider mode, validation outcome

Deferred from Step 1:

- storing full prompt/request/response pairs in a database model
- creating workflow or audit objects to represent AI usage

## 6. Validation and Guardrails

The future implementation should validate both the request and the response draft.

### Required input fields

- `scenario_text` is required
- all other fields are optional but must validate if supplied

### Maximum scenario length

Recommended initial maximum:

- `scenario_text` max length: `20,000` characters

Reasoning:

- large enough for realistic intake
- small enough to protect latency, cost, and abuse risk

### Locale handling

- default `user_locale` to `en`
- accept values matching `^[a-z]{2}(-[A-Z]{2})?$`
- unsupported locales should fall back to `en` and emit a warning rather than fail hard

### Strict mode behavior

- when `strict_mode=true`, low-confidence or ambiguous data should become:
  - blocking questions, or
  - draft objects with `needs_review=true`, or
  - both
- when `strict_mode=false`, the service may return more inferred drafts, but must still remain advisory-only

### Allowed `draft_type`

- only `AiCaseIntakeDraft` is valid for Step 1

### Required `schema_version`

- initial recommended fixed value: `0.2.0`
- reject unknown or missing schema versions if the response validator is version-locked

### Confidence range

- every `confidence` field must be between `0.0` and `1.0`
- `overall_confidence` must also be between `0.0` and `1.0`

### Required `source_text_refs`

- every inferred draft object must include one or more `source_text_refs`
- each source reference should include:
  - `ref_id`
  - `excerpt`
  - `char_start`
  - `char_end`

### Required `rationale`

- every inferred draft object must include non-empty `rationale`

### Required `required_human_action`

Step 1 should strengthen the Step 0.2 contract by requiring `required_human_action` on every inferred suggestion object.

Recommended shape:

- `required_human_action: string`

Examples:

- `"Confirm whether to reuse an existing Folder or create a new domain"`
- `"Confirm the final framework after StoredLibrary and Framework lookups"`

### `needs_review` behavior

`needs_review` must be `true` when:

- confidence is below `0.85`
- a lookup is still required
- scoring or severity is inferred
- an entity mapping is ambiguous
- the suggestion affects creation order or future write behavior

### Blocking questions behavior

- `blocking_questions` must be used when missing answers would make later create steps unsafe or incorrect
- every blocking question must include:
  - `question_id`
  - `question_text`
  - `reason`
  - `affected_fields`
  - `severity: "blocking"`

### Canonical platform entity restrictions

`platform_entity` values must be restricted to canonical internal names, including:

- `Folder`
- `Perimeter`
- `ComplianceAssessment`
- `RequirementNode`
- `RequirementAssessment`
- `Asset`
- `AppliedControl`
- `Vulnerability`
- `Threat`
- `RiskAssessment`
- `RiskScenario`
- `Evidence`
- `EvidenceRevision`
- `Finding`
- `FindingsAssessment`
- `RiskAcceptance`
- `ValidationFlow`

`WorkflowCase` must remain optional until serializer verification is complete.

### No final compliance result rule

- Step 1 must not emit final requirement-assessment results or final audit compliance conclusions
- it may emit `AiRequirementFocusDraft`, but not committed `RequirementAssessment` decisions

### No risk acceptance rule

- Step 1 must not emit final `RiskAcceptance` decisions or approval-ready acceptance outcomes

### No audit closure rule

- Step 1 must not emit closure decisions for audits, findings, validation flows, or workflow cases

### No invented entity type rule

- the service must reject any response draft that invents a non-canonical entity type
- examples to reject:
  - `DomainRecord`
  - `AuditCase`
  - `RemediationPlan`
  - `ComplianceGapCase`

## 7. AI Service Design

Do not implement prompts or external AI integration yet. Define the service boundary only.

### Suggested service interface

Recommended boundary:

```python
def build_case_intake_draft(
    request_data: dict,
    *,
    base_dir: str,
    provider: "CaseIntakeProvider | None" = None,
) -> dict:
    ...
```

### Suggested input object

Recommended internal request object:

```python
CaseIntakeRequest = {
    "scenario_text": str,
    "preferred_framework": str | None,
    "assessment_period": dict | None,
    "organization_hint": str | None,
    "scope_hint": str | None,
    "known_deadline": str | None,
    "known_trigger": str | None,
    "user_locale": str,
    "strict_mode": bool,
}
```

### Suggested output object

Recommended internal output object:

```python
CaseIntakeDraftResult = {
    "draft": dict,
    "provider_mode": "rules_only | llm | hybrid",
    "warnings": list,
    "blocking_questions": list,
    "validation_passed": bool,
}
```

### How strict JSON mode should be handled

Recommended flow:

1. validate input serializer
2. build canonical provider payload
3. if provider is enabled, request JSON-only output
4. parse returned JSON strictly
5. run schema validation
6. run guardrail validation
7. return only validated draft JSON

### How malformed AI JSON should be handled

Recommended behavior:

- if malformed JSON is returned by the provider:
  - do not forward raw AI output to the client
  - attempt safe parse extraction once, similar to the defensive logic already present in `backend/ai_onboarding/llm_engine.py`
  - if still invalid:
    - if a safe rules-only fallback can produce a valid draft, return that fallback with warnings
    - otherwise return a `422` or `503` error depending on failure mode

### How confidence should be normalized

Recommended rule:

- provider-native confidence, rule confidence, or heuristic score should be normalized into `0.0..1.0`
- if the provider emits `0..100`, divide by `100`
- if no reliable confidence exists, use conservative defaults and set `needs_review=true`

### How source references should be preserved

Recommended rule:

- every inferred draft object should preserve text traceability from the original scenario
- store `excerpt`, `char_start`, and `char_end` where possible
- if exact offsets cannot be preserved in a fallback path, emit a warning and still include an excerpt-based reference

### How warnings and blocking questions should be returned

- warnings should describe non-fatal uncertainty, unsupported assumptions, or provider degradation
- blocking questions should only be used for unresolved decisions that would make later create flows unsafe
- both should be present in the final response payload, not only in logs

## 8. Model Recommendation

Do not hardcode a provider for Step 1, but the feature should be designed for a model class that can return reliable structured JSON.

### Option A: Strong reasoning LLM with structured JSON output

**Pros**

- best for multi-entity extraction and cross-linking
- handles ambiguous business-language normalization into canonical platform vocabulary
- can produce rationale, confidence, warnings, and blocking questions in one pass

**Cons**

- more expensive than small extraction models
- requires strict output validation and guardrails

### Option B: Smaller extraction model

**Pros**

- cheaper and faster
- potentially good for shallow entity extraction

**Cons**

- weaker at multi-step reasoning across scope, framework choice, control gaps, risk implications, and evidence expectations
- higher likelihood of brittle or incomplete draft structure

### Option C: RAG-based approach

**Pros**

- useful later if framework catalogs, regulatory notes, or internal templates need retrieval support

**Cons**

- not the best first fit for Step 1
- the primary task is structured scenario normalization, not document QA
- adds complexity before the base draft contract is proven

### Option D: Rules-only approach

**Pros**

- deterministic
- easy to test
- good fallback layer

**Cons**

- too brittle for nuanced scenario parsing
- weak at synthesizing linked drafts across assets, controls, vulnerabilities, requirements, and evidence

### Recommended model class for Step 1

Use a **strong reasoning LLM with structured JSON output**, wrapped behind a provider abstraction and backed by deterministic schema validation and rules-only fallback behavior.

Why:

- the feature needs reasoning, not just extraction
- the output is multi-object and interdependent
- canonical vocabulary enforcement needs both semantic understanding and hard validation
- the project already shows early LLM integration patterns in `backend/ai_onboarding/llm_engine.py`, but Step 1 should abstract over that rather than hardcode it

Recommended Step 1 operating mode:

- **hybrid**
  - strong reasoning model for primary draft generation
  - deterministic guardrails and validation
  - rules-only fallback for degraded or unavailable provider paths

## 9. Frontend Review UX Design

### Where the user triggers AI Case Intake

Recommendation:

- add a dedicated review page entry, not a generic create modal
- likely navigation options for later implementation:
  - a new onboarding/AI entry under the overview or presets area
  - a button from a future onboarding landing page
  - optionally a button from the domains/folders area when starting a new GRC intake

Current frontend evidence:

- quick-start currently exists as a route action and modal pattern
- the sidebar contains a commented quick-start navigation item in `frontend/src/lib/components/SideBar/navData.ts`
- generic create modal flows are model-centric and not a good fit for a multi-entity, draft-only review artifact

### What form fields are shown

The Step 1 review form should expose at least:

- `scenario_text`
- `preferred_framework`
- `assessment_period`
- `organization_hint`
- `scope_hint`
- `known_deadline`
- `known_trigger`
- `user_locale`
- `strict_mode`

### How draft results are displayed

Use a dedicated review screen with sections for:

- case summary
- framework resolution
- setup draft
- asset drafts
- applied-control drafts
- vulnerability drafts
- risk drafts
- requirement focus drafts
- evidence expectation drafts
- blocking questions and warnings

### How confidence and `needs_review` are shown

- show a confidence badge on every draft object
- show a visible `Needs review` indicator when `needs_review=true`
- highlight blocking questions at the top of the page

### How users accept/edit/reject suggested objects

Each draft object should allow:

- accept
- edit
- reject

Edits should remain local to the review draft and should not create or update backend GRC objects in Step 1.

### Why object creation should remain out of scope for Step 1

- Step 1 is the contract-validation and human-review stage
- mixing review and creation would blur safety boundaries
- record creation depends on framework lookup, folder reuse decisions, requirement lookup, and explicit reviewer approval

### How this should later connect to Step 2 Case Setup Wizard

Recommended future sequence:

1. Step 1 returns advisory draft JSON
2. reviewer edits and approves draft objects
3. approved draft is passed into a later Step 2 setup wizard
4. Step 2 transforms approved draft data into explicit create payloads and controlled write actions

The Step 1 review screen should therefore store draft state in a way that can later feed Step 2, but it should not itself perform creation.

## 10. Test Plan for Future Implementation

When implementation starts, the following tests should be added.

### Input serializer tests

- required `scenario_text`
- optional-field validation
- `assessment_period` date ordering
- locale normalization
- max scenario length rejection
- strict-mode default behavior

### Output validator tests

- valid full draft payload
- missing top-level keys
- invalid nested object shape
- invalid `platform_entity`
- invalid confidence range
- missing `source_text_refs`
- missing `rationale`
- missing `required_human_action`

### No database write tests

- assert key model counts unchanged before and after endpoint call
- assert no SQL `INSERT`, `UPDATE`, or `DELETE` statements are executed
- monkeypatch known write functions to fail if invoked

### Permission tests

- unauthenticated request returns `401`
- authenticated request succeeds when feature is enabled
- if a future feature flag or custom permission is added, unauthorized users receive `403`

### Strict mode tests

- ambiguous scenario with `strict_mode=true` yields blocking questions or stronger `needs_review`
- same scenario with `strict_mode=false` yields a valid but more permissive draft

### Invalid JSON tests

- malformed provider JSON is rejected or safely converted to fallback draft
- malformed top-level AI output cannot bypass output validation

### Ambiguous scenario tests

- business term ambiguity like `domain`, `audit`, `framework`, `control`, `evidence`, `finding`, `remediation`, and `closure` results in canonical mapping notes and review flags

### Al-Rawasi example golden test

- the `Al-Rawasi Fintech ECC-1:2018` example from `AI_CASE_INTAKE_JSON_CONTRACT.md` should have a locked golden response test for the fallback or fixture provider path

### No final decision tests

- response must not contain final compliance decisions
- response must not contain final risk-acceptance state changes
- response must not contain audit/finding/workflow closure decisions

## 11. Files Expected to Change During Step 1 Implementation

Do not modify these now. These are the files most likely to be created or changed later.

### Backend

- `backend/core/urls.py`
- `backend/core/views.py`
- `backend/ciso_assistant/settings.py`
- `backend/ai_onboarding/case_intake_serializers.py`
- `backend/ai_onboarding/case_intake_service.py`
- `backend/ai_onboarding/case_intake_types.py`
- `backend/ai_onboarding/case_intake_guardrails.py`
- `backend/ai_onboarding/case_intake_provider.py`
- `backend/ai_onboarding/case_intake_fallbacks.py`
- `backend/ai_onboarding/prompt_builder.py` or a new case-intake-specific prompt module later
- `backend/ai_onboarding/llm_engine.py` only if provider abstraction reuse requires small adapter changes
- `backend/app_tests/test_ai_case_intake.py`

### Frontend

- `frontend/src/lib/utils/schemas.ts`
- `frontend/src/lib/utils/types.ts`
- `frontend/src/lib/components/SideBar/navData.ts`
- `frontend/src/routes/(app)/(internal)/ai/case-intake/+page.svelte`
- `frontend/src/routes/(app)/(internal)/ai/case-intake/+page.server.ts`
- `frontend/src/lib/components/AI/CaseIntakeForm.svelte`
- `frontend/src/lib/components/AI/CaseIntakeReview.svelte`
- `frontend/src/lib/components/AI/DraftObjectCard.svelte`
- `frontend/src/lib/components/AI/BlockingQuestionsPanel.svelte`

## 12. Step 1 Design Acceptance Criteria

Step 1 implementation should not begin until all of the following are true:

1. The endpoint location is agreed and remains advisory-only.
2. The team agrees that Step 1 will be implemented as a new endpoint under the AI/onboarding area, not by reusing quick-start write logic.
3. The request payload is locked to the Step 0.2 input contract.
4. The response payload is locked to the Step 0.2 top-level output contract.
5. Canonical internal vocabulary from `AI_CANONICAL_WORKFLOW_DICTIONARY.md` is mandatory for structured output.
6. `WorkflowCase` remains optional until the serializer gap is verified.
7. The `requirements` vs `/api/requirement-nodes/` mismatch is preserved as an explicit implementation constraint unless resolved by direct inspection.
8. The no-database-write strategy is agreed, including tests and defense-in-depth enforcement.
9. The team agrees that no final compliance decision, risk acceptance, or closure outcome may be emitted by Step 1.
10. The provider abstraction boundary is agreed before any external model integration begins.
11. Output validation and guardrail validation responsibilities are clearly separated.
12. Logging policy is agreed so Step 1 does not accidentally persist sensitive AI content in the database.
13. The frontend review experience is agreed as review-first and non-creating.
14. No application code, migrations, dependencies, AI API calls, or final prompts are introduced during this design step.
