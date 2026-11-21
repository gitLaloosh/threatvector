"""System names found without their "-", in every box where a system is typed (build queue 064; Project doc roadmap/dashless-search-plan.md,
now roadmap/dashless-search-plan.md). The owner: "system search in intel map should be searchable without "-" and still hit. test for any
conflicts if done this way.", "(should be the case in all system searches for all tabs)", then "1. just the feed search box, 2. your
recommendation, 3. no mockup." Also the three Intel bugs seen in J-space that went with 064 (the owner: "left panel bug"; the review's answers
"With the Wormholes tab hint (Recommended)", "Yes, same wording (Recommended)").

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/dashless_search_check.py [index.html]   -> 'FAILURES: N' (must be 0)
    (DS_FAST=1 skips the mutants.)

Uses intel_check.py's made-up folder, mocks and names (you in 1DQ1-A; the real dashed names it gives, the rest "N<id>"); made-up names for the
shared-form guard; CCP's own J-space table. Checks:
  * the helpers: a dashless name finds its system ("1dq1a" is 1DQ1-A), any case; a name typed with its "-" matches exactly as before; a query
    with a "-" suggests exactly what the map search did before 064 (the old code run beside it); starts-with ahead of contains; a dashless form
    two systems share lists both and picks neither (and the box says so); the 'k' scope never gives a J-space system, 'all' does;
  * each box: the Intel map's search (its list, Enter picks), Routes -> Avoid, Intel's Wormholes list -> Add, the "word = system" list, the
    System Analyzer's typed box (the map search's list, not the browser's datalist: arrows and Enter pick, not cut off by the panel at 1440 and
    390 px, 44 px rows on a phone), the Wormholes tab's + Add / "Add a system here" / Routes pin; the Feed search finds a dashless name, and a
    query with its "-" sees the text as before; pasted Sov / bridge lists and the chat reader unchanged (they keep byLower);
  * J-space with no known way in: the map box shows only its message (no filter column, canvas, search, zoom or rail) and Near You is hidden,
    all back once there is a map (the filter column in one column at 1440); the status line names the J-space system, not its
    ID; Intel's line, the map's message and the System Analyzer's "My location" say "You're in J… and where you came in isn't known (link it on
    the Wormholes tab)";
  * mutants; no page errors.
"""
import sys, os, re, json, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
_src = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
_src = _src[:_src.index('with sync_playwright() as p:')]
NS = {'__file__': os.path.join(HERE, 'intel_check.py'), '__name__': 'intel_check_prefix'}
exec(compile(_src, 'intel_check.py (first part)', 'exec'), NS)   # the made-up folder, mocks, names; its table checks run too
globals().update({k: v for k, v in NS.items() if not k.startswith('__') and k not in ('check', 'fails')})
from playwright.sync_api import sync_playwright
check = NS['check']
PAGE = open(HTML, encoding='utf-8').read()
HOME = SYSID['1DQ1-A']
QX = SYSID['QX-LIJ']

def start(b, html, w, errs, h=1000, touch=False):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch, device_scale_factor=2 if touch else 1)
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); route(ctx)
    pg = ctx.new_page(); pg.goto('file://' + html)
    pg.evaluate("(s) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({channels: ['region.intel'], me: 95000001, range: 3, sound: false, notify: false, forget: 15})); }", SIDE)
    pg.reload(); pg.wait_for_timeout(400)
    setup_logs(pg); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg, 3200)
    pg.evaluate("() => document.querySelector('#intelPanel .it-map-box').scrollIntoView({block: 'center'})"); pg.wait_for_timeout(200)
    return ctx, pg

# before 064: the map search's suggestions (the old code, run beside the new one)
OLD = """(q) => { q = q.trim().toLowerCase(); const a = [], b = [];
  for(const nm of it.names.list){ if(nm.startsWith(q)) a.push(nm); else if(b.length < 8 && nm.includes(q)) b.push(nm); }
  return [...a.sort(), ...b.sort()].slice(0, 8).map(nm => it.names.byLower.get(nm)); }"""
