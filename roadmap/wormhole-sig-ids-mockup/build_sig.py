"""Wormhole signature IDs mockup: the real page (index.html, main d227c9d, after 040) with made-up Intel around C-J6MT, 18 small patches to
index.html (PATCHES below: what the build would change) and proto_sig.js (the new functions), mk_sig.js (the MOCKUP bar).
python3 -I build_sig.py <repo>/index.html <out.html>   (mock.js, proto_sig.js, mk_sig.js, boot_wh.js beside this script)
Far systems (Jita, Amarr, Tama, 1DQ1-A, Amamake): ids checked against the page's own map table (regions The Forge, Domain, The Citadel, Delve, Heimatar).
Systems: k-space names from ref-data.everef.net (checked 2026-11-11, as the map-look mockup); wormhole systems are made up (J99xxxx,
past the real J-names). Everyone and every group is invented ("Mk ..." / "Mockup ...")."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(sys.argv[1], encoding='utf-8').read()
J = json.loads(re.search(r'const INTEL_JUMPS = (\{.*?\});', src).group(1))
NAMES = {30000772: 'C-J6MT', 30000773: '78-0R6', 30000780: 'RERZ-L', 30000779: 'SHBF-V', 30000781: '0UBC-R', 30000796: 'EUU-4N',
         30000543: '0TYR-T', 30000458: '9N-0HF', 30000771: '8G-2FP', 30000786: 'L5-UWT', 30000776: '4M-QXK', 30000774: 'MSG-BZ',
         30000788: 'I-1QKL', 30000784: 'YPW-M4', 30000775: '8-WYQZ', 30000778: 'G-EURJ', 30000782: '3U-48K',
         30000142: 'Jita', 30002187: 'Amarr', 30002813: 'Tama', 30004759: '1DQ1-A', 30002537: 'Amamake'}
CORP, ALLI, HC1, HALLI = 98100001, 99100001, 98100002, 99100002
ORGS = {CORP: ['corporation', 'Mockup Shipyards', 'MKSY', ALLI], ALLI: ['alliance', 'Mockup Coalition', 'MKCO', None],
        HC1: ['corporation', 'Mockup Raider Corp', 'MKRC', HALLI], HALLI: ['alliance', 'Mockup Raiders', 'MKRD', None]}
WC = 98100003
ORGS_X = {WC: ['corporation', 'Mockup Word Corp', 'MKWC', None]}
# made-up characters named like plain words, so "Today" shows what the page does now with "class" and "then" in a wormhole line
PIL = {95000001: ('Mk Your Main', CORP), 95000011: ('Mk Raider One', HC1), 95000012: ('Mk Raider Two', HC1), 95000021: ('Class', WC), 95000022: ('Then', WC)}
ORGS.update(ORGS_X)
T = {'Sabre': (22456, 541), 'Muninn': (12015, 358)}
GROUPS = {541: 'Interdictor', 358: 'Heavy Assault Cruiser'}
REP = [(30, 'Mk Gate Watcher', 'C-J6MT wh sig MKV crit'),
       (60, 'Mk Scout Alt', 'C-J6MT wh rzl-429 z971 class 1-3 medium size less then 1 day less then 50% mass'),
       (200, 'Mk Gate Watcher', 'RERZ-L wh sig QDX'),
       (420, 'Mk Scout Alt', 'SHBF-V 2 wh xyz-123 h296 and pqr-4 k162'),
       (600, 'Mk Gate Watcher', 'EUU-4N drifter hole BKT772'),
       (500, 'Mk Scout Alt', 'EUU-4N drifter KLM-204 frig hole'),
       (380, 'Mk Gate Watcher', 'EUU-4N wh XRT-331'),
       (800, 'Mk Scout Alt', '78-0R6 Mk Raider One Sabre')]
data = {'build': J['build'], 'homeName': 'C-J6MT', 'me': {'id': 95000001, 'name': 'Mk Your Main'},
        'names': {str(k): v for k, v in NAMES.items()},
        'orgs': {str(k): v for k, v in ORGS.items()}, 'byId': {str(k): [v[0], v[1]] for k, v in PIL.items()},
        'pilots': {v[0].lower(): k for k, v in PIL.items()},
        'types': {str(v[0]): [k, v[1]] for k, v in T.items()}, 'groups': {str(k): v for k, v in GROUPS.items()}, 'seq': 70000,
        'side': {'pilot': {'id': 95000001, 'name': 'Mk Your Main'}, 'corp': {'id': CORP, 'name': 'Mockup Shipyards'}, 'alliance': {'id': ALLI, 'name': 'Mockup Coalition'},
                 'friendly': [], 'hostile': [{'id': HALLI, 'name': 'Mockup Raiders', 'kind': 'alliance'}], 'rows': 15},
        'intel': {'channels': ['region.intel'], 'me': 95000001, 'range': 3, 'nearRange': 6, 'mapReach': 10, 'killRange': 10, 'forget': 30, 'sound': False, 'notify': False},
        'reports': sorted(REP, reverse=True)}
CSP = '<meta http-equiv="Content-Security-Policy" content="img-src data: blob:; connect-src \'none\'; font-src data:; media-src data: blob:">'
s = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', CSP, src, count=1)
rd = lambda n: open(os.path.join(HERE, n), encoding='utf-8').read()
PATCHES = [
  ("  const W = itWords(msg), used = new Array(W.length).fill(null);\n",
   "  const W = itWords(msg), used = new Array(W.length).fill(null);\n  const whd = itWhDetails(W, used);   // the wormhole's signature IDs, type and the words describing it, before systems and pilots\n"),
  ("  return {W, used, sys, ships, kw, extra, count, mentions,", "  return {whd, W, used, sys, ships, kw, extra, count, mentions,"),
  ("  st.rep[sys] = {id: sys, t: e.t, who: String(e.who || '').slice(0, 64), drifter: w === 'drifter', src: 'intel'};",
   "  st.rep[sys] = {id: sys, t: e.t, who: String(e.who || '').slice(0, 64), drifter: w === 'drifter', src: 'intel', sigs: itWhSigMerge(r, e), info: itWhRepInfo(r, e), drNoId: itWhDrNoId(r, e, w), raws: itWhRawKeep(r, e)}; itWhDrSet(st.rep[sys]);"),
  ("  if(whw) tags.push(itWhBadgeHtml(whw === 'drifter', itWhBadgeTitle({drifter: whw === 'drifter', who: e.who, t: e.t})));",
   "  if(whw) tags.push(itWhBadgeHtml(whw === 'drifter', itWhBadgeTitle({drifter: whw === 'drifter', who: e.who, t: e.t})) + itWhLineHtml(e.p.whd));"),
  ("  if(wh) out.push(itWhBadgeHtml(wh.drifter, itWhBadgeTitle(wh)));", "  if(wh) out.push(itWhBadgeHtml(wh.drifter, itWhBadgeTitle(wh)) + itWhSigsHtml(wh.sigs, 2) + itWhInfoHtml(wh.info, wh.t));"),
  ('<span class="it-whp-by">${escapeHtml(by)}</span>', '<span class="it-whp-by">${itWhRawTog(w)}${itWhSigsHtml(w.sigs, 4, {rm: w.id})}${itWhInfoHtml(w.info, w.t)}${escapeHtml(by)}</span>'),
  ("function itMapWhLabel(w){ return `${w.drifter ? 'DRIFTER' : 'WH'} · ${itWhAge(w.t)}`; }",
   "function itMapWhLabel(w){ const s = Array.isArray(w.sigs) && w.sigs[0]; return `${w.drifter ? `DRIFTER${w.drN > 1 ? ` ×${w.drN}` : ''}` : 'WH'}${s ? ` ${s.sig}${s.part ? '…' : ''}${s.type ? `→${itWhDestTxt(s.type)[0]}` : s.info && s.info.cls ? ` ${itWhClsTxt(s.info.cls)[0]}` : ''}${w.sigs.length > 1 ? ` +${w.sigs.length - 1}` : ''}` : ''} · ${itWhAge(w.t)}`; }"),
  ("      + '<div class=\"it-whp-msg\" role=\"status\"></div><div class=\"it-whp-rows\"></div>';",
   "      + itWhScanBoxHtml() + '<div class=\"it-whp-msg\" role=\"status\"></div><div class=\"it-whp-rows\"></div>';"),
  ("      if(e.target.closest('[data-it-whx]')){ itWhListOpen(false); return; }",
   "      if(e.target.closest('[data-it-whx]')){ itWhListOpen(false); return; }\n      if(itWhScanClick(e, p)) return;   // the probe scan, pasted"),
  ("    c.strokeStyle = itMapWhCol(w); c.beginPath(); c.arc(x, y, r1, 0, 6.283); c.moveTo(x + r2, y); c.arc(x, y, r2, 0, 6.283); c.stroke();",
   "    itWhRingDraw(c, x, y, r1, r2, w);   // split by kind: plain and Drifter holes in one system share the rings"),
  ("reported ${itMapSwHtml([itMapWhCol({drifter: true})])} Drifter · last",
   "reported ${itMapSwHtml([itMapWhCol({drifter: true})])} Drifter · split: both · last"),
  ("  :root{--it-wh:#a98bd8; --it-wh-drifter:#e4b5ff;}", "  :root{--it-wh:#a98bd8; --it-wh-drifter:#ff5fbf;}   /* Drifter: hot pink (and dashed on the map), the owner's pick */"),
  ("itMapCol('--it-wh-drifter', '#e4b5ff')", "itMapCol('--it-wh-drifter', '#ff5fbf')"),
  ("<label><input type=\"checkbox\" name=\"dr\"> Drifter</label><button type=\"submit\">Add</button></form>'",
   "<label><input type=\"checkbox\" name=\"dr\"> Drifter</label><button type=\"submit\">Add</button>' + itWhAddMoreHtml() + '</form>'"),
  ("      const f = e.target, r = itWhAdd(f.sys.value, f.dr.checked);", "      const f = e.target, r = itWhAddFull(f);   // the system, and any of: signature ID, type, life, mass, size, Drifter"),
  ("      if(r.ok){ f.sys.value = ''; f.dr.checked = false; f.sys.removeAttribute('aria-invalid'); } else f.sys.setAttribute('aria-invalid', 'true');\n      f.sys.focus();",
   "      for(const k of ['sys', 'sig', 'ty']) f[k].removeAttribute('aria-invalid');\n      if(r.ok){ f.sys.value = ''; f.dr.checked = false; } else f[r.field || 'sys'].setAttribute('aria-invalid', 'true');\n      f[(!r.ok && r.field) || 'sys'].focus();"),
  ("    itWhL.el = p;\n", "    p.querySelector('input[name=ty]').addEventListener('input', () => itWhTypeHint(p.querySelector('form')));\n    itWhL.el = p;\n"),
  (">Remove</button></div>`;", ">Remove</button>${itWhRawHtml(w)}</div>`;"),
]
for a, b in PATCHES:
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
mock = rd('mock.js').replace('__MKDATA__', json.dumps(data, separators=(',', ':'), ensure_ascii=False))
i = s.index('>', s.index('<head')) + 1
s = s[:i] + '<script>' + mock + '</script><script>window.__SIGOFF = location.hash === "#today";</script><script>' + rd('proto_sig.js') + '</script>' + s[i:]   # in the head: Intel can read lines while the page loads
j = s.rindex('</body>')
s = s[:j] + '<script>' + rd('boot_wh.js') + '</script><script>' + rd('mk_sig.js') + '</script>' + s[j:]
open(sys.argv[2], 'w', encoding='utf-8').write(s)
print('built', sys.argv[2], len(s))
