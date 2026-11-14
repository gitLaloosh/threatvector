"""The route planner (build queue 047, roadmap/route-planner-plan.md; mockup Claude outputs/route_planner_mockup.html; the owner: "I'd like the option
to set it in game for convenience. seeing the route in the tool doesn't help much if i have to manually set 25+ systems to a route manually").

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/route_planner_check.py [index.html]   -> 'FAILURES: N' (must be 0)
    (RP_FAST=1 skips the mutants, for a quick look while working.)

Never a live login and never live ESI (CLAUDE.md): sso_game_check.py's stand-ins (CCP's login with keys made for this run, ESI's routes) plus a
stand-in POST /ui/autopilot/waypoint that records each request and answers 204 (or what a case sets). The page is served at the dev app's
address (http://localhost:8000/) with intel_check.py's made-up folder and Intel. Made-up characters and tokens only. Checks:
  * Threat Vector's route on a made-up graph (the page's own search, the table swapped for one made here): Prefer shorter = fewest jumps;
    Prefer safer goes round low and null sec, Prefer less secure round high sec, at penalty 50; at penalty 0 Prefer safer takes the shorter
    way again; the band decides null / low / high, never the rounded number (a system shown as 0.45 that is low sec); a flagged system is gone
    round however long the detour (the owner: "keep my rule"); with no clean route the fewest flagged, named in the warning; the destination
    and your own system never count;
  * on the real map: jump numbers stay the shortest by stargate (itm.D), the drawn route follows Threat Vector's route, the tooltip says
    "Threat Vector's route: N jumps (shortest M)" and what it couldn't avoid; the Intel example's map keeps the shortest routes;
  * logged off in the game (ESI answers 204, the game drops it): known logged off, nothing sent and Retry (was Send anyway, read as "send away"); not known, the note says
    to send it while in the game (047's hand test);
  * the EVE tab's switch off: nothing sent even with the permission held, the note's Turn it on (047's hand test);
  * the search box: drawn as the site's one text field (the --bg fill, 4px corners); suggestions (names starting with the text first), the keyboard (arrows, Enter, Esc), a pick centres the map on the
    system, zooms in, keeps its route and opens its tooltip; Shift+F10 in the box opens the menu;
  * the right-click menu: the system's name, the three items, the focus on the first, arrows, Esc and a press outside close it, the items off
    for your own system; Avoid this system adds it to the list (and Stop avoiding takes it off), the route then goes round it;
  * a phone (390 px): a pressed system's tooltip carries the three buttons, 44 px each, and takes presses; no sideways scroll;
  * Intel settings → Routes: each control saves tvRoute and changes the route; the slider is off while Prefer shorter; the list's Avoid and
    Remove; an unknown system refused; not in the Intel example's numbered setup;
  * setting the destination: not logged in, or without the permission: the note asks, Continue to EVE asks EVE for Waypoints, and nothing is
    sent; back from EVE with it: the EVE tab's switch on, "press again"; without it: SSO-07 and the switch off; EVE's route: one request with
    clear_other_waypoints=true and add_to_beginning=false, the token and X-Compatibility-Date; Threat Vector's route: one request per jump, in
    order, the first clearing, never two at once; a failure stops the rest (ROUTE-01, how far it got), 403 turns the switch off (SSO-07), 401
    SSO-08 and nothing more until a new login; a press while sending is refused; nothing sent without a press;
  * 048: kills on their own Routes box (kill; a setting saved without it keeps host's), ESS with hostiles and neutrals;
  * storage: tvRoute and tvRouteSend only, dscanIntel's keys unchanged; mutants, each must fail; no page errors.
"""
import sys, os, re, json, time, tempfile, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_G = open(os.path.join(HERE, 'sso_game_check.py'), encoding='utf-8').read()
exec(compile(_G[:_G.index('from playwright.sync_api import sync_playwright\nwith sync_playwright() as p:')], 'sso_game_check (first part)', 'exec'))
from playwright.sync_api import sync_playwright
WP = 'esi-ui.write_waypoint.v1'
WREQ, WS = [], {}
def wreset(**o):
    WREQ.clear(); WS.clear(); WS.update({'fail_at': None, 'fail': 500}); WS.update(o)
wreset()
def esi_wp(route):
    u = route.request.url
    if '/ui/autopilot/waypoint' in u:
        q = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(u).query))
        WREQ.append({'m': route.request.method, 'q': q, 'h': {k.lower(): v for k, v in route.request.headers.items()}})
        hd = {'access-control-allow-origin': '*', 'x-ratelimit-group': 'ui', 'x-ratelimit-limit': '900/15m', 'x-ratelimit-remaining': str(900 - 2 * len(WREQ))}
        if WS['fail_at'] is not None and len(WREQ) == WS['fail_at']: return route.fulfill(status=WS['fail'], content_type='application/json', headers=hd, body='{"error":"made-up"}')
        return route.fulfill(status=204, headers=hd, body='')
    return esi_loc(route)
# never two waypoint requests in the air at once: the page's own fetch, counted
INFLIGHT = r"""(() => { const f0 = window.fetch; window.__wpIn = 0; window.__wpMax = 0;
  window.fetch = function(u, i){ const wp = typeof u === 'string' && u.includes('/ui/autopilot/waypoint'); if(!wp) return f0.apply(this, arguments);
    window.__wpIn++; window.__wpMax = Math.max(window.__wpMax, window.__wpIn);
    return new Promise((res) => setTimeout(res, 60)).then(() => f0.call(this, u, i)).finally(() => { window.__wpIn--; }); }; })();"""

