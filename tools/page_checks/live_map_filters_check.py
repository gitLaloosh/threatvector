"""The Intel map's filters from live data (build queue 065; Project doc roadmap/live-map-filters-plan.md, mockup Claude outputs/live_map_filters_mockup.html).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/live_map_filters_check.py [index.html]   -> 'FAILURES: N' (must be 0)

The owner's answers 2026-11-20 (the plan's section 7 and 8): Sov holder "Switch, default standing", logos "No" over patches zoomed out, the hover
"Show both", Kills (past hour) "One filter, NPC as setting", Region pick "Box per region + search" with Select all, the phone column "Fold the fix
in" (at the build review "Yes, build the wrap now"), the ring (Q9), no distance fades for the three (Q10), soft colour "More" (Q11).
Uses intel_check.py's made-up folder, mocks and names (you in 1DQ1-A) and its stand-ins for ESI's /sovereignty/systems (SOV) and the two
hourly lists (LV). Every holder, count and level here is made up, from the map's own systems by gate jumps from you: your alliance (EXA) out to
2 jumps (its capital your system; one system at 1 jump not listed), a friendly alliance (BCM, typed) 3-4, a hostile one (CRTS, typed) 5-6, two
neutral ones 7-8 and 9-10 (NPACT's logo doesn't load), unclaimed 11-14, an NPC faction past that. Logos are a made-up 8 px picture.
The drawing is read from the map's own canvas calls (fills with their strength, strokes with their colour, drawImage, fillText), not pixels.
Checks, at 1440 px and 390 px:
  * the column: Colour 6 (Security, Jumps, Region, Sov holder, Jumps (past hour), Kills (past hour)), Only 8 (Sov hubs, build queue 068, then Region pick after Sov upgrades),
    View 1, in groups; settings buttons for Sov holder, Kills (past hour) and Region pick, none for Jumps (past hour); the desktop column's rows
    count the filters and lines (17), not the group wrappers;
  * the reader: nothing asked with Security on; Sov holder on: one sov read, none again before Expires (refreshes, draws, a setting); a failed
    read: grey everywhere (never a colour) and "no data yet" in the legend and hover, asked again only after its wait; Jumps / Kills (past hour)
    one read each (kind 'activity'), switching NPC kills asks nothing; nothing kept in localStorage; the Intel example asks nothing;
  * Sov holder by standing: yours blue, the typed friendly light blue, the typed hostile red, neutral grey, NPC faction khaki, unclaimed and not
    listed plain; per alliance (its settings): neighbouring holders differ, the reserved hues kept; the legend; the In view line with logos;
    holder lines only between two systems of one holder, in its colour; zoomed out no logo, zoomed in logos in the circles, a logo that fails
    shows its ticker, a capital its star; the hover: holder name, ticker, standing, capital, holding corporation, since, levels, ADM, window;
  * Jumps (past hour): every system's step right (absent = 0, all six used), the legend "as of", the hover; Kills (past hour): ships + pods,
    NPC kills from its settings, the legend says so, the hover's three numbers;
  * Q10: with a live colour no dot is drawn faint or faded and the legend has no faded / faint entries; Security keeps both;
  * soft colour (Q11): a system no Only filter picks keeps 80% zoomed out;
  * Region pick: switched on with none picked opens its list, nothing matches but you; a box per region, yours first; a pick matches its
    region; search narrows (dashes and spaces ignored); a second region adds; the Only line names them; Select all (every region, the dash with
    some, "Select all shown" with a search picks only those shown, unticked none); stacks with Security range; kept across a reload, an
    unknown region dropped; Clear;
  * the phone column (390 px): Colour with View under it, Only in its own column, nothing moves when a settings button shows, 44 px; a short
    map wraps Only into a second column inside the map;
  * no sideways scroll, no page errors;
  * mutants, each must fail (see MUTANTS).
v2026.11.22.1 fails (none of these filters).
"""
import sys, os, re, json, time, tempfile, base64, zlib, struct
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
_src = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
_src = _src[:_src.index('with sync_playwright() as p:')]
NS = {'__file__': os.path.join(HERE, 'intel_check.py'), '__name__': 'intel_check_prefix'}
exec(compile(_src, 'intel_check.py (first part)', 'exec'), NS)   # the made-up folder, mocks, names
globals().update({k: v for k, v in NS.items() if not k.startswith('__') and k not in ('check', 'fails')})
from playwright.sync_api import sync_playwright
check, SOV, LV = NS['check'], NS['SOV'], NS['LV']
PAGE = open(HTML, encoding='utf-8').read()
T0 = time.time()
HOME = SYSID['1DQ1-A']
YOURS, FRIEND, HOST, NEU1, NEU2 = M.ALLIANCE, M.BCM, M.CRTS, M.VOIDR, M.NPACT
SIDE2 = dict(SIDE, friendly=[{'id': FRIEND, 'name': 'Blue Coalition Member', 'kind': 'alliance'}])
D0 = bfs(HOME)
MISSING = sorted(s for s, v in D0.items() if v == 1)[0]

def holder(sid):
    d = D0.get(sid, 99)
    return YOURS if d <= 2 else FRIEND if d <= 4 else HOST if d <= 6 else NEU1 if d <= 8 else NEU2 if d <= 10 else 'u' if d <= 14 else 'f'
