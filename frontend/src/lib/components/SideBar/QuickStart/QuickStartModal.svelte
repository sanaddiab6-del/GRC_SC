<script lang="ts">
	import { deserialize } from '$app/forms';
	import AutocompleteSelect from '$lib/components/Forms/AutocompleteSelect.svelte';
	import SuperForm from '$lib/components/Forms/Form.svelte';
	import { goto } from '$lib/utils/breadcrumbs';
	import { getSecureRedirect } from '$lib/utils/helpers';
	import { defaults, superForm, type SuperValidated } from 'sveltekit-superforms';
	import { zod } from 'sveltekit-superforms/adapters';
 	import type { ActionResult } from '@sveltejs/kit';

	import * as m from '$paraglide/messages';
	import TextField from '$lib/components/Forms/TextField.svelte';
	import Checkbox from '$lib/components/Forms/Checkbox.svelte';
	import { quickStartSchema } from '$lib/utils/schemas';
	import { getLocale } from '$paraglide/runtime';
	import { getModalStore, type ModalStore } from '$lib/components/Modals/stores';

	const modalStore: ModalStore = getModalStore();

	interface Props {
		/** Exposes parent props to this component. */
		parent: any;
		invalidateAll?: boolean; // set to false to keep form data using muliple forms on a page
		formAction?: string;
		additionalInitialData?: any;
		suggestions?: { [key: string]: any };
		debug?: boolean;
		[key: string]: any;
	}

	let {
		parent,
		invalidateAll = true,
		formAction = '/quick-start?/create',
		additionalInitialData = {},
		suggestions = {},
		debug = false,
		initialMode = 'manual',
		...rest
	}: Props = $props();

	let closeModal = true;
	let mode = $state<'manual' | 'ai'>(initialMode === 'ai' ? 'ai' : 'manual');
	const defaultScenarioText =
		'SAMA ECC-1:2018 annual access management review found no formal user access review records, no MFA for remote access, and no PAM for privileged administrator accounts.';
	let aiScenarioText = $state(defaultScenarioText);
	let aiPreferredFramework = $state('SAMA ECC-1:2018');
	let aiOrganizationHint = $state('');
	let aiScopeHint = $state('');
	let aiAssessmentPeriodLabel = $state('');
	let aiKnownDeadline = $state('');
	let aiKnownTrigger = $state('');
	let aiStrictMode = $state(true);
	let aiCreateRiskAssessment = $state(false);
	let aiRiskMatrixId = $state('');
	let aiSelectedFrameworkId = $state('');
	let aiStep2Approved = $state(false);
	let aiLoading = $state<'step1' | 'dry-run' | 'create' | null>(null);
	let aiError = $state<any>(null);
	let caseIntakeDraft = $state<any>(null);
	let caseIntakeHash = $state('');
	let caseSetupDryRun = $state<any>(null);
	let caseSetupCreate = $state<any>(null);

	// Base Classes
	const cBase = 'card bg-surface-50 p-4 w-fit max-w-4xl shadow-xl space-y-4';
	const cHeader = 'text-2xl font-bold';
	const providerMode = $derived(caseIntakeDraft?.source_summary?.provider_mode ?? 'not run');
	const isConfiguredLocalProvider = $derived(providerMode === 'configured_local_provider');
	const step2FrameworkName = $derived(
		caseIntakeDraft?.framework_resolution?.canonical_framework_name ??
			caseIntakeDraft?.framework_resolution?.requested_framework_name ??
			aiPreferredFramework
	);
	const step2BlockingErrors = $derived(caseSetupDryRun?.blocking_errors ?? []);
	const frameworkAmbiguityError = $derived(
		step2BlockingErrors.find((error: any) => error?.code === 'multiple_framework_candidates') ?? null
	);
	const frameworkCandidateIds = $derived(frameworkAmbiguityError?.candidate_ids ?? []);
	const requiresExplicitFrameworkSelection = $derived(
		Boolean(frameworkAmbiguityError) || frameworkCandidateIds.length > 0
	);
	const hasSuccessfulStep2DryRun = $derived(
		Boolean(caseSetupDryRun) &&
			caseSetupDryRun?.status !== 'blocked' &&
			step2BlockingErrors.length === 0
	);
	const canRunApprovedCreate = $derived(
		aiLoading === null &&
			Boolean(aiStep2Approved) &&
			hasSuccessfulStep2DryRun &&
			(!requiresExplicitFrameworkSelection || Boolean(aiSelectedFrameworkId.trim()))
	);
	const approvedCreateDisabledReason = $derived.by(() => {
		if (aiLoading !== null) return 'Wait for the current Step 2 action to finish.';
		if (!caseSetupDryRun) return 'Run Step 2 dry-run first.';
		if (caseSetupDryRun?.status === 'blocked' || step2BlockingErrors.length > 0) {
			if (frameworkAmbiguityError) {
				return 'Multiple framework candidates found. Select one framework ID and rerun Step 2 dry-run.';
			}
			return 'Resolve the Step 2 blocking errors before approved create.';
		}
		if (requiresExplicitFrameworkSelection && !aiSelectedFrameworkId.trim()) {
			return 'Paste the selected Framework ID before approved create.';
		}
		if (!aiStep2Approved) return 'Check the approval box to enable approved create.';
		return null;
	});

	const form = defaults(
		{
			framework: 'urn:intuitem:risk:library:iso27001-2022',
			risk_matrix: 'urn:intuitem:risk:library:critical_risk_matrix_5x5',
			audit_name: `Quick start audit ${new Date().toLocaleTimeString(getLocale(), { hour: '2-digit', minute: '2-digit', second: '2-digit' })}`,
			risk_assessment_name: `Quick start risk assessment ${new Date().toLocaleTimeString(getLocale(), { hour: '2-digit', minute: '2-digit', second: '2-digit' })}`
		},
		zod(quickStartSchema)
	);

	const _form = superForm(form, {
		dataType: 'json',
		invalidateAll,
		applyAction: rest.applyAction ?? true,
		resetForm: rest.resetForm ?? false,
		validators: zod(quickStartSchema),
		taintedMessage: m.taintedFormMessage(),
		validationMethod: 'auto',
		onUpdated: async ({ form }) => {
			if (form.message?.redirect) {
				goto(getSecureRedirect(form.message.redirect));
			}
			if (form.valid) {
				parent.onConfirm();
			}
		}
	});

	function stableStringify(value: any): string {
		if (value === null || typeof value !== 'object') return JSON.stringify(value);
		if (Array.isArray(value)) return `[${value.map((item) => stableStringify(item)).join(',')}]`;
		return `{${Object.keys(value)
			.sort()
			.map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`)
			.join(',')}}`;
	}

	async function sha256Draft(value: any) {
		const digest = await crypto.subtle.digest(
			'SHA-256',
			new TextEncoder().encode(stableStringify(value))
		);
		return `sha256:${Array.from(new Uint8Array(digest))
			.map((byte) => byte.toString(16).padStart(2, '0'))
			.join('')}`;
	}

	async function postAiAction(action: string, payload: any) {
		const formData = new FormData();
		formData.set('payload', JSON.stringify(payload));

		const response = await fetch(`/quick-start?/${action}`, {
			method: 'POST',
			body: formData
		});
		const responseText = await response.text();
		let result: ActionResult<Record<string, any>> | null = null;
		try {
			result = deserialize(responseText) as ActionResult<Record<string, any>>;
		} catch {
			result = null;
		}

		if (result?.type === 'success') return result.data?.aiResult;
		if (result?.type === 'failure') throw result.data?.aiError ?? { detail: 'AI request failed.' };
		if (result?.type === 'error') throw { detail: 'AI request failed on the server.' };
		if (result?.type === 'redirect') throw { detail: 'Unexpected redirect during AI request.' };

		try {
			const parsed = JSON.parse(responseText);
			if (parsed && typeof parsed === 'object') throw parsed;
		} catch {
			// If response is not JSON, fall through to a plain detail message.
		}

		throw {
			detail: responseText || `AI request failed with status ${response.status}.`
		};
	}

	function buildStep1Payload() {
		return {
			scenario_text: aiScenarioText,
			preferred_framework: aiPreferredFramework || null,
			organization_hint: aiOrganizationHint || null,
			scope_hint: aiScopeHint || null,
			assessment_period: aiAssessmentPeriodLabel ? { label: aiAssessmentPeriodLabel } : null,
			known_deadline: aiKnownDeadline || null,
			known_trigger: aiKnownTrigger || null,
			strict_mode: aiStrictMode
		};
	}

	function buildStep2Payload(dryRun: boolean) {
		if (!caseIntakeDraft || !caseIntakeHash) throw { detail: 'Run Step 1 before Step 2.' };
		if (!dryRun && !aiStep2Approved) throw { detail: 'Approve the deterministic setup write first.' };
		if (requiresExplicitFrameworkSelection && !aiSelectedFrameworkId.trim()) {
			throw { detail: 'Select one framework before approved create.' };
		}
		if (aiCreateRiskAssessment && !aiRiskMatrixId.trim()) {
			throw { detail: 'Select or paste a RiskMatrix ID before creating a risk assessment.' };
		}

		const setupDraft = caseIntakeDraft.case_setup_draft ?? {};
		const framework = caseIntakeDraft.framework_resolution ?? {};
		const folderDraft = setupDraft.folder_domain_draft ?? {};
		const perimeterDraft = setupDraft.perimeter_draft ?? {};
		const auditDraft = setupDraft.compliance_assessment_draft ?? {};
		const riskDraft = setupDraft.optional_risk_assessment_draft ?? {};
		const candidate = framework.candidate_frameworks?.[0] ?? {};

		return {
			draft_type: 'AiCaseSetupApprovalRequest',
			schema_version: '0.1.0',
			approved_by_user: !dryRun && aiStep2Approved,
			source_step1_draft_hash: caseIntakeHash,
			source_step1_schema_version: caseIntakeDraft.schema_version,
			dry_run: dryRun,
			idempotency_key: dryRun ? null : `frontend-step2-${Date.now()}`,
			framework_resolution: {
				requested_framework_name:
					framework.canonical_framework_name || framework.requested_framework_name || aiPreferredFramework,
				selected_framework_id:
					aiSelectedFrameworkId.trim() || framework.selected_framework_id || null,
				selected_stored_library_urn: candidate.stored_library_urn || null,
				user_confirmed: true,
				allow_auto_load: false
			},
			folder_domain_decision: {
				action: 'create',
				platform_entity: 'Folder',
				selected_existing_id: null,
				proposed_fields: {
					name: folderDraft.name || aiOrganizationHint || 'AI Onboarding Domain',
					description: folderDraft.description || 'Domain reviewed from Local AI case intake.',
					create_iam_groups: false
				},
				human_approved: dryRun || aiStep2Approved,
				rationale: folderDraft.rationale || 'Human reviewed Step 1 domain draft.',
				source_reference: 'Step 1 draft'
			},
			perimeter_decision: {
				action: 'create',
				platform_entity: 'Perimeter',
				selected_existing_id: null,
				proposed_fields: {
					name: perimeterDraft.name || 'AI Onboarding Perimeter',
					description: perimeterDraft.description || 'Perimeter reviewed from Local AI case intake.',
					ref_id: perimeterDraft.reference_id || null,
					lc_status: perimeterDraft.lifecycle_status_if_known || 'in_design'
				},
				human_approved: dryRun || aiStep2Approved,
				rationale: perimeterDraft.rationale || 'Human reviewed Step 1 perimeter draft.',
				source_reference: 'Step 1 draft'
			},
			compliance_assessment_decision: {
				action: 'create',
				platform_entity: 'ComplianceAssessment',
				selected_existing_id: null,
				proposed_fields: {
					name: auditDraft.name || 'AI Onboarding Audit',
					description: auditDraft.description || 'Audit reviewed from Local AI case intake.',
					ref_id: auditDraft.reference_id || null,
					version: '1.0',
					status: auditDraft.status || 'planned'
				},
				human_approved: dryRun || aiStep2Approved,
				rationale: auditDraft.rationale || 'Human reviewed Step 1 audit draft.',
				source_reference: 'Step 1 draft'
			},
			risk_assessment_decision: aiCreateRiskAssessment
				? {
						action: 'create',
						platform_entity: 'RiskAssessment',
						selected_existing_id: null,
						proposed_fields: {
							name: riskDraft.name || 'AI Onboarding Risk Assessment',
							description: riskDraft.description || 'Risk assessment reviewed from Local AI case intake.',
							ref_id: null,
							version: '1.0',
							status: 'planned',
							selected_risk_matrix_id: aiRiskMatrixId.trim()
						},
						human_approved: dryRun || aiStep2Approved,
						rationale: riskDraft.rationale || 'Human selected optional risk assessment creation.',
						source_reference: 'Step 1 draft'
					}
				: {
						action: 'skip',
						platform_entity: 'RiskAssessment',
						selected_existing_id: null,
						proposed_fields: null,
						human_approved: dryRun || aiStep2Approved,
						rationale: 'Optional risk assessment was not selected.',
						source_reference: 'Step 1 draft'
					}
		};
	}

	function setupReferenceFromResult(result: any) {
		const objects = [...(result?.created_objects ?? []), ...(result?.reused_objects ?? [])];
		const findId = (entity: string) => objects.find((item: any) => item.platform_entity === entity)?.id;
		return {
			folder_id: findId('Folder'),
			perimeter_id: findId('Perimeter'),
			compliance_assessment_id: findId('ComplianceAssessment'),
			risk_assessment_id: findId('RiskAssessment') ?? null,
			selected_framework_id: findId('Framework') ?? null
		};
	}

	async function runCaseIntake() {
		aiLoading = 'step1';
		aiError = null;
		caseSetupDryRun = null;
		caseSetupCreate = null;
		try {
			caseIntakeDraft = await postAiAction('aiCaseIntake', buildStep1Payload());
			caseIntakeHash = await sha256Draft(caseIntakeDraft);
			aiSelectedFrameworkId = caseIntakeDraft?.framework_resolution?.selected_framework_id ?? '';
			aiStep2Approved = false;
			caseSetupDryRun = null;
			caseSetupCreate = null;
		} catch (error) {
			aiError = error;
		} finally {
			aiLoading = null;
		}
	}

	async function runCaseSetup(dryRun: boolean) {
		aiLoading = dryRun ? 'dry-run' : 'create';
		aiError = null;
		try {
			const result = await postAiAction('aiCaseSetup', buildStep2Payload(dryRun));
			if (dryRun) caseSetupDryRun = result;
			else {
				caseSetupCreate = result;
				const setupReference = setupReferenceFromResult(result);
				localStorage.setItem(
					'sanad_ai_onboarding_setup',
					JSON.stringify({
						setupReference,
						source_step1_draft_hash: caseIntakeHash,
						scenario_summary: caseIntakeDraft?.source_summary?.scenario_excerpt ?? '',
						case_context: caseIntakeDraft?.case_context ?? null,
						created_at: new Date().toISOString()
					})
				);
			}
		} catch (error) {
			aiError = error;
		} finally {
			aiLoading = null;
		}
	}
</script>

{#if $modalStore[0]}
	<div class="modal-example-form {cBase}">
		<div class="flex items-center justify-between">
			<header class={cHeader} data-testid="modal-title">
				{$modalStore[0].title ?? '(title missing)'}
			</header>
			<div
				role="button"
				tabindex="0"
				class="flex items-center hover:text-primary-500 cursor-pointer"
				onclick={parent.onClose}
				onkeydown={parent.onClose}
			>
				<i class="fa-solid fa-xmark"></i>
			</div>
		</div>
		<div class="inline-flex overflow-hidden rounded-md border bg-white text-sm">
			<button
				type="button"
				class="px-3 py-2 {mode === 'manual' ? 'preset-filled-primary-500' : ''}"
				onclick={() => (mode = 'manual')}>Manual</button
			>
			<button
				type="button"
				class="px-3 py-2 {mode === 'ai' ? 'preset-filled-primary-500' : ''}"
				onclick={() => (mode = 'ai')}>Local AI Case Onboarding</button
			>
		</div>

		{#if mode === 'manual'}
			<SuperForm
			class="flex flex-col space-y-3"
			dataType="json"
			enctype="application/x-www-form-urlencoded"
			data={form}
			{_form}
			{invalidateAll}
			validators={zod(quickStartSchema)}
			action={formAction}
			{...rest}
		>
			{#snippet children({ form, data, initialData })}
				<AutocompleteSelect
					{form}
					field="framework"
					label={m.framework()}
					optionsEndpoint="stored-libraries"
					optionsDetailedUrlParameters={[['object_type', 'framework']]}
					optionsValueField="urn"
				/>
				<TextField {form} field="audit_name" label={m.auditName()} />
				<Checkbox {form} field="create_risk_assessment" label={m.createRiskAssessment()} />
				<TextField
					{form}
					field="risk_assessment_name"
					label={m.riskAssessmentName()}
					disabled={!data.create_risk_assessment}
				/>
				<AutocompleteSelect
					{form}
					field="risk_matrix"
					label={m.riskMatrix()}
					optionsEndpoint="stored-libraries"
					optionsDetailedUrlParameters={[['object_type', 'risk_matrix']]}
					optionsValueField="urn"
					disabled={!data.create_risk_assessment}
				/>
				<div class="flex flex-row justify-between space-x-4">
					<button
						class="btn bg-gray-400 text-white font-semibold w-full"
						data-testid="cancel-button"
						type="button"
						onclick={(event) => {
							parent.onClose(event);
						}}>{m.cancel()}</button
					>

					<button
						class="btn preset-filled-primary-500 font-semibold w-full"
						data-testid="save-button"
						type="submit">{m.save()}</button
					>
				</div>
			{/snippet}
			</SuperForm>
		{:else}
			<div class="grid gap-4 text-sm">
				<label class="grid gap-1">
					<span class="font-semibold">Scenario text</span>
					<textarea class="textarea" rows="5" bind:value={aiScenarioText}></textarea>
				</label>
				<div class="grid gap-3 md:grid-cols-2">
					<label class="grid gap-1">
						<span class="font-semibold">Preferred framework</span>
						<input class="input" bind:value={aiPreferredFramework} />
					</label>
					<label class="grid gap-1">
						<span class="font-semibold">Organization hint</span>
						<input class="input" bind:value={aiOrganizationHint} />
					</label>
					<label class="grid gap-1 md:col-span-2">
						<span class="font-semibold">Scope hint</span>
						<input class="input" bind:value={aiScopeHint} />
					</label>
					<label class="grid gap-1">
						<span class="font-semibold">Assessment period label</span>
						<input class="input" bind:value={aiAssessmentPeriodLabel} />
					</label>
					<label class="grid gap-1">
						<span class="font-semibold">Known deadline</span>
						<input class="input" type="date" bind:value={aiKnownDeadline} />
					</label>
					<label class="grid gap-1 md:col-span-2">
						<span class="font-semibold">Known trigger</span>
						<input class="input" bind:value={aiKnownTrigger} />
					</label>
				</div>
				<label class="flex items-center gap-2">
					<input type="checkbox" bind:checked={aiStrictMode} />
					<span>Strict mode</span>
				</label>
				<button
					class="btn preset-filled-primary-500 font-semibold w-fit"
					type="button"
					disabled={aiLoading !== null || !aiScenarioText.trim()}
					onclick={runCaseIntake}
				>
					{aiLoading === 'step1' ? 'Running Local AI...' : 'Run Local AI'}
				</button>

				{#if caseIntakeDraft}
					<div class="rounded-md border bg-white p-4 space-y-3">
						<div class="flex flex-wrap items-center gap-2">
							<span class="font-semibold">provider_mode:</span>
							<span class="rounded px-2 py-1 text-xs {isConfiguredLocalProvider ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-900'}">{providerMode}</span>
							{#if !isConfiguredLocalProvider}
								<span class="text-xs text-amber-700">fallback or blocked output is not real local AI success</span>
							{/if}
						</div>
						<div>Confidence: {caseIntakeDraft.overall_confidence}</div>
						{#if caseIntakeDraft.blocking_questions?.length}
							<ul class="list-disc pl-5 text-red-700">
								{#each caseIntakeDraft.blocking_questions as question}
									<li>{question.question_text}</li>
								{/each}
							</ul>
						{/if}
						{#if caseIntakeDraft.warnings?.length}
							<ul class="list-disc pl-5 text-amber-700">
								{#each caseIntakeDraft.warnings as warning}
									<li>{warning.message}</li>
								{/each}
							</ul>
						{/if}
						<div class="grid gap-2 md:grid-cols-3">
							<div><span class="font-semibold">Domain:</span> {caseIntakeDraft.case_setup_draft?.folder_domain_draft?.name}</div>
							<div><span class="font-semibold">Perimeter:</span> {caseIntakeDraft.case_setup_draft?.perimeter_draft?.name}</div>
							<div><span class="font-semibold">Audit:</span> {caseIntakeDraft.case_setup_draft?.compliance_assessment_draft?.name}</div>
						</div>
						<div class="grid gap-3 md:grid-cols-2">
							<label class="grid gap-1">
								<span class="font-semibold">Framework name</span>
								<input class="input bg-slate-100" value={step2FrameworkName} readonly />
							</label>
							<label class="grid gap-1">
								<span class="font-semibold">Selected Framework ID</span>
								<input
									class="input"
									bind:value={aiSelectedFrameworkId}
									placeholder="Paste the visible Framework UUID used for Step 2"
								/>
							</label>
						</div>
						{#if aiSelectedFrameworkId.trim()}
							<p class="text-xs text-slate-600">
								Step 2 will send this as <span class="font-mono">framework_resolution.selected_framework_id</span>.
							</p>
						{/if}
						<label class="flex items-center gap-2">
							<input type="checkbox" bind:checked={aiCreateRiskAssessment} />
							<span>Create optional RiskAssessment</span>
						</label>
						{#if aiCreateRiskAssessment}
							<label class="grid gap-1">
								<span class="font-semibold">Selected RiskMatrix ID</span>
								<input class="input" bind:value={aiRiskMatrixId} />
							</label>
						{/if}
						<p class="text-xs text-slate-600">No AI model is used in this write step.</p>
						<div class="flex flex-wrap gap-2">
							<button class="btn btn-sm preset-tonal-primary" type="button" disabled={aiLoading !== null} onclick={() => runCaseSetup(true)}>
								{aiLoading === 'dry-run' ? 'Dry-running...' : 'Step 2 dry-run'}
							</button>
							<label class="flex items-center gap-2">
								<input type="checkbox" bind:checked={aiStep2Approved} />
								<span>I approve creating/reusing the reviewed setup objects</span>
							</label>
							<button class="btn btn-sm preset-filled-primary-500" type="button" disabled={!canRunApprovedCreate} onclick={() => runCaseSetup(false)}>
								{aiLoading === 'create' ? 'Creating...' : 'Approved create'}
							</button>
						</div>
						{#if approvedCreateDisabledReason}
							<p class="text-xs text-amber-800">{approvedCreateDisabledReason}</p>
						{/if}
						{#if caseSetupDryRun}
							<div class="rounded border p-3">
								<div class="font-semibold">Dry-run status: {caseSetupDryRun.status}</div>
								{#if frameworkAmbiguityError}
									<div class="mt-2 rounded border border-amber-200 bg-amber-50 p-3 text-amber-900">
										<div class="font-semibold">
											Multiple framework candidates found. Select one framework before approved create.
										</div>
										<div class="mt-1 text-sm">{frameworkAmbiguityError.detail}</div>
										{#if frameworkCandidateIds.length}
											<details class="mt-2">
												<summary class="cursor-pointer font-semibold">
													Candidate framework IDs ({frameworkCandidateIds.length})
												</summary>
												<ul class="mt-2 max-h-40 list-disc overflow-auto pl-5 text-xs">
													{#each frameworkCandidateIds as candidateId}
														<li class="break-all">{candidateId}</li>
													{/each}
												</ul>
											</details>
										{/if}
									</div>
								{/if}
								{#if step2BlockingErrors.length}
									<ul class="mt-2 list-disc pl-5 text-sm text-red-700">
										{#each step2BlockingErrors as error}
											<li>{error.code}: {error.detail}</li>
										{/each}
									</ul>
								{/if}
								<ul class="list-disc pl-5">
									{#each caseSetupDryRun.planned_actions ?? [] as action}
										<li>{action.platform_entity}: {action.action} - {action.detail}</li>
									{/each}
								</ul>
							</div>
						{/if}
						{#if caseSetupCreate}
							<div class="rounded border border-emerald-200 bg-emerald-50 p-3">
								<div class="font-semibold">Create status: {caseSetupCreate.status}</div>
								<div>Created/reused objects are saved for the Assets page handoff.</div>
							</div>
						{/if}
						<details>
							<summary class="cursor-pointer font-semibold">Raw JSON</summary>
							<pre class="mt-2 max-h-80 overflow-auto rounded bg-slate-950 p-3 text-xs text-slate-50">{JSON.stringify({ caseIntakeDraft, caseSetupDryRun, caseSetupCreate }, null, 2)}</pre>
						</details>
					</div>
				{/if}

				{#if aiError}
					<pre class="max-h-64 overflow-auto rounded border border-red-200 bg-red-50 p-3 text-xs text-red-900">{JSON.stringify(aiError, null, 2)}</pre>
				{/if}
			</div>
		{/if}
	</div>
{/if}
