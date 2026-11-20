"""The Intel map's stacked filters (build queue 058; Project doc roadmap/intel-map-stack-plan.md, mockup Claude outputs/stacked_filters_mockup.html).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/intel_map_stack_check.py [index.html]   -> 'FAILURES: N' (must be 0)

The owner: "i need the ability to have filters from some existing types work together. example: i want to see systems with threat detection
array level 3 where system security level is N"; his answers Q1-Q21 (the plan's section 2). Uses intel_check.py's made-up folder, mocks and
names (you in 1DQ1-A); every pilot, line, wormhole and sov list is made up (the sov list is written from the map's own systems at the start).
The drawing is read from the map's own canvas calls (every arc's place, radius, strength and colour, recorded during one draw), not pixels.
Checks, at 1440 px and 390 px:
  * the column: Colour (Security, Jumps, Region) · Only (Security range, Within N jumps, Intel reports, Kills, Wormholes, Sov upgrades) ·
    View (Paths to you), a line between groups; nothing dims and no "Only" line with no Only filter on; no wormholes chip;
  * soft colour (Q15): with nothing on every system but yours softened zoomed out and a tinted disc zoomed in; a match keeps its colour;
  * the owner's example (Security range -0.5 to -0.3 + Sov upgrades Threat Detection level 3): the matches exactly the systems in that range
    (the number the map shows) with a Threat Detection Array at level 3, some level-3 systems outside it; a match bright anywhere (past
    "Map: within" too) and bigger (zoomed out 1.6 px, zoomed in a quarter), the rest dim, your system never; the legend's second line
    (count first, whole); the chip "N match ›" stepping nearest first; the pressed buttons; the phone button's count;
  * colour: a colour switch keeps the stack; the colour that is on, pressed again: plain grey, no number, the legend says so; Kills never
    colours a dot (Q3); rings at full strength on a system that doesn't match (Q7); the alert glow half today's zoomed out, today's zoomed in;
  * Paths to you: the stack and the chip step aside, back keeps colour and stack;
  * the panels: Security range's settings open the first time it is switched on, inside the map (right of the column on a wide window), the
    shared close button, 0.1 steps, quick Null, Escape; a filter that is off keeps its setting, shuts its panel and shows no settings button
    (on hover neither); Sov off shuts its panel; Sov's Level boxes: one ticked narrows, 1 + 2 kept as [1, 2] and named in the legend, none =
    any;
  * Wormholes (Q21): alone, every kept hole bold with the fresh ones pulsing and the chip counting them; with Within 3 jumps, the holes that
    match bold, a live one past 3 thin, the rest unmarked;
  * the security shown (the owner at the review): a system stored at 0.45 and low-sec shows 0.4, in the 0.4 colour, outside quick High;
  * stored: tvMapStack across a reload, a bad value read as the defaults, tvSov keeps its form; the Intel example never reads or writes it;
  * no sideways scroll, no page errors;
  * build queue 060: each settings button (Security range, Within N jumps) pressed with its filter off opens its settings, the
    filter still off (the owner's bug: it did nothing);
  * mutants, each must fail (see MUTANTS).
v2026.11.16.2 fails (one filter at a time, no tvMapStack).
"""
import sys, os, re, json, time, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
_src = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
_src = _src[:_src.index('with sync_playwright() as p:')]
NS = {'__file__': os.path.join(HERE, 'intel_check.py'), '__name__': 'intel_check_prefix'}
exec(compile(_src, 'intel_check.py (first part)', 'exec'), NS)   # the made-up folder, mocks, names
globals().update({k: v for k, v in NS.items() if not k.startswith('__') and k not in ('check', 'fails')})
from playwright.sync_api import sync_playwright
check = NS['check']
PAGE = open(HTML, encoding='utf-8').read()

HOME = SYSID['1DQ1-A']
D0 = bfs(HOME)
near = sorted((s for s, v in D0.items() if 1 <= v <= 4), key=lambda s: (D0[s], s))
HOST = M.PILOTS[M.pick(98000003, 0)][0]
H, MIN = 3600, 60
T0 = time.time()
by_d = {}
for s_, v in sorted(D0.items(), key=lambda kv: (kv[1], kv[0])): by_d.setdefault(v, []).append(s_)
def at(d, k=0): return by_d[d][k % len(by_d[d])]
# the wormholes (made up): fresh Intel holes at 1, 2 and 5 jumps (live inside "Map: within"), kept older ones at 2, 3 and 9, one far
WH = [(at(1, 3), 5 * MIN, 'intel', False), (at(2, 4), 8 * MIN, 'intel', True), (at(5, 2), 6 * MIN, 'intel', False),
      (at(2, 6), 2 * H, 'intel', False), (at(3, 5), 3 * H, 'you', False), (at(9, 1), 5 * H, 'intel', False), (at(20, 0), 9 * H, 'intel', True)]
def wh_seed(now):
    return {'v': 1, 'keepH': 24, 'gone': {}, 'rep': {str(i): {'id': i, 't': int((now - age) * 1000), 'who': '' if src == 'you' else 'Scout Alt', 'drifter': dr, 'src': src} for i, age, src, dr in WH}}

# every stepper's number shown whole in the settings panel, at its widest ("-1.0"): text width against the box (the owner's hand test, 2026-11-16: "0.:" and "-0")
FITS = """() => { const out = []; for(const k of ['mapSecLo', 'mapSecHi', 'mapNear']){ const inp = document.querySelector(`.it-mpp [data-rs=${k}] .rs-v`); if(!inp) continue;
  const v = inp.value; inp.value = k === 'mapNear' ? '30' : '-1.0'; const c = document.createElement('canvas').getContext('2d'), cs = getComputedStyle(inp); c.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
  const need = c.measureText(inp.value).width + parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight); if(inp.offsetParent && need > inp.clientWidth + 0.5) out.push([k, inp.value, Math.round(need), inp.clientWidth]); inp.value = v; } return out; }"""
