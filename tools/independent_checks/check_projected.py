"""Projected webs / painters / scrams (PYFA CORE projected, v2026.10.14.35; roadmap/turret-application-plan.md Phase 2a).

    PYFA_SRC=... python3 -I tools/independent_checks/check_projected.py [index.html]   -> 'N mismatches'

pyfa's damage graph applies the attacker's own webs, target painters, web / painter drones and warp scramblers
to the target by default (graph setting applyProjected). This check runs pyfa's files UNMODIFIED:
  graphs/data/fitDamageStats/calc/projected.py   getScramRange, getScrammables, getTackledSpeed, getSigRadiusMult
  graphs/data/fitDamageStats/cache/projected.py  ProjectedDataCache (what each web / painter / drone contributes)
  eos/modifiedAttributeDict.py getResistanceAttrID (lifted by ast), eos/calc.py, eos/utils/float.py, graphs/calc.py
on pyfa's own attribute values for both fits -- tools/pyfa_fit_oracle.py runs pyfa's handlers on the golden fit
with the tool's resolved module states and drones in space (inputs, as compare_fit_stats.py does); the target's
speed and signature radius with extra multipliers and without the scrammed modules come from the oracle's port of
getExtended / __calculateValue (pyfa_fit_oracle.Attrs.extended). The tool's side is its PYFA CORE projected
functions on its own estimate.application.projected and estimate.projectedTarget (projected_grid.mjs).
Compared for every attacker that has a web, painter, web / painter drone or scram (and every golden fit as the
target), over a grid of distance x the target's own speed (share of its top speed) x graph settings (lock range
respected or not, drone control range ignored or not, mobile drone mode):
  * the attacker's inputs (pyfa's webMods / tpMods / webDrones / tpDrones / webFighters / tpFighters and getScramRange);
    since v2026.10.14.70 the oracle launches the squadrons the tool launched, with the abilities the tool has on
    (estimate.fighterStates: inputs), so a support squadron's web (getProjFighterData) is compared too;
  * the target's untackled top speed and signature radius;
  * at every point, the tackled speed and the painted signature radius.
Tolerance 1e-6 relative (floatUnerr keeps 7 significant digits).
Since build queue 050 (EWAR phase A, roadmap/ewar-plan.md): tracking and guidance disruptors and TD drones. pyfa's own
eos/effects.py Effect6424 / Effect6423 / Effect6694 run unmodified from every golden fit's active disruptors and TD drones
in space onto every golden fit's weapons (the oracle's modules and charges, context ('projected', ...), each drone once),
over DIS_GRID distances, with the victim's weaponDisruptionResistance through pyfa's getResistance (lifted by ast); then:
  * the source's inputs (optimal, falloff, bonuses) against projectedTarget.disrupt, and each victim's resistance and
    disallowOffensiveModifiers against application.wdVictim;
  * every weapon attribute pyfa changed (turret maxRange / falloff / trackingSpeed; the charge's aoeCloudSize /
    aoeVelocity / maxVelocity / explosionDelay) against the tool's pyfaDisruptionMults and pyfaDisruptedApp, and the
    missile's flight range against pyfa's Module.missileMaxRangeData (lifted) on the disrupted charge;
  * the stacking rule the tool's shortcut rests on: no fitted module, rig, subsystem or hull puts a penalised modifier of
    the disruptors' sign on those attributes (WEAPON_RANGE_MOD_EFFECTS);
  * DIS_MUTANTS: each change to one rule of the tool's code must make the disruptor part fail.
"""
import sys, os, re, ast, json, subprocess, tempfile, itertools, collections, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
from pyfa_sde import PYFA_SRC, ename, effs
from pyfa_fit_oracle import EFFECTS
from golden_oracle import oracle_for, GOLDEN

# ---- pyfa's own code ----------------------------------------------------------------------------------------
SETTINGS = {'mobileDroneMode': 1, 'ignoreDCR': False, 'ignoreResists': True, 'ignoreLockRange': True, 'applyProjected': True}
class GraphSettings:
    @classmethod
    def getInstance(cls): return cls
    @classmethod
    def get(cls, k): return SETTINGS[k]
def _exec(rel, ns, drop=()):
    src = open(os.path.join(PYFA_SRC, rel), encoding='utf-8').read()
    for pat in drop: src = re.sub(pat, '', src, flags=re.M)
    exec(compile(src, rel, 'exec'), ns)
    return ns
def _lift(rel, fname, ns):
    src = open(os.path.join(PYFA_SRC, rel), encoding='utf-8').read()
    node = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == fname)
    exec(compile(ast.Module(body=[node], type_ignores=[]), rel, 'exec'), ns)
    return ns[fname]
