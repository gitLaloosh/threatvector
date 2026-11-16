"""The security the map shows agrees with CCP's security band, and only one function works it out (build queue 058, LESSON #170).

    python3 -I tools/check_sec_shown.py [index.html]   -> 'SECURITY SHOWN: ... 0 problems' (exit 1 otherwise)
    python3 -I tools/check_sec_shown.py --self-test    -> 'SECURITY SHOWN self-test: ok'

Why: INTEL_MAP.sec holds CCP's security rounded to hundredths (tools/jump_table_update.py), and the page rounded it again to tenths in
several places, so 19 low-sec systems (true value just under 0.45, stored as 45) showed 0.5 in the high-sec colour (found at 058's
review, 2026-11-16; the owner: "you dont think we need to do anything further to prevent an issue like this moving forward?", then "yes").
047's INTEL_MAP.band holds each system's band from CCP's unrounded value. Two checks, offline:
  1. the code: `.sec[` is read only inside itMapSecT (the shown value, in tenths) and itRpBand (the route planner's fallback when a table
     has no band); every other reader goes through itMapSecT, itMapSecClass or itMapSecText;
  2. the data: the page's own itMapSecT, run in node on every system of INTEL_MAP, agrees with the band: high (2) shows 0.5 or more, low (1)
     0.1 to 0.4, null (0) 0.0 or less.
The other edge values (a stored x.x5 the game may round either way) can't be settled from the table: a backlog item (the generator to
store the value the game shows).
"""
import base64, json, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ALLOWED = {'itMapSecT', 'itRpBand'}

def script_of(src):
    m = [x.group(1) for x in re.finditer(r'<script>(.*?)</script>', src, re.S)]
    return max(m, key=len) if m else ''

def readers(js):
    """the top-level functions that read `.sec[` (a line outside any function counts as '(top level)')"""
    bad = []
    for m in re.finditer(r'\.sec\[', js):
        head = js.rfind('\nfunction ', 0, m.start())
        name = re.match(r'\nfunction (\w+)', js[head:]).group(1) if head >= 0 else '(top level)'
        # the reader must still be inside that function: no other top-level line start ("\n" + a letter, not an indent) between them
        between = js[head + 1:m.start()] if head >= 0 else js[:m.start()]
        if re.search(r'\n(?:const|let|var|function|//)', between): name = '(top level)'
        if name not in ALLOWED: bad.append((name, js.count('\n', 0, m.start()) + 1))
    return bad

def data_check(js, src):
    fn = re.search(r'\nfunction itMapSecT\(i\)\{.*?\n\}', js, re.S)
    if not fn: return ['itMapSecT not found'], {}
    im = re.search(r'\nconst INTEL_MAP = (\{.*?\});\n', src, re.S)
    if not im: return ['INTEL_MAP not found'], {}
    M = json.loads(im.group(1)); n = M['systems']
    if 'band' not in M: return ['INTEL_MAP has no band (047)'], {}
    prog = ("const M = " + json.dumps({'sec': M['sec'], 'band': M['band'], 'n': n}) + ";\n"
            "const sec = new Int8Array(Buffer.from(M.sec, 'base64')), bb = Buffer.from(M.band, 'base64'), band = new Uint8Array(M.n);\n"
            "for(let i = 0; i < M.n; i++) band[i] = (bb[i >> 2] >> ((i & 3) * 2)) & 3;\n"
            "const T = {sec, band, n: M.n}; function itMapTable(){ return T; }\n" + fn.group(0) + "\n"
            "const bad = [], fixed = []; for(let i = 0; i < T.n; i++){ const t = itMapSecT(i), b = band[i];\n"
            "  if(!Number.isInteger(t) || (b === 2 && t < 5) || (b === 1 && (t < 1 || t > 4)) || (b === 0 && t > 0)) bad.push([i, sec[i], b, t]);\n"
            "  if(sec[i] === 45 && b === 1) fixed.push(i); }\n"
            "console.log(JSON.stringify({bad: bad.slice(0, 10), nbad: bad.length, fixed: fixed.length, n: T.n}));\n")
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(prog); path = f.name
    try: r = subprocess.run(['node', path], capture_output=True, text=True, timeout=60)
    finally: os.unlink(path)
    if r.returncode: return [f'node: {r.stderr.strip()[:300]}'], {}
    o = json.loads(r.stdout)
    probs = [f"{o['nbad']} systems show a security outside their band (first: {o['bad']})"] if o['nbad'] else []
    return probs, o

def run(path):
    src = open(path, encoding='utf-8').read(); js = script_of(src)
    probs = [f'`.sec[` read in {nm} (line {ln} of the script): go through itMapSecT' for nm, ln in readers(js)]
    p2, o = data_check(js, src); probs += p2
    return probs, o

def self_test():
    path = os.path.join(HERE, '..', 'index.html'); src = open(path, encoding='utf-8').read()
    probs, _ = run(path)
    if probs: return [f'the page itself: {probs[0]}']
    out = []
    with tempfile.TemporaryDirectory() as d:
        def mutant(a, b, why):
            if src.count(a) != 1: out.append(f'mutant not applied ({why})'); return
            p = os.path.join(d, 'm.html'); open(p, 'w', encoding='utf-8').write(src.replace(a, b))
            if not run(p)[0]: out.append(f'mutant not caught: {why}')
        mutant("return t >= 5 && T.band && T.band[i] === 1 ? 4 : t;", "return t;", 'the band line taken out (19 low-sec systems read 0.5)')
        mutant("function itMapSecClass(i){ return Math.max(0, itMapSecT(i)); }",
               "function itMapSecClass(i){ const T = itMapTable(), s = T.sec[i]; return s <= 0 ? 0 : Math.max(1, Math.min(10, Math.round(s / 10))); }",
               'a second reader rounding T.sec again')
    return out

if __name__ == '__main__':
    if '--self-test' in sys.argv:
        bad = self_test(); print('\n'.join(bad)); print('SECURITY SHOWN self-test: ' + ('ok' if not bad else f'{len(bad)} problems')); sys.exit(1 if bad else 0)
    path = next((a for a in sys.argv[1:] if not a.startswith('-')), os.path.join(HERE, '..', 'index.html'))
    probs, o = run(path)
    for p in probs: print('PROBLEM: ' + p)
    print(f"SECURITY SHOWN: {o.get('n', '?')} systems against their band, {o.get('fixed', '?')} stored at 0.45 and low-sec shown 0.4; {len(probs)} problems")
    sys.exit(1 if probs else 0)
