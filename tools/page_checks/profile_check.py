"""The profile (v2026.11.01.1; redesigned v2026.11.10.1, build queue 032: Project doc roadmap/profile-redesign-plan.md, mockup
Claude outputs/profile_redesign_mockup.html, look 9 "Annunciator").

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/profile_check.py [index.html]   -> 'FAILURES: N' (must be 0)

The owner: "the profile control in the header should be able to communicate several things to the user without them having to open
the settings dialogue." On the real page (ESI served from pyfa's SDE, made-up pilots, corporations and fits), checks:
  * four lamps, each a button that opens its own tab (the owner: "each tab in the control maps to a tab in the panel that opens"):
    EVE, Pilot, Fit, Intel; pressed again it closes; Esc, the close button and a press outside close; the focus goes back to the lamp
    that opened it; the tabs move with the arrow keys and only the one shown takes Tab;
  * not set up: the silhouette, "Set up your profile", "Log in with EVE", the Fit lamp "+ Add" (it opens Fits at the paste box), Intel
    "Off"; no "N of 3" anywhere (031) and no data-p;
  * set up: the pilot's name (initials without a portrait), the Fit lamp the hull in use, "Use in assessments" in the Fits tab turning it
    on and off ("Vexor · off"); a pilot with no standings at all lights the pilot lamp amber, "No standings"; never a Standings part;
  * the EVE lamp follows the login: dark logged out, cyan logged in, amber when a feature waits for EVE's OK or the login ended;
  * Intel's lamp: off, clear (cyan, the radar sweeping), not working (amber "Stopped", the sweep stopped), near (amber, people, not
    systems: "14 near · 3j"), in system (red, "In system · 6", the pulse); 20 systems x 60 people "999+ near" with the full number in its
    title, 15 systems counted past Near You's 14, a report with no head count counts one, an older tab's message (no h) as before; the
    lamp as wide for "Clear" as for "999+ near · 10j"; no sweep and no pulse with reduced motion; pressed, the profile's Intel tab;
  * long names: a 37-character pilot name and a 60-character fit name on a 33-character hull end in an ellipsis in the header, the
    whole name in its title, at 1440, 1024, 768 and 390 px, without sideways scroll;
  * 20 saved fits: the panel ends above the window's bottom and scrolls inside, the page doesn't move, not trapped (LESSON #96);
  * the Intel card's head and "My Fit" (unchanged); 390 px: the EVE lamp, the portrait and Intel, 44 px; the panel a sheet;
  * mutants (the page with one rule broken) each fail the cases: a lamp opening the wrong tab, the focus not back on the opener, the
    count capped at 14, systems counted instead of people, no "999+", the radar sweeping while off, the sweep ignoring reduced motion,
    the EVE lamp not showing a waiting feature, no "No standings", an older tab's message read as people;
  * no page errors.
"""
import sys, os, json, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from esi_from_sde import route_all
from playwright.sync_api import sync_playwright

HTML = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith('--')),
                            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'index.html')))
PAGE = open(HTML, encoding='utf-8').read()
VEXOR = """[Vexor, Brawl]
Damage Control II
Medium Armor Repairer II
Multispectrum Energized Membrane II
Drone Damage Amplifier II

50MN Microwarpdrive II
Warp Scrambler II
Stasis Webifier II

Heavy Neutron Blaster II, Void M
Heavy Neutron Blaster II, Void M
Heavy Neutron Blaster II, Void M

Medium Auxiliary Nano Pump I
Medium Auxiliary Nano Pump I
Medium Nanobot Accelerator I

Hammerhead II x5
"""
LONG_PILOT = 'Madeup Longname Pilotforthe Checksxyz'   # 37 characters, EVE's longest (EVE_NAME_MAX)
LONG_FIT = 'A Made Up Fit Name That Runs To Sixty Characters For Checkss'   # 60, myShipRename's limit
LONG_HULL = 'Miasmos Quafe Ultramarine Edition'   # 33, the longest ship hull in the page's table (the plan, section 8)
assert len(LONG_PILOT) == 37 and len(LONG_FIT) == 60 and len(LONG_HULL) == 33
fails = 0
def check(ok, msg):
    global fails
    print(('OK   ' if ok else 'FAIL ') + msg); fails += not ok

