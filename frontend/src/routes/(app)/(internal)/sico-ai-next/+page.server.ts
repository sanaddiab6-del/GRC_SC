/** SICO AI Next: authenticated AI generation with approval-gated GRC case execution. */
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
    ai_sixteen_phase: async (event) => {
        if (!hasAiOnboardingSession(event)) return fail(401, { ai_sixteen_error: 'Sign in again.' });
        const form = await event.request.formData();
        const payload = {
            organization_name: String(form.get('organization_name') ?? '').trim(),
            framework_name: String(form.get('framework_name') ?? '').trim(),
            problem: String(form.get('problem') ?? '').trim(),
            phase: Number(form.get('phase') ?? -1)
        };
        if (payload.organization_name.length < 2 || payload.organization_name.length > 150 ||
            payload.framework_name.length < 2 || payload.framework_name.length > 150 ||
            payload.problem.length < 20 || payload.problem.length > 4000 ||
            !Number.isInteger(payload.phase) || payload.phase < 0 || payload.phase > 3) {
            return fail(400, { ai_sixteen_error: 'Enter the company, framework, problem and a valid generation phase.' });
        }
        try {
            const response = await fetchAiOnboardingBackend(
                event, '/ai/workforce/assistant/lifecycle/generate-four/', payload
            );
            const data = await response.json().catch(() => ({}));
            if (!response.ok) return fail(response.status, { ai_sixteen_error: backendMessage(data) });
            if (data.generated_by_model !== true || data.phase !== payload.phase ||
                !Array.isArray(data.activities) || data.activities.length !== 4) {
                return fail(502, { ai_sixteen_error: 'AI output did not contain four validated activities.' });
            }
            return { ai_sixteen_phase: data };
        } catch {
            return fail(502, { ai_sixteen_error: 'The Qwen generation request failed. Previously generated activities remain visible.' });
        }
    },
    lifecycle_intake: async (event) => {
        if (!hasAiOnboardingSession(event)) return fail(401, { lifecycle_error: 'Sign in again.' });
        const body = await event.request.formData();
        const skipLegacyGeneration = body.get('skip_legacy_generation') === 'yes';
        const payload = {
            organization_name: String(body.get('organization_name') ?? '').trim(),
            framework_name: String(body.get('framework_name') ?? '').trim(),
            problem: String(body.get('problem') ?? '').trim(),
            selected_framework_id: String(body.get('selected_framework_id') ?? '').trim() || undefined,
            selected_organization_id: String(body.get('selected_organization_id') ?? '').trim() || undefined
        };
        if (payload.organization_name.length < 2 || payload.organization_name.length > 150 ||
            payload.framework_name.length < 2 || payload.framework_name.length > 150 ||
            payload.problem.length < 20 || payload.problem.length > 4000)
            return fail(400, { lifecycle_error: 'Enter an existing organization, loaded framework, and a problem of at least 20 characters.' });
        try {
            const r = await fetchAiOnboardingBackend(event, '/ai/workforce/assistant/lifecycle/intake/', payload);
            const data = await r.json().catch(() => ({}));
            if (!r.ok) {
                if (data?.status === 'needs_exact_selection' && Array.isArray(data?.frameworks))
                    return { lifecycle_choices: data };
                return fail(r.status, { lifecycle_error: backendMessage(data) });
            }
            if (!data.engagement_id || !data.review?.operation_payload || !data.prepared_digest)
                return fail(502, { lifecycle_error: 'Could not verify the reviewable GRC case.' });
            // The new sixteen-stage generator already ran: do not invoke the old
            // oversized single-model report again when preparing case records.
            let generated: Record<string, any> | null = null;
            let generationError = '';
            if (!skipLegacyGeneration) {
            try {
                const g = await fetchAiOnboardingBackend(
                    event, '/ai/workforce/assistant/lifecycle/generate/',
                    { engagement_id: String(data.engagement_id) }
                );
                const response = await g.json().catch(() => ({}));
                if (g.ok && response?.generated_by_model === true && response?.report)
                    generated = response;
                else generationError = backendMessage(response);
            } catch {
                generationError = 'Local AI generation was unavailable; no fabricated response was substituted.';
            }
            }
            return { workflow_prepared: data, generated_assessment: generated, generation_error: generationError };
        } catch {
            return fail(502, { lifecycle_error: 'Could not prepare the case using the loaded GRC records.' });
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
            // The user explicitly approved creation of these exact records. The
            // existing case-only writer is now the NEXT operation, not a second
            // manually navigated wizard. It verifies the stored approval, RBAC,
            // scope, digest, transaction and idempotency independently.
            if (data?.approved === true && data?.commit_enabled === true) {
                try {
                    const saved = await fetchAiOnboardingBackend(
                        event, '/ai/workforce/assistant/workflow/commit/',
                        { engagement_id, prepared_digest, confirm_reviewed: true }
                    );
                    const result = await saved.json().catch(() => ({}));
                    if (!saved.ok || result?.business_records_written !== true ||
                        !Array.isArray(result?.created_objects)) {
                        return {
                            workflow_approved: data,
                            workflow_error: 'Approval was recorded, but case creation was blocked: ' +
                                backendMessage(result) + '. No second approval is required.'
                        };
                    }
                    return { workflow_approved: data, workflow_committed: result };
                } catch {
                    return { workflow_approved: data, workflow_error: 'Approval was recorded. Case save could not be verified; do not start another case.' };
                }
            }
            return {
                workflow_approved: data,
                workflow_error: 'Approval recorded, but the restricted case writer is disabled. No GRC case was saved.'
            };
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
