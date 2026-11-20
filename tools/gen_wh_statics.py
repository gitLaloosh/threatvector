"""Build queue 061 (Project doc roadmap/wh-statics-plan.md): each wormhole system's statics, from Wanderer's community list, into the page.

    python3 -I tools/gen_wh_statics.py [index.html] --check                     # the block is sound; against the pinned file when reachable
    python3 -I tools/gen_wh_statics.py [index.html] --src FILE --commit SHA     # compare a copy of Wanderer's file with the page
    python3 -I tools/gen_wh_statics.py [index.html] --src FILE --commit SHA --write [--body PR.md]   # and write the block
    python3 -I tools/gen_wh_statics.py --self-test                              # the checks refuse broken files (made-up data)
    python3 -I tools/gen_wh_statics.py --ccp-fields                             # (the Action) list CCP's J-space system fields

The source is wanderer-industries/wanderer `priv/repo/data/wormholeSystems.json` (source: https://github.com/wanderer-industries/wanderer,
the file at commit 4d4a035, checked 2026-11-19): one record per J-space system, {solarSystemID, systemName, effectName, statics, wanderers}.
Only `solarSystemID` and `statics` are read (LESSON #153: the other fields may change form; class and effect stay CCP's, INTEL_WH).
The file is outside data: every record is checked before anything is written, and only type codes the page already knows (IT_WH_TYPE,
CCP's, tools/gen_wh_table.py) reach the page. Matched by ID, never by name (Wanderer calls CCP's "Liberated Barbican" "Barbican").

INTEL_WH_STC, in its own block after the wormhole table (the owner at the 061 review, "go with your recommendations": not a field of
INTEL_WH, which tools/jump_table_update.py rebuilds and compares whole):
  n     the number of systems it follows; of: FNV-1a (32 bit) of INTEL_WH.sys, the system list it follows. The page uses the statics only
        while both match (whTable), so a wormhole table rebuilt for a new system list can't pair systems with another system's statics.
  codes the type codes used, space-separated; stc: per system in INTEL_WH's order, its codes as characters of ABC (an index into codes),
        systems separated by '|', in Wanderer's order (the page shows them in class order).
  src   {repo, file, commit, sha256} of the file it was made from.

The Action (.github/workflows/jump-table.yml, job wh-statics) runs this twice a day against Wanderer's newest commit and opens a pull
request when the statics changed (or the system list moved under them); a change in Wanderer's other fields doesn't count.

Wanderer's licence (the file's data is used under it):

MIT License

Copyright (c) 2024 Wanderer Industries

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import sys, os, re, io, json, base64, struct, hashlib, urllib.request, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO, FILE = 'wanderer-industries/wanderer', 'priv/repo/data/wormholeSystems.json'
RAW = 'https://raw.githubusercontent.com/{repo}/{commit}/{file}'
ABC = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'   # the page's WH_STC_ABC
WH_LO = 31000000   # the page's WH_LO: INTEL_WH.sys holds each ID as a 16-bit step from here
WBEGIN, WEND = '// ---- WORMHOLE TABLE (tools/jump_table_update.py; do not edit by hand) ----', '// ---- END WORMHOLE TABLE ----'
SBEGIN, SEND = '// ---- WORMHOLE STATICS (tools/gen_wh_statics.py; do not edit by hand) ----', '// ---- END WORMHOLE STATICS ----'
CODE = re.compile(r'[A-Z]\d{3}')

def opt(name):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv): return sys.argv[i + 1]
    return None
def out(key, val):   # a GitHub Actions step output (nothing outside the Action)
    f = os.environ.get('GITHUB_OUTPUT')
    if f:
        with open(f, 'a', encoding='utf-8') as h: h.write(f'{key}={val}\n')
def summary(text):
    f = os.environ.get('GITHUB_STEP_SUMMARY')
    if f:
        with open(f, 'a', encoding='utf-8') as h: h.write(text + '\n')
def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'threat-vector wormhole statics check (github.com/gitlaloosh/threatvector)'})
    with urllib.request.urlopen(req, timeout=120) as r: return r.read()

def fnv(s):   # FNV-1a, 32 bit, over the string's UTF-8 bytes (the page's whFnv, over an ASCII string)
    h = 0x811c9dc5
    for b in s.encode('utf-8'): h = ((h ^ b) * 0x01000193) & 0xffffffff
    return f'{h:08x}'

# ---- the page ----
def page_parts(src):
    mw = re.search(re.escape(WBEGIN) + r'\nconst INTEL_WH = (.*);\n' + re.escape(WEND), src)
    if not mw: raise SystemExit('index.html has no wormhole table (INTEL_WH)')
    W = json.loads(mw.group(1))
    d, ids, cur = base64.b64decode(W['sys']), [], WH_LO
    for i in range(W['systems']):
        cur += struct.unpack_from('<H', d, 2 * i)[0]; ids.append(cur)
    mt = re.search(r'const IT_WH_TYPE = (\{.*?\});', src)
    if not mt: raise SystemExit('index.html has no IT_WH_TYPE (tools/gen_wh_table.py)')
    types = json.loads(mt.group(1))
    ms = re.search(re.escape(SBEGIN) + r'\nconst INTEL_WH_STC = (.*);\n' + re.escape(SEND), src)
    return W, ids, types, (json.loads(ms.group(1)) if ms else None), ms

# ---- Wanderer's file: read and checked (outside data) ----
def read_source(raw, ids, types):
    """{id: [codes]} from the file's bytes, or SystemExit with every problem found."""
    problems = []
    try: data = json.loads(raw.decode('utf-8'))
    except (UnicodeDecodeError, ValueError) as e: raise SystemExit(f'Wanderer\'s file is not JSON: {e}')
    if not isinstance(data, list): raise SystemExit('Wanderer\'s file is not a list of systems')
    got = {}
    for i, r in enumerate(data):
        sid = r.get('solarSystemID') if isinstance(r, dict) else None
        if not isinstance(sid, int) or isinstance(sid, bool): problems.append(f'record {i}: no whole-number solarSystemID'); continue
        if sid in got: problems.append(f'{sid}: listed twice'); continue
        st = r.get('statics')
        if not isinstance(st, list) or not all(isinstance(x, str) for x in st): problems.append(f'{sid}: statics is not a list of codes'); continue
        bad = [x for x in st if not CODE.fullmatch(x)]
        if bad: problems.append(f'{sid}: not a type code: {bad[:3]}'); continue
        if not 1 <= len(st) <= 3: problems.append(f'{sid}: {len(st)} statics (1 to 3 expected)')
        if len(set(st)) != len(st): problems.append(f'{sid}: a static listed twice')
        if 'K162' in st: problems.append(f'{sid}: K162 as a static (it is only ever the far end of a hole)')
        unk = [x for x in st if x not in types]
        if unk: problems.append(f'{sid}: codes the page doesn\'t know (IT_WH_TYPE): {unk}')
        got[sid] = list(st)
    want = set(ids)
    if set(got) - want: problems.append(f'{len(set(got) - want)} system(s) not in the page\'s wormhole table, e.g. {sorted(set(got) - want)[:3]}')
    if want - set(got): problems.append(f'{len(want - set(got))} of the page\'s wormhole systems missing, e.g. {sorted(want - set(got))[:3]}')
    if problems: raise SystemExit('Wanderer\'s file refused (nothing written): ' + '; '.join(problems[:12]) + (f'; and {len(problems) - 12} more' if len(problems) > 12 else ''))
    return got

