"""Jump bridges on the Intel map (build queue 041; plan roadmap/jump-bridges-plan.md, mockup Claude outputs/jump_bridges_mockup.html).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/intel_bridges_check.py [index.html]   -> 'FAILURES: N' (must be 0)

The owner: "add jump bridges to the map (as a setting that can be toggled off and on). when turned on, jump ranges will be calculated using
bridges. default setting will be off." and "ideally i'd like to only have near you not use bridges"; at the re-plan "Both count bridges",
"Switch governs both; gates until 057". Uses intel_check.py's made-up folder, mocks and names (you in 1DQ1-A); every list here is made up from
the map's own systems (his real list is alliance data: never in a check). The mock's names are one word, so the 3-word case isn't run here.
Checks:
  * the list (itBridges): EVE's structure name with text after it, <->, ⇄, ->, a comma, a tab, two names and any case; SMT's export with
    structure ids, one line per direction (D8 ids ignored: no system's name is digits only, so no mutant can show it; D6 the reverse a dim repeat counted once); a separator line with a third system
    (D7: the pair around the separator); refused: three systems with no separator, the same system twice, one system; the warnings (one
    bridge per system, more than 5 LY) counted all the same; the count;
  * the setting off (a saved setting without the keys): itm.D is itm.Dg, no curves, no bridge words;
  * on, bridges from systems 1 jump out to ones 9 and 12 out: the map 2 jumps (itm.D), by stargate 9 and 12 (itm.Dg), never longer than itm.Dg anywhere;
    itJumps, Near You's rows (and their alert marks) and the Feed the same on and off; the alert glow and Paths to you's sources by stargate;
    the hover: "1 of the 2 jumps by jump bridge · by stargate only 9 jumps", "route by stargate:", the kill-range line by stargate, Threat
    Vector's route compared with the stargate count; 058's Jumps colour and Within N count the bridge, off they don't, the legend and the
    notes say so; green curves while on, a route's bridge step drawn as a curve (D13);
  * sovBridgeEnds() (053's hook): both ends of every counted bridge, the same with the switch off; 053's Jump bridge kind has them;
  * the box under the gear right after Routes, the switch's row 32 px (44 on a phone), typing reads the rows, the switch counts them, a reload
    keeps both; the Intel example leaves the live map's search alone; no sideways scroll, no page errors;
  * mutants, each must fail (see MUTANTS).
v2026.11.16.4 fails (no bridges).
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
by_d = {}
for s_, v in sorted(D0.items(), key=lambda kv: (kv[1], kv[0])): by_d.setdefault(v, []).append(s_)
def at(d, k=0): return by_d[d][k % len(by_d[d])]
def nm(i): return SYSNAME[i]
T0 = time.time()
NEARBY, FAR = at(1, 0), at(9, 0)   # the bridge the counts are checked on: 1 jump out to 9 out (inside Near You's reach, which stops at the Feed's kill range, 10)
NEARBY2, FAR2 = at(1, 1), at(12, 0)   # and one to 12 out: past the Feed's kill range by stargate
# the list's cases (each system once except where a case needs it twice)
P = [at(d, k) for d in (14, 15, 16, 17) for k in range(8)]
LIST_ROWS = [
    (f'{nm(P[0])} » {nm(P[1])} - Mockup bridge', 'count', (P[0], P[1])),
    (f'Mockup gate {nm(P[2])} <-> {nm(P[3])}', 'count', (P[2], P[3])),
    (f'{nm(P[4])} ⇄ {nm(P[5])}', 'count', (P[4], P[5])),
    (f'{nm(P[6])} -> {nm(P[7])}', 'count', (P[6], P[7])),
    (f'{nm(P[8])}, {nm(P[9])}', 'count', (P[8], P[9])),
    (f'{nm(P[10])}\t{nm(P[11])}', 'count', (P[10], P[11])),
    (f'{nm(P[12]).lower()} {nm(P[13]).upper()}', 'count', (P[12], P[13])),
    (f'1234567 {nm(P[14])} → {nm(P[15])}', 'count', (P[14], P[15])),
    (f'1234568 {nm(P[15])} → {nm(P[14])}', 'dup', 'same bridge as line 8'),
    (f'{nm(P[16])} » {nm(P[17])} - {nm(P[18])} Mockup', 'count', (P[16], P[17])),
    (f'{nm(P[19])} {nm(P[20])} {nm(P[21])}', 'bad', 'more than two systems'),
    (f'{nm(P[22])} {nm(P[22])}', 'bad', 'the same system twice'),
    (f'{nm(P[23])} Nowhere', 'bad', 'needs two systems (found only'),
    (f'{nm(P[0])} » {nm(P[24])}', 'warn', 'is also on line 1 (one jump bridge per system)'),
]
COUNT_TEXT = f'{nm(NEARBY)} » {nm(FAR)} - Mockup bridge\n{nm(NEARBY2)} » {nm(FAR2)} - Mockup bridge\n'

def start(b, html, w, errs, h=1000, touch=False):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch, device_scale_factor=2 if touch else 1)
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); route(ctx)
    pg = ctx.new_page(); pg.goto('file://' + html)
    # a saved setting from before 041: no bridges, no bridgesOn
    pg.evaluate("([s]) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({nearShown: true, channels: ['region.intel'], me: 95000001, range: 3, nearRange: 15, mapReach: 15, sound: false, notify: false, forget: 15, hideFriendly: true})); }", [SIDE])
    pg.reload(); pg.wait_for_timeout(400)
    setup_logs(pg); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg)
    W(pg, F_INTEL, line(T0, 'Scout Alt', f'{nm(FAR)} 2 red') + line(T0 + 1, 'Scout Alt', f'{nm(at(2, 1))} 3 red'))
    tick(pg, 3200)
    pg.evaluate("() => document.querySelector('#intelPanel .it-map-box').scrollIntoView({block: 'center'})"); pg.wait_for_timeout(200)
    pg.evaluate(REC)
    return ctx, pg

# the map's canvas calls during one draw: the alert glow's discs and the curves (green ones are bridges)
REC = """() => { const C = CanvasRenderingContext2D.prototype; if(C.__jb) return; C.__jb = true; window.__rec = null;
  const arc = C.arc, qc = C.quadraticCurveTo;
  C.arc = function(x, y, r, a, b){ if(window.__rec && this.canvas === itm.cv && String(this.fillStyle).replace(/\\s/g, '') === 'rgba(217,154,60,0.07)') window.__rec.glow.push([x, y]); return arc.apply(this, arguments); };
  C.quadraticCurveTo = function(){ if(window.__rec && this.canvas === itm.cv) window.__rec.qc.push(String(this.strokeStyle).toLowerCase()); return qc.apply(this, arguments); }; }"""
DRAW = "() => { window.__rec = {glow: [], qc: []}; itMapDraw(); const r = window.__rec; window.__rec = null; return r; }"
SET = "([t, on]) => { it.set.bridges = t; it.set.bridgesOn = on; itWriteSet(); itMapRefresh(); itMapFitView(); return [itm.jbKey, itBridges().edges.length]; }"
STATE = """([far, near]) => { const g = itGraphGet(), i = g.at.get(far), D = itm.D, Dg = itm.Dg; let longer = 0; for(let k = 0; k < D.length; k++) if(Dg[k] >= 0 && D[k] > Dg[k]) longer++;
  return {D: D[i], Dg: Dg[i], same: D === Dg, longer, ij: itJumps(itMySys(), far), ijn: itJumps(itMySys(), near), src: itPtSources().includes(i), i}; }"""

def cases(b, html, parts=('list', 'counts', 'ui', 'phone')):
    out, errs = [], []
    if 'list' in parts or 'counts' in parts:
        ctx, pg = start(b, html, 1440, errs)
        if 'list' in parts:
            r = pg.evaluate("() => [it.set.bridges, it.set.bridgesOn, itm.jbKey, itm.D === itm.Dg]")
            if r != ['', False, '', True]: out.append(f'a saved setting without the keys: {r} (want off and empty, itm.D the stargate count)')
            text = '\n'.join(x[0] for x in LIST_ROWS)
            # the 5 LY warning: a pair of gate neighbours under 5 LY (counted, no warning) and a pair over 6 LY (counted, warned)
            ly = pg.evaluate("""() => { const T = itMapTable(), g = itGraphGet(); let near = null, far = null; const h = g.at.get(itMySys());
              for(let i = 0; i < T.n && !(near && far); i++){ if(!near) for(const j of T.adj[i]) if(itMapLy(i, j) < 4){ near = [g.ids[i], g.ids[j]]; break; } if(!far && i !== h && itMapLy(i, h) > 6.5 && itMapLy(i, h) < 9) far = [g.ids[i], g.ids[h]]; }
              return [near, far]; }""")
            used = {x for row in LIST_ROWS if isinstance(row[2], tuple) for x in row[2]}
            ok_pair, far_pair = ly
            text += f'\n{nm(ok_pair[0])} {nm(ok_pair[1])}\n{nm(far_pair[0])} {nm(far_pair[1])}'
            r = pg.evaluate("(t) => { it.set.bridges = t; const B = itBridges(); return {rows: B.rows.map(r => [r.n, r.st, r.a || 0, r.b || 0, r.msg || '']), n: B.edges.length, ends: B.ends, count: itBridgeCountText()}; }", text)
            rows = {x[0]: x for x in r['rows']}
            for n, (ln, want, what) in enumerate(LIST_ROWS, 1):
                got = rows.get(n)
                if not got: out.append(f'line {n} ({ln!r}): no row'); continue
                if want == 'count':
                    if got[1] not in ('ok', 'warn') or {got[2], got[3]} != set(what): out.append(f'line {n} ({ln!r}): {got} (want counted, {what})')
                elif want == 'dup':
                    if got[1] != 'dup' or what not in got[4]: out.append(f'line {n} ({ln!r}): {got} (want the dim repeat "{what}")')
                elif got[1] != want or what not in got[4]: out.append(f'line {n} ({ln!r}): {got} (want {want} "{what}")')
            nl = len(LIST_ROWS)
            okr, farr = rows.get(nl + 1), rows.get(nl + 2)
            if not okr or okr[1] != 'ok' or okr[4]: out.append(f'a bridge under 4 LY with nothing else on its line: {okr} (want ✓, no warning)')
            if not farr or farr[1] != 'warn' or 'more than 5 LY apart' not in farr[4]: out.append(f'a bridge over 6.5 LY: {farr} (want ⚠ more than 5 LY apart, counted)')
            want_n = sum(1 for x in LIST_ROWS if x[1] in ('count', 'warn')) + 2
            if r['n'] != want_n or r['count'] != f'({want_n} bridges)': out.append(f'the count: {r["n"]} edges, {r["count"]!r} (want {want_n})')
            want_ends = sorted({x for row in LIST_ROWS if isinstance(row[2], tuple) for x in row[2]} | {P[0], P[24]} | set(ok_pair) | set(far_pair))
            if r['ends'] != want_ends: out.append(f'sovBridgeEnds: {len(r["ends"])} ends (want {len(want_ends)}: both ends of every counted bridge)')
            for on in (False, True):
                e = pg.evaluate("(on) => { it.set.bridgesOn = on; return [sovBridgeEnds().length, sovBridgeEnds()[0], [...sovIndex().at.values()].filter(m => m.has(SOV_ALN)).length]; }", on)
                if e[0] != len(want_ends) or e[1] != want_ends[0] or e[2] < len(want_ends): out.append(f'sovBridgeEnds with the switch {"on" if on else "off"}: {e} (want {len(want_ends)} ends, each in Sov\'s Jump bridge kind)')
            pg.evaluate("() => { it.set.bridges = ''; it.set.bridgesOn = false; }")
        if 'counts' in parts:
            near_off, feed_off = pg.evaluate(NEAR), pg.evaluate(FEED)
            st_off = pg.evaluate(STATE, [FAR, NEARBY])
            if not st_off['same'] or st_off['D'] != D0[FAR]: out.append(f'off: {st_off} (want itm.D the stargate count {D0[FAR]})')
            dr_off = pg.evaluate(DRAW)
            if any(c == '#00f000' for c in dr_off['qc']): out.append('off: a green curve drawn')
            r = pg.evaluate(SET, [COUNT_TEXT, True])
            if not r[0] or r[1] != 2: out.append(f'on: {r} (want two bridges counted)')
            st = pg.evaluate(STATE, [FAR, NEARBY])
            if st['D'] != 2 or st['Dg'] != D0[FAR] or st['same'] or st['longer']: out.append(f'on: {st} (want the map 2 jumps, by stargate {D0[FAR]}, never longer than itm.Dg)')
            if st['ij'] != D0[FAR] or st['ijn'] != 1: out.append(f'on: itJumps {st["ij"]}, {st["ijn"]} (want {D0[FAR]}, 1: Near You, alerts and the Feed stay by stargate)')
            if st['src']: out.append('on: Paths to you takes the bridged system as a source (2 by bridge, 12 by stargate, the alert range 3)')
            pg.wait_for_timeout(300)
            near_on, feed_on = pg.evaluate(NEAR), pg.evaluate(FEED)
            if near_on != near_off: out.append(f'on: Near You\'s rows changed {near_off} -> {near_on}')
            if feed_on != feed_off: out.append('on: the Feed\'s rows changed')
            if not any(r_[0] == nm(FAR) and r_[1] == f'{D0[FAR]}j' for r_ in near_on): out.append(f'Near You: no row for the bridged system at {D0[FAR]} jumps {near_on}')
            dr = pg.evaluate(DRAW)
            if not any(c == '#00f000' for c in dr['qc']): out.append('on: no green curve drawn')
            q = pg.evaluate("(i) => [itm.Q[2 * i], itm.Q[2 * i + 1], itm.W, itm.H]", st['i'])
            if not (0 <= q[0] <= q[2] and 0 <= q[1] <= q[3]): out.append(f'on: the bridged system is off the map after a fit {q}')
            elif any(abs(x - q[0]) < 1 and abs(y - q[1]) < 1 for x, y in dr['glow']): out.append('on: the alert glow on the bridged system (2 by bridge, 12 by stargate)')
            tip = pg.evaluate("(i) => { itMapTip(i, 20, 20); return itm.tip.innerHTML; }", st['i'])
            for want in ['1 of the 2 jumps by jump bridge', f'by stargate only {D0[FAR]} jumps', 'route by stargate:']:
                if want not in tip: out.append(f'on: the hover lacks "{want}"')
            if "past the Feed's kill range" in tip: out.append(f'on: the hover says {D0[FAR]} stargate jumps is past the kill range (10)')
            tip2 = pg.evaluate("(id) => { itMapTip(itGraphGet().at.get(id), 20, 20); return itm.tip.innerHTML; }", FAR2)
            if "past the Feed's kill range" not in tip2: out.append(f'on: the hover of a system 2 by bridge, {D0[FAR2]} by stargate lacks the kill-range line')
            if re.search(r'\(shortest[^)]* 2\)', tip): out.append('on: Threat Vector\'s route compared with the bridges\' count ("shortest 2")')
            # 058: Jumps colour and Within N count the bridge while on
            r = pg.evaluate("""(i) => { const s = itMapSt(), c0 = s.colour, o0 = s.only.near, n0 = s.near.n; s.colour = 'jumps'; s.only.near = true; s.near.n = 3;
              const out = [itMapColRaw(i), IT_MAP_JUMPS[2], !!(itMapMatch() || {m: []}).m[i], itMapFLegHtml(), itMapFLegTitle(), itMpBodyHtml('near'), itMapFNote(IT_MAP_FILTERS.find(f => f.k === 'jumps'))];
              it.set.bridgesOn = false; itMapRefresh();
              out.push(itMapColRaw(i), !!(itMapMatch() || {m: []}).m[i], itMapFLegHtml(), itMpBodyHtml('near'), itm.jbKey, itm.D === itm.Dg);
              it.set.bridgesOn = true; itMapRefresh(); out.push(!!(itMapMatch() || {m: []}).m[i]);
              s.colour = c0; s.only.near = o0; s.near.n = n0; itm.mt = null; return out; }""", st['i'])
            if r[0] != r[1]: out.append(f'on: Jumps colours the bridged system {r[0]} (want {r[1]}, 2 jumps)')
            if not r[2]: out.append('on: Within 3 jumps doesn\'t match the bridged system')
            if 'your jump bridges counted' not in r[3] or 'your jump bridges counted' not in r[4] or 'your jump bridges counted' not in r[5] or 'your jump bridges counted' not in r[6]: out.append('on: the Jumps legend, title, Within N note or filter note doesn\'t say the bridges are counted')
            if r[7] == r[0] or r[8] or 'your jump bridges counted' in r[9] or 'your jump bridges counted' in r[10] or r[11] != '' or not r[12]: out.append(f'off again: Jumps {r[7]} (on {r[0]}), Within 3 {r[8]}, key {r[11]!r}, D is Dg {r[12]} (want stargates, no bridge words)')
            if not r[13]: out.append('on again: Within 3 jumps lost the bridged system')
            # D13: a route step that isn't a gate is drawn as its bridge's curve (the Intel example's / not-yet-worked-out fallback, itm.par)
            r = pg.evaluate("""([i, id]) => { const a = itRpAside; itRpAside = true; itm.pinned.add(id); window.__rec = {glow: [], qc: []}; itMapDraw(); const q = window.__rec.qc; window.__rec = null;
              itm.pinned.delete(id); itRpAside = a; itMapDraw(); return q.filter(c => c !== '#00f000').length; }""", [st['i'], FAR])
            if r < 1: out.append('on: a route over a bridge drew its bridge step as a straight line (D13)')
            # the Intel example draws with the setting off and leaves the live search alone
            r = pg.evaluate("() => { const D = itm.D, k = itm.jbKey; itEx.map = null; const u = itExMapPic(800); return [!!u, itm.D === D, itm.jbKey === k, it.set.bridgesOn]; }")
            if r != [True, True, True, True]: out.append(f'the Intel example: {r} (want a picture, the live map\'s search and the setting untouched)')
        ctx.close()
    if 'ui' in parts:
        ctx, pg = start(b, html, 1440, errs)
        pg.click('[data-it-act="gear"]'); pg.wait_for_timeout(300)
        r = pg.evaluate("() => { const b = document.querySelector('[data-it-jb-box]'), p = b && b.previousElementSibling; return [!!b, !!(p && p.matches('[data-it-rp-box]')), b ? Math.round(b.querySelector('.jb-on').getBoundingClientRect().height) : 0, b ? b.querySelector('[data-it-jb-n]').textContent : '']; }")
        if r[:2] != [True, True] or r[2] < 32 or r[3] != '(0 bridges)': out.append(f'the box: {r} (want right after Routes, its row 32 px, "(0 bridges)")')
        pg.fill('[data-it-jb]', COUNT_TEXT + f'{nm(at(3, 0))} {nm(at(9, 0))}\nnot a bridge'); pg.wait_for_timeout(200)
        r = pg.evaluate("() => [[...document.querySelectorAll('[data-it-jb-box] li')].map(l => l.className), document.querySelector('[data-it-jb-n]').textContent, itm.jbKey, document.activeElement && document.activeElement.matches('[data-it-jb]')]")
        if r[0][-1:] != ['bad'] or len(r[0]) != 4 or r[1] != '(3 bridges)' or r[2] != '' or not r[3]: out.append(f'typed: {r} (want 4 rows, the last ✗, "(3 bridges)", not counted while off, the focus kept)')
        pg.click('[data-it-jbon]'); pg.wait_for_timeout(300)
        r = pg.evaluate("([far]) => [it.set.bridgesOn, !!itm.jbKey, itm.D[itGraphGet().at.get(far)], JSON.parse(localStorage.getItem('dscanIntel')).bridgesOn]", [FAR])
        if r != [True, True, 2, True]: out.append(f'the switch on: {r} (want counted, the bridged system 2 jumps, saved)')
        pg.reload(); pg.wait_for_timeout(500)
        r = pg.evaluate("() => [it.set.bridgesOn, it.set.bridges.split('\\n').length]")
        if r != [True, 4]: out.append(f'after a reload: {r} (want the switch on and the 4 lines kept)')
        if not pg.evaluate("() => document.scrollingElement.scrollWidth <= innerWidth + 1"): out.append('1440 px: sideways scroll')
        ctx.close()
    if 'phone' in parts:
        ctx, pg = start(b, html, 390, errs, h=844, touch=True)
        pg.click('[data-it-act="gear"]'); pg.wait_for_timeout(300)
        h = pg.evaluate("() => { const l = document.querySelector('[data-it-jb-box] .jb-on'); return l ? Math.round(l.getBoundingClientRect().height) : 0; }")
        if h < 44: out.append(f'390 px: the switch\'s row {h} px (want 44)')
        pg.fill('[data-it-jb]', COUNT_TEXT); pg.wait_for_timeout(200)
        if not pg.evaluate("() => document.scrollingElement.scrollWidth <= innerWidth + 1"): out.append('390 px: sideways scroll')
        ctx.close()
    return out, errs

MUTANTS = [
    ('Near You counting a bridge', "  const g = itGraphGet(), s = g.at.get(from), t = g.at.get(to);\n  if(s === undefined || t === undefined) return null;\n  let d = g.dist.get(from);",
     "  const g0 = itGraphGet(), g = itBridgeOn() ? {...g0, adj: itBridgeAdj(), dist: new Map()} : g0, s = g.at.get(from), t = g.at.get(to);\n  if(s === undefined || t === undefined) return null;\n  let d = g.dist.get(from);", ('counts',)),
    ('bridges counted with the switch off', "function itBridgeOn(){ return !!(it.set && it.set.bridgesOn) && itBridges().edges.length > 0; }", "function itBridgeOn(){ return itBridges().edges.length > 0; }", ('counts',)),
    ('Paths to you on the bridges\' count', "  const D = itm.Dg || itm.D, R = it.set.range, out = [];", "  const D = itm.D, R = it.set.range, out = [];", ('counts',)),
    ('the alert glow on the bridges\' count', "if(Dg[i] >= 0 && Dg[i] <= it.set.range && seen(i)){", "if(D[i] <= it.set.range && seen(i)){", ('counts',)),
    ('the kill-range line on the bridges\' count', "  const dg = itm.Dg ? itm.Dg[i] : d;", "  const dg = d;", ('counts',)),
    ('Threat Vector\'s route compared with the bridges\' count', "sd = jb ? itm.Dg[i] : d;", "sd = d;", ('counts',)),
    ('a reverse line shown as ✗', "return rows.push({n, ln, st: 'dup', a, b,", "return rows.push({n, ln, st: 'bad', a, b,", ('list',)),
    ('a separator line refused for a third name', "ids = [L[L.length - 1], R[0]].filter(x => x !== undefined); }",
     "const u = [...new Set([...L, ...R])]; if(u.length > 2) return rows.push({n, ln, st: 'bad', msg: 'more than two systems'}); ids = u; }", ('list',)),
    ('sovBridgeEnds empty with the switch off', "function sovBridgeEnds(){ return itBridges().ends; }", "function sovBridgeEnds(){ return itBridgeOn() ? itBridges().ends : []; }", ('list',)),
    ('Within N not told the count changed', "${itMapStKey()}|${itm.home}|${itm.jbKey || ''}|", "${itMapStKey()}|${itm.home}|", ('counts',)),
    ('the map not searched again on a change', "const jbMoved = !moved && itBridgeKey() !== itm.jbKey;", "const jbMoved = false;", ('ui',)),
    ('no curves', "  if(itm.jbKey){\n    c.strokeStyle = itMapCol('--it-bridge'", "  if(false){\n    c.strokeStyle = itMapCol('--it-bridge'", ('counts',)),
    ('a bridge step drawn straight (D13)', "if(T.adj[a].includes(b)) { c.moveTo", "if(true) { c.moveTo", ('counts',)),
    ('the setting not kept', "      if(r.bridgesOn === true) d.bridgesOn = true;", "", ('ui',)),
    ('the switch\'s row short on a phone', "@media (max-width:599px){ .it-jb .jb-on{min-height:44px;} }", "", ('phone',)),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, 'jump bridges: the list, the counts on and off, what stays by stargate, the hover, the box, storage, phone')
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
