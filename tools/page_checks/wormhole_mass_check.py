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
  * a safe plan that is slow (Megathron and Heron on a D382 at less than 50%: the Heron's small trips) offers the faster jump beside it with its
    odds and its own estimate, never chosen by itself; pressed, that step is the faster one with "Back to the safe way", and the step after an
    answer is chosen as before; the estimate counts a minute a step plus the 5-minute polarization waits (a Heron alone: 2 steps per 5 minutes);
  * + Add's Linked to: with you on the map, a system selected, both, neither; after an Add the list is built again (from an empty map the
    second system is linked to the first);
  * a phone (390 px): the toolbar's controls 44 x 44 without overlapping each other or the rail, the panel without sideways scroll, the
    answers 44 px tall;
  * 072 (Project doc roadmap/hole-mass-runs-plan.md): the odds split in two (stuck + gone, not crit = 070's number for every step, Roll never
    "gone, not crit", the words name the far side), Crit picks the least stuck, the safe mass (Crit out Rmin / 2, Roll out Rmin, none coming in),
    a Send X instead per finisher (lightest first, one sent frees only it), Carry on never matches a lost ship; + Finisher (its side, Add off
    until its masses, the log, Undo), Change → + Ship asks its side and Undo goes back past Carry on with the rows, 5 ships at most; saved runs
    (replay = live, a reload resumes the same step, two at once, Open, Delete asks, WH-01 when the browser refuses with the box in view, deleting
    another run saves this one, a finished run stays); "mass mass" never in the connection list; a ship lost (alone on the finish side, part way
    through a group step on the far side with its pod coming home, the last of a part step, every ship, the finisher, a replacement on the far
    side); the five buttons inside the panel at 1440 and 390 px; the redraw with 5 ships and 3 finishers is printed (TIME);
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

# ---- 072 (Project doc roadmap/hole-mass-runs-plan.md): the odds split, stuck first, the safe mass, a finisher freed per ship, Carry on's match
SPLIT = """([sets]) => {
  const res = {bad: [], both: 0, colOnly: 0, n: 0}, lightest = (x) => Math.min(...x.modes.map(m => m.m));
  for(const ships of sets) for(const goal of ['crit', 'roll']) for(const code of ['B274', 'D382']) for(const st0 of ['fresh', 'stable', 'reduced']) for(const f of [0.92, 1.0, 1.08]){
    const h = hmHole(code), pl = {H: h, M0: h.M0, goal, fin: 'this', here: 'A', there: 'B', ships: ships.map(s => ({...s, modes: s.modes.filter(m => m.m <= h.J), at: 'this', last: {out: 0, back: 0}})),
      P: hmPoss(h.M0, st0), obs: st0, hist: [], done: '', reset: false, free: [], part: null};
    const M = h.M0 * f; let R = st0 === 'fresh' ? M : st0 === 'stable' ? M * 0.75 : M * 0.3, now = Date.now();
    for(let k = 0; k < 40; k++){
      const s = hmNext(pl, now); if(!s || s.none) break; res.n++;
      if(Math.abs(s.stuck + s.col - s.risk) > 1e-12) res.bad.push(`${goal} ${code}: stuck ${s.stuck} + gone ${s.col} isn't the risk ${s.risk}`);
      if(goal === 'roll' && s.col) res.bad.push(`roll ${code}: a "gone, not crit" part (${s.col})`);
      const g = s.g, m = s.m; let old;   // 070's number, worked out here
      if(s.home){ const back = g.map(x => lightest(pl.ships[x.i])); old = hmShare(pl.P, m + back.reduce((a, b) => a + b, 0) - (goal === 'roll' ? Math.max(...back) : 0)); }
      else { const offs = pl.ships.filter(x => x.at !== pl.fin).length, pre = m - Math.max(...g.map(x => x.mo.m)); old = hmShare(pl.P, g.length === offs && goal === 'roll' ? pre : m); }
      if(Math.abs(old - s.risk) > 1e-12) res.bad.push(`${goal} ${code}: the risk ${s.risk} isn't 070's ${old}`);
      if(goal === 'crit' && s.stuck > 0 && s.col > 0) res.both++;
      if(goal === 'crit' && !s.stuck && s.col > 0){ res.colOnly++; if(!/^no one can be left behind, but /.test(hmRiskWords(pl, s))) res.bad.push('only the collapse can happen, words: ' + hmRiskWords(pl, s)); }
      if(s.stuck > 0 && !hmRiskWords(pl, s).includes('stuck in B')) res.bad.push('the words don\\'t name the far side: ' + hmRiskWords(pl, s));
      if(s.risk >= 0.99) break;
      let closed = false; for(const x of g){ R -= x.mo.m; if(R <= 0){ closed = true; break; } } if(closed) break;
      now = Math.max(now, s.wait) + 60e3; hmApply(pl, s, hmSt(M, R), now); if(pl.done) break;
    }
  }
  return res; }"""
# the pick in Crit: with no safe group, the least stuck one (worked out here from every group). For the main pick that is also the least risk (the
# lightest ship cold alone has both the least total and the least stuck: found at the build), so the case where they differ is the faster offer
# beside a slow safe plan (FASTSTUCK)
STUCK = """([sets]) => {
  const res = {bad: [], n: 0, differ: 0}, lightest = (x) => Math.min(...x.modes.map(m => m.m));
  for(const ships of sets) for(const code of ['D382', 'B274']) for(const f of [0.9, 0.95, 1.0, 1.05, 1.1]){
    const h = hmHole(code), pl = {H: h, M0: h.M0, goal: 'crit', fin: 'this', here: 'A', there: 'B', ships: ships.map(s => ({...s, modes: s.modes.filter(m => m.m <= h.J), at: 'this', last: {out: 0, back: 0}})),
      P: hmPoss(h.M0, 'reduced'), obs: 'reduced', hist: [], done: '', reset: false, free: [], part: null};
    const M = h.M0 * f; let R = M * 0.35, now = Date.now();
    for(let k = 0; k < 30; k++){
      const s = hmNext(pl, now); if(!s || s.none || s.risk >= 0.99) break;
      if(s.home && s.risk > 0){
        const S = pl.ships, C = [], idx = S.map((x, i) => i);
        for(let mask = 1; mask < (1 << S.length); mask++){ const ii = idx.filter(i => mask & (1 << i)); let gs = [[]]; for(const i of ii) gs = gs.flatMap(c => S[i].modes.map(mo => c.concat([{i, mo}])));
          for(const g of gs){ const back = g.map(x => lightest(S[x.i])), m = g.reduce((a, x) => a + x.mo.m, 0), all = m + back.reduce((a, b) => a + b, 0), mb = Math.max(...back); C.push({risk: hmShare(pl.P, all), stuck: hmShare(pl.P, all - mb)}); } }
        if(!C.some(c => c.risk === 0)){ res.n++; const ms = Math.min(...C.map(c => c.stuck)), mr = Math.min(...C.map(c => c.risk)), lr = C.filter(c => c.risk === mr);
          if(s.stuck > ms + 1e-12) res.bad.push(`crit ${code}: the step is ${s.stuck} stuck, ${ms} was possible (risk ${s.risk})`); }
      }
      let closed = false; for(const x of s.g){ R -= x.mo.m; if(R <= 0){ closed = true; break; } } if(closed) break;
      now = Math.max(now, s.wait) + 60e3; hmApply(pl, s, hmSt(M, R), now); if(pl.done) break;
    }
  }
  return res; }"""
