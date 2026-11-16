"""Intel for new users: an example of Intel at work (v2026.11.07.7, build queue 017; Project docs roadmap/intel-example-plan.md and
roadmap/intel-example-build-review.md; mockup Claude outputs/intel_example_mockup.html).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/intel_example_check.py [index.html]   -> 'FAILURES: N' (must be 0)

intel_check.py's stand-ins (its made-up Chatlogs folder, ESI and system names, the R2Z2 stand-in), then:
  * a new user (nothing saved): the example under the setup steps, before "Log Chat to File": the EXAMPLE tag, its title, the
    page's own rows from IT_EXAMPLE (7 Near You rows, the Feed's first 5), the map as a picture, the notes 1-5 and the foot line;
    each of the 5 markers on its target (within 4 px of the target's left edge, or the picture's corner) at 1440 and 390;
  * no leaks: drawing it asks nothing of anyone (only ship icons from images.evetech.net), writes nothing to localStorage, plays no
    sound, shows no notification, leaves Intel's state (its lists, filters, names, Standings) and the map's state as they were;
  * inert: Tab never lands inside it, a press on its kill badge or a pilot opens nothing; every chip's corporation and alliance has
    its emblem (an inline image, no empty logo box) and ticker;
  * 390 px (052): no sideways scroll, the map picture with Near You's list under it, note 3 as on a wide screen;
  * v2026.11.07.8: the switch is disabled (its hover says what's missing) until a folder is chosen and a channel ticked;
  * the bug found at 017's review (the owner: "why would we allow intel to be turned out if no intel channels have been linked and
    chosen?"): the folder chosen, no channel ticked, the switch: Intel stays off and says to choose the channels; on with a channel,
    unticking the last one stops it;
  * a quiet start (on, nothing reported yet): the empty lists on top and the example below them; the first real report: gone, and
    remembered (dscanItExGone) while the folder is linked; the window emptied: still gone; reloaded with the folder: gone; with no
    folder linked: shown again; "See an example" in the info panel: shown with the shared close button, which takes it away again;
  * a browser without the folder picker: the amber note above the steps (Chrome or Edge), the example still shown; Brave (a stand-in
    navigator.brave): the Brave line with brave://flags/#file-system-access-api as text (no link, no button), and INTEL-01 on the
    button press says the same; the picker there too (the flag on): no note.
  * build queue 055 (Project doc roadmap/intel-example-controls-plan.md; the owner: "should accurately reflect changes made to the functioning
    map"), at 1440, 760, 390 and 320 px: the drift guard (every control the live map's markup shows at rest, itMapMarkupHtml, and the rows
    under its box have a twin in the example's map); still copies (no id, no data-im/it/rs hook, nothing focusable, one #itRpSug at most,
    Security pressed); the picture as tall as the live map (itMapH) with you in the part its Near You list doesn't cover and past the filter
    column; the rail under the zoom row and clear of the search box, Near You level with the rail (wide), the column shut behind its button
    (phone); Near You's rows with height on a phone; marker 3 at the picture's bottom-left, clear of the search box and the column; no
    sideways scroll; with another stack saved (Region, Only Kills), the example's legend, column and picture still today's defaults and the
    store untouched (the 055 review's bug);
  * mutants, each must fail (see MUTANTS).
v2026.11.07.6 fails (no example, and the switch turns on with no channel). v2026.11.16.3 fails 055's cases (no controls in the example).
"""
import sys, os, re, json, time, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
_src = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
_src = _src[:_src.index('with sync_playwright() as p:')]
NS = {'__file__': os.path.join(HERE, 'intel_check.py'), '__name__': 'intel_check_prefix'}
exec(compile(_src, 'intel_check.py (first part)', 'exec'), NS)
globals().update({k: v for k, v in NS.items() if not k.startswith('__') and k not in ('check', 'fails')})
check = NS['check']
from playwright.sync_api import sync_playwright

REQ = []
SPY = r"""(() => { window.__ls = []; const s = Storage.prototype.setItem; Storage.prototype.setItem = function(k, v){ window.__ls.push(k); return s.call(this, k, v); }; })();"""
STATE = """() => JSON.stringify({feed: it.feed.length, near: it.near.size, fl: it.fl.length, q: it.q, names: !!it.names, set: JSON.stringify(it.set), me: JSON.stringify(it.me),
  side: JSON.stringify(side.rec), pins: [...itm.pinned].length, home: itm.home, draws: itm.draws, layouts: itm.layouts, cv: !!itm.cv && itm.cv.isConnected, ex: itExOrg})"""
