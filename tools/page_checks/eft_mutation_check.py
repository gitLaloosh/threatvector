"""Page check (build queue 035, pyfa v2.70.0): a fit pasted from pyfa with "Mutated attributes" on reads as the same fit as
without it. pyfa's EFT export (service/port/eft.py) writes a mutated item's ORIGINAL name with a ' [N]' tag -- after the
charge and /OFFLINE on a module line, after 'xN' on a drone or cargo line -- and ends the paste with one block per mutated
item: '[N] <original name>', the mutaplasmid, the attribute line ("maxRange 14000, speedFactor -60"), up to a blank line.
Before 035 the tag stayed on the name (nothing resolved) and the attribute line read as a module with a charge.

Through the real page: parseEftFit on made-up pastes (no real fits, names or pilots), compared with the same fit pasted
without the mutation export; then the Fit Analyzer's own path (buildFitFromEft): a Tristan with a Small Dread Guristas
Synchronizer and a Dread Guristas Drone Damage Amplifier. Since build queue 042 (pyfa v2.70.1, its a2c7b8e) a MUTATED
faction module doesn't count toward the Synchronizer (pyfa reads it as its abyssal type, which has no faction-module
effect), so the mutated paste shows exactly the drone damage the plain paste shows on a copy of the page whose
SYNC_WRITER_EFFECTS is empty (nothing counted), and less than the plain paste on the real page. Two mutants must fail:
the reader before 035, and the paste reader not passing its mutated mark on (042).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/eft_mutation_check.py [index.html]

Ends with 'FAILURES: N' (must be 0).
"""
import sys, os, re, json, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from esi_from_sde import route_all
from playwright.sync_api import sync_playwright

PLAIN = """[Rifter, mutation test]
Federation Navy Stasis Webifier
Light Neutron Blaster II, Void S /OFFLINE

Hobgoblin II x2
"""
MUTA = """[Rifter, mutation test]
Federation Navy Stasis Webifier [1]
Light Neutron Blaster II, Void S /OFFLINE [2]

Hobgoblin II x2 [3]

[1] Federation Navy Stasis Webifier
  Unstable Stasis Webifier Mutaplasmid
  maxRange 14000, speedFactor -60

[2] Light Neutron Blaster II
  Unstable Light Hybrid Turret Mutaplasmid
  damageMultiplier 1.8, falloff 2500
[3] Hobgoblin II
  Exigent Light Drone Firepower Mutaplasmid
  damageMultiplier 1.8
"""
SYNC_PLAIN = """[Tristan, synchronizer]
Dread Guristas Drone Damage Amplifier
Small Dread Guristas Synchronizer

Hobgoblin II x3
"""
SYNC_MUTA = """[Tristan, synchronizer]
Dread Guristas Drone Damage Amplifier [1]
Small Dread Guristas Synchronizer

Hobgoblin II x3

[1] Dread Guristas Drone Damage Amplifier
  Unstable Drone Damage Amplifier Mutaplasmid
  damageMultiplierBonus 25
"""

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
html = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith('--')), os.path.join(ROOT, 'index.html')))
CHROMIUM = os.environ.get('CHROMIUM_PATH') or ('/opt/pw-browsers/chromium' if os.path.exists('/opt/pw-browsers/chromium') else None)
bad = []
def check(c, msg):
    print(('OK   ' if c else 'FAIL ') + msg)
    if not c: bad.append(msg)

PARSE = """async (t) => { const r = await parseEftFit(t);
  return {ship: r.shipTypeId, tally: r.tally, high: [...r.highSlotByFlag.entries()], unresolved: r.unresolved}; }"""

