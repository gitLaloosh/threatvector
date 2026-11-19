"""Builds wh_statics_mockup.html: the real index.html with data_stc.js and proto_stc.js after its own script.

Usage: python3 -I build_stc.py <repo>/index.html data_stc.js proto_stc.js <out.html>
data_stc.js comes from gen_data_stc.py (Wanderer's statics + CCP's wormhole types). The page's CSP is taken out; tests use bypass_csp too.
"""
import re, sys
src, data, proto, out = sys.argv[1:5]
html = open(src, encoding='utf-8').read()
js = open(data, encoding='utf-8').read() + '\n' + open(proto, encoding='utf-8').read()
html, n = re.subn(r'<meta http-equiv="Content-Security-Policy"[^>]*>\s*', '', html, count=1)
assert n == 1, 'CSP meta not found'
html = html.replace('<title>', '<title>MOCKUP · Statics on entry · ', 1)
assert html.count('</body>') == 1
html = html.replace('</body>', '<script>\n' + js + '\n</script>\n</body>')
open(out, 'w', encoding='utf-8').write(html)
print('wrote', out, len(html), 'bytes')