LAMPS = {'eve': 'profileEve', 'pilot': 'profileBtn', 'fit': 'profileFitL', 'intel': 'intelNear'}
HEAD = """() => { const h = document.querySelector('#intelPanel .it-head'), R = (s) => h.querySelector(s).getBoundingClientRect();
  const t = R('h2'), w = R('#intelSwLabel'), g = R('.it-gear'), i = R('.info-btn'), hr = h.getBoundingClientRect();
  return [Math.round(t.right), Math.round(w.left), Math.round(g.left), Math.round(i.left), Math.round(i.right), Math.round(hr.right), Math.round(hr.width)]; }"""
LAMP = """() => { const b = document.querySelector('#intelNear'), sw = getComputedStyle(b.querySelector('.pf-radar .sw'));
  return {s: document.querySelector('#profile').dataset.s, t: b.querySelector('.pf-vw').textContent, n: b.querySelector('.pf-vn').textContent, title: b.title,
    bg: getComputedStyle(b).backgroundImage, sweep: sw.animationName, pulse: getComputedStyle(document.querySelector('#profile'), '::before').animationName,
    w: Math.round(b.getBoundingClientRect().width), dot: getComputedStyle(document.querySelector('#tabBtnIntel .tb')).display}; }"""
STUB = """() => { if(window.__stub) return; window.__stub = [itNearAll, itThreat, itCount, itR2Stopped, itFeedDown]; window.__nl = [];
  window.itNearAll = () => window.__nl; window.itThreat = (st) => st.t !== false; window.itCount = (st) => st.n; window.itR2Stopped = () => false; window.itFeedDown = () => false; }"""
UNSTUB = "() => { if(window.__stub){ [window.itNearAll, window.itThreat, window.itCount, window.itR2Stopped, window.itFeedDown] = window.__stub; window.__stub = null; } it.on = false; it.other = false; it.remote = null; itHeaderSync(); }"

def intel(pg, js):
    pg.evaluate(STUB); pg.evaluate("(js) => { (new Function(js))(); itHeaderSync(); }", js); pg.wait_for_timeout(80); return pg.evaluate(LAMP)

