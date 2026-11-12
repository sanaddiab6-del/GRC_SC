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
    },
    workflow_options: async (event) => {
        if (!hasAiOnboardingSession(event)) return fail(401, { workflow_error: 'Sign in again to access GRC records.' });
        const body = await event.request.formData();
        const input = {
            organization_query: String(body.get('organization_query') ?? '').trim().slice(0, 150),
            framework_query: String(body.get('framework_query') ?? '').trim().slice(0, 100),
            folder_id: String(body.get('folder_id') ?? '').trim() || undefined
        };
        try {
            const r = await fetchAiOnboardingBackend(event, '/ai/workforce/assistant/workflow/options/', input);
            const data = await r.json().catch(() => ({}));
            if (!r.ok) return fail(r.status, { workflow_error: backendMessage(data) });
            return { workflow_options: data };
        } catch {
            return fail(502, { workflow_error: 'Unable to retrieve authorized GRC options.' });
        }
    },
    workflow_prepare: async (event) => {
        if (!hasAiOnboardingSession(event)) return fail(401, { workflow_error: 'Sign in again.' });
        const body = await event.request.formData();
        const payload = {
            instruction: String(body.get('instruction') ?? '').trim(),
            assessment_name: String(body.get('assessment_name') ?? '').trim(),
            folder_id: String(body.get('folder_id') ?? '').trim(),
            framework_id: String(body.get('framework_id') ?? '').trim(),
            perimeter_id: String(body.get('perimeter_id') ?? '').trim() || undefined,
            new_perimeter_name: String(body.get('new_perimeter_name') ?? '').trim() || undefined,
            risk_matrix_id: String(body.get('risk_matrix_id') ?? '').trim() || undefined
        };
        if (payload.instruction.length < 20 || payload.instruction.length > 4000 ||
            payload.assessment_name.length < 4 || payload.assessment_name.length > 200 ||
            !/^[0-9a-fA-F-]{36}$/.test(payload.folder_id) ||
            !/^[0-9a-fA-F-]{36}$/.test(payload.framework_id)) {
            return fail(400, { workflow_error: 'Confirm a real organization, framework, and assessment name.' });
        }
        try {
            const r = await fetchAiOnboardingBackend(event, '/ai/workforce/assistant/lifecycle/start/', payload);
            const data = await r.json().catch(() => ({}));
            if (!r.ok) return fail(r.status, { workflow_error: backendMessage(data) });
            if (!data.engagement_id || !data.review?.operation_payload || !data.prepared_digest)
                return fail(502, { workflow_error: 'The backend did not provide a reviewable operation.' });
            return { workflow_prepared: data };
        } catch {
            return fail(502, { workflow_error: 'Could not prepare the real GRC operation.' });
        }
    },
    workflow_review: async (event) => {
        if (!hasAiOnboardingSession(event)) return fail(401, { workflow_error: 'Sign in again.' });
        const body = await event.request.formData();
        const engagement_id = String(body.get('engagement_id') ?? '').trim();
        if (!/^[0-9a-fA-F-]{36}$/.test(engagement_id)) return fail(400, { workflow_error: 'Invalid engagement ID.' });
        try {
            const r = await fetchAiOnboardingBackend(event, '/ai/workforce/assistant/workflow/review/', { engagement_id });
            const data = await r.json().catch(() => ({}));
            if (!r.ok) return fail(r.status, { workflow_error: backendMessage(data) });
            return { workflow_review: data };
        } catch {
            return fail(502, { workflow_error: 'Could not retrieve the verified review.' });
        }
    },
    workflow_approve: async (event) => {
        if (!hasAiOnboardingSession(event)) return fail(401, { workflow_error: 'Sign in again.' });
        const body = await event.request.formData();
        const engagement_id = String(body.get('engagement_id') ?? '').trim();
        const prepared_digest = String(body.get('prepared_digest') ?? '').trim();
        if (!/^[0-9a-fA-F-]{36}$/.test(engagement_id) || !/^[0-9a-f]{64}$/.test(prepared_digest) ||
            body.get('confirm_reviewed') !== 'yes')
            return fail(400, { workflow_error: 'Read the exact proposal and explicitly confirm it.' });
        try {
            const r = await fetchAiOnboardingBackend(event, '/ai/workforce/assistant/workflow/approve/',
                { engagement_id, prepared_digest, confirm_reviewed: true });
            const data = await r.json().catch(() => ({}));
            if (!r.ok) return fail(r.status, { workflow_error: backendMessage(data) });
            return { workflow_approved: data };
        } catch {
            return fail(502, { workflow_error: 'Could not record human approval.' });
        }
    },
    workflow_commit: async (event) => {
        if (!hasAiOnboardingSession(event)) return fail(401, { workflow_error: 'Sign in again.' });
        const body = await event.request.formData();
        const engagement_id = String(body.get('engagement_id') ?? '').trim();
        const prepared_digest = String(body.get('prepared_digest') ?? '').trim();
        if (!/^[0-9a-fA-F-]{36}$/.test(engagement_id) || !/^[0-9a-f]{64}$/.test(prepared_digest) ||
            body.get('confirm_reviewed') !== 'yes')
            return fail(400, { workflow_error: 'A separate explicit confirmation is required to save records.' });
        try {
            const r = await fetchAiOnboardingBackend(event, '/ai/workforce/assistant/workflow/commit/',
                { engagement_id, prepared_digest, confirm_reviewed: true });
            const data = await r.json().catch(() => ({}));
            if (!r.ok) return fail(r.status, { workflow_error: backendMessage(data) });
            if (!data.business_records_written || !Array.isArray(data.created_objects))
                return fail(502, { workflow_error: 'The GRC writer did not verify saved records.' });
            return { workflow_committed: data };
        } catch {
            return fail(502, { workflow_error: 'Unable to verify the saved GRC records.' });
        }
    },
    workflow_resume: async (event) => {
        if (!hasAiOnboardingSession(event)) return fail(401, { workflow_error: 'Sign in again.' });
        const body = await event.request.formData();
        const engagement_id = String(body.get('engagement_id') ?? '').trim();
        if (!/^[0-9a-fA-F-]{36}$/.test(engagement_id)) return fail(400, { workflow_error: 'Invalid engagement ID.' });
        try {
            const r = await fetchAiOnboardingBackend(event, '/ai/workforce/assistant/workflow/resume/', { engagement_id });
            const data = await r.json().catch(() => ({}));
            if (!r.ok) return fail(r.status, { workflow_error: backendMessage(data) });
            return { workflow_resumed: data };
        } catch {
            return fail(502, { workflow_error: 'Could not read the saved workflow status.' });
        }
    },
    lifecycle_status: async (event) => {
        if (!hasAiOnboardingSession(event)) return fail(401, { lifecycle_error: 'Sign in again.' });
        const body = await event.request.formData();
        const engagement_id = String(body.get('engagement_id') ?? '').trim();
        if (!/^[0-9a-fA-F-]{36}$/.test(engagement_id)) return fail(400, { lifecycle_error: 'Enter the saved engagement ID.' });
        try {
            const r = await fetchAiOnboardingBackend(event, '/ai/workforce/assistant/lifecycle/status/', { engagement_id });
            const data = await r.json().catch(() => ({}));
            if (!r.ok) return fail(r.status, { lifecycle_error: backendMessage(data) });
            return { lifecycle_status: data };
        } catch { return fail(502, { lifecycle_error: 'Could not load saved GRC lifecycle.' }); }
    },
    lifecycle_next: async (event) => {
        if (!hasAiOnboardingSession(event)) return fail(401, { lifecycle_error: 'Sign in again.' });
        const body = await event.request.formData();
        const engagement_id = String(body.get('engagement_id') ?? '').trim();
        if (!/^[0-9a-fA-F-]{36}$/.test(engagement_id)) return fail(400, { lifecycle_error: 'Select a saved engagement.' });
        try {
            const r = await fetchAiOnboardingBackend(event, '/ai/workforce/assistant/lifecycle/next/', {
                engagement_id, human_facts: String(body.get('human_facts') ?? '').trim().slice(0, 1200)
            });
            const data = await r.json().catch(() => ({}));
            if (!r.ok) return fail(r.status, { lifecycle_error: backendMessage(data) });
            return { lifecycle_next: data };
        } catch { return fail(502, { lifecycle_error: 'AI could not safely prepare the next stage.' }); }
    },
    lifecycle_stage_approve: async (event) => {
        if (!hasAiOnboardingSession(event)) return fail(401, { lifecycle_error: 'Sign in again.' });
        const body = await event.request.formData();
        const payload = {
            engagement_id: String(body.get('engagement_id') ?? ''),
            stage: String(body.get('stage') ?? ''),
            prepared_digest: String(body.get('prepared_digest') ?? ''),
            confirm_reviewed: body.get('confirm_reviewed') === 'yes'
        };
        if (!payload.confirm_reviewed || !/^[a-f0-9]{64}$/.test(payload.prepared_digest))
            return fail(400, { lifecycle_error: 'Review the exact proposal before approval.' });
        try {
            const r = await fetchAiOnboardingBackend(event, '/ai/workforce/assistant/lifecycle/approve/', payload);
            const data = await r.json().catch(() => ({}));
            if (!r.ok) return fail(r.status, { lifecycle_error: backendMessage(data) });
            return { lifecycle_stage_approved: data };
        } catch { return fail(502, { lifecycle_error: 'Could not record the stage approval.' }); }
    },
    lifecycle_stage_commit: async (event) => {
        if (!hasAiOnboardingSession(event)) return fail(401, { lifecycle_error: 'Sign in again.' });
        const body = await event.request.formData();
        const payload = {
            engagement_id: String(body.get('engagement_id') ?? ''),
            stage: String(body.get('stage') ?? ''),
            prepared_digest: String(body.get('prepared_digest') ?? ''),
            confirm_reviewed: body.get('confirm_reviewed') === 'yes'
        };
        if (!payload.confirm_reviewed || !/^[a-f0-9]{64}$/.test(payload.prepared_digest))
            return fail(400, { lifecycle_error: 'A separate final confirmation is required.' });
        try {
            const r = await fetchAiOnboardingBackend(event, '/ai/workforce/assistant/lifecycle/commit/', payload);
            const data = await r.json().catch(() => ({}));
            if (!r.ok) return fail(r.status, { lifecycle_error: backendMessage(data) });
            if (data.business_records_written !== true) return fail(502, { lifecycle_error: 'The original GRC writer did not confirm its operation.' });
            return { lifecycle_stage_committed: data };
        } catch { return fail(502, { lifecycle_error: 'Could not verify the GRC stage save.' }); }
    },
} satisfies Actions;
