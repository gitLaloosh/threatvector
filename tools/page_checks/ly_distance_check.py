"""The Intel map's Distance filter in jumps or light years (build queue 067; roadmap/ly-distance-plan.md, mockup Claude outputs/ly_distance_mockup.html).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/ly_distance_check.py [index.html]   -> 'FAILURES: N' (must be 0)

The owner: "Within N jumps → Distance (Recommended)", "Only where a jump can land (Recommended)", "Typed + quick picks (Recommended)", "From you",
the landing rules "i can confirm"; at the build review "Add 7.5 LY pick (Recommended)". Uses intel_check.py's made-up folder, mocks and names
(you in 1DQ1-A). Every expected value is worked out here from the map's own table (positions, security, regions), apart from the page's code.
Checks, at 1440 px and 390 px:
  * the filter is named Distance, its notes (bridges off and on) and its settings button's label;
  * switched on, its settings open; the Jumps / Light years switch; Light years: the LY stepper (7.0), five quick picks 6 / 7 / 7.5 / 8 / 10 LY
    with the ships in their titles, the one equal to the value pressed (none for an off-pick value); focus kept on the switch after it redraws;
  * the match in light years, for 6.0, 7.0, 7.5 and 10.0 LY: every system whose LY from you, rounded up to 0.01 as the hover shows it, is the
    value or less and where a jump drive can land, and nothing else; your system matches; the hover's LY and the filter agree for every system;
  * the rounding: a system just past a tenth (shown one hundredth over) stays out at that tenth;
  * where a jump drive can't land: from a low-sec system beside a 0.5 one, the 0.5 system in range is out and its hover says why (high-sec); a
    landable one in range says "within jump range"; Pochven by region; Zarzakh by ID; nothing added out of range or on your own system;
  * the Only line "within 7.0 LY (jump drive)", back to "within N jumps"; the panel's count follows; the stepper shows tenths and snaps a typed
    value (a computer);
  * Jumps: exactly today's match (stargate jumps from you, N or fewer);
  * stored: mode and LY in tvMapStack across a reload; a stack from before reads as Jumps with its N; bad values fall back to Jumps, 7.0; the
    page from main reads the new stack without trouble (its N kept);
  * 390 px: the panel inside the screen, its switch and quick picks 44 px tall, no sideways scroll; no page errors;
  * mutants, each must fail (see MUTANTS).
"""
import sys, os, json, time, tempfile, subprocess
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
T0 = time.time()

def start(b, html, w, errs, stack=None):
    touch = w < 600
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': 1000 if not touch else 844}, has_touch=touch, is_mobile=touch, device_scale_factor=2 if touch else 1)
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); route(ctx)
    pg = ctx.new_page(); pg.goto('file://' + html)
    pg.evaluate("([s, st]) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({nearShown: false, channels: ['region.intel'], me: 95000001, range: 3, sound: false, notify: false, forget: 15, hideFriendly: true}));"
                " if(st !== null) localStorage.setItem('tvMapStack', st); }", [SIDE, stack])
    pg.reload(); pg.wait_for_timeout(400)
    setup_logs(pg); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg)
    pg.wait_for_function("() => typeof itm !== 'undefined' && itm.el && itm.el.isConnected && itm.D && itm.home >= 0", timeout=30000)
    pg.evaluate("() => document.querySelector('#intelPanel .it-map-box').scrollIntoView({block: 'center'})"); pg.wait_for_timeout(200)
    return ctx, pg

# the plan's rule, worked out here: in range (rounded up to 0.01, as the hover shows it) and landable (not 0.5+ as shown, not Pochven, not Zarzakh)
RULE = """(t) => { const T = itMapTable(), ids = itGraphGet().ids, h = itm.home, land = [], why = {};
  for(let i = 0; i < T.n; i++){ if(i === h) continue; const d = itMapLy(i, h); if(d === null) continue; if(Math.ceil(d * 100 - 1e-9) > t * 10) continue;
    const w = T.secT[i] >= 5 ? 'high-sec' : T.regions[T.reg[i]] === 'Pochven' ? 'Pochven' : ids[i] === 30100000 ? 'Zarzakh' : ''; if(w) why[i] = w; else land.push(i); }
  return {land, why}; }"""