def encode(ids, got, sys_str, commit, sha):
    codes = sorted({c for v in got.values() for c in v})
    if len(codes) > len(ABC): raise SystemExit(f'{len(codes)} distinct codes, more than the {len(ABC)} the encoding holds')
    at = {c: i for i, c in enumerate(codes)}
    stc = '|'.join(''.join(ABC[at[c]] for c in got[i]) for i in ids)
    return {'n': len(ids), 'of': fnv(sys_str), 'codes': ' '.join(codes), 'stc': stc, 'src': {'repo': REPO, 'file': FILE, 'commit': commit, 'sha256': sha}}

def decode(S):
    codes = S['codes'].split(' ')
    return [[codes[ABC.index(ch)] for ch in g] for g in S['stc'].split('|')]

def block(S): return SBEGIN + '\nconst INTEL_WH_STC = ' + json.dumps(S, separators=(',', ':')) + ';\n' + SEND

def sound(S, W, ids, types):
    """Problems with the page's block on its own (no source needed)."""
    p = []
    if S.get('n') != W['systems'] or S.get('of') != fnv(W['sys']):
        return ['the statics follow another wormhole system list (n / of differ from INTEL_WH): run the Action (job wh-statics), or this tool with --src and --write']
    try: dec = decode(S)
    except (ValueError, KeyError, IndexError, AttributeError) as e: return [f'the block doesn\'t decode: {e}']
    if len(dec) != len(ids): p.append(f'{len(dec)} entries for {len(ids)} systems')
    for i, v in zip(ids, dec):
        if not 1 <= len(v) <= 3: p.append(f'{i}: {len(v)} statics')
        if 'K162' in v or any(c not in types for c in v): p.append(f'{i}: a code the page doesn\'t know or K162: {v}')
        if len(p) > 10: break
    src = S.get('src') or {}
    if src.get('repo') != REPO or src.get('file') != FILE or not re.fullmatch(r'[0-9a-f]{40}', str(src.get('commit'))) or not re.fullmatch(r'[0-9a-f]{64}', str(src.get('sha256'))):
        p.append('src must name the repository, the file, a full commit id and the file\'s sha256')
    return p

