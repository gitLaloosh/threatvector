"""The Wormholes map's tree (build queue 073; roadmap/wh-tree-layout-plan.md, mockup Claude outputs/wh_tree_mockup.html, its tests
roadmap/wh-tree-mockup/test_tree.py). The owner: "we need to fix this so the tree is drawn efficiently and easy to read", at the review "ideally, i'd
like to be able to move a system w/out it automatically moving any others", and his answers "Home, else k-space entry (Recommended)", "Nearest free
row (Recommended)", "Auto-tidy, drag pins (Recommended)", "Small zoom, floor, pan (Recommended)", "Pick the direction (Recommended)".

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/wormhole_tree_check.py [index.html]   -> 'FAILURES: N' (must be 0)

Made-up chains only: CCP's wormhole systems picked by class from the page's own table (INTEL_WH), four k-space systems by ID; no pilots or groups.
intel_check.py's stand-ins answer ESI. At 1440 and 390 px, a fresh page per group:
  * 7 systems, Home locked off to the side: none on another; Home where it's locked; every connection one tree step; the tree starts at Home;
    Home's status off: the chain starts at the first k-space entry, the locked system stays;
  * 25 systems (Home, a target and the k-space home locked and set aside, one moved, a loop, a chain scanned out of the k-space home): none on
    another; every placed one where it was; each tree system within a tree step of the one above it (at most two pushed further by free rows);
    the k-space chain beside the k-space home;
  * a drag with the mouse: during it and after the release nothing but the dragged system moves; its branch is pinned (a place in tvWhChain.pos),
    systems it wouldn't shift aren't; a new hole off the dragged system grows beside it; none on another;
  * holes come and go: placed systems stay, tree systems move (closed up), none on another;
  * Rearrange: none on another, every move and pin dropped, locked kept;
  * the direction: a long chain left to right on a wide map, top to bottom on a phone; a bushy one left to right; the 1.25 rule;
  * a new hole out of view (a jump): in view after, the zoom never under 0.7, a small zoom out on a wide map; one arriving during a drag leaves the
    view alone until the release, then shows;
  * 074: three landmarks connected to nothing (locked, set aside) don't change the direction after Rearrange (the owner's shape: left to right on a
    wide map) and stay where they were put; with no Home they don't move the tree;
  * 1,000 systems (WH_SYS_MAX) placed in under 50 ms; no sideways scroll; no page errors.
Mutants, each must fail: a system not following the placed one above it (before 073: one jump only); no free row; the tree not starting at Home;
a drag that pins nothing; the direction never chosen; a new system never brought into view; the view moved during a drag; Rearrange keeping moves;
074: landmarks counted in the direction; the shift taken from a landmark.
"""
import sys, os, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
_src = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
_src = _src[:_src.index('with sync_playwright() as p:')]
NS = {'__file__': os.path.join(HERE, 'intel_check.py'), '__name__': 'intel_check_prefix'}
exec(compile(_src, 'intel_check.py (first part)', 'exec'), NS)   # HTML, route (stand-ins for ESI and zKillboard), check
globals().update({k: v for k, v in NS.items() if not k.startswith('__') and k not in ('check', 'fails')})
from playwright.sync_api import sync_playwright
check = NS['check']
PAGE = open(HTML, encoding='utf-8').read()

