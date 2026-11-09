"""SSO Phase 2, Use my game location (v2026.11.08.4, build queue 028; Project doc roadmap/sso-phase2-plan.md).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/sso_game_check.py [index.html]   -> 'FAILURES: N' (must be 0)

Never a live login and never live ESI (CLAUDE.md): login.eveonline.com is a stand-in with keys made for this run (as sso_check.py), and
ESI's /characters/<id>/location/ is a stand-in that records each request's headers and answers with Expires, X-Ratelimit-*, 401, 403 or
429 as a case sets. The page is served at the dev app's address (http://localhost:8000/), with intel_check.py's made-up Chatlogs folder
and quiet R2Z2; the folder, its files and the folder's permission are kept in sessionStorage across the trip to EVE's page (the page's
own IndexedDB store is a stand-in, as in intel_folder_check.py). Made-up characters and tokens only. Checks:
  * a new user: sound and desktop notification unchecked, and Intel's switch asks the browser for no notification permission; a saved
    sound and notification stay on;
  * box 3: Use my game location, unchecked, "Needs your EVE login and its OK", its info panel with the shared close button; ticking it
    without a login opens Continue to EVE / Cancel; Cancel closes it; Continue asks EVE for the location scope only (never a ship scope);
  * back from EVE: the scope as an array and as a string turns the switch on; without it, SSO-07 and the switch stays off; the profile:
    "EVE permissions:" with a Location tag and Manage on EVE's site (through the outside-link gate); the profile's button says "Also asks
    for: Location" and asks for it; Log out turns the switch off and says the permissions ended with it;
  * Intel running, logged in as You: every location request has the token, X-Compatibility-Date and X-User-Agent; the game's system,
    when it differs from the Local log, is used (the status line, the amber line); the log catching up: "the same as your Local log";
    the next check never before Expires; twice as long under a quarter of the group's tokens; a 429 waits its Retry-After; a 401: SSO-08
    and no second request; a 403: SSO-07 and the switch off; nothing drawn when an answer changes nothing;
  * renewal: under a minute left renews first (grant_type refresh_token, the refresh token and the Client ID, no secret); two calls at
    once renew once; a new refresh token is stored before the next request; invalid_grant: SSO-06, the login ends, Log in again; a 429
    waits its Retry-After; an HTML 500: 30 s;
  * the login's character not You: one amber line, no request; Intel off, or the tab without the lock: no request; no /ship/ or /online/;
  * a duplicated tab (the same tvSsoTab answered on the channel) drops its login; the original keeps it;
  * the Back-button bug: Back from EVE's page (Playwright go_back) and a synthetic pageshow with persisted: the EVE button, never
    "Checking your login with EVE…", tvSsoPending gone, "nothing changed"; the same for Use my game location's Continue; a normal load
    drops a stale tvSsoPending; the real return still logs in;
  * Intel after the trip: running before, it runs again after Authorize and after Cancel; off before, or a stale or foreign pending entry:
    off; the folder needing a click: Allow reading, nothing read until it's pressed, then Intel runs; sound on: the "click anywhere" line,
    gone after a click; the other tab: "Intel is paused while the other tab logs in with EVE.", then "Intel is on in another tab.";
  * Intel stopped reading (the folder throws NotAllowedError): one sound with sound on, none with sound off, none on the next ticks, none
    on a stop by hand; the sound isn't Near You's or In system's;
  * 390 px: Continue to EVE 44 px tall, no sideways scroll; no page errors.
"""
import sys, os, re, json, time, base64, hashlib, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SRC = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
exec(compile(SRC[:SRC.index('with sync_playwright() as p:')], 'intel_check', 'exec'))   # its folder stand-in, logs, ESI and R2Z2 routes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

fails = 0
def check(ok, msg):
    global fails
    print(('ok   ' if ok else 'FAIL ') + msg)
    if not ok: fails += 1

PAGE = open(HTML, encoding='utf-8').read()
DEV, DEV_ORIGIN = '659bdd63a604458e95c419de3373fdc3', 'http://localhost:8000'
LOC = 'esi-location.read_location.v1'
COMPAT = re.search(r"const ESI_COMPAT = '([\d-]+)'", PAGE).group(1)
REFRESH = 'madeUpRefreshToken0028'
YOU = {'pilot': {'id': MAIN, 'name': 'Your Main'}, 'corp': {'id': M.CORP, 'name': 'Example Corp', 'kind': 'corporation'}, 'alliance': None, 'friendly': [], 'hostile': [], 'rows': 15}

