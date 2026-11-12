"""Region names where system names are shown (build queue 038; Project doc roadmap/region-names-plan.md, mockup
Claude outputs/region_names_mockup.html).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/region_names_check.py [index.html]   -> 'FAILURES: N' (must be 0)

The owner's picks from the review of the 27 places a system is named ("1. yes, 2. yes (in it's own column)", "4. yes, 5. yes, 6. yes in
it's own column", "7. yes but not in the hover text (phones only get system name), 8. yes but not on hover and phones only get system
name.", "11. yes", "13. yes", "17. yes", "18. yes, 19. yes"; "we dont need region names for wormhole space"), and from the mockup
"A: own column", phones "System only", sentences "Yes, as drawn". Every region expected here is decoded from the page's INTEL_MAP and
INTEL_JUMPS by this check itself, not by the page. Uses intel_check.py's made-up folder, mocks and names (its first part, run here) and
sa_mocks.py's pilots; every pilot, line and character is made up. Checks:
  * the helper: a k-space system's region; a wormhole id (not in the table) and a table that doesn't match the jump table give none;
    the sentence bracket "(Region)", "(Region, N jumps)", or today's "(N jumps)" / nothing without a region;
  * 7 Near You and 8 the Feed: a Region cell right after the system on every row, the system's region (the first system's on the Feed),
    empty for none; one column (every cell's left edge the same); as wide as the widest of the 68 region names in the cell's own font
    (--it-rg-w, itSysWidths), nothing cut off; no hover text anywhere in the two lists names a region;
  * 11 the status line "Your Main in 1DQ1-A (Delve)"; 13 the notification's title "System (Region) · N jumps" (a stand-in Notification);
  * 17 the Feed search: a region's name finds exactly the shown reports with a system in it; the placeholder names region;
  * 18 System Analyzer and 19 Pilot Analyzer "From Intel" notes: "8WA-Z6 (Delve, 1 jump)", one bracket;
  * 1 the dossier's usual systems each with "(Region)"; 2 its kill list: a Region heading after System and each kill's region;
  * 4 the Fleet tab's head line, 5 the kill picker's heading and 6 its rows (own column, at least the widest region at 1440 px, nothing
    off its box at 1440 / 1000 / 900 / 600 px), with a wormhole kill showing none; the dossier's kill rows stay inside it at 1440 / 1000 px;
  * 390 px: the Region cells of 2, 6, 7, 8 hidden, the sentences keep the region; nothing off the page; no page errors;
  * mutants, each must fail: sysRegion always '', the phone rule gone, the column width not set, the search without regions, a
    sentence with two brackets.
"""
import sys, os, re, json, time, base64, struct, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
_src = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
_src = _src[:_src.index('with sync_playwright() as p:')]
NS = {'__file__': os.path.join(HERE, 'intel_check.py'), '__name__': 'intel_check_prefix'}
exec(compile(_src, 'intel_check.py (first part)', 'exec'), NS)   # the made-up folder, mocks, names; its table checks run too
globals().update({k: v for k, v in NS.items() if not k.startswith('__') and k not in ('check', 'fails')})
from playwright.sync_api import sync_playwright
check = NS['check']
PAGE = open(HTML, encoding='utf-8').read()

# ---- each system's region, decoded here from the page's own tables (independently of sysRegion) ----
_mm = re.search(r'^const INTEL_MAP = (.*);$', PAGE, re.M)
MAP = json.loads(_mm.group(1)); _reg = base64.b64decode(MAP['reg'])
REGION = {i: MAP['regions'][_reg[k]] for k, i in enumerate(ids)}
check(len(_reg) == len(ids) == MAP['systems'] and MAP['jumps'] == J['md5'], f"the region table: {len(MAP['regions'])} regions over {len(ids)} systems, made for this jump table")
WH = 31000005   # a made-up wormhole id: wormhole space has no gates, so it isn't in the tables
check(WH not in REGION, 'a wormhole id is not in the table')
R = lambda name: REGION[SYSID[name]]

T0 = time.time()
LINES = [(1, 'Scout Alt', '8WA-Z6 Marrek Ketter sabre'), (2, 'Gate Watcher', 'Anouk Morrow (Scimitar) jumped QX-L from 4K-TRB'),
         (3, 'Gate Watcher', 'E-VKJV Seren Ketter Kirra Longtail sabre'), (4, 'Someone', '8-YNBE Vesna Dossier vedmak'),
         (5, 'Someone', 'D-W7F0 Marrek Ketter vedmak x2'), (6, 'Scout Alt', 'Y-OMTZ clr')]
