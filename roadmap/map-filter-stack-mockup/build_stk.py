"""Stacked map filters mockup: the real page (index.html, main 51207b6 / v2026.11.16.1, after 053) fed made-up Intel around C-J6MT,
plus proto_stk.js (the panel review's model, claude/roadmap/map-filter-model-panel.md: Colour by one, Show only conditions stacked,
marks always on, Paths to you a view).
python3 -I build_stk.py <repo>/index.html <out.html>   (mock.js, proto_stk.js, boot_stk.js beside this script)
mock.js: the repo's roadmap/paths-to-you-mockup/mock.js, unchanged. Data: that mockup's (build_pt.py), plus two wormhole reports.
System names: the map-look mockup's list (ref-data.everef.net, checked 2026-11-11). Everyone and every group is invented ("Mk ..." /
"Mockup ..."); ship types are EVE's own. The sov list is made up at start (boot_stk.js), from these systems only; 12 more wormholes
are made up at start too (MKP.seedWh), on unnamed systems given made-up names MKW-01 to MKW-12."""
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
REP = [(60, 'Mk Gate Watcher', '78-0R6 Mk Raider One Sabre camping C-J6MT gate'),
       (120, 'Mk Scout Alt', 'MSG-BZ Mk Raider Three Muninn'),
       (200, 'Mk Gate Watcher', 'SHBF-V Mk Raider Two Muninn'),
       (260, 'Mk Scout Alt', '3U-48K 5 red'),
       (330, 'Mk Gate Watcher', 'MJ-LGH Mk Raider Four Sabre'),
       (400, 'Mk Scout Alt', '4M-QXK 2 neut'),
       (450, 'Mk Gate Watcher', 'G-EURJ 8 red'),
       (500, 'Mk Scout Alt', '0UBC-R Mk Raider Five Muninn'),
       (150, 'Mk Scout Alt', 'RERZ-L Mk Raider Seven Sabre hacking the ess'),
       (600, 'Mk Scout Alt', '8-WYQZ wh in system'),
       (900, 'Mk Gate Watcher', 'KS-1TS wormhole')]
def who(i):
    c = PIL[i][1]; a = ORGS[c][3]
    return {'character_id': i, 'corporation_id': c, **({'alliance_id': a} if a else {})}
def kill(kid, sysid, ago, victim, vship, atts, value):
    return {'id': kid, 'hash': f'{kid:040x}', 'sys': sysid, 'ago': ago, 'victim': dict(who(victim), ship_type_id=T[vship][0], damage_taken=9000),
            'attackers': [dict(who(a), ship_type_id=T[sh][0], final_blow=k == 0, damage_done=4000 - 600 * k) for k, (a, sh) in enumerate(atts)],
            'zkb': {'totalValue': value, 'npc': False, 'solo': len(atts) == 1, 'attackerCount': len(atts)}}
SEQ = 3
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
        'intel': {'channels': ['region.intel'], 'me': 95000001, 'range': 4, 'nearRange': 6, 'mapReach': 10, 'killRange': 10, 'forget': 30, 'sound': False, 'notify': False, 'nearShown': False},
        'reports': sorted(REP, reverse=True)}
CSP = '<meta http-equiv="Content-Security-Policy" content="img-src data: blob:; connect-src \'none\'; font-src data:; media-src data: blob:">'
s = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', CSP, src, count=1)
# nine hooks in the page's own code (each line must be found exactly once)
PATCH = [
    ("alpha = (i) => itMapDimmed(i) ? IT_MAP_DIM : (whF && itm.wh.kept.has(i)) || (itm.sov && itm.sov.has(i)) ? 1 : !on(i) ? IT_MAP_FAINT : D[i] > near ? 0.45 : 1;",
     "alpha0 = (i) => itMapDimmed(i) ? IT_MAP_DIM : (whF && itm.wh.kept.has(i)) || (itm.sov && itm.sov.has(i)) ? 1 : !on(i) ? IT_MAP_FAINT : D[i] > near ? 0.45 : 1, alpha = (i) => window.__MKalpha ? window.__MKalpha(i, alpha0) : alpha0(i);"),
    ("mark: itm.filter === 'wh' ? kept : live", "mark: window.__MKmark ? window.__MKmark(kept, live) : itm.filter === 'wh' ? kept : live"),
    ("if(itm.filter === 'sov') h += sovTipHtml(i);", "if(itm.filter === 'sov' || (window.__MKsov && window.__MKsov())) h += sovTipHtml(i);"),
    ("const rr = Number(a) === IT_MAP_FAINT ? Math.max(1.2, dotR - 0.6) : dotR;", "const rr = Number(a) === IT_MAP_FAINT ? Math.max(1.2, dotR - 0.6) : (Number(a) === 1 && window.__MKbig && window.__MKbig()) ? dotR + 1.6 : dotR;"),
    ("c.globalAlpha = a; c.fillStyle = itMapFcol(i); c.beginPath(); c.arc(x, y, r, 0, 6.283); c.fill();\n      c.globalAlpha = 1; c.lineWidth = 1.5; c.strokeStyle = '#0c1014'; c.stroke();",
     "if(!(window.__MKcircle && window.__MKcircle(c, i, x, y, r, a))){ c.globalAlpha = a; c.fillStyle = itMapFcol(i); c.beginPath(); c.arc(x, y, r, 0, 6.283); c.fill();\n      c.globalAlpha = 1; c.lineWidth = 1.5; c.strokeStyle = '#0c1014'; c.stroke(); }"),
    ("c.arc(X(i), Y(i), big ? r + 9 : 22 * Math.min(1.4, Math.sqrt(g / IT_MAP_START_GATE)), 0, 6.283)",
     "c.arc(X(i), Y(i), window.__MKglow ? window.__MKglow(big, r, g) : (big ? r + 9 : 22 * Math.min(1.4, Math.sqrt(g / IT_MAP_START_GATE))), 0, 6.283)"),
    ("c.fillText(itm.filter === 'jumps' ? (D[i] < 0 ? '–' : String(D[i])) : itMapSecText(T.sec[i]), x, y + 0.5);",
     "if(!(window.__MKplain && window.__MKplain())) c.fillText(itm.filter === 'jumps' ? (D[i] < 0 ? '–' : String(D[i])) : itMapSecText(T.sec[i]), x, y + 0.5);"),
    # Q21 (answered 2026-11-16): 045's bold mark, pulse and filled label for the holes that match, with the Wormholes filter on
    ("if(whF){ itMapWhBold(c, x, y, w, big, r);", "if(whF || (window.__MKwhBold && window.__MKwhBold(i))){ itMapWhBold(c, x, y, w, big, r);"),
    ("whS ? {t: itMapWhLabel(w), bg: itMapWhCol(w)", "(whS || (window.__MKwhBold && window.__MKwhBold(i))) ? {t: itMapWhLabel(w), bg: itMapWhCol(w)"),
]
for a, b in PATCH:
    assert s.count(a) == 1, ('hook not found once', a[:60])
    s = s.replace(a, b)
rd = lambda n: open(os.path.join(HERE, n), encoding='utf-8').read()
mock = rd('mock.js').replace('__MKDATA__', json.dumps(data, separators=(',', ':'), ensure_ascii=False))
i = s.index('>', s.index('<head')) + 1
s = s[:i] + '<script>' + mock + '</script>' + s[i:]
j = s.rindex('</body>')
s = s[:j] + '<script>' + rd('proto_stk.js') + '</script><script>' + rd('boot_stk.js') + '</script>' + s[j:]
open(sys.argv[2], 'w', encoding='utf-8').write(s)
print('built', sys.argv[2], len(s))
