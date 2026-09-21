/**
 * Where each Local AI Case Onboarding step lives, and what has to be finished before it unlocks.
 *
 * A step is placed on the page that manages the resource it actually writes, so the user follows
 * the data instead of returning to Assets between steps. This table is the single description of
 * that placement: the guardrail shown when a prerequisite is missing links to the page named
 * here, so the "go do the previous step over there" hint can never point at the wrong page.
 */

export interface AiOnboardingStepInfo {
	/** Step label as it appears in the UI and in the backend design docs. */
	id: string;
	/** Short human name of the step. */
	title: string;
	/** Page the step is rendered on. */
	page: string;
	/** Link to that page. `null` for steps that live in the sidebar Quick Start modal. */
	href: string | null;
}

export const AI_ONBOARDING_STEPS: Record<string, AiOnboardingStepInfo> = {
	'1': {
		id: 'Step 1',
		title: 'Case intake',
		page: 'Quick Start · Local AI Case Onboarding',
		href: null
	},
	'2': {
		id: 'Step 2',
		title: 'Case setup',
		page: 'Quick Start · Local AI Case Onboarding',
		href: null
	},
	'3A': { id: 'Step 3A', title: 'Asset suggestion', page: 'Assets', href: '/assets' },
	'3B': { id: 'Step 3B', title: 'Asset commit', page: 'Assets', href: '/assets' },
	'4A': {
		id: 'Step 4A',
		title: 'Applied control suggestion',
		page: 'Applied controls',
		href: '/applied-controls'
	},
	'4B': {
		id: 'Step 4B',
		title: 'Applied control commit',
		page: 'Applied controls',
		href: '/applied-controls'
	},
	'5A': {
		id: 'Step 5A',
		title: 'Evidence / finding suggestion',
		page: 'Evidences',
		href: '/evidences'
	},
	'5B': {
		id: 'Step 5B',
		title: 'Evidence / finding commit',
		page: 'Evidences',
		href: '/evidences'
	},
	'6A': {
		id: 'Step 6A',
		title: 'Remediation action suggestion',
		page: 'Applied controls',
		href: '/applied-controls'
	},
	'6B': {
		id: 'Step 6B',
		title: 'Remediation action commit',
		page: 'Applied controls',
		href: '/applied-controls'
	},
	'7A': {
		id: 'Step 7A',
		title: 'Framework control mapping suggestion',
		page: 'the audit',
		href: null
	},
	'7B': {
		id: 'Step 7B',
		title: 'Framework control mapping commit',
		page: 'the audit',
		href: null
	},
	'8A': {
		id: 'Step 8A',
		title: 'Risk scenario suggestion',
		page: 'Risk scenarios',
		href: '/risk-scenarios'
	},
	'8B': {
		id: 'Step 8B',
		title: 'Risk scenario commit',
		page: 'Risk scenarios',
		href: '/risk-scenarios'
	},
	'9A': {
		id: 'Step 9A',
		title: 'Control effectiveness suggestion',
		page: 'the audit',
		href: null
	},
	'9B': { id: 'Step 9B', title: 'Control effectiveness commit', page: 'the audit', href: null },
	'10A': { id: 'Step 10A', title: 'Audit readiness summary', page: 'the audit', href: null },
	'10B': { id: 'Step 10B', title: 'Audit readiness commit', page: 'the audit', href: null },
	'11A': { id: 'Step 11A', title: 'Report draft', page: 'the audit', href: null },
	'11B': { id: 'Step 11B', title: 'Report save commit', page: 'the audit', href: null },
	'12A': { id: 'Step 12A', title: 'Final review summary', page: 'the audit', href: null },
	'12B': { id: 'Step 12B', title: 'Case handoff commit', page: 'the audit', href: null }
};

/**
 * Steps 7 and 9 through 12 all act on the audit that Step 2 created, so their page link is only
 * known once a compliance assessment id exists.
 */
export function stepHref(step: string, complianceAssessmentId: string): string | null {
	const info = AI_ONBOARDING_STEPS[step];
	if (!info) return null;
	if (info.href) return info.href;
	if (info.page === 'the audit' && complianceAssessmentId) {
		return `/compliance-assessments/${complianceAssessmentId}`;
	}
	return null;
}

export function stepPageLabel(step: string): string {
	return AI_ONBOARDING_STEPS[step]?.page ?? 'another page';
}

/** Context key carrying the step ids the surrounding panel renders. */
export const AI_ONBOARDING_PAGE_STEPS = Symbol('ai-onboarding-page-steps');
