"""The Intel map laid out like EVE's in-game 2D map, with a filter bar (build queue 039; Project doc roadmap/map-look-plan.md, mockup
Claude outputs/map_look_mockup.html).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/intel_map_look_check.py [index.html]   -> 'FAILURES: N' (must be 0)

The owner: "is there any way to make it look more alike so players know what they're looking at for systems and regions that they're
familiar with?"; "small push apart seems fine"; "Whole galaxy, centred on you"; "No tint, like the game"; zoom stages, dotted gates
between regions and region names in spaced capitals; "can you add a filter bar near the bottom like the in-game map?"; "Bar stays; name
line fades"; at the build review "yes" to routes past the reach, the shorter info text and "Map: within". Every expected place, region
and jump count here is decoded from the page's INTEL_MAP and INTEL_JUMPS by this check (the second through intel_check.py's first part),
not by the page. Uses intel_check.py's made-up folder, mocks and names (you in 1DQ1-A); every pilot and line is made up. Checks:
  * the layout: every system in the table placed; one scale for x and y (two systems outside the reach, never pushed, sit exactly
    where CCP's flat map puts them, scaled alike); left/right and up/down kept; the systems within the reach at least 12 px apart at
    the starting zoom and each within a few px of CCP's place; the start: you in the middle, a typical gate 16 px; ⤢: every system
    within the reach in the box; zoomed all the way out: every system in the box;
  * the zoom stages: dots under a 34 px gate, circles from 34 px (the circle's fill in the system's colour), names from 80 px;
  * gates between two regions dotted (the dash and colour at the stroke); your region's name white, the others grey, in capitals;
  * the filters: each system's colour (security class; jumps 0 to 10+, none without a gate route; region, never the same colour as a
    region joined by a gate; reports and kills dimming the rest), a dot's pixel follows the pressed filter, a press redraws once;
  * the bar: five buttons inside the map box, the pressed one aria-pressed, 32 px; the name line shown on a press, faded after;
  * routes past the reach (the owner: "yes"): hover shows its route and the tip says reports aren't shown there; a press keeps it; a
    system with no gate route to you: the tip says so, nothing kept;
  * Near You beside the map at 905, 1000 and 1200 px with a busy row (LESSON #113): at least 400 px, no row wider than its box, and
    the map's column (so Near You) the same height for every filter;
  * 390 px: one 44 px button; it opens the row of five 44 px buttons; a pick, Escape (focus back on the button) and a press outside
    close it; no sideways scroll;
  * the info text and "Map: within"; the timings (layout at a 30-jump reach, a redraw of the whole galaxy), printed for the history doc;
  * mutants, each must fail: separate x and y scales, a wider spread off CCP's place, a filter that doesn't redraw, gates between
    regions solid, your region's name grey, a long filter legend allowed to wrap, Escape not closing the phone's row;
  * no page errors.
v2026.11.12.2 fails (no filter bar, the whole galaxy not laid out).
"""
import sys, os, re, json, time, base64, struct, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
_src = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
_src = _src[:_src.index('with sync_playwright() as p:')]
NS = {'__file__': os.path.join(HERE, 'intel_check.py'), '__name__': 'intel_check_prefix'}
exec(compile(_src, 'intel_check.py (first part)', 'exec'), NS)   # the made-up folder, mocks, names; its table checks run too
globals().update({k: v for k, v in NS.items() if not k.startswith('__') and k not in ('check', 'fails')})
from playwright.sync_api import sync_playwright
check = NS['check']
PAGE = open(HTML, encoding='utf-8').read()

