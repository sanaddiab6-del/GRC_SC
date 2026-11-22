/**
 * The single source of truth for every Local AI onboarding step action (Steps 1 through 12B).
 *
 * Each entry maps the named client action to the backend `ai_onboarding` endpoint it proxies and
 * to the platform resource the step actually writes. The resource is what decides which page the
 * step belongs on, so keeping it next to the endpoint keeps the UI placement and the transport
 * from drifting apart.
 *
 * Both the shared `/fe-api/ai-onboarding/[action]` proxy and the pre-existing
 * `[model=urlmodel]` proxies read this map, so an action can never resolve to a different
 * backend endpoint depending on which route it entered through.
 */

/** Platform resource a step writes to. Used only to document/verify step placement. */
export type AiOnboardingResource =
	| 'assets'
	| 'applied-controls'
	| 'evidences'
	| 'risk-scenarios'
	| 'compliance-assessments';

export const AI_ONBOARDING_ACTIONS = {
	aiAssetSuggest: { endpoint: '/ai/onboarding/assets/suggest/', resource: 'assets' },
	aiAssetCommit: { endpoint: '/ai/onboarding/assets/commit/', resource: 'assets' },
	aiAppliedControlSuggest: {
		endpoint: '/ai/onboarding/applied-controls/suggest/',
		resource: 'applied-controls'
	},
	aiAppliedControlCommit: {
		endpoint: '/ai/onboarding/applied-controls/commit/',
		resource: 'applied-controls'
	},
	aiEvidenceFindingSuggest: {
		endpoint: '/ai/onboarding/evidence-findings/suggest/',
		resource: 'evidences'
	},
	aiEvidenceFindingCommit: {
		endpoint: '/ai/onboarding/evidence-findings/commit/',
		resource: 'evidences'
	},
	aiRemediationActionSuggest: {
		endpoint: '/ai/onboarding/remediation-actions/suggest/',
		resource: 'applied-controls'
	},
	aiRemediationActionCommit: {
		endpoint: '/ai/onboarding/remediation-actions/commit/',
		resource: 'applied-controls'
	},
	aiFrameworkControlMappingSuggest: {
		endpoint: '/ai/onboarding/framework-control-mappings/suggest/',
		resource: 'compliance-assessments'
	},
	aiFrameworkControlMappingCommit: {
		endpoint: '/ai/onboarding/framework-control-mappings/commit/',
		resource: 'compliance-assessments'
	},
	aiRiskScenarioSuggest: {
		endpoint: '/ai/onboarding/risk-scenarios/suggest/',
		resource: 'risk-scenarios'
	},
	aiRiskScenarioCommit: {
		endpoint: '/ai/onboarding/risk-scenarios/commit/',
		resource: 'risk-scenarios'
	},
	aiControlEffectivenessSuggest: {
		endpoint: '/ai/onboarding/control-effectiveness/suggest/',
		resource: 'compliance-assessments'
	},
	aiControlEffectivenessCommit: {
		endpoint: '/ai/onboarding/control-effectiveness/commit/',
		resource: 'compliance-assessments'
	},
	aiAuditReadinessSuggest: {
		endpoint: '/ai/onboarding/audit-readiness/suggest/',
		resource: 'compliance-assessments'
	},
	aiAuditReadinessCommit: {
		endpoint: '/ai/onboarding/audit-readiness/commit/',
		resource: 'compliance-assessments'
	},
	aiAuditReportSuggest: {
		endpoint: '/ai/onboarding/audit-report/suggest/',
		resource: 'compliance-assessments'
	},
	aiAuditReportCommit: {
		endpoint: '/ai/onboarding/audit-report/commit/',
		resource: 'compliance-assessments'
	},
	aiFinalReviewSuggest: {
		endpoint: '/ai/onboarding/final-review/suggest/',
		resource: 'compliance-assessments'
	},
	aiFinalReviewCommit: {
		endpoint: '/ai/onboarding/final-review/commit/',
		resource: 'compliance-assessments'
	}
} as const satisfies Record<string, { endpoint: string; resource: AiOnboardingResource }>;

export type AiOnboardingAction = keyof typeof AI_ONBOARDING_ACTIONS;

/** Backend endpoint for a named action, or `null` when the name is not a known step action. */
export function aiOnboardingEndpoint(action: string | null | undefined): string | null {
	if (!action) return null;
	return AI_ONBOARDING_ACTIONS[action as AiOnboardingAction]?.endpoint ?? null;
}

/**
 * The route every step component posts to.
 *
 * Steps live on the page that owns their resource, so the transport must not depend on which
 * page is open. A single route keeps authentication, payload validation, and the action
 * allowlist in one place instead of one copy per destination page.
 */
export function aiOnboardingActionUrl(action: AiOnboardingAction): string {
	return `/fe-api/ai-onboarding/${action}`;
}

/** Endpoint-only view of the map, for callers that only resolve names to backend paths. */
export const AI_ONBOARDING_ACTION_ENDPOINTS: Record<string, string> = Object.fromEntries(
	Object.entries(AI_ONBOARDING_ACTIONS).map(([action, entry]) => [action, entry.endpoint])
);