_float = _exec('eos/utils/float.py', {})
_calc = _exec('eos/calc.py', {})
_sconst = _exec('service/const.py', {})
_gcalc = _exec('graphs/calc.py', {'GraphSettings': GraphSettings}, drop=[r'^from service\.settings import .*$'])
PROJ = _exec('graphs/data/fitDamageStats/calc/projected.py', {
    'calculateRangeFactor': _calc['calculateRangeFactor'], 'floatUnerr': _float['floatUnerr'], 'checkLockRange': _gcalc['checkLockRange'],
    'checkDroneControlRange': _gcalc['checkDroneControlRange'], 'GraphDpsDroneMode': _sconst['GraphDpsDroneMode'], 'GraphSettings': GraphSettings},
    drop=[r'^from (eos|graphs|service)\.\S+ import .*$', r'^import math$'])
PROJ['math'] = __import__('math')
getResistanceAttrID = _lift('eos/modifiedAttributeDict.py', 'getResistanceAttrID', {'resistanceCache': {}})
class FitDataCache:   # graphs/data/base: a per-fit dict
    def __init__(s): s._data = {}
CACHE = _exec('graphs/data/fitDamageStats/cache/projected.py', {'getResistanceAttrID': getResistanceAttrID, 'FitDataCache': FitDataCache},
              drop=[r'^from (eos|graphs)\.\S+ import .*$'])
ProjectedDataCache = CACHE['ProjectedDataCache']
DroneMode = _sconst['GraphDpsDroneMode']

# ---- pyfa-shaped fits over the oracle -------------------------------------------------------------------------
class _Eff:
    """eos.gamedata.Effect: resistanceID (SDE resistanceAttributeID) and getattr() of the handler class."""
    def __init__(s, eid): s.ID = eid; s.name = ename(eid); s.resistanceID = effs.get(str(eid), {}).get('resistanceAttributeID'); s.type = getattr(EFFECTS.get(eid), 'type', None)
    def getattr(s, k): return getattr(EFFECTS.get(s.ID), k, None)
class _G:
    def __init__(s, n): s.name = n
class _I:
    def __init__(s, gi): s.ID = int(gi.ID); s.name = gi.name; s.group = _G(gi.group.name); s.effects = {ename(e): _Eff(e) for e in gi.effectIds}
class _Owner:
    def __init__(s, o): s.ship = _Attr(o.ship)
class _Attr:
    def __init__(s, it): s.it = it
    def getModifiedItemAttr(s, k, default=0):
        v = s.it.get(k); return v if v is not None else default
class _Mod(_Attr):
    """eos Module: item / charge effects, modified attributes, maxRange and falloff (eos/saveddata/module.py)."""
    def __init__(s, m, o):
        super().__init__(m); s.m = m; s.owner = _Owner(o)
        s.item = _I(m.item); s.charge = _I(m.charge.item) if m.charge is not None else None
    @property
    def maxRange(s):
        for a in ("maxRange", "shieldTransferRange", "powerTransferRange", "energyDestabilizationRange", "empFieldRange",
                  "ecmBurstRange", "warpScrambleRange", "cargoScanRange", "shipScanRange", "surveyScanRange"):
            v = s.getModifiedItemAttr(a)
            if v:
                if 'burst projector' in s.item.name.lower(): v -= s.owner.ship.getModifiedItemAttr("radius")
                return v
        return None
    @property
    def falloff(s):
        for a in ("falloffEffectiveness", "falloff", "shipScanFalloff"):
            v = s.getModifiedItemAttr(a)
            if v: return v
class _Drone(_Attr):
    """eos Drone: amountActive, maxRange and falloff (eos/saveddata/drone.py)."""
    def __init__(s, d):
        super().__init__(d); s.item = _I(d.item); s.amountActive = d.amountActive; s.charge = None
    @property
    def maxRange(s):
        for a in ("shieldTransferRange", "powerTransferRange", "energyDestabilizationRange", "empFieldRange", "ecmBurstRange", "maxRange", "ECMRangeOptimal"):
            v = s.getModifiedItemAttr(a)
            if v: return v
    @property
    def falloff(s):
        for a in ("falloff", "falloffEffectiveness"):
            v = s.getModifiedItemAttr(a)
            if v: return v
class _Ability:
    """eos FighterAbility: its effect (name, resistanceID, prefix via getattr)."""
    def __init__(s, eid): s.effect = _Eff(eid)
class _Fighter(_Attr):
    """eos Fighter (one squadron): amount, its item's effects, modified attributes."""
    def __init__(s, fi):
        super().__init__(fi); s.item = _I(fi.item); s.amount = fi.amount; s.active = sorted(fi.activeAbilities)