# the chains (as the mockup's boot_tree.js): seeded straight into the tab's state, saved, drawn
SEEDS = r"""() => {
  const K = {rens: 30002510, tama: 30002813, jita: 30000142, cj: 30000772}, used = new Set();
  const J = (cls) => { const T = whTable(); for(let i = 0; i < T.ids.length; i++) if(T.cls[i] === cls && /^J\d{6}$/.test(T.names[i]) && !used.has(T.ids[i]) && i % 7 === 3){ used.add(T.ids[i]); return T.ids[i]; } return null; };
  const reset = () => { const S = whState(); S.st = whBlank(); S.mk = {}; S.sel = null; S.last = null; S.lastT = 0; S.pn = {}; S.showNew = null; if(S.M){ S.M.group.clear(); S.M.cam = null; S.M.dir = null; } used.clear(); };
  let T0 = 0, I = 0;
  const L = (a, b) => { whAddSys(a, T0 + I * 60e3); whAddSys(b, T0 + I * 60e3 + 1); whAddLink(a, b, T0 + I * 60e3); I++; };
  const finish = (you, marks, moved) => { const S = whS; for(const [id, m] of Object.entries(marks)) S.mk[id] = m; for(const [id, p] of Object.entries(moved)) S.st.pos[id] = p;
    S.last = you; S.lastT = Date.now() - 60e3; S.sel = you; whSave(); whMkSave(); S.drawKey = ''; whPaint(true); };
  window.CK = {
    seven(){ reset(); T0 = Date.now() - 20 * 3600e3; I = 0; const H = J('4'), X1 = J('5'), X2 = J('2'), X3 = J('2'), X4 = J('3');
      L(K.rens, X3); L(X3, X2); L(X2, H); L(H, X1); L(X1, X4); L(X4, K.tama); finish(H, {[H]: {st: 'home', tag: 'HOME', lock: true, at: [420, 260]}}, {}); window.TJ = {H, X1, X2, X3, X4}; },
    twentyFive(){ reset(); T0 = Date.now() - 30 * 3600e3; I = 0;
      const H = J('3'), a1 = J('5'), a2 = J('2'), b1 = J('6'), b2 = J('5'), b3 = J('2'), b4 = J('1'), c1 = J('4'), c2 = J('6'), c4 = J('3'), c5 = J('4'), c6 = J('1'), c7 = J('2'), c8 = J('5');
      const d1 = J('4'), d2 = J('5'), d3 = J('5'), e1 = J('3'), e2 = J('2'), s1 = J('1'), s2 = J('2'), s3 = J('3');
      L(K.jita, H); L(H, a1); L(H, a2); L(a1, b1); L(a1, b2); L(b1, c1); L(b1, c2); L(c2, c8); L(b2, K.tama); L(a2, b3); L(a2, b4);
      L(b3, c4); L(b3, c5); L(c5, d1); L(d1, d2); L(d2, d3); L(d3, e1); L(d3, e2); L(e1, K.cj); L(b4, c6); L(c6, c7); L(c7, c4); L(K.rens, s1); L(s1, s2); L(s2, s3);
      finish(b3, {[H]: {st: 'home', tag: 'HOME', lock: true, at: [300, 200]}, [d3]: {st: 'target', tag: 'TGT', lock: true, at: [1120, 40]}, [K.rens]: {st: 'friendly', tag: 'K-HOME', lock: true, at: [-260, 40]}}, {[b2]: [560, 360]});
      window.TJ = {H, a1, a2, b1, b2, b3, b4, c1, c2, c4, c5, c6, c8, d1, d2, d3, e1, s1, s2, s3}; },
    long(){ reset(); T0 = Date.now() - 10 * 3600e3; I = 0; const H = J('2'); let p = H; for(let i = 0; i < 13; i++){ const n = J(String(1 + i % 6)); L(p, n); p = n; } finish(p, {[H]: {st: 'home', lock: true, at: [0, 0]}}, {}); window.TJ = {H}; },
    bushy(){ reset(); T0 = Date.now() - 10 * 3600e3; I = 0; const H = J('5'); for(let i = 0; i < 6; i++){ const a = J(String(1 + i % 6)); L(H, a); for(let k = 0; k < 4; k++) L(a, J(String(1 + (i + k) % 6))); } finish(H, {[H]: {st: 'home', lock: true, at: [0, 0]}}, {}); window.TJ = {H}; },
    big(){ reset(); const ids = whTable().ids.filter(n => whIsJ(n)).slice(0, WH_SYS_MAX), t0 = Date.now() - 50 * 3600e3; let trunk = ids[0];
      whAddSys(ids[0], t0); for(let i = 1; i < ids.length; i++){ const n = ids[i], par = i % 4 === 0 ? trunk : ids[i - 1]; whAddSys(n, t0 + i); whAddLink(par, n, t0 + i); if(i % 4 === 0) trunk = n; }
      whS.mk[ids[0]] = {st: 'home', lock: true, at: [0, 0]}; for(let i = 50; i < ids.length; i += 97) whS.st.pos[ids[i]] = [i * 3, -400]; whSave(); whMkSave(); whS.drawKey = ''; return ids.length; },
    lm(marks, home = true){ reset(); T0 = Date.now() - 3 * 3600e3; I = 0;   // 074: Home locked with branches (5 tree leaves, 4 deep), landmarks set aside
      const H = J('4'), a = J('5'), b = J('2'), c = J('2'), d = J('4'), e = J('3'), f = J('5'), g = J('3');
      L(H, a); L(a, b); L(H, c); L(c, d); L(d, K.tama); L(d, e); L(e, K.rens); L(H, f); L(H, g);
      const mk = home ? {[H]: {st: 'home', lock: true, at: [600, 300]}} : {};
      if(marks) [[30000772, [1300, -100]], [30000142, [1300, 0]], [30004759, [1300, 100]]].forEach(([n, at]) => { whAddSys(n, T0 - 9e5); mk[n] = {lock: true, at}; });
      finish(H, mk, {}); window.TJ = {H, a, c}; },
    fresh(){ return whTable().ids.find(x => whIsJ(x) && !whS.st.sys[x]); },
    look(s, n){ const M = whS.M; M.cam.s = s; whCenter(n); whDraw(); },
    you(from){ const S = whS; S.last = from; S.lastT = Date.now() - 5e3; S.youNew = false; S.who = 0; S.M.viewFor = from; },   // you're in `from` (not a fresh start: 063)
    jump(from, s, at){ CK.you(from); CK.look(s, at); const n = CK.fresh(); whSeen(n, Date.now()); return n; },
    pt(id){ const M = whS.M, r = whCv().getBoundingClientRect(), p = M.P.get(id); return [r.left + (p.x + WH_NW / 2 - M.cam.x) * M.cam.s, r.top + (p.y + WH_NH / 2 - M.cam.y) * M.cam.s]; },
  };
  return true; }"""