# ---- a made-up graph for the search (the page's own itRpUpdate, its table swapped for this one) ----
# 0 = you. Short way 0-1-2-3 through 1 (sec 0.3, low) and 2 (null); long way 0-4-5-6-7-3 all high. 9 (low) is 0-8-9 through 8, shown as
# 0.45 but low sec by its band, or 0-1-10-9 through two more low systems: Prefer less secure takes 8 only while its band says low.
GRAPH = """([edges, sec, band, flags, home, pref, pen]) => {
  const n = sec.length, adj = Array.from({length: n}, () => []);
  for(const [a, b] of edges){ adj[a].push(b); adj[b].push(a); }
  adj.forEach(a => a.sort((p, q) => p - q));
  const keep = {tab: itMapTab, home: itm.home, P: itm.P, rp: {...itRp}, set: itRp.set, fl: itRpFlags};
  try{
    itMapTab = {n, adj, sec: Int8Array.from(sec), band: band ? Uint8Array.from(band) : null};
    itm.home = home; itm.P = itm.P || new Float64Array(2); itRp.key = ''; itRp.par = null;
    itRp.set = {...itRpSet(), pref, pen, list: []};
    window.itRpFlags = () => new Map(flags.map(([i, w]) => [i, [w]]));
    itRpUpdate();
    const path = (i) => itRpPath(i);
    const out = {}; for(let i = 0; i < n; i++){ const p = path(i); out[i] = p ? p.join('-') : null; }
    out.warn3 = itRpWarn(path(3)); out.warn9 = itRpWarn(path(9) || []);
    return out;
  } finally {
    window.itRpFlags = keep.fl; itMapTab = keep.tab; itm.home = keep.home; itm.P = keep.P; Object.assign(itRp, keep.rp); itRp.set = keep.set; itRp.key = '';
  }
}"""
EDGES = [[0, 1], [1, 2], [2, 3], [0, 4], [4, 5], [5, 6], [6, 7], [7, 3], [0, 8], [8, 9], [1, 10], [10, 9]]
SEC = [50, 30, -20, 50, 50, 50, 50, 50, 45, 30, 30]
BAND = [2, 1, 0, 2, 2, 2, 2, 2, 1, 1, 1]   # 8: shown as 0.45, really just under it: low sec

