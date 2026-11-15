"""Dossier-by-fights mockup: the real page (index.html) with one made-up pilot whose newest 50 kills are all one war weekend,
and whose small-gang and solo kills are older. zKillboard's lists carry the full killmail (as zKillboard's API does); the
mockup expands the fleets at load time so the file stays small. No network.
python3 -I build_fights.py <repo>/index.html <out.html>   (mock_fights.js, proto_fights.js, boot_fights.js beside this script)"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(sys.argv[1], encoding='utf-8').read()
# Everyone and every group is invented ("Mk ..." / "Mockup ..."); ship types and systems are EVE's public data.
ME = 95000011
ORGS = {98200001: ['corporation', 'Mockup Line Corp', 'MKLC', 99200001], 98200002: ['corporation', 'Mockup Second Wing', 'MKSW', 99200001],
        98200003: ['corporation', 'Mockup Third Wing', 'MKTW', 99200001], 99200001: ['alliance', 'Mockup Coalition', 'MKCO', None],
        98300001: ['corporation', 'Mockup Raider Corp', 'MKRC', 99300001], 98300002: ['corporation', 'Mockup Blade Works', 'MKBW', 99300001],
        99300001: ['alliance', 'Mockup Raiders', 'MKRD', None], 98300003: ['corporation', 'Mockup Haulers', 'MKHL', None]}
WING = {95000101: 'Mk Wing Ari', 95000102: 'Mk Wing Bo', 95000103: 'Mk Wing Cy', 95000104: 'Mk Wing Dee', 95000105: 'Mk Wing Eli', 95000106: 'Mk Wing Fen'}
T = {'Ferox Navy Issue': (72811, 419), 'Typhoon': (644, 27), 'Svipul': (34562, 1305), 'Rupture': (629, 26), 'Osprey Navy Issue': (29340, 26),
     'Retribution': (11393, 324), 'Enyo': (12044, 324), 'Keres': (11174, 893), 'Vulture': (22446, 540), 'Absolution': (22448, 540),
     'Confessor': (34317, 1305), 'Scimitar': (11978, 832), 'Sabre': (22456, 541), 'Stabber': (622, 26), 'Venture': (32880, 1283),
     'Rifter': (587, 25), 'Hurricane': (24702, 419), 'Capsule': (670, 29), 'Caracal': (621, 26), 'Moa': (623, 26), 'Exequror': (634, 26),
     'Badger': (648, 28), 'Hound': (12034, 834), 'Merlin': (603, 25), 'Vexor': (626, 26), 'Ishtar': (12005, 358), 'Muninn': (12015, 358),
     'Cheetah': (11182, 830), 'Ferox': (16227, 419)}
GROUPS = {419: 'Combat Battlecruiser', 27: 'Battleship', 1305: 'Tactical Destroyer', 26: 'Cruiser', 324: 'Assault Frigate', 893: 'Electronic Attack Ship',
          540: 'Command Ship', 832: 'Logistics', 541: 'Interdictor', 1283: 'Expedition Frigate', 25: 'Frigate', 29: 'Capsule', 28: 'Hauler',
          834: 'Stealth Bomber', 358: 'Heavy Assault Cruiser', 830: 'Covert Ops'}
SYS = {30004759: ('1DQ1-A', -0.4), 30004712: ('NOL-M9', -0.5), 30004738: ('T5ZI-S', -0.2), 30001198: ('GE-8JV', -0.3),
       30002086: ('Turnur', 0.3), 30002537: ('Amamake', 0.4), 30003504: ('Niarja', 0.5), 30000142: ('Jita', 0.9), 30002053: ('Hek', 0.5),
       30002813: ('Tama', 0.3)}
NUL = [30004759, 30004712, 30004738, 30001198]
LOW = [30002086, 30002537, 30002813]
H, D = 3600, 86400
VICT = ['Stabber', 'Caracal', 'Moa', 'Exequror', 'Rifter', 'Merlin', 'Vexor', 'Badger', 'Venture', 'Hound', 'Hurricane', 'Ferox']
# An op: a fleet (n pilots, ship mix) or a gang (named wingmates); its kills a few minutes apart.
kills, nk = [], [0]
def op(ago, sysid, hull, count, fleet=None, gang=None, vict=None):
    for i in range(count):
        nk[0] += 1
        v = (vict or VICT)[(nk[0] * 7) % len(vict or VICT)]
        kills.append([ago - i * 240, sysid, hull, v, fleet, gang])
FLEET_TY = [140, 1000, ['Typhoon', 'Typhoon', 'Typhoon', 'Absolution', 'Confessor', 'Scimitar']]
FLEET_TY2 = [130, 1200, ['Typhoon', 'Typhoon', 'Absolution', 'Scimitar', 'Sabre']]
FLEET_FNI = [31, 1000, ['Ferox Navy Issue', 'Svipul', 'Vulture', 'Scimitar']]
FLEET_FX = [60, 1400, ['Ferox', 'Ferox', 'Vulture', 'Scimitar', 'Sabre']]
A, B, C, Dd, E, F = 95000101, 95000102, 95000103, 95000104, 95000105, 95000106
# page 1 (newest 200): the war weekend first, then the small-gang life behind it
op(22 * H, NUL[0], 'Ferox Navy Issue', 3, fleet=FLEET_FNI)
op(8 * D, NUL[1], 'Typhoon', 24, fleet=FLEET_TY, vict=['Badger', 'Venture', 'Hound', 'Caracal'])
op(9 * D + 3 * H, NUL[2], 'Typhoon', 23, fleet=FLEET_TY, vict=['Badger', 'Hound', 'Moa'])
op(18 * D, LOW[0], 'Svipul', 3, gang=[[A, 'Svipul'], [B, 'Rupture'], [C, 'Osprey Navy Issue']])
op(21 * D, LOW[1], 'Svipul', 2, gang=[[A, 'Svipul'], [B, 'Svipul'], [Dd, 'Keres']])
op(25 * D, LOW[2], 'Svipul', 1, gang=[[A, 'Enyo'], [B, 'Svipul']])
op(33 * D, LOW[0], 'Retribution', 1)
op(41 * D, LOW[1], 'Retribution', 1)
op(47 * D, NUL[3], 'Typhoon', 38, fleet=FLEET_TY2)
op(48 * D + 2 * H, NUL[0], 'Typhoon', 32, fleet=FLEET_TY2)
op(52 * D, LOW[2], 'Enyo', 1)
op(60 * D, LOW[0], 'Rupture', 4, gang=[[A, 'Rupture'], [C, 'Rupture'], [E, 'Stabber'], [F, 'Osprey Navy Issue']])
op(66 * D, LOW[1], 'Osprey Navy Issue', 2, gang=[[A, 'Rupture'], [B, 'Rupture']])
op(74 * D, LOW[2], 'Keres', 3, gang=[[A, 'Svipul'], [B, 'Svipul'], [C, 'Svipul'], [Dd, 'Enyo'], [E, 'Rupture']])
op(81 * D, LOW[0], 'Svipul', 2, gang=[[A, 'Svipul'], [B, 'Retribution']])
op(100 * D, NUL[1], 'Ferox', 30, fleet=FLEET_FX)
op(104 * D, NUL[2], 'Ferox', 25, fleet=FLEET_FX)
op(120 * D, LOW[1], 'Retribution', 1)
op(130 * D, LOW[2], 'Svipul', 4, gang=[[A, 'Svipul'], [Dd, 'Svipul'], [F, 'Enyo']])
# pages 2 and 3 (older): the same pattern, further back (read only when the fights so far fall short of the quota)
ago = 140 * D
k = 0
while len(kills) < 640:
    k += 1
    if k % 3 == 0:
        op(ago, NUL[k % 4], 'Typhoon', 40, fleet=FLEET_TY2 if k % 2 else FLEET_TY)
    elif k % 3 == 1:
        op(ago, LOW[k % 3], ['Svipul', 'Rupture', 'Retribution', 'Keres'][k % 4], 3, gang=[[A, 'Svipul'], [B, 'Rupture'], [[C, Dd, E, F][k % 4], 'Enyo']])
    else:
        op(ago, LOW[(k + 1) % 3], 'Retribution', 1)
    ago += 4 * D + (k % 5) * D
kills.sort(key=lambda x: x[0])
# losses: what they fly between wars (and two Typhoons, many pods)
LOSS = [(18 * D, 'Svipul'), (30 * D, 'Capsule'), (73 * D, 'Rupture'), (76 * D, 'Osprey Navy Issue'), (80 * D, 'Retribution'), (82 * D, 'Capsule'),
        (88 * D, 'Osprey Navy Issue'), (95 * D, 'Typhoon'), (110 * D, 'Osprey Navy Issue'), (125 * D, 'Enyo'), (131 * D, 'Capsule'),
        (160 * D, 'Keres'), (170 * D, 'Svipul'), (190 * D, 'Rupture'), (205 * D, 'Osprey Navy Issue'), (220 * D, 'Capsule'), (240 * D, 'Retribution'),
        (260 * D, 'Typhoon'), (280 * D, 'Svipul'), (300 * D, 'Capsule'), (320 * D, 'Retribution'), (345 * D, 'Svipul'), (360 * D, 'Capsule')]
losses = [[a, LOW[i % 3] if s not in ('Typhoon',) else NUL[i % 4], s, 2 + (i * 5) % 9] for i, (a, s) in enumerate(LOSS)]
data = {'me': ME, 'meName': 'Mk Line Pilot', 'meCorp': 98200001, 'orgs': {str(k): v for k, v in ORGS.items()},
        'wing': {str(k): v for k, v in WING.items()}, 'types': {str(v[0]): [k, v[1]] for k, v in T.items()},
        'groups': {str(k): v for k, v in GROUPS.items()}, 'sys': {str(k): v for k, v in SYS.items()}, 'kills': kills, 'losses': losses}
CSP = '<meta http-equiv="Content-Security-Policy" content="img-src data: blob:; connect-src \'none\'; font-src data:; media-src data: blob:">'
s = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', CSP, src, count=1)
mock = open(os.path.join(HERE, 'mock_fights.js'), encoding='utf-8').read().replace('__MKDATA__', json.dumps(data, separators=(',', ':'), ensure_ascii=False))
i = s.index('>', s.index('<head')) + 1
s = s[:i] + '<script>' + mock + '</script>' + s[i:]
j = s.rindex('</body>')
s = s[:j] + ''.join('<script>' + open(os.path.join(HERE, f), encoding='utf-8').read() + '</script>' for f in ('proto_fights.js', 'boot_fights.js')) + s[j:]
open(sys.argv[2], 'w', encoding='utf-8').write(s)
print('built', sys.argv[2], len(kills), 'kills', len(losses), 'losses')
