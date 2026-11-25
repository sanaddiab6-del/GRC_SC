/** Invoked by the focused runner with installed TypeScript, never a full build. */
module.exports = async ({ ts, sources, vm, assert, coordinationFixture }) => {
    let checks=0;
    const transpile = source => ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
    const coordination={};
    vm.runInNewContext(transpile(sources['frontend/src/lib/utils/sicoGenerationPlan.ts']),{exports:coordination});
    const rows=[{requirement_id:'source-a',reference:'AC-A'},{requirement_id:'source-b',reference:'RC-B'}];
    const slot=(step,index,parents=[],row=rows[0])=>({activity_number:step,draft_index:index,
        draft_reference:coordination.draftReference(step,index),theme:'identity_and_access',
        focus_requirement_id:row.requirement_id,focus_requirement_reference:row.reference,
        dependency_draft_references:parents});
    const queue=[slot(4,1),slot(5,1,['draft-04-01']),slot(6,1,['draft-04-01','draft-05-01']),
        slot(7,1,['draft-06-01']),slot(4,2,[],rows[1]),slot(10,18,['draft-07-01'],rows[1])];
    assert.equal(coordination.validateGenerationQueue({generation_queue:queue},rows).length,6);checks++;
    assert.throws(()=>coordination.validateGenerationQueue({generation_queue:[...queue,{...queue[0]}]},rows));checks++;
    assert.throws(()=>coordination.validateGenerationQueue({generation_queue:[{...queue[0],focus_requirement_id:'forged'}]},rows));checks++;
    const accepted=queue.slice(0,4).map(s=>({activity_number:s.activity_number,provenance:'qwen_quality_single_authenticated_v7',quality_contract_checked:true,business_records_written:false,draft:{draft_reference:s.draft_reference,status:'new_unsaved_ai_draft_pending_verification',title:'Preserved operational content',content:'A complete model-generated operational description.',record_type:s.activity_number===4?'Asset':'Other',proposed_attributes:[{field:'asset_reference',proposed_value:'draft-04-01'}],related_draft_references:s.dependency_draft_references}}));
    assert.equal(coordination.nextGenerationSlot(queue,accepted).draft_reference,'draft-04-02');checks++;
    assert.equal(coordination.nextGenerationSlot(queue,[...accepted,{...accepted[0],draft:{...accepted[0].draft,draft_reference:'draft-04-02'}}]).draft_reference,'draft-10-18');checks++;
    const context=coordination.plannedDraftContext(queue[2],accepted);
    assert.equal(context.length,2);assert.equal(context[1].proposed_attributes[0].proposed_value,'draft-04-01');checks++;
    assert.throws(()=>coordination.nextGenerationSlot(queue,[...accepted,{...accepted[0],provenance:'imported_html_review_required',draft:{...accepted[0].draft,draft_reference:'draft-04-02'}}]),/cannot be silently replaced/);checks++;
    const actualQueue=coordination.validateGenerationQueue(coordinationFixture.plan,coordinationFixture.rows);
    const completed=[];
    while(completed.length<actualQueue.length){
        const task=coordination.nextGenerationSlot(actualQueue,completed);
        assert.ok(task,'The actual Python planner queue must not deadlock');
        assert.ok(task.dependency_draft_references.every(ref=>completed.some(r=>r.draft.draft_reference===ref)));
        if([14,16].includes(task.activity_number))assert.ok(actualQueue.filter(s=>s.activity_number<task.activity_number).every(s=>completed.some(r=>r.draft.draft_reference===s.draft_reference)));
        completed.push({activity_number:task.activity_number,provenance:'qwen_quality_single_authenticated_v7',quality_contract_checked:true,business_records_written:false,draft:{draft_reference:task.draft_reference,status:'new_unsaved_ai_draft_pending_verification'}});
    }
    assert.equal(completed.filter(r=>r.activity_number===10).length,coordinationFixture.rows.length);
    assert.equal(coordination.nextGenerationSlot(actualQueue,completed),null);checks++;
    let session=true, sent, response;
    const actions={};
    vm.runInNewContext(transpile(sources['frontend/src/routes/(app)/(internal)/sico-ai-next/+page.server.ts']),{
        exports:actions,require:name=>{
            if(name==='@sveltejs/kit')return {fail:(status,data)=>({status,data})};
            if(name==='$lib/utils/aiOnboardingProxy')return {hasAiOnboardingSession:()=>session,AI_ONBOARDING_SESSION_EXPIRED:{detail:'Expired'},fetchAiOnboardingBackend:async(event,url,body)=>{sent={url,body};return {ok:true,json:async()=>response}}};
            throw Error(name);
        }
    });
    const fields={organization_name:'Test dispatch operator',framework_name:'Selected installed edition',problem:'Assess operator authentication for sensitive delivery dispatch configuration.',activity_number:'6',draft_index:'18',source_digest:'a'.repeat(64),focus_requirement_reference:'AC-A',focus_theme:'identity_and_access',previous_drafts:'[]'};
    const event={request:{formData:async()=>({get:k=>fields[k]??null})}};
    response={quality_contract_checked:true,business_records_written:false,activity_number:6,source_digest:fields.source_digest,generation_focus_reference:'AC-A',draft:{draft_reference:'draft-06-18'}};
    assert.ok((await actions.actions.quality_draft_one(event)).quality_draft_one);assert.equal(sent.body.focus_theme,fields.focus_theme);assert.equal(sent.body.focus_requirement_reference,'AC-A');checks++;
    response={...response,generation_focus_reference:'forged'};assert.equal((await actions.actions.quality_draft_one(event)).status,502);checks++;
    fields.focus_theme='untrusted topic';assert.equal((await actions.actions.quality_draft_one(event)).status,400);checks++;
    session=false;assert.equal((await actions.actions.quality_draft_one(event)).status,401);checks++;
    return checks;
};
