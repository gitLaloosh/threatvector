"""Generate SELF_ACTIVE_EFFECTS (index.html, PYFA CORE section 'self-active').

    PYFA_SRC=/path/to/Pyfa python3 -I tools/gen_self_active_table.py [index.html]          # diff
    PYFA_SRC=/path/to/Pyfa python3 -I tools/gen_self_active_table.py [index.html] --write  # embed

Build queue 042, pyfa v2.70.1 (its 820d0d8, "drifter mod effects"): an ACTIVE effect that changes only the module's own
attribute, which that module's own passive effect then reads. The four 'Vigilant' Drifter modules:
  Effect13048 the Overdrive Injector's implantBonusVelocity x moduleAberrantOverdriveActiveSpeedBoostAmount (early), read by
    Effect2865 velocityBonusOnline (the ship's maxVelocity, penalized);
  Effect13049 the Shield Boost Amplifier's shieldBoostMultiplier x moduleAberrant...BonusEffect, read by Effect1720 (the shield
    boosters' shieldBonus, penalized);
  Effect13050 the Drone Navigation Computer's speedFactor x moduleAberrantDroneNavigationComputerBonusEffect (penalized), read
    by Effect6555 (drones' and fighters' maxVelocity, penalized);
  Effect13051 the Cap Recharger's capacitorRechargeRateMultiplier forced to ModuleAberrantCapacitorRechargeRatePostAssignment
    Hidden, read by Effect51 (the ship's rechargeRate).
Before 042 (pyfa v2.70.0) these effects changed the ship, the shield boosters and the drones directly.

  SELF_ACTIVE_EFFECTS {effectId: [[attrId, op, srcAttrId, penaltyGroup|null], ...]}
    op: 'mul' (multiplyItemAttr) or 'force' (forceItemAttr); penaltyGroup: the stacking group, or null.

The page (pyfaSelfActiveDogma) gives a module's ACTIVE copies their own attributes after these rows, and its other copies
the plain ones, wherever a passive effect of the module reads them (the capacitor and module-attribute tables, the speed
calculation, the drones' and fighters' attributes). One modifier on its own attribute, so a penalized one counts in full.

Asserted, so a pyfa change that breaks the model fails here instead of producing wrong numbers:
  * every such effect is 'active', makes only self.<multiply|force>ItemAttr(attr, <its own attribute>) calls, and every
    attribute it changes is read by a passive effect of each type that carries it;
  * no other pyfa effect (skill, hull, module) changes those attributes on those types, so the page may read the rest
    unmodified;
  * an active effect that changes only its own module but that no passive of the module reads is listed (not modelled:
    nothing on the page reads it) -- overheat effects are not 'active' and are skipped by the other generators.
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pyfa_effects import *

attrId = {v['name']: int(k) for k, v in attrs.items()}
OPS = {'multiplyItemAttr': 'mul', 'forceItemAttr': 'force'}
def etype(e):
    t = getattr(EFFECTS[e], 'type', None)
    return t if isinstance(t, tuple) else ((t,) if t else ())
def effs_of(t): return [e['effectID'] for e in td.get(str(t), {}).get('dogmaEffects', [])]

# Ported on their own (the page's own code), kept out of the table so nothing is applied twice:
PORTED = {7012: 'Assault Damage Control burst: forces its resonances, which Effect2302 reads; ported in the resist calc '
                '(ASSAULT_DAMAGE_CONTROL_EFFECT_ID, check_module_states.py)'}
carr = carriers()
problems, table, unread, ported = [], {}, [], []
for eid in sorted(e for e in EFFECTS if e in carr):
    if 'active' not in etype(eid): continue
    holders = [t for t in carr[eid] if cat(t) == 7]
    if not holders: continue
    calls, err = run(eid, 'module')
    if err or not calls or any(c[0] != 'self' for c in calls): continue
    rows, ok = [], True
    for coll, meth, a, kw in calls:
        m = re.fullmatch(r'a:(\w+)', repr(a[1])) if len(a) == 2 else None
        if meth not in OPS or not m or set(kw) - {'stackingPenalties', 'penaltyGroup'}:
            problems.append(f'effect {eid} {ename(eid)}: self.{meth}{a!r} {kw!r} (only self.multiply/forceItemAttr(attr, <own attribute>) expected)'); ok = False; break
        pg = str(kw.get('penaltyGroup', 'default')) if kw.get('stackingPenalties') else None
        rows.append([attrId[str(a[0])], OPS[meth], attrId[m.group(1)], pg])
    if not ok: continue
    names = {aname(r[0]) for r in rows}
    readBy = {}
    for t in holders:
        for pe in effs_of(t):
            if pe == eid or pe not in EFFECTS or 'passive' not in etype(pe): continue
            pc, perr = run(pe, 'module')
            if perr: continue
            for n in names:
                if any(f'a:{n}' in repr(x) for c in pc for x in c[2][1:]): readBy.setdefault(n, set()).add(pe)
    if eid in PORTED: ported.append(f'{eid} {ename(eid)}: {PORTED[eid]}'); continue
    if set(readBy) != names:
        if not readBy: unread.append(f'{eid} {ename(eid)}'); continue
        problems.append(f'effect {eid} {ename(eid)}: changes {sorted(names)} but its modules\' passives read only {sorted(readBy)}'); continue
    table[str(eid)] = rows
    print(f'  {eid} {ename(eid)}: ' + ', '.join(f'{aname(r[0])} {r[1]} {aname(r[2])}{" (" + r[3] + ")" if r[3] else ""}' for r in rows)
          + f'; read by {sorted(e for s in readBy.values() for e in s)}; carried by {sorted({name(t) for t in holders})[:3]}')

# Nothing else may change those attributes on those types.
selfAttrs = {}
for eid, rows in table.items():
    for t in carr[int(eid)]:
        for r in rows: selfAttrs.setdefault(aname(r[0]), set()).add(t)
CTX = {6: 'ship', 7: 'module', 32: 'module', 16: 'skill', 8: 'charge'}
for eid in sorted(e for e in EFFECTS if e in carr):
    if str(eid) in table: continue
    for c in sorted({cat(t) for t in carr[eid]} & set(CTX)):
        calls, err = run(eid, CTX[c], carrier=carr[eid][0])
        if err: continue
        for coll, meth, a, kw in calls:
            if coll == 'modules' and meth.startswith('filteredItem') and len(a) > 1 and str(a[1]) in selfAttrs:
                hits, _ = filter_hits(a[0], sorted(selfAttrs[str(a[1])]))
                if hits: problems.append(f'effect {eid} {ename(eid)} ({CTX[c]}): {meth} {a[1]} on {sorted({name(t) for t in hits})[:3]} (the page reads it unmodified)')
            if coll == 'self' and c == 7 and a and str(a[0]) in selfAttrs and set(carr[eid]) & selfAttrs[str(a[0])] and meth != 'getModifiedItemAttr':
                problems.append(f'effect {eid} {ename(eid)}: self.{meth} {a[0]} on a carrier of a self-active effect')

print(f'SELF_ACTIVE_EFFECTS: {len(table)} effects')
for x in ported: print('  ported separately:', x)
for u in unread: print('  not modelled (an active effect on its own module that none of its passives reads):', u)
for p in problems: print('PROBLEM', p)
if problems: sys.exit(f'gen_self_active_table: {len(problems)} problems')

html = next((x for x in sys.argv[1:] if not x.startswith('--')), os.path.join(os.path.dirname(__file__), '..', 'index.html'))
src = open(html, encoding='utf-8').read()
pat = re.compile(r'(const SELF_ACTIVE_EFFECTS = )(\{.*?\});\n', re.S)
m = pat.search(src)
blob = json.dumps(table, separators=(',', ':'))
if '--write' in sys.argv:
    if not m: sys.exit('SELF_ACTIVE_EFFECTS not found in ' + html)
    open(html, 'w', encoding='utf-8').write(src[:m.start(2)] + blob + src[m.end(2):]); print('wrote SELF_ACTIVE_EFFECTS into', html)
elif m: print('index.html table is up to date with this pyfa/SDE.' if json.loads(m.group(2)) == table else 'SELF_ACTIVE_EFFECTS vs index.html: DIFFERENT')
else: print('SELF_ACTIVE_EFFECTS not in index.html yet')