def cases(b, html, phone=True):
    out, errs = [], []
    wreset(); reset(); lreset()   # each run (the page, then each mutant) starts with empty request logs and the stand-ins' defaults
    h = html
    def serve(route): return route.fulfill(status=200, content_type='text/html; charset=utf-8', body=h) if urllib.parse.urlsplit(route.request.url).path == '/' else route.fulfill(status=404, body='')
    def ctx(w=1440, H=1000):
        c = b.new_context(bypass_csp=True, viewport={'width': w, 'height': H}, has_touch=w < 600, is_mobile=w < 600)
        c.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
        c.add_init_script(FS); c.add_init_script(EXTRA); c.add_init_script(INFLIGHT); route(c)
        c.route(re.compile(r'https://esi\.evetech\.net/.*'), esi_wp)
        c.route(re.compile(r'https://login\.eveonline\.com/.*'), sso)
        c.route(re.compile(r'^http://localhost:8000/.*'), serve)
        return c
    def start(c, phone=False):
        pg = c.new_page(); pg.goto(DEV_ORIGIN + '/')
        pg.evaluate("(s) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({channels: ['region.intel'], me: %d, range: 3, forget: 15})); localStorage.removeItem('tvRoute'); localStorage.removeItem('tvRouteSend'); }" % MAIN, YOU)
        pg.reload(); pg.wait_for_function("typeof it !== 'undefined' && it.loaded", timeout=10000); pg.wait_for_timeout(300)
        setup_logs(pg); pg.evaluate('closeProfile(false)'); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.click('#intelPanel [data-it-act="folder"]'); pg.wait_for_timeout(400)
        pg.click('#intelSwLabel'); pg.wait_for_function("it.on", timeout=8000); tick(pg)
        if phone: pg.evaluate("() => { const nv = document.querySelector('[data-it-nv=\"map\"]'); if(nv) nv.click(); }"); pg.wait_for_timeout(300)   # a phone: the map is Near You's Map view
        pg.wait_for_function("itm.home >= 0 && itRp.par !== null", timeout=8000)
        return pg
    def login(pg, scp):
        pg.evaluate("([id, scp]) => { sso.who = {id, name: 'Your Main'}; sso.access = 'madeUpAccessToken'; sso.exp = Date.now() + 1200e3; sso.scp = scp;"
                    " ssoSet(SSO_REFRESH, 'madeUpRefreshToken0047'); ssoSet(SSO_WHO, JSON.stringify(sso.who)); ssoSet(SSO_TAB, 'madeUpTab0047'); renderSidePanel(); }", [MAIN, list(scp)])
    # ---- A: the search on a made-up graph
    c = ctx(); pg = start(c)
    g = lambda pref, pen, flags=(), band=BAND, home=0: pg.evaluate(GRAPH, [EDGES, SEC, band, [list(f) for f in flags], home, pref, pen])
    r = g('Shorter', 50)
    if r['3'] != '0-1-2-3': out.append(f'Prefer shorter should take the fewest jumps: {r["3"]}')
    r = g('Safer', 50)
    if r['3'] != '0-4-5-6-7-3': out.append(f'Prefer safer should go round low and null sec: {r["3"]}')
    r = g('Safer', 0)
    if r['3'] != '0-1-2-3': out.append(f'Prefer safer at penalty 0 should take the shorter way: {r["3"]}')
    r = g('LessSecure', 50)
    if r['3'] != '0-1-2-3' or r['9'] != '0-8-9': out.append(f'Prefer less secure should keep to low and null: 3 {r["3"]}, 9 {r["9"]}')
    # the band, not the rounded number: 8 is shown as 0.45 but is low, so Prefer less secure goes 0-8-9 (into low twice) rather than 0-1-2-3-9
    r2 = g('LessSecure', 50, band=[2, 1, 0, 2, 2, 2, 2, 2, 2, 1, 1])
    if r['9'] != '0-8-9' or r2['9'] != '0-1-10-9': out.append(f'the band should decide low sec (a system shown as 0.45): low {r["9"]}, high {r2["9"]}')
    # the owner's rule: a flagged system gone round however long the detour; no clean route: the fewest, named; the destination never counts
    r = g('Shorter', 50, [(1, 'camp')])
    if r['3'] != '0-4-5-6-7-3' or r['warn3']: out.append(f'a flagged system should be gone round: {r["3"]} {r["warn3"]}')
    r = g('Shorter', 50, [(1, 'camp'), (4, 'hostiles'), (8, 'bubble')])
    if not r['3'] or r['3'].count('-') != 3 or len(r['warn3']) != 1: out.append(f'no clean route: the fewest flagged, named: {r["3"]} {r["warn3"]}')
    r = g('Shorter', 50, [(3, 'kills')])
    if r['3'] != '0-1-2-3' or r['warn3']: out.append(f'the destination never counts as flagged: {r["3"]} {r["warn3"]}')
    r = g('Shorter', 50, [(0, 'camp')])
    if r['3'] != '0-1-2-3': out.append(f'your own system never counts as flagged: {r["3"]}')
    # ---- B: the real map
    m = pg.evaluate("""() => { const g = itGraphGet(), T = itMapTable(), D = itm.D; const bfs = new Int16Array(T.n).fill(-1), q = [itm.home]; bfs[itm.home] = 0;
      for(let k = 0; k < q.length; k++) for(const y of T.adj[q[k]]) if(bfs[y] < 0){ bfs[y] = bfs[q[k]] + 1; q.push(y); }
      let same = true; for(let i = 0; i < T.n; i++) if(bfs[i] !== D[i]) same = false;
      return {same, band: !!T.band, flags: [...itRp.flags].map(([i, w]) => [g.ids[i], w])}; }""")
    if not m['same']: out.append('jump numbers should stay the shortest by stargate (itm.D)')
    if not m['band']: out.append("the page's map table has no band")
    # a destination 2-8 jumps away whose shortest route passes a flagged system (made here: the avoid list's first system)
    d = pg.evaluate("""() => { const T = itMapTable(), g = itGraphGet();
      for(let i = 0; i < T.n; i++){ if(itm.D[i] < 3 || itm.D[i] > 7) continue; const mid = itm.par[i]; if(itm.par[mid] < 0 || mid === itm.home) continue;
        // only if going round mid is possible
        return {i, id: g.ids[i], mid: g.ids[mid], d: itm.D[i]}; } return null; }""")
    if not d: out.append('no destination for the detour test'); c.close(); return out, errs
    pg.evaluate("(id) => { const s = itRpSet(); s.list = [id]; itRpSave(); itRpRefresh(); }", d['mid'])
    t = pg.evaluate("""([i, mid]) => { const g = itGraphGet(), p = itRpPath(i); const r = itm.cv.getBoundingClientRect();
      itMapTip(i, itm.Q[2 * i], itm.Q[2 * i + 1]); const tip = itm.tip.innerText;
      return {p: p && p.map(x => g.ids[x]), len: p ? p.length - 1 : null, tip, route: itMapRoute(i).length}; }""", [d['i'], d['mid']])
    if not t['p'] or d['mid'] in t['p'][1:-1] and not ('No route avoids all' in t['tip']):
        out.append(f'the avoid list should send the route round {d["mid"]}, or say it couldn\'t: {t}')
    if t['len'] != t['route']: out.append(f'the drawn route should follow Threat Vector\'s route: {t["len"]} vs {t["route"]}')
    if t['len'] is not None and t['len'] != d['d'] and f"Threat Vector's route: {t['len']} jumps (shortest {d['d']})" not in t['tip']:
        out.append(f'the tooltip should say Threat Vector\'s route and the shortest: {t["tip"]!r}')
    if 'right-click: send destination to EVE' not in t['tip']: out.append('the tooltip should say right-click: send destination to EVE on a wide screen')
    ex = pg.evaluate("() => { let same = null; itExSandbox(() => { same = itRpParNow() === itm.par; }); return same; }")
    if not ex: out.append("the Intel example's map should keep the shortest stargate routes")
    pg.evaluate("() => { const s = itRpSet(); s.list = []; itRpSave(); itRpRefresh(); }")
    # ---- the search box
    # 047, the owner's hand test ("search box is white, should match the background color, no?"): drawn as the site's one text field
    look = pg.evaluate("() => { const i = document.querySelector('.it-rp-search input'), c = getComputedStyle(i), t = document.createElement('div'); t.style.background = 'var(--bg)'; document.body.appendChild(t); const bg = getComputedStyle(t).backgroundColor; t.remove(); return [c.backgroundColor, bg, c.borderTopLeftRadius, c.color === getComputedStyle(document.body).color || c.color]; }")
    if look[0] != look[1] or look[2] != '4px': out.append(f'the search box should be drawn as the site\'s text field (--bg fill, 4px corners): {look}')
    nm = pg.evaluate("(id) => itSysName(id)", d['id'])
    pg.click('.it-rp-search input'); pg.keyboard.type(nm[:3].lower()); pg.wait_for_timeout(150)
    sug = pg.evaluate("[...document.querySelectorAll('#itRpSug li')].map(l => l.textContent)")
    if not sug or not all(x.lower().startswith(nm[:3].lower()) for x in sug[:1]): out.append(f'suggestions should start with the text first: {sug[:3]}')
    pg.fill('.it-rp-search input', nm); pg.wait_for_timeout(150)
    pg.keyboard.press('ArrowDown')
    if pg.evaluate("document.querySelector('.it-rp-search input').getAttribute('aria-activedescendant')") != 'itRpo0': out.append('ArrowDown should mark the first suggestion')
    pg.keyboard.press('Enter'); pg.wait_for_timeout(250)
    k = pg.evaluate("(id) => [itRp.sel === itGraphGet().at.get(id), itm.pinned.has(id), !itm.tip.hidden, itMapGatePx() >= 40 - 0.01, Math.abs(itm.Q[2 * itRp.sel] - itm.W / 2) < 2, document.querySelector('#itRpSug').hidden]", d['id'])
    if not all(k): out.append(f'a pick: selected, route kept, tooltip open, zoomed in, centred, list closed: {k}')
    pg.keyboard.press('Shift+F10'); pg.wait_for_timeout(150)
    if not pg.evaluate("!!itRp.menu"): out.append('Shift+F10 in the search box should open the menu')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(100)
    if pg.evaluate("!!itRp.menu || document.activeElement !== document.querySelector('.it-rp-search input')"): out.append('Esc should close the menu and give the focus back to the search box')
    # ---- the right-click menu
    xy = lambda i: pg.evaluate("(i) => { const r = itm.cv.getBoundingClientRect(); return [r.left + itm.Q[2 * i], r.top + itm.Q[2 * i + 1]]; }", i)
    x, y = xy(d['i']); pg.mouse.click(x, y, button='right'); pg.wait_for_timeout(150)
    mn = pg.evaluate("() => itRp.menu ? [itRp.menu.querySelector('.it-rp-mh').textContent, [...itRp.menu.querySelectorAll('button')].map(b => b.textContent + (b.disabled ? '(off)' : '')), document.activeElement.dataset.itRpGo || '', itRp.menu.getAttribute('role')] : null")
    if not mn or nm not in mn[0] or len(mn[1]) != 3 or mn[2] != 'eve' or mn[3] != 'menu' or not mn[1][2].startswith('Avoid this system'): out.append(f'the menu: name, three items, focus on the first: {mn}')
    pg.keyboard.press('ArrowDown')
    if pg.evaluate("document.activeElement.dataset.itRpGo") != 'tv': out.append('ArrowDown should move to the next item')
    pg.mouse.click(5, 5); pg.wait_for_timeout(100)
    if pg.evaluate("!!itRp.menu"): out.append('a press outside should close the menu')
    pg.evaluate("() => itMapCenter()"); hx, hy = xy(pg.evaluate("itm.home")); pg.mouse.click(hx, hy, button='right'); pg.wait_for_timeout(150)
    off = pg.evaluate("() => itRp.menu ? [...itRp.menu.querySelectorAll('button')].map(b => b.disabled) : null")
    if off != [True, True, True]: out.append(f'your own system: the items off: {off}')
    pg.keyboard.press('Escape')
    pg.evaluate("(i) => { const v = itm.view; v.tx = itm.W / 2 - itm.P[2 * i] * v.k; v.ty = itm.H / 2 - itm.P[2 * i + 1] * v.k; itMapDraw(); }", d['i'])
    x, y = xy(d['i']); pg.mouse.click(x, y, button='right'); pg.wait_for_timeout(100); pg.click('.it-rp-menu [data-it-rp-av]'); pg.wait_for_timeout(200)
    if pg.evaluate("(id) => JSON.parse(localStorage.getItem('tvRoute')).list", d['id']) != [d['id']]: out.append('Avoid this system should add it to the list (tvRoute)')
    pg.mouse.click(x, y, button='right'); pg.wait_for_timeout(100)
    if pg.evaluate("itRp.menu.querySelector('[data-it-rp-av]').textContent") != 'Stop avoiding': out.append('the menu should say Stop avoiding for a system on the list')
    pg.click('.it-rp-menu [data-it-rp-av]'); pg.wait_for_timeout(200)
    if pg.evaluate("JSON.parse(localStorage.getItem('tvRoute')).list.length") != 0: out.append('Stop avoiding should take it off the list')
    # ---- Intel settings → Routes
    pg.evaluate("() => { it.pop = true; itRender(true); }"); pg.wait_for_timeout(200)
    if not pg.locator('[data-it-rp-box]').count(): out.append('the Routes box should be in Intel settings')
    else:
        if not pg.is_disabled('[data-it-rp-set="pen"]'): out.append('the security penalty should be off while Prefer shorter')
        k0 = pg.evaluate("itRp.key")
        pg.check('[data-it-rp-set="pref"][value="Safer"]'); pg.wait_for_timeout(150)
        st = pg.evaluate("[JSON.parse(localStorage.getItem('tvRoute')).pref, itRp.key, document.querySelector('[data-it-rp-set=\"pen\"]').disabled, document.activeElement && document.activeElement.value]")
        if st[0] != 'Safer' or st[1] == k0 or st[2] or st[3] != 'Safer': out.append(f'Prefer safer: saved, the route again, the slider on, the focus kept: {st}')
        pg.evaluate("() => { const r = document.querySelector('[data-it-rp-set=\"pen\"]'); r.value = '80'; r.dispatchEvent(new Event('input', {bubbles: true})); r.dispatchEvent(new Event('change', {bubbles: true})); }"); pg.wait_for_timeout(150)
        if pg.evaluate("[JSON.parse(localStorage.getItem('tvRoute')).pen, itRp.key.split('|')[2]]") != [80, '80']: out.append('the security penalty should save and change the route')
        for kk in ('camp', 'bub', 'host', 'kill', 'mine'):
            pg.uncheck(f'[data-it-rp-set="{kk}"]'); pg.wait_for_timeout(80)
            if pg.evaluate(f"JSON.parse(localStorage.getItem('tvRoute')).{kk}") is not False: out.append(f'{kk}: unticking should save')
        pg.fill('.it-rp-add input[name=sys]', 'Nowhere Special'); pg.click('.it-rp-add button'); pg.wait_for_timeout(100)
        if 'isn’t a system on the map' not in pg.inner_text('[data-it-rp-box] .it-rp-msg'): out.append('an unknown system should be refused')
        pg.fill('.it-rp-add input[name=sys]', nm); pg.click('.it-rp-add button'); pg.wait_for_timeout(150)
        if pg.evaluate("JSON.parse(localStorage.getItem('tvRoute')).list") != [d['id']]: out.append('Avoid in the box should add the system')
        pg.click('[data-it-rp-box] [data-it-rp-av]'); pg.wait_for_timeout(150)
        if pg.evaluate("JSON.parse(localStorage.getItem('tvRoute')).list.length") != 0: out.append('Remove should take it off')
    if pg.evaluate("itSettingsHtml(true).includes('data-it-rp-box')"): out.append("the Routes box shouldn't be in the Intel example's numbered setup")
    # 048 (the owner: "separate kills as their own avoid option"): its own box; a setting saved before it keeps what `host` did for kills;
    # hostiles, neutrals and ESS stay on `host` (the owner: "ESS by itself indicates someone is in it")
    mg = pg.evaluate("""() => { const r = (o) => { localStorage.setItem('tvRoute', JSON.stringify(o)); itRp.set = null; return itRpSet().kill; };
      const a = [r({host: false}), r({host: true}), r({host: true, kill: false}), r({host: false, kill: true})];
      localStorage.removeItem('tvRoute'); itRp.set = null;
      const near = it.near, id = itGraphGet().ids[itm.home === 1 ? 2 : 1], now = Date.now();
      it.near = new Map([[id, {sys: id, t: now, kind: 'tag', kills: [{t: now}], essAt: [{t: now, who: 'Made Up'}]}]]);
      const f = (o) => { itRp.set = Object.assign({}, IT_RP_DEF, {list: [], camp: false, bub: false}, o); return JSON.stringify([...itRpFlags().values()]); };
      const b = [f({}), f({kill: false}), f({host: false}), f({host: false, kill: false})]; it.near = near; itRp.set = null; return [a, b]; }""")
    if mg[0] != [False, True, False, True]: out.append(f'kills: a setting saved before 048 keeps what host did, a saved kill wins: {mg[0]}')
    if mg[1] != ['[["kills","ESS"]]', '[["ESS"]]', '[["kills"]]', '[]']: out.append(f'kills on their own box, ESS with hostiles and neutrals: {mg[1]}')
    if 'systems with kills' not in pg.evaluate("itRpBoxHtml(false)") or 'neutrals, kills' in pg.evaluate("itRpBoxHtml(false)"): out.append("the Routes box: a box for kills, the third box's label without kills")
    pg.evaluate("() => { localStorage.removeItem('tvRoute'); itRp.set = null; it.pop = false; itRpRefresh(); itRender(true); }")
    # ---- setting the destination
    n0 = len(WREQ); pg.wait_for_timeout(500)
    if len(WREQ) != n0 or n0: out.append(f'nothing should be sent without a press ({len(WREQ)} requests)')
    go = lambda mode, i: pg.evaluate("([m, i]) => { itRpGo(m, i); }", [mode, i])   # a press: not waited for (evaluate would wait for the whole send)
    go('eve', d['i']); pg.wait_for_timeout(150)
    if 'needs your EVE login with the Waypoints permission' not in pg.inner_text('.it-rp-note') or WREQ: out.append('not logged in: the note should ask, nothing sent')
    login(pg, [LOC]); go('tv', d['i']); pg.wait_for_timeout(150)
    if not pg.locator('.it-rp-note [data-it-rp-eve]').count() or WREQ: out.append('logged in without Waypoints: the note should ask, nothing sent')
    # Continue to EVE, in another tab of the same browser (this one keeps Intel and its map): it leaves for EVE's page asking for Waypoints
    S['nav'] = False; LOG.clear()
    p2 = c.new_page(); p2.goto(DEV_ORIGIN + '/'); p2.wait_for_function("typeof it !== 'undefined' && it.loaded", timeout=10000); p2.wait_for_timeout(200)
    login(p2, [LOC])
    p2.evaluate("() => { const b = document.createElement('button'); b.type = 'button'; b.dataset.itRpEve = ''; b.id = 'rpGoTest'; document.getElementById('intelPanel').appendChild(b); }")
    p2.click('#rpGoTest'); p2.wait_for_timeout(1000)
    asked = [f for pth, mth, f, _ in LOG if pth == '/v2/oauth/authorize']
    if not asked or WP not in asked[0].get('scope', '').split() or LOC not in asked[0].get('scope', '').split(): out.append(f'Continue to EVE should ask EVE for Waypoints (and what else is on): {asked[:1]}')
    p2.close(); S['nav'] = True
    if pg.evaluate("localStorage.getItem('tvRouteSend')") != 'true': out.append("Continue to EVE should turn on the EVE tab's switch (tvRouteSend)")
    # back from EVE: itRpGranted with and without the permission
    login(pg, [LOC]); pg.evaluate("() => itRpGranted()")
    gm = pg.evaluate("[localStorage.getItem('tvRouteSend'), itRp.msg && itRp.msg.text]")
    if gm[0] != 'false' or 'SSO-07' not in (gm[1] or ''): out.append(f'back without Waypoints: SSO-07, the switch off: {gm}')
    login(pg, [LOC, WP]); pg.evaluate("() => itRpGranted()")
    gm = pg.evaluate("[localStorage.getItem('tvRouteSend'), itRp.msg && itRp.msg.text]")
    if gm[0] != 'true' or 'press Send destination to EVE' not in (gm[1] or ''): out.append(f'back with Waypoints: the switch on, press again: {gm}')
    pg.evaluate("() => openProfile('eve')"); pg.wait_for_timeout(150)
    ev = pg.evaluate("() => { const f = document.querySelector('#eveTab [data-feat=\"wp\"]'); return f ? [f.textContent.replace(/\\s+/g, ' '), document.querySelector('#ppSw-wp').checked] : null; }")
    if not ev or 'Set my destination in EVE' not in ev[0] or not ev[1]: out.append(f"the profile's EVE tab should show Set my destination in EVE, on: {ev}")
    pg.evaluate('closeProfile(false)'); pg.wait_for_timeout(100)
    # the owner's hand test: the switch turned off while the login still holds Waypoints sent anyway and turned itself back on
    wreset(); pg.evaluate("() => itRpSendToggle(false)"); go('eve', d['i']); pg.wait_for_timeout(300)
    off = [len(WREQ), pg.evaluate("localStorage.getItem('tvRouteSend')"), pg.inner_text('.it-rp-note'), pg.locator('.it-rp-note [data-it-rp-on]').count()]
    if off[0] or off[1] != 'false' or 'is off' not in off[2] or off[3] != 1: out.append(f'the switch off, Waypoints held: nothing sent, the switch stays off, a Turn it on button: {off}')
    if off[3]: pg.click('.it-rp-note [data-it-rp-on]'); pg.wait_for_timeout(150)
    else: pg.evaluate("() => itRpSendToggle(true)")
    on = [len(WREQ), pg.evaluate("localStorage.getItem('tvRouteSend')"), pg.inner_text('.it-rp-note')]
    if on[0] or on[1] != 'true' or 'press Send destination to EVE again' not in on[2]: out.append(f'Turn it on: the switch on, nothing sent until the next press: {on}')
    # EVE's route: one request
    wreset(); go('eve', d['i']); pg.wait_for_function("!itRp.busy", timeout=8000)
    if len(WREQ) != 1 or WREQ[0]['m'] != 'POST' or WREQ[0]['q'] != {'add_to_beginning': 'false', 'clear_other_waypoints': 'true', 'destination_id': str(d['id'])}:
        out.append(f"EVE's route: one POST clearing the others: {[(w['m'], w['q']) for w in WREQ]}")
    elif WREQ[0]['h'].get('authorization') != 'Bearer madeUpAccessToken' or WREQ[0]['h'].get('x-compatibility-date') != COMPAT: out.append('the waypoint request should carry the token and X-Compatibility-Date')
    if 'Destination set:' not in pg.inner_text('.it-rp-note') or 'autopilot settings' not in pg.inner_text('.it-rp-note'): out.append(f"EVE's route: the note {pg.inner_text('.it-rp-note')!r}")
    # the owner's hand test: logged off in the game ESI still answers 204 and the game drops the destination
    if "while you're in the game" not in pg.inner_text('.it-rp-note'): out.append(f"online not known: the note should say to send it while in the game: {pg.inner_text('.it-rp-note')!r}")
    pg.evaluate("() => { window.__onShown = ssoOnShown; window.__onl = false; ssoOnShown = () => window.__onl; }")
    wreset(); go('eve', d['i']); pg.wait_for_timeout(200)
    t_off = pg.inner_text('.it-rp-note')
    if WREQ or "logged off in EVE" not in t_off or pg.locator('.it-rp-note [data-it-rp-force]').count() != 1 or pg.inner_text('.it-rp-note [data-it-rp-force]').strip() != 'Retry': out.append(f'known logged off: nothing sent, a note with Send anyway: {len(WREQ)} {t_off!r}')
    else:
        pg.click('.it-rp-note [data-it-rp-force]'); pg.wait_for_function("!itRp.busy", timeout=8000); pg.wait_for_timeout(100)
        if len(WREQ) != 1 or "while you're in the game" not in pg.inner_text('.it-rp-note'): out.append(f"Send anyway: one request, the note says it's dropped while logged off: {len(WREQ)} {pg.inner_text('.it-rp-note')!r}")
    pg.evaluate("() => { window.__onl = true; }"); wreset(); go('eve', d['i']); pg.wait_for_function("!itRp.busy", timeout=8000); pg.wait_for_timeout(100)
    if len(WREQ) != 1 or "while you're in the game" in pg.inner_text('.it-rp-note'): out.append(f"known in the game: sent, no logged-off line: {len(WREQ)} {pg.inner_text('.it-rp-note')!r}")
    pg.evaluate("() => { ssoOnShown = window.__onShown; }")
    # Threat Vector's route: one per jump, in order, never two at once
    wreset(); pg.evaluate("window.__wpMax = 0"); path = pg.evaluate("(i) => itRpPath(i).slice(1).map(x => itGraphGet().ids[x])", d['i'])
    go('tv', d['i']); pg.wait_for_timeout(50)
    go('eve', d['i']); pg.wait_for_timeout(30)
    busy = pg.inner_text('.it-rp-note')
    pg.wait_for_function("!itRp.busy", timeout=15000)
    got = [w['q']['destination_id'] for w in WREQ]
    if got != [str(x) for x in path]: out.append(f"Threat Vector's route: every system in order: {got} vs {path}")
    if [w['q']['clear_other_waypoints'] for w in WREQ] != ['true'] + ['false'] * (len(path) - 1): out.append('only the first waypoint should clear the others')
    if pg.evaluate("window.__wpMax") != 1: out.append(f'never two waypoint requests at once: {pg.evaluate("window.__wpMax")}')
    if 'Still setting this destination' not in busy: out.append(f'a press while sending should be refused, the line kept: {busy!r}')
    if f'Destination set: {nm}, {len(path)} jump' not in pg.inner_text('.it-rp-note'): out.append(f"Threat Vector's route: the note {pg.inner_text('.it-rp-note')!r}")
    if "can't read your game's avoidance list" not in pg.inner_text('.it-rp-note'): out.append(f"Threat Vector's route: the note should say it can't read the game's avoidance list (the hand test): {pg.inner_text('.it-rp-note')!r}")
    # a failure stops the rest; 403 and 401
    if len(path) >= 3:
        wreset(fail_at=2, fail=500); go('tv', d['i']); pg.wait_for_function("!itRp.busy", timeout=15000)
        nt = pg.inner_text('.it-rp-note')
        if len(WREQ) != 2 or 'ROUTE-01' not in nt or 'after waypoint 1 of' not in nt: out.append(f'a failure should stop the rest and say how far: {len(WREQ)} {nt!r}')
    wreset(fail_at=1, fail=403); go('eve', d['i']); pg.wait_for_function("!itRp.busy", timeout=8000)
    if 'SSO-07' not in pg.inner_text('.it-rp-note') or pg.evaluate("localStorage.getItem('tvRouteSend')") != 'false': out.append('403: SSO-07 and the switch off')
    pg.evaluate("() => itRpSendToggle(true)")   # the 403 turned it off; nothing turns it on again by itself (the hand test)
    wreset(fail_at=1, fail=401); go('eve', d['i']); pg.wait_for_timeout(100)
    pg.wait_for_function("!itRp.busy", timeout=8000)
    if WREQ and 'SSO-08' not in pg.inner_text('.it-rp-note'): out.append(f"401: SSO-08 {pg.inner_text('.it-rp-note')!r}")
    wreset(); go('eve', d['i']); pg.wait_for_timeout(300)
    if WREQ or 'log in again' not in pg.inner_text('.it-rp-note'): out.append(f'after a 401 nothing more is sent until a new login (SSO-08): {len(WREQ)} {pg.inner_text(".it-rp-note")!r}')
    pg.click('.it-rp-note [data-it-rp-nx]')
    if pg.evaluate("!document.querySelector('.it-rp-note').hidden"): out.append('the note should close from its close button')
    # storage: only the new keys; dscanIntel keeps its keys
    keys = pg.evaluate("() => Object.keys(JSON.parse(localStorage.getItem('dscanIntel')))")
    if any('rp' in k.lower() or 'route' in k.lower() for k in keys): out.append(f'dscanIntel should not change: {keys}')
    c.close()
    # ---- a phone: the tooltip's buttons
    if phone:
        c = ctx(390, 844); pp = start(c, phone=True)
        pp.wait_for_function("itm.home >= 0 && itm.box.clientWidth > 0", timeout=8000)
        i = pp.evaluate("() => { const T = itMapTable(); for(let i = 0; i < T.n; i++){ const x = itm.Q[2 * i], y = itm.Q[2 * i + 1]; if(itm.D[i] >= 2 && itm.D[i] <= 6 && x > 40 && x < itm.W - 40 && y > 130 && y < itm.H - 120) return i; } return -1; }")
        if i < 0: out.append('390 px: no system to press')
        else:
            px, py = pp.evaluate("(i) => { const r = itm.cv.getBoundingClientRect(); return [r.left + itm.Q[2 * i], r.top + itm.Q[2 * i + 1]]; }", i)
            pp.mouse.click(px, py); pp.wait_for_timeout(200)
            bt = pp.evaluate("() => [...itm.tip.querySelectorAll('[data-it-rp-go], [data-it-rp-av]')].map(b => Math.round(b.getBoundingClientRect().height)).concat([getComputedStyle(itm.tip).pointerEvents === 'auto' ? 1 : 0, document.scrollingElement.scrollWidth <= innerWidth + 1 ? 1 : 0, Math.round(document.querySelector('.it-rp-search input').getBoundingClientRect().height)])")
            if len(bt) != 6 or min(bt[:3]) < 44 or not bt[3] or not bt[4] or bt[5] < 44: out.append(f'390 px: three 44 px buttons in the tooltip, it takes presses, no sideways scroll, a 44 px search box: {bt}')
            elif not pp.evaluate("itm.tip.innerText").count('right-click') == 0: out.append('390 px: no right-click hint on a phone')
            else:
                pp.click('.it-map-tip [data-it-rp-go="eve"]'); pp.wait_for_timeout(200)
                if 'needs your EVE login' not in pp.inner_text('.it-rp-note'): out.append('390 px: a tooltip button should act (the note asks for the login)')
        c.close()
    return out, errs