# ---- keys made for this run; the stand-in SSO ----
RSA = rsa.generate_private_key(public_exponent=65537, key_size=2048)
b64u = lambda b: base64.urlsafe_b64encode(b).rstrip(b'=').decode()
def int_b64u(n): return b64u(n.to_bytes((n.bit_length() + 7) // 8, 'big'))
rn = RSA.public_key().public_numbers()
JWKS = {'keys': [{'kty': 'RSA', 'alg': 'RS256', 'kid': 'JWT-Signature-Key', 'use': 'sig', 'n': int_b64u(rn.n), 'e': int_b64u(rn.e)}]}
def jwt(c):
    h = b64u(json.dumps({'alg': 'RS256', 'kid': 'JWT-Signature-Key', 'typ': 'JWT'}).encode()); bd = b64u(json.dumps(c).encode())
    return h + '.' + bd + '.' + b64u(RSA.sign((h + '.' + bd).encode(), padding.PKCS1v15(), hashes.SHA256()))
def claims(cid, scp, sub=MAIN, name='Your Main', life=1200):
    c = {'jti': 'madeUpJti', 'kid': 'JWT-Signature-Key', 'sub': f'CHARACTER:EVE:{sub}', 'azp': cid, 'tenant': 'tranquility', 'tier': 'live',
         'region': 'world', 'aud': [cid, 'EVE Online'], 'name': name, 'owner': 'madeUpOwnerHash=', 'exp': int(time.time()) + life,
         'iat': int(time.time()), 'iss': 'https://login.eveonline.com'}
    if scp is not None: c['scp'] = scp
    return c
S, LOG = {}, []
def reset(**o):
    LOG.clear(); S.clear(); S.update({'deny': False, 'scp': [LOC], 'nav': True, 'refresh': 'ok', 'rotate': 0}); S.update(o)
reset()
def sso(route):
    req = route.request; u = urllib.parse.urlsplit(req.url); path = u.path
    form = dict(urllib.parse.parse_qsl(req.post_data or '')) if req.method == 'POST' else dict(urllib.parse.parse_qsl(u.query))
    LOG.append((path, req.method, form, time.time()))
    j = lambda o, st=200, hd=None: route.fulfill(status=st, content_type='application/json; charset=utf-8', headers=dict({'access-control-allow-origin': '*', 'access-control-expose-headers': 'retry-after'}, **(hd or {})), body=json.dumps(o))
    H = 'https://login.eveonline.com'
    if path == '/.well-known/oauth-authorization-server':
        return j({'issuer': H, 'authorization_endpoint': H + '/v2/oauth/authorize', 'token_endpoint': H + '/v2/oauth/token', 'jwks_uri': H + '/oauth/jwks',
                  'revocation_endpoint': H + '/v2/oauth/revoke', 'code_challenge_methods_supported': ['S256']})
    if path == '/oauth/jwks': return j(JWKS)
    if path == '/v2/oauth/authorize':
        S['challenge'] = form.get('code_challenge')
        if not S['nav']: return route.fulfill(status=200, content_type='text/html', body='<!doctype html><p>made-up authorize page</p>')
        back = form.get('redirect_uri', '') + '?' + urllib.parse.urlencode({'error': 'access_denied', 'state': form.get('state', '')} if S['deny'] else {'code': 'madeUpCode0028', 'state': form.get('state', '')})
        return route.fulfill(status=200, content_type='text/html', body=f'<!doctype html><script>location.replace({json.dumps(back)})</script>')
    if path == '/v2/oauth/token':
        cid = form.get('client_id')
        if form.get('grant_type') == 'refresh_token':
            m = S['refresh']
            if m == 'invalid_grant': return j({'error': 'invalid_grant', 'error_description': 'made-up: revoked'}, 400)
            if m == '429': return j({'error': 'slow down'}, 429, {'retry-after': '40'})
            if m == 'html500': return route.fulfill(status=500, content_type='text/html', body='<html>made-up error page</html>')
            S['rotate'] += 1
            return j({'access_token': jwt(claims(cid, S['scp'])), 'expires_in': 1199, 'token_type': 'Bearer', 'refresh_token': f'madeUpRotated{S["rotate"]:04d}'})
        v = form.get('code_verifier', '')
        if b64u(hashlib.sha256(v.encode()).digest()) != S.get('challenge'): return j({'error': 'invalid_grant'}, 400)
        return j({'access_token': jwt(claims(cid, S['scp'])), 'expires_in': 1199, 'token_type': 'Bearer', 'refresh_token': REFRESH})
    if path == '/v2/oauth/revoke': return route.fulfill(status=200, body='')
    return j({'error': 'not in the stand-in'}, 404)

# ---- the stand-in ESI location route ----
L = {}
LREQ, BAD = [], []
def lreset(**o):
    LREQ.clear(); L.clear(); L.update({'mode': 'ok', 'sys': SYSID['8WA-Z6'], 'exp': 5, 'lim': '600/15m', 'rem': 550, 'ra': 20}); L.update(o)
lreset()
def esi_loc(route):
    u = route.request.url
    if re.search(r'/characters/\d+/(ship|online)/', u): BAD.append(u); return route.fulfill(status=404, body='')
    m = re.search(r'/characters/(\d+)/location/', u)
    if m:
        LREQ.append({'t': time.time(), 'id': int(m.group(1)), 'h': {k.lower(): v for k, v in route.request.headers.items()}})
        hd = {'access-control-allow-origin': '*', 'access-control-expose-headers': 'x-ratelimit-group, x-ratelimit-limit, x-ratelimit-remaining, retry-after, expires',
              'x-ratelimit-group': 'char-location', 'x-ratelimit-limit': L['lim'], 'x-ratelimit-remaining': str(L['rem']),
              'expires': time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(time.time() + L['exp']))}
        md = L['mode']
        if md in ('401', '403'): return route.fulfill(status=int(md), content_type='application/json', headers=hd, body='{"error":"made-up"}')
        if md == '429': hd['retry-after'] = str(L['ra']); return route.fulfill(status=429, content_type='application/json', headers=hd, body='{"error":"made-up"}')
        return route.fulfill(status=200, content_type='application/json', headers=hd, body=json.dumps({'solar_system_id': L['sys']}))
    if '/characters/affiliation/' in u and str(MAIN) in (route.request.post_data or ''):
        return route.fulfill(status=200, content_type='application/json', body=json.dumps([{'character_id': MAIN, 'corporation_id': M.CORP}]))
    return route.fallback()

# the folder, its files and its permission survive the trip to EVE (sessionStorage, per origin); Intel's store is a stand-in; a
# Notification whose permission is "default", counting the asks
EXTRA = r"""(() => {
  const S = (k, v) => { try{ if(v === undefined) return JSON.parse(sessionStorage.getItem('__t_' + k) || 'null'); sessionStorage.setItem('__t_' + k, JSON.stringify(v)); }catch(e){ return null; } };
  window.__tS = S;
  const w0 = __fs.write, f0 = S('files') || {};
  __fs.write = (n, t) => { w0(n, t); const f = S('files') || {}; f[n] = (f[n] || '') + t; S('files', f); };
  for(const [n, t] of Object.entries(f0)) w0(n, t);
  if(S('perm')) __fs.perm = S('perm');
  __fs.answer = null; __fs.reads = 0; __fs.block = false; __fs.nask = 0;
  window.Notification = class { constructor(t, o){ __fs.notes.push([t, o && o.body]); } static get permission(){ return 'default'; } static requestPermission(){ __fs.nask++; return Promise.resolve('default'); } };
  const real = window.indexedDB, kv = new Map(), req = (v) => { const r = {result: v}; setTimeout(() => r.onsuccess && r.onsuccess()); return r; };
  const pick = window.showDirectoryPicker;
  window.__fsDirP = !pick ? Promise.resolve(undefined) : pick().then((d) => {
    d.queryPermission = async () => __fs.perm;
    d.requestPermission = async () => { if(__fs.answer) __fs.perm = __fs.answer; return __fs.perm; };
    const e0 = d.entries;
    d.entries = function(){ __fs.reads++; if(__fs.block || __fs.perm !== 'granted') throw new DOMException('not allowed', 'NotAllowedError'); return e0.call(this); };
    return d;
  });
  const db = {objectStoreNames: {contains: () => true}, createObjectStore(){},
    transaction(){ return {objectStore(){ return {
      get(k){ if(k !== 'dir') return req(kv.get(k)); const r = {}; window.__fsDirP.then((d) => { r.result = S('saved') ? d : undefined; r.onsuccess && r.onsuccess(); }); return r; },
      put(v, k){ if(k === 'dir') S('saved', 1); else kv.set(k, v); return req(undefined); }}; }}; }};
  Object.defineProperty(window, 'indexedDB', {value: {open(name, v){ if(name !== 'eta-intel') return real.open(name, v); const r = {}; setTimeout(() => { r.result = db; r.onsuccess && r.onsuccess(); }); return r; }, deleteDatabase: (n) => real.deleteDatabase(n)}, configurable: true});
  window.__ps = 0; window.addEventListener('pageshow', (e) => { if(e.persisted) window.__ps++; });
})();"""
ST = """() => { const q = (s) => document.querySelector(s), gl = q('#intelPanel [data-it-glbox]'), cb = q('#intelPanel [data-it-gl]');
  const t = (x) => x ? x.textContent.replace(/\\s+/g, ' ').trim() : '';
  return {on: it.on, gl: it.set.gameLoc, box: t(gl), cb: cb ? cb.checked : null, ask: !!q('#intelPanel [data-it-act="gl-go"]'), notes: t(q('#itNotes')),
    status: t(q('#intelPanel [data-it-status]')), my: itMySys(), who: sso.who, scp: sso.scp, err: it.err, sound: it.set.sound, notify: it.set.notify,
    ss: Object.fromEntries(Object.keys(sessionStorage).filter(k => !k.startsWith('__t_')).map(k => [k, sessionStorage.getItem(k)])),
    side: t(q('#sidePanel')), btn: !!q('button.sso-btn'), checking: /Checking your login with EVE/.test(t(q('#sidePanel'))), other: it.other,
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
        c.route(re.compile(r'https://esi\.evetech\.net/.*'), esi_loc)
        c.route(re.compile(r'https://login\.eveonline\.com/.*'), sso)
        c.route(re.compile(r'^http://localhost:8000/.*'), serve)
        return c
    def ready(pg): pg.wait_for_function("typeof it !== 'undefined' && it.loaded", timeout=10000); pg.wait_for_timeout(300)
    def page(c, intel=None, side=YOU, first=True):
        pg = c.new_page(); pg.goto(DEV_ORIGIN + '/')
        if first:
            pg.evaluate("([s, i]) => { localStorage.setItem('dscanSide', JSON.stringify(s)); if(i) localStorage.setItem('dscanIntel', JSON.stringify(i)); else localStorage.removeItem('dscanIntel'); }", [side, intel])
            pg.reload()
        ready(pg)
        setup_logs(pg); pg.click('#tabBtnIntel'); pg.click('#intelPanel [data-it-act="folder"]'); pg.wait_for_timeout(400)
        if not pg.is_checked('[data-it-chan="region.intel"]'): pg.check('[data-it-chan="region.intel"]')
        if not pg.is_checked(f'[data-it-me="{MAIN}"]'): pg.check(f'[data-it-me="{MAIN}"]')
        pg.wait_for_timeout(200); return pg
    def login(pg, scp=(LOC,), exp_s=1200, tab='madeUpTabId0028', tok='madeUpAccessToken'):   # a login as if back from EVE (the flow itself is tested below)
        pg.evaluate("([id, scp, exp, tab, rt, tok]) => { sso.who = {id, name: 'Your Main'}; sso.access = tok; sso.exp = Date.now() + exp * 1000; sso.scp = scp;"
                    " ssoSet(SSO_REFRESH, rt); ssoSet(SSO_WHO, JSON.stringify(sso.who)); ssoSet(SSO_TAB, tab); renderSidePanel(); itRender(true); }", [MAIN, list(scp), exp_s, tab, REFRESH, tok])
    def on(pg):
        pg.click('#intelSwLabel'); pg.wait_for_function("it.on", timeout=8000); pg.wait_for_timeout(300)
    def gl_on(pg): pg.evaluate("() => { it.set.gameLoc = true; itWriteSet(); itGlReset(); itRender(true); }")
    st = lambda pg: pg.evaluate(ST)
    def prof(pg): pg.evaluate("() => { if(!profileIsOpen()) openProfile(); }"); pg.wait_for_timeout(150)
    def gear(pg): pg.evaluate("() => { switchTab('intel'); it.pop = true; itRender(true); }"); pg.wait_for_timeout(100)

    # ---- a new user: alerts start unchecked; no notification prompt ----
    c = ctx_new(); pg = page(c)
    s = st(pg); bx = pg.evaluate("() => [...document.querySelectorAll('#intelPanel [data-it-set=\"sound\"], #intelPanel [data-it-set=\"notify\"]')].map(x => x.checked)")
    check(not s['sound'] and not s['notify'] and bx == [False, False], f'a new user: sound and desktop notification unchecked {bx}')
    on(pg)
    check(pg.evaluate("__fs.nask") == 0, f'pressing Intel\'s switch asks the browser for no notification permission ({pg.evaluate("__fs.nask")})')
    pg.click('#intelSwLabel'); pg.wait_for_timeout(300)
    # ---- box 3 ----
    pg.evaluate("() => { it.pop = true; itRender(true); }"); s = st(pg)
    check(s['cb'] is False and 'Use my game location' in s['box'] and 'Needs your EVE login and its OK' in s['box'], f"box 3: Use my game location, unchecked, its line ({s['box'][-80:]!r})")
    pg.click('#intelPanel [data-it-glbox] summary.info-btn'); pg.wait_for_timeout(200)
    ip = pg.evaluate("() => { const d = [...document.querySelectorAll('[role=dialog]')].find(x => x.offsetParent && /How Use my game location works/.test(x.textContent)); return d ? !!d.querySelector('button.x-close') : null; }")
    check(ip is True, f'its info panel: "How Use my game location works", the shared close button ({ip})')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(100); pg.evaluate("() => { it.pop = true; itRender(true); }")
    pg.click('#intelPanel [data-it-gl]'); pg.wait_for_timeout(200); s = st(pg)
    check(s['ask'] and s['cb'] is False and not s['gl'] and 'Continue to EVE' in s['box'] and 'Cancel' in s['box'], f"ticked without a login: Continue to EVE / Cancel, still off ({s['box'][:90]!r})")
    pg.click('#intelPanel [data-it-act="gl-no"]'); pg.wait_for_timeout(150); s = st(pg)
    check(not s['ask'] and not s['gl'], 'Cancel closes it; the switch stays off')
    # ---- Continue to EVE; back with the scope as an array ----
    pg.evaluate("() => localStorage.setItem('dscanIntel', JSON.stringify(Object.assign(JSON.parse(localStorage.getItem('dscanIntel')), {sound: true, notify: true})))")
    pg.reload(); ready(pg); setup_logs(pg); pg.click('#tabBtnIntel'); pg.wait_for_timeout(300)
    s = st(pg)
    check(s['sound'] and s['notify'], 'a saved sound and notification stay on after the update')
    reset(); gear(pg); pg.click('#intelPanel [data-it-gl]'); pg.wait_for_timeout(150)
    pg.click('#intelPanel [data-it-act="gl-go"]'); pg.wait_for_url(DEV_ORIGIN + '/**', timeout=8000); ready(pg); pg.wait_for_timeout(800)
    auth = [x for x in LOG if x[0] == '/v2/oauth/authorize']; q = auth[0][2] if auth else {}
    check(q.get('scope') == LOC, f"Continue to EVE: EVE is asked for the location scope only ({q.get('scope')!r})")
    s = st(pg)
    check(s['who'] and s['who']['id'] == MAIN and s['gl'] and s['cb'] is True and s['scp'] == [LOC], f"back with the scope (an array): logged in, the switch on ({s['gl']}, {s['scp']})")
    check('From your EVE login' in s['box'], f"its line says where it comes from ({s['box'][-60:]!r})")
    pg.evaluate("() => openProfile()"); pg.wait_for_timeout(200)
    pm = pg.evaluate("() => { const x = document.querySelector('.sso-perms'); return x ? [x.textContent.replace(/\\s+/g, ' ').trim(), (x.querySelector('a') || {}).href || ''] : null; }")
    check(pm and 'EVE permissions:' in pm[0] and 'Location' in pm[0] and "Manage on EVE's site" in pm[0] and pm[1].startswith('https://developers.eveonline.com/'),
          f"the profile: EVE permissions, a Location tag, Manage on EVE's site {pm}")
    pg.click('.sso-perms a'); pg.wait_for_timeout(200)
    lv = pg.evaluate("() => { const b = document.getElementById('leaveBox'); return b ? b.textContent : ''; }")
    check("EVE's developer site" in lv, f"Manage on EVE's site asks first (the outside-link gate) ({lv[:40]!r})")
    pg.keyboard.press('Escape')
    prof(pg); pg.click('[data-sso="logout"]'); pg.wait_for_timeout(400); s = st(pg)
    check(not s['who'] and not s['gl'] and "The permissions you gave EVE ended with it." in s['side'] and any(x[0] == '/v2/oauth/revoke' for x in LOG),
          f"Log out: the switch off, the token revoked, the permissions ended ({s['side'][-120:]!r})")
    # the profile's button asks for the features that are on
    gl_on(pg); pg.evaluate("() => { renderSidePanel(); }"); pg.wait_for_timeout(100)
    sub = pg.evaluate("() => [...document.querySelectorAll('#sidePanel .sso-sub .ctx')].map(x => x.textContent)")
    check(sub == ['Also asks for: Location'], f'the profile\'s button: "Also asks for: Location" while the switch is on ({sub})')
    reset(scp=LOC); prof(pg); pg.click('button.sso-btn'); pg.wait_for_url(DEV_ORIGIN + '/**', timeout=8000); ready(pg); pg.wait_for_timeout(800)
    auth = [x for x in LOG if x[0] == '/v2/oauth/authorize']; q = auth[0][2] if auth else {}; s = st(pg)
    check(q.get('scope') == LOC and s['who'] and s['scp'] == [LOC], f"the profile's button asks for it; a scope as a string is read ({q.get('scope')!r}, {s['scp']})")
    # back without the scope: SSO-07, the switch stays off
    prof(pg); pg.click('[data-sso="logout"]'); pg.wait_for_timeout(300); pg.click('#tabBtnIntel')
    reset(scp=[]); gear(pg); pg.click('#intelPanel [data-it-gl]'); pg.wait_for_timeout(150); pg.click('#intelPanel [data-it-act="gl-go"]'); pg.wait_for_url(DEV_ORIGIN + '/**', timeout=8000); ready(pg); pg.wait_for_timeout(800)
    s = st(pg)
    check(s['who'] and not s['gl'] and '(SSO-07)' in s['box'], f"back without the permission: SSO-07, the switch stays off ({s['box'][-110:]!r})")
    asked = [x[2].get('scope', '') for x in LOG if x[0] == '/v2/oauth/authorize']
    check(not any('ship' in a or 'online' in a for a in asked), f'no ship or online scope asked ({asked})')
    pg.close(); c.close()

    # ---- Intel running, logged in as You: the location checks ----
    c = ctx_new(); pg = page(c); lreset(); login(pg); gl_on(pg)
    check(not LREQ, 'Intel off: no location request')
    on(pg); pg.wait_for_timeout(2500); gear(pg); s = st(pg)
    h = LREQ[0]['h'] if LREQ else {}
    check(len(LREQ) == 1 and LREQ[0]['id'] == MAIN, f'Intel on: one location request for You ({len(LREQ)})')
    check(h.get('authorization') == 'Bearer madeUpAccessToken' and h.get('x-compatibility-date') == COMPAT and 'threatvectorapp@gmail.com' in h.get('x-user-agent', ''),
          f"the request: the token, X-Compatibility-Date {COMPAT}, X-User-Agent ({sorted(k for k in h if k.startswith('x-') or k == 'authorization')})")
    check(s['my'] == SYSID['8WA-Z6'] and '8WA-Z6 (newer, used)' in s['box'] and 'your Local log still says 1DQ1-A' in s['box'] and 'Your Main in 8WA-Z6' in s['status'],
          f"the game newer than the log: used, the amber line shows both, the status line ({s['box'][-90:]!r}; {s['status'][:40]!r})")
    nx = pg.evaluate("() => itGl.next - itGl.at")
    check(4900 <= nx <= 6100, f'the next check at Expires (5 s after the answer), never sooner ({nx / 1000:.1f} s)')
    n0 = len(LREQ); pg.wait_for_timeout(2500)
    check(len(LREQ) == n0, f'no request before Expires ({len(LREQ) - n0} more in 2.5 s)')
    # drawn: a change on screen (the checked time aside), or a forced redraw (itRender(true) skips the page's own compare, LESSON #120)
    pg.evaluate("() => { window.__draws = 0; new MutationObserver((ms) => { for(const m of ms) if(!(m.target.closest && m.target.closest('[data-it-glat]'))) window.__draws++; }).observe(document.querySelector('#intelPanel [data-it-glbox]'), {childList: true, subtree: true, characterData: true});"
                " const r = itRender; itRender = function(f){ if(f === true) window.__draws++; return r.apply(this, arguments); }; }")
    pg.wait_for_timeout(4000)
    dr = pg.evaluate("() => window.__draws")
    check(len(LREQ) > n0 and dr == 0, f'an answer that changes nothing draws nothing ({len(LREQ) - n0} answers, {dr} redraws)')
    W(pg, F_LOCAL_MAIN, line(time.time(), 'EVE System', 'Channel changed to Local : 8WA-Z6*')); pg.wait_for_timeout(2600)
    gear(pg); s = st(pg)
    check('8WA-Z6, the same as your Local log' in s['box'] and 'checked' in s['box'], f"the log caught up: \"the same as your Local log\" ({s['box'][-80:]!r})")
    # low on tokens: twice as long
    L['rem'] = 100; pg.wait_for_function("itGl.next - itGl.at > 6500", timeout=12000)
    nx = pg.evaluate("() => itGl.next - itGl.at")
    check(8000 <= nx <= 12100, f'under a quarter of the tokens left: twice as long ({nx / 1000:.1f} s)')
    L['rem'] = 550
    # 429: Retry-After
    pg.evaluate("() => { itGl.next = 0; }"); L['mode'] = '429'; L['ra'] = 20; n0 = len(LREQ); pg.wait_for_timeout(2500)
    nx = pg.evaluate("() => itGl.next - Date.now()"); n1 = len(LREQ); pg.wait_for_timeout(4000)
    check(n1 == n0 + 1 and 16000 <= nx <= 20100 and len(LREQ) == n1, f'a 429 waits its Retry-After ({nx / 1000:.1f} s; {len(LREQ) - n0} request)')
    # 401: SSO-08, never again
    pg.evaluate("() => { itGl.next = 0; }"); L['mode'] = '401'; n0 = len(LREQ); pg.wait_for_timeout(8000); gear(pg); s = st(pg)
    check(len(LREQ) == n0 + 1 and '(SSO-08)' in s['box'] and 'Log in again' in s['box'], f"a 401: SSO-08 with Log in again, and no second request ({len(LREQ) - n0} requests)")
    # 403: SSO-07, the switch off
    pg.evaluate("() => { itGlReset(); itGl.msg = null; }"); L['mode'] = '403'; n0 = len(LREQ); pg.wait_for_timeout(5000); gear(pg); s = st(pg)
    check(len(LREQ) == n0 + 1 and not s['gl'] and '(SSO-07)' in s['box'], f"a 403: SSO-07, the switch off ({len(LREQ) - n0} requests, gameLoc {s['gl']})")
    L['mode'] = 'ok'
    # ---- renewal ----
    gl_on(pg); pg.evaluate("() => { sso.exp = Date.now() + 30000; itGl.next = 0; }"); reset(); n0 = len(LREQ); pg.wait_for_timeout(3000)
    rf = [x for x in LOG if x[0] == '/v2/oauth/token']
    f = rf[0][2] if rf else {}
    check(len(rf) == 1 and f == {'grant_type': 'refresh_token', 'refresh_token': REFRESH, 'client_id': DEV}, f'under a minute left: renewed first, refresh token and Client ID only, no secret {sorted(f)}')
    ss = st(pg)['ss']
    check(ss.get('tvSsoRefresh') == 'madeUpRotated0001' and len(LREQ) > n0 and LREQ[-1]['h'].get('authorization', '').startswith('Bearer ey'),
          f"the new refresh token stored; the next request carries the new token ({ss.get('tvSsoRefresh')})")
    LOG.clear(); pg.evaluate("() => { sso.exp = Date.now() + 1000; return Promise.all([esiFetch(`${ESI}/characters/" + str(MAIN) + "/location/`, {}, 'location', {scope: SSO_LOC}), esiFetch(`${ESI}/characters/" + str(MAIN) + "/location/`, {}, 'location', {scope: SSO_LOC})]).then(() => 1); }")
    rf = [x for x in LOG if x[0] == '/v2/oauth/token']
    check(len(rf) == 1, f'two calls at once renew once ({len(rf)} renewals)')
    for mode, want, lab in (('429', 40, 'a 429 from the token endpoint waits its Retry-After'), ('html500', 30, 'an HTML 500 waits 30 s')):
        reset(refresh=mode); pg.evaluate("() => { sso.exp = Date.now() + 1000; sso.fails = 0; sso.renewAt = 0; itGl.next = 0; itGl.msg = null; }"); pg.wait_for_timeout(2600)
        ra = pg.evaluate("() => (sso.renewAt - Date.now()) / 1000"); gear(pg); s = st(pg)
        check(want - 4 <= ra <= want and s['who'] and '(SSO-03)' in s['box'], f'{lab} ({ra:.1f} s; the login kept, SSO-03 in the line)')
    reset(refresh='invalid_grant'); pg.evaluate("() => { sso.renewAt = 0; sso.fails = 0; itGl.next = 0; itGl.msg = null; }"); n0 = len(LREQ); pg.wait_for_timeout(2600); gear(pg); s = st(pg)
    check(not s['who'] and 'tvSsoRefresh' not in s['ss'] and '(SSO-06)' in s['box'] and 'Log in again' in s['box'] and len(LREQ) == n0,
          f"invalid_grant: SSO-06, the login ends, Log in again; nothing asked of ESI ({s['box'][-100:]!r})")
    pg.click('#intelSwLabel'); pg.wait_for_timeout(300); pg.close(); c.close()

    # ---- who isn't You; the tab without the lock; a duplicated tab ----
    c = ctx_new(); A = page(c); lreset(); login(A); gl_on(A)
    A.check(f'[data-it-me="{ALT}"]'); A.wait_for_timeout(100); on(A); A.wait_for_timeout(3000); gear(A); s = st(A)
    check(not LREQ and 'Your EVE login is Your Main, not Your Alt' in s['box'], f"the login's character isn't You: an amber line, no request ({len(LREQ)}; {s['box'][-90:]!r})")
    A.click('#intelSwLabel'); A.wait_for_timeout(200); gear(A); A.check(f'[data-it-me="{MAIN}"]'); A.evaluate("() => { it.pop = false; itRender(true); }"); on(A)
    B = page(c, first=False); login(B, tab='madeUpTabId0029', tok='madeUpAccessTokenB'); B.evaluate("() => { it.set.gameLoc = true; itGlReset(); }"); B.wait_for_timeout(3000)
    toks = {x['h'].get('authorization') for x in LREQ}
    check(LREQ and st(B)['other'] and not st(B)['on'] and 'Bearer madeUpAccessTokenB' not in toks, f'the tab without the lock: no request from it ({len(LREQ)} requests, all from the running tab: {sorted(toks)})')
    n0 = len(LREQ); A.click('#intelSwLabel'); A.wait_for_timeout(3000)
    check(len(LREQ) == n0, f'Intel off: no more requests ({len(LREQ) - n0})')
    # duplicated: B gets A's sessionStorage, then reloads
    ssA = A.evaluate("() => ({w: sessionStorage.getItem('tvSsoWho'), r: sessionStorage.getItem('tvSsoRefresh'), t: sessionStorage.getItem('tvSsoTab')})")
    B.evaluate("(x) => { sessionStorage.setItem('tvSsoWho', x.w); sessionStorage.setItem('tvSsoRefresh', x.r); sessionStorage.setItem('tvSsoTab', x.t); }", ssA)
    B.reload(); ready(B); B.wait_for_timeout(800); prof(B); sB, sA = st(B), st(A)
    check(not sB['who'] and "This tab was copied from another, so it's logged out here." in sB['side'] and sA['who'] and A.evaluate("sessionStorage.getItem('tvSsoRefresh')") == REFRESH,
          f"a duplicated tab drops its login; the original keeps it ({sB['side'][-70:]!r})")
    A.close(); B.close(); c.close()

    # ---- the Back-button bug ----
    c = ctx_new(); pg = page(c); reset(nav=False)
    pg.evaluate("() => openProfile()"); pg.wait_for_timeout(150); pg.click('button.sso-btn'); pg.wait_for_url('https://login.eveonline.com/**', timeout=8000)
    pg.go_back(); ready(pg); pg.wait_for_timeout(400); pg.evaluate("() => { if(!profileIsOpen()) openProfile(); }"); pg.wait_for_timeout(150); s = st(pg)
    ps = pg.evaluate("window.__ps")
    check(s['btn'] and not s['checking'] and 'tvSsoPending' not in s['ss'] and (ps == 0 or "nothing changed" in s['side']),
          f"Back from EVE's page ({'from the cache' if ps else 'a fresh load'}): the EVE button, not \"Checking…\", tvSsoPending gone")
    pg.evaluate("() => { sso.leaving = Date.now(); side.msg.pilot = {text: \"Opening EVE's login…\"}; ssoSet(SSO_PENDING, JSON.stringify({verifier: 'madeUpV', state: 'madeUpS', at: Date.now()})); renderSidePanel(); window.dispatchEvent(new PageTransitionEvent('pageshow', {persisted: true})); }")
    pg.wait_for_timeout(200); s = st(pg)
    check(s['btn'] and not s['checking'] and 'tvSsoPending' not in s['ss'] and "You came back from EVE's page without logging in, so nothing changed." in s['side'],
          f"a pageshow from the cache: the EVE button, the line, tvSsoPending gone ({s['side'][-90:]!r})")
    pg.evaluate("() => { closeProfile(); openProfile(); }"); pg.wait_for_timeout(150); s = st(pg)
    check(s['btn'] and not s['checking'], 'after the profile closes and opens: still the EVE button')
    pg.click('#tabBtnIntel'); pg.evaluate("() => { sso.leaving = Date.now(); sso.from = 'loc'; itGl.msg = {text: \"Opening EVE's login…\"}; ssoSet(SSO_PENDING, '{}'); window.dispatchEvent(new PageTransitionEvent('pageshow', {persisted: true})); }")
    pg.wait_for_timeout(200); s = st(pg)
    check("nothing changed" in s['box'] and not s['gl'] and 'tvSsoPending' not in s['ss'], f"the same for Use my game location: its line, the switch off ({s['box'][-80:]!r})")
    pg.evaluate("() => sessionStorage.setItem('tvSsoPending', JSON.stringify({verifier: 'madeUpV', state: 'madeUpS', at: Date.now(), intelWasOn: true}))")
    pg.reload(); ready(pg); s = st(pg)
    check('tvSsoPending' not in s['ss'] and not s['on'], 'a normal load drops a stale tvSsoPending (and starts nothing)')
    pg.close(); c.close()

    # ---- Intel after the trip ----
    def trip(intel_on, deny=False, perm=None, sound=False, other=None):
        reset(deny=deny); lreset()
        c = ctx_new(); pg = page(c, intel={'sound': sound, 'notify': False})
        if other: pass
        login(pg); pg.wait_for_timeout(100)
        if intel_on: on(pg)
        if perm: pg.evaluate("(v) => { __tS('perm', v); }", perm)
        pg.click('#tabBtnIntel'); pg.evaluate("() => { it.pop = true; itGl.ask = true; itRender(true); }"); pg.wait_for_timeout(100)
        pg.click('#intelPanel [data-it-act="gl-go"]'); pg.wait_for_url(DEV_ORIGIN + '/**', timeout=8000); ready(pg); pg.wait_for_timeout(1500)
        return c, pg
    c, pg = trip(True); s = st(pg)
    check(s['on'] and s['gl'], f'running before the trip, Authorize: Intel runs again, the switch on ({s["on"]}, {s["gl"]})')
    c.close()
    c, pg = trip(True, deny=True); s = st(pg)
    check(s['on'] and not s['gl'] and '(SSO-01)' in s['box'] and s['who'], f"running before, Cancel at EVE: Intel runs again, the switch off, the login kept ({s['box'][-60:]!r})")
    c.close()
    c, pg = trip(False); s = st(pg)
    check(not s['on'] and s['gl'], 'off before the trip: Intel stays off (the switch on)')
    c.close()
    c, pg = trip(True, sound=True); s = st(pg)
    check(s['on'] and 'Intel is running again. Click anywhere on the page to turn its sound back on.' in s['notes'], f"sound on: the \"click anywhere\" line ({s['notes'][:80]!r})")
    wk = pg.evaluate("() => { const b = document.querySelector('#itNotes .it-wake [data-it-act=\"wake\"]'); return b ? [b.textContent, getComputedStyle(b.closest('.it-wake')).borderTopStyle] : null; }")
    check(wk and wk[0] == 'Turn sound on' and wk[1] == 'solid', f'the line is the amber callout with Turn sound on (the owner: it has to stand out) {wk}')
    pg.mouse.click(5, 300); pg.wait_for_timeout(300)
    check('Click anywhere' not in st(pg)['notes'], 'gone after the first click')
    c.close()
    c, pg = trip(True, perm='prompt'); s = st(pg); r0 = pg.evaluate("__fs.reads")
    al = pg.evaluate("() => !!document.querySelector('#intelPanel [data-it-act=\"allow\"]')")
    pg.wait_for_timeout(2500)
    check(not s['on'] and al and pg.evaluate("__fs.reads") == r0, f'the folder needs a click: Allow reading, nothing read until it is pressed ({pg.evaluate("__fs.reads") - r0} reads)')
    pg.evaluate("() => { __fs.answer = 'granted'; }"); pg.click('#intelPanel [data-it-act="allow"]'); pg.wait_for_timeout(1500)
    check(st(pg)['on'], 'Allow reading starts Intel')
    c.close()
    # stale and foreign pending entries
    for lab, pend, ret in (('a stale pending entry', {'at': -11 * 60000, 'state': 'madeUpS1'}, 'madeUpS1'), ('a foreign one', {'at': 0, 'state': 'madeUpS2'}, 'madeUpOther')):
        reset(); c = ctx_new(); pg = page(c)
        pg.evaluate("(p) => sessionStorage.setItem('tvSsoPending', JSON.stringify({verifier: 'madeUpV', state: p.state, at: Date.now() + p.at, intelWasOn: true, from: 'loc', want: ['" + LOC + "']}))", pend)
        pg.goto(DEV_ORIGIN + f'/?code=madeUpCode0028&state={ret}'); ready(pg); pg.wait_for_timeout(1200); s = st(pg)
        check(not s['on'] and '(SSO-02)' in s['side'], f'{lab}: SSO-02, Intel stays off')
        c.close()
    # the other tab while this one is at EVE's page
    reset(nav=False); lreset(); c = ctx_new(); A = page(c); B = page(c, first=False); login(A); on(A); B.wait_for_timeout(600)
    # a message posted from pagehide may never arrive (the owner's Chrome, 2026-11-08): drop A's, so the line must come from before leaving
    # (the page's own pagehide listener runs before any added here, so the check drops what is posted while a pagehide is being handled)
    A.evaluate("() => { const f = itLockPost; itLockPost = function(m){ if(window.event && window.event.type === 'pagehide') return; return f.apply(this, arguments); }; }")
    A.click('#tabBtnIntel'); A.evaluate("() => { it.pop = true; itGl.ask = true; itRender(true); }"); A.click('#intelPanel [data-it-act="gl-go"]'); A.wait_for_url('https://login.eveonline.com/**', timeout=8000)
    B.wait_for_timeout(800); sB = st(B)
    check('Intel is paused while the other tab logs in with EVE.' in sB['notes'], f"the other tab: \"Intel is paused while the other tab logs in with EVE.\" ({sB['notes'][:80]!r})")
    # Chrome may keep A in its back/forward cache still holding the lock (the owner's Chrome): B shown again must stay "paused"
    B.evaluate("() => { const q = navigator.locks.query.bind(navigator.locks); navigator.locks.query = async () => ({held: [{name: IT_LOCK, mode: 'exclusive'}], pending: []}); return itLockCheck().then(() => { navigator.locks.query = q; }); }")
    sB = st(B)
    check('Intel is paused while the other tab logs in with EVE.' in sB['notes'], f"B shown again while A, away, still holds the lock: still paused ({sB['notes'][:80]!r})")
    S['nav'] = True; A.go_back(); ready(A); A.wait_for_timeout(800); sB = st(B)
    sA = st(A)
    check('paused' not in sB['notes'] and sA['on'] and 'Intel is on in another tab.' in sB['notes'] and "nothing changed" in (A.evaluate("() => itGl.msg ? itGl.msg.text : ''") or ''),
          f"A back without logging in (a fresh load from the Back button): Intel runs again in A, the line says nothing changed, B says it's on in another tab ({sB["notes"][:60]!r}; A on {sA["on"]}; {sA["side"][-60:]!r}; {sA["box"][-60:]!r})")
    A.close(); B.close(); c.close()

    # ---- Intel stopped reading ----
    for snd in (True, False):
        c = ctx_new(); pg = page(c, intel={'sound': snd, 'soundNear': 'chime', 'soundHere': 'klaxon'}); on(pg); pg.wait_for_timeout(2500)
        pg.evaluate("() => { __fs.beeps = 0; window.__k = []; for(const k of Object.keys(IT_SYNTH)){ const f = IT_SYNTH[k]; IT_SYNTH[k] = function(){ window.__k.push(k); return f.apply(this, arguments); }; } __fs.block = true; it.lastScan = 0; }")
        pg.wait_for_timeout(3000); pg.evaluate("() => { it.lastScan = 0; }"); pg.wait_for_timeout(3000); k = pg.evaluate("() => window.__k")
        check(k == (['triple'] if snd else []), f"Intel stopped reading, sound {'on' if snd else 'off'}: {'one Triple beep, none on the next ticks' if snd else 'no sound'} ({k})")
        c.close()
    c = ctx_new(); pg = page(c, intel={'sound': True, 'soundNear': 'triple', 'soundHere': 'chime'}); on(pg); pg.wait_for_timeout(2500)
    pg.evaluate("() => { window.__k = []; for(const k of Object.keys(IT_SYNTH)){ const f = IT_SYNTH[k]; IT_SYNTH[k] = function(){ window.__k.push(k); return f.apply(this, arguments); }; } }")
    pg.click('#intelSwLabel'); pg.wait_for_timeout(500)
    check(pg.evaluate("() => window.__k") == [], 'a stop by hand: no sound')
    on(pg); pg.wait_for_timeout(2500); pg.evaluate("() => { window.__k = []; __fs.block = true; it.lastScan = 0; }"); pg.wait_for_timeout(3500); k = pg.evaluate("() => window.__k")
    check(len(k) == 1 and k[0] not in ('triple', 'chime'), f"with Triple beep in use, another built-in sound: neither Near You's nor In system's ({k})")
    c.close()

    # ---- 390 px ----
    c = ctx_new(390); pg = page(c); gear(pg); pg.click('#intelPanel [data-it-gl]'); pg.wait_for_timeout(200)
    hh = pg.evaluate("() => document.querySelector('#intelPanel [data-it-act=\"gl-go\"]').getBoundingClientRect().height"); s = st(pg)
    check(hh >= 44 and s['sw'] <= s['vw'], f'390 px: Continue to EVE {hh:.0f} px tall, no sideways scroll')
    c.close()
    check(not BAD, f'no /ship/ or /online/ request anywhere ({BAD[:2]})')
    check(not errs, f'no page errors {errs[:3]}')
    b.close()
print(f'\nFAILURES: {fails}')
sys.exit(1 if fails else 0)