class _FitItem:
    def __init__(s, o):
        s.o = o; s.ID = id(o)
        s.mods = [_Mod(m, o) for m in o.modules if m.state >= 2]
        s.drones = [_Drone(d) for d in o.drones if d.amountActive > 0]
        s.fighters = [_Fighter(fi) for fi in o.fighters]
        s.ship = _Attr(o.ship)
        s.maxTargetRange = o.ship.get('maxTargetRange')
        s.extraAttributes = {'droneControlRange': o.ship.get('droneControlRange')}
    def activeModulesIter(s): return iter(s.mods)
    def activeDronesIter(s): return iter(s.drones)
    def activeFighterAbilityIter(s):
        # eos Fit.activeFighterAbilityIter: every ability switched on of every squadron in space (v2026.10.14.70: the
        # tool's launch and abilities, its fighterStates, are inputs here as in check_application.py)
        for fi in s.fighters:
            for e in fi.active: yield fi, _Ability(e)
class _Fit:
    """graphs/wrapper.py SourceWrapper / TargetWrapper over an oracle fit."""
    isFit = True; isProfile = False
    def __init__(s, o): s.o = o; s.item = _FitItem(o)
    def getRadius(s): return s.o.ship.get('radius')
    def getMaxVelocity(s, extraMultipliers=None, ignoreAfflictors=()):
        if extraMultipliers or ignoreAfflictors: return s.o.ship.attrs.extended('maxVelocity', extraMultipliers, [a.m for a in ignoreAfflictors])
        return s.o.ship.get('maxVelocity')
    def getSigRadius(s, extraMultipliers=None, ignoreAfflictors=()):
        if extraMultipliers or ignoreAfflictors: return s.o.ship.attrs.extended('signatureRadius', extraMultipliers, [a.m for a in ignoreAfflictors])
        return s.o.ship.get('signatureRadius')

def pyfa_inputs(src):
    cache = ProjectedDataCache()
    webMods, tpMods = cache.getProjModData(src); webDrones, tpDrones = cache.getProjDroneData(src); webFighters, tpFighters = cache.getProjFighterData(src)
    return {'scramRange': PROJ['getScramRange'](src), 'webMods': webMods, 'tpMods': tpMods, 'webDrones': webDrones, 'tpDrones': tpDrones,
            'webFighters': webFighters, 'tpFighters': tpFighters}

def pyfa_point(src, tgt, inp, p):
    """getter.py _calculatePoint with applyProjected on: tackled speed, then the signature radius at that speed."""
    SETTINGS.update(ignoreLockRange=p['ignoreLockRange'], ignoreDCR=p['ignoreDCR'], mobileDroneMode=DroneMode(p['droneMode']))
    scrammables = PROJ['getScrammables'](tgt=tgt)
    d = p['distance']; cur = p['speedFrac'] * tgt.getMaxVelocity()
    speed = PROJ['getTackledSpeed'](src=src, tgt=tgt, currentUntackledSpeed=cur, srcScramRange=inp['scramRange'], tgtScrammables=scrammables,
                                    webMods=inp['webMods'], webDrones=inp['webDrones'], webFighters=inp['webFighters'], distance=d)
    sig = tgt.getSigRadius() * PROJ['getSigRadiusMult'](src=src, tgt=tgt, tgtSpeed=speed, srcScramRange=inp['scramRange'], tgtScrammables=scrammables,
                                                         tpMods=inp['tpMods'], tpDrones=inp['tpDrones'], tpFighters=inp['tpFighters'], distance=d)
    return speed, sig

GRID = [dict(distance=d, speedFrac=f, ignoreLockRange=il, ignoreDCR=idcr, droneMode=dm)
        for d, f, (il, idcr, dm) in itertools.product(
            [0, 1500, 5000, 9000, 10000, 12000, 13400, 16000, 20000, 30000, 45000, 80000, 150000],   # 13400: inside a Berserker SW-900 optimal only from the drone itself (optimal - attacker radius + drone radius)
            [0, 0.35, 1],
            [(True, False, 1), (False, False, 1), (True, True, 3), (True, False, 2)])]

def close(a, b):
    if a is None or b is None: return a == b
    return abs(a - b) <= 1e-6 * max(1.0, abs(a), abs(b))
def key_of(x, mobile):
    t = (round(x[0], 9), round(x[1], 6), round(x[2], 6), x[3], x[4])
    return t + ((round(x[5], 6), round(x[6], 6)) if mobile else ())

def tool_states(t):
    ms = (t.get('moduleStates') or {}).get('items') or []
    states = {str(it['typeId']): {'active': round(it['active']), 'online': round(it['online']), 'offline': round(it['offline'])} for it in ms}
    drones = [(it['typeId'], round(it['active'])) for it in ((t.get('droneStates') or {}).get('items') or []) if round(it['active']) > 0]
    return states, drones

def tool_fighters(t):
    """[(typeId, squadron size, active ability ids)] per squadron the tool launched (estimate.fighterStates: damage AND
    support squadrons, v2026.10.14.70)."""
    out = []
    for it in ((t.get('fighterStates') or {}).get('items') or []):
        out += [(it['typeId'], it['squadronSize'], [a['effectId'] for a in it.get('abilities') or [] if a.get('on')])] * int(it.get('active') or 0)
    return out

