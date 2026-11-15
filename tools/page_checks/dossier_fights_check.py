"""Pilot Dossier read by fights (build queue 049; Project doc roadmap/dossier-fights-plan.md, its section 10 and the build review's 13).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/dossier_fights_check.py [index.html]   -> 'FAILURES: N' (must be 0)

The owner, 2026-11-14: "their newest 50 kills and 30 losses could be accounted for in two or three hulls over a weekend or a week. so
you get nothing useful about the pilot when they're out roaming with a small gang between large alliance fleets." The real page with
ESI answered from sa_mocks.py and zKillboard's pilot lists answered here the way zKillboard answers (plan rows Z1-Z3): each item the
whole killmail plus its zkb object, 200 a page, newest first, /page/N/. Made-up pilots (every name and id invented; wingmates' ids are
never looked up), killmail ids growing with time (LESSON #129). Expected numbers are worked out here from the made-up kills:
  * "Mk War Pilot": 200 kills on page 1 (a 140-pilot battleship fleet with an NPC on each kill, 15 small-gang roams of 4 kills, 20 solo kills): page 1 only,
    36 fights, the heading "200 kills in 36 fights, 3 losses", Typhoon 1 fight / Svipul 15 / Retribution 20, Solo 20 and Small gang 60
    filled, 0 ESI killmail reads (the Last kill line too), losses from a year back only (4 older Loki losses left out, no Loki row);
  * "Mk Fleet Pilot": 600 kills of one fleet, 15 minutes apart: 3 kill pages, then it stops ("600 kills in 1 fight");
  * "Mk Quiet Pilot": 130 kills, 5 of them sent without their killmail: 1 page, those 5 read from ESI (the fallback), 130 kills;
  * "Mk Year Pilot": a full page whose oldest kills are over a year old: page 1 only, the 150 of the past year counted, 5 of 20 losses;
  * "Mk Old Pilot": nothing in the past year: the kills and losses read are shown, "(none in the past year)" (build review Q7);
  * "Mk Big Pilot": 70 kills of 2,000 attackers (a page over 20 MB of JSON): no page 2 ("a large page"), each kill kept under 4 KB,
    its fleet still one fight, a loss of 2,000 attackers kept as the victim and 20 attackers, the dossier drawn after the answer;
  * the fight rule (pdFights on made-up trimmed kills): the pilot left out; 1 shared pilot for kills with 1-2 others, else 2; 3 hours;
  * page 1 first: the dossier is drawn ("reading older kills…") while page 2 is held, then redrawn once; a new pilot meanwhile
    stops the reading (no page 3, the new pilot's dossier stays);
  * System Analyzer rows (saPilotData): all of page 1 (200 kills, not 50), 2 zKillboard requests, 0 ESI killmail reads;
  * stored data: lists in the zkb store under 't:' + the address, trimmed; the cap: under 50 MB nothing deleted; over it the killmails
    used longest ago are deleted to under 40 MB, once a page load (a figure lagging behind deletes nothing more), expired zkb entries
    deleted, types / groups / orgs untouched; the older page (main before 049) reads its
    own entries after this page wrote its own;
  * mutants, each must fail: whole killmails kept; the pilot counted among his wingmates; no 3-hour window; 50 kills read; an ESI read
    despite a whole item; no size stop; no year limit;
  * no page errors.
v2026.11.14.1 fails (the dossier reads its newest 50 kills and 30 losses from ESI).
"""
import sys, os, re, json, time, hashlib, tempfile, subprocess, calendar
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
from playwright.sync_api import sync_playwright
import sa_mocks as M

HTML = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith('--')), os.path.join(HERE, '..', '..', 'index.html')))
NO_MUT = '--no-mutants' in sys.argv
fails = 0
def check(ok, msg):
    global fails
    print(('OK   ' if ok else 'FAIL ') + msg); fails += not ok
B = M.byname
NOW = time.time()
DAY = 86400
def iso(t): return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(t))

# ---- made-up pilots and their killmails ----
CORP = 98000041   # Third Party Corp (Random Third Party): made up in sa_mocks
VICTIMS = [i for i, v in M.PILOTS.items() if v[1] == 98000013][:4]   # Lantern Bay Traders: made up
P = {}   # name -> id
for k, nm in enumerate(['Mk War Pilot', 'Mk Fleet Pilot', 'Mk Quiet Pilot', 'Mk Year Pilot', 'Mk Old Pilot', 'Mk Big Pilot', 'Mk Next Pilot']):
    cid = 93000001 + k; P[nm] = cid; M.PILOTS[cid] = (nm, CORP); M.NAME_ID[nm.lower()] = cid
