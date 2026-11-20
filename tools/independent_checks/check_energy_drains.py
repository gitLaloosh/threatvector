"""Neutralizers and nosferatu (PYFA CORE projected and cap-sim; build queue 060, roadmap/ewar-plan.md phase B).

    PYFA_SRC=... python3 -I tools/independent_checks/check_energy_drains.py [index.html]   -> 'N mismatches'

pyfa projects an attacker fit onto a target fit: each of the attacker's running neutralizers and nosferatu, neutralizer drones
(EV) and Cenobite squadrons runs its own handler on the target, which hands Fit.addDrain an incoming drain for the target's
capacitor simulation. Run here, UNMODIFIED, from every golden fit with one (the oracle, tools/pyfa_fit_oracle.py, with the tool's
own module states, drones in space and squadrons: inputs, as compare_fit_stats.py) onto every golden fit as the target:
  eos/effects.py Effect6187 (neutralizer), Effect6197 (nosferatu), Effect6691 (EV drones), Effect6434 (Cenobite), with pyfa's
    own calculateRangeFactor put back (tools/pyfa_effects.py stubs it for the oracle's own fits: LESSON #171);
  eos/modifiedAttributeDict.py getResistance and getResistanceAttrID (lifted by ast) on the target's energyWarfareResistance
    from the oracle (pyfa's handlers on the target fit: Capacitor Batteries, T3 Cores, Halcyon boosters, the Monitor's 0.3 and
    the Herald's 0.5 base);
  eos/saveddata/fit.py Fit.addDrain (lifted by ast): the capital neutralizers' signature factor; the extra drains as
    Fit.__generateDrain appends them (int(cycleTime), capNeed, clipSize, staggered, reloadTime, not an injector), typed by hand;
  Module / Drone / Fighter.canBeApplied: an offensive effect (all four are, SDE isOffensive) isn't applied to a target with
    disallowOffensiveModifiers, typed by hand.
Modules project at the distance (pyfa: projectionRange). Drones and fighters (the owner's "A", 2026-11-20): as
pyfa's EWAR graph, graphs/data/fitEwarStats/getter.py: EV drones while the distance is within the attacker's drone control range
(checkDroneControlRange, ignoreDCR off), fighters at any distance; their handlers run with projectionRange 0, as pyfa's
Fit.__runProjectionEffects projects drones and fighters (forcedProjRange=0).
Compared, over DRAIN_GRID distances, with the same target signature on both sides:
  * the attacker's inputs (amount, cycle, optimal, falloff, signature resolution) against estimate.application.projected;
  * each target's energyWarfareResistance and disallowOffensiveModifiers against estimate.projectedTarget;
  * the drain list against pyfaEnergyDrainsAt (energy_grid.mjs), as multisets, 1e-9 relative;
  * on SIM_TARGETS, pyfa's own eos/capSim.py (as tools/cap_sim_oracle.py runs it) on the target's best case plus pyfa's drains
    against capSimPyfa on the same best case plus the tool's: stable, stable % (rounded as pyfa), the exact empty time;
  * MUTANTS: each change to one rule of the tool's drain code must make it fail.
"""
import sys, os, ast, json, subprocess, tempfile, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
from pyfa_sde import PYFA_SRC, effs
from pyfa_fit_oracle import EFFECTS
from golden_oracle import oracle_for, GOLDEN
from check_projected import _Eff, _calc, _lift_method, getResistance, tool_states, tool_fighters

NEUT, NOS, EV, CENO = 6187, 6197, 6691, 6434
DRAIN_GRID = [0, 2000, 5000, 6250, 7500, 7600, 10000, 15000, 20000, 25000, 30000, 36000, 45000, 54000, 60000, 61000, 72000, 90000, 140000]
SIM_DISTANCES = [0, 20000, 45000]
_spec = importlib.util.spec_from_file_location('capSim', os.path.join(PYFA_SRC, 'eos', 'capSim.py'))
capSim = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(capSim)
addDrain = _lift_method('eos/saveddata/fit.py', 'Fit', 'addDrain', {})
# The neutralizer handlers import ModifiedAttributeDict inside their body (`from eos.modifiedAttributeDict import ...`) for its
# getResistance: a stand-in module whose only member is pyfa's own getResistance, lifted by ast in check_projected.py.
import types as _types
_mad = _types.ModuleType('eos.modifiedAttributeDict')
class _ModifiedAttributeDict: getResistance = staticmethod(getResistance)
_mad.ModifiedAttributeDict = _ModifiedAttributeDict
sys.modules.setdefault('eos', _types.ModuleType('eos')); sys.modules['eos.modifiedAttributeDict'] = _mad

