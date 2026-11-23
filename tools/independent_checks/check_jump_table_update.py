"""tools/jump_table_update.py (the GitHub Action's jump-table check, v2026.10.29.5) on made-up copies of CCP's data.

    python3 -I tools/independent_checks/check_jump_table_update.py [index.html]   -> 'JUMP TABLE UPDATE: N problems' (must be 0)

The Action can't be run here (CCP's site isn't reachable from the cloud workspace), so its script is run on CCP's file
layout built from the page's own table: mapStargates.jsonl (one record per gate, each connection as two gates with
solarSystemID and destination.solarSystemID, as in CCP's file), mapSolarSystems.jsonl (names), latest.jsonl (the build).
  * the same gates on a newer build: "matches", changed=false, the page untouched, exit 0 (--check too);
  * one connection removed and one added (to a new system): changed=true and the build as step outputs, the two
    named in the pull request's text, the page's table rewritten; read back it has exactly the new connections and the
    same encoding as tools/gen_intel_tables.py (sys/edges round-trip); --check then exits 1 on the old page;
  * the rewritten page passes the check against the same data (nothing to do the next time).
v2026.11.02.4 (the Intel map): mapSolarSystems.jsonl also carries position2D, securityStatus and regionID, and mapRegions.jsonl the
region names, made from the page's own INTEL_MAP, so:
  * with the same data the map matches too; after a gate change INTEL_MAP is rewritten with INTEL_JUMPS, aligned to its new
    fingerprint and systems (a new system gets its position);
  * one system moved on CCP's map with no gate changed: changed=true, the pull request says the map changed, only INTEL_MAP
    rewritten (that system's position, nothing else), --check exits 1 before and 0 after.
v2026.11.04.1 (light-years in the map's hover): mapSolarSystems.jsonl also carries each system's geographic position (3D,
metres), made here from the page's own INTEL_MAP.p3 with CCP's light-year (9.46e15 m) written out in this check, so:
  * the same data still matches (a script using another light-year, or another unit, fails here);
  * one system moved in space only (position2D unchanged): changed=true, only that system's x, y, z rewritten (3 values);
  * a page from before (INTEL_MAP without p3): changed=true, the positions added, every other value of INTEL_MAP unchanged;
  * a system with no position in CCP's data: the script stops (exit not 0) and the page is untouched.
Build queue 035 (main's CSP hash went stale after a "Game data" pull request): every page the script rewrites passes
tools/csp_hash.py --check (the CSP names the script by hash); a copy of the script without that refresh fails here.
Build queue 063 (roadmap/security-shown-plan.md): INTEL_MAP.secT, the tenth the game shows, in place of sec and band. The made-up
securities are worked out from the page's secT, and the tenth expected from them by the plan's rule written out here (IN_GAME: the owner's
two checks). 065a: the page has had secT since the data pull request (#77), so the case of a page from before 063 (sec + band, converted by
the first run) is gone with the page's own fallback; a page without secT is refused here. So:
  * one system's security crosses a tenth (0.5 to 0.449): only its secT rewritten, named in the pull request;
  * a new system on a halfway point: written with the nearest tenth, named at the top of the pull request to check in game (D4);
  * the systems checked in game keep the owner's tenth on their halfway values, unflagged; 0.0346 shows 0.1; a copy of the script without
    the 0.0-0.05 line is caught.
"""
import sys, os, re, json, math, base64, struct, subprocess, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
HTML = next((a for a in sys.argv[1:] if not a.startswith('--')), os.path.join(ROOT, 'index.html'))
SCRIPT = os.path.join(ROOT, 'tools', 'jump_table_update.py')
problems = []
def check(ok, msg):
    print(('OK   ' if ok else 'FAIL ') + msg)
    if not ok: problems.append(msg)

CSP = os.path.join(ROOT, 'tools', 'csp_hash.py')
def csp_ok(path):   # the page's CSP hash fits its script (build queue 035)
    return subprocess.run([sys.executable, '-I', CSP, '--check', path], capture_output=True, text=True).returncode == 0
def table(path):
    s = open(path, encoding='utf-8').read()
    return json.loads(re.search(r'^const INTEL_JUMPS = (.*);$', s, re.M).group(1))
