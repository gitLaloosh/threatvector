// Wormholes filter prototype (phase 1 of wormhole mapping; research session 2026-11-12, main 1e22ec7 / v2026.11.12.3).
// Adds a sixth map filter; keeps Intel's wormhole reports 24 h in browser storage. Wraps itMapFcol, itMapDimmed, itMapDraw,
// itMapTip, itMapFLegHtml, itMapFLegTitle, itNearTagsHtml, itFeedRowHtml, itMapLegend. In the build the reports are taken where Intel reads a line
// (not by a 1 s scan of it.feed), and the setting is drawn by itRender's settings box (not inserted afterwards).
(() => {
  'use strict';
  const KEY = 'tvWormholes', KEEP = [1, 2, 4, 8, 12, 24, 48], RX = /\b(wh|wormhole|drifter)\b/i;
  const COL = '#a98bd8', DRIFT = '#e4b5ff';   // the new token --wh (and a lighter shade for Drifter holes)
  const blank = () => ({v: 1, rep: {}, gone: {}, keepH: 24});
  const W = window.WHF = {st: null};
  try{ const o = JSON.parse(localStorage.getItem(KEY) || 'null'); W.st = o && o.v === 1 ? Object.assign(blank(), o) : blank(); }catch(e){ W.st = blank(); }
  const save = () => { try{ localStorage.setItem(KEY, JSON.stringify(W.st)); }catch(e){ } };
  const idx = (id) => { const i = itGraphGet().at.get(Number(id)); return i === undefined ? -1 : i; };
  const ago = (t) => itAgo(t);
  // kept reports by map index, newest first; only those inside the keep window
  function kept(){ const cut = Date.now() - W.st.keepH * 3600e3, m = new Map(); for(const r of Object.values(W.st.rep)) if(r.t >= cut){ const i = idx(r.id); if(i >= 0) m.set(i, r); } return m; }
  // ---- take wormhole lines from Intel (a line with "wh", "wormhole" or "drifter" and a system) ----
  function scan(){
    if(typeof it === 'undefined' || !it.feed) return;
    let ch = false;
    for(const e of it.feed){
      if(e.kind === 'kill' || !e.p || !e.p.sys || !e.p.sys[0] || !RX.test(e.raw || '')) continue;
      const id = e.p.sys[0].id, r = W.st.rep[id];
      if((r && r.t >= e.t) || (W.st.gone && W.st.gone[id] >= e.t)) continue;
      W.st.rep[id] = {id, t: e.t, who: e.who, drifter: /drifter/i.test(e.raw), raw: String(e.raw).slice(0, 120)}; ch = true;
    }
    const cut = Date.now() - 48 * 3600e3; for(const k of Object.keys(W.st.rep)) if(W.st.rep[k].t < cut){ delete W.st.rep[k]; ch = true; }
    if(ch){ save(); if(itm.el) itMapRefresh(true); }
  }
  // ---- the filter ----
  IT_MAP_FILTERS.push({k: 'wh', name: 'Wormholes', note: `wormholes reported in Intel, kept ${W.st.keepH} h; the rest dimmed`,
    icon: '<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M9 2.5a6.5 6.5 0 1 1-6.5 6.5"/><path d="M9 5.5a3.5 3.5 0 1 1-3.5 3.5"/><circle cx="9" cy="9" r="1" fill="currentColor"/></svg>'});
  const _fcol = itMapFcol;
  itMapFcol = function(i){ if(itm.filter !== 'wh') return _fcol(i); const r = W.k.get(i); return r ? (r.drifter ? DRIFT : COL) : IT_MAP_NONE; };
  const _dim = itMapDimmed;
  itMapDimmed = function(i){ if(itm.filter !== 'wh') return _dim(i); return i !== itm.home && !W.k.has(i); };
  W.k = kept(); W.count = () => kept().size;
  // live: inside "forget reports after" and "Map: within", as other reports
  function live(){ const keep = Date.now() - it.set.forget * 60000, m = new Map(); for(const [i, r] of kept()) if(r.t >= keep && itm.D && itm.D[i] >= 0 && itm.D[i] <= itm.reach) m.set(i, r); return m; }
  W.live = live;
  const _leg = itMapFLegHtml;
  itMapFLegHtml = function(){ return itm.filter === 'wh' ? `<b>Wormholes</b> ${itMapSwHtml([COL])} reported ${itMapSwHtml([DRIFT])} Drifter · last ${W.st.keepH} h · dim: none` : _leg(); };
  const _mleg = itMapLegend;
  itMapLegend = function(){ _mleg(); const L = itm.el && itm.el.querySelector('.it-map-leg'); if(L && !L.querySelector('.whf-lg')) L.insertAdjacentHTML('beforeend', `<span class="whf-lg"><i class="ring" style="width:12px;height:12px;border-color:${COL}"></i>wormhole reported (WH)</span>`); };
  const _legT = itMapFLegTitle;
  itMapFLegTitle = function(){ return itm.filter === 'wh' ? `Systems where Intel reported a wormhole (“wh”, “wormhole” or “drifter”) in the last ${W.st.keepH} h, anywhere on the map; the rest dimmed` : _legT(); };
  // the map's own drawing leaves systems past "Map: within" faint; with this filter a kept report is bright anywhere, so it's drawn
  // again on top, with WH / DRIFTER and its age on the left (the page writes names on the right)
  const _draw = itMapDraw;
  itMapDraw = function(){
    W.k = kept(); _draw();
    try{
      const c = itm.cv.getContext('2d'), dpr = window.devicePixelRatio || 1, font = getComputedStyle(document.body).fontFamily;
      c.setTransform(dpr, 0, 0, dpr, 0, 0); c.globalAlpha = 1;
      const X = (i) => itm.Q[2 * i], Y = (i) => itm.Q[2 * i + 1];
      if(itm.filter === 'wh') for(const [i, r] of W.k){
        const x = X(i), y = Y(i), col = r.drifter ? DRIFT : COL; if(x < -40 || y < -40 || x > itm.W + 40 || y > itm.H + 40) continue;
        c.fillStyle = col; c.beginPath(); c.arc(x, y, 3.2, 0, 6.283); c.fill();
        c.strokeStyle = col; c.lineWidth = 1.6; c.beginPath(); c.arc(x, y, 8, 0, 6.283); c.stroke();
        const t = `${r.drifter ? 'DRIFTER' : 'WH'} · ${ago(r.t)}`; c.font = `700 10px ${font}`;
        const w = c.measureText(t).width; c.fillStyle = 'rgba(12,16,20,.75)'; c.fillRect(x - 13 - w, y - 7, w + 4, 13); c.fillStyle = col; c.fillText(t, x - 11 - w, y + 3);
      }
      // the owner, 2026-11-12: on the other filters a wormhole report shows like any Intel report (inside "Map: within", gone after
      // "forget reports after"). Today a wormhole line with no pilots is an info line (kind 'info') that never reaches the map, so it's
      // drawn here: a wormhole ring and "WH · age" on the left.
      if(itm.filter !== 'wh') for(const [i, r] of live()){
        const x = X(i), y = Y(i), col = r.drifter ? DRIFT : COL; if(x < -40 || y < -40 || x > itm.W + 40 || y > itm.H + 40) continue;
        c.strokeStyle = col; c.lineWidth = 2; c.beginPath(); c.arc(x, y, 9, 0, 6.283); c.stroke(); c.beginPath(); c.arc(x, y, 4.5, 0, 6.283); c.stroke();
        const t = `${r.drifter ? 'DRIFTER' : 'WH'} · ${ago(r.t)}`; c.font = `700 10px ${font}`;
        const w = c.measureText(t).width; c.fillStyle = 'rgba(12,16,20,.75)'; c.fillRect(x - 14 - w, y - 7, w + 4, 13); c.fillStyle = col; c.fillText(t, x - 12 - w, y + 3);
      }
    }catch(e){ }
  };
  // live (inside "forget reports after") wormhole-only reports: with the proposal on, kept off the hostile rings

  const _tip = itMapTip;
  itMapTip = function(i, x, y){
    _tip(i, x, y);
    const r = i >= 0 && W.k.get(i); if(!r || !itm.tip || itm.tip.hidden) return;
    if(r.t >= Date.now() - it.set.forget * 60000) itm.tip.querySelectorAll('.d').forEach(d => { if(/nothing reported in the last/.test(d.textContent)){ const br = d.previousSibling; if(br && br.nodeName === 'BR') br.remove(); d.remove(); } });
    if(itm.filter === 'wh') itm.tip.querySelectorAll('.d').forEach(d => { if(/reports aren.t shown here/.test(d.textContent)){ const br = d.previousSibling; if(br && br.nodeName === 'BR') br.remove(); d.remove(); } });   // the filter shows this one wherever it is
    itm.tip.insertAdjacentHTML('beforeend', `<br><span style="color:${r.drifter ? DRIFT : COL}">${r.drifter ? 'Drifter wormhole' : 'Wormhole'}</span> <span class="d">· reported by ${escapeHtml(r.who)}, ${escapeHtml(ago(r.t))} ago</span>`);
  };
  // the owner, 2026-11-12: "add a wormhole badge to intel as well." → a Wormhole / Drifter WH badge (one tag style) in Near You and on
  // Feed rows, for as long as the report is shown there (Near You: "forget reports after"; a Feed row: as long as the row stays)
  const badge = (r) => `<span class="it-gtag whf${r.drifter ? ' dr' : ''}" title="${escapeHtml(`${r.drifter ? 'A Drifter wormhole' : 'A wormhole'}: reported by ${r.who}, ${itAgo(r.t)} ago. Kept ${W.st.keepH} h on the map's Wormholes filter`)}">${r.drifter ? 'Drifter WH' : 'Wormhole'}</span>`;
  const _tags = itNearTagsHtml;
  itNearTagsHtml = function(st, now = Date.now()){
    const h = _tags(st, now), r = W.st.rep[st.sys];
    return r && r.t >= now - it.set.forget * 60000 && st.kind !== 'clear' ? badge(r) + h : h;
  };
  const _frow = itFeedRowHtml;
  itFeedRowHtml = function(e){
    const h = _frow(e);
    if(e.kind === 'kill' || !e.p || !e.p.sys || !e.p.sys[0] || !RX.test(e.raw || '')) return h;
    return h.replace('<span class="ftg">', '<span class="ftg">' + badge({drifter: /drifter/i.test(e.raw), who: e.who, t: e.t}));
  };
  // ---- the list (the owner, 2026-11-12): hovering the Wormholes button shows a list button to its right (it also stays while the
  // filter is on, since a phone has no hover); the panel adds a wormhole by hand (kept from the time it's added, for the setting's
  // hours) or removes one that has collapsed. Closed by × (the shared x-close), Esc or a press outside; focus back on the list button.
  const LIST_ICON = '<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M6.5 4.5h9M6.5 9h9M6.5 13.5h9"/><circle cx="3" cy="4.5" r=".9" fill="currentColor"/><circle cx="3" cy="9" r=".9" fill="currentColor"/><circle cx="3" cy="13.5" r=".9" fill="currentColor"/></svg>';
  const _fbtns = itMapFbtnsHtml;
  itMapFbtnsHtml = function(){ return _fbtns() + `<button type="button" class="whf-lb" data-whf-list aria-haspopup="dialog" aria-expanded="false" aria-label="Wormhole list" title="Wormhole list: add or remove">${LIST_ICON}</button>`; };
  W.gone = W.st.gone || (W.st.gone = {});
  let panel = null, out = null;
  function rowsHtml(){
    const cut = Date.now() - W.st.keepH * 3600e3, list = Object.values(W.st.rep).filter(r => r.t >= cut).sort((a, b) => b.t - a.t), my = itMySys();
    if(!list.length) return '<div class="whf-none">No wormholes kept. Intel lines with “wh”, “wormhole” or “drifter” and a system land here, or add one above.</div>';
    return list.map(r => { const j = my ? itJumps(my, r.id) : null, left = Math.max(0, Math.ceil((r.t + W.st.keepH * 3600e3 - Date.now()) / 3600e3));
      return `<div class="whf-r"><span class="whf-j">${j == null ? '–' : j === 0 ? 'here' : j + ' j'}</span><span class="whf-s">${escapeHtml(itSysName(r.id))}</span>`
        + `<span class="it-gtag whf${r.drifter ? ' dr' : ''}">${r.drifter ? 'Drifter WH' : 'Wormhole'}</span>`
        + `<span class="whf-by">${r.src === 'you' ? 'added by you' : 'reported by ' + escapeHtml(r.who)} · ${escapeHtml(itAgo(r.t))} ago · gone in ${left} h</span>`
        + `<button type="button" data-whf-rm="${r.id}" aria-label="Remove ${escapeHtml(itSysName(r.id))}">Remove</button></div>`; }).join('');
  }
  function paintList(){ if(panel && !panel.hidden){ panel.querySelector('.whf-rows').innerHTML = rowsHtml(); panel.querySelector('.whf-keep').textContent = `kept ${W.st.keepH} h, in this browser only`; } }
  function closeList(back = true){
    if(!panel || panel.hidden) return; panel.hidden = true;
    document.querySelectorAll('[data-whf-list]').forEach(b => b.setAttribute('aria-expanded', 'false'));
    if(out){ document.removeEventListener('pointerdown', out, true); document.removeEventListener('keydown', out.k, true); out = null; }
    if(back){ const b = document.querySelector('[data-whf-list]'), cur = document.querySelector('.it-map-fcur'); (b && b.offsetParent ? b : cur || b) && (b && b.offsetParent ? b : cur || b).focus(); }   // the list button, or on a phone the filter button
  }
  function openList(btn){
    const host = btn.closest('.it-map-fb').parentElement;
    if(btn.closest('.it-map-fb').classList.contains('open')) itMapFbarOpen(false);   // a phone: the filter row closes as the list opens
    if(!panel){
      panel = document.createElement('div'); panel.className = 'whf-panel'; panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-label', 'Wormhole list'); panel.hidden = true;
      panel.innerHTML = `<div class="whf-h"><h4>Wormholes</h4><span class="whf-keep"></span><button type="button" class="x-close" aria-label="Close" title="Close (Esc)">×</button></div>
        <form class="whf-add" autocomplete="off"><input type="text" name="sys" placeholder="System, e.g. Tama" aria-label="System with a wormhole" maxlength="40" spellcheck="false">
        <label><input type="checkbox" name="dr"> Drifter</label><button type="submit">Add</button></form><div class="whf-msg" role="status"></div><div class="whf-rows"></div>`;
      panel.querySelector('.x-close').addEventListener('click', () => closeList());
      panel.querySelector('.whf-add').addEventListener('submit', (ev) => {
        ev.preventDefault(); const f = ev.target, name = f.sys.value.trim(), id = name && it.names && it.names.byLower.get(name.toLowerCase());
        const msg = panel.querySelector('.whf-msg');
        if(!id || !itGraphGet().at.has(id)){ msg.textContent = name ? `“${name}” isn’t a system on the map (wormhole systems come in a later phase).` : 'Type a system name.'; f.sys.setAttribute('aria-invalid', 'true'); return; }
        f.sys.removeAttribute('aria-invalid');
        W.st.rep[id] = {id, t: Date.now(), who: 'you', src: 'you', drifter: f.dr.checked, raw: ''}; delete W.gone[id]; save();
        msg.textContent = `Added ${itSysName(id)}: kept ${W.st.keepH} h from now.`; f.sys.value = ''; f.dr.checked = false; f.sys.focus();
        W.k = kept(); paintList(); itMapRefresh(true);
      });
      panel.querySelector('.whf-rows').addEventListener('click', (ev) => {
        const b = ev.target.closest('[data-whf-rm]'); if(!b) return; const id = Number(b.dataset.whfRm), r = W.st.rep[id];
        if(r){ W.gone[id] = r.t; delete W.st.rep[id]; save(); }   // a removed one doesn't come back from the same Intel line
        panel.querySelector('.whf-msg').textContent = `Removed ${itSysName(id)}.`; W.k = kept(); paintList(); itMapRefresh(true);
        const next = panel.querySelector('[data-whf-rm]') || panel.querySelector('input[name=sys]'); next.focus();
      });
    }
    if(panel.parentElement !== host) host.appendChild(panel);
    panel.hidden = false; btn.setAttribute('aria-expanded', 'true'); paintList(); panel.querySelector('input[name=sys]').focus();
    out = (e) => { if(!panel.contains(e.target) && !e.target.closest('[data-whf-list]')) closeList(false); };
    out.k = (e) => { if(e.key === 'Escape' && !panel.hidden){ e.stopPropagation(); closeList(); } };
    document.addEventListener('pointerdown', out, true); document.addEventListener('keydown', out.k, true);
  }
  document.addEventListener('click', (ev) => { const b = ev.target.closest('[data-whf-list]'); if(!b) return; ev.stopPropagation(); panel && !panel.hidden ? closeList() : openList(b); }, true);
  W.openList = () => { const b = document.querySelector('[data-whf-list]'); if(b) openList(b); };
  // ---- the setting, beside "forget reports after" ----
  function setting(){
    const f = document.querySelector('select[data-it-set="forget"]'); if(!f || document.querySelector('[data-whf-keep]')) return;
    const l = document.createElement('label'); l.innerHTML = `keep wormhole reports for <select data-whf-keep>${KEEP.map(h => `<option value="${h}"${h === W.st.keepH ? ' selected' : ''}>${h} h</option>`).join('')}</select>`;
    l.title = 'How long a wormhole Intel mentioned stays on the map’s Wormholes filter (other reports go after “forget reports after”)';
    f.closest('label').after(l);
    l.querySelector('select').addEventListener('change', (ev) => { W.st.keepH = Number(ev.target.value) || 24; IT_MAP_FILTERS.find(x => x.k === 'wh').note = `wormholes reported in Intel, kept ${W.st.keepH} h; the rest dimmed`; save(); itMapRefresh(true); itMapLegend(); });
  }
  setInterval(() => { scan(); setting(); paintList(); }, 1000);
  // ---- MOCKUP bar (not part of the design) ----
  const H = 3600e3, now0 = Date.now(), seed = (id, h, who, drifter, raw) => { if(!W.st.rep[id]) W.st.rep[id] = {id, t: now0 - h * H, who, drifter, raw}; };
  seed(30000782, 0.7, 'Mk Scout Alt', false, '3U-48K wh off the sun');
  seed(30002813, 2.5, 'Mk Gate Watcher', false, 'Tama wh to a C5');
  seed(30004759, 6, 'Mk Scout Alt', true, '1DQ1-A drifter hole at planet 4');
  seed(30002537, 18, 'Mk Gate Watcher', false, 'Amamake wormhole');
  seed(30000142, 30, 'Mk Scout Alt', false, 'Jita wh (older than 24 h: not shown)');
  save();
  const bar = document.createElement('div'); bar.className = 'mkbar';
  bar.innerHTML = `<b>MOCKUP</b><button type="button" data-mk="post">Post “8G-2FP wormhole” in Intel</button>
    <button type="button" data-mk="wh">Wormholes filter</button><button type="button" data-mk="sec">Security filter</button><button type="button" data-mk="list">Open the list</button>`;
  bar.addEventListener('click', (ev) => {
    const b = ev.target.closest('button'); if(!b) return;
    if(b.dataset.mk === 'post') window.__MKintel('Mk Scout Alt', '8G-2FP wormhole');
    if(b.dataset.mk === 'wh') itMapFilterSet('wh');
    if(b.dataset.mk === 'sec') itMapFilterSet('sec');
    if(b.dataset.mk === 'list'){ itMapFilterSet('wh'); W.openList(); }
  });
  const st = document.createElement('style');
  st.textContent = `:root{--wh:${COL};}
    .it-gtag.whf{color:var(--wh); background:color-mix(in srgb, var(--wh) 18%, transparent);} .it-gtag.whf.dr{color:${DRIFT};}

    .it-map-fbtns{position:relative;}
    button.whf-lb{position:absolute; left:100%; top:-1px; margin-left:6px; border:1px solid var(--line) !important; border-radius:6px !important; background:rgba(12,16,20,.92) !important; color:var(--heading) !important;
      visibility:hidden; opacity:0; transition:opacity .15s, visibility 0s .6s;}
    [data-im-f="wh"]:hover + button.whf-lb, [data-im-f="wh"]:focus-visible + button.whf-lb, button.whf-lb:hover, button.whf-lb:focus-visible, button.whf-lb[aria-expanded="true"],
    .it-map-fbtns:has([data-im-f="wh"][aria-pressed="true"]) button.whf-lb{visibility:visible; opacity:1; transition-delay:0s;}
    .whf-panel{position:absolute; right:8px; bottom:56px; z-index:5; width:min(400px, calc(100% - 16px)); max-height:min(420px, calc(100% - 72px)); overflow:auto; box-sizing:border-box; padding:10px 12px; border:1px solid var(--line); border-radius:6px; background:var(--panel, #12181d); box-shadow:0 8px 24px rgba(0,0,0,.5); font:12px var(--sans); color:var(--text);}
    .whf-panel[hidden]{display:none;}
    .whf-h{display:flex; align-items:center; gap:8px; margin-bottom:8px;} .whf-h h4{margin:0; font:700 14px var(--sans); color:var(--heading);} .whf-keep{color:var(--text-dim);}
    .whf-add{display:flex; gap:6px; align-items:center; flex-wrap:wrap;} .whf-add input[type=text]{flex:1 1 140px; min-width:0;} .whf-add label{display:inline-flex; gap:4px; align-items:center; color:var(--text-dim);}
    .whf-msg{min-height:16px; margin:4px 0; color:var(--text-dim);}
    .whf-r{display:flex; flex-wrap:wrap; align-items:center; gap:4px 8px; padding:6px 0; border-top:1px solid var(--line);}
    .whf-j{min-width:36px; color:var(--text-dim); font-weight:600;} .whf-s{font:700 13px var(--sans); color:var(--heading);} .whf-r .it-gtag{margin-left:0;}
    .whf-by{flex:1 1 100%; order:4; color:var(--text-dim); padding-left:44px;} .whf-r button{margin-left:auto; order:3; min-height:28px; padding:2px 10px;}
    .whf-none{color:var(--text-dim); padding:6px 0;}
    @media (max-width:599px){ .whf-panel{left:8px; right:8px; width:auto; bottom:64px;} .whf-r button, .whf-add button{min-height:44px;} .whf-panel .x-close{width:44px; height:44px;} button.whf-lb{width:44px; height:44px;} }
    .mkbar{position:fixed; left:8px; bottom:8px; z-index:9999; display:flex; flex-wrap:wrap; gap:6px; align-items:center; max-width:calc(100vw - 16px); box-sizing:border-box; padding:6px 8px; border-radius:6px; background:#3a2a10; border:1px solid var(--amber); font:12px var(--sans); color:var(--heading);}
    .mkbar b{color:var(--amber); letter-spacing:.5px;} .mkbar button{font-size:12px; padding:4px 8px; min-height:30px;} .mkseg{display:inline-flex; gap:4px; align-items:center;}
    .mkbar [aria-pressed="true"]{background:var(--amber); color:#111;}
    @media (max-width:599px){ .mkbar button{min-height:36px;} }`;
  document.head.appendChild(st); document.body.appendChild(bar);
})();
