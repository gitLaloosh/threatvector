"""Every box where one system is typed and added shows the map search's suggestion list (build queue 066; the owner: "all input fields that allow the
entry of a system name should use the helper to identify real systems like the intel map does", then at the review "Fill the box (Recommended)",
"Leave it out (Recommended)" for the "word = system" shorthands, "No mockup (Recommended)").

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/system_boxes_check.py [index.html]   -> 'FAILURES: N' (must be 0)
    (SB_FAST=1 skips the mutants.)

Uses intel_check.py's made-up folder, mocks and names (you in 1DQ1-A; QX-LIJ among the real dashed names it gives) and CCP's own J-space table.
The five boxes: Intel's Wormholes list -> Add, Intel settings -> Routes -> Avoid (k-space); the Wormholes tab's + Add, "Add a system here" and
Routes -> Pin (J-space too). Each:
  * a name typed without its "-" ("qxli") lists QX-LIJ first, in the map search's list (.it-rp-sug, a combobox: aria-expanded, aria-controls);
    on the Wormholes tab a J-space name lists J-space rows with their class;
  * Enter (or a press on a row) fills the box with the name and shuts the list, and adds nothing yet; Enter again does the box's action;
    a name typed in full acts on its first Enter, as before 066;
  * an unknown name still gets the box's own refusal;
  * the list is on top (the row under its own centre is the row) and inside the window; 44 px rows at 390 px;
  * the shorthand box, the paste boxes and the Feed search have no list (the owner: left out);
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
QX = SYSID['QX-LIJ']

def start(b, html, w, errs, h=1000, touch=False):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch, device_scale_factor=2 if touch else 1)
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); route(ctx)
    pg = ctx.new_page(); pg.goto('file://' + html)
    pg.evaluate("(s) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({channels: ['region.intel'], me: 95000001, range: 3, sound: false, notify: false, forget: 15})); }", SIDE)
    pg.reload(); pg.wait_for_timeout(400)
    setup_logs(pg); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg, 3200)
    if not pg.evaluate("!!it.names"): pg.evaluate("itLoadNames()"); pg.wait_for_timeout(300)
    return ctx, pg

# the list under a box: shown, its rows' names (and the dim text), on top, inside the window, the rows' height
LIST = """(sel) => { const inp = document.querySelector(sel); if(!inp) return null; const box = inp.closest('.sys-cb'), ul = box && box.querySelector('.it-rp-sug');
  if(!ul) return {none: true};
  const lis = [...ul.querySelectorAll('[data-sys-pick]')], r = ul.getBoundingClientRect();
  let top = false; if(lis.length){ lis[0].scrollIntoView({block: 'nearest'}); const q = lis[0].getBoundingClientRect(), at = document.elementFromPoint(q.left + q.width / 2, q.top + q.height / 2); top = !!at && lis[0].contains(at); }
  return {shown: !ul.hidden, names: lis.map(li => li.querySelector('.it-sn') ? li.querySelector('.it-sn').textContent : li.childNodes[0].textContent.trim()), dims: lis.map(li => (li.querySelector('.d') || {}).textContent || ''),
    exp: inp.getAttribute('aria-expanded'), ctl: inp.getAttribute('aria-controls') === ul.id && !!ul.id, role: inp.getAttribute('role'), cls: ul.className, top,
    inView: r.left >= -1 && r.right <= innerWidth + 1, h: lis.length ? Math.round(lis[0].getBoundingClientRect().height) : 0}; }"""

def typed(pg, sel, text):
    pg.click(sel); pg.fill(sel, ''); pg.keyboard.type(text); pg.wait_for_timeout(250)
    return pg.evaluate(LIST, sel)

def box(pg, w, label, sel, did, want=('QX-LIJ', QX), unknown=None):
    """one box: the list for "qxli", Enter fills, Enter again acts (did() says whether the action happened), an unknown name refused"""
    out = []
    L = typed(pg, sel, 'qxli')
    if not L or L.get('none'): return [f'{w}: {label}: no suggestion list ({L})']
    if not L['shown'] or not L['names'] or L['names'][0] != want[0] or L['exp'] != 'true' or not L['ctl'] or L['role'] != 'combobox' or L['cls'] != 'it-rp-sug':
        out.append(f'{w}: {label}: the list for "qxli": {L}')
    if not L['top'] or not L['inView']: out.append(f'{w}: {label}: the list is covered or cut off: on top {L["top"]}, inside the window {L["inView"]}')
    if w < 600 and L['h'] < 44: out.append(f'{w}: {label}: a row is {L["h"]} px (want 44 on a phone)')
    pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
    v = pg.evaluate("(sel) => { const i = document.querySelector(sel); return i ? [i.value, i.closest('.sys-cb').querySelector('.it-rp-sug').hidden, document.activeElement === i] : null; }", sel)
    if v != [want[0], True, True]: out.append(f'{w}: {label}: Enter on the list fills the box and shuts the list: {v}')
    if did(pg): out.append(f'{w}: {label}: a pick acted at once (want it only to fill the box)')
    pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
    if not did(pg): out.append(f'{w}: {label}: Enter again doesn\'t do the box\'s action')
    if unknown:
        sel2, msg = unknown
        pg.click(sel); pg.fill(sel, ''); pg.keyboard.type('nowhere special'); pg.wait_for_timeout(200)
        n = pg.evaluate("(sel) => document.querySelector(sel).closest('.sys-cb').querySelector('.it-rp-sug').textContent", sel)
        if 'No system by that name' not in n: out.append(f'{w}: {label}: the list for an unknown name: {n!r}')
        pg.keyboard.press('Enter'); pg.wait_for_timeout(250)
        t = pg.evaluate("(s) => { const e = document.querySelector(s); return e ? e.textContent : null; }", sel2)
        if not t or msg not in t: out.append(f'{w}: {label}: an unknown name refused: {t!r} (want {msg!r})')
    return out

def cases(b, html, parts=('whl', 'avoid', 'whole', 'add', 'here', 'pin', 'left', 'phone')):
    out, errs = [], []
    ctx, pg = start(b, html, 1440, errs)
    if not pg.evaluate("typeof sysCbBind === 'function'"): out.append('no sysCbBind on the page'); ctx.close(); return out, errs
    J = pg.evaluate("() => { const T = whTable(), i = T.names.findIndex(n => /^J\\d{6}$/.test(n)); return [T.ids[i], T.names[i]]; }")
    if 'whl' in parts:
        pg.evaluate("() => { delete itWhStore().rep[%d]; delete itWhStore().gone[%d]; itWhSave(); itWhListOpen(true); }" % (QX, QX)); pg.wait_for_timeout(250)
        out += box(pg, 1440, "Intel's Wormholes list -> Add", '.it-whp-add input[name=sys]', lambda pg: pg.evaluate("(q) => !!itWhStore().rep[q]", QX),
                   unknown=('.it-whp-msg', 'isn'))
        pg.evaluate("itWhListOpen(false, false)")
    if 'avoid' in parts:
        pg.evaluate("() => { const r = JSON.parse(localStorage.getItem('tvRoute') || '{}'); if(r.list){ r.list = r.list.filter(x => x !== %d); localStorage.setItem('tvRoute', JSON.stringify(r)); } it.pop = true; itRender(true); }" % QX); pg.wait_for_timeout(250)
        out += box(pg, 1440, 'Routes -> Avoid', '[data-it-rp-box] .it-rp-add input[name=sys]', lambda pg: QX in (pg.evaluate("JSON.parse(localStorage.getItem('tvRoute') || '{}').list") or []),
                   unknown=('[data-it-rp-box] .it-rp-msg', 'nowhere special'))
        pg.evaluate("() => { it.pop = false; itRender(true); }"); pg.wait_for_timeout(150)
    if 'whole' in parts:   # a name typed in full: the first Enter acts, as before 066 (wormhole_tab_check's way)
        pg.evaluate("() => { delete itWhStore().rep[%d]; delete itWhStore().gone[%d]; itWhSave(); itWhListOpen(true); }" % (QX, QX)); pg.wait_for_timeout(250)
        L = typed(pg, '.it-whp-add input[name=sys]', 'qx-lij'); pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
        if not pg.evaluate("(q) => !!itWhStore().rep[q]", QX): out.append(f'a name typed in full ("qx-lij") is added on the first Enter (list: {L and L.get("names")})')
        pg.evaluate("itWhListOpen(false, false)")
    if any(x in parts for x in ('add', 'here', 'pin')):
        pg.evaluate("switchTab('wh')"); pg.wait_for_timeout(300)
    if 'add' in parts:
        pg.click('[data-wh-pop="add"]'); pg.wait_for_timeout(200)
        L = typed(pg, '.wh-addf input[name=sys]', J[1][:4].lower())
        if not L or not L.get('names') or not all(re.fullmatch(r'J\d{6}', n) for n in L['names'][:3]) or not all(re.fullmatch(r'C\d|[A-Z][a-z]+.*|\?', d.strip()) for d in L['dims'][:3]):
            out.append(f"+ Add: J-space rows with their class for {J[1][:4].lower()!r}: {L}")
        pg.fill('.wh-addf input[name=sys]', '')
        out += box(pg, 1440, "the Wormholes tab's + Add", '.wh-addf input[name=sys]', lambda pg: pg.evaluate("(q) => !!whState().st.sys[q]", QX),
                   unknown=('.wh-msg', 'isn’t a wormhole system'))
    if 'here' in parts:
        pg.evaluate("([q, j]) => { whRemoveSys(q); if(!whState().st.sys[j]) whAddSys(j, Date.now()); whSave(); whPaint(true); whHereOpen(60, 60); }", [QX, J[0]]); pg.wait_for_timeout(200)   # a system first: an empty map has no view yet
        out += box(pg, 1440, '"Add a system here"', '.wh-here input[name=sys]', lambda pg: pg.evaluate("(q) => !!whState().st.sys[q]", QX))
    if 'pin' in parts:
        pg.evaluate("(j) => { if(!whState().st.sys[j]) whAddSys(j, Date.now()); whSave(); const R = whRtState(); R.pins = R.pins.filter(x => x !== %d); whPnSet('rt'); whPaint(true); }" % QX, J[0]); pg.wait_for_timeout(300)
        out += box(pg, 1440, 'Routes -> Pin', '#whPnRt [data-wh-rt-pin] input[name=sys]', lambda pg: pg.evaluate("(q) => whRtState().pins.includes(q)", QX))
        pg.evaluate("() => { whPnSet(''); whPaint(true); }")
    if 'left' in parts:   # the owner: left out of it
        pg.evaluate("switchTab('intel')"); pg.wait_for_timeout(200)
        pg.evaluate("() => { it.pop = true; itRender(true); }"); pg.wait_for_timeout(250)
        n = pg.evaluate("() => [!!document.querySelector('[data-it-alias]'), !!document.querySelector('[data-it-alias]') && !!document.querySelector('[data-it-alias]').closest('.sys-cb'), document.querySelectorAll('textarea.sys-cb, .sys-cb > textarea').length, !!(document.querySelector('[data-it-q]') || {closest: () => null}).closest('.sys-cb')]")
        if n[1] or n[2] or n[3]: out.append(f'the shorthands, a paste box or the Feed search got the list (left out): {n}')
        pg.evaluate("() => { it.pop = false; itRender(true); }")
    ctx.close()
    if 'phone' in parts:
        ctx, pg = start(b, html, 390, errs, h=844, touch=True)
        pg.evaluate("() => { delete itWhStore().rep[%d]; delete itWhStore().gone[%d]; itWhSave(); itWhListOpen(true); }" % (QX, QX)); pg.wait_for_timeout(300)
        out += box(pg, 390, "Intel's Wormholes list -> Add", '.it-whp-add input[name=sys]', lambda pg: pg.evaluate("(q) => !!itWhStore().rep[q]", QX))
        pg.evaluate("itWhListOpen(false, false)"); pg.evaluate("switchTab('wh')"); pg.wait_for_timeout(300)
        pg.click('[data-wh-pop="add"]'); pg.wait_for_timeout(250)
        out += box(pg, 390, "the Wormholes tab's + Add", '.wh-addf input[name=sys]', lambda pg: pg.evaluate("(q) => !!whState().st.sys[q]", QX))
        if not pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"): out.append('390: the page scrolls sideways')
        ctx.close()
    return out, errs

MUTANTS = [
    ('Avoid left without the list', '<form class="it-rp-add" autocomplete="off"><span class="sys-cb"><input type="text" name="sys" placeholder="System, e.g. 8BA-RA"', '<form class="it-rp-add" autocomplete="off"><span><input type="text" name="sys" placeholder="System, e.g. 8BA-RA"', ('avoid',)),
    ('Pin left without the list', '<form class="it-rp-add" data-wh-rt-pin autocomplete="off"><span class="sys-cb" data-scope="all">', '<form class="it-rp-add" data-wh-rt-pin autocomplete="off"><span data-scope="all">', ('pin',)),
    ('the Wormholes tab\'s boxes stargate-only', "const scope = box.dataset.scope === 'all' ? 'all' : 'k'", "const scope = 'k'", ('add',)),
    ('Enter with the list shut no longer sends the form', "    enter: () => {}});   // the list shut", "    });   // the list shut", ('whl',)),
    ('a pick acts at once', "inp.value = nm; inp.focus(); if(whole && inp.form) inp.form.requestSubmit(); },", "inp.value = nm; inp.focus(); if(inp.form) inp.form.requestSubmit(); },", ('here',)),
    ('a name typed in full needs a second Enter', "inp.value = nm; inp.focus(); if(whole && inp.form) inp.form.requestSubmit(); },", "inp.value = nm; inp.focus(); },", ('whole',)),
    ('the list under what follows it', "  .sys-cb > .it-rp-sug{position:absolute; left:0; right:0; top:100%; z-index:8; min-width:200px;}", "  .sys-cb > .it-rp-sug{position:absolute; left:0; right:0; top:100%; z-index:-1; min-width:200px;}", ('add',)),
    ('never bound', "if(t && t.matches && t.matches('.sys-cb > input') && sysCbBind(t)", "if(false && sysCbBind(t)", ('whl',)),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, f'the system boxes suggest real systems ({len(out)} problems)')
    check(not errs, f'no page errors ({errs[:2]})')
    if not os.environ.get('SB_FAST'):
        for name, a, bb, parts in MUTANTS:
            if PAGE.count(a) != 1: check(False, f'mutant "{name}": its text is in the page ({PAGE.count(a)})'); continue
            with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f: f.write(PAGE.replace(a, bb)); mp = f.name
            try:
                mo, me = cases(b, mp, parts)
                check(bool(mo) or bool(me), f'mutant caught: {name}' + (f' ({mo[0][:90]})' if mo else ''))
            finally: os.unlink(mp)
    b.close()
print(f'FAILURES: {NS["fails"]}')
sys.exit(1 if NS['fails'] else 0)