def cases(pg, out, note=lambda ok, msg: None):
    """The cases the mutants must fail (run on the real page too). A failure appends to out."""
    def ck(ok, msg):
        note(ok, msg)
        if not ok: out.append(msg)
    # each lamp opens its own tab; the focus goes back to it
    for k, lid in LAMPS.items():
        pg.evaluate("() => closeProfile(false)"); pg.click('#' + lid); pg.wait_for_timeout(120)
        sel = pg.evaluate("() => [!document.getElementById('profilePanel').hidden, (document.querySelector('#profileTabs [aria-selected=\"true\"]') || {}).dataset?.pfTab, [...document.querySelectorAll('.pp-pane')].filter(x => !x.hidden).map(x => x.id)]")
        pg.keyboard.press('Escape'); pg.wait_for_timeout(100)
        foc = pg.evaluate("document.activeElement.id")
        ck(sel == [True, k, [f'ppPane-{k}']] and foc == lid, f'the {k} lamp opens the {k} tab (only it shown); Esc closes, the focus back on it {sel} {foc!r}')
    # Intel's lamp: people, uncapped, 999+
    m = intel(pg, "it.on = true; it.other = false; it.err = ''; it.kfNote = ''; window.__nl = Array.from({length: 20}, (_, i) => ({j: 1 + (i % 3), st: {n: 60}}));")
    ck(m['s'] == 'near' and m['t'] == '999+ near · 1j' and m['n'] == '999+' and '1,200 hostiles and neutrals in 20 systems' in m['title'],
       f'20 systems x 60 people: "999+ near · 1j" (the count alone on a phone), the title "1,200 hostiles and neutrals in 20 systems" ({m["t"]!r}, {m["title"][:90]!r})')
    m = intel(pg, "window.__nl = Array.from({length: 15}, (_, i) => ({j: 2 + (i % 2), st: {n: 1}}));")
    ck(m['t'] == '15 near · 2j' and 'in 15 systems' in m['title'], f'15 systems: counted past Near You\'s 14 ({m["t"]!r})')
    m = intel(pg, "window.__nl = [{j: 2, st: {n: 0}}, {j: 3, st: {n: 2}}];")
    ck(m["t"] == "3 near · 2j", f'a report with no head count counts one: 1 + 2 = "3 near · 2j" ({m["t"]!r})')
    m = intel(pg, "window.__nl = [{j: 0, st: {n: 6}}, {j: 2, st: {n: 4}}];")
    ck(m['s'] == 'in' and m['t'] == 'In system · 6', f'in system: "In system · 6", the people in your system ({m["t"]!r})')
    # the radar sweeps only while Intel runs; never with reduced motion
    m = intel(pg, "window.__nl = [];")
    ck(m['s'] == 'clear' and m['sweep'] == 'pfSweep', f'clear: the radar sweeps ({m["sweep"]})')
    m = intel(pg, "it.on = false; it.other = false; it.remote = null;")
    ck(m['s'] == 'off' and m['sweep'] == 'none' and m['t'] == 'Off', f'off: "Off", no sweep ({m["t"]!r}, {m["sweep"]})')
    m = intel(pg, "it.on = true; it.kfNote = 'The kill feed is not answering';")
    ck(m['s'] == 'broken' and m['sweep'] == 'none' and m['t'] == 'Stopped', f'not working: "Stopped", the sweep stopped ({m["t"]!r}, {m["sweep"]})')
    pg.emulate_media(reduced_motion='reduce')
    m = intel(pg, "it.kfNote = ''; window.__nl = [{j: 0, st: {n: 1}}];")
    ck(m['sweep'] == 'none' and m['pulse'] == 'none', f'reduced motion: no sweep, no pulse ({m["sweep"]}, {m["pulse"]})')
    pg.emulate_media(reduced_motion='no-preference')
    # another tab's Intel (026): its message; an older page sends no h
    m = intel(pg, "it.on = false; itLockHear({on: true, s: 'near', n: 3});")
    ck(m['t'] == '3 near' and 'systems with a hostile or neutral report' in m['title'], f'an older tab\'s message (no h): "3 near", systems, as before ({m["t"]!r})')
    m = intel(pg, "itLockHear({on: true, s: 'near', n: 2, h: 9, j: 4, i: 0});")
    ck(m['t'] == '9 near · 4j' and 'from your other Threat Vector tab' in m['title'], f'a newer tab\'s message: "9 near · 4j", from the other tab ({m["t"]!r})')
    pg.evaluate(UNSTUB)
    # the EVE lamp follows the login
    L = "() => document.getElementById('profileEve').dataset.l"
    def eve(js): pg.evaluate("(js) => { (new Function(js))(); renderProfile(); }", js); return pg.evaluate(L)
    s0 = eve("sso.who = null; sso.lost = false;")
    s1 = eve("sso.who = {id: 90000001, name: 'Made Up Main'}; sso.scp = []; ssoOnSave(false); sideEveSave(false); it.set.gameLoc = false;")
    s2 = eve("ssoOnSave(true);")
    s3 = eve("ssoOnSave(false); sso.who = null; sso.lost = true;")
    eve("sso.lost = false; sso.scp = null;")
    ck([s0, s1, s2, s3] == ['off', 'lit', 'warn', 'warn'], f'the EVE lamp: dark logged out, cyan logged in, amber waiting for EVE\'s OK, amber when the login ended {[s0, s1, s2, s3]}')
    # a pilot with no standings: the pilot lamp amber, in its own words; with a typed list, not
    pg.evaluate("() => { Object.assign(side.rec, {pilot: {id: 90000002, name: 'Made Up Typed'}, corp: {id: 98000001, name: 'Made Up Corp', kind: 'corporation'}, alliance: null, friendly: [], hostile: []}); renderProfile(); }")
    a = pg.evaluate("() => [document.getElementById('profileBtn').dataset.l, document.getElementById('profileSub').textContent, !!document.querySelector('#profile .pf-stand, #profile [data-pf-go=\"stand\"]')]")
    pg.evaluate("() => { side.rec.hostile = [{id: 98000004, name: 'Made Up Reds', kind: 'corporation'}]; renderProfile(); }")
    b2 = pg.evaluate("() => [document.getElementById('profileBtn').dataset.l, document.getElementById('profileSub').textContent]")
    pg.evaluate("() => { Object.assign(side.rec, {pilot: null, corp: null, alliance: null, hostile: []}); renderProfile(); }")
    ck(a == ['warn', 'No standings', False] and b2 == ['dim', 'Typed · log in for more'], f'no standings: the pilot lamp amber "No standings", never a Standings part; with a list, "Typed · log in for more" {a} {b2}')

