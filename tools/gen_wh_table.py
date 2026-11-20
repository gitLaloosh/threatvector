"""Generate IT_WH_TYPE (index.html, build queue 044): where each wormhole type leads, read from CCP's SDE (pyfa's dump: the
"Wormhole" group's types and their wormholeTargetSystemClass attribute), for Intel's wormhole reports ("Z971→C1", "N110→HS").

    PYFA_SRC=/path/to/Pyfa python3 -I tools/gen_wh_table.py [index.html]          # diff
    PYFA_SRC=/path/to/Pyfa python3 -I tools/gen_wh_table.py [index.html] --write  # embed

IT_WH_TYPE {code: where}: 'c1'..'c6', 'c13', 'hs', 'ls', 'ns', 'th' (Thera), 'dr' (a Drifter system), 'po' (Pochven), '?' (no fixed
destination in the data: C729), 'exit' (K162, the far end of a hole opened from the other side; it has no target class).
The class numbers' meanings (7 highsec, 8 lowsec, 9 nullsec, 12 Thera, 13 shattered, 14-18 the Drifter systems, 25 Pochven) aren't in
the SDE's attributes; they agree with the EVE University wiki's table (https://wiki.eveuniversity.org/Wormhole_attributes, secondary
source, checked 2026-11-12) for every code both list. The QA test holes (classes 10 and 11) are left out.

IT_WH_LIFE {code: [lifetime in minutes, total mass, mass per jump, mass regained, in tonnes]} (build queue 061, D5: the static chip's
hover): attributes 1382 wormholeMaxStableTime, 1383 wormholeMaxStableMass, 1385 wormholeMaxJumpMass, 1384 wormholeMassRegeneration
(source: pyfa-org/Pyfa staticdata/fsd_built/ dogmaattributes and typedogma at the manifest's commit e5483f8, checked 2026-11-19).
CCP's record gives 1383-1385 unit 2 (kilograms), shown here in tonnes (kg / 1000, whole); 1382 unit 3, which CCP's record names
seconds, but its values are minutes (C247 960 = 16 h; UNVERIFIED, the 061 hand test). K162 has none (its numbers are the other end's).

IT_WH_EFF_MOD (build queue 062, E1): each J-space effect's numbers by its beacon's class (see the block above its table below).
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pyfa_sde import types, td, groups, attrs, _en

grp = [int(g) for g, v in groups.items() if _en(v.get('groupName')) == 'Wormhole']
assert len(grp) == 1, grp
att = [int(a) for a, v in attrs.items() if v.get('name') == 'wormholeTargetSystemClass']
assert att == [1381], att
CLASS = {1: 'c1', 2: 'c2', 3: 'c3', 4: 'c4', 5: 'c5', 6: 'c6', 7: 'hs', 8: 'ls', 9: 'ns', 12: 'th', 13: 'c13',
         14: 'dr', 15: 'dr', 16: 'dr', 17: 'dr', 18: 'dr', 25: 'po', -1: '?'}
SKIP = {10, 11}   # QA Wormhole A / B
table = {}
for t, v in types.items():
    if v.get('groupID') != grp[0]: continue
    nm = _en(v.get('typeName')) or ''
    m = re.fullmatch(r'Wormhole ([A-Z]\d{3})', nm)
    if not m: continue
    code = m.group(1)
    a = {x['attributeID']: x['value'] for x in td.get(str(t), {}).get('dogmaAttributes', [])}
    c = a.get(1381)
    if c is None:
        assert code == 'K162', (code, t)
        where = 'exit'
    else:
        c = int(c)
        if c in SKIP: continue
        assert c in CLASS, (code, c)
        where = CLASS[c]
    assert table.get(code, where) == where, (code, table.get(code), where)   # the same code in two types must lead to the same place
    table[code] = where
assert table.get('K162') == 'exit' and table.get('Z971') == 'c1' and table.get('N110') == 'hs', 'expected codes missing'
by = {}
for k, w in table.items(): by.setdefault(w, []).append(k)
for w in sorted(by): print(w, len(by[w]), ' '.join(sorted(by[w])))
# 061 (D5): lifetime and masses per code, from the same types (the same code in two types must agree)
LIFE_ATTR = {}
for a, v in attrs.items():
    if v.get('name') in ('wormholeMaxStableTime', 'wormholeMaxStableMass', 'wormholeMaxJumpMass', 'wormholeMassRegeneration'): LIFE_ATTR[v['name']] = int(a)
assert LIFE_ATTR == {'wormholeMaxStableTime': 1382, 'wormholeMaxStableMass': 1383, 'wormholeMassRegeneration': 1384, 'wormholeMaxJumpMass': 1385}, LIFE_ATTR
life = {}
for t, v in types.items():
    if v.get('groupID') != grp[0]: continue
    m = re.fullmatch(r'Wormhole ([A-Z]\d{3})', _en(v.get('typeName')) or '')
    if not m or m.group(1) == 'K162' or m.group(1) not in table: continue
    a = {x['attributeID']: x['value'] for x in td.get(str(t), {}).get('dogmaAttributes', [])}
    if a.get(1382) is None or a.get(1383) is None: continue
    row = [int(round(a.get(1382, 0)))] + [int(round(a.get(k, 0) / 1000)) for k in (1383, 1385, 1384)]
    assert life.get(m.group(1), row) == row, (m.group(1), life.get(m.group(1)), row)
    life[m.group(1)] = row
assert life.get('C247') == [960, 2000000, 375000, 0], life.get('C247')
print('lifetime and mass:', len(life), 'codes')
# 062 (E1, plan roadmap/wormholes-part4-plan.md section 5; the owner: "we need to add any affects that the hole has", Q12 "Name and numbers"):
# each J-space effect's numbers by its beacon's class, from CCP's 36 beacons "Class 1-6 <effect> Effects" (group 920 Effect Beacon; pyfa's copy of CCP's
# data at the manifest's commit). One line per modifying attribute, as a percent change: operation 4 (multiply) (v - 1) x 100; operation 6 (a percent
# added to a resonance, i.e. to the damage taken) v itself, the words saying "damage taken". The words are this table's (how each reads in the game's
# own info window is UNVERIFIED: the hand test). A beacon attribute with no words here stops the generator, so a new one is never shown silently.
# IT_WH_EFF_MOD {letter: {l: [words], c: {"1".."6": [percent, ...]}}}, letters as INTEL_WH.eff.
from pyfa_sde import effs
EFF_LETTER = {'Black Hole': 'b', 'Cataclysmic Variable': 'c', 'Magnetar': 'm', 'Pulsar': 'p', 'Red Giant': 'r', 'Wolf Rayet': 'w'}
EFF_WORDS = {   # modifying attribute -> words; the order is the order shown
    'shieldCapacityMultiplier': 'Shield HP', 'armorHPMultiplier': 'Armor HP',
    'armorEmDamageResistanceBonus': 'Armor damage taken', 'shieldEmDamageResistanceBonus': 'Shield damage taken',
    'signatureRadiusMultiplier': 'Signature radius', 'maxVelocityMultiplier': 'Ship max speed', 'agilityMultiplier': 'Inertia (align time)',
    'maxTargetRangeMultiplier': 'Targeting range', 'capacitorCapacityMultiplierSystem': 'Capacitor capacity', 'rechargeRateMultiplier': 'Capacitor recharge time',
    'damageMultiplierMultiplier': 'Turret, missile, drone and fighter damage', 'smallWeaponDamageMultiplier': 'Small turret, light missile and rocket damage',
    'trackingSpeedMultiplier': 'Turret and drone tracking', 'missileVelocityMultiplier': 'Missile velocity',
    'aoeVelocityMultiplier': 'Missile explosion velocity', 'aoeCloudSizeMultiplier': 'Missile explosion radius',
    'armorDamageAmountMultiplier': 'Local armor repair', 'shieldBonusMultiplier': 'Local shield boost',
    'armorDamageAmountMultiplierRemote': 'Remote armor repair', 'shieldBonusMultiplierRemote': 'Remote shield repair', 'energyTransferAmountBonus': 'Remote capacitor transfer',
    'energyWarfareStrengthMultiplier': 'Neutralizer and nosferatu amount', 'stasisWebStrengthMultiplier': 'Stasis web strength',
    'targetPainterStrengthMultiplier': 'Target painter strength', 'empFieldRangeMultiplier': 'Smartbomb range', 'smartbombDamageMultiplier': 'Smartbomb and bomb damage',
    'overloadBonusMultiplier': 'Overheat bonuses', 'heatDamageMultiplier': 'Overheat damage to modules'}
EFF_SAME = {'armorEmDamageResistanceBonus': ('armorExplosiveDamageResistanceBonus', 'armorKineticDamageResistanceBonus', 'armorThermalDamageResistanceBonus'),
            'shieldEmDamageResistanceBonus': ('shieldExplosiveDamageResistanceBonus', 'shieldKineticDamageResistanceBonus', 'shieldThermalDamageResistanceBonus')}   # one line: all four must agree
EFF_SKIP = {x for v in EFF_SAME.values() for x in v}
effmod = {}
for t, v in types.items():
    m = re.fullmatch(r'Class (\d) (.+) Effects', _en(v.get('typeName')) or '')
    if v.get('groupID') != 920 or not m or m.group(2) not in EFF_LETTER: continue
    d = td.get(str(t), {}); vals = {attrs[str(x['attributeID'])]['name']: x['value'] for x in d.get('dogmaAttributes', [])}
    ops = {}
    for e in d.get('dogmaEffects', []):
        for mi in effs[str(e['effectID'])].get('modifierInfo', []):
            k = attrs[str(mi['modifyingAttributeID'])]['name']; assert ops.get(k, mi['operation']) == mi['operation'], (k, 'two operations'); ops[k] = mi['operation']
    used = [k for k in EFF_WORDS if k in ops]
    assert all(k in EFF_WORDS or k in EFF_SKIP for k in ops), (m.group(0), 'no words for', [k for k in ops if k not in EFF_WORDS and k not in EFF_SKIP])
    for k, same in EFF_SAME.items():
        if k in ops: assert all(vals.get(x) == vals[k] for x in same), (m.group(0), k, 'the four resonances differ')
    row = []
    for k in used:
        op = ops[k]; assert op in (4, 6), (m.group(0), k, op)
        row.append(int(round((vals[k] - 1) * 100)) if op == 4 else int(round(vals[k])))
    e = effmod.setdefault(EFF_LETTER[m.group(2)], {'l': [EFF_WORDS[k] for k in used], 'c': {}})
    assert e['l'] == [EFF_WORDS[k] for k in used], (m.group(0), 'another set of lines than its other classes')
    e['c'][m.group(1)] = row
assert sorted(effmod) == sorted(EFF_LETTER.values()) and all(sorted(x['c']) == list('123456') for x in effmod.values()), 'expected 6 effects x 6 classes'
assert effmod['p']['c']['3'] == [58, 29, 58, -29, 58] and effmod['p']['l'][1] == 'Armor damage taken', effmod['p']   # Class 3 Pulsar (the plan's example)
effmod = {k: {'l': effmod[k]['l'], 'c': dict(sorted(effmod[k]['c'].items()))} for k in sorted(effmod)}
print('effects:', ', '.join(f"{k} {len(v['l'])} lines" for k, v in effmod.items()))
html = next((a for a in sys.argv[1:] if not a.startswith('--')), os.path.join(os.path.dirname(__file__), '..', 'index.html'))
src = open(html, encoding='utf-8').read()
new = 'const IT_WH_TYPE = ' + json.dumps(dict(sorted(table.items())), separators=(',', ':')) + ';'
new_life = 'const IT_WH_LIFE = ' + json.dumps(dict(sorted(life.items())), separators=(',', ':')) + ';'   # 061
new_eff = 'const IT_WH_EFF_MOD = ' + json.dumps(effmod, separators=(',', ':')) + ';'   # 062
EFF_RX = r'const IT_WH_EFF_MOD = \{.*?\}\}\};'
m = re.search(r'const IT_WH_TYPE = \{.*?\};', src); ml = re.search(r'const IT_WH_LIFE = \{.*?\};', src); me = re.search(EFF_RX, src)
state = [('IT_WH_TYPE', 'missing' if not m else 'same' if m.group(0) == new else 'CHANGED'), ('IT_WH_LIFE', 'missing' if not ml else 'same' if ml.group(0) == new_life else 'CHANGED'),
         ('IT_WH_EFF_MOD', 'missing' if not me else 'same' if me.group(0) == new_eff else 'CHANGED')]
if all(x == 'same' for _, x in state): print('index.html tables (IT_WH_TYPE, IT_WH_LIFE, IT_WH_EFF_MOD) are up to date with this SDE.')
else: print('vs index.html: ' + ', '.join(f'{k} {x}' for k, x in state if x != 'same'))
if '--write' in sys.argv:
    src, n = re.subn(r'const IT_WH_TYPE = \{.*?\};', lambda _: new, src, count=1)
    if n != 1: sys.exit('no IT_WH_TYPE line to replace (add a placeholder "const IT_WH_TYPE = {};" first)')
    if ml: src = re.sub(r'const IT_WH_LIFE = \{.*?\};', lambda _: new_life, src, count=1)
    else: src = re.sub(r'(const IT_WH_TYPE = \{.*?\};)', lambda x: x.group(1) + '\n' + new_life, src, count=1)
    if me: src = re.sub(EFF_RX, lambda _: new_eff, src, count=1)
    else: src = re.sub(r'(const IT_WH_LIFE = \{.*?\};)', lambda x: x.group(1) + '\n' + new_eff, src, count=1)
    open(html, 'w', encoding='utf-8', newline='\n').write(src)
    print('written')
