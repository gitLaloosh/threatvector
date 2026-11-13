"""Wormholes list Export / Import mockup (plan claude/roadmap/wormholes-export-import-plan.md): the real page (index.html, main 60d75f1,
v2026.11.12.6, after 045) with
- 044's list changes (the patches below and proto_sig044.js: a stand-in copied from claude/roadmap/wormhole-sig-ids-mockup/, probe scan left
  out, plus 044's per-ID removal mark), so the list has signature IDs, details and raw lines to export;
- this plan's Export and Import (proto_xi.js), and the MOCKUP bar (mk_xi.js);
- a made-up list already in the browser (SEED) and made-up Intel around C-J6MT (mock.js, boot_wh.js: as the Wormholes filter mockups).
python3 -I build_xi.py <repo>/index.html <out.html>
Systems: k-space names and ids from the page's own map table (as the earlier mockups); everyone and every group is invented ("Mk ..." / "Mockup ...")."""
import json, os, re, sys
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
REP = [(90, 'Mk Gate Watcher', '78-0R6 Mk Raider One Sabre'), (400, 'Mk Scout Alt', 'MSG-BZ clr'), (700, 'Mk Gate Watcher', 'YPW-M4 Mk Raider Two Muninn +3')]
data = {'build': J['build'], 'homeName': 'C-J6MT', 'me': {'id': 95000001, 'name': 'Mk Your Main'},
        'names': {str(k): v for k, v in NAMES.items()},
        'orgs': {str(k): v for k, v in ORGS.items()}, 'byId': {str(k): [v[0], v[1]] for k, v in PIL.items()},
        'pilots': {v[0].lower(): k for k, v in PIL.items()},
        'types': {str(v[0]): [k, v[1]] for k, v in T.items()}, 'groups': {str(k): v for k, v in GROUPS.items()}, 'seq': 70000,
        'side': {'pilot': {'id': 95000001, 'name': 'Mk Your Main'}, 'corp': {'id': CORP, 'name': 'Mockup Shipyards'}, 'alliance': {'id': ALLI, 'name': 'Mockup Coalition'},
                 'friendly': [], 'hostile': [{'id': HALLI, 'name': 'Mockup Raiders', 'kind': 'alliance'}], 'rows': 15},
        'intel': {'channels': ['region.intel'], 'me': 95000001, 'range': 3, 'nearRange': 6, 'mapReach': 10, 'killRange': 10, 'forget': 30, 'sound': False, 'notify': False},
        'reports': sorted(REP, reverse=True)}
