// Mockup stand-in for build queue 044 (signature IDs in wormhole reports), so the Export / Import mockup has 044's list to work on.
// Copied from claude/roadmap/wormhole-sig-ids-mockup/proto_sig.js (2026-11-12) with the probe scan paste (D11) left out (removed from 044
// the same day), and 044's ADDED note: D13's × records a per-ID removal mark (goneSig). Not the design of this mockup: 044 is built from its plan.

// where a wormhole type leads (EVE University wiki "Wormhole attributes", read 2026-11-12; the build reads it from CCP's data)
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
const IT_WH_WORDS = new Set(['class', 'cls', 'size', 'sized', 'mass', 'massed', 'life', 'lifetime', 'day', 'days', 'hour', 'hours', 'hr', 'hrs', 'h', 'min', 'mins',
  'less', 'than', 'then', 'more', 'under', 'over', 'about', 'medium', 'med', 'small', 'large', 'big', 'xl', 'huge', 'frig', 'frigate', 'frigates', 'cruiser', 'cruisers', 'bs', 'battleship',
  'capital', 'caps', 'eol', 'crit', 'critical', 'reduced', 'stable', 'fresh', 'half', 'static', 'statics', 'sig', 'sigs', 'signature', 'exit', 'entrance', 'leads',
  'new', 'old', 'shrink', 'shrinking', 'left', 'only', 'hole', 'holes', 'end', 'very', 'natural']);
