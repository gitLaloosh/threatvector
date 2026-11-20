"""The Wormholes tab: J-space statics known the moment you enter a system (build queue 061; Project doc roadmap/wh-statics-plan.md; the owner:
"i need you to find a way for us to know what a j-space systems's statics are when the user enters one. i know what wanderer does it.").

CCP's wormhole system names and the community list's statics from the page's own tables (INTEL_WH, INTEL_WH_STC); no network. Checks:
  * a system with nothing typed shows the list's statics (as INTEL_WH_STC has them) and the note "from the community list (Wanderer) ...",
    and tvWhChain still holds statics '' for it; the map box draws them too;
  * typing replaces them (the note "typed by you", saved); clearing the field brings the list's back (the note again, saved as '');
    a system with typed statics shows only those after a reload;
  * the order: chips and the map box by where they lead, CCP's class number (a system whose list has them the other way round);
  * the chip's hover: CCP's lifetime and both masses for a code (IT_WH_LIFE), none for K162;
  * the suggestions: the connection editor's Type field lists the system's statics first, then K162; + Add's type field lists the
    "Linked to" system's statics first, and none once Linked to is "nothing";
  * Share: the export carries typed statics only, never the list's;
  * statics made for another system list (INTEL_WH_STC.of differs) are not used: no chips, no note, no page error;
  * a phone (390 px): the note shows, no sideways scroll;
  * mutants; no page errors.
"""
import sys, os, json, tempfile
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
HTML = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith('--')), os.path.join(REPO, 'index.html')))
PAGE = open(HTML, encoding='utf-8').read()
fails = 0
def check(ok, msg):
    global fails
    print(('PASS ' if ok else 'FAIL ') + msg)
    if not ok: fails += 1

NOTE_LIST, NOTE_YOU = 'from the community list (Wanderer) · type your own to replace them', 'typed by you'
# a chain p0 - p1 - p2 - p3 of CCP's own wormhole systems; R: one whose list has its statics in the other order from class order
SEED = """() => { const T = whTable(), J = T.names.filter(n => /^J\\d{6}$/.test(n)), p = [40, 310, 655, 902].map(i => whIdOf(J[i]));
  const t0 = Date.now() - 3 * 3600e3; p.forEach((id, i) => whSeen(id, t0 + i * 60e3, false));
  const r = T.ids.find((id, i) => /^J\\d{6}$/.test(T.names[i]) && T.stc[i] && whStcSort(T.stc[i]) !== T.stc[i] && !p.includes(id));
  if(r){ whAddSys(r); whAddLink(p[3], r); }
  whSave(); whState().drawKey = ''; return {p, r: r || null, list: Object.fromEntries([...p, r].filter(Boolean).map(id => [id, T.stc[T.at.get(id)] || '']))}; }"""
OPEN = "(n) => { if(whS.open !== 'sum') whPnSet('sum', true); whSelect(n); }"
PANEL = """() => { const q = (s) => document.querySelector('#whPnSum ' + s), nt = q('[data-wh-stcsrc]');
  return {chips: [...document.querySelectorAll('#whPnSum [data-wh-stc] .wh-sc')].map(e => e.firstChild.textContent.trim()),
          titles: [...document.querySelectorAll('#whPnSum [data-wh-stc] .wh-sc')].map(e => e.title),
          note: nt && !nt.hidden ? nt.textContent : null, field: q('[data-f="statics"]') ? q('[data-f="statics"]').value : null}; }"""
STORED = "(n) => { const s = JSON.parse(localStorage.getItem('tvWhChain') || '{}'); return s.sys && s.sys[n] ? s.sys[n].statics : null; }"
# what the map box writes for system n: the texts on its statics line, in order
BOX = """(n) => { const M = whS.M, p = M.P.get(n), r = whCv().getBoundingClientRect();
  M.cam = {x: p.x + WH_NW / 2 - r.width / 2, y: p.y + WH_NH / 2 - r.height / 2, s: 1};
  const T = [], f = CanvasRenderingContext2D.prototype.fillText;
  CanvasRenderingContext2D.prototype.fillText = function(t, x, y, ...z){ if(Math.abs(y - (p.y + 42)) < 0.5 && x >= p.x && x <= p.x + WH_NW) T.push(String(t)); return f.call(this, t, x, y, ...z); };
  try{ whDraw(); } finally { CanvasRenderingContext2D.prototype.fillText = f; }
  return T; }"""
