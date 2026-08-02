import { describe, expect, it } from 'vitest';
import {
	buildReviewedAppliedControlDecisions,
	getAutoReuseAppliedControlMatch
} from './appliedControlCommitDecisions';

describe('appliedControlCommitDecisions', () => {
	it('defaults exact duplicate applied controls to reuse_existing', () => {
		const candidate = {
			temporary_id: 'CTL-CAND-001',
			proposed_name: 'Multi-Factor Authentication for Remote Access',
			proposed_description: 'Require MFA for remote access.',
			proposed_reference_id: 'CTL-MFA-001',
			proposed_control_type: 'safeguard',
			proposed_control_category: 'technical',
			proposed_status: 'to_do',
			proposed_implementation_state: 'planned',
			linked_asset_ids: ['asset-1', 'asset-2'],
			linked_asset_temporary_ids: ['asset-ref-1', 'asset-ref-2'],
			related_weaknesses: ['No MFA for remote access'],
			confidence: 0.94,
			ambiguity_flags: []
		};
		const duplicateCandidates = [
			{
				temporary_id: 'CTL-CAND-001',
				proposed_name: 'Multi-Factor Authentication for Remote Access',
				recommended_human_action: 'review_reuse_or_rename',
				matches: [
					{
						existing_applied_control_id: 'ctl-existing-1',
						existing_name: 'Multi-Factor Authentication for Remote Access',
						match_type: 'exact_name_same_folder',
						match_score: 0.99
					}
				]
			}
		];

		const autoReuseMatch = getAutoReuseAppliedControlMatch(candidate, duplicateCandidates);
		const [decision] = buildReviewedAppliedControlDecisions([candidate], duplicateCandidates);

		expect(autoReuseMatch?.existing_applied_control_id).toBe('ctl-existing-1');
		expect(decision).toEqual({
			temporary_id: 'CTL-CAND-001',
			selected: true,
			action: 'reuse',
			human_approved: true,
			selected_existing_applied_control_id: 'ctl-existing-1',
			approved_fields: null,
			original_suggestion_summary: {
				proposed_name: 'Multi-Factor Authentication for Remote Access',
				proposed_description: 'Require MFA for remote access.',
				proposed_reference_id: 'CTL-MFA-001',
				proposed_control_type: 'safeguard',
				proposed_control_category: 'technical',
				proposed_status: 'to_do',
				proposed_implementation_state: 'planned',
				linked_asset_ids: ['asset-1', 'asset-2'],
				linked_asset_temporary_ids: ['asset-ref-1', 'asset-ref-2'],
				related_weaknesses: ['No MFA for remote access'],
				confidence: 0.94,
				ambiguity_flags: []
			},
			reviewer_notes:
				'Reuse existing applied control Multi-Factor Authentication for Remote Access for duplicate candidate CTL-CAND-001.',
			ambiguity_resolution: null,
			duplicate_resolution: {
				decision: 'reuse_existing',
				reviewed_match_ids: ['ctl-existing-1'],
				resolution_note: 'Exact-name or reference-id duplicate matched during Step 4A review.'
			}
		});
	});

	it('keeps non-duplicate applied controls as create decisions', () => {
		const [decision] = buildReviewedAppliedControlDecisions([
			{
				temporary_id: 'CTL-CAND-002',
				proposed_name: 'Privileged Access Management',
				proposed_description: 'Deploy PAM for administrators.',
				proposed_reference_id: null,
				proposed_control_type: 'safeguard',
				proposed_control_category: 'technical',
				proposed_status: 'to_do',
				proposed_implementation_state: 'planned',
				linked_asset_ids: ['asset-3'],
				linked_asset_temporary_ids: ['asset-ref-3'],
				related_weaknesses: ['No PAM for privileged admin accounts'],
				confidence: 0.91,
				ambiguity_flags: []
			}
		]);

		expect(decision.action).toBe('create');
		expect(decision.selected_existing_applied_control_id).toBeNull();
		expect(decision.approved_fields).toEqual({
			name: 'Privileged Access Management',
			description: 'Deploy PAM for administrators.',
			ref_id: null,
			category: 'technical',
			status: 'to_do',
			linked_asset_ids: ['asset-3']
		});
		expect(decision.duplicate_resolution).toBeNull();
	});
});