const IT_SIG_WORDS = new Set(['sig', 'sigs', 'signature']);
const IT_WH_RANK = {life: ['lt1d', 'eol', 'lt1h'], mass: ['stable', 'reduced', 'critical']};
function itWhInfoOf(W){
  const t = ' ' + W.map(x => x.lw).join(' ').replace(/</g, ' less than ').replace(/>/g, ' more than ').replace(/(\d)(%|d|h|hr|hrs)\b/g, '$1 $2').replace(/\s+/g, ' ') + ' ';
  const LT = '(?:less|under) (?:than |then )?', MT = '(?:more|over) (?:than |then )?', o = {};
  const put = (k, v) => { const r = IT_WH_RANK[k]; if(!o[k] || (r && r.indexOf(v) > r.indexOf(o[k]))) o[k] = v; };
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
function itWhInfoMerge(a, b){ const o = {...(a || {})}; for(const k of ['life', 'mass', 'size', 'cls']) if(b && b[k]) o[k] = b[k]; return Object.keys(o).length ? o : undefined; }
function itWhRepInfo(old, e){ const d = e.p.whd; return itWhInfoMerge(old && old.info, d && d.info); }
function itWhDetails(W, used){
  const isWh = (x) => x && (IT_KW[x.lw] === 'wormhole' || IT_KW[x.lw] === 'drifter');
  if(!W.some(isWh)) return null;
  const N = it.names, sysName = (lw) => !!(N && N.byLower.has(lw));
  const sigs = [], types = [], info = itWhInfoOf(W);
  let cls = '';
  const typeOf = (w) => { const u = w.toUpperCase(); return IT_WH_TYPE[u] ? u : null; };
  const sigOf = (w) => {
    let m = /^([a-z]{3})-?(\d{3})$/i.exec(w); if(m) return {sig: `${m[1].toUpperCase()}-${m[2]}`, part: false};
    m = /^([a-z]{3})-(\d{0,2})$/i.exec(w); if(m) return {sig: `${m[1].toUpperCase()}-${m[2]}`.replace(/-$/, ''), part: true};
    return null;
  };
  for(let i = 0; i < W.length; i++){
    if(used[i]) continue;
    const x = W[i], lw = x.lw;
    if(sysName(lw)) continue;
    const t = typeOf(x.w); if(t){ types.push({type: t, at: i}); used[i] = 'wt'; continue; }
    const s = sigOf(x.w);
    if(s && s.part && N && N.list.some(n => n.startsWith(lw) && n.includes('-'))) continue;
    if(s){ sigs.push({...s, at: i}); used[i] = 'sig'; continue; }
    let m = /^c(13|[1-6])$/i.exec(x.w); if(m){ cls = cls || `C${m[1]}`; used[i] = 'wd'; continue; }
    if(lw === 'class' || lw === 'cls'){
      used[i] = 'wd';
      const n = W[i + 1]; m = n && !used[i + 1] && /^c?(\d{1,2}(?:-\d{1,2})?)$/i.exec(n.w);
      if(m){ cls = cls || `C${m[1]}`; used[i + 1] = 'wd'; i++; }
      continue;
    }
    if(/^[<>~]?\d{1,3}%$/.test(x.w) || /^[<>~]?\d{1,3}(h|hr|hrs|d|m)$/i.test(x.w)){ used[i] = 'wd'; continue; }
    if(IT_WH_WORDS.has(lw)){ used[i] = 'wd'; continue; }
  }
  for(let i = 0; i < W.length; i++){
    if(used[i] && used[i] !== null) continue;
    const x = W[i];
    if(!/^[a-z]{3}$/i.test(x.w) || IT_KW[x.lw] || IT_FILLER.has(x.lw) || IT_NOT_PILOT.has(x.lw) || itShips().has(x.lw) || sysName(x.lw) || x.linked) continue;
    const p = W[i - 1], n = W[i + 1];
    const by = (p && (isWh(p) || IT_SIG_WORDS.has(p.lw) || used[i - 1] === 'wt')) || (n && used[i + 1] === 'wt');
    if(by){ sigs.push({sig: x.w.toUpperCase(), part: true, at: i}); used[i] = 'sig'; }
  }
  sigs.sort((a, b) => a.at - b.at);
  for(const s of sigs){ const t = types.find(t => Math.abs(t.at - s.at) === 1) || (sigs.length === 1 && types.length === 1 ? types[0] : null); if(t){ s.type = t.type; t.taken = true; } }
  const drLine = W.some(x => IT_KW[x.lw] === 'drifter');
  for(const s of sigs) s.dr = drLine || IT_WH_TYPE[s.type || ''] === 'dr';
  if(cls) info.cls = cls;
  const one = sigs.length === 1 && Object.keys(info).length;
  return {sigs: sigs.map(s => ({sig: s.sig, part: s.part, type: s.type || '', ...(s.dr ? {dr: true} : {}), ...(one ? {info} : {})})), types: types.filter(t => !t.taken).map(t => t.type), cls,
    info: !one && Object.keys(info).length ? info : undefined, drNoId: drLine && !sigs.length};
}
function itWhDrNoId(old, e, w){
  const st = itWhStore(), cut = Date.now() - st.keepH * 3600e3, d = e.p.whd;
  const was = !!old && old.t >= cut && (old.drNoId || (old.drifter && !(Array.isArray(old.sigs) && old.sigs.some(s => s.dr))));
  return was || (w === 'drifter' && !(d && d.sigs.length)) || undefined;
}
function itWhDrSet(w){ if(!w) return w; const n = (w.sigs || []).filter(s => s.dr).length; w.drifter = !!w.drNoId || n > 0; w.drN = n; return w; }
// 044's merge, plus its ADDED note: an ID removed with × stays removed unless the line is newer than the removal (goneSig)
function itWhGoneSig(old, sig, t){ const g = old && old.goneSig; if(!g) return false; return Object.entries(g).some(([k, gt]) => (k.startsWith(sig) || sig.startsWith(k)) && gt >= t); }
function itWhSigMerge(old, e){
  const st = itWhStore(), cut = Date.now() - st.keepH * 3600e3, d = e.p.whd;
  let list = (old && Array.isArray(old.sigs) ? old.sigs : []).filter(s => s.t >= cut).map(s => ({...s}));
  for(const n of (d ? d.sigs : []).slice().reverse()){
    if(itWhGoneSig(old, n.sig, e.t)) continue;
    const hits = list.filter(s => s.sig.startsWith(n.sig) || n.sig.startsWith(s.sig)), same = hits.length === 1 ? hits[0] : null;
    if(same){ if(n.sig.length > same.sig.length){ same.sig = n.sig; same.part = n.part; } if(n.type) same.type = n.type; if(n.info) same.info = itWhInfoMerge(same.info, n.info); if(n.dr) same.dr = true; same.t = e.t; same.who = String(e.who || '').slice(0, 64); list = [same, ...list.filter(s => s !== same)]; }
    else list.unshift({sig: n.sig, part: n.part, type: n.type || '', ...(n.dr ? {dr: true} : {}), ...(n.info ? {info: n.info} : {}), t: e.t, who: String(e.who || '').slice(0, 64)});
  }
  return list.slice(0, 8);
}
function itWhDestTxt(type){ const d = IT_WH_DEST[IT_WH_TYPE[type]]; return d ? d : ['?', 'somewhere the page doesn’t know']; }
function itWhSigHtml(s, opt){
  const shown = s.part ? `${s.sig}${s.sig.includes('-') ? '' : '-'}…` : s.sig;
  const title = `${s.part ? `Part of a signature ID: ${s.sig}, as reported (enough to tell it apart in that system’s scan)` : `Signature ${s.sig}`}${s.type ? `, a ${s.type} (leads to ${itWhDestTxt(s.type)[1]})` : ''}${s.who ? `; reported by ${s.who}${s.t ? `, ${itAgo(s.t)} ago` : ''}` : ''}`;
  const rm = opt && opt.rm ? `<button type="button" class="it-sigx" data-it-whsrm="${Number(opt.rm)}|${escapeHtml(s.sig)}" aria-label="${escapeHtml(`Remove ${s.sig} only`)}" title="Remove this one (closed or collapsed)">×</button>` : '';
  const note = s.note ? `<span class="it-signote" title="${escapeHtml(itWhNoteTxt(s.note))}" aria-label="${escapeHtml(itWhNoteTxt(s.note))}">!</span>` : '';
  return `<span class="it-gtag it-sig${s.part ? ' part' : ''}${s.dr ? ' dr' : ''}" title="${escapeHtml((s.dr ? 'Drifter wormhole. ' : '') + title)}">${s.dr ? '<i class="drm">DR</i>' : ''}${escapeHtml(shown)}${s.type ? ` <b>${escapeHtml(s.type)}→${escapeHtml(itWhDestTxt(s.type)[0])}</b>` : s.info && s.info.cls ? ` <b>${escapeHtml(itWhClsTxt(s.info.cls)[0])}</b>` : ''}${note}${rm}</span>`;
}
function itWhNoteTxt(n){ const t = IT_WH_INFO_TXT[n.k] && IT_WH_INFO_TXT[n.k][n.v]; return `A shared report, ${itAgo(n.t)} ago and newer than yours, says ${t ? t[0] : n.v}${t ? ` (${t[1]})` : ''}. Yours is kept.`; }
function itWhSigsHtml(list, max = 3, opt){
  const l = Array.isArray(list) ? list : [];
  return l.slice(0, max).map(s => itWhSigHtml(s, opt) + itWhInfoHtml(s.info, s.t, true)).join('') + (l.length > max ? `<span class="it-gtag it-sig more" title="${escapeHtml(l.slice(max).map(s => s.sig).join(', '))}">+${l.length - max}</span>` : '');
}
function itWhLineHtml(d){
  if(!d) return '';
  return itWhSigsHtml(d.sigs.map(s => ({...s})), 4) + d.types.map(t => `<span class="it-gtag it-sig" title="${escapeHtml(`A ${t} (leads to ${itWhDestTxt(t)[1]}); no signature ID with it`)}"><b>${escapeHtml(t)}→${escapeHtml(itWhDestTxt(t)[0])}</b></span>`).join('')
    + itWhInfoHtml(d.info);
}
function itWhSigRemove(sys, sig){
  const st = itWhStore(), w = st.rep[sys]; if(!w || !Array.isArray(w.sigs)) return;
  w.sigs = w.sigs.filter(s => s.sig !== sig); w.goneSig = {...(w.goneSig || {}), [sig]: Date.now()};   // 044 ADDED: the removal mark
  itWhDrSet(w); itWhSave(); itWhChanged();
}
// the list's clicks 044 adds: a row's raw-lines chevron, one ID's ×
function itWhListClick(e, p){
  const rt = e.target.closest('[data-it-whraw]');
  if(rt){ const id = Number(rt.dataset.itWhraw); itWhRawOpen.has(id) ? itWhRawOpen.delete(id) : itWhRawOpen.add(id); itWhListPaint(true); const b = p.querySelector(`[data-it-whraw="${id}"]`); if(b) b.focus(); return true; }
  const x = e.target.closest('[data-it-whsrm]');
  if(x){ const [id, sig] = x.dataset.itWhsrm.split('|'); itWhSigRemove(Number(id), sig); p.querySelector('.it-whp-msg').textContent = `Removed ${sig} from ${itSysName(Number(id))}.`; return true; }
  return false;
}
(() => {
  const st = document.createElement('style');
  st.textContent = `.it-sig{font-family:var(--mono, monospace); letter-spacing:.3px; color:var(--it-wh, #a98bd8); background:color-mix(in srgb, var(--it-wh, #a98bd8) 12%, transparent); border-color:color-mix(in srgb, var(--it-wh, #a98bd8) 40%, transparent);}
    .it-sig.part{border-style:dashed;} .it-sig b{font-weight:600; color:var(--text, #c9d1d9); margin-left:2px;} .it-sig.more{font-family:var(--sans);} .it-whp-by .it-sig{margin-right:6px;}
    .it-whi{font-family:var(--sans); color:var(--text-dim, #8b98a5); border-color:var(--line, #30363d);} .it-whi.warn{color:var(--amber, #d99a3c); border-color:color-mix(in srgb, var(--amber, #d99a3c) 45%, transparent);}
    .it-whi.bad{color:var(--danger, #e5534b); border-color:color-mix(in srgb, var(--danger, #e5534b) 50%, transparent);} .it-whp-by .it-whi{margin-right:6px;}
    .it-sig.dr{color:var(--it-wh-drifter, #ff5fbf); border-color:color-mix(in srgb, var(--it-wh-drifter, #ff5fbf) 55%, transparent);} .it-sig .drm{font-style:normal; font:700 10px var(--sans); margin-right:4px; padding:0 3px; border-radius:2px; background:var(--it-wh-drifter, #ff5fbf); color:#1a1020;}
    .it-sigx{all:unset; cursor:pointer; margin-left:5px; padding:0 3px; color:var(--text-dim, #8b98a5); font:700 12px var(--sans); line-height:1;} .it-sigx:hover, .it-sigx:focus-visible{color:var(--danger, #e5534b); outline:1px solid currentColor; border-radius:2px;}
    .it-signote{margin-left:4px; padding:0 4px; border-radius:2px; font:700 11px var(--sans); color:#111; background:var(--amber, #d99a3c); cursor:help;}
    @media (max-width:599px){ .it-sigx{padding:4px 7px; margin:-4px -4px -4px 3px;} }`;
  document.head.appendChild(st);
})();
function itWhAddMoreHtml(){
  const opt = (k) => '<option value="">' + {life: 'Life', mass: 'Mass', size: 'Size'}[k] + '</option>' + Object.entries(IT_WH_INFO_TXT[k]).map(([v, [a, b]]) => `<option value="${escapeHtml(v)}" title="${escapeHtml(b)}">${escapeHtml(a)}</option>`).join('');
  return '<div class="it-whp-more"><input type="text" name="sig" placeholder="Sig ID, e.g. RZL-429 or RZL" aria-label="Signature ID (optional)" maxlength="7" spellcheck="false" autocapitalize="characters">'
    + '<span class="it-whp-ty"><input type="text" name="ty" placeholder="Type or class: Z971, C3, 1-3, HS" aria-label="Wormhole type or class (optional)" maxlength="7" spellcheck="false" autocapitalize="characters"><output name="dest" aria-live="polite"></output></span>'
    + `<select name="life" aria-label="Life (optional)">${opt('life')}</select><select name="mass" aria-label="Mass (optional)">${opt('mass')}</select><select name="size" aria-label="Size (optional)">${opt('size')}</select></div>`;
}
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
  if(tc.bad) return {ok: false, msg: `“${String(f.ty.value).trim()}” isn’t a type or class the page knows.`, field: 'ty'};
  const info = {}; for(const k of ['life', 'mass', 'size']) if(f[k].value) info[k] = f[k].value;
  if(tc.cls) info.cls = tc.cls;
  const nm = String(f.sys.value || '').trim(), id = it.names && it.names.byLower.get(nm.toLowerCase()), st = itWhStore(), old = id ? st.rep[id] : null;
  const keep = old && old.t >= Date.now() - st.keepH * 3600e3 ? {sigs: old.sigs, info: old.info, drNoId: old.drNoId, raws: old.raws, goneSig: old.goneSig} : {};
  const r = itWhAdd(f.sys.value, f.dr.checked && !sigRaw);
  if(!r.ok) return r;
  const w = st.rep[id]; Object.assign(w, keep);
  if(f.dr.checked && !sigRaw) w.drNoId = true;
  const sig = sigRaw.replace(/-$/, ''), now = Date.now(), set = {};
  if(sig){
    const part = !/^[A-Z]{3}-\d{3}$/.test(sig), n = {sig, part, type: ty, ...(f.dr.checked || IT_WH_TYPE[ty] === 'dr' ? {dr: true} : {}), ...(Object.keys(info).length ? {info} : {})};
    if(w.goneSig) for(const k of Object.keys(w.goneSig)) if(k.startsWith(sig) || sig.startsWith(k)) delete w.goneSig[k];   // you added it again
    w.sigs = itWhSigMerge({sigs: w.sigs}, {t: now, who: '', p: {whd: {sigs: [n]}}});
    set.sigs = [n];
  } else { if(Object.keys(info).length){ w.info = itWhInfoMerge(w.info, info); set.info = info; } if(f.dr.checked) set.drNoId = true; }
  itWhRawAdd(w, {t: now, raw: itWhSetText(id, set), k: 'you', set});
  itWhDrSet(w); itWhSave(); itWhChanged();
  for(const k of ['sig', 'ty', 'life', 'mass', 'size']) f[k].value = ''; f.dest.value = '';
  return {ok: true, msg: r.msg};
}
// a generated line's text, from what it set ("Tama GHI-123 C247 EOL <4h")
function itWhSetText(id, set){
  const bits = [itSysName(id)];
  for(const s of (set.sigs || [])){ bits.push(s.sig + (s.part ? '…' : '')); if(s.type) bits.push(s.type); if(s.dr) bits.push('Drifter'); if(s.info) for(const k of ['cls', 'life', 'mass', 'size']) if(s.info[k]) bits.push(k === 'cls' ? s.info.cls : IT_WH_INFO_TXT[k][s.info[k]][0]); }
  if(set.info) for(const k of ['cls', 'life', 'mass', 'size']) if(set.info[k]) bits.push(k === 'cls' ? set.info.cls : IT_WH_INFO_TXT[k][set.info[k]][0]);
  if(set.drNoId) bits.push('Drifter');
  return bits.join(' ');
}
(() => {
  const st = document.createElement('style');
  st.textContent = `.it-whp-more{display:flex; flex-wrap:wrap; gap:6px; width:100%; margin-top:6px;} .it-whp-more input[name=sig]{flex:1 1 150px; min-width:0; font-family:var(--mono, monospace);}
    .it-whp-ty{display:inline-flex; gap:4px; align-items:center; flex:1 1 190px; min-width:0;} .it-whp-ty input{width:100%; min-width:0; font-family:var(--mono, monospace);} .it-whp-ty output{font:600 12px var(--sans); color:var(--text-dim, #8b98a5); white-space:nowrap;}
    .it-whp-more select{flex:1 1 90px; min-width:0;}
    @media (max-width:599px){ .it-whp-more input, .it-whp-more select{min-height:44px;} }`;
  document.head.appendChild(st);
})();
// each system's raw reports (044 D17), plus this plan's: what each line set (D4), its repeat count (D6), and where it came from
const IT_WH_RAW_MAX = 10, itWhRawOpen = new Set();
function itWhRawAdd(w, x){
  const st = itWhStore(), cut = Date.now() - st.keepH * 3600e3, l = (Array.isArray(w.raws) ? w.raws : []).filter(r => r.t >= cut);
  const same = l.find(r => r.raw === x.raw && (r.k || 'intel') === (x.k || 'intel'));
  if(same){ if(x.t > same.t){ same.n = (same.n || 1) + 1; same.t = x.t; same.who = String(x.who || same.who || '').slice(0, 64); } }
  else l.unshift({t: x.t, who: String(x.who || '').slice(0, 64), raw: String(x.raw || '').slice(0, 400), k: x.k || 'intel', ...(x.set ? {set: x.set} : {})});
  w.raws = l.sort((a, b) => b.t - a.t).slice(0, IT_WH_RAW_MAX);
  return w.raws;
}
function itWhRawKeep(old, e){ return itWhRawAdd({raws: old && old.raws}, {t: e.t, who: e.who, raw: e.raw}); }
function itWhRawTog(w){
  const open = itWhRawOpen.has(w.id), n = (w.raws || []).length; if(!n) return '';
  return `<button type="button" class="it-rawt" data-it-whraw="${Number(w.id)}" aria-expanded="${open}" aria-label="${open ? 'Hide' : 'Show'} the ${n === 1 ? 'report' : `${n} reports`} as typed" title="${open ? 'Hide' : 'Show'} the ${n === 1 ? 'line' : `${n} lines`} as typed, and who sent ${n === 1 ? 'it' : 'them'}">${IT_CHEV}</button>`;
}
function itWhRawWho(r){ return r.k === 'you' ? 'Added by you' : r.k === 'hand' ? 'Added by hand (shared)' : r.who || '<a pilot>'; }
function itWhRawHtml(w){
  const l = w.raws || []; if(!l.length) return '';
  return `<div class="it-whp-raws"${itWhRawOpen.has(w.id) ? '' : ' hidden'}>` + l.map(r => `<div class="it-raw it-whp-raw${r.k !== 'intel' ? ' you' : ''}${r.via ? ' shared' : ''}"><span class="who">${escapeHtml(itWhRawWho(r))}</span><span class="gt">&gt;</span><span class="raw">${escapeHtml(r.raw)}</span>${r.via ? '<span class="it-whp-shared" title="From an import">shared</span>' : ''}<span class="it-age" title="your time ${escapeHtml(itClock(r.t))}">${escapeHtml(itAgo(r.t))}${r.n > 1 ? ` ×${Number(r.n)}` : ''}</span></div>`).join('') + '</div>';
}
(() => {
  const st = document.createElement('style');
  st.textContent = `.it-whp-r .it-whp-by{position:relative;} .it-whp-r .it-whp-by > button.it-rawt{position:absolute; left:2px; top:0; margin:0; order:0; min-height:0; width:24px; height:20px; padding:0;}
    .it-whp-r button.it-rawt[aria-expanded="true"] svg{transform:rotate(180deg);}
    .it-whp-raws{flex:1 1 100%; order:5; display:flex; flex-direction:column; gap:3px; margin-top:2px;} .it-whp-raws[hidden]{display:none;} .it-whp-raws .it-raw{margin:0; flex-wrap:wrap; row-gap:2px;}
    .it-whp-raws .it-raw .raw{flex:1 1 200px; min-width:0; overflow-wrap:anywhere;} .it-whp-raws .it-raw.you .who{font-style:italic;} .it-whp-raws .it-age{margin-left:auto;}
    .it-whp-shared{font:600 11px var(--sans); color:var(--it-wh, #a98bd8); margin-left:6px;}
    .it-whp-r .it-sigx{margin:0 0 0 5px; order:0; min-height:0; padding:0 3px;}
    @media (max-width:599px){ .it-whp-r .it-whp-by > button.it-rawt{position:static; width:36px; height:32px; vertical-align:middle; margin-right:4px;} .it-whp-r .it-sigx{padding:4px 7px; margin:-4px -4px -4px 3px;} }`;
  document.head.appendChild(st);
})();
// 044's fields read back (a stand-in: 044's build checks each one)
function itWhReadMore(w){
  const o = {};
  if(Array.isArray(w.sigs)) o.sigs = w.sigs.filter(s => s && typeof s.sig === 'string' && /^[A-Z]{3}(-\d{1,3})?$/.test(s.sig)).slice(0, 8);
  if(w.info && typeof w.info === 'object') o.info = w.info;
  if(w.drNoId === true) o.drNoId = true;
  if(Array.isArray(w.raws)) o.raws = w.raws.filter(r => r && typeof r.raw === 'string' && Number.isFinite(r.t)).slice(0, IT_WH_RAW_MAX);
  if(w.goneSig && typeof w.goneSig === 'object') o.goneSig = w.goneSig;
  if(w.via === 'import') o.via = 'import';
  itWhDrSet({...o, drifter: w.drifter}); if(o.sigs) o.drN = o.sigs.filter(s => s.dr).length;
  return o;
}