LISTS = {}   # (kind, cid) -> killmails, newest first (whole, with zkb)
STUB = set()   # killmail ids sent without their killmail (the fallback)
KM_ESI = {}    # what ESI answers for them
def att(cid, ship, final=False, dmg=100, weapon=None):
    a = {'character_id': cid, 'corporation_id': CORP, 'alliance_id': M.THIRD, 'damage_done': dmg, 'final_blow': final, 'security_status': 0, 'ship_type_id': ship}
    if weapon: a['weapon_type_id'] = weapon
    return a
def victim(k):
    c = VICTIMS[k % len(VICTIMS)]
    return {'character_id': c, 'corporation_id': 98000013, 'ship_type_id': B['Ferox'], 'damage_taken': 1000, 'items': [], 'position': {'x': 0, 'y': 0, 'z': 0}}
def build(cid, kills, losses):
    """kills: [(t, pilot hull, [(mate id, mate hull)], npc)]; losses: [(t, golden hull, n attackers)]. Ids grow with time."""
    ev = sorted([('k', x) for x in kills] + [('l', x) for x in losses], key=lambda e: e[1][0])
    ks, ls = [], []
    for kind, x in ev:
        kid = M._kid[0] = M._kid[0] + 1
        if kind == 'k':
            t, hull, mates, npc = x
            a = [att(cid, B[hull], True, 300)] + [att(m, B[h]) for m, h in mates] + ([{'corporation_id': 1000125, 'damage_done': 5, 'final_blow': False, 'security_status': 0, 'ship_type_id': B['Ferox']}] if npc else [])
            km = {'killmail_id': kid, 'killmail_time': iso(t), 'solar_system_id': 30000142, 'victim': victim(kid), 'attackers': a}
            ks.append(km)
        else:
            t, hull, n = x
            v = json.loads(json.dumps(M.GOLDEN[M.GF[hull]]['killmail']['victim']))
            v.update(character_id=cid, corporation_id=CORP, alliance_id=M.THIRD, damage_taken=1000, position={'x': 0, 'y': 0, 'z': 0})
            km = {'killmail_id': kid, 'killmail_time': iso(t), 'solar_system_id': 30000142, 'victim': v,
                  'attackers': [att(VICTIMS[0], B['Ferox'], True, 900)] + [att(94000000 + j, B['Ferox'], False, 10 + j) for j in range(n - 1)]}
            ls.append(km)
        M.KM[kid] = km; M.H[kid] = hashlib.sha1(str(kid).encode()).hexdigest()
    LISTS[('kills', cid)] = ks[::-1]; LISTS[('losses', cid)] = ls[::-1]
GOLD = {'Curse', 'Vedmak', 'Loki'}
# Mk War Pilot: 120 fleet kills a minute apart, 140 players, 2 days ago; 15 roams of 4 kills with 3 mates of their own; 20 solo kills
FLEET = [(95100000 + i, 'Scimitar' if i % 10 == 0 else 'Typhoon') for i in range(139)]
war = [(NOW - 2 * DAY + i * 60, 'Typhoon', FLEET, True) for i in range(120)]
for f in range(15):
    mates = [(95200000 + f * 10 + j, 'Svipul') for j in range(3)]
    war += [(NOW - (5 + 4 * f) * DAY + i * 600, 'Svipul', mates, False) for i in range(4)]
war += [(NOW - (3.3 + 3.1 * i) * DAY, 'Retribution', [], True) for i in range(20)]
build(P['Mk War Pilot'], war, [(NOW - 2.5 * DAY, 'Curse', 30), (NOW - 10 * DAY, 'Curse', 30), (NOW - 20 * DAY, 'Vedmak', 30)]
      + [(NOW - (800 + 30 * i) * DAY, 'Loki', 5) for i in range(4)])
# Mk Fleet Pilot: 600 kills, 15 minutes apart, the same 20 mates: one fight, read to the 3-page cap
FM = [(95300000 + i, 'Hurricane') for i in range(20)]
build(P['Mk Fleet Pilot'], [(NOW - 7 * DAY + i * 900, 'Hurricane', FM, False) for i in range(600)], [(NOW - 3 * DAY, 'Curse', 4)])
# Mk Quiet Pilot: 130 kills in 3 roams; 5 sent without their killmail
qk = []
for f in range(3):
    mates = [(95400000 + f * 10 + j, 'Svipul') for j in range(4)]
    qk += [(NOW - (10 + 20 * f) * DAY + i * 300, 'Svipul', mates, False) for i in range(43 + (1 if f == 0 else 0))]
