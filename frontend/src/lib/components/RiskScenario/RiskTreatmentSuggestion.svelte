<script lang="ts">
	import {
		confidencePercent,
		fetchRiskTreatmentSuggestion,
		outcomeMessage,
		priorityBadgeClass,
		treatmentLabel,
		type RiskTreatmentSuggestion
	} from './riskTreatmentSuggestion';

	/**
	 * "AI Treatment Suggestion" panel on a Risk Scenario's own detail page.
	 *
	 * Advisory only: it calls the local AI provider through the backend's
	 * risk-scenarios/{id}/ai-treatment-suggestion action and only ever displays the result. It
	 * never changes the scenario, its treatment, its ratings, or any control or remediation, and
	 * offers no "apply" action. The only follow-up it offers is ordinary navigation to the existing
	 * edit page, and only for a user who can already edit the scenario.
	 */
	interface Props {
		riskScenarioId: string;
		/** Existing edit page, passed only when the caller may edit the scenario. */
		editHref?: string | null;
	}

	let { riskScenarioId, editHref = null }: Props = $props();

	type PanelState =
		| { kind: 'idle' }
		| { kind: 'loading' }
		| { kind: 'result'; result: RiskTreatmentSuggestion }
		| { kind: 'unauthorized' }
		| { kind: 'error'; message: string };

	let panel = $state<PanelState>({ kind: 'idle' });

	async function requestSuggestion() {
		panel = { kind: 'loading' };
		const outcome = await fetchRiskTreatmentSuggestion(fetch, riskScenarioId);
		if (outcome.state === 'success') {
			panel = { kind: 'result', result: outcome.result };
		} else if (outcome.state === 'unauthorized') {
			panel = { kind: 'unauthorized' };
		} else {
			panel = { kind: 'error', message: outcome.message };
		}
	}
</script>

<div class="card px-4 py-3 bg-white shadow-lg space-y-3" data-testid="risk-treatment-suggestion">
	<div class="flex items-center justify-between gap-2">
		<h4 class="h4 font-semibold">AI Treatment Suggestion</h4>
		<button
			type="button"
			class="btn preset-tonal-primary btn-sm"
			disabled={panel.kind === 'loading'}
			onclick={requestSuggestion}
			data-testid="risk-treatment-suggestion-button"
		>
			{#if panel.kind === 'loading'}
				<i class="fa-solid fa-spinner fa-spin mr-2"></i> Analyzing...
			{:else}
				<i class="fa-solid fa-wand-magic-sparkles mr-2"></i> Suggest treatment
			{/if}
		</button>
	</div>

	{#if panel.kind === 'idle'}
		<p class="text-sm text-surface-600-400">
			Ask the local AI assistant to suggest a treatment for this risk, based on its ratings,
			threats, assets, and controls. This never changes the risk &mdash; you decide what to do with
			the suggestion.
		</p>
	{:else if panel.kind === 'unauthorized'}
		<p class="text-sm text-error-600-400" data-testid="risk-treatment-suggestion-unauthorized">
			You are not authorized to request an AI treatment suggestion for this risk scenario.
		</p>
	{:else if panel.kind === 'error'}
		<p class="text-sm text-error-600-400" data-testid="risk-treatment-suggestion-error">
			The AI suggestion could not be completed: {panel.message}
		</p>
	{:else if panel.kind === 'result'}
		{@const result = panel.result}
		<div class="space-y-3" data-testid="risk-treatment-suggestion-result">
			<p
				class="text-xs font-semibold rounded bg-surface-100-900 px-2 py-1"
				data-testid="risk-treatment-suggestion-advisory"
			>
				This is an AI recommendation and has not changed the risk.
			</p>

			{#if result.suggested_treatment}
				<div class="flex items-center gap-2 flex-wrap">
					<span class="text-sm">{outcomeMessage(result.outcome)}:</span>
					<span class="badge preset-tonal-primary">{treatmentLabel(result.suggested_treatment)}</span>
					<span class="text-xs text-surface-500">
						confidence {confidencePercent(result.confidence)}%
					</span>
				</div>
			{:else}
				<p class="text-sm font-semibold" data-testid="risk-treatment-suggestion-none">
					{outcomeMessage(result.outcome)}
				</p>
			{/if}

			<div>
				<div class="text-xs font-semibold text-surface-600-400">Why</div>
				<p class="text-sm">{result.rationale}</p>
			</div>

			{#if result.mitigating_actions.length > 0}
				<div>
					<div class="text-xs font-semibold text-surface-600-400">Suggested mitigating actions</div>
					<ul class="space-y-1">
						{#each result.mitigating_actions as action}
							<li class="text-sm">
								<span class={priorityBadgeClass(action.priority)}>{action.priority}</span>
								<span class="font-semibold">{action.title}</span>
								{#if action.description}
									<span class="text-surface-600-400"> &mdash; {action.description}</span>
								{/if}
							</li>
						{/each}
					</ul>
				</div>
			{/if}

			{#if result.considerations.length > 0}
				<div>
					<div class="text-xs font-semibold text-surface-600-400">Considerations and assumptions</div>
					<ul class="list-disc list-inside text-sm">
						{#each result.considerations as consideration}
							<li>{consideration}</li>
						{/each}
					</ul>
				</div>
			{/if}

			{#if result.warnings.length > 0}
				<ul class="text-xs text-warning-600-400">
					{#each result.warnings as warning}
						<li>{warning}</li>
					{/each}
				</ul>
			{/if}

			<p class="text-xs text-surface-500 italic">{result.advisory_notice}</p>

			{#if editHref && result.suggested_treatment}
				<a href={editHref} class="btn preset-tonal-surface btn-sm" data-testid="risk-treatment-suggestion-edit">
					<i class="fa-solid fa-pen-to-square mr-2"></i> Review and edit the risk scenario
				</a>
			{/if}
		</div>
	{/if}
</div>
