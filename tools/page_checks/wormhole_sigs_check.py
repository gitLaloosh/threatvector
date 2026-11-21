"""The Wormholes tab, part 3: Signatures inside the System panel (build queue 059; Project doc roadmap/wormholes-part3-plan.md P1-P8, P20, P21;
mockup Claude outputs/wormholes_part3_mockup.html). The owner: "signatures are IN a system so signatures should probably be come part of the system
panel.", "we want ALL items that show up in the system on a probe scan available for the user", "off is probably safer, correct?" (Lazy update),
"let's have the lazy update ask for verification every time.", "one-step undo is a good idea, yes.", "any deletions should require verification.",
the list "looks more like the in-game list, reflects status of id's scanned based on color".

Made-up scans only (IDs and names invented; CCP's wormhole system names from the page's own table). No network. Checks:
  * the panel's order (P1): Class and Statics, Connections, Signatures, then who's there and notes; Statics still saved from its new place;
  * the reader (P4): a row per line by its ID, anomalies kept with their scan group, an unscanned row, ',' decimals, a broken line counted, a
    repeat once, the 150-row cap counted; text with no row refused with the how-to and the box kept open with the text;
  * the paste box (P2, P3): open with nothing kept, folded after a good read, the warning when the focus isn't where you are;
  * Lazy update (P5, P6): off by default; off a paste only adds and updates; on it asks before every removal (Remove them / Keep them); Undo
    puts the list back (also after Remove them) and is gone after a reload; an unscanned row never overwrites a known group; a missing ID that is
    a connection's end: the row goes, the end is marked, the connection stays;
  * Type (build queue 062, S1-S3; the owner: "unscanned items at the top, then scanned in the order provided", the game's order "unscanned, wormhole,
    gas site, data site, relic site, asteroid belt, combat site, then the rest"): the first sort; a group not listed after Combat, A to Z; inside a group
    the latest paste's order (`o`), rows without it after; a remembered sort switched to Type once (`sv: 2`), the next pick kept through a reload;
  * the list (P7): the game's signal bands at their edges, the game's shapes (cross at 0%, dot when partly scanned, a placeholder for a kind with
    no shape), short ages, the sort (each heading both ways, aria-sort, kept), select like the map (click, Ctrl-click, a tap, Space, the heading's
    box), Copy selected in the game's format and read back, Edit one (ID checked, a repeat refused) and several (type only), Delete asking first;
  * kept (P8): tvWhSigs and tvWhSecs through a reload (the section folded); a removed system's signatures gone; the panel's Remove asks first, a
    locked system refuses with no question;
  * drawing cost (LESSON #120): nothing written while the panel is shut; a rewrite never replaces the paste box being typed in;
  * stored data safe both ways: cb9a995's page (056) saving its chain leaves tvWhSigs, tvWhEnds and tvWhSecs as they were;
  * 1440 / 760 / 390 px: the list no wider than the panel, no sideways scroll; 44 px targets on a phone;
  * mutants; no page errors.
"""
import sys, os, json, tempfile, subprocess
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
HTML = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith('--')), os.path.join(REPO, 'index.html')))
PAGE = open(HTML, encoding='utf-8').read()
OLD = 'cb9a995'   # v2026.11.17.1 (056), the last main before part 3: never origin/main, which is this page once it's merged (LESSON #168)
fails = 0
def check(ok, msg):
    global fails
    print(('PASS ' if ok else 'FAIL ') + msg)
    if not ok: fails += 1

SEED = """() => { const T = whTable(), J = T.names.filter(n => /^J\\d{6}$/.test(n)), p = [40, 310, 655, 902, 1210].map(i => whIdOf(J[i]));
  const t0 = Date.now() - 3 * 3600e3; [p[0], p[1], p[2], p[1], p[3], p[4]].forEach((id, i) => whSeen(id, t0 + i * 60e3, false));
  whSave(); return p; }"""
ROW = lambda i, sg, g, n, pc: '\t'.join([i, sg, g, n, pc, '4,21 AU'])
SCAN1 = '\n'.join([ROW('XYZ-789', 'Cosmic Signature', 'Wormhole', 'Unstable Wormhole', '100,0%'), ROW('KLM-402', 'Cosmic Signature', 'Data Site', 'Mk Data Spot', '100,0%'),
                   ROW('RTA-610', 'Cosmic Signature', 'Gas Site', 'Mk Gas Cloud', '100,0%'), ROW('BHV-118', 'Cosmic Signature', '', '', '18,4%'),
                   ROW('PLE-930', 'Cosmic Signature', '', '', '0,0%'), ROW('JKO-554', 'Cosmic Anomaly', 'Combat Site', 'Mk Combat Spot', '100,0%'),
                   ROW('WDE-071', 'Cosmic Anomaly', 'Ore Site', 'Mk Ore Spot', '100,0%'), 'Distance\tnot a row', ROW('XYZ-789', 'Cosmic Signature', 'Wormhole', 'Unstable Wormhole', '100,0%')])
