/** Queue coordination only. Content comes from authenticated Qwen responses. */
export type GenerationSlot = {
    activity_number: number; draft_index: number; draft_reference: string;
    theme: string; focus_requirement_reference: string; focus_requirement_id: string;
    dependency_draft_references: string[];
    scope_subject?: string; task_identity?: string; execution_mode?: string; draft_case_scope_id?: string; case_scope_kind?: string;
};
export const draftReference = (step: number, index: number) =>
    `draft-${String(step).padStart(2, '0')}-${String(index).padStart(2, '0')}`;
export function validateGenerationQueue(plan: any, rows: any[]): GenerationSlot[] {
    if (!Array.isArray(plan?.generation_queue) || !plan.generation_queue.length)
        throw new Error('The server did not supply a framework-driven generation queue.');
    const source = new Map(rows.map(r => [String(r.requirement_id), String(r.reference)]));
    const queue = plan.generation_queue as GenerationSlot[];
    const ids = new Set(queue.map(s => s.draft_reference));
    if (ids.size !== queue.length) throw new Error('Duplicate generation tasks.');
    for (const slot of queue) {
        if (!Number.isInteger(slot.activity_number) || slot.activity_number < 1 || slot.activity_number > 16 ||
            !Number.isInteger(slot.draft_index) || slot.draft_index < 1 || slot.draft_index > 10000 ||
            slot.draft_reference !== draftReference(slot.activity_number, slot.draft_index) ||
            source.get(slot.focus_requirement_id) !== slot.focus_requirement_reference ||
            !/^[a-z_]{1,60}$/.test(slot.theme) || !Array.isArray(slot.dependency_draft_references) ||
            slot.dependency_draft_references.some(r => !ids.has(r) || Number(r.slice(6,8)) >= slot.activity_number))
            throw new Error('Generation task does not match the authorized source or workflow dependencies.');
    }
    return queue;
}

export function acceptedGenerationItem(row: any): boolean {
    return row?.business_records_written === false &&
        row?.draft?.status === 'new_unsaved_ai_draft_pending_verification' &&
        ((row?.quality_contract_checked === true && row?.provenance === 'qwen_quality_single_authenticated_v7') ||
         (row?.deterministic_contract_checked === true && row?.provenance === 'sico_deterministic_authenticated_v1'));
}
export function deterministicGenerationItem(plan: any, slot: GenerationSlot): any {
    const source = plan?.deterministic_drafts?.find((r: any) => r.draft_reference === slot.draft_reference);
    if (!source || source.source !== 'sico_deterministic' || source.approval_status !== 'not_approved' ||
        source.business_records_written !== false ||
        !(source.tenant_id || (source.scope_kind === 'draft_only_case' && /^draft-case:[a-f0-9]{64}$/.test(source.draft_case_scope_id ?? '') && source.draft_case_scope_id === plan.draft_case_scope_id)) ||
        source.activity_number !== slot.activity_number || source.status !== 'proposed_unverified')
        throw new Error('An authorized organization and exact framework are required for deterministic setup.');
    return {
        activity_number: slot.activity_number, activity_code: slot.activity_number === 14 ? 'human_review' : slot.activity_number === 16 ? 'reports' : slot.theme,
        activity_name: source.title, target_existing_sico_model: source.target_model,
        provenance: 'sico_deterministic_authenticated_v1', deterministic_contract_checked: true,
        business_records_written: false, generated_by_model: false,
        source_digest: plan.source_digest, framework_id: plan.framework_id,
        ...(source.draft_case_scope_id ? { draft_case_scope_id: source.draft_case_scope_id } : {}),
        generation_scope_subject: slot.scope_subject ?? '', generation_task_identity: slot.task_identity,
        source_proposal: source,
        draft: { draft_reference: slot.draft_reference, record_type: source.target_model,
            title: source.title, status: 'new_unsaved_ai_draft_pending_verification',
            content: `${source.title}: ${plan.scope.organization}. ${plan.scope.framework}. ${plan.coverage.authorized_requirements_loaded} authorized requirements; human review pending.`,
            proposed_attributes: Object.entries(source.model_fields).slice(0, 7).map(([field, value]) => ({
                field, proposed_value: String(typeof value === 'string' ? value : JSON.stringify(value)).slice(0, 360)
            })),
            related_draft_references: slot.dependency_draft_references,
            evidence_request: 'Not assessed. Supporting evidence remains subject to human review.',
            verification_question: 'Confirm this source-prepared setup and its scope before approval.',
            is_verified_existing_asset_or_evidence: false }
    };
}
export function nextAssetBatch(queue: GenerationSlot[], items: any[], first: GenerationSlot, limit: 1 | 2 = 2, deferred: string[] = []): GenerationSlot[] {
    const accepted = new Set(items.filter(acceptedGenerationItem).map(r => r.draft.draft_reference));
    const occupied = new Set(items.map(r => r?.draft?.draft_reference));
    const ready = queue.filter(s => s.activity_number === 4 && !occupied.has(s.draft_reference) && !deferred.includes(s.draft_reference) &&
        s.dependency_draft_references.every(r => accepted.has(r)));
    if (!ready.some(s => s.draft_reference === first.draft_reference)) throw new Error('The first asset slot is not ready.');
    return [first, ...ready.filter(s => s.draft_reference !== first.draft_reference)].slice(0, limit);
}