MARKS = """() => { const f = document.querySelector('#intelPanel .itx'); if(!f) return null; const E = (s) => f.querySelector(s);
  const al = f.querySelectorAll('.itx-near .it-nb.alert'), T = {1: E('.itx-feed .it-fd.rep'), 2: E('.itx-near .it-nb'), 3: E('.itx-map img[src]'), 4: al[1] || al[0], 5: E('.itx-near .it-kl')};
  const phone = innerWidth < 600, F = f.getBoundingClientRect();
  return [1, 2, 3, 4, 5].map(n => { const m = f.querySelector(`[data-itx-mk="${n}"]`), r = m.getBoundingClientRect(), cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    if(m.hidden) return [n, 'hidden'];
    const inF = r.left >= F.left - 1 && r.right <= F.right + 1 && r.top >= F.top - 1 && r.bottom <= F.bottom + 1;
    // build queue 052: marker 3 on the map picture on a phone too (it was by Near You's heading while the phone's example had no map)
    const t = T[n]; if(!t) return [n, 'no target']; const b = t.getBoundingClientRect();
    // build queue 055 (D1): marker 3 at the picture's bottom-left corner (the search box has its top left)
    const ok = n === 5 ? Math.abs(cx - (b.right + 16)) <= 4 && Math.abs(cy - (b.top + 7)) <= 4 : n === 3 ? Math.abs(cx - b.left - 14) <= 4 && Math.abs(cy - (b.bottom - 14)) <= 4 : Math.abs(cx - b.left) <= 4 && cy >= b.top - 2 && cy <= b.bottom + 2;
    return [n, inF && ok]; }); }"""
INFO = """() => { const f = document.querySelector('#intelPanel .itx'); if(!f) return null; const p = f.parentElement;
  const setup = document.querySelector('#intelPanel .it-setup'), log = [...document.querySelectorAll('#intelPanel .it-sub')].find(x => /Log Chat to File/.test(x.textContent));
  return {tag: f.querySelector('.itx-tag').textContent, title: f.querySelector('.itx-t').textContent, ctx: (f.querySelector('.itx-h .ctx') || {}).textContent,
    near: f.querySelectorAll('.itx-near .it-nb').length, feed: f.querySelectorAll('.itx-feed .it-fd').length, img: (f.querySelector('.itx-map img') || {}).naturalWidth || 0,
    notes: [...f.querySelectorAll('.itx-notes li')].map(l => l.textContent.trim()), foot: f.querySelector('.itx-foot').textContent,
    afterSetup: !!setup && !!(setup.compareDocumentPosition(f) & 4), beforeLog: !!log && !!(f.compareDocumentPosition(log) & 4), inert: f.querySelector('.itx-body').inert,
    role: f.getAttribute('role'), label: f.getAttribute('aria-label'), close: !!f.querySelector('button.x-close'),
    logos: [...f.querySelectorAll('.it-seg.grp')].map(g => [!!g.querySelector('.it-lg img[src^="data:image/svg+xml"]'), (g.querySelector('.tk') || {}).textContent || '']),
    emptyLogo: f.querySelectorAll('.it-lg:not(:has(img))').length, tkFor: f.querySelectorAll('[data-tk-for]').length, sw: document.documentElement.scrollWidth}; }"""
NOTES = ['1A report from your intel channel: read as your scouts type it: who, what they fly, where.', '2How far, in jumps: Near You lists everything within reach, nearest first.',
         '3The map: reports and kills around you; hover one for its route to you.', '4Inside your alert range: a sound and a desktop notice if you turn them on, and an amber mark on your profile, from any tab.',
         '5Kills nearby: from zKillboard as they happen; press one to see the attacking fleet and its fits.']