# ---- CCP's flat map, decoded here from the page's own table ----
MAP = json.loads(re.search(r'^const INTEL_MAP = (.*);$', PAGE, re.M).group(1))
def i16(b64): b = base64.b64decode(b64); return struct.unpack('<%dh' % (len(b) // 2), b)
XS, YS, SEC = i16(MAP['x']), i16(MAP['y']), struct.unpack('<%db' % MAP['systems'], base64.b64decode(MAP['sec']))
REG = base64.b64decode(MAP['reg'])
IDX = {sid: k for k, sid in enumerate(ids)}
HOME = SYSID['1DQ1-A']
SECCOL = ['#8f2f69', '#6d221d', '#bb1014', '#ce4611', '#de6a0c', '#eeff83', '#71e452', '#62daa6', '#4acff3', '#389cf6', '#2e74df']
JUMPCOL = ['#ffffff', '#4acff3', '#62daa6', '#71e452', '#eeff83', '#de6a0c', '#ce4611', '#bb1014', '#8f2f69', '#7a4a6e', '#6a5a78']
def secclass(s): return 0 if s <= 0 else max(1, min(10, int((s / 10) + 0.5)))
NOGATE = next(sid for sid in ids if sid not in D0)   # a system with no gate route to 1DQ1-A (Pochven, from k-space)
# a busy Near You row (LESSON #113): three pilots, three ships, a count, camp words
HOST = [M.PILOTS[M.pick(98000003, k)][0] for k in range(3)]
T0 = time.time()

def start(b, html, w, errs, h=1000, touch=False):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch, device_scale_factor=2 if touch else 1)
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); route(ctx)
    pg = ctx.new_page(); pg.goto('file://' + html)
    pg.evaluate("(s) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({channels: ['region.intel'], me: 95000001, range: 3, sound: false, notify: false, forget: 15, hideFriendly: true})); }", SIDE)
    pg.reload(); pg.wait_for_timeout(400)
    setup_logs(pg); pg.click('#tabBtnIntel'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg)
    near = sorted((s for s, v in D0.items() if 1 <= v <= 3), key=lambda s: (D0[s], s))
    W(pg, F_INTEL, line(T0, 'Scout Alt', f'{SYSNAME[near[0]]} {HOST[0]} {HOST[1]} {HOST[2]} sabre muninn loki +12 camp on gate bubble')
      + line(T0 + 1, 'Gate Watcher', f'{SYSNAME[near[1]]} {HOST[0]} hurricane +3')); tick(pg, 3200)
    if touch and pg.query_selector('[data-it-nv="map"]'): pg.click('[data-it-nv="map"]'); tick(pg, 600)
    pg.evaluate("() => document.querySelector('#intelPanel .it-map-box').scrollIntoView({block: 'center'})"); pg.wait_for_timeout(200)
    return ctx, pg

VIEW = "(g) => { const k = Math.min(itm.kMax, g / itm.G), i = itm.home; itm.view = {k, tx: itm.W / 2 - itm.P[2 * i] * k, ty: itm.H / 2 - itm.P[2 * i + 1] * k}; itMapDraw(); }"