# made-up ships on an N766 at less than 50%: the least stuck faster jump (196,800 t: 0.77% stuck, 25% in all), not the least risk (190,000 t: 0.86%
# stuck, 13% in all)
FASTSTUCK = """() => { const mk = (n, h, c, z) => ({name: n, label: n, modes: [{k: 'hot', lab: 'MWD on', m: h}, {k: 'cold', lab: 'prop off', m: c}].concat(z ? [{k: 'zpme', lab: 'ZPME on', m: z}] : [])});
  const h = hmHole('N766'), ships = [mk('Hauler', 90000, 40000, 8000), mk('Megathron', 296800, 196800), mk('Brick', 200000, 100000)];
  const pl = {H: h, M0: h.M0, goal: 'crit', fin: 'this', here: 'A', there: 'B', ships: ships.map(x => ({...x, modes: x.modes.filter(m => m.m <= h.J), at: 'this', last: {out: 0, back: 0}})), P: hmPoss(h.M0, 'reduced'), obs: 'reduced', hist: [], done: '', reset: false, free: [], part: null};
  const st = hmNext(pl, Date.now()); return st && st.fast ? [st.fast.m, st.fast.stuck, st.fast.risk] : null; }"""
# the safe mass: Crit out Rmin / 2, Roll out Rmin (rounded down to 100 t), coming in no sentence; never "No ship is light enough" beside Send X
SAFE = """([mega, phobos, heron]) => {
  const res = [], mk = (code, st, goal, ships) => { const h = hmHole(code); return {H: h, M0: h.M0, goal, fin: 'this', here: 'A', there: 'B', ships: ships.map(s => ({...s, modes: s.modes.filter(m => m.m <= h.J), at: 'this', last: {out: 0, back: 0}})), P: hmPoss(h.M0, st), obs: st, hist: [], done: '', reset: false, free: [], part: null}; };
  for(const goal of ['crit', 'roll']) for(const code of ['D382', 'B274']){
    const pl = mk(code, 'reduced', goal, [mega]), s = hmNext(pl, Date.now()); if(!s || !(s.risk > 0)) continue;
    const want = Math.max(0, Math.floor((goal === 'crit' ? hmLo(pl.P[0]) / 2 : hmLo(pl.P[0])) / 100) * 100);
    res.push({goal, code, safe: s.safe, want, home: s.home, txt: hmSafeTxt(pl, s)});
    const q = mk(code, 'critical', goal, [mega]); q.ships[0].at = 'other'; const c = hmNext(q, Date.now()); if(c && !c.none) res.push({goal, code, in: true, txt: hmSafeTxt(q, c), home: c.home});
  }
  const pf = mk('D382', 'reduced', 'crit', [mega, {...heron, fin: true}]), sf = hmNext(pf, Date.now()), div = document.createElement('div'); div.innerHTML = hmRiskHtml(pf, sf);
  res.push({fin: true, alt: !!sf.finAlt, txt: div.textContent});
  return res; }"""
# a "Send X instead" per finisher, lightest first; one sent frees only it (a log entry replayed by hmRunPl, as the panel does)
FREE = """([mega, phobos, heron]) => {
  const ships = [mega, {...phobos, fin: true}, {...heron, fin: true}].map(s => hmRunShip(s));
  const run = {code: 'D382', st0: 'reduced', goal: 'roll', fin: 'this', here: {id: 1, name: 'A'}, there: {id: 2, name: 'B'}, ships, log: []};
  const p0 = hmRunPl(run), s0 = hmNext(p0, Date.now()), div = document.createElement('div'); div.innerHTML = hmFinAltHtml(p0, s0);
  const btns = [...div.querySelectorAll('[data-hm-f]')].map(b => [Number(b.dataset.hmF), b.textContent]);
  run.log.push({t: 'free', i: btns.length ? btns[0][0] : 2}); const p1 = hmRunPl(run), s1 = hmNext(p1, Date.now());
  return {risk: s0.risk, alt: s0.finAlt || null, btns, after: s1 && s1.g ? s1.g.map(x => x.i) : null, free: p1.free}; }"""
# Carry on matches a kept ship by its label, never a lost one: two Megathrons, the second out; the first lost; carried on with one Megathron
CARRY = """([mega]) => {
  const run = {code: 'B274', st0: 'fresh', goal: 'roll', fin: 'this', here: {id: 1, name: 'A'}, there: {id: 2, name: 'B'}, ships: [hmRunShip(mega), hmRunShip(mega)], log: [
    {t: 's', g: [[1, 'cold']], d: 'out', a: 'stable', at: Date.now() - 60e3}, {t: 'lost', i: 0, at: Date.now()}, {t: 'carry', ships: [hmRunShip(mega)], rows0: []}]};
  const pl = hmRunPl(run); return pl.ships.filter(s => !s.lost).map(s => [s.at, s.last.out > 0]); }"""

