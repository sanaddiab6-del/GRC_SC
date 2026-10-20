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
casePlan: async (event) => {
    if (!hasAiOnboardingSession(event)) {
        return fail(401, { error: errorDetail(AI_ONBOARDING_SESSION_EXPIRED) });
    }
    const data = await event.request.formData();
    const organization = field(data, 'organization_hint', 150);
    const frameworkHint = field(data, 'preferred_framework', 150);
    const scope = field(data, 'scope_hint', 500);
    const frameworkId = field(data, 'framework_id', 36);
    const strategy = field(data, 'domain_strategy', 10);
    const existingFolder = field(data, 'selected_folder_id', 36);
    const parentFolder = field(data, 'parent_folder_id', 36);
    if (!organization || !scope || !frameworkId || !['create', 'reuse'].includes(strategy)) {
        return fail(400, { error: 'Choose the organization, exact framework, scope, and domain decision.' });
    }
    try {
        // Refresh the read-only snapshot; never trust a browser-submitted discovery result.
        const discoveryResponse = await fetchAiOnboardingBackend(event, '/ai/workforce/discover/', {
            organization, framework_hint: frameworkHint,
            ...(strategy === 'reuse' && existingFolder ? { selected_folder_id: existingFolder } : {})
        });
        const discovered = await discoveryResponse.json().catch(() => ({}));
        if (!discoveryResponse.ok) return fail(discoveryResponse.status, { error: errorDetail(discovered) });
        const response = await fetchAiOnboardingBackend(event, '/ai/workforce/new-case-plan/', {
            organization, scope, framework_id: frameworkId, domain_strategy: strategy,
            ...(strategy === 'reuse' ? {selected_folder_id: existingFolder} : {parent_folder_id: parentFolder}),
            framework_review_confirmed: data.get('framework_review_confirmed') === 'on'
        });
        const planned = await response.json().catch(() => ({}));
        if (!response.ok) return fail(response.status, { error: errorDetail(planned) });
        return { case_plan: planned, discovery: { ...discovered, case_context: { scope } }, message: 'New-case plan checked against real records. No changes made.' };
    } catch (error) {
        return fail(502, { error: errorDetail(error) });
    }
},
	discover: async (event) => {
		if (!hasAiOnboardingSession(event)) {
			return fail(401, { error: errorDetail(AI_ONBOARDING_SESSION_EXPIRED) });
		}
		const data = await event.request.formData();
		const organization = field(data, 'organization_hint');
		const frameworkHint = field(data, 'preferred_framework');
		const selectedFolderId = field(data, 'selected_folder_id', 36);
		if (organization.length < 3) {
			return fail(400, { error: 'Please enter the organization name (at least 3 characters).' });
		}
		try {
			const response = await fetchAiOnboardingBackend(event, '/ai/workforce/discover/', {
				organization,
				framework_hint: frameworkHint,
				...(selectedFolderId ? { selected_folder_id: selectedFolderId } : {})
			});
			const result = await response.json().catch(() => ({ detail: 'Invalid backend response.' }));
			if (!response.ok) return fail(response.status, { error: errorDetail(result) });
			return { discovery: { ...result, case_context: { scope: field(data, 'scope_hint', 500) || 'Access management', period: field(data, 'assessment_period', 100) } }, message: 'Real platform records checked. No changes made.' };
		} catch (error) {
			return fail(502, { error: errorDetail(error) });
		}
	},
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
