"""The Wormholes tab's Mass panel: crit or roll a hole (build queue 070; Project doc roadmap/hole-mass-plan.md, mockup Claude outputs/
hole_mass_mockup.html; the owner: "build a button into the wormhole map that lets you calculate how to crit or roll a hole. ... we want simple,
clear steps that will allow you to quickly identify how best to reach the hole state that is desired."), and the + Add form's Linked to after an
Add (070; the owner's bug: "\"add\" system button in map defaults to no connection.", then "go with option A").

CCP's wormhole systems from the page's own tables; ESI answered from pyfa's SDE copy (esi_from_sde, PYFA_SRC); made-up saved fits. Checks:
  * the steps, replayed against holes the answers allow (the page's own hmNext / hmApply; each ship of a group jumps lightest first and the hole
    closes behind the ship whose jump empties it): over 60 holes, Crit it never shows a step marked safe that could close the hole; over 60 holes
    and both finish sides, Roll it never shows a step marked safe that leaves anyone on the wrong side; B274 fresh with one 100,000 / 150,000 t
    ship at 1.8, 2.0 and 2.2 million follows the steps with nobody stranded after safe steps;
  * the risk shown is the share of the holes still possible (boxes that could have that little left, counted here one by one); a seeded run
    of 300;
  * polarization: a ship that jumped the same way under 5 minutes ago waits (or a free group goes); the finisher stays home until less than
    10% while a safe step without it exists, and "Send … instead" is offered when only it has a safe trip; an answer no hole fits starts over;
    groups are counted ("Megathron ×2") and the step says who goes last when it can close the hole; finishing on the other side, the first
    jump is "in";
  * saved fits' masses from the page's fit maths: a Higgs Anchor doubles the hull, a 100MN MWD adds 50,000 t before it, the ZPME mode is
    the fit with the ZPME running (x0.2); a typed hull is its mass plus a MWD of its size, marked "hull only"; a ship over the hole's mass per
    jump is marked; a hole that regains its mass gives no steps;
  * the panel: opened from the toolbar on the system in focus, the hole from its connection, K162 asks for the far side's type (its list
    without K162); answers set the connection's Mass and Undo puts it back (off before the first answer); Start over asks while jumps were made
    (Keep going keeps them) and returns with It says now = the last answer; It's gone asks before removing the connection; the ship rows and
    the Finisher tick are kept after a reload (tvWhMass);
  * + Add's Linked to: with you on the map, a system selected, both, neither; after an Add the list is built again (from an empty map the
    second system is linked to the first);
  * a phone (390 px): the toolbar's controls 44 x 44 without overlapping each other or the rail, the panel without sideways scroll, the
    answers 44 px tall;
  * mutants; no page errors.
"""
import sys, os, json, tempfile, re
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..')); sys.path.insert(0, HERE)
from esi_from_sde import handle as esi_handle
HTML = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith('--')), os.path.join(REPO, 'index.html')))
PAGE = open(HTML, encoding='utf-8').read()
fails = 0
def check(ok, msg):
    global fails
    print(('PASS ' if ok else 'FAIL ') + msg)
    if not ok: fails += 1

# made-up saved fits (their masses are worked out by the page from CCP's data)
FITS = {'v': 2, 'inUse': 'mf1', 'use': False, 'fits': [
    {'v': 1, 'id': 'mf1', 'shipName': 'Megathron', 'fitName': 'Rolling Higgs', 'savedAt': '2026-11-20T00:00:03Z',
     'eft': '[Megathron, Rolling Higgs]\nDamage Control II\n\n500MN Microwarpdrive II\n\nSalvager I\n\nLarge Higgs Anchor I\n'},
    {'v': 1, 'id': 'mf2', 'shipName': 'Phobos', 'fitName': 'Roller', 'savedAt': '2026-11-20T00:00:02Z',
     'eft': '[Phobos, Roller]\nDamage Control II\n\n50MN Microwarpdrive II\n\nZero-Point Mass Entangler\n\nMedium Higgs Anchor I\n'},
    {'v': 1, 'id': 'mf3', 'shipName': 'Heron', 'fitName': 'Light trip', 'savedAt': '2026-11-20T00:00:01Z',
     'eft': '[Heron, Light trip]\nDamage Control II\n\n5MN Microwarpdrive II\n\nSalvager I\n'}]}
