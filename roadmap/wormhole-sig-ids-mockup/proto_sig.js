// Mockup 2026-11-12 (research session): wormhole report details. In a line that names a wormhole (wh, wormhole, drifter), the parser
// reads the cosmic signature ID (whole "RZL-429" or a part "RZL" / "RZL-4"), the wormhole type ("Z971") and the words that describe the
// hole ("class 1-3", "medium size", "less than 1 day", "50% mass"), before it looks for systems and pilots, so those words are never read as
// a system ("1-3" for 1-3HWZ) or looked up as a pilot ("class", "then"). The IDs are kept with the system's wormhole report (040's list).
// build_sig.py patches 7 places in index.html to call these; window.__SIGOFF (the MOCKUP bar's "Today") turns the reading off.

// where a wormhole type leads (EVE University wiki "Wormhole attributes", read 2026-11-12; the build reads it from CCP's SDE)
const IT_WH_TYPE = (() => {
  const o = {K162: 'exit'};
  const T = {c1: 'H121 P060 Q317 V301 Y790 Z647 Z971 E004', c2: 'C125 D364 D382 G024 I182 N766 R943 L005', c3: 'C247 L477 M267 N968 O477 O883 X702 Z006',
    c4: 'E175 M001 M609 O128 T405 X877 Y683 Z457', c5: 'H296 H900 L614 M555 N062 N432 N770 V911 C008', c6: 'A982 B041 R474 S804 U319 U574 V753 W237 G008',
    c13: 'A009', hs: 'A641 B274 B449 B520 D792 D845 N110 Q063 S047', ls: 'A239 C140 C391 J244 N290 N944 R051 U210 V898 J377',
    ns: 'C248 E545 E587 K329 K346 Q003 S199 V283 Z060 Z142', th: 'F135 F353 L031 M164 T458', po: 'C729 F216 U372', dr: 'B735 C414 R259 S877 V928'};
  for(const [d, codes] of Object.entries(T)) for(const c of codes.split(' ')) o[c] = d;
  return o;
})();
const IT_WH_DEST = {c1: ['C1', 'Class 1'], c2: ['C2', 'Class 2'], c3: ['C3', 'Class 3'], c4: ['C4', 'Class 4'], c5: ['C5', 'Class 5'], c6: ['C6', 'Class 6'],
  c13: ['C13', 'a shattered Class 13'], hs: ['HS', 'highsec'], ls: ['LS', 'lowsec'], ns: ['NS', 'nullsec'], th: ['Thera', 'Thera'], po: ['Pochven', 'Pochven'],
  dr: ['Drifter', 'a Drifter system'], exit: ['exit', 'the other side (K162 is the far end of a hole opened from there)']};
// words that describe a hole, in a wormhole line only: never a pilot or a system there
const IT_WH_WORDS = new Set(['class', 'cls', 'size', 'sized', 'mass', 'massed', 'life', 'lifetime', 'day', 'days', 'hour', 'hours', 'hr', 'hrs', 'h', 'min', 'mins',
  'less', 'than', 'then', 'more', 'under', 'over', 'about', 'medium', 'med', 'small', 'large', 'big', 'xl', 'huge', 'frig', 'frigate', 'frigates', 'cruiser', 'cruisers', 'bs', 'battleship',
  'capital', 'caps', 'eol', 'crit', 'critical', 'reduced', 'stable', 'fresh', 'half', 'static', 'statics', 'sig', 'sigs', 'signature', 'exit', 'entrance', 'leads',
  'new', 'old', 'shrink', 'shrinking', 'left', 'only', 'hole', 'holes', 'end', 'very', 'natural']);
