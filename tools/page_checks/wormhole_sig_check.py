"""Signature IDs and hole details in Intel's wormhole reports (build queue 044, roadmap/wormhole-sig-ids-plan.md; the owner: "need the intel
parser to be able to identify when someone reporting a wormhole also includes the ID of the cosmic signature and record that along w/ the
wormhole ... someone might give a partial ID that's unique in the list of anomalies in that system.").

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/wormhole_sig_check.py [index.html]   -> 'FAILURES: N' (must be 0)
    (SIG_FAST=1 skips the mutants, for a quick look while working.)

Uses intel_check.py's made-up folder, mocks and names (you in 1DQ1-A); every pilot and line is made up. Checks:
  * the reader (itParse's whd): the owner's line shape ("wh rzl-429 z971 class 1-3 medium size less then 1 day less then 50% mass": RZL-429,
    Z971, C1-3, under a day, under 50%, medium; no word left, no pilot run, one system), "wh sig QDX", two IDs with types, "drifter hole
    BKT772", "wh lmn c3 fresh", "wormhole QDX-581 n110 eol"; life / mass / size only when plain; a line without a wormhole word unchanged;
    "wh the" no ID; the type table from CCP's data (C729 "?", K162 exit, R081 C4);
  * kept with the report: part -> whole, a part fitting two kept IDs on its own, newest first, at most 8, "RZL crit" changing only RZL-429's
    mass; Drifter per hole (two Drifter IDs + a plain one: drN 2, "DRIFTER ×2"); a Drifter report with no ID surviving a plain "wh";
    `set` on every kept line;
  * the removal mark: × removes one ID (and Drifter with it), the same line read again or an older one (or its part) doesn't bring it back,
    a newer report does; the mark survives a reload of the store;
  * the store read back with checks (bad fields dropped), and an entry 040 wrote (drifter, no sigs) read as a Drifter report with no ID;
  * tags on the Feed line, Near You's row (a system with a hostile report), the list (with ×) and the map label; the split ring (two colours);
  * the Add form: every property, the hint as you type, a part updating a kept ID, refused fields; the lines as typed under the chevron;
  * 390 px: no sideways scroll with the list open, the × at least 44 px;
  * mutants, each must fail: the reader after the systems; a part merged into the first of two matches; an older line bringing back a
    removed ID; no `set` on lines;
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
near = sorted((s for s, v in D0.items() if 1 <= v <= 3), key=lambda s: (D0[s], s))
HOST = M.PILOTS[M.pick(98000003, 0)][0]
PARSE = """(m) => { const p = itParse(m, itMySys()); return JSON.stringify({whd: p.whd, sys: p.sys.map(s => itSysName(s.id)), left: p.W.filter((x, i) => !p.used[i]).map(x => x.w), runs: (p.runs || []).map(r => r.map(i => p.W[i].w).join(' '))}); }"""
SIGS = "(id) => (itWhStore().rep[id] && itWhStore().rep[id].sigs || []).map(s => s.sig + (s.part ? '~' : '') + (s.type ? ':' + s.type : '') + (s.dr ? '!' : ''))"

def start(b, html, errs, W=1440, H=1000):
    ctx = b.new_context(bypass_csp=True, viewport={'width': W, 'height': H})
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); route(ctx)
    pg = ctx.new_page(); pg.goto('file://' + html)
    pg.evaluate("(s) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({channels: ['region.intel'], me: 95000001, range: 3, forget: 15})); }", SIDE)
    pg.reload(); pg.wait_for_timeout(400)
    setup_logs(pg); pg.click('#tabBtnIntel'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg)
    return ctx, pg

def cases(b, html, phone=True):
    out, errs = [], []
    ctx, pg = start(b, html, errs)
    if not pg.evaluate("typeof itWhStore === 'function'"): out.append('no wormhole store'); ctx.close(); return out, errs
    taken = set(pg.evaluate("[...it.near.keys()]"))
    S = [x for x in near if x not in taken][:7]
    A, B, C, Dd, E, F, G = S; N = {x: SYSNAME[x] for x in S}
    # two made-up null-sec names whose starts look like the words of a wormhole line ("class 1-3"; a part "zxb-4"), LESSON #163
    R1, R2, H = [x for x in near if x not in taken and x not in S][:3]
    pg.evaluate("""(pairs) => { const N = it.names; for(const [id, nm] of pairs){ const o = N.byId.get(id); if(o) N.byLower.delete(o.toLowerCase()); N.byLower.set(nm.toLowerCase(), id); N.byId.set(id, nm); }
      N.list = [...N.byLower.keys()]; }""", [[R1, '1-3QQZ'], [R2, 'ZXB-4Q']])
    # ---- the reader
    R = {
        f'{N[A]} wh rzl-429 z971 class 1-3 medium size less then 1 day less then 50% mass': (['RZL-429'], 'Z971', 'C1-3', {'life': 'lt1d', 'mass': 'reduced', 'size': 'medium', 'cls': 'C1-3'}),
        f'{N[B]} wh sig QDX': (['QDX'], '', '', None),
        f'{N[C]} 2 wh xyz-123 h296 and pqr-4 k162': (['XYZ-123', 'PQR-4'], 'H296', '', None),
        f'{N[Dd]} drifter hole BKT772': (['BKT-772'], '', '', None),
        f'{N[E]} wh lmn c3 fresh': (['LMN'], '', 'C3', {'cls': 'C3'}),
        f'{N[B]} wormhole QDX-581 n110 eol': (['QDX-581'], 'N110', '', {'life': 'eol'}),
    }
    for m, (sigs, typ, cls, info) in R.items():
        r = json.loads(pg.evaluate(PARSE, m)); d = r['whd'] or {'sigs': [], 'types': [], 'cls': ''}
        got = [s['sig'] for s in d['sigs']]
        ok = got == sigs and (not typ or d['sigs'][0].get('type') == typ) and d['cls'] == cls and not r['left'] and not r['runs'] and len(r['sys']) == 1 and (d['sigs'][0].get('info') if d['sigs'] else None) == info
        if not ok: out.append(f'reads "{m}": {got} {[s.get("type") for s in d["sigs"]]} {d["cls"]!r} {[s.get("info") for s in d["sigs"]]}; left {r["left"]}; runs {r["runs"]}; systems {r["sys"]}')
    for m, want in [('wh abc-123 <4h crit', {'life': 'eol', 'mass': 'critical'}), ('wh abc-123 end of life', {'life': 'eol'}), ('wh abc-123 frig hole', {'size': 'small'}),
                    ('wh abc-123 <1h', {'life': 'lt1h'}), ('wh abc-123 2 frigs on it', None), ('wh abc-123 fresh', None), ('wh abc-123 caps', None),
                    ('wh abc-123 >50% stable xl', {'mass': 'stable', 'size': 'xl'}), ('wh abc-123 reduced and crit', {'mass': 'critical'})]:
        r = json.loads(pg.evaluate(PARSE, f'{N[A]} {m}'))
        got = r['whd']['sigs'][0].get('info') if r['whd'] and r['whd']['sigs'] else 'no sig'
        if got != want: out.append(f'life/mass/size only when plain: "{m}" -> {got} (want {want})')
    r = json.loads(pg.evaluate(PARSE, f'{N[A]} wh zxb-4'))
    if r['sys'] != [N[A], 'ZXB-4Q'] or (r['whd'] and r['whd']['sigs']): out.append(f'a dash part that starts a system\'s name stays a system: {r["sys"]} {r["whd"]}')
    r = json.loads(pg.evaluate(PARSE, f'{N[A]} rzl and class neuts'))
    if r['whd'] is not None: out.append('a line with no wormhole word read wormhole details')
    r = json.loads(pg.evaluate(PARSE, f'{N[A]} wh the bob'))
    if r['whd']['sigs']: out.append(f'"wh the" took an ID: {r["whd"]["sigs"]}')
    T = pg.evaluate("[IT_WH_TYPE.C729, IT_WH_TYPE.K162, IT_WH_TYPE.R081, IT_WH_TYPE.Z971, IT_WH_TYPE.N110, Object.keys(IT_WH_TYPE).length]")
    if T[:5] != ['?', 'exit', 'c4', 'c1', 'hs'] or T[5] < 100: out.append(f'the type table: {T}')
    # ---- kept with the report (lines through Intel's folder)
    t = time.time()
    def post(lines, wait=3200):
        nonlocal t
        W(pg, F_INTEL, ''.join(line(t + k, who, msg) for k, (who, msg) in enumerate(lines))); t += len(lines) + 1; tick(pg, wait)
    post([('Gate Watcher', f'{N[F]} {HOST} sabre')])   # F gets a Near You row (a hostile), so its wormhole badge and IDs show there
    post([('Scout Alt', f'{N[A]} wh rzl-429 z971 class 1-3 medium size less then 1 day less then 50% mass'), ('Gate Watcher', f'{N[A]} wh sig MKV crit'),
          ('Gate Watcher', f'{N[B]} wh sig QDX'), ('Scout Alt', f'{N[C]} 2 wh xyz-123 h296 and pqr-4 k162'),
          ('Gate Watcher', f'{N[Dd]} drifter hole BKT772'), ('Scout Alt', f'{N[Dd]} drifter KLM-204 frig hole'), ('Gate Watcher', f'{N[Dd]} wh XRT-331'),
          ('Scout Alt', f'{N[F]} wh def-777 c247')])
    post([('Gate Watcher', f'{N[B]} wormhole QDX-581 n110 eol'), ('Scout Alt', f'{N[A]} wh RZL crit now'), ('Gate Watcher', f'{N[C]} wh pqr-417'), ('Scout Alt', f'{N[E]} wh lmn c3 fresh')])
    sg = {x: pg.evaluate(SIGS, x) for x in (A, B, C, Dd, E)}
    if sg[B] != ['QDX-581:N110']: out.append(f'the part QDX should become QDX-581: {sg[B]}')
    if sg[A] != ['RZL-429:Z971', 'MKV~']: out.append(f'"RZL" should match the kept RZL-429, newest first: {sg[A]}')
    if sg[C] != ['PQR-417:K162', 'XYZ-123:H296']: out.append(f'PQR-4 should become PQR-417, newest first: {sg[C]}')
    if sg[E] != ['LMN~']: out.append(f'a part kept: {sg[E]}')
    if sg[Dd] != ['XRT-331', 'KLM-204!', 'BKT-772!']: out.append(f'Drifter per hole: {sg[Dd]}')
    inf = pg.evaluate("(id) => itWhStore().rep[id].sigs.find(s => s.sig === 'RZL-429').info", A)
    if inf != {'life': 'lt1d', 'mass': 'critical', 'size': 'medium', 'cls': 'C1-3'}: out.append(f'"RZL crit" should change RZL-429\'s mass only: {inf}')
    dr = pg.evaluate("(id) => { const w = itWhStore().rep[id]; return [w.drifter, w.drN, itMapWhLabel(w).split(' · ')[0], itWhKinds(w).length]; }", Dd)
    if dr != [True, 2, 'DRIFTER ×2 XRT-331 +2', 2]: out.append(f'Drifter per hole: {dr} (want Drifter, 2, "DRIFTER ×2 XRT-331 +2", a split ring)')
    sets = pg.evaluate("(id) => (itWhStore().rep[id].raws || []).map(r => r.set && r.set.sigs.map(s => s.sig + (s.dr ? '!' : '')).join(','))", Dd)
    if sets != ['XRT-331', 'KLM-204!', 'BKT-772!']: out.append(f'each kept line says what it set: {sets}')
    post([('Gate Watcher', f'{N[C]} wh xyz-456'), ('Gate Watcher', f'{N[C]} wh sig xyz')])
    c3 = pg.evaluate(SIGS, C)
    if c3[:1] != ['XYZ~'] or 'XYZ-456' not in c3 or 'XYZ-123:H296' not in c3: out.append(f'"xyz" fits two kept IDs, so it is kept on its own: {c3}')
    post([('Scout Alt', f'{N[G]} drifter'), ('Scout Alt', f'{N[G]} wh')])
    g = pg.evaluate("(id) => [itWhStore().rep[id].drifter, !!itWhStore().rep[id].drNoId]", G)
    if g != [True, True]: out.append(f'a Drifter report with no ID should stay after a plain "wh": {g}')
    for i in range(9): post([('Scout Alt', f'{N[E]} wh q{chr(97 + i)}x-10{i}')], 400)
    if len(pg.evaluate(SIGS, E)) != 8: out.append(f'at most 8 IDs: {pg.evaluate(SIGS, E)}')
    # ---- tags: the Feed line, Near You's row, the map label
    fd = pg.evaluate("() => [...document.querySelectorAll('#itFeedList .it-fd')].map(r => [...r.querySelectorAll('.it-sig, .it-whi')].map(x => x.textContent.trim()).join(' ')).filter(Boolean)")
    if not any('RZL-429' in x and 'Z971→C1' in x and '<1 day' in x and 'mass <50%' in x and 'medium' in x for x in fd): out.append(f'the Feed line\'s tags: {fd[:6]}')
    nr = pg.evaluate("(id) => { const r = document.querySelector(`#itNearList > .it-nb[data-it-sys=\"${id}\"]`); return r ? [...r.querySelectorAll('.it-sig')].map(x => x.textContent.trim()) : null; }", F)
    if not nr or not any(x.startswith('DEF-777') for x in nr): out.append(f'Near You\'s row: {nr} (want DEF-777)')
    if str(G) in pg.evaluate("[...document.querySelectorAll('#itNearList > .it-nb')].map(r => r.dataset.itSys)"): out.append('a bare wormhole line made a Near You row')
    lab = pg.evaluate("(id) => itMapWhLabel(itWhStore().rep[id])", A)
    if not lab.startswith('WH RZL-429→C1 +1 ·'): out.append(f'the map label: {lab!r}')
    # the split ring: both colours stroked for a mixed system
    ring = pg.evaluate("""(id) => { itMapFilterSet('sec'); const i = itGraphGet().at.get(id), k = 44 / itm.G; itm.view = {k, tx: itm.W / 2 - itm.P[2 * i] * k, ty: itm.H / 2 - itm.P[2 * i + 1] * k};
      const c = itm.cv.getContext('2d'), s0 = c.stroke, seen = new Set(); c.stroke = function(){ seen.add(String(this.strokeStyle).toLowerCase()); return s0.apply(this, arguments); };
      try{ itMapDraw(); itMapFilterSet('wh'); itMapDraw(); }finally{ c.stroke = s0; } itMapFilterSet('sec'); return [...seen]; }""", Dd)
    if '#a98bd8' not in ring or '#ff5fbf' not in ring: out.append(f'the split ring: colours stroked {ring}')
    # ---- the list: ×, the removal mark, the lines as typed, the Add form
    pg.evaluate("itMapFilterSet('wh'); itWhListOpen(true)"); pg.wait_for_timeout(300)
    if pg.locator('.it-whp-rows .it-sig').count() < 5: out.append('the list shows no IDs')
    for sig in ('KLM-204', 'BKT-772'): pg.locator(f'[data-it-whsrm="{Dd}|{sig}"]').click(); pg.wait_for_timeout(200)
    dd = pg.evaluate("(id) => { const w = itWhStore().rep[id]; return [w.drifter, w.drN, w.sigs.map(s => s.sig), Object.keys(w.goneSig || {}).sort()]; }", Dd)
    if dd != [False, 0, ['XRT-331'], ['BKT-772', 'KLM-204']]: out.append(f'× on both Drifter IDs: {dd}')
    if f'Removed BKT-772 from {N[Dd]}' not in pg.locator('.it-whp-msg').inner_text(): out.append('the list doesn\'t say what was removed')
    back = pg.evaluate("""([id, nm]) => { const old = Date.now() - 600e3, again = (msg, t) => { const p = itParse(msg, itMySys()); itWhTake({t, who: 'Gate Watcher', raw: msg, p}); };
      const w = itWhStore().rep[id], kt = (w.raws.find(r => r.raw.includes('KLM-204')) || {}).t;
      again(`${nm} drifter KLM-204 frig hole`, kt); again(`${nm} drifter BKT`, old); const a = itWhStore().rep[id].sigs.map(s => s.sig);
      again(`${nm} drifter BKT-772`, Date.now() + 1000); return [a, itWhStore().rep[id].sigs.map(s => s.sig)]; }""", [Dd, N[Dd]])
    if 'KLM-204' in back[0] or any(x.startswith('BKT') for x in back[0]) or 'BKT-772' not in back[1]: out.append(f'the removal mark: after older lines {back[0]}, after a newer report {back[1]}')
    same = pg.evaluate("""([id, nm]) => { const w = itWhStore().rep[id], s = w.sigs.find(x => x.sig === 'BKT-772'); itWhSigRemove(id, 'BKT-772');
      const p = itParse(`${nm} wh bkt-772 still there`, itMySys()); itWhTake({t: itWhStore().rep[id].t, who: 'Scout Alt', raw: `${nm} wh bkt-772 still there`, p});
      const a = itWhStore().rep[id].sigs.map(x => x.sig); return [s.t === itWhStore().rep[id].t, a]; }""", [Dd, N[Dd]])
    if not same[0] or 'BKT-772' in same[1]: out.append(f'another line in the same second brought back a removed ID: {same}')
    pg.evaluate("([id, nm]) => { const p = itParse(`${nm} drifter BKT-772`, itMySys()); itWhTake({t: Date.now() + 2000, who: 'Gate Watcher', raw: `${nm} drifter BKT-772 again`, p}); }", [Dd, N[Dd]])
    rl = pg.evaluate("(id) => { localStorage.setItem('tvWormholes', JSON.stringify(itWhStore())); itWhSt = null; const w = itWhStore().rep[id]; return [Object.keys(w.goneSig || {}), w.sigs.map(s => s.sig)]; }", Dd)
    if rl[0] != ['KLM-204'] or 'BKT-772' not in rl[1]: out.append(f'read back: goneSig {rl[0]}, sigs {rl[1]}')
    bad = pg.evaluate("""(ids) => { const [a, b] = ids, st = JSON.parse(localStorage.getItem('tvWormholes')), n = Date.now();
      st.rep[a] = {id: a, t: n, who: 'x', drifter: true, src: 'intel'};   // as 040 wrote it
      st.rep[b] = {id: b, t: n, who: 'x', drifter: false, src: 'intel', sigs: [{sig: 'bad', t: n}, {sig: 'ABC-123', type: 'Q999', t: n, info: {life: 'forever', mass: 'critical'}}, {sig: 'DEF-1', t: n - 100 * 3600e3}],
        raws: [{t: n, raw: 42}, {t: n, raw: 'ok', k: 'weird', set: {sigs: [{sig: 'zzz'}]}}], goneSig: {'<b>': n}};
      localStorage.setItem('tvWormholes', JSON.stringify(st)); itWhSt = null; const A = itWhStore().rep[a], B = itWhStore().rep[b];
      return [A.drifter, !!A.drNoId, A.drN, B.sigs, B.raws, B.goneSig || null]; }""", [E, F])
    if bad[:3] != [True, True, 0] or bad[3] != [{'sig': 'ABC-123', 'part': False, 'type': '', 'info': {'mass': 'critical'}, 't': bad[3][0]['t'] if bad[3] else 0, 'who': ''}] or len(bad[4] or []) != 1 or bad[4][0]['k'] != 'intel' or bad[4][0]['set']['sigs'] or bad[5]:
        out.append(f'the store read back with checks: {bad}')
    pr = pg.evaluate("""(id) => { const st = itWhStore(), w = st.rep[id], n = Date.now(); w.goneSig = {'AAA-111': n - 49 * 3600e3, 'BBB-222': n - 47 * 3600e3};
      itWhPrune(st); const g = Object.keys(st.rep[id].goneSig || {});
      const keep = st.keepH; st.rep[id].sigs = [{sig: 'OLD-100', part: false, type: '', t: n - (keep + 1) * 3600e3, who: ''}, ...st.rep[id].sigs];
      const m = itWhSigMerge(st.rep[id], [{sig: 'NEW-200', part: false}], n, 'x', 'intel').map(s => s.sig); st.rep[id].sigs = st.rep[id].sigs.filter(s => s.sig !== 'OLD-100'); return [g, m]; }""", Dd)
    if pr[0] != ['BBB-222'] or 'OLD-100' in pr[1] or pr[1][:1] != ['NEW-200']: out.append(f'removal marks pruned at 48 h, IDs past the keep setting dropped: {pr}')
    pg.evaluate("itWhChanged()"); pg.wait_for_timeout(200)
    # the lines as typed, under the chevron
    tg = pg.locator(f'[data-it-whraw="{A}"]')
    RB = f"""() => {{ const b = document.querySelector('[data-it-whraw="{A}"]').closest('.it-whp-r').querySelector('.it-whp-raws'); return [!!b.offsetParent, b.innerText]; }}"""
    if tg.get_attribute('aria-expanded') != 'false' or pg.evaluate(RB)[0]: out.append('the lines should be closed at first')
    tg.click(); pg.wait_for_timeout(250)
    vis, txt = pg.evaluate(RB)
    if pg.locator(f'[data-it-whraw="{A}"]').get_attribute('aria-expanded') != 'true' or not vis or 'Scout Alt' not in txt or 'less then 1 day' not in txt: out.append(f'the chevron should show who sent each line: {vis} {txt[:80]!r}')
    if not pg.evaluate(f"document.activeElement && document.activeElement.dataset.itWhraw === '{A}'"): out.append('focus should stay on the chevron')
    pg.locator(f'[data-it-whraw="{A}"]').click(); pg.wait_for_timeout(200)
    # the Add form
    Fm = '.it-whp-add '
    nm = SYSNAME[H]
    pg.fill(Fm + 'input[name=sys]', nm); pg.fill(Fm + 'input[name=sig]', 'ghi-123'); pg.fill(Fm + 'input[name=ty]', 'c247'); pg.wait_for_timeout(100)
    if pg.locator(Fm + 'output[name=dest]').inner_text() != '→ C3': out.append(f'the type hint: {pg.locator(Fm + "output[name=dest]").inner_text()!r}')
    pg.select_option(Fm + 'select[name=life]', 'eol'); pg.select_option(Fm + 'select[name=mass]', 'reduced'); pg.select_option(Fm + 'select[name=size]', 'large')
    pg.locator(Fm + 'button[type=submit]').click(); pg.wait_for_timeout(300)
    h = pg.evaluate("(id) => { const w = itWhStore().rep[id]; return w && [w.src, w.sigs.map(s => [s.sig, s.part, s.type, s.info || null, s.src || '']), w.raws[0].k, w.raws[0].raw, w.raws[0].set.sigs[0].sig]; }", H)
    if h != ['you', [['GHI-123', False, 'C247', {'life': 'eol', 'mass': 'reduced', 'size': 'large'}, 'you']], 'you', f'{nm} GHI-123 c247 EOL <4h mass <50% large', 'GHI-123']: out.append(f'added by hand: {h}')
    if 'GHI-123, C247 → C3, EOL <4h, mass <50%, large' not in pg.locator('.it-whp-msg').inner_text(): out.append(f'the form\'s message: {pg.locator(".it-whp-msg").inner_text()!r}')
    pg.fill(Fm + 'input[name=sys]', N[A]); pg.fill(Fm + 'input[name=sig]', 'rzl'); pg.select_option(Fm + 'select[name=mass]', 'stable'); pg.locator(Fm + 'button[type=submit]').click(); pg.wait_for_timeout(300)
    rz = pg.evaluate("(id) => itWhStore().rep[id].sigs.filter(s => s.sig.startsWith('RZL')).map(s => [s.sig, s.info, s.src || ''])", A)
    if rz != [['RZL-429', {'life': 'lt1d', 'mass': 'stable', 'size': 'medium', 'cls': 'C1-3'}, '']]: out.append(f'"RZL" by hand should update RZL-429\'s mass only: {rz}')
    pg.fill(Fm + 'input[name=sys]', nm); pg.fill(Fm + 'input[name=sig]', '1234'); pg.locator(Fm + 'button[type=submit]').click(); pg.wait_for_timeout(200)
    if pg.locator(Fm + 'input[name=sig]').get_attribute('aria-invalid') != 'true' or 'three letters' not in pg.locator('.it-whp-msg').inner_text(): out.append('a bad ID should be refused at its field')
    for v, hint in [('1-3', 'class C1-3'), ('c13', 'class C13'), ('hs', 'leads to HS'), ('k162', '→ exit'), ('c729', '→ ?')]:
        pg.fill(Fm + 'input[name=ty]', v); pg.wait_for_timeout(50)
        if pg.locator(Fm + 'output[name=dest]').inner_text() != hint: out.append(f'"{v}" reads as {pg.locator(Fm + "output[name=dest]").inner_text()!r} (want {hint!r})')
    pg.fill(Fm + 'input[name=sig]', ''); pg.fill(Fm + 'input[name=ty]', 'x999'); pg.locator(Fm + 'button[type=submit]').click(); pg.wait_for_timeout(200)
    if pg.locator(Fm + 'input[name=ty]').get_attribute('aria-invalid') != 'true': out.append('an unknown type should be refused at its field')
    pg.fill(Fm + 'input[name=ty]', ''); pg.fill(Fm + 'input[name=sys]', '')
    if pg.evaluate("document.querySelectorAll('.it-whp-scan, [data-it-whscan]').length"): out.append('a probe scan paste is on the page (D11 was removed)')
    ctx.close()
    if phone:
        ctx, pg = start(b, html, errs, 390, 844)
        pg.evaluate("""(nm) => { const st = itWhStore(), id = it.names.byLower.get(nm.toLowerCase()); st.rep[id] = itWhDrSet({id, t: Date.now(), who: 'Scout Alt', drifter: false, src: 'intel', sigs: [{sig: 'RZL-429', part: false, type: 'Z971', t: Date.now(), who: 'Scout Alt', info: {life: 'lt1d', mass: 'reduced', size: 'medium'}}, {sig: 'MKV', part: true, type: '', t: Date.now(), who: 'Scout Alt'}], raws: [{t: Date.now(), who: 'Scout Alt', raw: 'x', k: 'intel'}]}); itWhSave(); }""", SYSNAME[near[0]])
        pg.evaluate("() => { const nv = document.querySelector('[data-it-nv=\"map\"]'); if(nv) nv.click(); }"); pg.wait_for_timeout(300)
        pg.evaluate("itMapFilterSet('wh'); itWhListOpen(true)"); pg.wait_for_timeout(300)
        X = pg.evaluate("() => { const b = document.querySelector('.it-whp-rows button.it-sigx'); const r = b && b.getBoundingClientRect(); return [r ? Math.round(r.width) : 0, r ? Math.round(r.height) : 0, document.scrollingElement.scrollWidth <= innerWidth + 1]; }")
        if X[0] < 44 or X[1] < 44 or not X[2]: out.append(f'390 px: the × {X[0]}x{X[1]} px, no sideways scroll {X[2]}')
        ctx.close()
    return out, errs

MUTANTS = [
    ('the reader after the systems', "  const whd = itWhDetails(W, used);   // build queue 044: a wormhole line's signature IDs, type and the words describing the hole, before systems and pilots\n  const sys = itFindSystems(W, used, mySys, force);",
     "  const sys = itFindSystems(W, used, mySys, force);\n  const whd = itWhDetails(W, used);"),
    ('a part merged into the first of two matches', "same = hits.length === 1 ? hits[0] : null;", "same = hits.length >= 1 ? hits[0] : null;"),
    ('an older line bringing back a removed ID', "function itWhSigGone(gs, sig, t){ for(", "function itWhSigGone(gs, sig, t){ return false; for("),
    ('no set on the lines', "k: x.k === 'you' ? 'you' : 'intel', set: x.set});", "k: x.k === 'you' ? 'you' : 'intel'});"),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, 'signature IDs and hole details: the reader, the store, the tags, the list, the map')
    check(not errs, f'no page errors {errs[:3]}')
    for name, old, new in (MUTANTS if not os.environ.get('SIG_FAST') else []):
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
