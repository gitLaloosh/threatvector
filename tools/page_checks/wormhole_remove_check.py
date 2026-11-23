"""The Wormholes tab: removing systems (065a, the build session's first delivery from build queue 065's "with the next delivery" blocks).

The owner, 2026-11-21: "record the following bug related to removing a system from the wormhole tab: content hidden by bottom of the map." and
"ability to select a group of systems exists but not the ability to remove all selected systems. when multiple are selected, right click > delete
(can we have this work with the delete key?) should delete everything that's selected (with verification prompt of course)."; at the review,
2026-11-22: the group menu's other items act on "The one right-clicked (Recommended)", the Delete key's question shows "Beside last-picked system
(Recommended)", "No mockup (Recommended)".

Made-up Intel (intel_check.py's folder and stand-ins, through wormhole_menu_check.py's set-up), CCP's wormhole system names from the page's own
table. Checks, at 1440 x 700 (a short map, where the question went under the map's bottom) and 390 px:
  * the system menu opened as low as it fits, then Remove: the question's Remove and Cancel inside the map and on the screen; the same opened at
    the top; the empty-space menu's Remove all question opened low; the System panel's own Remove question inside its panel;
  * a selection of 3 (Shift-click) with one locked: a right-click on one of them says "Remove 3 selected…"; its question asks for 2 and names the
    locked one; Cancel keeps all; Remove takes the 2 and their connections, keeps the locked one, clears the selection and says so; the menu's tag
    and status act on the system right-clicked only; a right-click on a system outside the selection is today's single-system menu;
  * the Delete key (and Backspace) with the map focused: the same question in the system menu at the system picked last, inside the map; Remove
    takes them; one system selected: its own question; Delete typed in the Add box or the tag field removes nothing and asks nothing;
  * mutants; no page errors.
"""
import sys, os, re, json, time, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
_m = open(os.path.join(HERE, 'wormhole_menu_check.py'), encoding='utf-8').read()
_m = _m[:_m.index('\ndef cases(')]
NS = {'__file__': os.path.join(HERE, 'wormhole_menu_check.py'), '__name__': 'wormhole_menu_check_prefix'}
exec(compile(_m, 'wormhole_menu_check.py (first part)', 'exec'), NS)   # intel_check's folder and stand-ins, start, intel_on, jump, AT, menu_on
globals().update({k: v for k, v in NS.items() if not k.startswith('__') and k not in ('check', 'fails')})
from playwright.sync_api import sync_playwright
check = NS['check']
PAGE = open(HTML, encoding='utf-8').read()

# the buttons of the question in a menu (or the panel), against the map's box and the screen
INSIDE = """(sel) => { const m = document.querySelector(sel), bx = document.querySelector('.wh-box').getBoundingClientRect(), bs = m ? [...m.querySelectorAll('.wh-ask button')] : [];
  return {on: !!m && !m.hidden, n: bs.length, q: m && m.querySelector('.wh-ask') ? m.querySelector('.wh-ask').textContent.trim() : '',
    inside: bs.length > 0 && bs.every(b => { const r = b.getBoundingClientRect(), mr = m.getBoundingClientRect(); return r.height > 0 && r.top >= bx.top - 1 && r.bottom <= Math.min(bx.bottom, innerHeight) + 1
      && r.left >= bx.left - 1 && r.right <= bx.right + 1 && r.top >= mr.top - 1 && r.bottom <= mr.bottom + 1; })}; }"""

def chain(pg, n):   # a chain of n wormhole systems after 1DQ1-A, made by jumps (the page's own tracking), returned as ids
    J = pg.evaluate("(n) => whTable().names.filter(x => /^J\\d{6}$/.test(x)).slice(0, n)", n)
    intel_on(pg); t = time.time(); jump(pg, '1DQ1-A', t)
    for k, nm in enumerate(J): jump(pg, nm, t + 1 + k)
    pg.click('#tabBtnWh'); pg.wait_for_timeout(400)
    return pg.evaluate("(n) => n.map(x => whIdOf(x))", ['1DQ1-A'] + J)

def low_open(pg, sid, top=False):   # the system menu opened as low as it fits (its bottom at the map's), or at the top
    pg.evaluate("([id, top]) => { const bx = whS.el.querySelector('.wh-box'); whMenuOpen(id, 40, top ? 4 : bx.clientHeight); }", [sid, top]); pg.wait_for_timeout(100)

def shift_click(pg, sid):
    a = pg.evaluate(AT, sid); pg.keyboard.down('Shift'); pg.mouse.click(a['x'], a['y']); pg.keyboard.up('Shift'); pg.wait_for_timeout(120)

