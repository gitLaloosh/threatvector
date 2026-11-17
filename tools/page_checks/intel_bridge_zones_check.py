"""Threat Vector's route by Ansiblex zone (build queue 057; plan roadmap/ansiblex-zones-plan.md, mockup Claude outputs/ansiblex_zones_mockup.html).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/intel_bridge_zones_check.py [index.html]   -> 'FAILURES: N' (must be 0)

The owner: "generate routes that avoid using jump bridges outside of zone 1 if we're not jumping back into zone 1", "A setting with a checkbox
for each zone with only zone 1 turned on by default.", "Threat Vector's route only", "Both: login, then sov", "Leave out + warn on row", "At 5.00
LY"; for the map's counts "let's go with your recommendation" (change 11); at the build "maybe make them 70% of their current brightness".
Uses intel_check.py's made-up folder, mocks and names (you in 1DQ1-A) and its stand-in for ESI's /sovereignty/systems (SOV): a made-up answer
(alliance 99000001 holds everything near you, its capital your system; 99000002 holds one far system; one far system unclaimed) and five made-up
bridges picked from the map's own systems by gate jumps and the page's own light-years (itMapLy):
  b1 free both ways (both ends within 4.5 LY of the capital), b2 one-way (home end zone 1, far end zone 2), b3 zone 2 both ways (its near end up to 8 jumps out),
  b4 one end the other alliance's, b5 one end unclaimed.
Checks:
  * zones: itJbZoneOf at 0, 4.99, 5.00, 5.001, 10.00, 10.01, 15.01, 20.01, 25 LY; each direction's zone from its arrival (the expected zones
    worked out here from itMapLy, not from the page's tables); no capital: every direction zone 5, none used with zone 1 only;
  * usable: logged out, b4 "different alliances" and b5 "isn't held by any alliance" left out; logged in as Your pilot in 99000001, b4 "is held
    by"; a login with no alliance leaves every bridge out;
  * the route: to b1's far end by the free bridge (fewer jumps than by gate), its step line, "route:" (not "route by stargate:"), the menu's
    "1 by jump bridge", no "Threat Vector's route" line when it is the shortest over its own graph; b2 used only toward its home end (from its
    far end home in one jump); zone 2 ticked: both ways; every zone unticked: none; the switch off: stargate routes, no sov read;
  * the map's counts (change 11): before the answer every bridge counts (b4, b5 too); with it, b4 and b5 are left out and b3 (usable, zone 2)
    still counts; the answer arriving searches again; itm.Dg never changes; sovBridgeEnds() unchanged; the read runs with no zone ticked;
  * the read: one ask, none again before Expires, none with no bridge listed or the switch off; a failed read: ROUTE-02, back-off, no ask again
    at once; the address exactly IT_SOV_URL;
  * tvRouteJb: default [1], a bad value [1], kept after a reload, tvRoute's form unchanged; the Routes box's zone rows after the avoid list,
    the status line, a click on zone 2 saves and routes again;
  * the map: b4 / b5 dashed (D5), the colour #00a800; the hover on a bridge line (both directions, zones, the capital, how routes use it);
  * 1440 and 390 px (zone rows 44 px), no sideways scroll, no page errors; the Intel example asks nothing;
  * mutants, each must fail (see MUTANTS).
v2026.11.16.5 fails (no zones).
"""
import sys, os, re, json, time, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
_src = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
_src = _src[:_src.index('with sync_playwright() as p:')]
NS = {'__file__': os.path.join(HERE, 'intel_check.py'), '__name__': 'intel_check_prefix'}
exec(compile(_src, 'intel_check.py (first part)', 'exec'), NS)   # the made-up folder, mocks, names
globals().update({k: v for k, v in NS.items() if not k.startswith('__') and k not in ('check', 'fails')})
from playwright.sync_api import sync_playwright
check, SOV = NS['check'], NS['SOV']
PAGE = open(HTML, encoding='utf-8').read()
A, B_AL, PILOT = 99000001, 99000002, 95000099
T0 = time.time()

def start(b, html, w, errs, h=1000, touch=False):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch, device_scale_factor=2 if touch else 1)
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); route(ctx)
    pg = ctx.new_page(); pg.goto('file://' + html)
    # the avoid options off: the check's own reports would flag systems beside the bridges (flags win over length, as on main)
    pg.evaluate("() => localStorage.setItem('tvRoute', JSON.stringify({pref: 'Shorter', pen: 50, camp: false, bub: false, host: false, kill: false, mine: false, list: []}))")
    pg.evaluate("([s]) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({nearShown: false, channels: ['region.intel'], me: 95000001, range: 3, nearRange: 15, mapReach: 30, sound: false, notify: false, forget: 15, hideFriendly: true})); }", [SIDE])
    pg.reload(); pg.wait_for_timeout(400)
    setup_logs(pg); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg)
    tick(pg, 2500)
    pg.evaluate("() => document.querySelector('#intelPanel .it-map-box').scrollIntoView({block: 'center'})"); pg.wait_for_timeout(200)
    return ctx, pg