const IT_SIG_WORDS = new Set(['sig', 'sigs', 'signature']);
// what a line says about the hole's life, mass and size, only when it's said plainly (the game's own steps; EVE University wiki "Wormholes":
// life "less than 1 day / 4 hours / 1 hour remaining", mass "more than 50% / less than 50% / less than 10% remaining", size small / medium /
// large / extra large): "less than 1 day", "<1d" → under a day; "eol", "end of life", "less than 4h" → under 4 h; "less than 1h" → under an hour;
// "crit", "critical", "<10%" → under 10%; "reduced", "less than 50% mass", "half mass" → under 50%; "stable", ">50%" → over 50%; a size word only
// with size / sized / hole / only after it ("medium size", "frig hole", "small hole"), and "xl" or "very large". "fresh", "new", "frig" or "caps"
// alone are left out: they can mean a ship in the line rather than the hole.
const IT_WH_RANK = {life: ['lt1d', 'eol', 'lt1h'], mass: ['stable', 'reduced', 'critical']};
function itWhInfoOf(W){
  const t = ' ' + W.map(x => x.lw).join(' ').replace(/</g, ' less than ').replace(/>/g, ' more than ').replace(/(\d)(%|d|h|hr|hrs)\b/g, '$1 $2').replace(/\s+/g, ' ') + ' ';
  const LT = '(?:less|under) (?:than |then )?', MT = '(?:more|over) (?:than |then )?', o = {};
  const put = (k, v) => { const r = IT_WH_RANK[k]; if(!o[k] || (r && r.indexOf(v) > r.indexOf(o[k]))) o[k] = v; };   // both said: the worse
  if(/ (eol|end of (its )?(natural )?life) /.test(t) || new RegExp(` ${LT}(4|four) ?(h|hr|hrs|hour|hours) `).test(t)) put('life', 'eol');
  if(new RegExp(` ${LT}(1|a|one) ?(d|day) `).test(t) || new RegExp(` ${LT}24 ?(h|hr|hrs|hours) `).test(t)) put('life', 'lt1d');
  if(new RegExp(` ${LT}(1|an|one) ?(h|hr|hour) `).test(t)) put('life', 'lt1h');
  if(/ (crit|critical|crit mass) /.test(t) || new RegExp(` ${LT}10 ?% `).test(t)) put('mass', 'critical');
  if(/ (reduced|half mass) /.test(t) || new RegExp(` ${LT}50 ?% `).test(t)) put('mass', 'reduced');
  if(/ stable /.test(t) || new RegExp(` ${MT}50 ?% `).test(t)) put('mass', 'stable');
  const sz = / (frig|frigs|frigate|small|medium|med|large|xl|very large|capital|cap) (size|sized|hole|only) /.exec(t) || / (xl|very large) /.exec(t);
  if(sz) o.size = {frig: 'small', frigs: 'small', frigate: 'small', small: 'small', medium: 'medium', med: 'medium', large: 'large', xl: 'xl', 'very large': 'xl', capital: 'xl', cap: 'xl'}[sz[1]];
  return o;
}
const IT_WH_INFO_TXT = {life: {lt1d: ['<1 day', 'Less than 1 day of life remaining'], eol: ['EOL <4h', 'End of life: less than 4 hours remaining'], lt1h: ['<1h', 'Less than 1 hour of life remaining']},
  mass: {stable: ['mass >50%', 'More than 50% of its mass remaining'], reduced: ['mass <50%', 'Less than 50% of its mass remaining'], critical: ['crit <10%', 'Mass critical: less than 10% remaining']},
  size: {small: ['small', 'Small: frigates, destroyers and some HICs only'], medium: ['medium', 'Medium: battlecruisers and smaller'], large: ['large', 'Large: battleships and smaller'], xl: ['XL', 'Extra large: all but titans and supercarriers']}};
