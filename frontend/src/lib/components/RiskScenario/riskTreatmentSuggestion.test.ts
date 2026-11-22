import { describe, expect, it, vi } from 'vitest';
import {
	confidencePercent,
	fetchRiskTreatmentSuggestion,
	outcomeMessage,
	priorityBadgeClass,
	treatmentLabel,
	type RiskTreatmentSuggestion
} from './riskTreatmentSuggestion';

function suggestion(overrides: Partial<RiskTreatmentSuggestion> = {}): RiskTreatmentSuggestion {
	return {
		risk_scenario_id: 'rs-1',
		risk_scenario_name: 'Unauthorized privileged access',
		current_treatment: 'open',
		outcome: 'suggested',
		suggested_treatment: 'mitigate',
		confidence: 0.72,
		rationale: 'Current risk is above tolerance.',
		mitigating_actions: [
			{ title: 'Roll out PAM', description: 'Recommend PAM for admins.', priority: 'P1' }
		],
		considerations: ['Assumes budget is available.'],
		is_rated: true,
		linked_assets_count: 1,
		linked_threats_count: 1,
		existing_controls_count: 1,
		planned_controls_count: 1,
		provider_mode: 'configured_local_provider',
		warnings: [],
		advisory_notice: 'AI suggestion only. This has not changed the risk scenario.',
		reviewed_at: '2026-09-28T10:00:00Z',
		...overrides
	};
}

function respond(body: unknown, status = 200) {
	return vi.fn().mockResolvedValue(
		new Response(typeof body === 'string' ? body : JSON.stringify(body), {
			status,
			headers: { 'Content-Type': 'application/json' }
		})
	);
}

describe('display helpers', () => {
	it('labels every real treatment and phrases outcomes as advice, not a decision', () => {
		expect(['mitigate', 'accept', 'avoid', 'transfer'].map((t) => treatmentLabel(t as any))).toEqual([
			'Mitigate',
			'Accept',
			'Avoid',
			'Transfer'
		]);
		const suggested = outcomeMessage('suggested').toLowerCase();
		expect(suggested).toContain('suggests');
		for (const word of ['applied', 'accepted', 'changed', 'decided']) {
			expect(suggested).not.toContain(word);
		}
	});

	it('maps each action priority to a distinct badge, highest priority as the strongest', () => {
		const classes = (['P1', 'P2', 'P3', 'P4'] as const).map(priorityBadgeClass);
		expect(new Set(classes).size).toBe(4);
		expect(priorityBadgeClass('P1')).toContain('error');
	});

	it('clamps and rounds confidence for display', () => {
		expect(confidencePercent(0.724)).toBe(72);
		expect(confidencePercent(1.7)).toBe(100);
		expect(confidencePercent(-1)).toBe(0);
		expect(confidencePercent(Number.NaN)).toBe(0);
	});
});

describe('fetchRiskTreatmentSuggestion', () => {
	it('posts to the route-local proxy for the given scenario and returns the result', async () => {
		const fetchFn = respond(suggestion());

		const outcome = await fetchRiskTreatmentSuggestion(fetchFn as any, 'rs-1');

		expect(fetchFn).toHaveBeenCalledWith(
			'/risk-scenarios/rs-1/ai-treatment-suggestion',
			expect.objectContaining({ method: 'POST' })
		);
		expect(outcome.state).toBe('success');
		if (outcome.state === 'success') {
			expect(outcome.result.suggested_treatment).toBe('mitigate');
			expect(outcome.result.mitigating_actions).toHaveLength(1);
		}
	});

	it.each(['insufficient_context', 'provider_unavailable'] as const)(
		'treats a %s outcome with no treatment as a normal, non-error result',
		async (outcome) => {
			const fetchFn = respond(
				suggestion({ outcome, suggested_treatment: null, confidence: 0, mitigating_actions: [] })
			);

			const result = await fetchRiskTreatmentSuggestion(fetchFn as any, 'rs-1');

			expect(result.state).toBe('success');
			if (result.state === 'success') expect(result.result.suggested_treatment).toBeNull();
		}
	);

	it.each([401, 403])('maps a %i to the unauthorized state', async (status) => {
		const outcome = await fetchRiskTreatmentSuggestion(respond({}, status) as any, 'rs-1');
		expect(outcome.state).toBe('unauthorized');
	});

	it('surfaces the backend detail on a guardrail rejection', async () => {
		const fetchFn = respond(
			{
				error_code: 'ai_risk_treatment_suggestion_guardrails_failed',
				detail: 'Generated advisory risk treatment output violated safety guardrails.'
			},
			422
		);

		const outcome = await fetchRiskTreatmentSuggestion(fetchFn as any, 'rs-1');

		expect(outcome.state).toBe('error');
		if (outcome.state === 'error') expect(outcome.message).toContain('safety guardrails');
	});

	it('never reports success when the request itself fails', async () => {
		const fetchFn = vi.fn().mockRejectedValue(new TypeError('network error'));
		expect((await fetchRiskTreatmentSuggestion(fetchFn as any, 'rs-1')).state).toBe('error');
	});

	it.each([
		['non-JSON body', 'not json'],
		['unrelated JSON', { unrelated: true }],
		['treatment outside the real vocabulary', suggestion({ suggested_treatment: 'ignore' as any })],
		['"suggested" outcome with no treatment', suggestion({ suggested_treatment: null })],
		['no-suggestion outcome that still carries a treatment', suggestion({ outcome: 'insufficient_context' })]
	])('treats a 200 with %s as an error, never a fabricated success', async (_label, body) => {
		const outcome = await fetchRiskTreatmentSuggestion(respond(body) as any, 'rs-1');
		expect(outcome.state).toBe('error');
	});
});
