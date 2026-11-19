"""Data for the statics mockup: the real Wanderer statics (by system ID) and CCP's wormhole type attributes (pyfa's SDE dump)."""
import sys, json
sys.path.insert(0, '/home/claude/threatvector/tools')
from pyfa_sde import types, td, groups, attrs, _en
import re
g = [int(k) for k, v in groups.items() if _en(v.get('groupName')) == 'Wormhole'][0]
info = {}
for k, v in types.items():
    if v.get('groupID') != g: continue
    m = re.fullmatch(r'Wormhole ([A-Z]\d{3})', _en(v.get('typeName')) or '')
    if not m: continue
    a = {attrs[str(x['attributeID'])]['name']: x['value'] for x in td.get(k, {}).get('dogmaAttributes', [])}
    if 'wormholeMaxStableTime' not in a: continue
    r = [int(a['wormholeMaxStableTime']), int(a['wormholeMaxStableMass'] / 1000), int(a['wormholeMaxJumpMass'] / 1000), int(a.get('wormholeMassRegeneration', 0) / 1000)]
    if m.group(1) in info and info[m.group(1)] != r: print('differs', m.group(1), info[m.group(1)], r, file=sys.stderr)
    info.setdefault(m.group(1), r)
wd = json.load(open('/home/claude/ext/wanderer/priv/repo/data/wormholeSystems.json'))
st = {x['solarSystemID']: ' '.join(x['statics']) for x in wd}
codes = sorted({c for x in wd for c in x['statics']})
missing = [c for c in codes if c not in info]
print('types', len(info), 'static codes', len(codes), 'without attrs', missing, file=sys.stderr)
open(sys.argv[1], 'w').write('const MOCK_STATICS = ' + json.dumps(st, separators=(',', ':')) + ';\nconst MOCK_WHINFO = ' + json.dumps(dict(sorted(info.items())), separators=(',', ':')) + ';\n')