function itWhClsTxt(c){ return /^C/.test(c) ? [c, `Class ${c.slice(1)} wormhole space`] : [`→${c}`, `Leads to ${{HS: 'highsec', LS: 'lowsec', NS: 'nullsec'}[c] || c}`]; }
function itWhInfoHtml(i, t, onId){
  if(!i) return '';
  const age = t ? `, reported ${itAgo(t)} ago` : '';
  const cl = i.cls && !onId ? `<span class="it-gtag it-sig" title="${escapeHtml(itWhClsTxt(i.cls)[1] + ' (as reported)' + age)}">${escapeHtml(itWhClsTxt(i.cls)[0])}</span>` : '';
  return cl + ['life', 'mass', 'size'].filter(k => i[k] && IT_WH_INFO_TXT[k][i[k]]).map(k => { const [a, b] = IT_WH_INFO_TXT[k][i[k]], bad = i[k] === 'eol' || i[k] === 'lt1h' || i[k] === 'critical', warn = i[k] === 'lt1d' || i[k] === 'reduced';
    return `<span class="it-gtag it-whi${bad ? ' bad' : warn ? ' warn' : ''}" title="${escapeHtml(b + age)}">${escapeHtml(a)}</span>`; }).join('');
}
// a newer line's word wins; what it doesn't say stays
function itWhInfoMerge(a, b){ const o = {...(a || {})}; for(const k of ['life', 'mass', 'size', 'cls']) if(b && b[k]) o[k] = b[k]; return Object.keys(o).length ? o : undefined; }
function itWhRepInfo(old, e){ const d = e.p.whd; return itWhInfoMerge(old && old.info, d && d.info); }
// the wormhole details in a line (null if it names no wormhole); marks the words it takes as used (itParse calls it before the systems)
function itWhDetails(W, used){
  if(window.__SIGOFF) return null;   // MOCKUP only: "Today"
  const isWh = (x) => x && (IT_KW[x.lw] === 'wormhole' || IT_KW[x.lw] === 'drifter');
  if(!W.some(isWh)) return null;
  const N = it.names, sysName = (lw) => !!(N && N.byLower.has(lw));
  const sigs = [], types = [], info = itWhInfoOf(W);
  let cls = '';
  const typeOf = (w) => { const u = w.toUpperCase(); return IT_WH_TYPE[u] ? u : null; };
  const sigOf = (w) => {   // "RZL-429", "rzl429" (whole), "RZL-4", "RZL-" (a part)
    let m = /^([a-z]{3})-?(\d{3})$/i.exec(w); if(m) return {sig: `${m[1].toUpperCase()}-${m[2]}`, part: false};
    m = /^([a-z]{3})-(\d{0,2})$/i.exec(w); if(m) return {sig: `${m[1].toUpperCase()}-${m[2]}`.replace(/-$/, ''), part: true};
    return null;
  };
  for(let i = 0; i < W.length; i++){
    if(used[i]) continue;
    const x = W[i], lw = x.lw;
    if(sysName(lw)) continue;   // a real system's name stays a system
    const t = typeOf(x.w); if(t){ types.push({type: t, at: i}); used[i] = 'wt'; continue; }
    const s = sigOf(x.w);
    if(s && s.part && N && N.list.some(n => n.startsWith(lw) && n.includes('-'))) continue;   // "ZXB-" could be the start of a system's name: the system reader decides
    if(s){ sigs.push({...s, at: i}); used[i] = 'sig'; continue; }
    let m = /^c(13|[1-6])$/i.exec(x.w); if(m){ cls = cls || `C${m[1]}`; used[i] = 'wd'; continue; }
    if(lw === 'class' || lw === 'cls'){   // "class 1-3", "class 5", "class c5"
      used[i] = 'wd';
      const n = W[i + 1]; m = n && !used[i + 1] && /^c?(\d{1,2}(?:-\d{1,2})?)$/i.exec(n.w);
      if(m){ cls = cls || `C${m[1]}`; used[i + 1] = 'wd'; i++; }
      continue;
    }
    if(/^[<>~]?\d{1,3}%$/.test(x.w) || /^[<>~]?\d{1,3}(h|hr|hrs|d|m)$/i.test(x.w)){ used[i] = 'wd'; continue; }
    if(IT_WH_WORDS.has(lw)){ used[i] = 'wd'; continue; }
  }
  // a part given as just its 3 letters ("wh rzl", "sig RZL", "rzl z971"): only right after a wormhole or signature word, or right before or
  // after a wormhole type, and never an intel, filler or ship word
  for(let i = 0; i < W.length; i++){
    if(used[i] && used[i] !== null) continue;
    const x = W[i];
    if(!/^[a-z]{3}$/i.test(x.w) || IT_KW[x.lw] || IT_FILLER.has(x.lw) || IT_NOT_PILOT.has(x.lw) || itShips().has(x.lw) || sysName(x.lw) || x.linked) continue;
    const p = W[i - 1], n = W[i + 1];
    const by = (p && (isWh(p) || IT_SIG_WORDS.has(p.lw) || used[i - 1] === 'wt')) || (n && used[i + 1] === 'wt');
    if(by){ sigs.push({sig: x.w.toUpperCase(), part: true, at: i}); used[i] = 'sig'; }
  }
  sigs.sort((a, b) => a.at - b.at);
  // a type goes with the signature it's written beside (else, with one signature in the line, that one)
  for(const s of sigs){ const t = types.find(t => Math.abs(t.at - s.at) === 1) || (sigs.length === 1 && types.length === 1 ? types[0] : null); if(t){ s.type = t.type; t.taken = true; } }
  const drLine = W.some(x => IT_KW[x.lw] === 'drifter');   // "drifter" in the line: each ID in it is a Drifter hole; so is a Drifter type (B735, C414…)
  for(const s of sigs) s.dr = drLine || IT_WH_TYPE[s.type || ''] === 'dr';
  if(cls) info.cls = cls;   // the class the line gives ("class 1-3", "c5") is kept like life, mass and size (the owner: "yes")
  // life, mass, size and class go with the line's only signature; with none or several, with the system's report
  const one = sigs.length === 1 && Object.keys(info).length;
  return {sigs: sigs.map(s => ({sig: s.sig, part: s.part, type: s.type || '', ...(s.dr ? {dr: true} : {}), ...(one ? {info} : {})})), types: types.filter(t => !t.taken).map(t => t.type), cls,
    info: !one && Object.keys(info).length ? info : undefined};
}
// Drifter, per hole (the owner: "some systems have more than one drifter hole as well"): the system shows Drifter while any kept hole is one, or
// while a Drifter report with no ID is kept; a later plain "wh" report no longer clears it. 040's saved entries (drifter with no Drifter ID) read as
// a Drifter report with no ID.
function itWhDrNoId(old, e, w){
  const st = itWhStore(), cut = Date.now() - st.keepH * 3600e3, d = e.p.whd;
  const was = !!old && old.t >= cut && (old.drNoId || (old.drifter && !(Array.isArray(old.sigs) && old.sigs.some(s => s.dr))));
  return was || (w === 'drifter' && !(d && d.sigs.length)) || undefined;
}
function itWhDrSet(w){ if(!w) return w; const n = (w.sigs || []).filter(s => s.dr).length; w.drifter = !!w.drNoId || n > 0; w.drN = n; return w; }
// the system's kept signatures after a new line: a part and the whole ID (or a longer part) are the same signature; newest first, at most 8,
// none older than the setting
function itWhSigMerge(old, e){
  const st = itWhStore(), cut = Date.now() - st.keepH * 3600e3, d = e.p.whd;
  let list = (old && Array.isArray(old.sigs) ? old.sigs : []).filter(s => s.t >= cut).map(s => ({...s}));
  for(const n of (d ? d.sigs : []).slice().reverse()){
    const hits = list.filter(s => s.sig.startsWith(n.sig) || n.sig.startsWith(s.sig)), same = hits.length === 1 ? hits[0] : null;   // two kept IDs can share their letters (ABC-123, ABC-456): a part that fits both is kept on its own
    if(same){ if(n.sig.length > same.sig.length){ same.sig = n.sig; same.part = n.part; } if(n.type) same.type = n.type; if(n.info) same.info = itWhInfoMerge(same.info, n.info); if(n.dr) same.dr = true; same.t = e.t; same.who = String(e.who || '').slice(0, 64); list = [same, ...list.filter(s => s !== same)]; }
    else list.unshift({sig: n.sig, part: n.part, type: n.type || '', ...(n.dr ? {dr: true} : {}), ...(n.info ? {info: n.info} : {}), t: e.t, who: String(e.who || '').slice(0, 64)});
  }
  return list.slice(0, 8);
}
function itWhDestTxt(type){ const d = IT_WH_DEST[IT_WH_TYPE[type]]; return d ? d : ['?', 'somewhere the page doesn’t know']; }
function itWhSigHtml(s, opt){
  const shown = s.part ? `${s.sig}${s.sig.includes('-') ? '' : '-'}…` : s.sig;
  const title = `${s.part ? `Part of a signature ID: ${s.sig}, as reported (enough to tell it apart in that system’s scan)` : `Signature ${s.sig}`}${s.type ? `, a ${s.type} (leads to ${itWhDestTxt(s.type)[1]})` : ''}${s.who ? `; reported by ${s.who}${s.t ? `, ${itAgo(s.t)} ago` : ''}` : ''}`;
  const sc = s.scan ? (s.scan.in ? `. In your probe scan ${itAgo(s.scan.t)} ago${s.scan.group ? ` (${s.scan.group}, ${s.scan.pct}%)` : ''}` : `. Not in your probe scan ${itAgo(s.scan.t)} ago: it may have closed`) : '';
  const from = s.src === 'scan' ? '. Found in your probe scan' : '';
  const rm = opt && opt.rm ? `<button type="button" class="it-sigx" data-it-whsrm="${Number(opt.rm)}|${escapeHtml(s.sig)}" aria-label="${escapeHtml(`Remove ${s.sig} only`)}" title="Remove this one (closed or collapsed)">×</button>` : '';
  return `<span class="it-gtag it-sig${s.part ? ' part' : ''}${s.dr ? ' dr' : ''}${s.scan && !s.scan.in ? ' gone' : ''}" title="${escapeHtml((s.dr ? 'Drifter wormhole. ' : '') + title + from + sc)}">${s.dr ? '<i class="drm">DR</i>' : ''}${escapeHtml(shown)}${s.scan && s.scan.in ? '<span class="ok" aria-hidden="true">✓</span>' : ''}${s.type ? ` <b>${escapeHtml(s.type)}→${escapeHtml(itWhDestTxt(s.type)[0])}</b>` : s.info && s.info.cls ? ` <b>${escapeHtml(itWhClsTxt(s.info.cls)[0])}</b>` : ''}${rm}</span>`;
}
function itWhSigsHtml(list, max = 3, opt){
  const l = Array.isArray(list) ? list : [];
  return l.slice(0, max).map(s => itWhSigHtml(s, opt) + itWhInfoHtml(s.info, s.t, true)).join('') + (l.length > max ? `<span class="it-gtag it-sig more" title="${escapeHtml(l.slice(max).map(s => s.sig).join(', '))}">+${l.length - max}</span>` : '');
}
// the Feed line's own: its signatures, and a type written alone
function itWhLineHtml(d){
  if(!d) return '';
  return itWhSigsHtml(d.sigs.map(s => ({...s})), 4) + d.types.map(t => `<span class="it-gtag it-sig" title="${escapeHtml(`A ${t} (leads to ${itWhDestTxt(t)[1]}); no signature ID with it`)}"><b>${escapeHtml(t)}→${escapeHtml(itWhDestTxt(t)[0])}</b></span>`).join('')
    + itWhInfoHtml(d.info);
}
(() => {
  const st = document.createElement('style');
  st.textContent = `.it-sig{font-family:var(--mono, monospace); letter-spacing:.3px; color:var(--it-wh, #a98bd8); background:color-mix(in srgb, var(--it-wh, #a98bd8) 12%, transparent); border-color:color-mix(in srgb, var(--it-wh, #a98bd8) 40%, transparent);}
    .it-sig.part{border-style:dashed;} .it-sig b{font-weight:600; color:var(--text, #c9d1d9); margin-left:2px;} .it-sig.more{font-family:var(--sans);} .it-whp-by .it-sig{margin-right:6px;}
    .it-whi{font-family:var(--sans); color:var(--text-dim, #8b98a5); border-color:var(--line, #30363d);} .it-whi.warn{color:var(--amber, #d99a3c); border-color:color-mix(in srgb, var(--amber, #d99a3c) 45%, transparent);}
    .it-whi.bad{color:var(--danger, #e5534b); border-color:color-mix(in srgb, var(--danger, #e5534b) 50%, transparent);} .it-whp-by .it-whi{margin-right:6px;}`;
  document.head.appendChild(st);
})();

