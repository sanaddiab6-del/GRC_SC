/**
 * SICO AI Activity 1 v3 client-held read-only checkpoint.
 * This is NOT a stored GRC assessment or proof of compliance.
 * The backend signs the continuation cursor; the client-held reviews are not signed.
 */
export type ReviewScope = {
    organization_name: string;
    framework_name: string;
    problem: string;
    business_context: string;
};

export type RequirementDraft = {
    requirement_id: string;
    reference: string;
    requirement_name: string;
    applicability: string;
    rationale: string;
    evidence_to_request: string;
    question_to_resolve: string;
    source: string;
    status: string;
    source_text_excerpt_truncated: boolean;
};

export type ReviewCheckpoint = {
    format: 'sico_activity1_v3_read_only_checkpoint';
    version: 1;
    scope: ReviewScope;
    matched_framework: { name: string; reference: string; urn: string; provider: string };
    snapshot_digest: string;
    coverage: { accessible_total: number; reviewed_through: number; remaining: number; complete: boolean };
    requirement_reviews: RequirementDraft[];
    next_cursor: string | null;
    framework_edition_status: string;
    organization_context_status: string;
    business_records_written: false;
    compliance_verdict: 'not_established';
};

const allowedApplicability = new Set([
    'potentially_applicable', 'needs_confirmation', 'potentially_out_of_scope_pending_confirmation'
]);
const HEX64 = /^[a-fA-F0-9]{64}$/;

function object(value: unknown): Record<string, unknown> {
    if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('Invalid assessment data structure.');
    return value as Record<string, unknown>;
}

function int(value: unknown): number {
    if (typeof value !== 'number' || !Number.isSafeInteger(value) || value < 0) {
        throw new Error('Invalid requirement coverage counters.');
    }
    return value;
}

function reviewRows(value: unknown): RequirementDraft[] {
    if (!Array.isArray(value)) throw new Error('Missing requirement review list.');
    return value.map((original: unknown) => {
        const r = object(original);
        if (typeof r.requirement_id !== 'string' || !r.requirement_id || r.requirement_id.length > 128 ||
            typeof r.reference !== 'string' || r.reference.length > 250 ||
            typeof r.requirement_name !== 'string' || r.requirement_name.length > 200 ||
            !allowedApplicability.has(String(r.applicability)) ||
            r.source !== 'sico_authorized_requirement_record' ||
            r.status !== 'provisional_ai_draft_not_evidence_verified' ||
            typeof r.source_text_excerpt_truncated !== 'boolean') {
            throw new Error('Invalid or ungrounded requirement review.');
        }
        for (const key of ['rationale', 'evidence_to_request', 'question_to_resolve'] as const) {
            if (typeof r[key] !== 'string' || !(r[key] as string).trim() || (r[key] as string).length > 1200) {
                throw new Error('Missing or invalid evidence-based reasoning.');
            }
        }
        return {
            requirement_id: r.requirement_id as string,
            reference: r.reference as string,
            requirement_name: r.requirement_name as string,
            applicability: r.applicability as string,
            rationale: r.rationale as string,
            evidence_to_request: r.evidence_to_request as string,
            question_to_resolve: r.question_to_resolve as string,
            source: r.source as string,
            status: r.status as string,
            source_text_excerpt_truncated: r.source_text_excerpt_truncated as boolean,
        };
    });
}

function metadata(value: unknown): ReviewCheckpoint['matched_framework'] {
    const f = object(value);
    if (typeof f.name !== 'string' || !f.name.trim()) throw new Error('Selected SICO framework was not identified.');
    for (const key of ['reference', 'urn', 'provider']) {
        if (typeof f[key] !== 'string') throw new Error('Incomplete framework metadata.');
    }
    return {
        name: f.name.slice(0, 200), reference: (f.reference as string).slice(0, 100),
        urn: (f.urn as string).slice(0, 255), provider: (f.provider as string).slice(0, 200)
    };
}

export function scopeKey(scope: ReviewScope): string {
    return JSON.stringify([scope.organization_name, scope.framework_name, scope.problem, scope.business_context]);
}

