"""The security the map shows is the tenth the game shows, and only one function reads it (build queue 058, LESSON #170; build queue 063).

    python3 -I tools/check_sec_shown.py [index.html]   -> 'SECURITY SHOWN: ... 0 problems' (exit 1 otherwise)
    python3 -I tools/check_sec_shown.py --self-test    -> 'SECURITY SHOWN self-test: ok'

Why: INTEL_MAP.sec held CCP's security rounded to hundredths (tools/jump_table_update.py), and the page rounded it again to tenths, so 19
low-sec systems (true value just under 0.45, stored as 45) showed 0.5 in the high-sec colour (found at 058's review, 2026-11-16; the owner:
"you dont think we need to do anything further to prevent an issue like this moving forward?", then "yes"), and 333 systems in all a tenth off
(measured 2026-11-20, build queue 063). Since 063 the generator stores the tenth the game shows (INTEL_MAP.secT, in place of sec and 047's
band); the data pull request (#77) brought it, and 065a took the page's fallback for sec + band out. Checks, offline:
  1. the code: `.secT[` is read only inside itMapSecT; nothing reads `.sec[`, `INTEL_MAP.sec` or `INTEL_MAP.band` any more (065a); every
     other reader goes through itMapSecT, itMapSecClass or itMapSecText (system names through itSecTab);
  2. the data: INTEL_MAP has secT (a table without it is refused), every value -10..10, the page's own itMapSecT (run in node) returns it,
     and the systems checked in game (SAMPLES: the owner's 7 screenshots, Egbinger, and the two on a halfway point) show the tenth he saw.
The self-test's mutants: a reader of `.secT[` outside itMapSecT, a reader of the old `.sec[` (the fallback brought back), itMapSecT not
returning the table's tenth, and a secT one tenth off on a sample (the double rounding).
"""
import base64, json, os, re, struct, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ALLOWED = {'.sec[': set(), '.secT[': {'itMapSecT'}}   # 065a: no reader of 058's sec is left
GONE = ('INTEL_MAP.sec)', 'INTEL_MAP.sec,', 'INTEL_MAP.band', 'function itMapBand')   # 065a: the fallback's reads of the old table
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

def fn_of(js, name):
    """a top-level function's source, by counting braces (one line or many)"""
    m = re.search(r'\nfunction ' + name + r'\([^)]*\)\{', js)
    if not m: return None
    i, d = m.end(), 1
    while i < len(js) and d: d += {'{': 1, '}': -1}.get(js[i], 0); i += 1
    return js[m.start() + 1:i]

def data_check(js, src):
    fn = fn_of(js, 'itMapSecT')
    if not fn: return ['itMapSecT not found'], {}
    im = re.search(r'\nconst INTEL_MAP = (\{.*?\});\n', src, re.S)
    if not im: return ['INTEL_MAP not found'], {}
    M = json.loads(im.group(1)); n = M['systems']
    if 'secT' not in M: return ['INTEL_MAP has no secT (063): the page has no fallback for 058\'s sec any more (065a)'], {}
    if True:
        S = ids_of(src); at = {s: i for i, s in enumerate(S)}
        pins = {str(at[s]): t for s, t in SAMPLES.items() if s in at}
        prog = ("const M = " + json.dumps({'secT': M['secT'], 'n': n, 'pins': pins}) + ";\n"
                "const secT = new Int8Array(Buffer.from(M.secT, 'base64'));\n"
                "const T = {secT, n: M.n}; function itMapTable(){ return T; }\n" + fn + "\n"
                "const bad = [], pinBad = []; let range = 0; for(let i = 0; i < T.n; i++){ const t = itMapSecT(i);\n"
                "  if(t !== secT[i]) bad.push([i, secT[i], t]); if(!(secT[i] >= -10 && secT[i] <= 10)) range++; }\n"
                "for(const [i, w] of Object.entries(M.pins)) if(itMapSecT(Number(i)) !== w) pinBad.push([Number(i), w, itMapSecT(Number(i))]);\n"
                "console.log(JSON.stringify({form: 'secT', bad: bad.slice(0, 10), nbad: bad.length, range, pinBad, pins: Object.keys(M.pins).length, n: T.n, len: secT.length}));\n")
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(prog); path = f.name
    try: r = subprocess.run(['node', path], capture_output=True, text=True, timeout=60)
    finally: os.unlink(path)
    if r.returncode: return [f'node: {r.stderr.strip()[:300]}'], {}
    o = json.loads(r.stdout); probs = []
    if o['len'] != o['n']: probs.append(f"secT holds {o['len']} values for {o['n']} systems")
    if o['nbad']: probs.append(f"itMapSecT doesn't return the table's tenth for {o['nbad']} systems (first: {o['bad']})")
    if o['range']: probs.append(f"{o['range']} systems have a tenth outside -10..10")
    if o['pinBad']: probs.append(f"systems checked in game show another tenth ([index, in game, shown]: {o['pinBad']})")
    if o['pins'] != len(SAMPLES): probs.append(f"only {o['pins']} of the {len(SAMPLES)} systems checked in game are in the table")
    return probs, o

def run(path):
    src = open(path, encoding='utf-8').read(); js = script_of(src)
    probs = [f'`{col}` read in {nm} (line {ln} of the script): go through itMapSecT' for col, nm, ln in readers(js)]
    probs += [f'`{g}` is in the script: 063\'s fallback for the old table is gone (065a); read the security through itMapSecT' for g in GONE if g in js]
    p2, o = data_check(js, src); probs += p2
    return probs, o

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
        s2, at = src, {s: i for i, s in enumerate(ids_of(src))}
        mutant(s2, "function itMapSecClass(i){ return Math.max(0, itMapSecT(i)); }",
               "function itMapSecClass(i){ const T = itMapTable(); return Math.max(0, T.secT[i]); }", 'a reader of secT outside itMapSecT')
        mutant(s2, "function itMapSecT(i){ return itMapTable().secT[i]; }", "function itMapSecT(i){ const t = itMapTable().secT[i]; return t === -9 ? -8 : t; }",
               'itMapSecT not returning the table\'s tenth (A2V6-6 at -0.8, the double rounding)')
        mutant(s2, "function itMapSecClass(i){ return Math.max(0, itMapSecT(i)); }",
               "function itMapSecClass(i){ const T = itMapTable(); return T.sec ? Math.max(0, Math.round(T.sec[i] / 10)) : Math.max(0, itMapSecT(i)); }",
               'a reader of the old sec brought back (the fallback)')
        mutant(s2, "function itMapSecT(i){ return itMapTable().secT[i]; }", "function itMapSecT(i){ return itMapTable().secT[i]; }\nfunction itMapBand(raw, n){ return INTEL_MAP.band ? raw(INTEL_MAP.band) : null; }",
               'itMapBand brought back')
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
    print(f"SECURITY SHOWN: {o.get('n', '?')} systems, the table's tenth (secT), {o.get('pins', '?')} checked in game; {len(probs)} problems")
    sys.exit(1 if probs else 0)