def changes(ids, names, old, new):
    """Lines 'J123456: C247 → C247 N062' for the systems whose statics changed."""
    o = dict(zip(ids, old)) if old else {}
    return [f'{names[k]}: {" ".join(o.get(i) or []) or "(none)"} → {" ".join(new[k])}' for k, i in enumerate(ids) if (o.get(i) or []) != new[k]]

# ---- the made-up world for --self-test ----
def self_test():
    ids = [31000001, 31000002, 31000005, 31000010]
    sys_str = base64.b64encode(b''.join(struct.pack('<H', b - a) for a, b in zip([WH_LO] + ids, ids))).decode()
    W = {'systems': len(ids), 'sys': sys_str}
    types = {'C247': 'c3', 'N062': 'c5', 'D845': 'hs', 'U210': 'ls', 'K162': 'exit'}
    good = [{'solarSystemID': 31000001, 'systemName': 'Liberated Made-up', 'statics': ['C247']},
            {'solarSystemID': 31000002, 'systemName': 'J000002', 'statics': ['N062', 'C247']},
            {'solarSystemID': 31000005, 'systemName': 'J000005', 'statics': ['D845', 'U210', 'C247'], 'effectName': None},
            {'solarSystemID': 31000010, 'systemName': 'J000010', 'statics': ['U210']}]
    raw = lambda d: json.dumps(d).encode()
    fails = []
    got = read_source(raw(good), ids, types)
    S = encode(ids, got, sys_str, 'a' * 40, 'b' * 64)
    if decode(S) != [got[i] for i in ids]: fails.append('round trip')
    if sound(S, W, ids, types): fails.append(f'a sound block refused: {sound(S, W, ids, types)}')
    renamed = json.loads(json.dumps(good)); renamed[0]['systemName'] = 'Made-up'; renamed[1]['effectName'] = 'Pulsar'
    if read_source(raw(renamed), ids, types) != got: fails.append('a renamed system or another effect changed the statics (must match by ID)')
    def refused(d, why):
        try: read_source(d if isinstance(d, bytes) else raw(d), ids, types); fails.append(f'not refused: {why}')
        except SystemExit: pass
    m = lambda f: (lambda d: (f(d), d)[1])(json.loads(json.dumps(good)))
    refused(good[:3], 'a dropped system')
    refused(good + [{'solarSystemID': 31000011, 'statics': ['C247']}], 'a system the page doesn\'t know')
    refused(m(lambda d: d[1].__setitem__('statics', ['Z999'])), 'an unknown code')
    refused(m(lambda d: d[1].__setitem__('statics', ['K162'])), 'K162 as a static')
    refused(m(lambda d: d[1].__setitem__('statics', [])), 'no statics')
    refused(m(lambda d: d[1].__setitem__('statics', ['C247', 'N062', 'D845', 'U210'])), 'four statics')
    refused(m(lambda d: d[1].__setitem__('statics', ['C247', 'C247'])), 'a static twice')
    refused(m(lambda d: d[1].__setitem__('statics', ['<b>x</b>'])), 'markup in a code')
    refused(m(lambda d: d[1].__setitem__('statics', 'C247')), 'statics as a string')
    refused(m(lambda d: d[1].__setitem__('solarSystemID', '31000002')), 'an ID as text')
    refused(m(lambda d: d.append(dict(d[0]))), 'a system twice')
    refused(b'{"not": "a list"}', 'not a list'); refused(b'\xff\xfe', 'not JSON')
    moved = dict(W, sys=base64.b64encode(struct.pack('<HHHH', 1, 1, 3, 6)).decode())
    if not sound(S, moved, ids, types): fails.append('statics made for another system list were accepted')
    bad = dict(S, stc=S['stc'].replace('|', '', 1))
    if not sound(bad, W, ids, types): fails.append('a block with a system missing was accepted')
    bad = dict(S, src=dict(S['src'], commit='main'))
    if not sound(bad, W, ids, types): fails.append('a block without a full commit id was accepted')
    print('gen_wh_statics self-test: ' + ('; '.join(fails) if fails else 'ok')); return 1 if fails else 0

