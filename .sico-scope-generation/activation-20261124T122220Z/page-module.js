import { createHotContext as __vite__createHotContext } from "/@vite/client";import.meta.hot = __vite__createHotContext("/src/routes/(app)/(internal)/sico-ai-next/+page.svelte");import "/node_modules/.vite/deps/svelte_internal_disclose-version.js?v=aff06c8b";

_page[$.FILENAME] = 'src/routes/(app)/(internal)/sico-ai-next/+page.svelte';

import * as $ from "/node_modules/.vite/deps/svelte_internal_client.js?v=aff06c8b";
import { enhance, deserialize, applyAction } from "/node_modules/.pnpm/@sveltejs+kit@2.52.2_@sveltejs+vite-plugin-svelte@4.0.4_svelte@5.53.5_vite@5.4.21_@type_1cad34e88a2286f38bbea3c42f1e9233/node_modules/@sveltejs/kit/src/runtime/app/forms.js?v=aff06c8b";
import { onMount } from "/node_modules/.vite/deps/svelte.js?v=aff06c8b";
import SicoGeneratedCase from "/src/lib/components/AiOnboarding/SicoGeneratedCase.svelte";

import {
	validateGenerationQueue,
	nextGenerationSlot,
	plannedDraftContext
} from "/src/lib/utils/sicoGenerationPlan.ts?t=1795523043911";

import { applyFrameworkBatch, validateCheckpoint, scopeKey } from "/src/lib/utils/sicoFrameworkReviewV3.ts";

var root_1 = $.add_locations($.from_html(`<meta name="description" content="Generate structured, reviewable GRC case drafts using the existing SICO workspace." class="s-OYdrvhQpzABG"/>`), _page[$.FILENAME], [[1042, 4]]);
var root_3 = $.add_locations($.from_html(`<button type="button" class="s-OYdrvhQpzABG">Resume failed draft with a different focus</button>`), _page[$.FILENAME], [[1071, 24]]);
var root_4 = $.add_locations($.from_html(`<button type="submit" class="s-OYdrvhQpzABG"> </button>`), _page[$.FILENAME], [[1073, 24]]);
var root_5 = $.add_locations($.from_html(`<p class="message error s-OYdrvhQpzABG" role="alert"> </p>`), _page[$.FILENAME], [[1082, 34]]);
var root_6 = $.add_locations($.from_html(`<p class="message s-OYdrvhQpzABG" role="status"> </p>`), _page[$.FILENAME], [[1083, 35]]);
var root_9 = $.add_locations($.from_html(`<li class="s-OYdrvhQpzABG"><strong class="s-OYdrvhQpzABG"> </strong> <span class="footnote s-OYdrvhQpzABG">· Not assessed · Evidence needed · Human review required</span></li>`), _page[$.FILENAME], [[1109, 40, [[1110, 44], [1111, 44]]]]);
var root_10 = $.add_locations($.from_html(`<button type="button" class="s-OYdrvhQpzABG">Show remaining requirements</button>`), _page[$.FILENAME], [[1116, 36]]);
var root_11 = $.add_locations($.from_html(`<button type="button" class="s-OYdrvhQpzABG">Show first 12 only</button>`), _page[$.FILENAME], [[1118, 36]]);

var root_8 = $.add_locations($.from_html(`<section class="requirement-coverage-plan s-OYdrvhQpzABG" aria-label="Framework requirement review coverage"><h4 class="s-OYdrvhQpzABG">Requirement-by-requirement review plan</h4> <p class="s-OYdrvhQpzABG"><strong class="s-OYdrvhQpzABG"> </strong> requirements prepared for review · <strong class="s-OYdrvhQpzABG"> </strong> source-linked Qwen review drafts · <strong class="s-OYdrvhQpzABG">0</strong> evidence-verified compliance decisions</p> <p class="footnote s-OYdrvhQpzABG">All requirement work items start as Not assessed. Applicability and organization evidence are awaiting review. A work item is not an AI-generated compliance conclusion.</p> <p class="footnote s-OYdrvhQpzABG">Risk ratings: pending tenant-authorized risk assessment and configured SICO risk matrix. The AI cannot calculate current or residual risk from a framework name alone.</p> <p class="footnote s-OYdrvhQpzABG">The case board displays accepted Qwen content only. Planned records and an unapproved matrix do not establish implementation or compliance.</p> <button type="button" class="s-OYdrvhQpzABG">Download full requirement work plan</button> <details class="s-OYdrvhQpzABG"><summary class="s-OYdrvhQpzABG"> </summary> <ol class="requirement-work-items s-OYdrvhQpzABG"></ol> <!></details></section>`), _page[$.FILENAME], [
	[
		1093,
		24,
		[
			[1094, 28],
			[1095, 28, [[1096, 32], [1098, 32], [1099, 32]]],
			[1101, 28],
			[1102, 28],
			[1103, 28],
			[1104, 28],
			[1105, 28, [[1106, 32], [1107, 32]]]
		]
	]
]);

var root_12 = $.add_locations($.from_html(`<p class="footnote s-OYdrvhQpzABG">Preparing authorized framework coverage before model drafting.</p>`), _page[$.FILENAME], [[1123, 24]]);
var root_13 = $.add_locations($.from_html(`<p class="message error s-OYdrvhQpzABG" role="alert"> </p>`), _page[$.FILENAME], [[1125, 43]]);
var root_14 = $.add_locations($.from_html(`<span class="footnote s-OYdrvhQpzABG"> </span> <button type="button" class="s-OYdrvhQpzABG">Pause after current request</button>`, 1), _page[$.FILENAME], [[1132, 28], [1133, 28]]);
var root_16 = $.add_locations($.from_html(`<button type="button" class="s-OYdrvhQpzABG">Resume automatic generation</button>`), _page[$.FILENAME], [[1136, 32]]);
var root_15 = $.add_locations($.from_html(`<!> <button type="button" class="s-OYdrvhQpzABG">Start a new case</button>`, 1), _page[$.FILENAME], [[1138, 28]]);
var root_17 = $.add_locations($.from_html(`<button type="button" class="s-OYdrvhQpzABG">Download checkpoint</button>`), _page[$.FILENAME], [[1141, 28]]);
var root_18 = $.add_locations($.from_html(`<button type="button" class="s-OYdrvhQpzABG">Download framework requirements</button>`), _page[$.FILENAME], [[1144, 28]]);
var root_19 = $.add_locations($.from_html(`<p class="footnote s-OYdrvhQpzABG" role="status"> </p>`), _page[$.FILENAME], [[1147, 41]]);
var root_21 = $.add_locations($.from_html(`<li class="s-OYdrvhQpzABG"> </li>`), _page[$.FILENAME], [[1153, 36]]);
var root_20 = $.add_locations($.from_html(`<details class="generation-timing s-OYdrvhQpzABG"><summary class="s-OYdrvhQpzABG"> </summary> <ul class="s-OYdrvhQpzABG"></ul></details>`), _page[$.FILENAME], [[1149, 24, [[1150, 28], [1151, 28]]]]);
var root_22 = $.add_locations($.from_html(`<p class="footnote s-OYdrvhQpzABG"> </p>`), _page[$.FILENAME], [[1158, 45]]);
var root_23 = $.add_locations($.from_html(`<p class="footnote s-OYdrvhQpzABG"> </p>`), _page[$.FILENAME], [[1159, 46]]);
var root_25 = $.add_locations($.from_html(`<div class="s-OYdrvhQpzABG"><dt class="s-OYdrvhQpzABG"> </dt><dd class="s-OYdrvhQpzABG"> </dd></div>`), _page[$.FILENAME], [[1167, 36, [[1167, 41], [1167, 81]]]]);
var root_26 = $.add_locations($.from_html(`<p class="s-OYdrvhQpzABG"><strong class="s-OYdrvhQpzABG">Related Drafts:</strong> </p>`), _page[$.FILENAME], [[1173, 32, [[1173, 35]]]]);

var root_24 = $.add_locations($.from_html(`<article class="sico-case-draft s-OYdrvhQpzABG"><h4 class="s-OYdrvhQpzABG"> <span class="footnote s-OYdrvhQpzABG"> </span></h4> <p class="footnote s-OYdrvhQpzABG"> </p> <p class="s-OYdrvhQpzABG"> </p> <dl class="s-OYdrvhQpzABG"></dl> <p class="s-OYdrvhQpzABG"><strong class="s-OYdrvhQpzABG">Evidence to Request:</strong> </p> <p class="s-OYdrvhQpzABG"><strong class="s-OYdrvhQpzABG">Verification Question:</strong> </p> <!> <p class="footnote s-OYdrvhQpzABG">Hypothetical, unsaved. Not verified organization data or proof of compliance.</p></article>`), _page[$.FILENAME], [
	[
		1161,
		24,
		[
			[1162, 28, [[1162, 51]]],
			[1163, 28],
			[1164, 28],
			[1165, 28],
			[1170, 28, [[1170, 31]]],
			[1171, 28, [[1171, 31]]],
			[1175, 28]
		]
	]
]);

var root_7 = $.add_locations($.from_html(`<div class="framework-coverage s-OYdrvhQpzABG" aria-label="New SICO GRC case draft results"><div class="framework-coverage-title s-OYdrvhQpzABG"><h3 class="s-OYdrvhQpzABG"> </h3> <span class="footnote s-OYdrvhQpzABG">No records saved · No compliance verdict</span></div> <p class="source-note s-OYdrvhQpzABG"> </p> <!> <!> <!> <p class="footnote s-OYdrvhQpzABG">Framework, assessment charter and business scope are inputs to confirm, not model-generated assessment results.</p> <div class="framework-meter s-OYdrvhQpzABG"><div class="framework-meter-fill s-OYdrvhQpzABG"></div></div> <p class="footnote s-OYdrvhQpzABG"> </p> <div class="framework-actions s-OYdrvhQpzABG"><!> <!> <!></div> <!> <!> <!> <!> <!></div>`), _page[$.FILENAME], [
	[
		1085,
		16,
		[
			[1086, 20, [[1087, 24], [1088, 24]]],
			[1090, 20],
			[1127, 20],
			[1128, 20, [[1128, 49]]],
			[1129, 20],
			[1130, 20]
		]
	]
]);

var root = $.add_locations($.from_html(`<div class="workspace s-OYdrvhQpzABG"><div class="shell s-OYdrvhQpzABG"><header class="topbar s-OYdrvhQpzABG"><div class="logo s-OYdrvhQpzABG">✦</div> <div class="s-OYdrvhQpzABG"><strong class="s-OYdrvhQpzABG">SICO AI</strong><small class="s-OYdrvhQpzABG">ASSESSMENT WORKSPACE</small></div> <span class="scope-pill s-OYdrvhQpzABG">Uses your GRC permissions</span></header> <section class="report s-OYdrvhQpzABG" aria-label="Build a GRC case" id="start-grc-case"><div class="report-head s-OYdrvhQpzABG"><h2 class="s-OYdrvhQpzABG">Build a GRC case</h2> <span class="status-pill s-OYdrvhQpzABG">One workflow · Your existing SICO GRC library</span></div> <p class="report-intro s-OYdrvhQpzABG">Enter three details to generate structured GRC case drafts across SICO’s 16 activities, including proposed assets, risks, controls, policies, evidence requests, tasks and reports. Drafts remain unsaved and do not establish compliance.</p> <form class="workflow-form s-OYdrvhQpzABG"><label class="s-OYdrvhQpzABG">1. Organization <input name="organization_name" required="" minlength="2" maxlength="150" placeholder="Organization name (new or existing)" class="s-OYdrvhQpzABG"/></label> <label class="s-OYdrvhQpzABG">2. Framework <input name="framework_name" required="" minlength="2" maxlength="150" placeholder="Enter the exact framework name from SICO’s library" class="s-OYdrvhQpzABG"/></label> <label class="s-OYdrvhQpzABG">3. GRC case objective <textarea name="problem" required="" minlength="20" maxlength="4000" rows="4" placeholder="Create a complete new GRC case with proposed assets, controls, risks, policy drafts, evidence requests, remediation and reports." class="s-OYdrvhQpzABG"></textarea></label> <!> <label class="checkpoint-upload s-OYdrvhQpzABG">Restore an earlier draft session from a JSON checkpoint <input type="file" accept=".json,application/json" class="s-OYdrvhQpzABG"/></label></form> <!> <!> <!> <p class="footnote s-OYdrvhQpzABG">These are proposed drafts structured around existing SICO GRC models. They have not been verified against the organization or saved as business records.</p></section> <footer class="s-OYdrvhQpzABG">SICO AI · One case-building workflow · AI-generated GRC drafts across 16 activities · No database writes.</footer></div></div>`), _page[$.FILENAME], [
	[
		1045,
		0,
		[
			[
				1046,
				4,
				[
					[
						1047,
						8,
						[[1048, 12], [1049, 12, [[1049, 17], [1049, 41]]], [1050, 12]]
					],

					[
						1053,
						8,
						[
							[1054, 12, [[1055, 16], [1056, 16]]],
							[1058, 12],
							[
								1059,
								12,
								[
									[1060, 16, [[1061, 20]]],
									[1063, 16, [[1064, 20]]],
									[1066, 16, [[1067, 20]]],
									[1078, 16, [[1079, 20]]]
								]
							],
							[1180, 12]
						]
					],
					[1182, 8]
				]
			]
		]
	]
]);

function _page($$anchor, $$props) {
	$.check_target(new.target);
	$.push($$props, true, _page);

	let instruction = $.tag($.state(''), 'instruction');
	let organization = $.tag($.state(''), 'organization');
	let busy = false;
	let lastAgentRun = $.tag($.state(null), 'lastAgentRun');
	let eligibleOptions = $.tag($.state(null), 'eligibleOptions');
	let preparedWorkflow = $.tag($.state(null), 'preparedWorkflow');
	let recordedApproval = $.tag($.state(null), 'recordedApproval');
	let activeEngagement = $.tag($.state(''), 'activeEngagement');
	let generatedAssessment = $.tag($.state(null), 'generatedAssessment');
	let generationError = $.tag($.state(''), 'generationError');
	let generatedSixteen = $.tag($.state($.proxy([])), 'generatedSixteen');
	let generatedFor = $.tag($.state(''), 'generatedFor');
	let sixteenBusy = $.tag($.state(false), 'sixteenBusy');
	let sixteenError = $.tag($.state(''), 'sixteenError');
	let caseSaveNotice = $.tag($.state(''), 'caseSaveNotice');
	let controlProgress = $.tag($.state(null), 'controlProgress');
	let controlBusy = $.tag($.state(false), 'controlBusy');
	let controlError = $.tag($.state(''), 'controlError');
	let controlNotice = $.tag($.state(''), 'controlNotice');
	let lastControlCaseLoaded = '';
	let lifecycleProgress = $.tag($.state(null), 'lifecycleProgress');
	let lifecycleProposal = $.tag($.state(null), 'lifecycleProposal');
	let lifecycleApproval = $.tag($.state(null), 'lifecycleApproval');
	let evidenceContext = '';
	let selectedFolder = '';
	let selectedPerimeter = '__new__';
	let frameworkSearch = $.tag($.state(''), 'frameworkSearch');
	let frameworkConfirmation = '';
	let organizationConfirmation = '';
	let proposedAssessment = 'Cybersecurity compliance assessment';
	let proposedPerimeter = 'SICO cybersecurity assessment perimeter';
	let selectedFramework = '';
	let selectedRiskMatrix = '';

	// Build a GRC case follows the authorized framework plan, generating one
	// Qwen record per dependency-ready task. Approval and writers stay separate.
	let draftedCaseStages = $.tag($.state($.proxy([])), 'draftedCaseStages');

	let draftedCaseScope = $.tag($.state(''), 'draftedCaseScope');
	let draftedCaseBusy = $.tag($.state(false), 'draftedCaseBusy');
	let draftedCaseError = $.tag($.state(''), 'draftedCaseError');
	let draftedCaseNotice = $.tag($.state(''), 'draftedCaseNotice');
	let stopAfterPhase = $.tag($.state(false), 'stopAfterPhase');
	let authorizedFrameworkSource = $.tag($.state(null), 'authorizedFrameworkSource');
	let authorizedSourceRows = $.tag($.state($.proxy([])), 'authorizedSourceRows');
	let frameworkSourceSummary = $.tag($.state(''), 'frameworkSourceSummary');

	// Source-grounded requirement-review queue. A prepared work item is NOT a
	// completed assessment, and this state is never used to authorize access.
	let coveragePlan = $.tag($.state(null), 'coveragePlan');

	let coveragePlanScope = $.tag($.state(''), 'coveragePlanScope');
	let coveragePlanError = $.tag($.state(''), 'coveragePlanError');
	let showAllCoverageItems = $.tag($.state(false), 'showAllCoverageItems');

	function validCoveragePlanForScope() {
		return $.strict_equals($.get(coveragePlanScope), qualityScopeKey()) ? $.get(coveragePlan) : null;
	}

	// Only Qwen records that cite a real authorized requirement count as
	// provisional review drafts. Never count them as verified compliance.
	function sourceLinkedReviewCount() {
		const plan = validCoveragePlanForScope();

		if (!plan) return 0;

		const allowed = new Set((plan.requirement_work_items ?? []).map((row) => row.requirement_id));
		const referenced = new Set();

		for (const row of $.get(qualityDrafts)) {
			const id = String(row?.draft?.authorized_requirement_id ?? '');

			if ($.strict_equals(row?.activity_number, 10) && $.strict_equals(row?.activity_code, 'requirement_reviews') && $.strict_equals(row?.business_records_written, false) && $.strict_equals(row?.draft?.status, 'new_unsaved_ai_draft_pending_verification') && allowed.has(id)) referenced.add(id);
		}

		return referenced.size;
	}

	async function loadSicoCoveragePlan() {
		if (!$.get(authorizedFrameworkSource)?.complete_source_snapshot || !$.get(authorizedFrameworkSource).source_digest || !$.get(authorizedFrameworkSource).framework_id || !$.get(authorizedSourceRows).length) {
			throw new Error('An authorized complete framework source is required before planning coverage.');
		}

		const response = (await $.track_reactivity_loss(sicoPostAction('case_coverage_plan', {
			organization_name: $.get(organization).trim(),
			framework_name: $.get(frameworkSearch).trim(),
			problem: $.get(instruction).trim(),
			source_digest: String($.get(authorizedFrameworkSource).source_digest)
		})))();

		const plan = response.data?.case_coverage_plan;
		const rows = Array.isArray(plan?.requirement_work_items) ? plan.requirement_work_items : [];
		const sourceIds = new Set($.get(authorizedSourceRows).map((r) => String(r.requirement_id)));

		if ($.strict_equals(plan?.schema, 'sico-ai-coverage-plan-v1', false) || $.strict_equals(plan?.business_records_written, false, false) || $.strict_equals(plan?.full_framework_assessed, false, false) || $.strict_equals(plan.source_digest, $.get(authorizedFrameworkSource).source_digest, false) || $.strict_equals(plan.framework_id, $.get(authorizedFrameworkSource).framework_id, false) || $.strict_equals(rows.length, $.get(authorizedSourceRows).length, false) || $.strict_equals(new Set(rows.map((r) => String(r.requirement_id))).size, rows.length, false) || rows.some((r) => !sourceIds.has(String(r.requirement_id)) || $.strict_equals(r.proposed_result, 'not_assessed', false) || $.strict_equals(r.evidence_verified, false, false))) {
			throw new Error('Coverage plan does not match the authorized SICO framework source.');
		}

		validateGenerationQueue(plan, $.get(authorizedSourceRows));
		$.set(coveragePlan, plan, true);
		$.set(coveragePlanScope, qualityScopeKey(), true);
		$.set(coveragePlanError, '');
	}

	function downloadCoveragePlan() {
		const plan = validCoveragePlanForScope();

		if (!plan) return;

		const file = new Blob([JSON.stringify(plan, null, 2)], { type: 'application/json' });
		const url = URL.createObjectURL(file);

		try {
			const link = document.createElement('a');

			link.href = url;
			link.download = 'SICO-AI-REQUIREMENT-REVIEW-PLAN.json';
			link.click();
		} finally {
			URL.revokeObjectURL(url);
		}
	}

	async function loadSicoAuthorizedFrameworkSource() {
		let cursor = '';
		let sourceDigest = '';
		let selectedFrameworkId = '';
		const rows = [];

		for (let page = 0; page < 200; page++) {
			const response = (await $.track_reactivity_loss(sicoPostAction('framework_source_page', { framework_name: $.get(frameworkSearch).trim(), cursor })))();
			const part = response.data?.framework_source_page;

			if (!part) throw new Error('No authorized framework source was returned.');

			if ($.strict_equals(part.status, 'partial', false) && $.strict_equals(part.status, 'complete', false)) {
				const candidates = Array.isArray(part.candidates) ? part.candidates.join(', ') : '';

				throw new Error('The exact selected framework could not be resolved using your SICO permissions.' + (candidates ? ` Authorized matches: ${candidates}` : ''));
			}

			if (!part.framework_id || !part.source_digest || !Array.isArray(part.requirements)) {
				throw new Error('Framework catalog did not include verified SICO source identifiers.');
			}

			if (sourceDigest && $.strict_equals(sourceDigest, part.source_digest, false)) {
				throw new Error('Framework library changed during retrieval; restart the draft.');
			}

			if (selectedFrameworkId && $.strict_equals(selectedFrameworkId, part.framework_id, false)) {
				throw new Error('The resolved framework changed during retrieval.');
			}

			sourceDigest = part.source_digest;
			selectedFrameworkId = part.framework_id;
			rows.push(...part.requirements);
			$.set(frameworkSourceSummary, `SICO authorized framework: ${rows.length}/${part.coverage.accessible_total} requirements loaded`);

			if ($.strict_equals(part.status, 'complete')) {
				if ($.strict_equals(part.coverage.accessible_total, 0)) {
					throw new Error('The selected SICO framework has no requirements readable to this user.');
				}

				if (!part.coverage.complete || $.strict_equals(rows.length, part.coverage.accessible_total, false)) {
					throw new Error('Framework source count mismatch. No coverage can be claimed.');
				}

				$.set(authorizedSourceRows, rows, true);

				$.set(
					authorizedFrameworkSource,
					{
						framework_id: selectedFrameworkId,
						matched_framework: part.matched_framework,
						source_digest: sourceDigest,
						accessible_total: rows.length,
						complete_source_snapshot: true,
						edition_independently_verified: false
					},
					true
				);

				return;
			}

			if (!part.next_cursor || $.strict_equals(part.next_cursor, cursor)) {
				throw new Error('Framework source pagination did not advance.');
			}

			cursor = part.next_cursor;
		}

		throw new Error('Framework source is too large to load safely in one run.');
	}

	function draftScopeKey() {
		return JSON.stringify([
			$.get(organization).trim(),
			$.get(frameworkSearch).trim(),
			$.get(instruction).trim()
		]);
	}

	// One Qwen record per request: the same proven approach as the HTML runner.
	// No server-side GRC case/asset/risk writers are ever called by this path.
	const generationOrder = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16];

	let qualityDrafts = $.tag($.state($.proxy([])), 'qualityDrafts');
	let qualityIssues = $.tag($.state($.proxy([])), 'qualityIssues');
	let loadedOlderCheckpoint = $.tag($.state(false), 'loadedOlderCheckpoint');
	let checkpointSource = $.tag($.state(null), 'checkpointSource');
	let currentGeneratingActivity = $.tag($.state(0), 'currentGeneratingActivity');
	let localCheckpointInfo = $.tag($.state(''), 'localCheckpointInfo');

	// UX-only generation diagnostics: the API and stored draft schema remain unchanged.
	let attemptHistory = $.tag($.state($.proxy([])), 'attemptHistory');

	let nextAttemptBySlot = $.tag($.state($.proxy({})), 'nextAttemptBySlot');
	let lastAttemptInfo = $.tag($.state(''), 'lastAttemptInfo');

	function slotAttemptKey(step, index) {
		return `draft-${String(step).padStart(2, '0')}-${String(index).padStart(2, '0')}`;
	}

	function safeAttemptCounters(source) {
		const result = {};

		if (!source || $.strict_equals(typeof source, 'object', false) || Array.isArray(source)) return result;

		for (const [key, value] of Object.entries(source)) {
			if ((/^draft-(?:0[1-9]|1[0-6])-(?:0[1-9]|[1-9][0-9]{1,3}|10000)$/).test(key) && Number.isInteger(value) && Number(value) >= 0 && Number(value) <= 30) result[key] = Number(value);
		}

		return result;
	}

	function safeAttemptHistory(source) {
		if (!Array.isArray(source)) return [];

		return source.slice(-20).filter((entry) => Number.isInteger(entry?.activity) && entry.activity >= 1 && entry.activity <= 16 && Number.isInteger(entry?.index) && entry.index >= 1 && entry.index <= 10000 && $.strict_equals(typeof entry?.elapsed_seconds, 'number') && entry.elapsed_seconds >= 0 && entry.elapsed_seconds < 3600 && ($.strict_equals(entry?.outcome, 'accepted') || $.strict_equals(entry?.outcome, 'rejected')) && $.strict_equals(typeof entry?.detail, 'string')).map((entry) => ({ ...entry, detail: entry.detail.slice(0, 180) }));
	}

	function recordDraftAttempt(activity, index, elapsed_seconds, outcome, detail) {
		const event = {
			activity,
			index,
			elapsed_seconds,
			outcome,
			detail: detail.slice(0, 180)
		};

		$.set(attemptHistory, [...$.get(attemptHistory).slice(-19), event], true);
		$.set(lastAttemptInfo, `Activity ${activity}, draft ${index}: ${outcome} after ${elapsed_seconds}s${$.strict_equals(outcome, 'rejected') ? ` · ${event.detail}` : ''}.`);
	}

	// All 16 existing activities use source-driven task counts. Planning and
	// unsaved Qwen work never count as evidence-verified assessment results.
	const firstPassTarget = generationOrder.length;

	onMount(() => {
		// Same-tab recovery only. Nothing is stored in SICO business tables.
		try {
			const raw = sessionStorage.getItem('sico-ai-quality-draft-v7');

			if (!raw) return;

			const cp = JSON.parse(raw);

			if ($.strict_equals(cp?.schema, 'sico-authenticated-quality-drafts-v7', false) || !Array.isArray(cp.items)) return;
			if (cp.items.length > 160000 || cp.items.some((r) => !r?.draft?.draft_reference)) return;

			$.set(organization, String(cp.scope?.organization ?? '').slice(0, 150), true);
			$.set(frameworkSearch, String(cp.scope?.framework ?? '').slice(0, 150), true);
			$.set(instruction, String(cp.scope?.objective ?? '').slice(0, 4000), true);

			if ($.get(organization).length < 2 || $.get(frameworkSearch).length < 2 || $.get(instruction).length < 20) return;

			$.set(qualityDrafts, cp.items, true);
			$.set(qualityIssues, Array.isArray(cp.issues) ? cp.issues.slice(-30) : [], true);
			$.set(nextAttemptBySlot, safeAttemptCounters(cp.attempt_counters), true);
			$.set(attemptHistory, safeAttemptHistory(cp.attempt_history), true);

			if ($.get(attemptHistory).length) {
				const last = $.get(attemptHistory)[$.get(attemptHistory).length - 1];

				$.set(lastAttemptInfo, `Last request: activity ${last.activity}, ${last.outcome} after ${last.elapsed_seconds}s.`);
			}

			$.set(checkpointSource, cp.source ?? null, true);
			$.set(draftedCaseScope, qualityScopeKey(), true);
			$.set(localCheckpointInfo, 'Recovered drafts from this browser tab. Load framework access again before resuming.');
		} catch {
			/* A corrupt or unavailable tab checkpoint is ignored. */
		}
	});

	function qualityScopeKey() {
		return JSON.stringify([
			$.get(organization).trim(),
			$.get(frameworkSearch).trim(),
			$.get(instruction).trim()
		]);
	}

	function checkpointPayload() {
		return {
			schema: 'sico-authenticated-quality-drafts-v7',
			scope: {
				organization: $.get(organization).trim(),
				framework: $.get(frameworkSearch).trim(),
				objective: $.get(instruction).trim()
			},
			source: $.get(authorizedFrameworkSource) ?? $.get(checkpointSource),
			items: $.get(qualityDrafts),
			generation_queue: validCoveragePlanForScope()?.generation_queue ?? [],
			issues: $.get(qualityIssues),
			attempt_counters: $.get(nextAttemptBySlot),
			attempt_history: $.get(attemptHistory).slice(-20),
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

			$.set(localCheckpointInfo, 'Progress saved in this browser session. Download a checkpoint to resume another day.');
		} catch {
			$.set(localCheckpointInfo, 'Browser storage is unavailable; download a checkpoint before leaving.');
		}
	}

	function downloadQualityCheckpoint() {
		const url = URL.createObjectURL(new Blob([JSON.stringify(checkpointPayload(), null, 2)], { type: 'application/json' }));

		try {
			const link = document.createElement('a');

			link.href = url;
			link.download = 'SICO-AI-quality-case-checkpoint.json';
			link.click();
		} finally {
			URL.revokeObjectURL(url);
		}
	}

	async function importQualityCheckpoint(event) {
		const input = event.currentTarget;
		const file = input.files?.[0];

		if (!file || $.get(draftedCaseBusy)) return;

		try {
			if (file.size > 50000000) throw new Error('Checkpoint file is too large.');

			const parsed = JSON.parse((await $.track_reactivity_loss(file.text()))());
			let items;

			if ($.strict_equals(parsed?.schema, 'sico-authenticated-quality-drafts-v7') && Array.isArray(parsed?.items)) {
				if ($.strict_equals(parsed?.scope?.organization, $.get(organization).trim(), false) || $.strict_equals(parsed?.scope?.framework, $.get(frameworkSearch).trim(), false) || $.strict_equals(parsed?.scope?.objective, $.get(instruction).trim(), false)) {
					throw new Error('The checkpoint belongs to different case inputs. Use those original inputs first.');
				}

				items = parsed.items;
			} else if (String(parsed?.schema ?? '').startsWith('sico-quality') && Array.isArray(parsed?.generated_items)) {
				// Existing HTML-runner v5 checkpoint: show it here without
				// claiming imported draft content passed this v7 generation.
				if ($.strict_equals(parsed.organization, $.get(organization).trim(), false) || $.strict_equals(parsed.framework, $.get(frameworkSearch).trim(), false)) throw new Error('HTML checkpoint organization/framework do not match the form.');

				items = parsed.generated_items.map((item) => ({ ...item, provenance: 'imported_html_review_required' }));
				$.set(loadedOlderCheckpoint, true);
			} else {
				throw new Error('Unsupported checkpoint. Select a SICO quality generator JSON checkpoint.');
			}

			if (items.length > 160000 || items.some((r) => !(/^draft-(?:0[1-9]|1[0-6])-(?:0[1-9]|[1-9][0-9]{1,3}|10000)$/).test(r?.draft?.draft_reference ?? '') || !r?.draft?.title || !r?.draft?.record_type || !r?.activity_number)) {
				throw new Error('Checkpoint contains invalid draft references or content.');
			}

			if ($.strict_equals(new Set(items.map((r) => r.draft.draft_reference)).size, items.length, false)) throw new Error('Checkpoint contains duplicate draft references.');

			$.set(qualityDrafts, items, true);
			$.set(checkpointSource, parsed.source ?? null, true);
			$.set(qualityIssues, [], true);
			$.set(nextAttemptBySlot, $.strict_equals(parsed?.schema, 'sico-authenticated-quality-drafts-v7') ? safeAttemptCounters(parsed.attempt_counters) : {}, true);
			$.set(attemptHistory, $.strict_equals(parsed?.schema, 'sico-authenticated-quality-drafts-v7') ? safeAttemptHistory(parsed.attempt_history) : [], true);

			$.set(
				lastAttemptInfo,
				$.get(attemptHistory).length
					? `Previous request: ${$.get(attemptHistory)[$.get(attemptHistory).length - 1].outcome} after ${$.get(attemptHistory)[$.get(attemptHistory).length - 1].elapsed_seconds}s.`
					: '',
				true
			);

			$.set(draftedCaseScope, qualityScopeKey(), true);
			$.set(draftedCaseStages, [], true);
			$.set(authorizedFrameworkSource, null);
			$.set(authorizedSourceRows, [], true);
			$.set(frameworkSourceSummary, '');
			$.set(coveragePlan, null);
			$.set(coveragePlanScope, '');
			$.set(coveragePlanError, '');
			$.set(draftedCaseNotice, `Loaded ${items.length} unsaved drafts. Imported records require review.`);
			$.set(draftedCaseError, '');
			saveLocalDraftCheckpoint();
		} catch(error) {
			$.set(draftedCaseError, error instanceof Error ? error.message : 'Checkpoint could not be loaded.', true);
		} finally {
			input.value = '';
		}
	}

	function nextQualitySlot() {
		const plan = validCoveragePlanForScope();

		if (!plan) return null;

		const planned = nextGenerationSlot(plan.generation_queue, $.get(qualityDrafts));

		return planned
			? {
				step: planned.activity_number,
				index: planned.draft_index,
				planned
			}
			: null;
	}

	function hasPendingGeneration() {
		try {
			return !validCoveragePlanForScope() || $.strict_equals(nextQualitySlot(), null, false);
		} catch {
			return true;
		} // A damaged checkpoint remains downloadable.
	}

	async function generateNewCaseDrafts(restart = false) {
		if ($.get(draftedCaseBusy)) return;

		if ($.get(organization).trim().length < 2 || $.get(frameworkSearch).trim().length < 2 || $.get(instruction).trim().length < 20) {
			$.set(draftedCaseError, 'Enter organization, exact framework and assessment objective.');

			return;
		}

		if (restart) {
			$.set(qualityDrafts, [], true);
			$.set(qualityIssues, [], true);
			$.set(loadedOlderCheckpoint, false);
			$.set(checkpointSource, null);
			$.set(nextAttemptBySlot, {}, true);
			$.set(attemptHistory, [], true);
			$.set(lastAttemptInfo, '');
			$.set(draftedCaseStages, [], true);
			$.set(draftedCaseScope, qualityScopeKey(), true);
			$.set(authorizedFrameworkSource, null);
			$.set(authorizedSourceRows, [], true);
			$.set(frameworkSourceSummary, '');
			$.set(coveragePlan, null);
			$.set(coveragePlanScope, '');
			$.set(coveragePlanError, '');
			$.set(showAllCoverageItems, false);
		} else if ($.strict_equals($.get(draftedCaseScope), qualityScopeKey(), false)) {
			$.set(draftedCaseError, 'The three inputs changed. Restore original inputs or start a new draft case.');

			return;
		}

		$.set(draftedCaseBusy, true);
		$.set(draftedCaseError, '');
		$.set(draftedCaseNotice, '');
		$.set(stopAfterPhase, false);

		try {
			if (!$.get(authorizedFrameworkSource)) (await $.track_reactivity_loss(loadSicoAuthorizedFrameworkSource()))();

			if ($.get(checkpointSource) && ($.strict_equals($.get(checkpointSource).source_digest, $.get(authorizedFrameworkSource)?.source_digest, false) || $.strict_equals($.get(checkpointSource).framework_id, $.get(authorizedFrameworkSource)?.framework_id, false))) {
				throw new Error('The checkpoint framework edition or source changed. Preserve this checkpoint and start a new case.');
			}

			if (!validCoveragePlanForScope() || $.strict_equals($.get(coveragePlan)?.source_digest, $.get(authorizedFrameworkSource)?.source_digest, false)) {
				$.set(draftedCaseNotice, 'Loading the authorized framework generation plan.');
				(await $.track_reactivity_loss(loadSicoCoveragePlan()))();
			}

			while (!$.get(stopAfterPhase) && $.strict_equals(qualityScopeKey(), $.get(draftedCaseScope))) {
				const slot = nextQualitySlot();

				if (!slot) {
					$.set(draftedCaseNotice, 'All scheduled Qwen drafts are ready for review. Evidence, risk ratings and approvals remain pending; the GRC case is not complete.');

					break;
				}

				$.set(currentGeneratingActivity, slot.step, true);

				const previous = plannedDraftContext(slot.planned, $.get(qualityDrafts));

				// Only a source-backed SICO reference is selected; the backend
				// independently rechecks authorization before using it.
				const chosenRef = $.strict_equals(slot.step, 10) ? slot.planned.focus_requirement_reference : '';

				const key = slotAttemptKey(slot.step, slot.index);

				// Only one model request per activity slot per run. A rejected
				// response is visible immediately; Resume rotates the focus.
				const attempt = Math.min(30, $.get(nextAttemptBySlot)[key] ?? 0);

				const started = Date.now();

				$.set(draftedCaseNotice, `Generating activity ${slot.step} of 16, draft ${slot.index}. One request at a time; accepted drafts are preserved.`);

				try {
					const response = (await $.track_reactivity_loss(sicoPostAction('quality_draft_one', {
						organization_name: $.get(organization).trim(),
						framework_name: $.get(frameworkSearch).trim(),
						problem: $.get(instruction).trim(),
						activity_number: String(slot.step),
						draft_index: String(slot.index),
						source_digest: String($.get(authorizedFrameworkSource)?.source_digest ?? ''),
						requirement_reference: chosenRef,
						previous_drafts: JSON.stringify(previous),
						focus_requirement_reference: slot.planned.focus_requirement_reference,
						focus_theme: slot.planned.theme,
						focus_attempt: String(attempt)
					})))();

					const item = response.data?.quality_draft_one;

					if (!item || $.strict_equals(item.quality_contract_checked, true, false) || $.strict_equals(item.business_records_written, false, false) || $.strict_equals(item.activity_number, slot.step, false) || !item.draft?.draft_reference || $.strict_equals(item.draft.draft_reference, key, false)) {
						throw new Error('The generated draft failed validation; previous drafts are preserved.');
					}

					const elapsed = Math.round((Date.now() - started) / 1000);

					$.set(
						nextAttemptBySlot,
						{
							...$.get(nextAttemptBySlot),
							[key]: Math.min(30, attempt + 1)
						},
						true
					);

					recordDraftAttempt(slot.step, slot.index, elapsed, 'accepted', 'Draft validated');
					$.set(qualityDrafts, [...$.get(qualityDrafts), item], true);
					$.set(draftedCaseNotice, `Generated ${$.get(qualityDrafts).filter((r) => $.strict_equals(r.provenance, 'qwen_quality_single_authenticated_v7')).length} new quality-checked drafts. Last request: ${elapsed}s. Source: ${$.get(authorizedSourceRows).length} authorized requirements. No records saved.`);
					saveLocalDraftCheckpoint();
				} catch(error) {
					const elapsed = Math.round((Date.now() - started) / 1000);
					const message = error instanceof Error ? error.message : 'Draft generation request failed.';

					$.set(
						nextAttemptBySlot,
						{
							...$.get(nextAttemptBySlot),
							[key]: Math.min(30, attempt + 1)
						},
						true
					);

					recordDraftAttempt(slot.step, slot.index, elapsed, 'rejected', message);

					$.set(
						qualityIssues,
						[
							...$.get(qualityIssues).slice(-29),
							`Activity ${slot.step}: ${message} (${elapsed}s)`
						],
						true
					);

					$.set(draftedCaseError, `Activity ${slot.step} was not accepted after ${elapsed}s. ${message} The next Resume will try a different focus; previous drafts are preserved.`);
					saveLocalDraftCheckpoint();

					break;
				}
			}
		} catch(error) {
			$.set(
				draftedCaseError,
				error instanceof Error
					? error.message
					: 'Generation failed; previous drafts remain.',
				true
			);
		} finally {
			$.set(draftedCaseBusy, false);
			$.set(currentGeneratingActivity, 0);
			saveLocalDraftCheckpoint();
		}
	}

	function downloadAuthorizedRequirementSource() {
		if (!$.get(authorizedFrameworkSource)?.complete_source_snapshot || !$.get(authorizedSourceRows).length) return;

		const payload = {
			schema: 'sico-user-exported-authorized-framework-requirements-v1',
			source_status: 'read_from_SICO_under_current_logged_in_user',
			source: $.get(authorizedFrameworkSource),
			requirements: $.get(authorizedSourceRows),
			official_edition_independently_verified: false,
			compliance_assessment_completed: false,
			business_records_written: false
		};

		const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }));

		try {
			const a = document.createElement('a');

			a.href = url;
			a.download = 'SICO-authorized-framework-source-READ-ONLY.json';
			a.click();
		} finally {
			URL.revokeObjectURL(url);
		}
	}

	function downloadCaseDraft() {
		if (!$.get(draftedCaseStages).length) return;

		const caseDraft = {
			schema: 'sico-unsaved-case-drafts-v1',
			organization_name: $.get(organization).trim(),
			framework_name: $.get(frameworkSearch).trim(),
			objective: $.get(instruction).trim(),
			generated_activity_count: $.get(draftedCaseStages).length,
			authorized_framework_source: $.get(authorizedFrameworkSource),
			authorized_requirements: $.get(authorizedFrameworkSource)?.complete_source_snapshot ? $.get(authorizedSourceRows) : [],
			authorized_requirements_not_compliance_verdict: true,
			business_records_written: false,
			note: 'Unverified hypothetical drafts. No GRC database records created.',
			activities: $.get(draftedCaseStages)
		};

		const url = URL.createObjectURL(new Blob([JSON.stringify(caseDraft, null, 2)], { type: 'application/json' }));

		try {
			const a = document.createElement('a');

			a.href = url;
			a.download = 'SICO-new-GRC-case-DRAFT.json';
			a.click();
		} finally {
			URL.revokeObjectURL(url);
		}
	}

	let creationBusy = $.tag($.state(false), 'creationBusy');
	let creationError = $.tag($.state(''), 'creationError');
	let creationNotice = $.tag($.state(''), 'creationNotice');
	let creationChoices = $.tag($.state(null), 'creationChoices');
	let confirmCaseCreation = $.tag($.state(false), 'confirmCaseCreation');
	let caseSaved = $.tag($.state(false), 'caseSaved');
	let stageBusy = $.tag($.state(false), 'stageBusy');
	let stageNotice = $.tag($.state(''), 'stageNotice');
	let stageError = $.tag($.state(''), 'stageError');
	let stageConfirmed = $.tag($.state(false), 'stageConfirmed');
	let stageHumanFacts = '';
	let frameworkBusinessContext = $.tag($.state(''), 'frameworkBusinessContext');
	let frameworkBatchSize = 2;
	let fullReview = $.tag($.state(null), 'fullReview');
	let fullReviewBusy = $.tag($.state(false), 'fullReviewBusy');
	let fullReviewAutomatic = $.tag($.state(false), 'fullReviewAutomatic');
	let fullReviewPause = $.tag($.state(false), 'fullReviewPause');
	let fullReviewError = $.tag($.state(''), 'fullReviewError');
	let fullReviewNotice = $.tag($.state(''), 'fullReviewNotice');
	let fullReviewCandidates = $.tag($.state($.proxy([])), 'fullReviewCandidates');
	let fullReviewShown = $.tag($.state(8), 'fullReviewShown');

	const fullReviewPercent = $.tag(
		$.derived(() => $.get(fullReview)?.coverage.accessible_total
			? Math.round($.get(fullReview).coverage.reviewed_through * 10000 / $.get(fullReview).coverage.accessible_total) / 100
			: 0),
		'fullReviewPercent'
	);

	const visibleFrameworkReviews = $.tag($.derived(() => $.get(fullReview)?.requirement_reviews.slice(0, $.get(fullReviewShown)) ?? []), 'visibleFrameworkReviews');

	function currentFrameworkScope() {
		return {
			organization_name: $.get(organization).trim(),
			framework_name: $.get(frameworkSearch).trim(),
			problem: $.get(instruction).trim(),
			business_context: $.get(frameworkBusinessContext).trim()
		};
	}

	function changedFrameworkInputs() {
		// A running model request is allowed to finish, but later batches will
		// not silently mix updated inputs with an earlier signed cursor.
		$.set(fullReviewPause, true);

		if ($.get(fullReview)) $.set(fullReviewNotice, 'Inputs changed. Restore the original inputs to resume, or explicitly start a new review.');
	}

	async function runFullFrameworkReview(automatic, restart = false) {
		if ($.get(fullReviewBusy)) return;

		const scope = currentFrameworkScope();

		if (scope.organization_name.length < 2 || scope.organization_name.length > 150 || scope.framework_name.length < 2 || scope.framework_name.length > 150 || scope.problem.length < 20 || scope.problem.length > 4000 || scope.business_context.length > 1200) {
			$.set(fullReviewError, 'Enter the organization, exact framework and assessment objective in the three fields above.');

			return;
		}

		if (restart) {
			$.set(fullReview, null);
			$.set(fullReviewCandidates, [], true);
			$.set(fullReviewShown, 8);
		} else if ($.get(fullReview) && $.strict_equals(scopeKey($.get(fullReview).scope), scopeKey(scope), false)) {
			$.set(fullReviewError, 'These inputs differ from the existing checkpoint. Restore them, or click Start new review.');

			return;
		}

		if ($.get(fullReview)?.coverage.complete) return;

		$.set(fullReviewBusy, true);
		$.set(fullReviewAutomatic, automatic, true);
		$.set(fullReviewPause, false);
		$.set(fullReviewError, '');
		$.set(fullReviewNotice, '');

		try {
			do {
				if ($.get(fullReviewPause) || $.strict_equals(scopeKey(currentFrameworkScope()), scopeKey(scope), false)) break;

				const result = (await $.track_reactivity_loss(sicoPostAction('ai_framework_batch', {
					organization_name: scope.organization_name,
					framework_name: scope.framework_name,
					problem: scope.problem,
					framework_business_context: scope.business_context,
					framework_batch_size: String(frameworkBatchSize),
					framework_cursor: $.get(fullReview)?.next_cursor ?? ''
				})))();

				const response = result.data?.ai_framework_batch;
				const batch = response?.framework_batch;

				if (!batch) throw new Error('No framework review was returned.');

				if ($.strict_equals(batch.status, 'partial', false) && $.strict_equals(batch.status, 'complete', false)) {
					$.set(
						fullReviewCandidates,
						Array.isArray(batch.candidate_frameworks)
							? batch.candidate_frameworks.map(String).slice(0, 8)
							: [],
						true
					);

					throw new Error('An exact authorized framework and accessible requirement list could not be found. Check the name and edition.');
				}

				if ($.strict_equals(scopeKey(currentFrameworkScope()), scopeKey(scope), false)) {
					throw new Error('Inputs changed during generation. This batch was not appended. Return to the original inputs and retry.');
				}

				$.set(fullReview, applyFrameworkBatch($.get(fullReview), scope, batch), true);
			} while (automatic && !$.get(fullReviewPause) && !$.get(fullReview)?.coverage.complete);

			if ($.get(fullReview)?.coverage.complete) {
				$.set(fullReviewNotice, 'All accessible assessable requirements have provisional reviews. Export the checkpoint and arrange evidence-based human verification.');
			} else if ($.get(fullReviewPause)) {
				$.set(fullReviewNotice, 'Paused after the current batch. Export the checkpoint before refreshing the page.');
			} else if ($.get(fullReview)) {
				$.set(fullReviewNotice, 'Batch completed. Continue when ready, or export a checkpoint.');
			}
		} catch(error) {
			$.set(
				fullReviewError,
				error instanceof Error
					? error.message
					: 'The current generation batch failed. Earlier reviews are preserved.',
				true
			);
		} finally {
			$.set(fullReviewBusy, false);
			$.set(fullReviewAutomatic, false);
		}
	}

	async function prepareNewGrcCase() {
		if ($.get(creationBusy) || $.get(preparedWorkflow) || $.get(caseSaved)) return;

		if ($.get(organization).trim().length < 2 || $.get(frameworkSearch).trim().length < 2 || $.get(instruction).trim().length < 20) {
			$.set(creationError, 'Enter an organization, exact loaded framework and objective of at least 20 characters.');

			return;
		}

		$.set(creationBusy, true);
		$.set(creationError, '');
		$.set(creationNotice, '');

		try {
			// This already exists in +page.server.ts and invokes the authenticated,
			// permission-checked Django lifecycle intake. No parallel GRC writer.
			const response = (await $.track_reactivity_loss(sicoPostAction('lifecycle_intake', {
				organization_name: $.get(organization).trim(),
				framework_name: $.get(frameworkSearch).trim(),
				problem: $.get(instruction).trim(),
				skip_legacy_generation: 'yes',
				selected_framework_id: frameworkConfirmation,
				selected_organization_id: organizationConfirmation
			})))();

			const data = response.data;

			if (data?.lifecycle_choices) {
				$.set(creationChoices, data.lifecycle_choices, true);
				$.set(creationNotice, 'Choose the exact authorized organization/framework record before creating a case.');

				return;
			}

			const prepared = data?.workflow_prepared;

			if (!prepared?.engagement_id || !prepared?.prepared_digest || !prepared?.review?.operation_payload) {
				throw new Error('The original SICO case-setup service did not provide a verified review.');
			}

			$.set(preparedWorkflow, prepared, true);
			$.set(activeEngagement, String(prepared.engagement_id), true);
			$.set(lifecycleProgress, prepared.lifecycle ?? null, true);
			$.set(recordedApproval, null);
			$.set(confirmCaseCreation, false);
			$.set(creationChoices, null);
			$.set(creationNotice, 'New assessment, scope and optional risk assessment are PREPARED through SICO. Review the exact creation plan before approving.');
		} catch(err) {
			$.set(creationError, err instanceof Error ? err.message : 'Unable to prepare this new GRC case.', true);
		} finally {
			$.set(creationBusy, false);
		}
	}

	async function approveAndCreateCase() {
		if ($.get(creationBusy) || $.get(caseSaved) || !$.get(confirmCaseCreation) || !$.get(preparedWorkflow)?.engagement_id || !$.get(preparedWorkflow)?.prepared_digest) return;

		$.set(creationBusy, true);
		$.set(creationError, '');

		try {
			// The existing SvelteKit action independently obtains server-side approval.
			// If its restricted case writer is enabled, it commits the SAME reviewed
			// payload through the existing atomic GRC service. Otherwise no case is saved.
			const response = (await $.track_reactivity_loss(sicoPostAction('workflow_approve', {
				engagement_id: String($.get(preparedWorkflow).engagement_id),
				prepared_digest: String($.get(preparedWorkflow).prepared_digest),
				confirm_reviewed: 'yes'
			})))();

			const data = response.data;

			$.set(recordedApproval, data?.workflow_approved ?? null, true);

			if ($.strict_equals(data?.workflow_committed?.business_records_written, true)) {
				$.set(caseSaved, true);
				$.set(lifecycleProgress, data.workflow_committed.lifecycle ?? $.get(lifecycleProgress), true);
				$.set(creationNotice, 'SICO confirmed new assessment records were created through its original GRC service.');
			} else {
				$.set(creationError, String(data?.workflow_error ?? 'Approval recorded, but the GRC case writer is disabled or saving was not independently verified. No case is claimed to be created.'), true);
			}
		} catch(err) {
			$.set(
				creationError,
				err instanceof Error
					? err.message
					: 'Case creation could not be verified; do not submit a duplicate.',
				true
			);
		} finally {
			$.set(creationBusy, false);
		}
	}

	async function prepareNextRealGrcStage() {
		if ($.get(stageBusy) || !$.get(caseSaved) || !$.get(activeEngagement) || $.get(lifecycleProposal)) return;

		$.set(stageBusy, true);
		$.set(stageError, '');
		$.set(stageNotice, '');

		try {
			const response = (await $.track_reactivity_loss(sicoPostAction('lifecycle_next', {
				engagement_id: $.get(activeEngagement),
				human_facts: stageHumanFacts.trim().slice(0, 1200)
			})))();

			const result = response.data?.lifecycle_next;

			if (!result) throw new Error('No verified lifecycle result was returned.');

			$.set(lifecycleProgress, result.lifecycle ?? $.get(lifecycleProgress), true);

			if ($.strict_equals(result.status, 'prepared_for_human_review') && result.review?.operation_payload) {
				$.set(lifecycleProposal, result, true);
				$.set(stageConfirmed, false);
				$.set(lifecycleApproval, null);
				$.set(stageNotice, `The ${result.stage} operation is prepared using SICO's existing GRC service. Nothing has been saved yet.`);
			} else {
				$.set(stageError, String(result.reason ?? result.questions?.join(' ') ?? 'More information or permission is needed before a new record can be prepared.'), true);
			}
		} catch(err) {
			$.set(stageError, err instanceof Error ? err.message : 'The GRC stage could not be prepared.', true);
		} finally {
			$.set(stageBusy, false);
		}
	}

	async function approveNextRealGrcStage() {
		if ($.get(stageBusy) || !$.get(stageConfirmed) || !$.get(lifecycleProposal)?.prepared_digest || !$.get(activeEngagement)) return;

		$.set(stageBusy, true);
		$.set(stageError, '');

		try {
			const response = (await $.track_reactivity_loss(sicoPostAction('lifecycle_stage_approve', {
				engagement_id: $.get(activeEngagement),
				stage: String($.get(lifecycleProposal).stage),
				prepared_digest: String($.get(lifecycleProposal).prepared_digest),
				confirm_reviewed: 'yes'
			})))();

			$.set(lifecycleApproval, response.data?.lifecycle_stage_approved ?? null, true);

			$.set(
				stageNotice,
				$.strict_equals($.get(lifecycleApproval)?.commit_enabled, true)
					? 'Human approval recorded. A separate click is required to create this new GRC record.'
					: 'Approval recorded, but this GRC writer is disabled. No business records were created.',
				true
			);
		} catch(err) {
			$.set(stageError, err instanceof Error ? err.message : 'Stage approval failed.', true);
		} finally {
			$.set(stageBusy, false);
		}
	}

	async function commitNextRealGrcStage() {
		if ($.get(stageBusy) || !$.get(lifecycleApproval)?.approved || $.strict_equals($.get(lifecycleApproval)?.commit_enabled, true, false) || !$.get(lifecycleProposal) || !$.get(activeEngagement)) return;

		$.set(stageBusy, true);
		$.set(stageError, '');

		try {
			const response = (await $.track_reactivity_loss(sicoPostAction('lifecycle_stage_commit', {
				engagement_id: $.get(activeEngagement),
				stage: String($.get(lifecycleProposal).stage),
				prepared_digest: String($.get(lifecycleProposal).prepared_digest),
				confirm_reviewed: 'yes'
			})))();

			const result = response.data?.lifecycle_stage_committed;

			if ($.strict_equals(result?.business_records_written, true, false)) throw new Error('Original SICO service did not verify that the record was saved.');

			$.set(lifecycleProgress, result.lifecycle ?? $.get(lifecycleProgress), true);
			$.set(stageNotice, `New ${$.get(lifecycleProposal).stage} records were saved through SICO's existing GRC service.`);
			$.set(lifecycleProposal, null);
			$.set(lifecycleApproval, null);
			$.set(stageConfirmed, false);
		} catch(err) {
			$.set(
				stageError,
				err instanceof Error
					? err.message
					: 'Stage save could not be verified; do not repeat blindly.',
				true
			);
		} finally {
			$.set(stageBusy, false);
		}
	}

	function downloadFullReview() {
		if (!$.get(fullReview) || $.get(fullReviewBusy)) return;

		const blob = new Blob([JSON.stringify($.get(fullReview), null, 2)], { type: 'application/json' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');

		a.href = url;
		a.download = `SICO_Activity1_v3_checkpoint_${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
		document.body.appendChild(a);
		a.click();
		a.remove();
		URL.revokeObjectURL(url);
		$.set(fullReviewNotice, 'Checkpoint exported to your device. Keep it private: it contains your assessment context and draft responses.');
	}

	async function importFullReview(event) {
		if ($.get(fullReviewBusy)) return;

		const field = event.currentTarget;
		const file = field.files?.[0];

		if (!file) return;

		try {
			if (file.size > 6 * 1024 * 1024) throw new Error('Checkpoint exceeds the 6 MB import limit.');

			const parsed = validateCheckpoint(JSON.parse((await $.track_reactivity_loss(file.text()))()));

			// Restore the exact previous inputs before allowing a signed-cursor continuation.
			$.set(organization, parsed.scope.organization_name, true);

			$.set(frameworkSearch, parsed.scope.framework_name, true);
			$.set(instruction, parsed.scope.problem, true);
			$.set(frameworkBusinessContext, parsed.scope.business_context, true);
			$.set(fullReview, parsed, true);
			$.set(fullReviewShown, 8);
			$.set(fullReviewCandidates, [], true);
			$.set(fullReviewError, '');
			$.set(fullReviewNotice, 'Imported an unverified, client-held draft. The backend will re-check the signed cursor, permissions and framework inventory on the next batch.');
		} catch(error) {
			$.set(fullReviewError, error instanceof Error ? error.message : 'Checkpoint could not be imported.', true);
		} finally {
			field.value = '';
		}
	}

	function clearStaleCase() {
		$.set(generatedSixteen, [], true);
		$.set(generatedFor, '');
		$.set(sixteenError, '');
		$.set(caseSaveNotice, '');
		$.set(preparedWorkflow, null);
		$.set(recordedApproval, null);
		$.set(lifecycleProgress, null);
		$.set(activeEngagement, '');
	}

	async function sicoPostAction(action, data) {
		const payload = new FormData();

		for (const [key, value] of Object.entries(data)) payload.set(key, value);

		const res = (await $.track_reactivity_loss(fetch(`?/${action}`, {
			method: 'POST',
			body: payload,
			headers: { accept: 'application/json' }
		})))();

		const parsed = deserialize((await $.track_reactivity_loss(res.text()))());

		if ($.strict_equals(parsed.type, 'success', false)) {
			const body = $.strict_equals(parsed.type, 'failure') ? parsed.data : null;

			throw new Error(String(body?.coverage_plan_error ?? body?.source_error ?? body?.case_draft_error ?? body?.framework_batch_error ?? body?.control_error ?? body?.ai_sixteen_error ?? body?.lifecycle_error ?? body?.workflow_error ?? 'The requested operation could not finish.'));
		}

		return parsed;
	}

	async function loadSavedControlProgress(caseId = '') {
		try {
			const response = (await $.track_reactivity_loss(sicoPostAction('requirement_review', {
				action: 'status',
				engagement_id: caseId || $.get(activeEngagement)
			})))();

			const progress = response.data?.control_review?.progress;

			if (progress?.case_id) {
				$.set(controlProgress, progress, true);
				$.set(controlError, '');
			}
		} catch {
			// An unprovisioned or not-yet-saved company has no control records.
			// Do not display a misleading result or ask for manual UUIDs.
		}
	}

	async function generateAndSaveNextControl() {
		if ($.get(controlBusy) || !$.get(controlProgress)?.case_id) return;

		$.set(controlBusy, true);
		$.set(controlError, '');
		$.set(controlNotice, '');

		try {
			const response = (await $.track_reactivity_loss(sicoPostAction('requirement_review', {
				action: 'generate_and_save',
				engagement_id: $.get(activeEngagement),
				confirm_preliminary_write: 'true'
			})))();

			const result = response.data?.control_review;

			if ($.strict_equals(result?.business_records_written, true, false) || $.strict_equals(result?.verified, true, false) || !result?.progress?.case_id || $.strict_equals(result?.record?.result, 'not_assessed', false)) {
				throw new Error('The audit record could not be independently verified as saved.');
			}

			$.set(controlProgress, result.progress, true);
			$.set(controlNotice, 'A control-specific review was generated and retrieved through SICO.');
		} catch(error) {
			$.set(controlError, error instanceof Error ? error.message : 'Control review could not be saved.', true);
		} finally {
			$.set(controlBusy, false);
		}
	}

	async function startGeneratedCase(event) {
		event.preventDefault();
		(await $.track_reactivity_loss(generateConnectedThrough(16)))();
	}

	async function generateConnectedThrough(lastActivity) {
		if ($.get(sixteenBusy) || !$.get(organization).trim() || !$.get(frameworkSearch).trim() || $.get(instruction).trim().length < 20) return;

		$.set(sixteenBusy, true);
		$.set(sixteenError, '');
		$.set(caseSaveNotice, '');

		const submitted = {
			organization_name: $.get(organization).trim(),
			framework_name: $.get(frameworkSearch).trim(),
			problem: $.get(instruction).trim()
		};

		const fingerprint = JSON.stringify(submitted);

		if ($.strict_equals(fingerprint, $.get(generatedFor), false)) {
			$.set(generatedSixteen, [], true);
			$.set(generatedFor, fingerprint, true);
		}

		try {
			// A single click generates sequentially; each validated result is
			// displayed immediately and a retry resumes the first missing item.
			for (let number = $.get(generatedSixteen).length + 1; number <= lastActivity; number++) {
				// Prior Qwen work products form the shared, unverified case context.
				// Only bounded earlier-stage text and proposed objects are forwarded.
				const keyStages = new Set([2, 4, 6, 7, 9, 11, 12]);

				const prior = $.get(generatedSixteen).filter((item) => keyStages.has(Number(item.number)) || Number(item.number) >= number - 2).map((item) => ({
					number: Number(item.number),
					analysis: String(item.analysis ?? '').slice(0, 180),
					proposed_work: String(item.proposed_work ?? '').slice(0, 180),
					case_profile: item.case_profile ?? null,
					candidate_assets: item.candidate_assets ?? []
				}));

				const response = (await $.track_reactivity_loss(sicoPostAction('ai_sixteen_item', {
					...submitted,
					activity_number: String(number),
					case_context: JSON.stringify(prior)
				})))();

				const result = response.data?.ai_sixteen_item;

				if (!result || $.strict_equals(result.activity_number, number, false) || !result.activity || $.strict_equals(result.activity.number, number, false) || $.strict_equals(typeof result.activity.analysis, 'string', false)) {
					throw new Error(`Activity ${number} returned an invalid draft result.`);
				}

				$.set(generatedSixteen, [...$.get(generatedSixteen), result.activity], true);
			}
		} catch(err) {
			$.set(
				sixteenError,
				err instanceof Error
					? err.message
					: 'Draft generation stopped unexpectedly.',
				true
			);
		}

		// This phase is GENERATION ONLY by user request. Never try to create,
		// approve or save an audit or tenant after finishing the 16 drafts.
		$.set(sixteenBusy, false);
	}

	const latestResponse = $.tag($.derived(() => $$props.form), 'latestResponse');

	$.user_effect(() => {
		if ($.get(latestResponse)?.sico_run) $.set(lastAgentRun, $.get(latestResponse), true);
		if ($.get(latestResponse)?.workflow_options) $.set(eligibleOptions, $.get(latestResponse).workflow_options, true);

		if ($.get(latestResponse)?.workflow_prepared) {
			$.set(generatedAssessment, $.get(latestResponse)?.generated_assessment ?? null, true);
			$.set(generationError, String($.get(latestResponse)?.generation_error ?? ''), true);
			$.set(preparedWorkflow, $.get(latestResponse).workflow_prepared, true);
			$.set(activeEngagement, String($.get(preparedWorkflow)?.engagement_id ?? ''), true);

			if ($.get(preparedWorkflow)?.lifecycle) $.set(lifecycleProgress, $.get(preparedWorkflow).lifecycle, true);

			$.set(recordedApproval, null);
		}

		if ($.get(latestResponse)?.workflow_review) {
			$.set(preparedWorkflow, $.get(latestResponse).workflow_review, true);

			$.set(
				recordedApproval,
				$.get(latestResponse).workflow_review.approved
					? {
						commit_enabled: $.get(latestResponse).workflow_review.commit_enabled
					}
					: null,
				true
			);
		}

		if ($.get(latestResponse)?.workflow_approved) $.set(recordedApproval, $.get(latestResponse).workflow_approved, true);

		const newlySavedCase = $.strict_equals($.get(latestResponse)?.workflow_committed?.business_records_written, true)
			? String($.get(preparedWorkflow)?.engagement_id ?? $.get(activeEngagement))
			: '';

		if (newlySavedCase && $.strict_equals(newlySavedCase, lastControlCaseLoaded, false)) {
			lastControlCaseLoaded = newlySavedCase;
			void loadSavedControlProgress(newlySavedCase);
		}

		if ($.get(latestResponse)?.workflow_committed?.workflow) {
			$.set(activeEngagement, String($.get(preparedWorkflow)?.engagement_id ?? $.get(activeEngagement)), true);

			if ($.get(latestResponse).workflow_committed.lifecycle) $.set(lifecycleProgress, $.get(latestResponse).workflow_committed.lifecycle, true);
		}

		if ($.get(latestResponse)?.lifecycle_status) {
			$.set(lifecycleProgress, $.get(latestResponse).lifecycle_status, true);
			$.set(activeEngagement, String($.get(latestResponse).lifecycle_status.engagement_id ?? $.get(activeEngagement)), true);
		}

		if ($.get(latestResponse)?.lifecycle_next) {
			$.set(lifecycleProposal, $.get(latestResponse).lifecycle_next, true);
			$.set(lifecycleApproval, null);

			if ($.get(lifecycleProposal)?.lifecycle) $.set(lifecycleProgress, $.get(lifecycleProposal).lifecycle, true);
		}

		if ($.get(latestResponse)?.lifecycle_stage_approved) $.set(lifecycleApproval, $.get(latestResponse).lifecycle_stage_approved, true);

		if ($.get(latestResponse)?.lifecycle_stage_committed) {
			if ($.get(latestResponse).lifecycle_stage_committed.lifecycle) $.set(lifecycleProgress, $.get(latestResponse).lifecycle_stage_committed.lifecycle, true);

			$.set(lifecycleProposal, null);
			$.set(lifecycleApproval, null);
		}
	});

	const result = $.tag($.derived(() => $.get(latestResponse)?.sico_run ? $.get(latestResponse) : $.get(lastAgentRun)), 'result');
	const run = $.tag($.derived(() => $.get(result)?.sico_run), 'run');
	const plan = $.tag($.derived(() => $.get(result)?.sico_plan), 'plan');
	const agent = $.tag($.derived(() => $.get(result)?.sico_agent), 'agent');
	const discovery = $.tag($.derived(() => $.get(result)?.discovery ?? $.get(result)?.records ?? null), 'discovery');
	const advisory = $.tag($.derived(() => $.get(result)?.draft ?? $.get(result)?.case_plan ?? $.get(result)?.case_intake ?? null), 'advisory');
	const providerMode = $.tag($.derived(() => String($.get(advisory)?.source_summary?.provider_mode ?? 'unknown')), 'providerMode');
	const providerFailed = $.tag($.derived(() => (/fallback|error|failed|unavailable/i).test($.get(providerMode))), 'providerFailed');
	const recordsReady = $.tag($.derived(() => $.strict_equals($.get(run)?.discovery, 'completed')), 'recordsReady');
	const intakeReady = $.tag($.derived(() => $.strict_equals($.get(run)?.intake, 'completed') && !$.get(providerFailed)), 'intakeReady');
	const recordGroups = $.tag($.derived(() => summarizeRecordGroups($.get(discovery))), 'recordGroups');
	const advisoryNotes = $.tag($.derived(() => $.get(intakeReady) ? collectPlainNotes($.get(advisory)) : []), 'advisoryNotes');
	const discoveryFailure = $.tag($.derived(() => String($.get(result)?.discovery_error ?? '').trim()), 'discoveryFailure');
	const intakeFailure = $.tag($.derived(() => String($.get(result)?.intake_error ?? '').trim()), 'intakeFailure');
	const needsOrganization = $.tag($.derived(() => !$.get(organization).trim() && ((/organization|domain/i).test($.get(discoveryFailure)) || !$.get(recordsReady))), 'needsOrganization');

	const examples = [
		'Assess the cybersecurity compliance of Demo Bank in Saudi Arabia against NCA ECC. Look up permitted records, identify missing information, and propose next steps for human review.',
		'Prepare an ISO 27001:2022 assessment plan. Confirm the scope, discover authorized records, and identify evidence that still needs review.',
		'Investigate our cybersecurity risk exposure, existing safeguards, and the additional information needed for a formal risk assessment.',
		'Assess our readiness for an internal security audit. Report only verified records and identify unanswered questions.'
	];

	function isObject(v) {
		return !!v && $.strict_equals(typeof v, 'object') && !Array.isArray(v);
	}

	function plainText(v) {
		if ($.strict_equals(typeof v, 'string', false)) return '';

		const s = v.replace(/\s+/g, ' ').trim();

		if (!s || (/^[\[{]/).test(s) || s.length > 650 || (/\"[a-z_]+\"\s*:/).test(s)) return '';

		return s;
	}

	// Presentation only: preserve the original keys and values in checkpoint JSON.
	// Turns labels like asset_type / owner_role / linkedRiskReference into readable text.
	function displayFieldLabel(raw) {
		const label = String(raw ?? '').replace(/([a-z0-9])([A-Z])/g, '$1 $2').replace(/[_-]+/g, ' ').replace(/\s*\/\s*/g, ' / ').replace(/\s+/g, ' ').trim();

		const abbreviations = new Set([
			'AI',
			'API',
			'CSF',
			'CVSS',
			'GRC',
			'ID',
			'IP',
			'ISO',
			'IT',
			'MFA',
			'NCA',
			'PDPL',
			'RBAC',
			'RPO',
			'RTO',
			'SICO',
			'SOC',
			'URL'
		]);

		return label.split(' ').map((part) => {
			if (!part || $.strict_equals(part, '/')) return part;

			const upper = part.toUpperCase();

			return abbreviations.has(upper)
				? upper
				: part.charAt(0).toUpperCase() + part.slice(1).toLowerCase();
		}).join(' ');
	}

	function itemLabel(v) {
		if (!isObject(v)) return '';

		for (const k of ['name', 'title', 'ref_id', 'label']) {
			const name = plainText(v[k]);

			if (name) return name.slice(0, 95);
		}

		return '';
	}

	function summarizeRecordGroups(source) {
		const found = new Map();

		const categories = [
			[/framework|librar/i, 'Frameworks'],
			[/asset/i, 'Assets'],
			[/polic/i, 'Policies'],
			[/applied.control|safeguard|^controls?$/i, 'Controls'],
			[/eviden/i, 'Evidence'],
			[/assessment/i, 'Assessments'],
			[/risk.scenario/i, 'Risk scenarios'],
			[/domain|folders?/i, 'Organizations / folders']
		];

		function walk(v, depth) {
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

	function collectPlainNotes(source) {
		const output = [];
		const matching = /summary|objective|recommendation|next.step|question|missing|warning|human.review/i;

		function walk(v, depth) {
			if (depth > 3 || output.length >= 5) return;

			if (Array.isArray(v)) {
				for (const child of v.slice(0, 6)) {
					const text = plainText(child);

					if (text && !output.includes(text)) output.push(text); else if (isObject(child)) walk(child, depth + 1);
				}

				return;
			}

			if (!isObject(v)) return;

			for (const [key, child] of Object.entries(v)) {
				if (output.length >= 5) return;
				if (!matching.test(key)) continue;

				const text = plainText(child);

				if (text && !output.includes(text)) output.push(text); else if (Array.isArray(child) || isObject(child)) walk(child, depth + 1);
			}
		}

		walk(source, 0);

		return output;
	}

	var $$exports = { ...$.legacy_api() };
	var div = root();

	$.head('3u1ruc', ($$anchor) => {
		var meta = root_1();

		$.effect(() => {
			$.document.title = 'SICO AI Next — Assessment Workspace';
		});

		$.append($$anchor, meta);
	});

	var div_1 = $.child(div);
	var section = $.sibling($.child(div_1), 2);
	var form_1 = $.sibling($.child(section), 4);
	var label_1 = $.child(form_1);
	var input_1 = $.sibling($.child(label_1));

	$.remove_input_defaults(input_1);
	$.reset(label_1);

	var label_2 = $.sibling(label_1, 2);
	var input_2 = $.sibling($.child(label_2));

	$.remove_input_defaults(input_2);
	$.reset(label_2);

	var label_3 = $.sibling(label_2, 2);
	var textarea = $.sibling($.child(label_3));

	$.remove_textarea_child(textarea);
	$.reset(label_3);

	var node = $.sibling(label_3, 2);

	{
		var consequent_1 = ($$anchor) => {
			var fragment = $.comment();
			var node_1 = $.first_child(fragment);

			{
				var consequent = ($$anchor) => {
					var button = root_3();

					$.delegated('click', button, function click() {
						return void generateNewCaseDrafts(false);
					});

					$.append($$anchor, button);
				};

				var d = $.derived(() => !$.get(draftedCaseBusy) && $.get(qualityIssues).length && $.strict_equals($.get(draftedCaseScope), qualityScopeKey()));

				var alternate = ($$anchor) => {
					var button_1 = root_4();
					var text_1 = $.child(button_1, true);

					$.reset(button_1);

					$.template_effect(
						($0) => {
							button_1.disabled = $0;

							$.set_text(text_1, $.get(draftedCaseBusy)
								? 'Generating GRC case drafts…'
								: 'Build GRC case with AI');
						},
						[
							() => $.get(draftedCaseBusy) || $.get(instruction).trim().length < 20 || !$.get(organization).trim() || !$.get(frameworkSearch).trim()
						]
					);

					$.append($$anchor, button_1);
				};

				$.add_svelte_meta(
					() => $.if(node_1, ($$render) => {
						if ($.get(d)) $$render(consequent); else $$render(alternate, false);
					}),
					'if',
					_page,
					1070,
					20
				);
			}

			$.append($$anchor, fragment);
		};

		$.add_svelte_meta(
			() => $.if(node, ($$render) => {
				if ($.strict_equals($.get(qualityDrafts).length, 0)) $$render(consequent_1);
			}),
			'if',
			_page,
			1069,
			16
		);
	}

	var label_4 = $.sibling(node, 2);
	var input_3 = $.sibling($.child(label_4));

	$.reset(label_4);
	$.reset(form_1);

	var node_2 = $.sibling(form_1, 2);

	{
		var consequent_2 = ($$anchor) => {
			var p = root_5();
			var text_2 = $.child(p, true);

			$.reset(p);
			$.template_effect(() => $.set_text(text_2, $.get(draftedCaseError)));
			$.append($$anchor, p);
		};

		$.add_svelte_meta(
			() => $.if(node_2, ($$render) => {
				if ($.get(draftedCaseError)) $$render(consequent_2);
			}),
			'if',
			_page,
			1082,
			12
		);
	}

	var node_3 = $.sibling(node_2, 2);

	{
		var consequent_3 = ($$anchor) => {
			var p_1 = root_6();
			var text_3 = $.child(p_1, true);

			$.reset(p_1);
			$.template_effect(() => $.set_text(text_3, $.get(draftedCaseNotice)));
			$.append($$anchor, p_1);
		};

		$.add_svelte_meta(
			() => $.if(node_3, ($$render) => {
				if ($.get(draftedCaseNotice)) $$render(consequent_3);
			}),
			'if',
			_page,
			1083,
			12
		);
	}

	var node_4 = $.sibling(node_3, 2);

	{
		var consequent_18 = ($$anchor) => {
			var div_2 = root_7();
			var div_3 = $.child(div_2);
			var h3 = $.child(div_3);
			var text_4 = $.child(h3);

			$.reset(h3);
			$.next(2);
			$.reset(div_3);

			var p_2 = $.sibling(div_3, 2);
			var text_5 = $.child(p_2, true);

			$.reset(p_2);

			var node_5 = $.sibling(p_2, 2);

			{
				let $0 = $.derived(validCoveragePlanForScope);

				$.add_svelte_meta(
					() => SicoGeneratedCase(node_5, {
						get items() {
							return $.get(qualityDrafts);
						},

						get plan() {
							return $.get($0);
						},

						get organization() {
							return $.get(organization);
						},

						get framework() {
							return $.get(frameworkSearch);
						}
					}),
					'component',
					_page,
					1091,
					20,
					{ componentTag: 'SicoGeneratedCase' }
				);
			}

			var node_6 = $.sibling(node_5, 2);

			{
				var consequent_6 = ($$anchor) => {
					var section_1 = root_8();
					var p_3 = $.sibling($.child(section_1), 2);
					var strong = $.child(p_3);
					var text_6 = $.child(strong, true);

					$.reset(strong);

					var strong_1 = $.sibling(strong, 2);
					var text_7 = $.child(strong_1, true);

					$.reset(strong_1);
					$.next(3);
					$.reset(p_3);

					var button_2 = $.sibling(p_3, 8);
					var details = $.sibling(button_2, 2);
					var summary = $.child(details);
					var text_8 = $.child(summary);

					$.reset(summary);

					var ol = $.sibling(summary, 2);

					$.add_svelte_meta(
						() => $.each(
							ol,
							21,
							() => ($.get(showAllCoverageItems)
								? validCoveragePlanForScope()?.requirement_work_items
								: validCoveragePlanForScope()?.requirement_work_items?.slice(0, 12)) ?? [],
							(item) => item.requirement_id,
							($$anchor, item) => {
								var li = root_9();
								var strong_2 = $.child(li);
								var text_9 = $.child(strong_2, true);

								$.reset(strong_2);

								var text_10 = $.sibling(strong_2);

								$.next();
								$.reset(li);

								$.template_effect(() => {
									$.set_text(text_9, $.get(item).reference);
									$.set_text(text_10, `: ${($.get(item).requirement_name || $.get(item).description) ?? ''} `);
								});

								$.append($$anchor, li);
							}
						),
						'each',
						_page,
						1108,
						36
					);

					$.reset(ol);

					var node_7 = $.sibling(ol, 2);

					{
						var consequent_4 = ($$anchor) => {
							var button_3 = root_10();

							$.delegated('click', button_3, function click_1() {
								$.set(showAllCoverageItems, true);
							});

							$.append($$anchor, button_3);
						};

						var d_1 = $.derived(() => !$.get(showAllCoverageItems) && (validCoveragePlanForScope()?.requirement_work_items?.length ?? 0) > 12);

						var consequent_5 = ($$anchor) => {
							var button_4 = root_11();

							$.delegated('click', button_4, function click_2() {
								$.set(showAllCoverageItems, false);
							});

							$.append($$anchor, button_4);
						};

						$.add_svelte_meta(
							() => $.if(node_7, ($$render) => {
								if ($.get(d_1)) $$render(consequent_4); else if ($.get(showAllCoverageItems)) $$render(consequent_5, 1);
							}),
							'if',
							_page,
							1115,
							32
						);
					}

					$.reset(details);
					$.reset(section_1);

					$.template_effect(
						($0, $1, $2) => {
							$.set_text(text_6, $0);
							$.set_text(text_7, $1);
							$.set_text(text_8, `Review requirement work queue (${$2 ?? ''})`);
						},
						[
							() => validCoveragePlanForScope()?.coverage?.requirements_considered_for_review,
							sourceLinkedReviewCount,
							() => validCoveragePlanForScope()?.requirement_work_items?.length ?? 0
						]
					);

					$.delegated('click', button_2, downloadCoveragePlan);
					$.append($$anchor, section_1);
				};

				var d_2 = $.derived(() => validCoveragePlanForScope());

				var consequent_7 = ($$anchor) => {
					var p_4 = root_12();

					$.append($$anchor, p_4);
				};

				$.add_svelte_meta(
					() => $.if(node_6, ($$render) => {
						if ($.get(d_2)) $$render(consequent_6); else if ($.get(draftedCaseBusy)) $$render(consequent_7, 1);
					}),
					'if',
					_page,
					1092,
					20
				);
			}

			var node_8 = $.sibling(node_6, 2);

			{
				var consequent_8 = ($$anchor) => {
					var p_5 = root_13();
					var text_11 = $.child(p_5, true);

					$.reset(p_5);
					$.template_effect(() => $.set_text(text_11, $.get(coveragePlanError)));
					$.append($$anchor, p_5);
				};

				$.add_svelte_meta(
					() => $.if(node_8, ($$render) => {
						if ($.get(coveragePlanError)) $$render(consequent_8);
					}),
					'if',
					_page,
					1125,
					20
				);
			}

			var div_4 = $.sibling(node_8, 4);
			var div_5 = $.child(div_4);

			$.reset(div_4);

			var p_6 = $.sibling(div_4, 2);
			var text_12 = $.child(p_6);

			$.reset(p_6);

			var div_6 = $.sibling(p_6, 2);
			var node_9 = $.child(div_6);

			{
				var consequent_9 = ($$anchor) => {
					var fragment_1 = root_14();
					var span = $.first_child(fragment_1);
					var text_13 = $.child(span);

					$.reset(span);

					var button_5 = $.sibling(span, 2);

					$.template_effect(() => $.set_text(text_13, `Generating activity ${$.get(currentGeneratingActivity) ?? ''} of 16 · Reviewing each draft individually.`));

					$.delegated('click', button_5, function click_3() {
						$.set(stopAfterPhase, true);
					});

					$.append($$anchor, fragment_1);
				};

				var alternate_1 = ($$anchor) => {
					var fragment_2 = root_15();
					var node_10 = $.first_child(fragment_2);

					{
						var consequent_10 = ($$anchor) => {
							var button_6 = root_16();

							$.delegated('click', button_6, function click_4() {
								return void generateNewCaseDrafts(false);
							});

							$.append($$anchor, button_6);
						};

						var d_3 = $.derived(() => hasPendingGeneration());

						$.add_svelte_meta(
							() => $.if(node_10, ($$render) => {
								if ($.get(d_3)) $$render(consequent_10);
							}),
							'if',
							_page,
							1135,
							28
						);
					}

					var button_7 = $.sibling(node_10, 2);

					$.delegated('click', button_7, function click_5() {
						return void generateNewCaseDrafts(true);
					});

					$.append($$anchor, fragment_2);
				};

				$.add_svelte_meta(
					() => $.if(node_9, ($$render) => {
						if ($.get(draftedCaseBusy)) $$render(consequent_9); else $$render(alternate_1, false);
					}),
					'if',
					_page,
					1131,
					24
				);
			}

			var node_11 = $.sibling(node_9, 2);

			{
				var consequent_11 = ($$anchor) => {
					var button_8 = root_17();

					$.delegated('click', button_8, downloadQualityCheckpoint);
					$.append($$anchor, button_8);
				};

				$.add_svelte_meta(
					() => $.if(node_11, ($$render) => {
						if ($.get(qualityDrafts).length) $$render(consequent_11);
					}),
					'if',
					_page,
					1140,
					24
				);
			}

			var node_12 = $.sibling(node_11, 2);

			{
				var consequent_12 = ($$anchor) => {
					var button_9 = root_18();

					$.delegated('click', button_9, downloadAuthorizedRequirementSource);
					$.append($$anchor, button_9);
				};

				$.add_svelte_meta(
					() => $.if(node_12, ($$render) => {
						if ($.get(authorizedFrameworkSource)?.complete_source_snapshot) $$render(consequent_12);
					}),
					'if',
					_page,
					1143,
					24
				);
			}

			$.reset(div_6);

			var node_13 = $.sibling(div_6, 2);

			{
				var consequent_13 = ($$anchor) => {
					var p_7 = root_19();
					var text_14 = $.child(p_7, true);

					$.reset(p_7);
					$.template_effect(() => $.set_text(text_14, $.get(lastAttemptInfo)));
					$.append($$anchor, p_7);
				};

				$.add_svelte_meta(
					() => $.if(node_13, ($$render) => {
						if ($.get(lastAttemptInfo)) $$render(consequent_13);
					}),
					'if',
					_page,
					1147,
					20
				);
			}

			var node_14 = $.sibling(node_13, 2);

			{
				var consequent_14 = ($$anchor) => {
					var details_1 = root_20();
					var summary_1 = $.child(details_1);
					var text_15 = $.child(summary_1);

					$.reset(summary_1);

					var ul = $.sibling(summary_1, 2);

					$.add_svelte_meta(
						() => $.each(ul, 21, () => [...$.get(attemptHistory)].reverse(), $.index, ($$anchor, attempt) => {
							var li_1 = root_21();
							var text_16 = $.child(li_1);

							$.reset(li_1);
							$.template_effect(() => $.set_text(text_16, `Activity ${$.get(attempt).activity ?? ''}, draft ${$.get(attempt).index ?? ''}: ${$.strict_equals($.get(attempt).outcome, 'accepted') ? 'Accepted' : 'Rejected'} · ${$.get(attempt).elapsed_seconds ?? ''}s · ${$.get(attempt).detail ?? ''}`));
							$.append($$anchor, li_1);
						}),
						'each',
						_page,
						1152,
						32
					);

					$.reset(ul);
					$.reset(details_1);
					$.template_effect(() => $.set_text(text_15, `Generation request history (${$.get(attemptHistory).length ?? ''} most recent)`));
					$.append($$anchor, details_1);
				};

				$.add_svelte_meta(
					() => $.if(node_14, ($$render) => {
						if ($.get(attemptHistory).length) $$render(consequent_14);
					}),
					'if',
					_page,
					1148,
					20
				);
			}

			var node_15 = $.sibling(node_14, 2);

			{
				var consequent_15 = ($$anchor) => {
					var p_8 = root_22();
					var text_17 = $.child(p_8, true);

					$.reset(p_8);
					$.template_effect(() => $.set_text(text_17, $.get(localCheckpointInfo)));
					$.append($$anchor, p_8);
				};

				$.add_svelte_meta(
					() => $.if(node_15, ($$render) => {
						if ($.get(localCheckpointInfo)) $$render(consequent_15);
					}),
					'if',
					_page,
					1158,
					20
				);
			}

			var node_16 = $.sibling(node_15, 2);

			{
				var consequent_16 = ($$anchor) => {
					var p_9 = root_23();
					var text_18 = $.child(p_9);

					$.reset(p_9);
					$.template_effect(() => $.set_text(text_18, `Failed attempts: ${$.get(qualityIssues).length ?? ''}. Last: ${$.get(qualityIssues)[$.get(qualityIssues).length - 1] ?? ''}`));
					$.append($$anchor, p_9);
				};

				$.add_svelte_meta(
					() => $.if(node_16, ($$render) => {
						if ($.get(qualityIssues).length) $$render(consequent_16);
					}),
					'if',
					_page,
					1159,
					20
				);
			}

			var node_17 = $.sibling(node_16, 2);

			$.add_svelte_meta(
				() => $.each(node_17, 17, () => $.get(qualityDrafts), (item) => item.draft.draft_reference, ($$anchor, item) => {
					var article = root_24();
					var h4 = $.child(article);
					var text_19 = $.child(h4);
					var span_1 = $.sibling(text_19);
					var text_20 = $.child(span_1, true);

					$.reset(span_1);
					$.reset(h4);

					var p_10 = $.sibling(h4, 2);
					var text_21 = $.child(p_10);

					$.reset(p_10);

					var p_11 = $.sibling(p_10, 2);
					var text_22 = $.child(p_11, true);

					$.reset(p_11);

					var dl = $.sibling(p_11, 2);

					$.add_svelte_meta(
						() => $.each(dl, 21, () => $.get(item).draft.proposed_attributes ?? [], $.index, ($$anchor, attr) => {
							var div_7 = root_25();
							var dt = $.child(div_7);
							var text_23 = $.child(dt, true);

							$.reset(dt);

							var dd = $.sibling(dt);
							var text_24 = $.child(dd, true);

							$.reset(dd);
							$.reset(div_7);

							$.template_effect(
								($0) => {
									$.set_text(text_23, $0);
									$.set_text(text_24, $.get(attr).proposed_value);
								},
								[() => displayFieldLabel($.get(attr).field)]
							);

							$.append($$anchor, div_7);
						}),
						'each',
						_page,
						1166,
						32
					);

					$.reset(dl);

					var p_12 = $.sibling(dl, 2);
					var text_25 = $.sibling($.child(p_12));

					$.reset(p_12);

					var p_13 = $.sibling(p_12, 2);
					var text_26 = $.sibling($.child(p_13));

					$.reset(p_13);

					var node_18 = $.sibling(p_13, 2);

					{
						var consequent_17 = ($$anchor) => {
							var p_14 = root_26();
							var text_27 = $.sibling($.child(p_14));

							$.reset(p_14);
							$.template_effect(($0) => $.set_text(text_27, ` ${$0 ?? ''}`), [() => $.get(item).draft.related_draft_references.join(', ')]);
							$.append($$anchor, p_14);
						};

						$.add_svelte_meta(
							() => $.if(node_18, ($$render) => {
								if ($.get(item).draft.related_draft_references?.length) $$render(consequent_17);
							}),
							'if',
							_page,
							1172,
							28
						);
					}

					$.next(2);
					$.reset(article);

					$.template_effect(
						($0) => {
							$.set_text(text_19, `${$.get(item).draft.title ?? ''} `);
							$.set_text(text_20, $.get(item).draft.draft_reference);

							$.set_text(text_21, `Activity ${$.get(item).activity_number ?? ''}: ${$.get(item).activity_name ?? ''} · SICO Module: ${$0 ?? ''} · ${$.strict_equals($.get(item).provenance, 'qwen_quality_single_authenticated_v7')
								? 'AI-generated draft · Pending verification'
								: 'Imported draft · Review required'}`);

							$.set_text(text_22, $.get(item).draft.content);
							$.set_text(text_25, ` ${$.get(item).draft.evidence_request ?? ''}`);
							$.set_text(text_26, ` ${$.get(item).draft.verification_question ?? ''}`);
						},
						[
							() => displayFieldLabel($.get(item).target_existing_sico_model)
						]
					);

					$.append($$anchor, article);
				}),
				'each',
				_page,
				1160,
				20
			);

			$.reset(div_2);

			$.template_effect(
				($0, $1, $2, $3) => {
					$.set_text(text_4, `Generated GRC case drafts — ${$0 ?? ''} new AI-generated drafts`);
					$.set_text(text_5, $.get(frameworkSourceSummary) || 'Framework catalog not loaded yet.');
					$.set_style(div_5, $1);
					$.set_text(text_12, `Activities with drafts: ${$2 ?? ''}/${firstPassTarget ?? ''}. Scheduled Qwen records: ${$3 ?? ''}. Each requirement review remains unassessed until evidence review.`);
				},
				[
					() => $.get(qualityDrafts).filter((r) => $.strict_equals(r.provenance, 'qwen_quality_single_authenticated_v7')).length,
					() => `width: ${Math.round(generationOrder.filter((n) => $.get(qualityDrafts).some((r) => $.strict_equals(r.activity_number, n))).length / firstPassTarget * 100)}%`,
					() => generationOrder.filter((n) => $.get(qualityDrafts).some((r) => $.strict_equals(r.activity_number, n))).length,
					() => validCoveragePlanForScope()?.generation_summary?.planned_qwen_detail_drafts ?? 'Planning pending'
				]
			);

			$.append($$anchor, div_2);
		};

		$.add_svelte_meta(
			() => $.if(node_4, ($$render) => {
				if ($.get(draftedCaseBusy) || $.get(qualityDrafts).length > 0 || $.get(authorizedFrameworkSource)) $$render(consequent_18);
			}),
			'if',
			_page,
			1084,
			12
		);
	}

	$.next(2);
	$.reset(section);
	$.next(2);
	$.reset(div_1);
	$.reset(div);

	$.template_effect(() => {
		input_1.disabled = $.get(draftedCaseBusy);
		input_2.disabled = $.get(draftedCaseBusy);
		textarea.disabled = $.get(draftedCaseBusy);
		input_3.disabled = $.get(draftedCaseBusy);
	});

	$.event('submit', form_1, function submit(event) {
		event.preventDefault();
		void generateNewCaseDrafts(true);
	});

	$.bind_value(
		input_1,
		function get() {
			return $.get(organization);
		},
		function set($$value) {
			$.set(organization, $$value);
		}
	);

	$.bind_value(
		input_2,
		function get() {
			return $.get(frameworkSearch);
		},
		function set($$value) {
			$.set(frameworkSearch, $$value);
		}
	);

	$.bind_value(
		textarea,
		function get() {
			return $.get(instruction);
		},
		function set($$value) {
			$.set(instruction, $$value);
		}
	);

	$.delegated('change', input_3, function change(event) {
		void importQualityCheckpoint(event);
	});

	$.append($$anchor, div);

	return $.pop($$exports);
}

if (import.meta.hot) {
	_page = $.hmr(_page);

	import.meta.hot.acceptExports(["default"],(module) => {
		$.cleanup_styles('s-OYdrvhQpzABG');
		_page[$.HMR].update(module.default);
	});
}

export default _page;

$.delegate(['click', 'change']);
import "/src/routes/(app)/(internal)/sico-ai-next/+page.svelte?t=1795515755236&svelte&type=style&lang.css";

//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJuYW1lcyI6W10sInNvdXJjZXMiOlsiK3BhZ2Uuc3ZlbHRlIl0sInNvdXJjZXNDb250ZW50IjpbIjwhLS0gU0lDTy1DTEVBUi1SRVBPUlQtVjI6IG5vIG5lc3RlZCBKU09OIGluIHByaW1hcnkgcmVwb3J0IC0tPlxuPHNjcmlwdCBsYW5nPVwidHNcIj5cbiAgICBpbXBvcnQgeyBlbmhhbmNlLCBkZXNlcmlhbGl6ZSwgYXBwbHlBY3Rpb24gfSBmcm9tICckYXBwL2Zvcm1zJztcbiAgICBpbXBvcnQgeyBvbk1vdW50IH0gZnJvbSAnc3ZlbHRlJztcbiAgICBpbXBvcnQgdHlwZSB7IEFjdGlvbkRhdGEgfSBmcm9tICcuLyR0eXBlcyc7XG4gICAgaW1wb3J0IFNpY29HZW5lcmF0ZWRDYXNlIGZyb20gXCIkbGliL2NvbXBvbmVudHMvQWlPbmJvYXJkaW5nL1NpY29HZW5lcmF0ZWRDYXNlLnN2ZWx0ZVwiO1xuICAgIGltcG9ydCB7IHZhbGlkYXRlR2VuZXJhdGlvblF1ZXVlLCBuZXh0R2VuZXJhdGlvblNsb3QsIHBsYW5uZWREcmFmdENvbnRleHQgfSBmcm9tICckbGliL3V0aWxzL3NpY29HZW5lcmF0aW9uUGxhbic7XG4gICAgaW1wb3J0IHtcbiAgICAgICAgYXBwbHlGcmFtZXdvcmtCYXRjaCwgdmFsaWRhdGVDaGVja3BvaW50LCBzY29wZUtleSxcbiAgICAgICAgdHlwZSBSZXZpZXdDaGVja3BvaW50LCB0eXBlIFJldmlld1Njb3BlXG4gICAgfSBmcm9tICckbGliL3V0aWxzL3NpY29GcmFtZXdvcmtSZXZpZXdWMyc7XG5cbiAgICBsZXQgeyBmb3JtIH06IHsgZm9ybTogQWN0aW9uRGF0YSB8IG51bGwgfSA9ICRwcm9wcygpO1xuICAgIGxldCBpbnN0cnVjdGlvbiA9ICRzdGF0ZSgnJyk7XG4gICAgbGV0IG9yZ2FuaXphdGlvbiA9ICRzdGF0ZSgnJyk7XG4gICAgbGV0IGJ1c3kgPSAkc3RhdGUoZmFsc2UpO1xuICAgIGxldCBsYXN0QWdlbnRSdW4gPSAkc3RhdGU8UmVjb3JkPHN0cmluZywgYW55PiB8IG51bGw+KG51bGwpO1xuICAgIGxldCBlbGlnaWJsZU9wdGlvbnMgPSAkc3RhdGU8UmVjb3JkPHN0cmluZywgYW55PiB8IG51bGw+KG51bGwpO1xuICAgIGxldCBwcmVwYXJlZFdvcmtmbG93ID0gJHN0YXRlPFJlY29yZDxzdHJpbmcsIGFueT4gfCBudWxsPihudWxsKTtcbiAgICBsZXQgcmVjb3JkZWRBcHByb3ZhbCA9ICRzdGF0ZTxSZWNvcmQ8c3RyaW5nLCBhbnk+IHwgbnVsbD4obnVsbCk7XG4gICAgbGV0IGFjdGl2ZUVuZ2FnZW1lbnQgPSAkc3RhdGUoJycpO1xuICAgIGxldCBnZW5lcmF0ZWRBc3Nlc3NtZW50ID0gJHN0YXRlPFJlY29yZDxzdHJpbmcsIGFueT4gfCBudWxsPihudWxsKTtcbiAgICBsZXQgZ2VuZXJhdGlvbkVycm9yID0gJHN0YXRlKCcnKTtcbiAgICBsZXQgZ2VuZXJhdGVkU2l4dGVlbiA9ICRzdGF0ZTxSZWNvcmQ8c3RyaW5nLCBhbnk+W10+KFtdKTtcbiAgICBsZXQgZ2VuZXJhdGVkRm9yID0gJHN0YXRlKCcnKTtcbiAgICBsZXQgc2l4dGVlbkJ1c3kgPSAkc3RhdGUoZmFsc2UpO1xuICAgIGxldCBzaXh0ZWVuRXJyb3IgPSAkc3RhdGUoJycpO1xuICAgIGxldCBjYXNlU2F2ZU5vdGljZSA9ICRzdGF0ZSgnJyk7XG4gICAgbGV0IGNvbnRyb2xQcm9ncmVzcyA9ICRzdGF0ZTxSZWNvcmQ8c3RyaW5nLCBhbnk+IHwgbnVsbD4obnVsbCk7XG4gICAgbGV0IGNvbnRyb2xCdXN5ID0gJHN0YXRlKGZhbHNlKTtcbiAgICBsZXQgY29udHJvbEVycm9yID0gJHN0YXRlKCcnKTtcbiAgICBsZXQgY29udHJvbE5vdGljZSA9ICRzdGF0ZSgnJyk7XG4gICAgbGV0IGxhc3RDb250cm9sQ2FzZUxvYWRlZCA9ICcnO1xuICAgIGxldCBsaWZlY3ljbGVQcm9ncmVzcyA9ICRzdGF0ZTxSZWNvcmQ8c3RyaW5nLCBhbnk+IHwgbnVsbD4obnVsbCk7XG4gICAgbGV0IGxpZmVjeWNsZVByb3Bvc2FsID0gJHN0YXRlPFJlY29yZDxzdHJpbmcsIGFueT4gfCBudWxsPihudWxsKTtcbiAgICBsZXQgbGlmZWN5Y2xlQXBwcm92YWwgPSAkc3RhdGU8UmVjb3JkPHN0cmluZywgYW55PiB8IG51bGw+KG51bGwpO1xuICAgIGxldCBldmlkZW5jZUNvbnRleHQgPSAkc3RhdGUoJycpO1xuICAgIGxldCBzZWxlY3RlZEZvbGRlciA9ICRzdGF0ZSgnJyk7XG4gICAgbGV0IHNlbGVjdGVkUGVyaW1ldGVyID0gJHN0YXRlKCdfX25ld19fJyk7XG4gICAgbGV0IGZyYW1ld29ya1NlYXJjaCA9ICRzdGF0ZSgnJyk7XG4gICAgbGV0IGZyYW1ld29ya0NvbmZpcm1hdGlvbiA9ICRzdGF0ZSgnJyk7XG4gICAgbGV0IG9yZ2FuaXphdGlvbkNvbmZpcm1hdGlvbiA9ICRzdGF0ZSgnJyk7XG4gICAgbGV0IHByb3Bvc2VkQXNzZXNzbWVudCA9ICRzdGF0ZSgnQ3liZXJzZWN1cml0eSBjb21wbGlhbmNlIGFzc2Vzc21lbnQnKTtcbiAgICBsZXQgcHJvcG9zZWRQZXJpbWV0ZXIgPSAkc3RhdGUoJ1NJQ08gY3liZXJzZWN1cml0eSBhc3Nlc3NtZW50IHBlcmltZXRlcicpO1xuICAgIGxldCBzZWxlY3RlZEZyYW1ld29yayA9ICRzdGF0ZSgnJyk7XG4gICAgbGV0IHNlbGVjdGVkUmlza01hdHJpeCA9ICRzdGF0ZSgnJyk7XG4gICAgLy8gQnVpbGQgYSBHUkMgY2FzZSBmb2xsb3dzIHRoZSBhdXRob3JpemVkIGZyYW1ld29yayBwbGFuLCBnZW5lcmF0aW5nIG9uZVxuICAgIC8vIFF3ZW4gcmVjb3JkIHBlciBkZXBlbmRlbmN5LXJlYWR5IHRhc2suIEFwcHJvdmFsIGFuZCB3cml0ZXJzIHN0YXkgc2VwYXJhdGUuXG4gICAgbGV0IGRyYWZ0ZWRDYXNlU3RhZ2VzID0gJHN0YXRlPFJlY29yZDxzdHJpbmcsIGFueT5bXT4oW10pO1xuICAgIGxldCBkcmFmdGVkQ2FzZVNjb3BlID0gJHN0YXRlKCcnKTtcbiAgICBsZXQgZHJhZnRlZENhc2VCdXN5ID0gJHN0YXRlKGZhbHNlKTtcbiAgICBsZXQgZHJhZnRlZENhc2VFcnJvciA9ICRzdGF0ZSgnJyk7XG4gICAgbGV0IGRyYWZ0ZWRDYXNlTm90aWNlID0gJHN0YXRlKCcnKTtcbiAgICBsZXQgc3RvcEFmdGVyUGhhc2UgPSAkc3RhdGUoZmFsc2UpO1xuICAgIGxldCBhdXRob3JpemVkRnJhbWV3b3JrU291cmNlID0gJHN0YXRlPFJlY29yZDxzdHJpbmcsIGFueT4gfCBudWxsPihudWxsKTtcbiAgICBsZXQgYXV0aG9yaXplZFNvdXJjZVJvd3MgPSAkc3RhdGU8UmVjb3JkPHN0cmluZywgYW55PltdPihbXSk7XG4gICAgbGV0IGZyYW1ld29ya1NvdXJjZVN1bW1hcnkgPSAkc3RhdGUoJycpO1xuICAgIC8vIFNvdXJjZS1ncm91bmRlZCByZXF1aXJlbWVudC1yZXZpZXcgcXVldWUuIEEgcHJlcGFyZWQgd29yayBpdGVtIGlzIE5PVCBhXG4gICAgLy8gY29tcGxldGVkIGFzc2Vzc21lbnQsIGFuZCB0aGlzIHN0YXRlIGlzIG5ldmVyIHVzZWQgdG8gYXV0aG9yaXplIGFjY2Vzcy5cbiAgICBsZXQgY292ZXJhZ2VQbGFuID0gJHN0YXRlPFJlY29yZDxzdHJpbmcsIGFueT4gfCBudWxsPihudWxsKTtcbiAgICBsZXQgY292ZXJhZ2VQbGFuU2NvcGUgPSAkc3RhdGUoJycpO1xuICAgIGxldCBjb3ZlcmFnZVBsYW5FcnJvciA9ICRzdGF0ZSgnJyk7XG4gICAgbGV0IHNob3dBbGxDb3ZlcmFnZUl0ZW1zID0gJHN0YXRlKGZhbHNlKTtcblxuICAgIGZ1bmN0aW9uIHZhbGlkQ292ZXJhZ2VQbGFuRm9yU2NvcGUoKTogUmVjb3JkPHN0cmluZywgYW55PiB8IG51bGwge1xuICAgICAgICByZXR1cm4gY292ZXJhZ2VQbGFuU2NvcGUgPT09IHF1YWxpdHlTY29wZUtleSgpID8gY292ZXJhZ2VQbGFuIDogbnVsbDtcbiAgICB9XG5cbiAgICAvLyBPbmx5IFF3ZW4gcmVjb3JkcyB0aGF0IGNpdGUgYSByZWFsIGF1dGhvcml6ZWQgcmVxdWlyZW1lbnQgY291bnQgYXNcbiAgICAvLyBwcm92aXNpb25hbCByZXZpZXcgZHJhZnRzLiBOZXZlciBjb3VudCB0aGVtIGFzIHZlcmlmaWVkIGNvbXBsaWFuY2UuXG4gICAgZnVuY3Rpb24gc291cmNlTGlua2VkUmV2aWV3Q291bnQoKTogbnVtYmVyIHtcbiAgICAgICAgY29uc3QgcGxhbiA9IHZhbGlkQ292ZXJhZ2VQbGFuRm9yU2NvcGUoKTtcbiAgICAgICAgaWYgKCFwbGFuKSByZXR1cm4gMDtcbiAgICAgICAgY29uc3QgYWxsb3dlZCA9IG5ldyBTZXQoKHBsYW4ucmVxdWlyZW1lbnRfd29ya19pdGVtcyA/PyBbXSkubWFwKChyb3c6IGFueSkgPT4gcm93LnJlcXVpcmVtZW50X2lkKSk7XG4gICAgICAgIGNvbnN0IHJlZmVyZW5jZWQgPSBuZXcgU2V0PHN0cmluZz4oKTtcbiAgICAgICAgZm9yIChjb25zdCByb3cgb2YgcXVhbGl0eURyYWZ0cykge1xuICAgICAgICAgICAgY29uc3QgaWQgPSBTdHJpbmcocm93Py5kcmFmdD8uYXV0aG9yaXplZF9yZXF1aXJlbWVudF9pZCA/PyAnJyk7XG4gICAgICAgICAgICBpZiAocm93Py5hY3Rpdml0eV9udW1iZXIgPT09IDEwICYmXG4gICAgICAgICAgICAgICAgcm93Py5hY3Rpdml0eV9jb2RlID09PSAncmVxdWlyZW1lbnRfcmV2aWV3cycgJiZcbiAgICAgICAgICAgICAgICByb3c/LmJ1c2luZXNzX3JlY29yZHNfd3JpdHRlbiA9PT0gZmFsc2UgJiZcbiAgICAgICAgICAgICAgICByb3c/LmRyYWZ0Py5zdGF0dXMgPT09ICduZXdfdW5zYXZlZF9haV9kcmFmdF9wZW5kaW5nX3ZlcmlmaWNhdGlvbicgJiZcbiAgICAgICAgICAgICAgICBhbGxvd2VkLmhhcyhpZCkpIHJlZmVyZW5jZWQuYWRkKGlkKTtcbiAgICAgICAgfVxuICAgICAgICByZXR1cm4gcmVmZXJlbmNlZC5zaXplO1xuICAgIH1cblxuICAgIGFzeW5jIGZ1bmN0aW9uIGxvYWRTaWNvQ292ZXJhZ2VQbGFuKCkge1xuICAgICAgICBpZiAoIWF1dGhvcml6ZWRGcmFtZXdvcmtTb3VyY2U/LmNvbXBsZXRlX3NvdXJjZV9zbmFwc2hvdCB8fFxuICAgICAgICAgICAgIWF1dGhvcml6ZWRGcmFtZXdvcmtTb3VyY2Uuc291cmNlX2RpZ2VzdCB8fCAhYXV0aG9yaXplZEZyYW1ld29ya1NvdXJjZS5mcmFtZXdvcmtfaWQgfHxcbiAgICAgICAgICAgICFhdXRob3JpemVkU291cmNlUm93cy5sZW5ndGgpIHtcbiAgICAgICAgICAgIHRocm93IG5ldyBFcnJvcignQW4gYXV0aG9yaXplZCBjb21wbGV0ZSBmcmFtZXdvcmsgc291cmNlIGlzIHJlcXVpcmVkIGJlZm9yZSBwbGFubmluZyBjb3ZlcmFnZS4nKTtcbiAgICAgICAgfVxuICAgICAgICBjb25zdCByZXNwb25zZSA9IGF3YWl0IHNpY29Qb3N0QWN0aW9uKCdjYXNlX2NvdmVyYWdlX3BsYW4nLCB7XG4gICAgICAgICAgICBvcmdhbml6YXRpb25fbmFtZTogb3JnYW5pemF0aW9uLnRyaW0oKSwgZnJhbWV3b3JrX25hbWU6IGZyYW1ld29ya1NlYXJjaC50cmltKCksXG4gICAgICAgICAgICBwcm9ibGVtOiBpbnN0cnVjdGlvbi50cmltKCksIHNvdXJjZV9kaWdlc3Q6IFN0cmluZyhhdXRob3JpemVkRnJhbWV3b3JrU291cmNlLnNvdXJjZV9kaWdlc3QpXG4gICAgICAgIH0pO1xuICAgICAgICBjb25zdCBwbGFuID0gKHJlc3BvbnNlLmRhdGEgYXMgUmVjb3JkPHN0cmluZywgYW55Pik/LmNhc2VfY292ZXJhZ2VfcGxhbjtcbiAgICAgICAgY29uc3Qgcm93cyA9IEFycmF5LmlzQXJyYXkocGxhbj8ucmVxdWlyZW1lbnRfd29ya19pdGVtcykgPyBwbGFuLnJlcXVpcmVtZW50X3dvcmtfaXRlbXMgOiBbXTtcbiAgICAgICAgY29uc3Qgc291cmNlSWRzID0gbmV3IFNldChhdXRob3JpemVkU291cmNlUm93cy5tYXAociA9PiBTdHJpbmcoci5yZXF1aXJlbWVudF9pZCkpKTtcbiAgICAgICAgaWYgKHBsYW4/LnNjaGVtYSAhPT0gJ3NpY28tYWktY292ZXJhZ2UtcGxhbi12MScgfHxcbiAgICAgICAgICAgIHBsYW4/LmJ1c2luZXNzX3JlY29yZHNfd3JpdHRlbiAhPT0gZmFsc2UgfHwgcGxhbj8uZnVsbF9mcmFtZXdvcmtfYXNzZXNzZWQgIT09IGZhbHNlIHx8XG4gICAgICAgICAgICBwbGFuLnNvdXJjZV9kaWdlc3QgIT09IGF1dGhvcml6ZWRGcmFtZXdvcmtTb3VyY2Uuc291cmNlX2RpZ2VzdCB8fFxuICAgICAgICAgICAgcGxhbi5mcmFtZXdvcmtfaWQgIT09IGF1dGhvcml6ZWRGcmFtZXdvcmtTb3VyY2UuZnJhbWV3b3JrX2lkIHx8XG4gICAgICAgICAgICByb3dzLmxlbmd0aCAhPT0gYXV0aG9yaXplZFNvdXJjZVJvd3MubGVuZ3RoIHx8XG4gICAgICAgICAgICBuZXcgU2V0KHJvd3MubWFwKChyOiBhbnkpID0+IFN0cmluZyhyLnJlcXVpcmVtZW50X2lkKSkpLnNpemUgIT09IHJvd3MubGVuZ3RoIHx8XG4gICAgICAgICAgICByb3dzLnNvbWUoKHI6IGFueSkgPT4gIXNvdXJjZUlkcy5oYXMoU3RyaW5nKHIucmVxdWlyZW1lbnRfaWQpKSB8fFxuICAgICAgICAgICAgICAgIHIucHJvcG9zZWRfcmVzdWx0ICE9PSAnbm90X2Fzc2Vzc2VkJyB8fCByLmV2aWRlbmNlX3ZlcmlmaWVkICE9PSBmYWxzZSkpIHtcbiAgICAgICAgICAgIHRocm93IG5ldyBFcnJvcignQ292ZXJhZ2UgcGxhbiBkb2VzIG5vdCBtYXRjaCB0aGUgYXV0aG9yaXplZCBTSUNPIGZyYW1ld29yayBzb3VyY2UuJyk7XG4gICAgICAgIH1cbiAgICAgICAgdmFsaWRhdGVHZW5lcmF0aW9uUXVldWUocGxhbiwgYXV0aG9yaXplZFNvdXJjZVJvd3MpO1xuICAgICAgICBjb3ZlcmFnZVBsYW4gPSBwbGFuO1xuICAgICAgICBjb3ZlcmFnZVBsYW5TY29wZSA9IHF1YWxpdHlTY29wZUtleSgpO1xuICAgICAgICBjb3ZlcmFnZVBsYW5FcnJvciA9ICcnO1xuICAgIH1cblxuICAgIGZ1bmN0aW9uIGRvd25sb2FkQ292ZXJhZ2VQbGFuKCkge1xuICAgICAgICBjb25zdCBwbGFuID0gdmFsaWRDb3ZlcmFnZVBsYW5Gb3JTY29wZSgpO1xuICAgICAgICBpZiAoIXBsYW4pIHJldHVybjtcbiAgICAgICAgY29uc3QgZmlsZSA9IG5ldyBCbG9iKFtKU09OLnN0cmluZ2lmeShwbGFuLCBudWxsLCAyKV0sIHsgdHlwZTogJ2FwcGxpY2F0aW9uL2pzb24nIH0pO1xuICAgICAgICBjb25zdCB1cmwgPSBVUkwuY3JlYXRlT2JqZWN0VVJMKGZpbGUpO1xuICAgICAgICB0cnkge1xuICAgICAgICAgICAgY29uc3QgbGluayA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoJ2EnKTtcbiAgICAgICAgICAgIGxpbmsuaHJlZiA9IHVybDsgbGluay5kb3dubG9hZCA9ICdTSUNPLUFJLVJFUVVJUkVNRU5ULVJFVklFVy1QTEFOLmpzb24nOyBsaW5rLmNsaWNrKCk7XG4gICAgICAgIH0gZmluYWxseSB7IFVSTC5yZXZva2VPYmplY3RVUkwodXJsKTsgfVxuICAgIH1cblxuXG4gICAgYXN5bmMgZnVuY3Rpb24gbG9hZFNpY29BdXRob3JpemVkRnJhbWV3b3JrU291cmNlKCkge1xuICAgICAgICBsZXQgY3Vyc29yID0gJyc7XG4gICAgICAgIGxldCBzb3VyY2VEaWdlc3QgPSAnJztcbiAgICAgICAgbGV0IHNlbGVjdGVkRnJhbWV3b3JrSWQgPSAnJztcbiAgICAgICAgY29uc3Qgcm93czogUmVjb3JkPHN0cmluZywgYW55PltdID0gW107XG4gICAgICAgIGZvciAobGV0IHBhZ2UgPSAwOyBwYWdlIDwgMjAwOyBwYWdlKyspIHtcbiAgICAgICAgICAgIGNvbnN0IHJlc3BvbnNlID0gYXdhaXQgc2ljb1Bvc3RBY3Rpb24oJ2ZyYW1ld29ya19zb3VyY2VfcGFnZScsIHtcbiAgICAgICAgICAgICAgICBmcmFtZXdvcmtfbmFtZTogZnJhbWV3b3JrU2VhcmNoLnRyaW0oKSwgY3Vyc29yXG4gICAgICAgICAgICB9KTtcbiAgICAgICAgICAgIGNvbnN0IHBhcnQgPSAocmVzcG9uc2UuZGF0YSBhcyBSZWNvcmQ8c3RyaW5nLCBhbnk+KT8uZnJhbWV3b3JrX3NvdXJjZV9wYWdlO1xuICAgICAgICAgICAgaWYgKCFwYXJ0KSB0aHJvdyBuZXcgRXJyb3IoJ05vIGF1dGhvcml6ZWQgZnJhbWV3b3JrIHNvdXJjZSB3YXMgcmV0dXJuZWQuJyk7XG4gICAgICAgICAgICBpZiAocGFydC5zdGF0dXMgIT09ICdwYXJ0aWFsJyAmJiBwYXJ0LnN0YXR1cyAhPT0gJ2NvbXBsZXRlJykge1xuICAgICAgICAgICAgICAgIGNvbnN0IGNhbmRpZGF0ZXMgPSBBcnJheS5pc0FycmF5KHBhcnQuY2FuZGlkYXRlcykgPyBwYXJ0LmNhbmRpZGF0ZXMuam9pbignLCAnKSA6ICcnO1xuICAgICAgICAgICAgICAgIHRocm93IG5ldyBFcnJvcignVGhlIGV4YWN0IHNlbGVjdGVkIGZyYW1ld29yayBjb3VsZCBub3QgYmUgcmVzb2x2ZWQgdXNpbmcgeW91ciBTSUNPIHBlcm1pc3Npb25zLicgKyAoY2FuZGlkYXRlcyA/IGAgQXV0aG9yaXplZCBtYXRjaGVzOiAke2NhbmRpZGF0ZXN9YCA6ICcnKSk7XG4gICAgICAgICAgICB9XG4gICAgICAgICAgICBpZiAoIXBhcnQuZnJhbWV3b3JrX2lkIHx8ICFwYXJ0LnNvdXJjZV9kaWdlc3QgfHwgIUFycmF5LmlzQXJyYXkocGFydC5yZXF1aXJlbWVudHMpKSB7XG4gICAgICAgICAgICAgICAgdGhyb3cgbmV3IEVycm9yKCdGcmFtZXdvcmsgY2F0YWxvZyBkaWQgbm90IGluY2x1ZGUgdmVyaWZpZWQgU0lDTyBzb3VyY2UgaWRlbnRpZmllcnMuJyk7XG4gICAgICAgICAgICB9XG4gICAgICAgICAgICBpZiAoc291cmNlRGlnZXN0ICYmIHNvdXJjZURpZ2VzdCAhPT0gcGFydC5zb3VyY2VfZGlnZXN0KSB7XG4gICAgICAgICAgICAgICAgdGhyb3cgbmV3IEVycm9yKCdGcmFtZXdvcmsgbGlicmFyeSBjaGFuZ2VkIGR1cmluZyByZXRyaWV2YWw7IHJlc3RhcnQgdGhlIGRyYWZ0LicpO1xuICAgICAgICAgICAgfVxuICAgICAgICAgICAgaWYgKHNlbGVjdGVkRnJhbWV3b3JrSWQgJiYgc2VsZWN0ZWRGcmFtZXdvcmtJZCAhPT0gcGFydC5mcmFtZXdvcmtfaWQpIHtcbiAgICAgICAgICAgICAgICB0aHJvdyBuZXcgRXJyb3IoJ1RoZSByZXNvbHZlZCBmcmFtZXdvcmsgY2hhbmdlZCBkdXJpbmcgcmV0cmlldmFsLicpO1xuICAgICAgICAgICAgfVxuICAgICAgICAgICAgc291cmNlRGlnZXN0ID0gcGFydC5zb3VyY2VfZGlnZXN0O1xuICAgICAgICAgICAgc2VsZWN0ZWRGcmFtZXdvcmtJZCA9IHBhcnQuZnJhbWV3b3JrX2lkO1xuICAgICAgICAgICAgcm93cy5wdXNoKC4uLnBhcnQucmVxdWlyZW1lbnRzKTtcbiAgICAgICAgICAgIGZyYW1ld29ya1NvdXJjZVN1bW1hcnkgPSBgU0lDTyBhdXRob3JpemVkIGZyYW1ld29yazogJHtyb3dzLmxlbmd0aH0vJHtwYXJ0LmNvdmVyYWdlLmFjY2Vzc2libGVfdG90YWx9IHJlcXVpcmVtZW50cyBsb2FkZWRgO1xuICAgICAgICAgICAgaWYgKHBhcnQuc3RhdHVzID09PSAnY29tcGxldGUnKSB7XG4gICAgICAgICAgICAgICAgaWYgKHBhcnQuY292ZXJhZ2UuYWNjZXNzaWJsZV90b3RhbCA9PT0gMCkge1xuICAgICAgICAgICAgICAgICAgICB0aHJvdyBuZXcgRXJyb3IoJ1RoZSBzZWxlY3RlZCBTSUNPIGZyYW1ld29yayBoYXMgbm8gcmVxdWlyZW1lbnRzIHJlYWRhYmxlIHRvIHRoaXMgdXNlci4nKTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgaWYgKCFwYXJ0LmNvdmVyYWdlLmNvbXBsZXRlIHx8IHJvd3MubGVuZ3RoICE9PSBwYXJ0LmNvdmVyYWdlLmFjY2Vzc2libGVfdG90YWwpIHtcbiAgICAgICAgICAgICAgICAgICAgdGhyb3cgbmV3IEVycm9yKCdGcmFtZXdvcmsgc291cmNlIGNvdW50IG1pc21hdGNoLiBObyBjb3ZlcmFnZSBjYW4gYmUgY2xhaW1lZC4nKTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgYXV0aG9yaXplZFNvdXJjZVJvd3MgPSByb3dzO1xuICAgICAgICAgICAgICAgIGF1dGhvcml6ZWRGcmFtZXdvcmtTb3VyY2UgPSB7XG4gICAgICAgICAgICAgICAgICAgIGZyYW1ld29ya19pZDogc2VsZWN0ZWRGcmFtZXdvcmtJZCxcbiAgICAgICAgICAgICAgICAgICAgbWF0Y2hlZF9mcmFtZXdvcms6IHBhcnQubWF0Y2hlZF9mcmFtZXdvcmssXG4gICAgICAgICAgICAgICAgICAgIHNvdXJjZV9kaWdlc3Q6IHNvdXJjZURpZ2VzdCxcbiAgICAgICAgICAgICAgICAgICAgYWNjZXNzaWJsZV90b3RhbDogcm93cy5sZW5ndGgsXG4gICAgICAgICAgICAgICAgICAgIGNvbXBsZXRlX3NvdXJjZV9zbmFwc2hvdDogdHJ1ZSxcbiAgICAgICAgICAgICAgICAgICAgZWRpdGlvbl9pbmRlcGVuZGVudGx5X3ZlcmlmaWVkOiBmYWxzZVxuICAgICAgICAgICAgICAgIH07XG4gICAgICAgICAgICAgICAgcmV0dXJuO1xuICAgICAgICAgICAgfVxuICAgICAgICAgICAgaWYgKCFwYXJ0Lm5leHRfY3Vyc29yIHx8IHBhcnQubmV4dF9jdXJzb3IgPT09IGN1cnNvcikge1xuICAgICAgICAgICAgICAgIHRocm93IG5ldyBFcnJvcignRnJhbWV3b3JrIHNvdXJjZSBwYWdpbmF0aW9uIGRpZCBub3QgYWR2YW5jZS4nKTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgICAgIGN1cnNvciA9IHBhcnQubmV4dF9jdXJzb3I7XG4gICAgICAgIH1cbiAgICAgICAgdGhyb3cgbmV3IEVycm9yKCdGcmFtZXdvcmsgc291cmNlIGlzIHRvbyBsYXJnZSB0byBsb2FkIHNhZmVseSBpbiBvbmUgcnVuLicpO1xuICAgIH1cblxuXG4gICAgZnVuY3Rpb24gZHJhZnRTY29wZUtleSgpIHtcbiAgICAgICAgcmV0dXJuIEpTT04uc3RyaW5naWZ5KFtvcmdhbml6YXRpb24udHJpbSgpLCBmcmFtZXdvcmtTZWFyY2gudHJpbSgpLCBpbnN0cnVjdGlvbi50cmltKCldKTtcbiAgICB9XG5cbiAgICAvLyBPbmUgUXdlbiByZWNvcmQgcGVyIHJlcXVlc3Q6IHRoZSBzYW1lIHByb3ZlbiBhcHByb2FjaCBhcyB0aGUgSFRNTCBydW5uZXIuXG4gICAgLy8gTm8gc2VydmVyLXNpZGUgR1JDIGNhc2UvYXNzZXQvcmlzayB3cml0ZXJzIGFyZSBldmVyIGNhbGxlZCBieSB0aGlzIHBhdGguXG4gICAgY29uc3QgZ2VuZXJhdGlvbk9yZGVyID0gWzEsIDIsIDMsIDQsIDUsIDYsIDcsIDgsIDksIDEwLCAxMSwgMTIsIDEzLCAxNCwgMTUsIDE2XTtcbiAgICBsZXQgcXVhbGl0eURyYWZ0cyA9ICRzdGF0ZTxSZWNvcmQ8c3RyaW5nLCBhbnk+W10+KFtdKTtcbiAgICBsZXQgcXVhbGl0eUlzc3VlcyA9ICRzdGF0ZTxzdHJpbmdbXT4oW10pO1xuICAgIGxldCBsb2FkZWRPbGRlckNoZWNrcG9pbnQgPSAkc3RhdGUoZmFsc2UpO1xuICAgIGxldCBjaGVja3BvaW50U291cmNlID0gJHN0YXRlPFJlY29yZDxzdHJpbmcsIGFueT4gfCBudWxsPihudWxsKTtcbiAgICBsZXQgY3VycmVudEdlbmVyYXRpbmdBY3Rpdml0eSA9ICRzdGF0ZSgwKTtcbiAgICBsZXQgbG9jYWxDaGVja3BvaW50SW5mbyA9ICRzdGF0ZSgnJyk7XG4gICAgLy8gVVgtb25seSBnZW5lcmF0aW9uIGRpYWdub3N0aWNzOiB0aGUgQVBJIGFuZCBzdG9yZWQgZHJhZnQgc2NoZW1hIHJlbWFpbiB1bmNoYW5nZWQuXG4gICAgdHlwZSBEcmFmdEF0dGVtcHQgPSB7IGFjdGl2aXR5OiBudW1iZXI7IGluZGV4OiBudW1iZXI7IGVsYXBzZWRfc2Vjb25kczogbnVtYmVyOyBvdXRjb21lOiAnYWNjZXB0ZWQnIHwgJ3JlamVjdGVkJzsgZGV0YWlsOiBzdHJpbmcgfTtcbiAgICBsZXQgYXR0ZW1wdEhpc3RvcnkgPSAkc3RhdGU8RHJhZnRBdHRlbXB0W10+KFtdKTtcbiAgICBsZXQgbmV4dEF0dGVtcHRCeVNsb3QgPSAkc3RhdGU8UmVjb3JkPHN0cmluZywgbnVtYmVyPj4oe30pO1xuICAgIGxldCBsYXN0QXR0ZW1wdEluZm8gPSAkc3RhdGUoJycpO1xuXG4gICAgZnVuY3Rpb24gc2xvdEF0dGVtcHRLZXkoc3RlcDogbnVtYmVyLCBpbmRleDogbnVtYmVyKSB7XG4gICAgICAgIHJldHVybiBgZHJhZnQtJHtTdHJpbmcoc3RlcCkucGFkU3RhcnQoMiwgJzAnKX0tJHtTdHJpbmcoaW5kZXgpLnBhZFN0YXJ0KDIsICcwJyl9YDtcbiAgICB9XG4gICAgZnVuY3Rpb24gc2FmZUF0dGVtcHRDb3VudGVycyhzb3VyY2U6IHVua25vd24pOiBSZWNvcmQ8c3RyaW5nLCBudW1iZXI+IHtcbiAgICAgICAgY29uc3QgcmVzdWx0OiBSZWNvcmQ8c3RyaW5nLCBudW1iZXI+ID0ge307XG4gICAgICAgIGlmICghc291cmNlIHx8IHR5cGVvZiBzb3VyY2UgIT09ICdvYmplY3QnIHx8IEFycmF5LmlzQXJyYXkoc291cmNlKSkgcmV0dXJuIHJlc3VsdDtcbiAgICAgICAgZm9yIChjb25zdCBba2V5LCB2YWx1ZV0gb2YgT2JqZWN0LmVudHJpZXMoc291cmNlKSkge1xuICAgICAgICAgICAgaWYgKC9eZHJhZnQtKD86MFsxLTldfDFbMC02XSktKD86MFsxLTldfFsxLTldWzAtOV17MSwzfXwxMDAwMCkkLy50ZXN0KGtleSkgJiZcbiAgICAgICAgICAgICAgICBOdW1iZXIuaXNJbnRlZ2VyKHZhbHVlKSAmJiBOdW1iZXIodmFsdWUpID49IDAgJiYgTnVtYmVyKHZhbHVlKSA8PSAzMCkgcmVzdWx0W2tleV0gPSBOdW1iZXIodmFsdWUpO1xuICAgICAgICB9XG4gICAgICAgIHJldHVybiByZXN1bHQ7XG4gICAgfVxuICAgIGZ1bmN0aW9uIHNhZmVBdHRlbXB0SGlzdG9yeShzb3VyY2U6IHVua25vd24pOiBEcmFmdEF0dGVtcHRbXSB7XG4gICAgICAgIGlmICghQXJyYXkuaXNBcnJheShzb3VyY2UpKSByZXR1cm4gW107XG4gICAgICAgIHJldHVybiBzb3VyY2Uuc2xpY2UoLTIwKS5maWx0ZXIoKGVudHJ5OiBhbnkpID0+XG4gICAgICAgICAgICBOdW1iZXIuaXNJbnRlZ2VyKGVudHJ5Py5hY3Rpdml0eSkgJiYgZW50cnkuYWN0aXZpdHkgPj0gMSAmJiBlbnRyeS5hY3Rpdml0eSA8PSAxNiAmJlxuICAgICAgICAgICAgTnVtYmVyLmlzSW50ZWdlcihlbnRyeT8uaW5kZXgpICYmIGVudHJ5LmluZGV4ID49IDEgJiYgZW50cnkuaW5kZXggPD0gMTAwMDAgJiZcbiAgICAgICAgICAgIHR5cGVvZiBlbnRyeT8uZWxhcHNlZF9zZWNvbmRzID09PSAnbnVtYmVyJyAmJiBlbnRyeS5lbGFwc2VkX3NlY29uZHMgPj0gMCAmJiBlbnRyeS5lbGFwc2VkX3NlY29uZHMgPCAzNjAwICYmXG4gICAgICAgICAgICAoZW50cnk/Lm91dGNvbWUgPT09ICdhY2NlcHRlZCcgfHwgZW50cnk/Lm91dGNvbWUgPT09ICdyZWplY3RlZCcpICYmIHR5cGVvZiBlbnRyeT8uZGV0YWlsID09PSAnc3RyaW5nJ1xuICAgICAgICApLm1hcCgoZW50cnk6IERyYWZ0QXR0ZW1wdCkgPT4gKHsgLi4uZW50cnksIGRldGFpbDogZW50cnkuZGV0YWlsLnNsaWNlKDAsIDE4MCkgfSkpO1xuICAgIH1cbiAgICBmdW5jdGlvbiByZWNvcmREcmFmdEF0dGVtcHQoYWN0aXZpdHk6IG51bWJlciwgaW5kZXg6IG51bWJlciwgZWxhcHNlZF9zZWNvbmRzOiBudW1iZXIsXG4gICAgICAgIG91dGNvbWU6ICdhY2NlcHRlZCcgfCAncmVqZWN0ZWQnLCBkZXRhaWw6IHN0cmluZykge1xuICAgICAgICBjb25zdCBldmVudCA9IHsgYWN0aXZpdHksIGluZGV4LCBlbGFwc2VkX3NlY29uZHMsIG91dGNvbWUsIGRldGFpbDogZGV0YWlsLnNsaWNlKDAsIDE4MCkgfTtcbiAgICAgICAgYXR0ZW1wdEhpc3RvcnkgPSBbLi4uYXR0ZW1wdEhpc3Rvcnkuc2xpY2UoLTE5KSwgZXZlbnRdO1xuICAgICAgICBsYXN0QXR0ZW1wdEluZm8gPSBgQWN0aXZpdHkgJHthY3Rpdml0eX0sIGRyYWZ0ICR7aW5kZXh9OiAke291dGNvbWV9IGFmdGVyICR7ZWxhcHNlZF9zZWNvbmRzfXMke291dGNvbWUgPT09ICdyZWplY3RlZCcgPyBgIMK3ICR7ZXZlbnQuZGV0YWlsfWAgOiAnJ30uYDtcbiAgICB9XG4gICAgLy8gQWxsIDE2IGV4aXN0aW5nIGFjdGl2aXRpZXMgdXNlIHNvdXJjZS1kcml2ZW4gdGFzayBjb3VudHMuIFBsYW5uaW5nIGFuZFxuICAgIC8vIHVuc2F2ZWQgUXdlbiB3b3JrIG5ldmVyIGNvdW50IGFzIGV2aWRlbmNlLXZlcmlmaWVkIGFzc2Vzc21lbnQgcmVzdWx0cy5cbiAgICBjb25zdCBmaXJzdFBhc3NUYXJnZXQgPSBnZW5lcmF0aW9uT3JkZXIubGVuZ3RoO1xuICAgIG9uTW91bnQoKCkgPT4ge1xuICAgICAgICAvLyBTYW1lLXRhYiByZWNvdmVyeSBvbmx5LiBOb3RoaW5nIGlzIHN0b3JlZCBpbiBTSUNPIGJ1c2luZXNzIHRhYmxlcy5cbiAgICAgICAgdHJ5IHtcbiAgICAgICAgICAgIGNvbnN0IHJhdyA9IHNlc3Npb25TdG9yYWdlLmdldEl0ZW0oJ3NpY28tYWktcXVhbGl0eS1kcmFmdC12NycpO1xuICAgICAgICAgICAgaWYgKCFyYXcpIHJldHVybjtcbiAgICAgICAgICAgIGNvbnN0IGNwID0gSlNPTi5wYXJzZShyYXcpO1xuICAgICAgICAgICAgaWYgKGNwPy5zY2hlbWEgIT09ICdzaWNvLWF1dGhlbnRpY2F0ZWQtcXVhbGl0eS1kcmFmdHMtdjcnIHx8ICFBcnJheS5pc0FycmF5KGNwLml0ZW1zKSkgcmV0dXJuO1xuICAgICAgICAgICAgaWYgKGNwLml0ZW1zLmxlbmd0aCA+IDE2MDAwMCB8fCBjcC5pdGVtcy5zb21lKChyOiBhbnkpID0+ICFyPy5kcmFmdD8uZHJhZnRfcmVmZXJlbmNlKSkgcmV0dXJuO1xuICAgICAgICAgICAgb3JnYW5pemF0aW9uID0gU3RyaW5nKGNwLnNjb3BlPy5vcmdhbml6YXRpb24gPz8gJycpLnNsaWNlKDAsIDE1MCk7XG4gICAgICAgICAgICBmcmFtZXdvcmtTZWFyY2ggPSBTdHJpbmcoY3Auc2NvcGU/LmZyYW1ld29yayA/PyAnJykuc2xpY2UoMCwgMTUwKTtcbiAgICAgICAgICAgIGluc3RydWN0aW9uID0gU3RyaW5nKGNwLnNjb3BlPy5vYmplY3RpdmUgPz8gJycpLnNsaWNlKDAsIDQwMDApO1xuICAgICAgICAgICAgaWYgKG9yZ2FuaXphdGlvbi5sZW5ndGggPCAyIHx8IGZyYW1ld29ya1NlYXJjaC5sZW5ndGggPCAyIHx8IGluc3RydWN0aW9uLmxlbmd0aCA8IDIwKSByZXR1cm47XG4gICAgICAgICAgICBxdWFsaXR5RHJhZnRzID0gY3AuaXRlbXM7XG4gICAgICAgICAgICBxdWFsaXR5SXNzdWVzID0gQXJyYXkuaXNBcnJheShjcC5pc3N1ZXMpID8gY3AuaXNzdWVzLnNsaWNlKC0zMCkgOiBbXTtcbiAgICAgICAgICAgIG5leHRBdHRlbXB0QnlTbG90ID0gc2FmZUF0dGVtcHRDb3VudGVycyhjcC5hdHRlbXB0X2NvdW50ZXJzKTtcbiAgICAgICAgICAgIGF0dGVtcHRIaXN0b3J5ID0gc2FmZUF0dGVtcHRIaXN0b3J5KGNwLmF0dGVtcHRfaGlzdG9yeSk7XG4gICAgICAgICAgICBpZiAoYXR0ZW1wdEhpc3RvcnkubGVuZ3RoKSB7IGNvbnN0IGxhc3QgPSBhdHRlbXB0SGlzdG9yeVthdHRlbXB0SGlzdG9yeS5sZW5ndGggLSAxXTsgbGFzdEF0dGVtcHRJbmZvID0gYExhc3QgcmVxdWVzdDogYWN0aXZpdHkgJHtsYXN0LmFjdGl2aXR5fSwgJHtsYXN0Lm91dGNvbWV9IGFmdGVyICR7bGFzdC5lbGFwc2VkX3NlY29uZHN9cy5gOyB9XG4gICAgICAgICAgICBjaGVja3BvaW50U291cmNlID0gY3Auc291cmNlID8/IG51bGw7XG4gICAgICAgICAgICBkcmFmdGVkQ2FzZVNjb3BlID0gcXVhbGl0eVNjb3BlS2V5KCk7XG4gICAgICAgICAgICBsb2NhbENoZWNrcG9pbnRJbmZvID0gJ1JlY292ZXJlZCBkcmFmdHMgZnJvbSB0aGlzIGJyb3dzZXIgdGFiLiBMb2FkIGZyYW1ld29yayBhY2Nlc3MgYWdhaW4gYmVmb3JlIHJlc3VtaW5nLic7XG4gICAgICAgIH0gY2F0Y2ggeyAvKiBBIGNvcnJ1cHQgb3IgdW5hdmFpbGFibGUgdGFiIGNoZWNrcG9pbnQgaXMgaWdub3JlZC4gKi8gfVxuICAgIH0pO1xuXG4gICAgZnVuY3Rpb24gcXVhbGl0eVNjb3BlS2V5KCkge1xuICAgICAgICByZXR1cm4gSlNPTi5zdHJpbmdpZnkoW29yZ2FuaXphdGlvbi50cmltKCksIGZyYW1ld29ya1NlYXJjaC50cmltKCksIGluc3RydWN0aW9uLnRyaW0oKV0pO1xuICAgIH1cbiAgICBmdW5jdGlvbiBjaGVja3BvaW50UGF5bG9hZCgpIHtcbiAgICAgICAgcmV0dXJuIHtcbiAgICAgICAgICAgIHNjaGVtYTogJ3NpY28tYXV0aGVudGljYXRlZC1xdWFsaXR5LWRyYWZ0cy12NycsXG4gICAgICAgICAgICBzY29wZTogeyBvcmdhbml6YXRpb246IG9yZ2FuaXphdGlvbi50cmltKCksIGZyYW1ld29yazogZnJhbWV3b3JrU2VhcmNoLnRyaW0oKSwgb2JqZWN0aXZlOiBpbnN0cnVjdGlvbi50cmltKCkgfSxcbiAgICAgICAgICAgIHNvdXJjZTogYXV0aG9yaXplZEZyYW1ld29ya1NvdXJjZSA/PyBjaGVja3BvaW50U291cmNlLFxuICAgICAgICAgICAgaXRlbXM6IHF1YWxpdHlEcmFmdHMsXG4gICAgICAgICAgICBnZW5lcmF0aW9uX3F1ZXVlOiB2YWxpZENvdmVyYWdlUGxhbkZvclNjb3BlKCk/LmdlbmVyYXRpb25fcXVldWUgPz8gW10sXG4gICAgICAgICAgICBpc3N1ZXM6IHF1YWxpdHlJc3N1ZXMsXG4gICAgICAgICAgICBhdHRlbXB0X2NvdW50ZXJzOiBuZXh0QXR0ZW1wdEJ5U2xvdCxcbiAgICAgICAgICAgIGF0dGVtcHRfaGlzdG9yeTogYXR0ZW1wdEhpc3Rvcnkuc2xpY2UoLTIwKSxcbiAgICAgICAgICAgIGJ1c2luZXNzX3JlY29yZHNfd3JpdHRlbjogZmFsc2UsXG4gICAgICAgICAgICBmdWxsX2ZyYW1ld29ya19hc3Nlc3NlZDogZmFsc2UsXG4gICAgICAgICAgICBzYXZlZF9pbl9icm93c2VyX29ubHk6IHRydWVcbiAgICAgICAgfTtcbiAgICB9XG4gICAgZnVuY3Rpb24gc2F2ZUxvY2FsRHJhZnRDaGVja3BvaW50KCkge1xuICAgICAgICB0cnkge1xuICAgICAgICAgICAgLy8gc2Vzc2lvblN0b3JhZ2Uga2VlcHMgdGhpcyBkcmFmdCBpbiB0aGUgY3VycmVudCBicm93c2VyIHNlc3Npb247XG4gICAgICAgICAgICAvLyB1c2VycyBjYW4gZG93bmxvYWQgYSBKU09OIGNoZWNrcG9pbnQgZm9yIGxvbmdlci10ZXJtIHN0b3JhZ2UuXG4gICAgICAgICAgICBzZXNzaW9uU3RvcmFnZS5zZXRJdGVtKCdzaWNvLWFpLXF1YWxpdHktZHJhZnQtdjcnLCBKU09OLnN0cmluZ2lmeShjaGVja3BvaW50UGF5bG9hZCgpKSk7XG4gICAgICAgICAgICBsb2NhbENoZWNrcG9pbnRJbmZvID0gJ1Byb2dyZXNzIHNhdmVkIGluIHRoaXMgYnJvd3NlciBzZXNzaW9uLiBEb3dubG9hZCBhIGNoZWNrcG9pbnQgdG8gcmVzdW1lIGFub3RoZXIgZGF5Lic7XG4gICAgICAgIH0gY2F0Y2ggeyBsb2NhbENoZWNrcG9pbnRJbmZvID0gJ0Jyb3dzZXIgc3RvcmFnZSBpcyB1bmF2YWlsYWJsZTsgZG93bmxvYWQgYSBjaGVja3BvaW50IGJlZm9yZSBsZWF2aW5nLic7IH1cbiAgICB9XG4gICAgZnVuY3Rpb24gZG93bmxvYWRRdWFsaXR5Q2hlY2twb2ludCgpIHtcbiAgICAgICAgY29uc3QgdXJsID0gVVJMLmNyZWF0ZU9iamVjdFVSTChuZXcgQmxvYihbSlNPTi5zdHJpbmdpZnkoY2hlY2twb2ludFBheWxvYWQoKSwgbnVsbCwgMildLCB7IHR5cGU6ICdhcHBsaWNhdGlvbi9qc29uJyB9KSk7XG4gICAgICAgIHRyeSB7IGNvbnN0IGxpbmsgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCdhJyk7IGxpbmsuaHJlZj11cmw7IGxpbmsuZG93bmxvYWQ9J1NJQ08tQUktcXVhbGl0eS1jYXNlLWNoZWNrcG9pbnQuanNvbic7IGxpbmsuY2xpY2soKTsgfVxuICAgICAgICBmaW5hbGx5IHsgVVJMLnJldm9rZU9iamVjdFVSTCh1cmwpOyB9XG4gICAgfVxuICAgIGFzeW5jIGZ1bmN0aW9uIGltcG9ydFF1YWxpdHlDaGVja3BvaW50KGV2ZW50OiBFdmVudCkge1xuICAgICAgICBjb25zdCBpbnB1dCA9IGV2ZW50LmN1cnJlbnRUYXJnZXQgYXMgSFRNTElucHV0RWxlbWVudDtcbiAgICAgICAgY29uc3QgZmlsZSA9IGlucHV0LmZpbGVzPy5bMF07XG4gICAgICAgIGlmICghZmlsZSB8fCBkcmFmdGVkQ2FzZUJ1c3kpIHJldHVybjtcbiAgICAgICAgdHJ5IHtcbiAgICAgICAgICAgIGlmIChmaWxlLnNpemUgPiA1MDAwMDAwMCkgdGhyb3cgbmV3IEVycm9yKCdDaGVja3BvaW50IGZpbGUgaXMgdG9vIGxhcmdlLicpO1xuICAgICAgICAgICAgY29uc3QgcGFyc2VkID0gSlNPTi5wYXJzZShhd2FpdCBmaWxlLnRleHQoKSk7XG4gICAgICAgICAgICBsZXQgaXRlbXM6IFJlY29yZDxzdHJpbmcsIGFueT5bXTtcbiAgICAgICAgICAgIGlmIChwYXJzZWQ/LnNjaGVtYSA9PT0gJ3NpY28tYXV0aGVudGljYXRlZC1xdWFsaXR5LWRyYWZ0cy12NycgJiYgQXJyYXkuaXNBcnJheShwYXJzZWQ/Lml0ZW1zKSkge1xuICAgICAgICAgICAgICAgIGlmIChwYXJzZWQ/LnNjb3BlPy5vcmdhbml6YXRpb24gIT09IG9yZ2FuaXphdGlvbi50cmltKCkgfHxcbiAgICAgICAgICAgICAgICAgICAgcGFyc2VkPy5zY29wZT8uZnJhbWV3b3JrICE9PSBmcmFtZXdvcmtTZWFyY2gudHJpbSgpIHx8XG4gICAgICAgICAgICAgICAgICAgIHBhcnNlZD8uc2NvcGU/Lm9iamVjdGl2ZSAhPT0gaW5zdHJ1Y3Rpb24udHJpbSgpKSB7XG4gICAgICAgICAgICAgICAgICAgIHRocm93IG5ldyBFcnJvcignVGhlIGNoZWNrcG9pbnQgYmVsb25ncyB0byBkaWZmZXJlbnQgY2FzZSBpbnB1dHMuIFVzZSB0aG9zZSBvcmlnaW5hbCBpbnB1dHMgZmlyc3QuJyk7XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgIGl0ZW1zID0gcGFyc2VkLml0ZW1zO1xuICAgICAgICAgICAgfSBlbHNlIGlmIChTdHJpbmcocGFyc2VkPy5zY2hlbWEgPz8gJycpLnN0YXJ0c1dpdGgoJ3NpY28tcXVhbGl0eScpICYmIEFycmF5LmlzQXJyYXkocGFyc2VkPy5nZW5lcmF0ZWRfaXRlbXMpKSB7XG4gICAgICAgICAgICAgICAgLy8gRXhpc3RpbmcgSFRNTC1ydW5uZXIgdjUgY2hlY2twb2ludDogc2hvdyBpdCBoZXJlIHdpdGhvdXRcbiAgICAgICAgICAgICAgICAvLyBjbGFpbWluZyBpbXBvcnRlZCBkcmFmdCBjb250ZW50IHBhc3NlZCB0aGlzIHY3IGdlbmVyYXRpb24uXG4gICAgICAgICAgICAgICAgaWYgKHBhcnNlZC5vcmdhbml6YXRpb24gIT09IG9yZ2FuaXphdGlvbi50cmltKCkgfHwgcGFyc2VkLmZyYW1ld29yayAhPT0gZnJhbWV3b3JrU2VhcmNoLnRyaW0oKSlcbiAgICAgICAgICAgICAgICAgICAgdGhyb3cgbmV3IEVycm9yKCdIVE1MIGNoZWNrcG9pbnQgb3JnYW5pemF0aW9uL2ZyYW1ld29yayBkbyBub3QgbWF0Y2ggdGhlIGZvcm0uJyk7XG4gICAgICAgICAgICAgICAgaXRlbXMgPSBwYXJzZWQuZ2VuZXJhdGVkX2l0ZW1zLm1hcCgoaXRlbTogYW55KSA9PiAoeyAuLi5pdGVtLCBwcm92ZW5hbmNlOiAnaW1wb3J0ZWRfaHRtbF9yZXZpZXdfcmVxdWlyZWQnIH0pKTtcbiAgICAgICAgICAgICAgICBsb2FkZWRPbGRlckNoZWNrcG9pbnQgPSB0cnVlO1xuICAgICAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgICAgICB0aHJvdyBuZXcgRXJyb3IoJ1Vuc3VwcG9ydGVkIGNoZWNrcG9pbnQuIFNlbGVjdCBhIFNJQ08gcXVhbGl0eSBnZW5lcmF0b3IgSlNPTiBjaGVja3BvaW50LicpO1xuICAgICAgICAgICAgfVxuICAgICAgICAgICAgaWYgKGl0ZW1zLmxlbmd0aCA+IDE2MDAwMCB8fCBpdGVtcy5zb21lKChyOiBhbnkpID0+XG4gICAgICAgICAgICAgICAgIS9eZHJhZnQtKD86MFsxLTldfDFbMC02XSktKD86MFsxLTldfFsxLTldWzAtOV17MSwzfXwxMDAwMCkkLy50ZXN0KHI/LmRyYWZ0Py5kcmFmdF9yZWZlcmVuY2UgPz8gJycpIHx8XG4gICAgICAgICAgICAgICAgIXI/LmRyYWZ0Py50aXRsZSB8fCAhcj8uZHJhZnQ/LnJlY29yZF90eXBlIHx8ICFyPy5hY3Rpdml0eV9udW1iZXIpKSB7XG4gICAgICAgICAgICAgICAgdGhyb3cgbmV3IEVycm9yKCdDaGVja3BvaW50IGNvbnRhaW5zIGludmFsaWQgZHJhZnQgcmVmZXJlbmNlcyBvciBjb250ZW50LicpO1xuICAgICAgICAgICAgfVxuICAgICAgICAgICAgaWYgKG5ldyBTZXQoaXRlbXMubWFwKChyOiBhbnkpID0+IHIuZHJhZnQuZHJhZnRfcmVmZXJlbmNlKSkuc2l6ZSAhPT0gaXRlbXMubGVuZ3RoKVxuICAgICAgICAgICAgICAgIHRocm93IG5ldyBFcnJvcignQ2hlY2twb2ludCBjb250YWlucyBkdXBsaWNhdGUgZHJhZnQgcmVmZXJlbmNlcy4nKTtcbiAgICAgICAgICAgIHF1YWxpdHlEcmFmdHMgPSBpdGVtcztcbiAgICAgICAgICAgIGNoZWNrcG9pbnRTb3VyY2UgPSBwYXJzZWQuc291cmNlID8/IG51bGw7XG4gICAgICAgICAgICBxdWFsaXR5SXNzdWVzID0gW107XG4gICAgICAgICAgICBuZXh0QXR0ZW1wdEJ5U2xvdCA9IHBhcnNlZD8uc2NoZW1hID09PSAnc2ljby1hdXRoZW50aWNhdGVkLXF1YWxpdHktZHJhZnRzLXY3J1xuICAgICAgICAgICAgICAgID8gc2FmZUF0dGVtcHRDb3VudGVycyhwYXJzZWQuYXR0ZW1wdF9jb3VudGVycykgOiB7fTtcbiAgICAgICAgICAgIGF0dGVtcHRIaXN0b3J5ID0gcGFyc2VkPy5zY2hlbWEgPT09ICdzaWNvLWF1dGhlbnRpY2F0ZWQtcXVhbGl0eS1kcmFmdHMtdjcnXG4gICAgICAgICAgICAgICAgPyBzYWZlQXR0ZW1wdEhpc3RvcnkocGFyc2VkLmF0dGVtcHRfaGlzdG9yeSkgOiBbXTtcbiAgICAgICAgICAgIGxhc3RBdHRlbXB0SW5mbyA9IGF0dGVtcHRIaXN0b3J5Lmxlbmd0aFxuICAgICAgICAgICAgICAgID8gYFByZXZpb3VzIHJlcXVlc3Q6ICR7YXR0ZW1wdEhpc3RvcnlbYXR0ZW1wdEhpc3RvcnkubGVuZ3RoIC0gMV0ub3V0Y29tZX0gYWZ0ZXIgJHthdHRlbXB0SGlzdG9yeVthdHRlbXB0SGlzdG9yeS5sZW5ndGggLSAxXS5lbGFwc2VkX3NlY29uZHN9cy5gIDogJyc7XG4gICAgICAgICAgICBkcmFmdGVkQ2FzZVNjb3BlID0gcXVhbGl0eVNjb3BlS2V5KCk7XG4gICAgICAgICAgICBkcmFmdGVkQ2FzZVN0YWdlcyA9IFtdO1xuICAgICAgICAgICAgYXV0aG9yaXplZEZyYW1ld29ya1NvdXJjZSA9IG51bGw7IGF1dGhvcml6ZWRTb3VyY2VSb3dzID0gW107IGZyYW1ld29ya1NvdXJjZVN1bW1hcnkgPSAnJztcbiAgICAgICAgICAgIGNvdmVyYWdlUGxhbiA9IG51bGw7IGNvdmVyYWdlUGxhblNjb3BlID0gJyc7IGNvdmVyYWdlUGxhbkVycm9yID0gJyc7XG4gICAgICAgICAgICBkcmFmdGVkQ2FzZU5vdGljZSA9IGBMb2FkZWQgJHtpdGVtcy5sZW5ndGh9IHVuc2F2ZWQgZHJhZnRzLiBJbXBvcnRlZCByZWNvcmRzIHJlcXVpcmUgcmV2aWV3LmA7XG4gICAgICAgICAgICBkcmFmdGVkQ2FzZUVycm9yID0gJyc7XG4gICAgICAgICAgICBzYXZlTG9jYWxEcmFmdENoZWNrcG9pbnQoKTtcbiAgICAgICAgfSBjYXRjaCAoZXJyb3IpIHsgZHJhZnRlZENhc2VFcnJvciA9IGVycm9yIGluc3RhbmNlb2YgRXJyb3IgPyBlcnJvci5tZXNzYWdlIDogJ0NoZWNrcG9pbnQgY291bGQgbm90IGJlIGxvYWRlZC4nOyB9XG4gICAgICAgIGZpbmFsbHkgeyBpbnB1dC52YWx1ZSA9ICcnOyB9XG4gICAgfVxuICAgIGZ1bmN0aW9uIG5leHRRdWFsaXR5U2xvdCgpIHtcbiAgICAgICAgY29uc3QgcGxhbiA9IHZhbGlkQ292ZXJhZ2VQbGFuRm9yU2NvcGUoKTtcbiAgICAgICAgaWYgKCFwbGFuKSByZXR1cm4gbnVsbDtcbiAgICAgICAgY29uc3QgcGxhbm5lZCA9IG5leHRHZW5lcmF0aW9uU2xvdChwbGFuLmdlbmVyYXRpb25fcXVldWUsIHF1YWxpdHlEcmFmdHMpO1xuICAgICAgICByZXR1cm4gcGxhbm5lZCA/IHsgc3RlcDogcGxhbm5lZC5hY3Rpdml0eV9udW1iZXIsIGluZGV4OiBwbGFubmVkLmRyYWZ0X2luZGV4LCBwbGFubmVkIH0gOiBudWxsO1xuICAgIH1cbiAgICBmdW5jdGlvbiBoYXNQZW5kaW5nR2VuZXJhdGlvbigpOiBib29sZWFuIHtcbiAgICAgICAgdHJ5IHsgcmV0dXJuICF2YWxpZENvdmVyYWdlUGxhbkZvclNjb3BlKCkgfHwgbmV4dFF1YWxpdHlTbG90KCkgIT09IG51bGw7IH1cbiAgICAgICAgY2F0Y2ggeyByZXR1cm4gdHJ1ZTsgfSAvLyBBIGRhbWFnZWQgY2hlY2twb2ludCByZW1haW5zIGRvd25sb2FkYWJsZS5cbiAgICB9XG4gICAgYXN5bmMgZnVuY3Rpb24gZ2VuZXJhdGVOZXdDYXNlRHJhZnRzKHJlc3RhcnQgPSBmYWxzZSkge1xuICAgICAgICBpZiAoZHJhZnRlZENhc2VCdXN5KSByZXR1cm47XG4gICAgICAgIGlmIChvcmdhbml6YXRpb24udHJpbSgpLmxlbmd0aCA8IDIgfHwgZnJhbWV3b3JrU2VhcmNoLnRyaW0oKS5sZW5ndGggPCAyIHx8IGluc3RydWN0aW9uLnRyaW0oKS5sZW5ndGggPCAyMCkge1xuICAgICAgICAgICAgZHJhZnRlZENhc2VFcnJvciA9ICdFbnRlciBvcmdhbml6YXRpb24sIGV4YWN0IGZyYW1ld29yayBhbmQgYXNzZXNzbWVudCBvYmplY3RpdmUuJztcbiAgICAgICAgICAgIHJldHVybjtcbiAgICAgICAgfVxuICAgICAgICBpZiAocmVzdGFydCkge1xuICAgICAgICAgICAgcXVhbGl0eURyYWZ0cyA9IFtdOyBxdWFsaXR5SXNzdWVzID0gW107IGxvYWRlZE9sZGVyQ2hlY2twb2ludCA9IGZhbHNlOyBjaGVja3BvaW50U291cmNlID0gbnVsbDtcbiAgICAgICAgICAgIG5leHRBdHRlbXB0QnlTbG90ID0ge307IGF0dGVtcHRIaXN0b3J5ID0gW107IGxhc3RBdHRlbXB0SW5mbyA9ICcnO1xuICAgICAgICAgICAgZHJhZnRlZENhc2VTdGFnZXMgPSBbXTsgZHJhZnRlZENhc2VTY29wZSA9IHF1YWxpdHlTY29wZUtleSgpO1xuICAgICAgICAgICAgYXV0aG9yaXplZEZyYW1ld29ya1NvdXJjZSA9IG51bGw7IGF1dGhvcml6ZWRTb3VyY2VSb3dzID0gW107IGZyYW1ld29ya1NvdXJjZVN1bW1hcnkgPSAnJztcbiAgICAgICAgICAgIGNvdmVyYWdlUGxhbiA9IG51bGw7IGNvdmVyYWdlUGxhblNjb3BlID0gJyc7IGNvdmVyYWdlUGxhbkVycm9yID0gJyc7IHNob3dBbGxDb3ZlcmFnZUl0ZW1zID0gZmFsc2U7XG4gICAgICAgIH0gZWxzZSBpZiAoZHJhZnRlZENhc2VTY29wZSAhPT0gcXVhbGl0eVNjb3BlS2V5KCkpIHtcbiAgICAgICAgICAgIGRyYWZ0ZWRDYXNlRXJyb3IgPSAnVGhlIHRocmVlIGlucHV0cyBjaGFuZ2VkLiBSZXN0b3JlIG9yaWdpbmFsIGlucHV0cyBvciBzdGFydCBhIG5ldyBkcmFmdCBjYXNlLic7XG4gICAgICAgICAgICByZXR1cm47XG4gICAgICAgIH1cbiAgICAgICAgZHJhZnRlZENhc2VCdXN5ID0gdHJ1ZTsgZHJhZnRlZENhc2VFcnJvcj0nJzsgZHJhZnRlZENhc2VOb3RpY2U9Jyc7IHN0b3BBZnRlclBoYXNlPWZhbHNlO1xuICAgICAgICB0cnkge1xuICAgICAgICAgICAgaWYgKCFhdXRob3JpemVkRnJhbWV3b3JrU291cmNlKSBhd2FpdCBsb2FkU2ljb0F1dGhvcml6ZWRGcmFtZXdvcmtTb3VyY2UoKTtcbiAgICAgICAgICAgIGlmIChjaGVja3BvaW50U291cmNlICYmIChjaGVja3BvaW50U291cmNlLnNvdXJjZV9kaWdlc3QgIT09IGF1dGhvcml6ZWRGcmFtZXdvcmtTb3VyY2U/LnNvdXJjZV9kaWdlc3QgfHxcbiAgICAgICAgICAgICAgICBjaGVja3BvaW50U291cmNlLmZyYW1ld29ya19pZCAhPT0gYXV0aG9yaXplZEZyYW1ld29ya1NvdXJjZT8uZnJhbWV3b3JrX2lkKSkge1xuICAgICAgICAgICAgICAgIHRocm93IG5ldyBFcnJvcignVGhlIGNoZWNrcG9pbnQgZnJhbWV3b3JrIGVkaXRpb24gb3Igc291cmNlIGNoYW5nZWQuIFByZXNlcnZlIHRoaXMgY2hlY2twb2ludCBhbmQgc3RhcnQgYSBuZXcgY2FzZS4nKTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgICAgIGlmICghdmFsaWRDb3ZlcmFnZVBsYW5Gb3JTY29wZSgpIHx8IGNvdmVyYWdlUGxhbj8uc291cmNlX2RpZ2VzdCAhPT0gYXV0aG9yaXplZEZyYW1ld29ya1NvdXJjZT8uc291cmNlX2RpZ2VzdCkge1xuICAgICAgICAgICAgICAgIGRyYWZ0ZWRDYXNlTm90aWNlID0gJ0xvYWRpbmcgdGhlIGF1dGhvcml6ZWQgZnJhbWV3b3JrIGdlbmVyYXRpb24gcGxhbi4nO1xuICAgICAgICAgICAgICAgIGF3YWl0IGxvYWRTaWNvQ292ZXJhZ2VQbGFuKCk7XG4gICAgICAgICAgICB9XG4gICAgICAgICAgICB3aGlsZSAoIXN0b3BBZnRlclBoYXNlICYmIHF1YWxpdHlTY29wZUtleSgpID09PSBkcmFmdGVkQ2FzZVNjb3BlKSB7XG4gICAgICAgICAgICAgICAgY29uc3Qgc2xvdCA9IG5leHRRdWFsaXR5U2xvdCgpO1xuICAgICAgICAgICAgICAgIGlmICghc2xvdCkgeyBkcmFmdGVkQ2FzZU5vdGljZSA9ICdBbGwgc2NoZWR1bGVkIFF3ZW4gZHJhZnRzIGFyZSByZWFkeSBmb3IgcmV2aWV3LiBFdmlkZW5jZSwgcmlzayByYXRpbmdzIGFuZCBhcHByb3ZhbHMgcmVtYWluIHBlbmRpbmc7IHRoZSBHUkMgY2FzZSBpcyBub3QgY29tcGxldGUuJzsgYnJlYWs7IH1cbiAgICAgICAgICAgICAgICBjdXJyZW50R2VuZXJhdGluZ0FjdGl2aXR5ID0gc2xvdC5zdGVwO1xuICAgICAgICAgICAgICAgIGNvbnN0IHByZXZpb3VzID0gcGxhbm5lZERyYWZ0Q29udGV4dChzbG90LnBsYW5uZWQsIHF1YWxpdHlEcmFmdHMpO1xuICAgICAgICAgICAgICAgIC8vIE9ubHkgYSBzb3VyY2UtYmFja2VkIFNJQ08gcmVmZXJlbmNlIGlzIHNlbGVjdGVkOyB0aGUgYmFja2VuZFxuICAgICAgICAgICAgICAgIC8vIGluZGVwZW5kZW50bHkgcmVjaGVja3MgYXV0aG9yaXphdGlvbiBiZWZvcmUgdXNpbmcgaXQuXG4gICAgICAgICAgICAgICAgY29uc3QgY2hvc2VuUmVmID0gc2xvdC5zdGVwID09PSAxMCA/IHNsb3QucGxhbm5lZC5mb2N1c19yZXF1aXJlbWVudF9yZWZlcmVuY2UgOiAnJztcbiAgICAgICAgICAgICAgICBjb25zdCBrZXkgPSBzbG90QXR0ZW1wdEtleShzbG90LnN0ZXAsIHNsb3QuaW5kZXgpO1xuICAgICAgICAgICAgICAgIC8vIE9ubHkgb25lIG1vZGVsIHJlcXVlc3QgcGVyIGFjdGl2aXR5IHNsb3QgcGVyIHJ1bi4gQSByZWplY3RlZFxuICAgICAgICAgICAgICAgIC8vIHJlc3BvbnNlIGlzIHZpc2libGUgaW1tZWRpYXRlbHk7IFJlc3VtZSByb3RhdGVzIHRoZSBmb2N1cy5cbiAgICAgICAgICAgICAgICBjb25zdCBhdHRlbXB0ID0gTWF0aC5taW4oMzAsIG5leHRBdHRlbXB0QnlTbG90W2tleV0gPz8gMCk7XG4gICAgICAgICAgICAgICAgY29uc3Qgc3RhcnRlZCA9IERhdGUubm93KCk7XG4gICAgICAgICAgICAgICAgZHJhZnRlZENhc2VOb3RpY2UgPSBgR2VuZXJhdGluZyBhY3Rpdml0eSAke3Nsb3Quc3RlcH0gb2YgMTYsIGRyYWZ0ICR7c2xvdC5pbmRleH0uIE9uZSByZXF1ZXN0IGF0IGEgdGltZTsgYWNjZXB0ZWQgZHJhZnRzIGFyZSBwcmVzZXJ2ZWQuYDtcbiAgICAgICAgICAgICAgICB0cnkge1xuICAgICAgICAgICAgICAgICAgICBjb25zdCByZXNwb25zZSA9IGF3YWl0IHNpY29Qb3N0QWN0aW9uKCdxdWFsaXR5X2RyYWZ0X29uZScsIHtcbiAgICAgICAgICAgICAgICAgICAgICAgIG9yZ2FuaXphdGlvbl9uYW1lOiBvcmdhbml6YXRpb24udHJpbSgpLCBmcmFtZXdvcmtfbmFtZTogZnJhbWV3b3JrU2VhcmNoLnRyaW0oKSxcbiAgICAgICAgICAgICAgICAgICAgICAgIHByb2JsZW06IGluc3RydWN0aW9uLnRyaW0oKSwgYWN0aXZpdHlfbnVtYmVyOiBTdHJpbmcoc2xvdC5zdGVwKSxcbiAgICAgICAgICAgICAgICAgICAgICAgIGRyYWZ0X2luZGV4OiBTdHJpbmcoc2xvdC5pbmRleCksIHNvdXJjZV9kaWdlc3Q6IFN0cmluZyhhdXRob3JpemVkRnJhbWV3b3JrU291cmNlPy5zb3VyY2VfZGlnZXN0ID8/ICcnKSxcbiAgICAgICAgICAgICAgICAgICAgICAgIHJlcXVpcmVtZW50X3JlZmVyZW5jZTogY2hvc2VuUmVmLCBwcmV2aW91c19kcmFmdHM6IEpTT04uc3RyaW5naWZ5KHByZXZpb3VzKSxcbiAgICAgICAgICAgICAgICAgICAgICAgIGZvY3VzX3JlcXVpcmVtZW50X3JlZmVyZW5jZTogc2xvdC5wbGFubmVkLmZvY3VzX3JlcXVpcmVtZW50X3JlZmVyZW5jZSxcbiAgICAgICAgICAgICAgICAgICAgICAgIGZvY3VzX3RoZW1lOiBzbG90LnBsYW5uZWQudGhlbWUsXG4gICAgICAgICAgICAgICAgICAgICAgICBmb2N1c19hdHRlbXB0OiBTdHJpbmcoYXR0ZW1wdClcbiAgICAgICAgICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICAgICAgICAgIGNvbnN0IGl0ZW0gPSAocmVzcG9uc2UuZGF0YSBhcyBSZWNvcmQ8c3RyaW5nLCBhbnk+KT8ucXVhbGl0eV9kcmFmdF9vbmU7XG4gICAgICAgICAgICAgICAgICAgIGlmICghaXRlbSB8fCBpdGVtLnF1YWxpdHlfY29udHJhY3RfY2hlY2tlZCAhPT0gdHJ1ZSB8fCBpdGVtLmJ1c2luZXNzX3JlY29yZHNfd3JpdHRlbiAhPT0gZmFsc2UgfHxcbiAgICAgICAgICAgICAgICAgICAgICAgIGl0ZW0uYWN0aXZpdHlfbnVtYmVyICE9PSBzbG90LnN0ZXAgfHwgIWl0ZW0uZHJhZnQ/LmRyYWZ0X3JlZmVyZW5jZSB8fFxuICAgICAgICAgICAgICAgICAgICAgICAgaXRlbS5kcmFmdC5kcmFmdF9yZWZlcmVuY2UgIT09IGtleSkge1xuICAgICAgICAgICAgICAgICAgICAgICAgdGhyb3cgbmV3IEVycm9yKCdUaGUgZ2VuZXJhdGVkIGRyYWZ0IGZhaWxlZCB2YWxpZGF0aW9uOyBwcmV2aW91cyBkcmFmdHMgYXJlIHByZXNlcnZlZC4nKTtcbiAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgICAgICBjb25zdCBlbGFwc2VkID0gTWF0aC5yb3VuZCgoRGF0ZS5ub3coKSAtIHN0YXJ0ZWQpIC8gMTAwMCk7XG4gICAgICAgICAgICAgICAgICAgIG5leHRBdHRlbXB0QnlTbG90ID0geyAuLi5uZXh0QXR0ZW1wdEJ5U2xvdCwgW2tleV06IE1hdGgubWluKDMwLCBhdHRlbXB0ICsgMSkgfTtcbiAgICAgICAgICAgICAgICAgICAgcmVjb3JkRHJhZnRBdHRlbXB0KHNsb3Quc3RlcCwgc2xvdC5pbmRleCwgZWxhcHNlZCwgJ2FjY2VwdGVkJywgJ0RyYWZ0IHZhbGlkYXRlZCcpO1xuICAgICAgICAgICAgICAgICAgICBxdWFsaXR5RHJhZnRzID0gWy4uLnF1YWxpdHlEcmFmdHMsIGl0ZW1dO1xuICAgICAgICAgICAgICAgICAgICBkcmFmdGVkQ2FzZU5vdGljZSA9IGBHZW5lcmF0ZWQgJHtxdWFsaXR5RHJhZnRzLmZpbHRlcihyID0+IHIucHJvdmVuYW5jZSA9PT0gJ3F3ZW5fcXVhbGl0eV9zaW5nbGVfYXV0aGVudGljYXRlZF92NycpLmxlbmd0aH0gbmV3IHF1YWxpdHktY2hlY2tlZCBkcmFmdHMuIExhc3QgcmVxdWVzdDogJHtlbGFwc2VkfXMuIFNvdXJjZTogJHthdXRob3JpemVkU291cmNlUm93cy5sZW5ndGh9IGF1dGhvcml6ZWQgcmVxdWlyZW1lbnRzLiBObyByZWNvcmRzIHNhdmVkLmA7XG4gICAgICAgICAgICAgICAgICAgIHNhdmVMb2NhbERyYWZ0Q2hlY2twb2ludCgpO1xuICAgICAgICAgICAgICAgIH0gY2F0Y2ggKGVycm9yKSB7XG4gICAgICAgICAgICAgICAgICAgIGNvbnN0IGVsYXBzZWQgPSBNYXRoLnJvdW5kKChEYXRlLm5vdygpIC0gc3RhcnRlZCkgLyAxMDAwKTtcbiAgICAgICAgICAgICAgICAgICAgY29uc3QgbWVzc2FnZSA9IGVycm9yIGluc3RhbmNlb2YgRXJyb3IgPyBlcnJvci5tZXNzYWdlIDogJ0RyYWZ0IGdlbmVyYXRpb24gcmVxdWVzdCBmYWlsZWQuJztcbiAgICAgICAgICAgICAgICAgICAgbmV4dEF0dGVtcHRCeVNsb3QgPSB7IC4uLm5leHRBdHRlbXB0QnlTbG90LCBba2V5XTogTWF0aC5taW4oMzAsIGF0dGVtcHQgKyAxKSB9O1xuICAgICAgICAgICAgICAgICAgICByZWNvcmREcmFmdEF0dGVtcHQoc2xvdC5zdGVwLCBzbG90LmluZGV4LCBlbGFwc2VkLCAncmVqZWN0ZWQnLCBtZXNzYWdlKTtcbiAgICAgICAgICAgICAgICAgICAgcXVhbGl0eUlzc3VlcyA9IFsuLi5xdWFsaXR5SXNzdWVzLnNsaWNlKC0yOSksIGBBY3Rpdml0eSAke3Nsb3Quc3RlcH06ICR7bWVzc2FnZX0gKCR7ZWxhcHNlZH1zKWBdO1xuICAgICAgICAgICAgICAgICAgICBkcmFmdGVkQ2FzZUVycm9yID0gYEFjdGl2aXR5ICR7c2xvdC5zdGVwfSB3YXMgbm90IGFjY2VwdGVkIGFmdGVyICR7ZWxhcHNlZH1zLiAke21lc3NhZ2V9IFRoZSBuZXh0IFJlc3VtZSB3aWxsIHRyeSBhIGRpZmZlcmVudCBmb2N1czsgcHJldmlvdXMgZHJhZnRzIGFyZSBwcmVzZXJ2ZWQuYDtcbiAgICAgICAgICAgICAgICAgICAgc2F2ZUxvY2FsRHJhZnRDaGVja3BvaW50KCk7XG4gICAgICAgICAgICAgICAgICAgIGJyZWFrO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgIH1cbiAgICAgICAgfSBjYXRjaCAoZXJyb3IpIHtcbiAgICAgICAgICAgIGRyYWZ0ZWRDYXNlRXJyb3IgPSBlcnJvciBpbnN0YW5jZW9mIEVycm9yID8gZXJyb3IubWVzc2FnZSA6ICdHZW5lcmF0aW9uIGZhaWxlZDsgcHJldmlvdXMgZHJhZnRzIHJlbWFpbi4nO1xuICAgICAgICB9IGZpbmFsbHkgeyBkcmFmdGVkQ2FzZUJ1c3kgPSBmYWxzZTsgY3VycmVudEdlbmVyYXRpbmdBY3Rpdml0eSA9IDA7IHNhdmVMb2NhbERyYWZ0Q2hlY2twb2ludCgpOyB9XG4gICAgfVxuXG4gICAgZnVuY3Rpb24gZG93bmxvYWRBdXRob3JpemVkUmVxdWlyZW1lbnRTb3VyY2UoKSB7XG4gICAgICAgIGlmICghYXV0aG9yaXplZEZyYW1ld29ya1NvdXJjZT8uY29tcGxldGVfc291cmNlX3NuYXBzaG90IHx8ICFhdXRob3JpemVkU291cmNlUm93cy5sZW5ndGgpIHJldHVybjtcbiAgICAgICAgY29uc3QgcGF5bG9hZCA9IHtcbiAgICAgICAgICAgIHNjaGVtYTogJ3NpY28tdXNlci1leHBvcnRlZC1hdXRob3JpemVkLWZyYW1ld29yay1yZXF1aXJlbWVudHMtdjEnLFxuICAgICAgICAgICAgc291cmNlX3N0YXR1czogJ3JlYWRfZnJvbV9TSUNPX3VuZGVyX2N1cnJlbnRfbG9nZ2VkX2luX3VzZXInLFxuICAgICAgICAgICAgc291cmNlOiBhdXRob3JpemVkRnJhbWV3b3JrU291cmNlLFxuICAgICAgICAgICAgcmVxdWlyZW1lbnRzOiBhdXRob3JpemVkU291cmNlUm93cyxcbiAgICAgICAgICAgIG9mZmljaWFsX2VkaXRpb25faW5kZXBlbmRlbnRseV92ZXJpZmllZDogZmFsc2UsXG4gICAgICAgICAgICBjb21wbGlhbmNlX2Fzc2Vzc21lbnRfY29tcGxldGVkOiBmYWxzZSxcbiAgICAgICAgICAgIGJ1c2luZXNzX3JlY29yZHNfd3JpdHRlbjogZmFsc2VcbiAgICAgICAgfTtcbiAgICAgICAgY29uc3QgdXJsID0gVVJMLmNyZWF0ZU9iamVjdFVSTChuZXcgQmxvYihbSlNPTi5zdHJpbmdpZnkocGF5bG9hZCwgbnVsbCwgMildLCB7IHR5cGU6ICdhcHBsaWNhdGlvbi9qc29uJyB9KSk7XG4gICAgICAgIHRyeSB7XG4gICAgICAgICAgICBjb25zdCBhID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgnYScpO1xuICAgICAgICAgICAgYS5ocmVmID0gdXJsOyBhLmRvd25sb2FkID0gJ1NJQ08tYXV0aG9yaXplZC1mcmFtZXdvcmstc291cmNlLVJFQUQtT05MWS5qc29uJzsgYS5jbGljaygpO1xuICAgICAgICB9IGZpbmFsbHkgeyBVUkwucmV2b2tlT2JqZWN0VVJMKHVybCk7IH1cbiAgICB9XG5cbiAgICBmdW5jdGlvbiBkb3dubG9hZENhc2VEcmFmdCgpIHtcbiAgICAgICAgaWYgKCFkcmFmdGVkQ2FzZVN0YWdlcy5sZW5ndGgpIHJldHVybjtcbiAgICAgICAgY29uc3QgY2FzZURyYWZ0ID0ge1xuICAgICAgICAgICAgc2NoZW1hOiAnc2ljby11bnNhdmVkLWNhc2UtZHJhZnRzLXYxJywgb3JnYW5pemF0aW9uX25hbWU6IG9yZ2FuaXphdGlvbi50cmltKCksXG4gICAgICAgICAgICBmcmFtZXdvcmtfbmFtZTogZnJhbWV3b3JrU2VhcmNoLnRyaW0oKSwgb2JqZWN0aXZlOiBpbnN0cnVjdGlvbi50cmltKCksXG4gICAgICAgICAgICBnZW5lcmF0ZWRfYWN0aXZpdHlfY291bnQ6IGRyYWZ0ZWRDYXNlU3RhZ2VzLmxlbmd0aCxcbiAgICAgICAgICAgIGF1dGhvcml6ZWRfZnJhbWV3b3JrX3NvdXJjZTogYXV0aG9yaXplZEZyYW1ld29ya1NvdXJjZSxcbiAgICAgICAgICAgIGF1dGhvcml6ZWRfcmVxdWlyZW1lbnRzOiBhdXRob3JpemVkRnJhbWV3b3JrU291cmNlPy5jb21wbGV0ZV9zb3VyY2Vfc25hcHNob3QgPyBhdXRob3JpemVkU291cmNlUm93cyA6IFtdLFxuICAgICAgICAgICAgYXV0aG9yaXplZF9yZXF1aXJlbWVudHNfbm90X2NvbXBsaWFuY2VfdmVyZGljdDogdHJ1ZSxcbiAgICAgICAgICAgIGJ1c2luZXNzX3JlY29yZHNfd3JpdHRlbjogZmFsc2UsXG4gICAgICAgICAgICBub3RlOiAnVW52ZXJpZmllZCBoeXBvdGhldGljYWwgZHJhZnRzLiBObyBHUkMgZGF0YWJhc2UgcmVjb3JkcyBjcmVhdGVkLicsXG4gICAgICAgICAgICBhY3Rpdml0aWVzOiBkcmFmdGVkQ2FzZVN0YWdlc1xuICAgICAgICB9O1xuICAgICAgICBjb25zdCB1cmwgPSBVUkwuY3JlYXRlT2JqZWN0VVJMKG5ldyBCbG9iKFtKU09OLnN0cmluZ2lmeShjYXNlRHJhZnQsIG51bGwsIDIpXSwgeyB0eXBlOiAnYXBwbGljYXRpb24vanNvbicgfSkpO1xuICAgICAgICB0cnkge1xuICAgICAgICAgICAgY29uc3QgYSA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoJ2EnKTtcbiAgICAgICAgICAgIGEuaHJlZiA9IHVybDsgYS5kb3dubG9hZCA9ICdTSUNPLW5ldy1HUkMtY2FzZS1EUkFGVC5qc29uJzsgYS5jbGljaygpO1xuICAgICAgICB9IGZpbmFsbHkgeyBVUkwucmV2b2tlT2JqZWN0VVJMKHVybCk7IH1cbiAgICB9XG5cbiAgICBsZXQgY3JlYXRpb25CdXN5ID0gJHN0YXRlKGZhbHNlKTtcbiAgICBsZXQgY3JlYXRpb25FcnJvciA9ICRzdGF0ZSgnJyk7XG4gICAgbGV0IGNyZWF0aW9uTm90aWNlID0gJHN0YXRlKCcnKTtcbiAgICBsZXQgY3JlYXRpb25DaG9pY2VzID0gJHN0YXRlPFJlY29yZDxzdHJpbmcsIGFueT4gfCBudWxsPihudWxsKTtcbiAgICBsZXQgY29uZmlybUNhc2VDcmVhdGlvbiA9ICRzdGF0ZShmYWxzZSk7XG4gICAgbGV0IGNhc2VTYXZlZCA9ICRzdGF0ZShmYWxzZSk7XG4gICAgbGV0IHN0YWdlQnVzeSA9ICRzdGF0ZShmYWxzZSk7XG4gICAgbGV0IHN0YWdlTm90aWNlID0gJHN0YXRlKCcnKTtcbiAgICBsZXQgc3RhZ2VFcnJvciA9ICRzdGF0ZSgnJyk7XG4gICAgbGV0IHN0YWdlQ29uZmlybWVkID0gJHN0YXRlKGZhbHNlKTtcbiAgICBsZXQgc3RhZ2VIdW1hbkZhY3RzID0gJHN0YXRlKCcnKTtcbiAgICBsZXQgZnJhbWV3b3JrQnVzaW5lc3NDb250ZXh0ID0gJHN0YXRlKCcnKTtcbiAgICBsZXQgZnJhbWV3b3JrQmF0Y2hTaXplID0gJHN0YXRlKDIpO1xuICAgIGxldCBmdWxsUmV2aWV3ID0gJHN0YXRlPFJldmlld0NoZWNrcG9pbnQgfCBudWxsPihudWxsKTtcbiAgICBsZXQgZnVsbFJldmlld0J1c3kgPSAkc3RhdGUoZmFsc2UpO1xuICAgIGxldCBmdWxsUmV2aWV3QXV0b21hdGljID0gJHN0YXRlKGZhbHNlKTtcbiAgICBsZXQgZnVsbFJldmlld1BhdXNlID0gJHN0YXRlKGZhbHNlKTtcbiAgICBsZXQgZnVsbFJldmlld0Vycm9yID0gJHN0YXRlKCcnKTtcbiAgICBsZXQgZnVsbFJldmlld05vdGljZSA9ICRzdGF0ZSgnJyk7XG4gICAgbGV0IGZ1bGxSZXZpZXdDYW5kaWRhdGVzID0gJHN0YXRlPHN0cmluZ1tdPihbXSk7XG4gICAgbGV0IGZ1bGxSZXZpZXdTaG93biA9ICRzdGF0ZSg4KTtcbiAgICBjb25zdCBmdWxsUmV2aWV3UGVyY2VudCA9ICRkZXJpdmVkKGZ1bGxSZXZpZXc/LmNvdmVyYWdlLmFjY2Vzc2libGVfdG90YWxcbiAgICAgICAgPyBNYXRoLnJvdW5kKGZ1bGxSZXZpZXcuY292ZXJhZ2UucmV2aWV3ZWRfdGhyb3VnaCAqIDEwMDAwIC8gZnVsbFJldmlldy5jb3ZlcmFnZS5hY2Nlc3NpYmxlX3RvdGFsKSAvIDEwMCA6IDApO1xuICAgIGNvbnN0IHZpc2libGVGcmFtZXdvcmtSZXZpZXdzID0gJGRlcml2ZWQoZnVsbFJldmlldz8ucmVxdWlyZW1lbnRfcmV2aWV3cy5zbGljZSgwLCBmdWxsUmV2aWV3U2hvd24pID8/IFtdKTtcblxuICAgIGZ1bmN0aW9uIGN1cnJlbnRGcmFtZXdvcmtTY29wZSgpOiBSZXZpZXdTY29wZSB7XG4gICAgICAgIHJldHVybiB7XG4gICAgICAgICAgICBvcmdhbml6YXRpb25fbmFtZTogb3JnYW5pemF0aW9uLnRyaW0oKSwgZnJhbWV3b3JrX25hbWU6IGZyYW1ld29ya1NlYXJjaC50cmltKCksXG4gICAgICAgICAgICBwcm9ibGVtOiBpbnN0cnVjdGlvbi50cmltKCksIGJ1c2luZXNzX2NvbnRleHQ6IGZyYW1ld29ya0J1c2luZXNzQ29udGV4dC50cmltKClcbiAgICAgICAgfTtcbiAgICB9XG5cbiAgICBmdW5jdGlvbiBjaGFuZ2VkRnJhbWV3b3JrSW5wdXRzKCkge1xuICAgICAgICAvLyBBIHJ1bm5pbmcgbW9kZWwgcmVxdWVzdCBpcyBhbGxvd2VkIHRvIGZpbmlzaCwgYnV0IGxhdGVyIGJhdGNoZXMgd2lsbFxuICAgICAgICAvLyBub3Qgc2lsZW50bHkgbWl4IHVwZGF0ZWQgaW5wdXRzIHdpdGggYW4gZWFybGllciBzaWduZWQgY3Vyc29yLlxuICAgICAgICBmdWxsUmV2aWV3UGF1c2UgPSB0cnVlO1xuICAgICAgICBpZiAoZnVsbFJldmlldykgZnVsbFJldmlld05vdGljZSA9ICdJbnB1dHMgY2hhbmdlZC4gUmVzdG9yZSB0aGUgb3JpZ2luYWwgaW5wdXRzIHRvIHJlc3VtZSwgb3IgZXhwbGljaXRseSBzdGFydCBhIG5ldyByZXZpZXcuJztcbiAgICB9XG5cbiAgICBhc3luYyBmdW5jdGlvbiBydW5GdWxsRnJhbWV3b3JrUmV2aWV3KGF1dG9tYXRpYzogYm9vbGVhbiwgcmVzdGFydCA9IGZhbHNlKSB7XG4gICAgICAgIGlmIChmdWxsUmV2aWV3QnVzeSkgcmV0dXJuO1xuICAgICAgICBjb25zdCBzY29wZSA9IGN1cnJlbnRGcmFtZXdvcmtTY29wZSgpO1xuICAgICAgICBpZiAoc2NvcGUub3JnYW5pemF0aW9uX25hbWUubGVuZ3RoIDwgMiB8fCBzY29wZS5vcmdhbml6YXRpb25fbmFtZS5sZW5ndGggPiAxNTAgfHxcbiAgICAgICAgICAgIHNjb3BlLmZyYW1ld29ya19uYW1lLmxlbmd0aCA8IDIgfHwgc2NvcGUuZnJhbWV3b3JrX25hbWUubGVuZ3RoID4gMTUwIHx8XG4gICAgICAgICAgICBzY29wZS5wcm9ibGVtLmxlbmd0aCA8IDIwIHx8IHNjb3BlLnByb2JsZW0ubGVuZ3RoID4gNDAwMCB8fFxuICAgICAgICAgICAgc2NvcGUuYnVzaW5lc3NfY29udGV4dC5sZW5ndGggPiAxMjAwKSB7XG4gICAgICAgICAgICBmdWxsUmV2aWV3RXJyb3IgPSAnRW50ZXIgdGhlIG9yZ2FuaXphdGlvbiwgZXhhY3QgZnJhbWV3b3JrIGFuZCBhc3Nlc3NtZW50IG9iamVjdGl2ZSBpbiB0aGUgdGhyZWUgZmllbGRzIGFib3ZlLic7XG4gICAgICAgICAgICByZXR1cm47XG4gICAgICAgIH1cbiAgICAgICAgaWYgKHJlc3RhcnQpIHtcbiAgICAgICAgICAgIGZ1bGxSZXZpZXcgPSBudWxsO1xuICAgICAgICAgICAgZnVsbFJldmlld0NhbmRpZGF0ZXMgPSBbXTtcbiAgICAgICAgICAgIGZ1bGxSZXZpZXdTaG93biA9IDg7XG4gICAgICAgIH0gZWxzZSBpZiAoZnVsbFJldmlldyAmJiBzY29wZUtleShmdWxsUmV2aWV3LnNjb3BlKSAhPT0gc2NvcGVLZXkoc2NvcGUpKSB7XG4gICAgICAgICAgICBmdWxsUmV2aWV3RXJyb3IgPSAnVGhlc2UgaW5wdXRzIGRpZmZlciBmcm9tIHRoZSBleGlzdGluZyBjaGVja3BvaW50LiBSZXN0b3JlIHRoZW0sIG9yIGNsaWNrIFN0YXJ0IG5ldyByZXZpZXcuJztcbiAgICAgICAgICAgIHJldHVybjtcbiAgICAgICAgfVxuICAgICAgICBpZiAoZnVsbFJldmlldz8uY292ZXJhZ2UuY29tcGxldGUpIHJldHVybjtcbiAgICAgICAgZnVsbFJldmlld0J1c3kgPSB0cnVlO1xuICAgICAgICBmdWxsUmV2aWV3QXV0b21hdGljID0gYXV0b21hdGljO1xuICAgICAgICBmdWxsUmV2aWV3UGF1c2UgPSBmYWxzZTtcbiAgICAgICAgZnVsbFJldmlld0Vycm9yID0gJyc7XG4gICAgICAgIGZ1bGxSZXZpZXdOb3RpY2UgPSAnJztcbiAgICAgICAgdHJ5IHtcbiAgICAgICAgICAgIGRvIHtcbiAgICAgICAgICAgICAgICBpZiAoZnVsbFJldmlld1BhdXNlIHx8IHNjb3BlS2V5KGN1cnJlbnRGcmFtZXdvcmtTY29wZSgpKSAhPT0gc2NvcGVLZXkoc2NvcGUpKSBicmVhaztcbiAgICAgICAgICAgICAgICBjb25zdCByZXN1bHQgPSBhd2FpdCBzaWNvUG9zdEFjdGlvbignYWlfZnJhbWV3b3JrX2JhdGNoJywge1xuICAgICAgICAgICAgICAgICAgICBvcmdhbml6YXRpb25fbmFtZTogc2NvcGUub3JnYW5pemF0aW9uX25hbWUsXG4gICAgICAgICAgICAgICAgICAgIGZyYW1ld29ya19uYW1lOiBzY29wZS5mcmFtZXdvcmtfbmFtZSxcbiAgICAgICAgICAgICAgICAgICAgcHJvYmxlbTogc2NvcGUucHJvYmxlbSxcbiAgICAgICAgICAgICAgICAgICAgZnJhbWV3b3JrX2J1c2luZXNzX2NvbnRleHQ6IHNjb3BlLmJ1c2luZXNzX2NvbnRleHQsXG4gICAgICAgICAgICAgICAgICAgIGZyYW1ld29ya19iYXRjaF9zaXplOiBTdHJpbmcoZnJhbWV3b3JrQmF0Y2hTaXplKSxcbiAgICAgICAgICAgICAgICAgICAgZnJhbWV3b3JrX2N1cnNvcjogZnVsbFJldmlldz8ubmV4dF9jdXJzb3IgPz8gJydcbiAgICAgICAgICAgICAgICB9KTtcbiAgICAgICAgICAgICAgICBjb25zdCByZXNwb25zZSA9IChyZXN1bHQuZGF0YSBhcyBSZWNvcmQ8c3RyaW5nLCBhbnk+KT8uYWlfZnJhbWV3b3JrX2JhdGNoO1xuICAgICAgICAgICAgICAgIGNvbnN0IGJhdGNoID0gcmVzcG9uc2U/LmZyYW1ld29ya19iYXRjaDtcbiAgICAgICAgICAgICAgICBpZiAoIWJhdGNoKSB0aHJvdyBuZXcgRXJyb3IoJ05vIGZyYW1ld29yayByZXZpZXcgd2FzIHJldHVybmVkLicpO1xuICAgICAgICAgICAgICAgIGlmIChiYXRjaC5zdGF0dXMgIT09ICdwYXJ0aWFsJyAmJiBiYXRjaC5zdGF0dXMgIT09ICdjb21wbGV0ZScpIHtcbiAgICAgICAgICAgICAgICAgICAgZnVsbFJldmlld0NhbmRpZGF0ZXMgPSBBcnJheS5pc0FycmF5KGJhdGNoLmNhbmRpZGF0ZV9mcmFtZXdvcmtzKVxuICAgICAgICAgICAgICAgICAgICAgICAgPyBiYXRjaC5jYW5kaWRhdGVfZnJhbWV3b3Jrcy5tYXAoU3RyaW5nKS5zbGljZSgwLCA4KSA6IFtdO1xuICAgICAgICAgICAgICAgICAgICB0aHJvdyBuZXcgRXJyb3IoJ0FuIGV4YWN0IGF1dGhvcml6ZWQgZnJhbWV3b3JrIGFuZCBhY2Nlc3NpYmxlIHJlcXVpcmVtZW50IGxpc3QgY291bGQgbm90IGJlIGZvdW5kLiBDaGVjayB0aGUgbmFtZSBhbmQgZWRpdGlvbi4nKTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgaWYgKHNjb3BlS2V5KGN1cnJlbnRGcmFtZXdvcmtTY29wZSgpKSAhPT0gc2NvcGVLZXkoc2NvcGUpKSB7XG4gICAgICAgICAgICAgICAgICAgIHRocm93IG5ldyBFcnJvcignSW5wdXRzIGNoYW5nZWQgZHVyaW5nIGdlbmVyYXRpb24uIFRoaXMgYmF0Y2ggd2FzIG5vdCBhcHBlbmRlZC4gUmV0dXJuIHRvIHRoZSBvcmlnaW5hbCBpbnB1dHMgYW5kIHJldHJ5LicpO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICBmdWxsUmV2aWV3ID0gYXBwbHlGcmFtZXdvcmtCYXRjaChmdWxsUmV2aWV3LCBzY29wZSwgYmF0Y2gpO1xuICAgICAgICAgICAgfSB3aGlsZSAoYXV0b21hdGljICYmICFmdWxsUmV2aWV3UGF1c2UgJiYgIWZ1bGxSZXZpZXc/LmNvdmVyYWdlLmNvbXBsZXRlKTtcbiAgICAgICAgICAgIGlmIChmdWxsUmV2aWV3Py5jb3ZlcmFnZS5jb21wbGV0ZSkge1xuICAgICAgICAgICAgICAgIGZ1bGxSZXZpZXdOb3RpY2UgPSAnQWxsIGFjY2Vzc2libGUgYXNzZXNzYWJsZSByZXF1aXJlbWVudHMgaGF2ZSBwcm92aXNpb25hbCByZXZpZXdzLiBFeHBvcnQgdGhlIGNoZWNrcG9pbnQgYW5kIGFycmFuZ2UgZXZpZGVuY2UtYmFzZWQgaHVtYW4gdmVyaWZpY2F0aW9uLic7XG4gICAgICAgICAgICB9IGVsc2UgaWYgKGZ1bGxSZXZpZXdQYXVzZSkge1xuICAgICAgICAgICAgICAgIGZ1bGxSZXZpZXdOb3RpY2UgPSAnUGF1c2VkIGFmdGVyIHRoZSBjdXJyZW50IGJhdGNoLiBFeHBvcnQgdGhlIGNoZWNrcG9pbnQgYmVmb3JlIHJlZnJlc2hpbmcgdGhlIHBhZ2UuJztcbiAgICAgICAgICAgIH0gZWxzZSBpZiAoZnVsbFJldmlldykge1xuICAgICAgICAgICAgICAgIGZ1bGxSZXZpZXdOb3RpY2UgPSAnQmF0Y2ggY29tcGxldGVkLiBDb250aW51ZSB3aGVuIHJlYWR5LCBvciBleHBvcnQgYSBjaGVja3BvaW50Lic7XG4gICAgICAgICAgICB9XG4gICAgICAgIH0gY2F0Y2ggKGVycm9yKSB7XG4gICAgICAgICAgICBmdWxsUmV2aWV3RXJyb3IgPSBlcnJvciBpbnN0YW5jZW9mIEVycm9yID8gZXJyb3IubWVzc2FnZSA6ICdUaGUgY3VycmVudCBnZW5lcmF0aW9uIGJhdGNoIGZhaWxlZC4gRWFybGllciByZXZpZXdzIGFyZSBwcmVzZXJ2ZWQuJztcbiAgICAgICAgfSBmaW5hbGx5IHtcbiAgICAgICAgICAgIGZ1bGxSZXZpZXdCdXN5ID0gZmFsc2U7XG4gICAgICAgICAgICBmdWxsUmV2aWV3QXV0b21hdGljID0gZmFsc2U7XG4gICAgICAgIH1cbiAgICB9XG5cblxuICAgIGFzeW5jIGZ1bmN0aW9uIHByZXBhcmVOZXdHcmNDYXNlKCkge1xuICAgICAgICBpZiAoY3JlYXRpb25CdXN5IHx8IHByZXBhcmVkV29ya2Zsb3cgfHwgY2FzZVNhdmVkKSByZXR1cm47XG4gICAgICAgIGlmIChvcmdhbml6YXRpb24udHJpbSgpLmxlbmd0aCA8IDIgfHwgZnJhbWV3b3JrU2VhcmNoLnRyaW0oKS5sZW5ndGggPCAyIHx8IGluc3RydWN0aW9uLnRyaW0oKS5sZW5ndGggPCAyMCkge1xuICAgICAgICAgICAgY3JlYXRpb25FcnJvciA9ICdFbnRlciBhbiBvcmdhbml6YXRpb24sIGV4YWN0IGxvYWRlZCBmcmFtZXdvcmsgYW5kIG9iamVjdGl2ZSBvZiBhdCBsZWFzdCAyMCBjaGFyYWN0ZXJzLic7XG4gICAgICAgICAgICByZXR1cm47XG4gICAgICAgIH1cbiAgICAgICAgY3JlYXRpb25CdXN5ID0gdHJ1ZTtcbiAgICAgICAgY3JlYXRpb25FcnJvciA9ICcnO1xuICAgICAgICBjcmVhdGlvbk5vdGljZSA9ICcnO1xuICAgICAgICB0cnkge1xuICAgICAgICAgICAgLy8gVGhpcyBhbHJlYWR5IGV4aXN0cyBpbiArcGFnZS5zZXJ2ZXIudHMgYW5kIGludm9rZXMgdGhlIGF1dGhlbnRpY2F0ZWQsXG4gICAgICAgICAgICAvLyBwZXJtaXNzaW9uLWNoZWNrZWQgRGphbmdvIGxpZmVjeWNsZSBpbnRha2UuIE5vIHBhcmFsbGVsIEdSQyB3cml0ZXIuXG4gICAgICAgICAgICBjb25zdCByZXNwb25zZSA9IGF3YWl0IHNpY29Qb3N0QWN0aW9uKCdsaWZlY3ljbGVfaW50YWtlJywge1xuICAgICAgICAgICAgICAgIG9yZ2FuaXphdGlvbl9uYW1lOiBvcmdhbml6YXRpb24udHJpbSgpLFxuICAgICAgICAgICAgICAgIGZyYW1ld29ya19uYW1lOiBmcmFtZXdvcmtTZWFyY2gudHJpbSgpLFxuICAgICAgICAgICAgICAgIHByb2JsZW06IGluc3RydWN0aW9uLnRyaW0oKSxcbiAgICAgICAgICAgICAgICBza2lwX2xlZ2FjeV9nZW5lcmF0aW9uOiAneWVzJyxcbiAgICAgICAgICAgICAgICBzZWxlY3RlZF9mcmFtZXdvcmtfaWQ6IGZyYW1ld29ya0NvbmZpcm1hdGlvbixcbiAgICAgICAgICAgICAgICBzZWxlY3RlZF9vcmdhbml6YXRpb25faWQ6IG9yZ2FuaXphdGlvbkNvbmZpcm1hdGlvblxuICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICBjb25zdCBkYXRhID0gcmVzcG9uc2UuZGF0YSBhcyBSZWNvcmQ8c3RyaW5nLCBhbnk+O1xuICAgICAgICAgICAgaWYgKGRhdGE/LmxpZmVjeWNsZV9jaG9pY2VzKSB7XG4gICAgICAgICAgICAgICAgY3JlYXRpb25DaG9pY2VzID0gZGF0YS5saWZlY3ljbGVfY2hvaWNlcztcbiAgICAgICAgICAgICAgICBjcmVhdGlvbk5vdGljZSA9ICdDaG9vc2UgdGhlIGV4YWN0IGF1dGhvcml6ZWQgb3JnYW5pemF0aW9uL2ZyYW1ld29yayByZWNvcmQgYmVmb3JlIGNyZWF0aW5nIGEgY2FzZS4nO1xuICAgICAgICAgICAgICAgIHJldHVybjtcbiAgICAgICAgICAgIH1cbiAgICAgICAgICAgIGNvbnN0IHByZXBhcmVkID0gZGF0YT8ud29ya2Zsb3dfcHJlcGFyZWQ7XG4gICAgICAgICAgICBpZiAoIXByZXBhcmVkPy5lbmdhZ2VtZW50X2lkIHx8ICFwcmVwYXJlZD8ucHJlcGFyZWRfZGlnZXN0IHx8ICFwcmVwYXJlZD8ucmV2aWV3Py5vcGVyYXRpb25fcGF5bG9hZCkge1xuICAgICAgICAgICAgICAgIHRocm93IG5ldyBFcnJvcignVGhlIG9yaWdpbmFsIFNJQ08gY2FzZS1zZXR1cCBzZXJ2aWNlIGRpZCBub3QgcHJvdmlkZSBhIHZlcmlmaWVkIHJldmlldy4nKTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgICAgIHByZXBhcmVkV29ya2Zsb3cgPSBwcmVwYXJlZDtcbiAgICAgICAgICAgIGFjdGl2ZUVuZ2FnZW1lbnQgPSBTdHJpbmcocHJlcGFyZWQuZW5nYWdlbWVudF9pZCk7XG4gICAgICAgICAgICBsaWZlY3ljbGVQcm9ncmVzcyA9IHByZXBhcmVkLmxpZmVjeWNsZSA/PyBudWxsO1xuICAgICAgICAgICAgcmVjb3JkZWRBcHByb3ZhbCA9IG51bGw7XG4gICAgICAgICAgICBjb25maXJtQ2FzZUNyZWF0aW9uID0gZmFsc2U7XG4gICAgICAgICAgICBjcmVhdGlvbkNob2ljZXMgPSBudWxsO1xuICAgICAgICAgICAgY3JlYXRpb25Ob3RpY2UgPSAnTmV3IGFzc2Vzc21lbnQsIHNjb3BlIGFuZCBvcHRpb25hbCByaXNrIGFzc2Vzc21lbnQgYXJlIFBSRVBBUkVEIHRocm91Z2ggU0lDTy4gUmV2aWV3IHRoZSBleGFjdCBjcmVhdGlvbiBwbGFuIGJlZm9yZSBhcHByb3ZpbmcuJztcbiAgICAgICAgfSBjYXRjaCAoZXJyKSB7XG4gICAgICAgICAgICBjcmVhdGlvbkVycm9yID0gZXJyIGluc3RhbmNlb2YgRXJyb3IgPyBlcnIubWVzc2FnZSA6ICdVbmFibGUgdG8gcHJlcGFyZSB0aGlzIG5ldyBHUkMgY2FzZS4nO1xuICAgICAgICB9IGZpbmFsbHkge1xuICAgICAgICAgICAgY3JlYXRpb25CdXN5ID0gZmFsc2U7XG4gICAgICAgIH1cbiAgICB9XG5cbiAgICBhc3luYyBmdW5jdGlvbiBhcHByb3ZlQW5kQ3JlYXRlQ2FzZSgpIHtcbiAgICAgICAgaWYgKGNyZWF0aW9uQnVzeSB8fCBjYXNlU2F2ZWQgfHwgIWNvbmZpcm1DYXNlQ3JlYXRpb24gfHwgIXByZXBhcmVkV29ya2Zsb3c/LmVuZ2FnZW1lbnRfaWQgfHwgIXByZXBhcmVkV29ya2Zsb3c/LnByZXBhcmVkX2RpZ2VzdCkgcmV0dXJuO1xuICAgICAgICBjcmVhdGlvbkJ1c3kgPSB0cnVlO1xuICAgICAgICBjcmVhdGlvbkVycm9yID0gJyc7XG4gICAgICAgIHRyeSB7XG4gICAgICAgICAgICAvLyBUaGUgZXhpc3RpbmcgU3ZlbHRlS2l0IGFjdGlvbiBpbmRlcGVuZGVudGx5IG9idGFpbnMgc2VydmVyLXNpZGUgYXBwcm92YWwuXG4gICAgICAgICAgICAvLyBJZiBpdHMgcmVzdHJpY3RlZCBjYXNlIHdyaXRlciBpcyBlbmFibGVkLCBpdCBjb21taXRzIHRoZSBTQU1FIHJldmlld2VkXG4gICAgICAgICAgICAvLyBwYXlsb2FkIHRocm91Z2ggdGhlIGV4aXN0aW5nIGF0b21pYyBHUkMgc2VydmljZS4gT3RoZXJ3aXNlIG5vIGNhc2UgaXMgc2F2ZWQuXG4gICAgICAgICAgICBjb25zdCByZXNwb25zZSA9IGF3YWl0IHNpY29Qb3N0QWN0aW9uKCd3b3JrZmxvd19hcHByb3ZlJywge1xuICAgICAgICAgICAgICAgIGVuZ2FnZW1lbnRfaWQ6IFN0cmluZyhwcmVwYXJlZFdvcmtmbG93LmVuZ2FnZW1lbnRfaWQpLFxuICAgICAgICAgICAgICAgIHByZXBhcmVkX2RpZ2VzdDogU3RyaW5nKHByZXBhcmVkV29ya2Zsb3cucHJlcGFyZWRfZGlnZXN0KSxcbiAgICAgICAgICAgICAgICBjb25maXJtX3Jldmlld2VkOiAneWVzJ1xuICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICBjb25zdCBkYXRhID0gcmVzcG9uc2UuZGF0YSBhcyBSZWNvcmQ8c3RyaW5nLCBhbnk+O1xuICAgICAgICAgICAgcmVjb3JkZWRBcHByb3ZhbCA9IGRhdGE/LndvcmtmbG93X2FwcHJvdmVkID8/IG51bGw7XG4gICAgICAgICAgICBpZiAoZGF0YT8ud29ya2Zsb3dfY29tbWl0dGVkPy5idXNpbmVzc19yZWNvcmRzX3dyaXR0ZW4gPT09IHRydWUpIHtcbiAgICAgICAgICAgICAgICBjYXNlU2F2ZWQgPSB0cnVlO1xuICAgICAgICAgICAgICAgIGxpZmVjeWNsZVByb2dyZXNzID0gZGF0YS53b3JrZmxvd19jb21taXR0ZWQubGlmZWN5Y2xlID8/IGxpZmVjeWNsZVByb2dyZXNzO1xuICAgICAgICAgICAgICAgIGNyZWF0aW9uTm90aWNlID0gJ1NJQ08gY29uZmlybWVkIG5ldyBhc3Nlc3NtZW50IHJlY29yZHMgd2VyZSBjcmVhdGVkIHRocm91Z2ggaXRzIG9yaWdpbmFsIEdSQyBzZXJ2aWNlLic7XG4gICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgIGNyZWF0aW9uRXJyb3IgPSBTdHJpbmcoZGF0YT8ud29ya2Zsb3dfZXJyb3IgPz8gJ0FwcHJvdmFsIHJlY29yZGVkLCBidXQgdGhlIEdSQyBjYXNlIHdyaXRlciBpcyBkaXNhYmxlZCBvciBzYXZpbmcgd2FzIG5vdCBpbmRlcGVuZGVudGx5IHZlcmlmaWVkLiBObyBjYXNlIGlzIGNsYWltZWQgdG8gYmUgY3JlYXRlZC4nKTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfSBjYXRjaCAoZXJyKSB7XG4gICAgICAgICAgICBjcmVhdGlvbkVycm9yID0gZXJyIGluc3RhbmNlb2YgRXJyb3IgPyBlcnIubWVzc2FnZSA6ICdDYXNlIGNyZWF0aW9uIGNvdWxkIG5vdCBiZSB2ZXJpZmllZDsgZG8gbm90IHN1Ym1pdCBhIGR1cGxpY2F0ZS4nO1xuICAgICAgICB9IGZpbmFsbHkge1xuICAgICAgICAgICAgY3JlYXRpb25CdXN5ID0gZmFsc2U7XG4gICAgICAgIH1cbiAgICB9XG5cbiAgICBhc3luYyBmdW5jdGlvbiBwcmVwYXJlTmV4dFJlYWxHcmNTdGFnZSgpIHtcbiAgICAgICAgaWYgKHN0YWdlQnVzeSB8fCAhY2FzZVNhdmVkIHx8ICFhY3RpdmVFbmdhZ2VtZW50IHx8IGxpZmVjeWNsZVByb3Bvc2FsKSByZXR1cm47XG4gICAgICAgIHN0YWdlQnVzeSA9IHRydWU7XG4gICAgICAgIHN0YWdlRXJyb3IgPSAnJztcbiAgICAgICAgc3RhZ2VOb3RpY2UgPSAnJztcbiAgICAgICAgdHJ5IHtcbiAgICAgICAgICAgIGNvbnN0IHJlc3BvbnNlID0gYXdhaXQgc2ljb1Bvc3RBY3Rpb24oJ2xpZmVjeWNsZV9uZXh0Jywge1xuICAgICAgICAgICAgICAgIGVuZ2FnZW1lbnRfaWQ6IGFjdGl2ZUVuZ2FnZW1lbnQsXG4gICAgICAgICAgICAgICAgaHVtYW5fZmFjdHM6IHN0YWdlSHVtYW5GYWN0cy50cmltKCkuc2xpY2UoMCwgMTIwMClcbiAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgY29uc3QgcmVzdWx0ID0gKHJlc3BvbnNlLmRhdGEgYXMgUmVjb3JkPHN0cmluZywgYW55Pik/LmxpZmVjeWNsZV9uZXh0O1xuICAgICAgICAgICAgaWYgKCFyZXN1bHQpIHRocm93IG5ldyBFcnJvcignTm8gdmVyaWZpZWQgbGlmZWN5Y2xlIHJlc3VsdCB3YXMgcmV0dXJuZWQuJyk7XG4gICAgICAgICAgICBsaWZlY3ljbGVQcm9ncmVzcyA9IHJlc3VsdC5saWZlY3ljbGUgPz8gbGlmZWN5Y2xlUHJvZ3Jlc3M7XG4gICAgICAgICAgICBpZiAocmVzdWx0LnN0YXR1cyA9PT0gJ3ByZXBhcmVkX2Zvcl9odW1hbl9yZXZpZXcnICYmIHJlc3VsdC5yZXZpZXc/Lm9wZXJhdGlvbl9wYXlsb2FkKSB7XG4gICAgICAgICAgICAgICAgbGlmZWN5Y2xlUHJvcG9zYWwgPSByZXN1bHQ7XG4gICAgICAgICAgICAgICAgc3RhZ2VDb25maXJtZWQgPSBmYWxzZTtcbiAgICAgICAgICAgICAgICBsaWZlY3ljbGVBcHByb3ZhbCA9IG51bGw7XG4gICAgICAgICAgICAgICAgc3RhZ2VOb3RpY2UgPSBgVGhlICR7cmVzdWx0LnN0YWdlfSBvcGVyYXRpb24gaXMgcHJlcGFyZWQgdXNpbmcgU0lDTydzIGV4aXN0aW5nIEdSQyBzZXJ2aWNlLiBOb3RoaW5nIGhhcyBiZWVuIHNhdmVkIHlldC5gO1xuICAgICAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgICAgICBzdGFnZUVycm9yID0gU3RyaW5nKHJlc3VsdC5yZWFzb24gPz8gcmVzdWx0LnF1ZXN0aW9ucz8uam9pbignICcpID8/ICdNb3JlIGluZm9ybWF0aW9uIG9yIHBlcm1pc3Npb24gaXMgbmVlZGVkIGJlZm9yZSBhIG5ldyByZWNvcmQgY2FuIGJlIHByZXBhcmVkLicpO1xuICAgICAgICAgICAgfVxuICAgICAgICB9IGNhdGNoIChlcnIpIHtcbiAgICAgICAgICAgIHN0YWdlRXJyb3IgPSBlcnIgaW5zdGFuY2VvZiBFcnJvciA/IGVyci5tZXNzYWdlIDogJ1RoZSBHUkMgc3RhZ2UgY291bGQgbm90IGJlIHByZXBhcmVkLic7XG4gICAgICAgIH0gZmluYWxseSB7XG4gICAgICAgICAgICBzdGFnZUJ1c3kgPSBmYWxzZTtcbiAgICAgICAgfVxuICAgIH1cblxuICAgIGFzeW5jIGZ1bmN0aW9uIGFwcHJvdmVOZXh0UmVhbEdyY1N0YWdlKCkge1xuICAgICAgICBpZiAoc3RhZ2VCdXN5IHx8ICFzdGFnZUNvbmZpcm1lZCB8fCAhbGlmZWN5Y2xlUHJvcG9zYWw/LnByZXBhcmVkX2RpZ2VzdCB8fCAhYWN0aXZlRW5nYWdlbWVudCkgcmV0dXJuO1xuICAgICAgICBzdGFnZUJ1c3kgPSB0cnVlO1xuICAgICAgICBzdGFnZUVycm9yID0gJyc7XG4gICAgICAgIHRyeSB7XG4gICAgICAgICAgICBjb25zdCByZXNwb25zZSA9IGF3YWl0IHNpY29Qb3N0QWN0aW9uKCdsaWZlY3ljbGVfc3RhZ2VfYXBwcm92ZScsIHtcbiAgICAgICAgICAgICAgICBlbmdhZ2VtZW50X2lkOiBhY3RpdmVFbmdhZ2VtZW50LFxuICAgICAgICAgICAgICAgIHN0YWdlOiBTdHJpbmcobGlmZWN5Y2xlUHJvcG9zYWwuc3RhZ2UpLFxuICAgICAgICAgICAgICAgIHByZXBhcmVkX2RpZ2VzdDogU3RyaW5nKGxpZmVjeWNsZVByb3Bvc2FsLnByZXBhcmVkX2RpZ2VzdCksXG4gICAgICAgICAgICAgICAgY29uZmlybV9yZXZpZXdlZDogJ3llcydcbiAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgbGlmZWN5Y2xlQXBwcm92YWwgPSAocmVzcG9uc2UuZGF0YSBhcyBSZWNvcmQ8c3RyaW5nLCBhbnk+KT8ubGlmZWN5Y2xlX3N0YWdlX2FwcHJvdmVkID8/IG51bGw7XG4gICAgICAgICAgICBzdGFnZU5vdGljZSA9IGxpZmVjeWNsZUFwcHJvdmFsPy5jb21taXRfZW5hYmxlZCA9PT0gdHJ1ZVxuICAgICAgICAgICAgICAgID8gJ0h1bWFuIGFwcHJvdmFsIHJlY29yZGVkLiBBIHNlcGFyYXRlIGNsaWNrIGlzIHJlcXVpcmVkIHRvIGNyZWF0ZSB0aGlzIG5ldyBHUkMgcmVjb3JkLidcbiAgICAgICAgICAgICAgICA6ICdBcHByb3ZhbCByZWNvcmRlZCwgYnV0IHRoaXMgR1JDIHdyaXRlciBpcyBkaXNhYmxlZC4gTm8gYnVzaW5lc3MgcmVjb3JkcyB3ZXJlIGNyZWF0ZWQuJztcbiAgICAgICAgfSBjYXRjaCAoZXJyKSB7XG4gICAgICAgICAgICBzdGFnZUVycm9yID0gZXJyIGluc3RhbmNlb2YgRXJyb3IgPyBlcnIubWVzc2FnZSA6ICdTdGFnZSBhcHByb3ZhbCBmYWlsZWQuJztcbiAgICAgICAgfSBmaW5hbGx5IHtcbiAgICAgICAgICAgIHN0YWdlQnVzeSA9IGZhbHNlO1xuICAgICAgICB9XG4gICAgfVxuXG4gICAgYXN5bmMgZnVuY3Rpb24gY29tbWl0TmV4dFJlYWxHcmNTdGFnZSgpIHtcbiAgICAgICAgaWYgKHN0YWdlQnVzeSB8fCAhbGlmZWN5Y2xlQXBwcm92YWw/LmFwcHJvdmVkIHx8IGxpZmVjeWNsZUFwcHJvdmFsPy5jb21taXRfZW5hYmxlZCAhPT0gdHJ1ZSB8fCAhbGlmZWN5Y2xlUHJvcG9zYWwgfHwgIWFjdGl2ZUVuZ2FnZW1lbnQpIHJldHVybjtcbiAgICAgICAgc3RhZ2VCdXN5ID0gdHJ1ZTtcbiAgICAgICAgc3RhZ2VFcnJvciA9ICcnO1xuICAgICAgICB0cnkge1xuICAgICAgICAgICAgY29uc3QgcmVzcG9uc2UgPSBhd2FpdCBzaWNvUG9zdEFjdGlvbignbGlmZWN5Y2xlX3N0YWdlX2NvbW1pdCcsIHtcbiAgICAgICAgICAgICAgICBlbmdhZ2VtZW50X2lkOiBhY3RpdmVFbmdhZ2VtZW50LFxuICAgICAgICAgICAgICAgIHN0YWdlOiBTdHJpbmcobGlmZWN5Y2xlUHJvcG9zYWwuc3RhZ2UpLFxuICAgICAgICAgICAgICAgIHByZXBhcmVkX2RpZ2VzdDogU3RyaW5nKGxpZmVjeWNsZVByb3Bvc2FsLnByZXBhcmVkX2RpZ2VzdCksXG4gICAgICAgICAgICAgICAgY29uZmlybV9yZXZpZXdlZDogJ3llcydcbiAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgY29uc3QgcmVzdWx0ID0gKHJlc3BvbnNlLmRhdGEgYXMgUmVjb3JkPHN0cmluZywgYW55Pik/LmxpZmVjeWNsZV9zdGFnZV9jb21taXR0ZWQ7XG4gICAgICAgICAgICBpZiAocmVzdWx0Py5idXNpbmVzc19yZWNvcmRzX3dyaXR0ZW4gIT09IHRydWUpIHRocm93IG5ldyBFcnJvcignT3JpZ2luYWwgU0lDTyBzZXJ2aWNlIGRpZCBub3QgdmVyaWZ5IHRoYXQgdGhlIHJlY29yZCB3YXMgc2F2ZWQuJyk7XG4gICAgICAgICAgICBsaWZlY3ljbGVQcm9ncmVzcyA9IHJlc3VsdC5saWZlY3ljbGUgPz8gbGlmZWN5Y2xlUHJvZ3Jlc3M7XG4gICAgICAgICAgICBzdGFnZU5vdGljZSA9IGBOZXcgJHtsaWZlY3ljbGVQcm9wb3NhbC5zdGFnZX0gcmVjb3JkcyB3ZXJlIHNhdmVkIHRocm91Z2ggU0lDTydzIGV4aXN0aW5nIEdSQyBzZXJ2aWNlLmA7XG4gICAgICAgICAgICBsaWZlY3ljbGVQcm9wb3NhbCA9IG51bGw7XG4gICAgICAgICAgICBsaWZlY3ljbGVBcHByb3ZhbCA9IG51bGw7XG4gICAgICAgICAgICBzdGFnZUNvbmZpcm1lZCA9IGZhbHNlO1xuICAgICAgICB9IGNhdGNoIChlcnIpIHtcbiAgICAgICAgICAgIHN0YWdlRXJyb3IgPSBlcnIgaW5zdGFuY2VvZiBFcnJvciA/IGVyci5tZXNzYWdlIDogJ1N0YWdlIHNhdmUgY291bGQgbm90IGJlIHZlcmlmaWVkOyBkbyBub3QgcmVwZWF0IGJsaW5kbHkuJztcbiAgICAgICAgfSBmaW5hbGx5IHtcbiAgICAgICAgICAgIHN0YWdlQnVzeSA9IGZhbHNlO1xuICAgICAgICB9XG4gICAgfVxuXG4gICAgZnVuY3Rpb24gZG93bmxvYWRGdWxsUmV2aWV3KCkge1xuICAgICAgICBpZiAoIWZ1bGxSZXZpZXcgfHwgZnVsbFJldmlld0J1c3kpIHJldHVybjtcbiAgICAgICAgY29uc3QgYmxvYiA9IG5ldyBCbG9iKFtKU09OLnN0cmluZ2lmeShmdWxsUmV2aWV3LCBudWxsLCAyKV0sIHsgdHlwZTogJ2FwcGxpY2F0aW9uL2pzb24nIH0pO1xuICAgICAgICBjb25zdCB1cmwgPSBVUkwuY3JlYXRlT2JqZWN0VVJMKGJsb2IpO1xuICAgICAgICBjb25zdCBhID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgnYScpO1xuICAgICAgICBhLmhyZWYgPSB1cmw7XG4gICAgICAgIGEuZG93bmxvYWQgPSBgU0lDT19BY3Rpdml0eTFfdjNfY2hlY2twb2ludF8ke25ldyBEYXRlKCkudG9JU09TdHJpbmcoKS5yZXBsYWNlKC9bOi5dL2csICctJyl9Lmpzb25gO1xuICAgICAgICBkb2N1bWVudC5ib2R5LmFwcGVuZENoaWxkKGEpO1xuICAgICAgICBhLmNsaWNrKCk7XG4gICAgICAgIGEucmVtb3ZlKCk7XG4gICAgICAgIFVSTC5yZXZva2VPYmplY3RVUkwodXJsKTtcbiAgICAgICAgZnVsbFJldmlld05vdGljZSA9ICdDaGVja3BvaW50IGV4cG9ydGVkIHRvIHlvdXIgZGV2aWNlLiBLZWVwIGl0IHByaXZhdGU6IGl0IGNvbnRhaW5zIHlvdXIgYXNzZXNzbWVudCBjb250ZXh0IGFuZCBkcmFmdCByZXNwb25zZXMuJztcbiAgICB9XG5cbiAgICBhc3luYyBmdW5jdGlvbiBpbXBvcnRGdWxsUmV2aWV3KGV2ZW50OiBFdmVudCkge1xuICAgICAgICBpZiAoZnVsbFJldmlld0J1c3kpIHJldHVybjtcbiAgICAgICAgY29uc3QgZmllbGQgPSBldmVudC5jdXJyZW50VGFyZ2V0IGFzIEhUTUxJbnB1dEVsZW1lbnQ7XG4gICAgICAgIGNvbnN0IGZpbGUgPSBmaWVsZC5maWxlcz8uWzBdO1xuICAgICAgICBpZiAoIWZpbGUpIHJldHVybjtcbiAgICAgICAgdHJ5IHtcbiAgICAgICAgICAgIGlmIChmaWxlLnNpemUgPiA2ICogMTAyNCAqIDEwMjQpIHRocm93IG5ldyBFcnJvcignQ2hlY2twb2ludCBleGNlZWRzIHRoZSA2IE1CIGltcG9ydCBsaW1pdC4nKTtcbiAgICAgICAgICAgIGNvbnN0IHBhcnNlZCA9IHZhbGlkYXRlQ2hlY2twb2ludChKU09OLnBhcnNlKGF3YWl0IGZpbGUudGV4dCgpKSk7XG4gICAgICAgICAgICAvLyBSZXN0b3JlIHRoZSBleGFjdCBwcmV2aW91cyBpbnB1dHMgYmVmb3JlIGFsbG93aW5nIGEgc2lnbmVkLWN1cnNvciBjb250aW51YXRpb24uXG4gICAgICAgICAgICBvcmdhbml6YXRpb24gPSBwYXJzZWQuc2NvcGUub3JnYW5pemF0aW9uX25hbWU7XG4gICAgICAgICAgICBmcmFtZXdvcmtTZWFyY2ggPSBwYXJzZWQuc2NvcGUuZnJhbWV3b3JrX25hbWU7XG4gICAgICAgICAgICBpbnN0cnVjdGlvbiA9IHBhcnNlZC5zY29wZS5wcm9ibGVtO1xuICAgICAgICAgICAgZnJhbWV3b3JrQnVzaW5lc3NDb250ZXh0ID0gcGFyc2VkLnNjb3BlLmJ1c2luZXNzX2NvbnRleHQ7XG4gICAgICAgICAgICBmdWxsUmV2aWV3ID0gcGFyc2VkO1xuICAgICAgICAgICAgZnVsbFJldmlld1Nob3duID0gODtcbiAgICAgICAgICAgIGZ1bGxSZXZpZXdDYW5kaWRhdGVzID0gW107XG4gICAgICAgICAgICBmdWxsUmV2aWV3RXJyb3IgPSAnJztcbiAgICAgICAgICAgIGZ1bGxSZXZpZXdOb3RpY2UgPSAnSW1wb3J0ZWQgYW4gdW52ZXJpZmllZCwgY2xpZW50LWhlbGQgZHJhZnQuIFRoZSBiYWNrZW5kIHdpbGwgcmUtY2hlY2sgdGhlIHNpZ25lZCBjdXJzb3IsIHBlcm1pc3Npb25zIGFuZCBmcmFtZXdvcmsgaW52ZW50b3J5IG9uIHRoZSBuZXh0IGJhdGNoLic7XG4gICAgICAgIH0gY2F0Y2ggKGVycm9yKSB7XG4gICAgICAgICAgICBmdWxsUmV2aWV3RXJyb3IgPSBlcnJvciBpbnN0YW5jZW9mIEVycm9yID8gZXJyb3IubWVzc2FnZSA6ICdDaGVja3BvaW50IGNvdWxkIG5vdCBiZSBpbXBvcnRlZC4nO1xuICAgICAgICB9IGZpbmFsbHkge1xuICAgICAgICAgICAgZmllbGQudmFsdWUgPSAnJztcbiAgICAgICAgfVxuICAgIH1cblxuICAgIGZ1bmN0aW9uIGNsZWFyU3RhbGVDYXNlKCkge1xuICAgICAgICBnZW5lcmF0ZWRTaXh0ZWVuID0gW107XG4gICAgICAgIGdlbmVyYXRlZEZvciA9ICcnO1xuICAgICAgICBzaXh0ZWVuRXJyb3IgPSAnJztcbiAgICAgICAgY2FzZVNhdmVOb3RpY2UgPSAnJztcbiAgICAgICAgcHJlcGFyZWRXb3JrZmxvdyA9IG51bGw7XG4gICAgICAgIHJlY29yZGVkQXBwcm92YWwgPSBudWxsO1xuICAgICAgICBsaWZlY3ljbGVQcm9ncmVzcyA9IG51bGw7XG4gICAgICAgIGFjdGl2ZUVuZ2FnZW1lbnQgPSAnJztcbiAgICB9XG5cbiAgICBhc3luYyBmdW5jdGlvbiBzaWNvUG9zdEFjdGlvbihhY3Rpb246IHN0cmluZywgZGF0YTogUmVjb3JkPHN0cmluZywgc3RyaW5nPikge1xuICAgICAgICBjb25zdCBwYXlsb2FkID0gbmV3IEZvcm1EYXRhKCk7XG4gICAgICAgIGZvciAoY29uc3QgW2tleSwgdmFsdWVdIG9mIE9iamVjdC5lbnRyaWVzKGRhdGEpKSBwYXlsb2FkLnNldChrZXksIHZhbHVlKTtcbiAgICAgICAgY29uc3QgcmVzID0gYXdhaXQgZmV0Y2goYD8vJHthY3Rpb259YCwge1xuICAgICAgICAgICAgbWV0aG9kOiAnUE9TVCcsIGJvZHk6IHBheWxvYWQsIGhlYWRlcnM6IHsgYWNjZXB0OiAnYXBwbGljYXRpb24vanNvbicgfVxuICAgICAgICB9KTtcbiAgICAgICAgY29uc3QgcGFyc2VkID0gZGVzZXJpYWxpemUoYXdhaXQgcmVzLnRleHQoKSk7XG4gICAgICAgIGlmIChwYXJzZWQudHlwZSAhPT0gJ3N1Y2Nlc3MnKSB7XG4gICAgICAgICAgICBjb25zdCBib2R5ID0gcGFyc2VkLnR5cGUgPT09ICdmYWlsdXJlJyA/IChwYXJzZWQuZGF0YSBhcyBSZWNvcmQ8c3RyaW5nLCBhbnk+KSA6IG51bGw7XG4gICAgICAgICAgICB0aHJvdyBuZXcgRXJyb3IoU3RyaW5nKGJvZHk/LmNvdmVyYWdlX3BsYW5fZXJyb3IgPz8gYm9keT8uc291cmNlX2Vycm9yID8/IGJvZHk/LmNhc2VfZHJhZnRfZXJyb3IgPz8gYm9keT8uZnJhbWV3b3JrX2JhdGNoX2Vycm9yID8/IGJvZHk/LmNvbnRyb2xfZXJyb3IgPz8gYm9keT8uYWlfc2l4dGVlbl9lcnJvciA/PyBib2R5Py5saWZlY3ljbGVfZXJyb3IgPz8gYm9keT8ud29ya2Zsb3dfZXJyb3IgPz8gJ1RoZSByZXF1ZXN0ZWQgb3BlcmF0aW9uIGNvdWxkIG5vdCBmaW5pc2guJykpO1xuICAgICAgICB9XG4gICAgICAgIHJldHVybiBwYXJzZWQ7XG4gICAgfVxuXG4gICAgYXN5bmMgZnVuY3Rpb24gbG9hZFNhdmVkQ29udHJvbFByb2dyZXNzKGNhc2VJZCA9ICcnKSB7XG4gICAgICAgIHRyeSB7XG4gICAgICAgICAgICBjb25zdCByZXNwb25zZSA9IGF3YWl0IHNpY29Qb3N0QWN0aW9uKCdyZXF1aXJlbWVudF9yZXZpZXcnLCB7XG4gICAgICAgICAgICAgICAgYWN0aW9uOiAnc3RhdHVzJywgZW5nYWdlbWVudF9pZDogY2FzZUlkIHx8IGFjdGl2ZUVuZ2FnZW1lbnRcbiAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgY29uc3QgcHJvZ3Jlc3MgPSAocmVzcG9uc2UuZGF0YSBhcyBSZWNvcmQ8c3RyaW5nLCBhbnk+KT8uY29udHJvbF9yZXZpZXc/LnByb2dyZXNzO1xuICAgICAgICAgICAgaWYgKHByb2dyZXNzPy5jYXNlX2lkKSB7XG4gICAgICAgICAgICAgICAgY29udHJvbFByb2dyZXNzID0gcHJvZ3Jlc3M7XG4gICAgICAgICAgICAgICAgY29udHJvbEVycm9yID0gJyc7XG4gICAgICAgICAgICB9XG4gICAgICAgIH0gY2F0Y2gge1xuICAgICAgICAgICAgLy8gQW4gdW5wcm92aXNpb25lZCBvciBub3QteWV0LXNhdmVkIGNvbXBhbnkgaGFzIG5vIGNvbnRyb2wgcmVjb3Jkcy5cbiAgICAgICAgICAgIC8vIERvIG5vdCBkaXNwbGF5IGEgbWlzbGVhZGluZyByZXN1bHQgb3IgYXNrIGZvciBtYW51YWwgVVVJRHMuXG4gICAgICAgIH1cbiAgICB9XG5cbiAgICBhc3luYyBmdW5jdGlvbiBnZW5lcmF0ZUFuZFNhdmVOZXh0Q29udHJvbCgpIHtcbiAgICAgICAgaWYgKGNvbnRyb2xCdXN5IHx8ICFjb250cm9sUHJvZ3Jlc3M/LmNhc2VfaWQpIHJldHVybjtcbiAgICAgICAgY29udHJvbEJ1c3kgPSB0cnVlO1xuICAgICAgICBjb250cm9sRXJyb3IgPSAnJztcbiAgICAgICAgY29udHJvbE5vdGljZSA9ICcnO1xuICAgICAgICB0cnkge1xuICAgICAgICAgICAgY29uc3QgcmVzcG9uc2UgPSBhd2FpdCBzaWNvUG9zdEFjdGlvbigncmVxdWlyZW1lbnRfcmV2aWV3Jywge1xuICAgICAgICAgICAgICAgIGFjdGlvbjogJ2dlbmVyYXRlX2FuZF9zYXZlJywgZW5nYWdlbWVudF9pZDogYWN0aXZlRW5nYWdlbWVudCxcbiAgICAgICAgICAgICAgICBjb25maXJtX3ByZWxpbWluYXJ5X3dyaXRlOiAndHJ1ZSdcbiAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgY29uc3QgcmVzdWx0ID0gKHJlc3BvbnNlLmRhdGEgYXMgUmVjb3JkPHN0cmluZywgYW55Pik/LmNvbnRyb2xfcmV2aWV3O1xuICAgICAgICAgICAgaWYgKHJlc3VsdD8uYnVzaW5lc3NfcmVjb3Jkc193cml0dGVuICE9PSB0cnVlIHx8IHJlc3VsdD8udmVyaWZpZWQgIT09IHRydWUgfHxcbiAgICAgICAgICAgICAgICAhcmVzdWx0Py5wcm9ncmVzcz8uY2FzZV9pZCB8fCByZXN1bHQ/LnJlY29yZD8ucmVzdWx0ICE9PSAnbm90X2Fzc2Vzc2VkJykge1xuICAgICAgICAgICAgICAgIHRocm93IG5ldyBFcnJvcignVGhlIGF1ZGl0IHJlY29yZCBjb3VsZCBub3QgYmUgaW5kZXBlbmRlbnRseSB2ZXJpZmllZCBhcyBzYXZlZC4nKTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgICAgIGNvbnRyb2xQcm9ncmVzcyA9IHJlc3VsdC5wcm9ncmVzcztcbiAgICAgICAgICAgIGNvbnRyb2xOb3RpY2UgPSAnQSBjb250cm9sLXNwZWNpZmljIHJldmlldyB3YXMgZ2VuZXJhdGVkIGFuZCByZXRyaWV2ZWQgdGhyb3VnaCBTSUNPLic7XG4gICAgICAgIH0gY2F0Y2ggKGVycm9yKSB7XG4gICAgICAgICAgICBjb250cm9sRXJyb3IgPSBlcnJvciBpbnN0YW5jZW9mIEVycm9yID8gZXJyb3IubWVzc2FnZSA6ICdDb250cm9sIHJldmlldyBjb3VsZCBub3QgYmUgc2F2ZWQuJztcbiAgICAgICAgfSBmaW5hbGx5IHtcbiAgICAgICAgICAgIGNvbnRyb2xCdXN5ID0gZmFsc2U7XG4gICAgICAgIH1cbiAgICB9XG5cblxuICAgIGFzeW5jIGZ1bmN0aW9uIHN0YXJ0R2VuZXJhdGVkQ2FzZShldmVudDogU3VibWl0RXZlbnQpIHtcbiAgICAgICAgZXZlbnQucHJldmVudERlZmF1bHQoKTtcbiAgICAgICAgYXdhaXQgZ2VuZXJhdGVDb25uZWN0ZWRUaHJvdWdoKDE2KTtcbiAgICB9XG5cbiAgICBhc3luYyBmdW5jdGlvbiBnZW5lcmF0ZUNvbm5lY3RlZFRocm91Z2gobGFzdEFjdGl2aXR5OiBudW1iZXIpIHtcbiAgICAgICAgaWYgKHNpeHRlZW5CdXN5IHx8ICFvcmdhbml6YXRpb24udHJpbSgpIHx8ICFmcmFtZXdvcmtTZWFyY2gudHJpbSgpIHx8IGluc3RydWN0aW9uLnRyaW0oKS5sZW5ndGggPCAyMCkgcmV0dXJuO1xuICAgICAgICBzaXh0ZWVuQnVzeSA9IHRydWU7XG4gICAgICAgIHNpeHRlZW5FcnJvciA9ICcnO1xuICAgICAgICBjYXNlU2F2ZU5vdGljZSA9ICcnO1xuICAgICAgICBjb25zdCBzdWJtaXR0ZWQgPSB7XG4gICAgICAgICAgICBvcmdhbml6YXRpb25fbmFtZTogb3JnYW5pemF0aW9uLnRyaW0oKSwgZnJhbWV3b3JrX25hbWU6IGZyYW1ld29ya1NlYXJjaC50cmltKCksIHByb2JsZW06IGluc3RydWN0aW9uLnRyaW0oKVxuICAgICAgICB9O1xuICAgICAgICBjb25zdCBmaW5nZXJwcmludCA9IEpTT04uc3RyaW5naWZ5KHN1Ym1pdHRlZCk7XG4gICAgICAgIGlmIChmaW5nZXJwcmludCAhPT0gZ2VuZXJhdGVkRm9yKSB7XG4gICAgICAgICAgICBnZW5lcmF0ZWRTaXh0ZWVuID0gW107XG4gICAgICAgICAgICBnZW5lcmF0ZWRGb3IgPSBmaW5nZXJwcmludDtcbiAgICAgICAgfVxuICAgICAgICB0cnkge1xuICAgICAgICAgICAgLy8gQSBzaW5nbGUgY2xpY2sgZ2VuZXJhdGVzIHNlcXVlbnRpYWxseTsgZWFjaCB2YWxpZGF0ZWQgcmVzdWx0IGlzXG4gICAgICAgICAgICAvLyBkaXNwbGF5ZWQgaW1tZWRpYXRlbHkgYW5kIGEgcmV0cnkgcmVzdW1lcyB0aGUgZmlyc3QgbWlzc2luZyBpdGVtLlxuICAgICAgICAgICAgZm9yIChsZXQgbnVtYmVyID0gZ2VuZXJhdGVkU2l4dGVlbi5sZW5ndGggKyAxOyBudW1iZXIgPD0gbGFzdEFjdGl2aXR5OyBudW1iZXIrKykge1xuICAgICAgICAgICAgICAgIC8vIFByaW9yIFF3ZW4gd29yayBwcm9kdWN0cyBmb3JtIHRoZSBzaGFyZWQsIHVudmVyaWZpZWQgY2FzZSBjb250ZXh0LlxuICAgICAgICAgICAgICAgIC8vIE9ubHkgYm91bmRlZCBlYXJsaWVyLXN0YWdlIHRleHQgYW5kIHByb3Bvc2VkIG9iamVjdHMgYXJlIGZvcndhcmRlZC5cbiAgICAgICAgICAgICAgICBjb25zdCBrZXlTdGFnZXMgPSBuZXcgU2V0KFsyLCA0LCA2LCA3LCA5LCAxMSwgMTJdKTtcbiAgICAgICAgICAgICAgICBjb25zdCBwcmlvciA9IGdlbmVyYXRlZFNpeHRlZW4uZmlsdGVyKChpdGVtKSA9PlxuICAgICAgICAgICAgICAgICAgICBrZXlTdGFnZXMuaGFzKE51bWJlcihpdGVtLm51bWJlcikpIHx8IE51bWJlcihpdGVtLm51bWJlcikgPj0gbnVtYmVyIC0gMlxuICAgICAgICAgICAgICAgICkubWFwKChpdGVtKSA9PiAoe1xuICAgICAgICAgICAgICAgICAgICBudW1iZXI6IE51bWJlcihpdGVtLm51bWJlciksXG4gICAgICAgICAgICAgICAgICAgIGFuYWx5c2lzOiBTdHJpbmcoaXRlbS5hbmFseXNpcyA/PyAnJykuc2xpY2UoMCwgMTgwKSxcbiAgICAgICAgICAgICAgICAgICAgcHJvcG9zZWRfd29yazogU3RyaW5nKGl0ZW0ucHJvcG9zZWRfd29yayA/PyAnJykuc2xpY2UoMCwgMTgwKSxcbiAgICAgICAgICAgICAgICAgICAgY2FzZV9wcm9maWxlOiBpdGVtLmNhc2VfcHJvZmlsZSA/PyBudWxsLFxuICAgICAgICAgICAgICAgICAgICBjYW5kaWRhdGVfYXNzZXRzOiBpdGVtLmNhbmRpZGF0ZV9hc3NldHMgPz8gW11cbiAgICAgICAgICAgICAgICB9KSk7XG4gICAgICAgICAgICAgICAgY29uc3QgcmVzcG9uc2UgPSBhd2FpdCBzaWNvUG9zdEFjdGlvbignYWlfc2l4dGVlbl9pdGVtJywge1xuICAgICAgICAgICAgICAgICAgICAuLi5zdWJtaXR0ZWQsIGFjdGl2aXR5X251bWJlcjogU3RyaW5nKG51bWJlciksXG4gICAgICAgICAgICAgICAgICAgIGNhc2VfY29udGV4dDogSlNPTi5zdHJpbmdpZnkocHJpb3IpXG4gICAgICAgICAgICAgICAgfSk7XG4gICAgICAgICAgICAgICAgY29uc3QgcmVzdWx0ID0gKHJlc3BvbnNlLmRhdGEgYXMgUmVjb3JkPHN0cmluZywgYW55Pik/LmFpX3NpeHRlZW5faXRlbTtcbiAgICAgICAgICAgICAgICBpZiAoIXJlc3VsdCB8fCByZXN1bHQuYWN0aXZpdHlfbnVtYmVyICE9PSBudW1iZXIgfHxcbiAgICAgICAgICAgICAgICAgICAgIXJlc3VsdC5hY3Rpdml0eSB8fCByZXN1bHQuYWN0aXZpdHkubnVtYmVyICE9PSBudW1iZXIgfHxcbiAgICAgICAgICAgICAgICAgICAgdHlwZW9mIHJlc3VsdC5hY3Rpdml0eS5hbmFseXNpcyAhPT0gJ3N0cmluZycpIHtcbiAgICAgICAgICAgICAgICAgICAgdGhyb3cgbmV3IEVycm9yKGBBY3Rpdml0eSAke251bWJlcn0gcmV0dXJuZWQgYW4gaW52YWxpZCBkcmFmdCByZXN1bHQuYCk7XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgIGdlbmVyYXRlZFNpeHRlZW4gPSBbLi4uZ2VuZXJhdGVkU2l4dGVlbiwgcmVzdWx0LmFjdGl2aXR5XTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfSBjYXRjaCAoZXJyKSB7XG4gICAgICAgICAgICBzaXh0ZWVuRXJyb3IgPSBlcnIgaW5zdGFuY2VvZiBFcnJvciA/IGVyci5tZXNzYWdlIDogJ0RyYWZ0IGdlbmVyYXRpb24gc3RvcHBlZCB1bmV4cGVjdGVkbHkuJztcbiAgICAgICAgfVxuICAgICAgICAvLyBUaGlzIHBoYXNlIGlzIEdFTkVSQVRJT04gT05MWSBieSB1c2VyIHJlcXVlc3QuIE5ldmVyIHRyeSB0byBjcmVhdGUsXG4gICAgICAgIC8vIGFwcHJvdmUgb3Igc2F2ZSBhbiBhdWRpdCBvciB0ZW5hbnQgYWZ0ZXIgZmluaXNoaW5nIHRoZSAxNiBkcmFmdHMuXG4gICAgICAgIHNpeHRlZW5CdXN5ID0gZmFsc2U7XG4gICAgfVxuICAgIGNvbnN0IGxhdGVzdFJlc3BvbnNlID0gJGRlcml2ZWQoZm9ybSBhcyBSZWNvcmQ8c3RyaW5nLCBhbnk+IHwgbnVsbCk7XG4gICAgJGVmZmVjdCgoKSA9PiB7XG4gICAgICAgIGlmIChsYXRlc3RSZXNwb25zZT8uc2ljb19ydW4pIGxhc3RBZ2VudFJ1biA9IGxhdGVzdFJlc3BvbnNlO1xuICAgICAgICBpZiAobGF0ZXN0UmVzcG9uc2U/LndvcmtmbG93X29wdGlvbnMpIGVsaWdpYmxlT3B0aW9ucyA9IGxhdGVzdFJlc3BvbnNlLndvcmtmbG93X29wdGlvbnM7XG4gICAgICAgIGlmIChsYXRlc3RSZXNwb25zZT8ud29ya2Zsb3dfcHJlcGFyZWQpIHtcbiAgICAgICAgICAgIGdlbmVyYXRlZEFzc2Vzc21lbnQgPSBsYXRlc3RSZXNwb25zZT8uZ2VuZXJhdGVkX2Fzc2Vzc21lbnQgPz8gbnVsbDtcbiAgICAgICAgICAgIGdlbmVyYXRpb25FcnJvciA9IFN0cmluZyhsYXRlc3RSZXNwb25zZT8uZ2VuZXJhdGlvbl9lcnJvciA/PyAnJyk7XG4gICAgICAgICAgICBwcmVwYXJlZFdvcmtmbG93ID0gbGF0ZXN0UmVzcG9uc2Uud29ya2Zsb3dfcHJlcGFyZWQ7XG4gICAgICAgICAgICBhY3RpdmVFbmdhZ2VtZW50ID0gU3RyaW5nKHByZXBhcmVkV29ya2Zsb3c/LmVuZ2FnZW1lbnRfaWQgPz8gJycpO1xuICAgICAgICAgICAgaWYgKHByZXBhcmVkV29ya2Zsb3c/LmxpZmVjeWNsZSkgbGlmZWN5Y2xlUHJvZ3Jlc3MgPSBwcmVwYXJlZFdvcmtmbG93LmxpZmVjeWNsZTtcbiAgICAgICAgICAgIHJlY29yZGVkQXBwcm92YWwgPSBudWxsO1xuICAgICAgICB9XG4gICAgICAgIGlmIChsYXRlc3RSZXNwb25zZT8ud29ya2Zsb3dfcmV2aWV3KSB7XG4gICAgICAgICAgICBwcmVwYXJlZFdvcmtmbG93ID0gbGF0ZXN0UmVzcG9uc2Uud29ya2Zsb3dfcmV2aWV3O1xuICAgICAgICAgICAgcmVjb3JkZWRBcHByb3ZhbCA9IGxhdGVzdFJlc3BvbnNlLndvcmtmbG93X3Jldmlldy5hcHByb3ZlZCA/XG4gICAgICAgICAgICAgICAgeyBjb21taXRfZW5hYmxlZDogbGF0ZXN0UmVzcG9uc2Uud29ya2Zsb3dfcmV2aWV3LmNvbW1pdF9lbmFibGVkIH0gOiBudWxsO1xuICAgICAgICB9XG4gICAgICAgIGlmIChsYXRlc3RSZXNwb25zZT8ud29ya2Zsb3dfYXBwcm92ZWQpIHJlY29yZGVkQXBwcm92YWwgPSBsYXRlc3RSZXNwb25zZS53b3JrZmxvd19hcHByb3ZlZDtcbiAgICAgICAgY29uc3QgbmV3bHlTYXZlZENhc2UgPSBsYXRlc3RSZXNwb25zZT8ud29ya2Zsb3dfY29tbWl0dGVkPy5idXNpbmVzc19yZWNvcmRzX3dyaXR0ZW4gPT09IHRydWVcbiAgICAgICAgICAgID8gU3RyaW5nKHByZXBhcmVkV29ya2Zsb3c/LmVuZ2FnZW1lbnRfaWQgPz8gYWN0aXZlRW5nYWdlbWVudCkgOiAnJztcbiAgICAgICAgaWYgKG5ld2x5U2F2ZWRDYXNlICYmIG5ld2x5U2F2ZWRDYXNlICE9PSBsYXN0Q29udHJvbENhc2VMb2FkZWQpIHtcbiAgICAgICAgICAgIGxhc3RDb250cm9sQ2FzZUxvYWRlZCA9IG5ld2x5U2F2ZWRDYXNlO1xuICAgICAgICAgICAgdm9pZCBsb2FkU2F2ZWRDb250cm9sUHJvZ3Jlc3MobmV3bHlTYXZlZENhc2UpO1xuICAgICAgICB9XG4gICAgICAgIGlmIChsYXRlc3RSZXNwb25zZT8ud29ya2Zsb3dfY29tbWl0dGVkPy53b3JrZmxvdykge1xuICAgICAgICAgICAgYWN0aXZlRW5nYWdlbWVudCA9IFN0cmluZyhwcmVwYXJlZFdvcmtmbG93Py5lbmdhZ2VtZW50X2lkID8/IGFjdGl2ZUVuZ2FnZW1lbnQpO1xuICAgICAgICAgICAgaWYgKGxhdGVzdFJlc3BvbnNlLndvcmtmbG93X2NvbW1pdHRlZC5saWZlY3ljbGUpXG4gICAgICAgICAgICAgICAgbGlmZWN5Y2xlUHJvZ3Jlc3MgPSBsYXRlc3RSZXNwb25zZS53b3JrZmxvd19jb21taXR0ZWQubGlmZWN5Y2xlO1xuICAgICAgICB9XG4gICAgICAgIGlmIChsYXRlc3RSZXNwb25zZT8ubGlmZWN5Y2xlX3N0YXR1cykge1xuICAgICAgICAgICAgbGlmZWN5Y2xlUHJvZ3Jlc3MgPSBsYXRlc3RSZXNwb25zZS5saWZlY3ljbGVfc3RhdHVzO1xuICAgICAgICAgICAgYWN0aXZlRW5nYWdlbWVudCA9IFN0cmluZyhsYXRlc3RSZXNwb25zZS5saWZlY3ljbGVfc3RhdHVzLmVuZ2FnZW1lbnRfaWQgPz8gYWN0aXZlRW5nYWdlbWVudCk7XG4gICAgICAgIH1cbiAgICAgICAgaWYgKGxhdGVzdFJlc3BvbnNlPy5saWZlY3ljbGVfbmV4dCkge1xuICAgICAgICAgICAgbGlmZWN5Y2xlUHJvcG9zYWwgPSBsYXRlc3RSZXNwb25zZS5saWZlY3ljbGVfbmV4dDtcbiAgICAgICAgICAgIGxpZmVjeWNsZUFwcHJvdmFsID0gbnVsbDtcbiAgICAgICAgICAgIGlmIChsaWZlY3ljbGVQcm9wb3NhbD8ubGlmZWN5Y2xlKSBsaWZlY3ljbGVQcm9ncmVzcyA9IGxpZmVjeWNsZVByb3Bvc2FsLmxpZmVjeWNsZTtcbiAgICAgICAgfVxuICAgICAgICBpZiAobGF0ZXN0UmVzcG9uc2U/LmxpZmVjeWNsZV9zdGFnZV9hcHByb3ZlZCkgbGlmZWN5Y2xlQXBwcm92YWwgPSBsYXRlc3RSZXNwb25zZS5saWZlY3ljbGVfc3RhZ2VfYXBwcm92ZWQ7XG4gICAgICAgIGlmIChsYXRlc3RSZXNwb25zZT8ubGlmZWN5Y2xlX3N0YWdlX2NvbW1pdHRlZCkge1xuICAgICAgICAgICAgaWYgKGxhdGVzdFJlc3BvbnNlLmxpZmVjeWNsZV9zdGFnZV9jb21taXR0ZWQubGlmZWN5Y2xlKVxuICAgICAgICAgICAgICAgIGxpZmVjeWNsZVByb2dyZXNzID0gbGF0ZXN0UmVzcG9uc2UubGlmZWN5Y2xlX3N0YWdlX2NvbW1pdHRlZC5saWZlY3ljbGU7XG4gICAgICAgICAgICBsaWZlY3ljbGVQcm9wb3NhbCA9IG51bGw7XG4gICAgICAgICAgICBsaWZlY3ljbGVBcHByb3ZhbCA9IG51bGw7XG4gICAgICAgIH1cbiAgICB9KTtcbiAgICBjb25zdCByZXN1bHQgPSAkZGVyaXZlZCgobGF0ZXN0UmVzcG9uc2U/LnNpY29fcnVuID8gbGF0ZXN0UmVzcG9uc2UgOiBsYXN0QWdlbnRSdW4pIGFzIFJlY29yZDxzdHJpbmcsIGFueT4gfCBudWxsKTtcbiAgICBjb25zdCBydW4gPSAkZGVyaXZlZChyZXN1bHQ/LnNpY29fcnVuIGFzIFJlY29yZDxzdHJpbmcsIGFueT4gfCB1bmRlZmluZWQpO1xuICAgIGNvbnN0IHBsYW4gPSAkZGVyaXZlZChyZXN1bHQ/LnNpY29fcGxhbiBhcyBSZWNvcmQ8c3RyaW5nLCBhbnk+IHwgdW5kZWZpbmVkKTtcbiAgICBjb25zdCBhZ2VudCA9ICRkZXJpdmVkKHJlc3VsdD8uc2ljb19hZ2VudCBhcyBSZWNvcmQ8c3RyaW5nLCBhbnk+IHwgdW5kZWZpbmVkKTtcbiAgICBjb25zdCBkaXNjb3ZlcnkgPSAkZGVyaXZlZChyZXN1bHQ/LmRpc2NvdmVyeSA/PyByZXN1bHQ/LnJlY29yZHMgPz8gbnVsbCk7XG4gICAgY29uc3QgYWR2aXNvcnkgPSAkZGVyaXZlZChyZXN1bHQ/LmRyYWZ0ID8/IHJlc3VsdD8uY2FzZV9wbGFuID8/IHJlc3VsdD8uY2FzZV9pbnRha2UgPz8gbnVsbCk7XG4gICAgY29uc3QgcHJvdmlkZXJNb2RlID0gJGRlcml2ZWQoU3RyaW5nKGFkdmlzb3J5Py5zb3VyY2Vfc3VtbWFyeT8ucHJvdmlkZXJfbW9kZSA/PyAndW5rbm93bicpKTtcbiAgICBjb25zdCBwcm92aWRlckZhaWxlZCA9ICRkZXJpdmVkKC9mYWxsYmFja3xlcnJvcnxmYWlsZWR8dW5hdmFpbGFibGUvaS50ZXN0KHByb3ZpZGVyTW9kZSkpO1xuICAgIGNvbnN0IHJlY29yZHNSZWFkeSA9ICRkZXJpdmVkKHJ1bj8uZGlzY292ZXJ5ID09PSAnY29tcGxldGVkJyk7XG4gICAgY29uc3QgaW50YWtlUmVhZHkgPSAkZGVyaXZlZChydW4/LmludGFrZSA9PT0gJ2NvbXBsZXRlZCcgJiYgIXByb3ZpZGVyRmFpbGVkKTtcbiAgICBjb25zdCByZWNvcmRHcm91cHMgPSAkZGVyaXZlZChzdW1tYXJpemVSZWNvcmRHcm91cHMoZGlzY292ZXJ5KSk7XG4gICAgY29uc3QgYWR2aXNvcnlOb3RlcyA9ICRkZXJpdmVkKGludGFrZVJlYWR5ID8gY29sbGVjdFBsYWluTm90ZXMoYWR2aXNvcnkpIDogW10pO1xuICAgIGNvbnN0IGRpc2NvdmVyeUZhaWx1cmUgPSAkZGVyaXZlZChTdHJpbmcocmVzdWx0Py5kaXNjb3ZlcnlfZXJyb3IgPz8gJycpLnRyaW0oKSk7XG4gICAgY29uc3QgaW50YWtlRmFpbHVyZSA9ICRkZXJpdmVkKFN0cmluZyhyZXN1bHQ/LmludGFrZV9lcnJvciA/PyAnJykudHJpbSgpKTtcbiAgICBjb25zdCBuZWVkc09yZ2FuaXphdGlvbiA9ICRkZXJpdmVkKCFvcmdhbml6YXRpb24udHJpbSgpICYmIChcbiAgICAgICAgL29yZ2FuaXphdGlvbnxkb21haW4vaS50ZXN0KGRpc2NvdmVyeUZhaWx1cmUpIHx8ICFyZWNvcmRzUmVhZHlcbiAgICApKTtcblxuICAgIGNvbnN0IGV4YW1wbGVzID0gW1xuICAgICAgICAnQXNzZXNzIHRoZSBjeWJlcnNlY3VyaXR5IGNvbXBsaWFuY2Ugb2YgRGVtbyBCYW5rIGluIFNhdWRpIEFyYWJpYSBhZ2FpbnN0IE5DQSBFQ0MuIExvb2sgdXAgcGVybWl0dGVkIHJlY29yZHMsIGlkZW50aWZ5IG1pc3NpbmcgaW5mb3JtYXRpb24sIGFuZCBwcm9wb3NlIG5leHQgc3RlcHMgZm9yIGh1bWFuIHJldmlldy4nLFxuICAgICAgICAnUHJlcGFyZSBhbiBJU08gMjcwMDE6MjAyMiBhc3Nlc3NtZW50IHBsYW4uIENvbmZpcm0gdGhlIHNjb3BlLCBkaXNjb3ZlciBhdXRob3JpemVkIHJlY29yZHMsIGFuZCBpZGVudGlmeSBldmlkZW5jZSB0aGF0IHN0aWxsIG5lZWRzIHJldmlldy4nLFxuICAgICAgICAnSW52ZXN0aWdhdGUgb3VyIGN5YmVyc2VjdXJpdHkgcmlzayBleHBvc3VyZSwgZXhpc3Rpbmcgc2FmZWd1YXJkcywgYW5kIHRoZSBhZGRpdGlvbmFsIGluZm9ybWF0aW9uIG5lZWRlZCBmb3IgYSBmb3JtYWwgcmlzayBhc3Nlc3NtZW50LicsXG4gICAgICAgICdBc3Nlc3Mgb3VyIHJlYWRpbmVzcyBmb3IgYW4gaW50ZXJuYWwgc2VjdXJpdHkgYXVkaXQuIFJlcG9ydCBvbmx5IHZlcmlmaWVkIHJlY29yZHMgYW5kIGlkZW50aWZ5IHVuYW5zd2VyZWQgcXVlc3Rpb25zLidcbiAgICBdO1xuXG4gICAgdHlwZSBHcm91cCA9IHsgbGFiZWw6IHN0cmluZzsgY291bnQ6IG51bWJlcjsgZXhhbXBsZXM6IHN0cmluZ1tdIH07XG4gICAgZnVuY3Rpb24gaXNPYmplY3QodjogdW5rbm93bik6IHYgaXMgUmVjb3JkPHN0cmluZywgdW5rbm93bj4ge1xuICAgICAgICByZXR1cm4gISF2ICYmIHR5cGVvZiB2ID09PSAnb2JqZWN0JyAmJiAhQXJyYXkuaXNBcnJheSh2KTtcbiAgICB9XG4gICAgZnVuY3Rpb24gcGxhaW5UZXh0KHY6IHVua25vd24pOiBzdHJpbmcge1xuICAgICAgICBpZiAodHlwZW9mIHYgIT09ICdzdHJpbmcnKSByZXR1cm4gJyc7XG4gICAgICAgIGNvbnN0IHMgPSB2LnJlcGxhY2UoL1xccysvZywgJyAnKS50cmltKCk7XG4gICAgICAgIGlmICghcyB8fCAvXltcXFt7XS8udGVzdChzKSB8fCBzLmxlbmd0aCA+IDY1MCB8fCAvXFxcIlthLXpfXStcXFwiXFxzKjovLnRlc3QocykpIHJldHVybiAnJztcbiAgICAgICAgcmV0dXJuIHM7XG4gICAgfVxuICAgIC8vIFByZXNlbnRhdGlvbiBvbmx5OiBwcmVzZXJ2ZSB0aGUgb3JpZ2luYWwga2V5cyBhbmQgdmFsdWVzIGluIGNoZWNrcG9pbnQgSlNPTi5cbiAgICAvLyBUdXJucyBsYWJlbHMgbGlrZSBhc3NldF90eXBlIC8gb3duZXJfcm9sZSAvIGxpbmtlZFJpc2tSZWZlcmVuY2UgaW50byByZWFkYWJsZSB0ZXh0LlxuICAgIGZ1bmN0aW9uIGRpc3BsYXlGaWVsZExhYmVsKHJhdzogdW5rbm93bik6IHN0cmluZyB7XG4gICAgICAgIGNvbnN0IGxhYmVsID0gU3RyaW5nKHJhdyA/PyAnJylcbiAgICAgICAgICAgIC5yZXBsYWNlKC8oW2EtejAtOV0pKFtBLVpdKS9nLCAnJDEgJDInKVxuICAgICAgICAgICAgLnJlcGxhY2UoL1tfLV0rL2csICcgJylcbiAgICAgICAgICAgIC5yZXBsYWNlKC9cXHMqXFwvXFxzKi9nLCAnIC8gJylcbiAgICAgICAgICAgIC5yZXBsYWNlKC9cXHMrL2csICcgJylcbiAgICAgICAgICAgIC50cmltKCk7XG4gICAgICAgIGNvbnN0IGFiYnJldmlhdGlvbnMgPSBuZXcgU2V0KFsnQUknLCAnQVBJJywgJ0NTRicsICdDVlNTJywgJ0dSQycsICdJRCcsICdJUCcsICdJU08nLCAnSVQnLCAnTUZBJywgJ05DQScsICdQRFBMJywgJ1JCQUMnLCAnUlBPJywgJ1JUTycsICdTSUNPJywgJ1NPQycsICdVUkwnXSk7XG4gICAgICAgIHJldHVybiBsYWJlbC5zcGxpdCgnICcpLm1hcChwYXJ0ID0+IHtcbiAgICAgICAgICAgIGlmICghcGFydCB8fCBwYXJ0ID09PSAnLycpIHJldHVybiBwYXJ0O1xuICAgICAgICAgICAgY29uc3QgdXBwZXIgPSBwYXJ0LnRvVXBwZXJDYXNlKCk7XG4gICAgICAgICAgICByZXR1cm4gYWJicmV2aWF0aW9ucy5oYXModXBwZXIpID8gdXBwZXIgOiBwYXJ0LmNoYXJBdCgwKS50b1VwcGVyQ2FzZSgpICsgcGFydC5zbGljZSgxKS50b0xvd2VyQ2FzZSgpO1xuICAgICAgICB9KS5qb2luKCcgJyk7XG4gICAgfVxuXG4gICAgZnVuY3Rpb24gaXRlbUxhYmVsKHY6IHVua25vd24pOiBzdHJpbmcge1xuICAgICAgICBpZiAoIWlzT2JqZWN0KHYpKSByZXR1cm4gJyc7XG4gICAgICAgIGZvciAoY29uc3QgayBvZiBbJ25hbWUnLCAndGl0bGUnLCAncmVmX2lkJywgJ2xhYmVsJ10pIHtcbiAgICAgICAgICAgIGNvbnN0IG5hbWUgPSBwbGFpblRleHQodltrXSk7XG4gICAgICAgICAgICBpZiAobmFtZSkgcmV0dXJuIG5hbWUuc2xpY2UoMCwgOTUpO1xuICAgICAgICB9XG4gICAgICAgIHJldHVybiAnJztcbiAgICB9XG4gICAgZnVuY3Rpb24gc3VtbWFyaXplUmVjb3JkR3JvdXBzKHNvdXJjZTogdW5rbm93bik6IEdyb3VwW10ge1xuICAgICAgICBjb25zdCBmb3VuZCA9IG5ldyBNYXA8c3RyaW5nLCBHcm91cD4oKTtcbiAgICAgICAgY29uc3QgY2F0ZWdvcmllczogW1JlZ0V4cCwgc3RyaW5nXVtdID0gW1xuICAgICAgICAgICAgWy9mcmFtZXdvcmt8bGlicmFyL2ksICdGcmFtZXdvcmtzJ10sXG4gICAgICAgICAgICBbL2Fzc2V0L2ksICdBc3NldHMnXSxcbiAgICAgICAgICAgIFsvcG9saWMvaSwgJ1BvbGljaWVzJ10sXG4gICAgICAgICAgICBbL2FwcGxpZWQuY29udHJvbHxzYWZlZ3VhcmR8XmNvbnRyb2xzPyQvaSwgJ0NvbnRyb2xzJ10sXG4gICAgICAgICAgICBbL2V2aWRlbi9pLCAnRXZpZGVuY2UnXSxcbiAgICAgICAgICAgIFsvYXNzZXNzbWVudC9pLCAnQXNzZXNzbWVudHMnXSxcbiAgICAgICAgICAgIFsvcmlzay5zY2VuYXJpby9pLCAnUmlzayBzY2VuYXJpb3MnXSxcbiAgICAgICAgICAgIFsvZG9tYWlufGZvbGRlcnM/L2ksICdPcmdhbml6YXRpb25zIC8gZm9sZGVycyddXG4gICAgICAgIF07XG4gICAgICAgIGZ1bmN0aW9uIHdhbGsodjogdW5rbm93biwgZGVwdGg6IG51bWJlcikge1xuICAgICAgICAgICAgaWYgKGRlcHRoID4gNCB8fCAhaXNPYmplY3QodikpIHJldHVybjtcbiAgICAgICAgICAgIGZvciAoY29uc3QgW2tleSwgY2hpbGRdIG9mIE9iamVjdC5lbnRyaWVzKHYpKSB7XG4gICAgICAgICAgICAgICAgY29uc3QgdHlwZSA9IGNhdGVnb3JpZXMuZmluZCgoW3JlXSkgPT4gcmUudGVzdChrZXkpKT8uWzFdO1xuICAgICAgICAgICAgICAgIGlmICh0eXBlICYmIEFycmF5LmlzQXJyYXkoY2hpbGQpKSB7XG4gICAgICAgICAgICAgICAgICAgIGNvbnN0IGxhYmVsbGVkID0gY2hpbGQubWFwKGl0ZW1MYWJlbCkuZmlsdGVyKEJvb2xlYW4pO1xuICAgICAgICAgICAgICAgICAgICBpZiAoY2hpbGQubGVuZ3RoIHx8IGxhYmVsbGVkLmxlbmd0aCkge1xuICAgICAgICAgICAgICAgICAgICAgICAgY29uc3QgZ3JvdXAgPSBmb3VuZC5nZXQodHlwZSkgPz8geyBsYWJlbDogdHlwZSwgY291bnQ6IDAsIGV4YW1wbGVzOiBbXSB9O1xuICAgICAgICAgICAgICAgICAgICAgICAgZ3JvdXAuY291bnQgKz0gY2hpbGQubGVuZ3RoO1xuICAgICAgICAgICAgICAgICAgICAgICAgZm9yIChjb25zdCBuYW1lIG9mIGxhYmVsbGVkKSB7XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgaWYgKGdyb3VwLmV4YW1wbGVzLmxlbmd0aCA8IDMgJiYgIWdyb3VwLmV4YW1wbGVzLmluY2x1ZGVzKG5hbWUpKSBncm91cC5leGFtcGxlcy5wdXNoKG5hbWUpO1xuICAgICAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgICAgICAgICAgZm91bmQuc2V0KHR5cGUsIGdyb3VwKTtcbiAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgIH0gZWxzZSBpZiAoaXNPYmplY3QoY2hpbGQpKSB7XG4gICAgICAgICAgICAgICAgICAgIHdhbGsoY2hpbGQsIGRlcHRoICsgMSk7XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgfVxuICAgICAgICB9XG4gICAgICAgIHdhbGsoc291cmNlLCAwKTtcbiAgICAgICAgcmV0dXJuIFsuLi5mb3VuZC52YWx1ZXMoKV0uc2xpY2UoMCwgOCk7XG4gICAgfVxuICAgIGZ1bmN0aW9uIGNvbGxlY3RQbGFpbk5vdGVzKHNvdXJjZTogdW5rbm93bik6IHN0cmluZ1tdIHtcbiAgICAgICAgY29uc3Qgb3V0cHV0OiBzdHJpbmdbXSA9IFtdO1xuICAgICAgICBjb25zdCBtYXRjaGluZyA9IC9zdW1tYXJ5fG9iamVjdGl2ZXxyZWNvbW1lbmRhdGlvbnxuZXh0LnN0ZXB8cXVlc3Rpb258bWlzc2luZ3x3YXJuaW5nfGh1bWFuLnJldmlldy9pO1xuICAgICAgICBmdW5jdGlvbiB3YWxrKHY6IHVua25vd24sIGRlcHRoOiBudW1iZXIpIHtcbiAgICAgICAgICAgIGlmIChkZXB0aCA+IDMgfHwgb3V0cHV0Lmxlbmd0aCA+PSA1KSByZXR1cm47XG4gICAgICAgICAgICBpZiAoQXJyYXkuaXNBcnJheSh2KSkge1xuICAgICAgICAgICAgICAgIGZvciAoY29uc3QgY2hpbGQgb2Ygdi5zbGljZSgwLCA2KSkge1xuICAgICAgICAgICAgICAgICAgICBjb25zdCB0ZXh0ID0gcGxhaW5UZXh0KGNoaWxkKTtcbiAgICAgICAgICAgICAgICAgICAgaWYgKHRleHQgJiYgIW91dHB1dC5pbmNsdWRlcyh0ZXh0KSkgb3V0cHV0LnB1c2godGV4dCk7XG4gICAgICAgICAgICAgICAgICAgIGVsc2UgaWYgKGlzT2JqZWN0KGNoaWxkKSkgd2FsayhjaGlsZCwgZGVwdGggKyAxKTtcbiAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgcmV0dXJuO1xuICAgICAgICAgICAgfVxuICAgICAgICAgICAgaWYgKCFpc09iamVjdCh2KSkgcmV0dXJuO1xuICAgICAgICAgICAgZm9yIChjb25zdCBba2V5LCBjaGlsZF0gb2YgT2JqZWN0LmVudHJpZXModikpIHtcbiAgICAgICAgICAgICAgICBpZiAob3V0cHV0Lmxlbmd0aCA+PSA1KSByZXR1cm47XG4gICAgICAgICAgICAgICAgaWYgKCFtYXRjaGluZy50ZXN0KGtleSkpIGNvbnRpbnVlO1xuICAgICAgICAgICAgICAgIGNvbnN0IHRleHQgPSBwbGFpblRleHQoY2hpbGQpO1xuICAgICAgICAgICAgICAgIGlmICh0ZXh0ICYmICFvdXRwdXQuaW5jbHVkZXModGV4dCkpIG91dHB1dC5wdXNoKHRleHQpO1xuICAgICAgICAgICAgICAgIGVsc2UgaWYgKEFycmF5LmlzQXJyYXkoY2hpbGQpIHx8IGlzT2JqZWN0KGNoaWxkKSkgd2FsayhjaGlsZCwgZGVwdGggKyAxKTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgICAgICB3YWxrKHNvdXJjZSwgMCk7XG4gICAgICAgIHJldHVybiBvdXRwdXQ7XG4gICAgfVxuPC9zY3JpcHQ+XG5cbjxzdmVsdGU6aGVhZD5cbiAgICA8dGl0bGU+U0lDTyBBSSBOZXh0IOKAlCBBc3Nlc3NtZW50IFdvcmtzcGFjZTwvdGl0bGU+XG4gICAgPG1ldGEgbmFtZT1cImRlc2NyaXB0aW9uXCIgY29udGVudD1cIkdlbmVyYXRlIHN0cnVjdHVyZWQsIHJldmlld2FibGUgR1JDIGNhc2UgZHJhZnRzIHVzaW5nIHRoZSBleGlzdGluZyBTSUNPIHdvcmtzcGFjZS5cIiAvPlxuPC9zdmVsdGU6aGVhZD5cblxuPGRpdiBjbGFzcz1cIndvcmtzcGFjZVwiPlxuICAgIDxkaXYgY2xhc3M9XCJzaGVsbFwiPlxuICAgICAgICA8aGVhZGVyIGNsYXNzPVwidG9wYmFyXCI+XG4gICAgICAgICAgICA8ZGl2IGNsYXNzPVwibG9nb1wiPuKcpjwvZGl2PlxuICAgICAgICAgICAgPGRpdj48c3Ryb25nPlNJQ08gQUk8L3N0cm9uZz48c21hbGw+QVNTRVNTTUVOVCBXT1JLU1BBQ0U8L3NtYWxsPjwvZGl2PlxuICAgICAgICAgICAgPHNwYW4gY2xhc3M9XCJzY29wZS1waWxsXCI+VXNlcyB5b3VyIEdSQyBwZXJtaXNzaW9uczwvc3Bhbj5cbiAgICAgICAgPC9oZWFkZXI+XG5cbiAgICAgICAgPHNlY3Rpb24gY2xhc3M9XCJyZXBvcnRcIiBhcmlhLWxhYmVsPVwiQnVpbGQgYSBHUkMgY2FzZVwiIGlkPVwic3RhcnQtZ3JjLWNhc2VcIj5cbiAgICAgICAgICAgIDxkaXYgY2xhc3M9XCJyZXBvcnQtaGVhZFwiPlxuICAgICAgICAgICAgICAgIDxoMj5CdWlsZCBhIEdSQyBjYXNlPC9oMj5cbiAgICAgICAgICAgICAgICA8c3BhbiBjbGFzcz1cInN0YXR1cy1waWxsXCI+T25lIHdvcmtmbG93IMK3IFlvdXIgZXhpc3RpbmcgU0lDTyBHUkMgbGlicmFyeTwvc3Bhbj5cbiAgICAgICAgICAgIDwvZGl2PlxuICAgICAgICAgICAgPHAgY2xhc3M9XCJyZXBvcnQtaW50cm9cIj5FbnRlciB0aHJlZSBkZXRhaWxzIHRvIGdlbmVyYXRlIHN0cnVjdHVyZWQgR1JDIGNhc2UgZHJhZnRzIGFjcm9zcyBTSUNP4oCZcyAxNiBhY3Rpdml0aWVzLCBpbmNsdWRpbmcgcHJvcG9zZWQgYXNzZXRzLCByaXNrcywgY29udHJvbHMsIHBvbGljaWVzLCBldmlkZW5jZSByZXF1ZXN0cywgdGFza3MgYW5kIHJlcG9ydHMuIERyYWZ0cyByZW1haW4gdW5zYXZlZCBhbmQgZG8gbm90IGVzdGFibGlzaCBjb21wbGlhbmNlLjwvcD5cbiAgICAgICAgICAgIDxmb3JtIGNsYXNzPVwid29ya2Zsb3ctZm9ybVwiIG9uc3VibWl0PXsoZXZlbnQpID0+IHsgZXZlbnQucHJldmVudERlZmF1bHQoKTsgdm9pZCBnZW5lcmF0ZU5ld0Nhc2VEcmFmdHModHJ1ZSk7IH19PlxuICAgICAgICAgICAgICAgIDxsYWJlbD4xLiBPcmdhbml6YXRpb25cbiAgICAgICAgICAgICAgICAgICAgPGlucHV0IG5hbWU9XCJvcmdhbml6YXRpb25fbmFtZVwiIGJpbmQ6dmFsdWU9e29yZ2FuaXphdGlvbn0gZGlzYWJsZWQ9e2RyYWZ0ZWRDYXNlQnVzeX0gcmVxdWlyZWQgbWlubGVuZ3RoPVwiMlwiIG1heGxlbmd0aD1cIjE1MFwiIHBsYWNlaG9sZGVyPVwiT3JnYW5pemF0aW9uIG5hbWUgKG5ldyBvciBleGlzdGluZylcIiAvPlxuICAgICAgICAgICAgICAgIDwvbGFiZWw+XG4gICAgICAgICAgICAgICAgPGxhYmVsPjIuIEZyYW1ld29ya1xuICAgICAgICAgICAgICAgICAgICA8aW5wdXQgbmFtZT1cImZyYW1ld29ya19uYW1lXCIgYmluZDp2YWx1ZT17ZnJhbWV3b3JrU2VhcmNofSBkaXNhYmxlZD17ZHJhZnRlZENhc2VCdXN5fSByZXF1aXJlZCBtaW5sZW5ndGg9XCIyXCIgbWF4bGVuZ3RoPVwiMTUwXCIgcGxhY2Vob2xkZXI9XCJFbnRlciB0aGUgZXhhY3QgZnJhbWV3b3JrIG5hbWUgZnJvbSBTSUNP4oCZcyBsaWJyYXJ5XCIgLz5cbiAgICAgICAgICAgICAgICA8L2xhYmVsPlxuICAgICAgICAgICAgICAgIDxsYWJlbD4zLiBHUkMgY2FzZSBvYmplY3RpdmVcbiAgICAgICAgICAgICAgICAgICAgPHRleHRhcmVhIG5hbWU9XCJwcm9ibGVtXCIgYmluZDp2YWx1ZT17aW5zdHJ1Y3Rpb259IGRpc2FibGVkPXtkcmFmdGVkQ2FzZUJ1c3l9IHJlcXVpcmVkIG1pbmxlbmd0aD1cIjIwXCIgbWF4bGVuZ3RoPVwiNDAwMFwiIHJvd3M9XCI0XCIgcGxhY2Vob2xkZXI9XCJDcmVhdGUgYSBjb21wbGV0ZSBuZXcgR1JDIGNhc2Ugd2l0aCBwcm9wb3NlZCBhc3NldHMsIGNvbnRyb2xzLCByaXNrcywgcG9saWN5IGRyYWZ0cywgZXZpZGVuY2UgcmVxdWVzdHMsIHJlbWVkaWF0aW9uIGFuZCByZXBvcnRzLlwiPjwvdGV4dGFyZWE+XG4gICAgICAgICAgICAgICAgPC9sYWJlbD5cbiAgICAgICAgICAgICAgICB7I2lmIHF1YWxpdHlEcmFmdHMubGVuZ3RoID09PSAwfVxuICAgICAgICAgICAgICAgICAgICB7I2lmICFkcmFmdGVkQ2FzZUJ1c3kgJiYgcXVhbGl0eUlzc3Vlcy5sZW5ndGggJiYgZHJhZnRlZENhc2VTY29wZSA9PT0gcXVhbGl0eVNjb3BlS2V5KCl9XG4gICAgICAgICAgICAgICAgICAgICAgICA8YnV0dG9uIHR5cGU9XCJidXR0b25cIiBvbmNsaWNrPXsoKSA9PiB2b2lkIGdlbmVyYXRlTmV3Q2FzZURyYWZ0cyhmYWxzZSl9PlJlc3VtZSBmYWlsZWQgZHJhZnQgd2l0aCBhIGRpZmZlcmVudCBmb2N1czwvYnV0dG9uPlxuICAgICAgICAgICAgICAgICAgICB7OmVsc2V9XG4gICAgICAgICAgICAgICAgICAgICAgICA8YnV0dG9uIHR5cGU9XCJzdWJtaXRcIiBkaXNhYmxlZD17ZHJhZnRlZENhc2VCdXN5IHx8IGluc3RydWN0aW9uLnRyaW0oKS5sZW5ndGggPCAyMCB8fCAhb3JnYW5pemF0aW9uLnRyaW0oKSB8fCAhZnJhbWV3b3JrU2VhcmNoLnRyaW0oKX0+XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAge2RyYWZ0ZWRDYXNlQnVzeSA/ICdHZW5lcmF0aW5nIEdSQyBjYXNlIGRyYWZ0c+KApicgOiAnQnVpbGQgR1JDIGNhc2Ugd2l0aCBBSSd9XG4gICAgICAgICAgICAgICAgICAgICAgICA8L2J1dHRvbj5cbiAgICAgICAgICAgICAgICAgICAgey9pZn1cbiAgICAgICAgICAgICAgICB7L2lmfVxuICAgICAgICAgICAgICAgIDxsYWJlbCBjbGFzcz1cImNoZWNrcG9pbnQtdXBsb2FkXCI+UmVzdG9yZSBhbiBlYXJsaWVyIGRyYWZ0IHNlc3Npb24gZnJvbSBhIEpTT04gY2hlY2twb2ludFxuICAgICAgICAgICAgICAgICAgICA8aW5wdXQgdHlwZT1cImZpbGVcIiBhY2NlcHQ9XCIuanNvbixhcHBsaWNhdGlvbi9qc29uXCIgZGlzYWJsZWQ9e2RyYWZ0ZWRDYXNlQnVzeX0gb25jaGFuZ2U9eyhldmVudCkgPT4geyB2b2lkIGltcG9ydFF1YWxpdHlDaGVja3BvaW50KGV2ZW50KTsgfX0gLz5cbiAgICAgICAgICAgICAgICA8L2xhYmVsPlxuICAgICAgICAgICAgPC9mb3JtPlxuICAgICAgICAgICAgeyNpZiBkcmFmdGVkQ2FzZUVycm9yfTxwIGNsYXNzPVwibWVzc2FnZSBlcnJvclwiIHJvbGU9XCJhbGVydFwiPntkcmFmdGVkQ2FzZUVycm9yfTwvcD57L2lmfVxuICAgICAgICAgICAgeyNpZiBkcmFmdGVkQ2FzZU5vdGljZX08cCBjbGFzcz1cIm1lc3NhZ2VcIiByb2xlPVwic3RhdHVzXCI+e2RyYWZ0ZWRDYXNlTm90aWNlfTwvcD57L2lmfVxuICAgICAgICAgICAgeyNpZiBkcmFmdGVkQ2FzZUJ1c3kgfHwgcXVhbGl0eURyYWZ0cy5sZW5ndGggPiAwIHx8IGF1dGhvcml6ZWRGcmFtZXdvcmtTb3VyY2V9XG4gICAgICAgICAgICAgICAgPGRpdiBjbGFzcz1cImZyYW1ld29yay1jb3ZlcmFnZVwiIGFyaWEtbGFiZWw9XCJOZXcgU0lDTyBHUkMgY2FzZSBkcmFmdCByZXN1bHRzXCI+XG4gICAgICAgICAgICAgICAgICAgIDxkaXYgY2xhc3M9XCJmcmFtZXdvcmstY292ZXJhZ2UtdGl0bGVcIj5cbiAgICAgICAgICAgICAgICAgICAgICAgIDxoMz5HZW5lcmF0ZWQgR1JDIGNhc2UgZHJhZnRzIOKAlCB7cXVhbGl0eURyYWZ0cy5maWx0ZXIociA9PiByLnByb3ZlbmFuY2UgPT09ICdxd2VuX3F1YWxpdHlfc2luZ2xlX2F1dGhlbnRpY2F0ZWRfdjcnKS5sZW5ndGh9IG5ldyBBSS1nZW5lcmF0ZWQgZHJhZnRzPC9oMz5cbiAgICAgICAgICAgICAgICAgICAgICAgIDxzcGFuIGNsYXNzPVwiZm9vdG5vdGVcIj5ObyByZWNvcmRzIHNhdmVkIMK3IE5vIGNvbXBsaWFuY2UgdmVyZGljdDwvc3Bhbj5cbiAgICAgICAgICAgICAgICAgICAgPC9kaXY+XG4gICAgICAgICAgICAgICAgICAgIDxwIGNsYXNzPVwic291cmNlLW5vdGVcIj57ZnJhbWV3b3JrU291cmNlU3VtbWFyeSB8fCAnRnJhbWV3b3JrIGNhdGFsb2cgbm90IGxvYWRlZCB5ZXQuJ308L3A+XG4gICAgICAgICAgICAgICAgICAgIDxTaWNvR2VuZXJhdGVkQ2FzZSBpdGVtcz17cXVhbGl0eURyYWZ0c30gcGxhbj17dmFsaWRDb3ZlcmFnZVBsYW5Gb3JTY29wZSgpfSB7b3JnYW5pemF0aW9ufSBmcmFtZXdvcms9e2ZyYW1ld29ya1NlYXJjaH0gLz5cbiAgICAgICAgICAgICAgICAgICAgeyNpZiB2YWxpZENvdmVyYWdlUGxhbkZvclNjb3BlKCl9XG4gICAgICAgICAgICAgICAgICAgICAgICA8c2VjdGlvbiBjbGFzcz1cInJlcXVpcmVtZW50LWNvdmVyYWdlLXBsYW5cIiBhcmlhLWxhYmVsPVwiRnJhbWV3b3JrIHJlcXVpcmVtZW50IHJldmlldyBjb3ZlcmFnZVwiPlxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIDxoND5SZXF1aXJlbWVudC1ieS1yZXF1aXJlbWVudCByZXZpZXcgcGxhbjwvaDQ+XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgPHA+XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIDxzdHJvbmc+e3ZhbGlkQ292ZXJhZ2VQbGFuRm9yU2NvcGUoKT8uY292ZXJhZ2U/LnJlcXVpcmVtZW50c19jb25zaWRlcmVkX2Zvcl9yZXZpZXd9PC9zdHJvbmc+XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIHJlcXVpcmVtZW50cyBwcmVwYXJlZCBmb3IgcmV2aWV3IMK3XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIDxzdHJvbmc+e3NvdXJjZUxpbmtlZFJldmlld0NvdW50KCl9PC9zdHJvbmc+IHNvdXJjZS1saW5rZWQgUXdlbiByZXZpZXcgZHJhZnRzIMK3XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIDxzdHJvbmc+MDwvc3Ryb25nPiBldmlkZW5jZS12ZXJpZmllZCBjb21wbGlhbmNlIGRlY2lzaW9uc1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgIDwvcD5cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICA8cCBjbGFzcz1cImZvb3Rub3RlXCI+QWxsIHJlcXVpcmVtZW50IHdvcmsgaXRlbXMgc3RhcnQgYXMgTm90IGFzc2Vzc2VkLiBBcHBsaWNhYmlsaXR5IGFuZCBvcmdhbml6YXRpb24gZXZpZGVuY2UgYXJlIGF3YWl0aW5nIHJldmlldy4gQSB3b3JrIGl0ZW0gaXMgbm90IGFuIEFJLWdlbmVyYXRlZCBjb21wbGlhbmNlIGNvbmNsdXNpb24uPC9wPlxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIDxwIGNsYXNzPVwiZm9vdG5vdGVcIj5SaXNrIHJhdGluZ3M6IHBlbmRpbmcgdGVuYW50LWF1dGhvcml6ZWQgcmlzayBhc3Nlc3NtZW50IGFuZCBjb25maWd1cmVkIFNJQ08gcmlzayBtYXRyaXguIFRoZSBBSSBjYW5ub3QgY2FsY3VsYXRlIGN1cnJlbnQgb3IgcmVzaWR1YWwgcmlzayBmcm9tIGEgZnJhbWV3b3JrIG5hbWUgYWxvbmUuPC9wPlxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIDxwIGNsYXNzPVwiZm9vdG5vdGVcIj5UaGUgY2FzZSBib2FyZCBkaXNwbGF5cyBhY2NlcHRlZCBRd2VuIGNvbnRlbnQgb25seS4gUGxhbm5lZCByZWNvcmRzIGFuZCBhbiB1bmFwcHJvdmVkIG1hdHJpeCBkbyBub3QgZXN0YWJsaXNoIGltcGxlbWVudGF0aW9uIG9yIGNvbXBsaWFuY2UuPC9wPlxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIDxidXR0b24gdHlwZT1cImJ1dHRvblwiIG9uY2xpY2s9e2Rvd25sb2FkQ292ZXJhZ2VQbGFufT5Eb3dubG9hZCBmdWxsIHJlcXVpcmVtZW50IHdvcmsgcGxhbjwvYnV0dG9uPlxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIDxkZXRhaWxzPlxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA8c3VtbWFyeT5SZXZpZXcgcmVxdWlyZW1lbnQgd29yayBxdWV1ZSAoe3ZhbGlkQ292ZXJhZ2VQbGFuRm9yU2NvcGUoKT8ucmVxdWlyZW1lbnRfd29ya19pdGVtcz8ubGVuZ3RoID8/IDB9KTwvc3VtbWFyeT5cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgPG9sIGNsYXNzPVwicmVxdWlyZW1lbnQtd29yay1pdGVtc1wiPlxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgeyNlYWNoIChzaG93QWxsQ292ZXJhZ2VJdGVtcyA/IHZhbGlkQ292ZXJhZ2VQbGFuRm9yU2NvcGUoKT8ucmVxdWlyZW1lbnRfd29ya19pdGVtcyA6IHZhbGlkQ292ZXJhZ2VQbGFuRm9yU2NvcGUoKT8ucmVxdWlyZW1lbnRfd29ya19pdGVtcz8uc2xpY2UoMCwgMTIpKSA/PyBbXSBhcyBpdGVtIChpdGVtLnJlcXVpcmVtZW50X2lkKX1cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA8bGk+XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIDxzdHJvbmc+e2l0ZW0ucmVmZXJlbmNlfTwvc3Ryb25nPjoge2l0ZW0ucmVxdWlyZW1lbnRfbmFtZSB8fCBpdGVtLmRlc2NyaXB0aW9ufVxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA8c3BhbiBjbGFzcz1cImZvb3Rub3RlXCI+IMK3IE5vdCBhc3Nlc3NlZCDCtyBFdmlkZW5jZSBuZWVkZWQgwrcgSHVtYW4gcmV2aWV3IHJlcXVpcmVkPC9zcGFuPlxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIDwvbGk+XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICB7L2VhY2h9XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIDwvb2w+XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIHsjaWYgIXNob3dBbGxDb3ZlcmFnZUl0ZW1zICYmICh2YWxpZENvdmVyYWdlUGxhbkZvclNjb3BlKCk/LnJlcXVpcmVtZW50X3dvcmtfaXRlbXM/Lmxlbmd0aCA/PyAwKSA+IDEyfVxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgPGJ1dHRvbiB0eXBlPVwiYnV0dG9uXCIgb25jbGljaz17KCkgPT4geyBzaG93QWxsQ292ZXJhZ2VJdGVtcyA9IHRydWU7IH19PlNob3cgcmVtYWluaW5nIHJlcXVpcmVtZW50czwvYnV0dG9uPlxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICB7OmVsc2UgaWYgc2hvd0FsbENvdmVyYWdlSXRlbXN9XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA8YnV0dG9uIHR5cGU9XCJidXR0b25cIiBvbmNsaWNrPXsoKSA9PiB7IHNob3dBbGxDb3ZlcmFnZUl0ZW1zID0gZmFsc2U7IH19PlNob3cgZmlyc3QgMTIgb25seTwvYnV0dG9uPlxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICB7L2lmfVxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIDwvZGV0YWlscz5cbiAgICAgICAgICAgICAgICAgICAgICAgIDwvc2VjdGlvbj5cbiAgICAgICAgICAgICAgICAgICAgezplbHNlIGlmIGRyYWZ0ZWRDYXNlQnVzeX1cbiAgICAgICAgICAgICAgICAgICAgICAgIDxwIGNsYXNzPVwiZm9vdG5vdGVcIj5QcmVwYXJpbmcgYXV0aG9yaXplZCBmcmFtZXdvcmsgY292ZXJhZ2UgYmVmb3JlIG1vZGVsIGRyYWZ0aW5nLjwvcD5cbiAgICAgICAgICAgICAgICAgICAgey9pZn1cbiAgICAgICAgICAgICAgICAgICAgeyNpZiBjb3ZlcmFnZVBsYW5FcnJvcn08cCBjbGFzcz1cIm1lc3NhZ2UgZXJyb3JcIiByb2xlPVwiYWxlcnRcIj57Y292ZXJhZ2VQbGFuRXJyb3J9PC9wPnsvaWZ9XG5cbiAgICAgICAgICAgICAgICAgICAgPHAgY2xhc3M9XCJmb290bm90ZVwiPkZyYW1ld29yaywgYXNzZXNzbWVudCBjaGFydGVyIGFuZCBidXNpbmVzcyBzY29wZSBhcmUgaW5wdXRzIHRvIGNvbmZpcm0sIG5vdCBtb2RlbC1nZW5lcmF0ZWQgYXNzZXNzbWVudCByZXN1bHRzLjwvcD5cbiAgICAgICAgICAgICAgICAgICAgPGRpdiBjbGFzcz1cImZyYW1ld29yay1tZXRlclwiPjxkaXYgY2xhc3M9XCJmcmFtZXdvcmstbWV0ZXItZmlsbFwiIHN0eWxlPXtgd2lkdGg6ICR7TWF0aC5yb3VuZChnZW5lcmF0aW9uT3JkZXIuZmlsdGVyKG4gPT4gcXVhbGl0eURyYWZ0cy5zb21lKHIgPT4gci5hY3Rpdml0eV9udW1iZXIgPT09IG4pKS5sZW5ndGggLyBmaXJzdFBhc3NUYXJnZXQgKiAxMDApfSVgfT48L2Rpdj48L2Rpdj5cbiAgICAgICAgICAgICAgICAgICAgPHAgY2xhc3M9XCJmb290bm90ZVwiPkFjdGl2aXRpZXMgd2l0aCBkcmFmdHM6IHtnZW5lcmF0aW9uT3JkZXIuZmlsdGVyKG4gPT4gcXVhbGl0eURyYWZ0cy5zb21lKHIgPT4gci5hY3Rpdml0eV9udW1iZXIgPT09IG4pKS5sZW5ndGh9L3tmaXJzdFBhc3NUYXJnZXR9LiBTY2hlZHVsZWQgUXdlbiByZWNvcmRzOiB7dmFsaWRDb3ZlcmFnZVBsYW5Gb3JTY29wZSgpPy5nZW5lcmF0aW9uX3N1bW1hcnk/LnBsYW5uZWRfcXdlbl9kZXRhaWxfZHJhZnRzID8/ICdQbGFubmluZyBwZW5kaW5nJ30uIEVhY2ggcmVxdWlyZW1lbnQgcmV2aWV3IHJlbWFpbnMgdW5hc3Nlc3NlZCB1bnRpbCBldmlkZW5jZSByZXZpZXcuPC9wPlxuICAgICAgICAgICAgICAgICAgICA8ZGl2IGNsYXNzPVwiZnJhbWV3b3JrLWFjdGlvbnNcIj5cbiAgICAgICAgICAgICAgICAgICAgICAgIHsjaWYgZHJhZnRlZENhc2VCdXN5fVxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIDxzcGFuIGNsYXNzPVwiZm9vdG5vdGVcIj5HZW5lcmF0aW5nIGFjdGl2aXR5IHtjdXJyZW50R2VuZXJhdGluZ0FjdGl2aXR5fSBvZiAxNiDCtyBSZXZpZXdpbmcgZWFjaCBkcmFmdCBpbmRpdmlkdWFsbHkuPC9zcGFuPlxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIDxidXR0b24gdHlwZT1cImJ1dHRvblwiIG9uY2xpY2s9eygpID0+IHsgc3RvcEFmdGVyUGhhc2UgPSB0cnVlOyB9fT5QYXVzZSBhZnRlciBjdXJyZW50IHJlcXVlc3Q8L2J1dHRvbj5cbiAgICAgICAgICAgICAgICAgICAgICAgIHs6ZWxzZX1cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICB7I2lmIGhhc1BlbmRpbmdHZW5lcmF0aW9uKCl9XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIDxidXR0b24gdHlwZT1cImJ1dHRvblwiIG9uY2xpY2s9eygpID0+IHZvaWQgZ2VuZXJhdGVOZXdDYXNlRHJhZnRzKGZhbHNlKX0+UmVzdW1lIGF1dG9tYXRpYyBnZW5lcmF0aW9uPC9idXR0b24+XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgey9pZn1cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICA8YnV0dG9uIHR5cGU9XCJidXR0b25cIiBvbmNsaWNrPXsoKSA9PiB2b2lkIGdlbmVyYXRlTmV3Q2FzZURyYWZ0cyh0cnVlKX0+U3RhcnQgYSBuZXcgY2FzZTwvYnV0dG9uPlxuICAgICAgICAgICAgICAgICAgICAgICAgey9pZn1cbiAgICAgICAgICAgICAgICAgICAgICAgIHsjaWYgcXVhbGl0eURyYWZ0cy5sZW5ndGh9XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgPGJ1dHRvbiB0eXBlPVwiYnV0dG9uXCIgb25jbGljaz17ZG93bmxvYWRRdWFsaXR5Q2hlY2twb2ludH0+RG93bmxvYWQgY2hlY2twb2ludDwvYnV0dG9uPlxuICAgICAgICAgICAgICAgICAgICAgICAgey9pZn1cbiAgICAgICAgICAgICAgICAgICAgICAgIHsjaWYgYXV0aG9yaXplZEZyYW1ld29ya1NvdXJjZT8uY29tcGxldGVfc291cmNlX3NuYXBzaG90fVxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIDxidXR0b24gdHlwZT1cImJ1dHRvblwiIG9uY2xpY2s9e2Rvd25sb2FkQXV0aG9yaXplZFJlcXVpcmVtZW50U291cmNlfT5Eb3dubG9hZCBmcmFtZXdvcmsgcmVxdWlyZW1lbnRzPC9idXR0b24+XG4gICAgICAgICAgICAgICAgICAgICAgICB7L2lmfVxuICAgICAgICAgICAgICAgICAgICA8L2Rpdj5cbiAgICAgICAgICAgICAgICAgICAgeyNpZiBsYXN0QXR0ZW1wdEluZm99PHAgY2xhc3M9XCJmb290bm90ZVwiIHJvbGU9XCJzdGF0dXNcIj57bGFzdEF0dGVtcHRJbmZvfTwvcD57L2lmfVxuICAgICAgICAgICAgICAgICAgICB7I2lmIGF0dGVtcHRIaXN0b3J5Lmxlbmd0aH1cbiAgICAgICAgICAgICAgICAgICAgICAgIDxkZXRhaWxzIGNsYXNzPVwiZ2VuZXJhdGlvbi10aW1pbmdcIj5cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICA8c3VtbWFyeT5HZW5lcmF0aW9uIHJlcXVlc3QgaGlzdG9yeSAoe2F0dGVtcHRIaXN0b3J5Lmxlbmd0aH0gbW9zdCByZWNlbnQpPC9zdW1tYXJ5PlxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIDx1bD5cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgeyNlYWNoIFsuLi5hdHRlbXB0SGlzdG9yeV0ucmV2ZXJzZSgpIGFzIGF0dGVtcHR9XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA8bGk+QWN0aXZpdHkge2F0dGVtcHQuYWN0aXZpdHl9LCBkcmFmdCB7YXR0ZW1wdC5pbmRleH06IHthdHRlbXB0Lm91dGNvbWUgPT09ICdhY2NlcHRlZCcgPyAnQWNjZXB0ZWQnIDogJ1JlamVjdGVkJ30gwrcge2F0dGVtcHQuZWxhcHNlZF9zZWNvbmRzfXMgwrcge2F0dGVtcHQuZGV0YWlsfTwvbGk+XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIHsvZWFjaH1cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICA8L3VsPlxuICAgICAgICAgICAgICAgICAgICAgICAgPC9kZXRhaWxzPlxuICAgICAgICAgICAgICAgICAgICB7L2lmfVxuICAgICAgICAgICAgICAgICAgICB7I2lmIGxvY2FsQ2hlY2twb2ludEluZm99PHAgY2xhc3M9XCJmb290bm90ZVwiPntsb2NhbENoZWNrcG9pbnRJbmZvfTwvcD57L2lmfVxuICAgICAgICAgICAgICAgICAgICB7I2lmIHF1YWxpdHlJc3N1ZXMubGVuZ3RofTxwIGNsYXNzPVwiZm9vdG5vdGVcIj5GYWlsZWQgYXR0ZW1wdHM6IHtxdWFsaXR5SXNzdWVzLmxlbmd0aH0uIExhc3Q6IHtxdWFsaXR5SXNzdWVzW3F1YWxpdHlJc3N1ZXMubGVuZ3RoLTFdfTwvcD57L2lmfVxuICAgICAgICAgICAgICAgICAgICB7I2VhY2ggcXVhbGl0eURyYWZ0cyBhcyBpdGVtIChpdGVtLmRyYWZ0LmRyYWZ0X3JlZmVyZW5jZSl9XG4gICAgICAgICAgICAgICAgICAgICAgICA8YXJ0aWNsZSBjbGFzcz1cInNpY28tY2FzZS1kcmFmdFwiPlxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIDxoND57aXRlbS5kcmFmdC50aXRsZX0gPHNwYW4gY2xhc3M9XCJmb290bm90ZVwiPntpdGVtLmRyYWZ0LmRyYWZ0X3JlZmVyZW5jZX08L3NwYW4+PC9oND5cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICA8cCBjbGFzcz1cImZvb3Rub3RlXCI+QWN0aXZpdHkge2l0ZW0uYWN0aXZpdHlfbnVtYmVyfToge2l0ZW0uYWN0aXZpdHlfbmFtZX0gwrcgU0lDTyBNb2R1bGU6IHtkaXNwbGF5RmllbGRMYWJlbChpdGVtLnRhcmdldF9leGlzdGluZ19zaWNvX21vZGVsKX0gwrcge2l0ZW0ucHJvdmVuYW5jZSA9PT0gJ3F3ZW5fcXVhbGl0eV9zaW5nbGVfYXV0aGVudGljYXRlZF92NycgPyAnQUktZ2VuZXJhdGVkIGRyYWZ0IMK3IFBlbmRpbmcgdmVyaWZpY2F0aW9uJyA6ICdJbXBvcnRlZCBkcmFmdCDCtyBSZXZpZXcgcmVxdWlyZWQnfTwvcD5cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICA8cD57aXRlbS5kcmFmdC5jb250ZW50fTwvcD5cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICA8ZGw+XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIHsjZWFjaCBpdGVtLmRyYWZ0LnByb3Bvc2VkX2F0dHJpYnV0ZXMgPz8gW10gYXMgYXR0cn1cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIDxkaXY+PGR0PntkaXNwbGF5RmllbGRMYWJlbChhdHRyLmZpZWxkKX08L2R0PjxkZD57YXR0ci5wcm9wb3NlZF92YWx1ZX08L2RkPjwvZGl2PlxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICB7L2VhY2h9XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgPC9kbD5cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICA8cD48c3Ryb25nPkV2aWRlbmNlIHRvIFJlcXVlc3Q6PC9zdHJvbmc+IHtpdGVtLmRyYWZ0LmV2aWRlbmNlX3JlcXVlc3R9PC9wPlxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIDxwPjxzdHJvbmc+VmVyaWZpY2F0aW9uIFF1ZXN0aW9uOjwvc3Ryb25nPiB7aXRlbS5kcmFmdC52ZXJpZmljYXRpb25fcXVlc3Rpb259PC9wPlxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIHsjaWYgaXRlbS5kcmFmdC5yZWxhdGVkX2RyYWZ0X3JlZmVyZW5jZXM/Lmxlbmd0aH1cbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgPHA+PHN0cm9uZz5SZWxhdGVkIERyYWZ0czo8L3N0cm9uZz4ge2l0ZW0uZHJhZnQucmVsYXRlZF9kcmFmdF9yZWZlcmVuY2VzLmpvaW4oJywgJyl9PC9wPlxuICAgICAgICAgICAgICAgICAgICAgICAgICAgIHsvaWZ9XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgPHAgY2xhc3M9XCJmb290bm90ZVwiPkh5cG90aGV0aWNhbCwgdW5zYXZlZC4gTm90IHZlcmlmaWVkIG9yZ2FuaXphdGlvbiBkYXRhIG9yIHByb29mIG9mIGNvbXBsaWFuY2UuPC9wPlxuICAgICAgICAgICAgICAgICAgICAgICAgPC9hcnRpY2xlPlxuICAgICAgICAgICAgICAgICAgICB7L2VhY2h9XG4gICAgICAgICAgICAgICAgPC9kaXY+XG4gICAgICAgICAgICB7L2lmfVxuICAgICAgICAgICAgPHAgY2xhc3M9XCJmb290bm90ZVwiPlRoZXNlIGFyZSBwcm9wb3NlZCBkcmFmdHMgc3RydWN0dXJlZCBhcm91bmQgZXhpc3RpbmcgU0lDTyBHUkMgbW9kZWxzLiBUaGV5IGhhdmUgbm90IGJlZW4gdmVyaWZpZWQgYWdhaW5zdCB0aGUgb3JnYW5pemF0aW9uIG9yIHNhdmVkIGFzIGJ1c2luZXNzIHJlY29yZHMuPC9wPlxuICAgICAgICA8L3NlY3Rpb24+XG4gICAgICAgIDxmb290ZXI+U0lDTyBBSSDCtyBPbmUgY2FzZS1idWlsZGluZyB3b3JrZmxvdyDCtyBBSS1nZW5lcmF0ZWQgR1JDIGRyYWZ0cyBhY3Jvc3MgMTYgYWN0aXZpdGllcyDCtyBObyBkYXRhYmFzZSB3cml0ZXMuPC9mb290ZXI+XG4gICAgPC9kaXY+XG48L2Rpdj5cblxuPHN0eWxlPlxuLmxpdmUtcXdlbi1jYXNle21hcmdpbjoxOHB4IDA7cGFkZGluZzoyMHB4O2JvcmRlcjoxcHggc29saWQgIzJhOWRiNjtib3JkZXItcmFkaXVzOjE1cHg7YmFja2dyb3VuZDpsaW5lYXItZ3JhZGllbnQoMTM1ZGVnLCMxMTJiM2MgMCUsIzEwMWMzMCA3MCUpO2NvbG9yOiNlZWZhZmZ9XG4ubGl2ZS1xd2VuLWNhc2UtaGVhZHtkaXNwbGF5OmZsZXg7YWxpZ24taXRlbXM6ZmxleC1zdGFydDtqdXN0aWZ5LWNvbnRlbnQ6c3BhY2UtYmV0d2VlbjtnYXA6MTZweDtmbGV4LXdyYXA6d3JhcH1cbi5saXZlLXF3ZW4tY2FzZSBoNHttYXJnaW46MCAwIDhweDtmb250LXNpemU6MjBweDtjb2xvcjojZmZmfVxuLmxpdmUtcXdlbi1jYXNlLWhlYWQgcHttYXJnaW46NHB4IDA7Y29sb3I6I2QyZTNlZX1cbi5saXZlLXF3ZW4tdGFne3BhZGRpbmc6NnB4IDEwcHg7Ym9yZGVyOjFweCBzb2xpZCAjMzNiY2QwO2JvcmRlci1yYWRpdXM6MjBweDtmb250LXNpemU6MTJweDtjb2xvcjojOTNlZWZmO3doaXRlLXNwYWNlOm5vd3JhcH1cbi5saXZlLXF3ZW4tc3RhdHN7bWFyZ2luOjE2cHggMDtkaXNwbGF5OmdyaWQ7Z3JpZC10ZW1wbGF0ZS1jb2x1bW5zOnJlcGVhdChhdXRvLWZpdCxtaW5tYXgoMTMwcHgsMWZyKSk7Z2FwOjEwcHh9XG4ubGl2ZS1xd2VuLXN0YXRzPmRpdntwYWRkaW5nOjE1cHg7YmFja2dyb3VuZDojMGIxYjJlO2JvcmRlcjoxcHggc29saWQgIzJkNGU2Mjtib3JkZXItcmFkaXVzOjEwcHg7ZGlzcGxheTpmbGV4O2ZsZXgtZGlyZWN0aW9uOmNvbHVtbjtnYXA6NnB4fVxuLmxpdmUtcXdlbi1zdGF0cyBzdHJvbmd7Zm9udC1zaXplOjI2cHg7Y29sb3I6I2EwZjJmZn1cbi5saXZlLXF3ZW4tc3RhdHMgc3Bhbntmb250LXNpemU6MTJweDtjb2xvcjojYzJkNGUxfVxuLmxpdmUtcXdlbi1ncm91cHN7ZGlzcGxheTpncmlkO2dyaWQtdGVtcGxhdGUtY29sdW1uczpyZXBlYXQoYXV0by1maXQsbWlubWF4KG1pbigxMDAlLDMyMHB4KSwxZnIpKTtnYXA6MTJweDthbGlnbi1pdGVtczpzdGFydH1cbi5saXZlLXF3ZW4tZ3JvdXB7Ym9yZGVyOjFweCBzb2xpZCAjM2E1MzZhO2JvcmRlci1yYWRpdXM6MTJweDtiYWNrZ3JvdW5kOiMwZDIwMzE7bWluLXdpZHRoOjB9XG4ubGl2ZS1xd2VuLWdyb3VwIHN1bW1hcnl7cGFkZGluZzoxMnB4O2N1cnNvcjpwb2ludGVyO2Rpc3BsYXk6ZmxleDtqdXN0aWZ5LWNvbnRlbnQ6c3BhY2UtYmV0d2VlbjtnYXA6MTJweDthbGlnbi1pdGVtczpjZW50ZXJ9XG4ubGl2ZS1xd2VuLWdyb3VwIHN1bW1hcnk+c3Bhbnt0ZXh0LXRyYW5zZm9ybTpjYXBpdGFsaXplO2ZvbnQtd2VpZ2h0OjY1MH1cbi5saXZlLXF3ZW4tZ3JvdXAgc3VtbWFyeT5zdHJvbmd7Y29sb3I6IzliZGVlZDtmb250LXNpemU6MTJweDt3aGl0ZS1zcGFjZTpub3dyYXB9XG4ubGl2ZS1xd2VuLXJlY29yZHtib3JkZXItdG9wOjFweCBzb2xpZCAjMmQ0YTYwO3BhZGRpbmc6MTNweH1cbi5saXZlLXF3ZW4tcmVjb3JkIGg1e2ZvbnQtc2l6ZToxNXB4O2NvbG9yOiNiMGVmZmY7bWFyZ2luOjAgMCA4cHh9XG4ubGl2ZS1xd2VuLXJlY29yZCBwe2ZvbnQtc2l6ZToxM3B4O2xpbmUtaGVpZ2h0OjEuNTU7b3ZlcmZsb3ctd3JhcDphbnl3aGVyZX1cbi5saXZlLXF3ZW4tcmVjb3JkIGRse21hcmdpbjo4cHggMDtkaXNwbGF5OmdyaWQ7Z2FwOjhweH1cbi5saXZlLXF3ZW4tcmVjb3JkIGRsPmRpdntkaXNwbGF5OmdyaWQ7Z2FwOjNweH1cbi5saXZlLXF3ZW4tcmVjb3JkIGR0e2ZvbnQtc2l6ZToxMXB4O2NvbG9yOiM4YWI2Y2U7dGV4dC10cmFuc2Zvcm06Y2FwaXRhbGl6ZX1cbi5saXZlLXF3ZW4tcmVjb3JkIGRke2ZvbnQtc2l6ZToxM3B4O21hcmdpbjowO292ZXJmbG93LXdyYXA6YW55d2hlcmV9XG4gICAgLndvcmtzcGFjZXttaW4taGVpZ2h0OjEwMHZoO2JhY2tncm91bmQ6cmFkaWFsLWdyYWRpZW50KGVsbGlwc2UgYXQgNjAlIDAlLCMxMjM5NTAgMCx0cmFuc3BhcmVudCA0NiUpLCMwODBmMjA7Y29sb3I6I2U5ZjRmZjtmb250LWZhbWlseTppbmhlcml0fVxuICAgIC5zaGVsbHttYXgtd2lkdGg6MTA2MHB4O21hcmdpbjphdXRvO3BhZGRpbmc6MzRweCAyOHB4IDY1cHh9XG4gICAgLnRvcGJhcntkaXNwbGF5OmZsZXg7Z2FwOjEycHg7YWxpZ24taXRlbXM6Y2VudGVyfS5sb2dve2Rpc3BsYXk6Z3JpZDtwbGFjZS1pdGVtczpjZW50ZXI7d2lkdGg6NDJweDtoZWlnaHQ6NDJweDtib3JkZXI6MXB4IHNvbGlkICM0MzhjOGM7Ym9yZGVyLXJhZGl1czoxMnB4O2JhY2tncm91bmQ6IzEyNDA0YTtmb250LXNpemU6MjVweDtjb2xvcjojNzhlMmNlfS50b3BiYXIgc3Ryb25ne2Rpc3BsYXk6YmxvY2s7Zm9udC1zaXplOjE3cHg7bGV0dGVyLXNwYWNpbmc6LjA4ZW19LnRvcGJhciBzbWFsbHtmb250LXNpemU6MTBweDtsZXR0ZXItc3BhY2luZzouMTRlbTtjb2xvcjojYTJiN2NifS5zY29wZS1waWxsLC5zdGF0dXMtcGlsbHttYXJnaW4tbGVmdDphdXRvO2ZvbnQtc2l6ZToxMnB4O2NvbG9yOiNhM2VhZGM7Ym9yZGVyOjFweCBzb2xpZCAjMzc2MzZhO2JvcmRlci1yYWRpdXM6MzBweDtwYWRkaW5nOjhweCAxMnB4fVxuICAgIC5oZXJve21hcmdpbjo2NXB4IGF1dG8gMzJweDttYXgtd2lkdGg6NzYwcHg7dGV4dC1hbGlnbjpjZW50ZXJ9LmV5ZWJyb3d7Zm9udC1zaXplOjExcHg7bGV0dGVyLXNwYWNpbmc6LjE2ZW07Y29sb3I6IzcyZDljNDtmb250LXdlaWdodDo4MDB9Lmhlcm8gaDF7Zm9udC1zaXplOmNsYW1wKDMycHgsNXZ3LDU2cHgpO2xldHRlci1zcGFjaW5nOi0uMDRlbTtsaW5lLWhlaWdodDoxLjEzO21hcmdpbjoxNHB4IDB9Lmhlcm8gZW17Zm9udC1zdHlsZTpub3JtYWw7Y29sb3I6IzcxZTBjYn0uaGVybz5wOmxhc3QtY2hpbGR7Y29sb3I6I2FkYmVkMTtsaW5lLWhlaWdodDoxLjc1fVxuICAgIC5wcm9tcHQtZm9ybXtiYWNrZ3JvdW5kOiMxMjFmMzQ7Ym9yZGVyOjFweCBzb2xpZCAjMzU1MTY2O2JvcmRlci1yYWRpdXM6MThweDtwYWRkaW5nOjE2cHg7Ym94LXNoYWRvdzowIDIwcHggNjBweCAjMDAwNX0ucHJvbXB0LWZvcm0gdGV4dGFyZWF7d2lkdGg6MTAwJTtib3gtc2l6aW5nOmJvcmRlci1ib3g7Ym9yZGVyOjA7cmVzaXplOnZlcnRpY2FsO2JhY2tncm91bmQ6dHJhbnNwYXJlbnQ7Y29sb3I6I2VkZjZmZjtwYWRkaW5nOjE0cHg7Zm9udDppbmhlcml0O2ZvbnQtc2l6ZToxNXB4O2xpbmUtaGVpZ2h0OjEuNzttaW4taGVpZ2h0OjE0NXB4O291dGxpbmU6bm9uZX0ucHJvbXB0LWZvcm0gdGV4dGFyZWE6OnBsYWNlaG9sZGVye2NvbG9yOiM4ZWE0YmR9LmNvbnRleHQtcm93e2JvcmRlci10b3A6MXB4IHNvbGlkICMzMTQzNTk7cGFkZGluZzoxNHB4IDEycHggMTBweH0uY29udGV4dC1yb3cgbGFiZWx7ZGlzcGxheTpibG9jaztjb2xvcjojY2RlMGViO2ZvbnQtc2l6ZToxM3B4O2ZvbnQtd2VpZ2h0OjcwMDttYXJnaW4tYm90dG9tOjhweH0uY29udGV4dC1yb3cgaW5wdXR7YmFja2dyb3VuZDojMGUxOTJiO2NvbG9yOiNmNGY4ZmY7Ym9yZGVyOjFweCBzb2xpZCAjNDI2MTc2O2JvcmRlci1yYWRpdXM6OXB4O3BhZGRpbmc6MTFweCAxMnB4O3dpZHRoOjEwMCU7Ym94LXNpemluZzpib3JkZXItYm94O2ZvbnQ6aW5oZXJpdDtmb250LXNpemU6MTRweH0uaGVscHtkaXNwbGF5OmJsb2NrO2NvbG9yOiM5MGE5YzI7Zm9udC1zaXplOjEycHg7bWFyZ2luLXRvcDo3cHh9LnByb21wdC1mb290ZXJ7ZGlzcGxheTpmbGV4O2FsaWduLWl0ZW1zOmNlbnRlcjtqdXN0aWZ5LWNvbnRlbnQ6c3BhY2UtYmV0d2VlbjtnYXA6MTJweDtwYWRkaW5nOjEzcHggMTBweCAzcHg7Y29sb3I6IzlkYjRjODtmb250LXNpemU6MTJweH0ucHJvbXB0LWZvb3RlciBidXR0b257YmFja2dyb3VuZDojNzNlMmM5O2JvcmRlcjowO2JvcmRlci1yYWRpdXM6MTBweDtjb2xvcjojMDkyYTMxO2ZvbnQ6aW5oZXJpdDtmb250LXdlaWdodDo3NTA7Zm9udC1zaXplOjE0cHg7cGFkZGluZzoxM3B4IDIycHg7Y3Vyc29yOnBvaW50ZXJ9LnByb21wdC1mb290ZXIgYnV0dG9uOmRpc2FibGVke29wYWNpdHk6LjU7Y3Vyc29yOm5vdC1hbGxvd2VkfVxuICAgIC5leGFtcGxlc3ttYXJnaW4tdG9wOjQycHh9LmV4YW1wbGVzIGgye2ZvbnQtc2l6ZToxNXB4O2NvbG9yOiNhYWJkZDA7Zm9udC13ZWlnaHQ6NTAwfS5leGFtcGxlLWdyaWR7ZGlzcGxheTpncmlkO2dyaWQtdGVtcGxhdGUtY29sdW1uczpyZXBlYXQoMixtaW5tYXgoMCwxZnIpKTtnYXA6MTJweH0uZXhhbXBsZS1ncmlkIGJ1dHRvbntjdXJzb3I6cG9pbnRlcjtjb2xvcjojZGJlOWY2O3RleHQtYWxpZ246bGVmdDtiYWNrZ3JvdW5kOiMxNDI0M2I7Ym9yZGVyOjFweCBzb2xpZCAjMzU0YjY1O2JvcmRlci1yYWRpdXM6MTNweDtwYWRkaW5nOjE3cHg7Zm9udDppbmhlcml0O2ZvbnQtc2l6ZToxM3B4O2xpbmUtaGVpZ2h0OjEuNTV9LmV4YW1wbGUtZ3JpZCBidXR0b24gc3Bhbntjb2xvcjojN2RlNGQwO21hcmdpbi1sZWZ0OjhweH0uZXhhbXBsZS1ncmlkIGJ1dHRvbjpob3Zlcntib3JkZXItY29sb3I6IzY3YzhiOH1cbiAgICAubWVzc2FnZXttYXJnaW4tdG9wOjI1cHg7cGFkZGluZzoxN3B4O2JvcmRlci1yYWRpdXM6MTJweDtib3JkZXI6MXB4IHNvbGlkICMzZDY1NzI7Y29sb3I6I2NmZTZlZDtiYWNrZ3JvdW5kOiMxODM2NDN9Lm1lc3NhZ2UuZXJyb3J7Ym9yZGVyLWNvbG9yOiM5NzVjNTg7YmFja2dyb3VuZDojM2EyMjI2fS5tZXNzYWdlIHB7bWFyZ2luLWJvdHRvbTowfS5yZXBvcnR7bWFyZ2luLXRvcDo1MHB4fS5yZXBvcnQtaGVhZHtkaXNwbGF5OmZsZXg7anVzdGlmeS1jb250ZW50OnNwYWNlLWJldHdlZW47YWxpZ24taXRlbXM6Y2VudGVyO2dhcDoxOHB4fS5yZXBvcnQtaGVhZCBoMntmb250LXNpemU6MjlweDttYXJnaW46OHB4IDB9LnJlcG9ydC1pbnRyb3tjb2xvcjojYjFjMWQzO2xpbmUtaGVpZ2h0OjEuNzttYXJnaW46MThweCAwfS5zdGF0dXMtZ3JpZHtkaXNwbGF5OmdyaWQ7Z3JpZC10ZW1wbGF0ZS1jb2x1bW5zOnJlcGVhdCgzLG1pbm1heCgwLDFmcikpO2dhcDoxMnB4O21hcmdpbjoyM3B4IDB9LnN0YXR1cy1pdGVtLC5yZXBvcnQtY2FyZHtib3JkZXI6MXB4IHNvbGlkICMzMzQ4NWY7YmFja2dyb3VuZDojMTMyMTM3O2JvcmRlci1yYWRpdXM6MTNweDtwYWRkaW5nOjE5cHh9LnN0YXR1cy1pdGVtIHNwYW57ZGlzcGxheTpibG9jaztmb250LXNpemU6MTJweDtjb2xvcjojOWViNGM5O21hcmdpbi1ib3R0b206OXB4fS5zdGF0dXMtaXRlbSBzdHJvbmd7Zm9udC1zaXplOjE1cHh9LmZpbmRpbmctYWxlcnR7Ym9yZGVyOjFweCBzb2xpZCAjYjU4ZTQ0O2JhY2tncm91bmQ6IzM0MmMxYjtjb2xvcjojZjNkZWFmO2JvcmRlci1yYWRpdXM6MTNweDtwYWRkaW5nOjE5cHggMjFweDttYXJnaW46MjJweCAwfS5maW5kaW5nLWFsZXJ0IGgze21hcmdpbjowIDAgMTBweDtmb250LXNpemU6MTdweH0uZmluZGluZy1hbGVydCBwe2ZvbnQtc2l6ZToxNHB4O2xpbmUtaGVpZ2h0OjEuNn0uZmluZGluZy1hbGVydCBwOmxhc3QtY2hpbGR7bWFyZ2luLWJvdHRvbTowfS5maW5kaW5nLWFsZXJ0IGNvZGV7b3ZlcmZsb3ctd3JhcDphbnl3aGVyZTtmb250LXNpemU6MTJweH1cbiAgICAucmVwb3J0LWdyaWR7ZGlzcGxheTpncmlkO2dyaWQtdGVtcGxhdGUtY29sdW1uczpyZXBlYXQoMixtaW5tYXgoMCwxZnIpKTtnYXA6MTRweH0ucmVwb3J0LWNhcmR7bWluLXdpZHRoOjA7cGFkZGluZzoyMnB4fS5yZXBvcnQtY2FyZCBoM3tmb250LXNpemU6MThweDttYXJnaW46MCAwIDE1cHg7Y29sb3I6I2U5ZjZmOH0ucmVwb3J0LWNhcmQgcCwucmVwb3J0LWNhcmQgbGl7Zm9udC1zaXplOjE0cHg7bGluZS1oZWlnaHQ6MS43O2NvbG9yOiNiZmQxZTQ7b3ZlcmZsb3ctd3JhcDphbnl3aGVyZX0ucmVwb3J0LWNhcmQgc3Ryb25ne2NvbG9yOiNlZGY3ZmZ9LnJlY29yZHMsLm5vdGVze3BhZGRpbmctbGVmdDoyMHB4O21hcmdpbjowfS5yZWNvcmRzIGxpLC5ub3RlcyBsaXttYXJnaW4tYm90dG9tOjExcHh9LmZvb3Rub3Rle2NvbG9yOiM5MWFhYmMhaW1wb3J0YW50O2ZvbnQtc2l6ZToxMnB4IWltcG9ydGFudH0udGVjaG5pY2Fse21hcmdpbi10b3A6MjJweDtib3JkZXI6MXB4IHNvbGlkICMzMTQ5NWM7Ym9yZGVyLXJhZGl1czoxMnB4O3BhZGRpbmc6MTVweDtjb2xvcjojYTdiZGQxfS50ZWNobmljYWwgc3VtbWFyeXtjdXJzb3I6cG9pbnRlcn0udGVjaG5pY2FsIHB7Zm9udC1zaXplOjEycHh9LnRlY2huaWNhbCBwcmV7Zm9udC1zaXplOjExcHg7bWF4LWhlaWdodDozNDBweDt3aGl0ZS1zcGFjZTpwcmUtd3JhcDtvdmVyZmxvdy13cmFwOmFueXdoZXJlO292ZXJmbG93OmF1dG87YmFja2dyb3VuZDojMDgxMjIxO3BhZGRpbmc6MTRweDtib3JkZXItcmFkaXVzOjhweH1mb290ZXJ7Ym9yZGVyLXRvcDoxcHggc29saWQgIzMwNDM1NDtjb2xvcjojODM5YWIxO2ZvbnQtc2l6ZToxMnB4O21hcmdpbi10b3A6NTVweDtwYWRkaW5nLXRvcDoyM3B4fS5zci1vbmx5e3Bvc2l0aW9uOmFic29sdXRlO3dpZHRoOjFweDtoZWlnaHQ6MXB4O21hcmdpbjotMXB4O292ZXJmbG93OmhpZGRlbjtjbGlwOnJlY3QoMCwwLDAsMCk7d2hpdGUtc3BhY2U6bm93cmFwfVxuICAgIEBtZWRpYShtYXgtd2lkdGg6ODAwcHgpey5zaGVsbHtwYWRkaW5nOjIzcHggMTZweCA1MHB4fS5zY29wZS1waWxse2Rpc3BsYXk6bm9uZX0uaGVyb3ttYXJnaW46NTBweCBhdXRvIDI1cHh9LmV4YW1wbGUtZ3JpZCwucmVwb3J0LWdyaWQsLnN0YXR1cy1ncmlke2dyaWQtdGVtcGxhdGUtY29sdW1uczoxZnJ9LnJlcG9ydC1oZWFke2ZsZXgtZGlyZWN0aW9uOmNvbHVtbjthbGlnbi1pdGVtczpmbGV4LXN0YXJ0fS5wcm9tcHQtZm9vdGVye2ZsZXgtZGlyZWN0aW9uOmNvbHVtbjthbGlnbi1pdGVtczpzdHJldGNofS5wcm9tcHQtZm9vdGVyIGJ1dHRvbnt3aWR0aDoxMDAlfX1cbi53b3JrZmxvdy1mb3Jte21hcmdpbi10b3A6MTRweDtwYWRkaW5nOjE1cHg7Ym9yZGVyOjFweCBzb2xpZCAjMzE0YjYxO2JvcmRlci1yYWRpdXM6MTJweDtkaXNwbGF5OmdyaWQ7Z2FwOjEycHg7YmFja2dyb3VuZDojMTExZTMwfS53b3JrZmxvdy1mb3JtIGgze21hcmdpbjowO2ZvbnQtc2l6ZToxNXB4fS53b3JrZmxvdy1mb3JtIGxhYmVse2Rpc3BsYXk6Z3JpZDtnYXA6NnB4O2ZvbnQtc2l6ZToxM3B4O2NvbG9yOiNkMmU2ZWZ9LndvcmtmbG93LWZvcm0gaW5wdXQ6bm90KFt0eXBlPVwiY2hlY2tib3hcIl0pLC53b3JrZmxvdy1mb3JtIHRleHRhcmVhLC53b3JrZmxvdy1mb3JtIHNlbGVjdHttaW4td2lkdGg6MDt3aWR0aDoxMDAlO2JveC1zaXppbmc6Ym9yZGVyLWJveDtwYWRkaW5nOjEwcHg7YmFja2dyb3VuZDojMGUxOTJiO2NvbG9yOiNlZWY2ZmY7Ym9yZGVyOjFweCBzb2xpZCAjNDY2MzdhO2JvcmRlci1yYWRpdXM6OHB4O2ZvbnQ6aW5oZXJpdH0ud29ya2Zsb3ctZm9ybSBidXR0b257anVzdGlmeS1zZWxmOnN0YXJ0O2JvcmRlcjowO2JvcmRlci1yYWRpdXM6OXB4O3BhZGRpbmc6MTFweCAxNnB4O2ZvbnQ6aW5oZXJpdDtmb250LXdlaWdodDo3MDA7YmFja2dyb3VuZDojNzNlMmM5O2NvbG9yOiMwODI2MzA7Y3Vyc29yOnBvaW50ZXJ9LndvcmtmbG93LWZvcm0gYnV0dG9uOmRpc2FibGVke29wYWNpdHk6LjQ1O2N1cnNvcjpub3QtYWxsb3dlZH0ud29ya2Zsb3ctZm9ybSAuY29uZmlybWF0aW9ue2Rpc3BsYXk6ZmxleDthbGlnbi1pdGVtczpjZW50ZXI7Z2FwOjlweH0uZnJhbWV3b3JrLWNvdmVyYWdlIC5jb25maXJtYXRpb257ZGlzcGxheTpmbGV4O2FsaWduLWl0ZW1zOmNlbnRlcjtnYXA6MTBweDtwYWRkaW5nOjE2cHggMDtmb250LXNpemU6MTNweH0uZnJhbWV3b3JrLWNvdmVyYWdlIGJ1dHRvbntib3JkZXI6MDtib3JkZXItcmFkaXVzOjlweDtiYWNrZ3JvdW5kOiM3M2UyYzk7Y29sb3I6IzA4MjYzMDtwYWRkaW5nOjEycHggMTZweDtmb250OmluaGVyaXQ7Zm9udC13ZWlnaHQ6NzAwO2N1cnNvcjpwb2ludGVyO21hcmdpbi10b3A6MTBweH0uZnJhbWV3b3JrLWNvdmVyYWdlIGJ1dHRvbjpkaXNhYmxlZHtvcGFjaXR5Oi40NTtjdXJzb3I6bm90LWFsbG93ZWR9LmZyYW1ld29yay1jb3ZlcmFnZSB0ZXh0YXJlYXt3aWR0aDoxMDAlO2JhY2tncm91bmQ6IzBlMTkyYjtjb2xvcjojZWVmNmZmO2JvcmRlcjoxcHggc29saWQgIzQ2NjM3YTtib3JkZXItcmFkaXVzOjhweDtwYWRkaW5nOjExcHg7Ym94LXNpemluZzpib3JkZXItYm94O2ZvbnQ6aW5oZXJpdH1cbiAgICAuZnJhbWV3b3JrLWFjdGlvbnMgeyBkaXNwbGF5OmZsZXg7IGZsZXgtd3JhcDp3cmFwOyBnYXA6MTBweDsgYWxpZ24taXRlbXM6Y2VudGVyOyBtYXJnaW46MTJweCAwOyB9XG4gICAgLmZyYW1ld29yay1hY3Rpb25zIGJ1dHRvbiB7IGZsZXg6MCAxIGF1dG87IH1cbiAgICAuZnJhbWV3b3JrLWNvdmVyYWdlIHsgbWFyZ2luOjIwcHggMCAxNnB4OyBwYWRkaW5nOjE2cHg7IGJvcmRlcjoxcHggc29saWQgcmdiYSgxMzQsMTg1LDE3NCwuMjUpOyBib3JkZXItcmFkaXVzOjEycHg7IH1cbiAgICAuZnJhbWV3b3JrLWNvdmVyYWdlLXRpdGxlIHsgZGlzcGxheTpmbGV4OyBqdXN0aWZ5LWNvbnRlbnQ6c3BhY2UtYmV0d2VlbjsgYWxpZ24taXRlbXM6Y2VudGVyOyBnYXA6MTJweDsgZmxleC13cmFwOndyYXA7IG1hcmdpbi1ib3R0b206MTJweDsgfVxuICAgIC5mcmFtZXdvcmstbWV0ZXIgeyBoZWlnaHQ6MTJweDsgYm9yZGVyLXJhZGl1czo5OXB4OyBiYWNrZ3JvdW5kOnJnYmEoMTUwLDE3MCwxODUsLjIzKTsgb3ZlcmZsb3c6aGlkZGVuOyB9XG4gICAgLmZyYW1ld29yay1tZXRlci1maWxsIHsgaGVpZ2h0OjEwMCU7IGJhY2tncm91bmQ6IzYxZDhiYzsgYm9yZGVyLXJhZGl1czo5OXB4OyB0cmFuc2l0aW9uOndpZHRoIC4yNXMgZWFzZTsgfVxuICAgIC5yZXZpZXctbW9yZXttYXJnaW4tdG9wOjE0cHg7Ym9yZGVyOjFweCBzb2xpZCAjNDY2MzdhO2JhY2tncm91bmQ6IzE3MmQ0Mjtjb2xvcjojZTZmM2ZkO3BhZGRpbmc6MTJweCAxNnB4O2JvcmRlci1yYWRpdXM6OXB4O2N1cnNvcjpwb2ludGVyfVxuICAgIC5jaGVja3BvaW50LWxhYmVse2Rpc3BsYXk6Z3JpZDtnYXA6MTBweDtmb250LXNpemU6MTNweDttYXJnaW4tdG9wOjE0cHh9XG4gICAgLmNoZWNrcG9pbnQtbGFiZWwgaW5wdXR7Y29sb3I6I2QwZTdlZH1cbiAgICAjc3RhcnQtZ3JjLWNhc2V7bWFyZ2luLXRvcDo1NXB4fVxuICAgIC5zaWNvLWNhc2UtZHJhZnR7cGFkZGluZzoxNXB4O21hcmdpbjoxMnB4IDA7YmFja2dyb3VuZDojMGQxYzMwO2JvcmRlcjoxcHggc29saWQgIzM1NTY2Yztib3JkZXItcmFkaXVzOjlweH1cbiAgICAuc2ljby1jYXNlLWRyYWZ0IGg0e21hcmdpbjowIDAgMTBweDtjb2xvcjojOWVmMGRkfVxuICAgIC5zaWNvLWNhc2UtZHJhZnQgcHtsaW5lLWhlaWdodDoxLjY1O2NvbG9yOiNjNGQ4ZTZ9XG4gICAgLnNpY28tY2FzZS1kcmFmdCBkbHtkaXNwbGF5OmdyaWQ7Z2FwOjhweDttYXJnaW46MTJweCAwfVxuICAgIC5zaWNvLWNhc2UtZHJhZnQgZGwgZGl2e2Rpc3BsYXk6Z3JpZDtncmlkLXRlbXBsYXRlLWNvbHVtbnM6bWlubWF4KDEyMHB4LDMyJSkgMWZyO2dhcDoxMHB4O2JvcmRlci1ib3R0b206MXB4IHNvbGlkICMyNTQwNTI7cGFkZGluZy1ib3R0b206N3B4fVxuICAgIC5zaWNvLWNhc2UtZHJhZnQgZHR7Y29sb3I6IzkzYmVjZTtmb250LXdlaWdodDo3MDB9XG4gICAgLnNpY28tY2FzZS1kcmFmdCBkZHttYXJnaW46MDtjb2xvcjojZTVmMGY0O292ZXJmbG93LXdyYXA6YW55d2hlcmV9XG4gICAgLyogU0lDTyBBSSBOZXh0OiBkaXNwbGF5LW9ubHkgcmVmaW5lbWVudC4gTm8gZ2VuZXJhdGlvbiwgc3RvcmFnZSBvciBBUEkgY2hhbmdlcy4gKi9cbiAgICAucmVwb3J0LWludHJve21heC13aWR0aDo4MmNoO2ZvbnQtc2l6ZToxNXB4O2xpbmUtaGVpZ2h0OjEuODtjb2xvcjojYzFkNGUwfVxuICAgIC5yZXBvcnQtaGVhZCBoMntmb250LXNpemU6Y2xhbXAoMjVweCwzdncsMzJweCk7bGV0dGVyLXNwYWNpbmc6LS4wMjVlbX1cbiAgICAud29ya2Zsb3ctZm9ybXtwYWRkaW5nOjIwcHg7Z2FwOjE1cHh9XG4gICAgLndvcmtmbG93LWZvcm0gbGFiZWx7Zm9udC13ZWlnaHQ6NjUwO2xpbmUtaGVpZ2h0OjEuNDV9XG4gICAgLndvcmtmbG93LWZvcm0gaW5wdXQ6Zm9jdXMtdmlzaWJsZSwud29ya2Zsb3ctZm9ybSB0ZXh0YXJlYTpmb2N1cy12aXNpYmxle291dGxpbmU6MnB4IHNvbGlkICM3OGRmY2M7b3V0bGluZS1vZmZzZXQ6MnB4fVxuICAgIC5zaWNvLWNhc2UtZHJhZnR7cGFkZGluZzoyMHB4IDIycHg7bWFyZ2luOjE0cHggMDtiYWNrZ3JvdW5kOiMxMDIxMzk7Ym9yZGVyLWNvbG9yOiMzNjUzNmI7Ym9yZGVyLXJhZGl1czoxMnB4O2JveC1zaGFkb3c6MCAzcHggMTBweCAjMDAwMn1cbiAgICAuc2ljby1jYXNlLWRyYWZ0IGg0e2ZvbnQtc2l6ZToxNnB4O2xpbmUtaGVpZ2h0OjEuNTtsZXR0ZXItc3BhY2luZzotLjAxZW07Y29sb3I6IzgwZTZkMn1cbiAgICAuc2ljby1jYXNlLWRyYWZ0IHB7Zm9udC1zaXplOjE0cHg7bGluZS1oZWlnaHQ6MS43O21hcmdpbjoxMHB4IDA7Y29sb3I6I2QwZGZlYTtvdmVyZmxvdy13cmFwOmFueXdoZXJlfVxuICAgIC5zaWNvLWNhc2UtZHJhZnQgcCBzdHJvbmd7Y29sb3I6I2U3ZjNmOX1cbiAgICAuc2ljby1jYXNlLWRyYWZ0IGRse2dhcDowO21hcmdpbjoxNnB4IDB9XG4gICAgLnNpY28tY2FzZS1kcmFmdCBkbCBkaXZ7Z3JpZC10ZW1wbGF0ZS1jb2x1bW5zOm1pbm1heCgxNDVweCwzMiUpIG1pbm1heCgwLDFmcik7YWxpZ24taXRlbXM6c3RhcnQ7Z2FwOjE0cHg7cGFkZGluZzo5cHggMDtib3JkZXItYm90dG9tOjFweCBzb2xpZCAjMjk0NDVhfVxuICAgIC5zaWNvLWNhc2UtZHJhZnQgZHR7Y29sb3I6I2FlY2JkYjtmb250LXdlaWdodDo3MDA7Zm9udC1zaXplOjEzcHg7bGluZS1oZWlnaHQ6MS41fVxuICAgIC5zaWNvLWNhc2UtZHJhZnQgZGR7Zm9udC1zaXplOjE0cHg7bGluZS1oZWlnaHQ6MS41NX1cbiAgICAuc2ljby1jYXNlLWRyYWZ0IC5mb290bm90ZXtsaW5lLWhlaWdodDoxLjZ9XG4gICAgQG1lZGlhKG1heC13aWR0aDo2MDBweCl7LndvcmtmbG93LWZvcm17cGFkZGluZzoxNHB4fS5zaWNvLWNhc2UtZHJhZnR7cGFkZGluZzoxNXB4fS5zaWNvLWNhc2UtZHJhZnQgZGwgZGl2e2dyaWQtdGVtcGxhdGUtY29sdW1uczoxZnI7Z2FwOjNweDtwYWRkaW5nOjEwcHggMH19XG4gICAgLmZ1bGwtY2FzZS1wcmV2aWV3e2JvcmRlcjoxcHggc29saWQgIzM5N2Y3ODtiYWNrZ3JvdW5kOiMxMDJiMzM7Ym9yZGVyLXJhZGl1czoxMnB4O3BhZGRpbmc6MTZweDttYXJnaW46MTZweCAwfVxuICAgIC5mdWxsLWNhc2UtcHJldmlldy1oZWFkZXJ7ZGlzcGxheTpmbGV4O2FsaWduLWl0ZW1zOmNlbnRlcjtqdXN0aWZ5LWNvbnRlbnQ6c3BhY2UtYmV0d2VlbjtmbGV4LXdyYXA6d3JhcDtnYXA6OHB4fVxuICAgIC5mdWxsLWNhc2UtcHJldmlldyBoNHttYXJnaW46NHB4IDAgOHB4O2ZvbnQtc2l6ZToxN3B4O2NvbG9yOiNiNmY1ZTZ9XG4gICAgLmZ1bGwtY2FzZS13YXJuaW5ne3BhZGRpbmc6NXB4IDlweDtib3JkZXI6MXB4IHNvbGlkICNiOThiNGQ7Ym9yZGVyLXJhZGl1czoyMHB4O2ZvbnQtc2l6ZToxMXB4O2NvbG9yOiNmM2QwYTJ9XG4gICAgLmZ1bGwtY2FzZS1jb3VudHN7ZGlzcGxheTpncmlkO2dyaWQtdGVtcGxhdGUtY29sdW1uczpyZXBlYXQoYXV0by1maXQsbWlubWF4KDEzMnB4LDFmcikpO2dhcDo4cHg7bWFyZ2luOjEycHggMH1cbiAgICAuZnVsbC1jYXNlLWNvdW50e2JvcmRlcjoxcHggc29saWQgIzMzNWM2OTtib3JkZXItcmFkaXVzOjhweDtwYWRkaW5nOjExcHg7YmFja2dyb3VuZDojMTMyYzNkfVxuICAgIC5mdWxsLWNhc2UtY291bnQgc3Ryb25ne2Rpc3BsYXk6YmxvY2s7Zm9udC1zaXplOjIxcHg7Y29sb3I6I2RmZjlmNn1cbiAgICAuZnVsbC1jYXNlLWNvdW50IHNwYW57Zm9udC1zaXplOjEycHg7Y29sb3I6I2I2Y2VkYn1cbiAgICAuZnVsbC1jYXNlLWRldGFpbHN7Ym9yZGVyLXRvcDoxcHggc29saWQgIzMxNTc2NTtwYWRkaW5nOjEwcHggMDttYXJnaW4tdG9wOjEwcHh9XG4gICAgLmZ1bGwtY2FzZS1kZXRhaWxzIHN1bW1hcnl7Y3Vyc29yOnBvaW50ZXI7Zm9udC1zaXplOjE0cHg7Zm9udC13ZWlnaHQ6NzAwO2NvbG9yOiNjY2VjZWZ9XG4gICAgLmZ1bGwtY2FzZS1zdWJkZXRhaWxze21hcmdpbi1sZWZ0OjEycHh9XG4gICAgLmZ1bGwtY2FzZS1yZWNvcmQtbGlzdHttYXgtaGVpZ2h0OjMzMHB4O292ZXJmbG93OmF1dG87cGFkZGluZy1sZWZ0OjIwcHg7Zm9udC1zaXplOjEzcHh9XG4gICAgLmZ1bGwtY2FzZS1yZWNvcmQtbGlzdCBsaXtwYWRkaW5nOjZweCAwO2xpbmUtaGVpZ2h0OjEuNTtib3JkZXItYm90dG9tOjFweCBzb2xpZCAjMjQ0ODUyfVxuICAgIC5mdWxsLWNhc2UtbWF0cml4LXNjcm9sbHtvdmVyZmxvdy14OmF1dG87bWFyZ2luOjEycHggMH1cbiAgICAuZnVsbC1jYXNlLW1hdHJpeHtkaXNwbGF5OmdyaWQ7Z2FwOjNweDttaW4td2lkdGg6bWF4LWNvbnRlbnR9XG4gICAgLmZ1bGwtY2FzZS1tYXRyaXgtbGFiZWx7cGFkZGluZzo4cHggNnB4O2JhY2tncm91bmQ6IzIyM2Q0ZDtjb2xvcjojZWRmNWY4O2ZvbnQtc2l6ZToxMXB4O3RleHQtYWxpZ246Y2VudGVyO2JvcmRlci1yYWRpdXM6NHB4O2Rpc3BsYXk6Z3JpZDtwbGFjZS1pdGVtczpjZW50ZXI7bWluLWhlaWdodDozOHB4fVxuICAgIC5mdWxsLWNhc2UtbWF0cml4LWNlbGx7ZGlzcGxheTpncmlkO3BsYWNlLWl0ZW1zOmNlbnRlcjttaW4taGVpZ2h0OjQycHg7Ym9yZGVyLXJhZGl1czo0cHg7cGFkZGluZzo1cHg7Zm9udC1zaXplOjExcHg7Zm9udC13ZWlnaHQ6ODAwO2NvbG9yOiMxODI1MmQ7dGV4dC1hbGlnbjpjZW50ZXJ9XG4gICAgLnJlcXVpcmVtZW50LWNvdmVyYWdlLXBsYW57Ym9yZGVyOjFweCBzb2xpZCAjNDE2ZDcyO2JvcmRlci1yYWRpdXM6MTJweDtiYWNrZ3JvdW5kOiMxMDI1MzQ7cGFkZGluZzoxOHB4O21hcmdpbjoxOHB4IDA7Y29sb3I6I2U5ZjRmZn1cbiAgICAucmVxdWlyZW1lbnQtY292ZXJhZ2UtcGxhbiBoNHtmb250LXNpemU6MTdweDttYXJnaW46MCAwIDhweH0ucmVxdWlyZW1lbnQtY292ZXJhZ2UtcGxhbiBwe21hcmdpbjo4cHggMH0ucmVxdWlyZW1lbnQtY292ZXJhZ2UtcGxhbiBkZXRhaWxze21hcmdpbi10b3A6MTJweH0ucmVxdWlyZW1lbnQtd29yay1pdGVtc3ttYXgtaGVpZ2h0OjMyMHB4O292ZXJmbG93OmF1dG87cGFkZGluZy1sZWZ0OjI1cHh9LnJlcXVpcmVtZW50LXdvcmstaXRlbXMgbGl7cGFkZGluZzo4cHggMDtib3JkZXItYm90dG9tOjFweCBzb2xpZCAjMjQ0NDRjO2xpbmUtaGVpZ2h0OjEuNH1cbiAqe308L3N0eWxlPlxuIl0sIm1hcHBpbmdzIjoiOzs7OztTQUVhLE9BQU8sRUFBRSxXQUFXLEVBQUUsV0FBVyxRQUFRLFlBQVk7U0FDckQsT0FBTyxRQUFRLFFBQVE7T0FFekIsaUJBQWlCLE1BQU0sdURBQXVEOzs7Q0FDNUUsdUJBQXVCO0NBQUUsa0JBQWtCO0NBQUUsbUJBQW1CO09BQVEsK0JBQStCOztTQUU1RyxtQkFBbUIsRUFBRSxrQkFBa0IsRUFBRSxRQUFRLFFBRTlDLGtDQUFrQzs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7O2tDQVQ3QyxDQUFDOzs7O0tBWU8sV0FBVyxTQUFHLE9BQU0sQ0FBQyxFQUFFO0tBQ3ZCLFlBQVksU0FBRyxPQUFNLENBQUMsRUFBRTtLQUN4QixJQUFJLEdBQVUsS0FBSztLQUNuQixZQUFZLFNBQUcsT0FBTSxDQUE2QixJQUFJO0tBQ3RELGVBQWUsU0FBRyxPQUFNLENBQTZCLElBQUk7S0FDekQsZ0JBQWdCLFNBQUcsT0FBTSxDQUE2QixJQUFJO0tBQzFELGdCQUFnQixTQUFHLE9BQU0sQ0FBNkIsSUFBSTtLQUMxRCxnQkFBZ0IsU0FBRyxPQUFNLENBQUMsRUFBRTtLQUM1QixtQkFBbUIsU0FBRyxPQUFNLENBQTZCLElBQUk7S0FDN0QsZUFBZSxTQUFHLE9BQU0sQ0FBQyxFQUFFO0tBQzNCLGdCQUFnQixTQUFHLE9BQU07S0FDekIsWUFBWSxTQUFHLE9BQU0sQ0FBQyxFQUFFO0tBQ3hCLFdBQVcsU0FBRyxPQUFNLENBQUMsS0FBSztLQUMxQixZQUFZLFNBQUcsT0FBTSxDQUFDLEVBQUU7S0FDeEIsY0FBYyxTQUFHLE9BQU0sQ0FBQyxFQUFFO0tBQzFCLGVBQWUsU0FBRyxPQUFNLENBQTZC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