class _Ship:
    """The target's ship as the handlers and addDrain read it: getModifiedItemAttr and itemModifiedAttributes[name]."""
    def __init__(s, v): s.v = v; s.itemModifiedAttributes = v
    def getModifiedItemAttr(s, k, default=0):
        x = s.v.get(k); return x if x is not None else default
class _Target:
    def __init__(s, vals):
        s.ship = _Ship(vals); s.modifier = None
        setattr(s, '__extraDrains', [])   # addDrain is lifted out of the class, so its self.__extraDrains isn't name-mangled
    def getModifier(s): return s.modifier
    def addDrain(s, src, cycleTime, capNeed, clipSize=0, reloadTime=0): return addDrain(s, src, cycleTime, capNeed, clipSize, reloadTime)
    def drains(s): return [(int(c), n, k, False, r, False) for c, n, k, r in getattr(s, '__extraDrains')]   # Fit.__generateDrain

def sources(o):
    """(effect, item, copies, projectionRange) as pyfa runs them: active modules with 6187 / 6197 (state >= ACTIVE), each EV
    drone in space once per drone (not grouped), each Cenobite squadron once (grouped) with its neutralizer ability on."""
    out = []
    for m in o.modules:
        if m.state < 2: continue
        for e in (NEUT, NOS):
            if e in m.item.effectIds: out.append((e, m, 1, 'd'))
    for d in o.drones:
        if EV in d.item.effectIds and getattr(d, 'amountActive', 0) > 0: out.append((EV, d, d.amountActive, 0))
    for fi in o.fighters:
        if CENO in fi.activeAbilities: out.append((CENO, fi, 1, 0))
    return out

def pyfa_drains(o, tvals, d):
    """pyfa's drain list from attacker o on a target with attributes tvals at distance d."""
    if tvals.get('disallowOffensiveModifiers') == 1 and all(effs.get(str(e), {}).get('isOffensive') for e in (NEUT, NOS, EV, CENO)): return []
    tf = _Target(tvals)
    g = EFFECTS[NEUT].handler.__globals__   # LESSON #171: pyfa_effects stubs calculateRangeFactor to 1
    stub = g['calculateRangeFactor']; g['calculateRangeFactor'] = _calc['calculateRangeFactor']
    try:
        dcr = o.ship.get('droneControlRange')
        for eid, item, n, pr in sources(o):
            if eid == EV and not (d <= dcr): continue   # option A: pyfa's EWAR graph, checkDroneControlRange
            ctx = ('projected', 'drone') if eid == EV else ('projected', 'fighter') if eid == CENO else ('projected', 'module')
            for _ in range(n):
                tf.modifier = item
                EFFECTS[eid].handler(tf, item, ctx, d if pr == 'd' else pr, effect=_Eff(eid))
    finally:
        g['calculateRangeFactor'] = stub
    return tf.drains()

def pyfa_inputs(o):
    out = {'neutMods': [], 'neutDrones': [], 'neutFighters': []}
    for eid, it, n, _ in sources(o):
        g = lambda a: it.get(a) or 0
        if eid in (NEUT, NOS):
            out['neutMods'].append((eid == NOS, g('powerTransferAmount' if eid == NOS else 'energyNeutralizerAmount'), g('duration'), g('maxRange'),
                                    g('falloffEffectiveness'), g('energyNeutralizerSignatureResolution')))
        elif eid == EV: out['neutDrones'] += [(g('energyNeutralizerAmount'), g('energyNeutralizerDuration'), g('energyNeutralizerRangeOptimal'))] * n
        else: out['neutFighters'].append((g('fighterAbilityEnergyNeutralizerAmount') * it.amount, g('fighterAbilityEnergyNeutralizerDuration'),
                                          g('fighterAbilityEnergyNeutralizerOptimalRange'), g('fighterAbilityEnergyNeutralizerFalloffRange')))
    return {k: sorted(v) for k, v in out.items()}
def tool_inputs(p):
    r = lambda xs: tuple(round(x, 6) if isinstance(x, float) else x for x in xs)
    return {'neutMods': sorted(r((m['nos'], m['amount'], m['durationMs'], m['optimal'], m['falloff'], m['sigRes'])) for m in p.get('neutMods') or []),
            'neutDrones': sorted(r((x['amount'], x['durationMs'], x['optimal'])) for x in p.get('neutDrones') or []),
            'neutFighters': sorted(r((x['amount'], x['durationMs'], x['optimal'], x['falloff'])) for x in p.get('neutFighters') or [])}

def close(a, b, tol=1e-9):
    if a is None or b is None: return a == b
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))
def same_drains(a, b):
    k = lambda x: (int(x[0]), round(x[1], 6))
    a, b = sorted(a, key=k), sorted(b, key=k)
    return len(a) == len(b) and all(int(x[0]) == int(y[0]) and close(x[1], y[1]) and x[2:] == tuple(y[2:]) for x, y in zip(a, b))

