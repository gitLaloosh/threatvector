"""The Intel map's "Paths to you" filter (build queue 043; Project doc roadmap/paths-to-you-plan.md, mockup Claude outputs/paths_to_you_mockup.html).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/paths_to_you_check.py [index.html]   -> 'FAILURES: N' (must be 0)

The owner: "a tree view of paths to you from reported hostiles within the "near you" alert range", then "alert range", "every shortest
route", top down with "pan and zoom rather than scrolling", borderless ("system name centered, relevant data below it"), "lose the security
status number" and "add badges for gate camps, ess and kills"; the button before Wormholes, beside its list button. At the build review:
the top line the count only, the map's drag help kept under the box, the count a 3 px tag (the tag rule). Uses intel_check.py's made-up
folder, mocks and names; the systems around 1DQ1-A have no loops, so you jump (a Local line) to a made-up area with one, its systems
named PTnn-Z here; every pilot and line is made up. The expected tree is worked out here from the jump table on its own. Checks:
  * the bar: seven filters, Paths to you just before Wormholes, the list button right after Wormholes; the name line;
  * the tree: exactly your system, the sources (a hostile or neutral report, or kills, within the alert range; a clear and a report past
    the alert range left out) and the systems on their shortest routes; exactly the gates on those routes; a system with two shortest
    routes has both gates;
  * top down: you at the top, every row lower than the one nearer you; no security number in a system's text (its hover has it);
  * under the names: the count a tag with 3-4 px corners (hostile kh, neutral kn), the ships or "hostiles"; YOU under your system;
    nothing under a system only on the way;
  * badges only where Intel has them: Camp (the gate in its hover) from camp words, ESS from "hacking the ess", "N kill(s)" from kills; no
    grey gate tag (a gate named without camp words);
  * the top line "N systems with hostiles"; the legend line "Paths to you ... within 4 jumps (your alert range)"; the map's zoom buttons
    and canvas hidden, its drag help still shown;
  * hover traces a source's routes (worked out here), and so does its Near You row; a press keeps it, Escape and a press on you clear it; + / − / Fit, the wheel, a
    drag (which presses nothing);
  * redrawn only when what it shows changed: map draws and refreshes with nothing new write nothing; a new report joins (once); a jump
    rebuilds from the new system; Security brings the map back;
  * the Intel example's picture drawn while it's on leaves it on;
  * the timings at the largest alert range (10, every system within it reported; LESSON #160): a build and a write, a build with
    nothing new (printed for the history doc; a write under 200 ms);
  * 390 px: the opened filter row of seven 44 px buttons inside the map box, Wormholes and its list button side by side; the tree's
    buttons 44 px; fitted no smaller than 0.75; no sideways scroll;
  * mutants, each must fail: one route per system; Near You's range for the alert range; the security number back; Wormholes no longer
    last; the tree written on every draw; the example's picture hiding it; the grey gate tag shown;
  * no page errors. v2026.11.12.4 fails (no Paths to you filter).
"""
import sys, os, re, json, time, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
_src = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
_src = _src[:_src.index('with sync_playwright() as p:')]
NS = {'__file__': os.path.join(HERE, 'intel_check.py'), '__name__': 'intel_check_prefix'}
exec(compile(_src, 'intel_check.py (first part)', 'exec'), NS)   # the made-up folder, mocks, names; its table checks run too
globals().update({k: v for k, v in NS.items() if not k.startswith('__') and k not in ('check', 'fails')})
from playwright.sync_api import sync_playwright
check = NS['check']
PAGE = open(HTML, encoding='utf-8').read()

