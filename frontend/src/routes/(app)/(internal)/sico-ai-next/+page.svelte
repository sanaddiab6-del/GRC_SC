<!-- SICO-CLEAR-REPORT-V2: no nested JSON in primary report -->
<script lang="ts">
    import { enhance } from '$app/forms';
    import type { ActionData } from './$types';

    let { form }: { form: ActionData | null } = $props();
    let instruction = $state('');
    let organization = $state('');
    let busy = $state(false);
    let lastAgentRun = $state<Record<string, any> | null>(null);
    let eligibleOptions = $state<Record<string, any> | null>(null);
    let preparedWorkflow = $state<Record<string, any> | null>(null);
    let recordedApproval = $state<Record<string, any> | null>(null);
    let activeEngagement = $state('');
    let lifecycleProgress = $state<Record<string, any> | null>(null);
    let lifecycleProposal = $state<Record<string, any> | null>(null);
    let lifecycleApproval = $state<Record<string, any> | null>(null);
    let evidenceContext = $state('');
    let selectedFolder = $state('');
    let selectedPerimeter = $state('__new__');
    let frameworkSearch = $state('NCA ECC');
    let proposedAssessment = $state('Cybersecurity compliance assessment');
    let proposedPerimeter = $state('SICO cybersecurity assessment perimeter');
    let selectedFramework = $state('');
    let selectedRiskMatrix = $state('');
    const latestResponse = $derived(form as Record<string, any> | null);
    $effect(() => {
        if (latestResponse?.sico_run) lastAgentRun = latestResponse;
        if (latestResponse?.workflow_options) eligibleOptions = latestResponse.workflow_options;
        if (latestResponse?.workflow_prepared) {
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
        if (latestResponse?.workflow_committed?.workflow) {
            activeEngagement = String(preparedWorkflow?.engagement_id ?? activeEngagement);
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

        <section class="hero">
            <p class="eyebrow">ONE REQUEST · REAL CONTEXT · NO INVENTED FINDINGS</p>
            <h1>What would you like to <em>assess?</em></h1>
            <p>Describe the goal. SICO will look up permitted records and request an advisory intake. It will tell you clearly when it cannot verify something.</p>
        </section>

        <form method="POST" action="?/run" use:enhance={() => {
            busy = true;
            return async ({ update }) => {
                try { await update({ reset: false }); }
                finally { busy = false; }
            };
        }} class="prompt-form">
            <label class="sr-only" for="sico-instruction">Describe your GRC assignment</label>
            <textarea id="sico-instruction" name="scenario_text" bind:value={instruction} rows="5" required minlength="20" maxlength="12000" placeholder="Example: Assess Demo Bank in Saudi Arabia against NCA ECC. Identify the scope, permitted records, missing information, and the next steps for review."></textarea>
            <div class="context-row">
                <div>
                    <label for="sico-organization">Organization (optional)</label>
                    <input id="sico-organization" name="organization_hint" bind:value={organization} placeholder="Optional organization name" autocomplete="off" />
                    <span class="help">Optional for framework lookup. Enter an exact authorized organization name, or use folder focus, to inspect company records.</span>
                </div>
            </div>
            <input type="hidden" name="preferred_framework" value="" />
            <input type="hidden" name="scope_hint" value="" />
            <input type="hidden" name="assessment_period" value="" />
            <input type="hidden" name="known_deadline" value="" />
            <input type="hidden" name="known_trigger" value="" />
            <div class="prompt-footer">
                <span>AI planning and authorized read-only execution</span>
                <button type="submit" disabled={busy || instruction.trim().length < 20}>
                    {#if busy}Preparing…{:else}Run SICO AI ↗{/if}
                </button>
            </div>
        </form>

        {#if !result && !busy}
            <section class="examples">
                <h2>Example assignments</h2>
                <div class="example-grid">
                    {#each examples as example}
                        <button type="button" onclick={() => instruction = example}>{example} <span>↗</span></button>
                    {/each}
                </div>
            </section>
        {/if}

        {#if busy}
            <div class="message" role="status">The local AI is planning and choosing authorized read-only GRC tools. A bounded run may take up to five minutes…</div>
        {/if}
        {#if result?.error}
            <div class="message error" role="alert"><strong>We couldn't complete this request.</strong><p>{String(result.error)}</p></div>
        {/if}

        {#if result?.plan_error}
            <div class="message error" role="alert">Planning: {String(result.plan_error)}</div>
        {/if}
        {#if result?.agent_error}
            <div class="message error" role="alert">Agent execution: {String(result.agent_error)}</div>
        {/if}
        {#if agent}
            <section class="report" aria-live="polite" aria-label="Agent execution">
                <div class="report-head">
                    <div><p class="eyebrow">SICO AI · REAL TOOL EXECUTION</p><h2>Agent execution</h2></div>
                    <span class="status-pill">{String(agent.status)} · Read only</span>
                </div>
                <p class="footnote">Model: {String(agent.model)} · {Number(agent.model_calls)} model decisions requested · No GRC records written</p>
                {#if agent.model_error_code}<p class="finding-alert">Model failure: {String(agent.model_error_code)}</p>{/if}
                <div class="report-grid">
                    {#each (agent.trace ?? []) as step, i}
                        {@const observation = (agent.observations ?? []).find((item: any) => item.id === step.observation_id)}
                        <article class="report-card">
                            <h3>{i + 1}. {String(step.decision?.tool || step.decision?.kind)}</h3>
                            <p>{String(step.decision?.explanation ?? '')}</p>
                            <p class="footnote">{String(step.status ?? 'refused')} {observation ? `· ${observation.id}` : ''}</p>
                            {#if observation?.status === 'succeeded'}
                                <p>{Number(observation.result?.returned_count ?? 0)} authorized record(s) retrieved{observation.result?.limited ? ' · Results limited' : ''}.</p>
                                <ul class="records">
                                    {#each (observation.result?.records ?? []) as record}
                                        <li>
                                            <strong>{String(record.name ?? record.requirement_id ?? record.id)}</strong>
                                            {#if record.reference} · {String(record.reference)}{/if}
                                            {#if record.status} · Status: {String(record.status)}{/if}
                                            {#if record.stored_result} · Stored result: {String(record.stored_result)}{/if}
                                            <small> · Record {String(record.id)}</small>
                                        </li>
                                    {/each}
                                </ul>
                                <p class="footnote">{String(observation.result?.caveat ?? '')}</p>
                            {:else if observation?.error}
                                <p class="finding-alert">{String(observation.error)}</p>
                            {/if}
                            {#if agent.trace[i + 1]}
                                <p class="footnote">Next AI decision: {String(agent.trace[i + 1].decision?.tool || agent.trace[i + 1].decision?.kind)}</p>
                            {/if}
                        </article>
                    {/each}
                </div>
                <article class="report-card" style="margin-top:14px">
                    <h3>Final answer from retrieved records</h3>
                    <p style="white-space:pre-wrap">{String(agent.final_answer || 'The run stopped before a grounded final answer was available. Review the partial results and unresolved work.')}</p>
                    {#if agent.citations?.length}<p class="footnote">Sources: {agent.citations.join(', ')}</p>{/if}
                    <p class="footnote">AI synthesis of the cited stored records; this is not an independent audit or compliance verdict.</p>
                    {#if agent.unresolved?.length}
                        <h3>Unresolved work / authorization needed</h3>
                        <ul class="notes">{#each agent.unresolved as item}<li>{String(item)}</li>{/each}</ul>
                    {/if}
                    <p class="footnote">{String(agent.approval_required)}</p>
                </article>
            </section>
        {/if}

        {#if plan}
            <section class="report" aria-live="polite">
                <div class="report-head">
                    <div>
                        <p class="eyebrow">SICO AI COORDINATOR · LIVE MODEL PLAN</p>
                        <h2>GRC workflow plan</h2>
                    </div>
                    <span class="status-pill">No GRC records changed</span>
                </div>
                <p class="report-intro">{String(plan.summary ?? '')}</p>
                <p class="footnote">Model: {String(plan.model ?? 'unavailable')} · {Array.isArray(plan.steps) ? plan.steps.length : 0} registered stages selected · AI-generated plan, not executed work.</p>
                <div class="report-grid">
                    {#each (Array.isArray(plan.steps) ? plan.steps : []) as step, i}
                        <article class="report-card">
                            <h3>{i + 1}. {String(step.title)}</h3>
                            <p>{String(step.purpose)}</p>
                            <p class="footnote">Stage: {String(step.stage)} · Awaiting human approval and execution integration</p>
                        </article>
                    {/each}
                </div>
                {#if Array.isArray(plan.questions) && plan.questions.length}
                    <article class="report-card" style="margin-top:14px">
                        <h3>Information to confirm</h3>
                        <ul class="notes">{#each plan.questions as question}<li>{String(question)}</li>{/each}</ul>
                    </article>
                {/if}
                {#if Array.isArray(plan.limitations) && plan.limitations.length}
                    <details class="technical">
                        <summary>Current limits and safeguards</summary>
                        <ul class="notes">{#each plan.limitations as note}<li>{String(note)}</li>{/each}</ul>
                    </details>
                {/if}
            </section>
        {/if}

        {#if run && !plan && !agent && !result?.agent_error}
            <section class="report" aria-live="polite">
                <div class="report-head">
                    <div>
                        <p class="eyebrow">ASSESSMENT INTAKE RESULT</p>
                        <h2>{recordsReady && intakeReady ? 'Preparation results' : 'Assessment needs attention'}</h2>
                    </div>
                    <span class="status-pill">No GRC changes saved</span>
                </div>
                <p class="report-intro">This is an advisory intake, not a completed audit or a compliance verdict. Every statement below is limited to what the services actually returned.</p>
                <div class="status-grid">
                    <div class="status-item"><span>GRC record lookup</span><strong>{recordsReady ? 'Completed' : 'Unavailable'}</strong></div>
                    <div class="status-item"><span>AI / intake service</span><strong>{providerFailed ? 'AI fallback — not verified' : intakeReady ? 'Advisory received' : 'Unavailable'}</strong></div>
                    <div class="status-item"><span>Compliance decision</span><strong>Not established</strong></div>
                </div>

                {#if !recordsReady || providerFailed || !intakeReady}
                    <div class="finding-alert" role="alert">
                        <h3>Why you haven't received an assessment</h3>
                        {#if !recordsReady}
                            <p><strong>GRC records could not be verified.</strong> {discoveryFailure || 'The existing record-discovery service did not return a successful result.'}</p>
                        {/if}
                        {#if providerFailed}
                            <p><strong>The AI provider did not produce a reliable response.</strong> The backend reported fallback mode <code>{providerMode}</code>. We are deliberately not presenting that fallback as an AI finding.</p>
                        {:else if !intakeReady}
                            <p><strong>Advisory intake is unavailable.</strong> {intakeFailure || 'The intake service did not return an accepted result.'}</p>
                        {/if}
                        {#if needsOrganization}
                            <p><strong>What you can do:</strong> Enter the exact name of a permitted organization in the field above, then rerun the request.</p>
                        {/if}
                    </div>
                {/if}

                <div class="report-grid">
                    <article class="report-card">
                        <h3>01 · Records we can verify</h3>
                        {#if !recordsReady}
                            <p>No GRC records were verified by this run. This does <strong>not</strong> mean your platform has no records.</p>
                        {:else if recordGroups.length}
                            <ul class="records">
                                {#each recordGroups as group}
                                    <li><strong>{group.label}:</strong> {group.count} record(s) returned{group.examples.length ? ` — ${group.examples.join(', ')}` : ''}</li>
                                {/each}
                            </ul>
                        {:else}
                            <p>The lookup completed, but its response did not contain a clear record list suitable for this summary. We aren't claiming that records were found.</p>
                        {/if}
                    </article>
                    <article class="report-card">
                        <h3>02 · Advisory output</h3>
                        {#if providerFailed}
                            <p>AI-generated assessment findings are unavailable. The provider returned an error fallback.</p>
                        {:else if !intakeReady}
                            <p>The intake service did not produce a usable advisory result.</p>
                        {:else if advisoryNotes.length}
                            <ul class="notes">{#each advisoryNotes as note}<li>{note}</li>{/each}</ul>
                        {:else}
                            <p>An advisory response was received, but it contained no concise supported statements for this report. We won't display technical JSON as findings.</p>
                        {/if}
                    </article>
                    <article class="report-card">
                        <h3>03 · Information still needed</h3>
                        <ul class="notes">
                            {#if !organization.trim()}<li>Identify the organization or assessment domain you are authorized to inspect.</li>{/if}
                            <li>Confirm the relevant regulatory framework, its edition, and the assessment boundary.</li>
                            <li>Identify existing controls and obtain supporting evidence before evaluating implementation.</li>
                            {#if providerFailed}<li>Restore the AI provider connection before requesting model-generated analysis.</li>{/if}
                        </ul>
                        <p class="footnote">These are prerequisites, not verified deficiencies in the organization's cybersecurity.</p>
                    </article>
                    <article class="report-card">
                        <h3>04 · Recommended next action</h3>
                        {#if !recordsReady}
                            <p><strong>First:</strong> Supply an exact permitted organization name and retry record discovery.</p>
                        {:else if providerFailed}
                            <p><strong>First:</strong> Resolve the AI provider fallback. Meanwhile, review the verified records shown alongside this message.</p>
                        {:else}
                            <p><strong>First:</strong> Have an authorized assessor confirm the framework, scope and evidence requirements before any formal assessment or GRC write.</p>
                        {/if}
                        <p class="footnote">No control has been declared compliant, and no risk has been rated or modified.</p>
                    </article>
                </div>
                <details class="technical">
                    <summary>Developer diagnostics (optional)</summary>
                    <p>Backend response for troubleshooting only. Not an assessment report.</p>
                    <pre>{JSON.stringify(result, null, 2)}</pre>
                </details>
            </section>
        {/if}
        <section class="report" aria-label="Real GRC workflow" id="real-grc-workflow">
            <div class="report-head">
                <div><p class="eyebrow">SICO AI · EXISTING GRC SERVICES</p><h2>Prepare and execute a real GRC workflow</h2></div>
                <span class="status-pill">Independent approval required</span>
            </div>
            <p class="report-intro">The current execution adapter can prepare a perimeter, compliance assessment, linked requirement assessments and (with a selected risk matrix) a risk assessment. The other reviewed GRC stages remain pending verified input and separate approvals. This does not declare any compliance result.</p>
            {#if latestResponse?.workflow_error}
                <div class="message error" role="alert">{String(latestResponse.workflow_error)}</div>
            {/if}
            <form method="POST" action="?/workflow_options" use:enhance class="workflow-form">
                <h3>1. Find your authorized organization and framework</h3>
                <label>Organization search
                    <input name="organization_query" bind:value={organization} placeholder="Exact company name" />
                </label>
                <label>Framework search
                    <input name="framework_query" bind:value={frameworkSearch} placeholder="NCA ECC" />
                </label>
                <label>Organization / scope for perimeter lookup
                    <select name="folder_id" bind:value={selectedFolder}>
                        <option value="">Select after loading organizations</option>
                        {#each (eligibleOptions?.organizations ?? []) as org}
                            <option value={String(org.id)}>{String(org.name)}</option>
                        {/each}
                    </select>
                </label>
                <button type="submit">Load verified choices</button>
                <p class="footnote">If you select an organization, click Load verified choices again to retrieve its permitted perimeters and risk matrices. No GRC business records are written.</p>
            </form>
            {#if eligibleOptions}
                <form method="POST" action="?/workflow_prepare" use:enhance class="workflow-form">
                    <h3>2. Prepare exact GRC operations from your instruction</h3>
                    <p class="footnote">Authorized organization, framework and target record IDs are selected here—not invented by the model.</p>
                    <input type="hidden" name="instruction" value={instruction} />
                    <label>Organization
                        <select name="folder_id" bind:value={selectedFolder} required>
                            <option value="">Select a permitted organization</option>
                            {#each (eligibleOptions.organizations ?? []) as item}
                                <option value={String(item.id)}>{String(item.name)}</option>
                            {/each}
                        </select>
                    </label>
                    <label>Actual loaded framework
                        <select name="framework_id" bind:value={selectedFramework} required>
                            <option value="">Select the exact edition/reference</option>
                            {#each (eligibleOptions.frameworks ?? []) as item}
                                <option value={String(item.id)}>{String(item.name)} {item.ref_id ? `(${item.ref_id})` : ''}</option>
                            {/each}
                        </select>
                    </label>
                    <label>Compliance assessment name
                        <input name="assessment_name" bind:value={proposedAssessment} minlength="4" maxlength="200" required />
                    </label>
                    <label>Assessment perimeter
                        <select bind:value={selectedPerimeter}>
                            <option value="__new__">Create a new perimeter (requires permission)</option>
                            {#each (eligibleOptions.perimeters ?? []) as item}
                                <option value={String(item.id)}>Reuse: {String(item.name)}</option>
                            {/each}
                        </select>
                    </label>
                    {#if selectedPerimeter === '__new__'}
                        <label>New perimeter name
                            <input name="new_perimeter_name" bind:value={proposedPerimeter} minlength="4" maxlength="200" required />
                        </label>
                    {:else}
                        <input type="hidden" name="perimeter_id" value={selectedPerimeter}/>
                    {/if}
                    <label>Risk assessment (optional)
                        <select name="risk_matrix_id" bind:value={selectedRiskMatrix}>
                            <option value="">Skip risk assessment for now</option>
                            {#each (eligibleOptions.risk_matrices ?? []) as item}
                                <option value={String(item.id)}>Create using: {String(item.name)}</option>
                            {/each}
                        </select>
                    </label>
                    <button type="submit" disabled={instruction.trim().length < 20}>Prepare real GRC operation — no business writes</button>
                </form>
            {/if}
            {#if preparedWorkflow}
                <article class="report-card" style="margin-top:14px">
                    <h3>3. Review the exact prepared operation</h3>
                    <p class="footnote">Engagement: {String(preparedWorkflow.engagement_id)}</p>
                    <ul class="notes">
                        {#each (preparedWorkflow.planned_actions ?? []) as action}
                            <li>{String(action.platform_entity)} — {String(action.action)}: {String(action.detail)}</li>
                        {/each}
                    </ul>
                    <details class="technical">
                        <summary>View exact scoped IDs and business fields before approving</summary>
                        <pre>{JSON.stringify(preparedWorkflow.review?.operation_payload, null, 2)}</pre>
                        <p>Fingerprint: {String(preparedWorkflow.prepared_digest)}</p>
                    </details>
                    {#if !recordedApproval}
                        <form method="POST" action="?/workflow_approve" use:enhance class="workflow-form">
                            <input type="hidden" name="engagement_id" value={String(preparedWorkflow.engagement_id)} />
                            <input type="hidden" name="prepared_digest" value={String(preparedWorkflow.prepared_digest)} />
                            <label class="confirmation"><input type="checkbox" name="confirm_reviewed" value="yes" required /> I reviewed the target company, framework, perimeter, assessment name and proposed changes.</label>
                            <button type="submit">Record independent human approval</button>
                        </form>
                    {:else if recordedApproval.commit_enabled === true}
                        <form method="POST" action="?/workflow_commit" use:enhance class="workflow-form">
                            <input type="hidden" name="engagement_id" value={String(preparedWorkflow.engagement_id)} />
                            <input type="hidden" name="prepared_digest" value={String(preparedWorkflow.prepared_digest)} />
                            <label class="confirmation"><input type="checkbox" name="confirm_reviewed" value="yes" required /> Final confirmation: save these exact records in the existing GRC modules.</label>
                            <button type="submit">Save approved GRC records</button>
                        </form>
                    {:else}
                        <p class="finding-alert">Human review recorded. Live business writes are still disabled pending isolated PostgreSQL transaction and tenant-isolation verification. No GRC case has been saved.</p>
                    {/if}
                </article>
            {/if}
            {#if latestResponse?.workflow_committed}
                <article class="report-card" style="margin-top:14px">
                    <h3>Verified records saved in existing GRC modules</h3>
                    <ul class="notes">
                        {#each (latestResponse.workflow_committed.created_objects ?? []) as record}
                            <li>{String(record.platform_entity)}: {String(record.name)} — {String(record.id)}</li>
                        {/each}
                    </ul>
                    <p class="footnote">Linked requirement assessments: {Number(latestResponse.workflow_committed.requirement_assessments_count ?? 0)}. Their compliance results and evidence have not been evaluated.</p>
                </article>
            {/if}
            {#if latestResponse?.workflow_resumed || latestResponse?.workflow_committed?.workflow || preparedWorkflow?.workflow}
                {@const execution = latestResponse?.workflow_resumed ?? latestResponse?.workflow_committed?.workflow ?? preparedWorkflow?.workflow}
                <div class="report-grid" style="margin-top:14px">
                    {#each (execution.workflow ?? []) as step}
                        <article class="report-card"><h3>{String(step.stage)}</h3><p>{String(step.status)}</p></article>
                    {/each}
                </div>
            {/if}
            <article class="report-card" style="margin-top:22px" aria-label="Full professional GRC lifecycle">
                <h3>One instruction · Full GRC assessment lifecycle</h3>
                <p class="footnote">You select the existing organization and exact framework above. SICO keeps your original instruction across the assessment, prepares the next reviewed module operation with AI, and pauses for required evidence or human approval. Records save only through authorized existing services.</p>
                <p class="finding-alert"><strong>Important:</strong> A saved module operation is not proof of compliance, control effectiveness or completed audit. Framework selection is never changed automatically.</p>
                {#if latestResponse?.lifecycle_error}
                    <div class="message error" role="alert">{String(latestResponse.lifecycle_error)}</div>
                {/if}
                <form method="POST" action="?/lifecycle_status" use:enhance class="workflow-form">
                    <label>Existing SICO engagement ID (also used to resume after refresh)
                        <input name="engagement_id" bind:value={activeEngagement} placeholder="Engagement UUID" required />
                    </label>
                    <button type="submit">Load saved lifecycle progress</button>
                </form>
                {#if lifecycleProgress?.lifecycle}
                    <p class="footnote">Selected framework ID: {String(lifecycleProgress.framework_id)} · Compliance verdict: {String(lifecycleProgress.compliance_verdict)} · Not yet a completed GRC case</p>
                    <div class="report-grid" style="margin-top:14px">
                        {#each lifecycleProgress.lifecycle as task, i}
                            <article class="report-card">
                                <h3>{i + 1}. {String(task.title)}</h3>
                                <p>{String(task.state).replace(/_/g, ' ')}</p>
                                <p class="footnote">{task.stage ? `Existing service: ${task.stage}` : 'Requires separate verified professional record or review'}</p>
                            </article>
                        {/each}
                    </div>
                    <form method="POST" action="?/lifecycle_next" use:enhance class="workflow-form">
                        <h3>Continue the same assessment with AI</h3>
                        <input type="hidden" name="engagement_id" value={activeEngagement} />
                        <label>Additional verified facts or evidence references (optional)
                            <input name="human_facts" bind:value={evidenceContext} maxlength="1200"
                                placeholder="Only supply information you can verify in the GRC platform" />
                        </label>
                        <button type="submit" disabled={busy}>Prepare next authorized GRC stage with Qwen</button>
                        <p class="footnote">AI cannot approve its own proposal or invent evidence. It may stop to request verified inputs.</p>
                    </form>
                {/if}
                {#if lifecycleProposal}
                    <article class="report-card" style="margin-top:16px">
                        <h3>AI next-stage result: {String(lifecycleProposal.stage ?? lifecycleProposal.status)}</h3>
                        {#if lifecycleProposal.reason}<p class="finding-alert">{String(lifecycleProposal.reason)}</p>{/if}
                        {#if lifecycleProposal.questions?.length}
                            <ul class="notes">{#each lifecycleProposal.questions as q}<li>{String(q)}</li>{/each}</ul>
                        {/if}
                        {#if lifecycleProposal.status === 'prepared_for_human_review' && lifecycleProposal.review?.operation_payload}
                            <p>Prepared using the existing GRC serializer. <strong>No business record has been written.</strong></p>
                            <details class="technical" open>
                                <summary>Review every proposed record, field and exact ID</summary>
                                <pre>{JSON.stringify(lifecycleProposal.review.operation_payload, null, 2)}</pre>
                                <p>SHA-256 fingerprint: {String(lifecycleProposal.prepared_digest)}</p>
                            </details>
                            {#if !lifecycleApproval}
                                <form method="POST" action="?/lifecycle_stage_approve" use:enhance class="workflow-form">
                                    <input type="hidden" name="engagement_id" value={activeEngagement} />
                                    <input type="hidden" name="stage" value={String(lifecycleProposal.stage)} />
                                    <input type="hidden" name="prepared_digest" value={String(lifecycleProposal.prepared_digest)} />
                                    <label class="confirmation"><input type="checkbox" name="confirm_reviewed" value="yes" required /> I have reviewed the exact GRC changes and have authority to approve them.</label>
                                    <button type="submit">Record human approval for this stage</button>
                                </form>
                            {:else if lifecycleApproval.commit_enabled === true}
                                <form method="POST" action="?/lifecycle_stage_commit" use:enhance class="workflow-form">
                                    <input type="hidden" name="engagement_id" value={activeEngagement} />
                                    <input type="hidden" name="stage" value={String(lifecycleProposal.stage)} />
                                    <input type="hidden" name="prepared_digest" value={String(lifecycleProposal.prepared_digest)} />
                                    <label class="confirmation"><input type="checkbox" name="confirm_reviewed" value="yes" required /> Final confirmation: save this exact approved stage in SICO GRC.</label>
                                    <button type="submit">Save stage to existing GRC modules</button>
                                </form>
                            {:else}
                                <p class="finding-alert">Approval recorded, but this writer is not independently enabled for live saves. Further isolated transaction and permission tests are required.</p>
                            {/if}
                        {/if}
                    </article>
                {/if}
                {#if latestResponse?.lifecycle_stage_committed}
                    <p class="message">The existing GRC service reported a committed operation for {String(latestResponse.lifecycle_stage_committed.stage)}. Verify the saved records in the corresponding module before trusting the result.</p>
                {/if}
            </article>
            <form method="POST" action="?/workflow_review" use:enhance class="workflow-form">
                <label>Restore an existing case-setup review by engagement ID
                    <input name="engagement_id" value={String(preparedWorkflow?.engagement_id ?? '')} placeholder="Prepared engagement UUID" />
                </label>
                <button type="submit">Restore pending approval</button>
            </form>
            <form method="POST" action="?/workflow_resume" use:enhance class="workflow-form">
                <label>Resume an existing SICO engagement (ID)
                    <input name="engagement_id" value={String(preparedWorkflow?.engagement_id ?? '')} placeholder="Existing engagement UUID" />
                </label>
                <button type="submit">Show verified workflow progress</button>
            </form>
        </section>
        <footer>SICO AI Next · Read operations execute automatically when authorized · GRC writes require explicit recorded human approval and an enabled, verified writer.</footer>
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
.workflow-form{margin-top:14px;padding:15px;border:1px solid #314b61;border-radius:12px;display:grid;gap:12px;background:#111e30}.workflow-form h3{margin:0;font-size:15px}.workflow-form label{display:grid;gap:6px;font-size:13px;color:#d2e6ef}.workflow-form input:not([type="checkbox"]),.workflow-form select{min-width:0;width:100%;box-sizing:border-box;padding:10px;background:#0e192b;color:#eef6ff;border:1px solid #46637a;border-radius:8px;font:inherit}.workflow-form button{justify-self:start;border:0;border-radius:9px;padding:11px 16px;font:inherit;font-weight:700;background:#73e2c9;color:#082630;cursor:pointer}.workflow-form button:disabled{opacity:.45;cursor:not-allowed}.workflow-form .confirmation{display:flex;align-items:center;gap:9px}
</style>
