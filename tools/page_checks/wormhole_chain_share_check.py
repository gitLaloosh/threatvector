"""The Wormholes tab, part 3: Share (build queue 059; Project doc roadmap/wormholes-part3-plan.md P14-P18; 046's format and boxes). The owner: "Chain
only (Recommended)", "Yes, fill empty only (Recommended)" (status and tag), "7 allow it" (a removed system comes back by import), notes and who's
there "yes" to leaving them out unless ticked.

Two made-up players' chains of CCP's wormhole systems (names from the page's own table), no network. Checks:
  * the export: 046's object with `chain` beside an empty `sys`, v 1; systems by id, links by key; no positions, locks, src, gone marks; who's
    there and notes only when ticked; status and tag in; both ends' IDs; a link's old single ID only while a side isn't known; signatures;
  * the import's refusals and drops: another tool, v 2, not JSON, too long; a system the page doesn't know or whose name doesn't match; bad class,
    statics, IDs, types, status, a long note cut, a link to nothing, all counted;
  * the merge: newer wins per field, status and tag only into empty ones, an older edit never overwrites, nothing of yours removed, a removed
    system comes back (counted under Adds), a signature row last seen later wins; the preview's numbers, then the same worked out again at "Add
    to my map" after the store changed in between;
  * Copy link: a round trip through a #wh= link (deflate-raw), the tab opened with the preview and nothing added until the press, the address
    cleaned; over 1,800 characters refused; a broken link's message;
  * a chain export in Intel's Import says to use the Wormholes tab; Intel's export in the tab's Import says the reverse;
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

# picks wormhole systems by position in CCP's table; the sender's chain p0-p1-p2, p1-p3; IDs on each end of p0-p1, an old single one on p1-p2
SEED = """(k) => { const T = whTable(), J = T.names.filter(n => /^J\\d{6}$/.test(n)), p = [40, 310, 655, 902, 1210, 1488].map(i => whIdOf(J[i])), S = whState(), t0 = Date.now() - 3 * 3600e3;
  if(k === 'send'){ [p[0], p[1], p[2], p[1], p[3]].forEach((id, i) => whSeen(id, t0 + i * 60e3, false));
    const s1 = S.st.sys[p[1]]; s1.statics = 'D845'; s1.who = 'MKCO'; s1.notes = 'Mk note'; s1.u = Date.now();
    whEndSet(whLinkOf(p[0], p[1]), p[0], 'ABC-123', 'H296'); whEndSet(whLinkOf(p[0], p[1]), p[1], 'XYZ-789', 'K162');
    const l12 = whLinkOf(p[1], p[2]); l12.sig = 'RZL-429'; l12.mass = 'reduced'; l12.u = Date.now();
    S.mk[p[0]] = {lock: true, st: 'home', tag: 'HOME', at: [0, 0]}; S.mk[p[1]] = {st: 'warning'}; S.mk[p[3]] = {st: 'danger', tag: 'CAMP'};
    S.sg.sys[p[1]] = {t: Date.now(), rows: [{id: 'XYZ-789', sg: 'Cosmic Signature', grp: 'Wormhole', nm: 'Unstable Wormhole', pct: 100, f: Date.now() - 600e3, t: Date.now()}]};
    whEndGone(whLinkOf(p[0], p[1]), p[1], Date.now());
  } else {   // the receiver: p1 with an older static and its own status; p4 not in the sender's chain
    [p[4], p[1]].forEach((id, i) => whSeen(id, t0 + i * 60e3, false)); const s1 = S.st.sys[p[1]]; s1.statics = 'N062'; s1.u = t0; S.mk[p[1]] = {st: 'friendly'};
    S.sg.sys[p[1]] = {t: t0, rows: [{id: 'XYZ-789', sg: 'Cosmic Signature', grp: '', nm: '', pct: 20, f: t0 - 600e3, t: t0}]};
  }
  whSave(); whMkSave(); whSgSave(); whEndSave(); S.drawKey = ''; return p; }"""

def start(b, html, errs, w=1440):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': 900})
    ctx.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + html); pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_timeout(300)
    pg.evaluate("switchTab('wh'); navigator.clipboard.writeText = (t) => { window.__clip = t; return Promise.resolve(); }"); pg.wait_for_timeout(150)
    return ctx, pg

def export(pg, incl=False):
    pg.evaluate("whPopClose(); whPop('share')"); pg.wait_for_timeout(80)
    if incl: pg.click('.wh-pop[data-pop="share"] [data-wh-shinc]')
    pg.click('.wh-pop[data-pop="share"] [data-it-whxb="exp"]'); pg.wait_for_timeout(250)
    if incl: pg.wait_for_timeout(100)
    return pg.evaluate("document.querySelector('#whShExp textarea').value")

def preview(pg, text):
    pg.evaluate("whPopClose(); whPop('share')"); pg.click('.wh-pop[data-pop="share"] [data-it-whxb="imp"]')
    pg.fill('#whShImp textarea', text); pg.click('#whShImp [data-it-whimp]'); pg.wait_for_timeout(200)
    return pg.evaluate("[document.querySelector('#whShImp .it-whp-bs').textContent, document.querySelector('#whShImp .it-whp-prev').hidden ? '' : document.querySelector('#whShImp .it-whp-prev').textContent]")

def cases(b, html, parts=('export', 'read', 'merge', 'link', 'cross')):
    out, errs = [], []
    cs, snd = start(b, html, errs); p = snd.evaluate(SEED, 'send')
    txt = export(snd); o = json.loads(txt or '{}')
    if 'export' in parts:
        c = o.get('chain', {})
        if o.get('tv') != 'wormholes' or o.get('v') != 1 or o.get('sys') != [] or not c: out.append(f'the export: 046\'s object, chain beside an empty sys, v 1: {txt[:80]}')
        ids = [s['id'] for s in c.get('sys', [])]
        if ids != sorted(ids) or len(ids) != 4: out.append(f'the export\'s systems by id: {ids}')
        for bad in ('"pos"', '"lock"', '"at"', '"src"', '"gone"', '"who"', '"notes"'):
            if bad in txt: out.append(f'the export should hold no {bad}')
        if '"st":"home"' not in txt or '"tag":"CAMP"' not in txt: out.append('the export: status and tag in')
        L = {f"{l['a']}-{l['b']}": l for l in c.get('links', [])}
        l01 = next((l for l in c.get('links', []) if {l['a'], l['b']} == {p[0], p[1]}), {}); l12 = next((l for l in c.get('links', []) if {l['a'], l['b']} == {p[1], p[2]}), {})
        if l01.get('ends') != {str(p[0]): {'sig': 'ABC-123', 'type': 'H296'}, str(p[1]): {'sig': 'XYZ-789', 'type': 'K162'}} or 'sig' in l01: out.append(f'the export: both ends\' IDs, no old ID: {l01}')
        if l12.get('sig') != 'RZL-429': out.append(f'the export: the old single ID while its side isn\'t known: {l12}')
        if list(L) != sorted(L, key=lambda k: snd.evaluate("([a, b]) => whLinkKey(a, b)", [int(k.split('-')[0]), int(k.split('-')[1])])): out.append('the export\'s links in a stable order')
        if c.get('sigs', {}).get(str(p[1]), {}).get('rows', [{}])[0].get('id') != 'XYZ-789': out.append('the export: signatures')
        t2 = export(snd, True)
        if '"who":"MKCO"' not in t2 or '"notes":"Mk note"' not in t2: out.append('ticked: who\'s there and notes in')
    cr, rcv = start(b, html, errs); rcv.evaluate(SEED, 'recv')
    if 'read' in parts:
        rd = lambda t: rcv.evaluate("(t) => { const r = whChainRead(t); return r.err || JSON.stringify(r.sk); }", t)
        if 'isn’t a wormhole chain' not in rd('{"tv": "other", "v": 1}'): out.append('another tool should be refused')
        if 'newer version' not in rd('{"tv": "wormholes", "v": 2, "chain": {}}'): out.append('v 2 should be refused as newer')
        if 'isn’t JSON' not in rd('not json'): out.append('not JSON should be refused')
        if 'too long' not in rd(' ' * 10 + '{' + 'x' * (256 * 1024 + 10) + '}'): out.append('over 256 KB should be refused')
        bad = json.loads(txt); s0 = bad['chain']['sys']
        s0.append({'id': 30000142, 'name': 'Mk Nowhere'}); s0.append({'id': p[5], 'name': 'J000000'}); s0.append({'id': 999, 'name': 'x'})
        s0[1]['cls'] = 'c99'; s0[1]['statics'] = 'ZZZZ D845'; s0[1]['st'] = 'pirate'; s0[1]['notes'] = 'n' * 900
        bad['chain']['links'].append({'a': p[0], 'b': 31999999}); bad['chain']['links'][0]['ends'] = {str(p[0]): {'sig': 'bad', 'type': 'ZZ99'}}
        r = rcv.evaluate("(t) => { const r = whChainRead(t); if(r.err) return r.err; const s = r.sys.find(x => x.notes.length); return {sk: r.sk, cls: r.sys.map(x => x.cls), st: r.sys.map(x => x.st), notes: s ? s.notes.length : 0, stat: r.sys.map(x => x.statics), ends: r.links.map(l => l.ends)}; }", json.dumps(bad))
        if isinstance(r, str): out.append(f'a chain with bad parts should still read: {r}')
        else:
            if r['sk']['unknown'] != 3 or r['sk']['bad'] != 1: out.append(f'unknown systems and a link to nothing counted: {r["sk"]}')
            if 'c99' in r['cls'] or 'pirate' in r['st'] or r['notes'] > 400 or 'ZZZZ D845' in r['stat']: out.append(f'bad class, status, statics dropped, a long note cut: {r}')
            if any(e for e in r['ends'][:1]): out.append(f'a bad end ID and type dropped: {r["ends"][:1]}')
    if 'merge' in parts:
        n0 = rcv.evaluate("Object.keys(whS.st.sys).length"); l0 = rcv.evaluate("whS.st.links.length")
        st, pv = preview(rcv, txt)
        if 'Adds 3 systems and 3 connections' not in pv or 'updates 1 where theirs is newer' not in pv: out.append(f'the preview\'s numbers: {pv!r} {st!r}')
        if rcv.evaluate("Object.keys(whS.st.sys).length") != n0: out.append('the preview added something')
        rcv.evaluate("(n) => { whAddSys(n); whSave(); }", p[2])   # the store changes before the press: p2 is already there
        rcv.click('#whShImp [data-it-whadd]'); rcv.wait_for_timeout(200)
        m = rcv.evaluate("""(p) => { const S = whS, s1 = S.st.sys[p[1]]; return {n: Object.keys(S.st.sys).length, l: S.st.links.length, st1: s1.statics, mk1: (S.mk[p[1]] || {}).st, mk3: S.mk[p[3]] || null,
          lock0: !!(S.mk[p[0]] || {}).lock, src0: S.st.sys[p[0]].src, p4: !!S.st.sys[p[4]], sig: S.sg.sys[p[1]].rows[0], f: S.sg.sys[p[1]].rows[0].f,
          ends: JSON.stringify(S.ends[whLinkKey(p[0], p[1])] || {}), gone: Object.values(S.ends[whLinkKey(p[0], p[1])] || {}).some(e => e.gone), msg: document.querySelector('.wh-msg').textContent}; }""", p)
        if m['n'] != n0 + 3: out.append(f'Add to my map: 3 new systems (one already there by then): {m["n"]} of {n0 + 3}')
        if 'Added 2 systems' not in m['msg']: out.append(f'Add works the merge out again against the store as it is then: {m["msg"]!r}')
        if m['st1'] != 'D845': out.append(f'newer statics should win: {m["st1"]}')
        if m['mk1'] != 'friendly': out.append(f'your status kept (fill empty only): {m["mk1"]}')
        if m['mk3'] != {'st': 'danger', 'tag': 'CAMP'}: out.append(f'status and tag fill an empty one: {m["mk3"]}')
        if m['lock0'] or m['src0'] != 'shared': out.append(f'no lock travels; a new system is "shared": {m}')
        if not m['p4']: out.append('nothing of yours removed')
        if m['sig']['pct'] != 100 or m['sig']['grp'] != 'Wormhole': out.append(f'the signature row last seen later wins: {m["sig"]}')
        if m['gone'] or 'ABC-123' not in m['ends']: out.append(f'both ends\' IDs in, no gone mark travels: {m["ends"]}')
        older = json.loads(txt); older['chain']['sys'] = [dict(s, statics='C247', u=1) for s in older['chain']['sys']]
        rcv.evaluate("(t) => { const rd = whChainRead(t); whChainMerge(rd, true); }", json.dumps(older))
        if rcv.evaluate("(n) => whS.st.sys[n].statics", p[1]) != 'D845': out.append('an older edit overwrote a newer one')
        rcv.evaluate("(n) => { whS.mk[n] = {}; whRemoveSys(n); }", p[3])
        st, pv = preview(rcv, txt)
        if 'Adds 1 system' not in pv: out.append(f'a removed system comes back, counted under Adds: {pv!r}')
    if 'link' in parts:
        snd.evaluate("whPopClose(); whPop('share')"); snd.click('.wh-pop[data-pop="share"] [data-it-whxb="exp"]'); snd.wait_for_timeout(250)
        snd.click('#whShExp [data-it-whlink]'); snd.wait_for_timeout(300)
        link = snd.evaluate("window.__clip || ''")
        if '#wh=' not in link or len(link) > 1800: out.append(f'Copy link: a #wh= link under 1,800 characters: {len(link)} {link[:60]}')
        else:
            cl, lpg = start(b, html, errs); lpg.evaluate(SEED, 'recv'); n0 = lpg.evaluate("Object.keys(whS.st.sys).length")
            lpg.evaluate("(h) => { switchTab('intel'); history.replaceState(null, '', location.pathname + '#' + h.split('#')[1]); whLinkOpen(); }", link); lpg.wait_for_timeout(500)
            r = lpg.evaluate("[whTabNow(), !document.querySelector('#whShImp').hidden, document.querySelector('#whShImp .it-whp-prev').textContent, location.hash, Object.keys(whS.st.sys).length]")
            if r[0] != 'wh' or not r[1] or 'Adds 3 systems' not in r[2] or r[3] != '' or r[4] != n0: out.append(f'a #wh= link opens the tab with the preview, nothing added, the address cleaned: {r}')
            lpg.click('#whShImp [data-it-whadd]'); lpg.wait_for_timeout(200)
            if lpg.evaluate("Object.keys(whS.st.sys).length") != n0 + 3: out.append('the link\'s chain added at the press')
            lpg.evaluate("() => { history.replaceState(null, '', location.pathname + '#wh=AAAA_broken'); whLinkOpen(); }"); lpg.wait_for_timeout(300)
            if 'broken' not in lpg.evaluate("document.querySelector('#whShImp .it-whp-bs').textContent"): out.append('a broken link should say so')
            cl.close()
        big = snd.evaluate("""() => { const T = whTable(), J = T.names.filter(n => /^J\\d{6}$/.test(n)), t = Date.now(); let prev = null;
          for(let i = 0; i < 160; i++){ const id = whIdOf(J[100 + i * 7]); whAddSys(id, t); if(prev) whAddLink(prev, id, t); prev = id; } whSave(); return Object.keys(whS.st.sys).length; }""")
        snd.evaluate("whPopClose(); whPop('share')"); snd.click('.wh-pop[data-pop="share"] [data-it-whxb="exp"]'); snd.wait_for_timeout(300); snd.evaluate("window.__clip = ''")
        snd.click('#whShExp [data-it-whlink]'); snd.wait_for_timeout(300)
        if 'Too long for a link' not in snd.evaluate("document.querySelector('#whShExp .it-whp-bs').textContent") or snd.evaluate("window.__clip"): out.append(f'over 1,800 characters: nothing copied, copy the text instead ({big} systems)')
    if 'cross' in parts:
        r = rcv.evaluate("(t) => itWhImportRead(t).err || ''", txt)
        if 'Wormholes tab' not in r: out.append(f'a chain export in Intel\'s Import should point at the Wormholes tab: {r!r}')
        st, pv = preview(rcv, json.dumps({'tv': 'wormholes', 'v': 1, 'made': 1, 'sys': [{'id': 30000142, 'name': 'Jita', 't': 1, 'raws': []}]}))
        if 'Intel’s Wormholes list' not in st: out.append(f'Intel\'s export in the tab\'s Import should point at Intel: {st!r}')
    cs.close(); cr.close()
    return out, errs

MUTANTS = [
    ('the merge takes an older edit', "    if(x.u > m.u) for(const f of ['cls', 'statics', 'who', 'notes'])", "    for(const f of ['cls', 'statics', 'who', 'notes'])", ('merge',)),
    ('positions in the export', "  return {tv: 'wormholes', v: 1, made: Date.now(), sys: [], chain: {sys, links, sigs}};", "  return {tv: 'wormholes', v: 1, made: Date.now(), sys: [], chain: {sys, links, sigs, pos: S.st.pos}};", ('export',)),
    ('locks in the export', "if(m.st) o.st = m.st; if(m.tag) o.tag = m.tag;", "if(m.st) o.st = m.st; if(m.tag) o.tag = m.tag; if(m.lock) o.lock = true;", ('export',)),
    ('a link adds without the press', "  box.querySelector('textarea').value = text; whShareImport();", "  box.querySelector('textarea').value = text; whChainMerge(whChainRead(text), true); whShareImport();", ('link',)),
    ('status overwrites yours', "    if(x.st && !mk.st){", "    if(x.st){", ('merge',)),
    ('no length cap on the link', "        if(txt.length > WH_LINK_MAX_CH){", "        if(false){", ('link',)),
]

if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch()
        out, errs = cases(b, HTML)
        for o in out: check(False, o)
        check(not out, 'Share: the export, the import\'s checks, the merge, Copy link and #wh= links, Intel\'s Import and the tab\'s')
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