# a chain: A (where you are) - Rens through a B274 seen from A, A - C a K162 (far side not known), A - D a D382 at less than 50%
SEED = """() => { const T = whTable(), J = T.names.filter(n => /^J\\d{6}$/.test(n)), [a, c, d] = [120, 480, 777].map(i => whIdOf(J[i])), rens = 30002510;
  const t0 = Date.now() - 3600e3; whSeen(a, t0, false); for(const id of [rens, c, d]) whAddSys(id);
  const l1 = whAddLink(a, rens); whEndSet(l1, a, 'ABC-123', 'B274'); const l2 = whAddLink(a, c); whEndSet(l2, a, 'KKK-162', 'K162');
  const l3 = whAddLink(a, d); whEndSet(l3, a, 'DDD-382', 'D382'); l3.mass = 'reduced';
  whSave(); whEndSave(); whState().drawKey = ''; whSelect(a); return {a, c, d, rens, names: {a: whName(a), c: whName(c), d: whName(d)}}; }"""
# the steps replayed against one true hole (total M, left R): marks every step shown as safe that strands someone (Roll it) or closes the
# hole (Crit it); each ship of a group jumps lightest first, the one whose jump empties it goes through
REPLAY = """([code, st, goal, fin, ships, M, R0, maxSteps]) => {
  const h = hmHole(code), pl = {H: h, M0: h.M0, goal, fin, here: 'A', there: 'B', ships: ships.map(s => ({...s, modes: s.modes.filter(m => m.m <= h.J), at: 'this', last: {out: 0, back: 0}})),
    P: hmPoss(h.M0, st), obs: st, hist: [], done: '', reset: false, finOk: false};
  let R = R0, now = Date.now(), bad = [], n = 0, end = '', outSafe = false;
  // a fresh hole: the answers pin its total to [Mlo, Mhi] exactly (Show Info's words of what's left over the total, everything through so far T)
  let Mlo = 0.9 * h.M0, Mhi = 1.1 * h.M0, T = 0; const BAND = {stable: [0.5, 1], reduced: [0.1, 0.5], critical: [0, 0.1]};
  for(; n < maxSteps; n++){
    const s = hmNext(pl, now); if(!s){ end = pl.done; break; } if(s.none){ end = 'none'; break; }
    const offs = pl.ships.some(sh => sh.at !== pl.fin);   // ships that went out on a safe step must have a safe way back
    if(offs && outSafe && s.risk > 0) bad.push(`step ${n + 1} (${hmShortTxt(pl, s)}): no safe way back after a safe trip out (risk ${s.risk.toFixed(3)}, M ${Math.round(M)})`);
    if(s.risk >= 0.99){ end = 'stuck'; break; }
    if(!offs) outSafe = s.risk === 0;
    if(st === 'fresh' && s.risk === 0 && s.need >= Mlo - T - 1e-6) bad.push(`step ${n + 1} (${hmShortTxt(pl, s)}) marked safe needs ${Math.round(s.need)} t, a hole the answers allow has ${Math.round(Mlo - T)} t left`);
    const safe = s.risk === 0; let closed = false, after = [];
    for(const x of s.g){ if(closed){ after.push(x.i); continue; } R -= x.mo.m; if(R <= 0) closed = true; }
    if(closed){
      for(const x of s.g) if(!after.includes(x.i)){ const sh = pl.ships[x.i]; sh.at = sh.at === 'this' ? 'other' : 'this'; }
      const off = pl.ships.filter(sh => sh.at !== pl.fin).length;
      if(safe && (goal === 'crit' || off)) bad.push(`step ${n + 1} (${hmShortTxt(pl, s)}) marked safe closed the hole (M ${Math.round(M)}, ${off} stranded)`);
      end = off ? 'stranded' : 'closed'; break;
    }
    const said = hmSt(M, R); T += s.m;
    if(st === 'fresh'){ const b = BAND[said]; Mlo = Math.max(Mlo, T / (1 - b[0])); if(b[1] < 1) Mhi = Math.min(Mhi, T / (1 - b[1])); }
    now = Math.max(now, s.wait) + 60e3; hmApply(pl, s, said, now); if(pl.done){ end = pl.done; break; }
  }
  return {bad, end, n}; }"""
SHIPS = {'mega': {'name': 'Megathron', 'label': 'Megathron', 'modes': [{'k': 'hot', 'lab': 'MWD on', 'm': 296800}, {'k': 'cold', 'lab': 'prop off', 'm': 196800}]},
         'phobos': {'name': 'Phobos', 'label': 'Phobos', 'modes': [{'k': 'hot', 'lab': 'MWD on', 'm': 38000}, {'k': 'cold', 'lab': 'prop off', 'm': 28000}, {'k': 'zpme', 'lab': 'ZPME on', 'm': 5600}]},
         'heron': {'name': 'Heron', 'label': 'Heron', 'modes': [{'k': 'hot', 'lab': 'MWD on', 'm': 1650}, {'k': 'cold', 'lab': 'prop off', 'm': 1150}]},
         'bs': {'name': 'Battleship', 'label': 'Battleship', 'modes': [{'k': 'hot', 'lab': 'MWD on', 'm': 150000}, {'k': 'cold', 'lab': 'prop off', 'm': 100000}]}}

