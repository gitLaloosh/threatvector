"""Wormholes map tree mockup (Project doc claude/roadmap/wh-tree-layout-plan.md): the real page (index.html) with no network, the
repo's roadmap/paths-to-you-mockup/mock.js as its runtime (storage in memory), made-up chains, and proto_tree.js.
    python3 -I build_tree.py <repo>/index.html <repo>/roadmap/paths-to-you-mockup/mock.js <out.html>   (proto_tree.js, boot_tree.js beside this script)
Systems are EVE's public data, picked by class from the page's own table; no pilots, corporations or channels."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(sys.argv[1], encoding='utf-8').read()
J = json.loads(re.search(r'const INTEL_JUMPS = (\{.*?\});', src).group(1))
NAMES = {30000772: 'C-J6MT', 30000142: 'Jita', 30002510: 'Rens', 30002813: 'Tama'}
data = {'build': J['build'], 'homeName': 'Rens', 'me': {'id': 95000001, 'name': 'Mk Your Main'}, 'names': {str(k): v for k, v in NAMES.items()},
        'orgs': {}, 'byId': {}, 'pilots': {}, 'types': {}, 'groups': {}, 'seq': 0, 'kills': {},
        'side': {'pilot': {'id': 95000001, 'name': 'Mk Your Main'}, 'corp': None, 'alliance': None, 'friendly': [], 'hostile': [], 'rows': 15},
        'intel': {'channels': [], 'me': 95000001, 'range': 3, 'nearRange': 6, 'mapReach': 12, 'killRange': 10, 'forget': 30, 'sound': False, 'notify': False, 'nearShown': False},
        'reports': []}
CSP = '<meta http-equiv="Content-Security-Policy" content="img-src data: blob:; connect-src \'none\'; font-src data:; media-src data: blob:">'
s = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', CSP, src, count=1)
rd = lambda p: open(p, encoding='utf-8').read()
mock = rd(sys.argv[2]).replace('__MKDATA__', json.dumps(data, separators=(',', ':'), ensure_ascii=False))
i = s.index('>', s.index('<head')) + 1
s = s[:i] + '<script>' + mock + '</script>' + s[i:]
s = s.replace('<title>', '<title>MOCKUP · Wormholes map tree · ', 1)
j = s.rindex('</body>')
s = s[:j] + '<script>' + rd(os.path.join(HERE, 'proto_tree.js')) + '</script><script>' + rd(os.path.join(HERE, 'boot_tree.js')) + '</script>' + s[j:]
open(sys.argv[3], 'w', encoding='utf-8').write(s)
print('built', sys.argv[3], len(s))
