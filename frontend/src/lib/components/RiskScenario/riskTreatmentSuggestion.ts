/**
 * Pure logic for the "AI Treatment Suggestion" panel on the Risk Scenario detail page: the fetch
 * wrapper, response normalization, and display mapping. Kept out of the .svelte component so it
 * can be unit tested the same way as Evidence/evidenceFreshnessReview.ts.
 */

export type SuggestableTreatment = 'mitigate' | 'accept' | 'avoid' | 'transfer';
export type SuggestionOutcome = 'suggested' | 'insufficient_context' | 'provider_unavailable';
export type ActionPriority = 'P1' | 'P2' | 'P3' | 'P4';

export interface MitigatingAction {
	title: string;
	description: string;
	priority: ActionPriority;
}

export interface RiskTreatmentSuggestion {
	risk_scenario_id: string;
	risk_scenario_name: string;
	current_treatment: string;
	outcome: SuggestionOutcome;
	suggested_treatment: SuggestableTreatment | null;
	confidence: number;
	rationale: string;
	mitigating_actions: MitigatingAction[];
	considerations: string[];
	is_rated: boolean;
	linked_assets_count: number;
	linked_threats_count: number;
	existing_controls_count: number;
	planned_controls_count: number;
	provider_mode: string;
	warnings: string[];
	advisory_notice: string;
	reviewed_at: string;
}

export type RiskTreatmentSuggestionOutcome =
	| { state: 'success'; result: RiskTreatmentSuggestion }
	| { state: 'error'; message: string }
	| { state: 'unauthorized' };

const SUGGESTABLE_TREATMENTS: readonly string[] = ['mitigate', 'accept', 'avoid', 'transfer'];
const OUTCOMES: readonly string[] = ['suggested', 'insufficient_context', 'provider_unavailable'];

/** Phrased as a recommendation, never as a decision that was taken. */
export function treatmentLabel(treatment: SuggestableTreatment): string {
	switch (treatment) {
		case 'mitigate':
			return 'Mitigate';
		case 'accept':
			return 'Accept';
		case 'avoid':
			return 'Avoid';
		case 'transfer':
			return 'Transfer';
	}
}

export function outcomeMessage(outcome: SuggestionOutcome): string {
	switch (outcome) {
		case 'suggested':
			return 'AI suggests considering this treatment';
		case 'insufficient_context':
			return 'Not enough context to suggest a treatment';
		case 'provider_unavailable':
			return 'The local AI assistant is unavailable';
	}
}

/** Skeleton tonal badge classes, matching the action-priority order P1 (highest) to P4. */
export function priorityBadgeClass(priority: ActionPriority): string {
	switch (priority) {
		case 'P1':
			return 'badge preset-tonal-error';
		case 'P2':
			return 'badge preset-tonal-warning';
		case 'P3':
			return 'badge preset-tonal-secondary';
		case 'P4':
			return 'badge preset-tonal-surface';
	}
}

export function confidencePercent(confidence: number): number {
	if (!Number.isFinite(confidence)) return 0;
	return Math.round(Math.min(1, Math.max(0, confidence)) * 100);
}

/**
 * Only a body with the exact contract the backend guarantees is treated as a result. Anything
 * else (an unrelated JSON shape, a treatment outside the real vocabulary, a "suggested" outcome
 * with no treatment) is an error, never a fabricated success.
 */
function isSuggestion(value: unknown): value is RiskTreatmentSuggestion {
	if (!value || typeof value !== 'object') return false;
	const v = value as Record<string, unknown>;
	if (typeof v.risk_scenario_id !== 'string' || typeof v.outcome !== 'string') return false;
	if (!OUTCOMES.includes(v.outcome)) return false;
	if (!Array.isArray(v.mitigating_actions) || !Array.isArray(v.considerations)) return false;
	if (v.outcome === 'suggested') {
		return typeof v.suggested_treatment === 'string' && SUGGESTABLE_TREATMENTS.includes(v.suggested_treatment);
	}
	return v.suggested_treatment === null;
}

export async function fetchRiskTreatmentSuggestion(
	fetchFn: typeof fetch,
	riskScenarioId: string
): Promise<RiskTreatmentSuggestionOutcome> {
	let response: Response;
	try {
		response = await fetchFn(`/risk-scenarios/${riskScenarioId}/ai-treatment-suggestion`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: '{}'
		});
	} catch {
		return { state: 'error', message: 'The AI suggestion request could not be sent.' };
	}

	if (response.status === 401 || response.status === 403) {
		return { state: 'unauthorized' };
	}

	let body: unknown = null;
	try {
		body = await response.json();
	} catch {
		body = null;
	}

	if (!response.ok) {
		const detail =
			body && typeof body === 'object' && typeof (body as { detail?: unknown }).detail === 'string'
				? (body as { detail: string }).detail
				: 'The AI suggestion could not be completed.';
		return { state: 'error', message: detail };
	}

	if (!isSuggestion(body)) {
		return { state: 'error', message: 'The AI suggestion response was not understood.' };
	}

	return { state: 'success', result: body };
}
