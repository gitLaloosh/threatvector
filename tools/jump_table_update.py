"""The page's jump table (INTEL_JUMPS) against CCP's published static data, newest build (v2026.10.29.5).

    python3 -I tools/jump_table_update.py [index.html] --check            # the update-check chain: exit 1 when a gate differs
    python3 -I tools/jump_table_update.py [index.html] --write --body F   # the GitHub Action: rewrite the table when a gate
                                                                         #   changed, and write a pull request's text to F
    ... --sde PATH   use a downloaded copy (the JSON Lines zip, or a folder holding mapStargates.jsonl and
                     mapSolarSystems.jsonl, with latest.jsonl for the build) instead of downloading

The owner, 2026-10-29: "Eve deploys patches very often. is there a way to automate the update so the user never has to
see it?" Until v2026.10.29.4 the page compared EVE's build (ESI /status/) with the build its table came from and showed an
amber warning after every patch, though patches seldom touch stargates. Now .github/workflows/jump-table.yml runs this
twice a day: CCP publishes the static data with each build (developers.eveonline.com/docs/services/static-data/:
tranquility/latest.jsonl names the build; eve-online-static-data-<build>-jsonl.zip holds mapStargates.jsonl, each gate
with its solarSystemID and destination.solarSystemID). When the gate connections differ from the page's, the Action
opens a pull request with the new table; otherwise nothing happens. Only the connections are compared: a new build with
the same gates changes nothing (the table keeps the build it was last rebuilt from).

v2026.11.02.4 (the Intel map, roadmap/intel-map-plan.md): the same run also derives INTEL_MAP, the map's table, from
mapSolarSystems.jsonl and mapRegions.jsonl, aligned to INTEL_JUMPS's sorted systems: CCP's flat schematic position
(position2D x and y, in units of 1e14 m, rounded half up, int16), the security status (to 3 decimals, then in
hundredths, rounded half up, int8: the same arithmetic as the browser-side export the first table came from,
claude/roadmap/intel-map-mockup/sde_extract3.js) and the region (an index into the region names, sorted by region ID).
A change there opens the same pull request; `--check` fails on it too.

v2026.11.04.1 (light-years in the map's hover, roadmap/map-ly-hover-plan.md): INTEL_MAP also holds each system's place in
space, CCP's geographic `position` (3D, metres; position2D is only the flat map's), as p3: x for every system, then y,
then z, each in units of p3u = 0.0001 light-year (CCP's light-year, LY_M = 9.46e15 m, not the real-world one), rounded
half up, int24 little-endian (the largest is about 54 LY: 540,000 units). 0.0001 LY rather than 0.001: the page rounds
distances UP to 0.01 LY (the owner: "Round up to 0.01"), so the table's own error must stay far below that step; it cost
4.1 KB gzipped more (measured on build 3665151).

Build queue 047 (the route planner, roadmap/route-planner-plan.md change 1a): INTEL_MAP also holds band, each system's security band
from CCP's unrounded securityStatus (0 null at 0.0 or below, 1 low below 0.45, 2 high), 2 bits a system, four to a byte (the first
system in the lowest bits), base64. The sec column is rounded to hundredths, which puts systems just under 0.45 at "0.45": 19 of them
in build 3682781, all low sec in EVE's own route (ESI's POST /route on 40 sample routes, compared at the 047 build review). The
page's own route planner reads the band, never sec, for the 0.0 / 0.45 lines.

Build queue 063 (roadmap/security-shown-plan.md; LESSON #170): INTEL_MAP.secT, in place of sec and band, holds the tenth the game shows
(int8, -10..10) from CCP's unrounded securityStatus: the nearest tenth, except above 0.0 and below 0.05 shows 0.1 (shown_tenth). The sec
column's double rounding (to 3 decimals, then hundredths, then the page's tenths) put 333 systems a tenth off (measured 2026-11-20); band
is the shown tenth's (0 or less null, 1-4 low, 5 or more high; asserted for every system before writing). A value on a halfway point
takes the tenth the owner saw in game (SEC_CHECKED_IN_GAME), else the nearest and the pull request names it at its top to check in game.
The first run on a page from before 063 rewrites the column for every system and lists those whose shown security changes.
`--self-test`: the rule's cases, offline.

Checked 2026-10-29 in the owner's browser: build 3660036's 13,978 gates make the same 6,989 connections as the page's
table from the client's jumps.static (build 3654997), none missing either way.

Build queue 048 (the Wormholes tab, Project doc roadmap/wormhole-mapping-plan.md): INTEL_WH, the wormhole systems (IDs 31,000,000 to
31,999,999, CCP's developer docs' ID ranges), in its own block after the INTEL TABLES (tools/gen_intel_tables.py rewrites that block from
the lines it knows): sys = base64 of uint16 LE deltas of the sorted IDs (the first from 31000000); names = the English names, "|"-joined, in
that order; cls = one character a system for its wormholeClassID (the system's own, else its constellation's, else its region's: in build
3698585 only the five Drifter systems carry their own): 1-6, s shattered (13), t Thera (12), d a Drifter system (14-18); eff = one character
a system for the effect its secondary sun's beacon gives (mapSecondarySuns.effectBeaconTypeID, named in types.jsonl "Class N <effect>
Effects"): b Black Hole, c Cataclysmic Variable, m Magnetar, p Pulsar, r Red Giant, w Wolf-Rayet, "-" none; effc (build queue 062, E2) = one
character a system, the N of that beacon's name (its strength: shattered and Drifter systems needn't match their class), "-" none; con = uint16 LE index a
system into cons (constellation names, sorted by ID), conr = uint8 a constellation into regions (region names, sorted by ID). Build 3698585:
2,604 systems, 1,038 with an effect. A change opens the same pull request as a gate change.

Encoding as tools/gen_intel_tables.py: sys = base64 of uint16 LE deltas of the sorted system IDs (the first from
30000000); edges = base64 of uint16 LE index pairs into sys, each connection once, sorted; md5 = the table's fingerprint
(here the md5 of the sorted "a-b" lines; the page keys its cached system names by it, so new systems get their names).
"""
import sys, os, re, io, json, math, base64, struct, hashlib, zipfile, tempfile, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from csp_hash import write as csp_write   # build queue 035: the page's CSP names the script by hash, so a rewrite refreshes it
args = [a for a in sys.argv[1:] if not a.startswith('--')]
def opt(name):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv): return sys.argv[i + 1]
    return None
