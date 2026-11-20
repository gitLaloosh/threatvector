"""Wormholes tab part 4 mockup: the real page (index.html, main 995f6a0 / v2026.11.19.1) fed made-up Intel around C-J6MT and a made-up
wormhole chain, plus proto_rt.js (Project doc claude/roadmap/wormholes-part4-plan.md).
python3 -I build_rt.py <repo>/index.html <out.html>   (mock.js, data_rt.js, proto_rt.js, boot_rt.js beside this script)
mock.js: the repo's roadmap/paths-to-you-mockup/mock.js, unchanged. data_rt.js: gen_data_rt.py (CCP's effect beacons, pyfa e5483f8).
Everyone and every group is invented ("Mk ..." / "Mockup ..."); systems and ship types are EVE's public data."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(sys.argv[1], encoding='utf-8').read()
J = json.loads(re.search(r'const INTEL_JUMPS = (\{.*?\});', src).group(1))
NAMES = {30000772: 'C-J6MT', 30000773: '78-0R6', 30000780: 'RERZ-L', 30000779: 'SHBF-V', 30000781: '0UBC-R', 30000796: 'EUU-4N',
         30000543: '0TYR-T', 30000458: '9N-0HF', 30000771: '8G-2FP', 30000786: 'L5-UWT', 30000776: '4M-QXK', 30000774: 'MSG-BZ',
         30000788: 'I-1QKL', 30000784: 'YPW-M4', 30000736: 'KOG-TA', 30000764: '6BJH-3', 30000760: 'AGCP-I', 30000766: '1TG7-W',
         30000765: 'U-UTU9', 30000775: '8-WYQZ', 30000759: '7-JT09', 30000762: '5-2PQU', 30000803: 'MJ-LGH', 30000801: 'MOCW-2',
         30000770: '8BA-RA', 30000763: 'SN9-3Z', 30000758: 'I3CR-F', 30000757: '2JT-3Q', 30000756: '2-Q4YG', 30000802: 'Z0-4AR',
         30000142: 'Jita', 30002510: 'Rens', 30002813: 'Tama', 30002187: 'Amarr', 30004759: '1DQ1-A'}
CORP, ALLI, HC1, HALLI = 98100001, 99100001, 98100002, 99100002
ORGS = {CORP: ['corporation', 'Mockup Shipyards', 'MKSY', ALLI], ALLI: ['alliance', 'Mockup Coalition', 'MKCO', None],
        HC1: ['corporation', 'Mockup Raider Corp', 'MKRC', HALLI], HALLI: ['alliance', 'Mockup Raiders', 'MKRD', None]}
PIL = {95000001: ('Mk Your Main', CORP), 95000011: ('Mk Raider One', HC1), 95000012: ('Mk Raider Two', HC1)}
T = {'Sabre': (22456, 541), 'Muninn': (12015, 358)}
GROUPS = {541: 'Interdictor', 358: 'Heavy Assault Cruiser'}
REP = [(120, 'Mk Scout Alt', 'RERZ-L Mk Raider One Sabre'), (300, 'Mk Gate Watcher', 'SHBF-V Mk Raider Two Muninn')]
data = {'build': J['build'], 'homeName': 'C-J6MT', 'me': {'id': 95000001, 'name': 'Mk Your Main'},
        'names': {str(k): v for k, v in NAMES.items()},
        'orgs': {str(k): v for k, v in ORGS.items()}, 'byId': {str(k): [v[0], v[1]] for k, v in PIL.items()},
        'pilots': {v[0].lower(): k for k, v in PIL.items()},
        'types': {str(v[0]): [k, v[1]] for k, v in T.items()}, 'groups': {str(k): v for k, v in GROUPS.items()}, 'seq': 0, 'kills': {},
        'side': {'pilot': {'id': 95000001, 'name': 'Mk Your Main'}, 'corp': {'id': CORP, 'name': 'Mockup Shipyards'}, 'alliance': {'id': ALLI, 'name': 'Mockup Coalition'},
                 'friendly': [], 'hostile': [{'id': HALLI, 'name': 'Mockup Raiders', 'kind': 'alliance'}], 'rows': 15},
        'intel': {'channels': ['region.intel'], 'me': 95000001, 'range': 3, 'nearRange': 6, 'mapReach': 12, 'killRange': 10, 'forget': 30, 'sound': False, 'notify': False, 'nearShown': False},
        'reports': sorted(REP, reverse=True)}
CSP = '<meta http-equiv="Content-Security-Policy" content="img-src data: blob:; connect-src \'none\'; font-src data:; media-src data: blob:">'
s = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', CSP, src, count=1)
# two hooks in whDraw (each found exactly once): the route's glow under the connection lines; outlines and the EXIT pill over the boxes
PATCH = [
    ("  const ctr = (n) => { const p = M.P.get(n); return {x: p.x + WH_NW / 2, y: p.y + WH_NH / 2}; };\n  for(const l of st.links){",
     "  const ctr = (n) => { const p = M.P.get(n); return {x: p.x + WH_NW / 2, y: p.y + WH_NH / 2}; };\n  if(window.__RTglow) window.__RTglow(c, ctr, C);\n  for(const l of st.links){"),
    ("  c.setTransform(dpr, 0, 0, dpr, 0, 0);\n  whEndMarks(c, C, dpr, w, h);",
     "  if(window.__RTover) window.__RTover(c, C, font);\n  c.setTransform(dpr, 0, 0, dpr, 0, 0);\n  whEndMarks(c, C, dpr, w, h);"),
]
for a, b in PATCH:
    assert s.count(a) == 1, ('hook not found once', a[:60])
    s = s.replace(a, b)
rd = lambda n: open(os.path.join(HERE, n), encoding='utf-8').read()
mock = rd('mock.js').replace('__MKDATA__', json.dumps(data, separators=(',', ':'), ensure_ascii=False))
i = s.index('>', s.index('<head')) + 1
s = s[:i] + '<script>' + mock + '</script>' + s[i:]
s = s.replace('<title>', '<title>MOCKUP · Wormholes part 4 · ', 1)
j = s.rindex('</body>')
s = s[:j] + '<script>' + rd('data_rt.js') + '\n' + rd('proto_rt.js') + '</script><script>' + rd('boot_rt.js') + '</script>' + s[j:]
open(sys.argv[2], 'w', encoding='utf-8').write(s)
print('built', sys.argv[2], len(s))
