// Sov hubs (Project doc claude/roadmap/sov-hubs-plan.md). The owner 2026-11-21: [stated] "One filter, two kinds (Recommended)", "24 h fights,
// now for hubs (Recommended)", "Fight tags only, filter on (Recommended)", "Every 2 min, raise cap (Recommended)". Every fight, window and
// alliance here is made up (no ESI read). Shortcuts the build must not copy: README.md.
(() => {
  const H = window.MKH = {};
  const MIN = 60000, HOUR = 3600000, now0 = Math.floor(Date.now() / MIN) * MIN;
  const AL = {99100001: ['Mockup Coalition', 'MKCO'], 99100002: ['Mockup Raiders', 'MKRD'], 99100003: ['Mockup Holdings', 'MKHD']};
  // made-up campaigns (ESI's /sovereignty/campaigns fields), start relative to now; RERZ-L past the default 24 h
  const CAMP = [[30000773, 70, 99100002, 0.6], [30000779, -25, 99100001, 0.45], [30000774, 365, 99100003, 0.6], [30000781, 1300, 99100002, 0.6],
    [30000780, 1800, 99100003, 0.6], [30000796, 200, 99100001, 0.6]];
  const at = (h) => new Date(h).toISOString().slice(11, 16);
  const dur = (ms) => { const m = Math.max(0, Math.round(ms / MIN)), h = Math.floor(m / 60); return h ? `${h} h ${String(m % 60).padStart(2, '0')} min` : `${m} min`; };
  H.build = () => {
    const ids = itGraphGet().ids, ix = new Map(ids.map((v, i) => [v, i]));
    H.fight = new Map();   // system index → campaign
    for(const [id, m, def, ds] of CAMP){ const i = ix.get(id); if(i === undefined) continue; H.fight.set(i, {kind: 'ihub_defense', start: now0 + m * MIN, def, ds, as: Math.round((1 - ds) * 100) / 100}); }
    // made-up hub windows: every nullsec system "held", a window of 3 or 4 h starting at an hour from its ID; none while in a fight (as ESI)
    H.win = new Map();
    const day = Math.floor(now0 / (24 * HOUR)) * 24 * HOUR;
    for(let i = 0; i < ids.length; i++){
      if(itMapSecT(i) > 0 || H.fight.has(i)) continue;
      const h0 = (ids[i] * 7) % 24, len = 3 + (ids[i] % 2);
      let s = day + h0 * HOUR; if(s + len * HOUR <= now0) s += 24 * HOUR;   // the next window that hasn't ended
      H.win.set(i, {s, e: s + len * HOUR, al: [99100001, 99100002, 99100003][ids[i] % 3]});
    }
    H.at = now0; H.data = true;
  };
  // the stack's new fields (safe both ways, as 058's)
  const blank0 = itMapStackBlank, read0 = itMapStackRead, key0 = itMapStKey;
  itMapStackBlank = function(){ const o = blank0(); o.hub = {fight: true, fightH: 24, vuln: true, vulnH: 0}; o.seen.hub = false; return o; };
  itMapStackRead = function(){
    const o = read0(); let s = null; try{ s = JSON.parse(localStorage.getItem(MAP_STACK_KEY)); }catch(e){ s = null; }
    const b = s && s.hub, int = (v, a, z, d) => Number.isInteger(v) && v >= a && v <= z ? v : d;
    if(b && typeof b === 'object'){ o.hub.fight = b.fight !== false; o.hub.vuln = b.vuln !== false; o.hub.fightH = int(b.fightH, 0, 48, 24); o.hub.vulnH = int(b.vulnH, 0, 24, 0); }
    if(s && s.seen && s.seen.hub === true) o.seen.hub = true;
    return o;
  };
  itMapStKey = function(){ return key0() + JSON.stringify([itMapSt().hub, H.data ? H.at : 0]); };   // a new read (or the clock at a read) works the match out again
  // the filter: after Sov upgrades
  IT_MAP_ONLY.push('hub');
  const icon = '<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M5 15.5V2.5"/><path d="M5 3h8.5l-2 3 2 3H5"/><path d="M2.5 15.5h5"/></svg>';
  IT_MAP_FILTERS.splice(IT_MAP_FILTERS.findIndex(f => f.k === 'sov') + 1, 0, {k: 'hub', g: 'only', name: 'Sov hubs', note: 'only: systems whose sov hub has a fight coming up, or is vulnerable', icon});
  IT_MAP_PANEL_BTN.hub = () => `<button type="button" class="it-map-pb" data-it-mpn="hub" aria-haspopup="dialog" aria-expanded="false" aria-label="Sov hubs: which and when" title="Sov hubs: which and when">${IT_MAP_SET_ICON}</button>`;
  // the match: any ticked kind counts
  const fightIn = (i, s) => { const f = H.fight.get(i); return !!f && f.start - H.at <= s.fightH * HOUR; };   // started ones always count
  const vulnIn = (i, s) => { const w = H.win.get(i); return !!w && w.s - H.at <= s.vulnH * HOUR && w.e > H.at; };
  window.__MKhub = (i) => { if(!H.data) return false; const s = itMapSt().hub; return (s.fight && fightIn(i, s)) || (s.vuln && vulnIn(i, s)); };
  H.counts = () => { let f = 0, v = 0; const s = itMapSt().hub; for(const i of H.fight.keys()) if(fightIn(i, s)) f++; for(const i of H.win.keys()) if(vulnIn(i, s)) v++; return {f, v}; };
  // the hover
  const alTxt = (id) => { const a = AL[id]; return a ? `${a[0]} [${a[1]}]` : 'an alliance'; };
  const KIND = {ihub_defense: 'hub defense', tcu_defense: 'TCU defense', station_defense: 'station defense', station_freeport: 'station freeport'};
  window.__MKtip = (i) => {
    const st = itMapSt(); if(!itMapOnlyOn() || !st.only.hub || !H.data) return '';
    const now = Date.now(), f = H.fight.get(i), w = H.win.get(i); let h = '';
    if(f) h += `<br><span class="d">Sov fight: ${KIND[f.kind]}, ${f.start <= now ? `under way since ${at(f.start)} EVE (${dur(now - f.start)})` : `starts ${at(f.start)} EVE (in ${dur(f.start - now)})`}; defending ${escapeHtml(alTxt(f.def))}, score ${Math.round(f.ds * 100)} / ${Math.round(f.as * 100)}; nodes anywhere in this constellation</span>`
      + '<br><span class="d">Hub: no vulnerability window (in a fight)</span>';
    else if(w) h += `<br><span class="d">Hub vulnerable ${at(w.s)}–${at(w.e)} EVE (${w.s <= now ? `now, ${dur(w.e - now)} left` : `opens in ${dur(w.s - now)}`})</span>`;
    return h;
  };
  // the tags beside fights coming up ("SOV 19:45": the plan's ⚔ isn't in every font, and on a canvas without it it falls back to an ✕ like the kill count's) (the kind ticked and within its hours)
  window.__MKftag = (i, TAG) => {   // the tag for system i, or none
    const st = itMapSt(), f = H.fight && H.fight.get(i);
    if(!f || !itMapOnlyOn() || !st.only.hub || !st.hub.fight || !H.data || !fightIn(i, st.hub)) return [];
    return [{t: `SOV ${f.start <= Date.now() ? 'now' : at(f.start)}`, bg: 'rgba(12,16,20,.85)', col: '#d7dee3', font: TAG}];
  };
  window.__MKlab = (put, nm, F, TAG, focus) => {   // fights with no report: named with their tag, where there's room
    for(const i of [...(H.fight || new Map()).keys()].sort((a, b) => H.fight.get(a).start - H.fight.get(b).start)){
      if(i === itm.home || itm.rep.has(i)) continue;
      const tag = window.__MKftag(i, TAG); if(tag.length) put(i, [{t: nm(i), col: '#d7dee3', font: F}, ...tag], false);
    }
  };
  // the Only line
  const only0 = itMapOnlyHtml;
  itMapOnlyHtml = function(){
    const s = itMapSt(); let h = only0(); if(!s.only.hub) return h;
    h = h.replace(/ · $/, '');   // no other Only filter on: the base line ends in its separator
    const p = [];
    if(!H.data) p.push('sov hubs: no data yet');
    else { const c = H.counts();
      if(s.hub.fight) p.push(`a sov fight within ${s.hub.fightH} h (${c.f})`);
      if(s.hub.vuln) p.push(`a hub vulnerable ${s.hub.vulnH ? `within ${s.hub.vulnH} h` : 'now'} (${c.v})`);
      if(!p.length) p.push('sov hubs: no kind ticked'); }
    return h + ` · ${escapeHtml(p.join(' or '))}${H.data ? ` · ESI ${at(H.at)}` : ''}`;
  };
  // the steppers
  RS.mapHubF = {label: 'within', unit: 'h', title: () => 'Sov fight: starting within N hours (started fights always count)', steps: () => itRangeList(0, 48), value: () => itMapSt().hub.fightH,
    set: (v) => { itMapSt().hub.fightH = v; }, why: (end) => end === 'lo' ? 'Started fights only' : 'At most 48 hours', aria: 'hours', after: () => itMpChanged()};
  RS.mapHubV = {label: 'opens', unit: 'h', title: () => 'Vulnerable: now, or opening within N hours', steps: () => itRangeList(0, 24), value: () => itMapSt().hub.vulnH,
    set: (v) => { itMapSt().hub.vulnH = v; }, why: (end) => end === 'lo' ? 'Vulnerable now' : 'At most 24 hours', aria: 'hours', show: (v) => v ? String(v) : 'now', read: (t) => /now/i.test(t) ? 0 : Math.round(parseFloat(t)), after: () => itMpChanged()};
  // the settings panel
  const body0 = itMpBodyHtml;
  itMpBodyHtml = function(k){
    if(k !== 'hub') return body0(k);
    const s = itMapSt().hub, box = (v, on, t) => `<label class="it-sov-k"><input type="checkbox" data-mk-hk="${v}"${on ? ' checked' : ''}> <span>${t}</span></label>`;
    return `<div class="mk-hk">${box('fight', s.fight, 'Fight coming up')}<div class="it-mp-row">${rsHtml('mapHubF')}</div></div>`
      + `<div class="mk-hk">${box('vuln', s.vuln, 'Vulnerable')}<div class="it-mp-row">${rsHtml('mapHubV')}</div></div>`
      + '<div class="it-mp-note">Any ticked kind counts. EVE time; from ESI every 2 min while on.</div><div class="it-mp-cnt" role="status"></div>';
  };
  const make0 = itMpMake;
  itMpMake = function(){ make0(); itMp.el.addEventListener('change', (e) => { const b = e.target.closest('[data-mk-hk]'); if(!b) return; itMapSt().hub[b.dataset.mkHk] = b.checked; itMpChanged(); }); };
  // the first time it's switched on, its settings open (as Security range's and Within N jumps')
  const set0 = itMapFilterSet;
  itMapFilterSet = function(k){ const s = itMapSt(), first = k === 'hub' && !s.only.hub && !s.seen.hub; set0(k); if(first && itm.box && itm.box.isConnected){ s.seen.hub = true; itMapStackSave(); itMpOpen('hub'); } };
  const css = document.createElement('style');
  css.textContent = '.it-mpp .mk-hk{display:flex; flex-wrap:wrap; align-items:center; gap:2px 10px; margin:0 0 6px;} .it-mpp .mk-hk .it-sov-k{flex:0 0 auto; margin:0;} .it-mpp .mk-hk .it-mp-row{margin:0;}';
  document.head.appendChild(css);
  // scenes for the MOCKUP box
  H.zoomTo = (gpx) => { const i = itm.home; itMapZoom(itm.Q[2 * i], itm.Q[2 * i + 1], gpx / itMapGatePx()); itMapCenter(false); itMapDraw(); };
  H.scene = (k) => {
    itMpOpen('', false);
    const s = itMapSt(); for(const o of IT_MAP_ONLY) s.only[o] = false; s.colour = 'sec';
    s.hub = {fight: true, fightH: 24, vuln: true, vulnH: 0};
    H.data = k !== 'nodata'; if(H.data && !H.fight) H.build();
    if(k !== 'off') s.only.hub = true;
    if(k === 'fights') s.hub.vuln = false;
    if(k === 'vuln') s.hub.fight = false;
    if(k === 'f48'){ s.hub.vuln = false; s.hub.fightH = 48; }
    if(k === 'v4'){ s.hub.fight = false; s.hub.vulnH = 4; }
    s.seen.hub = true; itMapStackSave(); itm.mtStep = -1; itMapFbarPaint(true); itMapLegend(); itMpPaint(); itMapDraw();
    H.zoomTo(k === 'wide' ? 6 : 26);
    itMp.built = ''; if(k !== 'off' && k !== 'wide') itMpOpen('hub', false);
  };
  H.boot = () => {
    H.build();
    const d = document.createElement('div'); d.id = 'mkHb';
    const B = (a, t) => `<button type="button" ${a}>${t}</button>`;
    d.innerHTML = `<b>MOCKUP</b> <span class="mk-fold">${B('data-mk-sc="both"', 'Defaults')}${B('data-mk-sc="fights"', 'Fights only')}${B('data-mk-sc="f48"', 'Fights 48 h')}${B('data-mk-sc="vuln"', 'Vulnerable now')}${B('data-mk-sc="v4"', 'Vulnerable 4 h')}${B('data-mk-sc="wide"', 'Zoomed out')}${B('data-mk-sc="nodata"', 'No data yet')}${B('data-mk-sc="off"', 'Off')}</span>` + B('data-mk-fold', '▾');
    document.body.appendChild(d);
    const st = document.createElement('style');
    st.textContent = `#mkHb{position:fixed; right:8px; top:8px; z-index:99; background:#2a1d3a; border:1px solid #a98bd8; border-radius:6px; padding:6px 8px; font:12px system-ui; color:#eee; display:flex; flex-wrap:wrap; gap:4px 8px; align-items:center; max-width:min(520px, calc(100vw - 32px));}
      #mkHb button{font:12px system-ui; padding:2px 6px; border:1px solid #6d5a8a; border-radius:4px; background:#3a2a50; color:#eee; cursor:pointer; min-height:0;}
      #mkHb .mk-fold{display:contents;} #mkHb.folded .mk-fold{display:none;}
      @media (max-width: 599px){ #mkHb{top:auto; bottom:8px; left:8px; right:auto;} }`;
    document.head.appendChild(st);
    if(matchMedia('(max-width: 599px)').matches) d.classList.add('folded');
    d.addEventListener('click', (e) => { const b = e.target.closest('button'); if(!b) return; if(b.dataset.mkSc) H.scene(b.dataset.mkSc); if(b.dataset.mkFold !== undefined) d.classList.toggle('folded'); });
  };
})();
