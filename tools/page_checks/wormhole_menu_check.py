"""The Wormholes tab, part 2: the system menu (build queue 051; Project doc roadmap/wormhole-mapping-plan.md "Build in parts" 2, D25, D26, D34;
mockup Claude outputs/wormholes_tab_mockup.html). The owner: borders "set by the user to denote level of danger", "LOCK is all we need ... just need
the lock to prevent accidental deletions of home systems", "locked systems cannot be deleted until unlocked.", the tag on the map in "the page's"
tag look, and "the map should push the bottom of the page to the bottom of the screen even if it's empty. no re-size when it's populated that way."

Made-up Intel (intel_check.py's folder and stand-ins), CCP's wormhole system names from the page's own table (INTEL_WH). Checks:
  * the empty map is as tall as the full one (to the bottom of the screen), at 1440 and 390 px; adding the first system resizes nothing;
  * the menu: a right-click on a system opens it (a menu: no close button, focus on its first item, the arrows move, Esc closes and gives the
    focus back to the map), on empty space "Add a system here" still opens; no "Routes from here" yet;
  * status: the six and No status; the box's border in the status colour (read off the canvas), its name in the System panel (the page's tag) and
    in the box's hover; kept after a reload (tvWhMarks);
  * the tag: cut to 8, shown in the System panel and kept after a reload;
  * Lock: the message (D34's words); the locked system doesn't move when dragged, alone or in a group (the others do); Rearrange leaves it;
    Remove is greyed with "(unlock first)" in the menu and refuses there and in the System panel; a connection touching it can still be deleted;
    Unlock, then Remove takes the system, its connections and its marks;
  * Copy the name: copied when the browser allows it, else the name stays in the menu, selected;
  * stored data safe both ways: main's page (part 1, from git) saving its chain leaves tvWhMarks as it was and the marks still show here after;
    marks for a system no longer on the map are dropped;
  * a phone: press and hold on a system opens the menu (not a drag or a pan) and lifting the finger picks nothing in it (LESSON #167), 44 px
    rows, inside the map and the screen, no sideways scroll;
  * mutants; no page errors.
"""
import sys, os, re, json, time, tempfile, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
_src = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
_src = _src[:_src.index('with sync_playwright() as p:')]
NS = {'__file__': os.path.join(HERE, 'intel_check.py'), '__name__': 'intel_check_prefix'}
exec(compile(_src, 'intel_check.py (first part)', 'exec'), NS)   # the made-up folder, mocks, names
globals().update({k: v for k, v in NS.items() if not k.startswith('__') and k not in ('check', 'fails')})
from playwright.sync_api import sync_playwright
check = NS['check']
PAGE = open(HTML, encoding='utf-8').read()
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
PART1 = '9459b35'   # v2026.11.15.1, the last main with part 1 only: never origin/main, which is this page once it's merged (LESSON #168)
DANGER = (0xe5, 0x53, 0x4b)

def start(b, html, w, errs, h=1000, touch=False, chain=None):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch, device_scale_factor=2 if touch else 1)
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); route(ctx)
    pg = ctx.new_page(); pg.goto('file://' + html)
    pg.evaluate("([s, c]) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({channels: ['region.intel'], me: 95000001, range: 3, sound: false, notify: false}));"
                " localStorage.removeItem('tvWhMarks'); if(c) localStorage.setItem('tvWhChain', JSON.stringify(c)); else localStorage.removeItem('tvWhChain'); localStorage.setItem('tvWormholes', JSON.stringify({v: 1, keepH: 24, gone: {}, rep: {}})); if(!c) localStorage.setItem('tvWhPanels', JSON.stringify({v: 1, open: 'sum'})); }", [SIDE, chain])   # 056: System open, so its body is drawn (not the phone's chain: the sheet would cover the map)
    pg.reload(); pg.wait_for_timeout(400)
    return ctx, pg

def intel_on(pg):
    setup_logs(pg); pg.click('#tabBtnIntel'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg)

def jump(pg, name, t): W(pg, F_LOCAL_MAIN, line(t, 'EVE System', f'Channel changed to Local : {name}*')); tick(pg, 2800)

