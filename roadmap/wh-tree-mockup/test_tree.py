"""Checks for the Wormholes map tree mockup, round 2 (Project doc claude/roadmap/wh-tree-layout-plan.md).
    python3 -I test_tree.py <wh_tree_mockup.html> [--mutants <build_tree.py> <index.html> <mock.js>]
A fresh page per group, at 1440 and 390 px. Prints each failure and 'N of M checks pass'; with --mutants, each mutant must fail."""
import sys, os, subprocess, tempfile, shutil
from playwright.sync_api import sync_playwright

GEO = """() => { const M = whS.M, P = [...M.P.entries()], o = [], lk = [];
  for(let i = 0; i < P.length; i++) for(let j = i + 1; j < P.length; j++){ const a = P[i][1], b = P[j][1]; if(Math.abs(a.x - b.x) < WH_NW && Math.abs(a.y - b.y) < WH_NH) o.push([whName(P[i][0]), whName(P[j][0])]); }
  for(const l of whS.st.links){ const a = M.P.get(l.a), b = M.P.get(l.b); if(a && b) lk.push([whName(l.a), whName(l.b), Math.hypot(a.x - b.x, a.y - b.y)]); }
  return {over: o, links: lk, n: P.length, dir: M.dir}; }"""
AT = "(id) => { const p = whS.M.P.get(id); return p && [Math.round(p.x), Math.round(p.y)]; }"
ALL = "() => Object.fromEntries([...whS.M.P].map(([n, p]) => [n, [Math.round(p.x), Math.round(p.y)]]))"
# a system you didn't place is within one tree step of the system above it (a free-row push may add rows)
STEP = """(slack) => { const T = TREE.shape(), M = whS.M, bad = [], d = M.dir, c = d === 'lr' ? 150 : 130, r = d === 'lr' ? 64 : 84;
  for(const [n, u] of T.up) if(!whAt(n)){ const a = M.P.get(n), b = M.P.get(u), dd = Math.abs(T.dr.get(n).r - T.dr.get(u).r);
    const lim = d === 'lr' ? {x: c + 1, y: (dd + slack) * r + 1} : {x: (dd + slack) * c + 1, y: r + 1}; if(Math.abs(a.x - b.x) > lim.x || Math.abs(a.y - b.y) > lim.y) bad.push(whName(n)); } return bad; }"""

