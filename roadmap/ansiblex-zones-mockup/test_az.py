"""Checks for the Ansiblex zones mockup (python3 -I test_az.py ansiblex_zones_mockup.html shots/). A fresh page per case, 1440 and 390 px."""
import os, sys
from playwright.sync_api import sync_playwright
PAGE = 'file://' + os.path.abspath(sys.argv[1]); SHOTS = sys.argv[2]; os.makedirs(SHOTS, exist_ok=True)
fails, n = [], 0
def ok(c, what):
    global n; n += 1
    if not c: fails.append(what); print('FAIL', what)
JS_PATH = '''(n) => { const g = itGraphGet(), i = g.at.get(it.names.byLower.get(n.toLowerCase())), p = itRpPath(i); return p ? p.map(x => itSysName(g.ids[x])) : null; }'''
def at_px(pg, name):
    return pg.evaluate('''(n) => { const g = itGraphGet(), i = g.at.get(it.names.byLower.get(n.toLowerCase())), r = itm.el.querySelector('canvas').getBoundingClientRect(); return [r.left + itm.Q[2*i], r.top + itm.Q[2*i+1]]; }''', name)
def bridge_mid(pg, a, b):
    return pg.evaluate('''([a, b]) => { const g = itGraphGet(), A = g.at.get(it.names.byLower.get(a.toLowerCase())), B = g.at.get(it.names.byLower.get(b.toLowerCase()));
      const [p, q] = A < B ? [A, B] : [B, A], Q = itm.Q, x1 = Q[2*p], y1 = Q[2*p+1], x2 = Q[2*q], y2 = Q[2*q+1], mx = (x1+x2)/2, my = (y1+y2)/2, dx = x2-x1, dy = y2-y1, cx = mx - dy*0.22, cy = my + dx*0.22;
      const r = itm.el.querySelector('canvas').getBoundingClientRect(); return [r.left + 0.25*x1 + 0.5*cx + 0.25*x2, r.top + 0.25*y1 + 0.5*cy + 0.25*y2]; }''', [a, b])
def page(p, w, h):
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': w, 'height': h}, has_touch=w < 600, is_mobile=w < 600); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(PAGE); pg.wait_for_function('window.__MKREADY || window.__MKERR', timeout=40000)
    ok(not pg.evaluate('window.__MKERR'), f'{w}: boot ' + str(pg.evaluate('window.__MKERR')))
    pg.wait_for_timeout(500)
    return b, pg, errs
def open_settings(pg):
    pg.evaluate("document.querySelector('[data-it-act=gear]').click()"); pg.wait_for_timeout(400)
