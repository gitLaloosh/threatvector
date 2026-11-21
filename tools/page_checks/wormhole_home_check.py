"""One Home on the Wormholes tab, and system names coloured from the map's table (build queue 063; Project doc roadmap/security-shown-plan.md and
the queue file's "one Home only" block). The owner: "wormholes tab, setting two systems as "Home" results in odd behavior. particularly related to
the routes.", "Only one Home: setting Home on a system clears it from the other, with a line saying so.", "do not overwrite the existing home.",
"pick the closest one and remove the other(s)", then at the 063 review "2. yes to both, 3. sure, 4. sure."

A made-up chain of CCP's own wormhole systems (the page's tables; names from INTEL_WH, no network). Checks:
  * setting Home on a system clears it from every other, with the line "<new>: Home. <old> is no longer Home."; tvWhMarks keeps one;
  * an import never replaces your Home: a shared system with Home arrives without it, yours stays;
  * with no Home of yours, a shared chain carrying two Homes: the closest to where you are keeps it, the other loses it, said in Add's line;
  * two Homes already saved (an older page): nothing changes while where you are isn't known (Routes shows the lowest ID); once it is, the one
    with the fewest jumps keeps Home (the higher ID here, so not by ID), with a line; a tie keeps the lowest ID; none reachable, the lowest ID;
  * names coloured from the table (the owner: "Read the table (Recommended)"): on a copy of the page given a made-up INTEL_MAP.secT, a k-space
    name (Juddi, checked in game: 0.6) takes its tenth from the table at once, with no ESI request; a J-space name still asks ESI; on the page as it is (no secT yet) a
    k-space name asks ESI as before;
  * mutants; no page errors.
"""
import sys, os, re, json, tempfile
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'tools'))
from check_sec_shown import with_secT
HTML = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith('--')), os.path.join(REPO, 'index.html')))
PAGE = open(HTML, encoding='utf-8').read()
fails = 0
def check(ok, msg):
    global fails
    print(('PASS ' if ok else 'FAIL ') + msg)
    if not ok: fails += 1

# a chain of five J-space systems, a - b - c - d - e, ids ascending; you in c. lone, lone2: on the map with no connection
SEED = """() => { const T = whTable(), J = T.ids.filter((id, i) => /^J\\d{6}$/.test(T.names[i]) && T.cls[i] === '3').slice(0, 7);
  const [a, b, c, d, e, lone, lone2] = J, t0 = Date.now() - 3600e3;
  whAddSys(a, t0); whAddSys(b, t0); whAddSys(c, t0); whAddSys(d, t0); whAddSys(e, t0); whAddSys(lone, t0); whAddSys(lone2, t0);
  whAddLink(a, b, t0); whAddLink(b, c, t0); whAddLink(c, d, t0); whAddLink(d, e, t0); whSave(); whPaint(true);
  return {a, b, c, d, e, lone, lone2, n: J.length}; }"""
HOMES = "() => whHomes()"
MSG = "() => document.querySelector('.wh-msg').textContent"
SET = "([n, v]) => { whS.menu = n; whMenuAct('st:' + v); }"

def start(b, html, errs, reqs, keep=False, ctx=None):
    ctx = ctx or b.new_context(bypass_csp=True, viewport={'width': 1440, 'height': 900})
    def rt(r):
        reqs.append(r.request.method + ' ' + r.request.url)
        return r.abort() if not r.request.url.startswith('file:') else r.continue_()
    ctx.route('**/*', rt)
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + html)
    if not keep: pg.evaluate("localStorage.clear()"); pg.reload()
    pg.wait_for_timeout(300); pg.evaluate("switchTab('wh')"); pg.wait_for_timeout(200)
    return ctx, pg

def chain(sysl):   # a shared chain (046's form), J-space systems with a status
    return json.dumps({'tv': 'wormholes', 'v': 1, 'sys': [], 'chain': {'sys': sysl, 'links': []}})

def import_(pg, text):
    pg.evaluate("whPopClose(); whPop('share')"); pg.click('.wh-pop[data-pop="share"] [data-it-whxb="imp"]')
    pg.fill('#whShImp textarea', text); pg.click('#whShImp [data-it-whimp]'); pg.wait_for_timeout(250)
    if pg.query_selector('#whShImp [data-it-whadd]'): pg.click('#whShImp [data-it-whadd]'); pg.wait_for_timeout(200)

