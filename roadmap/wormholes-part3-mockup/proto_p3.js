// MOCKUP prototype: the Wormholes tab, part 3 (Project doc claude/roadmap/wormholes-part3-plan.md).
// Runs after the real page's script (main cb9a995). Everything is made up: wormhole systems picked by position from CCP's own table
// (INTEL_WH), made-up signature IDs and scans, no pilots, no corporations. "Proposed" adds: the Signatures section inside the System panel
// (paste box, Lazy update asking before every removal, Undo, the list: signal colours, type icons, sortable columns, select + Copy / Edit / Delete selected), Connections in the same list (P22), each connection's ID per end, Select all / Remove all on empty space, and Share.
// "Today" is the real page as built. The owner's answers are in the plan's section 10.
(function(){
  'use strict';
  const SK = 'tvWhSigs', EK = 'tvWhEnds', CK = 'tvWhSecs', ROWS = 150;   // anomalies count too now (the owner: "we want ALL items that show up in the system on a probe scan")
  let mode = 'proposed';
  const on = () => mode === 'proposed';
  const css = `
  [data-p3share][hidden]{display:none !important;}
  body.p3 .wh-sec{border-top:1px solid var(--line); padding-top:8px; display:flex; flex-direction:column; gap:6px;}
  body.p3 .wh-sech{display:flex; align-items:center; gap:8px; flex-wrap:nowrap;}
  body.p3 .wh-sech > button.wh-sect{display:flex; align-items:center; gap:6px; padding:0; min-height:28px; border:0; background:none; color:var(--heading); font:700 13px var(--sans); cursor:pointer;}
  body.p3 .wh-sech > button.wh-sect svg{transition:transform .15s;} body.p3 .wh-sech > button.wh-sect[aria-expanded="false"] svg{transform:rotate(-90deg);}
  body.p3 .wh-sech .wh-secn{flex:1 1 auto; min-width:0; color:var(--text-dim); font:12px var(--sans); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
  body.p3 .wh-lz{flex:none; margin-left:auto; display:flex; white-space:nowrap; align-items:center; gap:6px; font:12px var(--sans); color:var(--text); cursor:pointer;}
  body.p3 .wh-paste{display:flex; flex-direction:column; gap:6px;}
  body.p3 .wh-paste textarea{width:100%; box-sizing:border-box; font:12px var(--mono, monospace); resize:vertical;}
  body.p3 .wh-pastet{display:flex; align-items:center; gap:6px; padding:0; min-height:28px; border:0; background:none; color:var(--cyan); font:12px var(--sans); cursor:pointer; align-self:flex-start;}
  body.p3 .wh-pastet[aria-expanded="false"] svg{transform:rotate(-90deg);}
  body.p3 .wh-warn{font:12px var(--sans); color:var(--amber);}
  body.p3 .wh-res{display:flex; align-items:center; gap:8px; font:12px var(--sans); color:var(--text-dim);} body.p3 .wh-res span{white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
  body.p3 .wh-ask{padding:8px; border:1px solid var(--amber); border-radius:4px; background:var(--panel-2); font:12px var(--sans); color:var(--text); display:flex; flex-direction:column; gap:6px;}
  body.p3 .wh-ask div{display:flex; gap:6px;}
  body.p3 .wh-sigs{display:flex; flex-direction:column; gap:2px;}
  body.p3 .wh-sgbar{display:flex; align-items:center; gap:4px; min-height:28px; font:12px var(--sans); color:var(--text-dim);}
  body.p3 .wh-sgbar .n{flex:1 1 auto; white-space:nowrap;} body.p3 .wh-sgbar .n b{color:var(--heading);}
  body.p3 .wh-sgbar button.ib{display:inline-grid; place-items:center; width:28px; min-height:28px; padding:0;}
  body.p3 .wh-sgbar button.ib:disabled{opacity:.35; cursor:default;} body.p3 .wh-sgbar button.ib.dl:not(:disabled){color:var(--danger);}
  body.p3 .wh-sgbar .wh-cf{flex:1 1 100%;}
  body.p3 .wh-sgh, body.p3 .wh-sg{display:grid; grid-template-columns:18px 64px minmax(0, 1fr) 38px 44px; gap:6px; align-items:center; padding:3px 6px; font:12px var(--sans);}
  body.p3 .wh-sgh{color:var(--text-dim); font:600 11px var(--sans); padding-bottom:2px; border-bottom:1px solid var(--line);}
  body.p3 .wh-sgh input{margin:0;} body.p3 .wh-sgh button{display:flex; align-items:center; gap:3px; padding:0; min-height:24px; border:0; background:none; color:inherit; font:inherit; cursor:pointer; white-space:nowrap;}
  body.p3 .wh-sgh button .ar{color:var(--text-faint);} body.p3 .wh-sgh [aria-sort="ascending"] button, body.p3 .wh-sgh [aria-sort="descending"] button{color:var(--cyan);} body.p3 .wh-sgh [aria-sort="ascending"] .ar, body.p3 .wh-sgh [aria-sort="descending"] .ar{color:var(--cyan);}
  body.p3 .wh-sgh .r, body.p3 .wh-sg .pc, body.p3 .wh-sg .ag{justify-self:end; text-align:right;}
  body.p3 .wh-sg{--sg:var(--text-dim); background:var(--panel-2); border-radius:3px; cursor:pointer; outline-offset:-1px;}
  body.p3 .wh-sg.b0{--sg:var(--danger);} body.p3 .wh-sg.b1{--sg:var(--amber);} body.p3 .wh-sg.b2{--sg:var(--exp);} body.p3 .wh-sg.b3{--sg:var(--it-clear);}
  body.p3 .wh-sg .ic{display:grid; place-items:center; color:var(--sg);}
  body.p3 .wh-sg.cm0{--sg:var(--text);} body.p3 .wh-sg.cm1{--sg:var(--amber);} body.p3 .wh-sg.cm2{--sg:var(--danger);}
  body.p3 .wh-sg .nm .ty{color:var(--text-dim); font:11px var(--mono, monospace); margin-left:4px;} body.p3 .wh-sg[data-p3cn] .nm{display:flex; align-items:center; gap:2px;} body.p3 .wh-sg[data-p3cn] .nm .wh-n{min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;}
  body.p3 .wh-cnw .wh-sgh, body.p3 .wh-sg[data-p3cn]{grid-template-columns:18px 64px minmax(0, 1fr) 30px 40px 24px;} body.p3 .wh-sg .gc{justify-self:end;}
  body.p3 .wh-sg .go{flex:none; min-height:22px; min-width:24px; padding:0 4px; border:0; background:none; color:var(--cyan); cursor:pointer; font:13px var(--sans);}
  body.p3 .wh-sg .lf{justify-self:end; font:600 10px var(--sans); color:var(--drain); white-space:nowrap;}
  body.p3 .wh-sge .ot{flex:1 1 100%; color:var(--text-dim); font:11px var(--sans);} body.p3 .wh-sge label.dr{display:flex; align-items:center; gap:4px;}
  body.p3 .gi.wait{display:block; border:1px dotted var(--text-faint); width:9px; height:9px; border-radius:2px;} body.p3 .wh-sg .id{font:600 12px var(--mono, monospace); color:var(--sg);} body.p3 .wh-sg .pc{color:var(--sg); font:11px var(--mono, monospace);}
  body.p3 .wh-sg .nm{min-width:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; color:var(--text);} body.p3 .wh-sg .nm i{font-style:normal; color:var(--text-dim);}
  body.p3 .wh-sg .ag{color:var(--text-dim); font:11px var(--mono, monospace); white-space:nowrap;}
  body.p3 .wh-sg:hover{background:color-mix(in srgb, var(--cyan) 7%, var(--panel-2));}
  body.p3 .wh-sg[aria-selected="true"]{background:color-mix(in srgb, var(--cyan) 18%, var(--panel-2)); box-shadow:inset 2px 0 0 var(--cyan);}
  body.p3 .wh-sg.old > :not(.to){opacity:.5;}
  body.p3 .wh-sg .to{grid-column:3 / -1; font-size:12px; color:var(--text-dim);} body.p3 .wh-sg .to button{min-height:22px; padding:0 6px;}
  body.p3 .wh-sge{display:flex; flex-wrap:wrap; gap:6px; align-items:center; padding:6px; background:var(--panel-2); border-radius:3px; box-shadow:inset 2px 0 0 var(--cyan); font:12px var(--sans);}
  body.p3 .wh-sge input, body.p3 .wh-sge select{min-width:0; font:12px var(--sans);} body.p3 .wh-sge input.i{width:76px; font-family:var(--mono, monospace);} body.p3 .wh-sge input.m{flex:1 1 140px;}
  body.p3 .wh-sge .bt{display:flex; gap:6px; flex:1 1 100%;}
  body.p3 .wh-cf{display:flex; flex-wrap:wrap; align-items:center; gap:6px; grid-column:1 / -1; font:12px var(--sans); color:var(--amber);}
  body.p3 .wh-sg .wh-cf{grid-column:1 / -1;}
  body.p3 .wh-hmenu button.wh-mi{display:flex; align-items:center; gap:8px; width:100%; min-height:32px; padding:0 8px; border:0; border-radius:4px; background:transparent; color:var(--text); font:13px var(--sans); text-align:left; cursor:pointer;}
  body.p3 .wh-hmenu button.wh-mi:hover{background:color-mix(in srgb, var(--cyan) 14%, transparent); color:var(--heading);}
  body.p3 .wh-hmenu button.wh-mdel{color:color-mix(in srgb, var(--danger) 70%, var(--heading));}
  body.p3 .wh-hmenu .wh-vfy{padding:6px 8px; font:12px var(--sans); color:var(--text);} body.p3 .wh-hmenu .wh-vfy div{display:flex; gap:6px; margin-top:6px;}
  body.p3 .wh-hmenu .wh-hr{border-top:1px solid var(--line); margin:4px 0;}
  body.p3 .wh-pop[data-pop="share"]{width:340px; max-width:calc(100vw - 24px);}
  body.p3 .wh-pop[data-pop="share"] textarea{width:100%; box-sizing:border-box; font:11px var(--mono, monospace);}
  body.p3 .wh-shr{display:flex; flex-wrap:wrap; gap:6px; align-items:center; margin:6px 0;} body.p3 .wh-shs{font:12px var(--sans); color:var(--text-dim);}
  body.p3 .wh-pv{font:12px var(--sans); color:var(--text); margin:6px 0;}
  @media (max-width:599px){
    body.p3 .wh-hmenu button.wh-mi, body.p3 .wh-cf button, body.p3 .wh-sech > button.wh-sect, body.p3 .wh-pastet, body.p3 .wh-sec button, body.p3 .wh-pop[data-pop="share"] button, body.p3 .wh-lz{min-height:44px;}
    body.p3 .wh-sgh, body.p3 .wh-sg{grid-template-columns:18px 62px minmax(0, 1fr) 34px 38px; gap:5px;} body.p3 .wh-sg{min-height:44px; padding-top:2px; padding-bottom:2px; box-sizing:border-box;}
    body.p3 .wh-sgbar button.ib{width:44px; min-height:44px;} body.p3 .wh-sgh button{min-height:44px;} body.p3 .wh-sgh input{width:20px; height:20px;}
    body.p3 .wh-sge input, body.p3 .wh-sge select{min-height:44px;} body.p3 .wh-sg .to button, body.p3 .wh-sg .go{min-height:44px; min-width:44px;}
    body.p3 .wh-cnw .wh-sgh, body.p3 .wh-sg[data-p3cn]{grid-template-columns:18px 58px minmax(0, 1fr) 30px 44px;} body.p3 .wh-sg[data-p3cn] .ag, body.p3 .wh-cnw .wh-sgh .ag{display:none;}
  }
  #p3Bar{position:fixed; z-index:99999; left:50%; transform:translateX(-50%); top:8px; display:flex; flex-wrap:wrap; gap:6px; align-items:center; max-width:calc(100vw - 24px); box-sizing:border-box;
    padding:8px 10px; border:1px dashed var(--amber); border-radius:6px; background:#12171c; color:var(--text); font:12px var(--sans); box-shadow:0 6px 20px rgba(0,0,0,.6);}
  #p3Bar b{color:var(--amber); letter-spacing:.5px;} #p3Bar button{min-height:28px; padding:0 9px; font-size:12px;} #p3Bar button[aria-pressed="true"]{background:var(--amber); color:#1b1306;}
  #p3Bar.fold > :not(.p3-fold){display:none;} @media (max-width:599px){ #p3Bar{left:8px; right:8px; transform:none;} #p3Bar button{min-height:36px;} }
  `;
  const js = (k, d) => { try{ const o = JSON.parse(localStorage.getItem(k) || 'null'); return o && o.v === 1 ? o : d; }catch(e){ return d; } };
  const put = (k, o) => { try{ localStorage.setItem(k, JSON.stringify(o)); }catch(e){ } };
  const sigsSt = () => js(SK, {v: 1, lazy: false, sys: {}}), endsSt = () => js(EK, {v: 1, links: {}}), secsSt = () => js(CK, {v: 1, sigs: true});
  const esc = (s) => escapeHtml(String(s));
  const chev = () => IT_CHEV;
  const ago = (t) => { const m = Math.round((Date.now() - t) / 60000); return m < 1 ? 'just now' : m < 60 ? `${m} min ago` : `${Math.round(m / 60)} h ago`; };
  const P3 = {undo: null, res: null, ask: null, pasteOpen: {}, confirm: null, sel: new Set(), selN: null, edit: null, csel: new Set(), cselN: null, cedit: null};
  // the owner, 2026-11-17: "any deletions should require verification." One look everywhere: the delete control turns into a question with Delete / Cancel
  const cfHtml = (q, yes) => `<span class="wh-cf" role="alert">${esc(q)} <button type="button" data-p3="cfyes">${esc(yes)}</button><button type="button" data-p3="cfno">Cancel</button></span>`;

  // ---- made-up chain: CCP's wormhole systems picked by position, made-up IDs; per-end IDs on the first two connections
  const T0 = Date.now() - 3 * 3600e3;
  let PICK = null;
  function picks(){ if(PICK) return PICK; const T = whTable(), J = T.names.filter(n => /^J\d{6}$/.test(n)); PICK = [40, 310, 655, 902, 1210, 1488, 1733, 2011, 2222, 2400, 120].map(i => whIdOf(J[i % J.length])); PICK.th = whIdOf('Thera'); return PICK; }
  function seed(){
    if(localStorage.getItem('tvWhChain')) return;
    const p = picks(), path = [p[0], p[1], p[2], p[1], p[3], p[4], p[3], p[5], p[1], p[6], p.th, p[6], p[7], p[6], p[1]];
    path.forEach((id, i) => whSeen(id, T0 + i * 60e3, false));
    const S = whState(); S.st.sys[p[0]].statics = 'H296 D845'; S.st.sys[p[1]].statics = 'N062';
    S.st.links.forEach((l, i) => { if(i === 0){ l.sig = 'ABC-123'; l.type = 'H296'; } if(i === 2) l.life = 'eol'; if(i === 3){ l.sig = 'QDX-581'; } });
    S.mk[p[0]] = {st: 'home', tag: 'HOME', lock: true}; S.mk[p[4]] = {st: 'warning'};
    whSave(); whMkSave(); S.drawKey = '';
    const l0 = S.st.links[0], E = {v: 1, links: {}};
    E.links[whLinkKey(l0.a, l0.b)] = {[l0.a]: {sig: 'ABC-123', type: 'H296'}, [l0.b]: {sig: 'XYZ-789', type: 'K162'}};
    put(EK, E);
    const G = {v: 1, lazy: false, sys: {}};
    G.sys[l0.b] = {t: T0 + 20 * 60e3, rows: [
      {id: 'XYZ-789', grp: 'Wormhole', nm: 'Unstable Wormhole', pct: 100, f: T0 + 4 * 60e3, t: T0 + 20 * 60e3},
      {id: 'KLM-402', grp: 'Data Site', nm: 'Unsecured Perimeter Comms Relay', pct: 100, f: T0 + 4 * 60e3, t: T0 + 20 * 60e3},
      {id: 'RTA-610', grp: 'Gas Site', nm: 'Barren Perimeter Reservoir', pct: 100, f: T0 + 20 * 60e3, t: T0 + 20 * 60e3},
      {id: 'BHV-118', grp: '', nm: '', pct: 18.4, f: T0 + 20 * 60e3, t: T0 + 20 * 60e3}]};
    put(SK, G);
  }
  // made-up scans for the system in focus (tab-separated, as the plan's Sources row; IDs made up)
  const row = (id, sg, g, n, p) => [id, sg, g, n, p, '4,21 AU'].join('\t');
  function scanA(){ return [row('XYZ-789', 'Cosmic Signature', 'Wormhole', 'Unstable Wormhole', '100,0%'), row('KLM-402', 'Cosmic Signature', 'Data Site', 'Unsecured Perimeter Comms Relay', '100,0%'),
    row('RTA-610', 'Cosmic Signature', 'Gas Site', 'Barren Perimeter Reservoir', '100,0%'), row('BHV-118', 'Cosmic Signature', 'Relic Site', 'Forgotten Perimeter Gateway', '62,5%'),
    row('PLE-930', 'Cosmic Signature', '', '', '0,0%'), row('NOS-275', 'Cosmic Signature', 'Wormhole', 'Unstable Wormhole', '41,0%'),
    row('JKO-554', 'Cosmic Anomaly', 'Combat Site', 'Perimeter Ambush Point', '100,0%'), row('WDE-071', 'Cosmic Anomaly', 'Ore Site', 'Ordinary Perimeter Deposit', '100,0%'), 'Distance\tnot a row'].join('\n'); }
  function scanB(){ return [row('XYZ-789', 'Cosmic Signature', 'Wormhole', 'Unstable Wormhole', '100,0%'), row('BHV-118', 'Cosmic Signature', 'Relic Site', 'Forgotten Perimeter Gateway', '100,0%'),
    row('PLE-930', 'Cosmic Signature', 'Data Site', 'Central Sansha Survey Site', '100,0%'), row('NOS-275', 'Cosmic Signature', 'Wormhole', 'Unstable Wormhole', '100,0%'),
    row('VAQ-812', 'Cosmic Signature', '', '', '4,8%'), row('JKO-554', 'Cosmic Anomaly', 'Combat Site', 'Perimeter Ambush Point', '100,0%'), row('WDE-071', 'Cosmic Anomaly', 'Ore Site', 'Ordinary Perimeter Deposit', '100,0%')].join('\n'); }   // KLM-402 (hacked) and RTA-610 (huffed) gone
  function scanC(){ return [row('NOS-275', 'Cosmic Signature', 'Wormhole', 'Unstable Wormhole', '100,0%')].join('\n'); }   // a scanner window filtered to wormholes

  // ---- the reader (plan P4)
  function scanRows(text){
    const out = [], skip = {bad: 0};
    for(const line of String(text || '').split(/\r?\n/)){
      if(!line.trim()) continue;
      const c = line.split('\t').map(x => x.trim());
      if(!/^[A-Z]{3}-\d{3}$/.test(c[0] || '')){ skip.bad++; continue; }
      if(out.length >= ROWS){ skip.bad++; continue; }
      const pct = Math.max(0, Math.min(100, parseFloat(String(c[4] || '').replace(',', '.').replace('%', '')) || 0));
      out.push({id: c[0], sg: (c[1] || '').slice(0, 24), grp: (c[2] || '').slice(0, 24), nm: (c[3] || '').slice(0, 48), pct});
    }
    return {rows: out, skip};
  }
  // ---- per-end IDs (plan P9-P12)
  function endOf(l, n){ const e = endsSt().links[whLinkKey(l.a, l.b)]; return e && e[n] ? e[n] : null; }
  function endSet(l, n, k, v){ const E = endsSt(), key = whLinkKey(l.a, l.b); E.links[key] = E.links[key] || {}; E.links[key][n] = {...(E.links[key][n] || {}), [k]: v}; if(k === 'sig') delete E.links[key][n].gone; put(EK, E); }
  function endMark(l, n, t){ const E = endsSt(), key = whLinkKey(l.a, l.b); if(!E.links[key] || !E.links[key][n]) return; if(t) E.links[key][n].gone = t; else delete E.links[key][n].gone; put(EK, E); }
  function sideId(l, n){ const e = endOf(l, n); return e && e.sig ? {sig: e.sig, type: e.type || '', own: true, gone: e.gone} : l.sig ? {sig: l.sig, type: l.type || '', own: false} : null; }
  function matchLink(n, id){ for(const l of whLinksOf(n)){ const s = sideId(l, n); if(s && (s.sig === id || (s.sig.length < 7 && id.startsWith(s.sig)))) return l; } return null; }

  // ---- the paste (plan P5, P6)
  function readScan(n, text, force){
    const r = scanRows(text);
    if(!r.rows.length){ P3.res = {err: 'Nothing in that looks like the Probe Scanner’s list. In the game: the Probe Scanner, Ctrl+A, Ctrl+C, then paste here.'}; return false; }
    const G = sigsSt(), cur = (G.sys[n] && G.sys[n].rows) || [], now = Date.now(), byId = new Map(cur.map(x => [x.id, {...x}]));
    let up = 0, add = 0; const seen = new Set();
    for(const x of r.rows){ seen.add(x.id); const o = byId.get(x.id);
      if(o){ o.pct = x.pct; o.t = now; if(x.sg) o.sg = x.sg; if(x.grp){ o.grp = x.grp; o.nm = x.nm; } up++; } else { byId.set(x.id, {...x, f: now, t: now}); add++; } }
    const gone = G.lazy ? cur.filter(x => !seen.has(x.id)).map(x => x.id) : [];
    if(G.lazy && gone.length && !force){ P3.ask = {n, text, gone: gone.length, of: cur.length}; return true; }   // the owner, 2026-11-17: "let's have the lazy update ask for verification every time."
    const keepAll = force === 'keep';
    P3.undo = {n, rows: cur.map(x => ({...x})), t: G.sys[n] ? G.sys[n].t : 0, ends: JSON.parse(JSON.stringify(endsSt()))};
    const removed = keepAll ? [] : gone;
    for(const id of removed){ byId.delete(id); const l = matchLink(n, id); if(l) endMark(l, n, now); }
    for(const id of seen){ const l = matchLink(n, id); if(l) endMark(l, n, 0); }
    G.sys[n] = {t: now, rows: [...byId.values()].sort((a, b) => b.t - a.t || a.id.localeCompare(b.id))}; put(SK, G);
    const an = r.rows.filter(x => /anomaly/i.test(x.sg)).length, sk = [an && `${an} of them anomal${an === 1 ? 'y' : 'ies'}`, r.skip.bad && `${r.skip.bad} line${r.skip.bad === 1 ? '' : 's'} not read`].filter(Boolean).join(', ');
    P3.res = {txt: `Updated ${up} · added ${add}${G.lazy ? ` · removed ${removed.length}` : ''}`, tip: [sk, removed.length ? 'Removed: ' + removed.join(', ') : ''].filter(Boolean).join('. ')};
    P3.ask = null; P3.pasteOpen[n] = false; return true;
  }
  function undo(){
    const u = P3.undo; if(!u) return; const G = sigsSt();
    if(u.rows.length) G.sys[u.n] = {t: u.t, rows: u.rows}; else delete G.sys[u.n];
    put(SK, G); put(EK, u.ends); P3.undo = null; P3.res = {txt: 'Undone: the list is back as it was.'};
  }

  // ---- the list (owner 2026-11-17: in-game concepts, own design): colour by the game's signal bands, a type icon, sortable
  // columns kept as you left them, short ages, select like the map, Copy / Edit / Delete selected (every delete asks)
  const band = (p) => p >= 100 ? 3 : p >= 75 ? 2 : p >= 25 ? 1 : 0;
  const BAND_TXT = ['under 25%: not located', '25–74%', '75–99%', '100%: warpable'];
  const svg = (d, extra) => `<svg viewBox="0 0 12 12" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${extra || ''}>${d}</svg>`;
  // The game's Probe Scanner icons, redrawn as shapes (the owner, 2026-11-17: "the icons you changed, should not be changed for signature types...
  // they reflect the actual in-game icons.", then "it's fine to re-draw them, just use the same shapes", "that'll allow you to draw them in any color
  // you need"): traced from his screenshots of the game, drawn in currentColor so each takes the row's colour. Traced so far: Wormhole, Data Site, Relic Site, Gas Site, Combat Site, Ore Site (asteroid belt). The cross for a result at 0% and the dot for one partly scanned, type not shown yet. Structures and others as he meets them;
  // until then a kind without a shape shows a dim placeholder.
  const WH_SWIRL = 'M5.00 3.50Q6.90 1.70 8.90 0.40Q7.30 2.40 7.50 4.30ZM7.67 3.88Q10.17 4.63 12.30 5.71Q9.77 5.33 8.22 6.45ZM8.67 6.38Q9.27 8.93 9.40 11.31Q8.47 8.93 6.72 8.15ZM7.00 8.50Q5.10 10.30 3.10 11.60Q4.70 9.60 4.50 7.70ZM4.33 8.12Q1.83 7.37 -0.30 6.29Q2.23 6.67 3.78 5.55ZM3.33 5.62Q2.73 3.07 2.60 0.69Q3.53 3.07 5.28 3.85Z';   // the wormhole shape's arms (its centre: a circle r 3 at 6,6); one drawing for the list and the map
  const GAME_ICON = {'Wormhole': `<svg viewBox="0 0 12 12" width="12" height="12" fill="currentColor" aria-hidden="true"><circle cx="6" cy="6" r="3"/><path d="${WH_SWIRL}"/></svg>`,
    'Data Site': '<svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true" stroke="currentColor"><rect x="1.3" y="1.3" width="9.4" height="9.4" fill="currentColor" fill-opacity=".4" stroke-width="1.1"/><path d="M3.8 3.4V8.6M6 3.4V8.6M8.2 3.4V8.6" stroke-width="1.2"/></svg>',
    'Relic Site': '<svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><circle cx="6" cy="4.3" r="2.9" fill="currentColor" fill-opacity=".4" stroke="currentColor" stroke-width="1.1"/><rect x=".6" y="3.3" width="1.7" height="1.9" rx=".4" fill="currentColor"/><rect x="9.7" y="3.3" width="1.7" height="1.9" rx=".4" fill="currentColor"/><path d="M1.6 5.4L3.3 9.5Q3.7 10.5 4.6 10.5H7.4Q8.3 10.5 8.7 9.5L10.4 5.4" fill="none" stroke="currentColor" stroke-width="1.1" stroke-linejoin="round" stroke-linecap="round"/></svg>',
    'Combat Site': '<svg viewBox="0 0 12 12" width="12" height="12" fill="currentColor" aria-hidden="true"><path d="M6 .9L8.8 3.6H3.2Z"/><path d="M.7 5.3L3.5 4.3L6 5.9L8.5 4.3L11.3 5.3L6 11.1Z"/></svg>',
    'Ore Site': '<svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true" fill="currentColor" fill-opacity=".4" stroke="currentColor" stroke-width="1.1"><ellipse cx="6" cy="3.4" rx="3.4" ry="2.7"/><ellipse cx="3.3" cy="9.2" rx="2.6" ry="1.6"/><ellipse cx="8.7" cy="9.2" rx="2.6" ry="1.6"/></svg>',   // asteroid belts (anomalies, listed too: the owner, "we want ALL items that show up in the system on a probe scan")
    'Gas Site': '<svg viewBox="0 0 12 12" width="12" height="12" aria-hidden="true"><path d="M1.5 1.5H4.6L6 2.4L7.4 1.5H10.5V4.4L8.4 10.5H3.6L1.5 4.4Z" fill="currentColor" fill-opacity=".4" stroke="currentColor" stroke-width="1.1" stroke-linejoin="round"/></svg>'};
  const WAIT = '<span class="gi wait" aria-hidden="true" title="No shape drawn yet for this kind"></span>';   // a kind we have no shape for yet (structures and others, as the owner meets them)
  const GROUPS = ['Wormhole', 'Data Site', 'Relic Site', 'Gas Site', 'Combat Site', 'Ore Site'];
  const TICON = Object.fromEntries(GROUPS.map(g => [g, GAME_ICON[g] || WAIT]));
  const UNK ='<svg viewBox="0 0 12 12" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" aria-hidden="true"><path d="M3.3 3.3L8.7 8.7M8.7 3.3L3.3 8.7"/></svg>';   // the game's mark for a result not scanned far enough to show its type (a cross)
  const DOT = '<svg viewBox="0 0 12 12" width="12" height="12" fill="currentColor" aria-hidden="true"><circle cx="6" cy="6" r="3.9"/></svg>';   // the game's mark for a partly scanned result whose type isn't shown yet (a dot)
  const IB ={copy: svg('<rect x="4" y="4" width="6.4" height="6.4" rx="1"/><path d="M8 4V2.4a.8.8 0 0 0-.8-.8H2.4a.8.8 0 0 0-.8.8v4.8a.8.8 0 0 0 .8.8H4"/>'),
    edit: svg('<path d="M8.2 1.8 10.2 3.8 4 10H2V8z"/>'), del: svg('<path d="M2 3.2h8M4.6 3.2V2h2.8v1.2M3.2 3.2l.5 7h4.6l.5-7"/>')};
  const age = (t) => { const x = Math.max(0, Math.round((Date.now() - t) / 1000)); return x < 60 ? `${x} s` : x < 3600 ? `${Math.floor(x / 60)} min` : x < 172800 ? `${Math.floor(x / 3600)} h` : `${Math.floor(x / 86400)} d`; };
  const SORTS = {id: ['ID', (a, b) => a.id.localeCompare(b.id)], nm: ['Name', (a, b) => ((a.grp || '~') + (a.nm || '')).localeCompare((b.grp || '~') + (b.nm || '')) || a.id.localeCompare(b.id)],
    pct: ['Signal', (a, b) => a.pct - b.pct || a.id.localeCompare(b.id)], f: ['Age', (a, b) => (b.f || b.t) - (a.f || a.t) || a.id.localeCompare(b.id)]};
  const sortOf = () => { const S = sigsSt().sort; return S && SORTS[S.k] ? S : {k: 'f', d: 1}; };   // default: Age ascending = newest first (each key's natural order is d 1)
  function selFor(n){ if(P3.selN !== n){ P3.selN = n; P3.sel = new Set(); P3.edit = null; } return P3.sel; }
  function listHtml(n, s, rows){
    const so = sortOf(), sel = selFor(n), cmp = SORTS[so.k][1], sorted = [...rows].sort((a, b) => so.d * cmp(a, b));
    for(const id of [...sel]) if(!rows.some(r => r.id === id)) sel.delete(id);
    const k = sel.size, all = k === rows.length;
    const cf = P3.confirm && P3.confirm.kind === 'sigs' && P3.confirm.n === n ? cfHtml(`Delete ${k} signature${k === 1 ? '' : 's'}?`, 'Delete') : '';
    const bar = `<div class="wh-sgbar"><span class="n">Selected: <b>${k}</b> of ${rows.length}</span>`
      + `<button type="button" class="ib" data-p3="sgcopy"${k ? '' : ' disabled'} title="Copy selected (in the game's own format)" aria-label="Copy selected">${IB.copy}</button>`
      + `<button type="button" class="ib" data-p3="sgedit"${k ? '' : ' disabled'} title="Edit selected" aria-label="Edit selected">${IB.edit}</button>`
      + `<button type="button" class="ib dl" data-p3="sgdel"${k ? '' : ' disabled'} title="Delete selected" aria-label="Delete selected">${IB.del}</button>${cf}</div>`;
    const multi = P3.edit === '*' && k > 1 ? `<div class="wh-sge" role="group" aria-label="Edit ${k} signatures">Type of the ${k} selected: <select data-p3e="grp"><option value="">(not known)</option>${GROUPS.map(g => `<option>${g}</option>`).join('')}</select>`
      + `<span class="bt"><button type="button" data-p3="esave">Save</button><button type="button" data-p3="eno">Cancel</button></span></div>` : '';
    const th = (key, cls) => `<span role="columnheader"${cls ? ` class="${cls}"` : ''} aria-sort="${so.k === key ? (so.d === 1 ? 'ascending' : 'descending') : 'none'}"><button type="button" data-p3="sort" data-k="${key}" title="Sort by ${SORTS[key][0].toLowerCase()}">${SORTS[key][0]}<span class="ar" aria-hidden="true">${so.k === key ? (so.d === 1 ? '↑' : '↓') : '↕'}</span></button></span>`;
    const head = `<div class="wh-sgh" role="row"><span role="columnheader"><input type="checkbox" data-p3="sgall" aria-label="Select all signatures"${all ? ' checked' : ''}></span>${th('id')}${th('nm')}${th('pct', 'r')}${th('f', 'r')}</div>`;
    const body = sorted.map(x => {
      if(P3.edit === x.id && k === 1) return `<div class="wh-sge" role="row" aria-label="Edit ${esc(x.id)}"><input class="i" data-p3e="id" value="${esc(x.id)}" aria-label="Signature ID" maxlength="7">`
        + `<select data-p3e="grp" aria-label="Type"><option value=""${x.grp ? '' : ' selected'}>(not known)</option>${GROUPS.map(g => `<option${g === x.grp ? ' selected' : ''}>${g}</option>`).join('')}</select>`
        + `<input class="m" data-p3e="nm" value="${esc(x.nm || '')}" placeholder="Name" aria-label="Name" maxlength="48"><span class="bt"><button type="button" data-p3="esave">Save</button><button type="button" data-p3="eno">Cancel</button></span></div>`;
      const l = matchLink(n, x.id), o = l ? (l.a === n ? l.b : l.a) : null, b = band(x.pct), old = s.t && x.t < s.t;
      const tip = `${x.sg ? x.sg + ' · ' : ''}${x.grp || 'Type not known yet'}${x.nm ? ' · ' + x.nm : ''} · signal ${Math.round(x.pct)}% (${BAND_TXT[b]}) · first seen ${age(x.f || x.t)} ago · last in a scan ${age(x.t)} ago${old ? ' · not in your last scan' : ''}`;
      return `<div class="wh-sg b${b}${old ? ' old' : ''}" role="row" tabindex="0" aria-selected="${sel.has(x.id)}" data-p3row="${esc(x.id)}" title="${esc(tip)}">`
        + `<span class="ic" role="gridcell">${x.grp ? (TICON[x.grp] || WAIT) : x.pct > 0 ? DOT : UNK}</span><span class="id" role="gridcell">${esc(x.id)}</span>`
        + `<span class="nm" role="gridcell">${x.nm ? esc(x.nm) : x.grp ? esc(x.grp) : '<i>not known</i>'}</span>`
        + `<span class="pc" role="gridcell">${esc(Math.round(x.pct))}%</span><span class="ag" role="gridcell">${esc(age(x.f || x.t))}</span>`
        + (o !== null ? `<span class="to">→ <button type="button" class="wh-n sm" data-wh-sel="${Number(o)}">${whNameHtml(o)}</button></span>` : '') + '</div>';
    }).join('');
    return `${bar}${multi}<div class="wh-sgt" role="grid" aria-label="Signatures in ${esc(whName(n))}" aria-multiselectable="true">${head}${body}</div>`;
  }
  function gameRows(n, ids){ const G = sigsSt(), rows = (G.sys[n] && G.sys[n].rows) || [];
    return rows.filter(r => ids.has(r.id)).map(r => [r.id, r.sg || 'Cosmic Signature', r.grp || '', r.nm || '', `${(Math.round(r.pct * 10) / 10).toFixed(1)}%`, ''].join('\t')).join('\n'); }
  function rowClick(ev, id){
    const sel = selFor(whFocus()), add = ev.ctrlKey || ev.metaKey || ev.shiftKey || ev.pointerType === 'touch' || ev.type === 'keydown';
    if(add){ if(sel.has(id)) sel.delete(id); else sel.add(id); } else { const only = sel.size === 1 && sel.has(id); sel.clear(); if(!only) sel.add(id); }
    P3.edit = null; P3.confirm = null; refresh();
    const r = sec() && sec().querySelector(`[data-p3row="${id}"]`); if(r) r.focus({preventScroll: true});
  }
  // ---- Connections in the same list (the owner, 2026-11-17: "can we treat connections similarly though?", then "sounds good. let's see it mocked up."):
  // one row per connection, coloured by mass (normal / reduced / critical), an EOL mark, Edit / Delete selected, "→" to the other system, no Copy
  const LIFE = IT_WH_INFO_TXT.life, MASS = IT_WH_INFO_TXT.mass, SIZE = IT_WH_INFO_TXT.size;
  const cnSortOf = () => { const S = secsSt().cn; return S && ['id', 'to', 'lf', 'f'].includes(S.k) ? S : {k: 'f', d: 1}; };
  function cselFor(n){ if(P3.cselN !== n){ P3.cselN = n; P3.csel = new Set(); P3.cedit = null; } return P3.csel; }
  function cnRows(n){ return whLinksOf(n).map(l => { const o = l.a === n ? l.b : l.a, me = sideId(l, n), ot = sideId(l, o); return {l, key: whLinkKey(l.a, l.b), o, me, ot, name: whName(o)}; }); }
  const CN_SORTS = {id: ['ID', (a, b) => ((a.me && a.me.sig) || '~').localeCompare((b.me && b.me.sig) || '~') || a.name.localeCompare(b.name)], to: ['To', (a, b) => a.name.localeCompare(b.name)],
    lf: ['Life', (a, b) => (({lt1h: 0, eol: 1, lt1d: 2})[a.l.life] ?? 3) - (({lt1h: 0, eol: 1, lt1d: 2})[b.l.life] ?? 3) || a.name.localeCompare(b.name)], f: ['Age', (a, b) => (b.l.t || 0) - (a.l.t || 0) || a.name.localeCompare(b.name)]};
  const opts = (T, v, none) => `<option value="">${none}</option>` + Object.entries(T).map(([x, [a, b]]) => `<option value="${x}" title="${esc(b)}"${x === v ? ' selected' : ''}>${esc(a)}</option>`).join('');
  function cnListHtml(n){
    const R = cnRows(n), so = cnSortOf(), sel = cselFor(n), cmp = CN_SORTS[so.k][1], sorted = [...R].sort((a, b) => so.d * cmp(a, b));
    for(const k of [...sel]) if(!R.some(r => r.key === k)) sel.delete(k);
    if(!R.length) return '<div class="wh-note">No connections yet.</div>';
    const k = sel.size, all = k === R.length;
    const cf = P3.confirm && P3.confirm.kind === 'cns' && P3.confirm.n === n ? cfHtml(`Delete ${k} connection${k === 1 ? '' : 's'}?`, 'Delete') : '';
    const bar = `<div class="wh-sgbar"><span class="n">Selected: <b>${k}</b> of ${R.length}</span>`
      + `<button type="button" class="ib" data-p3="cnedit"${k ? '' : ' disabled'} title="Edit selected" aria-label="Edit selected connections">${IB.edit}</button>`
      + `<button type="button" class="ib dl" data-p3="cndel"${k ? '' : ' disabled'} title="Delete selected" aria-label="Delete selected connections">${IB.del}</button>${cf}</div>`;
    const multi = P3.cedit === '*' && k > 1 ? `<div class="wh-sge" role="group" aria-label="Edit ${k} connections">For the ${k} selected: <select data-p3c="life" aria-label="Life">${opts(LIFE, '', 'Life: keep')}</select><select data-p3c="mass" aria-label="Mass">${opts(MASS, '', 'Mass: keep')}</select>`
      + `<span class="bt"><button type="button" data-p3="cnsave">Save</button><button type="button" data-p3="cnno">Cancel</button></span></div>` : '';
    const th = (key, cls) => `<span role="columnheader"${cls ? ` class="${cls}"` : ''} aria-sort="${so.k === key ? (so.d === 1 ? 'ascending' : 'descending') : 'none'}"><button type="button" data-p3="cnsort" data-k="${key}" title="Sort by ${CN_SORTS[key][0].toLowerCase()}">${CN_SORTS[key][0]}<span class="ar" aria-hidden="true">${so.k === key ? (so.d === 1 ? '↑' : '↓') : '↕'}</span></button></span>`;
    const head = `<div class="wh-sgh" role="row"><span role="columnheader"><input type="checkbox" data-p3="cnall" aria-label="Select all connections"${all ? ' checked' : ''}></span>${th('id')}${th('to')}${th('lf', 'r')}${th('f', 'r ag')}<span role="columnheader" aria-label="Go"></span></div>`;
    const body = sorted.map(r => {
      const l = r.l, me = r.me, ot = r.ot;
      if(P3.cedit === r.key && k === 1) return `<div class="wh-sge" role="row" data-p3ce="${esc(r.key)}" aria-label="Edit the connection to ${esc(r.name)}"><input class="i" data-p3c="sig" value="${esc(me && me.own ? me.sig : '')}" placeholder="Sig ID here" aria-label="Signature ID in ${esc(whName(n))}" maxlength="7">`
        + `<input class="i" data-p3c="type" value="${esc(me && me.own ? me.type : '')}" placeholder="Type here" aria-label="Type in ${esc(whName(n))}" maxlength="4" style="width:58px">`
        + `<select data-p3c="life" aria-label="Life">${opts(LIFE, l.life, 'Life')}</select><select data-p3c="mass" aria-label="Mass">${opts(MASS, l.mass, 'Mass')}</select><select data-p3c="size" aria-label="Size">${opts(SIZE, l.size, 'Size')}</select>`
        + `<label class="dr"><input type="checkbox" data-p3c="dr"${l.dr ? ' checked' : ''}> Drifter</label>`
        + `<span class="ot">Other side: <button type="button" class="wh-n sm" data-wh-sel="${Number(r.o)}">${whNameHtml(r.o)}</button>${ot && ot.own ? ` · ${esc([ot.sig, ot.type].filter(Boolean).join(' '))}` : ''}</span>`
        + `<span class="bt"><button type="button" data-p3="cnsave">Save</button><button type="button" data-p3="cnno">Cancel</button></span></div>`;
      const m = l.mass === 'critical' ? 2 : l.mass === 'reduced' ? 1 : 0, gone = me && me.gone, lf = l.life === 'eol' || l.life === 'lt1h' ? (l.life === 'lt1h' ? '<1h' : 'EOL') : '';
      const tip = [`To ${r.name}`, me ? `this side ${[me.sig, me.type].filter(Boolean).join(' ')}${me.own ? '' : ' (side not known)'}` : 'no ID this side', ot && ot.own ? `other side ${[ot.sig, ot.type].filter(Boolean).join(' ')}` : '',
        l.life && LIFE[l.life] ? LIFE[l.life][1] : '', l.mass && MASS[l.mass] ? MASS[l.mass][1] : '', l.size && SIZE[l.size] ? SIZE[l.size][1] : '', l.dr ? 'Drifter hole' : '', `found ${age(l.t)} ago`, gone ? 'its ID wasn’t in your last scan here' : ''].filter(Boolean).join(' · ');
      return `<div class="wh-sg cm${m}${gone ? ' old' : ''}" role="row" tabindex="0" aria-selected="${sel.has(r.key)}" data-p3cn="${esc(r.key)}" title="${esc(tip)}">`
        + `<span class="ic" role="gridcell">${GAME_ICON.Wormhole}</span><span class="id" role="gridcell">${me && me.sig ? esc(me.sig) : '<i style="font-style:normal;color:var(--text-faint)">—</i>'}</span>`
        + `<span class="nm" role="gridcell"><span class="wh-n">${whNameHtml(r.o)}</span>${me && me.type ? `<span class="ty">${esc(me.type)}</span>` : ''}${l.dr ? '<span class="ty">Drifter</span>' : ''}</span>`
        + `<span class="lf" role="gridcell">${lf}</span><span class="ag" role="gridcell">${esc(age(l.t || Date.now()))}</span><span class="gc" role="gridcell"><button type="button" class="go" data-wh-sel="${Number(r.o)}" aria-label="Go to ${esc(r.name)}" title="Go to ${esc(r.name)}">→</button></span></div>`;
    }).join('');
    return `${bar}${multi}<div class="wh-sgt" role="grid" aria-label="Connections of ${esc(whName(n))}" aria-multiselectable="true">${head}${body}</div>`;
  }
  function cnRowClick(ev, key){
    const sel = cselFor(whFocus()), add = ev.ctrlKey || ev.metaKey || ev.shiftKey || ev.pointerType === 'touch' || ev.type === 'keydown';
    if(add){ if(sel.has(key)) sel.delete(key); else sel.add(key); } else { const only = sel.size === 1 && sel.has(key); sel.clear(); if(!only) sel.add(key); }
    P3.cedit = null; P3.confirm = null; refresh();
    const r = whS.el.querySelector(`#whPnSum [data-p3cn="${CSS.escape(key)}"]`); if(r) r.focus({preventScroll: true});
  }
  // ---- the section (plan P1, P2, P5, P7)
  function sigsHtml(n){
    const G = sigsSt(), s = G.sys[n], rows = (s && s.rows) || [], open = secsSt().sigs !== false, me = whS.last;
    const head = `<div class="wh-sech"><button type="button" class="wh-sect" data-p3="sec" aria-expanded="${open}" aria-controls="whSecSigs">${chev()}Signatures</button>`
      + `<span class="wh-secn" title="${esc(rows.length ? `${rows.length} kept · scanned ${ago(s.t)}` : 'none kept')}">${esc(rows.length ? `(${rows.length}) · ${ago(s.t)}` : '(0)')}</span>`
      + `<label class="wh-lz" title="On: a paste is the whole list, and signatures missing from it go. Off: a paste only adds and updates."><input type="checkbox" class="mys-sw" role="switch" data-p3="lazy"${G.lazy ? ' checked' : ''}> Lazy update</label></div>`;
    if(!open) return `<div class="wh-sec" data-p3sec>${head}</div>`;
    const showBox = !rows.length || P3.pasteOpen[n] || (P3.res && P3.res.err);
    const warn = me !== null && me !== n ? `<div class="wh-warn">Goes to ${esc(whName(n))}; you’re in ${esc(whName(me))}.</div>` : '';
    const box = showBox ? `<div class="wh-paste">${rows.length ? `<button type="button" class="wh-pastet" data-p3="fold" aria-expanded="true">${chev()}Paste a new scan</button>` : ''}`
      + `<textarea rows="4" data-p3="ta" spellcheck="false" placeholder="Paste the Probe Scanner list (Ctrl+A, Ctrl+C in the game)" aria-label="Probe Scanner list for ${esc(whName(n))}"></textarea>${warn}`
      + `<div><button type="button" data-p3="read">Read scan</button></div></div>`
      : `<button type="button" class="wh-pastet" data-p3="unfold" aria-expanded="false">${chev()}Paste a new scan</button>`;
    const ask = P3.ask && P3.ask.n === n ? `<div class="wh-ask" role="alert">This scan would remove ${P3.ask.gone} of ${P3.ask.of} signatures.<div><button type="button" data-p3="rm">Remove them</button><button type="button" data-p3="keep">Keep them</button></div></div>` : '';
    const res = P3.res ? (P3.res.err ? `<div class="wh-warn" role="status">${esc(P3.res.err)}</div>` : `<div class="wh-res" role="status"><span title="${esc(P3.res.tip || '')}">${esc(P3.res.txt)}</span>${P3.undo && P3.undo.n === n ? '<button type="button" data-p3="undo">Undo</button>' : ''}</div>`) : '';
    const list = rows.length ? listHtml(n, s, rows) : `<div class="wh-note">No signatures kept for ${esc(whName(n))}.</div>`;
    return `<div class="wh-sec" data-p3sec>${head}<div id="whSecSigs" class="wh-sec">${box}${ask}${res}<div class="wh-sigs">${list}</div></div></div>`;
  }
  // ---- System's body, proposed: Class and Statics, then Connections in the list (P22), then Signatures (plan P1, P7)
  const realSum = whSumHtml;
  window.whSumHtml = function(n){
    const html = realSum(n); if(!on()) return html;
    const t = document.createElement('template'); t.innerHTML = html;
    const ed = t.content.querySelector('.wh-ed'), cns = t.content.querySelector('.wh-cns');
    if(cns && ed){
      const wrap = document.createElement('div'); wrap.dataset.whEd = String(n); wrap.className = 'wh-cnw'; cns.classList.remove('wide'); wrap.appendChild(cns); ed.before(wrap);
      // the owner, 2026-11-17: "class and statics - i'd move these above connections. connections change, class and statics do not."
      const fixed = [ed.querySelector('[data-f="cls"]'), ed.querySelector('[data-f="statics"]')].filter(Boolean).map(f => f.closest('label'));
      if(fixed.length){ const top = document.createElement('div'); top.dataset.whEd = String(n); top.className = 'wh-ed wh-cs'; fixed.forEach(x => top.appendChild(x)); wrap.before(top); }
      wrap.innerHTML = '<div class="wh-sub">Connections</div>' + cnListHtml(n);   // P19 replaced: Connections in P21's list
      if(P3.confirm && P3.confirm.kind === 'del' && P3.confirm.n === n){ const x = t.content.querySelector('.wh-rm'); if(x) x.outerHTML = cfHtml(`Remove ${whName(n)} and its connections?`, 'Remove'); }
      wrap.insertAdjacentHTML('afterend', sigsHtml(n));
    }
    return t.innerHTML;
  };
  // ---- the map: a small wormhole mark at each end of a line, where it meets that end's box, for every end that has an ID (the owner,
  // 2026-11-17: "connections will have two IDs, one in each system", "might not be enough room to actually write out the ID on every connection.
  // maybe some kind of connector on each end that shows the signature ID on hover?", then "could use a small version of the wormhole icon?").
  // No text on the lines; the ID in the mark's hover, a tap on a phone puts it in the tab's message line. An old connection whose one ID has no
  // known side gets a mark at both ends ("side not known"). Fixed size on screen; none when zoomed far out (where the grid coarsens, s < 0.45).
  const SWIRL = typeof Path2D === 'function' ? (() => { const p = new Path2D(WH_SWIRL); p.addPath(new Path2D('M9 6A3 3 0 1 1 3 6A3 3 0 1 1 9 6Z')); return p; })() : null;
  const END_PX = 14, END_R = 9, END_HIT = 12, END_MIN_S = 0.45;
  P3.ends = [];
  function bez(a, b){   // the page's own curve for a line (whDraw): horizontal-first or vertical-first by the longer side
    const v = Math.abs(b.y - a.y) > Math.abs(b.x - a.x), m = v ? (a.y + b.y) / 2 : (a.x + b.x) / 2;
    const c1 = v ? {x: a.x, y: m} : {x: m, y: a.y}, c2 = v ? {x: b.x, y: m} : {x: m, y: b.y};
    return (t) => { const u = 1 - t; return {x: u * u * u * a.x + 3 * u * u * t * c1.x + 3 * u * t * t * c2.x + t * t * t * b.x, y: u * u * u * a.y + 3 * u * u * t * c1.y + 3 * u * t * t * c2.y + t * t * t * b.y}; };
  }
  function edgeT(f, p, from){   // where the curve leaves the box at p (WH_NW x WH_NH), walking from its end; the mark sits just outside it
    const pad = (END_R + 2) / whS.M.cam.s, inside = (q) => q.x >= p.x - pad && q.x <= p.x + WH_NW + pad && q.y >= p.y - pad && q.y <= p.y + WH_NH + pad;
    for(let i = 1; i <= 100; i++){ const t = from ? i / 100 : 1 - i / 100, q = f(t); if(!inside(q)) return q; }
    return f(0.5);
  }
  function endTxt(l, n, s){ const o = l.a === n ? l.b : l.a; return `${[s.sig, s.type].filter(Boolean).join(' ')} in ${whName(n)}, to ${whName(o)}${s.own ? '' : ' (side not known)'}`; }
  const realDraw = whDraw;
  window.whDraw = function(){
    if(!on()) return realDraw();
    const S = whS, saved = S.st.links.map(l => [l.sig, l.type]);
    S.st.links.forEach(l => { l.sig = ''; l.type = ''; });   // no text on the lines any more
    try{ realDraw(); } finally { S.st.links.forEach((l, i) => { l.sig = saved[i][0]; l.type = saved[i][1]; }); }
    P3.ends = [];
    const M = S.M, cv = S.el.querySelector('.wh-box canvas'); if(!M.cam || cv.hidden || !SWIRL || M.cam.s < END_MIN_S) return;
    const c = cv.getContext('2d'), dpr = window.devicePixelRatio || 1, s = M.cam.s, C = whCols(), W = cv.width / dpr, H = cv.height / dpr;
    const scr = (q) => ({x: (q.x - M.cam.x) * s, y: (q.y - M.cam.y) * s});
    for(const l of S.st.links){
      const pa = M.P.get(l.a), pb = M.P.get(l.b); if(!pa || !pb) continue;
      const f = bez({x: pa.x + WH_NW / 2, y: pa.y + WH_NH / 2}, {x: pb.x + WH_NW / 2, y: pb.y + WH_NH / 2});
      const col = l.mass === 'critical' ? C.hi : l.mass === 'reduced' ? C.mid : C.dim, key = whLinkKey(l.a, l.b);
      let ms = [[l.a, pa, true], [l.b, pb, false]].map(([n, p, from]) => { const sd = sideId(l, n); return sd ? {x: 0, y: 0, ...scr(edgeT(f, p, from)), txt: endTxt(l, n, sd), key, n, own: sd.own} : null; }).filter(Boolean);
      // two systems close together: one mark between them, its hover naming both sides (two would overlap)
      if(ms.length === 2 && Math.hypot(ms[0].x - ms[1].x, ms[0].y - ms[1].y) < 2 * END_R + 6){   // one line per side; an old single ID said once
        const [A, B] = ms, idOf = (m) => { const sd = sideId(l, m.n); return [sd.sig, sd.type].filter(Boolean).join(' '); };
        const txt = !A.own && !B.own ? `${idOf(A)} (side not known)\n${whName(A.n)} ↔ ${whName(B.n)}`
          : [A, B].map(m => `${whName(m.n)}: ${idOf(m)}${m.own ? '' : ' (side not known)'}`).join('\n');
        ms = [{x: (A.x + B.x) / 2, y: (A.y + B.y) / 2, txt, key, n: null, own: A.own && B.own}];
      }
      for(const q of ms){
        if(q.x < -END_R || q.y < -END_R || q.x > W + END_R || q.y > H + END_R) continue;
        c.setTransform(dpr, 0, 0, dpr, 0, 0);
        c.globalAlpha = 0.92; c.fillStyle = C.bg; c.beginPath(); c.arc(q.x, q.y, END_R, 0, 6.283); c.fill(); c.globalAlpha = 1;
        c.strokeStyle = col; c.lineWidth = 1; c.globalAlpha = 0.6; c.stroke(); c.globalAlpha = 1;
        const k = END_PX / 12; c.setTransform(dpr * k, 0, 0, dpr * k, dpr * (q.x - END_PX / 2), dpr * (q.y - END_PX / 2)); c.fillStyle = col; c.fill(SWIRL);
        P3.ends.push(q);
      }
    }
    c.setTransform(dpr, 0, 0, dpr, 0, 0);
  };
  function endAt(x, y){ let best = null, bd = END_HIT; for(const e of P3.ends){ const d = Math.hypot(e.x - x, e.y - y); if(d <= bd){ bd = d; best = e; } } return best; }
  // the legend gains the marks and the empty-space menu's new items (plan section 9)
  const realLeg = whLegendHtml;
  window.whLegendHtml = function(){
    const h = realLeg(); if(!on()) return h;
    return h.replace('to add a system there.', 'to add a system there, select all or remove all.')
      .replace('thicker for bigger ships.', 'thicker for bigger ships. The small wormhole mark at an end: that side’s signature ID (hover it, or tap it on a phone).');
  };
  // ---- empty space: Select all / Remove all with the verify step (plan P13)
  const realHere = whHereOpen;
  window.whHereOpen = function(x, y){
    realHere(x, y); if(!on()) return;
    const S = whS, m = S.el.querySelector('.wh-hmenu'), n = Object.keys(S.st.sys).length; if(!n) return;
    m.insertAdjacentHTML('afterbegin', `<button type="button" class="wh-mi" data-p3="all">Select all (${n})</button><button type="button" class="wh-mi wh-mdel" data-p3="rmall">Remove all…</button><div class="wh-hr"></div>`);
  };
  function rmAllAsk(m){
    const S = whS, ids = Object.keys(S.st.sys).map(Number), keep = ids.filter(whLocked), go = ids.length - keep.length;
    m.innerHTML = go ? `<div class="wh-mh">Remove all</div><div class="wh-vfy">Remove ${go} system${go === 1 ? '' : 's'} and their connections? ${keep.length ? `${keep.length} locked stay.` : ''}<div><button type="button" data-p3="rmyes">Remove</button><button type="button" data-p3="rmno">Cancel</button></div></div>`
      : '<div class="wh-mh">Remove all</div><div class="wh-vfy">Nothing to remove: every system is locked.</div>';
    const b = m.querySelector('[data-p3="rmno"]'); if(b) b.focus();
  }
  function rmAll(){
    const S = whS, ids = Object.keys(S.st.sys).map(Number), keep = ids.filter(whLocked), G = sigsSt(), E = endsSt();
    for(const id of ids) if(!whLocked(id)){ delete S.st.sys[id]; delete S.st.pos[id]; delete S.mk[id]; delete G.sys[id]; }
    S.st.links = S.st.links.filter(l => S.st.sys[l.a] && S.st.sys[l.b]);
    for(const k of Object.keys(E.links)){ const [a, b] = k.split('-').map(Number); if(!S.st.sys[a] || !S.st.sys[b]) delete E.links[k]; }
    if(S.sel !== null && !S.st.sys[S.sel]) S.sel = null; S.M.group.clear();
    whSave(); whMkSave(); put(SK, G); put(EK, E); whHereClose(); S.pn = {}; S.drawKey = ''; whPaint(true); if(typeof itMapRefresh === 'function') itMapRefresh(true);
    whMsg(`Removed ${ids.length - keep.length} systems; ${keep.length} locked kept.`);
  }
  // ---- Share (plan P14-P18)
  const SHARE_SVG = '<svg width="15" height="15" viewBox="0 0 16 16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="4" cy="8" r="2"/><circle cx="12" cy="3.5" r="2"/><circle cx="12" cy="12.5" r="2"/><path d="M5.8 7l4.4-2.5M5.8 9l4.4 2.5"/></svg>';
  function addShare(){
    const S = whS, ctl = S.el.querySelector('.wh-ctl'); if(!ctl || ctl.querySelector('[data-wh-pop="share"]')) return;
    ctl.querySelector('[data-wh-pop="add"]').insertAdjacentHTML('afterend', `<button type="button" class="it-map-clr wh-tb" data-wh-pop="share" data-p3share aria-expanded="false" title="Share your chain, or import someone's" aria-label="Share">${SHARE_SVG}<span>Share</span></button>`);
    ctl.insertAdjacentHTML('afterend', `<div class="wh-pop" data-pop="share" role="dialog" aria-label="Share your chain" hidden><div class="wh-poph">Share your chain<button type="button" class="x-close" data-wh-popx aria-label="Close" title="Close (Esc)">×</button></div>`
      + `<label class="wh-shs"><input type="checkbox" data-p3="incl"> Include notes and who’s there</label>`
      + `<div class="wh-sub">Export</div><textarea readonly rows="3" data-p3="exp" spellcheck="false" aria-label="Your chain as text"></textarea>`
      + `<div class="wh-shr"><button type="button" data-p3="copy">Copy</button><button type="button" data-p3="link">Copy link</button><span class="wh-shs" data-p3="exps" role="status"></span></div>`
      + `<div class="wh-sub">Import</div><textarea rows="3" data-p3="imp" spellcheck="false" placeholder="Paste someone’s chain, or open their link" aria-label="A chain to import"></textarea>`
      + `<div class="wh-shr"><button type="button" data-p3="import">Import</button><span class="wh-shs" data-p3="imps" role="status"></span></div><div class="wh-pv" data-p3="pv" hidden></div></div>`);
  }
  function exportObj(incl){
    const S = whS, G = sigsSt(), E = endsSt(), ids = Object.keys(S.st.sys).map(Number).sort((a, b) => a - b);
    const sys = ids.map(id => { const s = S.st.sys[id], m = S.mk[id] || {}, o = {id, name: whName(id), statics: s.statics, t: s.t, u: s.u};
      if(s.cls) o.cls = s.cls; if(m.st) o.st = m.st; if(m.tag) o.tag = m.tag; if(incl){ if(s.who) o.who = s.who; if(s.notes) o.notes = s.notes; } return o; });
    const links = S.st.links.slice().sort((a, b) => whLinkKey(a.a, a.b).localeCompare(whLinkKey(b.a, b.b))).map(l => {
      const o = {a: l.a, b: l.b, t: l.t, u: l.u, seen: l.seen, life: l.life, mass: l.mass, size: l.size}; if(l.dr) o.dr = true;
      const e = E.links[whLinkKey(l.a, l.b)];
      if(e){ o.ends = {}; for(const [k, v] of Object.entries(e)) if(v.sig) o.ends[k] = {sig: v.sig, ...(v.type ? {type: v.type} : {})}; }
      else if(l.sig){ o.sig = l.sig; if(l.type) o.type = l.type; }
      return o; });
    const sigs = {}; for(const id of ids) if(G.sys[id]) sigs[id] = {t: G.sys[id].t, rows: G.sys[id].rows.map(r => ({id: r.id, ...(r.sg ? {sg: r.sg} : {}), grp: r.grp, nm: r.nm, pct: r.pct, f: r.f || r.t, t: r.t}))};
    return {tv: 'wormholes', v: 1, made: Date.now(), sys: [], chain: {sys, links, sigs}};
  }
  const b64u = (u8) => btoa(String.fromCharCode(...u8)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  async function deflate(s){ const r = new Blob([s]).stream().pipeThrough(new CompressionStream('deflate-raw')); return new Uint8Array(await new Response(r).arrayBuffer()); }
  function importPlan(text){
    let o; try{ o = JSON.parse(String(text || '').trim()); }catch(e){ return {err: 'That isn’t a chain from this tool (it isn’t JSON).'}; }
    if(!o || o.tv !== 'wormholes') return {err: 'That isn’t a chain from this tool.'};
    if(o.v !== 1) return {err: 'That export is from a newer version of this tool: reload the page and try again.'};
    if(!o.chain) return {err: 'That export holds Intel’s wormhole list: import it in Intel’s Wormholes list.'};
    const S = whS, res = {add: 0, links: 0, upd: 0, keep: 0, sigs: 0, unknown: 0, sys: [], lk: []};
    for(const x of o.chain.sys || []){ if(!x || !Number.isInteger(x.id) || !whKnown(x.id) || whName(x.id).toLowerCase() !== String(x.name || '').toLowerCase()){ res.unknown++; continue; }
      const mine = S.st.sys[x.id]; if(!mine){ res.add++; res.sys.push(x); } else if(x.u > mine.u && (x.statics && x.statics !== mine.statics)){ res.upd++; res.sys.push(x); } else res.keep++; }
    const ok = (id) => S.st.sys[id] || res.sys.some(s => s.id === id);
    for(const l of o.chain.links || []){ if(!ok(l.a) || !ok(l.b)) continue; if(!S.st.links.some(m => whLinkKey(m.a, m.b) === whLinkKey(l.a, l.b))){ res.links++; res.lk.push(l); } }
    for(const [, v] of Object.entries(o.chain.sigs || {})) res.sigs += (v.rows || []).length;
    res.o = o; return res;
  }
  function importApply(r){
    const S = whS, now = Date.now(), G = sigsSt(), E = endsSt();
    for(const x of r.sys){ if(!S.st.sys[x.id]){ S.st.sys[x.id] = {cls: x.cls || null, statics: whStatics(x.statics).ok, who: '', notes: '', t: x.t || now, u: x.u || now, src: 'shared'}; if(x.st || x.tag) S.mk[x.id] = {...(x.st ? {st: x.st} : {}), ...(x.tag ? {tag: whTagClean(x.tag)} : {})}; }
      else { S.st.sys[x.id].statics = whStatics(x.statics).ok; S.st.sys[x.id].u = x.u; } }
    for(const l of r.lk){ const n = {a: l.a, b: l.b, t: l.t || now, u: l.u || now, seen: l.seen || now, sig: l.sig || '', type: l.type || '', life: l.life || '', mass: l.mass || '', size: l.size || ''}; S.st.links.push(n);
      if(l.ends) E.links[whLinkKey(l.a, l.b)] = Object.fromEntries(Object.entries(l.ends).map(([k, v]) => [k, {sig: v.sig, type: v.type || ''}])); }
    for(const [k, v] of Object.entries(r.o.chain.sigs || {})){ const id = Number(k); if(!S.st.sys[id]) continue; const cur = (G.sys[id] && G.sys[id].rows) || [], by = new Map(cur.map(x => [x.id, x]));
      for(const x of v.rows || []){ const m = by.get(x.id), f = Math.min(x.f || x.t, m ? (m.f || m.t) : Infinity); if(!m || x.t > m.t) by.set(x.id, {...x, f}); else m.f = f; } G.sys[id] = {t: Math.max(v.t || 0, G.sys[id] ? G.sys[id].t : 0), rows: [...by.values()].sort((a, b) => b.t - a.t)}; }
    whSave(); whMkSave(); put(SK, G); put(EK, E); S.pn = {}; S.drawKey = ''; whPaint(true); if(typeof itMapRefresh === 'function') itMapRefresh(true);
  }
  function friendChain(){   // a made-up friend's chain: two of yours, three new systems, one newer static, signatures
    const p = picks(), now = Date.now(), o = exportObj(false), keep = new Set([p[1], p[6]]);
    o.chain.sys = o.chain.sys.filter(s => keep.has(s.id)).map(s => s.id === p[6] ? {...s, statics: 'C247', u: now} : s);
    for(const id of [p[8], p[9], p[10]]) o.chain.sys.push({id, name: whName(id), statics: '', t: now - 20 * 60e3, u: now - 20 * 60e3, ...(id === p[9] ? {st: 'danger', tag: 'CAMP'} : {})});
    o.chain.links = [{a: p[6], b: p[8], t: now - 30 * 60e3, u: now - 30 * 60e3, seen: now - 30 * 60e3, life: '', mass: 'reduced', size: 'large', ends: {[p[6]]: {sig: 'WQE-338', type: 'X877'}, [p[8]]: {sig: 'FOP-144', type: 'K162'}}},
      {a: p[8], b: p[9], t: now - 25 * 60e3, u: now - 25 * 60e3, seen: now - 25 * 60e3, life: 'eol', mass: '', size: 'medium'}, {a: p[8], b: p[10], t: now - 20 * 60e3, u: now - 20 * 60e3, seen: now - 20 * 60e3, life: '', mass: '', size: ''}];
    o.chain.sigs = {[p[8]]: {t: now - 22 * 60e3, rows: [{id: 'FOP-144', grp: 'Wormhole', nm: 'Unstable Wormhole', pct: 100, f: now - 40 * 60e3, t: now - 22 * 60e3}, {id: 'GHA-901', grp: 'Data Site', nm: 'Unsecured Frontier Database', pct: 100, f: now - 22 * 60e3, t: now - 22 * 60e3}]}};
    return JSON.stringify(o);
  }
  // ---- events
  function sec(){ const pnl = whS.el.querySelector('#whPnSum'); return pnl && pnl.querySelector('[data-p3sec]'); }
  function refresh(){ whS.pn = {}; whS.drawKey = ''; whPaint(true); }
  function wire(){
    const el = whS.el;
    // every delete asks first (the owner: "any deletions should require verification."): the panel's Remove from the map and the menu's
    // Remove are caught before the page acts; a locked system keeps the page's own refusal (connections: Delete selected, P22)
    el.addEventListener('click', (ev) => {
      if(!on()) return; const b = ev.target.closest('[data-wh-del], [data-wh-m="del"]'); if(!b) return;
      if(b.dataset.whDel){ const n = Number(b.dataset.whDel); if(whLocked(n)) return; ev.stopPropagation(); ev.preventDefault(); P3.confirm = {kind: 'del', n}; refresh(); const y = el.querySelector('#whPnSum [data-p3="cfno"]'); if(y) y.focus(); return; }
      const n = whS.menu; if(n === null || n === undefined || whLocked(n)) return;
      ev.stopPropagation(); ev.preventDefault(); P3.confirm = {kind: 'menu', n};
      b.outerHTML = `<div class="wh-vfy" style="padding:6px 8px; font:12px var(--sans);">Remove ${esc(whName(n))} and its connections?<div style="display:flex; gap:6px; margin-top:6px;"><button type="button" data-p3="cfyes">Remove</button><button type="button" data-p3="cfno">Cancel</button></div></div>`;
      const y = el.querySelector('.wh-smenu [data-p3="cfno"]'); if(y) y.focus();
    }, true);
    el.addEventListener('click', (ev) => {   // a row: click selects it alone; Ctrl/Shift-click or a tap adds or removes it
      if(!on() || ev.target.closest('button, input, select')) return; const r = ev.target.closest('[data-p3row]'); if(r){ rowClick(ev, r.dataset.p3row); return; }
      const c = ev.target.closest('[data-p3cn]'); if(c) cnRowClick(ev, c.dataset.p3cn);
    });
    el.addEventListener('keydown', (ev) => { if(!on() || (ev.key !== ' ' && ev.key !== 'Enter')) return; const r = ev.target.closest && ev.target.closest('[data-p3row], [data-p3cn]'); if(!r || ev.target !== r) return; ev.preventDefault(); if(r.dataset.p3row) rowClick(ev, r.dataset.p3row); else cnRowClick(ev, r.dataset.p3cn); });
    el.addEventListener('change', (ev) => { if(!on() || ev.target.dataset.p3 !== 'cnall') return; const n = whFocus(), sel = cselFor(n);
      if(ev.target.checked) cnRows(n).forEach(r => sel.add(r.key)); else sel.clear(); P3.cedit = null; ev.target.blur(); refresh(); const c = whS.el.querySelector('#whPnSum [data-p3="cnall"]'); if(c) c.focus({preventScroll: true}); });
    el.addEventListener('change', (ev) => { if(!on() || ev.target.dataset.p3 !== 'sgall') return; const n = whFocus(), G = sigsSt(), rows = (G.sys[n] && G.sys[n].rows) || [], sel = selFor(n);
      if(ev.target.checked) rows.forEach(x => sel.add(x.id)); else sel.clear(); P3.edit = null; ev.target.blur(); refresh(); const c = sec() && sec().querySelector('[data-p3="sgall"]'); if(c) c.focus({preventScroll: true}); });   // the panel isn't rewritten under a focused field (LESSON #120)
    el.addEventListener('click', async (ev) => {
      if(!on()) return; const b = ev.target.closest('[data-p3]'); if(!b) return; const k = b.dataset.p3, n = whFocus();
      if(k === 'sec'){ const C = secsSt(); C.sigs = b.getAttribute('aria-expanded') !== 'true'; put(CK, C); refresh(); }   // keeps the Connections sort beside it
      else if(k === 'unfold'){ P3.pasteOpen[n] = true; P3.res = null; refresh(); const t = sec() && sec().querySelector('textarea'); if(t) t.focus(); }
      else if(k === 'fold'){ P3.pasteOpen[n] = false; refresh(); }
      else if(k === 'read'){ const t = sec().querySelector('textarea'); readScan(n, t.value); const keepText = P3.res && P3.res.err ? t.value : ''; refresh(); if(keepText){ const t2 = sec().querySelector('textarea'); t2.value = keepText; } }
      else if(k === 'rm' || k === 'keep'){ const a = P3.ask; readScan(a.n, a.text, k === 'rm' ? 'rm' : 'keep'); refresh(); }
      else if(k === 'undo'){ undo(); refresh(); }
      else if(k === 'sort'){ const so = sortOf(), G = sigsSt(); G.sort = {k: b.dataset.k, d: so.k === b.dataset.k ? -so.d : 1}; put(SK, G); refresh(); }
      else if(k === 'sgcopy'){ const n2 = whFocus(), txt = gameRows(n2, selFor(n2)); try{ await navigator.clipboard.writeText(txt); whMsg(`Copied ${selFor(n2).size} signature${selFor(n2).size === 1 ? '' : 's'} (the game's own format).`); }catch(e){ whMsg('Couldn’t copy: this browser didn’t allow it.'); } }
      else if(k === 'sgedit'){ const sl = selFor(n); P3.edit = sl.size === 1 ? [...sl][0] : '*'; P3.confirm = null; refresh(); const f = sec() && sec().querySelector('[data-p3e]'); if(f) f.focus(); }
      else if(k === 'eno'){ P3.edit = null; refresh(); }
      else if(k === 'esave'){ const G = sigsSt(), rows = (G.sys[n] && G.sys[n].rows) || [], box = b.closest('.wh-sge'), gv = box.querySelector('[data-p3e="grp"]').value;
        if(P3.edit === '*'){ for(const r of rows) if(P3.sel.has(r.id)){ r.grp = gv; if(!gv) r.nm = ''; } }
        else { const r = rows.find(x => x.id === P3.edit); if(r){ const nid = box.querySelector('[data-p3e="id"]').value.trim().toUpperCase().replace(/^([A-Z]{3})(\d)/, '$1-$2');
          if(!/^[A-Z]{3}-\d{3}$/.test(nid) || (nid !== r.id && rows.some(x => x.id === nid))){ whMsg(nid !== r.id && rows.some(x => x.id === nid) ? `${nid} is already in the list.` : 'A signature ID is three letters and three digits (RZL-429).'); return; }
          P3.sel.delete(r.id); r.id = nid; P3.sel.add(nid); r.grp = gv; r.nm = box.querySelector('[data-p3e="nm"]').value.trim().slice(0, 48); } }
        put(SK, G); P3.edit = null; refresh(); }
      else if(k === 'sgdel'){ P3.confirm = {kind: 'sigs', n}; P3.edit = null; refresh(); const y = sec() && sec().querySelector('[data-p3="cfno"]'); if(y) y.focus(); }
      else if(k === 'cnsort'){ const so = cnSortOf(), C = secsSt(); C.cn = {k: b.dataset.k, d: so.k === b.dataset.k ? -so.d : 1}; put(CK, C); refresh(); }
      else if(k === 'cnedit'){ const sl = cselFor(n); P3.cedit = sl.size === 1 ? [...sl][0] : '*'; P3.confirm = null; refresh(); const f = whS.el.querySelector('#whPnSum [data-p3c]'); if(f) f.focus(); }
      else if(k === 'cnno'){ P3.cedit = null; refresh(); }
      else if(k === 'cnsave'){ const box = b.closest('.wh-sge'), v = (f) => { const x = box.querySelector(`[data-p3c="${f}"]`); return x ? (x.type === 'checkbox' ? x.checked : x.value) : undefined; };
        if(P3.cedit === '*'){ for(const l of whS.st.links) if(P3.csel.has(whLinkKey(l.a, l.b))){ if(v('life')) l.life = v('life'); if(v('mass')) l.mass = v('mass'); l.u = Date.now(); } }
        else { const l = whS.st.links.find(x => whLinkKey(x.a, x.b) === P3.cedit); if(l){
          const sg = String(v('sig') || '').trim().toUpperCase().replace(/^([A-Z]{3})(\d)/, '$1-$2'), ty = String(v('type') || '').toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 4);
          if(sg && !/^[A-Z]{3}(-\d{0,3})?$/.test(sg)){ whMsg('A signature ID is three letters and three digits (RZL-429), or its start.'); return; }
          if(ty && !(IT_WH_TYPE[ty] || ty === 'K162')){ whMsg(`“${ty}” isn’t a wormhole type the page knows.`); return; }
          endSet(l, n, 'sig', sg); endSet(l, n, 'type', ty); l.life = v('life') || ''; l.mass = v('mass') || ''; l.size = v('size') || ''; l.dr = !!v('dr'); l.u = Date.now(); } }
        whSave(); P3.cedit = null; whS.drawKey = ''; refresh(); }
      else if(k === 'cndel'){ P3.confirm = {kind: 'cns', n}; P3.cedit = null; refresh(); const y = whS.el.querySelector('#whPnSum .wh-cnw [data-p3="cfno"]'); if(y) y.focus(); }
      else if(k === 'cfno'){ const c = P3.confirm; P3.confirm = null; if(c && c.kind === 'menu'){ whMenuClose(true); return; } refresh(); }
      else if(k === 'cfyes'){ const c = P3.confirm; P3.confirm = null; if(!c) return;
        if(c.kind === 'sigs'){ const G = sigsSt(), gone = [...P3.sel]; if(G.sys[c.n]){ G.sys[c.n].rows = G.sys[c.n].rows.filter(x => !P3.sel.has(x.id)); put(SK, G); } P3.sel.clear(); whMsg(`Deleted ${gone.length} signature${gone.length === 1 ? '' : 's'}: ${gone.join(', ')}.`); refresh(); }
        else if(c.kind === 'cns'){ const ks = new Set(P3.csel), E = endsSt(), names = whS.st.links.filter(l => ks.has(whLinkKey(l.a, l.b))).map(l => whName(l.a === c.n ? l.b : l.a));
          whS.st.links = whS.st.links.filter(l => !ks.has(whLinkKey(l.a, l.b))); for(const k2 of ks) delete E.links[k2]; put(EK, E); P3.csel.clear(); whSave(); whS.drawKey = ''; whMsg(`Deleted ${ks.size} connection${ks.size === 1 ? '' : 's'}: to ${names.join(', ')}.`); refresh(); if(typeof itMapRefresh === 'function') itMapRefresh(true); }
        else if(c.kind === 'del'){ whRemoveAsk(c.n); }
        else if(c.kind === 'menu'){ whMenuClose(true); whRemoveAsk(c.n); } }
      else if(k === 'all'){ whHereClose(); for(const id of Object.keys(whS.st.sys)) whS.M.group.add(Number(id)); whDraw(); }
      else if(k === 'rmall'){ rmAllAsk(el.querySelector('.wh-hmenu')); }
      else if(k === 'rmno'){ whHereClose(); }
      else if(k === 'rmyes'){ rmAll(); }
      else if(k === 'copy' || k === 'link'){
        const ta = el.querySelector('[data-p3="exp"]'), st = el.querySelector('[data-p3="exps"]'); let txt = ta.value;
        if(k === 'link'){ try{ const u = location.origin + location.pathname + '#wh=' + b64u(await deflate(ta.value)); if(u.length > 1800){ st.textContent = `Too long for a link (${u.length} characters): copy the text instead.`; return; } txt = u; }catch(e){ st.textContent = 'This browser can’t make a chain link: copy the text instead.'; return; } }
        try{ await navigator.clipboard.writeText(txt); st.textContent = k === 'link' ? `Link copied (${txt.length} characters).` : 'Copied!'; }catch(e){ st.textContent = 'Press Ctrl+C (⌘C) to copy.'; if(k === 'copy'){ ta.focus(); ta.select(); } }
      }
      else if(k === 'import'){ const r = importPlan(el.querySelector('[data-p3="imp"]').value), pv = el.querySelector('[data-p3="pv"]'), st = el.querySelector('[data-p3="imps"]');
        if(r.err){ st.textContent = r.err; pv.hidden = true; return; } st.textContent = ''; P3.imp = r;
        pv.innerHTML = `${esc(`Adds ${r.add} system${r.add === 1 ? '' : 's'} and ${r.links} connection${r.links === 1 ? '' : 's'} · updates ${r.upd} where theirs is newer · keeps yours for ${r.keep} · ${r.sigs} signatures`)}${r.unknown ? `<br>${esc(`Skipped: ${r.unknown} not a known system`)}` : ''}`
          + '<div class="wh-shr"><button type="button" data-p3="impadd">Add to my map</button><button type="button" data-p3="impno">Cancel</button></div>'; pv.hidden = false; pv.scrollIntoView({block: 'nearest'}); }
      else if(k === 'impadd'){ const r = P3.imp; importApply(r); el.querySelector('[data-p3="pv"]').hidden = true; el.querySelector('[data-p3="imp"]').value = ''; whPopClose(); whMsg(`Added ${r.add} systems and ${r.links} connections; updated ${r.upd}; ${r.sigs} signatures.`); }
      else if(k === 'impno'){ el.querySelector('[data-p3="pv"]').hidden = true; }
    });
    el.addEventListener('change', (ev) => {
      if(!on()) return; const f = ev.target;
      if(f.dataset.p3 === 'lazy'){ const G = sigsSt(); G.lazy = f.checked; put(SK, G); refresh(); }
      if(f.dataset.p3 === 'incl'){ el.querySelector('[data-p3="exp"]').value = JSON.stringify(exportObj(f.checked)); }
    }, true);
    el.addEventListener('click', (ev) => {   // Share opens: the export made now
      const b = ev.target.closest('[data-p3share]'); if(!b || !on()) return;
      setTimeout(() => { const ta = el.querySelector('[data-p3="exp"]'), inc = el.querySelector('[data-p3="incl"]'); if(inc) inc.checked = false; if(ta){ ta.value = JSON.stringify(exportObj(false)); } }, 0);
    });
    // press and hold on empty space (a phone): the same menu (plan P13)
    const cv = el.querySelector('.wh-box canvas'); let lp = 0, at = null;
    cv.addEventListener('pointerdown', (ev) => { if(!on() || ev.pointerType === 'mouse' || whS.M.selMode) return; const r = cv.getBoundingClientRect(), q = {x: ev.clientX - r.left, y: ev.clientY - r.top};
      if(whHit(whToWorld(q.x, q.y)) !== null) return; at = q; clearTimeout(lp); lp = setTimeout(() => { if(!at) return; whS.M.drag = null; whS.M.ptrs.clear(); whHereOpen(at.x, at.y); at = null; }, 550); });
    cv.addEventListener('pointermove', (ev) => { if(!at) return; const r = cv.getBoundingClientRect(); if(Math.hypot(ev.clientX - r.left - at.x, ev.clientY - r.top - at.y) > 6){ at = null; clearTimeout(lp); } });
    cv.addEventListener('pointerup', () => { at = null; clearTimeout(lp); });
    // the ends' wormhole marks: the ID in the mark's hover (a mouse, when no system is under the pointer), a tap puts it in the message line
    const cpt = (ev) => { const r = cv.getBoundingClientRect(); return {x: ev.clientX - r.left, y: ev.clientY - r.top}; };
    let endHov = null, dn = null;
    cv.addEventListener('pointermove', (ev) => {
      if(!on() || ev.buttons || ev.pointerType !== 'mouse') return; const q = cpt(ev);
      if(whHit(whToWorld(q.x, q.y)) !== null){ endHov = null; return; }
      const e = endAt(q.x, q.y); if(e === endHov && (!e || cv.title === e.txt)) return; endHov = e;
      cv.title = e ? e.txt : ''; cv.style.cursor = e ? 'help' : '';
    });
    cv.addEventListener('pointerdown', (ev) => { dn = cpt(ev); });
    cv.addEventListener('click', (ev) => {
      if(!on() || !dn) return; const q = cpt(ev), far = Math.hypot(q.x - dn.x, q.y - dn.y) > 6; dn = null; if(far || whHit(whToWorld(q.x, q.y)) !== null) return;
      const e = endAt(q.x, q.y); if(e) whMsg(e.txt.split('\n').join(' · ') + '.');
    });
  }
  // ---- info text (plan section 9)
  const INFO_NEW = [
    "Your wormhole chain, drawn as you jump: each wormhole system you enter is added with the connection you came through, from your Local log or from EVE with Use my game location on. A change of system that lands you docked (a jump clone, a pod death) adds no connection.",
    "[Moving around] Drag to pan, the wheel or a pinch to zoom, drag a system to move it. Select (or Shift) drags a box around a group to move together; right-click empty space for Select all. The overview in the corner shows where everything is. ⚙ → Rearrange as a tree puts them back; locked ones stay.",
    "[Focus and adding] Click a system for the System panel (its button, top left): class, effect, statics, notes, connections, signatures. Right-click it (press and hold on a phone) for its menu: status, tag, Lock, Copy the name, Remove. + Add adds a system or connection by hand; right-click empty space adds one there.",
    "[Connections] Each side of a hole has its own signature ID: hover the mark at its end, or see that side's list.",
    "[Signatures] Paste the Probe Scanner's list (Ctrl+A, Ctrl+C) for the system in focus: signatures and anomalies. Colours follow the game's signal. Select rows (Ctrl-click adds) to copy, edit or delete. With Lazy update on, a paste is the whole list: signatures missing from it go, after you confirm. Undo takes back the last paste.",
    "[Sharing] Share copies your chain as text or a link: positions and locks stay with you, notes and who's there only if ticked. Import shows what it adds first; the newer edit wins and nothing of yours is removed.",
    "[Kept] In this browser only, until you remove it: nothing expires. Lock a system (your home, say) so it can't be moved or removed; Remove all leaves locked ones. In a wormhole, Intel counts jumps from where you came into the chain."];
  const INFO_OLD = CARD_INFO.whmap.slice();
  // ---- the MOCKUP bar
  function bar(){
    const b = document.createElement('div'); b.id = 'p3Bar'; b.setAttribute('role', 'toolbar'); b.setAttribute('aria-label', 'Mockup controls');
    b.innerHTML = '<b>MOCKUP</b><button type="button" data-m="today">Today</button><button type="button" data-m="proposed">Proposed</button>'
      + '<button type="button" data-m="s1">Scan 1</button><button type="button" data-m="s2">Scan 2 (sites done)</button><button type="button" data-m="s3">Filtered scan</button>'
      + '<button type="button" data-m="friend">Friend’s chain</button><button type="button" data-m="reset">Reset</button><button type="button" class="p3-fold" data-m="fold" aria-label="Fold the mockup bar">–</button>';
    document.body.appendChild(b);
    b.addEventListener('click', (ev) => { const x = ev.target.closest('[data-m]'); if(!x) return; const m = x.dataset.m;
      if(m === 'fold'){ b.classList.toggle('fold'); x.textContent = b.classList.contains('fold') ? '+' : '–'; return; }
      if(m === 'today' || m === 'proposed'){ setMode(m); return; }
      if(m === 'reset'){ for(const k of ['tvWhChain', 'tvWhMarks', SK, EK, CK, 'tvWhPanels']) localStorage.removeItem(k); location.reload(); return; }
      if(m === 'friend'){ setMode('proposed'); whPop('share'); setTimeout(() => { const t = whS.el.querySelector('[data-p3="imp"]'); t.value = friendChain(); t.focus(); }, 30); return; }
      setMode('proposed'); openSys(picks()[1]);
      P3.pasteOpen[picks()[1]] = true; P3.res = null; refresh();
      const t = sec() && sec().querySelector('textarea'); if(t){ t.value = m === 's1' ? scanA() : m === 's2' ? scanB() : scanC(); t.focus(); }
    });
    paintBar();
  }
  function paintBar(){ const b = document.getElementById('p3Bar'); if(!b) return; for(const x of b.querySelectorAll('[data-m="today"],[data-m="proposed"]')) x.setAttribute('aria-pressed', String(x.dataset.m === mode)); }
  function openSys(id){ if(whS.open !== 'sum') whPnSet('sum', true); whSelect(id); }
  function setMode(m){
    mode = m; document.body.classList.toggle('p3', on());
    CARD_INFO.whmap.splice(0, CARD_INFO.whmap.length, ...(on() ? INFO_NEW : INFO_OLD));
    const sb = whS.el.querySelector('[data-p3share]'); if(sb) sb.hidden = !on();
    P3.res = null; P3.ask = null; refresh(); paintBar();
  }
  window.__p3 = P3;   // for test_p3.py: the end marks drawn last (P3.ends)
  function boot(){
    const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
    seed(); document.getElementById('tabBtnWh').click(); whMake(); whPaint(true);
    if(!whS.el){ setTimeout(boot, 200); return; }
    addShare(); wire(); bar(); setMode('proposed');
    if(whS.open !== 'sum') whPnSet('sum', true); whSelect(picks()[1]);
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else setTimeout(boot, 0);
})();
