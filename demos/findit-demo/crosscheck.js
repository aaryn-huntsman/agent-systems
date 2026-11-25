#!/usr/bin/env node
/* Cross-check: the browser-side cosine ranking, computed from the SHIPPED
 * rounded vectors in findit-data.js, must reproduce the Python pipeline's
 * full-precision top-5 for every preset question.
 * Also re-derives hit@5 from the JS ranking and compares with META.
 */
const fs = require('fs');
const path = require('path');

const jsFile = path.join(__dirname, 'findit-data.js');
const resultsFile = path.join(__dirname, 'results.json');

const src = fs.readFileSync(jsFile, 'utf8');
const jsonText = src.slice(src.indexOf('{'), src.lastIndexOf('}') + 1);
const D = JSON.parse(jsonText);
const R = JSON.parse(fs.readFileSync(resultsFile, 'utf8'));

function cosine(q, v) { let s = 0; for (let i = 0; i < q.length; i++) s += q[i] * v[i]; return s; }
function top5(q) {
  return D.vectors
    .map((v, i) => ({ i, s: cosine(q, v) }))
    .sort((a, b) => (b.s - a.s) || (a.i - b.i))
    .slice(0, 5)
    .map(t => D.chunks[t.i].id);
}

let allOk = true;
let jsHits = 0;
D.questions.forEach((q, qi) => {
  const jsTop = top5(q.vector);
  const pyTop = R.questions[qi].top5.map(t => t.id);
  const match = JSON.stringify(jsTop) === JSON.stringify(pyTop);
  const shippedMatch = JSON.stringify(jsTop) === JSON.stringify(q.python_top5);
  const hit = jsTop.some(id => q.gold.includes(id));
  if (hit) jsHits++;
  const scored = D.vectors.map((v, i) => cosine(q.vector, v)).sort((a, b) => b - a);
  const margin = scored[4] - scored[5];
  console.log(`Q${qi + 1}: js==python ${match ? 'MATCH' : 'MISMATCH'} | js==shipped ${shippedMatch ? 'MATCH' : 'MISMATCH'} | hit ${hit} | rank5-6 margin ${margin.toFixed(5)}`);
  if (!match) { allOk = false; console.log('  js:', jsTop.join(', ')); console.log('  py:', pyTop.join(', ')); }
});
const metaHits = D.META.hit_at_5;
console.log(`JS-derived hit@5: ${jsHits}/${D.questions.length} | META says: ${metaHits}`);
console.log(`Dims: ${D.META.dims} | chunks: ${D.chunks.length} | vectors: ${D.vectors.length} | vector width ok: ${D.vectors.every(v => v.length === D.META.dims)}`);
console.log(allOk && `${jsHits}/${D.questions.length}` === metaHits ? 'CROSS-CHECK PASS' : 'CROSS-CHECK FAIL');
process.exit(allOk ? 0 : 1);
