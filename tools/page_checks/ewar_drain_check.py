"""Neutralizers and nosferatu in the fight (build queue 060, phase B of the Project doc roadmap/ewar-plan.md, now roadmap/ewar-plan.md;
mockup Claude outputs/ewar_mockup.html, its "A + B" state without its line under the chart: B2).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/ewar_drain_check.py [index.html]   -> 'FAILURES: N' (must be 0)

The numbers are pyfa's (tools/independent_checks/check_energy_drains.py runs pyfa's Effect6187 / 6197 / 6691 / 6434, Fit.addDrain
and eos/capSim.py against pyfaEnergyDrainsAt and capSimPyfa; check_matchup.py the times). This checks the page around them, with
made-up fits:
  * a threat with two Medium Energy Neutralizer II and a Medium Energy Nosferatu II against your armor-repairing Thorax at 4 km:
    "you last" is shorter than the same fight without the drains, the board shows the Matchup's own time, and its "why" carries
    one drain sentence ("Their 2 neutralizers and 1 nosferatu drain N GJ/s from you at 4 km (nosferatu in full, as pyfa): ...");
    "they last" has none (your Thorax drains nothing); no line under either chart says anything about neutralizers (B2);
  * the threat's Capacitor card: its ring's hover counts the nosferatu's gain and gives the result without it (B1);
  * a Bhaalgorn that holds only on its nosferatu: the Weaknesses card's capacitor flag stays, "without its nosferatu's gain" (B1);
  * no neutralizer on the threat: no drain sentence;
  * 390 px: the sentence is there, no sideways scroll; no page errors anywhere;
  * mutants, each must fail (MUTANTS).
"""
import sys, os, re, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from esi_from_sde import route_all, icon_route
from playwright.sync_api import sync_playwright

HTML = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith('--')),
                            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'index.html')))
PAGE = open(HTML, encoding='utf-8').read()

NEUT_THREAT = """[Arbitrator, Made-up drains]
Damage Control II
Drone Damage Amplifier II

10MN Afterburner II
Warp Scrambler II

Medium Energy Neutralizer II
Medium Energy Neutralizer II
Medium Energy Nosferatu II

Hobgoblin II x5
"""
PLAIN_THREAT = """[Arbitrator, Made-up plain]
Damage Control II

10MN Afterburner II

Hobgoblin II x5
"""
NOS_HOLDS = """[Bhaalgorn, Made-up nos]
Damage Control II

Stasis Webifier II
Stasis Webifier II

Heavy Energy Neutralizer II
Heavy Energy Neutralizer II
Heavy Energy Nosferatu II
"""
THORAX = """[Thorax, Made-up blaster]
Medium Armor Repairer II
Magnetic Field Stabilizer II
Magnetic Field Stabilizer II

10MN Afterburner II
Warp Scrambler II

Heavy Neutron Blaster II, Void M
Heavy Neutron Blaster II, Void M
Heavy Neutron Blaster II, Void M
Heavy Neutron Blaster II, Void M
Heavy Neutron Blaster II, Void M
"""

R = '#fitAnalyzerResults'
MV = f'{R} .mys-mine-view'
TV = f'{R} .mys-threat-view'
NS = {'fails': 0}
def check(ok, msg):
    print(('OK   ' if ok else 'FAIL ') + msg); NS['fails'] += not ok

def settle(pg, ms=400):
    pg.wait_for_timeout(ms); pg.wait_for_function("() => !document.querySelector('.fit-card-busy')", timeout=90000); pg.wait_for_timeout(ms)

