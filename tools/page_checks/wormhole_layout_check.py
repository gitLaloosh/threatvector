"""The Wormholes tab's panels behind icons (build queue 056; Project doc roadmap/wormholes-panels-plan.md, mockup Claude outputs/
wormholes_panels_mockup.html). The owner: "Top left, where panels are now", "Only working panels", "Yes, a click opens it", "As you left it",
"Sheet beside the rail", "nevermind, i see you just click on the icon again" (no close button), the ringed planet ("A"), and at the build review
"A" (no button until the map has a system).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/wormhole_layout_check.py [index.html]   -> 'FAILURES: N' (must be 0)

A made-up chain only: wormhole systems picked by position from the page's own table (INTEL_WH), made-up statics and a note; no pilots or groups.
intel_check.py's stand-ins answer ESI. At 1440, 760 and 390 px, a fresh page each:
  * an empty map: no rail button and no panel, even with tvWhPanels open;
  * shut by default: no stacked panels and no phone tab bar; one rail button at the map's left edge, under the "you're in" line (a phone: under
    the button row), the zoom buttons' size (30 px; 44 on a phone), fill and edge (rule A), aria-pressed false, the focused system in its title;
  * pressed: System opens right of the rail, inside the map, in the site panel style (rule B), with no close button; clear of the button row and
    (wide) the overview; a phone: the overview and the "you're in" line hidden while it's open; every map control still clickable; aria-pressed;
    Esc doesn't shut it; (wide) ⤢ fits the chain right of it, and opening it moved nothing;
  * remembered across a reload (tvWhPanels {v: 1, open: 'sum'}); pressed again it shuts, kept; a bad tvWhPanels reads as shut;
  * the overview back at the bottom right (a phone too, with the tab bar gone);
  * while shut, its body isn't written (LESSON #120); opened, it shows the system in focus;
  * a drag on a system, Select mode, the system menu and + Add leave it shut; a click on a system focuses it and opens System;
  * no sideways scroll; no page errors.
Mutants, each must fail: open by default; whFree ignoring the panel; not remembered; a click not opening it; the menu opening it; the phone
sheet over the rail; a phone shutting what was remembered open; the rail on an empty map.
"""
import sys, os, json, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
_src = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
_src = _src[:_src.index('with sync_playwright() as p:')]
NS = {'__file__': os.path.join(HERE, 'intel_check.py'), '__name__': 'intel_check_prefix'}
exec(compile(_src, 'intel_check.py (first part)', 'exec'), NS)   # HTML, route (stand-ins for ESI and zKillboard), check
globals().update({k: v for k, v in NS.items() if not k.startswith('__') and k not in ('check', 'fails')})
from playwright.sync_api import sync_playwright
check = NS['check']
PAGE = open(HTML, encoding='utf-8').read()

SEED = """() => {   // a made-up chain: CCP's wormhole systems by position in the table, made-up statics and a note, no pilots
  const T = whTable(), J = T.names.filter(n => /^J\\d{6}$/.test(n)), pick = [40, 310, 655, 902, 1210, 1488, 1733, 2011].map(i => whIdOf(J[i % J.length])), th = whIdOf('Thera');
  const t0 = Date.now() - 3 * 3600e3, path = [pick[0], pick[1], pick[2], pick[1], pick[3], pick[4], pick[3], pick[5], pick[1], pick[6], th, pick[6], pick[7], pick[6], pick[1]];
  path.forEach((id, i) => whSeen(id, t0 + i * 60e3, false));
  const S = whState(); S.st.sys[pick[0]].statics = 'H296 D845'; S.st.sys[pick[0]].notes = 'made-up note'; S.st.sys[pick[1]].statics = 'N062';
  whSave(); return pick; }"""
R = "(s) => { const e = document.querySelector(s); if(!e || !e.offsetParent) return null; const r = e.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; }"
BOX = "() => { const r = document.querySelector('.wh-box').getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; }"
HITS = """() => [...document.querySelectorAll('.wh-ctl button, .wh-ctl summary, .wh-rail button, canvas.wh-mini')].filter(e => e.offsetParent || e.getClientRects().length)
  .filter(e => { const r = e.getBoundingClientRect(); return r.width && r.top < innerHeight; })
  .map(e => { const r = e.getBoundingClientRect(), h = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return [e.className || e.tagName, !!h && (h === e || e.contains(h))]; })"""