def layout_cases(b, html, out, errs, parts=('layout', 'look', 'filters', 'bar', 'routes', 'near', 'phone')):
    ctx, pg = start(b, html, 1440, errs)
    if 'layout' in parts:
        L = pg.evaluate("""(ids) => { const n = itMapTable().n, P = itm.P, at = ids.map(id => itGraphGet().at.get(id));
          return {n, placed: [...Array(n).keys()].every(i => isFinite(P[2 * i]) && isFinite(P[2 * i + 1])), vis: itm.vis.map(i => itGraphGet().ids[i]),
            P: at.map(i => [P[2 * i], P[2 * i + 1]]), k: itm.view.k, G: itm.G, home: [itm.Q[2 * itm.home], itm.Q[2 * itm.home + 1]], W: itm.W, H: itm.H}; }""", ids)
        if L['n'] != len(ids) or not L['placed']: out.append(f"every system placed: {L['n']} systems, all placed {L['placed']}")
        reach = set(L['vis'])
        if reach != {s for s, v in D0.items() if v <= 10}: out.append(f'the reach: {len(reach)} systems (want the {sum(1 for v in D0.values() if v <= 10)} within 10 jumps)')
        P = L['P']
        far = [k for k, sid in enumerate(ids) if sid not in reach]
        a, c = far[0], max(far, key=lambda k: abs(XS[k] - XS[far[0]]) + abs(YS[k] - YS[far[0]]))
        sx, sy = (P[c][0] - P[a][0]) / (XS[c] - XS[a]), (P[c][1] - P[a][1]) / (-(YS[c] - YS[a]))
        if abs(sx / sy - 1) > 0.005: out.append(f'one scale for x and y: {sx:.6f} vs {sy:.6f}')
        flips = 0
        for k in range(0, len(far) - 1, 37):
            p, q = far[k], far[k + 1]
            if (XS[q] - XS[p]) * (P[q][0] - P[p][0]) < 0 or (-(YS[q] - YS[p])) * (P[q][1] - P[p][1]) < 0: flips += 1
        if flips: out.append(f'{flips} pairs outside the reach swapped left/right or up/down')
        k0 = L['k']
        rk = [IDX[s] for s in reach]
        # off CCP's place (px at the start zoom): CCP's place by the same scale and the far pair's offset
        moved = max(((P[k][0] - (P[a][0] + (XS[k] - XS[a]) * sx)) ** 2 + (P[k][1] - (P[a][1] - (YS[k] - YS[a]) * sx)) ** 2) ** 0.5 * k0 for k in rk)
        if moved > 14: out.append(f'a system within the reach moved {moved:.1f} px off CCP\'s place at the start (want at most 14)')
        gap = min(((P[x][0] - P[y][0]) ** 2 + (P[x][1] - P[y][1]) ** 2) ** 0.5 * k0 for ii, x in enumerate(rk) for y in rk[ii + 1:])
        if gap < 11.9: out.append(f'the systems within the reach {gap:.2f} px apart at the start (want at least 12)')
        if abs(L['home'][0] - L['W'] / 2) > 1 or abs(L['home'][1] - L['H'] / 2) > 1 or abs(L['G'] * k0 - 16) > 0.5: out.append(f"the start: you at {L['home']} in a {L['W']}x{L['H']} box, a gate {L['G'] * k0:.1f} px")
        pg.click('.it-map-zoom [data-im-z="fit"]'); pg.wait_for_timeout(150)
        o = pg.evaluate("() => itm.vis.filter(i => { const x = itm.Q[2 * i], y = itm.Q[2 * i + 1]; return x < 0 || y < 0 || x > itm.W || y > itm.H; }).length")
        if o: out.append(f'⤢: {o} systems within the reach out of the box')
        box = pg.query_selector('#intelPanel .it-map-box canvas').bounding_box()
        pg.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
        for _ in range(12): pg.mouse.wheel(0, 600); pg.wait_for_timeout(30)
        o = pg.evaluate("() => [itm.view.k, itm.Q.filter((v, j) => j % 2 ? v < 0 || v > itm.H : v < 0 || v > itm.W).length]")
        if o[0] > 1.001 or o[1]: out.append(f'zoomed all the way out: k {o[0]}, {o[1]} coordinates out of the box (want the whole galaxy in it)')
        pg.evaluate("() => { itMapStartView(); itMapDraw(); }")
    if 'look' in parts:
        st = pg.evaluate("(V) => { const v = eval(V); return [30, 40, 85].map(g => { v(g); return itm.stage; }); }", VIEW)
        if st != [0, 1, 2]: out.append(f'the zoom stages at a 30 / 40 / 85 px gate: {st} (want dots, circles, circles with names)')
        px = pg.evaluate("""([V, id]) => { eval(V)(40); const i = itGraphGet().at.get(id), r = Math.max(9, Math.min(15, 40 * 0.2)), c = itm.cv.getContext('2d'), d = window.devicePixelRatio || 1;
          return [...c.getImageData(Math.round(itm.Q[2 * i] * d), Math.round((itm.Q[2 * i + 1] - r + 2.5) * d), 1, 1).data]; }""", [VIEW, SYSID['8WA-Z6']])
        want = SECCOL[secclass(SEC[IDX[SYSID['8WA-Z6']]])]
        rgb = [int(want[1:3], 16), int(want[3:5], 16), int(want[5:7], 16)]
        if max(abs(px[q] - rgb[q]) for q in range(3)) > 24: out.append(f'zoomed in, 8WA-Z6\'s circle in its security colour {want}: {px}')
        spy = pg.evaluate("""(V) => { eval(V)(16); const c = itm.cv.getContext('2d'), log = [], s0 = c.stroke, f0 = c.fillText; let dash = [];
          const d0 = c.setLineDash; c.setLineDash = function(a){ dash = a; return d0.call(this, a); };
          c.stroke = function(){ log.push(['s', dash.join(','), this.strokeStyle]); return s0.apply(this, arguments); };
          c.fillText = function(t){ log.push(['t', t, this.fillStyle]); return f0.apply(this, arguments); };
          try{ itMapDraw(); }finally{ c.stroke = s0; c.fillText = f0; c.setLineDash = d0; } return [log, itm.regLabels]; }""", VIEW)
        log, regl = spy
        if not any(e[0] == 's' and e[1] in ('2,3', '3,4') and e[2] == '#3a4753' for e in log): out.append('no gate between two regions drawn dotted')
        if not any(e[0] == 's' and e[1] == '' and e[2] == '#26303b' for e in log): out.append('no gate inside a region drawn solid')
        mine = MAP['regions'][REG[IDX[HOME]]].upper()
        texts = [e for e in log if e[0] == 't' and e[1].replace(' ', '') in [r.upper().replace(' ', '') for r in MAP['regions']]]
        if not any(e[1].replace(' ', '') == mine.replace(' ', '') and e[2] == '#ffffff' for e in texts): out.append(f'your region\'s name {mine} not drawn in white {texts[:3]}')
        if any(e[1].replace(' ', '') != mine.replace(' ', '') and e[2] != '#8f9ba5' for e in texts) or len(texts) < 2: out.append(f'the other regions\' names not grey or missing {texts[:4]}')
    if 'filters' in parts:
        pg.evaluate("() => { itMapStartView(); itMapDraw(); }")
        F = pg.evaluate("""(ids) => { const g = itGraphGet(), r = {}; for(const f of ['sec', 'jumps', 'region', 'reports', 'kills']){ itMapFilterSet(f);
            r[f] = ids.map(id => { const i = g.at.get(id); return [itMapFcol(i), itMapDimmed(i)]; }); } itMapFilterSet('sec');
          return [r, [...itm.rep.keys()].map(i => g.ids[i]), [...itm.rep].filter(([i, x]) => x.kills).map(([i]) => g.ids[i])]; }""", ids)
        cols, reps, kills = F
        bad = [ids[k] for k in range(len(ids)) if cols['sec'][k][0] != SECCOL[secclass(SEC[k])]]
        if bad: out.append(f'Security status: {len(bad)} systems in the wrong colour ({bad[:3]})')
        bad = [ids[k] for k in range(len(ids)) if cols['jumps'][k][0] != (JUMPCOL[min(10, D0[ids[k]])] if ids[k] in D0 else '#4a535b')]
        if bad: out.append(f'Jumps from you: {len(bad)} systems in the wrong colour ({bad[:3]})')
        rc = {}
        for k in range(len(ids)): rc.setdefault(REG[k], set()).add(cols['region'][k][0])
        if any(len(v) != 1 for v in rc.values()): out.append('Region: a region in more than one colour')
        same = {(REG[IDX[a_]], REG[IDX[b_]]) for a_ in G for b_ in G[a_] if REG[IDX[a_]] != REG[IDX[b_]] and cols['region'][IDX[a_]][0] == cols['region'][IDX[b_]][0]}
        if same: out.append(f'Region: {len(same)} pairs of regions joined by a gate share a colour')
        dimr = {ids[k] for k in range(len(ids)) if cols['reports'][k][1]}
        if not reps or set(reps) & dimr or dimr != set(ids) - set(reps) - {HOME}: out.append(f'Intel reports: the dimmed systems are not exactly those without a report ({len(reps)} reports)')
        dimk = {ids[k] for k in range(len(ids)) if cols['kills'][k][1]}
        if dimk != set(ids) - set(kills) - {HOME}: out.append(f'Kills from Intel: the dimmed systems are not exactly those without kills ({len(kills)} with kills)')
        # a dot's pixel follows the pressed filter, and a press redraws once
        q = next(s for s, v in sorted(D0.items(), key=lambda x: x[1]) if 2 <= v <= 4 and s not in reps)
        DOT = """(id) => { const i = itGraphGet().at.get(id), d = window.devicePixelRatio || 1; return [...itm.cv.getContext('2d').getImageData(Math.round(itm.Q[2 * i] * d), Math.round(itm.Q[2 * i + 1] * d), 1, 1).data]; }"""
        d0 = pg.evaluate('itm.draws'); pg.click('#intelPanel [data-im-f="jumps"]'); pg.wait_for_timeout(150)
        d1, px = pg.evaluate('itm.draws'), pg.evaluate(DOT, q)
        want = JUMPCOL[D0[q]]; rgb = [int(want[1:3], 16), int(want[3:5], 16), int(want[5:7], 16)]
        if d1 - d0 != 1 or max(abs(px[k] - rgb[k]) for k in range(3)) > 30: out.append(f'Jumps from you pressed: {d1 - d0} draws (want 1), {SYSNAME[q]}\'s dot {px[:3]} (want {want})')
        pg.click('#intelPanel [data-im-f="sec"]'); pg.wait_for_timeout(150)
    if 'bar' in parts:
        bb = pg.evaluate("""() => { const box = itm.box.getBoundingClientRect(); return [...itm.box.querySelectorAll('[data-im-f]')].map(b => { const r = b.getBoundingClientRect();
          return [b.dataset.imF, b.getAttribute('aria-pressed'), Math.round(r.width), Math.round(r.height), r.left >= box.left && r.right <= box.right && r.top >= box.top && r.bottom <= box.bottom]; }); }""")
        if [x[0] for x in bb] != ['sec', 'jumps', 'region', 'reports', 'kills'] or [x[1] for x in bb] != ['true', 'false', 'false', 'false', 'false'] or any(x[2] != 32 or x[3] != 32 or not x[4] for x in bb):
            out.append(f'the bar at 1440 px: {bb}')
        pg.mouse.move(5, 5); pg.click('#intelPanel [data-im-f="region"]'); pg.mouse.move(5, 5); pg.wait_for_timeout(500)
        nm = pg.evaluate("() => { const n = itm.box.querySelector('.it-map-fn'); return [n.textContent, getComputedStyle(n).opacity, itm.box.querySelector('[data-im-f=\"region\"]').getAttribute('aria-pressed')]; }")
        pg.wait_for_timeout(4300)
        nm2 = pg.evaluate("() => getComputedStyle(itm.box.querySelector('.it-map-fn')).opacity")
        if not nm[0].startswith('Region') or nm[1] != '1' or nm[2] != 'true' or nm2 != '0': out.append(f'the name line: shown on a press {nm}, faded after {nm2}')
        pg.click('#intelPanel [data-im-f="sec"]'); pg.mouse.move(5, 5)
    if 'routes' in parts:
        pg.evaluate(VIEW, 16)
        far = next(s for s, v in sorted(D0.items(), key=lambda x: x[1]) if v == 12)
        pg.evaluate("(id) => { const i = itGraphGet().at.get(id); itm.view.tx = itm.W / 2 - itm.P[2 * i] * itm.view.k; itm.view.ty = itm.H / 3 - itm.P[2 * i + 1] * itm.view.k; itMapDraw(); }", far)
        POS = "(id) => { const i = itGraphGet().at.get(id), r = itm.cv.getBoundingClientRect(); return [r.left + itm.Q[2 * i], r.top + itm.Q[2 * i + 1]]; }"
        x, y = pg.evaluate(POS, far); pg.mouse.move(x, y); pg.wait_for_timeout(200)
        hv = pg.evaluate("(id) => [itm.hover >= 0 ? itGraphGet().ids[itm.hover] : 0, itMapRoute(itm.hover).length, itm.tip.innerText]", far)
        if hv[0] != far or hv[1] != 12 or 'reports aren’t shown here' not in hv[2]: out.append(f'a system 12 jumps out (past the reach) hovered: {hv[:2]} {hv[2][:120]!r}')
        pg.mouse.click(x, y); pg.wait_for_timeout(200)
        if pg.evaluate("(id) => itm.pinned.has(id)", far) is not True: out.append('a system past the reach pressed: its route not kept')
        pg.click('.it-map-clr'); pg.wait_for_timeout(150)
        pg.evaluate("(id) => { const i = itGraphGet().at.get(id); itm.view.tx = itm.W / 2 - itm.P[2 * i] * itm.view.k; itm.view.ty = itm.H / 3 - itm.P[2 * i + 1] * itm.view.k; itMapDraw(); }", NOGATE)
        x, y = pg.evaluate(POS, NOGATE); pg.mouse.move(x, y); pg.wait_for_timeout(200); pg.mouse.click(x, y); pg.wait_for_timeout(200)
        ng = pg.evaluate("(id) => [itm.tip.innerText, itm.pinned.size]", NOGATE)
        if 'no gate route to you' not in ng[0] or ng[1]: out.append(f'a system with no gate route: {ng}')
        pg.mouse.move(5, 5)
    if 'info' in parts or 'routes' in parts:
        it_ = pg.evaluate("() => [CARD_INFO.intel.join(' '), rsLabel(RS.mapReach), RS.mapReach.title()]")
        if "**{card:itmap}:** EVE's 2D map around you; hover one, or a row, for its route to you." not in it_[0] or 'The bottom bar picks the colours.' not in it_[0] or '(solo, 2–10, 11+)' not in it_[0]: out.append('the info text (intel) is not the owner\'s pick')
        if it_[1] != 'Map: within' or not it_[2].startswith('Reports and names show this many jumps from you'): out.append(f'the stepper: {it_[1:]}')
        tm = pg.evaluate("() => { it.set.mapReach = 30; itm.W = 0; itMapRefresh(true); const a = [itm.layoutMs, itm.vis.length]; itMapZoom(itm.W / 2, itm.H / 2, 1e-6); const t = performance.now(); for(let k = 0; k < 10; k++) itMapDraw(); a.push((performance.now() - t) / 10); it.set.mapReach = null; itm.W = 0; itMapRefresh(true); return a; }")
        print(f'TIMING: layout at a 30-jump reach ({tm[1]} systems) {tm[0]:.1f} ms; a redraw of the whole galaxy {tm[2]:.1f} ms')
        if tm[0] > 400 or tm[2] > 60: out.append(f'too slow: layout {tm[0]:.0f} ms (at most 400), a whole-galaxy redraw {tm[2]:.0f} ms (at most 60)')
    ctx.close()
    if 'near' in parts:
        for w in (905, 1000, 1200):
            ctx, pg = start(b, html, w, errs)
            r = pg.evaluate("""() => { const hs = []; for(const f of ['sec', 'jumps', 'region', 'reports', 'kills']){ itMapFilterSet(f); hs.push(Math.round(document.querySelector('#intelPanel .it-mapcol').getBoundingClientRect().height * 10) / 10); }
              itMapFilterSet('sec'); const nc = document.querySelector('#intelPanel .it-nearcol').getBoundingClientRect();
              const over = [...document.querySelectorAll('#itNearList > .it-nb')].filter(e => e.scrollWidth > e.clientWidth + 1 || e.getBoundingClientRect().right > nc.right + 1).length;
              return [hs, Math.round(nc.width), over, document.querySelectorAll('#itNearList > .it-nb').length, document.querySelector('#intelPanel .it-map-fl').getBoundingClientRect().height]; }""")
            hs, nw, over, rows, flh = r
            if len(set(hs)) != 1 or nw < 400 or over or rows < 2 or flh > 18: out.append(f'{w} px: the map column {hs} (one height for every filter), Near You {nw} px wide, {over} of {rows} rows wider than their box, the legend line {flh} px')
            ctx.close()
    if 'phone' in parts:
        ctx, pg = start(b, html, 390, errs, h=844, touch=True)
        ph = pg.evaluate("""() => { const c = itm.box.querySelector('.it-map-fcur'), r = c.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height), getComputedStyle(itm.box.querySelector('.it-map-fbtns')).display]; }""")
        if ph != [44, 44, 'none']: out.append(f'390 px: one 44 px button, the row hidden {ph}')
        pg.tap('#intelPanel .it-map-fcur'); pg.wait_for_timeout(150)
        op = pg.evaluate("() => [itm.box.querySelector('.it-map-fb').classList.contains('open'), [...itm.box.querySelectorAll('[data-im-f]')].map(b => { const r = b.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; })]")
        if not op[0] or op[1] != [[44, 44]] * 5: out.append(f'390 px: a tap opens the row of five 44 px buttons {op}')
        pg.tap('#intelPanel [data-im-f="jumps"]'); pg.wait_for_timeout(150)
        pk = pg.evaluate("() => [itm.filter, itm.box.querySelector('.it-map-fb').classList.contains('open')]")
        pg.tap('#intelPanel .it-map-fcur'); pg.wait_for_timeout(100); pg.keyboard.press('Escape'); pg.wait_for_timeout(100)
        es = pg.evaluate("() => [itm.box.querySelector('.it-map-fb').classList.contains('open'), document.activeElement === itm.box.querySelector('.it-map-fcur')]")
        pg.tap('#intelPanel .it-map-fcur'); pg.wait_for_timeout(100); pg.touchscreen.tap(20, 20); pg.wait_for_timeout(150)
        ou = pg.evaluate("() => itm.box.querySelector('.it-map-fb').classList.contains('open')")
        sw = pg.evaluate('document.documentElement.scrollWidth')
        if pk != ['jumps', False] or es != [False, True] or ou or sw > 390: out.append(f'390 px: a pick {pk}, Escape {es}, a press outside {ou} close it; page width {sw}')
        ctx.close()

