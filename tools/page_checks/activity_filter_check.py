"""The Intel map's Activity (past hour) Only filter (build queue 069; roadmap/activity-filter-plan.md, mockup Claude outputs/activity_mockup.html).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/activity_filter_check.py [index.html]   -> 'FAILURES: N' (must be 0)

The owner's answers (the plan's section 7): "One filter, kind + minimum (Recommended)", "Per kind, those defaults (Recommended)", "Round numbers
1–2000 (Recommended)", "No, use 065's colours (Recommended)", "Mockup yes, raise cap (Recommended)".
Uses intel_check.py's made-up folder, mocks and names (you in 1DQ1-A) and its stand-in for ESI's /universe/system_jumps/ and
/universe/system_kills/ (LV). Every count here is made up, from the map's own systems by gate jumps from you (out to 6 jumps; the rest missing,
so 0), with a few set at the edges: exactly 50 and 49 jumps, a lone pod kill (ship + pod 1), exactly 200 and 199 NPC kills.
Checks, at 1440 px and 390 px:
  * the column: Activity (past hour) last in the Only group, its settings button;
  * the reader: nothing asked with the filter off; switched on (its settings open the first time, not the second): one jumps read and no
    kills read; none again on refreshes; the kind switched to ship + pod kills: one kills read; NPC kills: none more (the same list);
    Paths to you: not wanted;
  * the match equals the rule worked out here (at least N of the picked kind, a missing system 0) for each kind at its default and at
    other steps; your system kept; each kind keeps its own minimum across switches; a typed number goes to the nearest step;
  * the key: the list going and coming back works the match out again;
  * the Only line ("at least 50 jumps in the past hour (N) · ESI HH:MM", singular at 1) and the panel's count;
  * the hover: the picked kind's count (a missing system 0); said once with 065's matching colour on;
  * a failed read: "no data yet" in the Only line and the hover, nothing but your system matched;
  * the settings kept (tvMapStack: only.act, act, seen.act), a bad kind or an off-step number falls back, an older stack reads with the
    defaults; nothing else kept;
  * the panel inside the window, three kinds and one stepper, rows 24 px or more on a phone; at 390 px the opened column's buttons don't
    overlap and stay in the map; no sideways scroll; no page errors;
  * mutants, each must fail (see MUTANTS).
v2026.11.25.2 fails (no such filter).
"""
import sys, os, re, json, time, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
_src = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
_src = _src[:_src.index('with sync_playwright() as p:')]
NS = {'__file__': os.path.join(HERE, 'intel_check.py'), '__name__': 'intel_check_prefix'}
exec(compile(_src, 'intel_check.py (first part)', 'exec'), NS)   # the made-up folder, mocks, names
globals().update({k: v for k, v in NS.items() if not k.startswith('__') and k not in ('check', 'fails')})
from playwright.sync_api import sync_playwright
check, LV = NS['check'], NS['LV']
PAGE = open(HTML, encoding='utf-8').read()
HOME = SYSID['1DQ1-A']
D0 = bfs(HOME)
NEAR = sorted(s for s, v in D0.items() if v <= 6)
def ring(d): return sorted(s for s, v in D0.items() if v == d)
J50, J49 = ring(2)[0], ring(2)[1]
POD1, NPC200, NPC199 = ring(3)[0], ring(3)[1], ring(3)[2]
MISSING = ring(4)[0]   # in neither list
def jumps_of(sid):
    if sid == MISSING: return 0
    if sid == J50: return 50
    if sid == J49: return 49
    return (sid * 7) % 160
def kills_of(sid):   # [ship, pod, npc]
    if sid == MISSING: return [0, 0, 0]
    if sid == POD1: return [0, 1, 0]
    if sid == NPC200: return [0, 0, 200]
    if sid == NPC199: return [0, 0, 199]
    return [sid % 3 if sid % 5 == 0 else 0, 1 if sid % 7 == 0 else 0, (sid * 13) % 400]