# ---- a made-up area with a loop: the first system 8+ jumps from 1DQ1-A with a system 3 jumps out that has two nearer neighbours ----
R = 4   # the alert range set here
D0 = bfs(SYSID['1DQ1-A'])
def two_parents(d, s): return sum(1 for y in G[s] if d.get(y) == d[s] - 1) >= 2
HOME = next(h for h, v in sorted(D0.items(), key=lambda x: (x[1], x[0])) if v >= 8 and any(two_parents(bfs(h), s) for s, w in bfs(h).items() if w == 3))
DH = bfs(HOME)
AREA = sorted((s for s, v in DH.items() if v <= 7), key=lambda s: (DH[s], s))
for k, s in enumerate(AREA): SYSNAME[s] = f'PT{k:02d}-Z'   # NS's own dicts: the stand-in ESI answers these names
SYSID.update({SYSNAME[s]: s for s in AREA})
at = lambda d: [s for s in AREA if DH[s] == d]
TWO = next(s for s in at(3) if two_parents(DH, s))
S1 = at(1)[0]; NB1 = next(y for y in sorted(G[S1]) if y != HOME)       # a camp, on the gate to NB1
S2 = next(s for s in at(2) if s not in G[TWO])                          # hacking the ESS
S4 = next(s for s in at(4) if not any(DH[y] == 3 and y == TWO for y in G[s]))   # neutrals, and two kills
def route_nodes(h, d=DH):
    dh = bfs_limited(h, d[h]); return {x for x, v in dh.items() if x in d and d[x] + v == d[h]}
def bfs_limited(h, lim):
    dd = {h: 0}; q = [h]
    for x in q:
        if dd[x] >= lim: continue
        for y in G[x]:
            if y not in dd: dd[y] = dd[x] + 1; q.append(y)
    return dd
used = {HOME, S1, S2, TWO, S4} | route_nodes(S1) | route_nodes(S2) | route_nodes(TWO) | route_nodes(S4)
KO = next(s for s in at(2) if s not in used)                            # kills only, no report
used |= route_nodes(KO)
CLR = next(s for s in at(3) if s not in used)                           # reported clear: no source
FAR = at(5)[0]                                                          # past the alert range (inside Near You's)
NEW = next(s for s in at(4) if s not in used and s != S4 and not (route_nodes(s) & {CLR}))   # a later report
NBT = next(y for y in sorted(G[TWO]) if DH[y] == 2)                     # a gate named without camp words
HOST = M.PILOTS[M.pick(98000003, 0)][0]

def expect(srcs, d=DH, home=HOME):
    nodes, edges = {home}, set()
    for h in srcs:
        on = route_nodes(h, d); nodes |= on
        for x in on:
            for y in G[x]:
                if y in on and d[y] == d[x] - 1: edges.add((x, y))
    return nodes, edges
def lit_for(f, srcs, d=DH):
    hs = [h for h in srcs if f in route_nodes(h, d)]
    E = set()
    for h in hs: E |= expect([h], d)[1]
    keep = set()
    for nxt in ((lambda e: e), (lambda e: (e[1], e[0]))):
        st = [f]; seen = set()
        while st:
            x = st.pop()
            if x in seen: continue
            seen.add(x); keep.add(x)
            for e in E:
                a, b = nxt(e)
                if a == x and b not in seen: st.append(b)
    return keep
SRC = [S1, S2, TWO, S4, KO]

def start(b, html, w, errs, h=1000, touch=False):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch, device_scale_factor=2 if touch else 1)
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); route(ctx)
    pg = ctx.new_page(); pg.goto('file://' + html)
    pg.evaluate("(s) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({channels: ['region.intel'], me: 95000001, range: %d, sound: false, notify: false, forget: 15, hideFriendly: true})); }" % R, SIDE)
    pg.reload(); pg.wait_for_timeout(400)
    setup_logs(pg); W(pg, F_LOCAL_MAIN, line(time.time() - 600, 'EVE System', f'Channel changed to Local : {SYSNAME[HOME]}*'))
    pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg)
    t0 = time.time()
    W(pg, F_INTEL, line(t0, 'Scout Alt', f'{SYSNAME[S1]} 2 reds gate camp on {SYSNAME[NB1]} gate') + line(t0 + 1, 'Scout Alt', f'{SYSNAME[S2]} 3 reds hacking the ess')
      + line(t0 + 2, 'Gate Watcher', f'{SYSNAME[TWO]} {HOST} sabre on {SYSNAME[NBT]} gate') + line(t0 + 3, 'Gate Watcher', f'{SYSNAME[S4]} 2 neuts')
      + line(t0 + 4, 'Gate Watcher', f'{SYSNAME[CLR]} clr') + line(t0 + 5, 'Gate Watcher', f'{SYSNAME[FAR]} 5 reds'))
    tick(pg, 3200)
    pg.evaluate("""([ko, s4]) => { const mk = (id, sys, ago) => ({km: {killmail_id: id, killmail_time: new Date(Date.now() - ago).toISOString(), solar_system_id: sys,
        victim: {character_id: 91000045, corporation_id: 98000013, ship_type_id: 587}, attackers: [{character_id: 92000004, corporation_id: 98000013, ship_type_id: 22456, final_blow: true, damage_done: 100}]},
        z: {locationID: 40000123, totalValue: 2e7, attackerCount: 1, hash: 'x'}, t: Date.now() - ago});
      itAddKill(mk(9101, ko, 60000)); itAddKill(mk(9102, s4, 50000)); itAddKill(mk(9103, s4, 40000)); itRenderLists(); }""", [KO, S4])
    tick(pg, 1500)
    if touch and pg.query_selector('[data-it-nv="map"]'): pg.click('[data-it-nv="map"]'); tick(pg, 600)
    pg.evaluate("() => document.querySelector('#intelPanel .it-map-box').scrollIntoView({block: 'center'})"); pg.wait_for_timeout(200)
    return ctx, pg

