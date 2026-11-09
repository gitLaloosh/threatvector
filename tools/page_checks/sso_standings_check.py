"""Standings from your corporation's and alliance's EVE contacts (v2026.11.09.2, build queue 030, SSO Phase 3; Project doc
roadmap/sso-phase3-standings-plan.md).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/sso_standings_check.py [index.html]   -> 'FAILURES: N' (must be 0)

Never a live login and never live ESI (CLAUDE.md): sso_game_check.py's stand-ins (CCP's login with keys made per run, intel_check.py's
made-up Chatlogs folder and sa_mocks.py's made-up Local), plus a stand-in for ESI's /corporations/<id>/contacts/ and
/alliances/<id>/contacts/ that records each request and answers with pages (X-Pages, Last-Modified), Expires, 401, 403, 429 or 503 as a
case sets. Made-up characters, groups, standings and tokens only. Checks:
  * the Standings section: logged out, one line and its info panel (shared close button); logged in, the switch unchecked; ticked without
    the permission: Continue to EVE / Cancel; Continue asks EVE for both contacts scopes; back with both: on, tvEveStand true, both lists
    read with the token, X-Compatibility-Date and X-User-Agent, "From EVE: 5 blue · 6 red", the typed lists and Suggested friendlies hidden
    (dscanSide unchanged), the profile's tags; back with one: SSO-07, off; an NPC corporation: the switch disabled, no request;
  * the rule, in the System Analyzer: your own groups friendly; an alliance entry; a corporation entry inside a listed alliance (grouped by
    the corporation); a pilot entry (that pilot only, under his group); the corporation's entry where the alliance has none; a 0 entry is
    none; corporation and alliance disagree: the alliance decides, flagged (both directions, and a corporation's pilot entry against the
    alliance's alliance entry); zKillboard's evidence only a note beside a neutral; the typed lists ignored; with the switch off: today's
    sideOf exactly (main's function, every pilot, with and without evidence);
  * the hovers: the Fleet tab row's icon, Intel's chip title, the Pilot Analyzer's tag (Hostile with EVE's reason; Neutral · killed N);
  * reads: none before Expires and none within 5 minutes; an unchanged re-read draws nothing; a changed one redraws once and re-works
    Intel once; X-Pages read in order; pages whose Last-Modified differ read once more; no alliance: no alliance request; 401: SSO-08, no
    second request, the typed lists; 403 with the permission: SIDE-03, the other list used; both: the typed lists; 429: Retry-After;
    503: SIDE-04, the copy in hand; nothing in localStorage or sessionStorage but the setting;
  * Intel: a report and a kill made while the typed lists said friendly are worked out again when EVE's standings come in (sides, friendlies
    only, the kill's threat ships, Near You), with no alert; a typed-list edit re-works them too;
  * the first read after a reload is waited for (Analyze draws once, with EVE's sides); over 10 s: the typed lists, then a redraw;
  * a new tab with the setting on: the login's button says "Also asks for: Corporation contacts, Alliance contacts"; Log out: off, the typed
    lists back;
  * 390 px: Continue to EVE 44 px tall, no sideways scroll; no page errors;
  * mutants (the page with one rule broken) each fail the rule cases: typed lists winning, evidence deciding, the corporation winning,
    hostile winning across lists, an alliance entry over a pilot entry, a 0 entry deciding, a read before Expires, a 401 retried, the
    lists stored, Intel not re-worked, a caller without the pilot's id, an NPC corporation's contacts asked.
"""
import sys, os, re, json, time, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
G = open(os.path.join(HERE, 'sso_game_check.py'), encoding='utf-8').read()
exec(compile(G[:G.index('from playwright.sync_api import sync_playwright\nwith')], 'sso_game_check', 'exec'))   # its stand-ins and helpers
SC, SA_ = 'esi-corporations.read_contacts.v1', 'esi-alliances.read_contacts.v1'
REPO = os.path.join(HERE, '..', '..')

# ---- made-up standings (sa_mocks' groups) ----
P_BWF, P_RLH, P_VOID = M.pick(98000002), M.pick(98000003), M.pick(98000005)
ALLY_LIST = [  # your alliance's contacts
    {'contact_id': M.CRTS, 'contact_type': 'alliance', 'standing': -10.0}, {'contact_id': M.BCM, 'contact_type': 'alliance', 'standing': 10.0},
    {'contact_id': M.TURNCOAT, 'contact_type': 'corporation', 'standing': -5.0}, {'contact_id': P_BWF, 'contact_type': 'character', 'standing': -10.0},
    {'contact_id': M.NPACT, 'contact_type': 'alliance', 'standing': 5.0}, {'contact_id': M.QHC, 'contact_type': 'alliance', 'standing': -5.0},
    {'contact_id': 98000013, 'contact_type': 'corporation', 'standing': 0.0}, {'contact_id': 500001, 'contact_type': 'faction', 'standing': 5.0}]
CORP_LIST = [  # your corporation's contacts
    {'contact_id': M.NPACT, 'contact_type': 'alliance', 'standing': -10.0}, {'contact_id': M.QHC, 'contact_type': 'alliance', 'standing': 10.0},
    {'contact_id': 98000013, 'contact_type': 'corporation', 'standing': -10.0}, {'contact_id': M.ASHR, 'contact_type': 'corporation', 'standing': 5.0},
    {'contact_id': P_RLH, 'contact_type': 'character', 'standing': 10.0, 'label_ids': [], 'is_watched': False}]
ME = {'pilot': {'id': MAIN, 'name': 'Your Main'}, 'corp': {'id': M.CORP, 'name': 'Example Corp', 'kind': 'corporation'},
      'alliance': {'id': M.ALLIANCE, 'name': 'Example Alliance', 'kind': 'alliance'},
      'friendly': [{'id': M.CRTS, 'name': 'Crimson Tide Syndicate', 'kind': 'alliance'}, {'id': M.VOIDR, 'name': 'Void Runners', 'kind': 'alliance'}],
      'hostile': [{'id': M.BCM, 'name': 'Blue Coalition Member', 'kind': 'alliance'}], 'rows': 15}
