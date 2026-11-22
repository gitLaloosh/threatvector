// Kill counts by who died on the Intel map's labels (Project doc claude/roadmap/kill-rings-plan.md; the owner 2026-11-20: "maybe instead of
// changing rings, we just represent the death count by standing? amber X [N] [N] [N]", then "Yes, counts by who died", "Friendly, hostile,
// neutral", "Yes, quick mockup"). Rings unchanged. Mockup shortcuts the build must not copy are in README.md.
(() => {
  const K = window.MKK = {mode: 'proposed', pal: 'a'};
  // [stated] 2026-11-20 "the blue and white for friendlies and neuts are too close in color/shade. can we make them contrast a bit more?"
  // (first try: friendly #8db8f2, neutral #b9c3ca, both light). Three pairs to compare; hostile stays #f08b7e (.it-kl.kh)
  const PAL = {a: {f: '#4f8fe0', n: '#b9c3ca'},   // A: the friendly token (--side-friendly, the friendly ring) beside the light neutral ring grey (lightness 59 vs 78)
               b: {f: '#7dbbff', n: '#6b7781'},   // B: a bright blue beside a dim grey (74 vs 49)
               c: {f: '#4f8fe0', n: '#d4dbe0'}};  // C: the friendly token beside a near-white grey (59 vs 87)
  const COL = {f: PAL.a.f, h: '#f08b7e', n: PAL.a.n};
  K.setPal = (k) => { K.pal = k; COL.f = PAL[k].f; COL.n = PAL[k].n; };
  const WORD = {f: ['friendly lost', 'friendlies lost'], h: ['hostile killed', 'hostiles killed'], n: ['neutral killed', 'neutrals killed']};
  const ORDER = ['f', 'h', 'n'];   // Near You's badge order
  // per system: kills by who died (a build: itMapReports, from st.kills' v, which the page already keeps)
  const reps0 = itMapReports;
  itMapReports = function(){
    const out = reps0(), keep = Date.now() - it.set.forget * 60000;
    for(const r of out.values()){ const kb = {f: 0, h: 0, n: 0}; for(const k of (r.st && r.st.kills) || []) if(k.t >= keep) kb[COL[k.v] ? k.v : 'n']++; r.kb = kb; }
    return out;
  };
  window.__MKkt = (r, C) => {
    const big = '700 11px system-ui, sans-serif';
    if(K.mode === 'today' || !r.kb) return [{t: '✕' + r.kills, col: C.amber, font: big}];
    return [{t: '✕', col: C.amber, font: big}, ...ORDER.filter(v => r.kb[v]).map(v => ({t: String(r.kb[v]), col: COL[v], font: big}))];
  };
  window.__MKkh = (r) => {
    const tot = `✕ ${r.kills} kill${r.kills === 1 ? '' : 's'} here`;
    if(K.mode === 'today' || !r.kb) return `<br><span class="d">${tot}</span>`;
    return `<br><span class="d">${tot}:</span> ` + ORDER.filter(v => r.kb[v]).map(v => `<span style="color:${COL[v]}">${r.kb[v]} ${WORD[v][r.kb[v] === 1 ? 0 : 1]}</span>`).join('<span class="d">, </span>');
  };
  window.__MKkl = () => K.mode === 'today' ? '<span>✕ kills</span>'
    : `<span title="Kills here within &quot;forget reports after&quot;, by who died: friendlies lost, hostiles killed, neutrals killed">✕ kills by who died: <b style="color:${COL.f}">friendly</b> <b style="color:${COL.h}">hostile</b> <b style="color:${COL.n}">neutral</b></span>`;

  // made-up kills, through the page's own Near You path (itNearAdd), so Near You's badges and the map agree
  let pid = 95001000, kid = 900000;
  const pilot = (side) => { const id = ++pid; return {id, name: `Mk Pilot ${id - 95001000}`, corp: 98100000 + (side === 'f' ? 1 : side === 'h' ? 2 : 9), alliance: null, side, ship: null}; };
  const kill = (sys, killers, victimSide, minsAgo) => {
    const att = killers.map(pilot), victim = pilot(victimSide);
    const e = {id: ++itEntryId, kind: 'kill', t: Date.now() - minsAgo * 60000, who: 'zKillboard', chan: '', raw: '', history: true, pilots: att, pairs: new Map(),
      p: {sys: [{id: sys, at: 0, k: 1}], ships: [], kw: new Set(), extra: 0, W: [], used: []},
      kill: {id: ++kid, victim, value: 1e6 * (5 + (kid % 40)), solo: att.length === 1, n: att.length, ships: 0, players: att.length}};
    e.friendlyOnly = att.every(a => a.side === 'f'); e.sighting = e.friendlyOnly && victimSide !== 'f';
    it.feed.unshift(e); itNearAdd(e, sys);
  };
  K.seed = () => {
    const id = (nm) => it.names.byLower.get(nm.toLowerCase());
    const many = (sys, spec) => { let m = 1; for(const [n, killers, v] of spec) for(let k = 0; k < n; k++) kill(id(sys), killers, v, m++); };
    // the owner's example: 2 neutrals, 5 hostiles and 3 friendlies killed
    many('78-0R6', [[3, ['h', 'h', 'h'], 'f'], [5, ['f', 'f'], 'h'], [2, ['h', 'h'], 'n']]);
    many('MSG-BZ', [[2, ['h'], 'f']]);
    many('SHBF-V', [[1, ['f', 'f', 'f'], 'h'], [1, ['h'], 'n']]);
    // a busy area: many systems close together, some with all three
    many('RERZ-L', [[4, ['n', 'n'], 'n']]);
    many('0UBC-R', [[1, ['h'], 'f'], [1, ['f'], 'h']]);
    many('EUU-4N', [[12, ['f', 'f', 'f', 'f'], 'h'], [1, ['h', 'h'], 'f']]);
    many('8G-2FP', [[2, ['h', 'h'], 'f'], [3, ['f'], 'h'], [1, ['h'], 'n']]);
    many('L5-UWT', [[1, ['n'], 'h']]);
    many('4M-QXK', [[6, ['h', 'h', 'h'], 'f'], [2, ['f', 'f'], 'h'], [14, ['h', 'h'], 'n']]);
    many('I-1QKL', [[1, ['f'], 'n']]);
    many('YPW-M4', [[2, ['h'], 'h']]);
    many('8-WYQZ', [[1, ['h', 'h'], 'f'], [1, ['f'], 'h'], [1, ['n'], 'n']]);
    itRender(); itMapRefresh();
  };
  K.zoomTo = (gpx) => { const i = itm.home; itMapZoom(itm.Q[2 * i], itm.Q[2 * i + 1], gpx / itMapGatePx()); itMapCenter(false); itMapDraw(); };
  K.redraw = () => { itm.key = null; itMapLegend(); itMapDraw(); };
  K.boot = () => {
    const d = document.createElement('div'); d.id = 'mkKc';
    const B = (a, t) => `<button type="button" ${a}>${t}</button>`;
    d.innerHTML = `<b>MOCKUP</b> <span class="mk-fold"><span>Kill label: ${B('data-mk-m="today"', 'Today')}${B('data-mk-m="proposed"', 'By who died')}</span>`
      + `<span>Friendly / neutral: ${B('data-mk-p="a"', 'A')}${B('data-mk-p="b"', 'B')}${B('data-mk-p="c"', 'C')}</span>`
      + `<span>Zoom: ${B('data-mk-z="12"', 'Out')}${B('data-mk-z="30"', 'Middle')}${B('data-mk-z="90"', 'In')}</span></span>` + B('data-mk-fold', '▾');
    document.body.appendChild(d);
    const st = document.createElement('style');
    st.textContent = `#mkKc{position:fixed; right:8px; top:8px; z-index:99; background:#2a1d3a; border:1px solid #a98bd8; border-radius:6px; padding:6px 8px; font:12px system-ui; color:#eee; display:flex; flex-wrap:wrap; gap:4px 8px; align-items:center; max-width:min(460px, calc(100vw - 32px));}
      #mkKc button{font:12px system-ui; padding:2px 6px; border:1px solid #6d5a8a; border-radius:4px; background:#3a2a50; color:#eee; cursor:pointer; min-height:0;} #mkKc button[aria-pressed="true"]{background:#a98bd8; color:#1a1024;}
      #mkKc .mk-fold{display:contents;} #mkKc.folded .mk-fold{display:none;}
      @media (max-width: 599px){ #mkKc{top:auto; bottom:8px; left:8px; right:auto;} }`;
    document.head.appendChild(st);
    if(matchMedia('(max-width: 599px)').matches) d.classList.add('folded');
    const paint = () => { for(const b of d.querySelectorAll('[data-mk-m]')) b.setAttribute('aria-pressed', String(b.dataset.mkM === K.mode));
      for(const b of d.querySelectorAll('[data-mk-p]')) b.setAttribute('aria-pressed', String(b.dataset.mkP === K.pal)); };
    d.addEventListener('click', (e) => { const b = e.target.closest('button'); if(!b) return;
      if(b.dataset.mkM){ K.mode = b.dataset.mkM; K.redraw(); }
      if(b.dataset.mkP){ K.setPal(b.dataset.mkP); K.redraw(); }
      if(b.dataset.mkZ) K.zoomTo(Number(b.dataset.mkZ));
      if(b.dataset.mkFold !== undefined) d.classList.toggle('folded');
      paint(); });
    paint();
  };
})();
