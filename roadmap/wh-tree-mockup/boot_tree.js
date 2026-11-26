// Seeds made-up chains (CCP's own wormhole systems picked by class from the page's table, never the owner's), opens the Wormholes tab and shows
// the MOCKUP bar. The k-space systems are Rens, Tama, Jita and C-J6MT. Landmarks are locked and set off to the side, as the owner keeps them
// ("outside of the big constantly changing tree of systems that are often deleted w/in 24hrs").
(() => {
  const wait = (f, ms = 30000) => new Promise((res, rej) => { const t0 = Date.now(); const k = () => { let v; try{ v = f(); }catch(e){ v = null; } if(v) res(v); else if(Date.now() - t0 > ms) rej(new Error('timeout')); else setTimeout(k, 100); }; k(); });
  const K = {rens: 30002510, tama: 30002813, jita: 30000142, cj: 30000772};
  const used = new Set();
  const J = (cls) => { const T = whTable(); for(let i = 0; i < T.ids.length; i++) if(T.cls[i] === cls && /^J\d{6}$/.test(T.names[i]) && !used.has(T.ids[i]) && i % 7 === 3){ used.add(T.ids[i]); return T.ids[i]; } return null; };
  function reset(){
    const S = whState(); S.st = whBlank(); S.mk = {}; S.sel = null; S.last = null; S.lastT = 0; S.pn = {};
    if(S.M){ S.M.group.clear(); S.M.cam = null; S.M.dir = null; }
    TREE.pinned = 0; TREE.last = null;
    const m = S.el && S.el.querySelector('.wh-msg'); if(m) m.textContent = '';   // the last scene's message
  }
  let T0 = 0, I = 0;
  const L = (a, b) => { whAddSys(a, T0 + I * 60e3); whAddSys(b, T0 + I * 60e3 + 1); whAddLink(a, b, T0 + I * 60e3); I++; };
  function finish(you, marks, moved){
    const S = whS;
    for(const [id, m] of Object.entries(marks)) S.mk[id] = m;
    for(const [id, p] of Object.entries(moved)) S.st.pos[id] = p;
    S.last = you; S.lastT = Date.now() - 60e3; S.sel = you;
    whSave(); whMkSave(); S.drawKey = '';
  }
  // seven systems, the shape of the owner's screenshot (not its systems): in from highsec through two C2s into a C4 Home, locked and set aside;
  // out of Home a C5 to a C3 to lowsec
  function seven(){
    used.clear(); reset(); T0 = Date.now() - 20 * 3600e3; I = 0;
    const H = J('4'), X1 = J('5'), X2 = J('2'), X3 = J('2'), X4 = J('3');
    L(K.rens, X3); L(X3, X2); L(X2, H); L(H, X1); L(X1, X4); L(X4, K.tama);
    Object.assign(whLinkOf(H, X1), {mass: 'critical'});
    finish(H, {[H]: {st: 'home', tag: 'HOME', lock: true, at: [420, 260]}}, {});
    window.TJ = {H, X1, X2, X3, X4};
  }
  // twenty-five: the J-space Home (C3) locked and set aside, its branches, a loop; landmarks set aside: the k-space home (Rens, locked, where you
  // clone after a death) and a target (locked, deep in the chain); one system you moved; and a chain you scanned out of Rens after a death,
  // not joined to Home's
  function twentyFive(){
    used.clear(); reset(); T0 = Date.now() - 30 * 3600e3; I = 0;
    const H = J('3'), a1 = J('5'), a2 = J('2'), b1 = J('6'), b2 = J('5'), b3 = J('2'), b4 = J('1'), c1 = J('4'), c2 = J('6'), c4 = J('3'), c5 = J('4'), c6 = J('1'), c7 = J('2'), c8 = J('5');
    const d1 = J('4'), d2 = J('5'), d3 = J('5'), e1 = J('3'), e2 = J('2'), s1 = J('1'), s2 = J('2'), s3 = J('3');
    L(K.jita, H); L(H, a1); L(H, a2); L(a1, b1); L(a1, b2); L(b1, c1); L(b1, c2); L(c2, c8); L(b2, K.tama); L(a2, b3); L(a2, b4);
    L(b3, c4); L(b3, c5); L(c5, d1); L(d1, d2); L(d2, d3); L(d3, e1); L(d3, e2); L(e1, K.cj); L(b4, c6); L(c6, c7); L(c7, c4);
    L(K.rens, s1); L(s1, s2); L(s2, s3);
    finish(b3, {[H]: {st: 'home', tag: 'HOME', lock: true, at: [300, 200]}, [d3]: {st: 'target', tag: 'TGT', lock: true, at: [1120, 40]},
      [K.rens]: {st: 'friendly', tag: 'K-HOME', lock: true, at: [-260, 40]}}, {[b2]: [560, 360]});
    window.TJ = {H, a1, a2, b1, b2, b3, b4, c1, c2, c4, c5, c6, c8, d1, d2, d3, e1, s1, s2, s3};
  }
  // a long chain, no branches (13 holes from Home), and a bushy one (Home, 6 branches of 4 each): the direction each width picks
  function longChain(){ used.clear(); reset(); T0 = Date.now() - 10 * 3600e3; I = 0; const H = J('2'); let p = H; for(let i = 0; i < 13; i++){ const n = J(String(1 + i % 6)); L(p, n); p = n; } finish(p, {[H]: {st: 'home', tag: 'HOME', lock: true, at: [0, 0]}}, {}); window.TJ = {H, end: p}; }
  function bushy(){ used.clear(); reset(); T0 = Date.now() - 10 * 3600e3; I = 0; const H = J('5'); for(let i = 0; i < 6; i++){ const a = J(String(1 + i % 6)); L(H, a); for(let k = 0; k < 4; k++) L(a, J(String(1 + (i + k) % 6))); } finish(H, {[H]: {st: 'home', tag: 'HOME', lock: true, at: [0, 0]}}, {}); window.TJ = {H}; }
  // a drag scripted on the canvas, as a person would: press on the system's box, move, let go
  window.TRdrag = async (id, dx, dy, mid) => {
    const cv = whCv(), M = whS.M, r = cv.getBoundingClientRect(), p = M.P.get(id), s = M.cam.s;
    const x0 = r.left + (p.x + WH_NW / 2 - M.cam.x) * s, y0 = r.top + (p.y + WH_NH / 2 - M.cam.y) * s;
    const ev = (type, x, y) => cv.dispatchEvent(new PointerEvent(type, {bubbles: true, clientX: x, clientY: y, pointerId: 7, pointerType: 'mouse', button: 0, buttons: type === 'pointerup' ? 0 : 1}));
    ev('pointerdown', x0, y0);
    for(let k = 1; k <= 6; k++){ ev('pointermove', x0 + dx * s * k / 6, y0 + dy * s * k / 6); await new Promise(r => setTimeout(r, 16)); }
    if(mid) await mid();
    ev('pointerup', x0 + dx * s, y0 + dy * s);
  };
  // 1,000 systems (WH_SYS_MAX): a long trunk with a branch of 3 every few systems, a few placed (the timing check)
  window.TRbig = () => { reset(); const T = whTable(), ids = T.ids.filter(n => whIsJ(n)).slice(0, WH_SYS_MAX), t0 = Date.now() - 50 * 3600e3; let k = 0, trunk = ids[0];
    whAddSys(ids[0], t0); for(let i = 1; i < ids.length; i++){ const n = ids[i], par = i % 4 === 0 ? trunk : ids[i - 1]; whAddSys(n, t0 + i); whAddLink(par, n, t0 + i); if(i % 4 === 0) trunk = n; }
    whS.mk[ids[0]] = {st: 'home', lock: true, at: [0, 0]}; for(let i = 50; i < ids.length; i += 97) whS.st.pos[ids[i]] = [i * 3, -400]; whSave(); whMkSave(); whS.drawKey = ''; return ids.length; };
  const look = (s, n) => { const M = whS.M; M.cam.s = s; whCenter(n); whDraw(); };
  const scenes = {
    s7t(){ TREE.mode = 'today'; seven(); }, s7n(){ TREE.mode = 'new'; seven(); },
    s25t(){ TREE.mode = 'today'; twentyFive(); }, s25n(){ TREE.mode = 'new'; twentyFive(); },
    async drag(){ TREE.mode = 'new'; twentyFive(); switchTab('wh'); whPaint(true); const M = whS.M, a = M.P.get(TJ.a2), v = whFree(), inV = (x, y) => { const sx = (a.x + x - M.cam.x) * M.cam.s, sy = (a.y + y - M.cam.y) * M.cam.s; return sx >= v.l + 8 && sy >= v.t + 8 && sx + WH_NW * M.cam.s <= v.r - 8 && sy + WH_NH * M.cam.s <= v.b - 80; };
      const d = [[260, 0], [0, -260], [-260, 0], [0, 260], [420, 0], [0, -420], [-420, 0], [180, -180], [-180, -180]].find(([x, y]) => inV(x, y) && ![...M.P].some(([n, p]) => n !== TJ.a2 && Math.abs(p.x - a.x - x) < WH_NW + 8 && Math.abs(p.y - a.y - y) < WH_NH + 8)) || [0, -260]; window.TJ.dd = d; await TRdrag(TJ.a2, d[0], d[1]); const n = J('4'); whAddSys(n); whAddLink(TJ.a2, n); whSave(); whS.drawKey = ''; whPaint(true); window.TJ.n1 = n; whMsg('Dragged one system: nothing else moved. Then a new hole beyond it grew from where you put it.'); },
    churn(){ TREE.mode = 'new'; twentyFive(); switchTab('wh'); whPaint(true); whRemoveIds([TJ.b1, TJ.c1, TJ.c2, TJ.c8]); const x = J('2'), y = J('4'); whAddSys(x); whAddLink(TJ.b4, x); whAddSys(y); whAddLink(TJ.b4, y); whSave(); whS.drawKey = ''; whPaint(true); window.TJ.x = x; whMsg('A branch collapsed and two new holes opened: the tree closed up and made room by itself; the systems you placed stayed.'); },
    long(){ TREE.mode = 'new'; longChain(); }, bushy(){ TREE.mode = 'new'; bushy(); },
    nearNew(){ TREE.mode = 'new'; twentyFive(); switchTab('wh'); whPaint(true); look(1.1, TJ.H); const S = whS; S.last = TJ.c4; S.lastT = Date.now() - 5e3; const n = J('6'); whSeen(n, Date.now()); window.TJ.n2 = n; },
    farNew(){ TREE.mode = 'new'; twentyFive(); switchTab('wh'); whPaint(true); look(1.25, TJ.s3); const S = whS; S.last = TJ.e1; S.lastT = Date.now() - 5e3; const n = J('6'); whSeen(n, Date.now()); window.TJ.n3 = n; },
    arr(){ TREE.mode = 'new'; whZoomBtn(document.createElement('button'), 'arr'); },
  };
  const LABEL = {s7t: '7 · today', s7n: '7 · new', s25t: '25 · today', s25n: '25 · new', drag: 'Drag one system', churn: 'Holes come and go', long: 'Long chain', bushy: 'Bushy chain', nearNew: 'New hole out of view', farNew: '…far out of view', arr: 'Rearrange as a tree'};
  window.TRscene = async (k) => { await scenes[k](); if(!['arr', 'drag', 'churn', 'nearNew', 'farNew'].includes(k)){ switchTab('wh'); whPaint(true); } document.querySelectorAll('#trBar [data-s]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.s === k))); window.TRnow = k; };
  function bar(){
    const b = document.createElement('div'); b.id = 'trBar';
    b.innerHTML = '<b>MOCKUP</b>' + Object.entries(LABEL).map(([k, v]) => `<button type="button" data-s="${k}">${v}</button>`).join('') + '<button type="button" class="tr-fold" data-s="fold" aria-label="Fold the bar">⇕</button>';
    b.addEventListener('click', (e) => { const s = e.target.closest('button') && e.target.closest('button').dataset.s; if(!s) return; if(s === 'fold'){ b.classList.toggle('fold'); return; } TRscene(s); });
    const st = document.createElement('style');
    st.textContent = '#trBar{position:fixed; left:8px; bottom:8px; z-index:9999; display:flex; flex-wrap:wrap; gap:6px; align-items:center; max-width:calc(100vw - 16px); padding:6px 8px; background:#1d2a33; border:1px dashed #d99a3c; border-radius:6px; font:12px system-ui, sans-serif; color:#eef2f4}'
      + '#trBar b{color:#d99a3c} #trBar button{min-height:30px; padding:2px 8px; background:#0f1419; color:#eef2f4; border:1px solid #5b6773; border-radius:4px; cursor:pointer} #trBar button[aria-pressed="true"]{border-color:#4fc3d9; color:#4fc3d9}'
      + '#trBar.fold button:not(.tr-fold){display:none} @media (max-width:600px){ #trBar button{min-height:44px} }';
    document.head.appendChild(st); document.body.appendChild(b);
    if(innerWidth < 600) b.classList.add('fold');
  }
  (async () => { try{
    await wait(() => document.querySelector('#tabBtnWh') && typeof whState === 'function');
    switchTab('wh');
    await wait(() => whS && whS.el && whS.el.isConnected);
    await itLoadNames().catch(() => {});
    bar(); await TRscene('s25n');
    await new Promise(r => setTimeout(r, 400));
    window.__MKREADY = true;
  }catch(e){ window.__MKERR = String(e && e.stack || e); } })();
})();
