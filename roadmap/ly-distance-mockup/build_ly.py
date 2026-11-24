"""Distance in light years on the Intel map (Project doc claude/roadmap/ly-distance-plan.md; research claude/roadmap/intel-later-filters-research.md
E1, answered 2026-11-20): the real page (index.html, main e72ba18 / v2026.11.20.2) fed made-up Intel around C-J6MT, plus proto_ly.js: 058's
"Within N jumps" becomes "Distance" with a Jumps / Light years switch in its settings, a typed LY with quick picks from CCP's jump ranges,
systems a jump drive can't land in (high-sec, Pochven, Zarzakh) left out.
python3 -I build_ly.py <repo>/index.html <out.html>   (mock.js, proto_ly.js, boot_ly.js beside this script)
mock.js: the repo's roadmap/paths-to-you-mockup/mock.js, unchanged. System names: the map-look mockup's list (ref-data.everef.net,
checked 2026-11-11). Every pilot, corporation and alliance is invented ("Mk ..." / "Mockup ...").
Build queue 067 (2026-11-24): rebuilt from main aa55779 (v2026.11.23.3, before 067) for the repo; mock.js read from ../paths-to-you-mockup/
when it isn't beside this script."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(sys.argv[1], encoding='utf-8').read()
J = json.loads(re.search(r'const INTEL_JUMPS = (\{.*?\});', src).group(1))
NAMES = {30000772: 'C-J6MT', 30000773: '78-0R6', 30000780: 'RERZ-L', 30000779: 'SHBF-V', 30000781: '0UBC-R', 30000796: 'EUU-4N',
         30000543: '0TYR-T', 30000458: '9N-0HF', 30000771: '8G-2FP', 30000786: 'L5-UWT', 30000776: '4M-QXK', 30000774: 'MSG-BZ',
         30000788: 'I-1QKL', 30000784: 'YPW-M4', 30000736: 'KOG-TA', 30000764: '6BJH-3', 30000760: 'AGCP-I', 30000766: '1TG7-W',
         30000765: 'U-UTU9', 30000775: '8-WYQZ', 30000759: '7-JT09', 30000762: '5-2PQU', 30000803: 'MJ-LGH', 30000801: 'MOCW-2',
         30000770: '8BA-RA', 30000763: 'SN9-3Z', 30000758: 'I3CR-F', 30000757: '2JT-3Q', 30000756: '2-Q4YG', 30000802: 'Z0-4AR',
         30000800: '9DLQ-6', 30000761: 'M4-GJ6', 30000750: 'XQP-9C', 30000805: 'RD-FWY', 30000804: 'F2A-GX', 30000798: '3AE-CP',
         30000743: 'C8H5-X', 30000752: 'XKH-6O', 30000751: 'W-6GBI', 30000799: '0-VG7A', 30000806: 'V8PT-T', 30000747: 'TZN-2V',
         30000749: '4DS-OI', 30000754: 'F39H-1', 30000755: 'V-QXXK', 30000807: 'KS-1TS', 30000753: 'S8U-MO', 30000748: '8EF-58',
         30000746: 'WF4C-8', 30000778: 'G-EURJ', 30000795: '4CJ-AC', 30000782: '3U-48K', 30000791: '67Y-NR'}
CORP, ALLI, HC1, HALLI = 98100001, 99100001, 98100002, 99100002
ORGS = {CORP: ['corporation', 'Mockup Shipyards', 'MKSY', ALLI], ALLI: ['alliance', 'Mockup Coalition', 'MKCO', None],
        HC1: ['corporation', 'Mockup Raider Corp', 'MKRC', HALLI], HALLI: ['alliance', 'Mockup Raiders', 'MKRD', None]}
PIL = {95000001: ('Mk Your Main', CORP), 95000011: ('Mk Raider One', HC1), 95000012: ('Mk Raider Two', HC1), 95000013: ('Mk Raider Three', HC1)}
T = {'Sabre': (22456, 541), 'Muninn': (12015, 358)}
GROUPS = {541: 'Interdictor', 358: 'Heavy Assault Cruiser'}
REP = [(90, 'Mk Gate Watcher', '78-0R6 Mk Raider One Sabre camping C-J6MT gate'),
       (200, 'Mk Scout Alt', 'MSG-BZ Mk Raider Three Muninn'),
       (420, 'Mk Gate Watcher', 'SHBF-V Mk Raider Two Muninn')]
data = {'build': J['build'], 'homeName': 'C-J6MT', 'me': {'id': 95000001, 'name': 'Mk Your Main'},
        'names': {str(k): v for k, v in NAMES.items()},
        'orgs': {str(k): v for k, v in ORGS.items()}, 'byId': {str(k): [v[0], v[1]] for k, v in PIL.items()},
        'pilots': {v[0].lower(): k for k, v in PIL.items()},
        'types': {str(v[0]): [k, v[1]] for k, v in T.items()}, 'groups': {str(k): v for k, v in GROUPS.items()}, 'seq': 0, 'kills': {},
        'side': {'pilot': {'id': 95000001, 'name': 'Mk Your Main'}, 'corp': {'id': CORP, 'name': 'Mockup Shipyards'}, 'alliance': {'id': ALLI, 'name': 'Mockup Coalition'},
                 'friendly': [], 'hostile': [{'id': HALLI, 'name': 'Mockup Raiders', 'kind': 'alliance'}], 'rows': 15},
        'intel': {'channels': ['region.intel'], 'me': 95000001, 'range': 4, 'nearRange': 6, 'mapReach': 10, 'killRange': 10, 'forget': 30, 'sound': False, 'notify': False, 'nearShown': False},
        'reports': sorted(REP, reverse=True)}
CSP = '<meta http-equiv="Content-Security-Policy" content="img-src data: blob:; connect-src \'none\'; font-src data:; media-src data: blob:">'
s = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', CSP, src, count=1)
# hooks in the page's own code (each must be found exactly once); a build edits these lines instead (README)
PATCH = [
    # 1. the Distance filter's match: by jumps as today, or by light years where a jump drive can land
    ("    if(ok && o.near) ok = D[i] >= 0 && D[i] <= s.near.n;",
     "    if(ok && o.near) ok = window.__MKnear ? window.__MKnear(i, D) : D[i] >= 0 && D[i] <= s.near.n;"),
    # 2. the hover's line for the LY mode
    ("  if(itMapOnlyOn() && itMapSt().only.sov) h += sovTipHtml(i);",
     "  if(window.__MKtip) h += window.__MKtip(i);\n  if(itMapOnlyOn() && itMapSt().only.sov) h += sovTipHtml(i);"),
]
for a, b in PATCH:
    assert s.count(a) == 1, ('hook not found once', a[:70])
    s = s.replace(a, b)
def rd(n):
    p = os.path.join(HERE, n)
    if not os.path.exists(p) and n == 'mock.js': p = os.path.join(HERE, '..', 'paths-to-you-mockup', 'mock.js')
    return open(p, encoding='utf-8').read()
mock = rd('mock.js').replace('__MKDATA__', json.dumps(data, separators=(',', ':'), ensure_ascii=False))
i = s.index('>', s.index('<head')) + 1
s = s[:i] + '<script>' + mock + '</script>' + s[i:]
j = s.rindex('</body>')
s = s[:j] + '<script>' + rd('proto_ly.js') + '</script><script>' + rd('boot_ly.js') + '</script>' + s[j:]
open(sys.argv[2], 'w', encoding='utf-8').write(s)
print('built', sys.argv[2], len(s))
