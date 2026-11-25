import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';

const { manifest } = await import('/app/build/server/manifest.js');
const routes = manifest._.routes.map((route) => route.id).sort();
const route = '/(app)/(internal)/sico-ai-next';
assert.equal(routes.filter((id) => id === route).length, 1);
if (process.argv.includes('--baseline')) {
  console.log(JSON.stringify({ routes }));
} else {
  const prior = JSON.parse(fs.readFileSync('/checks/frontend-baseline-routes.json', 'utf8'));
  assert.deepEqual(routes, prior.routes);
  function files(dir) {
    return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => entry.isDirectory()
      ? files(path.join(dir, entry.name)) : [path.join(dir, entry.name)]);
  }
  const serverFiles = files('/app/build/server').filter((name) => name.endsWith('.js'));
  assert.ok(serverFiles.some((name) => fs.readFileSync(name, 'utf8').includes('/ai/workforce/assistant/execute/')));
  assert.ok(serverFiles.some((name) => fs.readFileSync(name, 'utf8').includes('Agent execution')));
  console.log(JSON.stringify({ compiled_agent_action_present: true, execution_section_present: true,
    existing_route_count: routes.length, route_set_unchanged: true }));
}