# made-up names (the guard): two that share a dashless form, and a starts-with / contains pair
MADE = """() => { const keep = it.names, ids = itGraphGet().ids, byLower = new Map(), byId = new Map();
  const nm = {[ids[10]]: 'AB-C12', [ids[11]]: 'A-BC12', [ids[12]]: 'XQZ-7', [ids[13]]: 'PXQZ-1', [ids[14]]: 'Plainname'};
  for(const [id, n] of Object.entries(nm)){ byLower.set(n.toLowerCase(), Number(id)); byId.set(Number(id), n); }
  it.names = {byLower, byId, list: [...byLower.keys()], heads: new Map()};
  const r = {shared: sysFind('abc12', 'k'), dash1: sysFind('ab-c12', 'k'), dash2: sysFind('A-BC12', 'k'), half: sysFind('ab-c1', 'k'), plain: sysFind('PLAINNAME', 'k'),
    order: sysSuggest('xqz', 8, 'k').map(id => byId.get(id)), many: sysManyText('abc12', [ids[10], ids[11]]), ids: [ids[10], ids[11]],
    alias: (() => { const a0 = it.set.alias; it.set.alias = 'x = abc12'; itAliasMemo = null; const rows = itAliases().rows; it.set.alias = a0; itAliasMemo = null; return rows; })(),
    wh: (() => { const r0 = itWhAdd('abc12'); return r0; })()};
  it.names = keep; return r; }"""

