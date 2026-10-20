<script lang="ts">
	import type { ActionData } from './$types';

	let { form }: { form: ActionData | null } = $props();
	let showTechnical = $state(false);
	const discovery = $derived((form && 'discovery' in form ? form.discovery : null) as any);
	const casePlan = $derived((form && 'case_plan' in form ? form.case_plan : null) as any);
	const draft = $derived((form && 'draft' in form ? form.draft : null) as any);
	const error = $derived(form && 'error' in form ? form.error : null);
	const provider = $derived(draft?.source_summary?.provider_mode || 'not verified');

	const sections = [
		{
			name: 'Case initiation',
			items: [
				{ title: 'Frameworks & libraries', href: '/frameworks', detail: 'Verify loaded regulatory frameworks' },
				{ title: 'Domains & organization', href: '/folders', detail: 'Use the existing organizational domain' },
				{ title: 'Perimeters & scope', href: '/perimeters', detail: 'Define included systems and boundaries' },
				{ title: 'Compliance assessments', href: '/compliance-assessments', detail: 'Create an assessment after setup approval' }
			]
		},
		{
			name: 'Assets & security posture',
			items: [
				{ title: 'Assets', href: '/assets', detail: 'Inventory in-scope information assets' },
				{ title: 'Applied controls', href: '/applied-controls', detail: 'Existing safeguards and planned controls' },
				{ title: 'Vulnerabilities', href: '/vulnerabilities', detail: 'Document verified weaknesses' },
				{ title: 'Policies', href: '/policies', detail: 'Review governing policies' }
			]
		},
		{
			name: 'Assessment & assurance',
			items: [
				{ title: 'Risk assessments', href: '/risk-assessments', detail: 'Risk matrix and assessment scope' },
				{ title: 'Risk scenarios', href: '/risk-scenarios', detail: 'Threats, controls, inherent/current/residual risk' },
				{ title: 'Evidences', href: '/evidences', detail: 'Actual supporting documents and revisions' },
				{ title: 'Findings & follow-up', href: '/findings-assessments', detail: 'Review findings, remediation and approvals' }
			]
		},
		{
			name: 'Extended GRC capabilities',
			items: [
				{ title: 'Third-party risk', href: '/entity-assessments', detail: 'Supplier and entity assessments' },
				{ title: 'Business impact analysis', href: '/business-impact-analysis', detail: 'Critical services and business impacts' },
				{ title: 'Incidents', href: '/incidents', detail: 'Incident lifecycle and controls' },
				{ title: 'Reports', href: '/reports', detail: 'Audit and executive deliverables' }
			]
		}
	];
</script>

<svelte:head>
	<title>SICO AI Workspace — GRC Consultant</title>
	<meta name="description" content="SICO AI GRC assignment workspace: framework, organization, scope, assessment and full-platform capability navigation." />
</svelte:head>

