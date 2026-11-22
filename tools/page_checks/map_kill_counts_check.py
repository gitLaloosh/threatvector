"""The Intel map's kill counts by who died (build queue 066; Project doc roadmap/kill-counts-plan.md, mockup Claude outputs/kill_counts_mockup.html).
The owner: "maybe instead of changing rings, we just represent the death count by standing? amber X [N] [N] [N]", then "Yes, counts by who died
(Recommended)", "Friendly, hostile, neutral (Recommended)" and, for the colours, "go with A".

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/map_kill_counts_check.py [index.html]   -> 'FAILURES: N' (must be 0)
    (KC_FAST=1 skips the mutants.)

Uses intel_check.py's made-up folder, mocks and names (you in 1DQ1-A); made-up kills ("Mk Pilot N", negative-free made-up ids) through the page's
own Near You path (itNearAdd), as the mockup did. Checks:
  * itMapReports' kb: the owner's example (3 friendlies lost, 5 hostiles killed, 2 neutrals killed), friendlies only, one standing only, a kill older
    than "forget reports after" dropped, a victim whose side isn't known counted as neutral; the total is their sum;
  * the label (every fillText on the map's canvas recorded): after the system's name the amber ✕, then the counts in the order friendly, hostile,
    neutral, each in its colour (--side-friendly, #f08b7e, the neutral ring grey #b9c3ca; friendly and neutral at least 15 points of lightness apart),
    a standing with none left out; the label boxes of two labelled systems don't overlap;
  * the hover: "✕ 10 kills here: 3 friendlies lost, 5 hostiles killed, 2 neutrals killed", each part in its colour class; one kill says "kill";
  * the legend: "✕ kills by who died: friendly hostile neutral", its hover naming "forget reports after";
  * Near You's badges for the same system say the same counts (unchanged);
  * the map's key changes when who died changes with the same total (a re-work of sides), and not on a redraw alone;
  * 390 px: the label and legend drawn, no sideways scroll;
  * mutants; no page errors.
"""
import sys, os, re, json, tempfile, colorsys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
_src = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
_src = _src[:_src.index('with sync_playwright() as p:')]
NS = {'__file__': os.path.join(HERE, 'intel_check.py'), '__name__': 'intel_check_prefix'}
exec(compile(_src, 'intel_check.py (first part)', 'exec'), NS)   # the made-up folder, mocks, names; its table checks run too
globals().update({k: v for k, v in NS.items() if not k.startswith('__') and k not in ('check', 'fails')})
from playwright.sync_api import sync_playwright
check = NS['check']
PAGE = open(HTML, encoding='utf-8').read()

def start(b, html, w, errs, h=1000, touch=False):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch, device_scale_factor=2 if touch else 1)
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); route(ctx)
    # every text drawn on a canvas, with its colour, so the label's pieces can be read back
    ctx.add_init_script("""(() => { const f = CanvasRenderingContext2D.prototype.fillText; window.__txt = [];
      CanvasRenderingContext2D.prototype.fillText = function(t, x, y){ if(window.__rec) window.__txt.push({t: String(t), c: String(this.fillStyle), x, y}); return f.apply(this, arguments); }; })();""")
    pg = ctx.new_page(); pg.goto('file://' + html)
    pg.evaluate("(s) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({channels: ['region.intel'], me: 95000001, range: 3, sound: false, notify: false, forget: 15})); }", SIDE)
    pg.reload(); pg.wait_for_timeout(400)
    setup_logs(pg); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg, 3200)
    pg.evaluate("() => document.querySelector('#intelPanel .it-map-box').scrollIntoView({block: 'center'})"); pg.wait_for_timeout(200)
    return ctx, pg

