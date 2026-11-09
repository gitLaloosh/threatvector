"""The copy of the site GitHub Pages serves: the repo's files, with index.html's comments taken out (build queue 027).

    python3 -I tools/publish.py [--out _site]   -> writes the folder; 'PUBLISH: ok' and both gzipped sizes, or exits 1
    python3 -I tools/publish.py --size          -> only the two gzipped sizes (index.html stripped and checked in memory; nothing written)
    python3 -I tools/publish.py --self-test     -> made-up pages with comments in awkward places, and the checks catching harm

Project doc roadmap/page-publish-plan.md; the owner, 2026-11-08: "GitHub Actions deploys it (Recommended)", and the 800 KB
ceiling applies to the served copy ("confirmed"). The repo keeps the commented source; nothing is ever edited in the output by
hand. .github/workflows/pages.yml runs this on every merge to main and publishes the folder.

What is served: every file git tracks (what Pages served from the branch), less dotfiles and .github/ (Jekyll never served
those). index.html, stripped:
- the one inline script: tools/publish/strip_js.js (acorn, a copy kept in tools/publish/) drops comments and the spaces
  around tokens, copies every token's text as is, and checks the tokens are the source's one for one;
- CSS comments inside <style> and HTML comments elsewhere: a small scanner (strings and url(...) skipped); a comment alone on
  its line takes its line with it;
- the CSP meta's script hash rewritten for the stripped script (csp_hash.write), then checked.
Checks before anything is written (any failure: exit 1, nothing published): node --check on the script; csp_hash's problems;
outside the script, the output is the source with exactly the comment spans removed, each span a whole comment; the same ids,
data-* attribute names and tags; and the size line. Owner's ceiling: 800 KB gzipped for the served copy.
"""
import sys, os, re, json, shutil, subprocess, gzip, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)   # -I leaves this folder off the path; csp_hash lives here
import csp_hash

ROOT = os.path.abspath(os.path.join(HERE, '..'))
STRIP_JS = os.path.join(HERE, 'publish', 'strip_js.js')
CEILING = 800_000   # the owner, 2026-11-03: "At 800 KB"; since 027 it applies to the served copy
SCRIPT_RX = re.compile(r'<script>(.*?)</script>', re.S)


class PublishError(Exception):
    pass


def css_comment_spans(css, base):
    """Spans (start, end) of /* ... */ in CSS text, skipping strings and unquoted url(...)."""
    spans, i, n = [], 0, len(css)
    while i < n:
        c = css[i]
        if c in '"\'':
            j = i + 1
            while j < n and css[j] != c:
                if css[j] == '\\': j += 1
                j += 1
            i = j + 1
        elif css.startswith('url(', i) and not css[i + 4:i + 5] in ('"', "'"):
            j = css.find(')', i)
            if j < 0: raise PublishError('CSS: url( without )')
            i = j + 1
        elif css.startswith('/*', i):
            j = css.find('*/', i + 2)
            if j < 0: raise PublishError('CSS: a comment never closed')
            spans.append((base + i, base + j + 2)); i = j + 2
        else:
            i += 1
    return spans


def html_comment_spans(html, script_span):
    """Comment spans outside the script: CSS comments inside <style>, HTML comments elsewhere."""
    spans = []
    s0, s1 = script_span
    for seg_start, seg_end in ((0, s0), (s1, len(html))):
        seg = html[seg_start:seg_end]
        styles = [(m.start(1) + seg_start, m.end(1) + seg_start) for m in re.finditer(r'<style>(.*?)</style>', seg, re.S)]
        for a, b in styles: spans += css_comment_spans(html[a:b], a)
        i = seg_start
        while True:
            j = html.find('<!--', i, seg_end)
            if j < 0: break
            if any(a <= j < b for a, b in styles): i = j + 4; continue
            k = html.find('-->', j + 4, seg_end)
            if k < 0: raise PublishError('HTML: a comment never closed')
            spans.append((j, k + 3)); i = k + 3
    return sorted(spans)


