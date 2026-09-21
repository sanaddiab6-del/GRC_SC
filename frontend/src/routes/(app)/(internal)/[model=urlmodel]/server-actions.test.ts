import { describe, expect, it, vi } from 'vitest';

// `getModelInfo` is only reached by the GET handler, but importing it pulls in the whole
// ModelTable component tree and its `$app/*` virtual modules, which do not exist outside the
// SvelteKit plugin. Stubbing it keeps these tests on the POST/AI-proxy path under test.
vi.mock('$lib/utils/crud', () => ({
	getModelInfo: (model: string) => ({ urlModel: model, endpointUrl: model })
}));

const { POST } = await import('./+server');

/**
 * The AI onboarding client posts the step payload as a form field named `payload`.
 *
 * The body is serialized here and the content type is set explicitly: jsdom's `FormData` and
 * `URLSearchParams` are not the ones the global `Request` recognizes, so passing either as a
 * body silently degrades to `text/plain` and would exercise the malformed-payload branch
 * instead of the proxy path under test.
 */
const AI_REQUEST_CONTENT_TYPE = 'application/x-www-form-urlencoded';

function aiRequestBody(payload: unknown = { sample: true }) {
	return new URLSearchParams({ payload: JSON.stringify(payload) }).toString();
}

function authenticatedEvent(action: string, fetch: any, body?: string) {
	const cookies = new Map([
		['token', 'session-token'],
		['csrftoken', 'session-csrf']
	]);
	return {
		fetch,
		locals: { user: { id: 'user-1' } },
		cookies: { get: (name: string) => cookies.get(name) },
		params: { model: 'assets' },
		request: new Request(`http://localhost/assets?/${action}`, {
			method: 'POST',
			headers: {
				cookie: 'token=session-token; csrftoken=session-csrf',
				'content-type': AI_REQUEST_CONTENT_TYPE
			},
			body
		}),
		url: new URL(`http://localhost/assets?/${action}`)
	} as any;
}

describe('[model=urlmodel] route POST AI actions', () => {
	it.each([
		['aiAssetSuggest', '/ai/onboarding/assets/suggest/'],
		['aiAssetCommit', '/ai/onboarding/assets/commit/'],
		['aiAppliedControlSuggest', '/ai/onboarding/applied-controls/suggest/'],
		['aiAppliedControlCommit', '/ai/onboarding/applied-controls/commit/'],
		['aiEvidenceFindingSuggest', '/ai/onboarding/evidence-findings/suggest/'],
		['aiEvidenceFindingCommit', '/ai/onboarding/evidence-findings/commit/'],
		['aiRemediationActionSuggest', '/ai/onboarding/remediation-actions/suggest/'],
		['aiRemediationActionCommit', '/ai/onboarding/remediation-actions/commit/'],
		['aiFrameworkControlMappingSuggest', '/ai/onboarding/framework-control-mappings/suggest/'],
		['aiFrameworkControlMappingCommit', '/ai/onboarding/framework-control-mappings/commit/'],
		['aiRiskScenarioSuggest', '/ai/onboarding/risk-scenarios/suggest/'],
		['aiRiskScenarioCommit', '/ai/onboarding/risk-scenarios/commit/'],
		['aiControlEffectivenessSuggest', '/ai/onboarding/control-effectiveness/suggest/'],
		['aiControlEffectivenessCommit', '/ai/onboarding/control-effectiveness/commit/'],
		['aiAuditReadinessSuggest', '/ai/onboarding/audit-readiness/suggest/'],
		['aiAuditReadinessCommit', '/ai/onboarding/audit-readiness/commit/'],
		['aiAuditReportSuggest', '/ai/onboarding/audit-report/suggest/'],
		['aiAuditReportCommit', '/ai/onboarding/audit-report/commit/'],
		['aiFinalReviewSuggest', '/ai/onboarding/final-review/suggest/'],
		['aiFinalReviewCommit', '/ai/onboarding/final-review/commit/']
	])('proxies %s for /assets with the caller credentials', async (action, expectedEndpoint) => {
		const backendPayload = { provider_mode: 'configured_local_provider', candidates: [{ id: 1 }] };
		const fetch = vi.fn().mockResolvedValue(
			new Response(JSON.stringify(backendPayload), {
				status: 200,
				headers: { 'Content-Type': 'application/json' }
			})
		);

		const response = await POST(authenticatedEvent(action, fetch, aiRequestBody()));

		expect(response.status).toBe(200);
		expect(fetch).toHaveBeenCalledWith(expect.stringContaining(expectedEndpoint), {
			method: 'POST',
			headers: expect.any(Headers),
			body: JSON.stringify({ sample: true })
		});

		const headers = fetch.mock.calls[0][1].headers as Headers;
		expect(headers.get('Authorization')).toBe('Token session-token');
		expect(headers.get('cookie')).toBe('token=session-token; csrftoken=session-csrf');
		expect(await response.json()).toEqual(backendPayload);
	});

	it('refuses an unauthenticated AI request instead of proxying it anonymously', async () => {
		const fetch = vi.fn();

		const response = await POST({
			fetch,
			cookies: { get: () => undefined },
			params: { model: 'assets' },
			request: new Request('http://localhost/assets?/aiFrameworkControlMappingSuggest', {
				method: 'POST',
				headers: { 'content-type': AI_REQUEST_CONTENT_TYPE },
				body: aiRequestBody()
			}),
			url: new URL('http://localhost/assets?/aiFrameworkControlMappingSuggest')
		} as any);

		expect(response.status).toBe(401);
		expect(fetch).not.toHaveBeenCalled();
		expect((await response.json()).detail).toContain('Sign in again');
	});

	it('keeps non-AI POSTs on /assets rejected', async () => {
		const response = await POST(authenticatedEvent('unknownAction', vi.fn()));

		expect(response.status).toBe(405);
		expect(await response.json()).toEqual({ detail: 'POST method not allowed' });
	});
});