def start(b, html, w, errs, h=1000, touch=False, stack=None):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch, device_scale_factor=2 if touch else 1)
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); route(ctx)
    pg = ctx.new_page(); pg.goto('file://' + html)
    pg.evaluate("([s, w, st]) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({nearShown: false, channels: ['region.intel'], me: 95000001, range: 3, sound: false, notify: false, forget: 15, hideFriendly: true}));"
                " localStorage.setItem('tvWormholes', JSON.stringify(w)); if(st !== null) localStorage.setItem('tvMapStack', st); }", [SIDE, wh_seed(time.time()), stack])
    pg.reload(); pg.wait_for_timeout(400)
    setup_logs(pg); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg)
    W(pg, F_INTEL, line(T0, 'Scout Alt', f'{SYSNAME[near[0]]} {HOST} sabre') + line(T0 + 1, 'Scout Alt', f'{SYSNAME[near[2]]} 3 red') + line(T0 + 2, 'Gate Watcher', f'{SYSNAME[near[4]]} 2 neut'))
    tick(pg, 3200)
    pg.evaluate(SOV_SEED); pg.wait_for_timeout(200)
    pg.evaluate("() => document.querySelector('#intelPanel .it-map-box').scrollIntoView({block: 'center'})"); pg.wait_for_timeout(200)
    pg.evaluate(REC)
    return ctx, pg

# a made-up sov list from the map's own systems, 1 to 35 jumps out: three in four have a Threat Detection Array at a level 1-3, some an
# Exploration Detector; written before anything reads tvSov in the visit's map (053's reader)
SOV_SEED = """() => {
  const g = itGraphGet(), T = itMapTable(), D = itm.D, rows = [], UP = [['Major Threat Detection Array 3', 'Exploration Detector 1'], ['Major Threat Detection Array 2'],
    ['Minor Threat Detection Array 3', 'Tritanium Prospecting Array 2'], ['Major Threat Detection Array 1'], ['Exploration Detector 2']];
  let k = 0; for(let i = 0; i < T.n; i++){ if(i === itm.home || D[i] < 1 || D[i] > 35 || i % 3) continue; rows.push(`${itSysName(g.ids[i])} <- ${UP[k % UP.length].join(', ')}`); k++; }
  localStorage.setItem('tvSov', JSON.stringify({v: 1, lists: [{id: 'chk1', kind: '', text: rows.join('\\n'), at: Date.now() - 86400e3}], pick: []}));
  sovSt = null; sovIx = null; itMapRefresh(true); return rows.length; }"""
# every arc the map's canvas draws in one itMapDraw: [x, y, r, alpha, fill, stroke] (CSS px, as itm.Q)
REC = """() => { const c = itm.cv.getContext('2d'); if(c.__rec) return; const arc = c.arc; c.__rec = [];
  c.arc = function(x, y, r, a0, a1){ if(c.__on) c.__rec.push([x, y, r, c.globalAlpha, String(c.fillStyle), String(c.strokeStyle)]); return arc.apply(this, arguments); }; }"""
ARCS = """(sel) => { const c = itm.cv.getContext('2d'); c.__rec = []; c.__on = true; itMapDraw(); c.__on = false;
  const out = {}; for(const i of sel){ const x = itm.Q[2 * i], y = itm.Q[2 * i + 1]; out[i] = c.__rec.filter(a => Math.abs(a[0] - x) < 0.01 && Math.abs(a[1] - y) < 0.01); } return {arcs: out, all: c.__rec.length}; }"""
ZOOM_OUT = "() => { itMapStartView(); itMapDraw(); return [itMapGatePx(), itm.stage]; }"
ZOOM_IN = "() => { itMapCenter(false); for(let k = 0; k < 14 && itMapGatePx() < 44; k++) itMapZoom(itm.W / 2, itm.H / 2, 1.4); itMapDraw(); return [itMapGatePx(), itm.stage]; }"
EXAMPLE = """() => { const s = itMapSt(); for(const k of IT_MAP_ONLY) s.only[k] = false; Object.assign(s, {colour: 'sec', view: 'map', secr: {lo: -5, hi: -3}, sovLv: [3]}); s.only.secr = true; s.only.sov = true; s.seen.secr = true;
  const st = sovStore(); st.pick = ['Major Threat Detection Array', 'Minor Threat Detection Array']; sovSave(); sovIx = null; itMapStackSave(); itMapFbarPaint(false); itMapRefresh(true); itMapLegend(); return itMapMatch() ? itMapMatch().list.length : -1; }"""
WANT_EXAMPLE = """() => { const T = itMapTable(), mt = itMapMatch(), ix = sovIndex(), bad = []; let n = 0, tda = 0, inR = 0, far = 0;
  for(let i = 0; i < T.n; i++){ if(i === itm.home) continue; const v = Number(itMapSecText(i)), e = ix.at.get(i);
    const t3 = !!e && [...e].some(([k, l]) => (k === 'Major Threat Detection Array' || k === 'Minor Threat Detection Array') && l === 3), want = v >= -0.5 - 1e-9 && v <= -0.3 + 1e-9 && t3;
    if(want !== !!mt.m[i]) bad.push(i); if(mt.m[i]){ n++; if(itm.D[i] > itm.reach) far++; } if(t3) tda++; if(t3 && want) inR++; }
  return {n, tda, inR, bad: bad.length, list: mt.list.length, far}; }"""
def pb_click(pg, k, out):   # 057: a settings button shows on hover; one that doesn't is a failure here, not a 30 s stall
    pg.hover(f'.it-map-fbtns [data-im-f="{k}"]')
    try: pg.click(f'[data-it-mpn="{k}"]', timeout=3000)
    except Exception: out.append(f'the {k} settings button can\'t be pressed while its filter is hovered')
VIS_PB = "(k) => { const f = document.querySelector(`.it-map-fbtns [data-im-f='${k}']`), b = f && f.parentNode.querySelector('.it-map-pb'); if(!b) return false; const cs = getComputedStyle(b); return cs.display !== 'none' && cs.visibility !== 'hidden' && Number(cs.opacity) > 0.5 && b.getBoundingClientRect().width > 0; }"

