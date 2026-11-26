"""The Intel map's Sov hubs Only filter (build queue 068; roadmap/sov-hubs-plan.md, mockup Claude outputs/sov_hubs_mockup.html).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/sov_hubs_check.py [index.html]   -> 'FAILURES: N' (must be 0)

The owner's answers 2026-11-21 (the plan's section 7): "One filter, two kinds (Recommended)", "24 h fights, now for hubs (Recommended)", "Fight tags
only, filter on (Recommended)", "Every 2 min, raise cap (Recommended)", ""SOV 19:45" (Recommended)"; at the build review 2026-11-25 (section 10):
"your recommendations are fine for all of those questions" (B1-B4), and the Wormholes filter's icon the game's wormhole shape.
Uses intel_check.py's made-up folder, mocks and names (you in 1DQ1-A) and its stand-ins for ESI's /sovereignty/systems (SOV) and
/sovereignty/campaigns (CAMP). Every fight, window and alliance here is made up, from the map's own systems by gate jumps from you: six fights
2-4 jumps out (one under way, five to come, one a station freeport with two alliances taking part, one past 24 h), every system out to 8 jumps
held by the made-up alliance with a window by its ID: open now, opening in 30 minutes, opening in 3 hours, or ended an hour ago; a system in a
fight has none (as ESI).
Checks, at 1440 px and 390 px:
  * the column: Sov hubs right after Sov upgrades in the Only group, its settings button; the Wormholes filter's icon is the game's wormhole shape;
  * the reader: nothing asked with the filter off or in Paths to you; switched on (its settings open the first time, not the second): one
    campaigns read and the sovereignty read with Security as the colour; none again before 2 minutes (refreshes, settings); after them one more;
    a failed read: "no data yet" in the legend and hover, nothing matched for fights, asked again only after its wait; nothing kept in
    localStorage but the settings;
  * the match equals the rule worked out here (any ticked kind; fights within their hours or under way; windows open now or opening within
    their hours, never ended; a hub in a fight has none), for the defaults, each kind alone, 48 h, 0 h, 4 h and nothing ticked; your system kept;
  * the key: the data going and coming back, and the minute passing (a window opening with no new read), each work the match out again;
  * the Only line's counts, "under way", "no kind ticked" and "ESI HH:MM"; the panel's count;
  * the hover: under way, to come (its countdown), the defender and score, a freeport's alliances, vulnerable now with what is left, opening
    later, in a fight; with Sov holder on too the window is said once;
  * the tags: "SOV now" and "SOV HH:MM" only on fights in their hours that every Only filter picks out, none past 24 h (until 48 h is set), none
    with Fight coming up unticked or the filter off (another Only filter on);
  * the settings kept (tvMapStack: only.hub, hub, seen.hub), bad hours fall back, an older stack reads with the defaults;
  * 390 px: the panel inside the window, each tick's row 24 px or more; no sideways scroll; no page errors;
  * mutants, each must fail (see MUTANTS).
v2026.11.25.1 fails (no such filter).
"""
import sys, os, re, json, time, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
_src = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
_src = _src[:_src.index('with sync_playwright() as p:')]
NS = {'__file__': os.path.join(HERE, 'intel_check.py'), '__name__': 'intel_check_prefix'}
exec(compile(_src, 'intel_check.py (first part)', 'exec'), NS)   # the made-up folder, mocks, names
globals().update({k: v for k, v in NS.items() if not k.startswith('__') and k not in ('check', 'fails')})
from playwright.sync_api import sync_playwright
check, SOV, CAMP = NS['check'], NS['SOV'], NS['CAMP']
PAGE = open(HTML, encoding='utf-8').read()
HOME = SYSID['1DQ1-A']
D0 = bfs(HOME)
def ring(d): return sorted(s for s, v in D0.items() if v == d)
MIN, HOUR = 60, 3600
T = time.time()
iso = lambda t: time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(t))
YOURS, P1, P2 = M.ALLIANCE, M.BCM, M.CRTS
# the fights: [system, start (minutes from now), kind, defender, defender's and attackers' scores, taking part]
F_UNDER, F_SOON = ring(2)[0], ring(2)[1]
F_6H, F_21H = ring(3)[0], ring(3)[1]
F_30H, F_FREE = ring(4)[0], ring(4)[1]
FIGHTS = [(F_UNDER, -25, 'ihub_defense', YOURS, 0.45, 0.55, None), (F_SOON, 70, 'ihub_defense', YOURS, 0.6, 0.4, None), (F_6H, 365, 'tcu_defense', YOURS, 0.6, 0.4, None),
          (F_21H, 1300, 'ihub_defense', YOURS, 0.6, 0.4, None), (F_30H, 1800, 'ihub_defense', YOURS, 0.6, 0.4, None), (F_FREE, 200, 'station_freeport', None, None, None, [(P1, 0.5), (P2, 0.5)])]