def pyfa_sim(capacity, rechargeMs, drains):
    """tools/cap_sim_oracle.py's settings (pyfa Fit.__runCapSim)."""
    if not drains: return {'stable': True, 'stablePct': 100, 'timeToEmptyExactSec': None}
    sim = capSim.CapSimulator(); sim.init([tuple(x) for x in drains])
    sim.capacitorCapacity = capacity; sim.capacitorRecharge = rechargeMs; sim.startingCapacity = capacity
    sim.stagger = True; sim.scale = False; sim.t_max = 6 * 60 * 60 * 1000; sim.reload = False; sim.optimize_repeats = True
    sim.run()
    cs = (sim.cap_stable_low + sim.cap_stable_high) / (2 * sim.capacitorCapacity)
    return {'stable': cs > 0, 'stablePct': round(min(100, cs * 100), 1) if cs > 0 else None, 'timeToEmptyExactSec': None if cs > 0 else sim.t / 1000}

# Each changes one rule of the tool's drain code; the check must then find mismatches.
MUTANTS = {
    'signature factor off': ("    if(sigRes) capNeed = capNeed * Math.min(1, tgt.sig / sigRes);\n", "\n"),
    'resistance ignored': ("  const res = tgt.resist || 1;\n  const add", "  const res = 1;\n  const add"),
    'range factor off': ("    const rf = pyfaCalculateRangeFactor(m.optimal, m.falloff, distance);\n", "    const rf = 1;\n"),
    'EV drones past drone control range': ("for(const d of src.neutDrones || []) if(inDcr)", "for(const d of src.neutDrones || []) if(true)"),
    'EV drones given a falloff': ("for(const d of src.neutDrones || []) if(inDcr) add(d.durationMs, d.amount * res, 0);",
                                  "for(const d of src.neutDrones || []) if(inDcr) add(d.durationMs, d.amount * res * pyfaCalculateRangeFactor(d.optimal, d.optimal / 2, distance), 0);"),
    'disallowOffensiveModifiers ignored': ("  if(!src || !tgt || tgt.disallow) return out;\n  const res", "  if(!src || !tgt) return out;\n  const res"),
    'fighters fade with distance': ("for(const f of src.neutFighters || []) add(f.durationMs, f.amount * res, 0);",
                                    "for(const f of src.neutFighters || []) add(f.durationMs, f.amount * res * pyfaCalculateRangeFactor(f.optimal, f.falloff, distance), 0);"),
}

def run(html, tool, fits, tvals, attackers, tmp, notes, quiet=False):
    """The drain lists and simulations for every attacker x target x distance; returns the mismatch count."""
    srcs = {a: (tool[a].get('application') or {}).get('projected') or {} for a in attackers}
    cases, want = [], []
    sim_targets = [t for i, t in enumerate(sorted(tvals)) if i % 12 == 0 or 'constructed' in t]
    for a in attackers:
        for t, tv in tvals.items():
            si = ((tool[t].get('capacitor') or {}).get('simInputs')) or {}
            for d in DRAIN_GRID:
                c = {'src': a, 'tgt': {'resist': tv['tool_resist'], 'disallow': bool(tv['tool_disallow']), 'sig': tv['signatureRadius']}, 'd': d}
                withSim = t in sim_targets and d in SIM_DISTANCES and si.get('capacity', 0) > 0 and si.get('rechargeMs', 0) > 0
                if withSim: c['sim'] = {'capacity': si['capacity'], 'rechargeMs': si['rechargeMs'], 'best': si.get('best') or []}
                cases.append(c); want.append((a, t, d, withSim))
    gin, gout = os.path.join(tmp, 'ein.json'), os.path.join(tmp, 'eout.json')
    json.dump({'srcs': srcs, 'cases': cases}, open(gin, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'energy_grid.mjs'), html, gin, gout], check=True)
    got = json.load(open(gout))
    bad = 0; nd = ns = 0
    for (a, t, d, withSim), c, g in zip(want, cases, got):
        pd = pyfa_drains(fits[a], tvals[t], d); nd += 1
        if not same_drains(pd, g['drains']):
            bad += 1
            if not quiet and len(notes) < 40: notes.append(f'{a} -> {t} at {d} m: drains tool {g["drains"]} pyfa {pd}')
            continue
        if withSim:
            ns += 1
            ps = pyfa_sim(c['sim']['capacity'], c['sim']['rechargeMs'], list(c['sim']['best']) + pd); ts = g['sim']
            if ps['stable'] != ts['stable'] or ps['stablePct'] != ts['stablePct'] or not close(ps['timeToEmptyExactSec'], ts['timeToEmptyExactSec']):
                bad += 1
                if not quiet and len(notes) < 40: notes.append(f'{a} -> {t} at {d} m: capacitor tool {ts} pyfa {ps}')
    return bad, nd, ns