def route(ctx):
    def h(r):
        u = r.request.url
        if u.startswith('file:'): return r.continue_()
        if u.startswith('https://esi.evetech.net/'): return esi_handle(r)
        return r.abort()
    ctx.route('**/*', h)

def start(b, html, w, errs, h=900, touch=False, fits=True):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch)
    route(ctx)
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + html); pg.evaluate("([f]) => { localStorage.clear(); if(f) localStorage.setItem('dscanMyShips', JSON.stringify(f)); }", [FITS if fits else None])
    pg.reload(); pg.wait_for_timeout(300); pg.evaluate("switchTab('wh')"); pg.wait_for_timeout(200)
    return ctx, pg

def wait_masses(pg, n, timeout=60000):
    pg.wait_for_function("(n) => { const ls = [...document.querySelectorAll('.hm-pop .hm-m')]; return ls.length >= n && ls.slice(0, n).every(e => e.textContent.trim() && !/working out/.test(e.textContent)); }", arg=n, timeout=timeout)
    return pg.evaluate("() => [...document.querySelectorAll('.hm-pop .hm-m')].map(e => e.textContent.trim())")

def pop_text(pg): return pg.evaluate("() => { const p = document.querySelector('.wh-pop[data-pop=\"mass\"]'); return p && !p.hidden ? p.textContent : null; }")
def link_mass(pg, a, o): return pg.evaluate("([a, o]) => { const s = JSON.parse(localStorage.getItem('tvWhChain') || '{}'); const l = (s.links || []).find(l => (l.a === a && l.b === o) || (l.a === o && l.b === a)); return l ? (l.mass || '') : null; }", [a, o])

