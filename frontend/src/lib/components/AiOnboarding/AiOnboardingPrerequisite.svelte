<script lang="ts">
	import { getContext } from 'svelte';
	import { ai } from './aiOnboardingState.svelte';
	import { AI_ONBOARDING_PAGE_STEPS, stepHref, stepPageLabel } from './aiOnboardingSteps';

	/**
	 * The guardrail a step shows when the step it depends on has not produced its handoff yet.
	 *
	 * The single-page implementation simply did not render the later step. Now that steps sit on
	 * different pages, silently rendering nothing would look like a missing feature, so the same
	 * prerequisite is stated explicitly and points at the page that satisfies it.
	 */
	interface Props {
		/** Step this guardrail belongs to, e.g. `6B`. */
		step: string;
		/** Step that must run first, e.g. `6A`. */
		requires: string;
		/** The prerequisite message. Reuses the wording the step's own payload check throws. */
		detail: string;
	}

	let { step, requires, detail }: Props = $props();

	const pageSteps = getContext<(() => string[]) | undefined>(AI_ONBOARDING_PAGE_STEPS);
	const onThisPage = $derived((pageSteps?.() ?? []).includes(requires));
	const href = $derived(stepHref(requires, ai.setupReference.compliance_assessment_id));
	const pageLabel = $derived(stepPageLabel(requires));
</script>

<div
	class="rounded border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900"
	data-testid="ai-onboarding-prerequisite-{step}"
>
	<div class="font-semibold">Step {step} is not available yet</div>
	<p class="mt-1 text-xs">{detail}</p>
	<p class="mt-1 text-xs">
		{#if onThisPage}
			Step {requires} is on this page, above.
		{:else if href}
			Step {requires} runs on <a class="font-semibold underline" {href}>{pageLabel}</a>.
		{:else}
			Step {requires} runs on <span class="font-semibold">{pageLabel}</span>.
		{/if}
	</p>
</div>
