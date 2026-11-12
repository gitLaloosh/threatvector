"""The Intel map's Wormholes filter (build queue 040, wormhole mapping phase 1; Project doc roadmap/wormholes-filter-plan.md, mockup
Claude outputs/wormholes_filter_mockup.html).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/wormhole_filter_check.py [index.html]   -> 'FAILURES: N' (must be 0)

The owner: wormholes are reported as "wh", "wormhole", "drifter"; kept across reloads, "Default 24 h, a setting (Recommended)"; the
filter shows "All of them, anywhere"; on the other filters "Show newly reported as you would intel reports"; "add a wormhole badge to
intel as well."; a list to add or remove them by hand, reached from a button beside the Wormholes button, closed by its x or a press
outside; at the build review "Keywords (Recommended)" (never looked up as pilots), hand-added ones "Wormholes filter only (Recommended)",
"Drifter alone counts". Uses intel_check.py's made-up folder, mocks and names (you in 1DQ1-A); every pilot and line is made up. Checks:
  * taking lines: wh / wormhole / drifter with a system kept (drifter flagged, who and when), "whatever" and "whiskey" not; "Drifter"
    never sent to ESI as a pilot name; a kill or a line without a system changes nothing;
  * the store: a bad tvWormholes ignored; entries off the map, of the wrong form or past 48 h dropped on read; dscanIntel keeps its form;
  * the badge: Wormhole / Drifter WH on the Feed rows that say so, and on a Near You row with a wormhole report; none for a hand-added one;
  * the filter: kept systems in --it-wh (Drifter lighter), the rest dimmed, a kept one past "Map: within" bright (the pixel); the legend's
    filter line one line, the map's column as tall as on Security; the other filters: a live wormhole report (Intel's, inside "forget
    reports after" and "Map: within") ringed in --it-wh, an older or hand-added one not; Intel reports counts a live one as a report;
  * the map's key: a label's age or a kept one's end redraws once; nothing changed, no redraw;
  * the hover: "Wormhole · reported by X" (or "added by you"); no "reports aren't shown here" for a kept far one on the filter;
  * the setting: "keep wormhole reports for" beside "forget reports after", 24 h by default; 4 h drops the older ones, kept in
    tvWormholes across a reload;
  * the list: its button hidden on another filter, shown hovering Wormholes, gone after the pointer leaves, shown while the filter is
    on; opens a dialog with the shared close button, focus in the field; an unknown name refused; a system added by hand (Drifter);
    one removed, and the same line read again after a reload doesn't bring it back, a newer one does; closed by x (focus back on the
    list button), Escape, and a press outside;
  * the Intel example: its sandbox never reads or writes the user's wormholes;
  * 390 px: the list button in the opened row (44 px), the row closes as the list opens, x puts focus on the filter button; no sideways
    scroll;
  * the timings at the largest settings (LESSON #160): 500 kept over the galaxy, kept 48 h, the map's largest reach, zoomed out to the
    whole galaxy: a draw on Wormholes, the key, the list's paint (printed for the history doc; a draw under 400 ms);
  * mutants, each must fail: the filter not dimming; a removal not setting `gone`; kept ones faint past the reach; the example reading
    the store; the map's key without the wormholes; hand-added ones shown as live reports; the words not intel keywords;
  * no page errors.
v2026.11.12.3 fails (no Wormholes filter, no tvWormholes).
"""
import sys, os, re, json, time, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
_src = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
_src = _src[:_src.index('with sync_playwright() as p:')]
NS = {'__file__': os.path.join(HERE, 'intel_check.py'), '__name__': 'intel_check_prefix'}
exec(compile(_src, 'intel_check.py (first part)', 'exec'), NS)   # the made-up folder, mocks, names; its table checks run too
globals().update({k: v for k, v in NS.items() if not k.startswith('__') and k not in ('check', 'fails')})
from playwright.sync_api import sync_playwright
check = NS['check']
PAGE = open(HTML, encoding='utf-8').read()

HOME = SYSID['1DQ1-A']
D0 = bfs(HOME)
near = sorted((s for s, v in D0.items() if 1 <= v <= 4), key=lambda s: (D0[s], s))
A, B, C, X, Y, P1 = near[0], near[1], near[2], near[3], near[4], near[5]   # A: a pilot report with wh; B: "wh" alone; C: "drifter"; X, Y: no wormhole
FAR = max((s for s, v in D0.items() if v <= 60), key=lambda s: D0[s])   # far past the map's reach (a gate route, so a place on the map)
HAND = near[6]   # added by hand
OLD = near[7]    # kept 2 h ago by Intel: kept, not live
HOST = M.PILOTS[M.pick(98000003, 0)][0]
WHC, DRC = '#a98bd8', '#ff5fbf'   # 045: Drifter hot pink (044 D15)
H = 3600
T0 = time.time()