def run_main(b):
    ctx = b.new_context(bypass_csp=True, viewport={'width': 1440, 'height': 900})
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    route_all(pg)
    pg.route('**/characters/*/portrait*', lambda r: r.abort())   # no portrait: the initials
    pg.goto('file://' + HTML); pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_timeout(500)
    # ---- not set up ----
    st = pg.evaluate("""() => { const t = (id) => document.getElementById(id).textContent.trim();
      return [!!document.querySelector('#profileAv svg'), t('profileName'), t('profileSub'), document.getElementById('profileEve').dataset.l, t('profileFitV'), document.querySelector('#intelNear .pf-vw').textContent,
        document.querySelector('#profile').dataset.p === undefined, /of 3/.test(document.getElementById('profile').innerText + document.getElementById('profileBtn').getAttribute('aria-label')),
        getComputedStyle(document.querySelector('#tabBtnIntel .tb')).display, document.querySelectorAll('#profile button').length]; }""")
    check(st == [True, 'Set up your profile', 'Log in with EVE', 'off', '+ Add', 'Off', True, False, 'none', 4],
          f'not set up: the silhouette, "Set up your profile", "Log in with EVE", EVE dark, Fit "+ Add", Intel "Off"; no "of 3", no data-p; four lamps {st}')
    pg.click('#profileBtn'); pg.wait_for_selector('#profilePanel:not([hidden])')
    pan = pg.evaluate("""() => { const p = document.querySelector('#profilePanel'), h = p.querySelector('.pp-head'), x = h.lastElementChild.getBoundingClientRect(), hr = h.getBoundingClientRect();
      return [[...p.querySelectorAll('[role="tab"]')].map(t => t.querySelector('.pp-tt').textContent + ':' + t.tabIndex), h.lastElementChild.className, Math.round(x.width), Math.round(x.height),
        Math.round(hr.right - x.right), document.activeElement.id, !!p.querySelector('#profileSteps, .pp-steps'), /of 3/.test(p.innerText)]; }""")
    check(pan[0] == ['EVE:-1', 'Pilot:0', 'Fits:-1', 'Intel:-1'] and 'x-close' in pan[1] and pan[2] == 32 and pan[3] == 32 and pan[4] <= 0 and pan[5] == 'sidePilot' and not pan[6] and not pan[7],
          f'the panel: tabs EVE / Pilot / Fits / Intel, only the shown one in the Tab order; the close button last in its head, 32 px; the focus on your pilot; no count {pan}')
    pg.focus('#ppTab-pilot'); pg.keyboard.press('ArrowRight'); r1 = pg.evaluate("document.activeElement.id"); pg.keyboard.press('End'); r2 = pg.evaluate("document.activeElement.id")
    pg.keyboard.press('ArrowRight'); r3 = pg.evaluate("[document.activeElement.id, document.getElementById('ppPane-eve').hidden]")
    check([r1, r2, r3] == ['ppTab-fit', 'ppTab-intel', ['ppTab-eve', False]], f'the arrow keys, Home and End move between the tabs, wrapping {[r1, r2, r3]}')
    pg.click('#profilePanel .pp-x'); pg.wait_for_timeout(150)
    c1 = pg.is_hidden('#profilePanel')
    pg.click('#profileBtn'); pg.mouse.click(300, 600); pg.wait_for_timeout(150)
    c2 = pg.is_hidden('#profilePanel')
    pg.click('#profileBtn'); pg.click('#profileBtn'); pg.wait_for_timeout(150)
    check(c1 and c2 and pg.is_hidden('#profilePanel'), 'the close button, a press outside and the same lamp again close it')
    pg.click('#profileFitL'); pg.wait_for_timeout(150)
    check(pg.is_visible('#ppPane-fit') and pg.evaluate("document.activeElement.id") == 'myShipEft', 'the Fit lamp\'s "+ Add" opens Fits at the paste box')
    pg.fill('#myShipEft', VEXOR); pg.click('#myShipPanel [data-act="save"]'); pg.wait_for_selector('#myShipPanel .mys-tiles', timeout=60000)
    pg.keyboard.press('Escape')
    # ---- set up: a made-up pilot, Standings, a fit ----
    pg.evaluate("""() => { Object.assign(side.rec, {pilot: {id: 90000001, name: 'Kael Varos'}, corp: {id: 98000001, name: 'Ashfall Corp', kind: 'corporation'}, alliance: null});
      side.rec.hostile = [{id: 98000004, name: 'Red Tide Syndicate', kind: 'corporation'}]; sideWrite(); renderProfile(); }""")
    pg.wait_for_timeout(400)
    sw = pg.evaluate("""() => [(document.querySelector('#profileAv .pf-ini') || {}).textContent, document.getElementById('profileName').textContent, document.getElementById('profileSub').textContent,
      document.getElementById('profileFitL').dataset.l, document.getElementById('profileFitV').textContent, document.getElementById('profileFitL').title]""")
    check(sw == ['KV', 'Kael Varos', 'Typed · log in for more', 'lit', 'Vexor', 'Fit in use: Vexor · Brawl'], f'set up: the initials without a portrait, the name, its line; the Fit lamp the hull, its title the fit {sw}')
    pg.click('#profileFitL'); pg.wait_for_selector('#myShipUse')
    u0 = pg.evaluate("() => [document.querySelector('#myShipUseRow .pp-fn').textContent, document.getElementById('myShipUse').checked]")
    pg.click('#myShipUse'); pg.wait_for_timeout(200)
    off = pg.evaluate("() => [document.getElementById('myShipUse').checked, myShip.rec.use, document.getElementById('profileFitV').textContent, document.getElementById('profileFitL').dataset.l]")
    pg.click('#myShipUse'); pg.wait_for_timeout(200)
    on = pg.evaluate("() => [document.getElementById('myShipUse').checked, myShip.rec.use, document.getElementById('profileFitV').textContent, getComputedStyle(document.getElementById('myShipUse')).backgroundColor]")
    check(u0 == ['Vexor · Brawl', True] and off == [False, False, 'Vexor · off', 'dim'] and on == [True, True, 'Vexor', 'rgb(31, 111, 128)'],
          f'"Use in assessments" in the Fits tab turns the fit off ("Vexor · off") and on {u0} {off} {on}')
    pg.keyboard.press('Escape')
    head = pg.evaluate("() => { openProfile('pilot'); const h = document.getElementById('profileHead'); return [h.querySelector('.pf-name').textContent, [...h.querySelectorAll('.pp-chip')].map(c => c.textContent)]; }")
    pg.keyboard.press('Escape')
    check(head == ['Kael Varos', ['Typed pilot']], f'the card: the name, "Typed pilot" {head}')
    # ---- the cases (also run against each mutant) ----
    out = []
    cases(pg, out, check)
    # the Intel lamp: as wide for "Clear" as for "999+ near · 10j" (the header doesn't move as numbers change)
    pg.evaluate(STUB)
    w1 = intel(pg, "it.on = true; it.err = ''; it.kfNote = ''; window.__nl = [];")['w']
    w2 = intel(pg, "window.__nl = Array.from({length: 20}, () => ({j: 10, st: {n: 60}}));")['w']
    check(w1 == w2, f'the Intel lamp as wide for "Clear" as for "999+ near · 10j" ({w1}, {w2})')
    m = intel(pg, "window.__nl = [{j: 2, st: {n: 2}}];")
    pg.eval_on_selector('#tabBtnPilot', 'b => b.click()'); pg.click('#intelNear'); pg.wait_for_timeout(200)
    pres = pg.evaluate("() => [!document.getElementById('ppPane-intel').hidden, document.querySelector('#ppPane-intel').innerText.includes('2 hostiles and neutrals in 1 system within'), it.on, document.getElementById('tabIntel').style.display]")
    check(m['dot'] == 'inline-block' and pres[:3] == [True, True, True] and pres[3] != 'block', f'pressing the Intel lamp opens the profile\'s Intel tab (its sentence), leaves Intel on and the page tab where it was {pres}')
    pg.keyboard.press('Escape'); pg.evaluate(UNSTUB)
    # ---- 20 saved fits: the panel stays inside the window ----
    pg.evaluate("""() => { const s = JSON.parse(localStorage.getItem('dscanMyShips')); const f0 = s.fits[0];
      s.fits = Array.from({length: 20}, (_, i) => Object.assign({}, f0, {id: f0.id + (i ? '-' + i : ''), fitName: i ? 'Copy ' + i : f0.fitName})); localStorage.setItem('dscanMyShips', JSON.stringify(s)); }""")
    pg.reload(); pg.wait_for_timeout(500)
    pg.click('#profileFitL'); pg.wait_for_selector('#myShipPanel .mys-row'); pg.wait_for_timeout(300)
    y0 = pg.evaluate('scrollY')
    geo = pg.evaluate("""() => { const p = document.querySelector('#profilePanel'), r = p.getBoundingClientRect(), c = getComputedStyle(p);
      return [document.querySelectorAll('#myShipPanel .mys-row').length, Math.round(r.bottom), innerHeight, p.scrollHeight > p.clientHeight + 50, c.overflowY, c.overscrollBehaviorY]; }""")
    check(geo[0] == 20 and geo[1] <= geo[2] - 16 and geo[3] and geo[4] == 'auto' and geo[5] == 'auto',
          f'20 fits: the panel ends above the window\'s bottom and scrolls inside, the wheel not trapped {geo}')
    pg.mouse.move(1260, 500); pg.mouse.wheel(0, 400); pg.wait_for_timeout(300)
    check(pg.evaluate("document.querySelector('#profilePanel').scrollTop") > 0 and pg.evaluate('scrollY') == y0, 'the wheel scrolls the panel, not the page')
    pg.keyboard.press('Escape')
    # ---- long names ----
    pg.evaluate("""([p, h, f]) => { Object.assign(side.rec, {pilot: {id: 90000003, name: p}}); myShip.rec = Object.assign({}, myShip.rec, {shipName: h, fitName: f, use: true}); renderProfile(); }""", [LONG_PILOT, LONG_HULL, LONG_FIT])
    for w in (1440, 1024, 768, 390):
        pg.set_viewport_size({'width': w, 'height': 900}); pg.wait_for_timeout(250)
        g = pg.evaluate("""() => { const P = document.getElementById('profile').getBoundingClientRect(), n = document.getElementById('profileName'), v = document.getElementById('profileFitV');
          const cut = (e) => e.checkVisibility() ? e.scrollWidth > e.clientWidth : null;
          return {left: Math.round(P.left), right: Math.round(P.right), vw: innerWidth, sx: document.documentElement.scrollWidth, name: cut(n), fit: cut(v),
            nt: document.getElementById('profileBtn').title, ft: document.getElementById('profileFitL').title}; }""")
        okw = g['left'] >= 0 and g['right'] <= g['vw'] and g['sx'] <= g['vw'] and LONG_PILOT in g['nt'] and LONG_FIT in g['ft'] and LONG_HULL in g['ft']
        if w > 1100: okw = okw and g['name'] is True and g['fit'] is True
        check(okw, f'{w} px: long names cut with an ellipsis where shown, the whole name in the titles, the control on screen, no sideways scroll {g}')
    pg.set_viewport_size({'width': 1440, 'height': 900}); pg.wait_for_timeout(200)
    # ---- the Intel card's head: the switch, the gear, the info button at the top right ----
    for w in (1280, 860, 390):
        pg.set_viewport_size({'width': w, 'height': 800}); pg.wait_for_timeout(300); pg.evaluate("() => { switchTab('intel'); itRender(true); }"); pg.wait_for_timeout(150)
        h = pg.evaluate(HEAD)
        check(h[0] < h[1] < h[2] < h[3] and h[5] - h[4] <= 2 and h[1] - h[0] > (100 if w > 600 else 30),
              f'{w} px: the Intel card\'s head: the title, then at the top right the switch, the gear, the info button {h}')
    pg.set_viewport_size({'width': 1280, 'height': 800}); pg.wait_for_timeout(300)
    # ---- "My Fit" ----
    names = pg.evaluate("() => [CARD_NAMES.myshippage, CARD_NAMES['perspective.mine']]")
    pg.eval_on_selector('#tabBtnFit', 'b => b.click()'); pg.wait_for_timeout(200)
    leftover = pg.evaluate("() => (document.body.innerText.match(/\\bMy Ships?\\b|\\bmy ships?\\b/g) || [])")
    check(names == ['Viewing My Fit', 'My Fit Perspective'] and not leftover, f'"My Ship" reads "My Fit": the card names, nothing left in the page\'s text {names} {leftover[:3]}')
    check(not errs, f'no page errors {errs[:3]}')
    ctx.close()
    # ---- 390 px ----
    ctx = b.new_context(bypass_csp=True, viewport={'width': 390, 'height': 800}, is_mobile=True, has_touch=True)
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    route_all(pg); pg.goto('file://' + HTML); pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_timeout(400)
    pg.tap('#profileBtn'); pg.tap('#ppTab-fit'); pg.fill('#myShipEft', VEXOR); pg.tap('#myShipPanel [data-act="save"]'); pg.wait_for_selector('#myShipPanel .mys-tiles', timeout=60000)
    sheet = pg.evaluate("() => { const r = document.querySelector('#profilePanel').getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right), Math.round(r.bottom)]; }")
    tabs = pg.evaluate("() => [...document.querySelectorAll('#profileTabs [role=\"tab\"]')].map(t => Math.round(t.getBoundingClientRect().height))")
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    ph = pg.evaluate("""() => { const p = document.querySelector('#profile').getBoundingClientRect(), t = document.querySelector('.tab-btn').getBoundingClientRect(), vis = (id) => document.getElementById(id).checkVisibility();
      return [Math.round(p.bottom) <= Math.round(t.top) + 1, ['profileEve', 'profileBtn', 'profileFitL', 'intelNear'].map(vis), vis('profileName'),
        ['profileEve', 'profileBtn', 'intelNear'].map(id => Math.round(document.getElementById(id).getBoundingClientRect().height)), document.documentElement.scrollWidth]; }""")
    check(sheet == [0, 390, 800] and ph[0] and ph[1] == [True, True, False, True] and not ph[2] and min(ph[3]) >= 44 and min(tabs) >= 44 and ph[4] <= 390,
          f'390 px: above the tabs, the EVE lamp, the portrait and Intel (44 px), no name line and no Fit lamp; tabs 44 px; the panel a sheet from the bottom {sheet} {ph} {tabs}')
    check(not errs, f'390 px: no page errors {errs[:3]}')
    ctx.close()

