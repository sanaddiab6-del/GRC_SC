type AmbiguityFlag = {
	code: string;
	message: string;
};

export type AppliedControlSuggestionCandidate = {
	temporary_id: string;
	proposed_name: string;
	proposed_description?: string | null;
	proposed_reference_id?: string | null;
	proposed_control_type?: string | null;
	proposed_control_category?: string | null;
	proposed_status?: string | null;
	proposed_implementation_state?: string | null;
	linked_asset_ids?: string[];
	linked_asset_temporary_ids?: string[];
	related_weaknesses?: string[];
	confidence?: number;
	ambiguity_flags?: AmbiguityFlag[];
};

export type AppliedControlDuplicateMatch = {
	existing_applied_control_id: string;
	existing_name: string;
	match_type: string;
	match_score?: number;
};

export type AppliedControlDuplicateCandidate = {
	temporary_id: string;
	proposed_name: string;
	recommended_human_action?: string;
	matches?: AppliedControlDuplicateMatch[];
};

export function originalAppliedControlSuggestionSummary(
	candidate: AppliedControlSuggestionCandidate
) {
	return {
		proposed_name: candidate.proposed_name,
		proposed_description: candidate.proposed_description ?? null,
		proposed_reference_id: candidate.proposed_reference_id ?? null,
		proposed_control_type: candidate.proposed_control_type ?? null,
		proposed_control_category: candidate.proposed_control_category ?? null,
		proposed_status: candidate.proposed_status ?? null,
		proposed_implementation_state: candidate.proposed_implementation_state ?? null,
		linked_asset_ids: candidate.linked_asset_ids ?? [],
		linked_asset_temporary_ids: candidate.linked_asset_temporary_ids ?? [],
		related_weaknesses: candidate.related_weaknesses ?? [],
		confidence: candidate.confidence,
		ambiguity_flags: candidate.ambiguity_flags ?? []
	};
}

function ambiguityResolution(candidate: AppliedControlSuggestionCandidate) {
	return candidate.ambiguity_flags?.length
		? { resolution_type: 'human_reviewed', resolution_note: 'Reviewed in the Assets page.' }
		: null;
}

export function getAutoReuseAppliedControlMatch(
	candidate: AppliedControlSuggestionCandidate,
	duplicateCandidates: AppliedControlDuplicateCandidate[] = []
) {
	const duplicateCandidate = duplicateCandidates.find(
		(duplicate) => duplicate.temporary_id === candidate.temporary_id
	);
	if (!duplicateCandidate) return null;
	if (duplicateCandidate.recommended_human_action !== 'review_reuse_or_rename') return null;

	return (
		(duplicateCandidate.matches ?? [])
			.filter((match) =>
				['exact_name_same_folder', 'reference_id_same_folder'].includes(match.match_type)
			)
			.sort((left, right) => (right.match_score ?? 0) - (left.match_score ?? 0))[0] ?? null
	);
}

export function buildReviewedAppliedControlDecisions(
	selectedCandidates: AppliedControlSuggestionCandidate[],
	duplicateCandidates: AppliedControlDuplicateCandidate[] = []
) {
	return selectedCandidates.map((candidate) => {
		const autoReuseMatch = getAutoReuseAppliedControlMatch(candidate, duplicateCandidates);

		if (autoReuseMatch) {
			return {
				temporary_id: candidate.temporary_id,
				selected: true,
				action: 'reuse',
				human_approved: true,
				selected_existing_applied_control_id: autoReuseMatch.existing_applied_control_id,
				approved_fields: null,
				original_suggestion_summary: originalAppliedControlSuggestionSummary(candidate),
				reviewer_notes: `Reuse existing applied control ${autoReuseMatch.existing_name} for duplicate candidate ${candidate.temporary_id}.`,
				ambiguity_resolution: ambiguityResolution(candidate),
				duplicate_resolution: {
					decision: 'reuse_existing',
					reviewed_match_ids: [autoReuseMatch.existing_applied_control_id],
					resolution_note:
						'Exact-name or reference-id duplicate matched during Step 4A review.'
				}
			};
		}

		return {
			temporary_id: candidate.temporary_id,
			selected: true,
			action: 'create',
			human_approved: true,
			selected_existing_applied_control_id: null,
			approved_fields: {
				name: candidate.proposed_name,
				description: candidate.proposed_description ?? null,
				ref_id: candidate.proposed_reference_id ?? null,
				category: candidate.proposed_control_category ?? null,
				status: candidate.proposed_status ?? null,
				linked_asset_ids: candidate.linked_asset_ids ?? []
			},
			original_suggestion_summary: originalAppliedControlSuggestionSummary(candidate),
			reviewer_notes:
				'Human selected this candidate for deterministic applied-control commit.',
			ambiguity_resolution: ambiguityResolution(candidate),
			duplicate_resolution: null
		};
	});
}