def jumps_answer(): return [{'system_id': s, 'ship_jumps': jumps_of(s)} for s in NEAR if jumps_of(s)]   # ESI has no zero rows
def kills_answer(): return [{'system_id': s, 'ship_kills': k[0], 'pod_kills': k[1], 'npc_kills': k[2]} for s in NEAR for k in [kills_of(s)] if any(k)]
def count(sid, k):
    if sid not in NEAR: return 0
    if k == 'j': return jumps_of(sid)
    x = kills_of(sid); return x[0] + x[1] if k == 'sp' else x[2]
def expect(k, n): return {s for s in NEAR if count(s, k) >= n} | {HOME}
def nmatch(k, n): return sum(1 for s in NEAR if count(s, k) >= n)
WORD = {'j': ('jump', 'jumps'), 'sp': ('ship or pod kill', 'ship and pod kills'), 'npc': ('NPC kill', 'NPC kills')}
DEF = {'k': 'j', 'j': 50, 'sp': 1, 'npc': 200}

MATCHED = "() => { const mt = itMapMatch(), ids = itGraphGet().ids; return mt ? [...mt.m].map((v, i) => v ? ids[i] : 0).filter(Boolean) : []; }"

def start(b, html, w, errs, h=1000, touch=False):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch, device_scale_factor=2 if touch else 1)
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); route(ctx)
    pg = ctx.new_page(); pg.goto('file://' + html)
    pg.evaluate("([s]) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({nearShown: false, channels: ['region.intel'], me: 95000001, range: 3, nearRange: 8, mapReach: 10, sound: false, notify: false, forget: 15, hideFriendly: true})); }", [SIDE])
    pg.reload(); pg.wait_for_timeout(400)
    setup_logs(pg); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg)
    tick(pg, 2500)
    pg.evaluate("() => document.querySelector('#intelPanel .it-map-box').scrollIntoView({block: 'center'})"); pg.wait_for_timeout(200)
    return ctx, pg

def tipof(pg, sid): return pg.evaluate("(id) => { const i = itGraphGet().at.get(id); itMapTip(i, 40, 40); const t = itm.tip.textContent; itMapTip(-1); return t; }", sid)
def leg(pg): return pg.evaluate("() => itm.el.querySelector('.it-map-leg').textContent")
def asked(k): return LV['asked'].count(k)
def kind(pg, k):   # the panel's radio, as a press would
    pg.evaluate("(k) => { if(!itMpShown() || itMp.k !== 'act') itMpOpen('act', false); const r = itMp.el.querySelector(`[name=itMpAct][value=${k}]`); r.focus(); r.checked = true; r.dispatchEvent(new Event('change', {bubbles: true})); }", k)   # focused first, as a press is
    pg.wait_for_timeout(250)
def setmin(pg, v): pg.evaluate("(v) => { RS.mapAct.set(v); itMpChanged(); }", v); pg.wait_for_timeout(120)
def act(pg): return pg.evaluate("() => itMapSt().act")