MUTANTS = [
    ("the game's avoidance list not said (047, the hand test)", ", ['d', IT_RP_GAME_AVOID]];", "];"),
    ('sent while known logged off (047, the hand test)', "  if(onl === false && !force){", "  if(false){"),
    ('sending with the switch off (047, the hand test)', "  if(!itRpSendOn()){ itRpNote({off: true}); return; }", "  if(false){ itRpNote({off: true}); return; }"),
    ('the search box drawn by the browser (047, the hand test)', "  input[type=text], input[type=search], select{", "  input[type=text], select{"),
    ('the rounded number instead of the band', "function itRpBand(T, i){ if(T.band) return T.band[i];", "function itRpBand(T, i){"),
    ('cost before the flagged count (no detours)', "    const fx = f[x] + (x !== home && flags.has(x) ? 1 : 0);   // a system counts once you go through it: the destination never does\n", "    const fx = 0;\n"),
    ('the destination named in the warning', "return path.slice(1, -1).filter(x => itRp.flags.has(x))", "return path.slice(1).filter(x => itRp.flags.has(x))"),
    ('every waypoint clearing the others', "clear_other_waypoints: done === 0 ? 'true' : 'false'", "clear_other_waypoints: 'true'"),
    ('the waypoints sent at once', "      const r = await esiFetch(`${ESI}/ui/autopilot/waypoint/?${q}`, {method: 'POST'}, 'waypoints', {scope: SSO_WP});\n      if(r.status === 204 || r.ok)",
     "      const r = {status: 204}; esiFetch(`${ESI}/ui/autopilot/waypoint/?${q}`, {method: 'POST'}, 'waypoints', {scope: SSO_WP});\n      if(r.status === 204 || r.ok)"),
    ("the Intel example on Threat Vector's route", "  const rpAside = itRpAside; itRpAside = true;   // 047: its map keeps the shortest stargate routes (the build review)", "  const rpAside = itRpAside;"),
    ('kills still on the hostiles box (048, the owner)', "    if(s.kill && (st.kills || []).some(x => x.t >= keep)) add(i, 'kills');   // 048: its own box\n", "    if(s.host && (st.kills || []).some(x => x.t >= keep)) add(i, 'kills');\n"),
    ('a saved setting without kill avoids kills (048)', "    s.kill = typeof o.kill === 'boolean' ? o.kill : s.host;\n", "    s.kill = typeof o.kill === 'boolean' ? o.kill : true;\n"),
    ('no permission check before sending', "  if(!sso.who || !ssoHeld(SSO_WP)){ itRpNote({ask: true}); return; }", "  if(!sso.who){ itRpNote({ask: true}); return; }"),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, PAGE)
    for o in out: check(False, o)
    check(not out, "the route planner: the search's rules, the map, the search box, the menu, the Routes box, setting the destination, a phone")
    check(not errs, f'no page errors {errs[:3]}')
    for name, old, new in (MUTANTS if not os.environ.get('RP_FAST') else []):
        if PAGE.count(old) != 1: check(False, f'mutant "{name}": its line isn\'t in the page once'); continue
        try: mo, me = cases(b, PAGE.replace(old, new), phone=False)
        except Exception as ex: mo, me = [f'stopped: {str(ex).splitlines()[0]}'], []
        check(bool(mo) or bool(me), f'mutant "{name}" fails ({(mo or me or ["nothing"])[0][:90]})')
    b.close()
print('FAILURES:', fails)
sys.exit(1 if fails else 0)
