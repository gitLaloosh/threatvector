"""Checks for the Intel map Home mockup: python3 -I test_ho.py home_mockup.html [shots dir]. A fresh page per width, 1440 and 390 px."""
import os, sys
from playwright.sync_api import sync_playwright
PAGE = 'file://' + os.path.abspath(sys.argv[1]); SHOTS = sys.argv[2] if len(sys.argv) > 2 else None
if SHOTS: os.makedirs(SHOTS, exist_ok=True)
fails, n = [], 0
HOME = 30000736   # KOG-TA in the mock
def ok(c, what):
    global n; n += 1
    if not c: fails.append(what); print('FAIL', what)
def page(p, w, h):
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': w, 'height': h}, has_touch=w < 600, is_mobile=w < 600, bypass_csp=True); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(PAGE); pg.wait_for_function('window.__MKREADY || window.__MKERR', timeout=90000)
    ok(not pg.evaluate('window.__MKERR'), f'{w}: boot ' + str(pg.evaluate('window.__MKERR')))
    return b, pg, errs
def scene(pg, s, w):
    pg.evaluate(f"HOscene('{s}')"); pg.wait_for_timeout(500)
    if SHOTS: pg.evaluate("itm.box.scrollIntoView()"); pg.screenshot(path=os.path.join(SHOTS, f'{s}_{w}.png'))
def menu(pg): return pg.evaluate("(document.querySelector('.it-rp-menu') || {}).innerText || ''").replace('\n', ' | ')
def tip(pg): return pg.evaluate("itm.tip.hidden ? '' : itm.tip.innerText").replace('\n', ' | ')
def stored(pg): return pg.evaluate("JSON.parse(localStorage.getItem('tvHome') || 'null')")
def rail(pg): return pg.evaluate("(() => { const b = itm.box.querySelector('.it-map-zoom [data-it-home-go]'); if(!b) return null; const r = b.getBoundingClientRect(), n = b.nextElementSibling; return {vis: getComputedStyle(b).display !== 'none' && r.width > 0, w: r.width, h: r.height, title: b.title, beforeMe: !!n && n.dataset.imZ === 'me'}; })()")
def menu_on_home(pg): pg.evaluate("itMapTip(-1); itRpMenuClose(false); const i = itGraphGet().at.get(HO.id); const p = HOpos(i); itRpMenuOpen(i, p[0] + 10, p[1] + 10);")
def nohscroll(pg): return pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
# an independent count of jumps: a plain search over the gate table, written again here (not the mockup's hoDist)
BFS = """(src) => { const T = itMapTable(), at = itGraphGet().at, s = at.get(src), D = new Array(T.n).fill(-1), q = [s]; D[s] = 0;
  for(let k = 0; k < q.length; k++){ const x = q[k]; for(const y of T.adj[x]) if(D[y] < 0){ D[y] = D[x] + 1; q.push(y); } } return D; }"""