FSYS = {f[0] for f in FIGHTS}
def camp_answer():
    out = []
    for n, (sid, m, k, d, ds, a, part) in enumerate(FIGHTS):
        c = {'campaign_id': 7000 + n, 'solar_system_id': sid, 'constellation_id': 20000001, 'structure_id': 1000000000 + sid, 'start_time': iso(T + m * MIN), 'event_type': k}
        if part: c['participants'] = [{'alliance_id': x, 'score': s} for x, s in part]
        else: c.update(defender_id=d, defender_score=ds, attackers_score=a)
        out.append(c)
    return out
# the windows: by the system's ID, none in a fight; [start, end] in seconds
def window(sid):
    if sid in FSYS: return None
    k = sid % 4
    return [T - HOUR, T + 2 * HOUR] if k == 0 else [T + 30 * MIN, T + 4 * HOUR] if k == 1 else [T + 3 * HOUR, T + 6 * HOUR] if k == 2 else [T - 5 * HOUR, T - HOUR]
HELD = [s for s, v in D0.items() if v <= 8]
def sov_answer():
    out = []
    for sid in HELD:
        hub = {'id': 1000000000 + sid}
        w = window(sid)
        if w: hub['vulnerability_window'] = {'start': iso(w[0]), 'end': iso(w[1])}
        out.append({'solar_system_id': sid, 'claim': {'alliance': {'alliance_id': YOURS, 'corporation_id': M.CORP, 'is_capital_system': sid == HOME, 'sovereignty_hub': hub}}})
    return {'solar_systems': out}
WOPEN = next(s for s in HELD if window(s) and s % 4 == 0 and s != HOME)
WSOON = next(s for s in HELD if window(s) and s % 4 == 1 and s != HOME)
WLATER = next(s for s in HELD if window(s) and s % 4 == 2 and s != HOME)
WENDED = next(s for s in HELD if window(s) and s % 4 == 3 and s != HOME)

def expect(now_ms, h):   # the rule, worked out here: the system ids that match (your system always does)
    now = now_ms / 1000.0
    out = {HOME}
    for sid, m, *_ in FIGHTS:
        if h['fight'] and (T + m * MIN) - now <= h['fightH'] * HOUR: out.add(sid)
    for sid in HELD:
        w = window(sid)
        if h['vuln'] and w and w[0] - now <= h['vulnH'] * HOUR and w[1] > now: out.add(sid)
    return out
def counts(now_ms, h):
    now = now_ms / 1000.0
    f = sum(1 for sid, m, *_ in FIGHTS if (T + m * MIN) - now <= h['fightH'] * HOUR)
    v = sum(1 for sid in HELD if window(sid) and window(sid)[0] - now <= h['vulnH'] * HOUR and window(sid)[1] > now)
    return f, v

REC_INIT = r"""(() => { const R = window.__rec = {on: false, texts: []}, P = CanvasRenderingContext2D.prototype, t0 = P.fillText;
  P.fillText = function(...a){ if(R.on && this.canvas.parentNode && this.canvas.parentNode.classList.contains('it-map-box')) R.texts.push(String(a[0])); return t0.apply(this, a); }; })()"""