def widen(html, spans):
    """A comment alone on its line(s) takes the line with it, so no blank lines are left."""
    out = []
    for a, b in spans:
        ls = html.rfind('\n', 0, a) + 1
        le = html.find('\n', b); le = len(html) if le < 0 else le
        if html[ls:a].strip() == '' and html[b:le].strip() == '' and le < len(html): a, b = ls, le + 1
        out.append((a, b))
    return out


def cut(text, spans):
    parts, prev = [], 0
    for a, b in spans:
        if a < prev: raise PublishError('overlapping comments')
        parts.append(text[prev:a]); prev = b
    parts.append(text[prev:])
    return ''.join(parts)


def strip_js(js):
    r = subprocess.run(['node', STRIP_JS], input=js.encode('utf-8'), capture_output=True)
    if r.returncode: raise PublishError(r.stderr.decode('utf-8', 'replace').strip() or 'strip_js failed')
    return r.stdout.decode('utf-8')


def names(html):
    return (sorted(re.findall(r'\bid="([^"$]*)"', html)), sorted(set(re.findall(r'\s(data-[a-z0-9-]+)=', html))),
            sorted(re.findall(r'<([a-zA-Z][a-zA-Z0-9-]*)[\s>]', html)))


def strip_page(src):
    """index.html's source -> the served copy (str). Raises PublishError on anything but comments going."""
    ms = list(SCRIPT_RX.finditer(src))
    if len(re.findall(r'<script\b', src)) != 1 or len(ms) != 1: raise PublishError('expected exactly one plain <script> in the page')
    m = ms[0]
    spans = widen(src, html_comment_spans(src, (m.start(), m.end())))
    for a, b in spans:
        t = src[a:b].strip()
        if not ((t.startswith('/*') and t.endswith('*/') and '*/' not in t[2:-2]) or (t.startswith('<!--') and t.endswith('-->') and '-->' not in t[4:-3])):
            raise PublishError(f'a cut that is not one whole comment: {t[:60]!r}')
    pre_spans = [s for s in spans if s[1] <= m.start(1)]
    post_spans = [(a - m.end(1), b - m.end(1)) for a, b in spans if a >= m.end(1)]
    js = strip_js(m.group(1))
    out = cut(src[:m.start(1)], pre_spans) + js + cut(src[m.end(1):], post_spans)
    out, _ = csp_hash.write(out)
    check(src, out)
    return out


def check(src, out):
    """The served copy's own checks (also run by the self-test against harmed copies)."""
    ms = list(SCRIPT_RX.finditer(out))
    if len(ms) != 1: raise PublishError('the served copy has no single <script>')
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(ms[0].group(1)); p = f.name
    try:
        r = subprocess.run(['node', '--check', p], capture_output=True)
        if r.returncode: raise PublishError('node --check: ' + r.stderr.decode('utf-8', 'replace').strip()[:300])
    finally: os.unlink(p)
    ps = csp_hash.problems(out)
    if ps: raise PublishError('CSP: ' + '; '.join(ps))
    a, b = SCRIPT_RX.search(src), ms[0]
    # The source's names, with comments found by a second, naive reading (a cross-check on the scanner above):
    # HTML comments, and /* */ inside <style>.
    rest = re.sub(r'<!--.*?-->', '', src[:a.start()] + src[a.end():], flags=re.S)
    rest = re.sub(r'<style>.*?</style>', lambda mm: re.sub(r'/\*.*?\*/', '', mm.group(0), flags=re.S), rest, flags=re.S)
    na, nb = names(rest), names(out[:b.start()] + out[b.end():])
    for what, x, y in zip(('ids', 'data-* attributes', 'tags'), na, nb):
        if x != y:
            lost = sorted(set(x) - set(y)) or sorted(set(y) - set(x))
            raise PublishError(f'{what} differ outside the script: {lost[:5]}')
    ta, tb = js_tokens(a.group(1)), js_tokens(b.group(1))
    if ta != tb:
        i = next((i for i, (x, y) in enumerate(zip(ta, tb)) if x != y), min(len(ta), len(tb)))
        raise PublishError(f'the script\'s tokens differ from the source\'s at token {i} ({len(ta)} before, {len(tb)} after)')


