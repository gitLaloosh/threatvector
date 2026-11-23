"""Mass (crit or roll a hole) mockup: the real page (index.html, main 4c28fdd / v2026.11.22.1) with a made-up wormhole chain, made-up saved
fits and proto_hm.js (Project doc claude/roadmap/hole-mass-plan.md).
python3 -I build_hm.py <repo>/index.html <out.html>   (proto_hm.js and boot_hm.js beside this script)
Fit names are invented; systems, hole types, hull masses and module masses are EVE's public data (CCP's SDE)."""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(sys.argv[1], encoding='utf-8').read()
CSP = '<meta http-equiv="Content-Security-Policy" content="img-src data: blob:; connect-src \'none\'; font-src data:; media-src data: blob:">'
s = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', CSP, src, count=1)
rd = lambda n: open(os.path.join(HERE, n), encoding='utf-8').read()
s = s.replace('<title>', '<title>MOCKUP · Crit or roll a hole · ', 1)
j = s.rindex('</body>')
s = s[:j] + '<script>' + rd('proto_hm.js') + '</script><script>' + rd('boot_hm.js') + '</script>' + s[j:]
open(sys.argv[2], 'w', encoding='utf-8').write(s)
print('built', sys.argv[2], len(s))