TEXTS = "() => { const R = window.__rec; R.texts = []; R.on = true; itMapDraw(); R.on = false; return R.texts; }"
MATCHED = "() => { const mt = itMapMatch(), ids = itGraphGet().ids; return mt ? [...mt.m].map((v, i) => v ? ids[i] : 0).filter(Boolean) : []; }"
NOW = "() => Date.now()"

def start(b, html, w, errs, h=1000, touch=False):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch, device_scale_factor=2 if touch else 1)
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); ctx.add_init_script(REC_INIT); route(ctx)
    pg = ctx.new_page(); pg.goto('file://' + html)
    pg.evaluate("([s]) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({nearShown: false, channels: ['region.intel'], me: 95000001, range: 3, nearRange: 8, mapReach: 10, sound: false, notify: false, forget: 15, hideFriendly: true})); }", [SIDE])
    pg.reload(); pg.wait_for_timeout(400)
    setup_logs(pg); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg)
    tick(pg, 2500)
    pg.evaluate("() => document.querySelector('#intelPanel .it-map-box').scrollIntoView({block: 'center'})"); pg.wait_for_timeout(200)
    return ctx, pg

def tipof(pg, sid): return pg.evaluate("(id) => { const i = itGraphGet().at.get(id); itMapTip(i, 40, 40); const t = itm.tip.textContent; itMapTip(-1); return t; }", sid)
def leg(pg): return pg.evaluate("() => itm.el.querySelector('.it-map-leg').textContent")
def sethub(pg, h): pg.evaluate("(h) => { itMapSt().hub = h; itMpChanged(); }", h); pg.wait_for_timeout(120)
def asked(): return len(CAMP['asked'])
def hhmm(t): return time.strftime('%H:%M', time.gmtime(t))
DEF = {'fight': True, 'fightH': 24, 'vuln': True, 'vulnH': 0}

