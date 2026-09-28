import { describe, expect, it, vi } from 'vitest';

const { POST } = await import('./+server');

function event(fetch: any, { token = 'session-token' }: { token?: string | null } = {}) {
	const cookies = new Map<string, string>();
	if (token) cookies.set('token', token);
	return {
		fetch,
		params: { id: 'rs-1' },
		cookies: { get: (name: string) => cookies.get(name) },
		request: new Request('http://localhost/risk-scenarios/rs-1/ai-treatment-suggestion', {
			method: 'POST',
			headers: {
				'content-type': 'application/json',
				...(token ? { cookie: `token=${token}` } : {})
			},
			body: '{}'
		})
	} as any;
}

function backend(body: unknown, status = 200) {
	return vi.fn().mockResolvedValue(
		new Response(typeof body === 'string' ? body : JSON.stringify(body), {
			status,
			headers: { 'Content-Type': typeof body === 'string' ? 'text/html' : 'application/json' }
		})
	);
}

describe('risk treatment suggestion proxy', () => {
	it('refuses to proxy a request with no session token, and never calls Django', async () => {
		const fetch = backend({ outcome: 'suggested' });

		const response = await POST(event(fetch, { token: null }));

		expect(response.status).toBe(401);
		expect(fetch).not.toHaveBeenCalled();
	});

	it('forwards a POST with the caller credentials to the backend action for this scenario', async () => {
		const fetch = backend({ outcome: 'suggested', suggested_treatment: 'mitigate' });

		const response = await POST(event(fetch));

		expect(fetch).toHaveBeenCalledTimes(1);
		const [url, init] = fetch.mock.calls[0];
		expect(url).toContain('/risk-scenarios/rs-1/ai-treatment-suggestion/');
		expect(init.method).toBe('POST');
		expect(new Headers(init.headers).get('Authorization')).toBe('Token session-token');
		expect(response.status).toBe(200);
		expect((await response.json()).suggested_treatment).toBe('mitigate');
	});

	it.each([401, 403, 404, 422])('relays a %i from Django unchanged', async (status) => {
		const fetch = backend({ detail: 'backend said no' }, status);

		const response = await POST(event(fetch));

		expect(response.status).toBe(status);
		expect((await response.json()).detail).toBe('backend said no');
	});

	it('replaces a backend 5xx with a generic message instead of relaying it', async () => {
		const fetch = backend('<html>Traceback: LOCAL_AI_BASE_URL=http://127.0.0.1:11434</html>', 500);

		const response = await POST(event(fetch));
		const text = await response.text();

		expect(response.status).toBe(502);
		expect(text).not.toMatch(/Traceback|11434|127\.0\.0\.1|LOCAL_AI_BASE_URL/);
	});

	it('replaces a non-JSON 2xx body with a generic error instead of relaying it', async () => {
		const fetch = backend('<html>unexpected</html>', 200);

		const response = await POST(event(fetch));

		expect(response.status).toBe(502);
		expect(await response.text()).not.toContain('<html>');
	});

	it('returns a generic 502 when the backend cannot be reached at all', async () => {
		const fetch = vi.fn().mockRejectedValue(new TypeError('fetch failed: ECONNREFUSED 127.0.0.1'));

		const response = await POST(event(fetch));

		expect(response.status).toBe(502);
		expect(await response.text()).not.toContain('ECONNREFUSED');
	});
});
