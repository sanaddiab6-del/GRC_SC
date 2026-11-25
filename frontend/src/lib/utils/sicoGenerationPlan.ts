/** Queue coordination only. Content comes from authenticated Qwen responses. */
export type GenerationSlot = {
    activity_number: number; draft_index: number; draft_reference: string;
    theme: string; focus_requirement_reference: string; focus_requirement_id: string;
    dependency_draft_references: string[];
    scope_subject?: string; task_identity?: string;
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
export function nextGenerationSlot(queue: GenerationSlot[], items: any[]): GenerationSlot | null {
    for (const item of items) {
        const slot=queue.find(s=>s.draft_reference===item?.draft?.draft_reference);
        if (slot?.scope_subject && (item.generation_scope_subject!==slot.scope_subject ||
            item.generation_task_identity!==slot.task_identity))
            throw new Error('The saved draft does not match this scope task. Preserve the checkpoint and review its scope mapping before resuming; no record was reassigned.');
    }
    const accepted = new Set(items.filter(r => r?.quality_contract_checked === true &&
        r?.business_records_written === false && r?.provenance === 'qwen_quality_single_authenticated_v7' &&
        r?.draft?.status === 'new_unsaved_ai_draft_pending_verification').map(r => r.draft.draft_reference));
    const pending = queue.filter(s => !accepted.has(s.draft_reference));
    const occupied = new Set(items.map(r => r?.draft?.draft_reference));
    if (pending.some(s => occupied.has(s.draft_reference)))
        throw new Error('An imported or unvalidated draft already occupies a planned slot. Preserve this checkpoint and start a new case; existing content cannot be silently replaced.');
    const ready = pending.find(s => s.dependency_draft_references.every(r => accepted.has(r)) &&
        (![14,16].includes(s.activity_number) || !pending.some(p => p.activity_number < s.activity_number)));
    if (pending.length && !ready) throw new Error('Generation is blocked by missing validated parent drafts. Restore or review the checkpoint.');
    return ready ?? null;
}
export function plannedDraftContext(slot: GenerationSlot, items: any[]) {
    const required = new Set(slot.dependency_draft_references);
    const parents = items.filter(r => required.has(r?.draft?.draft_reference));
    if (parents.length !== required.size) throw new Error('A planned parent draft is missing.');
    const earlier = items.filter(r => r.activity_number === slot.activity_number &&
        r.draft?.draft_reference !== slot.draft_reference).slice(-Math.max(0,45-parents.length));
    return [...earlier,...parents].map(r => ({
        draft_reference: r.draft.draft_reference, title: r.draft.title,
        record_type: r.draft.record_type, content: String(r.draft.content ?? '').slice(0,670),
        proposed_attributes: r.draft.proposed_attributes ?? [],
        related_draft_references: r.draft.related_draft_references ?? []
    }));
}
