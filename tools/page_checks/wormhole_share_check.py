"""The Wormholes list's Export and Import (build queue 046, roadmap/wormholes-export-import-plan.md; the owner: "plan a change to the wormholes
list panel that allows you to export from and import to your wormhole list. import should have de-dupe/merge logic to ensure that any pre-existing
holes are only added to and not duplicated or lose data.").

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/wormhole_share_check.py [index.html]   -> 'FAILURES: N' (must be 0)
    (SHARE_FAST=1 skips the mutants, for a quick look while working.)

Uses intel_check.py's made-up folder, mocks and names (you in 1DQ1-A); every pilot, ticker and line is made up. Two browsers: A (Intel running,
its lines through the made-up folder, one hole added by hand) and B (another player's list, set up in its store). Checks:
  * Export: the box opens with the JSON selected; no reporter, pilot or ticker anywhere in it (default-deny: a pilot in a wormhole line, a ticker in
    brackets, a two-word name, a pilot after "wh"), while systems, ships, IDs, types and detail words stay; the same list exports the same text;
    Copy fills the clipboard (granted) and says Copied!; refused, the text stays selected with the Ctrl+C line;
  * round trip: A's export into an empty B: the same systems, IDs, details and (redacted) lines; the preview first; importing it again: "Nothing new";
  * the merge: your hand value kept against a newer shared report, which shows as "!"; a report-only detail takes the newer report; a part
    completes to the whole ID; Drifter stays; an ID you removed stays removed against an older line and comes back with a newer one; a system you
    removed likewise; a detail with no line (saved before 044) kept; the same report from both sides one line (your names kept, the count the larger);
    the 10-line cap keeps a line that still decides a detail; a repeat of your own Intel line is one line "×2";
  * imported holes act like Intel's reports (the owner: "i think so") and say they're from a shared list;
  * the checks on import: wrong tv, newer v, 300 KB, an unknown system, a mismatched name, a time 3 days old, a time in the future, a bad ID, an
    unknown type, HTML in a line: refused or skipped and counted, nothing run, nothing saved; Cancel changes nothing;
  * the UI: the chevrons turn with aria-expanded, one box at a time, focus into the box and back, Esc closes the list, 44 px and no sideways scroll at
    390 px; a new Intel line redrawing the card keeps the open list where it was scrolled to and the Add field's focus and text (047), and the page where it was scrolled to (the map in
    view, down in the Feed, a short window; 047's hand test);
  * mutants, each must fail: lines matched by time instead of text; theirs kept over yours; the cap dropping a line that decides a detail; the
    reporter written into the export; an older line bringing back a removed ID; the page creeping with each redraw;
  * no page errors.
"""
import sys, os, json, time, tempfile
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
near = sorted((s for s, v in D0.items() if 1 <= v <= 4), key=lambda s: (D0[s], s))
HOST = M.PILOTS[M.pick(98000003, 0)][0]
SIGS = "(id) => { const w = itWhStore().rep[id]; return w ? (w.sigs || []).map(s => s.sig + (s.part ? '~' : '') + (s.type ? ':' + s.type : '') + (s.dr ? '!' : '')) : null; }"

def start(b, html, errs, W=1440, H=1000, intel=True, perm=True):
    ctx = b.new_context(bypass_csp=True, viewport={'width': W, 'height': H})
    if perm: ctx.grant_permissions(['clipboard-read', 'clipboard-write'])
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); route(ctx)
    pg = ctx.new_page(); pg.goto('file://' + html)
    pg.evaluate("(s) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({channels: ['region.intel'], me: 95000001, range: 3, forget: 15})); }", SIDE)
    pg.reload(); pg.wait_for_timeout(400)
    setup_logs(pg); pg.click('#tabBtnIntel'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg)
    if not intel: pg.evaluate("() => { localStorage.removeItem('tvWormholes'); itWhSt = null; itWhChanged(); }")   # another player's browser: no wormholes yet
    return ctx, pg

def open_list(pg):
    pg.evaluate("() => { itMapFilterSet('wh'); itWhListOpen(true); }"); pg.wait_for_timeout(250)

