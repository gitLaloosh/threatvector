"""Paths-to-you mockup: the real page (index.html, main d227c9d / v2026.11.12.4) fed made-up Intel around C-J6MT, plus proto_pt.js
(a seventh map filter, "Paths to you": a tree of the gate routes from reported hostiles inside your alert range to you).
python3 -I build_pt.py <repo>/index.html <out.html>   (mock.js, proto_pt.js, boot_pt.js beside this script)
System names: the map-look mockup's list (claude/roadmap/map-look-mockup/build_map.py: ref-data.everef.net, checked 2026-11-11, and
the owner's in-game map read by position). Everyone and every group is invented ("Mk ..." / "Mockup ..."); ship types are EVE's own."""
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
PIL = {95000001: ('Mk Your Main', CORP), 95000011: ('Mk Raider One', HC1), 95000012: ('Mk Raider Two', HC1), 95000013: ('Mk Raider Three', HC1),
       95000014: ('Mk Raider Four', HC1), 95000015: ('Mk Raider Five', HC1), 95000016: ('Mk Raider Six', HC1), 95000017: ('Mk Raider Seven', HC1),
       95000002: ('Mk Corp Mate', CORP), 95000003: ('Mk Ratter Alt', CORP)}
T = {'Sabre': (22456, 541), 'Muninn': (12015, 358)}
GROUPS = {541: 'Interdictor', 358: 'Heavy Assault Cruiser'}
# seconds ago, reporter, line. Alert range set to 4 here so G-EURJ's two equally short routes show. Inside it (4): 78-0R6 (1), 4M-QXK (1, neutrals), MSG-BZ (2), MJ-LGH (2), SHBF-V (3), 3U-48K (3).
# ... and G-EURJ (4: two shortest routes), 0UBC-R (4).
REP = [(60, 'Mk Gate Watcher', '78-0R6 Mk Raider One Sabre camping C-J6MT gate'),
       (120, 'Mk Scout Alt', 'MSG-BZ Mk Raider Three Muninn'),
       (200, 'Mk Gate Watcher', 'SHBF-V Mk Raider Two Muninn'),
       (260, 'Mk Scout Alt', '3U-48K 5 red'),
       (330, 'Mk Gate Watcher', 'MJ-LGH Mk Raider Four Sabre'),
       (400, 'Mk Scout Alt', '4M-QXK 2 neut'),
       (450, 'Mk Gate Watcher', 'G-EURJ 8 red'),
       (500, 'Mk Scout Alt', '0UBC-R Mk Raider Five Muninn'),
       (150, 'Mk Scout Alt', 'RERZ-L Mk Raider Seven Sabre hacking the ess')]
# kills (made-up killmails, read through the stand-in R2Z2): two of ours lost in MSG-BZ, one hostile killed in SHBF-V, and one in 8-WYQZ,
# a system nobody reported (it joins the tree from the kill alone)
def who(i):
    c = PIL[i][1]; a = ORGS[c][3]
    return {'character_id': i, 'corporation_id': c, **({'alliance_id': a} if a else {})}
def kill(kid, sysid, ago, victim, vship, atts, value):
    return {'id': kid, 'hash': f'{kid:040x}', 'sys': sysid, 'ago': ago, 'victim': dict(who(victim), ship_type_id=T[vship][0], damage_taken=9000),
            'attackers': [dict(who(a), ship_type_id=T[sh][0], final_blow=k == 0, damage_done=4000 - 600 * k) for k, (a, sh) in enumerate(atts)],
            'zkb': {'totalValue': value, 'npc': False, 'solo': len(atts) == 1, 'attackerCount': len(atts)}}
SEQ = 3   # the reader reads back from 0: these four, then 404 = caught up
KILLS = {str(SEQ - 3): kill(9400001, 30000774, 170, 95000002, 'Muninn', [(95000013, 'Muninn'), (95000011, 'Sabre')], 182e6),
         str(SEQ - 2): kill(9400002, 30000774, 130, 95000003, 'Sabre', [(95000013, 'Muninn')], 64e6),
         str(SEQ - 1): kill(9400003, 30000779, 220, 95000012, 'Muninn', [(95000002, 'Sabre')], 210e6),
         str(SEQ): kill(9400004, 30000775, 90, 95000003, 'Sabre', [(95000014, 'Sabre')], 58e6)}
data = {'build': J['build'], 'homeName': 'C-J6MT', 'me': {'id': 95000001, 'name': 'Mk Your Main'},
        'names': {str(k): v for k, v in NAMES.items()},
        'orgs': {str(k): v for k, v in ORGS.items()}, 'byId': {str(k): [v[0], v[1]] for k, v in PIL.items()},
        'pilots': {v[0].lower(): k for k, v in PIL.items()},
        'types': {str(v[0]): [k, v[1]] for k, v in T.items()}, 'groups': {str(k): v for k, v in GROUPS.items()}, 'seq': SEQ, 'kills': KILLS,
        'side': {'pilot': {'id': 95000001, 'name': 'Mk Your Main'}, 'corp': {'id': CORP, 'name': 'Mockup Shipyards'}, 'alliance': {'id': ALLI, 'name': 'Mockup Coalition'},
                 'friendly': [], 'hostile': [{'id': HALLI, 'name': 'Mockup Raiders', 'kind': 'alliance'}], 'rows': 15},
        'intel': {'channels': ['region.intel'], 'me': 95000001, 'range': 4, 'nearRange': 6, 'mapReach': 10, 'killRange': 10, 'forget': 30, 'sound': False, 'notify': False},
        'reports': sorted(REP, reverse=True)}
CSP = '<meta http-equiv="Content-Security-Policy" content="img-src data: blob:; connect-src \'none\'; font-src data:; media-src data: blob:">'
s = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', CSP, src, count=1)
rd = lambda n: open(os.path.join(HERE, n), encoding='utf-8').read()
mock = rd('mock.js').replace('__MKDATA__', json.dumps(data, separators=(',', ':'), ensure_ascii=False))
i = s.index('>', s.index('<head')) + 1
s = s[:i] + '<script>' + mock + '</script>' + s[i:]
j = s.rindex('</body>')
s = s[:j] + '<script>' + rd('proto_pt.js') + '</script><script>' + rd('boot_pt.js') + '</script>' + s[j:]
open(sys.argv[2], 'w', encoding='utf-8').write(s)
print('built', sys.argv[2], len(s))
