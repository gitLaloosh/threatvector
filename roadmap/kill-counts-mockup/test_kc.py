"""Checks for the kill counts mockup (python3 -I test_kc.py kill_counts_mockup.html shots/), at 1440 and 390 px."""
import os, sys
from playwright.sync_api import sync_playwright
PAGE = 'file://' + os.path.abspath(sys.argv[1]); SHOTS = sys.argv[2]; os.makedirs(SHOTS, exist_ok=True)
fails, n = [], 0
def ok(c, what):
    global n; n += 1
    if not c: fails.append(what); print('FAIL', what)
REP = "(nm) => itm.rep.get(itGraphGet().at.get(it.names.byLower.get(nm.toLowerCase())))"
with sync_playwright() as p:
    for w, h in [(1440, 900), (390, 844)]:
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = b.new_page(viewport={'width': w, 'height': h}, has_touch=w < 600, is_mobile=w < 600); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(PAGE); pg.wait_for_function('window.__MKREADY || window.__MKERR', timeout=60000)
        ok(not pg.evaluate('window.__MKERR'), f'{w}: boot')
        kb = pg.evaluate(f"({REP})('78-0R6').kb"); ok(kb == {'f': 3, 'h': 5, 'n': 2}, f'{w}: the owner\'s example: 3 friendlies lost, 5 hostiles and 2 neutrals killed {kb}')
        ok(pg.evaluate(f"({REP})('78-0R6').kills") == 10, f'{w}: ✕ total still 10')
        pcs = pg.evaluate(f"__MKkt(({REP})('78-0R6'), {{amber: '#d99a3c'}}).map(p => [p.t, p.col])")
        ok(pcs == [['✕', '#d99a3c'], ['3', '#4f8fe0'], ['5', '#f08b7e'], ['2', '#b9c3ca']], f'{w}: label ✕ then friendly, hostile, neutral in their colours {pcs}')
        for k, f, nn in [('b', '#7dbbff', '#6b7781'), ('c', '#4f8fe0', '#d4dbe0')]:
            got = pg.evaluate(f"(() => {{ MKK.setPal('{k}'); const r = __MKkt(({REP})('78-0R6'), {{amber: '#d99a3c'}}).map(p => p.col); MKK.setPal('a'); return r; }})()")
            ok(got == ['#d99a3c', f, '#f08b7e', nn], f'{w}: pair {k} {got}')
        # contrast between friendly and neutral: lightness differs by at least 15 points (L* from sRGB), in every pair (the first try, #8db8f2 vs #b9c3ca, differed by 4)
        def L(hx):
            r, g, b2 = [int(hx[i:i + 2], 16) / 255 for i in (1, 3, 5)]
            lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
            Y = 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b2)
            return 116 * (Y ** (1 / 3) if Y > 0.008856 else 7.787 * Y + 16 / 116) - 16
        for nm, f, nn in [('a', '#4f8fe0', '#b9c3ca'), ('b', '#7dbbff', '#6b7781'), ('c', '#4f8fe0', '#d4dbe0')]:
            ok(abs(L(f) - L(nn)) >= 15 , f'{w}: pair {nm} friendly vs neutral lightness differs ({L(f):.0f} vs {L(nn):.0f})')
        one = pg.evaluate(f"__MKkt(({REP})('MSG-BZ'), {{amber: '#d99a3c'}}).map(p => p.t)"); ok(one == ['✕', '2'], f'{w}: a standing with no deaths left out {one}')
        tip = pg.evaluate(f"__MKkh(({REP})('78-0R6'))"); ok('3 friendlies lost' in tip and '5 hostiles killed' in tip and '2 neutrals killed' in tip, f'{w}: hover in words')
        ok('kills by who died' in pg.evaluate("itm.el.querySelector('.it-map-leg').textContent"), f'{w}: legend entry')
        # Near You's badges agree (same who-died counts)
        ok(pg.evaluate(f"(() => {{ const r = ({REP})('78-0R6'); return itKillBadges(r.st.kills, 0); }})()").count('it-kl') == 3, f'{w}: Near You shows the same three badges')
        for z in (12, 30, 90):
            pg.evaluate(f"MKK.zoomTo({z}); itm.box.scrollIntoView({{block:'start'}})"); pg.wait_for_timeout(250)
            ok(any(l[0] == pg.evaluate("itGraphGet().at.get(it.names.byLower.get('78-0r6'))") for l in pg.evaluate("itm.labels")), f'{w}: 78-0R6 labelled at zoom {z}')
            pg.screenshot(path=os.path.join(SHOTS, f'{w}_by_who_died_{z}.png'))
        pg.evaluate("MKK.mode = 'today'; MKK.redraw()"); pg.wait_for_timeout(200)
        ok(pg.evaluate(f"__MKkt(({REP})('78-0R6'), {{amber: '#d99a3c'}}).map(p => p.t)") == ['✕10'], f'{w}: Today shows ✕10')
        pg.screenshot(path=os.path.join(SHOTS, f'{w}_today_90.png'))
        ok(pg.evaluate("document.documentElement.scrollWidth <= innerWidth"), f'{w}: no sideways scroll')
        ok(not errs, f'{w}: no page errors {errs[:2]}')
        b.close()
print(f'{n - len(fails)} of {n} passed'); sys.exit(1 if fails else 0)
