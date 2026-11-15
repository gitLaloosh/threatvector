"""The Wormholes tab, part 1 (build queue 048; Project doc roadmap/wormhole-mapping-plan.md "Build in parts" 1; mockup
Claude outputs/wormholes_tab_mockup.html). The owner: "1. own wormholes tab, 2. yes as you suggest, 3. right after intel", "add a "BETA" tag
on the wormholes tab", and at the build review: a connection comes from your last recorded system ("which hole you came through comes from your
last recorded location"), "yes, skip system changes that land you docked", Intel counting from where you came in (D14), the tab reading EVE
location on its own while it's in front (D19), the three later panels saying so.

Made-up Intel (intel_check.py's folder and stand-ins), CCP's wormhole system names from the page's own table (INTEL_WH). Checks:
  * INTEL_WH: 2,604 systems, Thera class Thera, a shattered and a Drifter system, effects;
  * the tab right after Intel with its BETA tag and aria-label; one tab row at 1440 and 390 px;
  * a scripted path from the Local log (k → J1 → J2 → J1 → k2, after a k → k jump): the right systems and connections, a k → k jump records
    nothing; entering J-space from Intel switches to Wormholes, from Pilot Analyzer only marks the button, leaving goes back to Intel;
  * D14: in J-space Intel's system is the k-space entrance and the map says so;
  * EVE location (a stand-in answer through itGameLoc): a docked answer adds no connection, an undocked one does; read with Intel off while the
    tab is in front, not while it isn't;
  * the System panel: CCP's class, a k-space name in its security colour, statics chips coloured by where they lead (C5 amber, HS green, K162
    grey), edits saved and kept after a reload; tvWormholes untouched; Signatures, Routes and Local say they come later;
  * + Add refuses an unknown name and adds a J-system linked to the focus with its signature ID; "Add a system here" on empty space puts it there;
  * dragging saves a position, Rearrange drops them; Shift-drag selects a group that moves together; the overview moves the view;
  * a phone: the More menu (one row; System, Pilot and Fit in it; a pick switches; Esc closes), no sideways scroll; mutants; no page errors.
"""
import sys, os, re, json, time, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
_src = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
_src = _src[:_src.index('with sync_playwright() as p:')]
NS = {'__file__': os.path.join(HERE, 'intel_check.py'), '__name__': 'intel_check_prefix'}
exec(compile(_src, 'intel_check.py (first part)', 'exec'), NS)   # the made-up folder, mocks, names
globals().update({k: v for k, v in NS.items() if not k.startswith('__') and k not in ('check', 'fails')})
from playwright.sync_api import sync_playwright
check = NS['check']
PAGE = open(HTML, encoding='utf-8').read()

def start(b, html, w, errs, h=1000, touch=False):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch, device_scale_factor=2 if touch else 1)
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); route(ctx)
    pg = ctx.new_page(); pg.goto('file://' + html)
    pg.evaluate("(s) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({channels: ['region.intel'], me: 95000001, range: 3, sound: false, notify: false}));"
                " localStorage.removeItem('tvWhChain'); localStorage.setItem('tvWormholes', JSON.stringify({v: 1, keepH: 24, gone: {}, rep: {}})); }", SIDE)
    pg.reload(); pg.wait_for_timeout(400)
    return ctx, pg

def intel_on(pg):
    setup_logs(pg); pg.click('#tabBtnIntel'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg)

def jump(pg, name, t): W(pg, F_LOCAL_MAIN, line(t, 'EVE System', f'Channel changed to Local : {name}*')); tick(pg, 2800)

ST = "() => { const s = JSON.parse(localStorage.getItem('tvWhChain') || 'null'); return s && {sys: Object.keys(s.sys).map(Number).sort(), links: s.links.map(l => [Math.min(l.a, l.b), Math.max(l.a, l.b)]).sort(), pos: s.pos}; }"
ROW = "() => { const v = [...document.querySelectorAll('.tabs .tab-btn')].filter(e => e.offsetParent); return [v.map(e => e.id), new Set(v.map(e => Math.round(e.getBoundingClientRect().top))).size, document.documentElement.scrollWidth <= innerWidth]; }"
LOC = """([sys, docked]) => { it.set.gameLoc = true; sso.who = {id: 95000001, name: 'Your Main'}; sso.scp = [SSO_LOC]; itGl.next = 0; itGl.stop = ''; itGl.busy = false;
  window.__locAsked = (window.__locAsked || 0);
  esiFetch = async () => { window.__locAsked++; const j = {solar_system_id: sys}; if(docked) j.station_id = 60003760;
    return {status: 200, ok: true, headers: new Headers({expires: new Date(Date.now() - 1000).toUTCString()}), json: async () => j}; };
  return itGameLoc(); }"""

