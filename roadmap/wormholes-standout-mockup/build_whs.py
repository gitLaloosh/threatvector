"""Wormholes standing out on the Intel map's Wormholes filter (requirement 8 of roadmap/wormhole-mapping-plan.md; the owner: "yes please" to
mocking options 1-4 together, with 5 as a toggle). The real page (index.html, main d227c9d, after 040) patched in place (PATCHES, each found
exactly once), plus made-up busy Intel around C-J6MT so the wormholes have something to get lost in.
python3 -I build_whs.py <repo>/index.html <out.html>   (mock.js, boot_wh.js, proto_whs.js beside this script)
The MOCKUP bar turns the new look on and off (to compare with today's) and the "N wormholes" chip on and off.
Systems: k-space names from ref-data.everef.net (as the earlier mockups); everyone and every group is invented ("Mk ..." / "Mockup ...").
Built (build queue 045, v2026.11.12.6): the page itself now has the look, so this script runs only on a page from before it (main 25d3ae2
or older): `git show 25d3ae2:index.html > old.html`."""
import json, os, re, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(sys.argv[1], encoding='utf-8').read()
J = json.loads(re.search(r'const INTEL_JUMPS = (\{.*?\});', src).group(1))
NAMES = {30000772: 'C-J6MT', 30000773: '78-0R6', 30000780: 'RERZ-L', 30000779: 'SHBF-V', 30000781: '0UBC-R', 30000796: 'EUU-4N',
         30000543: '0TYR-T', 30000458: '9N-0HF', 30000771: '8G-2FP', 30000786: 'L5-UWT', 30000776: '4M-QXK', 30000774: 'MSG-BZ',
         30000788: 'I-1QKL', 30000784: 'YPW-M4', 30000775: '8-WYQZ', 30000778: 'G-EURJ', 30000782: '3U-48K'}
CORP, ALLI, HC1, HALLI = 98100001, 99100001, 98100002, 99100002
ORGS = {CORP: ['corporation', 'Mockup Shipyards', 'MKSY', ALLI], ALLI: ['alliance', 'Mockup Coalition', 'MKCO', None],
        HC1: ['corporation', 'Mockup Raider Corp', 'MKRC', HALLI], HALLI: ['alliance', 'Mockup Raiders', 'MKRD', None]}
PIL = {95000001: ('Mk Your Main', CORP), 95000011: ('Mk Raider One', HC1), 95000012: ('Mk Raider Two', HC1)}
T = {'Sabre': (22456, 541), 'Muninn': (12015, 358)}
GROUPS = {541: 'Interdictor', 358: 'Heavy Assault Cruiser'}
# busy Intel: hostiles with counts, clears, a neutral, and wormholes (fresh, a Drifter, one beside a hostile report)
REP = [(40, 'Mk Gate Watcher', '78-0R6 Mk Raider One Sabre +3'),
       (120, 'Mk Scout Alt', 'L5-UWT Mk Raider Two +6'),
       (150, 'Mk Scout Alt', 'L5-UWT wh'),
       (200, 'Mk Gate Watcher', 'I-1QKL clr'),
       (260, 'Mk Gate Watcher', '4M-QXK Mk Raider One'),
       (300, 'Mk Scout Alt', 'RERZ-L wh on the sun'),
       (380, 'Mk Gate Watcher', 'MSG-BZ nv +2'),
       (450, 'Mk Scout Alt', 'YPW-M4 Mk Raider Two Muninn +19'),
       (520, 'Mk Gate Watcher', 'EUU-4N drifter hole spotted'),
       (600, 'Mk Scout Alt', '3U-48K clr'),
       (700, 'Mk Scout Alt', 'SHBF-V Mk Raider Two Muninn'),
       (900, 'Mk Gate Watcher', '8-WYQZ clr'),
       (1000, 'Mk Gate Watcher', 'G-EURJ Mk Raider One +2'),
       (1300, 'Mk Scout Alt', '0UBC-R wh')]
data = {'build': J['build'], 'homeName': 'C-J6MT', 'me': {'id': 95000001, 'name': 'Mk Your Main'},
        'names': {str(k): v for k, v in NAMES.items()},
        'orgs': {str(k): v for k, v in ORGS.items()}, 'byId': {str(k): [v[0], v[1]] for k, v in PIL.items()},
        'pilots': {v[0].lower(): k for k, v in PIL.items()},
        'types': {str(v[0]): [k, v[1]] for k, v in T.items()}, 'groups': {str(k): v for k, v in GROUPS.items()}, 'seq': 70000,
        'side': {'pilot': {'id': 95000001, 'name': 'Mk Your Main'}, 'corp': {'id': CORP, 'name': 'Mockup Shipyards'}, 'alliance': {'id': ALLI, 'name': 'Mockup Coalition'},
                 'friendly': [], 'hostile': [{'id': HALLI, 'name': 'Mockup Raiders', 'kind': 'alliance'}], 'rows': 15},
        'intel': {'channels': ['region.intel'], 'me': 95000001, 'range': 3, 'nearRange': 6, 'mapReach': 10, 'killRange': 10, 'forget': 30, 'sound': False, 'notify': False},
        'reports': sorted(REP, reverse=True)}