BOX = "() => { const b = document.querySelector('.wh-box').getBoundingClientRect(); return [Math.round(b.height), Math.round(b.bottom), innerHeight]; }"
# a system's box on the screen, brought into the part of the map no panel covers first
AT = """(id) => { const M = whS.M, cv = whCv(); if(!whInView(id)){ whCenter(id); whDraw(); }
  const at = () => { const p = M.P.get(id), c = M.cam, r = cv.getBoundingClientRect(); return {x: r.x + (p.x + 56 - c.x) * c.s, y: r.y + (p.y + 24 - c.y) * c.s, ex: r.x + (p.x - c.x) * c.s, ey: r.y + (p.y + 24 - c.y) * c.s, wx: p.x, wy: p.y}; };
  for(let k = 0; k < 6; k++){ const a = at(); if(document.elementFromPoint(a.x, a.y) === cv && document.elementFromPoint(a.ex + 1, a.ey) === cv) return a; M.cam = {...M.cam, x: M.cam.x - 70 / M.cam.s, y: M.cam.y - 90 / M.cam.s}; whDraw(); }   // not under the overview or a panel
  return at(); }"""
PIX = """([x, y, w]) => { const cv = whCv(), r = cv.getBoundingClientRect(), d = window.devicePixelRatio || 1, cx = cv.getContext('2d'); let best = null, bd = 1e9;   // across the border's edge: the pixel nearest the colour w
  for(let dx = -2; dx <= 3; dx++){ const g = cx.getImageData(Math.round((x - r.x) * d) + dx, Math.round((y - r.y) * d), 1, 1).data, v = [g[0], g[1], g[2], g[3]], dd = Math.abs(v[0] - w[0]) + Math.abs(v[1] - w[1]) + Math.abs(v[2] - w[2]); if(dd < bd){ bd = dd; best = v; } }
  return best; }"""
MK = "() => JSON.parse(localStorage.getItem('tvWhMarks') || 'null')"
# 056: the press-and-hold case needs a menu item under the finger once the menu opens (else the release presses nothing and LESSON #167 isn't
# tested). The menu opens at the press, pushed in from the map's edges: opened at the bottom right it sits where any press near there puts it, so
# the finger goes on its Home item and the system is moved under it.
LP_AT = """(id) => { const S = whS, M = S.M, cv = whCv(), r = cv.getBoundingClientRect(), bx = S.el.querySelector('.wh-box');
  whMenuOpen(id, bx.clientWidth, bx.clientHeight); const h = S.el.querySelector('.wh-smenu [data-wh-m="st:home"]').getBoundingClientRect(); whMenuClose(false);
  const x = h.left + h.width / 2 - r.x, y = h.top + h.height / 2 - r.y, p = M.P.get(id);
  M.cam = {x: p.x + WH_NW / 2 - x / M.cam.s, y: p.y + WH_NH / 2 - y / M.cam.s, s: M.cam.s}; whDraw();
  return {x: r.x + x, y: r.y + y, on: document.elementFromPoint(r.x + x, r.y + y) === cv && whHit(whToWorld(x, y)) === id}; }"""
MENU = "() => { const m = document.querySelector('.wh-smenu'); return m && !m.hidden; }"

def near(c, want, tol=40): return c[3] > 200 and all(abs(a - b) <= tol for a, b in zip(c[:3], want))

def menu_on(pg, sid):   # a right-click on the system; if another box lies over that point (a locked system keeps its place while the tree moves), its own menu by script
    a = pg.evaluate(AT, sid)
    if pg.evaluate("([x, y]) => { const r = whCv().getBoundingClientRect(); return whHit(whToWorld(x - r.x, y - r.y)); }", [a['x'], a['y']]) == sid: pg.mouse.click(a['x'], a['y'], button='right')
    else: pg.evaluate("([id, x, y]) => { const r = whCv().getBoundingClientRect(); whMenuOpen(id, x - r.x, y - r.y); }", [sid, a['x'], a['y']])
    pg.wait_for_timeout(150); return a

