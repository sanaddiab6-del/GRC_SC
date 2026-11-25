/** Focused compile and server-action checks; run with read-only frontend dependencies. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const dependencyRequire = (name) => require(`/deps/${name}`);
const ts = dependencyRequire('typescript');
const { compile } = dependencyRequire('svelte/compiler');
const route = '/source/src/routes/(app)/(internal)/sico-ai-next';
const source = fs.readFileSync(path.join(route, '+page.svelte'), 'utf8');
const compiled = compile(source, { filename: '+page.svelte', generate: 'server' });
assert.ok(compiled.js.code);
const server = fs.readFileSync(path.join(route, '+page.server.ts'), 'utf8');
const transpiled = ts.transpileModule(server, {
    reportDiagnostics: true,
    compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS }
});
assert.equal(transpiled.diagnostics.length, 0);

let session = true;
let backend;
const exportsObject = {};
vm.runInNewContext(transpiled.outputText, {
    exports: exportsObject,
    require: (name) => {
        if (name === '@sveltejs/kit') return { fail: (status, data) => ({ status, data }) };
        if (name === '$lib/utils/aiOnboardingProxy') return {
            hasAiOnboardingSession: () => session,
            AI_ONBOARDING_SESSION_EXPIRED: { detail: 'Session expired' },
            fetchAiOnboardingBackend: (...args) => backend(...args)
        };
        throw new Error(`Unexpected dependency: ${name}`);
    }
});
const event = (instruction = 'Find the NCA ECC framework and inspect authorized information.') => ({
    request: { formData: async () => ({ get: (key) => key === 'scenario_text' ? instruction : '' }) }
});
const response = (ok, data) => ({ ok, json: async () => data });
const plan = { steps: [], provider_mode: 'configured_local_provider' };
const agent = { trace: [], mode: 'model_driven_read_only_agent', status: 'completed' };

async function main() {
    session = false;
    assert.equal((await exportsObject.actions.run(event())).status, 401);
    session = true;
    assert.equal((await exportsObject.actions.run(event('short'))).status, 400);
    backend = async (_event, endpoint) => response(true, endpoint.includes('/plan/') ? plan : agent);
    let result = await exportsObject.actions.run(event());
    assert.equal(result.sico_agent.status, 'completed');
    assert.equal(result.sico_plan.provider_mode, 'configured_local_provider');
    backend = async (_event, endpoint) => endpoint.includes('/plan/')
        ? response(false, { detail: 'Planning failed' }) : response(true, agent);
    result = await exportsObject.actions.run(event());
    assert.equal(result.sico_agent.status, 'completed');
    assert.equal(result.plan_error, 'Planning failed');
    backend = async (_event, endpoint) => endpoint.includes('/plan/')
        ? response(true, plan) : response(false, { detail: 'Agent unavailable' });
    result = await exportsObject.actions.run(event());
    assert.equal(result.agent_error, 'Agent unavailable');
    assert.ok(result.sico_plan);
    backend = async (_event, endpoint) => {
        if (endpoint.includes('/plan/')) throw new Error('Network failure');
        return response(true, agent);
    };
    result = await exportsObject.actions.run(event());
    assert.equal(result.sico_agent.status, 'completed');
    console.log(JSON.stringify({ svelte_compiled: true, typescript_transpiled: true,
        action_checks_passed: 6, compiler_warnings: compiled.warnings.map((w) => w.code) }));
}
main().catch((error) => { console.error(error); process.exit(1); });