def cases(b, html, parts=('help', 'boxes', 'sa', 'wh', 'feed', 'jspace', 'phone')):
    out, errs = [], []
    ctx, pg = start(b, html, 1440, errs)
    if not pg.evaluate("typeof sysFind === 'function' && typeof sysSuggest === 'function'"): out.append('no sysFind / sysSuggest on the page'); ctx.close(); return out, errs
    if not pg.evaluate("!!it.names"): pg.evaluate("itLoadNames()"); pg.wait_for_timeout(300)
    if 'help' in parts:
        r = pg.evaluate("([h, q]) => [sysFind('1dq1a', 'k') === h, sysFind('1DQ1A', 'k') === h, sysFind('1DQ1-A', 'k') === h, sysFind('1dq1-', 'k'), sysFind('qxlij', 'k') === q, sysFind('nowhere', 'k')]", [HOME, QX])
        if r != [True, True, True, None, True, None]: out.append(f'sysFind: 1dq1a / 1DQ1A / 1DQ1-A / 1dq1- / qxlij / nowhere: {r}')
        for q in ('m-', '1dq1-', 'qx-', '8-', '4k-', '-a', 'n3000', 'jita'):   # with a "-" (and two no dash could change): as before
            a, o = pg.evaluate("([q, old]) => [sysSuggest(q, 8, 'k'), eval(old)(q)]", [q, OLD])
            if a != o: out.append(f'"{q}": suggests {a} (before 064: {o})')
        r = pg.evaluate("(h) => { const s = sysSuggest('1dq1a', 8, 'k'); return [s[0] === h, sysSuggest('qxli', 8, 'k').map(itSysName)]; }", HOME)
        if not r[0] or r[1] != ['QX-LIJ']: out.append(f'dashless suggestions: "1dq1a" first is 1DQ1-A {r[0]}, "qxli" {r[1]}')
        M = pg.evaluate(MADE)
        sh = M['shared'] if isinstance(M['shared'], list) else [M['shared']]
        if sorted(x or 0 for x in sh) != sorted(M['ids']) or M['dash1'] != M['ids'][0] or M['dash2'] != M['ids'][1] or M['half'] is not None or not M['plain']:
            out.append(f"the shared form: abc12 {M['shared']} (want both), ab-c12 {M['dash1']}, A-BC12 {M['dash2']}, ab-c1 {M['half']} (want null), PLAINNAME {M['plain']}")
        if M['order'] != ['XQZ-7', 'PXQZ-1']: out.append(f"starts-with ahead of contains: {M['order']}")
        if 'matches 2 systems' not in M['many'] or 'AB-C12' not in M['many'] or 'type it with its dash' not in M['many']: out.append(f"the shared-form line: {M['many']!r}")
        if not any('matches 2 systems' in (x.get('bad') or '') for x in M['alias']): out.append(f"the word = system list with a shared form: {M['alias']}")
        if M['wh'].get('ok') or 'matches 2 systems' not in M['wh'].get('msg', ''): out.append(f"Intel's Wormholes Add with a shared form: {M['wh']}")
        J = pg.evaluate("""() => { const T = whTable(), i = T.names.findIndex(n => /^J\\d{6}$/.test(n)), d = T.names.findIndex(n => n.includes('-'));
          return {j: T.names[i], jid: T.ids[i], d: T.names[d], did: T.ids[d], k: sysFind(T.names[i], 'k'), a: sysFind(T.names[i].toLowerCase(), 'all'),
            dd: d >= 0 ? sysFind(T.names[d].replace(/-/g, ''), 'all') : null, sk: sysSuggest('j1', 8, 'k').filter(whIsJ).length, sa: sysSuggest('j1', 8, 'all').filter(whIsJ).length,
            kAll: sysFind('1dq1a', 'all')}; }""")
        if J['k'] is not None or J['a'] != J['jid'] or J['sk'] != 0 or J['sa'] == 0 or J['kAll'] != HOME: out.append(f"scope: a J-space name in 'k' {J['k']}, in 'all' {J['a']} (want {J['jid']}); J-space in a 'k' list {J['sk']}, in 'all' {J['sa']}; 1dq1a in 'all' {J['kAll']}")
        if J['did'] and J['dd'] != J['did']: out.append(f"the dashed J-space name {J['d']} found without its dash: {J['dd']}")
    if 'boxes' in parts:
        pg.click('.it-rp-search input'); pg.keyboard.type('1dq1a'); pg.wait_for_timeout(200)
        o = pg.evaluate("[...document.querySelectorAll('#itRpSug [data-sys-pick]')].map(li => li.querySelector('.it-sn').textContent)")
        if not o or o[0] != '1DQ1-A': out.append(f'the map search "1dq1a": {o}')
        pg.fill('.it-rp-search input', 'qx-'); pg.wait_for_timeout(200)
        o = pg.evaluate("[...document.querySelectorAll('#itRpSug [data-sys-pick]')].map(li => Number(li.dataset.sysPick))")
        if o != pg.evaluate(f"({OLD})('qx-')"): out.append(f'the map search "qx-": {o} (want what it gave before 064)')
        pg.fill('.it-rp-search input', 'qxlij'); pg.wait_for_timeout(200); pg.keyboard.press('ArrowDown'); pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
        if pg.evaluate("(q) => itRp.sel === itGraphGet().at.get(q) && document.querySelector('.it-rp-search input').value === 'QX-LIJ'", QX) is not True: out.append('the map search: Enter on "qxlij" picks QX-LIJ')
        pg.evaluate("() => { it.pop = true; itRender(true); }"); pg.wait_for_timeout(250)
        pg.fill('.it-rp-add input[name=sys]', 'qxlij'); pg.click('.it-rp-add button'); pg.wait_for_timeout(200)
        if QX not in (pg.evaluate("JSON.parse(localStorage.getItem('tvRoute') || '{}').list") or []): out.append('Routes -> Avoid: "qxlij" adds QX-LIJ')
        pg.evaluate("() => { it.pop = false; itRender(true); }"); pg.wait_for_timeout(150)
        r = pg.evaluate("(q) => { const a = itWhAdd('qxlij'); return [a.ok, !!itWhStore().rep[q]]; }", QX)
        if r != [True, True]: out.append(f"Intel's Wormholes list -> Add \"qxlij\": {r}")
        r = pg.evaluate("(h) => { const a0 = it.set.alias; it.set.alias = 'home = 1dq1a'; itAliasMemo = null; const id = itAliases().map.get('home'); it.set.alias = a0; itAliasMemo = null; return id === h; }", HOME)
        if not r: out.append('the word = system list: "home = 1dq1a" is 1DQ1-A')
        u = pg.evaluate("(h) => [sovParse('1dq1a <- Major Threat Detection Array 1', '').rows.some(r => r.ok), itBridgeNames('1dq1a qxlij').length]", HOME) if pg.evaluate("typeof sovParse === 'function'") else None
        if u and (u[0] or u[1]): out.append(f'pasted Sov / bridge lists should still need the dash (unchanged by choice): {u}')
    if 'feed' in parts:
        r = pg.evaluate("(h) => { const e = {pilots: [], raw: 'x', who: '', p: {sys: [{id: h}], ships: []}}; return [itSearchText(e, true).includes('1dq1a'), itSearchText(e, false).includes('1dq1a'), itSearchText(e, false) === itSearchText(e)]; }", HOME)
        if r != [True, False, True]: out.append(f'the Feed text: dashless with a dashless query {r[0]}, not with a dashed one {r[1]}, as before {r[2]}')
        n = pg.evaluate("(h) => { const e = it.feed.find(x => x.p && x.p.sys && x.p.sys.some(s => s.id === h)); return e ? 1 : 0; }", HOME)
        if n:
            pg.fill('[data-it-q]', '1dq1a'); pg.wait_for_timeout(300)
            k = pg.evaluate("(h) => itFeedShown().length > 0 && itFeedShown().every(e => e.p && e.p.sys && e.p.sys.some(s => s.id === h) || itSearchText(e, true).includes('1dq1a'))", HOME)
            if not k: out.append('the Feed search "1dq1a" finds the reports in 1DQ1-A')
            pg.fill('[data-it-q]', ''); pg.wait_for_timeout(200)
    if 'sa' in parts:
        out += sa_box(pg, 1440)
    if 'wh' in parts:
        r = pg.evaluate("""(h) => { switchTab('wh'); const T = whTable(), i = T.names.findIndex(n => /^J\\d{6}$/.test(n));
          return [whNameIn('1dq1a') === h, whNameIn(T.names[i].toLowerCase()) === T.ids[i], whNameIn('nowhere'), whNameMiss('nowhere').includes('isn’t a wormhole system')]; }""", HOME)
        if r != [True, True, None, True]: out.append(f"the Wormholes tab's + Add / Add a system here: 1dq1a {r[0]}, a J-space name {r[1]}, nowhere {r[2]}, its line {r[3]}")
        pg.wait_for_timeout(200)
        p = pg.evaluate("(h) => { const R = whRtState(); whRtPinForm({sys: {value: '1dq1a'}, contains: () => false}); return whRtState().pins.includes(h); }", HOME)
        if not p: out.append("the Wormholes tab's Routes pin: \"1dq1a\" pins 1DQ1-A")
        pg.evaluate("switchTab('intel')"); pg.wait_for_timeout(300)
    if 'jspace' in parts:
        out += jspace(pg, 1440)
    ctx.close()
    if 'phone' in parts:
        ctx, pg = start(b, html, 390, errs, h=844, touch=True)
        if not pg.evaluate("!!it.names"): pg.evaluate("itLoadNames()"); pg.wait_for_timeout(300)
        out += sa_box(pg, 390)
        out += jspace(pg, 390)
        sw = pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
        if not sw: out.append('390: the page scrolls sideways')
        ctx.close()
    return out, errs