# ---- R2 (the 061 review): which fields CCP's own data gives a J-space system ----
def ccp_fields():
    base = 'https://developers.eveonline.com/static-data/tranquility'
    build = None
    for line in fetch(f'{base}/latest.jsonl').decode('utf-8').splitlines():
        if line.strip():
            o = json.loads(line)
            if o.get('_key') == 'sde': build = int(o['buildNumber'])
    if not build: raise SystemExit('latest.jsonl has no "sde" record')
    z = zipfile.ZipFile(io.BytesIO(fetch(f'{base}/eve-online-static-data-{build}-jsonl.zip')))
    keys, n = {}, 0
    for line in io.TextIOWrapper(z.open('mapSolarSystems.jsonl'), encoding='utf-8'):
        if not line.strip(): continue
        o = json.loads(line)
        if not WH_LO <= int(o.get('_key', 0)) < 32000000: continue
        n += 1
        for k in o: keys[k] = keys.get(k, 0) + 1
    hint = sorted(k for k in keys if re.search(r'static|wormhole|hole', k, re.I))
    files = sorted(x for x in z.namelist() if re.search(r'static|wormhole', x, re.I))
    msg = (f"CCP's build {build}: {n} J-space systems in mapSolarSystems.jsonl; their fields: " + ', '.join(f'{k} ({v})' for k, v in sorted(keys.items()))
           + f". Fields that could hold statics: {', '.join(hint) or 'none'}; files named for statics or wormholes: {', '.join(files) or 'none'}.")
    print(msg); summary(f'**Statics in CCP\'s own data (build queue 061, R2).** {msg}')