def calc_cases(pg, out, parts):
    if parts is None or 'calc' in parts:
        rng = [0.9 + 0.2 * i / 59 for i in range(60)]
        for goal, fin, ships in (('crit', 'this', ['mega', 'phobos', 'heron']), ('roll', 'this', ['mega', 'phobos', 'heron']), ('roll', 'other', ['mega', 'phobos', 'heron']), ('roll', 'this', ['mega', 'mega', 'phobos'])):
            bad = []
            for f in rng:
                M = 2000000 * f
                r = pg.evaluate(REPLAY, ['B274', 'fresh', goal, fin, [SHIPS[s] for s in ships], M, M, 120])
                bad += r['bad']
            if bad: out.append(f'{goal} it, finish {fin}, {"+".join(ships)}: {bad[0]} ({len(bad)} in all)')
        # holes just past the edge of a box (where points and boxes differ), and the light trips at the end
        for goal, fin in (('roll', 'this'), ('crit', 'this'), ('roll', 'other')):
            bad = []
            for k in range(0, 400, 5):
                M = 1.8e6 + 2 * k * 500 + 1
                bad += pg.evaluate(REPLAY, ['B274', 'fresh', goal, fin, [SHIPS[s] for s in ('mega', 'phobos', 'heron')], M, M, 160])['bad']
            if bad: out.append(f'{goal} it, finish {fin}, holes at a box\'s edge: {bad[0]} ({len(bad)} in all)')
        for M in (1.8e6, 2.0e6, 2.2e6):
            r = pg.evaluate(REPLAY, ['B274', 'fresh', 'roll', 'this', [SHIPS['bs']], M, M, 200])
            if r['bad']: out.append(f'one battleship at {M:.0f}: {r["bad"][0]}')
            if r['end'] == 'stranded' and not r['bad']: pass   # stranded only after a step shown with its odds
        # the risk shown is the share of the holes still possible (counted one by one)
        rk = pg.evaluate("""() => { const h = hmHole('B274'); let worst = 0, seen = 0, s = 7;
          const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
          for(let t = 0; t < 300; t++){ const st = ['stable', 'reduced', 'critical'][t % 3], P = hmPoss(h.M0, st), m = 1000 + rnd() * 400000;
            let c = 0; for(const x of P) if(x[1] - x[3] - m <= 0) c++; worst = Math.max(worst, Math.abs(c / P.length - hmShare(P, m))); seen++; }
          return {worst, seen}; }""")
        if rk['worst'] > 1e-9: out.append(f'the risk shown differs from the share of possible holes by {rk["worst"]}')
        # a step marked risky shows its odds and the safe mass; a reduced hole where only the finisher has a safe trip offers it
        fa = pg.evaluate("""([mega, heron]) => { const h = hmHole('D382'), pl = {H: h, M0: h.M0, goal: 'roll', fin: 'this', here: 'A', there: 'B',
            ships: [mega, {...heron, fin: true}].map(s => ({...s, modes: s.modes.filter(m => m.m <= h.J), at: 'this', last: {out: 0, back: 0}})), P: hmPoss(h.M0, 'reduced'), obs: 'reduced', hist: [], done: '', reset: false, finOk: false};
          const st = hmNext(pl, Date.now()); return {fin: st.g.some(x => pl.ships[x.i].fin), alt: !!st.finAlt, risk: st.risk, safe: st.safe}; }""", [SHIPS['mega'], SHIPS['heron']])
        if fa['fin']: out.append('the finisher goes at less than 50% while it is kept for the end')
        if fa['risk'] > 0 and not fa['alt']: out.append('a risky step without the finisher doesn\'t offer "Send … instead"')
        if fa['risk'] > 0 and fa['safe'] % 100: out.append(f'the safe mass isn\'t rounded down to 100 t ({fa["safe"]})')
        # the finisher: home on step 1 (a safe step without it exists), out once the hole says less than 10%
        f1 = pg.evaluate("""([mega, phobos]) => { const h = hmHole('B274'), mk = (st) => ({H: h, M0: h.M0, goal: 'roll', fin: 'this', here: 'A', there: 'B',
            ships: [mega, {...phobos, fin: true}].map(s => ({...s, modes: s.modes.filter(m => m.m <= h.J), at: 'this', last: {out: 0, back: 0}})), P: hmPoss(h.M0, st), obs: st, hist: [], done: '', reset: false, finOk: false});
          const a = hmNext(mk('fresh'), Date.now()), q = mk('critical'), b = hmNext(q, Date.now());
          return {first: a.g.map(x => x.i), crit: b && b.g ? b.g.map(x => [x.i, x.mo.k]) : null}; }""", [SHIPS['mega'], SHIPS['phobos']])
        if 1 in f1['first']: out.append(f'the finisher goes on step 1 ({f1["first"]})')
        if not f1['crit'] or not any(i == 1 for i, k in f1['crit']): out.append(f'at less than 10% the finisher isn\'t sent ({f1["crit"]})')
        # polarization: the group that just jumped out waits, or a free group goes
        po = pg.evaluate("""([mega]) => { const h = hmHole('B274'), pl = {H: h, M0: h.M0, goal: 'crit', fin: 'this', here: 'A', there: 'B',
            ships: [mega].map(s => ({...s, modes: s.modes.filter(m => m.m <= h.J), at: 'this', last: {out: 0, back: 0}})), P: hmPoss(h.M0, 'fresh'), obs: 'fresh', hist: [], done: '', reset: false, finOk: false};
          const now = Date.now(), a = hmNext(pl, now); hmApply(pl, a, 'stable', now); const b = hmNext(pl, now + 1000); hmApply(pl, b, 'stable', now + 2000); const c = hmNext(pl, now + 3000);
          return {dir: [a.dir, b.dir, c.dir], wait: c.wait, at: now}; }""", [SHIPS['mega']])
        if not (po['wait'] and po['wait'] > po['at']): out.append(f'a jump the same way within 5 minutes doesn\'t wait ({po})')
        # an answer no hole fits starts over from what it says now
        im = pg.evaluate("""([mega]) => { const h = hmHole('B274'), pl = {H: h, M0: h.M0, goal: 'roll', fin: 'this', here: 'A', there: 'B',
            ships: [mega].map(s => ({...s, modes: s.modes.filter(m => m.m <= h.J), at: 'this', last: {out: 0, back: 0}})), P: hmPoss(h.M0, 'fresh'), obs: 'fresh', hist: [], done: '', reset: false, finOk: false};
          const a = hmNext(pl, Date.now()); hmApply(pl, a, 'critical', Date.now()); return {reset: pl.reset, n: pl.P.length, obs: pl.obs}; }""", [SHIPS['mega']])
        if not im['reset'] or not im['n'] or im['obs'] != 'critical': out.append(f'an answer no hole fits doesn\'t start over ({im})')
        # words: groups counted, who goes last, in / out by the finish side
        wd = pg.evaluate("""([mega, phobos]) => { const h = hmHole('B274'), mk = (fin, ships, st) => ({H: h, M0: h.M0, goal: 'roll', fin, here: 'A', there: 'B',
            ships: ships.map(s => ({...s, modes: s.modes.filter(m => m.m <= h.J), at: 'this', last: {out: 0, back: 0}})), P: hmPoss(h.M0, st), obs: st, hist: [], done: '', reset: false, finOk: false});
          const p1 = mk('this', [mega, mega, phobos], 'fresh'), s1 = hmNext(p1, Date.now()), p2 = mk('other', [mega], 'fresh'), s2 = hmNext(p2, Date.now());
          const p3 = mk('this', [mega, mega], 'fresh'); p3.ships.forEach(s => s.at = 'other'); p3.P = hmPoss(h.M0, 'critical'); p3.obs = 'critical'; const s3 = hmNext(p3, Date.now());
          const div = document.createElement('div'); div.innerHTML = hmStepHtml(p3, s3);
          return {g: hmShortTxt(p1, s1), d2: hmDirWord(p2, s2), last: div.textContent}; }""", [SHIPS['mega'], SHIPS['phobos']])
        if not re.search(r'Megathron ×2', wd['g']): out.append(f'a group isn\'t counted: {wd["g"]!r}')
        if wd['d2'] != 'in': out.append(f'finishing on the other side, the first jump isn\'t "in" ({wd["d2"]})')
        if 'last.' not in wd['last'] or 'lightest first' not in wd['last']: out.append(f'a group that can close the hole doesn\'t say who goes last: {wd["last"][:160]!r}')

