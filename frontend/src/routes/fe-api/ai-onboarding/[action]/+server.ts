import {
	AI_ONBOARDING_SESSION_EXPIRED,
	fetchAiOnboardingBackend,
	hasAiOnboardingSession
} from '$lib/utils/aiOnboardingProxy';
import { aiOnboardingEndpoint } from '$lib/utils/aiOnboardingActions';
import type { RequestHandler } from './$types';

/**
 * Shared proxy for every Local AI onboarding step action (Steps 3A through 12B).
 *
 * Each step is rendered on the page that owns the resource it writes — assets on Assets,
 * applied controls on Applied Controls, and so on — so the transport cannot be tied to one
 * page's form actions. This route keeps the session check, the payload check, and the action
 * allowlist in one place for all of them.
 *
 * It deliberately adds no business logic: authorization, scope validation, dry-run/approval
 * gating, and every guardrail stay in the Django `ai_onboarding` services.
 */

function jsonResponse(body: unknown, status: number) {
	return new Response(body === null ? '' : JSON.stringify(body), {
		status,
		headers: { 'Content-Type': 'application/json' }
	});
}

async function readResponseBody(response: Response) {
	const text = await response.text();
	if (!text) return null;
	try {
		return JSON.parse(text);
	} catch {
		return { detail: text };
	}
}

export const POST: RequestHandler = async (event) => {
	const endpoint = aiOnboardingEndpoint(event.params.action);
	if (!endpoint) {
		return jsonResponse({ detail: 'Unknown AI onboarding action.' }, 404);
	}

	// `fe-api` routes are outside the `(app)` layout, so its session guard never runs here. An
	// unauthenticated caller must be refused rather than proxied to Django anonymously.
	if (!hasAiOnboardingSession(event)) {
		return jsonResponse(AI_ONBOARDING_SESSION_EXPIRED, 401);
	}

	let payload: unknown = null;
	try {
		payload = await event.request.json();
	} catch {
		payload = null;
	}

	if (!payload || typeof payload !== 'object') {
		return jsonResponse({ detail: 'Invalid AI request payload.' }, 400);
	}

	const response = await fetchAiOnboardingBackend(event, endpoint, payload);
	return jsonResponse(await readResponseBody(response), response.status);
};
