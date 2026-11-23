"""Intel's own Home on the map (build queue 071; plan roadmap/intel-home-plan.md, mockup Claude outputs/home_mockup.html).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/intel_home_check.py [index.html]   -> 'FAILURES: N' (must be 0)

The owner: "also add the ability to set a "home" system from the intel map. use something like the in-game "home" system icon (just draw it
yourself)", then "Intel's own Home (Recommended)", "Route to Home,Jumps from Home on hover", "i would put the "home" button at the top to the
left of the "center on your system". it should "center on your home system"", "Home's menu (Recommended)", "Off until shown (Recommended)",
"Add it while set (Recommended)", "Yes, add it (Recommended)"; at the build review "go with your suggestion" (a phone: the top row holds only
+ − ⤢ ⌂ ⌖, the bridge lines button and Hide all routes go down the rail's column). Uses intel_check.py's made-up folder, mocks and names (you
in 1DQ1-A); real systems and gates, made-up pilots. Checks:
  * wide (1440 px): nothing stored, the house hidden and left of Center on your system; a right-click's menu ends with Set as Home (a
    menuitem, named by the system alone); the pick stores {v: 1, id, route: false}, closes the menu, shows the house ("Center on your Home
    (X)"); the house drawn on the canvas above Home; every hover's "N jumps from Home (X)" against a search written again here, "no gate
    route from Home" where there is none, "Your Home" on Home; the house centers Home in the free part at the same zoom, Center on your
    system still centers you; the legend's Home entry, no route line while it's off; Home's menu: Show the route / Remove Home, another
    system's "Set as Home (instead of X)"; the route shown: stored, drawn in the house colour even with hostiles reported at Home, kept
    when you move (the map's own kept routes cleared), Hide turns it off; in Home the route item is off "(you are here)"; Hide all routes
    clear of the top row with the house shown, and with the bridge lines button too; Remove Home clears storage, the house, the hover line,
    the legend entry and the button;
  * storage: an unknown version and bad JSON ignored, a route read back, another tab's change picked up; the Intel example has no Home;
  * a phone (390 px, touch): the top row's buttons 44 px and at most five, none under Hide all routes; the bridge lines button and Hide
    all routes down the rail's column under Near You's button; a kept system's tooltip buttons end with Set as Home; your own system's
    tooltip holds Home's buttons alone; no sideways scroll;
  * mutants, each must fail (see MUTANTS).
v2026.11.23.2 fails (no Home).
"""
import sys, os, json, time, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
_src = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
_src = _src[:_src.index('with sync_playwright() as p:')]
NS = {'__file__': os.path.join(HERE, 'intel_check.py'), '__name__': 'intel_check_prefix'}
exec(compile(_src, 'intel_check.py (first part)', 'exec'), NS)   # the made-up folder, mocks, names
globals().update({k: v for k, v in NS.items() if not k.startswith('__') and k not in ('check', 'fails')})
from playwright.sync_api import sync_playwright
check = NS['check']
PAGE = open(HTML, encoding='utf-8').read()

YOU = SYSID['1DQ1-A']
D0 = bfs(YOU)
by_d = {}
for s_, v in sorted(D0.items(), key=lambda kv: (kv[1], kv[0])): by_d.setdefault(v, []).append(s_)
def at(d, k=0): return by_d[d][k % len(by_d[d])]
def nm(i): return SYSNAME[i]
T0 = time.time()
HO, OTHER, NEXT = at(6, 0), at(4, 1), at(1, 0)   # Home 6 jumps out; another system; a neighbour you jump to

def start(b, html, w, errs, h=1000, touch=False):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch, device_scale_factor=2 if touch else 1)
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); route(ctx)
    pg = ctx.new_page(); pg.set_default_timeout(8000); pg.goto('file://' + html)
    pg.evaluate("([s]) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({channels: ['region.intel'], me: 95000001, range: 3, nearRange: 15, mapReach: 15, sound: false, notify: false, forget: 15, hideFriendly: true})); }", [SIDE])
    pg.reload(); pg.wait_for_timeout(400)
    setup_logs(pg); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg)
    pg.evaluate("() => document.querySelector('#intelPanel .it-map-box').scrollIntoView({block: 'center'})"); pg.wait_for_timeout(200)
    return ctx, pg