PRESSED = "() => document.querySelector('.wh-rail button').getAttribute('aria-pressed')"
OPEN = "() => !!document.getElementById('whPnSum').offsetParent"
def over(a, b): return a and b and a[0] < b[2] - 1 and b[0] < a[2] - 1 and a[1] < b[3] - 1 and b[1] < a[3] - 1
def inside(a, b): return a and b and a[0] >= b[0] - 1 and a[1] >= b[1] - 1 and a[2] <= b[2] + 1 and a[3] <= b[3] + 1

def start(b, html, w, errs, seed=True, panels=None):
    phone = w < 600
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': 844 if phone else 900}, has_touch=phone, is_mobile=phone)
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    route(ctx)
    pg = ctx.new_page(); pg.goto('file://' + html); pg.wait_for_timeout(300)
    pg.evaluate("(p) => { localStorage.removeItem('tvWhChain'); localStorage.removeItem('tvWhMarks'); if(p === null) localStorage.removeItem('tvWhPanels'); else localStorage.setItem('tvWhPanels', p); }", panels)
    pick = None
    if seed:
        pg.reload(); pg.wait_for_timeout(300); pick = pg.evaluate(SEED)
    pg.reload(); pg.wait_for_timeout(300)
    go(pg)
    return ctx, pg, pick

def go(pg):
    pg.click('#tabBtnWh') if pg.evaluate("!!document.getElementById('tabBtnWh').offsetParent") else pg.evaluate("() => switchTab('wh')")
    pg.wait_for_timeout(400); pg.evaluate("() => document.querySelector('.wh-box').scrollIntoView({block: 'start'})"); pg.wait_for_timeout(150)

def sys_pt(pg, i=0):   # the screen centre of a system's box in the part of the map no panel covers (the i-th, in the page's own order)
    return pg.evaluate("""(i) => { const M = whS.M, cv = whCv(), r = cv.getBoundingClientRect(), v = whFree();
      const ps = [...M.P.entries()].map(([n, p]) => [n, r.left + (p.x + WH_NW / 2 - M.cam.x) * M.cam.s, r.top + (p.y + WH_NH / 2 - M.cam.y) * M.cam.s])
        .filter(([n, x, y]) => x > r.left + v.l + 20 && x < r.left + v.r - 20 && y > r.top + v.t + 20 && y < Math.min(r.top + v.b, innerHeight) - 20 && document.elementFromPoint(x, y) === cv);
      return ps[i] || null; }""", i)

def press(pg, p, touch):
    if touch: pg.touchscreen.tap(p[1], p[2])
    else: pg.mouse.click(p[1], p[2])
    pg.wait_for_timeout(300)

