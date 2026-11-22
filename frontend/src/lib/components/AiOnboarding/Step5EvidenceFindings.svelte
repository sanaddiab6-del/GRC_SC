<script lang="ts">
	import AiOnboardingAlreadyCommitted from './AiOnboardingAlreadyCommitted.svelte';
	import AiOnboardingPrerequisite from './AiOnboardingPrerequisite.svelte';
	import {
		ai,
		displayAuditQuestionTitle,
		displayEvidenceTitle,
		displayFindingTitle,
		evidenceFindingProviderMode,
		formatConfidence,
		humanizeActionName,
		humanizeFieldLabel,
		humanizeProviderMode,
		linkedAssetLabel,
		linkedControlLabel,
		runEvidenceFindingCommit,
		runEvidenceFindingSuggestion
	} from './aiOnboardingState.svelte';

	/**
	 * Steps 5A and 5B: the evidence / finding suggestion and its deterministic write.
	 *
	 * They render on the Evidences page. Step 5B is one backend call that writes draft Evidence
	 * records for the evidence requests and audit questions, and Finding records for the
	 * preliminary findings, so it is not split across the two pages: splitting it would mean two
	 * commits and therefore a second write of records the first commit already created.
	 */
</script>

<section data-testid="ai-onboarding-step-5a">
	{#if !ai.appliedControlCommitResult}
		<AiOnboardingPrerequisite
			step="5A"
			requires="4B"
			detail="Complete the approved applied control commit (Step 4B) before Step 5A."
		/>
	{:else}
		<div class="rounded border border-indigo-200 bg-indigo-50/60 p-3 text-sm text-indigo-950">
			<div class="font-semibold">Step 5A &middot; Evidence / Finding Suggestion</div>
			<p class="mt-1 text-indigo-900">
				<span class="font-semibold">AI suggestion only / no database write.</span>
				Step 5A drafts evidence requests, audit questions, and preliminary findings for review. No findings
				or evidence records are created until the approved Step 5B commit.
			</p>
			<p class="mt-1 text-xs text-indigo-900">
				Step 5B creates draft <span class="font-semibold">Evidence</span> records for the evidence
				requests and audit questions, and <span class="font-semibold">Finding</span> records for the preliminary
				findings.
			</p>
			<div class="mt-3 flex flex-wrap items-center gap-3">
				<button
					class="btn btn-sm preset-filled-primary-500"
					type="button"
					disabled={ai.loading !== null || !ai.appliedControlCommitResult}
					onclick={() => runEvidenceFindingSuggestion()}
				>
					{ai.loading === 'evidence-suggest'
						? 'Running...'
						: 'Run Local AI Evidence/Finding Suggestion'}
				</button>
				<span class="text-xs text-indigo-900">
					AI Provider: {humanizeProviderMode(evidenceFindingProviderMode())} &middot; No database writes
					occur in Step 5A.
				</span>
			</div>

			{#if ai.evidenceFindingDraft}
				<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">Step 5A suggestion summary</div>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Overall confidence: {formatConfidence(ai.evidenceFindingDraft.overall_confidence)}
						</span>
						<span class="rounded bg-indigo-100 px-2 py-1 font-semibold text-indigo-900">
							Evidence requests: {ai.evidenceFindingDraft.evidence_requests?.length ?? 0}
						</span>
						<span class="rounded bg-indigo-100 px-2 py-1 font-semibold text-indigo-900">
							Audit questions: {ai.evidenceFindingDraft.audit_questions?.length ?? 0}
						</span>
						<span class="rounded bg-indigo-100 px-2 py-1 font-semibold text-indigo-900">
							Preliminary findings: {ai.evidenceFindingDraft.preliminary_findings?.length ?? 0}
						</span>
						<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
							Warnings: {ai.evidenceFindingDraft.warnings?.length ?? 0}
						</span>
					</div>
				</div>

				{#if ai.evidenceFindingDraft.evidence_requests?.length}
					<div class="mt-3">
						<div class="font-semibold text-indigo-950">
							Evidence requests ({ai.evidenceFindingDraft.evidence_requests.length})
						</div>
						<p class="text-xs text-indigo-900">
							Documents or artifacts the AI suggests collecting as audit evidence.
						</p>
						<div class="mt-2 grid gap-2">
							{#each ai.evidenceFindingDraft.evidence_requests as request, index}
								<div class="rounded border bg-white p-3 text-xs text-slate-800">
									<div class="flex flex-wrap items-start justify-between gap-2">
										<div class="text-sm font-semibold text-slate-950">
											{displayEvidenceTitle(request, index)}
										</div>
										<div class="flex flex-wrap gap-1">
											<span class="rounded bg-slate-100 px-2 py-0.5 font-semibold text-slate-700">
												Confidence: {formatConfidence(request.confidence)}
											</span>
											{#if request.review_status}
												<span
													class="rounded bg-indigo-100 px-2 py-0.5 font-semibold text-indigo-900"
												>
													{humanizeFieldLabel(request.review_status)}
												</span>
											{/if}
										</div>
									</div>
									{#if request.description}
										<div class="mt-1 text-slate-700">{request.description}</div>
									{/if}
									{#if request.rationale}
										<div class="mt-1">
											<span class="font-semibold">Rationale:</span>
											{request.rationale}
										</div>
									{/if}
									{#if request.linked_asset_ids?.length}
										<div class="mt-1">
											<span class="font-semibold">Linked assets:</span>
											{request.linked_asset_ids
												.map((assetId: string) => linkedAssetLabel(assetId))
												.join(', ')}
										</div>
									{/if}
									{#if request.linked_applied_control_ids?.length}
										<div class="mt-1">
											<span class="font-semibold">Linked controls:</span>
											{request.linked_applied_control_ids
												.map((controlId: string) => linkedControlLabel(controlId))
												.join(', ')}
										</div>
									{/if}
								</div>
							{/each}
						</div>
					</div>
				{/if}

				{#if ai.evidenceFindingDraft.audit_questions?.length}
					<div class="mt-3">
						<div class="font-semibold text-indigo-950">
							Audit questions ({ai.evidenceFindingDraft.audit_questions.length})
						</div>
						<p class="text-xs text-indigo-900">
							Questions the AI suggests asking during the audit interviews.
						</p>
						<div class="mt-2 grid gap-2">
							{#each ai.evidenceFindingDraft.audit_questions as question, index}
								<div class="rounded border bg-white p-3 text-xs text-slate-800">
									<div class="flex flex-wrap items-start justify-between gap-2">
										<div class="text-sm font-semibold text-slate-950">
											{displayAuditQuestionTitle(question, index)}
										</div>
										<div class="flex flex-wrap gap-1">
											<span class="rounded bg-slate-100 px-2 py-0.5 font-semibold text-slate-700">
												Confidence: {formatConfidence(question.confidence)}
											</span>
											{#if question.review_status}
												<span
													class="rounded bg-indigo-100 px-2 py-0.5 font-semibold text-indigo-900"
												>
													{humanizeFieldLabel(question.review_status)}
												</span>
											{/if}
										</div>
									</div>
									{#if question.rationale}
										<div class="mt-1">
											<span class="font-semibold">Rationale:</span>
											{question.rationale}
										</div>
									{/if}
									{#if question.linked_asset_ids?.length}
										<div class="mt-1">
											<span class="font-semibold">Linked assets:</span>
											{question.linked_asset_ids
												.map((assetId: string) => linkedAssetLabel(assetId))
												.join(', ')}
										</div>
									{/if}
									{#if question.linked_applied_control_ids?.length}
										<div class="mt-1">
											<span class="font-semibold">Linked controls:</span>
											{question.linked_applied_control_ids
												.map((controlId: string) => linkedControlLabel(controlId))
												.join(', ')}
										</div>
									{/if}
								</div>
							{/each}
						</div>
					</div>
				{/if}

				{#if ai.evidenceFindingDraft.preliminary_findings?.length}
					<div class="mt-3">
						<div class="font-semibold text-indigo-950">
							Preliminary findings ({ai.evidenceFindingDraft.preliminary_findings.length})
						</div>
						<p class="text-xs text-indigo-900">
							Draft findings the AI suggests investigating based on the known weaknesses.
						</p>
						<div class="mt-2 grid gap-2">
							{#each ai.evidenceFindingDraft.preliminary_findings as finding, index}
								<div class="rounded border bg-white p-3 text-xs text-slate-800">
									<div class="flex flex-wrap items-start justify-between gap-2">
										<div class="text-sm font-semibold text-slate-950">
											{displayFindingTitle(finding, index)}
										</div>
										<div class="flex flex-wrap gap-1">
											{#if finding.severity}
												<span class="rounded bg-amber-100 px-2 py-0.5 font-semibold text-amber-900">
													Severity: {finding.severity}
												</span>
											{/if}
											<span class="rounded bg-slate-100 px-2 py-0.5 font-semibold text-slate-700">
												Confidence: {formatConfidence(finding.confidence)}
											</span>
											{#if finding.review_status}
												<span
													class="rounded bg-indigo-100 px-2 py-0.5 font-semibold text-indigo-900"
												>
													{humanizeFieldLabel(finding.review_status)}
												</span>
											{/if}
										</div>
									</div>
									{#if finding.summary}
										<div class="mt-1 text-slate-700">{finding.summary}</div>
									{/if}
									{#if finding.rationale}
										<div class="mt-1">
											<span class="font-semibold">Rationale:</span>
											{finding.rationale}
										</div>
									{/if}
									{#if finding.related_weaknesses?.length}
										<div class="mt-1">
											<span class="font-semibold">Related weaknesses:</span>
											{finding.related_weaknesses.join('; ')}
										</div>
									{/if}
									{#if finding.linked_asset_ids?.length}
										<div class="mt-1">
											<span class="font-semibold">Linked assets:</span>
											{finding.linked_asset_ids
												.map((assetId: string) => linkedAssetLabel(assetId))
												.join(', ')}
										</div>
									{/if}
									{#if finding.linked_applied_control_ids?.length}
										<div class="mt-1">
											<span class="font-semibold">Linked controls:</span>
											{finding.linked_applied_control_ids
												.map((controlId: string) => linkedControlLabel(controlId))
												.join(', ')}
										</div>
									{/if}
								</div>
							{/each}
						</div>
					</div>
				{/if}

				{#if ai.evidenceFindingDraft.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.evidenceFindingDraft.warnings as warning}
							<li>{warning.message ?? warning.detail ?? warning.code}</li>
						{/each}
					</ul>
				{/if}
			{/if}
		</div>
	{/if}
</section>

<section data-testid="ai-onboarding-step-5b">
	{#if !ai.evidenceFindingDraft}
		<AiOnboardingPrerequisite step="5B" requires="5A" detail="Run Step 5A before Step 5B." />
	{:else}
		<div class="rounded border border-emerald-300 bg-emerald-50/60 p-3 text-sm text-emerald-950">
			<div class="font-semibold">Step 5B &middot; Evidence / Finding Commit</div>
			<p class="mt-1 text-emerald-900">
				<span class="font-semibold">No AI model is used / writes only after approval.</span>
				Select the Step 5A suggestions to keep, then dry-run to preview. Dry-run does not write. The approved
				commit writes deterministic records only for the items you selected and approved.
			</p>

			{#if ai.evidenceFindingDraft.evidence_requests?.length}
				<div class="mt-3">
					<div class="font-semibold text-emerald-950">Evidence requests</div>
					<div class="mt-1 grid gap-1">
						{#each ai.evidenceFindingDraft.evidence_requests as request, index}
							<label
								class="flex items-start gap-2 rounded border bg-white p-2 text-xs text-slate-800"
							>
								<input
									type="checkbox"
									bind:checked={ai.selectedEvidenceRequestIds[request.temporary_id]}
								/>
								<span>
									<span class="font-semibold text-slate-950">
										{displayEvidenceTitle(request, index)}
									</span>
									{#if request.description || request.rationale}
										<span class="block text-slate-700">
											{request.description || request.rationale}
										</span>
									{/if}
									<span class="block text-slate-500">
										Confidence: {formatConfidence(request.confidence)} &middot; Will be created as a draft
										Evidence record.
									</span>
								</span>
							</label>
						{/each}
					</div>
				</div>
			{/if}

			{#if ai.evidenceFindingDraft.audit_questions?.length}
				<div class="mt-3">
					<div class="font-semibold text-emerald-950">Audit questions</div>
					<div class="mt-1 grid gap-1">
						{#each ai.evidenceFindingDraft.audit_questions as question, index}
							<label
								class="flex items-start gap-2 rounded border bg-white p-2 text-xs text-slate-800"
							>
								<input
									type="checkbox"
									bind:checked={ai.selectedAuditQuestionIds[question.temporary_id]}
								/>
								<span>
									<span class="font-semibold text-slate-950">
										{displayAuditQuestionTitle(question, index)}
									</span>
									{#if question.rationale}
										<span class="block text-slate-700">{question.rationale}</span>
									{/if}
									<span class="block text-slate-500">
										Confidence: {formatConfidence(question.confidence)}
									</span>
								</span>
							</label>
						{/each}
					</div>
				</div>
			{/if}

			{#if ai.evidenceFindingDraft.preliminary_findings?.length}
				<div class="mt-3">
					<div class="font-semibold text-emerald-950">Preliminary findings</div>
					<div class="mt-1 grid gap-1">
						{#each ai.evidenceFindingDraft.preliminary_findings as finding, index}
							<label
								class="flex items-start gap-2 rounded border bg-white p-2 text-xs text-slate-800"
							>
								<input
									type="checkbox"
									bind:checked={ai.selectedPreliminaryFindingIds[finding.temporary_id]}
								/>
								<span>
									<span class="font-semibold text-slate-950">
										{displayFindingTitle(finding, index)}
									</span>
									{#if finding.summary || finding.rationale || finding.description}
										<span class="block text-slate-700">
											{finding.summary || finding.rationale || finding.description}
										</span>
									{/if}
									<span class="block text-slate-500">
										{#if finding.severity}Severity: {finding.severity} &middot;{/if}
										Confidence: {formatConfidence(finding.confidence)} &middot; Will be created as a Finding
										record.
									</span>
								</span>
							</label>
						{/each}
					</div>
				</div>
			{/if}

			<div class="mt-3 flex flex-wrap items-center gap-3">
				<button
					class="btn btn-sm preset-tonal-primary"
					type="button"
					disabled={ai.loading !== null}
					onclick={() => runEvidenceFindingCommit(true)}
				>
					{ai.loading === 'evidence-commit-dry-run' ? 'Dry-running...' : 'Step 5B dry-run'}
				</button>
				<label class="flex items-center gap-2 text-sm">
					<input type="checkbox" bind:checked={ai.evidenceFindingCommitApproved} />
					<span>
						I approve deterministic Step 5B decisions for selected evidence/finding suggestions
					</span>
				</label>
				<button
					class="btn btn-sm preset-filled-primary-500"
					type="button"
					disabled={ai.loading !== null ||
						Boolean(ai.evidenceFindingCommitResult) ||
						!ai.evidenceFindingCommitApproved}
					onclick={() => runEvidenceFindingCommit(false)}
				>
					{ai.loading === 'evidence-commit' ? 'Committing...' : 'Approved evidence/finding commit'}
				</button>
				<span class="text-xs text-emerald-900">No AI model is used in this write step.</span>
			</div>

			{#if ai.evidenceFindingCommitResult}
				<AiOnboardingAlreadyCommitted step="5B" rerun="5A" />
			{/if}

			{#if ai.evidenceFindingCommitDryRun}
				<div class="mt-3 rounded border bg-white p-3 text-sm">
					<div class="font-semibold">
						Step 5B dry-run status: {ai.evidenceFindingCommitDryRun.status}
					</div>
					<p class="mt-1 text-xs text-slate-600">
						Dry-run is a preview only — nothing was written to the database. The plan below shows
						what an approved commit would do.
					</p>
					{#if ai.evidenceFindingCommitDryRun.counts}
						<div class="mt-2 flex flex-wrap gap-2 text-xs">
							<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
								Rejected: {ai.evidenceFindingCommitDryRun.counts.rejected ?? 0}
							</span>
							<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
								Deferred: {ai.evidenceFindingCommitDryRun.counts.deferred ?? 0}
							</span>
							<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
								Skipped: {ai.evidenceFindingCommitDryRun.counts.skipped ?? 0}
							</span>
						</div>
					{/if}
					{#if ai.evidenceFindingCommitDryRun.planned_actions?.length}
						<div class="mt-2 text-xs font-semibold text-slate-950">Planned actions</div>
						<ul class="mt-1 list-disc pl-5 text-xs text-slate-800">
							{#each ai.evidenceFindingCommitDryRun.planned_actions as action}
								<li>
									<span class="font-semibold"
										>{humanizeFieldLabel(action.record_type ?? action.kind)}</span
									>
									{#if action.name}"{action.name}"{/if}
									&mdash; {humanizeActionName(action.action)} &rarr;
									{humanizeFieldLabel(action.status)}: {action.detail}
								</li>
							{/each}
						</ul>
					{/if}
					{#if ai.evidenceFindingCommitDryRun.warnings?.length}
						<div class="mt-2 text-xs font-semibold text-amber-800">Warnings</div>
						<ul class="mt-1 list-disc pl-5 text-xs text-amber-800">
							{#each ai.evidenceFindingCommitDryRun.warnings as warning}
								<li>{warning.detail ?? warning.message ?? warning.code}</li>
							{/each}
						</ul>
					{/if}
					{#if ai.evidenceFindingCommitDryRun.blocking_errors?.length}
						<div class="mt-2 text-xs font-semibold text-red-700">
							Blocking errors (commit will be refused until resolved)
						</div>
						<ul class="mt-1 list-disc pl-5 text-xs text-red-700">
							{#each ai.evidenceFindingCommitDryRun.blocking_errors as blockingError}
								<li>{blockingError.detail}</li>
							{/each}
						</ul>
					{/if}
				</div>
			{/if}

			{#if ai.evidenceFindingCommitResult}
				<div class="mt-3 grid gap-2 rounded border border-emerald-200 bg-white p-3 text-sm">
					<div class="font-semibold">
						Step 5B commit status: {ai.evidenceFindingCommitResult.status}
					</div>
					<p class="text-xs text-emerald-900">
						Approved commit complete — deterministic records only, no AI model involved in this
						write.
					</p>
					<div class="flex flex-wrap gap-2 text-xs">
						<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
							Created: {ai.evidenceFindingCommitResult.counts?.created ?? 0}
						</span>
						<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
							Reused: {ai.evidenceFindingCommitResult.counts?.reused ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Rejected: {ai.evidenceFindingCommitResult.counts?.rejected ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Deferred: {ai.evidenceFindingCommitResult.counts?.deferred ?? 0}
						</span>
						<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
							Skipped: {ai.evidenceFindingCommitResult.counts?.skipped ?? 0}
						</span>
						<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
							Warnings: {ai.evidenceFindingCommitResult.warnings?.length ?? 0}
						</span>
						<span class="rounded bg-red-100 px-2 py-1 font-semibold text-red-800">
							Blocking errors: {ai.evidenceFindingCommitResult.blocking_errors?.length ?? 0}
						</span>
					</div>
					{#if ai.evidenceFindingCommitResult.created_records?.length}
						<div class="text-xs font-semibold text-emerald-950">Created records</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.evidenceFindingCommitResult.created_records as record}
								<li>{humanizeFieldLabel(record.record_type)}: {record.name}</li>
							{/each}
						</ul>
					{/if}
					{#if ai.evidenceFindingCommitResult.reused_records?.length}
						<div class="text-xs font-semibold text-emerald-950">Reused existing records</div>
						<ul class="list-disc pl-5 text-xs text-slate-800">
							{#each ai.evidenceFindingCommitResult.reused_records as record}
								<li>{humanizeFieldLabel(record.record_type)}: {record.name}</li>
							{/each}
						</ul>
					{/if}
					<p class="text-xs text-emerald-900">
						Next: <a class="font-semibold underline" href="/applied-controls">
							Step 6A on the Applied controls page</a
						>.
					</p>
				</div>
				{#if ai.evidenceFindingCommitResult.warnings?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
						{#each ai.evidenceFindingCommitResult.warnings as warning}
							<li>{warning.detail ?? warning.message ?? warning.code}</li>
						{/each}
					</ul>
				{/if}
				{#if ai.evidenceFindingCommitResult.blocking_errors?.length}
					<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
						{#each ai.evidenceFindingCommitResult.blocking_errors as blockingError}
							<li>{blockingError.detail}</li>
						{/each}
					</ul>
				{/if}
			{/if}
		</div>
	{/if}
</section>