def sa_box(pg, w):
    out = []
    pg.evaluate("() => { switchTab('dscan'); saSetToggle(true); }"); pg.wait_for_timeout(300)
    if pg.evaluate("!!document.querySelector('#saPop datalist, #saPop [list]')"): out.append(f'{w}: the typed box still uses the browser\'s datalist')
    inp = '#saPop .sa-sys-search input'
    if not pg.locator(inp).count(): out.append(f'{w}: no typed box with the shared list'); return out
    pg.click(inp); pg.fill(inp, ''); pg.keyboard.type('1dq1'); pg.wait_for_timeout(250)
    L = pg.evaluate("""() => { const ul = document.getElementById('saSysSug'), pop = document.getElementById('saPop'), r = ul.getBoundingClientRect(), p = pop.getBoundingClientRect();
      const lis = [...ul.querySelectorAll('[data-sys-pick]')];
      return {shown: !ul.hidden, first: lis[0] && lis[0].querySelector('.it-sn').textContent, n: lis.length, inPop: r.left >= p.left - 1 && r.right <= p.right + 1 && r.top >= p.top - 1,
        inView: r.left >= 0 && r.right <= innerWidth + 1, h: lis.length ? Math.round(lis[0].getBoundingClientRect().height) : 0,
        exp: document.querySelector('#saPop .sa-sys-search input').getAttribute('aria-expanded'), cls: ul.className}; }""")
    if not L['shown'] or L['first'] != '1DQ1-A' or L['exp'] != 'true' or L['cls'] != 'it-rp-sug': out.append(f'{w}: the System Analyzer\'s list for "1dq1": {L}')
    if not L['inPop'] or not L['inView']: out.append(f'{w}: the list is cut off: inside the panel {L["inPop"]}, inside the window {L["inView"]}')
    if w < 600 and L['h'] < 44: out.append(f'{w}: a suggestion row is {L["h"]} px (want 44 on a phone)')
    pg.keyboard.press('ArrowDown'); pg.keyboard.press('Enter'); pg.wait_for_timeout(400)
    if pg.evaluate("[saSet.typed, saSet.src]") != ['1DQ1-A', 'typed']: out.append(f'{w}: arrows and Enter pick 1DQ1-A: {pg.evaluate("[saSet.typed, saSet.src]")}')
    pg.fill(inp, 'qxlij'); pg.keyboard.press('Escape'); pg.wait_for_timeout(100); pg.keyboard.press('Enter'); pg.wait_for_timeout(400)
    if pg.evaluate("saSet.typed") != 'QX-LIJ': out.append(f'{w}: Enter with the list shut takes "qxlij" as QX-LIJ: {pg.evaluate("saSet.typed")}')
    pg.evaluate("() => { saSetToggle(false); switchTab('intel'); }"); pg.wait_for_timeout(300)
    return out

