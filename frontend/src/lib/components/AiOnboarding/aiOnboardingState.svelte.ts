import { browser } from '$app/environment';
import { aiOnboardingActionUrl, type AiOnboardingAction } from '$lib/utils/aiOnboardingActions';
import {
	buildReviewedAppliedControlDecisions,
	getAutoReuseAppliedControlMatch,
	type AppliedControlDuplicateCandidate
} from '$lib/components/Assets/appliedControlCommitDecisions';
import {
	buildReviewedAssetDecisions,
	getAutoReuseMatch,
	type DuplicateCandidate
} from '$lib/components/Assets/assetCommitDecisions';

/**
 * Shared workflow state for the Local AI Case Onboarding steps.
 *
 * Steps 3A through 12B used to live in a single component on the Assets page, so every draft,
 * hash, selection, dry-run, and commit result was ordinary component state. Each step now
 * renders on the page that owns the resource it writes, so the same values have to survive
 * client-side navigation between those pages — that is the only reason this module exists.
 *
 * Nothing here changes what a step does. The payload builders, prerequisite checks, dry-run
 * gating, and approval flags are the ones the single-page implementation used; they were moved,
 * not rewritten. Authorization, scope validation, and every write guardrail remain in the Django
 * `ai_onboarding` services.
 */

/** Step 2 writes this key; the onboarding steps read the case reference back out of it. */
const SETUP_STORAGE_KEY = 'sanad_ai_onboarding_setup';
/** Everything Steps 3A-12B produce, so navigating between destination pages keeps the flow. */
const WORKFLOW_STORAGE_KEY = 'sanad_ai_onboarding_workflow';

export type AiOnboardingLoading =
	| 'suggest'
	| 'dry-run'
	| 'commit'
	| 'control-suggest'
	| 'control-dry-run'
	| 'control-commit'
	| 'evidence-suggest'
	| 'evidence-commit-dry-run'
	| 'evidence-commit'
	| 'remediation-suggest'
	| 'remediation-commit-dry-run'
	| 'remediation-commit'
	| 'framework-mapping-suggest'
	| 'framework-mapping-commit-dry-run'
	| 'framework-mapping-commit'
	| 'risk-scenario-suggest'
	| 'risk-scenario-commit-dry-run'
	| 'risk-scenario-commit'
	| 'control-effectiveness-suggest'
	| 'control-effectiveness-commit-dry-run'
	| 'control-effectiveness-commit'
	| 'audit-readiness-suggest'
	| 'audit-readiness-commit-dry-run'
	| 'audit-readiness-commit'
	| 'audit-report-suggest'
	| 'audit-report-commit-dry-run'
	| 'audit-report-commit'
	| 'final-review-suggest'
	| 'final-review-commit-dry-run'
	| 'final-review-commit'
	| null;

function initialState() {
	return {
		/** Set once the browser has read the persisted case reference and workflow snapshot. */
		hydrated: false,
		/** Step 2 handoff timestamp the persisted workflow snapshot belongs to. */
		setupCreatedAt: '',
		sourceStep1DraftHash: '',
		setupReference: {
			folder_id: '',
			perimeter_id: '',
			compliance_assessment_id: '',
			risk_assessment_id: '',
			selected_framework_id: ''
		},
		scenarioText: '',
		scopeSummary: '',
		knownWeaknesses: '',
		strictMode: true,
		loading: null as AiOnboardingLoading,
		error: null as any,
		caseContext: null as any,
		// Step 3
		assetDraft: null as any,
		assetDraftHash: '',
		selectedTemporaryIds: {} as Record<string, boolean>,
		commitApproved: false,
		commitDryRun: null as any,
		commitResult: null as any,
		assetCommitHash: '',
		// Step 4
		appliedControlDraft: null as any,
		appliedControlDraftHash: '',
		selectedAppliedControlTemporaryIds: {} as Record<string, boolean>,
		appliedControlCommitApproved: false,
		appliedControlCommitDryRun: null as any,
		appliedControlCommitResult: null as any,
		appliedControlCommitHash: '',
		// Step 5
		evidenceFindingDraft: null as any,
		evidenceFindingDraftHash: '',
		selectedEvidenceRequestIds: {} as Record<string, boolean>,
		selectedAuditQuestionIds: {} as Record<string, boolean>,
		selectedPreliminaryFindingIds: {} as Record<string, boolean>,
		evidenceFindingCommitApproved: false,
		evidenceFindingCommitDryRun: null as any,
		evidenceFindingCommitResult: null as any,
		// Step 6A is advisory only: there is no commit state, no dry-run state, and no approval flag.
		remediationActionDraft: null as any,
		// Step 6B is the deterministic write step for the Step 6A suggestions.
		selectedRemediationActionIds: {} as Record<string, boolean>,
		remediationCommitApproved: false,
		remediationCommitDryRun: null as any,
		// Selection the last successful dry-run actually covered. See `selectionKey`.
		remediationDryRunSelectionKey: '',
		remediationCommitResult: null as any,
		// Step 7A is advisory only: no commit state, no dry-run state, and no approval flag.
		frameworkControlMappingDraft: null as any,
		// Step 7B is the deterministic write step for the Step 7A framework mappings.
		selectedFrameworkMappingIds: {} as Record<string, boolean>,
		frameworkMappingCommitApproved: false,
		frameworkMappingCommitDryRun: null as any,
		frameworkMappingDryRunSelectionKey: '',
		frameworkMappingCommitResult: null as any,
		// Step 8A is advisory only: no commit state, no dry-run state, and no approval flag.
		riskScenarioDraft: null as any,
		// Step 8B is the deterministic write step for the Step 8A risk scenarios.
		selectedRiskScenarioIds: {} as Record<string, boolean>,
		riskScenarioCommitApproved: false,
		riskScenarioCommitDryRun: null as any,
		riskScenarioDryRunSelectionKey: '',
		riskScenarioCommitResult: null as any,
		// Step 9A is advisory only: no commit state, no dry-run state, and no approval flag.
		controlEffectivenessDraft: null as any,
		// Step 9B is the deterministic write step for the Step 9A judgements.
		selectedControlEffectivenessIds: {} as Record<string, boolean>,
		controlEffectivenessCommitApproved: false,
		controlEffectivenessCommitDryRun: null as any,
		controlEffectivenessDryRunSelectionKey: '',
		controlEffectivenessCommitResult: null as any,
		// Step 10A is advisory only: no commit state, no dry-run state, and no approval flag.
		auditReadinessDraft: null as any,
		// Step 10B is the deterministic write step for the Step 10A readiness summary.
		auditReadinessSelected: false,
		auditReadinessCommitApproved: false,
		auditReadinessCommitDryRun: null as any,
		auditReadinessCommitResult: null as any,
		// Step 11A is advisory only: no commit state, no dry-run state, and no approval flag.
		auditReportDraft: null as any,
		// Step 11B is the deterministic write step for the Step 11A report draft.
		auditReportSelected: false,
		auditReportCommitApproved: false,
		auditReportCommitDryRun: null as any,
		auditReportCommitResult: null as any,
		// Step 12A is advisory only: no commit state, no dry-run state, and no approval flag.
		finalReviewDraft: null as any,
		// Step 12B is the deterministic write step for the Step 12A handoff summary.
		finalReviewSelected: false,
		finalReviewCommitApproved: false,
		finalReviewCommitDryRun: null as any,
		finalReviewCommitResult: null as any
	};
}

export type AiOnboardingState = ReturnType<typeof initialState>;

export const ai = $state<AiOnboardingState>(initialState());

/** Fields that are never persisted: they describe an in-flight request, not workflow progress. */
const TRANSIENT_KEYS = new Set(['hydrated', 'loading', 'error']);

function persistableSnapshot() {
	const snapshot: Record<string, any> = { setup_created_at: ai.setupCreatedAt };
	for (const key of Object.keys(initialState()) as (keyof AiOnboardingState)[]) {
		if (TRANSIENT_KEYS.has(key as string)) continue;
		snapshot[key as string] = $state.snapshot(ai[key]);
	}
	return snapshot;
}

function persist() {
	if (!browser) return;
	try {
		localStorage.setItem(WORKFLOW_STORAGE_KEY, JSON.stringify(persistableSnapshot()));
	} catch {
		// A full or unavailable localStorage must never break a step; the flow simply stops
		// surviving navigation until the quota frees up.
	}
}

function readJson(key: string) {
	try {
		const stored = localStorage.getItem(key);
		return stored ? JSON.parse(stored) : null;
	} catch {
		return null;
	}
}

let hydrating = false;

/**
 * Loads the Step 2 case reference and any persisted Steps 3A-12B progress.
 *
 * Called from `onMount`, never at module load: the server renders without `localStorage`, so
 * reading it any earlier would make the first client render disagree with the server HTML.
 * Safe to call from every mounted step panel; only the first call does the work.
 */
export function hydrateAiOnboarding() {
	if (!browser || ai.hydrated || hydrating) return;
	hydrating = true;

	const setup = readJson(SETUP_STORAGE_KEY);
	const workflow = readJson(WORKFLOW_STORAGE_KEY);
	const setupCreatedAt = setup?.created_at ?? '';

	if (setup) {
		ai.setupCreatedAt = setupCreatedAt;
		ai.sourceStep1DraftHash = setup.source_step1_draft_hash ?? '';
		ai.scenarioText = setup.scenario_summary ?? '';
		ai.caseContext = setup.case_context ?? null;
		ai.setupReference = {
			folder_id: setup.setupReference?.folder_id ?? '',
			perimeter_id: setup.setupReference?.perimeter_id ?? '',
			compliance_assessment_id: setup.setupReference?.compliance_assessment_id ?? '',
			risk_assessment_id: setup.setupReference?.risk_assessment_id ?? '',
			selected_framework_id: setup.setupReference?.selected_framework_id ?? ''
		};
	}

	// A workflow snapshot only belongs to the case Step 2 last created. Re-running Step 2 starts
	// a new case, and carrying the previous case's drafts, hashes, and commit results into it
	// would let a later step hand a stale reference to the backend.
	if (workflow && (!setup || workflow.setup_created_at === setupCreatedAt)) {
		for (const key of Object.keys(initialState()) as (keyof AiOnboardingState)[]) {
			if (TRANSIENT_KEYS.has(key as string)) continue;
			if (!(key in workflow)) continue;
			(ai as any)[key] = workflow[key as string];
		}
		ai.setupCreatedAt = setupCreatedAt;
	} else if (workflow) {
		try {
			localStorage.removeItem(WORKFLOW_STORAGE_KEY);
		} catch {
			// Ignore: the mismatched snapshot was already refused above.
		}
	}

	ai.hydrated = true;
	hydrating = false;

	// One root for the whole app session. It has to outlive any individual step panel, since
	// panels unmount whenever the user navigates to the next step's page.
	$effect.root(() => {
		$effect(() => {
			if (!ai.hydrated) return;
			persist();
		});
	});
}

