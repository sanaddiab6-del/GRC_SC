import { BASE_API_URL } from '$lib/utils/constants';
import type { RequestHandler } from './$types';

/**
 * Proxies the advisory, read-only AI evidence freshness review to Django. Thin on purpose:
 * authorization, tenant scoping, guardrails, and the local AI call all live in the backend
 * `evidences/{id}/ai-freshness-review/` action, exactly as for reading the evidence itself.
 * `fetch` here is SvelteKit's event-bound fetch, which `hooks.server.ts` already attaches the
 * caller's auth token to, so no session handling is needed in this route (see fe-api/comments
 * for the same pattern on another resource).
 */
export const POST: RequestHandler = async ({ fetch, params, request }) => {
	const body = await request.text();
	const endpoint = `${BASE_API_URL}/evidences/${params.id}/ai-freshness-review/`;
	const res = await fetch(endpoint, {
		method: 'POST',
		body: body || '{}',
		headers: {
			'Content-Type': 'application/json'
		}
	});
	const responseData = await res.text();

	return new Response(responseData, {
		status: res.status,
		headers: {
			'Content-Type': res.headers.get('Content-Type') ?? 'application/json'
		}
	});
};
