<script lang="ts">
	import { onMount, setContext, type Snippet } from 'svelte';
	import { ai, hydrateAiOnboarding, resetAiOnboardingWorkflow } from './aiOnboardingState.svelte';
	import { AI_ONBOARDING_PAGE_STEPS, stepHref } from './aiOnboardingSteps';

	/**
	 * Shell every onboarding page shares: the case reference, the shared error surface, and the
	 * raw payload inspector.
	 *
	 * The steps themselves are passed in as children, so each page renders only the steps that
	 * belong to the resource it manages.
	 */
	interface Props {
		/** Steps rendered on this page, in order. */
		children: Snippet;
		/** Step ids this page hosts, used for the panel heading. */
		steps: string[];
	}

	let { children, steps }: Props = $props();

	// A prerequisite guardrail points at the page that satisfies it. When that step is on this
	// same page it must say so instead of offering a link back to where the reader already is.
	setContext(AI_ONBOARDING_PAGE_STEPS, () => steps);

	// The case reference lives in `localStorage`, which the server render cannot see. Reading it
	// on mount keeps the first client render identical to the server HTML, so there is no
	// hydration mismatch; the panel simply fills in once the browser takes over.
	let mounted = $state(false);
	onMount(() => {
		hydrateAiOnboarding();
		mounted = true;
	});

	const hasCase = $derived(Boolean(ai.setupReference.folder_id || ai.sourceStep1DraftHash));
	const auditHref = $derived(stepHref('12A', ai.setupReference.compliance_assessment_id));
</script>