def run(b, html, w):
    out, errs = [], []; tag = f'{w}:'; phone = w < 600
    # an empty map: nothing to show, even with the panel remembered open (the owner at the build review: "A")
    ctx, pg, _ = start(b, html, w, errs, seed=False, panels=json.dumps({'v': 1, 'open': 'sum'}))
    e = pg.evaluate("() => [!!document.querySelector('.wh-rail') && !!document.querySelector('.wh-rail').offsetParent, !!document.getElementById('whPnSum').offsetParent, !document.querySelector('.wh-empty').hidden]")
    if e != [False, False, True]: out.append(f'{tag} an empty map: no rail button, no panel, the empty note: {e}')
    ctx.close()
    ctx, pg, pick = start(b, html, w, errs)
    box = pg.evaluate(BOX)
    old = pg.evaluate("() => document.querySelectorAll('.wh-panels, .wh-pn, .wh-pnh').length")
    if old: out.append(f'{tag} the stacked panels (and the phone tab bar) should be gone: {old}')
    rail = pg.evaluate(R, '.wh-rail button'); zoom = pg.evaluate(R, '.wh-ctl [data-wh-z="fit"]'); topl = pg.evaluate(R, '.wh-topl .wh-ctx')
    sz = 44 if phone else 30
    if not (rail and round(rail[2] - rail[0]) == sz and round(rail[3] - rail[1]) == sz): out.append(f'{tag} one rail button, {sz} px: {rail}')
    elif rail[0] - box[0] > 12: out.append(f'{tag} the rail at the map\'s left edge: {rail} {box}')
    if pg.evaluate("document.querySelectorAll('.wh-rail button').length") != 1: out.append(f'{tag} one button only (the owner: "Only working panels")')
    if not phone and not (rail and topl and rail[1] > topl[3]): out.append(f'{tag} the rail under the "you\'re in" line: {rail} {topl}')
    if phone and not (rail and zoom and rail[1] > zoom[3]): out.append(f'{tag} the rail under the button row: {rail} {zoom}')
    f = pg.evaluate("() => { const a = getComputedStyle(document.querySelector('.wh-rail button')), z = getComputedStyle(document.querySelector('.wh-ctl .it-map-zoom button')); return [a.backgroundColor === z.backgroundColor, a.borderTopColor === z.borderTopColor]; }")
    if f != [True, True]: out.append(f'{tag} the rail button in the zoom buttons\' fill and edge (rule A): {f}')
    t0 = pg.evaluate("() => [document.querySelector('.wh-rail button').title, whName(whFocus())]")
    if not t0[0].startswith(f'System: {t0[1]} ') or 'press to show' not in t0[0]: out.append(f'{tag} the button\'s title names the focused system: {t0}')
    if pg.evaluate(OPEN) or pg.evaluate(PRESSED) != 'false': out.append(f'{tag} shut by default')
    if pg.evaluate("() => document.querySelector('[data-pnb=\"sum\"]').innerHTML") != '': out.append(f'{tag} shut: System\'s body isn\'t written (LESSON #120)')
    cam0 = pg.evaluate("[whS.M.cam.x, whS.M.cam.y, whS.M.cam.s]")
    pg.click('.wh-rail button'); pg.wait_for_timeout(250)
    pn = pg.evaluate(R, '#whPnSum'); rail = pg.evaluate(R, '.wh-rail button'); ctl = pg.evaluate(R, '.wh-ctl'); mini = pg.evaluate(R, 'canvas.wh-mini')
    if not pn or pg.evaluate(PRESSED) != 'true': out.append(f'{tag} pressed: System opens, aria-pressed: {pn}')
    else:
        if pn[0] < rail[2] + 2: out.append(f'{tag} the panel right of the rail: {pn} {rail}')
        if not inside(pn, [box[0], box[1], box[2], max(box[3], box[1] + 400)]): out.append(f'{tag} the panel inside the map: {pn} {box}')
        if over(pn, ctl): out.append(f'{tag} the panel clear of the button row')
        if not phone and over(pn, mini): out.append(f'{tag} the panel clear of the overview')
        if phone and (mini is not None or pg.evaluate(R, '.wh-topl .wh-ctx') is not None): out.append(f'{tag} the overview and the "you\'re in" line hidden while the sheet is open')
        rb = pg.evaluate("() => { const s = getComputedStyle(document.getElementById('whPnSum')); return [s.borderTopLeftRadius, s.boxShadow.includes('24px'), s.backgroundColor, s.borderTopColor]; }")
        pv = pg.evaluate("() => { const d = document.createElement('div'); d.style.cssText = 'background:var(--panel); border-top:1px solid var(--line)'; document.body.appendChild(d); const s = getComputedStyle(d), o = [s.backgroundColor, s.borderTopColor]; d.remove(); return o; }")
        if not (rb[0] == '6px' and rb[1] and rb[2] == pv[0] and rb[3] == pv[1]): out.append(f'{tag} the site panel style (rule B): {rb} vs {pv}')
        hd = pg.evaluate("() => { const p = document.getElementById('whPnSum'), h = p.querySelector('h3'); return [h && h.textContent, getComputedStyle(h).fontSize, !!p.querySelector('.x-close'), p.getAttribute('role'), !!p.querySelector('[data-pnb=\"sum\"] .wh-shn')]; }")
        if hd != ['System', '14px', False, None, True]: out.append(f'{tag} heading "System" 14 px, no close button, not a dialog, the system shown: {hd}')
        hits = pg.evaluate(HITS); bad = [h for h in hits if not h[1]]
        if len(hits) < (6 if phone else 9) or bad: out.append(f'{tag} every map control still clickable with the panel open: {bad or len(hits)}')
        if pg.evaluate("[whS.M.cam.x, whS.M.cam.y, whS.M.cam.s]") != cam0: out.append(f'{tag} opening the panel moved the view')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(100)
        if not pg.evaluate(OPEN): out.append(f'{tag} Esc shut the panel (a view, not a dialog: only its button shuts it)')
        if not phone:
            pg.click('.wh-ctl [data-wh-z="fit"]'); pg.wait_for_timeout(200)
            ok = pg.evaluate("""() => { const M = whS.M, q = document.getElementById('whPnSum').getBoundingClientRect(), r = whCv().getBoundingClientRect();
              return [...M.P.values()].every(p => r.left + (p.x - M.cam.x) * M.cam.s >= q.right - 1); }""")
            if not ok: out.append(f'{tag} ⤢ with the panel open fits the chain right of it')
    pg.reload(); pg.wait_for_timeout(300); go(pg)
    if not pg.evaluate(OPEN) or json.loads(pg.evaluate("localStorage.getItem('tvWhPanels')") or 'null') != {'v': 1, 'open': 'sum'}: out.append(f'{tag} remembered across a reload (tvWhPanels)')
    pg.click('.wh-rail button'); pg.wait_for_timeout(200)
    if pg.evaluate(OPEN) or json.loads(pg.evaluate("localStorage.getItem('tvWhPanels')") or 'null') != {'v': 1, 'open': ''}: out.append(f'{tag} pressed again it shuts, and that is kept')
    mini = pg.evaluate(R, 'canvas.wh-mini'); box = pg.evaluate(BOX)
    if not (mini and mini[2] > box[2] - 30 and mini[3] > min(box[3], pg.evaluate("innerHeight")) - 40): out.append(f'{tag} the overview at the bottom right: {mini} {box}')
    # shut: the body isn't rewritten when the focus moves; opened, it shows the system in focus
    b0 = pg.evaluate("() => document.querySelector('[data-pnb=\"sum\"]').innerHTML")
    pg.evaluate("(id) => whSelect(id)", pick[3]); pg.wait_for_timeout(150)
    if pg.evaluate("() => document.querySelector('[data-pnb=\"sum\"]').innerHTML") != b0: out.append(f'{tag} shut: the body was written when the focus moved (LESSON #120)')
    pg.click('.wh-rail button'); pg.wait_for_timeout(200)
    nm = pg.evaluate("(id) => [document.querySelector('[data-pnb=\"sum\"] .wh-shn') && document.querySelector('[data-pnb=\"sum\"] .wh-shn').textContent, whName(id)]", pick[3])
    if not nm[0] or nm[1] not in nm[0]: out.append(f'{tag} opened, System shows the system in focus: {nm}')
    pg.click('.wh-rail button'); pg.wait_for_timeout(200)
    # what leaves it shut: a drag, Select mode, the system menu, + Add
    p = sys_pt(pg, 1)
    if not p: out.append(f'{tag} no system in view to drag')
    else:
        pg.mouse.move(p[1], p[2]); pg.mouse.down(); pg.mouse.move(p[1] + 40, p[2] + 30, steps=6); pg.mouse.up(); pg.wait_for_timeout(250)
        if pg.evaluate(OPEN): out.append(f'{tag} dragging a system opened System')
    if not phone:
        pg.click('.wh-ctl [data-wh-z="sel"]'); pg.wait_for_timeout(100); p = sys_pt(pg, 0); press(pg, p, False)
        if pg.evaluate(OPEN): out.append(f'{tag} a click in Select mode opened System')
        pg.click('.wh-ctl [data-wh-z="sel"]'); pg.wait_for_timeout(100)
        sel = pg.evaluate("whS.sel"); p = next((q for q in (sys_pt(pg, i) for i in range(8)) if q and q[0] != sel), None)   # not the one in focus: the menu focuses it
        pg.mouse.click(p[1], p[2], button='right'); pg.wait_for_timeout(150)
        if pg.evaluate("document.querySelector('.wh-smenu').hidden") or pg.evaluate(OPEN): out.append(f'{tag} the system menu opens and leaves System shut')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(100)
    else:
        pg.evaluate("(a) => { const id = a.find(x => x !== whS.sel); whMenuOpen(id, 40, 120); }", pick); pg.wait_for_timeout(150)   # not the one in focus
        if pg.evaluate(OPEN): out.append(f'{tag} the system menu opened System')
        pg.evaluate("() => whMenuClose(false)")
    pg.click('[data-wh-pop="add"]'); pg.wait_for_timeout(100)
    pg.fill('.wh-addf input[name=sys]', pg.evaluate("() => whTable().names.filter(n => /^J\\d{6}$/.test(n))[99]")); pg.click('.wh-addf button[type=submit]'); pg.wait_for_timeout(150); pg.evaluate("() => whPopClose()")
    if pg.evaluate(OPEN): out.append(f'{tag} + Add opened System')
    p = sys_pt(pg, 0)
    if not p: out.append(f'{tag} no system in view to click')
    else:
        press(pg, p, phone)
        st = pg.evaluate("() => [whS.sel, !!document.getElementById('whPnSum').offsetParent, document.querySelector('.wh-rail button').getAttribute('aria-pressed')]")
        if st != [p[0], True, 'true']: out.append(f'{tag} a click on a system focuses it and opens System (the owner: "Yes, a click opens it"): {st}, want {p[0]}')
    pg.evaluate("() => { localStorage.setItem('tvWhPanels', '{bad'); }"); pg.reload(); pg.wait_for_timeout(300); go(pg)
    if pg.evaluate(OPEN): out.append(f'{tag} a bad tvWhPanels reads as shut')
    pg.evaluate("() => { localStorage.setItem('tvWhPanels', JSON.stringify({v: 2, open: 'sum'})); }"); pg.reload(); pg.wait_for_timeout(300); go(pg)
    if pg.evaluate(OPEN): out.append(f'{tag} a tvWhPanels of another version reads as shut')
    if not pg.evaluate("document.documentElement.scrollWidth <= innerWidth"): out.append(f'{tag} sideways scroll')
    ctx.close()
    return out, errs

