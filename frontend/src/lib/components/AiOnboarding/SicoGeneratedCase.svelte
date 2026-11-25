<script lang="ts">
    let { items, plan, organization, framework }: { items: any[]; plan: any; organization: string; framework: string } = $props();
    let category = $state('all');
    let query = $state('');
    let selected = $state('');
    let limit = $state(25);
    const records = $derived(items.filter(r => r?.provenance === 'qwen_quality_single_authenticated_v7' &&
        r?.quality_contract_checked === true && r?.business_records_written === false &&
        r?.draft?.status === 'new_unsaved_ai_draft_pending_verification'));
    const categories = $derived([...new Set(records.map(r => r.activity_code))]);
    const filtered = $derived(records.filter(r => (category === 'all' || r.activity_code === category) &&
        (!query.trim() || JSON.stringify(r.draft).toLowerCase().includes(query.trim().toLowerCase()))));
    const detail = $derived(records.find(r => r.draft.draft_reference === selected) ?? filtered[0]);
    const matrix = $derived(plan?.full_case_blueprint?.risk_matrix_proposal?.json_definition);
    const reviewed = $derived(new Set(records.filter(r => r.activity_number === 10).map(r => r.draft.authorized_requirement_id).filter(Boolean)).size);
    const label = (value: string) => value.replaceAll('_',' ').replace(/\b\w/g,c => c.toUpperCase());
    function inspect(ref: string) { selected = ref; }
</script>

