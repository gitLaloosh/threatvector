"""The Wormholes tab, part 3: each end of a connection has its own signature ID, and Connections in the System panel's list (build queue 059;
Project doc roadmap/wormholes-part3-plan.md P9-P12, P20, P22; the owner: "this is a real issue", "connections will have two IDs, one in each system
as the connection is represented by signature in each system.", "maybe some kind of connector on each end that shows the signature ID on hover?",
"could use a small version of the wormhole icon?", "can we treat connections similarly though?").

CCP's wormhole system names from the page's own table; IDs made up; no network. Checks:
  * per-end IDs (tvWhEnds): Edit selected in a system's Connections list sets that side's ID and type; the other side shows its own (or none), and
    the row's hover names the other side; + Add's ID lands on the "Linked to" system's end; an old single ID (tvWhChain's sig) shows on both sides
    as "side not known" until a side gets its own; matching a scanned ID by this side's own ID first;
  * the Connections list (P22): one row per connection, this side's ID and type, the EOL mark, colour by mass; sort by To kept in tvWhSecs.cn;
    Edit one (ID and type checked as + Add's, life / mass / size / Drifter) and several (life and mass only); no Copy; "→" sets the focus to the
    other system; Delete selected asks first, Cancel keeps it, Delete removes the connection and its ends;
  * the map: no ID written on the lines; a wormhole mark at each end that has an ID, outside its box; the hover names it; a press on it puts it
    in the message line; two marks too close share one (one line a side); an old single ID said once; none zoomed far out;
  * stored data safe both ways: cb9a995's page (056) saving its chain leaves tvWhEnds as it was; an end of a connection the older page deleted
    is dropped here;
  * a phone: the Age column hidden, "→" 44 px; no sideways scroll;
  * mutants; no page errors.
"""
import sys, os, re, tempfile, subprocess
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
HTML = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith('--')), os.path.join(REPO, 'index.html')))
PAGE = open(HTML, encoding='utf-8').read()
OLD = 'cb9a995'   # v2026.11.17.1 (056), the last main before part 3: never origin/main (LESSON #168)
fails = 0
def check(ok, msg):
    global fails
    print(('PASS ' if ok else 'FAIL ') + msg)
    if not ok: fails += 1

# a chain p0 - p1 - p2, p1 - p3 - p4: link 0 (p0-p1) gets an old single ID; the rest none
SEED = """() => { const T = whTable(), J = T.names.filter(n => /^J\\d{6}$/.test(n)), p = [40, 310, 655, 902, 1210].map(i => whIdOf(J[i]));
  const t0 = Date.now() - 3 * 3600e3; [p[0], p[1], p[2], p[1], p[3], p[4]].forEach((id, i) => whSeen(id, t0 + i * 60e3, false));
  const S = whState(), l0 = whLinkOf(p[0], p[1]); l0.sig = 'RZL-429'; l0.type = 'H296'; whSave(); S.drawKey = ''; return p; }"""
CN = "[...document.querySelectorAll('#whPnSum [data-wh-l=\"cn\"][data-wh-lr]')]"
ROW = lambda k: f'#whPnSum [data-wh-l="cn"][data-wh-lr="{k}"]'
E = "JSON.parse(localStorage.getItem('tvWhEnds') || 'null')"
# the camera on a link's middle at zoom s; returns what the end marks drew for it, and every text written on the canvas
VIEW = """([a, b, s]) => { const M = whS.M, pa = M.P.get(a), pb = M.P.get(b), r = whCv().getBoundingClientRect();
  M.cam = {x: (pa.x + pb.x + WH_NW) / 2 - r.width / 2 / s, y: (pa.y + pb.y + WH_NH) / 2 - r.height / 2 / s, s};
  const T = [], f = CanvasRenderingContext2D.prototype.fillText; CanvasRenderingContext2D.prototype.fillText = function(t, ...x){ T.push(String(t)); return f.call(this, t, ...x); };
  try{ whDraw(); } finally { CanvasRenderingContext2D.prototype.fillText = f; }
  const k = whLinkKey(a, b); return {texts: T, all: M.ends.length, ends: M.ends.filter(e => e.key === k).map(e => ({x: e.x, y: e.y, n: e.n, txt: e.txt, box: whHit(whToWorld(e.x, e.y))}))}; }"""