def conns_of(J):
    d = struct.unpack('<%dH' % (len(base64.b64decode(J['sys'])) // 2), base64.b64decode(J['sys']))
    e = struct.unpack('<%dH' % (len(base64.b64decode(J['edges'])) // 2), base64.b64decode(J['edges']))
    S, p = [], 30000000
    for x in d: p += x; S.append(p)
    return {(S[e[i]], S[e[i + 1]]) for i in range(0, len(e), 2)}, S
def mtable(path):
    s = open(path, encoding='utf-8').read(); m = re.search(r'^const INTEL_MAP = (.*);$', s, re.M)
    return json.loads(m.group(1)) if m else None
M0 = mtable(HTML)
LY_M, P3U = 9.46e15, 0.0001   # CCP's light-year (developers.eveonline.com map-data guide), the table's unit (the plan)
def p3_of(M):   # INTEL_MAP.p3 -> [x..., y..., z...] (int24 LE, signed), independently of the script
    b = base64.b64decode(M['p3']); return [int.from_bytes(b[i:i + 3], 'little', signed=True) for i in range(0, len(b), 3)]
def m_rows(M, S):   # system id -> (x, y, shown tenth, region index, (px, py, pz) in 0.0001 LY), from the page's INTEL_MAP aligned to S
    dec = lambda k, f: struct.unpack('<%d%s' % (M['systems'], f), base64.b64decode(M[k]))
    n = M['systems']; P = p3_of(M) if M.get('p3') else [0] * (3 * n)
    T = dec('secT', 'b')   # build queue 063: the tenth the game shows, stored as is
    return {s: v for s, v in zip(S, zip(dec('x', 'h'), dec('y', 'h'), T, dec('reg', 'B'), ((P[k], P[n + k], P[2 * n + k]) for k in range(n))))}
jr = lambda v: math.floor(v + 0.5)   # half up, as the page's Math.round
# 063: the owner's checks in game (2026-11-20), written out here, not read from the script: A2V6-6 -0.9 and A-5M31 -0.2 on a halfway point
IN_GAME = {30004550: -9, 30004544: -2}
def tenth(v, s=None):   # the tenth the game shows (the plan's rule), worked out here
    if s in IN_GAME: return IN_GAME[s]
    return 1 if 0 < v < 0.05 else int(jr(v * 10)) + 0
def vals_of(M, S):   # a made-up unrounded security for each system that the script must show as the page shows it
    dec = lambda k, f: struct.unpack('<%d%s' % (M['systems'], f), base64.b64decode(M[k]))
    return {s: t / 10 for s, t in zip(S, dec('secT', 'b'))}
def sde(folder, conns, systems, build, rows=None, regions=None, nopos=(), vals=None):
    os.makedirs(folder, exist_ok=True); L, g = [], 50000000
    for a, c in sorted(conns):
        L.append(json.dumps({'_key': g, 'destination': {'solarSystemID': c, 'stargateID': g + 1}, 'solarSystemID': a, 'typeID': 16}))
        L.append(json.dumps({'_key': g + 1, 'destination': {'solarSystemID': a, 'stargateID': g}, 'solarSystemID': c, 'typeID': 16})); g += 2
    open(os.path.join(folder, 'mapStargates.jsonl'), 'w', encoding='utf-8').write('\r\n'.join(L) + '\r\n')   # CRLF, as CCP's latest.jsonl
    rows = rows or {}; regions = regions or ['Region A']; vals = vals or {}
    def rec(s):
        x, y, _t, rg, p = rows.get(s, (0, 0, 5, 0, (0, 0, 0)))
        o = {'_key': s, 'name': {'en': f'SYS-{s - 30000000}'}, 'position2D': {'x': x * 1e14, 'y': y * 1e14}, 'securityStatus': vals.get(s, 0.5), 'regionID': 10000001 + rg}
        if s not in nopos: o['position'] = {a: v * P3U * LY_M for a, v in zip('xyz', p)}   # metres, as CCP's file
        return o
    open(os.path.join(folder, 'mapSolarSystems.jsonl'), 'w', encoding='utf-8').write('\n'.join(json.dumps(rec(s)) for s in sorted(systems)) + '\n')
    open(os.path.join(folder, 'mapRegions.jsonl'), 'w', encoding='utf-8').write('\n'.join(json.dumps({'_key': 10000001 + k, 'name': {'en': r}}) for k, r in enumerate(regions)) + '\n')
    open(os.path.join(folder, 'latest.jsonl'), 'w', encoding='utf-8').write(json.dumps({'_key': 'sde', 'buildNumber': build, 'releaseDate': '2026-10-29T11:10:30Z'}) + '\r\n')
def run(page, folder, *extra, env=None, script=None):
    e = dict(os.environ); e.pop('GITHUB_OUTPUT', None); e.pop('GITHUB_STEP_SUMMARY', None); e.update(env or {})
    r = subprocess.run([sys.executable, '-I', script or SCRIPT, page, '--sde', folder, *extra], capture_output=True, text=True, env=e, timeout=300)
    return r.returncode, r.stdout + r.stderr
def put_map(path, src, M):   # a copy of the page with another INTEL_MAP
    open(path, 'w', encoding='utf-8').write(re.sub(r'^const INTEL_MAP = .*;$', lambda m_: 'const INTEL_MAP = ' + json.dumps(M, ensure_ascii=False, separators=(',', ':')) + ';', src, count=1, flags=re.M))

J0 = table(HTML); C0, S0 = conns_of(J0)
tmp = tempfile.mkdtemp(prefix='jtu-')
try:
    out_f, sum_f, body = os.path.join(tmp, 'out.txt'), os.path.join(tmp, 'summary.md'), os.path.join(tmp, 'pr.md')
    GH = {'GITHUB_OUTPUT': out_f, 'GITHUB_STEP_SUMMARY': sum_f}
    def fresh(): open(out_f, 'w').close(); os.path.exists(body) and os.remove(body)
    check(M0 is not None and M0['jumps'] == J0['md5'] and M0['systems'] == len(S0), "the page's INTEL_MAP is aligned to its INTEL_JUMPS")
    check(bool(M0 and M0.get('secT')) and not ({'sec', 'band'} & set(M0 or {})), "the page's INTEL_MAP holds secT only (063), no sec or band (065a: the fallback is gone)")
    if not (M0 and M0.get('secT')): raise SystemExit(1)
    R0 = m_rows(M0, S0); V0 = vals_of(M0, S0); REG = M0['regions']
    check(M0.get('p3u') == P3U and len(p3_of(M0)) == 3 * len(S0) and max(abs(v) for v in p3_of(M0)) < 1 << 23 and len({R0[s][4] for s in S0}) > len(S0) - 5,
          f"the page's INTEL_MAP holds every system's position in space (p3, units {M0.get('p3u')} LY, {len(p3_of(M0)) if M0.get('p3') else 0} values)")
    check(all(tenth(V0[s], s) == R0[s][2] for s in S0), "the made-up securities show what the page shows (before the script runs)")
    same = os.path.join(tmp, 'same'); sde(same, C0, S0, J0['build'] + 5063, R0, REG, vals=V0)
    BASE_HTML = HTML
    base_src = open(BASE_HTML, encoding='utf-8').read()
    gone = sorted(C0)[0]; new_sys = 30100000; added = (S0[5], new_sys)
    C1 = (C0 - {gone}) | {added}
    changed = os.path.join(tmp, 'changed'); sde(changed, C1, set(S0) | {new_sys}, J0['build'] + 5100, R0, REG, vals=V0)
    moved = os.path.join(tmp, 'moved'); mv = S0[7]; R2 = dict(R0); R2[mv] = (R0[mv][0] + 3, R0[mv][1] - 2) + R0[mv][2:]
    sde(moved, C0, S0, J0['build'] + 5200, R2, REG, vals=V0)
    page = os.path.join(tmp, 'index.html'); shutil.copy(BASE_HTML, page); before = open(page, encoding='utf-8').read()

    fresh(); rc, o = run(page, same, '--write', '--body', body, env=GH)
    outs = open(out_f).read() if os.path.exists(out_f) else ''
    check(rc == 0 and o.strip().splitlines()[-1].startswith('jump table matches') and 'changed=false' in outs and open(page, encoding='utf-8').read() == before and not os.path.exists(body),
          f'the same gates on a newer build: matches, changed=false, the page untouched, no pull request text ({o.strip().splitlines()[-1]!r}; {outs.split()})')
    rc2, _ = run(page, same, '--check')
    check(rc2 == 0, f'--check on the same gates exits 0 ({rc2})')

    rc3, _ = run(page, changed, '--check')
    check(rc3 == 1, f'--check with a gate changed exits 1 ({rc3})')
    fresh(); rc4, o4 = run(page, changed, '--write', '--body', body, env=GH)
    outs = open(out_f).read(); txt = open(body, encoding='utf-8').read() if os.path.exists(body) else ''
    check(rc4 == 0 and 'changed=true' in outs and f'build={J0["build"] + 5100}' in outs, f'a gate changed: changed=true and the build as step outputs {outs.split()}')
    check(f'- added: SYS-{S0[5] - 30000000} – SYS-100000' in txt and f'- removed: SYS-{gone[0] - 30000000} – SYS-{gone[1] - 30000000}' in txt and 'git pull' in txt,
          f"the pull request's text names the connection added and the one removed {txt.splitlines()[2:4]}")
    J1 = table(page); C1r, _ = conns_of(J1)
    check(C1r == C1 and J1['build'] == J0['build'] + 5100 and J1['n'] == len(C1) and J1['systems'] == len({s for c in C1 for s in c}),
          f"the page's table rewritten: exactly the new connections, the new build ({J1['n']} connections, {J1['systems']} systems, build {J1['build']})")
    after = open(page, encoding='utf-8').read()
    strip = lambda s: re.sub(r'<meta http-equiv="Content-Security-Policy" content="[^"]*">', '', re.sub(r'^const INTEL_(JUMPS|MAP) = .*;$', '', s, flags=re.M))
    check(csp_ok(page), 'a gate changed: the rewritten page\'s CSP hash fits its script (csp_hash --check)')
    M1 = mtable(page); S1 = conns_of(J1)[1]; R1 = m_rows(M1, S1)
    check(strip(after) == strip(before) and M1['jumps'] == J1['md5'] and M1['systems'] == J1['systems'] and R1[new_sys] == R0.get(new_sys, (0, 0, 5, 0, (0, 0, 0))) and all(R1[s] == R0[s] for s in S0 if s in R1),
          'only INTEL_JUMPS and INTEL_MAP changed in the page; the map re-aligned to the new table (every system keeps its own place)')
    rc5, o5 = run(page, changed, '--check')
    check(rc5 == 0 and 'matches' in o5, f'the rewritten page against the same data: nothing to do ({rc5})')
    # one system moved on CCP's map, no gate changed
    page2 = os.path.join(tmp, 'index2.html'); shutil.copy(BASE_HTML, page2)
    rc6, _ = run(page2, moved, '--check')
    fresh(); rc7, o7 = run(page2, moved, '--write', '--body', body, env=GH)
    outs = open(out_f).read(); txt = open(body, encoding='utf-8').read() if os.path.exists(body) else ''
    a2 = open(page2, encoding='utf-8').read(); M2 = mtable(page2); R2r = m_rows(M2, S0)
    check(rc6 == 1 and rc7 == 0 and 'changed=true' in outs and 'map table: 2 value(s) differ' in txt and 'map' in txt.splitlines()[0],
          f'a system moved on the map, no gate changed: --check exits 1, changed=true, the pull request says the map changed ({rc6}, {outs.split()}, {[l for l in txt.splitlines() if "map" in l][:2]})')
    nomap = lambda t: re.sub(r'<meta http-equiv="Content-Security-Policy" content="[^"]*">', '', re.sub(r'^const INTEL_MAP = .*;$', '', t, flags=re.M))
    check(csp_ok(page2), 'a system moved: the rewritten page\'s CSP hash fits its script (csp_hash --check)')
    check(nomap(a2) == nomap(base_src) and R2r == R2, 'only INTEL_MAP rewritten: that system moved, nothing else')
    rc8, o8 = run(page2, moved, '--check')
    check(rc8 == 0, f'the rewritten page against the same data: nothing to do ({rc8})')
    # v2026.11.04.1: one system moved in space only (its flat-map place unchanged)
    sp = os.path.join(tmp, 'space'); sv = S0[11]; R3 = dict(R0); x3, y3, z3 = R0[sv][4]; R3[sv] = R0[sv][:4] + ((x3 + 17, y3 - 4, z3 + 250),)
    sde(sp, C0, S0, J0['build'] + 5300, R3, REG, vals=V0)
    page3 = os.path.join(tmp, 'index3.html'); shutil.copy(BASE_HTML, page3); fresh()
    rc9, _ = run(page3, sp, '--check')
    rc10, o10 = run(page3, sp, '--write', '--body', body, env=GH)
    M3 = mtable(page3); R3r = m_rows(M3, S0)
    check(rc9 == 1 and rc10 == 0 and 'map table: 3 value(s) differ' in o10 and R3r == R3 and all(M3[k] == M0[k] for k in ('x', 'y', 'secT', 'reg', 'regions')),
          f'a system moved in space only: --check exits 1, its x, y, z rewritten (3 values), nothing else ({rc9}, {rc10}, {[l for l in o10.splitlines() if "map table" in l][:1]})')
    # 063: one system's security crosses a tenth (0.5 to 0.449, high sec to low): only its secT changes (1 value), listed in the pull request
    bv = next(x for x in S0 if R0[x][2] == 5 and x not in IN_GAME); V4 = dict(V0); V4[bv] = 0.449; R4 = dict(R0); R4[bv] = R0[bv][:2] + (4,) + R0[bv][3:]
    bd = os.path.join(tmp, 'tenth'); sde(bd, C0, S0, J0['build'] + 5400, R0, REG, vals=V4)
    page4 = os.path.join(tmp, 'index4.html'); shutil.copy(BASE_HTML, page4); fresh()
    rc11, _ = run(page4, bd, '--check')
    rc12, o12 = run(page4, bd, '--write', '--body', body, env=GH)
    M4 = mtable(page4); R4r = m_rows(M4, S0); txt = open(body, encoding='utf-8').read() if os.path.exists(body) else ''
    check(rc11 == 1 and rc12 == 0 and 'map table: 1 value(s) differ' in o12 and R4r == R4 and all(M4[k] == M0[k] for k in ('x', 'y', 'reg', 'regions', 'p3'))
          and f'SYS-{bv - 30000000} ({bv}): 0.5 → 0.4' in txt and '1 system(s) show another security' in txt,
          f'a security change across a tenth: --check exits 1, only its secT rewritten, named in the pull request ({rc11}, {rc12}, {[l for l in o12.splitlines() if "map table" in l][:1]})')
    # 063 D4: a new system on a halfway point (not checked in game): the nearest tenth, still written, named first in the pull request
    hv = next(x for x in S0 if R0[x][2] == 3 and x not in IN_GAME); V5 = dict(V0); V5[hv] = 0.35000002; R5 = dict(R0); R5[hv] = R0[hv][:2] + (4,) + R0[hv][3:]
    hd = os.path.join(tmp, 'half'); sde(hd, C0, S0, J0['build'] + 5500, R0, REG, vals=V5)
    page5 = os.path.join(tmp, 'index5h.html'); shutil.copy(BASE_HTML, page5); fresh()
    rc13, o13 = run(page5, hd, '--write', '--body', body, env=GH)
    txt = open(body, encoding='utf-8').read() if os.path.exists(body) else ''; outs = open(out_f).read()
    check(rc13 == 0 and 'changed=true' in outs and m_rows(mtable(page5), S0) == R5 and txt.startswith(f'- **to check in game:** SYS-{hv - 30000000} ({hv})') and 'shown as 0.4' in txt,
          f'a new system on a halfway point: written with the nearest tenth, named at the top of the pull request to check in game ({rc13}, {txt.splitlines()[:1]})')
    # 063: a system checked in game keeps the owner's tenth on its halfway value, and isn't flagged
    ck = [s for s in IN_GAME if s in R0]
    if ck:
        V6 = dict(V0); V6[30004550] = -0.85000008; V6[30004544] = -0.15000151
        V6[hv] = 0.0346   # and a value above 0.0 and below 0.05: 0.1
        R6 = dict(R0); R6[hv] = R0[hv][:2] + (1,) + R0[hv][3:]
        cd = os.path.join(tmp, 'checked'); sde(cd, C0, S0, J0['build'] + 5600, R0, REG, vals=V6)
        page6c = os.path.join(tmp, 'index6c.html'); shutil.copy(BASE_HTML, page6c); fresh()
        rc14, o14 = run(page6c, cd, '--write', '--body', body, env=GH); txt = open(body, encoding='utf-8').read() if os.path.exists(body) else ''
        R6r = m_rows(mtable(page6c), S0)
        check(rc14 == 0 and R6r == R6 and all(R6r[s][2] == IN_GAME[s] for s in ck) and 'to check in game' not in txt,
              f'the systems checked in game keep the owner\'s tenth on their halfway values, unflagged; 0.0346 shows 0.1 ({rc14}, {[R6r[s][2] for s in ck]})')
        # the mutant: the script without the "above 0.0 and below 0.05 shows 0.1" line
        mdir2 = os.path.join(tmp, 'mut2'); os.makedirs(mdir2); shutil.copy(CSP, mdir2)
        msrc = open(SCRIPT, encoding='utf-8').read(); A2 = '    if 0.0 < v < 0.05: return 1\n'
        check(A2 in msrc, 'mutant: the 0.0-0.05 line is in the script (if not, update the mutant)')
        open(os.path.join(mdir2, 'jump_table_update.py'), 'w', encoding='utf-8').write(msrc.replace(A2, ''))
        page6m = os.path.join(tmp, 'index6m.html'); shutil.copy(BASE_HTML, page6m)
        rcm, om = run(page6m, cd, '--write', script=os.path.join(mdir2, 'jump_table_update.py'))   # its band assert stops it (0.0 is null, 0.0346 low)
        check((rcm != 0 and 'in another band' in om) or m_rows(mtable(page6m), S0)[hv][2] != 1, f'mutant without the 0.0-0.05 line: caught (rc {rcm})')
    # a page from before v2026.11.04.1: no positions yet
    page7 = os.path.join(tmp, 'index7.html'); old = dict(M0); old.pop('p3'); old.pop('p3u'); put_map(page7, base_src, old)
    rc15, _ = run(page7, same, '--check'); rc16, _ = run(page7, same, '--write'); M7 = mtable(page7)
    check(rc15 == 1 and rc16 == 0 and M7.get('p3') == M0['p3'] and M7.get('p3u') == P3U and all(M7[k] == M0[k] for k in ('x', 'y', 'secT', 'reg', 'regions', 'jumps', 'systems')),
          f'a page without positions: --check exits 1, --write adds them (equal to the page\'s own), nothing else changes ({rc15}, {rc16})')
    # a system with no position in CCP's data: stop, the page untouched
    nop = os.path.join(tmp, 'nopos'); sde(nop, C0, S0, J0['build'] + 5700, R0, REG, nopos={S0[3]}, vals=V0)
    page8 = os.path.join(tmp, 'index8.html'); shutil.copy(BASE_HTML, page8)
    rc17, o17 = run(page8, nop, '--write')
    check(rc17 != 0 and 'without a position' in o17 and open(page8, encoding='utf-8').read() == base_src,
          f'a system without a position in CCP\'s data: the script stops, the page untouched ({rc17})')
    # the mutant: the script without the CSP refresh (the code before 035), run from a copy beside csp_hash.py
    mdir = os.path.join(tmp, 'mut'); os.makedirs(mdir); shutil.copy(CSP, mdir)
    msrc = open(SCRIPT, encoding='utf-8').read(); A = 'write(csp_write(out_src)[0])'   # 048: the page is built in out_src (the wormhole table's block too)
    check(A in msrc, 'mutant: the CSP refresh line is in the script (if not, update the mutant)')
    open(os.path.join(mdir, 'jump_table_update.py'), 'w', encoding='utf-8').write(msrc.replace(A, 'write(out_src)'))
    page9 = os.path.join(tmp, 'index9.html'); shutil.copy(BASE_HTML, page9)
    p = subprocess.run([sys.executable, '-I', os.path.join(mdir, 'jump_table_update.py'), page9, '--sde', changed, '--write'], capture_output=True, text=True, timeout=300,
                       env={k: v for k, v in os.environ.items() if k not in ('GITHUB_OUTPUT', 'GITHUB_STEP_SUMMARY')})
    check(p.returncode == 0 and table(page9)['build'] == J0['build'] + 5100 and not csp_ok(page9),
          f'mutant without the CSP refresh: caught (rc {p.returncode}, hash fits: {csp_ok(page9)})')
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print(f'JUMP TABLE UPDATE: {len(problems)} problems')
sys.exit(1 if problems else 0)
