type ProposedAssetType = {
	value?: string | null;
	label?: string | null;
};

type AmbiguityFlag = {
	code: string;
	message: string;
};

export type AssetSuggestionCandidate = {
	temporary_id: string;
	proposed_name: string;
	proposed_description?: string | null;
	proposed_reference_id?: string | null;
	proposed_asset_type?: ProposedAssetType | null;
	proposed_asset_category?: string | null;
	confidence?: number;
	ambiguity_flags?: AmbiguityFlag[];
};

export type DuplicateMatch = {
	existing_asset_id: string;
	existing_name: string;
	match_type: string;
	match_score?: number;
};

export type DuplicateCandidate = {
	temporary_id: string;
	proposed_name: string;
	recommended_human_action?: string;
	matches?: DuplicateMatch[];
};

export function originalSuggestionSummary(candidate: AssetSuggestionCandidate) {
	return {
		proposed_name: candidate.proposed_name,
		proposed_description: candidate.proposed_description ?? null,
		proposed_reference_id: candidate.proposed_reference_id ?? null,
		proposed_asset_type: candidate.proposed_asset_type ?? null,
		proposed_asset_category: candidate.proposed_asset_category ?? null,
		confidence: candidate.confidence,
		ambiguity_flags: candidate.ambiguity_flags ?? []
	};
}

function ambiguityResolution(candidate: AssetSuggestionCandidate) {
	return candidate.ambiguity_flags?.length
		? { resolution_type: 'human_reviewed', resolution_note: 'Reviewed in the Assets page.' }
		: null;
}

export function getAutoReuseMatch(
	candidate: AssetSuggestionCandidate,
	duplicateCandidates: DuplicateCandidate[] = []
) {
	const duplicateCandidate = duplicateCandidates.find(
		(duplicate) => duplicate.temporary_id === candidate.temporary_id
	);
	if (!duplicateCandidate) return null;
	if (duplicateCandidate.recommended_human_action !== 'review_reuse_before_create') return null;

	return (
		(duplicateCandidate.matches ?? [])
			.filter((match) => match.match_type === 'exact_name_same_folder')
			.sort((left, right) => (right.match_score ?? 0) - (left.match_score ?? 0))[0] ?? null
	);
}

export function buildReviewedAssetDecisions(
	selectedCandidates: AssetSuggestionCandidate[],
	duplicateCandidates: DuplicateCandidate[] = []
) {
	return selectedCandidates.map((candidate) => {
		const autoReuseMatch = getAutoReuseMatch(candidate, duplicateCandidates);

		if (autoReuseMatch) {
			return {
				temporary_id: candidate.temporary_id,
				action: 'reuse',
				human_approved: true,
				selected_existing_asset_id: autoReuseMatch.existing_asset_id,
				approved_fields: null,
				original_suggestion_summary: originalSuggestionSummary(candidate),
				reviewer_notes: `Reuse existing asset ${autoReuseMatch.existing_name} for duplicate candidate ${candidate.temporary_id}.`,
				ambiguity_resolution: ambiguityResolution(candidate),
				duplicate_resolution: {
					decision: 'reuse_existing',
					reviewed_match_ids: [autoReuseMatch.existing_asset_id],
					resolution_note: 'Exact same-folder duplicate matched during Step 3A review.'
				}
			};
		}

		return {
			temporary_id: candidate.temporary_id,
			action: 'create',
			human_approved: true,
			selected_existing_asset_id: null,
			approved_fields: {
				name: candidate.proposed_name,
				description: candidate.proposed_description ?? null,
				type: candidate.proposed_asset_type?.value ?? 'PR',
				ref_id: candidate.proposed_reference_id ?? null,
				observation: `Created from Local AI asset suggestion ${candidate.temporary_id}.`
			},
			original_suggestion_summary: originalSuggestionSummary(candidate),
			reviewer_notes: 'Human selected this candidate for deterministic asset commit.',
			ambiguity_resolution: ambiguityResolution(candidate),
			duplicate_resolution: null
		};
	});
}