def calc072(pg, out):
    sp = pg.evaluate(SPLIT, [[[SHIPS['mega']], [SHIPS['mega'], SHIPS['mega']], [SHIPS['mega'], SHIPS['phobos'], SHIPS['heron']]]])
    if sp['bad']: out.append(f'the odds split: {sp["bad"][0]} ({len(sp["bad"])} in all)')
    if not sp['both']: out.append(f'no Crit step with both a stuck and a "gone, not crit" part in {sp["n"]} steps')
    if not sp['colOnly']: out.append(f'no Crit step where only the collapse can happen in {sp["n"]} steps')
    sk = pg.evaluate(STUCK, [[[SHIPS['mega'], SHIPS['phobos']], [SHIPS['mega'], SHIPS['bs']], [SHIPS['bs'], SHIPS['phobos'], SHIPS['heron']]]])
    if sk['bad']: out.append(f'stuck first: {sk["bad"][0]} ({len(sk["bad"])} in all)')
    if not sk['n']: out.append('stuck first: no risky position to check')
    fs = pg.evaluate(FASTSTUCK)
    if not fs or abs(fs[0] - 196800) > 1 or fs[1] > 0.0078 or fs[2] < 0.24: out.append(f'the faster offer isn\'t the least stuck (Hauler, Megathron, Brick on an N766 at less than 50%): {fs}')
    for r in pg.evaluate(SAFE, [SHIPS['mega'], SHIPS['phobos'], SHIPS['heron']]):
        if r.get('fin'):
            if r['alt'] and 'No ship is light enough' in r['txt']: out.append(f'"No ship is light enough" beside a safe Send X instead: {r["txt"][:200]!r}')
        elif r.get('in'):
            if r['txt']: out.append(f'{r["goal"]} {r["code"]} coming in has a safe-mass sentence: {r["txt"]!r}')
        elif r['safe'] != r['want'] or not r['home']: out.append(f'{r["goal"]} {r["code"]} out: the safe mass is {r["safe"]}, want {r["want"]}')
    fr = pg.evaluate(FREE, [SHIPS['mega'], SHIPS['phobos'], SHIPS['heron']])
    if not fr['alt'] or [b[0] for b in fr['btns']] != [2, 1] or not all('instead: safe' in b[1] for b in fr['btns']): out.append(f'two finishers: a Send X instead each, lightest first: {fr["alt"]} {fr["btns"]}')
    if not fr['after'] or 2 not in fr['after'] or 1 in fr['after']: out.append(f'one finisher sent frees only it: the next step is {fr["after"]} (free {fr["free"]})')
    ca = pg.evaluate(CARRY, [SHIPS['mega']])
    if ca != [['other', True]]: out.append(f'Carry on matched a kept Megathron to the lost one: {ca}')

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
        # a slow safe plan: the faster jump is offered, never chosen; the time counts polarization (a Heron alone, 2 steps per 5 minutes)
        sl = pg.evaluate("""([mega, heron]) => { const h = hmHole('D382'), mk = (ships, st, goal) => ({H: h, M0: h.M0, goal, fin: 'this', here: 'A', there: 'B',
            ships: ships.map(s => ({...s, modes: s.modes.filter(m => m.m <= h.J), at: 'this', last: {out: 0, back: 0}})), P: hmPoss(h.M0, st), obs: st, hist: [], done: '', reset: false, finOk: false});
          const p1 = mk([mega, heron], 'reduced', 'roll'), s1 = hmNext(p1, Date.now()), pv = hmPreview(p1), pf = hmPreview(p1, true);
          const p2 = mk([heron], 'stable', 'crit'), v2 = hmPreview(p2);
          return {risk: s1.risk, who: hmShortTxt(p1, s1), fast: s1.fast ? [s1.fast.risk, hmShortTxt(p1, s1.fast), !!s1.fast.isFast] : null, pv: [pv.cap, pv.thi], pf: [pf.cap, pf.hi, pf.thi, pf.lo],
            heron: [v2.cap, v2.thi, v2.waited], dur: [hmDurTxt(3 * 60e3), hmDurTxt(23 * 60e3), hmDurTxt(200 * 60e3), hmDurTxt(60 * 60e3)]}; }""", [SHIPS['mega'], SHIPS['heron']])
        if sl['risk'] != 0 or 'Heron' not in sl['who']: out.append(f'the slow case\'s step isn\'t the safe Heron trip (risk {sl["risk"]}, {sl["who"]!r}): the faster jump was chosen for you')
        if not sl['fast'] or not (0 < sl['fast'][0] < 0.99) or 'Megathron' not in sl['fast'][1] or not sl['fast'][2]: out.append(f'a slow safe plan offers no faster jump: {sl["fast"]}')
        if not (sl['pv'][0] or sl['pv'][1] >= 30 * 60e3): out.append(f'the Heron\'s safe plan isn\'t slow ({sl["pv"]})')
        if sl['pf'][0] or sl['pf'][1] > 20 or sl['pf'][2] >= 30 * 60e3: out.append(f'taking the faster jumps isn\'t faster ({sl["pf"]})')
        if sl['pf'][3] < 2: out.append(f'a run that strands someone is counted as steps (from {sl["pf"][3]} step)')
        if not (sl['heron'][0] and sl['heron'][2] and 195 * 60e3 <= sl['heron'][1] <= 205 * 60e3): out.append(f'a Heron alone: 80 steps aren\'t about 3 h 20 min with polarization ({sl["heron"]})')
        if sl['dur'] != ['3 min', '25 min', '3 h 20 min', '1 h']: out.append(f'durations: {sl["dur"]}')
        calc072(pg, out)

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
    g = pg.evaluate("""() => { const sb = document.querySelector('.hm-pop .hm-sum .hm-sb'), bs = [...sb.querySelectorAll('button')].map(b => b.getBoundingClientRect());
      return {cols: getComputedStyle(sb).gridTemplateColumns.split(' ').length, n: bs.length, rows: new Set(bs.map(r => Math.round(r.top))).size, h: Math.min(...bs.map(r => r.height))}; }""")
    if g != {'cols': 3, 'n': 5, 'rows': 2, 'h': g['h']} or g['h'] < 43.5: out.append(f'a phone: the pinned line\'s five buttons aren\'t 3 columns, two rows, 44 px: {g}')
    if inside(pg): out.append('a phone: a pinned-line button runs past the panel')
    ctx.close()

def fast_cases(b, html, out, errs, parts):
    if parts is not None and 'fast' not in parts: return
    ctx, pg = start(b, html, 1440, errs)
    ids = pg.evaluate(SEED); pg.evaluate("whPaint(true)"); pg.click('[data-wh-pop="mass"]'); pg.wait_for_timeout(200)
    k = pg.evaluate("([a, d]) => whLinkKey(a, d)", [ids['a'], ids['d']]); pg.select_option('.hm-pop [data-hm="link"]', k); pg.wait_for_timeout(100)
    for i, fid in enumerate(('mf1', 'mf3')):
        pg.click('.hm-pop [data-hm="add"]'); pg.select_option(f'.hm-pop [data-hm-ship="{i}"]', f'fit:{fid}'); pg.wait_for_timeout(100)
    wait_masses(pg, 2); pg.click('.hm-pop [data-hm="go"]'); pg.wait_for_timeout(400)
    t = pop_text(pg) or ''; now = pg.locator('.hm-pop .hm-now').text_content() or ''
    if not re.search(r'Steps · about 80\+ steps, over \d+ h( \d+ min)? with polarization', t): out.append(f'the slow plan\'s heading: {t[:160]!r}')
    if 'Heron' not in now or 'Megathron' in now: out.append(f'the first step isn\'t the safe Heron trip: {now[:120]!r}')
    fb = pg.locator('.hm-pop [data-hm="fast"]')
    if 'Safe but slow:' not in t or not fb.count(): out.append(f'a slow safe plan doesn\'t offer the faster jump: {t[:300]!r}'); ctx.close(); return
    ft = fb.text_content() or ''
    if not re.search(r'Send Megathron out (cold|hot) instead \(about 1 in \d+ stuck\); about [\d–]+ steps, [\d–]+ min( with polarization)? taking the faster jumps', ft): out.append(f'the faster jump\'s button: {ft!r}')
    fb.click(); pg.wait_for_timeout(300)
    t = pop_text(pg) or ''; now = pg.locator('.hm-pop .hm-now').text_content() or ''
    if 'Megathron' not in now or 'Faster, not safe:' not in t or not pg.locator('.hm-pop [data-hm="safe"]').count(): out.append(f'the faster jump picked doesn\'t show it with its odds: {now[:100]!r}')
    if 'over' in (pg.locator('.hm-pop .wh-sub').first.text_content() or ''): out.append('the heading keeps the safe plan\'s time after the faster jump was picked')
    bt = pg.locator('.hm-pop [data-hm="safe"]').text_content() or ''
    if not re.search(r'Back to the safe way: Heron out (hot|cold), about 80\+ steps, over', bt): out.append(f'Back to the safe way: {bt!r}')
    pg.click('.hm-pop [data-hm="safe"]'); pg.wait_for_timeout(300)
    now = pg.locator('.hm-pop .hm-now').text_content() or ''
    if 'Heron' not in now or 'Megathron' in now: out.append(f'Back to the safe way doesn\'t bring the Heron trip back: {now[:100]!r}')
    pg.click('.hm-pop [data-hm="fast"]'); pg.wait_for_timeout(300)
    pg.click('.hm-pop [data-hm-say="reduced"]'); pg.wait_for_timeout(300)
    h = pg.evaluate("() => { const H = hmState(); return [H.pl.hist.length, H.pl.hist[0] && H.pl.hist[0].short, H.step && H.step.isFast || false]; }")
    if h[0] != 1 or 'Megathron' not in (h[1] or '') or h[2]: out.append(f'after answering the faster jump: {h}')
    pg.click('.hm-pop [data-hm="undo"]'); pg.wait_for_timeout(300)
    now = pg.locator('.hm-pop .hm-now').text_content() or ''
    if 'Heron' not in now or pg.evaluate("() => hmState().fast"): out.append(f'Undo doesn\'t go back to the safe step: {now[:100]!r}')
    ctx.close()