{#if mounted}
	<section
		class="mb-4 rounded-lg border border-teal-200 bg-teal-50/60 p-4 shadow-sm"
		data-testid="ai-onboarding-panel"
	>
		<div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
			<div>
				<h2 class="text-lg font-bold text-teal-950">
					Local AI Case Onboarding &middot; Step{steps.length === 1 ? '' : 's'}
					{steps.join(', ')}
				</h2>
				<p class="text-sm text-teal-900">
					These are the onboarding steps that act on the records managed on this page. Every AI step
					is advisory and writes nothing; every commit step is deterministic, requires a dry-run and
					an explicit approval, and is validated by the backend.
				</p>
			</div>
			{#if hasCase}
				<div class="rounded bg-teal-100 px-2 py-1 text-xs font-semibold text-teal-900">
					Case folder: {ai.setupReference.folder_id || 'not set'}
				</div>
			{/if}
		</div>

		{#if !hasCase}
			<div class="mt-3 rounded border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900">
				<div class="font-semibold">No Local AI case is loaded yet</div>
				<p class="mt-1 text-xs">
					Run Step 1 (case intake) and Step 2 (case setup) from the sidebar Quick Start dialog, in
					the "Local AI Case Onboarding" tab. Step 2 records the folder, perimeter, audit, and
					optional risk assessment this workflow uses, and the steps below unlock from there. The
					reference can also be filled in by hand below.
				</p>
			</div>
		{/if}

		<details class="mt-3 rounded border border-teal-200 bg-white/70 p-3">
			<summary class="cursor-pointer text-sm font-semibold text-teal-950">
				Case reference &amp; context (shared by every step)
			</summary>

			<div class="mt-3 grid gap-3 md:grid-cols-2">
				<label class="grid gap-1">
					<span class="text-sm font-semibold">source_step1_draft_hash</span>
					<input class="input" bind:value={ai.sourceStep1DraftHash} />
				</label>
				<label class="grid gap-1">
					<span class="text-sm font-semibold">Folder ID</span>
					<input class="input" bind:value={ai.setupReference.folder_id} />
				</label>
				<label class="grid gap-1">
					<span class="text-sm font-semibold">Perimeter ID</span>
					<input class="input" bind:value={ai.setupReference.perimeter_id} />
				</label>
				<label class="grid gap-1">
					<span class="text-sm font-semibold">ComplianceAssessment ID</span>
					<input class="input" bind:value={ai.setupReference.compliance_assessment_id} />
				</label>
				<label class="grid gap-1">
					<span class="text-sm font-semibold">RiskAssessment ID</span>
					<input class="input" bind:value={ai.setupReference.risk_assessment_id} />
				</label>
				<label class="grid gap-1">
					<span class="text-sm font-semibold">Selected Framework ID</span>
					<input class="input" bind:value={ai.setupReference.selected_framework_id} />
				</label>
			</div>

			<div class="mt-3 grid gap-3">
				<label class="grid gap-1">
					<span class="text-sm font-semibold">Scenario/context summary</span>
					<textarea class="textarea" rows="3" bind:value={ai.scenarioText}></textarea>
				</label>
				<label class="grid gap-1">
					<span class="text-sm font-semibold">Scope summary</span>
					<textarea class="textarea" rows="2" bind:value={ai.scopeSummary}></textarea>
				</label>
				<label class="grid gap-1">
					<span class="text-sm font-semibold">Known weaknesses</span>
					<textarea class="textarea" rows="2" bind:value={ai.knownWeaknesses}></textarea>
				</label>
				<label class="flex items-center gap-2 text-sm">
					<input type="checkbox" bind:checked={ai.strictMode} />
					<span>Strict mode</span>
				</label>
			</div>

			<div class="mt-3 flex flex-wrap items-center gap-3">
				{#if auditHref}
					<a class="text-xs font-semibold text-teal-900 underline" href={auditHref}>
						Open the audit page (Steps 7, 9, 10, 11, 12)
					</a>
				{/if}
				<button
					class="btn btn-sm preset-tonal"
					type="button"
					onclick={resetAiOnboardingWorkflow}
					title="Clears the locally stored onboarding progress. No platform record is deleted."
				>
					Clear local onboarding progress
				</button>
				<span class="text-xs text-slate-600">
					Clearing only discards the browser-side drafts and results; nothing is deleted from the
					database.
				</span>
			</div>
		</details>

		<div class="mt-4 grid gap-4">
			{@render children()}
		</div>

		<details class="mt-3">
			<summary class="cursor-pointer text-sm font-semibold">Raw JSON</summary>
			<pre
				class="mt-2 max-h-80 overflow-auto rounded bg-slate-950 p-3 text-xs text-slate-50">{JSON.stringify(
					{
						assetDraft: ai.assetDraft,
						commitDryRun: ai.commitDryRun,
						commitResult: ai.commitResult,
						appliedControlDraft: ai.appliedControlDraft,
						appliedControlCommitDryRun: ai.appliedControlCommitDryRun,
						appliedControlCommitResult: ai.appliedControlCommitResult,
						evidenceFindingDraft: ai.evidenceFindingDraft,
						evidenceFindingCommitDryRun: ai.evidenceFindingCommitDryRun,
						evidenceFindingCommitResult: ai.evidenceFindingCommitResult,
						remediationActionDraft: ai.remediationActionDraft,
						remediationCommitDryRun: ai.remediationCommitDryRun,
						remediationCommitResult: ai.remediationCommitResult,
						frameworkControlMappingDraft: ai.frameworkControlMappingDraft,
						frameworkMappingCommitDryRun: ai.frameworkMappingCommitDryRun,
						frameworkMappingCommitResult: ai.frameworkMappingCommitResult,
						riskScenarioDraft: ai.riskScenarioDraft,
						riskScenarioCommitDryRun: ai.riskScenarioCommitDryRun,
						riskScenarioCommitResult: ai.riskScenarioCommitResult,
						controlEffectivenessDraft: ai.controlEffectivenessDraft,
						controlEffectivenessCommitDryRun: ai.controlEffectivenessCommitDryRun,
						controlEffectivenessCommitResult: ai.controlEffectivenessCommitResult,
						auditReadinessDraft: ai.auditReadinessDraft,
						auditReadinessCommitDryRun: ai.auditReadinessCommitDryRun,
						auditReadinessCommitResult: ai.auditReadinessCommitResult,
						auditReportDraft: ai.auditReportDraft,
						auditReportCommitDryRun: ai.auditReportCommitDryRun,
						auditReportCommitResult: ai.auditReportCommitResult,
						finalReviewDraft: ai.finalReviewDraft,
						finalReviewCommitDryRun: ai.finalReviewCommitDryRun,
						finalReviewCommitResult: ai.finalReviewCommitResult
					},
					null,
					2
				)}</pre>
		</details>

		{#if ai.error}
			<pre
				class="mt-4 max-h-64 overflow-auto rounded border border-red-200 bg-red-50 p-3 text-xs text-red-900">{JSON.stringify(
					ai.error,
					null,
					2
				)}</pre>
		{/if}
	</section>
{/if}