NAMES = {M.CRTS: 'Crimson Tide Syndicate', M.BCM: 'Blue Coalition Member', M.TURNCOAT: 'Turncoat Corp', M.NPACT: 'Northern Pact', M.QHC: 'Quiet Harbor Collective',
         98000013: 'Lantern Bay Traders', 500001: 'Caldari State', M.ASHR: 'Ashen Reach Industries', P_BWF: M.PILOTS[P_BWF][0], P_RLH: M.PILOTS[P_RLH][0]}

# ---- the stand-in ESI contacts routes ----
C, CREQ = {}, []
def creset(**o):
    CREQ.clear(); C.clear()
    C.update({'mode': {}, 'exp': 300, 'pages': {'alliance': 1, 'corporation': 1}, 'lm': {}, 'ra': 30, 'aff': {'corp': M.CORP, 'alliance': M.ALLIANCE},
              'lists': {'alliance': [dict(x) for x in ALLY_LIST], 'corporation': [dict(x) for x in CORP_LIST]}})
    C.update(o)
creset()
def esi_st(route):
    u = route.request.url
    m = re.search(r'/(corporations|alliances)/(\d+)/contacts/\?(.*)$', u)
    if m:
        who = 'alliance' if m.group(1) == 'alliances' else 'corporation'
        pg = int(re.search(r'page=(\d+)', m.group(3)).group(1))
        CREQ.append({'t': time.time(), 'who': who, 'id': int(m.group(2)), 'page': pg, 'h': {k.lower(): v for k, v in route.request.headers.items()}})
        hd = {'access-control-allow-origin': '*', 'access-control-expose-headers': 'x-pages, last-modified, expires, retry-after, x-ratelimit-group, x-ratelimit-limit, x-ratelimit-remaining',
              'x-ratelimit-group': 'corp-social', 'x-ratelimit-limit': '300/15m', 'x-ratelimit-remaining': '290',
              'expires': time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(time.time() + C['exp'])),
              'last-modified': C['lm'].get((who, pg), 'Mon, 09 Nov 2026 10:00:00 GMT')}
        md = C['mode'].get(who, 'ok')
        if md in ('401', '403', '503'): return route.fulfill(status=int(md), content_type='application/json', headers=hd, body='{"error":"made-up"}')
        if md == '429': hd['retry-after'] = str(C['ra']); return route.fulfill(status=429, content_type='application/json', headers=hd, body='{"error":"made-up"}')
        L, n = C['lists'][who], C['pages'][who]
        if n > 1: hd['x-pages'] = str(n)
        per = -(-len(L) // n); body = L[(pg - 1) * per: pg * per]
        return route.fulfill(status=200, content_type='application/json', headers=hd, body=json.dumps(body))
    if '/universe/names/' in u:
        q = json.loads(route.request.post_data or '[]')
        if q and all(i in NAMES for i in q):
            return route.fulfill(status=200, content_type='application/json', body=json.dumps([{'id': i, 'name': NAMES[i], 'category': 'alliance'} for i in q]))
    if '/characters/affiliation/' in u:
        q = json.loads(route.request.post_data or '[]')
        if MAIN in q:
            a = C['aff']; out = []
            for i in q:
                if i == MAIN: out.append({'character_id': MAIN, 'corporation_id': a['corp'], **({'alliance_id': a['alliance']} if a['alliance'] else {})})
                elif i in M.PILOTS: out.append(M.aff(i))
            return route.fulfill(status=200, content_type='application/json', body=json.dumps(out))
    return esi_loc(route)
# a slow ESI for the contacts routes, in the page (a route handler that sleeps would hold up every other answer); kept across a reload
DELAY = r"""(() => { const f = window.fetch; window.fetch = async function(u){ const d = Number(sessionStorage.getItem('__st_delay') || 0); if(d && /\/contacts\//.test(String(u))) await new Promise(r => setTimeout(r, d)); return f.apply(this, arguments); }; })();"""
reqs = lambda who=None: [x for x in CREQ if who is None or x['who'] == who]

GROUPS = """() => { const out = {}; for(const d of document.querySelectorAll('#saResults details[data-sa-g]')){ const w = d.querySelector('.sa-why');
  out[d.dataset.saG] = {n: Number((d.querySelector('.sa-gn') || {}).textContent || 0), why: w ? w.textContent : '', cls: w ? w.className : '', title: w ? w.title : ''}; } return out; }"""
SEC = """() => { const q = (s) => document.querySelector(s), t = (x) => x ? x.textContent.replace(/\\s+/g, ' ').trim() : '';
  const sec = q('#sidePanel .pp-sec[data-k="side"]'), cb = q('#sidePanel [data-sso="stand"]'), typed = q('#sidePanel .side-typed');
  return {sec: t(sec), cb: cb ? cb.checked : null, dis: cb ? cb.disabled : null, ask: !!q('#sidePanel [data-sso="st-go"]'), on: sideEve.on, use: sideEveUse(),
    ls: localStorage.getItem('tvEveStand'), typedHidden: typed ? typed.hidden : null, n: t(q('#sidePanel .pp-sec[data-k="side"] .pp-n')),
    side: localStorage.getItem('dscanSide'), sw: document.documentElement.scrollWidth, vw: innerWidth}; }"""

def mutate(page, a, b):
    assert page.count(a) >= 1, a[:70]
    return page.replace(a, b, 1)
MUTANTS = [
    ('a typed list winning', "  if(sideEveUse()) return sideEveSide(corpId, allianceId, evidence, charId);\n  if(sets.fC.has(corpId)) return {side: 'f'};",
     "  if(sets.fC.has(corpId)) return {side: 'f'};\n  if(allianceId && sets.fA.has(allianceId)) return {side: 'f'};\n  if(sideEveUse()) return sideEveSide(corpId, allianceId, evidence, charId);"),
    ('evidence deciding', "    return n ? {side: 'n', why: 'zkbnote', n} : {side: 'n'};", "    return n ? {side: 'h', why: 'zkb', n} : {side: 'n'};"),
    ('the corporation winning', "const a = one('alliance'), c = one('corporation'), d = a || c;", "const a = one('alliance'), c = one('corporation'), d = c || a;"),
    ('hostile winning across lists', "const a = one('alliance'), c = one('corporation'), d = a || c;", "const a = one('alliance'), c = one('corporation'), d = (c && c.v < 0) ? c : a || c;"),
    ('an alliance entry over a pilot entry', "[['p', 'pilot', charId], ['c', 'corporation', corpId], ['a', 'alliance', allianceId]]", "[['a', 'alliance', allianceId], ['c', 'corporation', corpId], ['p', 'pilot', charId]]"),
    ('a 0 entry deciding', "if(K[x.type] && x.v !== 0) m.set(", "if(K[x.type]) m.set("),
    ('a read before Expires', "  if(sideEve.for === f && Date.now() < sideEve.next) return null;\n", "\n"),
    ('a 401 retried', "      if(r.status === 401){ sideEve.stop = 'SSO-08'; return {fail: 'SSO-08'}; }", "      if(r.status === 401){ return {fail: 'SIDE-04'}; }"),
    ('the lists stored', "  if(sideEve.for === f) sideEve.tried = true;", "  if(sideEve.for === f) sideEve.tried = true; try{ localStorage.setItem('tvEveCopy', JSON.stringify(sideEve.L)); }catch(e){ }"),
    ('Intel not re-worked', "  try{ if(!it.feed || !it.feed.length || itExOrg) return false; }", "  try{ return false; }"),
    ('a caller without the pilot\'s id', "  return sideOf(a.corp, a.alliance, sideSets(), null, id);", "  return sideOf(a.corp, a.alliance, sideSets(), null);"),
    ('an NPC corporation\'s contacts asked', "corporation: r.corp && !isNpcCorp(r.corp.id) ? r.corp.id : null", "corporation: r.corp ? r.corp.id : null"),
]
OLD = subprocess.run(['git', '-C', REPO, 'show', '4a6aea4:index.html'], capture_output=True, text=True).stdout
mo = re.search(r'\nfunction sideOf\(corpId, allianceId, sets, evidence\)\{.*?\n\}', OLD, re.S)
OLD_SIDEOF = mo.group(0).replace('function sideOf(', 'function __oldSideOf(') if mo else ''

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    errs = []
    def ctx_new(w=1440, page_html=None):
        html = page_html or PAGE
        def serve(route):
            return route.fulfill(status=200, content_type='text/html; charset=utf-8', body=html) if urllib.parse.urlsplit(route.request.url).path == '/' else route.fulfill(status=404, body='')
        c = b.new_context(bypass_csp=True, viewport={'width': w, 'height': 1000})
        c.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
        c.add_init_script(FS); c.add_init_script(EXTRA); c.add_init_script(DELAY); route(c)
        c.route(re.compile(r'https://esi\.evetech\.net/.*'), esi_st)
        c.route(re.compile(r'https://login\.eveonline\.com/.*'), sso)
        c.route(re.compile(r'^http://localhost:8000/.*'), serve)
        return c
    def ready(pg): pg.wait_for_function("typeof it !== 'undefined' && it.loaded", timeout=10000); pg.wait_for_timeout(300)
    def page(c, stand=None, me=ME):
        pg = c.new_page(); pg.goto(DEV_ORIGIN + '/')
        pg.evaluate("([s, v]) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.removeItem('dscanIntel'); if(v === null) localStorage.removeItem('tvEveStand'); else localStorage.setItem('tvEveStand', JSON.stringify(v)); }", [me, stand])
        pg.reload(); ready(pg); return pg
    def login(pg, scp=(SC, SA_), tab='madeUpTabId0030', tok='madeUpAccessToken'):
        pg.evaluate("([id, scp, tab, rt, tok]) => { sso.who = {id, name: 'Your Main'}; sso.access = tok; sso.exp = Date.now() + 1200000; sso.scp = scp;"
                    " ssoSet(SSO_REFRESH, rt); ssoSet(SSO_WHO, JSON.stringify(sso.who)); ssoSet(SSO_TAB, tab); sideEve.stop = ''; renderSidePanel(); }", [MAIN, list(scp), tab, REFRESH, tok])
    def prof(pg): pg.evaluate("() => { if(!profileIsOpen()) openProfile(); renderSidePanel(); }"); pg.wait_for_timeout(150)
    def on(pg): pg.evaluate("() => { sideEveToggle(true); }"); pg.wait_for_function("() => !sideEve.busy && sideEve.tried", timeout=8000); pg.wait_for_timeout(200)
    def due(pg): pg.evaluate("() => { sideEve.next = 0; }")
    def need(pg): pg.evaluate("() => sideEveNeed()"); pg.wait_for_function("() => !sideEve.busy", timeout=8000); pg.wait_for_timeout(150)
    def analyze(pg):
        pg.evaluate("(t) => { switchTab('dscan'); document.getElementById('localInput').value = t; }", M.LOCAL)
        pg.click('#analyzeBtn'); pg.wait_for_function("() => sa.last && !document.getElementById('analyzeBtn').disabled", timeout=20000); pg.wait_for_timeout(500)
    sec = lambda pg: pg.evaluate(SEC)
    groups = lambda pg: pg.evaluate(GROUPS)
    def counters(pg):   # wraps once per page; later calls only reset the counts
        pg.evaluate("() => { window.__n = {sa: 0, rw: 0}; if(window.__wrapped) return; window.__wrapped = true; const s = saRender; saRender = function(){ __n.sa++; return s.apply(this, arguments); };"
                    " const r = itSidesRework; itSidesRework = function(){ __n.rw++; return r.apply(this, arguments); }; }")

    # ---- the rule cases (also run against each mutant): fails counted into a list ----
    def rule_cases(pg, out, note=lambda ok, msg: None):
        def ck(ok, msg):
            note(ok, msg)
            if not ok: out.append(msg)
        g = groups(pg)
        hs = {k: v for k, v in g.items() if k.startswith('h:')}; fs = {k: v for k, v in g.items() if k.startswith('f:')}; ns = {k: v for k, v in g.items() if k.startswith('n:')}
        ck(f'h:a{M.CRTS}' in hs and hs[f'h:a{M.CRTS}']['why'] == 'Your alliance: −10 in EVE', f"an alliance entry: Crimson Tide hostile, \"Your alliance: −10 in EVE\" ({hs.get(f'h:a{M.CRTS}')})")
        ck(f'f:a{M.CRTS}' not in fs, 'the typed list (Crimson Tide friendly) is ignored')
        ck(f'h:c{M.TURNCOAT}' in hs and hs[f'h:c{M.TURNCOAT}']['why'] == 'Your alliance: −5 in EVE', f"a corporation entry inside a blue alliance: Turncoat hostile, by itself ({hs.get(f'h:c{M.TURNCOAT}')})")
        ck(f'h:a{M.BCM}' in hs and hs[f'h:a{M.BCM}']['n'] == 1 and 'set a pilot here' in hs[f'h:a{M.BCM}']['why'], f"a pilot entry: that one pilot hostile, under his alliance ({hs.get(f'h:a{M.BCM}')})")
        ck(f'f:a{M.BCM}' in fs and fs[f'f:a{M.BCM}']['n'] == 11, f"the rest of Blue Coalition friendly (the typed hostile list ignored) ({fs.get(f'f:a{M.BCM}')})")
        ck(f'h:a{M.QHC}' in hs and hs[f'h:a{M.QHC}']['why'] == 'Alliance −5 (corp +10)' and ' dis' in hs[f'h:a{M.QHC}']['cls'] and 'alliance\'s standing decides' in hs[f'h:a{M.QHC}']['title'],
           f"corporation +10, alliance −5: hostile (the alliance decides), flagged ({hs.get(f'h:a{M.QHC}')})")
        ck(f'f:a{M.NPACT}' in fs and f'h:a{M.NPACT}' not in hs, f"corporation −10, alliance +5: friendly (the alliance decides) ({fs.get(f'f:a{M.NPACT}')})")
        ck(f'h:c98000013' in hs and hs['h:c98000013']['why'] == 'Your corporation: −10 in EVE', f"the alliance's 0 is no entry: the corporation's −10 decides ({hs.get('h:c98000013')})")
        ck(f'f:c{M.ASHR}' in fs, f'the corporation\'s +5 where the alliance has none: Ashen Reach friendly (its zKillboard evidence ignored)')
        ck(f'n:a{M.VOIDR}' in ns and ns[f'n:a{M.VOIDR}']['why'] == 'Killed 3 of yours in 7 days' and 'zkbnote' in ns[f'n:a{M.VOIDR}']['cls'] and f'h:a{M.VOIDR}' not in hs,
           f"no entry, zKillboard's evidence: Void Runners neutral with the note ({ns.get(f'n:a{M.VOIDR}')})")
        ck(f'f:a{M.ALLIANCE}' in fs, 'your own alliance friendly')
        rlh = pg.evaluate("(id) => { const s = sideOf(98000003, " + str(M.CRTS) + ", sideSets(), null, id); return [s.side, s.disagree, sideWhyText(s)]; }", P_RLH)
        ck(rlh == ['h', True, 'Alliance −10 (corp +10)'], f"your corporation set a pilot +10, your alliance his alliance −10: hostile, the alliance decides, flagged ({rlh})")
        tip = pg.evaluate("(id) => { it.aff.set(id, {corp: 98000003, alliance: " + str(M.CRTS) + "}); return itPilotTitle({side: itSide(id), sw: sideWhyText(itSideRes(id)), name: 'x'}); }", P_RLH)
        ck('Alliance −10 (corp +10)' in tip, f"Intel's chip title says why ({tip[:60]!r})")

    # ---- the Standings section; the permission step ----
    c = ctx_new(); pg = page(c); prof(pg); s = sec(pg)
    check(s['cb'] is None and "Log in with EVE (Pilot, above) to use your corporation's and alliance's standings instead of typing them" in s['sec'] and s['typedHidden'] is False,
          f"logged out: one line, the typed lists shown ({s['sec'][:120]!r})")
    pg.click('#sidePanel .side-eve summary.info-btn'); pg.wait_for_timeout(200)
    ip = pg.evaluate("() => { const d = [...document.querySelectorAll('[role=dialog]')].find(x => x.offsetParent && /How EVE standings work/.test(x.textContent)); return d ? [!!d.querySelector('button.x-close'), /alliance's standing decides/.test(d.textContent)] : null; }")
    check(ip == [True, True], f'its info panel: "How EVE standings work", the alliance deciding, the shared close button ({ip})')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(100)
    login(pg, scp=()); prof(pg); s = sec(pg)
    check(s['cb'] is False and 'Needs its OK from EVE' in s['sec'] and not s['on'], f"logged in: the switch, unchecked ({s['sec'][:90]!r})")
    pg.click('#sidePanel [data-sso="stand"]'); pg.wait_for_timeout(200); s = sec(pg)
    check(s['ask'] and not s['on'] and 'Continue to EVE' in s['sec'] and "read your corporation's and your alliance's contacts" in s['sec'], 'ticked without the permission: Continue to EVE / Cancel, still off')
    pg.click('#sidePanel [data-sso="st-no"]'); pg.wait_for_timeout(150); s = sec(pg)
    check(not s['ask'] and not s['on'], 'Cancel closes it; still off')
    reset(scp=[SC, SA_]); creset(); pg.click('#sidePanel [data-sso="stand"]'); pg.wait_for_timeout(150)
    pg.click('#sidePanel [data-sso="st-go"]'); pg.wait_for_url(DEV_ORIGIN + '/**', timeout=8000); ready(pg); pg.wait_for_timeout(1500)
    auth = [x for x in LOG if x[0] == '/v2/oauth/authorize']; q = auth[0][2] if auth else {}
    check(set((q.get('scope') or '').split()) == {SC, SA_}, f"Continue to EVE: EVE is asked for both contacts scopes ({q.get('scope')!r})")
    pg.wait_for_function("() => sideEve.tried", timeout=8000); prof(pg); s = sec(pg)
    h0 = CREQ[0]['h'] if CREQ else {}
    check(s['on'] and s['ls'] == 'true' and s['cb'] is True and s['use'], f"back with both: on, tvEveStand true, in use ({s['ls']})")
    check(sorted((x['who'], x['id']) for x in CREQ) == [('alliance', M.ALLIANCE), ('corporation', M.CORP)], f"both lists read, your corporation's and your alliance's ({[(x['who'], x['id']) for x in CREQ]})")
    check(h0.get('authorization', '').startswith('Bearer ') and h0.get('x-compatibility-date') == COMPAT and 'threatvectorapp@gmail.com' in h0.get('x-user-agent', ''), 'each read: the token, X-Compatibility-Date, X-User-Agent')
    check('From EVE: 5 blue · 6 red' in s['sec'] and 'from EVE · 5 blue · 6 red' in s['n'] and s['typedHidden'] is True and 'Suggested friendlies' in s['sec'] and json.loads(s['side'])['hostile'] == ME['hostile'],
          f"\"From EVE: 5 blue · 6 red\" (factions and 0 not counted); the typed lists and Suggested friendlies hidden, kept in dscanSide ({s['n']!r})")
    vis = pg.evaluate("() => { const t = document.querySelector('#sidePanel .side-typed'); return t && t.getBoundingClientRect().height; }")
    check(vis == 0, f'the typed lists take no room ({vis})')
    tg = pg.evaluate("() => [...document.querySelectorAll('#sidePanel .sso-perms .sso-tag')].map(x => x.textContent)")
    check(set(tg) == {'Corporation contacts', 'Alliance contacts'}, f'the profile: Corporation contacts and Alliance contacts tags {tg}')
    pg.click('#sidePanel [data-sso="st-list"]'); pg.wait_for_timeout(600)
    lst = pg.evaluate("() => [...document.querySelectorAll('#sidePanel .side-eve-l')].map(l => [l.querySelector('.side-lab').textContent, [...l.querySelectorAll('.side-eve-r')].map(r => r.textContent)])")
    al = dict(lst).get('Your alliance · 8', [])
    check(len(lst) == 2 and len(al) == 8 and any('Caldari State' in r and 'faction' in r for r in al) and al[0].startswith('+') is False and any('Blue Coalition Member' in r and '+10' in r for r in al),
          f"See EVE's standings: both lists, names, kinds, standings ({[x[0] for x in lst]}; {al[:2]})")
    rf = pg.evaluate("() => { const b = document.querySelector('#sidePanel [data-sso=\"st-refresh\"]'); return b ? [b.disabled, b.title] : null; }")
    check(rf and rf[0] and 'EVE keeps them until' in rf[1], f'Refresh disabled until EVE\'s copy can change ({rf})')
    pg.close(); c.close()
    # back with one scope only
    c = ctx_new(); pg = page(c); login(pg, scp=()); prof(pg); reset(scp=[SC]); creset()
    pg.click('#sidePanel [data-sso="stand"]'); pg.wait_for_timeout(150); pg.click('#sidePanel [data-sso="st-go"]'); pg.wait_for_url(DEV_ORIGIN + '/**', timeout=8000); ready(pg); pg.wait_for_timeout(1200); prof(pg); s = sec(pg)
    check(not s['on'] and '(SSO-07)' in s['sec'] and not CREQ, f"back with one of the two: SSO-07, still off, nothing read ({s['sec'][-120:]!r})")
    pg.close(); c.close()
    # an NPC corporation, no alliance: disabled, nothing asked
    me_npc = dict(ME, corp={'id': 1000167, 'name': 'State War Academy', 'kind': 'corporation'}, alliance=None)
    c = ctx_new(); creset(aff={'corp': 1000167, 'alliance': None}); pg = page(c, stand=True, me=me_npc); login(pg); prof(pg); s = sec(pg)
    pg.evaluate("() => sideEveNeed()"); pg.wait_for_timeout(600)
    check(s['dis'] is True and 'NPC corporation' in s['sec'] and not CREQ, f"an NPC corporation: the switch disabled, its line, no request ({len(CREQ)})")
    pg.close(); c.close()
    creset()

    # ---- the rule, in the System Analyzer ----
    c = ctx_new(); pg = page(c, stand=True); login(pg); analyze(pg)
    check(len(reqs()) == 2, f"an Analyze reads EVE's lists (the first read, waited for) ({len(reqs())})")
    rc = []; rule_cases(pg, rc, check)
    # off: main's sideOf exactly
    if OLD_SIDEOF:
        diff = pg.evaluate("(src) => { eval(src.replace('function __oldSideOf', 'window.__oldSideOf = function')); sideEveToggle(false); const sets = sideSets(), out = [];"
                           " for(const ev of [null, sa.evidence]) for(const x of sa.last.pilots){ const a = JSON.stringify(sideOf(x.corp, x.alliance, sets, ev, x.id)), b = JSON.stringify(__oldSideOf(x.corp, x.alliance, sets, ev)); if(a !== b) out.push([x.name, a, b]); }"
                           " return [out.length, out.slice(0, 2), sa.last.pilots.length]; }", OLD_SIDEOF)
        check(diff[0] == 0 and diff[2] > 100, f"switch off: today's sideOf exactly, for every pilot with and without evidence ({diff[0]} differ of {diff[2]} {diff[1]})")
    else: check(False, "main's sideOf found for the comparison")
    pg.wait_for_timeout(300); g = groups(pg)
    check(f'h:a{M.BCM}' in g and g[f'h:a{M.BCM}']['why'] == 'Your hostile list' and f'f:a{M.CRTS}' in g, 'switch off: the typed lists again (Blue Coalition hostile, Crimson Tide friendly), redrawn')
    # the Pilot Analyzer's tag and the Fleet tab row's hover
    pg.evaluate("() => sideEveToggle(true)"); pg.wait_for_function("() => sideEveUse()", timeout=8000)
    pg.evaluate("() => { if(!document.getElementById('pilotSideTag')){ const d = document.createElement('div'); d.id = 'pilotSideTag'; document.body.appendChild(d); } }")
    tags = []
    for cid in (P_VOID, M.pick(98000003, 1)):
        pg.evaluate("(id) => sideTagForPilot(id)", cid); pg.wait_for_timeout(900)
        tags.append(pg.evaluate("() => { const t = document.querySelector('#pilotSideTag .side-tag'); return t ? [t.className, t.textContent, t.title] : null; }"))
    check(tags[0] and 'side-tag n ev' in tags[0][0] and 'Neutral · killed 3 of yours lately' in tags[0][1], f"the Pilot Analyzer's tag: a neutral with evidence says so ({tags[0]})")
    check(tags[1] and 'Hostile · Your alliance: −10 in EVE' in tags[1][1], f"the Pilot Analyzer's tag: EVE's reason ({tags[1]})")
    fr = pg.evaluate("(id) => { const sr = sideOf(" + str(M.TURNCOAT) + ", " + str(M.BCM) + ", sideSets(), sa.evidence, id); return standMark(sr.side, " + str(M.TURNCOAT) + ", " + str(M.BCM) + ", sideWhyText(sr)); }", M.pick(M.TURNCOAT))
    fsrc = re.search(r'\nfunction fkRowHtml\(m\)\{.*?\n\}', PAGE, re.S).group(0)
    check('<title>Hostile: Your alliance: −5 in EVE</title>' in fr and 'standMark(s, m.corp, m.alliance, sideWhyText(sr))' in fsrc and 'sideOf(m.corp, m.alliance, sideSets(), sa.evidence, m.id)' in fsrc,
          f"the Fleet tab row: the pilot's id passed, the icon's hover says why ({re.search(r'<title>[^<]*', fr).group(0) if '<title>' in fr else fr[:80]})")

    # ---- reads: Expires, 5 minutes, redraws ----
    counters(pg); n0 = len(CREQ)
    need(pg); analyze(pg)
    check(len(CREQ) == n0, f'no read before Expires and within 5 minutes ({len(CREQ) - n0})')
    nx = pg.evaluate("() => Math.round((sideEve.next - sideEve.at) / 1000)")
    check(295 <= nx <= 305, f'the next read at Expires, 5 minutes at least ({nx} s)')
    counters(pg); due(pg); need(pg); cn = pg.evaluate("() => __n")
    check(len(CREQ) == n0 + 2 and cn == {'sa': 0, 'rw': 0}, f"due: read again; the same answer redraws nothing ({len(CREQ) - n0} requests, {cn})")
    C['lists']['alliance'][0]['standing'] = 10.0; counters(pg); due(pg); need(pg); cn = pg.evaluate("() => __n"); g = groups(pg)
    check(cn == {'sa': 1, 'rw': 1} and f'f:a{M.CRTS}' in g, f'a changed answer: one redraw, Intel re-worked once ({cn}; Crimson Tide now friendly: {f"f:a{M.CRTS}" in g})')
    C['lists']['alliance'][0]['standing'] = -10.0
    creset(exp=900); due(pg); need(pg); nx = pg.evaluate("() => Math.round((sideEve.next - Date.now()) / 1000)")
    check(890 <= nx <= 905, f'Expires later than 5 minutes: the read waits for it ({nx} s)')
    creset(pages={'alliance': 3, 'corporation': 1}); due(pg); need(pg)
    check([x['page'] for x in reqs('alliance')] == [1, 2, 3] and pg.evaluate("() => sideEve.L.alliance.rows.length") == 8, f"X-Pages 3: pages 1, 2, 3 in order, all entries kept ({[x['page'] for x in reqs('alliance')]})")
    creset(pages={'alliance': 2, 'corporation': 1}, lm={('alliance', 2): 'Mon, 09 Nov 2026 10:05:00 GMT'}); due(pg); need(pg)
    check([x['page'] for x in reqs('alliance')] == [1, 2, 1, 2], f"pages whose Last-Modified differ: read once more ({[x['page'] for x in reqs('alliance')]})")
    creset(mode={'corporation': '403'}); due(pg); need(pg); prof(pg); s = sec(pg)
    qhc = pg.evaluate("() => sideOf(98000012, " + str(M.QHC) + ", sideSets(), null, 1).side")
    check('(SIDE-03)' in s['sec'] and "only your alliance's are used" in s['sec'] and s['use'] and qhc == 'h', f"403 on the corporation's list with the permission: SIDE-03, the alliance's still used ({s['sec'][-120:]!r})")
    creset(mode={'corporation': '403', 'alliance': '403'}); due(pg); need(pg); prof(pg); s = sec(pg)
    check('(SIDE-03)' in s['sec'] and 'your typed lists are used' in s['sec'] and not s['use'], f"403 on both: the typed lists, said so ({s['sec'][-110:]!r})")
    creset(); due(pg); need(pg)
    creset(mode={'alliance': '429'}, ra=45); due(pg); need(pg); nx = pg.evaluate("() => Math.round((sideEve.next - Date.now()) / 1000)")
    check(40 <= nx <= 46 and pg.evaluate("sideEveUse()"), f'a 429: wait its Retry-After, the copy in hand used ({nx} s)')
    creset(mode={'alliance': '503'}); due(pg); need(pg); prof(pg); s = sec(pg)
    nx = pg.evaluate("() => Math.round((sideEve.next - Date.now()) / 1000)")
    check('(SIDE-04)' in s['sec'] and 'copy read before is used' in s['sec'] and s['use'] and 55 <= nx <= 61, f"503: SIDE-04, the copy in hand, again in a minute ({nx} s; {s['sec'][-90:]!r})")
    store = pg.evaluate("() => { const all = [...Object.keys(localStorage).map(k => k + '=' + localStorage.getItem(k)), ...Object.keys(sessionStorage).map(k => k + '=' + sessionStorage.getItem(k))]; return all.filter(x => /" + str(P_BWF) + "|contact_id|standing/.test(x)).length; }")
    check(store == 0, f'nothing of the lists in localStorage or sessionStorage ({store})')
    creset(mode={'alliance': '401'}); due(pg); need(pg); n1 = len(CREQ); due(pg); need(pg); analyze(pg); prof(pg); s = sec(pg)
    check(len(CREQ) == n1 and '(SSO-08)' in s['sec'] and 'Log in again' in s['sec'] and not s['use'] and f'h:a{M.BCM}' in groups(pg),
          f"401: SSO-08 with Log in again, never asked again, the typed lists ({len(CREQ) - n1} more)")
    pg.close(); c.close()
    # no alliance: no alliance request
    c = ctx_new(); creset(aff={'corp': M.CORP, 'alliance': None}); pg = page(c, stand=True, me=dict(ME, alliance=None)); login(pg); need(pg)
    check([x['who'] for x in CREQ] == ['corporation'], f"no alliance: only the corporation's list ({[x['who'] for x in CREQ]})")
    pg.close(); c.close(); creset()

    # ---- Intel: stored sides worked out again ----
    c = ctx_new(); pg = page(c, stand=False); login(pg)
    setup_logs(pg); pg.click('#tabBtnIntel'); pg.click('#intelPanel [data-it-act="folder"]'); pg.wait_for_timeout(400)
    if not pg.is_checked('[data-it-chan="region.intel"]'): pg.check('[data-it-chan="region.intel"]')
    if not pg.is_checked(f'[data-it-me="{MAIN}"]'): pg.check(f'[data-it-me="{MAIN}"]')
    pg.click('#intelSwLabel'); pg.wait_for_function("it.on", timeout=8000); pg.wait_for_timeout(1500)
    name = M.PILOTS[M.pick(98000003, 2)][0]
    pg.evaluate("([n, t]) => __fs.write(n, t)", [F_INTEL, line(time.time(), 'Gate Watcher', f'8WA-Z6 {name}')]); pg.wait_for_timeout(4500)
    ship = pg.evaluate("() => Object.keys(INTEL_SHIPS)[0]")
    pg.evaluate("([id, ship, sys]) => itAddKill({km: {killmail_id: 77000001, killmail_time: new Date().toISOString(), solar_system_id: sys, attackers: [{character_id: id, corporation_id: 98000003, alliance_id: " + str(M.CRTS) + ", ship_type_id: Number(ship), final_blow: true, damage_done: 100}], victim: {character_id: " + str(P_VOID) + ", corporation_id: 98000005, alliance_id: " + str(M.VOIDR) + ", ship_type_id: Number(ship)}}, z: {totalValue: 1}, t: Date.now(), history: false})",
                [M.pick(98000003, 3), ship, SYSID['8WA-Z6']]); pg.wait_for_timeout(300)
    ST = "(n) => { const r = it.feed.find(e => e.kind !== 'kill' && e.raw.includes(n)), k = it.feed.find(e => e.kind === 'kill' && e.kill.id === 77000001), st = it.near.get(" + str(SYSID['8WA-Z6']) + ");" \
         " return {r: r ? [r.pilots.map(x => x.side).join(''), r.friendlyOnly] : null, k: k ? [k.pilots.map(x => x.side).join(''), k.p.ships.length, k.friendlyOnly, k.sighting] : null," \
         " near: st ? st.pilots.filter(x => x.name === n).map(x => x.side).join('') : null, beeps: __fs.beeps, notes: __fs.notes.length}; }"
    a0 = pg.evaluate(ST, name)
    check(a0['r'] == ['f', True] and a0['k'] and a0['k'][:3] == ['f', 0, True], f"before: the report and the kill by a typed friendly are friendly only ({a0})")
    pg.evaluate("() => sideEveToggle(true)"); pg.wait_for_function("() => sideEveUse() && !sideEve.busy", timeout=8000); pg.wait_for_timeout(500)
    a1 = pg.evaluate(ST, name)
    check(a1['r'] == ['h', False] and a1['k'] and a1['k'][:3] == ['h', 1, False] and a1['near'] == 'h', f"EVE's standings in: the report, the kill (its threat ship) and Near You worked out again ({a1})")
    check(a1['beeps'] == a0['beeps'] and a1['notes'] == a0['notes'], f"no alert from the re-work ({a0['beeps']}->{a1['beeps']} sounds, {a0['notes']}->{a1['notes']} notifications)")
    nb = pg.evaluate("() => [...document.querySelectorAll('#intelPanel .it-pl')].filter(x => x.classList.contains('h')).length")
    check(nb >= 1, f'Intel drawn again with the new sides ({nb} hostile names)')
    pg.evaluate("() => sideEveToggle(false)"); pg.wait_for_timeout(300)
    pg.evaluate("(id) => { side.rec.friendly = side.rec.friendly.filter(x => x.id !== id); sideChanged(); }", M.CRTS); pg.wait_for_timeout(300)
    a2 = pg.evaluate(ST, name)
    check(a2['r'] and a2['r'][0] == 'n' and a2['k'][0] == 'n', f"a typed-list edit re-works them too ({a2})")
    pg.close(); c.close()

    # ---- the first read after a reload ----
    c = ctx_new(); pg = page(c, stand=True); login(pg); reset(scp=[SC, SA_]); creset(); pg.evaluate("() => sessionStorage.setItem('__st_delay', '2000')")
    pg.reload(); ready(pg); counters(pg); analyze(pg); g = groups(pg); cn = pg.evaluate("() => __n")
    check(f'h:a{M.CRTS}' in g and cn['sa'] == 1 and len(CREQ) == 2, f"after a reload, Analyze waits for the first read and draws once, with EVE's sides ({cn}, {len(CREQ)} reads)")
    pg.close(); c.close()
    c = ctx_new(); pg = page(c, stand=True); login(pg); creset(); pg.evaluate("() => sessionStorage.setItem('__st_delay', '13000')")
    pg.reload(); ready(pg); counters(pg); t0 = time.time(); analyze(pg); dt = time.time() - t0; g = groups(pg)
    check(9 <= dt <= 13 and f'h:a{M.BCM}' in g and g[f'h:a{M.BCM}']['why'] == 'Your hostile list', f"over 10 s: drawn with the typed lists ({dt:.1f} s)")
    pg.wait_for_function("() => sideEve.tried && !sideEve.busy && sideEveUse()", timeout=30000); pg.wait_for_timeout(400); g = groups(pg)
    check(f'h:a{M.CRTS}' in g and pg.evaluate("() => __n.sa") == 2, f"then drawn again when EVE's standings come in ({pg.evaluate('() => __n')})")
    pg.close(); c.close(); creset()

    # ---- a new tab; Log out ----
    c = ctx_new(); pg = page(c, stand=True); prof(pg)
    sub = pg.evaluate("() => [...document.querySelectorAll('#sidePanel .sso-box .sso-sub .ctx')].map(x => x.textContent)")
    check(sub == ['Also asks for: Corporation contacts, Alliance contacts'], f'logged out with it on: the button asks for both ({sub})')
    login(pg); on(pg); prof(pg); pg.click('[data-sso="logout"]'); pg.wait_for_timeout(500); prof(pg); s = sec(pg)
    check(not s['on'] and s['ls'] == 'false' and not s['use'] and s['typedHidden'] is False, f"Log out: off, the typed lists back ({s['ls']})")
    pg.close(); c.close()

    # ---- 390 px ----
    c = ctx_new(390); pg = page(c); login(pg, scp=()); prof(pg); pg.click('#sidePanel [data-sso="stand"]'); pg.wait_for_timeout(200)
    hh = pg.evaluate("() => document.querySelector('#sidePanel [data-sso=\"st-go\"]').getBoundingClientRect().height"); s = sec(pg)
    check(hh >= 44 and s['sw'] <= s['vw'], f'390 px: Continue to EVE {hh:.0f} px tall, no sideways scroll')
    pg.click('#sidePanel [data-sso="st-no"]'); login(pg); on(pg); prof(pg); pg.click('#sidePanel [data-sso="st-list"]'); pg.wait_for_timeout(500); s = sec(pg)
    check(s['sw'] <= s['vw'], f"390 px: See EVE's standings open, no sideways scroll ({s['sw']} / {s['vw']})")
    pg.close(); c.close()

    # ---- mutants: each must fail the rule or read cases ----
    for name_, a, bb in MUTANTS:
        try: html = mutate(PAGE, a, bb)
        except AssertionError as e: check(False, f'mutant "{name_}": its text is in the page ({e})'); continue
        creset(); c = ctx_new(page_html=html); pg = page(c, stand=True); login(pg); out = []
        try:
            analyze(pg); rule_cases(pg, out)
            n0 = len(CREQ); need(pg)
            if len(CREQ) != n0: out.append('read before Expires')
            creset(mode={'alliance': '401'}); due(pg); need(pg); n1 = len(CREQ); due(pg); need(pg)
            if len(CREQ) != n1: out.append('401 retried')
            st = pg.evaluate("() => Object.keys(localStorage).filter(k => /tvEveCopy/.test(k)).length")
            if st: out.append('stored')
            creset(); pg.evaluate("() => { sideEve.stop = ''; sideEve.msg = null; }"); due(pg); need(pg)
            pg.evaluate("() => { it.feed = [{id: 1, kind: 'seen', t: Date.now(), who: 'x', chan: '', raw: 'x', p: {sys: [], ships: [], extra: 0, count: 0, kw: new Set(), W: [], used: [], mentions: []}, pilots: [{id: " + str(P_RLH) + ", name: 'x', side: 'f'}], history: true}];"
                        " it.aff.set(" + str(P_RLH) + ", {corp: 98000003, alliance: " + str(M.CRTS) + "}); sideEve.key = 'x'; sideEveApplied(); }")
            if pg.evaluate("() => it.feed[0].pilots[0].side") != 'h': out.append('Intel not re-worked')
        except Exception as e: out.append(f'error {str(e)[:60]}')
        pg.close(); c.close()
        if name_.startswith('an NPC'):
            creset(aff={'corp': 1000167, 'alliance': None}); c = ctx_new(page_html=html); pg = page(c, stand=True, me=me_npc); login(pg); pg.evaluate("() => sideEveNeed()"); pg.wait_for_timeout(600)
            if CREQ: out.append('NPC asked')
            pg.close(); c.close(); creset()
        check(bool(out), f'mutant "{name_}" fails the cases ({out[:1]})')
    errs_real = [e for e in errs if 'made-up' not in e]
    check(not errs_real, f'no page errors {errs_real[:3]}')
    b.close()
print(f'\nFAILURES: {fails}')
sys.exit(1 if fails else 0)
