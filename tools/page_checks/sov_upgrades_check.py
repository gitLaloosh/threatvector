"""The Intel map's Sov upgrades filter (build queue 053, part 2 of the Project doc roadmap/intel-layout-sov-plan.md; mockup Claude outputs/
intel_layout_mockup.html).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/sov_upgrades_check.py [index.html]   -> 'FAILURES: N' (must be 0)

The owner: "i've got a list of sov upgrades that i'd like to be able to apply to the map like filters but i'd like to be able to pick and
choose which ones"; "Paste now, ESI later"; "Kind, level shown"; "Until replaced"; "Bright / dim"; "More kinds later"; "each list on it's
own so it can be replaced or edited separately"; at the build review "Yes, one shared path", "420 px, one column below", "Bright
anywhere", "INTEL-11 when storage is full", "Load names before checking". Uses intel_check.py's made-up folder, mocks and names (you in
1DQ1-A). **Every list here is made up** (systems of the mock map with upgrades picked by this check; never anyone's real lists). Checks:
  * the table: INTEL_SOV from CCP's data (44 published upgrades in the four groups), kinds and levels read from the names;
  * the store: a bad tvSov reads as empty; lists of the wrong form or an unknown kind dropped; a list kept across a reload;
    dscanIntel keeps its form;
  * the filter: before Paths to you, with its panel button beside it; chosen with no lists, its panel opens at the paste box;
  * pasting: "System <- Upgrade, Upgrade" lines ✓, ⚠ naming what isn't an upgrade, ✗ an unknown system or no "<-", a system twice
    "also on line N"; names alone take a kind (Cyno beacons by default); Add saves it and picks its kinds;
  * the picks: grouped, one checkbox per kind with its count and the levels in the hover; unpicking dims those systems;
  * the map: picked systems bright, the rest dimmed, your system never; a picked one past "Map: within" bright (the pixel); the hover
    names the upgrades with levels; the legend's line; the map's key follows the picks;
  * the lists: Edit / Save, Replace, Remove with Undo (gone after 6 s), each list on its own;
  * a full storage: INTEL-11 in the panel, the list kept for the visit;
  * the names: loaded before a paste is checked; INTEL-03 when ESI can't give them;
  * one filter panel at a time (the Wormholes list and Sov upgrades); placement right of the panel buttons, inside the map, clear of
    Near You at 1440 px; at 760 px the two take turns (under SOV_PANEL_MIN); 390 px a sheet that shuts Near You, 44 px targets, no
    sideways scroll;
  * nothing about the lists sent anywhere (no upgrade word asked of ESI);
  * mutants, each must fail: no level read; the dimming ignoring the picks; picked ones faint past the reach; two panels open at once;
    a full storage not said; a paste checked without names.
v2026.11.15.3 fails (no Sov upgrades filter).
"""
import sys, os, re, json, time, tempfile
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
D0 = bfs(HOME)
near = sorted((s for s, v in D0.items() if 1 <= v <= 4), key=lambda s: (D0[s], s))
A, B, C, X = near[0], near[1], near[2], near[3]
FAR = max((s for s, v in D0.items() if v <= 60), key=lambda s: D0[s])   # far past the map's reach
N = lambda s: SYSNAME[s]
UPG = '\n'.join([f'{N(A)} <- Major Threat Detection Array 3, Cynosural Navigation', f'{N(B)}  <-  minor threat detection array 2,   Exploration Detector 1',
                 f'{N(C)} <- Major Threat Detection Array 2, Gold Plated Toilet', 'Nowhere Special <- Major Threat Detection Array 1', f'{N(X)} Major Threat Detection Array 1',
                 f'{N(A)} <- Tritanium Prospecting Array 3', f'{N(FAR)} <- Major Threat Detection Array 1'])
BARE = f'{N(X)}\n{N(C)}\n'
EXPECT_SOV = 44
SOV_MIN = 420   # SOV_PANEL_MIN (the owner at the review: "420 px, one column below")

def start(b, html, w, errs, h=1000, touch=False, store=None, ny=False):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch, device_scale_factor=2 if touch else 1)
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); route(ctx)
    pg = ctx.new_page(); pg.goto('file://' + html)
    pg.evaluate("([s, v, ny]) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({nearShown: ny, channels: ['region.intel'], me: 95000001, range: 3, sound: false, notify: false, forget: 15, hideFriendly: true}));"
                " if(v !== null) localStorage.setItem('tvSov', typeof v === 'string' ? v : JSON.stringify(v)); }", [SIDE, store, ny])
    pg.reload(); pg.wait_for_timeout(400)
    setup_logs(pg); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg, 3200)
    pg.evaluate("() => document.querySelector('#intelPanel .it-map-box').scrollIntoView({block: 'center'})"); pg.wait_for_timeout(200)
    return ctx, pg