MUTANTS = [
    ('separate x and y scales', "  const s = Math.min((W - 2 * pad) / Math.max(1, x1 - x0), (H - 2 * pad) / Math.max(1, y1 - y0)), qx = (W - (x1 - x0) * s) / 2, qy = (H - (y1 - y0) * s) / 2;\n  for(let i = 0; i < n; i++){ P[2 * i] = qx + (P[2 * i] - x0) * s; P[2 * i + 1] = qy + (P[2 * i + 1] - y0) * s; }",
     "  const s = (W - 2 * pad) / Math.max(1, x1 - x0), sy = (H - 2 * pad) / Math.max(1, y1 - y0), qx = pad, qy = pad;\n  for(let i = 0; i < n; i++){ P[2 * i] = qx + (P[2 * i] - x0) * s; P[2 * i + 1] = qy + (P[2 * i + 1] - y0) * sy; }", ('layout',)),
    ('a wider spread off CCP\'s place', "dmin = IT_MAP_GAP / k0,", "dmin = 4 * IT_MAP_GAP / k0,", ('layout',)),
    ('a filter that doesn\'t redraw', "  itMapFbarPaint(true); itMapLegend(); if(changed) itMapDraw();", "  itMapFbarPaint(true); itMapLegend();", ('filters',)),
    ('gates between regions solid', "c.setLineDash(k & 1 ? (big ? [3, 4] : [2, 3]) : []);", "c.setLineDash([]);", ('look',)),
    ('your region\'s name grey', "c.fillStyle = rg === mine ? '#ffffff' : '#8f9ba5';", "c.fillStyle = '#8f9ba5';", ('look',)),
    ('a long legend allowed to wrap', [(".it-map-leg .it-map-fl{flex:1 0 100%; display:flex; align-items:center; gap:6px; height:16px; overflow:hidden; white-space:nowrap; text-overflow:ellipsis;}",
     ".it-map-leg .it-map-fl{flex:1 0 100%; display:flex; flex-wrap:wrap; align-items:center; gap:6px;}"), ("10+ · grey: no gate route`", "10+ · grey: no gate route to you, by any stargate from where you are now in New Eden`")], ('near',)),
    ('Escape not closing the phone\'s row', "if(e.key === 'Escape' && itm.el.querySelector('.it-map-fb.open'))", "if(e.key === 'Esc' && itm.el.querySelector('.it-map-fb.open'))", ('phone',)),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    errs = []
    out = []; layout_cases(b, HTML, out, errs)
    check(not out, "the map like EVE's 2D map: the whole galaxy at CCP's places, one scale, 12 px apart in the reach, opening on you; zoom stages, dotted gates between regions, region names; the five filters and their bar; routes past the reach; Near You beside it unmoved by the filters at 905-1200 px; the phone's one button" + ''.join(f'\n      {o}' for o in out))
    tmp = tempfile.mkdtemp(prefix='maplook_mut_')
    for name_, a_, *rest in MUTANTS:
        b_, parts = (None, rest[0]) if isinstance(a_, list) else rest
        pairs = a_ if isinstance(a_, list) else [(a_, b_)]
        if any(PAGE.count(x) != 1 for x, _ in pairs): check(False, f'mutant "{name_}": its text is not in the page exactly once'); continue
        mut = PAGE
        for x, y in pairs: mut = mut.replace(x, y, 1)
        f = os.path.join(tmp, 'index.html'); open(f, 'w', encoding='utf-8').write(mut)
        mo, me = [], []
        try: layout_cases(b, f, mo, me, parts)
        except Exception as e: mo.append(f'error {str(e)[:80]}')
        check(bool(mo), f'mutant "{name_}" fails ({mo[:1]})')
    check(not errs, f'no page errors {errs[:3]}')
    b.close()
print(f"FAILURES: {NS['fails']}")
sys.exit(1 if NS['fails'] else 0)
