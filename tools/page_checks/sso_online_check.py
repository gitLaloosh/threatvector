"""Show when I'm online in EVE (v2026.11.09.1, build queue 029; Project doc roadmap/sso-online-status-plan.md).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/sso_online_check.py [index.html]   -> 'FAILURES: N' (must be 0)

Never a live login and never live ESI (CLAUDE.md): sso_game_check.py's stand-ins (CCP's login with keys made per run, intel_check.py's
made-up Chatlogs folder, quiet R2Z2), plus a stand-in for ESI's /characters/<id>/online/ that records each request's headers and answers
{"online": true|false} with Expires, X-Ratelimit-*, 401, 403 or 429 as a case sets. Made-up characters and tokens only. Checks:
  * the profile's EVE tab (032): the row before a login too ("Not asked for"); logged in: "Show when I'm online in EVE", unchecked, "Off",
    its info panel with the shared close button; ticked without the permission it waits ("Needs EVE's OK", one Continue to EVE); unticked,
    off; Continue asks EVE for the online scope (and nothing for a feature that is off); back with it: on, tvOnlineShow true, an "Online
    status" tag; Log out keeps the pick (the owner: "keep the picks"), nothing on the portrait; back without the permission: SSO-07, off;
  * one tab, no Intel: one /online/ request with the token, X-Compatibility-Date and X-User-Agent; "Online in EVE · checked hh:mm UTC";
    the portrait's dot (online colour) on its top-right corner, the button's label; the next check at Expires and never under 60 s; no
    request before; logged off: the grey dot, the portrait greyed, "Logged off in EVE"; the same answer again redraws nothing; twice as
    long under a quarter of the group's tokens; a 429 waits its Retry-After; a 401: SSO-08 with Log in again, no second request; a 403:
    SSO-07, off; off: nothing on the portrait, no request; a login without the permission: nothing shown, Continue to EVE; Log out: off, nothing on the portrait;
  * Intel running as You and logged off: "Your character is logged off in EVE." with Stop Intel, above the amber wake line; Intel keeps
    running; Stop Intel stops it; the checks ride Intel's tick (no timer of its own); another character as You: no line;
  * two tabs logged in as the same character: one asks, the other shows what it heard; a tab opened later hears it at once; a hidden tab
    without Intel lets go and asks nothing, the other takes over; the tab running Intel takes it over; a tab leaving for EVE's page lets
    go first; a tab waiting 3 minutes without an answer takes over;
  * the dot and Intel's square never overlap (clear, not working, near, in system) at 1440 and 390 px; 390 px: Continue to EVE and Stop
    Intel 44 px tall, no sideways scroll; no page errors.
"""
import sys, os, re, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
G = open(os.path.join(HERE, 'sso_game_check.py'), encoding='utf-8').read()
exec(compile(G[:G.index('from playwright.sync_api import sync_playwright\nwith')], 'sso_game_check', 'exec'))   # its stand-ins and helpers
ON = 'esi-location.read_online.v1'

# ---- the stand-in ESI online route ----
O, OREQ = {}, []
def oreset(**o):
    OREQ.clear(); O.clear(); O.update({'mode': 'ok', 'online': True, 'exp': 60, 'lim': '1200/15m', 'rem': 1100, 'ra': 20}); O.update(o)
oreset()
def esi_on(route):
    u = route.request.url
    m = re.search(r'/characters/(\d+)/online/', u)
    if not m: return esi_loc(route)
    OREQ.append({'t': time.time(), 'id': int(m.group(1)), 'h': {k.lower(): v for k, v in route.request.headers.items()}})
    hd = {'access-control-allow-origin': '*', 'access-control-expose-headers': 'x-ratelimit-group, x-ratelimit-limit, x-ratelimit-remaining, retry-after, expires',
          'x-ratelimit-group': 'char-location', 'x-ratelimit-limit': O['lim'], 'x-ratelimit-remaining': str(O['rem']),
          'expires': time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(time.time() + O['exp']))}
    md = O['mode']
    if md in ('401', '403'): return route.fulfill(status=int(md), content_type='application/json', headers=hd, body='{"error":"made-up"}')
    if md == '429': hd['retry-after'] = str(O['ra']); return route.fulfill(status=429, content_type='application/json', headers=hd, body='{"error":"made-up"}')
    return route.fulfill(status=200, content_type='application/json', headers=hd, body=json.dumps({'online': O['online'], 'logins': 7}))
