"""EWAR mockup (claude/roadmap/ewar-plan.md): the real page with two made-up fits and proto_ewar.js, photographed in
each phase (today, A, A+B, A+B+C) at 1440 px and once on a phone (390 px), put into one HTML page.

    PYFA_SRC=/path/to/pyfa python3 -I build_ewar.py <repo>/index.html ewar_mockup.html [shots dir]

Needs fits.py and proto_ewar.js beside it, and the repo's tools/page_checks/esi_from_sde.py (ESI answered from pyfa's
copy of CCP's data: no network). Made-up fits only ("Mockup EWAR", "Mockup blaster"); no player names.
"""
import sys, os, json, base64
HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.abspath(sys.argv[1]); OUT = os.path.abspath(sys.argv[2]); SHOTS = os.path.abspath(sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, 'shots'))
sys.path.insert(0, os.path.join(os.path.dirname(HTML), 'tools', 'page_checks')); sys.path.insert(0, HERE)
from esi_from_sde import route_all, icon_route
import re
from playwright.sync_api import sync_playwright
from fits import THREAT, MINE
os.makedirs(SHOTS, exist_ok=True)
PROTO = open(os.path.join(HERE, 'proto_ewar.js'), encoding='utf-8').read()
R = '#fitAnalyzerResults'
RANGE_M = 4000
PHASES = [(0, 'today', 'Today'), (1, 'a', 'A: disruptors'), (2, 'b', 'A + B: neuts and nos'), (3, 'c', 'A + B + C: damps, lock, ECM')]
errs = []

def settle(pg, ms=500):
    pg.wait_for_timeout(ms); pg.wait_for_function("() => !document.querySelector('.fit-card-busy')", timeout=90000); pg.wait_for_timeout(ms)

def load(b, w, h):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, device_scale_factor=1); pg = ctx.new_page()
    pg.on('pageerror', lambda e: errs.append(f'{w}px: {e}'))
    route_all(pg); pg.route(re.compile(r'https://images\.evetech\.net/types/.*'), icon_route); pg.goto('file://' + HTML); pg.evaluate("localStorage.clear()"); pg.reload()
    if w < 600:
        pg.evaluate("document.querySelector('#tabBtnFit') ? document.querySelector('#tabBtnFit').click() : null")
    else:
        pg.click('#tabBtnFit')
    pg.fill('#fitAnalyzerInput', THREAT); pg.click('#fitAnalyzerBtn'); pg.wait_for_selector(f'{R} .fit-layout'); settle(pg)
    if pg.is_visible('#profileFitL'): pg.click('#profileFitL')
    else: pg.click('#profileBtn'); pg.click('#ppTab-fit')
    pg.fill('#myShipEft', MINE); pg.click('#myShipPanel [data-act="save"]'); pg.wait_for_selector('#myShipPanel .mys-tiles'); pg.keyboard.press('Escape')
    pg.wait_for_function(f"() => {{ const b = document.querySelector('{R} .mys-board'); return b && !/…/.test(b.textContent); }}", timeout=90000); settle(pg, 800)
    pg.add_script_tag(content=PROTO)
    pg.evaluate(f"() => {{ const h = document.querySelector('{R} .mys-switch-host'); mysFightSet(h, 'range', {RANGE_M}); }}"); settle(pg, 400)
    return pg

def shot(pg, sels, name, pad=8):
    boxes = [pg.locator(s).first.bounding_box() for s in sels]
    boxes = [b for b in boxes if b]
    sx, sy = pg.evaluate("[window.scrollX, window.scrollY]")
    boxes = [dict(b, x=b['x'] + sx, y=b['y'] + sy) for b in boxes]
    x0 = min(b['x'] for b in boxes) - pad; y0 = min(b['y'] for b in boxes) - pad
    x1 = max(b['x'] + b['width'] for b in boxes) + pad; y1 = max(b['y'] + b['height'] for b in boxes) + pad
    path = os.path.join(SHOTS, name + '.jpg')
    pg.screenshot(path=path, type='jpeg', quality=78, full_page=True, clip={'x': max(0, x0), 'y': max(0, y0), 'width': x1 - max(0, x0), 'height': y1 - max(0, y0)})
    return path

def why(pg, cell):
    pg.evaluate(f"() => {{ ttkWhyHide(); ttkWhyShow(document.querySelector('{R} .mys-board [data-cell=\"{cell}\"]'), 'tap'); }}"); pg.wait_for_timeout(250)

