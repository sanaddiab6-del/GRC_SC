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
            const payload = { instruction, organization_hint };
            // Independent requests: a planning failure must not discard an execution trace.
            const [planning, execution] = await Promise.allSettled([
                fetchAiOnboardingBackend(event, '/ai/workforce/assistant/plan/', payload)
                    .then(async (response) => ({ ok: response.ok, data: await response.json() })),
                fetchAiOnboardingBackend(event, '/ai/workforce/assistant/execute/', payload)
                    .then(async (response) => ({ ok: response.ok, data: await response.json() }))
            ]);
            const planResult = planning.status === 'fulfilled' ? planning.value : null;
            const agentResult = execution.status === 'fulfilled' ? execution.value : null;
            const validPlan = planResult?.ok && Array.isArray(planResult.data?.steps)
                && planResult.data.provider_mode === 'configured_local_provider';
            const validAgent = agentResult?.ok && Array.isArray(agentResult.data?.trace)
                && agentResult.data.mode === 'model_driven_read_only_agent';
            return {
                sico_plan: validPlan ? planResult?.data : null,
                sico_agent: validAgent ? agentResult?.data : null,
                plan_error: validPlan ? null : backendMessage(planResult?.data),
                agent_error: validAgent ? null : agentResult
                    ? backendMessage(agentResult.data) : 'Unable to reach the agent execution backend.',
                sico_run: {
                    planning: validPlan ? 'completed' : 'failed',
                    execution: validAgent ? agentResult?.data.status : 'unavailable',
                    advisory_only: !validAgent,
                    grc_business_records_written: false
                }
            };
        } catch {
            return fail(502, { error: 'Unable to reach the SICO AI planning backend.' });
        }
    }
} satisfies Actions;
