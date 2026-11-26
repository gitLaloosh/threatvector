"""Checks for the Activity (past hour) mockup (python3 -I test_ac.py activity_mockup.html shots/), at 1440 and 390 px."""
import os, sys
from playwright.sync_api import sync_playwright
PAGE = 'file://' + os.path.abspath(sys.argv[1]); SHOTS = sys.argv[2]; os.makedirs(SHOTS, exist_ok=True)
fails, n = [], 0
def ok(c, what):
    global n; n += 1
    if not c: fails.append(what); print('FAIL', what)
# the plan's rule, worked out apart: the picked kind's count (missing = 0) at least that kind's minimum; your system off the list
RULE = """(() => { const s = itMapSt().act, M = s.k === 'j' ? MKA.j : s.k === 'sp' ? MKA.sp : MKA.npc, out = [];
  for(let i = 0; i < itGraphGet().ids.length; i++) if(i !== itm.home && (M.get(i) || 0) >= s[s.k]) out.push(i);
  return out; })()"""
MATCH = "(() => { const mt = itMapMatch(); return mt ? [...mt.list].sort((a, b) => a - b) : null; })()"
ONLY = "(itm.el.querySelector('.it-map-only') || {}).textContent || ''"
STEPS = [1, 2, 3, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200, 300, 500, 750, 1000, 1500, 2000]
with sync_playwright() as p:
    for w, h in [(1440, 900), (390, 844)]:
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = b.new_page(viewport={'width': w, 'height': h}, has_touch=w < 600, is_mobile=w < 600); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(PAGE); pg.wait_for_function('window.__MKREADY || window.__MKERR', timeout=60000)
        ok(not pg.evaluate('window.__MKERR'), f'{w}: boot {pg.evaluate("window.__MKERR")}')
        # the filter
        ok(pg.evaluate("IT_MAP_FILTERS.find(f => f.k === 'act').name") == 'Activity (past hour)' and pg.evaluate("IT_MAP_ONLY[IT_MAP_ONLY.length - 1]") == 'act', f'{w}: an Only filter "Activity (past hour)", last in the Only group')
        ok(pg.evaluate("IT_MAP_ONLY.length") == 9, f'{w}: nine Only filters with the two stand-ins')
        ok(pg.evaluate("JSON.stringify(itMapStackBlank().act)") == '{"k":"j","j":50,"sp":1,"npc":200}', f'{w}: defaults Jumps, minimums 50 / 1 / 200')
        ok(pg.evaluate("itMpShown() && itMp.k === 'act'"), f'{w}: its settings panel is open')
        ok(pg.evaluate("[...itMp.el.querySelectorAll('[name=mkAct]')].map(x => x.value + ':' + x.checked).join()") == 'j:true,sp:false,npc:false', f'{w}: three kinds, Jumps picked')
        ok(pg.evaluate("RS.mapAct.steps()") == STEPS, f'{w}: round-number steps 1 to 2000')
        # the match
        m = pg.evaluate(MATCH); r = pg.evaluate(RULE)
        ok(m == r and len(m) > 100, f'{w}: Jumps ≥ 50 matches the rule worked out apart ({len(m or [])})')
        ok(pg.evaluate("itMapMatched(itm.home)"), f'{w}: your system matches')
        ok(pg.evaluate("[...itMapMatch().list].every(i => itGraphGet().ids[i] < 31000000)"), f'{w}: no J-space system matches')
        ok(f'at least 50 jumps in the past hour ({len(m):,})' in pg.evaluate(ONLY) and 'ESI ' in pg.evaluate(ONLY), f'{w}: Only line {pg.evaluate(ONLY)!r}')
        i78 = pg.evaluate("itGraphGet().ids.findIndex(x => itSysName(x) === '78-0R6')")
        ok('140 jumps in the past hour (ESI, as of' in pg.evaluate(f"__MKtip({i78})"), f'{w}: hover gives the picked kind\'s count')
        ok(pg.evaluate("[...MKA.j.keys(), ...MKA.sp.keys(), ...MKA.npc.keys()].every(i => itGraphGet().ids[i] < 31000000)"), f'{w}: no made-up counts in J-space (as ESI)')
        pg.evaluate("itm.box.scrollIntoView({block:'start'})"); pg.wait_for_timeout(250)
        pg.screenshot(path=os.path.join(SHOTS, f'{w}_jumps.png'))
        # the stepper and per-kind minimums
        pg.evaluate("itMp.el.querySelector('[data-rs=\"mapAct\"]').scrollIntoView({block:'center'})")
        pg.click('[data-rs="mapAct"] [data-rs-d="1"]'); pg.wait_for_timeout(100)
        ok(pg.evaluate("itMapSt().act.j") == 75, f'{w}: + steps 50 → 75')
        ok(pg.evaluate(MATCH) == pg.evaluate(RULE), f'{w}: 75 matches the rule')
        pg.click('[name=mkAct][value=npc]'); pg.wait_for_timeout(150)
        ok(pg.evaluate("itMapSt().act.k") == 'npc' and pg.evaluate("itMp.el.querySelector('[data-rs=\"mapAct\"] .rs-v').value") == '200', f'{w}: NPC kills brings back its own 200')
        ok(pg.evaluate(MATCH) == pg.evaluate(RULE) and 'at least 200 NPC kills' in pg.evaluate(ONLY), f'{w}: NPC kills ≥ 200 matches the rule')
        ok(pg.evaluate("document.activeElement && document.activeElement.name === 'mkAct'"), f'{w}: focus stays on the kind after the panel redraws')
        pg.click('[name=mkAct][value=j]'); pg.wait_for_timeout(150)
        ok(pg.evaluate("itMp.el.querySelector('[data-rs=\"mapAct\"] .rs-v').value") == '75', f'{w}: back to Jumps: its own 75 kept')
        pg.click('[name=mkAct][value=sp]'); pg.wait_for_timeout(150)
        ok(pg.evaluate(MATCH) == pg.evaluate(RULE) and 'at least 1 ship + pod kills' in pg.evaluate(ONLY), f'{w}: Ship + pod ≥ 1 matches the rule')
        ok(len(pg.evaluate(MATCH)) < len(m), f'{w}: kills are rarer than jumps')
        pg.evaluate("itMapSt().act.sp = 2000; itMpChanged()")
        ok(pg.evaluate(MATCH) == [], f'{w}: 2000 ship + pod kills: nothing')
        pg.evaluate("MKA.scene('busy')")
        ok(len(pg.evaluate(MATCH)) < len(m) and pg.evaluate(MATCH) == pg.evaluate(RULE), f'{w}: Jumps ≥ 500 matches fewer, by the rule')
        # no data, and data back
        pg.evaluate("MKA.scene('nodata')")
        ok(pg.evaluate(MATCH) == [] and 'no data yet' in pg.evaluate(ONLY) and pg.evaluate(f"__MKtip({i78})") == '', f'{w}: no data yet: nothing matches, no hover line')
        pg.evaluate("MKA.scene('jumps')")
        ok(pg.evaluate(MATCH) == pg.evaluate(RULE) and len(pg.evaluate(MATCH)) > 100, f'{w}: data back: worked out again')
        # kept
        pg.evaluate("itMapSt().act.npc = 300; itMapSt().act.k = 'npc'; itMapStackSave()")
        ok(pg.evaluate("(() => { const o = itMapStackRead(); return o.act.k === 'npc' && o.act.npc === 300 && o.act.j === 50; })()"), f'{w}: saved and read back, per kind')
        ok(pg.evaluate("(() => { const k = localStorage.getItem(MAP_STACK_KEY), s = JSON.parse(k); s.act = {k: 'x', j: 51, sp: -1, npc: 300}; localStorage.setItem(MAP_STACK_KEY, JSON.stringify(s)); const o = itMapStackRead(); localStorage.setItem(MAP_STACK_KEY, k); return o.act.k === 'j' && o.act.j === 50 && o.act.sp === 1 && o.act.npc === 300; })()"), f'{w}: a bad kind or an off-step number falls back, the rest kept')
        ok(pg.evaluate("(() => { const k = localStorage.getItem(MAP_STACK_KEY), s = JSON.parse(k); delete s.act; delete s.only.act; localStorage.setItem(MAP_STACK_KEY, JSON.stringify(s)); const o = itMapStackRead(); localStorage.setItem(MAP_STACK_KEY, k); return o.only.act === false && o.act.j === 50; })()"), f'{w}: a stack saved before this reads with it off, the defaults')
        # first switch-on opens the settings
        pg.evaluate("MKA.scene('off'); itMapSt().seen.act = false; itMapFilterSet('act')")
        ok(pg.evaluate("itMapSt().only.act && itMpShown() && itMp.k === 'act'"), f'{w}: switched on the first time, its settings open')
        pg.evaluate("itMapFilterSet('act')")
        ok(pg.evaluate("!itMapSt().only.act && !itMpShown()"), f'{w}: switched off, its settings close')
        # the column with nine Only filters: every button inside the map box, none overlapping
        pg.evaluate("MKA.scene('jumps'); itMpOpen('', false); itm.box.scrollIntoView({block:'start'})"); pg.wait_for_timeout(250)
        if w < 600: pg.click('.it-map-fcur'); pg.wait_for_timeout(250)   # the phone's column opens from its button
        col = pg.evaluate("""(() => { const box = itm.box.getBoundingClientRect(), bs = [...itm.el.querySelectorAll('.it-map-fbtns button')].filter(x => x.offsetParent).map(x => x.getBoundingClientRect());
          let over = 0; for(let a = 0; a < bs.length; a++) for(let c = a + 1; c < bs.length; c++){ const p = bs[a], q = bs[c]; if(p.left < q.right - 1 && q.left < p.right - 1 && p.top < q.bottom - 1 && q.top < p.bottom - 1) over++; }
          return {n: bs.length, inside: bs.every(r => r.top >= box.top - 0.5 && r.bottom <= box.bottom + 0.5 && r.left >= box.left - 0.5), over, cols: new Set(bs.map(r => Math.round(r.left))).size, rows: getComputedStyle(itm.el.querySelector('.it-map-fbtns')).getPropertyValue('--it-flr')}; })()""")
        ok(col['inside'] and col['over'] == 0 and col['n'] >= 13, f'{w}: the filter column fits the map, nothing overlaps {col}')
        if w < 600: ok(min(pg.evaluate("[...itm.el.querySelectorAll('.it-map-fbtns button')].filter(x => x.offsetParent).map(x => x.getBoundingClientRect().height)")) >= 44, f'{w}: column buttons 44 px')
        pg.screenshot(path=os.path.join(SHOTS, f'{w}_column.png'))
        # the panel fits; no sideways scroll
        pg.evaluate("itMpOpen('act', false)"); pg.wait_for_timeout(150)
        bx = pg.evaluate("(() => { const r = itMp.el.getBoundingClientRect(); return [r.left, r.right, innerWidth]; })()")
        ok(bx[0] >= 0 and bx[1] <= bx[2] + 0.5, f'{w}: the panel fits across {bx}')
        if w < 600:
            hs = pg.evaluate("[...itMp.el.querySelectorAll('[name=mkAct]')].map(x => Math.round(x.closest('label').getBoundingClientRect().height))")
            ok(len(hs) == 3 and min(hs) >= 24, f'{w}: the kinds at least 24 px tall {hs}')
        else:
            pg.evaluate("MKA.scene('wide'); itm.box.scrollIntoView({block:'start'})"); pg.wait_for_timeout(250)
            pg.screenshot(path=os.path.join(SHOTS, f'{w}_wide.png'))
        ok(pg.evaluate("document.documentElement.scrollWidth <= innerWidth"), f'{w}: no sideways scroll')
        ok(not errs, f'{w}: no page errors {errs[:2]}')
        b.close()
print(f'{n - len(fails)} of {n} passed'); sys.exit(1 if fails else 0)