// ---- the probe scan, pasted into the list (the owner: "that would be cool"): the probe scanner's rows (Ctrl+A, Ctrl+C), one per line, cells split
// by tabs: ID, Cosmic Signature / Cosmic Anomaly, group (Wormhole, Data Site… or empty until scanned), name, signal %, distance. Taken as a scan
// of the system you're in. It turns a part into the whole ID when exactly one ID in the scan starts with it; marks each kept ID of that system
// as in or not in the scan (not in: it may have closed; nothing is removed); and keeps the scan's wormholes (group Wormhole) not reported yet.
function itWhScanRows(text){
  const out = [];
  for(const line of String(text || '').split(/\r?\n/)){
    const c = line.split('\t').map(x => x.trim()), m = /^([A-Z]{3}-\d{3})$/.exec(c[0] || '');
    if(!m) continue;
    out.push({id: m[1], anom: /anomal/i.test(c[1] || ''), group: c[2] || '', name: c[3] || '', pct: parseFloat(String(c[4] || '').replace(',', '.')) || 0});
  }
  return out;
}
function itWhScanApply(text){
  const rows = itWhScanRows(text), sys = itMySys();
  if(!rows.length) return 'Nothing in that looks like the probe scanner’s list. In the game: the Probe Scanner window, Ctrl+A, Ctrl+C, then paste here.';
  if(!sys) return 'Your system isn’t known yet (turn on Intel, or Use my game location), so the scan can’t be placed.';
  const st = itWhStore(), now = Date.now(), ids = rows.map(r => r.id), name = itSysName(sys), done = [], two = [], gone = [];
  let w = st.rep[sys];
  const holes = rows.filter(r => !r.anom && /wormhole/i.test(r.group));
  if(!w && !holes.length) return `${name}: none of the scan's ${rows.length} rows is a wormhole, and no wormhole is kept there.`;
  if(!w){ w = st.rep[sys] = {id: sys, t: now, who: '', drifter: false, src: 'you', sigs: []}; delete st.gone[sys]; }
  w.sigs = Array.isArray(w.sigs) ? w.sigs : [];
  for(const s of w.sigs){
    if(s.part){ const c = ids.filter(id => id.startsWith(s.sig)); if(c.length === 1){ done.push(`${s.sig} → ${c[0]}`); s.sig = c[0]; s.part = false; } else if(c.length > 1) two.push(`${s.sig} (${c.join(' or ')})`); }
    const r = rows.find(x => x.id === s.sig), fits = s.part && ids.some(id => id.startsWith(s.sig));   // a part still fitting several: in the scan, not yet told apart
    s.scan = {t: now, in: !!r || fits, ...(r ? {group: r.group, pct: r.pct} : {})};
    if(!r && !s.part) gone.push(s.sig);
  }
  let added = 0;
  for(const r of holes) if(!w.sigs.some(s => s.sig === r.id)){ w.sigs.push({sig: r.id, part: false, type: '', t: now, who: '', src: 'scan', scan: {t: now, in: true, group: r.group, pct: r.pct}}); added++; }
  w.sigs = w.sigs.slice(0, 12);
  itWhRawAdd(w, {t: now, raw: `${rows.length} rows: ${rows.map(r => r.id + (r.group ? ' ' + r.group : '')).join(', ')}`.slice(0, 400), k: 'scan'});
  itWhDrSet(w); itWhSave(); itWhChanged();
  return [`${name}: ${rows.length} rows read, ${holes.length} wormhole${holes.length === 1 ? '' : 's'}.`, done.length ? `Completed ${done.join(', ')}.` : '', added ? `${added} new from your scan.` : '',
    two.length ? `Still a part (fits more than one): ${two.join('; ')}.` : '', gone.length ? `Not in your scan: ${gone.join(', ')} (it may have closed).` : ''].filter(Boolean).join(' ');
}
function itWhScanBoxHtml(){
  return '<details class="it-whp-scan"><summary>Paste your probe scan</summary><textarea rows="4" spellcheck="false" aria-label="Probe scanner rows" placeholder="In the game: Probe Scanner, Ctrl+A, Ctrl+C, then paste here"></textarea>'
    + '<button type="button" data-it-whscan>Use for the system I’m in</button></details>';
}
function itWhSigRemove(sys, sig){
  const st = itWhStore(), w = st.rep[sys]; if(!w || !Array.isArray(w.sigs)) return;
  w.sigs = w.sigs.filter(s => s.sig !== sig); itWhDrSet(w); itWhSave(); itWhChanged();
}
// the list's clicks this adds: one ID's ×, and the probe scan
function itWhScanClick(e, p){
  const rt = e.target.closest('[data-it-whraw]');
  if(rt){ const id = Number(rt.dataset.itWhraw); itWhRawOpen.has(id) ? itWhRawOpen.delete(id) : itWhRawOpen.add(id); itWhListPaint(true); const b = p.querySelector(`[data-it-whraw="${id}"]`); if(b) b.focus(); return true; }
  const x = e.target.closest('[data-it-whsrm]');
  if(x){ const [id, sig] = x.dataset.itWhsrm.split('|'); itWhSigRemove(Number(id), sig); p.querySelector('.it-whp-msg').textContent = `Removed ${sig} from ${itSysName(Number(id))}.`; return true; }
  if(!e.target.closest('[data-it-whscan]')) return false;
  const ta = p.querySelector('.it-whp-scan textarea');
  p.querySelector('.it-whp-msg').textContent = itWhScanApply(ta.value);
  ta.value = '';
  return true;
}
(() => {
  const st = document.createElement('style');
  st.textContent = `.it-whp-scan{margin:8px 0 0;} .it-whp-scan summary{cursor:pointer; color:var(--cyan, #4fc3d9); font:13px var(--sans);} .it-whp-scan textarea{display:block; width:100%; box-sizing:border-box; margin:6px 0; font:12px var(--mono, monospace);}
    .it-sig.gone{opacity:.55; text-decoration:line-through;}
    .it-sig.dr{color:var(--it-wh-drifter, #ff5fbf); border-color:color-mix(in srgb, var(--it-wh-drifter, #ff5fbf) 55%, transparent);} .it-sig .drm{font-style:normal; font:700 10px var(--sans); margin-right:4px; padding:0 3px; border-radius:2px; background:var(--it-wh-drifter, #ff5fbf); color:#1a1020;}
    .it-sigx{all:unset; cursor:pointer; margin-left:5px; padding:0 3px; color:var(--text-dim, #8b98a5); font:700 12px var(--sans); line-height:1;} .it-sigx:hover, .it-sigx:focus-visible{color:var(--danger, #e5534b); outline:1px solid currentColor; border-radius:2px;}
    @media (max-width:599px){ .it-sigx{padding:4px 7px; margin:-4px -4px -4px 3px;} } .it-sig .ok{color:var(--it-clear, #3fb950); margin-left:3px;}`;
  document.head.appendChild(st);
})();

