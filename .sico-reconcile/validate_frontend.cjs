/** Isolated component compilation and the existing six mocked server-action checks. */
const fs = require('node:fs');
const vm = require('node:vm');
const ts = require('/workspace/node_modules/typescript');
const svelte = require('/workspace/node_modules/svelte/compiler');
const sources = Object.fromEntries(Object.entries(PAYLOAD.sources).map(([p,v])=>[p,Buffer.from(v,'base64').toString('utf8')]));
const mainPage = 'frontend/src/routes/(app)/(internal)/sico-ai-next/+page.svelte';
const warnings = [];
let components = 0, typescript = 0;
for (const [p,source] of Object.entries(sources)) {
    if (p.endsWith('.svelte') && p !== mainPage) {
        const result = svelte.compile(source,{filename:p,generate:'server'});
        if (!result.js.code) throw new Error('No compiled component: '+p);
        components++;
        warnings.push(...result.warnings.map(w=>({file:p,code:w.code})));
    } else if (p.endsWith('.ts')) {
        const result = ts.transpileModule(source,{fileName:p,reportDiagnostics:true,compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.CommonJS}});
        if (result.diagnostics.length) throw new Error('TypeScript syntax diagnostics: '+p);
        typescript++;
    }
}
let originalChecks;
function sandboxRequire(name) {
    if (name.startsWith('/deps/')) return require('/workspace/node_modules/'+name.slice(6));
    if (name === 'node:fs') return {
        readFileSync(p) {
            const key = 'frontend/'+p.slice('/source/'.length);
            if (!(key in sources)) throw new Error('Unscoped file read: '+p);
            return sources[key];
        }
    };
    return require(name);
}
async function main() {
    await vm.runInNewContext(Buffer.from(PAYLOAD.checkScript,'base64').toString('utf8'), {
        require:sandboxRequire,
        console:{log:s=>{originalChecks=JSON.parse(s)},error:e=>{throw e}},
        process:{exit:code=>{throw new Error('Existing checks failed: '+code)}}
    });
    if (!originalChecks || originalChecks.action_checks_passed !== 6) throw new Error('Existing action checks did not complete');
    components++;
    warnings.push(...originalChecks.compiler_warnings.map(code=>({file:mainPage,code})));
    console.log(JSON.stringify({node_version:process.version,svelte_version:svelte.VERSION,typescript_version:ts.version,
        svelte_components_compiled:components,typescript_files_transpiled:typescript,
        action_checks_passed:originalChecks.action_checks_passed,compiler_warnings:warnings,
        full_frontend_build:false,successful:true}));
}
main().catch(e=>{console.error(e);process.exitCode=1});
