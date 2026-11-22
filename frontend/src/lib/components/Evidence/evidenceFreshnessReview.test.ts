import { describe, expect, it, vi } from 'vitest';
import {
	fetchEvidenceFreshnessReview,
	freshnessStatusBadgeClass,
	freshnessStatusLabel,
	type EvidenceFreshnessReviewResult
} from './evidenceFreshnessReview';

function validResult(
	overrides: Partial<EvidenceFreshnessReviewResult> = {}
): EvidenceFreshnessReviewResult {
	return {
		evidence_id: 'ev-1',
		evidence_name: 'MFA configuration export',
		freshness_status: 'REVIEW_RECOMMENDED',
		confidence: 0.62,
		explanation: 'No revision since the linked control changed.',
		concerns: ['Latest revision predates the linked control update.'],
		recommended_action: 'Ask the evidence owner to confirm this is still current.',
		linked_applied_controls_count: 1,
		linked_requirement_assessments_count: 0,
		linked_findings_count: 0,
		revision_count: 1,
		provider_mode: 'configured_local_provider',
		warnings: [],
		advisory_notice: 'AI suggestion only. This review never changes Evidence.',
		reviewed_at: '2026-09-22T10:00:00Z',
		...overrides
	};
}

describe('freshnessStatusLabel / freshnessStatusBadgeClass', () => {
	it('never phrases a status as a verdict about the evidence being invalid', () => {
		for (const status of [
			'CURRENT',
			'REVIEW_RECOMMENDED',
			'POSSIBLY_OUTDATED',
			'INSUFFICIENT_CONTEXT'
		] as const) {
			const label = freshnessStatusLabel(status).toLowerCase();
			expect(label).not.toContain('invalid');
			expect(label).not.toContain('determined');
			expect(label).not.toContain('rejected');
		}
	});

	it('maps each status to a distinct tonal badge class', () => {
		const classes = new Set(
			(['CURRENT', 'REVIEW_RECOMMENDED', 'POSSIBLY_OUTDATED', 'INSUFFICIENT_CONTEXT'] as const).map(
				freshnessStatusBadgeClass
			)
		);
		expect(classes.size).toBe(4);
		expect(freshnessStatusBadgeClass('POSSIBLY_OUTDATED')).toContain('error');
		expect(freshnessStatusBadgeClass('CURRENT')).toContain('success');
	});
});

describe('fetchEvidenceFreshnessReview', () => {
	it('posts to the fe-api proxy for the given evidence id', async () => {
		const fetchFn = vi.fn().mockResolvedValue(
			new Response(JSON.stringify(validResult()), {
				status: 200,
				headers: { 'Content-Type': 'application/json' }
			})
		);

		const outcome = await fetchEvidenceFreshnessReview(fetchFn as any, 'ev-1');

		expect(fetchFn).toHaveBeenCalledWith(
			'/fe-api/evidences/ev-1/ai-freshness-review',
			expect.objectContaining({ method: 'POST' })
		);
		expect(outcome.state).toBe('success');
		if (outcome.state === 'success') {
			expect(outcome.result.freshness_status).toBe('REVIEW_RECOMMENDED');
		}
	});

	it('reports INSUFFICIENT_CONTEXT as a normal success outcome, not an error', async () => {
		const fetchFn = vi.fn().mockResolvedValue(
			new Response(
				JSON.stringify(validResult({ freshness_status: 'INSUFFICIENT_CONTEXT', confidence: 0 })),
				{ status: 200, headers: { 'Content-Type': 'application/json' } }
			)
		);

		const outcome = await fetchEvidenceFreshnessReview(fetchFn as any, 'ev-1');

		expect(outcome.state).toBe('success');
		if (outcome.state === 'success') {
			expect(outcome.result.freshness_status).toBe('INSUFFICIENT_CONTEXT');
		}
	});

	it('maps a 401 to an unauthorized outcome distinct from a generic error', async () => {
		const fetchFn = vi.fn().mockResolvedValue(new Response(null, { status: 401 }));

		const outcome = await fetchEvidenceFreshnessReview(fetchFn as any, 'ev-1');

		expect(outcome.state).toBe('unauthorized');
	});

	it('maps a 403 to an unauthorized outcome', async () => {
		const fetchFn = vi.fn().mockResolvedValue(new Response(null, { status: 403 }));

		const outcome = await fetchEvidenceFreshnessReview(fetchFn as any, 'ev-1');

		expect(outcome.state).toBe('unauthorized');
	});

	it('surfaces the backend detail message on a guardrail rejection', async () => {
		const fetchFn = vi.fn().mockResolvedValue(
			new Response(
				JSON.stringify({
					error_code: 'ai_evidence_freshness_review_guardrails_failed',
					detail: 'Generated advisory evidence freshness output violated safety guardrails.'
				}),
				{ status: 422, headers: { 'Content-Type': 'application/json' } }
			)
		);

		const outcome = await fetchEvidenceFreshnessReview(fetchFn as any, 'ev-1');

		expect(outcome.state).toBe('error');
		if (outcome.state === 'error') {
			expect(outcome.message).toContain('safety guardrails');
		}
	});

	it('never reports success when the network call itself fails', async () => {
		const fetchFn = vi.fn().mockRejectedValue(new TypeError('network error'));

		const outcome = await fetchEvidenceFreshnessReview(fetchFn as any, 'ev-1');

		expect(outcome.state).toBe('error');
	});

	it('treats an unparseable/unexpected 200 body as an error, never a fabricated success', async () => {
		const fetchFn = vi
			.fn()
			.mockResolvedValue(new Response('not json', { status: 200 }));

		const outcome = await fetchEvidenceFreshnessReview(fetchFn as any, 'ev-1');

		expect(outcome.state).toBe('error');
	});

	it('treats a 200 with an unrelated JSON shape as an error, not a false success', async () => {
		const fetchFn = vi.fn().mockResolvedValue(
			new Response(JSON.stringify({ unrelated: true }), {
				status: 200,
				headers: { 'Content-Type': 'application/json' }
			})
		);

		const outcome = await fetchEvidenceFreshnessReview(fetchFn as any, 'ev-1');

		expect(outcome.state).toBe('error');
	});
});
