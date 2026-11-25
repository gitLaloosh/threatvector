"""Mass panel follow-up mockup (saved runs, + Finisher, odds split): the real page (index.html, main a02d876 / v2026.11.24.1) with a made-up
wormhole chain, made-up saved fits and proto_rr.js (Project doc claude/roadmap/hole-mass-runs-plan.md).
python3 -I build_rr.py <repo>/index.html <out.html>   (proto_rr.js and boot_rr.js beside this script)
Fit names and ship masses are invented; systems and hole types are EVE's public data (CCP's SDE, as in the page)."""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(sys.argv[1], encoding='utf-8').read()
CSP = '<meta http-equiv="Content-Security-Policy" content="img-src data: blob:; connect-src \'none\'; font-src data:; media-src data: blob:">'
s, n = re.subn(r'<meta http-equiv="Content-Security-Policy"[^>]*>', CSP, src, count=1)
if n != 1: sys.exit('no CSP meta found')
rd = lambda f: open(os.path.join(HERE, f), encoding='utf-8').read()
s = s.replace('<title>', '<title>MOCKUP · Saved runs and finishers · ', 1)
j = s.rindex('</body>')
s = s[:j] + '<script>' + rd('proto_rr.js') + '</script><script>' + rd('boot_rr.js') + '</script>' + s[j:]
open(sys.argv[2], 'w', encoding='utf-8').write(s)
print('built', sys.argv[2], len(s))