CLICK = "(s) => { const e = document.querySelector(s); if(!e) return 'missing'; if(e.disabled) return 'disabled'; e.click(); return 'ok'; }"
ANSWER = """(avoid) => { const H = hmState(); if(!H.step || H.step.none) return null; const k = hmPossibleSays(H.pl, H.step).find(k => !avoid.includes(k)); if(!k) return null;
  document.querySelector(`.hm-pop [data-hm-say="${k}"]`).click(); return k; }"""
# replay = live: the run as the panel holds it against the run rebuilt from its saved log
SIG = """() => { const H = hmState(), a = H.pl, b = hmRunPl(H.run), sg = (p) => JSON.stringify([p.P.length, p.P[0], p.P[p.P.length - 1], p.obs, p.done, p.hist.map(x => x.short + x.obs),
  p.ships.map(s => [s.name, s.at, s.last, !!s.lost, !!s.pod, !!s.podHome]), p.free, p.part]); return [sg(a) === sg(b), sg(a).slice(0, 160), sg(b).slice(0, 160)]; }"""
STATE = "() => { const H = hmState(); return {log: H.run ? H.run.log.map(e => e.t) : null, ships: H.pl ? H.pl.ships.map(s => [s.name, s.at, !!s.lost, !!s.pod]) : null, rows: H.ships.map(r => r.fit || r.hull), step: H.step && H.step.g ? H.step.g.map(x => x.i) : null, part: !!(H.step && H.step.part), runs: hmRunsRead().length}; }"
def clk(pg, s, t=250):
    r = pg.evaluate(CLICK, s); pg.wait_for_timeout(t); return r
def answer(pg, avoid=('gone',)):
    k = pg.evaluate(ANSWER, list(avoid)); pg.wait_for_timeout(300); return k
def setup_run(pg, ids, link, goal, rows, fins=()):
    pg.select_option('.hm-pop [data-hm="link"]', pg.evaluate("([a, o]) => whLinkKey(a, o)", [ids['a'], ids[link]])); pg.wait_for_timeout(100)
    pg.select_option('.hm-pop [data-hm="goal"]', goal); pg.wait_for_timeout(100)
    for i, r in enumerate(rows):
        pg.click('.hm-pop [data-hm="add"]')
        if r.startswith('mf'): pg.select_option(f'.hm-pop [data-hm-ship="{i}"]', f'fit:{r}')
        else: f = pg.locator(f'.hm-pop [data-hm-hull="{i}"]'); f.fill(r); f.dispatch_event('change')
        pg.wait_for_timeout(100)
    for i in fins: pg.check(f'.hm-pop [data-hm-fin="{i}"]'); pg.wait_for_timeout(80)
    wait_masses(pg, len(rows)); return clk(pg, '.hm-pop [data-hm="go"]', 400)
def inside(pg):
    return pg.evaluate("""() => { const p = document.querySelector('.hm-pop').getBoundingClientRect(); return [...document.querySelectorAll('.hm-pop .hm-sum .hm-sb button')].map(b => b.getBoundingClientRect())
      .filter(r => r.left < p.left - 0.5 || r.right > p.right + 0.5).length; }""")

