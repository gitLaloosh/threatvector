"""A probe dragged in from D-Scan is read as probes, never as a pilot and a ship (build queue 049, with the dossier fights delivery).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/intel_probe_check.py [index.html]   -> 'FAILURES: N' (must be 0)

The owner's report (backlog "Intel: a probe dragged in from D-Scan is read as a pilot and a ship", 2026-11-14): a line "<system> <pilot>
Sisters Core Scanner Probe" after he dragged a probe from his D-Scan into the intel channel put the reported pilot, a second "pilot" named
after the probe's first three words (a real character has that name) and a Probe frigate in Near You. "Probe" alone is the Minmatar
exploration frigate, so the reader took the last word as a ship and the rest as a pilot. At the build review: "probes only for now".
Runs intel_check.py's start (its made-up Chatlogs folder, ESI and system names; you in 1DQ1-A) up to Intel turned on, with a made-up
character named "Sisters Core Scanner" (as a real one is), then made-up lines:
  * "<sys> <pilot>* Sisters Core Scanner Probe": the dragged-in pilot only, no ship, the probes tag; "Sisters Core Scanner" never looked up;
  * "<sys> <pilot>* Combat Scanner Probe I" and the same name without its " I": the same;
  * "<sys> <pilot>* Warp Disrupt Probe" (an interdiction probe): the same;
  * "<sys> <pilot>* Probe": the Probe frigate (a ship) still;
  * the names come from INTEL_PROBES (tools/gen_intel_tables.py, CCP's data through pyfa): every one of them reads as probes;
  * mutants, each must fail: the probe table empty; the probe match not run;
  * no page errors.
v2026.11.14.1 fails (the probe read as a ship and a pilot).
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
ONE_WORD['Sisters Core Scanner'] = 96000031   # a real character has this name; a probe's words must never reach it

def start(b, html, errs):
    ctx = b.new_context(bypass_csp=True, viewport={'width': 1440, 'height': 1000})
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); route(ctx)
    pg = ctx.new_page(); pg.goto('file://' + html)
    pg.evaluate("(s) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({channels: ['region.intel'], me: 95000001, range: 3, sound: true, notify: true, forget: 15})); }", SIDE)
    pg.reload(); pg.wait_for_timeout(400)
    setup_logs(pg); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg)
    return ctx, pg

def cases(b, html):
    out, errs = [], []
    IDS_ASKED.clear()
    ctx, pg = start(b, html, errs)
    if not pg.evaluate("typeof itParse === 'function'"): out.append('no Intel'); ctx.close(); return out, errs
    S1, S2, S3, S4, S5 = [SYSNAME[s] for s in near[:5]]
    lines = [f'{S1} {HOST}* Sisters Core Scanner Probe', f'{S2} {HOST}* Combat Scanner Probe I', f'{S3} {HOST}* Combat Scanner Probe',
             f'{S4} {HOST}* Warp Disrupt Probe', f'{S5} {HOST}* Probe']
    t0 = time.time() - 30
    W(pg, F_INTEL, ''.join(line(t0 + i, 'Scout Alt', m) for i, m in enumerate(lines))); tick(pg, 3500)
    R = pg.evaluate("""(lines) => Object.fromEntries(lines.map(l => { const e = it.feed.find(x => x.raw === l); return [l, e ? {
      pilots: e.pilots.map(x => x.name), ships: e.p.ships.map(s => [s.name, s.n]), kw: [...e.p.kw]} : null]; }))""", lines)
    for l in lines[:4]:
        g = R.get(l)
        if not g or g['pilots'] != [HOST] or g['ships'] or 'probes' not in g['kw']:
            out.append(f'{l!r}: want only {HOST}, no ship, the probes tag; got {g}')
    if 'sisters core scanner' in IDS_ASKED or 'warp disrupt' in IDS_ASKED or 'combat scanner' in IDS_ASKED:
        out.append(f"a probe's words were looked up as a pilot {sorted(x for x in IDS_ASKED if 'scanner' in x or 'disrupt' in x)}")
    g = R.get(lines[4])
    if not g or g['ships'] != [['Probe', 1]] or 'probes' in g['kw']:
        out.append(f'{lines[4]!r}: the Probe frigate is still a ship; got {g}')
    # every name in the table reads as probes (the table is CCP's, through pyfa: tools/gen_intel_tables.py)
    bad = pg.evaluate("""() => Object.values(INTEL_PROBES).flatMap(([en, zh]) => [en, zh]).filter(Boolean).filter(n => { const p = itParse('Jita ' + n, null); return p.ships.length || !p.kw.has('probes') || p.runs.length; })""")
    if bad: out.append(f'names in INTEL_PROBES not read as probes: {bad[:5]}')
    n = pg.evaluate("Object.keys(INTEL_PROBES).length")
    if n < 5: out.append(f'INTEL_PROBES has {n} names')
    ctx.close()
    return out, errs

MUTANTS = [
    ('the probe table empty', None, None),
    ('the probe match not run', "  itProbesIn(W, used, kw);   // build queue 049", "  // build queue 049"),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, 'a probe dragged in from D-Scan reads as probes: no pilot, no ship; the Probe frigate still a ship')
    check(not errs, f'no page errors {errs[:3]}')
    for name, old, new in MUTANTS:
        if old is None:
            import re
            m = re.search(r'^const INTEL_PROBES = .*;$', PAGE, re.M)
            if not m: check(False, f'mutant "{name}": INTEL_PROBES isn\'t in the page'); continue
            mut = PAGE[:m.start()] + 'const INTEL_PROBES = {};' + PAGE[m.end():]
        else:
            if PAGE.count(old) != 1: check(False, f'mutant "{name}": its line isn\'t in the page once'); continue
            mut = PAGE.replace(old, new)
        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f:
            f.write(mut); mp = f.name
        try:
            mo, me = cases(b, mp)
            check(bool(mo) or bool(me), f'mutant "{name}" fails ({(mo or me or ["nothing"])[0][:120]})')
        finally: os.unlink(mp)
    b.close()
print('FAILURES:', NS['fails'])
sys.exit(1 if NS['fails'] else 0)
