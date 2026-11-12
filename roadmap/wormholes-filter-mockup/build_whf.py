"""Wormholes filter mockup (wormhole mapping phase 1): the real page (index.html, main 1e22ec7) with made-up Intel around C-J6MT, plus proto_whf.js.
python3 -I build_whf.py <repo>/index.html <out.html>   (mock.js, proto_whf.js, boot_wh.js beside this script)
Far systems (Jita, Amarr, Tama, 1DQ1-A, Amamake): ids checked against the page's own map table (regions The Forge, Domain, The Citadel, Delve, Heimatar).
Systems: k-space names from ref-data.everef.net (checked 2026-11-11, as the map-look mockup); wormhole systems are made up (J99xxxx,
past the real J-names). Everyone and every group is invented ("Mk ..." / "Mockup ...")."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(sys.argv[1], encoding='utf-8').read()
J = json.loads(re.search(r'const INTEL_JUMPS = (\{.*?\});', src).group(1))
NAMES = {30000772: 'C-J6MT', 30000773: '78-0R6', 30000780: 'RERZ-L', 30000779: 'SHBF-V', 30000781: '0UBC-R', 30000796: 'EUU-4N',
         30000543: '0TYR-T', 30000458: '9N-0HF', 30000771: '8G-2FP', 30000786: 'L5-UWT', 30000776: '4M-QXK', 30000774: 'MSG-BZ',
         30000788: 'I-1QKL', 30000784: 'YPW-M4', 30000775: '8-WYQZ', 30000778: 'G-EURJ', 30000782: '3U-48K',
         30000142: 'Jita', 30002187: 'Amarr', 30002813: 'Tama', 30004759: '1DQ1-A', 30002537: 'Amamake'}
CORP, ALLI, HC1, HALLI = 98100001, 99100001, 98100002, 99100002
ORGS = {CORP: ['corporation', 'Mockup Shipyards', 'MKSY', ALLI], ALLI: ['alliance', 'Mockup Coalition', 'MKCO', None],
        HC1: ['corporation', 'Mockup Raider Corp', 'MKRC', HALLI], HALLI: ['alliance', 'Mockup Raiders', 'MKRD', None]}
PIL = {95000001: ('Mk Your Main', CORP), 95000011: ('Mk Raider One', HC1), 95000012: ('Mk Raider Two', HC1)}
T = {'Sabre': (22456, 541), 'Muninn': (12015, 358)}
GROUPS = {541: 'Interdictor', 358: 'Heavy Assault Cruiser'}
REP = [(40, 'Mk Gate Watcher', '78-0R6 Mk Raider One Sabre'),
       (300, 'Mk Scout Alt', 'RERZ-L wh on the sun'),
       (520, 'Mk Gate Watcher', 'EUU-4N drifter hole spotted'),
       (700, 'Mk Scout Alt', 'SHBF-V Mk Raider Two Muninn')]
data = {'build': J['build'], 'homeName': 'C-J6MT', 'me': {'id': 95000001, 'name': 'Mk Your Main'},
        'names': {str(k): v for k, v in NAMES.items()},
        'orgs': {str(k): v for k, v in ORGS.items()}, 'byId': {str(k): [v[0], v[1]] for k, v in PIL.items()},
        'pilots': {v[0].lower(): k for k, v in PIL.items()},
        'types': {str(v[0]): [k, v[1]] for k, v in T.items()}, 'groups': {str(k): v for k, v in GROUPS.items()}, 'seq': 70000,
        'side': {'pilot': {'id': 95000001, 'name': 'Mk Your Main'}, 'corp': {'id': CORP, 'name': 'Mockup Shipyards'}, 'alliance': {'id': ALLI, 'name': 'Mockup Coalition'},
                 'friendly': [], 'hostile': [{'id': HALLI, 'name': 'Mockup Raiders', 'kind': 'alliance'}], 'rows': 15},
        'intel': {'channels': ['region.intel'], 'me': 95000001, 'range': 3, 'nearRange': 6, 'mapReach': 10, 'killRange': 10, 'forget': 30, 'sound': False, 'notify': False},
        'reports': sorted(REP, reverse=True)}
CSP = '<meta http-equiv="Content-Security-Policy" content="img-src data: blob:; connect-src \'none\'; font-src data:; media-src data: blob:">'
s = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', CSP, src, count=1)
rd = lambda n: open(os.path.join(HERE, n), encoding='utf-8').read()
mock = rd('mock.js').replace('__MKDATA__', json.dumps(data, separators=(',', ':'), ensure_ascii=False))
i = s.index('>', s.index('<head')) + 1
s = s[:i] + '<script>' + mock + '</script>' + s[i:]
j = s.rindex('</body>')
s = s[:j] + '<script>' + rd('proto_whf.js') + '</script><script>' + rd('boot_wh.js') + '</script>' + s[j:]
open(sys.argv[2], 'w', encoding='utf-8').write(s)
print('built', sys.argv[2], len(s))