TREE = """() => { const g = itGraphGet(), box = itm.box.getBoundingClientRect();
  return {nodes: [...document.querySelectorAll('.pt-ov .pt-b')].map(b => { const r = b.getBoundingClientRect(), n = b.querySelector('.pt-n');
      return {id: g.ids[Number(b.dataset.pt)], top: r.top, text: b.textContent, title: b.title, n: n ? [n.className, n.textContent, getComputedStyle(n).borderTopLeftRadius] : null,
        sub: (b.querySelector('.pt-sub') || {}).textContent || '', tags: [...b.querySelectorAll('.pt-tags > *')].map(x => [x.className, x.textContent, x.title]), lit: b.classList.contains('lit'), pressed: b.getAttribute('aria-pressed')}; }),
    edges: [...document.querySelectorAll('.pt-ov .pt-e')].map(p => [g.ids[Number(p.dataset.x)], g.ids[Number(p.dataset.y)]]),
    head: (document.querySelector('.pt-head') || {}).textContent, hidden: itPt.ov ? itPt.ov.hidden : true, home: g.ids[itm.home]}; }"""

def cases(b, html, parts=('bar', 'tree', 'look', 'badges', 'chrome', 'trace', 'view', 'redraw', 'example', 'time', 'phone')):
    out, errs = [], []
    ctx, pg = start(b, html, 1440, errs)
    if not pg.evaluate("IT_MAP_FILTERS.some(f => f.k === 'paths') && typeof itPtPaint === 'function'"):
        out.append('no Paths to you filter on the page'); ctx.close(); return out, errs
    if 'bar' in parts:
        o = pg.evaluate("() => [[...document.querySelectorAll('.it-map-fbtns [data-im-f]')].map(b => b.dataset.imF), (() => { const w = document.querySelector('[data-im-f=wh]'); return !!w.nextElementSibling && w.nextElementSibling.matches('[data-it-whl]'); })()]")
        if o != [['sec', 'jumps', 'region', 'reports', 'kills', 'paths', 'wh'], True]: out.append(f'the bar: {o} (want Paths to you just before Wormholes, the list button after it)')
    pg.click('[data-im-f="paths"]'); pg.wait_for_timeout(300)
    T = pg.evaluate(TREE)
    got_n = {x['id'] for x in T['nodes']}; got_e = {tuple(e) for e in T['edges']}
    want_n, want_e = expect(SRC)
    if 'tree' in parts:
        if T['hidden'] or T['home'] != HOME: out.append(f'the tree not shown, or not from your system ({T["hidden"]}, {T["home"]} vs {HOME})')
        if got_n != want_n: out.append(f'the systems: missing {sorted(SYSNAME[s] for s in want_n - got_n)}, extra {sorted(SYSNAME.get(s, s) for s in got_n - want_n)}')
        if got_e != want_e: out.append(f'the gates: missing {sorted((SYSNAME[a], SYSNAME[c]) for a, c in want_e - got_e)}, extra {sorted((SYSNAME.get(a, a), SYSNAME.get(c, c)) for a, c in got_e - want_e)}')
        if len([e for e in got_e if e[0] == TWO]) < 2: out.append(f'{SYSNAME[TWO]} has two shortest routes, the tree shows {len([e for e in got_e if e[0] == TWO])} gates from it')
        if FAR in got_n or CLR in got_n: out.append('a report past the alert range, or a clear, made a source')
    if 'look' in parts:
        by = {x['id']: x for x in T['nodes']}
        if HOME in by and any(by[s]['top'] <= by[HOME]['top'] for s in by if s != HOME): out.append('not top down: a system at or above yours')
        if any(by[a]['top'] >= by[c]['top'] for a in by for c in by if DH.get(a, 99) < DH.get(c, 99)): out.append('a row not below the one nearer you')
        sec = [x['id'] for x in T['nodes'] if re.search(r'-?\d\.\d', x['text'])]
        if sec: out.append(f'a security number in the tree: {[SYSNAME[s] for s in sec]}')
        if HOME in by and not re.search(r'\(-?\d\.\d\)', by[HOME]['title']): out.append(f'the hover lost the security number: {by[HOME]["title"]!r}')
        for s, cls in ((S1, 'kh'), (S2, 'kh'), (S4, 'kn')):
            n = by.get(s, {}).get('n')
            if not n or cls not in n[0].split() or n[2] not in ('3px', '4px'): out.append(f'{SYSNAME[s]}: the count {n} (want a {cls} tag, 3-4 px corners)')
        if not by.get(HOME) or 'YOU' not in by[HOME]['sub']: out.append('YOU not under your system')
        on_way = [s for s in got_n if s not in SRC and s != HOME]
        if any(by[s]['sub'] or by[s]['tags'] for s in on_way): out.append(f'something under a system only on the way: {[SYSNAME[s] for s in on_way if by[s]["sub"] or by[s]["tags"]]}')
    if 'badges' in parts:
        by = {x['id']: x for x in T['nodes']}
        tg = {SYSNAME[s]: [t[1] for t in by[s]['tags']] for s in by if by[s]['tags']}
        want = {SYSNAME[S1]: ['Camp'], SYSNAME[S2]: ['ESS'], SYSNAME[S4]: ['2 kills'], SYSNAME[KO]: ['1 kill']}
        if tg != want: out.append(f'the badges: {tg} (want {want})')
        camp = [t for t in by.get(S1, {}).get('tags', []) if t[1] == 'Camp']
        if not camp or SYSNAME[NB1] not in camp[0][2]: out.append(f'the Camp badge\'s hover doesn\'t name the gate: {camp}')
        if 'it-ess' not in (by.get(S2, {}).get('tags') or [['']])[0][0]: out.append(f'the ESS badge not the linked (red) one: {by.get(S2, {}).get("tags")}')
        if by.get(TWO, {}).get('tags'): out.append(f'a grey gate tag in the tree: {by[TWO]["tags"]}')
    if 'chrome' in parts:
        c = pg.evaluate("() => [document.querySelector('.pt-head').textContent, document.querySelector('.it-map-fl').textContent, getComputedStyle(itm.el.querySelector('.it-map-zoom')).display, getComputedStyle(itm.cv).visibility, getComputedStyle(itm.el.querySelector('.it-map-help.wide')).display, itm.el.querySelector('.it-map-fn').textContent]")
        if c[0] != f'{len(SRC)} systems with hostiles': out.append(f'the top line: {c[0]!r} (want "{len(SRC)} systems with hostiles")')
        if not c[1].startswith('Paths to you') or f'within {R} jumps (your alert range)' not in c[1]: out.append(f'the legend line: {c[1]!r}')
        if c[2] != 'none' or c[3] != 'hidden' or c[4] == 'none': out.append(f'the map under it: zoom {c[2]}, canvas {c[3]}, drag help {c[4]} (want none, hidden, shown)')
        if not c[5].startswith('Paths to you'): out.append(f'the name line: {c[5]!r}')
        # 048 (the owner: "search should not be visible on Paths to you filter/map mode."): hidden here, its list closed; back on other filters
        SB = "() => { const f = itm.el.querySelector('.it-rp-search'); return [getComputedStyle(f).display, f.querySelector('ul').hidden]; }"
        s0 = pg.evaluate(SB)
        pg.click('[data-im-f="sec"]'); pg.wait_for_timeout(200); s1 = pg.evaluate(SB)
        pg.fill('.it-rp-search input', SYSNAME[TWO][:2]); pg.wait_for_timeout(150); s2 = pg.evaluate(SB)
        pg.click('[data-im-f="paths"]'); pg.wait_for_timeout(250); s3 = pg.evaluate(SB)
        pg.evaluate("() => { itm.el.querySelector('.it-rp-search input').value = ''; }")
        if s0[0] != 'none' or s1[0] == 'none' or s2[1] or s3 != ['none', True]: out.append(f'the search box: on Paths {s0}, on Security {s1}, typed {s2}, back on Paths {s3} (want hidden, shown, its list open, hidden and closed)')
    if 'trace' in parts:
        ids = pg.evaluate("(a) => a.map(id => itGraphGet().at.get(id))", [S4, TWO, HOME])
        for f, i in ((S4, ids[0]), (TWO, ids[1])):
            pg.hover(f'.pt-b[data-pt="{i}"]'); pg.wait_for_timeout(150)
            lit = {x['id'] for x in pg.evaluate(TREE)['nodes'] if x['lit']}
            if lit != lit_for(f, SRC): out.append(f'hover {SYSNAME[f]}: lit {sorted(SYSNAME[s] for s in lit)} (want {sorted(SYSNAME[s] for s in lit_for(f, SRC))})')
        pg.mouse.move(5, 5); pg.hover(f'#itNearList > .it-nb[data-it-sys="{S4}"]'); pg.wait_for_timeout(200)   # a Near You row lights its system's routes
        lit = {x['id'] for x in pg.evaluate(TREE)['nodes'] if x['lit']}
        if lit != lit_for(S4, SRC): out.append(f'hover the Near You row of {SYSNAME[S4]}: lit {sorted(SYSNAME[s] for s in lit)}')
        pg.click(f'.pt-b[data-pt="{ids[0]}"]'); pg.mouse.move(5, 5); pg.wait_for_timeout(150)
        T2 = pg.evaluate(TREE); lit = {x['id'] for x in T2['nodes'] if x['lit']}; pr = [x['id'] for x in T2['nodes'] if x['pressed'] == 'true']
        if lit != lit_for(S4, SRC) or pr != [S4]: out.append(f'a press keeps the trace: lit {len(lit)}, pressed {[SYSNAME[s] for s in pr]}')
        pg.focus(f'.pt-b[data-pt="{ids[0]}"]'); pg.keyboard.press('Escape'); pg.wait_for_timeout(100); pg.evaluate("document.activeElement.blur()")
        if pg.evaluate("itPt.pin") != -1: out.append('Escape doesn\'t clear the press')
        pg.click(f'.pt-b[data-pt="{ids[0]}"]'); pg.click(f'.pt-b[data-pt="{ids[2]}"]'); pg.mouse.move(5, 5)
        if pg.evaluate("itPt.pin") != -1: out.append('a press on your system doesn\'t clear it')
    if 'view' in parts:
        k0 = pg.evaluate('itPt.v.k')
        pg.click('[data-pt-z="in"]'); k1 = pg.evaluate('itPt.v.k'); pg.click('[data-pt-z="out"]'); pg.click('[data-pt-z="out"]'); k2 = pg.evaluate('itPt.v.k'); pg.click('[data-pt-z="fit"]'); k3 = pg.evaluate('itPt.v.k')
        if not (k1 > k0 > k2) or abs(k3 - k0) > 1e-9: out.append(f'+ / − / Fit: {k0} -> {k1} -> {k2} -> {k3}')
        bx = pg.evaluate("(() => { const r = document.querySelector('.pt-vp').getBoundingClientRect(); return [r.left + r.width - 40, r.top + r.height - 70]; })()")
        y0 = pg.evaluate('scrollY'); pg.mouse.move(*bx); pg.mouse.wheel(0, -300); pg.wait_for_timeout(200)
        if pg.evaluate('itPt.v.k') <= k0 or pg.evaluate('scrollY') != y0: out.append('the wheel doesn\'t zoom, or the page scrolled')
        tx = pg.evaluate('itPt.v.tx'); pg.mouse.move(*bx); pg.mouse.down(); pg.mouse.move(bx[0] - 120, bx[1] + 10, steps=6); pg.mouse.up(); pg.wait_for_timeout(100)
        if abs(pg.evaluate('itPt.v.tx') - (tx - 120)) > 2 or pg.evaluate('itPt.pin') != -1: out.append('a drag doesn\'t move the tree, or it pressed a system')
        pg.click('[data-pt-z="fit"]')
    if 'redraw' in parts:
        p0 = pg.evaluate("() => { const p = itPt.paints; for(let k = 0; k < 5; k++){ itMapDraw(); itMapRefresh(); } return [p, itPt.paints]; }")
        if p0[0] != p0[1]: out.append(f'nothing new, yet the tree was written {p0[1] - p0[0]} times')
        W(pg, F_INTEL, line(time.time(), 'Scout Alt', f'{SYSNAME[NEW]} 3 reds')); tick(pg, 3200)
        T3 = pg.evaluate(TREE); n3 = {x['id'] for x in T3['nodes']}
        if n3 != expect(SRC + [NEW])[0]: out.append(f'a new report: the systems {sorted(SYSNAME[s] for s in n3 ^ expect(SRC + [NEW])[0])} differ')
        p1 = pg.evaluate("itPt.paints")
        if p1 - p0[1] < 1: out.append('a new report wasn\'t written')
        J = S1   # you jump one system out: the tree from there
        W(pg, F_LOCAL_MAIN, line(time.time(), 'EVE System', f'Channel changed to Local : {SYSNAME[J]}*')); tick(pg, 3200)
        T4 = pg.evaluate(TREE); dj = bfs(J)
        srcs = [s for s in SRC + [NEW, FAR] if dj[s] <= R]   # FAR may be inside the alert range from there
        n4, w4 = {x['id'] for x in T4['nodes']}, expect(srcs, dj, J)[0]
        if T4['home'] != J or n4 != w4: out.append(f'after a jump to {SYSNAME[J]}: home {SYSNAME.get(T4["home"])}, systems differ {sorted(SYSNAME.get(s, s) for s in n4 ^ w4)}')
        pg.click('[data-im-f="sec"]'); pg.wait_for_timeout(200)
        s = pg.evaluate("[itPt.ov.hidden, getComputedStyle(itm.cv).visibility, itm.el.classList.contains('pt-on')]")
        if s != [True, 'visible', False]: out.append(f'Security: the tree hidden, the map back {s}')
        pg.click('[data-im-f="paths"]'); pg.wait_for_timeout(200)
    if 'example' in parts:
        e = pg.evaluate("() => { itEx.map = null; itExMapPic(600); return [itm.filter, itPt.ov.hidden, itm.el.classList.contains('pt-on')]; }")
        if e != ['paths', False, True]: out.append(f'the Intel example\'s picture changed the tree: {e} (want paths, shown)')
    if 'time' in parts:   # the largest alert range (10) with a report in every system within it (LESSON #160): a build and a write, printed
        far = [x for x in AREA if 1 <= DH[x] <= 10] + [x for x, v in sorted(DH.items()) if 8 <= v <= 10 and x not in AREA]
        W(pg, F_INTEL, ''.join(line(time.time(), 'Scout Alt', f'{SYSNAME[x]} 2 reds') for x in far if x in AREA)); tick(pg, 3500)
        Tm = pg.evaluate("""() => { it.set.range = 10; itMapRefresh(true); const t = (f, n = 5) => { const a = performance.now(); for(let q = 0; q < n; q++) f(); return (performance.now() - a) / n; };
          const write = t(() => { itPt.html = ''; itPtPaint(); }), same = t(() => itPtPaint()); const G = itPt.G;
          it.set.range = %d; itMapRefresh(true); return {write, same, sources: G.src.length, nodes: G.nodes.size, edges: G.edges.size}; }""" % R)
        print(f"   timings at the largest alert range (10, {Tm['sources']} sources, {Tm['nodes']} systems, {Tm['edges']} gates): built and written {Tm['write']:.1f} ms, built and compared (nothing new) {Tm['same']:.1f} ms")
        if Tm['write'] > 200: out.append(f'the largest alert range: {Tm}')
    ctx.close()
    if 'phone' in parts:
        ctx, pg = start(b, html, 390, errs, h=844, touch=True)
        pg.tap('#intelPanel .it-map-fcur'); pg.wait_for_timeout(200)
        P = pg.evaluate("""() => { const box = itm.box.getBoundingClientRect(), bs = [...itm.box.querySelectorAll('[data-im-f], [data-it-whl]')].map(b => b.getBoundingClientRect());
          const w = itm.box.querySelector('[data-im-f=wh]').getBoundingClientRect(), l = itm.box.querySelector('[data-it-whl]').getBoundingClientRect();
          return [bs.length, bs.every(q => Math.round(q.width) === 44 && Math.round(q.height) === 44), bs.every(q => q.left >= box.left - 0.5 && q.right <= box.right + 0.5 && q.top >= box.top - 0.5 && q.bottom <= box.bottom + 0.5),
            Math.abs(w.top - l.top) < 1 && l.left > w.left && l.left - w.right < 8]; }""")
        if P != [8, True, True, True]: out.append(f'390 px: the opened row {P} (want 7 filters + the list button, 44 px, inside the box, Wormholes beside its list button)')
        pg.tap('#intelPanel [data-im-f="paths"]'); pg.wait_for_timeout(300)
        Q = pg.evaluate("() => [[...document.querySelectorAll('.pt-z button')].every(b => Math.round(b.getBoundingClientRect().height) === 44), itPt.v.k >= 0.75, !itPt.ov.hidden, document.scrollingElement.scrollWidth <= innerWidth + 1]")
        if Q != [True, True, True, True]: out.append(f'390 px: the tree {Q} (want 44 px buttons, fitted at 0.75 or more, shown, no sideways scroll)')
        ctx.close()
    return out, errs