// the map's wormhole ring, split by kind (the owner: "we could have wormhole systems with more than one type show a ring w/ more than one color,
// couldn't we? like half purple and half another color?"): each kind the system's kept holes have gets an equal share of both rings, in its colour,
// starting at the top, clockwise: plain wormholes (purple, solid), then Drifter (hot pink, dashed: the owner's pick, "let's do pink and dashed", so
// it reads apart by its shape too). One kind: whole rings.
function itWhKinds(w){
  const sg = Array.isArray(w.sigs) ? w.sigs : [], k = [];
  const plain = sg.length ? sg.some(s => !s.dr) : !w.drifter, dr = !!w.drifter;
  if(plain) k.push({col: itMapWhCol({}), dash: false}); if(dr) k.push({col: itMapWhCol({drifter: true}), dash: true});
  return k.length ? k : [{col: itMapWhCol(w), dash: !!w.drifter}];
}
function itWhRingDraw(c, x, y, r1, r2, w){
  const parts = itWhKinds(w), n = parts.length, gap = n > 1 ? 0.22 : 0, top = -Math.PI / 2;
  parts.forEach((p, j) => {
    const a0 = top + j * 2 * Math.PI / n + gap / 2, a1 = top + (j + 1) * 2 * Math.PI / n - gap / 2;
    c.strokeStyle = p.col; c.setLineDash(p.dash ? [2.2, 1.8] : []);
    c.beginPath(); c.arc(x, y, r1, a0, a1); c.stroke(); c.beginPath(); c.arc(x, y, r2, a0, a1); c.stroke();
  });
  c.setLineDash([]);
}