def runs_cases(b, html, out, errs, parts):
    if parts is not None and 'runs' not in parts: return
    ctx, pg = start(b, html, 1440, errs)
    ids = pg.evaluate(SEED); pg.evaluate("whPaint(true)"); pg.click('[data-wh-pop="mass"]'); pg.wait_for_timeout(200)
    opts = pg.evaluate("() => [...document.querySelectorAll('.hm-pop [data-hm=\"link\"] option')].map(o => o.textContent)")
    if any('mass mass' in o or 'mass crit' in o for o in opts) or not any('· mass <50%' in o for o in opts): out.append(f'the connection list\'s mass words: {opts}')
    if setup_run(pg, ids, 'd', 'crit', ['mf1', 'mf3'], fins=(1,)) != 'ok': out.append('Show the steps is off'); ctx.close(); return
    if inside(pg): out.append('1440: a pinned-line button runs past the panel')
    for _ in range(2): answer(pg)
    s0 = pg.evaluate(STATE)
    # + Finisher: its row, the finish side picked, Add off until its masses are known; added on the far side; Undo takes it back
    clk(pg, '.hm-pop [data-hm="af"]')
    row = pg.evaluate("() => { const r = document.querySelector('.hm-pop [aria-label=\"Add a finisher\"]'), at = document.querySelector('.hm-pop [data-hm-af=\"at\"]'), add = document.querySelector('.hm-pop [data-hm=\"afadd\"]'); return r ? [at && at.value, add && add.disabled, document.querySelector('.hm-pop [data-hm=\"af\"]').getAttribute('aria-expanded')] : null; }")
    if row != ['this', True, 'true']: out.append(f'+ Finisher\'s row (its side, Add off, expanded): {row}')
    f = pg.locator('.hm-pop [data-hm-af="hull"]'); f.fill('Buzzard'); f.dispatch_event('change')
    try: pg.wait_for_function("() => { const b = document.querySelector('.hm-pop [data-hm=\"afadd\"]'); return b && !b.disabled; }", timeout=60000)
    except Exception: out.append('+ Finisher\'s Add stays off once the Buzzard\'s masses are known')
    pg.select_option('.hm-pop [data-hm-af="at"]', 'other'); pg.wait_for_timeout(150); clk(pg, '.hm-pop [data-hm="afadd"]', 400)
    s1 = pg.evaluate(STATE)
    if s1['log'][-1:] != ['add'] or len(s1['ships']) != 3 or s1['ships'][2][:2] != ['Buzzard', 'other'] or s1['rows'][-1] != 'Buzzard': out.append(f'+ Finisher on the far side: {s1}')
    if not pg.evaluate("() => { const k = JSON.parse(localStorage.getItem('tvWhMass')); return k.ships.length === 3 && k.ships[2].fin && k.ships.every(r => Object.keys(r).every(x => ['fit', 'hull', 'fin'].includes(x))); }"): out.append('tvWhMass doesn\'t keep the finisher row in its form')
    clk(pg, '.hm-pop [data-hm="undo"]', 400); s2 = pg.evaluate(STATE)
    if s2['log'] != s0['log'] or len(s2['ships']) != 2 or s2['rows'] != s0['rows']: out.append(f'Undo doesn\'t take the finisher back: {s2}')
    clk(pg, '.hm-pop [data-hm="af"]'); f = pg.locator('.hm-pop [data-hm-af="hull"]'); f.fill('Buzzard'); f.dispatch_event('change')
    pg.wait_for_function("() => { const b = document.querySelector('.hm-pop [data-hm=\"afadd\"]'); return b && !b.disabled; }", timeout=60000); clk(pg, '.hm-pop [data-hm="afadd"]', 400)
    # Change → + Ship (its side asked) → Carry on; Undo goes back past it, the setup's rows as they were
    clk(pg, '.hm-pop [data-hm="edit"]'); clk(pg, '.hm-pop [data-hm="add"]')
    at = pg.evaluate("() => { const s = document.querySelector('.hm-pop [data-hm-at=\"3\"]'); return s ? s.value : null; }")
    if at != 'this': out.append(f'a ship new to a run carried on doesn\'t ask its side (the finish side picked): {at}')
    f = pg.locator('.hm-pop [data-hm-hull="3"]'); f.fill('Thorax'); f.dispatch_event('change'); wait_masses(pg, 4)
    clk(pg, '.hm-pop [data-hm="goon"]', 400); s3 = pg.evaluate(STATE)
    if s3['log'][-1:] != ['carry'] or len(s3['ships']) != 4 or s3['ships'][3][:2] != ['Thorax', 'this'] or len(s3['rows']) != 4: out.append(f'Carry on with a new ship: {s3}')
    sg = pg.evaluate(SIG)
    if not sg[0]: out.append(f'replay isn\'t live after Carry on: {sg[1]} / {sg[2]}')
    clk(pg, '.hm-pop [data-hm="undo"]', 400); s4 = pg.evaluate(STATE)
    if s4['log'][-1:] != ['add'] or len(s4['ships']) != 3 or s4['rows'] != ['mf1', 'mf3', 'Buzzard']: out.append(f'Undo past Carry on (the rows back): {s4}')
    # five ships at most: + Finisher off with its title
    clk(pg, '.hm-pop [data-hm="edit"]'); clk(pg, '.hm-pop [data-hm="add"]'); clk(pg, '.hm-pop [data-hm="add"]')
    for i in (3, 4): f = pg.locator(f'.hm-pop [data-hm-hull="{i}"]'); f.fill('Heron'); f.dispatch_event('change')
    wait_masses(pg, 5)
    if pg.locator('.hm-pop [data-hm="add"]').count(): out.append('+ Ship still shows with 5 ships')
    clk(pg, '.hm-pop [data-hm="goon"]', 400)
    fb = pg.evaluate("() => { const b = document.querySelector('.hm-pop [data-hm=\"af\"]'); return b ? [b.disabled, b.title] : null; }")
    if fb != [True, '5 ships at most']: out.append(f'+ Finisher at 5 ships: {fb}')
    if inside(pg): out.append('1440: a pinned-line button runs past the panel with five ships')
    clk(pg, '.hm-pop [data-hm="undo"]', 400); clk(pg, '.hm-pop [data-hm="undo"]', 400)
    sg = pg.evaluate(SIG)
    if not sg[0]: out.append(f'replay isn\'t live after the Undos: {sg[1]} / {sg[2]}')
    answer(pg); before = pg.evaluate("() => [hmState().run.id, document.querySelector('.hm-pop .hm-now').textContent, hmState().run.log.length]")
    # the page reloaded: the run comes back at the same step, Undo working
    pg.reload(); pg.wait_for_timeout(300); pg.evaluate("switchTab('wh')"); pg.wait_for_timeout(200)
    pg.evaluate("(a) => whSelect(a)", ids['a']); pg.click('[data-wh-pop="mass"]'); pg.wait_for_timeout(400)   # the system picked (no system is in focus after a reload)
    after = pg.evaluate("() => { const H = hmState(), n = document.querySelector('.hm-pop .hm-now'), u = document.querySelector('.hm-pop [data-hm=\"undo\"]'); return [H.run && H.run.id, n && n.textContent, H.run && H.run.log.length, !!(u && !u.disabled)]; }")
    if after[:3] != before or not after[3]: out.append(f'a reload doesn\'t resume the run at the same step: {after[:3]} (was {before}), Undo {after[3]}')
    # a second run on another connection: both kept; Open, Delete asks, Keep it keeps
    first = after[0]
    clk(pg, '.hm-pop [data-hm="edit"]'); pg.select_option('.hm-pop [data-hm="link"]', pg.evaluate("([a, o]) => whLinkKey(a, o)", [ids['a'], ids['rens']])); pg.wait_for_timeout(150)
    clk(pg, '.hm-pop [data-hm="go"]', 400); answer(pg)
    r2 = pg.evaluate("() => [hmRunsRead().map(r => r.id), hmState().run.id, document.querySelector('.hm-pop [data-hm=\"runs\"]') && document.querySelector('.hm-pop [data-hm=\"runs\"]').textContent]")
    if len(r2[0]) != 2 or first not in r2[0] or 'Saved runs (2)' not in (r2[2] or ''): out.append(f'two saved runs at once: {r2}')
    second = r2[1]
    clk(pg, '.hm-pop [data-hm="runs"]'); clk(pg, f'.hm-pop [data-hm-open="{first}"]', 400)
    if pg.evaluate("() => hmState().run.id") != first: out.append('Open doesn\'t open the saved run')
    clk(pg, '.hm-pop [data-hm="runs"]'); clk(pg, f'.hm-pop [data-hm-del="{second}"]')
    t = pop_text(pg) or ''
    if 'Delete the saved run B274' not in t: out.append(f'Delete doesn\'t ask: {t[:200]!r}')
    clk(pg, '.hm-pop [data-wh-ask="hm-del-no"]')
    if pg.evaluate("() => hmRunsRead().length") != 2: out.append('Keep it doesn\'t keep the run')
    # WH-01: a refused save shows the red warning inside the pinned line, in view with the steps scrolled to the end; deleting the other run saves this one
    pg.evaluate("""() => { const lim = localStorage.getItem('tvWhMassRuns').length; window.__set = Storage.prototype.setItem;
      Storage.prototype.setItem = function(k, v){ if(k === 'tvWhMassRuns' && String(v).length > lim) throw new DOMException('full', 'QuotaExceededError'); return window.__set.call(this, k, v); }; }""")
    answer(pg)
    w = pg.evaluate("""() => { const p = document.querySelector('.hm-pop'), e = p.querySelector('.hm-sum .sa-warn[role="alert"]'); if(!e) return null; p.scrollTop = p.scrollHeight;
      const r = e.getBoundingClientRect(), q = p.getBoundingClientRect(), cs = getComputedStyle(e);
      return {txt: e.textContent, badge: !!e.querySelector('.ewar-badge.danger'), title: e.querySelector('.ctx').title, border: cs.borderTopColor, seen: r.top >= q.top - 1 && r.bottom <= q.bottom + 1}; }""")
    danger = pg.evaluate("() => getComputedStyle(document.documentElement).getPropertyValue('--danger').trim()")
    if not w: out.append('a refused save shows no WH-01 warning in the pinned line')
    else:
        if 'This run isn’t saved' not in w['txt'] or 'WH-01' not in w['txt'] or not w['badge'] or 'storage is full' not in w['title']: out.append(f'the WH-01 warning: {w}')
        if not w['seen']: out.append('the WH-01 warning isn\'t in view with the steps scrolled to the end')
        if w['border'] in ('rgba(0, 0, 0, 0)', '') or not danger: out.append(f'the WH-01 warning has no danger border ({w["border"]})')
    clk(pg, '.hm-pop [data-hm="runs"]'); clk(pg, f'.hm-pop [data-hm-del="{second}"]'); clk(pg, '.hm-pop [data-wh-ask="hm-del"]', 400)
    gone = pg.evaluate("() => [!document.querySelector('.hm-pop .sa-warn'), hmRunsRead().map(r => [r.id, r.log.length]), hmState().run.log.length]")
    if not gone[0] or len(gone[1]) != 1 or gone[1][0][1] != gone[2]: out.append(f'deleting the other run doesn\'t save the open one: {gone}')
    pg.evaluate("() => { Storage.prototype.setItem = window.__set; }")
    # a finished run stays, with Delete this run
    if not pg.locator('.hm-pop [data-hm-say="gone"]').count(): clk(pg, '.hm-pop [data-hm="undo"]', 400)   # "no safe step left" has no answers
    pg.evaluate("() => document.querySelector('.hm-pop [data-hm-say=\"gone\"]').click()"); pg.wait_for_timeout(300)
    fin = pg.evaluate("() => [hmRunsRead().map(r => r.done), !!document.querySelector('.hm-pop [data-hm=\"delcur\"]')]")
    if not fin[0] or not fin[0][0] or not fin[1]: out.append(f'a finished run isn\'t kept with Delete this run: {fin}')
    ctx.close()

