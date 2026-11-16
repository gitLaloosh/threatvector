"""The Intel tab's layout (build queue 052, part 1 of the Project doc roadmap/intel-layout-sov-plan.md; mockup Claude outputs/
intel_layout_mockup.html; the owner's picks: layout A, filters "Down the left", the feed icon, "cyan tick, dark box"; at the build review:
"1. your choice is fine, 2. yes, 3. sure, 4. leave it shut").

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/intel_map_layout_check.py [index.html]   -> 'FAILURES: N' (must be 0)

Uses intel_check.py's made-up folder, mocks and names (you in 1DQ1-A, alert range 3); every pilot and line is made up. At 1440, 760 and
390 px, a fresh page each:
  * the map full width (the Feed below it), as tall as the plan says; no List | Map switch;
  * Near You shut by default: only its map button shows, the size of the zoom buttons, inside the map under them, its badge the number of
    Near You's rows, amber while one is in the alert range; pressed, the list opens inside the map beside the rail (a phone: under the filter
    column's button) with every filter (or the column's button), the rail and zoom still clickable; remembered (nearShown) across a reload;
    pressed again it shuts; a map press on a system leaves it shut;
  * the filter column at the map's left edge, under the search box, inside the map, clear of the zoom buttons and the rail; Paths to you
    last; (wide) Wormholes on shows its panel button right of the column, level with it, and off hovering shows none (058, the owner:
    "disabling a filter (like security range) should hide the settings button for it"); the name line right of the panel buttons,
    level with the filter that is on, clear of the rail; (phone) the column shut behind its button, opened it shuts Near You and Near You
    shuts it;
  * the Wormholes list: (1440) right of the panel buttons, inside the map, clear of Near You, the name line hidden; (760) no room beside
    Near You: opening it shuts Near You; (390) a sheet inside the map, Near You shut;
  * a list row's system name (a button, "Show on the map") centres that system in the part of the map the list doesn't cover, its tooltip
    open; the list stays open (wide) or shuts (phone); ⌖ with Near You open centres you in the part Near You doesn't cover (wide);
  * Paths to you re-fits when its tree grows (a new hostile), not after a zoom by hand;
  * checkboxes and radios drawn by the site (appearance none, the --bg fill, a checked one's border cyan), switches untouched;
  * no sideways scroll; no page errors.
Mutants, each must fail: the name button not wired; centring ignoring the panels; no turn-taking at 760; Paths to you's fit key without
the tree's size; Near You open by default.
"""
import sys, os, time, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
_src = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
_src = _src[:_src.index('with sync_playwright() as p:')]
NS = {'__file__': os.path.join(HERE, 'intel_check.py'), '__name__': 'intel_check_prefix'}
exec(compile(_src, 'intel_check.py (first part)', 'exec'), NS)
globals().update({k: v for k, v in NS.items() if not k.startswith('__') and k not in ('check', 'fails')})
from playwright.sync_api import sync_playwright
check = NS['check']
PAGE = open(HTML, encoding='utf-8').read()

HOME = SYSID['1DQ1-A']
D0 = bfs(HOME)
near = sorted((s for s, v in D0.items() if 1 <= v <= 3), key=lambda s: (D0[s], s))
HOST = M.PILOTS[M.pick(98000003, 0)][0]

def start(b, html, errs, w, seed=None):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': 1000 if w > 600 else 844}, has_touch=w < 600)
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); route(ctx)
    pg = ctx.new_page(); pg.goto('file://' + html)
    st = {'channels': ['region.intel'], 'me': 95000001, 'range': 3, 'forget': 15}
    st.update(seed or {})
    pg.evaluate("([s, i]) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify(i)); }", [SIDE, st])
    pg.reload(); pg.wait_for_timeout(400)
    setup_logs(pg); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg)
    return ctx, pg

def report(pg, n=4, t=None, start_at=0):
    t = t or time.time()
    W(pg, F_INTEL, ''.join(line(t + i, 'Gate Watcher', f'{SYSNAME[s]} {HOST} sabre') for i, s in enumerate(near[start_at:start_at + n])))
    tick(pg, 3200)

OV = "(a,b)=>!(a.right<=b.left||a.left>=b.right||a.bottom<=b.top||a.top>=b.bottom)"
R = "(e)=>e.getBoundingClientRect()"
HIT = "(e)=>{const q=e.getBoundingClientRect(), h=document.elementFromPoint(q.left+q.width/2, q.top+q.height/2); return !!h && (h===e || e.contains(h));}"
SHUT = "(getComputedStyle(document.getElementById('itNearCol')).display==='none')"