def run(path, p, log):
    """{case: parsed or error} and the Fit Analyzer's drone DPS for the Synchronizer pastes, on the page at path."""
    b = p.chromium.launch(**({'executable_path': CHROMIUM} if CHROMIUM else {}))
    pg = b.new_page(bypass_csp=True, viewport={'width': 1440, 'height': 900}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    route_all(pg)
    pg.goto('file://' + path)
    out = {}
    for k, t in (('plain', PLAIN), ('muta', MUTA)):
        try: out[k] = pg.evaluate(PARSE, t)
        except Exception as ex: out[k] = {'error': str(ex)[:200]}
    pg.eval_on_selector('#tabBtnFit', 'b => b.click()')
    def drone_dps(text):
        pg.evaluate("() => { const r = document.querySelector('#fitAnalyzerResults'); if(r) r.innerHTML = ''; }")
        pg.fill('#fitAnalyzerInput', text); pg.click('#fitAnalyzerBtn')
        try: pg.wait_for_function("() => document.querySelector('#fitAnalyzerResults .fit-layout')", timeout=30000)
        except Exception: return None
        pg.wait_for_timeout(500)
        return pg.evaluate("async (t) => { const {f: ff} = await buildFitFromEft(t); const e = ff.estimate; return e.dpsBreakdown ? JSON.stringify(e.dpsBreakdown.filter(x => /drone/i.test(x.category || x.kind || x.label || ''))) + '|' + e.dpsFixed : String(e.dpsFixed); }", text)
    out['sync_plain'], out['sync_muta'] = drone_dps(SYNC_PLAIN), drone_dps(SYNC_MUTA)
    out['errs'] = errs
    b.close()
    return out

with sync_playwright() as p:
    r = run(html, p, True)
    check('error' not in r['plain'] and r['plain']['unresolved'] == [], f'plain paste: parsed, nothing unresolved ({r["plain"].get("unresolved", r["plain"].get("error"))})')
    check('error' not in r['muta'] and r['muta'].get('unresolved') == [], f'pyfa mutation export: parsed, nothing unresolved ({r["muta"].get("unresolved", r["muta"].get("error"))})')
    check(r['muta'].get('tally') == r['plain'].get('tally') and r['muta'].get('high') == r['plain'].get('high'),
          'pyfa mutation export: the same fit as the plain paste (tally, the blaster\'s charge; the mutation blocks read as nothing)')
    names = json.dumps(r['muta'].get('tally', {}))
    check('Mutaplasmid' not in names and 'maxRange' not in names and 'damageMultiplier' not in names, 'no mutaplasmid or attribute line read as an item')
    check(r['sync_plain'] is not None and r['sync_muta'] is not None and r['sync_plain'] != r['sync_muta'],
          f'Synchronizer + a mutated faction module: less drone damage than the plain paste (pyfa v2.70.1 leaves it out) {r["sync_plain"]} / {r["sync_muta"]}')
    check(not r['errs'], f'no page errors {r["errs"][:2]}')
    src = open(html, encoding='utf-8').read()
    def variant(text, edits, label):
        for a, b in edits:
            if a not in text: check(False, f'{label}: the line {a[:60]!r} was not found (update this check)'); return None
            text = text.replace(a, b, 1)
        with tempfile.NamedTemporaryFile('w', suffix='.html', dir=os.path.dirname(html), delete=False, encoding='utf-8') as f:
            f.write(text); mp = f.name
        try: return run(mp, p, False)
        finally: os.remove(mp)
    # nothing counted (SYNC_WRITER_EFFECTS emptied): the plain paste there is what the mutated paste must show here
    z = variant(src, [(re.search(r'const SYNC_WRITER_EFFECTS = \{.*?\};', src).group(0), 'const SYNC_WRITER_EFFECTS = {};')], 'count-0 copy')
    if z: check(z['sync_plain'] is not None and z['sync_plain'] == r['sync_muta'],
                f'the mutated paste counts nothing: its drone damage equals the plain paste with no faction-module effect {r["sync_muta"]} / {z["sync_plain"]}')
    # mutant (042): the paste reader doesn't pass its mutated mark on, so the mutated module counts (pyfa v2.70.0's rule)
    m2 = variant(src, [('if(m.mutated) mutated[moduleId] = (mutated[moduleId] || 0) + 1;', '')], 'mutant 042')
    if m2: check(m2['sync_muta'] == m2['sync_plain'], f'mutant (the mutated mark dropped) counts it, so this check catches it {m2["sync_muta"]} / {m2["sync_plain"]}')
    # the mutant: the paste reader before build queue 035
    mut = src.replace("const lines = eftStripMutations(text).filter(Boolean);", "const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);", 1)
    mut = mut.replace("const tag = line0.match(EFT_MUTA_TAG_RE);", "const tag = null;", 1)
    if 'const lines = eftStripMutations(text).filter(Boolean);' in mut or 'const tag = null;' not in mut:
        check(False, 'mutant: the reader\'s lines were not found (update this check)')
    else:
        with tempfile.NamedTemporaryFile('w', suffix='.html', dir=os.path.dirname(html), delete=False, encoding='utf-8') as f:
            f.write(mut); mp = f.name
        try:
            m = run(mp, p, False)
            caught = m['muta'].get('unresolved') or m['muta'].get('tally') != m['plain'].get('tally') or 'error' in m['muta']
            check(bool(caught), f'mutant (the reader before 035) is caught: unresolved {m["muta"].get("unresolved")}')
        finally:
            os.remove(mp)

print(f'FAILURES: {len(bad)}')
