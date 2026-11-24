"""Checks for the light-year distance mockup (python3 -I test_ly.py ly_distance_mockup.html shots/), at 1440 and 390 px."""
import os, sys
from playwright.sync_api import sync_playwright
PAGE = 'file://' + os.path.abspath(sys.argv[1]); SHOTS = sys.argv[2]; os.makedirs(SHOTS, exist_ok=True)
fails, n = [], 0
def ok(c, what):
    global n; n += 1
    if not c: fails.append(what); print('FAIL', what)
# every system by the plan's rule, worked out here apart from the mockup's own __MKnear (your own system always matches, and the page keeps it off the list)
RULE = """(ly) => { const T = itMapTable(), G = itGraphGet(), h = itm.home, inR = [], land = [], why = {};
  for(let i = 0; i < G.ids.length; i++){ const d = itMapLy(i, h); if(d === null) continue; const r = Math.ceil(d * 100 - 1e-9) / 100; if(r > ly + 1e-9) continue;
    inR.push(i); const w = itMapSecT(i) >= 5 ? 'high-sec' : T.regions[T.reg[i]] === 'Pochven' ? 'Pochven' : G.ids[i] === 30100000 ? 'Zarzakh' : '';
    if(w) why[i] = w; else if(i !== h) land.push(i); }
  return {inR: inR.length, land: land.sort((a, b) => a - b), why}; }"""
