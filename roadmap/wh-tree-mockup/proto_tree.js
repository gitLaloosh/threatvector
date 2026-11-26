// Prototype for the Wormholes map's tree, round 2 (Project doc claude/roadmap/wh-tree-layout-plan.md). TREE.mode 'new' replaces whLayout /
// whPlaces and adds the drag pin and the new-system view; 'today' puts the page's own back. Shortcuts the build must not copy: the functions
// swapped by name; the drag pin as extra canvas listeners (the build does it in whWireMap's own release); whSeen / whAddForm wrapped to see a
// new system (the build sets it where they add one).
(() => {
  const today = {whLayout: window.whLayout, whPlaces: window.whPlaces, whSeen: window.whSeen, whAddForm: window.whAddForm, whZoomBtn: window.whZoomBtn};
  const SP = {lr: {c: 150, r: 64}, tb: {c: 130, r: 84}};   // lr: depth across (columns of 150), rows of 64; tb: depth down (84), across 130 (today's phone)
  const GAP = 8, FLOOR = 0.7, FLIP = 1.25;   // FLOOR: the zoom whPaint already treats as readable (a fit under 0.7 centres you at 0.9)
  // the tree's shape: each chain (Home's first, the owner: "most branches are going to start from the home system in j-space"; else where you
  // started it: your first k-space entry, as today), breadth-first from its start; each system's depth and row; each one's parent (up)
  function shape(){
    const st = whState().st, ids = Object.keys(st.sys).map(Number), adj = new Map(ids.map(n => [n, []]));
    for(const l of st.links) if(adj.has(l.a) && adj.has(l.b)){ adj.get(l.a).push(l.b); adj.get(l.b).push(l.a); }
    const t = (n) => st.sys[n].t, seen = new Set(), dr = new Map(), up = new Map(), trees = [], home = whHomes()[0];
    const order = ids.slice().sort((a, b) => (a === home ? 0 : 1) - (b === home ? 0 : 1) || (whIsJ(a) ? 1 : 0) - (whIsJ(b) ? 1 : 0) || t(a) - t(b));
    let row = 0, maxd = 0;
    for(const r of order){
      if(seen.has(r)) continue;
      const kids = new Map(), dep = new Map([[r, 0]]), q = [r], bfs = [r]; seen.add(r);
      while(q.length){ const x = q.shift(), ks = []; for(const y of adj.get(x).slice().sort((p, s) => t(p) - t(s))) if(!seen.has(y)){ seen.add(y); dep.set(y, dep.get(x) + 1); maxd = Math.max(maxd, dep.get(y)); ks.push(y); q.push(y); bfs.push(y); up.set(y, x); } kids.set(x, ks); }
      const place = (x) => { const ks = kids.get(x); if(!ks.length){ dr.set(x, {d: dep.get(x), r: row++}); return; } ks.forEach(place); const rs = ks.map(k => dr.get(k).r); dr.set(x, {d: dep.get(x), r: (Math.min(...rs) + Math.max(...rs)) / 2}); };
      place(r); row += 0.5; trees.push(bfs);
    }
    return {dr, up, trees, rows: Math.max(1, row - 0.5), maxd};
  }
  const xy = (p, dir) => dir === 'lr' ? {x: p.d * SP.lr.c, y: p.r * SP.lr.r} : {x: p.r * SP.tb.c, y: p.d * SP.tb.r};
  // the direction (the owner: "Pick the direction (Recommended)"): whichever lets the whole tree fit the free part of the map at the larger zoom;
  // the one in use is kept until the other fits FLIP times better, so one hole doesn't turn the tree over; Rearrange picks afresh
  function fitOf(T, dir, v){
    const w = (dir === 'lr' ? T.maxd * SP.lr.c : (T.rows - 1) * SP.tb.c) + WH_NW, h = (dir === 'lr' ? (T.rows - 1) * SP.lr.r : T.maxd * SP.tb.r) + WH_NH;
    return Math.min((v.w - 40) / w, (v.h - 40) / h);
  }
  function pickDir(T, phone){
    const M = whS.M, v = whS.el && whS.el.isConnected ? whFree() : {w: phone ? 390 : 1400, h: 700}, cur = M.dir || (phone ? 'tb' : 'lr'), oth = cur === 'lr' ? 'tb' : 'lr';
    const fc = fitOf(T, cur, v), fo = fitOf(T, oth, v), d = TREE.force ? (fo > fc ? oth : cur) : (fo >= fc * FLIP ? oth : cur);
    TREE.force = false; M.dir = d; return d;
  }
  function layout(phone){ const T = shape(), d = pickDir(T, phone), out = new Map(); for(const [n, p] of T.dr) out.set(n, xy(p, d)); return out; }
  // where each system goes: one you placed (moved, locked, or pinned by a drag) where you put it, never moved by the page; every other one
  // grows from the nearest placed system above it in the tree, keeping its tree offset, however many jumps away; a chain's start with nothing
  // placed above it: its tree place, all chains shifted together by the first chain's start (Home's) when that one is placed; none on top of
  // another (the owner: "Nearest free row (Recommended)"): the next free row, its branch after it. The overlap test: a grid of boxes.
  function places(phone){
    const T = shape(), dir = pickDir(T, phone), A = new Map(), P = new Map(), cw = WH_NW + GAP, ch = WH_NH + GAP, G = new Map();
    for(const [n, p] of T.dr) A.set(n, xy(p, dir));
    const ck = (i, j) => i + ',' + j;
    const add = (n, p) => { P.set(n, p); const k = ck(Math.floor(p.x / cw), Math.floor(p.y / ch)); let L = G.get(k); if(!L) G.set(k, L = []); L.push(p); };
    const hits = (p) => { const i = Math.floor(p.x / cw), j = Math.floor(p.y / ch); for(let a = -1; a <= 1; a++) for(let b = -1; b <= 1; b++){ const L = G.get(ck(i + a, j + b)); if(L) for(const o of L) if(Math.abs(o.x - p.x) < cw && Math.abs(o.y - p.y) < ch) return true; } return false; };
    const st = dir === 'lr' ? {x: 0, y: SP.lr.r} : {x: SP.tb.c, y: 0};
    const free = (p) => { if(!hits(p)) return p; for(let k = 1; k <= 400; k++) for(const s of [k, -k]){ const c = {x: p.x + s * st.x, y: p.y + s * st.y}; if(!hits(c)) return c; } return p; };
    for(const n of A.keys()){ const q = whAt(n); if(q) add(n, {x: q[0], y: q[1]}); }
    const r0 = T.trees.length ? T.trees[0][0] : null, q0 = r0 !== null ? whAt(r0) : null, sh = q0 ? {x: q0[0] - A.get(r0).x, y: q0[1] - A.get(r0).y} : {x: 0, y: 0};
    for(const bfs of T.trees) for(const n of bfs){
      if(whAt(n)) continue;
      const u = T.up.get(n), a = A.get(n);
      add(n, free(u === undefined ? {x: a.x + sh.x, y: a.y + sh.y} : {x: P.get(u).x + a.x - A.get(u).x, y: P.get(u).y + a.y - A.get(u).y}));
    }
    return P;
  }
  // a drag moves only what you dragged (the owner: "i'd like to be able to move a system w/out it automatically moving any others"): every other
  // system the move would shift is pinned where it was (a place of its own, as if you'd put it there), so new holes then grow from them
  function pinAfterDrag(keys, was){
    // what the move itself would shift: the map laid out with the dragged systems where they were, then where you dropped them (anything else
    // that changed during the drag, a new hole say, is in both, so it pins nothing)
    const S = whS, now = new Map([...keys].map(n => [n, S.st.pos[n]]));
    keys.forEach((n, i) => { if(was[i]) S.st.pos[n] = was[i]; else delete S.st.pos[n]; });
    const P0 = places(S.M.phone);
    for(const [n, q] of now) S.st.pos[n] = q;
    const P1 = places(S.M.phone); let k = 0;
    for(const [n, p] of P1){ if(keys.has(n) || whAt(n)) continue; const o = P0.get(n); if(o && (Math.abs(o.x - p.x) > 0.5 || Math.abs(o.y - p.y) > 0.5)){ S.st.pos[n] = [Math.round(o.x), Math.round(o.y)]; k++; } }
    if(k) whSave();
    return k;
  }
  function wire(){
    const cv = whCv(); if(!cv || cv.__tr) return; cv.__tr = true; let rec = null;
    cv.addEventListener('pointerdown', () => { const M = whS.M, d = M.drag; rec = TREE.mode === 'new' && d && d.kind === 'move' && d.from.size ? {keys: new Set(d.from.keys()), pos: [...d.from.keys()].map(n => whS.st.pos[n] ? [...whS.st.pos[n]] : null)} : null; });
    cv.addEventListener('pointerup', () => { if(TREE.wait){ const w = TREE.wait; TREE.wait = null; TREE.last = showNew(w[0], w[1]); }   // held back by the drag
      const r = rec; rec = null; if(!r) return; if(JSON.stringify([...r.keys].map(n => whS.st.pos[n] || null)) === JSON.stringify(r.pos)) return;   // a click, not a drag
      TREE.pinned = pinAfterDrag(r.keys, r.pos); whS.drawKey = ''; whPaint(true); });
  }
  // a new system you caused (a jump, + Add) out of view (the owner: "Small zoom, floor, pan (Recommended)"): zoom out just enough to show it and the
  // system it connects to with what you see now; at the floor (FLOOR, names still readable), pan to them instead; never during a drag or a pinch
  function showNew(n, nb){
    const M = whS.M; if(!M || !M.cam || !M.P.has(n)) return 'none';
    if(M.drag || M.pinch){ TREE.wait = [n, nb]; return 'wait'; }
    if(whInView(n)) return 'in view';
    const v = whFree(), s0 = M.cam.s, pts = [n, nb].filter(x => x !== null && x !== undefined && M.P.has(x)).map(x => M.P.get(x));
    const a = whToWorld(v.l, v.t), b = whToWorld(v.r, v.b);
    const x0 = Math.min(a.x, ...pts.map(p => p.x)) - 12, y0 = Math.min(a.y, ...pts.map(p => p.y)) - 26, x1 = Math.max(b.x, ...pts.map(p => p.x + WH_NW)) + 12, y1 = Math.max(b.y, ...pts.map(p => p.y + WH_NH)) + 12;
    const s = Math.min(s0, v.w / (x1 - x0), v.h / (y1 - y0));
    if(s >= FLOOR){ M.cam = {x: (x0 + x1) / 2 - (v.l + v.w / 2) / s, y: (y0 + y1) / 2 - (v.t + v.h / 2) / s, s}; whDraw(); return 'zoom'; }
    const z = Math.min(s0, FLOOR), px0 = Math.min(...pts.map(p => p.x)), py0 = Math.min(...pts.map(p => p.y)), px1 = Math.max(...pts.map(p => p.x + WH_NW)), py1 = Math.max(...pts.map(p => p.y + WH_NH));
    const both = (px1 - px0) * z <= v.w - 24 && (py1 - py0) * z <= v.h - 24, c = both ? {x: (px0 + px1) / 2, y: (py0 + py1) / 2} : {x: M.P.get(n).x + WH_NW / 2, y: M.P.get(n).y + WH_NH / 2};
    M.cam = {x: c.x - (v.l + v.w / 2) / z, y: c.y - (v.t + v.h / 2) / z, s: z}; whDraw(); return 'pan';
  }
  window.TREE = {mode: 'new', layout, places, shape, showNew, today, pinned: 0, wait: null, force: false, last: null};
  window.whLayout = function(phone){ return TREE.mode === 'new' ? layout(phone) : today.whLayout(phone); };
  window.whPlaces = function(phone){ if(TREE.mode !== 'new') return today.whPlaces(phone); wire(); return places(phone); };
  window.whZoomBtn = function(b, a){ if(a === 'arr' && TREE.mode === 'new') TREE.force = true; return today.whZoomBtn(b, a); };
  // a jump: today's page centres you when you're out of view; the new rule keeps the system you came from in view too (zoom, floor, pan)
  window.whSeen = function(id, t, docked, who){
    const S = whState(), had = new Set(Object.keys(S.st.sys).map(Number)), prev = S.last, cam = S.M && S.M.cam ? {...S.M.cam} : null;
    today.whSeen(id, t, docked, who);
    if(TREE.mode !== 'new' || S.last === prev || had.has(S.last) || !cam) return;
    S.M.cam = cam; S.M.viewFor = S.last; whPaint(true); TREE.last = showNew(S.last, prev);
  };
  window.whAddForm = function(f){
    const S = whState(), had = new Set(Object.keys(S.st.sys).map(Number)), to = f.link && f.link.value ? Number(f.link.value) : null;
    today.whAddForm(f);
    if(TREE.mode !== 'new') return;
    const n = Object.keys(S.st.sys).map(Number).find(x => !had.has(x)); if(n === undefined) return;
    whPaint(true); TREE.last = showNew(n, to);
  };
})();