GEO = """() => { const M = whS.M, P = [...M.P.entries()], o = [], lk = [];
  for(let i = 0; i < P.length; i++) for(let j = i + 1; j < P.length; j++){ const a = P[i][1], b = P[j][1]; if(Math.abs(a.x - b.x) < WH_NW && Math.abs(a.y - b.y) < WH_NH) o.push([whName(P[i][0]), whName(P[j][0])]); }
  for(const l of whS.st.links){ const a = M.P.get(l.a), b = M.P.get(l.b); if(a && b) lk.push(Math.hypot(a.x - b.x, a.y - b.y)); }
  return {over: o, maxLink: Math.max(0, ...lk), n: P.length}; }"""
AT = "(id) => { const p = whS.M.P.get(id); return p && [Math.round(p.x), Math.round(p.y)]; }"
ALL = "() => Object.fromEntries([...whS.M.P].map(([n, p]) => [n, [Math.round(p.x), Math.round(p.y)]]))"
STEP = """(slack) => { const T = whLayout(whS.M.phone), M = whS.M, bad = [], sp = WH_SP[T.dir];
  for(const [n, u] of T.up) if(!whAt(n)){ const a = M.P.get(n), b = M.P.get(u), dd = Math.abs(T.dr.get(n).r - T.dr.get(u).r);
    const lim = T.dir === 'lr' ? {x: sp.c + 1, y: (dd + slack) * sp.r + 1} : {x: (dd + slack) * sp.c + 1, y: sp.r + 1}; if(Math.abs(a.x - b.x) > lim.x || Math.abs(a.y - b.y) > lim.y) bad.push(whName(n)); } return bad; }"""

