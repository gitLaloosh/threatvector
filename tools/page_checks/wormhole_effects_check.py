"""The Wormholes tab: a J-space system's effect with its numbers (build queue 062, E1-E3; Project doc roadmap/wormholes-part4-plan.md section 5;
the owner: "we need to add any affects that the hole has", Q12 "Name and numbers (Recommended)"; at the review: "no guessed numbers").

CCP's wormhole systems from the page's own table (INTEL_WH); the numbers from IT_WH_EFF_MOD (tools/gen_wh_table.py); no network. Checks:
  * IT_WH_EFF_MOD against pyfa's copy of CCP's data (PYFA_SRC, the manifest's commit), derived here without the generator's words table: each
    of the 36 beacons "Class 1-6 <effect> Effects" gives the same percent changes (operation 4: (v - 1) x 100; operation 6: v);
  * every effect at every class: whEffLines of a system with that effect and class is the table's row;
  * the System panel: a C1-C6 system's Effect line has one row a line under it (the words and "+58%" / "−29%");
  * a shattered and a Drifter system: with the page's own INTEL_WH.effc (since #72, build 3720952) its beacon's class's numbers; on a table
    without effc (an older page) the effect's name, no numbers, "not in the page's data yet";
  * INTEL_WH.effc (tools/jump_table_update.py): the beacon's own class wins (a shattered system at its beacon's class; a C3 system whose
    beacon says 2 shows class 2); an effc of the wrong length is not used;
  * whEffTxt (the hovers): "Pulsar: Shield HP +58% · …";
  * mutants; no page errors.
"""
import sys, os, re, json, tempfile
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
HTML = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith('--')), os.path.join(REPO, 'index.html')))
PAGE = open(HTML, encoding='utf-8').read()
fails = 0
def check(ok, msg):
    global fails
    print(('PASS ' if ok else 'FAIL ') + msg)
    if not ok: fails += 1

def pyfa_rows():   # {letter: {class: sorted percents}} straight from the beacons, no words table
    sys.path.insert(0, os.path.join(REPO, 'tools'))
    from pyfa_sde import types, td, attrs, effs, _en
    L = {'Black Hole': 'b', 'Cataclysmic Variable': 'c', 'Magnetar': 'm', 'Pulsar': 'p', 'Red Giant': 'r', 'Wolf Rayet': 'w'}
    out = {}
    for t, v in types.items():
        m = re.fullmatch(r'Class (\d) (.+) Effects', _en(v.get('typeName')) or '')
        if v.get('groupID') != 920 or not m or m.group(2) not in L: continue
        d = td.get(str(t), {}); vals = {x['attributeID']: x['value'] for x in d.get('dogmaAttributes', [])}; ops = {}
        for e in d.get('dogmaEffects', []):
            for mi in effs[str(e['effectID'])].get('modifierInfo', []): ops[mi['modifyingAttributeID']] = mi['operation']
        res = {}   # the four resonances of one layer are one line: keep one per layer
        rows = []
        for a, op in ops.items():
            nm = attrs[str(a)]['name']; val = vals[a]
            if op == 6:
                layer = 'armor' if nm.startswith('armor') else 'shield'
                if ('r', layer) in res: continue
                res[('r', layer)] = 1; rows.append(int(round(val)))
            else: rows.append(int(round((val - 1) * 100)))
        out.setdefault(L[m.group(2)], {})[m.group(1)] = sorted(rows)
    return out

SEED = """() => { const T = whTable(), pick = (f) => T.ids.find((id, i) => f(i));
  const c3p = pick(i => T.cls[i] === '3' && T.eff[i] === 'p' && /^J\\d{6}$/.test(T.names[i])), sh = pick(i => T.cls[i] === 's' && T.eff[i] !== '-'),
        dr = pick(i => T.cls[i] === 'd' && T.eff[i] !== '-'), none = pick(i => T.cls[i] === '2' && T.eff[i] === '-');
  const t0 = Date.now() - 3600e3; [c3p, sh, dr, none].forEach((id, i) => whSeen(id, t0 + i * 60e3, false)); whSave();
  return {c3p, sh, dr, none}; }"""
