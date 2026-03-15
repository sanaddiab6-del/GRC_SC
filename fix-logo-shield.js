const fs = require('fs');

// Read the sico-logo.svg and encode it
const svg = fs.readFileSync('/tmp/sico-logo.svg', 'utf8');
const newSvg = 'data:image/svg+xml,' + encodeURIComponent(svg).replace(/%20/g, ' ');

// Fix server chunk
const sf = '/app/build/server/chunks/Logo-BjQkYGJi.js';
let sc = fs.readFileSync(sf, 'utf8');
const i1 = sc.indexOf('data:image/svg+xml,');
const i2 = sc.indexOf('"', i1);
if (i1 >= 0 && i2 > i1) {
  sc = sc.substring(0, i1) + newSvg + sc.substring(i2);
  fs.writeFileSync(sf, sc);
  console.log('Server chunk updated');
}

// Fix client chunk
const cf = '/app/build/client/_app/immutable/chunks/ClMRAvhc.js';
let cc = fs.readFileSync(cf, 'utf8');
const j1 = cc.indexOf('data:image/svg+xml,');
const j2 = cc.indexOf('"', j1);
if (j1 >= 0 && j2 > j1) {
  cc = cc.substring(0, j1) + newSvg + cc.substring(j2);
  fs.writeFileSync(cf, cc);
  console.log('Client chunk updated');
}