def cases(b, html, parts=('empty', 'menu', 'lock', 'copy', 'store', 'phone')):
    out, errs = [], []
    ctx, pg = start(b, html, 1440, errs)
    if not pg.evaluate("typeof whMenuOpen === 'function'"): out.append('no system menu'); ctx.close(); return out, errs
    J = pg.evaluate("() => { const T = whTable(); return T.names.filter(n => /^J\\d{6}$/.test(n)).slice(0, 8); }")
    intel_on(pg); t = time.time()
    jump(pg, '1DQ1-A', t)
    pg.click('#tabBtnWh'); pg.wait_for_timeout(400)
    if 'empty' in parts:
        e0 = pg.evaluate(BOX)
        if pg.evaluate("document.querySelector('.wh-empty').hidden"): out.append('the empty map should say nothing is mapped yet')
        if e0[1] < e0[2] - 16: out.append(f'1440: the empty map should reach the bottom of the screen: height {e0[0]}, bottom {e0[1]} of {e0[2]}')
    jump(pg, J[0], t + 1); jump(pg, J[1], t + 2); jump(pg, J[0], t + 3); jump(pg, J[2], t + 4)
    pg.click('#tabBtnWh'); pg.wait_for_timeout(400)
    if 'empty' in parts:
        e1 = pg.evaluate(BOX)
        if abs(e1[0] - e0[0]) > 1: out.append(f'1440: adding the first systems resized the map: {e0[0]} → {e1[0]}')
    ids = pg.evaluate("(n) => n.map(x => whIdOf(x))", ['1DQ1-A', J[0], J[1], J[2]])
    k1, j0, j1, j2 = ids
    if 'menu' in parts:
        a = menu_on(pg, j1)
        m = pg.evaluate("""() => { const m = document.querySelector('.wh-smenu'); return {on: !m.hidden, role: m.getAttribute('role'), x: !!m.querySelector('.x-close'),
          st: [...m.querySelectorAll('[role=menuitemradio]')].map(b => b.textContent.trim()), routes: /routes/i.test(m.textContent), focus: document.activeElement === m.querySelector('[data-wh-m]'),
          sel: whS.sel}; }""")
        if not m['on']: out.append('a right-click on a system should open its menu')
        else:
            if m['role'] != 'menu' or m['x']: out.append(f'the system menu is a menu, with no close button: role {m["role"]}, close button {m["x"]}')
            if m['st'] != ['Home', 'Friendly', 'Looking for', 'Warning', 'Target', 'Dangerous', 'No status']: out.append(f'the statuses: {m["st"]}')
            if m['routes']: out.append('"Routes from here" is part 4: not in the menu yet')
            if not m['focus'] or m['sel'] != j1: out.append(f'focus on the first item, the system in focus: {m["focus"]}, {m["sel"]} (want {j1})')
            pg.keyboard.press('ArrowDown'); f = pg.evaluate("document.activeElement.textContent.trim()")
            if f != 'Friendly': out.append(f'ArrowDown should move to the next item: {f!r}')
            pg.keyboard.press('Escape'); pg.wait_for_timeout(100)
            if pg.evaluate(MENU) or not pg.evaluate("document.activeElement === document.querySelector('.wh-box')"): out.append('Esc closes the menu and gives the focus back to the map')
            menu_on(pg, j1); pg.click('.wh-smenu [data-wh-m="st:danger"]'); pg.wait_for_timeout(200)
            if pg.evaluate(MENU): out.append('a pick closes the menu')
            mk = pg.evaluate(MK)
            if not mk or (mk['sys'].get(str(j1)) or {}).get('st') != 'danger': out.append(f'the status stored in tvWhMarks: {mk}')
            a = pg.evaluate(AT, j1); c = pg.evaluate(PIX, [a['ex'], a['ey'], list(DANGER)])
            if not near(c, DANGER): out.append(f'the box\'s border in the Dangerous colour: {c}')
            a0 = pg.evaluate(AT, j0); c0 = pg.evaluate(PIX, [a0['ex'], a0['ey'], list(DANGER)])
            if near(c0, DANGER): out.append('a system with no status keeps its neutral border')
            sp = pg.evaluate("() => [...document.querySelectorAll('[data-pnb=\"sum\"] .wh-sh .it-gtag.wh-st')].map(e => [e.textContent, e.className])")
            if not sp or sp[0][0] != 'Dangerous' or 'st-danger' not in sp[0][1]: out.append(f'the System panel names the status in the page\'s tag: {sp}')
            pg.mouse.move(a['x'], a['y']); pg.mouse.move(a['x'] + 2, a['y'] + 1); pg.wait_for_timeout(80)
            ti = pg.evaluate("whCv().title")
            if 'status: Dangerous' not in ti: out.append(f'the box\'s hover names its status: {ti!r}')
            menu_on(pg, j1); pg.evaluate("() => { document.querySelector('.wh-smenu [data-wh-mtag]').value = 'ABCDEFGHIJKL'; }")
            pg.click('.wh-smenu [data-wh-m="tag"]'); pg.wait_for_timeout(150)
            tg = (pg.evaluate(MK)['sys'].get(str(j1)) or {}).get('tag'); tp = pg.evaluate("() => [...document.querySelectorAll('[data-pnb=\"sum\"] .wh-sh .it-gtag.wh-st')].map(e => e.textContent)")
            if tg != 'ABCDEFGH' or 'ABCDEFGH' not in tp: out.append(f'the tag cut to 8 and shown in the System panel: {tg!r}, {tp}')
            menu_on(pg, j0); pg.fill('.wh-smenu [data-wh-mtag]', 'HOME'); pg.press('.wh-smenu [data-wh-mtag]', 'Enter'); pg.wait_for_timeout(150)
            if (pg.evaluate(MK)['sys'].get(str(j0)) or {}).get('tag') != 'HOME' or pg.evaluate(MENU): out.append('Enter in the tag field sets the tag and closes the menu')
            pg.reload(); pg.wait_for_timeout(500); pg.click('#tabBtnWh'); pg.wait_for_timeout(400)
            pg.evaluate("(id) => whSelect(id)", j1); pg.wait_for_timeout(150)
            a = pg.evaluate(AT, j1); c = pg.evaluate(PIX, [a['ex'], a['ey'], list(DANGER)])
            sp = pg.evaluate("() => [...document.querySelectorAll('[data-pnb=\"sum\"] .wh-sh .it-gtag.wh-st')].map(e => e.textContent)")
            if not near(c, DANGER) or sp != ['Dangerous', 'ABCDEFGH']: out.append(f'status and tag kept after a reload: border {c}, panel {sp}')
        e = pg.evaluate("""() => { const cv = whCv(), r = cv.getBoundingClientRect(), v = whFree();
          for(let y = v.t + 20; y < v.b - 20; y += 23) for(let x = v.l + 20; x < v.r - 20; x += 31){ if(whHit(whToWorld(x, y)) === null && document.elementFromPoint(r.x + x, r.y + y) === cv) return [r.x + x, r.y + y]; } return null; }""")
        pg.mouse.click(e[0], e[1], button='right'); pg.wait_for_timeout(150)
        if pg.evaluate("document.querySelector('.wh-hmenu').hidden") or pg.evaluate(MENU): out.append('a right-click on empty space opens "Add a system here" (and not the system menu)')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(80)
    if 'lock' in parts:
        menu_on(pg, j1); pg.fill('.wh-smenu [data-wh-mtag]', 'LK'); pg.press('.wh-smenu [data-wh-mtag]', 'Enter'); pg.wait_for_timeout(150)
        menu_on(pg, j1); pg.click('.wh-smenu [data-wh-m="lock"]'); pg.wait_for_timeout(150)
        msg = pg.inner_text('.wh-msg'); nm = pg.evaluate("(id) => whName(id)", j1)
        if msg != f'{nm} is locked: it can’t be moved or removed until you unlock it.': out.append(f'the lock message (D34\'s words): {msg!r}')
        p0 = pg.evaluate("(id) => { const p = whS.M.P.get(id); return [p.x, p.y]; }", j1)
        a = pg.evaluate(AT, j1); pg.mouse.move(a['x'], a['y']); pg.mouse.down(); pg.mouse.move(a['x'] + 60, a['y'] + 40, steps=6); pg.mouse.up(); pg.wait_for_timeout(150)
        p1 = pg.evaluate("(id) => { const p = whS.M.P.get(id); return [p.x, p.y]; }", j1)
        if p1 != p0: out.append(f'a locked system doesn\'t move when dragged: {p0} → {p1}')
        # a group with the locked one: the others move, it stays
        G = pg.evaluate("(a) => { const r = whCv().getBoundingClientRect(), c = whS.M.cam; return a.map(id => { const p = whS.M.P.get(id); return [r.x + (p.x - c.x) * c.s, r.y + (p.y - c.y) * c.s, r.x + (p.x + 112 - c.x) * c.s, r.y + (p.y + 48 - c.y) * c.s]; }); }", [j0, j1])
        pg.evaluate("() => whS.M.group.clear()")
        for g in G:
            pg.keyboard.down('Shift'); pg.mouse.click((g[0] + g[2]) / 2, (g[1] + g[3]) / 2); pg.keyboard.up('Shift')
        q0 = pg.evaluate("(id) => { const p = whS.M.P.get(id); return [p.x, p.y]; }", j0)
        cx, cy = (G[0][0] + G[0][2]) / 2, (G[0][1] + G[0][3]) / 2
        pg.mouse.move(cx, cy); pg.mouse.down(); pg.mouse.move(cx + 30, cy + 25, steps=5); pg.mouse.up(); pg.wait_for_timeout(150)
        q1 = pg.evaluate("(id) => { const p = whS.M.P.get(id); return [p.x, p.y]; }", j0); p2 = pg.evaluate("(id) => { const p = whS.M.P.get(id); return [p.x, p.y]; }", j1)
        if pg.evaluate("whS.M.group.size") < 2 or q1 == q0 or p2 != p0: out.append(f'a group drag: the unlocked one moves ({q0} → {q1}), the locked one stays ({p0} → {p2})')
        pg.evaluate("() => { whS.M.group.clear(); document.querySelector('[data-wh-pop=\"set\"]').click(); }"); pg.wait_for_timeout(100); pg.click('[data-wh-z="arr"]'); pg.wait_for_timeout(200)
        p3 = pg.evaluate("(id) => { const p = whS.M.P.get(id); return [p.x, p.y]; }", j1); pos = pg.evaluate("() => Object.keys(JSON.parse(localStorage.getItem('tvWhChain')).pos)")
        if p3 != p0 or str(j0) in pos: out.append(f'Rearrange leaves the locked system where it is ({p0} → {p3}) and drops the others\' places ({pos})')
        menu_on(pg, j1)
        rm = pg.evaluate("() => { const b = document.querySelector('.wh-smenu [data-wh-m=\"del\"]'); return [b.getAttribute('aria-disabled'), b.textContent]; }")
        if rm[0] != 'true' or '(unlock first)' not in rm[1]: out.append(f'Remove is greyed with "(unlock first)" while locked: {rm}')
        pg.evaluate("() => document.querySelector('.wh-smenu [data-wh-m=\"del\"]').click()"); pg.wait_for_timeout(150)   # aria-disabled: Playwright won't press it
        if not pg.evaluate("(id) => !!whS.st.sys[id]", j1) or 'is locked' not in pg.inner_text('.wh-msg'): out.append('the menu\'s Remove refuses while locked')
        pg.keyboard.press('Escape'); pg.evaluate("(id) => whSelect(id)", j1); pg.wait_for_timeout(150)
        pg.evaluate("() => document.querySelector('[data-pnb=\"sum\"] [data-wh-del]').click()"); pg.wait_for_timeout(150)
        if not pg.evaluate("(id) => !!whS.st.sys[id]", j1) or 'is locked' not in pg.inner_text('.wh-msg'): out.append('the System panel\'s Remove refuses while locked')
        n0 = pg.evaluate("(id) => whLinksOf(id).length", j1)
        pg.click('[data-pnb="sum"] [data-wh-dl]'); pg.wait_for_timeout(150)
        if pg.evaluate("(id) => whLinksOf(id).length", j1) != n0 - 1: out.append('a connection touching a locked system can still be deleted')
        menu_on(pg, j1); pg.click('.wh-smenu [data-wh-m="lock"]'); pg.wait_for_timeout(150)
        menu_on(pg, j1)
        if pg.evaluate("() => document.querySelector('.wh-smenu [data-wh-m=\"del\"]').getAttribute('aria-disabled')"): out.append('unlocked: Remove is no longer greyed')
        pg.click('.wh-smenu [data-wh-m="del"]'); pg.wait_for_timeout(150)
        gone = pg.evaluate("(id) => [!!whS.st.sys[id], whLinksOf(id).length, !!(JSON.parse(localStorage.getItem('tvWhMarks')).sys[id])]", j1)
        if gone != [False, 0, False]: out.append(f'Remove takes the system, its connections and its marks: {gone}')
        pg.click('[data-wh-pop="add"]'); pg.wait_for_timeout(100); pg.fill('.wh-addf input[name=sys]', J[1]); pg.click('.wh-addf button[type=submit]'); pg.wait_for_timeout(150); pg.evaluate("() => whPopClose()")
        if pg.evaluate("(id) => JSON.stringify(whMk(id))", j1) != '{}': out.append('a system removed and added again starts with no status, tag or lock')
    if 'copy' in parts:
        ctx.grant_permissions(['clipboard-read', 'clipboard-write'])
        menu_on(pg, j0); pg.click('.wh-smenu [data-wh-m="copy"]'); pg.wait_for_timeout(200)
        nm = pg.evaluate("(id) => whName(id)", j0)
        try: clip = pg.evaluate("navigator.clipboard.readText()")
        except Exception as e: clip = f'(unreadable: {e})'
        if clip != nm or pg.inner_text('.wh-msg') != f'Copied {nm}.': out.append(f'Copy the name: the clipboard {clip!r}, the line {pg.inner_text(".wh-msg")!r}')
        pg.evaluate("() => { navigator.clipboard.writeText = () => Promise.reject(new Error('not allowed')); }")
        menu_on(pg, j0); pg.click('.wh-smenu [data-wh-m="copy"]'); pg.wait_for_timeout(200)
        h = pg.evaluate("() => { const f = document.querySelector('.wh-smenu input.wh-mcopy'); return f && [f.value, document.activeElement === f, f.selectionStart, f.selectionEnd]; }")
        if h != [nm, True, 0, len(nm)]: out.append(f'refused: the name stays in the menu, selected: {h}')
        pg.keyboard.press('Escape')
    if 'store' in parts:
        # an older page (part 1: PART1, main before 051) in the same browser saves its chain: tvWhMarks stays as it was, and this page still shows the marks
        menu_on(pg, j0); pg.click('.wh-smenu [data-wh-m="st:home"]'); pg.wait_for_timeout(150)
        a = pg.evaluate(AT, j0); pg.mouse.move(a['x'], a['y']); pg.mouse.down(); pg.mouse.move(a['x'] + 90, a['y'] + 70, steps=6); pg.mouse.up(); pg.wait_for_timeout(150)   # off its tree place, so its own place can be told apart
        menu_on(pg, j0); pg.click('.wh-smenu [data-wh-m="lock"]'); pg.wait_for_timeout(150)
        pg.evaluate("(id) => { const s = JSON.parse(localStorage.getItem('tvWhMarks')); s.sys['31999999'] = {st: 'target'}; localStorage.setItem('tvWhMarks', JSON.stringify(s)); }", j0)   # a system not on the map
        before = pg.evaluate("localStorage.getItem('tvWhMarks')")
        old = subprocess.run(['git', '-C', REPO, 'show', PART1 + ':index.html'], capture_output=True, text=True, encoding='utf-8').stdout
        if 'whMenuOpen' in old or 'function whRead' not in old: out.append(f'store: no part-1 page at {PART1} (git fetch --depth=200 origin main)')
        else:
            with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f:
                f.write(old); op = f.name
            try:
                q = ctx.new_page(); q.goto('file://' + op); q.wait_for_timeout(500); q.click('#tabBtnWh'); q.wait_for_timeout(400)
                q.evaluate("(id) => { const s = whS.st.sys[id]; s.notes = 'from the older page'; whSave(); }", j0); q.wait_for_timeout(100)
                q.evaluate("() => { document.querySelector('[data-wh-pop=\"set\"]').click(); document.querySelector('[data-wh-z=\"arr\"]').click(); }"); q.wait_for_timeout(200)   # the older page's Rearrange: every place dropped
                after = q.evaluate("localStorage.getItem('tvWhMarks')"); ch = q.evaluate("(id) => JSON.parse(localStorage.getItem('tvWhChain')).sys[id].notes", j0); q.close()
                if after != before or ch != 'from the older page': out.append(f'store: the older page\'s save changed tvWhMarks or lost its own edit ({ch!r})')
            finally: os.unlink(op)
        lk = pg.evaluate("(id) => whMk(id).at", j0)
        pg.reload(); pg.wait_for_timeout(500); pg.click('#tabBtnWh'); pg.wait_for_timeout(300)
        r = pg.evaluate("(id) => [whMk(id).st, whLocked(id), !!whS.mk['31999999'], whS.st.sys[id].notes]", j0)
        pl = pg.evaluate("(id) => { const p = whS.M.P.get(id); return [p.x, p.y]; }", j0)
        if not lk or pl != lk: out.append(f'store: the older page\'s Rearrange moved the locked system: {lk} → {pl}')
        if r != ['home', True, False, 'from the older page']: out.append(f'store: read back after the older page (status, lock, a stray entry dropped, its edit kept): {r}')
        pg.evaluate("() => whMkSave()")
        if '31999999' in pg.evaluate("localStorage.getItem('tvWhMarks')"): out.append('store: marks for a system no longer on the map are dropped')
    if not pg.evaluate("document.documentElement.scrollWidth <= innerWidth"): out.append('1440: sideways scroll')
    ctx.close()
    if 'phone' in parts:
        chain = {'v': 1, 'sys': {}, 'links': [], 'pos': {}}
        now = int(time.time() * 1000)
        for i, n in enumerate([k1, j0, j2]): chain['sys'][str(n)] = {'cls': None, 'statics': '', 'who': '', 'notes': '', 't': now - 9000 + i, 'u': now, 'src': 'you'}
        for a_, b_ in ((k1, j0), (j0, j2)): chain['links'].append({'a': a_, 'b': b_, 't': now, 'u': now, 'seen': now, 'sig': '', 'type': '', 'life': '', 'mass': '', 'size': ''})
        for full in (False, True):
            ctx, pg = start(b, html, 390, errs, h=844, touch=True, chain=chain if full else None)
            pg.tap('#tabBtnWh'); pg.wait_for_timeout(500)
            hb = pg.evaluate(BOX)
            if 'empty' in parts:
                if hb[1] < hb[2] - 12: out.append(f'390: the {"full" if full else "empty"} map should reach the bottom of the screen: {hb}')
                if not full: e390 = hb[0]
                elif abs(hb[0] - e390) > 1: out.append(f'390: the empty and the full map differ in height: {e390} vs {hb[0]}')
            if full:
                a = pg.evaluate(LP_AT, j0)
                if not a['on']: out.append(f'390: the system isn\'t under the finger for the press and hold: {a}')
                cam0 = pg.evaluate("[whS.M.cam.x, whS.M.cam.y, whS.M.cam.s]"); p0 = pg.evaluate("(id) => { const p = whS.M.P.get(id); return [p.x, p.y]; }", j0)
                cdp = ctx.new_cdp_session(pg)
                cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': a['x'], 'y': a['y']}]}); pg.wait_for_timeout(750)
                if not pg.evaluate("([x, y]) => { const e = document.elementFromPoint(x, y); return !!(e && e.closest('.wh-smenu [data-wh-m=\"st:home\"]')); }", [a['x'], a['y']]):
                    out.append('390: no menu item under the finger once the menu opens: LESSON #167 can\'t be tested (056)')
                cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []}); pg.wait_for_timeout(200)
                m = pg.evaluate("""() => { const m = document.querySelector('.wh-smenu'), r = m.getBoundingClientRect(), bx = document.querySelector('.wh-box').getBoundingClientRect();
                  return {on: !m.hidden, rows: [...m.querySelectorAll('button.wh-mi')].every(b => b.getBoundingClientRect().height >= 44),
                    inside: r.left >= bx.left - 1 && r.right <= bx.right + 1 && r.top >= bx.top - 1 && r.bottom <= Math.min(bx.bottom, innerHeight) + 1}; }""")
                cam1 = pg.evaluate("[whS.M.cam.x, whS.M.cam.y, whS.M.cam.s]"); p1 = pg.evaluate("(id) => { const p = whS.M.P.get(id); return [p.x, p.y]; }", j0)
                if not m['on']: out.append('390: press and hold on a system should open its menu')
                elif not m['rows'] or not m['inside']: out.append(f'390: the menu\'s rows 44 px, inside the map and the screen: {m}')
                if cam1 != cam0 or p1 != p0: out.append(f'390: press and hold pans or drags: camera {cam0} → {cam1}, system {p0} → {p1}')
                if pg.evaluate("(id) => JSON.stringify(whMk(id))", j0) != '{}': out.append('390: lifting the finger picked a menu item (LESSON #167)')
            if not pg.evaluate("document.documentElement.scrollWidth <= innerWidth"): out.append(f'390: sideways scroll ({"full" if full else "empty"})')
            ctx.close()
    return out, errs