SCAN2 = '\n'.join([ROW('XYZ-789', 'Cosmic Signature', '', '', '100,0%'), ROW('BHV-118', 'Cosmic Signature', 'Relic Site', 'Mk Relic Spot', '62.5%'),
                   ROW('PLE-930', 'Cosmic Signature', 'Data Site', 'Mk Data Two', '100%'), ROW('JKO-554', 'Cosmic Anomaly', 'Combat Site', 'Mk Combat Spot', '100,0%'),
                   ROW('WDE-071', 'Cosmic Anomaly', 'Ore Site', 'Mk Ore Spot', '100,0%'), ROW('VAQ-812', 'Cosmic Signature', '', '', '4,8%')])   # KLM-402 and RTA-610 gone
N_SG = "document.querySelectorAll('#whPnSum [data-wh-l=\"sg\"][data-wh-lr]').length"
ROWS = "[...document.querySelectorAll('#whPnSum [data-wh-l=\"sg\"][data-wh-lr]')].map(r => r.dataset.whLr)"
SELD = "[...document.querySelectorAll('#whPnSum [data-wh-l=\"sg\"][aria-selected=\"true\"]')].map(r => r.dataset.whLr).sort().join()"
G = "JSON.parse(localStorage.getItem('tvWhSigs') || 'null')"

def start(b, html, w, errs, h=900, touch=False, keep=False):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch)
    ctx.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + html)
    if not keep: pg.evaluate("localStorage.clear()"); pg.reload()
    pg.wait_for_timeout(300); pg.evaluate("switchTab('wh')"); pg.wait_for_timeout(200)
    return ctx, pg

def paste(pg, text):
    pg.evaluate("(t) => { const ta = document.querySelector('#whPnSum [data-wh-ta]'); if(!ta) document.querySelector('#whPnSum [data-wh-paste]').click(); const t2 = document.querySelector('#whPnSum [data-wh-ta]'); t2.value = t; t2.dispatchEvent(new Event('input', {bubbles: true})); }", text)
    pg.click('#whPnSum [data-wh-read]'); pg.wait_for_timeout(120)

def row_click(pg, i, touch, mod=None):
    sel = f'#whPnSum [data-wh-l="sg"][data-wh-lr="{i}"] .id'
    pg.evaluate("(s) => document.querySelector(s).scrollIntoView({block: 'center'})", sel)
    if touch: pg.tap(sel)
    else: pg.click(sel, modifiers=[mod] if mod else [])
    pg.wait_for_timeout(80)