def js_tokens(js):
    """The script's tokens, each its own text, as acorn reads them (the same reader strip_js uses)."""
    r = subprocess.run(['node', '-e', 'process.stdout.write(JSON.stringify(require(process.argv[1]).tokens(require("fs").readFileSync(0, "utf8")).list))', STRIP_JS],
                       input=js.encode('utf-8'), capture_output=True)
    if r.returncode: raise PublishError('the script does not parse: ' + r.stderr.decode('utf-8', 'replace').strip()[:300])
    return json.loads(r.stdout.decode('utf-8'))


def gz(data):
    try:
        r = subprocess.run(['gzip', '-9', '-c'], input=data, capture_output=True, check=True)
        return len(r.stdout)
    except (OSError, subprocess.CalledProcessError):
        return len(gzip.compress(data, 9))


# Folders kept in the repo but never served (the owner, 2026-11-08: "i'd like you to just take care of it"): the mockups in
# `Claude outputs/` are copies of the page with made-up data and stand-in logins; served on the site they would share its browser
# storage (a visitor's Intel settings, Standings, My Fits) and could pass for the real page.
NOT_SERVED = ('Claude outputs/',)


def tracked():
    r = subprocess.run(['git', 'ls-files', '-z'], cwd=ROOT, capture_output=True, check=True)
    out = []
    for f in r.stdout.decode('utf-8').split('\0'):
        if not f or any(part.startswith('.') for part in f.split('/')): continue
        if f.startswith(NOT_SERVED): continue
        out.append(f)
    return out


def sizes():
    """(source, served) gzipped sizes of index.html: the served copy made and checked in memory, nothing copied (2026-11-08: a
    planning session wanted the number, and --out copies the whole site, 560+ files)."""
    src = open(os.path.join(ROOT, 'index.html'), 'rb').read().decode('utf-8')
    return gz(src.encode('utf-8')), gz(strip_page(src).encode('utf-8'))


def size_line(g_src, g_out):
    return f'PUBLISH: index.html {g_src:,} bytes gzipped in the source, {g_out:,} served (gzip -9); ceiling {CEILING:,} for the served copy'


def publish(out_dir):
    out_dir = os.path.abspath(out_dir)
    if out_dir == ROOT or ROOT.startswith(out_dir + os.sep): raise PublishError('the output folder must not hold the repo')
    src = open(os.path.join(ROOT, 'index.html'), 'rb').read().decode('utf-8')
    page = strip_page(src)
    files = tracked()
    if 'index.html' not in files: raise PublishError('index.html is not tracked')
    if os.path.isdir(out_dir): shutil.rmtree(out_dir)
    for f in files:
        dst = os.path.join(out_dir, f)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if f == 'index.html': open(dst, 'wb').write(page.encode('utf-8'))
        else: shutil.copy2(os.path.join(ROOT, f), dst)
    g_src, g_out = gz(src.encode('utf-8')), gz(page.encode('utf-8'))
    print(f'PUBLISH: {len(files)} files into {os.path.relpath(out_dir, ROOT) if out_dir.startswith(ROOT) else out_dir}')
    print(size_line(g_src, g_out))
    if g_out > CEILING: raise PublishError(f'the served copy is past 800 KB ({g_out:,} bytes): stop and ask the owner')
    print('PUBLISH: ok')