OPEN = "(n) => { if(whS.open !== 'sum') whPnSet('sum', true); whSelect(n); }"
ROWS = "() => { const e = document.querySelector('#whPnSum [data-wh-eff]'); if(!e) return null; const k = [...e.children].map(x => x.textContent); const o = []; for(let i = 0; i < k.length; i += 2) o.push([k[i], k[i + 1]]); return o; }"
SETC = """(f) => { const T = whTable(), s = [...T.cls].map((c, i) => f[T.ids[i]] || (/^[1-6]$/.test(c) && T.eff[i] !== '-' ? c : '-')).join(''); INTEL_WH.effc = s; whT = null; whS.pn = {}; whPaint(true); return s.length; }"""

def start(b, html, w, errs, h=900):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h})
    ctx.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + html); pg.evaluate("localStorage.clear()"); pg.reload()
    pg.wait_for_timeout(300); pg.evaluate("switchTab('wh')"); pg.wait_for_timeout(200)
    return ctx, pg

def cases(b, html, parts=('table', 'panel', 'none', 'effc')):
    out, errs = [], []
    ctx, pg = start(b, html, 1440, errs); ev = pg.evaluate
    S = ev(SEED)
    if not all(S.values()): out.append(f'the seed needs a C3 Pulsar, a shattered and a Drifter system with an effect, and a C2 without one: {S}')
    if 'table' in parts:
        bad = ev("""() => { const T = whTable(), bad = [];
          for(const [L, e] of Object.entries(IT_WH_EFF_MOD)) for(const c of '123456'){
            const id = T.ids.find((x, i) => T.eff[i] === L && T.cls[i] === c); if(!id) continue;
            const got = JSON.stringify(whEffLines(id)), want = JSON.stringify(e.l.map((w, k) => [w, e.c[c][k]])); if(got !== want) bad.push(L + c + ' ' + got); }
          return bad; }""")
        if bad: out.append(f'whEffLines should be the table\'s row at the system\'s class: {bad[:3]}')
        t = ev("(n) => whEffTxt(n)", S['c3p'])
        if not t.startswith('Pulsar: Shield HP +58% · Armor damage taken +29%') or 'Capacitor recharge time −29%' not in t: out.append(f'whEffTxt for a C3 Pulsar: {t!r}')
        if ev("(n) => whEffTxt(n)", S['none']) != '': out.append('a system with no effect: no effect text')
    if 'panel' in parts:
        ev(OPEN, S['c3p']); pg.wait_for_timeout(120)
        rows = ev(ROWS); want = ev("() => IT_WH_EFF_MOD.p.l.map((w, k) => [w, whEffPct(IT_WH_EFF_MOD.p.c['3'][k])])")
        if rows != want: out.append(f'the panel\'s rows under Effect for a C3 Pulsar: {rows}')
        if not rows or ['Shield HP', '+58%'] not in rows or ['Capacitor recharge time', '−29%'] not in rows: out.append(f'a C3 Pulsar: Shield HP +58%, recharge time −29%: {rows}')
        if ev("() => { const e = document.querySelector('#whPnSum [data-wh-eff]'), p = e && e.previousElementSibling; return !!p && /Effect\\s*Pulsar/.test(p.textContent); }") is not True:
            out.append('the rows sit right under the Effect line')
        ev(OPEN, S['none']); pg.wait_for_timeout(100)
        if ev(ROWS) is not None: out.append('no effect: no rows')
    if 'none' in parts:
        # 063: the page's INTEL_WH has effc since the Jump table data pull request of build 3720952 (#72): with it, a shattered or Drifter
        # system shows its beacon's own class's numbers (CCP's data, nothing guessed); a table without it (an older page) shows the name alone
        real = ev("""(ks) => { const T = whTable(); if(!T.effc) return null; return ks.map(n => { const i = T.at.get(n), c = T.effc[i], e = IT_WH_EFF_MOD[T.eff[i]];
          return [c, JSON.stringify(whEffLines(n).map(x => x[1])), /^[1-6]$/.test(c) && e && e.c[c] ? JSON.stringify(e.c[c]) : '[]']; }); }""", [S['sh'], S['dr']])
        if real is not None:
            for k, (c, got, want) in zip(('sh', 'dr'), real):
                if got != want: out.append(f'{k}: the page\'s own effc ({c!r}): the beacon\'s class sets the numbers: {got} (want {want})')
        ev("() => { window.__effc = INTEL_WH.effc; delete INTEL_WH.effc; whT = null; whS.pn = {}; }")   # an older table: no effc yet
        for k in ('sh', 'dr'):
            ev(OPEN, S[k]); pg.wait_for_timeout(100)
            rows = ev(ROWS)
            if ev("(n) => whEffLines(n).length", S[k]) or not rows or rows[0][0] != 'Its numbers' or 'not in the page’s data yet' not in rows[0][1]:
                out.append(f'{k}: the name, no numbers until INTEL_WH.effc (the owner: "no guessed numbers"): {rows}')
            if ev("(n) => whEffTxt(n) === whEff(n) && !!whEff(n)", S[k]) is not True: out.append(f'{k}: the hover text is the name alone')
        ev("() => { if(window.__effc !== undefined) INTEL_WH.effc = window.__effc; whT = null; whS.pn = {}; }")
    if 'effc' in parts:
        n = ev(SETC, {str(S['sh']): '6', str(S['c3p']): '2'})
        if n != ev("whTable().ids.length"): out.append('the made-up effc should be one character a system')
        if ev("(n) => JSON.stringify(whEffLines(n).map(x => x[1]))", S['sh']) != ev("(n) => { const T = whTable(); return JSON.stringify(IT_WH_EFF_MOD[T.eff[T.at.get(n)]].c['6']); }", S['sh']):
            out.append('a shattered system with effc: its beacon\'s class (6) sets the numbers')
        if ev("(n) => JSON.stringify(whEffLines(n).map(x => x[1]))", S['c3p']) != json.dumps(ev("IT_WH_EFF_MOD.p.c['2']"), separators=(',', ':')):
            out.append('effc wins over the system\'s class (a C3 whose beacon says 2)')
        if ev("(n) => whEffLines(n).length", S['dr']) != 0: out.append('effc "-" for a system: no numbers')
        ev("() => { INTEL_WH.effc = INTEL_WH.effc.slice(1); whT = null; }")
        if ev("(n) => JSON.stringify(whEffLines(n).map(x => x[1]))", S['c3p']) != json.dumps(ev("IT_WH_EFF_MOD.p.c['3']"), separators=(',', ':')) or ev("(n) => whEffLines(n).length", S['sh']):
            out.append('an effc of the wrong length is not used (back to the class, none for shattered)')
    ctx.close()
    return out, errs

