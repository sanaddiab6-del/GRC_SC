<script lang="ts">
	import {
		fetchEvidenceFreshnessReview,
		freshnessStatusBadgeClass,
		freshnessStatusLabel,
		type EvidenceFreshnessReviewResult
	} from './evidenceFreshnessReview';

	/**
	 * "AI Freshness Review" panel shown on an Evidence's own detail page.
	 *
	 * Advisory only: it calls the local AI provider through the backend's
	 * evidences/{id}/ai-freshness-review action and only ever displays the result. Nothing
	 * here writes to the Evidence, its revisions, or anything it is linked to — the phrasing
	 * is deliberately "AI review recommends checking this evidence", never "AI determined
	 * this evidence is invalid", so the human reviewing it stays the one making the call.
	 *
	 * No separate view-permission prop: this only renders on an Evidence detail page the
	 * caller already loaded, which itself required view_evidence. The backend action re-checks
	 * that same permission independently (never trust the frontend for authorization), so an
	 * unauthorized `evidenceId` still fails safely with the "unauthorized" panel state below.
	 */
	interface Props {
		evidenceId: string;
	}

	let { evidenceId }: Props = $props();

	type PanelState =
		| { kind: 'idle' }
		| { kind: 'loading' }
		| { kind: 'result'; result: EvidenceFreshnessReviewResult }
		| { kind: 'unauthorized' }
		| { kind: 'error'; message: string };

	let panel = $state<PanelState>({ kind: 'idle' });

	async function runReview() {
		panel = { kind: 'loading' };
		const outcome = await fetchEvidenceFreshnessReview(fetch, evidenceId);
		if (outcome.state === 'success') {
			panel = { kind: 'result', result: outcome.result };
		} else if (outcome.state === 'unauthorized') {
			panel = { kind: 'unauthorized' };
		} else {
			panel = { kind: 'error', message: outcome.message };
		}
	}
</script>

{#if evidenceId}
	<div class="card p-4 space-y-3" data-testid="evidence-freshness-review">
		<div class="flex items-center justify-between">
			<h3 class="h4">AI Freshness Review</h3>
			<button
				type="button"
				class="btn preset-tonal-primary btn-sm"
				disabled={panel.kind === 'loading'}
				onclick={runReview}
				data-testid="evidence-freshness-review-button"
			>
				{#if panel.kind === 'loading'}
					<i class="fa-solid fa-spinner fa-spin mr-2"></i> Reviewing...
				{:else}
					<i class="fa-solid fa-wand-magic-sparkles mr-2"></i> Review freshness
				{/if}
			</button>
		</div>

		{#if panel.kind === 'idle'}
			<p class="text-sm text-surface-600-400">
				Ask the local AI assistant whether this evidence still looks current, based on its
				age, status, and what it is linked to. This never changes the evidence &mdash; you
				decide what to do with the result.
			</p>
		{:else if panel.kind === 'unauthorized'}
			<p class="text-sm text-error-600-400" data-testid="evidence-freshness-review-unauthorized">
				You are not authorized to run an AI freshness review on this evidence.
			</p>
		{:else if panel.kind === 'error'}
			<p class="text-sm text-error-600-400" data-testid="evidence-freshness-review-error">
				The AI review could not be completed: {panel.message}
			</p>
		{:else if panel.kind === 'result'}
			{@const result = panel.result}
			<div class="space-y-2" data-testid="evidence-freshness-review-result">
				<div class="flex items-center gap-2 flex-wrap">
					<span class={freshnessStatusBadgeClass(result.freshness_status)}>
						{freshnessStatusLabel(result.freshness_status)}
					</span>
					<span class="text-xs text-surface-500">
						AI review recommends checking this evidence &mdash; confidence {Math.round(
							result.confidence * 100
						)}%
					</span>
				</div>

				<p class="text-sm">{result.explanation}</p>

				{#if result.concerns.length > 0}
					<div>
						<div class="text-xs font-semibold text-surface-600-400">Concerns noted</div>
						<ul class="list-disc list-inside text-sm">
							{#each result.concerns as concern}
								<li>{concern}</li>
							{/each}
						</ul>
					</div>
				{/if}

				<div>
					<div class="text-xs font-semibold text-surface-600-400">Suggested next step</div>
					<p class="text-sm">{result.recommended_action}</p>
				</div>

				{#if result.warnings.length > 0}
					<ul class="text-xs text-warning-600-400">
						{#each result.warnings as warning}
							<li>{warning}</li>
						{/each}
					</ul>
				{/if}

				<p class="text-xs text-surface-500 italic">{result.advisory_notice}</p>
			</div>
		{/if}
	</div>
{/if}
