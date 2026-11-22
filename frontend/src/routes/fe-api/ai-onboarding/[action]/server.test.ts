import { describe, expect, it, vi } from 'vitest';

const { POST } = await import('./+server');

/**
 * Every onboarding step now posts to this one route, whichever page it renders on, so the
 * action-to-endpoint mapping, the session refusal, and the unknown-action refusal are what keep
 * a step from reaching the wrong backend service or reaching Django anonymously.
 */
function authenticatedEvent(action: string, fetch: any, body?: string) {
	const cookies = new Map([
		['token', 'session-token'],
		['csrftoken', 'session-csrf']
	]);
	return {
		fetch,
		locals: { user: { id: 'user-1' } },
		cookies: { get: (name: string) => cookies.get(name) },
		params: { action },
		request: new Request(`http://localhost/fe-api/ai-onboarding/${action}`, {
			method: 'POST',
			headers: {
				cookie: 'token=session-token; csrftoken=session-csrf',
				'content-type': 'application/json'
			},
			body
		}),
		url: new URL(`http://localhost/fe-api/ai-onboarding/${action}`)
	} as any;
}

describe('shared AI onboarding proxy', () => {
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
	])('proxies %s with the caller credentials', async (action, expectedEndpoint) => {
		const backendPayload = { provider_mode: 'configured_local_provider', candidates: [{ id: 1 }] };
		const fetch = vi.fn().mockResolvedValue(
			new Response(JSON.stringify(backendPayload), {
				status: 200,
				headers: { 'Content-Type': 'application/json' }
			})
		);

		const response = await POST(
			authenticatedEvent(action, fetch, JSON.stringify({ sample: true }))
		);

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

	it('forwards the backend status and body when a step is refused', async () => {
		const backendError = { detail: 'Approved commit requires a successful dry-run.' };
		const fetch = vi.fn().mockResolvedValue(
			new Response(JSON.stringify(backendError), {
				status: 400,
				headers: { 'Content-Type': 'application/json' }
			})
		);

		const response = await POST(
			authenticatedEvent('aiRiskScenarioCommit', fetch, JSON.stringify({ dry_run: false }))
		);

		expect(response.status).toBe(400);
		expect(await response.json()).toEqual(backendError);
	});

	it('refuses an unauthenticated AI request instead of proxying it anonymously', async () => {
		const fetch = vi.fn();

		const response = await POST({
			fetch,
			cookies: { get: () => undefined },
			params: { action: 'aiFrameworkControlMappingSuggest' },
			request: new Request(
				'http://localhost/fe-api/ai-onboarding/aiFrameworkControlMappingSuggest',
				{
					method: 'POST',
					headers: { 'content-type': 'application/json' },
					body: JSON.stringify({ sample: true })
				}
			),
			url: new URL('http://localhost/fe-api/ai-onboarding/aiFrameworkControlMappingSuggest')
		} as any);

		expect(response.status).toBe(401);
		expect(fetch).not.toHaveBeenCalled();
		expect((await response.json()).detail).toContain('Sign in again');
	});

	it('refuses an unknown action before checking anything else', async () => {
		const fetch = vi.fn();

		const response = await POST(
			authenticatedEvent('aiSomethingElse', fetch, JSON.stringify({ sample: true }))
		);

		expect(response.status).toBe(404);
		expect(fetch).not.toHaveBeenCalled();
	});

	it('refuses a malformed payload without calling the backend', async () => {
		const fetch = vi.fn();

		const response = await POST(authenticatedEvent('aiAssetSuggest', fetch, 'not json'));

		expect(response.status).toBe(400);
		expect(fetch).not.toHaveBeenCalled();
		expect((await response.json()).detail).toBe('Invalid AI request payload.');
	});
});
