// Ansiblex zones mockup prototype (Project doc claude/roadmap/ansiblex-zones-plan.md). Loaded after the real page (main 51207b6).
// It stands in for 041 (the Jump bridges box and list, which main doesn't have yet) and adds this item: each bridge's zone each way,
// measured from the capital of the alliance that holds it (ESI /sovereignty/systems, made up here), Threat Vector's route using only
// the directions whose arrival zone is ticked in Routes, zones on the list rows, the map's bridge hover and the route's bridge steps.
// Mockup shortcuts the build must not copy: function wraps by name, two hooks in itMapDraw (build_az.py), T.adj swapped during itRpUpdate.
(() => {
  const COL = '#00f000', ZMUL = [0, 0, 2, 6, 9, 15], ZLY = ['', '0–5 LY', '5.1–10 LY', '10.1–15 LY', '15.1–20 LY', '20.1 LY and on'];
  const SOV_URL = 'https://esi.evetech.net/sovereignty/systems?compatibility_date=2026-05-19';
  const AZ = window.AZ = {login: true, capLost: false, sov: null, sovErr: '', zones: [1], text: '', on: true, hover: -1, memo: null, key: ''};
  // ---- made-up sovereignty (the mockup's ESI answer): Mockup Coalition holds the area with its capital in 8G-2FP; Mockup Raiders hold four
  const COAL = 99100001, RAID = 99100002;
  const RAIDERS = [30000779, 30000781, 30000780, 30000458];   // SHBF-V (their capital), 0UBC-R, RERZ-L, 9N-0HF
  function sovAnswer(){
    const ids = Object.keys(window.__MK.names).map(Number);
    return {solar_systems: ids.map(id => {
      const raid = RAIDERS.includes(id), a = raid ? RAID : COAL;
      const cap = !AZ.capLost && (raid ? id === 30000779 : id === 30000771);
      return {solar_system_id: id, claim: {alliance: {alliance_id: a, corporation_id: raid ? 98100002 : 98100001, claimed_since: '2026-01-01T00:00:00Z',
        is_capital_system: cap || (raid && id === 30000779), sovereignty_hub: {id: 1000000000000 + id}, development: {activity_defense_multiplier: 1, military_level: 0, industrial_level: 0, strategic_level: 0}}}};
    })};
  }
  const fetch0 = window.fetch;
  window.fetch = async (input, init) => {
    const url = typeof input === 'string' ? input : input.url;
    if(url.startsWith('https://esi.evetech.net/sovereignty/systems')) return new Response(JSON.stringify(sovAnswer()), {status: 200, headers: {'content-type': 'application/json'}});
    return fetch0(input, init);
  };
  // ---- the read (plan change 3): one simple GET, the answer kept in memory; again at most every 5 minutes (ESI's cache), on demand here
  async function azSovRead(){
    try{
      const r = await fetch(SOV_URL); if(!r.ok) throw new Error('status ' + r.status);
      const o = await r.json(), sys = new Map(), caps = new Map();
      for(const s of o.solar_systems || []){ const a = s.claim && s.claim.alliance; if(!a) continue; sys.set(s.solar_system_id, a.alliance_id); if(a.is_capital_system) caps.set(a.alliance_id, s.solar_system_id); }
      AZ.sov = {sys, caps, at: Date.now()}; AZ.sovErr = '';
      for(const a of new Set(sys.values())) getOrg('alliance', a).then(() => azChanged()).catch(() => {});
    }catch(e){ AZ.sovErr = String(e.message || e); }
    azChanged();
  }
  AZ.read = azSovRead;
  const orgName = (a) => { const o = orgCache.get(`alliance:${a}`); return o && o.name ? o.name : `alliance ${a}`; };
  // zone of an arrival d LY from the capital, on the number the page shows (rounded up to 0.01: the owner's "At 5.00 LY")
  function azZone(d){ const r = Math.ceil(d * 100 - 1e-9) / 100; return r <= 5 ? 1 : r <= 10 ? 2 : r <= 15 ? 3 : r <= 20 ? 4 : 5; }
  function yours(){ return AZ.login ? COAL : null; }   // the build: sideEveGroups().alliance while logged in as Your pilot (the owner: "login, then sov")
  // ---- the list (stand-in for 041's itBridges: "A » B" style lines, the two names around the separator) and each bridge's zones
  function azBridges(){
    const g = itGraphGet(), N = it.names, key = [AZ.text, N ? N.list.length : 0, AZ.login, AZ.sov ? AZ.sov.at : 0, AZ.zones.join(''), AZ.capLost, AZ.on].join('|');
    if(AZ.memo && AZ.memo.key === key) return AZ.memo;
    const rows = [], edges = [], out = new Map();
    String(AZ.text).split(/\r?\n/).forEach((raw, li) => {
      const ln = raw.trim(); if(!ln) return;
      const parts = ln.split(/\s*(?:»|«|<->|->|→|⇄|↔)\s*/);
      const nm = (w) => { const t = String(w || '').trim().split(/\s+/); for(let k = Math.min(3, t.length); k >= 1; k--){ const id = N && N.byLower.get(t.slice(0, k).join(' ').toLowerCase()); if(id) return id; } return undefined; };
      const A = nm(parts[0] && parts[0].split(/\s+/).slice(-3).join(' ')) || nm(parts[0]), B = nm(parts[1]);
      if(!A || !B || A === B) return rows.push({ln, bad: 'needs two systems'});
      const ia = g.at.get(A), ib = g.at.get(B), ly = itMapLy(ia, ib);
      const r = {ln, a: A, b: B, ia, ib, ly, z: null, use: [false, false], why: ''};
      const s = AZ.sov, me = yours();
      if(!AZ.on){ r.off = true; rows.push(r); return; }   // 041's switch off: no sov read, no zones (the plan's change 8)
      if(!s){ r.why = AZ.sovErr ? 'sovereignty not read: left out of routes' : 'reading sovereignty…'; rows.push(r); return; }
      const ha = s.sys.get(A), hb = s.sys.get(B), who = me || (ha && ha === hb ? ha : null);
      if(!who) r.why = ha && hb && ha !== hb ? 'its two ends are held by different alliances: left out of routes' : `${itSysName(ha ? B : A)} isn't held by any alliance: left out of routes`;
      else if(ha !== who || hb !== who){ const x = ha !== who ? A : B, h = s.sys.get(x); r.why = h ? `${itSysName(x)} is held by ${orgName(h)}, not your alliance: left out of routes` : `${itSysName(x)} isn't held by any alliance: left out of routes`; }
      else {
        const cap = s.caps.get(who); r.cap = cap; r.who = who;
        const zt = (x) => cap ? azZone(itMapLy(g.at.get(x), g.at.get(cap))) : 5;
        r.z = [zt(B), zt(A)];   // [a → b arrives in b's zone, b → a arrives in a's zone]
        r.use = [AZ.zones.includes(r.z[0]), AZ.zones.includes(r.z[1])];
        if(r.use[0]){ edges.push([ia, ib]); } if(r.use[1]){ edges.push([ib, ia]); }
      }
      rows.push(r);
    });
    for(const [x, y] of edges){ (out.get(x) || out.set(x, []).get(x)).push(y); }
    const pair = new Map(); for(const r of rows) if(r.ia !== undefined && r.ib !== undefined) pair.set(Math.min(r.ia, r.ib) * 65536 + Math.max(r.ia, r.ib), r);
    AZ.memo = {key, rows, edges, out, pair};
    return AZ.memo;
  }
  AZ.bridges = azBridges;
  const isJb = (a, b) => azBridges().pair.get(Math.min(a, b) * 65536 + Math.max(a, b));
  function azChanged(){ AZ.memo = null; itRp.key = ''; azPaintBox(); if(itm.el) itMapRefresh(true); const rb = document.querySelector('[data-it-rp-box]'); if(rb) itRpRefresh(); }
  AZ.changed = azChanged;
  // ---- Threat Vector's route: the ticked directions join the gates for the search (the build: itRpUpdate reads them itself)
  const rpUpdate0 = itRpUpdate;
  itRpUpdate = function(){
    const T = itMapTable(); if(!T) return rpUpdate0();
    const B = azBridges(), k = B.edges.map(e => e.join('>')).join(',');
    if(k !== AZ.key){ AZ.key = k; itRp.key = ''; }
    if(!B.edges.length) return rpUpdate0();
    const adj0 = T.adj; T.adj = adj0.map((a, i) => B.out.has(i) ? a.concat(B.out.get(i)) : a);
    try{ return rpUpdate0(); } finally { T.adj = adj0; }
  };
  // ---- the map: bridges drawn (041's look: solid curves in the game's green), a route's bridge step curved too, hover on a bridge
  function ctl(x1, y1, x2, y2){ const mx = (x1 + x2) / 2, my = (y1 + y2) / 2, dx = x2 - x1, dy = y2 - y1; return [mx - dy * 0.22, my + dx * 0.22]; }
  window.__AZbridges = (c, X, Y, big) => {
    if(!AZ.on) return;
    const B = azBridges(); c.save(); c.lineCap = 'round';
    for(const r of B.rows){ if(r.ia === undefined) continue;
      const [p, q] = r.ia < r.ib ? [r.ia, r.ib] : [r.ib, r.ia], hov = AZ.hover === p * 65536 + q;
      const x1 = X(p), y1 = Y(p), x2 = X(q), y2 = Y(q), [cx, cy] = ctl(x1, y1, x2, y2);
      c.strokeStyle = COL; c.globalAlpha = hov ? 1 : r.z ? 0.8 : 0.4; c.lineWidth = (big ? 1.8 : 1.3) + (hov ? 1.5 : 0);
      c.setLineDash(r.z ? [] : [4, 4]);
      c.beginPath(); c.moveTo(x1, y1); c.quadraticCurveTo(cx, cy, x2, y2); c.stroke();
    }
    c.restore(); c.setLineDash([]);
  };
  window.__AZcurve = (c, a, b, X, Y) => {
    if(!isJb(a, b) || itGraphGet().adj[a].includes(b)) return false;
    const [p, q] = a < b ? [a, b] : [b, a], [cx, cy] = ctl(X(p), Y(p), X(q), Y(q));
    if(a === p) c.quadraticCurveTo(cx, cy, X(q), Y(q)); else c.quadraticCurveTo(cx, cy, X(p), Y(p));
    return true;
  };
  function azHit(x, y){
    if(!AZ.on || !itm.Q) return null;
    const Q = itm.Q, lim = itRpTouch() ? 12 : 7; let best = null, bd = lim * lim;
    for(const r of azBridges().rows){ if(r.ia === undefined) continue;
      const [p, q] = r.ia < r.ib ? [r.ia, r.ib] : [r.ib, r.ia], x1 = Q[2 * p], y1 = Q[2 * p + 1], x2 = Q[2 * q], y2 = Q[2 * q + 1], [cx, cy] = ctl(x1, y1, x2, y2);
      for(let k = 0; k <= 24; k++){ const t = k / 24, u = 1 - t, px = u * u * x1 + 2 * u * t * cx + t * t * x2, py = u * u * y1 + 2 * u * t * cy + t * t * y2, d = (px - x) ** 2 + (py - y) ** 2; if(d < bd){ bd = d; best = {r, key: p * 65536 + q}; } }
    }
    return best;
  }
  const zTxt = (z) => z === 1 ? 'zone 1 · free' : `zone ${z} · ×${ZMUL[z]}`;
  const useTxt = (r) => r.use[0] && r.use[1] ? 'Routes use it both ways' : r.use[0] ? `Routes use it toward ${itSysName(r.b)} only` : r.use[1] ? `Routes use it toward ${itSysName(r.a)} only` : 'Routes don’t use it (its zones aren’t ticked in Routes)';
  function azTipHtml(r){
    let h = `<b>Jump bridge</b> <span class="d">${escapeHtml(itSysName(r.a))} ⇄ ${escapeHtml(itSysName(r.b))} · ${itMapLyText(r.ly)} LY</span>`;
    if(r.z){
      h += `<br>→ ${escapeHtml(itSysName(r.b))}: <b class="it-az-z${r.z[0]}">${escapeHtml(zTxt(r.z[0]))}</b><br>→ ${escapeHtml(itSysName(r.a))}: <b class="it-az-z${r.z[1]}">${escapeHtml(zTxt(r.z[1]))}</b>`;
      h += `<br><span class="d">${escapeHtml(r.cap ? `from ${orgName(r.who)}'s capital, ${itSysName(r.cap)}` : `${orgName(r.who)} has no capital: every jump counts as zone 5`)}</span>`;
      h += `<br><span class="${r.use[0] || r.use[1] ? 'it-az-ok' : 'd'}">${escapeHtml(useTxt(r))}</span>`;
    } else h += `<br><span class="it-rp-w">⚠ ${escapeHtml(r.why)}</span>`;
    return h;
  }
  const tip0 = itMapTip;
  itMapTip = function(i, x, y){
    const hit = i < 0 && x !== undefined ? azHit(x, y) : null, k = hit ? hit.key : -1;
    if(k !== AZ.hover){ AZ.hover = k; itMapDraw(); }
    if(!hit) return tip0(i, x, y);
    const tip = itm.tip; tip.innerHTML = azTipHtml(hit.r); tip.hidden = false; tip.classList.remove('it-rp-act');
    const tw = tip.offsetWidth, th = tip.offsetHeight;
    tip.style.left = Math.max(4, Math.min(itm.W - tw - 6, x + 14)) + 'px'; tip.style.top = (y + th + 18 > itm.H ? Math.max(4, y - th - 12) : y + 14) + 'px';
    const cv = itm.el.querySelector('canvas'); if(cv) cv.style.cursor = 'pointer';
  };
  // ---- the route's bridge steps (the system's hover, and the menu's Threat Vector's route line)
  function azSteps(path){ if(!path) return []; const g = itGraphGet(), out = []; for(let k = 1; k < path.length; k++){ const a = path[k - 1], b = path[k]; const r = !g.adj[a].includes(b) && isJb(a, b); if(r) out.push({a, b, z: r.ia === a ? r.z[0] : r.z[1]}); } return out; }
  AZ.steps = azSteps;
  let azDr = null;
  function azRouteShortest(){   // breadth-first over the graph the route searches (the plan's change 5)
    const T = itMapTable(), B = azBridges(), k = itm.home + '|' + AZ.key;
    if(azDr && azDr.k === k) return azDr.D;
    const n = T.n, D = new Int16Array(n).fill(-1), q = [itm.home]; D[itm.home] = 0;
    for(let h = 0; h < q.length; h++){ const x = q[h]; for(const y of T.adj[x].concat(B.out.get(x) || [])) if(D[y] < 0){ D[y] = D[x] + 1; q.push(y); } }
    azDr = {k, D}; return D;
  }
  const rpTip0 = itRpTipHtml;
  itRpTipHtml = function(i){
    let o;
    if(azBridges().edges.length && itm.home >= 0){ const D0 = itm.D; itm.D = azRouteShortest(); try{ o = rpTip0(i); } finally { itm.D = D0; } }
    else o = rpTip0(i); if(itRpAside || i < 0 || i === itm.home) return o;
    const ids = itGraphGet().ids, st = azSteps(itRpPath(i));
    const add = st.map(s => `<br><span class="it-az-rs">⇢ jump bridge ${escapeHtml(itSysName(ids[s.a]))} → ${escapeHtml(itSysName(ids[s.b]))} · arriving in ${escapeHtml(zTxt(s.z))}</span>`).join('');
    return {h: o.h.replace(/(<br><span class="it-rp-w">|<br><span class="d">on your avoid list|<br><span class="d">right-click|<div class="it-rp-btns)/, add + '$1') + (/(it-rp-w|on your avoid list|right-click|it-rp-btns)/.test(o.h) ? '' : add), act: o.act};
  };
  const sub0 = itRpSubHtml;
  itRpSubHtml = function(path, w){
    if(!path) return '';
    const n = azSteps(path).length;
    return `<small>${escapeHtml(`${path.length - 1} jump${path.length === 2 ? '' : 's'}${n ? ` · ${n} by jump bridge` : ''}${w.length ? ` · ⚠ ${w.length} flagged` : ''}`)}</small>`;
  };
  // ---- Routes box: the zone row (the owner: "a checkbox for each zone with only zone 1 turned on by default"; "Route settings")
  function azStatus(){
    const B = azBridges(), n = B.rows.filter(r => r.ia !== undefined).length, ok = B.rows.filter(r => r.z).length;
    if(!n) return 'Add your bridges in the Jump bridges box to use them in routes.';
    if(!AZ.on) return 'Use jump bridges on the map is off (in the Jump bridges box): routes use stargates only.';
    if(!AZ.sov) return AZ.sovErr ? `Zones need EVE's sovereignty data, which couldn't be read (${AZ.sovErr}): routes use stargates only for now.` : 'Reading EVE’s sovereignty data…';
    const me = yours(), cap = me ? AZ.sov.caps.get(me) : null;
    let t = me ? (cap ? `Measured from your alliance's capital, ${itSysName(cap)} (${orgName(me)}).` : `${orgName(me)} has no capital right now: CCP counts every jump as zone 5 until a new one is set.`) : 'Logged out: each bridge is taken as yours, measured from the capital of the alliance that holds it.';
    return `${t} A jump's zone is where it arrives. ${ok} of ${n} bridge${n === 1 ? '' : 's'} usable.`;
  }
  function azZonesHtml(){
    let h = '<div class="it-rp-avk">jump bridges: use jumps arriving in</div><div class="it-az-zones" role="group" aria-label="Jump bridge zones">';
    for(let z = 1; z <= 5; z++) h += `<label><input type="checkbox" data-az-zone="${z}"${itOnHtml(AZ.zones.includes(z), 'checked')}> zone ${z} <span class="d">${z === 1 ? 'free' : `×${ZMUL[z]}`} · ${ZLY[z]}</span></label>`;
    return h + `</div><div class="c it-az-st">${escapeHtml(azStatus())}</div>`;
  }
  const rpBox0 = itRpBoxHtml;
  itRpBoxHtml = function(numbered){
    const h = rpBox0(numbered); if(!h) return h;
    const k = h.lastIndexOf('<div class="c">For the map');
    return h.slice(0, k) + azZonesHtml() + h.slice(k) + (numbered ? '' : azBoxHtml());   // 041's box right after Routes (gear only)
  };
  // itRpRefresh redraws Routes from itRpBoxHtml(), which here also carries the stand-in box: drop the old one first
  const rpRefresh0 = itRpRefresh;
  itRpRefresh = function(...a){ const f = document.activeElement, ta = f && f.matches && f.matches('[data-az-text]'); if(ta) return azPaintBox(); document.querySelectorAll('[data-az-box]').forEach(e => e.remove()); return rpRefresh0(...a); };
  // ---- 041's Jump bridges box (stand-in), rows with this item's zones
  function azRowsHtml(){
    return azBridges().rows.map(r => {
      if(r.ia === undefined) return `<li class="bad">✗ ${escapeHtml(r.ln)}: ${escapeHtml(r.bad)}</li>`;
      const head = `${escapeHtml(itSysName(r.a))} ⇄ ${escapeHtml(itSysName(r.b))} · ${itMapLyText(r.ly)} LY`;
      if(r.off) return `<li class="ok">✓ ${head}</li>`;
      if(!r.z) return `<li class="${AZ.sov ? 'warn' : 'd'}">${AZ.sov ? '⚠' : '·'} ${head}<span class="it-az-zl">${escapeHtml(r.why)}</span></li>`;
      const dir = (to, z, on) => `<span class="it-az-dir${on ? ' on' : ''}">→ ${escapeHtml(itSysName(to))} <b class="it-az-z${z}">${escapeHtml(zTxt(z))}</b></span>`;
      return `<li class="ok">✓ ${head}<span class="it-az-zl">${dir(r.b, r.z[0], r.use[0])}${dir(r.a, r.z[1], r.use[1])}</span></li>`;
    }).join('');
  }
  function azBoxHtml(){
    const n = azBridges().rows.filter(r => r.ia !== undefined).length;
    return `<div class="it-box it-alias it-az-box" data-az-box><div class="k">Jump bridges <span class="it-az-tag">041 stand-in</span></div>`
      + `<label><input type="checkbox" data-az-on${itOnHtml(AZ.on, 'checked')}> Use jump bridges on the map <span class="d">· ${n} bridge${n === 1 ? '' : 's'}</span></label>`
      + `<div class="c">One per line: <code>A » B</code>. Each row shows the zone each way: a jump costs by the zone it arrives in, from your alliance's capital.</div>`
      + `<textarea data-az-text rows="5" spellcheck="false" aria-label="Your jump bridges, one per line">${escapeHtml(AZ.text)}</textarea><ul>${azRowsHtml()}</ul></div>`;
  }
  function azPaintBox(){ const b = document.querySelector('[data-az-box] ul'); if(b) b.innerHTML = azRowsHtml(); const st = document.querySelector('.it-az-st'); if(st) st.textContent = azStatus(); }
  document.addEventListener('change', (e) => {
    const t = e.target; if(!t || !t.closest) return;
    if(t.matches('[data-az-zone]')){ const z = Number(t.dataset.azZone); AZ.zones = t.checked ? [...new Set([...AZ.zones, z])].sort() : AZ.zones.filter(v => v !== z); azChanged(); const f = document.querySelector(`[data-az-zone="${z}"]`); if(f) f.focus({preventScroll: true}); }
    else if(t.matches('[data-az-on]')){ AZ.on = t.checked; azChanged(); if(AZ.on && !AZ.sov) azSovRead(); }
  });
  document.addEventListener('input', (e) => { const t = e.target; if(t && t.matches && t.matches('[data-az-text]')){ AZ.text = t.value; azChanged(); } });
  const css = document.createElement('style');
  css.textContent = `.it-az-zones{display:flex; flex-direction:column;} .it-az-zones label{margin:2px 0;}
    .it-alias li.warn{color:var(--amber);} .it-alias li.d{color:var(--text-dim);}
    .it-az-zl{display:flex; flex-wrap:wrap; gap:2px 12px; padding-left:14px; color:var(--text-dim); font-size:11.5px;}
    .it-az-dir{opacity:.75;} .it-az-dir.on{opacity:1; color:var(--text);} .it-az-z1{color:var(--it-clear);} .it-az-z2,.it-az-z3,.it-az-z4,.it-az-z5{color:var(--amber);}
    .it-az-tag{font:600 10px var(--sans); color:var(--text-dim); border:1px solid var(--line); border-radius:3px; padding:0 4px; margin-left:4px;}
    .it-az-rs{color:#7fe08a;} .it-map-tip .it-az-ok{color:#7fe08a;}
    @media (max-width: 599px){ .it-az-zones label{min-height:44px;} }`;
  document.head.appendChild(css);
  // ---- MOCKUP box
  window.MKAZ = {boot(){
    const d = document.createElement('div'); d.id = 'mkAz';
    d.innerHTML = `<b>MOCKUP</b> <label><input type="checkbox" data-mk="login" checked> logged in (Mockup Coalition)</label><label><input type="checkbox" data-mk="cap"> capital lost</label>`
      + `<span class="mk-you">you in <button type="button" data-mk-you="C-J6MT">C-J6MT</button><button type="button" data-mk-you="F39H-1">F39H-1</button></span><button type="button" data-mk="gear">Intel settings</button>`;
    d.style.cssText = 'position:fixed; right:8px; top:8px; z-index:99; background:#2a1d3a; border:1px solid #a98bd8; border-radius:6px; padding:6px 8px; font:12px system-ui; color:#eee; display:flex; flex-wrap:wrap; gap:4px 10px; align-items:center; max-width:calc(100vw - 32px);';
    document.body.appendChild(d);
    d.addEventListener('change', (e) => { const k = e.target.dataset.mk; if(k === 'login'){ AZ.login = e.target.checked; azChanged(); } if(k === 'cap'){ AZ.capLost = e.target.checked; AZ.sov = null; azChanged(); azSovRead(); } });
    d.addEventListener('click', (e) => { const y = e.target.dataset.mkYou; if(y) window.__MKlocal(y); if(e.target.dataset.mk === 'gear'){ const g = document.querySelector('[data-it-act="gear"]'); if(g) g.click(); setTimeout(() => { const b = document.querySelector('[data-it-rp-box]'); if(b) b.scrollIntoView({block: 'center'}); }, 300); } });
  }};
})();