def ui_cases(b, html, out, errs, parts):
    if parts is not None and not ({'fit', 'ui'} & set(parts)): return
    ctx, pg = start(b, html, 1440, errs)
    calc_cases(pg, out, parts)
    if parts is not None and not ({'fit', 'ui'} & set(parts)): ctx.close(); return
    ids = pg.evaluate(SEED); pg.evaluate("whPaint(true)")
    pg.click('[data-wh-pop="mass"]'); pg.wait_for_timeout(200)
    t = pop_text(pg) or ''
    if 'Crit or roll a hole' not in t: out.append('the Mass button doesn\'t open the panel'); ctx.close(); return
    if not re.search(r'B274 → \w+ · 2,000,000 t total', t): out.append(f'the hole line isn\'t the B274\'s: {t[:200]!r}')
    # ships: the three saved fits and a typed hull
    for i, fid in enumerate(('mf1', 'mf2')):
        pg.click('.hm-pop [data-hm="add"]'); pg.select_option(f'.hm-pop [data-hm-ship="{i}"]', f'fit:{fid}'); pg.wait_for_timeout(100)
    pg.click('.hm-pop [data-hm="add"]'); f = pg.locator('.hm-pop [data-hm-hull="2"]'); f.fill('megathron'); f.dispatch_event('change')
    ms = wait_masses(pg, 3)
    if parts is None or 'fit' in parts:
        if '296,800 t hot (MWD on) · 196,800 t cold' not in ms[0]: out.append(f'the Megathron with a Higgs Anchor: {ms[0]!r}')
        if not ('38,000 t hot (MWD on) · 28,000 t cold' in ms[1] and '5,600 t cold, ZPME on' in ms[1]): out.append(f'the Phobos with a ZPME: {ms[1]!r}')
        if not ('148,400 t hot (MWD on) · 98,400 t cold' in ms[2] and 'hull only' in ms[2]): out.append(f'a typed hull: {ms[2]!r}')
    if parts is not None and 'ui' not in parts: ctx.close(); return
    # the Finisher tick and the rows kept
    pg.check('.hm-pop [data-hm-fin="1"]'); pg.wait_for_timeout(100)
    kept = pg.evaluate("() => JSON.parse(localStorage.getItem('tvWhMass') || 'null')")
    if not (kept and kept.get('v') == 1 and [r.get('fit') or r.get('hull') for r in kept['ships']] == ['mf1', 'mf2', 'Megathron'] and kept['ships'][1].get('fin')):
        out.append(f'tvWhMass doesn\'t keep the rows and the Finisher tick: {kept}')
    # too heavy and a hole that regains its mass
    small = pg.evaluate("() => Object.entries(IT_WH_LIFE).find(([c, v]) => !v[3] && v[2] < 190000 && c !== 'K162')[0]")
    pg.select_option('.hm-pop [data-hm="link"]', ''); ty = pg.locator('.hm-pop [data-hm="ty"]'); ty.fill(small); ty.dispatch_event('change'); pg.wait_for_timeout(150)
    t = pop_text(pg)
    if 'too heavy for this hole' not in t and 'fits this hole' not in t: out.append(f'a ship heavier than {small}\'s mass per jump isn\'t marked')
    ty = pg.locator('.hm-pop [data-hm="ty"]'); ty.fill('A009'); ty.dispatch_event('change'); pg.wait_for_timeout(150)
    if 'regains its mass' not in pop_text(pg) or not pg.evaluate("() => document.querySelector('.hm-pop [data-hm=\"go\"]').disabled"): out.append('a hole that regains its mass still offers steps')
    # K162: asks for the far side's type, its list without K162
    k = pg.evaluate("([a, c]) => whLinkKey(a, c)", [ids['a'], ids['c']]); pg.select_option('.hm-pop [data-hm="link"]', k); pg.wait_for_timeout(150)
    ph = pg.evaluate("() => { const i = document.querySelector('.hm-pop [data-hm=\"ty\"]'); return i ? [i.placeholder, [...document.querySelectorAll('#whMassTyDl option')].some(o => o.value === 'K162')] : null; }")
    if not ph or 'K162: what’s the type on the other side' not in ph[0] or ph[1]: out.append(f'a K162 with no far side: {ph}')
    # the B274 again, without the typed hull: steps, answers, the connection's Mass, Undo
    k = pg.evaluate("([a, r]) => whLinkKey(a, r)", [ids['a'], ids['rens']]); pg.select_option('.hm-pop [data-hm="link"]', k); pg.wait_for_timeout(100)
    pg.click('.hm-pop [data-hm-rm="2"]'); pg.wait_for_timeout(100)
    if not pg.evaluate("() => !document.querySelector('.hm-pop [data-hm=\"undo\"]')"): out.append('Undo shows before the steps start')
    pg.click('.hm-pop [data-hm="go"]'); pg.wait_for_timeout(300)
    t = pop_text(pg)
    if not re.search(r'Steps · about \d', t) or not pg.locator('.hm-pop .hm-now').count(): out.append(f'Show the steps shows no step: {t[:200]!r}')
    if not pg.evaluate("() => document.querySelector('.hm-pop [data-hm=\"undo\"]').disabled"): out.append('Undo isn\'t off before the first answer')
    if 'Phobos' in (pg.locator('.hm-pop .hm-now').text_content() or ''): out.append('the finisher (Phobos) goes on step 1')
    before = link_mass(pg, ids['a'], ids['rens'])
    say = pg.evaluate("() => { const H = hmState(); return hmPossibleSays(H.pl, H.step).find(k => k !== 'gone'); }")
    pg.click(f'.hm-pop [data-hm-say="{say}"]'); pg.wait_for_timeout(300)
    if link_mass(pg, ids['a'], ids['rens']) != say: out.append(f'an answer doesn\'t set the connection\'s Mass ({link_mass(pg, ids["a"], ids["rens"])!r}, answered {say})')
    if pg.locator('.hm-pop .hm-done li').count() != 1: out.append('the answered step isn\'t listed')
    pg.click('.hm-pop [data-hm="undo"]'); pg.wait_for_timeout(300)
    if link_mass(pg, ids['a'], ids['rens']) != before: out.append(f'Undo doesn\'t put the connection\'s Mass back ({link_mass(pg, ids["a"], ids["rens"])!r}, was {before!r})')
    if pg.locator('.hm-pop .hm-done li').count() or not pg.evaluate("() => document.querySelector('.hm-pop [data-hm=\"undo\"]').disabled"): out.append('Undo doesn\'t go back to step 1')
    # Start over: asks while jumps were made; Keep going keeps them; Start over returns with It says now = the last answer
    pg.click(f'.hm-pop [data-hm-say="{say}"]'); pg.wait_for_timeout(300)
    pg.click('.hm-pop [data-hm="reset"]'); pg.wait_for_timeout(150)
    if 'Start over? The 1 step so far are forgotten' not in pop_text(pg): out.append('Start over doesn\'t ask while jumps were made')
    pg.click('.hm-pop [data-wh-ask="hm-rs-no"]'); pg.wait_for_timeout(150)
    if pg.locator('.hm-pop .hm-done li').count() != 1: out.append('Keep going doesn\'t keep the step')
    pg.click('.hm-pop [data-hm="reset"]'); pg.wait_for_timeout(150); pg.click('.hm-pop [data-wh-ask="hm-rs"]'); pg.wait_for_timeout(200)
    sv = pg.evaluate("() => { const s = document.querySelector('.hm-pop [data-hm=\"st\"]'); return s ? s.value : null; }")
    if sv != say: out.append(f'Start over doesn\'t return to the setup with It says now = the last answer ({sv!r}, answered {say})')
    # It's gone: asks before removing the connection
    pg.click('.hm-pop [data-hm="go"]'); pg.wait_for_timeout(300); pg.click('.hm-pop [data-hm-say="gone"]'); pg.wait_for_timeout(300)
    t = pop_text(pg)
    if f'Remove the connection to {pg.evaluate("(r) => whName(r)", ids["rens"])}?' not in t: out.append(f'It\'s gone doesn\'t ask to remove the connection: {t[-200:]!r}')
    elif link_mass(pg, ids['a'], ids['rens']) is None: out.append('the connection went before Remove was pressed')
    else:
        pg.click('.hm-pop [data-wh-ask="hm-rm"]'); pg.wait_for_timeout(300)
        if link_mass(pg, ids['a'], ids['rens']) is not None: out.append('Remove doesn\'t remove the connection')
    # the rows after a reload
    pg.reload(); pg.wait_for_timeout(300); pg.evaluate("switchTab('wh')"); pg.wait_for_timeout(200); pg.click('[data-wh-pop="mass"]'); pg.wait_for_timeout(200)
    r = pg.evaluate("() => [[...document.querySelectorAll('.hm-pop [data-hm-ship]')].map(s => s.value), [...document.querySelectorAll('.hm-pop [data-hm-fin]')].map(c => c.checked)]")
    if r != [['fit:mf1', 'fit:mf2'], [False, True]]: out.append(f'the ship rows after a reload: {r}')
    ctx.close()

