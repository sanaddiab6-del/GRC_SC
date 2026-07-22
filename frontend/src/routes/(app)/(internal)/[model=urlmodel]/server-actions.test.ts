import { describe, expect, it, vi } from 'vitest';
import { POST } from './+server';

describe('[model=urlmodel] route POST AI actions', () => {
	it.each([
		['aiAssetSuggest', '/ai/onboarding/assets/suggest/'],
		['aiAssetCommit', '/ai/onboarding/assets/commit/'],
		['aiAppliedControlSuggest', '/ai/onboarding/applied-controls/suggest/'],
		['aiAppliedControlCommit', '/ai/onboarding/applied-controls/commit/']
	])('proxies %s for /assets without returning 405', async (action, expectedEndpoint) => {
		const backendPayload = { provider_mode: 'configured_local_provider', candidates: [{ id: 1 }] };
		const fetch = vi.fn().mockResolvedValue(
			new Response(JSON.stringify(backendPayload), {
				status: 200,
				headers: { 'Content-Type': 'application/json' }
			})
		);

		const formData = new FormData();
		formData.set('payload', JSON.stringify({ sample: true }));

		const response = await POST({
			fetch,
			params: { model: 'assets' },
			request: new Request(`http://localhost/assets?/${action}`, {
				method: 'POST',
				body: formData
			}),
			url: new URL(`http://localhost/assets?/${action}`)
		} as any);

		expect(response.status).toBe(200);
		expect(fetch).toHaveBeenCalledWith(expect.stringContaining(expectedEndpoint), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ sample: true })
		});
		expect(await response.json()).toEqual(backendPayload);
	});

	it('keeps non-AI POSTs on /assets rejected', async () => {
		const response = await POST({
			fetch: vi.fn(),
			params: { model: 'assets' },
			request: new Request('http://localhost/assets?/unknownAction', {
				method: 'POST'
			}),
			url: new URL('http://localhost/assets?/unknownAction')
		} as any);

		expect(response.status).toBe(405);
		expect(await response.json()).toEqual({ detail: 'POST method not allowed' });
	});
});