POS = "(id) => { const i = itGraphGet().at.get(id), r = itm.cv.getBoundingClientRect(); return [r.left + itm.Q[2 * i], r.top + itm.Q[2 * i + 1]]; }"
SHOW = "(id) => { itMapTip(-1); itRpMenuClose(false); itMapStartView(); itMapCenter(true, itGraphGet().at.get(id)); }"   # the start zoom (a gate 16 px), the system in the middle
MENU = "() => { const m = document.querySelector('.it-rp-menu'); return m ? {t: m.innerText.replace(/\\n+/g, ' | '), label: m.getAttribute('aria-label'), last: [...m.querySelectorAll('button')].pop().dataset.itHo || '', role: (m.querySelector('[data-it-ho]') || {getAttribute: () => ''}).getAttribute('role')} : null; }"
TIP = "() => itm.tip.hidden ? '' : itm.tip.innerText.replace(/\\n+/g, ' | ')"
STORED = "() => JSON.parse(localStorage.getItem('tvHome') || 'null')"
BTN = "() => { const b = itm.box.querySelector('.it-map-zoom [data-im-z=\"home\"]'); if(!b) return null; const r = b.getBoundingClientRect(), n = b.nextElementSibling; return {vis: !b.hidden && r.width > 0, title: b.title, beforeMe: !!n && n.dataset.imZ === 'me', w: Math.round(r.width), h: Math.round(r.height)}; }"
LEG = "() => itm.el.querySelector('.it-map-leg').innerText.replace(/\\n+/g, ' | ')"
# the canvas along the route to Home's stargate steps (the house colour #4fc3d9 vs the hostile red #c65b4e), and the house's own pixels
ROUTE_PX = """() => { const h = itHoIdx(); if(h < 0) return [0, 0, 0]; const T = itMapTable(), c = itm.cv.getContext('2d'), dpr = window.devicePixelRatio || 1, Q = itm.Q, pts = [];
  for(const [a, b] of itMapRoute(h)){ if(!T.adj[a].includes(b)) continue; for(const f of [0.35, 0.5, 0.65]){ const x = Q[2 * a] + (Q[2 * b] - Q[2 * a]) * f, y = Q[2 * a + 1] + (Q[2 * b + 1] - Q[2 * a + 1]) * f;
    if(x > 4 && y > 4 && x < itm.W - 4 && y < itm.H - 4) pts.push([Math.round(x * dpr) - 3, Math.round(y * dpr) - 3]); } }
  const read = () => pts.map(([x, y]) => c.getImageData(x, y, 7, 7).data), was = itHo.route;
  itHo.route = false; itMapDraw(); const off = read(); itHo.route = was; itMapDraw(); const on = read();
  const near = (d, k, rgb) => Math.abs(d[k] - rgb[0]) < 45 && Math.abs(d[k + 1] - rgb[1]) < 45 && Math.abs(d[k + 2] - rgb[2]) < 45;
  let cy = 0, red = 0;
  pts.forEach((_, n) => { const A = off[n], B = on[n]; for(let k = 0; k < B.length; k += 4){ if(Math.abs(A[k] - B[k]) + Math.abs(A[k + 1] - B[k + 1]) + Math.abs(A[k + 2] - B[k + 2]) < 60) continue; if(near(B, k, [79, 195, 217])) cy++; else if(near(B, k, [198, 91, 78])) red++; } });
  return [pts.length, cy, red]; }"""
HOUSE_PX = """() => { const b = itm.hoBox; if(!b) return 0; const c = itm.cv.getContext('2d'), dpr = window.devicePixelRatio || 1; let k = 0;
  for(let x = b[0]; x <= b[2]; x += 1) for(let y = b[1]; y <= b[3]; y += 1){ const d = c.getImageData(Math.round(x * dpr), Math.round(y * dpr), 1, 1).data; if(Math.abs(d[0] - 79) < 30 && Math.abs(d[1] - 195) < 30 && Math.abs(d[2] - 217) < 30) k++; }
  return k; }"""
