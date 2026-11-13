"""Generate IT_WH_TYPE (index.html, build queue 044): where each wormhole type leads, read from CCP's SDE (pyfa's dump: the
"Wormhole" group's types and their wormholeTargetSystemClass attribute), for Intel's wormhole reports ("Z971→C1", "N110→HS").

    PYFA_SRC=/path/to/Pyfa python3 -I tools/gen_wh_table.py [index.html]          # diff
    PYFA_SRC=/path/to/Pyfa python3 -I tools/gen_wh_table.py [index.html] --write  # embed

IT_WH_TYPE {code: where}: 'c1'..'c6', 'c13', 'hs', 'ls', 'ns', 'th' (Thera), 'dr' (a Drifter system), 'po' (Pochven), '?' (no fixed
destination in the data: C729), 'exit' (K162, the far end of a hole opened from the other side; it has no target class).
The class numbers' meanings (7 highsec, 8 lowsec, 9 nullsec, 12 Thera, 13 shattered, 14-18 the Drifter systems, 25 Pochven) aren't in
the SDE's attributes; they agree with the EVE University wiki's table (https://wiki.eveuniversity.org/Wormhole_attributes, secondary
source, checked 2026-11-12) for every code both list. The QA test holes (classes 10 and 11) are left out.
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
html = next((a for a in sys.argv[1:] if not a.startswith('--')), os.path.join(os.path.dirname(__file__), '..', 'index.html'))
src = open(html, encoding='utf-8').read()
new = 'const IT_WH_TYPE = ' + json.dumps(dict(sorted(table.items())), separators=(',', ':')) + ';'
m = re.search(r'const IT_WH_TYPE = \{.*?\};', src)
if m:
    print('index.html table is up to date with this SDE.' if m.group(0) == new else 'vs index.html: CHANGED')
else:
    print('index.html has no IT_WH_TYPE yet')
if '--write' in sys.argv:
    src, n = re.subn(r'const IT_WH_TYPE = \{.*?\};', lambda _: new, src, count=1)
    if n != 1: sys.exit('no IT_WH_TYPE line to replace (add a placeholder "const IT_WH_TYPE = {};" first)')
    open(html, 'w', encoding='utf-8', newline='\n').write(src)
    print('written')
