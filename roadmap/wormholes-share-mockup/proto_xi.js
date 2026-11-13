// Mockup 2026-11-12 (research session): the Wormholes list's Export and Import (plan claude/roadmap/wormholes-export-import-plan.md).
// Builds on the 044 stand-in (proto_sig044.js). The owner's decisions: Export copies JSON only, shown in a read-only box inside the list with a
// Copy button; fixed "Export" / "Import" labels with Intel's chevron; Import its own editable box; names replaced with "<a pilot>"; your removals
// win unless the report is newer; what you entered is never overwritten, worked out from the raw lines; a repeat is one line with "×N".
const IT_WH_PH = '<a pilot>', IT_WH_SHARE_MAX = 256 * 1024;

// ---- D7: redaction, default-deny. Intel's own reader reads the line; a word it placed stays, every other word (or run) is one "<a pilot>".
function itWhRedact(raw){
  return String(raw || '').split(IT_WH_PH).map(part => {
    if(!part.trim()) return part;
    const p = itParse(part, null), W = p.W, U = p.used, out = [];
    for(let i = 0; i < W.length; i++){
      const u = U[i], w = W[i];
      const keep = u && !(u === 'f' && !(IT_FILLER.has(w.lw) || /^\d+([.,]\d+)?$/.test(w.w) || IT_NOT_PILOT.has(w.lw)));
      if(keep) out.push(w.w); else if(out[out.length - 1] !== IT_WH_PH) out.push(IT_WH_PH);
    }
    return out.join(' ');
  }).join(` ${IT_WH_PH} `).replace(new RegExp(`(${IT_WH_PH.replace(/[<>]/g, '\\$&')}\\s*)+`, 'g'), `${IT_WH_PH} `).replace(/\s+/g, ' ').trim();
}
const itWhNorm = (s) => String(s || '').toLowerCase().replace(/\s+/g, ' ').trim();
// D4: what a line set (stored with it; a line kept before that is read once with 044's reader)
function itWhLineSet(r){
  if(r.set) return r.set;
  const W = itWords(r.raw || ''), d = itWhDetails(W, new Array(W.length).fill(null)) || {sigs: []};
  return (r.set = {...(d.sigs.length ? {sigs: d.sigs} : {}), ...(d.info ? {info: d.info} : {}), ...(d.drNoId ? {drNoId: true} : {})});
}
const itWhSetKey = (set) => JSON.stringify([(set.sigs || []).map(s => [s.sig, s.type || '', !!s.dr, s.info || {}]), set.info || {}, !!set.drNoId]);
// D6: two lines are the same report when their redacted text matches (Intel lines), or their kind and what they set (lines added by hand)
function itWhLineKey(r){ return r.k === 'intel' ? 'i|' + itWhNorm(itWhRedact(r.raw)) : 'h|' + itWhSetKey(itWhLineSet(r)); }

// ---- D3: the export
function itWhExportObj(){
  const st = itWhStore(), cut = Date.now() - st.keepH * 3600e3, sys = [];
  for(const w of Object.values(st.rep).filter(w => w.t >= cut).sort((a, b) => a.id - b.id)){
    const raws = (w.raws || []).map(r => { const set = itWhLineSet(r), hand = r.k !== 'intel';
      return {t: r.t, k: hand ? 'hand' : 'intel', raw: hand ? itWhSetText(w.id, set) : itWhRedact(r.raw), set, n: r.n || 1}; });
    sys.push({id: w.id, name: itSysName(w.id), t: w.t, ...(w.drNoId ? {drNoId: true} : {}), ...(w.info ? {info: w.info} : {}),
      sigs: (w.sigs || []).map(s => ({sig: s.sig, part: !!s.part, type: s.type || '', ...(s.info ? {info: s.info} : {}), ...(s.dr ? {dr: true} : {}), t: s.t})), raws});
  }
  return {tv: 'wormholes', v: 1, made: Date.now(), sys};
}