build(P['Mk Quiet Pilot'], qk, [(NOW - 4 * DAY, 'Vedmak', 3)])
for km in LISTS[('kills', P['Mk Quiet Pilot'])][10:15]: STUB.add(km['killmail_id'])
# Mk Year Pilot: 150 kills of one chain in the past year, 50 of another over a year ago; 5 recent losses, 15 old
yk = [(NOW - 30 * DAY + i * 1800, 'Hurricane', FM[:5], False) for i in range(150)] + [(NOW - 450 * DAY + i * 1800, 'Hurricane', FM[5:10], False) for i in range(50)]
build(P['Mk Year Pilot'], yk, [(NOW - (5 + i) * DAY, 'Curse', 3) for i in range(5)] + [(NOW - (500 + 10 * i) * DAY, 'Loki', 3) for i in range(15)])
# Mk Old Pilot: everything two years old
build(P['Mk Old Pilot'], [(NOW - (700 + i) * DAY, 'Retribution', [], False) for i in range(30)], [(NOW - (720 + i) * DAY, 'Curse', 3) for i in range(3)])
# Mk Big Pilot: 70 structure-sized kills (2,000 attackers) in 70 minutes, 130 small kills in one chain; a loss with 2,000 attackers
BIG = [(96000000 + i, 'Typhoon') for i in range(1999)]
SM = [(95500000 + i, 'Svipul') for i in range(5)]
build(P['Mk Big Pilot'], [(NOW - 1 * DAY + i * 60, 'Typhoon', BIG, False) for i in range(70)] + [(NOW - 5 * DAY + i * 1200, 'Svipul', SM, False) for i in range(130)],
      [(NOW - 2 * DAY, 'Curse', 2000)])
# Mk Next Pilot: a few kills (the pilot asked for while another's older pages are read)
build(P['Mk Next Pilot'], [(NOW - (1 + i) * DAY, 'Retribution', [], False) for i in range(5)], [])

def item(km):
    if km['killmail_id'] in STUB: return {'killmail_id': km['killmail_id'], 'zkb': {'hash': M.H[km['killmail_id']], 'totalValue': 1e6}}
    return dict(km, zkb={'hash': M.H[km['killmail_id']], 'totalValue': 1e6, 'npc': False, 'solo': False, 'awox': False, 'labels': []})
BODY = {}
def page_body(kind, cid, page):
    k = (kind, cid, page)
    if k not in BODY: BODY[k] = json.dumps([item(x) for x in LISTS[(kind, cid)][(page - 1) * 200: page * 200]], separators=(',', ':'))
    return BODY[k]
CALLS, ESI_KM, HELD = [], [], []
HOLD = {'on': None}   # (cid, page) whose answer is held until the check lets it go
def zkb(route):
    url = route.request.url
    m = re.search(r'/(kills|losses)/characterID/(\d+)/(?:shipTypeID/(\d+)/)?(?:page/(\d+)/)?$', url)
    if m and (m.group(1), int(m.group(2))) in LISTS:
        kind, cid, st, page = m.group(1), int(m.group(2)), m.group(3), int(m.group(4) or 1)
        CALLS.append((kind, cid, page, st))
        body = page_body(kind, cid, page) if not st else json.dumps([item(x) for x in LISTS[(kind, cid)] if x['victim']['ship_type_id'] == int(st)])
        if HOLD['on'] == (cid, page): HELD.append((route, body)); return
        return route.fulfill(status=200, content_type='application/json', headers={'access-control-allow-origin': '*'}, body=body)
    return M.zkb(route)
def esi(route):
    m = re.search(r'/killmails/(\d+)/([^/]+)/', route.request.url)
    if m: ESI_KM.append(int(m.group(1)))
    return M.esi(route)
def routes(ctx):
    M.route(ctx)
    ctx.route(re.compile(r'https://zkillboard\.com/.*'), zkb)
    ctx.route(re.compile(r'https://esi\.evetech\.net/.*'), esi)

def idle(pg):
    pg.wait_for_function("() => !document.querySelector('#fitBtn').disabled && document.querySelector('#pilotBusy').hidden", timeout=180000); pg.wait_for_timeout(300)
