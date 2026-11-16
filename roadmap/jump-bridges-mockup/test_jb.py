"""Checks for jump_bridges_mockup.html (build queue 041), at 1440 and 390 px, a fresh page per case.
python3 -I test_jb.py jump_bridges_mockup.html shots/"""
import os, sys
from playwright.sync_api import sync_playwright
OUT, SHOTS = sys.argv[1], sys.argv[2]
os.makedirs(SHOTS, exist_ok=True)
URL = 'file://' + os.path.abspath(OUT)
res = []
def ok(name, cond, extra=''):
    res.append((name, bool(cond))); print(('PASS ' if cond else 'FAIL ') + name + (f'  [{extra}]' if extra and not cond else ''))
JS_IDX = "(n) => itGraphGet().at.get(it.names.byLower.get(n.toLowerCase()))"
def fresh(p, w, h):
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': w, 'height': h}, bypass_csp=True, device_scale_factor=1)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_function('window.__JBREADY || window.__JBERR || window.__MKERR', timeout=60000)
    pg.evaluate(f'() => {{ window.IX = {JS_IDX}; }}')
    return b, pg, errs
def green(pg):   # pixels in the bridge green on the map's canvas
    return pg.evaluate('''() => { const c = itm.cv, d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; let n = 0;
      for(let i = 0; i < d.length; i += 4) if(d[i] < 60 && d[i + 1] > 150 && d[i + 2] < 60) n++; return n; }''')
def tip(pg, name):
    return pg.evaluate(f'''() => {{ const i = IX({name!r}); itm.pinned.clear(); itMapTip(i, 200, 200); return itm.tip.innerText; }}''')
