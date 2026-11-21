"""The security the map shows is the tenth the game shows, and only one function reads it (build queue 058, LESSON #170; build queue 063).

    python3 -I tools/check_sec_shown.py [index.html]   -> 'SECURITY SHOWN: ... 0 problems' (exit 1 otherwise)
    python3 -I tools/check_sec_shown.py --self-test    -> 'SECURITY SHOWN self-test: ok'

Why: INTEL_MAP.sec held CCP's security rounded to hundredths (tools/jump_table_update.py), and the page rounded it again to tenths, so 19
low-sec systems (true value just under 0.45, stored as 45) showed 0.5 in the high-sec colour (found at 058's review, 2026-11-16; the owner:
"you dont think we need to do anything further to prevent an issue like this moving forward?", then "yes"), and 333 systems in all a tenth off
(measured 2026-11-20, build queue 063). Since 063 the generator stores the tenth the game shows (INTEL_MAP.secT, in place of sec and 047's
band); until the "Jump table" workflow's data pull request brings it, the page reads sec + band as 058 did (the fallback). Checks, offline:
  1. the code: `.secT[` is read only inside itMapSecT; `.sec[` only inside itMapSecT and itRpBand (the fallback); every other reader goes
     through itMapSecT, itMapSecClass or itMapSecText (system names through itSecTab);
  2. the data, with secT: every value -10..10, the page's own itMapSecT (run in node) returns it, and the systems checked in game (SAMPLES: the
     owner's 7 screenshots, Egbinger, and the two on a halfway point) show the tenth he saw;
     without secT (the fallback): itMapSecT agrees with the band: high (2) 0.5 or more, low (1) 0.1 to 0.4, null (0) 0.0 or less.
The self-test runs mutants on the page as it is and on a copy given a made-up secT: the band line taken out, a second reader re-rounding,
a reader of `.secT[` outside itMapSecT, and a secT one tenth off on a sample (the double rounding).
"""
import base64, json, os, re, struct, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ALLOWED = {'.sec[': {'itMapSecT', 'itRpBand'}, '.secT[': {'itMapSecT'}}
# the systems checked in game (system ID -> the tenth shown), from the plan's section 2: the owner's 7 screenshots (2026-11-16), Egbinger 0.1,
# A2V6-6 -0.9 and A-5M31 -0.2 (his checks in game, 2026-11-20); the generator's SEC_CHECKED_IN_GAME holds the last two
SAMPLES = {30000585: -6, 30000645: -6, 30000307: -3, 30000617: -1, 30000784: -5, 30002063: 2, 30000051: 6, 30002420: 1, 30004550: -9, 30004544: -2}

def script_of(src):
    m = [x.group(1) for x in re.finditer(r'<script>(.*?)</script>', src, re.S)]
    return max(m, key=len) if m else ''

def readers(js):
    """(column, top-level function, line) for each read of `.sec[` / `.secT[` outside the functions allowed to read it"""
    bad = []
    for col, ok in ALLOWED.items():
        for m in re.finditer(re.escape(col), js):
            head = js.rfind('\nfunction ', 0, m.start())
            name = re.match(r'\nfunction (\w+)', js[head:]).group(1) if head >= 0 else '(top level)'
            # the reader must still be inside that function: no other top-level line start ("\n" + a letter, not an indent) between them
            between = js[head + 1:m.start()] if head >= 0 else js[:m.start()]
            if re.search(r'\n(?:const|let|var|function|//)', between): name = '(top level)'
            if name not in ok: bad.append((col, name, js.count('\n', 0, m.start()) + 1))
    return bad

