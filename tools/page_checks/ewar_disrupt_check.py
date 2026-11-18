"""Tracking and guidance disruptors in the damage cards and the Matchup (build queue 050, phase A of the Project doc
roadmap/ewar-plan.md; mockup Claude outputs/ewar_mockup.html).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/ewar_disrupt_check.py [index.html]   -> 'FAILURES: N' (must be 0)

The numbers are pyfa's (tools/independent_checks/check_projected.py runs pyfa's Effect6423 / 6424 / 6694 against the
tool's pyfaDisruptionMults / pyfaDisruptedApp; the regression suite pins disrupted@ values). This checks the page around
them, with made-up fits:
  * a threat with two scripted Tracking Disruptor II against your blaster Thorax at 4 km: your card's line under its
    chart ("Their disruptors: optimal -59%, falloff -59%, tracking -59%", its hover saying it is counted in the DPS);
    the board's "DPS applied to them" is the card's headline, and less than the same fight without the disruptors;
    "they last"'s why opens with the disruptors' sentence, "counted in your damage";
  * the threat's card: the disruptors' zone has a D badge with the Tracking Disruptor II's own icon (type 2109) in
    the chart and in the key row, the image loaded; pointing at the key row lights the badge (.hl) and back;
  * a resisting hull: your Hecate (Sharpshooter Mode, a third of the strength) gets -20% each;
  * a Guidance Disruptor II against your heavy-missile Caracal: explosion radius up, explosion velocity and range down;
  * no disruptors on the threat: no line;
  * 390 px: the line shows, no sideways scroll; no page errors anywhere;
  * mutants, each must fail (MUTANTS).
"""
import sys, os, re, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from esi_from_sde import route_all, icon_route
from playwright.sync_api import sync_playwright

HTML = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith('--')),
                            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'index.html')))
PAGE = open(HTML, encoding='utf-8').read()

TD_THREAT = """[Arbitrator, Made-up disruptors]
Damage Control II
Drone Damage Amplifier II
Drone Damage Amplifier II

Tracking Disruptor II, Optimal Range Disruption Script
Tracking Disruptor II, Tracking Speed Disruption Script
10MN Afterburner II

Medium Energy Neutralizer II

Hobgoblin II x5
"""
GD_THREAT = """[Arbitrator, Made-up guidance]
Damage Control II

Guidance Disruptor II
Guidance Disruptor II
10MN Afterburner II

Medium Energy Neutralizer II

Hobgoblin II x5
"""
PLAIN_THREAT = """[Arbitrator, Made-up plain]
Damage Control II

10MN Afterburner II

Medium Energy Neutralizer II

Hobgoblin II x5
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
HECATE = """[Hecate, Made-up sharpshooter]
Magnetic Field Stabilizer II

1MN Afterburner II

Light Neutron Blaster II, Void S
Light Neutron Blaster II, Void S
Light Neutron Blaster II, Void S
Light Neutron Blaster II, Void S
"""
CARACAL = """[Caracal, Made-up heavies]
Ballistic Control System II

10MN Afterburner II
Large Shield Extender II

