<script lang="ts">
	import AiOnboardingAlreadyCommitted from './AiOnboardingAlreadyCommitted.svelte';
	import AiOnboardingPrerequisite from './AiOnboardingPrerequisite.svelte';
	import {
		ai,
		appliedControlDuplicateCandidates,
		appliedControlProviderMode,
		approvedAssetReferences,
		formatConfidence,
		getAutoReuseAppliedControlMatch,
		humanizeActionName,
		humanizeFieldLabel,
		humanizeProviderMode,
		isAppliedControlConfiguredLocalProvider,
		linkedAssetLabel,
		runAppliedControlCommit,
		runAppliedControlSuggestion,
		selectedAppliedControlCandidates
	} from './aiOnboardingState.svelte';

	/**
	 * Steps 4A and 4B: the applied control suggestion and the deterministic applied control write.
	 *
	 * They render on the Applied controls page because Step 4B creates or reuses AppliedControl
	 * records. Step 4A still consumes the approved assets Step 3B produced; that handoff travels
	 * through the shared workflow state rather than through the page.
	 */
</script>

<section data-testid="ai-onboarding-step-4a">
	{#if !ai.commitResult || !ai.assetCommitHash || !approvedAssetReferences().length}
		<AiOnboardingPrerequisite
			step="4A"
			requires="3B"
			detail="Complete the approved asset commit before Step 4A. Step 4A requires at least one created or reused approved asset."
		/>
	{:else}
		<div class="rounded-md border border-cyan-200 bg-cyan-50/70 p-4">
			<div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
				<div>
					<h3 class="text-base font-bold text-cyan-950">
						Step 4A &middot; AI Suggested Applied Controls
					</h3>
					<p class="text-sm text-cyan-900">
						<span class="font-semibold">AI suggestion only / no database write.</span>
						Step 4A drafts candidate applied controls for the approved assets. No applied controls are
						created until the approved Step 4B commit.
					</p>
				</div>
				<div
					class="rounded px-2 py-1 text-xs font-semibold {isAppliedControlConfiguredLocalProvider()
						? 'bg-emerald-100 text-emerald-800'
						: appliedControlProviderMode() === 'not run'
							? 'bg-slate-100 text-slate-700'
							: 'bg-amber-100 text-amber-900'}"
				>
					AI Provider: {humanizeProviderMode(appliedControlProviderMode())}
				</div>
			</div>

			<div class="mt-3 flex flex-wrap items-center gap-3">
				<button
					class="btn btn-sm preset-filled-primary-500"
					type="button"
					disabled={ai.loading !== null || !ai.assetCommitHash || !approvedAssetReferences().length}
					onclick={runAppliedControlSuggestion}
				>
					{ai.loading === 'control-suggest'
						? 'Running Local AI...'
						: 'Run Local AI Applied Control Suggestion'}
				</button>
				<span class="text-xs text-cyan-900"
					>Uses {approvedAssetReferences().length} approved asset{approvedAssetReferences()
						.length === 1
						? ''
						: 's'} from Step 3B.</span
				>
			</div>

			{#if ai.appliedControlDraft}
				<div class="mt-4 rounded border bg-white p-3 text-sm">
					<div class="flex flex-wrap gap-3">
						<div>
							<span class="font-semibold">Suggestion type:</span>
							{humanizeFieldLabel(ai.appliedControlDraft.draft_type)}
						</div>
						<div>
							<span class="font-semibold">Suggestions found:</span>
							{ai.appliedControlDraft.candidate_applied_controls?.length ?? 0}
						</div>
						<div>
							<span class="font-semibold">Overall confidence:</span>
							{formatConfidence(ai.appliedControlDraft.overall_confidence)}
						</div>
					</div>

					{#if !ai.appliedControlDraft.candidate_applied_controls?.length}
						<div class="mt-3 rounded border border-amber-200 bg-amber-50 p-3 text-amber-900">
							No applied-control candidates were returned. Review warnings or backend validation
							details before rerunning.
						</div>
					{/if}

					<div class="mt-3 grid gap-3">
						{#each ai.appliedControlDraft.candidate_applied_controls ?? [] as candidate}
							{@const autoReuseAppliedControlMatch = getAutoReuseAppliedControlMatch(
								candidate,
								appliedControlDuplicateCandidates()
							)}
							<div class="rounded border p-3">
								<div class="flex items-start gap-3">
									<input
										type="checkbox"
										checked={!!ai.selectedAppliedControlTemporaryIds[candidate.temporary_id]}
										onchange={(event) => {
											ai.selectedAppliedControlTemporaryIds = {
												...ai.selectedAppliedControlTemporaryIds,
												[candidate.temporary_id]: event.currentTarget.checked
											};
										}}
									/>
									<div class="grow">
										<div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
											<div>
												<div class="font-semibold text-slate-950">{candidate.proposed_name}</div>
												<div class="mt-1 text-slate-700">{candidate.proposed_description}</div>
											</div>
											<div
												class="rounded bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700"
											>
												Confidence: {formatConfidence(candidate.confidence)}
											</div>
										</div>
										{#if autoReuseAppliedControlMatch}
											<div
												class="mt-3 rounded border border-amber-200 bg-amber-50 px-2 py-1 text-xs text-amber-900"
											>
												Existing applied control found: {autoReuseAppliedControlMatch.existing_name}
												will be reused instead of creating a duplicate.
											</div>
										{/if}
										<div class="mt-3 grid gap-2 text-xs text-slate-700 md:grid-cols-3">
											<div>
												<span class="font-semibold">Category:</span>
												{humanizeFieldLabel(candidate.proposed_control_category)}
											</div>
											<div>
												<span class="font-semibold">Status:</span>
												{humanizeFieldLabel(candidate.proposed_status)}
											</div>
											<div>
												<span class="font-semibold">Implementation:</span>
												{humanizeFieldLabel(candidate.proposed_implementation_state)}
											</div>
											<div>
												<span class="font-semibold">Review status:</span>
												{humanizeFieldLabel(candidate.human_review_status)}
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
											<div class="mt-2 text-xs text-slate-500">
												<span class="font-semibold">Available review actions:</span>
												{candidate.allowed_next_actions
													.map((nextAction: string) => humanizeActionName(nextAction))
													.join(', ')}
											</div>
										{/if}
									</div>
								</div>
							</div>
						{/each}
					</div>

					{#if ai.appliedControlDraft.duplicate_candidates?.length}
						<div
							class="mt-3 rounded border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900"
						>
							<div class="font-semibold">Possible duplicate applied controls</div>
							<p class="text-xs">
								These suggestions look similar to applied controls that already exist. Review them
								before creating new ones.
							</p>
							<ul class="mt-1 list-disc pl-5">
								{#each ai.appliedControlDraft.duplicate_candidates as duplicate}
									<li>
										<span class="font-semibold">{duplicate.proposed_name}</span> &mdash;
										{humanizeActionName(duplicate.recommended_human_action)}
										{#if duplicate.matches?.[0]}
											(matches existing applied control "{duplicate.matches[0].existing_name}")
										{/if}
									</li>
								{/each}
							</ul>
						</div>
					{/if}
				</div>
			{/if}
		</div>
	{/if}
</section>

<section data-testid="ai-onboarding-step-4b">
	{#if !ai.appliedControlDraft}
		<AiOnboardingPrerequisite step="4B" requires="4A" detail="Run Step 4A before Step 4B." />
	{:else}
		<div class="rounded border border-cyan-200 bg-cyan-50/60 p-3 text-sm text-cyan-950">
			<div class="font-semibold">Step 4B &middot; Applied Control Commit</div>
			<p class="mt-1 text-cyan-900">
				<span class="font-semibold">No AI model is used / writes only after approval.</span>
				Step 4A above remains advisory and no-write. Step 4B dry-run previews the plan without writing;
				the approved commit writes only the applied controls you selected.
			</p>
			<div class="mt-3 flex flex-wrap items-center gap-3">
				<button
					class="btn btn-sm preset-tonal-primary"
					type="button"
					disabled={ai.loading !== null || !selectedAppliedControlCandidates().length}
					onclick={() => runAppliedControlCommit(true)}
				>
					{ai.loading === 'control-dry-run' ? 'Dry-running...' : 'Step 4B dry-run'}
				</button>
				<label class="flex items-center gap-2 text-sm">
					<input type="checkbox" bind:checked={ai.appliedControlCommitApproved} />
					<span>I approve deterministic Step 4B decisions for selected applied controls</span>
				</label>
				<button
					class="btn btn-sm preset-filled-primary-500"
					type="button"
					disabled={ai.loading !== null ||
						Boolean(ai.appliedControlCommitResult) ||
						!selectedAppliedControlCandidates().length ||
						!ai.appliedControlCommitApproved}
					onclick={() => runAppliedControlCommit(false)}
				>
					{ai.loading === 'control-commit' ? 'Committing...' : 'Approved applied control commit'}
				</button>
				<span class="text-xs text-cyan-900">No AI model is used in this write step.</span>
			</div>

			{#if ai.appliedControlCommitResult}
				<AiOnboardingAlreadyCommitted step="4B" rerun="4A" />
			{/if}

			{#if ai.appliedControlCommitDryRun}
				<div class="mt-3 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">
						Step 4B dry-run status: {ai.appliedControlCommitDryRun.status}
					</div>
					<p class="mt-1 text-xs text-slate-600">
						Dry-run is a preview only — nothing was written to the database.
					</p>
					<ul class="mt-2 list-disc pl-5">
						{#each ai.appliedControlCommitDryRun.planned_actions ?? [] as action}
							<li>
								<span class="font-semibold">{humanizeActionName(action.action)}</span> &mdash; {action.detail}
							</li>
						{/each}
					</ul>
				</div>
			{/if}

			{#if ai.appliedControlCommitResult}
				<div class="mt-3 grid gap-2 rounded border border-emerald-200 bg-emerald-50 p-3 text-sm">
					<div class="font-semibold">
						Step 4B commit status: {ai.appliedControlCommitResult.status}
					</div>
					<p class="text-xs text-emerald-900">
						Approved deterministic write completed — only the counted records below were touched.
					</p>
					<div>Created: {ai.appliedControlCommitResult.created_applied_controls?.length ?? 0}</div>
					<div>Reused: {ai.appliedControlCommitResult.reused_applied_controls?.length ?? 0}</div>
					<div>
						Rejected: {ai.appliedControlCommitResult.rejected_applied_controls?.length ?? 0}
					</div>
					<div>
						Deferred: {ai.appliedControlCommitResult.deferred_applied_controls?.length ?? 0}
					</div>
					<div>Warnings: {ai.appliedControlCommitResult.warnings?.length ?? 0}</div>
					<div>Blocking errors: {ai.appliedControlCommitResult.blocking_errors?.length ?? 0}</div>
					<p class="text-xs text-emerald-900">
						Next: <a class="font-semibold underline" href="/evidences">
							Step 5A on the Evidences page</a
						>.
					</p>
				</div>
				{#if ai.appliedControlCommitResult.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.appliedControlCommitResult.warnings as warning}
							<li>{warning.detail ?? warning.message ?? warning.code}</li>
						{/each}
					</ul>
				{/if}
				{#if ai.appliedControlCommitResult.blocking_errors?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
						{#each ai.appliedControlCommitResult.blocking_errors as blockingError}
							<li>{blockingError.detail}</li>
						{/each}
					</ul>
				{/if}
			{/if}
		</div>
	{/if}
</section>