def read_done(pg):
    pg.wait_for_function("() => pd.d && !pd.reading", timeout=180000); pg.wait_for_timeout(200)
def analyze(pg, name, wait=True):
    pg.eval_on_selector('#tabBtnPilot', 'b => b.click()'); pg.fill('#pilotName', name); pg.fill('#manualShip', ''); pg.click('#fitBtn'); pg.wait_for_timeout(300)
    if wait: idle(pg); read_done(pg)
HEAD = "() => document.querySelector('#pilotDossier .pd-head .ctx').textContent"
HEAD_T = "() => document.querySelector('#pilotDossier .pd-head .ctx').title"
ROWS = """() => Object.fromEntries([...document.querySelectorAll('#pilotDossier button.pd-row')].map(b => [b.querySelector('.pd-hull .nm').firstChild.textContent,
  [[...b.querySelector('.pd-n.k').childNodes].filter(n => !(n.classList && n.classList.contains('pd-fights'))).map(n => n.textContent).join(''),
   (b.querySelector('.pd-fights') || {}).textContent || '', (b.querySelector('.pd-fights') || {}).title || '']]))"""
SEG = "() => Object.fromEntries([...document.querySelectorAll('#pilotDossier [data-pd-mode]')].map(b => [b.dataset.pdMode, b.querySelector('b').textContent]))"
def kpages(cid): return sorted(p for k, c, p, st in CALLS if k == 'kills' and c == cid and not st)

def new_ctx(b, errs, w=1440):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': 1000})
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e)))); routes(ctx); return ctx

def s_war(b, html):
    out, errs = [], []
    ctx = new_ctx(b, errs); pg = ctx.new_page(); pg.goto('file://' + html)
    CALLS.clear(); ESI_KM.clear()
    cid = P['Mk War Pilot']; analyze(pg, 'Mk War Pilot')
    h, rows, seg, tip = pg.evaluate(HEAD), pg.evaluate(ROWS), pg.evaluate(SEG), pg.evaluate(HEAD_T)
    if not h.startswith('200 kills in 36 fights, 3 losses, '): out.append(f'War: the heading {h!r}, want "200 kills in 36 fights, 3 losses, …"')
    if 'stopped at 15 fights' not in tip: out.append(f'War: the heading\'s hover says why it stopped {tip!r}')
    want = {'Typhoon': ['120', '1 fight'], 'Svipul': ['60', '15 fights'], 'Retribution': ['20', '20 fights']}
    for hull, w in want.items():
        if (rows.get(hull) or [None, None])[:2] != w: out.append(f'War: the {hull} row {rows.get(hull)}, want {w}')
    if 'kills from 15 separate fights' not in (rows.get('Svipul') or ['', '', ''])[2]: out.append(f"War: the fights line's hover {rows.get('Svipul')}")
    if 'Loki' in rows: out.append('War: a hull lost only over a year ago is listed (Loki)')
    if seg != {'all': '200', 'solo': '20', 'small': '60', 'fleet': '120'}: out.append(f'War: the switch {seg}')
    if kpages(cid) != [1]: out.append(f'War: kill pages read {kpages(cid)}, want [1]')
    if ESI_KM: out.append(f'War: {len(ESI_KM)} ESI killmail reads, want 0')
    lk = pg.evaluate("() => (document.querySelector('#lastKillInfo .lk-att-head .lk-label') || {}).textContent || ''")
    if lk != '140 other attackers': out.append(f'War: the Last kill line from the list, its attackers {lk!r}')
    # the zkb store holds the trimmed lists under 't:' + the address
    st = pg.evaluate("""async (cid) => { const db = await openDscanCacheDb(); const get = (k) => new Promise(r => { const q = db.transaction('zkb').objectStore('zkb').get(k); q.onsuccess = () => r(q.result); });
      const t = await get('t:' + ZKB + '/kills/characterID/' + cid + '/'), plain = await get(ZKB + '/kills/characterID/' + cid + '/');
      return [t ? t.data.data.length : null, t ? t.data.data.every(x => x.tk) : false, !!plain, t ? JSON.stringify(t.data).length : 0]; }""", cid)
    if st[:3] != [200, True, False]: out.append(f"War: the zkb store's trimmed page under 't:' {st}")
    ctx.close(); return out, errs