STATUS = "() => itStatusLine()"
ROWS = """(sel) => [...document.querySelectorAll(sel)].map(r => { const s = r.querySelector('.it-sysb'), g = r.querySelector('.it-rg');
  return {sys: s ? s.textContent : '', rg: g ? g.textContent : null, after: !!(g && s && (g.previousElementSibling === s || g.previousElementSibling === s.parentElement)),
    left: g ? Math.round(g.getBoundingClientRect().left) : null, cut: g ? g.scrollWidth > g.clientWidth + 0.5 : null, shown: g ? getComputedStyle(g).display !== 'none' : null}; })"""
NEAR_SEL, FEED_SEL = '#itNearList .it-nb', '#itFeedList .it-fd'

def intel_cases(b, html, out, errs, phone=True):
    def start(w):
        ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': 1100}); ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
        ctx.add_init_script(FS); route(ctx)
        pg = ctx.new_page(); pg.goto('file://' + html)
        pg.evaluate("(s) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({channels: ['region.intel'], me: 95000001, range: 3, sound: false, notify: false, forget: 15, hideFriendly: true})); }", SIDE)
        pg.reload(); pg.wait_for_timeout(400)
        setup_logs(pg); pg.click('#tabBtnIntel'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg)
        W(pg, F_INTEL, ''.join(line(T0 + dt, who, msg) for dt, who, msg in LINES)); tick(pg, 3200)
        return ctx, pg
    ctx, pg = start(1440)
    # the helper
    h = pg.evaluate(f"""() => [sysRegion({SYSID['E-VKJV']}), sysRegion({WH}), sysBracket({SYSID['E-VKJV']}), sysBracket({SYSID['E-VKJV']}, 4), sysBracket({WH}, 1), sysBracket({WH}),
      itRgHtml({WH}), (() => {{ const keep = INTEL_MAP.jumps; INTEL_MAP.jumps = 'not this table'; sysRegTab = undefined; const r = sysRegion({SYSID['E-VKJV']}); INTEL_MAP.jumps = keep; sysRegTab = undefined; return r; }})()]""")
    want = [R('E-VKJV'), '', f" ({R('E-VKJV')})", f" ({R('E-VKJV')}, 4 jumps)", ' (1 jump)', '', '<span class="it-rg"></span>', '']
    if h != want: out.append(f'the helper: {h} (want {want})')
    # 7 Near You and 8 the Feed
    for what, sel in (('Near You', NEAR_SEL), ('the Feed', FEED_SEL)):
        rows = pg.evaluate(ROWS, sel)
        if len(rows) < 3: out.append(f'{what}: {len(rows)} rows (want at least 3)'); continue
        bad = [r for r in rows if r['rg'] != REGION.get(SYSID.get(r['sys']), '') or not r['after']]
        if bad: out.append(f'{what}: rows without their region right after the system {bad[:2]}')
        if len({r['left'] for r in rows}) != 1: out.append(f'{what}: the Region cells are not one column {sorted({r["left"] for r in rows})}')
        if any(r['cut'] for r in rows): out.append(f'{what}: a region cut off {[r for r in rows if r["cut"]][:1]}')
    regs = list(dict.fromkeys(MAP['regions']))
    w = pg.evaluate("""(regs) => { const g = document.querySelector('#itNearList .it-rg, #itFeedList .it-rg'), c = document.createElement('canvas').getContext('2d'); c.font = getComputedStyle(g).font;
      const widest = Math.max(...regs.map(n => c.measureText(n).width)); return [parseFloat(getComputedStyle(g).getPropertyValue('--it-rg-w')) || 0, widest, g.getBoundingClientRect().width]; }""", regs)
    if not (w[0] >= w[1] and w[2] + 0.5 >= w[1]): out.append(f'the Region column ({w[0]} px set, {w[2]:.1f} px drawn) is narrower than the widest region name ({w[1]:.1f} px)')
    tips = pg.evaluate("""() => [...document.querySelectorAll('#itNearList .it-nb, #itFeedList .it-fd')].flatMap(r => { const g = r.querySelector('.it-rg'), n = g && g.textContent;
      return n ? [...r.querySelectorAll('.it-sysb[title], .it-rg[title], .j[title], .age[title], .it-age[title]')].map(e => e.title).filter(t => t.includes(n)) : []; })""")
    if tips: out.append(f'hover text on a row names its region: {tips[:2]}')
    # 11 the status line, 13 the notification
    st = pg.evaluate(STATUS)
    if not st.startswith(f"Your Main in 1DQ1-A ({R('1DQ1-A')}) · "): out.append(f'the status line {st!r}')
    nt = pg.evaluate(f"""() => {{ const got = []; window.Notification = function(t, o){{ got.push([t, o.tag]); }}; window.Notification.permission = 'granted';
      it.set.notify = true; it.set.sound = false; it.alerted = new Map(); const st = it.near.get({SYSID['8WA-Z6']}); const e = it.feed.find(x => x.p.sys[0] && x.p.sys[0].id === {SYSID['8WA-Z6']});
      itAlert(st, e); return got; }}""")
    jn = D0[SYSID['8WA-Z6']]
    if nt != [[f"8WA-Z6 ({R('8WA-Z6')}) · {jn} jump{'' if jn == 1 else 's'}", f"intel-{SYSID['8WA-Z6']}"]]: out.append(f'the notification {nt}')
    # 17 the Feed search
    q = pg.query_selector('[data-it-q]')
    ph = q.get_attribute('placeholder') if q else None
    if ph != 'Search pilot, corp, ship, system, region': out.append(f'the search placeholder {ph!r}')
    ENT = "() => [...document.querySelectorAll('#itFeedList [data-it-raw]')].map(b => Number(b.dataset.itRaw))"
    before = pg.evaluate(ENT)
    sysof = pg.evaluate("() => Object.fromEntries(it.feed.map(e => [e.id, e.p.sys.map(s => s.id)]))")
    rq = R('E-VKJV')
    exp = sorted(i for i in before if any(REGION.get(s) == rq for s in sysof[str(i)]))
    if q:
        pg.fill('[data-it-q]', rq.lower()); pg.wait_for_timeout(300); got = sorted(pg.evaluate(ENT)); pg.fill('[data-it-q]', ''); pg.wait_for_timeout(300)
        if not exp or got != exp: out.append(f'searching "{rq.lower()}" shows {got} (want {exp})')
    # 18 / 19 the From Intel notes
    pg.click('[data-it-assess="%d"]' % SYSID['8WA-Z6']); pg.wait_for_timeout(600)
    sa = pg.evaluate("() => document.querySelector('#saFromIntel').textContent")
    one = f"8WA-Z6 ({R('8WA-Z6')}, {jn} jump{'' if jn == 1 else 's'})"
    if f'· {one}, reported in the last' not in sa: out.append(f'the System Analyzer note {sa[:90]!r} (want "{one}")')
    pg.click('#tabBtnIntel'); pg.wait_for_timeout(200)
    pg.evaluate(f"() => [...document.querySelectorAll('#itNearList .it-nb')].find(r => r.dataset.itSys === '{SYSID['8WA-Z6']}').querySelector('button.it-pl').click()"); pg.wait_for_timeout(600)
    pa = pg.evaluate("() => document.querySelector('#pilotFromIntel').textContent")
    if f'at {one}' not in pa: out.append(f'the Pilot Analyzer note {pa[:90]!r} (want "at {one}")')
    ctx.close()
    if not phone: return
    # 390 px: the rows show the system only; the sentences keep the region
    ctx, pg = start(390)
    if not pg.is_visible('#itNearList') and pg.query_selector('[data-it-nv="list"]'): pg.click('[data-it-nv="list"]'); pg.wait_for_timeout(300)
    for what, sel in (('Near You', NEAR_SEL), ('the Feed', FEED_SEL)):
        rows = pg.evaluate(ROWS, sel)
        if not rows or any(r['shown'] for r in rows): out.append(f'390 px: {what} shows the Region cell {[r for r in rows if r["shown"]][:1]} ({len(rows)} rows)')
    st = pg.evaluate(STATUS)
    if f"1DQ1-A ({R('1DQ1-A')})" not in st: out.append(f'390 px: the status line lost its region {st!r}')
    over = pg.evaluate("() => [document.documentElement.scrollWidth, innerWidth]")
    if over[0] > over[1]: out.append(f'390 px: the page scrolls sideways {over}')
    ctx.close()

