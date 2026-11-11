"""Generate SYNC_RIG_EFFECTS (index.html, PYFA CORE section 'synchronizer-rigs', build queue 035, pyfa v2.70.0).

    PYFA_SRC=/path/to/Pyfa python3 -I tools/gen_sync_table.py [index.html]          # diff
    PYFA_SRC=/path/to/Pyfa python3 -I tools/gen_sync_table.py [index.html] --write  # embed

pyfa v2.70.0's Synchronizer rigs (group 'Rig Synchronizer') grow with the number of matching faction modules fitted:
one 'early' handler per rig line (e.g. Effect13012, Dread Guristas) sums a counter attribute over the fit's modules in
the states it counts, then raises the rig's OWN attributes by that count (+1 or -1 each); the rig's ordinary effects
then read the raised values. The value is a count over the whole fit, which the generic generators (attribute op
value) can't express, so they skip these effects (pyfa_effects.counting_effects) and this table carries them:

  SYNC_RIG_EFFECTS {effectId: [counterAttrId, minState, [[rigAttrId, sign, defaultValue], ...]]}
    counterAttrId: the attribute summed over fitted modules (pyfa reads it modified; nothing in pyfa modifies it);
    minState: the lowest pyfa FittingModuleState counted (-1 offline, 0 online, 1 active), from running the handler
      with a probe module in each state (pyfa_effects.counting_effects);
    sign: +1 or -1, from the handler's increaseItemAttr(attr, count) / (attr, -count).

The page (pyfaSyncRigTypes) applies them before anything reads the rig: a copy of the rig's type for this fit only,
each attribute raised by sign x count (pyfa's increaseItemAttr, position 'pre': added to the base value).

Asserted, so a pyfa change that breaks the model fails here instead of producing wrong numbers:
  * every counting effect reads exactly one counter, counts an upper set of states, makes only
    self.increaseItemAttr(attr, +/-count) calls with no other keyword, runs 'early' and is carried only by
    'Rig Synchronizer' types;
  * no pyfa effect READS a rigSet...Bonus attribute (v2.70.0's faction modules write them onto the rigs, Effect12963
    ..., and nothing reads them; pyfa's master after v2.70.0, a2c7b8e, counts through them instead).
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pyfa_effects import *

attrId = {v['name']: int(k) for k, v in attrs.items()}
DEFAULT = {v['name']: v.get('defaultValue', 0.0) for v in attrs.values()}
GROUP = 'Rig Synchronizer'
S = module_states()

carr = carriers()
found = counting_effects(sorted(e for e in EFFECTS if e in carr))
problems, table, writers = [], {}, []
for eid, v in sorted(found.items()):
    if len(v['counter']) != 1: problems.append(f'effect {eid}: reads {v["counter"]} off the fit\'s modules (one counter expected)'); continue
    counter = v['counter'][0]
    st = v['states']
    if not st or st != [int(s) for s in S if int(s) >= st[0]]: problems.append(f'effect {eid}: counts states {st} (an upper set expected)'); continue
    if getattr(EFFECTS[eid], 'runTime', None) != 'early': problems.append(f'effect {eid}: runTime {getattr(EFFECTS[eid], "runTime", None)!r} (early expected)')
    holders = carr.get(eid, [])
    if not holders or any(gname(t) != GROUP for t in holders): problems.append(f'effect {eid}: carried by {sorted({gname(t) for t in holders})} (only {GROUP!r} expected)')
    cnt = f'(0+m:{counter})'
    rows = []
    for coll, meth, a, kw in v['calls']:
        if coll != 'self' or meth != 'increaseItemAttr' or len(a) != 2 or kw: problems.append(f'effect {eid}: {coll}.{meth}{a!r} {kw!r} (only self.increaseItemAttr(attr, +/-count) expected)'); continue
        r = repr(a[1])
        sign = 1 if r == cnt else -1 if r == f'(-{cnt})' else None
        if sign is None: problems.append(f'effect {eid}: {a[0]} raised by {r} (+/-{cnt} expected)'); continue
        rows.append([attrId[str(a[0])], sign, DEFAULT.get(str(a[0]), 0.0)])
    if not rows: problems.append(f'effect {eid}: no rows')
    table[str(eid)] = [attrId[counter], st[0], rows]

# Nobody may read a rigSet...Bonus attribute (pyfa v2.70.0 writes them and never reads them).
for eid in sorted(e for e in EFFECTS if e in carr):
    for ctx in ('module', 'ship', 'skill'):
        calls, err = run(eid, ctx)
        if err: continue
        txt = repr(calls)
        if re.search(r"a:rigSet\w+Bonus", txt): problems.append(f'effect {eid} ({ctx}): reads a rigSet...Bonus attribute -- pyfa now counts through them (its master a2c7b8e): rebuild this table from those effects')
        for coll, meth, a, kw in calls:
            if coll == 'modules' and meth == 'filteredItemIncrease' and len(a) > 1 and re.fullmatch(r'rigSet\w+Bonus', str(a[1])):
                if eid not in writers: writers.append(eid)
        break

print(f'SYNC_RIG_EFFECTS: {len(table)} counting effects (pyfa {"/".join(sorted({str(len(x[2])) for x in table.values()}))} rows each)')
for e, (c, m, rows) in table.items():
    print(f'  {e} {ename(int(e))}: counts {aname(c)} at state >= {S(m).name}; ' + ', '.join(f'{aname(a)} {"+" if s > 0 else "-"}count' for a, s, _ in rows))
print(f'  not modelled, by design: {len(writers)} faction-module effects write a rigSet...Bonus attribute that no pyfa effect reads: {writers}')
for p in problems: print('PROBLEM', p)
if problems: sys.exit(f'gen_sync_table: {len(problems)} problems')

html = next((x for x in sys.argv[1:] if not x.startswith('--')), os.path.join(os.path.dirname(__file__), '..', 'index.html'))
src = open(html, encoding='utf-8').read()
pat = re.compile(r'(const SYNC_RIG_EFFECTS = )(\{.*?\});\n', re.S)
m = pat.search(src)
blob = json.dumps(table, separators=(',', ':'))
if '--write' in sys.argv:
    if not m: sys.exit('SYNC_RIG_EFFECTS not found in ' + html)
    open(html, 'w', encoding='utf-8').write(src[:m.start(2)] + blob + src[m.end(2):]); print('wrote SYNC_RIG_EFFECTS into', html)
elif m:
    print('index.html table is up to date with this pyfa/SDE.' if json.loads(m.group(2)) == table else 'SYNC_RIG_EFFECTS vs index.html: DIFFERENT')
else: print('SYNC_RIG_EFFECTS not in index.html yet')