def s_pages(b, html):
    out, errs = [], []
    ctx = new_ctx(b, errs); pg = ctx.new_page(); pg.goto('file://' + html)
    CALLS.clear(); ESI_KM.clear()
    cid = P['Mk Fleet Pilot']; analyze(pg, 'Mk Fleet Pilot')
    h, tip = pg.evaluate(HEAD), pg.evaluate(HEAD_T)
    if kpages(cid) != [1, 2, 3] or not h.startswith('600 kills in 1 fight, 1 loss, ') or 'stopped at 3 pages' not in tip: out.append(f'Fleet: 3 pages read {kpages(cid)}, the heading {h!r}, {tip[:120]!r}')
    CALLS.clear(); cid = P['Mk Quiet Pilot']; analyze(pg, 'Mk Quiet Pilot')
    h, tip = pg.evaluate(HEAD), pg.evaluate(HEAD_T)
    stub = sorted(STUB)
    if kpages(cid) != [1] or not h.startswith('130 kills in 3 fights, 1 loss, ') or 'stopped at all their kills' not in tip: out.append(f'Quiet: 1 page {kpages(cid)}, the heading {h!r} {tip[:120]!r}')
    if sorted(ESI_KM) != stub: out.append(f'Quiet: the 5 sent without their killmail read from ESI {sorted(ESI_KM)} want {stub}')
    CALLS.clear(); ESI_KM.clear(); cid = P['Mk Year Pilot']; analyze(pg, 'Mk Year Pilot')
    h, tip, seg = pg.evaluate(HEAD), pg.evaluate(HEAD_T), pg.evaluate(SEG)
    y0 = time.gmtime(NOW - 30 * DAY)
    if kpages(cid) != [1] or not h.startswith('150 kills in 1 fight, 5 losses, ') or 'stopped at a year back' not in tip or seg['all'] != '150': out.append(f'Year: page 1, the past year only {kpages(cid)} {h!r} {seg} {tip[:120]!r}')
    span = h.split(', ', 2)[2] if h.count(', ') >= 2 else ''
    if str(time.gmtime(NOW - 450 * DAY).tm_year) in span and time.gmtime(NOW - 450 * DAY).tm_year != y0.tm_year: out.append(f'Year: the span reaches past a year {h!r}')
    rows = pg.evaluate(ROWS)
    if 'Loki' in rows: out.append(f'Year: a hull lost only over a year ago is listed {list(rows)}')
    CALLS.clear(); analyze(pg, 'Mk Old Pilot')
    h, rows = pg.evaluate(HEAD), pg.evaluate(ROWS)
    if not h.startswith('30 kills in 30 fights, 3 losses, ') or not h.endswith('(none in the past year)') or set(rows) != {'Retribution', 'Curse'}: out.append(f'Old: shown as read, said so {h!r} {list(rows)}')
    ctx.close(); return out, errs

def s_big(b, html):
    out, errs = [], []
    ctx = new_ctx(b, errs); pg = ctx.new_page(); pg.goto('file://' + html)
    CALLS.clear(); ESI_KM.clear()
    cid = P['Mk Big Pilot']
    n = len(page_body('kills', cid, 1))
    if n <= 20e6: out.append(f'Big: the made-up page is {n:,} characters, not over 20 MB')
    analyze(pg, 'Mk Big Pilot')
    h, tip, rows = pg.evaluate(HEAD), pg.evaluate(HEAD_T), pg.evaluate(ROWS)
    if kpages(cid) != [1] or 'stopped at a large page' not in tip: out.append(f'Big: no page 2 after a page over 20 MB {kpages(cid)} {tip[:140]!r}')
    if not h.startswith('200 kills in 2 fights, 1 loss, ') or (rows.get('Typhoon') or [0, ''])[1] != '1 fight': out.append(f'Big: the fleet one fight {h!r} {rows.get("Typhoon")}')
    st = pg.evaluate("""async (cid) => { const db = await openDscanCacheDb(); const get = (k) => new Promise(r => { const q = db.transaction('zkb').objectStore('zkb').get(k); q.onsuccess = () => r(q.result); });
      const k = await get('t:' + ZKB + '/kills/characterID/' + cid + '/'), l = await get('t:' + ZKB + '/losses/characterID/' + cid + '/');
      return [k ? Math.max(...k.data.data.map(x => JSON.stringify(x).length)) : null, k ? k.data.big : null, l ? [l.data.data[0].attackers.length, l.data.data[0].na, !!l.data.data[0].victim.items.length] : null]; }""", cid)
    if not (st[0] and st[0] < 4000 and st[1] is True): out.append(f'Big: each kill kept under 4 KB, the page marked large {st[:2]}')
    if st[2] != [20, 2000, True]: out.append(f'Big: a loss of 2,000 attackers kept as the victim (its fit) and 20 attackers {st[2]}')
    t = pg.evaluate("""async (cid) => { const t0 = performance.now(); zkbPilotMem.clear(); killStubCache.clear(); pd.charId = null;
      await pdLoad({id: cid, name: 'Mk Big Pilot'}, document.getElementById('fitStatus'), true, true); return performance.now() - t0; }""", cid)
    print(f'     (Big: a forced read of the {n / 1e6:.1f} MB page and its losses, to the dossier drawn: {t:.0f} ms)')
    if t > 15000: out.append(f'Big: {t:.0f} ms from asking to the dossier drawn')
    ctx.close(); return out, errs