# ---- 1 / 2 the dossier, 4 / 5 / 6 the Fleet tab, on sa_mocks.py's pilots ----
PICKS = [{'id': 1, 'name': 'Mk Victim One', 'ship': 'Rifter', 'sysId': SYSID['E-VKJV'], 'sys': 'E-VKJV', 'ships': 3, 'isk': 12e6, 'word': ['h', 'hostile lost'], 'v': 'h'},
         {'id': 2, 'name': 'Mk Victim Two', 'ship': 'Caracal', 'sysId': 30000142, 'sys': 'Jita', 'ships': 1, 'isk': 0, 'word': ['n', 'neutral lost'], 'v': 'n'},
         {'id': 3, 'name': 'Mk Victim Three', 'ship': 'Stabber', 'sysId': WH, 'sys': 'J100005', 'ships': 2, 'isk': 5e6, 'word': ['h', 'hostile lost'], 'v': 'h'}]
PICK_JS = """([P, w]) => { let box = document.getElementById('rgPicks'); if(!box){ box = document.createElement('div'); box.id = 'rgPicks'; box.className = 'card'; document.querySelector('main, body').prepend(box); }
  box.style.width = w ? w + 'px' : ''; box.innerHTML = '<div class="fk-picks">' + P.map((p, i) => fkPickHtml({...p, t: Date.now() - 60000}, i)).join('') + '</div>';
  const b = box.getBoundingClientRect();
  return [...box.querySelectorAll('button.fk-pk')].map(x => { const r = x.querySelector('.fk-pk-r'), s = x.querySelector('.fk-pk-s');
    return {rg: r ? r.textContent : null, after: !!(r && r.previousElementSibling === s), shown: r ? getComputedStyle(r).display !== 'none' : null, cut: r ? r.scrollWidth > r.clientWidth + 0.5 : null,
      out: x.getBoundingClientRect().right > b.right + 1 || x.scrollWidth > x.clientWidth + 1}; }); }"""
