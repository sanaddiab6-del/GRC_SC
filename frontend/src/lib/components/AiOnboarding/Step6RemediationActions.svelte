<script lang="ts">
	import AiOnboardingAlreadyCommitted from './AiOnboardingAlreadyCommitted.svelte';
	import AiOnboardingPrerequisite from './AiOnboardingPrerequisite.svelte';
	import {
		ai,
		formatConfidence,
		humanizeActionName,
		humanizeFieldLabel,
		humanizeProviderMode,
		remediationActionProviderMode,
		remediationDryRunSucceeded,
		remediationPriorityBadgeClass,
		runRemediationActionCommit,
		runRemediationActionSuggestion,
		selectedRemediationActions
	} from './aiOnboardingState.svelte';

	/**
	 * Steps 6A and 6B: the remediation action suggestion and its deterministic write.
	 *
	 * They render on the Applied controls page because Step 6B creates AppliedControl records
	 * (the platform's remediation action). Step 6A reads the Step 5A preliminary findings out of
	 * the shared workflow state, so the user does not have to go back to Evidences for it.
	 */
</script>

<section data-testid="ai-onboarding-step-6a">
	{#if !ai.evidenceFindingDraft}
		<AiOnboardingPrerequisite
			step="6A"
			requires="5A"
			detail="Step 6A needs at least one Step 5A preliminary finding or one known weakness."
		/>
	{:else}
		<div class="rounded border border-violet-200 bg-violet-50/60 p-3 text-sm text-violet-950">
			<div class="font-semibold">Step 6A &middot; Remediation Action Suggestion</div>
			<p class="mt-1 text-violet-900">
				<span class="font-semibold">AI suggestion only / no database write.</span>
				Step 6A drafts remediation actions for review. No remediation records are created in this step.
			</p>
			<div class="mt-3 flex flex-wrap items-center gap-3">
				<button
					class="btn btn-sm preset-filled-primary-500"
					type="button"
					disabled={ai.loading !== null}
					onclick={() => runRemediationActionSuggestion()}
				>
					{ai.loading === 'remediation-suggest'
						? 'Running...'
						: 'Run Local AI Remediation Suggestion'}
				</button>
				<span class="text-xs text-violet-900">
					AI Provider: {humanizeProviderMode(remediationActionProviderMode())} &middot; No database writes
					occur in Step 6A.
				</span>
			</div>

			{#if ai.remediationActionDraft}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">Step 6A suggestion summary</div>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Overall confidence: {formatConfidence(ai.remediationActionDraft.overall_confidence)}
						</span>
						<span class="rounded bg-violet-100 px-2 py-1 font-semibold text-violet-900">
							Remediation actions: {ai.remediationActionDraft.remediation_actions?.length ?? 0}
						</span>
						<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
							Warnings: {ai.remediationActionDraft.warnings?.length ?? 0}
						</span>
					</div>
				</div>

				{#if ai.remediationActionDraft.remediation_actions?.length}
					<div class="mt-3">
						<div class="font-semibold text-violet-950">
							Remediation actions ({ai.remediationActionDraft.remediation_actions.length})
						</div>
						<p class="text-xs text-violet-900">
							Corrective actions the AI suggests for the preliminary findings. Advisory drafts only.
						</p>
						<div class="mt-2 grid gap-2">
							{#each ai.remediationActionDraft.remediation_actions as action}
								<div class="rounded border bg-white p-3 text-xs text-slate-800">
									<div class="flex flex-wrap items-start justify-between gap-2">
										<div class="text-sm font-semibold text-slate-950">{action.title}</div>
										<div class="flex flex-wrap gap-1">
											{#if action.priority}
												<span
													class="rounded px-2 py-0.5 font-semibold {remediationPriorityBadgeClass(
														action.priority
													)}"
												>
													Priority: {humanizeFieldLabel(action.priority)}
												</span>
											{/if}
											<span class="rounded bg-slate-100 px-2 py-0.5 font-semibold text-slate-700">
												Confidence: {formatConfidence(action.confidence)}
											</span>
											{#if action.review_status}
												<span
													class="rounded bg-violet-100 px-2 py-0.5 font-semibold text-violet-900"
												>
													{humanizeFieldLabel(action.review_status)}
												</span>
											{/if}
										</div>
									</div>
									<div class="mt-1 flex flex-wrap gap-3">
										{#if action.suggested_owner}
											<div>
												<span class="font-semibold">Suggested owner:</span>
												{action.suggested_owner}
											</div>
										{/if}
										{#if action.target_timeline}
											<div>
												<span class="font-semibold">Target timeline:</span>
												{action.target_timeline}
											</div>
										{/if}
									</div>
									{#if action.description}
										<div class="mt-1 text-slate-700">{action.description}</div>
									{/if}
									{#if action.rationale}
										<div class="mt-1">
											<span class="font-semibold">Rationale:</span>
											{action.rationale}
										</div>
									{/if}
									{#if action.linked_finding_title || action.linked_finding_reference}
										<div class="mt-1">
											<span class="font-semibold">Linked finding:</span>
											{action.linked_finding_title || action.linked_finding_reference}
										</div>
									{/if}
									{#if action.linked_asset_title || action.linked_asset_reference}
										<div class="mt-1">
											<span class="font-semibold">Linked asset:</span>
											{action.linked_asset_title || action.linked_asset_reference}
										</div>
									{/if}
									{#if action.linked_control_title || action.linked_control_reference}
										<div class="mt-1">
											<span class="font-semibold">Linked control:</span>
											{action.linked_control_title || action.linked_control_reference}
										</div>
									{/if}
									{#if action.success_criteria?.length}
										<div class="mt-1">
											<span class="font-semibold">Success criteria:</span>
											<ul class="list-disc pl-5">
												{#each action.success_criteria as criterion}
													<li>{criterion}</li>
												{/each}
											</ul>
										</div>
									{/if}
									{#if action.required_follow_up_evidence?.length}
										<div class="mt-1">
											<span class="font-semibold">Required follow-up evidence:</span>
											<ul class="list-disc pl-5">
												{#each action.required_follow_up_evidence as evidenceItem}
													<li>{evidenceItem}</li>
												{/each}
											</ul>
										</div>
									{/if}
								</div>
							{/each}
						</div>
					</div>
				{/if}

				{#if ai.remediationActionDraft.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.remediationActionDraft.warnings as warning}
							<li>{warning.message ?? warning.detail ?? warning.code}</li>
						{/each}
					</ul>
				{/if}

				{#if ai.remediationActionDraft.ambiguity_flags?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.remediationActionDraft.ambiguity_flags as flag}
							<li>{flag.message ?? flag.code}</li>
						{/each}
					</ul>
				{/if}
			{/if}
		</div>
	{/if}
</section>

<section data-testid="ai-onboarding-step-6b">
	{#if !ai.remediationActionDraft?.remediation_actions?.length}
		<AiOnboardingPrerequisite
			step="6B"
			requires="6A"
			detail="Run Step 6A before Step 6B. Step 6B needs at least one Step 6A remediation action."
		/>
	{:else}
		<div class="rounded border border-emerald-300 bg-emerald-50/60 p-3 text-sm text-emerald-950">
			<div class="font-semibold">Step 6B &middot; Remediation Action Commit</div>
			<p class="mt-1 text-emerald-900">
				<span class="font-semibold">No AI model is used / writes only after approval.</span>
				Select the Step 6A remediation actions to keep, then dry-run to preview. Dry-run does not write.
				The approved commit writes deterministic records only for selected and approved remediation actions.
			</p>

			{#if !ai.setupReference.folder_id}
				<p class="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-900">
					A Folder ID is required before the deterministic Step 6B write. It comes from Step 2 and
					can also be filled in under "Case reference &amp; context" above.
				</p>
			{/if}

			<div class="mt-3 grid gap-2">
				{#each ai.remediationActionDraft.remediation_actions as action}
					<label class="flex items-start gap-2 rounded border bg-white p-2 text-xs">
						<input
							type="checkbox"
							bind:checked={ai.selectedRemediationActionIds[action.temporary_id]}
						/>
						<span>
							<span class="font-semibold">{action.title}</span>
							<span class="text-slate-600">
								&middot; Priority: {humanizeFieldLabel(action.priority)} &middot; Confidence: {formatConfidence(
									action.confidence
								)}
							</span>
						</span>
					</label>
				{/each}
			</div>

			<div class="mt-3 flex flex-wrap items-center gap-3">
				<button
					class="btn btn-sm preset-tonal"
					type="button"
					disabled={ai.loading !== null || !selectedRemediationActions().length}
					onclick={() => runRemediationActionCommit(true)}
				>
					{ai.loading === 'remediation-commit-dry-run' ? 'Dry-running...' : 'Step 6B dry-run'}
				</button>
				<label class="flex items-center gap-2 text-xs">
					<input type="checkbox" bind:checked={ai.remediationCommitApproved} />
					<span>I approve deterministic Step 6B decisions for selected remediation actions</span>
				</label>
				<button
					class="btn btn-sm preset-filled-error-500"
					type="button"
					disabled={ai.loading !== null ||
						Boolean(ai.remediationCommitResult) ||
						!ai.remediationCommitApproved ||
						!remediationDryRunSucceeded() ||
						!selectedRemediationActions().length}
					onclick={() => runRemediationActionCommit(false)}
				>
					{ai.loading === 'remediation-commit'
						? 'Committing...'
						: 'Approved remediation action commit'}
				</button>
				<span class="text-xs text-emerald-900">No AI model is used in this write step.</span>
			</div>

			{#if ai.remediationCommitResult}
				<AiOnboardingAlreadyCommitted step="6B" rerun="6A" dryRunReArms />
			{/if}

			{#if ai.remediationCommitDryRun && !remediationDryRunSucceeded() && selectedRemediationActions().length}
				<p class="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-900">
					The selection changed after the last dry-run, or the dry-run was blocked. Run the Step 6B
					dry-run again before the approved commit.
				</p>
			{/if}

			{#if ai.remediationCommitDryRun}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">
						Step 6B dry-run status: {humanizeFieldLabel(ai.remediationCommitDryRun.commit_status)}
					</div>
					<p class="text-xs text-slate-700">
						Dry-run only previews the deterministic write. Nothing was written.
					</p>
					{#if ai.remediationCommitDryRun.planned_actions?.length}
						<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.remediationCommitDryRun.planned_actions as action}
								<li>
									{action.target_name ?? action.source_temporary_id}:
									{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
									&middot; {action.detail}
								</li>
							{/each}
						</ul>
					{/if}
					{#if ai.remediationCommitDryRun.rejected_records?.length || ai.remediationCommitDryRun.deferred_records?.length || ai.remediationCommitDryRun.skipped_records?.length}
						<div class="flex flex-wrap gap-2 text-xs">
							<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
								Rejected: {ai.remediationCommitDryRun.rejected_records?.length ?? 0}
							</span>
							<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
								Deferred: {ai.remediationCommitDryRun.deferred_records?.length ?? 0}
							</span>
							<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
								Skipped: {ai.remediationCommitDryRun.skipped_records?.length ?? 0}
							</span>
						</div>
					{/if}
				</div>
				{#if ai.remediationCommitDryRun.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.remediationCommitDryRun.warnings as warning}
							<li>{warning.detail ?? warning.message ?? warning.code}</li>
						{/each}
					</ul>
				{/if}
				{#if ai.remediationCommitDryRun.blocking_errors?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
						{#each ai.remediationCommitDryRun.blocking_errors as blockingError}
							<li>{blockingError.detail}</li>
						{/each}
					</ul>
				{/if}
			{/if}

			{#if ai.remediationCommitResult}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">
						Step 6B commit status: {humanizeFieldLabel(ai.remediationCommitResult.commit_status)}
					</div>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
							Created: {ai.remediationCommitResult.created_records?.length ?? 0}
						</span>
						<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
							Reused: {ai.remediationCommitResult.reused_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Rejected: {ai.remediationCommitResult.rejected_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Deferred: {ai.remediationCommitResult.deferred_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Skipped: {ai.remediationCommitResult.skipped_records?.length ?? 0}
						</span>
						<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
							Warnings: {ai.remediationCommitResult.warnings?.length ?? 0}
						</span>
						<span class="rounded bg-red-100 px-2 py-1 font-semibold text-red-900">
							Blocking errors: {ai.remediationCommitResult.blocking_errors?.length ?? 0}
						</span>
					</div>
					{#if ai.remediationCommitResult.created_records?.length}
						<div class="text-xs font-semibold text-emerald-950">Created records</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.remediationCommitResult.created_records as record}
								<li>{humanizeFieldLabel(record.record_type)}: {record.name}</li>
							{/each}
						</ul>
					{/if}
					{#if ai.remediationCommitResult.reused_records?.length}
						<div class="text-xs font-semibold text-emerald-950">Reused existing records</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.remediationCommitResult.reused_records as record}
								<li>{humanizeFieldLabel(record.record_type)}: {record.name}</li>
							{/each}
						</ul>
					{/if}
					{#if ai.remediationCommitResult.planned_actions?.length}
						<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.remediationCommitResult.planned_actions as action}
								<li>
									{action.target_name ?? action.source_temporary_id}:
									{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
								</li>
							{/each}
						</ul>
					{/if}
				</div>
				{#if ai.remediationCommitResult.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.remediationCommitResult.warnings as warning}
							<li>{warning.detail ?? warning.message ?? warning.code}</li>
						{/each}
					</ul>
				{/if}
				{#if ai.remediationCommitResult.blocking_errors?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
						{#each ai.remediationCommitResult.blocking_errors as blockingError}
							<li>{blockingError.detail}</li>
						{/each}
					</ul>
				{/if}
			{/if}
		</div>
	{/if}
</section>