MATCH = "(() => { const mt = itMapMatch(); return mt ? [...mt.list].sort((a, b) => a - b) : null; })()"
ONLY = "itm.el.querySelector('.it-map-only') ? itm.el.querySelector('.it-map-only').textContent : ''"
with sync_playwright() as p:
    for w, h in [(1440, 900), (390, 844)]:
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox']) if os.path.exists('/usr/bin/google-chrome') else p.chromium.launch()
        pg = b.new_page(viewport={'width': w, 'height': h}, has_touch=w < 600, is_mobile=w < 600); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(PAGE); pg.wait_for_function('window.__MKREADY || window.__MKERR', timeout=60000)
        ok(not pg.evaluate('window.__MKERR'), f'{w}: boot {pg.evaluate("window.__MKERR")}')
        ok(pg.evaluate("IT_MAP_FILTERS.find(f => f.k === 'near').name") == 'Distance', f'{w}: the filter is named Distance')
        ok(pg.evaluate("itMpShown() && itMp.k === 'near'"), f'{w}: its settings panel is open')
        ok(pg.evaluate("itMp.el.querySelector('[name=mkDist][value=ly]').checked"), f'{w}: Light years picked')
        ok(pg.evaluate("rsHtml && !!itMp.el.querySelector('[data-rs=mapLy], .rs') && itMp.el.textContent.includes('LY')"), f'{w}: the LY stepper shows')
        # 7 LY: the match is exactly the plan's rule
        r7 = pg.evaluate(f"({RULE})(7)"); m7 = pg.evaluate(MATCH)
        ok(m7 == r7['land'], f'{w}: 7 LY matches every landable system within 7.00 LY and nothing else ({len(m7 or [])} vs {len(r7["land"])})')
        ok(len(r7['land']) > 5, f'{w}: some systems in range ({len(r7["land"])})')
        ok(pg.evaluate("itMapMatched(itm.home)"), f'{w}: your own system matches')
        ok(not any(int(i) in (m7 or []) for i in r7['why']), f'{w}: no high-sec, Pochven or Zarzakh system matches')
        ok('within 7.0 LY (jump drive)' in pg.evaluate(ONLY), f'{w}: Only line says within 7.0 LY {pg.evaluate(ONLY)!r}')
        # the hover: in range, and in range but can't land
        land1 = next((i for i in r7['land'] if i != pg.evaluate('itm.home')), None)
        ok(land1 is not None and 'within jump range (7.0 LY)' in pg.evaluate(f"__MKtip({land1})"), f'{w}: hover says within jump range')
        bad = next(iter(r7['why']), None)
        if bad is None:   # nothing unlandable within 7 LY of the mock home: widen to find one
            r20 = pg.evaluate(f"({RULE})(20)"); bad = next(iter(r20['why']), None)
            pg.evaluate("itMapSt().near.ly = 200; itMpChanged()")
        ok(bad is not None and "can't land here" in pg.evaluate(f"__MKtip({bad})"), f'{w}: hover says a jump drive can\'t land in {bad}')
        pg.evaluate("itMapSt().near.ly = 70; itMpChanged()")
        ok(pg.evaluate("__MKtip(itm.home)") == '', f'{w}: no extra line on your own system')
        # the hover's LY and the filter agree: a system shown as 7.00 LY or less, by itMapLyText, is in range
        agree = pg.evaluate("(() => { const G = itGraphGet(); let bad = 0; for(let i = 0; i < G.ids.length; i++){ const d = itMapLy(i, itm.home); if(d === null) continue; const shown = Number(itMapLyText(d).replace(/,/g, '')); const inR = MKY.why(i) ? __MKtip(i).includes(\"can't land\") : __MKnear(i, itm.D); if((shown <= 7) !== inR && i !== itm.home) bad++; } return bad; })()")
        ok(agree == 0, f'{w}: the hover\'s LY and the filter agree for every system ({agree} differ)')
        pg.evaluate("itm.box.scrollIntoView({block:'start'})"); pg.wait_for_timeout(250)
        pg.screenshot(path=os.path.join(SHOTS, f'{w}_7ly.png'))
        # quick picks
        n7 = len(m7)
        pg.click('[data-mk-lyq="100"]'); pg.wait_for_timeout(150)
        ok(pg.evaluate("itMapSt().near.ly") == 100, f'{w}: quick pick 10 LY sets 10.0')
        ok(pg.evaluate("itMp.el.querySelector('[data-mk-lyq=\"100\"]').getAttribute('aria-pressed')") == 'true', f'{w}: the picked quick button is pressed')
        ok(pg.evaluate("[...itMp.el.querySelectorAll('[data-mk-lyq]')].filter(x => x.getAttribute('aria-pressed') === 'true').length") == 1, f'{w}: only one quick button pressed')
        m10 = pg.evaluate(MATCH); ok(m10 == pg.evaluate(f"({RULE})(10)")['land'] and len(m10) > n7, f'{w}: 10 LY matches more ({len(m10)} > {n7})')
        ok(pg.evaluate("itMp.el.querySelector('[data-mk-lyq=\"60\"]').title").startswith('Titans'), f'{w}: quick pick title names the ships')
        ok(pg.evaluate("[...itMp.el.querySelectorAll('[data-mk-lyq]')].map(x => x.textContent)") == ['6 LY', '7 LY', '8 LY', '10 LY'], f'{w}: quick picks 6, 7, 8, 10 LY')
        ok('10.0' in pg.evaluate("itMp.el.querySelector('.it-mp-row').textContent + [...itMp.el.querySelectorAll('.it-mp-row input')].map(x => x.value).join(' ')"), f'{w}: the stepper shows 10.0')
        pg.evaluate("itMapSt().near.ly = 69; itMpChanged()")
        ok(pg.evaluate("[...itMp.el.querySelectorAll('[data-mk-lyq]')].every(x => x.getAttribute('aria-pressed') !== 'true')"), f'{w}: 6.9 LY: no quick button pressed')
        pg.evaluate("MKY.scene('ly10'); itm.box.scrollIntoView({block:'start'})"); pg.wait_for_timeout(250)
        pg.screenshot(path=os.path.join(SHOTS, f'{w}_10ly.png'))
        # count in the panel follows
        ok(f"{len(m10)} system" in pg.evaluate("itMp.el.querySelector('.it-mp-cnt').textContent"), f'{w}: the panel count says {len(m10)}')
        # kept: the stack saves mode and ly, and reads them back; bad values fall back
        ok(pg.evaluate("(() => { const s = JSON.parse(localStorage.getItem(MAP_STACK_KEY)); return s.near.mode === 'ly' && s.near.ly === 100; })()"), f'{w}: saved')
        ok(pg.evaluate("(() => { const o = itMapStackRead(); return o.near.mode === 'ly' && o.near.ly === 100; })()"), f'{w}: read back')
        ok(pg.evaluate("(() => { const k = localStorage.getItem(MAP_STACK_KEY), s = JSON.parse(k); s.near.ly = 999; s.near.mode = 'x'; localStorage.setItem(MAP_STACK_KEY, JSON.stringify(s)); const o = itMapStackRead(); localStorage.setItem(MAP_STACK_KEY, k); return o.near.mode === 'j' && o.near.ly === 70; })()"), f'{w}: bad saved values fall back to Jumps, 7.0')
        ok(pg.evaluate("(() => { const k = localStorage.getItem(MAP_STACK_KEY), s = JSON.parse(k); delete s.near.mode; delete s.near.ly; localStorage.setItem(MAP_STACK_KEY, JSON.stringify(s)); const o = itMapStackRead(); localStorage.setItem(MAP_STACK_KEY, k); return o.near.mode === 'j' && o.near.n === s.near.n; })()"), f'{w}: a stack saved before this reads as Jumps, its N kept')
        # back to Jumps: today's filter, unchanged
        pg.click('[name=mkDist][value=j]'); pg.wait_for_timeout(150)
        ok(pg.evaluate("itMapSt().near.mode") == 'j', f'{w}: Jumps picked')
        ok(pg.evaluate("!!itMp.el.querySelector('.it-mp-row') && !itMp.el.querySelector('[data-mk-lyq]')"), f'{w}: Jumps shows the jumps stepper, no LY quick picks')
        mj = pg.evaluate(MATCH); rj = pg.evaluate("(() => { const a = []; for(let i = 0; i < itm.D.length; i++) if(i !== itm.home && itm.D[i] >= 0 && itm.D[i] <= itMapSt().near.n) a.push(i); return a; })()")
        ok(mj == rj, f'{w}: Jumps matches as today ({len(mj or [])})')
        ok(pg.evaluate("document.activeElement && document.activeElement.name === 'mkDist'"), f'{w}: focus stays on the switch after the panel redraws')
        ok('jump' in pg.evaluate(ONLY) and 'LY' not in pg.evaluate(ONLY), f'{w}: Only line back to jumps {pg.evaluate(ONLY)!r}')
        pg.evaluate("MKY.scene('jumps'); itm.box.scrollIntoView({block:'start'})"); pg.wait_for_timeout(250)
        pg.screenshot(path=os.path.join(SHOTS, f'{w}_jumps.png'))
        # the panel fits the screen; on a phone the quick picks are big enough to press
        pg.evaluate("MKY.scene('ly7')"); pg.wait_for_timeout(200)
        ok(pg.evaluate("itMp.el.querySelectorAll('[data-mk-lyq]').length") == 4, f'{w}: a scene after Jumps shows the LY panel again')
        box = pg.evaluate("(() => { const r = itMp.el.getBoundingClientRect(); return [r.left, r.right, innerWidth]; })()")
        ok(box[0] >= 0 and box[1] <= box[2] + 0.5, f'{w}: the panel fits across {box}')
        if w < 600:
            hs = pg.evaluate("[...itMp.el.querySelectorAll('[data-mk-lyq], [name=mkDist]')].map(x => { const r = (x.closest('label') || x).getBoundingClientRect(); return Math.round(r.height); })")
            ok(len(hs) == 6 and min(hs) >= 24, f'{w}: quick picks and the switch at least 24 px tall {hs}')
            pg.evaluate("itm.box.scrollIntoView({block:'start'})"); pg.wait_for_timeout(200)
            pg.screenshot(path=os.path.join(SHOTS, f'{w}_7ly_panel.png'))
        ok(pg.evaluate("document.documentElement.scrollWidth <= innerWidth"), f'{w}: no sideways scroll')
        ok(not errs, f'{w}: no page errors {errs[:2]}')
        b.close()
print(f'{n - len(fails)} of {n} passed'); sys.exit(1 if fails else 0)
