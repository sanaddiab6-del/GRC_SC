/**
 * SICO AI Workspace — authenticated case intake and reviewed risk-scenario execution.
 * The existing preflight remains read-only. Only explicit reviewer approval
 * can invoke the protected risk-scenario commit API.
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
	return 'SICO AI request failed. Check the provider settings, permissions, and selected records.';
}

// SICO Risk Scenario Step 8A/8B: use the existing authenticated backend services.
// Each POST remains scoped to the current user's credential and existing backend RBAC.
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const RISK_LEVELS = new Set(['low', 'medium', 'high', 'critical']);

function reviewedScenario(raw: unknown): Record<string, unknown> | null {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return null;
    const item = raw as Record<string, unknown>;
    const requiredText = (key: string, maximum: number) =>
        typeof item[key] === 'string' ? (item[key] as string).trim().slice(0, maximum) : '';
    const temporary_id = requiredText('temporary_id', 64);
    const title = requiredText('title', 200);
    const likelihood = requiredText('likelihood', 20);
    const impact = requiredText('impact', 20);
    const risk_level = requiredText('risk_level', 20);
    const confidence = Number(item.confidence);
    if (!temporary_id || !title || !RISK_LEVELS.has(likelihood) || !RISK_LEVELS.has(impact) ||
        !RISK_LEVELS.has(risk_level) || !Number.isFinite(confidence) || confidence < 0 || confidence > 1) {
        return null;
    }
    const optional = (key: string, maximum: number) => requiredText(key, maximum);
    const steps = Array.isArray(item.recommended_next_steps)
        ? item.recommended_next_steps.filter((step): step is string => typeof step === 'string')
            .slice(0, 10).map(step => step.trim().slice(0, 500)).filter(Boolean)
        : [];
    // Whitelist only fields recognized by the deterministic Step 8B serializer.
    return {
        temporary_id, title,
        description: optional('description', 5000),
        threat: optional('threat', 500),
        vulnerability: optional('vulnerability', 500),
        impact_description: optional('impact_description', 3000),
        likelihood, impact, risk_level,
        rationale: optional('rationale', 3000),
        recommended_next_steps: steps,
        confidence,
        review_status: 'pending_review'
    };
}

function riskCommitPayload(folder: string, assessment: string, scenario: Record<string, unknown>, dryRun: boolean) {
    return {
        dry_run: dryRun,
        approved: !dryRun,
        folder_reference: folder,
        assessment_reference: assessment,
        decisions: [{
            temporary_id: scenario.temporary_id,
            selected: true,
            decision: 'create',
            payload: scenario
        }]
    };
}

function reviewFromForm(data: FormData) {
    const folder_reference = field(data, 'folder_reference', 36);
    const assessment_reference = field(data, 'assessment_reference', 36);
    const candidate = reviewedScenario({
        temporary_id: field(data, 'temporary_id', 64),
        title: field(data, 'title', 200),
        description: field(data, 'description', 5000),
        threat: field(data, 'threat', 500),
        vulnerability: field(data, 'vulnerability', 500),
        impact_description: field(data, 'impact_description', 3000),
        likelihood: field(data, 'likelihood', 20),
        impact: field(data, 'impact', 20),
        risk_level: field(data, 'risk_level', 20),
        rationale: field(data, 'rationale', 3000),
        recommended_next_steps: field(data, 'recommended_next_steps', 5000).split(/\r?\n/),
        confidence: field(data, 'confidence', 20)
    });
    if (!UUID.test(folder_reference) || !UUID.test(assessment_reference) || !candidate) return null;
    return { folder_reference, assessment_reference, scenario: candidate };
}

function reviewFromJson(value: string) {
    if (value.length > 16000) return null;
    try {
        const candidate = JSON.parse(value) as Record<string, unknown>;
        if (!candidate || typeof candidate !== 'object') return null;
        const folder_reference = candidate.folder_reference;
        const assessment_reference = candidate.assessment_reference;
        const scenario = reviewedScenario(candidate.scenario);
        if (typeof folder_reference !== 'string' || typeof assessment_reference !== 'string' ||
            !UUID.test(folder_reference) || !UUID.test(assessment_reference) || !scenario) return null;
        return { folder_reference, assessment_reference, scenario };
    } catch {
        return null;
    }
}

function hasBlockers(result: any): boolean {
    return !result || !Array.isArray(result.blocking_errors) || result.blocking_errors.length > 0 ||
        !Array.isArray(result.planned_actions) || !result.planned_actions.some((a: any) =>
            a?.decision === 'create' && a?.status === 'planned');
}

export const actions: Actions = {
    riskSuggest: async (event) => {
        if (!hasAiOnboardingSession(event)) return fail(401, { error: errorDetail(AI_ONBOARDING_SESSION_EXPIRED) });
        const data = await event.request.formData();
        const case_summary = field(data, 'case_summary', 4000);
        const organization_hint = field(data, 'organization_hint', 150);
        const known_weaknesses = field(data, 'known_weaknesses', 2500).split(/\r?\n/)
            .map(item => item.trim()).filter(Boolean).slice(0, 10);
        if (case_summary.length < 20 || !known_weaknesses.length) {
            return fail(400, { error: 'Describe the scope and at least one known weakness. Fictional test data is recommended.' });
        }
        try {
            const response = await fetchAiOnboardingBackend(event, '/ai/onboarding/risk-scenarios/suggest/', {
                case_summary, known_weaknesses, user_locale: 'en', strict_mode: true
            });
            const result = await response.json().catch(() => ({}));
            if (!response.ok) return fail(response.status, { error: errorDetail(result) });
            let risk_discovery: unknown = null;
            if (organization_hint.length >= 3) {
                try {
                    const discoverResponse = await fetchAiOnboardingBackend(event, '/ai/workforce/discover/', {
                        organization: organization_hint, framework_hint: ''
                    });
                    if (discoverResponse.ok) risk_discovery = await discoverResponse.json();
                } catch { /* Discovery is optional and cannot change Step 8A's no-write behavior. */ }
            }
            return { risk_draft: result, risk_discovery,
                message: 'Risk scenario suggestions generated. No record has been saved.' };
        } catch (error) {
            return fail(502, { error: errorDetail(error) });
        }
    },
    riskDryRun: async (event) => {
        if (!hasAiOnboardingSession(event)) return fail(401, { error: errorDetail(AI_ONBOARDING_SESSION_EXPIRED) });
        const data = await event.request.formData();
        const review = reviewFromForm(data);
        if (!review) return fail(400, { error: 'Select a valid existing folder and risk assessment and review the scenario fields.' });
        try {
            const response = await fetchAiOnboardingBackend(event, '/ai/onboarding/risk-scenarios/commit/',
                riskCommitPayload(review.folder_reference, review.assessment_reference, review.scenario, true));
            const result = await response.json().catch(() => ({}));
            if (!response.ok) return fail(response.status, { risk_review: review, risk_dry_run: result,
                error: errorDetail(result) });
            return { risk_review: review, risk_dry_run: result,
                message: hasBlockers(result) ? 'The dry-run found blockers. No data was saved.' :
                    'Dry-run passed. Review the planned action, then explicitly approve the save.' };
        } catch (error) {
            return fail(502, { risk_review: review, error: errorDetail(error) });
        }
    },
    riskCommit: async (event) => {
        if (!hasAiOnboardingSession(event)) return fail(401, { error: errorDetail(AI_ONBOARDING_SESSION_EXPIRED) });
        const data = await event.request.formData();
        if (data.get('approved_by_reviewer') !== 'on') {
            return fail(400, { error: 'Explicit reviewer approval is required before saving.' });
        }
        const review = reviewFromJson(field(data, 'review_json', 16000));
        if (!review) return fail(400, { error: 'Reviewed scenario is missing or invalid. Run the dry-run again.' });
        try {
            // Do not trust a browser-submitted dry-run status; recheck authorization and scope.
            const checkResponse = await fetchAiOnboardingBackend(event, '/ai/onboarding/risk-scenarios/commit/',
                riskCommitPayload(review.folder_reference, review.assessment_reference, review.scenario, true));
            const checked = await checkResponse.json().catch(() => ({}));
            if (!checkResponse.ok || hasBlockers(checked)) {
                return fail(checkResponse.ok ? 422 : checkResponse.status, {
                    risk_review: review, risk_dry_run: checked,
                    error: 'The latest dry-run did not authorize a create action. Nothing was saved.'
                });
            }
            const commitResponse = await fetchAiOnboardingBackend(event, '/ai/onboarding/risk-scenarios/commit/',
                riskCommitPayload(review.folder_reference, review.assessment_reference, review.scenario, false));
            const result = await commitResponse.json().catch(() => ({}));
            if (!commitResponse.ok) return fail(commitResponse.status, {
                risk_review: review, risk_dry_run: checked, risk_result: result, error: errorDetail(result)
            });
            return { risk_result: result,
                message: Array.isArray(result.created_records) && result.created_records.length
                    ? 'A real risk scenario was created. Open Risk Scenarios to review/edit it.'
                    : 'No new scenario was created. Review the returned status and any reused record.' };
        } catch (error) {
            return fail(502, { error: errorDetail(error) });
        }
    },

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