def link_cases(b, html, out, errs, parts):
    if parts is not None and 'link' not in parts: return
    ctx, pg = start(b, html, 1440, errs, fits=False)
    r = pg.evaluate("""() => { const [a, c] = ['J100001', 'J100009'].map(n => whNameIn(n)); whMake(); const S = whState(), res = {};
      const open = (k) => { whPopClose(); whPop('add'); const f = S.el.querySelector('.wh-addf'); res[k] = f.link.value; };
      open('empty'); whPop('add'); const f = S.el.querySelector('.wh-addf');
      f.sys.value = 'J100001'; whAddForm(f); res.afterOne = f.link.value; f.sys.value = 'J100009'; whAddForm(f); res.links = S.st.links.length;
      S.last = a; S.sel = null; open('you'); S.last = null; whSelect(c); open('sel'); S.last = a; whSelect(c); open('both');
      res.ids = [a, c]; return res; }""")
    a, c = r['ids']
    if r['empty'] != '': out.append(f'+ Add on an empty map isn\'t loose ({r["empty"]!r})')
    if r['afterOne'] != str(a) or r['links'] != 1: out.append(f'after an Add, Linked to isn\'t built again: {r["afterOne"]!r}, {r["links"]} connection(s)')
    if r['you'] != str(a): out.append(f'+ Add with you on the map: {r["you"]!r}')
    if r['sel'] != str(c): out.append(f'+ Add with a system selected: {r["sel"]!r}')
    if r['both'] != str(a): out.append(f'+ Add with both, where you are first: {r["both"]!r}')
    ctx.close()