def cases(b, html, parts=('panel', 'lazy', 'list', 'store', 'type', 'older')):
    out, errs = [], []
    for w, h, touch in ((1440, 900, False), (760, 900, False), (390, 844, True)):
        tag = f'{w}px'
        ctx, pg = start(b, html, w, errs, h, touch); ev = pg.evaluate
        p = ev(SEED); B = p[1]
        ev("(n) => { whPnSet('sum'); whSelect(n); }", B); pg.wait_for_timeout(150)
        if 'panel' in parts:
            order = ev("""() => { const q = (s) => document.querySelector('#whPnSum ' + s), a = [q('[data-f="statics"]'), q('.wh-cnw'), q('[data-wh-sec="sigs"]'), q('[data-f="who"]')];
              return a.every(Boolean) && a.every((e, i) => !i || (a[i - 1].compareDocumentPosition(e) & Node.DOCUMENT_POSITION_FOLLOWING)); }""")
            if not order: out.append(f'{tag}: the panel\'s order should be Statics, Connections, Signatures, who\'s there')
            ev("() => { const f = document.querySelector('#whPnSum [data-f=\"statics\"]'); f.value = 'C247'; f.dispatchEvent(new Event('change', {bubbles: true})); }")
            if ev("(n) => whS.st.sys[n].statics", B) != 'C247': out.append(f'{tag}: Statics not saved from its new place')
            if not ev("!!document.querySelector('#whPnSum [data-wh-ta]') && !document.querySelector('#whPnSum [data-wh-paste]')"): out.append(f'{tag}: with nothing kept the paste box should be open (no toggle)')
            if 'you’re in' not in ev("document.querySelector('#whPnSum .wh-paste').textContent"): out.append(f'{tag}: the warning when the focus isn\'t where you are')
            paste(pg, 'hello there')
            if 'Nothing in that looks like' not in ev("document.querySelector('#whPnSum .wh-secbd').textContent") or ev("document.querySelector('#whPnSum [data-wh-ta]').value") != 'hello there':
                out.append(f'{tag}: unreadable text: the how-to, the box open with the text kept')
        paste(pg, SCAN1)
        n1 = ev(N_SG)
        if n1 != 7: out.append(f'{tag}: scan 1 should keep 7 rows (anomalies, unscanned, a repeat once), got {n1}')
        if 'panel' in parts:
            tip = ev("document.querySelector('#whPnSum .wh-secbd .wh-note[title]').title")
            if '1 line not read' not in tip or '2 of them anomalies' not in tip: out.append(f'{tag}: the result line\'s counts: {tip!r}')
            if ev("!!document.querySelector('#whPnSum [data-wh-ta]')") or ev("document.querySelector('#whPnSum [data-wh-paste]').getAttribute('aria-expanded')") != 'false':
                out.append(f'{tag}: after a good read the box should fold to "Paste a new scan"')
            cap = ev("() => { const t = Array.from({length: 160}, (_, i) => 'Q' + String.fromCharCode(65 + (i % 26)) + String.fromCharCode(65 + Math.floor(i / 26)) + '-' + String(100 + i).slice(-3) + '\\tCosmic Signature\\t\\t\\t1%').join('\\n'); const r = whScanRows(t); return [r.rows.length, r.over]; }")
            if cap != [150, 10]: out.append(f'{tag}: the 150-row cap should be counted: {cap}')
        if 'list' in parts:
            bands = ev("[24.9, 25, 74.9, 75, 99.9, 100].map(whBand).join()")
            if bands != '0,1,1,2,2,3': out.append(f'{tag}: the signal bands at their edges: {bands}')
            cls = ev("() => Object.fromEntries([...document.querySelectorAll('#whPnSum [data-wh-l=\"sg\"][data-wh-lr]')].map(r => [r.dataset.whLr, r.className]))")
            if 'b0' not in cls.get('BHV-118', '') or 'b3' not in cls.get('XYZ-789', ''): out.append(f'{tag}: colours by the game\'s bands: {cls}')
            ic = ev("""() => { const q = (i) => document.querySelector(`#whPnSum [data-wh-lr="${i}"] .ic`); return {data: !!q('KLM-402').querySelector('rect'), cross: !!q('PLE-930').querySelector('path') && !q('PLE-930').querySelector('circle'),
              dot: !!q('BHV-118').querySelector('circle'), ore: !!q('WDE-071').querySelector('ellipse'), same: getComputedStyle(q('XYZ-789')).color === getComputedStyle(q('XYZ-789').parentNode.querySelector('.id')).color}; }""")
            if not all(ic.values()): out.append(f'{tag}: the game\'s shapes in the row\'s colour: {ic}')
            ph = ev("(n) => { whS.sg.sys[n].rows.push({id: 'STR-001', sg: 'Structure', grp: 'Citadel', nm: '', pct: 100, f: Date.now(), t: Date.now()}); whPnRedraw(); const ok = !!document.querySelector('#whPnSum [data-wh-lr=\"STR-001\"] .wh-gwait'); whS.sg.sys[n].rows.pop(); whPnRedraw(); return ok; }", B)
            if not ph: out.append(f'{tag}: a kind with no shape drawn yet should show the placeholder')
            if not ev("[...document.querySelectorAll('#whPnSum [data-wh-l=\"sg\"][data-wh-lr] .ag')].every(e => /^\\d+ (s|min|h|d)$/.test(e.textContent))"): out.append(f'{tag}: ages short (s / min / h / d)')
            if not ev("!!document.querySelector('#whPnSum .wh-lt.sg [aria-sort=\"ascending\"] [data-wh-ls=\"ty\"]')"): out.append(f'{tag}: the first sort should be Type (062)')
            pg.click('#whPnSum .wh-lt.sg [data-wh-ls="id"]'); pg.wait_for_timeout(80)
            a = ev(ROWS)
            if a != sorted(a) or ev(G)['sort'] != {'k': 'id', 'd': 1}: out.append(f'{tag}: sort by ID A to Z, kept: {a}')
            pg.click('#whPnSum .wh-lt.sg [data-wh-ls="id"]'); pg.wait_for_timeout(80)
            a = ev(ROWS)
            if a != sorted(a, reverse=True) or not ev("!!document.querySelector('#whPnSum .wh-lt.sg [aria-sort=\"descending\"] [data-wh-ls=\"id\"]')"): out.append(f'{tag}: a second press turns it, aria-sort follows')
            if not ev("(() => { const t = document.querySelector('#whPnSum .wh-lt.sg'), pn = document.querySelector('#whPnSum'); return t.scrollWidth <= t.clientWidth + 1 && pn.scrollWidth <= pn.clientWidth + 1; })()"): out.append(f'{tag}: the list wider than the panel')
            if not ev("['copy', 'edit', 'del'].every(k => document.querySelector(`#whPnSum [data-wh-la=\"${k}\"][data-wh-l=\"sg\"]`).disabled)"): out.append(f'{tag}: nothing selected: Copy / Edit / Delete off')
            if touch:
                row_click(pg, 'KLM-402', True); row_click(pg, 'XYZ-789', True)
                if ev(SELD) != 'KLM-402,XYZ-789': out.append(f'{tag}: a tap adds a row: {ev(SELD)}')
                row_click(pg, 'XYZ-789', True)
                if ev(SELD) != 'KLM-402': out.append(f'{tag}: a second tap takes it off')
                row_click(pg, 'XYZ-789', True)
            else:
                row_click(pg, 'KLM-402', False)
                if ev(SELD) != 'KLM-402': out.append(f'{tag}: a click selects one row: {ev(SELD)}')
                row_click(pg, 'RTA-610', False, 'Control')
                if ev(SELD) != 'KLM-402,RTA-610': out.append(f'{tag}: Ctrl-click adds: {ev(SELD)}')
                row_click(pg, 'XYZ-789', False)
                if ev(SELD) != 'XYZ-789': out.append(f'{tag}: a plain click selects only that one: {ev(SELD)}')
                pg.focus('#whPnSum [data-wh-lr="KLM-402"]'); pg.keyboard.press('Space'); pg.wait_for_timeout(80)
                if ev(SELD) != 'KLM-402,XYZ-789': out.append(f'{tag}: Space on a row adds it: {ev(SELD)}')
            if 'Selected: 2' not in ev("document.querySelector('#whPnSum .wh-secbd .wh-lb').textContent"): out.append(f'{tag}: the bar should say Selected: 2')
            ev("navigator.clipboard.writeText = (t) => { window.__clip = t; return Promise.resolve(); }")
            pg.click('#whPnSum [data-wh-la="copy"][data-wh-l="sg"]'); pg.wait_for_timeout(100)
            clip = ev("window.__clip || ''")
            back = ev("(t) => whScanRows(t).rows.map(r => r.id).sort().join()", clip)
            if clip.count('\n') != 1 or 'XYZ-789\tCosmic Signature\tWormhole\tUnstable Wormhole\t100.0%\t' not in clip or back != 'KLM-402,XYZ-789': out.append(f'{tag}: Copy selected in the game\'s format, read back: {clip!r}')
            pg.click('#whPnSum [data-wh-la="edit"][data-wh-l="sg"]'); pg.wait_for_timeout(80)
            if not ev("!!document.querySelector('#whPnSum .wh-le [data-wh-le=\"grp\"]') && !document.querySelector('#whPnSum .wh-le [data-wh-le=\"id\"]')"): out.append(f'{tag}: Edit with two selected: type only')
            ev("document.querySelector('#whPnSum .wh-le [data-wh-le=\"grp\"]').value = 'Relic Site'"); pg.click('#whPnSum .wh-le [data-wh-la="save"]'); pg.wait_for_timeout(80)
            if [r['grp'] for r in ev(f"{G}.sys[{B}].rows") if r['id'] in ('KLM-402', 'XYZ-789')] != ['Relic Site', 'Relic Site']: out.append(f'{tag}: Edit several should set the type of both')
            row_click(pg, 'BHV-118', touch)
            if touch: row_click(pg, 'KLM-402', True); row_click(pg, 'XYZ-789', True)
            pg.click('#whPnSum [data-wh-la="edit"][data-wh-l="sg"]'); pg.wait_for_timeout(80)
            if not ev("['id', 'grp', 'nm'].every(k => !!document.querySelector(`#whPnSum .wh-le [data-wh-le=\"${k}\"]`))"): out.append(f'{tag}: Edit one: ID, type and name in place')
            pg.fill('#whPnSum .wh-le [data-wh-le="id"]', 'KLM-402'); pg.click('#whPnSum .wh-le [data-wh-la="save"]'); pg.wait_for_timeout(80)
            if 'already in the list' not in ev("document.querySelector('.wh-msg').textContent"): out.append(f'{tag}: a repeated ID should be refused')
            pg.fill('#whPnSum .wh-le [data-wh-le="id"]', 'bhv-119'); pg.fill('#whPnSum .wh-le [data-wh-le="nm"]', 'Mk Relic Spot'); ev("document.querySelector('#whPnSum .wh-le [data-wh-le=\"grp\"]').value = 'Relic Site'")
            pg.click('#whPnSum .wh-le [data-wh-la="save"]'); pg.wait_for_timeout(80)
            r = [x for x in ev(f"{G}.sys[{B}].rows") if x['id'] == 'BHV-119']
            if not r or r[0]['grp'] != 'Relic Site' or r[0]['nm'] != 'Mk Relic Spot': out.append(f'{tag}: Edit one should save ID, type and name')
            elif not ev("!!document.querySelector('#whPnSum [data-wh-lr=\"BHV-119\"] .ic circle')"): out.append(f'{tag}: the relic shape once the type is set')
            pg.click('#whPnSum [data-wh-la="del"][data-wh-l="sg"]'); pg.wait_for_timeout(80)
            if 'Delete 1 signature?' not in ev("document.querySelector('#whPnSum .wh-secbd .wh-lb').textContent") or ev(N_SG) != 7: out.append(f'{tag}: Delete selected should ask first')
            if ev("document.activeElement && document.activeElement.dataset.whAsk") != 'sg-no': out.append(f'{tag}: the question\'s focus should be on Cancel')
            pg.click('#whPnSum [data-wh-ask="sg-no"]'); pg.wait_for_timeout(80)
            if ev(N_SG) != 7: out.append(f'{tag}: Cancel deletes nothing')
            pg.click('#whPnSum [data-wh-la="del"][data-wh-l="sg"]'); pg.wait_for_timeout(80); pg.click('#whPnSum [data-wh-ask="sg-yes"]'); pg.wait_for_timeout(80)
            if ev(N_SG) != 6 or ev("!!document.querySelector('#whPnSum [data-wh-lr=\"BHV-119\"]')"): out.append(f'{tag}: Delete removes the selected signature')
            pg.click('#whPnSum [data-wh-lall="sg"]'); pg.wait_for_timeout(80)
            if 'Selected: 6' not in ev("document.querySelector('#whPnSum .wh-secbd .wh-lb').textContent"): out.append(f'{tag}: the heading box selects all')
            pg.click('#whPnSum [data-wh-lall="sg"]'); pg.wait_for_timeout(80)
            if 'Selected: 0' not in ev("document.querySelector('#whPnSum .wh-secbd .wh-lb').textContent"): out.append(f'{tag}: and none again')
            if touch:
                small = ev("[...document.querySelectorAll('#whPnSum .wh-sec button, #whPnSum .wh-sec .wh-lz, #whPnSum .wh-cnw button, #whPnSum [data-wh-lr]')].filter(e => e.offsetParent && e.getBoundingClientRect().height < 43.5).map(e => e.className || e.textContent.trim()).slice(0, 3)")
                if small: out.append(f'{tag}: 44 px targets in the lists: {small}')
        if 'lazy' in parts:
            ev("(n) => { const l = whLinksOf(n)[0]; whEndSet(l, n, 'NOS-275', ''); whEndSave(); }", B)
            paste(pg, '\n'.join([SCAN1, ROW('NOS-275', 'Cosmic Signature', 'Wormhole', 'Unstable Wormhole', '100,0%')]))
            if ev(f"{G}.lazy") is not False or ev("document.querySelector('#whPnSum [data-wh-sw=\"lazy\"]').checked"): out.append(f'{tag}: Lazy update should start off')
            n0 = ev(N_SG); paste(pg, SCAN2)
            if ev(N_SG) != n0 + 1: out.append(f'{tag}: Lazy off: a paste only adds and updates ({n0} → {ev(N_SG)})')
            if [x['grp'] for x in ev(f"{G}.sys[{B}].rows") if x['id'] == 'XYZ-789'] != ['Wormhole']: out.append(f'{tag}: an unscanned row overwrote a known group')
            pg.click('#whPnSum [data-wh-undo]'); pg.wait_for_timeout(80)
            if ev(N_SG) != n0: out.append(f'{tag}: Undo should put the list back ({ev(N_SG)} of {n0})')
            pg.click('#whPnSum [data-wh-sw="lazy"]'); pg.wait_for_timeout(80)
            if ev(f"{G}.lazy") is not True: out.append(f'{tag}: Lazy update should be kept on')
            paste(pg, SCAN2)
            ask = ev("(document.querySelector('#whPnSum .wh-secbd .wh-ask') || {}).textContent || ''")
            if f'would remove 3 of {n0}' not in ask or ev(N_SG) != n0: out.append(f'{tag}: Lazy on asks before removing ({ask!r})')
            pg.click('#whPnSum [data-wh-ask="lazy-keep"]'); pg.wait_for_timeout(80)
            if ev(N_SG) != n0 + 1: out.append(f'{tag}: Keep them applies the scan and removes nothing')
            paste(pg, SCAN2); pg.click('#whPnSum [data-wh-ask="lazy-rm"]'); pg.wait_for_timeout(80)
            if ev(N_SG) != 6 or 'removed 3' not in ev("document.querySelector('#whPnSum .wh-secbd [role=status]').textContent"): out.append(f'{tag}: Remove them removes the missing ones and counts them ({ev(N_SG)})')
            e = ev("(n) => { const l = whLinksOf(n).find(l => (whEnd(l, n) || {}).sig === 'NOS-275'); return l ? {gone: !!whEnd(l, n).gone, kept: true} : {kept: false}; }", B)
            if not e.get('kept') or not e.get('gone'): out.append(f'{tag}: a missing connection ID: the connection stays, its end marked: {e}')
            if not ev("!!document.querySelector('#whPnSum [data-wh-l=\"cn\"].old')"): out.append(f'{tag}: the connection\'s row should be dimmed')
            pg.click('#whPnSum [data-wh-undo]'); pg.wait_for_timeout(80)
            if ev(N_SG) != n0 + 1 or ev("!!document.querySelector('#whPnSum [data-wh-l=\"cn\"].old')"): out.append(f'{tag}: Undo after Remove them puts the rows and the end back')
        if 'store' in parts:
            pg.click('#whPnSum [data-wh-sec="sigs"]'); pg.wait_for_timeout(80)
            ev("(n) => { whS.p3.undo = {rows: [], t: 0, ends: []}; whPnRedraw(); }", B)
            pg.reload(); pg.wait_for_timeout(300); ev("(n) => { switchTab('wh'); whPnSet('sum'); whSelect(n); }", B); pg.wait_for_timeout(150)
            if ev("JSON.parse(localStorage.getItem('tvWhSecs')).sigs") is not False or ev("!!document.querySelector('#whSec-sigs')"): out.append(f'{tag}: the folded section should be kept')
            pg.click('#whPnSum [data-wh-sec="sigs"]'); pg.wait_for_timeout(80)
            if ev(N_SG) < 6 or ev("!!document.querySelector('#whPnSum [data-wh-undo]')"): out.append(f'{tag}: after a reload the list is kept and Undo gone')
            ev("() => { whPnSet(''); const b = document.querySelector('#whPnSum [data-pnb=\"sum\"]'); b.innerHTML = 'MARK'; whS.pn = {}; whPaint(true); }")
            if ev("document.querySelector('#whPnSum [data-pnb=\"sum\"]').innerHTML") != 'MARK': out.append(f'{tag}: the panel body written while it\'s shut (LESSON #120)')
            ev("whPnSet('sum')"); pg.wait_for_timeout(80)
            pg.click('#whPnSum [data-wh-paste]'); pg.wait_for_timeout(80); pg.focus('#whPnSum [data-wh-ta]'); pg.keyboard.type('ABC')
            same = ev("() => { const t = document.activeElement; whS.sg.sys[whFocus()].t -= 60000; whS.pn = {}; whPaint(true); return document.activeElement === t && t.isConnected && t.value === 'ABC'; }")
            if not same: out.append(f'{tag}: a rewrite replaced the paste box being typed in')
            ev("document.activeElement.blur()")
            pg.click('#whPnSum [data-wh-del]'); pg.wait_for_timeout(80)
            if ev("(n) => !!whS.st.sys[n]", B) is not True or 'Remove ' not in ev("document.querySelector('#whPnSum .wh-acts').textContent"): out.append(f'{tag}: Remove from the map should ask first')
            # the owner's screenshot (059): Cancel wrapped alone onto the next line; the two buttons stay on one line together
            # a width where the question and Remove fit on a line but Cancel doesn't: the two must go down together
            tops = ev("""() => { const k = document.querySelector('#whPnSum .wh-acts .wh-ask'), [q, r] = [k.firstElementChild, k.querySelector('button')];
              k.style.maxWidth = (q.getBoundingClientRect().width + r.getBoundingClientRect().width + 24) + 'px';
              const t = [...k.querySelectorAll('button')].map(e => Math.round(e.getBoundingClientRect().top)); k.style.maxWidth = ''; return t; }""")
            if len(tops) != 2 or tops[0] != tops[1]: out.append(f'{tag}: Remove and Cancel should sit on one line together: {tops}')
            pg.click('#whPnSum [data-wh-ask="del-yes"]'); pg.wait_for_timeout(120)
            if ev("(n) => !!whS.st.sys[n] || !!whS.sg.sys[n]", B) or str(B) in (ev(G) or {}).get('sys', {}): out.append(f'{tag}: the removed system\'s signatures should go with it (a jump back in shows none)')
            ev("(n) => { whS.mk[n] = {lock: true}; whMkSave(); whPnSet('sum'); whSelect(n); }", p[0]); pg.wait_for_timeout(80)
            ev("document.querySelector('#whPnSum [data-wh-del]').click()"); pg.wait_for_timeout(80)   # aria-disabled: Playwright won't press it
            if ev("!!document.querySelector('#whPnSum .wh-acts .wh-ask')") or 'locked' not in ev("document.querySelector('.wh-msg').textContent"): out.append(f'{tag}: a locked system refuses with no question')
        if not ev("document.documentElement.scrollWidth <= innerWidth"): out.append(f'{tag}: sideways scroll')
        ctx.close()
    if 'type' in parts: out += type_cases(b, html, errs)
    if 'older' in parts:
        old = os.path.join(os.path.dirname(HTML), '.wh_old_059.html')
        try:
            open(old, 'w', encoding='utf-8').write(subprocess.check_output(['git', '-C', REPO, 'show', f'{OLD}:index.html']).decode('utf-8'))
            ctx, pg = start(b, html, 1440, errs); ev = pg.evaluate
            p = ev(SEED); ev("(n) => { whPnSet('sum'); whSelect(n); }", p[1]); pg.wait_for_timeout(100); paste(pg, SCAN1)
            ev("(n) => { const l = whLinksOf(n)[0]; whEndSet(l, n, 'ABC-123', 'H296'); whEndSave(); whS.secs.sigs = false; whSecSave(); }", p[1])
            keys = ev("['tvWhSigs', 'tvWhEnds', 'tvWhSecs'].map(k => localStorage.getItem(k))")
            pg.goto('file://' + old); pg.wait_for_timeout(400)
            pg.evaluate("(n) => { switchTab('wh'); whS.st.sys[n].notes = 'Mk note'; whSave(); }", p[1]); pg.wait_for_timeout(200)
            if pg.evaluate("['tvWhSigs', 'tvWhEnds', 'tvWhSecs'].map(k => localStorage.getItem(k))") != keys: out.append('the older page (056) should leave tvWhSigs, tvWhEnds and tvWhSecs as they were')
            pg.goto('file://' + html); pg.wait_for_timeout(300); pg.evaluate("(n) => { switchTab('wh'); whPnSet('sum'); whSelect(n); }", p[1]); pg.wait_for_timeout(100)
            if pg.evaluate("(n) => (whS.sg.sys[n] || {rows: []}).rows.length", p[1]) != 7: out.append('back on this page after the older one: the signatures should still be there')
            ctx.close()
        finally:
            if os.path.exists(old): os.unlink(old)
    return out, errs

