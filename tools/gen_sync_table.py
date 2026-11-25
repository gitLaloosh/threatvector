"""Generate SYNC_RIG_EFFECTS and SYNC_WRITER_EFFECTS (index.html, PYFA CORE section 'synchronizer-rigs').

    PYFA_SRC=/path/to/Pyfa python3 -I tools/gen_sync_table.py [index.html]          # diff
    PYFA_SRC=/path/to/Pyfa python3 -I tools/gen_sync_table.py [index.html] --write  # embed

Build queue 042, pyfa v2.70.1 (its a2c7b8e and 41b0629; build queue 035 had v2.70.0's model). A Synchronizer rig (group
'Rig Synchronizer') grows with the matching faction modules fitted, in two steps:
  * each faction module's own effect (Effect12963 Imperial Navy ..., type 'offline', runTime 'earliest') adds its
    rigSet...Module value (1) to the rigSet...Bonus attribute of every fitted Synchronizer rig. 'offline' effects run in
    every state, so an offline module counts. A mutated module is its abyssal type in pyfa (mutatedMixin._mutaInit),
    which carries no such effect, so it never counts;
  * the rig's counting effect (Effect13012 Dread Guristas ..., runTime 'early') reads its OWN rigSet...Bonus and raises
    its own attributes by it (+1 or -1 each, increaseItemAttr, position 'pre': added to the base value); the rig's
    ordinary effects then read the raised values.
A value counted over the fit is not 'attribute op value', so the generic generators skip these (pyfa_effects.sync_effects)
and these tables carry them:

  SYNC_WRITER_EFFECTS {effectId: [bonusAttrId, moduleAttrId]}
    bonusAttrId: the rig's rigSet...Bonus the module's effect adds to; moduleAttrId: the module's rigSet...Module it adds.
  SYNC_RIG_EFFECTS {effectId: [bonusAttrId, [[rigAttrId, sign, defaultValue], ...]]}
    bonusAttrId: the rigSet...Bonus the rig reads off itself; sign: +1 or -1 (increaseItemAttr(attr, +/-bonus)).

The page (pyfaSyncRigTypes) makes, for this fit only, a copy of each Synchronizer rig's type: its bonus = its own value
plus, for every fitted module copy whose type carries a writer for that bonus, the module's rigSet...Module (a pasted
module marked mutated left out), then each attribute raised by sign x bonus.

Asserted, so a pyfa change that breaks the model fails here instead of producing wrong numbers:
  * no handler sums over fit.modules any more (pyfa_effects.counting_effects: v2.70.0's shape);
  * every writer is 'offline', runs 'earliest', makes exactly one fit.modules.filteredItemIncrease(filter, bonus,
    <its own rigSet...Module>) with no keyword, its filter accepts exactly the 'Rig Synchronizer' types, and no
    Synchronizer, abyssal or mutated type carries it;
  * every rig effect runs 'early', is carried only by 'Rig Synchronizer' types, reads one rigSet...Bonus, and makes only
    self.increaseItemAttr(attr, +/-bonus) calls with no keyword; every rig bonus has a writer and every writer a rig;
  * nothing else in pyfa writes a rigSet...Bonus or rigSet...Module attribute (so the page may read them unmodified).
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pyfa_effects import *

attrId = {v['name']: int(k) for k, v in attrs.items()}
DEFAULT = {v['name']: v.get('defaultValue', 0.0) for v in attrs.values()}
GROUP = 'Rig Synchronizer'
BONUS_RX, MODULE_RX = re.compile(r'rigSet\w+Bonus'), re.compile(r'rigSet\w+Module')

def etype(e):
    t = getattr(EFFECTS[e], 'type', None)
    return t if isinstance(t, tuple) else ((t,) if t else ())

carr = carriers()
pool = sorted(e for e in EFFECTS if e in carr)
problems, rigs, writers = [], {}, {}

old = counting_effects(pool)
for eid in old: problems.append(f'effect {eid} {ename(eid)}: sums an attribute over fit.modules -- pyfa v2.70.0\'s Synchronizer shape is back: rebuild this table')

found = sync_effects(pool)
syncTypes = sorted(int(t) for t, v in types.items() if v.get('published') and gname(t) == GROUP)
modulePool = sorted(int(t) for t, v in types.items() if v.get('published') and cat(t) == 7)

for eid, w in sorted(found['writers'].items()):
    calls, _ = run(eid, 'module')
    if len(calls) != 1: problems.append(f'writer {eid}: {len(calls)} calls (one filteredItemIncrease expected)')
    m = re.fullmatch(r'a:(rigSet\w+Module)', w['value'])
    if not m: problems.append(f'writer {eid}: adds {w["value"]} (its own rigSet...Module expected)'); continue
    if w['kw']: problems.append(f'writer {eid}: keywords {w["kw"]!r} (none expected)')
    if 'offline' not in etype(eid): problems.append(f'writer {eid}: type {etype(eid)} (offline expected: pyfa runs it in every state)')
    if getattr(EFFECTS[eid], 'runTime', None) != 'earliest': problems.append(f'writer {eid}: runTime {getattr(EFFECTS[eid], "runTime", None)!r} (earliest expected)')
    hits, _ = filter_hits(w['filter'], modulePool)
    if sorted(hits) != syncTypes: problems.append(f'writer {eid}: its filter accepts {len(hits)} types, not exactly the {len(syncTypes)} {GROUP!r} types')
    holders = carr.get(eid, [])
    bad = sorted({name(t) for t in holders if gname(t) == GROUP or 'abyssal' in (name(t) or '').lower() or 'mutated' in (name(t) or '').lower()})
    if bad: problems.append(f'writer {eid}: carried by {bad[:4]} (a faction module expected; a mutated module is its abyssal type in pyfa)')
    writers[str(eid)] = [attrId[w['bonus']], attrId[m.group(1)]]

for eid, r in sorted(found['rigs'].items()):
    if len(r['bonus']) != 1: problems.append(f'rig effect {eid}: reads {r["bonus"]} (one rigSet...Bonus expected)'); continue
    bonus = r['bonus'][0]
    if getattr(EFFECTS[eid], 'runTime', None) != 'early': problems.append(f'rig effect {eid}: runTime {getattr(EFFECTS[eid], "runTime", None)!r} (early expected)')
    holders = carr.get(eid, [])
    if not holders or any(gname(t) != GROUP for t in holders): problems.append(f'rig effect {eid}: carried by {sorted({gname(t) for t in holders})} (only {GROUP!r} expected)')
    rows = []
    for coll, meth, a, kw in r['calls']:
        if coll != 'self' or meth != 'increaseItemAttr' or len(a) != 2 or kw: problems.append(f'rig effect {eid}: {coll}.{meth}{a!r} {kw!r} (only self.increaseItemAttr(attr, +/-bonus) expected)'); continue
        v = repr(a[1])
        sign = 1 if v == f'a:{bonus}' else -1 if v == f'(-a:{bonus})' else None
        if sign is None: problems.append(f'rig effect {eid}: {a[0]} raised by {v} (+/-a:{bonus} expected)'); continue
        rows.append([attrId[str(a[0])], sign, DEFAULT.get(str(a[0]), 0.0)])
    if not rows: problems.append(f'rig effect {eid}: no rows')
    rigs[str(eid)] = [attrId[bonus], rows]

wb, rb = {w[0] for w in writers.values()}, {r[0] for r in rigs.values()}
for b in sorted(rb - wb): problems.append(f'{aname(b)}: read by a rig, written by no faction module')
for b in sorted(wb - rb): problems.append(f'{aname(b)}: written by faction modules, read by no rig')

# Nothing else may write a rigSet...Bonus or rigSet...Module attribute.
for eid in sorted(e for e in EFFECTS if e in carr):
    if str(eid) in writers: continue
    for ctx in ('module', 'ship', 'skill', 'charge'):
        calls, err = run(eid, ctx)
        if err: continue
        for coll, meth, a, kw in calls:
            tgt = str(a[1]) if coll in ('modules', 'drones', 'fighters', 'charges') and len(a) > 1 else (str(a[0]) if a else '')
            if (BONUS_RX.fullmatch(tgt) or MODULE_RX.fullmatch(tgt)) and meth != 'getModifiedItemAttr':
                problems.append(f'effect {eid} {ename(eid)} ({ctx}): {coll}.{meth} writes {tgt} (only the faction modules\' own effects may)')
        break

print(f'SYNC_WRITER_EFFECTS: {len(writers)} faction-module effects; SYNC_RIG_EFFECTS: {len(rigs)} rig effects')
for e, (b, ma) in writers.items(): print(f'  writer {e} {ename(int(e))}: + {aname(ma)} -> every Synchronizer\'s {aname(b)} (any state)')
for e, (b, rows) in rigs.items():
    print(f'  rig {e} {ename(int(e))}: reads {aname(b)}; ' + ', '.join(f'{aname(a)} {"+" if s > 0 else "-"}bonus' for a, s, _ in rows))
for p in problems: print('PROBLEM', p)
if problems: sys.exit(f'gen_sync_table: {len(problems)} problems')

html = next((x for x in sys.argv[1:] if not x.startswith('--')), os.path.join(os.path.dirname(__file__), '..', 'index.html'))
src = open(html, encoding='utf-8').read()
ok = True
for tname, data in (('SYNC_RIG_EFFECTS', rigs), ('SYNC_WRITER_EFFECTS', writers)):
    pat = re.compile(r'(const ' + tname + r' = )(\{.*?\});\n', re.S)
    m = pat.search(src)
    blob = json.dumps(data, separators=(',', ':'))
    if '--write' in sys.argv:
        if not m: sys.exit(tname + ' not found in ' + html)
        src = src[:m.start(2)] + blob + src[m.end(2):]; print('wrote', tname)
    elif not m: print(tname, 'not in index.html yet'); ok = False
    elif json.loads(m.group(2)) != data: print(tname, 'vs index.html: DIFFERENT'); ok = False
if '--write' in sys.argv: open(html, 'w', encoding='utf-8').write(src); print('into', html)
elif ok: print('index.html tables are up to date with this pyfa/SDE.')
