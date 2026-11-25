$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$result=ConvertFrom-Json -InputObject ([IO.File]::ReadAllText((Join-Path $PSScriptRoot 'mock-results.json')))
$payload=@{fixture=$result.fixture;source=[IO.File]::ReadAllText((Join-Path $root 'frontend/src/lib/utils/sicoGenerationPlan.ts'))}|ConvertTo-Json -Depth 30 -Compress
$encoded=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($payload))
$script="const PAYLOAD=JSON.parse(Buffer.from('$encoded','base64').toString('utf8'));`n"+@'
const ts=require('/workspace/node_modules/typescript'),vm=require('vm'),assert=require('assert/strict');
const exportsObject={};
vm.runInNewContext(ts.transpileModule(PAYLOAD.source,{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.CommonJS}}).outputText,{exports:exportsObject});
const f=PAYLOAD.fixture,queue=exportsObject.validateGenerationQueue(f.plan,f.rows);
let saved=[];
while(saved.length<queue.length){
 const next=exportsObject.nextGenerationSlot(queue,saved);assert.ok(next);
 assert.ok(next.dependency_draft_references.every(ref=>saved.some(r=>r.draft.draft_reference===ref)));
 saved.push(f.accepted[next.draft_reference]);
 if(saved.length===6)saved=JSON.parse(JSON.stringify(saved));
}
assert.equal(exportsObject.nextGenerationSlot(queue,saved),null);
const stale=JSON.parse(JSON.stringify(saved));
stale.find(r=>r.activity_number===4).generation_scope_subject='Different scope';
assert.throws(()=>exportsObject.nextGenerationSlot(queue,stale),/no record was reassigned/);
console.log(JSON.stringify({scheduled_records:queue.length,simulated_accepted_records:saved.length,activity_count:new Set(saved.map(r=>r.activity_number)).size,checkpoint_resume:true,scope_reassignment_blocked:true,real_qwen_verified:false,deployed:false}));
'@
$raw=$script|docker exec -i amro-frontend node
$code=$LASTEXITCODE
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'coordinator-results.json'),($raw -join "`n"),(New-Object Text.UTF8Encoding($false)))
Write-Output ($raw -join "`n")
if($code -ne 0){throw 'Coordinator checks failed'}