def export(pg):
    open_list(pg)
    if pg.get_attribute('[data-it-whxb="exp"]', 'aria-expanded') != 'true': pg.click('[data-it-whxb="exp"]')
    pg.wait_for_function("document.querySelector('#itWhExp textarea').value.length > 0", timeout=10000)
    return pg.evaluate("document.querySelector('#itWhExp textarea').value")

def preview(pg, text):
    open_list(pg)
    if pg.get_attribute('[data-it-whxb="imp"]', 'aria-expanded') != 'true': pg.click('[data-it-whxb="imp"]')
    pg.fill('#itWhImp textarea', text); pg.click('[data-it-whimp]'); pg.wait_for_timeout(400)
    return pg.evaluate("() => { const b = document.querySelector('#itWhImp'); return [b.querySelector('.it-whp-prev').hidden ? '' : b.querySelector('.it-whp-prev').innerText, b.querySelector('.it-whp-bs').textContent]; }")

def add(pg):
    pg.click('[data-it-whadd]'); pg.wait_for_timeout(300)
    return pg.evaluate("document.querySelector('.it-whp-msg').textContent")

# B's own list, set up in its store: what another player had before importing
SEED_B = """([ids, nm, now]) => {
  const [P, Q, R, S, T, U, V] = ids, m = 60000, set = (sigs, info, dr) => itWhSetOf(sigs.map(x => itWhSigNew(...x)), info, dr);
  const line = (t, raw, k, who, s) => ({t, who: who || '', raw, k: k || 'intel', set: s});
  const rep = {};
  // P: RZL-429, your own value: mass more than 50% (added by you, older than A's reports)
  rep[P] = {id: P, t: now - 50 * m, who: '', drifter: false, src: 'you', sigs: [{...itWhSigNew('RZL-429', false, 'Z971', false, {mass: 'stable'}), t: now - 50 * m, who: '', src: 'you'}],
    raws: [line(now - 50 * m, `${nm[0]} RZL-429 Z971 mass >50%`, 'you', '', set([['RZL-429', false, 'Z971', false, {mass: 'stable'}]]))]};
  // Q: a part, QDX, from your own Intel
  rep[Q] = {id: Q, t: now - 40 * m, who: 'B Scout', drifter: false, src: 'intel', sigs: [{...itWhSigNew('QDX', true, '', false), t: now - 40 * m, who: 'B Scout'}],
    raws: [line(now - 40 * m, `${nm[1]} wh sig QDX`, 'intel', 'B Scout', set([['QDX', true, '', false]]))]};
  // R: KLM-204 removed by you 20 minutes ago (its report was 30 minutes ago); XRT-331 kept
  rep[R] = {id: R, t: now - 30 * m, who: 'B Scout', drifter: false, src: 'intel', sigs: [{...itWhSigNew('XRT-331', false, '', false), t: now - 30 * m, who: 'B Scout'}],
    goneSig: {'KLM-204': now - 20 * m}, raws: [line(now - 30 * m, `${nm[2]} wh XRT-331 KLM-204`, 'intel', 'B Scout', set([['XRT-331', false, '', false], ['KLM-204', false, '', false]]))]};
  // T: saved before 044 (no lines), with a mass you can't trace to a line
  rep[T] = {id: T, t: now - 25 * m, who: 'B Scout', drifter: false, src: 'intel', sigs: [], info: {mass: 'critical'}};
  // U: ten lines; the oldest (yours) still decides ABC-123's size
  const ul = [line(now - 45 * m, `${nm[5]} ABC-123 large`, 'you', '', set([['ABC-123', false, '', false, {size: 'large'}]]))];
  for(let i = 1; i < 10; i++) ul.unshift(line(now - (45 - i) * m, `${nm[5]} wh ping ${i}`, 'intel', 'B Scout', set([])));
  rep[U] = {id: U, t: now - 36 * m, who: 'B Scout', drifter: false, src: 'intel', sigs: [{...itWhSigNew('ABC-123', false, '', false, {size: 'large'}), t: now - 45 * m, who: '', src: 'you'}], raws: ul};
  const st = {v: 1, rep, gone: {[S]: now - 15 * m}, keepH: 24};   // S: you removed it 15 minutes ago
  localStorage.setItem('tvWormholes', JSON.stringify(st)); itWhSt = null; itWhChanged();
}"""