def case_wide(b, html, w, out, errs):
    ctx, pg = start(b, html, errs, w)
    report(pg, 5)
    pg.evaluate("itm.box.scrollIntoView({block:'start'})"); pg.wait_for_timeout(200)
    g = pg.evaluate(f"""(()=>{{ const R={R}, m=R(itm.box), c=R(document.querySelector('#intelPanel .it-card')), f=R(document.querySelector('#intelPanel .it-feedcol'));
      return {{full: m.width >= c.width - 60, h: Math.round(m.height), want: Math.round(Math.min(720, Math.max(520, itm.box.clientWidth * 0.5))) + 2, feedBelow: f.top >= m.bottom, nv: !!document.querySelector('[data-it-nv]')}}; }})()""")
    if not g['full'] or abs(g['h'] - g['want']) > 2 or not g['feedBelow'] or g['nv']: out.append(f'{w}: the map full width and {g["want"]} px tall, the Feed below, no List | Map: {g}')
    # Near You shut by default: only its button, the size of the zoom buttons, under them, inside the map; the badge counts the rows, amber with an alert row
    n = pg.evaluate(f"""(()=>{{ const R={R}, b=document.querySelector('[data-it-ny]'), z=R(document.querySelector('.it-map-zoom button')), zc=R(document.querySelector('.it-map-zoom')), r=R(b), m=R(itm.box), bd=b.querySelector('.it-ny-badge');
      const rows=document.querySelectorAll('#itNearList > .it-nb'), al=[...rows].some(x=>x.classList.contains('alert'));
      return {{shut: {SHUT}, size: Math.abs(r.width-z.width)<=2 && Math.abs(r.height-z.height)<=2, under: r.top>=zc.bottom && Math.abs(r.right-zc.right)<=2, inside: r.right<=m.right && r.top>=m.top,
        count: bd.textContent===String(rows.length) && rows.length>0, amber: bd.classList.contains('al')===al && al, pressed: b.getAttribute('aria-pressed')==='false'}}; }})()""")
    if not all(n.values()): out.append(f'{w}: Near You shut by default, its button the zoom buttons\' size under them, the badge = rows, amber: {n}')
    # a press on a system on the map leaves Near You shut (the owner: "leave it shut")
    pg.evaluate("(() => { const i = itGraphGet().at.get(%d); const r = itm.cv.getBoundingClientRect(); itm.cv.dispatchEvent(new MouseEvent('click', {bubbles: true, clientX: r.left + itm.Q[2*i], clientY: r.top + itm.Q[2*i+1]})); })()" % near[0])
    pg.wait_for_timeout(300)
    if not pg.evaluate(SHUT): out.append(f'{w}: a map press opened Near You (want it left shut)')
    # the filter column: left edge, under the search box, inside the map, clear of zoom and the rail; Paths to you last
    col = pg.evaluate(f"""(()=>{{ const R={R}, ov={OV}, f=R(document.querySelector('.it-map-fbtns')), m=R(itm.box), q=R(document.querySelector('.it-rp-search')), r=R(document.querySelector('.it-map-rail'));
      const z=[...document.querySelectorAll('.it-map-zoom button')].filter(e=>e.offsetParent).map(R), ks=[...document.querySelectorAll('.it-map-fbtns [data-im-f]')].map(e=>e.dataset.imF);
      return {{left: f.left-m.left<=12, under: f.top>=q.bottom, inMap: f.bottom<=m.bottom && f.top>=m.top, tall: f.height>f.width, clear: !ov(f,r) && z.every(x=>!ov(f,x)), last: ks[ks.length-1]==='paths'}}; }})()""")
    if not all(col.values()): out.append(f'{w}: the filter column at the left edge under the search box, clear of zoom and the rail, Paths to you last: {col}')
    pg.hover('[data-im-f="wh"]'); pg.wait_for_timeout(700)
    if pg.evaluate("getComputedStyle(document.querySelector('[data-it-whl]')).visibility === 'visible'"): out.append(f'{w}: hovering Wormholes while it is off shows its panel button (058: only while on)')
    pg.evaluate("itMapFilterSet('wh')"); pg.mouse.move(5, 5); pg.wait_for_timeout(700)
    pb = pg.evaluate(f"""(()=>{{ const R={R}, p=document.querySelector('[data-it-whl]'), pr=R(p), f=R(document.querySelector('[data-im-f="wh"]')), c=R(document.querySelector('.it-map-fbtns'));
      return {{shown: getComputedStyle(p).visibility==='visible', right: pr.left>=c.right, level: Math.abs(pr.top-f.top)<4}}; }})()""")
    if not all(pb.values()): out.append(f'{w}: Wormholes on shows its panel button right of the column, level with it: {pb}')
    pg.evaluate("itMapFilterSet('wh')"); pg.wait_for_timeout(300)
    pg.evaluate("document.querySelector('.it-map-fb').classList.add('named')"); pg.wait_for_timeout(350)
    nl = pg.evaluate(f"""(()=>{{ const R={R}, n=R(document.querySelector('.it-map-fn')), c=R(document.querySelector('.it-map-fbtns')), f=R([...document.querySelectorAll('.it-map-fbtns [data-im-f]')].find(x=>x.dataset.imF===(itMapSt().colour||'sec'))), r=R(document.querySelector('.it-map-rail'));
      return {{right: n.left>=c.right+32, level: Math.abs((n.top+n.bottom)/2-(f.top+f.bottom)/2)<3, clearRail: n.right<=r.left}}; }})()""")
    if not all(nl.values()): out.append(f'{w}: the name line right of the panel buttons, level with the filter that is on, clear of the rail: {nl}')
    # Near You open: inside the map beside the rail, every control clickable; remembered
    pg.click('[data-it-ny]'); pg.wait_for_timeout(400)
    o = pg.evaluate(f"""(()=>{{ const R={R}, hit={HIT}, c=R(document.getElementById('itNearCol')), r=R(document.querySelector('.it-map-rail')), m=R(itm.box);
      return {{open: !{SHUT}, inside: c.top>=m.top-1 && c.bottom<=m.bottom+1 && c.left>=m.left-1, beside: c.right<=r.left+1, saved: JSON.parse(localStorage.getItem('dscanIntel')).nearShown===true,
        click: [...document.querySelectorAll('.it-map-fbtns [data-im-f], [data-it-ny], .it-map-zoom button')].filter(e=>e.offsetParent).every(hit), rows: document.querySelectorAll('#itNearList > .it-nb').length > 0}}; }})()""")
    if not all(o.values()): out.append(f'{w}: Near You open inside the map beside the rail, every control clickable, saved: {o}')
    # ⌖ with Near You open: you in the part Near You doesn't cover
    pg.click('[data-im-z="me"]'); pg.wait_for_timeout(250)
    cx = pg.evaluate("(() => { const c = document.getElementById('itNearCol').getBoundingClientRect(), b = itm.box.getBoundingClientRect(); return [itm.Q[2*itm.home], (c.left - b.left - 4) / 2]; })()")
    if abs(cx[0] - cx[1]) > 3: out.append(f'{w}: ⌖ with Near You open puts you at x {cx[0]:.0f} (want {cx[1]:.0f}, the middle of the part it doesn\'t cover)')
    pg.reload(); pg.wait_for_timeout(400); setup_logs(pg); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.wait_for_timeout(300)
    if pg.evaluate("!it.on"):
        fb = pg.query_selector('[data-it-act="folder"]')
        if fb: fb.click(); pg.wait_for_timeout(300)
        pg.click('#intelSwLabel'); tick(pg)
    if pg.evaluate(SHUT): out.append(f'{w}: Near You open isn\'t remembered across a reload')
    # the Wormholes list
    pg.evaluate("itMapFilterSet('wh')"); pg.wait_for_timeout(200)
    W(pg, F_INTEL, line(time.time(), 'Scout Alt', f'{SYSNAME[near[8]]} wh')); tick(pg, 3200)
    pg.evaluate("document.querySelector('[data-it-whl]').click()"); pg.wait_for_timeout(500)
    if w >= 1200:
        p = pg.evaluate(f"""(()=>{{ const R={R}, ov={OV}, p=R(document.querySelector('.it-whp')), c=R(document.getElementById('itNearCol')), b=R(document.querySelector('[data-it-whl]')), m=R(itm.box);
          return {{nearOpen: !{SHUT}, clear: !ov(p,c), right: p.left>=b.right, inMap: p.left>=m.left && p.right<=m.right && p.top>=m.top && p.bottom<=m.bottom+1, nameHidden: getComputedStyle(document.querySelector('.it-map-fn')).visibility==='hidden'}}; }})()""")
        if not all(p.values()): out.append(f'{w}: the Wormholes list right of the panel buttons, inside the map, clear of Near You, the name hidden: {p}')
    else:
        if not pg.evaluate(SHUT) or not pg.evaluate("itWhListShown()"): out.append(f'{w}: no room beside Near You: opening the Wormholes list should shut Near You (the owner: "sure")')
        pg.click('[data-it-ny]'); pg.wait_for_timeout(300)
        if pg.evaluate("itWhListShown()") or pg.evaluate(SHUT): out.append(f'{w}: opening Near You with the list open and no room should shut the list')
        pg.evaluate("document.querySelector('[data-it-whl]').click()"); pg.wait_for_timeout(400)
    # a row's system name centres that system in the part the list doesn't cover, its tooltip open, the list still open
    pg.click('.it-whp [data-it-whgo]'); pg.wait_for_timeout(400)
    c = pg.evaluate(f"""(()=>{{ const id = Number(document.querySelector('.it-whp [data-it-whgo]').dataset.itWhgo), i = itGraphGet().at.get(id), [a, b] = itMapFree();
      return {{x: itm.Q[2*i], want: (a+b)/2, y: itm.Q[2*i+1], h: itm.H/2, tip: !itm.tip.hidden, list: itWhListShown(), title: document.querySelector('.it-whp [data-it-whgo]').title}}; }})()""")
    if abs(c['x'] - c['want']) > 3 or abs(c['y'] - c['h']) > 3 or not c['tip'] or not c['list'] or c['title'] != 'Show on the map' or c['want'] <= pg.evaluate("itm.W/2") + 20:
        out.append(f'{w}: a list name centres its system in the part the list doesn\'t cover, tooltip open, list open: {c}')
    # the site's checkboxes; switches untouched
    ck = pg.evaluate("""(()=>{const c=document.querySelector('.it-whp input[name=dr]'), sw=document.querySelector('#intelSw'), g=getComputedStyle(c); const t=document.createElement('i'); t.style.color='var(--bg)'; document.body.appendChild(t); const bg=getComputedStyle(t).color; t.remove();
      c.checked=true; const on=getComputedStyle(c).borderTopColor; c.checked=false; return {app: g.appearance==='none', bg: g.backgroundColor===bg, size: g.width==='16px', on: on!==getComputedStyle(c).borderTopColor, sw: getComputedStyle(sw).width==='36px'};})()""")
    if not all(ck.values()): out.append(f'{w}: checkboxes drawn by the site (dark box, cyan when checked), switches untouched: {ck}')
    sw = pg.evaluate('document.documentElement.scrollWidth - innerWidth')
    if sw > 0: out.append(f'{w}: sideways scroll {sw} px')
    ctx.close()

