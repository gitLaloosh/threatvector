"""Builds intel_example_controls_mockup.html: the real index.html with proto_exctl.js after its own script.

Usage: python3 -I build_exctl.py <repo>/index.html proto_exctl.js <out.html>
The page's Content-Security-Policy is taken out (it allows only the page's own script by hash); tests also use bypass_csp=True.
"""
import re
import sys

src, proto, out = sys.argv[1:4]
html = open(src, encoding='utf-8').read()
js = open(proto, encoding='utf-8').read()
html, n = re.subn(r'<meta http-equiv="Content-Security-Policy"[^>]*>\s*', '', html, count=1)
assert n == 1, 'CSP meta not found'
html = html.replace('<title>', '<title>MOCKUP · Intel example controls · ', 1)
assert html.count('</body>') == 1
html = html.replace('</body>', '<script>\n' + js + '\n</script>\n</body>')
open(out, 'w', encoding='utf-8').write(html)
print('wrote', out, len(html), 'bytes')