# A's export, made in the page from these entries (another player's newer and older reports)
FRIEND = """([ids, nm, now]) => {
  const [P, Q, R, S, T, U, V] = ids, m = 60000;
  const ln = (t, raw, sigs, info, dr, k, n) => ({t, k: k || 'intel', raw, set: itWhSetOf(sigs.map(x => itWhSigNew(...x)), info, dr), n: n || 1});
  const sys = (id, t, raws, sigs) => ({id, name: itSysName(id), t, sigs: sigs || [], raws});
  return JSON.stringify({tv: 'wormholes', v: 1, made: now, sys: [
    sys(P, now - 10 * m, [ln(now - 10 * m, `${nm[0]} wh RZL crit`, [['RZL', true, '', false, {mass: 'critical'}]]), ln(now - 12 * m, `${nm[0]} wh RZL eol`, [['RZL', true, '', false, {life: 'eol'}]])]),
    sys(Q, now - 20 * m, [ln(now - 20 * m, `${nm[1]} wormhole QDX-581 n110`, [['QDX-581', false, 'N110', false]]), ln(now - 40 * m, `${nm[1]} wh sig QDX`, [['QDX', true, '', false]], null, false, 'intel', 3)]),
    sys(R, now - 5 * m, [ln(now - 35 * m, `${nm[2]} wh KLM-204`, [['KLM-204', false, '', false]]), ln(now - 5 * m, `${nm[2]} drifter BKT-772`, [['BKT-772', false, '', true]])]),
    sys(S, now - 18 * m, [ln(now - 18 * m, `${nm[3]} wh`, [])]),
    sys(T, now - 3 * m, [ln(now - 3 * m, `${nm[4]} wh reduced`, [], {mass: 'reduced'})]),
    sys(U, now - 2 * m, [ln(now - 2 * m, `${nm[5]} wh new 1`, []), ln(now - 3 * m, `${nm[5]} wh new 2`, []), ln(now - 4 * m, `${nm[5]} wh ABC-123 small`, [['ABC-123', false, '', false, {size: 'small'}]])]),
    sys(V, now - 6 * m, [ln(now - 6 * m, `${nm[6]} GHI-123 C247`, [['GHI-123', false, 'C247', false]], null, false, 'hand')]),
  ]});
}"""