SHORT = "(codes) => codes.map(c => c === 'K162' ? 'exit' : itWhDestTxt(c)[0])"

def start(b, html, w, errs, h=900, touch=False):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch)
    ctx.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + html); pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_timeout(300)
    pg.evaluate("switchTab('wh')"); pg.wait_for_timeout(200)
    return ctx, pg

def type_in(pg, v):
    f = pg.locator('#whPnSum [data-f="statics"]'); f.fill(v); f.dispatch_event('change'); pg.wait_for_timeout(120)

def cases(b, html, parts=('list', 'typed', 'order', 'hover', 'suggest', 'share', 'moved', 'phone')):
    out, errs = [], []
    ctx, pg = start(b, html, 1440, errs); ev = pg.evaluate
    w = ev(SEED); p, R, L = w['p'], w['r'], {int(k): v.split() for k, v in w['list'].items()}
    if not all(L[x] for x in p): out.append(f'the made-up chain\'s systems should all be on the community list: {L}')
    sort = lambda n: ev("(v) => whStcSort(v)", ' '.join(L[n])).split()
    if 'list' in parts:
        ev(OPEN, p[2]); pg.wait_for_timeout(120); s = ev(PANEL)
        if s['chips'] != sort(p[2]): out.append(f'nothing typed: the list\'s statics should show, in class order: {s["chips"]} vs {sort(p[2])}')
        if s['note'] != NOTE_LIST: out.append(f'nothing typed: the note should name the community list: {s["note"]!r}')
        if s['field'] != '': out.append(f'the Statics field should stay empty for the list\'s statics: {s["field"]!r}')
        if ev(STORED, p[2]) != '': out.append(f'the list\'s statics should never be saved: {ev(STORED, p[2])!r}')
        bx = ev(BOX, p[2])
        if bx[1:] != ev(SHORT, sort(p[2])): out.append(f'the map box should draw the list\'s statics: {bx}')
    if 'typed' in parts:
        ev(OPEN, p[1]); pg.wait_for_timeout(120); type_in(pg, 'D845')
        s = ev(PANEL)
        if s['chips'] != ['D845'] or s['note'] != NOTE_YOU: out.append(f'typed statics replace the list\'s, noted "typed by you": {s}')
        if ev(STORED, p[1]) != 'D845': out.append(f'typed statics are saved: {ev(STORED, p[1])!r}')
        if ev(BOX, p[1])[1:] != ev(SHORT, ['D845']): out.append(f'the map box draws the typed statics: {ev(BOX, p[1])}')
        type_in(pg, ''); s = ev(PANEL)
        if s['chips'] != sort(p[1]) or s['note'] != NOTE_LIST: out.append(f'clearing the field brings the list\'s back with its note: {s}')
        if ev(STORED, p[1]) != '': out.append(f'cleared statics are saved empty: {ev(STORED, p[1])!r}')
        f = pg.locator('#whPnSum [data-f="statics"]'); f.fill('U210'); pg.wait_for_timeout(80); s = ev(PANEL)   # while typing, before the change
        if s['chips'] != ['U210'] or s['note'] != NOTE_YOU: out.append(f'while typing, the chips and the note follow the field: {s}')
        f.fill(''); pg.wait_for_timeout(80); s = ev(PANEL)
        if s['chips'] != sort(p[1]) or s['note'] != NOTE_LIST: out.append(f'while typing, an empty field shows the list\'s again: {s}')
        type_in(pg, 'N062 D845')
        pg.reload(); pg.wait_for_timeout(300); ev("switchTab('wh')"); pg.wait_for_timeout(150); ev(OPEN, p[1]); pg.wait_for_timeout(120); s = ev(PANEL)
        if s['chips'] != ev("(v) => whStcSort(v)", 'N062 D845').split() or s['note'] != NOTE_YOU: out.append(f'after a reload a system with typed statics shows only those: {s}')
    if 'order' in parts:
        if not R: out.append('no system on the community list has its statics out of class order (the check needs one)')
        else:
            ev(OPEN, R); pg.wait_for_timeout(120); s = ev(PANEL)
            ranks = ev("(c) => c.map(x => WH_STC_ORD[IT_WH_TYPE[x]] || 98)", s['chips'])
            if s['chips'] == L[R] or ranks != sorted(ranks): out.append(f'the chips should be in class order, not the list\'s: {s["chips"]} (list {L[R]})')
            bx = ev(BOX, R)
            if bx[1:] != ev(SHORT, s['chips']): out.append(f'the map box should list them in the same class order: {bx} vs {s["chips"]}')
    if 'hover' in parts:
        ev(OPEN, p[2]); pg.wait_for_timeout(120); s = ev(PANEL)
        d = ev("(c) => IT_WH_LIFE[c]", s['chips'][0])
        want = ev("(d) => ` · up to ${d[0] % 60 ? (d[0] / 60).toFixed(1) : d[0] / 60} h · ${d[1].toLocaleString('en-US')} t in all · ${d[2].toLocaleString('en-US')} t per jump`", d)
        if want not in s['titles'][0] or 'leads to' not in s['titles'][0]: out.append(f'a static\'s hover gives where it leads, CCP\'s lifetime and both masses: {s["titles"][0]!r} ({want!r})')
        c247 = ev("() => { const t = document.createElement('div'); t.innerHTML = whStcHtml('C247'); return t.firstChild.title; }")
        if 'up to 16 h · 2,000,000 t in all · 375,000 t per jump' not in c247: out.append(f'C247\'s hover: CCP\'s 960 minutes, 2,000,000,000 and 375,000,000 kg: {c247!r}')
        k = ev("() => { const t = document.createElement('div'); t.innerHTML = whStcHtml('K162'); return t.firstChild.title; }")
        if ' h · ' in k or 't in all' in k: out.append(f'K162 has no lifetime or mass of its own: {k!r}')
    if 'suggest' in parts:
        opts = ev("""([a, b]) => { const l = whLinkOf(a, b), r = {l, me: null, ot: null, o: b, name: whName(b)}, t = document.createElement('div');
          t.innerHTML = whCnEditHtml({n: a}, r); const i = t.querySelector('[data-wh-le="type"]'), dl = t.querySelector('#' + i.getAttribute('list'));
          return dl ? [...dl.options].map(o => o.value) : null; }""", [p[2], p[3]])
        want = sort(p[2])
        if not opts or opts[:len(want) + 1] != want + ['K162'] or len(opts) != len(set(opts)) or len(opts) < 50:
            out.append(f'the connection editor\'s Type field suggests the system\'s statics, then K162, then the rest: {(opts or [])[:6]} vs {want}')
        ev(OPEN, p[2]); pg.wait_for_timeout(100); pg.click('[data-wh-pop="add"]'); pg.wait_for_timeout(120)
        a = ev("() => { const f = document.querySelector('.wh-addf'); return {link: f.link.value, list: f.ty.getAttribute('list'), opts: [...f.querySelectorAll('#whAddTyDl option')].map(o => o.value)}; }")
        lk = int(a['link']) if a['link'] else None
        if lk is None or a['list'] != 'whAddTyDl' or a['opts'][:len(sort(lk)) + 1] != sort(lk) + ['K162']:
            out.append(f'+ Add\'s type field suggests the "Linked to" system\'s statics first: {a["opts"][:5]} (linked to {lk})')
        pg.select_option('.wh-addf select[name="link"]', ''); pg.wait_for_timeout(80)
        o = ev("() => [...document.querySelectorAll('.wh-addf #whAddTyDl option')].map(o => o.value)")
        if not o or o[0] != 'K162': out.append(f'+ Add linked to nothing suggests K162 first, no statics: {o[:4]}')
        ev("whPopClose()")
    if 'share' in parts:
        ev(OPEN, p[0]); pg.wait_for_timeout(100); type_in(pg, 'D845')
        x = ev("() => whChainExport(false)")
        st = {int(y['id']): y.get('statics', '') for y in (x.get('chain') or x).get('sys', [])} if isinstance(x, dict) else {}
        if st.get(p[0]) != 'D845' or any(v for k, v in st.items() if k != p[0] and k != p[1]):
            out.append(f'the export carries typed statics only, never the list\'s: {dict(list(st.items())[:5])}')
    ctx.close()
    if 'moved' in parts:   # statics made for another system list: not used
        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(html)) as f:
            src = open(html, encoding='utf-8').read(); i = src.index('const INTEL_WH_STC = {'); j = src.index('"of":"', i) + 6
            f.write(src[:j] + '0000000' + src[j + 7:]); mv = f.name
        try:
            ctx, pg = start(b, mv, 1440, errs); w2 = pg.evaluate(SEED); pg.evaluate(OPEN, w2['p'][2]); pg.wait_for_timeout(120); s = pg.evaluate(PANEL)
            if s['chips'] or s['note'] is not None: out.append(f'statics made for another system list must not be used: {s}')
            ctx.close()
        finally: os.unlink(mv)
    if 'phone' in parts:
        ctx, pg = start(b, html, 390, errs, 844, True); w3 = pg.evaluate(SEED); pg.evaluate(OPEN, w3['p'][2]); pg.wait_for_timeout(150)
        s = pg.evaluate(PANEL); sw = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        vis = pg.evaluate("() => { const e = document.querySelector('#whPnSum [data-wh-stcsrc]'); if(!e) return false; const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0; }")
        if s['note'] != NOTE_LIST or not vis: out.append(f'a phone shows the note under the chips: {s["note"]!r} visible {vis}')
        if sw > 0: out.append(f'a phone: no sideways scroll ({sw} px)')
        ctx.close()
    return out, errs