def run(b, html, w):
    out, errs = [], []
    phone = w < 600
    SOV.update(answer=sov_answer(), asked=[], status=200, expires=300); CAMP.update(answer=camp_answer(), asked=[], status=200)
    ctx, pg = start(b, html, w, errs, h=1000 if not phone else 844, touch=phone)
    try:
        # ---- the column
        r = pg.evaluate("() => { const f = IT_MAP_FILTERS.map(x => x.k), b = document.querySelector('#intelPanel [data-im-f=hub]'); return {order: f.indexOf('hub') - f.indexOf('sov'), g: (IT_MAP_FILTERS.find(x => x.k === 'hub') || {}).g, inOnly: !!(b && b.closest('.it-map-fg-only')), label: b && b.getAttribute('aria-label'), set: !!document.querySelector('#intelPanel [data-it-mpn=hub]'), wh: (document.querySelector('#intelPanel [data-im-f=wh] svg path') || {}).getAttribute ? document.querySelector('#intelPanel [data-im-f=wh] svg path').getAttribute('d') === WH_SWIRL : false}; }")
        if r['order'] != 1 or r['g'] != 'only' or not r['inOnly'] or r['label'] != 'Sov hubs' or not r['set']: out.append(f'{w}: the column {r}')
        if not r['wh']: out.append(f'{w}: the Wormholes filter\'s icon isn\'t the wormhole shape')
        # ---- nothing asked while off
        pg.evaluate("() => { itMapRefresh(true); itMapDraw(); }"); pg.wait_for_timeout(300)
        if asked(): out.append(f'{w}: campaigns asked with the filter off ({asked()})')
        if SOV['asked']: out.append(f'{w}: sovereignty asked with nothing needing it ({len(SOV["asked"])})')
        # ---- switched on: its settings open the first time; one read of each
        if phone: pg.evaluate("() => itMapFbarOpen(true)"); pg.wait_for_timeout(150)
        pg.evaluate("() => itMapFilterSet('hub')"); pg.wait_for_timeout(600)
        if pg.evaluate("() => itMpShown() && itMp.k") != 'hub': out.append(f'{w}: switched on the first time, its settings didn\'t open')
        if asked() != 1: out.append(f'{w}: switched on: {asked()} campaigns reads (want 1)')
        if not SOV['asked']: out.append(f'{w}: switched on: no sovereignty read (the windows come from it)')
        for _ in range(3): pg.evaluate("() => { itMapRefresh(true); itMpChanged(); }"); pg.wait_for_timeout(150)
        if asked() != 1: out.append(f'{w}: asked again before 2 minutes ({asked()})')
        pg.evaluate("() => { itCamp.exp = Date.now() - 1; itMapRefresh(); }"); pg.wait_for_timeout(400)
        if asked() != 2: out.append(f'{w}: not asked again after 2 minutes ({asked()})')
        if pg.evaluate("() => itCamp.exp - Date.now()") < 110000: out.append(f'{w}: the next read is due before 2 minutes')
        # ---- the match, the Only line, the panel's count
        for h in (DEF, dict(DEF, vuln=False), dict(DEF, fight=False), dict(DEF, vuln=False, fightH=48), dict(DEF, vuln=False, fightH=0), dict(DEF, fight=False, vulnH=4), dict(DEF, fight=False, vuln=False)):
            sethub(pg, h)
            got, now = set(pg.evaluate(MATCHED)), pg.evaluate(NOW)
            want = expect(now, h)
            if got != want: out.append(f'{w}: {h}: matched {len(got)}, want {len(want)} (extra {sorted(got - want)[:4]}, missing {sorted(want - got)[:4]})')
            L = leg(pg); f, v = counts(now, h)
            if not h['fight'] and not h['vuln']:
                if 'sov hubs: no kind ticked' not in L: out.append(f'{w}: nothing ticked: the Only line {L[:200]!r}')
            else:
                if h['fight'] and (f'a sov fight within {h["fightH"]} h ({f})' if h['fightH'] else f'a sov fight under way ({f})') not in L: out.append(f'{w}: {h}: the Only line\'s fights {L[:240]!r}')
                if h['vuln'] and (f'a hub vulnerable within {h["vulnH"]} h ({v})' if h['vulnH'] else f'a hub vulnerable now ({v})') not in L: out.append(f'{w}: {h}: the Only line\'s hubs {L[:240]!r}')
                if not re.search(r'ESI \d\d:\d\d', L): out.append(f'{w}: no "ESI HH:MM" in the Only line')
            c = pg.evaluate("() => (itMp.el && itMp.el.querySelector('.it-mp-cnt') || {}).textContent || ''")
            if not c.startswith(f'{len(want) - 1} system'): out.append(f'{w}: {h}: the panel\'s count {c!r} (want {len(want) - 1})')
        sethub(pg, DEF)
        # ---- the key: the data going and coming back; the minute passing
        r = pg.evaluate(f"() => {{ const ids = () => {{ const mt = itMapMatch(), g = itGraphGet().ids; return [...mt.m].map((v, i) => v ? g[i] : 0).filter(Boolean); }}; const keep = itCamp.d; itCamp.d = null; const a = ids(); itCamp.d = keep; const b = ids(); return [a.includes({F_SOON}), b.includes({F_SOON})]; }}")
        if r != [False, True]: out.append(f'{w}: the match with the fights gone and back {r} (want [False, True])')
        sethub(pg, dict(DEF, fight=False))
        r = pg.evaluate(f"() => {{ const ids = () => {{ const mt = itMapMatch(), g = itGraphGet().ids; return [...mt.m].map((v, i) => v ? g[i] : 0).filter(Boolean); }}; const a = ids().includes({WSOON}); const d0 = Date.now; Date.now = () => d0.call(Date) + 31 * 60000; let b; try{{ b = ids().includes({WSOON}); }} finally {{ Date.now = d0; }} return [a, b]; }}")
        if r != [False, True]: out.append(f'{w}: a window opening with no new read {r} (want [False, True])')
        sethub(pg, DEF)
        # ---- the hover
        t = tipof(pg, F_UNDER)
        if not re.search(r'Sov fight: hub defense, under way since \d\d:\d\d EVE \(2\d min\)', t) or 'defending' not in t or 'score 45 / 55' not in t or 'nodes anywhere in this constellation' not in t: out.append(f'{w}: the hover, under way {t[:300]!r}')
        if 'Hub: no vulnerability window (in a fight)' not in t: out.append(f'{w}: the hover, in a fight {t[:300]!r}')
        t = tipof(pg, F_SOON)
        if f'starts {hhmm(T + 70 * MIN)} EVE (in 1 h ' not in t or 'score 60 / 40' not in t: out.append(f'{w}: the hover, to come {t[:300]!r}')
        t = tipof(pg, F_6H)
        if 'TCU defense' not in t: out.append(f'{w}: the hover, a TCU defense {t[:200]!r}')
        t = tipof(pg, F_FREE)
        if 'station freeport' not in t or 'taking part' not in t or 'defending' in t: out.append(f'{w}: the hover, a freeport {t[:300]!r}')
        t = tipof(pg, WOPEN)
        if not re.search(r'Hub vulnerable \d\d:\d\d–\d\d:\d\d EVE \(now, [12] h \d\d min left\)', t): out.append(f'{w}: the hover, vulnerable now {t[:300]!r}')
        t = tipof(pg, WLATER)
        if not re.search(r'Hub vulnerable \d\d:\d\d–\d\d:\d\d EVE \(opens in [23] h \d\d min\)', t): out.append(f'{w}: the hover, opening later {t[:300]!r}')
        t = tipof(pg, WENDED)
        if '(ended)' not in t: out.append(f'{w}: the hover, an ended window {t[:300]!r}')
        # B4: with Sov holder's colour on too, the window once
        pg.evaluate("() => itMapFilterSet('sovh')"); pg.wait_for_timeout(300)
        t = tipof(pg, WOPEN)
        if t.count('vulnerable ') != 1 or 'Hub vulnerable' not in t: out.append(f'{w}: Sov holder and Sov hubs: the window said {t.count("vulnerable ")} times {t[:300]!r}')
        pg.evaluate("() => itMapFilterSet('hub')"); pg.wait_for_timeout(200)
        t = tipof(pg, WOPEN)
        if not re.search(r'vulnerable \d\d:\d\d–\d\d:\d\d EVE', t) or 'Hub vulnerable' in t: out.append(f'{w}: Sov holder alone: its window line {t[:300]!r}')
        pg.evaluate("() => { itMapFilterSet('sec'); itMapFilterSet('hub'); }"); pg.wait_for_timeout(300)
        if pg.evaluate("() => itMpShown() && itMp.k") == 'hub': out.append(f'{w}: its settings opened again on a second switch-on')
        # ---- the tags
        sethub(pg, DEF)
        tags = pg.evaluate("() => { const m = itHubTags(), g = itGraphGet().ids; return m ? [...m].map(([i, v]) => [g[i], v.t]) : null; }")
        want = {F_UNDER: 'SOV now', F_SOON: f'SOV {hhmm(T + 70 * MIN)}', F_6H: f'SOV {hhmm(T + 365 * MIN)}', F_21H: f'SOV {hhmm(T + 1300 * MIN)}', F_FREE: f'SOV {hhmm(T + 200 * MIN)}'}
        if not tags or dict(tags) != want: out.append(f'{w}: the tags {tags} (want {want})')
        texts = [x for x in pg.evaluate(TEXTS) if x.startswith('SOV')]
        if not texts or not set(texts) <= set(want.values()): out.append(f'{w}: drawn tags {texts}')
        sethub(pg, dict(DEF, fightH=48))
        tags = pg.evaluate("() => { const m = itHubTags(), g = itGraphGet().ids; return m ? [...m.keys()].map(i => g[i]) : []; }")
        if F_30H not in tags: out.append(f'{w}: 48 h: no tag for the fight in 30 h')
        sethub(pg, dict(DEF, fight=False))
        if [x for x in pg.evaluate(TEXTS) if x.startswith('SOV')]: out.append(f'{w}: tags with Fight coming up unticked')
        sethub(pg, DEF)
        pg.evaluate("() => { const s = itMapSt(); s.secr = {lo: -10, hi: 10}; s.only.secr = true; s.only.hub = false; itMpChanged(); }"); pg.wait_for_timeout(150)
        if [x for x in pg.evaluate(TEXTS) if x.startswith('SOV')]: out.append(f'{w}: tags with Sov hubs off (Security range on)')
        pg.evaluate("() => { const s = itMapSt(); s.only.secr = false; s.only.hub = true; itMpChanged(); }"); pg.wait_for_timeout(150)
        # ---- a failed read
        CAMP['status'] = 503
        pg.evaluate("() => { Object.assign(itCamp, {d: null, at: 0, exp: 0, next: 0, fails: 0, err: ''}); itMapRefresh(); }"); pg.wait_for_timeout(500)
        n0 = asked()
        if 'sov fights: no data yet' not in leg(pg): out.append(f'{w}: a failed read: the Only line {leg(pg)[:200]!r}')
        if 'Sov fights: no data yet' not in tipof(pg, F_SOON): out.append(f'{w}: a failed read: the hover')
        if F_SOON in pg.evaluate(MATCHED): out.append(f'{w}: a failed read: a fight matched from nothing')
        if pg.evaluate("() => itCamp.next - Date.now()") < 50000: out.append(f'{w}: a failed read: asked again within its wait')
        pg.evaluate("() => { itMapRefresh(true); itMpChanged(); }"); pg.wait_for_timeout(300)
        if asked() != n0: out.append(f'{w}: a failed read: asked again before its wait')
        CAMP['status'] = 200
        pg.evaluate("() => { itCamp.next = 0; itMapRefresh(); }"); pg.wait_for_timeout(500)
        if F_SOON not in pg.evaluate(MATCHED): out.append(f'{w}: the read back: the fight not matched')
        # ---- Paths to you: nothing asked
        pg.evaluate("() => { itMapFilterSet('paths'); itCamp.exp = 0; itMapRefresh(); }"); pg.wait_for_timeout(400)
        n1 = asked(); pg.evaluate("() => itMapRefresh()"); pg.wait_for_timeout(300)
        if asked() != n1 or pg.evaluate("() => itMapLvWant('camp')"): out.append(f'{w}: asked in Paths to you')
        pg.evaluate("() => itMapFilterSet('paths')"); pg.wait_for_timeout(300)
        # ---- kept: the settings, nothing else
        sethub(pg, {'fight': True, 'fightH': 30, 'vuln': False, 'vulnH': 2})
        st = pg.evaluate("() => JSON.parse(localStorage.getItem('tvMapStack'))")
        if st.get('hub') != {'fight': True, 'fightH': 30, 'vuln': False, 'vulnH': 2} or st['only'].get('hub') is not True or st['seen'].get('hub') is not True: out.append(f'{w}: kept {st.get("hub")} {st["only"].get("hub")} {st["seen"].get("hub")}')
        if pg.evaluate("() => Object.keys(localStorage).some(k => /campaign|defender_id|start_time/.test(localStorage.getItem(k) || ''))"): out.append(f'{w}: fights kept in localStorage')
        r = pg.evaluate("() => { const k = 'tvMapStack', keep = localStorage.getItem(k), s = JSON.parse(keep); s.hub = {fight: 'x', fightH: 99, vuln: false, vulnH: -1}; localStorage.setItem(k, JSON.stringify(s)); const a = itMapStackRead().hub; delete s.hub; delete s.only.hub; delete s.seen.hub; localStorage.setItem(k, JSON.stringify(s)); const o = itMapStackRead(); localStorage.setItem(k, keep); return [a, o.hub, o.only.hub, o.seen.hub]; }")
        if r[0] != {'fight': True, 'fightH': 24, 'vuln': False, 'vulnH': 0} or r[1] != DEF or r[2] is not False or r[3] is not False: out.append(f'{w}: bad hours / an older stack {r}')
        pg.reload(); pg.wait_for_timeout(500)
        if pg.evaluate("() => [itMapSt().hub, itMapSt().only.hub]") != [{'fight': True, 'fightH': 30, 'vuln': False, 'vulnH': 2}, True]: out.append(f'{w}: not kept across a reload')
        setup_logs(pg); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.wait_for_timeout(300)
        # ---- the panel on this width
        if not pg.evaluate("() => !!(itm.el && itm.el.isConnected)"): pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg)
        pg.evaluate("() => document.querySelector('#intelPanel .it-map-box').scrollIntoView({block: 'center'})"); pg.wait_for_timeout(150)
        pg.evaluate("() => itMpOpen('hub')"); pg.wait_for_timeout(250)
        r = pg.evaluate("() => { if(!itMpShown()) return null; const p = itMp.el.getBoundingClientRect(), rows = [...itMp.el.querySelectorAll('.it-sov-k')].map(l => l.getBoundingClientRect().height); return {l: p.left, r: p.right, rows, steppers: itMp.el.querySelectorAll('.rs[data-rs]').length}; }")
        if not r: out.append(f'{w}: the panel didn\'t open')
        else:
            if r['l'] < 0 or r['r'] > w: out.append(f'{w}: the panel leaves the window {r}')
            if r['steppers'] != 2 or len(r['rows']) != 2 or (phone and min(r['rows']) < 24): out.append(f'{w}: the panel\'s rows {r}')
        pg.evaluate("() => itMpOpen('', false)")
        if pg.evaluate("() => document.documentElement.scrollWidth > innerWidth"): out.append(f'{w}: sideways scroll')
    except Exception as e:   # a mutant can leave something the next step reads missing: that is a failure, not a crash
        out.append(f'{w}: stopped: {str(e).splitlines()[0][:160]}')
    finally:
        ctx.close()
    return out, errs

