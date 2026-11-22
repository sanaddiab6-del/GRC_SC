import { describe, expect, it } from 'vitest';
import { buildReviewedAssetDecisions, getAutoReuseMatch } from './assetCommitDecisions';

describe('assetCommitDecisions', () => {
	it('defaults exact same-folder duplicate candidates to reuse_existing', () => {
		const candidate = {
			temporary_id: 'AST-CAND-001',
			proposed_name: 'Core Banking Platform',
			proposed_description: 'Primary platform',
			proposed_reference_id: 'AST-CBP-001',
			proposed_asset_type: { value: 'PR', label: 'Primary' },
			confidence: 0.97,
			ambiguity_flags: []
		};
		const duplicateCandidates = [
			{
				temporary_id: 'AST-CAND-001',
				proposed_name: 'Core Banking Platform',
				recommended_human_action: 'review_reuse_before_create',
				matches: [
					{
						existing_asset_id: 'a40523bb-1fdc-41e3-89fc-7c41da82ac06',
						existing_name: 'Core Banking Platform',
						match_type: 'exact_name_same_folder',
						match_score: 0.99
					}
				]
			}
		];

		const autoReuseMatch = getAutoReuseMatch(candidate, duplicateCandidates);
		const [decision] = buildReviewedAssetDecisions([candidate], duplicateCandidates);

		expect(autoReuseMatch?.existing_asset_id).toBe('a40523bb-1fdc-41e3-89fc-7c41da82ac06');
		expect(decision).toEqual({
			temporary_id: 'AST-CAND-001',
			action: 'reuse',
			human_approved: true,
			selected_existing_asset_id: 'a40523bb-1fdc-41e3-89fc-7c41da82ac06',
			approved_fields: null,
			original_suggestion_summary: {
				proposed_name: 'Core Banking Platform',
				proposed_description: 'Primary platform',
				proposed_reference_id: 'AST-CBP-001',
				proposed_asset_type: { value: 'PR', label: 'Primary' },
				proposed_asset_category: null,
				confidence: 0.97,
				ambiguity_flags: []
			},
			reviewer_notes:
				'Reuse existing asset Core Banking Platform for duplicate candidate AST-CAND-001.',
			ambiguity_resolution: null,
			duplicate_resolution: {
				decision: 'reuse_existing',
				reviewed_match_ids: ['a40523bb-1fdc-41e3-89fc-7c41da82ac06'],
				resolution_note: 'Exact same-folder duplicate matched during Step 3A review.'
			}
		});
	});

	it('keeps non-duplicate candidates as create decisions', () => {
		const [decision] = buildReviewedAssetDecisions([
			{
				temporary_id: 'AST-CAND-002',
				proposed_name: 'Treasury Workstation',
				proposed_description: 'Support platform',
				proposed_reference_id: null,
				proposed_asset_type: { value: 'SP', label: 'Support' },
				confidence: 0.84,
				ambiguity_flags: []
			}
		]);

		expect(decision.action).toBe('create');
		expect(decision.selected_existing_asset_id).toBeNull();
		expect(decision.approved_fields).toEqual({
			name: 'Treasury Workstation',
			description: 'Support platform',
			type: 'SP',
			ref_id: null,
			observation: 'Created from Local AI asset suggestion AST-CAND-002.'
		});
		expect(decision.duplicate_resolution).toBeNull();
	});
});