# ---- build queue 055: the live map's controls in the example ----
PAGE = open(HTML, encoding='utf-8').read()
CTL = r"""() => { const f = document.querySelector('#intelPanel .itx'); if(!f) return null;
  const col = f.querySelector('.it-mapcol'), box = f.querySelector('.itx-map'), img = box.querySelector('img'), R = (e) => e ? e.getBoundingClientRect() : null;
  const shown = (e) => { const r = R(e); return !!r && r.width > 0 && r.height > 0 && getComputedStyle(e).visibility !== 'hidden'; };
  // the drift guard: the live map's markup as made (nothing drawn yet): the box's children shown at rest, and the rows under the box
  const d = document.createElement('div'); d.innerHTML = itMapMarkupHtml();
  const rest = (e) => !e.matches('canvas, [hidden], [aria-hidden="true"]'), cls = (e) => e.classList[0];
  const want = [...[...d.querySelector('.it-map-box').children].filter(rest).map(cls), ...[...d.children].filter(e => !e.matches('.it-map-box')).map(cls)];
  const miss = want.filter(c => !(c === 'it-map-leg' || c === 'it-map-row' ? col.querySelector(':scope > .' + c) : box.querySelector(':scope > .' + c)));
  const ctl = [...box.querySelectorAll(':scope > :not(img)'), ...col.querySelectorAll(':scope > .it-map-row')];
  const hooks = ctl.flatMap(e => [e, ...e.querySelectorAll('*')]).flatMap(e => [...e.attributes].map(a => a.name)).filter(n => /^data-(im|it|rs)(-|$)/.test(n));
  const foc = ctl.flatMap(e => [...e.querySelectorAll('button, input, select, textarea, a[href]')]).filter(e => e.tabIndex >= 0).length;
  const pressed = [...box.querySelectorAll('.it-map-fbtns button[aria-pressed="true"]')].map(b => b.getAttribute('aria-label'));
  const zoom = box.querySelector(':scope > .it-map-zoom'), rail = box.querySelector(':scope > .it-map-rail'), srch = box.querySelector(':scope > .it-rp-search');
  const ny = f.querySelector('.it-nearcol'), nr = R(ny), ir = R(img), zr = R(zoom), rr = R(rail), sr = R(srch);
  const m3 = R(f.querySelector('[data-itx-mk="3"]')), over = (e) => { const r = R(e); return !!r && r.width > 0 && shown(e) && m3.left < r.right && m3.right > r.left && m3.top < r.bottom && m3.bottom > r.top; };
  const fbr = R(box.querySelector('.it-map-fbtns')), phone = itExPhone(), you = itEx.mapYou || [-1, -1], fit = !!itEx.mapFit, reps = (itEx.mapRep || []).map(q => q[0]);
  const near = f.querySelector('.itx-near'), row1 = near && near.querySelector('.it-nb');
  const leg = col.querySelector(':scope > .it-map-leg'), rsv = col.querySelector('.it-map-row input');
  return {want, miss, ids: [...f.querySelectorAll('[id]')].map(e => e.id), hooks, foc, sug: document.querySelectorAll('#itRpSug').length, pressed,
    h: Math.round(img.naturalHeight / (window.devicePixelRatio || 1)), w: Math.round(ir.width), H: itMapH(Math.round(ir.width), phone), phone,
    you, fit, reps, nyL: phone ? null : Math.round(nr.left - ir.left), fbR: fbr && fbr.width > 0 ? Math.round(fbr.right - ir.left) : 0,
    railUnderZoom: !!(rr && zr) && rr.top >= zr.bottom - 1, railClear: !!(rr && sr) && (rr.top >= sr.bottom - 1 || rr.bottom <= sr.top + 1 || rr.left >= sr.right - 1), nyLevel: phone || !rr ? null : Math.round(nr.top - rr.top),
    colShown: shown(box.querySelector('.it-map-fbtns')), curShown: shown(box.querySelector('.it-map-fcur')),
    nearH: near ? Math.round(R(near).height) : 0, row1: row1 ? Math.round(R(row1).height) : 0,
    m3: [Math.round(m3.left + m3.width / 2 - ir.left), Math.round(ir.bottom - (m3.top + m3.height / 2))], m3over: [over(srch), over(box.querySelector('.it-map-fbtns')), over(box.querySelector('.it-map-fcur'))],
    leg: leg ? leg.innerText.split('\n')[0] : '', only: !!(leg && leg.querySelector('.it-map-only')), reach: rsv ? rsv.value : null, sw: document.documentElement.scrollWidth}; }"""

