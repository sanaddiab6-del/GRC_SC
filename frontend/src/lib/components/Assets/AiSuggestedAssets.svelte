<script lang="ts">
	import { deserialize } from '$app/forms';
	import type { ActionResult } from '@sveltejs/kit';
	import { onMount } from 'svelte';
	import {
		buildReviewedAppliedControlDecisions,
		getAutoReuseAppliedControlMatch,
		type AppliedControlDuplicateCandidate
	} from './appliedControlCommitDecisions';
	import {
		buildReviewedAssetDecisions,
		getAutoReuseMatch,
		type DuplicateCandidate
	} from './assetCommitDecisions';

	let sourceStep1DraftHash = $state('');
	let setupReference = $state({
		folder_id: '',
		perimeter_id: '',
		compliance_assessment_id: '',
		risk_assessment_id: '',
		selected_framework_id: ''
	});
	let scenarioText = $state('');
	let scopeSummary = $state('');
	let knownWeaknesses = $state('');
	let strictMode = $state(true);
	let loading = $state<
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
		| null
	>(null);
	let error = $state<any>(null);
	let assetDraft = $state<any>(null);
	let assetDraftHash = $state('');
	let selectedTemporaryIds = $state<Record<string, boolean>>({});
	let commitApproved = $state(false);
	let commitDryRun = $state<any>(null);
	let commitResult = $state<any>(null);
	let assetCommitHash = $state('');
	let appliedControlDraft = $state<any>(null);
	let appliedControlDraftHash = $state('');
	let selectedAppliedControlTemporaryIds = $state<Record<string, boolean>>({});
	let appliedControlCommitApproved = $state(false);
	let appliedControlCommitDryRun = $state<any>(null);
	let appliedControlCommitResult = $state<any>(null);
	let appliedControlCommitHash = $state('');
	let evidenceFindingDraft = $state<any>(null);
	let evidenceFindingDraftHash = $state('');
	let selectedEvidenceRequestIds = $state<Record<string, boolean>>({});
	let selectedAuditQuestionIds = $state<Record<string, boolean>>({});
	let selectedPreliminaryFindingIds = $state<Record<string, boolean>>({});
	let evidenceFindingCommitApproved = $state(false);
	let evidenceFindingCommitDryRun = $state<any>(null);
	let evidenceFindingCommitResult = $state<any>(null);
	// Step 6A is advisory only: there is no commit state, no dry-run state, and no approval flag.
	let remediationActionDraft = $state<any>(null);
	// Step 6B is the deterministic write step for the Step 6A suggestions.
	let selectedRemediationActionIds = $state<Record<string, boolean>>({});
	let remediationCommitApproved = $state(false);
	let remediationCommitDryRun = $state<any>(null);
	let remediationCommitResult = $state<any>(null);
	// Step 7A is advisory only: no commit state, no dry-run state, and no approval flag.
	let frameworkControlMappingDraft = $state<any>(null);
	let caseContext = $state<any>(null);
	// Step 7B is the deterministic write step for the Step 7A framework mappings.
	let selectedFrameworkMappingIds = $state<Record<string, boolean>>({});
	let frameworkMappingCommitApproved = $state(false);
	let frameworkMappingCommitDryRun = $state<any>(null);
	let frameworkMappingCommitResult = $state<any>(null);
	// Step 8A is advisory only: no commit state, no dry-run state, and no approval flag.
	let riskScenarioDraft = $state<any>(null);
	// Step 8B is the deterministic write step for the Step 8A risk scenarios.
	let selectedRiskScenarioIds = $state<Record<string, boolean>>({});
	let riskScenarioCommitApproved = $state(false);
	let riskScenarioCommitDryRun = $state<any>(null);
	let riskScenarioCommitResult = $state<any>(null);
	// Step 9A is advisory only: no commit state, no dry-run state, and no approval flag.
	let controlEffectivenessDraft = $state<any>(null);
	// Step 9B is the deterministic write step for the Step 9A judgements.
	let selectedControlEffectivenessIds = $state<Record<string, boolean>>({});
	let controlEffectivenessCommitApproved = $state(false);
	let controlEffectivenessCommitDryRun = $state<any>(null);
	let controlEffectivenessCommitResult = $state<any>(null);
	// Step 10A is advisory only: no commit state, no dry-run state, and no approval flag.
	let auditReadinessDraft = $state<any>(null);
	// Step 10B is the deterministic write step for the Step 10A readiness summary.
	let auditReadinessSelected = $state(false);
	let auditReadinessCommitApproved = $state(false);
	let auditReadinessCommitDryRun = $state<any>(null);
	let auditReadinessCommitResult = $state<any>(null);
	// Step 11A is advisory only: no commit state, no dry-run state, and no approval flag.
	let auditReportDraft = $state<any>(null);
	// Step 11B is the deterministic write step for the Step 11A report draft.
	let auditReportSelected = $state(false);
	let auditReportCommitApproved = $state(false);
	let auditReportCommitDryRun = $state<any>(null);
	let auditReportCommitResult = $state<any>(null);
	// Step 12A is advisory only: no commit state, no dry-run state, and no approval flag.
	let finalReviewDraft = $state<any>(null);
	// Step 12B is the deterministic write step for the Step 12A handoff summary.
	let finalReviewSelected = $state(false);
	let finalReviewCommitApproved = $state(false);
	let finalReviewCommitDryRun = $state<any>(null);
	let finalReviewCommitResult = $state<any>(null);

	const providerMode = $derived(
		assetDraft?.provider_mode ?? assetDraft?.source_summary?.provider_mode ?? 'not run'
	);
	const appliedControlProviderMode = $derived(
		appliedControlDraft?.provider_mode ??
			appliedControlDraft?.source_summary?.provider_mode ??
			'not run'
	);
	const evidenceFindingProviderMode = $derived(
		evidenceFindingDraft?.provider_mode ??
			evidenceFindingDraft?.source_summary?.provider_mode ??
			'not run'
	);
	const remediationActionProviderMode = $derived(
		remediationActionDraft?.provider_mode ?? 'not run'
	);
	const frameworkControlMappingProviderMode = $derived(
		frameworkControlMappingDraft?.provider_mode ?? 'not run'
	);
	const riskScenarioProviderMode = $derived(riskScenarioDraft?.provider_mode ?? 'not run');
	const controlEffectivenessProviderMode = $derived(
		controlEffectivenessDraft?.provider_mode ?? 'not run'
	);
	const auditReadinessProviderMode = $derived(auditReadinessDraft?.provider_mode ?? 'not run');
	const auditReportProviderMode = $derived(auditReportDraft?.provider_mode ?? 'not run');
	const finalReviewProviderMode = $derived(finalReviewDraft?.provider_mode ?? 'not run');
	const isConfiguredLocalProvider = $derived(providerMode === 'configured_local_provider');
	const isAppliedControlConfiguredLocalProvider = $derived(
		appliedControlProviderMode === 'configured_local_provider'
	);
	const selectedCandidates = $derived(
		(assetDraft?.candidate_assets ?? []).filter(
			(candidate: any) => selectedTemporaryIds[candidate.temporary_id]
		)
	);
	const duplicateCandidates = $derived((assetDraft?.duplicate_candidates ?? []) as DuplicateCandidate[]);
	const approvedAssetReferences = $derived(buildApprovedAssetReferences());
	const selectedAppliedControlCandidates = $derived(
		(appliedControlDraft?.candidate_applied_controls ?? []).filter(
			(candidate: any) => selectedAppliedControlTemporaryIds[candidate.temporary_id]
		)
	);
	const appliedControlDuplicateCandidates = $derived(
		(appliedControlDraft?.duplicate_candidates ?? []) as AppliedControlDuplicateCandidate[]
	);
	const linkedAssetNamesById = $derived(
		Object.fromEntries(approvedAssetReferences.map((asset: any) => [asset.asset_id, asset.name]))
	);

	onMount(() => {
		const stored = localStorage.getItem('sanad_ai_onboarding_setup');
		if (!stored) return;
		try {
			const parsed = JSON.parse(stored);
			sourceStep1DraftHash = parsed.source_step1_draft_hash ?? '';
			scenarioText = parsed.scenario_summary ?? '';
			caseContext = parsed.case_context ?? null;
			setupReference = {
				folder_id: parsed.setupReference?.folder_id ?? '',
				perimeter_id: parsed.setupReference?.perimeter_id ?? '',
				compliance_assessment_id: parsed.setupReference?.compliance_assessment_id ?? '',
				risk_assessment_id: parsed.setupReference?.risk_assessment_id ?? '',
				selected_framework_id: parsed.setupReference?.selected_framework_id ?? ''
			};
		} catch {
			// Ignore stale local demo handoff data; visible fields remain editable.
		}
	});

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

	async function postAiAction(action: string, payload: any) {
		const formData = new FormData();
		formData.set('payload', JSON.stringify(payload));

		const response = await fetch(`?/${action}`, {
			method: 'POST',
			body: formData
		});
		const responseText = await response.text();
		let result: ActionResult<Record<string, any>> | null = null;
		try {
			result = deserialize(responseText) as ActionResult<Record<string, any>>;
		} catch {
			result = null;
		}

		if (result?.type === 'success') return result.data?.aiResult;
		if (result?.type === 'failure') throw result.data?.aiError ?? { detail: 'AI request failed.' };
		if (result?.type === 'error') throw { detail: 'AI request failed on the server.' };
		if (result?.type === 'redirect') throw { detail: 'Unexpected redirect during AI request.' };

		try {
			const parsed = JSON.parse(responseText);
			if (response.ok) return parsed;
			if (parsed && typeof parsed === 'object') throw parsed;
		} catch {
			// If response is not JSON, fall through to a plain detail message.
		}

		throw {
			detail: responseText || `AI request failed with status ${response.status}.`
		};
	}

	function cleanSetupReferenceForSuggestion() {
		return {
			folder_id: setupReference.folder_id,
			perimeter_id: setupReference.perimeter_id || null,
			compliance_assessment_id: setupReference.compliance_assessment_id || null,
			risk_assessment_id: setupReference.risk_assessment_id || null
		};
	}

	function cleanSetupReferenceForCommit() {
		return {
			folder_id: setupReference.folder_id,
			perimeter_id: setupReference.perimeter_id || null,
			compliance_assessment_id: setupReference.compliance_assessment_id || null,
			risk_assessment_id: setupReference.risk_assessment_id || null,
			selected_framework_id: setupReference.selected_framework_id || null
		};
	}

	function knownWeaknessList() {
		return knownWeaknesses
			.split('\n')
			.map((item) => item.trim())
			.filter(Boolean);
	}

	function buildApprovedAssetReferences() {
		const assets = [
			...(commitResult?.created_assets ?? []),
			...(commitResult?.reused_assets ?? [])
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

	function buildSuggestionPayload() {
		return {
			source_step1_draft_hash: sourceStep1DraftHash,
			case_setup_reference: cleanSetupReferenceForSuggestion(),
			folder_id: setupReference.folder_id,
			perimeter_id: setupReference.perimeter_id || null,
			compliance_assessment_id: setupReference.compliance_assessment_id || null,
			risk_assessment_id: setupReference.risk_assessment_id || null,
			scenario_text: scenarioText,
			scope_summary: scopeSummary,
			known_weaknesses: knownWeaknessList(),
			selected_framework_id: setupReference.selected_framework_id || null,
			strict_mode: strictMode
		};
	}

	function buildAssetDecisions() {
		return buildReviewedAssetDecisions(selectedCandidates as any[], duplicateCandidates);
	}

	function buildCommitPayload(dryRun: boolean) {
		if (!assetDraft || !assetDraftHash) throw { detail: 'Run Step 3A before Step 3B.' };
		if (!selectedCandidates.length) throw { detail: 'Select at least one candidate asset.' };
		if (!dryRun && !commitApproved)
			throw { detail: 'Approve the deterministic asset write first.' };

		return {
			dry_run: dryRun,
			approved_by_user: !dryRun && commitApproved,
			idempotency_key: dryRun ? null : `frontend-step3b-${Date.now()}`,
			source_step1_draft_hash: sourceStep1DraftHash,
			source_asset_draft_hash: assetDraftHash,
			case_setup_reference: cleanSetupReferenceForCommit(),
			asset_decisions: buildAssetDecisions()
		};
	}

	function buildAppliedControlSuggestionPayload() {
		if (!commitResult) throw { detail: 'Complete the approved asset commit before Step 4A.' };
		if (!assetCommitHash) throw { detail: 'Missing source_asset_commit_hash from Step 3B result.' };
		if (!approvedAssetReferences.length) {
			throw { detail: 'Step 4A requires at least one created or reused approved asset.' };
		}

		return {
			source_step1_draft_hash: sourceStep1DraftHash,
			source_asset_commit_hash: assetCommitHash,
			case_setup_reference: cleanSetupReferenceForCommit(),
			asset_references: approvedAssetReferences,
			scenario_text: scenarioText,
			scope_summary: scopeSummary,
			known_weaknesses: knownWeaknessList(),
			selected_framework_id: setupReference.selected_framework_id || null,
			user_locale: 'en',
			strict_mode: true
		};
	}

	function buildAppliedControlDecisions() {
		return buildReviewedAppliedControlDecisions(
			selectedAppliedControlCandidates as any[],
			appliedControlDuplicateCandidates
		);
	}

	function buildAppliedControlCommitPayload(dryRun: boolean) {
		if (!appliedControlDraft || !appliedControlDraftHash) {
			throw { detail: 'Run Step 4A before Step 4B.' };
		}
		if (!assetCommitHash) throw { detail: 'Complete the approved asset commit before Step 4B.' };
		if (!selectedAppliedControlCandidates.length) {
			throw { detail: 'Select at least one candidate applied control.' };
		}
		if (!dryRun && !appliedControlCommitApproved) {
			throw { detail: 'Approve the deterministic applied-control write first.' };
		}

		return {
			dry_run: dryRun,
			approved_by_user: !dryRun && appliedControlCommitApproved,
			idempotency_key: dryRun ? null : `frontend-step4b-${Date.now()}`,
			source_step1_draft_hash: sourceStep1DraftHash,
			source_asset_commit_hash: assetCommitHash,
			source_applied_control_draft_hash: appliedControlDraftHash,
			case_setup_reference: cleanSetupReferenceForCommit(),
			asset_references: approvedAssetReferences,
			applied_control_decisions: buildAppliedControlDecisions()
		};
	}

	async function runSuggestion() {
		loading = 'suggest';
		error = null;
		commitDryRun = null;
		commitResult = null;
		assetCommitHash = '';
		appliedControlDraft = null;
		appliedControlDraftHash = '';
		selectedAppliedControlTemporaryIds = {};
		appliedControlCommitApproved = false;
		appliedControlCommitDryRun = null;
		appliedControlCommitResult = null;
		try {
			assetDraft = await postAiAction('aiAssetSuggest', buildSuggestionPayload());
			assetDraftHash = await sha256Draft(assetDraft);
			selectedTemporaryIds = Object.fromEntries(
				(assetDraft?.candidate_assets ?? []).map((candidate: any) => [
					candidate.temporary_id,
					false
				])
			);
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	async function runCommit(dryRun: boolean) {
		loading = dryRun ? 'dry-run' : 'commit';
		error = null;
		try {
			const result = await postAiAction('aiAssetCommit', buildCommitPayload(dryRun));
			if (dryRun) commitDryRun = result;
			else {
				commitResult = result;
				assetCommitHash = await sha256Draft(result);
				appliedControlDraft = null;
				appliedControlDraftHash = '';
				selectedAppliedControlTemporaryIds = {};
				appliedControlCommitApproved = false;
				appliedControlCommitDryRun = null;
				appliedControlCommitResult = null;
				appliedControlCommitHash = '';
				evidenceFindingDraft = null;
				remediationActionDraft = null;
			}
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	async function runAppliedControlSuggestion() {
		loading = 'control-suggest';
		error = null;
		try {
			appliedControlDraft = await postAiAction(
				'aiAppliedControlSuggest',
				buildAppliedControlSuggestionPayload()
			);
			appliedControlDraftHash = await sha256Draft(appliedControlDraft);
			selectedAppliedControlTemporaryIds = Object.fromEntries(
				(appliedControlDraft?.candidate_applied_controls ?? []).map((candidate: any) => [
					candidate.temporary_id,
					false
				])
			);
			appliedControlCommitApproved = false;
			appliedControlCommitDryRun = null;
			appliedControlCommitResult = null;
			appliedControlCommitHash = '';
			evidenceFindingDraft = null;
			remediationActionDraft = null;
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	async function runAppliedControlCommit(dryRun: boolean) {
		loading = dryRun ? 'control-dry-run' : 'control-commit';
		error = null;
		try {
			const result = await postAiAction(
				'aiAppliedControlCommit',
				buildAppliedControlCommitPayload(dryRun)
			);
			if (dryRun) appliedControlCommitDryRun = result;
			else {
				appliedControlCommitResult = result;
				appliedControlCommitHash = await sha256Draft(result);
				evidenceFindingDraft = null;
				remediationActionDraft = null;
			}
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	function buildApprovedAppliedControlReferences() {
		const controls = [
			...(appliedControlCommitResult?.created_applied_controls ?? []),
			...(appliedControlCommitResult?.reused_applied_controls ?? [])
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

	function buildEvidenceFindingSuggestionPayload() {
		if (!appliedControlCommitResult || !appliedControlCommitHash) {
			throw { detail: 'Complete the approved applied control commit (Step 4B) before Step 5A.' };
		}
		if (!assetCommitHash) throw { detail: 'Missing source_asset_commit_hash from Step 3B result.' };
		if (!appliedControlDraftHash) throw { detail: 'Missing source_applied_control_draft_hash from Step 4A.' };
		const appliedControlReferences = buildApprovedAppliedControlReferences();
		if (!approvedAssetReferences.length) {
			throw { detail: 'Step 5A requires at least one created or reused approved asset.' };
		}
		if (!appliedControlReferences.length) {
			throw { detail: 'Step 5A requires at least one committed or reused applied control.' };
		}

		return {
			source_step1_draft_hash: sourceStep1DraftHash,
			source_asset_commit_hash: assetCommitHash,
			source_applied_control_draft_hash: appliedControlDraftHash,
			source_applied_control_commit_hash: appliedControlCommitHash,
			case_setup_reference: cleanSetupReferenceForCommit(),
			asset_references: approvedAssetReferences,
			applied_control_references: appliedControlReferences,
			scenario_text: scenarioText,
			scope_summary: scopeSummary,
			known_weaknesses: knownWeaknessList(),
			selected_framework_id: setupReference.selected_framework_id || null,
			user_locale: 'en',
			strict_mode: true
		};
	}

	async function runEvidenceFindingSuggestion() {
		loading = 'evidence-suggest';
		error = null;
		try {
			const draft = await postAiAction(
				'aiEvidenceFindingSuggest',
				buildEvidenceFindingSuggestionPayload()
			);
			evidenceFindingDraft = draft;
			evidenceFindingDraftHash = await sha256Draft(draft);
			selectedEvidenceRequestIds = Object.fromEntries(
				(draft?.evidence_requests ?? []).map((item: any) => [item.temporary_id, false])
			);
			selectedAuditQuestionIds = Object.fromEntries(
				(draft?.audit_questions ?? []).map((item: any) => [item.temporary_id, false])
			);
			selectedPreliminaryFindingIds = Object.fromEntries(
				(draft?.preliminary_findings ?? []).map((item: any) => [item.temporary_id, false])
			);
			evidenceFindingCommitApproved = false;
			evidenceFindingCommitDryRun = null;
			evidenceFindingCommitResult = null;
			remediationActionDraft = null;
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

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
				human_approved: evidenceFindingCommitApproved,
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

	function selectedEvidenceFindingCount() {
		const draft = evidenceFindingDraft;
		if (!draft) return 0;
		return (
			buildEvidenceFindingDecisions(draft.evidence_requests, selectedEvidenceRequestIds, 'x').length +
			buildEvidenceFindingDecisions(draft.audit_questions, selectedAuditQuestionIds, 'x').length +
			buildEvidenceFindingDecisions(draft.preliminary_findings, selectedPreliminaryFindingIds, 'x')
				.length
		);
	}

	function buildEvidenceFindingCommitPayload(dryRun: boolean) {
		if (!evidenceFindingDraft || !evidenceFindingDraftHash) {
			throw { detail: 'Run Step 5A before Step 5B.' };
		}
		if (!appliedControlCommitHash) {
			throw { detail: 'Complete the approved applied control commit (Step 4B) before Step 5B.' };
		}
		if (!selectedEvidenceFindingCount()) {
			throw { detail: 'Select at least one evidence/finding suggestion to commit.' };
		}
		if (!dryRun && !evidenceFindingCommitApproved) {
			throw { detail: 'Approve the deterministic Step 5B write first.' };
		}

		return {
			dry_run: dryRun,
			approved_by_user: !dryRun && evidenceFindingCommitApproved,
			idempotency_key: dryRun ? null : `frontend-step5b-${Date.now()}`,
			source_step1_draft_hash: sourceStep1DraftHash,
			source_asset_commit_hash: assetCommitHash,
			source_applied_control_commit_hash: appliedControlCommitHash,
			source_evidence_finding_draft_hash: evidenceFindingDraftHash,
			case_setup_reference: cleanSetupReferenceForCommit(),
			asset_references: approvedAssetReferences,
			applied_control_references: buildApprovedAppliedControlReferences(),
			evidence_request_decisions: buildEvidenceFindingDecisions(
				evidenceFindingDraft.evidence_requests,
				selectedEvidenceRequestIds,
				'evidence_request'
			),
			audit_question_decisions: buildEvidenceFindingDecisions(
				evidenceFindingDraft.audit_questions,
				selectedAuditQuestionIds,
				'audit_question'
			),
			preliminary_finding_decisions: buildEvidenceFindingDecisions(
				evidenceFindingDraft.preliminary_findings,
				selectedPreliminaryFindingIds,
				'preliminary_finding'
			)
		};
	}

	async function runEvidenceFindingCommit(dryRun: boolean) {
		loading = dryRun ? 'evidence-commit-dry-run' : 'evidence-commit';
		error = null;
		try {
			const result = await postAiAction(
				'aiEvidenceFindingCommit',
				buildEvidenceFindingCommitPayload(dryRun)
			);
			if (dryRun) evidenceFindingCommitDryRun = result;
			else evidenceFindingCommitResult = result;
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	// ---- Step 6A: advisory remediation suggestion. No commit, no dry-run, no write. ----

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

	function buildRemediationActionSuggestionPayload() {
		const preliminaryFindings = buildRemediationContextItems(
			evidenceFindingDraft?.preliminary_findings ?? [],
			(item, index) => displayFindingTitle(item, index)
		);
		const weaknesses = knownWeaknessList();
		if (!preliminaryFindings.length && !weaknesses.length) {
			throw {
				detail: 'Step 6A needs at least one Step 5A preliminary finding or one known weakness.'
			};
		}

		const caseSummary = [scenarioText, scopeSummary]
			.map((value) => (typeof value === 'string' ? value.trim() : ''))
			.filter(Boolean)
			.join('\n\n');

		// Optional references are sent when available; missing ones never block the request.
		return {
			case_summary: caseSummary.slice(0, 20000),
			scenario_name: (scopeSummary || scenarioText || '').trim().slice(0, 500),
			folder_reference: {
				folder_id: setupReference.folder_id || null,
				folder_name: null
			},
			assets: approvedAssetReferences
				.map((asset: any) => toContextItem(asset.ref_id ?? asset.asset_id, asset.name))
				.filter(Boolean),
			applied_controls: buildApprovedAppliedControlReferences()
				.map((control: any) =>
					toContextItem(control.ref_id ?? control.applied_control_id, control.name)
				)
				.filter(Boolean),
			evidence_requests: buildRemediationContextItems(
				evidenceFindingDraft?.evidence_requests ?? [],
				(item, index) => displayEvidenceTitle(item, index)
			),
			audit_questions: buildRemediationContextItems(
				evidenceFindingDraft?.audit_questions ?? [],
				(item, index) => displayAuditQuestionTitle(item, index)
			),
			preliminary_findings: preliminaryFindings,
			known_weaknesses: weaknesses,
			user_locale: 'en',
			strict_mode: true
		};
	}

	async function runRemediationActionSuggestion() {
		loading = 'remediation-suggest';
		error = null;
		try {
			const draft = await postAiAction(
				'aiRemediationActionSuggest',
				buildRemediationActionSuggestionPayload()
			);
			remediationActionDraft = draft;
			selectedRemediationActionIds = Object.fromEntries(
				(draft?.remediation_actions ?? []).map((action: any) => [action.temporary_id, false])
			);
			remediationCommitApproved = false;
			remediationCommitDryRun = null;
			remediationCommitResult = null;
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	// ---- Step 6B: deterministic commit. No AI model is called in this step. ----

	const selectedRemediationActions = $derived(
		(remediationActionDraft?.remediation_actions ?? []).filter(
			(action: any) => selectedRemediationActionIds[action.temporary_id]
		)
	);
	const remediationDryRunSucceeded = $derived(
		Boolean(remediationCommitDryRun) &&
			!(remediationCommitDryRun?.blocking_errors ?? []).length &&
			remediationCommitDryRun?.commit_status !== 'blocked'
	);

	function buildRemediationActionCommitPayload(dryRun: boolean) {
		if (!remediationActionDraft) throw { detail: 'Run Step 6A before Step 6B.' };
		if (!setupReference.folder_id) {
			throw { detail: 'A Folder ID is required before the deterministic Step 6B write.' };
		}
		if (!selectedRemediationActions.length) {
			throw { detail: 'Select at least one remediation action to commit.' };
		}
		if (!dryRun && !remediationDryRunSucceeded) {
			throw { detail: 'Run a successful Step 6B dry-run before the approved commit.' };
		}
		if (!dryRun && !remediationCommitApproved) {
			throw { detail: 'Approve the deterministic Step 6B write first.' };
		}

		return {
			dry_run: dryRun,
			approved: dryRun ? false : remediationCommitApproved,
			folder_reference: setupReference.folder_id,
			decisions: selectedRemediationActions.map((action: any) => ({
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

	async function runRemediationActionCommit(dryRun: boolean) {
		loading = dryRun ? 'remediation-commit-dry-run' : 'remediation-commit';
		error = null;
		try {
			const result = await postAiAction(
				'aiRemediationActionCommit',
				buildRemediationActionCommitPayload(dryRun)
			);
			if (dryRun) {
				remediationCommitDryRun = result;
				remediationCommitResult = null;
			} else {
				remediationCommitResult = result;
			}
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	// ---- Step 7A: advisory framework control mapping. No commit, no dry-run, no write. ----

	// Best-effort framework label from the Step 1 case context. It only narrows the
	// read-only candidate lookup; a missing label never blocks Step 7A.
	function frameworkNameHint() {
		const entries = caseContext?.regulatory_context;
		for (const entry of Array.isArray(entries) ? entries : []) {
			const label =
				typeof entry === 'string' ? entry : (entry?.value ?? entry?.label ?? entry?.name ?? '');
			if (typeof label === 'string' && label.trim()) return label.trim().slice(0, 200);
		}
		return '';
	}

	function buildFrameworkControlMappingSuggestionPayload() {
		const frameworkName = frameworkNameHint();
		const caseSummary = [scenarioText, scopeSummary]
			.map((value) => (typeof value === 'string' ? value.trim() : ''))
			.filter(Boolean)
			.join('\n\n');

		// Optional references are sent when available; missing ones never block the demo.
		// Framework controls are never invented here: the backend only maps to controls
		// that were supplied or safely discovered read-only from the referenced framework.
		return {
			case_summary: caseSummary.slice(0, 20000),
			scenario_name: (scopeSummary || scenarioText || '').trim().slice(0, 500),
			folder_reference: {
				folder_id: setupReference.folder_id || null,
				folder_name: null
			},
			framework_name: frameworkName || null,
			framework_reference: {
				framework_id: setupReference.selected_framework_id || null,
				framework_urn: null,
				framework_name: frameworkName || null
			},
			assets: approvedAssetReferences
				.map((asset: any) => toContextItem(asset.ref_id ?? asset.asset_id, asset.name))
				.filter(Boolean),
			applied_controls: buildApprovedAppliedControlReferences()
				.map((control: any) =>
					toContextItem(control.ref_id ?? control.applied_control_id, control.name)
				)
				.filter(Boolean),
			remediation_actions: buildRemediationContextItems(
				remediationActionDraft?.remediation_actions ?? [],
				(item, index) => item?.title || `Remediation action ${index + 1}`
			),
			evidence_requests: buildRemediationContextItems(
				evidenceFindingDraft?.evidence_requests ?? [],
				(item, index) => displayEvidenceTitle(item, index)
			),
			audit_questions: buildRemediationContextItems(
				evidenceFindingDraft?.audit_questions ?? [],
				(item, index) => displayAuditQuestionTitle(item, index)
			),
			preliminary_findings: buildRemediationContextItems(
				evidenceFindingDraft?.preliminary_findings ?? [],
				(item, index) => displayFindingTitle(item, index)
			),
			known_weaknesses: knownWeaknessList(),
			candidate_framework_controls: [],
			user_locale: 'en',
			strict_mode: true
		};
	}

	async function runFrameworkControlMappingSuggestion() {
		loading = 'framework-mapping-suggest';
		error = null;
		try {
			const draft = await postAiAction(
				'aiFrameworkControlMappingSuggest',
				buildFrameworkControlMappingSuggestionPayload()
			);
			frameworkControlMappingDraft = draft;
			// Hand the Step 7A suggestions to the Step 7B review state. Nothing is written.
			selectedFrameworkMappingIds = Object.fromEntries(
				(draft?.framework_control_mappings ?? []).map((mapping: any) => [
					mapping.temporary_id,
					false
				])
			);
			frameworkMappingCommitApproved = false;
			frameworkMappingCommitDryRun = null;
			frameworkMappingCommitResult = null;
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	// ---- Step 7B: deterministic commit. No AI model is called in this step. ----

	const selectedFrameworkMappings = $derived(
		(frameworkControlMappingDraft?.framework_control_mappings ?? []).filter(
			(mapping: any) => selectedFrameworkMappingIds[mapping.temporary_id]
		)
	);
	const frameworkMappingDryRunSucceeded = $derived(
		Boolean(frameworkMappingCommitDryRun) &&
			!(frameworkMappingCommitDryRun?.blocking_errors ?? []).length &&
			frameworkMappingCommitDryRun?.commit_status !== 'blocked'
	);
	// Step 7A falls back to the read-only framework export file when the referenced framework
	// has no assessable requirement nodes in the database. Those controls exist in the export
	// but not as platform records, and Step 7B never creates framework controls, so the commit
	// will block. Surfacing it here explains the block before the dry-run rather than after.
	const frameworkMappingUsedCsvFallback = $derived(
		(frameworkControlMappingDraft?.warnings ?? []).some(
			(warning: any) => warning?.code === 'framework_controls_loaded_from_csv_export'
		)
	);

	function buildFrameworkControlMappingCommitPayload(dryRun: boolean) {
		if (!frameworkControlMappingDraft) throw { detail: 'Run Step 7A before Step 7B.' };
		if (!setupReference.folder_id) {
			throw { detail: 'A Folder ID is required before the deterministic Step 7B write.' };
		}
		if (!setupReference.compliance_assessment_id) {
			throw {
				detail: 'A Compliance Assessment ID is required before the deterministic Step 7B write.'
			};
		}
		if (!selectedFrameworkMappings.length) {
			throw { detail: 'Select at least one framework control mapping to commit.' };
		}
		if (!dryRun && !frameworkMappingDryRunSucceeded) {
			throw { detail: 'Run a successful Step 7B dry-run before the approved commit.' };
		}
		if (!dryRun && !frameworkMappingCommitApproved) {
			throw { detail: 'Approve the deterministic Step 7B write first.' };
		}

		return {
			dry_run: dryRun,
			approved: dryRun ? false : frameworkMappingCommitApproved,
			folder_reference: setupReference.folder_id,
			assessment_reference: setupReference.compliance_assessment_id,
			framework_reference: setupReference.selected_framework_id || '',
			decisions: selectedFrameworkMappings.map((mapping: any) => ({
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

	async function runFrameworkControlMappingCommit(dryRun: boolean) {
		loading = dryRun ? 'framework-mapping-commit-dry-run' : 'framework-mapping-commit';
		error = null;
		try {
			const result = await postAiAction(
				'aiFrameworkControlMappingCommit',
				buildFrameworkControlMappingCommitPayload(dryRun)
			);
			if (dryRun) {
				frameworkMappingCommitDryRun = result;
				frameworkMappingCommitResult = null;
			} else {
				frameworkMappingCommitResult = result;
			}
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	// ---- Shared onboarding context helpers for Steps 8A-12A ----------------------------

	function caseSummaryText() {
		return [scenarioText, scopeSummary]
			.map((value) => (typeof value === 'string' ? value.trim() : ''))
			.filter(Boolean)
			.join('\n\n')
			.slice(0, 20000);
	}

	function scenarioLabel() {
		return (scopeSummary || scenarioText || '').trim().slice(0, 500);
	}

	function folderReferenceContext() {
		return { folder_id: setupReference.folder_id || null, folder_name: null };
	}

	function assessmentReferenceContext() {
		return {
			assessment_id: setupReference.compliance_assessment_id || null,
			assessment_name: null
		};
	}

	function approvedAssetContextItems() {
		return approvedAssetReferences
			.map((asset: any) => toContextItem(asset.ref_id ?? asset.asset_id, asset.name))
			.filter(Boolean);
	}

	function approvedControlContextItems() {
		return buildApprovedAppliedControlReferences()
			.map((control: any) => toContextItem(control.ref_id ?? control.applied_control_id, control.name))
			.filter(Boolean);
	}

	function evidenceRequestContextItems() {
		return buildRemediationContextItems(evidenceFindingDraft?.evidence_requests ?? [], (item, index) =>
			displayEvidenceTitle(item, index)
		);
	}

	function auditQuestionContextItems() {
		return buildRemediationContextItems(evidenceFindingDraft?.audit_questions ?? [], (item, index) =>
			displayAuditQuestionTitle(item, index)
		);
	}

	function findingContextItems() {
		return buildRemediationContextItems(
			evidenceFindingDraft?.preliminary_findings ?? [],
			(item, index) => displayFindingTitle(item, index)
		);
	}

	function remediationActionContextItems() {
		return buildRemediationContextItems(
			remediationActionDraft?.remediation_actions ?? [],
			(item, index) => item?.title || `Remediation action ${index + 1}`
		);
	}

	// Framework mappings are carried over exactly as Step 7A resolved them, so later steps
	// can only ever reference framework controls that already exist.
	function frameworkMappingContextItems() {
		return (frameworkControlMappingDraft?.framework_control_mappings ?? [])
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
		return (riskScenarioDraft?.risk_scenarios ?? [])
			.map((scenario: any) => toContextItem(scenario?.temporary_id, scenario?.title, scenario?.description))
			.filter(Boolean);
	}

	function controlEffectivenessContextItems() {
		return (controlEffectivenessDraft?.control_effectiveness_suggestions ?? [])
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

	// ---- Step 8A: advisory risk scenario suggestion. No commit, no dry-run, no write. ----

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

	async function runRiskScenarioSuggestion() {
		loading = 'risk-scenario-suggest';
		error = null;
		try {
			const draft = await postAiAction('aiRiskScenarioSuggest', buildRiskScenarioSuggestionPayload());
			riskScenarioDraft = draft;
			// Hand the Step 8A suggestions to the Step 8B review state. Nothing is written.
			selectedRiskScenarioIds = Object.fromEntries(
				(draft?.risk_scenarios ?? []).map((scenario: any) => [scenario.temporary_id, false])
			);
			riskScenarioCommitApproved = false;
			riskScenarioCommitDryRun = null;
			riskScenarioCommitResult = null;
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	// ---- Step 8B: deterministic commit. No AI model is called in this step. ----

	const selectedRiskScenarios = $derived(
		(riskScenarioDraft?.risk_scenarios ?? []).filter(
			(scenario: any) => selectedRiskScenarioIds[scenario.temporary_id]
		)
	);
	const riskScenarioDryRunSucceeded = $derived(
		Boolean(riskScenarioCommitDryRun) &&
			!(riskScenarioCommitDryRun?.blocking_errors ?? []).length &&
			riskScenarioCommitDryRun?.commit_status !== 'blocked'
	);

	function buildRiskScenarioCommitPayload(dryRun: boolean) {
		if (!riskScenarioDraft) throw { detail: 'Run Step 8A before Step 8B.' };
		if (!setupReference.folder_id) {
			throw { detail: 'A Folder ID is required before the deterministic Step 8B write.' };
		}
		if (!setupReference.risk_assessment_id) {
			throw {
				detail:
					'A Risk Assessment ID is required before the deterministic Step 8B write. Step 8B never creates a risk assessment.'
			};
		}
		if (!selectedRiskScenarios.length) {
			throw { detail: 'Select at least one risk scenario to commit.' };
		}
		if (!dryRun && !riskScenarioDryRunSucceeded) {
			throw { detail: 'Run a successful Step 8B dry-run before the approved commit.' };
		}
		if (!dryRun && !riskScenarioCommitApproved) {
			throw { detail: 'Approve the deterministic Step 8B write first.' };
		}

		return {
			dry_run: dryRun,
			approved: dryRun ? false : riskScenarioCommitApproved,
			folder_reference: setupReference.folder_id,
			assessment_reference: setupReference.risk_assessment_id,
			decisions: selectedRiskScenarios.map((scenario: any) => ({
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

	async function runRiskScenarioCommit(dryRun: boolean) {
		loading = dryRun ? 'risk-scenario-commit-dry-run' : 'risk-scenario-commit';
		error = null;
		try {
			const result = await postAiAction('aiRiskScenarioCommit', buildRiskScenarioCommitPayload(dryRun));
			if (dryRun) {
				riskScenarioCommitDryRun = result;
				riskScenarioCommitResult = null;
			} else {
				riskScenarioCommitResult = result;
			}
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	// ---- Step 9A: advisory control effectiveness suggestion. No write. ----

	// Requirement assessments that Step 7B actually paired with the audit. They are the
	// existing rows Step 9B may later update; Step 9A never invents one.
	function requirementAssessmentContextItems() {
		return [
			...(frameworkMappingCommitResult?.created_records ?? []),
			...(frameworkMappingCommitResult?.reused_records ?? [])
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

	async function runControlEffectivenessSuggestion() {
		loading = 'control-effectiveness-suggest';
		error = null;
		try {
			const draft = await postAiAction(
				'aiControlEffectivenessSuggest',
				buildControlEffectivenessSuggestionPayload()
			);
			controlEffectivenessDraft = draft;
			selectedControlEffectivenessIds = Object.fromEntries(
				(draft?.control_effectiveness_suggestions ?? []).map((suggestion: any) => [
					suggestion.temporary_id,
					false
				])
			);
			controlEffectivenessCommitApproved = false;
			controlEffectivenessCommitDryRun = null;
			controlEffectivenessCommitResult = null;
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	// ---- Step 9B: deterministic commit. No AI model is called in this step. ----

	const selectedControlEffectiveness = $derived(
		(controlEffectivenessDraft?.control_effectiveness_suggestions ?? []).filter(
			(suggestion: any) => selectedControlEffectivenessIds[suggestion.temporary_id]
		)
	);
	const controlEffectivenessDryRunSucceeded = $derived(
		Boolean(controlEffectivenessCommitDryRun) &&
			!(controlEffectivenessCommitDryRun?.blocking_errors ?? []).length &&
			controlEffectivenessCommitDryRun?.commit_status !== 'blocked'
	);

	function buildControlEffectivenessCommitPayload(dryRun: boolean) {
		if (!controlEffectivenessDraft) throw { detail: 'Run Step 9A before Step 9B.' };
		if (!setupReference.folder_id) {
			throw { detail: 'A Folder ID is required before the deterministic Step 9B write.' };
		}
		if (!setupReference.compliance_assessment_id) {
			throw {
				detail: 'A Compliance Assessment ID is required before the deterministic Step 9B write.'
			};
		}
		if (!selectedControlEffectiveness.length) {
			throw { detail: 'Select at least one control effectiveness judgement to commit.' };
		}
		if (!dryRun && !controlEffectivenessDryRunSucceeded) {
			throw { detail: 'Run a successful Step 9B dry-run before the approved commit.' };
		}
		if (!dryRun && !controlEffectivenessCommitApproved) {
			throw { detail: 'Approve the deterministic Step 9B write first.' };
		}

		return {
			dry_run: dryRun,
			approved: dryRun ? false : controlEffectivenessCommitApproved,
			folder_reference: setupReference.folder_id,
			assessment_reference: setupReference.compliance_assessment_id,
			decisions: selectedControlEffectiveness.map((suggestion: any) => ({
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

	async function runControlEffectivenessCommit(dryRun: boolean) {
		loading = dryRun ? 'control-effectiveness-commit-dry-run' : 'control-effectiveness-commit';
		error = null;
		try {
			const result = await postAiAction(
				'aiControlEffectivenessCommit',
				buildControlEffectivenessCommitPayload(dryRun)
			);
			if (dryRun) {
				controlEffectivenessCommitDryRun = result;
				controlEffectivenessCommitResult = null;
			} else {
				controlEffectivenessCommitResult = result;
			}
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	// ---- Step 10A: advisory audit readiness summary. No write. ----

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

	async function runAuditReadinessSuggestion() {
		loading = 'audit-readiness-suggest';
		error = null;
		try {
			const draft = await postAiAction(
				'aiAuditReadinessSuggest',
				buildAuditReadinessSuggestionPayload()
			);
			auditReadinessDraft = draft;
			auditReadinessSelected = false;
			auditReadinessCommitApproved = false;
			auditReadinessCommitDryRun = null;
			auditReadinessCommitResult = null;
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	// ---- Step 10B: deterministic commit. No AI model is called in this step. ----

	const auditReadinessDryRunSucceeded = $derived(
		Boolean(auditReadinessCommitDryRun) &&
			!(auditReadinessCommitDryRun?.blocking_errors ?? []).length &&
			auditReadinessCommitDryRun?.commit_status !== 'blocked'
	);

	function buildAuditReadinessCommitPayload(dryRun: boolean) {
		if (!auditReadinessDraft) throw { detail: 'Run Step 10A before Step 10B.' };
		if (!setupReference.folder_id) {
			throw { detail: 'A Folder ID is required before the deterministic Step 10B write.' };
		}
		if (!setupReference.compliance_assessment_id) {
			throw {
				detail: 'A Compliance Assessment ID is required before the deterministic Step 10B write.'
			};
		}
		if (!auditReadinessSelected) {
			throw { detail: 'Select the readiness summary to record before committing.' };
		}
		if (!dryRun && !auditReadinessDryRunSucceeded) {
			throw { detail: 'Run a successful Step 10B dry-run before the approved commit.' };
		}
		if (!dryRun && !auditReadinessCommitApproved) {
			throw { detail: 'Approve the deterministic Step 10B write first.' };
		}

		return {
			dry_run: dryRun,
			approved: dryRun ? false : auditReadinessCommitApproved,
			folder_reference: setupReference.folder_id,
			assessment_reference: setupReference.compliance_assessment_id,
			decisions: [
				{
					temporary_id: 'audit_readiness_1',
					selected: true,
					decision: 'create',
					existing_record_reference: '',
					payload: {
						temporary_id: 'audit_readiness_1',
						readiness_status: auditReadinessDraft.readiness_status,
						readiness_score: auditReadinessDraft.readiness_score,
						summary: auditReadinessDraft.summary ?? '',
						ready_items: auditReadinessDraft.ready_items ?? [],
						missing_evidence: auditReadinessDraft.missing_evidence ?? [],
						open_findings: auditReadinessDraft.open_findings ?? [],
						open_risks: auditReadinessDraft.open_risks ?? [],
						blocked_controls: auditReadinessDraft.blocked_controls ?? [],
						recommended_next_steps: auditReadinessDraft.recommended_next_steps ?? [],
						priority_actions: auditReadinessDraft.priority_actions ?? [],
						confidence: auditReadinessDraft.overall_confidence,
						review_status: auditReadinessDraft.review_status
					}
				}
			]
		};
	}

	async function runAuditReadinessCommit(dryRun: boolean) {
		loading = dryRun ? 'audit-readiness-commit-dry-run' : 'audit-readiness-commit';
		error = null;
		try {
			const result = await postAiAction(
				'aiAuditReadinessCommit',
				buildAuditReadinessCommitPayload(dryRun)
			);
			if (dryRun) {
				auditReadinessCommitDryRun = result;
				auditReadinessCommitResult = null;
			} else {
				auditReadinessCommitResult = result;
			}
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	// ---- Step 11A: advisory report draft. No write. ----

	function buildAuditReportSuggestionPayload() {
		return {
			case_summary: caseSummaryText(),
			scenario_name: scenarioLabel(),
			organization_name: (caseContext?.organization ?? '') || null,
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
			evidence_gaps: auditReadinessDraft?.missing_evidence ?? [],
			audit_readiness: auditReadinessDraft
				? {
						readiness_status: auditReadinessDraft.readiness_status,
						readiness_score: auditReadinessDraft.readiness_score,
						summary: (auditReadinessDraft.summary ?? '').slice(0, 5000)
					}
				: null,
			known_weaknesses: knownWeaknessList(),
			user_locale: 'en',
			strict_mode: true
		};
	}

	async function runAuditReportSuggestion() {
		loading = 'audit-report-suggest';
		error = null;
		try {
			const draft = await postAiAction('aiAuditReportSuggest', buildAuditReportSuggestionPayload());
			auditReportDraft = draft;
			auditReportSelected = false;
			auditReportCommitApproved = false;
			auditReportCommitDryRun = null;
			auditReportCommitResult = null;
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	// ---- Step 11B: deterministic commit. No AI model is called in this step. ----

	const auditReportDryRunSucceeded = $derived(
		Boolean(auditReportCommitDryRun) &&
			!(auditReportCommitDryRun?.blocking_errors ?? []).length &&
			auditReportCommitDryRun?.commit_status !== 'blocked'
	);

	function buildAuditReportCommitPayload(dryRun: boolean) {
		if (!auditReportDraft) throw { detail: 'Run Step 11A before Step 11B.' };
		if (!setupReference.folder_id) {
			throw { detail: 'A Folder ID is required before the deterministic Step 11B write.' };
		}
		if (!(auditReportDraft.limitations ?? []).length) {
			throw { detail: 'The report draft must carry its limitations before it can be saved.' };
		}
		if (!auditReportSelected) {
			throw { detail: 'Select the report draft to save before committing.' };
		}
		if (!dryRun && !auditReportDryRunSucceeded) {
			throw { detail: 'Run a successful Step 11B dry-run before the approved commit.' };
		}
		if (!dryRun && !auditReportCommitApproved) {
			throw { detail: 'Approve the deterministic Step 11B write first.' };
		}

		return {
			dry_run: dryRun,
			approved: dryRun ? false : auditReportCommitApproved,
			folder_reference: setupReference.folder_id,
			assessment_reference: setupReference.compliance_assessment_id || '',
			decisions: [
				{
					temporary_id: 'audit_report_1',
					selected: true,
					decision: 'create',
					existing_record_reference: '',
					payload: {
						temporary_id: 'audit_report_1',
						report_title: auditReportDraft.report_title,
						executive_summary: auditReportDraft.executive_summary ?? '',
						report_sections: (auditReportDraft.report_sections ?? []).map((section: any) => ({
							heading: section.heading,
							content: section.content ?? '',
							source_items: section.source_items ?? [],
							confidence: section.confidence
						})),
						limitations: auditReportDraft.limitations ?? [],
						recommended_next_steps: auditReportDraft.recommended_next_steps ?? [],
						confidence: auditReportDraft.overall_confidence,
						review_status: auditReportDraft.review_status
					}
				}
			]
		};
	}

	async function runAuditReportCommit(dryRun: boolean) {
		loading = dryRun ? 'audit-report-commit-dry-run' : 'audit-report-commit';
		error = null;
		try {
			const result = await postAiAction('aiAuditReportCommit', buildAuditReportCommitPayload(dryRun));
			if (dryRun) {
				auditReportCommitDryRun = result;
				auditReportCommitResult = null;
			} else {
				auditReportCommitResult = result;
			}
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	// ---- Step 12A: advisory final review summary. No write. ----

	// Every commit step reports its own outcome; Step 12A only ever summarizes what those
	// steps actually returned.
	function commitStepResults(): [string, any][] {
		return [
			['3B', commitResult],
			['4B', appliedControlCommitResult],
			['5B', evidenceFindingCommitResult],
			['6B', remediationCommitResult],
			['7B', frameworkMappingCommitResult],
			['8B', riskScenarioCommitResult],
			['9B', controlEffectivenessCommitResult],
			['10B', auditReadinessCommitResult],
			['11B', auditReportCommitResult]
		];
	}

	function buildStepOutcomes() {
		return commitStepResults()
			.filter(([, result]) => Boolean(result))
			.map(([step, result]) => {
				const blocking = result.blocking_errors ?? [];
				const detail = blocking.length
					? String(blocking[0].detail ?? blocking[0].code ?? '').slice(0, 2000)
					: `${(result.created_records ?? []).length} created, ${
							(result.reused_records ?? []).length
						} reused.`;
				return {
					step,
					status: String(result.commit_status ?? result.status ?? '').slice(0, 64),
					detail
				};
			});
	}

	function collectRecordSummaries(key: 'created_records' | 'reused_records', action: string) {
		return commitStepResults()
			.filter(([, result]) => Boolean(result))
			.flatMap(([, result]) => result[key] ?? [])
			.filter((record: any) => record?.name)
			.map((record: any) => ({
				record_type: record.record_type ?? null,
				name: String(record.name).slice(0, 500),
				action
			}));
	}

	function collectBlockedItems() {
		return commitStepResults()
			.filter(([, result]) => Boolean(result))
			.flatMap(([step, result]) =>
				(result.blocking_errors ?? []).map((blockingError: any) =>
					`Step ${step}: ${blockingError.detail ?? blockingError.code ?? 'blocked'}`.slice(0, 500)
				)
			);
	}

	function buildFinalReviewSuggestionPayload() {
		const stepOutcomes = buildStepOutcomes();
		const createdRecords = collectRecordSummaries('created_records', 'create');
		const reusedRecords = collectRecordSummaries('reused_records', 'reuse');
		const blockedItems = collectBlockedItems();
		const outstandingItems = auditReadinessDraft?.missing_evidence ?? [];

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

	async function runFinalReviewSuggestion() {
		loading = 'final-review-suggest';
		error = null;
		try {
			const draft = await postAiAction('aiFinalReviewSuggest', buildFinalReviewSuggestionPayload());
			finalReviewDraft = draft;
			finalReviewSelected = false;
			finalReviewCommitApproved = false;
			finalReviewCommitDryRun = null;
			finalReviewCommitResult = null;
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	// ---- Step 12B: deterministic commit. No AI model is called in this step. ----

	const finalReviewDryRunSucceeded = $derived(
		Boolean(finalReviewCommitDryRun) &&
			!(finalReviewCommitDryRun?.blocking_errors ?? []).length &&
			finalReviewCommitDryRun?.commit_status !== 'blocked'
	);

	function buildFinalReviewCommitPayload(dryRun: boolean) {
		if (!finalReviewDraft) throw { detail: 'Run Step 12A before Step 12B.' };
		if (!setupReference.folder_id) {
			throw { detail: 'A Folder ID is required before the deterministic Step 12B write.' };
		}
		if (!setupReference.compliance_assessment_id) {
			throw {
				detail: 'A Compliance Assessment ID is required before the deterministic Step 12B write.'
			};
		}
		if (!finalReviewSelected) {
			throw { detail: 'Select the case handoff summary to record before committing.' };
		}
		if (!dryRun && !finalReviewDryRunSucceeded) {
			throw { detail: 'Run a successful Step 12B dry-run before the approved commit.' };
		}
		if (!dryRun && !finalReviewCommitApproved) {
			throw { detail: 'Approve the deterministic Step 12B write first.' };
		}

		return {
			dry_run: dryRun,
			approved: dryRun ? false : finalReviewCommitApproved,
			folder_reference: setupReference.folder_id,
			assessment_reference: setupReference.compliance_assessment_id,
			decisions: [
				{
					temporary_id: 'final_review_1',
					selected: true,
					decision: 'create',
					existing_record_reference: '',
					payload: {
						temporary_id: 'final_review_1',
						completion_summary: finalReviewDraft.completion_summary ?? '',
						completed_steps: finalReviewDraft.completed_steps ?? [],
						incomplete_steps: finalReviewDraft.incomplete_steps ?? [],
						created_or_reused_records_summary:
							finalReviewDraft.created_or_reused_records_summary ?? [],
						blocked_items: finalReviewDraft.blocked_items ?? [],
						human_review_required: finalReviewDraft.human_review_required ?? [],
						recommended_next_steps: finalReviewDraft.recommended_next_steps ?? [],
						demo_readiness_status: finalReviewDraft.demo_readiness_status,
						confidence: finalReviewDraft.overall_confidence,
						review_status: finalReviewDraft.review_status
					}
				}
			]
		};
	}

	async function runFinalReviewCommit(dryRun: boolean) {
		loading = dryRun ? 'final-review-commit-dry-run' : 'final-review-commit';
		error = null;
		try {
			const result = await postAiAction('aiFinalReviewCommit', buildFinalReviewCommitPayload(dryRun));
			if (dryRun) {
				finalReviewCommitDryRun = result;
				finalReviewCommitResult = null;
			} else {
				finalReviewCommitResult = result;
			}
		} catch (caught) {
			error = caught;
		} finally {
			loading = null;
		}
	}

	function linkedAssetLabel(assetId: string) {
		return linkedAssetNamesById[assetId] ?? assetId;
	}

	const linkedControlNamesById = $derived(
		Object.fromEntries(
			[
				...(appliedControlCommitResult?.created_applied_controls ?? []),
				...(appliedControlCommitResult?.reused_applied_controls ?? [])
			]
				.filter((control: any) => control?.applied_control_id)
				.map((control: any) => [control.applied_control_id, control.name])
		)
	);

	function linkedControlLabel(controlId: string) {
		return linkedControlNamesById[controlId] ?? controlId;
	}

	function formatConfidence(value: any) {
		if (typeof value !== 'number' || Number.isNaN(value)) return 'n/a';
		return `${Math.round(value * 100)}%`;
	}

	// ---- Display-only helpers. These never alter request payloads or backend data. ----

	function humanizeProviderMode(mode: any) {
		if (mode === 'configured_local_provider') return 'Local AI provider';
		if (mode === 'not run') return 'Not run yet';
		if (typeof mode === 'string' && mode.trim()) return mode.replaceAll('_', ' ');
		return 'Unknown';
	}

	function humanizeActionName(action: any) {
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

	function humanizeFieldLabel(value: any) {
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

	function displayEvidenceTitle(item: any, index: number) {
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

	function displayAuditQuestionTitle(item: any, index: number) {
		if (!isGenericCandidateTitle(item?.question_text)) return item.question_text;
		if (!isGenericCandidateTitle(item?.question)) return item.question;
		if (!isGenericCandidateTitle(item?.title)) return item.title;
		return (
			firstMeaningfulText(item?.summary, item?.rationale) || `Audit question ${index + 1}`
		);
	}

	function remediationPriorityBadgeClass(priority: any) {
		if (priority === 'critical') return 'bg-red-100 text-red-900';
		if (priority === 'high') return 'bg-orange-100 text-orange-900';
		if (priority === 'medium') return 'bg-yellow-100 text-yellow-900';
		if (priority === 'low') return 'bg-slate-100 text-slate-700';
		return 'bg-slate-100 text-slate-700';
	}

	function displayFindingTitle(item: any, index: number) {
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
</script>

<section class="mb-4 rounded-lg border border-teal-200 bg-teal-50/60 p-4 shadow-sm">
	<div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
		<div>
			<h2 class="text-lg font-bold text-teal-950">Step 3A &middot; AI Suggested Assets</h2>
			<p class="text-sm text-teal-900">
				<span class="font-semibold">AI suggestion only / no database write.</span>
				Step 3A drafts candidate assets for review. Nothing is saved until you select candidates
				and approve the deterministic Step 3B commit below.
			</p>
		</div>
		<div
			class="rounded px-2 py-1 text-xs font-semibold {isConfiguredLocalProvider
				? 'bg-emerald-100 text-emerald-800'
				: providerMode === 'not run'
					? 'bg-slate-100 text-slate-700'
					: 'bg-amber-100 text-amber-900'}"
		>
			AI Provider: {humanizeProviderMode(providerMode)}
		</div>
	</div>

	<div class="mt-4 grid gap-3 md:grid-cols-2">
		<label class="grid gap-1">
			<span class="text-sm font-semibold">source_step1_draft_hash</span>
			<input class="input" bind:value={sourceStep1DraftHash} />
		</label>
		<label class="grid gap-1">
			<span class="text-sm font-semibold">Folder ID</span>
			<input class="input" bind:value={setupReference.folder_id} />
		</label>
		<label class="grid gap-1">
			<span class="text-sm font-semibold">Perimeter ID</span>
			<input class="input" bind:value={setupReference.perimeter_id} />
		</label>
		<label class="grid gap-1">
			<span class="text-sm font-semibold">ComplianceAssessment ID</span>
			<input class="input" bind:value={setupReference.compliance_assessment_id} />
		</label>
		<label class="grid gap-1">
			<span class="text-sm font-semibold">RiskAssessment ID</span>
			<input class="input" bind:value={setupReference.risk_assessment_id} />
		</label>
		<label class="grid gap-1">
			<span class="text-sm font-semibold">Selected Framework ID</span>
			<input class="input" bind:value={setupReference.selected_framework_id} />
		</label>
	</div>

	<div class="mt-3 grid gap-3">
		<label class="grid gap-1">
			<span class="text-sm font-semibold">Scenario/context summary</span>
			<textarea class="textarea" rows="3" bind:value={scenarioText}></textarea>
		</label>
		<label class="grid gap-1">
			<span class="text-sm font-semibold">Scope summary</span>
			<textarea class="textarea" rows="2" bind:value={scopeSummary}></textarea>
		</label>
		<label class="grid gap-1">
			<span class="text-sm font-semibold">Known weaknesses</span>
			<textarea class="textarea" rows="2" bind:value={knownWeaknesses}></textarea>
		</label>
		<label class="flex items-center gap-2 text-sm">
			<input type="checkbox" bind:checked={strictMode} />
			<span>Strict mode</span>
		</label>
	</div>

	<div class="mt-4 flex flex-wrap items-center gap-3">
		<button
			class="btn preset-filled-primary-500"
			type="button"
			disabled={loading !== null ||
				!sourceStep1DraftHash ||
				!setupReference.folder_id ||
				!setupReference.perimeter_id ||
				!setupReference.compliance_assessment_id ||
				(!scenarioText.trim() && !scopeSummary.trim())}
			onclick={runSuggestion}
		>
			{loading === 'suggest' ? 'Running Local AI...' : 'Run Local AI Asset Suggestion'}
		</button>
		<span class="text-xs text-teal-900">No database writes occur in Step 3A.</span>
	</div>

	{#if assetDraft}
		<div class="mt-4 rounded-md border bg-white p-4">
			<div class="flex flex-wrap items-center gap-2 text-sm">
				<span class="font-semibold">AI Provider:</span>
				<span
					class="rounded px-2 py-1 text-xs {isConfiguredLocalProvider
						? 'bg-emerald-100 text-emerald-800'
						: 'bg-amber-100 text-amber-900'}">{humanizeProviderMode(providerMode)}</span
				>
				{#if !isConfiguredLocalProvider}
					<span class="text-xs text-amber-700"
						>Fallback or blocked output — this was not a successful local AI run.</span
					>
				{/if}
			</div>
			<div class="mt-2 text-sm">
				Overall confidence: {formatConfidence(assetDraft.overall_confidence)}
			</div>

			<div class="mt-3 grid gap-3">
				{#each assetDraft.candidate_assets ?? [] as candidate}
					{@const autoReuseMatch = getAutoReuseMatch(candidate, duplicateCandidates)}
					<label class="rounded border p-3 text-sm">
						<div class="flex items-start gap-3">
							<input
								type="checkbox"
								checked={!!selectedTemporaryIds[candidate.temporary_id]}
								onchange={(event) => {
									selectedTemporaryIds = {
										...selectedTemporaryIds,
										[candidate.temporary_id]: event.currentTarget.checked
									};
								}}
							/>
							<div class="space-y-1">
								<div class="font-semibold">{candidate.proposed_name}</div>
								<div>{candidate.proposed_description}</div>
								<div class="text-xs text-slate-600">
									Type: {candidate.proposed_asset_type?.label ??
										candidate.proposed_asset_type?.value ??
										'PR'} &middot; Confidence: {formatConfidence(candidate.confidence)}
								</div>
								{#if candidate.ambiguity_flags?.length}
									<div class="text-xs text-amber-700">
										Ambiguity: {candidate.ambiguity_flags
											.map((flag: any) => flag.message)
											.join('; ')}
									</div>
								{/if}
								{#if autoReuseMatch}
									<div class="rounded border border-amber-200 bg-amber-50 px-2 py-1 text-xs text-amber-900">
										Existing asset found: {autoReuseMatch.existing_name} will be reused instead of
										creating a duplicate.
									</div>
								{/if}
							</div>
						</div>
					</label>
				{/each}
			</div>

			{#if assetDraft.duplicate_candidates?.length}
				<div class="mt-3 rounded border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
					<div class="font-semibold">Possible duplicates</div>
					<p class="text-xs">
						These suggestions look similar to records that already exist. Review them before
						creating new ones.
					</p>
					<ul class="mt-1 list-disc pl-5">
						{#each assetDraft.duplicate_candidates as duplicate}
							<li>
								<span class="font-semibold">{duplicate.proposed_name}</span> &mdash;
								{humanizeActionName(duplicate.recommended_human_action)}
								{#if duplicate.matches?.[0]}
									(matches existing asset "{duplicate.matches[0].existing_name}")
								{/if}
							</li>
						{/each}
					</ul>
				</div>
			{/if}

			{#if assetDraft.blocking_questions?.length}
				<ul class="mt-3 list-disc pl-5 text-sm text-red-700">
					{#each assetDraft.blocking_questions as question}
						<li>{question.question_text}</li>
					{/each}
				</ul>
			{/if}

			<div class="mt-4 rounded border border-teal-200 bg-teal-50/50 p-3">
				<div class="text-sm font-semibold text-teal-950">Step 3B &middot; Asset Commit</div>
				<p class="mt-1 text-xs text-teal-900">
					<span class="font-semibold">No AI model is used / writes only after approval.</span>
					Dry-run previews the plan without writing. The approved commit writes only the asset
					candidates you selected above.
				</p>
				<div class="mt-3 flex flex-wrap items-center gap-3">
					<button
						class="btn btn-sm preset-tonal-primary"
						type="button"
						disabled={loading !== null || !selectedCandidates.length}
						onclick={() => runCommit(true)}
					>
						{loading === 'dry-run' ? 'Dry-running...' : 'Step 3B dry-run'}
					</button>
					<label class="flex items-center gap-2 text-sm">
						<input type="checkbox" bind:checked={commitApproved} />
						<span>I approve deterministic Step 3B decisions for selected asset candidates</span>
					</label>
					<button
						class="btn btn-sm preset-filled-primary-500"
						type="button"
						disabled={loading !== null || !selectedCandidates.length || !commitApproved}
						onclick={() => runCommit(false)}
					>
						{loading === 'commit' ? 'Committing...' : 'Approved asset commit'}
					</button>
					<span class="text-xs text-slate-600">No AI model is used in this write step.</span>
				</div>
			</div>

			{#if commitDryRun}
				<div class="mt-3 rounded border p-3 text-sm">
					<div class="font-semibold">Step 3B dry-run status: {commitDryRun.status}</div>
					<p class="mt-1 text-xs text-slate-600">
						Dry-run is a preview only — nothing was written to the database.
					</p>
					<ul class="mt-2 list-disc pl-5">
						{#each commitDryRun.planned_actions ?? [] as action}
							<li>
								<span class="font-semibold">{humanizeActionName(action.action)}</span> &mdash; {action.detail}
							</li>
						{/each}
					</ul>
				</div>
			{/if}

			{#if commitResult}
				<div class="mt-3 grid gap-2 rounded border border-emerald-200 bg-emerald-50 p-3 text-sm">
					<div class="font-semibold">Step 3B commit status: {commitResult.status}</div>
					<p class="text-xs text-emerald-900">
						Approved deterministic write completed — only the records below were touched.
					</p>
					<div>Created: {commitResult.created_assets?.length ?? 0}</div>
					<div>Reused: {commitResult.reused_assets?.length ?? 0}</div>
					<div>Rejected: {commitResult.rejected_assets?.length ?? 0}</div>
					<div>Deferred: {commitResult.deferred_assets?.length ?? 0}</div>
				</div>

				<div class="mt-4 rounded-md border border-cyan-200 bg-cyan-50/70 p-4">
					<div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
						<div>
							<h3 class="text-base font-bold text-cyan-950">
								Step 4A &middot; AI Suggested Applied Controls
							</h3>
							<p class="text-sm text-cyan-900">
								<span class="font-semibold">AI suggestion only / no database write.</span>
								Step 4A drafts candidate applied controls for the approved assets. No applied
								controls are created until the approved Step 4B commit.
							</p>
						</div>
						<div
							class="rounded px-2 py-1 text-xs font-semibold {isAppliedControlConfiguredLocalProvider
								? 'bg-emerald-100 text-emerald-800'
								: appliedControlProviderMode === 'not run'
									? 'bg-slate-100 text-slate-700'
									: 'bg-amber-100 text-amber-900'}"
						>
							AI Provider: {humanizeProviderMode(appliedControlProviderMode)}
						</div>
					</div>

					<div class="mt-3 flex flex-wrap items-center gap-3">
						<button
							class="btn btn-sm preset-filled-primary-500"
							type="button"
							disabled={loading !== null || !assetCommitHash || !approvedAssetReferences.length}
							onclick={runAppliedControlSuggestion}
						>
							{loading === 'control-suggest'
								? 'Running Local AI...'
								: 'Run Local AI Applied Control Suggestion'}
						</button>
						<span class="text-xs text-cyan-900"
							>Uses {approvedAssetReferences.length} approved asset{approvedAssetReferences.length ===
							1
								? ''
								: 's'} from Step 3B.</span
						>
					</div>

					{#if appliedControlDraft}
						<div class="mt-4 rounded border bg-white p-3 text-sm">
							<div class="flex flex-wrap gap-3">
								<div>
									<span class="font-semibold">Suggestion type:</span>
									{humanizeFieldLabel(appliedControlDraft.draft_type)}
								</div>
								<div>
									<span class="font-semibold">Suggestions found:</span>
									{appliedControlDraft.candidate_applied_controls?.length ?? 0}
								</div>
								<div>
									<span class="font-semibold">Overall confidence:</span>
									{formatConfidence(appliedControlDraft.overall_confidence)}
								</div>
							</div>

							{#if !appliedControlDraft.candidate_applied_controls?.length}
								<div class="mt-3 rounded border border-amber-200 bg-amber-50 p-3 text-amber-900">
									No applied-control candidates were returned. Review warnings or backend validation
									details before rerunning.
								</div>
							{/if}

							<div class="mt-3 grid gap-3">
								{#each appliedControlDraft.candidate_applied_controls ?? [] as candidate}
									{@const autoReuseAppliedControlMatch = getAutoReuseAppliedControlMatch(
										candidate,
										appliedControlDuplicateCandidates
									)}
									<div class="rounded border p-3">
										<div class="flex items-start gap-3">
											<input
												type="checkbox"
												checked={!!selectedAppliedControlTemporaryIds[candidate.temporary_id]}
												onchange={(event) => {
													selectedAppliedControlTemporaryIds = {
														...selectedAppliedControlTemporaryIds,
														[candidate.temporary_id]: event.currentTarget.checked
													};
												}}
											/>
											<div class="grow">
												<div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
											<div>
												<div class="font-semibold text-slate-950">{candidate.proposed_name}</div>
												<div class="mt-1 text-slate-700">{candidate.proposed_description}</div>
											</div>
											<div
												class="rounded bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700"
											>
												Confidence: {formatConfidence(candidate.confidence)}
											</div>
												</div>
												{#if autoReuseAppliedControlMatch}
													<div class="mt-3 rounded border border-amber-200 bg-amber-50 px-2 py-1 text-xs text-amber-900">
														Existing applied control found: {autoReuseAppliedControlMatch.existing_name}
														will be reused instead of creating a duplicate.
													</div>
												{/if}
												<div class="mt-3 grid gap-2 text-xs text-slate-700 md:grid-cols-3">
													<div>
														<span class="font-semibold">Category:</span>
														{humanizeFieldLabel(candidate.proposed_control_category)}
													</div>
													<div>
														<span class="font-semibold">Status:</span>
														{humanizeFieldLabel(candidate.proposed_status)}
													</div>
													<div>
														<span class="font-semibold">Implementation:</span>
														{humanizeFieldLabel(candidate.proposed_implementation_state)}
													</div>
													<div>
														<span class="font-semibold">Review status:</span>
														{humanizeFieldLabel(candidate.human_review_status)}
													</div>
													<div class="md:col-span-2">
														<span class="font-semibold">Linked assets:</span>
														{(candidate.linked_asset_ids ?? [])
															.map((assetId: string) => linkedAssetLabel(assetId))
															.join(', ') || 'none'}
													</div>
												</div>
												<div class="mt-3 text-sm">
													<span class="font-semibold">Rationale:</span>
													{candidate.rationale}
												</div>
												{#if candidate.related_weaknesses?.length}
													<div class="mt-2 text-xs text-slate-700">
														<span class="font-semibold">Related weaknesses:</span>
														{candidate.related_weaknesses.join('; ')}
													</div>
												{/if}
												{#if candidate.allowed_next_actions?.length}
													<div class="mt-2 text-xs text-slate-500">
														<span class="font-semibold">Available review actions:</span>
														{candidate.allowed_next_actions
															.map((nextAction: string) => humanizeActionName(nextAction))
															.join(', ')}
													</div>
												{/if}
											</div>
										</div>
									</div>
								{/each}
							</div>

							{#if appliedControlDraft.duplicate_candidates?.length}
								<div class="mt-3 rounded border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
									<div class="font-semibold">Possible duplicate applied controls</div>
									<p class="text-xs">
										These suggestions look similar to applied controls that already exist. Review
										them before creating new ones.
									</p>
									<ul class="mt-1 list-disc pl-5">
										{#each appliedControlDraft.duplicate_candidates as duplicate}
											<li>
												<span class="font-semibold">{duplicate.proposed_name}</span> &mdash;
												{humanizeActionName(duplicate.recommended_human_action)}
												{#if duplicate.matches?.[0]}
													(matches existing applied control "{duplicate.matches[0].existing_name}")
												{/if}
											</li>
										{/each}
									</ul>
								</div>
							{/if}

							<div class="mt-4 rounded border border-cyan-200 bg-cyan-50/60 p-3 text-sm text-cyan-950">
								<div class="font-semibold">Step 4B &middot; Applied Control Commit</div>
								<p class="mt-1 text-cyan-900">
									<span class="font-semibold">No AI model is used / writes only after approval.</span>
									Step 4A above remains advisory and no-write. Step 4B dry-run previews the plan
									without writing; the approved commit writes only the applied controls you selected.
								</p>
								<div class="mt-3 flex flex-wrap items-center gap-3">
									<button
										class="btn btn-sm preset-tonal-primary"
										type="button"
										disabled={loading !== null || !selectedAppliedControlCandidates.length}
										onclick={() => runAppliedControlCommit(true)}
									>
										{loading === 'control-dry-run' ? 'Dry-running...' : 'Step 4B dry-run'}
									</button>
									<label class="flex items-center gap-2 text-sm">
										<input type="checkbox" bind:checked={appliedControlCommitApproved} />
										<span>
											I approve deterministic Step 4B decisions for selected applied controls
										</span>
									</label>
									<button
										class="btn btn-sm preset-filled-primary-500"
										type="button"
										disabled={
											loading !== null ||
											!selectedAppliedControlCandidates.length ||
											!appliedControlCommitApproved
										}
										onclick={() => runAppliedControlCommit(false)}
									>
										{loading === 'control-commit'
											? 'Committing...'
											: 'Approved applied control commit'}
									</button>
									<span class="text-xs text-cyan-900">
										No AI model is used in this write step.
									</span>
								</div>

								{#if appliedControlCommitDryRun}
									<div class="mt-3 rounded border bg-white p-3 text-sm">
										<div class="font-semibold">
											Step 4B dry-run status: {appliedControlCommitDryRun.status}
										</div>
										<p class="mt-1 text-xs text-slate-600">
											Dry-run is a preview only — nothing was written to the database.
										</p>
										<ul class="mt-2 list-disc pl-5">
											{#each appliedControlCommitDryRun.planned_actions ?? [] as action}
												<li>
								<span class="font-semibold">{humanizeActionName(action.action)}</span> &mdash; {action.detail}
							</li>
											{/each}
										</ul>
									</div>
								{/if}

								{#if appliedControlCommitResult}
									<div class="mt-3 grid gap-2 rounded border border-emerald-200 bg-emerald-50 p-3 text-sm">
										<div class="font-semibold">
											Step 4B commit status: {appliedControlCommitResult.status}
										</div>
										<p class="text-xs text-emerald-900">
											Approved deterministic write completed — only the counted records below were
											touched.
										</p>
										<div>
											Created: {appliedControlCommitResult.created_applied_controls?.length ?? 0}
										</div>
										<div>
											Reused: {appliedControlCommitResult.reused_applied_controls?.length ?? 0}
										</div>
										<div>
											Rejected: {appliedControlCommitResult.rejected_applied_controls?.length ?? 0}
										</div>
										<div>
											Deferred: {appliedControlCommitResult.deferred_applied_controls?.length ?? 0}
										</div>
										<div>
											Warnings: {appliedControlCommitResult.warnings?.length ?? 0}
										</div>
										<div>
											Blocking errors: {appliedControlCommitResult.blocking_errors?.length ?? 0}
										</div>
									</div>
									{#if appliedControlCommitResult.warnings?.length}
										<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
											{#each appliedControlCommitResult.warnings as warning}
												<li>{warning.detail ?? warning.message ?? warning.code}</li>
											{/each}
										</ul>
									{/if}
									{#if appliedControlCommitResult.blocking_errors?.length}
										<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
											{#each appliedControlCommitResult.blocking_errors as blockingError}
												<li>{blockingError.detail}</li>
											{/each}
										</ul>
									{/if}
								{/if}
							</div>
						</div>
					{/if}
				</div>
			{/if}

			{#if appliedControlCommitResult}
				<div class="mt-4 rounded border border-indigo-200 bg-indigo-50/60 p-3 text-sm text-indigo-950">
					<div class="font-semibold">Step 5A &middot; Evidence / Finding Suggestion</div>
					<p class="mt-1 text-indigo-900">
						<span class="font-semibold">AI suggestion only / no database write.</span>
						Step 5A drafts evidence requests, audit questions, and preliminary findings for review.
						No findings or evidence records are created until the approved Step 5B commit.
					</p>
					<div class="mt-3 flex flex-wrap items-center gap-3">
						<button
							class="btn btn-sm preset-filled-primary-500"
							type="button"
							disabled={loading !== null || !appliedControlCommitResult}
							onclick={() => runEvidenceFindingSuggestion()}
						>
							{loading === 'evidence-suggest'
								? 'Running...'
								: 'Run Local AI Evidence/Finding Suggestion'}
						</button>
						<span class="text-xs text-indigo-900">
							AI Provider: {humanizeProviderMode(evidenceFindingProviderMode)} &middot; No database
							writes occur in Step 5A.
						</span>
					</div>

					{#if evidenceFindingDraft}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">Step 5A suggestion summary</div>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Overall confidence: {formatConfidence(evidenceFindingDraft.overall_confidence)}
								</span>
								<span class="rounded bg-indigo-100 px-2 py-1 font-semibold text-indigo-900">
									Evidence requests: {evidenceFindingDraft.evidence_requests?.length ?? 0}
								</span>
								<span class="rounded bg-indigo-100 px-2 py-1 font-semibold text-indigo-900">
									Audit questions: {evidenceFindingDraft.audit_questions?.length ?? 0}
								</span>
								<span class="rounded bg-indigo-100 px-2 py-1 font-semibold text-indigo-900">
									Preliminary findings: {evidenceFindingDraft.preliminary_findings?.length ?? 0}
								</span>
								<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
									Warnings: {evidenceFindingDraft.warnings?.length ?? 0}
								</span>
							</div>
						</div>

						{#if evidenceFindingDraft.evidence_requests?.length}
							<div class="mt-3">
								<div class="font-semibold text-indigo-950">
									Evidence requests ({evidenceFindingDraft.evidence_requests.length})
								</div>
								<p class="text-xs text-indigo-900">
									Documents or artifacts the AI suggests collecting as audit evidence.
								</p>
								<div class="mt-2 grid gap-2">
									{#each evidenceFindingDraft.evidence_requests as request, index}
										<div class="rounded border bg-white p-3 text-xs text-slate-800">
											<div class="flex flex-wrap items-start justify-between gap-2">
												<div class="text-sm font-semibold text-slate-950">
													{displayEvidenceTitle(request, index)}
												</div>
												<div class="flex flex-wrap gap-1">
													<span class="rounded bg-slate-100 px-2 py-0.5 font-semibold text-slate-700">
														Confidence: {formatConfidence(request.confidence)}
													</span>
													{#if request.review_status}
														<span class="rounded bg-indigo-100 px-2 py-0.5 font-semibold text-indigo-900">
															{humanizeFieldLabel(request.review_status)}
														</span>
													{/if}
												</div>
											</div>
											{#if request.description}
												<div class="mt-1 text-slate-700">{request.description}</div>
											{/if}
											{#if request.rationale}
												<div class="mt-1">
													<span class="font-semibold">Rationale:</span>
													{request.rationale}
												</div>
											{/if}
											{#if request.linked_asset_ids?.length}
												<div class="mt-1">
													<span class="font-semibold">Linked assets:</span>
													{request.linked_asset_ids
														.map((assetId: string) => linkedAssetLabel(assetId))
														.join(', ')}
												</div>
											{/if}
											{#if request.linked_applied_control_ids?.length}
												<div class="mt-1">
													<span class="font-semibold">Linked controls:</span>
													{request.linked_applied_control_ids
														.map((controlId: string) => linkedControlLabel(controlId))
														.join(', ')}
												</div>
											{/if}
										</div>
									{/each}
								</div>
							</div>
						{/if}

						{#if evidenceFindingDraft.audit_questions?.length}
							<div class="mt-3">
								<div class="font-semibold text-indigo-950">
									Audit questions ({evidenceFindingDraft.audit_questions.length})
								</div>
								<p class="text-xs text-indigo-900">
									Questions the AI suggests asking during the audit interviews.
								</p>
								<div class="mt-2 grid gap-2">
									{#each evidenceFindingDraft.audit_questions as question, index}
										<div class="rounded border bg-white p-3 text-xs text-slate-800">
											<div class="flex flex-wrap items-start justify-between gap-2">
												<div class="text-sm font-semibold text-slate-950">
													{displayAuditQuestionTitle(question, index)}
												</div>
												<div class="flex flex-wrap gap-1">
													<span class="rounded bg-slate-100 px-2 py-0.5 font-semibold text-slate-700">
														Confidence: {formatConfidence(question.confidence)}
													</span>
													{#if question.review_status}
														<span class="rounded bg-indigo-100 px-2 py-0.5 font-semibold text-indigo-900">
															{humanizeFieldLabel(question.review_status)}
														</span>
													{/if}
												</div>
											</div>
											{#if question.rationale}
												<div class="mt-1">
													<span class="font-semibold">Rationale:</span>
													{question.rationale}
												</div>
											{/if}
											{#if question.linked_asset_ids?.length}
												<div class="mt-1">
													<span class="font-semibold">Linked assets:</span>
													{question.linked_asset_ids
														.map((assetId: string) => linkedAssetLabel(assetId))
														.join(', ')}
												</div>
											{/if}
											{#if question.linked_applied_control_ids?.length}
												<div class="mt-1">
													<span class="font-semibold">Linked controls:</span>
													{question.linked_applied_control_ids
														.map((controlId: string) => linkedControlLabel(controlId))
														.join(', ')}
												</div>
											{/if}
										</div>
									{/each}
								</div>
							</div>
						{/if}

						{#if evidenceFindingDraft.preliminary_findings?.length}
							<div class="mt-3">
								<div class="font-semibold text-indigo-950">
									Preliminary findings ({evidenceFindingDraft.preliminary_findings.length})
								</div>
								<p class="text-xs text-indigo-900">
									Draft findings the AI suggests investigating based on the known weaknesses.
								</p>
								<div class="mt-2 grid gap-2">
									{#each evidenceFindingDraft.preliminary_findings as finding, index}
										<div class="rounded border bg-white p-3 text-xs text-slate-800">
											<div class="flex flex-wrap items-start justify-between gap-2">
												<div class="text-sm font-semibold text-slate-950">
													{displayFindingTitle(finding, index)}
												</div>
												<div class="flex flex-wrap gap-1">
													{#if finding.severity}
														<span class="rounded bg-amber-100 px-2 py-0.5 font-semibold text-amber-900">
															Severity: {finding.severity}
														</span>
													{/if}
													<span class="rounded bg-slate-100 px-2 py-0.5 font-semibold text-slate-700">
														Confidence: {formatConfidence(finding.confidence)}
													</span>
													{#if finding.review_status}
														<span class="rounded bg-indigo-100 px-2 py-0.5 font-semibold text-indigo-900">
															{humanizeFieldLabel(finding.review_status)}
														</span>
													{/if}
												</div>
											</div>
											{#if finding.summary}
												<div class="mt-1 text-slate-700">{finding.summary}</div>
											{/if}
											{#if finding.rationale}
												<div class="mt-1">
													<span class="font-semibold">Rationale:</span>
													{finding.rationale}
												</div>
											{/if}
											{#if finding.related_weaknesses?.length}
												<div class="mt-1">
													<span class="font-semibold">Related weaknesses:</span>
													{finding.related_weaknesses.join('; ')}
												</div>
											{/if}
											{#if finding.linked_asset_ids?.length}
												<div class="mt-1">
													<span class="font-semibold">Linked assets:</span>
													{finding.linked_asset_ids
														.map((assetId: string) => linkedAssetLabel(assetId))
														.join(', ')}
												</div>
											{/if}
											{#if finding.linked_applied_control_ids?.length}
												<div class="mt-1">
													<span class="font-semibold">Linked controls:</span>
													{finding.linked_applied_control_ids
														.map((controlId: string) => linkedControlLabel(controlId))
														.join(', ')}
												</div>
											{/if}
										</div>
									{/each}
								</div>
							</div>
						{/if}

						{#if evidenceFindingDraft.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each evidenceFindingDraft.warnings as warning}
									<li>{warning.message ?? warning.detail ?? warning.code}</li>
								{/each}
							</ul>
						{/if}
					{/if}
				</div>
			{/if}

			{#if evidenceFindingDraft}
				<div class="mt-4 rounded border border-emerald-300 bg-emerald-50/60 p-3 text-sm text-emerald-950">
					<div class="font-semibold">Step 5B &middot; Evidence / Finding Commit</div>
					<p class="mt-1 text-emerald-900">
						<span class="font-semibold">No AI model is used / writes only after approval.</span>
						Select the Step 5A suggestions to keep, then dry-run to preview. Dry-run does not
						write. The approved commit writes deterministic records only for the items you
						selected and approved.
					</p>

					{#if evidenceFindingDraft.evidence_requests?.length}
						<div class="mt-3">
							<div class="font-semibold text-emerald-950">Evidence requests</div>
							<div class="mt-1 grid gap-1">
								{#each evidenceFindingDraft.evidence_requests as request, index}
									<label
										class="flex items-start gap-2 rounded border bg-white p-2 text-xs text-slate-800"
									>
										<input
											type="checkbox"
											bind:checked={selectedEvidenceRequestIds[request.temporary_id]}
										/>
										<span>
											<span class="font-semibold text-slate-950">
												{displayEvidenceTitle(request, index)}
											</span>
											{#if request.description || request.rationale}
												<span class="block text-slate-700">
													{request.description || request.rationale}
												</span>
											{/if}
											<span class="block text-slate-500">
												Confidence: {formatConfidence(request.confidence)} &middot; Will be created
												as a draft Evidence record.
											</span>
										</span>
									</label>
								{/each}
							</div>
						</div>
					{/if}

					{#if evidenceFindingDraft.audit_questions?.length}
						<div class="mt-3">
							<div class="font-semibold text-emerald-950">Audit questions</div>
							<div class="mt-1 grid gap-1">
								{#each evidenceFindingDraft.audit_questions as question, index}
									<label
										class="flex items-start gap-2 rounded border bg-white p-2 text-xs text-slate-800"
									>
										<input
											type="checkbox"
											bind:checked={selectedAuditQuestionIds[question.temporary_id]}
										/>
										<span>
											<span class="font-semibold text-slate-950">
												{displayAuditQuestionTitle(question, index)}
											</span>
											{#if question.rationale}
												<span class="block text-slate-700">{question.rationale}</span>
											{/if}
											<span class="block text-slate-500">
												Confidence: {formatConfidence(question.confidence)}
											</span>
										</span>
									</label>
								{/each}
							</div>
						</div>
					{/if}

					{#if evidenceFindingDraft.preliminary_findings?.length}
						<div class="mt-3">
							<div class="font-semibold text-emerald-950">Preliminary findings</div>
							<div class="mt-1 grid gap-1">
								{#each evidenceFindingDraft.preliminary_findings as finding, index}
									<label
										class="flex items-start gap-2 rounded border bg-white p-2 text-xs text-slate-800"
									>
										<input
											type="checkbox"
											bind:checked={selectedPreliminaryFindingIds[finding.temporary_id]}
										/>
										<span>
											<span class="font-semibold text-slate-950">
												{displayFindingTitle(finding, index)}
											</span>
											{#if finding.summary || finding.rationale || finding.description}
												<span class="block text-slate-700">
													{finding.summary || finding.rationale || finding.description}
												</span>
											{/if}
											<span class="block text-slate-500">
												{#if finding.severity}Severity: {finding.severity} &middot;{/if}
												Confidence: {formatConfidence(finding.confidence)}
											</span>
										</span>
									</label>
								{/each}
							</div>
						</div>
					{/if}

					<div class="mt-3 flex flex-wrap items-center gap-3">
						<button
							class="btn btn-sm preset-tonal-primary"
							type="button"
							disabled={loading !== null}
							onclick={() => runEvidenceFindingCommit(true)}
						>
							{loading === 'evidence-commit-dry-run' ? 'Dry-running...' : 'Step 5B dry-run'}
						</button>
						<label class="flex items-center gap-2 text-sm">
							<input type="checkbox" bind:checked={evidenceFindingCommitApproved} />
							<span>
								I approve deterministic Step 5B decisions for selected evidence/finding suggestions
							</span>
						</label>
						<button
							class="btn btn-sm preset-filled-primary-500"
							type="button"
							disabled={loading !== null || !evidenceFindingCommitApproved}
							onclick={() => runEvidenceFindingCommit(false)}
						>
							{loading === 'evidence-commit' ? 'Committing...' : 'Approved evidence/finding commit'}
						</button>
						<span class="text-xs text-emerald-900">No AI model is used in this write step.</span>
					</div>

					{#if evidenceFindingCommitDryRun}
						<div class="mt-3 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">
								Step 5B dry-run status: {evidenceFindingCommitDryRun.status}
							</div>
							<p class="mt-1 text-xs text-slate-600">
								Dry-run is a preview only — nothing was written to the database. The plan below
								shows what an approved commit would do.
							</p>
							{#if evidenceFindingCommitDryRun.counts}
								<div class="mt-2 flex flex-wrap gap-2 text-xs">
									<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
										Rejected: {evidenceFindingCommitDryRun.counts.rejected ?? 0}
									</span>
									<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
										Deferred: {evidenceFindingCommitDryRun.counts.deferred ?? 0}
									</span>
									<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
										Skipped: {evidenceFindingCommitDryRun.counts.skipped ?? 0}
									</span>
								</div>
							{/if}
							{#if evidenceFindingCommitDryRun.planned_actions?.length}
								<div class="mt-2 text-xs font-semibold text-slate-950">Planned actions</div>
								<ul class="mt-1 list-disc pl-5 text-xs text-slate-800">
									{#each evidenceFindingCommitDryRun.planned_actions as action}
										<li>
											<span class="font-semibold"
												>{humanizeFieldLabel(action.record_type ?? action.kind)}</span
											>
											{#if action.name}"{action.name}"{/if}
											&mdash; {humanizeActionName(action.action)} &rarr;
											{humanizeFieldLabel(action.status)}: {action.detail}
										</li>
									{/each}
								</ul>
							{/if}
							{#if evidenceFindingCommitDryRun.warnings?.length}
								<div class="mt-2 text-xs font-semibold text-amber-800">Warnings</div>
								<ul class="mt-1 list-disc pl-5 text-xs text-amber-800">
									{#each evidenceFindingCommitDryRun.warnings as warning}
										<li>{warning.detail ?? warning.message ?? warning.code}</li>
									{/each}
								</ul>
							{/if}
							{#if evidenceFindingCommitDryRun.blocking_errors?.length}
								<div class="mt-2 text-xs font-semibold text-red-700">
									Blocking errors (commit will be refused until resolved)
								</div>
								<ul class="mt-1 list-disc pl-5 text-xs text-red-700">
									{#each evidenceFindingCommitDryRun.blocking_errors as blockingError}
										<li>{blockingError.detail}</li>
									{/each}
								</ul>
							{/if}
						</div>
					{/if}

					{#if evidenceFindingCommitResult}
						<div class="mt-3 grid gap-2 rounded border border-emerald-200 bg-white p-3 text-sm">
							<div class="font-semibold">
								Step 5B commit status: {evidenceFindingCommitResult.status}
							</div>
							<p class="text-xs text-emerald-900">
								Approved commit complete — deterministic records only, no AI model involved in
								this write.
							</p>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
									Created: {evidenceFindingCommitResult.counts?.created ?? 0}
								</span>
								<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
									Reused: {evidenceFindingCommitResult.counts?.reused ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Rejected: {evidenceFindingCommitResult.counts?.rejected ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Deferred: {evidenceFindingCommitResult.counts?.deferred ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Skipped: {evidenceFindingCommitResult.counts?.skipped ?? 0}
								</span>
								<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
									Warnings: {evidenceFindingCommitResult.warnings?.length ?? 0}
								</span>
								<span class="rounded bg-red-100 px-2 py-1 font-semibold text-red-800">
									Blocking errors: {evidenceFindingCommitResult.blocking_errors?.length ?? 0}
								</span>
							</div>
							{#if evidenceFindingCommitResult.created_records?.length}
								<div class="text-xs font-semibold text-emerald-950">Created records</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each evidenceFindingCommitResult.created_records as record}
										<li>{humanizeFieldLabel(record.record_type)}: {record.name}</li>
									{/each}
								</ul>
							{/if}
							{#if evidenceFindingCommitResult.reused_records?.length}
								<div class="text-xs font-semibold text-emerald-950">Reused existing records</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each evidenceFindingCommitResult.reused_records as record}
										<li>{humanizeFieldLabel(record.record_type)}: {record.name}</li>
									{/each}
								</ul>
							{/if}
						</div>
						{#if evidenceFindingCommitResult.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each evidenceFindingCommitResult.warnings as warning}
									<li>{warning.detail ?? warning.message ?? warning.code}</li>
								{/each}
							</ul>
						{/if}
						{#if evidenceFindingCommitResult.blocking_errors?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
								{#each evidenceFindingCommitResult.blocking_errors as blockingError}
									<li>{blockingError.detail}</li>
								{/each}
							</ul>
						{/if}
					{/if}
				</div>
			{/if}

			{#if evidenceFindingDraft}
				<div class="mt-4 rounded border border-violet-200 bg-violet-50/60 p-3 text-sm text-violet-950">
					<div class="font-semibold">Step 6A &middot; Remediation Action Suggestion</div>
					<p class="mt-1 text-violet-900">
						<span class="font-semibold">AI suggestion only / no database write.</span>
						Step 6A drafts remediation actions for review. No remediation records are created in this
						step.
					</p>
					<div class="mt-3 flex flex-wrap items-center gap-3">
						<button
							class="btn btn-sm preset-filled-primary-500"
							type="button"
							disabled={loading !== null}
							onclick={() => runRemediationActionSuggestion()}
						>
							{loading === 'remediation-suggest'
								? 'Running...'
								: 'Run Local AI Remediation Suggestion'}
						</button>
						<span class="text-xs text-violet-900">
							AI Provider: {humanizeProviderMode(remediationActionProviderMode)} &middot; No database
							writes occur in Step 6A.
						</span>
					</div>

					{#if remediationActionDraft}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">Step 6A suggestion summary</div>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Overall confidence: {formatConfidence(remediationActionDraft.overall_confidence)}
								</span>
								<span class="rounded bg-violet-100 px-2 py-1 font-semibold text-violet-900">
									Remediation actions: {remediationActionDraft.remediation_actions?.length ?? 0}
								</span>
								<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
									Warnings: {remediationActionDraft.warnings?.length ?? 0}
								</span>
							</div>
						</div>

						{#if remediationActionDraft.remediation_actions?.length}
							<div class="mt-3">
								<div class="font-semibold text-violet-950">
									Remediation actions ({remediationActionDraft.remediation_actions.length})
								</div>
								<p class="text-xs text-violet-900">
									Corrective actions the AI suggests for the preliminary findings. Advisory drafts
									only.
								</p>
								<div class="mt-2 grid gap-2">
									{#each remediationActionDraft.remediation_actions as action}
										<div class="rounded border bg-white p-3 text-xs text-slate-800">
											<div class="flex flex-wrap items-start justify-between gap-2">
												<div class="text-sm font-semibold text-slate-950">{action.title}</div>
												<div class="flex flex-wrap gap-1">
													{#if action.priority}
														<span
															class="rounded px-2 py-0.5 font-semibold {remediationPriorityBadgeClass(
																action.priority
															)}"
														>
															Priority: {humanizeFieldLabel(action.priority)}
														</span>
													{/if}
													<span class="rounded bg-slate-100 px-2 py-0.5 font-semibold text-slate-700">
														Confidence: {formatConfidence(action.confidence)}
													</span>
													{#if action.review_status}
														<span class="rounded bg-violet-100 px-2 py-0.5 font-semibold text-violet-900">
															{humanizeFieldLabel(action.review_status)}
														</span>
													{/if}
												</div>
											</div>
											<div class="mt-1 flex flex-wrap gap-3">
												{#if action.suggested_owner}
													<div>
														<span class="font-semibold">Suggested owner:</span>
														{action.suggested_owner}
													</div>
												{/if}
												{#if action.target_timeline}
													<div>
														<span class="font-semibold">Target timeline:</span>
														{action.target_timeline}
													</div>
												{/if}
											</div>
											{#if action.description}
												<div class="mt-1 text-slate-700">{action.description}</div>
											{/if}
											{#if action.rationale}
												<div class="mt-1">
													<span class="font-semibold">Rationale:</span>
													{action.rationale}
												</div>
											{/if}
											{#if action.linked_finding_title || action.linked_finding_reference}
												<div class="mt-1">
													<span class="font-semibold">Linked finding:</span>
													{action.linked_finding_title || action.linked_finding_reference}
												</div>
											{/if}
											{#if action.linked_asset_title || action.linked_asset_reference}
												<div class="mt-1">
													<span class="font-semibold">Linked asset:</span>
													{action.linked_asset_title || action.linked_asset_reference}
												</div>
											{/if}
											{#if action.linked_control_title || action.linked_control_reference}
												<div class="mt-1">
													<span class="font-semibold">Linked control:</span>
													{action.linked_control_title || action.linked_control_reference}
												</div>
											{/if}
											{#if action.success_criteria?.length}
												<div class="mt-1">
													<span class="font-semibold">Success criteria:</span>
													<ul class="list-disc pl-5">
														{#each action.success_criteria as criterion}
															<li>{criterion}</li>
														{/each}
													</ul>
												</div>
											{/if}
											{#if action.required_follow_up_evidence?.length}
												<div class="mt-1">
													<span class="font-semibold">Required follow-up evidence:</span>
													<ul class="list-disc pl-5">
														{#each action.required_follow_up_evidence as evidenceItem}
															<li>{evidenceItem}</li>
														{/each}
													</ul>
												</div>
											{/if}
										</div>
									{/each}
								</div>
							</div>
						{/if}

						{#if remediationActionDraft.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each remediationActionDraft.warnings as warning}
									<li>{warning.message ?? warning.detail ?? warning.code}</li>
								{/each}
							</ul>
						{/if}

						{#if remediationActionDraft.ambiguity_flags?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each remediationActionDraft.ambiguity_flags as flag}
									<li>{flag.message ?? flag.code}</li>
								{/each}
							</ul>
						{/if}
					{/if}
				</div>
			{/if}

			{#if remediationActionDraft?.remediation_actions?.length}
				<div class="mt-4 rounded border border-emerald-300 bg-emerald-50/60 p-3 text-sm text-emerald-950">
					<div class="font-semibold">Step 6B &middot; Remediation Action Commit</div>
					<p class="mt-1 text-emerald-900">
						<span class="font-semibold">No AI model is used / writes only after approval.</span>
						Select the Step 6A remediation actions to keep, then dry-run to preview. Dry-run does not
						write. The approved commit writes deterministic records only for selected and approved
						remediation actions.
					</p>

					<div class="mt-3 grid gap-2">
						{#each remediationActionDraft.remediation_actions as action}
							<label class="flex items-start gap-2 rounded border bg-white p-2 text-xs">
								<input
									type="checkbox"
									bind:checked={selectedRemediationActionIds[action.temporary_id]}
								/>
								<span>
									<span class="font-semibold">{action.title}</span>
									<span class="text-slate-600">
										&middot; Priority: {humanizeFieldLabel(action.priority)} &middot; Confidence: {formatConfidence(
											action.confidence
										)}
									</span>
								</span>
							</label>
						{/each}
					</div>

					<div class="mt-3 flex flex-wrap items-center gap-3">
						<button
							class="btn btn-sm preset-tonal"
							type="button"
							disabled={loading !== null || !selectedRemediationActions.length}
							onclick={() => runRemediationActionCommit(true)}
						>
							{loading === 'remediation-commit-dry-run' ? 'Dry-running...' : 'Step 6B dry-run'}
						</button>
						<label class="flex items-center gap-2 text-xs">
							<input type="checkbox" bind:checked={remediationCommitApproved} />
							<span>
								I approve deterministic Step 6B decisions for selected remediation actions
							</span>
						</label>
						<button
							class="btn btn-sm preset-filled-error-500"
							type="button"
							disabled={loading !== null ||
								!remediationCommitApproved ||
								!remediationDryRunSucceeded ||
								!selectedRemediationActions.length}
							onclick={() => runRemediationActionCommit(false)}
						>
							{loading === 'remediation-commit'
								? 'Committing...'
								: 'Approved remediation action commit'}
						</button>
						<span class="text-xs text-emerald-900">No AI model is used in this write step.</span>
					</div>

					{#if remediationCommitDryRun}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">
								Step 6B dry-run status: {humanizeFieldLabel(remediationCommitDryRun.commit_status)}
							</div>
							<p class="text-xs text-slate-700">
								Dry-run only previews the deterministic write. Nothing was written.
							</p>
							{#if remediationCommitDryRun.planned_actions?.length}
								<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each remediationCommitDryRun.planned_actions as action}
										<li>
											{action.target_name ?? action.source_temporary_id}:
											{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(
												action.status
											)} &middot; {action.detail}
										</li>
									{/each}
								</ul>
							{/if}
							{#if remediationCommitDryRun.rejected_records?.length || remediationCommitDryRun.deferred_records?.length || remediationCommitDryRun.skipped_records?.length}
								<div class="flex flex-wrap gap-2 text-xs">
									<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
										Rejected: {remediationCommitDryRun.rejected_records?.length ?? 0}
									</span>
									<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
										Deferred: {remediationCommitDryRun.deferred_records?.length ?? 0}
									</span>
									<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
										Skipped: {remediationCommitDryRun.skipped_records?.length ?? 0}
									</span>
								</div>
							{/if}
						</div>
						{#if remediationCommitDryRun.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each remediationCommitDryRun.warnings as warning}
									<li>{warning.detail ?? warning.message ?? warning.code}</li>
								{/each}
							</ul>
						{/if}
						{#if remediationCommitDryRun.blocking_errors?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
								{#each remediationCommitDryRun.blocking_errors as blockingError}
									<li>{blockingError.detail}</li>
								{/each}
							</ul>
						{/if}
					{/if}

					{#if remediationCommitResult}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">
								Step 6B commit status: {humanizeFieldLabel(remediationCommitResult.commit_status)}
							</div>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
									Created: {remediationCommitResult.created_records?.length ?? 0}
								</span>
								<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
									Reused: {remediationCommitResult.reused_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Rejected: {remediationCommitResult.rejected_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Deferred: {remediationCommitResult.deferred_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Skipped: {remediationCommitResult.skipped_records?.length ?? 0}
								</span>
								<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
									Warnings: {remediationCommitResult.warnings?.length ?? 0}
								</span>
								<span class="rounded bg-red-100 px-2 py-1 font-semibold text-red-900">
									Blocking errors: {remediationCommitResult.blocking_errors?.length ?? 0}
								</span>
							</div>
							{#if remediationCommitResult.created_records?.length}
								<div class="text-xs font-semibold text-emerald-950">Created records</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each remediationCommitResult.created_records as record}
										<li>{humanizeFieldLabel(record.record_type)}: {record.name}</li>
									{/each}
								</ul>
							{/if}
							{#if remediationCommitResult.reused_records?.length}
								<div class="text-xs font-semibold text-emerald-950">Reused existing records</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each remediationCommitResult.reused_records as record}
										<li>{humanizeFieldLabel(record.record_type)}: {record.name}</li>
									{/each}
								</ul>
							{/if}
							{#if remediationCommitResult.planned_actions?.length}
								<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each remediationCommitResult.planned_actions as action}
										<li>
											{action.target_name ?? action.source_temporary_id}:
											{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(
												action.status
											)}
										</li>
									{/each}
								</ul>
							{/if}
						</div>
						{#if remediationCommitResult.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each remediationCommitResult.warnings as warning}
									<li>{warning.detail ?? warning.message ?? warning.code}</li>
								{/each}
							</ul>
						{/if}
						{#if remediationCommitResult.blocking_errors?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
								{#each remediationCommitResult.blocking_errors as blockingError}
									<li>{blockingError.detail}</li>
								{/each}
							</ul>
						{/if}
					{/if}
				</div>
			{/if}

			{#if remediationActionDraft}
				<div class="mt-4 rounded border border-sky-200 bg-sky-50/60 p-3 text-sm text-sky-950">
					<div class="font-semibold">Step 7A &middot; Framework Control Mapping Suggestion</div>
					<p class="mt-1 text-sky-900">
						<span class="font-semibold">AI suggestion only / no database write.</span>
						Step 7A suggests mappings to existing framework controls for review. No framework
						controls or mappings are created in this step.
					</p>
					<div class="mt-3 flex flex-wrap items-center gap-3">
						<button
							class="btn btn-sm preset-filled-primary-500"
							type="button"
							disabled={loading !== null}
							onclick={() => runFrameworkControlMappingSuggestion()}
						>
							{loading === 'framework-mapping-suggest'
								? 'Running...'
								: 'Run Local AI Framework Mapping Suggestion'}
						</button>
						<span class="text-xs text-sky-900">
							AI Provider: {humanizeProviderMode(frameworkControlMappingProviderMode)} &middot; No
							database writes occur in Step 7A.
						</span>
					</div>

					{#if frameworkControlMappingDraft}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">Step 7A suggestion summary</div>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Overall confidence: {formatConfidence(
										frameworkControlMappingDraft.overall_confidence
									)}
								</span>
								<span class="rounded bg-sky-100 px-2 py-1 font-semibold text-sky-900">
									Framework mappings: {frameworkControlMappingDraft.framework_control_mappings
										?.length ?? 0}
								</span>
								<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
									Warnings: {frameworkControlMappingDraft.warnings?.length ?? 0}
								</span>
							</div>
						</div>

						{#if frameworkControlMappingDraft.framework_control_mappings?.length}
							<div class="mt-3">
								<div class="font-semibold text-sky-950">
									Framework control mappings ({frameworkControlMappingDraft
										.framework_control_mappings.length})
								</div>
								<p class="text-xs text-sky-900">
									Existing framework controls the AI considers relevant. Advisory drafts only; no
									framework control is created.
								</p>
								<div class="mt-2 grid gap-2">
									{#each frameworkControlMappingDraft.framework_control_mappings as mapping}
										<div class="rounded border bg-white p-3 text-xs text-slate-800">
											<div class="flex flex-wrap items-start justify-between gap-2">
												<div class="text-sm font-semibold text-slate-950">
													{#if mapping.framework_control_code}
														<span class="text-slate-600">{mapping.framework_control_code}</span>
														&middot;
													{/if}
													{mapping.framework_control_title}
												</div>
												<div class="flex flex-wrap gap-1">
													<span class="rounded bg-sky-100 px-2 py-0.5 font-semibold text-sky-900">
														{humanizeFieldLabel(mapping.mapping_type)}
													</span>
													<span class="rounded bg-slate-100 px-2 py-0.5 font-semibold text-slate-700">
														Confidence: {formatConfidence(mapping.confidence)}
													</span>
													{#if mapping.review_status}
														<span
															class="rounded bg-violet-100 px-2 py-0.5 font-semibold text-violet-900"
														>
															{humanizeFieldLabel(mapping.review_status)}
														</span>
													{/if}
												</div>
											</div>
											{#if mapping.framework_name}
												<div class="mt-1">
													<span class="font-semibold">Framework:</span>
													{mapping.framework_name}
												</div>
											{/if}
											{#if mapping.framework_control_description}
												<div class="mt-1 text-slate-700">
													{mapping.framework_control_description}
												</div>
											{/if}
											{#if mapping.rationale}
												<div class="mt-1">
													<span class="font-semibold">Rationale:</span>
													{mapping.rationale}
												</div>
											{/if}
											{#if mapping.linked_finding_title || mapping.linked_finding_reference}
												<div class="mt-1">
													<span class="font-semibold">Linked finding:</span>
													{mapping.linked_finding_title || mapping.linked_finding_reference}
												</div>
											{/if}
											{#if mapping.linked_applied_control_title || mapping.linked_applied_control_reference}
												<div class="mt-1">
													<span class="font-semibold">Linked applied control:</span>
													{mapping.linked_applied_control_title ||
														mapping.linked_applied_control_reference}
												</div>
											{/if}
											{#if mapping.linked_remediation_action_title || mapping.linked_remediation_action_reference}
												<div class="mt-1">
													<span class="font-semibold">Linked remediation action:</span>
													{mapping.linked_remediation_action_title ||
														mapping.linked_remediation_action_reference}
												</div>
											{/if}
											{#if mapping.evidence_needed?.length}
												<div class="mt-1">
													<span class="font-semibold">Evidence needed:</span>
													<ul class="list-disc pl-5">
														{#each mapping.evidence_needed as evidenceItem}
															<li>{evidenceItem}</li>
														{/each}
													</ul>
												</div>
											{/if}
										</div>
									{/each}
								</div>
							</div>
						{/if}

						{#if frameworkControlMappingDraft.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each frameworkControlMappingDraft.warnings as warning}
									<li>{warning.message ?? warning.detail ?? warning.code}</li>
								{/each}
							</ul>
						{/if}

						{#if frameworkControlMappingDraft.ambiguity_flags?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each frameworkControlMappingDraft.ambiguity_flags as flag}
									<li>{flag.message ?? flag.code}</li>
								{/each}
							</ul>
						{/if}
					{/if}
				</div>
			{/if}

			{#if frameworkControlMappingDraft?.framework_control_mappings?.length}
				<div class="mt-4 rounded border border-emerald-300 bg-emerald-50/60 p-3 text-sm text-emerald-950">
					<div class="font-semibold">Step 7B &middot; Framework Control Mapping Commit</div>
					<p class="mt-1 text-emerald-900">
						<span class="font-semibold">No AI model is used / writes only after approval.</span>
						Select the Step 7A framework mappings to keep, then dry-run to preview. The approved
						commit writes deterministic mappings only for selected and approved items.
					</p>

					{#if frameworkMappingUsedCsvFallback}
						<p class="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-900">
							These controls were matched from the read-only framework export file, not from the
							database, because the selected audit's framework has no assessable requirement nodes
							loaded. Step 7B never creates framework controls, so the dry-run will block. To get a
							committable mapping: load the framework library from the Libraries page, then run
							Step 2 for a new case against that loaded framework.
						</p>
					{/if}

					<div class="mt-3 grid gap-2">
						{#each frameworkControlMappingDraft.framework_control_mappings as mapping}
							<label class="flex items-start gap-2 rounded border bg-white p-2 text-xs">
								<input
									type="checkbox"
									bind:checked={selectedFrameworkMappingIds[mapping.temporary_id]}
								/>
								<span>
									<span class="font-semibold">
										{#if mapping.framework_control_code}
											{mapping.framework_control_code} &middot;
										{/if}
										{mapping.framework_control_title}
									</span>
									<span class="text-slate-600">
										&middot; {humanizeFieldLabel(mapping.mapping_type)} &middot; Confidence: {formatConfidence(
											mapping.confidence
										)}
									</span>
								</span>
							</label>
						{/each}
					</div>

					<div class="mt-3 flex flex-wrap items-center gap-3">
						<button
							class="btn btn-sm preset-tonal"
							type="button"
							disabled={loading !== null || !selectedFrameworkMappings.length}
							onclick={() => runFrameworkControlMappingCommit(true)}
						>
							{loading === 'framework-mapping-commit-dry-run'
								? 'Dry-running...'
								: 'Step 7B dry-run'}
						</button>
						<label class="flex items-center gap-2 text-xs">
							<input type="checkbox" bind:checked={frameworkMappingCommitApproved} />
							<span>
								I approve deterministic Step 7B decisions for selected framework control mappings
							</span>
						</label>
						<button
							class="btn btn-sm preset-filled-error-500"
							type="button"
							disabled={loading !== null ||
								!frameworkMappingCommitApproved ||
								!frameworkMappingDryRunSucceeded ||
								!selectedFrameworkMappings.length}
							onclick={() => runFrameworkControlMappingCommit(false)}
						>
							{loading === 'framework-mapping-commit'
								? 'Committing...'
								: 'Approved framework mapping commit'}
						</button>
						<span class="text-xs text-emerald-900">No AI model is used in this write step.</span>
					</div>

					{#if frameworkMappingCommitDryRun}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">
								Step 7B dry-run status: {humanizeFieldLabel(
									frameworkMappingCommitDryRun.commit_status
								)}
							</div>
							<p class="text-xs text-slate-700">
								Dry-run only previews the deterministic write. Nothing was written.
							</p>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Rejected: {frameworkMappingCommitDryRun.rejected_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Deferred: {frameworkMappingCommitDryRun.deferred_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Skipped: {frameworkMappingCommitDryRun.skipped_records?.length ?? 0}
								</span>
							</div>
							{#if frameworkMappingCommitDryRun.planned_actions?.length}
								<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each frameworkMappingCommitDryRun.planned_actions as action}
										<li>
											{action.target_name ?? action.source_temporary_id}:
											{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(
												action.status
											)} &middot; {action.detail}
										</li>
									{/each}
								</ul>
							{/if}
						</div>
						{#if frameworkMappingCommitDryRun.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each frameworkMappingCommitDryRun.warnings as warning}
									<li>{warning.detail ?? warning.message ?? warning.code}</li>
								{/each}
							</ul>
						{/if}
						{#if frameworkMappingCommitDryRun.blocking_errors?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
								{#each frameworkMappingCommitDryRun.blocking_errors as blockingError}
									<li>{blockingError.detail}</li>
								{/each}
							</ul>
						{/if}
					{/if}

					{#if frameworkMappingCommitResult}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">
								Step 7B commit status: {humanizeFieldLabel(
									frameworkMappingCommitResult.commit_status
								)}
							</div>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
									Created: {frameworkMappingCommitResult.created_records?.length ?? 0}
								</span>
								<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
									Reused: {frameworkMappingCommitResult.reused_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Rejected: {frameworkMappingCommitResult.rejected_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Deferred: {frameworkMappingCommitResult.deferred_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Skipped: {frameworkMappingCommitResult.skipped_records?.length ?? 0}
								</span>
								<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
									Warnings: {frameworkMappingCommitResult.warnings?.length ?? 0}
								</span>
								<span class="rounded bg-red-100 px-2 py-1 font-semibold text-red-900">
									Blocking errors: {frameworkMappingCommitResult.blocking_errors?.length ?? 0}
								</span>
							</div>
							{#if frameworkMappingCommitResult.created_records?.length}
								<div class="text-xs font-semibold text-emerald-950">Created mappings</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each frameworkMappingCommitResult.created_records as record}
										<li>{humanizeFieldLabel(record.record_type)}: {record.name}</li>
									{/each}
								</ul>
							{/if}
							{#if frameworkMappingCommitResult.reused_records?.length}
								<div class="text-xs font-semibold text-emerald-950">Reused existing mappings</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each frameworkMappingCommitResult.reused_records as record}
										<li>{humanizeFieldLabel(record.record_type)}: {record.name}</li>
									{/each}
								</ul>
							{/if}
							{#if frameworkMappingCommitResult.planned_actions?.length}
								<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each frameworkMappingCommitResult.planned_actions as action}
										<li>
											{action.target_name ?? action.source_temporary_id}:
											{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(
												action.status
											)}
										</li>
									{/each}
								</ul>
							{/if}
						</div>
						{#if frameworkMappingCommitResult.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each frameworkMappingCommitResult.warnings as warning}
									<li>{warning.detail ?? warning.message ?? warning.code}</li>
								{/each}
							</ul>
						{/if}
						{#if frameworkMappingCommitResult.blocking_errors?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
								{#each frameworkMappingCommitResult.blocking_errors as blockingError}
									<li>{blockingError.detail}</li>
								{/each}
							</ul>
						{/if}
					{/if}
				</div>
			{/if}

			{#if frameworkControlMappingDraft}
				<div class="mt-4 rounded border border-sky-200 bg-sky-50/60 p-3 text-sm text-sky-950">
					<div class="font-semibold">Step 8A &middot; Risk Scenario Suggestion</div>
					<p class="mt-1 text-sky-900">
						<span class="font-semibold">AI suggestion only / no database write.</span>
						Step 8A drafts risk scenarios for review. No risk records are created, no risk is
						accepted or treated, and no risk is closed in this step.
					</p>
					<div class="mt-3 flex flex-wrap items-center gap-3">
						<button
							class="btn btn-sm preset-filled-primary-500"
							type="button"
							disabled={loading !== null}
							onclick={() => runRiskScenarioSuggestion()}
						>
							{loading === 'risk-scenario-suggest'
								? 'Running...'
								: 'Run Local AI Risk Scenario Suggestion'}
						</button>
						<span class="text-xs text-sky-900">
							AI Provider: {humanizeProviderMode(riskScenarioProviderMode)} &middot; No database
							writes occur in Step 8A.
						</span>
					</div>

					{#if riskScenarioDraft}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">Step 8A suggestion summary</div>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Overall confidence: {formatConfidence(riskScenarioDraft.overall_confidence)}
								</span>
								<span class="rounded bg-sky-100 px-2 py-1 font-semibold text-sky-900">
									Risk scenarios: {riskScenarioDraft.risk_scenarios?.length ?? 0}
								</span>
								<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
									Warnings: {riskScenarioDraft.warnings?.length ?? 0}
								</span>
							</div>
						</div>

						{#if riskScenarioDraft.risk_scenarios?.length}
							<div class="mt-3">
								<div class="font-semibold text-sky-950">
									Risk scenarios ({riskScenarioDraft.risk_scenarios.length})
								</div>
								<p class="text-xs text-sky-900">
									Advisory drafts only. Likelihood, impact, and risk level are review labels, not
									platform risk ratings.
								</p>
								<div class="mt-2 grid gap-2">
									{#each riskScenarioDraft.risk_scenarios as scenario}
										<div class="rounded border bg-white p-3 text-xs text-slate-800">
											<div class="flex flex-wrap items-start justify-between gap-2">
												<div class="text-sm font-semibold text-slate-950">{scenario.title}</div>
												<div class="flex flex-wrap gap-1">
													<span class="rounded bg-sky-100 px-2 py-0.5 font-semibold text-sky-900">
														Likelihood: {humanizeFieldLabel(scenario.likelihood)}
													</span>
													<span class="rounded bg-orange-100 px-2 py-0.5 font-semibold text-orange-900">
														Impact: {humanizeFieldLabel(scenario.impact)}
													</span>
													<span class="rounded bg-red-100 px-2 py-0.5 font-semibold text-red-900">
														Risk level: {humanizeFieldLabel(scenario.risk_level)}
													</span>
													<span class="rounded bg-slate-100 px-2 py-0.5 font-semibold text-slate-700">
														Confidence: {formatConfidence(scenario.confidence)}
													</span>
													{#if scenario.review_status}
														<span
															class="rounded bg-violet-100 px-2 py-0.5 font-semibold text-violet-900"
														>
															{humanizeFieldLabel(scenario.review_status)}
														</span>
													{/if}
												</div>
											</div>
											{#if scenario.description}
												<div class="mt-1 text-slate-700">{scenario.description}</div>
											{/if}
											{#if scenario.threat}
												<div class="mt-1"><span class="font-semibold">Threat:</span> {scenario.threat}</div>
											{/if}
											{#if scenario.vulnerability}
												<div class="mt-1">
													<span class="font-semibold">Vulnerability:</span>
													{scenario.vulnerability}
												</div>
											{/if}
											{#if scenario.impact_description}
												<div class="mt-1">
													<span class="font-semibold">Potential impact:</span>
													{scenario.impact_description}
												</div>
											{/if}
											{#if scenario.asset_title || scenario.asset_reference}
												<div class="mt-1">
													<span class="font-semibold">Asset:</span>
													{scenario.asset_title || scenario.asset_reference}
												</div>
											{/if}
											{#if scenario.linked_finding_title || scenario.linked_finding_reference}
												<div class="mt-1">
													<span class="font-semibold">Linked finding:</span>
													{scenario.linked_finding_title || scenario.linked_finding_reference}
												</div>
											{/if}
											{#if scenario.linked_applied_control_title || scenario.linked_applied_control_reference}
												<div class="mt-1">
													<span class="font-semibold">Linked applied control:</span>
													{scenario.linked_applied_control_title ||
														scenario.linked_applied_control_reference}
												</div>
											{/if}
											{#if scenario.linked_framework_control_title || scenario.linked_framework_control_code}
												<div class="mt-1">
													<span class="font-semibold">Linked framework control:</span>
													{scenario.linked_framework_control_code}
													{scenario.linked_framework_control_title}
												</div>
											{/if}
											{#if scenario.rationale}
												<div class="mt-1">
													<span class="font-semibold">Rationale:</span>
													{scenario.rationale}
												</div>
											{/if}
											{#if scenario.recommended_next_steps?.length}
												<div class="mt-1">
													<span class="font-semibold">Recommended next steps:</span>
													<ul class="list-disc pl-5">
														{#each scenario.recommended_next_steps as nextStep}
															<li>{nextStep}</li>
														{/each}
													</ul>
												</div>
											{/if}
										</div>
									{/each}
								</div>
							</div>
						{/if}

						{#if riskScenarioDraft.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each riskScenarioDraft.warnings as warning}
									<li>{warning.message ?? warning.detail ?? warning.code}</li>
								{/each}
							</ul>
						{/if}

						{#if riskScenarioDraft.ambiguity_flags?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each riskScenarioDraft.ambiguity_flags as flag}
									<li>{flag.message ?? flag.code}</li>
								{/each}
							</ul>
						{/if}
					{/if}
				</div>
			{/if}

			{#if riskScenarioDraft?.risk_scenarios?.length}
				<div class="mt-4 rounded border border-emerald-300 bg-emerald-50/60 p-3 text-sm text-emerald-950">
					<div class="font-semibold">Step 8B &middot; Risk Scenario Commit</div>
					<p class="mt-1 text-emerald-900">
						<span class="font-semibold">No AI model is used / writes only after approval.</span>
						Select the Step 8A risk scenarios to keep, then dry-run to preview. The approved commit
						creates unrated risk scenarios under the existing risk assessment; no risk rating,
						treatment, or acceptance is recorded.
					</p>

					<!-- A RiskScenario always belongs to an existing RiskAssessment, and Step 8B never
					     creates one. Step 2 only creates a RiskAssessment when it was explicitly
					     requested there, so the reference is surfaced here as a required field: it is
					     prefilled from the Step 2 handoff when one exists and can otherwise be pasted. -->
					<label class="mt-3 grid gap-1">
						<span class="text-sm font-semibold">
							Risk Assessment ID <span class="text-red-700">(required for Step 8B)</span>
						</span>
						<input
							class="input"
							placeholder="UUID of an existing Risk Assessment"
							bind:value={setupReference.risk_assessment_id}
						/>
					</label>
					{#if !setupReference.risk_assessment_id}
						<p class="mt-2 rounded border border-amber-300 bg-amber-50 p-2 text-xs text-amber-900">
							No Risk Assessment is linked to this case yet, so Step 8B cannot run. A risk scenario
							can only be created under an existing risk assessment, and Step 8B never creates one.
							Either re-run Step 2 with "create risk assessment" enabled (it needs a Risk Matrix
							ID), or paste the ID of an existing Risk Assessment above.
						</p>
					{/if}

					<div class="mt-3 grid gap-2">
						{#each riskScenarioDraft.risk_scenarios as scenario}
							<label class="flex items-start gap-2 rounded border bg-white p-2 text-xs">
								<input type="checkbox" bind:checked={selectedRiskScenarioIds[scenario.temporary_id]} />
								<span>
									<span class="font-semibold">{scenario.title}</span>
									<span class="text-slate-600">
										&middot; Risk level: {humanizeFieldLabel(scenario.risk_level)} &middot; Confidence: {formatConfidence(
											scenario.confidence
										)}
									</span>
								</span>
							</label>
						{/each}
					</div>

					<div class="mt-3 flex flex-wrap items-center gap-3">
						<button
							class="btn btn-sm preset-tonal"
							type="button"
							disabled={loading !== null ||
								!selectedRiskScenarios.length ||
								!setupReference.risk_assessment_id}
							onclick={() => runRiskScenarioCommit(true)}
						>
							{loading === 'risk-scenario-commit-dry-run' ? 'Dry-running...' : 'Step 8B dry-run'}
						</button>
						<label class="flex items-center gap-2 text-xs">
							<input type="checkbox" bind:checked={riskScenarioCommitApproved} />
							<span>I approve deterministic Step 8B decisions for selected risk scenarios</span>
						</label>
						<button
							class="btn btn-sm preset-filled-error-500"
							type="button"
							disabled={loading !== null ||
								!riskScenarioCommitApproved ||
								!riskScenarioDryRunSucceeded ||
								!selectedRiskScenarios.length}
							onclick={() => runRiskScenarioCommit(false)}
						>
							{loading === 'risk-scenario-commit' ? 'Committing...' : 'Approved risk scenario commit'}
						</button>
						<span class="text-xs text-emerald-900">No AI model is used in this write step.</span>
					</div>

					{#if riskScenarioCommitDryRun}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">
								Step 8B dry-run status: {humanizeFieldLabel(riskScenarioCommitDryRun.commit_status)}
							</div>
							<p class="text-xs text-slate-700">
								Dry-run only previews the deterministic write. Nothing was written.
							</p>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Rejected: {riskScenarioCommitDryRun.rejected_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Deferred: {riskScenarioCommitDryRun.deferred_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Skipped: {riskScenarioCommitDryRun.skipped_records?.length ?? 0}
								</span>
							</div>
							{#if riskScenarioCommitDryRun.planned_actions?.length}
								<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each riskScenarioCommitDryRun.planned_actions as action}
										<li>
											{action.target_name ?? action.source_temporary_id}:
											{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
											&middot; {action.detail}
										</li>
									{/each}
								</ul>
							{/if}
						</div>
						{#if riskScenarioCommitDryRun.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each riskScenarioCommitDryRun.warnings as warning}
									<li>{warning.detail ?? warning.message ?? warning.code}</li>
								{/each}
							</ul>
						{/if}
						{#if riskScenarioCommitDryRun.blocking_errors?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
								{#each riskScenarioCommitDryRun.blocking_errors as blockingError}
									<li>{blockingError.detail}</li>
								{/each}
							</ul>
						{/if}
					{/if}

					{#if riskScenarioCommitResult}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">
								Step 8B commit status: {humanizeFieldLabel(riskScenarioCommitResult.commit_status)}
							</div>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
									Created: {riskScenarioCommitResult.created_records?.length ?? 0}
								</span>
								<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
									Reused: {riskScenarioCommitResult.reused_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Rejected: {riskScenarioCommitResult.rejected_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Deferred: {riskScenarioCommitResult.deferred_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Skipped: {riskScenarioCommitResult.skipped_records?.length ?? 0}
								</span>
								<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
									Warnings: {riskScenarioCommitResult.warnings?.length ?? 0}
								</span>
								<span class="rounded bg-red-100 px-2 py-1 font-semibold text-red-900">
									Blocking errors: {riskScenarioCommitResult.blocking_errors?.length ?? 0}
								</span>
							</div>
							{#if riskScenarioCommitResult.created_records?.length}
								<div class="text-xs font-semibold text-emerald-950">Created risk scenarios</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each riskScenarioCommitResult.created_records as record}
										<li>{humanizeFieldLabel(record.record_type)}: {record.name}</li>
									{/each}
								</ul>
							{/if}
							{#if riskScenarioCommitResult.reused_records?.length}
								<div class="text-xs font-semibold text-emerald-950">Reused risk scenarios</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each riskScenarioCommitResult.reused_records as record}
										<li>{humanizeFieldLabel(record.record_type)}: {record.name}</li>
									{/each}
								</ul>
							{/if}
							{#if riskScenarioCommitResult.planned_actions?.length}
								<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each riskScenarioCommitResult.planned_actions as action}
										<li>
											{action.target_name ?? action.source_temporary_id}:
											{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
										</li>
									{/each}
								</ul>
							{/if}
						</div>
						{#if riskScenarioCommitResult.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each riskScenarioCommitResult.warnings as warning}
									<li>{warning.detail ?? warning.message ?? warning.code}</li>
								{/each}
							</ul>
						{/if}
						{#if riskScenarioCommitResult.blocking_errors?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
								{#each riskScenarioCommitResult.blocking_errors as blockingError}
									<li>{blockingError.detail}</li>
								{/each}
							</ul>
						{/if}
					{/if}
				</div>
			{/if}

			{#if riskScenarioDraft}
				<div class="mt-4 rounded border border-sky-200 bg-sky-50/60 p-3 text-sm text-sky-950">
					<div class="font-semibold">Step 9A &middot; Control Effectiveness Suggestion</div>
					<p class="mt-1 text-sky-900">
						<span class="font-semibold">AI suggestion only / no database write.</span>
						Step 9A suggests how effective each mapped control appears and what compliance status
						the evidence supports. No requirement assessment is updated, no audit is closed, and no
						compliance is certified in this step.
					</p>
					<div class="mt-3 flex flex-wrap items-center gap-3">
						<button
							class="btn btn-sm preset-filled-primary-500"
							type="button"
							disabled={loading !== null}
							onclick={() => runControlEffectivenessSuggestion()}
						>
							{loading === 'control-effectiveness-suggest'
								? 'Running...'
								: 'Run Local AI Control Effectiveness Suggestion'}
						</button>
						<span class="text-xs text-sky-900">
							AI Provider: {humanizeProviderMode(controlEffectivenessProviderMode)} &middot; No
							database writes occur in Step 9A.
						</span>
					</div>

					{#if controlEffectivenessDraft}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">Step 9A suggestion summary</div>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Overall confidence: {formatConfidence(controlEffectivenessDraft.overall_confidence)}
								</span>
								<span class="rounded bg-sky-100 px-2 py-1 font-semibold text-sky-900">
									Judgements: {controlEffectivenessDraft.control_effectiveness_suggestions?.length ?? 0}
								</span>
								<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
									Warnings: {controlEffectivenessDraft.warnings?.length ?? 0}
								</span>
							</div>
						</div>

						{#if controlEffectivenessDraft.control_effectiveness_suggestions?.length}
							<div class="mt-3">
								<div class="font-semibold text-sky-950">
									Control effectiveness suggestions ({controlEffectivenessDraft
										.control_effectiveness_suggestions.length})
								</div>
								<p class="text-xs text-sky-900">
									Advisory judgements for auditor review. They are not compliance conclusions.
								</p>
								<div class="mt-2 grid gap-2">
									{#each controlEffectivenessDraft.control_effectiveness_suggestions as suggestion}
										<div class="rounded border bg-white p-3 text-xs text-slate-800">
											<div class="flex flex-wrap items-start justify-between gap-2">
												<div class="text-sm font-semibold text-slate-950">
													{#if suggestion.framework_control_code}
														<span class="text-slate-600">{suggestion.framework_control_code}</span>
														&middot;
													{/if}
													{suggestion.framework_control_title}
												</div>
												<div class="flex flex-wrap gap-1">
													<span class="rounded bg-sky-100 px-2 py-0.5 font-semibold text-sky-900">
														{humanizeFieldLabel(suggestion.suggested_effectiveness)}
													</span>
													<span class="rounded bg-orange-100 px-2 py-0.5 font-semibold text-orange-900">
														{humanizeFieldLabel(suggestion.suggested_compliance_status)}
													</span>
													<span class="rounded bg-slate-100 px-2 py-0.5 font-semibold text-slate-700">
														Confidence: {formatConfidence(suggestion.confidence)}
													</span>
													{#if suggestion.review_status}
														<span
															class="rounded bg-violet-100 px-2 py-0.5 font-semibold text-violet-900"
														>
															{humanizeFieldLabel(suggestion.review_status)}
														</span>
													{/if}
												</div>
											</div>
											{#if suggestion.evidence_summary}
												<div class="mt-1">
													<span class="font-semibold">Evidence summary:</span>
													{suggestion.evidence_summary}
												</div>
											{/if}
											{#if suggestion.gaps?.length}
												<div class="mt-1">
													<span class="font-semibold">Gaps:</span>
													<ul class="list-disc pl-5">
														{#each suggestion.gaps as gap}
															<li>{gap}</li>
														{/each}
													</ul>
												</div>
											{/if}
											{#if suggestion.recommended_auditor_action}
												<div class="mt-1">
													<span class="font-semibold">Recommended auditor action:</span>
													{suggestion.recommended_auditor_action}
												</div>
											{/if}
											{#if suggestion.rationale}
												<div class="mt-1">
													<span class="font-semibold">Rationale:</span>
													{suggestion.rationale}
												</div>
											{/if}
										</div>
									{/each}
								</div>
							</div>
						{/if}

						{#if controlEffectivenessDraft.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each controlEffectivenessDraft.warnings as warning}
									<li>{warning.message ?? warning.detail ?? warning.code}</li>
								{/each}
							</ul>
						{/if}

						{#if controlEffectivenessDraft.ambiguity_flags?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each controlEffectivenessDraft.ambiguity_flags as flag}
									<li>{flag.message ?? flag.code}</li>
								{/each}
							</ul>
						{/if}
					{/if}
				</div>
			{/if}

			{#if controlEffectivenessDraft?.control_effectiveness_suggestions?.length}
				<div class="mt-4 rounded border border-emerald-300 bg-emerald-50/60 p-3 text-sm text-emerald-950">
					<div class="font-semibold">Step 9B &middot; Control Effectiveness Commit</div>
					<p class="mt-1 text-emerald-900">
						<span class="font-semibold">No AI model is used / writes only after approval.</span>
						Select the Step 9A judgements to record, then dry-run to preview. The approved commit
						updates only the result and observation of existing requirement assessments; it never
						changes the audit status and never certifies compliance.
					</p>

					<div class="mt-3 grid gap-2">
						{#each controlEffectivenessDraft.control_effectiveness_suggestions as suggestion}
							<label class="flex items-start gap-2 rounded border bg-white p-2 text-xs">
								<input
									type="checkbox"
									bind:checked={selectedControlEffectivenessIds[suggestion.temporary_id]}
								/>
								<span>
									<span class="font-semibold">
										{#if suggestion.framework_control_code}
											{suggestion.framework_control_code} &middot;
										{/if}
										{suggestion.framework_control_title}
									</span>
									<span class="text-slate-600">
										&middot; {humanizeFieldLabel(suggestion.suggested_compliance_status)} &middot;
										Confidence: {formatConfidence(suggestion.confidence)}
									</span>
								</span>
							</label>
						{/each}
					</div>

					<div class="mt-3 flex flex-wrap items-center gap-3">
						<button
							class="btn btn-sm preset-tonal"
							type="button"
							disabled={loading !== null || !selectedControlEffectiveness.length}
							onclick={() => runControlEffectivenessCommit(true)}
						>
							{loading === 'control-effectiveness-commit-dry-run'
								? 'Dry-running...'
								: 'Step 9B dry-run'}
						</button>
						<label class="flex items-center gap-2 text-xs">
							<input type="checkbox" bind:checked={controlEffectivenessCommitApproved} />
							<span>
								I approve deterministic Step 9B decisions for selected control effectiveness
								judgements
							</span>
						</label>
						<button
							class="btn btn-sm preset-filled-error-500"
							type="button"
							disabled={loading !== null ||
								!controlEffectivenessCommitApproved ||
								!controlEffectivenessDryRunSucceeded ||
								!selectedControlEffectiveness.length}
							onclick={() => runControlEffectivenessCommit(false)}
						>
							{loading === 'control-effectiveness-commit'
								? 'Committing...'
								: 'Approved control effectiveness commit'}
						</button>
						<span class="text-xs text-emerald-900">No AI model is used in this write step.</span>
					</div>

					{#if controlEffectivenessCommitDryRun}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">
								Step 9B dry-run status: {humanizeFieldLabel(
									controlEffectivenessCommitDryRun.commit_status
								)}
							</div>
							<p class="text-xs text-slate-700">
								Dry-run only previews the deterministic write. Nothing was written.
							</p>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Rejected: {controlEffectivenessCommitDryRun.rejected_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Deferred: {controlEffectivenessCommitDryRun.deferred_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Skipped: {controlEffectivenessCommitDryRun.skipped_records?.length ?? 0}
								</span>
							</div>
							{#if controlEffectivenessCommitDryRun.planned_actions?.length}
								<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each controlEffectivenessCommitDryRun.planned_actions as action}
										<li>
											{action.target_name ?? action.source_temporary_id}:
											{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
											&middot; {action.detail}
										</li>
									{/each}
								</ul>
							{/if}
						</div>
						{#if controlEffectivenessCommitDryRun.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each controlEffectivenessCommitDryRun.warnings as warning}
									<li>{warning.detail ?? warning.message ?? warning.code}</li>
								{/each}
							</ul>
						{/if}
						{#if controlEffectivenessCommitDryRun.blocking_errors?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
								{#each controlEffectivenessCommitDryRun.blocking_errors as blockingError}
									<li>{blockingError.detail}</li>
								{/each}
							</ul>
						{/if}
					{/if}

					{#if controlEffectivenessCommitResult}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">
								Step 9B commit status: {humanizeFieldLabel(
									controlEffectivenessCommitResult.commit_status
								)}
							</div>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
									Recorded: {controlEffectivenessCommitResult.created_records?.length ?? 0}
								</span>
								<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
									Unchanged: {controlEffectivenessCommitResult.reused_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Rejected: {controlEffectivenessCommitResult.rejected_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Deferred: {controlEffectivenessCommitResult.deferred_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Skipped: {controlEffectivenessCommitResult.skipped_records?.length ?? 0}
								</span>
								<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
									Warnings: {controlEffectivenessCommitResult.warnings?.length ?? 0}
								</span>
								<span class="rounded bg-red-100 px-2 py-1 font-semibold text-red-900">
									Blocking errors: {controlEffectivenessCommitResult.blocking_errors?.length ?? 0}
								</span>
							</div>
							{#if controlEffectivenessCommitResult.created_records?.length}
								<div class="text-xs font-semibold text-emerald-950">
									Updated requirement assessments
								</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each controlEffectivenessCommitResult.created_records as record}
										<li>{record.name} &middot; result: {humanizeFieldLabel(record.result)}</li>
									{/each}
								</ul>
							{/if}
							{#if controlEffectivenessCommitResult.reused_records?.length}
								<div class="text-xs font-semibold text-emerald-950">Unchanged (already recorded)</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each controlEffectivenessCommitResult.reused_records as record}
										<li>{record.name}</li>
									{/each}
								</ul>
							{/if}
							{#if controlEffectivenessCommitResult.planned_actions?.length}
								<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each controlEffectivenessCommitResult.planned_actions as action}
										<li>
											{action.target_name ?? action.source_temporary_id}:
											{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
										</li>
									{/each}
								</ul>
							{/if}
						</div>
						{#if controlEffectivenessCommitResult.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each controlEffectivenessCommitResult.warnings as warning}
									<li>{warning.detail ?? warning.message ?? warning.code}</li>
								{/each}
							</ul>
						{/if}
						{#if controlEffectivenessCommitResult.blocking_errors?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
								{#each controlEffectivenessCommitResult.blocking_errors as blockingError}
									<li>{blockingError.detail}</li>
								{/each}
							</ul>
						{/if}
					{/if}
				</div>
			{/if}

			{#if controlEffectivenessDraft}
				<div class="mt-4 rounded border border-sky-200 bg-sky-50/60 p-3 text-sm text-sky-950">
					<div class="font-semibold">Step 10A &middot; Evidence Gap / Audit Readiness Summary</div>
					<p class="mt-1 text-sky-900">
						<span class="font-semibold">AI suggestion only / no database write.</span>
						Step 10A summarizes what is ready, what is missing, and what is blocking the assessment.
						Nothing is marked ready and nothing is closed in this step.
					</p>
					<div class="mt-3 flex flex-wrap items-center gap-3">
						<button
							class="btn btn-sm preset-filled-primary-500"
							type="button"
							disabled={loading !== null}
							onclick={() => runAuditReadinessSuggestion()}
						>
							{loading === 'audit-readiness-suggest'
								? 'Running...'
								: 'Run Local AI Audit Readiness Summary'}
						</button>
						<span class="text-xs text-sky-900">
							AI Provider: {humanizeProviderMode(auditReadinessProviderMode)} &middot; No database
							writes occur in Step 10A.
						</span>
					</div>

					{#if auditReadinessDraft}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">Step 10A readiness summary</div>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-sky-100 px-2 py-1 font-semibold text-sky-900">
									Readiness: {humanizeFieldLabel(auditReadinessDraft.readiness_status)}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Advisory score: {auditReadinessDraft.readiness_score}/100
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Overall confidence: {formatConfidence(auditReadinessDraft.overall_confidence)}
								</span>
								<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
									Warnings: {auditReadinessDraft.warnings?.length ?? 0}
								</span>
							</div>
							{#if auditReadinessDraft.summary}
								<p class="text-xs text-slate-800">{auditReadinessDraft.summary}</p>
							{/if}
						</div>

						<div class="mt-3 grid gap-2 md:grid-cols-2">
							{#each [['Ready items', auditReadinessDraft.ready_items], ['Missing evidence', auditReadinessDraft.missing_evidence], ['Open findings', auditReadinessDraft.open_findings], ['Open risks', auditReadinessDraft.open_risks], ['Blocked controls', auditReadinessDraft.blocked_controls], ['Priority actions', auditReadinessDraft.priority_actions], ['Recommended next steps', auditReadinessDraft.recommended_next_steps]] as [sectionLabel, entries]}
								{#if entries?.length}
									<div class="rounded border bg-white p-3 text-xs text-slate-800">
										<div class="font-semibold text-slate-950">{sectionLabel}</div>
										<ul class="mt-1 list-disc pl-5">
											{#each entries as entry}
												<li>{entry}</li>
											{/each}
										</ul>
									</div>
								{/if}
							{/each}
						</div>

						{#if auditReadinessDraft.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each auditReadinessDraft.warnings as warning}
									<li>{warning.message ?? warning.detail ?? warning.code}</li>
								{/each}
							</ul>
						{/if}

						{#if auditReadinessDraft.ambiguity_flags?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each auditReadinessDraft.ambiguity_flags as flag}
									<li>{flag.message ?? flag.code}</li>
								{/each}
							</ul>
						{/if}
					{/if}
				</div>
			{/if}

			{#if auditReadinessDraft}
				<div class="mt-4 rounded border border-emerald-300 bg-emerald-50/60 p-3 text-sm text-emerald-950">
					<div class="font-semibold">Step 10B &middot; Audit Readiness Commit</div>
					<p class="mt-1 text-emerald-900">
						<span class="font-semibold">No AI model is used / writes only after approval.</span>
						Select the readiness summary to record, then dry-run to preview. The approved commit
						appends it to the audit's observation note only; the audit status is never changed and
						the audit is never marked ready or complete.
					</p>

					<div class="mt-3 grid gap-2">
						<label class="flex items-start gap-2 rounded border bg-white p-2 text-xs">
							<input type="checkbox" bind:checked={auditReadinessSelected} />
							<span>
								<span class="font-semibold">
									Readiness summary: {humanizeFieldLabel(auditReadinessDraft.readiness_status)}
								</span>
								<span class="text-slate-600">
									&middot; advisory score {auditReadinessDraft.readiness_score}/100
								</span>
							</span>
						</label>
					</div>

					<div class="mt-3 flex flex-wrap items-center gap-3">
						<button
							class="btn btn-sm preset-tonal"
							type="button"
							disabled={loading !== null || !auditReadinessSelected}
							onclick={() => runAuditReadinessCommit(true)}
						>
							{loading === 'audit-readiness-commit-dry-run' ? 'Dry-running...' : 'Step 10B dry-run'}
						</button>
						<label class="flex items-center gap-2 text-xs">
							<input type="checkbox" bind:checked={auditReadinessCommitApproved} />
							<span>I approve the deterministic Step 10B readiness note</span>
						</label>
						<button
							class="btn btn-sm preset-filled-error-500"
							type="button"
							disabled={loading !== null ||
								!auditReadinessCommitApproved ||
								!auditReadinessDryRunSucceeded ||
								!auditReadinessSelected}
							onclick={() => runAuditReadinessCommit(false)}
						>
							{loading === 'audit-readiness-commit'
								? 'Committing...'
								: 'Approved audit readiness commit'}
						</button>
						<span class="text-xs text-emerald-900">No AI model is used in this write step.</span>
					</div>

					{#if auditReadinessCommitDryRun}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">
								Step 10B dry-run status: {humanizeFieldLabel(auditReadinessCommitDryRun.commit_status)}
							</div>
							<p class="text-xs text-slate-700">
								Dry-run only previews the deterministic write. Nothing was written.
							</p>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Rejected: {auditReadinessCommitDryRun.rejected_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Deferred: {auditReadinessCommitDryRun.deferred_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Skipped: {auditReadinessCommitDryRun.skipped_records?.length ?? 0}
								</span>
							</div>
							{#if auditReadinessCommitDryRun.planned_actions?.length}
								<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each auditReadinessCommitDryRun.planned_actions as action}
										<li>
											{action.target_name ?? action.source_temporary_id}:
											{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
											&middot; {action.detail}
										</li>
									{/each}
								</ul>
							{/if}
						</div>
						{#if auditReadinessCommitDryRun.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each auditReadinessCommitDryRun.warnings as warning}
									<li>{warning.detail ?? warning.message ?? warning.code}</li>
								{/each}
							</ul>
						{/if}
						{#if auditReadinessCommitDryRun.blocking_errors?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
								{#each auditReadinessCommitDryRun.blocking_errors as blockingError}
									<li>{blockingError.detail}</li>
								{/each}
							</ul>
						{/if}
					{/if}

					{#if auditReadinessCommitResult}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">
								Step 10B commit status: {humanizeFieldLabel(auditReadinessCommitResult.commit_status)}
							</div>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
									Recorded: {auditReadinessCommitResult.created_records?.length ?? 0}
								</span>
								<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
									Unchanged: {auditReadinessCommitResult.reused_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Rejected: {auditReadinessCommitResult.rejected_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Deferred: {auditReadinessCommitResult.deferred_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Skipped: {auditReadinessCommitResult.skipped_records?.length ?? 0}
								</span>
								<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
									Warnings: {auditReadinessCommitResult.warnings?.length ?? 0}
								</span>
								<span class="rounded bg-red-100 px-2 py-1 font-semibold text-red-900">
									Blocking errors: {auditReadinessCommitResult.blocking_errors?.length ?? 0}
								</span>
							</div>
							{#if auditReadinessCommitResult.created_records?.length}
								<div class="text-xs font-semibold text-emerald-950">Recorded on</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each auditReadinessCommitResult.created_records as record}
										<li>{record.name} &middot; {humanizeFieldLabel(record.record_type)}</li>
									{/each}
								</ul>
							{/if}
							{#if auditReadinessCommitResult.planned_actions?.length}
								<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each auditReadinessCommitResult.planned_actions as action}
										<li>
											{action.target_name ?? action.source_temporary_id}:
											{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
										</li>
									{/each}
								</ul>
							{/if}
						</div>
						{#if auditReadinessCommitResult.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each auditReadinessCommitResult.warnings as warning}
									<li>{warning.detail ?? warning.message ?? warning.code}</li>
								{/each}
							</ul>
						{/if}
						{#if auditReadinessCommitResult.blocking_errors?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
								{#each auditReadinessCommitResult.blocking_errors as blockingError}
									<li>{blockingError.detail}</li>
								{/each}
							</ul>
						{/if}
					{/if}
				</div>
			{/if}

			{#if auditReadinessDraft}
				<div class="mt-4 rounded border border-sky-200 bg-sky-50/60 p-3 text-sm text-sky-950">
					<div class="font-semibold">Step 11A &middot; Management / Audit Report Draft</div>
					<p class="mt-1 text-sky-900">
						<span class="font-semibold">AI draft only / no database write.</span>
						Step 11A drafts the management report from the reviewed onboarding output. It is never a
						final audit opinion, a compliance certification, or a regulator-approved result.
					</p>
					<div class="mt-3 flex flex-wrap items-center gap-3">
						<button
							class="btn btn-sm preset-filled-primary-500"
							type="button"
							disabled={loading !== null}
							onclick={() => runAuditReportSuggestion()}
						>
							{loading === 'audit-report-suggest' ? 'Running...' : 'Run Local AI Report Draft'}
						</button>
						<span class="text-xs text-sky-900">
							AI Provider: {humanizeProviderMode(auditReportProviderMode)} &middot; No database
							writes occur in Step 11A.
						</span>
					</div>

					{#if auditReportDraft}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">{auditReportDraft.report_title}</div>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Overall confidence: {formatConfidence(auditReportDraft.overall_confidence)}
								</span>
								<span class="rounded bg-sky-100 px-2 py-1 font-semibold text-sky-900">
									Sections: {auditReportDraft.report_sections?.length ?? 0}
								</span>
								<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
									Warnings: {auditReportDraft.warnings?.length ?? 0}
								</span>
								{#if auditReportDraft.review_status}
									<span class="rounded bg-violet-100 px-2 py-1 font-semibold text-violet-900">
										{humanizeFieldLabel(auditReportDraft.review_status)}
									</span>
								{/if}
							</div>
							{#if auditReportDraft.executive_summary}
								<p class="text-xs text-slate-800">{auditReportDraft.executive_summary}</p>
							{/if}
						</div>

						{#if auditReportDraft.report_sections?.length}
							<div class="mt-3 grid gap-2">
								{#each auditReportDraft.report_sections as section}
									<div class="rounded border bg-white p-3 text-xs text-slate-800">
										<div class="flex flex-wrap items-start justify-between gap-2">
											<div class="text-sm font-semibold text-slate-950">{section.heading}</div>
											<span class="rounded bg-slate-100 px-2 py-0.5 font-semibold text-slate-700">
												Confidence: {formatConfidence(section.confidence)}
											</span>
										</div>
										{#if section.content}
											<div class="mt-1 whitespace-pre-line text-slate-700">{section.content}</div>
										{/if}
										{#if section.source_items?.length}
											<div class="mt-1">
												<span class="font-semibold">Source items:</span>
												<ul class="list-disc pl-5">
													{#each section.source_items as sourceItem}
														<li>{sourceItem}</li>
													{/each}
												</ul>
											</div>
										{/if}
									</div>
								{/each}
							</div>
						{/if}

						{#if auditReportDraft.limitations?.length}
							<div class="mt-3 rounded border border-amber-300 bg-amber-50 p-3 text-xs text-amber-900">
								<div class="font-semibold">Limitations / human review required</div>
								<ul class="mt-1 list-disc pl-5">
									{#each auditReportDraft.limitations as limitation}
										<li>{limitation}</li>
									{/each}
								</ul>
							</div>
						{/if}

						{#if auditReportDraft.recommended_next_steps?.length}
							<div class="mt-3 rounded border bg-white p-3 text-xs text-slate-800">
								<div class="font-semibold text-slate-950">Recommended next steps</div>
								<ul class="mt-1 list-disc pl-5">
									{#each auditReportDraft.recommended_next_steps as nextStep}
										<li>{nextStep}</li>
									{/each}
								</ul>
							</div>
						{/if}

						{#if auditReportDraft.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each auditReportDraft.warnings as warning}
									<li>{warning.message ?? warning.detail ?? warning.code}</li>
								{/each}
							</ul>
						{/if}

						{#if auditReportDraft.ambiguity_flags?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each auditReportDraft.ambiguity_flags as flag}
									<li>{flag.message ?? flag.code}</li>
								{/each}
							</ul>
						{/if}
					{/if}
				</div>
			{/if}

			{#if auditReportDraft}
				<div class="mt-4 rounded border border-emerald-300 bg-emerald-50/60 p-3 text-sm text-emerald-950">
					<div class="font-semibold">Step 11B &middot; Report Save Commit</div>
					<p class="mt-1 text-emerald-900">
						<span class="font-semibold">No AI model is used / writes only after approval.</span>
						Select the report draft to save, then dry-run to preview. The approved commit stores it
						as a draft document; the report is never marked final or published and the audit status
						is never changed.
					</p>

					<div class="mt-3 grid gap-2">
						<label class="flex items-start gap-2 rounded border bg-white p-2 text-xs">
							<input type="checkbox" bind:checked={auditReportSelected} />
							<span>
								<span class="font-semibold">{auditReportDraft.report_title}</span>
								<span class="text-slate-600">
									&middot; {auditReportDraft.report_sections?.length ?? 0} section(s) &middot; saved as
									a draft document
								</span>
							</span>
						</label>
					</div>

					<div class="mt-3 flex flex-wrap items-center gap-3">
						<button
							class="btn btn-sm preset-tonal"
							type="button"
							disabled={loading !== null || !auditReportSelected}
							onclick={() => runAuditReportCommit(true)}
						>
							{loading === 'audit-report-commit-dry-run' ? 'Dry-running...' : 'Step 11B dry-run'}
						</button>
						<label class="flex items-center gap-2 text-xs">
							<input type="checkbox" bind:checked={auditReportCommitApproved} />
							<span>I approve saving the deterministic Step 11B report draft</span>
						</label>
						<button
							class="btn btn-sm preset-filled-error-500"
							type="button"
							disabled={loading !== null ||
								!auditReportCommitApproved ||
								!auditReportDryRunSucceeded ||
								!auditReportSelected}
							onclick={() => runAuditReportCommit(false)}
						>
							{loading === 'audit-report-commit' ? 'Committing...' : 'Approved report save commit'}
						</button>
						<span class="text-xs text-emerald-900">No AI model is used in this write step.</span>
					</div>

					{#if auditReportCommitDryRun}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">
								Step 11B dry-run status: {humanizeFieldLabel(auditReportCommitDryRun.commit_status)}
							</div>
							<p class="text-xs text-slate-700">
								Dry-run only previews the deterministic write. Nothing was written.
							</p>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Rejected: {auditReportCommitDryRun.rejected_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Deferred: {auditReportCommitDryRun.deferred_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Skipped: {auditReportCommitDryRun.skipped_records?.length ?? 0}
								</span>
							</div>
							{#if auditReportCommitDryRun.planned_actions?.length}
								<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each auditReportCommitDryRun.planned_actions as action}
										<li>
											{action.target_name ?? action.source_temporary_id}:
											{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
											&middot; {action.detail}
										</li>
									{/each}
								</ul>
							{/if}
						</div>
						{#if auditReportCommitDryRun.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each auditReportCommitDryRun.warnings as warning}
									<li>{warning.detail ?? warning.message ?? warning.code}</li>
								{/each}
							</ul>
						{/if}
						{#if auditReportCommitDryRun.blocking_errors?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
								{#each auditReportCommitDryRun.blocking_errors as blockingError}
									<li>{blockingError.detail}</li>
								{/each}
							</ul>
						{/if}
					{/if}

					{#if auditReportCommitResult}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">
								Step 11B commit status: {humanizeFieldLabel(auditReportCommitResult.commit_status)}
							</div>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
									Created: {auditReportCommitResult.created_records?.length ?? 0}
								</span>
								<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
									Reused: {auditReportCommitResult.reused_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Rejected: {auditReportCommitResult.rejected_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Deferred: {auditReportCommitResult.deferred_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Skipped: {auditReportCommitResult.skipped_records?.length ?? 0}
								</span>
								<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
									Warnings: {auditReportCommitResult.warnings?.length ?? 0}
								</span>
								<span class="rounded bg-red-100 px-2 py-1 font-semibold text-red-900">
									Blocking errors: {auditReportCommitResult.blocking_errors?.length ?? 0}
								</span>
							</div>
							{#if auditReportCommitResult.created_records?.length}
								<div class="text-xs font-semibold text-emerald-950">Saved report documents</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each auditReportCommitResult.created_records as record}
										<li>{record.name} &middot; status: {humanizeFieldLabel(record.status)}</li>
									{/each}
								</ul>
							{/if}
							{#if auditReportCommitResult.reused_records?.length}
								<div class="text-xs font-semibold text-emerald-950">Reused existing documents</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each auditReportCommitResult.reused_records as record}
										<li>{record.name}</li>
									{/each}
								</ul>
							{/if}
							{#if auditReportCommitResult.planned_actions?.length}
								<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each auditReportCommitResult.planned_actions as action}
										<li>
											{action.target_name ?? action.source_temporary_id}:
											{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
										</li>
									{/each}
								</ul>
							{/if}
						</div>
						{#if auditReportCommitResult.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each auditReportCommitResult.warnings as warning}
									<li>{warning.detail ?? warning.message ?? warning.code}</li>
								{/each}
							</ul>
						{/if}
						{#if auditReportCommitResult.blocking_errors?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
								{#each auditReportCommitResult.blocking_errors as blockingError}
									<li>{blockingError.detail}</li>
								{/each}
							</ul>
						{/if}
					{/if}
				</div>
			{/if}

			{#if auditReportDraft}
				<div class="mt-4 rounded border border-sky-200 bg-sky-50/60 p-3 text-sm text-sky-950">
					<div class="font-semibold">Step 12A &middot; Final End-to-End Review Summary</div>
					<p class="mt-1 text-sky-900">
						<span class="font-semibold">AI suggestion only / no database write.</span>
						Step 12A explains what the onboarding flow completed and what remains for human review.
						The workflow is never marked complete and no audit is closed in this step.
					</p>
					<div class="mt-3 flex flex-wrap items-center gap-3">
						<button
							class="btn btn-sm preset-filled-primary-500"
							type="button"
							disabled={loading !== null}
							onclick={() => runFinalReviewSuggestion()}
						>
							{loading === 'final-review-suggest' ? 'Running...' : 'Run Local AI Final Review Summary'}
						</button>
						<span class="text-xs text-sky-900">
							AI Provider: {humanizeProviderMode(finalReviewProviderMode)} &middot; No database
							writes occur in Step 12A.
						</span>
					</div>

					{#if finalReviewDraft}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">Step 12A completion summary</div>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-sky-100 px-2 py-1 font-semibold text-sky-900">
									Demo readiness: {humanizeFieldLabel(finalReviewDraft.demo_readiness_status)}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Overall confidence: {formatConfidence(finalReviewDraft.overall_confidence)}
								</span>
								<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
									Warnings: {finalReviewDraft.warnings?.length ?? 0}
								</span>
								{#if finalReviewDraft.review_status}
									<span class="rounded bg-violet-100 px-2 py-1 font-semibold text-violet-900">
										{humanizeFieldLabel(finalReviewDraft.review_status)}
									</span>
								{/if}
							</div>
							{#if finalReviewDraft.completion_summary}
								<p class="text-xs text-slate-800">{finalReviewDraft.completion_summary}</p>
							{/if}
						</div>

						<div class="mt-3 grid gap-2 md:grid-cols-2">
							{#each [['Completed steps', finalReviewDraft.completed_steps], ['Incomplete steps', finalReviewDraft.incomplete_steps], ['Created or reused records', finalReviewDraft.created_or_reused_records_summary], ['Blocked items', finalReviewDraft.blocked_items], ['Human review required', finalReviewDraft.human_review_required], ['Recommended next steps', finalReviewDraft.recommended_next_steps]] as [sectionLabel, entries]}
								{#if entries?.length}
									<div class="rounded border bg-white p-3 text-xs text-slate-800">
										<div class="font-semibold text-slate-950">{sectionLabel}</div>
										<ul class="mt-1 list-disc pl-5">
											{#each entries as entry}
												<li>{entry}</li>
											{/each}
										</ul>
									</div>
								{/if}
							{/each}
						</div>

						{#if finalReviewDraft.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each finalReviewDraft.warnings as warning}
									<li>{warning.message ?? warning.detail ?? warning.code}</li>
								{/each}
							</ul>
						{/if}

						{#if finalReviewDraft.ambiguity_flags?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each finalReviewDraft.ambiguity_flags as flag}
									<li>{flag.message ?? flag.code}</li>
								{/each}
							</ul>
						{/if}
					{/if}
				</div>
			{/if}

			{#if finalReviewDraft}
				<div class="mt-4 rounded border border-emerald-300 bg-emerald-50/60 p-3 text-sm text-emerald-950">
					<div class="font-semibold">Step 12B &middot; Final Review Commit / Case Handoff</div>
					<p class="mt-1 text-emerald-900">
						<span class="font-semibold">No AI model is used / writes only after approval.</span>
						Select the case handoff summary to record, then dry-run to preview. The approved commit
						appends it to the audit's observation note only; the workflow is never marked complete,
						the audit is never closed, and no compliance is certified.
					</p>

					<div class="mt-3 grid gap-2">
						<label class="flex items-start gap-2 rounded border bg-white p-2 text-xs">
							<input type="checkbox" bind:checked={finalReviewSelected} />
							<span>
								<span class="font-semibold">
									Case handoff summary: {humanizeFieldLabel(finalReviewDraft.demo_readiness_status)}
								</span>
								<span class="text-slate-600">
									&middot; {finalReviewDraft.human_review_required?.length ?? 0} human-review item(s)
								</span>
							</span>
						</label>
					</div>

					<div class="mt-3 flex flex-wrap items-center gap-3">
						<button
							class="btn btn-sm preset-tonal"
							type="button"
							disabled={loading !== null || !finalReviewSelected}
							onclick={() => runFinalReviewCommit(true)}
						>
							{loading === 'final-review-commit-dry-run' ? 'Dry-running...' : 'Step 12B dry-run'}
						</button>
						<label class="flex items-center gap-2 text-xs">
							<input type="checkbox" bind:checked={finalReviewCommitApproved} />
							<span>I approve the deterministic Step 12B case handoff note</span>
						</label>
						<button
							class="btn btn-sm preset-filled-error-500"
							type="button"
							disabled={loading !== null ||
								!finalReviewCommitApproved ||
								!finalReviewDryRunSucceeded ||
								!finalReviewSelected}
							onclick={() => runFinalReviewCommit(false)}
						>
							{loading === 'final-review-commit' ? 'Committing...' : 'Approved case handoff commit'}
						</button>
						<span class="text-xs text-emerald-900">No AI model is used in this write step.</span>
					</div>

					{#if finalReviewCommitDryRun}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">
								Step 12B dry-run status: {humanizeFieldLabel(finalReviewCommitDryRun.commit_status)}
							</div>
							<p class="text-xs text-slate-700">
								Dry-run only previews the deterministic write. Nothing was written.
							</p>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Rejected: {finalReviewCommitDryRun.rejected_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Deferred: {finalReviewCommitDryRun.deferred_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Skipped: {finalReviewCommitDryRun.skipped_records?.length ?? 0}
								</span>
							</div>
							{#if finalReviewCommitDryRun.planned_actions?.length}
								<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each finalReviewCommitDryRun.planned_actions as action}
										<li>
											{action.target_name ?? action.source_temporary_id}:
											{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
											&middot; {action.detail}
										</li>
									{/each}
								</ul>
							{/if}
						</div>
						{#if finalReviewCommitDryRun.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each finalReviewCommitDryRun.warnings as warning}
									<li>{warning.detail ?? warning.message ?? warning.code}</li>
								{/each}
							</ul>
						{/if}
						{#if finalReviewCommitDryRun.blocking_errors?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
								{#each finalReviewCommitDryRun.blocking_errors as blockingError}
									<li>{blockingError.detail}</li>
								{/each}
							</ul>
						{/if}
					{/if}

					{#if finalReviewCommitResult}
						<div class="mt-3 grid gap-2 rounded border bg-white p-3 text-sm">
							<div class="font-semibold">
								Step 12B commit status: {humanizeFieldLabel(finalReviewCommitResult.commit_status)}
							</div>
							<div class="flex flex-wrap gap-2 text-xs">
								<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
									Recorded: {finalReviewCommitResult.created_records?.length ?? 0}
								</span>
								<span class="rounded bg-emerald-100 px-2 py-1 font-semibold text-emerald-900">
									Unchanged: {finalReviewCommitResult.reused_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Rejected: {finalReviewCommitResult.rejected_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Deferred: {finalReviewCommitResult.deferred_records?.length ?? 0}
								</span>
								<span class="rounded bg-slate-100 px-2 py-1 font-semibold text-slate-700">
									Skipped: {finalReviewCommitResult.skipped_records?.length ?? 0}
								</span>
								<span class="rounded bg-amber-100 px-2 py-1 font-semibold text-amber-900">
									Warnings: {finalReviewCommitResult.warnings?.length ?? 0}
								</span>
								<span class="rounded bg-red-100 px-2 py-1 font-semibold text-red-900">
									Blocking errors: {finalReviewCommitResult.blocking_errors?.length ?? 0}
								</span>
							</div>
							{#if finalReviewCommitResult.created_records?.length}
								<div class="text-xs font-semibold text-emerald-950">Recorded on</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each finalReviewCommitResult.created_records as record}
										<li>{record.name} &middot; {humanizeFieldLabel(record.record_type)}</li>
									{/each}
								</ul>
							{/if}
							{#if finalReviewCommitResult.planned_actions?.length}
								<div class="text-xs font-semibold text-emerald-950">Planned actions</div>
								<ul class="list-disc pl-5 text-xs text-slate-800">
									{#each finalReviewCommitResult.planned_actions as action}
										<li>
											{action.target_name ?? action.source_temporary_id}:
											{humanizeActionName(action.decision)} &middot; {humanizeFieldLabel(action.status)}
										</li>
									{/each}
								</ul>
							{/if}
						</div>
						{#if finalReviewCommitResult.warnings?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-amber-800">
								{#each finalReviewCommitResult.warnings as warning}
									<li>{warning.detail ?? warning.message ?? warning.code}</li>
								{/each}
							</ul>
						{/if}
						{#if finalReviewCommitResult.blocking_errors?.length}
							<ul class="mt-3 list-disc pl-5 text-xs text-red-700">
								{#each finalReviewCommitResult.blocking_errors as blockingError}
									<li>{blockingError.detail}</li>
								{/each}
							</ul>
						{/if}
					{/if}
				</div>
			{/if}

			<details class="mt-3">
				<summary class="cursor-pointer font-semibold">Raw JSON</summary>
				<pre
					class="mt-2 max-h-80 overflow-auto rounded bg-slate-950 p-3 text-xs text-slate-50">{JSON.stringify(
						{
							assetDraft,
							commitDryRun,
							commitResult,
							appliedControlDraft,
							appliedControlCommitDryRun,
							appliedControlCommitResult,
							evidenceFindingDraft,
							evidenceFindingCommitDryRun,
							evidenceFindingCommitResult,
							remediationActionDraft,
							remediationCommitDryRun,
							remediationCommitResult,
							frameworkControlMappingDraft,
							frameworkMappingCommitDryRun,
							frameworkMappingCommitResult,
							riskScenarioDraft,
							riskScenarioCommitDryRun,
							riskScenarioCommitResult,
							controlEffectivenessDraft,
							controlEffectivenessCommitDryRun,
							controlEffectivenessCommitResult,
							auditReadinessDraft,
							auditReadinessCommitDryRun,
							auditReadinessCommitResult,
							auditReportDraft,
							auditReportCommitDryRun,
							auditReportCommitResult,
							finalReviewDraft,
							finalReviewCommitDryRun,
							finalReviewCommitResult
						},
						null,
						2
					)}</pre>
			</details>
		</div>
	{/if}

	{#if error}
		<pre
			class="mt-4 max-h-64 overflow-auto rounded border border-red-200 bg-red-50 p-3 text-xs text-red-900">{JSON.stringify(
				error,
				null,
				2
			)}</pre>
	{/if}
</section>
