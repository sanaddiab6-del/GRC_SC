<script lang="ts">
	import AiOnboardingAlreadyCommitted from './AiOnboardingAlreadyCommitted.svelte';
	import AiOnboardingPrerequisite from './AiOnboardingPrerequisite.svelte';
	import {
		ai,
		finalReviewDryRunSucceeded,
		finalReviewProviderMode,
		formatConfidence,
		humanizeActionName,
		humanizeFieldLabel,
		humanizeProviderMode,
		runFinalReviewCommit,
		runFinalReviewSuggestion
	} from './aiOnboardingState.svelte';

	/**
	 * Steps 12A and 12B: the end-to-end review summary and the case handoff note.
	 *
	 * They render on the audit page because Step 12B appends the handoff note to this audit's
	 * observation. The workflow is never marked complete, the audit is never closed, and no
	 * compliance is certified.
	 */
</script>

<section data-testid="ai-onboarding-step-12a">
	{#if !ai.auditReportDraft}
		<AiOnboardingPrerequisite
			step="12A"
			requires="11A"
			detail="Run Step 11A before Step 12A. Step 12A also needs at least one completed commit step before it can review the flow."
		/>
	{:else}
		<div class="rounded border border-sky-200 bg-sky-50/60 p-3 text-sm text-sky-950">
			<div class="font-semibold">Step 12A &middot; Final End-to-End Review Summary</div>
			<p class="mt-1 text-sky-900">
				<span class="font-semibold">AI suggestion only / no database write.</span>
				Step 12A explains what the onboarding flow completed and what remains for human review. The workflow
				is never marked complete and no audit is closed in this step.
			</p>
			<div class="mt-3 flex flex-wrap items-center gap-3">
				<button
					class="btn btn-sm preset-filled-primary-500"
					type="button"
					disabled={ai.loading !== null}
					onclick={() => runFinalReviewSuggestion()}
				>
					{ai.loading === 'final-review-suggest'
						? 'Running...'
						: 'Run Local AI Final Review Summary'}
				</button>
				<span class="text-xs text-sky-900">
					AI Provider: {humanizeProviderMode(finalReviewProviderMode())} &middot; No database writes occur
					in Step 12A.
				</span>
			</div>

			{#if ai.finalReviewDraft}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">Step 12A completion summary</div>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-sky-100 px-2 py-1 font-semibold text-sky-900">
							Demo readiness: {humanizeFieldLabel(ai.finalReviewDraft.demo_readiness_status)}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Overall confidence: {formatConfidence(ai.finalReviewDraft.overall_confidence)}
						</span>
						<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
							Warnings: {ai.finalReviewDraft.warnings?.length ?? 0}
						</span>
						{#if ai.finalReviewDraft.review_status}
							<span class="rounded bg-violet-100 px-2 py-1 font-semibold text-violet-900">
								{humanizeFieldLabel(ai.finalReviewDraft.review_status)}
							</span>
						{/if}
					</div>
					{#if ai.finalReviewDraft.completion_summary}
						<p class="text-xs text-slate-800">{ai.finalReviewDraft.completion_summary}</p>
					{/if}
				</div>

				<div class="mt-3 grid gap-2 md:grid-cols-2">
					{#each [['Completed steps', ai.finalReviewDraft.completed_steps], ['Incomplete steps', ai.finalReviewDraft.incomplete_steps], ['Created or reused records', ai.finalReviewDraft.created_or_reused_records_summary], ['Blocked items', ai.finalReviewDraft.blocked_items], ['Human review required', ai.finalReviewDraft.human_review_required], ['Recommended next steps', ai.finalReviewDraft.recommended_next_steps]] as [sectionLabel, entries]}
						{#if entries?.length}
							<div class="rounded border bg-white p-3 text-xs text-slate-800">
								<div class="font-semibold text-slate-950">{sectionLabel}</div>
								<ul class="mt-1 list-disc pl-5">
									{#each entries as entry}
										<li>{entry}</li>
									{/each}
								</ul>
							</div>
						{/if}
					{/each}
				</div>

				{#if ai.finalReviewDraft.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.finalReviewDraft.warnings as warning}
							<li>{warning.message ?? warning.detail ?? warning.code}</li>
						{/each}
					</ul>
				{/if}

				{#if ai.finalReviewDraft.ambiguity_flags?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.finalReviewDraft.ambiguity_flags as flag}
							<li>{flag.message ?? flag.code}</li>
						{/each}
					</ul>
				{/if}
			{/if}
		</div>
	{/if}
</section>

<section data-testid="ai-onboarding-step-12b">
	{#if !ai.finalReviewDraft}
		<AiOnboardingPrerequisite step="12B" requires="12A" detail="Run Step 12A before Step 12B." />
	{:else}
		<div class="rounded border border-emerald-300 bg-emerald-50/60 p-3 text-sm text-emerald-950">
			<div class="font-semibold">Step 12B &middot; Final Review Commit / Case Handoff</div>
			<p class="mt-1 text-emerald-900">
				<span class="font-semibold">No AI model is used / writes only after approval.</span>
				Select the case handoff summary to record, then dry-run to preview. The approved commit appends
				it to the audit's observation note only; the workflow is never marked complete, the audit is never
				closed, and no compliance is certified.
			</p>

			{#if !ai.setupReference.folder_id || !ai.setupReference.compliance_assessment_id}
				<p class="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-900">
					A Folder ID and a Compliance Assessment ID are required before the deterministic Step 12B
					write. Both come from Step 2 and can also be filled in under "Case reference &amp;
					context" above.
				</p>
			{/if}

			<div class="mt-3 grid gap-2">
				<label class="flex items-start gap-2 rounded border bg-white p-2 text-xs">
					<input type="checkbox" bind:checked={ai.finalReviewSelected} />
					<span>
						<span class="font-semibold">
							Case handoff summary: {humanizeFieldLabel(ai.finalReviewDraft.demo_readiness_status)}
						</span>
						<span class="text-slate-600">
							&middot; {ai.finalReviewDraft.human_review_required?.length ?? 0} human-review item(s)
						</span>
					</span>
				</label>
			</div>

			<div class="mt-3 flex flex-wrap items-center gap-3">
				<button
					class="btn btn-sm preset-tonal"
					type="button"
					disabled={ai.loading !== null || !ai.finalReviewSelected}
					onclick={() => runFinalReviewCommit(true)}
				>
					{ai.loading === 'final-review-commit-dry-run' ? 'Dry-running...' : 'Step 12B dry-run'}
				</button>
				<label class="flex items-center gap-2 text-xs">
					<input type="checkbox" bind:checked={ai.finalReviewCommitApproved} />
					<span>I approve the deterministic Step 12B case handoff note</span>
				</label>
				<button
					class="btn btn-sm preset-filled-error-500"
					type="button"
					disabled={ai.loading !== null ||
						Boolean(ai.finalReviewCommitResult) ||
						!ai.finalReviewCommitApproved ||
						!finalReviewDryRunSucceeded() ||
						!ai.finalReviewSelected}
					onclick={() => runFinalReviewCommit(false)}
				>
					{ai.loading === 'final-review-commit' ? 'Committing...' : 'Approved case handoff commit'}
				</button>
				<span class="text-xs text-emerald-900">No AI model is used in this write step.</span>
			</div>

			{#if ai.finalReviewCommitResult}
				<AiOnboardingAlreadyCommitted step="12B" rerun="12A" dryRunReArms />
			{/if}

			{#if ai.finalReviewCommitDryRun && !finalReviewDryRunSucceeded()}
				<p class="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-900">
					The last Step 12B dry-run was blocked. Resolve the blocking errors below and run the
					dry-run again before the approved commit.
				</p>
			{/if}

			{#if ai.finalReviewCommitDryRun}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">
						Step 12B dry-run status: {humanizeFieldLabel(ai.finalReviewCommitDryRun.commit_status)}
					</div>
					<p class="text-xs text-slate-700">
						Dry-run only previews the deterministic write. Nothing was written.
					</p>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Rejected: {ai.finalReviewCommitDryRun.rejected_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Deferred: {ai.finalReviewCommitDryRun.deferred_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Skipped: {ai.finalReviewCommitDryRun.skipped_records?.length ?? 0}
						</span>
					</div>
					{#if ai.finalReviewCommitDryRun.planned_actions?.length}
						<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.finalReviewCommitDryRun.planned_actions as action}
								<li>
									{action.target_name ?? action.source_temporary_id}:
									{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
									&middot; {action.detail}
								</li>
							{/each}
						</ul>
					{/if}
				</div>
				{#if ai.finalReviewCommitDryRun.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.finalReviewCommitDryRun.warnings as warning}
							<li>{warning.detail ?? warning.message ?? warning.code}</li>
						{/each}
					</ul>
				{/if}
				{#if ai.finalReviewCommitDryRun.blocking_errors?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
						{#each ai.finalReviewCommitDryRun.blocking_errors as blockingError}
							<li>{blockingError.detail}</li>
						{/each}
					</ul>
				{/if}
			{/if}

			{#if ai.finalReviewCommitResult}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">
						Step 12B commit status: {humanizeFieldLabel(ai.finalReviewCommitResult.commit_status)}
					</div>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
							Recorded: {ai.finalReviewCommitResult.created_records?.length ?? 0}
						</span>
						<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
							Unchanged: {ai.finalReviewCommitResult.reused_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Rejected: {ai.finalReviewCommitResult.rejected_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Deferred: {ai.finalReviewCommitResult.deferred_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Skipped: {ai.finalReviewCommitResult.skipped_records?.length ?? 0}
						</span>
						<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
							Warnings: {ai.finalReviewCommitResult.warnings?.length ?? 0}
						</span>
						<span class="rounded bg-red-100 px-2 py-1 font-semibold text-red-900">
							Blocking errors: {ai.finalReviewCommitResult.blocking_errors?.length ?? 0}
						</span>
					</div>
					{#if ai.finalReviewCommitResult.created_records?.length}
						<div class="text-xs font-semibold text-emerald-950">Recorded on</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.finalReviewCommitResult.created_records as record}
								<li>{record.name} &middot; {humanizeFieldLabel(record.record_type)}</li>
							{/each}
						</ul>
					{/if}
					{#if ai.finalReviewCommitResult.planned_actions?.length}
						<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.finalReviewCommitResult.planned_actions as action}
								<li>
									{action.target_name ?? action.source_temporary_id}:
									{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
								</li>
							{/each}
						</ul>
					{/if}
				</div>
				{#if ai.finalReviewCommitResult.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.finalReviewCommitResult.warnings as warning}
							<li>{warning.detail ?? warning.message ?? warning.code}</li>
						{/each}
					</ul>
				{/if}
				{#if ai.finalReviewCommitResult.blocking_errors?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
						{#each ai.finalReviewCommitResult.blocking_errors as blockingError}
							<li>{blockingError.detail}</li>
						{/each}
					</ul>
				{/if}
			{/if}
		</div>
	{/if}
</section>