def run(b, html, w):
    out, errs = [], []
    phone = w < 600
    LV.update(jumps=jumps_answer(), kills=kills_answer(), asked=[], status=200, expires=3600)
    ctx, pg = start(b, html, w, errs, h=1000 if not phone else 844, touch=phone)
    try:
        # ---- the column
        r = pg.evaluate("() => { const f = IT_MAP_FILTERS.map(x => x.k), o = f.filter(k => (IT_MAP_FILTERS.find(x => x.k === k) || {}).g === 'only'), b = document.querySelector('#intelPanel [data-im-f=act]'); return {last: o[o.length - 1], g: (IT_MAP_FILTERS.find(x => x.k === 'act') || {}).g, inOnly: !!(b && b.closest('.it-map-fg-only')), label: b && b.getAttribute('aria-label'), set: !!document.querySelector('#intelPanel [data-it-mpn=act]')}; }")
        if r['last'] != 'act' or r['g'] != 'only' or not r['inOnly'] or r['label'] != 'Activity (past hour)' or not r['set']: out.append(f'{w}: the column {r}')
        # ---- nothing asked while off
        pg.evaluate("() => { itMapRefresh(true); itMapDraw(); }"); pg.wait_for_timeout(300)
        if LV['asked']: out.append(f'{w}: asked with the filter off {LV["asked"]}')
        # ---- switched on: its settings open the first time; the jumps list only
        if phone: pg.evaluate("() => itMapFbarOpen(true)"); pg.wait_for_timeout(150)
        pg.evaluate("() => itMapFilterSet('act')"); pg.wait_for_timeout(600)
        if pg.evaluate("() => itMpShown() && itMp.k") != 'act': out.append(f'{w}: switched on the first time, its settings didn\'t open')
        if asked('jumps') != 1 or asked('kills'): out.append(f'{w}: switched on: {LV["asked"]} (want one jumps read, no kills read)')
        for _ in range(3): pg.evaluate("() => { itMapRefresh(true); itMpChanged(); }"); pg.wait_for_timeout(150)
        if asked('jumps') != 1: out.append(f'{w}: jumps asked again before its Expires ({asked("jumps")})')
        if act(pg) != DEF: out.append(f'{w}: the defaults {act(pg)}')
        # ---- the match per kind, the Only line, the panel's count
        def cmp(k, n, what):
            got = set(pg.evaluate(MATCHED)); want = expect(k, n)
            if got != want: out.append(f'{w}: {what}: matched {len(got)}, want {len(want)} (extra {sorted(got - want)[:4]}, missing {sorted(want - got)[:4]})')
            L = leg(pg); word = WORD[k][0] if n == 1 else WORD[k][1]
            line = f'at least {n} {word} in the past hour ({nmatch(k, n):,})'
            if line not in L or not re.search(r'· ESI \d\d:\d\d', L): out.append(f'{w}: {what}: the Only line {L[:260]!r} (want {line!r} · ESI HH:MM)')
            c = pg.evaluate("() => (itMp.el && itMp.el.querySelector('.it-mp-cnt') || {}).textContent || ''")
            if itMpOpen_shown(pg) and not c.startswith(f'{len(want) - 1} system'): out.append(f'{w}: {what}: the panel\'s count {c!r} (want {len(want) - 1})')
        cmp('j', 50, 'jumps at 50')
        if J50 not in set(pg.evaluate(MATCHED)) or J49 in set(pg.evaluate(MATCHED)): out.append(f'{w}: 50 and 49 jumps at the edge')
        setmin(pg, 100); cmp('j', 100, 'jumps at 100')
        kind(pg, 'sp')
        if asked('kills') != 1: out.append(f'{w}: ship + pod kills: {asked("kills")} kills reads (want 1)')
        if act(pg)['sp'] != 1: out.append(f'{w}: ship + pod kills didn\'t bring back its own 1 {act(pg)}')
        cmp('sp', 1, 'ship + pod at 1')
        if POD1 not in set(pg.evaluate(MATCHED)): out.append(f'{w}: a lone pod kill isn\'t a ship + pod kill')
        setmin(pg, 2); cmp('sp', 2, 'ship + pod at 2')
        kind(pg, 'npc')
        if asked('kills') != 1: out.append(f'{w}: NPC kills: the kills list asked again ({asked("kills")})')
        if act(pg)['npc'] != 200: out.append(f'{w}: NPC kills didn\'t bring back its own 200 {act(pg)}')
        shown = pg.evaluate("() => itMp.el.querySelector('.rs[data-rs=mapAct] .rs-v').value")
        if shown != '200': out.append(f'{w}: NPC kills: the stepper shows {shown!r} (want its own 200)')
        cmp('npc', 200, 'NPC at 200')
        m = set(pg.evaluate(MATCHED))
        if NPC200 not in m or NPC199 in m: out.append(f'{w}: 200 and 199 NPC kills at the edge')
        kind(pg, 'j')
        if act(pg) != {'k': 'j', 'j': 100, 'sp': 2, 'npc': 200}: out.append(f'{w}: each kind\'s own number not kept {act(pg)}')
        if pg.evaluate("() => (document.activeElement || {}).name") != 'itMpAct': out.append(f'{w}: focus not kept on the kind switch')
        # a typed number goes to the nearest step (a phone's box is read-only: its buttons step)
        if not phone: pg.evaluate("() => { const i = itMp.el.querySelector('.rs[data-rs=mapAct] .rs-v'); i.focus(); i.value = '60'; i.dispatchEvent(new Event('input', {bubbles: true})); i.blur(); }"); pg.wait_for_timeout(200)
        else: setmin(pg, 50)
        if act(pg)['j'] != 50: out.append(f'{w}: 60 typed went to {act(pg)["j"]} (want the nearest step, 50)')
        cmp('j', 50, 'jumps at 50 again')
        # ---- the key: the list going and coming back
        r = pg.evaluate(f"() => {{ const ids = () => {{ const mt = itMapMatch(), g = itGraphGet().ids; return [...mt.m].map((v, i) => v ? g[i] : 0).filter(Boolean); }}; const keep = itLv.jumps.d; itLv.jumps.d = null; const a = ids(); itLv.jumps.d = keep; const b = ids(); return [a.includes({J50}), a.length, b.includes({J50})]; }}")
        if r != [False, 1, True]: out.append(f'{w}: the match with the list gone and back {r} (want [False, 1, True])')
        # ---- the hover
        t = tipof(pg, J50)
        if '50 jumps in the past hour' not in t or not re.search(r'\(ESI, as of \d\d:\d\d EVE\)', t): out.append(f'{w}: the hover {t[:260]!r}')
        t = tipof(pg, MISSING)
        if '0 jumps in the past hour' not in t: out.append(f'{w}: the hover, a system missing from the list {t[:260]!r}')
        pg.evaluate("() => itMapFilterSet('jumph')"); pg.wait_for_timeout(300)
        t = tipof(pg, J50)
        if t.count('jumps in the past hour') != 1: out.append(f'{w}: Jumps (past hour) and Activity: said {t.count("jumps in the past hour")} times {t[:260]!r}')
        kind(pg, 'npc'); pg.evaluate("() => itMapFilterSet('killh')"); pg.wait_for_timeout(300)
        t = tipof(pg, NPC200)
        if t.count('in the past hour') != 1 or '200 NPC killed in the past hour' not in t: out.append(f'{w}: Kills (past hour) and Activity: {t[:260]!r}')
        pg.evaluate("() => itMapFilterSet('sec')"); pg.wait_for_timeout(200)
        t = tipof(pg, NPC200)
        if '200 NPC kills in the past hour' not in t: out.append(f'{w}: the hover, NPC kills {t[:260]!r}')
        kind(pg, 'j')
        # ---- second switch-on: its settings stay shut
        pg.evaluate("() => { itMpOpen('', false); itMapFilterSet('act'); itMapFilterSet('act'); }"); pg.wait_for_timeout(300)
        if pg.evaluate("() => itMpShown() && itMp.k") == 'act': out.append(f'{w}: its settings opened again on a second switch-on')
        # ---- a failed read
        LV['status'] = 503
        pg.evaluate("() => { Object.assign(itLv.jumps, {d: null, at: 0, exp: 0, next: 0, fails: 0, err: ''}); itMapRefresh(); }"); pg.wait_for_timeout(500)
        if 'activity: no data yet' not in leg(pg): out.append(f'{w}: a failed read: the Only line {leg(pg)[:220]!r}')
        if 'Activity: no data yet' not in tipof(pg, J50): out.append(f'{w}: a failed read: the hover {tipof(pg, J50)[:200]!r}')
        if set(pg.evaluate(MATCHED)) != {HOME}: out.append(f'{w}: a failed read: matched more than your system')
        LV['status'] = 200
        pg.evaluate("() => { itLv.jumps.next = 0; itMapRefresh(); }"); pg.wait_for_timeout(500)
        if J50 not in pg.evaluate(MATCHED): out.append(f'{w}: the read back: not matched')
        # ---- Paths to you: not wanted
        pg.evaluate("() => itMapFilterSet('paths')"); pg.wait_for_timeout(300)
        if pg.evaluate("() => itMapLvWant('jumps') || itMapLvWant('kills')"): out.append(f'{w}: wanted in Paths to you')
        pg.evaluate("() => itMapFilterSet('paths')"); pg.wait_for_timeout(300)
        # ---- kept: the settings, nothing else
        kind(pg, 'sp'); setmin(pg, 5)
        st = pg.evaluate("() => JSON.parse(localStorage.getItem('tvMapStack'))")
        if st.get('act') != {'k': 'sp', 'j': 50, 'sp': 5, 'npc': 200} or st['only'].get('act') is not True or st['seen'].get('act') is not True: out.append(f'{w}: kept {st.get("act")} {st["only"].get("act")} {st["seen"].get("act")}')
        if pg.evaluate("() => Object.keys(localStorage).some(k => /ship_jumps|npc_kills|system_id/.test(localStorage.getItem(k) || ''))"): out.append(f'{w}: the counts kept in localStorage')
        r = pg.evaluate("() => { const k = 'tvMapStack', keep = localStorage.getItem(k), s = JSON.parse(keep); s.act = {k: 'x', j: 60, sp: '5', npc: 200}; localStorage.setItem(k, JSON.stringify(s)); const a = itMapStackRead().act; s.act = {k: 'constructor', j: 2000, sp: 1, npc: 1}; localStorage.setItem(k, JSON.stringify(s)); const c = itMapStackRead().act; delete s.act; delete s.only.act; delete s.seen.act; localStorage.setItem(k, JSON.stringify(s)); const o = itMapStackRead(); localStorage.setItem(k, keep); return [a, c, o.act, o.only.act, o.seen.act]; }")
        if r != [DEF, {'k': 'j', 'j': 2000, 'sp': 1, 'npc': 1}, DEF, False, False]: out.append(f'{w}: a bad kind or step / an older stack {r}')
        pg.reload(); pg.wait_for_timeout(500)
        if pg.evaluate("() => [itMapSt().act, itMapSt().only.act]") != [{'k': 'sp', 'j': 50, 'sp': 5, 'npc': 200}, True]: out.append(f'{w}: not kept across a reload')
        setup_logs(pg); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.wait_for_timeout(300)
        if not pg.evaluate("() => !!(itm.el && itm.el.isConnected)"): pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg)
        pg.evaluate("() => document.querySelector('#intelPanel .it-map-box').scrollIntoView({block: 'center'})"); pg.wait_for_timeout(150)
        # ---- the panel on this width
        pg.evaluate("() => itMpOpen('act')"); pg.wait_for_timeout(250)
        r = pg.evaluate("() => { if(!itMpShown()) return null; const p = itMp.el.getBoundingClientRect(), rows = [...itMp.el.querySelectorAll('.it-sov-k')].map(l => l.getBoundingClientRect().height); return {l: p.left, r: p.right, rows, radios: itMp.el.querySelectorAll('[name=itMpAct]').length, steppers: itMp.el.querySelectorAll('.rs[data-rs]').length, h: itMp.el.querySelector('h4').textContent}; }")
        if not r: out.append(f'{w}: the panel didn\'t open')
        else:
            if r['l'] < 0 or r['r'] > w: out.append(f'{w}: the panel leaves the window {r}')
            if r['radios'] != 3 or r['steppers'] != 1 or r['h'] != 'Activity (past hour)' or (phone and min(r['rows']) < 24): out.append(f'{w}: the panel {r}')
        pg.evaluate("() => itMpOpen('', false)")
        # ---- 390 px: the opened column, every filter, nothing overlapping
        if phone:
            pg.evaluate("() => itMapFbarOpen(true)"); pg.wait_for_timeout(250)
            r = pg.evaluate("""() => { const bx = itm.box.getBoundingClientRect(), R = [...document.querySelectorAll('#intelPanel .it-map-fbtns [data-im-f]')].map(b => b.getBoundingClientRect()).filter(q => q.width);
              let over = 0; for(let i = 0; i < R.length; i++) for(let j = i + 1; j < R.length; j++){ const a = R[i], c = R[j]; if(a.left < c.right - 1 && c.left < a.right - 1 && a.top < c.bottom - 1 && c.top < a.bottom - 1) over++; }
              return {n: R.length, over, inside: R.every(q => q.left >= bx.left - 1 && q.right <= bx.right + 1 && q.top >= bx.top - 1 && q.bottom <= bx.bottom + 1), h: Math.min(...R.map(q => Math.round(q.height)))}; }""")
            if r['n'] != 16 or r['over'] or not r['inside'] or r['h'] < 44: out.append(f'390 px: the opened column {r} (want 16 buttons, none overlapping, inside the map, 44 px)')
            pg.evaluate("() => itMapFbarOpen(false)")
        if pg.evaluate("() => document.documentElement.scrollWidth > innerWidth"): out.append(f'{w}: sideways scroll')
    except Exception as e:   # a mutant can leave something the next step reads missing: that is a failure, not a crash
        out.append(f'{w}: stopped: {str(e).splitlines()[0][:160]}')
    finally:
        ctx.close()
    return out, errs