SDE = opt('--sde'); BODY = opt('--body')
HTML = next((a for a in args if a not in (SDE, BODY, opt('--build'))), os.path.join(HERE, '..', 'index.html'))
CHECK, WRITE = '--check' in sys.argv, '--write' in sys.argv
BASE = 'https://developers.eveonline.com/static-data/tranquility'
BEGIN, END = '// ---- INTEL TABLES (tools/gen_intel_tables.py; do not edit by hand) ----', '// ---- END INTEL TABLES ----'

def out(key, val):   # a GitHub Actions step output (nothing outside the Action)
    f = os.environ.get('GITHUB_OUTPUT')
    if f:
        with open(f, 'a', encoding='utf-8') as h: h.write(f'{key}={val}\n')
def summary(text):
    f = os.environ.get('GITHUB_STEP_SUMMARY')
    if f:
        with open(f, 'a', encoding='utf-8') as h: h.write(text + '\n')

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'threat-vector jump-table check (github.com/gitlaloosh/threatvector)'})
    with urllib.request.urlopen(req, timeout=300) as r: return r.read()

def latest_build(text):
    for line in text.splitlines():
        if line.strip():
            o = json.loads(line)
            if o.get('_key') == 'sde': return int(o['buildNumber'])
    raise SystemExit('latest.jsonl has no "sde" record')

