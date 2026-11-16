<!-- SICO-CLEAR-REPORT-V2: no nested JSON in primary report -->
<script lang="ts">
    import { enhance, deserialize, applyAction } from '$app/forms';
    import type { ActionData } from './$types';
    import {
        applyFrameworkBatch, validateCheckpoint, scopeKey,
        type ReviewCheckpoint, type ReviewScope
    } from '$lib/utils/sicoFrameworkReviewV3';

    let { form }: { form: ActionData | null } = $props();
    let instruction = $state('');
    let organization = $state('');
    let busy = $state(false);
    let lastAgentRun = $state<Record<string, any> | null>(null);
    let eligibleOptions = $state<Record<string, any> | null>(null);
    let preparedWorkflow = $state<Record<string, any> | null>(null);
    let recordedApproval = $state<Record<string, any> | null>(null);
    let activeEngagement = $state('');
    let generatedAssessment = $state<Record<string, any> | null>(null);
    let generationError = $state('');
    let generatedSixteen = $state<Record<string, any>[]>([]);
    let generatedFor = $state('');
    let sixteenBusy = $state(false);
    let sixteenError = $state('');
    let caseSaveNotice = $state('');
    let controlProgress = $state<Record<string, any> | null>(null);
    let controlBusy = $state(false);
    let controlError = $state('');
    let controlNotice = $state('');
    let lastControlCaseLoaded = '';
    let lifecycleProgress = $state<Record<string, any> | null>(null);
    let lifecycleProposal = $state<Record<string, any> | null>(null);
    let lifecycleApproval = $state<Record<string, any> | null>(null);
    let evidenceContext = $state('');
    let selectedFolder = $state('');
    let selectedPerimeter = $state('__new__');
    let frameworkSearch = $state('NCA ECC');
    let frameworkConfirmation = $state('');
    let organizationConfirmation = $state('');
    let proposedAssessment = $state('Cybersecurity compliance assessment');
    let proposedPerimeter = $state('SICO cybersecurity assessment perimeter');
    let selectedFramework = $state('');
    let selectedRiskMatrix = $state('');
    // Unified Build a GRC case uses full-framework batches; legacy draft handlers remain unused by this page.
    let frameworkBusinessContext = $state('');
    let frameworkBatchSize = $state(2);
    let fullReview = $state<ReviewCheckpoint | null>(null);
    let fullReviewBusy = $state(false);
    let fullReviewAutomatic = $state(false);
    let fullReviewPause = $state(false);
    let fullReviewError = $state('');
    let fullReviewNotice = $state('');
    let fullReviewCandidates = $state<string[]>([]);
    let fullReviewShown = $state(8);
    const fullReviewPercent = $derived(fullReview?.coverage.accessible_total
        ? Math.round(fullReview.coverage.reviewed_through * 10000 / fullReview.coverage.accessible_total) / 100 : 0);
    const visibleFrameworkReviews = $derived(fullReview?.requirement_reviews.slice(0, fullReviewShown) ?? []);

    function currentFrameworkScope(): ReviewScope {
        return {
            organization_name: organization.trim(), framework_name: frameworkSearch.trim(),
            problem: instruction.trim(), business_context: frameworkBusinessContext.trim()
        };
    }

    function changedFrameworkInputs() {
        // A running model request is allowed to finish, but later batches will
        // not silently mix updated inputs with an earlier signed cursor.
        fullReviewPause = true;
        if (fullReview) fullReviewNotice = 'Inputs changed. Restore the original inputs to resume, or explicitly start a new review.';
    }

    async function runFullFrameworkReview(automatic: boolean, restart = false) {
        if (fullReviewBusy) return;
        const scope = currentFrameworkScope();
        if (scope.organization_name.length < 2 || scope.organization_name.length > 150 ||
            scope.framework_name.length < 2 || scope.framework_name.length > 150 ||
            scope.problem.length < 20 || scope.problem.length > 4000 ||
            scope.business_context.length > 1200) {
            fullReviewError = 'Enter the organization, exact framework and assessment objective in the three fields above.';
            return;
        }
        if (restart) {
            fullReview = null;
            fullReviewCandidates = [];
            fullReviewShown = 8;
        } else if (fullReview && scopeKey(fullReview.scope) !== scopeKey(scope)) {
            fullReviewError = 'These inputs differ from the existing checkpoint. Restore them, or click Start new review.';
            return;
        }
        if (fullReview?.coverage.complete) return;
        fullReviewBusy = true;
        fullReviewAutomatic = automatic;
        fullReviewPause = false;
        fullReviewError = '';
        fullReviewNotice = '';
        try {
            do {
                if (fullReviewPause || scopeKey(currentFrameworkScope()) !== scopeKey(scope)) break;
                const result = await sicoPostAction('ai_framework_batch', {
                    organization_name: scope.organization_name,
                    framework_name: scope.framework_name,
                    problem: scope.problem,
                    framework_business_context: scope.business_context,
                    framework_batch_size: String(frameworkBatchSize),
                    framework_cursor: fullReview?.next_cursor ?? ''
                });
                const response = (result.data as Record<string, any>)?.ai_framework_batch;
                const batch = response?.framework_batch;
                if (!batch) throw new Error('No framework review was returned.');
                if (batch.status !== 'partial' && batch.status !== 'complete') {
                    fullReviewCandidates = Array.isArray(batch.candidate_frameworks)
                        ? batch.candidate_frameworks.map(String).slice(0, 8) : [];
                    throw new Error('An exact authorized framework and accessible requirement list could not be found. Check the name and edition.');
                }
                if (scopeKey(currentFrameworkScope()) !== scopeKey(scope)) {
                    throw new Error('Inputs changed during generation. This batch was not appended. Return to the original inputs and retry.');
                }
                fullReview = applyFrameworkBatch(fullReview, scope, batch);
            } while (automatic && !fullReviewPause && !fullReview?.coverage.complete);
            if (fullReview?.coverage.complete) {
                fullReviewNotice = 'All accessible assessable requirements have provisional reviews. Export the checkpoint and arrange evidence-based human verification.';
            } else if (fullReviewPause) {
                fullReviewNotice = 'Paused after the current batch. Export the checkpoint before refreshing the page.';
            } else if (fullReview) {
                fullReviewNotice = 'Batch completed. Continue when ready, or export a checkpoint.';
            }
        } catch (error) {
            fullReviewError = error instanceof Error ? error.message : 'The current Qwen batch failed. Earlier reviews are preserved.';
        } finally {
            fullReviewBusy = false;
            fullReviewAutomatic = false;
        }
    }

    function downloadFullReview() {
        if (!fullReview || fullReviewBusy) return;
        const blob = new Blob([JSON.stringify(fullReview, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `SICO_Activity1_v3_checkpoint_${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
        fullReviewNotice = 'Checkpoint exported to your device. Keep it private: it contains your assessment context and draft responses.';
    }

    async function importFullReview(event: Event) {
        if (fullReviewBusy) return;
        const field = event.currentTarget as HTMLInputElement;
        const file = field.files?.[0];
        if (!file) return;
        try {
            if (file.size > 6 * 1024 * 1024) throw new Error('Checkpoint exceeds the 6 MB import limit.');
            const parsed = validateCheckpoint(JSON.parse(await file.text()));
            // Restore the exact previous inputs before allowing a signed-cursor continuation.
            organization = parsed.scope.organization_name;
            frameworkSearch = parsed.scope.framework_name;
            instruction = parsed.scope.problem;
            frameworkBusinessContext = parsed.scope.business_context;
            fullReview = parsed;
            fullReviewShown = 8;
            fullReviewCandidates = [];
            fullReviewError = '';
            fullReviewNotice = 'Imported an unverified, client-held draft. The backend will re-check the signed cursor, permissions and framework inventory on the next batch.';
        } catch (error) {
            fullReviewError = error instanceof Error ? error.message : 'Checkpoint could not be imported.';
        } finally {
            field.value = '';
        }
    }

    function clearStaleCase() {
        generatedSixteen = [];
        generatedFor = '';
        sixteenError = '';
        caseSaveNotice = '';
        preparedWorkflow = null;
        recordedApproval = null;
        lifecycleProgress = null;
        activeEngagement = '';
    }

    async function sicoPostAction(action: string, data: Record<string, string>) {
        const payload = new FormData();
        for (const [key, value] of Object.entries(data)) payload.set(key, value);
        const res = await fetch(`?/${action}`, {
            method: 'POST', body: payload, headers: { accept: 'application/json' }
        });
        const parsed = deserialize(await res.text());
        if (parsed.type !== 'success') {
            const body = parsed.type === 'failure' ? (parsed.data as Record<string, any>) : null;
            throw new Error(String(body?.framework_batch_error ?? body?.control_error ?? body?.ai_sixteen_error ?? body?.lifecycle_error ?? 'The requested operation could not finish.'));
        }
        return parsed;
    }

    async function loadSavedControlProgress(caseId = '') {
        try {
            const response = await sicoPostAction('requirement_review', {
                action: 'status', engagement_id: caseId || activeEngagement
            });
            const progress = (response.data as Record<string, any>)?.control_review?.progress;
            if (progress?.case_id) {
                controlProgress = progress;
                controlError = '';
            }
        } catch {
            // An unprovisioned or not-yet-saved company has no control records.
            // Do not display a misleading result or ask for manual UUIDs.
        }
    }

    async function generateAndSaveNextControl() {
        if (controlBusy || !controlProgress?.case_id) return;
        controlBusy = true;
        controlError = '';
        controlNotice = '';
        try {
            const response = await sicoPostAction('requirement_review', {
                action: 'generate_and_save', engagement_id: activeEngagement,
                confirm_preliminary_write: 'true'
            });
            const result = (response.data as Record<string, any>)?.control_review;
            if (result?.business_records_written !== true || result?.verified !== true ||
                !result?.progress?.case_id || result?.record?.result !== 'not_assessed') {
                throw new Error('The audit record could not be independently verified as saved.');
            }
            controlProgress = result.progress;
            controlNotice = 'Qwen generated a control-specific review, saved it in the existing audit, and SICO read it back.';
        } catch (error) {
            controlError = error instanceof Error ? error.message : 'Control review could not be saved.';
        } finally {
            controlBusy = false;
        }
    }


    async function startGeneratedCase(event: SubmitEvent) {
        event.preventDefault();
        await generateConnectedThrough(16);
    }

    async function generateConnectedThrough(lastActivity: number) {
        if (sixteenBusy || !organization.trim() || !frameworkSearch.trim() || instruction.trim().length < 20) return;
        sixteenBusy = true;
        sixteenError = '';
        caseSaveNotice = '';
        const submitted = {
            organization_name: organization.trim(), framework_name: frameworkSearch.trim(), problem: instruction.trim()
        };
        const fingerprint = JSON.stringify(submitted);
        if (fingerprint !== generatedFor) {
            generatedSixteen = [];
            generatedFor = fingerprint;
        }
        try {
            // A single click generates sequentially; each validated result is
            // displayed immediately and a retry resumes the first missing item.
            for (let number = generatedSixteen.length + 1; number <= lastActivity; number++) {
                // Prior Qwen work products form the shared, unverified case context.
                // Only bounded earlier-stage text and proposed objects are forwarded.
                const keyStages = new Set([2, 4, 6, 7, 9, 11, 12]);
                const prior = generatedSixteen.filter((item) =>
                    keyStages.has(Number(item.number)) || Number(item.number) >= number - 2
                ).map((item) => ({
                    number: Number(item.number),
                    analysis: String(item.analysis ?? '').slice(0, 180),
                    proposed_work: String(item.proposed_work ?? '').slice(0, 180),
                    case_profile: item.case_profile ?? null,
                    candidate_assets: item.candidate_assets ?? []
                }));
                const response = await sicoPostAction('ai_sixteen_item', {
                    ...submitted, activity_number: String(number),
                    case_context: JSON.stringify(prior)
                });
                const result = (response.data as Record<string, any>)?.ai_sixteen_item;
                if (!result || result.activity_number !== number ||
                    !result.activity || result.activity.number !== number ||
                    typeof result.activity.analysis !== 'string') {
                    throw new Error(`Activity ${number} returned an invalid Qwen result.`);
                }
                generatedSixteen = [...generatedSixteen, result.activity];
            }
        } catch (err) {
            sixteenError = err instanceof Error ? err.message : 'Local Qwen generation stopped unexpectedly.';
        }
        // This phase is GENERATION ONLY by user request. Never try to create,
        // approve or save an audit or tenant after finishing the 16 drafts.
        sixteenBusy = false;
    }
    const latestResponse = $derived(form as Record<string, any> | null);
    $effect(() => {
        if (latestResponse?.sico_run) lastAgentRun = latestResponse;
        if (latestResponse?.workflow_options) eligibleOptions = latestResponse.workflow_options;
        if (latestResponse?.workflow_prepared) {
            generatedAssessment = latestResponse?.generated_assessment ?? null;
            generationError = String(latestResponse?.generation_error ?? '');
            preparedWorkflow = latestResponse.workflow_prepared;
            activeEngagement = String(preparedWorkflow?.engagement_id ?? '');
            if (preparedWorkflow?.lifecycle) lifecycleProgress = preparedWorkflow.lifecycle;
            recordedApproval = null;
        }
        if (latestResponse?.workflow_review) {
            preparedWorkflow = latestResponse.workflow_review;
            recordedApproval = latestResponse.workflow_review.approved ?
                { commit_enabled: latestResponse.workflow_review.commit_enabled } : null;
        }
        if (latestResponse?.workflow_approved) recordedApproval = latestResponse.workflow_approved;
        const newlySavedCase = latestResponse?.workflow_committed?.business_records_written === true
            ? String(preparedWorkflow?.engagement_id ?? activeEngagement) : '';
        if (newlySavedCase && newlySavedCase !== lastControlCaseLoaded) {
            lastControlCaseLoaded = newlySavedCase;
            void loadSavedControlProgress(newlySavedCase);
        }
        if (latestResponse?.workflow_committed?.workflow) {
            activeEngagement = String(preparedWorkflow?.engagement_id ?? activeEngagement);
            if (latestResponse.workflow_committed.lifecycle)
                lifecycleProgress = latestResponse.workflow_committed.lifecycle;
        }
        if (latestResponse?.lifecycle_status) {
            lifecycleProgress = latestResponse.lifecycle_status;
            activeEngagement = String(latestResponse.lifecycle_status.engagement_id ?? activeEngagement);
        }
        if (latestResponse?.lifecycle_next) {
            lifecycleProposal = latestResponse.lifecycle_next;
            lifecycleApproval = null;
            if (lifecycleProposal?.lifecycle) lifecycleProgress = lifecycleProposal.lifecycle;
        }
        if (latestResponse?.lifecycle_stage_approved) lifecycleApproval = latestResponse.lifecycle_stage_approved;
        if (latestResponse?.lifecycle_stage_committed) {
            if (latestResponse.lifecycle_stage_committed.lifecycle)
                lifecycleProgress = latestResponse.lifecycle_stage_committed.lifecycle;
            lifecycleProposal = null;
            lifecycleApproval = null;
        }
    });
    const result = $derived((latestResponse?.sico_run ? latestResponse : lastAgentRun) as Record<string, any> | null);
    const run = $derived(result?.sico_run as Record<string, any> | undefined);
    const plan = $derived(result?.sico_plan as Record<string, any> | undefined);
    const agent = $derived(result?.sico_agent as Record<string, any> | undefined);
    const discovery = $derived(result?.discovery ?? result?.records ?? null);
    const advisory = $derived(result?.draft ?? result?.case_plan ?? result?.case_intake ?? null);
    const providerMode = $derived(String(advisory?.source_summary?.provider_mode ?? 'unknown'));
    const providerFailed = $derived(/fallback|error|failed|unavailable/i.test(providerMode));
    const recordsReady = $derived(run?.discovery === 'completed');
    const intakeReady = $derived(run?.intake === 'completed' && !providerFailed);
    const recordGroups = $derived(summarizeRecordGroups(discovery));
    const advisoryNotes = $derived(intakeReady ? collectPlainNotes(advisory) : []);
    const discoveryFailure = $derived(String(result?.discovery_error ?? '').trim());
    const intakeFailure = $derived(String(result?.intake_error ?? '').trim());
    const needsOrganization = $derived(!organization.trim() && (
        /organization|domain/i.test(discoveryFailure) || !recordsReady
    ));

    const examples = [
        'Assess the cybersecurity compliance of Demo Bank in Saudi Arabia against NCA ECC. Look up permitted records, identify missing information, and propose next steps for human review.',
        'Prepare an ISO 27001:2022 assessment plan. Confirm the scope, discover authorized records, and identify evidence that still needs review.',
        'Investigate our cybersecurity risk exposure, existing safeguards, and the additional information needed for a formal risk assessment.',
        'Assess our readiness for an internal security audit. Report only verified records and identify unanswered questions.'
    ];

    type Group = { label: string; count: number; examples: string[] };
    function isObject(v: unknown): v is Record<string, unknown> {
        return !!v && typeof v === 'object' && !Array.isArray(v);
    }
    function plainText(v: unknown): string {
        if (typeof v !== 'string') return '';
        const s = v.replace(/\s+/g, ' ').trim();
        if (!s || /^[\[{]/.test(s) || s.length > 650 || /\"[a-z_]+\"\s*:/.test(s)) return '';
        return s;
    }
    function itemLabel(v: unknown): string {
        if (!isObject(v)) return '';
        for (const k of ['name', 'title', 'ref_id', 'label']) {
            const name = plainText(v[k]);
            if (name) return name.slice(0, 95);
        }
        return '';
    }
    function summarizeRecordGroups(source: unknown): Group[] {
        const found = new Map<string, Group>();
        const categories: [RegExp, string][] = [
            [/framework|librar/i, 'Frameworks'],
            [/asset/i, 'Assets'],
            [/polic/i, 'Policies'],
            [/applied.control|safeguard|^controls?$/i, 'Controls'],
            [/eviden/i, 'Evidence'],
            [/assessment/i, 'Assessments'],
            [/risk.scenario/i, 'Risk scenarios'],
            [/domain|folders?/i, 'Organizations / folders']
        ];
        function walk(v: unknown, depth: number) {
            if (depth > 4 || !isObject(v)) return;
            for (const [key, child] of Object.entries(v)) {
                const type = categories.find(([re]) => re.test(key))?.[1];
                if (type && Array.isArray(child)) {
                    const labelled = child.map(itemLabel).filter(Boolean);
                    if (child.length || labelled.length) {
                        const group = found.get(type) ?? { label: type, count: 0, examples: [] };
                        group.count += child.length;
                        for (const name of labelled) {
                            if (group.examples.length < 3 && !group.examples.includes(name)) group.examples.push(name);
                        }
                        found.set(type, group);
                    }
                } else if (isObject(child)) {
                    walk(child, depth + 1);
                }
            }
        }
        walk(source, 0);
        return [...found.values()].slice(0, 8);
    }
    function collectPlainNotes(source: unknown): string[] {
        const output: string[] = [];
        const matching = /summary|objective|recommendation|next.step|question|missing|warning|human.review/i;
        function walk(v: unknown, depth: number) {
            if (depth > 3 || output.length >= 5) return;
            if (Array.isArray(v)) {
                for (const child of v.slice(0, 6)) {
                    const text = plainText(child);
                    if (text && !output.includes(text)) output.push(text);
                    else if (isObject(child)) walk(child, depth + 1);
                }
                return;
            }
            if (!isObject(v)) return;
            for (const [key, child] of Object.entries(v)) {
                if (output.length >= 5) return;
                if (!matching.test(key)) continue;
                const text = plainText(child);
                if (text && !output.includes(text)) output.push(text);
                else if (Array.isArray(child) || isObject(child)) walk(child, depth + 1);
            }
        }
        walk(source, 0);
        return output;
    }
</script>

<svelte:head>
    <title>SICO AI Next — Assessment Workspace</title>
    <meta name="description" content="Permission-scoped GRC discovery and reviewable assessment intake." />
</svelte:head>

<div class="workspace">
    <div class="shell">
        <header class="topbar">
            <div class="logo">✦</div>
            <div><strong>SICO AI</strong><small>ASSESSMENT WORKSPACE</small></div>
            <span class="scope-pill">Uses your GRC permissions</span>
        </header>

        <section class="report" aria-label="Build a GRC case" id="start-grc-case">
            <div class="report-head">
                <h2>Build a GRC case</h2>
                <span class="status-pill">One workflow · Your existing SICO GRC library</span>
            </div>
            <p class="report-intro">Tell SICO the organization, exact framework and objective once. It will begin with a full review of every accessible assessable requirement in that framework, then use the same verified context as the remaining GRC activities are integrated. No requirement is invented, and this draft does not write GRC business records.</p>
            <form class="workflow-form" onsubmit={(event) => { event.preventDefault(); void runFullFrameworkReview(false, true); }}>
                <label>1. Organization name
                    <input name="organization_name" bind:value={organization} oninput={() => { clearStaleCase(); changedFrameworkInputs(); }} disabled={fullReviewBusy} placeholder="Existing organization name" required minlength="2" maxlength="150" />
                </label>
                <label>2. Framework
                    <input name="framework_name" bind:value={frameworkSearch} oninput={() => { clearStaleCase(); changedFrameworkInputs(); }} disabled={fullReviewBusy} placeholder="e.g. ISO 27001:2022, NCA ECC, CCC, PDPL" required minlength="2" maxlength="150" />
                    <span class="footnote">SICO checks your permitted framework library and exact edition; it never silently switches frameworks.</span>
                </label>
                <label>3. Assessment objective
                    <textarea name="problem" bind:value={instruction} oninput={() => { clearStaleCase(); changedFrameworkInputs(); }} disabled={fullReviewBusy} rows="5" required minlength="20" maxlength="4000" placeholder="What should SICO assess? What is the organization's business situation or concern?"></textarea>
                </label>
                <label>Additional business context (optional, not verified)
                    <textarea name="framework_business_context" rows="3" bind:value={frameworkBusinessContext} oninput={changedFrameworkInputs} disabled={fullReviewBusy} maxlength="1200" placeholder="Known business activities, assets, systems, locations, data processing and exclusions; SICO will ask for proof."></textarea>
                </label>
                <details class="technical">
                    <summary>Batch size and model settings</summary>
                    <label style="margin-top:12px">Requirements per Qwen batch
                        <select bind:value={frameworkBatchSize} disabled={fullReviewBusy}>
                            <option value={1}>1 — smallest context</option>
                            <option value={2}>2 — recommended for local Qwen</option>
                            <option value={3}>3 — may need retries</option>
                        </select>
                    </label>
                </details>
                {#if !fullReview}
                    <button type="submit" disabled={fullReviewBusy || instruction.trim().length < 20 || !organization.trim() || !frameworkSearch.trim()}>
                        {fullReviewBusy ? 'Starting full framework assessment…' : 'Build GRC case with AI'}
                    </button>
                {/if}
            </form>

            {#if fullReviewBusy && !fullReview}
                <p class="message" role="status">Qwen is analyzing the first authorized requirements in your selected framework. No records are being saved.</p>
            {/if}
            {#if fullReviewError}
                <div class="message error" role="alert">{fullReviewError} Earlier completed batches remain available.</div>
            {/if}
            {#if fullReviewNotice}<p class="message" role="status">{fullReviewNotice}</p>{/if}
            {#if fullReviewCandidates.length}
                <p class="footnote">Possible authorized framework names (confirm the exact edition): {fullReviewCandidates.join(' · ')}</p>
            {/if}

            {#if fullReview}
                <div class="framework-coverage" aria-label="Activity 1 assessment progress">
                    <div class="framework-coverage-title">
                        <div><strong>Activity 1 of 16 · Framework assessment</strong><p class="footnote">{fullReview.matched_framework.name} {fullReview.matched_framework.reference ? `(${fullReview.matched_framework.reference})` : ''}</p></div>
                        <span>{fullReview.coverage.reviewed_through} / {fullReview.coverage.accessible_total} requirements</span>
                    </div>
                    <div class="framework-meter" role="progressbar" aria-label="Accessible requirement analysis progress" aria-valuemin="0" aria-valuemax={fullReview.coverage.accessible_total} aria-valuenow={fullReview.coverage.reviewed_through}>
                        <div class="framework-meter-fill" style={`width: ${fullReviewPercent}%`}></div>
                    </div>
                    <p class="footnote">{fullReview.coverage.remaining} remaining · {fullReviewPercent}% analyzed · {fullReview.framework_edition_status.replaceAll('_', ' ')} · All conclusions provisional.</p>
                </div>
                <div class="framework-actions">
                    {#if !fullReview.coverage.complete}
                        <button type="button" onclick={() => runFullFrameworkReview(false)} disabled={fullReviewBusy}>Analyze next batch</button>
                        <button type="button" onclick={() => runFullFrameworkReview(true)} disabled={fullReviewBusy}>Continue automatically</button>
                    {/if}
                    {#if fullReviewBusy && fullReviewAutomatic}
                        <button type="button" onclick={() => { fullReviewPause = true; }} disabled={fullReviewPause}>{fullReviewPause ? 'Pausing…' : 'Pause after current batch'}</button>
                    {/if}
                    <button type="button" onclick={downloadFullReview} disabled={fullReviewBusy}>Download checkpoint and draft</button>
                    <button type="button" onclick={() => { fullReviewPause = true; fullReview = null; fullReviewCandidates = []; fullReviewError = ''; fullReviewNotice = 'Review cleared from this tab; use your downloaded checkpoint to resume.'; }} disabled={fullReviewBusy}>Start new case review</button>
                </div>
                <div class="stage-grid" aria-label="Provisional requirement findings">
                    {#each visibleFrameworkReviews as req (req.requirement_id)}
                        <article class="report-card">
                            <h3>{req.reference || 'Reference not listed'} — {req.requirement_name || 'Title unavailable in library'}</h3>
                            <p><strong>Provisional applicability:</strong> {req.applicability.replaceAll('_', ' ')}</p>
                            <p><strong>Reasoning:</strong> {req.rationale}</p>
                            <p><strong>Evidence to request:</strong> {req.evidence_to_request}</p>
                            <p><strong>Question for organization:</strong> {req.question_to_resolve}</p>
                            {#if req.source_text_excerpt_truncated}<p class="finding-alert">Source text shortened for Qwen; verify it against the original requirement.</p>{/if}
                            <p class="footnote">Authorized SICO requirement ID: {req.requirement_id} · AI draft, not a verified compliance finding</p>
                        </article>
                    {/each}
                </div>
                {#if fullReview.requirement_reviews.length > fullReviewShown}
                    <button type="button" class="review-more" onclick={() => { fullReviewShown += 20; }}>Show more requirement reviews ({fullReview.requirement_reviews.length - fullReviewShown} hidden)</button>
                {/if}
                {#if fullReview.coverage.complete}
                    <p class="message" role="status">Activity 1 has provisional reviews for every accessible assessable requirement. Evidence, organizational facts, regulatory edition and human decisions still need verification. Activities 2–16 are not yet connected to this unified workflow; no GRC case has been saved.</p>
                {/if}
            {/if}
            <details class="technical">
                <summary>Resume a downloaded assessment checkpoint</summary>
                <p class="footnote">The draft stays in this browser tab, not SICO's database. Download a checkpoint before refreshing. A signed continuation cursor expires after seven days and becomes invalid if access or the framework catalog changes.</p>
                <label class="checkpoint-label">Select your private checkpoint JSON file
                    <input type="file" accept=".json,application/json" onchange={importFullReview} disabled={fullReviewBusy} />
                </label>
            </details>
            <p class="footnote">SICO uses existing authorized framework records for this provisional analysis. Nothing is automatically approved or recorded as compliant.</p>
        </section>
        <footer>SICO AI · One Build a GRC case workflow · Permission-scoped, provisional and read-only. Future GRC stages will reuse the same selected framework and case context after separate validation.</footer>
    </div>
</div>

<style>
    .workspace{min-height:100vh;background:radial-gradient(ellipse at 60% 0%,#123950 0,transparent 46%),#080f20;color:#e9f4ff;font-family:inherit}
    .shell{max-width:1060px;margin:auto;padding:34px 28px 65px}
    .topbar{display:flex;gap:12px;align-items:center}.logo{display:grid;place-items:center;width:42px;height:42px;border:1px solid #438c8c;border-radius:12px;background:#12404a;font-size:25px;color:#78e2ce}.topbar strong{display:block;font-size:17px;letter-spacing:.08em}.topbar small{font-size:10px;letter-spacing:.14em;color:#a2b7cb}.scope-pill,.status-pill{margin-left:auto;font-size:12px;color:#a3eadc;border:1px solid #37636a;border-radius:30px;padding:8px 12px}
    .hero{margin:65px auto 32px;max-width:760px;text-align:center}.eyebrow{font-size:11px;letter-spacing:.16em;color:#72d9c4;font-weight:800}.hero h1{font-size:clamp(32px,5vw,56px);letter-spacing:-.04em;line-height:1.13;margin:14px 0}.hero em{font-style:normal;color:#71e0cb}.hero>p:last-child{color:#adbed1;line-height:1.75}
    .prompt-form{background:#121f34;border:1px solid #355166;border-radius:18px;padding:16px;box-shadow:0 20px 60px #0005}.prompt-form textarea{width:100%;box-sizing:border-box;border:0;resize:vertical;background:transparent;color:#edf6ff;padding:14px;font:inherit;font-size:15px;line-height:1.7;min-height:145px;outline:none}.prompt-form textarea::placeholder{color:#8ea4bd}.context-row{border-top:1px solid #314359;padding:14px 12px 10px}.context-row label{display:block;color:#cde0eb;font-size:13px;font-weight:700;margin-bottom:8px}.context-row input{background:#0e192b;color:#f4f8ff;border:1px solid #426176;border-radius:9px;padding:11px 12px;width:100%;box-sizing:border-box;font:inherit;font-size:14px}.help{display:block;color:#90a9c2;font-size:12px;margin-top:7px}.prompt-footer{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:13px 10px 3px;color:#9db4c8;font-size:12px}.prompt-footer button{background:#73e2c9;border:0;border-radius:10px;color:#092a31;font:inherit;font-weight:750;font-size:14px;padding:13px 22px;cursor:pointer}.prompt-footer button:disabled{opacity:.5;cursor:not-allowed}
    .examples{margin-top:42px}.examples h2{font-size:15px;color:#aabdd0;font-weight:500}.example-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.example-grid button{cursor:pointer;color:#dbe9f6;text-align:left;background:#14243b;border:1px solid #354b65;border-radius:13px;padding:17px;font:inherit;font-size:13px;line-height:1.55}.example-grid button span{color:#7de4d0;margin-left:8px}.example-grid button:hover{border-color:#67c8b8}
    .message{margin-top:25px;padding:17px;border-radius:12px;border:1px solid #3d6572;color:#cfe6ed;background:#183643}.message.error{border-color:#975c58;background:#3a2226}.message p{margin-bottom:0}.report{margin-top:50px}.report-head{display:flex;justify-content:space-between;align-items:center;gap:18px}.report-head h2{font-size:29px;margin:8px 0}.report-intro{color:#b1c1d3;line-height:1.7;margin:18px 0}.status-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:23px 0}.status-item,.report-card{border:1px solid #33485f;background:#132137;border-radius:13px;padding:19px}.status-item span{display:block;font-size:12px;color:#9eb4c9;margin-bottom:9px}.status-item strong{font-size:15px}.finding-alert{border:1px solid #b58e44;background:#342c1b;color:#f3deaf;border-radius:13px;padding:19px 21px;margin:22px 0}.finding-alert h3{margin:0 0 10px;font-size:17px}.finding-alert p{font-size:14px;line-height:1.6}.finding-alert p:last-child{margin-bottom:0}.finding-alert code{overflow-wrap:anywhere;font-size:12px}
    .report-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.report-card{min-width:0;padding:22px}.report-card h3{font-size:18px;margin:0 0 15px;color:#e9f6f8}.report-card p,.report-card li{font-size:14px;line-height:1.7;color:#bfd1e4;overflow-wrap:anywhere}.report-card strong{color:#edf7ff}.records,.notes{padding-left:20px;margin:0}.records li,.notes li{margin-bottom:11px}.footnote{color:#91aabc!important;font-size:12px!important}.technical{margin-top:22px;border:1px solid #31495c;border-radius:12px;padding:15px;color:#a7bdd1}.technical summary{cursor:pointer}.technical p{font-size:12px}.technical pre{font-size:11px;max-height:340px;white-space:pre-wrap;overflow-wrap:anywhere;overflow:auto;background:#081221;padding:14px;border-radius:8px}footer{border-top:1px solid #304354;color:#839ab1;font-size:12px;margin-top:55px;padding-top:23px}.sr-only{position:absolute;width:1px;height:1px;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap}
    @media(max-width:800px){.shell{padding:23px 16px 50px}.scope-pill{display:none}.hero{margin:50px auto 25px}.example-grid,.report-grid,.status-grid{grid-template-columns:1fr}.report-head{flex-direction:column;align-items:flex-start}.prompt-footer{flex-direction:column;align-items:stretch}.prompt-footer button{width:100%}}
.workflow-form{margin-top:14px;padding:15px;border:1px solid #314b61;border-radius:12px;display:grid;gap:12px;background:#111e30}.workflow-form h3{margin:0;font-size:15px}.workflow-form label{display:grid;gap:6px;font-size:13px;color:#d2e6ef}.workflow-form input:not([type="checkbox"]),.workflow-form textarea,.workflow-form select{min-width:0;width:100%;box-sizing:border-box;padding:10px;background:#0e192b;color:#eef6ff;border:1px solid #46637a;border-radius:8px;font:inherit}.workflow-form button{justify-self:start;border:0;border-radius:9px;padding:11px 16px;font:inherit;font-weight:700;background:#73e2c9;color:#082630;cursor:pointer}.workflow-form button:disabled{opacity:.45;cursor:not-allowed}.workflow-form .confirmation{display:flex;align-items:center;gap:9px}
    .framework-actions { display:flex; flex-wrap:wrap; gap:10px; align-items:center; margin:12px 0; }
    .framework-actions button { flex:0 1 auto; }
    .framework-coverage { margin:20px 0 16px; padding:16px; border:1px solid rgba(134,185,174,.25); border-radius:12px; }
    .framework-coverage-title { display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap; margin-bottom:12px; }
    .framework-meter { height:12px; border-radius:99px; background:rgba(150,170,185,.23); overflow:hidden; }
    .framework-meter-fill { height:100%; background:#61d8bc; border-radius:99px; transition:width .25s ease; }
    .review-more{margin-top:14px;border:1px solid #46637a;background:#172d42;color:#e6f3fd;padding:12px 16px;border-radius:9px;cursor:pointer}
    .checkpoint-label{display:grid;gap:10px;font-size:13px;margin-top:14px}
    .checkpoint-label input{color:#d0e7ed}
    #start-grc-case{margin-top:55px}
</style>