def controls(b, html, widths=(1440, 760, 390, 320), stack=True):
    out, errs = [], []
    def page(w, init=''):
        ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': 1000}); ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e)[:200])))
        if init: ctx.add_init_script(init)
        ctx.add_init_script(FS); route(ctx)
        pg = ctx.new_page(); pg.goto('file://' + html)
        pg.evaluate("(s) => { localStorage.clear(); localStorage.setItem('dscanSide', JSON.stringify(s)); }", SIDE); pg.reload(); pg.wait_for_timeout(500)
        pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.wait_for_timeout(1500)
        return ctx, pg
    for w in widths:
        ctx, pg = page(w); r = pg.evaluate(CTL)
        if r is None: out.append(f'{w}: no example'); ctx.close(); continue
        t = f'{w} px:'
        if r['miss'] or len(r['want']) < 6: out.append(f'{t} the drift guard: the live map shows {r["want"]} at rest; the example lacks {r["miss"]}')
        if r['ids'] or r['hooks'] or r['foc'] or r['sug'] > 1: out.append(f'{t} not still copies: ids {r["ids"][:4]}, hooks {r["hooks"][:4]}, {r["foc"]} focusable, {r["sug"]} #itRpSug')
        if r['pressed'] != ['Security status']: out.append(f'{t} pressed {r["pressed"]} (want Security only, today\'s defaults)')
        if r['reach'] != '10': out.append(f'{t} the "Map: within" copy shows {r["reach"]!r} (want the example\'s 10)')
        if r['h'] != r['H']: out.append(f'{t} the picture {r["h"]} px tall for {r["w"]} (the live map: {r["H"]})')
        x, y = r['you']
        if r['phone']:
            if not (0 < x < r['w'] and 0 < y < r['h']): out.append(f'{t} you at {r["you"]}, off the picture')
            if r['colShown'] or not r['curShown']: out.append(f'{t} the filter column not shut behind its button {r["colShown"], r["curShown"]}')
            if r['nearH'] < 100 or r['row1'] < 20: out.append(f'{t} Near You\'s rows have no height (list {r["nearH"]}, first row {r["row1"]})')
        else:
            if not (r['fbR'] < x < r['nyL'] and 0 < y < r['h']): out.append(f'{t} you at {r["you"]}, not between the filter column ({r["fbR"]}) and Near You ({r["nyL"]})')
            if not r['fit'] and abs(x - (r['nyL'] - 4) / 2) > 2: out.append(f'{t} you at x {x}, not centred in the part Near You doesn\'t cover (0 to {r["nyL"] - 4})')
            if not all(r['fbR'] < q < r['nyL'] for q in r['reps']): out.append(f'{t} a report under the filter column or Near You: x {r["reps"]} (free {r["fbR"]} to {r["nyL"]})')
            if r['nyLevel'] is None or abs(r['nyLevel']) > 1: out.append(f'{t} Near You {r["nyLevel"]} px off the rail\'s level')
            if not r['colShown'] or r['curShown']: out.append(f'{t} the filter column not open {r["colShown"], r["curShown"]}')
        if not r['railUnderZoom'] or not r['railClear']: out.append(f'{t} the rail under the zoom row {r["railUnderZoom"]}, clear of the search box {r["railClear"]}')
        if abs(r['m3'][0] - 14) > 4 or abs(r['m3'][1] - 14) > 4 or any(r['m3over']): out.append(f'{t} marker 3 at {r["m3"]} from the bottom-left (want 14, 14), over the search / column / button {r["m3over"]}')
        if r['sw'] > w: out.append(f'{t} sideways scroll ({r["sw"]})')
        ctx.close()
    if stack:   # the 055 review's bug: another stack saved; the example still today's defaults, the store untouched
        st = json.dumps({'v': 1, 'colour': 'region', 'view': 'map', 'only': {'secr': False, 'near': False, 'reports': False, 'kills': True, 'wh': False, 'sov': False},
                         'secr': {'lo': -5, 'hi': -3}, 'near': {'n': 5}, 'sovLv': [], 'seen': {'secr': False, 'near': False}})
        ctx, pg = page(1440, "try{ if(location.protocol === 'file:') localStorage.setItem('tvMapStack', %s); }catch(e){}" % json.dumps(st))
        r = pg.evaluate(CTL)
        pic = pg.evaluate("() => { itMapSt(); itEx.map = null; const a = itExMapPic(800); const keep = itm.st; itm.st = itMapStackBlank(); itEx.map = null; const p = itExMapPic(800); itm.st = keep;"
                          " return [a === p, keep.colour, localStorage.getItem('tvMapStack')]; }")
        if r is None or not r['leg'].startswith('Security') or r['only'] or r['pressed'] != ['Security status']:
            out.append(f'another stack saved (Region, Only Kills): the example\'s legend {r and r["leg"]!r}, its Only line {r and r["only"]}, pressed {r and r["pressed"]} (want Security, none, Security)')
        if not pic[0] or pic[1] != 'region': out.append(f'another stack saved: the example\'s picture differs from today\'s defaults {pic[0]} (the live stack {pic[1]})')
        if json.loads(pic[2] or '{}') != json.loads(st): out.append(f'the store changed: {pic[2]}')
        ctx.close()
    return out, errs

