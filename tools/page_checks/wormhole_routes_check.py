"""The Wormholes tab's Routes panel (build queue 062, R1-R9; Project doc roadmap/wormholes-part4-plan.md section 2; mockup Claude outputs/
wh_part4_mockup.html). The owner: "we need to be able to pin multiple systems that the page will automatically calculate the route to each time we
navigate another system/wormhole.", "the game's routing doesn't work inside of wormholes so it's only meant to be a point of reference.", "sig id is
useful if it was recorded but not required", "get rid of the "set destination" button and we'll just show the route as it's represented in the panel."

A made-up chain of CCP's own systems (the page's tables; k-space systems by map index, no names needed); no network. Checks:
  * the rail's second button opens Routes (one panel at a time; tvWhPanels 'rt' kept; an older page (f70fdd5) reads it as shut);
  * the rows: Home (a system with the Home status), nearest highsec, nearest lowsec, then the pins in the order pinned; no quick row for the band
    you're in; a pin with no route says so;
  * the strip: one square a jump, the hole jumps counted; a jump through a hole round; J-space squares in the wormhole colour;
  * the hover (and keyboard focus): a gate's line "0.5 <name> · <region>"; a hole's "A → B" with its ID and type only when recorded (never "ID
    not known"), its life / mass / size; the row's other squares dimmed; the row's route on the chain map only while hovered;
  * worked out again once after a jump (one search for every row) and not at all on an unchanged repaint;
  * a route through the chain then the gates; from k-space into J-space; your statuses never change a route (Q2);
  * pin by typing (a J-name), by the map's menu (Pin route / Unpin route), × unpins; tvWhRoutes and Shortest kept through a reload;
  * Routes from here (the menu) and "From where you are";
  * no Set destination in the panel, nothing sent to EVE (no autopilot or route request);
  * 047's route unchanged by the shared search: itRpUpdate's parents equal f70fdd5's for several homes, flags and preferences;
  * 1440 / 390 px: 44 px targets on a phone (the strip one target), no sideways scroll;
  * mutants; no page errors.
"""
import sys, os, re, json, tempfile, subprocess
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
HTML = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith('--')), os.path.join(REPO, 'index.html')))
PAGE = open(HTML, encoding='utf-8').read()
OLD = 'f70fdd5'   # v2026.11.20.1, the last main before 062: never origin/main (LESSON #168)
fails = 0
def check(ok, msg):
    global fails
    print(('PASS ' if ok else 'FAIL ') + msg)
    if not ok: fails += 1

# k: a highsec system next to a lowsec one (by stargate); j3 a C3, j2 a C2: k - j3 - j2; you in j2. far: a k-space system well away (the pin)
SEED = """() => { const T = whTable(), g = itGraphGet(), M = itMapTable(), pick = (f) => T.ids.find((id, i) => f(i));
  let k = -1; for(let x = 0; x < M.n && k < 0; x++) if(itRpBand(M, x) === 2 && M.adj[x].some(y => itRpBand(M, y) === 1) && M.adj[x].length >= 2) k = x;
  const j3 = pick(i => T.cls[i] === '3' && /^J\\d{6}$/.test(T.names[i])), j2 = pick(i => T.cls[i] === '2' && /^J\\d{6}$/.test(T.names[i])), jx = pick(i => T.cls[i] === '5' && /^J\\d{6}$/.test(T.names[i]));
  const t0 = Date.now() - 3600e3, kid = g.ids[k]; whSeen(kid, t0, false); whSeen(j3, t0 + 60e3, false); whSeen(j2, t0 + 120e3, false); whSave();
  let far = -1; { const d = new Int32Array(M.n).fill(-1), q = [k]; d[k] = 0; for(let h = 0; h < q.length; h++) for(const y of M.adj[q[h]]) if(d[y] < 0){ d[y] = d[q[h]] + 1; q.push(y); if(d[y] === 12 && far < 0) far = y; } }
  return {k: kid, j3, j2, jx, far: g.ids[far]}; }"""
OPEN = "() => { whPnSet('rt'); whPaint(true); }"
ROWS = "() => (whRtRows().out || []).map(r => [r.kind, r.none ? -1 : r.hops.length, r.id === undefined ? null : r.id])"