// ---- D9: the import, checked (someone else's text)
function itWhImportRead(text){
  const s = String(text || '').trim();
  if(!s) return {err: 'Paste a wormhole export first.'};
  if(s.length > IT_WH_SHARE_MAX) return {err: 'That’s too long to be a wormhole export (256 KB at most).'};
  let o; try{ o = JSON.parse(s); }catch(e){ return {err: 'That isn’t a wormhole export from this tool (it isn’t JSON).'}; }
  if(!o || o.tv !== 'wormholes') return {err: 'That isn’t a wormhole export from this tool.'};
  if(o.v !== 1) return {err: 'That export is from a newer version of this tool; reload the page and try again.'};
  const g = itGraphGet(), now = Date.now(), okT = (t) => Number.isFinite(t) && t >= now - IT_WH_MAX_H * 3600e3 && t <= now + 3600e3;
  const sk = {unknown: 0, old: 0, bad: 0}, out = [];
  const info = (i) => { if(!i || typeof i !== 'object') return undefined; const o2 = {};
    for(const k of ['life', 'mass', 'size']) if(IT_WH_INFO_TXT[k][i[k]]) o2[k] = i[k];
    if(typeof i.cls === 'string' && itWhTyOrCls(i.cls).cls) o2.cls = itWhTyOrCls(i.cls).cls; return Object.keys(o2).length ? o2 : undefined; };
  const sigOk = (x) => x && /^[A-Z]{3}(-\d{1,3})?$/.test(x.sig) && (!x.type || IT_WH_TYPE[x.type]);
  const sigOf = (x, t) => ({sig: x.sig, part: !/^[A-Z]{3}-\d{3}$/.test(x.sig), type: x.type || '', ...(info(x.info) ? {info: info(x.info)} : {}), ...(x.dr === true ? {dr: true} : {}), ...(t ? {t} : {})});
  for(const x of (Array.isArray(o.sys) ? o.sys : []).slice(0, IT_WH_MAX)){
    if(!x || !Number.isInteger(x.id) || !g.at.has(x.id) || itSysName(x.id) !== x.name){ sk.unknown++; continue; }
    const raws = [];
    for(const r of (Array.isArray(x.raws) ? x.raws : []).slice(0, IT_WH_RAW_MAX)){
      if(!r || !okT(r.t) || (r.k !== 'intel' && r.k !== 'hand') || typeof r.raw !== 'string'){ sk.bad++; continue; }
      const set = r.set && typeof r.set === 'object' ? {...(Array.isArray(r.set.sigs) ? {sigs: r.set.sigs.filter(sigOk).slice(0, 8).map(y => sigOf(y))} : {}),
        ...(info(r.set.info) ? {info: info(r.set.info)} : {}), ...(r.set.drNoId === true ? {drNoId: true} : {})} : undefined;
      raws.push({t: r.t, k: r.k, raw: r.raw.slice(0, 400), ...(set ? {set} : {}), n: Math.max(1, Math.min(99, Number(r.n) || 1)), who: IT_WH_PH, via: 'import'});
    }
    const sigs = (Array.isArray(x.sigs) ? x.sigs : []).filter(y => sigOk(y) && okT(y.t)).slice(0, 8).map(y => sigOf(y, y.t));
    const t = Math.max(okT(x.t) ? x.t : 0, ...raws.map(r => r.t));
    if(!t){ sk.old++; continue; }
    if(!raws.length) raws.push({t, k: 'hand', raw: `${x.name} (shared list)`, set: {}, n: 1, who: IT_WH_PH, via: 'import'});   // every time has a line behind it
    out.push({id: x.id, t, info: info(x.info), drNoId: x.drNoId === true, sigs, raws});
  }
  if(!out.length && !sk.unknown && !sk.old) return {err: 'That export has no wormholes in it.'};
  return {sys: out, sk};
}