STORE = "() => { try{ return JSON.parse(localStorage.getItem('tvSov')); }catch(e){ return 'bad'; } }"
PX = """([id, k]) => { const i = itGraphGet().at.get(id); itm.view = {k, tx: itMapFreeX() - itm.P[2 * i] * k, ty: itm.H / 2 - itm.P[2 * i + 1] * k}; itMapDraw();
  const c = itm.cv.getContext('2d'), d = window.devicePixelRatio || 1, r = itm.stage ? Math.max(9, Math.min(15, itMapGatePx() * 0.2)) : 0;
  return [[...c.getImageData(Math.round(itm.Q[2 * i] * d), Math.round((itm.Q[2 * i + 1] + 0.72 * r) * d), 1, 1).data], itMapFcol(i)]; }"""
def near_col(px, hexc, tol=40): return max(abs(px[q] - int(hexc[1 + 2 * q:3 + 2 * q], 16)) for q in range(3)) <= tol

def paste(pg, text, kind=None):
    pg.fill('#itSovPaste textarea', text); pg.wait_for_timeout(150)
    if kind: pg.select_option('[data-sov-kind]', kind); pg.wait_for_timeout(100)

def cases(b, html, parts=('table', 'store', 'filter', 'paste', 'map', 'lists', 'full', 'names', 'one', 'phone', 'nosend')):
    out, errs = [], []
    IDS_ASKED.clear()
    ctx, pg = start(b, html, 1440, errs, store='{not json')
    if not pg.evaluate("typeof sovStore === 'function' && IT_MAP_FILTERS.some(f => f.k === 'sov')"):
        out.append('no Sov upgrades filter on the page'); ctx.close(); return out, errs
    if 'table' in parts:
        T = pg.evaluate("""() => ({n: INTEL_SOV.length, ids: INTEL_SOV.filter(r => [81615, 81619, 81621].includes(r[0])).map(r => r.slice(1)),
          mtd: INTEL_SOV.filter(r => r[2] === 'Major Threat Detection Array').map(r => r[3]).sort(), kinds: sovTable().kinds.length, bare: sovBareKinds()})""")
        if T['n'] != EXPECT_SOV: out.append(f"INTEL_SOV has {T['n']} rows (want {EXPECT_SOV}, CCP's published upgrades)")
        if sorted(map(tuple, T['ids'])) != [('Advanced Logistics Network', 'Advanced Logistics Network', None), ('Cynosural Navigation', 'Cynosural Navigation', None), ('Cynosural Suppression', 'Cynosural Suppression', None)]:
            out.append(f"the navigation upgrades: {T['ids']}")
        if T['mtd'] != [1, 2, 3]: out.append(f"Major Threat Detection Array's levels {T['mtd']} (want 1, 2, 3)")
        if 'Advanced Logistics Network' in T['bare'] or 'Cynosural Navigation' not in T['bare'] or 'Major Threat Detection Array' in T['bare']: out.append(f"kinds a names-only list can be: {T['bare']}")
    if 'store' in parts:
        st = pg.evaluate("() => sovStore()")
        if st != {'v': 1, 'lists': [], 'pick': []}: out.append(f'a bad tvSov read as {str(st)[:120]} (want empty)')
        R = pg.evaluate("""(t) => { localStorage.setItem('tvSov', JSON.stringify({v: 1, pick: ['Cynosural Navigation', 'Nope'], lists: [{id: 'a', kind: '', text: t, at: 1}, {id: 'b', kind: 'Major Threat Detection Array', text: 'x', at: 1},
          {id: 'c', kind: 'Advanced Logistics Network', text: 'x', at: 1}, {id: 'a', kind: '', text: 'dup id', at: 1}, {id: 'd', text: 5, at: 1}, {id: 'e', kind: 'Cynosural Suppression', text: 'y', at: 2}]}));
          const r = sovRead(); return [r.lists.map(l => l.id), r.pick]; }""", UPG)
        if R != [['a', 'e'], ['Cynosural Navigation']]: out.append(f'tvSov read back: lists {R[0]}, picks {R[1]} (want a and e; the kinds with a level, the jump bridge, a repeated id and a non-text dropped; Cynosural Navigation kept)')
        pg.evaluate("() => localStorage.removeItem('tvSov')")
    if 'filter' in parts:
        F = pg.evaluate("""() => { const ks = IT_MAP_FILTERS.map(f => f.k), b = document.querySelector('[data-im-f="sov"]'), pb = document.querySelector('[data-it-sovl]');
          return [ks.indexOf('sov') === ks.indexOf('paths') - 1, !!b, !!pb && pb.parentElement === b.parentElement && b.parentElement.classList.contains('it-map-fw')]; }""")
        if F != [True, True, True]: out.append(f'the filter: before Paths to you {F[0]}, its button {F[1]}, its panel button beside it {F[2]}')
        pg.click('[data-im-f="sov"]'); pg.wait_for_timeout(400)
        P = pg.evaluate("() => { const p = document.querySelector('.it-sovp'); return p && [p.hidden, p.getAttribute('role'), !!p.querySelector('button.x-close'), !document.querySelector('#itSovPaste').hidden, document.activeElement && document.activeElement.matches('#itSovPaste textarea'), document.querySelector('[data-it-sovl]').getAttribute('aria-expanded')]; }")
        if P != [False, 'dialog', True, True, True, 'true']: out.append(f'no lists, the filter chosen: the panel {P} (want open, a dialog with the shared close button, at the paste box with the focus in it)')
    if 'paste' in parts:
        pg.evaluate("() => { itMapFilterSet('sov'); if(!sovShown()) sovOpen(true, false, 'paste'); }"); pg.wait_for_timeout(200)
        paste(pg, UPG)
        C1 = pg.evaluate("""() => ({sum: (document.querySelector('.it-sov-chk .it-sov-sum') || {}).textContent, kind: document.querySelector('.it-sov-kind').hidden,
          rows: [...document.querySelectorAll('.it-sov-chk .it-sov-r')].map(r => [r.classList[1], r.classList.contains('dup'), (r.querySelector('.ln') || {}).textContent, (r.querySelector('.d') || {}).textContent || ''])})""")
        want = [['ok', False, 'line 1', ''], ['ok', False, 'line 2', ''], ['warn', False, 'line 3', "not an upgrade's name: Gold Plated Toilet"], ['bad', False, 'line 4', 'Nowhere Special: not a system on the map'],
                ['bad', False, 'line 5', 'no upgrades on this line'], ['ok', True, 'line 6', 'also on line 1'], ['ok', False, 'line 7', '']]
        if C1['rows'] != want: out.append(f"the checked lines: {C1['rows']}")
        if C1['sum'] != '4 ✓ · 1 ⚠ · 2 ✗ · 4 systems' or not C1['kind']: out.append(f"the summary {C1['sum']!r}, the kind select hidden {C1['kind']} (want 4 ✓ · 1 ⚠ · 2 ✗ · 4 systems, hidden: these are upgrade lines)")
        pg.click('[data-sov-add]'); pg.wait_for_timeout(300)
        st = pg.evaluate(STORE) or {}
        L = st.get('lists', [])
        if len(L) != 1 or L[0].get('kind') != '' or L[0].get('text') != UPG: out.append(f'Add: the store {str(st)[:160]}')
        if sorted(st.get('pick', [])) != sorted(['Major Threat Detection Array', 'Minor Threat Detection Array', 'Cynosural Navigation', 'Exploration Detector', 'Tritanium Prospecting Array']): out.append(f"a new list's kinds not picked: {st.get('pick')}")
        pg.click('[data-sov-tog="paste"]'); pg.wait_for_timeout(150)   # Add shut the box
        paste(pg, BARE)
        K = pg.evaluate("() => [document.querySelector('.it-sov-kind').hidden, document.querySelector('[data-sov-kind]').value, [...document.querySelectorAll('[data-sov-kind] option')].map(o => o.value)]")
        if K[0] or K[1] != 'Cynosural Navigation' or 'Advanced Logistics Network' in K[2] or 'Major Threat Detection Array' in K[2]: out.append(f'names alone: the kind select {K} (want shown, Cyno beacons by default, no jump bridge or levelled kinds)')
        paste(pg, BARE, 'Cynosural Suppression'); pg.click('[data-sov-add]'); pg.wait_for_timeout(300)
        st = pg.evaluate(STORE) or {}
        if [l.get('kind') for l in st.get('lists', [])] != ['', 'Cynosural Suppression'] or 'Cynosural Suppression' not in st.get('pick', []): out.append(f"the names-only list: {[l.get('kind') for l in st.get('lists', [])]}, picks {st.get('pick')}")
        G = pg.evaluate("""() => ({lists: document.querySelector('[data-sov-tog="lists"]').textContent.trim(), rows: [...document.querySelectorAll('.it-sov-l .it-sov-ln')].map(x => x.textContent.replace(/\\s+/g, ' ').trim()),
          groups: [...document.querySelectorAll('.it-sov-g')].map(g => [g.querySelector('b').textContent, [...g.querySelectorAll('.it-sov-k')].map(k => k.querySelector('span').textContent + ' ' + k.querySelector('.it-sov-n').textContent)]),
          tip: (document.querySelector('[data-sov-pick="Major Threat Detection Array"]') || {closest(){ return {title: ''}; }}).closest('label').title})""")
        if G['lists'] != 'Lists (2)' or G['rows'] != ['Upgrades · 4 systems · pasted today', 'Cyno jammers · 2 systems · pasted today']: out.append(f"the lists: {G['lists']!r}, {G['rows']}")
        gs = dict((g, k) for g, k in G['groups'])
        if gs.get('Ratting') != ['Major Threat Detection Array 3', 'Minor Threat Detection Array 1'] or gs.get('Navigation') != ['Cyno beacon 1', 'Cyno jammer 2'] or gs.get('Mining') != ['Tritanium Prospecting Array 1']:
            out.append(f"the picks: {G['groups']}")
        if 'Levels: 3 in 1 system, 2 in 1 system, 1 in 1 system' not in G['tip']: out.append(f"Major Threat Detection Array's hover: {G['tip']!r}")
    if 'map' in parts:
        M_ = pg.evaluate("""([ids, home]) => { const g = itGraphGet(); itMapFilterSet('sov'); itMapDraw(); const dim = ids.map(id => itMapDimmed(g.at.get(id)));
          const leg = document.querySelector('.it-map-fl'), legT = leg.textContent, legTitle = leg.title;
          itMapTip(g.at.get(ids[0]), 50, 50); const tip = itm.tip.textContent; itMapTip(-1);
          const k0 = itMapKey(); const st = sovStore(); st.pick = st.pick.filter(k => k !== 'Major Threat Detection Array'); sovSave(); sovChanged(); const k1 = itMapKey();
          const dim2 = ids.map(id => itMapDimmed(g.at.get(id))), homeDim = itMapDimmed(g.at.get(home));
          const d0 = itm.draws; itMapRefresh(); const d1 = itm.draws;
          return {dim, legT, legTitle, tip, keyMoved: k0 !== k1, dim2, homeDim, redraw: d1 - d0}; }""", [[A, B, C, X, FAR, near[5]], HOME])
        if M_['dim'] != [False, False, False, False, False, True]: out.append(f"Sov upgrades: dimmed {M_['dim']} (want the listed systems bright, an unlisted one dimmed)")
        if not M_['legT'].startswith('Sov upgrades bright: ') or 'hover a system for its upgrades' not in M_['legT'] or 'Picked:' not in M_['legTitle']: out.append(f"the legend's line: {M_['legT']!r}")
        if 'Sov upgrades: Major Threat Detection Array 3, Cyno beacon, Tritanium Prospecting Array 3' not in M_['tip']: out.append(f"the hover on {N(A)}: {M_['tip'][:200]!r}")
        if not M_['keyMoved'] or M_['redraw'] != 0: out.append(f"the map's key: moved with a pick {M_['keyMoved']}, a refresh after it redrew {M_['redraw']} (want moved, none)")
        if M_['dim2'][:5] != [False, False, False, False, True] or M_['homeDim']: out.append(f"Major Threat Detection Array unpicked: dimmed {M_['dim2']}, your system {M_['homeDim']} (want only the far one, which has nothing else, dimmed now; yours never)")
        pg.evaluate("() => { const st = sovStore(); st.pick.push('Major Threat Detection Array'); sovSave(); sovChanged(); }")
        reach = pg.evaluate("[itm.reach, itm.D[itGraphGet().at.get(%d)]]" % FAR)
        if not reach[1] > reach[0]: out.append(f'the far system {N(FAR)} is inside the reach {reach}: pick another')
        px, col = pg.evaluate(PX, [FAR, 44 / pg.evaluate('itm.G')])
        if not near_col(px, col): out.append(f'a picked system past "Map: within" drawn {px[:3]} (want bright, {col})')
        pg.evaluate("() => { itMapFilterSet('sec'); itMapStartView(); itMapDraw(); }")
    if 'lists' in parts:
        pg.evaluate("() => { itMapFilterSet('sov'); if(!sovShown()) sovOpen(true, false); sovP.lists = true; sovPaint(true); }"); pg.wait_for_timeout(200)
        ids = pg.evaluate("() => sovStore().lists.map(l => l.id)")
        if len(ids) == 2:
            pg.click(f'[data-sov-ed="{ids[1]}"]'); pg.wait_for_timeout(200)
            pg.fill('[data-sov-et]', BARE + N(B) + '\n'); pg.wait_for_timeout(150)
            e = pg.evaluate("() => (document.querySelector('.it-sov-echk .it-sov-sum') || {}).textContent")
            pg.click('[data-sov-es]'); pg.wait_for_timeout(300)
            st = pg.evaluate(STORE)
            if e != '3 ✓ · 0 ⚠ · 0 ✗ · 3 systems' or st['lists'][1]['text'] != BARE + N(B) + '\n' or st['lists'][0]['text'] != UPG: out.append(f'Edit / Save: checked {e!r}, stored {[l["text"][:40] for l in st["lists"]]}')
            pg.click(f'[data-sov-rp="{ids[0]}"]'); pg.wait_for_timeout(200)
            R0 = pg.evaluate("() => [document.querySelector('#itSovPaste').hidden, document.querySelector('[data-sov-add]').textContent, document.activeElement && document.activeElement.matches('#itSovPaste textarea')]")
            paste(pg, f'{N(C)} <- Exploration Detector 3'); pg.click('[data-sov-add]'); pg.wait_for_timeout(300)
            st = pg.evaluate(STORE)
            if R0 != [False, 'Replace', True] or [l['id'] for l in st['lists']] != ids or st['lists'][0]['text'] != f'{N(C)} <- Exploration Detector 3' or st['lists'][1]['text'] != BARE + N(B) + '\n':
                out.append(f"Replace: the box {R0}, the store {[(l['id'], l['text'][:30]) for l in st['lists']]}")
            pg.click(f'[data-sov-rm="{ids[0]}"]'); pg.wait_for_timeout(300)
            u = pg.evaluate("() => [sovStore().lists.map(l => l.id), !!document.querySelector('[data-sov-undo]'), document.activeElement && document.activeElement.matches('[data-sov-undo]')]")
            pg.click('[data-sov-undo]'); pg.wait_for_timeout(300)
            back = pg.evaluate("() => sovStore().lists.map(l => l.id)")
            pg.click(f'[data-sov-rm="{ids[0]}"]'); pg.wait_for_timeout(6500)
            gone = pg.evaluate("() => [sovStore().lists.map(l => l.id), !!document.querySelector('[data-sov-undo]'), JSON.parse(localStorage.getItem('tvSov')).lists.map(l => l.id)]")
            if u != [[ids[1]], True, True] or back != ids or gone != [[ids[1]], False, [ids[1]]]: out.append(f'Remove / Undo: after Remove {u}, after Undo {back}, 6.5 s after a second Remove {gone}')
        else: out.append(f'the lists to edit: {ids}')
        pg.reload(); pg.wait_for_timeout(500)
        if pg.evaluate("sovStore().lists.length") != 1: out.append('the lists not kept across a reload')
        di = pg.evaluate("() => JSON.parse(localStorage.getItem('dscanIntel'))")
        if any('sov' in k.lower() for k in di): out.append(f'dscanIntel changed its form: {sorted(di)}')
        ctx.close(); ctx, pg = start(b, html, 1440, errs, store=None)
    if 'full' in parts:
        pg.evaluate("() => { itMapFilterSet('sov'); if(!sovShown()) sovOpen(true, false, 'paste'); const s0 = Storage.prototype.setItem; Storage.prototype.setItem = function(k, v){ if(k === 'tvSov') throw new DOMException('full', 'QuotaExceededError'); return s0.call(this, k, v); }; }")
        paste(pg, f'{N(A)} <- Major Threat Detection Array 3'); pg.click('[data-sov-add]'); pg.wait_for_timeout(300)
        f = pg.evaluate("() => [document.querySelector('.it-sov-warn').textContent, sovStore().lists.length, localStorage.getItem('tvSov'), itMapDimmed(itGraphGet().at.get(%d))]" % A)
        if '(INTEL-11)' not in f[0] or f[1] != 1 or f[2] is not None or f[3]: out.append(f'a full storage: {f} (want INTEL-11 shown, the list kept for the visit and used on the map, nothing written)')
        ctx.close(); ctx, pg = start(b, html, 1440, errs, store=None)
    if 'names' in parts:
        n = pg.evaluate("""async (t) => { const keep = it.names, load = itLoadNames; it.names = null; let done; window.itLoadNames = () => new Promise((ok, no) => { done = [ok, no]; });
          itMapFilterSet('sov'); if(!sovShown()) sovOpen(true, false, 'paste');
          const ta = document.querySelector('#itSovPaste textarea'); ta.value = t; ta.dispatchEvent(new Event('input', {bubbles: true}));
          const wait = document.querySelector('.it-sov-chk').textContent, dis = document.querySelector('[data-sov-add]').disabled;
          done[1](codedError('INTEL-03', 'ESI named 0 of 5268 systems.')); await new Promise(r => setTimeout(r, 50)); const err = document.querySelector('.it-sov-picks').textContent;
          sovP.names = ''; window.itLoadNames = load; it.names = keep; sovNames(); sovPaint(true); const after = (document.querySelector('.it-sov-chk .it-sov-sum') || {}).textContent;
          return [wait, dis, err, after]; }""", f'{N(A)} <- Major Threat Detection Array 3')
        if n[0] != 'Loading system names…' or not n[1] or '(INTEL-03)' not in n[2] or n[3] != '1 ✓ · 0 ⚠ · 0 ✗ · 1 system': out.append(f'the names: {n} (want "Loading system names…" with Add off, then INTEL-03, then the line read)')
        pg.evaluate("() => sovOpen(false, false)")
    if 'one' in parts:
        pg.evaluate("() => { const st = sovStore(); st.lists = [{id: 'z', kind: '', text: %s, at: Date.now()}]; st.pick = ['Major Threat Detection Array']; sovIx = null; sovSave(); }" % json.dumps(UPG))
        o = pg.evaluate("""() => { itMapFilterSet('sov'); sovOpen(true, false); const a = [sovShown(), itWhListShown()]; itWhListOpen(true); const b = [sovShown(), itWhListShown()];
          sovOpen(true, false); const c = [sovShown(), itWhListShown()]; return [a, b, c]; }""")
        if o != [[True, False], [False, True], [True, False]]: out.append(f'one filter panel at a time: {o}')
        pg.evaluate("() => itNearToggle(true)"); pg.wait_for_timeout(300)
        P = pg.evaluate("""() => { const p = sovP.el.getBoundingClientRect(), bx = itm.box.getBoundingClientRect(), ny = document.getElementById('itNearCol').getBoundingClientRect(), pb = document.querySelector('[data-it-sovl]').getBoundingClientRect();
          return [sovShown(), itNearShown(), Math.round(p.left - pb.right), p.right <= ny.left + 0.5, p.top >= bx.top + 7.5 && p.bottom <= bx.bottom - 7.5, Math.round(p.width), itMapFree()[0] >= p.right - bx.left]; }""")
        if not (P[0] and P[1] and 0 <= P[2] <= 12 and P[3] and P[4] and P[5] >= SOV_MIN and P[6]): out.append(f'1440 px with Near You: {P} (want both open, the panel right of its button, clear of Near You, inside the map, at least {SOV_MIN} px, centring right of it)')
        pg.set_viewport_size({'width': 760, 'height': 1000}); pg.wait_for_timeout(500)
        t = pg.evaluate("() => [sovShown(), itNearShown(), itMapRoomForBoth(SOV_PANEL_MIN), itMapRoomForBoth()]")
        if t[0] == t[1] or t[2]: out.append(f'760 px: Sov {t[0]}, Near You {t[1]}, room for Sov {t[2]} (want one at a time under {SOV_MIN} px of room)')
        pg.evaluate("() => { itNearToggle(true); }"); pg.wait_for_timeout(200)
        t2 = pg.evaluate("() => [sovShown(), itNearShown()]")
        if t2 != [False, True]: out.append(f'760 px, Near You opened over the Sov panel: {t2} (want the panel shut)')
        g = pg.evaluate("() => { sovOpen(true, false); if(itNearShown()) return [-1, -1]; const g = sovP.el.querySelector('.it-sov-gs'); return [Math.round(sovP.el.getBoundingClientRect().width), g ? getComputedStyle(g).gridTemplateColumns.split(' ').length : 0]; }")
        if g[0] >= 540 and g[1] != 2 or g[0] < 500 and g[1] != 1: out.append(f'the picks in columns: panel {g[0]} px, {g[1]} columns (want 2 at full width, 1 under about 560 px)')
    if 'nosend' in parts:
        bad = sorted(x for x in IDS_ASKED if re.search(r'threat|detection|cynosural|prospecting|explor|toilet|nowhere', x, re.I))
        if bad: out.append(f'list words sent to ESI as names: {bad[:5]}')
    ctx.close()
    if 'phone' in parts:
        ctx, pg = start(b, html, 390, errs, h=844, touch=True, store={'v': 1, 'lists': [{'id': 'p', 'kind': '', 'text': UPG, 'at': int(time.time() * 1000)}], 'pick': ['Major Threat Detection Array']}, ny=True)
        pg.evaluate("itMapFilterSet('sov')"); pg.wait_for_timeout(200)
        pg.click('.it-map-fcur'); pg.wait_for_timeout(300)
        P = pg.evaluate("() => { const l = document.querySelector('[data-it-sovl]'), r = l.getBoundingClientRect(); return [getComputedStyle(l).visibility, Math.round(r.width), Math.round(r.height)]; }")
        if P != ['visible', 44, 44]: out.append(f'390 px: the panel button {P} (want visible with Sov upgrades on, 44 px)')
        pg.click('[data-it-sovl]'); pg.wait_for_timeout(300)
        S = pg.evaluate("""() => { const p = sovP.el.getBoundingClientRect(), bx = itm.box.getBoundingClientRect(), ks = [...sovP.el.querySelectorAll('.it-sov-k, button')].filter(x => x.offsetParent).map(x => Math.round(x.getBoundingClientRect().height));
          return [sovShown(), itNearShown(), document.querySelector('.it-map-fb').classList.contains('open'), Math.round(p.left - bx.left), Math.round(bx.right - p.right), Math.min(...ks), document.scrollingElement.scrollWidth <= innerWidth + 1]; }""")
        if S[:3] != [True, False, False] or not (8 <= S[3] <= 9 and 8 <= S[4] <= 9) or S[5] < 44 or not S[6]: out.append(f'390 px: the sheet {S} (want open, Near You and the column shut, 8 px each side, 44 px targets, no sideways scroll)')
        pg.click('.it-sovp .x-close'); pg.wait_for_timeout(200)
        if not pg.evaluate("document.activeElement && document.activeElement.matches('.it-map-fcur')"): out.append('390 px: × doesn\'t put focus back on the filter button')
        ctx.close()
    return out, errs

