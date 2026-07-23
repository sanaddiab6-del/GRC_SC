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
							evidenceFindingCommitResult
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