// ---- adding by hand with every property (the owner: "the ability to set all of these properties we're supporting through the add button"): the list's
// Add form gains a second row: signature ID (whole or a part), type (its destination shown as you type), life, mass, size; Drifter was there already.
// All optional but the system. Kept for the setting's hours from now, "added by you"; an ID matching a kept one (part or whole) updates it.
function itWhAddMoreHtml(){
  const opt = (k) => '<option value="">' + {life: 'Life', mass: 'Mass', size: 'Size'}[k] + '</option>' + Object.entries(IT_WH_INFO_TXT[k]).map(([v, [a, b]]) => `<option value="${escapeHtml(v)}" title="${escapeHtml(b)}">${escapeHtml(a)}</option>`).join('');
  return '<div class="it-whp-more"><input type="text" name="sig" placeholder="Sig ID, e.g. RZL-429 or RZL" aria-label="Signature ID (optional)" maxlength="7" spellcheck="false" autocapitalize="characters">'
    + '<span class="it-whp-ty"><input type="text" name="ty" placeholder="Type or class: Z971, C3, 1-3, HS" aria-label="Wormhole type or class (optional)" maxlength="7" spellcheck="false" autocapitalize="characters"><output name="dest" aria-live="polite"></output></span>'
    + `<select name="life" aria-label="Life (optional)">${opt('life')}</select><select name="mass" aria-label="Mass (optional)">${opt('mass')}</select><select name="size" aria-label="Size (optional)">${opt('size')}</select></div>`;
}
// "Type or class": a type the page knows (Z971, K162), a class or a range (C3, c13, 1-3, C1-3), or where it leads (HS, LS, NS, Thera, Pochven)
function itWhTyOrCls(v){
  const u = String(v || '').trim().toUpperCase().replace(/\s+/g, '');
  if(!u) return {};
  if(IT_WH_TYPE[u]) return {type: u};
  const m = /^C?(13|[1-6])(?:-C?([1-6]))?$/.exec(u);
  if(m && (!m[2] || (m[1] !== '13' && Number(m[2]) > Number(m[1])))) return {cls: `C${m[1]}${m[2] ? '-' + m[2] : ''}`};
  const d = {HS: 'HS', HIGHSEC: 'HS', LS: 'LS', LOWSEC: 'LS', NS: 'NS', NULLSEC: 'NS', THERA: 'Thera', POCHVEN: 'Pochven'}[u];
  return d ? {cls: d} : {bad: true};
}
function itWhTypeHint(f){
  const r = itWhTyOrCls(f.ty.value);
  f.dest.value = r.type ? `→ ${itWhDestTxt(r.type)[0]}` : r.cls ? (/^C/.test(r.cls) ? `class ${r.cls}` : `leads to ${r.cls}`) : r.bad && String(f.ty.value).trim().length >= 3 ? 'not known' : '';
}
function itWhAddFull(f){
  const sigRaw = String(f.sig.value || '').trim().toUpperCase().replace(/^([A-Z]{3})(\d)/, '$1-$2'), tc = itWhTyOrCls(f.ty.value), ty = tc.type || '';
  if(sigRaw && !/^[A-Z]{3}(-\d{0,3})?$/.test(sigRaw)) return {ok: false, msg: 'A signature ID is three letters and three digits (RZL-429), or its start (RZL, RZL-4).', field: 'sig'};
  if(tc.bad) return {ok: false, msg: `“${String(f.ty.value).trim()}” isn’t a type or class the page knows: a type (Z971, K162), a class (C3, C13) or range (1-3), or HS, LS, NS, Thera, Pochven.`, field: 'ty'};
  const info = {}; for(const k of ['life', 'mass', 'size']) if(f[k].value) info[k] = f[k].value;
  if(tc.cls) info.cls = tc.cls;
  const nm = String(f.sys.value || '').trim(), id = it.names && it.names.byLower.get(nm.toLowerCase()), st = itWhStore(), old = id ? st.rep[id] : null;
  const keep = old && old.t >= Date.now() - st.keepH * 3600e3 ? {sigs: old.sigs, info: old.info, drNoId: old.drNoId} : {};
  const r = itWhAdd(f.sys.value, f.dr.checked && !sigRaw);   // 040's add: checks the name, keeps the system for the setting's hours
  if(!r.ok) return r;
  const w = st.rep[id]; Object.assign(w, keep);
  if(f.dr.checked && !sigRaw) w.drNoId = true;
  const sig = sigRaw.replace(/-$/, '');
  if(sig){
    const part = !/^[A-Z]{3}-\d{3}$/.test(sig), n = {sig, part, type: ty, ...(f.dr.checked || IT_WH_TYPE[ty] === 'dr' ? {dr: true} : {}), ...(Object.keys(info).length ? {info} : {})};
    const had = (w.sigs || []).some(s => s.sig.startsWith(n.sig) || n.sig.startsWith(s.sig));   // updating a kept one keeps where it came from
    w.sigs = itWhSigMerge({sigs: w.sigs}, {t: Date.now(), who: '', p: {whd: {sigs: [n]}}}).map(s => !had && s.sig === n.sig ? {...s, src: 'you'} : s);
  } else if(Object.keys(info).length) w.info = itWhInfoMerge(w.info, info);
  const what0 = [sig || '', String(f.ty.value || '').trim(), ...['life', 'mass', 'size'].filter(k => f[k].value).map(k => IT_WH_INFO_TXT[k][f[k].value][0]), f.dr.checked ? 'Drifter' : ''].filter(Boolean).join(' ');
  itWhRawAdd(w, {t: Date.now(), raw: `${itSysName(id)}${what0 ? ' ' + what0 : ''}`, k: 'you'});
  itWhDrSet(w); itWhSave(); itWhChanged();
  const what = [sig, ty && `${ty} → ${itWhDestTxt(ty)[0]}`, tc.cls && itWhClsTxt(tc.cls)[0], ...['life', 'mass', 'size'].filter(k => info[k]).map(k => IT_WH_INFO_TXT[k][info[k]][0]), f.dr.checked && 'Drifter'].filter(Boolean).join(', ');
  for(const k of ['sig', 'ty', 'life', 'mass', 'size']) f[k].value = ''; f.dest.value = '';
  return {ok: true, msg: what ? `${r.msg.replace(/\.$/, '')}: ${what}.` : r.msg};
}
(() => {
  const st = document.createElement('style');
  st.textContent = `.it-whp-more{display:flex; flex-wrap:wrap; gap:6px; width:100%; margin-top:6px;} .it-whp-more input[name=sig]{flex:1 1 150px; min-width:0; font-family:var(--mono, monospace);}
    .it-whp-ty{display:inline-flex; gap:4px; align-items:center; flex:1 1 190px; min-width:0;} .it-whp-ty input{width:100%; min-width:0; font-family:var(--mono, monospace);} .it-whp-ty output{font:600 12px var(--sans); color:var(--text-dim, #8b98a5); white-space:nowrap;}
    .it-whp-more select{flex:1 1 90px; min-width:0;}
    @media (max-width:599px){ .it-whp-more input, .it-whp-more select{min-height:44px;} }`;
  document.head.appendChild(st);
})();