# ---- build queue 050: tracking / guidance disruptors and TD drones (phase A of roadmap/ewar-plan.md) ----------
# pyfa applies an attacker's disruptors to the disrupted fit's weapons when that fit is projected (eos/saveddata/fit.py
# projected modules and drones, Module / Drone.calculateModifiedAttributes with context ('projected', ...)). Run here:
#   eos/effects.py Effect6424 (Tracking Disruptor), Effect6423 (Guidance Disruptor), Effect6694 (TD drones), unmodified,
#   on the source's oracle module / drone, against the victim's oracle modules (pyfa_fit_oracle HandledList filters);
#   eos/modifiedAttributeDict.py ModifiedAttributeDict.getResistance (lifted by ast) and getResistanceAttrID for the
#   victim's resistance. The one hand port is multiply's resisted step (lines 539-546: m = (m - 1) * resist + 1 before
#   the stacking chain), which the oracle's Attrs.multiply leaves out because nothing it ran before was projected.
# The victim's weapon attributes are read before and after; their ratio is what the tool must multiply by
# (pyfaDisruptionMults / pyfaDisruptedApp), so this also proves the tool's shortcut (the disruptors' own penalised chain
# times the victim's finished value) is exact: a victim modifier of the same sign in the same stacking group would make
# the ratio differ. Missiles: the charge's maxVelocity and explosionDelay against the tool's mrIn x its multipliers.
def _lift_method(rel, cls, fname, ns):
    src = open(os.path.join(PYFA_SRC, rel), encoding='utf-8').read()
    c = next(n for n in ast.parse(src).body if isinstance(n, ast.ClassDef) and n.name == cls)
    node = next(n for n in c.body if isinstance(n, ast.FunctionDef) and n.name == fname)
    node.decorator_list = []
    exec(compile(ast.Module(body=[node], type_ignores=[]), rel, 'exec'), ns)
    return ns[fname]
from pyfa_fit_oracle import ATTR_BY_ID
class _AttrInfo:
    def __init__(s, i): s.attributeName = ATTR_BY_ID[int(i)]['name'] if int(i) in ATTR_BY_ID else None
getResistance = _lift_method('eos/modifiedAttributeDict.py', 'ModifiedAttributeDict', 'getResistance',
                             {'getResistanceAttrID': getResistanceAttrID, 'getAttributeInfo': _AttrInfo})
PROJ_TD, PROJ_GD, PROJ_TDD = 6424, 6423, 6694
_missileMaxRangeData = _lift_method('eos/saveddata/module.py', 'Module', 'missileMaxRangeData', {'math': __import__('math'), 'floatUnerr': _float['floatUnerr']})
class _MrCharge:
    def __init__(s, ch): s.group = ch.item.group; s.effects = {ename(e) for e in ch.item.effectIds}
class _MrMod:
    """eos Module as missileMaxRangeData reads it, with the charge's attributes as pyfa left them after the disruptors."""
    def __init__(s, mo, vo, vals): s.charge = _MrCharge(mo.charge); s._v = vals; s._c = mo.charge; s.owner = vo
    def getModifiedChargeAttr(s, k, default=0):
        v = s._v.get('c.' + k)
        if v is None: v = s._c.attrs.get(k)
        return v if v is not None else default
def _mr_after(mo, vo, vals):
    r = _missileMaxRangeData(_MrMod(mo, vo, vals))
    return list(r) if r else None
DIS_GRID = [0, 5000, 9375, 9400, 20000, 36000, 50000, 60000, 72000, 90000, 108000, 130000, 160000, 250000]   # 9375: an Infiltrator TD-600's own maxRange (TD drones: full strength up to it, nothing past)
TURRET_ATTRS = ('maxRange', 'falloff', 'trackingSpeed')
CHARGE_ATTRS = ('aoeCloudSize', 'aoeVelocity', 'maxVelocity', 'explosionDelay')
TOOL_KEY = {'maxRange': 'optimal', 'falloff': 'falloff', 'trackingSpeed': 'tracking', 'aoeCloudSize': 'aoeCloudSize',
            'aoeVelocity': 'aoeVelocity', 'maxVelocity': 'maxVelocity', 'explosionDelay': 'explosionDelay'}

class _VictimFit:
    """What the handlers touch on the disrupted fit: fit.ship (disallowOffensiveModifiers, the resistance attribute),
    fit.getModifier() (eos Fit: the item whose effect runs) and fit.modules, whose boosts go through _resisted."""
    def __init__(s, o): s.o = o; s.ship = o.ship; s.modules = _ResList(s, o.modules); s.modifier = None
    def getModifier(s): return s.modifier
