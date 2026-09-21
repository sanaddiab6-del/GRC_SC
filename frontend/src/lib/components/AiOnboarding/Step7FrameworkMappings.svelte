<script lang="ts">
	import AiOnboardingAlreadyCommitted from './AiOnboardingAlreadyCommitted.svelte';
	import AiOnboardingPrerequisite from './AiOnboardingPrerequisite.svelte';
	import {
		ai,
		formatConfidence,
		frameworkControlMappingProviderMode,
		frameworkMappingDryRunSucceeded,
		frameworkMappingUsedCsvFallback,
		humanizeActionName,
		humanizeFieldLabel,
		humanizeProviderMode,
		runFrameworkControlMappingCommit,
		runFrameworkControlMappingSuggestion,
		selectedFrameworkMappings
	} from './aiOnboardingState.svelte';

	/**
	 * Steps 7A and 7B: the framework control mapping suggestion and its deterministic write.
	 *
	 * They render on the audit (compliance assessment) page because Step 7B pairs the mapped
	 * framework controls with this audit by creating RequirementAssessment rows on it. Step 7B
	 * never creates a framework control.
	 */
</script>

<section data-testid="ai-onboarding-step-7a">
	{#if !ai.remediationActionDraft}
		<AiOnboardingPrerequisite
			step="7A"
			requires="6A"
			detail="Run Step 6A before Step 7A, so the framework mapping can be drafted against the reviewed remediation actions."
		/>
	{:else}
		<div class="rounded border border-sky-200 bg-sky-50/60 p-3 text-sm text-sky-950">
			<div class="font-semibold">Step 7A &middot; Framework Control Mapping Suggestion</div>
			<p class="mt-1 text-sky-900">
				<span class="font-semibold">AI suggestion only / no database write.</span>
				Step 7A suggests mappings to existing framework controls for review. No framework controls or
				mappings are created in this step.
			</p>
			<div class="mt-3 flex flex-wrap items-center gap-3">
				<button
					class="btn btn-sm preset-filled-primary-500"
					type="button"
					disabled={ai.loading !== null}
					onclick={() => runFrameworkControlMappingSuggestion()}
				>
					{ai.loading === 'framework-mapping-suggest'
						? 'Running...'
						: 'Run Local AI Framework Mapping Suggestion'}
				</button>
				<span class="text-xs text-sky-900">
					AI Provider: {humanizeProviderMode(frameworkControlMappingProviderMode())} &middot; No database
					writes occur in Step 7A.
				</span>
			</div>

			{#if ai.frameworkControlMappingDraft}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">Step 7A suggestion summary</div>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Overall confidence: {formatConfidence(
								ai.frameworkControlMappingDraft.overall_confidence
							)}
						</span>
						<span class="rounded bg-sky-100 px-2 py-1 font-semibold text-sky-900">
							Framework mappings: {ai.frameworkControlMappingDraft.framework_control_mappings
								?.length ?? 0}
						</span>
						<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
							Warnings: {ai.frameworkControlMappingDraft.warnings?.length ?? 0}
						</span>
					</div>
				</div>

				{#if ai.frameworkControlMappingDraft.framework_control_mappings?.length}
					<div class="mt-3">
						<div class="font-semibold text-sky-950">
							Framework control mappings ({ai.frameworkControlMappingDraft
								.framework_control_mappings.length})
						</div>
						<p class="text-xs text-sky-900">
							Existing framework controls the AI considers relevant. Advisory drafts only; no
							framework control is created.
						</p>
						<div class="mt-2 grid gap-2">
							{#each ai.frameworkControlMappingDraft.framework_control_mappings as mapping}
								<div class="rounded border bg-white p-3 text-xs text-slate-800">
									<div class="flex flex-wrap items-start justify-between gap-2">
										<div class="text-sm font-semibold text-slate-950">
											{#if mapping.framework_control_code}
												<span class="text-slate-600">{mapping.framework_control_code}</span>
												&middot;
											{/if}
											{mapping.framework_control_title}
										</div>
										<div class="flex flex-wrap gap-1">
											<span class="rounded bg-sky-100 px-2 py-0.5 font-semibold text-sky-900">
												{humanizeFieldLabel(mapping.mapping_type)}
											</span>
											<span class="rounded bg-slate-100 px-2 py-0.5 font-semibold text-slate-700">
												Confidence: {formatConfidence(mapping.confidence)}
											</span>
											{#if mapping.review_status}
												<span
													class="rounded bg-violet-100 px-2 py-0.5 font-semibold text-violet-900"
												>
													{humanizeFieldLabel(mapping.review_status)}
												</span>
											{/if}
										</div>
									</div>
									{#if mapping.framework_name}
										<div class="mt-1">
											<span class="font-semibold">Framework:</span>
											{mapping.framework_name}
										</div>
									{/if}
									{#if mapping.framework_control_description}
										<div class="mt-1 text-slate-700">{mapping.framework_control_description}</div>
									{/if}
									{#if mapping.rationale}
										<div class="mt-1">
											<span class="font-semibold">Rationale:</span>
											{mapping.rationale}
										</div>
									{/if}
									{#if mapping.linked_finding_title || mapping.linked_finding_reference}
										<div class="mt-1">
											<span class="font-semibold">Linked finding:</span>
											{mapping.linked_finding_title || mapping.linked_finding_reference}
										</div>
									{/if}
									{#if mapping.linked_applied_control_title || mapping.linked_applied_control_reference}
										<div class="mt-1">
											<span class="font-semibold">Linked applied control:</span>
											{mapping.linked_applied_control_title ||
												mapping.linked_applied_control_reference}
										</div>
									{/if}
									{#if mapping.linked_remediation_action_title || mapping.linked_remediation_action_reference}
										<div class="mt-1">
											<span class="font-semibold">Linked remediation action:</span>
											{mapping.linked_remediation_action_title ||
												mapping.linked_remediation_action_reference}
										</div>
									{/if}
									{#if mapping.evidence_needed?.length}
										<div class="mt-1">
											<span class="font-semibold">Evidence needed:</span>
											<ul class="list-disc pl-5">
												{#each mapping.evidence_needed as evidenceItem}
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

				{#if ai.frameworkControlMappingDraft.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.frameworkControlMappingDraft.warnings as warning}
							<li>{warning.message ?? warning.detail ?? warning.code}</li>
						{/each}
					</ul>
				{/if}

				{#if ai.frameworkControlMappingDraft.ambiguity_flags?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.frameworkControlMappingDraft.ambiguity_flags as flag}
							<li>{flag.message ?? flag.code}</li>
						{/each}
					</ul>
				{/if}
			{/if}
		</div>
	{/if}
</section>

<section data-testid="ai-onboarding-step-7b">
	{#if !ai.frameworkControlMappingDraft?.framework_control_mappings?.length}
		<AiOnboardingPrerequisite
			step="7B"
			requires="7A"
			detail="Run Step 7A before Step 7B. Step 7B needs at least one Step 7A framework control mapping."
		/>
	{:else}
		<div class="rounded border border-emerald-300 bg-emerald-50/60 p-3 text-sm text-emerald-950">
			<div class="font-semibold">Step 7B &middot; Framework Control Mapping Commit</div>
			<p class="mt-1 text-emerald-900">
				<span class="font-semibold">No AI model is used / writes only after approval.</span>
				Select the Step 7A framework mappings to keep, then dry-run to preview. The approved commit writes
				deterministic mappings only for selected and approved items.
			</p>

			{#if frameworkMappingUsedCsvFallback()}
				<p class="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-900">
					These controls were matched from the read-only framework export file, not from the
					database, because the selected audit's framework has no assessable requirement nodes
					loaded. Step 7B never creates framework controls, so the dry-run will block. To get a
					committable mapping: load the framework library from the Libraries page, then run Step 2
					for a new case against that loaded framework.
				</p>
			{/if}

			{#if !ai.setupReference.folder_id || !ai.setupReference.compliance_assessment_id}
				<p class="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-900">
					A Folder ID and a Compliance Assessment ID are required before the deterministic Step 7B
					write. Both come from Step 2 and can also be filled in under "Case reference &amp;
					context" above.
				</p>
			{/if}

			<div class="mt-3 grid gap-2">
				{#each ai.frameworkControlMappingDraft.framework_control_mappings as mapping}
					<label class="flex items-start gap-2 rounded border bg-white p-2 text-xs">
						<input
							type="checkbox"
							bind:checked={ai.selectedFrameworkMappingIds[mapping.temporary_id]}
						/>
						<span>
							<span class="font-semibold">
								{#if mapping.framework_control_code}
									{mapping.framework_control_code} &middot;
								{/if}
								{mapping.framework_control_title}
							</span>
							<span class="text-slate-600">
								&middot; {humanizeFieldLabel(mapping.mapping_type)} &middot; Confidence: {formatConfidence(
									mapping.confidence
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
					disabled={ai.loading !== null || !selectedFrameworkMappings().length}
					onclick={() => runFrameworkControlMappingCommit(true)}
				>
					{ai.loading === 'framework-mapping-commit-dry-run' ? 'Dry-running...' : 'Step 7B dry-run'}
				</button>
				<label class="flex items-center gap-2 text-xs">
					<input type="checkbox" bind:checked={ai.frameworkMappingCommitApproved} />
					<span>
						I approve deterministic Step 7B decisions for selected framework control mappings
					</span>
				</label>
				<button
					class="btn btn-sm preset-filled-error-500"
					type="button"
					disabled={ai.loading !== null ||
						Boolean(ai.frameworkMappingCommitResult) ||
						!ai.frameworkMappingCommitApproved ||
						!frameworkMappingDryRunSucceeded() ||
						!selectedFrameworkMappings().length}
					onclick={() => runFrameworkControlMappingCommit(false)}
				>
					{ai.loading === 'framework-mapping-commit'
						? 'Committing...'
						: 'Approved framework mapping commit'}
				</button>
				<span class="text-xs text-emerald-900">No AI model is used in this write step.</span>
			</div>

			{#if ai.frameworkMappingCommitResult}
				<AiOnboardingAlreadyCommitted step="7B" rerun="7A" dryRunReArms />
			{/if}

			{#if ai.frameworkMappingCommitDryRun && !frameworkMappingDryRunSucceeded() && selectedFrameworkMappings().length}
				<p class="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-900">
					The selection changed after the last dry-run, or the dry-run was blocked. Run the Step 7B
					dry-run again before the approved commit.
				</p>
			{/if}

			{#if ai.frameworkMappingCommitDryRun}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">
						Step 7B dry-run status: {humanizeFieldLabel(
							ai.frameworkMappingCommitDryRun.commit_status
						)}
					</div>
					<p class="text-xs text-slate-700">
						Dry-run only previews the deterministic write. Nothing was written.
					</p>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Rejected: {ai.frameworkMappingCommitDryRun.rejected_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Deferred: {ai.frameworkMappingCommitDryRun.deferred_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Skipped: {ai.frameworkMappingCommitDryRun.skipped_records?.length ?? 0}
						</span>
					</div>
					{#if ai.frameworkMappingCommitDryRun.planned_actions?.length}
						<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.frameworkMappingCommitDryRun.planned_actions as action}
								<li>
									{action.target_name ?? action.source_temporary_id}:
									{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
									&middot; {action.detail}
								</li>
							{/each}
						</ul>
					{/if}
				</div>
				{#if ai.frameworkMappingCommitDryRun.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.frameworkMappingCommitDryRun.warnings as warning}
							<li>{warning.detail ?? warning.message ?? warning.code}</li>
						{/each}
					</ul>
				{/if}
				{#if ai.frameworkMappingCommitDryRun.blocking_errors?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
						{#each ai.frameworkMappingCommitDryRun.blocking_errors as blockingError}
							<li>{blockingError.detail}</li>
						{/each}
					</ul>
				{/if}
			{/if}

			{#if ai.frameworkMappingCommitResult}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">
						Step 7B commit status: {humanizeFieldLabel(
							ai.frameworkMappingCommitResult.commit_status
						)}
					</div>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
							Created: {ai.frameworkMappingCommitResult.created_records?.length ?? 0}
						</span>
						<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
							Reused: {ai.frameworkMappingCommitResult.reused_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Rejected: {ai.frameworkMappingCommitResult.rejected_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Deferred: {ai.frameworkMappingCommitResult.deferred_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Skipped: {ai.frameworkMappingCommitResult.skipped_records?.length ?? 0}
						</span>
						<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
							Warnings: {ai.frameworkMappingCommitResult.warnings?.length ?? 0}
						</span>
						<span class="rounded bg-red-100 px-2 py-1 font-semibold text-red-900">
							Blocking errors: {ai.frameworkMappingCommitResult.blocking_errors?.length ?? 0}
						</span>
					</div>
					{#if ai.frameworkMappingCommitResult.created_records?.length}
						<div class="text-xs font-semibold text-emerald-950">Created mappings</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.frameworkMappingCommitResult.created_records as record}
								<li>{humanizeFieldLabel(record.record_type)}: {record.name}</li>
							{/each}
						</ul>
					{/if}
					{#if ai.frameworkMappingCommitResult.reused_records?.length}
						<div class="text-xs font-semibold text-emerald-950">Reused existing mappings</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.frameworkMappingCommitResult.reused_records as record}
								<li>{humanizeFieldLabel(record.record_type)}: {record.name}</li>
							{/each}
						</ul>
					{/if}
					{#if ai.frameworkMappingCommitResult.planned_actions?.length}
						<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.frameworkMappingCommitResult.planned_actions as action}
								<li>
									{action.target_name ?? action.source_temporary_id}:
									{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
								</li>
							{/each}
						</ul>
					{/if}
					<p class="text-xs text-emerald-900">
						Next: <a class="font-semibold underline" href="/risk-scenarios">
							Step 8A on the Risk scenarios page</a
						>.
					</p>
				</div>
				{#if ai.frameworkMappingCommitResult.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.frameworkMappingCommitResult.warnings as warning}
							<li>{warning.detail ?? warning.message ?? warning.code}</li>
						{/each}
					</ul>
				{/if}
				{#if ai.frameworkMappingCommitResult.blocking_errors?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
						{#each ai.frameworkMappingCommitResult.blocking_errors as blockingError}
							<li>{blockingError.detail}</li>
						{/each}
					</ul>
				{/if}
			{/if}
		</div>
	{/if}
</section>
