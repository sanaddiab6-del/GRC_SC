const ts=require('/workspace/node_modules/typescript');
const {compile,VERSION}=require('/workspace/node_modules/svelte/compiler');
const vm=require('node:vm'),assert=require('node:assert/strict');
const sources=Object.fromEntries(Object.entries(PAYLOAD.sources).map(([p,v])=>[p,Buffer.from(v,'base64').toString('utf8')]));
const virtualFile='/tmp/sicoGenerationPlan.ts';
const host=ts.createCompilerHost({});
const originalGet=host.getSourceFile.bind(host);
host.getSourceFile=(name,version,...rest)=>name===virtualFile ? ts.createSourceFile(name,sources['frontend/src/lib/utils/sicoGenerationPlan.ts'],version,true) : originalGet(name,version,...rest);
const program=ts.createProgram([virtualFile],{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.CommonJS,strict:true,noEmit:true,types:[],skipLibCheck:true},host);
const diagnostics=ts.getPreEmitDiagnostics(program);
assert.equal(diagnostics.length,0,diagnostics.map(d=>ts.flattenDiagnosticMessageText(d.messageText,'\n')).join('\n'));
let components=0,typescripts=0,warnings=[];
let caseComponentCode;
for(const [p,source] of Object.entries(sources)){
    if(p.endsWith('.svelte')){const result=compile(source,{filename:p,generate:'server'});assert.ok(result.js.code);if(p.endsWith('SicoGeneratedCase.svelte'))caseComponentCode=result.js.code;components++;warnings.push(...result.warnings.map(w=>({file:p,code:w.code})))}
    if(p.endsWith('.ts')){const result=ts.transpileModule(source,{fileName:p,reportDiagnostics:true,compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.CommonJS}});assert.equal(result.diagnostics.length,0);typescripts++}
}
const moduleObject={exports:{}};
vm.runInNewContext(Buffer.from(PAYLOAD.test,'base64').toString('utf8'),{module:moduleObject});
moduleObject.exports({ts,sources,vm,assert,coordinationFixture:PAYLOAD.coordination_fixture}).then(async checks=>{
    let genuineQwenRecordsRendered=0;
    if(PAYLOAD.demo_evidence?.AcceptedModelRecords?.length){
        const {pathToFileURL}=require('node:url');
        const workspaceRequire=require('node:module').createRequire('/workspace/package.json');
        const code=caseComponentCode.replace(/from (['"])(svelte[^'"]*)\1/g,(_,quote,name)=>'from '+JSON.stringify(pathToFileURL(workspaceRequire.resolve(name)).href));
        const component=await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64'));
        const {render}=workspaceRequire('svelte/server');
        const data=PAYLOAD.demo_evidence;
        const result=render(component.default,{props:{items:data.AcceptedModelRecords,plan:null,organization:data.Organization,framework:data.Framework.name}});
        for(const record of data.AcceptedModelRecords){assert.ok(result.body.includes(record.draft.title.replaceAll('&','&amp;').replaceAll('<','&lt;')));genuineQwenRecordsRendered++}
    }
    console.log(JSON.stringify({svelte:VERSION,compiled_components:components,typescript_transpiled:typescripts,coordinator_strict_typecheck:true,checks,genuine_qwen_records_rendered:genuineQwenRecordsRendered,warning_counts:Object.fromEntries([...new Set(warnings.map(w=>w.code))].map(code=>[code,warnings.filter(w=>w.code===code).length])),full_frontend_build:false,successful:true}));
}).catch(e=>{console.error(e);process.exitCode=1});
