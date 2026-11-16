// Jump bridges prototype (build queue 041, Project doc claude/roadmap/jump-bridges-plan.md), rebuilt 2026-11-16 on main 396fbd6 with
// 058's stacked-filters prototype loaded first (proto_stk.js) as the map model. Mockup shortcuts, not for the build: function overrides
// by name, five hooks in the page (build_jb.py), the settings box spliced into itSettingsHtml's output.
// The owner: Near You, its alerts and the Feed stay by stargate; the map counts the bridges (itm.D: reach, labels, Jumps colour,
// Within N, the hover) while its alert glow, Near You fade, Paths to you and the kill-range line use the stargate count (itm.Dg).
// Threat Vector's route stays by stargate until 057 ("Switch governs both; gates until 057 (Recommended)").
(() => {
  const MAX = 12000, COL = '#00f000';   // the plan's IT_BRIDGE_MAX and --it-bridge
  const SEP = /»|«|<->|->|<-|=>|→|←|⇄|↔/;   // D7: a line with one of these: the bridge is the name before it and the name after it
  let memo = null;
  // the system names on a piece of a line, in order (1-3 words, longest first; words of digits only are ignored, D8)
  function names(part){
    const N = it.names, W = part.split(/[\s,;|\t]+/).map(w => w.replace(/^[^A-Za-z0-9]+|[^A-Za-z0-9]+$/g, '')).filter(w => w && !/^\d+$/.test(w)), out = [];
    for(let i = 0; i < W.length;){
      let hit = 0;
      for(let k = Math.min(3, W.length - i); k >= 1; k--){ const id = N && N.byLower.get(W.slice(i, i + k).join(' ').toLowerCase()); if(id){ out.push(id); hit = k; break; } }
      i += hit || 1;
    }
    return out;
  }
  function itBridges(){
    const text = String(it.set && it.set.bridges || ''), N = it.names;
    if(memo && memo.text === text && memo.N === N) return memo;
    const g = itGraphGet(), rows = [], edges = [], seen = new Map(), used = new Map();
    text.split(/\r?\n/).forEach((raw, li) => {
      const ln = raw.trim(); if(!ln) return;
      const n = li + 1, m = ln.match(SEP);
      let ids;
      if(m){ const L = names(ln.slice(0, m.index)), R = names(ln.slice(m.index + m[0].length)); ids = [L[L.length - 1], R[0]].filter(Boolean); }
      else {
        const f = names(ln), u = [...new Set(f)];
        if(u.length > 2) return rows.push({n, ln, st: 'bad', msg: 'more than two systems: one bridge per line'});
        ids = f.length === 2 && u.length === 1 ? [f[0], f[1]] : u;
      }
      if(ids.length === 2 && ids[0] === ids[1]) return rows.push({n, ln, st: 'bad', msg: 'the same system twice'});
      if(ids.length < 2) return rows.push({n, ln, st: 'bad', msg: ids.length ? `needs two systems (found only ${itSysName(ids[0])})` : 'needs two systems'});
      const [a, b] = ids, ia = g.at.get(a), ib = g.at.get(b);
      if(ia === undefined || ib === undefined) return rows.push({n, ln, st: 'bad', msg: `${itSysName(ia === undefined ? a : b)} has no stargates`});
      const key = Math.min(ia, ib) * 65536 + Math.max(ia, ib);
      if(seen.has(key)) return rows.push({n, ln, st: 'dup', a, b, msg: `same bridge as line ${seen.get(key)}`});   // D6: SMT lists each direction
      seen.set(key, n);
      const warn = [];
      for(const id of [a, b]){ if(used.has(id)) warn.push(`${itSysName(id)} is also on line ${used.get(id)} (one jump gate per system)`); else used.set(id, n); }
      const ly = itMapTable() ? itMapLy(ia, ib) : null;
      if(ly !== null && ly > 5) warn.push('more than 5 LY apart (an Ansiblex reaches 5)');
      edges.push([ia, ib]); rows.push({n, ln, st: warn.length ? 'warn' : 'ok', a, b, ly, msg: warn.join('; ')});
    });
    const ends = [...new Set(edges.flatMap(([x, y]) => [g.ids[x], g.ids[y]]))].sort((x, y) => x - y);
    memo = {text, N, rows, edges, set: new Set(seen.keys()), ends, key: `${text.length}:${edges.map(e => e.join('-')).join(',')}`};
    return memo;
  }
  const on = () => !!(it.set && it.set.bridgesOn) && itBridges().edges.length > 0;
  // 053's hook: both ends of every counted bridge (✓ and ⚠), whatever the switch (the Sov filter's Jump bridge kind)
  sovBridgeEnds = function(){ return itBridges().ends; };
  function itBridgeAdj(){
    const B = itBridges(); if(B.adj) return B.adj;
    const T = itMapTable(); B.adj = T.adj.map(a => a.slice());
    for(const [a, b] of B.edges){ B.adj[a].push(b); B.adj[b].push(a); }
    for(const a of B.adj) a.sort((p, q) => p - q);   // index order, one route per system, as T.adj
    return B.adj;
  }
  const isJb = (a, b) => itBridges().set.has(Math.min(a, b) * 65536 + Math.max(a, b));
  // the map's search: itm.D / itm.par with the bridges (switch on), itm.Dg by stargate (always)
  itMapBfs = function(home){
    const T = itMapTable(), n = T.n;
    const bfs = (adj) => { const D = new Int16Array(n).fill(-1), par = new Int32Array(n).fill(-1), q = [home]; D[home] = 0;
      for(let h = 0; h < q.length; h++){ const x = q[h]; for(const y of adj[x]) if(D[y] < 0){ D[y] = D[x] + 1; par[y] = x; q.push(y); } } return [D, par]; };
    const [Dg, pg] = bfs(T.adj);
    if(on()){ const [D, par] = bfs(itBridgeAdj()); itm.D = D; itm.par = par; } else { itm.D = Dg; itm.par = pg; }
    itm.Dg = Dg; itm.jbKey = on() ? itBridges().key : '';
  };
  function arc(c, x1, y1, x2, y2){ const mx = (x1 + x2) / 2, my = (y1 + y2) / 2, dx = x2 - x1, dy = y2 - y1; c.moveTo(x1, y1); c.quadraticCurveTo(mx - dy * 0.22, my + dx * 0.22, x2, y2); }
  // the bridges: solid green curves under the systems, faint past the reach (drawn only while the switch is on)
  const draw0 = itMapDraw;
  itMapDraw = function(){
    draw0();
    if(!on() || !itm.P || itm.home < 0 || (typeof itPtLive === 'function' && itPtLive())) return;
    const c = itm.cv.getContext('2d'), Q = itm.Q, D = itm.D, R = itm.reach, big = itMapGatePx() >= 34, X = (i) => Q[2 * i], Y = (i) => Q[2 * i + 1], o = (i) => D[i] >= 0 && D[i] <= R;
    c.save(); c.globalCompositeOperation = 'destination-over'; c.strokeStyle = COL; c.lineWidth = big ? 1.75 : 1.25; c.setLineDash([]);
    for(const [a, b] of itBridges().edges){ c.globalAlpha = o(a) || o(b) ? 0.85 : 0.35; c.beginPath(); arc(c, X(a), Y(a), X(b), Y(b)); c.stroke(); }
    c.restore();
  };
  const key0 = itMapKey;
  itMapKey = function(){ return key0() + '|jb:' + (on() ? itBridges().key : ''); };
  // the hover: how many of the map's jumps are by bridge and the count by stargate; the drawn route is by stargate (Threat Vector's
  // route, until 057), so its line says so; Threat Vector's route is compared with the stargate count
  const tip0 = itMapTip;
  itMapTip = function(i, x, y){
    tip0(i, x, y);
    if(i < 0 || !on() || !(itm.D[i] > 0)) return;
    let n = 0, k = i; while(k !== itm.home && itm.par[k] >= 0 && n < 999){ if(isJb(k, itm.par[k])) n++; k = itm.par[k]; }
    const tip = itm.tip, gj = itm.Dg[i];
    let h = tip.innerHTML.replace('<span class="d">route: ', '<span class="d">route by stargate: ');
    if(n) h = h.replace(/<br>/, `<br><span class="jb">${n} of the ${itm.D[i]} jumps by jump bridge</span> <span class="d">· by stargate only ${gj < 0 ? 'no route' : gj + ' jump' + (gj === 1 ? '' : 's')}</span><br>`);
    if(h !== tip.innerHTML){ tip.innerHTML = h; const tw = tip.offsetWidth, th = tip.offsetHeight; tip.style.left = Math.max(4, Math.min(itm.W - tw - 6, x + 14)) + 'px'; tip.style.top = (y + th + 18 > itm.H ? Math.max(4, y - th - 12) : y + 14) + 'px'; }
  };
  const rpTip0 = itRpTipHtml;
  itRpTipHtml = function(i){ if(!on() || !itm.Dg) return rpTip0(i); const D = itm.D; itm.D = itm.Dg; try{ return rpTip0(i); } finally { itm.D = D; } };
  // the Jumps colour's note and legend
  const jf = IT_MAP_FILTERS.find(f => f.k === 'jumps'), jfNote = jf.note;
  Object.defineProperty(jf, 'note', {configurable: true, get: () => on() ? 'colour: jumps from your system, your jump bridges counted' : jfNote, set: () => {}});
  const fleg0 = itMapFLegHtml, ftit0 = itMapFLegTitle;
  itMapFLegHtml = function(){ const h = fleg0(); return on() && itm.filter === 'jumps' ? h.replace('· grey: no gate route', '· your jump bridges counted · grey: no route') : h; };
  itMapFLegTitle = function(){ const t = ftit0(); return on() && itm.filter === 'jumps' ? 'Jumps from your system, your jump bridges counted (Intel settings), 0 to 10 or more; grey: no route to you' : t; };
  // the settings box, right after Routes (gear only, like Shorthands)
  function rowsHtml(){
    const nm = (id) => escapeHtml(itSysName(id));
    return itBridges().rows.map(r => r.st === 'bad' ? `<li class="bad">✗ ${escapeHtml(r.ln)}: ${escapeHtml(r.msg)}</li>`
      : r.st === 'dup' ? `<li class="jb-dup">${nm(r.a)} ⇄ ${nm(r.b)} · ${escapeHtml(r.msg)}</li>`
      : `<li class="${r.st === 'warn' ? 'jb-warn' : 'ok'}">${r.st === 'warn' ? '⚠' : '✓'} ${nm(r.a)} ⇄ ${nm(r.b)}${r.ly !== null ? ` · ${itMapLyText(r.ly)} LY` : ''}${r.msg ? `: ${escapeHtml(r.msg)}` : ''}</li>`).join('');
  }
  function countText(){ const n = itBridges().edges.length; return `(${n} bridge${n === 1 ? '' : 's'})`; }
  function boxHtml(){
    return `<div class="it-box it-alias it-jb"><div class="k">Jump bridges</div>`
      + `<label class="jb-on"><input type="checkbox" data-it-jbon${it.set.bridgesOn ? ' checked' : ''}> Use jump bridges on the map <span class="d">${countText()}</span></label>`
      + `<div class="c">One per line: <code>1DQ1-A » 8QT-H4</code>, <code>A → B</code> or two names; the rest of the line is ignored. Kept in this browser only.</div>`
      + `<textarea data-it-jb rows="4" maxlength="${MAX}" spellcheck="false" aria-label="Your jump bridges, one per line: two system names" placeholder="1DQ1-A » 8QT-H4">${escapeHtml(it.set.bridges || '')}</textarea><ul>${rowsHtml()}</ul></div>`;
  }
  const set0 = itSettingsHtml;
  itSettingsHtml = function(numbered){ const s = set0(numbered); if(numbered) return s; const a = itRpBoxHtml(false); return s.includes(a) ? s.replace(a, a + boxHtml()) : s.replace(itAliasBoxHtml(), boxHtml() + itAliasBoxHtml()); };
  const css = document.createElement('style');
  css.textContent = `.it-jb .jb-on{display:flex; align-items:center; gap:8px; min-height:32px; margin:2px 0 6px;} .it-jb .d{color:var(--text-dim);}
  .it-jb li.jb-warn{color:var(--amber);} .it-jb li.jb-dup{color:var(--text-dim);} .it-map-tip .jb{color:${COL};}
  @media (max-width:599px){ .it-jb .jb-on{min-height:44px;} }`;
  document.head.appendChild(css);
  function relay(){
    if(itm.home >= 0 && itMapTable() && itm.P){ itMapBfs(itm.home); itMapLayout(); itm.key = ''; itMapRefresh(true); }
    if(typeof itRenderLists === 'function') itRenderLists();
  }
  document.addEventListener('input', (e) => {
    const t = e.target; if(!t.matches || !t.matches('[data-it-jb]')) return;
    it.set.bridges = String(t.value || '').slice(0, MAX); itWriteSet(); itBridges();
    const ul = t.parentNode.querySelector('ul'); if(ul) ul.innerHTML = rowsHtml();
    const lab = t.parentNode.querySelector('.jb-on .d'); if(lab) lab.textContent = countText();
    relay();
  }, true);
  document.addEventListener('change', (e) => {
    const t = e.target; if(!t.matches || !t.matches('[data-it-jbon]')) return;
    it.set.bridgesOn = t.checked; itWriteSet(); relay(); if(window.JB && JB.boxPaint) JB.boxPaint();
  }, true);
  // the page's itReadSet drops keys it doesn't know (the build reads bridges / bridgesOn there)
  try{ const r = JSON.parse(localStorage.getItem('dscanIntel') || '{}'); it.set.bridges = typeof r.bridges === 'string' ? r.bridges.slice(0, MAX) : ''; it.set.bridgesOn = r.bridgesOn === true; }catch(e){ }
  window.JB = {relay, on, itBridges, rowsHtml};
})();