def start(b, html, w, errs):
    phone = w < 600
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': 844 if phone else 900}, has_touch=phone, is_mobile=phone)
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    route(ctx)
    pg = ctx.new_page(); pg.goto('file://' + html); pg.wait_for_timeout(300)
    pg.evaluate("() => { localStorage.removeItem('tvWhChain'); localStorage.removeItem('tvWhMarks'); localStorage.removeItem('tvWhPanels'); }"); pg.reload(); pg.wait_for_timeout(300)
    pg.evaluate("() => switchTab('wh')"); pg.wait_for_timeout(300)
    pg.evaluate("() => document.querySelector('.wh-box').scrollIntoView({block: 'start'})"); pg.wait_for_timeout(150)
    pg.evaluate(SEEDS)
    return ctx, pg

def seed(pg, k): pg.evaluate(f"() => CK.{k}()"); pg.wait_for_timeout(250)

def drag(pg, id_js, dx, dy, mid=None):   # the mouse on the system's box (brought into view first): press, move in steps, (mid), let go
    pg.evaluate(f"() => {{ whCenter({id_js}); whDraw(); }}")
    x, y = pg.evaluate(f"() => CK.pt({id_js})"); s = pg.evaluate("whS.M.cam.s")
    pg.mouse.move(x, y); pg.mouse.down()
    for k in range(1, 7): pg.mouse.move(x + dx * s * k / 6, y + dy * s * k / 6); pg.wait_for_timeout(16)
    r = mid() if mid else None
    pg.mouse.up(); pg.wait_for_timeout(200)
    return r