export function nextGenerationSlot(queue: GenerationSlot[], items: any[], deferred: string[] = []): GenerationSlot | null {
    const expectedScope = queue[0]?.draft_case_scope_id;
    for (const item of items) {
        if (expectedScope && ((item.draft_case_scope_id && item.draft_case_scope_id !== expectedScope) ||
            (queue[0]?.case_scope_kind === 'draft_only_case' && !item.draft_case_scope_id)))
            throw new Error('The checkpoint belongs to another or unbound draft-only case.');
        const slot=queue.find(s=>s.draft_reference===item?.draft?.draft_reference);
        if (slot?.scope_subject && (item.generation_scope_subject!==slot.scope_subject ||
            item.generation_task_identity!==slot.task_identity))
            throw new Error('The saved draft does not match this scope task. Preserve the checkpoint and review its scope mapping before resuming; no record was reassigned.');
    }
    const accepted = new Set(items.filter(acceptedGenerationItem).map(r => r.draft.draft_reference));
    const pending = queue.filter(s => !accepted.has(s.draft_reference));
    const occupied = new Set(items.map(r => r?.draft?.draft_reference));
    if (pending.some(s => occupied.has(s.draft_reference)))
        throw new Error('An imported or unvalidated draft already occupies a planned slot. Preserve this checkpoint and start a new case; existing content cannot be silently replaced.');
    const ready = pending.find(s => !deferred.includes(s.draft_reference) && s.dependency_draft_references.every(r => accepted.has(r)) &&
        (![14,16].includes(s.activity_number) || !pending.some(p => p.activity_number < s.activity_number)));
    if (pending.length && !ready) throw new Error('Pending work is blocked by missing validated parents or failed asset slots. Accepted records are saved; resume retries pending slots.');
    return ready ?? null;
}
export function plannedDraftContext(slot: GenerationSlot, items: any[]) {
    const required = new Set(slot.dependency_draft_references);
    const parents = items.filter(r => required.has(r?.draft?.draft_reference));
    if (parents.length !== required.size) throw new Error('A planned parent draft is missing.');
    const earlier = items.filter(r => r.activity_number === slot.activity_number &&
        r.draft?.draft_reference !== slot.draft_reference).slice(-Math.max(0,45-parents.length));
    return [...earlier,...parents].map(r => ({
        ...(r.draft_case_scope_id ? { draft_case_scope_id: r.draft_case_scope_id } : {}),
        draft_reference: r.draft.draft_reference, title: r.draft.title,
        record_type: r.draft.record_type, content: String(r.draft.content ?? '').slice(0,670),
        proposed_attributes: r.draft.proposed_attributes ?? [],
        related_draft_references: r.draft.related_draft_references ?? []
    }));
}
