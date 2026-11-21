"""Writes data_rt.js for the part 4 mockup: each wormhole effect's numbers per class, from CCP's effect beacons ("Class N <effect> Effects",
group 920) as pyfa ships CCP's data (staticdata/fsd_built at the manifest's commit e5483f8, v2.70.0).

    PYFA_SRC=/path/to/Pyfa python3 -I gen_data_rt.py data_rt.js

One line per modifying attribute (the words are this mockup's draft; the build checks them against the game's info window).
Operation 4 multiplies: shown as the change, +58% / -29%. Operation 6 adds a percent to a resonance (damage taken): shown as
"damage taken +29% (resists worse)"."""
import json, glob, os, re, sys
P = os.environ['PYFA_SRC']
L = lambda pat: {k: v for f in sorted(glob.glob(os.path.join(P, 'staticdata/fsd_built', pat))) for k, v in json.load(open(f, encoding='utf-8')).items()}
types, td = L('types.*.json'), L('typedogma.*.json')
A = json.load(open(os.path.join(P, 'staticdata/fsd_built/dogmaattributes.0.json'), encoding='utf-8'))
E = json.load(open(os.path.join(P, 'staticdata/fsd_built/dogmaeffects.0.json'), encoding='utf-8'))
WORDS = {   # modifying attribute -> the line's words (one line even where CCP's effect touches several attributes)
    'shieldCapacityMultiplier': 'Shield HP', 'armorHPMultiplier': 'Armor HP', 'signatureRadiusMultiplier': 'Signature radius',
    'armorEmDamageResistanceBonus': 'Armor resists', 'shieldEmDamageResistanceBonus': 'Shield resists',
    'rechargeRateMultiplier': 'Capacitor recharge time', 'capacitorCapacityMultiplierSystem': 'Capacitor capacity',
    'energyWarfareStrengthMultiplier': 'Neut and nos strength', 'maxTargetRangeMultiplier': 'Targeting range',
    'missileVelocityMultiplier': 'Missile velocity', 'maxVelocityMultiplier': 'Ship speed', 'aoeVelocityMultiplier': 'Missile explosion velocity',
    'agilityMultiplier': 'Inertia (align time)', 'stasisWebStrengthMultiplier': 'Stasis web strength',
    'armorDamageAmountMultiplier': 'Local armor repair', 'armorDamageAmountMultiplierRemote': 'Remote armor repair',
    'shieldBonusMultiplier': 'Local shield boost', 'shieldBonusMultiplierRemote': 'Remote shield repair',
    'energyTransferAmountBonus': 'Remote capacitor transfer', 'damageMultiplierMultiplier': 'Turret, missile and drone damage',
    'trackingSpeedMultiplier': 'Turret and drone tracking', 'aoeCloudSizeMultiplier': 'Missile explosion radius',
    'targetPainterStrengthMultiplier': 'Target painter strength', 'heatDamageMultiplier': 'Overheat damage to modules',
    'overloadBonusMultiplier': 'Overheat bonus', 'empFieldRangeMultiplier': 'Smartbomb range', 'smartbombDamageMultiplier': 'Smartbomb damage',
    'smallWeaponDamageMultiplier': 'Small weapon damage'}
SKIP = {'armorExplosiveDamageResistanceBonus', 'armorKineticDamageResistanceBonus', 'armorThermalDamageResistanceBonus',   # same line as EM
        'shieldExplosiveDamageResistanceBonus', 'shieldKineticDamageResistanceBonus', 'shieldThermalDamageResistanceBonus'}
EFF = {'Black Hole': 'b', 'Cataclysmic Variable': 'c', 'Magnetar': 'm', 'Pulsar': 'p', 'Red Giant': 'r', 'Wolf Rayet': 'w'}
out = {}
for tid, t in types.items():
    m = re.match(r'Class (\d) (.+) Effects$', (t.get('typeName') or {}).get('en-us', ''))
    if t.get('groupID') != 920 or not m or m.group(2) not in EFF: continue
    d = td[tid]; vals = {A[str(a['attributeID'])]['name']: a['value'] for a in d.get('dogmaAttributes', [])}
    ops = {}
    for e in d.get('dogmaEffects', []):
        for mi in E[str(e['effectID'])].get('modifierInfo', []): ops.setdefault(A[str(mi['modifyingAttributeID'])]['name'], mi['operation'])
    lines = []
    for k, v in vals.items():
        if k in SKIP or k not in ops: continue
        assert k in WORDS, ('no words for', k)
        op = ops[k]
        if op == 6: lines.append([WORDS[k], f'damage taken +{v:g}% (resists worse)'])
        elif op == 4: p = round((v - 1) * 100); lines.append([WORDS[k], f'{"+" if p > 0 else "−"}{abs(p)}%'])
        else: raise SystemExit(f'operation {op} for {k}')
    out.setdefault(EFF[m.group(2)], {})[m.group(1)] = lines
assert all(len(v) == 6 for v in out.values()) and len(out) == 6, 'expected 6 effects x 6 classes'
open(sys.argv[1], 'w', encoding='utf-8').write('const MOCK_EFF = ' + json.dumps(out, ensure_ascii=False) + ';\n')
print('wrote', sys.argv[1], sum(len(x) for v in out.values() for x in v.values()), 'lines')