def mutate(page, a, b):
    if a not in page:   # the served copy (tools/publish.py) drops the script's indentation
        a, b = ('\n'.join(l.lstrip() for l in s.split('\n')) for s in (a, b))
    assert page.count(a) >= 1, a[:70]
    return page.replace(a, b, 1)
MUTANTS = [
    ('a lamp opening the wrong tab', "    openProfile(k, k === 'pilot' && !profileState().pilot && !sso.who ? '#sidePilot' : null);", "    openProfile('pilot', null);"),
    ('the focus not back on the opener', "  if(returnFocus){ const b = document.getElementById(PF_LAMP[pf.from] || 'profileBtn');", "  if(returnFocus){ const b = document.getElementById('profileBtn');"),
    ('the count capped at 14', "  for(const x of itNearAll()){\n    if(x.j === null || x.j > it.set.range || !itThreat(x.st)) continue;", "  for(const x of itNearAll().slice(0, IT_NEAR_MAX)){\n    if(x.j === null || x.j > it.set.range || !itThreat(x.st)) continue;"),
    ('systems counted, not people', "    h += c; sys++;", "    h++; sys++;"),
    ('no 999+', "function itNum(n){ return n > PF_NUM_MAX ? `${PF_NUM_MAX}+` : String(n); }", "function itNum(n){ return String(n); }"),
    ('the radar sweeping while off', '.pf[data-s="clear"] .pf-radar .sw, .pf[data-s="near"] .pf-radar .sw, .pf[data-s="in"] .pf-radar .sw{opacity:1; animation:pfSweep', '.pf-radar .sw, .pf[data-s="clear"] .pf-radar .sw{opacity:1; animation:pfSweep'),
    ('the sweep ignoring reduced motion', '.pf[data-s="in"]::before, .pf .pf-radar .sw{animation:none !important;}', '.pf[data-s="in"]::before{animation:none !important;}'),
    ('the EVE lamp not showing a waiting feature', "    : m.pend.length ? {s: 'warn',", "    : false ? {s: 'warn',"),
    ('no "No standings"', "st.pilot && !standLive && !lists ? 'No standings' : ''", "''"),
    ('an older tab\'s message read as people', "old: !Number.isFinite(r.h)}", "old: false}"),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    run_main(b)
    tmp = tempfile.mkdtemp(prefix='profile_mut_')
    for name_, a, bb in MUTANTS:
        try: html = mutate(PAGE, a, bb)
        except AssertionError as e: check(False, f'mutant "{name_}": its text is in the page ({e})'); continue
        path = os.path.join(tmp, 'index.html'); open(path, 'w', encoding='utf-8').write(html)
        c = b.new_context(bypass_csp=True, viewport={'width': 1440, 'height': 900}); pg = c.new_page(); route_all(pg)
        pg.route('**/characters/*/portrait*', lambda r: r.abort())
        out = []
        try:
            pg.goto('file://' + path); pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_timeout(500)
            cases(pg, out)
        except Exception as e: out.append(f'error {str(e)[:80]}')
        c.close()
        check(bool(out), f'mutant "{name_}" fails the cases ({out[:1]})')
    b.close()
print(f'FAILURES: {fails}')
sys.exit(1 if fails else 0)
