const fs = require('fs');

// Fix server layout chunk - change favicon.ico to favicon.svg with proper type
const layoutFile = '/app/build/server/chunks/_layout.svelte-sTjjKRru.js';
let content = fs.readFileSync(layoutFile, 'utf8');
content = content.replace(
  '<link rel="icon" href="/favicon.ico"/>',
  '<link rel="icon" type="image/svg+xml" href="/favicon.svg"/>'
);
fs.writeFileSync(layoutFile, content);
console.log('Layout chunk updated: favicon.ico -> favicon.svg');