# ---- CCP's data: the build, the gates, the system names ----
def read_sde():
    files = {}
    if SDE and os.path.isdir(SDE):
        for n in ('mapStargates.jsonl', 'mapSolarSystems.jsonl', 'mapRegions.jsonl', 'mapConstellations.jsonl', 'mapSecondarySuns.jsonl', 'latest.jsonl'):
            p = os.path.join(SDE, n)
            if os.path.exists(p): files[n] = open(p, encoding='utf-8').read()
        tp = os.path.join(SDE, 'types.jsonl')
        types_lines = (lambda: open(tp, encoding='utf-8')) if os.path.exists(tp) else None
        build = latest_build(files['latest.jsonl']) if 'latest.jsonl' in files else int(opt('--build') or 0)
    else:
        if SDE: build, blob = int(opt('--build') or 0), open(SDE, 'rb').read()
        else:
            build = latest_build(fetch(f'{BASE}/latest.jsonl').decode('utf-8'))
            blob = fetch(f'{BASE}/eve-online-static-data-{build}-jsonl.zip')
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            for n in ('mapStargates.jsonl', 'mapSolarSystems.jsonl', 'mapRegions.jsonl', 'mapConstellations.jsonl', 'mapSecondarySuns.jsonl'): files[n] = z.read(n).decode('utf-8')
        zb = blob
        types_lines = lambda: io.TextIOWrapper(zipfile.ZipFile(io.BytesIO(zb)).open('types.jsonl'), encoding='utf-8')
    conns, gates = set(), 0
    for line in files['mapStargates.jsonl'].splitlines():
        if not line.strip(): continue
        g = json.loads(line); a = g['solarSystemID']; c = g['destination']['solarSystemID']; gates += 1
        assert a != c, g
        conns.add((min(a, c), max(a, c)))
    names, info, regions, jsys = {}, {}, {}, {}
    for line in files.get('mapSolarSystems.jsonl', '').splitlines():
        if line.strip():
            o = json.loads(line); k = int(o['_key']); names[k] = (o.get('name') or {}).get('en', str(k))
            if WH_LO <= k < WH_HI: jsys[k] = (names[k], int(o['constellationID']), int(o['regionID']), o.get('wormholeClassID'))
            if o.get('position2D') is not None:
                p = o.get('position') or {}
                info[k] = (o['position2D']['x'], o['position2D']['y'], float(o['securityStatus']), int(o['regionID']), tuple(p.get(a) for a in 'xyz'))
    rcls = {}
    for line in files.get('mapRegions.jsonl', '').splitlines():
        if line.strip():
            o = json.loads(line); regions[int(o['_key'])] = (o.get('name') or {}).get('en', str(o['_key'])); rcls[int(o['_key'])] = o.get('wormholeClassID')
    assert gates == 2 * len(conns), f'{gates} gates, {len(conns)} connections: a gate without its other end'
    wh = read_wh(files, jsys, regions, rcls, types_lines)
    return build, conns, names, gates, info, regions, wh