class _ResList:
    def __init__(s, vf, mods): s.vf, s.mods = vf, mods
    def _boost(s, charge):
        def f(flt, key, boostFactor, skill=None, **kw):
            for el in s.mods:
                try:
                    if not flt(el): continue
                except AttributeError: continue
                tgt = el.charge if charge else el
                if tgt is None: continue
                m = 1 + boostFactor / 100.0                              # ModifiedAttributeDict.boost
                if 'effect' in kw:                                       # ModifiedAttributeDict.multiply, lines 542-546
                    r = getResistance(s.vf, kw['effect']) or 1
                    if r != 1: m = (m - 1) * r + 1
                tgt.attrs.multiply(key, m, stackingPenalties=kw.get('stackingPenalties', False), penaltyGroup=kw.get('penaltyGroup', 'default'))
        return f
    def __getattr__(s, k):
        if k == 'filteredItemBoost': return s._boost(False)
        if k == 'filteredChargeBoost': return s._boost(True)
        raise AttributeError(k)

def dis_sources(o):
    """The source fit's disruptors as pyfa runs them: active modules carrying 6424 / 6423 (state >= ACTIVE: the 'active'
    type), and each TD drone in space once per drone (Drone.calculateModifiedAttributes: not grouped)."""
    out = []
    for m in o.modules:
        if m.state < 2: continue
        for e in (PROJ_TD, PROJ_GD):
            if e in m.item.effectIds: out.append((e, m, 1))
    for d in o.drones:
        if PROJ_TDD in d.item.effectIds and getattr(d, 'amountActive', 0) > 0: out.append((PROJ_TDD, d, d.amountActive))
    return out

def dis_read(v):
    """Per victim module: (weapon type, charge type, {attr: value}) for every module with a charge or a turret skill."""
    rows = []
    for m in v.modules:
        vals = {a: m.attrs.get(a) for a in TURRET_ATTRS}
        if m.charge is not None: vals.update({'c.' + a: m.charge.attrs.get(a) for a in CHARGE_ATTRS})
        rows.append((m.item.ID, m.charge.item.ID if m.charge is not None else None, vals))
    return rows

@contextlib.contextmanager
def dis_on(src_o, v, distance):
    """pyfa's handlers from every source disruptor on victim v at distance, undone when the block ends (check_matchup.py
    computes the disrupted fight inside one)."""
    keep = [(x.attrs, {k: {g: list(ms) for g, ms in d.items()} for k, d in x.attrs.pen.items()}, dict(x.attrs.mult),
             {k: list(a) for k, a in x.attrs.afflictions.items()}) for m in v.modules for x in (m, m.charge) if x is not None]
    vf = _VictimFit(v)
    g = EFFECTS[PROJ_TD].handler.__globals__   # tools/pyfa_effects.py stubs calculateRangeFactor (1) for the oracle's own fits (LESSON #171)
    stub = g['calculateRangeFactor']; g['calculateRangeFactor'] = _calc['calculateRangeFactor']
    try:
        for eid, item, n in dis_sources(src_o):
            ctx = ('projected', 'drone') if eid == PROJ_TDD else ('projected', 'module')
            for _ in range(n):
                vf.modifier = item
                EFFECTS[eid].handler(vf, item, ctx, distance, effect=_Eff(eid))
        g['calculateRangeFactor'] = stub
        yield v
    finally:
        g['calculateRangeFactor'] = stub
        for attrs_, pen, mult, aff in keep: attrs_.pen, attrs_.mult, attrs_.afflictions = pen, mult, aff
def dis_apply(src_o, v, distance):
    """dis_read of victim v with the source's disruptors on it at distance (then undone)."""
    with dis_on(src_o, v, distance): return dis_read(v)

def dis_inputs(o):
    """The source's disruptor inputs as pyfa's handlers read them (optimal, falloff, the bonus attributes)."""
    td, gd, dr = [], [], []
    for eid, it, n in dis_sources(o):
        g = lambda a: it.attrs.get(a) or 0
        if eid == PROJ_TD: td.append((g('maxRange'), g('falloffEffectiveness'), g('trackingSpeedBonus'), g('maxRangeBonus'), g('falloffBonus')))
        elif eid == PROJ_GD: gd.append((g('maxRange'), g('falloffEffectiveness'), g('aoeCloudSizeBonus'), g('aoeVelocityBonus'), g('missileVelocityBonus'), g('explosionDelayBonus')))
        else: dr += [(g('maxRange'), 0, g('trackingSpeedBonus'), g('maxRangeBonus'), g('falloffBonus'))] * n
    return sorted(td), sorted(gd), sorted(dr)
