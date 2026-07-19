<script lang="ts">
	import { deserialize } from '$app/forms';
	import type { ActionResult } from '@sveltejs/kit';
	import { onMount } from 'svelte';

	let sourceStep1DraftHash = $state('');
	let setupReference = $state({
		folder_id: '',
		perimeter_id: '',
		compliance_assessment_id: '',
		risk_assessment_id: '',
		selected_framework_id: ''
	});
	let scenarioText = $state('');
	let scopeSummary = $state('');
	let knownWeaknesses = $state('');
	let strictMode = $state(true);
	let loading = $state<'suggest' | 'dry-run' | 'commit' | null>(null);
	let error = $state<any>(null);
	let assetDraft = $state<any>(null);
	let assetDraftHash = $state('');
	let selectedTemporaryIds = $state<Record<string, boolean>>({});
	let commitApproved = $state(false);
	let commitDryRun = $state<any>(null);
	let commitResult = $state<any>(null);

	const providerMode = $derived(assetDraft?.provider_mode ?? assetDraft?.source_summary?.provider_mode ?? 'not run');
	const isConfiguredLocalProvider = $derived(providerMode === 'configured_local_provider');
	const selectedCandidates = $derived(
		(assetDraft?.candidate_assets ?? []).filter((candidate: any) => selectedTemporaryIds[candidate.temporary_id])
	);

	onMount(() => {
		const stored = localStorage.getItem('sanad_ai_onboarding_setup');
		if (!stored) return;
		try {
			const parsed = JSON.parse(stored);
			sourceStep1DraftHash = parsed.source_step1_draft_hash ?? '';
			scenarioText = parsed.scenario_summary ?? '';
			setupReference = {
				folder_id: parsed.setupReference?.folder_id ?? '',
				perimeter_id: parsed.setupReference?.perimeter_id ?? '',
				compliance_assessment_id: parsed.setupReference?.compliance_assessment_id ?? '',
				risk_assessment_id: parsed.setupReference?.risk_assessment_id ?? '',
				selected_framework_id: parsed.setupReference?.selected_framework_id ?? ''
			};
		} catch {
			// Ignore stale local demo handoff data; visible fields remain editable.
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

		const response = await fetch(`?/${action}`, {
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
			if (response.ok) return parsed;
			if (parsed && typeof parsed === 'object') throw parsed;
		} catch {
			// If response is not JSON, fall through to a plain detail message.
		}

		throw {
			detail: responseText || `AI request failed with status ${response.status}.`
		};
	}

	function cleanSetupReferenceForSuggestion() {
		return {
			folder_id: setupReference.folder_id,
			perimeter_id: setupReference.perimeter_id || null,
			compliance_assessment_id: setupReference.compliance_assessment_id || null,
			risk_assessment_id: setupReference.risk_assessment_id || null
		};
	}

	function cleanSetupReferenceForCommit() {
		return {
			folder_id: setupReference.folder_id,
			perimeter_id: setupReference.perimeter_id || null,
			compliance_assessment_id: setupReference.compliance_assessment_id || null,
			risk_assessment_id: setupReference.risk_assessment_id || null,
			selected_framework_id: setupReference.selected_framework_id || null
		};
	}

	function knownWeaknessList() {
		return knownWeaknesses
			.split('\n')
			.map((item) => item.trim())
			.filter(Boolean);
	}

	function buildSuggestionPayload() {
		return {
			source_step1_draft_hash: sourceStep1DraftHash,
			case_setup_reference: cleanSetupReferenceForSuggestion(),
			folder_id: setupReference.folder_id,
			perimeter_id: setupReference.perimeter_id || null,
			compliance_assessment_id: setupReference.compliance_assessment_id || null,
			risk_assessment_id: setupReference.risk_assessment_id || null,
			scenario_text: scenarioText,
			scope_summary: scopeSummary,
			known_weaknesses: knownWeaknessList(),
			selected_framework_id: setupReference.selected_framework_id || null,
			strict_mode: strictMode
		};
	}

	function originalSuggestionSummary(candidate: any) {
		return {
			proposed_name: candidate.proposed_name,
			proposed_description: candidate.proposed_description ?? null,
			proposed_reference_id: candidate.proposed_reference_id ?? null,
			proposed_asset_type: candidate.proposed_asset_type ?? null,
			proposed_asset_category: candidate.proposed_asset_category ?? null,
			confidence: candidate.confidence,
			ambiguity_flags: candidate.ambiguity_flags ?? []
		};
	}

	function buildAssetDecisions() {
		return selectedCandidates.map((candidate: any) => ({
			temporary_id: candidate.temporary_id,
			action: 'create',
			human_approved: true,
			selected_existing_asset_id: null,
			approved_fields: {
				name: candidate.proposed_name,
				description: candidate.proposed_description ?? null,
				type: candidate.proposed_asset_type?.value ?? 'PR',
				ref_id: candidate.proposed_reference_id ?? null,
				observation: `Created from Local AI asset suggestion ${candidate.temporary_id}.`
			},
			original_suggestion_summary: originalSuggestionSummary(candidate),
			reviewer_notes: 'Human selected this candidate for deterministic asset commit.',
			ambiguity_resolution: candidate.ambiguity_flags?.length
				? { resolution_type: 'human_reviewed', resolution_note: 'Reviewed in the Assets page.' }
				: null,
			duplicate_resolution: null
		}));
	}

	function buildCommitPayload(dryRun: boolean) {
		if (!assetDraft || !assetDraftHash) throw { detail: 'Run Step 3A before Step 3B.' };
		if (!selectedCandidates.length) throw { detail: 'Select at least one candidate asset.' };
		if (!dryRun && !commitApproved) throw { detail: 'Approve the deterministic asset write first.' };

		return {
			dry_run: dryRun,
			approved_by_user: !dryRun && commitApproved,
			idempotency_key: dryRun ? null : `frontend-step3b-${Date.now()}`,
			source_step1_draft_hash: sourceStep1DraftHash,
			source_asset_draft_hash: assetDraftHash,
			case_setup_reference: cleanSetupReferenceForCommit(),
			asset_decisions: buildAssetDecisions()
		};
	}

	async function runSuggestion() {
		loading = 'suggest';
		error = null;
		commitDryRun = null;
		commitResult = null;
		try {
			assetDraft = await postAiAction('aiAssetSuggest', buildSuggestionPayload());
			assetDraftHash = await sha256Draft(assetDraft);
			selectedTemporaryIds = Object.fromEntries(
				(assetDraft?.candidate_assets ?? []).map((candidate: any) => [candidate.temporary_id, false])
			);
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	async function runCommit(dryRun: boolean) {
		loading = dryRun ? 'dry-run' : 'commit';
		error = null;
		try {
			const result = await postAiAction('aiAssetCommit', buildCommitPayload(dryRun));
			if (dryRun) commitDryRun = result;
			else commitResult = result;
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}
</script>

<section class="mb-4 rounded-lg border border-teal-200 bg-teal-50/60 p-4 shadow-sm">
	<div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
		<div>
			<h2 class="text-lg font-bold text-teal-950">AI Suggested Assets</h2>
			<p class="text-sm text-teal-900">Step 3A suggests assets without writes. Step 3B writes only selected assets after approval.</p>
		</div>
		<div class="rounded px-2 py-1 text-xs font-semibold {isConfiguredLocalProvider ? 'bg-emerald-100 text-emerald-800' : providerMode === 'not run' ? 'bg-slate-100 text-slate-700' : 'bg-amber-100 text-amber-900'}">
			provider_mode: {providerMode}
		</div>
	</div>

	<div class="mt-4 grid gap-3 md:grid-cols-2">
		<label class="grid gap-1">
			<span class="text-sm font-semibold">source_step1_draft_hash</span>
			<input class="input" bind:value={sourceStep1DraftHash} />
		</label>
		<label class="grid gap-1">
			<span class="text-sm font-semibold">Folder ID</span>
			<input class="input" bind:value={setupReference.folder_id} />
		</label>
		<label class="grid gap-1">
			<span class="text-sm font-semibold">Perimeter ID</span>
			<input class="input" bind:value={setupReference.perimeter_id} />
		</label>
		<label class="grid gap-1">
			<span class="text-sm font-semibold">ComplianceAssessment ID</span>
			<input class="input" bind:value={setupReference.compliance_assessment_id} />
		</label>
		<label class="grid gap-1">
			<span class="text-sm font-semibold">RiskAssessment ID</span>
			<input class="input" bind:value={setupReference.risk_assessment_id} />
		</label>
		<label class="grid gap-1">
			<span class="text-sm font-semibold">Selected Framework ID</span>
			<input class="input" bind:value={setupReference.selected_framework_id} />
		</label>
	</div>

	<div class="mt-3 grid gap-3">
		<label class="grid gap-1">
			<span class="text-sm font-semibold">Scenario/context summary</span>
			<textarea class="textarea" rows="3" bind:value={scenarioText}></textarea>
		</label>
		<label class="grid gap-1">
			<span class="text-sm font-semibold">Scope summary</span>
			<textarea class="textarea" rows="2" bind:value={scopeSummary}></textarea>
		</label>
		<label class="grid gap-1">
			<span class="text-sm font-semibold">Known weaknesses</span>
			<textarea class="textarea" rows="2" bind:value={knownWeaknesses}></textarea>
		</label>
		<label class="flex items-center gap-2 text-sm">
			<input type="checkbox" bind:checked={strictMode} />
			<span>Strict mode</span>
		</label>
	</div>

	<div class="mt-4 flex flex-wrap items-center gap-3">
		<button class="btn preset-filled-primary-500" type="button" disabled={loading !== null || !sourceStep1DraftHash || !setupReference.folder_id || !setupReference.perimeter_id || !setupReference.compliance_assessment_id || (!scenarioText.trim() && !scopeSummary.trim())} onclick={runSuggestion}>
			{loading === 'suggest' ? 'Running Local AI...' : 'Run Local AI Asset Suggestion'}
		</button>
		<span class="text-xs text-teal-900">No database writes occur in Step 3A.</span>
	</div>

	{#if assetDraft}
		<div class="mt-4 rounded-md border bg-white p-4">
			<div class="flex flex-wrap items-center gap-2 text-sm">
				<span class="font-semibold">provider_mode:</span>
				<span class="rounded px-2 py-1 text-xs {isConfiguredLocalProvider ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-900'}">{providerMode}</span>
				{#if !isConfiguredLocalProvider}
					<span class="text-xs text-amber-700">fallback or blocked output is not real local AI success</span>
				{/if}
			</div>
			<div class="mt-2 text-sm">Overall confidence: {assetDraft.overall_confidence}</div>

			<div class="mt-3 grid gap-3">
				{#each assetDraft.candidate_assets ?? [] as candidate}
					<label class="rounded border p-3 text-sm">
						<div class="flex items-start gap-3">
							<input
								type="checkbox"
								checked={!!selectedTemporaryIds[candidate.temporary_id]}
								onchange={(event) => {
									selectedTemporaryIds = {
										...selectedTemporaryIds,
										[candidate.temporary_id]: event.currentTarget.checked
									};
								}}
							/>
							<div class="space-y-1">
								<div class="font-semibold">{candidate.proposed_name}</div>
								<div>{candidate.proposed_description}</div>
								<div class="text-xs text-slate-600">Type: {candidate.proposed_asset_type?.label ?? candidate.proposed_asset_type?.value ?? 'PR'} | Confidence: {candidate.confidence}</div>
								{#if candidate.ambiguity_flags?.length}
									<div class="text-xs text-amber-700">Ambiguity: {candidate.ambiguity_flags.map((flag: any) => flag.message).join('; ')}</div>
								{/if}
							</div>
						</div>
					</label>
				{/each}
			</div>

			{#if assetDraft.duplicate_candidates?.length}
				<div class="mt-3 rounded border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
					<div class="font-semibold">Duplicate candidates</div>
					<ul class="list-disc pl-5">
						{#each assetDraft.duplicate_candidates as duplicate}
							<li>{duplicate.proposed_name}: {duplicate.recommended_human_action}</li>
						{/each}
					</ul>
				</div>
			{/if}

			{#if assetDraft.blocking_questions?.length}
				<ul class="mt-3 list-disc pl-5 text-sm text-red-700">
					{#each assetDraft.blocking_questions as question}
						<li>{question.question_text}</li>
					{/each}
				</ul>
			{/if}

			<div class="mt-4 flex flex-wrap items-center gap-3">
				<button class="btn btn-sm preset-tonal-primary" type="button" disabled={loading !== null || !selectedCandidates.length} onclick={() => runCommit(true)}>
					{loading === 'dry-run' ? 'Dry-running...' : 'Step 3B dry-run'}
				</button>
				<label class="flex items-center gap-2 text-sm">
					<input type="checkbox" bind:checked={commitApproved} />
					<span>I approve deterministic creation of selected asset candidates</span>
				</label>
				<button class="btn btn-sm preset-filled-primary-500" type="button" disabled={loading !== null || !selectedCandidates.length || !commitApproved} onclick={() => runCommit(false)}>
					{loading === 'commit' ? 'Committing...' : 'Approved asset commit'}
				</button>
				<span class="text-xs text-slate-600">No AI model is used in this write step.</span>
			</div>

			{#if commitDryRun}
				<div class="mt-3 rounded border p-3 text-sm">
					<div class="font-semibold">Dry-run status: {commitDryRun.status}</div>
					<ul class="list-disc pl-5">
						{#each commitDryRun.planned_actions ?? [] as action}
							<li>{action.action} - {action.detail}</li>
						{/each}
					</ul>
				</div>
			{/if}

			{#if commitResult}
				<div class="mt-3 grid gap-2 rounded border border-emerald-200 bg-emerald-50 p-3 text-sm">
					<div class="font-semibold">Commit status: {commitResult.status}</div>
					<div>Created: {commitResult.created_assets?.length ?? 0}</div>
					<div>Reused: {commitResult.reused_assets?.length ?? 0}</div>
					<div>Rejected: {commitResult.rejected_assets?.length ?? 0}</div>
					<div>Deferred: {commitResult.deferred_assets?.length ?? 0}</div>
				</div>
			{/if}

			<details class="mt-3">
				<summary class="cursor-pointer font-semibold">Raw JSON</summary>
				<pre class="mt-2 max-h-80 overflow-auto rounded bg-slate-950 p-3 text-xs text-slate-50">{JSON.stringify({ assetDraft, commitDryRun, commitResult }, null, 2)}</pre>
			</details>
		</div>
	{/if}

	{#if error}
		<pre class="mt-4 max-h-64 overflow-auto rounded border border-red-200 bg-red-50 p-3 text-xs text-red-900">{JSON.stringify(error, null, 2)}</pre>
	{/if}
</section>