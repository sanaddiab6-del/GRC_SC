import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
	ai,
	controlEffectivenessDryRunSucceeded,
	frameworkMappingDryRunSucceeded,
	hydrateAiOnboarding,
	remediationDryRunSucceeded,
	resetAiOnboardingWorkflow,
	riskScenarioDryRunSucceeded,
	runControlEffectivenessCommit,
	runFrameworkControlMappingCommit,
	runRemediationActionCommit,
	runRiskScenarioCommit
} from './aiOnboardingState.svelte';

/**
 * The onboarding steps now live on different pages and share this module instead of a single
 * component's local state. These tests cover the guarantees that move with them: an approved
 * commit is refused until a dry-run covering the current selection succeeded, and changing the
 * selection afterwards takes that dry-run's blessing away again.
 */

function jsonResponse(body: unknown, status = 200) {
	return new Response(JSON.stringify(body), {
		status,
		headers: { 'Content-Type': 'application/json' }
	});
}

/** A dry-run the backend accepted: no blocking errors and not blocked. */
const CLEAN_DRY_RUN = { commit_status: 'dry_run_ok', blocking_errors: [], planned_actions: [] };

function mockFetch(...responses: Response[]) {
	const fetchMock = vi.fn();
	for (const response of responses) fetchMock.mockResolvedValueOnce(response);
	vi.stubGlobal('fetch', fetchMock);
	return fetchMock;
}

function lastRequestBody(fetchMock: ReturnType<typeof vi.fn>) {
	return JSON.parse(fetchMock.mock.calls.at(-1)![1].body);
}

