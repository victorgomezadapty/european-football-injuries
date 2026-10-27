import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
const read = name => readFileSync(new URL('../'+name,import.meta.url),'utf8');
const data = JSON.parse(read('web/data/project.json'));
test('all filter medians are supported by their own record counts and sums reconcile',()=>{
  for (const [mode,views] of Object.entries(data.views)) {
    for(const [key,view] of Object.entries(views)) {
      assert.equal(view.injuries.reduce((s,r)=>s+r.count,0),view.count,mode+key);
      assert.equal(view.injuries.reduce((s,r)=>s+r.days,0),view.days,mode+key);
      assert.equal(view.injuries.reduce((s,r)=>s+r.games,0),view.games,mode+key);
      assert(view.injuries.every(r=>r.n===r.count && r.q1<=r.median && r.median<=r.q3));
    }
    const all=views['all|all'];
    assert.equal(data.summary.leagues.reduce((sum,league)=>sum+views[league+'|all'].count,0),all.count);
    assert.equal(data.summary.seasons.reduce((sum,season)=>sum+views['all|'+season].count,0),all.count);
  }
});
test('public source and sensitivity results retain distinct meanings',()=>{
  assert.equal(data.views.raw['all|all'].count,15603);
  assert.equal(data.views.candidate['all|all'].count,14611);
  assert.equal(data.views.raw['all|all'].days,563314);
  assert.equal(data.views.candidate['all|all'].days,532422);
  assert.equal(data.source.license,'CC BY-SA 4.0');
  assert.match(data.source.csv_sha256,/^[a-f0-9]{64}$/);
});
test('public interactive data do not contain individual names or medical histories',()=>{
  const serialized=JSON.stringify(data.views);
  for(const key of ['"player_name"','"player_id"','"injury_start"','"injury_end"'])assert(!serialized.includes(key),key);
  for(const range of Object.values(data.summary.dates))assert.deepEqual(Object.keys(range).sort(),['max','min']);
  for(const views of Object.values(data.views))for(const view of Object.values(views))for(const row of view.injuries)assert.deepEqual(Object.keys(row).sort(),['count','days','games','label','median','n','q1','q3']);
  assert.equal(data.player_record_distribution.reduce((s,r)=>s+r.names,0),4081);
  assert.equal(data.player_record_distribution.reduce((s,r)=>s+r.names*r.records,0),15603);
});
test('both language articles and DOI references are published without placeholder content',()=>{
  const page=read('web/evidence.html');
  assert(!page.includes('{{DISCUSSION_'));
  assert(page.includes('data-content-lang="es"')&&page.includes('data-content-lang="en"'));
  const refs=JSON.parse(read('web/data/references.json')).references;
  assert(refs.length>=8);
  assert(refs.every(r=>/^10\.\d{4,9}\//.test(r.doi)&&r.title&&r.authors?.length&&r.verification_url));
  assert.equal(new Set(refs.map(r=>r.doi)).size,refs.length);
});
test('public downloads and build entry points exist',()=>{
  for(const file of ['injury_burden.csv','duplicate_sensitivity.csv','methodology.md','references.bib','reproducible_source.zip','publication_manifest.json'])assert(existsSync(new URL('../web/downloads/'+file,import.meta.url)),file);
  const home=read('web/index.html');
  assert(home.includes('prefers-reduced-motion')||read('web/styles.css').includes('prefers-reduced-motion'));
  assert(home.includes('motion-toggle'));
  assert(home.includes('Sanan Muzaffarov'));
  assert(!/AI injury predictor|predict who will be injured/i.test(home));
});
