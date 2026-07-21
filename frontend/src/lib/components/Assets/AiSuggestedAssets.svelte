<script lang="ts">
	import { deserialize } from '$app/forms';
	import type { ActionResult } from '@sveltejs/kit';
	import { onMount } from 'svelte';
	import {
		buildReviewedAssetDecisions,
		getAutoReuseMatch,
		type DuplicateCandidate
	} from './assetCommitDecisions';

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
	let assetCommitHash = $state('');
	let appliedControlDraft = $state<any>(null);

	const providerMode = $derived(
		assetDraft?.provider_mode ?? assetDraft?.source_summary?.provider_mode ?? 'not run'
	);
	const appliedControlProviderMode = $derived(
		appliedControlDraft?.provider_mode ??
			appliedControlDraft?.source_summary?.provider_mode ??
			'not run'
	);
	const isConfiguredLocalProvider = $derived(providerMode === 'configured_local_provider');
	const isAppliedControlConfiguredLocalProvider = $derived(
		appliedControlProviderMode === 'configured_local_provider'
	);
	const selectedCandidates = $derived(
		(assetDraft?.candidate_assets ?? []).filter(
			(candidate: any) => selectedTemporaryIds[candidate.temporary_id]
		)
	);
	const duplicateCandidates = $derived((assetDraft?.duplicate_candidates ?? []) as DuplicateCandidate[]);
	const approvedAssetReferences = $derived(buildApprovedAssetReferences());
	const linkedAssetNamesById = $derived(
		Object.fromEntries(approvedAssetReferences.map((asset: any) => [asset.asset_id, asset.name]))
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

	function buildApprovedAssetReferences() {
		const assets = [
			...(commitResult?.created_assets ?? []),
			...(commitResult?.reused_assets ?? [])
		];
		return assets
			.filter((asset: any) => asset?.asset_id)
			.map((asset: any) => ({
				asset_id: asset.asset_id,
				name: asset.name,
				ref_id: asset.ref_id ?? asset.reference_id ?? null,
				asset_class: asset.asset_class ?? null,
				type: asset.type ?? null,
				source_temporary_id: asset.source_temporary_id ?? asset.temporary_id ?? null
			}));
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

	function buildAssetDecisions() {
		return buildReviewedAssetDecisions(selectedCandidates as any[], duplicateCandidates);
	}

	function buildCommitPayload(dryRun: boolean) {
		if (!assetDraft || !assetDraftHash) throw { detail: 'Run Step 3A before Step 3B.' };
		if (!selectedCandidates.length) throw { detail: 'Select at least one candidate asset.' };
		if (!dryRun && !commitApproved)
			throw { detail: 'Approve the deterministic asset write first.' };

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

	function buildAppliedControlSuggestionPayload() {
		if (!commitResult) throw { detail: 'Complete the approved asset commit before Step 4A.' };
		if (!assetCommitHash) throw { detail: 'Missing source_asset_commit_hash from Step 3B result.' };
		if (!approvedAssetReferences.length) {
			throw { detail: 'Step 4A requires at least one created or reused approved asset.' };
		}

		return {
			source_step1_draft_hash: sourceStep1DraftHash,
			source_asset_commit_hash: assetCommitHash,
			case_setup_reference: cleanSetupReferenceForCommit(),
			asset_references: approvedAssetReferences,
			scenario_text: scenarioText,
			scope_summary: scopeSummary,
			known_weaknesses: knownWeaknessList(),
			selected_framework_id: setupReference.selected_framework_id || null,
			user_locale: 'en',
			strict_mode: true
		};
	}

	async function runSuggestion() {
		loading = 'suggest';
		error = null;
		commitDryRun = null;
		commitResult = null;
		assetCommitHash = '';
		appliedControlDraft = null;
		try {
			assetDraft = await postAiAction('aiAssetSuggest', buildSuggestionPayload());
			assetDraftHash = await sha256Draft(assetDraft);
			selectedTemporaryIds = Object.fromEntries(
				(assetDraft?.candidate_assets ?? []).map((candidate: any) => [
					candidate.temporary_id,
					false
				])
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
			else {
				commitResult = result;
				assetCommitHash = await sha256Draft(result);
				appliedControlDraft = null;
			}
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	async function runAppliedControlSuggestion() {
		loading = 'control-suggest';
		error = null;
		try {
			appliedControlDraft = await postAiAction(
				'aiAppliedControlSuggest',
				buildAppliedControlSuggestionPayload()
			);
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	function linkedAssetLabel(assetId: string) {
		return linkedAssetNamesById[assetId] ?? assetId;
	}
</script>

<section class="mb-4 rounded-lg border border-teal-200 bg-teal-50/60 p-4 shadow-sm">
	<div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
		<div>
			<h2 class="text-lg font-bold text-teal-950">AI Suggested Assets</h2>
			<p class="text-sm text-teal-900">
				Step 3A suggests assets without writes. Step 3B writes only selected assets after approval.
			</p>
		</div>
		<div
			class="rounded px-2 py-1 text-xs font-semibold {isConfiguredLocalProvider
				? 'bg-emerald-100 text-emerald-800'
				: providerMode === 'not run'
					? 'bg-slate-100 text-slate-700'
					: 'bg-amber-100 text-amber-900'}"
		>
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
		<button
			class="btn preset-filled-primary-500"
			type="button"
			disabled={loading !== null ||
				!sourceStep1DraftHash ||
				!setupReference.folder_id ||
				!setupReference.perimeter_id ||
				!setupReference.compliance_assessment_id ||
				(!scenarioText.trim() && !scopeSummary.trim())}
			onclick={runSuggestion}
		>
			{loading === 'suggest' ? 'Running Local AI...' : 'Run Local AI Asset Suggestion'}
		</button>
		<span class="text-xs text-teal-900">No database writes occur in Step 3A.</span>
	</div>

	{#if assetDraft}
		<div class="mt-4 rounded-md border bg-white p-4">
			<div class="flex flex-wrap items-center gap-2 text-sm">
				<span class="font-semibold">provider_mode:</span>
				<span
					class="rounded px-2 py-1 text-xs {isConfiguredLocalProvider
						? 'bg-emerald-100 text-emerald-800'
						: 'bg-amber-100 text-amber-900'}">{providerMode}</span
				>
				{#if !isConfiguredLocalProvider}
					<span class="text-xs text-amber-700"
						>fallback or blocked output is not real local AI success</span
					>
				{/if}
			</div>
			<div class="mt-2 text-sm">Overall confidence: {assetDraft.overall_confidence}</div>

			<div class="mt-3 grid gap-3">
				{#each assetDraft.candidate_assets ?? [] as candidate}
					{@const autoReuseMatch = getAutoReuseMatch(candidate, duplicateCandidates)}
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
								<div class="text-xs text-slate-600">
									Type: {candidate.proposed_asset_type?.label ??
										candidate.proposed_asset_type?.value ??
										'PR'} | Confidence: {candidate.confidence}
								</div>
								{#if candidate.ambiguity_flags?.length}
									<div class="text-xs text-amber-700">
										Ambiguity: {candidate.ambiguity_flags
											.map((flag: any) => flag.message)
											.join('; ')}
									</div>
								{/if}
								{#if autoReuseMatch}
									<div class="rounded border border-amber-200 bg-amber-50 px-2 py-1 text-xs text-amber-900">
										Exact folder duplicate detected. Step 3B will reuse existing asset
										{autoReuseMatch.existing_name} instead of creating another one.
									</div>
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
							<li>
								{duplicate.proposed_name}: {duplicate.recommended_human_action}
								{#if duplicate.matches?.[0]}
									(reuse {duplicate.matches[0].existing_name})
								{/if}
							</li>
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
				<button
					class="btn btn-sm preset-tonal-primary"
					type="button"
					disabled={loading !== null || !selectedCandidates.length}
					onclick={() => runCommit(true)}
				>
					{loading === 'dry-run' ? 'Dry-running...' : 'Step 3B dry-run'}
				</button>
				<label class="flex items-center gap-2 text-sm">
					<input type="checkbox" bind:checked={commitApproved} />
					<span>I approve deterministic Step 3B decisions for selected asset candidates</span>
				</label>
				<button
					class="btn btn-sm preset-filled-primary-500"
					type="button"
					disabled={loading !== null || !selectedCandidates.length || !commitApproved}
					onclick={() => runCommit(false)}
				>
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

				<div class="mt-4 rounded-md border border-cyan-200 bg-cyan-50/70 p-4">
					<div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
						<div>
							<h3 class="text-base font-bold text-cyan-950">AI Suggested Applied Controls</h3>
							<p class="text-sm text-cyan-900">
								AI suggestions only. No applied controls are created until a later approved commit
								step.
							</p>
						</div>
						<div
							class="rounded px-2 py-1 text-xs font-semibold {isAppliedControlConfiguredLocalProvider
								? 'bg-emerald-100 text-emerald-800'
								: appliedControlProviderMode === 'not run'
									? 'bg-slate-100 text-slate-700'
									: 'bg-amber-100 text-amber-900'}"
						>
							provider_mode: {appliedControlProviderMode}
						</div>
					</div>

					<div class="mt-3 flex flex-wrap items-center gap-3">
						<button
							class="btn btn-sm preset-filled-primary-500"
							type="button"
							disabled={loading !== null || !assetCommitHash || !approvedAssetReferences.length}
							onclick={runAppliedControlSuggestion}
						>
							{loading === 'control-suggest'
								? 'Running Local AI...'
								: 'Run Local AI Applied Control Suggestion'}
						</button>
						<span class="text-xs text-cyan-900"
							>Uses {approvedAssetReferences.length} approved asset{approvedAssetReferences.length ===
							1
								? ''
								: 's'} from Step 3B.</span
						>
					</div>

					{#if appliedControlDraft}
						<div class="mt-4 rounded border bg-white p-3 text-sm">
							<div class="flex flex-wrap gap-3">
								<div>
									<span class="font-semibold">draft_type:</span>
									{appliedControlDraft.draft_type}
								</div>
								<div>
									<span class="font-semibold">candidate_count:</span>
									{appliedControlDraft.candidate_applied_controls?.length ?? 0}
								</div>
								<div>
									<span class="font-semibold">overall_confidence:</span>
									{appliedControlDraft.overall_confidence ?? 'n/a'}
								</div>
							</div>

							{#if !appliedControlDraft.candidate_applied_controls?.length}
								<div class="mt-3 rounded border border-amber-200 bg-amber-50 p-3 text-amber-900">
									No applied-control candidates were returned. Review warnings or backend validation
									details before rerunning.
								</div>
							{/if}

							<div class="mt-3 grid gap-3">
								{#each appliedControlDraft.candidate_applied_controls ?? [] as candidate}
									<div class="rounded border p-3">
										<div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
											<div>
												<div class="font-semibold text-slate-950">{candidate.proposed_name}</div>
												<div class="mt-1 text-slate-700">{candidate.proposed_description}</div>
											</div>
											<div
												class="rounded bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700"
											>
												confidence: {candidate.confidence}
											</div>
										</div>
										<div class="mt-3 grid gap-2 text-xs text-slate-700 md:grid-cols-3">
											<div>
												<span class="font-semibold">Category:</span>
												{candidate.proposed_control_category ?? 'n/a'}
											</div>
											<div>
												<span class="font-semibold">Status:</span>
												{candidate.proposed_status ?? 'n/a'}
											</div>
											<div>
												<span class="font-semibold">Implementation:</span>
												{candidate.proposed_implementation_state ?? 'n/a'}
											</div>
											<div>
												<span class="font-semibold">Review:</span>
												{candidate.human_review_status ?? 'n/a'}
											</div>
											<div class="md:col-span-2">
												<span class="font-semibold">Linked assets:</span>
												{(candidate.linked_asset_ids ?? [])
													.map((assetId: string) => linkedAssetLabel(assetId))
													.join(', ') || 'none'}
											</div>
										</div>
										<div class="mt-3 text-sm">
											<span class="font-semibold">Rationale:</span>
											{candidate.rationale}
										</div>
										{#if candidate.related_weaknesses?.length}
											<div class="mt-2 text-xs text-slate-700">
												<span class="font-semibold">Related weaknesses:</span>
												{candidate.related_weaknesses.join('; ')}
											</div>
										{/if}
										{#if candidate.allowed_next_actions?.length}
											<div class="mt-2 text-xs text-slate-700">
												<span class="font-semibold">Allowed next actions:</span>
												{candidate.allowed_next_actions.join(', ')}
											</div>
										{/if}
									</div>
								{/each}
							</div>
						</div>
					{/if}
				</div>
			{/if}

			<details class="mt-3">
				<summary class="cursor-pointer font-semibold">Raw JSON</summary>
				<pre
					class="mt-2 max-h-80 overflow-auto rounded bg-slate-950 p-3 text-xs text-slate-50">{JSON.stringify(
						{ assetDraft, commitDryRun, commitResult, appliedControlDraft },
						null,
						2
					)}</pre>
			</details>
		</div>
	{/if}

	{#if error}
		<pre
			class="mt-4 max-h-64 overflow-auto rounded border border-red-200 bg-red-50 p-3 text-xs text-red-900">{JSON.stringify(
				error,
				null,
				2
			)}</pre>
	{/if}
</section>
