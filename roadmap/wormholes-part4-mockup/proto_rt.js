// MOCKUP prototype: Wormholes tab part 4 (Project doc claude/roadmap/wormholes-part4-plan.md), on the real page (main 995f6a0).
// Shortcuts the build must not copy: function wraps by name (whRailHtml, whPnRead, whPanels, whSumHtml, whMenuHtml, whMenuAct, whLThsHtml,
// whScanApply, whSeen, itWhByTxt, itWhRowsHtml, itSettingsHtml, itMapWh), two hooks patched into whDraw by build_rt.py, the route search as
// a copy of itRpUpdate's order (the build shares one search, plan R1), jump bridges left out of the mockup's search (none in the mock data),
// the auto-add switch in memory (the build: a field of Intel's settings). Effects: MOCK_EFF from gen_data_rt.py (CCP's beacons via pyfa).
(function(){
  'use strict';
  const RT = window.RT = {from: null, key: '', res: null, jw: true, msg: '', hov: null};
  const css = `
  .rt-top{display:flex; flex-wrap:wrap; align-items:center; gap:6px 10px; margin:0 0 6px;} .rt-top button{min-height:30px; padding:0 9px; font-size:12px;}
  .rt-short{margin-left:auto; display:flex; align-items:center; gap:5px; font-size:12px; color:var(--text);}
  .rt-ty{display:flex; gap:6px; margin:0 0 8px;} .rt-ty input{flex:1; min-width:0;}
  .rt-list{display:flex; flex-direction:column; gap:2px; position:relative;}
  .rt-row{padding:5px 6px; border-radius:4px; background:var(--panel-2);}
  .rt-l1{display:flex; align-items:center; gap:6px; min-height:24px; font-size:12px;} .rt-l1 .wh-n{font-size:12px;}
  .rt-sec{font:600 11px var(--mono, monospace); min-width:26px;}
  .rt-kind{color:var(--text-dim); font-size:11px;} .rt-w{font-size:11px;}
  .rt-n{margin-left:auto; color:var(--heading); font-variant-numeric:tabular-nums;}
  button.rt-rm{min-height:24px; width:26px; padding:0; display:inline-flex; align-items:center; justify-content:center; font-size:14px;}
  .rt-strip{display:flex; flex-wrap:wrap; gap:2px; margin:4px 0 1px; touch-action:pan-y;}
  button.rt-q{min-height:0; width:10px; height:10px; padding:0; margin:0; border:0; border-radius:2px; background:currentColor; cursor:default; box-sizing:border-box;}
  button.rt-q.j{color:var(--it-wh);} button.rt-q.hole{border-radius:50%;}   /* reached through a wormhole: round (not colour alone); J-space in the wormhole colour */
  button.rt-q.fl{box-shadow:0 2px 0 var(--amber);}
  .rt-strip.hov button.rt-q:not(.on){opacity:.3;} button.rt-q:focus-visible{outline:2px solid var(--cyan); outline-offset:1px;}
  .rt-tip{position:absolute; z-index:5; max-width:300px; padding:5px 8px; border:1px solid var(--line); border-radius:4px; background:#0d1216; color:var(--text); font-size:12px; line-height:1.35; pointer-events:none; box-shadow:0 4px 12px rgba(0,0,0,.5);}
  @media (max-width:599px){ .rt-l1{flex-wrap:wrap;} .rt-kind{flex-basis:100%; order:9;} .rt-short{margin-left:0;} .rt-strip{min-height:44px; align-content:center; gap:3px;} button.rt-q{width:14px; height:14px;} .rt-top button, .rt-short, button.rt-rm{min-height:44px; width:44px;} .rt-top button{width:auto;} }
  .rt-eff{margin:2px 0 6px 0; padding:0; list-style:none;} .rt-eff li{font-size:12px; color:var(--text-dim); line-height:1.4;} .rt-eff b{color:var(--text); font-weight:600;}
  #rtBar{position:fixed; z-index:99999; left:50%; transform:translateX(-50%); top:8px; display:flex; flex-wrap:wrap; gap:6px; align-items:center; max-width:calc(100vw - 24px); box-sizing:border-box;
    padding:8px 10px; border:1px dashed var(--amber); border-radius:6px; background:#12171c; color:var(--text); font:12px var(--sans); box-shadow:0 6px 20px rgba(0,0,0,.6);}
  #rtBar b{color:var(--amber); letter-spacing:.5px;} #rtBar button{min-height:28px; padding:0 9px; font-size:12px;}
  #rtBar.fold > :not(.rt-fold){display:none;} #rtBar.fold{left:auto; right:8px; transform:none;} @media (max-width:599px){ #rtBar{left:8px; right:8px; transform:none;} #rtBar button{min-height:44px;} }
  `;
  const stl = document.createElement('style'); stl.textContent = css; document.head.appendChild(stl);

  // ---- hole effects (plan section 5): CCP's numbers for the system's effect at its class
  function effLines(n){ if(!whIsJ(n)) return []; const T = whTable(), i = T.at.get(n); if(i === undefined) return []; return ((MOCK_EFF[T.eff[i]] || {})[T.cls[i]]) || []; }
  function effTxt(n){ const e = whEff(n); return e ? `${e}: ` + effLines(n).map(([a, b]) => `${a} ${b}`).join(' · ') : ''; }
  function clsEff(n){ const e = whEff(n); return `${whClsName(whCls(n))}${e ? ' · ' + e : ''}`; }
  window.RTeff = {effLines, effTxt};
  const oSum = whSumHtml;
  whSumHtml = function(n){
    const h = oSum(n); if(!whIsJ(n) || !whEff(n)) return h;
    const li = effLines(n).map(([a, b]) => `<li><b>${escapeHtml(a)}</b> ${escapeHtml(b)}</li>`).join('');
    return h.replace(/<div class="wh-kv"><span>Effect<\/span><b>([^<]*)<\/b><\/div>/, (m) => `${m}<ul class="rt-eff" data-rt-eff aria-label="${escapeHtml('What ' + whEff(n) + ' changes here')}">${li}</ul>`);
  };

  // ---- Routes (plan section 2): one search over the stargates and your chain's connections
  function graph(){
    const T = itMapTable(), g = itGraphGet(), n = T.n, st = whS.st, J = Object.keys(st.sys).map(Number).filter(whIsJ);
    const jx = new Map(J.map((id, k) => [id, n + k])), idx = (id) => whIsJ(id) ? jx.get(id) : g.at.get(id), idOf = (x) => x < n ? g.ids[x] : J[x - n];
    const hole = new Map();
    for(const l of st.links){ const a = idx(l.a), b = idx(l.b); if(a === undefined || b === undefined) continue;
      if(!hole.has(a)) hole.set(a, []); if(!hole.has(b)) hole.set(b, []); hole.get(a).push([b, l]); hole.get(b).push([a, l]); }
    return {T, g, n, N: n + J.length, idx, idOf, hole};
  }
  function search(G, src, short){
    const s0 = itRpSet(), s = short ? {...s0, pref: 'Shorter'} : s0, flags = itRpFlags(), pen = s.pref === 'Shorter' ? 0 : s.pen, p = Math.exp(0.15 * pen), N = G.N;
    const f = new Int32Array(N).fill(1 << 30), c = new Float64Array(N).fill(Infinity), len = new Int32Array(N).fill(-1), par = new Int32Array(N).fill(-1), via = new Array(N), done = new Uint8Array(N);
    f[src] = 0; c[src] = 0; len[src] = 0;
    const near = (a, b) => Math.abs(a - b) <= 1e-9 * Math.max(1, Math.abs(a)), less = (a, b) => f[a] < f[b] || (f[a] === f[b] && (near(c[a], c[b]) ? len[a] < len[b] : c[a] < c[b]));
    const h = [src], up = (k) => { while(k > 0){ const q = (k - 1) >> 1; if(!less(h[k], h[q])) break; [h[k], h[q]] = [h[q], h[k]]; k = q; } };
    const down = (k) => { for(;;){ const l = 2 * k + 1, r = l + 1; let m = k; if(l < h.length && less(h[l], h[m])) m = l; if(r < h.length && less(h[r], h[m])) m = r; if(m === k) break; [h[k], h[m]] = [h[m], h[k]]; k = m; } };
    while(h.length){
      const x = h[0], last = h.pop(); if(h.length){ h[0] = last; down(0); }
      if(done[x]) continue; done[x] = 1;
      const fx = f[x] + (x !== src && x < G.n && flags.has(x) ? 1 : 0), nb = (x < G.n ? G.T.adj[x].map(y => [y, null]) : []).concat(G.hole.get(x) || []);
      for(const [y, l] of nb){
        if(done[y]) continue;
        const cy = c[x] + (y < G.n ? itRpCost(G.T, y, s.pref, p) : s.pref === 'Shorter' ? 1 : 2 * p), ly = len[x] + 1;   // R2: into J-space costs as into nullsec
        if(fx < f[y] || (fx === f[y] && (near(cy, c[y]) ? ly < len[y] : cy < c[y]))){ f[y] = fx; c[y] = cy; len[y] = ly; par[y] = x; via[y] = l; h.push(y); up(h.length - 1); }
      }
    }
    return {f, c, len, par, via, flags, s};
  }
  function best(G, R, pick){ let b = -1; for(let x = 0; x < G.n; x++){ if(R.len[x] < 0 || !pick(x)) continue; if(b < 0 || R.f[x] < R.f[b] || (R.f[x] === R.f[b] && (R.c[x] < R.c[b] || (R.c[x] === R.c[b] && R.len[x] < R.len[b])))) b = x; } return b; }
  function homeSys(){ for(const id of Object.keys(whS.st.sys)) if(whMk(Number(id)).st === 'home') return Number(id); return null; }
  // pinned routes (the owner 2026-11-20: "we need to be able to pin multiple systems that the page will automatically calculate the route to each
  // time we navigate another system/wormhole"): kept in this browser (mockup: localStorage 'tvWhRoutes', v 1), as pinned, separate from Intel's
  // map pins; the quick rows (Home, nearest highsec, nearest lowsec) are always there. One search from where you are serves every row.
  const RK = 'tvWhRoutes';
  function rRead(){ try{ const o = JSON.parse(localStorage.getItem(RK) || 'null'); if(o && o.v === 1 && Array.isArray(o.pins)) return {pins: o.pins.filter(Number.isFinite).slice(0, 30), short: !!o.short}; }catch(e){ } return {pins: [], short: false}; }
  function rSave(){ try{ localStorage.setItem(RK, JSON.stringify({v: 1, pins: RT.pins, short: RT.short})); }catch(e){ } }
  Object.assign(RT, rRead());
  function rPin(id){ id = Number(id); const k = RT.pins.indexOf(id); if(k >= 0) RT.pins.splice(k, 1); else RT.pins.push(id); rSave(); RT.key = ''; }
  window.RTpin = rPin;
  function rows(){
    const S = whS, from = RT.from !== null ? RT.from : S.last; if(from === null || !S.st.sys[from] && !itGraphGet().at.has(from)) return {err: 'You aren’t on the map yet: jump into a wormhole or turn on location.'};
    const flags = itRpFlags(), set = itRpSet();
    const key = JSON.stringify([from, RT.pins, RT.short, S.st.links.map(l => whLinkKey(l.a, l.b) + l.life + l.mass + l.size + JSON.stringify(whEnd(l, l.a)) + JSON.stringify(whEnd(l, l.b))), set, [...flags.keys()], homeSys()]);
    if(key === RT.key && RT.res) return RT.res;
    const G = graph(), src = G.idx(from); if(src === undefined) return {err: 'Where you are isn’t on the map.'};
    const R = search(G, src, RT.short), out = [];
    const mk = (kind, t, id) => {
      if(t === null || t === undefined || R.len[t] < 0) return {kind, id, none: true};
      const path = []; for(let x = t; x >= 0; x = R.par[x]){ path.push(x); if(x === src) break; } path.reverse();
      const hops = []; for(let k = 1; k < path.length; k++){ const l = R.via[path[k]], a = G.idOf(path[k - 1]), b = G.idOf(path[k]); hops.push({a, b, l: l || null, flag: path[k] < G.n && k < path.length - 1 && R.flags.has(path[k]) ? R.flags.get(path[k]) : null}); }
      return {kind, id: G.idOf(t), hops, holes: hops.filter(h => h.l).length, warn: hops.filter(h => h.flag).length};
    };
    const h = homeSys(); if(h !== null && h !== from) out.push(mk('home', G.idx(h)));
    const bh = best(G, R, (x) => itRpBand(G.T, x) === 2), bl = best(G, R, (x) => itRpBand(G.T, x) === 1);
    if(bh !== src) out.push(mk('hs', bh < 0 ? null : bh)); if(bl !== src) out.push(mk('ls', bl < 0 ? null : bl));   // no quick row for where you already are
    for(const id of RT.pins) out.push(Object.assign(mk('pin', G.idx(id), id), {pin: id}));
    RT.key = key; RT.res = {from, out, set}; whS.drawKey = '';
    return RT.res;
  }
  window.RTroute = () => { RT.key = ''; return rows(); };
  const LIFE = {eol: 'end of life', lt1h: 'under 1 h left'}, MASS = {reduced: 'reduced mass', critical: 'critical mass'}, SIZE = {small: 'small ships only', medium: 'up to cruisers / medium'};
  function stepWarn(l){ return [LIFE[l.life], MASS[l.mass], SIZE[l.size]].filter(Boolean); }
  function secTxt(id){ if(whIsJ(id)) return whClsName(whCls(id)); const v = whSec(id); return v === null ? '' : itMapSecText(v); }
  function secHtml(id){ if(whIsJ(id)) return whTagHtml(id); const k = whSecKey(id); return `<span class="rt-sec it-sn s${Number(k)}">${escapeHtml(secTxt(id))}</span>`; }
  function hopTip(h){
    const where = `${secTxt(h.b)} ${whName(h.b)}${whPlace(h.b) ? ' · ' + whPlace(h.b) : ''}${whIsJ(h.b) && whEff(h.b) ? ' · ' + whEff(h.b) : ''}`;
    if(!h.l) return where + (h.flag ? ` · ⚠ ${h.flag.join(', ')}` : '');
    const e = whEnd(h.l, h.a), id = e && e.sig ? ` · ${e.sig}${e.type ? ` (${e.type})` : ''}` : '';   // the owner: "sig id is useful if it was recorded but not required" (no "ID not known")
    return `${whName(h.a)} → ${whName(h.b)}${id}${stepWarn(h.l).map(w => ' · ' + w).join('')} · ${where}`;
  }
  function stripHtml(r){
    return `<div class="rt-strip" role="list" aria-label="${escapeHtml(`${r.hops.length} jumps to ${whName(r.id)}`)}">` + r.hops.map((h, i) => {
      const j = whIsJ(h.b), k = j ? null : whSecKey(h.b), cls = `rt-q${j ? ' j' : ' it-sn s' + Number(k)}${h.l ? ' hole' : ''}${h.flag ? ' fl' : ''}`;
      return `<button type="button" class="${escapeHtml(cls)}" role="listitem" data-rt-q="${i}" aria-label="${escapeHtml(hopTip(h))}"></button>`; }).join('') + '</div>';
  }
  const KIND = {home: 'Home', hs: 'nearest highsec', ls: 'nearest lowsec'};
  function rowHtml(r, k){
    const name = r.id !== undefined && r.id !== null ? ((whS.st.sys[r.id] ? `<button type="button" class="wh-n sm" data-wh-sel="${Number(r.id)}">${whNameHtml(r.id)}</button>` : `<b>${whNameHtml(r.id)}</b>`)) : '';
    const tag = r.kind !== 'pin' ? `<span class="rt-kind">${escapeHtml(KIND[r.kind])}</span>` : '';
    const rm = r.kind === 'pin' ? `<button type="button" class="rt-rm" data-rt-rm="${Number(r.pin)}" aria-label="${escapeHtml('Unpin ' + whName(r.pin))}" title="Unpin">×</button>` : '';
    if(r.none) return `<div class="rt-row" data-rt-row="${k}"><div class="rt-l1">${r.id ? secHtml(r.id) : ''}${name || `<span class="wh-note">${escapeHtml(KIND[r.kind] || '')}</span>`}${tag}<span class="rt-n wh-note">no route</span>${rm}</div></div>`;
    return `<div class="rt-row" data-rt-row="${k}"><div class="rt-l1">${secHtml(r.id)}${name}${tag}${r.warn ? `<span class="rt-w it-warn" title="${escapeHtml(`Passes ${r.warn} flagged system${r.warn === 1 ? '' : 's'}`)}">⚠${r.warn}</span>` : ''}<b class="rt-n" title="${escapeHtml(`${r.hops.length} jumps${r.holes ? `, ${r.holes} by wormhole` : ''}`)}">${r.hops.length}</b>`
      + `${rm}</div>${stripHtml(r)}</div>`;
  }
  function rtHtml(){
    const res = rows(), me = whS.last, s = itRpSet();
    let o = `<div class="rt-top"><span class="wh-note">From ${res.from !== undefined && res.from !== null ? whNameHtml(res.from) : 'not known'}${res.from === me ? ' (you)' : ''}</span>`
      + (RT.from !== null && RT.from !== me ? `<button type="button" data-rt-me>From where you are</button>` : '')
      + `<label class="rt-short" title="On: the fewest jumps for every row. Off: your route preference in Intel ⚙ → Routes."><input type="checkbox" data-rt-short${RT.short ? ' checked' : ''}> Shortest</label></div>`
      + `<form class="rt-ty" data-rt-form autocomplete="off"><input type="text" data-rt-typed value="" placeholder="Pin a system, e.g. Jita or J123456" aria-label="Pin a system" maxlength="40" spellcheck="false"><button type="submit">Pin</button></form>`;
    if(res.err) return o + `<div class="wh-note" role="status">${escapeHtml(res.err)}</div>`;
    if(RT.msg) o += `<div class="wh-note" role="status">${escapeHtml(RT.msg)}</div>`;
    o += `<div class="rt-list" data-rt-list>${res.out.map(rowHtml).join('')}</div><div class="rt-tip" data-rt-tip hidden></div>`;
    if(!RT.pins.length) o += '<div class="wh-note">Pin systems here, or right-click a system on the map → Pin route. Each route is worked out again every time you move.</div>';
    return o + `<div class="wh-note" data-rt-set>${escapeHtml(`${RT.short ? 'Shortest' : IT_RP_PREF_NAME[s.pref]} · ${avoidTxt(s)} · change in Intel ⚙ → Routes`)}</div>`;
  }
  function avoidTxt(s){ const a = [['camp', 'camps'], ['bub', 'bubbles'], ['host', 'hostiles'], ['kill', 'kills'], ['mine', 'your avoid list']].filter(([k]) => s[k]).map(([, w]) => w); return a.length ? `avoiding ${a.join(', ')}` : 'avoiding nothing'; }
  // the rail's second button and its panel (R7): a route icon of our own (three stops joined by a path)
  const RT_ICON = '<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="4" cy="4" r="2"/><circle cx="14" cy="9" r="2"/><circle cx="5" cy="14.5" r="2"/><path d="M6 4.6c4 .4 6 1.6 6.4 3M12.3 10.6c-1.4 2.3-3.4 3.4-5.4 3.8"/></svg>';
  const oRail = whRailHtml;
  whRailHtml = function(){
    return oRail().replace('</button></div>', `</button><button type="button" data-wh-rp="rt" aria-controls="whPnRt" aria-pressed="false" title="Routes (press to show the panel)" aria-label="Routes (press to show the panel)">${RT_ICON}</button></div>`)
      + '<section class="wh-pnl" id="whPnRt" aria-label="Routes" hidden><h3>Routes</h3><div class="wh-pnb" data-pnb="rt"></div></section>';
  };
  const oPnRead = whPnRead;
  whPnRead = function(){ try{ const o = JSON.parse(localStorage.getItem(WH_PN_KEY) || 'null'); if(o && o.v === 1 && o.open === 'rt') return 'rt'; }catch(e){ } return oPnRead(); };
  const oPanels = whPanels;
  whPanels = function(){
    oPanels();
    const S = whS; if(!S || !S.el) return;
    const has = Object.keys(S.st.sys).length > 0, on = has && S.open === 'rt', pnl = S.el.querySelector('#whPnRt'), btn = S.el.querySelector('[data-wh-rp="rt"]'); if(!pnl || !btn) return;
    if(pnl.hidden === on) pnl.hidden = !on;
    if(btn.getAttribute('aria-pressed') !== String(on)) btn.setAttribute('aria-pressed', String(on));
    if(!on) return;
    const b = pnl.querySelector('[data-pnb="rt"]'), html = rtHtml();
    if(S.pn.rt !== html && !(b.contains(document.activeElement) && document.activeElement.matches(WH_TYPING))){ S.pn.rt = html; b.innerHTML = html; }
  };
  const repaint = () => { RT.key = ''; whS.pn = {}; whS.drawKey = ''; whPaint(true); };
  function tipShow(q){
    const row = q.closest('.rt-row'), r = RT.res && RT.res.out[Number(row.dataset.rtRow)], tip = document.querySelector('#whPnRt [data-rt-tip]'); if(!r || !tip) return;
    const st = q.parentElement; st.classList.add('hov'); for(const x of st.children) x.classList.toggle('on', x === q);
    tip.textContent = hopTip(r.hops[Number(q.dataset.rtQ)]); tip.hidden = false;
    const pb = tip.offsetParent.getBoundingClientRect(), qb = q.getBoundingClientRect();
    tip.style.top = `${qb.bottom - pb.top + tip.offsetParent.scrollTop + 4}px`; tip.style.left = `${Math.max(4, Math.min(qb.left - pb.left - 8, pb.width - tip.offsetWidth - 4))}px`;
    RT.hov = {row: Number(row.dataset.rtRow), q: Number(q.dataset.rtQ)}; whS.drawKey = ''; whPaint(true);
  }
  function tipHide(){ const tip = document.querySelector('#whPnRt [data-rt-tip]'); if(tip) tip.hidden = true; for(const st of document.querySelectorAll('#whPnRt .rt-strip.hov')){ st.classList.remove('hov'); for(const x of st.children) x.classList.remove('on'); } if(RT.hov){ RT.hov = null; whS.drawKey = ''; whPaint(true); } }
  document.addEventListener('pointerover', (e) => { const q = e.target.closest && e.target.closest('#whPnRt .rt-q'); if(q && e.pointerType !== 'touch') tipShow(q); });
  document.addEventListener('pointerout', (e) => { const q = e.target.closest && e.target.closest('#whPnRt .rt-q'); if(q && e.pointerType !== 'touch' && !(e.relatedTarget && e.relatedTarget.closest && e.relatedTarget.closest('#whPnRt .rt-q'))) tipHide(); });
  document.addEventListener('pointermove', (e) => { if(e.pointerType !== 'touch') return; const st = e.target.closest && e.target.closest('#whPnRt .rt-strip'); if(!st) return; const q = document.elementFromPoint(e.clientX, e.clientY); if(q && q.classList && q.classList.contains('rt-q') && !q.classList.contains('on')) tipShow(q); });
  document.addEventListener('focusin', (e) => { const q = e.target.closest && e.target.closest('#whPnRt .rt-q'); if(q) tipShow(q); });
  document.addEventListener('click', (e) => {
    const q = e.target.closest && e.target.closest('#whPnRt .rt-q'); if(q){ if(q.classList.contains('on') && !document.querySelector('#whPnRt [data-rt-tip]').hidden && e.pointerType === 'touch') tipHide(); else tipShow(q); return; }
    const t = e.target.closest && e.target.closest('#whPnRt button'); if(!t){ return; }
    if(t.dataset.rtRm){ rPin(t.dataset.rtRm); RT.msg = ''; repaint(); return; }
    if('rtMe' in t.dataset){ RT.from = null; repaint(); }
  });
  document.addEventListener('change', (e) => { if(e.target.matches && e.target.matches('[data-rt-short]')){ RT.short = e.target.checked; rSave(); repaint(); } });
  document.addEventListener('submit', (e) => {
    const f = e.target.closest && e.target.closest('[data-rt-form]'); if(!f) return; e.preventDefault();
    const v = f.querySelector('[data-rt-typed]').value.trim(), id = whIdOf(v);
    if(!id){ RT.msg = `“${v}” isn’t a system the page knows.`; repaint(); return; }
    if(!RT.pins.includes(id)) rPin(id); RT.msg = ''; f.querySelector('[data-rt-typed]').value = ''; repaint();
  });
  // the menu: Pin route / Unpin route, and Routes from here (R3)
  const oMenu = whMenuHtml;
  whMenuHtml = function(n){ return oMenu(n).replace('<button type="button" class="wh-mi" role="menuitem" data-wh-m="copy">', `<button type="button" class="wh-mi" role="menuitem" data-wh-m="pin">${RT.pins.includes(Number(n)) ? 'Unpin route' : 'Pin route'}</button><button type="button" class="wh-mi" role="menuitem" data-wh-m="route">Routes from here</button><button type="button" class="wh-mi" role="menuitem" data-wh-m="copy">`); };
  const oAct = whMenuAct;
  whMenuAct = function(act){
    if(act === 'route'){ const n = whS.menu; whMenuClose(false); RT.from = n; whPnSet('rt'); repaint(); return; }
    if(act === 'pin'){ const n = whS.menu; whMenuClose(false); rPin(n); whPnSet('rt'); repaint(); return; }
    return oAct(act);
  };
  // on the chain map (R6): while a square is hovered, that row's hole steps glow and its exit carries the pill; nothing drawn otherwise
  function hovRow(){ return whS && whS.open === 'rt' && RT.hov && RT.res && RT.res.out && RT.res.out[RT.hov.row]; }
  window.__RTglow = function(c, ctr, C){
    const r = hovRow(); if(!r || r.none) return; const M = whS.M;
    c.save(); c.strokeStyle = C.lo; c.globalAlpha = 0.35; c.lineWidth = 10; c.lineCap = 'round';
    for(const h of r.hops){ if(!h.l || !M.P.has(h.a) || !M.P.has(h.b)) continue; const p = ctr(h.a), q = ctr(h.b); c.beginPath(); c.moveTo(p.x, p.y);
      if(Math.abs(q.y - p.y) > Math.abs(q.x - p.x)) c.bezierCurveTo(p.x, (p.y + q.y) / 2, q.x, (p.y + q.y) / 2, q.x, q.y); else c.bezierCurveTo((p.x + q.x) / 2, p.y, (p.x + q.x) / 2, q.y, q.x, q.y); c.stroke(); }
    c.restore();
  };
  window.__RTover = function(c, C, font){
    const r = hovRow(); if(!r || r.none) return; const M = whS.M;
    c.save(); c.strokeStyle = C.lo; c.lineWidth = 1.6;
    const on = new Set([RT.res.from, ...r.hops.map(h => h.b)]);
    for(const id of on){ const p = M.P.get(id); if(!p) continue; c.beginPath(); c.roundRect(p.x - 10, p.y - 10, WH_NW + 20, WH_NH + 20, 9); c.stroke(); }
    const last = [...r.hops].reverse().find(h => h.l), exit = last && !whIsJ(last.b) ? last.b : null, p = exit !== null ? M.P.get(exit) : null, rest = r.hops.length - (r.hops.indexOf(last) + 1);
    if(p && rest > 0){ const t = `EXIT · then ${rest} j to ${whName(r.id)}`; c.font = `700 10px ${font}`; const w = c.measureText(t).width + 12, x = p.x + WH_NW + 16, y = p.y + WH_NH / 2 - 8;
      c.globalAlpha = 0.18; c.fillStyle = C.lo; c.beginPath(); c.roundRect(x, y, w, 16, 3); c.fill(); c.globalAlpha = 1; c.fillStyle = C.lo; c.fillText(t, x + 6, y + 11.5); }
    c.restore();
  };

  // ---- Signatures sorted by type (plan section 3): unscanned first, then by group, then the latest paste's order
  const ORDER = ['Wormhole', 'Gas Site', 'Data Site', 'Relic Site', 'Ore Site', 'Combat Site'];   // Q5, the owner in game 2026-11-20: "unscanned, wormhole, gas site, data site, relic site, asteroid belt, combat site, then the rest for now"; any other group after these, alphabetical
  WH_SG_SORTS.push('ty');
  WH_SG_SORT.ty = (a, b) => { const g = (x) => !x.grp ? 0 : 1 + (ORDER.indexOf(x.grp) + 1 || 99), o = (x) => Number.isFinite(x.o) ? x.o : 1e6; return g(a) - g(b) || (g(a) === 100 ? String(a.grp).localeCompare(String(b.grp)) : 0) || o(a) - o(b) || a.id.localeCompare(b.id); };
  const oThs = whLThsHtml;
  whLThsHtml = function(c){ return oThs(c.k === 'sg' ? {...c, cols: c.cols.map(x => x[0] === 'nm' ? ['ty', 'Type', ''] : x)} : c); };   // the Type heading over the name column (the icon column's head holds Select all)
  const oScan = whScanApply;
  whScanApply = function(n, text, force){
    const r = oScan.apply(this, arguments), P = whP3(n), s = whS.sg.sys[n]; if(P.lazyAsk || !s) return r;
    const pos = new Map(whScanRows(text).rows.map((x, i) => [x.id, i]));
    if(pos.size) for(const x of s.rows) x.o = pos.has(x.id) ? pos.get(x.id) : 1000 + (Number.isFinite(x.o) ? x.o : 999);   // Q7: the latest paste's order; the rest after, in their old order
    whSgSave(); whS.pn = {}; whPaint(true); return r;
  };

  // ---- Auto-add (plan section 4): a jump between k-space and J-space puts the k-space side's hole in Intel's Wormholes list
  const oSeen = whSeen;
  whSeen = function(id, t, docked){
    const S = whState(), prev = S.last, r = oSeen.apply(this, arguments), now = S.last;
    if(RT.jw && !docked && prev !== null && now !== prev && whIsJ(now) !== whIsJ(prev)){
      const k = whIsJ(now) ? prev : now, j = whIsJ(now) ? now : prev, st = itWhStore(), old = st.rep[k], tt = Number.isFinite(t) ? t : Date.now();
      const n = old ? {...old} : {id: k, t: tt, who: '', drifter: false, src: 'you', sigs: []};
      n.t = Math.max(tt, old ? old.t : 0); n.jw = {j, t: tt, out: !whIsJ(now)};
      const cl = whClsName(whCls(j)); if(IT_WH_CLS_RX.test(cl)) n.info = itWhInfoMerge(old && old.info, {cls: cl});
      delete st.gone[k]; st.rep[k] = itWhDrSet(n); itWhSave(); itWhChanged();
    }
    return r;
  };
  const oBy = itWhByTxt;
  itWhByTxt = function(w){
    if(w && w.src === 'chain') return `on your chain → ${whName(w.chain)} (${clsEff(w.chain)})`;
    if(w && w.jw) return `${w.jw.out ? 'you came out of' : 'you jumped into'} ${whName(w.jw.j)} (${clsEff(w.jw.j)})`;
    return oBy(w);
  };
  const oRows = itWhRowsHtml;
  itWhRowsHtml = function(){
    const st = itWhStore();
    return oRows().split('<div class="it-whp-r">').map((ch, i) => { if(!i) return ch; const m = /data-it-whgo="(\d+)"/.exec(ch), w = m && st.rep[m[1]];
      return '<div class="it-whp-r">' + (w && w.jw && whEff(w.jw.j) ? ch.replace('<span class="it-whp-by">', `<span class="it-whp-by" title="${escapeHtml(effTxt(w.jw.j))}">`) : ch); }).join('');
  };
  const oSet = itSettingsHtml;
  itSettingsHtml = function(numbered){
    return oSet(numbered).replace(/(data-it-whkeep>[\s\S]*?<\/select><\/label>)/, `$1<label title="Jumping between k-space and a wormhole adds that k-space system's hole to the Wormholes list, with the system it leads to"><input type="checkbox" data-rt-jw${RT.jw ? ' checked' : ''}> add the hole when you jump into or out of J-space</label>`);
  };
  document.addEventListener('change', (e) => { if(e.target.matches && e.target.matches('[data-rt-jw]')) RT.jw = e.target.checked; });

  // ---- the chain's k-space ends on the Intel map (plan section 6): rings like a live report, for connections seen within the keep time
  const oMapWh = itMapWh;
  itMapWh = function(){
    const out = oMapWh(); if(itWhAside || typeof whState !== 'function') return out;
    const S = whState(), g = itGraphGet(), cut = Date.now() - itWhStore().keepH * 3600e3;
    if(out.mark === out.live) out.mark = new Map(out.live);
    for(const l of S.st.links){
      const kk = whIsJ(l.a) ? (whIsJ(l.b) ? null : l.b) : (whIsJ(l.b) ? l.a : null); if(kk === null || !(l.seen >= cut)) continue;
      const i = g.at.get(kk); if(i === undefined) continue;
      const w = out.kept.get(i) || {id: kk, t: l.seen, who: '', drifter: !!l.dr, src: 'chain', sigs: [], chain: kk === l.a ? l.b : l.a};
      out.kept.set(i, w); out.live.set(i, w); out.mark.set(i, w);
    }
    return out;
  };
})();