MUTANTS = [
    ('a locked system moved by an older page\'s Rearrange', "return m.lock && m.at ? m.at : p || null; }", "return p || null; }", ('store',)),
    ('a locked system dragged', ".filter(n => !whLocked(n)).map(n => [n, {...M.P.get(n)}])", ".map(n => [n, {...M.P.get(n)}])", ('lock',)),
    ('Remove allowed while locked', "  const st = whState().st; if(whLocked(id)) return false;", "  const st = whState().st;", ('lock',)),
    ('the status lost on reload', "    if(WH_ST.some(x => x[0] === m.st)) e.st = m.st;", "", ('menu',)),
    ('the marks of a removed system kept', "delete st.sys[id]; delete st.pos[id]; delete whS.mk[id];", "delete st.sys[id]; delete st.pos[id];", ('lock',)),
    ('the empty map at its old height', "  if(box.style.getPropertyValue('--whH') !== H + 'px') box.style.setProperty('--whH', H + 'px');", "  if(n && box.style.getPropertyValue('--whH') !== H + 'px') box.style.setProperty('--whH', H + 'px');", ('empty',)),
    ('the release after a press and hold clicks the menu (LESSON #167)', "if(M.lpOpen){ M.lpOpen = false; ev.preventDefault(); }", "if(M.lpOpen){ M.lpOpen = false; }", ('phone',)),
    ('the status drawn on no border', "c.strokeStyle = sc || C.line; c.lineWidth = sc ? 2.2 : 1.2;", "c.strokeStyle = C.line; c.lineWidth = 1.2;", ('menu',)),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, 'the system menu: the empty map, the menu, status, tag, lock, copy, stored data, a phone')
    check(not errs, f'no page errors {errs[:3]}')
    for name, old, new, parts in MUTANTS:
        if PAGE.count(old) != 1: check(False, f'mutant "{name}": its line isn\'t in the page once'); continue
        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f:
            f.write(PAGE.replace(old, new)); mp = f.name
        try:
            try: mo, me = cases(b, mp, parts)
            except Exception as e: mo, me = [f'the check stopped: {str(e).splitlines()[0]}'], []   # the mutant broke a later step: caught
            check(bool(mo) or bool(me), f'mutant "{name}" fails ({(mo or me or ["nothing"])[0][:90]})')
        finally: os.unlink(mp)
    b.close()
print('FAILURES:', NS['fails'])
sys.exit(1 if NS['fails'] else 0)