Heavy Missile Launcher II, Scourge Heavy Missile
Heavy Missile Launcher II, Scourge Heavy Missile
Heavy Missile Launcher II, Scourge Heavy Missile
Heavy Missile Launcher II, Scourge Heavy Missile
Heavy Missile Launcher II, Scourge Heavy Missile
"""

R = '#fitAnalyzerResults'
MV = f'{R} .mys-mine-view'
TV = f'{R} .mys-threat-view'
NS = {'fails': 0}
def check(ok, msg):
    print(('OK   ' if ok else 'FAIL ') + msg); NS['fails'] += not ok

def settle(pg, ms=400):
    pg.wait_for_timeout(ms); pg.wait_for_function("() => !document.querySelector('.fit-card-busy')", timeout=90000); pg.wait_for_timeout(ms)

def load(b, html, threat, mine, width=1440):
    errs = []
    ctx = b.new_context(bypass_csp=True, viewport={'width': width, 'height': 1000}); pg = ctx.new_page()
    pg.on('pageerror', lambda e: errs.append(str(e)))
    route_all(pg); pg.route(re.compile(r'https://images\.evetech\.net/types/.*'), icon_route)
    pg.goto('file://' + html); pg.evaluate("localStorage.clear()"); pg.reload()
    pg.evaluate("document.querySelector('#tabBtnFit').click()")
    pg.fill('#fitAnalyzerInput', threat); pg.click('#fitAnalyzerBtn'); pg.wait_for_selector(f'{R} .fit-layout')
    settle(pg, 800)
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

def mine_line(pg):
    return pg.evaluate(f"""() => {{ const e = [...document.querySelectorAll('{MV} .dmg-ckey .dmg-ck-note')].find(x => /^(Their|Your) disruptors/.test(x.textContent));
      return e ? [e.textContent, e.title || (e.querySelector('[title]') || {{}}).title || ''] : null; }}""")

# The board's "DPS applied to them", the card's headline, and the same fight with pyfaDisruptedApp switched off
DPS = f"""() => {{ const c = document.querySelector('{MV} .fl-dmg .dmg-card')._dmg; const m = mysMatchup(c.f, c.mf, c.f.dmg);
  const real = pyfaDisruptedApp; pyfaDisruptedApp = (a) => a; let m0; try {{ m0 = mysMatchup(c.f, c.mf, c.f.dmg); }} finally {{ pyfaDisruptedApp = real; }}
  const cell = document.querySelector('{R} .mys-board [data-cell="your"] .mys-cell-v');
  return {{board: cell && cell.textContent, head: document.querySelector('{MV} .fl-dmg .dmg-card [data-out="head"]').textContent,
          your: m.yourDps, plain: m0.yourDps, fmt: dmgFmt(m.yourDps), why: (document.querySelector('{R} .mys-switch-host')._why || {{}}).them}}; }}"""

def cases(b, html, parts=('td', 'badge', 'resist', 'gd', 'none', 'phone')):
    out, errs = [], []
    def need(ok, msg):
        if not ok: out.append(msg)
    if 'td' in parts or 'badge' in parts:
        ctx, pg, e = load(b, html, TD_THREAT, THORAX)
        if 'badge' in parts:
            # the threat's card: their disruptors reach you, so their chart shades them (D) as it shades their web
            z = pg.evaluate(f"""() => [...document.querySelectorAll('{TV} .fl-dmg .dmg-card .dmg-badge.ic')].map(g => [g.getAttribute('data-dmg-z'),
                 (g.querySelector('image') || {{}}).getAttribute ? g.querySelector('image').getAttribute('href') : '', (g.querySelector('title') || {{}}).textContent || ''])""")
            td = [x for x in z if '/types/2109/' in (x[1] or '')]
            need(bool(td), f'threat card: no badge with the Tracking Disruptor II icon ({z[:4]})')
            if td:
                zi = td[0][0]
                row = f'{TV} .fl-dmg .dmg-card .dmg-ck-row[data-dmg-z="{zi}"]'
                need(pg.evaluate(f"() => {{ const i = document.querySelector('{row} img'); return !!i && i.complete && i.naturalWidth > 0 && /types\\/2109\\//.test(i.src); }}"),
                     'threat card: the key row has no loaded Tracking Disruptor II icon')
                need('tracking disruptor' in (pg.text_content(row) or '').lower(), f'threat card: the key row says {pg.text_content(row)!r}')
                pg.locator(row).scroll_into_view_if_needed(); pg.hover(row); pg.wait_for_timeout(300)
                need(pg.evaluate(f"() => !!document.querySelector('{TV} .fl-dmg .dmg-card .dmg-badge.ic.hl[data-dmg-z=\"{zi}\"]') && !!document.querySelector('{row}.hl')"),
                     'threat card: pointing at the key row does not light its badge')
                pg.mouse.move(2, 2); pg.wait_for_timeout(300)
                need(pg.evaluate(f"() => !document.querySelector('{TV} .fl-dmg .dmg-card .hl')"), 'threat card: the light stays after the pointer leaves')
        if 'td' in parts:
            to_mine(pg)
            ln = mine_line(pg)
            need(bool(ln) and ln[0] == 'Their disruptors: optimal −59%, falloff −59%, tracking −59%', f'your card at 4 km: line {ln}')
            need(bool(ln) and 'Counted in the DPS above' in ln[1] and '2 tracking disruptors at 4 km' in ln[1], f'your card: the line\'s hover {ln and ln[1]!r}')
            d = pg.evaluate(DPS)
            need(d['board'] == d['fmt'] and d['head'].startswith(d['fmt']), f"board {d['board']!r} / headline {d['head']!r} / matchup {d['fmt']!r}")
            need(d['your'] < d['plain'] - 1e-9, f"disrupted DPS {d['your']} not below the same fight without disruptors {d['plain']}")
            why = (d['why'] or {}).get('text') or []
            need(bool(why) and why[0].startswith('Their 2 tracking disruptors at 4 km') and why[0].endswith('counted in your damage.'), f'"they last" why: {why[:1]}')
        errs += e; ctx.close()
    if 'resist' in parts:
        ctx, pg, e = load(b, html, TD_THREAT, HECATE); to_mine(pg)
        ln = mine_line(pg)
        need(bool(ln) and ln[0] == 'Their disruptors: optimal −20%, falloff −20%, tracking −20%', f'your Hecate (a third of the strength): line {ln}')
        errs += e; ctx.close()
    if 'gd' in parts:
        ctx, pg, e = load(b, html, GD_THREAT, CARACAL); to_mine(pg)
        ln = mine_line(pg)
        need(bool(ln) and re.fullmatch(r'Their disruptors: explosion radius \+\d+%, explosion velocity −\d+%, range −\d+%', ln[0] or ''), f'your Caracal: line {ln}')
        need(bool(ln) and '2 guidance disruptors' in ln[1] and "your missiles'" in ln[1], f'your Caracal: hover {ln and ln[1]!r}')
        errs += e; ctx.close()
    if 'none' in parts:
        ctx, pg, e = load(b, html, PLAIN_THREAT, THORAX); to_mine(pg)
        need(mine_line(pg) is None, f'no disruptors: a line {mine_line(pg)}')
        errs += e; ctx.close()
    if 'phone' in parts:
        ctx, pg, e = load(b, html, TD_THREAT, THORAX, 390); to_mine(pg)
        ln = mine_line(pg)
        need(bool(ln) and ln[0].startswith('Their disruptors:'), f'390 px: line {ln}')
        need(pg.evaluate("() => document.scrollingElement.scrollWidth <= innerWidth + 1"), '390 px: sideways scroll')
        errs += e; ctx.close()
    return out, errs

MUTANTS = [
    ('no line under the chart', "${note}${dmgDisruptLineHtml(m)}`;", "${note}`;", ('td',)),
    ('the chart not disrupted', "  app = pyfaDisruptedApp(app, tgt.disrupt, q.d);   // build queue 050: the target's tracking / guidance disruptors on these weapons\n  const p = {distance: q.d, tgtSpeed: q.ySpeed",
     "  const p = {distance: q.d, tgtSpeed: q.ySpeed", ('td',)),
    ('the board not disrupted', "  app = pyfaDisruptedApp(app, tgt.disrupt, q.d);   // build queue 050\n", "", ('td',)),
    ('no why sentence', "  if(dT && !dT.none) why.them.text.unshift(`${dT.core}, counted in your damage.`);", "", ('td',)),
    ('no icon in the key', "function dmgCkBadgeHtml(z){\n  if(z.icon) return", "function dmgCkBadgeHtml(z){\n  if(false) return", ('badge',)),
    ('no highlight', "const keyAt = (e) => { const hl = zoneOf(e); if(hl !== (c.hl ?? null)){ c.hl = hl; dmgDraw(card); } };", "const keyAt = (e) => {};", ('badge',)),
    ('resistance ignored in the text', "if(res !== 1) m = (m - 1) * res + 1;", "", ('resist',)),
]

if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch()
        out, errs = cases(b, HTML)
        for o in out: check(False, o)
        check(not out, 'disruptors: the line, the board, the why, the badges and icons, the highlight, a resisting hull, missiles, none, phone')
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