def cases(b, html, parts=('set', 'import', 'saved', 'names')):
    out, errs, reqs = [], [], []
    if {'set', 'import', 'saved'} & set(parts):
        ctx, pg = start(b, html, errs, reqs); ev = pg.evaluate
        S = ev(SEED)
        if S['n'] < 7: out.append(f'the seed: {S}')
        nm = lambda n: ev("(n) => whName(n)", n)
        ev("(n) => whSeen(n, Date.now() - 1000, false)", S['c'])   # you are in c
        if 'set' in parts:
            ev(SET, [S['b'], 'home'])
            ev(SET, [S['e'], 'home']); h = ev(HOMES); m = ev(MSG)
            stored = [k for k, v in json.loads(ev("localStorage.getItem('tvWhMarks')"))['sys'].items() if v.get('st') == 'home']
            if h != [S['e']] or stored != [str(S['e'])]: out.append(f'a second Home clears the first: {h}, stored {stored} (want only {S["e"]})')
            if m != f"{nm(S['e'])}: Home. {nm(S['b'])} is no longer Home.": out.append(f'the line saying so: {m!r}')
            ev(SET, [S['e'], 'friendly'])
            if ev(HOMES): out.append('another status on your Home: no Home left')
        if 'import' in parts:
            ev(SET, [S['a'], 'home'])   # yours 2 jumps from you; theirs (d) 1 jump: closer, so the closest rule can't hide a Home taken over yours
            t = int(ev("Date.now()")) - 5000
            import_(pg, chain([{'id': S['d'], 'name': nm(S['d']), 't': t, 'st': 'home'}, {'id': S['lone'], 'name': nm(S['lone']), 't': t, 'st': 'home'}]))
            h = ev(HOMES); std = ev("(n) => whMk(n).st || ''", S['d'])
            if h != [S['a']] or std: out.append(f'an import never replaces your Home: {h}, the shared Home on yours: {std!r} (want only {S["a"]})')
            ev(SET, [S['a'], ''])   # no status at all (an import sets a status only where yours is empty)
            if ev(HOMES) or ev("(n) => whMk(n).st || ''", S['a']): out.append('the seed for "no Home of yours": a status left')
            # no Home of yours: a chain with two Homes, d 1 jump from you (c), a 2 jumps: the closest (d, the higher ID) keeps it
            import_(pg, chain([{'id': S['a'], 'name': nm(S['a']), 't': t, 'st': 'home'}, {'id': S['d'], 'name': nm(S['d']), 't': t, 'st': 'home'}]))
            h = ev(HOMES); m = ev(MSG)
            if h != [S['d']]: out.append(f'a shared chain with two Homes, none of yours: the closest keeps it: {h} (want {S["d"]})')
            if f"{nm(S['d'])} is your Home (the closest to you). {nm(S['a'])} is no longer Home." not in m: out.append(f"Add's line names them: {m!r}")
            ev(SET, [S['d'], 'friendly'])
        ctx.close()
    if 'saved' in parts:
        # two saved by an older page; where you are not known after the reload
        def saved(homes, you):
            ctx, pg = start(b, html, errs, reqs); ev = pg.evaluate; S = ev(SEED)
            ev("(hs) => { for(const n of hs) whS.mk[n] = {st: 'home'}; whMkSave(); }", [S[k] for k in homes]); pg.reload(); pg.wait_for_timeout(300); pg.evaluate("switchTab('wh')"); pg.wait_for_timeout(150)
            before = [ev(HOMES), ev("() => whRtHome()")]
            ev("(n) => whSeen(n, Date.now() - 1000, false)", S[you]); pg.wait_for_timeout(50)
            r = (S, before, ev(HOMES), ev(MSG), json.loads(ev("localStorage.getItem('tvWhMarks')"))['sys']); ctx.close(); return r
        S, before, after, m, st = saved(('a', 'd'), 'c')   # a 2 jumps, d 1 jump
        if before != [[S['a'], S['d']], S['a']]: out.append(f'two saved, where you are not known: both kept, Routes the lowest ID: {before}')
        if after != [S['d']] or [k for k, v in st.items() if v.get('st') == 'home'] != [str(S['d'])]: out.append(f'two saved, then where you are: the closest (not the lowest ID) keeps it: {after}')
        if 'is your Home (the closest to you).' not in m or 'is no longer Home.' not in m: out.append(f'the line saying so: {m!r}')
        S, _, after, _, _ = saved(('b', 'd'), 'c')   # both 1 jump: a tie
        if after != [S['b']]: out.append(f'a tie keeps the lowest ID: {after} (want {S["b"]})')
        S, _, after, _, _ = saved(('lone', 'lone2'), 'c')   # none reachable
        if after != [min(S['lone'], S['lone2'])]: out.append(f'none reachable keeps the lowest ID: {after}')
    if 'names' in parts:
        src2, _ = with_secT(PAGE)
        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(html)) as f:
            f.write(src2 if html == HTML else with_secT(open(html, encoding='utf-8').read())[0]); sp = f.name
        try:
            r2 = []; ctx, pg = start(b, sp, errs, r2); ev = pg.evaluate
            jid = ev("() => whTable().ids[5]")
            got = ev("(j) => { const a = document.createElement('div'); a.innerHTML = sysNameHtml(30000051, 'Juddi') + sysNameHtml(j, 'J'); document.body.appendChild(a); return [...a.children].map(e => e.className); }", jid)
            pg.wait_for_timeout(300)
            asked = [u for u in r2 if '/universe/systems/' in u]
            if 's6' not in got[0].split() or 'hs' not in got[0].split() or any('/systems/30000051/' in u for u in asked): out.append(f'a k-space name from the table: {got[0]!r}, asked {asked[:3]}')
            if not any(f'/systems/{jid}/' in u for u in asked): out.append(f'a J-space name still asks ESI: {asked[:3]}')
            if ev("() => [itSecText(30000051), itSecKey(30000051), itSysTitle(30000051).endsWith('(security 0.6)')]") != ['0.6', 6, True]: out.append('Juddi\'s text, key and title from the table (0.6: CCP 0.649, 0.7 from the old double rounding)')
            ctx.close()
        finally: os.unlink(sp)
        if '"secT"' not in re.search(r'^const INTEL_MAP = (.*);$', open(html, encoding='utf-8').read(), re.M).group(1):
            r3 = []; ctx, pg = start(b, html, errs, r3); ev = pg.evaluate
            ev("() => { const a = document.createElement('div'); a.innerHTML = sysNameHtml(30000142, 'Jita'); document.body.appendChild(a); }"); pg.wait_for_timeout(300)
            if not any('/systems/30000142/' in u for u in r3): out.append('the page as it is (no secT yet): a k-space name asks ESI as before')
            ctx.close()
    return out, errs

