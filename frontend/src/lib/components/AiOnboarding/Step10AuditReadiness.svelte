<script lang="ts">
	import AiOnboardingAlreadyCommitted from './AiOnboardingAlreadyCommitted.svelte';
	import AiOnboardingPrerequisite from './AiOnboardingPrerequisite.svelte';
	import {
		ai,
		auditReadinessDryRunSucceeded,
		auditReadinessProviderMode,
		formatConfidence,
		humanizeActionName,
		humanizeFieldLabel,
		humanizeProviderMode,
		runAuditReadinessCommit,
		runAuditReadinessSuggestion
	} from './aiOnboardingState.svelte';

	/**
	 * Steps 10A and 10B: the evidence gap / audit readiness summary and its deterministic write.
	 *
	 * They render on the audit page because Step 10B appends the readiness note to this audit's
	 * observation. The audit status is never changed and the audit is never marked ready.
	 */
</script>

<section data-testid="ai-onboarding-step-10a">
	{#if !ai.controlEffectivenessDraft}
		<AiOnboardingPrerequisite
			step="10A"
			requires="9A"
			detail="Run Step 9A before Step 10A, so the readiness summary is drafted against the reviewed control effectiveness judgements."
		/>
	{:else}
		<div class="rounded border border-sky-200 bg-sky-50/60 p-3 text-sm text-sky-950">
			<div class="font-semibold">Step 10A &middot; Evidence Gap / Audit Readiness Summary</div>
			<p class="mt-1 text-sky-900">
				<span class="font-semibold">AI suggestion only / no database write.</span>
				Step 10A summarizes what is ready, what is missing, and what is blocking the assessment. Nothing
				is marked ready and nothing is closed in this step.
			</p>
			<div class="mt-3 flex flex-wrap items-center gap-3">
				<button
					class="btn btn-sm preset-filled-primary-500"
					type="button"
					disabled={ai.loading !== null}
					onclick={() => runAuditReadinessSuggestion()}
				>
					{ai.loading === 'audit-readiness-suggest'
						? 'Running...'
						: 'Run Local AI Audit Readiness Summary'}
				</button>
				<span class="text-xs text-sky-900">
					AI Provider: {humanizeProviderMode(auditReadinessProviderMode())} &middot; No database writes
					occur in Step 10A.
				</span>
			</div>

			{#if ai.auditReadinessDraft}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">Step 10A readiness summary</div>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-sky-100 px-2 py-1 font-semibold text-sky-900">
							Readiness: {humanizeFieldLabel(ai.auditReadinessDraft.readiness_status)}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Advisory score: {ai.auditReadinessDraft.readiness_score}/100
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Overall confidence: {formatConfidence(ai.auditReadinessDraft.overall_confidence)}
						</span>
						<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
							Warnings: {ai.auditReadinessDraft.warnings?.length ?? 0}
						</span>
					</div>
					{#if ai.auditReadinessDraft.summary}
						<p class="text-xs text-slate-800">{ai.auditReadinessDraft.summary}</p>
					{/if}
				</div>

				<div class="mt-3 grid gap-2 md:grid-cols-2">
					{#each [['Ready items', ai.auditReadinessDraft.ready_items], ['Missing evidence', ai.auditReadinessDraft.missing_evidence], ['Open findings', ai.auditReadinessDraft.open_findings], ['Open risks', ai.auditReadinessDraft.open_risks], ['Blocked controls', ai.auditReadinessDraft.blocked_controls], ['Priority actions', ai.auditReadinessDraft.priority_actions], ['Recommended next steps', ai.auditReadinessDraft.recommended_next_steps]] as [sectionLabel, entries]}
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

				{#if ai.auditReadinessDraft.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.auditReadinessDraft.warnings as warning}
							<li>{warning.message ?? warning.detail ?? warning.code}</li>
						{/each}
					</ul>
				{/if}

				{#if ai.auditReadinessDraft.ambiguity_flags?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.auditReadinessDraft.ambiguity_flags as flag}
							<li>{flag.message ?? flag.code}</li>
						{/each}
					</ul>
				{/if}
			{/if}
		</div>
	{/if}
</section>

<section data-testid="ai-onboarding-step-10b">
	{#if !ai.auditReadinessDraft}
		<AiOnboardingPrerequisite step="10B" requires="10A" detail="Run Step 10A before Step 10B." />
	{:else}
		<div class="rounded border border-emerald-300 bg-emerald-50/60 p-3 text-sm text-emerald-950">
			<div class="font-semibold">Step 10B &middot; Audit Readiness Commit</div>
			<p class="mt-1 text-emerald-900">
				<span class="font-semibold">No AI model is used / writes only after approval.</span>
				Select the readiness summary to record, then dry-run to preview. The approved commit appends it
				to the audit's observation note only; the audit status is never changed and the audit is never
				marked ready or complete.
			</p>

			{#if !ai.setupReference.folder_id || !ai.setupReference.compliance_assessment_id}
				<p class="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-900">
					A Folder ID and a Compliance Assessment ID are required before the deterministic Step 10B
					write. Both come from Step 2 and can also be filled in under "Case reference &amp;
					context" above.
				</p>
			{/if}

			<div class="mt-3 grid gap-2">
				<label class="flex items-start gap-2 rounded border bg-white p-2 text-xs">
					<input type="checkbox" bind:checked={ai.auditReadinessSelected} />
					<span>
						<span class="font-semibold">
							Readiness summary: {humanizeFieldLabel(ai.auditReadinessDraft.readiness_status)}
						</span>
						<span class="text-slate-600">
							&middot; advisory score {ai.auditReadinessDraft.readiness_score}/100
						</span>
					</span>
				</label>
			</div>

			<div class="mt-3 flex flex-wrap items-center gap-3">
				<button
					class="btn btn-sm preset-tonal"
					type="button"
					disabled={ai.loading !== null || !ai.auditReadinessSelected}
					onclick={() => runAuditReadinessCommit(true)}
				>
					{ai.loading === 'audit-readiness-commit-dry-run' ? 'Dry-running...' : 'Step 10B dry-run'}
				</button>
				<label class="flex items-center gap-2 text-xs">
					<input type="checkbox" bind:checked={ai.auditReadinessCommitApproved} />
					<span>I approve the deterministic Step 10B readiness note</span>
				</label>
				<button
					class="btn btn-sm preset-filled-error-500"
					type="button"
					disabled={ai.loading !== null ||
						Boolean(ai.auditReadinessCommitResult) ||
						!ai.auditReadinessCommitApproved ||
						!auditReadinessDryRunSucceeded() ||
						!ai.auditReadinessSelected}
					onclick={() => runAuditReadinessCommit(false)}
				>
					{ai.loading === 'audit-readiness-commit'
						? 'Committing...'
						: 'Approved audit readiness commit'}
				</button>
				<span class="text-xs text-emerald-900">No AI model is used in this write step.</span>
			</div>

			{#if ai.auditReadinessCommitResult}
				<AiOnboardingAlreadyCommitted step="10B" rerun="10A" dryRunReArms />
			{/if}

			{#if ai.auditReadinessCommitDryRun && !auditReadinessDryRunSucceeded()}
				<p class="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-900">
					The last Step 10B dry-run was blocked. Resolve the blocking errors below and run the
					dry-run again before the approved commit.
				</p>
			{/if}

			{#if ai.auditReadinessCommitDryRun}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">
						Step 10B dry-run status: {humanizeFieldLabel(
							ai.auditReadinessCommitDryRun.commit_status
						)}
					</div>
					<p class="text-xs text-slate-700">
						Dry-run only previews the deterministic write. Nothing was written.
					</p>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Rejected: {ai.auditReadinessCommitDryRun.rejected_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Deferred: {ai.auditReadinessCommitDryRun.deferred_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Skipped: {ai.auditReadinessCommitDryRun.skipped_records?.length ?? 0}
						</span>
					</div>
					{#if ai.auditReadinessCommitDryRun.planned_actions?.length}
						<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.auditReadinessCommitDryRun.planned_actions as action}
								<li>
									{action.target_name ?? action.source_temporary_id}:
									{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
									&middot; {action.detail}
								</li>
							{/each}
						</ul>
					{/if}
				</div>
				{#if ai.auditReadinessCommitDryRun.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.auditReadinessCommitDryRun.warnings as warning}
							<li>{warning.detail ?? warning.message ?? warning.code}</li>
						{/each}
					</ul>
				{/if}
				{#if ai.auditReadinessCommitDryRun.blocking_errors?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
						{#each ai.auditReadinessCommitDryRun.blocking_errors as blockingError}
							<li>{blockingError.detail}</li>
						{/each}
					</ul>
				{/if}
			{/if}

			{#if ai.auditReadinessCommitResult}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">
						Step 10B commit status: {humanizeFieldLabel(
							ai.auditReadinessCommitResult.commit_status
						)}
					</div>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
							Recorded: {ai.auditReadinessCommitResult.created_records?.length ?? 0}
						</span>
						<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
							Unchanged: {ai.auditReadinessCommitResult.reused_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Rejected: {ai.auditReadinessCommitResult.rejected_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Deferred: {ai.auditReadinessCommitResult.deferred_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Skipped: {ai.auditReadinessCommitResult.skipped_records?.length ?? 0}
						</span>
						<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
							Warnings: {ai.auditReadinessCommitResult.warnings?.length ?? 0}
						</span>
						<span class="rounded bg-red-100 px-2 py-1 font-semibold text-red-900">
							Blocking errors: {ai.auditReadinessCommitResult.blocking_errors?.length ?? 0}
						</span>
					</div>
					{#if ai.auditReadinessCommitResult.created_records?.length}
						<div class="text-xs font-semibold text-emerald-950">Recorded on</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.auditReadinessCommitResult.created_records as record}
								<li>{record.name} &middot; {humanizeFieldLabel(record.record_type)}</li>
							{/each}
						</ul>
					{/if}
					{#if ai.auditReadinessCommitResult.planned_actions?.length}
						<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.auditReadinessCommitResult.planned_actions as action}
								<li>
									{action.target_name ?? action.source_temporary_id}:
									{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
								</li>
							{/each}
						</ul>
					{/if}
				</div>
				{#if ai.auditReadinessCommitResult.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.auditReadinessCommitResult.warnings as warning}
							<li>{warning.detail ?? warning.message ?? warning.code}</li>
						{/each}
					</ul>
				{/if}
				{#if ai.auditReadinessCommitResult.blocking_errors?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
						{#each ai.auditReadinessCommitResult.blocking_errors as blockingError}
							<li>{blockingError.detail}</li>
						{/each}
					</ul>
				{/if}
			{/if}
		</div>
	{/if}
</section>