def cases(b, html, phone=True):
    out, errs = [], []
    # ---- A: Intel running, lines through the made-up folder
    ca, pa = start(b, html, errs)
    if not pa.evaluate("typeof itWhExportObj === 'function'"): out.append('no export'); ca.close(); return out, errs
    taken = set(pa.evaluate("[...it.near.keys()]"))
    S = [x for x in near if x not in taken][:10]; N = {x: SYSNAME[x] for x in S}
    A0, A1, A2, A3 = S[:4]
    t = time.time()
    lines = [('Gate Watcher', f'{N[A0]} wh rzl-429 z971 class 1-3 medium size less then 1 day less then 50% mass'),
             ('Scout Alt', f'{N[A0]} wh {HOST} [MKRC] sig MKV crit rifter'),
             ('Gate Watcher', f'{N[A1]} drifter hole BKT772 Mk Friendly Name sabre'),
             ('Scout Alt', f'{N[A2]} wh'), ('Gate Watcher', f'{N[A2]} wh')]
    body = ''.join(line(t + 2 * k, who, msg) for k, (who, msg) in enumerate(lines))
    W(pa, F_INTEL, body); tick(pa, 3200)
    rep = pa.evaluate("(id) => (itWhStore().rep[id].raws || []).map(r => [r.n || 1, r.raw])", A2)
    if len(rep) != 1 or rep[0][0] != 2: out.append(f'a repeat of your own Intel line should be one line ×2: {rep}')
    open_list(pa)
    pa.fill('.it-whp-add input[name=sys]', N[A3]); pa.fill('.it-whp-add input[name=sig]', 'ghi-123'); pa.fill('.it-whp-add input[name=ty]', 'c247'); pa.click('.it-whp-add button[type=submit]'); pa.wait_for_timeout(300)
    j1 = export(pa)
    sel = pa.evaluate("(() => { const ta = document.querySelector('#itWhExp textarea'); return document.activeElement === ta && ta.selectionStart === 0 && ta.selectionEnd === ta.value.length; })()")
    if not sel: out.append('Export: the JSON should be focused and selected')
    for bad in ['Gate Watcher', 'Scout Alt', HOST, 'MKRC', 'Mk Friendly', 'Friendly Name']:
        if bad.lower() in j1.lower(): out.append(f'Export leaks a name: {bad!r}')
    for good in [N[A0], 'rzl-429', 'z971', 'class', '1-3', 'MKV', 'crit', 'rifter', 'BKT772', 'sabre', 'GHI-123', 'C247', '<a pilot>']:
        if good.lower() not in j1.lower(): out.append(f'Export lost {good!r}')
    if '"who"' in j1: out.append('Export writes a reporter field')
    pa.click('[data-it-whxb="exp"]'); pa.wait_for_timeout(200)
    j2 = export(pa)
    strip = lambda j: {k: v for k, v in json.loads(j).items() if k != 'made'}
    if strip(j1) != strip(j2): out.append('the same list should export the same text')
    pa.click('[data-it-whcopy]'); pa.wait_for_timeout(400)
    clip = pa.evaluate("navigator.clipboard.readText()")
    if clip != j2 or pa.inner_text('[data-it-whcopy]') != 'Copied!': out.append(f'Copy: the clipboard ({len(clip)} chars) or the button ({pa.inner_text("[data-it-whcopy]")!r})')
    # one box at a time; focus back on the button; the chevron turns with aria-expanded
    pa.click('[data-it-whxb="imp"]'); pa.wait_for_timeout(200)
    st = pa.evaluate("[document.querySelector('#itWhExp').hidden, document.querySelector('#itWhImp').hidden, document.querySelector('[data-it-whxb=\"exp\"]').getAttribute('aria-expanded'), document.activeElement === document.querySelector('#itWhImp textarea'), getComputedStyle(document.querySelector('[data-it-whxb=\"imp\"] svg')).transform]")
    if st[:4] != [True, False, 'false', True] or st[4] in ('none', ''): out.append(f'one box at a time, focus into it, the chevron turned: {st}')
    pa.click('[data-it-whxb="imp"]'); pa.wait_for_timeout(150)
    if not pa.evaluate("document.activeElement === document.querySelector('[data-it-whxb=\"imp\"]')"): out.append('closing a box should return focus to its button')
    # 047 (the owner, after 046: "when the feed updates and the page re-draws, the wormhole list automatically scrolls to the top and the user
    # keeps losing their place in the list"): a long list scrolled down, the Add field being typed in, then a new Intel line redraws the card
    many = [x for x in sorted(D0, key=lambda s: (D0[s], s)) if 5 <= D0[x] <= 9 and x not in taken][:30]
    pa.evaluate("(ids) => { const st = itWhStore(), now = Date.now(); ids.forEach((id, k) => st.rep[id] = {id, t: now - (k + 1) * 1000, who: '', drifter: false, src: 'you'}); itWhSave(); itWhChanged(); }", many)
    pa.evaluate("() => { itWhL.el.scrollTop = 0; }")
    pa.click('.it-whp-add input[name=sys]'); pa.keyboard.type('Ta')
    pa.evaluate("() => { itWhL.el.scrollTop = 350; }"); top0 = pa.evaluate("itWhL.el.scrollTop")
    # 047, the owner's hand test ("it's like the page is slowly creeping up every time the feed refreshes"): the page scrolled into the map
    pa.evaluate("() => { const r = itm.el.getBoundingClientRect(); window.scrollTo(0, scrollY + r.top + 120); }"); y0 = pa.evaluate("scrollY")
    draws = pa.evaluate("window.__d = 0; const f = itRender; itRender = function(){ window.__d++; return f.apply(this, arguments); }; 0")
    W(pa, F_INTEL, body + line(time.time(), 'Gate Watcher', f'{SYSNAME[near[0]]} Seren Ketter sabre')); tick(pa, 3200)
    ks = pa.evaluate("[window.__d, itWhListShown(), itWhL.el.scrollTop, document.activeElement && document.activeElement.name, document.activeElement && document.activeElement.value]")
    keep = "[scrollY, itm.el.getBoundingClientRect().top, document.querySelector('#itFeedList').getBoundingClientRect().top, window.__d]"
    p0 = pa.evaluate(keep)
    if y0 < 100 or abs(p0[0] - y0) > 1: out.append(f'a redraw should leave the page where it was scrolled to: {y0} -> {p0[0]}')
    for k in range(3):
        W(pa, F_INTEL, body + line(time.time(), 'Gate Watcher', f'{SYSNAME[near[k + 1]]} Seren Ketter sabre')); tick(pa, 3200)
    p1 = pa.evaluate(keep)
    if p1[3] - p0[3] < 3 or abs(p1[0] - p0[0]) > 1 or abs(p1[1] - p0[1]) > 1: out.append(f'the page should not creep with the feed\'s redraws: scrolled {p0[0]} -> {p1[0]}, map at {p0[1]:.0f} -> {p1[1]:.0f} ({p1[3] - p0[3]} redraws)')
    # down in the Feed, and a short window with the map half above it
    for vp, at in (({'width': 1440, 'height': 1000}, "document.querySelector('#itFeedList')"), ({'width': 1000, 'height': 600}, "itm.el")):
        pa.set_viewport_size(vp); pa.wait_for_timeout(300)
        pa.evaluate(f"() => {{ const r = {at}.getBoundingClientRect(); window.scrollTo(0, scrollY + r.top + 250); }}"); q0 = pa.evaluate(keep)
        for k in range(2):
            W(pa, F_INTEL, body + line(time.time(), 'Gate Watcher', f'{SYSNAME[near[k + 4 + (vp["height"] < 900) * 2]]} Seren Ketter sabre')); tick(pa, 3200)
        q1 = pa.evaluate(keep)
        if q1[3] == q0[3] or abs(q1[0] - q0[0]) > 1 or abs(q1[1] - q0[1]) > 1: out.append(f'{vp["width"]} x {vp["height"]}, scrolled into {at}: the page {q0[0]} -> {q1[0]}, map {q0[1]:.0f} -> {q1[1]:.0f} ({q1[3] - q0[3]} redraws)')
    pa.set_viewport_size({'width': 1440, 'height': 1000}); pa.wait_for_timeout(200)
    if top0 < 300 or ks[0] < 1: out.append(f'the scroll test needs a long list and a redraw: scrolled {top0}, redraws {ks[0]}')
    elif not ks[1] or abs(ks[2] - top0) > 2 or ks[3] != 'sys' or ks[4] != 'Ta': out.append(f'a redraw while the list is open: shown {ks[1]}, scroll {top0} -> {ks[2]}, focus {ks[3]!r} {ks[4]!r}')
    pa.keyboard.press('Escape'); pa.wait_for_timeout(150)
    if pa.evaluate("itWhListShown()"): out.append('Esc should close the list')
    ca.close()
    # ---- B: an empty list, then the round trip
    cb, pb = start(b, html, errs, intel=False)
    pv, msg = preview(pb, j1)
    nsys = len(json.loads(j1)['sys'])
    if not pv.startswith(f'Adds {nsys} systems'): out.append(f'the preview: {pv!r} {msg!r}')
    if pb.evaluate("Object.keys(itWhStore().rep).length"): out.append('the preview changed the store')
    m = add(pb)
    got = pb.evaluate("() => Object.values(itWhStore().rep).map(w => [w.id, (w.sigs || []).map(s => s.sig).sort().join(','), (w.raws || []).length, w.via || '', w.who]).sort()")
    exp = sorted([[x['id'], ','.join(sorted(s['sig'] for s in x['sigs'])), len(x['raws']), 'import', '<a pilot>' if x['raws'][0]['k'] == 'intel' else ''] for x in json.loads(j1)['sys']])
    if [g[:3] for g in got] != [e[:3] for e in exp] or any(g[3] != 'import' for g in got): out.append(f'the round trip: {got} vs {exp} ({m!r})')
    j3 = export(pb)
    if [(x['id'], x['raws']) for x in json.loads(j3)['sys']] != [(x['id'], x['raws']) for x in json.loads(j1)['sys']]: out.append(f"exported again, the lines should read the same: {[(x['id'], x['raws']) for x in json.loads(j3)['sys']]} vs {[(x['id'], x['raws']) for x in json.loads(j1)['sys']]}")
    pv, msg = preview(pb, j1)
    if not pv.startswith(f'Nothing new: you already have {nsys}'): out.append(f'importing again: {pv!r}')
    # imported ones act like Intel's reports, and say they're from a shared list
    live = pb.evaluate("(id) => { const w = itWhNear(id); return w ? itWhBadgeTitle(w) : null; }", A0)
    if not live or 'from a shared list, reported by <a pilot>' not in live: out.append(f'an imported fresh report should be live and say so: {live!r}')
    cb.close()
    # ---- B with its own list: the merge
    cb, pb = start(b, html, errs, intel=False)
    P, Q, R, Sx, T, U, V = S[3:10]
    ids = [P, Q, R, Sx, T, U, V]; nm = [SYSNAME[x] for x in ids]
    now = pb.evaluate("Date.now()")
    pb.evaluate(SEED_B, [ids, nm, now])
    jf = pb.evaluate(FRIEND, [ids, nm, now])
    pv, msg = preview(pb, jf)
    if 'kept yours for 2' not in pv or 'removed by you' not in pv: out.append(f'the merge preview: {pv!r} {msg!r}')
    before = pb.evaluate("localStorage.getItem('tvWormholes')")
    pb.click('[data-it-whcancel]'); pb.wait_for_timeout(150)
    if pb.evaluate("localStorage.getItem('tvWormholes')") != before: out.append('Cancel changed the store')
    pb.click('[data-it-whimp]'); pb.wait_for_timeout(300); add(pb)
    rz = pb.evaluate("(id) => itWhStore().rep[id].sigs.map(s => [s.sig, s.info || null, s.note ? s.note.v : null])", P)
    if rz != [['RZL-429', {'mass': 'stable', 'life': 'eol'}, 'critical']]: out.append(f'your value kept, the newer shared one a note, a report-only detail added: {rz}')
    if pb.locator(f'.it-whp-rows .it-signote').count() < 1: out.append('the note "!" isn\'t shown in the list')
    if pb.evaluate(SIGS, Q) != ['QDX-581:N110']: out.append(f'a part should complete to the whole ID: {pb.evaluate(SIGS, Q)}')
    qn = pb.evaluate("(id) => itWhStore().rep[id].raws.map(r => [r.raw, r.n || 1, r.who])", Q)
    q0 = [x for x in qn if 'wh sig qdx' in x[0].lower()]
    if len(q0) != 1 or q0[0][1] != 3 or q0[0][2] != 'B Scout': out.append(f'the same report from both sides is one line, yours kept, the larger count: {qn}')
    rr = pb.evaluate(SIGS, R)
    if 'KLM-204' in rr or 'BKT-772!' not in rr or not pb.evaluate("(id) => itWhStore().rep[id].drifter", R): out.append(f'an ID you removed stays removed against an older line; Drifter kept: {rr}')
    if pb.evaluate("(id) => !!itWhStore().rep[id]", Sx): out.append('a system you removed came back from an older report')
    if pb.evaluate("(id) => (itWhStore().rep[id].info || {}).mass", T) != 'critical': out.append(f'a detail with no line should be kept: {pb.evaluate("(id) => itWhStore().rep[id].info", T)}')
    ur = pb.evaluate("(id) => { const w = itWhStore().rep[id]; return [w.raws.length, w.raws.some(r => r.k === 'you'), w.sigs[0].info]; }", U)
    if ur != [10, True, {'size': 'large'}]: out.append(f'the 10-line cap should keep the line that decides a detail: {ur}')
    if pb.evaluate(SIGS, V) != ['GHI-123:C247'] or pb.evaluate("(id) => itWhStore().rep[id].raws[0].k", V) != 'shared': out.append(f'someone\'s hand-added hole: {pb.evaluate(SIGS, V)}')
    # newer reports bring back an ID and a system you removed
    jn = pb.evaluate("""([R, S, nr, ns, now]) => JSON.stringify({tv: 'wormholes', v: 1, made: now, sys: [
      {id: R, name: nr, t: now - 60000, sigs: [], raws: [{t: now - 60000, k: 'intel', raw: `${nr} wh KLM-204`, set: itWhSetOf([itWhSigNew('KLM-204', false, '', false)]), n: 1}]},
      {id: S, name: ns, t: now - 60000, sigs: [], raws: [{t: now - 60000, k: 'intel', raw: `${ns} wh`, set: itWhSetOf([]), n: 1}]}]})""", [R, Sx, SYSNAME[R], SYSNAME[Sx], now])
    preview(pb, jn); add(pb)
    if 'KLM-204' not in pb.evaluate(SIGS, R) or not pb.evaluate("(id) => !!itWhStore().rep[id]", Sx): out.append(f'a newer report should bring back a removed ID and system: {pb.evaluate(SIGS, R)}')
    # ---- the checks on import
    store0 = pb.evaluate("localStorage.getItem('tvWormholes')")
    bads = {
        'wrong tv': json.dumps({'tv': 'x', 'v': 1, 'sys': []}), 'newer v': json.dumps({'tv': 'wormholes', 'v': 2, 'sys': []}),
        '300 KB': json.dumps({'tv': 'wormholes', 'v': 1, 'sys': [], 'pad': 'x' * 300000}), 'not JSON': 'hello <b>there</b>',
    }
    for k, v in bads.items():
        pv, msg = preview(pb, v)
        if pv or not msg: out.append(f'{k}: should be refused ({pv!r} {msg!r})')
    pb.evaluate("window.__x = 0")
    jb = pb.evaluate("""([P, nm, now]) => JSON.stringify({tv: 'wormholes', v: 1, made: now, sys: [
      {id: 30000001, name: 'Nowhere', t: now, raws: []}, {id: P, name: 'Not its name', t: now, raws: []},
      {id: P, name: nm, t: now - 3 * 86400e3, raws: [{t: now - 3 * 86400e3, k: 'intel', raw: 'x', n: 1}]},
      {id: P, name: nm, t: now + 5 * 3600e3, raws: [{t: now + 5 * 3600e3, k: 'intel', raw: 'x', n: 1}]},
      {id: P, name: nm, t: now - 60000, sigs: [{sig: 'NOPE-1', t: now}, {sig: 'ABC-123', type: 'Q999', t: now}],
       raws: [{t: now - 60000, k: 'intel', raw: `${nm} wh <img src=x onerror="window.__x=1">`, set: {sigs: [{sig: 'bad'}]}, n: 1}]}]})""", [P, SYSNAME[P], now])
    pv, msg = preview(pb, jb)
    if 'not systems on the map' not in pv and 'not a system on the map' not in pv: out.append(f'unknown and mismatched systems skipped and counted: {pv!r} {msg!r}')
    if pb.evaluate("window.__x") or pb.evaluate("document.querySelectorAll('.it-whp img').length"): out.append('HTML in an imported line ran or was drawn')
    if pb.evaluate("localStorage.getItem('tvWormholes')") != store0: out.append('a preview changed the store')
    if pb.locator('[data-it-whadd]').count():
        add(pb)
        bad = pb.evaluate("(id) => { const w = itWhStore().rep[id]; return [w.sigs.map(s => s.sig + ':' + s.type), w.raws.map(r => r.raw).join(' | ')]; }", P)
        if any(x.startswith('NOPE') or 'Q999' in x for x in bad[0]) or '<img' in bad[1] or 'onerror' in bad[1]: out.append(f'bad IDs, types or HTML got in: {bad}')
    # refused clipboard: the text stays selected with the Ctrl+C line
    pb.evaluate("() => { navigator.clipboard.writeText = () => Promise.reject(new Error('no')); }")
    export(pb); pb.click('[data-it-whcopy]'); pb.wait_for_timeout(300)
    cr = pb.evaluate("(() => { const ta = document.querySelector('#itWhExp textarea'); return [document.querySelector('#itWhExp .it-whp-bs').textContent, ta.selectionEnd - ta.selectionStart === ta.value.length]; })()")
    if 'Ctrl+C' not in cr[0] or not cr[1]: out.append(f'a refused copy: {cr}')
    cb.close()
    if phone:
        cp, pp = start(b, html, errs, 390, 844, intel=False)
        pp.evaluate("() => { const nv = document.querySelector('[data-it-nv=\"map\"]'); if(nv) nv.click(); }"); pp.wait_for_timeout(300)
        export(pp)
        X = pp.evaluate("() => [...document.querySelectorAll('[data-it-whxb], [data-it-whcopy]')].map(b => Math.round(b.getBoundingClientRect().height)).concat([document.scrollingElement.scrollWidth <= innerWidth + 1 ? 1 : 0])")
        if min(X[:-1]) < 44 or not X[-1]: out.append(f'390 px: heights {X[:-1]}, no sideways scroll {bool(X[-1])}')
        cp.close()
    return out, errs