def run(b, html, w):
    out, errs = [], []; ph = w < 600; tag = f'{w}:'
    def ck(ok, msg):
        if not ok: out.append(f'{tag} {msg}')
    k = 2 if ph else 1
    # 1. seven systems, Home locked and set aside
    ctx, pg = start(b, html, w, errs)
    seed(pg, 'seven'); g = pg.evaluate(GEO); h = pg.evaluate('TJ.H')
    ck(not g['over'], f"7: no system on another: {g['over']}")
    ck(pg.evaluate(AT, h) == [420, 260], f"7: Home stays where it's locked: {pg.evaluate(AT, h)}")
    ck(g['maxLink'] <= 160, f"7: every connection one step of the tree (before 073 one ran far): {g['maxLink']:.0f}")
    ps = pg.evaluate("() => [...whS.M.P.entries()].map(([n, p]) => [n, p.x, p.y])")
    ck(all(p[k] >= [q for q in ps if q[0] == h][0][k] for p in ps), f"7: the tree starts at Home ({'top' if ph else 'left'})")
    pg.evaluate("() => { delete whS.mk[TJ.H].st; whMkSave(); whS.drawKey = ''; whPaint(true); }"); pg.wait_for_timeout(150)
    ck(pg.evaluate("whLayout(whS.M.phone).trees[0][0]") == 30002510, 'no Home: the chain starts at the first k-space entry')
    ck(pg.evaluate(AT, h) == [420, 260] and not pg.evaluate(GEO)['over'], 'no Home: the locked system stays; none on another')
    ctx.close()
    # 2. twenty-five, a drag, holes coming and going, Rearrange
    ctx, pg = start(b, html, w, errs)
    seed(pg, 'twentyFive'); g = pg.evaluate(GEO)
    ck(g['n'] == 26 and not g['over'], f"25: 26 systems, none on another: {g['n']} {g['over']}")
    ck(pg.evaluate(AT, pg.evaluate('TJ.H')) == [300, 200] and pg.evaluate(AT, pg.evaluate('TJ.d3')) == [1120, 40] and pg.evaluate(AT, 30002510) == [-260, 40], '25: the locked landmarks stay where they are')
    ck(pg.evaluate(AT, pg.evaluate('TJ.b2')) == [560, 360], '25: the system you moved stays where you put it')
    bad = pg.evaluate(STEP, 2)
    ck(len(bad) <= 2, f"25: each tree system one step from the one above it (at most 2 pushed further by free rows): {bad}")
    s1 = pg.evaluate(AT, pg.evaluate('TJ.s1'))
    ck(abs(s1[0] + 260) <= 150 and abs(s1[1] - 40) <= 84, f"25: the chain scanned out of the k-space home grows from it: {s1}")
    seed(pg, 'twentyFive'); before = pg.evaluate(ALL); a2 = str(pg.evaluate('TJ.a2')); pos0 = pg.evaluate("Object.keys(whS.st.pos).length")
    mid = drag(pg, 'TJ.a2', 60, -200, lambda: pg.evaluate(ALL)); after = pg.evaluate(ALL)
    ck(mid[a2] != before[a2] and after[a2] != before[a2], 'drag: the dragged system moves')
    ck(all(mid[x] == before[x] for x in before if x != a2), f"drag: during the drag nothing else moves: {[x for x in before if x != a2 and mid[x] != before[x]][:4]}")
    ck(all(after[x] == before[x] for x in before if x != a2), f"drag: after you let go nothing else has moved: {[x for x in before if x != a2 and after[x] != before[x]][:4]}")
    pg.evaluate("() => { whS.drawKey = ''; whPaint(true); }"); again = pg.evaluate(ALL)
    ck(all(again[x] == after[x] for x in after), 'drag: drawn again, still where they were (the pins hold)')
    ck(pg.evaluate("Object.keys(whS.st.pos).length") > pos0 + 1 and pg.evaluate("[TJ.b3, TJ.b4].every(n => !!whS.st.pos[n])"), f"drag: its branch is pinned: {pg.evaluate('Object.keys(whS.st.pos).length') - pos0 - 1} pins")
    ck(pg.evaluate("() => !whS.st.pos[TJ.a1] && !whS.st.pos[TJ.b1]"), 'drag: systems it would not have shifted are not pinned')
    nb = pg.evaluate("() => { const n = CK.fresh(); whAddSys(n); whAddLink(TJ.a2, n); whSave(); whS.drawKey = ''; whPaint(true); return whName(n); }")
    ck(nb not in pg.evaluate(STEP, 1), f"drag: a new hole beyond the dragged system grows beside it: {nb}")
    ck(not pg.evaluate(GEO)['over'], 'drag: none on another')
    seed(pg, 'twentyFive'); before = pg.evaluate(ALL)
    pg.evaluate("() => { whRemoveIds([TJ.b1, TJ.c1, TJ.c2, TJ.c8]); const x = CK.fresh(); whAddSys(x); whAddLink(TJ.b4, x); const y = CK.fresh(); whAddSys(y); whAddLink(TJ.b4, y); whSave(); whS.drawKey = ''; whPaint(true); }"); pg.wait_for_timeout(150)
    after = pg.evaluate(ALL); placed = pg.evaluate("() => Object.keys(whS.st.sys).filter(n => whAt(+n))")
    ck(all(after[x] == before[x] for x in placed if x in before), 'churn: every placed system stays where it is')
    ck(any(after[x] != before[x] for x in after if x in before and x not in placed), 'churn: the tree closes up (systems you did not place move)')
    ck(not pg.evaluate(GEO)['over'] and len(pg.evaluate(STEP, 2)) <= 2, f"churn: none on another; each one step from the one above: {pg.evaluate(STEP, 2)}")
    pg.evaluate("() => { whS.st.pos[TJ.a1] = [900, 700]; whSave(); whZoomBtn(document.createElement('button'), 'arr'); }"); pg.wait_for_timeout(200)
    ck(not pg.evaluate(GEO)['over'], f"Rearrange: none on another: {pg.evaluate(GEO)['over']}")
    ck(pg.evaluate("Object.keys(whS.st.pos).every(n => whLocked(n))"), 'Rearrange: every move and pin dropped')
    ck(pg.evaluate(AT, pg.evaluate('TJ.H')) == [300, 200] and pg.evaluate(AT, 30002510) == [-260, 40], 'Rearrange: the locked systems stay')
    ctx.close()
    # 3. the direction, a new hole's view, 1,000 systems
    ctx, pg = start(b, html, w, errs)
    arr = "() => { whZoomBtn(document.createElement('button'), 'arr'); return whS.M.dir; }"   # Rearrange picks the direction afresh (M.dirNew)
    pg.evaluate("() => CK.lm(false)"); pg.wait_for_timeout(200); d0 = pg.evaluate(arr)
    pg.evaluate("() => CK.lm(true)"); pg.wait_for_timeout(200); d1 = pg.evaluate(arr)
    ck(d1 == d0, f"074: landmarks connected to nothing don't change the direction (Rearrange): {d0} without, {d1} with")
    if not ph: ck(d1 == 'lr', f"074: the owner's shape with three landmarks, wide map: left to right after Rearrange: {d1}")
    ck(pg.evaluate("[30000772, 30000142, 30004759].every((n, i) => { const p = whS.M.P.get(n); return p && p.x === 1300 && p.y === [-100, 0, 100][i]; })"), '074: the landmarks stay where they were put')
    pg.evaluate("() => CK.lm(false, false)"); pg.wait_for_timeout(200); r0 = pg.evaluate(AT, 30002510)
    pg.evaluate("() => CK.lm(true, false)"); pg.wait_for_timeout(200); r1 = pg.evaluate(AT, 30002510)
    ck(r0 == r1, f"074: no Home, landmarks don't move the tree (the shift comes from the first chain the page lays out): {r0} without, {r1} with")
    seed(pg, 'long'); ck(pg.evaluate('whS.M.dir') == ('tb' if ph else 'lr'), f"long chain: {'top to bottom on a phone' if ph else 'left to right'}: {pg.evaluate('whS.M.dir')}")
    seed(pg, 'bushy'); ck(pg.evaluate('whS.M.dir') == 'lr', f"bushy chain: left to right: {pg.evaluate('whS.M.dir')}")
    if ph:
        pg.evaluate("() => { whS.M.dir = 'tb'; const n = CK.fresh(); whAddSys(n); whAddLink(TJ.H, n); whSave(); whS.drawKey = ''; whPaint(true); }")
        ck(pg.evaluate('whS.M.dir') == 'lr', 'bushy on a phone: top to bottom fits far worse, so it turns')
    else:
        pg.evaluate("() => { whS.M.dir = 'tb'; whS.drawKey = ''; whPaint(true); }")
        ck(pg.evaluate('whS.M.dir') == 'tb', 'bushy, wide map: neither fits 1.25 times better, so the one in use stays')
    seed(pg, 'twentyFive')
    r = pg.evaluate("() => { const n = CK.jump(TJ.c4, 1.1, TJ.H); return {s: whS.M.cam.s, inv: whInView(n), pend: !!whS.showNew}; }")
    ck(r['inv'] and r['s'] >= 0.7 - 1e-9 and not r['pend'], f"a jump into a new hole out of view: brought into view, zoom at least 0.7: {r}")
    if not ph: ck(r['s'] < 1.1, f"a jump into a new hole out of view, wide map: a small zoom out: {r}")
    seed(pg, 'twentyFive')
    r = pg.evaluate("() => { const n = CK.jump(TJ.e1, 1.25, TJ.s3); return {s: whS.M.cam.s, inv: whInView(n)}; }")
    ck(r['inv'] and r['s'] >= 0.7 - 1e-9, f"a jump into a new hole far out of view: in view, never under the floor: {r}")
    seed(pg, 'twentyFive'); pg.evaluate("() => { CK.you(TJ.e1); CK.look(1.25, TJ.c1); }")
    def during():
        cam = pg.evaluate("JSON.stringify(whS.M.cam)"); pg.evaluate("() => { window.TJ.n4 = CK.fresh(); whSeen(TJ.n4, Date.now()); }")
        return {'same': pg.evaluate("JSON.stringify(whS.M.cam)") == cam, 'pend': pg.evaluate("!!whS.showNew")}
    d = drag(pg, 'TJ.c1', 0, 30, during)
    ck(d['same'] and d['pend'], f"a new hole during a drag: the view waits for the release: {d}")
    ck(pg.evaluate("whInView(TJ.n4)") and not pg.evaluate("!!whS.showNew"), 'a new hole during a drag: shown after you let go')
    n = pg.evaluate("() => CK.big()"); ms = pg.evaluate("() => { const t = []; for(let i = 0; i < 5; i++){ const a = performance.now(); whPlaces(whS.M.phone); t.push(performance.now() - a); } t.sort((a, b) => a - b); return t[2]; }")
    ck(n == 1000 and ms < 50, f"1,000 systems placed in under 50 ms: {n}, {ms:.1f} ms")
    ck(pg.evaluate("document.documentElement.scrollWidth <= innerWidth"), 'no sideways scroll')
    ctx.close()
    return out, errs