def start(b, html, w, errs, reqs, h=900, touch=False, keep=False):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch)
    def rt(r):
        reqs.append(r.request.method + ' ' + r.request.url)
        return r.abort() if not r.request.url.startswith('file:') else r.continue_()
    ctx.route('**/*', rt)
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + html)
    if not keep: pg.evaluate("localStorage.clear()"); pg.reload()
    pg.wait_for_timeout(300); pg.evaluate("switchTab('wh')"); pg.wait_for_timeout(200)
    return ctx, pg

def cases(b, html, parts=('rows', 'strip', 'hover', 'again', 'pin', 'from', 'esi', 'phone', 'same')):
    out, errs, reqs = [], [], []
    ctx, pg = start(b, html, 1440, errs, reqs); ev = pg.evaluate
    S = ev(SEED)
    if not all(S.values()): out.append(f'the seed: {S}')
    ev("(id) => whRtPin(id, true)", S['far']); ev(OPEN); pg.wait_for_timeout(120)
    if 'rows' in parts:
        if ev("[!document.querySelector('#whPnRt').hidden, document.querySelector('#whPnSum').hidden, document.querySelector('[data-wh-rp=\"rt\"]').getAttribute('aria-pressed'), JSON.parse(localStorage.getItem('tvWhPanels')).open]") != [True, True, 'true', 'rt']:
            out.append('the Routes button opens its panel (System shut), aria-pressed, kept as rt')
        r = ev(ROWS)
        if [x[0] for x in r] != ['hs', 'ls', 'pin'] or r[2][2] != S['far'] or r[0][1] != 2 or r[1][1] != 3: out.append(f'the rows: nearest highsec, nearest lowsec, then the pins: {r}')
        ev("(n) => { whS.mk[n] = {st: 'home'}; whMkSave(); whPaint(true); }", S['j3'])
        r = ev(ROWS)
        if [x[0] for x in r][:1] != ['home'] or r[0][1] != 1: out.append(f'Home first (1 jump to the C3): {r}')
        ev("(n) => { whRtPin(n, true); whPaint(true); }", S['jx'])
        r = ev(ROWS)
        if r[-1] != ['pin', -1, S['jx']] or 'no route' not in ev("document.querySelector('#whPnRt .wh-rt-list').textContent"): out.append(f'a pin with no route says so: {r[-1:]}')
        ev("(n) => { whRtPin(n, false); delete whS.mk[whS.last === n ? -1 : Object.keys(whS.mk)[0]]; }", S['jx'])
        # statuses never change a route (Q2 "Ignore statuses"): Dangerous on the C3 leaves every row as it was
        before = ev(ROWS); ev("(n) => { whS.mk[n] = {st: 'danger'}; whMkSave(); whPaint(true); }", S['j3']); after = ev(ROWS)
        if before != after: out.append(f'a Dangerous status changed the routes: {before} → {after}')
    if 'strip' in parts:
        st = ev("""() => { const r = whRtRows().out.find(x => x.kind === 'ls'), q = [...document.querySelectorAll('#whPnRt .wh-rt-strip')][whRtRows().out.indexOf(r)].children;
          return {n: r.hops.length, sq: q.length, round: [...q].map(e => getComputedStyle(e).borderRadius), j: [...q].map(e => e.classList.contains('j')), holes: r.holes,
            num: document.querySelectorAll('#whPnRt .wh-rt-n')[whRtRows().out.indexOf(r)].textContent, wh: getComputedStyle(document.documentElement).getPropertyValue('--it-wh').trim(), col: getComputedStyle(q[0]).backgroundColor}; }""")
        if st['sq'] != st['n'] or st['n'] != 3 or st['holes'] != 2 or st['num'] != str(st['n']): out.append(f'one square a jump, the two hole jumps counted: {st}')
        if st['round'][:2] != ['50%', '50%'] or st['round'][2] == '50%' or st['j'][:2] != [True, False]: out.append(f'holes round, gates square, J-space in the wormhole colour: {st}')
    if 'hover' in parts:
        ev("([k, j3]) => { const l = whLinkOf(k, j3); whEndSet(l, j3, 'ABC-123', 'K162'); whEndSave(); l.life = 'eol'; whSave(); whS.pn = {}; whPaint(true); }", [S['k'], S['j3']])
        sel = "#whPnRt .wh-rt-strip[data-wh-rt-row=\"1\"] .wh-rt-q"   # nearest lowsec: hole, hole, gate
        pg.hover(f'{sel}[data-wh-rt-q="1"]'); pg.wait_for_timeout(80)
        tip = ev("() => { const t = document.querySelector('#whPnRt [data-wh-rt-tip]'); return t.hidden ? null : t.textContent; }")
        names = ev("([a, b]) => [whName(a), whName(b)]", [S['j3'], S['k']])
        if not tip or not tip.startswith(f'{names[0]} → {names[1]} · ABC-123 (K162) · end of life · '): out.append(f'a hole\'s line with its recorded ID, type and life: {tip!r}')
        dim = ev(f"() => [...document.querySelectorAll('{sel}')].map(e => +getComputedStyle(e).opacity)")
        if dim[1] != 1 or any(x > 0.5 for i, x in enumerate(dim) if i != 1): out.append(f'the other squares dimmed: {dim}')
        if ev("() => !!whRtHovRow()") is not True: out.append('the route on the chain map while hovered')
        pg.hover(f'{sel}[data-wh-rt-q="0"]'); pg.wait_for_timeout(80)
        tip0 = ev("() => document.querySelector('#whPnRt [data-wh-rt-tip]').textContent")
        if 'ID not known' in tip0 or re.search(r'[A-Z]{3}-\d{3}', tip0) or not tip0.split(' · ')[0].endswith(' → ' + names[0]): out.append(f'a hole with no ID: system to system, no "ID not known": {tip0!r}')
        pg.hover(f'{sel}[data-wh-rt-q="2"]'); pg.wait_for_timeout(80)
        tip2 = ev("() => document.querySelector('#whPnRt [data-wh-rt-tip]').textContent")
        if '→' in tip2 or not tip2.split(' ')[0].replace('.', '').replace('-', '').isdigit(): out.append(f'a gate\'s line: security, name, region: {tip2!r}')
        pg.mouse.move(1200, 850); pg.wait_for_timeout(80)
        if ev("() => [!!whRtHovRow(), document.querySelector('#whPnRt [data-wh-rt-tip]').hidden]") != [False, True]: out.append('leaving the strip: no route on the map, the line hidden')
        pg.focus(f'{sel}[data-wh-rt-q="0"]'); pg.keyboard.press('ArrowRight'); pg.wait_for_timeout(60)
        if ev("() => [document.activeElement.dataset.whRtQ, !document.querySelector('#whPnRt [data-wh-rt-tip]').hidden]") != ['1', True]: out.append('the arrows step along the strip and show its line')
        pg.keyboard.press('Tab'); pg.wait_for_timeout(60)
    if 'again' in parts:
        ev("() => { window.__rtN = 0; const o = itRpSearch; itRpSearch = function(){ window.__rtN++; return o.apply(this, arguments); }; }")
        ev("() => { whS.pn = {}; whPaint(true); whS.pn = {}; whPaint(true); }")
        if ev("window.__rtN") != 0: out.append(f'an unchanged repaint worked the routes out again ({ev("window.__rtN")})')
        ev("(k) => whSeen(k, Date.now() - 60e3, false)", S['j3']); pg.wait_for_timeout(80)
        n1 = ev("window.__rtN")
        if n1 != 1: out.append(f'a jump: every row worked out again with one search ({n1})')
        r = ev(ROWS)
        if not r or r[0][0] != 'hs' or ev("whRtRows().from") != S['j3']: out.append(f'after the jump the rows start from the new system: {r}')
        ev("(k) => whSeen(k, Date.now() - 30e3, false)", S['k']); pg.wait_for_timeout(80)
        if any(x[0] == 'hs' for x in ev(ROWS)): out.append('out in highsec: no "nearest highsec" row')
        ev("(n) => whSeen(n, Date.now() - 10e3, false)", S['j2']); pg.wait_for_timeout(80)
    if 'pin' in parts:
        jn = ev("(n) => whName(n)", S['jx'])
        pg.fill('#whPnRt [data-wh-rt-pin] input', jn); pg.press('#whPnRt [data-wh-rt-pin] input', 'Enter'); pg.wait_for_timeout(100)
        if ev("whRtState().pins") != [S['far'], S['jx']]: out.append(f'pin by typing a J-name: {ev("whRtState().pins")}')
        pg.fill('#whPnRt [data-wh-rt-pin] input', 'NOT A SYSTEM'); pg.press('#whPnRt [data-wh-rt-pin] input', 'Enter'); pg.wait_for_timeout(100)
        if 'isn’t a system the page knows' not in ev("document.querySelector('#whPnRt .it-rp-msg').textContent"): out.append('an unknown name refused')
        pg.click(f'#whPnRt [data-wh-rt-rm="{S["jx"]}"]'); pg.wait_for_timeout(80)
        if ev("whRtState().pins") != [S['far']]: out.append('× unpins')
        ev("(n) => whMenuOpen(n, 40, 40)", S['j3']); pg.wait_for_timeout(80)
        if ev("document.querySelector('.wh-smenu [data-wh-m=\"pin\"]').textContent") != 'Pin route': out.append('the menu: Pin route')
        pg.click('.wh-smenu [data-wh-m="pin"]'); pg.wait_for_timeout(80)
        if ev("whRtState().pins") != [S['far'], S['j3']] or ev("whS.open") != 'rt': out.append('Pin route from the map\'s menu (Routes opens)')
        ev("(n) => whMenuOpen(n, 40, 40)", S['j3']); pg.wait_for_timeout(80)
        if ev("document.querySelector('.wh-smenu [data-wh-m=\"pin\"]').textContent") != 'Unpin route': out.append('the menu: Unpin route on a pinned one')
        pg.click('.wh-smenu [data-wh-m="pin"]'); pg.wait_for_timeout(80)
        pg.click('#whPnRt [data-wh-rt-short]'); pg.wait_for_timeout(80)
        pg.reload(); pg.wait_for_timeout(300); ev("switchTab('wh')"); pg.wait_for_timeout(200)
        if ev("[whRtState().pins, whRtState().short, whS.open, !document.querySelector('#whPnRt').hidden]") != [[S['far']], True, 'rt', True]: out.append(f'pins, Shortest and the open panel kept through a reload: {ev("[whRtState().pins, whRtState().short, whS.open]")}')
        if not ev("document.querySelector('#whPnRt [data-wh-rt-short]').checked"): out.append('Shortest shown on after the reload')
        pg.click('#whPnRt [data-wh-rt-short]'); pg.wait_for_timeout(80)
    if 'from' in parts:
        ev("(n) => whMenuOpen(n, 40, 40)", S['k']); pg.wait_for_timeout(80); pg.click('.wh-smenu [data-wh-m="route"]'); pg.wait_for_timeout(100)
        if ev("whRtRows().from") != S['k'] or not ev("!!document.querySelector('#whPnRt [data-wh-rt-me]')"): out.append('Routes from here: every row from that system, a "From where you are" button')
        if any(x[0] == 'hs' for x in ev(ROWS)): out.append('Routes from a highsec system: no "nearest highsec" row')
        pg.click('#whPnRt [data-wh-rt-me]'); pg.wait_for_timeout(80)
        if ev("whRtRows().from") != ev("whS.last") or ev("!!document.querySelector('#whPnRt [data-wh-rt-me]')"): out.append('From where you are: back to you')
    if 'esi' in parts:
        txt = ev("document.querySelector('#whPnRt').textContent")
        if 'destination' in txt.lower() or 'Send' in txt: out.append('no Set destination or Send in the panel')
        if any('autopilot' in u or '/route/' in u for u in reqs): out.append(f'nothing sent to EVE: {[u for u in reqs if "autopilot" in u or "/route/" in u][:2]}')
    ctx.close()
    if 'phone' in parts:
        ctx, pg = start(b, html, 390, errs, reqs, 844, True); ev = pg.evaluate
        S2 = ev(SEED); ev("(id) => whRtPin(id, true)", S2['far']); ev(OPEN); pg.wait_for_timeout(150)
        small = ev("() => [...document.querySelectorAll('#whPnRt button, #whPnRt input:not(.mys-sw), #whPnRt label.mys-use, #whPnRt .wh-rt-strip, .wh-rail button')].filter(e => e.offsetParent && e.getBoundingClientRect().height < 43.5).map(e => e.className || e.tagName).slice(0, 4)")
        if small: out.append(f'390 px: 44 px targets (the strip one target): {small}')
        if not ev("document.documentElement.scrollWidth <= innerWidth && document.querySelector('#whPnRt').scrollWidth <= document.querySelector('#whPnRt').clientWidth + 1"): out.append('390 px: sideways scroll')
        q = ev("() => { const s = document.querySelector('#whPnRt .wh-rt-strip'); const r = s.children[1].getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; }")
        pg.touchscreen.tap(q[0], q[1]); pg.wait_for_timeout(100)
        if ev("document.querySelector('#whPnRt [data-wh-rt-tip]').hidden"): out.append('390 px: a tap on the strip shows its line')
        ctx.close()
    if 'same' in parts:   # 047's route unchanged by the shared search: the older page's itRpUpdate against this one's, same homes, flags and preferences
        old = os.path.join(os.path.dirname(HTML), '.wh_old_062rt.html')
        try:
            open(old, 'w', encoding='utf-8').write(subprocess.check_output(['git', '-C', REPO, 'show', f'{OLD}:index.html']).decode('utf-8'))
            RUN = """() => { const M = itMapTable(), out = []; if(!itm.P) itm.P = new Float32Array(2);
              const fl = new Map([[17, ['camp']], [530, ['hostiles']], [1200, ['kills']], [4021, ['bubble']], [33, ['ESS']]]); itRpFlags = () => fl;
              for(const [home, pref, pen] of [[5, 'Shorter', 0], [17, 'Safer', 5], [100, 'Safer', 5], [2600, 'Safer', 10], [4100, 'LessSecure', 7], [5000, 'Safer', 1]]){
                Object.assign(itRpSet(), {pref, pen}); itm.home = home; itRp.key = ''; itRpUpdate(); let h = 0; for(let i = 0; i < itRp.par.length; i++) h = (Math.imul(h, 31) + itRp.par[i] + 7 * itRp.len[i] + 13 * itRp.f[i]) | 0; out.push(h); }
              return out; }"""
            res = []
            for f in (old, html):
                ctx, pg = start(b, f, 1440, errs, reqs)
                if f == old:   # tvWhPanels 'rt' on the older page: shut, no error
                    pg.evaluate("() => localStorage.setItem('tvWhPanels', JSON.stringify({v: 1, open: 'rt'}))"); pg.reload(); pg.wait_for_timeout(300); pg.evaluate("switchTab('wh')"); pg.wait_for_timeout(150)
                    if pg.evaluate("whS.open") != '': out.append('the older page should read tvWhPanels rt as shut')
                res.append(pg.evaluate(RUN)); ctx.close()
            if res[0] != res[1]: out.append(f'047\'s route changed by the shared search: {res}')
        finally:
            if os.path.exists(old): os.unlink(old)
    return out, errs