def cases(b, html, parts=('table', 'path', 'loc', 'panel', 'add', 'map', 'phone')):
    out, errs = [], []
    ctx, pg = start(b, html, 1440, errs)
    if not pg.evaluate("typeof whTable === 'function' && !!document.getElementById('tabBtnWh')"):
        out.append('no Wormholes tab'); ctx.close(); return out, errs
    T = pg.evaluate("() => { const T = whTable(), at = (n) => T.byName.get(n.toLowerCase()); return {n: T.ids.length, thera: whClsData(at('Thera')), j: T.names.filter(n => /^J\\d{6}$/.test(n)).slice(0, 12),"
                    " c13: T.names.find((n, i) => T.cls[i] === 's'), dr: T.names.filter((n, i) => T.cls[i] === 'd').length, eff: T.eff.replace(/-/g, '').length, c5: T.names.find((n, i) => T.cls[i] === '5' && /^J/.test(n)),"
                    " place: whPlace(at(T.names[100]))}; }")
    J = T['j']
    if 'table' in parts:
        if T['n'] != 2604 or T['thera'] != 'th' or not T['c13'] or T['dr'] != 5 or T['eff'] != 1038 or '/' not in T['place']:
            out.append(f'INTEL_WH: {T["n"]} systems, Thera {T["thera"]}, C13 {T["c13"]}, {T["dr"]} Drifter, {T["eff"]} effects, place {T["place"]!r} (want 2604, th, one, 5, 1038, "constellation / region")')
        tb = pg.evaluate("() => { const b = document.getElementById('tabBtnWh'); return [b.previousElementSibling && b.previousElementSibling.id, b.getAttribute('aria-label'), b.querySelector('.it-gtag') && b.querySelector('.it-gtag').textContent, TAB_PANELS.indexOf('wh')]; }")
        if tb != ['tabBtnIntel', 'Wormholes (beta)', 'Beta', 1]: out.append(f'the tab right after Intel, BETA, labelled: {tb}')
        r = pg.evaluate(ROW)
        if r[1] != 1 or not r[2]: out.append(f'1440: one tab row, no sideways scroll {r}')
    intel_on(pg)
    t = time.time()
    if 'path' in parts:
        jump(pg, '8WA-Z6', t)   # k → k: nothing recorded
        s0 = pg.evaluate(ST)
        if s0 and s0['sys']: out.append(f'a k → k jump recorded something: {s0}')
        jump(pg, '1DQ1-A', t + 1)
        jump(pg, J[0], t + 2)
        if pg.evaluate("whTabNow()") != 'wh': out.append('entering J-space from Intel should switch to Wormholes')
        jump(pg, J[1], t + 3); jump(pg, J[0], t + 4)
        d14 = pg.evaluate("[itMySys(), itMapCtx()]")
        if d14[0] != SYSID['1DQ1-A'] or 'counted from 1DQ1-A' not in d14[1]: out.append(f'D14: in J-space Intel counts from the entrance: {d14}')
        pg.click('#tabBtnPilot'); pg.wait_for_timeout(200)
        jump(pg, 'T5ZI-S', t + 5)   # out to another k-space system, from Pilot Analyzer: no switch
        if pg.evaluate("whTabNow()") != 'pilot': out.append('leaving J-space from Pilot Analyzer should not switch')
        jump(pg, J[1], t + 6)
        mk = pg.evaluate("[whTabNow(), document.getElementById('tabBtnWh').dataset.s]")
        if mk != ['pilot', 'in']: out.append(f'entering J-space from Pilot Analyzer only marks the button: {mk}')
        pg.click('#tabBtnWh'); pg.wait_for_timeout(200)
        if pg.evaluate("document.getElementById('tabBtnWh').dataset.s") != '': out.append('opening the tab clears the mark')
        jump(pg, 'T5ZI-S', t + 7)
        if pg.evaluate("whTabNow()") != 'intel': out.append('leaving J-space while on Wormholes should go back to Intel')
        s = pg.evaluate(ST); ids = pg.evaluate("(n) => n.map(x => whIdOf(x))", ['1DQ1-A', J[0], J[1], 'T5ZI-S'])
        k1, j1, j2, k2 = ids
        want_l = sorted([sorted([k1, j1]), sorted([j1, j2]), sorted([j1, k2]), sorted([j2, k2])])
        if s['sys'] != sorted(ids) or s['links'] != want_l: out.append(f'the path: systems {s["sys"]} links {s["links"]} (want {sorted(ids)} {want_l})')
        if pg.evaluate("localStorage.getItem('tvWormholes')") != json.dumps({'v': 1, 'keepH': 24, 'gone': {}, 'rep': {}}, separators=(',', ':')):
            if json.loads(pg.evaluate("localStorage.getItem('tvWormholes')")).get('sys'): out.append('the chain went into tvWormholes')
    if 'loc' in parts:
        n0 = len(pg.evaluate(ST)['links'] or [])
        pg.evaluate(LOC, [pg.evaluate("(n) => whIdOf(n)", J[3]), True]); pg.wait_for_timeout(150)
        s1 = pg.evaluate(ST)
        if len(s1['links']) != n0: out.append(f'a docked answer (a clone jump, a pod death) added a connection: {len(s1["links"])} vs {n0}')
        pg.evaluate("() => { itGl.next = 0; }"); pg.evaluate(LOC, [pg.evaluate("(n) => whIdOf(n)", J[4]), False]); pg.wait_for_timeout(150)
        s2 = pg.evaluate(ST)
        if len(s2['links']) != n0 + 1: out.append(f'an undocked answer from a J-system should add the connection: {len(s2["links"])} vs {n0 + 1}')
        # D19: read with Intel off while the tab is in front (its own tick), not while another tab is
        pg.evaluate("() => { itStop(); }"); pg.click('#tabBtnDscan'); pg.wait_for_timeout(200)
        pg.evaluate("() => { window.__locAsked = 0; itGl.next = 0; esiFetch = async () => { window.__locAsked++; return {status: 200, ok: true, headers: new Headers(), json: async () => ({solar_system_id: whIdOf('1DQ1-A')})}; }; }")
        pg.wait_for_timeout(2500); a0 = pg.evaluate("window.__locAsked")
        pg.click('#tabBtnWh'); pg.wait_for_timeout(2600); a1 = pg.evaluate("window.__locAsked")
        if a0 != 0 or a1 < 1: out.append(f'D19: EVE location read only while the tab is in front with Intel off: {a0} on another tab, {a1} on Wormholes')
    pg.click('#tabBtnWh'); pg.wait_for_timeout(300)
    if 'panel' in parts:
        j0 = pg.evaluate("(n) => whIdOf(n)", J[0]); pg.evaluate("(id) => whSelect(id)", j0); pg.wait_for_timeout(150)
        cls = pg.evaluate("(id) => [document.querySelector('[data-pnb=\"sum\"] [data-f=\"cls\"]').value, whClsData(id)]", j0)
        if cls[0] != cls[1]: out.append(f'the class from CCP\'s data: {cls}')
        pg.fill('[data-pnb="sum"] [data-f="statics"]', 'H296 D845 K162'); pg.press('[data-pnb="sum"] [data-f="statics"]', 'Tab'); pg.wait_for_timeout(150)
        chips = pg.evaluate("[...document.querySelectorAll('[data-pnb=\"sum\"] .wh-sc')].map(c => c.className)")
        if chips != ['wh-sc d-mid', 'wh-sc it-sn s6', 'wh-sc d-x']: out.append(f'statics chips by where they lead (C5, HS, the exit): {chips}')
        pg.fill('[data-pnb="sum"] [data-f="notes"]', 'made-up note'); pg.press('[data-pnb="sum"] [data-f="notes"]', 'Tab'); pg.wait_for_timeout(150)
        later = pg.evaluate("[...document.querySelectorAll('.wh-pn:not([data-pn=\"sum\"]) .wh-pnb')].map(b => b.textContent)")
        if later != ['Comes in a later part of the beta.'] * 3: out.append(f'Signatures, Routes and Local: {later}')
        k1 = pg.evaluate("whIdOf('1DQ1-A')"); pg.evaluate("(id) => whSelect(id)", k1); pg.wait_for_timeout(150)
        if not pg.evaluate("!!document.querySelector('[data-pnb=\"sum\"] .wh-shn .it-sn.s0')"): out.append('a nullsec k-space name in its security colour (it-sn s0)')
        pg.reload(); pg.wait_for_timeout(500); pg.click('#tabBtnWh'); pg.wait_for_timeout(300)
        kept = pg.evaluate("(id) => { const s = JSON.parse(localStorage.getItem('tvWhChain')).sys[id]; return [s.statics, s.notes]; }", j0)
        if kept != ['H296 D845 K162', 'made-up note']: out.append(f'edits kept after a reload: {kept}')
    if 'add' in parts:
        pg.click('[data-wh-pop="add"]'); pg.wait_for_timeout(150)
        pg.fill('.wh-addf input[name=sys]', 'Nowhere Special'); pg.click('.wh-addf button[type=submit]'); pg.wait_for_timeout(100)
        if 'isn’t a wormhole system' not in pg.inner_text('.wh-msg'): out.append('+ Add should refuse an unknown name')
        pg.fill('.wh-addf input[name=sys]', J[6]); pg.fill('.wh-addf input[name=sig]', 'RZL429'); pg.click('.wh-addf button[type=submit]'); pg.wait_for_timeout(150)
        jid = pg.evaluate("(n) => whIdOf(n)", J[6]); lk = pg.evaluate("(id) => whLinksOf(id).map(l => l.sig)", jid)
        if lk != ['RZL-429']: out.append(f'+ Add: linked to where you are, through RZL-429: {lk}')
        pg.evaluate("() => whPopClose()")
        box = pg.locator('.wh-box > canvas:not(.wh-mini)').bounding_box()
        pg.mouse.click(box['x'] + box['width'] - 260, box['y'] + 120, button='right'); pg.wait_for_timeout(150)
        if pg.evaluate("document.querySelector('.wh-menu').hidden"): out.append('right-click on empty space should open "Add a system here"')
        else:
            pg.fill('.wh-here input', J[7]); pg.press('.wh-here input', 'Enter'); pg.wait_for_timeout(150)
            h = pg.evaluate("(n) => { const id = whIdOf(n); return [!!whS.st.sys[id], whLinksOf(id).length, !!whS.st.pos[id]]; }", J[7])
            if h != [True, 0, True]: out.append(f'"Add a system here": added, linked to nothing, at the pressed place: {h}')
    if 'map' in parts:
        pg.evaluate("() => { whS.M.cam = null; whS.drawKey = ''; whPaint(true); }"); pg.wait_for_timeout(150)
        P = pg.evaluate("(n) => { const id = whIdOf(n), p = whS.M.P.get(id), c = whS.M.cam, r = whCv().getBoundingClientRect(); return [id, r.x + (p.x + 56 - c.x) * c.s, r.y + (p.y + 24 - c.y) * c.s]; }", J[0])
        pg.mouse.move(P[1], P[2]); pg.mouse.down(); pg.mouse.move(P[1] + 40, P[2] + 30, steps=5); pg.mouse.up(); pg.wait_for_timeout(150)
        if not pg.evaluate("(id) => !!JSON.parse(localStorage.getItem('tvWhChain')).pos[id]", P[0]): out.append('dragging a system should save its place')
        pg.evaluate("() => { document.querySelector('[data-wh-pop=\"set\"]').click(); }"); pg.wait_for_timeout(100); pg.click('[data-wh-z="arr"]'); pg.wait_for_timeout(200)
        if pg.evaluate("Object.keys(JSON.parse(localStorage.getItem('tvWhChain')).pos).length") != 0: out.append('Rearrange as a tree should drop the saved places')
        G = pg.evaluate("(a) => { const r = whCv().getBoundingClientRect(), c = whS.M.cam; return a.map(n => { const p = whS.M.P.get(whIdOf(n)); return [r.x + (p.x - c.x) * c.s, r.y + (p.y - c.y) * c.s, r.x + (p.x + 112 - c.x) * c.s, r.y + (p.y + 48 - c.y) * c.s]; }); }", [J[0], J[1]])
        x0, y0 = min(g[0] for g in G) - 8, min(g[1] for g in G) - 8; x1, y1 = max(g[2] for g in G) + 8, max(g[3] for g in G) + 8
        pg.keyboard.down('Shift'); pg.mouse.move(x0, y0); pg.mouse.down(); pg.mouse.move(x1, y1, steps=6); pg.mouse.up(); pg.keyboard.up('Shift'); pg.wait_for_timeout(100)
        grp = pg.evaluate("whS.M.group.size")
        if grp < 2: out.append(f'Shift-drag should select a group ({grp})')
        else:
            cx, cy = (G[0][0] + G[0][2]) / 2, (G[0][1] + G[0][3]) / 2
            pg.mouse.move(cx, cy); pg.mouse.down(); pg.mouse.move(cx + 30, cy + 20, steps=4); pg.mouse.up(); pg.wait_for_timeout(100)
            n = pg.evaluate("Object.keys(JSON.parse(localStorage.getItem('tvWhChain')).pos).length")
            if n < 2: out.append(f'dragging one of a group should move them all ({n} places saved)')
        c0 = pg.evaluate("[whS.M.cam.x, whS.M.cam.y]"); mb = pg.locator('.wh-mini').bounding_box()
        pg.mouse.click(mb['x'] + 6, mb['y'] + 6); pg.wait_for_timeout(100)
        if pg.evaluate("[whS.M.cam.x, whS.M.cam.y]") == c0: out.append('pressing the overview should move the view')
        if not pg.evaluate("document.documentElement.scrollWidth <= innerWidth"): out.append('1440: sideways scroll')
    ctx.close()
    if 'phone' in parts:
        ctx, pg = start(b, html, 390, errs, h=844, touch=True)
        r = pg.evaluate(ROW)
        if r[0] != ['tabBtnIntel', 'tabBtnWh', None] and r[0][:2] != ['tabBtnIntel', 'tabBtnWh']: out.append(f'390: the row: {r[0]}')
        if r[1] != 1 or not r[2]: out.append(f'390: one tab row, no sideways scroll {r}')
        pg.tap('.tab-more'); pg.wait_for_timeout(150)
        items = pg.evaluate("[...document.querySelectorAll('.tab-more-panel [data-tm]')].map(b => [b.dataset.tm, b.getBoundingClientRect().height >= 44])")
        if [i[0] for i in items] != ['tabBtnDscan', 'tabBtnPilot', 'tabBtnFit'] or not all(i[1] for i in items): out.append(f'390: More lists System, Pilot and Fit, 44 px each: {items}')
        pg.tap('.tab-more-panel [data-tm="tabBtnPilot"]'); pg.wait_for_timeout(150)
        st = pg.evaluate("[whTabNow(), document.querySelector('.tab-more-panel').hidden, document.getElementById('tabBtnPilot').offsetParent !== null, document.getElementById('tabBtnPilot').textContent.trim()]")
        if st != ['pilot', True, True, 'Pilot']: out.append(f'390: a pick switches, closes the panel and shows the tab by its short name: {st}')
        pg.tap('.tab-more'); pg.wait_for_timeout(100); pg.keyboard.press('Escape'); pg.wait_for_timeout(100)
        if not pg.evaluate("document.querySelector('.tab-more-panel').hidden"): out.append('390: Esc closes More')
        if pg.evaluate(ROW)[1] != 1: out.append('390: one row with an analyzer in front')
        pg.tap('#tabBtnWh'); pg.wait_for_timeout(300)
        if not pg.evaluate("document.documentElement.scrollWidth <= innerWidth"): out.append('390: the Wormholes tab scrolls sideways')
        ctx.close()
    return out, errs

MUTANTS = [
    ('switching from a non-Intel tab', "  if(kind === 'j' && t === 'intel') switchTab('wh');", "  if(kind === 'j') switchTab('wh');", ('path',)),
    ('a k → k jump recorded', "  if(prev !== null && (j || jp) && !docked){", "  if(prev !== null && !docked){", ('path',)),
    ('docked counted as a hole', "    whSeen(sys, now, !!(j.station_id || j.structure_id));", "    whSeen(sys, now, false);", ('path', 'loc')),
    ('Intel in J-space not counting from the entrance (D14)', "function whIntelSys(){ if(itWhAside || !whS || !whInJ()) return undefined;", "function whIntelSys(){ return undefined;", ('path',)),
    ('statics coloured by the system, not where they lead', "  const k = whStcKind(code), [sh, long]", "  const k = WH_BAND[whCls(whFocus())] || 'x', [sh, long]", ('path', 'panel')),
    ('location read while another tab is in front', "  const S = whState(), want = whTabNow() === 'wh' && document.visibilityState !== 'hidden';", "  const S = whState(), want = document.visibilityState !== 'hidden';", ('path', 'loc')),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, 'the Wormholes tab: the table, the tab, the path, location, the System panel, adding, the map, a phone')
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