# ---- 048: the wormhole systems (INTEL_WH)
WH_LO, WH_HI = 31000000, 32000000
WH_CLS = {1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 12: 't', 13: 's', 14: 'd', 15: 'd', 16: 'd', 17: 'd', 18: 'd'}
WH_EFF = {'Black Hole': 'b', 'Cataclysmic Variable': 'c', 'Magnetar': 'm', 'Pulsar': 'p', 'Red Giant': 'r', 'Wolf Rayet': 'w'}
def read_wh(files, jsys, regions, rcls, types_lines):
    if not jsys: return None   # a copy without mapSolarSystems.jsonl
    cons, ccls = {}, {}
    for line in files.get('mapConstellations.jsonl', '').splitlines():
        if line.strip():
            o = json.loads(line); k = int(o['_key']); cons[k] = ((o.get('name') or {}).get('en', str(k)), int(o['regionID'])); ccls[k] = o.get('wormholeClassID')
    beacon = {}
    for line in files.get('mapSecondarySuns.jsonl', '').splitlines():
        if line.strip():
            o = json.loads(line)
            if WH_LO <= int(o['solarSystemID']) < WH_HI and o.get('effectBeaconTypeID'): beacon[int(o['solarSystemID'])] = int(o['effectBeaconTypeID'])
    bname = {}
    if beacon:
        assert types_lines, 'types.jsonl is needed to name the wormhole effects'
        want = set(beacon.values())
        with types_lines() as fh:
            for line in fh:
                if not line.strip() or not any(f'"_key": {b},' in line or f'"_key":{b},' in line for b in want): continue
                o = json.loads(line)
                if int(o['_key']) in want: bname[int(o['_key'])] = (o.get('name') or {}).get('en', '')
    ids = sorted(jsys); cls, eff, effc = [], [], []
    for k in ids:
        nm, c, r, own = jsys[k]
        v = own or ccls.get(c) or rcls.get(r)
        assert v in WH_CLS, f'{nm}: wormhole class {v!r}'
        cls.append(WH_CLS[v])
        if k in beacon:
            mm_ = re.fullmatch(r'Class (\d) (.+) Effects', bname.get(beacon[k], ''))
            assert mm_ and mm_.group(2) in WH_EFF, f'{nm}: effect beacon {beacon[k]} {bname.get(beacon[k])!r}'
            eff.append(WH_EFF[mm_.group(2)]); effc.append(mm_.group(1))   # 062 (E2): the beacon's own class sets the strength (shattered and Drifter systems included)
        else: eff.append('-'); effc.append('-')
    cids = sorted({jsys[k][1] for k in ids}); ci = {c: i for i, c in enumerate(cids)}
    rids = sorted({cons[c][1] for c in cids}); ri = {r: i for i, r in enumerate(rids)}
    assert len(cids) < 65536 and len(rids) < 256 and all('|' not in jsys[k][0] for k in ids)
    d = [ids[0] - WH_LO] + [ids[i] - ids[i - 1] for i in range(1, len(ids))]
    assert all(0 <= v < 65536 for v in d)
    b64 = lambda f, a: base64.b64encode(struct.pack('<%d%s' % (len(a), f), *a)).decode()
    return {'systems': len(ids), 'sys': b64('H', d), 'names': '|'.join(jsys[k][0] for k in ids), 'cls': ''.join(cls), 'eff': ''.join(eff), 'effc': ''.join(effc),
            'con': b64('H', [ci[jsys[k][1]] for k in ids]), 'cons': [cons[c][0] for c in cids], 'conr': b64('B', [ri[cons[c][1]] for c in cids]),
            'regions': [regions.get(r, str(r)) for r in rids]}