def s_rule(b, html):
    out, errs = [], []
    ctx = new_ctx(b, errs); pg = ctx.new_page(); pg.goto('file://' + html)
    r = pg.evaluate("""() => { const me = 1, T = Date.parse('2026-01-01T00:00:00Z');
      const k = (id, mins, others, ships) => pdTrimKill({killmail_id: id, killmail_time: new Date(T + mins * 60000).toISOString(), solar_system_id: 30000142,
        victim: {ship_type_id: 603}, attackers: [{character_id: me, ship_type_id: 587}, ...others.map(c => ({character_id: c, ship_type_id: 587}))], zkb: {hash: 'h'}}, me);
      const f = (ks) => pdFights(ks).count;
      return {
        solo: f([k(1, 0, []), k(2, 10, [])]),
        one1h: f([k(1, 0, [7]), k(2, 60, [7])]), one4h: f([k(1, 0, [7]), k(2, 240, [7])]),
        five1: f([k(1, 0, [11, 12, 13, 14, 15]), k(2, 30, [11, 22, 23, 24, 25])]), five2: f([k(1, 0, [11, 12, 13, 14, 15]), k(2, 30, [11, 12, 23, 24, 25])]),
        chain: f([k(1, 0, [7]), k(2, 150, [7]), k(3, 300, [7])]),
        cap: pdTrimKill({killmail_id: 9, killmail_time: new Date(T).toISOString(), victim: {ship_type_id: 603}, zkb: {hash: 'h'},
          attackers: [{character_id: me, ship_type_id: 587}, ...Array.from({length: 300}, (_, i) => ({character_id: 1000 + 300 - i, ship_type_id: 587}))]}, me).ids.slice(0, 2).concat(PD_IDS_MAX)};
    }""")
    want = {'solo': 2, 'one1h': 1, 'one4h': 2, 'five1': 2, 'five2': 1, 'chain': 1, 'cap': [1001, 1002, 100]}
    if r != want: out.append(f'the fight rule: {r} want {want} (the pilot left out; 1 shared for 1-2 others, else 2; within 3 hours, chained; the 100 lowest ids)')
    ctx.close(); return out, errs

def s_first(b, html):
    out, errs = [], []
    ctx = new_ctx(b, errs); pg = ctx.new_page(); pg.goto('file://' + html)
    CALLS.clear(); HELD.clear()
    cid = P['Mk Fleet Pilot']; HOLD['on'] = (cid, 2)
    pg.evaluate("() => { window.__pdR = 0; const o = pdRender; pdRender = function(){ window.__pdR++; return o.apply(this, arguments); }; }")
    analyze(pg, 'Mk Fleet Pilot', wait=False)
    for _ in range(600):
        if HELD: break
        pg.wait_for_timeout(100)
    pg.wait_for_function("() => pd.d && pd.reading && /reading older kills/.test(document.querySelector('#pilotDossier .pd-head .ctx').textContent)", timeout=60000)
    h0 = pg.evaluate(HEAD); n0 = pg.evaluate('window.__pdR')
    if not HELD or not h0.startswith('200 kills in 1 fight'): out.append(f'page 1 first: drawn while page 2 waits {h0!r} {len(HELD)}')
    HOLD['on'] = None
    for rt, body in HELD: rt.fulfill(status=200, content_type='application/json', headers={'access-control-allow-origin': '*'}, body=body)
    HELD.clear(); read_done(pg); pg.wait_for_timeout(500)
    n1 = pg.evaluate('window.__pdR'); h1 = pg.evaluate(HEAD)
    if not h1.startswith('600 kills in 1 fight') or n1 - n0 > 3: out.append(f'then redrawn once with the older pages {h1!r} ({n1 - n0} redraws after page 1)')
    # a new pilot while the older pages are read stops the reading
    ctx2 = new_ctx(b, errs); pg = ctx2.new_page(); pg.goto('file://' + html)
    CALLS.clear(); HELD.clear(); HOLD['on'] = (cid, 2)
    analyze(pg, 'Mk Fleet Pilot', wait=False)
    for _ in range(600):
        if HELD: break
        pg.wait_for_timeout(100)
    idle(pg)
    analyze(pg, 'Mk Next Pilot', wait=False); idle(pg)
    HOLD['on'] = None
    for rt, body in HELD: rt.fulfill(status=200, content_type='application/json', headers={'access-control-allow-origin': '*'}, body=body)
    HELD.clear(); pg.wait_for_timeout(2500)
    h = pg.evaluate(HEAD)
    if 3 in kpages(cid) or not h.startswith('5 kills in 5 fights'): out.append(f'a new pilot stops the reading: no page 3 {kpages(cid)}, the new dossier stays {h!r}')
    ctx.close(); ctx2.close(); return out, errs