# your list, already in this browser (044's shape): a hand value of yours, a repeat (×2), a part, a removed ID, an 040-era entry, a removed system
SEED = r"""(() => { const n = Date.now(), m = (x) => n - x * 60000;
  const rep = {
    30000772: {id: 30000772, t: m(20), who: '', drifter: false, src: 'you',
      sigs: [{sig: 'RZL-429', part: false, type: 'Z971', info: {cls: 'C1-3', life: 'lt1d', mass: 'stable', size: 'medium'}, t: m(20), who: ''}, {sig: 'MKV', part: true, type: '', info: {mass: 'critical'}, t: m(30), who: 'Mk Gate Watcher'}],
      raws: [{t: m(20), who: '', raw: 'C-J6MT RZL-429 mass >50%', k: 'you', set: {sigs: [{sig: 'RZL-429', part: false, type: '', info: {mass: 'stable'}}]}},
             {t: m(30), who: 'Mk Gate Watcher', raw: 'C-J6MT wh sig MKV crit', k: 'intel', n: 2},
             {t: m(60), who: 'Mk Scout Alt', raw: 'C-J6MT wh rzl-429 z971 class 1-3 medium size less then 1 day less then 50% mass', k: 'intel'}]},
    30000780: {id: 30000780, t: m(200), who: 'Mk Gate Watcher', drifter: false, src: 'intel', sigs: [{sig: 'QDX', part: true, type: '', t: m(200), who: 'Mk Gate Watcher'}],
      raws: [{t: m(200), who: 'Mk Gate Watcher', raw: 'RERZ-L wh sig QDX', k: 'intel'}]},
    30000796: {id: 30000796, t: m(380), who: 'Mk Gate Watcher', drifter: true, drN: 1, src: 'intel', goneSig: {'KLM-204': m(30)},
      sigs: [{sig: 'XRT-331', part: false, type: '', t: m(380), who: 'Mk Gate Watcher'}, {sig: 'BKT-772', part: false, type: '', dr: true, t: m(600), who: 'Mk Scout Alt'}],
      raws: [{t: m(380), who: 'Mk Gate Watcher', raw: 'EUU-4N wh XRT-331 Mk Raider One Sabre [MKRC]', k: 'intel'}, {t: m(600), who: 'Mk Scout Alt', raw: 'EUU-4N drifter hole BKT772', k: 'intel'}]},
    30000458: {id: 30000458, t: m(120), who: 'Mk Scout Alt', drifter: false, src: 'intel'}
  };
  localStorage.setItem('tvWormholes', JSON.stringify({v: 1, rep, gone: {30000779: m(100)}, keepH: 24}));
})();"""
CSP = '<meta http-equiv="Content-Security-Policy" content="img-src data: blob:; connect-src \'none\'; font-src data:; media-src data: blob:">'
s = re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]*>', CSP, src, count=1)
rd = lambda n: open(os.path.join(HERE, n), encoding='utf-8').read()
# 044's list patches (from claude/roadmap/wormhole-sig-ids-mockup/build_sig.py; the probe scan, map ring and colour patches left out: 045 made
# the ring and the colour), then this plan's two
PATCHES = [
  ("  const W = itWords(msg), used = new Array(W.length).fill(null);\n",
   "  const W = itWords(msg), used = new Array(W.length).fill(null);\n  const whd = itWhDetails(W, used);   // 044: the wormhole's IDs and details, before systems and pilots\n"),
  ("  return {W, used, sys, ships, kw, extra, count, mentions,", "  return {whd, W, used, sys, ships, kw, extra, count, mentions,"),
  ("  st.rep[sys] = {id: sys, t: e.t, who: String(e.who || '').slice(0, 64), drifter: w === 'drifter', src: 'intel'};",
   "  st.rep[sys] = {id: sys, t: e.t, who: String(e.who || '').slice(0, 64), drifter: w === 'drifter', src: 'intel', sigs: itWhSigMerge(r, e), info: itWhRepInfo(r, e), drNoId: itWhDrNoId(r, e, w), raws: itWhRawKeep(r, e), ...(r && r.goneSig ? {goneSig: r.goneSig} : {})}; itWhDrSet(st.rep[sys]);"),
  ("  if(whw) tags.push(itWhBadgeHtml(whw === 'drifter', itWhBadgeTitle({drifter: whw === 'drifter', who: e.who, t: e.t})));",
   "  if(whw) tags.push(itWhBadgeHtml(whw === 'drifter', itWhBadgeTitle({drifter: whw === 'drifter', who: e.who, t: e.t})) + itWhLineHtml(e.p.whd));"),
  ("  if(wh) out.push(itWhBadgeHtml(wh.drifter, itWhBadgeTitle(wh)));", "  if(wh) out.push(itWhBadgeHtml(wh.drifter, itWhBadgeTitle(wh)) + itWhSigsHtml(wh.sigs, 2) + itWhInfoHtml(wh.info, wh.t));"),
  ('<span class="it-whp-by">${escapeHtml(by)}</span>', '<span class="it-whp-by">${itWhRawTog(w)}${itWhSigsHtml(w.sigs, 4, {rm: w.id})}${itWhInfoHtml(w.info, w.t)}${escapeHtml(by)}</span>'),
  ("function itMapWhLabel(w){ return `${w.drifter ? 'DRIFTER' : 'WH'} · ${itWhAge(w.t)}`; }",
   "function itMapWhLabel(w){ const s = Array.isArray(w.sigs) && w.sigs[0]; return `${w.drifter ? `DRIFTER${w.drN > 1 ? ` ×${w.drN}` : ''}` : 'WH'}${s ? ` ${s.sig}${s.part ? '…' : ''}${s.type ? `→${itWhDestTxt(s.type)[0]}` : ''}${w.sigs.length > 1 ? ` +${w.sigs.length - 1}` : ''}` : ''} · ${itWhAge(w.t)}`; }"),
  ("<label><input type=\"checkbox\" name=\"dr\"> Drifter</label><button type=\"submit\">Add</button></form>'",
   "<label><input type=\"checkbox\" name=\"dr\"> Drifter</label><button type=\"submit\">Add</button>' + itWhAddMoreHtml() + '</form>'"),
  ("      const f = e.target, r = itWhAdd(f.sys.value, f.dr.checked);", "      const f = e.target, r = itWhAddFull(f);"),
  ("      if(r.ok){ f.sys.value = ''; f.dr.checked = false; f.sys.removeAttribute('aria-invalid'); } else f.sys.setAttribute('aria-invalid', 'true');\n      f.sys.focus();",
   "      for(const k of ['sys', 'sig', 'ty']) f[k].removeAttribute('aria-invalid');\n      if(r.ok){ f.sys.value = ''; f.dr.checked = false; } else f[r.field || 'sys'].setAttribute('aria-invalid', 'true');\n      f[(!r.ok && r.field) || 'sys'].focus();"),
  ("    itWhL.el = p;\n", "    p.querySelector('input[name=ty]').addEventListener('input', () => itWhTypeHint(p.querySelector('form')));\n    itWhL.el = p;\n"),
  (">Remove</button></div>`;", ">Remove</button>${itWhRawHtml(w)}</div>`;"),
  # 044 reads back its own fields (the 040 reader keeps five); a stand-in for 044's own checks
  ("    st.rep[id] = {id, t, who: typeof w.who === 'string' ? w.who.slice(0, 64) : '', drifter: w.drifter === true, src: w.src === 'you' ? 'you' : 'intel'};",
   "    st.rep[id] = {id, t, who: typeof w.who === 'string' ? w.who.slice(0, 64) : '', drifter: w.drifter === true, src: w.src === 'you' ? 'you' : 'intel', ...itWhReadMore(w)};"),
  # this plan (D1): the Export / Import row and boxes under the Add form, and their clicks
  ("      + '<div class=\"it-whp-msg\" role=\"status\"></div><div class=\"it-whp-rows\"></div>';",
   "      + itWhShareHtml() + '<div class=\"it-whp-msg\" role=\"status\"></div><div class=\"it-whp-rows\"></div>';"),
  ("      if(e.target.closest('[data-it-whx]')){ itWhListOpen(false); return; }",
   "      if(e.target.closest('[data-it-whx]')){ itWhListOpen(false); return; }\n      if(itWhListClick(e, p) || itWhShareClick(e, p)) return;   // 044's row clicks; this plan's Export / Import"),
]
for a, b in PATCHES:
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
mock = rd('mock.js').replace('__MKDATA__', json.dumps(data, separators=(',', ':'), ensure_ascii=False))
i = s.index('>', s.index('<head')) + 1
s = s[:i] + '<script>' + mock + '</script><script>' + SEED + '</script><script>' + rd('proto_sig044.js') + '</script><script>' + rd('proto_xi.js') + '</script>' + s[i:]
j = s.rindex('</body>')
s = s[:j] + '<script>' + rd('boot_wh.js') + '</script><script>' + rd('mk_xi.js') + '</script>' + s[j:]
open(sys.argv[2], 'w', encoding='utf-8').write(s)
print('built', sys.argv[2], len(s))