if __name__ == '__main__':
    ROOT = os.path.join(HERE, '..', '..')
    html = next((a for a in sys.argv[1:] if not a.startswith('--')), os.path.join(ROOT, 'index.html'))
    G = json.load(open(GOLDEN))
    tmp = tempfile.mkdtemp(); dump = os.path.join(tmp, 'd.json')
    subprocess.run(['node', os.path.join(ROOT, 'regression_suite', 'dump_results.mjs'), html, dump,
                    'application,projectedTarget,moduleStates,droneStates,fighterStates,capacitor', '-', ','.join(G)], check=True, stdout=subprocess.DEVNULL)
    tool = json.load(open(dump))
    bad, notes, fits, tvals, attackers = 0, [], {}, {}, []
    for k in G:
        if 'error' in tool[k]: notes.append(f'{k}: tool error {tool[k]["error"][:120]}'); bad += 1; continue
        states, drones = tool_states(tool[k])
        o = oracle_for(k, states=states, drones=drones, group_limits=False, fighters=tool_fighters(tool[k]))
        if o.errors or o.oracleGaps: notes.append(f'{k}: ORACLE errors {o.errors} gaps {o.oracleGaps}'); bad += 1; continue
        fits[k] = o
        pt = tool[k].get('projectedTarget')
        if pt:
            v = {n: o.ship.get(n) for n in ('signatureRadius', 'energyWarfareResistance', 'disallowOffensiveModifiers')}
            v['tool_resist'] = (pt.get('resist') or {}).get('2045'); v['tool_disallow'] = 1 if pt.get('disallowOffensiveModifiers') else 0
            if not close(v['tool_resist'], v['energyWarfareResistance'] if v['energyWarfareResistance'] is not None else 1, 1e-6) or v['tool_disallow'] != (v['disallowOffensiveModifiers'] or 0):
                bad += 1; notes.append(f"{k} (target): energyWarfareResistance tool {v['tool_resist']} pyfa {v['energyWarfareResistance']}; disallow tool {v['tool_disallow']} pyfa {v['disallowOffensiveModifiers']}")
            tvals[k] = v
        p = (tool[k].get('application') or {}).get('projected') or {}
        pi, ti = pyfa_inputs(o), tool_inputs(p)
        if any(pi.values()) or any(ti.values()):
            attackers.append(k)
            r = lambda xs: [tuple(round(x, 6) if isinstance(x, float) else x for x in t) for t in xs]
            if {kk: r(v) for kk, v in pi.items()} != {kk: r(v) for kk, v in ti.items()}: bad += 1; notes.append(f'{k} (attacker inputs): tool {ti} pyfa {pi}')
    # No ship carries disallowOffensiveModifiers in today's data (Effect6581 on the Triage Modules forces it from an attribute they
    # don't have; the items with it are structures and jump portal generators), so one made-up target holds it on both sides:
    # canBeApplied must leave it undrained (LESSON #163: the test data must hold the case the guard decides).
    base = next(iter(tvals.values()))
    tvals['(made up: disallowOffensiveModifiers)'] = dict(base, disallowOffensiveModifiers=1, tool_disallow=1)
    tool['(made up: disallowOffensiveModifiers)'] = {'capacitor': None}
    b, nd, ns = run(html, tool, fits, tvals, attackers, tmp, notes)
    bad += b
    resists = sorted({round(v['energyWarfareResistance'] or 1, 4) for v in tvals.values()})
    summary = f'{len(attackers)} attackers ({", ".join(attackers)}) x {len(tvals)} targets, {nd} drain lists, {ns} capacitor simulations; target resistances seen {resists}'
    if '--no-mutants' not in sys.argv:
        src_html = open(html, encoding='utf-8').read(); caught = []
        for mname, (a, b2) in MUTANTS.items():
            if src_html.count(a) != 1: bad += 1; notes.append(f'mutant {mname}: its text is not in {html} once'); continue
            mp = os.path.join(tmp, 'mutant.html'); open(mp, 'w', encoding='utf-8').write(src_html.replace(a, b2))
            mb, _, _ = run(mp, tool, fits, tvals, attackers, tmp, [], quiet=True)
            if mb: caught.append(mname)
            else: bad += 1; notes.append(f'mutant {mname} NOT caught')
        summary += f'; mutants caught {len(caught)} of {len(MUTANTS)}'
    for n in notes: print(n)
    print(summary)
    print(f'{bad} mismatches')