def cases(b, html, widths=(1440, 760, 390)):
    out, errs = [], []
    for w in widths:
        o, e = run(b, html, w); out += o; errs += e
    return out, errs

MUTANTS = [
    ('open by default', "return o && o.v === 1 && o.open === 'sum' ? 'sum' : ''; }catch(e){ return ''; } }", "return o && o.v === 1 && o.open === '' ? '' : 'sum'; }catch(e){ return 'sum'; } }", (1440,)),
    ('whFree ignoring the panel', "if(q.width && v.w - l >= 96) r.l = l; }", "if(false) r.l = l; }", (1440,)),
    ('not remembered', "S.open = open; try{ localStorage.setItem(WH_PN_KEY, JSON.stringify({v: 1, open})); }catch(e){ }", "S.open = open;", (1440,)),
    ('a click not opening it', "else{ if(!M.selMode && whS.open !== 'sum') whPnSet('sum', true); whSelect(d.hit); }", "else{ whSelect(d.hit); }", (1440,)),
    ('the menu opening it', "  if(S.sel !== n) whSelect(n);\n  const m = S.el.querySelector('.wh-smenu');", "  if(S.sel !== n){ whPnSet('sum', true); whSelect(n); }\n  const m = S.el.querySelector('.wh-smenu');", (1440, 390)),
    ('the phone sheet over the rail', ".wh-pnl{top:60px; left:60px; right:8px;", ".wh-pnl{top:60px; left:0px; right:8px;", (390,)),
    ('a phone shutting what was remembered open', "  S.drawKey = key; M.phone = phone;", "  S.drawKey = key; M.phone = phone; if(phone && !M.pi){ M.pi = 1; whS.open = ''; }", (390,)),
    ('the rail on an empty map', "  if(rail.hidden === has) rail.hidden = !has;", "  if(rail.hidden) rail.hidden = false;", (1440,)),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, 'the Wormholes panels: the rail, the System panel, remembered, what opens it, 1440 / 760 / 390 px')
    check(not errs, f'no page errors {errs[:3]}')
    for name, old, new, widths in MUTANTS:
        if PAGE.count(old) != 1: check(False, f'mutant "{name}": its line isn\'t in the page once'); continue
        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f:
            f.write(PAGE.replace(old, new)); mp = f.name
        try:
            try: mo, me = cases(b, mp, widths)
            except Exception as e: mo, me = [f'the check stopped: {str(e).splitlines()[0]}'], []
            check(bool(mo) or bool(me), f'mutant "{name}" fails ({(mo or me or ["nothing"])[0][:90]})')
        finally: os.unlink(mp)
    b.close()
print('FAILURES:', NS['fails'])
sys.exit(1 if NS['fails'] else 0)