# made-up kills through itNearAdd (the mockup's way); A the owner's example, B friendlies only, C one hostile and one unknown side, D an old kill only
SEED = """() => {
  it.near = new Map(); itMapRefresh(true);
  const ids = itGraphGet().ids, D = itm.D, near = [];
  for(let i = 0; i < D.length && near.length < 4; i++) if(D[i] >= 1 && D[i] <= 2) near.push(ids[i]);
  let pid = 95001000, kid = 900000;
  const pilot = (side) => { const id = ++pid; return {id, name: `Mk Pilot ${id - 95001000}`, corp: 98100000 + (side === 'f' ? 1 : side === 'h' ? 2 : 9), alliance: null, side, ship: null}; };
  const kill = (sys, killers, vs, minsAgo) => { const att = killers.map(pilot), victim = pilot(vs);
    const e = {id: ++itEntryId, kind: 'kill', t: Date.now() - minsAgo * 60000, who: 'zKillboard', chan: '', raw: '', history: true, pilots: att, pairs: new Map(),
      p: {sys: [{id: sys, at: 0, k: 1}], ships: [], kw: new Set(), extra: 0, W: [], used: []},
      kill: {id: ++kid, victim, value: 5e6, solo: att.length === 1, n: att.length, ships: 0, players: att.length}};
    e.friendlyOnly = att.every(a => a.side === 'f'); e.sighting = e.friendlyOnly && vs !== 'f'; it.feed.unshift(e); itNearAdd(e, sys); };
  const many = (sys, spec) => { let m = 1; for(const [n, killers, v] of spec) for(let k = 0; k < n; k++) kill(sys, killers, v, m++); };
  const [A, B, C, Dd] = near;
  many(A, [[3, ['h', 'h'], 'f'], [5, ['f', 'f'], 'h'], [2, ['h'], 'n']]);
  many(B, [[2, ['h'], 'f']]);
  many(C, [[1, ['f'], 'h'], [1, ['h'], 'x']]);
  kill(Dd, ['h'], 'f', 3); kill(Dd, ['h'], 'f', 40);   // one fresh, one past "forget reports after" (15 min)
  itRender(true); itMapRefresh(true); itMapDraw();
  return near; }"""
REP = "(id) => { const r = itm.rep.get(itGraphGet().at.get(id)); return r ? {kb: r.kb, kills: r.kills} : null; }"
# the pieces drawn after a system's name: the texts that follow it on the same line, left to right
PIECES = """(id) => { const name = itSysName(id); window.__txt = []; window.__rec = true; itm.key = null; itMapDraw(); window.__rec = false;
  const T = window.__txt, k = T.findIndex(p => p.t === name); if(k < 0) return null;
  const y = T[k].y, row = T.filter(p => Math.abs(p.y - y) < 0.6 && p.x > T[k].x).sort((a, b) => a.x - b.x);
  const lab = itm.labels.find(l => l[0] === itGraphGet().at.get(id));
  return {pcs: row.map(p => [p.t, p.c]), box: lab ? lab.slice(1) : null}; }"""

def light(hexc):
    hexc = hexc.strip()
    m = re.match(r'#([0-9a-f]{6})$', hexc, re.I)
    if m: r, g, bb = (int(m.group(1)[q:q + 2], 16) / 255 for q in (0, 2, 4))
    else:
        n = [float(x) for x in re.findall(r'[\d.]+', hexc)[:3]]; r, g, bb = (x / 255 for x in n)
    return colorsys.rgb_to_hls(r, g, bb)[1] * 100

def norm(c):
    c = c.strip().lower()
    m = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', c)
    return '#%02x%02x%02x' % tuple(int(x) for x in m.groups()) if m else c

