"""Log in with EVE (v2026.11.08.1, build queue 024, SSO Phase 1; Project doc roadmap/sso-phase1-plan.md; prototype
Claude outputs/sso_login_prototype.html).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/sso_check.py [index.html]   -> 'FAILURES: N' (must be 0)

Never a live login (CLAUDE.md): login.eveonline.com is a stand-in here, with made-up metadata, a JWKS of keys made for this run
(an RSA key and a P-256 key), JWTs signed in the test, a revoke that records what it got. The page is served at the dev app's
address (http://localhost:8000/) and at threatvector.space by routes, so its origin picks the Client ID as it does for real.
Made-up pilot (sa_mocks.py) and made-up tokens only. Checks:
  * logged out: the profile's EVE tab (032): the three switches, then CCP's black image (270 x 45) in a button, its line ("Logs in only
    (no features picked)") with an info button ("How logging in with EVE works", the shared close button); the typed field on the Pilot
    tab; on a file:// copy the button is disabled with its title;
  * the press: the authorize address has response_type, redirect_uri (the origin + /), the origin's client_id, the S256 challenge
    of the verifier the token request sends, a state, and no scope; threatvector.space uses the production Client ID;
  * the return: the code and state are gone from the address before the page asks anything of anyone (every fetch() recorded with
    the address at that moment); the token request's body; the EVE tab's logged-in row (name, "EVE login" tag, "this tab", Log out),
    the corp on the profile's card; the refresh token in sessionStorage only, the access token in neither storage; the profile shows the pilot;
  * reload: still logged in, nothing asked of CCP; a new tab: the button again, the pilot as saved;
  * another tab clears the pilot: this tab is logged out with its line, the refresh token revoked;
  * Log out: revoke gets the refresh token, its hint and the Client ID; the keys go; the pilot is cleared; its one line, no
    authorized-apps link (a login with no permissions isn't listed on CCP's page, the owner's hand test 2026-11-08);
  * CCP's image is left as it is: hover draws an outline on the button, no filter on the image;
  * each refusal shows its code and changes nothing saved: cancelled (SSO-01), a state this tab didn't send / not the pending one / too old / used
    twice (SSO-02), metadata down, an HTML 500 from the token endpoint, an address that isn't CCP's (SSO-03), the token checks
    (wrong audience, without "EVE Online", wrong issuer, expired, alg none, HS256, an unknown kid, a bad signature, ES256 with the
    RSA key, a sub that isn't a character: SSO-04), an expired code (SSO-05); ES256 with the P-256 key logs in;
  * 1440 and 390 px: no sideways scroll; on a phone the EVE button and Log out are at least 44 px tall; no page errors.
"""
import sys, os, re, json, time, base64, hashlib, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sa_mocks as M
from playwright.sync_api import sync_playwright
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding, utils
from cryptography.hazmat.primitives import hashes

HTML = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith('--')),
                            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'index.html')))
PAGE = open(HTML, encoding='utf-8').read()
DEV, PROD = '659bdd63a604458e95c419de3373fdc3', 'eff6eec96b2e44cbb6a594f5e160a2e1'
DEV_ORIGIN, PROD_ORIGIN = 'http://localhost:8000', 'https://threatvector.space'
PILOT = 90000001   # sa_mocks' made-up "Test Pilot" (Example Corp, Example Alliance)
REFRESH = 'madeUpRefreshToken0024'
fails = []
def check(ok, what):
    print(('ok   ' if ok else 'FAIL ') + what)
    if not ok: fails.append(what)