// ---- D5: a system's details worked out from all its lines. Your own lines (Added by you) win; otherwise the newest report; a detail with no
// line behind it (saved before 044, or its line gone with the cap) is "source unknown": kept, only filled in where empty. A newer shared report
// that disagrees with your value becomes a note.
const IT_WH_DET = ['type', 'cls', 'life', 'mass', 'size'];
function itWhDerive(w, lines){
  const sigs = [], sysd = {}, by = new Map();   // by: line -> the details it decides
  let drNoId = false;
  const find = (sig) => { const h = sigs.filter(s => s.sig.startsWith(sig) || sig.startsWith(s.sig)); return h.length === 1 ? h[0] : null; };
  const put = (d, k, v, rank, t, line) => {
    const c = d[k];
    if(!c || rank > c.rank || (rank === c.rank && t >= c.t)){ d[k] = {v, rank, t, line}; if(c && c.v !== v && rank < c.rank) d[k].note = null; return; }
    if(c.v !== v && rank < c.rank && t > c.t && line && line.via) c.note = {k, v, t};
  };
  // baseline: what the entry holds that its own lines don't explain (source unknown, kept like yours)
  const own = itWhDeriveLines(w, (w.raws || []));
  for(const s of (w.sigs || [])){
    const o = own.find(x => x.sig === s.sig), b = {sig: s.sig, part: s.part, dr: !!s.dr, t: s.t, d: {}};
    const vals = {type: s.type, cls: s.info && s.info.cls, life: s.info && s.info.life, mass: s.info && s.info.mass, size: s.info && s.info.size};
    for(const k of IT_WH_DET) if(vals[k] && (!o || !o.d[k] || o.d[k].v !== vals[k])) b.d[k] = {v: vals[k], rank: 3, t: s.t};
    sigs.push(b);
  }
  if(w.info) for(const k of ['cls', 'life', 'mass', 'size']) if(w.info[k]) sysd[k] = {v: w.info[k], rank: 3, t: w.t};
  for(const r of lines.slice().sort((a, b) => a.t - b.t)){
    const set = itWhLineSet(r), rank = r.k === 'you' ? 2 : 1;
    for(const n of (set.sigs || [])){
      if(itWhGoneSig(w, n.sig, r.t)) continue;
      let s = find(n.sig);
      if(!s){ s = {sig: n.sig, part: n.part, dr: false, t: r.t, d: {}}; sigs.push(s); }
      if(n.sig.length > s.sig.length){ s.sig = n.sig; s.part = n.part; }
      if(n.dr) s.dr = true;
      s.t = Math.max(s.t, r.t);
      const vals = {type: n.type, ...(n.info || {})};
      for(const k of IT_WH_DET) if(vals[k]){ put(s.d, k, vals[k], rank, r.t, r); by.set(r, true); }
      by.set(r, true);
    }
    if(set.info) for(const k of ['cls', 'life', 'mass', 'size']) if(set.info[k]){ put(sysd, k, set.info[k], rank, r.t, r); by.set(r, true); }
    if(set.drNoId) drNoId = true;
  }
  const out = sigs.sort((a, b) => b.t - a.t).slice(0, 8).map(s => { const info = {}; for(const k of ['cls', 'life', 'mass', 'size']) if(s.d[k]) info[k] = s.d[k].v;
    const note = IT_WH_DET.map(k => s.d[k] && s.d[k].note).find(Boolean);
    return {sig: s.sig, part: s.part, type: s.d.type ? s.d.type.v : '', ...(Object.keys(info).length ? {info} : {}), ...(s.dr ? {dr: true} : {}), t: s.t, who: '', ...(note ? {note} : {})}; });
  const info = {}; for(const k of ['cls', 'life', 'mass', 'size']) if(sysd[k]) info[k] = sysd[k].v;
  // the lines that still decide a detail are never dropped by the 10-line cap (D12)
  const backing = new Set(); for(const s of sigs) for(const k of IT_WH_DET) if(s.d[k] && s.d[k].line) backing.add(s.d[k].line); for(const k in sysd) if(sysd[k].line) backing.add(sysd[k].line);
  return {sigs: out, info: Object.keys(info).length ? info : undefined, drNoId: drNoId || !!w.drNoId, backing, notes: out.filter(s => s.note).length};
}
// a plain pass over one side's own lines (for the baseline)
function itWhDeriveLines(w, lines){
  const sigs = [];
  for(const r of lines.slice().sort((a, b) => a.t - b.t)) for(const n of (itWhLineSet(r).sigs || [])){
    const h = sigs.filter(s => s.sig.startsWith(n.sig) || n.sig.startsWith(s.sig)); let s = h.length === 1 ? h[0] : null;
    if(!s){ s = {sig: n.sig, d: {}}; sigs.push(s); } if(n.sig.length > s.sig.length) s.sig = n.sig;
    const vals = {type: n.type, ...(n.info || {})}; for(const k of IT_WH_DET) if(vals[k]) s.d[k] = {v: vals[k]};
  }
  return sigs;
}
// one system merged: its lines joined (one per report; yours kept; count the larger), then its details worked out again
function itWhMergeOne(mine, theirs){
  const lines = (mine && mine.raws ? mine.raws : []).map(r => ({...r})), keys = new Map(lines.map(r => [itWhLineKey(r), r]));
  let newLines = 0, gone = 0;
  for(const r of theirs.raws){
    const set = itWhLineSet(r), base0 = mine || {};
    if((set.sigs || []).length && set.sigs.every(n => itWhGoneSig(base0, n.sig, r.t)) && !set.info && !set.drNoId){ gone++; continue; }   // only IDs you removed, and older: nothing to add
    const k = itWhLineKey(r), have = keys.get(k);
    if(have){ if(r.t > have.t) have.t = r.t; have.n = Math.max(have.n || 1, r.n || 1); continue; }
    const x = {...r}; lines.push(x); keys.set(k, x); newLines++;
  }
  const base = mine || {id: theirs.id, t: 0, sigs: [], drNoId: false};
  const d = itWhDerive({...base, sigs: base.sigs || theirs.sigs, info: mine ? mine.info : theirs.info}, lines);
  const sorted = lines.sort((a, b) => b.t - a.t), kept = [...sorted.filter(r => d.backing.has(r)), ...sorted.filter(r => !d.backing.has(r))].slice(0, IT_WH_RAW_MAX).sort((a, b) => b.t - a.t);
  const top = kept[0] || {t: theirs.t, via: 'import'};
  const w = {...(mine || {}), id: theirs.id, t: Math.max(top.t, mine ? mine.t : 0), sigs: d.sigs, info: d.info, raws: kept, drNoId: d.drNoId || theirs.drNoId || undefined,
    who: top.k === 'intel' ? (top.via ? IT_WH_PH : top.who) : '', src: top.k === 'you' ? 'you' : 'intel', ...(top.via ? {via: 'import'} : {})};
  if(!w.drNoId) delete w.drNoId;
  itWhDrSet(w);
  const oldSigs = new Set((mine && mine.sigs || []).map(s => s.sig));
  return {w, newLines, newSigs: d.sigs.filter(s => !oldSigs.has(s.sig) && ![...oldSigs].some(o => s.sig.startsWith(o))).length, notes: d.notes, gone, dropped: Math.max(0, sorted.length - kept.length)};
}
// D8 / D10: the preview, and the same merge again at "Add to my list"
function itWhImportPlan(rd){
  const st = itWhStore(), now = Date.now(), cut = now - st.keepH * 3600e3, res = {add: 0, addTo: 0, same: 0, newSigs: 0, newLines: 0, notes: 0, old: rd.sk.old, removed: 0, unknown: rd.sk.unknown, over: rd.sk.bad, out: []};
  for(const x of rd.sys){
    if(x.t < cut){ res.old++; continue; }
    if((st.gone[x.id] || 0) >= x.t){ res.removed++; continue; }
    const mine = st.rep[x.id] && st.rep[x.id].t >= cut ? st.rep[x.id] : null;
    const m = itWhMergeOne(mine, x);
    res.over += m.dropped; res.notes += m.notes; res.removed += m.gone;
    if(!mine){ res.add++; res.newSigs += m.newSigs; res.newLines += m.newLines; res.out.push(m.w); continue; }
    if(!m.newLines && !m.newSigs){ res.same++; continue; }
    res.addTo++; res.newSigs += m.newSigs; res.newLines += m.newLines; res.out.push(m.w);
  }
  return res;
}
function itWhImportApply(text){
  const rd = itWhImportRead(text); if(rd.err) return {msg: rd.err};
  const r = itWhImportPlan(rd), st = itWhStore();   // computed again against the store as it is now (another tab may have changed it)
  for(const w of r.out){ st.rep[w.id] = w; delete st.gone[w.id]; }
  itWhSave(); itWhChanged();
  return {msg: `Added ${r.add} system${r.add === 1 ? '' : 's'} and added to ${r.addTo} (${r.newSigs} new ID${r.newSigs === 1 ? '' : 's'}, ${r.newLines} new line${r.newLines === 1 ? '' : 's'}).${r.notes ? ` Kept yours for ${r.notes}: see the ! notes.` : ''}`, r};
}
function itWhPreviewHtml(r){
  const n = (k, one, many) => `${r[k]} ${r[k] === 1 ? one : many}`;
  const skip = [r.old && `${r.old} older than your ${itWhStore().keepH} h`, r.removed && `${r.removed} removed by you`, r.unknown && `${r.unknown} not a system on the map`, r.over && `${r.over} line${r.over === 1 ? '' : 's'} over the limits`].filter(Boolean);
  const head = r.out.length ? `Adds ${n('add', 'system', 'systems')} · adds to ${r.addTo} (${n('newSigs', 'new ID', 'new IDs')}, ${n('newLines', 'new line', 'new lines')}) · already have ${r.same}${r.notes ? ` · kept yours for ${r.notes} (see the ! notes)` : ''}` : `Nothing new: you already have ${r.same}.`;
  return `<div class="it-whp-ph">${escapeHtml(head)}</div>${skip.length ? `<div class="it-whp-psk">${escapeHtml('Skipped: ' + skip.join(' · '))}</div>` : ''}`
    + (r.out.length ? '<div class="it-whp-brow"><button type="button" data-it-whadd>Add to my list</button><button type="button" data-it-whcancel>Cancel</button></div>' : '');
}