CORP_OF = {YOURS: M.CORP, FRIEND: 98000002, HOST: 98000003, NEU1: 98000005, NEU2: 98000007}
def sov_answer():
    out = []
    for sid in ids:
        if sid == MISSING: continue
        h = holder(sid)
        if h == 'u': c = {'unclaimed': True}
        elif h == 'f': c = {'faction': {'faction_id': 500001}}
        else: c = {'alliance': {'alliance_id': h, 'corporation_id': CORP_OF[h], 'claimed_since': '2025-03-04T11:00:00Z', 'is_capital_system': sid == HOME,
                                'development': {'military_level': 3, 'industrial_level': 2, 'strategic_level': 1, 'activity_defense_multiplier': 4.2},
                                'sovereignty_hub': {'id': 1000000000 + sid, 'vulnerability_window': {'start': '2026-11-22T18:00:00Z', 'end': '2026-11-22T22:00:00Z'}}}}
        out.append({'solar_system_id': sid, 'claim': c})
    return {'solar_systems': out}
JUMPS = {sid: (sid * 7919) % 900 for sid in ids if sid % 13}   # absent: every 13th (none that hour)
KILLS = {sid: [sid % 25, sid % 3, sid % 600] for sid in ids if sid % 11 == 0}
def png8(rgb):
    raw = b''.join(b'\x00' + bytes(rgb) * 8 for _ in range(8))
    ch = lambda t, d: struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', 8, 8, 8, 2, 0, 0, 0)) + ch(b'IDAT', zlib.compress(raw)) + ch(b'IEND', b'')
LOGO = png8((200, 60, 60))
def logos(r):
    m = re.search(r'/alliances/(\d+)/logo', r.request.url)
    if m and int(m.group(1)) != NEU2: return r.fulfill(status=200, content_type='image/png', body=LOGO)
    return r.fulfill(status=404, body='')

# the map's canvas calls, recorded while __rec.on (one draw)
REC_INIT = r"""(() => { const R = window.__rec = {on: false, fills: [], strokes: [], imgs: 0, texts: []}, P = CanvasRenderingContext2D.prototype;
  const f0 = P.fill, s0 = P.stroke, d0 = P.drawImage, t0 = P.fillText;
  P.fill = function(...a){ if(R.on && this.canvas.parentNode && this.canvas.parentNode.classList.contains('it-map-box')) R.fills.push([String(this.fillStyle), this.globalAlpha]); return f0.apply(this, a); };
  P.stroke = function(...a){ if(R.on && this.canvas.parentNode && this.canvas.parentNode.classList.contains('it-map-box')) R.strokes.push([String(this.strokeStyle), this.globalAlpha]); return s0.apply(this, a); };
  P.drawImage = function(...a){ if(R.on) R.imgs++; return d0.apply(this, a); };
  P.fillText = function(...a){ if(R.on) R.texts.push(String(a[0])); return t0.apply(this, a); }; })()"""
DRAW = "() => { const R = window.__rec; R.fills = []; R.strokes = []; R.imgs = 0; R.texts = []; R.on = true; itMapDraw(); R.on = false; return {fills: R.fills, strokes: R.strokes, imgs: R.imgs, texts: R.texts}; }"
IX = "(id) => itGraphGet().at.get(id)"

def start(b, html, w, errs, h=1000, touch=False):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch, device_scale_factor=2 if touch else 1)
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); ctx.add_init_script(REC_INIT); route(ctx)
    ctx.route(re.compile(r'https://images\.evetech\.net/alliances/.*'), logos)
    pg = ctx.new_page(); pg.goto('file://' + html)
    pg.evaluate("([s]) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({nearShown: false, channels: ['region.intel'], me: 95000001, range: 3, nearRange: 8, mapReach: 10, sound: false, notify: false, forget: 15, hideFriendly: true})); }", [SIDE2])
    pg.reload(); pg.wait_for_timeout(400)
    setup_logs(pg); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg)
    tick(pg, 2500)
    pg.evaluate("() => document.querySelector('#intelPanel .it-map-box').scrollIntoView({block: 'center'})"); pg.wait_for_timeout(200)
    return ctx, pg

def setf(pg, k): pg.evaluate("(k) => itMapFilterSet(k)", k); pg.wait_for_timeout(250)
def zoom(pg, gpx): pg.evaluate("(g) => { itMapZoom(itm.Q[2 * itm.home], itm.Q[2 * itm.home + 1], g / itMapGatePx()); itMapCenter(false); itMapDraw(); }", gpx); pg.wait_for_timeout(150)
def leg(pg): return pg.evaluate("() => itm.el.querySelector('.it-map-leg').textContent")
def legfl(pg): return pg.evaluate("() => itm.el.querySelector('.it-map-leg .it-map-fl').textContent")
def tipof(pg, sid): return pg.evaluate("(id) => { const i = itGraphGet().at.get(id); itMapTip(i, 40, 40); const t = itm.tip.textContent; itMapTip(-1); return t; }", sid)
COLS = "() => { const T = itMapTable(), ids = itGraphGet().ids, o = {}; for(let i = 0; i < T.n; i++) o[ids[i]] = itMapColRaw(i); return o; }"