# ---- keys made for this run (never a real key) ----
RSA = rsa.generate_private_key(public_exponent=65537, key_size=2048)
EC = ec.generate_private_key(ec.SECP256R1())
OTHER = rsa.generate_private_key(public_exponent=65537, key_size=2048)   # signs the "bad signature" token
b64u = lambda b: base64.urlsafe_b64encode(b).rstrip(b'=').decode()
def int_b64u(n, size=None): return b64u(n.to_bytes(size or (n.bit_length() + 7) // 8, 'big'))
rn = RSA.public_key().public_numbers(); en = EC.public_key().public_numbers()
JWKS = {'keys': [{'kty': 'RSA', 'alg': 'RS256', 'kid': 'JWT-Signature-Key', 'use': 'sig', 'n': int_b64u(rn.n), 'e': int_b64u(rn.e)},
                 {'kty': 'EC', 'alg': 'ES256', 'kid': 'madeUpEcKey', 'use': 'sig', 'crv': 'P-256', 'x': int_b64u(en.x, 32), 'y': int_b64u(en.y, 32)}]}
def jwt(claims, alg='RS256', kid='JWT-Signature-Key', key=None):
    head = b64u(json.dumps({'alg': alg, 'kid': kid, 'typ': 'JWT'}).encode()); body = b64u(json.dumps(claims).encode())
    data = (head + '.' + body).encode()
    if alg == 'none': return head + '.' + body + '.'
    if alg == 'HS256': import hmac; return head + '.' + body + '.' + b64u(hmac.new(b'madeUpSecret', data, hashlib.sha256).digest())
    if alg == 'RS256': sig = (key or RSA).sign(data, padding.PKCS1v15(), hashes.SHA256())
    else:
        r, s = utils.decode_dss_signature((key or EC).sign(data, ec.ECDSA(hashes.SHA256()))); sig = r.to_bytes(32, 'big') + s.to_bytes(32, 'big')
    return head + '.' + body + '.' + b64u(sig)
def claims(cid, **o):
    c = {'scp': None, 'jti': 'madeUpJti', 'kid': 'JWT-Signature-Key', 'sub': f'CHARACTER:EVE:{PILOT}', 'azp': cid, 'tenant': 'tranquility',
         'tier': 'live', 'region': 'world', 'aud': [cid, 'EVE Online'], 'name': 'Test Pilot', 'owner': 'madeUpOwnerHash=',
         'exp': int(time.time()) + 1200, 'iat': int(time.time()), 'iss': 'https://login.eveonline.com'}
    c.update(o); return {k: v for k, v in c.items() if v is not None}

# ---- the stand-in ----
S = {}      # how the stand-in answers this round
LOG = []    # (path, method, form or query)
def reset(**o):
    LOG.clear(); S.clear(); S.update({'meta': 'ok', 'token': 'ok', 'deny': False, 'claims': {}, 'alg': 'RS256', 'kid': 'JWT-Signature-Key', 'key': None, 'auth_ep': None, 'nav': True}); S.update(o)
reset()
def sso(route):
    req = route.request; u = urllib.parse.urlsplit(req.url); path = u.path
    form = dict(urllib.parse.parse_qsl(req.post_data or '')) if req.method == 'POST' else dict(urllib.parse.parse_qsl(u.query))
    LOG.append((path, req.method, form))
    j = lambda o, st=200: route.fulfill(status=st, content_type='application/json; charset=utf-8', headers={'access-control-allow-origin': '*'}, body=json.dumps(o))
    if path == '/.well-known/oauth-authorization-server':
        if S['meta'] == 'down': return route.fulfill(status=503, content_type='text/html', body='<html><body>made-up outage</body></html>')
        H = 'https://login.eveonline.com'
        return j({'issuer': H, 'authorization_endpoint': S['auth_ep'] or H + '/v2/oauth/authorize', 'token_endpoint': H + '/v2/oauth/token',
                  'jwks_uri': H + '/oauth/jwks', 'revocation_endpoint': H + '/v2/oauth/revoke', 'response_types_supported': ['code', 'token'],
                  'code_challenge_methods_supported': ['S256']})
    if path == '/oauth/jwks': return j(JWKS)
    if path == '/v2/oauth/authorize':
        S['challenge'] = form.get('code_challenge')
        if not S['nav']: return route.fulfill(status=200, content_type='text/html', body='<p>made-up authorize page</p>')
        back = form.get('redirect_uri', '') + '?' + urllib.parse.urlencode({'error': 'access_denied', 'state': form.get('state', '')} if S['deny'] else {'code': 'madeUpCode0024', 'state': form.get('state', '')})
        # EVE's page sends the browser back to the callback (a 302 from a route isn't followed for a page, so the stand-in's page does it)
        return route.fulfill(status=200, content_type='text/html', body=f'<!doctype html><script>location.replace({json.dumps(back)})</script>')
    if path == '/v2/oauth/token':
        if S['token'] == 'html500': return route.fulfill(status=500, content_type='text/html', body='<html><body>made-up error page</body></html>')
        if S['token'] == 'htmljson': return route.fulfill(status=400, content_type='text/html', body=json.dumps({'error': 'invalid_grant'}))   # JSON words, not JSON
        if S['token'] == 'invalid_grant': return j({'error': 'invalid_grant', 'error_description': 'made-up: code expired'}, 400)
        v = form.get('code_verifier', '')
        if b64u(hashlib.sha256(v.encode()).digest()) != S.get('challenge'): return j({'error': 'invalid_grant', 'error_description': 'made-up: verifier mismatch'}, 400)
        cid = form.get('client_id')
        return j({'access_token': jwt(claims(cid, **S['claims']), S['alg'], S['kid'], S['key']), 'expires_in': 1199, 'token_type': 'Bearer', 'refresh_token': REFRESH})
    if path == '/v2/oauth/revoke': return route.fulfill(status=200, body='')
    return j({'error': 'not in the stand-in'}, 404)
def serve(route):
    u = urllib.parse.urlsplit(route.request.url)
    if u.path == '/': return route.fulfill(status=200, content_type='text/html; charset=utf-8', body=PAGE)
    return route.fulfill(status=404, body='')
# every fetch() with the address at that moment, before the page's own script runs
REC = """(() => { const f = window.fetch; window.__fl = []; window.fetch = function(u, i){ try{ window.__fl.push([String(u && u.url || u), location.search]); }catch(e){} return f.apply(this, arguments); }; })();"""

ST = """() => { const p = document.getElementById('sidePanel') || document; const q = (s) => document.querySelector(s);
  const btn = q('button.sso-btn'), img = btn && btn.querySelector('img'), lo = q('[data-sso="logout"]');
  let ls = ''; try{ for(let i = 0; i < localStorage.length; i++) ls += localStorage.getItem(localStorage.key(i)) || ''; }catch(e){}
  let ss = {}; try{ for(let i = 0; i < sessionStorage.length; i++) ss[sessionStorage.key(i)] = sessionStorage.getItem(sessionStorage.key(i)); }catch(e){}
  return {btn: !!btn, dis: btn ? btn.disabled : null, title: btn ? btn.title : '', img: img ? [img.naturalWidth, img.naturalHeight, img.alt, img.getBoundingClientRect().width, img.getBoundingClientRect().height] : null,
    bh: btn ? btn.getBoundingClientRect().height : 0, or: !!q('.sso-or'), sub: [...document.querySelectorAll('.sso-sub .ctx')].map(x => x.textContent),
    field: !!q('#sidePilot'), fieldVal: q('#sidePilot') ? q('#sidePilot').value : null, inRow: !!q('.sso-in'), name: q('.sso-who b') ? q('.sso-who b').textContent : '',
    tag: q('.sso-tag') ? q('.sso-tag').textContent : '', lo: !!lo, loh: lo ? lo.getBoundingClientRect().height : 0,
    corp: q('#profileHead') ? q('#profileHead').textContent : '', msg: [...document.querySelectorAll('#profilePanel .side-msg')].map(x => x.textContent).join(' | '),
    apps: q('#profilePanel .side-msg a') ? q('#profilePanel .side-msg a').href : '', inSub: q('.sso-in .ctx') ? q('.sso-in .ctx').textContent : '', search: location.search, hash: location.hash,
    rec: localStorage.getItem('dscanSide'), pilot: side.rec.pilot, ls, ss, mem: !!sso.access, fl: window.__fl || [],
    sw: document.documentElement.scrollWidth, vw: innerWidth, chip: (document.getElementById('profileBtn') || {getAttribute: () => ''}).getAttribute('aria-label') || ''}; }"""

with sync_playwright() as p:
    b = p.chromium.launch()
    errs = []
    def ctx_new(w=1440):
        c = b.new_context(bypass_csp=True, viewport={'width': w, 'height': 1000})
        c.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
        c.add_init_script(REC)
        M.route(c)
        c.route(re.compile(r'https://login\.eveonline\.com/.*'), sso)
        c.route(re.compile(r'^http://localhost:8000/.*'), serve)
        c.route(re.compile(r'^https://threatvector\.space/.*'), serve)
        return c
    def open_panel(pg):
        pg.evaluate("openProfile('eve')"); pg.wait_for_timeout(150)   # 032: the login is on the profile's EVE tab
    def login(pg, wait='.sso-in, #profilePanel .side-msg.err'):
        open_panel(pg)
        pg.click('button.sso-btn')
        try: pg.wait_for_selector(wait, timeout=8000)
        except Exception: pass
        pg.wait_for_timeout(300)
        return pg.evaluate(ST)
    def sso_hits(): return [x for x in LOG if x[0] != '/.well-known/oauth-authorization-server' and x[0] != '/oauth/jwks']

    # ---- logged out, a new user ----
    c = ctx_new(); pg = c.new_page(); pg.goto(DEV_ORIGIN + '/'); pg.wait_for_timeout(500)
    open_panel(pg); s = pg.evaluate(ST)
    check(s['btn'] and not s['dis'] and s['img'] and s['img'][:3] == [270, 45, 'Log in with EVE Online'] and s['img'][3:] == [270, 45],
          f"logged out: CCP's black image, 270 x 45, in an enabled button {s['img']}")
    check('Logs in only (no features picked)' in s['sub'] and s['field'] and not s['inRow'],
          f"logged out: its one line, \"Logs in only (no features picked)\"; the typed field on the Pilot tab ({s['sub']})")
    order = pg.evaluate("() => { const a = document.querySelector('#eveTab button.sso-btn'), f = document.querySelector('#eveTab [data-sso=\"stand\"]'); return !!(a && f && (f.compareDocumentPosition(a) & Node.DOCUMENT_POSITION_FOLLOWING)); }")
    check(order, 'the EVE tab: the switches, then the button (pick, then log in once)')
    pg.click('.sso-sub summary.info-btn'); pg.wait_for_timeout(200)
    ip = pg.evaluate("() => { const d = [...document.querySelectorAll('[role=dialog]')].find(x => x.offsetParent && /logging in with EVE/.test(x.textContent)); return d ? [d.querySelector('button.x-close') ? 1 : 0, (d.textContent.match(/asks EVE for no permissions/) || []).length] : null; }")
    check(ip == [1, 1], f"its info panel: \"How logging in with EVE works\", the shared close button, the no-permissions text {ip}")
    pg.keyboard.press('Escape'); pg.wait_for_timeout(100)
    open_panel(pg); pg.hover('button.sso-btn'); pg.wait_for_timeout(100)
    hv = pg.evaluate("() => { const b = document.querySelector('button.sso-btn'), i = b.querySelector('img'), cb = getComputedStyle(b), ci = getComputedStyle(i); return [cb.outlineStyle, ci.filter, ci.opacity, cb.opacity]; }")
    check(hv == ['solid', 'none', '1', '1'], f"hover: an outline on the button; the image itself unaltered (no filter, full opacity) {hv}")
    pg.mouse.move(0, 0)
    LOG.clear()
    # ---- the press and the return ----
    s = login(pg)
    auth = [x for x in LOG if x[0] == '/v2/oauth/authorize']; tok = [x for x in LOG if x[0] == '/v2/oauth/token']
    q = auth[0][2] if auth else {}
    check(len(auth) == 1 and q.get('response_type') == 'code' and q.get('redirect_uri') == DEV_ORIGIN + '/' and q.get('client_id') == DEV
          and q.get('code_challenge_method') == 'S256' and len(q.get('state', '')) >= 20 and 'scope' not in q,
          f"the press: response_type, redirect_uri, the dev Client ID, S256, a state, no scope {sorted(q)}")
    f = tok[0][2] if tok else {}
    check(len(tok) == 1 and f.get('grant_type') == 'authorization_code' and f.get('code') == 'madeUpCode0024' and f.get('client_id') == DEV
          and len(f.get('code_verifier', '')) == 43 and b64u(hashlib.sha256(f.get('code_verifier', '').encode()).digest()) == q.get('code_challenge') and 'client_secret' not in f,
          f"the token request: grant_type, code, client_id, the verifier whose S256 is the challenge, no secret {sorted(f)}")
    dirty = [x for x in s['fl'] if re.search(r'[?&](code|state)=', x[1])]
    check(not re.search(r'code|state', s['search']) and not dirty and s['fl'], f"the address cleaned before any request ({len(s['fl'])} recorded; {dirty[:2]})")
    check(s['inRow'] and s['name'] == 'Test Pilot' and s['tag'] == 'EVE login' and s['lo'] and not s['field'] and not s['btn'] and 'Example Corp' in s['corp']
          and s['inSub'] == 'this tab', f"logged in: the name, the EVE login tag, \"this tab\", Log out; the corp on the card {s['name'], s['tag'], s['corp'][:40], s['inSub']}")
    check(s['ss'].get('tvSsoRefresh') == REFRESH and REFRESH not in s['ls'] and 'eyJ' not in s['ls'] and not any('eyJ' in (v or '') for v in s['ss'].values())
          and json.loads(s['ss'].get('tvSsoWho') or '{}') == {'id': PILOT, 'name': 'Test Pilot'} and 'tvSsoPending' not in s['ss'] and s['mem'],
          f"the refresh token in sessionStorage only, the access token in memory only, tvSsoPending used up {sorted(s['ss'])}")
    check(s['pilot'] and s['pilot']['id'] == PILOT and 'Test Pilot' in s['chip'], f"the profile shows the pilot ({s['chip'][:40]!r})")
    # ---- reload; a new tab ----
    LOG.clear(); pg.reload(); pg.wait_for_timeout(600); open_panel(pg); s = pg.evaluate(ST)
    check(s['inRow'] and s['name'] == 'Test Pilot' and not LOG, f"reload: still logged in, nothing asked of CCP ({[x[0] for x in LOG]})")
    pg2 = c.new_page(); pg2.goto(DEV_ORIGIN + '/'); pg2.wait_for_timeout(500); open_panel(pg2); s2 = pg2.evaluate(ST)
    check(s2['btn'] and not s2['inRow'] and s2['fieldVal'] == 'Test Pilot', f"a new tab: the button again, the pilot as saved ({s2['fieldVal']!r})")
    # ---- another tab clears the pilot ----
    LOG.clear(); pg2.evaluate("sideSetPilot('')"); pg.wait_for_timeout(700); s = pg.evaluate(ST)
    rv = [x for x in LOG if x[0] == '/v2/oauth/revoke']
    check(not s['inRow'] and 'changed in another tab, so this tab is logged out' in s['msg'] and 'tvSsoWho' not in s['ss'] and 'tvSsoRefresh' not in s['ss']
          and len(rv) == 1 and rv[0][2].get('token') == REFRESH, f"another tab cleared the pilot: logged out here, with its line, revoked ({s['msg'][:70]!r}, {len(rv)})")
    pg2.close()
    # ---- Log out ----
    s = login(pg)
    check(s['inRow'], 'logged in again')
    LOG.clear(); pg.click('[data-sso="logout"]'); pg.wait_for_timeout(500); s = pg.evaluate(ST)
    rv = [x for x in LOG if x[0] == '/v2/oauth/revoke']
    check(len(rv) == 1 and rv[0][1] == 'POST' and rv[0][2] == {'token_type_hint': 'refresh_token', 'token': REFRESH, 'client_id': DEV},
          f"Log out: revoke gets the refresh token, its hint and the Client ID {rv[0][2] if rv else None}")
    check(not s['inRow'] and s['btn'] and s['field'] and s['pilot'] is None and json.loads(s['rec'])['pilot'] is None and 'tvSsoWho' not in s['ss'] and 'tvSsoRefresh' not in s['ss'] and not s['mem'],
          'Log out: the keys and the token go, the pilot is cleared, the logged-out layout')
    check(s['msg'].strip() == 'Logged out of this tab, and Your pilot is cleared.' and not s['apps'],
          f"Log out: its line, and no authorized-apps link (a login with no permissions isn't listed there) ({s['msg']!r})")
    pg.close(); c.close()

    # ---- refusals: each its code, nothing saved changes ----
    TYPED = {'pilot': {'id': 90000001, 'name': 'Test Pilot'}, 'corp': {'id': M.CORP, 'name': 'Example Corp', 'kind': 'corporation'}, 'alliance': None, 'friendly': [], 'hostile': [], 'rows': 15}
    def refused(label, code, start=None, **mode):
        reset(**mode)
        c = ctx_new(); pg = c.new_page(); pg.goto(DEV_ORIGIN + '/'); pg.wait_for_timeout(300)
        pg.evaluate("(r) => localStorage.setItem('dscanSide', JSON.stringify(r))", dict(TYPED, pilot={'id': 90000002, 'name': 'Someone Else Typed'}) if False else TYPED)
        pg.reload(); pg.wait_for_timeout(400)
        before = pg.evaluate("localStorage.getItem('dscanSide')")
        if start: pg.goto(DEV_ORIGIN + start); pg.wait_for_selector('#profilePanel .side-msg.err', timeout=8000); pg.wait_for_timeout(200); s = pg.evaluate(ST)
        else:
            try: s = login(pg)
            except Exception as e:   # the page left for somewhere else (an address CCP's metadata shouldn't have been trusted with)
                check(False, f"{label}: {code}; instead the page went to {pg.url[:60]!r}"); c.close(); return None
        ok = f'({code})' in s['msg'] and not s['inRow'] and s['rec'] == before and 'tvSsoWho' not in s['ss'] and 'tvSsoRefresh' not in s['ss'] and 'tvSsoPending' not in s['ss'] and s['btn'] and not s['dis']
        check(ok, f"{label}: {code}, nothing saved changes, the button there to try again ({s['msg'][:90]!r})")
        c.close(); return s
    refused('cancelled at EVE', 'SSO-01', deny=True)
    s = refused('a state this tab did not send', 'SSO-02', start='/?code=madeUpCode0024&state=madeUpForgedState#intel') or {'search': '?', 'hash': '', 'msg': ''}
    check(s['search'] == '' and s['hash'] == '#intel', f"the foreign answer is out of the address, the hash kept ({s['search']!r}, {s['hash']!r})")
    refused('metadata down', 'SSO-03', meta='down')
    s = refused('an HTML 500 from the token endpoint', 'SSO-03', token='html500') or {'msg': ''}
    check('500' in s['msg'] and 'made-up error page' not in s['msg'], 'the HTML 500: its status, never its body')
    refused('an authorize address that is not CCP\'s', 'SSO-03', auth_ep='https://evil.example/authorize')
    refused('the code expired', 'SSO-05', token='invalid_grant')
    refused('an answer that reads like JSON but is sent as HTML', 'SSO-03', token='htmljson')
    refused('another app\'s audience', 'SSO-04', claims={'aud': ['madeUpOtherClientId', 'EVE Online']})
    refused('an audience without "EVE Online"', 'SSO-04', claims={'aud': DEV})
    refused('another issuer', 'SSO-04', claims={'iss': 'https://login.example.com'})
    refused('expired', 'SSO-04', claims={'exp': int(time.time()) - 60})
    refused('alg none', 'SSO-04', alg='none')
    refused('HS256', 'SSO-04', alg='HS256')
    refused('an unknown kid', 'SSO-04', kid='madeUpUnknownKid')
    refused('a bad signature', 'SSO-04', key=OTHER)
    refused('ES256 naming the RSA key', 'SSO-04', alg='ES256', kid='JWT-Signature-Key')
    refused('a sub that is not a character', 'SSO-04', claims={'sub': 'CORPORATION:EVE:98000001'})
    # a state too old, then used twice
    reset(nav=False)
    c = ctx_new(); pg = c.new_page(); pg.goto(DEV_ORIGIN + '/'); pg.wait_for_timeout(300)
    pg.evaluate("() => sessionStorage.setItem('tvSsoPending', JSON.stringify({verifier: 'madeUpVerifier', state: 'madeUpOldState', at: Date.now() - 11 * 60000}))")
    pg.goto(DEV_ORIGIN + '/?code=madeUpCode0024&state=madeUpOldState'); pg.wait_for_selector('#profilePanel .side-msg.err', timeout=8000); s = pg.evaluate(ST)
    check('(SSO-02)' in s['msg'] and not [x for x in LOG if x[0] == '/v2/oauth/token'], f"a state more than 10 minutes old: SSO-02, no token request ({s['msg'][:60]!r})")
    pg.evaluate("() => sessionStorage.setItem('tvSsoPending', JSON.stringify({verifier: 'madeUpVerifier', state: 'madeUpThisTabState', at: Date.now()}))")
    LOG.clear(); pg.goto(DEV_ORIGIN + '/?code=madeUpCode0024&state=madeUpOtherState'); pg.wait_for_selector('#profilePanel .side-msg.err', timeout=8000); s = pg.evaluate(ST)
    check('(SSO-02)' in s['msg'] and not [x for x in LOG if x[0] == '/v2/oauth/token'], f"a state other than the one this tab sent (one is pending): SSO-02, no token request ({s['msg'][:60]!r})")
    pg.evaluate("() => sessionStorage.setItem('tvSsoPending', JSON.stringify({verifier: 'madeUpVerifier', state: 'madeUpOnceState', at: Date.now()}))")
    LOG.clear(); pg.goto(DEV_ORIGIN + '/?code=madeUpCode0024&state=madeUpOnceState'); pg.wait_for_timeout(1200)
    pg.goto(DEV_ORIGIN + '/?code=madeUpCode0024&state=madeUpOnceState'); pg.wait_for_selector('#profilePanel .side-msg.err', timeout=8000); s = pg.evaluate(ST)
    check('(SSO-02)' in s['msg'] and len([x for x in LOG if x[0] == '/v2/oauth/token']) == 1, f"a state used twice: SSO-02 the second time ({len([x for x in LOG if x[0] == '/v2/oauth/token'])} token requests)")
    c.close()
    # ES256 with the P-256 key logs in
    reset(alg='ES256', kid='madeUpEcKey')
    c = ctx_new(); pg = c.new_page(); pg.goto(DEV_ORIGIN + '/'); pg.wait_for_timeout(300); s = login(pg)
    check(s['inRow'] and s['name'] == 'Test Pilot', 'ES256 with the P-256 key: logged in'); c.close()

    # ---- threatvector.space: the production app ----
    reset(nav=False); LOG.clear()
    c = ctx_new(); pg = c.new_page(); pg.goto(PROD_ORIGIN + '/'); pg.wait_for_timeout(300); open_panel(pg); pg.click('button.sso-btn'); pg.wait_for_timeout(1500)
    auth = [x for x in LOG if x[0] == '/v2/oauth/authorize']; q = auth[0][2] if auth else {}
    check(q.get('client_id') == PROD and q.get('redirect_uri') == PROD_ORIGIN + '/' and 'scope' not in q, f"threatvector.space: the production Client ID and callback, no scope ({q.get('client_id')}, {q.get('redirect_uri')})")
    c.close()
    # ---- a file:// copy ----
    c = ctx_new(); pg = c.new_page(); pg.goto('file://' + HTML); pg.wait_for_timeout(400); open_panel(pg); s = pg.evaluate(ST)
    check(s['btn'] and s['dis'] and s['title'] == 'EVE login works only on threatvector.space' and s['field'], f"a file:// copy: the button disabled with its title ({s['title']!r})")
    c.close()
    # ---- widths ----
    for w in (1440, 390):
        reset(); c = ctx_new(w); pg = c.new_page(); pg.goto(DEV_ORIGIN + '/'); pg.wait_for_timeout(300); open_panel(pg); s0 = pg.evaluate(ST); s = login(pg)
        big = w > 600 or (s0['bh'] >= 44 and s['loh'] >= 44)
        check(s['inRow'] and s0['sw'] <= s0['vw'] and s['sw'] <= s['vw'] and big, f"{w} px: no sideways scroll; on a phone the button {s0['bh']:.0f} px and Log out {s['loh']:.0f} px tall")
        c.close()
    check(not errs, f'no page errors {errs[:3]}')
    b.close()
print(f'\nFAILURES: {len(fails)}')
sys.exit(1 if fails else 0)
