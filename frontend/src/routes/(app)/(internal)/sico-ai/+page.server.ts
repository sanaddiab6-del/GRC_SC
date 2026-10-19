/**
 * SICO AI Workspace — first visible, read-only, authenticated case-intake step.
 * Uses the same trusted proxy Amro's Quick Start already uses.
 * This route never creates or changes any GRC records.
 */
import {
	AI_ONBOARDING_SESSION_EXPIRED,
	fetchAiOnboardingBackend,
	hasAiOnboardingSession
} from '$lib/utils/aiOnboardingProxy';
import { fail, type Actions } from '@sveltejs/kit';

const MAX_SCENARIO_CHARS = 12000;
function field(data: FormData, key: string, maximum = 500): string {
	const value = data.get(key);
	return (typeof value === 'string' ? value : '').trim().slice(0, maximum);
}

function errorDetail(value: unknown): string {
	if (value && typeof value === 'object') {
		const object = value as Record<string, unknown>;
		if (typeof object.detail === 'string') return object.detail;
		if (typeof object.message === 'string') return object.message;
		if (typeof object.error === 'string') return object.error;
	}
	return 'Case intake failed. Check the AI provider settings and try again.';
}

export const actions: Actions = {
	intake: async (event) => {
		if (!hasAiOnboardingSession(event)) {
			return fail(401, { error: errorDetail(AI_ONBOARDING_SESSION_EXPIRED) });
		}
		const formData = await event.request.formData();
		const scenario = field(formData, 'scenario_text', MAX_SCENARIO_CHARS);
		const preferredFramework = field(formData, 'preferred_framework');
		const organization = field(formData, 'organization_hint');
		const scope = field(formData, 'scope_hint', 2000);
		const period = field(formData, 'assessment_period');
		const trigger = field(formData, 'known_trigger', 1000);
		const deadline = field(formData, 'known_deadline', 10);
		if (scenario.length < 20) {
			return fail(400, { error: 'Describe the assignment in at least 20 characters.' });
		}
		const payload = {
			scenario_text: scenario,
			preferred_framework: preferredFramework || null,
			organization_hint: organization || null,
			scope_hint: scope || null,
			assessment_period: period ? { label: period } : null,
			known_trigger: trigger || null,
			known_deadline: deadline || null,
			strict_mode: true
		};
		try {
			const response = await fetchAiOnboardingBackend(
				event,
				'/ai/onboarding/case-intake/',
				payload
			);
			const result = await response.json().catch(() => ({ detail: 'Invalid backend response.' }));
			if (!response.ok) return fail(response.status, { error: errorDetail(result) });
			// Advisory output only; the approved creation flow remains the existing Quick Start UI.
			return { draft: result, message: 'Draft generated. Review framework, domain and scope before setup.' };
		} catch (error) {
			return fail(502, { error: errorDetail(error) });
		}
	}
};