MUTANTS = [
    ('two Homes left after a set', "const off = m.st === 'home' ? whHomeOthersOff(n) : [];", "const off = [];", ('set',)),
    ('an imported Home over yours', "const x = mine && x0.st === 'home' ? {...x0, st: ''} : x0;", "const x = x0;", ('import',)),
    ('a chain\'s Homes not settled after Add', "const hm = whHomeOne();   // 063: a chain", "const hm = '';   // 063: a chain", ('import',)),
    ('two saved settled by ID, not by distance', "if(d >= 0 && (best < 0 || d < best)){ best = d; keep = n; }", "if(false){ }", ('saved',)),
    ('two saved never settled', "  const hm = whHomeOne(); if(hm) whMsg(hm, true);", "  const hm = '';", ('saved',)),
    ('names never from the table', "  const T = itMapTable(); if(!T || !T.secT) return undefined;", "  return undefined;", ('names',)),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, 'one Home: set, import, two saved (closest, wait, tie, none reachable); names from the table')
    check(not errs, f'no page errors {errs[:3]}')
    for name, old, new, parts in MUTANTS:
        if PAGE.count(old) != 1: check(False, f'mutant "{name}": its line isn\'t in the page once ({PAGE.count(old)})'); continue
        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f:
            f.write(PAGE.replace(old, new)); mp = f.name
        try:
            mo, me = cases(b, mp, parts)
            check(bool(mo) or bool(me), f'mutant "{name}" fails ({(mo or me or ["nothing"])[0][:90]})')
        finally: os.unlink(mp)
    b.close()
print('FAILURES:', fails)
sys.exit(1 if fails else 0)