def jspace(pg, w):
    out = []
    J = pg.evaluate("() => { const T = whTable(), i = T.names.findIndex(n => /^J\\d{6}$/.test(n)); return [T.ids[i], T.names[i]]; }")
    pg.evaluate("""(j) => { it.set.nearShown = true; window.__glKeep = itGlSys; window.itGlSys = () => j; const S = whState(); window.__whLast = S.last; S.last = j; itMapRefresh(true); itRender(true); }""", J[0]); pg.wait_for_timeout(400)
    line = f'You’re in {J[1]} and where you came in isn’t known (link it on the Wormholes tab)'
    R = pg.evaluate("""() => { const fb = itm.el.querySelector('.it-map-fb'), msg = itm.el.querySelector('.it-map-msg'), d = (e) => !e || getComputedStyle(e).display === 'none';
      return {fbHidden: d(fb), rest: [itm.cv, itm.el.querySelector('.it-rp-search'), itm.el.querySelector('.it-map-zoom'), itm.el.querySelector('.it-map-rail')].every(d),
        ny: d(document.getElementById('itNearCol')), msgShown: !d(msg), msg: msg.hidden ? '' : msg.textContent, warn: itNoSysWarnHtml(), status: itStatusLine()}; }""")
    if not R['fbHidden']: out.append(f'{w}: the filter column shown with no map')
    if not R['rest'] or not R['ny'] or not R['msgShown']: out.append(f"{w}: no map: the canvas, search, zoom and rail hidden {R['rest']}, Near You hidden {R['ny']}, the message shown {R['msgShown']}")
    if R['msg'] != line + '.': out.append(f"{w}: the map's message in J-space: {R['msg']!r}")
    if line + ', so no jumps and no alerts until then.' not in R['warn']: out.append(f"{w}: Intel's line in J-space: {R['warn'][:200]!r}")
    if f' in {J[1]}' not in R['status'] or str(J[0]) in R['status']: out.append(f"{w}: the status line names {J[1]}: {R['status'][:160]!r}")
    sa = pg.evaluate("async () => { const s0 = saSet.src; saSet.src = 'me'; const r = await saActSystem(); saSet.src = s0; return r; }")
    if sa.get('none') != line: out.append(f"{w}: the System Analyzer's My location in J-space: {sa}")
    pg.evaluate("() => { window.itGlSys = window.__glKeep; whState().last = window.__whLast; itMapRefresh(true); itRender(true); }"); pg.wait_for_timeout(500)
    B = pg.evaluate("() => { const fb = itm.el.querySelector('.it-map-fb'), bs = fb.querySelector('.it-map-fbtns'); return [itm.box.classList.contains('nomap'), getComputedStyle(fb).display, Number(bs.style.getPropertyValue('--it-flr')), getComputedStyle(itm.cv).display, getComputedStyle(document.getElementById('itNearCol')).display]; }")
    if B[0] or B[1] == 'none' or B[3] == 'none' or B[4] == 'none': out.append(f'{w}: back in k-space the filter column, the map and Near You are shown: {B}')
    if w >= 600 and B[2] < 6: out.append(f'{w}: the filter column\'s rows {B[2]} with the map back (want one column)')
    if pg.evaluate("itNoSysJ()") != '': out.append(f'{w}: out of J-space, no J-space line')
    return out