def cases(b, html, parts=('cut', 'group', 'key', 'phone')):
    out, errs = [], []
    ctx, pg = start(b, html, 1440, errs, h=700)
    if not pg.evaluate("typeof whMenuOpen === 'function'"): out.append('no system menu'); ctx.close(); return out, errs
    ids = chain(pg, 5); k1, j0, j1, j2, j3, j4 = ids
    if None in ids: out.append(f'the chain wasn\'t made: {ids}'); ctx.close(); return out, errs
    if 'cut' in parts:
        for top in (False, True):
            low_open(pg, j1, top); pg.click('.wh-smenu [data-wh-m="del"]'); pg.wait_for_timeout(150)
            r = pg.evaluate(INSIDE, '.wh-smenu')
            if not r['on'] or r['n'] != 2 or not r['inside']: out.append(f'1440x700, the menu opened {"at the top" if top else "low"}: Remove\'s question inside the map: {r}')
            pg.keyboard.press('Escape'); pg.wait_for_timeout(80)
        pg.evaluate("() => { const bx = whS.el.querySelector('.wh-box'); whHereOpen(300, bx.clientHeight); }"); pg.wait_for_timeout(100)
        pg.click('.wh-hmenu [data-wh-all="rm"]'); pg.wait_for_timeout(150)
        r = pg.evaluate(INSIDE, '.wh-hmenu')
        if not r['on'] or r['n'] != 2 or not r['inside']: out.append(f'1440x700: Remove all\'s question inside the map: {r}')
        pg.evaluate("whHereClose()")
        # the System panel's own Remove: inside its panel (it scrolls)
        pg.evaluate("(id) => { whPnSet('sum', true); whSelect(id); }", j2); pg.wait_for_timeout(200)
        d = pg.query_selector('#whPnSum [data-wh-del]')
        if d:
            d.scroll_into_view_if_needed(); d.click(); pg.wait_for_timeout(150)
            r = pg.evaluate("""() => { const p = document.querySelector('#whPnSum'), bs = [...p.querySelectorAll('.wh-ask button')], pr = p.getBoundingClientRect();
              bs.forEach(x => x.scrollIntoView({block: 'nearest'})); return bs.length === 2 && bs.every(x => { const r = x.getBoundingClientRect(); return r.top >= pr.top - 1 && r.bottom <= pr.bottom + 1; }); }""")
            if not r: out.append('1440x700: the System panel\'s Remove question can\'t be reached inside its panel')
            no = pg.query_selector('#whPnSum .wh-ask button:last-child')
            if no: no.click(); pg.wait_for_timeout(100)
        else: out.append('the System panel has no Remove for a system ([data-wh-del])')
    if 'group' in parts:
        pg.evaluate("() => { whS.M.group.clear(); whDraw(); }")
        pg.evaluate("(id) => { (whS.mk[id] = whS.mk[id] || {}).lock = true; whMkSave(); whPaint(true); }", j3)
        for sid in (j1, j2, j3): shift_click(pg, sid)
        if pg.evaluate("[...whS.M.group].sort()") != sorted([j1, j2, j3]): out.append(f'Shift-click should select 3: {pg.evaluate("[...whS.M.group]")}')
        menu_on(pg, j2)
        t = pg.evaluate("() => { const b = document.querySelector('.wh-smenu [data-wh-m=\"gdel\"]'); return b ? b.textContent.trim() : null; }")
        if t != 'Remove 3 selected…': out.append(f'a right-click inside the selection: its Remove should read "Remove 3 selected…": {t!r}')
        # the other items act on the system right-clicked only
        pg.fill('.wh-smenu [data-wh-mtag]', 'GRP'); pg.click('.wh-smenu [data-wh-m="tag"]'); pg.wait_for_timeout(120)
        tags = pg.evaluate("(a) => a.map(id => (whS.mk[id] || {}).tag || '')", [j1, j2, j3])
        if tags != ['', 'GRP', '']: out.append(f'the group menu\'s tag should go on the system right-clicked only: {tags}')
        if pg.evaluate("whS.M.group.size") != 3: out.append('setting a tag from the group menu should keep the selection')
        menu_on(pg, j2); pg.click('.wh-smenu [data-wh-m="gdel"]'); pg.wait_for_timeout(150)
        r = pg.evaluate(INSIDE, '.wh-smenu'); nm3 = pg.evaluate("(id) => whName(id)", j3)
        if not (r['on'] and r['n'] == 2 and r['inside'] and 'Remove 2 selected systems' in r['q'] and nm3 in r['q']): out.append(f'the group\'s question: 2 to remove, the locked one named, inside the map: {r}')
        pg.click('.wh-smenu .wh-ask button:last-child'); pg.wait_for_timeout(150)   # Cancel
        if pg.evaluate("(a) => a.every(id => !!whS.st.sys[id])", [j1, j2, j3]) is not True: out.append('Cancel should keep every selected system')
        links0 = pg.evaluate("(a) => whS.st.links.filter(l => a.includes(l.a) || a.includes(l.b)).length", [j1, j2])
        menu_on(pg, j1); pg.click('.wh-smenu [data-wh-m="gdel"]'); pg.wait_for_timeout(120); pg.click('.wh-smenu .wh-ask button:first-child'); pg.wait_for_timeout(250)
        g = pg.evaluate("""(a) => ({gone: a.slice(0, 2).every(id => !whS.st.sys[id]), kept: !!whS.st.sys[a[2]], links: whS.st.links.filter(l => a.slice(0, 2).includes(l.a) || a.slice(0, 2).includes(l.b)).length,
          group: whS.M.group.size, msg: whS.el.querySelector('.wh-msg').textContent, saved: Object.keys((JSON.parse(localStorage.getItem('tvWhChain')) || {}).sys || {}).map(Number)})""", [j1, j2, j3])
        if not (g['gone'] and g['kept'] and g['links'] == 0 and g['group'] == 0 and 'Removed 2 selected systems; 1 locked kept' in g['msg'] and j1 not in g['saved'] and j3 in g['saved']):
            out.append(f'Remove: the 2 and their connections go ({links0} before), the locked one stays, the selection cleared, said, saved: {g}')
        # outside the selection: the single-system menu
        pg.evaluate("(id) => { (whS.mk[id] || {}).lock = false; delete whS.mk[id].lock; whMkSave(); }", j3)
        shift_click(pg, j0); shift_click(pg, j3); menu_on(pg, j4)
        r = pg.evaluate("() => [!!document.querySelector('.wh-smenu [data-wh-m=\"gdel\"]'), !!document.querySelector('.wh-smenu [data-wh-m=\"del\"]')]")
        if r != [False, True]: out.append(f'a right-click outside the selection: the single system\'s Remove: {r}')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(80)
    if 'key' in parts:
        pg.evaluate("() => { whMenuClose(false); whS.M.group.clear(); whDraw(); }")
        live = pg.evaluate("() => Object.keys(whS.st.sys).map(Number).filter(id => !whLocked(id) && id !== whS.last)")
        if len(live) < 3: out.append(f'the Delete key: too few systems left to test ({live})')
        else:
            a, c, e = live[-3:]
            shift_click(pg, a); shift_click(pg, c)
            if not pg.evaluate("document.querySelector('.wh-box').contains(document.activeElement)"): out.append('after Shift-click the map should have the focus')
            pg.keyboard.press('Delete'); pg.wait_for_timeout(150)
            r = pg.evaluate(INSIDE, '.wh-smenu'); at = pg.evaluate("whS.menu")
            if not (r['on'] and r['n'] == 2 and r['inside'] and 'Remove 2 selected systems' in r['q']): out.append(f'Delete with 2 selected: the group\'s question in the system menu, inside the map: {r}')
            if at != c: out.append(f'Delete: the menu should open at the system picked last ({c}), not {at}')
            if not pg.evaluate("(a) => a.every(id => !!whS.st.sys[id])", [a, c]): out.append('Delete removed before Remove was pressed')
            pg.click('.wh-smenu .wh-ask button:first-child'); pg.wait_for_timeout(250)
            if pg.evaluate("(a) => a.some(id => !!whS.st.sys[id])", [a, c]): out.append('Delete, then Remove: the 2 selected should be gone')
            # one system: its own question; Backspace the same
            s1 = pg.evaluate(AT, e); pg.mouse.click(s1['x'], s1['y']); pg.wait_for_timeout(150)
            pg.evaluate("() => document.querySelector('.wh-box').focus()")
            pg.keyboard.press('Backspace'); pg.wait_for_timeout(150)
            r = pg.evaluate(INSIDE, '.wh-smenu'); nm = pg.evaluate("(id) => whName(id)", e)
            if not (r['on'] and r['n'] == 2 and f'Remove {nm} and its connections?' in r['q']): out.append(f'Backspace with one system selected: its own question: {r}')
            pg.keyboard.press('Escape'); pg.wait_for_timeout(80)
            # Delete typed in a text field: nothing removed, nothing asked
            n0 = pg.evaluate("Object.keys(whS.st.sys).length")
            pg.evaluate("(id) => { whS.M.group.add(id); whS.M.group.add(whS.last); whDraw(); }", e)
            pg.click('[data-wh-pop="add"]'); pg.wait_for_timeout(100); pg.fill('.wh-addf input[name=sys]', 'J12'); pg.focus('.wh-addf input[name=sys]')
            pg.keyboard.press('Delete'); pg.keyboard.press('Backspace'); pg.wait_for_timeout(120)
            if pg.evaluate(MENU) or pg.evaluate("Object.keys(whS.st.sys).length") != n0: out.append('Delete typed in the Add box should only edit the text')
            pg.evaluate("whPopClose()"); menu_on(pg, e); pg.focus('.wh-smenu [data-wh-mtag]'); pg.keyboard.press('Delete'); pg.wait_for_timeout(100)
            if pg.evaluate("Object.keys(whS.st.sys).length") != n0 or pg.query_selector('.wh-smenu .wh-ask'): out.append('Delete in the menu\'s tag field should only edit the text')
            pg.keyboard.press('Escape')
    ctx.close()
    if 'phone' in parts:
        ctx, pg = start(b, html, 390, errs, h=760, touch=True)
        ids = chain(pg, 3)
        pg.evaluate("whPnSet('', true)"); pg.wait_for_timeout(150)
        for top in (False, True):
            low_open(pg, ids[2], top); pg.evaluate("document.querySelector('.wh-smenu [data-wh-m=\"del\"]').click()"); pg.wait_for_timeout(150)
            r = pg.evaluate(INSIDE, '.wh-smenu')
            if not r['on'] or r['n'] != 2 or not r['inside']: out.append(f'390, the menu opened {"at the top" if top else "low"}: Remove\'s question inside the map: {r}')
            pg.evaluate("whMenuClose(false)")
        if not pg.evaluate("document.documentElement.scrollWidth <= innerWidth"): out.append('390: sideways scroll')
        ctx.close()
    return out, errs