def texts(pg):
    return pg.evaluate(f"""() => {{ const h = document.querySelector('{R} .mys-switch-host');
      const cells = Object.fromEntries([...document.querySelectorAll('{R} .mys-board [data-cell]')].map(c => [c.dataset.cell, (c.querySelector('.mys-cell-v') || c).textContent]));
      const lines = [...document.querySelectorAll('{R} .proto-ewar-line')].map(e => e.hidden ? '' : e.textContent);
      return {{cells, lines, why: h._why}}; }}""")

def main():
    images, facts = {}, {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = load(b, 1440, 1000)
        for ph, key, _ in PHASES:
            pg.evaluate(f"__ewarProto.set({ph}, '{'off' if ph == 0 else 'thin'}')"); settle(pg, 300)
            facts[key] = texts(pg)
            images[f'{key}_threat'] = shot(pg, [f'{R} .mys-board', f'{R} .mys-threat-view .fl-dmg'], f'{key}_threat')
            why(pg, 'youLast'); images[f'{key}_whyyou'] = shot(pg, [f'{R} .mys-board', '.ttk-why'], f'{key}_whyyou')
            why(pg, 'theyLast'); images[f'{key}_whythem'] = shot(pg, [f'{R} .mys-board', '.ttk-why'], f'{key}_whythem')
            pg.evaluate("ttkWhyHide()")
            pg.click(f'{R} .mys-sw-btn.is-mine'); pg.wait_for_selector(f'{R} .mys-mine-view .fl-dmg .dmg-card'); settle(pg, 300)
            pg.evaluate(f"__ewarProto.set({ph}, '{'off' if ph == 0 else 'thin'}')"); settle(pg, 300)
            images[f'{key}_mine'] = shot(pg, [f'{R} .mys-board', f'{R} .mys-mine-view .fl-dmg'], f'{key}_mine')
            pg.click(f'{R} .mys-sw-btn.is-threat'); pg.wait_for_selector(f'{R} .mys-threat-view:not([hidden])'); settle(pg, 300)
        CH = [f'{R} .mys-threat-view .fl-dmg svg:has(g.dmg-badge)', f'{R} .mys-threat-view .fl-dmg .dmg-ck-rows']
        for style in ('off', 'thin', 'bar'):
            pg.evaluate(f"__ewarProto.set(3, '{style}')"); settle(pg, 400)
            images[f'badge_{style}'] = shot(pg, CH, f'badge_{style}')
        pg.evaluate("__ewarProto.set(3, 'thin')"); settle(pg, 400)
        facts['icons_loaded'] = pg.evaluate(f"() => [...document.querySelectorAll('{R} .mys-threat-view .fl-dmg .dmg-ck-row img')].map(i => i.complete && i.naturalWidth > 0)")
        pg.evaluate(f"() => __ewarProto.highlight(document.querySelector('{R} .mys-threat-view .fl-dmg .dmg-card'), 'Their ECM')"); pg.wait_for_timeout(200)
        images['badge_link'] = shot(pg, CH, 'badge_link')
        sw = pg.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth")
        facts['wide_no_sideways'] = sw
        # phone
        ph = load(b, 390, 844)
        ph.evaluate("__ewarProto.set(3, 'thin')"); settle(ph, 300)
        ph.locator(f'{R} .mys-threat-view .fl-dmg').get_by_text('Damage Application', exact=True).first.click()
        settle(ph, 300)
        ph.evaluate(f"document.querySelector('{R} .mys-board').scrollIntoView({{block: 'start'}})"); ph.wait_for_timeout(300)
        why(ph, 'youLast')
        images['phone_why'] = os.path.join(SHOTS, 'phone_why.jpg'); ph.screenshot(path=images['phone_why'], type='jpeg', quality=78)
        ph.evaluate("ttkWhyHide()")
        images['phone_card'] = os.path.join(SHOTS, 'phone_card.jpg'); ph.locator(f'{R} .mys-threat-view .fl-dmg').screenshot(path=images['phone_card'], type='jpeg', quality=78)
        facts['phone_no_sideways'] = ph.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth")
        b.close()
    json.dump(facts, open(os.path.join(SHOTS, 'facts.json'), 'w'), indent=1, default=str)
    C = {k: facts[k]['cells'] for k in ('today', 'a', 'b', 'c')}
    checks = [
        ('no page errors', not errs),
        ('no sideways scroll at 1440 or 390 px', facts['wide_no_sideways'] and facts['phone_no_sideways']),
        ('A lowers your DPS on them (TDs)', float(C['a']['your'].replace(',', '')) < float(C['today']['your'].replace(',', ''))),
        ('A leaves you-last alone; B shortens it (neuts)', C['a']['youLast'] == C['today']['youLast'] and C['b']['youLast'] != C['a']['youLast']),
        ('their DPS on you unchanged by your-side EWAR', C['today']['their'] == C['c']['their']),
        ('line under their chart only from B on', not any(facts['a']['lines']) and any(facts['b']['lines'])),
        ('every key-row icon loaded (A + B + C, their card)', bool(facts['icons_loaded']) and all(facts['icons_loaded'])),
        ('C adds lock and jam lines to the why panels', any('lock' in t for t in facts['c']['why']['them']['text']) and any('jam' in t for t in facts['c']['why']['you']['text'])),
    ]
    for name, ok in checks: print(('OK   ' if ok else 'FAIL ') + name)
    print('CHECKS FAILED:', sum(not ok for _, ok in checks))
    write_html(images, facts)
    print('ERRORS', errs)

def img(path, alt):
    return f'<img alt="{alt}" src="data:image/jpeg;base64,{base64.b64encode(open(path, "rb").read()).decode()}">'

def write_html(images, facts):
    tabs = ''.join(f'<button type="button" data-ph="{k}"{" aria-pressed=\"true\"" if k == "c" else ""}>{label}</button>' for _, k, label in PHASES)
    panes = ''
    for _, k, label in PHASES:
        panes += f'''<section class="pane" data-ph="{k}"{"" if k == "c" else " hidden"}>
<h3>Their damage on you (threat view)</h3>{img(images[k + "_threat"], label + ": threat view")}
<h3>Your damage on them (My ship view)</h3>{img(images[k + "_mine"], label + ": my ship view")}
<div class="row"><figure><figcaption>“You last” why</figcaption>{img(images[k + "_whyyou"], label + ": you last why")}</figure>
<figure><figcaption>“They last” why</figcaption>{img(images[k + "_whythem"], label + ": they last why")}</figure></div></section>'''
    c = facts['c']['cells']; t = facts['today']['cells']
    page = f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>EWAR in the fight: mockup</title>
<style>body{{background:#0d1014;color:#dfe5ea;font:15px/1.5 system-ui,sans-serif;max-width:1480px;margin:0 auto;padding:20px 16px}} h1{{font-size:22px}} h2{{font-size:18px;color:#f0b43c;margin-top:32px}} h3{{font-size:15px;color:#9fb0bf;margin:22px 0 6px}}
img{{max-width:100%;border:1px solid #26303a;border-radius:6px;display:block}} .row{{display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start}} .row figure{{margin:0;flex:1 1 420px}} figcaption{{color:#9fb0bf;font-size:13px;margin:10px 0 4px}}
.tabs{{position:sticky;top:0;background:#0d1014;padding:10px 0;z-index:2;display:flex;gap:8px;flex-wrap:wrap;border-bottom:1px solid #26303a}} .tabs button{{background:#161c22;color:#dfe5ea;border:1px solid #2c3742;border-radius:5px;padding:8px 12px;font:inherit;cursor:pointer;min-height:44px}}
.tabs button[aria-pressed="true"]{{background:#2a2414;border-color:#f0b43c;color:#f0b43c}} ul{{padding-left:20px}} li{{margin:4px 0}} code{{color:#9fd0e0}} .phone{{display:flex;gap:16px;flex-wrap:wrap}} .phone img{{max-width:390px}}</style></head><body>
<h1>EWAR in the fight: mockup (all three deliveries)</h1>
<p>The real page (main bd04bb5, v2026.11.13.2) with two made-up fits: the threat is an Arbitrator with 2 tracking disruptors (optimal and tracking scripts), a sensor dampener (range script), a multispectral ECM, 2 medium neuts and a small nosferatu; your ship is a blaster Thorax with an armor repairer. Fight range set to {RANGE_M // 1000} km. Pick a phase to see what each delivery adds; <b>A + B + C</b> is the finished feature. The page's own code draws everything; a prototype changes what goes into it (see “How the numbers are made”).</p>
<div class="tabs" role="group" aria-label="Phase">{tabs}</div>
{panes}
<h2>What changes, phase by phase (at {RANGE_M // 1000} km)</h2>
<ul>
<li><b>Today:</b> your DPS on them {t.get("your")}, they last {t.get("theyLast")}, you last {t.get("youLast")}. Their tracking disruptors, dampener, ECM and neuts are on the EWAR card only.</li>
<li><b>A, disruptors:</b> your blasters' optimal, falloff and tracking shrink by their TDs at that range, so your DPS on them is {facts["a"]["cells"].get("your")} and they last {facts["a"]["cells"].get("theyLast")}. Their card's chart gets a <b>D</b> zone for the TDs' reach; your card gets a line under the chart; the “they last” panel says what was cut.</li>
<li><b>B, neuts and nos:</b> their neuts and nosferatu go into your capacitor simulation, so your repairer stops sooner: you last {facts["b"]["cells"].get("youLast")}. The <b>C</b> zone now counts; their card's line and the “you last” panel give the drain and when your capacitor empties.</li>
<li><b>C, targeting:</b> their dampener cuts your lock range (the pin on your card moves and says “damped”); past it you deal nothing, and the same rule holds for every ship (you decided: lock range always counts). Lock times and their ECM's jam chance go into the “why” panels and their card's line. D zones for the damp and ECM reach. You last {c.get("youLast")}, they last {c.get("theyLast")}.</li>
</ul>
<h2>Chart badges: the module's icon (A + B + C, their card)</h2>
<p>Each badge shows the module's own icon (CCP's image server, as the fit ring and module rows already use), with the category colour kept small: a faint thin frame, or a short bar under the icon. The letter stays underneath in the category colour, so if the image server doesn't answer you still see today's letter. The key rows under the chart get the same icon. Hover the module name in a badge's tooltip to check it.</p>
<div class="row"><figure><figcaption>Today: letters only</figcaption>{img(images["badge_off"], "letters")}</figure>
<figure><figcaption>Icon, faint frame (my pick)</figcaption>{img(images["badge_thin"], "thin frame")}</figure>
<figure><figcaption>Icon, colour bar under it</figcaption>{img(images["badge_bar"], "bar")}</figure>
<figure><figcaption>Linked highlight: hovering the ECM badge (or its key row) lights both</figcaption>{img(images["badge_link"], "linked highlight")}</figure></div>
<h2>Phone (390 px), A + B + C</h2>
<div class="phone"><figure><figcaption>The Matchup's “you last” panel opens as a sheet</figcaption>{img(images["phone_why"], "phone why")}</figure><figure><figcaption>Their card, with the line under the chart</figcaption>{img(images["phone_card"], "phone card")}</figure></div>
<h2>How the numbers are made (mockup)</h2>
<ul>
<li>Tracking disruptors: pyfa's handler (Effect6424) as a multiplier on your turrets' optimal, falloff and tracking, scaled by the TD's range factor at each distance and stacking-penalised, then the page's own application maths. Resistances left out (neither hull has one); the build adds them.</li>
<li>Capacitor: the page's own pyfa capacitor simulation with your modules' drains plus each neut and nos cycle (pyfa's <code>addDrain</code>, range factor applied). The page's “you last” then uses that empty time.</li>
<li>Lock range: your lock range times the dampener's stacking-penalised multiplier; lock time is pyfa's <code>calculateLockTime</code>; jam chance is pyfa's <code>jamChance</code> on your sensor strength.</li>
<li>Wording, the D/C letters and the line's place are proposals: tell me what to change.</li>
</ul>
<p style="color:#9fb0bf;font-size:13px">Mockup only. Made-up fits, no player data. Built by <code>build_ewar.py</code> with <code>proto_ewar.js</code> (Project docs <code>claude/roadmap/ewar-mockup/</code>).</p>
<script>document.querySelectorAll('.tabs button').forEach(b => b.addEventListener('click', () => {{
  document.querySelectorAll('.tabs button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
  document.querySelectorAll('.pane').forEach(p => p.hidden = p.dataset.ph !== b.dataset.ph); }}));</script>
</body></html>'''
    open(OUT, 'w', encoding='utf-8').write(page)
    print('wrote', OUT, os.path.getsize(OUT), 'bytes')

main()