def phone_cases(b, html, out, errs, parts):
    if parts is not None and 'phone' not in parts: return
    ctx, pg = start(b, html, 390, errs, h=844, touch=True)
    ids = pg.evaluate(SEED); pg.evaluate("whPaint(true)"); pg.wait_for_timeout(200)
    bx = pg.evaluate("""() => { const r = (e) => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.width, b.height]; };
      const cs = [...document.querySelectorAll('.wh-ctl button, .wh-ctl summary.info-btn')].filter(e => e.offsetParent && getComputedStyle(e).display !== 'none').map(r);
      const rail = document.querySelector('.wh-box .wh-rail'); return {cs, rail: rail && !rail.hidden ? r(rail) : null}; }""")
    small = [c for c in bx['cs'] if c[2] < 43.5 or c[3] < 43.5]
    if small: out.append(f'a phone: toolbar controls under 44 x 44: {small[:3]}')
    ov = lambda p, q: p[0] < q[0] + q[2] - 0.5 and q[0] < p[0] + p[2] - 0.5 and p[1] < q[1] + q[3] - 0.5 and q[1] < p[1] + p[3] - 0.5
    if any(ov(p, q) for i, p in enumerate(bx['cs']) for q in bx['cs'][i + 1:]): out.append('a phone: toolbar controls overlap')
    if bx['rail'] and any(ov(p, bx['rail']) for p in bx['cs']): out.append(f'a phone: the toolbar covers the rail ({bx["rail"]})')
    pg.click('[data-wh-pop="mass"]'); pg.wait_for_timeout(200)
    pg.click('.hm-pop [data-hm="add"]'); pg.select_option('.hm-pop [data-hm-ship="0"]', 'fit:mf1'); wait_masses(pg, 1)
    pg.click('.hm-pop [data-hm="go"]'); pg.wait_for_timeout(300)
    s = pg.evaluate("""() => { const p = document.querySelector('.hm-pop'); return {sw: p.scrollWidth - p.clientWidth, doc: document.documentElement.scrollWidth - innerWidth,
      ans: [...p.querySelectorAll('[data-hm-say]')].map(e => e.getBoundingClientRect().height)}; }""")
    if s['sw'] > 0 or s['doc'] > 0: out.append(f'a phone: sideways scroll (panel {s["sw"]} px, page {s["doc"]} px)')
    if not s['ans'] or min(s['ans']) < 43.5: out.append(f'a phone: answer buttons under 44 px ({s["ans"]})')
    ctx.close()