def seed(now):
    ms = lambda t: int(t * 1000)
    return {'v': 1, 'keepH': 24, 'gone': {}, 'rep': {
        str(FAR): {'id': FAR, 't': ms(now - 5 * H), 'who': 'Scout Alt', 'drifter': False, 'src': 'intel'},
        str(OLD): {'id': OLD, 't': ms(now - 2 * H), 'who': 'Gate Watcher', 'drifter': True, 'src': 'intel'},
        str(near[8]): {'id': near[8], 't': ms(now - 30 * H), 'who': 'Gate Watcher', 'drifter': False, 'src': 'intel'},   # kept in storage (< 48 h), not shown (> 24 h)
        str(near[9]): {'id': near[9], 't': ms(now - 60 * H), 'who': 'Gate Watcher', 'drifter': False, 'src': 'intel'},   # past 48 h: dropped on read
        '29999999': {'id': 29999999, 't': ms(now - H), 'who': 'x', 'drifter': False, 'src': 'intel'},                 # not on the map
        str(near[10]): {'id': near[10] + 1, 't': ms(now - H), 'who': 'x', 'drifter': False, 'src': 'intel'},          # id doesn't match its key
        str(near[11]): {'id': near[11], 't': 'soon', 'who': 'x', 'drifter': False, 'src': 'intel'}}}                   # no time

def start(b, html, w, errs, h=1000, touch=False, store=None, lines=True):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch, device_scale_factor=2 if touch else 1)
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); route(ctx)
    pg = ctx.new_page(); pg.goto('file://' + html)
    pg.evaluate("([s, w]) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({channels: ['region.intel'], me: 95000001, range: 3, sound: false, notify: false, forget: 15, hideFriendly: true}));"
                " if(w) localStorage.setItem('tvWormholes', JSON.stringify(w)); }", [SIDE, store if store is not None else seed(time.time())])
    pg.reload(); pg.wait_for_timeout(400)
    setup_logs(pg); pg.click('#tabBtnIntel'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg)
    if lines: write_lines(pg); tick(pg, 3200)
    if touch and pg.query_selector('[data-it-nv="map"]'): pg.click('[data-it-nv="map"]'); tick(pg, 600)
    pg.evaluate("() => document.querySelector('#intelPanel .it-map-box').scrollIntoView({block: 'center'})"); pg.wait_for_timeout(200)
    return ctx, pg

def write_lines(pg):
    W(pg, F_INTEL, line(T0, 'Scout Alt', f'{SYSNAME[A]} {HOST} sabre wh at planet 3') + line(T0 + 1, 'Scout Alt', f'{SYSNAME[B]} wh on the sun')
      + line(T0 + 2, 'Gate Watcher', f'{SYSNAME[C]} Drifter hole spotted') + line(T0 + 3, 'Gate Watcher', f'{SYSNAME[X]} whatever')
      + line(T0 + 4, 'Gate Watcher', f'{SYSNAME[Y]} whiskey') + line(T0 + 5, 'Gate Watcher', f'{SYSNAME[HAND]} {HOST} loki'))

def relaunch(pg):   # a reload: the made-up folder is written again (the same lines), Intel turned on, the lines read again as history
    pg.reload(); pg.wait_for_timeout(500)
    setup_logs(pg); write_lines(pg); pg.click('#tabBtnIntel'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300)
    if not pg.evaluate("it.on"): pg.click('#intelSwLabel')
    tick(pg, 3200)

STORE = "() => { try{ return JSON.parse(localStorage.getItem('tvWormholes')); }catch(e){ return 'bad'; } }"
PX = """([id, k, dy]) => { const i = itGraphGet().at.get(id); itm.view = {k, tx: itm.W / 2 - itm.P[2 * i] * k, ty: itm.H / 2 - itm.P[2 * i + 1] * k}; itMapDraw();
  const c = itm.cv.getContext('2d'), d = window.devicePixelRatio || 1, r = itm.stage ? Math.max(9, Math.min(15, itMapGatePx() * 0.2)) : 0;
  return [...c.getImageData(Math.round(itm.Q[2 * i] * d), Math.round((itm.Q[2 * i + 1] + (dy || 0) * r) * d), 1, 1).data]; }"""   # dy: below the circle's number, in radii (045: zoomed out a wormhole is a filled disc over its dot)
def near_col(px, hexc, tol=40): return max(abs(px[q] - int(hexc[1 + 2 * q:3 + 2 * q], 16)) for q in range(3)) <= tol