RECTS = """() => { const R = (e) => { if(!e || e.hidden) return null; const r = e.getBoundingClientRect(); return r.width > 0 ? [r.left, r.top, r.right, r.bottom] : null; }, z = itm.box.querySelector('.it-map-zoom');
  const top = [...z.querySelectorAll('button')].filter(b => !b.hidden && b.dataset.imZ !== 'jb').map(R).filter(Boolean);
  return {box: R(itm.box), top, jb: R(z.querySelector('[data-im-z="jb"]')), clr: R(itm.box.querySelector(':scope > .it-map-clr')), rail: R(itm.box.querySelector('.it-map-rail')), search: R(itm.box.querySelector('.it-rp-search'))}; }"""
def over(a, b): return bool(a and b and a[0] < b[2] - 0.5 and a[2] > b[0] + 0.5 and a[1] < b[3] - 0.5 and a[3] > b[1] + 0.5)
BRIDGES_ON = "([a, b]) => { it.set.bridges = itSysName(a) + ' » ' + itSysName(b); it.set.bridgesOn = true; itWriteSet(); itMapRefresh(true); return !!itm.jbKey; }"
BRIDGES_OFF = "() => { it.set.bridges = ''; it.set.bridgesOn = false; itWriteSet(); itMapRefresh(true); }"

def rclick(pg, sid):
    pg.evaluate(SHOW, sid); pg.wait_for_timeout(100)
    x, y = pg.evaluate(POS, sid); pg.mouse.click(x, y, button='right'); pg.wait_for_timeout(200)
    return pg.evaluate(MENU)