def dis_tool_inputs(d):
    r = lambda xs: [round(x, 6) for x in xs]
    td = sorted(tuple(r((m['optimal'], m['falloff'], m['bonus']['trackingSpeedBonus'], m['bonus']['maxRangeBonus'], m['bonus']['falloffBonus']))) for m in d.get('tdMods') or [])
    gd = sorted(tuple(r((m['optimal'], m['falloff'], m['bonus']['aoeCloudSizeBonus'], m['bonus']['aoeVelocityBonus'], m['bonus']['missileVelocityBonus'], m['bonus']['explosionDelayBonus']))) for m in d.get('gdMods') or [])
    dr = sorted(tuple(r((m['optimal'], m['falloff'], m['bonus']['trackingSpeedBonus'], m['bonus']['maxRangeBonus'], m['bonus']['falloffBonus']))) for m in d.get('tdDrones') or [])
    return td, gd, dr

def dis_assert_signs(html):
    """The tool multiplies its finished weapon value by the disruptors' own penalised product. That equals pyfa only while
    no fitted module, rig or hull of the victim puts a penalised modifier of the SAME sign as the disruptor on that
    attribute (pyfa penalises >1 and <1 chains apart). WEAPON_RANGE_MOD_EFFECTS (gen_weapon_range_table.py, every pyfa
    handler on these attributes) lists each modifier's source attribute: every penalised row's carriers must have the
    opposite sign. A carrier at 0 (an unscripted or zeroed bonus) is neither."""
    from pyfa_sde import td as TDOGMA, cat
    m = re.search(r'const WEAPON_RANGE_MOD_EFFECTS = (\{.*?\});\n// ==== PYFA CORE END weapon-range-table', open(html, encoding='utf-8').read(), re.S)
    table = json.loads(m.group(1))
    disruptor_sign = {'optimal': -1, 'falloff': -1, 'tracking': -1, 'missileVelocity': -1, 'missileFlightTime': -1,
                      'missileExplosionVelocity': -1, 'missileExplosionRadius': +1}
    carriers = collections.defaultdict(list)
    for t, v in TDOGMA.items():
        if cat(int(t)) not in (6, 7, 32): continue
        for e in v.get('dogmaEffects', []): carriers[str(e['effectID'])].append(t)
    bad = []; seen = 0
    for eid, rows in table.items():
        for tgt, sk, gs, src, per, pen in rows:
            if not pen or tgt not in disruptor_sign: continue
            seen += 1
            for t in carriers.get(eid, []):
                val = next((a['value'] for a in TDOGMA[t].get('dogmaAttributes', []) if a['attributeID'] == src), ATTR_BY_ID.get(src, {}).get('defaultValue', 0))
                if val and (val > 0) == (disruptor_sign[tgt] > 0): bad.append(f'effect {eid} on type {t}: {tgt} {val:+g} (same sign as a disruptor)')
    if seen < 10: bad.append(f'only {seen} penalised rows in WEAPON_RANGE_MOD_EFFECTS (the table moved?)')
    return bad, seen