# each mutant's line is one line with no leading space: the served copy (tools/publish.py) drops comments and indentation
MUTANTS = [
    ('the search left out of the example (the drift guard)', "d.innerHTML = itMapZoomHtml() + itRpSearchHtml() + itMapFbarHtml();", "d.innerHTML = itMapZoomHtml() + itMapFbarHtml();", (1440,)),
    ('the slider row left out (the drift guard)', "<div class=\"it-map-leg\">${itExLegendHtml()}</div>${itExRowHtml()}</div></div>`", "<div class=\"it-map-leg\">${itExLegendHtml()}</div></div></div>`", (1440,)),
    ('the copies not made still', "function itExStill(html){", "function itExStill(html){ return String(html);", (1440,)),
    ('the picture at its old height', "dpr = window.devicePixelRatio || 1, h = itMapH(w, phone);", "dpr = window.devicePixelRatio || 1, h = Math.round(Math.max(380, Math.min(560, w * 0.72)));", (1440,)),
    ('centred on the whole width (Near You ignored)', "return {free: b >= 96 ? [0, b] : [0, w], fb: box};", "return {free: [0, w], fb: box};", (1440, 760)),
    ('the old rail place', ".it-top.itx-top .itx-map{position:relative;}\n", ".it-top.itx-top .itx-map{position:relative;} .it-top.itx-top .itx-map .it-map-rail{top:8px;}\n", (1440,)),
    ('the phone Near You list with no height (D3)', ".it-top.itx-top .it-nearcol > .itx-near{flex:none; overflow:visible;}", ".it-top.itx-top .it-nearcol > .itx-near{overflow:visible;}", (390,)),
    ('marker 3 at the top-left (on the search box)', "at(3, img, 14, img ? img.getBoundingClientRect().height - 14 : 0);", "at(3, img, 14, 14);", (1440,)),
    ('the user\'s stack in the example (the 055 review)', "itm.st = itMapStackBlank(); itm.mt = null;", "itm.mt = null;", ()),
]