def run(b, html, w):
    out, n = [], [0]; ph = w < 600; tag = f'{w}:'
    def ck(ok, msg):
        n[0] += 1
        if not ok: out.append(f'{tag} {msg}')
    def page():
        ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': 844 if ph else 900}, has_touch=ph, is_mobile=ph)
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + html); pg.wait_for_function('window.__MKREADY || window.__MKERR', timeout=90000)
        ck(not pg.evaluate('window.__MKERR'), f"mockup started: {pg.evaluate('window.__MKERR')}")
        return ctx, pg, errs
    sc = lambda pg, s: (pg.evaluate(f"TRscene('{s}')"), pg.wait_for_timeout(350))
    k = 2 if ph else 1   # where the tree starts: left on a wide map (x), top on a phone (y)
    # 1. today's page shows the bug; the new one: 7 systems, no overlap, Home where it's locked, short links, the tree from Home
    ctx, pg, errs = page()
    sc(pg, 's7t'); g = pg.evaluate(GEO)
    ck(max(l[2] for l in g['links']) > 300, f"today: a connection runs far (the screenshot's bug): {max(l[2] for l in g['links']):.0f}")
    sc(pg, 's7n'); g = pg.evaluate(GEO); h = pg.evaluate('TJ.H')
    ck(not g['over'], f"7 new: no system on another: {g['over']}")
    ck(pg.evaluate(AT, h) == [420, 260], f"7 new: Home stays where it's locked: {pg.evaluate(AT, h)}")
    ck(max(l[2] for l in g['links']) <= 160, f"7 new: every connection one step of the tree: {max(l[2] for l in g['links']):.0f}")
    ps = pg.evaluate("() => [...whS.M.P.entries()].map(([n, p]) => [n, p.x, p.y])")
    ck(all(p[k] >= [q for q in ps if q[0] == h][0][k] for p in ps), f"7 new: the tree starts at Home ({'top' if ph else 'left'})")
    # 2. no Home: the chain starts where you started it (the first k-space entry, Rens); the locked system stays
    pg.evaluate("() => { delete whS.mk[TJ.H].st; whMkSave(); whS.drawKey = ''; whPaint(true); }"); pg.wait_for_timeout(200)
    ck(pg.evaluate("TREE.shape().trees[0][0]") == 30002510, 'no Home: the tree starts at the first k-space entry (Rens)')
    ck(pg.evaluate(AT, h) == [420, 260] and not pg.evaluate(GEO)['over'], 'no Home: the locked system stays; no system on another')
    ck(not errs, f'no page errors: {errs[:2]}'); ctx.close()
    # 3. 25 systems: landmarks set aside stay; each chain grows from its start; nothing on anything
    ctx, pg, errs = page()
    sc(pg, 's25n'); g = pg.evaluate(GEO)
    ck(g['n'] == 26 and not g['over'], f"25 new: 26 systems, none on another: {g['n']} {g['over']}")
    ck(pg.evaluate(AT, pg.evaluate('TJ.H')) == [300, 200] and pg.evaluate(AT, pg.evaluate('TJ.d3')) == [1120, 40] and pg.evaluate(AT, 30002510) == [-260, 40], '25 new: the locked landmarks stay where they are')
    ck(pg.evaluate(AT, pg.evaluate('TJ.b2')) == [560, 360], '25 new: the system you moved stays where you put it')
    bad = pg.evaluate(STEP, 2)
    ck(len(bad) <= 2, f"25 new: every system you didn't place sits one step from the one above it (free-row pushes allowed, at most 2 pushed further): {bad}")
    s1 = pg.evaluate(AT, pg.evaluate('TJ.s1'))
    ck(abs(s1[0] + 260) <= 150 and abs(s1[1] - 40) <= 84, f"25 new: the chain you scanned out of your k-space home grows from it: {s1}")
    # 4. a drag moves only what you dragged, during the drag and after; what it would have shifted is pinned; a new hole beyond it grows from it
    sc(pg, 's25n'); before = pg.evaluate(ALL); a2 = str(pg.evaluate('TJ.a2'))
    mid = pg.evaluate("""async () => { let snap = null; const d = [0, -260]; await TRdrag(TJ.a2, 60, -200, async () => { snap = Object.fromEntries([...whS.M.P].map(([n, p]) => [n, [Math.round(p.x), Math.round(p.y)]])); }); await new Promise(r => setTimeout(r, 200)); return snap; }""")
    after = pg.evaluate(ALL)
    ck(all(mid[x] == before[x] for x in before if x != a2), f"drag: during the drag nothing else moves: {[pg.evaluate('(n) => whName(+n)', x) for x in before if x != a2 and mid[x] != before[x]][:4]}")
    ck(mid[a2] != before[a2] and after[a2] != before[a2], 'drag: the dragged system moves')
    ck(all(after[x] == before[x] for x in before if x != a2), f"drag: after you let go nothing else has moved: {[pg.evaluate('(n) => whName(+n)', x) for x in before if x != a2 and after[x] != before[x]][:4]}")
    ck(pg.evaluate('TREE.pinned') > 0 and pg.evaluate("[TJ.b3, TJ.b4].every(n => !!whS.st.pos[n])"), f"drag: the systems it would have shifted are pinned (its branch): {pg.evaluate('TREE.pinned')}")
    ck(pg.evaluate("() => !whS.st.pos[TJ.a1] && !whS.st.pos[TJ.b1]"), 'drag: systems it would not have shifted are not pinned')
    nb = pg.evaluate("() => { const n = whTable().ids.find(x => whIsJ(x) && !whS.st.sys[x]); whAddSys(n); whAddLink(TJ.a2, n); whSave(); whS.drawKey = ''; whPaint(true); return whName(n); }")
    ck(nb not in pg.evaluate(STEP, 1), f"drag: a new hole beyond the dragged system grows beside it: {nb}")
    ck(not pg.evaluate(GEO)['over'], 'drag: no system on another')
    # 5. holes come and go: the tree closes up and makes room by itself; placed systems stay
    sc(pg, 's25n'); before = pg.evaluate(ALL)
    pg.evaluate("TRscene('churn')"); pg.wait_for_timeout(350); after = pg.evaluate(ALL); g = pg.evaluate(GEO)
    placed = pg.evaluate("() => Object.keys(whS.st.sys).filter(n => whAt(+n))")
    ck(all(after[x] == before[x] for x in placed if x in before), 'churn: every placed system stays where it is')
    ck(any(after[x] != before[x] for x in after if x in before and x not in placed), 'churn: the tree closes up (systems you did not place move)')
    ck(not g['over'] and len(pg.evaluate(STEP, 2)) <= 2, f"churn: none on another; each one step from the one above (at most 2 pushed further): {g['over']} {pg.evaluate(STEP, 2)}")
    # 6. Rearrange: places dropped, locked kept, nothing on anything
    sc(pg, 'arr'); g = pg.evaluate(GEO)
    ck(not g['over'], f"Rearrange: no system on another: {g['over']}")
    ck(pg.evaluate("Object.keys(whS.st.pos).every(n => whLocked(n))"), 'Rearrange: every place you moved (and every pin) is dropped')
    ck(pg.evaluate(AT, pg.evaluate('TJ.H')) == [300, 200] and pg.evaluate(AT, 30002510) == [-260, 40], 'Rearrange: the locked systems stay')
    ck(not errs, f'no page errors: {errs[:2]}'); ctx.close()
    # 7. the direction: a long chain runs across a wide map and down a phone; a bushy shallow one across on a phone; one more hole doesn't turn it over
    ctx, pg, errs = page()
    sc(pg, 'long'); ck(pg.evaluate('whS.M.dir') == ('tb' if ph else 'lr'), f"long chain: {'top to bottom on a phone' if ph else 'left to right'}: {pg.evaluate('whS.M.dir')}")
    sc(pg, 'bushy'); ck(pg.evaluate('whS.M.dir') == 'lr', f"bushy chain: left to right: {pg.evaluate('whS.M.dir')}")
    if ph:
        pg.evaluate("() => { whS.M.dir = 'tb'; const n = whTable().ids.find(x => whIsJ(x) && !whS.st.sys[x]); whAddSys(n); whAddLink(TJ.H, n); whSave(); whS.drawKey = ''; whPaint(true); }"); pg.wait_for_timeout(150)
        ck(pg.evaluate('whS.M.dir') == 'lr', 'bushy on a phone: top to bottom fits far worse, so it turns')
        sc(pg, 'long'); pg.evaluate("() => { whS.M.dir = 'lr'; whS.drawKey = ''; whPaint(true); }")
        ck(pg.evaluate('whS.M.dir') == 'tb', 'long on a phone: left to right fits far worse, so it turns')
    else:
        pg.evaluate("() => { whS.M.dir = 'tb'; whS.drawKey = ''; whPaint(true); }"); pg.wait_for_timeout(150)
        ck(pg.evaluate('whS.M.dir') == 'tb', 'bushy, wide map: neither fits 1.25 times better, so the one in use stays')
    # 8. a new system out of view: a small zoom out (never under the floor), else a pan; it ends in view; never during a drag
    sc(pg, 'nearNew'); r = pg.evaluate("() => ({last: TREE.last, s: whS.M.cam.s, inv: whInView(TJ.n2)})")
    ck(r['last'] in ('zoom', 'pan') and r['inv'] and r['s'] >= 0.7 - 1e-9, f"new hole out of view: brought into view, zoom at least 0.7: {r}")
    if not ph: ck(r['last'] == 'zoom' and r['s'] < 1.1, f"new hole out of view, wide map: a small zoom out: {r}")
    sc(pg, 'farNew'); r = pg.evaluate("() => ({last: TREE.last, s: whS.M.cam.s, inv: whInView(TJ.n3)})")
    ck(r['inv'] and r['s'] >= 0.7 - 1e-9, f"new hole far out of view: in view, never under the floor: {r}")
    sc(pg, 's25n')
    r = pg.evaluate("""async () => { const S = whS; S.last = TJ.e1; S.lastT = Date.now() - 5e3; whS.M.cam.s = 1.25; whCenter(TJ.s3); whDraw(); let during = null, cam = null;
      await TRdrag(TJ.c1, 0, 30, async () => { cam = JSON.stringify(whS.M.cam); const n = whTable().ids.find(x => whIsJ(x) && !whS.st.sys[x]); whSeen(n, Date.now()); during = {last: TREE.last, same: JSON.stringify(whS.M.cam) === cam}; window.TJ.n4 = n; });
      await new Promise(r => setTimeout(r, 100)); return {during, after: TREE.last, inv: whInView(TJ.n4)}; }""")
    ck(r['during'] and r['during']['last'] == 'wait' and r['during']['same'], f"a new hole during a drag: the view waits: {r['during']}")
    ck(r['after'] in ('zoom', 'pan', 'in view') and r['inv'], f"a new hole during a drag: shown after you let go: {r}")
    # 9. 1,000 systems: placing them is quick (the grid)
    ms = pg.evaluate("() => { TRbig(); const t = []; for(let i = 0; i < 5; i++){ const a = performance.now(); TREE.places(whS.M.phone); t.push(performance.now() - a); } t.sort((a, b) => a - b); return t[2]; }")
    ck(ms < 50, f"1,000 systems placed in under 50 ms: {ms:.1f} ms")
    ck(pg.evaluate("document.documentElement.scrollWidth <= innerWidth"), 'no sideways scroll')
    ck(not errs, f'no page errors: {errs[:2]}'); ctx.close()
    return out, n[0]