def ids_of(src):
    J = json.loads(re.search(r'\nconst INTEL_JUMPS = (\{.*?\});\n', src, re.S).group(1))
    d = struct.unpack('<%dH' % (len(base64.b64decode(J['sys'])) // 2), base64.b64decode(J['sys']))
    S, p = [], 30000000
    for x in d: p += x; S.append(p)
    return S

def data_check(js, src):
    fn = re.search(r'\nfunction itMapSecT\(i\)\{.*?\n\}', js, re.S)
    if not fn: return ['itMapSecT not found'], {}
    im = re.search(r'\nconst INTEL_MAP = (\{.*?\});\n', src, re.S)
    if not im: return ['INTEL_MAP not found'], {}
    M = json.loads(im.group(1)); n = M['systems']
    if 'secT' in M:
        S = ids_of(src); at = {s: i for i, s in enumerate(S)}
        pins = {str(at[s]): t for s, t in SAMPLES.items() if s in at}
        prog = ("const M = " + json.dumps({'secT': M['secT'], 'n': n, 'pins': pins}) + ";\n"
                "const secT = new Int8Array(Buffer.from(M.secT, 'base64'));\n"
                "const T = {secT, n: M.n}; function itMapTable(){ return T; }\n" + fn.group(0) + "\n"
                "const bad = [], pinBad = []; let range = 0; for(let i = 0; i < T.n; i++){ const t = itMapSecT(i);\n"
                "  if(t !== secT[i]) bad.push([i, secT[i], t]); if(!(secT[i] >= -10 && secT[i] <= 10)) range++; }\n"
                "for(const [i, w] of Object.entries(M.pins)) if(itMapSecT(Number(i)) !== w) pinBad.push([Number(i), w, itMapSecT(Number(i))]);\n"
                "console.log(JSON.stringify({form: 'secT', bad: bad.slice(0, 10), nbad: bad.length, range, pinBad, pins: Object.keys(M.pins).length, n: T.n, len: secT.length}));\n")
    else:
        if 'band' not in M: return ['INTEL_MAP has neither secT (063) nor band (047)'], {}
        prog = ("const M = " + json.dumps({'sec': M['sec'], 'band': M['band'], 'n': n}) + ";\n"
                "const sec = new Int8Array(Buffer.from(M.sec, 'base64')), bb = Buffer.from(M.band, 'base64'), band = new Uint8Array(M.n);\n"
                "for(let i = 0; i < M.n; i++) band[i] = (bb[i >> 2] >> ((i & 3) * 2)) & 3;\n"
                "const T = {secT: null, sec, band, n: M.n}; function itMapTable(){ return T; }\n" + fn.group(0) + "\n"
                "const bad = [], fixed = []; for(let i = 0; i < T.n; i++){ const t = itMapSecT(i), b = band[i];\n"
                "  if(!Number.isInteger(t) || (b === 2 && t < 5) || (b === 1 && (t < 1 || t > 4)) || (b === 0 && t > 0)) bad.push([i, sec[i], b, t]);\n"
                "  if(sec[i] === 45 && b === 1) fixed.push(i); }\n"
                "console.log(JSON.stringify({form: 'fallback', bad: bad.slice(0, 10), nbad: bad.length, fixed: fixed.length, n: T.n}));\n")
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(prog); path = f.name
    try: r = subprocess.run(['node', path], capture_output=True, text=True, timeout=60)
    finally: os.unlink(path)
    if r.returncode: return [f'node: {r.stderr.strip()[:300]}'], {}
    o = json.loads(r.stdout); probs = []
    if o['form'] == 'secT':
        if o['len'] != o['n']: probs.append(f"secT holds {o['len']} values for {o['n']} systems")
        if o['nbad']: probs.append(f"itMapSecT doesn't return the table's tenth for {o['nbad']} systems (first: {o['bad']})")
        if o['range']: probs.append(f"{o['range']} systems have a tenth outside -10..10")
        if o['pinBad']: probs.append(f"systems checked in game show another tenth ([index, in game, shown]: {o['pinBad']})")
        if o['pins'] != len(SAMPLES): probs.append(f"only {o['pins']} of the {len(SAMPLES)} systems checked in game are in the table")
    elif o['nbad']: probs.append(f"{o['nbad']} systems show a security outside their band (first: {o['bad']})")
    return probs, o

def run(path):
    src = open(path, encoding='utf-8').read(); js = script_of(src)
    probs = [f'`{col}` read in {nm} (line {ln} of the script): go through itMapSecT' for col, nm, ln in readers(js)]
    p2, o = data_check(js, src); probs += p2
    return probs, o

def with_secT(src):
    """the page with a made-up INTEL_MAP.secT in place of sec and band (058's shown tenths, the samples as checked in game), for the mutants"""
    M = json.loads(re.search(r'\nconst INTEL_MAP = (\{.*?\});\n', src, re.S).group(1)); n = M['systems']
    sec = struct.unpack('<%db' % n, base64.b64decode(M['sec'])); bb = base64.b64decode(M['band'])
    jr = lambda v: int((v + 0.5) // 1)
    def shown(s, b):
        if s <= 0: return jr(s / 10) + 0
        t = max(1, min(10, jr(s / 10))); return 4 if t >= 5 and b == 1 else t
    T = [shown(s, (bb[i >> 2] >> ((i & 3) * 2)) & 3) for i, s in enumerate(sec)]
    at = {s: i for i, s in enumerate(ids_of(src))}
    for s, t in SAMPLES.items():
        if s in at: T[at[s]] = t
    N = {k: v for k, v in M.items() if k not in ('sec', 'band')}; N['secT'] = base64.b64encode(struct.pack('<%db' % n, *T)).decode()
    return re.sub(r'\nconst INTEL_MAP = \{.*?\};\n', lambda m_: '\nconst INTEL_MAP = ' + json.dumps(N, ensure_ascii=False, separators=(',', ':')) + ';\n', src, count=1, flags=re.S), at

def self_test():
    path = os.path.join(HERE, '..', 'index.html'); src = open(path, encoding='utf-8').read()
    probs, _ = run(path)
    if probs: return [f'the page itself: {probs[0]}']
    out = []
    with tempfile.TemporaryDirectory() as d:
        def mutant(base, a, b, why, data=None):
            if a is not None and base.count(a) != 1: out.append(f'mutant not applied ({why})'); return
            p = os.path.join(d, 'm.html'); open(p, 'w', encoding='utf-8').write(data if data is not None else base.replace(a, b))
            if not run(p)[0]: out.append(f'mutant not caught: {why}')
        old = 'INTEL_MAP' in src and '"secT"' not in re.search(r'\nconst INTEL_MAP = (\{.*?\});\n', src, re.S).group(1)
        if old:   # the fallback, while the page's table has no secT
            mutant(src, "return t >= 5 && T.band && T.band[i] === 1 ? 4 : t;", "return t;", 'the band line taken out (19 low-sec systems read 0.5)')
            mutant(src, "function itMapSecClass(i){ return Math.max(0, itMapSecT(i)); }",
                   "function itMapSecClass(i){ const T = itMapTable(), s = T.sec[i]; return s <= 0 ? 0 : Math.max(1, Math.min(10, Math.round(s / 10))); }",
                   'a second reader rounding T.sec again')
            s2, at = with_secT(src)
            p = os.path.join(d, 's.html'); open(p, 'w', encoding='utf-8').write(s2)
            pr = run(p)[0]
            if pr: out.append(f'the page with a made-up secT: {pr[0]}'); return out
        else: s2, at = src, {s: i for i, s in enumerate(ids_of(src))}
        mutant(s2, "function itMapSecClass(i){ return Math.max(0, itMapSecT(i)); }",
               "function itMapSecClass(i){ const T = itMapTable(); return Math.max(0, T.secT[i]); }", 'a reader of secT outside itMapSecT')
        mutant(s2, "  if(T.secT) return T.secT[i];\n", "  if(T.secT) return T.secT[i] === -9 ? -8 : T.secT[i];\n",
               'itMapSecT not returning the table\'s tenth (A2V6-6 at -0.8, the double rounding)')
        M = json.loads(re.search(r'\nconst INTEL_MAP = (\{.*?\});\n', s2, re.S).group(1)); T = list(struct.unpack('<%db' % M['systems'], base64.b64decode(M['secT'])))
        T[at[30000142]] = 10   # Jita 1.0: what the double rounding showed (game 0.9) -- not a sample, so only a sample can catch the same slip
        T[at[30000051]] = 7    # Juddi 0.7 (game 0.6): a sample
        M['secT'] = base64.b64encode(struct.pack('<%db' % M['systems'], *T)).decode()
        mutant(s2, None, None, 'a secT a tenth off on a system checked in game (Juddi 0.7)',
               data=re.sub(r'\nconst INTEL_MAP = \{.*?\};\n', lambda m_: '\nconst INTEL_MAP = ' + json.dumps(M, ensure_ascii=False, separators=(',', ':')) + ';\n', s2, count=1, flags=re.S))
    return out

if __name__ == '__main__':
    if '--self-test' in sys.argv:
        bad = self_test(); print('\n'.join(bad)); print('SECURITY SHOWN self-test: ' + ('ok' if not bad else f'{len(bad)} problems')); sys.exit(1 if bad else 0)
    path = next((a for a in sys.argv[1:] if not a.startswith('-')), os.path.join(HERE, '..', 'index.html'))
    probs, o = run(path)
    for p in probs: print('PROBLEM: ' + p)
    if o.get('form') == 'secT':
        print(f"SECURITY SHOWN: {o.get('n', '?')} systems, the table's tenth (secT), {o.get('pins', '?')} checked in game; {len(probs)} problems")
    else:
        print(f"SECURITY SHOWN: {o.get('n', '?')} systems against their band (the fallback: no secT yet), {o.get('fixed', '?')} stored at 0.45 and low-sec shown 0.4; {len(probs)} problems")
    sys.exit(1 if probs else 0)