def self_test():
    """Comments in awkward places must go; everything else must stay; the checks must refuse harmed copies."""
    page = '''<!DOCTYPE html>
<html lang="en"><head>
<!-- a comment before the CSP meta -->
<meta http-equiv="Content-Security-Policy" content="CSP">
<meta name="referrer" content="no-referrer">
<style>
  /* a whole-line CSS comment */
  .a::before{content:"/* not a comment */"; background:url(http://x.test/*y*/z.png);}  /* trailing */
  .b{content:'it\\'s /* still text */';}
  .c::after{content:"<!-- not an HTML comment -->";}
</style></head>
<body><div id="one" data-k="v">text <!-- inline html comment --> more</div>
<script>
// a whole-line comment
const s1 = "http://not-a-comment";  // trailing
const s2 = 'a /* not a comment */ b';
const re = /\\/\\/[^/]*\\/\\*/g;
const t = `line one // kept
  /* kept too */ ${1 /* inside a substitution: goes */ + 2}`;
const h = "<!-- kept in a string -->";
/* a block
   over lines */
let a = 1
let b = a
++b
function f(){ return /* the value is on the next line:
  it stays there */
  1 }
const div = 4 / 2 / 1;
</script>
</body></html>
'''
    page = page.replace('content="CSP"', 'content="' + csp_hash.EXPECTED.replace('{hash}', 'x') + '"')
    out = strip_page(page)
    fails = []
    keep = ['"http://not-a-comment"', "'a /* not a comment */ b'", '/\\/\\/[^/]*\\/\\*/g', '`line one // kept\n  /* kept too */ ${', '"<!-- kept in a string -->"',
            'content:"/* not a comment */"', 'url(http://x.test/*y*/z.png)', "'it\\'s /* still text */'", 'content:"<!-- not an HTML comment -->"', 'id="one"', 'data-k="v"', 'let a = 1\nlet b = a\n++b', 'return\n1', '4 / 2 / 1']
    gone = ['a comment before the CSP meta', 'whole-line CSS comment', 'trailing */', 'inline html comment', 'a whole-line comment', '// trailing', 'a block', 'inside a substitution']
    for k in keep:
        if k not in out: fails.append(f'kept text lost: {k!r}')
    for g in gone:
        if g in out: fails.append(f'comment kept: {g!r}')
    if csp_hash.problems(out): fails.append('CSP problems in the output: ' + '; '.join(csp_hash.problems(out)))
    if '\n\n' in out.split('<script>')[0]: fails.append('a blank line left where a whole-line comment was')
    # the checks refuse a harmed copy (each must raise)
    harms = {
        'the CSP hash not rewritten': lambda o: o.replace(csp_hash.script_hash(o), 'A' * 43 + '='),
        'a string holding // cut': lambda o: o.replace('"http://not-a-comment"', '"http:"'),
        'an id lost': lambda o: o.replace('id="one" ', ''),
        'a line break lost (the return then gives back its value)': lambda o: o.replace('return\n1', 'return 1'),
        'a script that no longer parses': lambda o: o.replace('const div = 4 / 2 / 1;', 'const div = 4 / ;'),
    }
    for name, harm in harms.items():
        bad = harm(out)
        if name != 'the CSP hash not rewritten': bad, _ = csp_hash.write(bad)
        try:
            check(page, bad); fails.append(f'the checks passed a harmed copy: {name}')
        except PublishError:
            pass
    for name, bad in {'a comment that never closes': page.replace('-->', '', 1), 'two scripts': page.replace('</body>', '<script>1</script></body>')}.items():
        try:
            strip_page(bad); fails.append(f'strip_page accepted: {name}')
        except PublishError:
            pass
    # what is served: tracked files, never a dotfile or .github/
    if any(part.startswith('.') for f in tracked() for part in f.split('/')): fails.append('a dotfile or .github/ would be served')
    if 'index.html' not in tracked(): fails.append('index.html is not among the files served')
    if any(f.startswith(NOT_SERVED) for f in tracked()): fails.append("a mockup in 'Claude outputs/' would be served")
    # a failure exits 1 (here: an output folder that would hold the repo is refused before anything is deleted)
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        if main(['--out', ROOT]) != 1: fails.append('publish exited 0 on a failure')
    for f in fails: print('PUBLISH SELF-TEST', f)
    print(f'PUBLISH SELF-TEST: {len(fails)} problems')
    return 1 if fails else 0


def main(argv):
    if '--self-test' in argv: return self_test()
    if '--size' in argv:
        try:
            g_src, g_out = sizes()
        except (PublishError, subprocess.CalledProcessError, OSError) as e:
            print(f'PUBLISH: FAILED: {e}'); return 1
        print(size_line(g_src, g_out))
        if g_out > CEILING: print('PUBLISH: past 800 KB served: stop and ask the owner'); return 1
        return 0
    out = argv[argv.index('--out') + 1] if '--out' in argv and argv.index('--out') + 1 < len(argv) else os.path.join(ROOT, '_site')
    try:
        publish(out)
    except (PublishError, subprocess.CalledProcessError, OSError) as e:
        print(f'PUBLISH: FAILED: {e}')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