// ---- each system's raw reports (the owner: "let's have the rows for each system also preserve the raw report that lead to the wormhole being added
// ... we can see the raw report in case something is parsed incorrectly. have it expand/collapse like intel's near you rows."): every Intel line
// that added or updated the system is kept with it as typed (who, when, the line), newest first, up to 10, for as long as the system is kept;
// adding by hand and pasting a scan leave a line too, so the history is whole. The row's chevron (Intel's IT_CHEV / it-rawt) shows them.
const IT_WH_RAW_MAX = 10, itWhRawOpen = new Set();
function itWhRawAdd(w, x){
  const st = itWhStore(), cut = Date.now() - st.keepH * 3600e3, l = (Array.isArray(w.raws) ? w.raws : []).filter(r => r.t >= cut);
  if(!l.some(r => r.t === x.t && r.raw === x.raw)) l.unshift({t: x.t, who: String(x.who || '').slice(0, 64), raw: String(x.raw || '').slice(0, 400), k: x.k || 'intel'});
  w.raws = l.sort((a, b) => b.t - a.t).slice(0, IT_WH_RAW_MAX);
  return w.raws;
}
// itWhTake's: the old entry's lines (if still kept) and this one
function itWhRawKeep(old, e){ return itWhRawAdd({raws: old && old.raws}, {t: e.t, who: e.who, raw: e.raw}); }
function itWhRawTog(w){
  const open = itWhRawOpen.has(w.id), n = (w.raws || []).length; if(!n) return '';
  return `<button type="button" class="it-rawt" data-it-whraw="${Number(w.id)}" aria-expanded="${open}" aria-label="${open ? 'Hide' : 'Show'} the ${n === 1 ? 'report' : `${n} reports`} as typed" title="${open ? 'Hide' : 'Show'} the ${n === 1 ? 'line' : `${n} lines`} as typed, and who sent ${n === 1 ? 'it' : 'them'}">${IT_CHEV}</button>`;
}
function itWhRawHtml(w){
  const l = w.raws || []; if(!l.length) return '';
  return `<div class="it-whp-raws"${itWhRawOpen.has(w.id) ? '' : ' hidden'}>` + l.map(r => `<div class="it-raw it-whp-raw${r.k !== 'intel' ? ' you' : ''}"><span class="who">${escapeHtml(r.k === 'intel' ? r.who : r.k === 'scan' ? 'Your probe scan' : 'Added by you')}</span><span class="gt">&gt;</span><span class="raw">${escapeHtml(r.raw)}</span><span class="it-age" title="your time ${escapeHtml(itClock(r.t))}">${escapeHtml(itAgo(r.t))}</span></div>`).join('') + '</div>';
}
(() => {
  const st = document.createElement('style');
  st.textContent = `.it-whp-r .it-whp-by{position:relative;} .it-whp-r .it-whp-by > button.it-rawt{position:absolute; left:2px; top:0; margin:0; order:0; min-height:0; width:24px; height:20px; padding:0;}
    .it-whp-r button.it-rawt[aria-expanded="true"] svg{transform:rotate(180deg);}
    .it-whp-raws{flex:1 1 100%; order:5; display:flex; flex-direction:column; gap:3px; margin-top:2px;} .it-whp-raws[hidden]{display:none;} .it-whp-raws .it-raw{margin:0; flex-wrap:wrap; row-gap:2px;}
    .it-whp-raws .it-raw .raw{flex:1 1 200px; min-width:0; overflow-wrap:anywhere;} .it-whp-raws .it-raw.you .who{font-style:italic;} .it-whp-raws .it-age{margin-left:auto;}
    .it-whp-r .it-sigx{margin:0 0 0 5px; order:0; min-height:0; padding:0 3px;}
    @media (max-width:599px){ .it-whp-r .it-whp-by > button.it-rawt{position:static; width:36px; height:32px; vertical-align:middle; margin-right:4px;} .it-whp-r .it-sigx{padding:4px 7px; margin:-4px -4px -4px 3px;} }`;
  document.head.appendChild(st);
})();
