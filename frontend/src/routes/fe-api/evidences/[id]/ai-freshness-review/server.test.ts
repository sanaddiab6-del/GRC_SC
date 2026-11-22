import { describe, expect, it, vi } from 'vitest';

const { POST } = await import('./+server');

function event(fetch: any, id: string, body?: string) {
	return {
		fetch,
		params: { id },
		request: new Request(`http://localhost/fe-api/evidences/${id}/ai-freshness-review`, {
			method: 'POST',
			headers: { 'content-type': 'application/json' },
			body
		})
	} as any;
}

describe('evidence AI freshness review proxy', () => {
	it('forwards to the backend evidence freshness review action for the given evidence id', async () => {
		const backendPayload = {
			evidence_id: 'ev-1',
			freshness_status: 'REVIEW_RECOMMENDED',
			confidence: 0.6
		};
		const fetch = vi.fn().mockResolvedValue(
			new Response(JSON.stringify(backendPayload), {
				status: 200,
				headers: { 'Content-Type': 'application/json' }
			})
		);

		const response = await POST(event(fetch, 'ev-1', '{}'));

		expect(fetch).toHaveBeenCalledTimes(1);
		const [calledUrl, calledInit] = fetch.mock.calls[0];
		expect(calledUrl).toContain('/evidences/ev-1/ai-freshness-review/');
		expect(calledInit.method).toBe('POST');
		expect(response.status).toBe(200);
		expect(await response.json()).toEqual(backendPayload);
	});

	it('relays a non-200 backend status (not found) instead of masking it', async () => {
		const fetch = vi.fn().mockResolvedValue(
			new Response(JSON.stringify({ detail: 'Not found.' }), {
				status: 404,
				headers: { 'Content-Type': 'application/json' }
			})
		);

		const response = await POST(event(fetch, 'unknown-id', '{}'));

		expect(response.status).toBe(404);
	});

	it('relays a 401 from Django unchanged when the caller has no valid session', async () => {
		// hooks.server.ts attaches the Authorization header only when a session/token cookie
		// is present; an anonymous caller reaches this route with none, so the request this
		// proxy forwards has no token and Django's own IsAuthenticated check returns 401. The
		// proxy must relay that 401 as-is, never substitute a 200 or swallow it.
		const fetch = vi.fn().mockResolvedValue(
			new Response(JSON.stringify({ detail: 'Authentication credentials were not provided.' }), {
				status: 401,
				headers: { 'Content-Type': 'application/json' }
			})
		);

		const response = await POST(event(fetch, 'ev-1', '{}'));

		expect(response.status).toBe(401);
	});

	it('relays a 403 from Django unchanged for an authenticated but unauthorized caller', async () => {
		const fetch = vi.fn().mockResolvedValue(
			new Response(JSON.stringify({ detail: 'You do not have permission to perform this action.' }), {
				status: 403,
				headers: { 'Content-Type': 'application/json' }
			})
		);

		const response = await POST(event(fetch, 'ev-1', '{}'));

		expect(response.status).toBe(403);
	});

	it('never exposes AI provider configuration in a relayed error body', async () => {
		// The backend already sanitizes provider errors (build_sanitized_provider_detail); this
		// asserts the proxy does not add any config of its own on top of whatever it relays.
		const fetch = vi.fn().mockResolvedValue(
			new Response(
				JSON.stringify({
					error_code: 'ai_provider_request_failed',
					detail: 'The configured AI provider could not be reached or returned an unreadable response.'
				}),
				{ status: 422, headers: { 'Content-Type': 'application/json' } }
			)
		);

		const response = await POST(event(fetch, 'ev-1', '{}'));
		const body = await response.text();

		expect(body).not.toMatch(/11434|localhost|ollama:\/\/|LOCAL_AI_BASE_URL/i);
	});

	it('relays a guardrail rejection (422) from the backend unchanged', async () => {
		const fetch = vi.fn().mockResolvedValue(
			new Response(
				JSON.stringify({
					error_code: 'ai_evidence_freshness_review_guardrails_failed',
					detail: 'blocked'
				}),
				{ status: 422, headers: { 'Content-Type': 'application/json' } }
			)
		);

		const response = await POST(event(fetch, 'ev-1', '{}'));

		expect(response.status).toBe(422);
		expect((await response.json()).error_code).toBe(
			'ai_evidence_freshness_review_guardrails_failed'
		);
	});

	it('sends an empty JSON object when the caller sends no body', async () => {
		const fetch = vi.fn().mockResolvedValue(
			new Response(JSON.stringify({}), { status: 200 })
		);

		await POST(event(fetch, 'ev-1', undefined));

		const [, calledInit] = fetch.mock.calls[0];
		expect(calledInit.body).toBe('{}');
	});
});