def cases(b, html, parts=('take', 'store', 'badge', 'filter', 'stand', 'key', 'tip', 'setting', 'list', 'example', 'phone', 'time')):
    out, errs = [], []
    IDS_ASKED.clear()
    ctx, pg = start(b, html, 1440, errs)
    if not pg.evaluate("typeof itWhStore === 'function' && IT_MAP_FILTERS.some(f => f.k === 'wh')"):
        out.append('no Wormholes filter or wormhole store on the page'); ctx.close(); return out, errs
    st = pg.evaluate(STORE)
    rep = (st or {}).get('rep', {}) if isinstance(st, dict) else {}
    if 'take' in parts:
        a, bb, c = rep.get(str(A)), rep.get(str(B)), rep.get(str(C))
        if not (a and bb and c): out.append(f'wh / drifter lines not kept: {SYSNAME[A]} {bool(a)}, {SYSNAME[B]} {bool(bb)}, {SYSNAME[C]} {bool(c)}')
        else:
            if a['drifter'] or bb['drifter'] or not c['drifter']: out.append(f"the Drifter flag: {a['drifter']}, {bb['drifter']}, {c['drifter']} (want False, False, True)")
            if bb['who'] != 'Scout Alt' or c['who'] != 'Gate Watcher' or bb['src'] != 'intel': out.append(f"who reported it: {bb['who']!r}, {c['who']!r}, src {bb['src']!r}")
            if abs(bb['t'] / 1000 - (T0 + 1)) > 2: out.append(f"the line's time: {bb['t']} (want {(T0 + 1) * 1000:.0f})")
        if str(X) in rep or str(Y) in rep: out.append('"whatever" or "whiskey" kept as a wormhole')
        if str(HAND) in rep: out.append('a line with no wormhole word kept')
        if 'drifter' in IDS_ASKED or 'wh' in IDS_ASKED: out.append(f'a wormhole word sent to ESI as a pilot name ({sorted(x for x in IDS_ASKED if x in ("drifter", "wh"))})')
    if 'store' in parts:
        if not isinstance(st, dict) or st.get('v') != 1 or st.get('keepH') != 24: out.append(f'tvWormholes: {str(st)[:120]}')
        else:
            for k, why in ((str(near[9]), 'past 48 h'), ('29999999', 'off the map'), (str(near[10]), 'the wrong id'), (str(near[11]), 'no time')):
                if k in rep: out.append(f'a stored entry {why} kept on read')
            if str(near[8]) not in rep or str(FAR) not in rep: out.append('kept entries inside 48 h lost on read')
        di = pg.evaluate("() => JSON.parse(localStorage.getItem('dscanIntel'))")
        if any('wh' in k.lower() or 'worm' in k.lower() for k in di): out.append(f'dscanIntel changed its form: {sorted(di)}')
    if 'badge' in parts:
        bd = pg.evaluate("""() => ({feed: [...document.querySelectorAll('#itFeedList > .it-fd')].map(r => [((r.querySelector('.it-sysb') || {}).textContent || '').trim(), [...r.querySelectorAll('.it-gtag.it-wh')].map(x => x.textContent + '|' + x.title)]),
          near: [...document.querySelectorAll('#itNearList > .it-nb')].map(r => [((r.querySelector('.it-sysb') || {}).textContent || '').trim(), [...r.querySelectorAll('.it-gtag.it-wh')].map(x => x.textContent)])})""")
        fb = {}
        for s, t in bd['feed']: fb[s] = fb.get(s) or t   # a system with several rows: the row that has the badge
        for s, want in ((A, 'Wormhole'), (B, 'Wormhole'), (C, 'Drifter WH')):
            got = fb.get(SYSNAME[s], [])
            if not got or not got[0].startswith(want + '|') or 'reported by' not in got[0]: out.append(f'the Feed row for {SYSNAME[s]}: badges {got} (want {want}, its title naming who)')
        for s in (X, Y, HAND):
            if fb.get(SYSNAME[s]): out.append(f'the Feed row for {SYSNAME[s]} has a wormhole badge {fb[SYSNAME[s]]}')
        nb = {s: t for s, t in bd['near']}
        if nb.get(SYSNAME[A]) != ['Wormhole']: out.append(f'Near You\'s row for {SYSNAME[A]}: {nb.get(SYSNAME[A])} (want one Wormhole badge)')
        if nb.get(SYSNAME[HAND]): out.append(f'Near You\'s row for {SYSNAME[HAND]} has a badge before anything was added: {nb[SYSNAME[HAND]]}')
    if 'filter' in parts:
        F = pg.evaluate("""([ids, far]) => { const g = itGraphGet(); itMapFilterSet('wh');
            const r = ids.map(id => { const i = g.at.get(id); return [itMapFcol(i), itMapDimmed(i)]; }); const leg = document.querySelector('.it-map-fl');
            const out = {r, leg: leg.textContent, legH: leg.getBoundingClientRect().height, col: document.querySelector('.it-mapcol') ? document.querySelector('.it-mapcol').getBoundingClientRect().height : 0, reach: itm.reach, dfar: itm.D[g.at.get(far)]};
            itMapFilterSet('sec'); const leg2 = document.querySelector('.it-map-fl'); out.legH2 = leg2.getBoundingClientRect().height; out.col2 = document.querySelector('.it-mapcol') ? document.querySelector('.it-mapcol').getBoundingClientRect().height : 0;
            out.live = [...itMapWh().live.keys()].map(i => g.ids[i]); itMapFilterSet('reports'); out.repDim = [ids[0], ids[1]].map(id => itMapDimmed(g.at.get(id))); itMapFilterSet('sec'); return out; }""",
            [[B, C, FAR, X, HAND], FAR])
        (cb, db), (cc, dc), (cf, df), (cx, dx), (ch, dh) = F['r']
        if cb.lower() != WHC or cc.lower() != DRC or cf.lower() != WHC: out.append(f'Wormholes: colours {cb}, {cc}, {cf} (want {WHC}, Drifter {DRC}, the far one {WHC})')
        if db or dc or df or not dx or not dh: out.append(f'Wormholes: dimmed {[db, dc, df, dx, dh]} (want the kept bright, the rest dimmed)')
        if 'Wormholes' not in F['leg'] or 'last 24 h' not in F['leg']: out.append(f"the legend's filter line: {F['leg']!r}")
        if abs(F['legH'] - F['legH2']) > 0.5 or abs(F['col'] - F['col2']) > 0.5: out.append(f"the legend line {F['legH']} vs {F['legH2']} px, the map's column {F['col']} vs {F['col2']} px (want the same on every filter)")
        if not (F['dfar'] > F['reach']): out.append(f"the far system {SYSNAME[FAR]} is {F['dfar']} jumps, inside the reach {F['reach']}: pick another")
        if sorted(F['live']) != sorted([A, B, C]): out.append(f"live wormhole reports on Security: {sorted(SYSNAME.get(i, i) for i in F['live'])} (want {SYSNAME[A]}, {SYSNAME[B]}, {SYSNAME[C]}; not {SYSNAME[OLD]} kept 2 h ago or the far one)")
        if F['repDim'] != [False, False]: out.append(f"Intel reports: the live wormhole reports dimmed {F['repDim']}")
        pg.evaluate("itMapFilterSet('wh')")
        px = pg.evaluate(PX, [FAR, 44 / pg.evaluate('itm.G'), 0.72])   # zoomed in (circles): the circle itself, below its number
        if not near_col(px, WHC): out.append(f'Wormholes: the far kept system {SYSNAME[FAR]} past "Map: within" drawn {px[:3]} (want bright {WHC})')
        pg.evaluate("() => { itMapFilterSet('sec'); itMapStartView(); itMapDraw(); }")
        spy = pg.evaluate("""() => { const c = itm.cv.getContext('2d'), s0 = c.stroke, log = [];
          c.stroke = function(){ log.push(String(this.strokeStyle).toLowerCase()); return s0.apply(this, arguments); }; try{ itMapDraw(); }finally{ c.stroke = s0; } return log; }""")
        n = spy.count(WHC) + spy.count(DRC)
        if n < 3: out.append(f'Security: {n} wormhole rings stroked (want one per live report in view, 3)')
    if 'stand' in parts:   # build queue 045: wormholes stand out on the Wormholes filter
        S = pg.evaluate("""([hand, a]) => { const g = itGraphGet(), danger = itMapCol('--danger', '#c65b4e').toLowerCase();
          const spy = () => { const c = itm.cv.getContext('2d'), s0 = c.stroke, log = []; c.stroke = function(){ log.push([String(this.strokeStyle).toLowerCase(), Math.round(this.globalAlpha * 100) / 100, this.shadowBlur]); return s0.apply(this, arguments); };
            try{ itMapDraw(); }finally{ c.stroke = s0; } return log.filter(x => x[0] === danger && x[1] !== 0.9 && x[1] !== 0.35); };   // rings, not routes
          const lab = () => itm.labels.map(l => g.ids[l[0]]);
          const over = () => { const L = itm.labels; for(let x = 0; x < L.length; x++) for(let y = x + 1; y < L.length; y++){ const p = L[x], q = L[y]; if(p[1] < q[3] && p[3] > q[1] && p[2] < q[4] && p[4] > q[2]) return [g.ids[p[0]], g.ids[q[0]]]; } return null; };
          itm.hover = -1; itm.rowHover = -1; itm.pinned.clear();   // no route shown (a route still names what it passes, faintly)
          itMapFilterSet('sec'); itMapStartView(); const sec = {rings: spy(), labels: lab(), pulse: itm.whp.children.length, chip: !itm.whn.hidden};
          itMapFilterSet('wh'); itMapStartView(); const wh = {rings: spy(), labels: lab(), over: over(), pulse: itm.whp.children.length, chip: !itm.whn.hidden, chipText: itm.whn.textContent,
            fresh: [...itm.wh.kept].filter(([i, w]) => Date.now() - w.t < 30 * 60000 && itm.Q[2 * i] > -30 && itm.Q[2 * i] < itm.W + 30 && itm.Q[2 * i + 1] > -30 && itm.Q[2 * i + 1] < itm.H + 30).length,
            layer: getComputedStyle(itm.whp).pointerEvents, anim: itm.whp.firstElementChild ? getComputedStyle(itm.whp.firstElementChild).animationName : '', kept: itm.wh.kept.size};
          const D = itm.D, nearest = [...itm.wh.kept.keys()].sort((x, y) => ((D[x] >= 0 ? D[x] : 1e4) - (D[y] >= 0 ? D[y] : 1e4)) || (itm.wh.kept.get(y).t - itm.wh.kept.get(x).t))[0];
          itm.whn.click(); const c1 = itm.whn.textContent, cx = itm.Q[2 * nearest] - itm.W / 2, cy = itm.Q[2 * nearest + 1] - itm.H / 2;
          itMapFilterSet('sec'); itMapFilterSet('wh'); const again = itm.whn.textContent;
          // crowded: 40 more kept wormholes inside the reach, all fresh: labels never overlap, and only wormholes and you are named
          const st = itWhStore(), keepRep = JSON.parse(JSON.stringify(st.rep)); let k = 0;
          for(const id of g.ids){ const i = g.at.get(id); if(D[i] > 0 && D[i] <= Math.min(6, itm.reach) && !st.rep[id] && k < 40){ st.rep[id] = {id, t: Date.now() - k * 60000, who: 'Mk Scout', drifter: k % 4 === 0, src: 'intel'}; k++; } }
          itMapStartView(); itMapDraw(); const crowd = {over: over(), named: lab().filter(id => !st.rep[id] && id !== g.ids[itm.home]), n: itm.labels.length};
          for(const w of Object.values(st.rep)) w.t = Math.min(w.t, Date.now() - 40 * 60000);   // every one at least 40 minutes old: no pulse
          itMapDraw(); const old40 = [...itm.whp.children].length;
          st.rep = keepRep; itMapStartView(); itMapDraw();
          return {sec, wh, c1, cx: Math.round(cx), cy: Math.round(cy), nearest: g.ids[nearest], again, crowd, old40, hand, a}; }""", [HAND, A])
        sec, wh = S['sec'], S['wh']
        if any(a != 0.95 for _, a, _b in sec['rings']) or not sec['rings']: out.append(f"Security: report rings at {sorted(set(a for _, a, _b in sec['rings']))} (want 0.95, as before)")
        if HAND not in sec['labels'] or sec['pulse'] or sec['chip']: out.append(f"Security: {SYSNAME[HAND]} labelled {HAND in sec['labels']}, pulse rings {sec['pulse']}, chip {sec['chip']} (want labelled, none, no chip)")
        alphas = sorted(set(a for _, a, _b in wh['rings']))
        if 0.2 not in alphas or 0.95 not in alphas or any(b > 0 for _, a, b in wh['rings'] if a == 0.2): out.append(f"Wormholes: report rings at {alphas} (want the other reports at 0.2 with no glow, {SYSNAME[A]}'s (a wormhole there) at 0.95)")
        if HAND in wh['labels'] or A not in wh['labels']: out.append(f"Wormholes: labels {[SYSNAME.get(x, x) for x in wh['labels']]} (want none for {SYSNAME[HAND]}, a report with no wormhole; {SYSNAME[A]} named)")
        if wh['over']: out.append(f"Wormholes: two labels overlap {wh['over']}")
        if wh['pulse'] != wh['fresh'] or not wh['fresh'] or wh['layer'] != 'none' or wh['anim'] != 'it-whp': out.append(f"Wormholes: {wh['pulse']} pulse rings for {wh['fresh']} fresh holes in view, layer pointer-events {wh['layer']!r}, animation {wh['anim']!r}")
        if not wh['chip'] or wh['chipText'] != f"{wh['kept']} wormholes ›": out.append(f"the chip: shown {wh['chip']}, {wh['chipText']!r} (want '{wh['kept']} wormholes ›')")
        if not S['c1'].startswith(f"1/{wh['kept']} · {SYSNAME[S['nearest']]}") or abs(S['cx']) > 1 or abs(S['cy']) > 1: out.append(f"the chip pressed: {S['c1']!r}, the view off the nearest ({SYSNAME[S['nearest']]}) by {S['cx']}, {S['cy']} px")
        if S['again'] != f"{wh['kept']} wormholes ›": out.append(f"the chip after the filter was chosen again: {S['again']!r} (want the count again)")
        if S['crowd']['over'] or S['crowd']['named']: out.append(f"crowded ({S['crowd']['n']} labels): overlap {S['crowd']['over']}, named without a wormhole {S['crowd']['named'][:4]}")
        if S['old40']: out.append(f"{S['old40']} pulse rings on holes 40 minutes old (want none)")
        pg.emulate_media(reduced_motion='reduce'); pg.evaluate("() => { itm.whpKey = null; itMapDraw(); }")
        rm = pg.evaluate("[itm.whp.children.length, getComputedStyle(itm.whp).display]")
        pg.emulate_media(reduced_motion='no-preference'); pg.evaluate("() => { itm.whpKey = null; itMapFilterSet('sec'); itMapDraw(); }")
        if rm[0]: out.append(f'reduced motion: {rm[0]} pulse rings (want none)')
    if 'key' in parts:
        k = pg.evaluate("""(id) => { itMapRefresh(true); const d0 = itm.draws; itMapRefresh(); const d1 = itm.draws; const st = itWhStore(); st.rep[id].t -= 5 * 60000; itMapRefresh(); const d2 = itm.draws; itMapRefresh(); const d3 = itm.draws;
          st.rep[id].t -= 30 * 3600e3; itMapRefresh(); const d4 = itm.draws; return [d1 - d0, d2 - d1, d3 - d2, d4 - d3]; }""", B)
        if k != [0, 1, 0, 1]: out.append(f'the map\'s key: redraws {k} (want none unchanged, one when a label ages, none again, one when it ends)')
        pg.evaluate("(id) => { const st = itWhStore(); st.rep[id].t += 30 * 3600e3 + 5 * 60000; itMapRefresh(true); }", B)
    if 'tip' in parts:
        t = pg.evaluate("""([b, far]) => { const g = itGraphGet(); itMapFilterSet('sec'); itMapDraw(); itMapTip(g.at.get(b), 50, 50); const t1 = itm.tip.textContent;
          itMapFilterSet('wh'); itMapTip(g.at.get(far), 50, 50); const t2 = itm.tip.textContent; itMapTip(-1); itMapFilterSet('sec'); return [t1, t2]; }""", [B, FAR])
        if 'Wormhole' not in t[0] or 'reported by Scout Alt' not in t[0] or 'nothing reported' in t[0]: out.append(f'the hover on {SYSNAME[B]}: {t[0][:160]!r}')
        if 'Wormhole' not in t[1] or 'aren’t shown here' in t[1]: out.append(f'the hover on the far kept one, Wormholes on: {t[1][:160]!r}')
    if 'list' in parts:
        pg.evaluate("itMapFilterSet('sec')"); pg.wait_for_timeout(900)   # past the 0.6 s it stays after Wormholes was on
        vis = lambda: pg.evaluate("getComputedStyle(document.querySelector('[data-it-whl]')).visibility")
        v0 = vis(); pg.hover('[data-im-f="wh"]'); pg.wait_for_timeout(300); v1 = vis(); pg.mouse.move(5, 5); pg.wait_for_timeout(1000); v2 = vis()
        if [v0, v1, v2] != ['hidden', 'visible', 'hidden']: out.append(f'the list button: {v0} on Security, {v1} hovering Wormholes, {v2} after the pointer leaves')
        pg.click('[data-im-f="wh"]'); pg.wait_for_timeout(300)
        if vis() != 'visible': out.append('the list button hidden while Wormholes is on')
        pg.click('[data-it-whl]'); pg.wait_for_timeout(300)
        L = pg.evaluate("() => { const p = document.querySelector('.it-whp'); return p && [p.hidden, p.getAttribute('role'), !!p.querySelector('button.x-close'), document.activeElement && document.activeElement.name, p.querySelectorAll('.it-whp-r').length]; }")
        if not L or L[0] or L[1] != 'dialog' or not L[2] or L[3] != 'sys': out.append(f'the list: {L} (want open, a dialog with the shared close button, focus in the field)')
        pg.fill('.it-whp-add input[name=sys]', 'Nowhere Special'); pg.press('.it-whp-add input[name=sys]', 'Enter'); pg.wait_for_timeout(200)
        m = pg.inner_text('.it-whp-msg')
        if 'isn’t a system' not in m or pg.get_attribute('.it-whp-add input[name=sys]', 'aria-invalid') != 'true': out.append(f'an unknown name: {m!r}')
        pg.fill('.it-whp-add input[name=sys]', SYSNAME[HAND].lower()); pg.check('.it-whp-add input[name=dr]'); pg.click('.it-whp-add button[type=submit]'); pg.wait_for_timeout(300)
        h = (pg.evaluate(STORE) or {}).get('rep', {}).get(str(HAND))
        if not h or h.get('src') != 'you' or not h.get('drifter'): out.append(f'{SYSNAME[HAND]} added by hand (Drifter): {h}')
        pg.evaluate("itMapRefresh(true)")
        hl = pg.evaluate("(id) => [itMapWh().live.has(itGraphGet().at.get(id)), [...document.querySelectorAll('#itNearList > .it-nb')].filter(r => r.dataset.itSys == id).map(r => r.querySelectorAll('.it-gtag.it-wh').length)]", HAND)
        if hl[0] or any(hl[1]): out.append(f'a hand-added wormhole shown as a live report {hl} (want the Wormholes filter and the list only)')
        pg.click(f'[data-it-whrm="{B}"]'); pg.wait_for_timeout(300)
        s2 = pg.evaluate(STORE)
        if str(B) in s2['rep'] or str(B) not in s2.get('gone', {}): out.append(f'{SYSNAME[B]} removed: still kept {str(B) in s2["rep"]}, gone {s2.get("gone")}')
        if pg.evaluate("document.activeElement && document.activeElement.matches('[data-it-whrm], input[name=sys]')") is not True: out.append('focus lost after Remove')
        pg.click('.it-whp .x-close'); pg.wait_for_timeout(200)
        if pg.evaluate("[document.querySelector('.it-whp').hidden, document.activeElement && document.activeElement.matches('[data-it-whl]')]") != [True, True]: out.append('× doesn\'t close the list with focus back on the list button')
        pg.click('[data-it-whl]'); pg.wait_for_timeout(200); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        if not pg.evaluate("document.querySelector('.it-whp').hidden"): out.append('Escape doesn\'t close the list')
        pg.click('[data-it-whl]'); pg.wait_for_timeout(200); pg.mouse.click(5, 300); pg.wait_for_timeout(200)
        if not pg.evaluate("document.querySelector('.it-whp').hidden"): out.append('a press outside doesn\'t close the list')
        # the same line read again after a reload doesn't bring it back; a newer one does
        relaunch(pg)
        s3 = pg.evaluate(STORE)
        if str(B) in s3['rep']: out.append(f'{SYSNAME[B]} came back from the same line after a reload')
        W(pg, F_INTEL, line(time.time(), 'Scout Alt', f'{SYSNAME[B]} wh still there')); tick(pg, 3200)
        if str(B) not in pg.evaluate(STORE)['rep']: out.append(f'a newer line about {SYSNAME[B]} doesn\'t bring it back')
    if 'setting' in parts:
        pg.click('#intelPanel .it-gear'); pg.wait_for_timeout(600)
        S = pg.evaluate("() => { const s = document.querySelector('select[data-it-whkeep]'), f = document.querySelector('select[data-it-set=\"forget\"]'); return s && [s.value, [...s.options].map(o => o.value).join(','), f.closest('label').nextElementSibling === s.closest('label')]; }")
        if not S or S[0] != '24' or S[1] != '1,2,4,8,12,24,48' or not S[2]: out.append(f'"keep wormhole reports for": {S} (want 24 of 1..48, beside "forget reports after")')
        else:
            pg.select_option('select[data-it-whkeep]', '4'); pg.wait_for_timeout(400)
            kh = pg.evaluate("[itWhStore().keepH, JSON.parse(localStorage.getItem('tvWormholes')).keepH, itMapWh().kept.has(itGraphGet().at.get(%d)), itMapWh().kept.has(itGraphGet().at.get(%d))]" % (FAR, OLD))
            if kh != [4, 4, False, True]: out.append(f'keep 4 h: {kh} (want 4 saved, the 5 h one gone, the 2 h one kept)')
            relaunch(pg)
            if pg.evaluate("itWhStore().keepH") != 4: out.append('keep 4 h not kept across a reload')
    if 'example' in parts:
        e = pg.evaluate("""() => { const before = localStorage.getItem('tvWormholes'), mine = itWhStore();
          const inside = itExSandbox(() => { const n = Object.keys(itWhStore().rep).length; itWhTake({t: Date.now(), who: 'x', p: {kw: new Set(['wormhole']), sys: [{id: itGraphGet().ids[0]}]}}); return [n, itWhStore() !== mine]; });
          return [inside, localStorage.getItem('tvWormholes') === before, itWhStore() === mine]; }""")
        if e != [[0, True], True, True]: out.append(f'the Intel example\'s sandbox and the wormholes: {e} (want an empty store inside, nothing written, yours back after)')
    if 'time' in parts:
        T = pg.evaluate("""() => { const g = itGraphGet(), st = itWhStore(), now = Date.now(); st.keepH = 48; st.rep = {};
          for(let k = 0; k < 500; k++){ const id = g.ids[Math.floor(k * g.ids.length / 500)]; st.rep[id] = {id, t: now - k * 300000, who: 'Mk Scout', drifter: k % 5 === 0, src: k % 7 ? 'intel' : 'you'}; }
          it.set.mapReach = IT_MAP_MAX; itMapRefresh(true); itMapFilterSet('wh'); itm.view = {k: 1, tx: 0, ty: 0};
          const t = (f, n = 5) => { const a = performance.now(); for(let q = 0; q < n; q++) f(); return (performance.now() - a) / n; };
          const draw = t(() => itMapDraw()), key = t(() => itMapKey(), 20);
          itWhListOpen(true); const paint = t(() => { itWhL.html = null; itWhListPaint(true); }, 5); itWhListOpen(false, false);
          return {draw, key, paint, kept: itm.wh.kept.size, rows: document.querySelectorAll('.it-whp-r').length, reach: itm.reach}; }""")
        print(f"   timings at the largest settings (500 kept, 48 h, reach {T['reach']}, the whole galaxy): a draw on Wormholes {T['draw']:.1f} ms, the key {T['key']:.2f} ms, the list's paint ({T['rows']} rows) {T['paint']:.1f} ms")
        if T['kept'] != 500 or T['draw'] > 400: out.append(f'the largest settings: {T}')
    ctx.close()
    if 'phone' in parts:
        ctx, pg = start(b, html, 390, errs, h=844, touch=True)
        pg.click('.it-map-fcur'); pg.wait_for_timeout(300)
        P = pg.evaluate("() => { const l = document.querySelector('[data-it-whl]'), r = l.getBoundingClientRect(), row = document.querySelector('.it-map-fbtns').getBoundingClientRect(), box = itm.box.getBoundingClientRect();"
                        " const inBox = [...itm.box.querySelectorAll('[data-im-f], [data-it-whl]')].every(b => { const q = b.getBoundingClientRect(); return q.left >= box.left - 0.5 && q.right <= box.right + 0.5; });"
                        " return [getComputedStyle(l).visibility, Math.round(r.width), Math.round(r.height), r.right <= row.right + 0.5 && r.left >= row.left - 0.5, inBox]; }")
        if P != ['visible', 44, 44, True, True]: out.append(f'390 px: the list button {P} (want visible, 44 px, inside the opened row, every button inside the map box)')
        pg.click('[data-it-whl]'); pg.wait_for_timeout(300)
        if pg.evaluate("[document.querySelector('.it-whp').hidden, document.querySelector('.it-map-fb').classList.contains('open')]") != [False, False]: out.append('390 px: the list didn\'t open, or the filter row stayed open')
        if not pg.evaluate("document.scrollingElement.scrollWidth <= innerWidth + 1"): out.append('390 px: sideways scroll with the list open')
        pg.click('.it-whp .x-close'); pg.wait_for_timeout(200)
        if not pg.evaluate("document.activeElement && document.activeElement.matches('.it-map-fcur')"): out.append('390 px: × doesn\'t put focus back on the filter button')
        pg.evaluate("itMapFilterSet('wh')"); pg.wait_for_timeout(200)
        CH = pg.evaluate("""() => { const b = itm.whn, r = b.getBoundingClientRect(), shown = getComputedStyle(b).display !== 'none'; itMapFbarOpen(true);
          const hid = getComputedStyle(b).display === 'none'; itMapFbarOpen(false); return [shown, Math.round(r.height), hid]; }""")
        if CH != [True, 44, True]: out.append(f'390 px: the chip {CH} (want shown, 44 px tall, hidden while the filter row is open)')
        ctx.close()
    return out, errs