def case_phone(b, html, out, errs):
    w = 390
    ctx, pg = start(b, html, errs, w)
    report(pg, 5)
    pg.evaluate("itm.box.scrollIntoView({block:'start'})"); pg.wait_for_timeout(200)
    g = pg.evaluate(f"""(()=>{{ const R={R}, m=R(itm.box), b=R(document.querySelector('[data-it-ny]'));
      return {{h: Math.round(m.height), want: Math.round(Math.min(600, Math.max(440, itm.box.clientWidth * 1.45))) + 2, shut: {SHUT}, btn: b.width>=43, colShut: getComputedStyle(document.querySelector('.it-map-fbtns')).display==='none'}}; }})()""")
    if abs(g['h'] - g['want']) > 2 or not g['shut'] or not g['btn'] or not g['colShut']: out.append(f'390: the map {g["want"]} px tall, Near You and the filter column shut, 44 px buttons: {g}')
    pg.click('[data-it-ny]'); pg.wait_for_timeout(300)
    o = pg.evaluate(f"""(()=>{{ const R={R}, hit={HIT}, c=R(document.getElementById('itNearCol')), m=R(itm.box);
      return {{open: !{SHUT}, inside: c.left>=m.left && c.right<=m.right && c.bottom<=m.bottom+1, click: [document.querySelector('.it-map-fcur'), document.querySelector('[data-it-ny]'), ...document.querySelectorAll('.it-map-zoom button')].filter(e=>e.offsetParent).every(hit)}}; }})()""")
    if not all(o.values()): out.append(f'390: Near You open inside the map, the column\'s button, the rail and zoom clickable: {o}')
    pg.click('.it-map-fcur'); pg.wait_for_timeout(300)
    if not pg.evaluate(SHUT): out.append('390: opening the filter column should shut Near You')
    pg.click('[data-it-ny]'); pg.wait_for_timeout(300)
    if pg.evaluate("!!document.querySelector('.it-map-fb.open')"): out.append('390: opening Near You should shut the filter column')
    pg.evaluate("itMapFilterSet('wh')"); W(pg, F_INTEL, line(time.time(), 'Scout Alt', f'{SYSNAME[near[8]]} wh')); tick(pg, 3200)
    pg.click('.it-map-fcur'); pg.wait_for_timeout(300)
    pg.click('[data-it-whl]'); pg.wait_for_timeout(400)
    s = pg.evaluate(f"""(()=>{{ const R={R}, p=R(document.querySelector('.it-whp')), m=R(itm.box); return {{shown: itWhListShown(), inside: p.left>=m.left && p.right<=m.right && p.bottom<=m.bottom+1 && p.top>=m.top, near: {SHUT}}}; }})()""")
    if not all(s.values()): out.append(f'390: the Wormholes list a sheet inside the map, Near You shut: {s}')
    pg.click('.it-whp [data-it-whgo]'); pg.wait_for_timeout(400)
    c = pg.evaluate("""(()=>{ const id = Number(document.querySelector('.it-whp [data-it-whgo]').dataset.itWhgo), i = itGraphGet().at.get(id); return {x: itm.Q[2*i], w: itm.W/2, list: itWhListShown(), tip: !itm.tip.hidden}; })()""")
    if abs(c['x'] - c['w']) > 3 or c['list'] or not c['tip']: out.append(f'390: a list name shuts the list and centres its system, tooltip open: {c}')
    sw = pg.evaluate('document.documentElement.scrollWidth - innerWidth')
    if sw > 0: out.append(f'390: sideways scroll {sw} px')
    ctx.close()