TY_ORDER = ['BHV-118', 'PLE-930', 'XYZ-789', 'RTA-610', 'KLM-402', 'WDE-071', 'JKO-554']   # unscanned (paste order), Wormhole, Gas, Data, Ore, Combat
TY_SORT = """() => { const r = (id, grp, o) => Object.assign({id, grp, nm: '', pct: 100, f: 1, t: 1}, o === undefined ? {} : {o});
  const rows = [r('AAA-001', 'Citadel', 0), r('AAA-002', 'Combat Site', 5), r('AAA-003', 'Wormhole', 9), r('AAA-004', 'Wormhole', 2), r('AAA-005', 'Wormhole'),
    r('AAA-006', 'Beacon', 1), r('AAA-007', '', 4), r('AAA-008', 'Relic Site', 3), r('AAA-009', 'Gas Site', 8)];
  return rows.sort(WH_SG_SORT.ty).map(x => x.id).join(); }"""
def type_cases(b, html, errs):
    out = []
    ctx, pg = start(b, html, 1440, errs); ev = pg.evaluate
    p = ev(SEED); B = p[1]; ev("(n) => { whPnSet('sum'); whSelect(n); }", B); pg.wait_for_timeout(120); paste(pg, SCAN1)
    a = ev(ROWS)
    if a != TY_ORDER: out.append(f"Type: unscanned first, then the game's group order: {a}")
    # inside a group the latest paste's order; a group not listed after Combat Site, A to Z; a row with no `o` (an older page's) after those with it
    srt = ev(TY_SORT)
    if srt != 'AAA-007,AAA-004,AAA-003,AAA-005,AAA-009,AAA-008,AAA-002,AAA-006,AAA-001': out.append(f'Type: group order, paste order inside a group, others A to Z: {srt}')
    # a second paste listing two ore sites the other way round turns them
    paste(pg, '\n'.join([ROW('WDE-072', 'Cosmic Anomaly', 'Ore Site', 'Mk Ore Two', '100,0%'), ROW('WDE-071', 'Cosmic Anomaly', 'Ore Site', 'Mk Ore Spot', '100,0%')]))
    a = ev(ROWS)
    if a.index('WDE-072') > a.index('WDE-071'): out.append(f"Type: the latest paste's order inside a group: {a}")
    if any('o' not in x for x in ev(f"{G}.sys[{B}].rows")): out.append('Type: every row should carry its place (o)')
    # switch everyone once (Q6): a remembered Age sort without sv becomes Type; the next pick is kept through a reload
    ev("() => { const o = " + G + "; o.sort = {k: 'f', d: 1}; delete o.sv; localStorage.setItem('tvWhSigs', JSON.stringify(o)); }")
    pg.reload(); pg.wait_for_timeout(300); ev("(n) => { switchTab('wh'); whPnSet('sum'); whSelect(n); }", B); pg.wait_for_timeout(150)
    if ev("whS.sg.sort.k") != 'ty': out.append('Type: a remembered sort without sv should switch to Type once')
    pg.click('#whPnSum .wh-lt.sg [data-wh-ls="f"]'); pg.wait_for_timeout(80)
    g = ev(G)
    if g.get('sv') != 2 or g['sort'] != {'k': 'f', 'd': 1}: out.append(f"Type: the next pick saved with sv 2: {g.get('sv')}, {g['sort']}")
    pg.reload(); pg.wait_for_timeout(300); ev("(n) => { switchTab('wh'); whPnSet('sum'); whSelect(n); }", B); pg.wait_for_timeout(150)
    if ev("whS.sg.sort.k") != 'f': out.append('Type: after the switch the sort you pick is kept')
    ctx.close()
    return out