def timing_case(b, html, out, errs, parts):
    if parts is not None and 'runs' not in parts: return
    ctx, pg = start(b, html, 1440, errs)
    ids = pg.evaluate(SEED); pg.evaluate("whPaint(true)"); pg.click('[data-wh-pop="mass"]'); pg.wait_for_timeout(200)
    setup_run(pg, ids, 'd', 'crit', ['mf1', 'mf2', 'mf3', 'Buzzard', 'Megathron'], fins=(1, 2, 3))
    t = pg.evaluate("() => { const H = hmState(); const t0 = performance.now(); for(let k = 0; k < 3; k++) hmPaint(); return [(performance.now() - t0) / 3, H.pl.ships.filter(s => s.fin).length, H.pl.ships.length]; }")
    print(f'TIME the Mass panel\'s redraw with {t[2]} ships, {t[1]} finishers: {t[0]:.0f} ms (headless Chromium)')
    if t[2] != 5 or t[1] != 3: out.append(f'the timing run isn\'t 5 ships and 3 finishers: {t}')
    ctx.close()

def lost_cases(b, html, out, errs, parts):
    if parts is not None and 'lost' not in parts: return
    ctx, pg = start(b, html, 1440, errs)
    ids = pg.evaluate(SEED); pg.evaluate("whPaint(true)"); pg.click('[data-wh-pop="mass"]'); pg.wait_for_timeout(200)
    # L1: lost alone in its step on the finish side (the Phobos is the finisher, so the Megathron goes alone)
    setup_run(pg, ids, 'rens', 'roll', ['mf1', 'mf2'], fins=(1,))
    st = pg.evaluate(STATE); i = st['step'][0] if st['step'] and len(st['step']) == 1 else None
    if i is None: out.append(f'L1: step 1 isn\'t one ship: {st}'); ctx.close(); return
    clk(pg, '.hm-pop [data-hm="lf"]')
    row = pg.evaluate("() => { const s = document.querySelector('.hm-pop [data-hm-lf=\"i\"]'), g = document.querySelector('.hm-pop [data-hm=\"lfgo\"]'); return s ? [[...s.options].map(o => o.textContent), g.disabled] : null; }")
    if not row or not row[1] or len(row[0]) != 3 or not any('in this step' in o for o in row[0]) or not all(' · in ' in o for o in row[0][1:]): out.append(f'L1: the Ship lost row: {row}')
    pg.select_option('.hm-pop [data-hm-lf="i"]', str(i)); pg.wait_for_timeout(150)
    q = pg.evaluate("() => [!!document.querySelector('.hm-pop [data-hm-lf=\"others\"]'), !!document.querySelector('.hm-pop [data-hm-lf=\"pod\"]'), document.querySelector('.hm-pop [aria-label=\"A ship was lost\"]').textContent.includes('answer the step first'), document.querySelector('.hm-pop [data-hm=\"lfgo\"]').disabled]")
    if q != [False, False, True, False]: out.append(f'L1: lost alone on the finish side asks more ({q})')
    clk(pg, '.hm-pop [data-hm="lfgo"]', 400); s1 = pg.evaluate(STATE)
    if s1['log'][-1:] != ['lost'] or not s1['ships'][i][2] or (s1['step'] and i in s1['step']) or 'mf1' in s1['rows'] or '(lost)' not in (pg.locator('.hm-pop .hm-sum').text_content() or ''):
        out.append(f'L1: marked lost: {s1}')
    clk(pg, '.hm-pop [data-hm="undo"]', 400); s2 = pg.evaluate(STATE)
    if s2['ships'][i][2] or 'mf1' not in s2['rows'] or s2['log']: out.append(f'L1: Undo doesn\'t put the ship back: {s2}')
    # L2: two Megathrons out, coming back as one step; one lost before it jumped, on the far side: the other's part waits, then its pod comes home
    clk(pg, '.hm-pop [data-hm="edit"]'); pg.evaluate("() => { const H = hmState(); H.ships = []; hmSave(); H.prev = null; hmPaint(); }"); pg.wait_for_timeout(150)
    setup_run(pg, ids, 'rens', 'roll', ['mf1', 'mf1'])
    for _ in range(4):
        st = pg.evaluate("() => { const H = hmState(); return H.step && H.step.g ? [H.step.g.length, H.step.dir, H.pl.ships.map(s => s.at)] : null; }")
        if st and st[0] == 2 and all(a == 'other' for a in st[2]): break
        answer(pg)
    if not st or st[0] != 2 or not all(a == 'other' for a in st[2]): out.append(f'L2: no step with both Megathrons coming in: {st}'); ctx.close(); return
    clk(pg, '.hm-pop [data-hm="lf"]'); pg.select_option('.hm-pop [data-hm-lf="i"]', '1'); pg.wait_for_timeout(150)
    q = pg.evaluate("() => [document.querySelector('.hm-pop [data-hm-lf=\"others\"]') && document.querySelector('.hm-pop [data-hm-lf=\"others\"]').value, document.querySelector('.hm-pop [data-hm-lf=\"pod\"]') && document.querySelector('.hm-pop [data-hm-lf=\"pod\"]').value]")
    if q != ['keep', 'home']: out.append(f'L2: lost in a group step on the far side: {q}')
    try: pg.wait_for_function("() => /The pod \\(\\d[\\d,]* t\\) gets a step of its own, home\\./.test(document.querySelector('.hm-pop [aria-label=\"A ship was lost\"]').textContent)", timeout=60000)
    except Exception: out.append('L2: the pod\'s mass never shows')
    clk(pg, '.hm-pop [data-hm="lfgo"]', 400)
    p = pg.evaluate("() => { const H = hmState(); return [!!H.step.part, H.step.g.map(x => x.i), document.querySelector('.hm-pop').textContent.includes('Part of this step:'), H.pl.ships.map(s => [s.name, s.at, !!s.lost, !!s.pod])]; }")
    if not p[0] or p[1] != [0] or not p[2] or len(p[3]) != 3 or not p[3][2][3]: out.append(f'L2: the part step held for its answer, the pod added: {p}')
    answer(pg)
    p = pg.evaluate("() => { const H = hmState(); return [H.step && H.step.g ? H.step.g.map(x => H.pl.ships[x.i].name) : null, !!(H.step && H.step.part)]; }")
    if not p[0] or len(p[0]) != 1 or 'pod' not in p[0][0] or p[1]: out.append(f'L2: after the part step, the pod\'s step home: {p}')
    answer(pg)
    p = pg.evaluate("() => { const H = hmState(); return [H.pl.ships[2].podHome, document.querySelector('.hm-pop .hm-sum').textContent, H.step && H.step.g ? H.step.g.map(x => x.i) : null]; }")
    if not p[0] or '’s pod (home)' not in p[1] or (p[2] and 2 in p[2]): out.append(f'L2: the pod home leaves the run: {p}')
    sg = pg.evaluate(SIG)
    if not sg[0]: out.append(f'L2: replay isn\'t live: {sg[1]} / {sg[2]}')
    clk(pg, '.hm-pop [data-hm="undo"]', 400); clk(pg, '.hm-pop [data-hm="undo"]', 400)
    if not pg.evaluate("() => !!hmState().step.part"): out.append('L2: Undo doesn\'t go back to the part step')
    # L3: the last ship of a part step lost: the step wasn't made; L5: every ship lost
    clk(pg, '.hm-pop [data-hm="lf"]'); pg.select_option('.hm-pop [data-hm-lf="i"]', '0'); pg.wait_for_timeout(150); pg.select_option('.hm-pop [data-hm-lf="pod"]', 'no'); pg.wait_for_timeout(150); clk(pg, '.hm-pop [data-hm="lfgo"]', 400)
    p = pg.evaluate("() => { const H = hmState(); return [!!(H.step && H.step.part), H.step && H.step.g ? H.step.g.map(x => H.pl.ships[x.i].name) : null]; }")
    if p[0] or not p[1] or not all('pod' in n for n in p[1]): out.append(f'L3: the last ship of a part step lost: {p}')
    clk(pg, '.hm-pop [data-hm="lf"]'); pg.select_option('.hm-pop [data-hm-lf="i"]', '2'); pg.wait_for_timeout(150); clk(pg, '.hm-pop [data-hm="lfgo"]', 400)
    p = pg.evaluate("() => [document.querySelector('.hm-pop .hm-now') && document.querySelector('.hm-pop .hm-now').textContent, document.querySelector('.hm-pop [data-hm=\"lf\"]').disabled]")
    if not p[0] or 'No ships left: add one with + Finisher, or with Change.' not in p[0] or not p[1]: out.append(f'L5: every ship lost: {p}')
    # L4: the finisher lost: no Send X instead, "add one with + Finisher"; L6: a replacement on Carry on, on the far side, not matched to the lost one
    clk(pg, '.hm-pop [data-hm="edit"]'); pg.evaluate("() => { const H = hmState(); H.ships = []; hmSave(); H.prev = null; hmPaint(); }"); pg.wait_for_timeout(150)
    setup_run(pg, ids, 'd', 'crit', ['mf1', 'mf3'], fins=(1,))
    if not pg.locator('.hm-pop [data-hm="finnow"]').count(): out.append('L4: no Send Heron instead to begin with')
    clk(pg, '.hm-pop [data-hm="lf"]'); pg.select_option('.hm-pop [data-hm-lf="i"]', '1'); pg.wait_for_timeout(150); clk(pg, '.hm-pop [data-hm="lfgo"]', 400)
    t = pop_text(pg) or ''
    if pg.locator('.hm-pop [data-hm="finnow"]').count() or 'add one with + Finisher' not in t: out.append(f'L4: the finisher lost: {t[t.find("No fully"):][:240]!r}')
    answer(pg)
    clk(pg, '.hm-pop [data-hm="edit"]'); clk(pg, '.hm-pop [data-hm="add"]')
    n = pg.evaluate("() => hmState().ships.length - 1")
    pg.select_option(f'.hm-pop [data-hm-ship="{n}"]', 'fit:mf3'); pg.wait_for_timeout(150); pg.select_option(f'.hm-pop [data-hm-at="{n}"]', 'other'); pg.wait_for_timeout(150)
    wait_masses(pg, n + 1); clk(pg, '.hm-pop [data-hm="goon"]', 400)
    p = pg.evaluate("() => hmState().pl.ships.filter(s => !s.lost).map(s => [s.name, s.at, s.last.out + s.last.back])")
    if ['Heron', 'other', 0] not in p: out.append(f'L6: the replacement Heron isn\'t on the far side as a new ship: {p}')
    ctx.close()

