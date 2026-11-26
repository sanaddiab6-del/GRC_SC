# SICO AI Next pipeline map

[RAN-REAL] Static source trace of the **Build a GRC case** section. The form submits organization, framework and assessment objective to `generateNewCaseDrafts(true)`. The handler loads the authorized source and coverage plan, then selects a ready task. `sicoPostAction` submits named page actions by POST. (frontend/src/routes/(app)/(internal)/sico-ai-next/+page.svelte:1053–1067, :347–378, :765–776)

[NOT-RUN] No application execution, model calls, tests, Docker or build. The trace describes the checked-out source. Where source or runtime evidence is missing, the result is **UNKNOWN**.

## A. Where the 16 activities are defined

[RAN-REAL] `DRAFT_ACTIVITIES` defines the ordered registry, including code, display name, target model, writer stage, dependencies and guidance. The quality endpoint indexes it by activity number in `SicoQualityDraftOneView`, method `post`. `CONTRACTS` supplies the quality-generation fields and asserts the same order. (backend/ai_onboarding/sico_ai_case_draft_views.py:26–59; backend/ai_onboarding/sico_ai_case_quality_views.py:84–88, :110–111; backend/ai_onboarding/quality_sico_drafts_v5.py:23–41)

[RAN-REAL] Registry order (backend/ai_onboarding/sico_ai_case_draft_views.py:27–57):

| Activity | Code | Definition |
| --- | --- | --- |
| 1 | `framework_scope` | backend/ai_onboarding/sico_ai_case_draft_views.py:27 |
| 2 | `business_scope` | backend/ai_onboarding/sico_ai_case_draft_views.py:29 |
| 3 | `compliance_assessment` | backend/ai_onboarding/sico_ai_case_draft_views.py:31 |
| 4 | `assets` | backend/ai_onboarding/sico_ai_case_draft_views.py:33 |
| 5 | `threats` | backend/ai_onboarding/sico_ai_case_draft_views.py:35 |
| 6 | `risk_scenarios` | backend/ai_onboarding/sico_ai_case_draft_views.py:37 |
| 7 | `applied_controls` | backend/ai_onboarding/sico_ai_case_draft_views.py:39 |
| 8 | `policies` | backend/ai_onboarding/sico_ai_case_draft_views.py:41 |
| 9 | `evidence_requests` | backend/ai_onboarding/sico_ai_case_draft_views.py:43 |
| 10 | `requirement_reviews` | backend/ai_onboarding/sico_ai_case_draft_views.py:45 |
| 11 | `audit_findings` | backend/ai_onboarding/sico_ai_case_draft_views.py:47 |
| 12 | `remediation` | backend/ai_onboarding/sico_ai_case_draft_views.py:49 |
| 13 | `control_effectiveness` | backend/ai_onboarding/sico_ai_case_draft_views.py:51 |
| 14 | `human_review` | backend/ai_onboarding/sico_ai_case_draft_views.py:53 |
| 15 | `residual_risk` | backend/ai_onboarding/sico_ai_case_draft_views.py:55 |
| 16 | `reports` | backend/ai_onboarding/sico_ai_case_draft_views.py:57 |

## B. Source retrieval and task planning

1. [RAN-REAL] `loadSicoAuthorizedFrameworkSource` pages through `framework_source_page`. The action forwards to `AuthorizedFrameworkSourcePageView`, method `post`, which calls `read_authorized_source_page`. The browser checks the framework ID, source digest and final row count across the pages. (frontend/src/routes/(app)/(internal)/sico-ai-next/+page.svelte:128–177; frontend/src/routes/(app)/(internal)/sico-ai-next/+page.server.ts:24–36; backend/ai_onboarding/urls.py:313–315; backend/ai_onboarding/authorized_framework_source.py:29–39, :52–82, :86–100)
2. [RAN-REAL] `_load_authorized_requirements` requires one readable match from `_framework_candidates` and queries assessable `RequirementNode` rows filtered by `RoleAssignment.get_accessible_object_ids`. The matcher tries an exact name or reference and has an NCA ECC alias fallback. `_page_and_digest` hashes the whole authorized stream and returns the requested slice and count. (backend/ai_onboarding/sico_ai_framework_batch_v3.py:101–117, :155–187; backend/ai_onboarding/sico_ai_lifecycle_views.py:129–142)
3. [RAN-REAL] `loadSicoCoveragePlan` posts `case_coverage_plan` with the inputs and source digest. `SicoCaseCoveragePlanView`, method `post`, rereads the authorized rows, checks digest and count, and calls `make_coverage_plan`. The organization name serves as a planning label here. (frontend/src/routes/(app)/(internal)/sico-ai-next/+page.svelte:87–113; frontend/src/routes/(app)/(internal)/sico-ai-next/+page.server.ts:51–80; backend/ai_onboarding/urls.py:325–328; backend/ai_onboarding/sico_case_coverage_views.py:23–71)
4. [RAN-REAL] `make_coverage_plan` includes the output of `plan_generation_queue`. The planner groups source requirements by topic, uses `explicit_scope_subjects` when present, and assigns source focus, references, dependencies and task identities. It starts with one slot each for activities 1–3 and adds activity-specific slots for 4–16. `validateGenerationQueue` checks unique references, valid source mappings and earlier-activity dependencies in the browser. (backend/ai_onboarding/sico_case_coverage.py:159–161, :197, :211–264, :284–348; frontend/src/lib/utils/sicoGenerationPlan.ts:10–26)