def cases(b, html, parts=('wide', 'phone')):
    out, errs = [], []
    if 'wide' in parts:
        ctx, pg = start(b, html, 1440, errs)
        g = lambda: pg.evaluate(BTN)
        r = g()
        if pg.evaluate(STORED) is not None or not r or r['vis'] or not r['beforeMe']: out.append(f'to start: nothing stored, the house hidden, left of Center on your system ({pg.evaluate(STORED)}, {r})')
        m = rclick(pg, HO)
        if not m or 'Set as Home' not in m['t'] or 'instead of' in m['t'] or 'Avoid this system' not in m['t'] or m['last'] != 'set' or m['role'] != 'menuitem' or m['label'] != nm(HO):
            out.append(f'a right-click: the menu ends with Set as Home (a menuitem), named {nm(HO)!r} alone ({m})')
        pg.click('.it-rp-menu [data-it-ho="set"]'); pg.wait_for_timeout(250)
        r = g()
        if pg.evaluate(STORED) != {'v': 1, 'id': HO, 'route': False} or pg.evaluate("!!document.querySelector('.it-rp-menu')") or not r['vis'] or r['title'] != f'Center on your Home ({nm(HO)})':
            out.append(f'Set as Home: stored {pg.evaluate(STORED)}, the menu closed, the house shown with its title ({r})')
        pg.evaluate("() => itMapDraw()")
        hp = pg.evaluate(HOUSE_PX)
        if hp < 15: out.append(f'the house drawn on the canvas above Home: {hp} pixels in the house colour')
        # the hover: jumps from Home, against the search written again here
        DH = bfs(HO)
        for sid in (OTHER, YOU, at(9, 2)):
            pg.evaluate(SHOW, sid); pg.wait_for_timeout(80); x, y = pg.evaluate(POS, sid); pg.mouse.move(x, y); pg.wait_for_timeout(200)
            t, want = pg.evaluate(TIP), f"{DH[sid]} jump{'' if DH[sid] == 1 else 's'} from Home ({nm(HO)})"
            if want not in t: out.append(f'hovering {nm(sid)}: "{want}" ({t[:160]})')
        far = pg.evaluate("(ids) => { const g = itGraphGet(); return g.ids.find(id => !ids.includes(id)) || 0; }", list(DH))
        if far:
            t = pg.evaluate("(id) => { const i = itGraphGet().at.get(id); itMapTip(i, 60, 60); return itm.tip.innerText; }", far)
            if f'no gate route from Home ({nm(HO)})' not in t: out.append(f'a system with no gate route from Home: says so ({t[:160]})')
        pg.evaluate(SHOW, HO); pg.wait_for_timeout(80); x, y = pg.evaluate(POS, HO); pg.mouse.move(x, y); pg.wait_for_timeout(200)
        t = pg.evaluate(TIP)
        if 'Your Home' not in t or 'from Home' in t: out.append(f'hovering Home: "Your Home" ({t[:160]})')
        pg.mouse.move(3, 3); pg.wait_for_timeout(100)
        # the house button: Home in the middle of the free part, the zoom kept; Center on your system unchanged
        pg.evaluate("() => { itMapCenter(); itMapZoom(itm.W / 2, itm.H / 2, 1.6); }")
        k = pg.evaluate("itm.view.k"); pg.click('.it-map-zoom [data-im-z="home"]'); pg.wait_for_timeout(150)
        c = pg.evaluate("(id) => { const i = itGraphGet().at.get(id); return [itm.Q[2 * i] - itMapFreeX(), itm.Q[2 * i + 1] - itm.H / 2, itm.view.k]; }", HO)
        if abs(c[0]) > 2 or abs(c[1]) > 2 or abs(c[2] - k) > 1e-9: out.append(f'the house: Home in the middle of the free part at the same zoom ({c}, zoom before {k})')
        pg.click('.it-map-zoom [data-im-z="me"]'); pg.wait_for_timeout(150)
        c = pg.evaluate("() => [itm.Q[2 * itm.home] - itMapFreeX(), itm.Q[2 * itm.home + 1] - itm.H / 2]")
        if abs(c[0]) > 2 or abs(c[1]) > 2: out.append(f'Center on your system still centers you ({c})')
        lg = pg.evaluate(LEG)
        if f'Home ({nm(HO)})' not in lg or 'route to Home' in lg: out.append(f'the legend: Home once set, no route line while it is off ({lg[:200]})')
        # the menus
        m = rclick(pg, HO)
        if not m or 'Show the route to Home | Remove Home' not in m['t'] or 'Set as Home' in m['t']: out.append(f"Home's menu: Show the route to Home, Remove Home ({m})")
        pg.keyboard.press('Escape'); pg.wait_for_timeout(100)
        m = rclick(pg, OTHER)
        if not m or f'Set as Home (instead of {nm(HO)})' not in m['t'].replace(' | ', ' '): out.append(f'another system: "Set as Home (instead of {nm(HO)})" ({m})')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(100)
        # the route: stored, drawn in the house colour even with hostiles at Home, kept when you move
        W(pg, F_INTEL, line(time.time(), 'Scout Alt', f'{nm(HO)} 3 red')); tick(pg, 3200)
        rclick(pg, HO); pg.click('.it-rp-menu [data-it-ho="rt"]'); pg.wait_for_timeout(250)
        pg.evaluate("() => { itMapTip(-1); itMapFitView(); itMapDraw(); }")
        px = pg.evaluate(ROUTE_PX)
        if (pg.evaluate(STORED) or {}).get('route') is not True or pg.evaluate("!!document.querySelector('.it-rp-menu')"): out.append(f'Show the route to Home: stored {pg.evaluate(STORED)}, the menu closed')
        if px[0] < 3 or px[1] < 20 or px[2] * 4 > px[1]: out.append(f'the route to Home drawn in the house colour, though hostiles are reported at Home ({px[0]} places along it: {px[1]} pixels changed to the house colour, {px[2]} to red)')
        lg = pg.evaluate(LEG)
        if 'route to Home (kept)' not in lg: out.append(f'the legend adds the route line while it is shown ({lg[:200]})')
        pg.evaluate("(id) => itMapPin(id)", OTHER); pg.wait_for_timeout(100)
        W(pg, F_LOCAL_MAIN, line(time.time(), 'EVE System', f'Channel changed to Local : {nm(NEXT)}*')); tick(pg, 3500)
        pg.evaluate("() => { itMapTip(-1); itMapFitView(); itMapDraw(); }")
        px = pg.evaluate(ROUTE_PX); kept = pg.evaluate("() => [itSysName(itMySys()), itm.pinned.size]")
        if kept != [nm(NEXT), 0] or px[0] < 3 or px[1] < 20: out.append(f'a move: the map\'s kept routes cleared, the route to Home kept ({kept}, sampled {px})')
        # Hide all routes clear of the top row: the house shown, then the bridge lines button too
        pg.evaluate("(id) => itMapPin(id)", OTHER); pg.wait_for_timeout(100)
        R = pg.evaluate(RECTS)
        if not R['clr'] or any(over(R['clr'], t) for t in R['top']): out.append(f'Hide all routes clear of the top row with the house shown ({R})')
        if not pg.evaluate(BRIDGES_ON, [at(1, 1), at(9, 1)]): out.append('the bridges could not be turned on for the layout check')
        pg.evaluate("(id) => { if(!itm.pinned.has(id)) itMapPin(id); }", OTHER); pg.wait_for_timeout(100)
        R = pg.evaluate(RECTS)
        if not R['clr'] or not R['jb'] or any(over(R['clr'], t) for t in R['top'] + [R['jb']]): out.append(f'Hide all routes clear of the top row with the house and the bridge lines button ({R})')
        pg.evaluate(BRIDGES_OFF)
        m = rclick(pg, HO); pg.click('.it-rp-menu [data-it-ho="rt"]'); pg.wait_for_timeout(200)
        if (pg.evaluate(STORED) or {}).get('route') is not False or pg.evaluate("itHoRouteOn()"): out.append(f'Hide the route to Home turns it off ({pg.evaluate(STORED)}) [the item read: {m and m["t"]}]')
        if not m or 'Hide the route to Home' not in m['t']: out.append(f'the item reads Hide while the route is shown ({m})')
        # in Home: the route item off "(you are here)"
        W(pg, F_LOCAL_MAIN, line(time.time() + 1, 'EVE System', f'Channel changed to Local : {nm(HO)}*')); tick(pg, 3500)
        m = rclick(pg, HO)
        dis = pg.evaluate("() => { const b = document.querySelector('.it-rp-menu [data-it-ho=\"rt\"]'); return b ? b.disabled : null; }")
        if dis is not True or not m or '(you are here)' not in m['t']: out.append(f'in Home: the route item off, "(you are here)" ({dis}, {m})')
        pg.click('.it-rp-menu [data-it-ho="off"]'); pg.wait_for_timeout(250)
        t = pg.evaluate("(id) => { const i = itGraphGet().at.get(id); itMapTip(i, 60, 60); return itm.tip.innerText; }", OTHER)
        if pg.evaluate(STORED) is not None or g()['vis'] or 'from Home' in t or 'Home (' in pg.evaluate(LEG) or pg.evaluate("itm.hoBox") is not None:
            out.append(f'Remove Home: storage, the button, the hover line, the legend entry and the house gone ({pg.evaluate(STORED)}, {g()})')
        # storage both ways, another tab, the Intel example
        r = pg.evaluate("""(id) => { const o = [];
          localStorage.setItem('tvHome', JSON.stringify({v: 2, id})); itHoRead(); o.push(itHo.id);
          localStorage.setItem('tvHome', 'not json'); itHoRead(); o.push(itHo.id);
          localStorage.setItem('tvHome', JSON.stringify({v: 1, id: -4})); itHoRead(); o.push(itHo.id);
          localStorage.setItem('tvHome', JSON.stringify({v: 1, id, route: true})); itHoRead(); o.push(itHo.id === id && itHo.route);
          localStorage.removeItem('tvHome'); itHoRead();
          localStorage.setItem('tvHome', JSON.stringify({v: 1, id, route: false})); window.dispatchEvent(new StorageEvent('storage', {key: 'tvHome'}));
          const b = itm.box.querySelector('[data-im-z="home"]'); o.push(itHo.id === id && !b.hidden, itMapKey().includes('|ho:' + id + '.0'));
          o.push(itExSandbox(() => [itHoIdx(), itHoTipHtml(0), itHoLegHtml(), itHoBtnsHtml(0, false)]));
          return o; }""", OTHER)
        if r[:6] != [0, 0, 0, True, True, True] or r[6] != [-1, '', '', '']: out.append(f'storage (v2, bad JSON, a bad id ignored; a route read back; another tab\'s change; the map key) and the Intel example\'s sandbox: {r}')
        if not pg.evaluate("() => document.scrollingElement.scrollWidth <= innerWidth + 1"): out.append('1440 px: sideways scroll')
        ctx.close()
    if 'phone' in parts:
        ctx, pg = start(b, html, 390, errs, h=844, touch=True)
        pg.evaluate("(id) => { localStorage.setItem('tvHome', JSON.stringify({v: 1, id, route: false})); window.dispatchEvent(new StorageEvent('storage', {key: 'tvHome'})); }", HO)
        pg.evaluate("(id) => itMapPin(id)", OTHER); pg.wait_for_timeout(200)
        for bridges in (False, True):
            if bridges and not pg.evaluate(BRIDGES_ON, [at(1, 1), at(9, 1)]): out.append('390 px: the bridges could not be turned on'); continue
            pg.evaluate("(id) => { if(!itm.pinned.has(id)) itMapPin(id); }", OTHER); pg.wait_for_timeout(200)
            R = pg.evaluate(RECTS); w = 'with the bridge lines button' if bridges else 'without bridges'
            if len(R['top']) != 5 or any(t[2] - t[0] < 44 or t[3] - t[1] < 44 for t in R['top']) or any(t[0] < R['box'][0] for t in R['top']):
                out.append(f'390 px {w}: the top row\'s five buttons (+ − ⤢ ⌂ ⌖), 44 px, inside the map ({R["top"]})')
            if not R['clr'] or any(over(R['clr'], t) for t in R['top'] + [R['search']]) or abs(R['clr'][2] - R['rail'][2]) > 1 or R['clr'][1] < R['rail'][3] or R['clr'][2] - R['clr'][0] < 44:
                out.append(f'390 px {w}: Hide all routes a 44 px button down the rail\'s column, under Near You\'s button ({R})')
            if bridges and (not R['jb'] or abs(R['jb'][2] - R['rail'][2]) > 1 or R['jb'][1] < R['rail'][3] or R['clr'][1] < R['jb'][3] or any(over(R['jb'], t) for t in R['top'])):
                out.append(f'390 px: the bridge lines button down the rail\'s column, Hide all routes under it ({R})')
        pg.evaluate(BRIDGES_OFF)
        nm_ = pg.evaluate("() => [itm.box.querySelector(':scope > .it-map-clr').getAttribute('aria-label'), getComputedStyle(itm.box.querySelector(':scope > .it-map-clr > svg')).display]")
        if nm_ != ['Hide all routes', 'block']: out.append(f'390 px: Hide all routes an icon with its name ({nm_})')
        # a kept system's tooltip: its buttons end with Set as Home; your own system's: Home's buttons alone
        r = pg.evaluate("(id) => { const i = itGraphGet().at.get(id); if(!itm.pinned.has(id)) itMapPin(id); itMapTip(i, 40, 40); const bs = [...itm.tip.querySelectorAll('button')]; return [bs.map(b => b.innerText.replace(/\\s+/g, ' ').trim()), bs.every(b => b.getBoundingClientRect().height >= 44), bs.every(b => !b.hasAttribute('role'))]; }", OTHER)
        if not r[0] or not r[0][-1].startswith('Set as Home (instead of') or not r[1] or not r[2]: out.append(f'390 px: a kept system\'s tooltip buttons end with Set as Home, 44 px, plain buttons ({r})')
        r = pg.evaluate("() => { itMapTip(itm.home, 40, 40); return [...itm.tip.querySelectorAll('button')].map(b => b.dataset.itHo || b.dataset.itRpGo || b.dataset.itRpAv || '?'); }")
        if r != ['set']: out.append(f'390 px: your own system\'s tooltip holds Set as Home alone ({r})')
        if not pg.evaluate("() => document.scrollingElement.scrollWidth <= innerWidth + 1"): out.append('390 px: sideways scroll')
        ctx.close()
    return out, errs