def cases(b, html, parts=None):
    out, errs = [], []
    ui_cases(b, html, out, errs, parts)
    if parts is not None and 'calc' in parts and not ({'fit', 'ui'} & set(parts)):
        ctx, pg = start(b, html, 1440, errs, fits=False); calc_cases(pg, out, parts); ctx.close()
    link_cases(b, html, out, errs, parts)
    phone_cases(b, html, out, errs, parts)
    return out, errs

MUTANTS = [
    ('no ±10% (the exact total)', "for(let i = 0; i < n; i++){ const M = M0 * 0.9 + (2 * i + 1) * h; P.push([M, M, h, h]); } return P; }",
     "for(let i = 0; i < n; i++){ const M = M0; P.push([M, M, h, h]); } return P; }", ('calc',)),
    ('points instead of boxes (the mockup\'s)', "  const Ml = c[0] - c[2], Mh = c[0] + c[2], Rl = c[1] - c[3] - m, Rh = c[1] + c[3] - m;", "  const Ml = c[0], Mh = c[0], Rl = c[1] - m, Rh = c[1] - m;", ('calc',)),
    ('the out-jump rule loosened (no trip back counted)', "need = m + back.reduce((a, b) => a + b, 0) - (pl.goal === 'roll' ? Math.max(...back) : 0);", "need = m;", ('calc',)),
    ('the finisher not kept for the end', "const finOk = pl.obs === 'critical' || pl.finOk,", "const finOk = true,", ('calc',)),
    ('no polarization', "return t && now - t < WH_MASS_POL_MS ? t + WH_MASS_POL_MS : 0;", "return 0;", ('calc',)),
    ('an impossible answer kept', "  if(!P.length && obs !== 'gone'){ P = hmPoss(pl.M0, obs); pl.reset = true; }", "", ('calc',)),
    ('the risk by the smallest left only', "function hmShare(P, m){ return P.length ? hmLe(P, m) / P.length : 0; }", "function hmShare(P, m){ return P.length && P[0][1] <= m ? 1 : 0; }", ('calc',)),
    ('a fit\'s mass without its Higgs Anchor', "mass: {base: baseMass, boosted: boostedMass,", "mass: {base: baseMass / 2, boosted: boostedMass,", ('fit',)),
    ('no ZPME mode', "  if(zp.length){   // the ZPME running", "  if(false){   // the ZPME running", ('fit',)),
    ('a typed hull without its MWD', "  if(WH_MASS_PROP[rs]) modes.push(", "  if(false) modes.push(", ('fit',)),
    ('answers not written to the connection', "  if(pl.obs !== 'gone' && hmLinkLive()) hmLinkMass(pl.obs);", "", ('ui',)),
    ('Undo not putting the Mass back', "  if(b.mass !== null && hmLinkLive() && (H.link.mass || '') !== b.mass) hmLinkMass(b.mass);", "", ('ui',)),
    ('a K162\'s far side with K162 in its list', "(noK162 ? '' : o('K162',", "(false ? '' : o('K162',", ('ui',)),
    ('Start over without its question', "else if(d.hm === 'reset'){ if(H.pl && H.pl.hist.length && !H.pl.done) H.rs = true; else hmReset(); }", "else if(d.hm === 'reset') hmReset();", ('ui',)),
    ('the rows not kept', "function hmSave(){ try{ localStorage.setItem(WH_MASS_KEY,", "function hmSave(){ try{ if(0) localStorage.setItem(WH_MASS_KEY,", ('ui',)),
    ('+ Add\'s Linked to not built after an Add', "  whSelect(id); whAddLinkList(f);   // 070", "  whSelect(id);   // 070", ('link',)),
    ('the phone toolbar not wrapping', ".wh-ctl{left:8px; right:8px; justify-content:flex-end; gap:6px; flex-wrap:wrap;} .wh-ctl > *{flex:none;}", ".wh-ctl{left:8px; right:8px; justify-content:flex-end; gap:6px;}", ('phone',)),
]

if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch()
        out, errs = cases(b, HTML)
        for o in out: check(False, o)
        check(not out, 'the steps (crit, roll, both sides, the risk, the finisher, polarization, words), fits\' and hulls\' masses, the panel, + Add\'s Linked to, a phone')
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