def load(b, html, threat, mine=None, width=1440):
    errs = []
    ctx = b.new_context(bypass_csp=True, viewport={'width': width, 'height': 1000}); pg = ctx.new_page()
    pg.on('pageerror', lambda e: errs.append(str(e)))
    route_all(pg); pg.route(re.compile(r'https://images\.evetech\.net/types/.*'), icon_route)
    pg.goto('file://' + html); pg.evaluate("localStorage.clear()"); pg.reload()
    pg.evaluate("document.querySelector('#tabBtnFit').click()")
    pg.fill('#fitAnalyzerInput', threat); pg.click('#fitAnalyzerBtn'); pg.wait_for_selector(f'{R} .fit-layout')
    settle(pg, 800)
    if mine:
        pg.evaluate("() => { const l = document.querySelector('#profileFitL'); if(l && l.offsetParent) l.click(); else { document.querySelector('#profileBtn').click(); document.querySelector('#ppTab-fit').click(); } }")
        pg.fill('#myShipEft', mine); pg.click('#myShipPanel [data-act="save"]'); pg.wait_for_selector('#myShipPanel .mys-tiles'); pg.keyboard.press('Escape')
        pg.wait_for_function(f"() => {{ const b = document.querySelector('{R} .mys-board'); return b && !/…/.test(b.textContent); }}", timeout=90000); pg.wait_for_timeout(800)
        pg.evaluate(f"() => mysFightSet(document.querySelector('{R} .mys-switch-host'), 'range', 4000)"); pg.wait_for_timeout(1200)
    return ctx, pg, errs

def to_mine(pg):
    pg.evaluate(f"() => document.querySelector('{R} .mys-sw-btn.is-mine').click()"); pg.wait_for_selector(f'{MV} .fl-dmg'); settle(pg)
    if pg.locator(f'{MV} .fl-dmg .cc-closed').count():   # a phone: the card starts collapsed
        pg.evaluate(f"() => document.querySelector('{MV} .fl-dmg .cc-toggle[data-card=\"dmg\"]').click()"); settle(pg)
    pg.wait_for_selector(f'{MV} .fl-dmg .dmg-card [data-out="head"]:not(:empty)', timeout=60000)

def open_card(pg, scope, key):
    if pg.locator(f'{scope} button.cc-toggle[data-card="{key}"]').count() and pg.locator(f'{scope} .cc-closed button.cc-toggle[data-card="{key}"]').count():
        pg.evaluate(f"() => document.querySelector('{scope} .cc-closed button.cc-toggle[data-card=\"{key}\"]').click()"); settle(pg)

# The Matchup as the board took it, the same fight with the drains switched off, the board's cell and the "why" panels
FIGHT = f"""() => {{ const host = document.querySelector('{R} .mys-switch-host'), c = document.querySelector('{MV} .fl-dmg .dmg-card')._dmg;
  const m = mysMatchup(c.f, c.mf, c.f.dmg);
  const real = capDrainsAt; capDrainsAt = () => null; let m0; try {{ m0 = mysMatchup(c.f, c.mf, c.f.dmg); }} finally {{ capDrainsAt = real; }}
  const cell = document.querySelector('{R} .mys-board [data-cell="youLast"] .mys-cell-v');
  const notes = [...document.querySelectorAll('{R} .dmg-ckey .dmg-ck-note')].map(e => e.textContent + ' ' + (e.title || ''));
  return {{youLast: m.youLast, plain: m0.youLast, cell: cell && cell.textContent, txt: ttkText(m.youLast), why: (host._why || {{}}), notes,
    drains: m.drains && m.drains.you ? m.drains.you.gjs : null}}; }}"""