# five bridges from the map's own systems, by gate jumps from you and light-years from your system (the capital)
PICK = """() => { const T = itMapTable(), g = itGraphGet(), h = itm.home, Dg = itm.Dg, L = (i) => itMapLy(i, h), used = new Set([h]);
  const all = []; for(let i = 0; i < T.n; i++) if(Dg[i] > 0 && Dg[i] <= 30) all.push(i);
  const take = (px, py) => { for(const x of all){ if(used.has(x) || !px(x)) continue; for(const y of all){ if(used.has(y) || y === x || !py(y, x) || itMapLy(x, y) > 4.8) continue; used.add(x); used.add(y); return [x, y]; } } return null; };
  const z1 = (i) => L(i) <= 4.5, z2 = (i) => L(i) >= 5.3 && L(i) <= 9.5;
  const b1 = take(x => Dg[x] <= 2 && z1(x), (y, x) => z1(y) && Dg[y] >= Dg[x] + 5);
  const b2 = take(x => Dg[x] <= 3 && z1(x), (y, x) => z2(y) && Dg[y] >= Dg[x] + 5);
  const b3 = take(x => Dg[x] <= 8 && z2(x), (y, x) => z2(y) && Dg[y] >= Dg[x] + 4);
  const b4 = take(x => Dg[x] <= 2 && z1(x), (y, x) => Dg[y] >= Dg[x] + 6);
  const b5 = take(x => Dg[x] <= 2 && z1(x), (y, x) => Dg[y] >= Dg[x] + 6);
  const bs = [b1, b2, b3, b4, b5];
  return {ok: bs.every(Boolean), bs: bs.map(p => p && [g.ids[p[0]], g.ids[p[1]], p[0], p[1], Dg[p[0]], Dg[p[1]], L(p[0]), L(p[1])]), home: g.ids[h], near: all.map(i => g.ids[i])}; }"""

def answer(pk, cap=True):
    near = set(pk['near']) | {pk['home']}
    ss = []
    for s_ in sorted(near):
        if s_ == pk['bs'][3][1]: ss.append({'solar_system_id': s_, 'claim': {'alliance': {'alliance_id': B_AL, 'corporation_id': 98000001, 'is_capital_system': True}}})
        elif s_ == pk['bs'][4][1]: ss.append({'solar_system_id': s_, 'claim': {'unclaimed': True}})
        else: ss.append({'solar_system_id': s_, 'claim': {'alliance': {'alliance_id': A, 'corporation_id': 98000002, 'is_capital_system': bool(cap and s_ == pk['home'])}}})
    ss.append({'solar_system_id': 30000142, 'claim': {'faction': {'faction_id': 500001}}})
    return {'solar_systems': ss}

def zone(ly):   # worked out here: rounded up to 0.01, then 5 / 10 / 15 / 20 LY
    v = __import__('math').ceil(ly * 100 - 1e-9) / 100
    return 1 if v <= 5 else 2 if v <= 10 else 3 if v <= 15 else 4 if v <= 20 else 5

LIST = "(pk) => pk.bs.map(b => `${itSysName(b[0])} » ${itSysName(b[1])} - Mockup bridge`).join('\\n')"
ON = "([t]) => { it.set.bridges = t; it.set.bridgesOn = true; itWriteSet(); itBridgePaint(); itMapRefresh(); return [itm.jbKey, itBridges().edges.length]; }"
ZS = """() => { const Z = itJbZones(); return {st: Z.st, usable: Z.usable, total: Z.total, ukey: Z.ukey, rows: [...Z.rows].map(([n, r]) => [n, r.why ? r.why.k : null, r.dirs ? r.dirs.map(d => [d.from, d.to, d.z, d.use]) : null]),
  out: [...Z.out].map(([k, v]) => [k, v]), status: itRpJbStatus()}; }"""
ROUTE = """([i, j]) => { itRp.key = ''; itRpUpdate(); const p = itRpPath(i); if(!p) return null; const st = []; const T = itMapTable();
  for(let k = 0; k + 1 < p.length; k++) if(!T.adj[p[k]].includes(p[k + 1])) st.push([p[k], p[k + 1]]); return {n: p.length - 1, st, D: itm.D[i], Dg: itm.Dg[i]}; }"""