MUTANTS = [
    ('dashes dropped from a query that has one', "  const flat = !q.includes('-'), qq = flat ? sysFlatKey(q) : q, a = [], b = [];", "  const flat = true, qq = flat ? sysFlatKey(q) : q, a = [], b = [];"),
    ('a shared dashless form picks the first', "  return hits.length === 1 ? hits[0] : hits.length ? hits : null;", "  return hits.length ? hits[0] : null;"),
    ('J-space in a stargate-only list', "  for(const M of scope === 'all' ? [K, sysFlatJ()] : [K]) for(const [l, f, id] of M.rows){", "  for(const M of [K, sysFlatJ()]) for(const [l, f, id] of M.rows){"),
    ('contains ahead of starts-with', "  return [...a.sort(by), ...b.sort(by)].slice(0, n).map(x => x[1]);", "  return [...b.sort(by), ...a.sort(by)].slice(0, n).map(x => x[1]);"),
    ('the Feed without the dashless names', "if(flat && nm.includes('-')) parts.push(nm.replace(/-/g, ''));", "if(false) parts.push(nm.replace(/-/g, ''));"),
    ("the System Analyzer's list not bound", "  if(inp && ul) sysComboBind(inp, ul, {", "  if(false) sysComboBind(inp, ul, {"),
    ('Avoid still exact', "r = v && it.names ? sysFind(v, 'k') : null, id = typeof r === 'number' ? r : undefined", "r = v && it.names ? it.names.byLower.get(v.toLowerCase()) : null, id = typeof r === 'number' ? r : undefined"),
    ("the Wormholes tab's boxes still exact", "function whNameIn(raw){ const r = sysFind(raw, 'all'),", "function whNameIn(raw){ const r = whIdOf(raw),"),
    ('the box not marked when there is no map', "  if(itm.box.classList.contains('nomap') !== !!why) itm.box.classList.toggle('nomap', !!why);", "  0;"),
    ('no map, the controls still shown', " .it-map-box.nomap > :not(.it-map-msg){display:none !important;}", " .it-map-box.nomap > .nothing{display:none !important;}"),
    ('no map, Near You still shown', " .it-top:has(.it-map-box.nomap) .it-nearcol{display:none !important;}", " .it-top:has(.nothing) .it-nearcol{display:none !important;}"),
    ('the status line by itSysName', "mnm = (itGlSys() ? whName(itGlSys()) : it.me && it.me.sys)", "mnm = (itGlSys() ? itSysName(itGlSys()) : it.me && it.me.sys)"),
    ('no J-space line', "function itNoSysText(){ const j = itNoSysJ(); if(j) return j; return", "function itNoSysText(){ return"),
    ("the System Analyzer's old line", "{none: itNoSysJ() || 'Your location", "{none: 'Your location"),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, f'dashless names in every system box, the J-space lines ({len(out)} problems)')
    check(not errs, f'no page errors ({errs[:2]})')
    if not os.environ.get('DS_FAST'):
        PARTS = {'dashes dropped from a query that has one': ('help',), 'a shared dashless form picks the first': ('help',), 'J-space in a stargate-only list': ('help',),
                 'contains ahead of starts-with': ('help',), 'the Feed without the dashless names': ('feed',), "the System Analyzer's list not bound": ('sa',),
                 'Avoid still exact': ('boxes',), "the Wormholes tab's boxes still exact": ('wh',), 'the box not marked when there is no map': ('jspace',), 'no map, the controls still shown': ('jspace',), 'no map, Near You still shown': ('jspace',),
                 'the status line by itSysName': ('jspace',), 'no J-space line': ('jspace',), "the System Analyzer's old line": ('jspace',)}
        for name, a, bb in MUTANTS:
            if PAGE.count(a) != 1: check(False, f'mutant "{name}": its text is in the page ({PAGE.count(a)})'); continue
            with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f: f.write(PAGE.replace(a, bb)); mp = f.name
            try:
                mo, me = cases(b, mp, PARTS[name])
                check(bool(mo) or bool(me), f'mutant caught: {name}' + (f' ({mo[0][:90]})' if mo else ''))
            finally: os.unlink(mp)
    b.close()
print(f'FAILURES: {NS["fails"]}')
sys.exit(1 if NS['fails'] else 0)