MUTANTS = [
    ('no level read', "m.set(u.kind, Math.max(m.get(u.kind) || 0, u.level)); got++;", "m.set(u.kind, 0); got++;", ('paste', 'map')),
    ('the dimming ignoring the picks', "  for(const [i, e] of sovIndex().at) for(const k of e.keys()) if(p.has(k)){ out.add(i); break; }", "  for(const [i] of sovIndex().at) out.add(i);", ('paste', 'map')),
    ('picked ones faint past the reach', " || (itm.sov && itm.sov.has(i)) ? 1 : !on(i)", " ? 1 : !on(i)", ('paste', 'map')),
    ('two panels open at once', "  itWhListOpen(false, false);   // one filter panel at a time", "", ('one',)),
    ('a full storage not said', "p.querySelector('.it-sov-warn').textContent = sovP.unsaved ?", "p.querySelector('.it-sov-warn').textContent = false ?", ('full',)),
    ('a paste checked without names', "  if(!it.names) return `<div class=\"it-whp-none\">${escapeHtml(sovP.names && sovP.names !== 'busy' ? sovP.names : 'Loading system names…')}</div>`;", "", ('names',)),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, 'the Sov upgrades filter: its table, store, panel, lists and map')
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
print('FAILURES:', NS['fails'])
sys.exit(1 if NS['fails'] else 0)