def run(b, html, w, parts):
    out, errs = [], []
    phone = w < 600
    want = lambda *k: parts is None or any(x in parts for x in k)
    SOV.update(answer=None, asked=[], status=200, expires=300); LV.update(jumps=None, kills=None, asked=[], status=200, expires=3600)
    ctx, pg = start(b, html, w, errs, h=1000 if not phone else 844, touch=phone)
    try:
        # ---- the column
        if want('column'):
            keys = pg.evaluate("() => [...document.querySelectorAll('#intelPanel .it-map-fbtns [data-im-f]')].map(b => b.dataset.imF)")
            if keys != ['sec', 'jumps', 'region', 'sovh', 'jumph', 'killh', 'secr', 'near', 'reports', 'kills', 'wh', 'sov', 'hub', 'regpick', 'paths']: out.append(f'{w}: the column {keys}')   # 068: Sov hubs
            grp = pg.evaluate("() => [...document.querySelectorAll('#intelPanel .it-map-fbtns .it-map-fg')].map(g => [g.className.split(' ').pop(), g.querySelectorAll('[data-im-f]').length])")
            if grp != [['it-map-fg-colour', 6], ['it-map-fg-only', 8], ['it-map-fg-view', 1]]: out.append(f'{w}: the groups {grp}')
            names = pg.evaluate("() => ['sovh','jumph','killh','regpick'].map(k => document.querySelector(`#intelPanel [data-im-f=${k}]`).getAttribute('aria-label'))")
            if names != ['Sov holder', 'Jumps (past hour)', 'Kills (past hour)', 'Region pick']: out.append(f'{w}: names {names}')
            if not pg.evaluate("() => ['sovh','killh','regpick'].every(k => document.querySelector(`#intelPanel [data-it-mpn=${k}]`)) && !document.querySelector('#intelPanel [data-it-mpn=jumph]')"): out.append(f'{w}: settings buttons')
            if not phone:
                rows = pg.evaluate("() => document.querySelector('#intelPanel .it-map-fbtns').style.getPropertyValue('--it-flr')")
                if rows != '17': out.append(f'{w}: the column\'s rows {rows!r} (17: 15 filters and 2 lines; 068 added Sov hubs)')
                if pg.evaluate("() => getComputedStyle(document.querySelector('#intelPanel .it-map-fg-only')).display") != 'contents': out.append(f'{w}: the desktop groups aren\'t display:contents')
        # ---- the reader: nothing with Security on
        if want('read', 'sov', 'live', 'fade', 'region'):
            pg.evaluate("() => itMapRefresh(true)"); pg.wait_for_timeout(300)
            if SOV['asked'] or LV['asked']: out.append(f'{w}: asked with Security on: sov {len(SOV["asked"])}, {LV["asked"]}')
        if want('read', 'sov'):
            setf(pg, 'sovh'); pg.wait_for_timeout(500)   # the answer refused (404): a failed read
            if len(SOV['asked']) != 1: out.append(f'{w}: Sov holder on: {len(SOV["asked"])} sov read(s) (want 1)')
            cols = pg.evaluate(COLS)
            if set(cols.values()) != {'#56616b'}: out.append(f'{w}: a failed read coloured systems {sorted(set(cols.values()))[:4]}')
            if 'no data yet' not in legfl(pg): out.append(f'{w}: a failed read\'s legend: {legfl(pg)[:90]}')
            if 'no data yet' not in tipof(pg, HOME): out.append(f'{w}: a failed read\'s hover')
            nx = pg.evaluate("() => itSov.next - Date.now()")
            if not 50000 < nx <= 60500: out.append(f'{w}: the wait after a failed read {nx} ms (want 60 s)')
            pg.evaluate("() => { itMapRefresh(true); itMapDraw(); }"); pg.wait_for_timeout(300)
            if len(SOV['asked']) != 1: out.append(f'{w}: a failed read asked again at once ({len(SOV["asked"])})')
            SOV['answer'] = sov_answer()
            pg.evaluate("() => { itSov.next = 0; itMapRefresh(true); }"); pg.wait_for_timeout(1200)
            if len(SOV['asked']) != 2: out.append(f'{w}: after the wait: {len(SOV["asked"])} sov reads (want 2)')
            for _ in range(3): pg.evaluate("() => { itMapRefresh(true); itMapDraw(); }"); pg.wait_for_timeout(80)
            pg.evaluate("() => { itMapSt().sovBy = 'alliance'; itMpChanged(); itMapSt().sovBy = 'standing'; itMpChanged(); }"); pg.wait_for_timeout(200)
            if len(SOV['asked']) != 2: out.append(f'{w}: asked again before Expires ({len(SOV["asked"])})')
            if SOV['asked'][-1] != 'https://esi.evetech.net/sovereignty/systems?compatibility_date=2026-05-19': out.append(f'{w}: the sov address {SOV["asked"][-1]}')
        # ---- Sov holder by standing
        if want('sov'):
            cols = pg.evaluate(COLS)
            exp = {YOURS: '#4f8fe0', FRIEND: '#8db8f2', HOST: '#c65b4e', NEU1: '#a8b2b9', NEU2: '#a8b2b9', 'u': '#56616b', 'f': '#7a6f58'}
            bad = [(SYSNAME[s], holder(s), cols.get(str(s))) for s in ids if (exp[holder(s)] if s != MISSING else '#56616b') != cols.get(str(s))]
            if bad: out.append(f'{w}: by standing, {len(bad)} wrong, e.g. {bad[:3]}')
            fl = legfl(pg)
            if not all(x in fl for x in ['Sov holder', 'yours', 'friendly', 'neutral', 'hostile', 'NPC', 'unclaimed', 'as of']): out.append(f'{w}: legend by standing: {fl}')
            hv = pg.evaluate("() => { const e = itm.el.querySelector('.it-map-leg .it-map-hv'); return e ? [e.textContent, e.querySelectorAll('img').length] : null; }")
            if not hv or 'In view' not in hv[0] or 'EXA' not in hv[0] or hv[1] < 1: out.append(f'{w}: In view: {hv}')
            ed = pg.evaluate("() => { const X = itSovIx(); for(let e = 0; e < X.edges.length; e += 2) if(X.grp[X.edges[e]] !== X.grp[X.edges[e + 1]] || X.grp[X.edges[e]] < 0) return -1; return X.edges.length / 2; }")
            if ed <= 0: out.append(f'{w}: holder lines: {ed}')
            d = pg.evaluate(DRAW)
            if not any(c == '#4f8fe0' and a == 0.75 for c, a in d['strokes']): out.append(f'{w}: no holder line in your alliance\'s colour')
            if any(a in (0.22, 0.45) for c, a in d['fills']): out.append(f'{w}: Q10: Sov holder drew a faded or faint dot')
            if 'faint: past' in leg(pg) or 'faded: past' in leg(pg): out.append(f'{w}: Q10: the legend keeps faded / faint with Sov holder')
            soft = pg.evaluate("() => { const T = itMapTable(); for(let i = 0; i < T.n; i++) if(i !== itm.home && itMapColRaw(i) === '#c65b4e') return [itMapFcol(i), itMapMix('#c65b4e', 0.8)]; }")
            if not soft or soft[0] != soft[1]: out.append(f'{w}: soft colour not 80% {soft}')
            # zoomed in: logos, the failing logo's ticker, the capital's star
            zoom(pg, 95); pg.wait_for_timeout(600); pg.evaluate("() => { const L = itm.view; itm.view = {k: L.k, tx: L.tx, ty: L.ty}; }")
            d = pg.evaluate(DRAW)
            if d['imgs'] < 3: out.append(f'{w}: zoomed in, {d["imgs"]} logo(s)')
            if '★' not in d['texts']: out.append(f'{w}: zoomed in, no capital star')
            # a holder whose logo fails: its ticker (NPACT holds 9-10 jumps out)
            pg.evaluate("(id) => { const i = itGraphGet().at.get(id); const v = itm.view; v.tx = itMapFreeX() - itm.P[2 * i] * v.k; v.ty = itm.H / 2 - itm.P[2 * i + 1] * v.k; }", next(s for s in ids if D0.get(s) == 10))
            pg.wait_for_timeout(100); pg.evaluate(DRAW); pg.wait_for_timeout(700)
            d = pg.evaluate(DRAW)
            if 'NPACT' not in d['texts']: out.append(f'{w}: a logo that failed shows no ticker ({[t for t in d["texts"] if t.isupper()][:6]})')
            zoom(pg, 9); d = pg.evaluate(DRAW)   # zoomed out again, the logos loaded: none drawn
            if d['imgs']: out.append(f'{w}: zoomed out, {d["imgs"]} logo(s) drawn')
            t = tipof(pg, HOME); pg.wait_for_timeout(600); t = tipof(pg, HOME)
            for x in ['Example Alliance', '[EXA]', 'your alliance', '★ capital', 'held by Example Corp since 2025-03-04', 'Military 3 · Industrial 2 · Strategic 1 · ADM 4.2', 'vulnerable 18:00–22:00 EVE']:
                if x not in t: out.append(f'{w}: the hover lacks {x!r}: {t[:200]}')
            th = tipof(pg, next(s for s in ids if D0.get(s) == 5)); pg.wait_for_timeout(500); th = tipof(pg, next(s for s in ids if D0.get(s) == 5))
            if 'Crimson Tide Syndicate' not in th or 'hostile' not in th: out.append(f'{w}: a hostile holder\'s hover: {th[:160]}')
            if 'not listed' not in tipof(pg, MISSING) and 'no sovereignty listed' not in tipof(pg, MISSING): out.append(f'{w}: a system not listed: {tipof(pg, MISSING)[:120]}')
            if 'NPC faction space' not in tipof(pg, next(s for s in ids if holder(s) == 'f')): out.append(f'{w}: NPC faction hover')
            # per alliance
            pg.evaluate("() => itMpOpen('sovh')"); pg.wait_for_timeout(200)
            if not pg.evaluate("() => itMpShown() && itMp.k === 'sovh'"): out.append(f'{w}: Sov holder\'s settings don\'t open')
            else:
                pg.evaluate("() => itMp.el.querySelector('input[value=alliance]').click()"); pg.wait_for_timeout(250)
                if pg.evaluate("() => itMapSt().sovBy") != 'alliance': out.append(f'{w}: one colour per alliance not set')
                nb = pg.evaluate("() => { const T = itMapTable(), X = itSovIx(); let bad = 0; for(let i = 0; i < T.n; i++) for(const j of T.adj[i]) if(X.grp[i] >= 0 && X.grp[j] >= 0 && X.grp[i] !== X.grp[j] && itMapColRaw(i) === itMapColRaw(j)) bad++; return bad; }")
                if nb: out.append(f'{w}: per alliance, {nb} neighbouring holder pairs share a colour')
                if pg.evaluate("() => { const T = itMapTable(); for(let i = 0; i < T.n; i++) if(['#4fc3d9', '#d99a3c', '#9b7bd8', '#c98fd0'].includes(itMapColRaw(i))) return true; return false; }"): out.append(f'{w}: a reserved hue')
                if 'one per alliance' not in legfl(pg) or 'yours' not in legfl(pg): out.append(f'{w}: per alliance legend {legfl(pg)}')
                # the owner at the hand test: your alliance green, no other alliance green; no alliance (or no sov of yours): the palette as before
                gr = pg.evaluate("() => { const T = itMapTable(), X = itSovIx(), mine = X.grp[itm.home], o = []; for(let i = 0; i < T.n; i++) if(X.grp[i] >= 0 && X.grp[i] !== mine && ['#3fcf6a', '#5fbf7f', '#9fbf4f'].includes(itMapColRaw(i))) o.push(i); return [itMapColRaw(itm.home), o.length]; }")
                if gr != ['#3fcf6a', 0]: out.append(f'{w}: per alliance, yours {gr[0]} (want green #3fcf6a), {gr[1]} other systems green')
                na = pg.evaluate("() => { const a = side.rec.alliance; side.rec.alliance = null; itMpChanged(); const r = [itMapColRaw(itm.home), IT_MAP_REGION.includes(itMapColRaw(itm.home)), itm.el.querySelector('.it-map-leg .it-map-fl').textContent.includes('yours')]; side.rec.alliance = a; itMpChanged(); return r; }")
                if not na[1] or na[2]: out.append(f'{w}: no alliance: your holder\'s colour {na[0]} not from the palette, or the legend says yours')
                pg.evaluate("() => itMp.el.querySelector('input[value=standing]').click()"); pg.wait_for_timeout(200)
                pg.evaluate("() => itMpOpen('', false)")
        # ---- Jumps and Kills (past hour)
        if want('live', 'fade', 'read'):
            LV['jumps'] = [{'system_id': s, 'ship_jumps': v} for s, v in JUMPS.items()]; LV['kills'] = [{'system_id': s, 'ship_kills': k[0], 'pod_kills': k[1], 'npc_kills': k[2]} for s, k in KILLS.items()]
            setf(pg, 'jumph'); pg.wait_for_timeout(800)
            if LV['asked'].count('jumps') != 1: out.append(f'{w}: Jumps (past hour): {LV["asked"]}')
            if pg.evaluate("() => itMapSt().colour") != 'jumph': out.append(f'{w}: Jumps (past hour) isn\'t the colour')
            JH, JS = ['#5f676e', '#8f7d2c', '#cfa526', '#f5891c', '#ff5420', '#ff2433'], [0, 1, 10, 50, 150, 500]   # grey none, yellow to red (the owner's hand test)
            stp = lambda v, S: max(k for k in range(len(S)) if v >= S[k])
            cols = pg.evaluate(COLS)
            bad = [(SYSNAME[s], JUMPS.get(s, 0), cols.get(str(s))) for s in ids if cols.get(str(s)) != JH[stp(JUMPS.get(s, 0), JS)]]
            if bad: out.append(f'{w}: jumps steps, {len(bad)} wrong, e.g. {bad[:3]}')
            if len({JH[stp(JUMPS.get(s, 0), JS)] for s in ids}) != 6: out.append(f'{w}: not every jumps step used')
            fl = legfl(pg)
            if 'Jumps (past hour)' not in fl or 'as of' not in fl: out.append(f'{w}: jumps legend {fl}')
            s5 = next(s for s in ids if s in JUMPS and JUMPS[s] > 1)
            if f'{JUMPS[s5]} jumps in the past hour' not in tipof(pg, s5): out.append(f'{w}: the jumps hover')
            if '0 jumps in the past hour' not in tipof(pg, next(s for s in ids if s not in JUMPS)): out.append(f'{w}: a system not listed isn\'t 0 jumps')
            for _ in range(3): pg.evaluate("() => { itMapRefresh(true); itMapDraw(); }"); pg.wait_for_timeout(80)
            if LV['asked'].count('jumps') != 1: out.append(f'{w}: jumps asked again before Expires {LV["asked"]}')
            if want('fade', 'live'):
                d = pg.evaluate(DRAW)
                if any(a in (0.22, 0.45) for c, a in d['fills']): out.append(f'{w}: Q10: Jumps (past hour) drew a faded or faint dot')
                if 'faint: past' in leg(pg) or 'faded: past' in leg(pg): out.append(f'{w}: Q10: legend keeps faded / faint with Jumps (past hour)')
                setf(pg, 'sec')
                d = pg.evaluate(DRAW)
                if not any(a == 0.22 for c, a in d['fills']) or 'faint: past' not in leg(pg): out.append(f'{w}: Q10: Security lost its faint step or legend')
                setf(pg, 'jumph')
            setf(pg, 'killh'); pg.wait_for_timeout(800)
            if LV['asked'].count('kills') != 1: out.append(f'{w}: Kills (past hour): {LV["asked"]}')
            KH, KS, KN = ['#2a3640', '#6b4a52', '#9a4f55', '#c65b4e', '#ef8f78'], [0, 1, 2, 5, 20], [0, 1, 50, 200, 500]
            cols = pg.evaluate(COLS)
            bad = [s for s in ids if cols.get(str(s)) != KH[stp(sum(KILLS.get(s, [0, 0, 0])[:2]), KS)]]
            if bad: out.append(f'{w}: kills steps, {len(bad)} wrong')
            k1 = next(s for s in KILLS if KILLS[s][0] > 1 and KILLS[s][1] > 1)
            t = tipof(pg, k1)
            if f'{KILLS[k1][0]} ships · {KILLS[k1][1]} pods · {KILLS[k1][2]} NPC killed' not in t: out.append(f'{w}: the kills hover {t[:160]}')
            pg.evaluate("() => itMpOpen('killh')"); pg.wait_for_timeout(200)
            pg.evaluate("() => itMp.el.querySelector('input[value=npc]').click()"); pg.wait_for_timeout(250)
            if pg.evaluate("() => itMapSt().killNpc") is not True or 'NPC kills' not in legfl(pg): out.append(f'{w}: NPC kills from the panel')
            cols = pg.evaluate(COLS)
            if [s for s in ids if cols.get(str(s)) != KH[stp(KILLS.get(s, [0, 0, 0])[2], KN)]]: out.append(f'{w}: NPC kills steps')
            if LV['asked'].count('kills') != 1: out.append(f'{w}: NPC kills asked again {LV["asked"]}')
            pg.evaluate("() => { itMp.el.querySelector('input[value=ship]').click(); itMpOpen('', false); }")
            kinds = pg.evaluate("() => { const o = JSON.parse(localStorage.getItem('dscanEsiUse') || '{}'); return JSON.stringify(o); }")
            if 'activity' not in kinds: out.append(f'{w}: no "activity" kind counted in the Lookup budgets')
            setf(pg, 'sec')
        if want('read', 'sov'):
            ls = pg.evaluate("() => JSON.stringify(Object.fromEntries(Object.keys(localStorage).map(k => [k, localStorage.getItem(k)])))")
            if '2025-03-04' in ls or '"ship_jumps"' in ls or str(NEU1) in ls: out.append(f'{w}: live data kept in localStorage')
        # ---- Region pick
        if want('region'):
            setf(pg, 'sec')
            if phone: pg.evaluate("() => itMapFbarOpen(true)"); pg.wait_for_timeout(150)
            pg.evaluate("() => document.querySelector('#intelPanel [data-im-f=regpick]').click()"); pg.wait_for_timeout(300)
            if not pg.evaluate("() => itMpShown() && itMp.k === 'regpick'"): out.append(f'{w}: Region pick didn\'t open its list')
            else:
                if pg.evaluate("() => itMapMatch().list.length") != 0: out.append(f'{w}: none picked but something matches')
                nreg = pg.evaluate("() => itMp.el.querySelectorAll('[data-it-mpreg]').length"); allr = pg.evaluate("() => new Set(Array.from(itMapTable().reg)).size")
                if nreg != allr: out.append(f'{w}: {nreg} region boxes (want {allr})')
                mine = pg.evaluate("() => itMapTable().regions[itMapTable().reg[itm.home]]")
                if pg.evaluate("() => itMp.el.querySelector('[data-it-mpreg]').dataset.itMpreg") != mine: out.append(f'{w}: your region isn\'t first')
                pg.evaluate("(r) => itMp.el.querySelector(`[data-it-mpreg=\"${r}\"]`).click()", mine); pg.wait_for_timeout(200)
                cnt = pg.evaluate("() => { const T = itMapTable(), r = T.reg[itm.home]; let k = 0; for(let i = 0; i < T.n; i++) if(T.reg[i] === r && i !== itm.home) k++; return k; }")
                if pg.evaluate("() => itMapMatch().list.length") != cnt: out.append(f'{w}: your region doesn\'t match its {cnt} systems')
                other = pg.evaluate("(m) => { const R = [...new Set(Array.from(itMapTable().reg))].map(k => itMapTable().regions[k]).filter(r => r !== m && /\\s/.test(r)).sort(); return R[0]; }", mine)
                q = other.split()[0] + '-' + other.split()[1][:2]
                pg.evaluate("(q) => { const e = itMp.el.querySelector('.it-mp-rq'); e.value = q; e.dispatchEvent(new Event('input', {bubbles: true})); }", q); pg.wait_for_timeout(100)
                vis = pg.evaluate("() => [...itMp.el.querySelectorAll('[data-it-mpr]')].filter(l => !l.hidden).map(l => l.querySelector('input').dataset.itMpreg)")
                if other not in vis: out.append(f'{w}: the search {q!r} lost {other} ({vis[:4]})')
                pg.evaluate("(r) => itMp.el.querySelector(`[data-it-mpreg=\"${r}\"]`).click()", other); pg.wait_for_timeout(200)
                if pg.evaluate("() => itMapMatch().list.length") <= cnt: out.append(f'{w}: a second region adds nothing')
                only = pg.evaluate("() => (itm.el.querySelector('.it-map-leg .it-map-only') || {}).textContent || ''")
                if f'in {mine}, {other}' not in only and f'in {other}, {mine}' not in only: out.append(f'{w}: the Only line {only}')
                pg.evaluate("() => { const e = itMp.el.querySelector('.it-mp-rq'); e.value = ''; e.dispatchEvent(new Event('input', {bubbles: true})); }"); pg.wait_for_timeout(100)
                st = pg.evaluate("() => { const a = itMp.el.querySelector('[data-it-mprall]'); return [a.indeterminate, a.checked, getComputedStyle(a, '::before').visibility]; }")
                if st != [True, False, 'visible']: out.append(f'{w}: Select all with some picked {st}')
                pg.evaluate("() => itMp.el.querySelector('[data-it-mprall]').click()"); pg.wait_for_timeout(200)
                if pg.evaluate("() => itMapSt().regions.length") != allr or pg.evaluate("() => itMapMatch().list.length") != pg.evaluate("() => itMapTable().n - 1"): out.append(f'{w}: Select all doesn\'t pick every region')
                pg.evaluate("() => itMp.el.querySelector('[data-it-mprall]').click()"); pg.wait_for_timeout(150)
                if pg.evaluate("() => itMapSt().regions.length") != 0: out.append(f'{w}: unticking Select all leaves picks')
                pg.evaluate("() => { const e = itMp.el.querySelector('.it-mp-rq'); e.value = 'de'; e.dispatchEvent(new Event('input', {bubbles: true})); }"); pg.wait_for_timeout(100)
                shown = pg.evaluate("() => [...itMp.el.querySelectorAll('[data-it-mpr]')].filter(l => !l.hidden).map(l => l.querySelector('input').dataset.itMpreg)")
                if pg.evaluate("() => itMp.el.querySelector('.it-mp-rallt').textContent") != 'Select all shown': out.append(f'{w}: no "Select all shown" with a search')
                pg.evaluate("() => itMp.el.querySelector('[data-it-mprall]').click()"); pg.wait_for_timeout(150)
                if sorted(pg.evaluate("() => itMapSt().regions")) != sorted(shown) or not 2 <= len(shown) < allr: out.append(f'{w}: Select all shown picked {len(pg.evaluate("() => itMapSt().regions"))} (want the {len(shown)} shown)')
                pg.evaluate("([m, o]) => { const e = itMp.el.querySelector('.it-mp-rq'); e.value = ''; e.dispatchEvent(new Event('input', {bubbles: true})); itMapSt().regions = [m, o]; for(const b of itMp.el.querySelectorAll('[data-it-mpreg]')) b.checked = itMapSt().regions.includes(b.dataset.itMpreg); itMpChanged(); }", [mine, other])
                pg.evaluate("() => { itMpOpen('', false); const s = itMapSt(); s.only.secr = true; s.secr = {lo: -10, hi: -3}; itMpChanged(); }"); pg.wait_for_timeout(150)
                stk = pg.evaluate("([m, o]) => { const T = itMapTable(), L = itMapMatch().list; return [L.length, L.every(i => itMapSecT(i) <= -3 && [m, o].includes(T.regions[T.reg[i]]))]; }", [mine, other])
                if not stk[1] or stk[0] >= pg.evaluate("() => { const T = itMapTable(), r = new Set([T.reg[itm.home]]); let k = 0; for(let i = 0; i < T.n; i++) if(itMapSecT(i) <= -3) k++; return k; }"): out.append(f'{w}: Region pick doesn\'t stack with Security range {stk}')
                pg.evaluate("() => { itMapSt().only.secr = false; itMpChanged(); }")
                back = pg.evaluate("() => { itMapStackSave(); const s = JSON.parse(localStorage.getItem('tvMapStack')); s.regions.push('Nowhere Made Up'); localStorage.setItem('tvMapStack', JSON.stringify(s)); const o = itMapStackRead(); return [o.regions, o.only.regpick]; }")
                if sorted(back[0]) != sorted([mine, other]) or back[1] is not True: out.append(f'{w}: kept {back}')
                pg.evaluate("() => itMpOpen('regpick')"); pg.wait_for_timeout(100)
                pg.evaluate("() => itMp.el.querySelector('[data-it-mprclr]').click()"); pg.wait_for_timeout(150)
                if pg.evaluate("() => itMapSt().regions.length") or pg.evaluate("() => itMapMatch().list.length"): out.append(f'{w}: Clear left picks')
                pg.evaluate("() => itMpOpen('', false)")
            pg.evaluate("() => { itMapSt().only.regpick = false; itMpChanged(); }")
            if phone: pg.evaluate("() => itMapFbarOpen(false)")
        # ---- the phone column
        if phone and want('phone'):
            pg.evaluate("() => { itMapFilterSet('sec'); itMapFbarOpen(true); }"); pg.wait_for_timeout(250)
            r = pg.evaluate("() => { const q = (s) => document.querySelector('#intelPanel ' + s).getBoundingClientRect(); const c = q('.it-map-fg-colour'), o = q('.it-map-fg-only'), v = q('.it-map-fg-view'), m = itm.box.getBoundingClientRect(); return {c: [c.left, c.right, c.top, c.bottom], o: [o.left, o.right, o.top, o.bottom], v: [v.left, v.right, v.top, v.bottom], mb: m.bottom, mr: m.right}; }")
            if r['o'][0] < r['c'][1] - 1: out.append(f'{w}: Only isn\'t right of Colour {r}')
            if r['v'][2] < r['c'][3] - 1 or abs(r['v'][0] - r['c'][0]) > 2: out.append(f'{w}: View isn\'t under Colour {r}')
            if max(r['c'][3], r['o'][3], r['v'][3]) > r['mb'] or r['o'][1] > r['mr']: out.append(f'{w}: the column leaves the map {r}')
            x0 = pg.evaluate("() => document.querySelector('#intelPanel .it-map-fg-only').getBoundingClientRect().left")
            pg.evaluate("() => document.querySelector('#intelPanel [data-im-f=sovh]').click()"); pg.wait_for_timeout(250)
            if not pg.evaluate("() => !!document.querySelector('#intelPanel .it-map-fb.open')"): pg.evaluate("() => itMapFbarOpen(true)"); pg.wait_for_timeout(200)
            if pg.evaluate("() => getComputedStyle(document.querySelector('#intelPanel [data-it-mpn=sovh]')).display") == 'none': out.append(f'{w}: Sov holder\'s settings button hidden while on')
            x1 = pg.evaluate("() => document.querySelector('#intelPanel .it-map-fg-only').getBoundingClientRect().left")
            if abs(x1 - x0) >= 1: out.append(f'{w}: Only moved when a settings button showed ({x0} -> {x1})')
            if not pg.evaluate("() => [...document.querySelectorAll('#intelPanel .it-map-fbtns [data-im-f]')].every(b => b.getBoundingClientRect().height >= 44)"): out.append(f'{w}: buttons under 44 px')
            # a short map: Only wraps into another column, still inside the map
            pg.evaluate("() => { itm.H = 330; itm.ctlKey = null; itMapCtlPlace(); }"); pg.wait_for_timeout(150)
            r2 = pg.evaluate("() => { const o = document.querySelector('#intelPanel .it-map-fg-only'), bs = [...o.querySelectorAll(':scope > *')].map(e => e.getBoundingClientRect()); return [new Set(bs.map(b => Math.round(b.left))).size, Math.max(...bs.map(b => b.bottom)) - itm.box.getBoundingClientRect().top]; }")
            if r2[0] < 2 or r2[1] > 330 + 1: out.append(f'{w}: a short map: Only in {r2[0]} column(s), bottom {r2[1]:.0f} (want 2+, inside 330)')
            pg.evaluate("() => { itMapFilterSet('sec'); itMapFbarOpen(false); itMapRefresh(true); }")
        if pg.evaluate("() => document.documentElement.scrollWidth > innerWidth"): out.append(f'{w}: sideways scroll')
    finally:
        ctx.close()
    return out, errs

