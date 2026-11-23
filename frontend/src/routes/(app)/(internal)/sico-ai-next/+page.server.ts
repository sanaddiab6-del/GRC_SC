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

// Allowlisted shape of a previous quality-draft rejection (codes only, no generated text).
function parsePreviousRejection(raw: unknown): Record<string, unknown> | null {
    try {
        const text = String(raw ?? '');
        if (!text || text === 'null' || text.length > 600) return null;
        const value = JSON.parse(text);
        if (!value || typeof value.failure_reason !== 'string' ||
            !/^[a-z][a-z0-9_]{1,63}$/.test(value.failure_reason)) return null;
        const out: Record<string, unknown> = { failure_reason: value.failure_reason };
        if (Array.isArray(value.path)) {
            out.path = value.path.slice(0, 8).map((p: unknown) => String(p).slice(0, 40));
        }
        if (typeof value.rule === 'string' && /^[A-Za-z]{1,30}$/.test(value.rule)) out.rule = value.rule;
        return out;
    } catch {
        return null;
    }
}

export const actions = {
    // Uses the logged-in SICO user and existing RBAC-filtered RequirementNode catalog.
    framework_source_page: async (event) => {
        if (!hasAiOnboardingSession(event)) return fail(401, { source_error: 'Sign in again.' });
        const form = await event.request.formData();
        const framework_name = String(form.get('framework_name') ?? '').trim();
        const cursor = String(form.get('cursor') ?? '');
        if (framework_name.length < 2 || framework_name.length > 150 || cursor.length > 2048) {
            return fail(400, { source_error: 'Provide the exact authorized framework.' });
        }
        try {
            const response = await fetchAiOnboardingBackend(
                event, '/ai/workforce/assistant/framework-source/page/',
                { framework_name, page_size: 25, cursor }
            );
            const data = await response.json().catch(() => ({}));
            if (!response.ok) return fail(response.status, { source_error: backendMessage(data) });
            if (data.business_records_written !== false || !Array.isArray(data.requirements) ||
                typeof data.coverage?.accessible_total !== 'number' ||
                typeof data.coverage?.complete !== 'boolean') {
                return fail(502, { source_error: 'The authorized framework catalog response was invalid.' });
            }
            return { framework_source_page: data };
        } catch {
            return fail(502, { source_error: 'Could not reach the authorized framework catalog.' });
        }
    },
    // Creation-first: generate NEW unsaved, structured GRC drafts through SICO Qwen.
    case_draft_phase: async (event) => {
        if (!hasAiOnboardingSession(event)) return fail(401, { case_draft_error: 'Sign in again.' });
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
            return fail(400, { case_draft_error: 'Provide a company, framework, objective and valid phase.' });
        }
        try {
            const response = await fetchAiOnboardingBackend(
                event, '/ai/workforce/assistant/case-draft/phase/', payload
            );
            const data = await response.json().catch(() => ({}));
            if (!response.ok) return fail(response.status, { case_draft_error: backendMessage(data) });
            if (data.business_records_written !== false || data.generated_by_model !== true ||
                data.phase !== payload.phase || !Array.isArray(data.activities) || data.activities.length !== 4 ||
                data.activities.some((stage: any) => !Array.isArray(stage?.drafts) || !stage.drafts.length ||
                    stage.write_service_execution !== 'not_called' ||
                    stage.drafts.some((draft: any) => draft.status !== 'new_unsaved_ai_draft_pending_verification'))) {
                return fail(502, { case_draft_error: 'The draft generator response failed SICO validation.' });
            }
            return { case_draft_phase: data };
        } catch {
            return fail(502, { case_draft_error: 'Could not reach the SICO case-draft service.' });
        }
    },
    // Same one-record-at-a-time Qwen generation as the successful HTML runner.
    quality_draft_one: async (event) => {
        if (!hasAiOnboardingSession(event)) return fail(401, { case_draft_error: 'Sign in again.' });
        const form = await event.request.formData();
        let previous_drafts: unknown;
        try {
            const raw = String(form.get('previous_drafts') ?? '[]');
            if (raw.length > 30000) throw new Error('Too much context');
            previous_drafts = JSON.parse(raw);
            if (!Array.isArray(previous_drafts) || previous_drafts.length > 45) throw new Error('Invalid context');
        } catch {
            return fail(400, { case_draft_error: 'Invalid prior-draft checkpoint context.' });
        }
        const payload = {
            organization_name: String(form.get('organization_name') ?? '').trim(),
            framework_name: String(form.get('framework_name') ?? '').trim(),
            problem: String(form.get('problem') ?? '').trim(),
            activity_number: Number(form.get('activity_number')),
            draft_index: Number(form.get('draft_index')),
            source_digest: String(form.get('source_digest') ?? ''),
            requirement_reference: String(form.get('requirement_reference') ?? '').trim(),
            previous_drafts,
            focus_attempt: Number(form.get('focus_attempt') ?? 0),
            previous_rejection: parsePreviousRejection(form.get('previous_rejection'))
        };
        if (payload.organization_name.length < 2 || payload.organization_name.length > 150 ||
            payload.framework_name.length < 2 || payload.framework_name.length > 150 ||
            payload.problem.length < 20 || payload.problem.length > 4000 ||
            !Number.isInteger(payload.activity_number) || payload.activity_number < 1 || payload.activity_number > 16 ||
            !Number.isInteger(payload.draft_index) || payload.draft_index < 1 || payload.draft_index > 12 ||
            !/^[0-9a-f]{64}$/.test(payload.source_digest) ||
            payload.requirement_reference.length > 100 ||
            !Number.isInteger(payload.focus_attempt) || payload.focus_attempt < 0 || payload.focus_attempt > 30) {
            return fail(400, { case_draft_error: 'Invalid case scope, framework digest or draft index.' });
        }
        try {
            const response = await fetchAiOnboardingBackend(event, '/ai/workforce/assistant/case-draft/quality-one/', payload);
            const data = await response.json().catch(() => ({}));
            if (!response.ok) return fail(response.status, { case_draft_error:
                `${backendMessage(data)} ${typeof data.failure_reason === 'string' ? '(' + data.failure_reason.slice(0, 80) + ')' : ''}`,
                // Returned to the page only so the next Resume can tell the model why it was rejected.
                rejection: parsePreviousRejection(JSON.stringify({
                    failure_reason: data.failure_reason,
                    path: data.validation_failure?.path,
                    rule: data.validation_failure?.rule
                })) });
            if (data.business_records_written !== false || data.quality_contract_checked !== true ||
                data.activity_number !== payload.activity_number ||
                data.source_digest !== payload.source_digest ||
                data.draft?.draft_reference !== `draft-${String(payload.activity_number).padStart(2, '0')}-${String(payload.draft_index).padStart(2, '0')}`) {
                return fail(502, { case_draft_error: 'SICO could not verify the new quality-gated draft.' });
            }
            return { quality_draft_one: data };
        } catch {
            return fail(502, { case_draft_error: 'One draft request failed. Previous drafts remain in your checkpoint.' });
        }
    },
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
    requirement_review: async (event) => {
        if (!hasAiOnboardingSession(event)) return fail(401, { control_error: 'Sign in again.' });
        const form = await event.request.formData();
        const action = String(form.get('action') ?? '').trim();
        const engagement_id = String(form.get('engagement_id') ?? '').trim();
        if (!['status', 'generate_and_save'].includes(action) ||
            (engagement_id && !/^[0-9a-fA-F-]{36}$/.test(engagement_id))) {
            return fail(400, { control_error: 'Invalid saved case reference or action.' });
        }
        try {
            const response = await fetchAiOnboardingBackend(
                event, '/ai/workforce/assistant/lifecycle/requirements/review/', {
                    action, ...(engagement_id ? { engagement_id } : {}),
                    confirm_preliminary_write: action === 'generate_and_save' && form.get('confirm_preliminary_write') === 'true'
                }
            );
            const result = await response.json().catch(() => ({}));
            if (!response.ok) return fail(response.status, { control_error: backendMessage(result) });
            if (action === 'status') {
                if (!result?.progress?.case_id || !Array.isArray(result.progress.saved_reviews))
                    return fail(502, { control_error: 'Saved audit progress could not be verified.' });
            } else if (result?.business_records_written !== true || result?.verified !== true ||
                       result?.record?.result !== 'not_assessed') {
                return fail(502, { control_error: 'The GRC control save could not be verified.' });
            }
            return { control_review: result };
        } catch {
            return fail(502, { control_error: 'Could not reach the control-review service.' });
        }
    },
    // Activity 1 v3: full authorized framework coverage, one read-only Qwen batch.
    // Reuses the existing permission-checked generate-one endpoint. No GRC writes.
    ai_framework_batch: async (event) => {
        if (!hasAiOnboardingSession(event)) {
            return fail(401, { framework_batch_error: 'Sign in again.' });
        }
        const body = await event.request.formData();
        const payload = {
            organization_name: String(body.get('organization_name') ?? '').trim(),
            framework_name: String(body.get('framework_name') ?? '').trim(),
            problem: String(body.get('problem') ?? '').trim(),
            activity_number: 1,
            full_framework_batch: true,
            framework_batch_size: Number(body.get('framework_batch_size') ?? 2),
            framework_cursor: String(body.get('framework_cursor') ?? ''),
            framework_business_context: String(body.get('framework_business_context') ?? '').trim()
        };
        if (payload.organization_name.length < 2 || payload.organization_name.length > 150 ||
            payload.framework_name.length < 2 || payload.framework_name.length > 150 ||
            payload.problem.length < 20 || payload.problem.length > 4000 ||
            !Number.isInteger(payload.framework_batch_size) ||
            payload.framework_batch_size < 1 || payload.framework_batch_size > 3 ||
            payload.framework_cursor.length > 2048 ||
            payload.framework_business_context.length > 1200) {
            return fail(400, { framework_batch_error: 'Provide a valid organization, exact selected framework, objective, and batch size.' });
        }
        try {
            const response = await fetchAiOnboardingBackend(
                event, '/ai/workforce/assistant/lifecycle/generate-one/', payload
            );
            const data = await response.json().catch(() => ({}));
            if (!response.ok) {
                const kind = typeof data?.error_kind === 'string' ? data.error_kind.slice(0, 80) : '';
                return fail(response.status, {
                    framework_batch_error: (kind ? `${kind}: ` : '') + backendMessage(data)
                });
            }
            if (data.activity_number !== 1 || data.business_records_written !== false ||
                data.compliance_verdict !== 'not_established' ||
                !data.framework_batch || data.framework_batch.business_records_written !== false) {
                return fail(502, { framework_batch_error: 'Read-only Activity 1 response could not be verified.' });
            }
            const batch = data.framework_batch;
            if (batch.status === 'partial' || batch.status === 'complete') {
                if (data.generated_by_model !== true ||
                    !Array.isArray(batch.requirement_reviews) || !batch.requirement_reviews.length ||
                    typeof batch.coverage?.accessible_total !== 'number') {
                    return fail(502, { framework_batch_error: 'The full-framework batch was not validated.' });
                }
            } else if (typeof batch.status !== 'string' || !Array.isArray(batch.requirement_reviews) ||
                batch.requirement_reviews.length !== 0) {
                return fail(502, { framework_batch_error: 'Framework matching response was invalid.' });
            }
            return { ai_framework_batch: data };
        } catch {
            return fail(502, { framework_batch_error: 'The full-framework batch could not reach the backend. Previous progress remains available.' });
        }
    },
    ai_sixteen_item: async (event) => {
        if (!hasAiOnboardingSession(event)) return fail(401, { ai_sixteen_error: 'Sign in again.' });
        const form = await event.request.formData();
        const payload = {
            organization_name: String(form.get('organization_name') ?? '').trim(),
            framework_name: String(form.get('framework_name') ?? '').trim(),
            problem: String(form.get('problem') ?? '').trim(),
            activity_number: Number(form.get('activity_number') ?? 0),
            case_context: String(form.get('case_context') ?? '')
        };
        if (payload.organization_name.length < 2 || payload.organization_name.length > 150 ||
            payload.framework_name.length < 2 || payload.framework_name.length > 150 ||
            payload.problem.length < 20 || payload.problem.length > 4000 ||
            payload.case_context.length > 5500 ||
            !Number.isInteger(payload.activity_number) || payload.activity_number < 1 || payload.activity_number > 16) {
            return fail(400, { ai_sixteen_error: 'Enter a valid organization, framework, problem and activity number.' });
        }
        try {
            const response = await fetchAiOnboardingBackend(
                event, '/ai/workforce/assistant/lifecycle/generate-one/', payload
            );
            const data = await response.json().catch(() => ({}));
            if (!response.ok) return fail(response.status, { ai_sixteen_error: backendMessage(data) });
            if (data.generated_by_model !== true || data.activity_number !== payload.activity_number ||
                data.activity?.number !== payload.activity_number ||
                typeof data.activity.analysis !== 'string') {
                return fail(502, { ai_sixteen_error: 'The requested activity failed draft validation.' });
            }
            return { ai_sixteen_item: data };
        } catch {
            return fail(502, { ai_sixteen_error: 'Draft generation could not finish. Previously generated activities remain visible.' });
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
            return fail(502, { ai_sixteen_error: 'The generation request failed. Previously generated activities remain visible.' });
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