def main():
    if '--self-test' in sys.argv: return self_test()
    if '--ccp-fields' in sys.argv: ccp_fields(); return 0
    SRC, COMMIT, BODY = opt('--src'), opt('--commit'), opt('--body')
    args = [a for a in sys.argv[1:] if not a.startswith('--') and a not in (SRC, COMMIT, BODY)]
    html = args[0] if args else os.path.join(HERE, '..', 'index.html')
    text = open(html, encoding='utf-8').read()
    W, ids, types, S, ms = page_parts(text)
    names = W['names'].split('|')
    if '--check' in sys.argv and not SRC:
        if S is None: print('gen_wh_statics: index.html has no INTEL_WH_STC block; 1 problem'); return 1
        p = sound(S, W, ids, types)
        if p: print('gen_wh_statics: ' + '; '.join(p[:8]) + f'; {len(p)} problem(s)'); return 1
        try: raw = fetch(RAW.format(repo=REPO, commit=S['src']['commit'], file=FILE))
        except Exception as e:   # the chain may run where GitHub's raw files can't be reached: say so; the Action checks it twice a day
            print(f"gen_wh_statics: the block is sound ({W['systems']} systems, {len(S['codes'].split())} codes, Wanderer {S['src']['commit'][:7]}); "
                  f"Wanderer's file not reachable from here ({type(e).__name__}), so not compared; the Action compares it twice a day; 0 problems"); return 0
        p = []
        if hashlib.sha256(raw).hexdigest() != S['src']['sha256']: p.append('the pinned file\'s sha256 differs from the block\'s')
        new = read_source(raw, ids, types)
        diff = changes(ids, names, decode(S), new)
        if diff: p.append(f'{len(diff)} system(s) differ from the pinned file, e.g. {diff[:3]}')
        print(f"gen_wh_statics: {W['systems']} systems match Wanderer {S['src']['commit'][:7]}" if not p else 'gen_wh_statics: ' + '; '.join(p), end='')
        print(f'; {len(p)} problem(s)' if p else '; 0 problems'); return 1 if p else 0
    if not SRC or not COMMIT or not re.fullmatch(r'[0-9a-f]{40}', COMMIT): raise SystemExit('give --src FILE and --commit <the full commit id it came from> (or --check)')
    raw = open(SRC, 'rb').read(); sha = hashlib.sha256(raw).hexdigest()
    got = read_source(raw, ids, types)
    NS = encode(ids, got, W['sys'], COMMIT, sha)
    old = decode(S) if S and not sound(S, W, ids, types) else None   # statics made for another system list count as none
    diff = changes(ids, names, old, [got[i] for i in ids])
    moved = S is not None and old is None
    changed = bool(diff)
    msg = (f"Wanderer {COMMIT[:7]}: {len(diff)} system(s) changed statics" + (' (the page\'s statics followed another system list)' if moved else '')
           if changed else f"Wanderer {COMMIT[:7]}: the statics match the page's ({W['systems']} systems)")
    print(msg); print('\n'.join(diff[:40]))
    out('changed', 'true' if changed else 'false'); out('commit', COMMIT[:7])
    summary(f'**{msg}.**' + ('\n\n' + '\n'.join(f'- {x}' for x in diff[:200]) if diff else ''))
    if '--write' in sys.argv and changed:
        from csp_hash import write as csp_write   # the page's CSP names the script by hash, so a rewrite refreshes it
        nb = block(NS)
        if ms: text = text[:ms.start()] + nb + text[ms.end():]
        else:
            e = text.index(WEND) + len(WEND); text = text[:e] + '\n' + nb + text[e:]
        open(html, 'w', encoding='utf-8', newline='\n').write(csp_write(text)[0])
        print(f'written: INTEL_WH_STC from Wanderer {COMMIT[:7]}')
        if BODY:
            open(BODY, 'w', encoding='utf-8').write(
                f'Wanderer\'s community list of wormhole statics changed (wanderer-industries/wanderer `{FILE}` at {COMMIT}). This updates the page\'s '
                f'statics table (`INTEL_WH_STC`) in index.html; nothing else changes. Only the type codes the page already knows are taken.\n\n'
                + (('The page\'s statics followed another wormhole system list, so every system is listed.\n\n') if moved else '')
                + '\n'.join(f'- {x}' for x in diff[:300]) + (f'\n- … and {len(diff) - 300} more' if len(diff) > 300 else '')
                + f'\n\nMade by `.github/workflows/jump-table.yml` (job wh-statics) with `tools/gen_wh_statics.py`. After merging, run `git pull` before your next commit.\n')
    return 0

if __name__ == '__main__':
    sys.exit(main())