# older wormholes already in the store (kept 24 h): one 2 h old, a Drifter 5 h old, one 40 min old
SEED = "(() => { const n = Date.now(), r = {}; for(const [id, m, dr] of [[30000458, 120, false], [30000771, 300, true], [30000775, 40, false]]) r[id] = {id, t: n - m * 60000, who: 'Mk Scout Alt', drifter: dr, src: 'intel'}; localStorage.setItem('tvWormholes', JSON.stringify({v: 1, rep: r, gone: {}, keepH: 24})); })();"

# ---- the patches: each (what it does, old, new); old must be found exactly once ----
PATCHES = [
 ('whS: the new look, on the Wormholes filter only (window.__WHS turns it off to compare)',
  "  const whF = itm.filter === 'wh', alpha = ",
  "  const whF = itm.filter === 'wh', whS = whF && window.__WHS !== false, alpha = "),
 ('1: the alert range\'s amber wash faded',
  "  c.fillStyle = 'rgba(217,154,60,.07)';\n  for(const i of itm.vis) if(D[i] <= it.set.range && seen(i))",
  "  c.fillStyle = whS ? 'rgba(217,154,60,.02)' : 'rgba(217,154,60,.07)';\n  for(const i of itm.vis) if(D[i] <= it.set.range && seen(i))"),
 ('1: other reports\' rings, glow and fill at about 20% (a report in a wormhole system keeps its strength)',
  "      c.save(); c.shadowColor = col; c.shadowBlur = 10; c.strokeStyle = col; c.lineWidth = big ? 2.5 : 2.2; c.globalAlpha = 0.95; c.beginPath(); c.arc(X(i), Y(i), rad, 0, 6.283); c.stroke(); c.restore();\n      if(!big){ c.fillStyle = col; c.globalAlpha = 0.12;",
  "      const fade = whS && !itm.wh.kept.has(i);\n      c.save(); c.shadowColor = col; c.shadowBlur = fade ? 0 : 10; c.strokeStyle = col; c.lineWidth = big ? 2.5 : 2.2; c.globalAlpha = fade ? 0.2 : 0.95; c.beginPath(); c.arc(X(i), Y(i), rad, 0, 6.283); c.stroke(); c.restore();\n      if(!big){ c.fillStyle = col; c.globalAlpha = fade ? 0.03 : 0.12;"),
 ('2 and 3: the bolder mark (a filled disc with a glow and a ring; a Drifter pink and dashed, as 044), and the fresh ones listed for the pulse',
  "  c.lineWidth = 1.6; c.globalAlpha = 1;\n  for(const [i, w] of itm.wh.mark){\n    if(!seen(i)) continue;\n    const x = X(i), y = Y(i), r1 = big ? r + 3 : 4.5, r2 = big ? r + 7 : 8.5;\n    c.strokeStyle = itMapWhCol(w); c.beginPath(); c.arc(x, y, r1, 0, 6.283); c.moveTo(x + r2, y); c.arc(x, y, r2, 0, 6.283); c.stroke();\n  }",
  "  c.lineWidth = 1.6; c.globalAlpha = 1; itm.whPulse = [];\n  for(const [i, w] of itm.wh.mark){\n    if(!seen(i)) continue;\n    const x = X(i), y = Y(i), r1 = big ? r + 3 : 4.5, r2 = big ? r + 7 : 8.5;\n    if(whS){ itMapWhBold(c, x, y, w, big, r); if(Date.now() - w.t < 30 * 60000) itm.whPulse.push([i, w]); continue; }\n    c.strokeStyle = itMapWhCol(w); c.beginPath(); c.arc(x, y, r1, 0, 6.283); c.moveTo(x + r2, y); c.arc(x, y, r2, 0, 6.283); c.stroke();\n  }\n  itm.whBig = big ? r : 0;"),
 ('4: on the new look a label may sit over a faded system\'s dot (only the wormholes\' marks and your pin keep their room)',
  "  const WH = itm.wh || {mark: new Map()}, mk = (i) => itm.rep.has(i) || WH.mark.has(i);   // 040: a wormhole's rings take room like a report's\n  for(let i = 0; i < itm.D.length; i++){ const x = Q[2 * i], y = Q[2 * i + 1]; if(x < -10 || y < -10 || x > W + 10 || y > H + 10) continue;",
  "  const WH = itm.wh || {mark: new Map()}, mk = (i) => itm.rep.has(i) || WH.mark.has(i);   // 040: a wormhole's rings take room like a report's\n  const whS = itm.filter === 'wh' && window.__WHS !== false;\n  for(let i = 0; i < itm.D.length; i++){ const x = Q[2 * i], y = Q[2 * i + 1]; if(x < -10 || y < -10 || x > W + 10 || y > H + 10) continue; if(whS && !WH.mark.has(i) && i !== itm.home) continue;"),
 ('1 and 4: labels: only the wormholes\' (and yours); a wormhole\'s tag a filled pill in its colour',
  "  const whTag = (i) => { const w = WH.mark.get(i); return w ? [{t: itMapWhLabel(w), bg: 'rgba(12,16,20,.85)', col: itMapWhCol(w), font: TAG}] : []; };",
  "  const whTag = (i) => { const w = WH.mark.get(i); return w ? [whS ? {t: itMapWhLabel(w), bg: itMapWhBoldCol(w), col: '#0c1014', font: TAG} : {t: itMapWhLabel(w), bg: 'rgba(12,16,20,.85)', col: itMapWhCol(w), font: TAG}] : []; };"),
 ('1: a report without a wormhole gets no label on the new look; one with a wormhole keeps its name and the pill (its count tags dropped)',
  "  for(const i of order) put(i, [{t: nm(i), col: i === focus ? C.cyan : '#d7dee3', font: F}, ...tags(itm.rep.get(i)), ...whTag(i)], true);",
  "  for(const i of order){ if(!whS){ put(i, [{t: nm(i), col: i === focus ? C.cyan : '#d7dee3', font: F}, ...tags(itm.rep.get(i)), ...whTag(i)], true); continue; }\n    if(!WH.mark.has(i) && i !== focus) continue;   // the new look: a wormhole's report like any wormhole: its name and pill where they fit, else the pill alone, never over another label\n    const n0 = itm.labels.length; put(i, [{t: nm(i), col: i === focus ? C.cyan : '#d7dee3', font: F}, ...whTag(i)], i === focus); if(itm.labels.length === n0) put(i, whTag(i), false); }"),
 ('4: on the new look a label may sit a step further out (24 px) when the near spots are taken',
  "    for(const m of [0, 12]) spots.push(",
  "    for(const m of (itm.filter === 'wh' && window.__WHS !== false ? [0, 12, 24] : [0, 12])) spots.push("),
 ('4: on the new look a wormhole inside "Map: within" with no room for its name gets its pill alone, where that fits (never over another label)',
  "    put(i, [...(named ? [{t: nm(i), col: i === focus ? C.cyan : '#d7dee3', font: F}] : []), ...whTag(i)], live || i === focus); }",
  "    const n0 = itm.labels.length; put(i, [...(named ? [{t: nm(i), col: i === focus ? C.cyan : '#d7dee3', font: F}] : []), ...whTag(i)], (live && !whS) || i === focus); if(whS && itm.labels.length === n0) put(i, whTag(i), false); }"),
 ('4: route names along a hovered route stay, but faint, on the new look (unchanged)',
  "  for(const i of onRoute) if(i !== itm.home && i !== focus && !itm.rep.has(i) && !WH.mark.has(i))",
  "  for(const i of onRoute) if(i !== itm.home && i !== focus && !(itm.rep.has(i) && !whS) && !WH.mark.has(i))"),
]
for what, old, new in PATCHES:
    n = src.count(old)
    if n != 1: sys.exit(f'patch not found exactly once ({n}): {what}')
    src = src.replace(old, new)
CSP = '<meta http-equiv="Content-Security-Policy" content="img-src data: blob:; connect-src \'none\'; font-src data:; media-src data: blob:">'
s = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', CSP, src, count=1)
rd = lambda n: open(os.path.join(HERE, n), encoding='utf-8').read()
mock = rd('mock.js').replace('__MKDATA__', json.dumps(data, separators=(',', ':'), ensure_ascii=False))
i = s.index('>', s.index('<head')) + 1
s = s[:i] + '<script>' + mock + SEED + '</script><script>' + rd('proto_whs.js') + '</script>' + s[i:]
j = s.rindex('</body>')
s = s[:j] + '<script>' + rd('boot_wh.js') + '</script><script>window.__WHS_BAR && window.__WHS_BAR();</script>' + s[j:]
open(sys.argv[2], 'w', encoding='utf-8').write(s)
print('built', sys.argv[2], len(s), f'({len(PATCHES)} patches)')