describe('AI onboarding shared workflow state', () => {
	beforeEach(() => {
		vi.unstubAllGlobals();
		resetAiOnboardingWorkflow();
		ai.setupReference.folder_id = 'folder-1';
		ai.setupReference.compliance_assessment_id = 'audit-1';
		ai.setupReference.risk_assessment_id = 'risk-assessment-1';
	});

	describe('Step 6B remediation action commit', () => {
		beforeEach(() => {
			ai.remediationActionDraft = {
				remediation_actions: [
					{ temporary_id: 'ra-1', title: 'Rotate keys', priority: 'high', confidence: 0.8 },
					{ temporary_id: 'ra-2', title: 'Patch host', priority: 'low', confidence: 0.5 }
				]
			};
			ai.selectedRemediationActionIds = { 'ra-1': true, 'ra-2': false };
			ai.remediationCommitApproved = true;
		});

		it('posts the dry-run to the shared onboarding proxy with approval withheld', async () => {
			const fetchMock = mockFetch(jsonResponse(CLEAN_DRY_RUN));

			await runRemediationActionCommit(true);

			expect(fetchMock).toHaveBeenCalledTimes(1);
			expect(fetchMock.mock.calls[0][0]).toBe('/fe-api/ai-onboarding/aiRemediationActionCommit');
			const body = lastRequestBody(fetchMock);
			expect(body.dry_run).toBe(true);
			// A dry-run never carries the approval, whatever the checkbox says.
			expect(body.approved).toBe(false);
			expect(body.decisions).toHaveLength(1);
			expect(ai.error).toBeNull();
			expect(remediationDryRunSucceeded()).toBe(true);
		});

		it('refuses the approved commit until a dry-run succeeded', async () => {
			const fetchMock = mockFetch();

			await runRemediationActionCommit(false);

			expect(fetchMock).not.toHaveBeenCalled();
			expect(ai.error.detail).toBe('Run a successful Step 6B dry-run before the approved commit.');
			expect(ai.remediationCommitResult).toBeNull();
		});

		it('invalidates a successful dry-run when the selection changes', async () => {
			mockFetch(jsonResponse(CLEAN_DRY_RUN));
			await runRemediationActionCommit(true);
			expect(remediationDryRunSucceeded()).toBe(true);

			ai.selectedRemediationActionIds['ra-2'] = true;

			expect(remediationDryRunSucceeded()).toBe(false);

			const fetchMock = mockFetch();
			await runRemediationActionCommit(false);
			expect(fetchMock).not.toHaveBeenCalled();
			expect(ai.error.detail).toBe('Run a successful Step 6B dry-run before the approved commit.');
		});

		it('does not treat a blocked dry-run as a successful one', async () => {
			mockFetch(
				jsonResponse({ commit_status: 'blocked', blocking_errors: [{ detail: 'no permission' }] })
			);
			await runRemediationActionCommit(true);

			expect(remediationDryRunSucceeded()).toBe(false);

			const fetchMock = mockFetch();
			await runRemediationActionCommit(false);
			expect(fetchMock).not.toHaveBeenCalled();
		});

		it('refuses the approved commit while the approval checkbox is unchecked', async () => {
			mockFetch(jsonResponse(CLEAN_DRY_RUN));
			await runRemediationActionCommit(true);
			ai.remediationCommitApproved = false;

			const fetchMock = mockFetch();
			await runRemediationActionCommit(false);

			expect(fetchMock).not.toHaveBeenCalled();
			expect(ai.error.detail).toBe('Approve the deterministic Step 6B write first.');
		});

		it('sends the approval only once every gate is satisfied', async () => {
			mockFetch(jsonResponse(CLEAN_DRY_RUN));
			await runRemediationActionCommit(true);

			const fetchMock = mockFetch(
				jsonResponse({ commit_status: 'committed', created_records: [{ name: 'Rotate keys' }] })
			);
			await runRemediationActionCommit(false);

			const body = lastRequestBody(fetchMock);
			expect(body.dry_run).toBe(false);
			expect(body.approved).toBe(true);
			expect(ai.remediationCommitResult.commit_status).toBe('committed');
			expect(ai.error).toBeNull();
		});

		it('blocks the write when the Step 2 folder reference is missing', async () => {
			ai.setupReference.folder_id = '';
			const fetchMock = mockFetch();

			await runRemediationActionCommit(true);

			expect(fetchMock).not.toHaveBeenCalled();
			expect(ai.error.detail).toBe(
				'A Folder ID is required before the deterministic Step 6B write.'
			);
		});
	});

	describe('Step 7B framework control mapping commit', () => {
		beforeEach(() => {
			ai.frameworkControlMappingDraft = {
				framework_control_mappings: [
					{ temporary_id: 'fm-1', framework_control_reference: 'A.5.1', mapping_type: 'direct' },
					{ temporary_id: 'fm-2', framework_control_reference: 'A.5.2', mapping_type: 'direct' }
				]
			};
			ai.selectedFrameworkMappingIds = { 'fm-1': true, 'fm-2': false };
			ai.frameworkMappingCommitApproved = true;
		});

		it('invalidates a successful dry-run when the selection changes', async () => {
			mockFetch(jsonResponse(CLEAN_DRY_RUN));
			await runFrameworkControlMappingCommit(true);
			expect(frameworkMappingDryRunSucceeded()).toBe(true);

			ai.selectedFrameworkMappingIds['fm-1'] = false;
			ai.selectedFrameworkMappingIds['fm-2'] = true;

			expect(frameworkMappingDryRunSucceeded()).toBe(false);
		});

		it('requires the audit reference before the deterministic write', async () => {
			ai.setupReference.compliance_assessment_id = '';
			const fetchMock = mockFetch();

			await runFrameworkControlMappingCommit(true);

			expect(fetchMock).not.toHaveBeenCalled();
			expect(ai.error.detail).toBe(
				'A Compliance Assessment ID is required before the deterministic Step 7B write.'
			);
		});
	});

	describe('Step 8B risk scenario commit', () => {
		beforeEach(() => {
			ai.riskScenarioDraft = {
				risk_scenarios: [
					{ temporary_id: 'rs-1', title: 'Credential theft' },
					{ temporary_id: 'rs-2', title: 'Data loss' }
				]
			};
			ai.selectedRiskScenarioIds = { 'rs-1': true, 'rs-2': false };
			ai.riskScenarioCommitApproved = true;
		});

		it('invalidates a successful dry-run when the selection changes', async () => {
			mockFetch(jsonResponse(CLEAN_DRY_RUN));
			await runRiskScenarioCommit(true);
			expect(riskScenarioDryRunSucceeded()).toBe(true);

			ai.selectedRiskScenarioIds['rs-2'] = true;

			expect(riskScenarioDryRunSucceeded()).toBe(false);
		});

		it('never creates the risk assessment it writes into', async () => {
			ai.setupReference.risk_assessment_id = '';
			const fetchMock = mockFetch();

			await runRiskScenarioCommit(true);

			expect(fetchMock).not.toHaveBeenCalled();
			expect(ai.error.detail).toContain('Step 8B never creates a risk assessment');
		});
	});

	describe('Step 9B control effectiveness commit', () => {
		beforeEach(() => {
			ai.controlEffectivenessDraft = {
				control_effectiveness_suggestions: [
					{ temporary_id: 'ce-1', framework_control_reference: 'A.5.1' },
					{ temporary_id: 'ce-2', framework_control_reference: 'A.5.2' }
				]
			};
			ai.selectedControlEffectivenessIds = { 'ce-1': true, 'ce-2': false };
			ai.controlEffectivenessCommitApproved = true;
		});

		it('invalidates a successful dry-run when the selection changes', async () => {
			mockFetch(jsonResponse(CLEAN_DRY_RUN));
			await runControlEffectivenessCommit(true);
			expect(controlEffectivenessDryRunSucceeded()).toBe(true);

			ai.selectedControlEffectivenessIds['ce-2'] = true;

			expect(controlEffectivenessDryRunSucceeded()).toBe(false);
		});
	});

	describe('progress carried between the step pages', () => {
		const SETUP_KEY = 'sanad_ai_onboarding_setup';
		const WORKFLOW_KEY = 'sanad_ai_onboarding_workflow';

		function hydrateFresh() {
			// `hydrate` runs once per page load; a test navigates by replaying that first read.
			ai.hydrated = false;
			hydrateAiOnboarding();
		}

		beforeEach(() => {
			localStorage.clear();
		});

		it('restores the Step 2 case reference for a page that has no case of its own', () => {
			localStorage.setItem(
				SETUP_KEY,
				JSON.stringify({
					created_at: '2026-08-10T09:00:00.000Z',
					source_step1_draft_hash: 'sha256:step1',
					scenario_summary: 'Cloud migration audit',
					case_context: { organization: 'Acme' },
					setupReference: {
						folder_id: 'folder-9',
						perimeter_id: 'perimeter-9',
						compliance_assessment_id: 'audit-9',
						risk_assessment_id: 'risk-9',
						selected_framework_id: 'framework-9'
					}
				})
			);

			hydrateFresh();

			expect(ai.sourceStep1DraftHash).toBe('sha256:step1');
			expect(ai.scenarioText).toBe('Cloud migration audit');
			expect(ai.setupReference.compliance_assessment_id).toBe('audit-9');
			expect(ai.caseContext).toEqual({ organization: 'Acme' });
		});

		it('carries a step handoff to the next step page', () => {
			localStorage.setItem(
				SETUP_KEY,
				JSON.stringify({ created_at: '2026-08-10T09:00:00.000Z', setupReference: {} })
			);
			localStorage.setItem(
				WORKFLOW_KEY,
				JSON.stringify({
					setup_created_at: '2026-08-10T09:00:00.000Z',
					assetCommitHash: 'sha256:assets',
					commitResult: { created_assets: [{ asset_id: 'a-1', name: 'Payroll DB' }] },
					appliedControlCommitHash: 'sha256:controls'
				})
			);

			hydrateFresh();

			// Step 4A on the Applied controls page needs exactly this handoff from Step 3B.
			expect(ai.assetCommitHash).toBe('sha256:assets');
			expect(ai.commitResult.created_assets[0].name).toBe('Payroll DB');
			expect(ai.appliedControlCommitHash).toBe('sha256:controls');
		});

		it('discards progress that belongs to a previous case', () => {
			localStorage.setItem(
				SETUP_KEY,
				JSON.stringify({ created_at: '2026-08-10T11:00:00.000Z', setupReference: {} })
			);
			localStorage.setItem(
				WORKFLOW_KEY,
				JSON.stringify({
					setup_created_at: '2026-08-10T09:00:00.000Z',
					assetCommitHash: 'sha256:previous-case',
					commitResult: { created_assets: [{ asset_id: 'old', name: 'Old asset' }] }
				})
			);

			hydrateFresh();

			expect(ai.assetCommitHash).toBe('');
			expect(ai.commitResult).toBeNull();
			expect(localStorage.getItem(WORKFLOW_KEY)).toBeNull();
		});

		it('never restores an in-flight request or a stale error', () => {
			localStorage.setItem(
				WORKFLOW_KEY,
				JSON.stringify({ setup_created_at: '', loading: 'commit', error: { detail: 'old' } })
			);

			hydrateFresh();

			expect(ai.loading).toBeNull();
			expect(ai.error).toBeNull();
		});
	});

	describe('backend refusals', () => {
		it('surfaces the backend detail instead of a raw response string', async () => {
			ai.remediationActionDraft = {
				remediation_actions: [{ temporary_id: 'ra-1', title: 'Rotate keys' }]
			};
			ai.selectedRemediationActionIds = { 'ra-1': true };
			mockFetch(
				jsonResponse({ detail: 'You do not have permission to perform this action.' }, 403)
			);

			await runRemediationActionCommit(true);

			expect(ai.error).toEqual({ detail: 'You do not have permission to perform this action.' });
			expect(ai.remediationCommitDryRun).toBeNull();
		});
	});
});