def cases(b, html, widths=(1440, 390)):
    out, errs = [], []
    for w in widths:
        o, e = run(b, html, w); out += o; errs += e
    return out, errs

MUTANTS = [
    ('a system not following the placed one above it (one jump only, as before 073)', "add(n, free(u === undefined ? {x: a.x + sh.x, y: a.y + sh.y} : {x: P.get(u).x + a.x - A.get(u).x, y: P.get(u).y + a.y - A.get(u).y}));",
     "add(n, free({x: a.x + sh.x, y: a.y + sh.y}));", (1440,)),
    ('no free row', "const free = (p) => { if(!hits(p)) return p;", "const free = (p) => { return p;", (1440,)),
    ('the tree not starting at Home', "(a === home ? 0 : 1) - (b === home ? 0 : 1) || ", '', (1440,)),
    ('a drag that pins nothing', " if(d.from.size) whTreePin(d.from.keys(), d.was);", '', (1440,)),
    ('the direction never chosen', "M.dirNew = false; M.dir = d; return d;", "M.dirNew = false; M.dir = cur; return cur;", (390,)),
    ('a new system never brought into view', "const M = whS.M; if(!M.cam || !M.P.has(n) || whInView(n)) return;", "return;", (1440,)),
    ('the view moved during a drag', "if(S.showNew && !M.drag && !M.pinch){", "if(S.showNew){", (1440,)),
    ('074: landmarks counted in the direction (073\'s rule)', "    if(!bfs.some(n => !whAt(n))){ for(const n of bfs) dr.set(n, {d: dep.get(n), r: row}); continue; }\n", '', (1440,)),
    ('074: the shift taken from a landmark', "const t0 = T.trees.find(b => b.some(n => !whAt(n))), r0", "const t0 = T.trees[0], r0", (1440,)),
    ('Rearrange keeping moves', "S.st.pos = Object.fromEntries(Object.entries(S.st.pos).filter(([k]) => whLocked(k)));", "S.st.pos = {...S.st.pos};", (1440,)),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, 'the Wormholes map tree: placed systems, the tree from Home, drags, holes coming and going, the direction, new holes, 1440 / 390 px')
    check(not errs, f'no page errors {errs[:3]}')
    for name, old, new, widths in MUTANTS:
        if PAGE.count(old) != 1: check(False, f'mutant "{name}": its line isn\'t in the page once'); continue
        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f:
            f.write(PAGE.replace(old, new)); mp = f.name
        try:
            try: mo, me = cases(b, mp, widths)
            except Exception as e: mo, me = [f'the check stopped: {str(e).splitlines()[0]}'], []
            check(bool(mo) or bool(me), f'mutant "{name}" fails ({(mo or me or ["nothing"])[0][:90]})')
        finally: os.unlink(mp)
    b.close()
print('FAILURES:', NS['fails'])
sys.exit(1 if NS['fails'] else 0)