<div class="mx-auto max-w-7xl space-y-6 p-4 text-surface-950 md:p-8">
	<header class="rounded-2xl bg-slate-900 p-6 text-white shadow-lg md:p-8">
		<div class="mb-3 flex flex-wrap items-center gap-2 text-xs font-semibold tracking-wide text-teal-200">
			<span class="rounded-full border border-teal-400/40 bg-teal-500/20 px-3 py-1">SICO AI WORKSPACE</span>
			<span class="rounded-full border border-white/20 px-3 py-1">Implementation V3 · Case preflight · No writes</span>
		</div>
		<h1 class="text-3xl font-bold md:text-4xl">Your AI GRC Consultant & Analyst</h1>
		<p class="mt-3 max-w-3xl text-sm leading-relaxed text-slate-200">
			Start with a real assignment. SICO will prepare the proposed framework, organizational domain,
			assessment scope and setup for your review. All existing GRC functions remain available below.
		</p>
	</header>

	<section class="grid gap-3 md:grid-cols-4" aria-label="New case preparation sequence">
		{#each [
			{ num: '01', label: 'Framework selection', description: 'Confirm the correct standard' },
			{ num: '02', label: 'Organization / domain', description: 'Reuse or propose a domain' },
			{ num: '03', label: 'Perimeter / scope', description: 'Define assessment boundaries' },
			{ num: '04', label: 'Assessment setup', description: 'Create only after approval' }
		] as step}
			<div class="rounded-xl border border-surface-300 bg-surface-50 p-4 shadow-sm">
				<div class="text-sm font-bold text-teal-700">{step.num}</div>
				<div class="mt-2 font-semibold">{step.label}</div>
				<div class="mt-1 text-xs text-surface-600">{step.description}</div>
			</div>
		{/each}
	</section>

	<div class="grid items-start gap-6 lg:grid-cols-[minmax(0,1.25fr)_minmax(280px,0.75fr)]">
		<section class="rounded-xl border border-surface-300 bg-surface-50 p-5 shadow-sm md:p-6">
			<h2 class="text-xl font-bold">Start a GRC assignment</h2>
			<p class="mt-1 text-sm text-surface-600">This action calls the existing authenticated AI Case Intake service. It does not write any GRC records.</p>

			<form method="POST" action="?/intake" class="mt-5 space-y-4">
				<label class="block space-y-1 text-sm font-semibold">
					<span>Describe the assignment</span>
					<textarea name="scenario_text" rows="5" required minlength="20" maxlength="12000"
						class="textarea w-full" placeholder="Describe the organization, assessment objective, systems, issues and deadline...">Al-Rawasi Fintech is preparing for its Q4 2026 NCA ECC-1:2018 cybersecurity compliance assessment. Assess user access management for the core banking platform. Previous reviews found missing access reviews, no MFA on remote access, and weak privileged access management.</textarea>
				</label>
				<div class="grid gap-4 md:grid-cols-2">
					<label class="block space-y-1 text-sm font-semibold">
						<span>Preferred framework</span>
						<input name="preferred_framework" class="input w-full" value="NCA ECC-1:2018" />
					</label>
					<label class="block space-y-1 text-sm font-semibold">
						<span>Organization</span>
						<input name="organization_hint" class="input w-full" value="Al-Rawasi Fintech" />
					</label>
				</div>
				<label class="block space-y-1 text-sm font-semibold">
					<span>Scope / systems under assessment</span>
					<input name="scope_hint" class="input w-full" value="Core banking platform — user access management" />
				</label>
				<div class="grid gap-4 md:grid-cols-2">
					<label class="block space-y-1 text-sm font-semibold">
						<span>Assessment period</span>
						<input name="assessment_period" class="input w-full" value="Q4 2026" />
					</label>
					<label class="block space-y-1 text-sm font-semibold">
						<span>Known deadline (optional)</span>
						<input name="known_deadline" type="date" class="input w-full" />
					</label>
				</div>
				<label class="block space-y-1 text-sm font-semibold">
					<span>Known trigger (optional)</span>
					<input name="known_trigger" class="input w-full" value="Annual regulatory assessment; previous access review gaps" />
				</label>
				<div class="space-y-2">
					<button type="submit" formaction="?/discover" class="btn preset-filled-primary-500 w-full font-semibold">
						Investigate real GRC records (no AI model required)
					</button>
					<p class="text-xs text-surface-600">Looks up permitted existing frameworks, organizational folders, assets, policies, controls and assessments in the live database. Makes no changes.</p>
					<button type="submit" formaction="?/intake" class="btn preset-tonal-primary w-full font-semibold">
						Generate advisory case intake proposal
					</button>
				</div>
				<p class="text-xs text-surface-600">The model may take a minute on a cold start. This is a draft, not an audit conclusion or compliance determination.</p>
			</form>
		</section>

		<aside class="rounded-xl border border-surface-300 bg-surface-50 p-5 shadow-sm md:p-6">
			<h2 class="text-lg font-bold">Full GRC work programme</h2>
			<p class="mt-2 text-sm text-surface-600">The workspace begins with case foundations. Subsequent specialist work is part of the same overall programme—not limited to a short onboarding wizard.</p>
			<ol class="mt-4 space-y-2 text-sm">
				{#each [
					'Framework, business context and scope',
					'Domain, perimeter and assessment setup',
					'Assets, existing controls and vulnerabilities',
					'Risk scenarios and inherent risk',
					'Existing controls, current and residual risks',
					'Control-by-control evidence assessment',
					'Findings, nonconformities and remediation',
					'Independent review and audit support',
					'Risk treatment, approvals and closure',
					'Third parties, privacy, resilience and reporting'
				] as label, i}
					<li class="flex items-start gap-3"><span class="rounded bg-teal-100 px-2 py-0.5 text-xs font-bold text-teal-900">{i + 1}</span> {label}</li>
				{/each}
			</ol>
			<p class="mt-4 rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900">
				Case intake, real-record investigation and new-case preflight are connected. Record creation, evidence audits, and risk automation are not connected here yet.
			</p>
		</aside>
	</div>

	{#if error}
		<section role="alert" class="rounded-xl border border-red-300 bg-red-50 p-5 text-sm text-red-900">
			<h2 class="font-bold">Case intake could not complete</h2>
			<p class="mt-2">{error}</p>
		</section>
	{/if}

	{#if discovery}
		<section class="space-y-4 rounded-xl border-2 border-teal-500 bg-surface-50 p-5 shadow-sm md:p-6" aria-live="polite">
			<div>
				<h2 class="text-xl font-bold">Live GRC record investigation</h2>
				<p class="mt-1 text-sm text-surface-600">Results are from your actual database, filtered by your account's read permissions. This check used no AI model, did not read documents, and made no changes.</p>
			</div>
			<div class="grid gap-3 md:grid-cols-2">
				<div class="rounded-lg border border-surface-300 bg-surface-100 p-4">
					<h3 class="font-bold">Existing organization / domain</h3>
					<p class="mt-2 text-sm">Status: <strong>{discovery.domain_status}</strong></p>
					{#if discovery.selected_domain}
						<p class="mt-2 text-sm">Selected from platform: <strong>{discovery.selected_domain.name}</strong></p>
					{:else}
						<p class="mt-2 text-sm">No unambiguous exact domain was selected. A new one should not be created until candidates are reviewed.</p>
					{/if}
					{#each discovery.domain_candidates || [] as item}
						<p class="mt-2 text-sm">{item.name} — {item.match} match</p>
					{/each}
				</div>
				<div class="rounded-lg border border-surface-300 bg-surface-100 p-4">
					<h3 class="font-bold">Real framework candidates</h3>
					{#if !discovery.framework_candidates?.length}
						<p class="mt-2 text-sm">No readable candidate was found using this framework hint. That does not prove the framework is absent.</p>
					{:else}
						{#each discovery.framework_candidates as item}
							<div class="mt-2 border-b border-surface-300 pb-2 text-sm">
								<strong>{item.name}</strong> {#if item.reference}({item.reference}){/if}
								<div class="text-xs text-surface-600">Assessable requirements: {item.assessable_requirements} · Exact name match: {item.match === 'exact' ? 'yes' : 'not verified'}</div>
							</div>
						{/each}
					{/if}
				</div>
			</div>
			{#if !discovery.selected_domain && discovery.domain_candidates?.length}
				<div class="rounded-lg border border-amber-300 bg-amber-50 p-4">
					<h3 class="font-bold text-amber-900">Select a matching organizational domain to inspect its records</h3>
					<p class="mt-1 text-sm text-amber-900">Only domains your account can read are listed. Selection is read-only and is not approval to create anything.</p>
					{#each discovery.domain_candidates as item}
						<form method="POST" action="?/discover" class="mt-2 flex items-center justify-between gap-4 rounded border border-amber-200 p-2">
							<input type="hidden" name="organization_hint" value={discovery.organization_requested} />
							<input type="hidden" name="preferred_framework" value={discovery.framework_requested} />
							<input type="hidden" name="selected_folder_id" value={item.id} />
							<span class="text-sm">{item.name} ({item.match})</span>
							<button class="btn preset-tonal-primary" type="submit">Inspect</button>
						</form>
					{/each}
				</div>
			{/if}
			{#if discovery.selected_domain}
				<div>
					<h3 class="font-bold">Records in the selected domain (not child domains)</h3>
					<div class="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
						{#each [
							{label:'Perimeters / scopes',key:'perimeters',href:'/perimeters'},
							{label:'Assets',key:'assets',href:'/assets'},
							{label:'Applied controls',key:'applied_controls',href:'/applied-controls'},
							{label:'Policies',key:'policies',href:'/policies'},
							{label:'Vulnerabilities',key:'vulnerabilities',href:'/vulnerabilities'},
							{label:'Evidences',key:'evidences',href:'/evidences'},
							{label:'Risk assessments',key:'risk_assessments',href:'/risk-assessments'},
							{label:'Compliance assessments',key:'compliance_assessments',href:'/compliance-assessments'}
						] as category}
							<div class="rounded-lg border border-surface-300 bg-surface-100 p-3">
								<div class="flex items-center justify-between gap-3"><strong>{category.label}</strong><a href={category.href} class="text-sm text-teal-700 underline">Open</a></div>
							<p class="mt-1 text-xs text-surface-600">Up to {discovery.records_by_category?.[category.key]?.length || 0} visible matches shown</p>
							{#each discovery.records_by_category?.[category.key] || [] as record}
								<p class="mt-1 text-sm">{record.name}</p>
							{/each}
						</div>
						{/each}
					</div>
				</div>
			{/if}
			{#if discovery.next_checks?.length}
				<div class="rounded-lg border border-surface-300 bg-surface-100 p-4">
					<h3 class="font-bold">Recommended next investigation checks</h3>
					<p class="mt-1 text-xs text-surface-600">These checks come from identified database facts and gaps. They are not AI compliance findings.</p>
					<ul class="mt-2 list-disc space-y-2 pl-5 text-sm">
						{#each discovery.next_checks as check}
							<li><strong>{check.topic}:</strong> {check.message}</li>
						{/each}
					</ul>
				</div>
			{/if}
			{#if discovery.warnings?.length}
				<div class="rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900">
					<strong>Items to review</strong>
					<ul class="mt-2 list-disc pl-5">{#each discovery.warnings as warning}<li>{warning}</li>{/each}</ul>
				</div>
			{/if}
			<p class="text-xs text-surface-600">This is a source-backed starting inventory, not a completed audit. It does not verify evidence or determine compliance. It cannot conclude that records are absent outside the readable, scanned domain.</p>
		</section>
	{/if}

{#if discovery}
    <section class="space-y-4 rounded-xl border border-surface-300 bg-surface-50 p-5 shadow-sm md:p-6" aria-label="Prepare new case from discovered records">
        <div>
            <h2 class="text-xl font-bold">Prepare a new GRC case using real records</h2>
            <p class="mt-1 text-sm text-surface-600">Step 3: choose the exact framework, then tell SICO whether to create a new organizational domain or reuse an existing one. This performs a permission and duplicate preflight, not record creation.</p>
        </div>
        {#if discovery.framework_candidates?.length}
            {#if discovery.new_domain_parent_options?.length}
                <form method="POST" action="?/casePlan" class="space-y-3 rounded-lg border border-surface-300 p-4">
                    <h3 class="font-semibold">Option A — Start a completely new company/domain case</h3>
                    <input type="hidden" name="organization_hint" value={discovery.organization_requested} />
                    <input type="hidden" name="preferred_framework" value={discovery.framework_requested} />
                    <input type="hidden" name="domain_strategy" value="create" />
                    <label class="block space-y-1 text-sm font-semibold"><span>Exact framework from the database</span>
                        <select name="framework_id" class="select w-full" required>
                            <option value="" disabled selected>Choose the correct regulation and edition</option>
                            {#each discovery.framework_candidates as candidate}
                                <option value={candidate.id}>{candidate.name} ({candidate.assessable_requirements} assessable requirements)</option>
                            {/each}
                        </select>
                    </label>
                    <label class="block space-y-1 text-sm font-semibold"><span>Parent organizational folder</span>
                        <select name="parent_folder_id" class="select w-full" required>
                            <option value="" disabled selected>Choose the allowed parent</option>
                            {#each discovery.new_domain_parent_options as parent}
                                <option value={parent.id}>{parent.name}</option>
                            {/each}
                        </select>
                    </label>
                    <label class="block space-y-1 text-sm font-semibold"><span>Assessment scope / system</span>
                        <input name="scope_hint" class="input w-full" required minlength="5" maxlength="500" value={discovery.case_context?.scope || ''} placeholder="e.g. Core banking platform — access management" />
                    </label>
                    <label class="flex items-start gap-2 text-sm"><input type="checkbox" name="framework_review_confirmed" class="checkbox mt-1" />
                        <span>I have reviewed the selected framework's applicability and edition. This is my confirmation, not an AI verification.</span>
                    </label>
                    <button type="submit" class="btn preset-filled-primary-500 w-full">Prepare new-case plan and check blockers (no writes)</button>
                </form>
            {:else}
                <p class="rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900">No permitted top-level parent folder is available for new-domain creation. Ask an administrator to check domain-creation permissions; SICO will not bypass them.</p>
            {/if}
            {#if discovery.domain_candidates?.length}
                <form method="POST" action="?/casePlan" class="space-y-3 rounded-lg border border-surface-300 p-4">
                    <h3 class="font-semibold">Option B — Start a new assessment in an existing organizational domain</h3>
                    <input type="hidden" name="organization_hint" value={discovery.organization_requested} />
                    <input type="hidden" name="preferred_framework" value={discovery.framework_requested} />
                    <input type="hidden" name="domain_strategy" value="reuse" />
                    <label class="block space-y-1 text-sm font-semibold"><span>Exact framework</span>
                        <select name="framework_id" class="select w-full" required>
                            <option value="" disabled selected>Choose a framework</option>
                            {#each discovery.framework_candidates as candidate}
                                <option value={candidate.id}>{candidate.name} ({candidate.assessable_requirements} requirements)</option>
                            {/each}
                        </select>
                    </label>
                    <label class="block space-y-1 text-sm font-semibold"><span>Existing domain to reuse</span>
                        <select name="selected_folder_id" class="select w-full" required>
                            <option value="" disabled selected>Choose the existing domain</option>
                            {#each discovery.domain_candidates as domain}
                                <option value={domain.id}>{domain.name} ({domain.match} match)</option>
                            {/each}
                        </select>
                    </label>
                    <label class="block space-y-1 text-sm font-semibold"><span>Assessment scope / system</span>
                        <input name="scope_hint" class="input w-full" required minlength="5" maxlength="500" value={discovery.case_context?.scope || ''} />
                    </label>
                    <label class="flex items-start gap-2 text-sm"><input type="checkbox" name="framework_review_confirmed" class="checkbox mt-1" />
                        <span>I reviewed the framework applicability and edition.</span>
                    </label>
                    <button type="submit" class="btn preset-tonal-primary w-full">Prepare plan using this domain (no writes)</button>
                </form>
            {/if}
        {:else}
            <p class="text-sm text-surface-600">First resolve a readable framework in the investigation above, then return here.</p>
        {/if}
    </section>
{/if}

{#if casePlan}
    <section class="space-y-4 rounded-xl border-2 border-teal-500 bg-surface-50 p-5 shadow-sm md:p-6" aria-live="polite">
        <h2 class="text-xl font-bold">New GRC case — real preflight results</h2>
        <p class="text-sm">Status: <strong>{casePlan.status === 'blocked' ? 'Blocked: review the issues below' : 'Ready for human review and protected case-setup dry-run'}</strong></p>
        <p class="text-xs text-surface-600">Checked framework: {casePlan.framework?.name}, {casePlan.framework?.assessable_requirements} assessable requirements. Framework edition and regulatory applicability are NOT independently verified.</p>
        <div class="space-y-2">
            {#each casePlan.planned_actions || [] as action, index}
                <div class="flex gap-3 rounded-lg border border-surface-300 bg-surface-100 p-3 text-sm">
                    <strong>{index + 1}.</strong>
                    <span><strong>{action.entity} — {action.operation}:</strong> {action.name}<span class="block text-xs text-surface-600">{action.status}</span></span>
                </div>
            {/each}
        </div>
        {#if casePlan.blocking_checks?.length}
            <div class="rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900">
                <strong>Problems to resolve</strong>
                <ul class="mt-2 list-disc space-y-1 pl-5">{#each casePlan.blocking_checks as blocker}<li>{blocker.message}</li>{/each}</ul>
            </div>
        {/if}
        {#if casePlan.limitations?.length}
            <details class="rounded-lg border border-surface-300 p-4 text-sm">
                <summary class="cursor-pointer font-semibold">What this preflight cannot guarantee</summary>
                <ul class="mt-2 list-disc space-y-1 pl-5">{#each casePlan.limitations as limitation}<li>{limitation}</li>{/each}</ul>
            </details>
        {/if}
        <p class="rounded-lg border border-surface-300 p-4 text-sm">No records were created. After reviewing this plan, a separate existing <strong>Get Started → Local AI Case Onboarding → Step 2 dry-run</strong> must validate the final creation payload. Do not approve or create until the dry-run and permissions pass.</p>
    </section>
{/if}

	{#if draft}
		<section class="space-y-4 rounded-xl border-2 border-teal-500 bg-surface-50 p-5 shadow-sm md:p-6">
			<div class="flex flex-wrap items-center justify-between gap-3">
				<div>
					<h2 class="text-xl font-bold">Your case initiation proposal</h2>
					<p class="text-sm text-surface-600">Review the proposed framework, domain and perimeter. Nothing has been created.</p>
				</div>
				<span class="rounded-full px-3 py-1 text-xs font-semibold {provider === 'configured_local_provider' ? 'bg-teal-100 text-teal-900' : 'bg-amber-100 text-amber-900'}">
					Provider: {provider}
				</span>
			</div>
			{#if provider !== 'configured_local_provider'}
				<p class="rounded border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
					The provider did not report verified local model inference. Some or all of this proposal may come from deterministic fallback rules.
				</p>
			{/if}
			<div class="grid gap-3 md:grid-cols-2">
				{#each [
					{label:'01 · Framework',value:draft.framework_resolution?.canonical_framework_name || draft.framework_resolution?.requested_framework_name,description:'Verify this exact framework is available in the platform',href:'/frameworks'},
					{label:'02 · Organizational domain',value:draft.case_setup_draft?.folder_domain_draft?.name,description:'Check for an existing domain before creating a duplicate',href:'/folders'},
					{label:'03 · Perimeter / scope',value:draft.case_setup_draft?.perimeter_draft?.name,description:draft.case_setup_draft?.perimeter_draft?.description || 'Confirm in-scope systems',href:'/perimeters'},
					{label:'04 · Assessment',value:draft.case_setup_draft?.compliance_assessment_draft?.name,description:'Create only after framework and scope have been approved',href:'/compliance-assessments'}
				] as item}
					<div class="rounded-lg border border-surface-300 bg-surface-100 p-4">
						<div class="text-xs font-bold uppercase tracking-wide text-teal-700">{item.label}</div>
						<div class="mt-2 font-semibold">{item.value || 'Not resolved yet'}</div>
						<div class="mt-2 text-xs text-surface-600">{item.description}</div>
						<a class="mt-3 inline-block text-sm font-semibold text-teal-700 underline" href={item.href}>Review in the platform →</a>
					</div>
				{/each}
			</div>
			{#if draft.blocking_questions?.length}
				<div class="rounded-lg border border-amber-300 bg-amber-50 p-4">
					<h3 class="font-bold text-amber-900">Questions to resolve before creation</h3>
					<ul class="mt-2 list-disc space-y-1 pl-5 text-sm text-amber-900">
						{#each draft.blocking_questions as question}
							<li>{question.question_text || question.question || 'Review the unresolved prerequisite.'}</li>
						{/each}
					</ul>
				</div>
			{/if}
			{#if draft.warnings?.length}
				<details class="rounded border border-surface-300 p-3">
					<summary class="cursor-pointer font-semibold">AI warnings ({draft.warnings.length})</summary>
					<ul class="mt-2 list-disc space-y-1 pl-5 text-sm">
						{#each draft.warnings as warning}
							<li>{warning.message || warning.code}</li>
						{/each}
					</ul>
				</details>
			{/if}
			<div class="rounded border border-surface-300 p-4 text-sm">
				<p class="font-semibold">Next: validate and approve the actual case setup</p>
				<p class="mt-1 text-surface-600">Use <strong>Get Started → Local AI Case Onboarding</strong> to run the existing Step 2 dry-run and approval flow. This workspace does not bypass its permission checks or create records silently.</p>
			</div>
			<button class="btn preset-tonal-primary" type="button" onclick={() => (showTechnical = !showTechnical)}>
				{showTechnical ? 'Hide' : 'Show'} structured proposal JSON
			</button>
			{#if showTechnical}
				<pre class="max-h-96 overflow-auto rounded-lg bg-slate-900 p-4 text-xs text-slate-100">{JSON.stringify(draft, null, 2)}</pre>
			{/if}
		</section>
	{/if}

	<section class="space-y-3 rounded-xl border border-surface-300 bg-surface-50 p-5 shadow-sm md:p-6">
		<div class="flex flex-wrap items-center justify-between gap-3">
			<h2 class="text-xl font-bold">Existing GRC modules</h2>
			<span class="text-xs text-surface-600">Links to your actual platform screens</span>
		</div>
		<p class="text-sm text-surface-600">Use existing functions rather than duplicating them. Every module needs its own AI capability and acceptance tests before we claim automation.</p>
		<div class="grid gap-4 md:grid-cols-2">
			{#each sections as section}
				<div class="rounded-lg border border-surface-300 bg-surface-100 p-4">
					<h3 class="font-bold">{section.name}</h3>
					<div class="mt-3 divide-y divide-surface-300">
						{#each section.items as item}
							<a href={item.href} class="flex items-center justify-between gap-3 py-2 hover:text-teal-700">
								<span><span class="block text-sm font-semibold">{item.title}</span><span class="text-xs text-surface-600">{item.detail}</span></span>
								<span aria-hidden="true">↗</span>
							</a>
						{/each}
					</div>
				</div>
			{/each}
		</div>
	</section>
</div>