MUTANTS = [
    ('the route to Home coloured by its report', "    c.strokeStyle = i === hoR ? itMapCol('--wh-st-home', '#4fc3d9') : rp && rp.side !== 'clear' ? C[rp.side] : C.cyan;", "    c.strokeStyle = rp && rp.side !== 'clear' ? C[rp.side] : C.cyan;", ('wide',)),
    ('the route to Home not drawn', "if(hoR >= 0 && D[hoR] > 0) show.add(hoR);", "", ('wide',)),
    ('jumps counted from you, not Home', "q = [h]; D[h] = 0;", "q = [itm.home]; D[itm.home] = 0;", ('wide',)),
    ('the house button centers on you', "else if(z.dataset.imZ === 'home') itMapCenter(true, itHoIdx());", "else if(z.dataset.imZ === 'home') itMapCenter();", ('wide',)),
    ('the house button never shown', "const off = itHoIdx() < 0 || itm.box.classList.contains('nomap')", "const off = true", ('wide',)),
    ('no house drawn', "  itHoDraw(c, X, Y, big, r);   // 071", "  // 071", ('wide',)),
    ("Home's own menu offers Set as Home", "if(gid === itHo.id && itHoIdx() >= 0){", "if(false){", ('wide',)),
    ('a version 2 value read', "o.v === 1 && Number.isInteger(o.id)", "Number.isInteger(o.id)", ('wide',)),
    ('another tab not heard', "if(e.key === IT_HO_KEY){ itHoRead(); itHoChanged(); }", "if(e.key === 'tvHomeX'){ itHoRead(); itHoChanged(); }", ('wide', 'phone')),
    ('the Intel example keeps Home', "const hoAside = itHoAside; itHoAside = true;", "const hoAside = itHoAside;", ('wide',)),
    ('wide: Hide all routes not moved for the house', ".it-map-box:has(.it-map-zoom [data-im-z=\"home\"]:not([hidden])) button.it-map-clr{right:182px;}", ".x-none{right:182px;}", ('wide',)),
    ('a phone: Hide all routes back at the top left', ".it-map-box button.it-map-clr{top:160px; left:auto; right:8px; width:44px; height:44px; min-height:44px; padding:0;}", ".it-map-box button.it-map-clr{top:8px; left:8px; right:auto; min-height:44px;}", ('phone',)),
    ('a phone: the bridge lines button in the top row', ".it-map-zoom button[data-im-z=\"jb\"]{position:absolute; top:152px; right:0;}", ".x-none{top:152px;}", ('phone',)),
    ("a phone: your own system's tooltip without Home", "if(i === itm.home) return itRpTouch() && !itHoAside ?", "if(i === itm.home) return false ?", ('phone',)),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, "Intel's Home: the menu, the house, the hover, centring, the route, the legend, storage, the example, the phone")
    check(not errs, f'no page errors {errs[:3]}')
    if '--no-mutants' not in sys.argv:
        for name, old, new, parts in MUTANTS:
            if PAGE.count(old) != 1: check(False, f'mutant "{name}": its line isn\'t in the page once'); continue
            with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f:
                f.write(PAGE.replace(old, new)); mp = f.name
            try:
                try: mo, me = cases(b, mp, parts)
                except Exception as e: mo, me = [f'{type(e).__name__}: {str(e).splitlines()[0]}'], []   # a step it can't take (a button the mutant hid) is a failure too
                check(bool(mo) or bool(me), f'mutant "{name}" fails ({(mo or me or ["nothing"])[0][:90]})')
            finally: os.unlink(mp)
    b.close()
print('FAILURES:', NS['fails'])
sys.exit(1 if NS['fails'] else 0)