toks = lambda: [x['h'].get('authorization', '') for x in OREQ]

STO = """() => { const q = (s) => document.querySelector(s), t = (x) => x ? x.textContent.replace(/\\s+/g, ' ').trim() : '';
  const row = q('#eveTab [data-feat="online"]'), cb = q('#ppSw-online'), dot = q('#profileOn'), pf = q('#profile');
  return {row: row ? t(row) : null, cb: cb ? cb.checked : null, ask: !!q('#eveTab [data-sso="eve-go"]'), show: ssoOn.show, held: !!ssoOn.held,
    queued: !!ssoOn.req, stop: ssoOn.stop, st: ssoOn.st, ls: localStorage.getItem('tvOnlineShow'), on: pf.dataset.on || null,
    dot: dot && !dot.hidden ? (dot.classList.contains('off') ? 'off' : 'on') : null, lbl: q('#profileBtn').getAttribute('aria-label'),
    av: getComputedStyle(q('#profileAv')).filter, notes: t(q('#itNotes')), it: it.on, timer: ssoOn.timer, who: sso.who, side: t(q('#profilePanel')),
    sw: document.documentElement.scrollWidth, vw: innerWidth}; }"""

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    errs = []
    def serve(route):
        return route.fulfill(status=200, content_type='text/html; charset=utf-8', body=PAGE) if urllib.parse.urlsplit(route.request.url).path == '/' else route.fulfill(status=404, body='')
    def ctx_new(w=1440):
        c = b.new_context(bypass_csp=True, viewport={'width': w, 'height': 1000})
        c.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
        c.add_init_script(FS); c.add_init_script(EXTRA); route(c)
        c.route(re.compile(r'https://esi\.evetech\.net/.*'), esi_on)
        c.route(re.compile(r'https://login\.eveonline\.com/.*'), sso)
        c.route(re.compile(r'^http://localhost:8000/.*'), serve)
        return c
    def ready(pg): pg.wait_for_function("typeof it !== 'undefined' && it.loaded", timeout=10000); pg.wait_for_timeout(300)
    def page(c, show=None, first=True, intel=None):
        pg = c.new_page(); pg.goto(DEV_ORIGIN + '/')
        if first:
            pg.evaluate("([s, i, o]) => { localStorage.setItem('dscanSide', JSON.stringify(s)); if(i) localStorage.setItem('dscanIntel', JSON.stringify(i)); else localStorage.removeItem('dscanIntel'); if(o === null) localStorage.removeItem('tvOnlineShow'); else localStorage.setItem('tvOnlineShow', JSON.stringify(o)); }", [YOU, intel, show])
            pg.reload()
        ready(pg); return pg
    def folder(pg):
        setup_logs(pg); pg.click('#tabBtnIntel'); pg.click('#intelPanel [data-it-act="folder"]'); pg.wait_for_timeout(400)
        if not pg.is_checked('[data-it-chan="region.intel"]'): pg.check('[data-it-chan="region.intel"]')
        if not pg.is_checked(f'[data-it-me="{MAIN}"]'): pg.check(f'[data-it-me="{MAIN}"]')
        pg.wait_for_timeout(200)
    def login(pg, scp=(ON,), tab='madeUpTabId0029', tok='madeUpAccessToken'):
        pg.evaluate("([id, scp, tab, rt, tok]) => { sso.who = {id, name: 'Your Main'}; sso.access = tok; sso.exp = Date.now() + 1200000; sso.scp = scp;"
                    " ssoSet(SSO_REFRESH, rt); ssoSet(SSO_WHO, JSON.stringify(sso.who)); ssoSet(SSO_TAB, tab); ssoOn.stop = ''; ssoOn.next = 0; renderSidePanel(); ssoOnPump(); ssoOnHello(); }", [MAIN, list(scp), tab, REFRESH, tok])
    def show_on(pg): pg.evaluate("() => { ssoOnSave(true); ssoOn.next = 0; ssoOnPump(); ssoOnRedraw(); }")
    def now(pg): pg.evaluate("() => { ssoOn.next = 0; ssoOnArm(); }")   # the next check is due
    def gear(pg): pg.evaluate("() => { switchTab('intel'); it.pop = true; itRender(true); }"); pg.wait_for_timeout(100)
    def prof(pg): pg.evaluate("() => { openProfile('eve'); renderSidePanel(); }"); pg.wait_for_timeout(150)   # 032: the switch is on the profile's EVE tab
    def intel_on(pg): pg.click('#intelSwLabel'); pg.wait_for_function("it.on", timeout=8000); pg.wait_for_timeout(300)
    def hide(pg, h):
        pg.evaluate("(h) => { Object.defineProperty(document, 'hidden', {value: h, configurable: true}); Object.defineProperty(document, 'visibilityState', {value: h ? 'hidden' : 'visible', configurable: true}); document.dispatchEvent(new Event('visibilitychange')); }", h)
    sto = lambda pg: pg.evaluate(STO)

    # ---- the Pilot section; the permission step ----
    c = ctx_new(); pg = page(c); prof(pg); s = sto(pg)
    check(s['row'] and 'Not asked for' in s['row'] and s['cb'] is False and not s['show'], f'no login: the row, unchecked, "Not asked for" (picked before you go) ({s["row"]!r})')
    login(pg, scp=()); prof(pg); s = sto(pg)
    check(s['row'] and "Show when I'm online in EVE" in s['row'] and 'Off' in s['row'] and s['cb'] is False, f"logged in: the row, unchecked, its line ({s['row']!r})")
    pg.click('#eveTab [data-feat="online"] summary.info-btn'); pg.wait_for_timeout(200)
    ip = pg.evaluate("() => { const d = [...document.querySelectorAll('[role=dialog]')].find(x => x.offsetParent && /How online status works/.test(x.textContent)); return d ? [!!d.querySelector('button.x-close'), d.textContent.length] : null; }")
    check(ip and ip[0], f'its info panel: "How online status works", the shared close button ({ip})')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(100); prof(pg)
    pg.click('#ppSw-online'); pg.wait_for_timeout(200); s = sto(pg)
    check(s['ask'] and s['show'] and "Needs EVE's OK" in s['row'] and not s['held'] and not OREQ, f"ticked without the permission: it waits, Continue to EVE, nothing asked ({s['row'][:90]!r})")
    pg.click('#ppSw-online'); pg.wait_for_timeout(150); s = sto(pg)
    check(not s['ask'] and not s['show'] and s['ls'] == 'false', 'unticked: off, nothing waiting')
    reset(scp=[ON]); pg.click('#ppSw-online'); pg.wait_for_timeout(150)
    pg.click('#eveTab [data-sso="eve-go"]'); pg.wait_for_url(DEV_ORIGIN + '/**', timeout=8000); ready(pg); pg.wait_for_timeout(900)
    auth = [x for x in LOG if x[0] == '/v2/oauth/authorize']; q = auth[0][2] if auth else {}
    check(q.get('scope') == ON, f"Continue to EVE: EVE is asked for the online scope (nothing for a feature that's off) ({q.get('scope')!r})")
    prof(pg); s = sto(pg)
    check(s['show'] and s['ls'] == 'true' and s['cb'] is True and "Needs EVE's OK" not in s['row'], f"back with it: on, tvOnlineShow true ({s['ls']}; {s['row'][:80]!r})")
    tg = pg.evaluate("() => [...document.querySelectorAll('#eveTab .sso-perms .sso-tag')].map(x => x.textContent)")
    check(tg == ['Online status'], f'the profile: an "Online status" tag {tg}')
    prof(pg); pg.click('[data-sso="logout"]'); pg.wait_for_timeout(400); s = sto(pg)
    check(s['show'] and s['ls'] == 'true' and s['dot'] is None and s['on'] is None, f'Log out keeps the pick (the owner: "keep the picks"); nothing on the portrait ({s["ls"]}, {s["dot"]})')
    oreset()
    sub = pg.evaluate("() => { renderSidePanel(); return [...document.querySelectorAll('#eveTab .sso-sub .ctx')].map(x => x.textContent); }")
    check(sub == ['EVE will ask for 1 permission'], f'logged out with it on: the login says "EVE will ask for 1 permission" ({sub})')
    login(pg, scp=()); prof(pg); reset(scp=[])
    pg.click('#eveTab [data-sso="eve-go"]'); pg.wait_for_url(DEV_ORIGIN + '/**', timeout=8000); ready(pg); pg.wait_for_timeout(900); prof(pg); s = sto(pg)
    check(not s['show'] and '(SSO-07)' in s['row'], f"back without the permission: SSO-07, off ({s['row'][-100:]!r})")
    check(not OREQ, f'no /online/ request after Log out, while it was off ({len(OREQ)})')
    pg.close(); c.close()

    # ---- one tab, no Intel: the checks ----
    c = ctx_new(); pg = page(c, show=False); oreset(); login(pg); pg.wait_for_timeout(1500)
    check(not OREQ, 'logged in with the permission, the setting off: no request')
    show_on(pg); pg.wait_for_timeout(1500); prof(pg); s = sto(pg)
    h = OREQ[0]['h'] if OREQ else {}
    check(len(OREQ) == 1 and OREQ[0]['id'] == MAIN and s['held'], f'on: one /online/ request for the login\'s character ({len(OREQ)})')
    check(h.get('authorization') == 'Bearer madeUpAccessToken' and h.get('x-compatibility-date') == COMPAT and 'threatvectorapp@gmail.com' in h.get('x-user-agent', ''),
          f"the request: the token, X-Compatibility-Date, X-User-Agent ({sorted(k for k in h if k.startswith('x-') or k == 'authorization')})")
    check(re.search(r'Online in EVE · checked \d\d:\d\d UTC', s['row'] or '') and s['dot'] == 'on' and s['on'] == 'on' and 'online in EVE' in s['lbl'] and 'grayscale' not in s['av'],
          f"\"Online in EVE · checked hh:mm UTC\"; the dot; the button's label ({s['row'][-50:]!r}; {s['lbl']!r})")
    col = pg.evaluate("() => [getComputedStyle(document.getElementById('profileOn')).backgroundColor, getComputedStyle(document.documentElement).getPropertyValue('--cap-good').trim()]")
    check(col[0] == 'rgb(31, 174, 74)' and col[1] == '#1fae4a', f'the dot in --st-online ({col})')
    pos = pg.evaluate("() => { const a = document.getElementById('profileAv').getBoundingClientRect(), d = document.getElementById('profileOn').getBoundingClientRect(); return [d.left + d.width / 2 - a.right, d.top + d.height / 2 - a.top]; }")
    check(-6 <= pos[0] <= 1 and -1 <= pos[1] <= 6, f'the dot on the portrait\'s top-right corner (its centre {pos[0]:.1f}, {pos[1]:.1f} px from the corner)')
    nx = pg.evaluate("() => ssoOn.next - ssoOn.st.at")
    check(59900 <= nx <= 61200, f'the next check at Expires, 60 s here ({nx / 1000:.1f} s)')
    n0 = len(OREQ); pg.wait_for_timeout(2500)
    check(len(OREQ) == n0 and s['timer'], f'no request before then (one timer armed) ({len(OREQ) - n0})')
    oreset(exp=5); now(pg); pg.wait_for_timeout(1200); nx = pg.evaluate("() => ssoOn.next - ssoOn.st.at")
    check(len(OREQ) == 1 and 59900 <= nx <= 61200, f'Expires in 5 s: still 60 s at least ({nx / 1000:.1f} s)')
    O['online'] = False; O['exp'] = 60; now(pg); pg.wait_for_timeout(1200); s = sto(pg)
    check(s['dot'] == 'off' and s['on'] == 'off' and 'grayscale(1)' in s['av'] and 'Logged off in EVE · checked' in s['row'] and 'logged off in EVE' in s['lbl'],
          f"logged off: the grey dot, the portrait greyed, the line ({s['av']}; {s['row'][-45:]!r})")
    pg.evaluate("() => { window.__d = 0; const r = renderProfile; renderProfile = function(){ window.__d++; return r.apply(this, arguments); }; const rs = renderSidePanel; renderSidePanel = function(){ window.__d++; return rs.apply(this, arguments); };"
                " new MutationObserver((ms) => { for(const m of ms) if(!(m.target.closest && m.target.closest('[data-sso-onat]'))) window.__d++; }).observe(document.querySelector('#eveTab [data-feat=\"online\"]'), {childList: true, subtree: true, characterData: true}); }")
    n0 = len(OREQ); now(pg); pg.wait_for_timeout(1200); now(pg); pg.wait_for_timeout(1200)
    check(len(OREQ) == n0 + 2 and pg.evaluate("window.__d") == 0, f'the same answer again draws nothing ({len(OREQ) - n0} answers, {pg.evaluate("window.__d")} redraws)')
    O['rem'] = 100; now(pg); pg.wait_for_timeout(1200); nx = pg.evaluate("() => ssoOn.next - Date.now()")
    check(115000 <= nx <= 122500, f'under a quarter of the tokens left: twice as long ({nx / 1000:.1f} s)')
    O['rem'] = 1100; O['mode'] = '429'; n0 = len(OREQ); now(pg); pg.wait_for_timeout(1200); nx = pg.evaluate("() => ssoOn.next - Date.now()")
    check(len(OREQ) == n0 + 1 and 17000 <= nx <= 20100, f'a 429 waits its Retry-After ({nx / 1000:.1f} s)')
    O['mode'] = '401'; n0 = len(OREQ); now(pg); pg.wait_for_timeout(1200); now(pg); pg.wait_for_timeout(1500); prof(pg); s = sto(pg)
    check(len(OREQ) == n0 + 1 and s['stop'] == 'SSO-08' and '(SSO-08)' in s['row'] and 'Log in again' in s['row'] and not s['held'], f"a 401: SSO-08 with Log in again, no second request, the lock let go ({len(OREQ) - n0})")
    O['mode'] = '403'; login(pg); pg.wait_for_timeout(1200); prof(pg); s = sto(pg)
    check(not s['show'] and s['ls'] == 'false' and '(SSO-07)' in s['row'] and s['dot'] is None, f"a 403: SSO-07, off, nothing on the portrait ({s['row'][-90:]!r})")
    O['mode'] = 'ok'; n0 = len(OREQ); now(pg); pg.wait_for_timeout(1500)
    check(len(OREQ) == n0 and not sto(pg)['held'], 'off: no request, no lock')
    # on in this browser (another tab turned it on), this tab's login without the permission, an answer heard from another tab: nothing shown
    pg.evaluate("(id) => { sso.scp = []; ssoOnSave(true); ssoOnPump(); ssoOnSeen({id, online: true, at: Date.now() + 1000}, false); ssoOnRedraw(); }", MAIN); prof(pg); s = sto(pg)
    check(s['dot'] is None and s['on'] is None and "Needs EVE's OK" in s['row'] and s['ask'] and not s['held'],
          f"this tab's login without the permission: nothing on the portrait, Continue to EVE ({s['dot']}; {s['row'][-80:]!r})")
    pg.close(); c.close()

    # ---- Intel running, logged off ----
    c = ctx_new(); pg = page(c, show=True); oreset(online=False); folder(pg); login(pg); pg.wait_for_timeout(1200)
    s = sto(pg)
    check(s['dot'] == 'off' and not s['notes'].count('logged off in EVE'), 'Intel off: the portrait says logged off; no line in Intel')
    intel_on(pg); pg.wait_for_timeout(800); s = sto(pg)
    check(s['it'] and 'Your character is logged off in EVE.' in s['notes'] and 'Stop Intel' in s['notes'], f"Intel running as You, logged off: the line and Stop Intel ({s['notes'][:70]!r})")
    check(s['timer'] == 0 and s['held'], f'the tab running Intel asks on its tick (no timer of its own) ({s["timer"]})')
    n0 = len(OREQ); now(pg); pg.wait_for_timeout(2600)
    check(len(OREQ) == n0 + 1, f"Intel's tick makes the check when it's due ({len(OREQ) - n0})")
    pg.evaluate("() => { it.note = IT_WAKE_NOTE; itRender(true); }"); pg.wait_for_timeout(100)
    od = pg.evaluate("() => { const n = document.getElementById('itNotes'), a = n.querySelector('[data-it-offl]'), w = n.querySelector('.it-wake'); return a && w ? !!(a.compareDocumentPosition(w) & Node.DOCUMENT_POSITION_FOLLOWING) : null; }")
    check(od is True, f'the line sits above the amber wake line (the owner, at the review) ({od})')
    pg.wait_for_timeout(2500)
    check(sto(pg)['it'], 'Intel keeps running (it never stops by itself)')
    O['online'] = True; now(pg); pg.wait_for_timeout(2600)
    check('logged off in EVE' not in sto(pg)['notes'], 'online again: the line goes')
    O['online'] = False; now(pg); pg.wait_for_timeout(2600)
    pg.click('#itNotes [data-it-act="on-stop"]'); pg.wait_for_timeout(500); s = sto(pg)
    check(not s['it'] and 'logged off in EVE' not in s['notes'] and s['timer'], f'Stop Intel stops it; the line goes; the check back on its own timer ({s["timer"]})')
    gear(pg); pg.check(f'[data-it-me="{ALT}"]'); pg.wait_for_timeout(100); intel_on(pg); pg.wait_for_timeout(500)
    check('logged off in EVE' not in sto(pg)['notes'], 'another character as You: no line')
    pg.click('#intelSwLabel'); pg.wait_for_timeout(300)
    # 390 px: Stop Intel's height
    gear(pg); pg.check(f'[data-it-me="{MAIN}"]'); pg.evaluate("() => { it.pop = false; itRender(true); }"); pg.set_viewport_size({'width': 390, 'height': 900}); intel_on(pg); pg.wait_for_timeout(500)
    hh = pg.evaluate("() => { const x = document.querySelector('#itNotes [data-it-act=\"on-stop\"]'); return x ? x.getBoundingClientRect().height : 0; }"); s = sto(pg)
    check(hh >= 44 and s['sw'] <= s['vw'], f'390 px: Stop Intel {hh:.0f} px tall, no sideways scroll')
    pg.close(); c.close()

    # ---- two tabs, the same character ----
    c = ctx_new(); oreset(); A = page(c, show=True); login(A, tok='madeUpTokenA'); A.wait_for_timeout(1200)
    B = page(c, first=False); login(B, tab='madeUpTabId0030', tok='madeUpTokenB'); B.wait_for_timeout(800)
    sB = sto(B)
    check(set(toks()) == {'Bearer madeUpTokenA'} and sB['queued'] and not sB['held'] and sB['st'] and sB['st']['online'] is True and sB['dot'] == 'on',
          f'two tabs: one asks; a tab opened later hears the answer at once and waits in line ({set(toks())}, B {sB["dot"]})')
    now(A); now(B); A.wait_for_timeout(1500)
    check(toks().count('Bearer madeUpTokenB') == 0 and len(OREQ) == 2, f'one request per period ({len(OREQ)} requests)')
    O['online'] = False; now(A); A.wait_for_timeout(1500); sB = sto(B)
    check(sB['dot'] == 'off' and toks().count('Bearer madeUpTokenB') == 0, f"the other tab shows what it heard ({sB['dot']})")
    n0 = len(OREQ); hide(A, True); A.wait_for_timeout(1500); sA, sB = sto(A), sto(B)
    wB = B.evaluate("() => Math.round((ssoOn.next - ssoOn.st.at) / 1000)")
    check(not sA['held'] and not sA['queued'] and sB['held'] and len(OREQ) == n0 and 58 <= wB <= 62,
          f"a hidden tab without Intel lets go; the other takes over and waits for the other tab's next check, never sooner (the owner's hand test) ({sA['held']}, {sB['held']}, {len(OREQ) - n0} requests, next {wB} s after the last answer)")
    now(B); B.wait_for_timeout(1500)
    check(toks()[-1] == 'Bearer madeUpTokenB', 'when it is due, the tab that took over asks')
    n0 = len(OREQ); now(A); A.wait_for_timeout(1500)
    check(toks()[n0:].count('Bearer madeUpTokenA') == 0, 'the hidden tab asks nothing')
    hide(A, False); A.wait_for_timeout(600); folder(A); intel_on(A); A.wait_for_timeout(800); sA, sB = sto(A), sto(B)
    check(sA['held'] and not sB['held'] and sB['queued'], f'the tab running Intel takes it over ({sA["held"]}, B queued {sB["queued"]})')
    n0 = len(OREQ); now(A); now(B); A.wait_for_timeout(2600)
    check(toks()[n0:] == ['Bearer madeUpTokenA'], f'then only it asks ({toks()[n0:]})')
    hide(A, True); A.wait_for_timeout(800)
    check(sto(A)['held'], 'hidden while it runs Intel: it keeps asking')
    hide(A, False); A.click('#intelSwLabel'); A.wait_for_timeout(500)
    # A leaves for EVE's page: it lets go first, so B takes over at once
    reset(nav=False); A.evaluate("() => { ssoOn.held || ssoOnTake(false); }"); A.wait_for_timeout(300)
    # let go before the page leaves (a page kept in the browser's cache may keep its lock): noted only when not from pagehide
    A.evaluate("() => { const f = ssoOnFree; ssoOnFree = function(){ if(ssoOn.held && (sso.leaving || sso.starting) && !(window.event && window.event.type === 'pagehide')) __tS('freed', 1); return f.apply(this, arguments); }; }")
    hA = sto(A)['held']; A.evaluate("() => { it.set.gameLoc = true; renderSidePanel(); }"); prof(A); A.click('#eveTab [data-sso="eve-go"]'); A.wait_for_url('https://login.eveonline.com/**', timeout=8000)
    B.wait_for_timeout(800); hB = sto(B)['held']
    S['nav'] = True; A.go_back(); ready(A); fr = A.evaluate("() => __tS('freed')")
    check(hA and fr == 1 and hB, f'a tab leaving for EVE\'s page lets go first: the other takes over ({hA}, let go before leaving {fr}, {hB})')
    A.close()
    # a tab waiting without hearing an answer for 3 minutes takes over (one that still holds it went quiet)
    C = page(c, first=False); login(C, tab='madeUpTabId0031', tok='madeUpTokenC'); C.wait_for_timeout(500)
    q0 = sto(C)['queued']
    C.evaluate("() => { ssoOn.heard = ssoOn.waitAt = Date.now() - 181000; ssoOnTick(); }"); C.wait_for_timeout(600); sC, sB = sto(C), sto(B)
    check(q0 and sC['held'] and not sB['held'] and sB['queued'], f'waiting 3 minutes without an answer: it takes over; the other waits in line ({q0}, C {sC["held"]}, B {sB["queued"]})')
    B.close(); C.close(); c.close()

    # ---- the dot and Intel's square ----
    for w in (1440, 390):
        c = ctx_new(w); pg = page(c, show=True); oreset(online=False); login(pg); pg.wait_for_timeout(1200)
        ov = pg.evaluate("""() => { const pf = document.getElementById('profile'), b = document.getElementById('intelNear'), d = document.getElementById('profileOn'), out = {};
          b.hidden = false;
          for(const s of ['clear', 'broken', 'near', 'in']){ pf.dataset.s = s; const x = b.getBoundingClientRect(), y = d.getBoundingClientRect(), a = document.getElementById('profileAv').getBoundingClientRect();
            out[s] = [!(x.right <= y.left || y.right <= x.left || x.bottom <= y.top || y.bottom <= x.top), Math.round(y.left + y.width / 2 - a.right), Math.round(y.top + y.height / 2 - a.top)]; }
          return out; }""")
        check(not any(v[0] for v in ov.values()) and all(-6 <= v[1] <= 1 and -1 <= v[2] <= 6 for v in ov.values()), f'{w} px: the dot on the portrait\'s corner never overlaps Intel\'s square {ov}')
        s = sto(pg)
        check(s['sw'] <= s['vw'], f'{w} px: no sideways scroll')
        if w == 390:
            pg.evaluate("() => { ssoOnSave(false); sso.scp = []; ssoOnRedraw(); }"); prof(pg); pg.click('#ppSw-online'); pg.wait_for_timeout(200)
            hh = pg.evaluate("() => document.querySelector('#eveTab [data-sso=\"eve-go\"]').getBoundingClientRect().height"); s = sto(pg)
            check(hh >= 44 and s['sw'] <= s['vw'], f'390 px: Continue to EVE {hh:.0f} px tall, no sideways scroll')
        c.close()
    check(not errs, f'no page errors {errs[:3]}')
    b.close()
print(f'\nFAILURES: {fails}')
sys.exit(1 if fails else 0)