export function applyFrameworkBatch(
    previous: ReviewCheckpoint | null,
    scope: ReviewScope,
    raw: unknown
): ReviewCheckpoint {
    const batch = object(raw);
    if (batch.business_records_written !== false || batch.compliance_verdict !== 'not_established') {
        throw new Error('The read-only GRC safety guarantee was not confirmed.');
    }
    if (batch.status !== 'partial' && batch.status !== 'complete') {
        throw new Error('SICO could not match one exact, authorized, assessable framework.');
    }
    const fw = metadata(batch.matched_framework);
    const coverage = object(batch.coverage);
    const total = int(coverage.accessible_total);
    const before = int(coverage.reviewed_before);
    const current = int(coverage.reviewed_this_batch);
    const after = int(coverage.reviewed_through);
    const remaining = int(coverage.remaining);
    const complete = coverage.complete === true;
    const rows = reviewRows(batch.requirement_reviews);
    if (total < 1 || current < 1 || current > 3 || current !== rows.length ||
        before !== (previous?.requirement_reviews.length ?? 0) ||
        before + current !== after || after > total || remaining !== total - after ||
        complete !== (after === total) || (batch.status === 'complete') !== complete) {
        throw new Error('The backend returned inconsistent framework progress. Previous progress was preserved.');
    }
    const digest = batch.snapshot_digest;
    if (typeof digest !== 'string' || !HEX64.test(digest)) {
        throw new Error('Missing requirement catalog fingerprint.');
    }
    const cursor = batch.next_cursor;
    if (complete ? cursor !== null : (typeof cursor !== 'string' || !cursor || cursor.length > 2048)) {
        throw new Error('Missing or invalid signed continuation cursor.');
    }
    if (previous && (scopeKey(previous.scope) !== scopeKey(scope) ||
        previous.coverage.complete || previous.snapshot_digest !== digest ||
        JSON.stringify(previous.matched_framework) !== JSON.stringify(fw) ||
        previous.coverage.accessible_total !== total)) {
        throw new Error('Framework, user input or authorized catalog changed. Restart after checking access.');
    }
    const previousRows = previous?.requirement_reviews ?? [];
    const keys = new Set(previousRows.map((row) => row.requirement_id));
    for (const row of rows) {
        if (keys.has(row.requirement_id)) throw new Error('Duplicate requirement returned. No batch was applied.');
        keys.add(row.requirement_id);
    }
    return {
        format: 'sico_activity1_v3_read_only_checkpoint', version: 1, scope,
        matched_framework: fw, snapshot_digest: digest,
        coverage: { accessible_total: total, reviewed_through: after, remaining, complete },
        requirement_reviews: [...previousRows, ...rows], next_cursor: complete ? null : cursor as string,
        framework_edition_status: String(batch.framework_edition_status ?? 'not_independently_verified').slice(0, 100),
        organization_context_status: String(batch.organization_context_status ?? 'unverified').slice(0, 120),
        business_records_written: false, compliance_verdict: 'not_established',
    };
}

export function validateCheckpoint(input: unknown): ReviewCheckpoint {
    const value = object(input);
    if (value.format !== 'sico_activity1_v3_read_only_checkpoint' || value.version !== 1 ||
        value.business_records_written !== false || value.compliance_verdict !== 'not_established') {
        throw new Error('This is not an Activity 1 v3 read-only checkpoint.');
    }
    const s = object(value.scope);
    for (const [key, max] of Object.entries({
        organization_name: 150, framework_name: 150, problem: 4000, business_context: 1200
    })) {
        if (typeof s[key] !== 'string' || (s[key] as string).length > max) {
            throw new Error('Invalid checkpoint assessment scope.');
        }
    }
    if ((s.organization_name as string).trim().length < 2 ||
        (s.framework_name as string).trim().length < 2 ||
        (s.problem as string).trim().length < 20) {
        throw new Error('Incomplete checkpoint assessment scope.');
    }
    const rows = reviewRows(value.requirement_reviews);
    const ids = new Set(rows.map((row) => row.requirement_id));
    if (ids.size !== rows.length) throw new Error('Duplicate requirement IDs in checkpoint.');
    const c = object(value.coverage);
    const total = int(c.accessible_total);
    const through = int(c.reviewed_through);
    const remaining = int(c.remaining);
    const complete = c.complete === true;
    if (total < 1 || total > 50000 || rows.length !== through || through > total ||
        remaining !== total - through || complete !== (through === total)) {
        throw new Error('Invalid imported requirement coverage.');
    }
    if (typeof value.snapshot_digest !== 'string' || !HEX64.test(value.snapshot_digest) ||
        (complete ? value.next_cursor !== null :
            (typeof value.next_cursor !== 'string' || !value.next_cursor || value.next_cursor.length > 2048))) {
        throw new Error('Invalid or missing imported continuation cursor.');
    }
    return {
        format: 'sico_activity1_v3_read_only_checkpoint', version: 1,
        scope: {
            organization_name: s.organization_name as string, framework_name: s.framework_name as string,
            problem: s.problem as string, business_context: s.business_context as string
        },
        matched_framework: metadata(value.matched_framework),
        snapshot_digest: value.snapshot_digest,
        coverage: { accessible_total: total, reviewed_through: through, remaining, complete },
        requirement_reviews: rows,
        next_cursor: value.next_cursor as string | null,
        framework_edition_status: String(value.framework_edition_status ?? 'not_independently_verified').slice(0, 100),
        organization_context_status: String(value.organization_context_status ?? 'unverified').slice(0, 120),
        business_records_written: false,
        compliance_verdict: 'not_established',
    };
}
