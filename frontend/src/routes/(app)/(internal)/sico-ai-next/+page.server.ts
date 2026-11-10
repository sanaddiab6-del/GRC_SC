/** SICO AI Next: authenticated, organization-optional, read-only GRC coordinator. */
import { fail } from '@sveltejs/kit';
import type { Actions } from './$types';
import {
    AI_ONBOARDING_SESSION_EXPIRED,
    fetchAiOnboardingBackend,
    hasAiOnboardingSession
} from '$lib/utils/aiOnboardingProxy';

function backendMessage(value: unknown): string {
    if (value !== null && typeof value === 'object' && !Array.isArray(value)) {
        const data = value as Record<string, unknown>;
        for (const key of ['detail', 'error', 'message']) {
            if (typeof data[key] === 'string' && (data[key] as string).trim()) {
                return (data[key] as string).slice(0, 500);
            }
        }
    }
    return 'The SICO AI backend could not prepare a workflow plan.';
}

export const actions = {
    run: async (event) => {
        if (!hasAiOnboardingSession(event)) {
            return fail(401, { error: backendMessage(AI_ONBOARDING_SESSION_EXPIRED) });
        }
        const body = await event.request.formData();
        const instruction = String(body.get('scenario_text') ?? '').trim();
        const organization_hint = String(body.get('organization_hint') ?? '').trim();
        if (instruction.length < 20 || instruction.length > 12000) {
            return fail(400, { error: 'Describe the GRC task in 20 to 12,000 characters.' });
        }
        if (organization_hint.length > 150) {
            return fail(400, { error: 'Organization name is too long.' });
        }
        try {
            const response = await fetchAiOnboardingBackend(event, '/ai/workforce/assistant/plan/', {
                instruction,
                organization_hint
            });
            const result = await response.json().catch(() => ({}));
            if (!response.ok) return fail(response.status, { error: backendMessage(result) });
            if (!result || !Array.isArray(result.steps) || result.provider_mode !== 'configured_local_provider') {
                return fail(502, { error: 'SICO AI did not produce a verified model-generated workflow plan.' });
            }
            return {
                sico_plan: result,
                sico_run: {
                    planning: 'completed',
                    advisory_only: true,
                    grc_business_records_written: false
                }
            };
        } catch {
            return fail(502, { error: 'Unable to reach the SICO AI planning backend.' });
        }
    }
} satisfies Actions;
