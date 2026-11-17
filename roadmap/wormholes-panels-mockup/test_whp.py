"""Checks the Wormholes panels mockup: python3 -I test_whp.py <wormholes_panels_mockup.html>  -> 'FAILURES: 0'

Playwright, bypass_csp, no network (only file: loads). At 1440, 760 and 390 px, a fresh page each:
  * Proposed by default, the panel shut: the old stacked panels and the phone tab bar gone; one rail button at the map's top left, under the
    "you're in" line, the zoom buttons' size (30 px; 44 on a phone) and fill (rule A); no panel;
  * pressed: the panel to the rail's right, inside the map, in the site panel style (rule B), clear of the top row, the rail and the
    overview; every map control's centre still hits that control; aria-pressed; remembered across a reload (tvWhPanels); a bad value = shut;
  * pressed again it shuts; a click on a system opens System (Q3), a drag doesn't; ⤢ with it open fits the chain right of it (wide);
  * a phone: the sheet right of the rail, the overview and the line hidden while it's open, the overview at the bottom right when shut;
  * Today puts the page back (the stacked panels show, no rail);
  * no sideways scroll; no page errors.
"""
import sys, os, json
from playwright.sync_api import sync_playwright
HTML = os.path.abspath(sys.argv[1])
fails = []
def check(ok, what):
    print(('ok   ' if ok else 'FAIL ') + what)
    if not ok: fails.append(what)

R = "(s) => { const e = document.querySelector(s); if(!e || !e.offsetParent) return null; const r = e.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; }"
BOX = "() => { const r = document.querySelector('.wh-box').getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; }"
HITS = """() => [...document.querySelectorAll('.wh-ctl button, .wh-ctl summary, .wh-rail button, canvas.wh-mini')].filter(e => e.offsetParent || e.getClientRects().length)
  .filter(e => { const r = e.getBoundingClientRect(); return r.width && r.top < innerHeight; })
  .map(e => { const r = e.getBoundingClientRect(), h = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return [e.className || e.tagName, !!h && (h === e || e.contains(h))]; })"""
def over(a, b): return a and b and a[0] < b[2] - 1 and b[0] < a[2] - 1 and a[1] < b[3] - 1 and b[1] < a[3] - 1
def inside(a, b): return a and b and a[0] >= b[0] - 1 and a[1] >= b[1] - 1 and a[2] <= b[2] + 1 and a[3] <= b[3] + 1

def start(b, w, h, touch, errs):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch)
    ctx.route('**/*', lambda r: r.continue_() if r.request.url.startswith('file:') else r.abort())
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + HTML); pg.wait_for_timeout(900)
    pg.evaluate("() => { const b = document.getElementById('whpBar'); if(b) b.style.display = 'none'; }")   # the MOCKUP bar isn't part of the design
    pg.evaluate("() => document.querySelector('.wh-box').scrollIntoView({block: 'start'})"); pg.wait_for_timeout(150)
    return ctx, pg

def sys_pt(pg, i=0):   # the screen centre of a system's box (the i-th, in the page's own order)
    return pg.evaluate("""(i) => { const M = whS.M, cv = document.querySelector('.wh-box > canvas'), r = cv.getBoundingClientRect(), v = whFree();
      const ps = [...M.P.entries()].map(([n, p]) => [n, r.left + (p.x + WH_NW / 2 - M.cam.x) * M.cam.s, r.top + (p.y + WH_NH / 2 - M.cam.y) * M.cam.s])
        .filter(([n, x, y]) => x > r.left + v.l + 20 && x < r.left + v.r - 20 && y > r.top + v.t + 20 && y < Math.min(r.top + v.b, innerHeight) - 20);
      return ps[i] || null; }""", i)