MUTANTS = [
    ('the search box on Paths to you (048, the owner)', ", .it-map.pt-on .it-rp-search{display:none !important;}", "{display:none !important;}", ('chrome',)),
    ('one route per system', "      for(const y of T.adj[x]) if(on(y) && D[y] === D[x] - 1){ const k = x + '>' + y; (edges.get(k) || edges.set(k, {x, y, from: new Set()}).get(k)).from.add(h); }",
     "      { const y = T.adj[x].find(y => on(y) && D[y] === D[x] - 1); if(y !== undefined){ const k = x + '>' + y; (edges.get(k) || edges.set(k, {x, y, from: new Set()}).get(k)).from.add(h); } }", ('tree',)),
    ('Near You\'s range for the alert range', "  const D = itm.D, R = it.set.range, out = [];", "  const D = itm.D, R = itNearReach(), out = [];", ('tree',)),
    ('the security number back', '<span class="it-sn s${Number(itMapSecClass(T.sec[n.i]))}">${escapeHtml(name)}</span>', '<span class="it-sn s${Number(itMapSecClass(T.sec[n.i]))}">${escapeHtml(name)} ${escapeHtml(itMapSecText(T.sec[n.i]))}</span>', ('look',)),
    ('Wormholes no longer last', "function itMapFbtnsHtml(){ return IT_MAP_FILTERS.map(f =>", "function itMapFbtnsHtml(){ return [...IT_MAP_FILTERS.filter(f => f.k !== 'paths'), IT_MAP_FILTERS.find(f => f.k === 'paths')].map(f =>", ('bar',)),
    ('the tree written on every draw', "    if(text === itPt.html) return;   // written only when what it shows changed\n", "", ('redraw',)),
    ('the example\'s picture hiding it', "  if(itm.cv.parentNode === itm.box) itPtHide();\n", "  itPtHide();\n", ('example',)),
    ('the grey gate tag shown', "  if(short && cls === 'gt') return '';   // the tree shows camps only\n", "", ('badges',)),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, f"Paths to you: the bar, the tree around a made-up area ({len(expect(SRC)[0])} systems, {len(expect(SRC)[1])} gates; {SYSNAME[TWO]} two routes), its look, badges, trace, pan and zoom, redraws, the example, 390 px")
    check(not errs, f'no page errors {errs[:3]}')
    for name, old, new, parts in MUTANTS:
        if PAGE.count(old) != 1: check(False, f'mutant "{name}": its line isn\'t in the page once'); continue
        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f:
            f.write(PAGE.replace(old, new)); mp = f.name
        try:
            mo, me = cases(b, mp, parts)
            check(bool(mo) or bool(me), f'mutant "{name}" fails ({(mo or me or ["nothing"])[0][:90]})')
        finally: os.unlink(mp)
    b.close()
print('FAILURES:', NS['fails'])
sys.exit(1 if NS['fails'] else 0)