/** Clears the persisted onboarding progress. Never touches platform data. */
export function resetAiOnboardingWorkflow() {
	const fresh = initialState();
	for (const key of Object.keys(fresh) as (keyof AiOnboardingState)[]) {
		(ai as any)[key] = (fresh as any)[key];
	}
	ai.hydrated = true;
	if (browser) {
		try {
			localStorage.removeItem(WORKFLOW_STORAGE_KEY);
		} catch {
			// Nothing to do: the in-memory state was already reset.
		}
	}
}

// ---- Transport ---------------------------------------------------------------------------

function stableStringify(value: any): string {
	if (value === null || typeof value !== 'object') return JSON.stringify(value);
	if (Array.isArray(value)) return `[${value.map((item) => stableStringify(item)).join(',')}]`;
	return `{${Object.keys(value)
		.sort()
		.map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`)
		.join(',')}}`;
}

async function sha256Draft(value: any) {
	const digest = await crypto.subtle.digest(
		'SHA-256',
		new TextEncoder().encode(stableStringify(value))
	);
	return `sha256:${Array.from(new Uint8Array(digest))
		.map((byte) => byte.toString(16).padStart(2, '0'))
		.join('')}`;
}

/**
 * Posts a step payload to the shared onboarding proxy.
 *
 * The proxy refuses an unauthenticated caller itself and forwards the caller's own credentials,
 * so a step never reaches Django anonymously and never gains privileges it did not already have.
 */
async function postAiAction(action: AiOnboardingAction, payload: any) {
	const response = await fetch(aiOnboardingActionUrl(action), {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(payload)
	});

	const responseText = await response.text();

	// Parsing is kept out of the throw path so a backend error surfaces as its own object
	// instead of being re-wrapped as a raw JSON string.
	let parsed: any = null;
	let parsedJson = false;
	try {
		parsed = JSON.parse(responseText);
		parsedJson = true;
	} catch {
		// If the response is not JSON, fall through to a plain detail message.
	}

	if (parsedJson) {
		if (response.ok) return parsed;
		if (parsed && typeof parsed === 'object') throw parsed;
	}

	throw { detail: responseText || `AI request failed with status ${response.status}.` };
}

// ---- Shared payload helpers --------------------------------------------------------------

function cleanSetupReferenceForSuggestion() {
	return {
		folder_id: ai.setupReference.folder_id,
		perimeter_id: ai.setupReference.perimeter_id || null,
		compliance_assessment_id: ai.setupReference.compliance_assessment_id || null,
		risk_assessment_id: ai.setupReference.risk_assessment_id || null
	};
}

function cleanSetupReferenceForCommit() {
	return {
		folder_id: ai.setupReference.folder_id,
		perimeter_id: ai.setupReference.perimeter_id || null,
		compliance_assessment_id: ai.setupReference.compliance_assessment_id || null,
		risk_assessment_id: ai.setupReference.risk_assessment_id || null,
		selected_framework_id: ai.setupReference.selected_framework_id || null
	};
}

export function knownWeaknessList() {
	return ai.knownWeaknesses
		.split('\n')
		.map((item) => item.trim())
		.filter(Boolean);
}

export function approvedAssetReferences() {
	const assets = [
		...(ai.commitResult?.created_assets ?? []),
		...(ai.commitResult?.reused_assets ?? [])
	];
	return assets
		.filter((asset: any) => asset?.asset_id)
		.map((asset: any) => ({
			asset_id: asset.asset_id,
			name: asset.name,
			ref_id: asset.ref_id ?? asset.reference_id ?? null,
			asset_class: asset.asset_class ?? null,
			type: asset.type ?? null,
			source_temporary_id: asset.source_temporary_id ?? asset.temporary_id ?? null
		}));
}

export function buildApprovedAppliedControlReferences() {
	const controls = [
		...(ai.appliedControlCommitResult?.created_applied_controls ?? []),
		...(ai.appliedControlCommitResult?.reused_applied_controls ?? [])
	];
	return controls
		.filter((control: any) => control?.applied_control_id)
		.map((control: any) => ({
			applied_control_id: control.applied_control_id,
			name: control.name,
			ref_id: control.ref_id ?? null,
			category: control.category ?? null,
			status: control.status ?? null,
			source_temporary_id: control.source_temporary_id ?? null
		}));
}

/**
 * A dry-run only vouches for the exact items it ran against. Changing the selection afterwards
 * must not carry that result over, otherwise the approved commit would write items no dry-run
 * ever previewed.
 */
function selectionKey(items: any[]) {
	return items
		.map((item: any) => item.temporary_id)
		.sort()
		.join('|');
}

// ---- Step 3A: advisory asset suggestion --------------------------------------------------

export function providerMode() {
	return ai.assetDraft?.provider_mode ?? ai.assetDraft?.source_summary?.provider_mode ?? 'not run';
}

export function isConfiguredLocalProvider() {
	return providerMode() === 'configured_local_provider';
}

export function selectedCandidates() {
	return (ai.assetDraft?.candidate_assets ?? []).filter(
		(candidate: any) => ai.selectedTemporaryIds[candidate.temporary_id]
	);
}

export function duplicateCandidates(): DuplicateCandidate[] {
	return (ai.assetDraft?.duplicate_candidates ?? []) as DuplicateCandidate[];
}

export { getAutoReuseMatch, getAutoReuseAppliedControlMatch };

function buildSuggestionPayload() {
	return {
		source_step1_draft_hash: ai.sourceStep1DraftHash,
		case_setup_reference: cleanSetupReferenceForSuggestion(),
		folder_id: ai.setupReference.folder_id,
		perimeter_id: ai.setupReference.perimeter_id || null,
		compliance_assessment_id: ai.setupReference.compliance_assessment_id || null,
		risk_assessment_id: ai.setupReference.risk_assessment_id || null,
		scenario_text: ai.scenarioText,
		scope_summary: ai.scopeSummary,
		known_weaknesses: knownWeaknessList(),
		selected_framework_id: ai.setupReference.selected_framework_id || null,
		strict_mode: ai.strictMode
	};
}

export async function runSuggestion() {
	ai.loading = 'suggest';
	ai.error = null;
	ai.commitDryRun = null;
	ai.commitResult = null;
	ai.assetCommitHash = '';
	ai.appliedControlDraft = null;
	ai.appliedControlDraftHash = '';
	ai.selectedAppliedControlTemporaryIds = {};
	ai.appliedControlCommitApproved = false;
	ai.appliedControlCommitDryRun = null;
	ai.appliedControlCommitResult = null;
	try {
		ai.assetDraft = await postAiAction('aiAssetSuggest', buildSuggestionPayload());
		ai.assetDraftHash = await sha256Draft(ai.assetDraft);
		ai.selectedTemporaryIds = Object.fromEntries(
			(ai.assetDraft?.candidate_assets ?? []).map((candidate: any) => [
				candidate.temporary_id,
				false
			])
		);
	} catch (caught) {
		ai.error = caught;
	} finally {
		ai.loading = null;
	}
}

// ---- Step 3B: deterministic asset commit -------------------------------------------------

function buildAssetDecisions() {
	return buildReviewedAssetDecisions(selectedCandidates() as any[], duplicateCandidates());
}

function buildCommitPayload(dryRun: boolean) {
	if (!ai.assetDraft || !ai.assetDraftHash) throw { detail: 'Run Step 3A before Step 3B.' };
	if (!selectedCandidates().length) throw { detail: 'Select at least one candidate asset.' };
	if (!dryRun && !ai.commitApproved)
		throw { detail: 'Approve the deterministic asset write first.' };

	return {
		dry_run: dryRun,
		approved_by_user: !dryRun && ai.commitApproved,
		idempotency_key: dryRun ? null : `frontend-step3b-${Date.now()}`,
		source_step1_draft_hash: ai.sourceStep1DraftHash,
		source_asset_draft_hash: ai.assetDraftHash,
		case_setup_reference: cleanSetupReferenceForCommit(),
		asset_decisions: buildAssetDecisions()
	};
}

export async function runCommit(dryRun: boolean) {
	ai.loading = dryRun ? 'dry-run' : 'commit';
	ai.error = null;
	try {
		const result = await postAiAction('aiAssetCommit', buildCommitPayload(dryRun));
		if (dryRun) ai.commitDryRun = result;
		else {
			ai.commitResult = result;
			ai.assetCommitHash = await sha256Draft(result);
			ai.appliedControlDraft = null;
			ai.appliedControlDraftHash = '';
			ai.selectedAppliedControlTemporaryIds = {};
			ai.appliedControlCommitApproved = false;
			ai.appliedControlCommitDryRun = null;
			ai.appliedControlCommitResult = null;
			ai.appliedControlCommitHash = '';
			ai.evidenceFindingDraft = null;
			ai.remediationActionDraft = null;
		}
	} catch (caught) {
		ai.error = caught;
	} finally {
		ai.loading = null;
	}
}

// ---- Step 4A: advisory applied control suggestion ----------------------------------------

export function appliedControlProviderMode() {
	return (
		ai.appliedControlDraft?.provider_mode ??
		ai.appliedControlDraft?.source_summary?.provider_mode ??
		'not run'
	);
}

export function isAppliedControlConfiguredLocalProvider() {
	return appliedControlProviderMode() === 'configured_local_provider';
}

export function selectedAppliedControlCandidates() {
	return (ai.appliedControlDraft?.candidate_applied_controls ?? []).filter(
		(candidate: any) => ai.selectedAppliedControlTemporaryIds[candidate.temporary_id]
	);
}

export function appliedControlDuplicateCandidates(): AppliedControlDuplicateCandidate[] {
	return (ai.appliedControlDraft?.duplicate_candidates ?? []) as AppliedControlDuplicateCandidate[];
}

function buildAppliedControlSuggestionPayload() {
	if (!ai.commitResult) throw { detail: 'Complete the approved asset commit before Step 4A.' };
	if (!ai.assetCommitHash)
		throw { detail: 'Missing source_asset_commit_hash from Step 3B result.' };
	if (!approvedAssetReferences().length) {
		throw { detail: 'Step 4A requires at least one created or reused approved asset.' };
	}

	return {
		source_step1_draft_hash: ai.sourceStep1DraftHash,
		source_asset_commit_hash: ai.assetCommitHash,
		case_setup_reference: cleanSetupReferenceForCommit(),
		asset_references: approvedAssetReferences(),
		scenario_text: ai.scenarioText,
		scope_summary: ai.scopeSummary,
		known_weaknesses: knownWeaknessList(),
		selected_framework_id: ai.setupReference.selected_framework_id || null,
		user_locale: 'en',
		strict_mode: true
	};
}

export async function runAppliedControlSuggestion() {
	ai.loading = 'control-suggest';
	ai.error = null;
	try {
		ai.appliedControlDraft = await postAiAction(
			'aiAppliedControlSuggest',
			buildAppliedControlSuggestionPayload()
		);
		ai.appliedControlDraftHash = await sha256Draft(ai.appliedControlDraft);
		ai.selectedAppliedControlTemporaryIds = Object.fromEntries(
			(ai.appliedControlDraft?.candidate_applied_controls ?? []).map((candidate: any) => [
				candidate.temporary_id,
				false
			])
		);
		ai.appliedControlCommitApproved = false;
		ai.appliedControlCommitDryRun = null;
		ai.appliedControlCommitResult = null;
		ai.appliedControlCommitHash = '';
		ai.evidenceFindingDraft = null;
		ai.remediationActionDraft = null;
	} catch (caught) {
		ai.error = caught;
	} finally {
		ai.loading = null;
	}
}

// ---- Step 4B: deterministic applied control commit ---------------------------------------

function buildAppliedControlDecisions() {
	return buildReviewedAppliedControlDecisions(
		selectedAppliedControlCandidates() as any[],
		appliedControlDuplicateCandidates()
	);
}

function buildAppliedControlCommitPayload(dryRun: boolean) {
	if (!ai.appliedControlDraft || !ai.appliedControlDraftHash) {
		throw { detail: 'Run Step 4A before Step 4B.' };
	}
	if (!ai.assetCommitHash) throw { detail: 'Complete the approved asset commit before Step 4B.' };
	if (!selectedAppliedControlCandidates().length) {
		throw { detail: 'Select at least one candidate applied control.' };
	}
	if (!dryRun && !ai.appliedControlCommitApproved) {
		throw { detail: 'Approve the deterministic applied-control write first.' };
	}

	return {
		dry_run: dryRun,
		approved_by_user: !dryRun && ai.appliedControlCommitApproved,
		idempotency_key: dryRun ? null : `frontend-step4b-${Date.now()}`,
		source_step1_draft_hash: ai.sourceStep1DraftHash,
		source_asset_commit_hash: ai.assetCommitHash,
		source_applied_control_draft_hash: ai.appliedControlDraftHash,
		case_setup_reference: cleanSetupReferenceForCommit(),
		asset_references: approvedAssetReferences(),
		applied_control_decisions: buildAppliedControlDecisions()
	};
}

export async function runAppliedControlCommit(dryRun: boolean) {
	ai.loading = dryRun ? 'control-dry-run' : 'control-commit';
	ai.error = null;
	try {
		const result = await postAiAction(
			'aiAppliedControlCommit',
			buildAppliedControlCommitPayload(dryRun)
		);
		if (dryRun) ai.appliedControlCommitDryRun = result;
		else {
			ai.appliedControlCommitResult = result;
			ai.appliedControlCommitHash = await sha256Draft(result);
			ai.evidenceFindingDraft = null;
			ai.remediationActionDraft = null;
		}
	} catch (caught) {
		ai.error = caught;
	} finally {
		ai.loading = null;
	}
}

// ---- Step 5A: advisory evidence / finding suggestion -------------------------------------

export function evidenceFindingProviderMode() {
	return (
		ai.evidenceFindingDraft?.provider_mode ??
		ai.evidenceFindingDraft?.source_summary?.provider_mode ??
		'not run'
	);
}

function buildEvidenceFindingSuggestionPayload() {
	if (!ai.appliedControlCommitResult || !ai.appliedControlCommitHash) {
		throw { detail: 'Complete the approved applied control commit (Step 4B) before Step 5A.' };
	}
	if (!ai.assetCommitHash)
		throw { detail: 'Missing source_asset_commit_hash from Step 3B result.' };
	if (!ai.appliedControlDraftHash) {
		throw { detail: 'Missing source_applied_control_draft_hash from Step 4A.' };
	}
	const appliedControlReferences = buildApprovedAppliedControlReferences();
	if (!approvedAssetReferences().length) {
		throw { detail: 'Step 5A requires at least one created or reused approved asset.' };
	}
	if (!appliedControlReferences.length) {
		throw { detail: 'Step 5A requires at least one committed or reused applied control.' };
	}

	return {
		source_step1_draft_hash: ai.sourceStep1DraftHash,
		source_asset_commit_hash: ai.assetCommitHash,
		source_applied_control_draft_hash: ai.appliedControlDraftHash,
		source_applied_control_commit_hash: ai.appliedControlCommitHash,
		case_setup_reference: cleanSetupReferenceForCommit(),
		asset_references: approvedAssetReferences(),
		applied_control_references: appliedControlReferences,
		scenario_text: ai.scenarioText,
		scope_summary: ai.scopeSummary,
		known_weaknesses: knownWeaknessList(),
		selected_framework_id: ai.setupReference.selected_framework_id || null,
		user_locale: 'en',
		strict_mode: true
	};
}

export async function runEvidenceFindingSuggestion() {
	ai.loading = 'evidence-suggest';
	ai.error = null;
	try {
		const draft = await postAiAction(
			'aiEvidenceFindingSuggest',
			buildEvidenceFindingSuggestionPayload()
		);
		ai.evidenceFindingDraft = draft;
		ai.evidenceFindingDraftHash = await sha256Draft(draft);
		ai.selectedEvidenceRequestIds = Object.fromEntries(
			(draft?.evidence_requests ?? []).map((item: any) => [item.temporary_id, false])
		);
		ai.selectedAuditQuestionIds = Object.fromEntries(
			(draft?.audit_questions ?? []).map((item: any) => [item.temporary_id, false])
		);
		ai.selectedPreliminaryFindingIds = Object.fromEntries(
			(draft?.preliminary_findings ?? []).map((item: any) => [item.temporary_id, false])
		);
		ai.evidenceFindingCommitApproved = false;
		ai.evidenceFindingCommitDryRun = null;
		ai.evidenceFindingCommitResult = null;
		ai.remediationActionDraft = null;
	} catch (caught) {
		ai.error = caught;
	} finally {
		ai.loading = null;
	}
}

// ---- Step 5B: deterministic evidence / finding commit ------------------------------------

function buildEvidenceFindingDecisions(
	items: any[],
	selection: Record<string, boolean>,
	kind: string
) {
	return (items ?? [])
		.filter((item: any) => selection[item.temporary_id])
		.map((item: any) => ({
			temporary_id: item.temporary_id,
			kind,
			selected: true,
			action: 'create',
			human_approved: ai.evidenceFindingCommitApproved,
			approved_fields: {
				name: item.title ?? item.question_text ?? null,
				description: item.description ?? item.summary ?? item.rationale ?? null
			},
			original_suggestion_summary: {
				title: item.title ?? null,
				question_text: item.question_text ?? null,
				summary: item.summary ?? null,
				rationale: item.rationale ?? null,
				review_status: item.review_status ?? null,
				confidence: item.confidence,
				related_weaknesses: item.related_weaknesses ?? [],
				linked_asset_ids: item.linked_asset_ids ?? [],
				linked_applied_control_ids: item.linked_applied_control_ids ?? []
			}
		}));
}

export function selectedEvidenceFindingCount() {
	const draft = ai.evidenceFindingDraft;
	if (!draft) return 0;
	return (
		buildEvidenceFindingDecisions(draft.evidence_requests, ai.selectedEvidenceRequestIds, 'x')
			.length +
		buildEvidenceFindingDecisions(draft.audit_questions, ai.selectedAuditQuestionIds, 'x').length +
		buildEvidenceFindingDecisions(draft.preliminary_findings, ai.selectedPreliminaryFindingIds, 'x')
			.length
	);
}

function buildEvidenceFindingCommitPayload(dryRun: boolean) {
	if (!ai.evidenceFindingDraft || !ai.evidenceFindingDraftHash) {
		throw { detail: 'Run Step 5A before Step 5B.' };
	}
	if (!ai.appliedControlCommitHash) {
		throw { detail: 'Complete the approved applied control commit (Step 4B) before Step 5B.' };
	}
	if (!selectedEvidenceFindingCount()) {
		throw { detail: 'Select at least one evidence/finding suggestion to commit.' };
	}
	if (!dryRun && !ai.evidenceFindingCommitApproved) {
		throw { detail: 'Approve the deterministic Step 5B write first.' };
	}

	return {
		dry_run: dryRun,
		approved_by_user: !dryRun && ai.evidenceFindingCommitApproved,
		idempotency_key: dryRun ? null : `frontend-step5b-${Date.now()}`,
		source_step1_draft_hash: ai.sourceStep1DraftHash,
		source_asset_commit_hash: ai.assetCommitHash,
		source_applied_control_commit_hash: ai.appliedControlCommitHash,
		source_evidence_finding_draft_hash: ai.evidenceFindingDraftHash,
		case_setup_reference: cleanSetupReferenceForCommit(),
		asset_references: approvedAssetReferences(),
		applied_control_references: buildApprovedAppliedControlReferences(),
		evidence_request_decisions: buildEvidenceFindingDecisions(
			ai.evidenceFindingDraft.evidence_requests,
			ai.selectedEvidenceRequestIds,
			'evidence_request'
		),
		audit_question_decisions: buildEvidenceFindingDecisions(
			ai.evidenceFindingDraft.audit_questions,
			ai.selectedAuditQuestionIds,
			'audit_question'
		),
		preliminary_finding_decisions: buildEvidenceFindingDecisions(
			ai.evidenceFindingDraft.preliminary_findings,
			ai.selectedPreliminaryFindingIds,
			'preliminary_finding'
		)
	};
}

export async function runEvidenceFindingCommit(dryRun: boolean) {
	ai.loading = dryRun ? 'evidence-commit-dry-run' : 'evidence-commit';
	ai.error = null;
	try {
		const result = await postAiAction(
			'aiEvidenceFindingCommit',
			buildEvidenceFindingCommitPayload(dryRun)
		);
		if (dryRun) ai.evidenceFindingCommitDryRun = result;
		else ai.evidenceFindingCommitResult = result;
	} catch (caught) {
		ai.error = caught;
	} finally {
		ai.loading = null;
	}
}

// ---- Step 6A: advisory remediation suggestion. No commit, no dry-run, no write. ----------

function toContextItem(reference: any, title: any, description: any = null) {
	const readableTitle = typeof title === 'string' ? title.trim() : '';
	if (!readableTitle) return null;
	const readableReference = typeof reference === 'string' ? reference.trim() : '';
	const readableDescription = typeof description === 'string' ? description.trim() : '';
	return {
		reference: readableReference ? readableReference.slice(0, 200) : null,
		title: readableTitle.slice(0, 500),
		description: readableDescription ? readableDescription.slice(0, 5000) : null
	};
}

function buildRemediationContextItems(items: any[], toTitle: (item: any, index: number) => any) {
	return (items ?? [])
		.map((item: any, index: number) =>
			toContextItem(
				item?.temporary_id ?? item?.reference ?? null,
				toTitle(item, index),
				item?.description ?? item?.summary ?? item?.rationale ?? null
			)
		)
		.filter(Boolean);
}

export function remediationActionProviderMode() {
	return ai.remediationActionDraft?.provider_mode ?? 'not run';
}

function buildRemediationActionSuggestionPayload() {
	const preliminaryFindings = buildRemediationContextItems(
		ai.evidenceFindingDraft?.preliminary_findings ?? [],
		(item, index) => displayFindingTitle(item, index)
	);
	const weaknesses = knownWeaknessList();
	if (!preliminaryFindings.length && !weaknesses.length) {
		throw {
			detail: 'Step 6A needs at least one Step 5A preliminary finding or one known weakness.'
		};
	}

	const caseSummary = [ai.scenarioText, ai.scopeSummary]
		.map((value) => (typeof value === 'string' ? value.trim() : ''))
		.filter(Boolean)
		.join('\n\n');

	// Optional references are sent when available; missing ones never block the request.
	return {
		case_summary: caseSummary.slice(0, 20000),
		scenario_name: (ai.scopeSummary || ai.scenarioText || '').trim().slice(0, 500),
		folder_reference: {
			folder_id: ai.setupReference.folder_id || null,
			folder_name: null
		},
		assets: approvedAssetReferences()
			.map((asset: any) => toContextItem(asset.ref_id ?? asset.asset_id, asset.name))
			.filter(Boolean),
		applied_controls: buildApprovedAppliedControlReferences()
			.map((control: any) =>
				toContextItem(control.ref_id ?? control.applied_control_id, control.name)
			)
			.filter(Boolean),
		evidence_requests: buildRemediationContextItems(
			ai.evidenceFindingDraft?.evidence_requests ?? [],
			(item, index) => displayEvidenceTitle(item, index)
		),
		audit_questions: buildRemediationContextItems(
			ai.evidenceFindingDraft?.audit_questions ?? [],
			(item, index) => displayAuditQuestionTitle(item, index)
		),
		preliminary_findings: preliminaryFindings,
		known_weaknesses: weaknesses,
		user_locale: 'en',
		strict_mode: true
	};
}

export async function runRemediationActionSuggestion() {
	ai.loading = 'remediation-suggest';
	ai.error = null;
	try {
		const draft = await postAiAction(
			'aiRemediationActionSuggest',
			buildRemediationActionSuggestionPayload()
		);
		ai.remediationActionDraft = draft;
		ai.selectedRemediationActionIds = Object.fromEntries(
			(draft?.remediation_actions ?? []).map((action: any) => [action.temporary_id, false])
		);
		ai.remediationCommitApproved = false;
		ai.remediationCommitDryRun = null;
		ai.remediationCommitResult = null;
	} catch (caught) {
		ai.error = caught;
	} finally {
		ai.loading = null;
	}
}

// ---- Step 6B: deterministic commit. No AI model is called in this step. ------------------

export function selectedRemediationActions() {
	return (ai.remediationActionDraft?.remediation_actions ?? []).filter(
		(action: any) => ai.selectedRemediationActionIds[action.temporary_id]
	);
}

export function remediationDryRunSucceeded() {
	return (
		Boolean(ai.remediationCommitDryRun) &&
		ai.remediationDryRunSelectionKey === selectionKey(selectedRemediationActions()) &&
		!(ai.remediationCommitDryRun?.blocking_errors ?? []).length &&
		ai.remediationCommitDryRun?.commit_status !== 'blocked'
	);
}

function buildRemediationActionCommitPayload(dryRun: boolean) {
	if (!ai.remediationActionDraft) throw { detail: 'Run Step 6A before Step 6B.' };
	if (!ai.setupReference.folder_id) {
		throw { detail: 'A Folder ID is required before the deterministic Step 6B write.' };
	}
	if (!selectedRemediationActions().length) {
		throw { detail: 'Select at least one remediation action to commit.' };
	}
	if (!dryRun && !remediationDryRunSucceeded()) {
		throw { detail: 'Run a successful Step 6B dry-run before the approved commit.' };
	}
	if (!dryRun && !ai.remediationCommitApproved) {
		throw { detail: 'Approve the deterministic Step 6B write first.' };
	}

	return {
		dry_run: dryRun,
		approved: dryRun ? false : ai.remediationCommitApproved,
		folder_reference: ai.setupReference.folder_id,
		decisions: selectedRemediationActions().map((action: any) => ({
			temporary_id: action.temporary_id,
			selected: true,
			decision: 'create',
			existing_record_reference: '',
			payload: {
				temporary_id: action.temporary_id,
				title: action.title,
				description: action.description ?? '',
				linked_finding_reference: action.linked_finding_reference ?? '',
				linked_finding_title: action.linked_finding_title ?? '',
				linked_asset_reference: action.linked_asset_reference ?? '',
				linked_asset_title: action.linked_asset_title ?? '',
				linked_control_reference: action.linked_control_reference ?? '',
				linked_control_title: action.linked_control_title ?? '',
				priority: action.priority,
				suggested_owner: action.suggested_owner ?? '',
				target_timeline: action.target_timeline ?? '',
				success_criteria: action.success_criteria ?? [],
				required_follow_up_evidence: action.required_follow_up_evidence ?? [],
				rationale: action.rationale ?? '',
				confidence: action.confidence,
				review_status: action.review_status
			}
		}))
	};
}

export async function runRemediationActionCommit(dryRun: boolean) {
	ai.loading = dryRun ? 'remediation-commit-dry-run' : 'remediation-commit';
	ai.error = null;
	try {
		const result = await postAiAction(
			'aiRemediationActionCommit',
			buildRemediationActionCommitPayload(dryRun)
		);
		if (dryRun) {
			ai.remediationCommitDryRun = result;
			ai.remediationDryRunSelectionKey = selectionKey(selectedRemediationActions());
			ai.remediationCommitResult = null;
		} else {
			ai.remediationCommitResult = result;
		}
	} catch (caught) {
		ai.error = caught;
	} finally {
		ai.loading = null;
	}
}

// ---- Step 7A: advisory framework control mapping. No commit, no dry-run, no write. -------

/**
 * Best-effort framework label from the Step 1 case context. It only narrows the read-only
 * candidate lookup; a missing label never blocks Step 7A.
 */
function frameworkNameHint() {
	const entries = ai.caseContext?.regulatory_context;
	for (const entry of Array.isArray(entries) ? entries : []) {
		const label =
			typeof entry === 'string' ? entry : (entry?.value ?? entry?.label ?? entry?.name ?? '');
		if (typeof label === 'string' && label.trim()) return label.trim().slice(0, 200);
	}
	return '';
}

export function frameworkControlMappingProviderMode() {
	return ai.frameworkControlMappingDraft?.provider_mode ?? 'not run';
}

function buildFrameworkControlMappingSuggestionPayload() {
	const frameworkName = frameworkNameHint();
	const caseSummary = [ai.scenarioText, ai.scopeSummary]
		.map((value) => (typeof value === 'string' ? value.trim() : ''))
		.filter(Boolean)
		.join('\n\n');

	// Optional references are sent when available; missing ones never block the demo.
	// Framework controls are never invented here: the backend only maps to controls that were
	// supplied or safely discovered read-only from the referenced framework.
	return {
		case_summary: caseSummary.slice(0, 20000),
		scenario_name: (ai.scopeSummary || ai.scenarioText || '').trim().slice(0, 500),
		folder_reference: {
			folder_id: ai.setupReference.folder_id || null,
			folder_name: null
		},
		framework_name: frameworkName || null,
		framework_reference: {
			framework_id: ai.setupReference.selected_framework_id || null,
			framework_urn: null,
			framework_name: frameworkName || null
		},
		assets: approvedAssetReferences()
			.map((asset: any) => toContextItem(asset.ref_id ?? asset.asset_id, asset.name))
			.filter(Boolean),
		applied_controls: buildApprovedAppliedControlReferences()
			.map((control: any) =>
				toContextItem(control.ref_id ?? control.applied_control_id, control.name)
			)
			.filter(Boolean),
		remediation_actions: buildRemediationContextItems(
			ai.remediationActionDraft?.remediation_actions ?? [],
			(item, index) => item?.title || `Remediation action ${index + 1}`
		),
		evidence_requests: buildRemediationContextItems(
			ai.evidenceFindingDraft?.evidence_requests ?? [],
			(item, index) => displayEvidenceTitle(item, index)
		),
		audit_questions: buildRemediationContextItems(
			ai.evidenceFindingDraft?.audit_questions ?? [],
			(item, index) => displayAuditQuestionTitle(item, index)
		),
		preliminary_findings: buildRemediationContextItems(
			ai.evidenceFindingDraft?.preliminary_findings ?? [],
			(item, index) => displayFindingTitle(item, index)
		),
		known_weaknesses: knownWeaknessList(),
		candidate_framework_controls: [],
		user_locale: 'en',
		strict_mode: true
	};
}

export async function runFrameworkControlMappingSuggestion() {
	ai.loading = 'framework-mapping-suggest';
	ai.error = null;
	try {
		const draft = await postAiAction(
			'aiFrameworkControlMappingSuggest',
			buildFrameworkControlMappingSuggestionPayload()
		);
		ai.frameworkControlMappingDraft = draft;
		// Hand the Step 7A suggestions to the Step 7B review state. Nothing is written.
		ai.selectedFrameworkMappingIds = Object.fromEntries(
			(draft?.framework_control_mappings ?? []).map((mapping: any) => [mapping.temporary_id, false])
		);
		ai.frameworkMappingCommitApproved = false;
		ai.frameworkMappingCommitDryRun = null;
		ai.frameworkMappingCommitResult = null;
	} catch (caught) {
		ai.error = caught;
	} finally {
		ai.loading = null;
	}
}

// ---- Step 7B: deterministic commit. No AI model is called in this step. ------------------

export function selectedFrameworkMappings() {
	return (ai.frameworkControlMappingDraft?.framework_control_mappings ?? []).filter(
		(mapping: any) => ai.selectedFrameworkMappingIds[mapping.temporary_id]
	);
}

export function frameworkMappingDryRunSucceeded() {
	return (
		Boolean(ai.frameworkMappingCommitDryRun) &&
		ai.frameworkMappingDryRunSelectionKey === selectionKey(selectedFrameworkMappings()) &&
		!(ai.frameworkMappingCommitDryRun?.blocking_errors ?? []).length &&
		ai.frameworkMappingCommitDryRun?.commit_status !== 'blocked'
	);
}

/**
 * Step 7A falls back to the read-only framework export file when the referenced framework has no
 * assessable requirement nodes in the database. Those controls exist in the export but not as
 * platform records, and Step 7B never creates framework controls, so the commit will block.
 * Surfacing it here explains the block before the dry-run rather than after.
 */
export function frameworkMappingUsedCsvFallback() {
	return (ai.frameworkControlMappingDraft?.warnings ?? []).some(
		(warning: any) => warning?.code === 'framework_controls_loaded_from_csv_export'
	);
}

function buildFrameworkControlMappingCommitPayload(dryRun: boolean) {
	if (!ai.frameworkControlMappingDraft) throw { detail: 'Run Step 7A before Step 7B.' };
	if (!ai.setupReference.folder_id) {
		throw { detail: 'A Folder ID is required before the deterministic Step 7B write.' };
	}
	if (!ai.setupReference.compliance_assessment_id) {
		throw {
			detail: 'A Compliance Assessment ID is required before the deterministic Step 7B write.'
		};
	}
	if (!selectedFrameworkMappings().length) {
		throw { detail: 'Select at least one framework control mapping to commit.' };
	}
	if (!dryRun && !frameworkMappingDryRunSucceeded()) {
		throw { detail: 'Run a successful Step 7B dry-run before the approved commit.' };
	}
	if (!dryRun && !ai.frameworkMappingCommitApproved) {
		throw { detail: 'Approve the deterministic Step 7B write first.' };
	}

	return {
		dry_run: dryRun,
		approved: dryRun ? false : ai.frameworkMappingCommitApproved,
		folder_reference: ai.setupReference.folder_id,
		assessment_reference: ai.setupReference.compliance_assessment_id,
		framework_reference: ai.setupReference.selected_framework_id || '',
		decisions: selectedFrameworkMappings().map((mapping: any) => ({
			temporary_id: mapping.temporary_id,
			selected: true,
			decision: 'create',
			existing_record_reference: '',
			payload: {
				temporary_id: mapping.temporary_id,
				framework_control_reference: mapping.framework_control_reference,
				framework_control_code: mapping.framework_control_code ?? '',
				framework_control_title: mapping.framework_control_title ?? '',
				framework_control_description: mapping.framework_control_description ?? '',
				framework_name: mapping.framework_name ?? '',
				mapping_type: mapping.mapping_type,
				linked_finding_reference: mapping.linked_finding_reference ?? '',
				linked_finding_title: mapping.linked_finding_title ?? '',
				linked_applied_control_reference: mapping.linked_applied_control_reference ?? '',
				linked_applied_control_title: mapping.linked_applied_control_title ?? '',
				linked_remediation_action_reference: mapping.linked_remediation_action_reference ?? '',
				linked_remediation_action_title: mapping.linked_remediation_action_title ?? '',
				rationale: mapping.rationale ?? '',
				evidence_needed: mapping.evidence_needed ?? [],
				confidence: mapping.confidence,
				review_status: mapping.review_status
			}
		}))
	};
}

export async function runFrameworkControlMappingCommit(dryRun: boolean) {
	ai.loading = dryRun ? 'framework-mapping-commit-dry-run' : 'framework-mapping-commit';
	ai.error = null;
	try {
		const result = await postAiAction(
			'aiFrameworkControlMappingCommit',
			buildFrameworkControlMappingCommitPayload(dryRun)
		);
		if (dryRun) {
			ai.frameworkMappingCommitDryRun = result;
			ai.frameworkMappingDryRunSelectionKey = selectionKey(selectedFrameworkMappings());
			ai.frameworkMappingCommitResult = null;
		} else {
			ai.frameworkMappingCommitResult = result;
		}
	} catch (caught) {
		ai.error = caught;
	} finally {
		ai.loading = null;
	}
}

// ---- Shared onboarding context helpers for Steps 8A-12A ----------------------------------

function caseSummaryText() {
	return [ai.scenarioText, ai.scopeSummary]
		.map((value) => (typeof value === 'string' ? value.trim() : ''))
		.filter(Boolean)
		.join('\n\n')
		.slice(0, 20000);
}

function scenarioLabel() {
	return (ai.scopeSummary || ai.scenarioText || '').trim().slice(0, 500);
}

function folderReferenceContext() {
	return { folder_id: ai.setupReference.folder_id || null, folder_name: null };
}

function assessmentReferenceContext() {
	return {
		assessment_id: ai.setupReference.compliance_assessment_id || null,
		assessment_name: null
	};
}

function approvedAssetContextItems() {
	return approvedAssetReferences()
		.map((asset: any) => toContextItem(asset.ref_id ?? asset.asset_id, asset.name))
		.filter(Boolean);
}

function approvedControlContextItems() {
	return buildApprovedAppliedControlReferences()
		.map((control: any) =>
			toContextItem(control.ref_id ?? control.applied_control_id, control.name)
		)
		.filter(Boolean);
}

function evidenceRequestContextItems() {
	return buildRemediationContextItems(
		ai.evidenceFindingDraft?.evidence_requests ?? [],
		(item, index) => displayEvidenceTitle(item, index)
	);
}

function auditQuestionContextItems() {
	return buildRemediationContextItems(
		ai.evidenceFindingDraft?.audit_questions ?? [],
		(item, index) => displayAuditQuestionTitle(item, index)
	);
}

function findingContextItems() {
	return buildRemediationContextItems(
		ai.evidenceFindingDraft?.preliminary_findings ?? [],
		(item, index) => displayFindingTitle(item, index)
	);
}

function remediationActionContextItems() {
	return buildRemediationContextItems(
		ai.remediationActionDraft?.remediation_actions ?? [],
		(item, index) => item?.title || `Remediation action ${index + 1}`
	);
}

/**
 * Framework mappings are carried over exactly as Step 7A resolved them, so later steps can only
 * ever reference framework controls that already exist.
 */
function frameworkMappingContextItems() {
	return (ai.frameworkControlMappingDraft?.framework_control_mappings ?? [])
		.map((mapping: any) => {
			const title = (mapping?.framework_control_title ?? '').trim();
			if (!title) return null;
			return {
				reference: mapping.framework_control_reference || null,
				code: mapping.framework_control_code || null,
				title: title.slice(0, 500),
				description: (mapping.framework_control_description || '').slice(0, 5000) || null
			};
		})
		.filter(Boolean);
}

function riskScenarioContextItems() {
	return (ai.riskScenarioDraft?.risk_scenarios ?? [])
		.map((scenario: any) =>
			toContextItem(scenario?.temporary_id, scenario?.title, scenario?.description)
		)
		.filter(Boolean);
}

function controlEffectivenessContextItems() {
	return (ai.controlEffectivenessDraft?.control_effectiveness_suggestions ?? [])
		.map((suggestion: any) => {
			const title = (suggestion?.framework_control_title ?? '').trim();
			if (!title) return null;
			return {
				reference: suggestion.temporary_id || null,
				title: title.slice(0, 500),
				description: (suggestion.rationale || '').slice(0, 5000) || null,
				status: suggestion.suggested_compliance_status || null
			};
		})
		.filter(Boolean);
}

// ---- Step 8A: advisory risk scenario suggestion. No commit, no dry-run, no write. --------

export function riskScenarioProviderMode() {
	return ai.riskScenarioDraft?.provider_mode ?? 'not run';
}

function buildRiskScenarioSuggestionPayload() {
	const findings = findingContextItems();
	const weaknesses = knownWeaknessList();
	const assets = approvedAssetContextItems();
	if (!findings.length && !weaknesses.length && !assets.length) {
		throw {
			detail:
				'Step 8A needs at least one approved asset, one Step 5A preliminary finding, or one known weakness.'
		};
	}

	// Optional references are sent when available; missing ones never block the request.
	return {
		case_summary: caseSummaryText(),
		scenario_name: scenarioLabel(),
		folder_reference: folderReferenceContext(),
		assessment_reference: assessmentReferenceContext(),
		assets,
		applied_controls: approvedControlContextItems(),
		evidence_requests: evidenceRequestContextItems(),
		audit_questions: auditQuestionContextItems(),
		preliminary_findings: findings,
		remediation_actions: remediationActionContextItems(),
		framework_mappings: frameworkMappingContextItems(),
		known_weaknesses: weaknesses,
		user_locale: 'en',
		strict_mode: true
	};
}

export async function runRiskScenarioSuggestion() {
	ai.loading = 'risk-scenario-suggest';
	ai.error = null;
	try {
		const draft = await postAiAction('aiRiskScenarioSuggest', buildRiskScenarioSuggestionPayload());
		ai.riskScenarioDraft = draft;
		// Hand the Step 8A suggestions to the Step 8B review state. Nothing is written.
		ai.selectedRiskScenarioIds = Object.fromEntries(
			(draft?.risk_scenarios ?? []).map((scenario: any) => [scenario.temporary_id, false])
		);
		ai.riskScenarioCommitApproved = false;
		ai.riskScenarioCommitDryRun = null;
		ai.riskScenarioCommitResult = null;
	} catch (caught) {
		ai.error = caught;
	} finally {
		ai.loading = null;
	}
}

// ---- Step 8B: deterministic commit. No AI model is called in this step. ------------------

export function selectedRiskScenarios() {
	return (ai.riskScenarioDraft?.risk_scenarios ?? []).filter(
		(scenario: any) => ai.selectedRiskScenarioIds[scenario.temporary_id]
	);
}

export function riskScenarioDryRunSucceeded() {
	return (
		Boolean(ai.riskScenarioCommitDryRun) &&
		ai.riskScenarioDryRunSelectionKey === selectionKey(selectedRiskScenarios()) &&
		!(ai.riskScenarioCommitDryRun?.blocking_errors ?? []).length &&
		ai.riskScenarioCommitDryRun?.commit_status !== 'blocked'
	);
}

function buildRiskScenarioCommitPayload(dryRun: boolean) {
	if (!ai.riskScenarioDraft) throw { detail: 'Run Step 8A before Step 8B.' };
	if (!ai.setupReference.folder_id) {
		throw { detail: 'A Folder ID is required before the deterministic Step 8B write.' };
	}
	if (!ai.setupReference.risk_assessment_id) {
		throw {
			detail:
				'A Risk Assessment ID is required before the deterministic Step 8B write. Step 8B never creates a risk assessment.'
		};
	}
	if (!selectedRiskScenarios().length) {
		throw { detail: 'Select at least one risk scenario to commit.' };
	}
	if (!dryRun && !riskScenarioDryRunSucceeded()) {
		throw { detail: 'Run a successful Step 8B dry-run before the approved commit.' };
	}
	if (!dryRun && !ai.riskScenarioCommitApproved) {
		throw { detail: 'Approve the deterministic Step 8B write first.' };
	}

	return {
		dry_run: dryRun,
		approved: dryRun ? false : ai.riskScenarioCommitApproved,
		folder_reference: ai.setupReference.folder_id,
		assessment_reference: ai.setupReference.risk_assessment_id,
		decisions: selectedRiskScenarios().map((scenario: any) => ({
			temporary_id: scenario.temporary_id,
			selected: true,
			decision: 'create',
			existing_record_reference: '',
			payload: {
				temporary_id: scenario.temporary_id,
				title: scenario.title,
				description: scenario.description ?? '',
				asset_reference: scenario.asset_reference ?? '',
				asset_title: scenario.asset_title ?? '',
				linked_finding_reference: scenario.linked_finding_reference ?? '',
				linked_finding_title: scenario.linked_finding_title ?? '',
				linked_applied_control_reference: scenario.linked_applied_control_reference ?? '',
				linked_applied_control_title: scenario.linked_applied_control_title ?? '',
				linked_remediation_action_reference: scenario.linked_remediation_action_reference ?? '',
				linked_remediation_action_title: scenario.linked_remediation_action_title ?? '',
				linked_framework_control_reference: scenario.linked_framework_control_reference ?? '',
				linked_framework_control_code: scenario.linked_framework_control_code ?? '',
				linked_framework_control_title: scenario.linked_framework_control_title ?? '',
				threat: scenario.threat ?? '',
				vulnerability: scenario.vulnerability ?? '',
				impact_description: scenario.impact_description ?? '',
				likelihood: scenario.likelihood,
				impact: scenario.impact,
				risk_level: scenario.risk_level,
				rationale: scenario.rationale ?? '',
				recommended_next_steps: scenario.recommended_next_steps ?? [],
				confidence: scenario.confidence,
				review_status: scenario.review_status
			}
		}))
	};
}

export async function runRiskScenarioCommit(dryRun: boolean) {
	ai.loading = dryRun ? 'risk-scenario-commit-dry-run' : 'risk-scenario-commit';
	ai.error = null;
	try {
		const result = await postAiAction(
			'aiRiskScenarioCommit',
			buildRiskScenarioCommitPayload(dryRun)
		);
		if (dryRun) {
			ai.riskScenarioCommitDryRun = result;
			ai.riskScenarioDryRunSelectionKey = selectionKey(selectedRiskScenarios());
			ai.riskScenarioCommitResult = null;
		} else {
			ai.riskScenarioCommitResult = result;
		}
	} catch (caught) {
		ai.error = caught;
	} finally {
		ai.loading = null;
	}
}

// ---- Step 9A: advisory control effectiveness suggestion. No write. -----------------------

export function controlEffectivenessProviderMode() {
	return ai.controlEffectivenessDraft?.provider_mode ?? 'not run';
}

/**
 * Requirement assessments that Step 7B actually paired with the audit. They are the existing
 * rows Step 9B may later update; Step 9A never invents one.
 */
function requirementAssessmentContextItems() {
	return [
		...(ai.frameworkMappingCommitResult?.created_records ?? []),
		...(ai.frameworkMappingCommitResult?.reused_records ?? [])
	]
		.filter((record: any) => record?.record_id && record?.name)
		.map((record: any) => ({
			reference: record.record_id,
			framework_control_title: String(record.name).slice(0, 500)
		}));
}

function buildControlEffectivenessSuggestionPayload() {
	const frameworkMappings = frameworkMappingContextItems();
	const requirementAssessments = requirementAssessmentContextItems();
	if (!frameworkMappings.length && !requirementAssessments.length) {
		throw {
			detail:
				'Step 9A needs at least one Step 7A framework control mapping or one committed requirement assessment.'
		};
	}

	return {
		case_summary: caseSummaryText(),
		scenario_name: scenarioLabel(),
		folder_reference: folderReferenceContext(),
		assessment_reference: assessmentReferenceContext(),
		framework_mappings: frameworkMappings,
		requirement_assessments: requirementAssessments,
		applied_controls: approvedControlContextItems(),
		evidence_requests: evidenceRequestContextItems(),
		audit_questions: auditQuestionContextItems(),
		preliminary_findings: findingContextItems(),
		remediation_actions: remediationActionContextItems(),
		risk_scenarios: riskScenarioContextItems(),
		known_weaknesses: knownWeaknessList(),
		user_locale: 'en',
		strict_mode: true
	};
}

export async function runControlEffectivenessSuggestion() {
	ai.loading = 'control-effectiveness-suggest';
	ai.error = null;
	try {
		const draft = await postAiAction(
			'aiControlEffectivenessSuggest',
			buildControlEffectivenessSuggestionPayload()
		);
		ai.controlEffectivenessDraft = draft;
		ai.selectedControlEffectivenessIds = Object.fromEntries(
			(draft?.control_effectiveness_suggestions ?? []).map((suggestion: any) => [
				suggestion.temporary_id,
				false
			])
		);
		ai.controlEffectivenessCommitApproved = false;
		ai.controlEffectivenessCommitDryRun = null;
		ai.controlEffectivenessCommitResult = null;
	} catch (caught) {
		ai.error = caught;
	} finally {
		ai.loading = null;
	}
}

// ---- Step 9B: deterministic commit. No AI model is called in this step. ------------------

export function selectedControlEffectiveness() {
	return (ai.controlEffectivenessDraft?.control_effectiveness_suggestions ?? []).filter(
		(suggestion: any) => ai.selectedControlEffectivenessIds[suggestion.temporary_id]
	);
}

export function controlEffectivenessDryRunSucceeded() {
	return (
		Boolean(ai.controlEffectivenessCommitDryRun) &&
		ai.controlEffectivenessDryRunSelectionKey === selectionKey(selectedControlEffectiveness()) &&
		!(ai.controlEffectivenessCommitDryRun?.blocking_errors ?? []).length &&
		ai.controlEffectivenessCommitDryRun?.commit_status !== 'blocked'
	);
}

function buildControlEffectivenessCommitPayload(dryRun: boolean) {
	if (!ai.controlEffectivenessDraft) throw { detail: 'Run Step 9A before Step 9B.' };
	if (!ai.setupReference.folder_id) {
		throw { detail: 'A Folder ID is required before the deterministic Step 9B write.' };
	}
	if (!ai.setupReference.compliance_assessment_id) {
		throw {
			detail: 'A Compliance Assessment ID is required before the deterministic Step 9B write.'
		};
	}
	if (!selectedControlEffectiveness().length) {
		throw { detail: 'Select at least one control effectiveness judgement to commit.' };
	}
	if (!dryRun && !controlEffectivenessDryRunSucceeded()) {
		throw { detail: 'Run a successful Step 9B dry-run before the approved commit.' };
	}
	if (!dryRun && !ai.controlEffectivenessCommitApproved) {
		throw { detail: 'Approve the deterministic Step 9B write first.' };
	}

	return {
		dry_run: dryRun,
		approved: dryRun ? false : ai.controlEffectivenessCommitApproved,
		folder_reference: ai.setupReference.folder_id,
		assessment_reference: ai.setupReference.compliance_assessment_id,
		decisions: selectedControlEffectiveness().map((suggestion: any) => ({
			temporary_id: suggestion.temporary_id,
			selected: true,
			decision: 'create',
			existing_record_reference: '',
			payload: {
				temporary_id: suggestion.temporary_id,
				framework_control_reference: suggestion.framework_control_reference,
				framework_control_code: suggestion.framework_control_code ?? '',
				framework_control_title: suggestion.framework_control_title ?? '',
				linked_requirement_assessment_reference:
					suggestion.linked_requirement_assessment_reference ?? '',
				linked_applied_control_reference: suggestion.linked_applied_control_reference ?? '',
				linked_applied_control_title: suggestion.linked_applied_control_title ?? '',
				linked_finding_reference: suggestion.linked_finding_reference ?? '',
				linked_finding_title: suggestion.linked_finding_title ?? '',
				suggested_effectiveness: suggestion.suggested_effectiveness,
				suggested_compliance_status: suggestion.suggested_compliance_status,
				evidence_summary: suggestion.evidence_summary ?? '',
				gaps: suggestion.gaps ?? [],
				recommended_auditor_action: suggestion.recommended_auditor_action ?? '',
				rationale: suggestion.rationale ?? '',
				confidence: suggestion.confidence,
				review_status: suggestion.review_status
			}
		}))
	};
}

export async function runControlEffectivenessCommit(dryRun: boolean) {
	ai.loading = dryRun ? 'control-effectiveness-commit-dry-run' : 'control-effectiveness-commit';
	ai.error = null;
	try {
		const result = await postAiAction(
			'aiControlEffectivenessCommit',
			buildControlEffectivenessCommitPayload(dryRun)
		);
		if (dryRun) {
			ai.controlEffectivenessCommitDryRun = result;
			ai.controlEffectivenessDryRunSelectionKey = selectionKey(selectedControlEffectiveness());
			ai.controlEffectivenessCommitResult = null;
		} else {
			ai.controlEffectivenessCommitResult = result;
		}
	} catch (caught) {
		ai.error = caught;
	} finally {
		ai.loading = null;
	}
}

// ---- Step 10A: advisory audit readiness summary. No write. -------------------------------

export function auditReadinessProviderMode() {
	return ai.auditReadinessDraft?.provider_mode ?? 'not run';
}

function buildAuditReadinessSuggestionPayload() {
	return {
		case_summary: caseSummaryText(),
		scenario_name: scenarioLabel(),
		folder_reference: folderReferenceContext(),
		assessment_reference: assessmentReferenceContext(),
		assets: approvedAssetContextItems(),
		applied_controls: approvedControlContextItems(),
		evidence_requests: evidenceRequestContextItems(),
		audit_questions: auditQuestionContextItems(),
		preliminary_findings: findingContextItems(),
		remediation_actions: remediationActionContextItems(),
		framework_mappings: frameworkMappingContextItems().map((mapping: any) => ({
			reference: mapping.reference,
			title: mapping.title,
			description: mapping.description
		})),
		risk_scenarios: riskScenarioContextItems(),
		control_effectiveness_suggestions: controlEffectivenessContextItems(),
		known_weaknesses: knownWeaknessList(),
		user_locale: 'en',
		strict_mode: true
	};
}

export async function runAuditReadinessSuggestion() {
	ai.loading = 'audit-readiness-suggest';
	ai.error = null;
	try {
		const draft = await postAiAction(
			'aiAuditReadinessSuggest',
			buildAuditReadinessSuggestionPayload()
		);
		ai.auditReadinessDraft = draft;
		ai.auditReadinessSelected = false;
		ai.auditReadinessCommitApproved = false;
		ai.auditReadinessCommitDryRun = null;
		ai.auditReadinessCommitResult = null;
	} catch (caught) {
		ai.error = caught;
	} finally {
		ai.loading = null;
	}
}

// ---- Step 10B: deterministic commit. No AI model is called in this step. -----------------

export function auditReadinessDryRunSucceeded() {
	return (
		Boolean(ai.auditReadinessCommitDryRun) &&
		!(ai.auditReadinessCommitDryRun?.blocking_errors ?? []).length &&
		ai.auditReadinessCommitDryRun?.commit_status !== 'blocked'
	);
}

function buildAuditReadinessCommitPayload(dryRun: boolean) {
	if (!ai.auditReadinessDraft) throw { detail: 'Run Step 10A before Step 10B.' };
	if (!ai.setupReference.folder_id) {
		throw { detail: 'A Folder ID is required before the deterministic Step 10B write.' };
	}
	if (!ai.setupReference.compliance_assessment_id) {
		throw {
			detail: 'A Compliance Assessment ID is required before the deterministic Step 10B write.'
		};
	}
	if (!ai.auditReadinessSelected) {
		throw { detail: 'Select the readiness summary to record before committing.' };
	}
	if (!dryRun && !auditReadinessDryRunSucceeded()) {
		throw { detail: 'Run a successful Step 10B dry-run before the approved commit.' };
	}
	if (!dryRun && !ai.auditReadinessCommitApproved) {
		throw { detail: 'Approve the deterministic Step 10B write first.' };
	}

	return {
		dry_run: dryRun,
		approved: dryRun ? false : ai.auditReadinessCommitApproved,
		folder_reference: ai.setupReference.folder_id,
		assessment_reference: ai.setupReference.compliance_assessment_id,
		decisions: [
			{
				temporary_id: 'audit_readiness_1',
				selected: true,
				decision: 'create',
				existing_record_reference: '',
				payload: {
					temporary_id: 'audit_readiness_1',
					readiness_status: ai.auditReadinessDraft.readiness_status,
					readiness_score: ai.auditReadinessDraft.readiness_score,
					summary: ai.auditReadinessDraft.summary ?? '',
					ready_items: ai.auditReadinessDraft.ready_items ?? [],
					missing_evidence: ai.auditReadinessDraft.missing_evidence ?? [],
					open_findings: ai.auditReadinessDraft.open_findings ?? [],
					open_risks: ai.auditReadinessDraft.open_risks ?? [],
					blocked_controls: ai.auditReadinessDraft.blocked_controls ?? [],
					recommended_next_steps: ai.auditReadinessDraft.recommended_next_steps ?? [],
					priority_actions: ai.auditReadinessDraft.priority_actions ?? [],
					confidence: ai.auditReadinessDraft.overall_confidence,
					review_status: ai.auditReadinessDraft.review_status
				}
			}
		]
	};
}

export async function runAuditReadinessCommit(dryRun: boolean) {
	ai.loading = dryRun ? 'audit-readiness-commit-dry-run' : 'audit-readiness-commit';
	ai.error = null;
	try {
		const result = await postAiAction(
			'aiAuditReadinessCommit',
			buildAuditReadinessCommitPayload(dryRun)
		);
		if (dryRun) {
			ai.auditReadinessCommitDryRun = result;
			ai.auditReadinessCommitResult = null;
		} else {
			ai.auditReadinessCommitResult = result;
		}
	} catch (caught) {
		ai.error = caught;
	} finally {
		ai.loading = null;
	}
}

// ---- Step 11A: advisory report draft. No write. ------------------------------------------

export function auditReportProviderMode() {
	return ai.auditReportDraft?.provider_mode ?? 'not run';
}

function buildAuditReportSuggestionPayload() {
	return {
		case_summary: caseSummaryText(),
		scenario_name: scenarioLabel(),
		organization_name: (ai.caseContext?.organization ?? '') || null,
		framework_name: frameworkNameHint() || null,
		folder_reference: folderReferenceContext(),
		assessment_reference: assessmentReferenceContext(),
		assets: approvedAssetContextItems(),
		applied_controls: approvedControlContextItems(),
		evidence_requests: evidenceRequestContextItems(),
		audit_questions: auditQuestionContextItems(),
		preliminary_findings: findingContextItems(),
		remediation_actions: remediationActionContextItems(),
		framework_mappings: frameworkMappingContextItems().map((mapping: any) => ({
			reference: mapping.reference,
			title: mapping.title,
			description: mapping.description
		})),
		risk_scenarios: riskScenarioContextItems(),
		control_effectiveness_suggestions: controlEffectivenessContextItems(),
		evidence_gaps: ai.auditReadinessDraft?.missing_evidence ?? [],
		audit_readiness: ai.auditReadinessDraft
			? {
					readiness_status: ai.auditReadinessDraft.readiness_status,
					readiness_score: ai.auditReadinessDraft.readiness_score,
					summary: (ai.auditReadinessDraft.summary ?? '').slice(0, 5000)
				}
			: null,
		known_weaknesses: knownWeaknessList(),
		user_locale: 'en',
		strict_mode: true
	};
}

export async function runAuditReportSuggestion() {
	ai.loading = 'audit-report-suggest';
	ai.error = null;
	try {
		const draft = await postAiAction('aiAuditReportSuggest', buildAuditReportSuggestionPayload());
		ai.auditReportDraft = draft;
		ai.auditReportSelected = false;
		ai.auditReportCommitApproved = false;
		ai.auditReportCommitDryRun = null;
		ai.auditReportCommitResult = null;
	} catch (caught) {
		ai.error = caught;
	} finally {
		ai.loading = null;
	}
}

// ---- Step 11B: deterministic commit. No AI model is called in this step. -----------------

export function auditReportDryRunSucceeded() {
	return (
		Boolean(ai.auditReportCommitDryRun) &&
		!(ai.auditReportCommitDryRun?.blocking_errors ?? []).length &&
		ai.auditReportCommitDryRun?.commit_status !== 'blocked'
	);
}

function buildAuditReportCommitPayload(dryRun: boolean) {
	if (!ai.auditReportDraft) throw { detail: 'Run Step 11A before Step 11B.' };
	if (!ai.setupReference.folder_id) {
		throw { detail: 'A Folder ID is required before the deterministic Step 11B write.' };
	}
	if (!(ai.auditReportDraft.limitations ?? []).length) {
		throw { detail: 'The report draft must carry its limitations before it can be saved.' };
	}
	if (!ai.auditReportSelected) {
		throw { detail: 'Select the report draft to save before committing.' };
	}
	if (!dryRun && !auditReportDryRunSucceeded()) {
		throw { detail: 'Run a successful Step 11B dry-run before the approved commit.' };
	}
	if (!dryRun && !ai.auditReportCommitApproved) {
		throw { detail: 'Approve the deterministic Step 11B write first.' };
	}

	return {
		dry_run: dryRun,
		approved: dryRun ? false : ai.auditReportCommitApproved,
		folder_reference: ai.setupReference.folder_id,
		assessment_reference: ai.setupReference.compliance_assessment_id || '',
		decisions: [
			{
				temporary_id: 'audit_report_1',
				selected: true,
				decision: 'create',
				existing_record_reference: '',
				payload: {
					temporary_id: 'audit_report_1',
					report_title: ai.auditReportDraft.report_title,
					executive_summary: ai.auditReportDraft.executive_summary ?? '',
					report_sections: (ai.auditReportDraft.report_sections ?? []).map((section: any) => ({
						heading: section.heading,
						content: section.content ?? '',
						source_items: section.source_items ?? [],
						confidence: section.confidence
					})),
					limitations: ai.auditReportDraft.limitations ?? [],
					recommended_next_steps: ai.auditReportDraft.recommended_next_steps ?? [],
					confidence: ai.auditReportDraft.overall_confidence,
					review_status: ai.auditReportDraft.review_status
				}
			}
		]
	};
}

export async function runAuditReportCommit(dryRun: boolean) {
	ai.loading = dryRun ? 'audit-report-commit-dry-run' : 'audit-report-commit';
	ai.error = null;
	try {
		const result = await postAiAction('aiAuditReportCommit', buildAuditReportCommitPayload(dryRun));
		if (dryRun) {
			ai.auditReportCommitDryRun = result;
			ai.auditReportCommitResult = null;
		} else {
			ai.auditReportCommitResult = result;
		}
	} catch (caught) {
		ai.error = caught;
	} finally {
		ai.loading = null;
	}
}

// ---- Step 12A: advisory final review summary. No write. ----------------------------------

export function finalReviewProviderMode() {
	return ai.finalReviewDraft?.provider_mode ?? 'not run';
}

/**
 * Every commit step reports its own outcome; Step 12A only ever summarizes what those steps
 * actually returned.
 *
 * Steps 3B and 4B name their collections after the records they write (`created_assets`,
 * `created_applied_controls`); every later commit step uses `created_records`. Each step is
 * therefore read through its own keys, otherwise Step 12A reports the assets and applied
 * controls that were actually written as "0 created".
 */
function commitStepResults() {
	return [
		{
			step: '3B',
			result: ai.commitResult,
			recordType: 'Asset',
			createdKey: 'created_assets',
			reusedKey: 'reused_assets'
		},
		{
			step: '4B',
			result: ai.appliedControlCommitResult,
			recordType: 'AppliedControl',
			createdKey: 'created_applied_controls',
			reusedKey: 'reused_applied_controls'
		},
		{ step: '5B', result: ai.evidenceFindingCommitResult },
		{ step: '6B', result: ai.remediationCommitResult },
		{ step: '7B', result: ai.frameworkMappingCommitResult },
		{ step: '8B', result: ai.riskScenarioCommitResult },
		{ step: '9B', result: ai.controlEffectivenessCommitResult },
		{ step: '10B', result: ai.auditReadinessCommitResult },
		{ step: '11B', result: ai.auditReportCommitResult }
	]
		.filter((entry: any) => Boolean(entry.result))
		.map((entry: any) => ({
			recordType: null,
			createdKey: 'created_records',
			reusedKey: 'reused_records',
			...entry
		}));
}

function buildStepOutcomes() {
	return commitStepResults().map((entry: any) => {
		const blocking = entry.result.blocking_errors ?? [];
		const detail = blocking.length
			? String(blocking[0].detail ?? blocking[0].code ?? '').slice(0, 2000)
			: `${(entry.result[entry.createdKey] ?? []).length} created, ${
					(entry.result[entry.reusedKey] ?? []).length
				} reused.`;
		return {
			step: entry.step,
			status: String(entry.result.commit_status ?? entry.result.status ?? '').slice(0, 64),
			detail
		};
	});
}

function collectRecordSummaries(kind: 'created' | 'reused', action: string) {
	return commitStepResults()
		.flatMap((entry: any) =>
			(entry.result[kind === 'created' ? entry.createdKey : entry.reusedKey] ?? []).map(
				(record: any) => ({ record, recordType: entry.recordType })
			)
		)
		.filter(({ record }: any) => record?.name)
		.map(({ record, recordType }: any) => ({
			record_type: record.record_type ?? recordType ?? null,
			name: String(record.name).slice(0, 500),
			action
		}));
}

function collectBlockedItems() {
	return commitStepResults().flatMap((entry: any) =>
		(entry.result.blocking_errors ?? []).map((blockingError: any) =>
			`Step ${entry.step}: ${blockingError.detail ?? blockingError.code ?? 'blocked'}`.slice(0, 500)
		)
	);
}

function buildFinalReviewSuggestionPayload() {
	const stepOutcomes = buildStepOutcomes();
	const createdRecords = collectRecordSummaries('created', 'create');
	const reusedRecords = collectRecordSummaries('reused', 'reuse');
	const blockedItems = collectBlockedItems();
	const outstandingItems = ai.auditReadinessDraft?.missing_evidence ?? [];

	if (
		!stepOutcomes.length &&
		!createdRecords.length &&
		!reusedRecords.length &&
		!blockedItems.length &&
		!outstandingItems.length
	) {
		throw {
			detail: 'Step 12A needs at least one completed commit step before it can review the flow.'
		};
	}

	return {
		case_summary: caseSummaryText(),
		scenario_name: scenarioLabel(),
		folder_reference: folderReferenceContext(),
		assessment_reference: assessmentReferenceContext(),
		step_outcomes: stepOutcomes,
		created_records: createdRecords,
		reused_records: reusedRecords,
		blocked_items: blockedItems,
		outstanding_items: outstandingItems,
		user_locale: 'en',
		strict_mode: true
	};
}

export async function runFinalReviewSuggestion() {
	ai.loading = 'final-review-suggest';
	ai.error = null;
	try {
		const draft = await postAiAction('aiFinalReviewSuggest', buildFinalReviewSuggestionPayload());
		ai.finalReviewDraft = draft;
		ai.finalReviewSelected = false;
		ai.finalReviewCommitApproved = false;
		ai.finalReviewCommitDryRun = null;
		ai.finalReviewCommitResult = null;
	} catch (caught) {
		ai.error = caught;
	} finally {
		ai.loading = null;
	}
}

// ---- Step 12B: deterministic commit. No AI model is called in this step. -----------------

export function finalReviewDryRunSucceeded() {
	return (
		Boolean(ai.finalReviewCommitDryRun) &&
		!(ai.finalReviewCommitDryRun?.blocking_errors ?? []).length &&
		ai.finalReviewCommitDryRun?.commit_status !== 'blocked'
	);
}

function buildFinalReviewCommitPayload(dryRun: boolean) {
	if (!ai.finalReviewDraft) throw { detail: 'Run Step 12A before Step 12B.' };
	if (!ai.setupReference.folder_id) {
		throw { detail: 'A Folder ID is required before the deterministic Step 12B write.' };
	}
	if (!ai.setupReference.compliance_assessment_id) {
		throw {
			detail: 'A Compliance Assessment ID is required before the deterministic Step 12B write.'
		};
	}
	if (!ai.finalReviewSelected) {
		throw { detail: 'Select the case handoff summary to record before committing.' };
	}
	if (!dryRun && !finalReviewDryRunSucceeded()) {
		throw { detail: 'Run a successful Step 12B dry-run before the approved commit.' };
	}
	if (!dryRun && !ai.finalReviewCommitApproved) {
		throw { detail: 'Approve the deterministic Step 12B write first.' };
	}

	return {
		dry_run: dryRun,
		approved: dryRun ? false : ai.finalReviewCommitApproved,
		folder_reference: ai.setupReference.folder_id,
		assessment_reference: ai.setupReference.compliance_assessment_id,
		decisions: [
			{
				temporary_id: 'final_review_1',
				selected: true,
				decision: 'create',
				existing_record_reference: '',
				payload: {
					temporary_id: 'final_review_1',
					completion_summary: ai.finalReviewDraft.completion_summary ?? '',
					completed_steps: ai.finalReviewDraft.completed_steps ?? [],
					incomplete_steps: ai.finalReviewDraft.incomplete_steps ?? [],
					created_or_reused_records_summary:
						ai.finalReviewDraft.created_or_reused_records_summary ?? [],
					blocked_items: ai.finalReviewDraft.blocked_items ?? [],
					human_review_required: ai.finalReviewDraft.human_review_required ?? [],
					recommended_next_steps: ai.finalReviewDraft.recommended_next_steps ?? [],
					demo_readiness_status: ai.finalReviewDraft.demo_readiness_status,
					confidence: ai.finalReviewDraft.overall_confidence,
					review_status: ai.finalReviewDraft.review_status
				}
			}
		]
	};
}

export async function runFinalReviewCommit(dryRun: boolean) {
	ai.loading = dryRun ? 'final-review-commit-dry-run' : 'final-review-commit';
	ai.error = null;
	try {
		const result = await postAiAction('aiFinalReviewCommit', buildFinalReviewCommitPayload(dryRun));
		if (dryRun) {
			ai.finalReviewCommitDryRun = result;
			ai.finalReviewCommitResult = null;
		} else {
			ai.finalReviewCommitResult = result;
		}
	} catch (caught) {
		ai.error = caught;
	} finally {
		ai.loading = null;
	}
}

// ---- Display-only helpers. These never alter request payloads or backend data. -----------

export function linkedAssetNamesById(): Record<string, string> {
	return Object.fromEntries(
		approvedAssetReferences().map((asset: any) => [asset.asset_id, asset.name])
	);
}

export function linkedAssetLabel(assetId: string) {
	return linkedAssetNamesById()[assetId] ?? assetId;
}

export function linkedControlNamesById(): Record<string, string> {
	return Object.fromEntries(
		[
			...(ai.appliedControlCommitResult?.created_applied_controls ?? []),
			...(ai.appliedControlCommitResult?.reused_applied_controls ?? [])
		]
			.filter((control: any) => control?.applied_control_id)
			.map((control: any) => [control.applied_control_id, control.name])
	);
}

export function linkedControlLabel(controlId: string) {
	return linkedControlNamesById()[controlId] ?? controlId;
}

export function formatConfidence(value: any) {
	if (typeof value !== 'number' || Number.isNaN(value)) return 'n/a';
	return `${Math.round(value * 100)}%`;
}

export function humanizeProviderMode(mode: any) {
	if (mode === 'configured_local_provider') return 'Local AI provider';
	if (mode === 'not run') return 'Not run yet';
	if (typeof mode === 'string' && mode.trim()) return mode.replaceAll('_', ' ');
	return 'Unknown';
}

export function humanizeActionName(action: any) {
	const knownActions: Record<string, string> = {
		create: 'Create new record',
		reuse: 'Reuse existing record',
		reject: 'Reject',
		defer: 'Defer',
		skip: 'Skip',
		skipped: 'Skipped',
		created: 'Created',
		reused: 'Reused existing record',
		planned: 'Planned',
		review_reuse_before_create: 'Existing record found; review before creating another one',
		review_reuse_or_rename: 'Existing record found; review before creating another one'
	};
	if (typeof action !== 'string' || !action.trim()) return 'n/a';
	return knownActions[action] ?? action.replaceAll('_', ' ');
}

export function humanizeFieldLabel(value: any) {
	if (typeof value !== 'string' || !value.trim()) return 'n/a';
	return value.replaceAll('_', ' ');
}

function isGenericCandidateTitle(title: any) {
	if (typeof title !== 'string' || !title.trim()) return true;
	return /^(evidence\s*request|audit\s*question|preliminary\s*finding|finding|candidate|item|suggestion)\s*(candidate|item)?\s*#?\d*$/i.test(
		title.trim()
	);
}

function firstMeaningfulText(...values: any[]) {
	for (const value of values) {
		if (typeof value !== 'string' || !value.trim()) continue;
		const trimmed = value.trim();
		const sentenceMatch = trimmed.match(/^[^.?!\n]{3,}?[.?!]/);
		const sentence = (sentenceMatch ? sentenceMatch[0] : trimmed).trim();
		return sentence.length > 140 ? `${sentence.slice(0, 137)}...` : sentence;
	}
	return '';
}

export function displayEvidenceTitle(item: any, index: number) {
	if (!isGenericCandidateTitle(item?.title)) return item.title;
	if (!isGenericCandidateTitle(item?.name)) return item.name;
	return (
		firstMeaningfulText(
			item?.summary,
			item?.description,
			item?.request_text,
			item?.details,
			item?.rationale
		) || `Evidence request ${index + 1}`
	);
}

export function displayAuditQuestionTitle(item: any, index: number) {
	if (!isGenericCandidateTitle(item?.question_text)) return item.question_text;
	if (!isGenericCandidateTitle(item?.question)) return item.question;
	if (!isGenericCandidateTitle(item?.title)) return item.title;
	return firstMeaningfulText(item?.summary, item?.rationale) || `Audit question ${index + 1}`;
}

export function displayFindingTitle(item: any, index: number) {
	if (!isGenericCandidateTitle(item?.title)) return item.title;
	if (!isGenericCandidateTitle(item?.name)) return item.name;
	return (
		firstMeaningfulText(
			item?.finding_statement,
			item?.summary,
			item?.rationale,
			item?.description
		) || `Preliminary finding ${index + 1}`
	);
}

export function remediationPriorityBadgeClass(priority: any) {
	if (priority === 'critical') return 'bg-red-100 text-red-900';
	if (priority === 'high') return 'bg-orange-100 text-orange-900';
	if (priority === 'medium') return 'bg-yellow-100 text-yellow-900';
	if (priority === 'low') return 'bg-slate-100 text-slate-700';
	return 'bg-slate-100 text-slate-700';
}