def start(b, html, w, errs, h=900, touch=False):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch)
    ctx.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + html); pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_timeout(300)
    pg.evaluate("switchTab('wh')"); pg.wait_for_timeout(200)
    return ctx, pg

def pick(pg, key, touch):
    sel = ROW(key) + ' .id'; pg.evaluate("(s) => document.querySelector(s).scrollIntoView({block: 'center'})", sel)
    (pg.tap if touch else pg.click)(sel); pg.wait_for_timeout(80)

def cases(b, html, parts=('ends', 'list', 'map', 'older')):
    out, errs = [], []
    for w, h, touch in ((1440, 900, False), (390, 844, True)):
        tag = f'{w}px'
        ctx, pg = start(b, html, w, errs, h, touch); ev = pg.evaluate
        p = ev(SEED); A, B, C, D = p[0], p[1], p[2], p[3]
        kAB, kBC, kBD = (ev("([a, b]) => whLinkKey(a, b)", [x, y]) for x, y in ((A, B), (B, C), (B, D)))
        ev("(n) => { whPnSet('sum'); whSelect(n); }", B); pg.wait_for_timeout(150)
        if 'ends' in parts or 'list' in parts:
            if ev(f"{CN}.length") != 3: out.append(f'{tag}: one row per connection: {ev(CN + ".length")}')
            t = ev(f"document.querySelector('{ROW(kAB)}').title")
            if ev(f"document.querySelector('{ROW(kAB)} .id').textContent") != 'RZL-429' or '(side not known)' not in t: out.append(f'{tag}: an old single ID shows as "side not known": {t!r}')
        if 'ends' in parts:
            pick(pg, kAB, touch); pg.click('#whPnSum [data-wh-la="edit"][data-wh-l="cn"]'); pg.wait_for_timeout(80)
            if not ev("['sig', 'type', 'life', 'mass', 'size', 'dr'].every(k => !!document.querySelector(`#whPnSum .wh-le [data-wh-le=\"${k}\"]`))"): out.append(f'{tag}: Edit one: this side\'s ID and type, life, mass, size, Drifter')
            pg.fill('#whPnSum .wh-le [data-wh-le="sig"]', 'XYZ-78'); pg.fill('#whPnSum .wh-le [data-wh-le="type"]', 'Q999'); pg.click('#whPnSum .wh-le [data-wh-la="save"]'); pg.wait_for_timeout(80)
            if 'isn’t a wormhole type' not in ev("document.querySelector('.wh-msg').textContent"): out.append(f'{tag}: an unknown type should be refused')
            pg.fill('#whPnSum .wh-le [data-wh-le="sig"]', 'xyz789'); pg.fill('#whPnSum .wh-le [data-wh-le="type"]', 'k162'); pg.click('#whPnSum .wh-le [data-wh-la="save"]'); pg.wait_for_timeout(80)
            e = (ev(E) or {}).get('links', {}).get(kAB, {})
            if e.get(str(B)) != {'sig': 'XYZ-789', 'type': 'K162'} or str(A) in e: out.append(f'{tag}: Edit sets this side\'s own ID only: {e}')
            if ev(f"document.querySelector('{ROW(kAB)} .id').textContent") != 'XYZ-789': out.append(f'{tag}: the row shows this side\'s own ID')
            ev("(n) => whSelect(n)", A); pg.wait_for_timeout(80)
            t = ev(f"document.querySelector('{ROW(kAB)}').title")
            if ev(f"document.querySelector('{ROW(kAB)} .id').textContent") != 'RZL-429' or 'other side XYZ-789 K162' not in t: out.append(f'{tag}: the other system still shows the old ID ("side not known") and names this side in its hover: {t!r}')
            pick(pg, kAB, touch); pg.click('#whPnSum [data-wh-la="edit"][data-wh-l="cn"]'); pg.wait_for_timeout(80)
            pg.fill('#whPnSum .wh-le [data-wh-le="sig"]', 'ABC-123'); pg.fill('#whPnSum .wh-le [data-wh-le="type"]', 'H296'); pg.click('#whPnSum .wh-le [data-wh-la="save"]'); pg.wait_for_timeout(80)
            t = ev(f"document.querySelector('{ROW(kAB)}').title")
            if ev(f"document.querySelector('{ROW(kAB)} .id').textContent") != 'ABC-123' or '(side not known)' in t: out.append(f'{tag}: each side shows its own once both have one: {t!r}')
            m = ev("([n, id]) => { const l = whLinkBySig(n, id); return l ? whLinkKey(l.a, l.b) : null; }", [B, 'XYZ-789'])
            if m != kAB: out.append(f'{tag}: a scanned ID matches this side\'s own ID: {m}')
            ev("(n) => whSelect(n)", B); pg.wait_for_timeout(80)
            ev("""([to, sys]) => { whPop('add'); const f = document.querySelector('.wh-addf'); f.sys.value = sys; f.link.value = String(to); f.sig.value = 'MNO-555'; f.ty.value = 'D845'; f.requestSubmit(); }""", [B, ev("(i) => whName(i)", p[4])])
            pg.wait_for_timeout(120)
            e = (ev(E) or {}).get('links', {}).get(ev("([a, b]) => whLinkKey(a, b)", [B, p[4]]), {})
            if e.get(str(B)) != {'sig': 'MNO-555', 'type': 'D845'} or str(p[4]) in e: out.append(f'{tag}: + Add\'s ID lands on the linked system\'s end: {e}')
            ev("(n) => { whPopClose(); whSelect(n); }", B); pg.wait_for_timeout(80)
        if 'list' in parts:
            ev("([a, b]) => { const l = whLinkOf(a, b); l.life = 'eol'; l.mass = 'reduced'; whSave(); whPnRedraw(); }", [B, C])
            if ev(f"document.querySelector('{ROW(kBC)} .wh-llf').textContent") != 'EOL' or 'cm1' not in ev(f"document.querySelector('{ROW(kBC)}').className"): out.append(f'{tag}: the EOL mark and the mass colour')
            if ev("!!document.querySelector('#whPnSum [data-wh-la=\"copy\"][data-wh-l=\"cn\"]')"): out.append(f'{tag}: connections have no Copy')
            pg.click('#whPnSum .wh-lt.cn [data-wh-ls="to"]'); pg.wait_for_timeout(80)
            names = ev(f"{CN}.map(r => r.querySelector('.wh-lnm').textContent)")
            if names != sorted(names) or ev("JSON.parse(localStorage.getItem('tvWhSecs')).cn.k") != 'to': out.append(f'{tag}: sort by To, kept: {names}')
            pg.click('#whPnSum [data-wh-lall="cn"]'); pg.wait_for_timeout(80); pg.click('#whPnSum [data-wh-la="edit"][data-wh-l="cn"]'); pg.wait_for_timeout(80)
            if not ev("!!document.querySelector('#whPnSum .wh-le [data-wh-le=\"life\"]') && !document.querySelector('#whPnSum .wh-le [data-wh-le=\"sig\"]')"): out.append(f'{tag}: Edit several: life and mass only')
            ev("document.querySelector('#whPnSum .wh-le [data-wh-le=\"life\"]').value = 'lt1h'"); pg.click('#whPnSum .wh-le [data-wh-la="save"]'); pg.wait_for_timeout(80)
            lv = ev("(n) => whLinksOf(n).map(l => l.life + '/' + l.mass)", B)
            if not all(x.startswith('lt1h/') for x in lv) or not any(x.endswith('/reduced') for x in lv): out.append(f'{tag}: several set to <1h at once, mass kept: {lv}')
            pg.click('#whPnSum [data-wh-lall="cn"]'); pg.wait_for_timeout(80)
            n0 = ev("whS.st.links.length"); pick(pg, kBD, touch)
            pg.click('#whPnSum [data-wh-la="del"][data-wh-l="cn"]'); pg.wait_for_timeout(80)
            if 'Delete 1 connection?' not in ev("document.querySelector('#whPnSum .wh-cnw .wh-lb').textContent") or ev("whS.st.links.length") != n0: out.append(f'{tag}: Delete selected connections asks first')
            pg.click('#whPnSum [data-wh-ask="cn-no"]'); pg.wait_for_timeout(80)
            if ev("whS.st.links.length") != n0: out.append(f'{tag}: Cancel keeps it')
            pg.click('#whPnSum [data-wh-la="del"][data-wh-l="cn"]'); pg.wait_for_timeout(80); pg.click('#whPnSum [data-wh-ask="cn-yes"]'); pg.wait_for_timeout(120)
            if ev("whS.st.links.length") != n0 - 1 or ev(f"!!document.querySelector('{ROW(kBD)}')"): out.append(f'{tag}: Delete removes the connection')
            pg.click(ROW(kBC) + ' .wh-lgo'); pg.wait_for_timeout(120)
            if ev("whFocus()") != C: out.append(f'{tag}: "→" goes to the other system')
            ev("(n) => whSelect(n)", B); pg.wait_for_timeout(80)
            if touch:
                g = ev(f"(() => {{ const r = document.querySelector('{ROW(kBC)}'); return [getComputedStyle(r.querySelector('.ag')).display, r.querySelector('.wh-lgo').getBoundingClientRect().width, r.getBoundingClientRect().height]; }})()")
                if g[0] != 'none' or g[1] < 43.5 or g[2] < 43.5: out.append(f'{tag}: a phone: Age hidden, "→" and the row 44 px: {g}')
        if 'map' in parts:
            ev("whPnSet('')"); pg.wait_for_timeout(80)
            ev("([a, b]) => { whEndSet(whLinkOf(a, b), a, 'QRS-111', 'N062'); whEndSet(whLinkOf(a, b), b, 'TUV-222', 'K162'); whEndSave(); }", [B, C])
            v = ev(VIEW, [B, C, 2.0])
            if any(re.search(r'[A-Z]{3}-\d{3}', t) for t in v['texts']): out.append(f'{tag}: an ID is written on the map: {[t for t in v["texts"] if re.search(r"[A-Z]{3}-", t)][:2]}')
            ends = v['ends']
            if len(ends) != 2 or {e['n'] for e in ends} != {B, C} or any(e['box'] is not None for e in ends): out.append(f'{tag}: a mark at each end, outside its box: {ends}')
            elif not any(e['txt'].startswith('QRS-111 N062 in ') for e in ends): out.append(f'{tag}: each mark names its own side: {[e["txt"] for e in ends]}')
            else:
                e0 = next(e for e in ends if e['n'] == B); r = ev("(() => { const r = whCv().getBoundingClientRect(); return [r.x, r.y]; })()")
                if not touch:
                    pg.mouse.move(r[0] + e0['x'] + 1, r[1] + e0['y']); pg.wait_for_timeout(80)
                    if ev("whCv().title") != e0['txt']: out.append(f'{tag}: hovering a mark should show its ID: {ev("whCv().title")!r}')
                    pg.mouse.move(r[0] + e0['x'] + 80, r[1] + e0['y'] + 80); pg.mouse.click(r[0] + e0['x'], r[1] + e0['y'])
                else: pg.touchscreen.tap(r[0] + e0['x'], r[1] + e0['y'])
                pg.wait_for_timeout(120)
                if 'QRS-111 N062' not in ev("document.querySelector('.wh-msg').textContent"): out.append(f'{tag}: a press on a mark puts its ID in the message line')
            v = ev(VIEW, [B, C, 0.6])
            if not (len(v['ends']) == 2 or (len(v['ends']) == 1 and v['ends'][0]['txt'].count('\n') == 1 and 'QRS-111' in v['ends'][0]['txt'] and 'TUV-222' in v['ends'][0]['txt'])): out.append(f'{tag}: two marks too close share one, a line a side: {v["ends"]}')
            v = ev(VIEW, [A, B, 2.0])
            if [e['txt'].count('ABC-123') + e['txt'].count('RZL-429') for e in v['ends']] and len(v['ends']) != 2: out.append(f'{tag}: a mark at both ends of A-B: {v["ends"]}')
            ev("([a, b]) => { const S = whS, k = whLinkKey(a, b); delete S.ends[k]; whEndSave(); }", [A, B])
            v = ev(VIEW, [A, B, 0.6])
            if v['ends'] and not (len(v['ends']) == 2 or (v['ends'][0]['txt'].count('RZL-429') == 1 and '(side not known)' in v['ends'][0]['txt'])): out.append(f'{tag}: an old single ID shared: said once: {v["ends"]}')
            if ev(VIEW, [B, C, 0.3])['all'] != 0: out.append(f'{tag}: no marks zoomed far out')
        if not ev("document.documentElement.scrollWidth <= innerWidth"): out.append(f'{tag}: sideways scroll')
        ctx.close()
    if 'older' in parts:
        old = os.path.join(os.path.dirname(HTML), '.wh_old_059e.html')
        try:
            open(old, 'w', encoding='utf-8').write(subprocess.check_output(['git', '-C', REPO, 'show', f'{OLD}:index.html']).decode('utf-8'))
            ctx, pg = start(b, html, 1440, errs); ev = pg.evaluate
            p = ev(SEED); A, B, C = p[0], p[1], p[2]
            ev("([a, b, c]) => { whEndSet(whLinkOf(a, b), b, 'XYZ-789', 'K162'); whEndSet(whLinkOf(b, c), b, 'QRS-111', ''); whEndSave(); }", [A, B, C])
            before = ev("localStorage.getItem('tvWhEnds')")
            pg.goto('file://' + old); pg.wait_for_timeout(400)
            pg.evaluate("(n) => { switchTab('wh'); whS.st.sys[n].notes = 'Mk note'; whSave(); }", B); pg.wait_for_timeout(150)
            if pg.evaluate("localStorage.getItem('tvWhEnds')") != before: out.append('the older page (056) should leave tvWhEnds as it was')
            if pg.evaluate("(n) => whLinksOf(n).length", B) != 3: out.append('the older page should still read the chain\'s connections')
            pg.evaluate("([b, c]) => { whS.st.links = whS.st.links.filter(l => whLinkKey(l.a, l.b) !== whLinkKey(b, c)); whSave(); }", [B, C])
            pg.goto('file://' + html); pg.wait_for_timeout(300)
            e = pg.evaluate("() => { switchTab('wh'); return Object.keys(whS.ends); }")
            if len(e) != 1: out.append(f'back here: the end of a connection the older page deleted should be dropped: {e}')
            ctx.close()
        finally:
            if os.path.exists(old): os.unlink(old)
    return out, errs