MUTANTS = [
    ('hole edges one way only', "put(a, b, l); put(b, a, l); }", "put(a, b, l); }", ('rows',)),
    ('the hole jumps not counted', "${escapeHtml(r.here ? 'here' : String(r.hops.length))}", "${escapeHtml(r.here ? 'here' : String(r.hops.length - r.holes))}", ('strip',)),
    ('worked out again on every repaint', "  if(key === R.key && R.res) return R.res;\n", "", ('again',)),
    ('an "ID not known" text', "const e = whEnd(h.l, h.a), id = e && e.sig ? ` · ${e.sig}${e.type ? ` (${e.type})` : ''}` : '', l = h.l;", "const e = whEnd(h.l, h.a), id = e && e.sig ? ` · ${e.sig}${e.type ? ` (${e.type})` : ''}` : ' · ID not known', l = h.l;", ('hover',)),
    ('a quick row for where you are', "const b = best(band); if(b !== src) out.push(", "const b = best(band); if(true) out.push(", ('from',)),
    ('Shortest not kept', "whPut(WH_RT_KEY, {v: 1, pins: R.pins, short: R.short});", "whPut(WH_RT_KEY, {v: 1, pins: R.pins});", ('pin',)),
    ('the shared search drifts (the destination counted)', "const fx = f[x] + (x !== src && flag(x) ? 1 : 0);", "const fx = f[x] + (flag(x) ? 1 : 0);", ('same',)),
    ('holes square', ".wh-rt-q.hole{border-radius:50%;}", ".wh-rt-q.hole{}", ('strip',)),
]

if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch()
        out, errs = cases(b, HTML)
        for o in out: check(False, o)
        check(not out, 'Routes: the rows, the strip, the hover, again on a jump, pins, Routes from here, nothing sent, phone, 047 unchanged')
        check(not errs, f'no page errors {errs[:3]}')
        for name, old, new, parts in MUTANTS:
            if PAGE.count(old) != 1: check(False, f'mutant "{name}": its line isn\'t in the page once'); continue
            with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f:
                f.write(PAGE.replace(old, new)); mp = f.name
            try:
                try: mo, me = cases(b, mp, parts)
                except Exception as e: mo, me = [f'the check stopped: {str(e).splitlines()[0]}'], []
                check(bool(mo) or bool(me), f'mutant "{name}" fails ({(mo or me or ["nothing"])[0][:90]})')
            finally: os.unlink(mp)
        b.close()
    print('FAILURES:', fails)
    sys.exit(1 if fails else 0)