def cases(b, html, parts=None):
    out, errs = [], []
    ui_cases(b, html, out, errs, parts)
    fast_cases(b, html, out, errs, parts)
    if parts is not None and 'calc' in parts and not ({'fit', 'ui'} & set(parts)):
        ctx, pg = start(b, html, 1440, errs, fits=False); calc_cases(pg, out, parts); ctx.close()
    link_cases(b, html, out, errs, parts)
    phone_cases(b, html, out, errs, parts)
    runs_cases(b, html, out, errs, parts)
    lost_cases(b, html, out, errs, parts)
    timing_case(b, html, out, errs, parts)
    return out, errs

MUTANTS = [
    ('no ±10% (the exact total)', "for(let i = 0; i < n; i++){ const M = M0 * 0.9 + (2 * i + 1) * h; P.push([M, M, h, h]); } return P; }",
     "for(let i = 0; i < n; i++){ const M = M0; P.push([M, M, h, h]); } return P; }", ('calc',)),
    ('points instead of boxes (the mockup\'s)', "  const Ml = c[0] - c[2], Mh = c[0] + c[2], Rl = c[1] - c[3] - m, Rh = c[1] + c[3] - m;", "  const Ml = c[0], Mh = c[0], Rl = c[1] - m, Rh = c[1] - m;", ('calc',)),
    ('the out-jump rule loosened (no trip back counted)', "mb = Math.max(...back), need = crit ? all : all - mb;", "mb = Math.max(...back), need = m;", ('calc',)),
    ('the finisher not kept for the end', "pool = pl.obs === 'critical' || !nf.length ? C : nf;", "pool = C;", ('calc',)),
    ('no polarization', "return t && now - t < WH_MASS_POL_MS ? t + WH_MASS_POL_MS : 0;", "return 0;", ('calc',)),
    ('an impossible answer kept', "  if(!P.length && obs !== 'gone'){ P = hmPoss(pl.M0, obs); pl.reset = true; }", "", ('calc',)),
    ('the risk by the smallest left only', "function hmShare(P, m){ return P.length ? hmLe(P, m) / P.length : 0; }", "function hmShare(P, m){ return P.length && P[0][1] <= m ? 1 : 0; }", ('calc',)),
    ('a fit\'s mass without its Higgs Anchor', "mass: {base: baseMass, boosted: boostedMass,", "mass: {base: baseMass / 2, boosted: boostedMass,", ('fit',)),
    ('no ZPME mode', "  if(zp.length){   // the ZPME running", "  if(false){   // the ZPME running", ('fit',)),
    ('a typed hull without its MWD', "  if(WH_MASS_PROP[rs]) modes.push(", "  if(false) modes.push(", ('fit',)),
    ('answers not written to the connection', "  if(pl.obs !== 'gone' && hmLinkLive()) hmLinkMass(pl.obs);", "", ('ui',)),
    ('Undo not putting the Mass back', "if((H.link.mass || '') !== v) hmLinkMass(v); }", "}", ('ui',)),
    ('a K162\'s far side with K162 in its list', "(noK162 ? '' : o('K162',", "(false ? '' : o('K162',", ('ui',)),
    ('Start over without its question', "else if(d.hm === 'reset'){ if(H.pl && H.pl.hist.length && !H.pl.done) H.rs = true; else hmReset(); }", "else if(d.hm === 'reset') hmReset();", ('ui',)),
    ('the rows not kept', "function hmSave(){ try{ localStorage.setItem(WH_MASS_KEY,", "function hmSave(){ try{ if(0) localStorage.setItem(WH_MASS_KEY,", ('ui',)),
    ('the faster jump chosen for you', "if(f){ st.fast = out(f, away, safeOut, true); st.fast.isFast = true; st.fast.slow = {...st}; }", "if(f) return out(f, away, safeOut, true);", ('calc',)),
    ('the time without polarization', "const at = Math.max(now, st.wait);", "const at = now;", ('calc',)),
    ('no faster offer when the safe way is slow', "if(!st.fast || !pv || !(pv.cap || pv.thi >= WH_MASS_SLOW_MS)) return '';", "if(true) return '';", ('fast',)),
    ('the faster estimate takes it once only', "if(fast && st.fast) st = st.fast;", "if(fast && !k && st.fast) st = st.fast;", ('calc',)),
    ('a stranded run counted as steps', "const ok = runs.filter(r => !r.lost),", "const ok = runs,", ('calc',)),
    ('Back to the safe way doing nothing', "else if(d.hm === 'safe'){ if(H.pl && H.fast){ H.fast = false;", "else if(d.hm === 'safe'){ if(false){ H.fast = false;", ('fast',)),
    ('+ Add\'s Linked to not built after an Add', "  whSelect(id); whAddLinkList(f);   // 070", "  whSelect(id);   // 070", ('link',)),
    # 072
    ('one share for both (no split)', "stuck: crit ? hmShare(P, all - mb) : hmShare(P, need)", "stuck: hmShare(P, need)", ('calc',)),
    ('the faster offer by the total, not stuck first', "c.m >= 2 * st.m).sort((a, b) => a.stuck - b.stuck || a.risk - b.risk ||", "c.m >= 2 * st.m).sort((a, b) => a.risk - b.risk ||", ('calc',)),
    ('the safe mass by 070\'s formula', "const safeOut = crit ? Rmin / 2 : Rmin;", "const safeOut = Rmin - ((fr || best).need - (fr || best).m);", ('calc',)),
    ('one Send X instead frees every finisher', "pl.free = pl.free.concat([e.i]);", "pl.free = pl.ships.map((s, k) => k);", ('calc',)),
    ('Carry on matching a lost ship', "!used.has(j) && !o.lost && !o.pod && o.label === s.label", "!used.has(j) && o.label === s.label", ('calc',)),
    ('an added finisher always on this side', "pl.ships.push({...fit(e.ship), at: e.at, last: {out: 0, back: 0}});", "pl.ships.push({...fit(e.ship), at: 'this', last: {out: 0, back: 0}});", ('runs',)),
    ('no save after an answer', "Remove the connection to ${whName(l.a === n ? l.b : l.a)}?`; }\n  hmRunSave();", "Remove the connection to ${whName(l.a === n ? l.b : l.a)}?`; }", ('runs',)),
    ('Undo stopping at Carry on', "  const H = hmState(), r = H.run; if(!r || !r.log.length) return;", "  const H = hmState(), r = H.run; if(!r || !r.log.length || r.log[r.log.length - 1].t === 'carry') return;", ('runs',)),
    ('Undo past Carry on keeping the new rows', "else if(e.t === 'carry' && Array.isArray(e.rows0)) r.rows = e.rows0.map(x => ({...x}));", "", ('runs',)),
    ('"mass mass" in the connection list', "IT_WH_INFO_TXT.mass[l.mass] ? ` · ${IT_WH_INFO_TXT.mass[l.mass][0]}` : '';", "IT_WH_INFO_TXT.mass[l.mass] ? ` · mass ${IT_WH_INFO_TXT.mass[l.mass][0]}` : '';", ('runs',)),
    ('WH-01 never shown', "function hmErrHtml(){ return hmState().saveErr ?", "function hmErrHtml(){ return false ?", ('runs',)),
    ('a save dropping the other runs', "hmRunsWrite(hmRunsRead().filter(x => x.id !== r.id).concat([r]));", "hmRunsWrite([r]);", ('runs',)),
    ('a lost ship still in the steps', "LV = S.map((s, i) => i).filter(i => !S[i].lost)", "LV = S.map((s, i) => i)", ('lost',)),
    ('the part step worked out again', "  if(pl.part){   // 6b", "  if(false){   // 6b", ('lost',)),
    ('the pod left out', "if(e.pod) pl.ships.push(", "if(false) pl.ships.push(", ('lost',)),
    ('a new ship on Carry on always on the finish side', "n = {...fit(s), at: s.at0 || pl.fin, last", "n = {...fit(s), at: pl.fin, last", ('lost',)),
    ('the phone pinned line not in 3 columns', ".hm-sum .hm-sb{flex:1 1 100%; display:grid; grid-template-columns:repeat(3, minmax(0, 1fr));}", ".hm-sum .hm-sb{flex:1 1 100%;}", ('phone',)),
    ('the phone toolbar not wrapping', ".wh-ctl{left:8px; right:8px; justify-content:flex-end; gap:6px; flex-wrap:wrap; pointer-events:none;} .wh-ctl > *{flex:none; pointer-events:auto;}", ".wh-ctl{left:8px; right:8px; justify-content:flex-end; gap:6px;}", ('phone',)),
]

if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch()
        out, errs = cases(b, HTML)
        for o in out: check(False, o)
        check(not out, 'the steps (crit, roll, both sides, the risk, the finisher, polarization, words, a slow plan\'s faster jump, the time), fits\' and hulls\' masses, the panel, + Add\'s Linked to, a phone; 072: the odds split, stuck first, the safe mass, + Finisher, saved runs, WH-01, a ship lost')
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
