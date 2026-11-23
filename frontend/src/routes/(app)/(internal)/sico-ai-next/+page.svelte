<!-- SICO-CLEAR-REPORT-V2: no nested JSON in primary report -->
<script lang="ts">
    import { enhance, deserialize, applyAction } from '$app/forms';
    import { onMount } from 'svelte';
    import type { ActionData } from './$types';
    import {
        applyFrameworkBatch, validateCheckpoint, scopeKey,
        type ReviewCheckpoint, type ReviewScope
    } from '$lib/utils/sicoFrameworkReviewV3';

    let { form }: { form: ActionData | null } = $props();
    let instruction = $state('');
    let organization = $state('');
    let busy = $state(false);
    let lastAgentRun = $state<Record<string, any> | null>(null);
    let eligibleOptions = $state<Record<string, any> | null>(null);
    let preparedWorkflow = $state<Record<string, any> | null>(null);
    let recordedApproval = $state<Record<string, any> | null>(null);
    let activeEngagement = $state('');
    let generatedAssessment = $state<Record<string, any> | null>(null);
    let generationError = $state('');
    let generatedSixteen = $state<Record<string, any>[]>([]);
    let generatedFor = $state('');
    let sixteenBusy = $state(false);
    let sixteenError = $state('');
    let caseSaveNotice = $state('');
    let controlProgress = $state<Record<string, any> | null>(null);
    let controlBusy = $state(false);
    let controlError = $state('');
    let controlNotice = $state('');
    let lastControlCaseLoaded = '';
    let lifecycleProgress = $state<Record<string, any> | null>(null);
    let lifecycleProposal = $state<Record<string, any> | null>(null);
    let lifecycleApproval = $state<Record<string, any> | null>(null);
    let evidenceContext = $state('');
    let selectedFolder = $state('');
    let selectedPerimeter = $state('__new__');
    let frameworkSearch = $state('');
    let frameworkConfirmation = $state('');
    let organizationConfirmation = $state('');
    let proposedAssessment = $state('Cybersecurity compliance assessment');
    let proposedPerimeter = $state('SICO cybersecurity assessment perimeter');
    let selectedFramework = $state('');
    let selectedRiskMatrix = $state('');
    // Unified Build a GRC case uses full-framework batches; legacy draft handlers remain unused by this page.
    // Creation-first: the main button uses SICO's existing three-input lifecycle
    // intake, real case-setup serializer and dry-run. No AI-side business writes.
    // New creation-first *drafting* mode: never calls GRC writers.
    let draftedCaseStages = $state<Record<string, any>[]>([]);
    let draftedCaseScope = $state('');
    let draftedCaseBusy = $state(false);
    let draftedCaseError = $state('');
    let draftedCaseNotice = $state('');
    let stopAfterPhase = $state(false);
    let authorizedFrameworkSource = $state<Record<string, any> | null>(null);
    let authorizedSourceRows = $state<Record<string, any>[]>([]);
    let frameworkSourceSummary = $state('');

    async function loadSicoAuthorizedFrameworkSource() {
        let cursor = '';
        let sourceDigest = '';
        let selectedFrameworkId = '';
        const rows: Record<string, any>[] = [];
        for (let page = 0; page < 200; page++) {
            const response = await sicoPostAction('framework_source_page', {
                framework_name: frameworkSearch.trim(), cursor
            });
            const part = (response.data as Record<string, any>)?.framework_source_page;
            if (!part) throw new Error('No authorized framework source was returned.');
            if (part.status !== 'partial' && part.status !== 'complete') {
                const candidates = Array.isArray(part.candidates) ? part.candidates.join(', ') : '';
                throw new Error('The exact selected framework could not be resolved using your SICO permissions.' + (candidates ? ` Authorized matches: ${candidates}` : ''));
            }
            if (!part.framework_id || !part.source_digest || !Array.isArray(part.requirements)) {
                throw new Error('Framework catalog did not include verified SICO source identifiers.');
            }
            if (sourceDigest && sourceDigest !== part.source_digest) {
                throw new Error('Framework library changed during retrieval; restart the draft.');
            }
            if (selectedFrameworkId && selectedFrameworkId !== part.framework_id) {
                throw new Error('The resolved framework changed during retrieval.');
            }
            sourceDigest = part.source_digest;
            selectedFrameworkId = part.framework_id;
            rows.push(...part.requirements);
            frameworkSourceSummary = `SICO authorized framework: ${rows.length}/${part.coverage.accessible_total} requirements loaded`;
            if (part.status === 'complete') {
                if (part.coverage.accessible_total === 0) {
                    throw new Error('The selected SICO framework has no requirements readable to this user.');
                }
                if (!part.coverage.complete || rows.length !== part.coverage.accessible_total) {
                    throw new Error('Framework source count mismatch. No coverage can be claimed.');
                }
                authorizedSourceRows = rows;
                authorizedFrameworkSource = {
                    framework_id: selectedFrameworkId,
                    matched_framework: part.matched_framework,
                    source_digest: sourceDigest,
                    accessible_total: rows.length,
                    complete_source_snapshot: true,
                    edition_independently_verified: false
                };
                return;
            }
            if (!part.next_cursor || part.next_cursor === cursor) {
                throw new Error('Framework source pagination did not advance.');
            }
            cursor = part.next_cursor;
        }
        throw new Error('Framework source is too large to load safely in one run.');
    }


    function draftScopeKey() {
        return JSON.stringify([organization.trim(), frameworkSearch.trim(), instruction.trim()]);
    }

    // One Qwen record per request: the same proven approach as the HTML runner.
    // No server-side GRC case/asset/risk writers are ever called by this path.
    const generationOrder = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16];
    let qualityDrafts = $state<Record<string, any>[]>([]);
    let qualityIssues = $state<string[]>([]);
    let loadedOlderCheckpoint = $state(false);
    let targetDraftsPerActivity = $state(1);
    let currentGeneratingActivity = $state(0);
    let localCheckpointInfo = $state('');
    // UX-only generation diagnostics: the API and stored draft schema remain unchanged.
    type DraftAttempt = { activity: number; index: number; elapsed_seconds: number; outcome: 'accepted' | 'rejected'; detail: string };
    let attemptHistory = $state<DraftAttempt[]>([]);
    let nextAttemptBySlot = $state<Record<string, number>>({});
    let lastAttemptInfo = $state('');

    // Only block a clearly conflicting explicit framework name in the objective.
    // An objective with no named framework, or multiple mentioned frameworks,
    // remains legal (e.g., a genuine cross-framework comparison).
    function frameworkNames(text: string): string[] {
        const value = text.toLowerCase();
        const detected: string[] = [];
        const tests: [string, RegExp][] = [
            ['NCA ECC', /\b(?:nca\s+)?ecc\b|essential cybersecurity controls/i],
            ['NCA CCC', /\b(?:nca\s+)?ccc\b|cloud cybersecurity controls/i],
            ['NIST CSF', /\bnist\s*(?:csf|cybersecurity framework)\b/i],
            ['ISO 27001', /\b(?:iso\s*(?:\/\s*iec)?\s*)?27001\b/i],
            ['CyberFundamentals', /cyber\s*fundamentals|\bcyfun\b/i],
            ['PDPL', /\bpdpl\b/i],
            ['SAMA CSF', /\bsama\s*(?:csf|cybersecurity framework)\b/i]
        ];
        for (const [label, pattern] of tests) if (pattern.test(value)) detected.push(label);
        return detected;
    }
    function explicitFrameworkConflict(): string {
        const selected = frameworkNames(frameworkSearch);
        const requested = frameworkNames(instruction);
        if (selected.length !== 1 || requested.length !== 1 || selected[0] === requested[0]) return '';
        return `Framework mismatch: you selected ${frameworkSearch.trim()}, but the objective names ${requested[0]}. Correct the framework or objective before generating.`;
    }
    function slotAttemptKey(step: number, index: number) {
        return `draft-${String(step).padStart(2, '0')}-${String(index).padStart(2, '0')}`;
    }
    function safeAttemptCounters(source: unknown): Record<string, number> {
        const result: Record<string, number> = {};
        if (!source || typeof source !== 'object' || Array.isArray(source)) return result;
        for (const [key, value] of Object.entries(source)) {
            if (/^draft-(?:0[1-9]|1[0-6])-(?:0[1-9]|1[0-2])$/.test(key) &&
                Number.isInteger(value) && Number(value) >= 0 && Number(value) <= 30) result[key] = Number(value);
        }
        return result;
    }
    function safeAttemptHistory(source: unknown): DraftAttempt[] {
        if (!Array.isArray(source)) return [];
        return source.slice(-20).filter((entry: any) =>
            Number.isInteger(entry?.activity) && entry.activity >= 1 && entry.activity <= 16 &&
            Number.isInteger(entry?.index) && entry.index >= 1 && entry.index <= 12 &&
            typeof entry?.elapsed_seconds === 'number' && entry.elapsed_seconds >= 0 && entry.elapsed_seconds < 3600 &&
            (entry?.outcome === 'accepted' || entry?.outcome === 'rejected') && typeof entry?.detail === 'string'
        ).map((entry: DraftAttempt) => ({ ...entry, detail: entry.detail.slice(0, 180) }));
    }
    function recordDraftAttempt(activity: number, index: number, elapsed_seconds: number,
        outcome: 'accepted' | 'rejected', detail: string) {
        const event = { activity, index, elapsed_seconds, outcome, detail: detail.slice(0, 180) };
        attemptHistory = [...attemptHistory.slice(-19), event];
        lastAttemptInfo = `Activity ${activity}, draft ${index}: ${outcome} after ${elapsed_seconds}s${outcome === 'rejected' ? ` · ${event.detail}` : ''}.`;
    }
    // Fixed first pass: one substantive draft in each of the 13 AI work areas.
    // Framework, scope and setup are displayed separately as source-backed
    // scaffolds; they MUST NOT be counted as AI generated or assessed.
    const firstPassTarget = generationOrder.length;
    onMount(() => {
        // Same-tab recovery only. Nothing is stored in SICO business tables.
        try {
            const raw = sessionStorage.getItem('sico-ai-quality-draft-v7');
            if (!raw) return;
            const cp = JSON.parse(raw);
            if (cp?.schema !== 'sico-authenticated-quality-drafts-v7' || !Array.isArray(cp.items)) return;
            if (cp.items.length > 200 || cp.items.some((r: any) => !r?.draft?.draft_reference)) return;
            organization = String(cp.scope?.organization ?? '').slice(0, 150);
            frameworkSearch = String(cp.scope?.framework ?? '').slice(0, 150);
            instruction = String(cp.scope?.objective ?? '').slice(0, 4000);
            if (organization.length < 2 || frameworkSearch.length < 2 || instruction.length < 20) return;
            qualityDrafts = cp.items;
            qualityIssues = Array.isArray(cp.issues) ? cp.issues.slice(-30) : [];
            nextAttemptBySlot = safeAttemptCounters(cp.attempt_counters);
            attemptHistory = safeAttemptHistory(cp.attempt_history);
            if (attemptHistory.length) { const last = attemptHistory[attemptHistory.length - 1]; lastAttemptInfo = `Last request: activity ${last.activity}, ${last.outcome} after ${last.elapsed_seconds}s.`; }
            targetDraftsPerActivity = Math.max(1, Math.min(12, ...generationOrder.map(step =>
                cp.items.filter((r: any) => r.activity_number === step).length)));
            draftedCaseScope = qualityScopeKey();
            localCheckpointInfo = 'Recovered drafts from this browser tab. Load framework access again before resuming.';
        } catch { /* A corrupt or unavailable tab checkpoint is ignored. */ }
    });

    function qualityScopeKey() {
        return JSON.stringify([organization.trim(), frameworkSearch.trim(), instruction.trim()]);
    }
    function checkpointPayload() {
        return {
            schema: 'sico-authenticated-quality-drafts-v7',
            scope: { organization: organization.trim(), framework: frameworkSearch.trim(), objective: instruction.trim() },
            source: authorizedFrameworkSource,
            items: qualityDrafts,
            target_per_activity: targetDraftsPerActivity,
            issues: qualityIssues,
            attempt_counters: nextAttemptBySlot,
            attempt_history: attemptHistory.slice(-20),
            business_records_written: false,
            full_framework_assessed: false,
            saved_in_browser_only: true
        };
    }
    function saveLocalDraftCheckpoint() {
        try {
            // sessionStorage keeps this draft in the current browser session;
            // users can download a JSON checkpoint for longer-term storage.
            sessionStorage.setItem('sico-ai-quality-draft-v7', JSON.stringify(checkpointPayload()));
            localCheckpointInfo = 'Progress saved in this browser session. Download a checkpoint to resume another day.';
        } catch { localCheckpointInfo = 'Browser storage is unavailable; download a checkpoint before leaving.'; }
    }
    function downloadQualityCheckpoint() {
        const url = URL.createObjectURL(new Blob([JSON.stringify(checkpointPayload(), null, 2)], { type: 'application/json' }));
        try { const link = document.createElement('a'); link.href=url; link.download='SICO-AI-quality-case-checkpoint.json'; link.click(); }
        finally { URL.revokeObjectURL(url); }
    }
    async function importQualityCheckpoint(event: Event) {
        const input = event.currentTarget as HTMLInputElement;
        const file = input.files?.[0];
        if (!file || draftedCaseBusy) return;
        try {
            if (file.size > 3000000) throw new Error('Checkpoint file is too large.');
            const parsed = JSON.parse(await file.text());
            let items: Record<string, any>[];
            if (parsed?.schema === 'sico-authenticated-quality-drafts-v7' && Array.isArray(parsed?.items)) {
                if (parsed?.scope?.organization !== organization.trim() ||
                    parsed?.scope?.framework !== frameworkSearch.trim() ||
                    parsed?.scope?.objective !== instruction.trim()) {
                    throw new Error('The checkpoint belongs to different case inputs. Use those original inputs first.');
                }
                items = parsed.items;
            } else if (String(parsed?.schema ?? '').startsWith('sico-quality') && Array.isArray(parsed?.generated_items)) {
                // Existing HTML-runner v5 checkpoint: show it here without
                // claiming imported draft content passed this v7 generation.
                if (parsed.organization !== organization.trim() || parsed.framework !== frameworkSearch.trim())
                    throw new Error('HTML checkpoint organization/framework do not match the form.');
                items = parsed.generated_items.map((item: any) => ({ ...item, provenance: 'imported_html_review_required' }));
                loadedOlderCheckpoint = true;
            } else {
                throw new Error('Unsupported checkpoint. Select a SICO quality generator JSON checkpoint.');
            }
            if (items.length > 200 || items.some((r: any) =>
                !/^draft-(?:0[1-9]|1[0-6])-(?:0[1-9]|1[0-2])$/.test(r?.draft?.draft_reference ?? '') ||
                !r?.draft?.title || !r?.draft?.record_type || !r?.activity_number)) {
                throw new Error('Checkpoint contains invalid draft references or content.');
            }
            if (new Set(items.map((r: any) => r.draft.draft_reference)).size !== items.length)
                throw new Error('Checkpoint contains duplicate draft references.');
            qualityDrafts = items;
            targetDraftsPerActivity = parsed?.schema === 'sico-authenticated-quality-drafts-v7'
                ? Math.max(1, Math.min(12, Number(parsed.target_per_activity) || 1))
                : Math.max(1, Math.min(12, ...generationOrder.map(step => items.filter(r => r.activity_number === step).length)));
            qualityIssues = [];
            nextAttemptBySlot = parsed?.schema === 'sico-authenticated-quality-drafts-v7'
                ? safeAttemptCounters(parsed.attempt_counters) : {};
            attemptHistory = parsed?.schema === 'sico-authenticated-quality-drafts-v7'
                ? safeAttemptHistory(parsed.attempt_history) : [];
            lastAttemptInfo = attemptHistory.length
                ? `Previous request: ${attemptHistory[attemptHistory.length - 1].outcome} after ${attemptHistory[attemptHistory.length - 1].elapsed_seconds}s.` : '';
            draftedCaseScope = qualityScopeKey();
            draftedCaseStages = [];
            draftedCaseNotice = `Loaded ${items.length} unsaved drafts. Imported records require review.`;
            draftedCaseError = '';
            saveLocalDraftCheckpoint();
        } catch (error) { draftedCaseError = error instanceof Error ? error.message : 'Checkpoint could not be loaded.'; }
        finally { input.value = ''; }
    }
    function nextQualitySlot(): { step: number, index: number } | null {
        for (const step of generationOrder) {
            const existing = qualityDrafts.filter((r) => r.activity_number === step);
            if (existing.length < targetDraftsPerActivity) {
                const used = new Set(existing.map(r => r.draft.draft_reference));
                for (let index = 1; index <= targetDraftsPerActivity; index++) {
                    if (!used.has(`draft-${String(step).padStart(2, '0')}-${String(index).padStart(2, '0')}`))
                        return { step, index };
                }
            }
        }
        return null;
    }
    async function generateNewCaseDrafts(restart = false) {
        if (draftedCaseBusy) return;
        if (organization.trim().length < 2 || frameworkSearch.trim().length < 2 || instruction.trim().length < 20) {
            draftedCaseError = 'Enter organization, exact framework and assessment objective.';
            return;
        }
        const frameworkConflict = explicitFrameworkConflict();
        if (frameworkConflict) { draftedCaseError = frameworkConflict; return; }
        if (restart) {
            qualityDrafts = []; qualityIssues = []; loadedOlderCheckpoint = false; targetDraftsPerActivity = 1;
            nextAttemptBySlot = {}; attemptHistory = []; lastAttemptInfo = '';
            draftedCaseStages = []; draftedCaseScope = qualityScopeKey();
            authorizedFrameworkSource = null; authorizedSourceRows = []; frameworkSourceSummary = '';
        } else if (draftedCaseScope !== qualityScopeKey()) {
            draftedCaseError = 'The three inputs changed. Restore original inputs or start a new draft case.';
            return;
        }
        draftedCaseBusy = true; draftedCaseError=''; draftedCaseNotice=''; stopAfterPhase=false;
        try {
            if (!authorizedFrameworkSource) await loadSicoAuthorizedFrameworkSource();
            while (!stopAfterPhase && qualityScopeKey() === draftedCaseScope) {
                const slot = nextQualitySlot();
                if (!slot) { draftedCaseNotice = 'First pass complete. Review the drafts; framework assessment is not complete.'; break; }
                currentGeneratingActivity = slot.step;
                const dependencyMap: Record<number, number[]> = {
                    4: [2, 3], 5: [4], 6: [4, 5], 7: [3, 4, 6], 8: [2, 7],
                    9: [3, 4, 7], 10: [1, 3, 7, 9], 11: [9, 10], 12: [6, 7, 11],
                    13: [7, 9, 12], 14: [3, 10, 11, 13], 15: [6, 12, 14], 16: [3, 6, 10, 11, 12, 15]
                };
                const allowedActivities = new Set([slot.step, ...(dependencyMap[slot.step] ?? [])]);
                const previous = qualityDrafts.filter((r) => allowedActivities.has(r.activity_number) &&
                    r?.draft?.status === 'new_unsaved_ai_draft_pending_verification').slice(-45).map((r) => ({
                    draft_reference: r.draft.draft_reference,
                    title: r.draft.title,
                    record_type: r.draft.record_type,
                    content: String(r.draft.content || '').slice(0, 220)
                }));
                // Only a source-backed SICO reference is selected; the backend
                // independently rechecks authorization before using it.
                const chosenRef = slot.step === 10 ? String(authorizedSourceRows[(slot.index - 1) % authorizedSourceRows.length]?.reference ?? '') : '';
                const key = slotAttemptKey(slot.step, slot.index);
                // Only one model request per activity slot per run. A rejected
                // response is visible immediately; Resume rotates the focus.
                const attempt = Math.min(30, nextAttemptBySlot[key] ?? 0);
                const started = Date.now();
                draftedCaseNotice = `Generating activity ${slot.step} of 16, draft ${slot.index}. One request at a time; accepted drafts are preserved.`;
                try {
                    const response = await sicoPostAction('quality_draft_one', {
                        organization_name: organization.trim(), framework_name: frameworkSearch.trim(),
                        problem: instruction.trim(), activity_number: String(slot.step),
                        draft_index: String(slot.index), source_digest: String(authorizedFrameworkSource?.source_digest ?? ''),
                        requirement_reference: chosenRef, previous_drafts: JSON.stringify(previous),
                        focus_attempt: String(attempt)
                    });
                    const item = (response.data as Record<string, any>)?.quality_draft_one;
                    if (!item || item.quality_contract_checked !== true || item.business_records_written !== false ||
                        item.activity_number !== slot.step || !item.draft?.draft_reference ||
                        item.draft.draft_reference !== key) {
                        throw new Error('The generated draft failed validation; previous drafts are preserved.');
                    }
                    const elapsed = Math.round((Date.now() - started) / 1000);
                    nextAttemptBySlot = { ...nextAttemptBySlot, [key]: Math.min(30, attempt + 1) };
                    recordDraftAttempt(slot.step, slot.index, elapsed, 'accepted', 'Draft validated');
                    qualityDrafts = [...qualityDrafts, item];
                    draftedCaseNotice = `Generated ${qualityDrafts.filter(r => r.provenance === 'qwen_quality_single_authenticated_v7').length} new quality-checked drafts. Last request: ${elapsed}s. Source: ${authorizedSourceRows.length} authorized requirements. No records saved.`;
                    saveLocalDraftCheckpoint();
                } catch (error) {
                    const elapsed = Math.round((Date.now() - started) / 1000);
                    const message = error instanceof Error ? error.message : 'Draft generation request failed.';
                    nextAttemptBySlot = { ...nextAttemptBySlot, [key]: Math.min(30, attempt + 1) };
                    recordDraftAttempt(slot.step, slot.index, elapsed, 'rejected', message);
                    qualityIssues = [...qualityIssues.slice(-29), `Activity ${slot.step}: ${message} (${elapsed}s)`];
                    draftedCaseError = `Activity ${slot.step} was not accepted after ${elapsed}s. ${message} The next Resume will try a different focus; previous drafts are preserved.`;
                    saveLocalDraftCheckpoint();
                    break;
                }
            }
        } catch (error) {
            draftedCaseError = error instanceof Error ? error.message : 'Generation failed; previous drafts remain.';
        } finally { draftedCaseBusy = false; currentGeneratingActivity = 0; saveLocalDraftCheckpoint(); }
    }

    function downloadAuthorizedRequirementSource() {
        if (!authorizedFrameworkSource?.complete_source_snapshot || !authorizedSourceRows.length) return;
        const payload = {
            schema: 'sico-user-exported-authorized-framework-requirements-v1',
            source_status: 'read_from_SICO_under_current_logged_in_user',
            source: authorizedFrameworkSource,
            requirements: authorizedSourceRows,
            official_edition_independently_verified: false,
            compliance_assessment_completed: false,
            business_records_written: false
        };
        const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }));
        try {
            const a = document.createElement('a');
            a.href = url; a.download = 'SICO-authorized-framework-source-READ-ONLY.json'; a.click();
        } finally { URL.revokeObjectURL(url); }
    }

    function downloadCaseDraft() {
        if (!draftedCaseStages.length) return;
        const caseDraft = {
            schema: 'sico-unsaved-case-drafts-v1', organization_name: organization.trim(),
            framework_name: frameworkSearch.trim(), objective: instruction.trim(),
            generated_activity_count: draftedCaseStages.length,
            authorized_framework_source: authorizedFrameworkSource,
            authorized_requirements: authorizedFrameworkSource?.complete_source_snapshot ? authorizedSourceRows : [],
            authorized_requirements_not_compliance_verdict: true,
            business_records_written: false,
            note: 'Unverified hypothetical drafts. No GRC database records created.',
            activities: draftedCaseStages
        };
        const url = URL.createObjectURL(new Blob([JSON.stringify(caseDraft, null, 2)], { type: 'application/json' }));
        try {
            const a = document.createElement('a');
            a.href = url; a.download = 'SICO-new-GRC-case-DRAFT.json'; a.click();
        } finally { URL.revokeObjectURL(url); }
    }

    let creationBusy = $state(false);
    let creationError = $state('');
    let creationNotice = $state('');
    let creationChoices = $state<Record<string, any> | null>(null);
    let confirmCaseCreation = $state(false);
    let caseSaved = $state(false);
    let stageBusy = $state(false);
    let stageNotice = $state('');
    let stageError = $state('');
    let stageConfirmed = $state(false);
    let stageHumanFacts = $state('');
    let frameworkBusinessContext = $state('');
    let frameworkBatchSize = $state(2);
    let fullReview = $state<ReviewCheckpoint | null>(null);
    let fullReviewBusy = $state(false);
    let fullReviewAutomatic = $state(false);
    let fullReviewPause = $state(false);
    let fullReviewError = $state('');
    let fullReviewNotice = $state('');
    let fullReviewCandidates = $state<string[]>([]);
    let fullReviewShown = $state(8);
    const fullReviewPercent = $derived(fullReview?.coverage.accessible_total
        ? Math.round(fullReview.coverage.reviewed_through * 10000 / fullReview.coverage.accessible_total) / 100 : 0);
    const visibleFrameworkReviews = $derived(fullReview?.requirement_reviews.slice(0, fullReviewShown) ?? []);

    function currentFrameworkScope(): ReviewScope {
        return {
            organization_name: organization.trim(), framework_name: frameworkSearch.trim(),
            problem: instruction.trim(), business_context: frameworkBusinessContext.trim()
        };
    }

    function changedFrameworkInputs() {
        // A running model request is allowed to finish, but later batches will
        // not silently mix updated inputs with an earlier signed cursor.
        fullReviewPause = true;
        if (fullReview) fullReviewNotice = 'Inputs changed. Restore the original inputs to resume, or explicitly start a new review.';
    }

    async function runFullFrameworkReview(automatic: boolean, restart = false) {
        if (fullReviewBusy) return;
        const scope = currentFrameworkScope();
        if (scope.organization_name.length < 2 || scope.organization_name.length > 150 ||
            scope.framework_name.length < 2 || scope.framework_name.length > 150 ||
            scope.problem.length < 20 || scope.problem.length > 4000 ||
            scope.business_context.length > 1200) {
            fullReviewError = 'Enter the organization, exact framework and assessment objective in the three fields above.';
            return;
        }
        if (restart) {
            fullReview = null;
            fullReviewCandidates = [];
            fullReviewShown = 8;
        } else if (fullReview && scopeKey(fullReview.scope) !== scopeKey(scope)) {
            fullReviewError = 'These inputs differ from the existing checkpoint. Restore them, or click Start new review.';
            return;
        }
        if (fullReview?.coverage.complete) return;
        fullReviewBusy = true;
        fullReviewAutomatic = automatic;
        fullReviewPause = false;
        fullReviewError = '';
        fullReviewNotice = '';
        try {
            do {
                if (fullReviewPause || scopeKey(currentFrameworkScope()) !== scopeKey(scope)) break;
                const result = await sicoPostAction('ai_framework_batch', {
                    organization_name: scope.organization_name,
                    framework_name: scope.framework_name,
                    problem: scope.problem,
                    framework_business_context: scope.business_context,
                    framework_batch_size: String(frameworkBatchSize),
                    framework_cursor: fullReview?.next_cursor ?? ''
                });
                const response = (result.data as Record<string, any>)?.ai_framework_batch;
                const batch = response?.framework_batch;
                if (!batch) throw new Error('No framework review was returned.');
                if (batch.status !== 'partial' && batch.status !== 'complete') {
                    fullReviewCandidates = Array.isArray(batch.candidate_frameworks)
                        ? batch.candidate_frameworks.map(String).slice(0, 8) : [];
                    throw new Error('An exact authorized framework and accessible requirement list could not be found. Check the name and edition.');
                }
                if (scopeKey(currentFrameworkScope()) !== scopeKey(scope)) {
                    throw new Error('Inputs changed during generation. This batch was not appended. Return to the original inputs and retry.');
                }
                fullReview = applyFrameworkBatch(fullReview, scope, batch);
            } while (automatic && !fullReviewPause && !fullReview?.coverage.complete);
            if (fullReview?.coverage.complete) {
                fullReviewNotice = 'All accessible assessable requirements have provisional reviews. Export the checkpoint and arrange evidence-based human verification.';
            } else if (fullReviewPause) {
                fullReviewNotice = 'Paused after the current batch. Export the checkpoint before refreshing the page.';
            } else if (fullReview) {
                fullReviewNotice = 'Batch completed. Continue when ready, or export a checkpoint.';
            }
        } catch (error) {
            fullReviewError = error instanceof Error ? error.message : 'The current generation batch failed. Earlier reviews are preserved.';
        } finally {
            fullReviewBusy = false;
            fullReviewAutomatic = false;
        }
    }


    async function prepareNewGrcCase() {
        if (creationBusy || preparedWorkflow || caseSaved) return;
        if (organization.trim().length < 2 || frameworkSearch.trim().length < 2 || instruction.trim().length < 20) {
            creationError = 'Enter an organization, exact loaded framework and objective of at least 20 characters.';
            return;
        }
        creationBusy = true;
        creationError = '';
        creationNotice = '';
        try {
            // This already exists in +page.server.ts and invokes the authenticated,
            // permission-checked Django lifecycle intake. No parallel GRC writer.
            const response = await sicoPostAction('lifecycle_intake', {
                organization_name: organization.trim(),
                framework_name: frameworkSearch.trim(),
                problem: instruction.trim(),
                skip_legacy_generation: 'yes',
                selected_framework_id: frameworkConfirmation,
                selected_organization_id: organizationConfirmation
            });
            const data = response.data as Record<string, any>;
            if (data?.lifecycle_choices) {
                creationChoices = data.lifecycle_choices;
                creationNotice = 'Choose the exact authorized organization/framework record before creating a case.';
                return;
            }
            const prepared = data?.workflow_prepared;
            if (!prepared?.engagement_id || !prepared?.prepared_digest || !prepared?.review?.operation_payload) {
                throw new Error('The original SICO case-setup service did not provide a verified review.');
            }
            preparedWorkflow = prepared;
            activeEngagement = String(prepared.engagement_id);
            lifecycleProgress = prepared.lifecycle ?? null;
            recordedApproval = null;
            confirmCaseCreation = false;
            creationChoices = null;
            creationNotice = 'New assessment, scope and optional risk assessment are PREPARED through SICO. Review the exact creation plan before approving.';
        } catch (err) {
            creationError = err instanceof Error ? err.message : 'Unable to prepare this new GRC case.';
        } finally {
            creationBusy = false;
        }
    }

    async function approveAndCreateCase() {
        if (creationBusy || caseSaved || !confirmCaseCreation || !preparedWorkflow?.engagement_id || !preparedWorkflow?.prepared_digest) return;
        creationBusy = true;
        creationError = '';
        try {
            // The existing SvelteKit action independently obtains server-side approval.
            // If its restricted case writer is enabled, it commits the SAME reviewed
            // payload through the existing atomic GRC service. Otherwise no case is saved.
            const response = await sicoPostAction('workflow_approve', {
                engagement_id: String(preparedWorkflow.engagement_id),
                prepared_digest: String(preparedWorkflow.prepared_digest),
                confirm_reviewed: 'yes'
            });
            const data = response.data as Record<string, any>;
            recordedApproval = data?.workflow_approved ?? null;
            if (data?.workflow_committed?.business_records_written === true) {
                caseSaved = true;
                lifecycleProgress = data.workflow_committed.lifecycle ?? lifecycleProgress;
                creationNotice = 'SICO confirmed new assessment records were created through its original GRC service.';
            } else {
                creationError = String(data?.workflow_error ?? 'Approval recorded, but the GRC case writer is disabled or saving was not independently verified. No case is claimed to be created.');
            }
        } catch (err) {
            creationError = err instanceof Error ? err.message : 'Case creation could not be verified; do not submit a duplicate.';
        } finally {
            creationBusy = false;
        }
    }

    async function prepareNextRealGrcStage() {
        if (stageBusy || !caseSaved || !activeEngagement || lifecycleProposal) return;
        stageBusy = true;
        stageError = '';
        stageNotice = '';
        try {
            const response = await sicoPostAction('lifecycle_next', {
                engagement_id: activeEngagement,
                human_facts: stageHumanFacts.trim().slice(0, 1200)
            });
            const result = (response.data as Record<string, any>)?.lifecycle_next;
            if (!result) throw new Error('No verified lifecycle result was returned.');
            lifecycleProgress = result.lifecycle ?? lifecycleProgress;
            if (result.status === 'prepared_for_human_review' && result.review?.operation_payload) {
                lifecycleProposal = result;
                stageConfirmed = false;
                lifecycleApproval = null;
                stageNotice = `The ${result.stage} operation is prepared using SICO's existing GRC service. Nothing has been saved yet.`;
            } else {
                stageError = String(result.reason ?? result.questions?.join(' ') ?? 'More information or permission is needed before a new record can be prepared.');
            }
        } catch (err) {
            stageError = err instanceof Error ? err.message : 'The GRC stage could not be prepared.';
        } finally {
            stageBusy = false;
        }
    }

    async function approveNextRealGrcStage() {
        if (stageBusy || !stageConfirmed || !lifecycleProposal?.prepared_digest || !activeEngagement) return;
        stageBusy = true;
        stageError = '';
        try {
            const response = await sicoPostAction('lifecycle_stage_approve', {
                engagement_id: activeEngagement,
                stage: String(lifecycleProposal.stage),
                prepared_digest: String(lifecycleProposal.prepared_digest),
                confirm_reviewed: 'yes'
            });
            lifecycleApproval = (response.data as Record<string, any>)?.lifecycle_stage_approved ?? null;
            stageNotice = lifecycleApproval?.commit_enabled === true
                ? 'Human approval recorded. A separate click is required to create this new GRC record.'
                : 'Approval recorded, but this GRC writer is disabled. No business records were created.';
        } catch (err) {
            stageError = err instanceof Error ? err.message : 'Stage approval failed.';
        } finally {
            stageBusy = false;
        }
    }

    async function commitNextRealGrcStage() {
        if (stageBusy || !lifecycleApproval?.approved || lifecycleApproval?.commit_enabled !== true || !lifecycleProposal || !activeEngagement) return;
        stageBusy = true;
        stageError = '';
        try {
            const response = await sicoPostAction('lifecycle_stage_commit', {
                engagement_id: activeEngagement,
                stage: String(lifecycleProposal.stage),
                prepared_digest: String(lifecycleProposal.prepared_digest),
                confirm_reviewed: 'yes'
            });
            const result = (response.data as Record<string, any>)?.lifecycle_stage_committed;
            if (result?.business_records_written !== true) throw new Error('Original SICO service did not verify that the record was saved.');
            lifecycleProgress = result.lifecycle ?? lifecycleProgress;
            stageNotice = `New ${lifecycleProposal.stage} records were saved through SICO's existing GRC service.`;
            lifecycleProposal = null;
            lifecycleApproval = null;
            stageConfirmed = false;
        } catch (err) {
            stageError = err instanceof Error ? err.message : 'Stage save could not be verified; do not repeat blindly.';
        } finally {
            stageBusy = false;
        }
    }

    function downloadFullReview() {
        if (!fullReview || fullReviewBusy) return;
        const blob = new Blob([JSON.stringify(fullReview, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `SICO_Activity1_v3_checkpoint_${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
        fullReviewNotice = 'Checkpoint exported to your device. Keep it private: it contains your assessment context and draft responses.';
    }

    async function importFullReview(event: Event) {
        if (fullReviewBusy) return;
        const field = event.currentTarget as HTMLInputElement;
        const file = field.files?.[0];
        if (!file) return;
        try {
            if (file.size > 6 * 1024 * 1024) throw new Error('Checkpoint exceeds the 6 MB import limit.');
            const parsed = validateCheckpoint(JSON.parse(await file.text()));
            // Restore the exact previous inputs before allowing a signed-cursor continuation.
            organization = parsed.scope.organization_name;
            frameworkSearch = parsed.scope.framework_name;
            instruction = parsed.scope.problem;
            frameworkBusinessContext = parsed.scope.business_context;
            fullReview = parsed;
            fullReviewShown = 8;
            fullReviewCandidates = [];
            fullReviewError = '';
            fullReviewNotice = 'Imported an unverified, client-held draft. The backend will re-check the signed cursor, permissions and framework inventory on the next batch.';
        } catch (error) {
            fullReviewError = error instanceof Error ? error.message : 'Checkpoint could not be imported.';
        } finally {
            field.value = '';
        }
    }

    function clearStaleCase() {
        generatedSixteen = [];
        generatedFor = '';
        sixteenError = '';
        caseSaveNotice = '';
        preparedWorkflow = null;
        recordedApproval = null;
        lifecycleProgress = null;
        activeEngagement = '';
    }

    async function sicoPostAction(action: string, data: Record<string, string>) {
        const payload = new FormData();
        for (const [key, value] of Object.entries(data)) payload.set(key, value);
        const res = await fetch(`?/${action}`, {
            method: 'POST', body: payload, headers: { accept: 'application/json' }
        });
        const parsed = deserialize(await res.text());
        // An expired session makes the server hooks redirect to /login. Say so instead of
        // the generic failure; accepted drafts stay in this tab's sessionStorage checkpoint.
        if (parsed.type === 'redirect' && parsed.location.startsWith('/login')) {
            throw new Error('Your SICO session has expired. Sign in again, then open SICO AI and choose "Resume automatic generation". Accepted drafts are kept in this browser tab.');
        }
        if (parsed.type !== 'success') {
            const body = parsed.type === 'failure' ? (parsed.data as Record<string, any>) : null;
            throw new Error(String(body?.case_draft_error ?? body?.framework_batch_error ?? body?.control_error ?? body?.ai_sixteen_error ?? body?.lifecycle_error ?? body?.workflow_error ?? 'The requested operation could not finish.'));
        }
        return parsed;
    }

    async function loadSavedControlProgress(caseId = '') {
        try {
            const response = await sicoPostAction('requirement_review', {
                action: 'status', engagement_id: caseId || activeEngagement
            });
            const progress = (response.data as Record<string, any>)?.control_review?.progress;
            if (progress?.case_id) {
                controlProgress = progress;
                controlError = '';
            }
        } catch {
            // An unprovisioned or not-yet-saved company has no control records.
            // Do not display a misleading result or ask for manual UUIDs.
        }
    }

    async function generateAndSaveNextControl() {
        if (controlBusy || !controlProgress?.case_id) return;
        controlBusy = true;
        controlError = '';
        controlNotice = '';
        try {
            const response = await sicoPostAction('requirement_review', {
                action: 'generate_and_save', engagement_id: activeEngagement,
                confirm_preliminary_write: 'true'
            });
            const result = (response.data as Record<string, any>)?.control_review;
            if (result?.business_records_written !== true || result?.verified !== true ||
                !result?.progress?.case_id || result?.record?.result !== 'not_assessed') {
                throw new Error('The audit record could not be independently verified as saved.');
            }
            controlProgress = result.progress;
            controlNotice = 'A control-specific review was generated and retrieved through SICO.';
        } catch (error) {
            controlError = error instanceof Error ? error.message : 'Control review could not be saved.';
        } finally {
            controlBusy = false;
        }
    }


    async function startGeneratedCase(event: SubmitEvent) {
        event.preventDefault();
        await generateConnectedThrough(16);
    }

    async function generateConnectedThrough(lastActivity: number) {
        if (sixteenBusy || !organization.trim() || !frameworkSearch.trim() || instruction.trim().length < 20) return;
        sixteenBusy = true;
        sixteenError = '';
        caseSaveNotice = '';
        const submitted = {
            organization_name: organization.trim(), framework_name: frameworkSearch.trim(), problem: instruction.trim()
        };
        const fingerprint = JSON.stringify(submitted);
        if (fingerprint !== generatedFor) {
            generatedSixteen = [];
            generatedFor = fingerprint;
        }
        try {
            // A single click generates sequentially; each validated result is
            // displayed immediately and a retry resumes the first missing item.
            for (let number = generatedSixteen.length + 1; number <= lastActivity; number++) {
                // Prior Qwen work products form the shared, unverified case context.
                // Only bounded earlier-stage text and proposed objects are forwarded.
                const keyStages = new Set([2, 4, 6, 7, 9, 11, 12]);
                const prior = generatedSixteen.filter((item) =>
                    keyStages.has(Number(item.number)) || Number(item.number) >= number - 2
                ).map((item) => ({
                    number: Number(item.number),
                    analysis: String(item.analysis ?? '').slice(0, 180),
                    proposed_work: String(item.proposed_work ?? '').slice(0, 180),
                    case_profile: item.case_profile ?? null,
                    candidate_assets: item.candidate_assets ?? []
                }));
                const response = await sicoPostAction('ai_sixteen_item', {
                    ...submitted, activity_number: String(number),
                    case_context: JSON.stringify(prior)
                });
                const result = (response.data as Record<string, any>)?.ai_sixteen_item;
                if (!result || result.activity_number !== number ||
                    !result.activity || result.activity.number !== number ||
                    typeof result.activity.analysis !== 'string') {
                    throw new Error(`Activity ${number} returned an invalid draft result.`);
                }
                generatedSixteen = [...generatedSixteen, result.activity];
            }
        } catch (err) {
            sixteenError = err instanceof Error ? err.message : 'Draft generation stopped unexpectedly.';
        }
        // This phase is GENERATION ONLY by user request. Never try to create,
        // approve or save an audit or tenant after finishing the 16 drafts.
        sixteenBusy = false;
    }
    const latestResponse = $derived(form as Record<string, any> | null);
    $effect(() => {
        if (latestResponse?.sico_run) lastAgentRun = latestResponse;
        if (latestResponse?.workflow_options) eligibleOptions = latestResponse.workflow_options;
        if (latestResponse?.workflow_prepared) {
            generatedAssessment = latestResponse?.generated_assessment ?? null;
            generationError = String(latestResponse?.generation_error ?? '');
            preparedWorkflow = latestResponse.workflow_prepared;
            activeEngagement = String(preparedWorkflow?.engagement_id ?? '');
            if (preparedWorkflow?.lifecycle) lifecycleProgress = preparedWorkflow.lifecycle;
            recordedApproval = null;
        }
        if (latestResponse?.workflow_review) {
            preparedWorkflow = latestResponse.workflow_review;
            recordedApproval = latestResponse.workflow_review.approved ?
                { commit_enabled: latestResponse.workflow_review.commit_enabled } : null;
        }
        if (latestResponse?.workflow_approved) recordedApproval = latestResponse.workflow_approved;
        const newlySavedCase = latestResponse?.workflow_committed?.business_records_written === true
            ? String(preparedWorkflow?.engagement_id ?? activeEngagement) : '';
        if (newlySavedCase && newlySavedCase !== lastControlCaseLoaded) {
            lastControlCaseLoaded = newlySavedCase;
            void loadSavedControlProgress(newlySavedCase);
        }
        if (latestResponse?.workflow_committed?.workflow) {
            activeEngagement = String(preparedWorkflow?.engagement_id ?? activeEngagement);
            if (latestResponse.workflow_committed.lifecycle)
                lifecycleProgress = latestResponse.workflow_committed.lifecycle;
        }
        if (latestResponse?.lifecycle_status) {
            lifecycleProgress = latestResponse.lifecycle_status;
            activeEngagement = String(latestResponse.lifecycle_status.engagement_id ?? activeEngagement);
        }
        if (latestResponse?.lifecycle_next) {
            lifecycleProposal = latestResponse.lifecycle_next;
            lifecycleApproval = null;
            if (lifecycleProposal?.lifecycle) lifecycleProgress = lifecycleProposal.lifecycle;
        }
        if (latestResponse?.lifecycle_stage_approved) lifecycleApproval = latestResponse.lifecycle_stage_approved;
        if (latestResponse?.lifecycle_stage_committed) {
            if (latestResponse.lifecycle_stage_committed.lifecycle)
                lifecycleProgress = latestResponse.lifecycle_stage_committed.lifecycle;
            lifecycleProposal = null;
            lifecycleApproval = null;
        }
    });
    const result = $derived((latestResponse?.sico_run ? latestResponse : lastAgentRun) as Record<string, any> | null);
    const run = $derived(result?.sico_run as Record<string, any> | undefined);
    const plan = $derived(result?.sico_plan as Record<string, any> | undefined);
    const agent = $derived(result?.sico_agent as Record<string, any> | undefined);
    const discovery = $derived(result?.discovery ?? result?.records ?? null);
    const advisory = $derived(result?.draft ?? result?.case_plan ?? result?.case_intake ?? null);
    const providerMode = $derived(String(advisory?.source_summary?.provider_mode ?? 'unknown'));
    const providerFailed = $derived(/fallback|error|failed|unavailable/i.test(providerMode));
    const recordsReady = $derived(run?.discovery === 'completed');
    const intakeReady = $derived(run?.intake === 'completed' && !providerFailed);
    const recordGroups = $derived(summarizeRecordGroups(discovery));
    const advisoryNotes = $derived(intakeReady ? collectPlainNotes(advisory) : []);
    const discoveryFailure = $derived(String(result?.discovery_error ?? '').trim());
    const intakeFailure = $derived(String(result?.intake_error ?? '').trim());
    const needsOrganization = $derived(!organization.trim() && (
        /organization|domain/i.test(discoveryFailure) || !recordsReady
    ));

    const examples = [
        'Assess the cybersecurity compliance of Demo Bank in Saudi Arabia against NCA ECC. Look up permitted records, identify missing information, and propose next steps for human review.',
        'Prepare an ISO 27001:2022 assessment plan. Confirm the scope, discover authorized records, and identify evidence that still needs review.',
        'Investigate our cybersecurity risk exposure, existing safeguards, and the additional information needed for a formal risk assessment.',
        'Assess our readiness for an internal security audit. Report only verified records and identify unanswered questions.'
    ];

    type Group = { label: string; count: number; examples: string[] };
    function isObject(v: unknown): v is Record<string, unknown> {
        return !!v && typeof v === 'object' && !Array.isArray(v);
    }
    function plainText(v: unknown): string {
        if (typeof v !== 'string') return '';
        const s = v.replace(/\s+/g, ' ').trim();
        if (!s || /^[\[{]/.test(s) || s.length > 650 || /\"[a-z_]+\"\s*:/.test(s)) return '';
        return s;
    }
    // Presentation only: preserve the original keys and values in checkpoint JSON.
    // Turns labels like asset_type / owner_role / linkedRiskReference into readable text.
    function displayFieldLabel(raw: unknown): string {
        const label = String(raw ?? '')
            .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
            .replace(/[_-]+/g, ' ')
            .replace(/\s*\/\s*/g, ' / ')
            .replace(/\s+/g, ' ')
            .trim();
        const abbreviations = new Set(['AI', 'API', 'CSF', 'CVSS', 'GRC', 'ID', 'IP', 'ISO', 'IT', 'MFA', 'NCA', 'PDPL', 'RBAC', 'RPO', 'RTO', 'SICO', 'SOC', 'URL']);
        return label.split(' ').map(part => {
            if (!part || part === '/') return part;
            const upper = part.toUpperCase();
            return abbreviations.has(upper) ? upper : part.charAt(0).toUpperCase() + part.slice(1).toLowerCase();
        }).join(' ');
    }

    function itemLabel(v: unknown): string {
        if (!isObject(v)) return '';
        for (const k of ['name', 'title', 'ref_id', 'label']) {
            const name = plainText(v[k]);
            if (name) return name.slice(0, 95);
        }
        return '';
    }
    function summarizeRecordGroups(source: unknown): Group[] {
        const found = new Map<string, Group>();
        const categories: [RegExp, string][] = [
            [/framework|librar/i, 'Frameworks'],
            [/asset/i, 'Assets'],
            [/polic/i, 'Policies'],
            [/applied.control|safeguard|^controls?$/i, 'Controls'],
            [/eviden/i, 'Evidence'],
            [/assessment/i, 'Assessments'],
            [/risk.scenario/i, 'Risk scenarios'],
            [/domain|folders?/i, 'Organizations / folders']
        ];
        function walk(v: unknown, depth: number) {
            if (depth > 4 || !isObject(v)) return;
            for (const [key, child] of Object.entries(v)) {
                const type = categories.find(([re]) => re.test(key))?.[1];
                if (type && Array.isArray(child)) {
                    const labelled = child.map(itemLabel).filter(Boolean);
                    if (child.length || labelled.length) {
                        const group = found.get(type) ?? { label: type, count: 0, examples: [] };
                        group.count += child.length;
                        for (const name of labelled) {
                            if (group.examples.length < 3 && !group.examples.includes(name)) group.examples.push(name);
                        }
                        found.set(type, group);
                    }
                } else if (isObject(child)) {
                    walk(child, depth + 1);
                }
            }
        }
        walk(source, 0);
        return [...found.values()].slice(0, 8);
    }
    function collectPlainNotes(source: unknown): string[] {
        const output: string[] = [];
        const matching = /summary|objective|recommendation|next.step|question|missing|warning|human.review/i;
        function walk(v: unknown, depth: number) {
            if (depth > 3 || output.length >= 5) return;
            if (Array.isArray(v)) {
                for (const child of v.slice(0, 6)) {
                    const text = plainText(child);
                    if (text && !output.includes(text)) output.push(text);
                    else if (isObject(child)) walk(child, depth + 1);
                }
                return;
            }
            if (!isObject(v)) return;
            for (const [key, child] of Object.entries(v)) {
                if (output.length >= 5) return;
                if (!matching.test(key)) continue;
                const text = plainText(child);
                if (text && !output.includes(text)) output.push(text);
                else if (Array.isArray(child) || isObject(child)) walk(child, depth + 1);
            }
        }
        walk(source, 0);
        return output;
    }
</script>

<svelte:head>
    <title>SICO AI Next — Assessment Workspace</title>
    <meta name="description" content="Generate structured, reviewable GRC case drafts using the existing SICO workspace." />
</svelte:head>

<div class="workspace">
    <div class="shell">
        <header class="topbar">
            <div class="logo">✦</div>
            <div><strong>SICO AI</strong><small>ASSESSMENT WORKSPACE</small></div>
            <span class="scope-pill">Uses your GRC permissions</span>
        </header>

        <section class="report" aria-label="Build a GRC case" id="start-grc-case">
            <div class="report-head">
                <h2>Build a GRC case</h2>
                <span class="status-pill">One workflow · Your existing SICO GRC library</span>
            </div>
            <p class="report-intro">Enter three details to generate structured GRC case drafts across SICO’s 16 activities, including proposed assets, risks, controls, policies, evidence requests, tasks and reports. Drafts remain unsaved and do not establish compliance.</p>
            <form class="workflow-form" onsubmit={(event) => { event.preventDefault(); void generateNewCaseDrafts(true); }}>
                <label>1. Organization
                    <input name="organization_name" bind:value={organization} disabled={draftedCaseBusy} required minlength="2" maxlength="150" placeholder="Organization name (new or existing)" />
                </label>
                <label>2. Framework
                    <input name="framework_name" bind:value={frameworkSearch} disabled={draftedCaseBusy} required minlength="2" maxlength="150" placeholder="Enter the exact framework name from SICO’s library" />
                </label>
                <label>3. GRC case objective
                    <textarea name="problem" bind:value={instruction} disabled={draftedCaseBusy} required minlength="20" maxlength="4000" rows="4" placeholder="Create a complete new GRC case with proposed assets, controls, risks, policy drafts, evidence requests, remediation and reports."></textarea>
                </label>
                {#if qualityDrafts.length === 0}
                    {#if !draftedCaseBusy && qualityIssues.length && draftedCaseScope === qualityScopeKey()}
                        <button type="button" onclick={() => void generateNewCaseDrafts(false)}>Resume failed draft with a different focus</button>
                    {:else}
                        <button type="submit" disabled={draftedCaseBusy || instruction.trim().length < 20 || !organization.trim() || !frameworkSearch.trim()}>
                            {draftedCaseBusy ? 'Generating GRC case drafts…' : 'Build GRC case with AI'}
                        </button>
                    {/if}
                {/if}
                <label class="checkpoint-upload">Restore an earlier draft session from a JSON checkpoint
                    <input type="file" accept=".json,application/json" disabled={draftedCaseBusy} onchange={(event) => { void importQualityCheckpoint(event); }} />
                </label>
            </form>
            {#if draftedCaseError}<p class="message error" role="alert">{draftedCaseError}</p>{/if}
            {#if draftedCaseNotice}<p class="message" role="status">{draftedCaseNotice}</p>{/if}
            {#if draftedCaseBusy || qualityDrafts.length > 0 || authorizedFrameworkSource}
                <div class="framework-coverage" aria-label="New SICO GRC case draft results">
                    <div class="framework-coverage-title">
                        <h3>Generated GRC case drafts — {qualityDrafts.filter(r => r.provenance === 'qwen_quality_single_authenticated_v7').length} new AI-generated drafts</h3>
                        <span class="footnote">No records saved · No compliance verdict</span>
                    </div>
                    <p class="source-note">{frameworkSourceSummary || 'Framework catalog not loaded yet.'}</p>
                    <p class="footnote">Framework, assessment charter and business scope are inputs to confirm, not model-generated assessment results.</p>
                    <div class="framework-meter"><div class="framework-meter-fill" style={`width: ${Math.round(generationOrder.filter(n => qualityDrafts.some(r => r.activity_number === n)).length / firstPassTarget * 100)}%`}></div></div>
                    <p class="footnote">First-pass areas with drafts: {generationOrder.filter(n => qualityDrafts.some(r => r.activity_number === n)).length}/{firstPassTarget}. This does not indicate framework requirement coverage.</p>
                    <div class="framework-actions">
                        {#if draftedCaseBusy}
                            <span class="footnote">Generating activity {currentGeneratingActivity} of 16 · Reviewing each draft individually.</span>
                            <button type="button" onclick={() => { stopAfterPhase = true; }}>Pause after current request</button>
                        {:else}
                            {#if generationOrder.some(n => !qualityDrafts.some(r => r.activity_number === n))}
                                <button type="button" onclick={() => void generateNewCaseDrafts(false)}>Resume automatic generation</button>
                            {/if}
                            <button type="button" onclick={() => void generateNewCaseDrafts(true)}>Start a new case</button>
                        {/if}
                        {#if qualityDrafts.length}
                            <button type="button" onclick={downloadQualityCheckpoint}>Download checkpoint</button>
                            {#if !draftedCaseBusy && generationOrder.every(n => qualityDrafts.filter(r => r.activity_number === n).length >= targetDraftsPerActivity) && targetDraftsPerActivity < 12}
                                <button type="button" onclick={() => { targetDraftsPerActivity += 1; saveLocalDraftCheckpoint(); void generateNewCaseDrafts(false); }}>Generate more across all activities</button>
                            {/if}
                        {/if}
                        {#if authorizedFrameworkSource?.complete_source_snapshot}
                            <button type="button" onclick={downloadAuthorizedRequirementSource}>Download framework requirements</button>
                        {/if}
                    </div>
                    {#if lastAttemptInfo}<p class="footnote" role="status">{lastAttemptInfo}</p>{/if}
                    {#if attemptHistory.length}
                        <details class="generation-timing">
                            <summary>Generation request history ({attemptHistory.length} most recent)</summary>
                            <ul>
                                {#each [...attemptHistory].reverse() as attempt}
                                    <li>Activity {attempt.activity}, draft {attempt.index}: {attempt.outcome === 'accepted' ? 'Accepted' : 'Rejected'} · {attempt.elapsed_seconds}s · {attempt.detail}</li>
                                {/each}
                            </ul>
                        </details>
                    {/if}
                    {#if localCheckpointInfo}<p class="footnote">{localCheckpointInfo}</p>{/if}
                    {#if qualityIssues.length}<p class="footnote">Failed attempts: {qualityIssues.length}. Last: {qualityIssues[qualityIssues.length-1]}</p>{/if}
                    {#each qualityDrafts as item (item.draft.draft_reference)}
                        <article class="sico-case-draft">
                            <h4>{item.draft.title} <span class="footnote">{item.draft.draft_reference}</span></h4>
                            <p class="footnote">Activity {item.activity_number}: {item.activity_name} · SICO Module: {displayFieldLabel(item.target_existing_sico_model)} · {item.provenance === 'qwen_quality_single_authenticated_v7' ? 'AI-generated draft · Pending verification' : 'Imported draft · Review required'}</p>
                            <p>{item.draft.content}</p>
                            <dl>
                                {#each item.draft.proposed_attributes ?? [] as attr}
                                    <div><dt>{displayFieldLabel(attr.field)}</dt><dd>{attr.proposed_value}</dd></div>
                                {/each}
                            </dl>
                            <p><strong>Evidence to Request:</strong> {item.draft.evidence_request}</p>
                            <p><strong>Verification Question:</strong> {item.draft.verification_question}</p>
                            {#if item.draft.related_draft_references?.length}
                                <p><strong>Related Drafts:</strong> {item.draft.related_draft_references.join(', ')}</p>
                            {/if}
                            <p class="footnote">Hypothetical, unsaved. Not verified organization data or proof of compliance.</p>
                        </article>
                    {/each}
                </div>
            {/if}
            <p class="footnote">These are proposed drafts structured around existing SICO GRC models. They have not been verified against the organization or saved as business records.</p>
        </section>
        <footer>SICO AI · One case-building workflow · AI-generated GRC drafts across 16 activities · No database writes.</footer>
    </div>
</div>

<style>
    .workspace{min-height:100vh;background:radial-gradient(ellipse at 60% 0%,#123950 0,transparent 46%),#080f20;color:#e9f4ff;font-family:inherit}
    .shell{max-width:1060px;margin:auto;padding:34px 28px 65px}
    .topbar{display:flex;gap:12px;align-items:center}.logo{display:grid;place-items:center;width:42px;height:42px;border:1px solid #438c8c;border-radius:12px;background:#12404a;font-size:25px;color:#78e2ce}.topbar strong{display:block;font-size:17px;letter-spacing:.08em}.topbar small{font-size:10px;letter-spacing:.14em;color:#a2b7cb}.scope-pill,.status-pill{margin-left:auto;font-size:12px;color:#a3eadc;border:1px solid #37636a;border-radius:30px;padding:8px 12px}
    .hero{margin:65px auto 32px;max-width:760px;text-align:center}.eyebrow{font-size:11px;letter-spacing:.16em;color:#72d9c4;font-weight:800}.hero h1{font-size:clamp(32px,5vw,56px);letter-spacing:-.04em;line-height:1.13;margin:14px 0}.hero em{font-style:normal;color:#71e0cb}.hero>p:last-child{color:#adbed1;line-height:1.75}
    .prompt-form{background:#121f34;border:1px solid #355166;border-radius:18px;padding:16px;box-shadow:0 20px 60px #0005}.prompt-form textarea{width:100%;box-sizing:border-box;border:0;resize:vertical;background:transparent;color:#edf6ff;padding:14px;font:inherit;font-size:15px;line-height:1.7;min-height:145px;outline:none}.prompt-form textarea::placeholder{color:#8ea4bd}.context-row{border-top:1px solid #314359;padding:14px 12px 10px}.context-row label{display:block;color:#cde0eb;font-size:13px;font-weight:700;margin-bottom:8px}.context-row input{background:#0e192b;color:#f4f8ff;border:1px solid #426176;border-radius:9px;padding:11px 12px;width:100%;box-sizing:border-box;font:inherit;font-size:14px}.help{display:block;color:#90a9c2;font-size:12px;margin-top:7px}.prompt-footer{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:13px 10px 3px;color:#9db4c8;font-size:12px}.prompt-footer button{background:#73e2c9;border:0;border-radius:10px;color:#092a31;font:inherit;font-weight:750;font-size:14px;padding:13px 22px;cursor:pointer}.prompt-footer button:disabled{opacity:.5;cursor:not-allowed}
    .examples{margin-top:42px}.examples h2{font-size:15px;color:#aabdd0;font-weight:500}.example-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.example-grid button{cursor:pointer;color:#dbe9f6;text-align:left;background:#14243b;border:1px solid #354b65;border-radius:13px;padding:17px;font:inherit;font-size:13px;line-height:1.55}.example-grid button span{color:#7de4d0;margin-left:8px}.example-grid button:hover{border-color:#67c8b8}
    .message{margin-top:25px;padding:17px;border-radius:12px;border:1px solid #3d6572;color:#cfe6ed;background:#183643}.message.error{border-color:#975c58;background:#3a2226}.message p{margin-bottom:0}.report{margin-top:50px}.report-head{display:flex;justify-content:space-between;align-items:center;gap:18px}.report-head h2{font-size:29px;margin:8px 0}.report-intro{color:#b1c1d3;line-height:1.7;margin:18px 0}.status-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:23px 0}.status-item,.report-card{border:1px solid #33485f;background:#132137;border-radius:13px;padding:19px}.status-item span{display:block;font-size:12px;color:#9eb4c9;margin-bottom:9px}.status-item strong{font-size:15px}.finding-alert{border:1px solid #b58e44;background:#342c1b;color:#f3deaf;border-radius:13px;padding:19px 21px;margin:22px 0}.finding-alert h3{margin:0 0 10px;font-size:17px}.finding-alert p{font-size:14px;line-height:1.6}.finding-alert p:last-child{margin-bottom:0}.finding-alert code{overflow-wrap:anywhere;font-size:12px}
    .report-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.report-card{min-width:0;padding:22px}.report-card h3{font-size:18px;margin:0 0 15px;color:#e9f6f8}.report-card p,.report-card li{font-size:14px;line-height:1.7;color:#bfd1e4;overflow-wrap:anywhere}.report-card strong{color:#edf7ff}.records,.notes{padding-left:20px;margin:0}.records li,.notes li{margin-bottom:11px}.footnote{color:#91aabc!important;font-size:12px!important}.technical{margin-top:22px;border:1px solid #31495c;border-radius:12px;padding:15px;color:#a7bdd1}.technical summary{cursor:pointer}.technical p{font-size:12px}.technical pre{font-size:11px;max-height:340px;white-space:pre-wrap;overflow-wrap:anywhere;overflow:auto;background:#081221;padding:14px;border-radius:8px}footer{border-top:1px solid #304354;color:#839ab1;font-size:12px;margin-top:55px;padding-top:23px}.sr-only{position:absolute;width:1px;height:1px;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap}
    @media(max-width:800px){.shell{padding:23px 16px 50px}.scope-pill{display:none}.hero{margin:50px auto 25px}.example-grid,.report-grid,.status-grid{grid-template-columns:1fr}.report-head{flex-direction:column;align-items:flex-start}.prompt-footer{flex-direction:column;align-items:stretch}.prompt-footer button{width:100%}}
.workflow-form{margin-top:14px;padding:15px;border:1px solid #314b61;border-radius:12px;display:grid;gap:12px;background:#111e30}.workflow-form h3{margin:0;font-size:15px}.workflow-form label{display:grid;gap:6px;font-size:13px;color:#d2e6ef}.workflow-form input:not([type="checkbox"]),.workflow-form textarea,.workflow-form select{min-width:0;width:100%;box-sizing:border-box;padding:10px;background:#0e192b;color:#eef6ff;border:1px solid #46637a;border-radius:8px;font:inherit}.workflow-form button{justify-self:start;border:0;border-radius:9px;padding:11px 16px;font:inherit;font-weight:700;background:#73e2c9;color:#082630;cursor:pointer}.workflow-form button:disabled{opacity:.45;cursor:not-allowed}.workflow-form .confirmation{display:flex;align-items:center;gap:9px}.framework-coverage .confirmation{display:flex;align-items:center;gap:10px;padding:16px 0;font-size:13px}.framework-coverage button{border:0;border-radius:9px;background:#73e2c9;color:#082630;padding:12px 16px;font:inherit;font-weight:700;cursor:pointer;margin-top:10px}.framework-coverage button:disabled{opacity:.45;cursor:not-allowed}.framework-coverage textarea{width:100%;background:#0e192b;color:#eef6ff;border:1px solid #46637a;border-radius:8px;padding:11px;box-sizing:border-box;font:inherit}
    .framework-actions { display:flex; flex-wrap:wrap; gap:10px; align-items:center; margin:12px 0; }
    .framework-actions button { flex:0 1 auto; }
    .framework-coverage { margin:20px 0 16px; padding:16px; border:1px solid rgba(134,185,174,.25); border-radius:12px; }
    .framework-coverage-title { display:flex; justify-content:space-between; align-items:center; gap:12px; flex-wrap:wrap; margin-bottom:12px; }
    .framework-meter { height:12px; border-radius:99px; background:rgba(150,170,185,.23); overflow:hidden; }
    .framework-meter-fill { height:100%; background:#61d8bc; border-radius:99px; transition:width .25s ease; }
    .review-more{margin-top:14px;border:1px solid #46637a;background:#172d42;color:#e6f3fd;padding:12px 16px;border-radius:9px;cursor:pointer}
    .checkpoint-label{display:grid;gap:10px;font-size:13px;margin-top:14px}
    .checkpoint-label input{color:#d0e7ed}
    #start-grc-case{margin-top:55px}
    .sico-case-draft{padding:15px;margin:12px 0;background:#0d1c30;border:1px solid #35566c;border-radius:9px}
    .sico-case-draft h4{margin:0 0 10px;color:#9ef0dd}
    .sico-case-draft p{line-height:1.65;color:#c4d8e6}
    .sico-case-draft dl{display:grid;gap:8px;margin:12px 0}
    .sico-case-draft dl div{display:grid;grid-template-columns:minmax(120px,32%) 1fr;gap:10px;border-bottom:1px solid #254052;padding-bottom:7px}
    .sico-case-draft dt{color:#93bece;font-weight:700}
    .sico-case-draft dd{margin:0;color:#e5f0f4;overflow-wrap:anywhere}
    /* SICO AI Next: display-only refinement. No generation, storage or API changes. */
    .report-intro{max-width:82ch;font-size:15px;line-height:1.8;color:#c1d4e0}
    .report-head h2{font-size:clamp(25px,3vw,32px);letter-spacing:-.025em}
    .workflow-form{padding:20px;gap:15px}
    .workflow-form label{font-weight:650;line-height:1.45}
    .workflow-form input:focus-visible,.workflow-form textarea:focus-visible{outline:2px solid #78dfcc;outline-offset:2px}
    .sico-case-draft{padding:20px 22px;margin:14px 0;background:#102139;border-color:#36536b;border-radius:12px;box-shadow:0 3px 10px #0002}
    .sico-case-draft h4{font-size:16px;line-height:1.5;letter-spacing:-.01em;color:#80e6d2}
    .sico-case-draft p{font-size:14px;line-height:1.7;margin:10px 0;color:#d0dfea;overflow-wrap:anywhere}
    .sico-case-draft p strong{color:#e7f3f9}
    .sico-case-draft dl{gap:0;margin:16px 0}
    .sico-case-draft dl div{grid-template-columns:minmax(145px,32%) minmax(0,1fr);align-items:start;gap:14px;padding:9px 0;border-bottom:1px solid #29445a}
    .sico-case-draft dt{color:#aecbdb;font-weight:700;font-size:13px;line-height:1.5}
    .sico-case-draft dd{font-size:14px;line-height:1.55}
    .sico-case-draft .footnote{line-height:1.6}
    @media(max-width:600px){.workflow-form{padding:14px}.sico-case-draft{padding:15px}.sico-case-draft dl div{grid-template-columns:1fr;gap:3px;padding:10px 0}}
</style>