// ---- D1 / D2 / D8: the two buttons and their boxes, inside the list panel
function itWhShareHtml(){
  const btn = (k, label, box) => `<button type="button" class="it-whp-xb" data-it-whxb="${k}" aria-expanded="false" aria-controls="${box}">${IT_CHEV}<span>${label}</span></button>`;
  return `<div class="it-whp-share">${btn('exp', 'Export', 'itWhExp')}${btn('imp', 'Import', 'itWhImp')}</div>`
    + '<div class="it-whp-box" id="itWhExp" hidden><div class="it-whp-bl"></div><textarea readonly rows="6" spellcheck="false" aria-label="Your wormhole list as text"></textarea>'
    + '<div class="it-whp-brow"><button type="button" data-it-whcopy>Copy</button><span class="it-whp-bs" role="status"></span></div></div>'
    + '<div class="it-whp-box" id="itWhImp" hidden><div class="it-whp-bl">Paste someone’s wormhole export; you see what it adds before anything changes.</div>'
    + '<textarea rows="6" spellcheck="false" aria-label="A wormhole export to add to your list" placeholder="{&quot;tv&quot;: &quot;wormholes&quot;, …}"></textarea>'
    + '<div class="it-whp-brow"><button type="button" data-it-whimp>Import</button><span class="it-whp-bs" role="status"></span></div><div class="it-whp-prev" hidden></div></div>';
}
function itWhBoxOpen(p, k, open){
  for(const kk of ['exp', 'imp']){
    const b = p.querySelector(`[data-it-whxb="${kk}"]`), box = p.querySelector(kk === 'exp' ? '#itWhExp' : '#itWhImp'), on = kk === k && open;
    b.setAttribute('aria-expanded', String(on)); box.hidden = !on;
  }
  if(!open) return;
  if(k === 'exp'){
    const o = itWhExportObj(), ta = p.querySelector('#itWhExp textarea'), ids = o.sys.reduce((a, x) => a + x.sigs.length, 0);
    ta.value = JSON.stringify(o);
    p.querySelector('#itWhExp .it-whp-bl').textContent = `${o.sys.length} system${o.sys.length === 1 ? '' : 's'}, ${ids} signature ID${ids === 1 ? '' : 's'}; names replaced with <a pilot>.`;
    p.querySelector('#itWhExp .it-whp-bs').textContent = '';
    ta.focus({preventScroll: true}); ta.select();
  } else {
    const ta = p.querySelector('#itWhImp textarea'); p.querySelector('#itWhImp .it-whp-prev').hidden = true; p.querySelector('#itWhImp .it-whp-bs').textContent = '';
    ta.focus({preventScroll: true});
  }
}
function itWhShareClick(e, p){
  const xb = e.target.closest('[data-it-whxb]');
  if(xb){ const k = xb.dataset.itWhxb, open = xb.getAttribute('aria-expanded') !== 'true'; itWhBoxOpen(p, k, open); if(!open) xb.focus(); return true; }
  if(e.target.closest('[data-it-whcopy]')){
    const ta = p.querySelector('#itWhExp textarea'), bs = p.querySelector('#itWhExp .it-whp-bs'), b = e.target.closest('[data-it-whcopy]');
    ta.focus({preventScroll: true}); ta.select();
    (async () => { try{ await navigator.clipboard.writeText(ta.value); b.textContent = 'Copied!'; bs.textContent = ''; setTimeout(() => { b.textContent = 'Copy'; }, 2000); }
      catch(err){ bs.textContent = 'Press Ctrl+C (⌘C) to copy.'; ta.focus({preventScroll: true}); ta.select(); } })();
    return true;
  }
  if(e.target.closest('[data-it-whimp]')){
    const box = p.querySelector('#itWhImp'), ta = box.querySelector('textarea'), pv = box.querySelector('.it-whp-prev'), bs = box.querySelector('.it-whp-bs');
    const rd = itWhImportRead(ta.value);
    if(rd.err){ bs.textContent = rd.err; pv.hidden = true; ta.setAttribute('aria-invalid', 'true'); ta.focus(); return true; }
    ta.removeAttribute('aria-invalid'); bs.textContent = '';
    pv.innerHTML = itWhPreviewHtml(itWhImportPlan(rd)); pv.hidden = false;
    const add = pv.querySelector('[data-it-whadd]'); (add || ta).focus();
    return true;
  }
  if(e.target.closest('[data-it-whadd]')){
    const box = p.querySelector('#itWhImp'), ta = box.querySelector('textarea'), r = itWhImportApply(ta.value);
    p.querySelector('.it-whp-msg').textContent = r.msg; ta.value = ''; box.querySelector('.it-whp-prev').hidden = true;
    itWhBoxOpen(p, 'imp', false); p.querySelector('[data-it-whxb="imp"]').focus();
    return true;
  }
  if(e.target.closest('[data-it-whcancel]')){ const box = p.querySelector('#itWhImp'); box.querySelector('.it-whp-prev').hidden = true; box.querySelector('textarea').focus(); return true; }
  return false;
}
(() => {
  const st = document.createElement('style');
  st.textContent = `.it-whp-share{display:flex; flex-wrap:wrap; gap:6px; margin:8px 0 0;}
    .it-whp-xb{display:inline-flex; align-items:center; gap:6px;} .it-whp-xb svg{transition:transform .15s;} .it-whp-xb[aria-expanded="true"] svg{transform:rotate(180deg);}
    @media (prefers-reduced-motion: reduce){ .it-whp-xb svg{transition:none;} }
    .it-whp-box{margin:6px 0 0; padding:8px; border:1px solid var(--line, #30363d); border-radius:4px;} .it-whp-box[hidden]{display:none;}
    .it-whp-box textarea{display:block; width:100%; box-sizing:border-box; margin:4px 0 6px; font:12px var(--mono, monospace); resize:vertical;}
    .it-whp-bl{color:var(--text-dim, #8b98a5);} .it-whp-brow{display:flex; flex-wrap:wrap; gap:6px; align-items:center;} .it-whp-bs{color:var(--amber, #d99a3c);}
    .it-whp-prev{margin-top:8px; padding-top:6px; border-top:1px solid var(--line, #30363d);} .it-whp-prev[hidden]{display:none;} .it-whp-ph{color:var(--text, #c9d1d9); margin-bottom:4px;} .it-whp-psk{color:var(--text-dim, #8b98a5); margin-bottom:6px;}
    @media (max-width:599px){ .it-whp-xb, .it-whp-brow button{min-height:44px;} .it-whp-box textarea{min-height:88px;} }`;
  document.head.appendChild(st);
})();