def cases(b, html, parts=('kb', 'label', 'tip', 'legend', 'near', 'key', 'phone')):
    out, errs = [], []
    ctx, pg = start(b, html, 1440, errs)
    if not pg.evaluate("typeof itMapReports === 'function' && !!itm.D"): out.append('no map'); ctx.close(); return out, errs
    near = pg.evaluate(SEED)
    if len(near) < 4: out.append(f'made-up kills: found {len(near)} systems 1-2 jumps away (want 4)'); ctx.close(); return out, errs
    A, B, C, Dd = near
    FR = norm(pg.evaluate("itMapCol('--side-friendly', '#4f8fe0')"))
    if 'kb' in parts:
        R = {k: pg.evaluate(REP, v) for k, v in (('A', A), ('B', B), ('C', C), ('D', Dd))}
        if not R['A'] or R['A']['kb'] != {'f': 3, 'h': 5, 'n': 2} or R['A']['kills'] != 10: out.append(f"the owner's example: {R['A']} (want 3 / 5 / 2, 10)")
        if not R['B'] or R['B']['kb'] != {'f': 2, 'h': 0, 'n': 0}: out.append(f"friendlies only: {R['B']}")
        if not R['C'] or R['C']['kb'] != {'f': 0, 'h': 1, 'n': 1}: out.append(f"a victim whose side isn't known counts as neutral: {R['C']}")
        if not R['D'] or R['D']['kb'] != {'f': 1, 'h': 0, 'n': 0} or R['D']['kills'] != 1: out.append(f"a kill older than \"forget reports after\" dropped: {R['D']}")
    if 'label' in parts:
        P = pg.evaluate(PIECES, A)
        want = [['✕', None], ['3', FR], ['5', '#f08b7e'], ['2', '#b9c3ca']]
        got = [[t, norm(c)] for t, c in (P['pcs'] if P else [])]
        kx = [g[0] for g in got].index('✕') if got and '✕' in [g[0] for g in got] else -1
        seq = got[kx:kx + 4] if kx >= 0 else []
        if len(seq) != 4 or [s[0] for s in seq] != ['✕', '3', '5', '2'] or [s[1] for s in seq[1:]] != [w[1] for w in want[1:]]:
            out.append(f"the label's pieces after the name: {got} (want ✕ then 3 {FR}, 5 #f08b7e, 2 #b9c3ca)")
        elif norm(seq[0][1]) != norm(pg.evaluate("itMapCol('--amber', '#d99a3c')")): out.append(f'the ✕ in amber: {seq[0]}')
        if abs(light(FR) - light('#b9c3ca')) < 15: out.append(f'friendly {FR} and neutral #b9c3ca under 15 points of lightness apart')
        PB = pg.evaluate(PIECES, B)
        gb = [[t, norm(c)] for t, c in (PB['pcs'] if PB else [])]
        tb = [g[0] for g in gb]
        if '✕' not in tb or tb[tb.index('✕'):tb.index('✕') + 2] != ['✕', '2'] or (len(tb) > tb.index('✕') + 2 and re.fullmatch(r'\d+', tb[tb.index('✕') + 2])) or gb[tb.index('✕') + 1][1] != FR:
            out.append(f'a standing with no deaths left out (friendlies only): {gb}')
        if P and PB and P['box'] and PB['box']:
            a, c = P['box'], PB['box']
            if a[0] < c[2] and a[2] > c[0] and a[1] < c[3] and a[3] > c[1]: out.append(f'two kill labels overlap: {a} {c}')
        elif not (P and P['box']): out.append('the example system has no label box')
    if 'tip' in parts:
        T = pg.evaluate("""(id) => { const i = itGraphGet().at.get(id); itMapTip(i, itm.Q[2 * i], itm.Q[2 * i + 1]); const tip = itm.tip;
          const ln = [...tip.querySelectorAll('.it-mkb')].map(s => [s.className, s.textContent]); return {txt: tip.textContent, ln}; }""", A)
        if '✕ 10 kills here: 3 friendlies lost, 5 hostiles killed, 2 neutrals killed' not in T['txt']: out.append(f"the hover's kill line: {T['txt'][:240]!r}")
        if T['ln'] != [['it-mkb f', '3 friendlies lost'], ['it-mkb h', '5 hostiles killed'], ['it-mkb n', '2 neutrals killed']]: out.append(f"the hover's parts and their colours: {T['ln']}")
        T1 = pg.evaluate("(id) => { const i = itGraphGet().at.get(id); itMapTip(i, itm.Q[2 * i], itm.Q[2 * i + 1]); return itm.tip.textContent; }", Dd)
        if '✕ 1 kill here: 1 friendly lost' not in T1: out.append(f'one kill: {T1[:200]!r}')
        cs = pg.evaluate("() => { const s = document.createElement('span'); s.className = 'it-mkb n'; itm.tip.appendChild(s); const c = getComputedStyle(s).color; s.remove(); return c; }")
        if norm(cs) != '#b9c3ca': out.append(f'the hover\'s neutral colour: {cs}')
        pg.evaluate("itMapTip(-1)")
    if 'legend' in parts:
        L = pg.evaluate("() => { const leg = itm.el.querySelector('.it-map-leg'), s = [...leg.querySelectorAll('span')].find(x => x.textContent.startsWith('✕')); return s ? [s.textContent.replace(/\\s+/g, ' ').trim(), s.title, [...s.querySelectorAll('.it-mkb')].map(i => getComputedStyle(i).fontStyle)] : null; }")
        if not L or L[0] != '✕ kills by who died: friendly hostile neutral': out.append(f'the legend entry: {L}')
        elif 'forget reports after' not in L[1] or 'friendlies lost, hostiles killed, neutrals killed' not in L[1] or set(L[2]) != {'normal'}: out.append(f'the legend\'s hover and words: {L}')
    if 'near' in parts:
        N = pg.evaluate("(id) => { const st = it.near.get(id); return itKillBadges(st.kills.filter(x => x.t >= Date.now() - it.set.forget * 60000), id).replace(/<[^>]+>/g, ' ').replace(/\\s+/g, ' '); }", A)
        for w in ('3 friendlies lost', '5 hostiles killed', '2 neutrals killed'):
            if w not in N: out.append(f"Near You's badges and the map disagree: {N!r} (no {w!r})")
    if 'key' in parts:
        K = pg.evaluate("""(id) => { itMapRefresh(true); const k0 = itMapKey(), k1 = itMapKey(); const st = it.near.get(id), x = st.kills.find(k => k.v === 'h');
          x.v = 'n'; itm.rep = itMapReports(); const k2 = itMapKey(); x.v = 'h'; itm.rep = itMapReports(); itMapRefresh(true); return [k0 === k1, k0 !== k2]; }""", A)
        if K != [True, True]: out.append(f'the map key: steady on a redraw {K[0]}, changes when who died changes with the same total {K[1]}')
    ctx.close()
    if 'phone' in parts:
        ctx, pg = start(b, html, 390, errs, h=844, touch=True)
        near = pg.evaluate(SEED)
        if len(near) >= 1:
            P = pg.evaluate(PIECES, near[0])
            ts = [p[0] for p in (P['pcs'] if P else [])]
            if '✕' not in ts: out.append(f'390: no kill label: {ts}')
        L = pg.evaluate("() => !![...itm.el.querySelectorAll('.it-map-leg span')].find(x => x.textContent.startsWith('✕ kills by who died'))")
        if not L: out.append('390: the legend entry')
        if not pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"): out.append('390: the page scrolls sideways')
        ctx.close()
    return out, errs