MUTANTS = [
    ('the menu not placed again after Remove (the bug)', "const sm = S.el.querySelector('.wh-smenu'); whAskFocus(sm); whMenuReplace(sm); return;\n  }\n  if(k === 'gdel')",
     "const sm = S.el.querySelector('.wh-smenu'); whAskFocus(sm); return;\n  }\n  if(k === 'gdel')", ('cut',)),
    # Remove all's question is shorter than the menu it replaces, so it can't run off the map: its re-place is a guard with no mutant here
    ('no group Remove in the menu', "function whGroupOf(n){ const S = whS, M = S.M; if(!M", "function whGroupOf(n){ return null; const S = whS, M = S.M; if(!M", ('group',)),
    ('the group removed without asking', "    S.menuIds = g; it0.outerHTML = whGroupAskHtml(g);", "    whMenuClose(true); whRemoveIds(g, 'selected'); return; it0.outerHTML = whGroupAskHtml(g);", ('group',)),
    ('the group\'s Remove takes a locked system', "keep = have.filter(whLocked), go = have.filter(n => !whLocked(n));", "keep = [], go = have;", ('group',)),
    ('the group\'s tag on every selected system', "  if(k === 'tag'){ const t = whTagClean(S.el.querySelector('.wh-smenu [data-wh-mtag]').value); if(t) m.tag = t; else delete m.tag;",
     "  if(k === 'tag'){ const t = whTagClean(S.el.querySelector('.wh-smenu [data-wh-mtag]').value); for(const g of (whGroupOf(n) || [])) (S.mk[g] = S.mk[g] || {}).tag = t; if(t) m.tag = t; else delete m.tag;", ('group',)),
    ('no Delete key', "    if(whDelKey()) ev.preventDefault();", "    return;", ('key',)),
    ('Delete acting inside a text field', "|| a.matches('input, textarea, select, [contenteditable], [contenteditable] *') || a.closest('.wh-menu, .wh-pop, .wh-pnl')) return;", ") return;", ('key',)),
    ('the Delete key\'s menu at another system', "const n = ids.includes(M.last) ? M.last : ids.includes(S.sel) ? S.sel : ids[ids.length - 1]", "const n = ids[0]", ('key',)),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, 'removing systems: the question inside the map, the selection\'s Remove, the Delete key, a phone')
    check(not errs, f'no page errors {errs[:3]}')
    for name, old, new, parts in MUTANTS:
        if PAGE.count(old) != 1: check(False, f'mutant "{name}": its line isn\'t in the page once ({PAGE.count(old)})'); continue
        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f:
            f.write(PAGE.replace(old, new)); mp = f.name
        try:
            try: mo, me = cases(b, mp, parts)
            except Exception as e: mo, me = [f'the check stopped: {str(e).splitlines()[0]}'], []   # the mutant broke a later step: caught
            check(bool(mo) or bool(me), f'mutant "{name}" fails ({(mo or me or ["nothing"])[0][:90]})')
        finally: os.unlink(mp)
    b.close()
print('FAILURES:', NS['fails'])
sys.exit(1 if NS['fails'] else 0)