def itMpOpen_shown(pg): return pg.evaluate("() => itMpShown() && itMp.k === 'act'")

def cases(b, html, widths=(1440, 390)):
    out, errs = [], []
    for w in widths:
        o, e = run(b, html, w); out += o; errs += e
    return out, errs

MUTANTS = [
    ('the panel\'s count not following a read', "  if(itm.cv.parentNode === itm.box) itMpCountPaint();", ""),
    ('> instead of >=', "if(L.d) for(let i = 0; i < n; i++) if(itActCount(ids[i], a.k, L) >= min){", "if(L.d) for(let i = 0; i < n; i++) if(itActCount(ids[i], a.k, L) > min){"),
    ('one minimum shared by every kind', "set: (v) => { const a = itMapSt().act; a[a.k] = v; },", "set: (v) => { const a = itMapSt().act; a.j = a.sp = a.npc = v; },"),
    ('a missing system read as no data, not 0', "return k === 'j' ? x || 0 : x ?", "return k === 'j' ? x : x ?"),
    ('the key without the data flag', "|d${L.d ? 1 : 0}.${L.at}`; }", "|d${L.at}`; }"),
    ('the reader not asked for the filter', "  if((k === 'jumps' || k === 'kills') && itMapActOn() && IT_ACT_KINDS[itMapSt().act.k].lv === k) return true;", ""),
    ('both lists read whatever the kind', "if((k === 'jumps' || k === 'kills') && itMapActOn() && IT_ACT_KINDS[itMapSt().act.k].lv === k) return true;", "if((k === 'jumps' || k === 'kills') && itMapActOn()) return true;"),
    ('the hover said twice', "  if(c === (a.k === 'j' ? 'jumph' : 'killh')) return '';\n", ""),
    ('ship + pod counts ships only', "(k === 'sp' ? x[0] + x[1] : x[2])", "(k === 'sp' ? x[0] : x[2])"),
    ('its settings not opened the first time', "|| k === 'hub' || k === 'act') && !s.seen[k]", "|| k === 'hub') && !s.seen[k]"),
    ('a bad kind kept', "['j', 'sp', 'npc'].includes(a.k) ? a.k : 'j'", "a.k"),
    ('an off-step number kept', "st = (k) => IT_ACT_STEPS.includes(a[k]) ? a[k] : IT_ACT_DEF[k];", "st = (k) => Number.isInteger(a[k]) ? a[k] : IT_ACT_DEF[k];"),
    ('the stepper shows the jumps minimum for every kind', "value: () => { const a = itMapSt().act; return a[a.k]; },", "value: () => { const a = itMapSt().act; return a.j; },"),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, 'Activity (past hour): the column, the reader, the match per kind and its key, the minimums, the Only line, the hover, the stack, the panel, 390 px')
    check(not errs, f'no page errors {errs[:3]}')
    if '--no-mutants' not in sys.argv:
        for name, old, new in MUTANTS:
            if PAGE.count(old) != 1: check(False, f'mutant "{name}": its line isn\'t in the page once'); continue
            with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f:
                f.write(PAGE.replace(old, new)); mp = f.name
            try:
                mo, me = cases(b, mp, (1440,))
                check(bool(mo) or bool(me), f'mutant "{name}" fails ({(mo or me or ["nothing"])[0][:90]})')
            finally: os.unlink(mp)
    b.close()
print('FAILURES:', NS['fails'])
sys.exit(1 if NS['fails'] else 0)