with sync_playwright() as p:
    for w, h in [(1440, 900), (390, 844)]:
        # 1. rows: zones each way, the not-yours bridge left out
        b, pg, errs = page(p, w, h)
        rows = pg.evaluate('AZ.bridges().rows.map(r => ({z: r.z, use: r.use, why: r.why}))')
        ok(rows[0]['z'] == [1, 1] and rows[0]['use'] == [True, True], f'{w}: 8G-2FP ⇄ 8EF-58 zone 1 both ways, used both ways')
        ok(rows[1]['z'] == [2, 1] and rows[1]['use'] == [False, True], f'{w}: 4M-QXK → F39H-1 zone 2 (not used), back zone 1 (used)')
        ok(rows[2]['z'] == [2, 2] and rows[2]['use'] == [False, False], f'{w}: 3AE-CP ⇄ EUU-4N zone 2 both ways, unused')
        ok(rows[3]['z'] is None and 'Mockup Raiders' in rows[3]['why'], f'{w}: SHBF-V bridge held by another alliance, left out')
        # 2. routes
        p8 = pg.evaluate(JS_PATH, '8EF-58'); ok(p8 == ['C-J6MT', '8-WYQZ', '8G-2FP', '8EF-58'], f'{w}: route to 8EF-58 takes the free bridge (3 jumps) {p8}')
        pf = pg.evaluate(JS_PATH, 'F39H-1'); ok(pf and '4M-QXK' not in pf, f'{w}: route to F39H-1 avoids the zone-2 arrival {pf}')
        ok(pg.evaluate("itm.D[itGraphGet().at.get(it.names.byLower.get('8ef-58'))]") == 10, f'{w}: the map\'s jump count stays by stargate (10)')
        open_settings(pg)
        zl = pg.locator('[data-az-zone]'); ok(zl.count() == 5, f'{w}: five zone checkboxes')
        ok(pg.evaluate("[...document.querySelectorAll('[data-az-zone]')].map(x => x.checked).join()") == 'true,false,false,false,false', f'{w}: zone 1 only by default')
        ok('8G-2FP (Mockup Coalition)' in pg.inner_text('.it-az-st') and '3 of 4' in pg.inner_text('.it-az-st'), f'{w}: status names the capital and the count: ' + pg.inner_text('.it-az-st'))
        if w < 600:
            hh = pg.evaluate("[...document.querySelectorAll('.it-az-zones label')].map(l => l.getBoundingClientRect().height)")
            ok(min(hh) >= 44, f'{w}: zone rows 44 px on a phone {hh}')
        pg.locator('[data-az-zone="2"]').check(); pg.wait_for_timeout(300)
        pf2 = pg.evaluate(JS_PATH, 'F39H-1'); ok(pf2 and pf2[-2:] == ['4M-QXK', 'F39H-1'], f'{w}: with zone 2 ticked, F39H-1 by the bridge {pf2}')
        ok(pg.evaluate('AZ.bridges().rows[2].use.join()') == 'true,true', f'{w}: zone 2 ticked: 3AE-CP ⇄ EUU-4N used both ways')
        box = pg.locator('[data-az-box]'); box.scroll_into_view_if_needed(); pg.wait_for_timeout(200)
        txt = box.inner_text()
        ok('→ 8EF-58 zone 1 · free' in txt and '→ F39H-1 zone 2 · ×2' in txt and 'held by Mockup Raiders' in txt, f'{w}: list rows show zones and the warning')
        box.screenshot(path=f'{SHOTS}/{w}_bridges_box.png')
        rp = pg.locator('[data-it-rp-box]'); rp.scroll_into_view_if_needed(); rp.screenshot(path=f'{SHOTS}/{w}_routes_box.png')
        sw = pg.evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth'); ok(sw <= 0, f'{w}: no sideways scroll ({sw})')
        ok(not errs, f'{w}: no page errors {errs}')
        b.close()
        # 3. the map: hover a bridge, hover a destination (route step), menu
        b, pg, errs = page(p, w, h)
        pg.evaluate("document.querySelector('.it-map-box').scrollIntoView({block: 'center'})"); pg.wait_for_timeout(300)
        x, y = bridge_mid(pg, '4M-QXK', 'F39H-1')
        if w < 600: pg.mouse.click(x, y)
        else: pg.mouse.move(x, y)
        pg.wait_for_timeout(300)
        tip = pg.inner_text('.it-map-tip')
        ok('Jump bridge' in tip and 'F39H-1: zone 2 · ×2' in tip and '4M-QXK: zone 1 · free' in tip and 'toward 4M-QXK only' in tip, f'{w}: bridge hover shows both zones and use: {tip!r}')
        pg.locator('.it-map-box').screenshot(path=f'{SHOTS}/{w}_bridge_hover.png')
        if w >= 600:
            x, y = at_px(pg, '8EF-58'); pg.mouse.move(x, y); pg.wait_for_timeout(300)
            tip = pg.inner_text('.it-map-tip')
            ok('jump bridge 8G-2FP → 8EF-58 · arriving in zone 1 · free' in tip and "Threat Vector's route:" not in tip, f'{w}: route step line, no "(shortest N)" line when the route is the shortest over its own graph: {tip!r}')
            pg.locator('.it-map-box').screenshot(path=f'{SHOTS}/{w}_route_step.png')
            pg.mouse.click(x, y, button='right'); pg.wait_for_timeout(300)
            mt = pg.inner_text('.it-rp-menu'); ok('3 jumps · 1 by jump bridge' in mt, f'{w}: menu sub line {mt!r}')
            pg.locator('.it-map-box').screenshot(path=f'{SHOTS}/{w}_menu.png')
        else:
            pg.evaluate('''() => { const g = itGraphGet(), i = g.at.get(it.names.byLower.get('8ef-58')); itm.view.tx += itm.W * 0.5 - itm.Q[2*i]; itm.view.ty += itm.H * 0.3 - itm.Q[2*i+1]; itMapTip(-1); itMapDraw(); }''')
            pg.wait_for_timeout(200); x, y = at_px(pg, '8EF-58'); pg.mouse.click(x, y); pg.wait_for_timeout(300)
            tip = pg.inner_text('.it-map-tip')
            ok('jump bridge 8G-2FP → 8EF-58' in tip and '1 by jump bridge' in tip, f'{w}: phone press shows the step and the button line: {tip!r}')
            pg.locator('.it-map-box').screenshot(path=f'{SHOTS}/{w}_route_step.png')
        ok(not errs, f'{w}: no page errors (map) {errs}')
        b.close()
        # 4. coming home: you in F39H-1, the free return
        b, pg, errs = page(p, w, h)
        pg.evaluate("window.__MKlocal('F39H-1')"); pg.wait_for_function("itSysName(itGraphGet().ids[itm.home]) === 'F39H-1'", timeout=15000); pg.wait_for_timeout(400)
        pr = pg.evaluate(JS_PATH, '4M-QXK'); ok(pr == ['F39H-1', '4M-QXK'], f'{w}: from F39H-1 the free jump home {pr}')
        b.close()
        # 4b. 041's switch off: no zones, stargate routes, the status says so
        b, pg, errs = page(p, w, h)
        open_settings(pg); pg.locator('[data-az-on]').uncheck(); pg.wait_for_timeout(300)
        ok(pg.evaluate('AZ.bridges().edges.length') == 0, f'{w}: switch off: no bridge used')
        p8o = pg.evaluate(JS_PATH, '8EF-58'); ok(p8o and len(p8o) == 11, f'{w}: switch off: route to 8EF-58 by stargate (10 jumps) {p8o}')
        st = pg.inner_text('.it-az-st'); ok('is off' in st and 'Jump bridges box' in st, f'{w}: status says the switch is off: {st}')
        ok(pg.locator('[data-az-box] .it-az-zl').count() == 0, f'{w}: switch off: rows show no zones')
        ok(pg.evaluate("(() => { const r = document.querySelector('[data-it-rp-box]'), b = document.querySelector('[data-az-box]'); return !!(r && b && (r.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING)); })()"), f'{w}: the Jump bridges box comes after Routes')
        pg.locator('[data-az-on]').check(); pg.wait_for_timeout(300)
        ok(pg.evaluate('AZ.bridges().edges.length') > 0, f'{w}: switch on again: bridges by zone')
        ok(not errs, f'{w}: no page errors (switch) {errs}')
        b.close()
        # 5. logged out, capital lost
        b, pg, errs = page(p, w, h)
        pg.evaluate("document.querySelector('#mkAz [data-mk=login]').click()"); pg.wait_for_timeout(300)
        r3 = pg.evaluate('AZ.bridges().rows[3].why'); ok('different alliances' in r3, f'{w}: logged out, a bridge between two alliances is left out ({r3})')
        ok(pg.evaluate('AZ.bridges().rows[0].use.join()') == 'true,true', f'{w}: logged out, your own bridges still used (sov holder taken as yours)')
        pg.evaluate("document.querySelector('#mkAz [data-mk=cap]').click()"); pg.wait_for_function('AZ.sov', timeout=5000); pg.wait_for_timeout(300)
        ok(pg.evaluate('AZ.bridges().edges.length') == 0 and pg.evaluate('AZ.bridges().rows[0].z.join()') == '5,5', f'{w}: capital lost: every jump zone 5, none used')
        pg.evaluate("document.querySelector('#mkAz [data-mk=login]').click()"); pg.wait_for_timeout(300)
        open_settings(pg); st = pg.inner_text('.it-az-st'); ok('no capital right now' in st, f'{w}: status says the capital is gone: {st}')
        ok(not errs, f'{w}: no page errors (states) {errs}')
        b.close()
print(f'{n - len(fails)} of {n} checks passed'); sys.exit(1 if fails else 0)