TIP = "(i) => { itMapTip(i, 20, 20); const h = itm.tip.innerHTML; itMapTip(-1); return [h, itRpBtnsHtml(i, false)]; }"
SETZ = "(z) => { itRpJbZones = z; itRpJbSave(); itRpRefresh(); itBridgePaint(); return itRpJbSet(); }"
LOGIN = "([al, name, pid]) => { sso.who = {id: pid, name: 'Mk Pilot'}; side.rec = Object.assign({}, side.rec || {}, {pilot: {id: pid, name: 'Mk Pilot'}, alliance: al ? {id: al, name} : null}); itJbChanged(); return itJbYou(); }"
LOGOUT = "() => { sso.who = null; itJbChanged(); return itJbYou(); }"
SOVSET = "() => { itSov.sys = null; itSov.exp = 0; itSov.next = 0; itSov.err = ''; itSov.fails = 0; }"

def cases(b, html, parts=('zones', 'map', 'read', 'ui', 'phone')):
    out, errs = [], []
    SOV['answer'] = None; SOV['status'] = 200; SOV['asked'].clear(); SOV['expires'] = 300
    ctx, pg = start(b, html, 1440, errs)
    pk = pg.evaluate(PICK)
    if not pk['ok']: out.append(f'the made-up bridges could not be picked from the map: {pk["bs"]}'); ctx.close(); return out, errs
    bs = pk['bs']; idx = [(x[2], x[3]) for x in bs]
    text = pg.evaluate(LIST, pk)
    if 'zones' in parts:
        r = pg.evaluate("() => [0, 4.99, 5.0, 5.001, 10.0, 10.01, 15.01, 20.01, 25].map(itJbZoneOf)")
        if r != [1, 1, 1, 2, 2, 3, 4, 5, 5]: out.append(f'itJbZoneOf at 0 … 25 LY: {r} (want 1 1 1 2 2 3 4 5 5: "At 5.00 LY", rounded up)')
    # the switch off: nothing is read, routes by stargate, no zones on the rows
    pg.evaluate("([t]) => { it.set.bridges = t; it.set.bridgesOn = false; itWriteSet(); itBridgePaint(); itMapRefresh(); }", [text])
    pg.wait_for_timeout(300)
    if SOV['asked']: out.append(f'the switch off: EVE\'s sovereignty asked {len(SOV["asked"])} time(s) (want none)')
    z = pg.evaluate(ZS)
    if z['st'] != 'off' or 'Use jump bridges on the map is off (in the Jump bridges box)' not in z['status']: out.append(f'the switch off: {z["st"]} {z["status"]!r} (want off, naming the Jump bridges box)')
    # on, before the answer (the stand-in refuses): every bridge counts (D8)
    SOV['answer'] = answer(pk)
    SOV['status'] = 503
    pg.evaluate(ON, [text]); pg.wait_for_timeout(500)
    asked0 = len(SOV['asked'])
    z = pg.evaluate(ZS)
    dg0 = pg.evaluate("() => Array.from(itm.Dg).join(',')")
    d_before = pg.evaluate("(p) => p.map(([x, y]) => itm.D[y])", idx)
    if 'read' in parts:
        if asked0 != 1: out.append(f'a failed read: asked {asked0} times (want 1)')
        if z['st'] != 'fail' or 'ROUTE-02' not in z['status']: out.append(f'a failed read: {z["st"]} {z["status"]!r} (want fail with ROUTE-02)')
        pg.evaluate("() => { itSovNeed(); itMapRefresh(); itSovNeed(); }"); pg.wait_for_timeout(300)
        if len(SOV['asked']) != asked0: out.append('a failed read was asked again at once (want 60 s first)')
        if SOV['asked'] and SOV['asked'][0] != 'https://esi.evetech.net/sovereignty/systems?compatibility_date=2026-05-19': out.append(f'the address: {SOV["asked"][0]}')
        rows = pg.evaluate("() => itBridgeRowsHtml()")
        if 'Zones:' not in rows or 'ROUTE-02' not in rows: out.append('a failed read: the Jump bridges box doesn\'t say the zones aren\'t known (ROUTE-02)')
    if 'map' in parts:
        for k, (x, y) in enumerate(idx):
            if d_before[k] > bs[k][4] + 1: out.append(f'before the answer: b{k + 1} not counted on the map (D {d_before[k]}, want ≤ {bs[k][4] + 1}: D8)')
    # the answer arrives
    SOV['status'] = 200
    pg.evaluate(SOVSET); pg.evaluate("() => itMapRefresh()"); pg.wait_for_timeout(800)
    z = pg.evaluate(ZS)
    if z['st'] != 'ok': out.append(f'with the answer: {z["st"]} {z["status"]!r} (want ok)'); ctx.close(); return out, errs
    rows = {n: (k, dirs) for n, k, dirs in z['rows']}
    if 'zones' in parts:
        # logged out: b1-b3 usable, b4 two alliances, b5 none; zones per direction by the arrival
        L = pg.evaluate("(p) => { const g = itGraphGet(), h = g.at.get(p.home); return p.bs.map(b => [itMapLy(b[3], h), itMapLy(b[2], h)]); }", pk)
        for k in range(3):
            got = rows.get(k + 1)
            if not got or got[0] or not got[1]: out.append(f'logged out: b{k + 1} {got} (want usable)'); continue
            want = [zone(L[k][0]), zone(L[k][1])]
            if [d[2] for d in got[1]] != want: out.append(f'b{k + 1}: zones {[d[2] for d in got[1]]} (want {want}: from each arrival, {L[k][0]:.2f} / {L[k][1]:.2f} LY)')
            if [d[3] for d in got[1]] != [w == 1 for w in want]: out.append(f'b{k + 1}: used {[d[3] for d in got[1]]} (want only zone 1 arrivals)')
        if (rows.get(4) or [None])[0] != 'two': out.append(f'logged out: b4 {rows.get(4)} (want left out: two alliances)')
        if (rows.get(5) or [None])[0] != 'none': out.append(f'logged out: b5 {rows.get(5)} (want left out: no holder)')
        if z['usable'] != 3 or 'Logged out' not in z['status'] or '3 of 5 bridges usable' not in z['status']: out.append(f'logged out: {z["usable"]} usable, {z["status"]!r}')
        rh = pg.evaluate("() => itBridgeRowsHtml()")
        rh = rh.replace('&#39;', "'")
        for w in ['different alliances: left out of routes', "isn't held by any alliance", 'jb-zs', 'zone 2 · ×2', 'zone 1 · free']:
            if w not in rh: out.append(f'the rows lack "{w}"')
    if 'map' in parts:
        d_after = pg.evaluate("(p) => p.map(([x, y]) => itm.D[y])", idx)
        dg1 = pg.evaluate("() => Array.from(itm.Dg).join(',')")
        if dg1 != dg0: out.append('itm.Dg changed (want stargates only, always)')
        for k in (0, 2):
            if d_after[k] > bs[k][4] + 1: out.append(f'with the answer: b{k + 1} (usable) not counted on the map: D {d_after[k]} (want ≤ {bs[k][4] + 1}, whatever its zones)')
        for k in (3, 4):
            if d_after[k] <= bs[k][4] + 1: out.append(f'with the answer: b{k + 1} (left out) still counted on the map: D {d_after[k]} (want more than {bs[k][4] + 1})')
        if not re.search(r'\|x:', pg.evaluate("() => itm.jbKey || ''")): out.append('itm.jbKey lacks the bridges left out (the map not told to search again)')
        # the owner's hand test: Within N's hover said "stargate jumps" while the bridges counted
        t = pg.evaluate("() => (itm.el.querySelector('[data-im-f=\"near\"]') || {}).title || ''")
        if 'jump bridges you can use counted' not in t: out.append(f'Within N\'s hover with bridges on: {t!r} (want "jump bridges you can use counted")')
        e = pg.evaluate("() => sovBridgeEnds().length")
        if e != 10: out.append(f'sovBridgeEnds: {e} (want 10: every counted bridge, whatever its use)')
        rec = pg.evaluate("""() => { const C = CanvasRenderingContext2D.prototype, qc = C.quadraticCurveTo, out = []; C.quadraticCurveTo = function(){ if(this.canvas === itm.cv) out.push([String(this.strokeStyle).toLowerCase(), this.getLineDash().length]); return qc.apply(this, arguments); };
          try{ itMapDraw(); } finally { C.quadraticCurveTo = qc; } return out; }""")
        green = [x for x in rec if x[0] == '#00a800']
        if len(green) < 5 or sum(1 for x in green if x[1]) != 2: out.append(f'the curves: {green} (want 5 in #00a800, 2 of them dashed: D5)')
        if pg.evaluate("() => getComputedStyle(document.documentElement).getPropertyValue('--it-bridge').trim()") != '#00a800': out.append('--it-bridge isn\'t #00a800 (the owner: 70% of #00f000)')
        # the owner's hand test: "light blue line does not follow the jump bridge". The route to b1's far end crosses b1 against its listed
        # direction (the list says near » far; the route is drawn from the far end): its bridge step must be the bridge's own curve
        cv = pg.evaluate("""(id) => { const C = CanvasRenderingContext2D.prototype, qc = C.quadraticCurveTo, out = []; itRp.key = ''; itRpUpdate(); itm.pinned.add(id);
          C.quadraticCurveTo = function(cx, cy, x, y){ if(this.canvas === itm.cv) out.push([String(this.strokeStyle).toLowerCase(), cx, cy]); return qc.apply(this, arguments); };
          try{ itMapDraw(); } finally { C.quadraticCurveTo = qc; itm.pinned.delete(id); itMapDraw(); } return out; }""", bs[0][1])
        greens = [(x, y) for c, x, y in cv if c == '#00a800']
        others = [(x, y) for c, x, y in cv if c != '#00a800']
        if not others: out.append('the route over b1 drew no bridge step as a curve')
        elif not any(abs(x - gx) < 0.5 and abs(y - gy) < 0.5 for x, y in others for gx, gy in greens): out.append(f'the route\'s bridge step bows away from the bridge\'s curve (route {others[:1]}, bridges {greens[:2]})')
    if 'zones' in parts:
        # the route: to b1's far end by the free bridge; b2 only toward its home end
        r1 = pg.evaluate(ROUTE, [idx[0][1], 0])
        if not r1 or r1['n'] != bs[0][4] + 1 or [idx[0][0], idx[0][1]] not in r1['st']: out.append(f'the route to b1\'s far end: {r1} (want {bs[0][4] + 1} jumps by the free bridge, by gate {bs[0][5]})')
        r2 = pg.evaluate(ROUTE, [idx[1][1], 0])
        if not r2 or [idx[1][0], idx[1][1]] in r2['st']: out.append(f'the route to b2\'s far end took its zone 2 arrival: {r2}')
        tip, btn = pg.evaluate(TIP, idx[0][1])
        for w in ['route:', '⇢ jump bridge', 'arriving in zone 1 · free']:
            if w not in tip: out.append(f'b1\'s far end\'s hover lacks "{w}"')
        if 'route by stargate:' in tip: out.append('the hover says "route by stargate:" for a route that takes a bridge')
        if "Threat Vector's route:" in tip: out.append('the hover shows "Threat Vector\'s route" for the shortest over its own graph')
        if '1 by jump bridge' not in btn: out.append('the menu\'s Threat Vector\'s route line lacks "1 by jump bridge"')
        home = pg.evaluate("([y, x]) => { const h = itm.home; itm.home = y; itRp.key = ''; itRpUpdate(); const p = itRpPath(x); itm.home = h; itRp.key = ''; itRpUpdate(); return p ? p.length - 1 : -1; }", [idx[1][1], idx[1][0]])
        if home != 1: out.append(f'from b2\'s far end home: {home} jumps (want 1: its home end is zone 1)')
        pg.evaluate(SETZ, [1, 2])
        r2b = pg.evaluate(ROUTE, [idx[1][1], 0])
        if not r2b or [idx[1][0], idx[1][1]] not in r2b['st']: out.append(f'zone 2 ticked: the route to b2\'s far end doesn\'t take it: {r2b}')
        pg.evaluate(SETZ, [])
        z0 = pg.evaluate(ZS); r0 = pg.evaluate(ROUTE, [idx[0][1], 0])
        if z0['out'] or not r0 or r0['st'] or 'No zone is ticked' not in z0['status']: out.append(f'every zone unticked: {z0["out"]}, {r0}, {z0["status"]!r} (want stargates only)')
        d0 = pg.evaluate("(i) => itm.D[i]", idx[0][1])
        if d0 > bs[0][4] + 1: out.append('every zone unticked: b1 no longer counted on the map (want zones never to change the counts)')
        pg.evaluate(SETZ, [1])
        # logged in as Your pilot in the alliance: b4 "is held by"; no alliance: none usable
        pg.evaluate(LOGIN, [A, 'Mockup Coalition', PILOT]); pg.wait_for_timeout(300)
        z = pg.evaluate(ZS); rows = {n: k for n, k, _ in z['rows']}
        if rows.get(4) != 'other' or z['usable'] != 3 or "your alliance's capital" not in z['status']: out.append(f'logged in: b4 {rows.get(4)}, {z["usable"]} usable, {z["status"]!r}')
        if 'is held by' not in pg.evaluate("() => itBridgeRowsHtml()"): out.append('logged in: b4\'s row lacks "is held by"')
        pg.evaluate(LOGIN, [None, '', PILOT]); pg.wait_for_timeout(200)
        z = pg.evaluate(ZS)
        if z['usable'] != 0 or z['out'] or "isn't in an alliance" not in z['status']: out.append(f'logged in with no alliance: {z["usable"]} usable, {z["status"]!r}')
        pg.evaluate(LOGOUT)
        # the switch off after a read: stargate routes, rows without zones
        pg.evaluate("() => { it.set.bridgesOn = false; itWriteSet(); itBridgePaint(); itMapRefresh(); }")
        r = pg.evaluate(ROUTE, [idx[0][1], 0]); rh = pg.evaluate("() => itBridgeRowsHtml()")
        if not r or r['st'] or 'jb-zs' in rh or 'Zones:' in rh: out.append(f'the switch off after a read: {r}, zones on the rows {"jb-zs" in rh} (want stargate routes, 041\'s rows)')
        tip, _ = pg.evaluate(TIP, idx[0][1])
        pg.evaluate("() => { it.set.bridgesOn = true; itWriteSet(); itBridgePaint(); itMapRefresh(); }")
    if 'read' in parts:
        n = len(SOV['asked'])
        pg.evaluate("() => { for(let k = 0; k < 5; k++){ itSovNeed(); itMapRefresh(); } }"); pg.wait_for_timeout(300)
        if len(SOV['asked']) != n: out.append(f'asked again before Expires ({len(SOV["asked"]) - n} more)')
        pg.evaluate("() => { itSov.exp = 0; itRpJbZones = []; }"); pg.evaluate("() => itMapRefresh()"); pg.wait_for_timeout(400)
        if len(SOV['asked']) != n + 1: out.append('past Expires with no zone ticked: not asked again (want the map\'s counts kept current)')
        pg.evaluate("() => { itRpJbZones = [1]; it.set.bridges = ''; itSov.exp = 0; itBridgePaint(); itMapRefresh(); }"); pg.wait_for_timeout(300)
        if len(SOV['asked']) != n + 1: out.append('no bridge listed: asked anyway')
        pg.evaluate("([t]) => { it.set.bridges = t; itWriteSet(); itBridgePaint(); itMapRefresh(); }", [text]); pg.wait_for_timeout(400)
        r = pg.evaluate("() => { const a = itRpAside; itRpAside = true; const w = itSovWanted(), j = itRpJbOn(); itRpAside = a; return [w, j]; }")
        if r != [False, False]: out.append(f'the Intel example: {r} (want no read and stargate routes)')
    if 'map' in parts:
        # the hover on b1's line, at a point with no system near it
        pt = pg.evaluate("""([a, b]) => { const P = itm.P, v = itm.view, mx = (P[2*a] + P[2*b]) / 2, my = (P[2*a+1] + P[2*b+1]) / 2, len = Math.hypot(P[2*a] - P[2*b], P[2*a+1] - P[2*b+1]) || 1;
          v.k = Math.min(itm.kMax, Math.max(itm.kMin, 320 / len)); v.tx = itm.W / 2 - mx * v.k; v.ty = itm.H / 2 - my * v.k; itMapDraw(); const Q = itm.Q, x1 = Q[2*a], y1 = Q[2*a+1], x2 = Q[2*b], y2 = Q[2*b+1], dx = x2-x1, dy = y2-y1, cx = (x1+x2)/2 - dy*0.22, cy = (y1+y2)/2 + dx*0.22;
          for(const t of [0.5, 0.4, 0.6, 0.3, 0.7, 0.45, 0.55]){ const u = 1-t, px = u*u*x1 + 2*u*t*cx + t*t*x2, py = u*u*y1 + 2*u*t*cy + t*t*y2; if(itMapPick(px, py) < 0 && px > 4 && py > 4 && px < itm.W - 4 && py < itm.H - 4) return [px, py]; } return null; }""", list(idx[0]))
        if not pt: out.append('no free point on b1\'s line to hover')
        else:
            box = pg.evaluate("() => { const r = itm.cv.getBoundingClientRect(); return [r.left, r.top]; }")
            pg.mouse.move(box[0] + pt[0], box[1] + pt[1]); pg.wait_for_timeout(200)
            t = pg.evaluate("() => itm.tip.hidden ? '' : itm.tip.innerHTML")
            for w in ['Jump bridge', 'zone 1 · free', "capital", 'Routes use it both ways']:
                if w not in t: out.append(f'the hover on a bridge line lacks "{w}" ({t[:80]!r})')
            if pg.evaluate("() => itm.hoverJb") < 0: out.append('the hovered bridge isn\'t drawn thicker (itm.hoverJb)')
    # no capital: every direction zone 5, none used with zone 1 only
    if 'zones' in parts:
        SOV['answer'] = answer(pk, cap=False)
        pg.evaluate(SOVSET); pg.evaluate("([t]) => { itRpJbZones = [1]; it.set.bridges = t; it.set.bridgesOn = true; itMapRefresh(); }", [text]); pg.wait_for_timeout(600)
        z = pg.evaluate(ZS)
        dz = [d[2] for _, k, dirs in z['rows'] if dirs for d in dirs]
        if z['st'] != 'ok' or set(dz) != {5} or z['out'] or 'has no capital' not in z['status']: out.append(f'no capital: zones {dz}, used {z["out"]}, {z["status"]!r} (want every jump zone 5, none used)')
        SOV['answer'] = answer(pk)
        pg.evaluate(SOVSET); pg.evaluate("() => itMapRefresh()"); pg.wait_for_timeout(600)
    if 'ui' in parts:
        pg.click('[data-it-act="gear"]'); pg.wait_for_timeout(300)
        r = pg.evaluate("""() => { const b = document.querySelector('[data-it-rp-box]'); if(!b) return null; const z = [...b.querySelectorAll('[data-it-rp-jbz]')];
          const after = b.querySelector('.it-rp-msg').compareDocumentPosition(z[0]) & Node.DOCUMENT_POSITION_FOLLOWING;
          return [z.map(x => x.checked), !!after, (b.querySelector('[data-it-rp-jbs]') || {}).textContent || '']; }""")
        if not r or r[0] != [True, False, False, False, False] or not r[1] or 'usable' not in r[2]: out.append(f'the Routes box: {r} (want five zones, only zone 1, after the avoid list, the status line)')
        tv0 = pg.evaluate("() => Object.keys(JSON.parse(localStorage.getItem('tvRoute') || '{}')).sort().join(',')")
        pg.click('[data-it-rp-jbz="2"]'); pg.wait_for_timeout(300)
        r = pg.evaluate("() => [localStorage.getItem('tvRouteJb'), itRpJbSet().join(','), Object.keys(JSON.parse(localStorage.getItem('tvRoute') || '{}')).sort().join(',')]")
        if r[0] != '{"v":1,"zones":[1,2]}' or r[1] != '1,2' or r[2] != tv0: out.append(f'a click on zone 2: {r} (want tvRouteJb {{"v":1,"zones":[1,2]}}, tvRoute\'s form unchanged)')
        r2b = pg.evaluate(ROUTE, [idx[1][1], 0])
        if not r2b or [idx[1][0], idx[1][1]] not in r2b['st']: out.append('a click on zone 2 didn\'t route again')
        pg.reload(); pg.wait_for_timeout(500)
        if pg.evaluate("() => itRpJbSet().join(',')") != '1,2': out.append('zones not kept after a reload')
        for bad in ['"x"', '{"v":1}', '{"zones":"1"}', 'not json']:
            g = pg.evaluate("(v) => { localStorage.setItem('tvRouteJb', v); itRpJbZones = null; return itRpJbSet().join(','); }", bad)
            if g != '1': out.append(f'tvRouteJb {bad!r} read as {g!r} (want zone 1)')
        g = pg.evaluate("() => { localStorage.setItem('tvRouteJb', '{\"v\":1,\"zones\":[2,9,2]}'); itRpJbZones = null; return itRpJbSet().join(','); }")
        if g != '2': out.append(f'tvRouteJb with zones outside 1-5: {g!r} (want 2)')
        pg.evaluate("() => { localStorage.removeItem('tvRouteJb'); itRpJbZones = null; }")
        if not pg.evaluate("() => document.scrollingElement.scrollWidth <= innerWidth + 1"): out.append('1440 px: sideways scroll')
    ctx.close()
    if 'phone' in parts:
        SOV['answer'] = answer(pk); SOV['status'] = 200
        ctx, pg = start(b, html, 390, errs, h=844, touch=True)
        pg.evaluate(ON, [text]); pg.wait_for_timeout(500)
        pg.click('[data-it-act="gear"]'); pg.wait_for_timeout(300)
        h = pg.evaluate("() => Math.min(...[...document.querySelectorAll('.it-rp-jbz label')].map(l => Math.round(l.getBoundingClientRect().height)))")
        if h < 44: out.append(f'390 px: the zone rows {h} px (want 44)')
        if not pg.evaluate("() => document.scrollingElement.scrollWidth <= innerWidth + 1"): out.append('390 px: sideways scroll')
        ctx.close()
    return out, errs