DIS_MUTANTS = {
    'no stacking penalty': ('out[k] = pyfaPenalizedProduct(lists[k]);', 'out[k] = lists[k].reduce((a, b) => a * b, 1);'),
    'no range factor': ('push(k, m.bonus[b] * rangeFactor);', 'push(k, m.bonus[b]);'),
    'resistance ignored': ('if(res !== 1) m = (m - 1) * res + 1;', ''),
    'drones past their range': ('if(d.optimal < (distance || 0)) continue;', ''),
    'flight time not disrupted': ('ms * k.explosionDelay', 'ms'),
    'explosion velocity not disrupted': ('aoeVelocity: w.aoeVelocity * k.aoeVelocity', 'aoeVelocity: w.aoeVelocity'),
}
def disruptor_check(html, tool, fit, G, tmp):
    bad, notes = 0, []
    signs, nrows = dis_assert_signs(html)
    for b in signs: bad += 1; notes.append('stacking: ' + b)
    sources = []
    for k in G:
        o = fit(k).o
        if o.errors or o.oracleGaps: continue
        pt = tool[k].get('projectedTarget') or {}
        pin, tin = dis_inputs(o), dis_tool_inputs(pt.get('disrupt') or {})
        pin_r = tuple(sorted(tuple(round(x, 6) for x in r) for r in lst) for lst in pin)
        if pin_r != tuple(tin): bad += 1; notes.append(f'{k} (disruptor inputs): tool {tin} pyfa {pin_r}')
        if any(pin): sources.append(k)
    victims = [k for k in G if (tool[k].get('application') or {}).get('weapons') and not (fit(k).o.errors or fit(k).o.oracleGaps)]
    for k in victims:
        wv = tool[k]['application'].get('wdVictim') or {}
        ship = fit(k).o.ship
        pr, pdis = ship.attrs.get('weaponDisruptionResistance'), bool(ship.attrs.get('disallowOffensiveModifiers'))
        if not close(wv.get('resist'), pr if pr is not None else 1.0) or bool(wv.get('disallow')) != pdis:
            bad += 1; notes.append(f'{k} (victim): tool {wv} pyfa resist {pr} disallow {pdis}')
    pairs = [(v, s) for s in sources for v in victims]
    gin, gout = os.path.join(tmp, 'din.json'), os.path.join(tmp, 'dout.json')
    json.dump({'apps': {v: tool[v]['application'] for v in victims}, 'srcs': {s: tool[s]['projectedTarget']['disrupt'] for s in sources},
               'dpairs': pairs, 'dgrid': DIS_GRID}, open(gin, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'projected_grid.mjs'), html, gin, gout], check=True)
    out = json.load(open(gout))['disrupt']
    points = changed = 0
    for v, s in pairs:
        vo, so = fit(v).o, fit(s).o
        before = dis_read(vo)
        diffs = []
        for i, d in enumerate(DIS_GRID):
            after = dis_apply(so, vo, d)
            k, weapons = out[v + '|' + s][i]
            points += 1
            for w in weapons:
                rows = [((b[2], a[2]), mo) for b, a, mo in zip(before, after, vo.modules) if b[0] == w['weaponTypeId'] and b[1] == w.get('ammoTypeId')]
                if not rows: diffs.append(f'd={d} {w["name"]}: no pyfa module'); continue
                on = w.get('gunnery') if w['kind'] == 'turret' else w.get('mlo')
                names = TURRET_ATTRS if w['kind'] == 'turret' else tuple('c.' + a for a in CHARGE_ATTRS) if w['kind'] == 'missile' else ()
                for (bv, av), mo in rows:
                    for a in names:
                        if bv.get(a) is None: continue
                        ratio = av[a] / bv[a] if bv[a] else 1.0
                        want = k[TOOL_KEY[a.replace('c.', '')]] if on else 1.0
                        if ratio != 1.0: changed += 1
                        if not close(ratio, want): diffs.append(f'd={d} {w["name"]} {w.get("ammoName")} {a}: pyfa x{ratio} tool x{want}')
                        tk = TOOL_KEY[a.replace('c.', '')]
                        if tk in w['dis'] and not close(w['dis'][tk], w['base'][tk] * ratio):
                            diffs.append(f'd={d} {w["name"]} {tk}: tool {w["dis"][tk]} = {w["base"][tk]} x pyfa {ratio}?')
                    if w['kind'] == 'missile' and w.get('mrIn'):
                        if not close(w['mrIn'][0], bv['c.maxVelocity']) or not close(w['mrIn'][1], bv['c.explosionDelay']):
                            diffs.append(f'{w["name"]}: mrIn {w["mrIn"][:2]} pyfa {bv["c.maxVelocity"]}, {bv["c.explosionDelay"]}')
                        pm = _mr_after(mo, vo, av)
                        tm = w['dis'].get('missileMaxRangeData')
                        if (pm is None) != (tm is None) or (pm and not all(close(x, y) for x, y in zip(tm, pm))):
                            diffs.append(f'd={d} {w["name"]} {w.get("ammoName")}: flight range tool {tm} pyfa {pm}')
        if diffs: bad += 1; notes.append(f'{s} disrupts {v}: ' + '; '.join(diffs[:4]))
    return bad, notes, f'disruptors: {nrows} penalised own-fit rows of the opposite sign; {len(sources)} sources x {len(victims)} victims, {points} points ({changed} weapon attributes pyfa changes)'