with sync_playwright() as p:
    for w, h in [(1440, 900), (390, 844)]:
        b, pg, errs = page(p, w, h)
        phone = w < 600
        # no Home yet: nothing stored, the rail button hidden, the menu offers Set as Home with no "instead of"
        ok(stored(pg) is None, f'{w}: nothing stored to start')
        r = rail(pg); ok(r and not r['vis'] and r['beforeMe'], f'{w}: the house button hidden with no Home, left of Center on your system {r}')
        scene(pg, 'none', w); m = menu(pg)
        ok('Set as Home' in m and 'instead of' not in m and 'Avoid this system' in m, f'{w}: the menu adds Set as Home under Avoid {m}')
        ok(pg.evaluate("[...document.querySelectorAll('.it-rp-menu button')].pop().dataset.itHome === 'set' && document.querySelector('.it-rp-menu [data-it-home]').getAttribute('role') === 'menuitem'"), f'{w}: last item, role menuitem')
        r = rail(pg); ok(r and not r['vis'], f'{w}: still hidden in the none scene {r}')
        # set Home from the menu (the real click path)
        pg.evaluate("HO.id = 0; HO.route = false; hoSave(); hoRailPaint(); const i = itGraphGet().at.get(%d); const p = HOpos(i); itRpMenuOpen(i, p[0] + 10, p[1] + 10);" % HOME)
        pg.click('.it-rp-menu [data-it-home=set]'); pg.wait_for_timeout(200)
        ok(stored(pg) == {'v': 1, 'id': HOME, 'route': False}, f'{w}: stored as tvHome {stored(pg)}')
        ok(not pg.evaluate("document.querySelector('.it-rp-menu')"), f'{w}: the pick closes the menu')
        r = rail(pg); ok(r and r['vis'] and r['title'] == 'Center on your Home (KOG-TA)', f'{w}: the house button shows {r}')
        if phone: ok(r and r['w'] >= 44 and r['h'] >= 44, f'{w}: house button 44 px {r}')
        # the house button centers the map on Home, in the part no panel covers (as Center on your system does for you)
        pg.evaluate("itMapCenter(); itMapZoom(itm.W / 2, itm.H / 2, 1.6);"); pg.evaluate("itm.box.scrollIntoView()")
        pg.click('[data-it-home-go]'); pg.wait_for_timeout(150)
        c = pg.evaluate("(() => { const i = itGraphGet().at.get(%d); return [HOpos(i)[0] - itMapFreeX(), HOpos(i)[1] - itm.H / 2]; })()" % HOME)
        ok(abs(c[0]) < 2 and abs(c[1]) < 2, f'{w}: Home centered after the press {c}')
        pg.evaluate("itMapCenter()")
        c = pg.evaluate("(() => { const i = itm.home; return [HOpos(i)[0] - itMapFreeX(), HOpos(i)[1] - itm.H / 2]; })()")
        ok(abs(c[0]) < 2 and abs(c[1]) < 2, f'{w}: Center on your system still centers on you {c}')
        leg = lambda: pg.evaluate("itm.el.querySelector('.it-map-leg').innerText").replace('\n', ' | ')
        ok('Home (KOG-TA)' in leg() and 'route to Home' not in leg(), f'{w}: the legend shows Home once set, no route line while it is off {leg()[:300]}')
        # the menu on Home: Remove Home; on another system: Set as Home (instead of KOG-TA)
        scene(pg, 'menu', w); m = menu(pg)
        ok('Show the route to Home | Remove Home' in m and 'Set as Home' not in m, f'{w}: Show the route and Remove Home on Home {m}')
        pg.evaluate("itRpMenuClose(false); const i = itGraphGet().at.get(30000774); const p = HOpos(i); itRpMenuOpen(i, p[0] + 10, p[1] + 10);")
        m = menu(pg); ok('Set as Home (instead of KOG-TA)' in m.replace(' | ', ' '), f'{w}: replacing names the old Home {m}')
        pg.evaluate("itRpMenuClose(false)")
        # hover: jumps from Home, checked against the independent search
        scene(pg, 'tip', w); t = tip(pg)
        D = pg.evaluate(f"({BFS})({HOME})"); i = pg.evaluate("itGraphGet().at.get(30000774)")
        want = f"{D[i]} jump{'' if D[i] == 1 else 's'} from Home (KOG-TA)"
        ok(want in t, f'{w}: hover says "{want}" {t[:200]}')
        far = pg.evaluate(f"(() => {{ const D = ({BFS})({HOME}); return D.findIndex(d => d < 0); }})()")
        if far >= 0:
            ft = pg.evaluate(f"(() => {{ const i = {far}; itMapTip(i, 100, 100); return itm.tip.innerText; }})()")
            ok('no gate route from Home (KOG-TA)' in ft, f'{w}: unreachable systems say so {ft[:160]}')
        # a sample of systems against the search (the cache keyed by Home)
        bad = pg.evaluate(f"(() => {{ const D = ({BFS})({HOME}), H = hoDist(); let b = 0; for(let i = 0; i < D.length; i += 37) if(D[i] !== H[i]) b++; return b; }})()")
        ok(bad == 0, f'{w}: hoDist matches the plain search ({bad} differ)')
        # the route: from Home's menu, a kept route in the Home colour, kept after the map's own pins are cleared
        menu_on_home(pg); pg.click('.it-rp-menu [data-it-home=rt]'); pg.wait_for_timeout(150)
        ok(stored(pg)['route'] is True and not pg.evaluate("document.querySelector('.it-rp-menu')"), f'{w}: Show the route stores it and closes the menu')
        ok(pg.evaluate("window.__MKhomeRoute().includes(%d) && window.__MKhomeId() === %d" % (HOME, HOME)), f'{w}: the route is drawn to Home')
        ok('route to Home (kept)' in leg(), f'{w}: the legend adds the route line while it is shown')
        pg.evaluate("itm.pinned.clear(); itMapRefresh(true); itMapDraw();")
        ok(pg.evaluate("window.__MKhomeRoute().includes(%d)" % HOME), f'{w}: kept when the map clears its pins (a move)')
        menu_on_home(pg); m = menu(pg); ok('Hide the route to Home' in m, f'{w}: the item reads Hide while on {m}')
        pg.click('.it-rp-menu [data-it-home=rt]'); pg.wait_for_timeout(150)
        ok(stored(pg)['route'] is False and pg.evaluate("window.__MKhomeRoute().length") == 0, f'{w}: Hide turns it off')
        scene(pg, 'route', w); scene(pg, 'center', w); scene(pg, 'routeout', w)
        # you in Home: "Your Home", the rail button off (nothing to route)
        scene(pg, 'here', w); t = tip(pg)
        ok('you are here' in t and 'Your Home' in t and 'jumps from Home' not in t, f'{w}: in Home the hover says Your Home {t}')
        if phone: ok('Remove Home' in t and pg.evaluate("itm.tip.querySelector('[data-it-home=rt]').disabled"), f'{w}: a phone gets Remove Home in your own system\'s tooltip, the route item off {t}')
        else:
            menu_on_home(pg); ok(pg.evaluate("document.querySelector('.it-rp-menu [data-it-home=rt]').disabled") and '(you are here)' in menu(pg), f'{w}: the route item off while you are in Home {menu(pg)}')
        # a phone: the tooltip's buttons on a kept system end with Set as Home
        if phone:
            scene(pg, 'phone', w); t = tip(pg)
            ok(t.rstrip().endswith('Set as Home (instead of KOG-TA)') and 'Avoid this system' in t, f'{w}: tooltip buttons end with Set as Home {t[-200:]}')
            ok(pg.evaluate("[...itm.tip.querySelectorAll('button')].every(b => b.getBoundingClientRect().height >= 44)"), f'{w}: tooltip buttons 44 px')
            ok(pg.evaluate("!itm.tip.querySelector('[data-it-home]').hasAttribute('role')"), f'{w}: plain buttons in the tooltip group')
        # Remove Home: storage cleared, house gone, rail hidden
        menu_on_home(pg)
        pg.click('.it-rp-menu [data-it-home=off]'); pg.wait_for_timeout(200)
        ok(stored(pg) is None and pg.evaluate("HO.id") == 0 and not rail(pg)['vis'], f'{w}: Remove Home clears it and hides the house button {stored(pg)} {rail(pg)}')
        ok('Home (' not in leg(), f'{w}: no legend entry once removed')
        t = pg.evaluate("(() => { const i = itGraphGet().at.get(30000774); itMapTip(i, 50, 50); return itm.tip.innerText; })()")
        ok('from Home' not in t, f'{w}: no Home line once removed')
        # storage safe both ways: junk ignored, an older page's key untouched
        pg.evaluate("localStorage.setItem('tvHome', '{\\\"v\\\":2,\\\"id\\\":5}'); HO.id = 0; hoRead();")
        ok(pg.evaluate("HO.id") == 0, f'{w}: an unknown version is ignored')
        pg.evaluate("localStorage.setItem('tvHome', 'not json'); hoRead();")
        ok(pg.evaluate("HO.id") == 0, f'{w}: bad JSON is ignored')
        pg.evaluate("localStorage.removeItem('tvHome')")
        # info text: the [Map] line, under the cap
        words = pg.evaluate("CARD_INFO.intel.join(' ').replace(/<[^>]+>/g, ' ').split(/\\s+/).filter(Boolean).length")
        ok(words <= 740, f'{w}: Intel info {words} words, cap raised to ~738 (the owner: "Raise to ~738 (Recommended)")')
        ok(pg.evaluate("CARD_INFO.intel.some(p => p.startsWith('[Map]') && p.includes('Set as Home'))"), f'{w}: the [Map] line names Set as Home')
        ok(nohscroll(pg), f'{w}: no sideways scroll')
        ok(not errs, f'{w}: no page errors {errs[:2]}')
        b.close()
print(f'{n - len(fails)}/{n} passed')
sys.exit(1 if fails else 0)
