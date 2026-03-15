const fs = require('fs');

const newSvg = fs.readFileSync('/tmp/encoded_svg.txt', 'utf8').trim();

// Fix server chunk
const sf = '/app/build/server/chunks/Logo-BjQkYGJi.js';
let sc = fs.readFileSync(sf, 'utf8');
const i1 = sc.indexOf('data:image/svg+xml,');
const i2 = sc.indexOf('"', i1);
if (i1 >= 0 && i2 > i1) {
  sc = sc.substring(0, i1) + newSvg + sc.substring(i2);
  fs.writeFileSync(sf, sc);
  console.log('Server chunk updated');
} else {
  console.log('Server chunk: pattern not found');
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
} else {
  console.log('Client chunk: pattern not found');
}