if __name__ == '__main__':
    ROOT = os.path.join(HERE, '..', '..')
    html = next((a for a in sys.argv[1:] if not a.startswith('--')), os.path.join(ROOT, 'index.html'))
    G = json.load(open(GOLDEN))
    tmp = tempfile.mkdtemp(); dump = os.path.join(tmp, 'd.json')
    subprocess.run(['node', os.path.join(ROOT, 'regression_suite', 'dump_results.mjs'), html, dump, 'application,projectedTarget,moduleStates,droneStates,fighterStates', '-', ','.join(G)], check=True, stdout=subprocess.DEVNULL)
    tool = json.load(open(dump))
    fits = {}
    def fit(k):
        if k not in fits:
            states, drones = tool_states(tool[k])
            fits[k] = _Fit(oracle_for(k, states=states, drones=drones, group_limits=False, fighters=tool_fighters(tool[k])))
        return fits[k]
    bad, notes = 0, []
    # attackers: every fit the tool OR pyfa sees a web / painter / web drone / scram on
    attackers, inputs = [], {}
    for k in G:
        o = fit(k).o
        if o.errors or o.oracleGaps: notes.append(f'{k}: ORACLE errors {o.errors} gaps {o.oracleGaps}'); bad += 1; continue
        inp = pyfa_inputs(fit(k)); inputs[k] = inp
        tp = ((tool[k].get('application') or {}).get('projected')) or {}
        has_pyfa = inp['scramRange'] is not None or any(inp[x] for x in ('webMods', 'tpMods', 'webDrones', 'tpDrones', 'webFighters', 'tpFighters'))
        has_tool = tp.get('scramRange') is not None or any(tp.get(x) for x in ('webMods', 'tpMods', 'webDrones', 'tpDrones', 'webFighters', 'tpFighters'))
        if not (has_pyfa or has_tool): continue
        attackers.append(k)
        diffs = []
        if not close(tp.get('scramRange'), inp['scramRange']): diffs.append(f"scramRange tool {tp.get('scramRange')} pyfa {inp['scramRange']}")
        if not close((tool[k].get('application') or {}).get('lockRange') or 0, fit(k).item.maxTargetRange): diffs.append('lockRange')
        if not close(tp.get('droneControlRange') or 0, fit(k).item.extraAttributes['droneControlRange']): diffs.append(f"droneControlRange tool {tp.get('droneControlRange')} pyfa {fit(k).item.extraAttributes['droneControlRange']}")
        for name, mobile in (('webMods', 0), ('tpMods', 0), ('webDrones', 1), ('tpDrones', 1), ('webFighters', 1), ('tpFighters', 1)):
            pk = sorted(key_of(tuple(x), mobile) for x in inp[name])
            tk = sorted(key_of((x['boost'], x['optimal'], x['falloff'], x['stackingGroup'], x['resAttrID']) + ((x['speed'], x['radius']) if mobile else ()), mobile) for x in tp.get(name) or [])
            if pk != tk: diffs.append(f'{name} tool {tk} pyfa {pk}')
        if diffs: bad += 1; notes.append(f'{k} (attacker inputs): ' + '; '.join(diffs))
    targets = [k for k in G if tool[k].get('projectedTarget')]
    missing = [k for k in G if not tool[k].get('projectedTarget')]
    if missing: notes.append(f'no projectedTarget (hull record without effects): {missing}')
    pairs = [(a, t) for a in attackers for t in targets if a in inputs and t in inputs]
    gin, gout = os.path.join(tmp, 'in.json'), os.path.join(tmp, 'out.json')
    json.dump({'apps': {a: tool[a]['application'] for a in attackers}, 'targets': {t: tool[t]['projectedTarget'] for t in targets},
               'pairs': pairs, 'grid': GRID}, open(gin, 'w'))
    subprocess.run(['node', os.path.join(HERE, 'projected_grid.mjs'), html, gin, gout], check=True)
    out = json.load(open(gout))
    for t in targets:
        tv, ts = out['targets'][t]
        pv, ps = fit(t).getMaxVelocity(), fit(t).getSigRadius()
        if not (close(tv, pv) and close(ts, ps)): bad += 1; notes.append(f'{t} (target): maxVelocity tool {tv} pyfa {pv}; signatureRadius tool {ts} pyfa {ps}')
    points = exact = changed = 0
    for a, t in pairs:
        src, tgt, inp = fit(a), fit(t), inputs[a]
        tp = out['points'][a + '|' + t]
        diffs = []
        for i, p in enumerate(GRID):
            ps, pg = pyfa_point(src, tgt, inp, p); points += 1
            ts, tg = tp[i]
            if not (close(ts, ps) and close(tg, pg)):
                if len(diffs) < 4: diffs.append(f'{p} speed tool {ts} pyfa {ps}; sig tool {tg} pyfa {pg}')
            elif ts == ps and tg == pg: exact += 1
            if ps != p['speedFrac'] * tgt.getMaxVelocity() or pg != tgt.getSigRadius(): changed += 1
        if diffs: bad += 1; notes.append(f'{a} -> {t}: ' + '; '.join(diffs))
    dbad, dnotes, dsum = disruptor_check(html, tool, fit, G, tmp)
    bad += dbad; notes += dnotes
    # Each mutant changes one rule of the tool's disruptor code; the disruptor part above must then find mismatches.
    src_html = open(html, encoding='utf-8').read(); caught = []
    for mname, (a, b) in DIS_MUTANTS.items():
        if src_html.count(a) != 1: bad += 1; notes.append(f'mutant {mname}: its text is not in {html} once'); continue
        mp = os.path.join(tmp, 'mutant.html'); open(mp, 'w', encoding='utf-8').write(src_html.replace(a, b))
        mbad = disruptor_check(mp, tool, fit, G, tmp)[0]
        if mbad: caught.append(mname)
        else: bad += 1; notes.append(f'mutant {mname} NOT caught')
    dsum += f'; mutants caught {len(caught)} of {len(DIS_MUTANTS)}'
    for n in notes[:40]: print(n)
    print(dsum)
    print(f'{len(attackers)} attackers x {len(targets)} targets, {points} points ({changed} where pyfa changes speed or signature), {exact} bit-identical')
    print(f'{bad} mismatches (attacker inputs, targets and pairs vs pyfa calc/projected.py, grid of {len(GRID)}; disruptors vs pyfa Effect6423 / 6424 / 6694, grid of {len(DIS_GRID)})')