MUTANTS = [
    ('lines matched by time instead of text', "function itWhLineKey(r){ return r.k === 'intel' ?", "function itWhLineKey(r){ return 't|' + Math.round(r.t / 6e5); return r.k === 'intel' ?"),
    ('theirs kept over yours', "if(imp && c.line.k === 'you' && !c.line.via){", "if(false){"),
    ('the cap dropping a line that decides a detail', "kept = [...sorted.filter(r => d.backing.has(r)), ...sorted.filter(r => !d.backing.has(r))].slice(0, IT_WH_RAW_MAX)", "kept = sorted.slice(0, IT_WH_RAW_MAX)"),
    ('the reporter written into the export', "return {t: r.t, k: hand ? 'hand' : 'intel', raw:", "return {t: r.t, who: r.who, k: hand ? 'hand' : 'intel', raw:"),
    ('a card redraw losing the open list\'s scroll (047)', "  if(whTop && itWhListShown()) itWhL.el.scrollTop = whTop;\n", ""),
    ('the page creeping with each redraw (047, the hand test)', "  itKeepPlace(y0, a0);\n", ""),
    ('an older line bringing back a removed ID', "      if(itWhSigGone(w.goneSig, n.sig, r.t)) continue;   // removed by you after this line\n", ""),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, 'Export and Import: the redaction, the round trip, the merge, the checks, the boxes')
    check(not errs, f'no page errors {errs[:3]}')
    for name, old, new in (MUTANTS if not os.environ.get('SHARE_FAST') else []):
        if PAGE.count(old) != 1: check(False, f'mutant "{name}": its line isn\'t in the page once'); continue
        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f:
            f.write(PAGE.replace(old, new)); mp = f.name
        try:
            try: mo, me = cases(b, mp, phone=False)
            except Exception as ex: mo, me = [f'stopped: {str(ex).splitlines()[0]}'], []
            check(bool(mo) or bool(me), f'mutant "{name}" fails ({(mo or me or ["nothing"])[0][:90]})')
        finally: os.unlink(mp)
    b.close()
print('FAILURES:', NS['fails'])
sys.exit(1 if NS['fails'] else 0)