def case_paths(b, html, out, errs):
    ctx, pg = start(b, html, errs, 1440)
    report(pg, 2)
    pg.evaluate("itMapFilterSet('paths')"); pg.wait_for_timeout(400)
    v0 = pg.evaluate("JSON.stringify(itPt.v) + '|' + itPt.G.cw + 'x' + itPt.G.ch")
    report(pg, 4, start_at=2); pg.evaluate("itMapRefresh(true)"); pg.wait_for_timeout(300)
    v1 = pg.evaluate("JSON.stringify(itPt.v) + '|' + itPt.G.cw + 'x' + itPt.G.ch")
    if v0.split('|')[1] == v1.split('|')[1]: out.append(f'Paths to you: the tree did not change size ({v0} -> {v1}); the check needs a bigger change')
    elif v0.split('|')[0] == v1.split('|')[0]: out.append(f'Paths to you: the tree grew ({v0.split("|")[1]} -> {v1.split("|")[1]}) and the view was not fitted again')
    pg.evaluate("itPtZoomAt(300, 200, 1.3)"); vh = pg.evaluate("JSON.stringify(itPt.v)")
    report(pg, 3, start_at=6); pg.evaluate("itMapRefresh(true)"); pg.wait_for_timeout(300)
    if pg.evaluate("JSON.stringify(itPt.v)") != vh: out.append('Paths to you: re-fitted after a zoom by hand (want the hand view kept)')
    ctx.close()

