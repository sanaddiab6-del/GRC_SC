<script lang="ts">
	import AiOnboardingAlreadyCommitted from './AiOnboardingAlreadyCommitted.svelte';
	import AiOnboardingPrerequisite from './AiOnboardingPrerequisite.svelte';
	import {
		ai,
		controlEffectivenessDryRunSucceeded,
		controlEffectivenessProviderMode,
		formatConfidence,
		humanizeActionName,
		humanizeFieldLabel,
		humanizeProviderMode,
		runControlEffectivenessCommit,
		runControlEffectivenessSuggestion,
		selectedControlEffectiveness
	} from './aiOnboardingState.svelte';

	/**
	 * Steps 9A and 9B: the control effectiveness judgement and its deterministic write.
	 *
	 * They render on the audit page because Step 9B updates the result and observation of
	 * requirement assessments that already belong to this audit. It never creates a requirement
	 * assessment, never changes the audit status, and never certifies compliance.
	 */
</script>

<section data-testid="ai-onboarding-step-9a">
	{#if !ai.riskScenarioDraft}
		<AiOnboardingPrerequisite
			step="9A"
			requires="8A"
			detail="Run Step 8A before Step 9A, so the effectiveness judgements are drafted against the reviewed risk scenarios."
		/>
	{:else}
		<div class="rounded border border-sky-200 bg-sky-50/60 p-3 text-sm text-sky-950">
			<div class="font-semibold">Step 9A &middot; Control Effectiveness Suggestion</div>
			<p class="mt-1 text-sky-900">
				<span class="font-semibold">AI suggestion only / no database write.</span>
				Step 9A suggests how effective each mapped control appears and what compliance status the evidence
				supports. No requirement assessment is updated, no audit is closed, and no compliance is certified
				in this step.
			</p>
			<div class="mt-3 flex flex-wrap items-center gap-3">
				<button
					class="btn btn-sm preset-filled-primary-500"
					type="button"
					disabled={ai.loading !== null}
					onclick={() => runControlEffectivenessSuggestion()}
				>
					{ai.loading === 'control-effectiveness-suggest'
						? 'Running...'
						: 'Run Local AI Control Effectiveness Suggestion'}
				</button>
				<span class="text-xs text-sky-900">
					AI Provider: {humanizeProviderMode(controlEffectivenessProviderMode())} &middot; No database
					writes occur in Step 9A.
				</span>
			</div>

			{#if ai.controlEffectivenessDraft}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">Step 9A suggestion summary</div>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Overall confidence: {formatConfidence(
								ai.controlEffectivenessDraft.overall_confidence
							)}
						</span>
						<span class="rounded bg-sky-100 px-2 py-1 font-semibold text-sky-900">
							Judgements: {ai.controlEffectivenessDraft.control_effectiveness_suggestions?.length ??
								0}
						</span>
						<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
							Warnings: {ai.controlEffectivenessDraft.warnings?.length ?? 0}
						</span>
					</div>
				</div>

				{#if ai.controlEffectivenessDraft.control_effectiveness_suggestions?.length}
					<div class="mt-3">
						<div class="font-semibold text-sky-950">
							Control effectiveness suggestions ({ai.controlEffectivenessDraft
								.control_effectiveness_suggestions.length})
						</div>
						<p class="text-xs text-sky-900">
							Advisory judgements for auditor review. They are not compliance conclusions.
						</p>
						<div class="mt-2 grid gap-2">
							{#each ai.controlEffectivenessDraft.control_effectiveness_suggestions as suggestion}
								<div class="rounded border bg-white p-3 text-xs text-slate-800">
									<div class="flex flex-wrap items-start justify-between gap-2">
										<div class="text-sm font-semibold text-slate-950">
											{#if suggestion.framework_control_code}
												<span class="text-slate-600">{suggestion.framework_control_code}</span>
												&middot;
											{/if}
											{suggestion.framework_control_title}
										</div>
										<div class="flex flex-wrap gap-1">
											<span class="rounded bg-sky-100 px-2 py-0.5 font-semibold text-sky-900">
												{humanizeFieldLabel(suggestion.suggested_effectiveness)}
											</span>
											<span class="rounded bg-orange-100 px-2 py-0.5 font-semibold text-orange-900">
												{humanizeFieldLabel(suggestion.suggested_compliance_status)}
											</span>
											<span class="rounded bg-slate-100 px-2 py-0.5 font-semibold text-slate-700">
												Confidence: {formatConfidence(suggestion.confidence)}
											</span>
											{#if suggestion.review_status}
												<span
													class="rounded bg-violet-100 px-2 py-0.5 font-semibold text-violet-900"
												>
													{humanizeFieldLabel(suggestion.review_status)}
												</span>
											{/if}
										</div>
									</div>
									{#if suggestion.evidence_summary}
										<div class="mt-1">
											<span class="font-semibold">Evidence summary:</span>
											{suggestion.evidence_summary}
										</div>
									{/if}
									{#if suggestion.gaps?.length}
										<div class="mt-1">
											<span class="font-semibold">Gaps:</span>
											<ul class="list-disc pl-5">
												{#each suggestion.gaps as gap}
													<li>{gap}</li>
												{/each}
											</ul>
										</div>
									{/if}
									{#if suggestion.recommended_auditor_action}
										<div class="mt-1">
											<span class="font-semibold">Recommended auditor action:</span>
											{suggestion.recommended_auditor_action}
										</div>
									{/if}
									{#if suggestion.rationale}
										<div class="mt-1">
											<span class="font-semibold">Rationale:</span>
											{suggestion.rationale}
										</div>
									{/if}
								</div>
							{/each}
						</div>
					</div>
				{/if}

				{#if ai.controlEffectivenessDraft.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.controlEffectivenessDraft.warnings as warning}
							<li>{warning.message ?? warning.detail ?? warning.code}</li>
						{/each}
					</ul>
				{/if}

				{#if ai.controlEffectivenessDraft.ambiguity_flags?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.controlEffectivenessDraft.ambiguity_flags as flag}
							<li>{flag.message ?? flag.code}</li>
						{/each}
					</ul>
				{/if}
			{/if}
		</div>
	{/if}
</section>

<section data-testid="ai-onboarding-step-9b">
	{#if !ai.controlEffectivenessDraft?.control_effectiveness_suggestions?.length}
		<AiOnboardingPrerequisite
			step="9B"
			requires="9A"
			detail="Run Step 9A before Step 9B. Step 9B needs at least one Step 9A control effectiveness judgement."
		/>
	{:else}
		<div class="rounded border border-emerald-300 bg-emerald-50/60 p-3 text-sm text-emerald-950">
			<div class="font-semibold">Step 9B &middot; Control Effectiveness Commit</div>
			<p class="mt-1 text-emerald-900">
				<span class="font-semibold">No AI model is used / writes only after approval.</span>
				Select the Step 9A judgements to record, then dry-run to preview. The approved commit updates
				only the result and observation of existing requirement assessments; it never changes the audit
				status and never certifies compliance.
			</p>

			{#if !ai.setupReference.folder_id || !ai.setupReference.compliance_assessment_id}
				<p class="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-900">
					A Folder ID and a Compliance Assessment ID are required before the deterministic Step 9B
					write. Both come from Step 2 and can also be filled in under "Case reference &amp;
					context" above.
				</p>
			{/if}

			<div class="mt-3 grid gap-2">
				{#each ai.controlEffectivenessDraft.control_effectiveness_suggestions as suggestion}
					<label class="flex items-start gap-2 rounded border bg-white p-2 text-xs">
						<input
							type="checkbox"
							bind:checked={ai.selectedControlEffectivenessIds[suggestion.temporary_id]}
						/>
						<span>
							<span class="font-semibold">
								{#if suggestion.framework_control_code}
									{suggestion.framework_control_code} &middot;
								{/if}
								{suggestion.framework_control_title}
							</span>
							<span class="text-slate-600">
								&middot; {humanizeFieldLabel(suggestion.suggested_compliance_status)} &middot; Confidence:
								{formatConfidence(suggestion.confidence)}
							</span>
						</span>
					</label>
				{/each}
			</div>

			<div class="mt-3 flex flex-wrap items-center gap-3">
				<button
					class="btn btn-sm preset-tonal"
					type="button"
					disabled={ai.loading !== null || !selectedControlEffectiveness().length}
					onclick={() => runControlEffectivenessCommit(true)}
				>
					{ai.loading === 'control-effectiveness-commit-dry-run'
						? 'Dry-running...'
						: 'Step 9B dry-run'}
				</button>
				<label class="flex items-center gap-2 text-xs">
					<input type="checkbox" bind:checked={ai.controlEffectivenessCommitApproved} />
					<span>
						I approve deterministic Step 9B decisions for selected control effectiveness judgements
					</span>
				</label>
				<button
					class="btn btn-sm preset-filled-error-500"
					type="button"
					disabled={ai.loading !== null ||
						Boolean(ai.controlEffectivenessCommitResult) ||
						!ai.controlEffectivenessCommitApproved ||
						!controlEffectivenessDryRunSucceeded() ||
						!selectedControlEffectiveness().length}
					onclick={() => runControlEffectivenessCommit(false)}
				>
					{ai.loading === 'control-effectiveness-commit'
						? 'Committing...'
						: 'Approved control effectiveness commit'}
				</button>
				<span class="text-xs text-emerald-900">No AI model is used in this write step.</span>
			</div>

			{#if ai.controlEffectivenessCommitResult}
				<AiOnboardingAlreadyCommitted step="9B" rerun="9A" dryRunReArms />
			{/if}

			{#if ai.controlEffectivenessCommitDryRun && !controlEffectivenessDryRunSucceeded() && selectedControlEffectiveness().length}
				<p class="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-900">
					The selection changed after the last dry-run, or the dry-run was blocked. Run the Step 9B
					dry-run again before the approved commit.
				</p>
			{/if}

			{#if ai.controlEffectivenessCommitDryRun}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">
						Step 9B dry-run status: {humanizeFieldLabel(
							ai.controlEffectivenessCommitDryRun.commit_status
						)}
					</div>
					<p class="text-xs text-slate-700">
						Dry-run only previews the deterministic write. Nothing was written.
					</p>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Rejected: {ai.controlEffectivenessCommitDryRun.rejected_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Deferred: {ai.controlEffectivenessCommitDryRun.deferred_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Skipped: {ai.controlEffectivenessCommitDryRun.skipped_records?.length ?? 0}
						</span>
					</div>
					{#if ai.controlEffectivenessCommitDryRun.planned_actions?.length}
						<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.controlEffectivenessCommitDryRun.planned_actions as action}
								<li>
									{action.target_name ?? action.source_temporary_id}:
									{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
									&middot; {action.detail}
								</li>
							{/each}
						</ul>
					{/if}
				</div>
				{#if ai.controlEffectivenessCommitDryRun.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.controlEffectivenessCommitDryRun.warnings as warning}
							<li>{warning.detail ?? warning.message ?? warning.code}</li>
						{/each}
					</ul>
				{/if}
				{#if ai.controlEffectivenessCommitDryRun.blocking_errors?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
						{#each ai.controlEffectivenessCommitDryRun.blocking_errors as blockingError}
							<li>{blockingError.detail}</li>
						{/each}
					</ul>
				{/if}
			{/if}

			{#if ai.controlEffectivenessCommitResult}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">
						Step 9B commit status: {humanizeFieldLabel(
							ai.controlEffectivenessCommitResult.commit_status
						)}
					</div>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
							Recorded: {ai.controlEffectivenessCommitResult.created_records?.length ?? 0}
						</span>
						<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
							Unchanged: {ai.controlEffectivenessCommitResult.reused_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Rejected: {ai.controlEffectivenessCommitResult.rejected_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Deferred: {ai.controlEffectivenessCommitResult.deferred_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Skipped: {ai.controlEffectivenessCommitResult.skipped_records?.length ?? 0}
						</span>
						<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
							Warnings: {ai.controlEffectivenessCommitResult.warnings?.length ?? 0}
						</span>
						<span class="rounded bg-red-100 px-2 py-1 font-semibold text-red-900">
							Blocking errors: {ai.controlEffectivenessCommitResult.blocking_errors?.length ?? 0}
						</span>
					</div>
					{#if ai.controlEffectivenessCommitResult.created_records?.length}
						<div class="text-xs font-semibold text-emerald-950">
							Updated requirement assessments
						</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.controlEffectivenessCommitResult.created_records as record}
								<li>{record.name} &middot; result: {humanizeFieldLabel(record.result)}</li>
							{/each}
						</ul>
					{/if}
					{#if ai.controlEffectivenessCommitResult.reused_records?.length}
						<div class="text-xs font-semibold text-emerald-950">Unchanged (already recorded)</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.controlEffectivenessCommitResult.reused_records as record}
								<li>{record.name}</li>
							{/each}
						</ul>
					{/if}
					{#if ai.controlEffectivenessCommitResult.planned_actions?.length}
						<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.controlEffectivenessCommitResult.planned_actions as action}
								<li>
									{action.target_name ?? action.source_temporary_id}:
									{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
								</li>
							{/each}
						</ul>
					{/if}
				</div>
				{#if ai.controlEffectivenessCommitResult.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.controlEffectivenessCommitResult.warnings as warning}
							<li>{warning.detail ?? warning.message ?? warning.code}</li>
						{/each}
					</ul>
				{/if}
				{#if ai.controlEffectivenessCommitResult.blocking_errors?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
						{#each ai.controlEffectivenessCommitResult.blocking_errors as blockingError}
							<li>{blockingError.detail}</li>
						{/each}
					</ul>
				{/if}
			{/if}
		</div>
	{/if}
</section>
