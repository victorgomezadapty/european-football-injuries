'use strict';
(() => {
  const params = new URLSearchParams(location.search);
  let lang = params.get('lang') === 'en' ? 'en' : params.get('lang') === 'es' ? 'es' : localStorage.getItem('football-language') === 'en' ? 'en' : 'es';
  let project = null;
  let referenceData = [];
  let selected = 'Hamstring injury';
  const t = (es, en) => lang === 'es' ? es : en;
  const n = (value, decimals = 0) => new Intl.NumberFormat(lang === 'es' ? 'es-ES' : 'en-GB', { maximumFractionDigits: decimals, minimumFractionDigits: decimals, useGrouping: true }).format(value);
  const text = (tag, value, cls = '') => { const el = document.createElement(tag); el.textContent = value; if (cls) el.className = cls; return el; };
  const svgNS = 'http://www.w3.org/2000/svg';

  // Same non-injury filter and body regions as Sports Rehab Intelligence (web/synthesis.js), so both sites report the same numbers.
  const NON_INJURY_PATTERN = /corona|covid|virus|\bill\b|illness|flu|influenza|fever|\bcold\b|quarantine|infection|tonsil|stomach|\brest\b|fitness|sick|bronch|pneumon|gastro|appendic|malaria|cardiac|heart|tooth|dental|personal|family|suspen|vacc|isolation|angina|kidney|cancer|appendectomy|mononucle|poisoning|intestinal|shingles|chickenpox|skin disease|allergic|depression|circulation/i;
  const isInjury = row => !NON_INJURY_PATTERN.test(row.label);
  const REGIONS = [
    ['knee', 'Rodilla', 'Knee', /knee|cruciate|menisc|patell|inner ligament|collateral/i],
    ['ankle_foot', 'Tobillo y pie', 'Ankle and foot', /ankle|achilles|foot|metatars|toe|heel|plantar/i],
    ['hip_groin', 'Cadera e ingle', 'Hip and groin', /\bhip|groin|adductor|pubi|pubal/i],
    ['thigh', 'Muslo', 'Thigh', /hamstring|thigh|quadri|dead leg/i],
    ['lower_leg', 'Pierna', 'Lower leg', /calf|\bshin(?!gles)|tibia|fibula|lower leg/i]
  ];
  const regionOf = label => (REGIONS.find(r => r[3].test(label)) || ['other'])[0];
  const GLOSS = {'Hamstring injury':'Lesión de isquiotibiales','Hamstring muscle injury':'Lesión muscular de isquiotibiales','Muscle injury':'Lesión muscular','muscular problems':'Problemas musculares','Knee injury':'Lesión de rodilla','Knee problems':'Problemas de rodilla','Knee surgery':'Cirugía de rodilla','Ankle injury':'Lesión de tobillo','Ankle problems':'Problemas de tobillo','Knock':'Golpe','Cruciate ligament tear':'Rotura de ligamento cruzado','Cruciate ligament injury':'Lesión de ligamento cruzado','Achilles tendon rupture':'Rotura del tendón de Aquiles','Adductor injury':'Lesión de aductores','Adductor pain':'Dolor de aductores','Back problems':'Problemas de espalda','Calf injury':'Lesión de gemelo','Calf problems':'Problemas de gemelo','Dead leg':'Contusión en el muslo','Foot injury':'Lesión de pie','Groin injury':'Lesión inguinal','Meniscus injury':'Lesión de menisco','Muscle fatigue':'Fatiga muscular','Shoulder injury':'Lesión de hombro','Thigh problems':'Problemas en el muslo','Torn muscle fiber':'Rotura de fibras','Corona virus':'Coronavirus','Ill':'Enfermedad','Fitness':'Falta de forma física','flu':'Gripe'};
  const gloss = label => lang === 'es' && GLOSS[label] ? GLOSS[label] : '';
  const sum = (rows, key) => rows.reduce((total, row) => total + row[key], 0);
  const pct = (value, decimals = 0) => n(100 * value, decimals) + (lang === 'es' ? ' %' : '%');
  function chartWidth(svg, fallback, min = 300) { const w = Math.round(svg.getBoundingClientRect().width || svg.parentElement?.getBoundingClientRect().width || fallback); return Math.max(min, w || fallback); }
  function svgNode(tag, attrs = {}, value) { const el = document.createElementNS(svgNS, tag); for (const [key, val] of Object.entries(attrs)) el.setAttribute(key, String(val)); if (value !== undefined) el.textContent = value; return el; }
  function applyLanguage() {
    document.documentElement.lang = lang;
    document.querySelector('nav')?.setAttribute('aria-label',t('Principal','Main navigation'));
    document.querySelector('.languages')?.setAttribute('aria-label',t('Idioma','Language'));
    document.querySelector('.hero-art')?.setAttribute('aria-label',t('Campo conceptual animado y mediana reportada de 18 días por ausencia','Conceptual animated pitch and a reported median of 18 days per absence'));
    document.title = document.querySelector('.evidence-hero') ? t('Discusión y evidencia · Football Injury Burden','Discussion and evidence · Football Injury Burden') : t('Football Injury Burden · El coste de no estar','Football Injury Burden · The cost of being absent');
    document.querySelectorAll('[data-es][data-en]').forEach(el => { el.textContent = el.dataset[lang]; });
    document.querySelectorAll('[data-lang]').forEach(el => el.setAttribute('aria-pressed', String(el.dataset.lang === lang)));
    document.querySelectorAll('.lang-content').forEach(el => { el.hidden = el.dataset.contentLang !== lang; });
    document.querySelectorAll('a[href^="/evidence"], a[href="/"], a[href^="/?lang="]').forEach(el => { const url=new URL(el.getAttribute('href'),location.origin);url.searchParams.set('lang',lang);el.href=url.pathname+url.search+url.hash; });
    const pause = document.querySelector('#motion-toggle');
    if (pause) pause.setAttribute('aria-label', document.body.classList.contains('motion-paused') ? t('Activar animaciones','Play animations') : t('Pausar animaciones','Pause animations'));
    const values = [15603, 4081, 145, 5];
    document.querySelectorAll('.hero-stats strong').forEach((el, idx) => el.textContent = n(values[idx]));
    if (project && document.querySelector('#burden-chart')) { drawMiniBars(); renderExplorer(); drawHistory(); drawSeasons(); drawRegions(); }
    renderReferences();
  }
  document.querySelectorAll('[data-lang]').forEach(el => el.addEventListener('click', () => { lang = el.dataset.lang; localStorage.setItem('football-language', lang); const url = new URL(location); url.searchParams.set('lang', lang); history.replaceState({}, '', url); applyLanguage(); }));
  document.querySelector('#motion-toggle')?.addEventListener('click', (event) => { const paused = document.body.classList.toggle('motion-paused'); event.currentTarget.setAttribute('aria-pressed', String(paused)); event.currentTarget.textContent = paused ? '▶' : 'Ⅱ'; applyLanguage(); });
  if ('IntersectionObserver' in window) {
    document.documentElement.classList.add('js');
    const observer = new IntersectionObserver(entries => entries.forEach(entry => { if (entry.isIntersecting) { entry.target.classList.add('in-view'); observer.unobserve(entry.target); } }), { threshold: .06 });
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
  }
  applyLanguage();
  function renderReferences() {
    const list = document.querySelector('#reference-list');
    if (!list || !referenceData.length) return;
    list.replaceChildren();
    for (const ref of referenceData) {
      const li = document.createElement('li'); li.id = 'ref-' + ref.id;
      li.append(text('span', `[${ref.number || referenceData.indexOf(ref)+1}]`, 'ref-id'), document.createElement('br'), text('strong', ref.title));
      const authors = Array.isArray(ref.authors) ? ref.authors.join(', ') : ref.authors;
      li.append(text('div', `${authors} (${ref.year}). ${ref.journal || ''}`));
      const link = text('a', `DOI: ${ref.doi}`); link.href = ref.url; li.append(link);
      li.append(text('p', ref.limitation || '', 'ref-limit'));
      list.append(li);
    }
  }
  function activeView() {
    const mode = document.querySelector('#view-filter')?.value || 'raw';
    const league = document.querySelector('#league-filter')?.value || 'all';
    const season = document.querySelector('#season-filter')?.value || 'all';
    const view = project.views[mode][`${league}|${season}`];
    if (!view || (document.querySelector('#scope-filter')?.value || 'injury') === 'all') return view;
    const injuries = view.injuries.filter(isInjury);
    return { ...view, injuries, count: sum(injuries, 'count'), days: sum(injuries, 'days'), games: sum(injuries, 'games'), scoped: true };
  }
  function drawMiniBars() {
    const rows = project.views.raw['all|all'].injuries.filter(isInjury);
    for (const [id, metric] of [['frequency-bars','count'],['burden-bars','days']]) {
      const container = document.getElementById(id); if (!container) continue;
      const top = [...rows].sort((a,b) => b[metric] - a[metric]).slice(0,4);
      container.replaceChildren();
      for (const row of top) {
        const bar = text('div', '', 'mini-bar'); const label = text('span', gloss(row.label) || row.label, 'label'); label.title = row.label;
        const track = text('div', '', 'track'); const fill = text('div', '', 'fill'); fill.style.setProperty('--width', `${100 * row[metric] / top[0][metric]}%`); track.append(fill);
        bar.append(label,track,text('span',n(row[metric]),'value')); container.append(bar);
      }
    }
  }
  function showDetail(row) {
    selected = row.label;
    const aside = document.getElementById('injury-detail'); aside.replaceChildren();
    aside.append(text('span', t('ETIQUETA ORIGINAL','ORIGINAL SOURCE LABEL'), 'mono'), text('h3',row.label)); if (gloss(row.label)) aside.append(text('p', gloss(row.label), 'gloss')); if (!isInjury(row)) aside.append(text('p', t('Ausencia no lesiva según el filtro común.','Non-injury absence under the shared filter.'), 'gloss warn'));
    const dl = document.createElement('dl');
    for (const [label,value] of [
      [t('Registros','Records'),n(row.count)],
      [t('Mediana de días','Median days'),n(row.median, row.median % 1 ? 1 : 0)],
      [t('IQR de días','Days IQR'),`${n(row.q1,1)} ${t('a','to')} ${n(row.q3,1)}`],
      [t('Días sumados','Summed days'),n(row.days)],
      [t('Partidos sumados','Summed matches'),n(row.games)],
      [t('Duraciones válidas','Valid durations'),n(row.n)]
    ]) { const div = document.createElement('div'); div.append(text('dt',label),text('dd',value)); dl.append(div); }
    aside.append(dl,text('p',t('Duración por registro. Los días y partidos son sumas de episodios y pueden repetirse. No es un pronóstico clínico.','Per-record duration. Days and matches are episode sums and may repeat. This is not a clinical prognosis.')));
    document.querySelectorAll('.bubble').forEach(el => { const isSelected = el.dataset.label === selected; el.classList.toggle('selected',isSelected); el.setAttribute('aria-pressed',String(isSelected)); el.setAttribute('tabindex',isSelected?'0':'-1'); });
  }
  function renderExplorer() {
    const view = activeView(); if (!view) return;
    document.querySelector('.chart-axis-note span').textContent=t('Ambos ejes en escala logarítmica. Etiquetas originales en inglés, con traducción en la ficha. Teclado: flechas para recorrer etiquetas.','Both axes use logarithmic scales. Original English labels retained. Keyboard: arrow keys move between labels.');
    const stats = document.querySelector('#explorer-kpis'); stats.replaceChildren();
    for (const [value,label] of [[view.count,t('registros en esta vista','records in this view')],[view.days,t('días reportados sumados','reported days summed')],[view.games,t('partidos reportados sumados','reported missed matches summed')],[view.names,view.scoped?t('nombres (todas las ausencias)','names (all absences)'):t('nombres registrados','recorded names')]]) {
      const div = text('div','','kpi'); div.append(text('strong',n(value)),text('span',label)); stats.append(div);
    }
    const rows = view.injuries;
    const chart = document.querySelector('#burden-chart'); chart.replaceChildren();
    chart.setAttribute('aria-label',t('Matriz interactiva: registros, mediana de días y partidos perdidos. La tabla ofrece los mismos resultados.','Interactive matrix: records, median days and missed matches. The table offers the same results.'));
    chart.append(svgNode('title',{},t('Carga de ausencias por etiqueta','Absence burden by source label')));
    const W=chartWidth(chart,860),narrow=W<560,H=narrow?Math.round(W*0.9):430,L=narrow?44:65,R=narrow?14:26,T=narrow?16:30,B=narrow?50:60; chart.setAttribute('viewBox',`0 0 ${W} ${H}`);
    const maxX = Math.max(10,...rows.map(r=>r.count))*1.2; const rMax = narrow ? 16 : 26;
    const maxY = Math.max(10,...rows.map(r=>r.median))*1.3;
    const x = value => L + Math.log10(Math.max(1,value))/Math.log10(maxX)*(W-L-R);
    const y = value => H-B-Math.log10(Math.max(1,value))/Math.log10(maxY)*(H-T-B);
    for (const tick of [1,10,100,1000,10000]) {
      if (tick <= maxX && !(narrow && tick===10000)) { chart.append(svgNode('line',{x1:x(tick),x2:x(tick),y1:T,y2:H-B,class:'gridline'}),svgNode('text',{x:x(tick),y:H-B+22,'text-anchor':'middle',class:'axis-tick'},n(tick))); }
      if (tick <= maxY) { chart.append(svgNode('line',{x1:L,x2:W-R,y1:y(tick),y2:y(tick),class:'gridline'}),svgNode('text',{x:L-12,y:y(tick)+4,'text-anchor':'end',class:'axis-tick'},n(tick))); }
    }
    chart.append(svgNode('text',{x:(L+W-R)/2,y:H-10,'text-anchor':'middle',class:'axis-label'},t('Registros · escala log','Records · log scale')));
    chart.append(svgNode('text',{transform:`translate(${narrow?12:17} ${(T+H-B)/2}) rotate(-90)`,'text-anchor':'middle',class:'axis-label'},t('Mediana de días · escala log','Median days · log scale')));
    const maxGames = Math.max(1,...rows.map(r=>r.games));
    // A common maximum within the active view, and area (r²) proportional to games.
    for (const row of [...rows].sort((a,b)=>b.games-a.games)) {
      const circle = svgNode('circle',{cx:x(row.count),cy:y(row.median),r:Math.max(1.5,Math.sqrt(row.games/maxGames)*rMax),class:'bubble',tabindex:0,role:'button','aria-pressed':'false','aria-label':`${row.label}: ${n(row.count)} ${t('registros','records')}, ${n(row.median,1)} ${t('días de mediana','median days')}`});
      circle.dataset.label=row.label;
      circle.append(svgNode('title',{},`${row.label} · ${n(row.count)} / ${n(row.median,1)} ${t('días','days')}`));
      circle.addEventListener('pointerenter',()=>showDetail(row)); circle.addEventListener('focus',()=>showDetail(row)); circle.addEventListener('click',()=>showDetail(row));
      circle.addEventListener('keydown',event=>{
        if (event.key==='Enter'||event.key===' ') {event.preventDefault();showDetail(row);}
        const points=[...chart.querySelectorAll('.bubble')];const i=points.indexOf(circle);
        const next={ArrowRight:(i+1)%points.length,ArrowDown:(i+1)%points.length,ArrowLeft:(i-1+points.length)%points.length,ArrowUp:(i-1+points.length)%points.length,Home:0,End:points.length-1}[event.key];
        if(next!==undefined){event.preventDefault();points[next].focus();}
      });
      chart.append(circle);
    }
    const body=document.querySelector('#injury-table'); body.replaceChildren();
    for (const row of [...rows].sort((a,b)=>b.days-a.days)) { const tr=document.createElement('tr'); const first=document.createElement('td'); const button=text('button',row.label); button.type='button'; button.addEventListener('click',()=>{showDetail(row);document.getElementById('injury-detail').scrollIntoView({block:'nearest',behavior:document.body.classList.contains('motion-paused')?'instant':'smooth'});});first.append(button);tr.append(first);for (const value of [row.count,row.median,row.days,row.games]) tr.append(text('td',n(value,value%1?1:0)));body.append(tr); }
    const chosen=rows.find(r=>r.label===selected)||rows[0]; if(chosen) showDetail(chosen);
  }
  function drawHistory() {
    const chart=document.querySelector('#history-chart');if(!chart)return;chart.replaceChildren();
    const rows=project.player_record_distribution;
    const W=chartWidth(chart,700),narrow=W<560,H=narrow?260:280,L=45,R=15,T=20,B=53; chart.setAttribute('viewBox',`0 0 ${W} ${H}`);
    const max=Math.max(...rows.map(r=>r.names));const bw=(W-L-R)/rows.length;
    chart.append(svgNode('title',{},t('Distribución de registros por nombre en la fuente original','Distribution of records per name in the original source')));
    for(const tick of [0,400,800,1200,1600]) if(tick<=max){const yy=H-B-tick/max*(H-T-B);chart.append(svgNode('line',{x1:L,x2:W-R,y1:yy,y2:yy,class:'history-line'}),svgNode('text',{x:L-8,y:yy+4,'text-anchor':'end',class:'history-tick'},n(tick)));}
    rows.forEach((row,i)=>{const height=row.names/max*(H-T-B);const rect=svgNode('rect',{x:L+i*bw+3,y:H-B-height,width:Math.max(3,bw-6),height,class:'history-bar'});rect.append(svgNode('title',{},`${row.records} ${t('registros','records')}: ${n(row.names)} ${t('nombres','names')}`));chart.append(rect);if(i%(narrow?4:2)===0)chart.append(svgNode('text',{x:L+(i+.5)*bw,y:H-B+20,'text-anchor':'middle',class:'history-tick'},row.records));});
    chart.append(svgNode('text',{x:W/2,y:H-4,'text-anchor':'middle',class:'history-tick'},t('Registros por nombre (no por jugador verificado)','Records per name (not verified player identity)')));
  }

  function drawSeasons() {
    const chart = document.querySelector('#season-chart'); if (!chart) return; chart.replaceChildren();
    const seasons = project.summary.seasons.map(season => { const rows = project.views.raw['all|' + season].injuries; const inj = rows.filter(isInjury); const covid = rows.filter(r => /corona|covid/i.test(r.label)); return { season, all: sum(rows, 'count'), injury: sum(inj, 'count'), other: sum(rows, 'count') - sum(inj, 'count'), covid: sum(covid, 'count'), days: sum(inj, 'days') }; });
    const W = chartWidth(chart, 760), narrow = W < 560, H = narrow ? 320 : 340, L = narrow ? 40 : 56, R = 8, T = 20, B = narrow ? 66 : 46;
    chart.setAttribute('viewBox', `0 0 ${W} ${H}`);
    chart.append(svgNode('title', {}, t('Registros por temporada: lesiones y ausencias no lesivas', 'Records per season: injuries and non-injury absences')));
    const max = 3500, y = v => H - B - v / max * (H - T - B), band = (W - L - R) / seasons.length, bw = Math.min(64, band * 0.56);
    for (const tick of [0, 1000, 2000, 3000]) chart.append(svgNode('line', { x1: L, x2: W - R, y1: y(tick), y2: y(tick), class: 'gridline' }), svgNode('text', { x: L - 8, y: y(tick) + 4, 'text-anchor': 'end', class: 'axis-tick' }, n(tick)));
    seasons.forEach((row, i) => {
      const cx = L + band * (i + .5), x0 = cx - bw / 2;
      const r1 = svgNode('rect', { x: x0, y: y(row.injury), width: bw, height: y(0) - y(row.injury), class: 'season-injury' }); r1.append(svgNode('title', {}, `${row.season}: ${n(row.injury)} ${t('lesiones', 'injuries')}`));
      const r2 = svgNode('rect', { x: x0, y: y(row.all), width: bw, height: y(row.injury) - y(row.all), class: 'season-other' }); r2.append(svgNode('title', {}, `${row.season}: ${n(row.other)} ${t('ausencias no lesivas', 'non-injury absences')} (${n(row.covid)} COVID)`));
      chart.append(r1, r2,
        svgNode('text', { x: cx, y: y(row.all) - 8, 'text-anchor': 'middle', class: 'season-total' }, n(row.all)),
        narrow ? svgNode('text', { x: cx, y: H - B + 38, 'text-anchor': 'middle', class: 'season-in below' }, n(row.injury)) : svgNode('text', { x: cx, y: y(row.injury) + 18, 'text-anchor': 'middle', class: 'season-in' }, n(row.injury)),
        svgNode('text', { x: cx, y: H - B + 20, 'text-anchor': 'middle', class: 'axis-tick strong' }, row.season));
    });
    chart.append(svgNode('text', { x: (L + W - R) / 2, y: H - 6, 'text-anchor': 'middle', class: 'axis-label' }, t('Temporada de la fuente · registros originales', 'Source season · original records')));
    const list = document.querySelector('#season-days'); if (list) { list.replaceChildren(); const first = seasons[0].days; for (const row of seasons) { const li = document.createElement('li'); li.append(text('span', row.season, 'mono'), text('strong', n(row.days)), text('span', row === seasons[0] ? t('días de baja por lesión', 'injury days') : `${row.days >= first ? '+' : ''}${pct(row.days / first - 1)} ${t('frente a 20/21', 'vs 20/21')}`)); list.append(li); } }
  }
  function drawRegions() {
    const host = document.querySelector('#region-rows'); if (!host) return; host.replaceChildren();
    const rows = project.views.raw['all|all'].injuries.filter(isInjury), totalN = sum(rows, 'count'), totalD = sum(rows, 'days');
    const groups = REGIONS.map(([key, es, en]) => { const sel = rows.filter(r => regionOf(r.label) === key); return { key, name: t(es, en), count: sum(sel, 'count'), days: sum(sel, 'days'), labels: sel.length }; });
    const rest = rows.filter(r => regionOf(r.label) === 'other'); groups.push({ key: 'other', name: t('Sin región en la etiqueta', 'No region in label'), count: sum(rest, 'count'), days: sum(rest, 'days'), labels: rest.length });
    const max = Math.max(...groups.map(g => Math.max(g.count / totalN, g.days / totalD)));
    for (const g of groups) {
      const row = text('div', '', 'region-row' + (g.key === 'other' ? ' muted' : ''));
      const head = text('div', '', 'region-head'); head.append(text('strong', g.name), text('span', `${n(g.labels)} ${t('etiquetas', 'labels')}`, 'mono'));
      const bars = text('div', '', 'region-bars');
      for (const [cls, share, label] of [['freq', g.count / totalN, t('registros', 'records')], ['days', g.days / totalD, t('días', 'days')]]) {
        const line = text('div', '', 'region-line ' + cls); const track = text('span', '', 'track'); const fill = text('span', '', 'fill'); fill.style.width = `${100 * share / max}%`; track.append(fill);
        line.append(text('span', label, 'region-kind'), track, text('b', pct(share))); bars.append(line);
      }
      row.append(head, bars); host.append(row);
    }
  }
  let resizeTimer; window.addEventListener('resize', () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(() => { if (project && document.querySelector('#burden-chart')) { renderExplorer(); drawHistory(); drawSeasons(); } }, 150); });
  Promise.all([fetch('/data/project.json').then(r=>{if(!r.ok)throw new Error('project data unavailable');return r.json();}),fetch('/data/links.json').then(r=>r.json()),fetch('/data/references.json').then(r=>r.json())]).then(([data,links,refs])=>{
    project=data;referenceData=Array.isArray(refs)?refs:refs.references||[];
    document.querySelectorAll('[data-link]').forEach(el=>{const href=links[el.dataset.link];if(href && /^https:\/\//.test(href))el.href=href;});
    const league=document.querySelector('#league-filter');const season=document.querySelector('#season-filter');
    if(league){for(const value of data.summary.leagues){const option=text('option',value);option.value=value;league.append(option);}for(const value of data.summary.seasons){const option=text('option',value);option.value=value;season.append(option);}for(const id of ['league-filter','season-filter','view-filter','scope-filter'])document.getElementById(id).addEventListener('change',renderExplorer);}
    applyLanguage();
  }).catch(error=>{console.error(error);document.querySelector('#explore .wrap')?.prepend(text('p',t('No se pudieron cargar los datos interactivos. Puedes descargar las tablas CSV más abajo.','Interactive data could not load. You can download the CSV tables below.'),'data-error'));});
})();

// design-pass: on narrow screens the new-analysis sections start collapsed behind an accessible toggle.
(() => {
  const labels = { es: ['Ver el análisis', 'Ocultar el análisis'], en: ['Show the analysis', 'Hide the analysis'] };
  const lang = () => (document.documentElement.lang || 'es').slice(0, 2) === 'en' ? 'en' : 'es';
  const toggles = [];
  document.querySelectorAll('[data-collapse-after]').forEach((marker, index) => {
    const section = marker.closest('section');
    if (!section || section.querySelector('.collapse-body')) return;
    const body = document.createElement('div');
    body.className = 'collapse-body';
    body.id = `${section.id || 'analysis'}-body-${index}`;
    while (marker.nextSibling) body.appendChild(marker.nextSibling);
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'collapse-toggle';
    button.setAttribute('aria-controls', body.id);
    button.setAttribute('aria-expanded', 'false');
    button.innerHTML = '<span class="collapse-label"></span><span class="collapse-icon" aria-hidden="true">+</span>';
    marker.after(button, body);
    section.classList.add('is-collapsible');
    button.addEventListener('click', () => {
      const open = !section.classList.contains('is-open');
      section.classList.toggle('is-open', open);
      button.setAttribute('aria-expanded', String(open));
      paint();
      if (open) window.dispatchEvent(new Event('resize'));
    });
    toggles.push([section, button]);
  });
  function paint() {
    for (const [section, button] of toggles) {
      const open = section.classList.contains('is-open');
      button.querySelector('.collapse-label').textContent = labels[lang()][open ? 1 : 0];
      button.querySelector('.collapse-icon').textContent = open ? '−' : '+';
    }
  }
  paint();
  new MutationObserver(paint).observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
})();