MUTANTS = [
    ('an unknown side counted as hostile', "kb[IT_KILL_WORD[x.v] ? x.v : 'n']++", "kb[IT_KILL_WORD[x.v] ? x.v : 'h']++", ('kb',)),
    ('the order changed', "for(const v of ['f', 'h', 'n']) if(r.kb[v]) pcs.push", "for(const v of ['h', 'f', 'n']) if(r.kb[v]) pcs.push", ('label',)),
    ('a zero count shown', "for(const v of ['f', 'h', 'n']) if(r.kb[v]) pcs.push", "for(const v of ['f', 'h', 'n']) if(true) pcs.push", ('label',)),
    ('the old total label', "for(const v of ['f', 'h', 'n']) if(r.kb[v]) pcs.push({t: String(r.kb[v]), col: C.kill[v], font: KF});", "pcs[pcs.length - 1].t = '✕' + r.kills;", ('label',)),
    ('the friendly count in the light badge blue', "C.kill = {f: C.friendly, h: '#f08b7e', n: C.neutral};", "C.kill = {f: '#8db8f2', h: '#f08b7e', n: C.neutral};", ('label',)),
    ('the killers\' side, not who died', "if(x.t >= keep) kb[IT_KILL_WORD[x.v] ? x.v : 'n']++;", "if(x.t >= keep) kb[side[0] === 'f' ? 'f' : side[0] === 'h' ? 'h' : 'n']++;", ('kb',)),
    ('the hover without who died', "    if(r.kills) h += `<br>${itMapKbTipHtml(r)}`;", "    if(r.kills) h += `<br><span class=\"d\">✕ ${r.kills} kills here</span>`;", ('tip',)),
    ('the map key with the total only', "${r.kb ? `${r.kb.f}.${r.kb.h}.${r.kb.n}` : r.kills}", "${r.kills}", ('key',)),
    ('old kills counted', "if(x.t >= keep) kb[", "if(true) kb[", ('kb',)),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, f'kill counts by who died on the map ({len(out)} problems)')
    check(not errs, f'no page errors ({errs[:2]})')
    if not os.environ.get('KC_FAST'):
        for name, a, bb, parts in MUTANTS:
            if PAGE.count(a) != 1: check(False, f'mutant "{name}": its text is in the page ({PAGE.count(a)})'); continue
            with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f: f.write(PAGE.replace(a, bb)); mp = f.name
            try:
                mo, me = cases(b, mp, parts)
                check(bool(mo) or bool(me), f'mutant caught: {name}' + (f' ({mo[0][:90]})' if mo else ''))
            finally: os.unlink(mp)
    b.close()
print(f'FAILURES: {NS["fails"]}')
sys.exit(1 if NS['fails'] else 0)