MUTANTS = [
    ('the strength from the system\'s class with effc', "  if(T.effc) return /^[1-6]$/.test(T.effc[i]) ? T.effc[i] : null;\n", "", ('effc',)),
    ('a guess for shattered systems', "  return /^[1-6]$/.test(T.cls[i]) ? T.cls[i] : null;\n}", "  return /^[1-6]$/.test(T.cls[i]) ? T.cls[i] : '6';\n}", ('none',)),
    ('the sign turned', "return `${v > 0 ? '+' : v < 0 ? '−' : ''}${Math.abs(v)}%`;", "return `${v > 0 ? '−' : v < 0 ? '+' : ''}${Math.abs(v)}%`;", ('panel',)),
    ('no rows under Effect', "<b>${escapeHtml(eff || 'none')}</b></div>${whEffKvHtml(n)}`", "<b>${escapeHtml(eff || 'none')}</b></div>`", ('panel',)),
]

if __name__ == '__main__':
    if not os.environ.get('PYFA_SRC'): check(False, 'PYFA_SRC is needed (a pyfa checkout at the manifest\'s commit)')
    else:
        page = re.search(r'const IT_WH_EFF_MOD = (\{.*?\}\}\});', PAGE)
        tab = json.loads(page.group(1)) if page else {}
        derived = pyfa_rows()
        mine = {L: {c: sorted(v) for c, v in e['c'].items()} for L, e in tab.items()}
        check(sum(len(v) for v in derived.values()) == 36 and mine == derived, f'IT_WH_EFF_MOD matches the 36 beacons in pyfa\'s copy of CCP\'s data ({sum(len(v) for v in derived.values())} read)')
    with sync_playwright() as p:
        b = p.chromium.launch()
        out, errs = cases(b, HTML)
        for o in out: check(False, o)
        check(not out, 'Effects: every effect at every class, the panel\'s rows, shattered and Drifter without numbers, effc')
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