def cases(b, html, parts=('col', 'soft', 'ex', 'colour', 'kills', 'rings', 'glow', 'paths', 'panel', 'sovlv', 'wh', 'sec', 'store', 'example', 'phone')):
    out, errs = [], []
    ctx, pg = start(b, html, 1440, errs)
    if not pg.evaluate("typeof itMapSt === 'function' && typeof itMapMatch === 'function' && IT_MAP_FILTERS.some(f => f.k === 'secr')"):
        out.append('no stacked filters on the page (itMapSt, itMapMatch, Security range)'); ctx.close(); return out, errs
    if 'col' in parts:
        ks = pg.evaluate("() => [...document.querySelectorAll('.it-map-fbtns [data-im-f]')].map(b => b.dataset.imF)")
        if ks != ['sec', 'jumps', 'region', 'secr', 'near', 'reports', 'kills', 'wh', 'sov', 'paths']: out.append(f'the column: {ks}')
        sp = pg.evaluate("() => [...document.querySelector('.it-map-fbtns').children].map(c => c.classList.contains('it-map-fsep') ? '|' : (c.querySelector('[data-im-f]') || c).dataset.imF).join(' ')")
        if sp != 'sec jumps region | secr near reports kills wh sov | paths': out.append(f'the groups: {sp}')
        if pg.evaluate("() => itMapOnlyOn() || !!itm.mt || (() => { const T = itMapTable(); for(let i = 0; i < T.n; i++) if(itMapDimmed(i)) return true; return false; })()"): out.append('something dims with no Only filter on')
        if pg.evaluate("() => !!document.querySelector('.it-map-leg .it-map-only')"): out.append('an "Only" legend line with no Only filter on')
        if pg.evaluate("() => !!document.querySelector('.it-map-whn') || !document.querySelector('.it-map-mt').hidden"): out.append('the wormholes chip is still there, or the match chip shows with nothing on')
        if pg.evaluate("() => document.querySelector('.it-map-fbtns [aria-pressed=true]').dataset.imF") != 'sec': out.append('Security is not the colour on a first visit (Q16)')
    if 'soft' in parts:
        r = pg.evaluate("""() => { const T = itMapTable(); let soft = 0, bad = 0; for(let i = 0; i < T.n; i += 7){ const raw = itMapColRaw(i), c = itMapFcol(i);
          if(i === itm.home ? c !== raw : c !== itMapMix(raw, 0.55)) bad++; else soft++; } return [soft, bad, itMapFcol(itm.home) === itMapColRaw(itm.home)]; }""")
        if r[1] or not r[2]: out.append(f'soft colour with nothing on: {r[1]} systems not softened (or yours softened: {not r[2]})')
        pg.evaluate(ZOOM_IN); s0 = near[1]
        a = pg.evaluate(ARCS, [pg.evaluate(f"() => itGraphGet().at.get({s0})")])
        disc = [x for x in list(a['arcs'].values())[0] if x[4].startswith('#')]
        want = pg.evaluate(f"() => {{ const i = itGraphGet().at.get({s0}); return [itMapMix(itMapColRaw(i), 0.38), Math.max(9, Math.min(15, itMapGatePx() * 0.2))]; }}")
        if not disc or disc[0][4] != want[0] or abs(disc[0][2] - want[1]) > 0.01: out.append(f'zoomed in with nothing on: the disc {disc[:1]} (want the tinted {want[0]} at r {want[1]:.2f})')
        pg.evaluate(ZOOM_OUT)
    if 'ex' in parts or 'rings' in parts or 'kills' in parts or 'colour' in parts:
        n = pg.evaluate(EXAMPLE); pg.wait_for_timeout(300)
        r = pg.evaluate(WANT_EXAMPLE)
        if 'ex' in parts:
            if r['bad'] or not r['n']: out.append(f'the owner\'s example: {r["bad"]} systems wrong of {r["n"]} matches')
            if not r['tda'] > r['inR']: out.append(f'the example data: no level-3 system outside the range ({r})')
            if not r['far']: out.append(f'the example data: no match past "Map: within" ({r})')
            g, st = pg.evaluate(ZOOM_OUT)
            m = pg.evaluate("() => { const mt = itMapMatch(); const L = mt.list.filter(i => !itm.rep.has(i)), D = itm.D; let no = -1; for(let i = 0; i < D.length; i++) if(!mt.m[i] && !itm.rep.has(i) && D[i] >= 0 && D[i] <= itm.reach){ no = i; break; } return [L.filter(i => D[i] > itm.reach)[0], L.filter(i => D[i] <= itm.reach)[0], no]; }")
            pg.evaluate("([a, b, c]) => { const v = itm.view, P = itm.P; const xs = [a, b, c].map(i => P[2 * i]), ys = [a, b, c].map(i => P[2 * i + 1]); const k = Math.min(v.k, (itm.W - 80) / Math.max(1, Math.max(...xs) - Math.min(...xs)), (itm.H - 80) / Math.max(1, Math.max(...ys) - Math.min(...ys)));"
                        " v.k = Math.max(itm.kMin, k); v.tx = itm.W / 2 - (Math.max(...xs) + Math.min(...xs)) / 2 * v.k; v.ty = itm.H / 2 - (Math.max(...ys) + Math.min(...ys)) / 2 * v.k; }", m)
            a = pg.evaluate(ARCS, m); gp = pg.evaluate("() => itMapGatePx()")
            if gp < 34:
                dotR = 1.4 if gp < 5 else 2 if gp < 10 else 3
                far_, in_, no_ = (a['arcs'][str(x)] for x in m)
                if not far_ or abs(far_[0][3] - 1) > 1e-6 or abs(far_[0][2] - (dotR + 1.6)) > 0.01: out.append(f'a match past "Map: within" not bright and bigger: {far_[:1]} (want alpha 1, r {dotR + 1.6})')
                if not in_ or abs(in_[0][3] - 1) > 1e-6 or abs(in_[0][2] - (dotR + 1.6)) > 0.01: out.append(f'a match inside the reach not bright and bigger: {in_[:1]}')
                if not no_ or abs(no_[0][3] - 0.16) > 1e-6 or abs(no_[0][2] - dotR) > 0.01: out.append(f'a system that doesn\'t match not dimmed at today\'s size: {no_[:1]}')
            else: out.append(f'the zoomed-out view is zoomed in (gate {gp:.0f} px)')
            if pg.evaluate("() => itMapDimmed(itm.home) || !itMapMatched(itm.home)"): out.append('your system dims')
            pg.evaluate(ZOOM_IN)
            mi = pg.evaluate("() => { const mt = itMapMatch(), seen = (i) => itm.Q[2 * i] > 20 && itm.Q[2 * i] < itm.W - 20 && itm.Q[2 * i + 1] > 20 && itm.Q[2 * i + 1] < itm.H - 20; const L = []; for(let i = 0; i < mt.m.length; i++) if(mt.m[i] && i !== itm.home && !itm.rep.has(i)) L.push(i);"
                             " let i = L.find(seen); if(i === undefined){ i = L[0]; const v = itm.view; v.tx = itm.W / 2 - itm.P[2 * i] * v.k; v.ty = itm.H / 2 - itm.P[2 * i + 1] * v.k; } return i; }")
            a = pg.evaluate(ARCS, [mi]); r0 = pg.evaluate("() => Math.max(9, Math.min(15, itMapGatePx() * 0.2))"); col = pg.evaluate(f"() => itMapColRaw({mi})")
            disc = [x for x in a['arcs'][str(mi)] if x[4].startswith('#') and abs(x[3] - 1) < 1e-6]
            if not disc or abs(disc[0][2] - r0 * 1.25) > 0.01 or disc[0][4] != col: out.append(f'zoomed in, a match\'s disc {disc[:1]} (want r {r0 * 1.25:.2f} in {col})')
            pg.evaluate(ZOOM_OUT)
            leg = pg.evaluate("() => { const o = document.querySelector('.it-map-leg .it-map-only'); return o ? [o.textContent, o.scrollWidth <= o.clientWidth + 1 && o.scrollHeight <= o.clientHeight + 1] : ['', false]; }")
            if not (leg[0].startswith(f"Only {r['list']} match") and 'security -0.5 to -0.3' in leg[0] and 'level 3' in leg[0] and leg[1]): out.append(f'the legend\'s second line: {leg}')
            if not pg.evaluate("() => document.querySelector('.it-map-leg .it-map-fl:not(.it-map-only)').textContent.startsWith('Security')"): out.append('the colour line isn\'t first')
            pr = pg.evaluate("() => [...document.querySelectorAll('.it-map-fbtns [aria-pressed=true]')].map(b => b.dataset.imF).sort()")
            if pr != ['sec', 'secr', 'sov']: out.append(f'pressed: {pr} (want sec, secr, sov)')
            chip = pg.evaluate("() => { const c = document.querySelector('.it-map-mt'); return c && !c.hidden ? c.textContent : ''; }")
            if chip != f"{r['list']} match ›": out.append(f'the match chip: {chip!r}')
            v0 = pg.evaluate("() => [itm.view.tx, itm.view.ty]"); pg.click('.it-map-mt'); pg.wait_for_timeout(200)
            t1 = pg.evaluate("() => [itm.view.tx, itm.view.ty, document.querySelector('.it-map-mt').textContent, (() => { const L = itMapMatch().list; return itm.D[L[0]] <= itm.D[L[L.length - 1]]; })()]")
            if t1[:2] == v0 or not t1[2].startswith('1 of') or not t1[3]: out.append(f'the chip doesn\'t step nearest first: {t1}')
        if 'colour' in parts:
            pg.evaluate("() => itMapFilterSet('jumps')"); pg.wait_for_timeout(150)
            if not pg.evaluate("() => itMapSt().colour === 'jumps' && itMapSt().only.secr && itMapSt().only.sov && itMapMatch().list.length > 0"): out.append('a colour switch lost the stack')
            pg.evaluate("() => itMapFilterSet('jumps')"); pg.wait_for_timeout(150)
            r2 = pg.evaluate("""() => { const T = itMapTable(); let grey = true; for(let i = 0; i < T.n; i += 37) if(itMapColRaw(i) !== IT_MAP_PLAIN) grey = false;
              return [itMapSt().colour, grey, [...document.querySelectorAll('.it-map-fbtns [aria-pressed=true]')].some(b => IT_MAP_COLOURS.includes(b.dataset.imF)), document.querySelector('.it-map-leg .it-map-fl:not(.it-map-only)').textContent.startsWith('No colour'), itMapSt().only.secr]; }""")
            if r2 != ['', True, False, True, True]: out.append(f'no colour (the colour on, pressed again): {r2} (want "", grey, no colour pressed, the legend says so, the stack kept)')
            pg.evaluate(ZOOM_IN); t = pg.evaluate("() => { const ft = [], v = itm.view, P = itm.P, at = new Set(); for(let i = 0; i < P.length / 2; i++) at.add(Math.round(P[2 * i] * v.k + v.tx) + ',' + Math.round(P[2 * i + 1] * v.k + v.ty + 0.5)); const c = itm.cv.getContext('2d'), f = c.fillText; c.fillText = function(t, x, y){ if(at.has(Math.round(x) + ',' + Math.round(y))) ft.push(t); return f.apply(this, arguments); }; itMapDraw(); c.fillText = f; return ft; }")   # only text at a system's centre: a circle's number (a report's count is a label beside it)
            if t: out.append(f'no colour: {len(t)} numbers in the circles {t[:5]} (want none)')
            pg.evaluate("() => itMapFilterSet('sec')"); n_sec = pg.evaluate("() => { const v = itm.view, P = itm.P, at = new Set(); for(let i = 0; i < P.length / 2; i++) at.add(Math.round(P[2 * i] * v.k + v.tx) + ',' + Math.round(P[2 * i + 1] * v.k + v.ty + 0.5)); let n = 0; const c = itm.cv.getContext('2d'), f = c.fillText; c.fillText = function(t, x, y){ if(at.has(Math.round(x) + ',' + Math.round(y))) n++; return f.apply(this, arguments); }; itMapDraw(); c.fillText = f; return n; }")
            if not n_sec: out.append('no colour: the probe finds no circle numbers with Security on either')
            pg.evaluate("() => itMapFilterSet('sec')")
            pg.evaluate(ZOOM_OUT); pg.evaluate("() => itMapFilterSet('sec')")
        if 'kills' in parts:
            k = pg.evaluate("""() => { const s = itMapSt(); for(const x of IT_MAP_ONLY) s.only[x] = false; s.only.kills = true; const i = [...itm.rep.keys()][0]; itm.rep.get(i).kills = 2; itMt.key = null;
              itm.wh = itMapWh(); itm.mt = itMapMatch(itm.wh); const T = itMapTable(); let amber = 0; for(let j = 0; j < T.n; j++) if(itMapFcol(j) === IT_MAP_KILL || itMapColRaw(j) === IT_MAP_KILL) amber++;
              const L = itm.mt.list; itm.rep.get(i).kills = 0; return [amber, L.length, L[0] === i]; }""")
            if k[0] or k[1] != 1 or not k[2]: out.append(f'Kills: {k[0]} dots in amber, {k[1]} matches (want 0 amber, 1 match: the system with kills)')
            pg.evaluate(EXAMPLE)
        if 'rings' in parts:
            hr = pg.evaluate("() => { const mt = itMapMatch(); for(const [i, r] of itm.rep) if(r.side === 'hostile' && !mt.m[i]) return i; return -1; }")
            if hr < 0: out.append('the data: no hostile report outside the matches')
            else:
                pg.evaluate(f"() => {{ const v = itm.view, i = {hr}; v.tx = itm.W / 2 - itm.P[2 * i] * v.k; v.ty = itm.H / 2 - itm.P[2 * i + 1] * v.k; }}")
                a = pg.evaluate(ARCS, [hr]); col = pg.evaluate("() => itMapCol('--danger', '#c65b4e')")
                ring = [x for x in a['arcs'][str(hr)] if x[5].lower() == col.lower() and abs(x[3] - 0.95) < 1e-6]
                if not ring: out.append(f'a hostile ring on a system that doesn\'t match isn\'t at full strength: {a["arcs"][str(hr)]}')
    if 'glow' in parts:
        pg.evaluate("() => { const s = itMapSt(); for(const x of IT_MAP_ONLY) s.only[x] = false; itMapRefresh(true); }")
        g = pg.evaluate(ZOOM_OUT)
        a = pg.evaluate(ARCS, [pg.evaluate("() => itm.home")])
        gl = [x[2] for x in a['arcs'][str(pg.evaluate("() => itm.home"))] if x[4].startswith('rgba(217, 154, 60')]
        want = pg.evaluate("() => 11 * Math.min(1.4, Math.sqrt(itMapGatePx() / IT_MAP_START_GATE))")
        if not gl or abs(gl[0] - want) > 0.01: out.append(f'the alert glow zoomed out: {gl[:1]} (want half today\'s, {want:.2f})')
        pg.evaluate(ZOOM_IN)
        a = pg.evaluate(ARCS, [pg.evaluate("() => itm.home")])
        gl = [x[2] for x in a['arcs'][str(pg.evaluate("() => itm.home"))] if x[4].startswith('rgba(217, 154, 60')]
        want = pg.evaluate("() => Math.max(9, Math.min(15, itMapGatePx() * 0.2)) + 9")
        if not gl or abs(gl[0] - want) > 0.01: out.append(f'the alert glow zoomed in: {gl[:1]} (want today\'s r + 9, {want:.2f})')
        pg.evaluate(ZOOM_OUT)
    if 'paths' in parts:
        pg.evaluate(EXAMPLE); pg.evaluate("() => itMapFilterSet('paths')"); pg.wait_for_timeout(300)
        if not pg.evaluate("() => itPtLive() && !itMapOnlyOn() && !document.querySelector('.it-map-leg .it-map-only') && document.querySelector('.it-map-mt').hidden"): out.append('Paths to you: the stack, its legend line or the chip still shows')
        pg.evaluate("() => itMapFilterSet('paths')"); pg.wait_for_timeout(300)
        if not pg.evaluate("() => !itPtLive() && itMapSt().colour === 'sec' && itMapOnlyOn() && !!document.querySelector('.it-map-leg .it-map-only')"): out.append('back from Paths to you: colour or stack lost')
    ctx.close()

    if 'panel' in parts or 'sovlv' in parts:
        ctx, pg = start(b, html, 1440, errs)
        pg.click('.it-map-fbtns [data-im-f="secr"]'); pg.wait_for_timeout(300)
        bx = pg.evaluate("() => { const x = document.querySelector('.it-mpp'); if(!x || x.hidden) return null; const r = x.getBoundingClientRect(), b = itm.box.getBoundingClientRect(), c = document.querySelector('.it-map-fbtns').getBoundingClientRect();"
                         " return {inside: r.left >= b.left - 1 && r.right <= b.right + 1 && r.top >= b.top - 1 && r.bottom <= b.bottom + 1, right: r.left >= c.right, x: !!x.querySelector('button.x-close'), k: itMapPanel() && itMapPanel().k}; }")
        if 'panel' in parts:
            if not bx or not (bx['inside'] and bx['right'] and bx['x'] and bx['k'] == 'secr'): out.append(f'Security range\'s settings on first switch-on: {bx} (want open, inside the map, right of the column, a close button, itMapPanel)')
            pg.click('.it-mpp [data-rs="mapSecLo"] [data-rs-d="1"]'); pg.wait_for_timeout(150)
            v = pg.evaluate("() => [document.querySelector('.it-mpp [data-rs=mapSecLo] .rs-v').value, itMapSt().secr.lo]")
            if v != ['-0.4', -4]: out.append(f'From steps by 0.1: {v} (want -0.4)')
            pg.click('.it-mpp [data-it-mpq="null"]'); pg.wait_for_timeout(150)
            if pg.evaluate("() => [itMapSt().secr.lo, itMapSt().secr.hi, itMapMatch().list.length > 0]") != [-10, 0, True]: out.append('quick Null isn\'t -1.0 to 0.0, or matches nothing')
            cut = pg.evaluate(FITS)
            if cut: out.append(f'the panel\'s numbers cut off (the owner\'s hand test, 2026-11-16): {cut}')
            if pg.evaluate("() => (document.querySelector('.it-mpp .it-mp-cnt') || {}).textContent || ''") != f"{pg.evaluate('() => itMapMatch().list.length')} systems match every Only filter that is on": out.append('the panel\'s count')
            pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
            if not pg.evaluate("() => document.querySelector('.it-mpp').hidden && document.activeElement === document.querySelector('[data-it-mpn=secr]')"): out.append('Escape doesn\'t shut the panel with focus back on its button')
            if not pg.evaluate(VIS_PB, 'secr'): out.append('the settings button hidden while it has keyboard focus (Escape put it back)')
            # 057 (the owner: "hover should show settings button even when off or on. it doesn't need to stick when on")
            pg.evaluate("() => document.activeElement && document.activeElement.blur()"); pg.mouse.move(700, 900); pg.wait_for_timeout(800)
            if pg.evaluate(VIS_PB, 'secr'): out.append('the settings button stays up while Security range is on, not hovered (want it only on hover)')
            pg.hover('.it-map-fbtns [data-im-f="secr"]'); pg.wait_for_timeout(300)
            if not pg.evaluate(VIS_PB, 'secr'): out.append('no settings button on hover while Security range is on')
            pb_click(pg, 'secr', out); pg.wait_for_timeout(150)
            pg.evaluate("() => itMapFilterSet('secr')"); pg.wait_for_timeout(300)
            if not pg.evaluate("() => !itMapSt().only.secr && itMapSt().secr.lo === -10 && document.querySelector('.it-mpp').hidden"): out.append('off doesn\'t keep the setting and shut the panel')
            pg.hover('.it-map-fbtns [data-im-f="secr"]'); pg.wait_for_timeout(700)
            if not pg.evaluate(VIS_PB, 'secr'): out.append('no settings button on hover while its filter is off (057: on hover, on or off)')
            # build queue 060 (the owner's bug, 2026-11-20): pressed while its filter is off, the settings open; the filter stays off
            for fk in ('secr', 'near'):
                if pg.evaluate("(k) => itMapSt().only[k]", fk): pg.evaluate("(k) => itMapFilterSet(k)", fk); pg.wait_for_timeout(300)
                pb_click(pg, fk, out); pg.wait_for_timeout(300)
                st = pg.evaluate("(k) => { const x = document.querySelector('.it-mpp'); return {open: !!x && !x.hidden && !!itMapPanel() && itMapPanel().k === k, on: !!itMapSt().only[k]}; }", fk)
                if not (st['open'] and not st['on']): out.append(f'the {fk} settings button pressed with its filter off: {st} (want the settings open, the filter still off)')
                pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
            pg.hover('.it-map-fbtns [data-im-f="sov"]'); pg.wait_for_timeout(700)
            if not pg.evaluate(VIS_PB, 'sov'): out.append('no Sov settings button on hover while it is off (057)')
            pg.mouse.move(700, 900)
            pg.evaluate("() => { itMapFilterSet('sov'); sovOpen(true); }"); pg.wait_for_timeout(300)
            pg.evaluate("() => itMapFilterSet('sov')"); pg.wait_for_timeout(300)
            if pg.evaluate("() => sovShown()"): out.append('Sov off doesn\'t shut its panel')
        if 'sovlv' in parts:
            pg.evaluate("() => { const st = sovStore(); st.pick = ['Major Threat Detection Array', 'Minor Threat Detection Array']; sovSave(); const s = itMapSt(); for(const k of IT_MAP_ONLY) s.only[k] = false; s.sovLv = []; itMapFilterSet('sov'); sovOpen(true); }"); pg.wait_for_timeout(300)
            nb = pg.evaluate("() => document.querySelectorAll('.it-sovp .it-sov-lv input[data-sov-lv]').length")
            if nb != 3: out.append(f'Sov\'s Level boxes: {nb} (want 3)')
            n0 = pg.evaluate("() => itMapMatch().list.length")
            pg.click('.it-sovp [data-sov-lv="3"]'); pg.wait_for_timeout(200); n3 = pg.evaluate("() => itMapMatch().list.length")
            if not 0 < n3 < n0: out.append(f'level 3 ticked doesn\'t narrow: {n0} -> {n3}')
            for lv in ('3', '1', '2'): pg.click(f'.it-sovp [data-sov-lv="{lv}"]'); pg.wait_for_timeout(120)
            n12 = pg.evaluate("() => itMapMatch().list.length")
            if pg.evaluate("() => JSON.stringify(itMapSt().sovLv)") != '[1,2]' or not (0 < n12 < n0 and n12 + n3 >= n0): out.append(f'levels 1 and 2: {pg.evaluate("() => itMapSt().sovLv")}, {n12} of {n0} (3 alone {n3})')
            if 'level 1, 2' not in pg.evaluate("() => (document.querySelector('.it-map-leg .it-map-only') || {}).textContent || ''"): out.append('the legend doesn\'t name levels 1, 2')
            for lv in ('1', '2'): pg.click(f'.it-sovp [data-sov-lv="{lv}"]'); pg.wait_for_timeout(120)
            if pg.evaluate("() => itMapMatch().list.length") != n0: out.append('none ticked isn\'t any level again')
            if pg.evaluate("() => Object.keys(JSON.parse(localStorage.getItem('tvSov'))).sort().join(',')") != 'lists,pick,v': out.append('tvSov changed its form')
        ctx.close()

    if 'wh' in parts:
        ctx, pg = start(b, html, 1440, errs)
        r = pg.evaluate("""() => { const s = itMapSt(); for(const k of IT_MAP_ONLY) s.only[k] = false; itMapFilterSet('wh'); const wh = itm.wh, mt = itMapMatch();
          return {kept: wh.kept.size, mark: wh.mark.size, bold: [...wh.kept.keys()].every(i => itMapWhBoldAt(i)), fresh: [...wh.kept.values()].filter(w => Date.now() - w.t < IT_MAP_WH_FRESH_MS).length, list: mt.list.length,
            chip: document.querySelector('.it-map-mt').textContent}; }""")
        if not (r['kept'] == len(WH) and r['mark'] == len(WH) and r['bold'] and r['list'] == len(WH) and r['chip'] == f"{len(WH)} match ›"): out.append(f'Wormholes alone: {r} (want all {len(WH)} kept holes marked bold, the chip counting them)')
        pg.evaluate("() => { const P = itm.P, S = [itm.home, ...itm.wh.kept.keys()], xs = S.map(i => P[2 * i]), ys = S.map(i => P[2 * i + 1]), v = itm.view;"
                    " v.k = Math.max(itm.kMin, Math.min((itm.W - 120) / Math.max(1, Math.max(...xs) - Math.min(...xs)), (itm.H - 120) / Math.max(1, Math.max(...ys) - Math.min(...ys))));"
                    " v.tx = itm.W / 2 - (Math.max(...xs) + Math.min(...xs)) / 2 * v.k; v.ty = itm.H / 2 - (Math.max(...ys) + Math.min(...ys)) / 2 * v.k; itMapDraw(); }")
        reduced = pg.evaluate("() => matchMedia('(prefers-reduced-motion: reduce)').matches")
        np_ = pg.evaluate("() => itm.whp.children.length")
        if not reduced and np_ != r['fresh']: out.append(f'the pulse: {np_} rings (want {r["fresh"]}, the fresh holes)')
        q = pg.evaluate("""() => { const s = itMapSt(); s.only.near = true; s.near.n = 3; itMapStackSave(); itMapRefresh(true); const wh = itm.wh, mt = itMapMatch(), bad = [], n = {bold: 0, thin: 0, none: 0};
          for(const [i, w] of wh.kept){ const want = mt.m[i] ? 'bold' : wh.live.has(i) ? 'thin' : 'none', got = !wh.mark.has(i) ? 'none' : itMapWhBoldAt(i) ? 'bold' : 'thin'; n[got]++; if(want !== got) bad.push([itSysName(itGraphGet().ids[i]), want, got]); }
          return {bad, n, chip: document.querySelector('.it-map-mt').textContent, list: mt.list.length}; }""")
        if q['bad'] or not (q['n']['bold'] and q['n']['thin'] and q['n']['none']): out.append(f'Wormholes + Within 3 jumps (Q21b): {q} (want the matches bold, a live hole past 3 thin, the rest unmarked, one of each)')
        if q['chip'] != f"{q['list']} match ›": out.append(f'the chip with Wormholes + Within 3: {q["chip"]!r}')
        pg.evaluate("() => { const s = itMapSt(); s.only.near = false; s.only.wh = false; itMapRefresh(true); }")
        if pg.evaluate("() => itm.whp.children.length || [...itm.wh.mark.keys()].some(i => itMapWhBoldAt(i)) || itm.wh.mark.size !== itm.wh.live.size"): out.append('Wormholes off: a pulse, a bold hole, or kept holes still marked')
        ctx.close()

    if 'sec' in parts or 'store' in parts or 'example' in parts:
        ctx, pg = start(b, html, 1440, errs)
        if 'sec' in parts:
            r = pg.evaluate("""() => { const T = itMapTable(), L = []; for(let i = 0; i < T.n; i++) if(T.sec[i] === 45 && T.band[i] === 1) L.push(i);
              const i = L[0]; if(i === undefined) return null; const s = itMapSt(); for(const k of IT_MAP_ONLY) s.only[k] = false; s.only.secr = true; s.secr = {lo: 5, hi: 10}; itMt.key = null;
              itm.wh = itMapWh(); const mt = itMapMatch(itm.wh); return [L.length, itMapSecText(i), itMapSecClass(i), IT_MAP_SEC[itMapSecClass(i)] === IT_MAP_SEC[4], !!mt.m[i]]; }""")
            if r != [19, '0.4', 4, True, False]: out.append(f'the 0.45 systems that are low-sec: {r} (want 19 of them showing 0.4, the 0.4 colour, outside quick High)')
            pg.evaluate("() => { const s = itMapSt(); s.only.secr = false; s.secr = {lo: -5, hi: -3}; itMapRefresh(true); }")
        if 'store' in parts:
            pg.evaluate(EXAMPLE); pg.evaluate("() => { itMapFilterSet('jumps'); const s = itMapSt(); s.near.n = 7; itMapStackSave(); }")
            want = pg.evaluate("() => JSON.stringify(itMapSt())")
            pg.reload(); pg.wait_for_timeout(500)
            got = pg.evaluate("() => JSON.stringify(itMapStackRead())")
            if got != want: out.append(f'tvMapStack across a reload: {got} (want {want})')
            for bad in ('not json', '{"v": 2, "colour": ""}', '{"v": 1, "colour": "kills", "view": "x", "only": {"secr": "yes"}, "secr": {"lo": 3.5, "hi": -40}, "near": {"n": 99}, "sovLv": [0, 3, 3, 7, "2"]}'):
                pg.evaluate("(v) => localStorage.setItem('tvMapStack', v)", bad)
                r = pg.evaluate("() => itMapStackRead()")
                ok = r['colour'] == 'sec' and r['view'] == 'map' and not any(r['only'].values()) and r['secr'] == {'lo': -5, 'hi': -3} and r['near'] == {'n': 5} and r['sovLv'] == ([3] if '"v": 1' in bad else [])
                if not ok: out.append(f'a bad tvMapStack {bad[:30]!r} read as {r}')
        if 'example' in parts:
            before = pg.evaluate("() => { const v = JSON.stringify(Object.assign(itMapStackBlank(), {colour: '', only: {secr: true, near: false, reports: false, kills: false, wh: false, sov: false}})); localStorage.setItem('tvMapStack', v); return v; }")
            pg.reload(); pg.wait_for_timeout(500)   # the card draws the example on load: the store must still be what was written
            r = pg.evaluate("() => { itEx.map = null; const u = itExMapPic(800); return [!!u, localStorage.getItem('tvMapStack')]; }")
            if not r[0] or r[1] != before: out.append(f'the Intel example: {r[:1]} picture, the store {"changed" if r[1] != before else "kept"}')
        ctx.close()

    if 'phone' in parts:
        ctx, pg = start(b, html, 390, errs, h=844, touch=True)
        pg.evaluate(EXAMPLE); pg.wait_for_timeout(300)
        bd = pg.evaluate("() => (document.querySelector('.it-map-fcur .it-map-fbd') || {}).textContent || ''")
        if bd != '2': out.append(f'390 px: the folded button\'s count {bd!r} (want 2)')
        if pg.evaluate("() => { const b = document.querySelector('.it-map-fcur .it-map-fbd'); return b ? getComputedStyle(b).backgroundColor : ''; }") == pg.evaluate("() => getComputedStyle(document.body).getPropertyValue('--amber')"): out.append('390 px: the count is amber')
        pg.click('.it-map-fcur'); pg.wait_for_timeout(200)
        pb_click(pg, 'secr', out); pg.wait_for_timeout(300)
        r = pg.evaluate("() => { const x = document.querySelector('.it-mpp'), r = x.getBoundingClientRect(), b = itm.box.getBoundingClientRect(), q = [...x.querySelectorAll('.it-mp-q button, .rs-b')].map(e => Math.round(e.getBoundingClientRect().height));"
                        " return [!x.hidden, r.left >= b.left - 1 && r.right <= b.right + 1, Math.min(...q)]; }")
        if r[:2] != [True, True] or r[2] < 44: out.append(f'390 px: the Security range sheet {r} (want open inside the map, 44 px targets)')
        cut = pg.evaluate(FITS)
        if cut: out.append(f'390 px: the panel\'s numbers cut off: {cut}')
        pg.click('.it-mpp .x-close'); pg.wait_for_timeout(200)
        ch = pg.evaluate("() => { const c = document.querySelector('.it-map-mt'); return [!c.hidden, Math.round(c.getBoundingClientRect().height)]; }")
        if ch != [True, 44]: out.append(f'390 px: the match chip {ch} (want shown, 44 px)')
        if not pg.evaluate("() => document.scrollingElement.scrollWidth <= innerWidth + 1"): out.append('390 px: sideways scroll')
        ctx.close()
    return out, errs

