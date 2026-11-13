"""Screens of the Wormholes-filter look: today's vs the new (1-4), the chip (5), zoomed in, and a phone; plus checks.
python3 -I snap_whs.py wormholes_standout_mockup.html shots/"""
import os, sys, time
from playwright.sync_api import sync_playwright
page_path, out = os.path.abspath(sys.argv[1]), sys.argv[2]
os.makedirs(out, exist_ok=True)
fails = []
def ok(c, what):
    print(('ok   ' if c else 'FAIL ') + what)
    if not c: fails.append(what)
with sync_playwright() as p:
    b = p.chromium.launch()
    for W, H in ((1440, 1000), (390, 844)):
        ctx = b.new_context(viewport={'width': W, 'height': H}, bypass_csp=True, device_scale_factor=1)
        pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + page_path)
        pg.wait_for_function('window.__MKREADY || window.__MKERR', timeout=30000)
        ok(not pg.evaluate('window.__MKERR'), f'{W}: boot')
        if W < 600: pg.wait_for_selector('.it-nv button', timeout=20000); pg.locator('.it-nv button', has_text='Map').first.click(); time.sleep(1)
        pg.wait_for_function('typeof itm !== "undefined" && itm.filter === "wh" && itm.wh && itm.wh.kept.size >= 5', timeout=45000)
        time.sleep(5)   # the filter's note fades first
        def shot(name):
            if W < 600: pg.locator('[data-mk="fold"]').click(); time.sleep(.2)
            box.screenshot(path=f'{out}/{W}_{name}.png')
            if W < 600: pg.locator('[data-mk="fold"]').click()
        box = pg.locator('.it-map-box'); box.scroll_into_view_if_needed(); time.sleep(.5)
        kept = pg.evaluate('[...itm.wh.kept.values()].map(w => (w.drifter ? "D" : "W") + Math.round((Date.now() - w.t) / 60000))')
        ok(len(kept) >= 6, f'{W}: wormholes kept: {kept}')
        ok(pg.evaluate('itm.whPulse.length') >= 3, f'{W}: fresh holes pulse ({pg.evaluate("itm.whPulse.length")})')
        labs = pg.evaluate('itm.labels.map(l => l[0])'); marks = pg.evaluate('[...itm.wh.mark.keys()]'); reps = pg.evaluate('[...itm.rep.keys()]')
        no_wh = [i for i in reps if i not in marks and i != pg.evaluate('itm.home')]
        ok(not any(i in labs for i in no_wh), f'{W}: reports without a wormhole get no label on the new look')
        inview = pg.evaluate('[...itm.wh.mark.keys()].filter(i => itm.D[i] >= 0 && itm.D[i] <= itm.reach && itm.Q[2*i] > 0 && itm.Q[2*i] < itm.W && itm.Q[2*i+1] > 0 && itm.Q[2*i+1] < itm.H)')
        ok(sum(i in labs for i in inview) >= len(inview) - 1, f'{W}: wormholes in view and in reach labelled: {sum(i in labs for i in inview)} of {len(inview)}')
        L = pg.evaluate('itm.labels.map(l => l.slice(1))')
        ov = [(a, b) for x, a in enumerate(L) for b in L[x + 1:] if a[0] < b[2] - 1 and a[2] > b[0] + 1 and a[1] < b[3] - 1 and a[3] > b[1] + 1]
        ok(not ov, f'{W}: no label over another ({len(ov)}: {ov[:2]})')
        shot('2_new')
        pg.locator('[data-mk="look"]').click(); time.sleep(.6)
        shot('1_today')
        ok(any(i in pg.evaluate('itm.labels.map(l => l[0])') for i in no_wh), f'{W}: today\'s look still names the other reports')
        pg.locator('[data-mk="look"]').click(); time.sleep(.4)
        pg.locator('[data-mk="chip"]').click(); time.sleep(.6)
        chip = pg.locator('.whs-chip'); ok(chip.is_visible() and 'wormholes' in chip.inner_text(), f'{W}: the chip: {chip.inner_text() if chip.is_visible() else "-"}')
        chip.click(); time.sleep(.5); t1 = chip.inner_text(); chip.click(); time.sleep(.5); t2 = chip.inner_text()
        ok(t1.startswith('1/') and t2.startswith('2/') and t1 != t2, f'{W}: the chip steps: {t1} then {t2}')
        shot('3_chip')
        pg.locator('[data-mk="sec"]').click(); time.sleep(.5)
        ok(not chip.is_visible() and pg.evaluate('itm.whPulse.length') == 0, f'{W}: other filters unchanged: no chip, no pulse')
        pg.locator('[data-mk="wh"]').click(); time.sleep(.4)
        if W >= 600:
            # zoomed in on a fresh hole (the circles stage)
            pg.evaluate('(() => { const L = [...itm.wh.kept.keys()].sort((a, b) => itm.D[a] - itm.D[b]); const i = L[0], k = 60 / itm.G; itm.view = {k, tx: itm.W / 2 - itm.P[2 * i] * k, ty: itm.H / 2 - itm.P[2 * i + 1] * k}; itMapDraw(); })()'); time.sleep(.6)
            ok(pg.evaluate('itm.stage') >= 1, f'{W}: zoomed in (stage {pg.evaluate("itm.stage")})')
            shot('4_zoomed')
        ok(pg.evaluate('document.scrollingElement.scrollWidth <= innerWidth + 1'), f'{W}: no sideways scroll')
        ok(not errs, f'{W}: no page errors {errs[:3]}')
        ctx.close()
    b.close()
print('\n%d failed' % len(fails) if fails else '\nall passed'); sys.exit(1 if fails else 0)