def fleet_dossier_cases(b, html, out, errs):
    for w in (1440, 1000, 900, 600, 390):
        ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': 1000}); ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e)))); M.route(ctx)
        pg = ctx.new_page(); pg.goto('file://' + html); pg.wait_for_timeout(300)
        rows = pg.evaluate(PICK_JS, [PICKS, None])
        want = [REGION[SYSID['E-VKJV']], REGION[30000142], '']
        if [r['rg'] for r in rows] != want or not all(r['after'] for r in rows): out.append(f'{w} px: the kill picker rows {rows} (want regions {want} after the system)')
        if w < 600 and any(r['shown'] for r in rows): out.append(f'{w} px: the kill picker shows the Region cell')
        if w >= 600 and any(r['out'] for r in rows): out.append(f'{w} px: a kill picker row runs off its box {rows}')
        if w == 1440 and any(r['cut'] for r in rows): out.append(f'1440 px: a kill picker region cut off {rows}')
        if w == 1440:
            wide = pg.evaluate("(regs) => { const c = document.createElement('canvas').getContext('2d'), r = document.querySelector('#rgPicks .fk-pk-r'); c.font = getComputedStyle(r).font; return [r.getBoundingClientRect().width, Math.max(...regs.map(n => c.measureText(n).width))]; }", list(MAP['regions']))
            if wide[0] + 0.5 < wide[1]: out.append(f'1440 px: the kill picker\'s Region column ({wide[0]:.0f} px) is narrower than the widest region ({wide[1]:.0f} px)')
            hd = pg.evaluate(f"""() => [fkPicksWhereHtml([{{sysId: {SYSID['E-VKJV']}}}], ['E-VKJV']).replace(/<[^>]+>/g, ''), fkPicksWhereHtml([{{sysId: {WH}}}], ['J100005']).replace(/<[^>]+>/g, ''),
              (() => {{ const keep = [fk.sys, fk.km]; fk.sys = 'E-VKJV'; fk.km = {{solar_system_id: {SYSID['E-VKJV']}}}; const a = fkSubSysHtml().replace(/<[^>]+>/g, ''); fk.sys = keep[0]; fk.km = keep[1]; return a; }})()]""")
            hw = [f" in E-VKJV ({R('E-VKJV')})", ' in J100005', f" · E-VKJV ({R('E-VKJV')})"]
            if hd != hw: out.append(f'the kill picker heading and the Fleet tab head line {hd} (want {hw})')
        if w in (1440, 1000, 390):
            pg.click('#tabBtnPilot'); pg.fill('#pilotName', M.PILOTS[M.DOSSIER_PILOT][0]); pg.fill('#manualShip', ''); pg.click('#fitBtn'); pg.wait_for_timeout(300)
            pg.wait_for_function("() => !document.querySelector('#fitBtn').disabled && document.querySelector('#pilotBusy').hidden", timeout=120000); pg.wait_for_timeout(500)
            us = pg.evaluate("""() => [...document.querySelectorAll('[data-pd="systems"] b')].map(b => { const s = b.querySelector('[data-sec-sys]'), n = b.nextElementSibling;
              return [Number(s && s.dataset.secSys), n && n.classList.contains('pd-dim') && b.nextSibling === n.previousSibling ? n.textContent : n && n.classList.contains('pd-dim') ? n.textContent : '']; })""")
            bad = [u for u in us if u[1] != (f'({REGION[u[0]]})' if REGION.get(u[0]) else '')]
            if not us or bad: out.append(f'{w} px: the dossier\'s usual systems {us}')
            sab = M.byname['Sabre']
            pg.click(f'#pilotDossier [data-pd-exp="{sab}"]'); pg.wait_for_timeout(400)
            kl = pg.evaluate(f"""() => {{ const h = [...document.querySelectorAll('#pdk-{sab} .pdk-h span')].map(s => s.textContent);
              return [h, [...document.querySelectorAll('#pdk-{sab} .pdk[data-pdk]')].map(e => {{ const r = e.querySelector('.pdk-r');
                return [Number(e.dataset.pdk), r ? r.textContent : null, !!(r && r.previousElementSibling === e.querySelector('.pdk-s')), r ? getComputedStyle(r).display !== 'none' : null, r ? r.scrollWidth > r.clientWidth + 0.5 : null]; }})]; }}""")
            heads, ks = kl
            if w == 1440 and (heads[3:5] != ['System', 'Region']): out.append(f'the dossier kill list heading {heads}')
            badk = [k for k in ks if k[1] != REGION.get(M.KM[k[0]]['solar_system_id'], '') or not k[2]]
            if not ks or badk: out.append(f'{w} px: the dossier kills\' regions {badk[:2]} ({len(ks)} kills)')
            if w == 1440 and any(k[4] for k in ks): out.append('1440 px: a dossier kill\'s region cut off')
            if w == 390 and any(k[3] for k in ks): out.append('390 px: the dossier kill list shows the Region cell')
            over = pg.evaluate(f"() => [document.documentElement.scrollWidth, innerWidth, [...document.querySelectorAll('#pdk-{sab} .pdk')].filter(e => e.getBoundingClientRect().right > document.querySelector('#pilotDossier').getBoundingClientRect().right + 1).length]")
            if over[0] > over[1] or over[2]: out.append(f'{w} px: the page scrolls sideways or a kill row runs off the dossier {over}')   # (rows' content was already wider than the row under ~1100 px on main)
        ctx.close()

