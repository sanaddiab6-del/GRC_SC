import { BASE_API_URL } from '$lib/utils/constants';
import type { RequestEvent } from '@sveltejs/kit';

/**
 * Shared authenticated backend call for every AI onboarding step (Steps 1 through 12B).
 *
 * The AI onboarding proxies are `+server.ts` endpoints and form actions, so the
 * `(app)/+layout.server.ts` session guard never runs for them. When the session token cookie
 * is gone, `handleFetch` skips the `Authorization` header and the request used to reach
 * Django anonymously, which DRF answers with
 * `{"detail": "Authentication credentials were not provided."}`.
 *
 * Credentials are forwarded explicitly here, using the same pattern as the authenticated
 * fetch in `(app)/(internal)/analytics/+page.server.ts`.
 */

/** Session token cookie names, in the same order the rest of the app reads them. */
function sessionToken(event: RequestEvent): string {
	return (
		event.cookies.get('token') ||
		event.cookies.get('access_token') ||
		event.cookies.get('auth_token') ||
		event.cookies.get('knox_token') ||
		''
	);
}

export const AI_ONBOARDING_SESSION_EXPIRED = {
	detail:
		'Your session is no longer authenticated. Sign in again before running AI onboarding steps.'
};

/**
 * An AI onboarding request may only be proxied when the caller carries a session token.
 *
 * The check is deliberately limited to the credential itself rather than `locals.user`: the
 * backend stays the sole authority on whether the token is valid, so this can never refuse a
 * request that would otherwise have been authenticated.
 */
export function hasAiOnboardingSession(event: RequestEvent): boolean {
	return Boolean(sessionToken(event));
}

/** Posts an AI onboarding payload to the backend with the caller's own credentials attached. */
export function fetchAiOnboardingBackend(
	event: RequestEvent,
	endpoint: string,
	payload: unknown
): Promise<Response> {
	const headers = new Headers({ 'Content-Type': 'application/json' });

	const cookieHeader = event.request.headers.get('cookie');
	if (cookieHeader) headers.set('cookie', cookieHeader);

	const token = sessionToken(event);
	if (token) headers.set('Authorization', `Token ${token}`);

	// The CSRF token is deliberately left to `handleFetch`, which appends it for unsafe
	// methods. Setting it here as well would send a duplicated X-CSRFToken header.

	return event.fetch(`${BASE_API_URL}${endpoint}`, {
		method: 'POST',
		headers,
		body: JSON.stringify(payload)
	});
}