def cases(b, html, parts=None):
    out, errs = [], []
    for w in (1440, 390):
        o, e = run(b, html, w, parts); out += o; errs += e
    return out, errs

MUTANTS = [
    ('a system missing from the hour\'s list read as no data', "v[i] = val; col[i] = P[itMapLvStep(val, S)]; }", "v[i] = val; col[i] = x === undefined ? IT_MAP_PLAIN : P[itMapLvStep(val, S)]; }", ('live',)),
    ('jumps asked again before Expires', "  if((L.d && now < L.exp) || now < L.next) return;\n  itLvRead(k);", "  if(now < L.next) return;\n  itLvRead(k);", ('live',)),
    ('sov asked on every draw', "if((itSov.sys && now < itSov.exp) || now < itSov.next) return;", "if(now < itSov.next && !itSov.sys) return;", ('read',)),
    ('a failed read coloured from nothing', "  if(c === 'sovh'){\n    const X = itSovIx();\n    if(X){", "  if(c === 'sovh'){\n    const X = itSovIx();\n    if(!X) col.fill(IT_MAP_SOVC.n);\n    if(X){", ('read',)),
    ('Region pick ignoring the stack', "    if(ok && rg) ok = rg.has(T.reg[i]);", "    if(rg) ok = rg.has(T.reg[i]);", ('region',)),
    ('the fade skipped for every colour', "noFade = itMapNoFade(), alpha", "noFade = true, alpha", ('fade',)),
    ('the live colours faded', "noFade = itMapNoFade(), alpha", "noFade = false, alpha", ('fade',)),
    ('holder lines between any two held systems', "if(j > i && grp[j] === grp[i]) edges.push(i, j);", "if(j > i && grp[j] >= 0) edges.push(i, j);", ('sov',)),
    ('by standing not from your standings', "st = s.sovBy === 'standing' ? X.als.map(itSovSideOf) : null;", "st = s.sovBy === 'standing' ? X.als.map(() => 'n') : null;", ('sov',)),
    ('no ticker for a logo that failed', "else { const o = itSovOrg('alliance', al); if(o && o.ticker){", "else { const o = null; if(o && o.ticker){", ('sov',)),
    ('a logo zoomed out', "  itMapLvPrep();   // 065", "  itMapLvPrep(); if(itm.lvCol && itm.lvCol.c === 'sovh' && itm.lvCol.data) for(const a of itSovIx().als.slice(0, 4)){ const im = itSovLogo(a); if(im) c0dummy(im); }   // 065", ('sov',)),
    ('an unknown region kept', "o.regions = [...new Set(s.regions.filter(r => typeof r === 'string' && R.includes(r)))]; }", "o.regions = [...new Set(s.regions.filter(r => typeof r === 'string'))]; }", ('region',)),
    ('Select all ignores the search', "      const shown = [...p.querySelectorAll('[data-it-mpr]')].filter(l => !l.hidden).map(l => l.querySelector('input'));", "      const shown = [...p.querySelectorAll('[data-it-mpr]')].map(l => l.querySelector('input'));", ('region',)),
    ('no dash with some picked', "  all.checked = !!shown.length && on === shown.length; all.indeterminate = on > 0 && on < shown.length;", "  all.checked = !!shown.length && on === shown.length; all.indeterminate = false;", ('region',)),
    ('Region pick not opening its list', "    else if(k === 'regpick' && !s.regions.length) open = 'regpick';", "", ('region',)),
    ('the phone column not by group', "    .it-map-fbtns .it-map-fg-only{grid-column:2; grid-row:1 / span 2;", "    .it-map-fbtns .it-map-fg-only{grid-column:1; grid-row:3;", ('phone',)),
    ('no wrap on a short phone map', "grid-template-rows:repeat(var(--it-flr, 12), auto); grid-auto-columns:92px;", "grid-template-rows:none; grid-auto-flow:row; grid-auto-columns:92px;", ('phone',)),
    ('the rows counted from the group wrappers', "set('--it-flr', itMapFlRows(H, top, false, itMapFbN(bs)));", "set('--it-flr', itMapFlRows(H, top, false, bs.children.length));", ('column',)),
    ('soft colour back to 55%', "const IT_MAP_SOFT = 0.8,", "const IT_MAP_SOFT = 0.55,", ('sov',)),
    ('your alliance not green per alliance', "const c = Array.from(k, (v, g) => g === g0 ? IT_MAP_SOV_MINE : P[v]);", "const c = Array.from(k, (v, g) => P[Math.max(0, v)]);", ('sov',)),
    ('another alliance green per alliance', "IT_MAP_SOV_PAL = IT_MAP_REGION.filter(c => c !== '#5fbf7f' && c !== '#9fbf4f');", "IT_MAP_SOV_PAL = IT_MAP_REGION;", ('sov',)),
    ('the hover without the development levels', "if(d){ const p = [['Military', d.m]", "if(false){ const p = [['Military', d.m]", ('sov',)),
]
# the "logo zoomed out" mutant needs a drawImage on the live canvas: draws the logo once at the top left whenever Sov holder is on
MUTANTS[10] = ('a logo zoomed out', "  itSovGatesDraw(c, X, Y, on, big, W, H);   // 065", "  itSovGatesDraw(c, X, Y, on, big, W, H); if(itm.lvCol && itm.lvCol.c === 'sovh' && itm.lvCol.data) for(const im of itSovLogoC.values()) if(im.ok){ c.drawImage(im, 0, 0, 4, 4); break; }   // 065", ('sov',))

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, 'live-data map filters: the column, the reader, Sov holder, Jumps and Kills (past hour), Q10, soft colour, Region pick, the phone column')
    check(not errs, f'no page errors {errs[:3]}')
    if '--no-mutants' not in sys.argv:
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