def cases(b, html, which=('1440', '760', '390', 'paths')):
    out, errs = [], []
    for w in ('1440', '760'):
        if w in which: case_wide(b, html, int(w), out, errs)
    if '390' in which: case_phone(b, html, out, errs)
    if 'paths' in which: case_paths(b, html, out, errs)
    return out, errs

MUTANTS = [
    ('the name button not wired', "if(go){ const id = Number(go.dataset.itWhgo); if(itMapPhone()) itWhListOpen(false, false); itRpPick(id); return true; }", "", ('1440',)),
    ('centring ignoring the panels', "  return b - a >= 96 ? [a, b] : [0, W];\n}", "  return [0, W];\n}", ('1440',)),
    ('no turn-taking at 760', "  return R - L >= min;\n}", "  return true;\n}", ('760',)),   # 053: the room asked for is the open panel's
    ('the fit key without the tree\'s size', "(tk !== itPt.treeKey && !itPt.hand)", "false", ('paths',)),
    ('Near You open by default', "      if(r.nearShown === true) d.nearShown = true;", "      d.nearShown = r.nearShown !== false;", ('1440',)),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, 'the Intel layout: the map, Near You, the filter column, the panels, centring, Paths to you')
    check(not errs, f'no page errors {errs[:3]}')
    for name, old, new, which in MUTANTS:
        if PAGE.count(old) != 1: check(False, f'mutant "{name}": its line isn\'t in the page once'); continue
        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f:
            f.write(PAGE.replace(old, new)); mp = f.name
        try:
            mo, me = cases(b, mp, which)
            check(bool(mo) or bool(me), f'mutant "{name}" fails ({(mo or me or ["nothing"])[0][:90]})')
        finally: os.unlink(mp)
    b.close()
print('FAILURES:', NS['fails'])
sys.exit(1 if NS['fails'] else 0)
