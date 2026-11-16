// Prototype (research session, 2026-11-16): the Intel map's filters stacked, as the panel review recommended (Project doc
// claude/roadmap/map-filter-model-panel.md). The owner: "since you provided recommendations, how about you build a prototype using them
// and i'll decide after." Built on main 51207b6 (v2026.11.16.1, after 053). Mockup shortcuts, not for the build: function overrides,
// seven hooks in the page (build_stk.py), storage in memory, the popovers placed by hand.
//
// The model:
//  - Colour by (one, or none: press the one that is on): Security, Jumps from you, Region. Nothing else colours a dot.
//  - Show only (any number, each on/off, each keeps its settings while off): Security range, Within N jumps, Intel reports, Kills,
//    Wormholes, Sov upgrades (053's picks, plus Level boxes: any you tick). Every condition that is on must match; within one, any pick counts.
//  - While any condition is on: a matching system is bright anywhere, the rest dim (0.16); the distance fade steps aside (gates still fade).
//    Zoomed out, a matching dot is also 1.6 px bigger (MOCKUP box "Matches"; added after the first look: brightness alone was hard to spot).
//  - Marks (report rings, alert glow, your pin, wormhole rings, ✕ kills, routes) are never faded by a condition.
//  - View: Paths to you, as today.
//  - A settings button shows only while its filter is on (or its panel is open); switching a filter off shuts its panel (the owner, 2026-11-16).
//  - The legend gets a second line "Only: … · N match"; a "N match ›" chip steps through the matches, nearest first.
(() => {
  const SKEY = 'tvMapStackMock';
  const COLOURS = ['sec', 'jumps', 'region'], CONDS = ['secr', 'near', 'reports', 'kills', 'wh', 'sov'];
  const D0 = {colour: 'sec', view: 'map', on: {secr: false, near: false, reports: false, kills: false, wh: false, sov: false},
    secr: {lo: -5, hi: -3}, near: {n: 5}, sovLv: [], pal: 'reserved', emph: 'big', look: 'soft', glow: 'half', whLook: 'bold', seen: {}};
  const clone = (o) => JSON.parse(JSON.stringify(o));
  let ST = clone(D0);
  try{ const s = JSON.parse(localStorage.getItem(SKEY) || 'null'); if(s && typeof s === 'object') ST = Object.assign(clone(D0), s, {on: Object.assign(clone(D0.on), s.on || {})}); }catch(e){ }
  ST.sovLv = (Array.isArray(ST.sovLv) ? ST.sovLv : [ST.sovLv]).map(Number).filter((n) => n >= 1 && n <= 3);   // an older build kept one number
  const save = () => { try{ localStorage.setItem(SKEY, JSON.stringify(ST)); }catch(e){ } };
  const live = () => typeof itm !== 'undefined' && !!itm.box && !!itm.cv && itm.cv.parentNode === itm.box;
  const anyOn = () => itm.filter !== 'paths' && CONDS.some(k => ST.on[k]);
  const esc = (t) => escapeHtml(String(t));
  const tenth = (v) => (v / 10).toFixed(1);

  // ---- Region colours: today's, or with the reserved hues taken out (cyan = focus, amber = alert, lilac/pink = wormholes) ----
  const REG_TODAY = IT_MAP_REGION.slice();
  const REG_RES = ['#5fbf7f', '#d9687f', '#c9c35a', '#5f8fd9', '#3f9f8f', '#b08a6a', '#8fa0b8', '#9fbf4f'];
  function palSet(){ const p = ST.pal === 'today' ? REG_TODAY : REG_RES; for(let i = 0; i < IT_MAP_REGION.length; i++) IT_MAP_REGION[i] = p[i]; }
  palSet();

  // ---- the filter column: three groups ----
  const F = Object.fromEntries(IT_MAP_FILTERS.map(f => [f.k, f]));
  const I = (d) => `<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${d}</svg>`;
  F.secr = {k: 'secr', name: 'Security range', note: 'only: systems whose security is in your range', icon: I('<path d="M9 2.5a6.5 6.5 0 1 0 0 13" /><path d="M9 2.5a6.5 6.5 0 0 1 0 13" stroke-dasharray="2 2"/><path d="M6 9h6M6 7v4M12 7v4"/>')};
  F.near = {k: 'near', name: 'Within N jumps', note: 'only: systems this many gate jumps from you or fewer', icon: I('<circle cx="9" cy="9" r="1.6" fill="currentColor"/><circle cx="9" cy="9" r="4"/><circle cx="9" cy="9" r="7" stroke-dasharray="2 2.2"/>')};
  F.sec.note = 'colour: each system in its security colour, as in the game';
  F.jumps.note = 'colour: by stargate jumps from your system';
  F.region.note = 'colour: one per region; neighbours differ';
  F.reports.note = 'only: systems with a report or a live wormhole report';
  F.kills.note = 'only: systems with kills in Intel';
  F.wh.note = 'only: systems with a kept wormhole (its list beside it)';
  F.sov.note = 'only: systems with an upgrade you picked (at a level you ticked)';
  F.paths.note = 'view: the gate routes from hostiles inside your alert range to you, as a tree';
  IT_MAP_FILTERS.length = 0; IT_MAP_FILTERS.push(F.sec, F.jumps, F.region, F.secr, F.near, F.reports, F.kills, F.wh, F.sov, F.paths);
  const pbtn = (k, label) => `<button type="button" class="it-map-pb mk-pb" data-mk-pn="${k}" aria-haspopup="dialog" aria-expanded="false" aria-label="${label}" title="${label}">${I('<path d="M3 5h12M3 9h12M3 13h12"/><circle cx="6" cy="5" r="1.6" fill="currentColor"/><circle cx="12" cy="9" r="1.6" fill="currentColor"/><circle cx="8" cy="13" r="1.6" fill="currentColor"/>')}</button>`;
  IT_MAP_PANEL_BTN.secr = () => pbtn('secr', 'Security range: from and to');
  IT_MAP_PANEL_BTN.near = () => pbtn('near', 'Within N jumps: how many');
  itMapFbtnsHtml = function(){
    const one = (f) => IT_MAP_PANEL_BTN[f.k] ? `<span class="it-map-fw">${itMapFbtnHtml(f)}${itMapPanelBtnHtml(f.k)}</span>` : itMapFbtnHtml(f);
    const sep = (t) => `<span class="mk-sep" aria-hidden="true" title="${t}"></span>`;
    return IT_MAP_FILTERS.map(f => (f.k === 'secr' ? sep('Show only: switch on any number') : f.k === 'paths' ? sep('View') : '') + one(f)).join('');
  };

  // ---- which systems match (worked out once per change of the conditions or of what they read; never per system) ----
  const MC = {key: '', draws: -1, m: null, list: []};
  const condKey = () => JSON.stringify([ST.on, ST.secr, ST.near, ST.sovLv]);
  function match(wh0){
    if(!itm.D || !itm.P) return null;
    if(!wh0 && MC.draws === itm.draws && MC.m) return MC.m;
    const T = itMapTable(), wh = wh0 || itm.wh || itMapWh();
    const key = condKey() + '|' + itm.home + '|' + (ST.on.wh || ST.on.reports ? [...wh.kept.keys()].join(',') + '/' + [...wh.live.keys()].join(',') : '') + '|'
      + (ST.on.sov ? sovIndexKey() + '#' + sovStore().pick.join(',') : '') + '|' + [...itm.rep].map(([i, r]) => i + ':' + (r.kills || 0)).join(',');
    if(!wh0) MC.draws = itm.draws;
    if(key === MC.key && MC.m) return MC.m;
    const n = T.n, m = new Uint8Array(n), D = itm.D, lo = Math.min(ST.secr.lo, ST.secr.hi) / 10, hi = Math.max(ST.secr.lo, ST.secr.hi) / 10;
    const sv = ST.on.sov ? sovIndex() : null, pick = new Set(ST.on.sov ? sovStore().pick : []), lvT = sovTable().lv;
    for(let i = 0; i < n; i++){
      let ok = true;
      if(ST.on.secr){ const v = Number(itMapSecText(T.sec[i])); ok = v >= lo - 1e-9 && v <= hi + 1e-9; }   // the number the map shows
      if(ok && ST.on.near) ok = D[i] >= 0 && D[i] <= ST.near.n;
      if(ok && ST.on.reports) ok = itm.rep.has(i) || wh.live.has(i);
      if(ok && ST.on.kills) ok = !!(itm.rep.get(i) || {}).kills;
      if(ok && ST.on.wh) ok = wh.kept.has(i);
      if(ok && ST.on.sov){ const e = sv.at.get(i); ok = false; if(e) for(const [k, l] of e) if(pick.has(k) && (!lvT.has(k) || !ST.sovLv.length || ST.sovLv.includes(l))){ ok = true; break; } }
      m[i] = ok ? 1 : 0;
    }
    const list = []; for(let i = 0; i < n; i++) if(m[i] && i !== itm.home) list.push(i);
    list.sort((a, b) => (D[a] < 0 ? 1e9 : D[a]) - (D[b] < 0 ? 1e9 : D[b]));
    Object.assign(MC, {key, m, list}); MKS.step = -1;
    return m;
  }
  window.__MKalpha = (i, alpha0) => {
    if(!live() || !anyOn()) return alpha0(i);
    if(i === itm.home) return 1;
    const m = match(); return m && m[i] ? 1 : IT_MAP_DIM;   // bright anywhere, or dim: one meaning
  };
  // the owner, 2026-11-16: "can we make the yellow background circles for "within your alert range" a bit smaller? maybe try 50% of
  // current diameter?", then "i'm fine with today's diameter while zoomed in but want the new smaller diameter when zoomed out. it's much
  // better." Zoomed out: half the diameter; zoomed in: today's (r + 9). MOCKUP box "Alert glow": Today / Half zoomed out (default).
  window.__MKglow = (big, r, g) => { const today = big ? r + 9 : 22 * Math.min(1.4, Math.sqrt(g / IT_MAP_START_GATE)); return ST.glow === 'today' || !live() || big ? today : today / 2; };
  window.__MKbig = () => live() && anyOn() && ST.emph === 'big';   // zoomed out, a matching dot 1.6 px bigger (the MOCKUP box's Matches row)
  // Q21 (the owner, 2026-11-16: "045's bold + pulse", "Off-filter rule", "Match chip replaces it"): with the Wormholes filter on, the kept
  // holes that match every filter that is on get the Wormholes filter's marks; a hole that doesn't match keeps only the off-filter rule
  // (fresh and inside "Map: within": thin rings, as a report; otherwise no wormhole mark). The match chip steps through them.
  window.__MKwh = () => live() && anyOn() && ST.on.wh;
  window.__MKmark = (kept, live0) => {
    if(!window.__MKwh()) return itm.filter === 'wh' ? kept : live0;
    const m = match({kept, live: live0}), out = new Map(live0);
    for(const [i, w] of kept) if(m && m[i]) out.set(i, w);
    return out;
  };
  window.__MKwhBold = (i) => window.__MKwh() && ST.whLook === 'bold' && !!itm.wh && itm.wh.kept.has(i) && matched(i);   // the MOCKUP box's Wormholes row can show thin rings instead
  window.__MKsov = () => live() && itm.filter !== 'paths' && ST.on.sov;   // the hover names the upgrades
  const dim0 = itMapDimmed;
  itMapDimmed = function(i){ if(live() && anyOn()){ if(i === itm.home) return false; const m = match(); return !(m && m[i]); } return dim0(i); };
  const key0 = itMapKey;
  itMapKey = function(){ return key0() + '|mk:' + condKey() + (ST.on.sov ? '|' + sovIndexKey() + '#' + sovStore().pick.join(',') : ''); };

  // ---- pressing a filter ----
  // the owner, 2026-11-16 ("my one remaining concern right now, is that i can't toggle anything "off". this isn't an easy view to read."):
  // pressing the colour that is on turns colour off: every system a plain grey, no number in its circle; marks and matches stand out
  const PLAIN = '#56616b';
  const plain = () => live() && ST.colour === '' && itm.filter !== 'paths';
  window.__MKplain = plain;
  // the owner, 2026-11-16: "it's about the base color groups sort of washing out the other data". Soft colour (MOCKUP box "Colour"):
  // zoomed out, a system's colour mixed 45% toward the map's background; zoomed in, a dark disc tinted with the colour instead of a
  // solid one. A system your conditions match keeps the full, solid colour, so matches stand out.
  const BG = [12, 16, 20], softC = new Map();
  const soften = (hex) => { if(softC.has(hex)) return softC.get(hex); const n = parseInt(hex.slice(1), 16), c = [n >> 16, (n >> 8) & 255, n & 255].map((v, k) => Math.round(v * 0.55 + BG[k] * 0.45)), out = '#' + c.map(v => v.toString(16).padStart(2, '0')).join(''); softC.set(hex, out); return out; };
  const tintC = new Map(), tint = (hex) => { const h = plain() ? PLAIN : hex; if(tintC.has(h)) return tintC.get(h); const n = parseInt(h.slice(1), 16), c = [n >> 16, (n >> 8) & 255, n & 255].map((v, k) => Math.round(v * 0.38 + BG[k] * 0.62)), out = '#' + c.map(v => v.toString(16).padStart(2, '0')).join(''); tintC.set(h, out); return out; };
  const matched = (i) => { if(!anyOn()) return false; const m = match(); return !!(m && m[i]); };
  const soft = () => live() && ST.look === 'soft' && itm.filter !== 'paths';
  const fcol0 = itMapFcol;
  itMapFcol = function(i){ const c = plain() ? PLAIN : fcol0(i); return soft() && i !== itm.home && !matched(i) && c[0] === '#' && c.length === 7 ? soften(c) : c; };
  window.__MKcircle = (c, i, x, y, r, a) => {
    if(i === itm.home) return false;
    if(matched(i) && window.__MKbig()){   // zoomed in, a match's disc a quarter bigger (the owner: no difference seen between Brighter and Brighter + bigger)
      c.globalAlpha = a; c.fillStyle = itMapFcol(i); c.beginPath(); c.arc(x, y, r * 1.25, 0, 6.283); c.fill();
      c.globalAlpha = 1; c.lineWidth = 1.5; c.strokeStyle = '#0c1014'; c.stroke();
      return true;
    }
    if(!soft() || matched(i)) return false;   // the page's own solid disc
    // a dark disc tinted with the colour, no coloured outline: a ring on this map means a report (a red outline read as a hostile)
    c.globalAlpha = a; c.fillStyle = tint(fcol0(i)); c.beginPath(); c.arc(x, y, r, 0, 6.283); c.fill();
    c.globalAlpha = 1; c.lineWidth = 1.5; c.strokeStyle = '#0c1014'; c.stroke();
    return true;
  };
  const fleg0 = itMapFLegHtml, ftit0 = itMapFLegTitle;
  itMapFLegHtml = function(){ return plain() ? `<b>No colour</b> ${itMapSwHtml([PLAIN])} every system plain · press Security, Jumps or Region to colour them` : fleg0(); };
  itMapFLegTitle = function(){ return plain() ? 'No colour: the systems are plain grey, so reports, wormholes, kills and the systems your conditions match stand out' : ftit0(); };
  function apply(){ itm.filter = ST.view === 'paths' ? 'paths' : (ST.colour || 'sec'); }
  function redraw(){
    save(); apply(); itMapFbarPaint(true); itMapLegend();
    if(itm.P){ itMapDraw(); if(itm.rep && itm.D) itm.key = itMapKey(); }
    popPaint(); if(typeof sovShown === 'function' && sovShown()) sovPaint(true);
  }
  itMapFilterSet = function(k){
    if(!IT_MAP_FILTERS.some(f => f.k === k)) return;
    if(COLOURS.includes(k)){ ST.colour = ST.colour === k && ST.view === 'map' ? '' : k; ST.view = 'map'; }   // the colour that is on, pressed again: no colour
    else if(k === 'paths') ST.view = ST.view === 'paths' ? 'map' : 'paths';
    else {
      ST.on[k] = !ST.on[k];
      if(ST.on[k] && k === 'sov' && !sovStore().pick.length) sovOpen(true, false);
      else if(ST.on[k] && (k === 'secr' || k === 'near') && !ST.seen[k]){ ST.seen[k] = 1; setTimeout(() => popOpen(k), 0); }   // the first time: its settings
      else if(!ST.on[k]){   // the owner: "disabling a filter (like security range) should hide the settings button for it": its panel shuts too
        if(popK === k) popClose(false);
        if(k === 'sov' && sovShown()) sovOpen(false);
        if(k === 'wh' && itWhListShown()) itWhListOpen(false);
      }
    }
    redraw();
  };
  const paint0 = itMapFbarPaint;
  itMapFbarPaint = function(changed){
    paint0(changed);
    const fb = itm.el && itm.el.querySelector('.it-map-fb'); if(!fb) return;
    for(const b of fb.querySelectorAll('[data-im-f]')){
      const k = b.dataset.imF, on = k === ST.colour || (k === 'paths' && ST.view === 'paths') || (CONDS.includes(k) && ST.on[k]);
      if(b.getAttribute('aria-pressed') !== String(on)) b.setAttribute('aria-pressed', String(on));
    }
    const cur = fb.querySelector('.it-map-fcur'), n = CONDS.filter(k => ST.on[k]).length, cn = ST.colour ? F[ST.colour].name : 'no colour';
    if(!ST.colour && ST.view === 'map'){ const fn = fb.querySelector('.it-map-fn'), h = '<b>No colour</b> <span>press Security, Jumps or Region to colour the systems again</span>'; if(fn.innerHTML !== h) fn.innerHTML = h; }
    cur.title = `Map: ${cn}${n ? `, ${n} condition${n > 1 ? 's' : ''} on` : ''}`;
    let bd = cur.querySelector('.mk-bd'); if(n && !bd){ bd = document.createElement('span'); bd.className = 'mk-bd'; cur.appendChild(bd); }
    if(bd){ if(n) bd.textContent = String(n); else bd.remove(); }
    itm.ctlKey = ''; itMapCtlPlace();
  };

  // ---- the legend's second line and the match chip ----
  function onlyHtml(){
    const p = [], m = match(), n = MC.list.length;
    if(ST.on.secr){ const lo = Math.min(ST.secr.lo, ST.secr.hi), hi = Math.max(ST.secr.lo, ST.secr.hi); p.push(lo === hi ? `security ${tenth(lo)}` : `security ${tenth(lo)} to ${tenth(hi)}`); }
    if(ST.on.near) p.push(`within ${ST.near.n} jumps`);
    if(ST.on.sov){ const ks = sovPicked().map(sovShow); p.push((ks.length ? (ks.length > 2 ? `${ks.slice(0, 2).join(', ')} +${ks.length - 2}` : ks.join(', ')) : 'no upgrade picked') + (ST.sovLv.length ? ` level ${ST.sovLv.join(', ')}` : '')); }
    if(ST.on.reports) p.push('a report'); if(ST.on.kills) p.push('kills'); if(ST.on.wh) p.push('a wormhole');
    return `<b>Only</b> <b>${m ? n : 0} match</b> · ${esc(p.join(' · '))}`;   // the count first, so a narrow screen never loses it
  }
  function legOnly(){
    const leg = itm.el && itm.el.querySelector('.it-map-leg'); if(!leg) return;
    let o = leg.querySelector('.mk-only');
    if(!anyOn()){ if(o) o.remove(); return; }
    if(!o){ o = document.createElement('div'); o.className = 'it-map-fl mk-only'; o.title = 'Every condition that is on must match; inside one, any pick counts. Hostile and neutral rings, the alert glow and your pin never fade.'; const f = leg.querySelector('.it-map-fl'); if(f) f.after(o); else leg.prepend(o); }
    const h = onlyHtml(); if(o._h !== h){ o.innerHTML = h; o._h = h; }
  }
  const leg0 = itMapLegend;
  itMapLegend = function(){ leg0(); if(live()) legOnly(); };
  let chip = null;
  window.MKS = {step: -1};
  function chipPaint(){
    if(!itm.box) return;
    if(!chip || !chip.isConnected){ chip = document.createElement('button'); chip.type = 'button'; chip.className = 'mk-mt'; chip.hidden = true; itm.box.appendChild(chip); }
    const on = anyOn(); if(!on){ if(!chip.hidden) chip.hidden = true; return; }
    match(); const n = MC.list.length, s = MKS.step;
    const t = !n ? 'No system matches' : s >= 0 ? `${s + 1} of ${n} ›` : `${n} match ›`;
    if(chip.textContent !== t) chip.textContent = t;
    chip.disabled = !n; chip.title = n ? 'Step through the matching systems, nearest first' : 'Nothing on the map matches every condition that is on';
    chip.hidden = false;
    const bs = itm.box.querySelector('.it-map-fbtns'), fc = itm.box.querySelector('.it-map-fcur'), el = bs && bs.offsetParent ? bs : fc, bx = itm.box.getBoundingClientRect();
    let left = 8; if(el){ const r = el.getBoundingClientRect(); if(r.bottom > bx.bottom - 52) left = Math.round(r.right - bx.left + 8 + (bs && bs.offsetParent && !itMapPhone() ? 40 : 0)); }
    const css = `left:${left}px;`; if(chip.style.cssText !== css) chip.style.cssText = css;
  }
  function chipNext(){
    match(); const L = MC.list; if(!L.length || !itm.P) return;
    MKS.step = (MKS.step + 1) % L.length;
    const i = L[MKS.step], v = itm.view; v.tx = itMapFreeX() - itm.P[2 * i] * v.k; v.ty = itm.H / 2 - itm.P[2 * i + 1] * v.k;
    itm.rowHover = i; itMapTip(-1); itMapDraw(); itm.rowHover = -1;
  }
  const draw0 = itMapDraw;
  itMapDraw = function(){ draw0(); if(live()){ chipPaint(); legOnly(); } };

  // ---- the settings popovers (Security range, Within N jumps) and Sov's level row ----
  let pop = null, popK = '';
  const stepper = (key, label, val, aria) => `<span class="rs mk-rs" role="group" aria-label="${esc(label)}"><span class="rs-l">${esc(label)}</span><span class="rs-c"><button type="button" class="rs-b" data-mk-d="${key}:-1" aria-label="${esc(aria || label)}: less">−</button><input class="rs-v mk-v" readonly value="${esc(val)}" aria-label="${esc(aria || label)}"><button type="button" class="rs-b" data-mk-d="${key}:1" aria-label="${esc(aria || label)}: more">+</button></span></span>`;
  function popHtml(k){
    const off = !ST.on[k] ? `<div class="mk-off">Off: press its filter button to use it. Your setting is kept.</div>` : '';
    const cnt = ST.on[k] ? `<div class="mk-cnt">${MC.list.length} system${MC.list.length === 1 ? '' : 's'} match every condition that is on</div>` : '';
    if(k === 'secr') return `<div class="it-whp-h"><h4>Security range</h4><button type="button" class="x-close" data-mk-x aria-label="Close" title="Close (Esc)">×</button></div>${off}`
      + `<div class="mk-row">${stepper('lo', 'From', tenth(ST.secr.lo), 'Security from')}${stepper('hi', 'To', tenth(ST.secr.hi), 'Security to')}</div>`
      + `<div class="mk-q"><span>Quick:</span><button type="button" data-mk-q="hi">High</button><button type="button" data-mk-q="low">Low</button><button type="button" data-mk-q="null">Null</button></div>`
      + `<div class="mk-note">Both ends count, in either order. It compares the number the map shows (one decimal).</div>${cnt}`;
    return `<div class="it-whp-h"><h4>Within N jumps</h4><button type="button" class="x-close" data-mk-x aria-label="Close" title="Close (Esc)">×</button></div>${off}`
      + `<div class="mk-row">${stepper('n', 'Within', String(ST.near.n), 'Within jumps')}<span class="rs-u">jumps</span></div>`
      + `<div class="mk-note">By stargate from your system, as Jumps from you counts. “Map: within” still sets how far reports and names show.</div>${cnt}`;
  }
  function popOpen(k){
    if(!itm.box) return;
    if(typeof sovShown === 'function' && sovShown()) sovOpen(false);
    if(typeof itWhListShown === 'function' && itWhListShown()) itWhListOpen(false);
    if(!pop || !pop.isConnected){ pop = document.createElement('div'); pop.className = 'it-whp mk-pop'; pop.setAttribute('role', 'dialog'); pop.hidden = true; itm.box.appendChild(pop); }
    popK = k; pop.setAttribute('aria-label', F[k].name); pop.hidden = false; popPaint(); popPlace();
    for(const b of itm.box.querySelectorAll('[data-mk-pn]')) b.setAttribute('aria-expanded', String(b.dataset.mkPn === k));
    const f = pop.querySelector('.rs-b'); if(f) f.focus();
  }
  function popClose(back){
    if(!pop || pop.hidden) return; pop.hidden = true;
    for(const b of itm.box.querySelectorAll('[data-mk-pn]')) b.setAttribute('aria-expanded', 'false');
    if(back){ const b = itm.box.querySelector(`[data-mk-pn="${popK}"]`); if(b && b.offsetParent) b.focus(); }
    popK = '';
  }
  function popPaint(){ if(!pop || pop.hidden || !popK) return; match(); const h = popHtml(popK); if(pop._h !== h){ const foc = document.activeElement && document.activeElement.dataset ? document.activeElement.dataset.mkD : ''; pop.innerHTML = h; pop._h = h; if(foc){ const b = pop.querySelector(`[data-mk-d="${foc}"]`); if(b) b.focus(); } } }
  function popPlace(){
    if(!pop || pop.hidden || !itm.box) return;
    const bx = itm.box.getBoundingClientRect(), bs = itm.box.querySelector('.it-map-fbtns'), f = bs && bs.querySelector(`[data-im-f="${popK}"]`);
    let css;
    if(itMapPhone() || !bs || !bs.offsetParent || !f) css = 'left:8px; right:8px; top:60px; width:auto;';
    else { const sr = bs.getBoundingClientRect(), fr = f.getBoundingClientRect(), L = Math.round(sr.right - bx.left + 6 + 32 + 8), top = Math.round(Math.max(8, Math.min(itm.H - 8 - 230, fr.top - bx.top - 4))); css = `left:${L}px; top:${top}px; width:300px;`; }
    if(pop.style.cssText !== css) pop.style.cssText = css;
  }
  const place0 = itMapCtlPlace;
  itMapCtlPlace = function(){ place0(); popPlace(); };
  const sovOpen0 = sovOpen;
  sovOpen = function(open, ...a){ if(open) popClose(false); return sovOpen0(open, ...a); };
  const whOpen0 = itWhListOpen;
  itWhListOpen = function(open, ...a){ if(open) popClose(false); return whOpen0(open, ...a); };
  const sovPaint0 = sovPaint;
  sovPaint = function(force){
    sovPaint0(force);
    const p = sovP.el; if(!p) return;
    let r = p.querySelector('.mk-sovlv'); if(!r){ r = document.createElement('div'); r.className = 'mk-sovlv'; p.querySelector('.it-sov-picks').after(r); }
    const box = (n) => `<label class="it-sov-k mk-lvk"><input type="checkbox" data-mk-lv="${n}"${ST.sovLv.includes(n) ? ' checked' : ''}> <span>${n}</span></label>`;
    const h = `<div class="mk-lvrow"><b>Level</b>${box(1)}${box(2)}${box(3)}<span class="mk-lvany">${ST.sovLv.length ? '' : 'none ticked: any level'}</span></div><div class="mk-note">Tick one or more (the owner: "why not checkboxes so we can select more than one?"), for the kinds that come in levels (Threat Detection, Exploration, Prospecting); the rest match as picked.${ST.on.sov ? '' : ' The Sov upgrades filter is off: your picks are kept.'}</div>`;
    if(r._h !== h){ r.innerHTML = h; r._h = h; }
  };
  const sc0 = sovChanged;
  sovChanged = function(){ sc0(); if(ST.on.sov && itm.P && live()){ itMapDraw(); itm.key = itMapKey(); popPaint(); } };
  function stepBy(key, d){
    const cl = (v, a, b) => Math.max(a, Math.min(b, v));
    if(key === 'lo' || key === 'hi') ST.secr[key] = cl(ST.secr[key] + d, -10, 10);
    else if(key === 'n') ST.near.n = cl(ST.near.n + d, 1, 30);
    redraw();
  }
  document.addEventListener('click', (e) => {
    const pb = e.target.closest('[data-mk-pn]'); if(pb){ e.stopPropagation(); if(popK === pb.dataset.mkPn && pop && !pop.hidden) popClose(true); else popOpen(pb.dataset.mkPn); return; }
    if(e.target.closest('[data-mk-x]')){ e.stopPropagation(); popClose(true); return; }
    const d = e.target.closest('[data-mk-d]'); if(d){ e.stopPropagation(); const [k, s] = d.dataset.mkD.split(':'); stepBy(k, Number(s)); return; }   // ours alone (053's panel handler would see a button redrawn away)
    const q = e.target.closest('[data-mk-q]'); if(q){ e.stopPropagation(); ST.secr = {hi: {lo: 5, hi: 10}, low: {lo: 1, hi: 4}, null: {lo: -10, hi: 0}}[q.dataset.mkQ]; redraw(); return; }
    if(e.target.closest('.mk-mt')){ e.stopPropagation(); chipNext(); return; }
  }, true);
  document.addEventListener('change', (e) => {   // the Level boxes are ours (053's change handler ignores them, but keep them apart)
    const n = e.target.dataset && Number(e.target.dataset.mkLv); if(!n) return; e.stopPropagation();
    const s = new Set(ST.sovLv); if(e.target.checked) s.add(n); else s.delete(n); ST.sovLv = [...s].sort(); redraw(); const r = document.querySelector(`[data-mk-lv="${n}"]`); if(r) r.focus();
  }, true);
  document.addEventListener('pointerdown', (e) => { if(e.target.closest && e.target.closest('[data-mk-d]')) e.stopPropagation(); }, true);   // the page's own steppers (rsBind) take any .rs-b press
  document.addEventListener('keydown', (e) => { if(e.key === 'Escape' && pop && !pop.hidden){ e.stopPropagation(); popClose(true); } }, true);

  // ---- styles ----
  const css = document.createElement('style');
  css.textContent = `
  /* the owner, 2026-11-16: a filter that is off shows no settings button, hovered or not (052 showed it on hover) */
  @media (hover: hover){ .it-map-fw:hover > [aria-pressed="false"] ~ button.it-map-pb:not([aria-expanded="true"]), .it-map-fw:focus-within > [aria-pressed="false"] ~ button.it-map-pb:not([aria-expanded="true"]){visibility:hidden; opacity:0;} }
  .it-map-fbtns .mk-sep{display:block; width:24px; height:1px; margin:4px 4px; background:var(--line);}
  @media (max-width: 599px){ .it-map-fbtns .mk-sep{width:36px;} }
  button.it-map-fcur{position:relative;}
  .mk-bd{position:absolute; top:-5px; right:-5px; min-width:16px; height:16px; padding:0 4px; border-radius:8px; background:var(--tag-on); border:1px solid var(--line); color:var(--heading); font:700 10px/14px var(--sans); text-align:center;}
  .mk-pop{position:absolute; z-index:6; max-width:calc(100% - 16px);}
  .mk-pop .mk-row{display:flex; flex-wrap:wrap; gap:10px 14px; align-items:center; margin:8px 0 6px;}
  .mk-pop .mk-rs, .mk-sovlv .mk-rs{display:inline-flex; align-items:center; gap:6px;}
  .mk-pop .mk-v{width:4.6ch;}
  .mk-lvrow{display:flex; flex-wrap:wrap; align-items:center; gap:4px 14px; margin:6px 0 2px;} .mk-lvrow > b{font:600 12px var(--sans); color:var(--heading);} .mk-lvk{min-height:24px;} .mk-lvany{color:var(--text-dim); font-size:12px;}
  .mk-pop .mk-q{display:flex; gap:6px; align-items:center; margin:4px 0 8px; color:var(--text-dim); font-size:12px;}
  .mk-pop .mk-q button{min-height:28px; padding:0 10px; font-size:12px;}
  .mk-note{color:var(--text-dim); font-size:12px; line-height:1.4;}
  .mk-off{margin:6px 0 2px; color:var(--amber); font-size:12px;}
  .mk-cnt{margin-top:8px; color:var(--heading); font-size:12px;}
  .mk-sovlv{margin:8px 0 10px; display:flex; flex-direction:column; gap:4px;}
  button.mk-mt{position:absolute; left:8px; bottom:8px; z-index:3; min-height:32px; padding:0 12px; border-radius:6px; border:1px solid var(--line); background:rgba(18,23,28,.9); color:var(--heading); font:700 12px var(--sans); cursor:pointer;}
  button.mk-mt:hover:not(:disabled){border-color:color-mix(in srgb, var(--cyan) 55%, transparent);} button.mk-mt:disabled{color:var(--text-dim); cursor:default;} button.mk-mt[hidden]{display:none;}
  button.mk-mt:focus-visible{outline:2px solid var(--cyan); outline-offset:2px;}
  .it-map-leg .it-map-fl.mk-only{display:block; height:auto; overflow:visible; color:var(--text); white-space:normal; line-height:1.45;}
  @media (max-width: 599px){ button.mk-mt{min-height:44px;} .mk-pop .rs-b{width:44px; height:44px; min-height:44px;} .mk-pop .mk-q button{min-height:44px;} .it-map-box.fb-open button.mk-mt{display:none;} }
  .mk-box{position:fixed; right:12px; top:12px; z-index:9999; width:280px; padding:10px 12px; background:#1b2229; border:2px dashed #e0b341; border-radius:8px; color:#dfe6eb; font:12px/1.4 var(--sans); box-shadow:0 8px 24px rgba(0,0,0,.5);}
  .mk-box b.t{display:block; color:#e0b341; margin-bottom:6px;} .mk-box .r{display:flex; flex-wrap:wrap; gap:6px; align-items:center; margin:6px 0;}
  .mk-box button{min-height:28px; padding:0 10px; font-size:12px;} .mk-box button[aria-pressed="true"]{background:var(--tag-on); color:var(--heading);}
  .mk-box.fold > :not(.mk-hd){display:none;} .mk-box .mk-hd{display:flex; justify-content:space-between; align-items:center;}
  @media (max-width: 599px){ .mk-box{top:auto; bottom:8px; right:auto; left:8px; width:calc(100% - 40px);} .mk-box button{min-height:44px;} }
  `;
  document.head.appendChild(css);

  // ---- the MOCKUP box ----
  function boxMake(){
    const b = document.createElement('div'); b.className = 'mk-box' + (itMapPhone() ? ' fold' : '');
    b.innerHTML = `<div class="mk-hd"><b class="t">MOCKUP: stacked map filters</b><button type="button" data-mkb="fold" aria-label="Fold the mockup box">${itMapPhone() ? '▴' : '▾'}</button></div>`
      + `<div>Made-up Intel and sov list. The filter column has three groups: colour (one, or none: press the one that is on), only (any number), view.</div>`
      + `<div class="r"><button type="button" data-mkb="ex">Your example</button><button type="button" data-mkb="off">All off</button></div>`
      + `<div class="r"><span>Region colours:</span><button type="button" data-mkb="pal-today">Today</button><button type="button" data-mkb="pal-reserved">Reserved</button></div>`
      + `<div class="r"><span>Colour:</span><button type="button" data-mkb="look-full">Full</button><button type="button" data-mkb="look-soft">Soft</button></div>`
      + `<div class="r"><span>Alert glow:</span><button type="button" data-mkb="glow-today">Today</button><button type="button" data-mkb="glow-half">Half, zoomed out</button></div>`
      + `<div class="r"><span title="Only while a condition is on: that's when there are matches">Matches (a condition on):</span><button type="button" data-mkb="emph-bright">Brighter</button><button type="button" data-mkb="emph-big">Brighter + bigger</button></div>`
      + `<div class="r"><span title="Q21: how the matching wormholes look with the Wormholes filter on">Wormholes (Q21):</span><button type="button" data-mkb="whl-thin">Thin rings</button><button type="button" data-mkb="whl-bold">045's bold + pulse</button></div>`
      + `<div class="r"><button type="button" data-mkb="whex">Wormholes only</button></div>`
      + `<div class="mk-note">Your example: Security range −0.5 to −0.3 + Sov upgrades (Threat Detection, level 3), coloured by security.</div>`;
    b.addEventListener('click', (e) => {
      const t = e.target.closest('[data-mkb]'); if(!t) return; const k = t.dataset.mkb;
      if(k === 'fold'){ b.classList.toggle('fold'); t.textContent = b.classList.contains('fold') ? '▴' : '▾'; return; }
      if(k === 'ex') MKP.example();
      if(k === 'off'){ for(const c of CONDS) ST.on[c] = false; popClose(false); redraw(); }
      if(k.startsWith('emph-')){ ST.emph = k.slice(5); redraw(); }
      if(k.startsWith('look-')){ ST.look = k.slice(5); redraw(); }
      if(k.startsWith('glow-')){ ST.glow = k.slice(5); redraw(); }
      if(k.startsWith('whl-')){ ST.whLook = k.slice(4); redraw(); }
      if(k === 'whex') MKP.whExample();
      if(k.startsWith('pal-')){ ST.pal = k.slice(4); palSet(); itMapRegColTab = null; redraw(); }
      boxPaint(b);
    });
    document.body.appendChild(b); boxPaint(b);
  }
  function boxPaint(b){ for(const x of b.querySelectorAll('[data-mkb^="pal-"]')) x.setAttribute('aria-pressed', String(x.dataset.mkb === 'pal-' + ST.pal)); for(const x of b.querySelectorAll('[data-mkb^="emph-"]')) x.setAttribute('aria-pressed', String(x.dataset.mkb === 'emph-' + ST.emph)); for(const x of b.querySelectorAll('[data-mkb^="look-"]')) x.setAttribute('aria-pressed', String(x.dataset.mkb === 'look-' + ST.look)); for(const x of b.querySelectorAll('[data-mkb^="glow-"]')) x.setAttribute('aria-pressed', String(x.dataset.mkb === 'glow-' + ST.glow)); for(const x of b.querySelectorAll('[data-mkb^="whl-"]')) x.setAttribute('aria-pressed', String(x.dataset.mkb === 'whl-' + ST.whLook)); }

  window.MKP = {
    ST: () => ST, match: () => { match(); return MC; }, popOpen, popClose,
    example(){
      for(const c of CONDS) ST.on[c] = false;
      Object.assign(ST, {colour: 'sec', view: 'map', secr: {lo: -5, hi: -3}, sovLv: [3]}); ST.on.secr = true; ST.on.sov = true; ST.seen.secr = 1;
      const st = sovStore(); st.pick = ['Major Threat Detection Array', 'Minor Threat Detection Array']; sovSave(); sovIx = null;
      popClose(false); redraw(); itMapCenter();
    },
    // the owner, 2026-11-16: "there are only two wormholes in the mockup. can you add 12 with varying ranges and ages up to 24 hours and show
    // it to me again so i can see how the treatment differs?" Wormholes on alone, the whole map in view
    whExample(){
      for(const c of CONDS) ST.on[c] = false; ST.on.wh = true; Object.assign(ST, {view: 'map'});
      popClose(false); redraw();
      const P = itm.P, pad = 40, S = [itm.home, ...itm.wh.kept.keys()]; let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;   // every hole and you in view
      for(const i of S){ x0 = Math.min(x0, P[2 * i]); x1 = Math.max(x1, P[2 * i]); y0 = Math.min(y0, P[2 * i + 1]); y1 = Math.max(y1, P[2 * i + 1]); }
      const [fa, fbx] = itMapFree(), cl = itm.fbBox ? Math.max(fa, itm.fbBox[2]) : fa, wf = Math.max(80, fbx - cl);
      const k = Math.min(itm.kMax, Math.max(itm.kMin, Math.min((wf - 2 * pad) / Math.max(1e-6, x1 - x0), (itm.H - 2 * pad) / Math.max(1e-6, y1 - y0))));
      itm.view = {k, tx: (cl + fbx) / 2 - (x0 + x1) / 2 * k, ty: itm.H / 2 - (y0 + y1) / 2 * k}; itMapDraw();
    },
    // 12 more made-up wormholes (beside the two Intel reports): 2 to 28 jumps from you (every system next to yours is named here; some past "Map: within"), 4 min to 23.5 h old
    // (three under 30 min, so they pulse with 045's look), two Drifters, three added by hand; distance and age not in step
    seedWh(){
      const st = itWhStore(), g = itGraphGet(), now = Date.now(), D = itm.D, taken = new Set(Object.keys(st.rep).map(Number));
      const JUMPS = [2, 3, 4, 5, 6, 8, 10, 12, 15, 18, 22, 28], MIN = [95, 4, 960, 300, 25, 1410, 12, 180, 720, 45, 480, 1200];
      const by = new Map(); for(let i = 0; i < D.length; i++) if(D[i] > 0) (by.get(D[i]) || by.set(D[i], []).get(D[i])).push(i);
      JUMPS.forEach((j, k) => {
        const MKN = (window.__MK && window.__MK.names) || {}, L = (by.get(j) || []).filter(i => !taken.has(g.ids[i]) && !MKN[g.ids[i]]); if(!L.length) return;   // never a named system (reports, sov list)
        const id = g.ids[L[(k * 7) % L.length]]; taken.add(id);
        const nm = 'MKW-' + String(k + 1).padStart(2, '0'), N = it.names;   // a made-up name (the mockup names only the systems near you)
        if(N){ N.byLower.delete(String(N.byId.get(id) || '').toLowerCase()); N.byId.set(id, nm); N.byLower.set(nm.toLowerCase(), id); N.list = [...N.byLower.keys()]; }
        if(window.__MK && window.__MK.names) window.__MK.names[id] = nm;
        st.rep[id] = {id, t: now - MIN[k] * 60000, who: k % 4 === 3 ? '' : 'Mk Scout Alt', drifter: k === 4 || k === 9, src: k % 4 === 3 ? 'you' : 'intel'};
      });
      itWhSave();
    },
    // a made-up sov list from the mockup's own systems (nearest first), before anything reads tvSov
    seedSov(){
      const gr = itGraphGet(), T = itMapTable(), names = window.__MK.names, rows = [];
      const sys = Object.keys(names).map(Number).map(id => [id, gr.at.get(id)]).filter(([id, i]) => i !== undefined && i !== itm.home).sort((a, b) => itm.D[a[1]] - itm.D[b[1]]);
      const UP = [['Major Threat Detection Array 3', 'Exploration Detector 1'], ['Major Threat Detection Array 2'], ['Minor Threat Detection Array 3', 'Tritanium Prospecting Array 2'],
        ['Major Threat Detection Array 1', 'Cynosural Navigation'], ['Exploration Detector 2'], ['Major Threat Detection Array 3'], ['Minor Threat Detection Array 1'], ['Isogen Prospecting Array 1']];
      sys.forEach(([id], k) => { if(k % 9 !== 8) rows.push(`${names[id]} <- ${UP[k % UP.length].join(', ')}`); });
      localStorage.setItem('tvSov', JSON.stringify({v: 1, lists: [{id: 'mk1', kind: '', text: rows.join('\n'), at: Date.now() - 86400e3}], pick: ['Major Threat Detection Array', 'Minor Threat Detection Array', 'Exploration Detector']}));
      sovSt = null; sovIx = null;
    },
    boot(){ apply(); itMapFbarPaint(false); itMapLegend(); boxMake(); }
  };
})();