def run(b, w, h, touch):
    errs = []; tag = f'{w}:'
    ctx, pg = start(b, w, h, touch, errs)
    phone = w < 600
    box = pg.evaluate(BOX)
    check(pg.evaluate("() => !document.querySelector('.wh-panels').offsetParent"), f'{tag} the stacked panels (and the phone tab bar) are gone')
    rail = pg.evaluate(R, '.wh-rail button'); zoom = pg.evaluate(R, '.wh-ctl [data-wh-z="fit"]'); topl = pg.evaluate(R, '.wh-topl .wh-ctx')
    sz = 44 if phone else 30
    check(rail and round(rail[2] - rail[0]) == sz and round(rail[3] - rail[1]) == sz, f'{tag} one rail button, {sz} px: {rail}')
    check(rail and rail[0] - box[0] < 12, f'{tag} the rail at the map\'s left edge')
    if not phone: check(rail and topl and rail[1] > topl[3], f'{tag} the rail under the "you\'re in" line')
    else: check(rail and zoom and rail[1] > zoom[3], f'{tag} the rail under the top row')
    f = pg.evaluate("() => { const a = getComputedStyle(document.querySelector('.wh-rail button')), z = getComputedStyle(document.querySelector('.wh-ctl .it-map-zoom button')); return [a.backgroundColor === z.backgroundColor, a.borderTopColor === z.borderTopColor]; }")
    check(f == [True, True], f'{tag} the rail button in the zoom buttons\' fill and edge (rule A): {f}')
    check(pg.evaluate(R, '#whPnSum') is None and pg.evaluate("document.querySelector('.wh-rail button').getAttribute('aria-pressed')") == 'false', f'{tag} shut by default')
    pg.click('.wh-rail button'); pg.wait_for_timeout(250)
    pn = pg.evaluate(R, '#whPnSum'); rail = pg.evaluate(R, '.wh-rail button'); ctl = pg.evaluate(R, '.wh-ctl'); mini = pg.evaluate(R, 'canvas.wh-mini')
    check(pn is not None and pg.evaluate("document.querySelector('.wh-rail button').getAttribute('aria-pressed')") == 'true', f'{tag} pressed: System opens, aria-pressed')
    check(pn and rail and pn[0] >= rail[2] + 2, f'{tag} the panel right of the rail: {pn} {rail}')
    check(inside(pn, [box[0], box[1], box[2], max(box[3], box[1] + 400)]), f'{tag} the panel inside the map')
    check(not over(pn, ctl), f'{tag} the panel clear of the top row')
    if not phone: check(not over(pn, mini), f'{tag} the panel clear of the overview')
    else: check(mini is None and pg.evaluate(R, '.wh-topl .wh-ctx') is None, f'{tag} the overview and the line hidden while the sheet is open')
    rb = pg.evaluate("() => { const s = getComputedStyle(document.getElementById('whPnSum')), v = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim(); return [s.borderTopLeftRadius, s.boxShadow.includes('24px'), s.backgroundColor, s.borderTopColor]; }")
    pv = pg.evaluate("() => { const d = document.createElement('div'); d.style.cssText = 'background:var(--panel); border-top:1px solid var(--line)'; document.body.appendChild(d); const s = getComputedStyle(d), o = [s.backgroundColor, s.borderTopColor]; d.remove(); return o; }")
    check(rb[0] == '6px' and rb[1] and rb[2] == pv[0] and rb[3] == pv[1], f'{tag} the site panel style (rule B): {rb} vs {pv}')
    hits = pg.evaluate(HITS); bad = [h for h in hits if not h[1]]
    check(len(hits) >= (6 if phone else 9) and not bad, f'{tag} every map control still clickable with the panel open: {bad or len(hits)}')
    if not phone:
        pg.click('.wh-ctl [data-wh-z="fit"]'); pg.wait_for_timeout(200)
        ok = pg.evaluate("""() => { const M = whS.M, q = document.getElementById('whPnSum').getBoundingClientRect(), r = document.querySelector('.wh-box > canvas').getBoundingClientRect();
          return [...M.P.values()].every(p => r.left + (p.x - M.cam.x) * M.cam.s >= q.right - 1); }""")
        check(ok, f'{tag} ⤢ with the panel open fits the chain right of it')
    pg.reload(); pg.wait_for_timeout(900); pg.evaluate("() => { document.getElementById('whpBar').style.display = 'none'; document.querySelector('.wh-box').scrollIntoView({block: 'start'}); }"); pg.wait_for_timeout(150)
    check(pg.evaluate(R, '#whPnSum') is not None and json.loads(pg.evaluate("localStorage.getItem('tvWhPanels')")) == {'v': 1, 'open': 'sum'}, f'{tag} remembered across a reload (tvWhPanels)')
    pg.click('.wh-rail button'); pg.wait_for_timeout(200)
    check(pg.evaluate(R, '#whPnSum') is None and json.loads(pg.evaluate("localStorage.getItem('tvWhPanels')")) == {'v': 1, 'open': ''}, f'{tag} pressed again it shuts, and that is kept')
    if not phone:
        mini = pg.evaluate(R, 'canvas.wh-mini'); box = pg.evaluate(BOX)
        check(mini and mini[2] > box[2] - 30 and mini[3] > box[3] - 30, f'{tag} the overview at the bottom right')
    else:
        mini = pg.evaluate(R, 'canvas.wh-mini'); box = pg.evaluate(BOX)
        check(mini and mini[2] > box[2] - 30 and mini[1] > box[1] + 200, f'{tag} the overview back at the bottom right with the sheet shut: {mini} {box}')
    p = sys_pt(pg, 1)
    if p:
        pg.mouse.move(p[1], p[2]); pg.mouse.down(); pg.mouse.move(p[1] + 40, p[2] + 30, steps=6); pg.mouse.up(); pg.wait_for_timeout(250)
        check(pg.evaluate(R, '#whPnSum') is None, f'{tag} dragging a system leaves System shut')
        p = sys_pt(pg, 0)
        if touch: pg.touchscreen.tap(p[1], p[2])
        else: pg.mouse.click(p[1], p[2])
        pg.wait_for_timeout(300)
        st = pg.evaluate("() => [whS.sel, !!document.getElementById('whPnSum').offsetParent]")
        check(st == [p[0], True], f'{tag} a click on a system focuses it and opens System (Q3): {st} want {p[0]}')
    else: check(False, f'{tag} no system in view to click')
    pg.evaluate("() => { localStorage.setItem('tvWhPanels', '{bad'); }"); pg.reload(); pg.wait_for_timeout(900)
    check(pg.evaluate(R, '#whPnSum') is None, f'{tag} a bad tvWhPanels reads as shut')
    pg.evaluate("() => { const b = document.getElementById('whpBar'); b.style.display = ''; b.querySelector('[data-whp-m=\\\"today\\\"]').click(); }"); pg.wait_for_timeout(250)
    check(pg.evaluate("() => !!document.querySelector('.wh-panels').offsetParent && !document.querySelector('.wh-rail').offsetParent"), f'{tag} Today puts the page back')
    check(pg.evaluate("document.documentElement.scrollWidth <= innerWidth"), f'{tag} no sideways scroll')
    check(not errs, f'{tag} no page errors {errs[:2]}')
    ctx.close()

with sync_playwright() as p:
    b = p.chromium.launch()
    run(b, 1440, 900, False); run(b, 760, 900, False); run(b, 390, 844, True)
    b.close()
print('FAILURES:', len(fails))
sys.exit(1 if fails else 0)
