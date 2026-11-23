"""Live-data map filters mockup: the real page (index.html, main f70fdd5 / v2026.11.20.1, after 058, 057, 060) fed made-up Intel
around C-J6MT, plus proto_lm.js (Project doc claude/roadmap/live-map-filters-plan.md): Sov holder (by standing / per alliance, logos
in the circles zoomed in, gate lines in the holder's colour), Jumps (past hour), Kills (past hour, NPC kills in its settings), Region
pick, and the phone column laid out by group.
python3 -I build_lm.py <repo>/index.html <out.html>   (mock.js, proto_lm.js, boot_lm.js beside this script)
mock.js: the repo's roadmap/paths-to-you-mockup/mock.js, unchanged. System names: the map-look mockup's list (ref-data.everef.net,
checked 2026-11-11). Every alliance, logo, pilot and number is invented ("Mk ..." / "Mockup ..."); the sov holders, jumps and kills are
made up at start (proto_lm.js MKL.seed) from the page's own map table; ship types are EVE's own."""
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
# hooks in the page's own code (each must be found exactly once); a build reworks these functions instead (README "Shortcuts")
PATCH = [
    # 1. the holder's gate lines, over the plain gates and under the bridges
    ("  // build queue 041: your jump bridges, while the setting is on",
     "  if(window.__MKgates) window.__MKgates(c, X, Y, on, big, W, H);\n  // build queue 041: your jump bridges, while the setting is on"),
    # 2. a zoomed-in circle: the holder's logo inside it (Sov holder), else as today
    ("c.globalAlpha = a; c.fillStyle = hit || i === itm.home ? itMapColRaw(i) : itMapMix(itMapColRaw(i), 0.38); c.beginPath(); c.arc(x, y, hit ? r * 1.25 : r, 0, 6.283); c.fill();\n      c.globalAlpha = 1; c.lineWidth = 1.5; c.strokeStyle = '#0c1014'; c.stroke();",
     "if(!(window.__MKcircle && window.__MKcircle(c, i, x, y, hit ? r * 1.25 : r, a, hit))){ c.globalAlpha = a; c.fillStyle = hit || i === itm.home ? itMapColRaw(i) : itMapMix(itMapColRaw(i), 0.38); c.beginPath(); c.arc(x, y, hit ? r * 1.25 : r, 0, 6.283); c.fill();\n      c.globalAlpha = 1; c.lineWidth = 1.5; c.strokeStyle = '#0c1014'; c.stroke(); }"),
    # 3. the circle's number: the hour's count (Jumps / Kills past hour), none under a logo
    ("const col = itMapSt().colour; if(col) c.fillText(",
     "const col = itMapSt().colour; if(col && !(window.__MKnum && window.__MKnum(c, i, x, y, col))) c.fillText("),
    # 4. the hover's lines for the new colours
    ("  if(itMapOnlyOn() && itMapSt().only.sov) h += sovTipHtml(i);",
     "  if(window.__MKtip) h += window.__MKtip(i);\n  if(itMapOnlyOn() && itMapSt().only.sov) h += sovTipHtml(i);"),
    # 5. the settings panel opens for the new filters too
    ("if(!itm.box || (k !== 'secr' && k !== 'near')) return;",
     "if(!itm.box || !['secr', 'near', 'sovh', 'killh', 'regpick'].includes(k)) return;"),
    # 6. Region pick in the match pass
    ("    m[i] = ok ? 1 : 0;\n  }\n  if(itm.home >= 0) m[itm.home] = 1;",
     "    if(ok && o.regpick) ok = !!(window.__MKreg && window.__MKreg(i));\n    m[i] = ok ? 1 : 0;\n  }\n  if(itm.home >= 0) m[itm.home] = 1;"),
    # 7. the column's rows count the filters, not the group wrappers (live map and the Intel example)
    ("const rows = String(itMapFlRows(itm.H, fb.offsetTop, phone, bs.children.length));",
     "const rows = String(itMapFlRows(itm.H, fb.offsetTop, phone, window.__MKn ? window.__MKn(bs) : bs.children.length));"),
    ("if(bs){ const rows = String(itMapFlRows(h, fb.offsetTop, phone, bs.children.length));",
     "if(bs){ const rows = String(itMapFlRows(h, fb.offsetTop, phone, window.__MKn ? window.__MKn(bs) : bs.children.length));"),
    # 9. Q10 (the owner: "ok, go with your choice for now."): the three live-data colours skip the distance fades (only Only filters dim)
    ("const mt = itm.mt, alpha = (i) => mt ? (mt.m[i] ? 1 : IT_MAP_DIM) : !on(i) ? IT_MAP_FAINT",
     "const mt = itm.mt, noFade = !!(window.__MKnofade && window.__MKnofade()), alpha = (i) => mt ? (mt.m[i] ? 1 : IT_MAP_DIM) : noFade ? 1 : !on(i) ? IT_MAP_FAINT"),
    # 8. after a draw: the "holders in view" list in the legend (written only when it changes)
    ("  itMapRegionNames(c);\n  itMapYouArrow();\n}",
     "  itMapRegionNames(c);\n  itMapYouArrow();\n  if(window.__MKdrawn) window.__MKdrawn();\n}"),
]
for a, b in PATCH:
    assert s.count(a) == 1, ('hook not found once', a[:70])
    s = s.replace(a, b)
rd = lambda n: open(os.path.join(HERE, n), encoding='utf-8').read()
mock = rd('mock.js').replace('__MKDATA__', json.dumps(data, separators=(',', ':'), ensure_ascii=False))
i = s.index('>', s.index('<head')) + 1
s = s[:i] + '<script>' + mock + '</script>' + s[i:]
j = s.rindex('</body>')
s = s[:j] + '<script>' + rd('proto_lm.js') + '</script><script>' + rd('boot_lm.js') + '</script>' + s[j:]
open(sys.argv[2], 'w', encoding='utf-8').write(s)
print('built', sys.argv[2], len(s))
