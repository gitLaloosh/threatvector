"""Sov hubs on the Intel map (Project doc claude/roadmap/sov-hubs-plan.md; research claude/roadmap/intel-later-filters-research.md E2,
answered 2026-11-21): the real page (index.html, main e1ebe17 / v2026.11.21.1) fed made-up Intel around C-J6MT, plus proto_hb.js: a new Only
filter "Sov hubs" (kinds Fight coming up / Vulnerable, each with its hours), made-up sov fights and hub vulnerability windows (no ESI read),
the hover lines, "⚔ 19:45" tags beside fights, the Only line.
python3 -I build_hb.py <repo>/index.html <out.html>   (mock.js, proto_hb.js, boot_hb.js beside this script)
mock.js: the repo's roadmap/paths-to-you-mockup/mock.js, unchanged. System names: the map-look mockup's list (ref-data.everef.net,
checked 2026-11-11). Every pilot, corporation and alliance is invented ("Mk ..." / "Mockup ...")
Rebuilt 2026-11-25 by the build session for the archive (build queue 068) on main b1b9714 (v2026.11.25.1), the page before the build: hook 4
follows 065's IT_MP_KEYS (itMpOpen no longer names secr and near itself). Run it on a page from before 068: on 068's page the filter is there
already and the mockup would add it twice."""
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
    # 1. the Sov hubs filter's match (a build puts the test in itMapMatch itself)
    ("    if(ok && o.wh) ok = W.kept.has(i);",
     "    if(ok && o.wh) ok = W.kept.has(i);\n    if(ok && o.hub) ok = window.__MKhub ? window.__MKhub(i) : false;"),
    # 2. the hover's sov hub lines
    ("  if(itMapOnlyOn() && itMapSt().only.sov) h += sovTipHtml(i);",
     "  if(window.__MKtip) h += window.__MKtip(i);\n  if(itMapOnlyOn() && itMapSt().only.sov) h += sovTipHtml(i);"),
    # 3. the "⚔ 19:45" tags, placed with the map's other labels
    ("  if(focus >= 0 && focus !== itm.home && !itm.rep.has(focus) && !WH.mark.has(focus)) put(focus",
     "  if(window.__MKlab) window.__MKlab(put, nm, F, TAG, focus);\n  if(focus >= 0 && focus !== itm.home && !itm.rep.has(focus) && !WH.mark.has(focus)) put(focus"),
    # 3b. a reported system's fight tag joins its report label (a build adds it where the label's pieces are made)
    ("  for(const i of order) put(i, [{t: nm(i), col: i === focus ? C.cyan : '#d7dee3', font: F}, ...tags(itm.rep.get(i)), ...whTag(i)], true);",
     "  for(const i of order) put(i, [{t: nm(i), col: i === focus ? C.cyan : '#d7dee3', font: F}, ...tags(itm.rep.get(i)), ...whTag(i), ...(window.__MKftag ? window.__MKftag(i, TAG) : [])], true);"),
    # 4. its settings open in 058's panel (itMp), as Security range's and Within N jumps' do (2026-11-25: 065's IT_MP_KEYS)
    ("if(!itm.box || !IT_MP_KEYS.includes(k)) return;",
     "if(!itm.box || (!IT_MP_KEYS.includes(k) && k !== 'hub')) return;"),
]
for a, b in PATCH:
    assert s.count(a) == 1, ('hook not found once', a[:70])
    s = s.replace(a, b)
rd = lambda n: open(os.path.join(HERE, n), encoding='utf-8').read()
mock = rd('mock.js').replace('__MKDATA__', json.dumps(data, separators=(',', ':'), ensure_ascii=False))
i = s.index('>', s.index('<head')) + 1
s = s[:i] + '<script>' + mock + '</script>' + s[i:]
j = s.rindex('</body>')
s = s[:j] + '<script>' + rd('proto_hb.js') + '</script><script>' + rd('boot_hb.js') + '</script>' + s[j:]
open(sys.argv[2], 'w', encoding='utf-8').write(s)
print('built', sys.argv[2], len(s))