MUTANTS = [
    ('the filter not dimming', "  if(itm.filter === 'wh') return !(itm.wh && itm.wh.kept.has(i));   // build queue 040", "  if(itm.filter === 'wh') return false;", ('filter',)),
    ('a removal not setting gone', "if(w){ st.gone[id] = Math.max(w.t, st.gone[id] || 0); delete st.rep[id];", "if(w){ delete st.rep[id];", ('list',)),
    ('kept ones faint past the reach', "whF && itm.wh.kept.has(i) ? 1 : !on(i)", "!on(i)", ('filter',)),
    ('the example reading the store', "  itWhSt = itWhBlank(); itWhAside = true;", "", ('example',)),
    ('the map\'s key without the wormholes', "|${itMapWhKey(itMapWh())}`;", "`;", ('key',)),
    ('hand-added ones shown as live reports', "if(w.src === 'intel' && w.t >= fresh", "if(w.t >= fresh", ('list',)),
    ('045: reports faded on every filter', "      const fade = whF && !itm.wh.kept.has(i);", "      const fade = !itm.wh.kept.has(i);", ('stand',)),
    ('045: wormhole labels forced over others', "(live && !whS) || i === focus); if(whS", "true); if(whS", ('stand',)),
    ('045: a hole 40 minutes old pulses', "IT_MAP_WH_FRESH_MS = 30 * 60000", "IT_MAP_WH_FRESH_MS = 50 * 60000", ('stand',)),
    ('045: the chip on another filter', "itm.filter === 'wh' && !itPtLive() ? itMapWhChipList() : []", "!itPtLive() ? itMapWhChipList() : []", ('stand',)),
    ('the words not intel keywords', "  wh: 'wormhole', wormhole: 'wormhole', wormholes: 'wormhole', drifter: 'drifter', drifters: 'drifter'};", "};", ('take',)),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, 'the Wormholes filter, its store, badges, setting and list')
    check(not errs, f'no page errors {errs[:3]}')
    for name, old, new, parts in MUTANTS:
        if PAGE.count(old) != 1: check(False, f'mutant "{name}": its line isn\'t in the page once'); continue
        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f:
            f.write(PAGE.replace(old, new)); mp = f.name
        try:
            mo, me = cases(b, mp, parts)
            check(bool(mo) or bool(me), f'mutant "{name}" fails ({(mo or me or ["nothing"])[0][:90]})')
        finally: os.unlink(mp)
    b.close()
print('FAILURES:', NS['fails'])
sys.exit(1 if NS['fails'] else 0)
