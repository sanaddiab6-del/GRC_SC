/**
 * Pure logic for the "AI Freshness Review" panel on the Evidence detail page: the fetch
 * wrapper and the status -> label/badge mapping. Kept out of the .svelte component so it can
 * be unit tested the same way the rest of this app's AI-facing logic is (see
 * Assets/assetCommitDecisions.ts, AiOnboarding/aiOnboardingState.svelte.ts).
 */

export type FreshnessStatus =
	| 'CURRENT'
	| 'REVIEW_RECOMMENDED'
	| 'POSSIBLY_OUTDATED'
	| 'INSUFFICIENT_CONTEXT';

export interface EvidenceFreshnessReviewResult {
	evidence_id: string;
	evidence_name: string;
	freshness_status: FreshnessStatus;
	confidence: number;
	explanation: string;
	concerns: string[];
	recommended_action: string;
	linked_applied_controls_count: number;
	linked_requirement_assessments_count: number;
	linked_findings_count: number;
	revision_count: number;
	provider_mode: string;
	warnings: string[];
	advisory_notice: string;
	reviewed_at: string;
}

export type EvidenceFreshnessReviewOutcome =
	| { state: 'success'; result: EvidenceFreshnessReviewResult }
	| { state: 'error'; message: string }
	| { state: 'unauthorized' };

/**
 * A short, non-alarming label for each status. Deliberately phrased as a suggestion to a
 * human ("recommend checking") rather than a verdict ("is invalid"), per the platform's AI
 * safety rule: AI recommends, a human decides.
 */
export function freshnessStatusLabel(status: FreshnessStatus): string {
	switch (status) {
		case 'CURRENT':
			return 'Looks current';
		case 'REVIEW_RECOMMENDED':
			return 'Review recommended';
		case 'POSSIBLY_OUTDATED':
			return 'Possibly outdated';
		case 'INSUFFICIENT_CONTEXT':
			return 'Not enough context to assess';
	}
}

/** Skeleton design-system tonal badge class for each status. */
export function freshnessStatusBadgeClass(status: FreshnessStatus): string {
	switch (status) {
		case 'CURRENT':
			return 'badge preset-tonal-success';
		case 'REVIEW_RECOMMENDED':
			return 'badge preset-tonal-warning';
		case 'POSSIBLY_OUTDATED':
			return 'badge preset-tonal-error';
		case 'INSUFFICIENT_CONTEXT':
			return 'badge preset-tonal-surface';
	}
}

function isFreshnessReviewResult(value: unknown): value is EvidenceFreshnessReviewResult {
	return (
		!!value &&
		typeof value === 'object' &&
		typeof (value as Record<string, unknown>).freshness_status === 'string' &&
		typeof (value as Record<string, unknown>).evidence_id === 'string'
	);
}

/**
 * Calls the fe-api proxy for one evidence item and normalizes every backend outcome
 * (success, guardrail rejection, not-found/forbidden, network failure) into one outcome type,
 * so the component never has to guess what a given status code or empty body means.
 */
export async function fetchEvidenceFreshnessReview(
	fetchFn: typeof fetch,
	evidenceId: string
): Promise<EvidenceFreshnessReviewOutcome> {
	let response: Response;
	try {
		response = await fetchFn(`/fe-api/evidences/${evidenceId}/ai-freshness-review`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: '{}'
		});
	} catch {
		return { state: 'error', message: 'The AI review request could not be sent.' };
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
			body && typeof body === 'object' && typeof (body as any).detail === 'string'
				? (body as any).detail
				: 'The AI review could not be completed.';
		return { state: 'error', message: detail };
	}

	if (!isFreshnessReviewResult(body)) {
		return { state: 'error', message: 'The AI review response was not understood.' };
	}

	return { state: 'success', result: body };
}