MUTANTS = [
    ('sysRegion always empty', "  return i === undefined ? '' : T.names[T.reg[i]] || '';\n", "  return '';\n", 'intel'),
    ('the phone rule gone', "    .it-nb.dd > .it-rg, .it-fd.fe .it-rg{display:none;}", "", 'intel'),
    ('the column width not set', " if(rg) x.style.setProperty('--it-rg-w', `${wr}px`);", "", 'intel'),
    ('the search without regions', "  parts.push(...new Set(e.p.sys.map(s => sysRegion(s.id))));", "", 'intel'),
    ('a sentence with two brackets', "  return parts.length ? ` (${parts.join(', ')})` : '';", "  return parts.map(x => ` (${x})`).join('');", 'intel'),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    errs = []
    out = []; intel_cases(b, HTML, out, errs)
    check(not out, 'Intel: Near You and the Feed have their Region column (one column, widest region, no hover), the status line, the notification, the search and both From Intel notes say the region; 390 px rows show the system only' + ''.join(f'\n      {o}' for o in out))
    out = []; fleet_dossier_cases(b, HTML, out, errs)
    check(not out, "the dossier's usual systems and kill list, the Fleet tab's head line, the kill picker's heading and rows say the region (none for a wormhole); 390 px hides the cells" + ''.join(f'\n      {o}' for o in out))
    tmp = tempfile.mkdtemp(prefix='region_mut_')
    for name_, a_, b_, part in MUTANTS:
        if PAGE.count(a_) != 1: check(False, f'mutant "{name_}": its text is in the page {PAGE.count(a_)} times'); continue
        f = os.path.join(tmp, 'index.html'); open(f, 'w', encoding='utf-8').write(PAGE.replace(a_, b_, 1))
        mo, me = [], []
        try: intel_cases(b, f, mo, me, phone=(name_ == 'the phone rule gone'))
        except Exception as e: mo.append(f'error {str(e)[:80]}')
        check(bool(mo), f'mutant "{name_}" fails ({mo[:1]})')
    check(not errs, f'no page errors {errs[:3]}')
    b.close()
print(f"FAILURES: {NS['fails']}")
sys.exit(1 if NS['fails'] else 0)
