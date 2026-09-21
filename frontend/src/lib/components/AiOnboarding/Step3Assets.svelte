<script lang="ts">
	import AiOnboardingAlreadyCommitted from './AiOnboardingAlreadyCommitted.svelte';
	import {
		ai,
		duplicateCandidates,
		formatConfidence,
		getAutoReuseMatch,
		humanizeActionName,
		humanizeProviderMode,
		isConfiguredLocalProvider,
		providerMode,
		runCommit,
		runSuggestion,
		selectedCandidates
	} from './aiOnboardingState.svelte';

	/**
	 * Steps 3A and 3B: the asset suggestion and the deterministic asset write.
	 *
	 * They render on the Assets page because Step 3B is what creates or reuses Asset records.
	 * The two steps stay separate: 3A calls the model and writes nothing, 3B calls no model and
	 * writes only after its own dry-run and approval.
	 */
</script>

<section data-testid="ai-onboarding-step-3a">
	<div class="rounded-md border border-teal-200 bg-white p-4">
		<div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
			<div>
				<h3 class="text-base font-bold text-teal-950">Step 3A &middot; AI Suggested Assets</h3>
				<p class="text-sm text-teal-900">
					<span class="font-semibold">AI suggestion only / no database write.</span>
					Step 3A drafts candidate assets for review. Nothing is saved until you select candidates and
					approve the deterministic Step 3B commit below.
				</p>
			</div>
			<div
				class="rounded px-2 py-1 text-xs font-semibold {isConfiguredLocalProvider()
					? 'bg-emerald-100 text-emerald-800'
					: providerMode() === 'not run'
						? 'bg-slate-100 text-slate-700'
						: 'bg-amber-100 text-amber-900'}"
			>
				AI Provider: {humanizeProviderMode(providerMode())}
			</div>
		</div>

		<div class="mt-4 flex flex-wrap items-center gap-3">
			<button
				class="btn preset-filled-primary-500"
				type="button"
				disabled={ai.loading !== null ||
					!ai.sourceStep1DraftHash ||
					!ai.setupReference.folder_id ||
					!ai.setupReference.perimeter_id ||
					!ai.setupReference.compliance_assessment_id ||
					(!ai.scenarioText.trim() && !ai.scopeSummary.trim())}
				onclick={runSuggestion}
			>
				{ai.loading === 'suggest' ? 'Running Local AI...' : 'Run Local AI Asset Suggestion'}
			</button>
			<span class="text-xs text-teal-900">No database writes occur in Step 3A.</span>
		</div>

		{#if !ai.sourceStep1DraftHash || !ai.setupReference.folder_id || !ai.setupReference.perimeter_id || !ai.setupReference.compliance_assessment_id}
			<p class="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-900">
				Step 3A needs the Step 1 draft hash and the Step 2 folder, perimeter, and compliance
				assessment references, plus a scenario or scope summary. Run Steps 1 and 2 in the sidebar
				Quick Start dialog, or fill the case reference in above.
			</p>
		{/if}

		{#if ai.assetDraft}
			<div class="mt-4 rounded-md border bg-white p-4">
				<div class="flex flex-wrap items-center gap-2 text-sm">
					<span class="font-semibold">AI Provider:</span>
					<span
						class="rounded px-2 py-1 text-xs {isConfiguredLocalProvider()
							? 'bg-emerald-100 text-emerald-800'
							: 'bg-amber-100 text-amber-900'}">{humanizeProviderMode(providerMode())}</span
					>
					{#if !isConfiguredLocalProvider()}
						<span class="text-xs text-amber-700"
							>Fallback or blocked output — this was not a successful local AI run.</span
						>
					{/if}
				</div>
				<div class="mt-2 text-sm">
					Overall confidence: {formatConfidence(ai.assetDraft.overall_confidence)}
				</div>

				<div class="mt-3 grid gap-3">
					{#each ai.assetDraft.candidate_assets ?? [] as candidate}
						{@const autoReuseMatch = getAutoReuseMatch(candidate, duplicateCandidates())}
						<label class="rounded border p-3 text-sm">
							<div class="flex items-start gap-3">
								<input
									type="checkbox"
									checked={!!ai.selectedTemporaryIds[candidate.temporary_id]}
									onchange={(event) => {
										ai.selectedTemporaryIds = {
											...ai.selectedTemporaryIds,
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
											'PR'} &middot; Confidence: {formatConfidence(candidate.confidence)}
									</div>
									{#if candidate.ambiguity_flags?.length}
										<div class="text-xs text-amber-700">
											Ambiguity: {candidate.ambiguity_flags
												.map((flag: any) => flag.message)
												.join('; ')}
										</div>
									{/if}
									{#if autoReuseMatch}
										<div
											class="rounded border border-amber-200 bg-amber-50 px-2 py-1 text-xs text-amber-900"
										>
											Existing asset found: {autoReuseMatch.existing_name} will be reused instead of creating
											a duplicate.
										</div>
									{/if}
								</div>
							</div>
						</label>
					{/each}
				</div>

				{#if ai.assetDraft.duplicate_candidates?.length}
					<div class="mt-3 rounded border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
						<div class="font-semibold">Possible duplicates</div>
						<p class="text-xs">
							These suggestions look similar to records that already exist. Review them before
							creating new ones.
						</p>
						<ul class="mt-1 list-disc pl-5">
							{#each ai.assetDraft.duplicate_candidates as duplicate}
								<li>
									<span class="font-semibold">{duplicate.proposed_name}</span> &mdash;
									{humanizeActionName(duplicate.recommended_human_action)}
									{#if duplicate.matches?.[0]}
										(matches existing asset "{duplicate.matches[0].existing_name}")
									{/if}
								</li>
							{/each}
						</ul>
					</div>
				{/if}

				{#if ai.assetDraft.blocking_questions?.length}
					<ul class="mt-3 list-disc pl-5 text-sm text-red-700">
						{#each ai.assetDraft.blocking_questions as question}
							<li>{question.question_text}</li>
						{/each}
					</ul>
				{/if}
			</div>
		{/if}
	</div>
</section>

<section data-testid="ai-onboarding-step-3b">
	{#if !ai.assetDraft}
		<div class="rounded border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900">
			<div class="font-semibold">Step 3B is not available yet</div>
			<p class="mt-1 text-xs">Run Step 3A before Step 3B. Step 3A is on this page, above.</p>
		</div>
	{:else}
		<div class="rounded border border-teal-200 bg-teal-50/50 p-3">
			<div class="text-sm font-semibold text-teal-950">Step 3B &middot; Asset Commit</div>
			<p class="mt-1 text-xs text-teal-900">
				<span class="font-semibold">No AI model is used / writes only after approval.</span>
				Dry-run previews the plan without writing. The approved commit writes only the asset candidates
				you selected above.
			</p>
			<div class="mt-3 flex flex-wrap items-center gap-3">
				<button
					class="btn btn-sm preset-tonal-primary"
					type="button"
					disabled={ai.loading !== null || !selectedCandidates().length}
					onclick={() => runCommit(true)}
				>
					{ai.loading === 'dry-run' ? 'Dry-running...' : 'Step 3B dry-run'}
				</button>
				<label class="flex items-center gap-2 text-sm">
					<input type="checkbox" bind:checked={ai.commitApproved} />
					<span>I approve deterministic Step 3B decisions for selected asset candidates</span>
				</label>
				<button
					class="btn btn-sm preset-filled-primary-500"
					type="button"
					disabled={ai.loading !== null ||
						!selectedCandidates().length ||
						!ai.commitApproved ||
						Boolean(ai.commitResult)}
					onclick={() => runCommit(false)}
				>
					{ai.loading === 'commit' ? 'Committing...' : 'Approved asset commit'}
				</button>
				<span class="text-xs text-slate-600">No AI model is used in this write step.</span>
			</div>

			{#if ai.commitResult}
				<AiOnboardingAlreadyCommitted step="3B" rerun="3A" />
			{/if}

			{#if ai.commitDryRun}
				<div class="mt-3 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">Step 3B dry-run status: {ai.commitDryRun.status}</div>
					<p class="mt-1 text-xs text-slate-600">
						Dry-run is a preview only — nothing was written to the database.
					</p>
					<ul class="mt-2 list-disc pl-5">
						{#each ai.commitDryRun.planned_actions ?? [] as action}
							<li>
								<span class="font-semibold">{humanizeActionName(action.action)}</span> &mdash; {action.detail}
							</li>
						{/each}
					</ul>
				</div>
			{/if}

			{#if ai.commitResult}
				<div class="mt-3 grid gap-2 rounded border border-emerald-200 bg-emerald-50 p-3 text-sm">
					<div class="font-semibold">Step 3B commit status: {ai.commitResult.status}</div>
					<p class="text-xs text-emerald-900">
						Approved deterministic write completed — only the records below were touched.
					</p>
					<div>Created: {ai.commitResult.created_assets?.length ?? 0}</div>
					<div>Reused: {ai.commitResult.reused_assets?.length ?? 0}</div>
					<div>Rejected: {ai.commitResult.rejected_assets?.length ?? 0}</div>
					<div>Deferred: {ai.commitResult.deferred_assets?.length ?? 0}</div>
					<p class="text-xs text-emerald-900">
						Next: <a class="font-semibold underline" href="/applied-controls">
							Step 4A on the Applied controls page</a
						>.
					</p>
				</div>
			{/if}
		</div>
	{/if}
</section>
