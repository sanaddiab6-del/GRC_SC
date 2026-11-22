<script lang="ts">
	import AiOnboardingAlreadyCommitted from './AiOnboardingAlreadyCommitted.svelte';
	import AiOnboardingPrerequisite from './AiOnboardingPrerequisite.svelte';
	import {
		ai,
		formatConfidence,
		humanizeActionName,
		humanizeFieldLabel,
		humanizeProviderMode,
		riskScenarioDryRunSucceeded,
		riskScenarioProviderMode,
		runRiskScenarioCommit,
		runRiskScenarioSuggestion,
		selectedRiskScenarios
	} from './aiOnboardingState.svelte';

	/**
	 * Steps 8A and 8B: the risk scenario suggestion and its deterministic write.
	 *
	 * They render on the Risk scenarios page because Step 8B creates RiskScenario records. A risk
	 * scenario always belongs to an existing risk assessment, and Step 8B never creates one, so
	 * the risk assessment reference stays an explicit required field here.
	 */
</script>

<section data-testid="ai-onboarding-step-8a">
	{#if !ai.frameworkControlMappingDraft}
		<AiOnboardingPrerequisite
			step="8A"
			requires="7A"
			detail="Run Step 7A before Step 8A, so the risk scenarios are drafted against the reviewed framework mappings."
		/>
	{:else}
		<div class="rounded border border-sky-200 bg-sky-50/60 p-3 text-sm text-sky-950">
			<div class="font-semibold">Step 8A &middot; Risk Scenario Suggestion</div>
			<p class="mt-1 text-sky-900">
				<span class="font-semibold">AI suggestion only / no database write.</span>
				Step 8A drafts risk scenarios for review. No risk records are created, no risk is accepted or
				treated, and no risk is closed in this step.
			</p>
			<div class="mt-3 flex flex-wrap items-center gap-3">
				<button
					class="btn btn-sm preset-filled-primary-500"
					type="button"
					disabled={ai.loading !== null}
					onclick={() => runRiskScenarioSuggestion()}
				>
					{ai.loading === 'risk-scenario-suggest'
						? 'Running...'
						: 'Run Local AI Risk Scenario Suggestion'}
				</button>
				<span class="text-xs text-sky-900">
					AI Provider: {humanizeProviderMode(riskScenarioProviderMode())} &middot; No database writes
					occur in Step 8A.
				</span>
			</div>

			{#if ai.riskScenarioDraft}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">Step 8A suggestion summary</div>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Overall confidence: {formatConfidence(ai.riskScenarioDraft.overall_confidence)}
						</span>
						<span class="rounded bg-sky-100 px-2 py-1 font-semibold text-sky-900">
							Risk scenarios: {ai.riskScenarioDraft.risk_scenarios?.length ?? 0}
						</span>
						<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
							Warnings: {ai.riskScenarioDraft.warnings?.length ?? 0}
						</span>
					</div>
				</div>

				{#if ai.riskScenarioDraft.risk_scenarios?.length}
					<div class="mt-3">
						<div class="font-semibold text-sky-950">
							Risk scenarios ({ai.riskScenarioDraft.risk_scenarios.length})
						</div>
						<p class="text-xs text-sky-900">
							Advisory drafts only. Likelihood, impact, and risk level are review labels, not
							platform risk ratings.
						</p>
						<div class="mt-2 grid gap-2">
							{#each ai.riskScenarioDraft.risk_scenarios as scenario}
								<div class="rounded border bg-white p-3 text-xs text-slate-800">
									<div class="flex flex-wrap items-start justify-between gap-2">
										<div class="text-sm font-semibold text-slate-950">{scenario.title}</div>
										<div class="flex flex-wrap gap-1">
											<span class="rounded bg-sky-100 px-2 py-0.5 font-semibold text-sky-900">
												Likelihood: {humanizeFieldLabel(scenario.likelihood)}
											</span>
											<span class="rounded bg-orange-100 px-2 py-0.5 font-semibold text-orange-900">
												Impact: {humanizeFieldLabel(scenario.impact)}
											</span>
											<span class="rounded bg-red-100 px-2 py-0.5 font-semibold text-red-900">
												Risk level: {humanizeFieldLabel(scenario.risk_level)}
											</span>
											<span class="rounded bg-slate-100 px-2 py-0.5 font-semibold text-slate-700">
												Confidence: {formatConfidence(scenario.confidence)}
											</span>
											{#if scenario.review_status}
												<span
													class="rounded bg-violet-100 px-2 py-0.5 font-semibold text-violet-900"
												>
													{humanizeFieldLabel(scenario.review_status)}
												</span>
											{/if}
										</div>
									</div>
									{#if scenario.description}
										<div class="mt-1 text-slate-700">{scenario.description}</div>
									{/if}
									{#if scenario.threat}
										<div class="mt-1">
											<span class="font-semibold">Threat:</span>
											{scenario.threat}
										</div>
									{/if}
									{#if scenario.vulnerability}
										<div class="mt-1">
											<span class="font-semibold">Vulnerability:</span>
											{scenario.vulnerability}
										</div>
									{/if}
									{#if scenario.impact_description}
										<div class="mt-1">
											<span class="font-semibold">Potential impact:</span>
											{scenario.impact_description}
										</div>
									{/if}
									{#if scenario.asset_title || scenario.asset_reference}
										<div class="mt-1">
											<span class="font-semibold">Asset:</span>
											{scenario.asset_title || scenario.asset_reference}
										</div>
									{/if}
									{#if scenario.linked_finding_title || scenario.linked_finding_reference}
										<div class="mt-1">
											<span class="font-semibold">Linked finding:</span>
											{scenario.linked_finding_title || scenario.linked_finding_reference}
										</div>
									{/if}
									{#if scenario.linked_applied_control_title || scenario.linked_applied_control_reference}
										<div class="mt-1">
											<span class="font-semibold">Linked applied control:</span>
											{scenario.linked_applied_control_title ||
												scenario.linked_applied_control_reference}
										</div>
									{/if}
									{#if scenario.linked_framework_control_title || scenario.linked_framework_control_code}
										<div class="mt-1">
											<span class="font-semibold">Linked framework control:</span>
											{scenario.linked_framework_control_code}
											{scenario.linked_framework_control_title}
										</div>
									{/if}
									{#if scenario.rationale}
										<div class="mt-1">
											<span class="font-semibold">Rationale:</span>
											{scenario.rationale}
										</div>
									{/if}
									{#if scenario.recommended_next_steps?.length}
										<div class="mt-1">
											<span class="font-semibold">Recommended next steps:</span>
											<ul class="list-disc pl-5">
												{#each scenario.recommended_next_steps as nextStep}
													<li>{nextStep}</li>
												{/each}
											</ul>
										</div>
									{/if}
								</div>
							{/each}
						</div>
					</div>
				{/if}

				{#if ai.riskScenarioDraft.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.riskScenarioDraft.warnings as warning}
							<li>{warning.message ?? warning.detail ?? warning.code}</li>
						{/each}
					</ul>
				{/if}

				{#if ai.riskScenarioDraft.ambiguity_flags?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.riskScenarioDraft.ambiguity_flags as flag}
							<li>{flag.message ?? flag.code}</li>
						{/each}
					</ul>
				{/if}
			{/if}
		</div>
	{/if}
</section>

<section data-testid="ai-onboarding-step-8b">
	{#if !ai.riskScenarioDraft?.risk_scenarios?.length}
		<AiOnboardingPrerequisite
			step="8B"
			requires="8A"
			detail="Run Step 8A before Step 8B. Step 8B needs at least one Step 8A risk scenario."
		/>
	{:else}
		<div class="rounded border border-emerald-300 bg-emerald-50/60 p-3 text-sm text-emerald-950">
			<div class="font-semibold">Step 8B &middot; Risk Scenario Commit</div>
			<p class="mt-1 text-emerald-900">
				<span class="font-semibold">No AI model is used / writes only after approval.</span>
				Select the Step 8A risk scenarios to keep, then dry-run to preview. The approved commit creates
				unrated risk scenarios under the existing risk assessment; no risk rating, treatment, or acceptance
				is recorded.
			</p>

			<!-- A RiskScenario always belongs to an existing RiskAssessment, and Step 8B never
			     creates one. Step 2 only creates a RiskAssessment when it was explicitly requested
			     there, so the reference is surfaced here as a required field: it is prefilled from
			     the Step 2 handoff when one exists and can otherwise be pasted. -->
			<label class="mt-3 grid gap-1">
				<span class="text-sm font-semibold">
					Risk Assessment ID <span class="text-red-700">(required for Step 8B)</span>
				</span>
				<input
					class="input"
					placeholder="UUID of an existing Risk Assessment"
					bind:value={ai.setupReference.risk_assessment_id}
				/>
			</label>
			{#if !ai.setupReference.risk_assessment_id}
				<p class="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-900">
					No Risk Assessment is linked to this case yet, so Step 8B cannot run. A risk scenario can
					only be created under an existing risk assessment, and Step 8B never creates one. Either
					re-run Step 2 with "create risk assessment" enabled (it needs a Risk Matrix ID), or paste
					the ID of an existing Risk Assessment above.
				</p>
			{/if}

			<div class="mt-3 grid gap-2">
				{#each ai.riskScenarioDraft.risk_scenarios as scenario}
					<label class="flex items-start gap-2 rounded border bg-white p-2 text-xs">
						<input
							type="checkbox"
							bind:checked={ai.selectedRiskScenarioIds[scenario.temporary_id]}
						/>
						<span>
							<span class="font-semibold">{scenario.title}</span>
							<span class="text-slate-600">
								&middot; Risk level: {humanizeFieldLabel(scenario.risk_level)} &middot; Confidence: {formatConfidence(
									scenario.confidence
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
					disabled={ai.loading !== null ||
						!selectedRiskScenarios().length ||
						!ai.setupReference.risk_assessment_id}
					onclick={() => runRiskScenarioCommit(true)}
				>
					{ai.loading === 'risk-scenario-commit-dry-run' ? 'Dry-running...' : 'Step 8B dry-run'}
				</button>
				<label class="flex items-center gap-2 text-xs">
					<input type="checkbox" bind:checked={ai.riskScenarioCommitApproved} />
					<span>I approve deterministic Step 8B decisions for selected risk scenarios</span>
				</label>
				<button
					class="btn btn-sm preset-filled-error-500"
					type="button"
					disabled={ai.loading !== null ||
						Boolean(ai.riskScenarioCommitResult) ||
						!ai.riskScenarioCommitApproved ||
						!riskScenarioDryRunSucceeded() ||
						!selectedRiskScenarios().length}
					onclick={() => runRiskScenarioCommit(false)}
				>
					{ai.loading === 'risk-scenario-commit'
						? 'Committing...'
						: 'Approved risk scenario commit'}
				</button>
				<span class="text-xs text-emerald-900">No AI model is used in this write step.</span>
			</div>

			{#if ai.riskScenarioCommitResult}
				<AiOnboardingAlreadyCommitted step="8B" rerun="8A" dryRunReArms />
			{/if}

			{#if ai.riskScenarioCommitDryRun && !riskScenarioDryRunSucceeded() && selectedRiskScenarios().length}
				<p class="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-900">
					The selection changed after the last dry-run, or the dry-run was blocked. Run the Step 8B
					dry-run again before the approved commit.
				</p>
			{/if}

			{#if ai.riskScenarioCommitDryRun}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">
						Step 8B dry-run status: {humanizeFieldLabel(ai.riskScenarioCommitDryRun.commit_status)}
					</div>
					<p class="text-xs text-slate-700">
						Dry-run only previews the deterministic write. Nothing was written.
					</p>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Rejected: {ai.riskScenarioCommitDryRun.rejected_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Deferred: {ai.riskScenarioCommitDryRun.deferred_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Skipped: {ai.riskScenarioCommitDryRun.skipped_records?.length ?? 0}
						</span>
					</div>
					{#if ai.riskScenarioCommitDryRun.planned_actions?.length}
						<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.riskScenarioCommitDryRun.planned_actions as action}
								<li>
									{action.target_name ?? action.source_temporary_id}:
									{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
									&middot; {action.detail}
								</li>
							{/each}
						</ul>
					{/if}
				</div>
				{#if ai.riskScenarioCommitDryRun.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.riskScenarioCommitDryRun.warnings as warning}
							<li>{warning.detail ?? warning.message ?? warning.code}</li>
						{/each}
					</ul>
				{/if}
				{#if ai.riskScenarioCommitDryRun.blocking_errors?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
						{#each ai.riskScenarioCommitDryRun.blocking_errors as blockingError}
							<li>{blockingError.detail}</li>
						{/each}
					</ul>
				{/if}
			{/if}

			{#if ai.riskScenarioCommitResult}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">
						Step 8B commit status: {humanizeFieldLabel(ai.riskScenarioCommitResult.commit_status)}
					</div>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
							Created: {ai.riskScenarioCommitResult.created_records?.length ?? 0}
						</span>
						<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
							Reused: {ai.riskScenarioCommitResult.reused_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Rejected: {ai.riskScenarioCommitResult.rejected_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Deferred: {ai.riskScenarioCommitResult.deferred_records?.length ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Skipped: {ai.riskScenarioCommitResult.skipped_records?.length ?? 0}
						</span>
						<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
							Warnings: {ai.riskScenarioCommitResult.warnings?.length ?? 0}
						</span>
						<span class="rounded bg-red-100 px-2 py-1 font-semibold text-red-900">
							Blocking errors: {ai.riskScenarioCommitResult.blocking_errors?.length ?? 0}
						</span>
					</div>
					{#if ai.riskScenarioCommitResult.created_records?.length}
						<div class="text-xs font-semibold text-emerald-950">Created risk scenarios</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.riskScenarioCommitResult.created_records as record}
								<li>{humanizeFieldLabel(record.record_type)}: {record.name}</li>
							{/each}
						</ul>
					{/if}
					{#if ai.riskScenarioCommitResult.reused_records?.length}
						<div class="text-xs font-semibold text-emerald-950">Reused risk scenarios</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.riskScenarioCommitResult.reused_records as record}
								<li>{humanizeFieldLabel(record.record_type)}: {record.name}</li>
							{/each}
						</ul>
					{/if}
					{#if ai.riskScenarioCommitResult.planned_actions?.length}
						<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.riskScenarioCommitResult.planned_actions as action}
								<li>
									{action.target_name ?? action.source_temporary_id}:
									{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
								</li>
							{/each}
						</ul>
					{/if}
				</div>
				{#if ai.riskScenarioCommitResult.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.riskScenarioCommitResult.warnings as warning}
							<li>{warning.detail ?? warning.message ?? warning.code}</li>
						{/each}
					</ul>
				{/if}
				{#if ai.riskScenarioCommitResult.blocking_errors?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
						{#each ai.riskScenarioCommitResult.blocking_errors as blockingError}
							<li>{blockingError.detail}</li>
						{/each}
					</ul>
				{/if}
			{/if}
		</div>
	{/if}
</section>
