// "Paths to you" prototype (research session 2026-11-12, main d227c9d / v2026.11.12.4). A seventh map filter: instead of the galaxy,
// a tree of the stargate routes from every reported hostile (or neutral) system inside your alert range to you. Rows are jumps from
// you (rows, You at the top); a system on several routes is drawn once, so shared gates read as one
// trunk. Hover or press a system to trace its routes. Wraps itMapDraw, itMapFLegHtml, itMapFLegTitle. Prototype only: in the build it
// is drawn from itMapDraw's own data and redraws only when its key changes (LESSON #120).
(() => {
  'use strict';
  // Decided 2026-11-12: the alert range, every shortest route, this one layout and look (Graph, Plain), a map filter button.
  const PT = window.PT = {pin: -1, hover: -1, v: null, fitKey: '', drag: null, moved: false};
  // round 5 (the owner: "fix the orientation of the "path to you" filter button"): top down like the tree, you (filled) at the top
  const ICON = '<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
    + '<circle cx="9" cy="3.5" r="2.2" fill="currentColor"/><circle cx="3.5" cy="14.5" r="1.8"/><circle cx="9" cy="14.5" r="1.8"/><circle cx="14.5" cy="14.5" r="1.8"/>'
    + '<path d="M3.8 12.7C4 9 9 9 9 5.7M14.2 12.7C14 9 9 9 9 5.7M9 12.7v-7"/></svg>';
  // round 5 (the owner: "the wormhole filter button needs to be furthest right so it sits next to it's wormhole list button"): before Wormholes
  { const f = {k: 'paths', name: 'Paths to you', note: 'the gate routes from hostiles inside your alert range to you, as a tree', icon: ICON}, w = IT_MAP_FILTERS.findIndex(x => x.k === 'wh'); IT_MAP_FILTERS.splice(w < 0 ? IT_MAP_FILTERS.length : w, 0, f); }
  const range = () => it.set.range;   // the owner: "alert range"
  const scopeWord = () => 'your alert range';
  const sysId = (i) => itGraphGet().ids[i];
  const secCls = (i) => itMapSecClass(itMapTable().sec[i]);

  // ---- the tree: which systems and gates lie on a route from each reported system to you ----
  function build(){
    const T = itMapTable(), D = itm.D, R = range(), home = itm.home, src = [];
    for(const [i, r] of itm.rep) if((r.side === 'hostile' || r.side === 'neutral') && D[i] >= 0 && D[i] <= R) src.push(i);
    const nodes = new Map(), edges = new Map();   // i -> {d, from:Set}; "x>y" -> {x, y, from:Set}  (y one jump nearer you)
    const node = (i) => { let n = nodes.get(i); if(!n){ n = {i, d: D[i], from: new Set()}; nodes.set(i, n); } return n; };
    node(home);
    for(const h of src){
      node(h).from.add(h);
      // every shortest route: a breadth-first search from the reported system, as deep as its own distance to you
      const dh = new Map([[h, 0]]), q = [h];
      for(let k = 0; k < q.length; k++){ const x = q[k], dx = dh.get(x); if(dx >= D[h]) continue; for(const y of T.adj[x]) if(!dh.has(y)){ dh.set(y, dx + 1); q.push(y); } }
      const on = (x) => dh.has(x) && D[x] >= 0 && D[x] + dh.get(x) === D[h];
      for(const x of dh.keys()) if(on(x)){
        node(x).from.add(h);
        for(const y of T.adj[x]) if(on(y) && D[y] === D[x] - 1){ const k = x + '>' + y; (edges.get(k) || edges.set(k, {x, y, from: new Set()}).get(k)).from.add(h); }
      }
    }
    // layers by jumps from you, ordered so the lines cross as little as they can: outward by where each system leads (its nearer
    // neighbours' places), then back inward by what feeds it
    const L = []; for(const n of nodes.values()) (L[n.d] = L[n.d] || []).push(n.i);
    for(let d = 0; d <= R; d++) L[d] = L[d] || [];
    const pos = new Map([[home, 0]]), down = (x) => [...edges.values()].filter(e => e.x === x).map(e => e.y), up = (y) => [...edges.values()].filter(e => e.y === y).map(e => e.x);
    const nm = (i) => itSysName(sysId(i));
    const bary = (list, f) => list.length ? list.reduce((s, j) => s + (pos.has(j) ? pos.get(j) : 0), 0) / list.length : 1e9;
    for(let d = 1; d <= R; d++){ L[d].sort((a, b) => bary(down(a)) - bary(down(b)) || nm(a).localeCompare(nm(b))); L[d].forEach((i, k) => pos.set(i, k)); }
    for(let d = R - 1; d >= 1; d--){ L[d].sort((a, b) => { const ua = up(a), ub = up(b); return (ua.length ? bary(ua) : pos.get(a)) - (ub.length ? bary(ub) : pos.get(b)) || pos.get(a) - pos.get(b); }); L[d].forEach((i, k) => pos.set(i, k)); }
    return {R, src, nodes, edges, L};
  }

  // ---- badges (round 4, the owner: "add badges for gate camps, ess and kills"): the page's own tags, cut short for the tree.
  // Camp: Near You's camp tag (red from a report's camp words, orange from 2+ kills at one gate), word only, gate in its hover. ESS:
  // Near You's (red when linked/hacking, white when only at it). Kills: one per side, "N kill(s)" in the side's colour, value in the hover.
  function tagsHtml(i){
    const r = itm.rep.get(i); if(!r || !r.st) return '';
    const st = r.st, keep = Date.now() - it.set.forget * 60000, out = [];
    const box = document.createElement('div'); box.innerHTML = itNearTagsHtml(st);
    for(const x of box.children){
      if(x.classList.contains('it-ess') || x.classList.contains('it-essat')) out.push(x.outerHTML);
      else if(x.classList.contains('camp')){ x.textContent = 'Camp'; out.push(x.outerHTML); }
    }
    const by = {}, isk = {};
    for(const k of (st.kills || []).filter(k => k.t >= keep)){ const v = IT_KILL_WORD[k.v] ? k.v : 'n'; by[v] = (by[v] || 0) + 1; isk[v] = (isk[v] || 0) + (k.isk || 0); }
    for(const v of ['f', 'h', 'n']) if(by[v]) out.push(`<span class="it-kl ${IT_KILL_WORD[v][0]} pt-k" title="${escapeHtml(`${by[v]} ${IT_KILL_WORD[v][by[v] === 1 ? 2 : 3]} in the last ${it.set.forget} min${isk[v] ? `, ${itIsk(isk[v])} ISK` : ''} (zKillboard)`)}">${by[v]} kill${by[v] === 1 ? '' : 's'}</span>`);
    return out.length ? `<span class="pt-tags">${out.join('')}</span>` : '';
  }
  // ---- drawing (HTML boxes over an SVG of curved gate lines; inside the map's box, over its canvas) ----
  let ov = null;
  function mount(){
    if(ov && ov.isConnected && ov.parentNode === itm.box) return ov;
    ov = document.createElement('div'); ov.className = 'pt-ov'; ov.hidden = true;
    ov.innerHTML = '<div class="pt-scroll"><div class="pt-in"><svg class="pt-svg" aria-hidden="true"></svg></div></div><div class="pt-head"></div>'
      + '<div class="pt-z"><button type="button" data-pt-z="in" aria-label="Zoom in" title="Zoom in (or the mouse wheel)">+</button><button type="button" data-pt-z="out" aria-label="Zoom out" title="Zoom out (or the mouse wheel)">−</button><button type="button" data-pt-z="fit" title="Fit the whole tree, You at the top">Fit</button></div>';
    bindView();
    itm.box.insertBefore(ov, itm.box.querySelector('.it-map-fb'));
    ov.addEventListener('pointerover', (ev) => { const b = ev.target.closest('[data-pt]'); const v = b ? Number(b.dataset.pt) : -1; if(v !== PT.hover){ PT.hover = v; light(); } });
    ov.addEventListener('pointerleave', () => { PT.hover = -1; light(); });
    ov.addEventListener('focusin', (ev) => { const b = ev.target.closest('[data-pt]'); PT.hover = b ? Number(b.dataset.pt) : -1; light(); });
    ov.addEventListener('focusout', () => { PT.hover = -1; light(); });
    ov.addEventListener('click', (ev) => { const z = ev.target.closest('[data-pt-z]'); if(z){ zoomBtn(z.dataset.ptZ); return; } if(PT.moved){ PT.moved = false; return; } const b = ev.target.closest('[data-pt]'); if(!b) return; const v = Number(b.dataset.pt); PT.pin = PT.pin === v || v === itm.home ? -1 : v; light(); });
    ov.addEventListener('keydown', (ev) => { if(ev.key === 'Escape' && PT.pin >= 0){ PT.pin = -1; light(); ev.stopPropagation(); } });
    return ov;
  }
  let G = null;   // the last tree drawn
  function draw(){
    if(typeof itm === 'undefined' || !itm.el || !itm.box || !itm.box.isConnected) return;   // no map box yet (list view, the first draw): nothing to draw over
    mount();
    const on = itm.filter === 'paths';
    ov.hidden = !on; itm.el.classList.toggle('pt-on', on);
    if(!on) return;
    G = build();
    ov.classList.add('pt-plain');
    // columns only as far out as the farthest report (an empty column says nothing)
    const phone = matchMedia('(max-width: 599px)').matches, W = itm.box.clientWidth, R = Math.max(1, ...[...G.nodes.values()].map(n => n.d)), inn = ov.querySelector('.pt-in'), svg = ov.querySelector('.pt-svg');
    const most = Math.max(1, ...G.L.map(l => l.length)), PAD = 12, HEAD = 46, FOOT = phone ? 64 : 56;
    // top down: You at the top, one row per jump, the farthest at the bottom (the owner: "your system at the top")
    // fixed sizes: the view (pan and zoom, not scrolling) fits it into the box
    const bh = 60, LAB = 70, gap = 14, rowH = 100, bw = 150;
    const width = PAD * 2 + LAB + most * bw + (most - 1) * gap, top0 = 16, ch = top0 + R * rowH + bh + 16;
    const place = (d, k, n) => [LAB + (width - LAB - (n * bw + (n - 1) * gap)) / 2 + k * (bw + gap), top0 + d * rowH];
    inn.style.width = width + 'px'; inn.style.height = ch + 'px'; G.cw = width; G.ch = ch;
    // row 1 spread evenly under You; each farther row sits under the systems it leads to (the average of their places), pushed apart
    // just enough not to overlap and kept inside the box
    const P = new Map(), step = bw + gap, lo = LAB + PAD, hi = width - PAD - bw;
    G.youX = place(0, 0, 1)[0] + bw / 2;
    G.L.forEach((list, d) => {
      if(d < 2){ list.forEach((i, k) => P.set(i, place(d, k, list.length))); return; }
      const want = list.map(i => { const to = [...G.edges.values()].filter(e => e.x === i).map(e => P.get(e.y)[0]); return [i, to.reduce((a, x) => a + x, 0) / to.length]; }).sort((a, b) => a[1] - b[1]);
      const xs = want.map(w => w[1]);
      for(let k = 1; k < xs.length; k++) xs[k] = Math.max(xs[k], xs[k - 1] + step);
      const over = xs.length ? xs[xs.length - 1] - hi : 0; if(over > 0) for(let k = xs.length - 1; k >= 0; k--){ xs[k] -= over; if(k && xs[k - 1] > xs[k] - step) xs[k - 1] = xs[k] - step; else break; }
      const under = xs.length ? lo - xs[0] : 0; if(under > 0) for(let k = 0; k < xs.length; k++) xs[k] = Math.max(xs[k], k ? xs[k - 1] + step : lo);
      want.forEach(([i], k) => P.set(i, [xs[k], top0 + d * rowH]));
    });
    // headings: jumps from you, at the left of each row (above it on a phone)
    let html = '';
    for(let d = 0; d <= R; d++){
      const y = top0 + d * rowH + bh / 2 - 7;
      html += `<div class="pt-col row" style="left:${PAD}px;top:${y}px;">${d === 0 ? 'You' : `${d} jump${d === 1 ? '' : 's'}`}</div>`;
    }
    const nh = G.src.length, RR = G.R;
    ov.querySelector('.pt-head').innerHTML = (nh ? `<b>${nh} system${nh === 1 ? '' : 's'}</b> with hostiles within ${RR} jump${RR === 1 ? '' : 's'} (${escapeHtml(scopeWord())})` : `No hostiles within ${RR} jump${RR === 1 ? '' : 's'} (${escapeHtml(scopeWord())})`)
      + `<span class="pt-hint"> · ${phone ? 'two fingers move and zoom' : 'drag to move · wheel to zoom'}</span>`;
    for(const n of G.nodes.values()){
      const [x, y] = P.get(n.i), r = itm.rep.get(n.i), me = n.i === itm.home, id = sysId(n.i), sc = secCls(n.i);
      const bad = r && (r.side === 'hostile' || r.side === 'neutral') && n.d <= R ? r : null;
      let sub = '';
      if(bad && bad.n > 0){
        const L = itLive(bad.st), ships = L.ships.map(s => s.n > 1 ? `${s.n}× ${s.name}` : s.name), who = L.pilots.filter(p => p.side !== 'f').length;
        const what = ships.length ? ships.join(', ') : `${bad.side === 'neutral' ? 'neutral' : 'hostile'}${bad.n === 1 ? '' : 's'}`;
        sub = `<span class="pt-sub"><b class="pt-n ${bad.side}">${bad.n}</b><span class="pt-w">${escapeHtml(what)}</span><span class="pt-age">${escapeHtml(itAgo(bad.t))}</span></span>`;
      }else if(me) sub = `<span class="pt-sub"><span class="pt-you">YOU</span></span>`;
      else sub = '';
      const tip = `${itSysName(id)} (${itMapSecText(itMapTable().sec[n.i])}) · ${n.d === 0 ? 'your system' : `${n.d} jump${n.d === 1 ? '' : 's'} from you`}`;
      html += `<button type="button" class="pt-b${me ? ' you' : ''}${bad ? ' ' + bad.side : ''}" data-pt="${n.i}" style="left:${x}px;top:${y}px;width:${bw}px;height:${bh}px" title="${escapeHtml(tip)}">`
        + `<span class="pt-t"><span class="it-sn s${sc}">${escapeHtml(itSysName(id))}</span></span>${sub}${tagsHtml(n.i)}</button>`;
    }
    // gate lines (toward you), thicker where more of them come through
    let paths = `<defs><marker id="ptArr" viewBox="0 0 8 8" refX="7" refY="4" markerUnits="userSpaceOnUse" markerWidth="9" markerHeight="9" orient="auto"><path d="M0 0L8 4L0 8z" fill="currentColor"/></marker></defs>`;
    for(const e of G.edges.values()){
      const [x1, y1] = P.get(e.x), [x2, y2] = P.get(e.y), heads = [...e.from].reduce((s, h) => s + (itm.rep.get(h) ? itm.rep.get(h).n : 1), 0);
      const w = Math.min(5, 1.4 + heads / 3).toFixed(1);
      // from the top of the farther system up to the bottom of the nearer one
      const ax = x1 + bw / 2, ay = y1, bx = x2 + bw / 2, by = y2 + bh;
      const d = `M${ax} ${ay}C${ax} ${(ay + by) / 2} ${bx} ${(ay + by) / 2} ${bx} ${by + 2}`;
      paths += `<path class="pt-e" data-x="${e.x}" data-y="${e.y}" d="${d}" stroke-width="${w}" marker-end="url(#ptArr)"/>`;
    }
    svg.setAttribute('width', inn.style.width); svg.setAttribute('height', inn.style.height); svg.innerHTML = paths;
    [...inn.querySelectorAll('.pt-b,.pt-col')].forEach(x => x.remove());
    svg.insertAdjacentHTML('afterend', html);
    // the view: kept while you look around; fitted again when you move, or the range, the routes or the layout change
    const fk = [itm.home, it.set.range, W].join('|');
    if(!PT.v || fk !== PT.fitKey){ PT.fitKey = fk; fit(); } else apply();
    light();
  }
  // ---- pan and zoom (the map's own rules: drag or the wheel with a mouse; two fingers on a touch screen, one finger scrolls the page) ----
  const K_MIN = 0.3, K_MAX = 2.5;
  function apply(){ const inn = ov.querySelector('.pt-in'), v = PT.v; inn.style.transform = `translate(${v.tx}px, ${v.ty}px) scale(${v.k})`; const zp = ov.querySelector('[data-pt-z="fit"]'); if(zp) zp.textContent = 'Fit'; }
  function fit(){
    const W = itm.box.clientWidth, H = itm.H, top = matchMedia('(max-width: 599px)').matches ? 84 : 34, foot = matchMedia('(max-width: 599px)').matches ? 64 : 56;
    const phone = matchMedia('(max-width: 599px)').matches, all = Math.min(1.2, (W - 16) / G.cw, (H - top - foot) / G.ch);
    // on a phone a whole wide tree would be too small to read: no smaller than 0.75, centred on You (two fingers to look around)
    const k = Math.max(K_MIN, phone ? Math.max(0.75, all) : all);
    PT.v = {k, tx: Math.round(G.cw * k <= W ? (W - G.cw * k) / 2 : W / 2 - G.youX * k), ty: top}; apply();
  }
  function zoomAt(x, y, f){ const v = PT.v, k = Math.max(K_MIN, Math.min(K_MAX, v.k * f)); v.tx = x - (x - v.tx) * k / v.k; v.ty = y - (y - v.ty) * k / v.k; v.k = k; apply(); }
  function zoomBtn(z){ if(z === 'fit') return fit(); const W = itm.box.clientWidth; zoomAt(W / 2, itm.H / 3, z === 'in' ? 1.25 : 0.8); }
  function bindView(){
    const vp = ov.querySelector('.pt-scroll'), pts = new Map(), at = (ev) => { const r = vp.getBoundingClientRect(); return [ev.clientX - r.left, ev.clientY - r.top]; };
    vp.addEventListener('wheel', (ev) => { ev.preventDefault(); const [x, y] = at(ev); zoomAt(x, y, Math.exp(-ev.deltaY * 0.0015)); }, {passive: false});
    vp.addEventListener('pointerdown', (ev) => {
      if(ev.pointerType === 'mouse' && ev.button !== 0) return;
      pts.set(ev.pointerId, at(ev)); PT.moved = false;
      if(ev.pointerType !== 'touch' || pts.size === 2){ PT.drag = {pts: new Map(pts), v: {...PT.v}}; }
    });
    vp.addEventListener('pointermove', (ev) => {
      if(!pts.has(ev.pointerId) || !PT.drag) return;
      pts.set(ev.pointerId, at(ev));
      const a = [...PT.drag.pts.values()], b = [...pts.values()], v0 = PT.drag.v;
      if(ev.pointerType === 'touch' && b.length >= 2 && a.length >= 2){   // two fingers: move by the midpoint, zoom by the spread
        const m0 = [(a[0][0] + a[1][0]) / 2, (a[0][1] + a[1][1]) / 2], m1 = [(b[0][0] + b[1][0]) / 2, (b[0][1] + b[1][1]) / 2];
        const s = Math.hypot(b[0][0] - b[1][0], b[0][1] - b[1][1]) / Math.max(1, Math.hypot(a[0][0] - a[1][0], a[0][1] - a[1][1]));
        const k = Math.max(K_MIN, Math.min(K_MAX, v0.k * s));
        PT.v = {k, tx: m1[0] - (m0[0] - v0.tx) * k / v0.k, ty: m1[1] - (m0[1] - v0.ty) * k / v0.k}; PT.moved = true; apply(); ev.preventDefault(); return;
      }
      if(ev.pointerType === 'touch') return;
      const [x0, y0] = a[0], [x1, y1] = b[0];
      if(!PT.moved && Math.hypot(x1 - x0, y1 - y0) < 4) return;
      if(!PT.moved){ PT.moved = true; try{ vp.setPointerCapture(ev.pointerId); }catch(e){ } vp.classList.add('drag'); }
      PT.v = {k: v0.k, tx: v0.tx + x1 - x0, ty: v0.ty + y1 - y0}; apply();
    });
    const end = (ev) => { pts.delete(ev.pointerId); if(pts.size < (ev.pointerType === 'touch' ? 2 : 1)){ PT.drag = null; vp.classList.remove('drag'); } };
    vp.addEventListener('pointerup', end); vp.addEventListener('pointercancel', end);
  }
  // trace: from the system pressed or under the pointer, every gate line toward you and back toward what feeds it, for the reported
  // systems whose routes go through it
  function light(){
    if(!ov || !G) return;
    const f = PT.hover >= 0 ? PT.hover : PT.pin, inn = ov.querySelector('.pt-in');
    inn.classList.toggle('pt-tr', f >= 0 && f !== itm.home);
    const keepN = new Set(), keepE = new Set();
    if(f >= 0 && f !== itm.home && G.nodes.has(f)){
      const hs = G.nodes.get(f).from, E = [...G.edges.values()].filter(e => [...e.from].some(h => hs.has(h)));
      const walk = (start, next) => { const st = [start]; while(st.length){ const x = st.pop(); if(keepN.has(x) && x !== start) continue; keepN.add(x); for(const e of E){ const [a, b] = next(e); if(a === x){ keepE.add(e.x + '>' + e.y); if(!keepN.has(b)) st.push(b); } } } };
      walk(f, (e) => [e.x, e.y]); walk(f, (e) => [e.y, e.x]);
    }
    for(const b of inn.querySelectorAll('.pt-b')){ const i = Number(b.dataset.pt); b.classList.toggle('lit', keepN.has(i)); b.setAttribute('aria-pressed', String(PT.pin === i)); }
    for(const p of inn.querySelectorAll('.pt-e')) p.classList.toggle('lit', keepE.has(p.dataset.x + '>' + p.dataset.y));
  }
  PT.draw = draw;
  const _draw = itMapDraw;
  itMapDraw = function(){ _draw(); try{ draw(); }catch(e){ console.error(e); } };
  const _leg = itMapFLegHtml;
  itMapFLegHtml = function(){ return itm.filter === 'paths' ? `<b>Paths to you</b> ${itMapSwHtml([itMapCol('--danger', '#c65b4e')])} hostile ${itMapSwHtml(['#b9c3ca'])} neutral · within ${range()} jumps (${escapeHtml(scopeWord())}) · lines point toward you` : _leg(); };
  const _legT = itMapFLegTitle;
  itMapFLegTitle = function(){ return itm.filter === 'paths' ? 'Every stargate route from a system with hostiles or neutrals inside the range to you; a system on several routes is shown once. Hover or press a system to trace its routes.' : _legT(); };

  // ---- MOCKUP bar (not part of the design) ----
  const bar = document.createElement('div'); bar.className = 'mkbar';
  bar.innerHTML = `<b>MOCKUP</b><span class="mkseg"><button type="button" data-mk="paths">Paths to you</button><button type="button" data-mk="sec">Security</button></span>
    <button type="button" data-mk="post">Post “L5-UWT Mk Raider Six Sabre”</button><button type="button" data-mk="jump">You jump to 8BA-RA</button>`;
  bar.addEventListener('click', (ev) => {
    const b = ev.target.closest('button'); if(!b) return;
    if(b.dataset.mk === 'post'){ window.__MKintel('Mk Gate Watcher', 'L5-UWT Mk Raider Six Sabre'); return; }
    if(b.dataset.mk === 'jump'){ window.__MKlocal('8BA-RA'); return; }
    if(typeof itm === 'undefined' || !itm.el){ const nv = document.querySelector('[data-it-nv="map"]'); if(nv) nv.click(); return; }   // the map isn't drawn yet (list view): show it first
    if(b.dataset.mk === 'paths' || b.dataset.mk === 'sec') itMapFilterSet(b.dataset.mk);
    if(b.dataset.mk === 'post') window.__MKintel('Mk Gate Watcher', 'L5-UWT Mk Raider Six Sabre');
    if(b.dataset.mk === 'jump') window.__MKlocal('8BA-RA');
  });
  const st = document.createElement('style');
  st.textContent = `
    .pt-ov{position:absolute; inset:0; z-index:1; background:#0c1014;} .pt-ov[hidden]{display:none;}
    .pt-scroll{position:absolute; inset:0; overflow:hidden; touch-action:pan-y; cursor:grab; user-select:none; -webkit-user-select:none;} .pt-scroll.drag{cursor:grabbing;} .pt-scroll.drag button.pt-b{cursor:grabbing;}
    .pt-in{position:relative; transform-origin:0 0;} .pt-svg{position:absolute; left:0; top:0; color:var(--danger); overflow:visible;}
    .it-map.pt-on .it-map-zoom, .it-map.pt-on .it-map-you, .it-map.pt-on .it-map-clr, .it-map.pt-on .it-map-help{display:none !important;}
    .pt-head{position:absolute; z-index:2; left:12px; top:8px; right:150px; pointer-events:none; font:400 12px var(--sans); color:var(--text-dim); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;} .pt-head b{color:var(--heading);} .pt-hint{color:var(--text-dim); opacity:.8;}
    .pt-z{position:absolute; z-index:2; right:8px; top:8px; display:flex; gap:4px;} .pt-z button{min-width:32px; height:32px; padding:0 8px; border:1px solid var(--line); border-radius:6px; background:rgba(12,16,20,.92); color:var(--heading); font:600 14px var(--sans);}
    @media (max-width:599px){ .pt-z button{min-width:44px; height:44px;} .pt-head{right:12px; top:58px;} }
    .pt-col{position:absolute; text-align:center; font:600 10.5px var(--sans); letter-spacing:.06em; text-transform:uppercase; color:var(--text-dim);} .pt-col.row{text-align:left;}
    .pt-e{fill:none; stroke:currentColor; opacity:.42;} .pt-tr .pt-e{opacity:.12;} .pt-tr .pt-e.lit{opacity:1;}
    button.pt-b{position:absolute; display:flex; flex-direction:column; justify-content:center; gap:2px; box-sizing:border-box; padding:4px 8px; margin:0; text-align:left; min-height:0;
      border:1px solid #2c3842; border-left:3px solid #2c3842; border-radius:6px; background:var(--panel-2, #151c22); color:var(--text); font:400 11.5px var(--sans); cursor:pointer; overflow:hidden;}
    button.pt-b.hostile{border-left-color:var(--danger);} button.pt-b.neutral{border-left-color:#b9c3ca;} button.pt-b.you{border-color:var(--cyan); border-left-color:var(--cyan);}
    button.pt-b:hover, button.pt-b:focus-visible{border-color:var(--heading);} button.pt-b[aria-pressed="true"]{outline:2px solid var(--heading); outline-offset:1px;}
    .pt-tr button.pt-b{opacity:.35;} .pt-tr button.pt-b.lit{opacity:1;}
    .pt-t{display:flex; align-items:baseline; gap:6px; min-width:0;} .pt-t .it-sn{font:700 12.5px var(--sans); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
    .pt-sec{font:600 10.5px var(--sans);} .pt-sec.s0{color:#8f2f69;} .pt-sec.s1{color:#6d221d;} .pt-sec.s2{color:#bb1014;} .pt-sec.s3{color:#ce4611;} .pt-sec.s4{color:#de6a0c;} .pt-sec.s5{color:#eeff83;} .pt-sec.s6{color:#71e452;} .pt-sec.s7{color:#62daa6;} .pt-sec.s8{color:#4acff3;} .pt-sec.s9{color:#389cf6;} .pt-sec.s10{color:#2e74df;}
    .pt-age{margin-left:auto; flex:0 0 auto; padding-left:2px; font:400 10.5px var(--sans); color:var(--text-dim); white-space:nowrap;} .pt-you{ font:700 10px var(--sans); color:var(--cyan); letter-spacing:.06em;}
    .pt-sub{display:flex; align-items:center; gap:4px; min-width:0; white-space:nowrap; color:var(--text);} .pt-w{overflow:hidden; text-overflow:ellipsis; min-width:0;} .pt-sub.dim{color:var(--text-dim);}
    .pt-n{display:inline-block; min-width:16px; padding:0 4px; border-radius:8px; text-align:center; font:700 10.5px var(--sans); color:#111; background:var(--danger);} .pt-n.neutral{background:#b9c3ca;}
    @media (max-width:599px){ button.pt-b{font-size:11px;} }
    .pt-tags{display:flex; flex-wrap:nowrap; justify-content:flex-start; gap:4px; min-width:0; overflow:hidden;} .pt-tags > *{margin-left:0 !important; flex:0 0 auto;}
    .pt-k{display:inline-block; font:700 10px/16px var(--sans); padding:0 6px; border-radius:3px; white-space:nowrap;}
    .pt-plain .pt-tags{justify-content:center; padding:0 4px; border-radius:4px; background:#0c1014;}
    /* round 3 (the owner: "gets rid of the pills and is just borderless for each system? system name centered, relevant data below it") */
    .pt-plain button.pt-b{border:0; background:transparent; align-items:center; text-align:center; padding:2px 4px; overflow:visible;}
    .pt-plain button.pt-b .pt-t{justify-content:center;} .pt-plain button.pt-b .pt-sub{justify-content:center;} .pt-plain .pt-w{flex:0 1 auto;}
    .pt-plain .pt-age{margin-left:4px;} .pt-plain .pt-age::before{content:'· ';}
    .pt-plain .pt-t, .pt-plain .pt-sub{padding:0 4px; border-radius:4px; background:#0c1014;}   /* the page's own map background: lines pass behind the words */
    .pt-plain .pt-t .it-sn{font-size:13.5px;} .pt-plain button.pt-b.you .pt-t .it-sn{text-decoration:underline; text-decoration-color:var(--cyan); text-underline-offset:3px;}
    .pt-plain button.pt-b:hover .it-sn, .pt-plain button.pt-b:focus-visible .it-sn{text-decoration:underline; text-underline-offset:3px;}
    .pt-plain button.pt-b[aria-pressed="true"]{outline:1px dashed var(--heading); outline-offset:2px;}
    .mkbar{position:fixed; left:8px; bottom:8px; z-index:9999; display:flex; flex-wrap:wrap; gap:6px; align-items:center; max-width:calc(100vw - 16px); box-sizing:border-box; padding:6px 8px; border-radius:6px; background:#3a2a10; border:1px solid var(--amber); font:12px var(--sans); color:var(--heading);}
    .mkbar b{color:var(--amber); letter-spacing:.5px;} .mkbar button{font-size:12px; padding:4px 8px; min-height:30px;} .mkseg{display:inline-flex; gap:4px; align-items:center;}
    .mkbar [aria-pressed="true"]{background:var(--amber); color:#111;}
    @media (max-width:599px){ .mkbar{max-height:30vh; overflow:auto;} .mkbar button{min-height:36px;} }`;
  document.head.appendChild(st); document.body.appendChild(bar);
})();
