import { fetchAiOnboardingBackend, hasAiOnboardingSession } from '$lib/utils/aiOnboardingProxy';
import type { RequestHandler } from './$types';

/**
 * Proxies the advisory, read-only AI risk treatment suggestion to Django.
 *
 * `+server.ts` routes do not run the `(app)` layout session guard, so this refuses to proxy a
 * request that carries no session token instead of letting it reach Django anonymously, and
 * forwards the caller's own credentials explicitly (the shared AI proxy helpers). Django remains
 * the sole authority on the token, the RBAC-scoped queryset, and every AI guardrail.
 */

const SESSION_REQUIRED = {
	detail: 'Your session is no longer authenticated. Sign in again to request an AI suggestion.'
};
const BACKEND_UNAVAILABLE = { detail: 'The AI suggestion service is temporarily unavailable.' };

function json(body: unknown, status: number) {
	return new Response(JSON.stringify(body), {
		status,
		headers: { 'Content-Type': 'application/json' }
	});
}

export const POST: RequestHandler = async (event) => {
	if (!hasAiOnboardingSession(event)) {
		return json(SESSION_REQUIRED, 401);
	}

	let response: Response;
	try {
		response = await fetchAiOnboardingBackend(
			event,
			`/risk-scenarios/${event.params.id}/ai-treatment-suggestion/`,
			{}
		);
	} catch {
		return json(BACKEND_UNAVAILABLE, 502);
	}

	// Never relay a server error page or any non-JSON body: in DEBUG that could be a traceback.
	if (response.status >= 500) {
		return json(BACKEND_UNAVAILABLE, 502);
	}
	let body: unknown;
	try {
		body = await response.json();
	} catch {
		return json(BACKEND_UNAVAILABLE, 502);
	}
	return json(body, response.status);
};
