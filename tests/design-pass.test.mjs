import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read = name => readFileSync(new URL('../'+name,import.meta.url),'utf8');
const data = JSON.parse(read('web/data/project.json'));
const app = read('web/app.js');
const pattern = new RegExp(app.match(/NON_INJURY_PATTERN = \/(.+?)\/i;/)[1],'i');
const isInjury = row => !pattern.test(row.label);
const sum = (rows,key) => rows.reduce((s,r)=>s+r[key],0);
test('non-injury filter matches Sports Rehab Intelligence (39 labels, 3,093 records)',()=>{
  const rows = data.views.raw['all|all'].injuries;
  const excluded = rows.filter(r=>!isInjury(r));
  assert.equal(excluded.length,39);
  assert.equal(sum(excluded,'count'),3093);
  assert(excluded.some(r=>r.label==='Corona virus'));
  assert.equal(sum(rows.filter(isInjury),'count'),12510);
});
test('hamstring is the most frequent injury label and cruciate has about 8% more days',()=>{
  const rows = data.views.raw['all|all'].injuries.filter(isInjury);
  const byCount = [...rows].sort((a,b)=>b.count-a.count)[0], byDays = [...rows].sort((a,b)=>b.days-a.days)[0];
  assert.equal(byCount.label,'Hamstring injury');
  assert.equal(byDays.label,'Cruciate ligament tear');
  assert.equal(Math.round(100*(byDays.days/byCount.days-1)),8);
});
test('season claims: 21/22 has most records overall but fewest injuries; injury days +25%',()=>{
  const s = data.summary.seasons.map(season=>{const rows=data.views.raw['all|'+season].injuries;return {season,all:sum(rows,'count'),inj:sum(rows.filter(isInjury),'count'),days:sum(rows.filter(isInjury),'days')};});
  assert.equal([...s].sort((a,b)=>b.all-a.all)[0].season,'21/22');
  assert.equal([...s].sort((a,b)=>a.inj-b.inj)[0].season,'21/22');
  assert.equal(Math.round(100*(s.at(-1).days/s[0].days-1)),25);
  for (let i=1;i<s.length;i++) assert(s[i].days>s[i-1].days);
});
test('knee share: 14% of injury records, 30% of days',()=>{
  const rows = data.views.raw['all|all'].injuries.filter(isInjury);
  const knee = rows.filter(r=>/knee|cruciate|menisc|patell|inner ligament|collateral/i.test(r.label));
  assert.equal(Math.round(100*sum(knee,'count')/sum(rows,'count')),14);
  assert.equal(Math.round(100*sum(knee,'days')/sum(rows,'days')),30);
});
test('no long dashes in new page prose',()=>{
  const home = read('web/index.html');
  assert(!/[–—]/.test(home));
});