## C. One task to one provider call per attempt

1. [RAN-REAL] `nextQualitySlot` calls `nextGenerationSlot`. The loop in `generateNewCaseDrafts` gets prior and parent draft context through `plannedDraftContext` and awaits one `quality_draft_one` action with the activity number, draft index, source digest, focus and prior drafts. (frontend/src/routes/(app)/(internal)/sico-ai-next/+page.svelte:337–347, :374–397; frontend/src/lib/utils/sicoGenerationPlan.ts:28–58)
2. [RAN-REAL] The page action `quality_draft_one` forwards to `SicoQualityDraftOneView`, method `post`. It reloads the source, and for a supplied focus theme it recomputes `plan_generation_queue`, selects the matching activity/index, checks focus identity and checks that the required parents arrived. It calls `generate_quality_draft` with that single slot. (frontend/src/routes/(app)/(internal)/sico-ai-next/+page.server.ts:142, :179–192; backend/ai_onboarding/urls.py:319–321; backend/ai_onboarding/sico_ai_case_quality_views.py:88–111, :131–178)
3. [RAN-REAL] `_generate_quality_draft_once` calls `generate_structured` once for one draft per attempt. Exact excerpt (backend/ai_onboarding/quality_sico_drafts_v5.py:518–522):

~~~python
    output = selection.provider.generate_structured(
        capability=CAPABILITY_GRC_CAPABILITY_SELECTION,
        model=selection.config.model,
        system_prompt=(
            'Generate ONE new, specific, hypothetical UNSAVED GRC draft for the existing SICO '
~~~

4. [RAN-REAL] `get_advisory_provider_selection` returns `LocalAiProvider` for a configured local Ollama selection. Its `generate_structured` posts to `/api/generate`, parses a single JSON object and checks its schema. Input or configuration checks can stop the path before a provider call. The model is read from the configuration. Its live value is **UNKNOWN**. (backend/ai_onboarding/llm_provider.py:81–115, :124–143, :155–178, :531–547; backend/ai_onboarding/quality_sico_drafts_v5.py:357–366, :518–522)
5. [RAN-REAL] `_generate_quality_draft_once` calls `validate_draft` and constructs one draft with a slot reference and status `new_unsaved_ai_draft_pending_verification`. `SicoQualityDraftOneView` calls `enrich_quality_draft_result`, attaches source/task metadata and returns the result. The action and loop check the returned identity and safety flags before the page appends it to `qualityDrafts`. (backend/ai_onboarding/quality_sico_drafts_v5.py:582–615; backend/ai_onboarding/sico_ai_case_quality_views.py:229–249; frontend/src/routes/(app)/(internal)/sico-ai-next/+page.server.ts:184–192; frontend/src/routes/(app)/(internal)/sico-ai-next/+page.svelte:398–409)

## D. Retries, the 240-second budget and quality rejections

- [RAN-REAL] `generate_quality_draft` defaults to `max_attempts=2` and `retry_budget_seconds=240`. The endpoint leaves these defaults in place. The wrapper creates a shared monotonic deadline, passes the remaining time to each attempt, and supplies rejection feedback for recoverable failures. The provider call takes the minimum of 240 seconds, the configured timeout and remaining attempt time. The budget is for one backend draft request. One browser action can therefore produce up to two provider calls. (backend/ai_onboarding/sico_ai_case_quality_views.py:164–178; backend/ai_onboarding/quality_sico_drafts_v5.py:537, :654–695)
- [RAN-REAL] `validate_draft` raises `low_information_repetitive_description` when lowercased content has fewer than 19 distinct word tokens. It raises `copied_parent_narrative_not_new_record` when its similarity to a nonempty parent narrative is at least 0.96 after trimming and case folding. Both codes appear in `_RECOVERABLE_SEMANTIC_ERRORS`. (backend/ai_onboarding/quality_sico_drafts_v5.py:218, :260–261, :350–353, :628–643)
- [RAN-REAL] If bounded recovery fails, `generate_quality_draft` raises `QualityGenerationExhausted`. The view returns an error with sanitized failure metadata. The browser logs the rejection, increments the slot's saved attempt counter, checkpoints and breaks the loop. A later Resume is a separate browser request carrying the updated `focus_attempt`; the authorized task remains pinned. (backend/ai_onboarding/quality_sico_drafts_v5.py:618–625, :694–704; backend/ai_onboarding/sico_ai_case_quality_views.py:179–206, :228; frontend/src/routes/(app)/(internal)/sico-ai-next/+page.svelte:381–397, :410–423)

## E. Checkpoint storage and resume

- [RAN-REAL] `checkpointPayload` contains the input scope, source metadata, accepted drafts, generation queue, issues, attempt counters and history. `saveLocalDraftCheckpoint` writes JSON to browser `sessionStorage` under `sico-ai-quality-draft-v7`. The `onMount` callback restores same-tab state. `downloadQualityCheckpoint` saves a downloadable JSON file. (frontend/src/routes/(app)/(internal)/sico-ai-next/+page.svelte:232–284)
- [RAN-REAL] `importQualityCheckpoint` validates the JSON and draft references. The v7 import requires matching three inputs; older imports get `imported_html_review_required` provenance. Import clears the in-memory source and plan. Resume calls `generateNewCaseDrafts(false)`, reloads source/plan as needed, rejects a saved framework ID or digest mismatch, and uses `nextGenerationSlot` to skip accepted drafts and choose the first dependency-ready pending slot. A conflicting saved scope, occupied unvalidated slot or missing validated parent can block resume. (frontend/src/routes/(app)/(internal)/sico-ai-next/+page.svelte:286–341, :359–378, :1070–1079, :1133–1141; frontend/src/lib/utils/sicoGenerationPlan.ts:28–45)
- [RAN-REAL] This draft path returns unsaved objects and checkpoints them on the client. The separate `workflow_resume` action calls `WorkflowResumeView`, method `post`, which returns `workflow_status` for an authorized engagement. The Build resume handler uses `generateNewCaseDrafts(false)`. Server-persisted recovery for these case drafts is **UNKNOWN** beyond the inspected path. (backend/ai_onboarding/quality_sico_drafts_v5.py:594–610; frontend/src/routes/(app)/(internal)/sico-ai-next/+page.server.ts:566–578; backend/ai_onboarding/sico_ai_workflow_views.py:73, :497–506; frontend/src/routes/(app)/(internal)/sico-ai-next/+page.svelte:1136)

## F. Background jobs

[RAN-REAL] **NONE FOUND** in the permitted source for this path. Searches for Huey, Celery, threads/executors, enqueue/dispatch calls and management commands returned no matches. The generation queue is a plan that the browser iterates, awaiting each action; the backend calls the provider in the request. Worker configuration elsewhere is **UNKNOWN**. (backend/ai_onboarding/sico_case_coverage.py:318–335; frontend/src/routes/(app)/(internal)/sico-ai-next/+page.svelte:374–397; backend/ai_onboarding/sico_ai_case_quality_views.py:164–178; backend/ai_onboarding/llm_provider.py:132–143)

## G. Requirement review items and the reported 106

- [RAN-REAL] `make_coverage_plan` loops over the authorized in-scope requirements and builds `requirement_work_items` with one row per requirement. Each starts as `not_assessed`, `to_do`, evidence unverified and human review required. `prepare_requirement_assessments` maps each item to an unsaved `RequirementAssessment`-shaped proposal with no attached compliance assessment. The coverage response also calls `build_full_case_blueprint`, which produces an unassessed requirement assessment entry in its proposal loop. (backend/ai_onboarding/sico_case_coverage.py:71–95, :96–143, :152–158; backend/ai_onboarding/sico_case_record_proposals.py:21–68; backend/ai_onboarding/sico_full_case_blueprint.py:99, :213, :240–253)
- [RAN-REAL] `plan_generation_queue` replaces the initial activity 10 topic candidates with one Qwen review slot per source row, subject to the per-activity queue cap. For a generated review, `enrich_quality_draft_result` requires the chosen requirement to match and leaves the proposed assessment unscored and `not_assessed`. The page displays the planned requirement count separately from `sourceLinkedReviewCount` and evidence-verified decisions. (backend/ai_onboarding/sico_case_coverage.py:265–294, :327–348; backend/ai_onboarding/sico_case_record_proposals.py:95, :128–148; frontend/src/routes/(app)/(internal)/sico-ai-next/+page.svelte:71–84, :1093–1113)
- [RAN-REAL] A literal search for `106` in the permitted source returned no matches. The coverage count is `len(scoped)`. Whether the reported run had 106 readable requirements, 106 accepted review drafts, or another count is **UNKNOWN** from these files. (backend/ai_onboarding/sico_case_coverage.py:132–142; frontend/src/routes/(app)/(internal)/sico-ai-next/+page.svelte:1095–1099)
