// Intel tab layout mockup (research session 2026-11-14, main 85e20cb). The owner: "i'm wondering if the intel map needs to be more like
// the wormholes map. incorporate near you into a bigger map, place the feed below it. i'd like you to explore this and give me some
// options. if you think it's better to keep near you outside the map, give me options for that too."
// Round 2 (2026-11-14, the owner picked A, a panel button per filter shown on hover, and each sov list on its own): "I like option A with
// filters having their own settings button (show/hide on hover) but show me an option that shows them above the filter's button. for sov
// lists, each list on it's own so it can be replaced or edited separately." Panel button: beside | above. Lists: Edit / Replace / Remove.
// Round 1 layouts: today | a (Near You inside a bigger map) | b (Near You as a strip above a bigger map) | c (bigger map; Near You beside the Feed).
// Filters with panels: end (one button at the bar's end, for the filter that's on) | beside (a button beside each) | press (right-click /
// long-press the filter's own button). A stub "Sov upgrades" filter on MADE-UP data, with two ways of keeping pasted lists (own | merged).
(() => {
  const S = {lay: 'a', fp: 'beside', lists: 'own', look: 'dim', rail: 'right', icon: 'feed', fl: 'left', ck: 'tick', listsOpen: false, nyOpen: false, sovOpen: false, edit: ''};
  const phone = () => matchMedia('(max-width: 599px)').matches;
  window.__MKH = (w, ph) => S.lay === 'today' ? 0 : ph ? (S.lay === 'a' ? Math.round(Math.min(600, Math.max(440, w * 1.45))) : 0) : Math.round(Math.min(720, Math.max(520, w * 0.5)));

  // ---- made-up sov data (not anyone's real upgrades) ----
  const KINDS = [
    {g: 'Ratting', k: 'mtd', n: 'Major Threat Detection Array', lv: true}, {g: 'Ratting', k: 'ntd', n: 'Minor Threat Detection Array', lv: true},
    {g: 'Exploration', k: 'exd', n: 'Exploration Detector'},
    {g: 'Mining', k: 'meg', n: 'Megacyte Prospecting Array'}, {g: 'Mining', k: 'zyd', n: 'Zydrine Prospecting Array'}, {g: 'Mining', k: 'noc', n: 'Nocxium Prospecting Array'},
    {g: 'Mining', k: 'iso', n: 'Isogen Prospecting Array'}, {g: 'Mining', k: 'mex', n: 'Mexallon Prospecting Array'}, {g: 'Mining', k: 'pye', n: 'Pyerite Prospecting Array'},
    {g: 'Other', k: 'esg', n: 'Exotic Stability Generator'},
    {g: 'Navigation', k: 'cyb', n: 'Cyno beacon', from: 'names'},
    {g: 'Navigation', k: 'jb', n: 'Jump bridge', from: 'bridges'}];   // round 6 (the owner: "The bridges paste (041)"): read from the Jump bridges list, no second paste
  const pick = new Set(['mtd', 'cyb']);
  let sov = null;   // system index -> [{k, lv}]
  function sovBuild(){
    if(sov) return sov;
    sov = new Map();
    const T = itMapTable(), g = itGraphGet(), home = itMySys(), hi = g.at.get(home);
    if(hi === undefined) return sov;
    const near = [], seen = new Set([hi]); let fr = [hi];
    for(let d = 0; d < 7 && fr.length; d++){ const nx = []; for(const i of fr) for(const j of g.adj[i]) if(!seen.has(j)){ seen.add(j); nx.push(j); near.push(j); } fr = nx; }
    let r = 7; const rnd = () => (r = (r * 16807) % 2147483647) / 2147483647;   // fixed seed: the same made-up picture every load
    for(const j of near){
      if(!(it.names && it.names.byId.get(g.ids[j]))) continue;   // only systems with a name in this mockup, so Edit can list them
      const x = rnd(), ups = [];
      if(x < 0.55) ups.push({k: 'mtd', lv: 1 + Math.floor(rnd() * 3)});
      if(rnd() < 0.08) ups.push({k: 'ntd', lv: 1 + Math.floor(rnd() * 3)});
      if(rnd() < 0.1) ups.push({k: 'exd', lv: 3});
      if(rnd() < 0.12) ups.push({k: ['meg', 'zyd', 'noc', 'iso', 'mex', 'pye'][Math.floor(rnd() * 6)], lv: 3});
      if(rnd() < 0.05) ups.push({k: 'esg'});
      if(rnd() < 0.3) ups.push({k: 'cyb'});
      if(rnd() < 0.07) ups.push({k: 'jb'});
      if(ups.length) sov.set(j, ups);
    }
    return sov;
  }
  const sovOf = (i) => (sovBuild().get(i) || []);
  const sovHas = (i) => sovOf(i).some(u => pick.has(u.k));

  // ---- the stub filter (placed before Paths to you, so Wormholes is no longer last) ----
  const pi = IT_MAP_FILTERS.findIndex(f => f.k === 'paths');
  IT_MAP_FILTERS.splice(pi, 0, {k: 'sov', name: 'Sov upgrades', note: 'systems with the upgrades you picked bright, the rest dimmed (made-up data in this mockup)',
    icon: '<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M9 2.5l5.5 2.2v4.1c0 3.3-2.3 5.6-5.5 6.7-3.2-1.1-5.5-3.4-5.5-6.7V4.7z"/><path d="M6.5 9l1.8 1.8L11.8 7"/></svg>'});
  const wi = IT_MAP_FILTERS.findIndex(f => f.k === 'wh'), wf = IT_MAP_FILTERS.splice(wi, 1)[0];
  IT_MAP_FILTERS.splice(IT_MAP_FILTERS.findIndex(f => f.k === 'sov'), 0, wf);   // order: … Kills, Wormholes, Sov upgrades, Paths to you
  // round 2b: how sov upgrades look on the map (S.look): dim = bright/dim only; colour = a ring split by upgrade group; marks = short codes
  const GROUPC = {Ratting: ['--amber', '#d99a3c'], Exploration: ['--cyan', '#4fc3d9'], Mining: ['--it-clear', '#3fb950'], Other: ['--wh', '#a98bd8'], Navigation: ['--heading', '#f0f3f6']};
  const CODE = {mtd: 'Maj', ntd: 'Min', exd: 'Expl', meg: 'Mega', zyd: 'Zyd', noc: 'Nocx', iso: 'Iso', mex: 'Mex', pye: 'Pye', esg: 'ESG', cyb: 'Beacon', jb: 'JB'};
  const kindOf = (k) => KINDS.find(x => x.k === k), gOf = (k) => kindOf(k).g;
  const draw0 = itMapDraw, tip0 = itMapTip;
  itMapDraw = function(){
    draw0.apply(this, arguments);
    if(itm.filter !== 'sov' || S.look === 'dim' || !itm.cv) return;
    const c = itm.cv.getContext('2d'), dpr = window.devicePixelRatio || 1, Q = itm.Q, g = itMapGatePx();
    c.save(); c.setTransform(dpr, 0, 0, dpr, 0, 0);
    for(const [i, ups] of sovBuild()){
      const u = ups.filter(x => pick.has(x.k)); if(!u.length) continue;
      const x = Q[2 * i], y = Q[2 * i + 1]; if(x < -20 || y < -20 || x > itm.W + 20 || y > itm.H + 20) continue;
      const gs = [...new Set(u.map(x => gOf(x.k)))], R = g >= 34 ? Math.max(12, Math.min(19, g * 0.25)) : Math.max(5, Math.min(9, g * 0.45));
      if(S.look === 'colour' || g < 18){   // a ring split into one arc per group (like the wormhole ring split by kind); marks fall back to this zoomed out
        c.lineWidth = g >= 34 ? 3 : 2;
        gs.forEach((gr, n) => { const a0 = -Math.PI / 2 + n * 2 * Math.PI / gs.length, a1 = a0 + 2 * Math.PI / gs.length - (gs.length > 1 ? 0.25 : 0);
          c.strokeStyle = itMapCol(...GROUPC[gr]); c.beginPath(); c.arc(x, y, R, a0, a1); c.stroke(); });
      } else {   // marks: short codes beside the system, the level after Maj / Min
        const t = u.map(x => CODE[x.k] + (x.lv && kindOf(x.k).lv ? x.lv : '')).join(' · ');
        c.font = '600 10.5px system-ui, sans-serif'; const w = c.measureText(t).width + 8, bx = x + R + 3, by = y - 8;
        c.fillStyle = 'rgba(12,16,20,.88)'; c.strokeStyle = itMapCol(...GROUPC[gs[0]]); c.lineWidth = 1;
        c.beginPath(); if(c.roundRect) c.roundRect(bx, by, w, 16, 3); else c.rect(bx, by, w, 16); c.fill(); c.stroke();
        c.fillStyle = itMapCol('--heading', '#f0f3f6'); c.fillText(t, bx + 4, by + 12);
      }
    }
    c.restore();
  };
  itMapTip = function(i){
    tip0.apply(this, arguments);
    if(i < 0 || itm.filter !== 'sov' || !itm.tip || itm.tip.hidden) return;
    const ups = sovOf(i), line = document.createElement('div'); line.className = 'mk-tipsov';
    line.textContent = 'Sov upgrades: ' + (ups.length ? ups.map(u => kindOf(u.k).n + (u.lv && kindOf(u.k).lv ? ' ' + u.lv : '')).join(', ') : 'none in your lists');
    itm.tip.appendChild(line);
  };
  const dim0 = itMapDimmed, leg0 = itMapFLegHtml, tit0 = itMapFLegTitle, set0 = itMapFilterSet;
  itMapDimmed = function(i){ if(itm.filter === 'sov') return i !== itm.home && !sovHas(i); return dim0(i); };
  itMapFLegHtml = function(){ if(itm.filter !== 'sov') return leg0(); const gs = [...new Set([...pick].map(gOf))];
    return '<b>Sov upgrades</b> ' + (S.look === 'colour' ? gs.map(g => `<span style="color:${itMapCol(...GROUPC[g])}">◯</span> ${g}`).join(' · ') + ' · dim: none' : S.look === 'marks' ? 'codes beside each system (Maj / Min with their level) · zoomed out: coloured rings · dim: none' : `bright: ${pick.size ? [...pick].map(k => kindOf(k).n).join(', ') : 'none picked'} · dim: none`) + ' · hover a system for its upgrades'; };
  itMapFLegTitle = function(){ return itm.filter === 'sov' ? 'Systems with an upgrade you picked in the Sov upgrades panel bright, the rest dimmed (made-up data)' : tit0(); };
  itMapFilterSet = function(k){ set0(k); fpPaint(); if(k !== 'sov') sovPanel(false); };

  // ---- the Sov upgrades panel ----
  let sp = null, pasteOpen = false, pasteMsg = '', listMsg = '';
  const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'})[c]);
  function counts(){ const c = {}; for(const ups of sovBuild().values()) for(const u of ups) c[u.k] = (c[u.k] || 0) + 1; return c; }
  function sovHtml(){
    const c = counts(), groups = [...new Set(KINDS.map(k => k.g))];
    const grp = (g) => `<div class="mk-sg"><b>${g}</b>${KINDS.filter(k => k.g === g).map(k => `<label class="mk-sk"${k.lv ? ' title="Levels 1–3: a system\'s level shows when you hover it on the map"' : k.from === 'bridges' ? ' title="Systems with a bridge in your Jump bridges list (the Jump bridges feature). Change it there; nothing to paste here."' : ''}><input type="checkbox" data-mk-k="${k.k}"${pick.has(k.k) ? ' checked' : ''}> ${esc(k.n)}${k.from === 'bridges' ? ' <span class="mk-lv">from Jump bridges</span>' : ''} <span class="mk-n">${c[k.k] || 0}</span></label>`).join('')}</div>`;
    const show = `<div class="mk-col">${groups.filter(g => g !== 'Mining').map(grp).join('')}</div><div class="mk-col">${grp('Mining')}</div>`;
    const up = Object.entries(c).filter(([k]) => k !== 'cyb' && k !== 'jb').reduce((a, [, n]) => a + n, 0), sysUp = [...sovBuild().values()].filter(u => u.some(x => x.k !== 'cyb' && x.k !== 'jb')).length, sysCy = c.cyb || 0;
    const row = (id, name, n, form) => `<div class="mk-lr"><div title="${form}"><b>${name}</b> <span>· ${n} systems · pasted today</span></div>`
      + `<button type="button" data-mk-ed="${id}" aria-expanded="${S.edit === id}">Edit</button><button type="button" data-mk-rp="${id}">Replace</button><button type="button" data-mk-rm="${id}">Remove</button></div>`
      + (S.edit === id ? `<div class="mk-pb"><textarea rows="6" data-mk-et>${esc(listText(id))}</textarea><div class="mk-pr"><span>Edit the lines, then Save. Removing a line removes that system from this list only.</span><span><button type="button" data-mk-ec>Cancel</button> <button type="button" class="mys-primary" data-mk-es>Save</button></span></div><div class="mk-pm">${esc(pasteMsg)}</div></div>` : '');
    const lists = row('up', 'Upgrades', sysUp, 'Pasted as &quot;System &lt;- Upgrade Level, …&quot; lines') + row('cy', 'Cyno beacons', sysCy, 'Pasted as system names only, kind: Cyno beacons') + (listMsg ? `<div class="mk-pm">${esc(listMsg)}</div>` : '');
    const paste = pasteOpen ? `<div class="mk-pb"><textarea rows="4" placeholder="Paste a list: one system per line, as &quot;System &lt;- Upgrade Level, Upgrade&quot; or a system name alone" data-mk-ta></textarea>`
      + `<div class="mk-pr"><span data-mk-kind hidden>These lines are system names only: they are <select data-mk-sel><option>Cyno beacons</option><option>Cyno jammers</option><option>Other (name it)</option></select></span>`
      + `<button type="button" class="mys-primary" data-mk-add>Add as a new list</button></div><div class="mk-pm">${esc(pasteMsg)}</div></div>` : '';
    return `<div class="it-whp-h"><h4>Sov upgrades</h4><span class="it-whp-keep">made-up data</span><button type="button" class="x-close" data-mk-sx aria-label="Close" title="Close (Esc)">×</button></div>`
      + `<div class="mk-sec">Show on the map</div><div class="mk-sgs">${show}</div>`
      + `<button type="button" class="it-whp-xb mk-lx" data-mk-lists aria-expanded="${S.listsOpen}" title="Each list is kept on its own until you edit, replace or remove it">Lists (2) ${IT_CHEV}</button>`
      + (S.listsOpen ? `<div class="mk-lists">${lists}<button type="button" class="it-whp-xb" data-mk-paste aria-expanded="${pasteOpen}">Paste a list ${IT_CHEV}</button>${paste}</div>` : '');
  }
  function listText(id){
    const g = itGraphGet(), out = [];
    for(const [j, ups] of sovBuild()){
      const nm = itSysName(g.ids[j]);
      if(id === 'cy'){ if(ups.some(u => u.k === 'cyb')) out.push(nm); continue; }
      const u = ups.filter(x => x.k !== 'cyb' && x.k !== 'jb'); if(!u.length) continue;
      out.push(`${nm} <- ${u.map(x => KINDS.find(k => k.k === x.k).n + (x.lv ? ' ' + x.lv : '')).join(', ')}`);
    }
    return out.join('\n');
  }
  function sovPanel(open){
    if(!open){ if(sp) sp.hidden = true; S.sovOpen = false; fpPaint(); return; }
    if(typeof itWhListShown === 'function' && itWhListShown()) itWhListOpen(false, false);
    if(!sp){
      sp = document.createElement('div'); sp.className = 'it-whp mk-sp'; sp.setAttribute('role', 'dialog'); sp.setAttribute('aria-label', 'Sov upgrades');
      sp.addEventListener('click', (e) => {
        if(e.target.closest('[data-mk-sx]')){ sovPanel(false); return; }
        if(e.target.closest('[data-mk-lists]')){ S.listsOpen = !S.listsOpen; if(!S.listsOpen){ S.edit = ''; pasteOpen = false; } sp.innerHTML = sovHtml(); place(); return; }
        if(e.target.closest('[data-mk-paste]')){ pasteOpen = !pasteOpen; pasteMsg = ''; sp.innerHTML = sovHtml(); return; }
        listMsg = ''; const ed = e.target.closest('[data-mk-ed]'); if(ed){ S.edit = S.edit === ed.dataset.mkEd ? '' : ed.dataset.mkEd; pasteMsg = ''; sp.innerHTML = sovHtml(); const t = sp.querySelector('[data-mk-et]'); if(t) t.focus(); return; }
        if(e.target.closest('[data-mk-ec]')){ S.edit = ''; pasteMsg = ''; sp.innerHTML = sovHtml(); return; }
        if(e.target.closest('[data-mk-es]')){ pasteMsg = 'Mockup: nothing is saved. The real panel re-reads the lines and marks each ✓ / ⚠ / ✗.'; sp.innerHTML = sovHtml(); return; }
        if(e.target.closest('[data-mk-rp]')){ S.edit = ''; pasteOpen = true; pasteMsg = 'Replace: paste the new list here; it takes the old one\'s place (its kind kept).'; sp.innerHTML = sovHtml(); return; }
        const rm = e.target.closest('[data-mk-rm]'); if(rm){ listMsg = `Mockup: nothing removed. The real button removes the ${rm.dataset.mkRm === 'cy' ? 'Cyno beacons' : 'Upgrades'} list only, with Undo for a few seconds.`; sp.innerHTML = sovHtml(); return; }
        if(e.target.closest('[data-mk-add]')){ pasteMsg = 'Mockup: nothing is added. The real panel reads the lines, checks each system and shows ✓ / ⚠ / ✗ per line.'; sp.innerHTML = sovHtml(); return; }
      });
      sp.addEventListener('change', (e) => { const k = e.target.dataset.mkK; if(!k) return; if(e.target.checked) pick.add(k); else pick.delete(k); itMapDraw(); itMapLegend(); });
      sp.addEventListener('input', (e) => { if(!e.target.matches('[data-mk-ta]')) return; const v = e.target.value.trim(), bare = v && v.split(/\n/).every(l => !/<-/.test(l)); sp.querySelector('[data-mk-kind]').hidden = !bare; });
    }
    if(sp.parentNode !== itm.box) itm.box.appendChild(sp);
    if(phone()) S.nyOpen = false;   // a phone has room for one: the filter's panel shuts Near You
    sp.innerHTML = sovHtml(); sp.hidden = false; S.sovOpen = true; fpPaint(); place();
  }
  document.addEventListener('keydown', (e) => { if(e.key === 'Escape' && S.sovOpen){ sovPanel(false); } }, true);
  document.addEventListener('pointerdown', (e) => { if(S.sovOpen && sp && !sp.contains(e.target) && !e.target.closest('[data-mk-fp],[data-mk-sb],[data-im-f="sov"]')) sovPanel(false); }, true);

  // ---- filters with panels: one button at the end / beside each / right-click ----
  const PANEL = {wh: 'Wormhole list', sov: 'Sov upgrades: what to show, your lists'};
  const GEAR = '<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M3 5h12M3 9h12M3 13h7"/><circle cx="13.5" cy="13" r="1.6" fill="currentColor"/></svg>';
  function openFor(k){ if(k === 'sov'){ if(itm.filter !== 'sov') itMapFilterSet('sov'); sovPanel(!S.sovOpen); } }
  function fpMount(){
    const bar = itm.el && itm.el.querySelector('.it-map-fbtns'); if(!bar || bar.querySelector('.mk-fw')) return;
    const sb = document.createElement('button'); sb.type = 'button'; sb.className = 'mk-sb'; sb.dataset.mkSb = ''; sb.innerHTML = GEAR; sb.title = PANEL.sov; sb.setAttribute('aria-label', PANEL.sov);
    sb.setAttribute('aria-haspopup', 'dialog'); sb.addEventListener('click', () => openFor('sov'));
    const wl = bar.querySelector('button.it-whl');
    for(const [k, pb] of [['wh', wl], ['sov', sb]]){   // each filter with a panel and its own panel button, in one box
      const f = bar.querySelector(`[data-im-f="${k}"]`), w = document.createElement('span'); w.className = 'mk-fw';
      f.before(w); w.appendChild(f); w.appendChild(pb); pb.classList.add('mk-pbtn');
    }
    fpPaint();
  }
  function fpPaint(){
    const sb = itm.el && itm.el.querySelector('[data-mk-sb]'); if(sb) sb.setAttribute('aria-expanded', String(S.sovOpen));
  }

  // ---- layouts ----
  // round 3 (the owner, 2026-11-15): Near You's button in the map's own button style (no amber), an icon, sized like the map's
  // other buttons; collapsed, only the button shows (the map first); open, the panel sits beside a rail of buttons that stays
  // clickable (Near You now, Routes later), on the right or the left (S.rail); icon options (S.icon).
  const ICONS = {
    radar: '<circle cx="9" cy="9" r="7"/><circle cx="9" cy="9" r="3.6"/><path d="M9 9l4.6-4.6"/><circle cx="12.2" cy="11.8" r="1.1" fill="currentColor" stroke="none"/>',
    pin: '<path d="M6 15.5s-3.6-3.9-3.6-6.6a3.6 3.6 0 017.2 0c0 2.7-3.6 6.6-3.6 6.6z"/><circle cx="6" cy="8.9" r="1.2" fill="currentColor" stroke="none"/><path d="M11.5 5h4.5M11.5 9h4.5M11.5 13h3"/>',
    rings: '<circle cx="9" cy="9" r="1.8" fill="currentColor" stroke="none"/><circle cx="9" cy="9" r="4.6" stroke-dasharray="2 2"/><circle cx="9" cy="9" r="7.6"/><circle cx="12.3" cy="5.8" r="1.2" fill="currentColor" stroke="none"/><circle cx="3.2" cy="12.6" r="1.2" fill="currentColor" stroke="none"/>',
    blip: '<circle cx="9" cy="9" r="7.4"/><circle cx="9" cy="9" r="3.4"/><path d="M9 .8v2.6M9 14.6v2.6M.8 9h2.6M14.6 9h2.6"/><circle cx="11.6" cy="6.4" r="1.5" fill="currentColor" stroke="none"/>',
    // round 6 (the owner: "i need more options. one of those options should be an exclamation point or something that infers "alert"")
    alert: '<path d="M9 2.3l7 12.5H2z"/><path d="M9 7.2v3.6"/><circle cx="9" cy="13" r=".95" fill="currentColor" stroke="none"/>',
    bang: '<circle cx="9" cy="9" r="7.2"/><path d="M9 5v4.8"/><circle cx="9" cy="12.6" r=".95" fill="currentColor" stroke="none"/>',
    pinbang: '<path d="M9 16.6s-5.2-5.3-5.2-9.1a5.2 5.2 0 0110.4 0c0 3.8-5.2 9.1-5.2 9.1z"/><path d="M9 4.6v3.3"/><circle cx="9" cy="10.1" r=".95" fill="currentColor" stroke="none"/>',
    bell: '<path d="M4.6 12.8V8.6a4.4 4.4 0 018.8 0v4.2l1.4 1.6H3.2z"/><path d="M7.4 16.2a1.7 1.7 0 003.2 0"/>',
    signal: '<circle cx="9" cy="9" r="1.6" fill="currentColor" stroke="none"/><path d="M6 6a4.3 4.3 0 000 6M12 6a4.3 4.3 0 010 6M3.6 3.6a7.6 7.6 0 000 10.8M14.4 3.6a7.6 7.6 0 010 10.8"/>',
    feed: '<rect x="2.6" y="12.2" width="3.2" height="3.2" rx=".6" fill="currentColor" stroke="none"/><path d="M2.8 8.6a6.6 6.6 0 016.6 6.6M2.8 4.6a10.6 10.6 0 0110.6 10.6M2.8 .9a14.3 14.3 0 0114.3 14.3" stroke-width="1.7"/>',   // the owner's picture (2026-11-15): a feed icon, drawn here
    eye: '<path d="M1.6 9s2.8-5 7.4-5 7.4 5 7.4 5-2.8 5-7.4 5-7.4-5-7.4-5z"/><circle cx="9" cy="9" r="2.3"/>'};
  const ICONN = {radar: 'Radar', pin: 'Pin + list', rings: 'Rings', blip: 'Blip', alert: 'Warning !', bang: 'Circle !', pinbang: 'Pin !', bell: 'Bell', signal: 'Signal', eye: 'Eye', feed: 'Feed'};
  const ROUTE_ICON = '<circle cx="4" cy="14" r="1.8"/><circle cx="14" cy="4" r="1.8"/><path d="M5.6 13.2c4-1 1.5-6.4 6.8-8.4"/>';
  const svg = (p) => `<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">${p}</svg>`;
  function nyMount(){
    const box = itm.box; if(!box) return;
    let r = box.querySelector('.mk-rail');
    if(!r){
      r = document.createElement('div'); r.className = 'mk-rail'; r.setAttribute('role', 'toolbar'); r.setAttribute('aria-label', 'Map panels');
      r.innerHTML = `<button type="button" data-mk-ny></button><button type="button" data-mk-rt disabled title="Routes: a list of your routes (planned in its own session)" aria-label="Routes (planned)">${svg(ROUTE_ICON)}</button>`;
      box.appendChild(r);
      r.querySelector('[data-mk-ny]').addEventListener('click', () => { S.nyOpen = !S.nyOpen; if(S.nyOpen && phone() && flLeft() && itm.el.querySelector('.it-map-fb.open')) itMapFbarOpen(false); place(); });
    }
    box.dataset.mkRail = S.rail;
    const b = r.querySelector('[data-mk-ny]'), rows = [...document.querySelectorAll('#intelPanel #itNearList .it-nb')], n = rows.length, al = rows.some(x => x.classList.contains('alert'));
    const html = svg(ICONS[S.icon]) + (n ? `<span class="mk-badge${al ? ' al' : ''}">${n}</span>` : '');
    if(b.innerHTML !== html) b.innerHTML = html;
    const t = `Near You: ${n} system${n === 1 ? '' : 's'}${al ? ', some in your alert range' : ''} (press to ${S.nyOpen ? 'hide' : 'show'} the list)`;
    if(b.title !== t){ b.title = t; b.setAttribute('aria-label', t); }
    b.setAttribute('aria-pressed', String(S.nyOpen));
  }
  // round 6b: the Intel example (setup screen, five numbered notes) in the new layout: the map picture across, Near You's list open
  // beside the Feed button at its top right (as with the list open); on a phone the list under the picture (a tour, not the live map)
  function exPlace(){
    const t = document.querySelector('#intelPanel .itx .itx-top'); if(!t) return;
    const m = t.querySelector('.itx-map'), col = t.querySelector('.it-nearcol'); if(!m || !col) return;
    if(S.lay !== 'a'){ col.style.cssText = ''; const r0 = m.querySelector('.mk-exrail'); if(r0) r0.remove(); return; }
    let r = m.querySelector('.mk-exrail');
    if(!r){ r = document.createElement('div'); r.className = 'mk-rail mk-exrail'; r.setAttribute('aria-hidden', 'true'); m.appendChild(r); }
    const n = t.querySelectorAll('.itx-near .it-nb').length, al = !!t.querySelector('.itx-near .it-nb.alert');
    const html = `<button type="button" tabindex="-1" aria-pressed="true">${svg(ICONS[S.icon])}${n ? `<span class="mk-badge${al ? ' al' : ''}">${n}</span>` : ''}</button>`;
    if(r.innerHTML !== html) r.innerHTML = html;
    if(phone()){ col.style.cssText = ''; return; }
    const tr = t.getBoundingClientRect(), mr = m.getBoundingClientRect(), rr = r.getBoundingClientRect();
    col.style.cssText = `top:${Math.round(rr.top - tr.top)}px; left:${Math.round(rr.left - tr.left - 6 - 320)}px; width:320px; height:${Math.round(mr.bottom - 8 - rr.top)}px;`;
    const f = document.querySelector('#intelPanel .itx'); if(f && typeof itExPlace === 'function') itExPlace(f);   // the markers follow
  }
  // a phone's example draws the map picture too (today it shows the list only, note 3 saying to switch to Map), marker 3 on it
  const exFill0 = itExFill, exPlace0 = itExPlace;
  itExFill = function(f){
    exFill0.apply(this, arguments);
    if(S.lay !== 'a' || !itExPhone()) return;
    const img = f.querySelector('.itx-map img'), col = f.querySelector('.itx-map'), w = col ? Math.round(col.clientWidth) : 0, url = w > 0 ? itExMapPic(w) : null;
    if(img && url && img.getAttribute('src') !== url){ img.addEventListener('load', () => itExPlace(f), {once: true}); img.src = url; }
  };
  itExPlace = function(f){
    exPlace0.apply(this, arguments);
    if(S.lay !== 'a' || !itExPhone()) return;
    const W = f.querySelector('.itx-wrap'), img = f.querySelector('.itx-map img[src]'), m = f.querySelector('[data-itx-mk="3"]'); if(!W || !img || !m) return;
    const R = W.getBoundingClientRect(), r = img.getBoundingClientRect(); m.style.left = `${Math.round(r.left - R.left + 14)}px`; m.style.top = `${Math.round(r.top - R.top + 14)}px`; m.hidden = false;
  };
  const exNotes0 = itExNotesHtml;
  itExNotesHtml = function(phone){ return exNotes0.call(this, S.lay === 'a' ? false : phone); };   // the phone's note 3 ("switch Near You to Map") no longer applies: the map is always there
  let raf = 0;
  function place(){
    const top = document.querySelector('#intelPanel .it-top:not(.itx-top)'), col = top && top.querySelector('.it-nearcol'), box = itm.box;
    document.body.classList.toggle('mk-nyc', !S.nyOpen);
    exPlace();
    if(!col) return;
    if(S.lay !== 'a' || !box || !box.isConnected){ col.style.cssText = ''; flPlace(); return; }
    if(phone() && flLeft() && S.nyOpen && box.querySelector('.it-map-fb.open')) S.nyOpen = false;   // a phone: the filter column was just opened, so Near You shuts (one at a time)
    document.body.classList.toggle('mk-nyc', !S.nyOpen);
    nyMount();
    { // the rail starts under the map's top-row controls on its side: the zoom buttons (right) or the search box (left); on a phone the search box runs under the zoom row on both sides
      const rl = box.querySelector('.mk-rail'), bt = box.getBoundingClientRect().top, z = box.querySelector('.it-map-zoom'), q = box.querySelector('.it-rp-search');
      const zb = z && z.offsetParent ? z.getBoundingClientRect().bottom : bt + 38, qb = q && q.offsetParent ? q.getBoundingClientRect().bottom : bt + 40;
      const under = phone() ? Math.max(zb, qb) : S.rail === 'right' ? zb : qb;
      rl.style.top = `${Math.round(under - bt + 8)}px`;
      box.style.setProperty('--mk-flt', `${Math.round((phone() ? Math.max(zb, qb) : qb) - bt + 8)}px`);   // filters down the left: under the search box
    }
    const tr = top.getBoundingClientRect(), br = box.getBoundingClientRect(), r = box.querySelector('.mk-rail').getBoundingClientRect(), gap = 6;
    const fb = box.querySelector('.it-map-fb'), fr = fb && fb.getBoundingClientRect(), floor = phone() && !flLeft() && fr && fr.height ? fr.top - 8 : br.bottom - 8;   // phone: stop above the filter bar
    const w = phone() ? Math.round(br.width - 16 - r.width - gap) : 320, h = Math.round(floor - r.top);
    const left = S.rail === 'right' ? r.left - gap - w : r.right + gap;
    col.style.cssText = `top:${Math.round(r.top - tr.top)}px; left:${Math.round(left - tr.left)}px; width:${w}px; height:${h}px;`;
    flPlace(); panelsPlace();
  }
  // round 4 (the owner: "sure"): a filter's panel opens above the filter bar, inside the map and clear of the Near You list and the
  // buttons beside it, so the list stays in view while you change what the map shows; a phone shows one at a time (above, sovPanel)
  function panelsPlace(){
    const box = itm.box; if(!box || S.lay !== 'a' || phone()) return;
    if(flLeft()) return panelsLeft(box);
    const br = box.getBoundingClientRect(), rl = box.querySelector('.mk-rail'), col = document.querySelector('#intelPanel .it-top:not(.itx-top) .it-nearcol');
    const rr = rl && rl.getBoundingClientRect(), cr = S.nyOpen && col ? col.getBoundingClientRect() : null;
    let L = br.left + 8, R = br.right - 8;
    if(rr && S.rail === 'right') R = Math.min(R, (cr ? cr.left : rr.left) - 8);
    if(rr && S.rail === 'left') L = Math.max(L, (cr ? cr.right : rr.right) + 8);
    const fb = box.querySelector('.it-map-fbtns'), fn = box.querySelector('.it-map-fn'), fr0 = fb && fb.getBoundingClientRect(), nr = fn && fn.getBoundingClientRect();
    const fr = fr0 && fr0.height ? {top: Math.min(fr0.top, nr && nr.height ? nr.top : fr0.top), left: fr0.left, width: fr0.width, height: fr0.height} : null, lift = 0;   // above the filter's name line too (it sits above the bar)
    const bottom = fr ? br.bottom - fr.top + 8 : 64, maxH = Math.max(160, (fr ? fr.top : br.bottom - 56) - br.top - 16);
    for(const el of box.querySelectorAll('.it-whp')){
      if(el.hidden) continue;
      const w = Math.min(el.classList.contains('mk-sp') ? 560 : 340, R - L), mid = fr && fr.width ? fr.left + fr.width / 2 : (L + R) / 2;
      const x = Math.max(L, Math.min(R - w, mid - w / 2));
      el.style.cssText = `left:${Math.round(x - br.left)}px; right:auto; top:auto; bottom:${Math.round(bottom)}px; width:${Math.round(w)}px; max-height:${Math.round(maxH)}px;`;
    }
  }
  // round 5 (the owner, 2026-11-15: "i wonder if we should put filters on the left side and feeds on the right ... with filters on the
  // left, lists and settings would display to their right with the name line moved to the right of that"): the filter bar as a
  // column down the map's left edge, under the search box; a filter's panel button to the right of it; the name line to the right
  // of the panel buttons, beside the filter that is on; a filter's panel opens to the right of the panel buttons, level with its
  // filter, clear of Near You (always on the right in this layout).
  const flLeft = () => S.lay === 'a' && S.fl === 'left';
  const pbW = () => phone() ? 44 : 32;
  function flPlace(){
    const box = itm.box, fb = box && box.querySelector('.it-map-fb'), fn = fb && fb.querySelector('.it-map-fn'); if(!fn) return;
    document.body.classList.toggle('mk-pop', !!box.querySelector('.it-whp:not([hidden])'));
    if(!flLeft()){ fn.style.cssText = ''; return; }
    const bs = fb.querySelector('.it-map-fbtns'), fc = fb.querySelector('.it-map-fcur');
    { // the column wraps into a second one if the map is too short for it (a phone; more filters later)
      const fr0 = fb.getBoundingClientRect(), bb = box.getBoundingClientRect().bottom, one = phone() ? 46 : 34;
      bs.style.setProperty('--mk-flr', String(Math.min(bs.children.length, Math.max(3, Math.floor((bb - 8 - fr0.top - 8) / one)))));   // no empty rows
    }
    const shut = !bs.offsetParent, cur = shut ? fc : bs.querySelector(`[data-im-f="${itm.filter}"]`);   // a phone with the column shut: beside its one button
    const fr = fb.getBoundingClientRect(), sr = shut ? (fc && fc.getBoundingClientRect()) : bs.getBoundingClientRect(), cr = cur && cur.offsetParent ? cur.getBoundingClientRect() : null;
    if(!sr || !cr || !sr.width){ fn.style.cssText = 'display:none;'; return; }
    const rl = box.querySelector('.mk-rail'), col = document.querySelector('#intelPanel .it-top:not(.itx-top) .it-nearcol'), stop = S.nyOpen && col ? col.getBoundingClientRect().left : rl ? rl.getBoundingClientRect().left : box.getBoundingClientRect().right;
    const x = sr.right - fr.left + 6 + (phone() ? 0 : pbW() + 6), maxW = Math.min(340, stop - 8 - fr.left - x);   // a phone: its panel buttons sit inside the column
    if(maxW < 120){ fn.style.cssText = `left:0; top:${Math.round(sr.bottom - fr.top + 6)}px; transform:none; max-width:${Math.round(Math.min(340, stop - 8 - fr.left))}px;`; return; }   // no room beside it (a phone, two columns): under the column
    fn.style.cssText = `left:${Math.round(x)}px; top:${Math.round(cr.top - fr.top + cr.height / 2)}px; max-width:${Math.round(maxW)}px;`;
  }
  function panelsLeft(box){
    const br = box.getBoundingClientRect(), bs = box.querySelector('.it-map-fbtns'), sr = bs && bs.offsetParent ? bs.getBoundingClientRect() : null;
    const rl = box.querySelector('.mk-rail'), col = document.querySelector('#intelPanel .it-top:not(.itx-top) .it-nearcol'), rr = rl && rl.getBoundingClientRect(), cr = S.nyOpen && col ? col.getBoundingClientRect() : null;
    const L = sr ? sr.right + 6 + pbW() + 8 : br.left + 60, R = rr ? Math.min(br.right - 8, (cr ? cr.left : rr.left) - 8) : br.right - 8;
    for(const el of box.querySelectorAll('.it-whp')){
      if(el.hidden) continue;
      const k = el.classList.contains('mk-sp') ? 'sov' : 'wh', f = bs && bs.querySelector(`[data-im-f="${k}"]`), fr = f && f.getBoundingClientRect();
      const w = Math.min(k === 'sov' ? 560 : 400, R - L), maxH = br.height - 16, h = Math.min(el.scrollHeight || 300, maxH);
      const y = Math.max(br.top + 8, Math.min(br.bottom - 8 - h, fr ? fr.top - 4 : br.top + 8));   // level with its filter, kept inside the map
      el.style.cssText = `left:${Math.round(L - br.left)}px; right:auto; top:${Math.round(y - br.top)}px; bottom:auto; width:${Math.round(w)}px; max-height:${Math.round(maxH)}px;`;
    }
  }
  function apply(){
    if(flLeft()) S.rail = 'right';   // feeds on the right when the filters are on the left
    document.body.dataset.mkLay = S.lay; document.body.dataset.mkPm = flLeft() ? 'side' : S.fp; document.body.dataset.mkFl = flLeft() ? 'left' : 'bottom'; document.body.dataset.mkCk = S.ck;
    if(typeof itRender === 'function'){ try{ itRender(true); }catch(e){} }
    fpMount(); fpPaint();
    if(itm.el) itMapRefresh(true);
    requestAnimationFrame(() => { place(); if(itm.el) itMapRefresh(true); requestAnimationFrame(place); });
    if(S.sovOpen && sp) sp.innerHTML = sovHtml();
    paintBar();
  }
  new MutationObserver(() => { if(raf) return; raf = requestAnimationFrame(() => { raf = 0; fpMount(); place(); }); })
    .observe(document.getElementById('intelPanel') || document.body, {childList: true, subtree: true, attributes: true, attributeFilter: ['class', 'aria-pressed', 'hidden']});
  addEventListener('resize', () => requestAnimationFrame(place));

  // ---- styles ----
  const css = document.createElement('style');
  css.textContent = `
  /* filters with panels: each filter's own panel button, shown on hover / focus and while that filter is on (as the Wormholes list button today) */
  .it-map-fbtns .mk-fw{position:relative; display:inline-flex; align-items:center;}
  .it-map-fbtns .mk-fw > button.mk-pbtn{position:static !important; left:auto !important; top:auto !important; margin:0 2px 0 1px !important; border:1px solid var(--line) !important; border-radius:6px;
    background:rgba(12,16,20,.92); color:var(--heading); visibility:hidden !important; opacity:0 !important; transition:opacity .15s, visibility 0s .6s !important;}
  .it-map-fbtns .mk-fw > [aria-pressed="true"] ~ button.mk-pbtn,
  .it-map-fbtns .mk-fw > button.mk-pbtn[aria-expanded="true"]{visibility:visible !important; opacity:1 !important; transition-delay:0s !important;}
  @media (hover: hover){ .it-map-fbtns .mk-fw:hover > button.mk-pbtn, .it-map-fbtns .mk-fw:focus-within > button.mk-pbtn{visibility:visible !important; opacity:1 !important; transition-delay:0s !important;} }   /* touch screens: only while that filter is on (no sticky hover after a tap) */
  body[data-mk-pm="above"] .it-map-fbtns .mk-fw > button.mk-pbtn{position:absolute !important; left:50% !important; top:auto !important; bottom:calc(100% + 7px); transform:translateX(-50%); margin:0 !important; z-index:2;
    box-shadow:0 4px 12px rgba(0,0,0,.45);}
  body[data-mk-pm="above"] .it-map-fn{margin-bottom:38px;}   /* round 3b (the owner's screenshot): the name line sits above the raised panel button, not under it; always, so it never jumps */
  body[data-mk-pm="above"] .it-map-fbtns .mk-fw::before{content:''; position:absolute; left:0; right:0; bottom:100%; height:9px;}   /* keeps the hover while the pointer moves up to the button */
  body[data-mk-pm="above"] .it-map-fbtns .mk-fw > button.mk-pbtn::after{content:''; position:absolute; left:50%; top:100%; margin-left:-4px; border:4px solid transparent; border-top-color:var(--line);}
  @media (prefers-reduced-motion: reduce){ .it-map-fbtns .mk-fw > button.mk-pbtn{transition:none !important;} }
  @media (max-width: 599px){ .it-map-fbtns .mk-fw > button.mk-pbtn{min-width:44px; min-height:44px;} }
  .mk-sp{max-height:min(520px, calc(100% - 72px));}
  .mk-sec{margin:10px 0 4px; font:700 11px var(--sans); color:var(--text-dim); text-transform:uppercase; letter-spacing:.5px;} .mk-sec span{text-transform:none; letter-spacing:0; font-weight:400;}
  @media (min-width: 900px){ .mk-sp{width:min(560px, calc(100% - 16px));} .mk-sgs{display:grid; grid-template-columns:1fr 1fr; column-gap:18px;} }
  .mk-sg{display:flex; flex-direction:column; gap:2px; margin:0 0 6px;} .mk-sg > b{font:600 12px var(--sans); color:var(--heading);}
  .mk-tipsov{margin-top:3px; color:var(--text);}
  .mk-sk{display:flex; align-items:center; gap:6px; min-height:24px; color:var(--text);} .mk-lx{margin-top:8px;} .mk-lists{margin-top:4px;} .mk-sp{overflow:auto;} .mk-lv{color:var(--text-dim); font:400 11px var(--sans); margin-left:4px;} .mk-n{margin-left:auto; font:600 11px var(--mono); color:var(--text-dim);}
  .mk-lr{display:flex; flex-wrap:wrap; align-items:center; gap:6px; padding:6px 0; border-top:1px solid var(--line);} .mk-lr > div{flex:1 1 200px;} .mk-lr span{color:var(--text-dim);} .mk-lr button{min-height:28px; padding:2px 10px;}
  .mk-pb{margin-top:6px;} .mk-pb textarea{width:100%; box-sizing:border-box; font:12px/1.4 var(--mono);} .mk-pr{display:flex; flex-wrap:wrap; gap:6px; align-items:center; justify-content:space-between; margin-top:4px;} .mk-pm{color:var(--amber); margin-top:4px;}
  @media (max-width: 599px){ .mk-sk{min-height:40px;} .mk-lr button, .mk-pr button, .mk-pr select{min-height:44px;} .mk-sb, .mk-fp{min-width:44px; min-height:44px;} }
  /* Near You's hide button (A only) */
  /* round 3: the rail of map panel buttons, in the map's own button style (as + − ⤢ ⌖), under the zoom buttons (right) or the search box (left) */
  .mk-rail{display:none;}
  body[data-mk-lay="a"] .mk-rail{display:flex; flex-direction:column; gap:4px; position:absolute; z-index:5; top:46px; right:8px;}
  body[data-mk-lay="a"] .it-map-box[data-mk-rail="left"] .mk-rail{right:auto; left:8px; top:50px;}
  .mk-rail button{position:relative; width:30px; min-height:30px; height:30px; padding:0; border-radius:4px; border:1px solid var(--line); background:rgba(18,23,28,.9); color:var(--text); cursor:pointer; display:flex; align-items:center; justify-content:center;}
  .mk-rail button:hover:not(:disabled){border-color:color-mix(in srgb, var(--cyan) 55%, transparent);}
  .mk-rail button[aria-pressed="true"]{background:var(--tag-on); color:var(--heading);}
  .mk-rail button:disabled{opacity:.4; cursor:default;}
  .mk-rail button:focus-visible{outline:2px solid var(--cyan); outline-offset:1px;}
  .mk-rail svg{display:block;}
  .mk-badge{position:absolute; top:-6px; right:-7px; min-width:15px; height:15px; box-sizing:border-box; padding:0 3px; border-radius:8px; border:1px solid var(--line); background:#222c36; color:var(--heading); font:700 10px/13px var(--mono); text-align:center;}
  .mk-badge.al{background:var(--amber); border-color:var(--amber); color:#1b1306;}
  @media (max-width: 599px){ .mk-rail button{width:44px; height:44px; min-height:44px;} body[data-mk-lay="a"] .mk-rail, body[data-mk-lay="a"] .it-map-box[data-mk-rail="left"] .mk-rail{top:60px;} }
  /* bigger map, no List | Map switch (A, B, C) */
  body:not([data-mk-lay="today"]) .it-top .it-nv{display:none !important;}
  body:not([data-mk-lay="today"]) .it-top .it-mapcol{display:block !important;}
  body:not([data-mk-lay="today"]) .it-top #itNearList{display:block;}
  body[data-mk-lay="a"] #itNearList .it-nb.dd, body[data-mk-lay="b"] #itNearList .it-nb.dd{grid-template-columns:var(--it-jw, 66px) 26px minmax(0,1fr) auto !important;
    grid-template-areas:"j an sys age" ". . rg rg" ". . tg tg" ". . kb kb" "rt . wl wl" !important; row-gap:2px;}
  @media (max-width: 599px){ body[data-mk-lay="a"] #itNearList .it-nb.dd, body[data-mk-lay="b"] #itNearList .it-nb.dd{grid-template-columns:auto minmax(0,1fr) auto !important; grid-template-areas:"j sys age" "an rg rg" ". tg tg" ". kb kb" "rt wl wl" !important;} }
  /* A: Near You inside the map, a panel on its right (phone: a sheet over the bottom of the map) */
  body[data-mk-lay="a"] .it-top{display:block; position:relative;}
  body[data-mk-lay="a"] .it-top .it-nearcol{position:absolute; z-index:4; contain:none !important; min-height:0 !important; display:flex; flex-direction:column; box-sizing:border-box; padding:10px 12px 8px;
    background:var(--panel); border:1px solid var(--line); border-radius:6px; box-shadow:0 8px 24px rgba(0,0,0,.5); overflow:hidden;}   /* round 6 (the owner: "Site panel style"): as .it-whp */
  body[data-mk-lay="a"] .it-top .it-nearcol > .it-h h3{font:700 14px var(--sans); color:var(--heading); margin:0;}
  body[data-mk-lay="a"] #itNearList .it-nb, body[data-mk-lay="a"] #itNearList .it-nb.alert{background:var(--panel-2);}   /* rows: the site's card colour inside a panel */
  body[data-mk-lay="a"] .it-top .it-nearcol > #itNearList{flex:1 1 0; min-height:0; overflow-y:auto;}
  body[data-mk-lay="a"] .it-top .it-nearcol > .it-h{flex:none; display:flex; align-items:center; gap:8px; flex-wrap:nowrap;}
  body[data-mk-lay="a"] .it-top .it-nearcol > .it-h .ctx{white-space:nowrap; overflow:hidden; text-overflow:ellipsis; min-width:0;}
  body[data-mk-lay="a"] .it-top .it-nearcol > .it-more{display:block; flex:none; padding:5px 2px 0; font:400 11.5px var(--sans); color:var(--text-dim); border-top:1px solid var(--line-soft);}
  body[data-mk-lay="a"] .it-top .it-nearcol > .it-more[hidden]{display:none;}
  body[data-mk-lay="a"].mk-nyc .it-top .it-nearcol{display:none !important;}
  @media (max-width: 599px){ body[data-mk-lay="a"] .it-top .it-nearcol{order:2;} body[data-mk-lay="a"] .it-top .it-nearcol > .it-h h3{font-size:14px;} }
  /* B: Near You as a strip of cards above the map */
  body[data-mk-lay="b"] .it-top{display:flex; flex-direction:column; gap:10px;}
  body[data-mk-lay="b"] .it-top .it-nearcol{order:1; contain:none !important; min-height:0 !important; display:block; min-width:0; max-width:100%;} body[data-mk-lay="b"] .it-top{min-width:0; max-width:100%;}
  body[data-mk-lay="b"] .it-top .it-mapcol{order:2;}
  body[data-mk-lay="b"] .it-top .it-nearcol > #itNearList{display:flex !important; gap:8px; overflow-x:auto; overflow-y:hidden; scroll-snap-type:x proximity; padding-bottom:6px;}
  body[data-mk-lay="b"] #itNearList > *{flex:0 0 300px; scroll-snap-align:start; margin:0 !important;}
  body[data-mk-lay="b"] .it-top .it-nearcol > .it-more{display:none !important;}
  @media (max-width: 599px){ body[data-mk-lay="b"] #itNearList > *{flex-basis:82vw;} }
  /* C: the map across the top; Near You beside the Feed under it, staying in view while the Feed scrolls */
  body[data-mk-lay="c"] .it-card{display:grid; grid-template-columns:minmax(0, 2fr) minmax(0, 3fr); column-gap:18px; align-items:start;}
  body[data-mk-lay="c"] .it-card > *{grid-column:1 / -1;}
  body[data-mk-lay="c"] .it-top{display:contents;}
  body[data-mk-lay="c"] .it-top .it-mapcol{grid-column:1 / -1; margin-bottom:6px;}
  body[data-mk-lay="c"] .it-top .it-nearcol{grid-column:1; contain:none !important; min-height:0 !important; display:block; position:sticky; top:8px; max-height:calc(100vh - 16px); overflow:auto;}
  body[data-mk-lay="c"] .it-top .it-nearcol > #itNearList{overflow:visible; max-height:none;}
  body[data-mk-lay="c"] .it-top .it-nearcol > .it-more{display:none !important;}
  body[data-mk-lay="c"] .it-card > .it-feedcol{grid-column:2;}
  @media (max-width: 900px){ body[data-mk-lay="c"] .it-card{display:block;} body[data-mk-lay="c"] .it-top{display:flex; flex-direction:column;} body[data-mk-lay="c"] .it-top .it-mapcol{order:1;} body[data-mk-lay="c"] .it-top .it-nearcol{order:2; position:static; max-height:none;} }
  /* round 5: filters down the left edge (feeds on the right) */
  body[data-mk-fl="left"] .it-map-fb{left:8px !important; right:auto !important; top:var(--mk-flt, 52px); bottom:auto !important; transform:none !important; align-items:flex-start; max-width:none !important;}
  body[data-mk-fl="left"] .it-map-fbtns{display:grid; grid-auto-flow:column; grid-template-rows:repeat(var(--mk-flr, 12), auto); justify-items:start; align-content:start;}

  body[data-mk-fl="left"] .it-map-fn{position:absolute; transform:translateY(-50%); width:max-content; text-align:left; margin:0 !important; z-index:1;}
  body[data-mk-fl="left"].mk-pop .it-map-fn{visibility:hidden;}   /* a panel is open: its own heading names it */
  @media (max-width: 599px){ body[data-mk-fl="left"] .it-map-fb:not(.open) .it-map-fbtns{display:none;}
    body[data-mk-fl="left"] .it-map-fbtns .mk-fw > button.mk-pbtn{display:none !important;} body[data-mk-fl="left"] .it-map-fbtns .mk-fw > [aria-pressed="true"] ~ button.mk-pbtn{display:inline-flex !important;} }   /* a phone: only the panel button of the filter that is on, in the column */
  @media (min-width: 600px){ body[data-mk-fl="left"] .it-map-fbtns .mk-fw > button.mk-pbtn{position:absolute !important; left:calc(100% + 10px) !important; top:0 !important; bottom:auto !important; transform:none !important; margin:0 !important;} }
  body[data-mk-fl="left"] .it-map-fbtns .mk-fw > button.mk-pbtn::after{display:none;}
  body[data-mk-fl="left"] .it-map-fbtns .mk-fw::before{content:''; position:absolute; left:100%; top:0; bottom:0; width:12px;}   /* keeps the hover while the pointer crosses to the panel button */
  @media (max-width: 599px){ body[data-mk-fl="left"] .it-whp{top:auto; bottom:8px !important; max-height:calc(100% - 76px) !important;} }
  /* round 6b: the Intel example in layout A */
  body[data-mk-lay="a"] .itx-top{position:relative;}
  body[data-mk-lay="a"] .itx-map{position:relative;}
  body[data-mk-lay="a"] .itx-map .mk-exrail{display:flex; flex-direction:column; position:absolute; top:8px; right:8px; z-index:2;}
  body[data-mk-lay="a"].mk-nyc .it-top.itx-top .it-nearcol{display:flex !important;}
  body[data-mk-lay="a"] .it-top.itx-top .it-nearcol{max-width:none; z-index:2;}   /* under the numbered markers (z 3) */
  @media (max-width: 599px){ body[data-mk-lay="a"] .it-top.itx-top .it-nearcol{position:static; margin-top:10px; height:auto;} body[data-mk-lay="a"] .it-top.itx-top .it-nearcol > .itx-near{overflow:visible;} }
  /* round 6: checkboxes and radio buttons in the text field's colours (the owner: "can we treat radio buttons and checkboxes like text inputs with regard to colors?"); switches keep theirs */
  input[type=checkbox]:not(.mys-sw):not(.dmg-sw):not([role=switch]), input[type=radio]{appearance:none; -webkit-appearance:none; box-sizing:border-box; width:16px; height:16px; min-width:16px; margin:0 4px 0 0; padding:0;
    display:inline-grid; place-content:center; vertical-align:-3px; background:var(--bg); border:1px solid var(--field-border); border-radius:3px; cursor:pointer; color:var(--cyan);}
  input[type=radio]{border-radius:50%;}
  input[type=checkbox]:not(.mys-sw):not(.dmg-sw):not([role=switch])::before{content:''; width:8px; height:4px; margin-top:-2px; border:solid currentColor; border-width:0 0 2px 2px; transform:rotate(-45deg); visibility:hidden;}
  input[type=radio]::before{content:''; width:8px; height:8px; border-radius:50%; background:currentColor; visibility:hidden;}
  input[type=checkbox]:not(.mys-sw):not(.dmg-sw):not([role=switch]):checked::before, input[type=radio]:checked::before{visibility:visible;}
  input[type=checkbox]:not(.mys-sw):not(.dmg-sw):not([role=switch]):hover, input[type=radio]:hover{border-color:var(--field-border-hover);}
  input[type=checkbox]:not(.mys-sw):not(.dmg-sw):not([role=switch]):checked, input[type=radio]:checked{border-color:var(--cyan);}
  body[data-mk-ck="fill"] input[type=checkbox]:not(.mys-sw):not(.dmg-sw):not([role=switch]):checked, body[data-mk-ck="fill"] input[type=radio]:checked{background:var(--cyan); color:var(--bg);}
  input[type=checkbox]:not(.mys-sw):not(.dmg-sw):not([role=switch]):focus-visible, input[type=radio]:focus-visible{outline:none; border-color:var(--cyan); box-shadow:0 0 0 2px var(--accent-ring);}
  input[type=checkbox]:not(.mys-sw):not(.dmg-sw):not([role=switch]):disabled, input[type=radio]:disabled{opacity:.45; cursor:not-allowed;}
  /* the MOCKUP bar */
  .mk-bar{position:fixed; right:8px; top:8px; z-index:9999; max-width:min(560px, calc(100vw - 16px)); max-height:calc(100vh - 16px); overflow:auto; box-sizing:border-box; padding:6px 8px; border:1px solid #e4b5ff; border-radius:6px; background:rgba(12,16,20,.96); color:#e4b5ff; font:600 12px/1.4 system-ui, sans-serif;}
  .mk-bar .row{display:flex; flex-wrap:wrap; gap:4px; align-items:center; margin:2px 0;} .mk-bar .lb{min-width:64px;}
  .mk-bar button{min-height:30px; font:600 12px system-ui; background:#1d2731; color:#e4b5ff; border:1px solid #6b5480; border-radius:4px; padding:0 8px; cursor:pointer;}
  .mk-bar button[aria-pressed="true"]{background:#e4b5ff; color:#1a1020; border-color:#e4b5ff;}
  .mk-bar .note{font-weight:400; color:#d8c6e6; font-size:11.5px;} .mk-bar.min .row:not(.top){display:none;}
  @media (max-width: 599px){ .mk-bar{top:auto; bottom:8px; left:8px; right:auto;} .mk-bar:not(.min){right:8px;} .mk-bar button{min-height:36px;} .mk-bar .lb{min-width:0; flex:1 0 100%;} }`;
  document.head.appendChild(css);

  // ---- the MOCKUP bar ----
  const NOTES = {today: 'Today: the map beside Near You, the Feed below (for comparison).',
    a: 'A (picked): the map first. Near You is a button in the map\'s own style (count on it, amber when a system is in your alert range); press it and its list opens beside the buttons, which stay where they are and stay clickable. Routes (greyed) shows where a second panel would sit. Near You\'s list uses the site\'s panel style (as the filter panels), its rows the card colour. A filter\'s panel opens clear of the Near You list; on a phone it shuts Near You (one at a time). The Feed below, full width.'};
  const RAILN = {right: 'Right: the buttons under + − ⤢ ⌖; the list opens to their left.', left: 'Left: the buttons under the search box; the list opens to their right.'};
  const FLN = {bottom: 'Along the bottom: the filter bar centred at the foot of the map, as today; its panels open above it.',
    left: 'Down the left (picked): the filters in a column under the search box; a filter\'s panel button to its right, and the filter\'s name to the right of that. A panel opens to the right of the column, level with its filter. Near You and Routes stay on the right. On a phone, the filter column and the Near You list take turns.'};
  const FPN = {side: 'Panel button to the right of its filter: appears when you hover or focus the filter, and stays while that filter is on.',
    beside: 'Panel button beside its filter: appears when you hover or focus the filter, and stays while that filter is on. Its space is kept, so nothing moves when it appears.',
    above: 'Panel button above its filter, with a small pointer: appears when you hover or focus the filter, and stays while that filter is on. The bar keeps its width.'};
  const CKN = {tick: 'Checked: the border and the tick (or dot) turn cyan; the box stays dark.', fill: 'Checked: the box fills cyan with a dark tick (or dot).'};
  const LOOKN = {dim: 'Bright / dim: systems with a picked upgrade bright, the rest dimmed (as Wormholes). Hover a system for its upgrades and levels.',
    colour: 'Colour by group: bright / dim, plus a ring split into one arc per group the system has (Ratting amber, Exploration cyan, Mining green, Other violet, Navigation white).',
    marks: 'Marks: short codes beside each system (Maj3, Min2, Expl, Mega, Beacon …); zoomed out, where codes would pile up, the coloured rings instead.'};
  const bar = document.createElement('div'); bar.className = 'mk-bar'; bar.setAttribute('role', 'region'); bar.setAttribute('aria-label', 'Mockup controls');
  function paintBar(){
    const b = (g, v, t) => `<button type="button" data-mk-g="${g}" data-mk-v="${v}" aria-pressed="${S[g] === v}">${t}</button>`;
    bar.innerHTML = `<div class="row top"><span>MOCKUP · round 6</span><button type="button" data-mk-min>${bar.classList.contains('min') ? 'Show' : 'Hide'}</button></div>`
      + `<div class="row"><span class="lb">Layout</span>${b('lay', 'a', 'A · in the map')}${b('lay', 'today', 'Today')}</div>`
      + `<div class="row note">${NOTES[S.lay]}</div>`
      + `<div class="row"><span class="lb">Filters</span>${b('fl', 'bottom', 'Along the bottom')}${b('fl', 'left', 'Down the left')}</div>`
      + `<div class="row note">${FLN[S.fl]}</div>`
      + `<div class="row"><span class="lb">Near You</span>${b('rail', 'right', 'Right side')}${S.fl === 'left' ? '' : b('rail', 'left', 'Left side')}<button type="button" data-mk-nyt>${S.nyOpen ? 'Close the list' : 'Open the list'}</button></div>`
      + `<div class="row note">${RAILN[S.rail]}</div>`
      + `<div class="row"><span class="lb">Icon</span>${Object.keys(ICONN).map(k => `<button type="button" data-mk-g="icon" data-mk-v="${k}" aria-pressed="${S.icon === k}" title="${k}"><span style="display:inline-flex;vertical-align:middle">${svg(ICONS[k])}</span> ${ICONN[k]}</button>`).join('')}</div>`
      + (S.fl === 'left' ? '' : `<div class="row"><span class="lb">Panel button</span>${b('fp', 'beside', 'Beside the filter')}${b('fp', 'above', 'Above the filter')}</div>`)
      + `<div class="row note">${S.fl === 'left' ? FPN.side : FPN[S.fp]} Hover Wormholes or Sov upgrades on the map's filter bar.</div>`
      + `<div class="row"><span class="lb">Example</span><button type="button" data-mk-ex>${itEx.view ? 'Close the Intel example' : 'Show the Intel example'}</button></div>`
      + `<div class="row note">The setup screen's example (five numbered notes) in this layout: the map across, Near You open beside its button; on a phone the list under the map.</div>`
      + `<div class="row"><span class="lb">Sov lists</span><button type="button" data-mk-sov>Open Sov upgrades</button></div>`
      + `<div class="row note">Each list on its own: Edit, Replace or Remove one without touching the others. Made-up upgrades.</div>`
      + `<div class="row note">Sov look: bright / dim (picked). Jump bridge comes from your Jump bridges list (no paste here).</div>`
      + `<div class="row"><span class="lb">Checked</span>${b('ck', 'tick', 'Cyan tick, dark box')}${b('ck', 'fill', 'Solid cyan box')}</div>`
      + `<div class="row note">${CKN[S.ck]} Every checkbox and radio button on the site (Sov panel, Drifter in the Wormholes list, Intel's channels and settings, the route planner) gets the text field's colours: dark fill, field border, cyan focus ring; switches keep their own look.</div>`;
  }
  bar.addEventListener('click', (e) => {
    if(e.target.closest('[data-mk-min]')){ bar.classList.toggle('min'); paintBar(); return; }
    if(e.target.closest('[data-mk-nyt]')){ S.nyOpen = !S.nyOpen; place(); paintBar(); return; }
    if(e.target.closest('[data-mk-ex]')){ itExOpen(!itEx.view); paintBar(); const f = document.querySelector('#intelPanel .itx'); if(f && itEx.view) f.scrollIntoView({block: 'start'}); return; }
    if(e.target.closest('[data-mk-sov]')){ itMapFilterSet('sov'); sovPanel(true); if(itm.box) itm.box.scrollIntoView({block: 'center'}); return; }
    const x = e.target.closest('[data-mk-g]'); if(!x) return;
    S[x.dataset.mkG] = x.dataset.mkV; if(x.dataset.mkG === 'lay') S.nyOpen = false;
    if(x.dataset.mkG === 'rail' || x.dataset.mkG === 'icon'){ place(); paintBar(); return; }
    if(x.dataset.mkG === 'ck'){ document.body.dataset.mkCk = S.ck; paintBar(); return; }
    if(x.dataset.mkG === 'look'){ if(itm.filter !== 'sov') itMapFilterSet('sov'); if(S.look === 'marks' && itMapGatePx() < 26) itMapZoom(itm.W / 2, itm.H / 2, 30 / itMapGatePx()); itMapDraw(); itMapLegend(); paintBar(); return; }
    apply();
  });
  window.MKL = {S, apply, place, sovPanel, ready(){ document.body.appendChild(bar); bar.classList.add('min'); apply(); }};   // the MOCKUP box starts folded: open, it covered the map's top-right corner
})();