MUTANTS = [
    ('one ID shared by both ends', "function whEnd(l, n){ const e = whS.ends[whLinkKey(l.a, l.b)]; return e && e[n] ? e[n] : null; }",
     "function whEnd(l, n){ const e = whS.ends[whLinkKey(l.a, l.b)]; return e ? Object.values(e)[0] || null : null; }", ('ends',)),
    ('+ Add\'s ID on the new system\'s end', "if(sig || tc.type) whEndSet(l, to, sig, tc.type || '');", "if(sig || tc.type) whEndSet(l, id, sig, tc.type || '');", ('ends',)),
    ('a connection deleted without asking', "  if(a === 'del'){ if(!sel.size) return; P.ask = {k}; P.edit[k] = null;", "  if(a === 'del'){ if(!sel.size) return; P.ask = null; whAskAct(k + '-yes'); return;", ('list',)),
    ('Edit several changes the type too', "  if(P.edit.cn === '*'){ for(const l of ls){", "  if(P.edit.cn === '*'){ for(const l of ls){ l.mass = ''; ", ('list',)),
    ('the IDs written on the lines again', "    c.stroke(); c.setLineDash([]);   // 059: no text on the lines any more", "    c.stroke(); c.setLineDash([]); if(l.sig){ c.fillStyle = C.dim; c.fillText(l.sig, (a.x + b.x) / 2, (a.y + b.y) / 2); }", ('map',)),
    ('no mark for an old single ID', "function whSide(l, n){ const e = whEnd(l, n); return e && e.sig ? {sig: e.sig, type: e.type || '', own: true, gone: e.gone || 0} : l.sig ?",
     "function whSide(l, n){ const e = whEnd(l, n); return e && e.sig ? {sig: e.sig, type: e.type || '', own: true, gone: e.gone || 0} : false ?", ('ends',)),
    ('marks drawn zoomed far out', "if(!sw || s < WH_END_MIN_S) return;", "if(!sw) return;", ('map',)),
    ('ends of deleted connections kept', "    if(!keys.has(k) || !e || typeof e !== 'object') continue;", "    if(!e || typeof e !== 'object') continue;", ('older',)),
]

if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch()
        out, errs = cases(b, HTML)
        for o in out: check(False, o)
        check(not out, 'per-end IDs, the Connections list, the end marks on the map, stored data both ways')
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