with sync_playwright() as p:
    b = p.chromium.launch(); errs = []
    def new_ctx(w, init=''):
        ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': 1000}); ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e)[:200])))
        ctx.add_init_script(SPY)
        if init: ctx.add_init_script(init)
        ctx.add_init_script(FS); route(ctx)
        ctx.on('request', lambda r: REQ.append(r.url) if not r.url.startswith('file:') else None)
        return ctx
    def fresh(ctx):
        pg = ctx.new_page(); pg.goto('file://' + HTML)
        pg.evaluate("(s) => { localStorage.clear(); localStorage.setItem('dscanSide', JSON.stringify(s)); }", SIDE); pg.reload(); pg.wait_for_timeout(500)
        return pg

    # ---- a new user, 1440 ----
    ctx = new_ctx(1440); pg = fresh(ctx)
    pg.wait_for_timeout(1500)   # the page's own start-up writes (lookup counts, saved at most once a second) are done
    s0 = pg.evaluate(STATE); pg.evaluate("() => { window.__ls = []; }"); n0 = len(REQ)
    pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.wait_for_timeout(1500)
    I = pg.evaluate(INFO)
    check(I and I['tag'] == 'EXAMPLE' and I['title'] == 'What Intel looks like once it’s running' and I['ctx'] == 'made-up pilots on real systems' and I['afterSetup'] and I['beforeLog']
          and I['role'] == 'region' and I['label'] == 'Example: what Intel shows once it’s running' and not I['close'],
          f'a new user: the example under the setup steps, before "Log Chat to File", tagged EXAMPLE, its title and context, a region, no close button {I and {k: I[k] for k in ("tag", "title", "afterSetup", "beforeLog", "close")}}')
    check(I and I['near'] == 7 and I['feed'] == 5 and I['img'] > 100 and I['notes'] == NOTES and I['foot'] == 'Your own reports replace this example as soon as the first one arrives.',
          f'the page\'s own rows (7 Near You, the Feed\'s first 5), the map as a picture, the notes 1-5 and the foot line {I and (I["near"], I["feed"], I["img"], I["notes"][:1])}')
    M1 = pg.evaluate(MARKS)
    check(M1 and all(ok is True for _, ok in M1), f'1440: each marker on its target {M1}')
    check(I and I['logos'] and all(a and re.fullmatch(r'[\[<][A-Z]{3,5}[\]>]', t) for a, t in I['logos']) and I['emptyLogo'] == 0 and I['tkFor'] == 0,
          f'every corporation and alliance on a chip: its emblem (an inline image) and its ticker; no empty logo box, no ticker left to look up ({len(I["logos"]) if I else 0} groups)')
    asked = [u for u in REQ[n0:] if not re.match(r'https://images\.evetech\.net/types/\d+/icon', u)]
    s1 = pg.evaluate(STATE); ls = pg.evaluate("() => window.__ls"); snd = pg.evaluate("() => [__fs.beeps, __fs.notes.length]")
    check(not asked and s0 == s1 and not ls and snd == [0, 0] and pg.evaluate("() => document.querySelector('#profile').dataset.it || ''") in ('', 'off'),
          f'no leaks: nothing asked but ship icons {asked[:3]}, Intel\'s and the map\'s state unchanged {s0 == s1}, no storage write {ls}, no sound or notice {snd}')
    # inert: Tab never lands inside, a press does nothing
    inside = []
    for _ in range(60):
        pg.keyboard.press('Tab'); inside.append(pg.evaluate("() => !!(document.activeElement && document.activeElement.closest('.itx-body'))"))
    kb = pg.evaluate("() => { const r = document.querySelector('.itx .itx-near .it-kl').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }")
    pg.mouse.click(kb[0], kb[1]); pg.wait_for_timeout(400)
    pn = pg.evaluate("() => { const r = document.querySelector('.itx .itx-feed .it-seg.nmb').getBoundingClientRect(); return [r.left + 5, r.top + r.height / 2]; }")
    pg.mouse.click(pn[0], pn[1]); pg.wait_for_timeout(400)
    tab = pg.evaluate("() => [document.querySelector('.tab-btn.active').id, !document.querySelector('#tabBtnFleet') || document.querySelector('#tabBtnFleet').hidden || !document.querySelector('#tabBtnFleet').checkVisibility()]")
    check(not any(inside) and tab[0] == 'tabBtnIntel' and tab[1], f'inert: Tab never lands inside the example ({sum(inside)} of 60), a press on its kill badge or a pilot opens nothing {tab}')
    pg.close()

    # ---- the bug: no channel, no Intel ----
    # v2026.11.07.8 (the owner: "disable the on/off switch until a folder is chosen and at least one channel is checked")
    SW = "() => { const s = document.querySelector('#intelSw'), l = document.querySelector('#intelSwLabel'); return [it.on, s.checked, s.disabled, l.title, l.classList.contains('is-off')]; }"
    pg = fresh(ctx); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.wait_for_timeout(300)
    s0 = pg.evaluate(SW); pg.click('#intelSwLabel', force=True); pg.wait_for_timeout(400); s0b = pg.evaluate(SW)
    check(s0[:3] == [False, False, True] and 'Choose the Chatlogs folder' in s0[3] and s0[4] and s0b[:3] == [False, False, True],
          f'no folder: the switch is disabled (dimmed), its hover says what to do, a press does nothing {s0} {s0b[:3]}')
    setup_logs(pg); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(500)
    off = pg.evaluate(SW)
    check(off[:3] == [False, False, True] and 'Tick an intel channel' in off[3], f'the folder chosen, no channel ticked: still disabled, the hover says to tick a channel {off}')
    pg.evaluate("() => { it.on = false; itStart().then(() => itSwSync()); }"); pg.wait_for_timeout(400)
    g = pg.evaluate("() => [it.on, document.querySelector('#itNotes').textContent]")
    check(g[0] is False and 'Choose your intel channels first' in g[1], f'... and itStart itself still refuses with no channel {g}')
    pg.check('[data-it-chan="region.intel"]'); pg.check(f'[data-it-me="{MAIN}"]'); pg.wait_for_timeout(100)
    en = pg.evaluate(SW)
    check(en[:3] == [False, False, False] and en[3] == 'Intel is off' and not en[4], f'a channel ticked: the switch can be pressed {en}')
    pg.evaluate("() => { __fs.perm = 'denied'; }"); pg.click('#intelSwLabel'); pg.wait_for_timeout(800)
    dn = pg.evaluate(SW); pg.evaluate("() => { __fs.perm = 'granted'; }")
    check(dn[:2] == [False, False] and pg.inner_text('#intelSwLabel span').strip() == 'Off', f'pressed, the browser refuses the folder: Intel stays off and the box shows it (not left ticked) {dn}')
    pg.click('#intelSwLabel'); pg.wait_for_timeout(2500)
    on = pg.evaluate("() => it.on")
    pg.click('[data-it-act="gear"]'); pg.wait_for_timeout(300); pg.evaluate("() => document.querySelector('.it-pop [data-it-chan=\"region.intel\"]').click()"); pg.wait_for_timeout(500)   # a click: the box is redrawn away as it stops
    st = pg.evaluate("() => [it.on, document.querySelector('#itNotes').textContent, document.querySelector('#intelSw').disabled]")
    check(on is True and st[0] is False and 'no intel channel is ticked' in st[1] and st[2] is True, f'on with a channel, then the last one unticked: Intel stops and says why {on} {st}')
    pg.close()

    # ---- a quiet start, then the first real report ----
    pg = fresh(ctx); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()')
    W(pg, F_LOCAL_MAIN, header('Local', 'Your Main', NOW - 7200) + line(NOW - 4000, 'EVE System', 'Channel changed to Local : 1DQ1-A*'))
    W(pg, F_INTEL, header('region.intel', 'Your Main', NOW - 7000) + line(NOW - 6990, 'EVE System', 'Channel MOTD: hi'))
    pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(500)
    pg.check('[data-it-chan="region.intel"]'); pg.check(f'[data-it-me="{MAIN}"]'); pg.wait_for_timeout(100)
    pg.click('#intelSwLabel'); pg.wait_for_timeout(3000)
    q = pg.evaluate("() => { const f = document.querySelector('#intelPanel .itx'), l = document.querySelector('#itFeedList'); return [it.on, it.feed.length, !!f, !!f && !!l && !!(l.compareDocumentPosition(f) & 4), !!f && !!f.querySelector('button.x-close')]; }")
    check(q == [True, 0, True, True, False], f'a quiet start (on, nothing reported): the empty lists on top and the example below them, no close button {q}')
    # drawn again with Intel on (the example's alert-range rows would alert if they were live): no sound, notice or alert state; Standings back
    lk = pg.evaluate("""() => { const a = [__fs.beeps, __fs.notes.length, it.alerted.size, it.alerts || 0, JSON.stringify(side.rec)]; itEx.html = null; itEx.map = null; itRender(true);
      return [a, [__fs.beeps, __fs.notes.length, it.alerted.size, it.alerts || 0, JSON.stringify(side.rec)], (side.rec && side.rec.corp || {}).id]; }""")
    check(lk[0] == lk[1] and lk[2] == M.CORP, f'the example drawn again while Intel is on: no sound, notice or alert, your Standings as they were {lk[0][:4]} -> {lk[1][:4]}, Standings same {lk[0][4] == lk[1][4]}, yours {lk[2]}')
    pg.evaluate("() => { window.__ls = []; }")
    W(pg, F_INTEL, line(time.time() - 5, 'Kai Rhenn', 'T5ZI-S Seren Ketter sabre')); pg.wait_for_timeout(3500)
    g = pg.evaluate("() => [it.feed.length > 0, !!document.querySelector('#intelPanel .itx'), localStorage.getItem('dscanItExGone'), window.__ls.filter(k => k === 'dscanItExGone').length]")
    check(g == [True, False, '1', 1], f'the first real report: the example gone, remembered once (dscanItExGone) {g}')
    pg.evaluate("() => { it.feed = []; it.near = new Map(); itRender(true); }"); pg.wait_for_timeout(300)
    check(not pg.evaluate("() => !!document.querySelector('#intelPanel .itx')"), 'the window emptied later: it stays gone')
    # "See an example": shown with the close button; closed: gone
    pg.evaluate("() => { const d = document.querySelector('#intelPanel .it-head details.info-pop'); d.open = true; }")
    pg.evaluate("() => document.querySelector('#intelPanel .it-head [data-it-act=\"example\"]').click()"); pg.wait_for_timeout(800)
    v = pg.evaluate("() => { const f = document.querySelector('#intelPanel .itx'); return [!!f, !!f && !!f.querySelector('button.x-close'), !!document.querySelector('#intelPanel details.info-pop[open]'), document.activeElement && document.activeElement.matches('.itx button.x-close')]; }")
    pg.evaluate("() => document.querySelector('#intelPanel .itx button.x-close').click()"); pg.wait_for_timeout(500)
    v2 = pg.evaluate("() => !!document.querySelector('#intelPanel .itx')")
    check(v == [True, True, False, True] and v2 is False, f'"See an example" in the info panel: shown with the shared close button (focused), the panel closed; closed: gone {v} {v2}')
    # the stand-in folder can't be kept in IndexedDB as a real one is (a plain object): after the reload it is put back by hand, as the
    # page's start-up does with the kept handle
    pg.reload(); pg.wait_for_timeout(1500); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.wait_for_timeout(500)
    rl = pg.evaluate("() => { it.dir = {kind: 'directory', name: 'Chatlogs'}; itRender(true); return [!!it.dir, !!document.querySelector('#intelPanel .itx')]; }")
    check(rl == [True, False], f'reloaded with the folder still linked: still gone {rl}')
    pg.close()
    ctx.close()
    ctx = new_ctx(1440); pg = ctx.new_page(); pg.goto('file://' + HTML); pg.evaluate("() => { localStorage.clear(); localStorage.setItem('dscanItExGone', '1'); }"); pg.reload(); pg.wait_for_timeout(800)
    pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.wait_for_timeout(1200)
    check(pg.evaluate("() => [!!it.dir, !!document.querySelector('#intelPanel .itx')]") == [False, True], 'remembered as gone, but no folder linked (another browser, the folder unlinked): shown again')
    ctx.close()

    # ---- 390 px ----
    ctx = new_ctx(390); pg = fresh(ctx); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.wait_for_timeout(1500)
    I = pg.evaluate(INFO); M2 = pg.evaluate(MARKS)
    # build queue 052: the phone's example shows the map picture too (Near You's list under it), note 3 as on a wide screen
    vis = pg.evaluate("() => [getComputedStyle(document.querySelector('.itx .it-mapcol')).display, !!document.querySelector('.itx .itx-map img[src]'), (() => { const m = document.querySelector('.itx .itx-map').getBoundingClientRect(), n = document.querySelector('.itx .it-nearcol').getBoundingClientRect(); return n.top >= m.bottom - 1; })()]")
    check(I and I['sw'] <= 390 and vis == ['block', True, True] and I['notes'][2] == '3The map: reports and kills around you; hover one for its route to you.' and all(ok is True for _, ok in M2),
          f'390 px: no sideways scroll ({I and I["sw"]}), the map picture with Near You\'s list under it {vis}, note 3 as on a wide screen, each marker on its target {M2}')
    ctx.close()

    # ---- a browser without the folder picker; Brave ----
    NOTE = "() => { const n = document.querySelector('#intelPanel .it-nofs'), s = document.querySelector('#intelPanel .it-setup'); return n ? [n.textContent, !!(n.compareDocumentPosition(s) & 4), n.querySelectorAll('a, button').length, (n.querySelector('code') || {}).textContent || '', !!document.querySelector('#intelPanel .itx')] : [null, !!document.querySelector('#intelPanel .itx')]; }"
    ctx = new_ctx(1440, "window.__noFsApi = true;"); pg = fresh(ctx); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.wait_for_timeout(1000)
    n1 = pg.evaluate(NOTE)
    check(n1[0] and n1[0].startswith('Intel needs Chrome or Edge on a computer.') and n1[1] and n1[2] == 0 and n1[4], f'no folder picker (Firefox, Safari): the amber note above the steps, the example still shown {n1}')
    ctx.close()
    ctx = new_ctx(390, "window.__noFsApi = true; navigator.brave = {isBrave: () => Promise.resolve(true)};"); pg = fresh(ctx); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.wait_for_timeout(1000)
    n2 = pg.evaluate(NOTE); sw = pg.evaluate("() => document.documentElement.scrollWidth")
    pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(400)
    e1 = pg.evaluate("() => document.querySelector('#itNotes').textContent")
    check(n2[0] and n2[0].startswith('Brave turns off the folder picker Intel needs.') and n2[3] == 'brave://flags/#file-system-access-api' and n2[2] == 0 and n2[4] and sw <= 390
          and 'brave://flags/#file-system-access-api' in e1 and '(INTEL-01)' in e1,
          f'Brave without the picker: its own line, the flag\'s address as text (no link or button), no sideways scroll at 390 ({sw}); INTEL-01 says the same {n2[:1]} {e1[:80]}')
    ctx.close()
    ctx = new_ctx(1440, "navigator.brave = {isBrave: () => Promise.resolve(true)};"); pg = fresh(ctx); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.wait_for_timeout(1000)
    n3 = pg.evaluate(NOTE)
    check(n3[0] is None and n3[1], f'Brave with the flag on (the picker there): no note, the example shown {n3}')
    ctx.close()
    # ---- build queue 055 ----
    o5, e5 = controls(b, HTML)
    for o in o5: check(False, o)
    check(not o5, 'build queue 055: the live map\'s controls in the example (drift guard, still copies, height, centring, places, phone list, marker 3, no sideways scroll, the user\'s stack never shown) at 1440, 760, 390 and 320 px')
    errs += e5
    for name, old, new, ws in MUTANTS:
        if PAGE.count(old) != 1: check(False, f'mutant "{name}": its line isn\'t in the page once'); continue
        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f:
            f.write(PAGE.replace(old, new)); mp = f.name
        try:
            mo, me = controls(b, mp, ws, stack=not ws)
            check(bool(mo) or bool(me), f'mutant "{name}" fails ({(mo or me or ["nothing"])[0][:110]})')
        finally: os.unlink(mp)
    b.close()
check(not errs, f'no page errors {errs[:3]}')
print(f"FAILURES: {NS['fails']}")
sys.exit(1 if NS['fails'] else 0)