MUTANTS = [
    ('a non-matching kept hole still bold (Q21b)', "itm.wh.kept.has(i) && itm.mt.m[i]); }", "itm.wh.kept.has(i)); }", ('wh',)),
    ('Kills still amber (Q3)', "  const T = itMapTable(), c = itMapSt().colour;\n  if(c === 'jumps')", "  const T = itMapTable(), c = itMapSt().colour;\n  if((itm.rep.get(i) || {}).kills) return IT_MAP_KILL;\n  if(c === 'jumps')", ('kills',)),
    ('OR instead of AND (Q2)', "    if(ok && o.near) ok = D[i] >= 0 && D[i] <= s.near.n;", "    if(o.near) ok = ok || (D[i] >= 0 && D[i] <= s.near.n);", ('wh',)),
    ('the distance fade kept while filtering (Q6)', "alpha = (i) => mt ? (mt.m[i] ? 1 : IT_MAP_DIM)", "alpha = (i) => mt ? (mt.m[i] ? (!on(i) ? IT_MAP_FAINT : 1) : IT_MAP_DIM)", ('ex',)),
    ('no settings button on hover (057)', ".it-map-fw:hover > button.it-map-pb, .it-map-fw:has(", ".it-map-fw:has(", ('panel',)),
    ('the settings button kept up while its filter is on (057: hover only)', ".it-map-fw:hover > button.it-map-pb, .it-map-fw:has(", ".it-map-fw > [aria-pressed=\"true\"] ~ button.it-map-pb, .it-map-fw:hover > button.it-map-pb, .it-map-fw:has(", ('panel',)),
    ('the stack not kept (Q11)', "function itMapStackSave(){ try{ localStorage.setItem(MAP_STACK_KEY, JSON.stringify(itMapSt())); }", "function itMapStackSave(){ try{ }", ('store',)),
    ('a ring faded off the matches (Q7)', "c.lineWidth = big ? 2.5 : 2.2; c.globalAlpha = 0.95;", "c.lineWidth = big ? 2.5 : 2.2; c.globalAlpha = itMapDimmed(i) ? 0.2 : 0.95;", ('rings',)),
    ('the alert glow at today\'s size zoomed out', "big ? r + 9 : 11 * Math.min(1.4", "big ? r + 9 : 22 * Math.min(1.4", ('glow',)),
    ('no soft colour (Q15)', "function itMapFcol(i){ const c = itMapColRaw(i); return i === itm.home || itMapMatched(i) ? c : itMapMix(c, 0.55); }", "function itMapFcol(i){ return itMapColRaw(i); }", ('soft',)),
    ('a match not bigger (Q8)', "hit === '1' ? dotR + 1.6 : dotR;", "dotR;", ('ex',)),
    ('the 0.45 line ignored', "return t >= 5 && T.band && T.band[i] === 1 ? 4 : t;", "return t;", ('sec',)),
    ('a number in the circles with no colour', "const col = itMapSt().colour; if(col) c.fillText(", "const col = itMapSt().colour || 'sec'; if(col) c.fillText(", ('colour',)),
    ('the settings only open with the filter on (060\'s bug)', "  if(!itm.box || (k !== 'secr' && k !== 'near')) return;", "  if(!itm.box || !itMapSt().only[k] || (k !== 'secr' && k !== 'near')) return;", ('panel',)),
    ('the panel\'s numbers cut off (the hand test)', ".it-mpp .rs-v{width:5.2ch;}", ".it-mpp .rs-v{}", ('panel',)),
    # 055: the example's stack is set aside for everything it draws, in itExSandbox (it was set only for the picture, in itExMapPic)
    ('the example writing the user\'s stack', "itm.st = itMapStackBlank(); itm.mt = null;", "itMapSt().colour = 'region'; itMapStackSave(); itm.mt = null;", ('example',)),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, 'the stacked filters: column, colour, matches, marks, panels, wormholes, the security shown, storage, phone')
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
