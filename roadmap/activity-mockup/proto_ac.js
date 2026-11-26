// Activity (past hour) (Project doc claude/roadmap/activity-filter-plan.md). The owner 2026-11-20: [stated] "One filter, kind + minimum
// (Recommended)"; 2026-11-21: "Per kind, those defaults (Recommended)", "Round numbers 1–2000 (Recommended)", "No, use 065's colours
// (Recommended)", "Mockup yes, raise cap (Recommended)". Every count here is made up (no ESI read). Shortcuts the build must not copy: README.md.
(() => {
  const A = window.MKA = {};
  const MIN = 60000, now0 = Math.floor(Date.now() / MIN) * MIN;
  const STEPS = [1, 2, 3, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200, 300, 500, 750, 1000, 1500, 2000];
  const DEF = {k: 'j', j: 50, sp: 1, npc: 200};
  const KINDS = {j: ['Jumps', 'jumps'], sp: ['Ship + pod kills', 'ship + pod kills'], npc: ['NPC kills', 'NPC kills']};
  const at = (t) => new Date(t).toISOString().slice(11, 16);
  // made-up hourly counts shaped like ESI's of 2026-11-21 (jumps median 16, 90th 124; ship + pod in ~10% of systems, median 2; NPC in ~half)
  const h01 = (x) => { x = Math.imul(x ^ (x >>> 16), 0x45d9f3b); x = Math.imul(x ^ (x >>> 16), 0x45d9f3b); return ((x ^ (x >>> 16)) >>> 0) / 4294967296; };
  A.build = () => {
    const ids = itGraphGet().ids; A.j = new Map(); A.sp = new Map(); A.npc = new Map();
    for(let i = 0; i < ids.length; i++){
      const id = ids[i]; if(id >= 31000000) continue;   // no J-space data (as ESI)
      const u = Math.min(0.997, h01(id)), v = h01(id + 7), w = h01(id + 13);
      const j = Math.round(16 * u / (1 - u)); if(j > 0) A.j.set(i, j);
      if(v > 0.9) A.sp.set(i, Math.max(1, Math.round(2 * Math.pow((v - 0.9) / (1 - v + 0.001) * 0.5, 1.1))));
      if(itMapSecT(i) < 5 && w > 0.45) A.npc.set(i, Math.max(1, Math.round(80 * (w - 0.45) / (1.0005 - w) * 1.2)));
    }
    // a few around C-J6MT so the default view has matches near you
    for(const [nm, jv, sp, npc] of [['78-0R6', 140, 6, 30], ['SHBF-V', 62, 2, 310], ['MSG-BZ', 18, 0, 520], ['0UBC-R', 95, 1, 0], ['EUU-4N', 220, 0, 40]]){
      const i = ids.findIndex(x => itSysName(x) === nm); if(i < 0) continue;
      A.j.set(i, jv); if(sp) A.sp.set(i, sp); else A.sp.delete(i); if(npc) A.npc.set(i, npc); else A.npc.delete(i);
    }
    A.at = now0 - 50 * MIN; A.data = true;
  };
  // the stack's new fields (safe both ways)
  const blank0 = itMapStackBlank, read0 = itMapStackRead, key0 = itMapStKey;
  itMapStackBlank = function(){ const o = blank0(); o.act = {...DEF}; o.seen.act = false; return o; };
  itMapStackRead = function(){
    const o = read0(); let s = null; try{ s = JSON.parse(localStorage.getItem(MAP_STACK_KEY)); }catch(e){ s = null; }
    const b = s && s.act, ok = (v) => STEPS.includes(v);
    if(b && typeof b === 'object'){ if(KINDS[b.k]) o.act.k = b.k; for(const k of ['j', 'sp', 'npc']) if(ok(b[k])) o.act[k] = b[k]; }
    if(s && s.seen && s.seen.act === true) o.seen.act = true;
    return o;
  };
  itMapStKey = function(){ return key0() + JSON.stringify([itMapSt().act, A.data ? A.at : 0]); };   // data there or not is in the key (068's lesson)
  // two inert stand-ins so the column holds the Only filters it will: 065's Region pick and 068's Sov hubs (not part of this item)
  const ico = (d) => `<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${d}</svg>`;
  IT_MAP_ONLY.push('mkreg', 'mkhub', 'act');
  IT_MAP_FILTERS.push({k: 'mkreg', g: 'only', name: 'Region pick (065, stand-in)', note: 'stand-in: not part of this mockup', icon: ico('<path d="M3 4.5l4-1.5 4 1.5 4-1.5v10.5l-4 1.5-4-1.5-4 1.5z"/><path d="M7 3v10.5M11 4.5V15"/>')},
    {k: 'mkhub', g: 'only', name: 'Sov hubs (068, stand-in)', note: 'stand-in: not part of this mockup', icon: ico('<path d="M5 15.5V2.5"/><path d="M5 3h8.5l-2 3 2 3H5"/><path d="M2.5 15.5h5"/>')},
    {k: 'act', g: 'only', name: 'Activity (past hour)', note: 'only: systems with at least N jumps, ship + pod kills or NPC kills in the past hour (ESI)', icon: ico('<path d="M2 10h3l2-5 3 9 2-6 1.5 2H16"/>')});
  IT_MAP_PANEL_BTN.act = () => `<button type="button" class="it-map-pb" data-it-mpn="act" aria-haspopup="dialog" aria-expanded="false" aria-label="Activity: which and how many" title="Activity: which and how many">${IT_MAP_SET_ICON}</button>`;
  // the match
  const cnt = (i, k) => (k === 'j' ? A.j : k === 'sp' ? A.sp : A.npc).get(i) || 0;   // missing = 0 (065's UNVERIFIED row)
  window.__MKact = (i) => { if(!A.data) return false; const s = itMapSt().act; return cnt(i, s.k) >= s[s.k]; };
  A.count = () => { const s = itMapSt().act, M = s.k === 'j' ? A.j : s.k === 'sp' ? A.sp : A.npc; let n = 0; for(const v of M.values()) if(v >= s[s.k]) n++; return n; };
  // the hover: the picked kind's count (065's Colour line says it when that Colour is on; never twice)
  window.__MKtip = (i) => {
    const st = itMapSt(); if(!itMapOnlyOn() || !st.only.act || !A.data) return '';
    if(st.colour === (st.act.k === 'j' ? 'mkjph' : 'mkkph')) return '';   // 065's Jumps / Kills (past hour) colours (not in this page yet)
    if(itGraphGet().ids[i] >= 31000000) return '<br><span class="d">no hourly counts in J-space (ESI)</span>';
    const n = cnt(i, st.act.k);
    return `<br><span class="d">${n.toLocaleString('en-US')} ${KINDS[st.act.k][1]} in the past hour (ESI, as of ${at(A.at)})</span>`;
  };
  // the Only line
  const only0 = itMapOnlyHtml;
  itMapOnlyHtml = function(){
    const s = itMapSt(); let h = only0(); if(!s.only.act) return h;
    h = h.replace(/ · $/, '');
    const p = A.data ? `at least ${s.act[s.act.k].toLocaleString('en-US')} ${KINDS[s.act.k][1]} in the past hour (${A.count().toLocaleString('en-US')}) · ESI ${at(A.at)}` : 'activity: no data yet';
    return h + ' · ' + escapeHtml(p);
  };
  // the stepper: round numbers, one minimum per kind
  RS.mapAct = {label: 'At least', unit: '', title: () => 'Activity: at least this many in the past hour (ESI’s hourly counts)', steps: () => STEPS, value: () => { const s = itMapSt().act; return s[s.k]; },
    set: (v) => { const s = itMapSt().act; s[s.k] = v; }, why: (end) => end === 'lo' ? 'At least 1' : 'At most 2,000', aria: 'count', after: () => itMpChanged()};
  // the settings panel
  const body0 = itMpBodyHtml;
  itMpBodyHtml = function(k){
    if(k !== 'act') return body0(k);
    const s = itMapSt().act, rad = (v) => `<label class="it-sov-k"><input type="radio" name="mkAct" value="${v}"${s.k === v ? ' checked' : ''}> <span>${KINDS[v][0]}</span></label>`;
    return `<div class="mk-ak">${rad('j')}${rad('sp')}${rad('npc')}</div><div class="it-mp-row">${rsHtml('mapAct')}</div>`
      + '<div class="it-mp-note">In the past hour, from ESI’s hourly counts (no J-space). Each kind keeps its own number. To see the counts, pick Jumps or Kills (past hour) as the Colour.</div><div class="it-mp-cnt" role="status"></div>';
  };
  const make0 = itMpMake;
  itMpMake = function(){ make0(); itMp.el.addEventListener('change', (e) => { if(e.target.name !== 'mkAct') return; itMapSt().act.k = e.target.value; itMp.built = ''; itMpChanged(); const r = itMp.el.querySelector('[name=mkAct]:checked'); if(r) r.focus({preventScroll: true}); }); };
  const set0 = itMapFilterSet;
  itMapFilterSet = function(k){ const s = itMapSt(), first = k === 'act' && !s.only.act && !s.seen.act; set0(k); if(first && itm.box && itm.box.isConnected){ s.seen.act = true; itMapStackSave(); itMpOpen('act'); } };
  const css = document.createElement('style');
  css.textContent = '.it-mpp .mk-ak{display:flex; flex-wrap:wrap; gap:2px 12px; margin:0 0 6px;} .it-mpp .mk-ak .it-sov-k{flex:0 0 auto;}';
  document.head.appendChild(css);
  // scenes for the MOCKUP box
  A.zoomTo = (gpx) => { const i = itm.home; itMapZoom(itm.Q[2 * i], itm.Q[2 * i + 1], gpx / itMapGatePx()); itMapCenter(false); itMapDraw(); };
  A.scene = (k) => {
    itMpOpen('', false);
    const s = itMapSt(); for(const o of IT_MAP_ONLY) s.only[o] = false; s.colour = 'sec'; s.act = {...DEF};
    A.data = k !== 'nodata'; if(A.data && !A.j) A.build();
    if(k !== 'off') s.only.act = true;
    if(k === 'sp') s.act.k = 'sp';
    if(k === 'npc') s.act.k = 'npc';
    if(k === 'busy') s.act.j = 500;
    s.seen.act = true; itMapStackSave(); itm.mtStep = -1; itMapFbarPaint(true); itMapLegend(); itMpPaint(); itMapDraw();
    A.zoomTo(k === 'wide' ? 6 : 14);
    itMp.built = ''; if(k !== 'off' && k !== 'wide') itMpOpen('act', false);
  };
  A.boot = () => {
    A.build();
    const d = document.createElement('div'); d.id = 'mkAc';
    const B = (a, t) => `<button type="button" ${a}>${t}</button>`;
    d.innerHTML = `<b>MOCKUP</b> <span class="mk-fold">${B('data-mk-sc="jumps"', 'Jumps ≥ 50')}${B('data-mk-sc="busy"', 'Jumps ≥ 500')}${B('data-mk-sc="sp"', 'Ship + pod ≥ 1')}${B('data-mk-sc="npc"', 'NPC ≥ 200')}${B('data-mk-sc="wide"', 'Zoomed out')}${B('data-mk-sc="nodata"', 'No data yet')}${B('data-mk-sc="off"', 'Off')}</span>` + B('data-mk-fold', '▾');
    document.body.appendChild(d);
    const st = document.createElement('style');
    st.textContent = `#mkAc{position:fixed; right:8px; top:8px; z-index:99; background:#2a1d3a; border:1px solid #a98bd8; border-radius:6px; padding:6px 8px; font:12px system-ui; color:#eee; display:flex; flex-wrap:wrap; gap:4px 8px; align-items:center; max-width:min(520px, calc(100vw - 32px));}
      #mkAc button{font:12px system-ui; padding:2px 6px; border:1px solid #6d5a8a; border-radius:4px; background:#3a2a50; color:#eee; cursor:pointer; min-height:0;}
      #mkAc .mk-fold{display:contents;} #mkAc.folded .mk-fold{display:none;}
      @media (max-width: 599px){ #mkAc{top:auto; bottom:8px; left:8px; right:auto;} }`;
    document.head.appendChild(st);
    if(matchMedia('(max-width: 599px)').matches) d.classList.add('folded');
    d.addEventListener('click', (e) => { const b = e.target.closest('button'); if(!b) return; if(b.dataset.mkSc) A.scene(b.dataset.mkSc); if(b.dataset.mkFold !== undefined) d.classList.toggle('folded'); });
  };
})();