MUTANTS = [
    ('the list\'s statics win over typed ones', "function whStcOf(n, own = ((whS && whS.st.sys[n]) || {}).statics || ''){ if(own) return",
     "function whStcOf(n, own = ((whS && whS.st.sys[n]) || {}).statics || ''){ if(own && !whStcList(n)) return", ('typed',)),
    ('no statics without typing', "function whStcList(n){ if(!whIsJ(n)) return '';", "function whStcList(n){ if(n) return '';", ('list',)),
    ('chips in the list\'s order', "function whStcsHtml(v){ return whStcSort(v).split(' ')", "function whStcsHtml(v){ return String(v || '').split(' ')", ('order',)),
    ('the map box in the list\'s order', "const stc = k ? '' : whStcSort(whStcOf(n).codes);", "const stc = k ? '' : whStcOf(n).codes;", ('order',)),
    ('the map box with typed statics only', "const stc = k ? '' : whStcSort(whStcOf(n).codes);", "const stc = k ? '' : whStcSort(sy.statics);", ('list',)),
    ('no lifetime or mass on hover', "  const d = code === 'K162' ? null : IT_WH_LIFE[code],", "  const d = null,", ('hover',)),
    ('an empty field shows nothing', "  const so = whStcOf(Number(ed.dataset.whEd), whStatics(f.value).ok),", "  const so = {codes: whStatics(f.value).ok, src: 'you'},", ('typed',)),
    ('suggestions without the statics', "  const mine = n === null || n === undefined ? [] : whStcSort(", "  const mine = true ? [] : whStcSort(", ('suggest',)),
    ('+ Add\'s suggestions not following Linked to', "    if(f.name === 'link' && f.closest('.wh-addf')){ whAddTyList(f.form); return; }", "    if(f.name === 'link' && f.closest('.wh-addf')) return;", ('suggest',)),
    ('statics used for another system list', "if(S && S.n === W.systems && S.of === whFnv(W.sys)){", "if(S && S.n === W.systems){", ('moved',)),
    ('the list\'s statics saved', "else if(k === 'statics'){ const c = whStatics(f.value); s.statics = c.ok;", "else if(k === 'statics'){ const c = whStatics(f.value); s.statics = c.ok || whStcList(n);", ('typed',)),
    ('no note', "function whStcNoteHtml(src){ return src ?", "function whStcNoteHtml(src){ return false ?", ('list',)),
]

if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch()
        out, errs = cases(b, HTML)
        for o in out: check(False, o)
        check(not out, 'statics from the community list, typed ones replacing them, class order, the hover, the suggestions, Share, another system list, a phone')
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