def cases(b, html, widths=(1440, 390)):
    out, errs = [], []
    for w in widths:
        o, e = run(b, html, w); out += o; errs += e
    return out, errs

MUTANTS = [
    ('started fights left out', "function itHubFight(L, now, h){ return L ? L.find(c => c.t - now <= h * 3600000) || null : null; }", "function itHubFight(L, now, h){ return L ? L.find(c => c.t > now && c.t - now <= h * 3600000) || null : null; }"),
    ('an ended window matches', "function itHubVulnIn(w, now, h){ return !!w && w[0] - now <= h * 3600000 && w[1] > now; }", "function itHubVulnIn(w, now, h){ return !!w && w[0] - now <= h * 3600000; }"),
    ('tags with the filter off', "const s = itMapSt(); if(!itMapHubOn() || !s.hub.fight", "const s = itMapSt(); if(!s.hub.fight"),
    ('the key without the data flag', "|c${itCamp.d ? 1 : 0}.${itCamp.at}|", "|c${itCamp.at}|"),
    ('the key without the minute', "|m${Math.floor(Date.now() / 60000)}`; }", "`; }"),
    ('no sovereignty read for the windows', "if((k === 'sov' || k === 'camp') && itMapHubOn()) return true;", "if(k === 'camp' && itMapHubOn()) return true;"),
    ('the window said twice', "if(c.vw && !itMapHubOn()){", "if(c.vw){"),
    ('campaigns asked on every refresh', "  if((itCamp.d && now < itCamp.exp) || now < itCamp.next) return;\n  itCampRead();", "  if(now < itCamp.next && !itCamp.d) return;\n  itCampRead();"),
    ('campaigns asked while off', "if(itCamp.busy || !itMapLvWant('camp')) return;", "if(itCamp.busy) return;"),
    ('a freeport without its alliances', "if(f.part) return f.part.length ?", "if(false) return f.part.length ?"),
    ('its settings not opened the first time', "(k === 'secr' || k === 'near' || k === 'hub' || k === 'act') && !s.seen[k]", "(k === 'secr' || k === 'near' || k === 'act') && !s.seen[k]"),   # 069: Activity's in the same line
    ('bad hours kept', "fightH: int(h.fightH, 0, 48, 24)", "fightH: h.fightH"),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, 'Sov hubs: the column, the reader, the match and its key, the Only line, the hover, the tags, the stack, the panel')
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