with sync_playwright() as p:
    for (W, H, tag) in [(1440, 900, 'wide'), (390, 844, 'phone')]:
        # 1. boot, list rows, counts
        b, pg, errs = fresh(p, W, H)
        ok(f'{tag}: boot without errors', not pg.evaluate('window.__JBERR || window.__MKERR') and not errs, str(errs[:2]))
        rows = pg.evaluate('() => JB.itBridges().rows.map(r => r.st)')
        ok(f'{tag}: rows ok ok ok dup ok warn bad bad', rows == ['ok', 'ok', 'ok', 'dup', 'ok', 'warn', 'bad', 'bad'], str(rows))
        ok(f'{tag}: 5 bridges counted (the repeat once)', pg.evaluate('() => JB.itBridges().edges.length') == 5)
        ok(f'{tag}: D7 pair around the separator (SHBF-V ⇄ WF4C-8, the third name ignored)', pg.evaluate("() => { const r = JB.itBridges().rows[4]; return itSysName(r.a) === 'SHBF-V' && itSysName(r.b) === 'WF4C-8'; }"))
        ok(f'{tag}: D8 SMT line with a structure id reads as its bridge', pg.evaluate("() => { const r = JB.itBridges().rows[2]; return itSysName(r.a) === '3AE-CP' && itSysName(r.b) === 'EUU-4N'; }"))
        ok(f'{tag}: warnings name one-per-system and 5 LY', pg.evaluate("() => { const m = JB.itBridges().rows[5].msg; return /one jump gate per system/.test(m) && /5 LY/.test(m); }"))
        ok(f'{tag}: 053 hook: sovBridgeEnds has the 9 ends', pg.evaluate('() => sovBridgeEnds().length') == 9)
        # 2. the map counts the bridges, Near You doesn't
        d = pg.evaluate("() => ['8EF-58', 'F39H-1'].map(n => [itm.D[IX(n)], itm.Dg[IX(n)], itJumps(it.names.byLower.get('c-j6mt'), it.names.byLower.get(n.toLowerCase()))])")
        ok(f'{tag}: map D 3 / 2, stargate 10 / 11, itJumps unchanged', d == [[3, 10, 10], [2, 11, 11]], str(d))
        ok(f'{tag}: D never longer than Dg', pg.evaluate('() => { for(let i = 0; i < itm.D.length; i++) if(itm.Dg[i] >= 0 && (itm.D[i] < 0 || itm.D[i] > itm.Dg[i])) return false; return true; }'))
        nyOn = pg.evaluate("() => [...it.near.values()].filter(s => ['8EF-58', 'F39H-1'].includes(itSysName(s.sys))).map(s => itJumps(itMySys(), s.sys)).sort()")
        ok(f'{tag}: Near You has 8EF-58 and F39H-1 at 10 and 11', nyOn == [10, 11], str(nyOn))
        ok(f'{tag}: bridges drawn in green', green(pg) > 30)
        # 3. the hover
        t = tip(pg, '8EF-58')
        ok(f'{tag}: hover "1 of the 3 jumps by jump bridge · by stargate only 10 jumps"', '1 of the 3 jumps by jump bridge' in t and 'by stargate only 10 jumps' in t, t)
        ok(f'{tag}: hover route line says by stargate', 'route by stargate:' in t, t)
        ok(f'{tag}: Threat Vector\'s route not compared with the bridge count', 'shortest 3' not in t, t)
        t2 = tip(pg, 'F39H-1')
        ok(f'{tag}: kill-range line by stargate (F39H-1 11 > 10)', "past the Feed's kill range" in t2, t2)
        # 4. Paths to you: sources by stargate (alert range 4): 8EF-58's hostile (map 3, stargate 10) isn't one
        src = pg.evaluate("() => itPtSources().map(i => itSysName(itGraphGet().ids[i]))")
        ok(f'{tag}: Paths to you: 8EF-58 not a source, SHBF-V one', '8EF-58' not in src and 'SHBF-V' in src, str(src))
        # 5. the Jumps colour and Within N count bridges (the owner: "Both count bridges")
        ok(f'{tag}: Jumps legend says bridges counted', 'your jump bridges counted' in pg.evaluate("() => itMapFLegHtml()"))
        m = pg.evaluate("() => { const S = MKP.ST(); S.near.n = 3; S.seen.near = 1; itMapFilterSet('near'); const mm = MKP.match().m; return [mm[IX('8EF-58')], mm[IX('F39H-1')], mm[IX('3U-48K')]]; }")
        ok(f'{tag}: Within 3 matches 8EF-58 and F39H-1 by bridge', m[0] == 1 and m[1] == 1, str(m))
        pg.evaluate("() => itMapFilterSet('near')")
        pg.screenshot(path=os.path.join(SHOTS, f'{tag}_on.png'))
        # 6. switch off: stargates everywhere, nothing green, sov ends kept
        pg.evaluate("() => document.querySelector('[data-mkj=\"off\"]').click()")
        pg.wait_for_timeout(300)
        ok(f'{tag}: off: D equals Dg', pg.evaluate('() => itm.D.every((v, i) => v === itm.Dg[i])'))
        ok(f'{tag}: off: no green', green(pg) == 0, str(green(pg)))
        ok(f'{tag}: off: hover has no bridge line', 'jump bridge' not in tip(pg, '8EF-58'))
        ok(f'{tag}: off: sov ends still 9', pg.evaluate('() => sovBridgeEnds().length') == 9)
        ok(f'{tag}: off: Jumps legend plain', 'bridges' not in pg.evaluate("() => itMapFLegHtml()"))
        nyOff = pg.evaluate("() => [...it.near.values()].filter(s => ['8EF-58', 'F39H-1'].includes(itSysName(s.sys))).map(s => itJumps(itMySys(), s.sys)).sort()")
        ok(f'{tag}: off: Near You the same', nyOff == nyOn)
        pg.screenshot(path=os.path.join(SHOTS, f'{tag}_off.png'))
        # 7. the settings box after Routes, rows, 32 / 44 px row
        pg.evaluate("() => document.querySelector('[data-mkj=\"set\"]').click()")
        pg.wait_for_selector('.it-jb', timeout=5000); pg.wait_for_timeout(400)
        ok(f'{tag}: box right after Routes', pg.evaluate("() => { const b = document.querySelector('.it-jb'); return !!b && b.previousElementSibling && b.previousElementSibling.matches('.it-rp-box'); }"))
        hgt = pg.evaluate("() => document.querySelector('.it-jb .jb-on').getBoundingClientRect().height")
        ok(f'{tag}: checkbox row {"44" if tag == "phone" else "32"} px or taller', hgt >= (44 if tag == 'phone' else 32) - 0.5, str(hgt))
        li = pg.evaluate("() => [...document.querySelectorAll('.it-jb li')].map(l => l.className + '|' + l.textContent)")
        ok(f'{tag}: 8 rows shown; the repeat dim with no ✗', len(li) == 8 and li[3].startswith('jb-dup|') and '✗' not in li[3], str(li[3:4]))
        ok(f'{tag}: label counts 5', '(5 bridges)' in pg.evaluate("() => document.querySelector('.it-jb .jb-on').textContent"))
        pg.locator('.it-jb').scroll_into_view_if_needed(); pg.screenshot(path=os.path.join(SHOTS, f'{tag}_box.png'))
        # 8. edit the list: one line less redraws the rows and the map
        pg.evaluate("() => { const t = document.querySelector('[data-it-jb]'); t.value = t.value.split('\\n').slice(1).join('\\n'); t.dispatchEvent(new Event('input', {bubbles: true})); }")
        ok(f'{tag}: edit: 4 bridges', '(4 bridges)' in pg.evaluate("() => document.querySelector('.it-jb .jb-on').textContent"))
        pg.evaluate("() => { const c = document.querySelector('[data-it-jbon]'); c.checked = true; c.dispatchEvent(new Event('change', {bubbles: true})); }")
        ok(f'{tag}: edit: 8EF-58 6 on the map (its own bridge gone, SHBF-V ⇄ WF4C-8 still helps)', pg.evaluate("() => itm.D[IX('8EF-58')]") == 6)
        ok(f'{tag}: stored in dscanIntel', pg.evaluate("() => { const r = JSON.parse(localStorage.getItem('dscanIntel')); return typeof r.bridges === 'string' && r.bridgesOn === true; }"))
        sw = pg.evaluate('() => document.documentElement.scrollWidth <= window.innerWidth + 1')
        ok(f'{tag}: no sideways scroll', sw)
        ok(f'{tag}: no page errors', not errs, str(errs[:2]))
        b.close()
n = sum(1 for _, v in res if v)
print(f'{n} of {len(res)} checks passed')
sys.exit(0 if n == len(res) else 1)