def s_sa(b, html):
    out, errs = [], []
    ctx = new_ctx(b, errs); pg = ctx.new_page(); pg.goto('file://' + html)
    CALLS.clear(); ESI_KM.clear()
    cid = P['Mk War Pilot']
    r = pg.evaluate("""async (cid) => { saRowPick = async () => {};   // the row's pick needs a Local analysis; only the data is checked here
      const r = await saPilotData({id: cid, name: 'Mk War Pilot', corp: 98000041}); return r && r.d ? [r.state, r.d.nKills, r.d.nLosses, r.d.nFights] : [r && r.state]; }""", cid)
    n = [c for c in CALLS if c[1] == cid]
    if r != ['done', 200, 3, 36] or len(n) != 2 or ESI_KM: out.append(f'System Analyzer rows: all of page 1 {r}, {len(n)} zKillboard requests, {len(ESI_KM)} ESI killmail reads')
    ctx.close(); return out, errs

def s_store(b, html, old):
    out, errs = [], []
    ctx = new_ctx(b, errs)
    ctx.add_init_script("""(() => { window.__usage = 0; const est = () => Promise.resolve({usage: window.__usage, quota: 1e10});
      try{ Object.defineProperty(navigator, 'storage', {value: {estimate: est, persist: () => Promise.resolve(false)}, configurable: true}); }catch(e){} })();""")
    pg = ctx.new_page(); pg.goto('file://' + html)
    r = pg.evaluate("""async () => { if(dscanSweepP) await dscanSweepP;
      const db = await openDscanCacheDb(), now = Date.now(), pad = 'x'.repeat(1e6);
      const put = (st, k, v) => new Promise(r => { const tx = db.transaction(st, 'readwrite'); tx.objectStore(st).put(v, k); tx.oncomplete = () => r(); });
      for(let i = 0; i < 30; i++) await put('killmails', 8800000 + i, {ts: now - (30 - i) * 864e5, data: {killmail_id: 8800000 + i, hash: 'h', km: {pad}}});
      await put('zkb', 'old-list', {ts: now - 2 * 3600e3, data: []}); await put('zkb', 'fresh-list', {ts: now - 60e3, data: []});
      await put('types', 99999991, {ts: now - 900 * 864e5, data: {name: 'kept'}}); await put('orgs', 99999992, {ts: now - 900 * 864e5, data: {name: 'kept'}});
      window.__usage = 30e6; dscanSweepAt = 0;
      const under = (await dscanCacheSweep()).killmails;
      window.__usage = 60e6; dscanSweepAt = 0;
      const out = await dscanCacheSweep();
      window.__usage = 60e6; dscanSweepAt = 0;   // the browser's figure lagging behind the deletion: nothing more this page load
      const again = (await dscanCacheSweep()).killmails;
      out.under = under; out.again = again;
      const has = (st, k) => new Promise(r => { const q = db.transaction(st).objectStore(st).get(k); q.onsuccess = () => r(q.result !== undefined); });
      const kept = []; for(let i = 0; i < 30; i++) if(await has('killmails', 8800000 + i)) kept.push(i);
      return {out, kept, oldList: await has('zkb', 'old-list'), fresh: await has('zkb', 'fresh-list'), types: await has('types', 99999991), orgs: await has('orgs', 99999992)}; }""")
    # usage 60 MB, low mark 40 MB: about 20 MB of the oldest (1 MB each) go
    if not (r['kept'] and r['kept'][0] >= 19 and r['kept'][-1] == 29 and len(r['kept']) <= 11) or r['oldList'] or not r['fresh'] or not r['types'] or not r['orgs']:
        out.append(f'the cap: the oldest killmails deleted to under 40 MB, the expired list deleted, the rest kept {r}')
    if r['out'].get('under') != 0 or r['out'].get('again') != 0: out.append(f"under the cap nothing is deleted, and after one cut nothing more this page load {r['out']}")
    # the older page reads what it wrote before, after this one wrote its own
    if old:
        CALLS.clear(); ESI_KM.clear()
        pg2 = ctx.new_page(); pg2.goto('file://' + html)
        pg2.evaluate("() => { window.__usage = 0; }")
        cid = P['Mk War Pilot']; analyze(pg2, 'Mk War Pilot')
        pg3 = ctx.new_page(); pg3.goto('file://' + old); pg3.wait_for_timeout(500)
        ESI_KM.clear()
        o = pg3.evaluate("""async (cid) => { const l = await fetchLossesStubs(cid, undefined, false, {who: 'x'}); const k = await fetchKillsStubs(cid, false, {who: 'x'});
          const r = await fetchKillmail(k[0]); return [Array.isArray(l) && l.length, Array.isArray(k) && k.length, !!(r && r.km && r.km.attackers && r.km.attackers.length > 100)]; }""", cid)
        if o != [3 + 4, 200, True] or ESI_KM: out.append(f'the older page reads its lists and the newest killmail this page kept {o} ({len(ESI_KM)} ESI killmail reads)')
    ctx.close(); return out, errs