# ---- the page's table ----
src = open(HTML, encoding='utf-8').read()
m = re.search(re.escape(BEGIN) + r'\n(.*?)\n' + re.escape(END), src, re.S)
if not m: sys.exit('index.html has no INTEL TABLES block')
mm = re.search(r'^const INTEL_JUMPS = (.*);$', m.group(1), re.M)
J = json.loads(mm.group(1))
def decode(t):
    d = struct.unpack('<%dH' % (len(base64.b64decode(t['sys'])) // 2), base64.b64decode(t['sys']))
    e = struct.unpack('<%dH' % (len(base64.b64decode(t['edges'])) // 2), base64.b64decode(t['edges']))
    S, prev = [], 30000000
    for x in d: prev += x; S.append(prev)
    return {(S[e[i]], S[e[i + 1]]) for i in range(0, len(e), 2)}
def encode(conns, build):
    S = sorted({s for c in conns for s in c}); at = {s: i for i, s in enumerate(S)}
    prev, deltas = 30000000, []
    for s in S:
        d = s - prev; assert 0 < d < 65536, d; deltas.append(d); prev = s
    pairs = []
    for a, c in sorted(conns): pairs += [at[a], at[c]]
    assert len(S) < 65536
    md5 = hashlib.md5(''.join(f'{a}-{c}\n' for a, c in sorted(conns)).encode()).hexdigest()
    return {'build': build, 'md5': md5, 'n': len(conns), 'systems': len(S),
            'sys': base64.b64encode(struct.pack('<%dH' % len(deltas), *deltas)).decode(),
            'edges': base64.b64encode(struct.pack('<%dH' % len(pairs), *pairs)).decode()}
# v2026.11.02.4: the map's table, aligned to the jump table's sorted systems (see the top)
LY_M, P3U = 9.46e15, 0.0001   # CCP's light-year in metres; the position table's unit in light-years (v2026.11.04.1)
def jr(v): return math.floor(v + 0.5)   # half up, as JavaScript's Math.round (Python's round() rounds half to even)
def sec_band(v): return 0 if v <= 0.0 else 1 if v < 0.45 else 2   # 047: CCP's route guide's lines, on the unrounded value
# Build queue 063 (roadmap/security-shown-plan.md; LESSON #170): the tenth the game shows, worked out here once from CCP's unrounded
# securityStatus, so the page never rounds security again. The rule: the nearest tenth, except anything above 0.0 and below 0.05 shows 0.1
# (checked in game 2026-11-20 on 10 systems, the owner's screenshots and his checks: section 2 of the plan).
# A value on a halfway point (it reads x.x5000 at five decimals) could go either way in the game, so the tenth the owner saw there is kept
# in SEC_CHECKED_IN_GAME; one that isn't takes the nearest tenth and is named at the top of the pull request "to check in game" (the
# owner at the 063 review: "yes, the second.", over failing the run, which would also hold back that build's stargate changes).
SEC_TIE = 5e-6   # in security units: A2V6-6 (-0.85000008) and A-5M31 (-0.15000151) are ties; 2JJ-0E (-0.6500063) and KW-OAM (-0.6499916) aren't
SEC_CHECKED_IN_GAME = {30004550: -9, 30004544: -2}   # A2V6-6 -0.9, A-5M31 -0.2 (the owner, in game, 2026-11-20)
SEC_SAMPLES = {30000585: -6, 30000645: -6, 30000307: -3, 30000617: -1, 30000784: -5, 30002063: 2, 30000051: 6,   # the owner's 7 screenshots
               30002420: 1, 30004550: -9, 30004544: -2}   # Egbinger 0.1, A2V6-6 -0.9, A-5M31 -0.2 (his checks in game, 2026-11-20)
def sec_tie(v): return abs(v * 10 - math.floor(v * 10) - 0.5) * 0.1 < SEC_TIE
def shown_tenth(v, sid=None, flagged=None):
    if sid in SEC_CHECKED_IN_GAME: return SEC_CHECKED_IN_GAME[sid]
    if 0.0 < v < 0.05: return 1
    t = jr(v * 10)
    if sec_tie(v) and flagged is not None and not (v > 0 and t == 1): flagged.append((sid, v, t))   # above 0.0 the other way is 0.0, never shown
    return int(t) + 0   # + 0: -0 is 0
def tenth_band(t): return 0 if t <= 0 else 1 if t < 5 else 2   # the route planner's lines, read from the shown tenth (the page's itRpBand)
def old_shown(s, b):   # what the page showed from the old columns (sec in hundredths, band): 058's itMapSecT, for the pull request's list
    if s <= 0: return int(jr(s / 10)) + 0
    t = max(1, min(10, jr(s / 10)))
    return 4 if t >= 5 and b == 1 else t
def unpack_band(t, n):   # 047's band column, read back from a page made before 063 (the pull request's list of what it showed)
    b = base64.b64decode(t); return [(b[i >> 2] >> ((i & 3) * 2)) & 3 for i in range(n)]
if '--self-test' in sys.argv:   # 063: the rule's cases (the plan's C1), offline
    fl, bad = [], []
    for v, want in ((0.0346, 1), (0.0, 0), (-0.0, 0), (-0.04, 0), (-0.0503, -1), (0.4499, 4), (0.45007, 5), (-0.55004, -6), (0.94591, 9),
                    (1.0, 10), (-1.0, -10), (0.6491367, 6), (-0.5513124, -6), (-0.5500394, -6), (-0.2554699, -3), (0.1518976, 2)):
        if shown_tenth(v, None, fl) != want: bad.append(f'{v} shows {shown_tenth(v)}, not {want}')
    if fl: bad.append(f'flagged as halfway though none is: {fl}')
    for sid, v, want in ((30004550, -0.85000008, -9), (30004544, -0.15000151, -2)):   # checked in game: never flagged, the owner's tenth
        f2 = []
        if shown_tenth(v, sid, f2) != want or f2: bad.append(f'{sid}: {shown_tenth(v, sid, f2)}, flagged {f2}')
    for v, want in ((-0.75000002, -7), (0.35000004, 4), (0.04999999, 1)):   # a new halfway value: the nearest tenth, flagged (0.05 isn't: 0.0 never shows)
        f3 = []; t = shown_tenth(v, 1, f3)
        if (want == 1 and f3) or (want != 1 and (t != jr(v * 10) or len(f3) != 1)): bad.append(f'{v}: {t}, flagged {f3}')
    for v in (-0.6500063, -0.6499916): # 2JJ-0E, KW-OAM: close, not halfway (they read -0.65001 / -0.64999 at five decimals)
        if sec_tie(v): bad.append(f'{v} read as halfway')
    for t in range(-10, 11):
        v = t / 10 if t else 0.0
        if t == 1: v = 0.01
        if tenth_band(shown_tenth(v)) != sec_band(v): bad.append(f'band of {v}')
    for s, b, want in ((45, 1, 4), (45, 2, 5), (-85, 0, -8), (3, 1, 1), (-5, 0, 0), (95, 2, 10)):   # what the page showed before 063
        if old_shown(s, b) != want: bad.append(f'old_shown({s}, {b}) = {old_shown(s, b)}, not {want}')
    print('JUMP TABLE self-test: ' + ('ok' if not bad else f'{len(bad)} problem(s): ' + '; '.join(bad)))
    sys.exit(1 if bad else 0)
SEC_FLAGGED = []   # 063: (system, value, tenth) for each halfway value not in SEC_CHECKED_IN_GAME, for the pull request's text
def encode_map(conns, info, regions, build, jumps_md5):
    S = sorted({s for c in conns for s in c}); missing = [s for s in S if s not in info]
    assert not missing, f'{len(missing)} systems without a position2D: {missing[:5]}'
    rids = sorted({info[s][3] for s in S}); ri = {r: i for i, r in enumerate(rids)}
    assert len(rids) < 256
    x = [jr(info[s][0] / 1e14) for s in S]; y = [jr(info[s][1] / 1e14) for s in S]
    del SEC_FLAGGED[:]
    secT = [shown_tenth(info[s][2], s, SEC_FLAGGED) for s in S]; reg = [ri[info[s][3]] for s in S]   # 063: the tenth the game shows
    bad = [s for s, t in zip(S, secT) if tenth_band(t) != sec_band(info[s][2])]   # 063 D3: the band is the shown tenth's, exactly
    assert not bad, f'{len(bad)} systems whose shown tenth is in another band than their security: {bad[:5]}'
    assert all(-32768 <= v < 32768 for v in x + y) and all(-10 <= v <= 10 for v in secT)
    b64 = lambda f, a: base64.b64encode(struct.pack('<%d%s' % (len(a), f), *a)).decode()
    nopos = [s for s in S if None in info[s][4]]
    assert not nopos, f'{len(nopos)} systems without a position: {nopos[:5]}'
    p3 = [jr(info[s][4][a] / LY_M / P3U) for a in range(3) for s in S]   # x for every system, then y, then z
    assert all(-(1 << 23) <= v < (1 << 23) for v in p3)
    return {'build': build, 'jumps': jumps_md5, 'systems': len(S), 'x': b64('h', x), 'y': b64('h', y),
            'secT': b64('b', secT), 'reg': b64('B', reg), 'regions': [regions.get(r, str(r)) for r in rids],
            'p3': base64.b64encode(b''.join((v & 0xFFFFFF).to_bytes(3, 'little') for v in p3)).decode(), 'p3u': P3U}
def p3_values(t):   # the int24 values back (the checks and the diff count)
    b = base64.b64decode(t); return [int.from_bytes(b[i:i + 3], 'little', signed=True) for i in range(0, len(b), 3)]
mp = re.search(r'^const INTEL_MAP = (.*);$', m.group(1), re.M)
PM = json.loads(mp.group(1)) if mp else None
WBEGIN, WEND = '// ---- WORMHOLE TABLE (tools/jump_table_update.py; do not edit by hand) ----', '// ---- END WORMHOLE TABLE ----'
mw = re.search(re.escape(WBEGIN) + r'\nconst INTEL_WH = (.*);\n' + re.escape(WEND), src)
PW = json.loads(mw.group(1)) if mw else None
page = decode(J)
# the encoding round-trips: the page's own connections encode to the page's own sys and edges
t = encode(page, J['build']); assert (t['sys'], t['edges'], t['n'], t['systems']) == (J['sys'], J['edges'], J['n'], J['systems']), 'the encoding differs from gen_intel_tables.py'

try:
    build, conns, names, gates, info, regions, NW = read_sde()
except Exception as e:
    if CHECK and not SDE:   # the chain may run where CCP's site can't be reached: say so; the Action checks it twice a day
        print(f"jump table: skipped (CCP's static data not reachable from here: {type(e).__name__}); the GitHub Action checks it twice a day")
        sys.exit(0)
    raise

added, gone = sorted(conns - page), sorted(page - conns)
nm = lambda s: names.get(s, str(s))
out('build', build)
NM = encode_map(conns, info, regions, build, encode(conns, build)['md5'] if added or gone else J['md5'])   # 'jumps': the INTEL_JUMPS fingerprint it is aligned to
same_map = PM is not None and set(PM) == set(NM) and all(PM.get(k) == NM[k] for k in ('jumps', 'systems', 'x', 'y', 'secT', 'reg', 'regions', 'p3', 'p3u'))
sec_lines = []   # 063: the systems whose shown security changes, for the pull request (an old page's sec + band read as it showed them)
if not same_map:   # how many systems moved, changed security or region (a jump-table change re-aligns every row)
    if PM and PM.get('systems') == NM['systems'] and PM.get('jumps') == NM['jumps']:
        dec = lambda t, f: struct.unpack('<%d%s' % (NM['systems'], f), base64.b64decode(t))
        diff = sum(1 for k, f in (('x', 'h'), ('y', 'h'), ('reg', 'B')) for a, b in zip(dec(PM[k], f), dec(NM[k], f)) if a != b)
        if PM.get('p3') and PM.get('p3u') == NM['p3u']: diff += sum(1 for a, b in zip(p3_values(PM['p3']), p3_values(NM['p3'])) if a != b)
        elif PM.get('p3') != NM['p3']: diff += NM['systems']   # positions missing (a page from before v2026.11.04.1) or in other units
        S_ = sorted({s for c in conns for s in c}); newT = dec(NM['secT'], 'b')
        if PM.get('secT'): oldT = dec(PM['secT'], 'b')
        else:   # 063: a page from before the shown tenth: every row's column changes form; compare what it showed
            diff += NM['systems']
            ob = unpack_band(PM['band'], NM['systems']) if PM.get('band') else [None] * NM['systems']
            oldT = [old_shown(s, b) for s, b in zip(dec(PM['sec'], 'b'), ob)] if PM.get('sec') else [None] * NM['systems']
        for sid, a, b in zip(S_, oldT, newT):
            if a != b:
                if PM.get('secT'): diff += 1
                sec_lines.append(f'{nm(sid)} ({sid}): {"—" if a is None else f"{a / 10:.1f}"} → {b / 10:.1f}')
        map_msg = (f'map table: {diff} value(s) differ from build {build}' + ('' if PM.get('regions') == NM['regions'] else ', region names changed')
                   + ('' if PM.get('secT') else '; security now stored as the tenth the game shows (secT, in place of sec and band)')
                   + (f'; {len(sec_lines)} system(s) show another security' if sec_lines else ''))
    else: map_msg = 'map table: missing or made for another jump table'
    print(map_msg)
info_of = lambda sid: info.get(sid, (None, None, None))[2]
sec_flag = [f'- **to check in game:** {nm(s)} ({s}) is at {v:.8f}, on a halfway point: shown as {t / 10:.1f} (the nearest tenth). Check it in '
            f'game; if the game shows another tenth, add it to `SEC_CHECKED_IN_GAME` in `tools/jump_table_update.py`.' for s, v, t in SEC_FLAGGED]
sec_sample = [f'{nm(s)} ({s}): CCP {info_of(s):.8f} → {shown_tenth(info_of(s), s) / 10:.1f}, in game {t / 10:.1f}'
              + ('' if shown_tenth(info_of(s), s) == t else ' **(differs: CCP may have changed it; check in game)**')
              for s, t in SEC_SAMPLES.items() if info_of(s) is not None]
for s in SEC_FLAGGED: print('to check in game:', nm(s[0]), s[0], s[1])
if NW is not None: NW = dict(NW, build=build if PW is None or any(PW.get(k) != NW[k] for k in NW) else PW.get('build'))
same_wh = NW is None or PW == NW
if not same_wh:
    wh_msg = 'wormhole table: missing' if PW is None else f"wormhole table: differs from build {build} ({PW.get('systems')} → {NW['systems']} systems)"
    print(wh_msg)
if not added and not gone and same_map and same_wh:
    msg = f"jump table matches CCP's build {build}: {len(conns)} connections ({gates} gates); the page's table is from build {J['build']}"
    print(msg); summary(f'**No stargate changed.** {msg}.'); out('changed', 'false')
    sys.exit(0)
lines = ([] if same_map else sec_flag) + [f'- added: {nm(a)} – {nm(c)}' for a, c in added] + [f'- removed: {nm(a)} – {nm(c)}' for a, c in gone] + ([] if same_map else [f'- {map_msg}']) + ([] if same_wh else [f'- {wh_msg}'])
msg = (f"jump table differs from CCP's build {build}: {len(added)} connection(s) added, {len(gone)} removed" if added or gone
       else f"the map table differs from CCP's build {build} (no stargate changed)" if not same_map
       else f"the wormhole table differs from CCP's build {build} (no stargate changed)")
print(msg); print('\n'.join(lines[:40])); out('changed', 'true')
summary(f'**{msg}.**\n\n' + '\n'.join(lines))
if WRITE:
    new = encode(conns, build) if added or gone else J
    blk = m.group(1)
    blk = blk[:mm.start()] + 'const INTEL_JUMPS = ' + json.dumps(new, separators=(',', ':')) + ';' + blk[mm.end():]
    ml = 'const INTEL_MAP = ' + json.dumps(PM if same_map else NM, ensure_ascii=False, separators=(',', ':')) + ';'   # 048: kept as it is when only the wormhole table changed
    mp2 = re.search(r'^const INTEL_MAP = (.*);$', blk, re.M)
    blk = blk[:mp2.start()] + ml + blk[mp2.end():] if mp2 else blk + '\n' + ml
    out_src = src[:m.start(1)] + blk + src[m.end(1):]
    if NW is not None:   # 048: the wormhole table's own block, right after the INTEL TABLES
        wl = WBEGIN + '\nconst INTEL_WH = ' + json.dumps(NW, ensure_ascii=False, separators=(',', ':')) + ';\n' + WEND
        mw2 = re.search(re.escape(WBEGIN) + r'\n.*?\n' + re.escape(WEND), out_src, re.S)
        if mw2: out_src = out_src[:mw2.start()] + wl + out_src[mw2.end():]
        else:
            e = out_src.index(END, m.start(1)) + len(END); out_src = out_src[:e] + '\n' + wl + out_src[e:]
    open(HTML, 'w', encoding='utf-8').write(csp_write(out_src)[0])   # the CSP hash follows the new script
    print(f'written: {new["n"]} connections, {new["systems"]} systems' + (f', build {build}' if added or gone else ' (unchanged)') + f'; map table from build {build}')
    if BODY:
        sec_txt = '' if same_map else (   # 063: what the security column says, for the owner to compare with the game
            ('\n\n**Security the game shows** (`INTEL_MAP.secT`): the systems checked in game, with CCP\'s unrounded value:\n' + '\n'.join(f'- {x}' for x in sec_sample) if sec_sample else '')
            + (f'\n\n<details><summary>{len(sec_lines)} system(s) show another security (was → now)</summary>\n\n' + '\n'.join(f'- {x}' for x in sec_lines) + '\n\n</details>' if sec_lines else ''))
        open(BODY, 'w', encoding='utf-8').write(
            ('\n'.join(sec_flag) + '\n\n' if sec_flag and not same_map else '') +
            f'EVE build {build} changed the stargates, the map or the wormhole systems. This updates the page\'s jump table (`INTEL_JUMPS`), map table '
            f'(`INTEL_MAP`) and wormhole table (`INTEL_WH`) in index.html from CCP\'s published static data; nothing else changes.\n\n' + '\n'.join(lines) +
            sec_txt + f'\n\nThe table now has {new["n"]} connections between {new["systems"]} systems. Made by '
            f'`.github/workflows/jump-table.yml` with `tools/jump_table_update.py`. After merging, run `git pull` before your next commit.\n')
sys.exit(1 if CHECK else 0)