def cases(html):
    out, n = [], 0
    with sync_playwright() as p:
        b = p.chromium.launch()
        for w in (1440, 390):
            o, k = run(b, html, w); out += o; n += k
        b.close()
    return out, n

MUTANTS = [
    ("one hop only (today's placing)", "window.whPlaces = function(phone){ if(TREE.mode !== 'new') return today.whPlaces(phone); wire(); return places(phone); };",
     "window.whPlaces = function(phone){ wire(); return today.whPlaces(phone); };"),
    ('no free row', "const free = (p) => { if(!hits(p)) return p;", "const free = (p) => { return p;"),
    ('the tree not starting at Home', "(a === home ? 0 : 1) - (b === home ? 0 : 1) || ", ''),
    ('a system not following the placed one above it', "add(n, free(u === undefined ? {x: a.x + sh.x, y: a.y + sh.y} : {x: P.get(u).x + a.x - A.get(u).x, y: P.get(u).y + a.y - A.get(u).y}));",
     "add(n, free({x: a.x + sh.x, y: a.y + sh.y}));"),
    ('a drag pins nothing (its branch follows it)', "if(k) whSave();\n    return k;", "return 0;"),
    ('the direction never chosen', "TREE.force = false; M.dir = d; return d;", "TREE.force = false; M.dir = cur; return cur;"),
    ('a new system never brought into view', "if(M.drag || M.pinch){ TREE.wait = [n, nb]; return 'wait'; }", "return 'none';"),
    ('the view moved during a drag', "if(M.drag || M.pinch){ TREE.wait = [n, nb]; return 'wait'; }", ''),
]

if __name__ == '__main__':
    out, n = cases(os.path.abspath(sys.argv[1]))
    for o in out: print('FAIL', o)
    print(f'{n - len(out)} of {n} checks pass')
    if '--mutants' in sys.argv:
        i = sys.argv.index('--mutants'); build, idx, mock = sys.argv[i + 1:i + 4]
        here = os.path.dirname(os.path.abspath(build)); src = open(os.path.join(here, 'proto_tree.js'), encoding='utf-8').read()
        for name, a, b in MUTANTS:
            assert src.count(a) == 1, ('mutant text not found once', name)
            d = tempfile.mkdtemp(); shutil.copy(build, d); shutil.copy(os.path.join(here, 'boot_tree.js'), d)
            open(os.path.join(d, 'proto_tree.js'), 'w', encoding='utf-8').write(src.replace(a, b))
            outp = os.path.join(d, 'm.html'); subprocess.run([sys.executable, '-I', os.path.join(d, 'build_tree.py'), idx, mock, outp], check=True, capture_output=True)
            mo, _ = cases(outp)
            print(('caught' if mo else 'MISSED'), name, f'({len(mo)} failures: {mo[0] if mo else ""})')
            shutil.rmtree(d)