def cases(b, html, parts=('fight', 'ring', 'weak', 'none', 'phone')):
    out, errs = [], []
    def need(ok, msg):
        if not ok: out.append(msg)
    if 'fight' in parts or 'ring' in parts:
        ctx, pg, e = load(b, html, NEUT_THREAT, THORAX)
        if 'ring' in parts:   # the threat's own Capacitor card, before the My Fit view
            open_card(pg, TV, 'cp')
            t = pg.evaluate(f"() => {{ const w = document.querySelector('{TV} .cap-ring-wrap'); return w ? w.title : null; }}")
            need(bool(t) and re.search(r"counts its nosferatu's \+[\d.,]+ GJ/s every cycle, as pyfa does; without that gain: (stable at|drains)", t or ''), f'the ring\'s hover: {t!r}')
        if 'fight' in parts:
            to_mine(pg)
            f = pg.evaluate(FIGHT)
            need(f['drains'] and f['drains'] > 0, f'no drain on you at 4 km ({f["drains"]})')
            need(f['youLast'] < f['plain'] - 1e-9, f"you last {f['youLast']} not below the same fight without the drains {f['plain']}")
            need(f['cell'] == f['txt'], f"board's you last {f['cell']!r}, matchup {f['txt']!r}")
            yw = ' '.join((f['why'].get('you') or {}).get('text') or []); tw = ' '.join((f['why'].get('them') or {}).get('text') or [])
            need(bool(re.search(r'Their 2 neutralizers and 1 nosferatu drain [\d.,]+ GJ/s from you at 4 km \(nosferatu in full, as pyfa\): ', yw)), f'"you last" why: {yw!r}')
            need('drain' not in tw or 'drain nothing' in tw, f'"they last" why has a drain sentence: {tw!r}')
            need(not any(re.search(r'neutrali|nosferatu', n, re.I) for n in f['notes']), f'a line under a chart names neutralizers (B2): {f["notes"]}')
        errs += e; ctx.close()
    if 'weak' in parts:
        ctx, pg, e = load(b, html, NOS_HOLDS)
        open_card(pg, R, 'weak')
        t = pg.evaluate(f"() => {{ const g = document.querySelector('{R} .cap-gauge'); return g ? g.title : null; }}")
        need(bool(t) and "without its nosferatu's gain" in t and 'it holds only while its nosferatu has something to drain' in t, f'the Weaknesses flag: {t!r}')
        errs += e; ctx.close()
    if 'none' in parts:
        ctx, pg, e = load(b, html, PLAIN_THREAT, THORAX); to_mine(pg)
        f = pg.evaluate(FIGHT)
        yw = ' '.join((f['why'].get('you') or {}).get('text') or [])
        need(f['drains'] is None and 'GJ/s' not in yw, f'no neutralizer: drains {f["drains"]}, why {yw!r}')
        errs += e; ctx.close()
    if 'phone' in parts:
        ctx, pg, e = load(b, html, NEUT_THREAT, THORAX, 390); to_mine(pg)
        f = pg.evaluate(FIGHT)
        yw = ' '.join((f['why'].get('you') or {}).get('text') or [])
        need('GJ/s from you at 4 km' in yw, f'390 px: why {yw!r}')
        need(pg.evaluate("() => document.scrollingElement.scrollWidth <= innerWidth + 1"), '390 px: sideways scroll')
        errs += e; ctx.close()
    return out, errs

MUTANTS = [
    ('no why sentence', "  if(cIn) why.you.text.push(cIn);\n", "", ('fight',)),
    ('times without the drains', "  const uIn = dIn && capUnderDrains(mEst, dIn.drains), uOut = dOut && capUnderDrains(tEst, dOut.drains);",
     "  const uIn = null, uOut = null;", ('fight',)),
    ('no nosferatu gain', "    if(!noNos) for(const g of capNosGain) if(g) out.push(g.slice());", "", ('ring', 'weak')),
    ('no without-nos hover', "  const capNosTitle = cap.nosGainPerSec && cap.withoutNos && !asbDry", "  const capNosTitle = false", ('ring',)),
    ('no without-nos flag', "  const capWeakNoNos = !!(capBestSim.stable && capBestNoNosSim && !capBestNoNosSim.stable);", "  const capWeakNoNos = false;", ('weak',)),
]

if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch()
        out, errs = cases(b, HTML)
        for o in out: check(False, o)
        check(not out, 'neutralizers and nosferatu: the times, the why, no chart line, the ring\'s hover, the Weaknesses flag, none, phone')
        check(not errs, f'no page errors {errs[:3]}')
        if '--no-mutants' not in sys.argv:
            for name, old, new, parts in MUTANTS:
                if PAGE.count(old) != 1: check(False, f'mutant "{name}": its line isn\'t in the page once'); continue
                with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f:
                    f.write(PAGE.replace(old, new)); mp = f.name
                try:
                    mo, me = cases(b, mp, parts)
                    check(bool(mo) or bool(me), f'mutant "{name}" fails ({(mo or me or ["nothing"])[0][:90]})')
                finally: os.unlink(mp)
        b.close()
    print('FAILURES:', NS['fails'])
    sys.exit(1 if NS['fails'] else 0)
