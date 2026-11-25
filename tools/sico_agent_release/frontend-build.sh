#!/bin/sh
set -eu
mkdir -p /tmp/frontend
cp -a /source/. /tmp/frontend/
cd /tmp/frontend
export NODE_OPTIONS="${NODE_OPTIONS:---max-old-space-size=2560 --max-semi-space-size=16}"
export MALLOC_ARENA_MAX=2
export GOMAXPROCS=2
export CI=true
export PUBLIC_BACKEND_API_URL=http://backend:8000/api
export PUBLIC_BACKEND_API_EXPOSED_URL=https://localhost:9443/api
# Type declarations are development/checker artifacts, not production runtime code.
# Disable only their emission in this disposable build copy to reduce peak memory.
node --input-type=module <<'JS'
import fs from 'node:fs';
const file = 'vite.config.ts';
const source = fs.readFileSync(file, 'utf8');
const marker = 'emitTsDeclarations: true';
if (source.split(marker).length !== 2) throw new Error('Unexpected declaration-emission configuration');
fs.writeFileSync(file, source.replace(marker, 'emitTsDeclarations: false'));
if (process.env.SICO_LOW_MEMORY_BUILD === 'true') {
  const updated = fs.readFileSync(file, 'utf8');
  const buildMarker = 'sourcemap: false';
  if (updated.split(buildMarker).length !== 2) throw new Error('Unexpected production build configuration');
  fs.writeFileSync(file, updated.replace(buildMarker, 'sourcemap: false, minify: false, reportCompressedSize: false'));
}
JS
node node_modules/@sveltejs/kit/svelte-kit.js sync
node node_modules/vite/bin/vite.js build
test -s build/handler.js
test -s build/index.js