MATCH = "() => { const mt = itMapMatch(); return mt ? [...mt.list].sort((a, b) => a - b) : null; }"
ONLY = "() => { const e = itm.el.querySelector('.it-map-only'); return e ? e.textContent : ''; }"
SET = "(v) => { itMapSt().near.ly = v; itMpChanged(); }"

def cases(b, html, widths=(1440, 390)):
    out, errs = [], []
    for w in widths:
        ctx, pg = start(b, html, w, errs)
        P = f'{w} px: '
        # the name and notes
        f = pg.evaluate("() => { const f = IT_MAP_FILTERS.find(x => x.k === 'near'); const nb = itm.el.querySelector('[data-it-mpn=\"near\"]'); return [f.name, f.note, itMapFNote(f), nb ? nb.getAttribute('aria-label') : null]; }")
        if f[0] != 'Distance': out.append(P + f'the filter is named {f[0]!r} (want Distance)')
        if f[1] != 'only: systems within N stargate jumps of you, or N light years where a jump drive can land' or f[2] != f[1]: out.append(P + f'its note {f[1:3]}')
        if f[3] != 'Distance: how far': out.append(P + f'its settings button {f[3]!r}')
        bn = pg.evaluate("() => { it.set.bridgesOn = true; const f = IT_MAP_FILTERS.find(x => x.k === 'near'), t = itBridgeOn() ? itMapFNote(f) : null; it.set.bridgesOn = false; return t; }")
        if bn is not None and bn != 'only: systems within N jumps of you (jump bridges you can use counted), or N light years where a jump drive can land': out.append(P + f'its note with bridges on {bn!r}')
        # switched on: its settings open; the switch
        pg.evaluate("() => itm.el.querySelector('[data-im-f=\"near\"]').click()"); pg.wait_for_timeout(250)
        op = pg.evaluate("() => [itMpShown() && itMp.k === 'near', itMapSt().only.near, [...itMp.el.querySelectorAll('[name=itMpNear]')].map(r => [r.value, r.checked])]")
        if op != [True, True, [['j', True], ['ly', False]]]: out.append(P + f'switched on: settings {op} (want open, Jumps picked)')
        pg.evaluate("() => itMp.el.querySelector('[name=itMpNear][value=ly]').click()"); pg.wait_for_timeout(200)
        pn = pg.evaluate("() => [itMapSt().near.mode, itMapSt().near.ly, (document.activeElement || {}).name, (document.activeElement || {}).value, !!itMp.el.querySelector('[data-rs=mapLy]'), !itMp.el.querySelector('[data-rs=mapNear]'),"
                         " [...itMp.el.querySelectorAll('[data-it-mply]')].map(x => [x.textContent, x.title, x.getAttribute('aria-pressed')]), (itMp.el.querySelector('[data-rs=mapLy] .rs-v') || {}).value]")
        if pn[:6] != ['ly', 70, 'itMpNear', 'ly', True, True]: out.append(P + f'Light years: {pn[:6]} (want ly, 70, focus on the switch, the LY stepper only)')
        q = pn[6]
        if [x[0] for x in q] != ['6 LY', '7 LY', '7.5 LY', '8 LY', '10 LY']: out.append(P + f'quick picks {[x[0] for x in q]}')
        want_t = ['Titans, supercarriers', 'Carriers, dreadnoughts, FAX', 'Command carriers', 'Black Ops, Lancers', 'Jump freighters, Rorqual']
        if [x[1] for x in q] != [t + ', Jump Drive Calibration V' for t in want_t]: out.append(P + f'quick pick titles {[x[1] for x in q]}')
        if [x[2] for x in q] != ['false', 'true', 'false', 'false', 'false']: out.append(P + f'pressed at 7.0: {[x[2] for x in q]}')
        if pn[7] != '7.0': out.append(P + f'the stepper shows {pn[7]!r} (want 7.0)')
        # the match, for several ranges, against the rule worked out here
        for t in (60, 70, 75, 100):
            pg.evaluate(SET, t)
            r, m = pg.evaluate(f"({RULE})({t})"), pg.evaluate(MATCH)
            if m != r['land']: out.append(P + f'{t / 10} LY: {len(m or [])} match, the rule {len(r["land"])} ({sorted(set(m or []) ^ set(r["land"]))[:4]})')
            if t == 100 and len(r['land']) < 20: out.append(P + f'10 LY: only {len(r["land"])} systems in range (the case is too small)')
        pg.evaluate(SET, 70)
        if not pg.evaluate("() => itMapMatched(itm.home)"): out.append(P + 'your own system doesn\'t match')
        ag = pg.evaluate("() => { const T = itMapTable(), h = itm.home, mt = itMapMatch(); let bad = 0; for(let i = 0; i < T.n; i++){ if(i === h) continue; const d = itMapLy(i, h); if(d === null) continue;"
                         " const shown = Number(itMapLyText(d)) <= 7 && !itMapNoLand(i); if(shown !== !!mt.m[i]) bad++; } return bad; }")
        if ag: out.append(P + f'the hover\'s LY and the filter disagree for {ag} systems')
        # the rounding: a system just past a tenth is shown one hundredth over and stays out at that tenth
        edge = pg.evaluate("() => { const T = itMapTable(), h = itm.home; for(let i = 0; i < T.n; i++){ if(i === h || itMapNoLand(i)) continue; const d = itMapLy(i, h); if(d === null || d > 20) continue;"
                           " const x = d * 10, t = Math.floor(x); if(t >= 1 && x - t > 1e-6 && x - t < 0.05) return [i, t, itMapLyText(d)]; } return null; }")
        if not edge: out.append(P + 'no system just past a tenth to test the rounding with')
        else:
            pg.evaluate(SET, edge[1])
            inm = pg.evaluate("(i) => !!itMapMatch().m[i]", edge[0])
            if inm or float(edge[2]) <= edge[1] / 10: out.append(P + f'a system shown {edge[2]} LY matches at {edge[1] / 10} LY')
            pg.evaluate(SET, 70)
        # where a jump drive can't land: from a low-sec system beside a 0.5 one
        nl = pg.evaluate("""() => { const T = itMapTable(), G = itGraphGet(), h0 = itm.home, s = itMapSt(), res = {};
          let a = -1, b = -1; for(let i = 0; i < T.n && a < 0; i++){ if(T.secT[i] < 1 || T.secT[i] > 4) continue; for(const j of (G.adj ? G.adj[i] : [])) if(T.secT[j] === 5){ a = i; b = j; break; } }
          if(a < 0){ const E = G.edges || []; for(let k = 0; k < E.length && a < 0; k += 2){ const x = E[k], y = E[k + 1]; if(T.secT[x] >= 1 && T.secT[x] <= 4 && T.secT[y] === 5){ a = x; b = y; } else if(T.secT[y] >= 1 && T.secT[y] <= 4 && T.secT[x] === 5){ a = y; b = x; } } }
          if(a < 0) return {none: true};
          itm.home = a; const ly0 = s.near.ly; s.near.ly = Math.min(200, Math.ceil(itMapLy(a, b) * 10) + 3);
          const tx = (h) => { const d = document.createElement('div'); d.innerHTML = h; return d.textContent; };
          const mt = itMapMatch(); res.b = [itMapNoLand(b), !!mt.m[b], tx(itMapLyTipHtml(b))];
          let c = -1; for(let i = 0; i < T.n; i++) if(i !== a && mt.m[i]){ c = i; break; }
          res.c = c < 0 ? null : itMapLyTipHtml(c); res.ly = (s.near.ly / 10).toFixed(1); res.home = itMapLyTipHtml(a);
          let far = -1; for(let i = 0; i < T.n; i++){ const d = itMapLy(i, a); if(d !== null && d > 25){ far = i; break; } } res.far = far < 0 ? null : itMapLyTipHtml(far);
          let p = T.reg.findIndex(r => T.regions[r] === 'Pochven'); res.p = p < 0 ? null : itMapNoLand(p);
          const z0 = IT_MAP_NOLAND.sys, zi = T.secT.findIndex((v, i) => v < 5 && T.regions[T.reg[i]] !== 'Pochven'); IT_MAP_NOLAND.sys = G.ids[zi]; res.z = itMapNoLand(zi) || (T.secT[zi] >= 5 ? 'hs' : ''); IT_MAP_NOLAND.sys = z0;
          res.zsec = T.secT[zi];
          itm.home = h0; s.near.ly = ly0; itMt.key = null; itMapMatch(); return res; }""")
        if nl.get('none'): out.append(P + 'no low-sec system beside a 0.5 one to test with')
        else:
            if nl['b'][0] != 'high-sec' or nl['b'][1] or "in range, but a jump drive can't land here (high-sec)" not in nl['b'][2]: out.append(P + f'a 0.5 system in range: {nl["b"]} (want high-sec, out, its hover saying why)')
            if not nl['c'] or f'within jump range ({nl["ly"]} LY)' not in nl['c']: out.append(P + f'a landable system in range: hover {nl["c"]!r}')
            if nl['home'] != '' or nl['far'] not in ('', None): out.append(P + f'a line added on your own system or out of range: {nl["home"]!r} {nl["far"]!r}')
            if nl['p'] != 'Pochven': out.append(P + f'a Pochven system: {nl["p"]!r} (want Pochven)')
            if nl['z'] != 'Zarzakh': out.append(P + f'Zarzakh by its ID: {nl["z"]!r} (want Zarzakh)')
        # the hover itself carries the line
        tip = pg.evaluate("() => { const mt = itMapMatch(); const i = mt.list[0]; itMapTip(i, 20, 20); const h = itm.tip.innerHTML; itMapTip(-1); return h; }")
        if 'within jump range (7.0 LY)' not in tip: out.append(P + f'the hover of a match lacks "within jump range (7.0 LY)": {tip[-160:]!r}')
        # the Only line and the count
        on = pg.evaluate(ONLY)
        if 'within 7.0 LY (jump drive)' not in on: out.append(P + f'the Only line {on!r}')
        cnt = pg.evaluate("() => [itMp.el.querySelector('.it-mp-cnt').textContent, itMapMatch().list.length]")
        if not cnt[0].startswith(f'{cnt[1]} system'): out.append(P + f'the panel\'s count {cnt}')
        # quick picks
        pg.evaluate("() => itMp.el.querySelector('[data-it-mply=\"75\"]').click()"); pg.wait_for_timeout(120)
        qp = pg.evaluate("() => [itMapSt().near.ly, [...itMp.el.querySelectorAll('[data-it-mply]')].map(x => x.getAttribute('aria-pressed')), itMp.el.querySelector('[data-rs=mapLy] .rs-v').value]")
        if qp != [75, ['false', 'false', 'true', 'false', 'false'], '7.5']: out.append(P + f'quick pick 7.5: {qp}')
        pg.evaluate(SET, 69)
        if pg.evaluate("() => [...itMp.el.querySelectorAll('[data-it-mply]')].some(x => x.getAttribute('aria-pressed') === 'true')"): out.append(P + '6.9 LY: a quick pick pressed')
        if w >= 600:   # typed (read-only on a phone): snaps to 0.1
            inp = '.it-mpp [data-rs=mapLy] .rs-v'
            pg.fill(inp, '8.34'); pg.press(inp, 'Enter'); pg.wait_for_timeout(150)
            ty = pg.evaluate("() => [itMapSt().near.ly, itMp.el.querySelector('[data-rs=mapLy] .rs-v').value]")
            if ty != [83, '8.3']: out.append(P + f'typed 8.34: {ty} (want 83, 8.3)')
        pg.evaluate("() => itMp.el.querySelector('[data-it-mply=\"100\"]').click()"); pg.wait_for_timeout(120)
        sv = pg.evaluate("() => { const s = JSON.parse(localStorage.getItem('tvMapStack')); return [s.near.mode, s.near.ly, s.near.n]; }")
        if sv[:2] != ['ly', 100]: out.append(P + f'saved {sv}')
        if w < 600:   # the panel on a phone
            ph = pg.evaluate("() => { const r = itMp.el.getBoundingClientRect(); return [r.left >= -0.5 && r.right <= innerWidth + 0.5, Math.min(...[...itMp.el.querySelectorAll('[data-it-mply]')].map(x => x.getBoundingClientRect().height),"
                             " ...[...itMp.el.querySelectorAll('[name=itMpNear]')].map(x => x.closest('label').getBoundingClientRect().height))]; }")
            if not ph[0] or ph[1] < 43.5: out.append(P + f'the panel on a phone {ph} (want inside the screen, 44 px targets)')
        # back to Jumps: today's match
        pg.evaluate("() => itMp.el.querySelector('[name=itMpNear][value=j]').click()"); pg.wait_for_timeout(200)
        bj = pg.evaluate("() => [itMapSt().near.mode, (document.activeElement || {}).name, (document.activeElement || {}).value, !!itMp.el.querySelector('[data-rs=mapNear]'), !itMp.el.querySelector('[data-it-mply]')]")
        if bj != ['j', 'itMpNear', 'j', True, True]: out.append(P + f'back to Jumps: {bj}')
        for n in (2, 5):
            mj = pg.evaluate(f"() => {{ itMapSt().near.n = {n}; itMpChanged(); const mt = itMapMatch(); return [...mt.list].sort((a, b) => a - b); }}")
            rj = pg.evaluate(f"() => {{ const a = []; for(let i = 0; i < itm.D.length; i++) if(i !== itm.home && itm.D[i] >= 0 && itm.D[i] <= {n}) a.push(i); return a; }}")
            if mj != rj: out.append(P + f'Jumps {n}: {len(mj)} match, stargate jumps {len(rj)}')
        on = pg.evaluate(ONLY)
        if 'within 5 jumps' not in on or 'LY' in on: out.append(P + f'the Only line in Jumps {on!r}')
        if not pg.evaluate("() => document.scrollingElement.scrollWidth <= innerWidth + 1"): out.append(P + 'sideways scroll')
        # stored: across a reload, in light years
        pg.evaluate("() => { itMapSt().near.mode = 'ly'; itMapSt().near.ly = 80; itMapStackSave(); }")
        pg.reload(); pg.wait_for_timeout(500)
        rl = pg.evaluate("() => { itm.st = null; const s = itMapSt(); return [s.near.mode, s.near.ly, s.only.near]; }")
        if rl != ['ly', 80, True]: out.append(P + f'after a reload {rl} (want ly, 80, on)')
        ro = pg.evaluate("""() => { const k = localStorage.getItem('tvMapStack'), s = JSON.parse(k), res = [];
          const t = (x) => { localStorage.setItem('tvMapStack', JSON.stringify(x)); const o = itMapStackRead(); return [o.near.mode, o.near.ly, o.near.n]; };
          res.push(t({...s, near: {n: 7}})); res.push(t({...s, near: {n: 4, mode: 'x', ly: 999}})); res.push(t({...s, near: {n: 4, mode: 'ly', ly: 0}})); res.push(t({...s, near: {n: 4, mode: 'ly', ly: 7.5}}));
          localStorage.setItem('tvMapStack', k); return res; }""")
        if ro != [['j', 70, 7], ['j', 70, 4], ['ly', 70, 4], ['ly', 70, 4]]: out.append(P + f'stored values read back {ro}')
        ctx.close()
    return out, errs