MUTANTS = [
    ('a zone from the departure', "const ly = ic !== undefined ? itMapLy(y, ic) : null", "const ly = ic !== undefined ? itMapLy(x, ic) : null", ('zones',)),
    ('a direction used with its zone unticked', "return {from: x, to: y, toId: to, z, ly, use: zs.includes(z)};", "return {from: x, to: y, toId: to, z, ly, use: true};", ('zones',)),
    ('a two-alliance bridge used (logged out)', "else if(ha !== hb) why = {k: 'two'};", "else if(false) why = {k: 'two'};", ('zones',)),
    ('5.00 LY read as zone 2', "return v <= 5 ? 1 : v <= 10 ? 2", "return v < 5 ? 1 : v <= 10 ? 2", ('zones',)),
    ('a sov read with no bridge listed', "return !!(it.on && it.set && it.set.bridgesOn) && itBridges().edges.length > 0;", "return !!(it.on && it.set && it.set.bridgesOn);", ('read',)),
    ('bridges in the route with the switch off', "const st = !on ? 'off' : !B.edges.length", "const st = false ? 'off' : !B.edges.length", ('zones',)),
    ('zones on the rows with the switch off', "Z = it.set && it.set.bridgesOn ? itJbZones() : null;", "Z = itJbZones();", ('zones',)),
    ('another alliance\'s bridge counted on the map', "for(const [a, b] of B.edges){ if(Z.bad.has(itJbPair(a, b))) continue; B.adj[a].push(b);", "for(const [a, b] of B.edges){ B.adj[a].push(b);", ('map',)),
    ('a usable costly bridge left out of the map', "for(const [a, b] of B.edges){ if(Z.bad.has(itJbPair(a, b))) continue; B.adj[a].push(b);",
     "for(const [a, b] of B.edges){ if(Z.bad.has(itJbPair(a, b)) || (Z.st === 'ok' && !Z.used.includes(`${a}>${b}`) && !Z.used.includes(`${b}>${a}`))) continue; B.adj[a].push(b);", ('map',)),
    ('the map not searched again when the answer arrives', "return itBridges().key + (u ? `|x:${u}` : '');", "return itBridges().key;", ('map',)),
    ('asked again before Expires', "if((itSov.sys && now < itSov.exp) || now < itSov.next) return;", "if(now < itSov.next) return;", ('read',)),
    ('a failed read asked again at once', "if(!ok){ itSov.next = Date.now() + IT_SOV_RETRY_MS", "if(!ok){ itSov.next = Date.now() + 0 * IT_SOV_RETRY_MS", ('read',)),
    ('"route by stargate:" on a route over a bridge', "itm.jbKey && !itRpJbOn() ? ' by stargate' : ''", "itm.jbKey ? ' by stargate' : ''", ('zones',)),
    ('no route step lines', "if(jr) h += itRpJbStepsHtml(path);", "", ('zones',)),
    ('"(shortest N)" by stargate on a bridge route', "sd = jr ? itRp.sd[i] : jb ? itm.Dg[i] : d;", "sd = jr ? itm.Dg[i] : jb ? itm.Dg[i] : d;", ('zones',)),
    ('a bad tvRouteJb read as no zones', "if(!o || typeof o !== 'object' || !Array.isArray(o.zones)) return [1];", "if(!o || typeof o !== 'object' || !Array.isArray(o.zones)) return [];", ('ui',)),
    ('zones saved into tvRoute', "itRpJbZones = [...zs].sort((a, b) => a - b); itRpJbSave();", "itRpJbZones = [...zs].sort((a, b) => a - b); itRpSet().zones = itRpJbZones; itRpSave(); itRpJbSave();", ('ui',)),
    ('no capital read as zone 1', "z = ly === null ? 5 : itJbZoneOf(ly)", "z = ly === null ? 1 : itJbZoneOf(ly)", ('zones',)),
    ('left-out bridges drawn solid', "c.setLineDash(bad ? (big ? [5, 4] : [3, 3]) : []);", "c.setLineDash([]);", ('map',)),
    ('no hover on a bridge line', "bj = i < 0 ? itMapPickBridge(x, y, false) : -1;", "bj = -1;", ('map',)),
    ('the zone rows short on a phone', " .it-rp-box .it-rp-jbz label{min-height:44px;}", "", ('phone',)),
    ('a route\'s bridge step drawn the way it is crossed', "else itBridgeArc(c, a, b, X, Y); }", "else itMapArc(c, X(a), Y(a), X(b), Y(b)); }", ('map',)),
    ('Within N\'s hover says stargate jumps with bridges on', ": f.k === 'near' ? 'only: systems this many jumps from you or fewer, jump bridges you can use counted' : f.note; }", ": f.note; }", ('map',)),
    ('the bridges at full brightness', ":root{--it-bridge:#00a800;}", ":root{--it-bridge:#00f000;}", ('map',)),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, 'Ansiblex zones: zones by arrival, who can use a bridge, the route, the map\'s counts, the read, the Routes box, storage, hover, phone')
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