<section class="case-board" aria-label="Qwen-generated GRC case">
    <header><div><p class="eyebrow">Organization assessment workspace</p><h3>{organization} · {framework}</h3></div><span class="badge">Unsaved · Approval pending</span></header>
    <div class="summary">
        <div><strong>{records.length}</strong><span>Validated Qwen drafts</span></div>
        <div><strong>{plan?.generation_summary?.planned_qwen_detail_drafts ?? '—'}</strong><span>Source-driven tasks scheduled</span></div>
        <div><strong>{reviewed}/{plan?.coverage?.authorized_requirements_loaded ?? '—'}</strong><span>Requirements with review drafts</span></div>
        <div><strong>0</strong><span>Evidence-verified decisions</span></div>
    </div>
    <div class="columns"><div class="catalog">
        <nav aria-label="Generated record categories"><button type="button" class:active={category === 'all'} onclick={() => { category='all';limit=25; }}>All records ({records.length})</button>
            {#each categories as code (code)}<button type="button" class:active={category === code} onclick={() => { category=code;limit=25; }}>{label(code)} ({records.filter(r => r.activity_code === code).length})</button>{/each}
        </nav>
        <label class="search">Search generated content and relationships<input type="search" bind:value={query} oninput={() => limit=25} placeholder="Asset, risk, requirement or accountable role" /></label>
        <div class="rows">
            {#each filtered.slice(0,limit) as record (record.draft.draft_reference)}
                <button type="button" class="record" class:active={detail?.draft.draft_reference === record.draft.draft_reference} onclick={() => inspect(record.draft.draft_reference)}><strong>{record.draft.title}</strong><small>{record.draft.draft_reference} · {record.target_existing_sico_model} · {record.generation_focus_reference ?? 'Mapping pending'}</small></button>
            {:else}<p>No validated Qwen records match this category. Pending tasks are not generated records.</p>{/each}
        </div>
        <p class="muted">Showing {Math.min(limit,filtered.length)} of {filtered.length} generated records.</p>
        {#if filtered.length > limit}<button type="button" onclick={() => limit+=25}>Show more</button>{/if}
        {#if matrix && Array.isArray(matrix.grid)}
            <section class="methodology"><h4>Proposed case risk matrix · {matrix.probability.length} × {matrix.impact.length}</h4><p class="muted">Shared methodology for human review. No scenario ratings or risk appetite have been approved.</p>
                <div class="matrix-scroll"><div class="matrix" style={`grid-template-columns:100px repeat(${matrix.impact.length},minmax(65px,1fr))`}>
                    <span>Probability / Impact</span>{#each matrix.impact as impact}<span>{impact.name}</span>{/each}
                    {#each [...matrix.probability].reverse() as probability, n}<span>{probability.name}</span>
                        {#each matrix.impact as _, i}{@const level=matrix.risk[matrix.grid[matrix.probability.length-1-n][i]]}<span class="cell" style:background-color={/^#[0-9a-f]{6}$/i.test(level?.hexcolor ?? '') ? level.hexcolor : '#537884'}>{level?.name ?? 'Unrated'}</span>{/each}
                    {/each}
                </div></div>
            </section>
        {/if}
    </div><aside aria-label="Selected generated record">
        <h4>Selected draft</h4>
        {#if detail}
            <h4>{detail.draft.title}</h4><p class="muted">{detail.draft.draft_reference} · {detail.draft.record_type}</p><p>{detail.draft.content}</p>
            <dl>{#each detail.draft.proposed_attributes ?? [] as attribute}<div><dt>{label(attribute.field)}</dt><dd>{attribute.proposed_value}</dd></div>{/each}</dl>
            {#if detail.draft.vulnerability_proposal}<h5>Proposed vulnerability · Existing Vulnerability module</h5><p>{detail.draft.vulnerability_proposal.model_fields.description}</p><p class="muted">Potential weakness only · Evidence unverified · Proposed asset {detail.draft.vulnerability_proposal.candidate_asset_draft_reference}</p>{/if}
            <h5>Evidence collection</h5><p>{detail.draft.evidence_request}</p><h5>Uncertainty to resolve</h5><p>{detail.draft.verification_question}</p>
            <h5>Related proposed records</h5><div class="links">{#each detail.draft.related_draft_references ?? [] as ref}<button type="button" onclick={() => inspect(ref)} disabled={!records.some(r => r.draft.draft_reference === ref)}>{ref}</button>{/each}</div>
            <p class="muted">Authorized source focus: {detail.generation_focus_reference ?? 'Mapping pending'}. Provider model: {detail.model_provenance?.model ?? 'Recorded in original response'}. No generated content is substituted on failure.</p>
        {:else}<p>Select a validated draft after generation. The framework plan is not a generated assessment.</p>{/if}
        <p class="boundary">Organizational assumptions, evidence, likelihood and impact, control effectiveness and approvals require human verification. No business records have been created.</p>
    </aside></div>
</section>

<style>
    .case-board{margin:20px 0;color:#e8f0fa}.case-board header{display:flex;justify-content:space-between;gap:12px;align-items:center}.eyebrow{font-size:11px;text-transform:uppercase;letter-spacing:.12em;color:#80dcc8}.badge{border:1px solid #8b7442;border-radius:20px;padding:6px 10px;color:#eed191;font-size:12px}.summary{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:20px 0}.summary>div,aside,.catalog{background:#121e2e;border:1px solid #345064;border-radius:12px;padding:17px}.summary strong{font-size:26px;display:block}.summary span,.muted,small{color:#afc3d5;font-size:12px}.columns{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(260px,.85fr);gap:16px}nav,.links{display:flex;flex-wrap:wrap;gap:6px}button{background:#1b2c40;border:1px solid #3c586e;border-radius:8px;color:#d9e8f6;padding:8px 10px;cursor:pointer;font:inherit;font-size:12px}button.active{background:#195458;border-color:#61ccb3}.search{display:grid;gap:7px;font-size:12px;margin:17px 0}input{padding:10px;border:1px solid #54718a;border-radius:8px;background:#0b192a;color:#edf4fc;min-width:0}.record{display:block;text-align:left;width:100%;margin-bottom:8px;padding:13px}.record strong,.record small{display:block}.record small{margin-top:6px}.rows{max-height:600px;overflow:auto}aside{align-self:start;position:sticky;top:15px;word-break:break-word}aside p,dd{line-height:1.65;font-size:13px}dt{color:#80dcc8;font-size:11px;text-transform:uppercase;margin-top:13px}dd{margin:4px 0 0;white-space:pre-wrap}.boundary{padding-top:15px;border-top:1px solid #3c586e;color:#dec993}.methodology{margin-top:23px}.matrix-scroll{overflow:auto}.matrix{display:grid;gap:4px;min-width:440px;font-size:11px}.matrix>span{padding:9px;text-align:center}.cell{color:#122233;border-radius:5px;font-weight:bold}h3,h4{margin:10px 0}h5{margin:18px 0 5px}button:disabled{opacity:.5;cursor:default}@media(max-width:950px){.columns{grid-template-columns:1fr}aside{position:static}.summary{grid-template-columns:repeat(2,1fr)}}
</style>