SCEN = {'war': s_war, 'pages': s_pages, 'big': s_big, 'rule': s_rule, 'first': s_first, 'sa': s_sa}
MUTANTS = [
    ('whole killmails kept', "    const data = list.map(x => kind === 'kills' ? pdTrimKill(x, charId) : pdTrimLoss(x)).filter(Boolean);", "    const data = list;", 'big'),
    ('the pilot counted among his wingmates', "    if(a === me) continue;\n    ids.push(a.character_id);", "    ids.push(a.character_id);", 'rule'),
    ('no 3-hour window', "      if(t[j] - t[i] > PD_FIGHT_GAP_MS) break;\n", "", 'rule'),
    ('50 kills read', "  const st = {want, kills: kr.kills, losses:", "  const st = {want, kills: kr.kills.slice(0, 50), losses:", 'war'),
    ('an ESI read despite a whole item', "function zkbWholeKm(x){ return kmWhole(x) &&", "function zkbWholeKm(x){ return false &&", 'war'),
    ('no size stop', "  if(p.big) return 'big';", "", 'big'),
    ('no year limit', "  const k = kills.filter(inYear), l = losses.filter(inYear);", "  const k = kills, l = losses;", 'pages'),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    PAGE = open(HTML, encoding='utf-8').read()
    old = None
    try:
        src = subprocess.run(['git', '-C', os.path.dirname(HTML), 'show', '85e20cb:index.html'], capture_output=True, text=True, encoding='utf-8')
        if src.returncode == 0 and 'zkbPilotList' not in src.stdout:
            with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f: f.write(src.stdout); old = f.name
    except Exception as e: print('     (no git copy of the older page:', e, ')')
    try:
        for name, fn in SCEN.items():
            o, e = fn(b, HTML)
            for x in o: check(False, x)
            check(not o, f'{name}: as expected')
            check(not e, f'{name}: no page errors {e[:2]}')
        o, e = s_store(b, HTML, old)
        for x in o: check(False, x)
        check(not o, 'stored data: the cap, the zkb store, the older page' + ('' if old else ' (the older page not checked: no git copy)'))
        check(not e, f'stored data: no page errors {e[:2]}')
        if not NO_MUT:
            for name, a, z, sc in MUTANTS:
                if PAGE.count(a) != 1: check(False, f'mutant "{name}": its line isn\'t in the page once ({PAGE.count(a)})'); continue
                with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f: f.write(PAGE.replace(a, z)); mp = f.name
                try:
                    o, e = SCEN[sc](b, mp)
                    check(bool(o) or bool(e), f'mutant "{name}" fails ({(o or e or ["nothing"])[0][:110]})')
                finally: os.unlink(mp)
    finally:
        if old: os.unlink(old)
    b.close()
print(f'FAILURES: {fails}')
sys.exit(1 if fails else 0)
