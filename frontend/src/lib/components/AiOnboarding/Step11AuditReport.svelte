<script lang="ts">
	import AiOnboardingAlreadyCommitted from './AiOnboardingAlreadyCommitted.svelte';
	import AiOnboardingPrerequisite from './AiOnboardingPrerequisite.svelte';
	import {
		ai,
		auditReportDryRunSucceeded,
		auditReportProviderMode,
		formatConfidence,
		humanizeActionName,
		humanizeFieldLabel,
		humanizeProviderMode,
		runAuditReportCommit,
		runAuditReportSuggestion
	} from './aiOnboardingState.svelte';

	/**
	 * Steps 11A and 11B: the management / audit report draft and its deterministic save.
	 *
	 * They render on the audit page because the report summarizes this audit, and Step 11B stores
	 * it as a draft document scoped to the audit's folder. The report is never marked final or
	 * published and the audit status is never changed.
	 */
</script>

<section data-testid="ai-onboarding-step-11a">
	{#if !ai.auditReadinessDraft}
		<AiOnboardingPrerequisite
			step="11A"
			requires="10A"
			detail="Run Step 10A before Step 11A, so the report draft is written against the reviewed readiness summary."
		/>
	{:else}
		<div class="rounded border border-sky-200 bg-sky-50/60 p-3 text-sm text-sky-950">
			<div class="font-semibold">Step 11A &middot; Management / Audit Report Draft</div>
			<p class="mt-1 text-sky-900">
				<span class="font-semibold">AI draft only / no database write.</span>
				Step 11A drafts the management report from the reviewed onboarding output. It is never a final
				audit opinion, a compliance certification, or a regulator-approved result.
			</p>
			<div class="mt-3 flex flex-wrap items-center gap-3">
				<button
					class="btn btn-sm preset-filled-primary-500"
					type="button"
					disabled={ai.loading !== null}
					onclick={() => runAuditReportSuggestion()}
				>
					{ai.loading === 'audit-report-suggest' ? 'Running...' : 'Run Local AI Report Draft'}
				</button>
				<span class="text-xs text-sky-900">
					AI Provider: {humanizeProviderMode(auditReportProviderMode())} &middot; No database writes occur
					in Step 11A.
				</span>
			</div>

			{#if ai.auditReportDraft}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">{ai.auditReportDraft.report_title}</div>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Overall confidence: {formatConfidence(ai.auditReportDraft.overall_confidence)}
						</span>
						<span class="rounded bg-sky-100 px-2 py-1 font-semibold text-sky-900">
							Sections: {ai.auditReportDraft.report_sections?.length ?? 0}
						</span>
						<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
							Warnings: {ai.auditReportDraft.warnings?.length ?? 0}
						</span>
						{#if ai.auditReportDraft.review_status}
							<span class="rounded bg-violet-100 px-2 py-1 font-semibold text-violet-900">
								{humanizeFieldLabel(ai.auditReportDraft.review_status)}
							</span>
						{/if}
					</div>
					{#if ai.auditReportDraft.executive_summary}
						<p class="text-xs text-slate-800">{ai.auditReportDraft.executive_summary}</p>
					{/if}
				</div>

				{#if ai.auditReportDraft.report_sections?.length}
					<div class="mt-3 grid gap-2">
						{#each ai.auditReportDraft.report_sections as section}
							<div class="rounded border bg-white p-3 text-xs text-slate-800">
								<div class="flex flex-wrap items-start justify-between gap-2">
									<div class="text-sm font-semibold text-slate-950">{section.heading}</div>
									<span class="rounded bg-slate-100 px-2 py-0.5 font-semibold text-slate-700">
										Confidence: {formatConfidence(section.confidence)}
									</span>
								</div>
								{#if section.content}
									<div class="mt-1 whitespace-pre-line text-slate-700">{section.content}</div>
								{/if}
								{#if section.source_items?.length}
									<div class="mt-1">
										<span class="font-semibold">Source items:</span>
										<ul class="list-disc pl-5">
											{#each section.source_items as sourceItem}
												<li>{sourceItem}</li>
											{/each}
										</ul>
									</div>
								{/if}
							</div>
						{/each}
					</div>
				{/if}

				{#if ai.auditReportDraft.limitations?.length}
					<div class="mt-3 rounded border border-amber-300 bg-amber-50 p-3 text-xs text-amber-900">
						<div class="font-semibold">Limitations / human review required</div>
						<ul class="mt-1 list-disc pl-5">
							{#each ai.auditReportDraft.limitations as limitation}
								<li>{limitation}</li>
							{/each}
						</ul>
					</div>
				{/if}

				{#if ai.auditReportDraft.recommended_next_steps?.length}
					<div class="mt-3 rounded border bg-white p-3 text-xs text-slate-800">
						<div class="font-semibold text-slate-950">Recommended next steps</div>
						<ul class="mt-1 list-disc pl-5">
							{#each ai.auditReportDraft.recommended_next_steps as nextStep}
								<li>{nextStep}</li>
							{/each}
						</ul>
					</div>
				{/if}

				{#if ai.auditReportDraft.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.auditReportDraft.warnings as warning}
							<li>{warning.message ?? warning.detail ?? warning.code}</li>
						{/each}
					</ul>
				{/if}

				{#if ai.auditReportDraft.ambiguity_flags?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.auditReportDraft.ambiguity_flags as flag}
							<li>{flag.message ?? flag.code}</li>
						{/each}
					</ul>
				{/if}
			{/if}
		</div>
	{/if}
</section>

<section data-testid="ai-onboarding-step-11b">
	{#if !ai.auditReportDraft}
		<AiOnboardingPrerequisite step="11B" requires="11A" detail="Run Step 11A before Step 11B." />
	{:else}
		<div class="rounded border border-emerald-300 bg-emerald-50/60 p-3 text-sm text-emerald-950">
			<div class="font-semibold">Step 11B &middot; Report Save Commit</div>
			<p class="mt-1 text-emerald-900">
				<span class="font-semibold">No AI model is used / writes only after approval.</span>
				Select the report draft to save, then dry-run to preview. The approved commit stores it as a draft
				document; the report is never marked final or published and the audit status is never changed.
			</p>

			{#if !ai.setupReference.folder_id}
				<p class="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-900">
					A Folder ID is required before the deterministic Step 11B write. It comes from Step 2 and
					can also be filled in under "Case reference &amp; context" above.
				</p>
			{/if}

			{#if !(ai.auditReportDraft.limitations ?? []).length}
				<p class="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-900">
					The report draft must carry its limitations before it can be saved. Re-run Step 11A to get
					a draft that states them.
				</p>
			{/if}

			<div class="mt-3 grid gap-2">
				<label class="flex items-start gap-2 rounded border bg-white p-2 text-xs">
					<input type="checkbox" bind:checked={ai.auditReportSelected} />
					<span>
						<span class="font-semibold">{ai.auditReportDraft.report_title}</span>
						<span class="text-slate-600">
							&middot; {ai.auditReportDraft.report_sections?.length ?? 0} section(s) &middot; saved as
							a draft document
						</span>
					</span>
				</label>
			</div>

			<div class="mt-3 flex flex-wrap items-center gap-3">
				<button
					class="btn btn-sm preset-tonal"
					type="button"
					disabled={ai.loading !== null || !ai.auditReportSelected}
					onclick={() => runAuditReportCommit(true)}
				>
					{ai.loading === 'audit-report-commit-dry-run' ? 'Dry-running...' : 'Step 11B dry-run'}
				</button>
				<label class="flex items-center gap-2 text-xs">
					<input type="checkbox" bind:checked={ai.auditReportCommitApproved} />
					<span>I approve saving the deterministic Step 11B report draft</span>
				</label>
				<button
					class="btn btn-sm preset-filled-error-500"
					type="button"
					disabled={ai.loading !== null ||
						Boolean(ai.auditReportCommitResult) ||
						!ai.auditReportCommitApproved ||
						!auditReportDryRunSucceeded() ||
						!ai.auditReportSelected}
					onclick={() => runAuditReportCommit(false)}
				>
					{ai.loading === 'audit-report-commit' ? 'Committing...' : 'Approved report save commit'}
				</button>
				<span class="text-xs text-emerald-900">No AI model is used in this write step.</span>
			</div>

			{#if ai.auditReportCommitResult}
				<AiOnboardingAlreadyCommitted step="11B" rerun="11A" dryRunReArms />
			{/if}

			{#if ai.auditReportCommitDryRun && !auditReportDryRunSucceeded()}
				<p class="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-900">
					The last Step 11B dry-run was blocked. Resolve the blocking errors below and run the
					dry-run again before the approved commit.
				</p>
			{/if}

			{#if ai.auditReportCommitDryRun}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">
						Step 11B dry-run status: {humanizeFieldLabel(ai.auditReportCommitDryRun.commit_status)}
					</div>
					<p class="text-xs text-slate-700">
						Dry-run only previews the deterministic write. Nothing was written.
					</p>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Rejected: {ai.auditReportCommitDryRun.rejected_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Deferred: {ai.auditReportCommitDryRun.deferred_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Skipped: {ai.auditReportCommitDryRun.skipped_records?.length ?? 0}
						</span>
					</div>
					{#if ai.auditReportCommitDryRun.planned_actions?.length}
						<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.auditReportCommitDryRun.planned_actions as action}
								<li>
									{action.target_name ?? action.source_temporary_id}:
									{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
									&middot; {action.detail}
								</li>
							{/each}
						</ul>
					{/if}
				</div>
				{#if ai.auditReportCommitDryRun.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.auditReportCommitDryRun.warnings as warning}
							<li>{warning.detail ?? warning.message ?? warning.code}</li>
						{/each}
					</ul>
				{/if}
				{#if ai.auditReportCommitDryRun.blocking_errors?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
						{#each ai.auditReportCommitDryRun.blocking_errors as blockingError}
							<li>{blockingError.detail}</li>
						{/each}
					</ul>
				{/if}
			{/if}

			{#if ai.auditReportCommitResult}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">
						Step 11B commit status: {humanizeFieldLabel(ai.auditReportCommitResult.commit_status)}
					</div>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
							Created: {ai.auditReportCommitResult.created_records?.length ?? 0}
						</span>
						<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
							Reused: {ai.auditReportCommitResult.reused_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Rejected: {ai.auditReportCommitResult.rejected_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Deferred: {ai.auditReportCommitResult.deferred_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Skipped: {ai.auditReportCommitResult.skipped_records?.length ?? 0}
						</span>
						<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
							Warnings: {ai.auditReportCommitResult.warnings?.length ?? 0}
						</span>
						<span class="rounded bg-red-100 px-2 py-1 font-semibold text-red-900">
							Blocking errors: {ai.auditReportCommitResult.blocking_errors?.length ?? 0}
						</span>
					</div>
					{#if ai.auditReportCommitResult.created_records?.length}
						<div class="text-xs font-semibold text-emerald-950">Saved report documents</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.auditReportCommitResult.created_records as record}
								<li>{record.name} &middot; status: {humanizeFieldLabel(record.status)}</li>
							{/each}
						</ul>
					{/if}
					{#if ai.auditReportCommitResult.reused_records?.length}
						<div class="text-xs font-semibold text-emerald-950">Reused existing documents</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.auditReportCommitResult.reused_records as record}
								<li>{record.name}</li>
							{/each}
						</ul>
					{/if}
					{#if ai.auditReportCommitResult.planned_actions?.length}
						<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.auditReportCommitResult.planned_actions as action}
								<li>
									{action.target_name ?? action.source_temporary_id}:
									{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
								</li>
							{/each}
						</ul>
					{/if}
				</div>
				{#if ai.auditReportCommitResult.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.auditReportCommitResult.warnings as warning}
							<li>{warning.detail ?? warning.message ?? warning.code}</li>
						{/each}
					</ul>
				{/if}
				{#if ai.auditReportCommitResult.blocking_errors?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
						{#each ai.auditReportCommitResult.blocking_errors as blockingError}
							<li>{blockingError.detail}</li>
						{/each}
					</ul>
				{/if}
			{/if}
		</div>
	{/if}
</section>