def old_page_reads_new(b):
    """the page from main reads a stack the new page wrote: its N kept, no page error (reverting is safe)"""
    try: old = subprocess.run(['git', '-C', REPO, 'show', 'origin/main:index.html'], capture_output=True, text=True, check=True).stdout
    except Exception as e: return [f'main\'s page not readable from git ({e})'], []
    if "near: {n: 5, mode: 'j', ly: 70}" in old: return [], []   # main already has this build: nothing older to compare with
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f: f.write(old); op = f.name
    errs = []
    try:
        stack = json.dumps({'v': 1, 'colour': 'sec', 'view': 'map', 'only': {'near': True}, 'near': {'n': 6, 'mode': 'ly', 'ly': 75}, 'seen': {'near': True}})
        ctx, pg = start(b, op, 1440, errs, stack=stack)
        r = pg.evaluate("() => { itm.st = null; const s = itMapSt(); return [s.near.n, s.only.near, !!itMapMatch()]; }")
        ctx.close()
        return ([] if r == [6, True, True] else [f'main\'s page reading the new stack: {r} (want N 6, on, a match)']), errs
    finally: os.unlink(op)

MUTANTS = [
    ('the LY rounded to the nearest, not up as the hover shows', "function itMapLyC(d){ return Math.ceil(d * 100 - 1e-9); }", "function itMapLyC(d){ return Math.round(d * 100); }"),
    ('0.5 counted as landable', "const T = itMapTable(); if(itMapSecT(i) >= 5) return 'high-sec';", "const T = itMapTable(); if(itMapSecT(i) > 5) return 'high-sec';"),
    ('Pochven kept', "  if(T.regions[T.reg[i]] === IT_MAP_NOLAND.region) return IT_MAP_NOLAND.region;\n", ""),
    ('Zarzakh not left out', "return itGraphGet().ids[i] === IT_MAP_NOLAND.sys ? IT_MAP_NOLAND.sysName : '';", "return '';"),
    ('Jumps changed', ": D[i] >= 0 && D[i] <= s.near.n;   // as Jumps from you counts", ": D[i] >= 0 && D[i] < s.near.n;   // as Jumps from you counts"),
    ('light years not read back', "if(s.near.mode === 'ly') o.near.mode = 'ly'; ", ""),
    ('the hover never says why', "escapeHtml(w ? `in range, but", "escapeHtml(false ? `in range, but"),
    ('focus lost on the switch', "const r = p.querySelector('[name=itMpNear]:checked'); if(r) r.focus({preventScroll: true});", ""),
    ('no quick pick pressed', "if(b.getAttribute('aria-pressed') !== on) b.setAttribute('aria-pressed', on);", ""),
    ('the Only line still in jumps', "s.near.mode === 'ly' ? `within ${t(s.near.ly)} LY (jump drive)` :", "false ? '' :"),
    ('no 7.5 pick', "[75, 'Command carriers'], ", ""),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, 'Distance: the name, the switch, light years matched as the hover shows them where a jump drive can land, the quick picks, Jumps unchanged, stored, phone')
    check(not errs, f'no page errors {errs[:3]}')
    oo, oe = old_page_reads_new(b)
    for o in oo: check(False, o)
    check(not oo and not oe, f'main\'s page reads the new stack {oe[:2]}')
    for name, old, new in MUTANTS:
        if PAGE.count(old) != 1: check(False, f'mutant "{name}": its line isn\'t in the page once'); continue
        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f:
            f.write(PAGE.replace(old, new)); mp = f.name
        try:
            try: mo, me = cases(b, mp, (1440,))
            except Exception as e: mo, me = [f'the check stopped: {str(e).splitlines()[0][:90]}'], []   # a mutant that breaks the panel outright is caught too
            check(bool(mo) or bool(me), f'mutant "{name}" fails ({(mo or me or ["nothing"])[0][:110]})')
        finally: os.unlink(mp)
    b.close()
print('FAILURES:', NS['fails'])
sys.exit(1 if NS['fails'] else 0)