MUTANTS = [
    ('Type: ID order inside a group', "|| whSgPos(a) - whSgPos(b) || a.id.localeCompare(b.id)};", "|| a.id.localeCompare(b.id)};", ('type',)),
    ('Type: unscanned last', "function whSgTyRank(x){ if(!x.grp) return 0;", "function whSgTyRank(x){ if(!x.grp) return 99;", ('type',)),
    ('Type: a remembered sort kept (no switch)', "sort: o.sv === 2 && o.sort &&", "sort: o.sort &&", ('type',)),
    ('Type: the paste order not kept', "[...by.values()].sort((a, b) => oldPos(a) - oldPos(b) || a.id.localeCompare(b.id)).forEach((x, i) => { x.o = i; });", "", ('type',)),
    ('anomalies dropped', "    seen.add(id); rows.push({id, sg: whTxt(c[1], 24),", "    if(/anomal/i.test(c[1] || '')) continue; seen.add(id); rows.push({id, sg: whTxt(c[1], 24),", ('panel',)),
    ('Lazy update on by default', "out = {v: 1, lazy: o.lazy === true,", "out = {v: 1, lazy: o.lazy !== false,", ('lazy',)),
    ('a lazy removal without asking', "  if(gone.length && !force){ P.lazyAsk", "  if(false){ P.lazyAsk", ('lazy',)),
    ('Undo keeps the removals', "  if(u.rows.length) S.sg.sys[n] = {t: u.t, rows: u.rows}; else delete S.sg.sys[n];", "", ('lazy',)),
    ('an unscanned row overwrites the group', "if(x.sg) o.sg = x.sg; if(x.grp){ o.grp = x.grp; o.nm = x.nm; }", "if(x.sg) o.sg = x.sg; o.grp = x.grp; o.nm = x.nm;", ('lazy',)),
    ('a band edge off by one', "return p >= 100 ? 3 : p >= 75 ? 2 : p >= 25 ? 1 : 0;", "return p >= 100 ? 3 : p >= 75 ? 2 : p > 25 ? 1 : 0;", ('list',)),
    ('Delete selected without asking', "  if(a === 'del'){ if(!sel.size) return; P.ask = {k}; P.edit[k] = null;", "  if(a === 'del'){ if(!sel.size) return; P.ask = null; whAskAct(k + '-yes'); return;", ('list',)),
    ('the sort not kept', "whS.sg.sort = {k: key, d: o.k === key ? -o.d : 1}; whSgSave();", "whS.sg.sort = {k: key, d: o.k === key ? -o.d : 1};", ('list',)),
    ("the question's buttons wrap one by one", '<span class="wh-askb">${whAskBtnsHtml(btns)}</span>', '${whAskBtnsHtml(btns)}', ('store',)),
    ('Connections above Class and Statics', "    // 059 (P1): Class and Statics first", "    + `<div class=\"wh-cnw\"><div class=\"wh-sub\">Connections</div>${whCnListHtml(n)}</div>`\n    // 059 (P1): Class and Statics first", ('panel',)),
    ('a removed system\'s signatures kept', "delete whS.mk[id]; delete whS.sg.sys[id];", "delete whS.mk[id];", ('store',)),
]

if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch()
        out, errs = cases(b, HTML)
        for o in out: check(False, o)
        check(not out, 'Signatures: the panel\'s order, the reader, the paste box, Lazy update and Undo, the list, kept, drawing cost, the older page')
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
