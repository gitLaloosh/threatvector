// MOCKUP prototype (plan: claude/roadmap/hole-mass-runs-plan.md), appended after the page's own script (main a02d876, v2026.11.24.1).
// Mass panel: odds split (stuck / gone, not crit), the safe-mass line, + Finisher at any step, a "Send X instead" per finisher, up to 5 ships,
// saved runs (a log in tvWhMassRuns, replayed), Undo through the whole run. Overrides page functions by name; the build edits them in place.
(() => {
  const RR_KEY = 'tvWhMassRuns', RR_MAX_SHIPS = 5;
  const css = document.createElement('style');
  css.textContent = `
  .hm-runs{margin:0; padding:0; list-style:none; display:flex; flex-direction:column; gap:4px; font:12px/1.45 var(--sans); color:var(--text);} .hm-runs[hidden]{display:none;}
  .hm-runs li{display:flex; flex-wrap:wrap; gap:6px 8px; align-items:center; justify-content:space-between; padding:4px 8px; border:1px solid var(--line); border-radius:4px; background:var(--panel);}
  .hm-runs li.cur{border-color:var(--cyan);} .hm-runs li > span:first-child{flex:1 1 200px; min-width:0;} .hm-runs .hm-rb{display:inline-flex; gap:6px; align-items:center;}
  .hm-runs .d{color:var(--text-dim);} .hm-runs .wh-ask{flex-basis:100%;}
  .hm-addf{display:flex; flex-direction:column; gap:6px; padding:8px; border:1px dashed var(--line); border-radius:6px;}
  .hm-end-acts{display:flex; gap:6px; flex-wrap:wrap;}
  .hm-sum .hm-sb{flex:0 1 auto; max-width:100%;}   /* five buttons: the row may wrap instead of running past the panel */
  .hm-pop .sa-warn.hm-full{flex:1 1 100%; max-width:none; margin:0; padding:8px 10px; align-items:center; border:1px solid var(--danger); border-radius:6px; background:color-mix(in srgb, var(--danger) 12%, transparent);}
  .hm-pop .sa-warn.hm-full .warn-title{color:var(--danger);}
  @media (max-width:599px){ .hm-sum .hm-sb{flex:1 1 100%; display:grid; grid-template-columns:repeat(3, minmax(0, 1fr));} .hm-sum .hm-sb button{padding-inline:4px; white-space:nowrap;} .hm-runs button, .hm-addf button, .hm-end-acts button, .hm-pop .wh-note button{min-height:44px;} }`;
  document.head.appendChild(css);

  // ---- storage: a short log per run, replayed (never the possible holes themselves)
  window.rrRead = function(){ try{ const o = JSON.parse(localStorage.getItem(RR_KEY) || 'null'); if(o && o.v === 1 && Array.isArray(o.runs)) return o.runs.filter(r => r && typeof r.id === 'string' && typeof r.code === 'string' && Array.isArray(r.ships) && Array.isArray(r.log)); }catch(e){ } return []; };
  window.rrWrite = function(runs){ const H = hmState(); try{ localStorage.setItem(RR_KEY, JSON.stringify({v: 1, runs})); H.saveErr = false; return true; }catch(e){ H.saveErr = true; return false; } };
  window.rrSave = function(){
    const H = hmState(), r = H.run; if(!r) return;
    r.upd = Date.now(); r.done = H.pl ? H.pl.done || '' : ''; r.obs = H.pl ? H.pl.obs : r.st0; r.n = H.pl ? H.pl.hist.length : 0;
    rrWrite(rrRead().filter(x => x.id !== r.id).concat([r]));
  };
  window.rrShip = (s) => ({name: s.name, label: s.label, est: !!s.est, fin: !!s.fin, modes: s.modes.map(m => ({k: m.k, lab: m.lab, m: m.m}))});
  window.rrPl = function(r){
    const h = hmHole(r.code);
    const S = r.ships.map(s => ({...s, modes: s.modes.filter(m => m.m <= h.J), at: s.at0 || 'this', last: {out: 0, back: 0}}));
    const pl = {H: h, M0: h.M0, goal: r.goal, fin: r.fin, here: r.here.name, there: r.there.name, ships: S, P: hmPoss(h.M0, r.st0), obs: r.st0, hist: [], done: '', reset: false, finOk: false, free: []};
    for(const e of r.log) rrApply(pl, e, h);
    return pl;
  };
  window.rrApply = function(pl, e, h){
    if(e.t === 's'){ const g = e.g.map(([i, k]) => ({i, mo: pl.ships[i].modes.find(m => m.k === k)})); hmApply(pl, {g, dir: e.d, m: g.reduce((a, x) => a + x.mo.m, 0)}, e.a, e.at); }
    else if(e.t === 'add') pl.ships.push({...e.ship, modes: e.ship.modes.filter(m => m.m <= h.J), at: e.at, last: {out: 0, back: 0}});
    else if(e.t === 'free') pl.free = (pl.free || []).concat([e.i]);
    else if(e.t === 'lost'){   // a ship lost: out of the run; part of the step under way kept for its answer; its pod, when it comes home, a ship of its own
      const s = pl.ships[e.i]; if(!s) return; s.lost = true;
      if('part' in e) pl.part = e.part.length ? {g: e.part, dir: e.d} : null;
      if(e.pod) pl.ships.push({...e.pod, modes: e.pod.modes.filter(m => m.m <= h.J), at: s.at, last: {...s.last}, pod: true, fin: false});   // the pilot's polarization (UNVERIFIED: per pilot, hand test)
    }
    else if(e.t === 'carry'){   // Change → Carry on: a kept ship keeps its side and polarization; a new one starts on the finish side
      const old = pl.ships, used = new Set();
      pl.ships = e.ships.map(s => { const k = s.at0 ? -1 : old.findIndex((o, j) => !used.has(j) && !o.lost && !o.pod && o.label === s.label), n = {...s, modes: s.modes.filter(m => m.m <= h.J), at: s.at0 || pl.fin, last: {out: 0, back: 0}}; if(k >= 0){ used.add(k); n.at = old[k].at; n.last = {...old[k].last}; } return n; });
      pl.ships = pl.ships.concat(old.filter(o => o.pod && !o.lost)); pl.part = null;   // a pod on its way home stays
      pl.free = [];
    }
  };
  window.rrLoad = function(r){
    const H = hmState();
    H.run = r; H.link = whS.st.links.find(l => whLinkKey(l.a, l.b) === r.link) || null; H.ty = r.code; H.goal = r.goal; H.fin = r.fin; H.st = r.st0;
    if(Array.isArray(r.rows)) H.ships = r.rows.map(x => ({...x}));
    H.pl = rrPl(r); H.pv = H.pl.done ? null : hmPreview(H.pl); H.prev = null; H.ask = null; H.rs = false; H.fast = false; H.addF = null; H.lostF = null; H.delAsk = null;
  };
  window.rrDel = function(id){ const H = hmState(), was = H.saveErr; rrWrite(rrRead().filter(x => x.id !== id)); if(H.run && H.run.id === id){ H.run = null; H.pl = null; H.prev = null; } else if(was && H.run) rrSave(); };
  addEventListener('storage', (e) => {   // another tab saved: the open run follows it
    if(e.key !== RR_KEY) return; const H = hmState(); if(!H.run) return;
    const r = rrRead().find(x => x.id === H.run.id); if(!r){ H.run = null; H.pl = null; } else if(r.upd !== H.run.upd) rrLoad(r); hmPaint();
  });

  // ---- the next step: odds split into stuck / gone (not crit), stuck first in the pick; a freed finisher per ship; the safe mass for a lone ship
  window.hmNext = function(pl, now){
    if(pl.done) return null;
    const D = pl.fin, P = pl.P, S = pl.ships, Rmin = P.length ? hmLo(P[0]) : 0, LV = S.map((s, i) => i).filter(i => !S[i].lost), offs = LV.filter(i => S[i].at !== D);   // a lost ship takes no part
    if(pl.part){   // a ship lost part way through a step: the rest of it already jumped and waits for its answer
      const g = pl.part.g.map(([i, k]) => ({i, mo: S[i].modes.find(m => m.k === k)})).sort((x, y) => x.mo.m - y.mo.m);
      return {g, dir: pl.part.dir, m: g.reduce((a, x) => a + x.mo.m, 0), risk: 0, stuck: 0, col: 0, need: 0, wait: 0, home: false, lastIn: S[g[g.length - 1].i].name, safe: 0, part: true};
    }
    if(!LV.length) return {none: true};
    if(pl.goal === 'crit' && pl.obs === 'critical' && !offs.length){ pl.done = 'crit'; return null; }
    const crit = pl.goal === 'crit', free = new Set(pl.free || []);
    const lightest = (s) => Math.min(...s.modes.map(m => m.m)), light = Math.min(...LV.map(i => lightest(S[i])));
    const toward = D === 'this' ? 'back' : 'out', away = D === 'this' ? 'out' : 'back';
    const pol = (g, d) => Math.max(0, ...g.map(x => { const t = S[x.i].last[d]; return t && now - t < WH_MASS_POL_MS ? t + WH_MASS_POL_MS : 0; }));
    const combos = (idx) => idx.reduce((acc, i) => acc.flatMap(c => S[i].modes.map(mo => c.concat([{i, mo}]))), [[]]);
    const sum = (g) => g.reduce((a, x) => a + x.mo.m, 0);
    const kept = (i) => S[i].fin && !free.has(i);
    const fin = (g) => g.some(x => kept(x.i)) ? 1 : 0;
    const out = (b, dir, safe, home) => { const g = b.g.slice().sort((x, y) => x.mo.m - y.mo.m), lastIn = home ? g.reduce((a, x) => lightest(S[x.i]) >= lightest(S[a.i]) ? x : a, g[0]) : g[g.length - 1];
      return {g, dir, m: sum(g), risk: b.risk, stuck: b.stuck, col: Math.max(0, b.risk - b.stuck), need: b.need, wait: pol(g, dir), home, lastIn: S[lastIn.i].name, safe: b.risk > 0 ? Math.max(0, Math.floor(safe / 100) * 100) : 0}; };
    if(offs.length){
      let best = null;
      for(let mask = 1; mask < (1 << offs.length); mask++){
        const idx = offs.filter((i, k) => mask & (1 << k)), all = idx.length === offs.length;
        for(const g of combos(idx)){
          const m = sum(g), pre = m - Math.max(...g.map(x => x.mo.m)), close = all && !crit;
          const risk = hmShare(P, close ? pre : m), stuck = close ? risk : all ? hmShare(P, pre) : risk;   // all in, Crit: closing on the last one = everyone home, hole gone
          const keep = close ? hmLe(P, m) + (P.length - hmLe(P, m + light)) : 0;
          const k = [risk > 0 ? 1 : 0, stuck, risk, fin(g), all ? 0 : 1, -keep, -m]; if(!best || hmCmp(k, best.k) < 0) best = {g, k, risk, stuck, need: close ? pre : m};
        }
      }
      return out(best, toward, Rmin - (best.need - sum(best.g)), false);
    }
    const C = [];
    for(let mask = 1; mask < (1 << LV.length); mask++){
      const idx = LV.filter((i, k) => mask & (1 << k));
      for(const g of combos(idx)){
        const back = g.map(x => lightest(S[x.i])), m = sum(g), all = m + back.reduce((a, b) => a + b, 0), mb = Math.max(...back), need = crit ? all : all - mb;
        C.push({g, m, need, risk: hmShare(P, need), stuck: crit ? hmShare(P, all - mb) : hmShare(P, need), wait: pol(g, away), fin: fin(g)});
      }
    }
    const nf = C.filter(c => !c.fin), pool = pl.obs === 'critical' || !nf.length ? C : nf;
    pool.sort((a, b) => (a.risk > 0) - (b.risk > 0) || (a.risk > 0 ? a.stuck - b.stuck || a.risk - b.risk || a.m - b.m : a.fin - b.fin || b.m - a.m) || a.g.length - b.g.length);
    const best = pool[0], fr = best.wait ? pool.find(c => c.risk === best.risk && c.fin <= best.fin && !c.wait && c.m >= best.m * 0.75) : null;
    const safeOut = crit ? Rmin / 2 : Rmin;   // a lone ship: Crit, out and back cold must both fit; Roll, its way back may close it
    const st = out(fr || best, away, safeOut, true);
    if(pool !== C && st.risk > 0){   // each finisher that could go safely on its own terms: offered, lightest first
      st.finAlt = LV.filter(i => kept(i) && C.some(c => c.risk === 0 && c.g.some(x => x.i === i) && c.g.every(x => x.i === i || !kept(x.i)))).sort((a, b) => lightest(S[a]) - lightest(S[b]));
    }
    if(st.risk === 0){
      const f = pool.filter(c => c.risk > 0 && c.risk < 0.99 && c.m >= 2 * st.m).sort((a, b) => a.stuck - b.stuck || a.risk - b.risk || (a.wait > 0) - (b.wait > 0) || b.m - a.m)[0];
      if(f){ st.fast = out(f, away, safeOut, true); st.fast.isFast = true; st.fast.slow = {...st}; }
    }
    return st;
  };

  // ---- the words
  window.hmFarSide = (pl) => pl.fin === 'this' ? pl.there : pl.here;
  window.hmRiskWords = function(pl, st){
    const a = st.stuck > 0 ? `${hmRiskTxt(st.stuck)} that it closes with ${hmWho(pl, st)} stuck in ${hmFarSide(pl)}` : '';
    const b = st.col > 0 ? `${hmRiskTxt(st.col)} that it closes on ${st.lastIn}’s jump in: everyone’s home, but the hole is gone, not crit` : '';
    return a && b ? `${a}; ${b}.` : a ? a + '.' : `no one can be left behind, but ${b}.`;
  };
  window.hmRiskShort = (st) => [st.stuck > 0 ? `${hmRiskTxt(st.stuck)} stuck` : '', st.col > 0 ? `${hmRiskTxt(st.col)} gone, not crit` : ''].filter(Boolean).join(', ');
  window.hmSafeTxt = function(pl, st){
    if(!st.home) return '';   // ships coming in: only they can make that trip, so a lighter ship isn't the answer
    if(!(st.safe > 0)) return 'No ship is light enough to be sure.';
    return `A ship under ${hmT(st.safe)}${st.home && pl.goal === 'crit' ? ' (cold out and back)' : ''} would be safe${st.finAlt && st.finAlt.length ? '.' : ': add one with + Finisher.'}`;
  };
  window.hmRiskHtml = function(pl, st){
    if(st.part) return `<div class="wh-note"><b>Part of this step:</b> ${escapeHtml('a ship in it was lost before it jumped, so only the ships that jumped are counted. Show Info on the hole, as for any step.')}</div>`;
    if(st.isFast) return hmFastHtml(pl, st);
    if(!(st.risk > 0)) return hmSlowHtml(pl, st);
    return `<div class="wh-note it-warn"><b>No fully safe jump:</b> ${escapeHtml(`${hmRiskWords(pl, st)} ${hmSafeTxt(pl, st)}`.trim())}${hmFinAltHtml(pl, st)}</div>`;
  };
  window.hmFinAltHtml = function(pl, st){
    if(!st.finAlt || !st.finAlt.length) return '';
    const fr = new Set(pl.free || []), names = pl.ships.filter((s, i) => s.fin && !s.lost && !fr.has(i)).map(s => s.name);
    return ` ${escapeHtml(`${names.join(', ')} (finisher${names.length > 1 ? 's' : ''}) ${names.length > 1 ? 'are' : 'is'} kept for the end.`)} `
      + st.finAlt.map(i => { const q = hmClone(pl); q.free = (pl.free || []).concat([i]); return `<button type="button" data-hm="finnow" data-hm-f="${Number(i)}">${escapeHtml(`Send ${pl.ships[i].name} instead: safe, ${hmPvAllTxt(hmPreview(q))}`)}</button>`; }).join(' ');
  };
  window.hmSlowHtml = function(pl, st){
    const H = hmState(), pv = H.pv;
    if(!st.fast || !pv || !(pv.cap || pv.thi >= WH_MASS_SLOW_MS)) return '';
    const f = st.fast, pf = hmPreview(pl, true);
    return `<div class="wh-note it-warn"><b>Safe but slow:</b> ${escapeHtml(`${hmPvAllTxt(pv)}.`)} <button type="button" data-hm="fast">${escapeHtml(`Send ${hmShortTxt(pl, f)} instead (${hmRiskShort(f)}); ${hmPvAllTxt(pf)} taking the faster jumps`)}</button></div>`;
  };
  window.hmFastHtml = function(pl, st){
    const H = hmState(), s = st.slow, pv = H.pvSafe;
    return `<div class="wh-note it-warn"><b>Faster, not safe:</b> ${escapeHtml(hmRiskWords(pl, st))} <button type="button" data-hm="safe">${escapeHtml(`Back to the safe way: ${hmShortTxt(pl, s)}${pv ? `, ${hmPvAllTxt(pv)}` : ''}`)}</button></div>`;
  };
  window.hmBranchesHtml = function(pl, st, now){
    return hmPossibleSays(pl, st).map(k => { const q = hmClone(pl); hmApply(q, st, k, now + 60e3); const nx = hmNext(q, now + 60e3);
      return `<li>${hmSaidHtml(k, true)} ${escapeHtml(q.done ? hmDoneTxt(q) : nx && !nx.none ? hmShortTxt(q, nx) + (nx.risk > 0 ? ` (risky: ${hmRiskShort(nx)})` : '') + (nx.wait ? ', after a wait' : '') : 'no safe step')}</li>`; }).join('');
  };
  window.hmStepsBodyHtml = function(pl, st, stuck, now){
    const H = hmState();
    if(pl.done) return `<div class="hm-now hm-end">${escapeHtml(hmDoneTxt(pl))}</div>` + (H.ask ? whAskHtml(H.ask, [['hm-rm', 'Remove'], ['hm-rm-no', 'Keep it']]) : '')
      + `<div class="hm-end-acts"><button type="button" data-hm="delcur">Delete this run</button></div>` + (H.delAsk && H.run && H.delAsk === H.run.id ? rrDelAskHtml(H.run) : '');
    if(!st || st.none) return `<div class="hm-now">${escapeHtml(pl.ships.some(x => x.lost) ? 'No ships left: add one with + Finisher, or with Change.' : 'No ship here can jump this hole.')}</div>`;
    if(stuck) return `<div class="hm-now">${escapeHtml(`No safe step left with these ships: the next jump ${hmDirWord(pl, st)} would close the hole with ${hmWho(pl, st)} stuck in ${hmFarSide(pl)}.`)}</div>`
      + `<div class="wh-note it-warn">${escapeHtml(`${!st.home ? '' : st.safe > 0 ? `A ship under ${hmT(st.safe)}${st.home && pl.goal === 'crit' ? ' (cold out and back)' : ''} can do the last trip safely: add one with + Finisher. ` : 'No ship is light enough to be sure. '}Or leave it here: it says ${WH_MASS_SAYS[pl.obs].toLowerCase()}.`)}</div>`;
    return hmStepNowHtml(pl, st, now);
  };

  // a ship's masses arrive later: the add form is drawn again when they do (the page repaints only the setup)
  window.hmShipOf = function(r){
    const H = hmState(), k = hmKey(r), c = H.sm.get(k);
    if(c) return c.v ? {...c.v, fin: !!r.fin} : c.err ? {bad: true, err: c.err} : null;
    if(r.fit && !myShipById(r.fit)) return {bad: true, err: 'that saved fit is gone'};
    if(!r.fit && !String(r.hull || '').trim()) return null;
    const e = {v: null, err: ''}; H.sm.set(k, e);
    (r.fit ? hmFitModes(myShipById(r.fit)) : hmHullModes(r.hull)).then(v => { if(v.bad) e.err = 'not a ship the page knows'; else e.v = v; }, () => { e.err = 'its masses couldn’t be worked out'; }).then(() => { const S = hmState(); if(!S.pl || S.addF || S.lostF) hmPaint(); });
    return null;
  };
  // the connection list in the setup said "mass mass <50%" (IT_WH_INFO_TXT's short words already start with "mass" / "crit")
  const _links = hmLinksHtml; window.hmLinksHtml = (n) => _links(n).replace(/ · mass (mass|crit) /g, ' · $1 ');
  // ---- the panel: setup line with + Finisher, the add form, Saved runs
  const _row = hmShipRowHtml;
  window.hmShipRowHtml = (r, i, h) => { const H = hmState(), pv = H.prev, x = _row(r, i, h).replace('Finisher: waits until the hole is under 10%', 'Finisher: kept for the end, offered when it’s the safe choice');
    if(!pv || !r.nw) return x;   // a ship new to a run carried on (a replacement, say): which side it's in (the owner: "just ask which system it's being added in")
    const far = pv.fin === 'this' ? 'other' : 'this', at = `<label class="wh-lnk wide">It’s in <select data-hm-at="${Number(i)}" aria-label="${escapeHtml(`Ship ${i + 1} is in`)}">${whOptsHtml([[pv.fin, `${sideName(pv, pv.fin)} (where you finish)`], [far, sideName(pv, far)]], r.at || pv.fin)}</select></label>`;
    return x.slice(0, x.length - 6) + at + '</div>'; };
  window.hmAddBtnHtml = () => hmState().ships.length < RR_MAX_SHIPS ? '<button type="button" data-hm="add">+ Ship</button>' : '';
  window.hmSumHtml = function(pl){
    const H = hmState(), n = H.run ? H.run.log.length : 0, full = pl.ships.length >= RR_MAX_SHIPS, fr = new Set(pl.free || []);
    return `<div class="wh-note hm-sum"><span>${escapeHtml(`${pl.H.code} to ${pl.there} · ${pl.goal === 'roll' ? 'roll it' : 'crit it'}, finish in ${pl.fin === 'this' ? pl.here : pl.there} · ${pl.ships.map((s, i) => s.name + (s.lost ? (s.podHome ? ' (home)' : ' (lost)') : s.fin ? (fr.has(i) ? ' (finisher, sent)' : ' (finisher)') : '')).join(', ')}`)}</span><span class="hm-sb">`
      + `<button type="button" data-hm="undo"${escapeHtml(n ? '' : ' disabled')} title="Take the last step back (as far as the start of the run)">Undo</button>`
      + `<button type="button" data-hm="af" aria-expanded="${escapeHtml(String(!!H.addF))}"${escapeHtml(full || pl.done ? ' disabled' : '')} title="${escapeHtml(full ? '5 ships at most' : 'Add a light ship that waits for the end')}">+ Finisher</button>`
      + `<button type="button" data-hm="lf" aria-expanded="${escapeHtml(String(!!H.lostF))}"${escapeHtml(pl.done || !pl.ships.some(x => !x.lost) ? ' disabled' : '')} title="A ship was lost: the steps carry on with the rest">Ship lost</button>`
      + `<button type="button" data-hm="edit">Change</button><button type="button" data-hm="reset">Start over</button></span>${rrErrHtml()}</div>`
      + (H.rs ? whAskHtml(`Start over? The ${pl.hist.length} step${pl.hist.length === 1 ? '' : 's'} so far are forgotten; the hole starts from what it says now.`, [['hm-rs', 'Start over'], ['hm-rs-no', 'Keep going']]) : '');
  };
  window.rrAddFHtml = function(){
    const H = hmState(), a = H.addF, pl = H.pl; if(!a || !pl) return '';
    const s = hmShipOf(a.row), ok = s && !s.bad && s.modes.some(m => m.m <= pl.H.J), finN = pl.fin === 'this' ? pl.here : pl.there, farN = hmFarSide(pl), far = pl.fin === 'this' ? 'other' : 'this';
    return `<div class="hm-addf" role="group" aria-label="Add a finisher"><div class="wh-sub">Add a finisher</div><div class="hm-ship"><select data-hm-af="ship"${escapeHtml(a.row.fit ? ' class="hm-w2"' : '')} aria-label="Finisher">${hmFitOptsHtml(a.row)}<option value="hull"${escapeHtml(a.row.fit ? '' : ' selected')}>Type a hull…</option></select>`
      + (a.row.fit ? '' : `<input type="text" data-hm-af="hull" value="${escapeHtml(a.row.hull || '')}" placeholder="Hull, e.g. Buzzard" aria-label="Hull" list="whMassHullDl" maxlength="40" spellcheck="false">`)
      + `<span class="wh-note hm-m">${hmShipLineHtml(a.row, s, pl.H)}</span></div><datalist id="whMassHullDl">${hmHullDlHtml()}</datalist>`
      + `<label class="wh-lnk wide">It’s in <select data-hm-af="at" aria-label="It’s in">${whOptsHtml([[pl.fin, `${finN} (where you finish)`], [far, farN]], a.at)}</select></label>`
      + `<div class="wh-note">It waits for the end like any finisher: you’re offered it when the bigger ships have no safe trip.</div>`
      + `<div class="wh-acts"><button type="button" class="mys-primary" data-hm="afadd"${escapeHtml(ok ? '' : ' disabled')}>Add</button><button type="button" data-hm="afno">Cancel</button></div></div>`;
  };
  const DONE_W = {rolled: 'rolled', crit: 'crit', stranded: 'closed, ships stuck', closed: 'closed, not crit'};
  const when = (t) => { const d = new Date(t), now = new Date(); return (d.toDateString() === now.toDateString() ? '' : d.toLocaleDateString('en-US', {month: 'short', day: 'numeric'}) + ' ') + d.toTimeString().slice(0, 5); };
  window.rrLabel = (r) => `${r.code} · ${r.here.name} ↔ ${r.there.name} · ${r.goal === 'roll' ? 'roll' : 'crit'} · ${r.n || 0} step${r.n === 1 ? '' : 's'} · ${r.done ? DONE_W[r.done] || 'done' : r.obs === 'fresh' ? 'fresh' : 'says ' + WH_MASS_SAYS[r.obs].toLowerCase()} · ${when(r.upd || r.made)}`;
  window.rrDelAskHtml = (r) => whAskHtml(`Delete the saved run ${r.code} · ${r.here.name} ↔ ${r.there.name}? Its ${r.n || 0} step${r.n === 1 ? '' : 's'} are forgotten.`, [['hm-del', 'Delete'], ['hm-del-no', 'Keep it']]);
  const runsOpen = () => { const H = hmState(); return H.runsOpen === undefined ? !H.pl : H.runsOpen; };
  window.rrListHtml = function(){
    const H = hmState(), runs = rrRead().sort((a, b) => (b.upd || b.made) - (a.upd || a.made)), cur = H.run && H.run.id, op = runsOpen(); if(!runs.length) return '';
    return `<button type="button" class="it-whp-xb" data-hm="runs" aria-expanded="${escapeHtml(String(op))}" aria-controls="whMassRuns">${IT_CHEV}Saved runs (${runs.length})</button><ul class="hm-runs" id="whMassRuns"${escapeHtml(op ? '' : ' hidden')}>`
      + runs.map(r => `<li class="${escapeHtml(r.id === cur ? 'cur' : '')}"><span>${escapeHtml(rrLabel(r))}</span><span class="hm-rb">${r.id === cur && H.pl ? '<span class="d">open</span>' : `<button type="button" data-hm-open="${escapeHtml(r.id)}">Open</button>`}<button type="button" data-hm-del="${escapeHtml(r.id)}" aria-label="${escapeHtml('Delete ' + rrLabel(r))}">Delete</button></span>${H.delAsk === r.id && !(r.id === cur && H.pl && H.pl.done) ? rrDelAskHtml(r) : ''}</li>`).join('') + '</ul>';
  };
  // WH-01: the page's warning row (red ! badge, one bold line, one context line; the whole sentence on hover), in a red box that
  // sits inside the pinned line, so it stays in view while the steps scroll
  const RR_FULL = 'This browser’s storage is full, so this run will be lost if you leave or reload the page. Delete a saved run you don’t need and this one is saved again.';
  window.rrErrHtml = () => hmState().saveErr ? `<div class="sa-warn hm-full" role="alert"><span class="ewar-badge danger">!</span><span class="warn-text"><span class="warn-title">This run isn’t saved</span>${ctxHtml(withCode('Storage full: delete a saved run', 'WH-01'), '', withCode(RR_FULL, 'WH-01'))}</span></div>` : '';
  const _panel = hmPanelHtml;
  window.hmPanelHtml = function(){
    const H = hmState();
    if(H.pl) return hmHeadHtml() + hmSumHtml(H.pl) + rrAddFHtml() + rrLostHtml() + rrListHtml() + `<div class="hm-steps" aria-live="polite">${hmStepsHtml()}</div>`;
    const s = _panel(), head = hmHeadHtml();
    return head + rrErrHtml() + rrListHtml() + s.slice(head.length);
  };

  // ---- runs: Show the steps, answers, Undo, Start over, open on a connection
  window.hmGo = function(carry){
    const H = hmState(), h = hmHole(H.ty); if(!h) return;
    const ships = H.ships.map(hmShipOf).filter(s => s && !s.bad); if(!ships.length) return;
    const r = H.run;
    if(carry && r && H.prev){
      const sh = H.ships.map(x => ({x, s: hmShipOf(x)})).filter(o => o.s && !o.s.bad);
      r.log.push({t: 'carry', ships: sh.map(o => ({...rrShip(o.s), ...(o.x.nw ? {at0: o.x.at || H.prev.fin} : {})}))});
      r.rows = H.ships.map(({nw, at, ...x}) => ({...x})); H.ships = r.rows.map(x => ({...x})); hmSave(); H.pl = rrPl(r);
    }
    else {
      const n = whFocus(), l = H.link, o = l ? (l.a === n ? l.b : l.a) : null, base = hmNew(H, ships);
      const nr = {id: 'r' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6), made: Date.now(), link: l ? whLinkKey(l.a, l.b) : '', mass0: l ? l.mass || '' : '',
        here: {id: n, name: base.here}, there: {id: o, name: base.there}, code: h.code, st0: H.st, goal: H.goal, fin: H.fin, ships: base.ships.map(rrShip), rows: H.ships.map(x => ({...x})), log: []};
      if(r && (!r.log.length || H.prev)) nr.id = r.id;   // Start over (or Change → Start over) keeps the same saved run
      H.run = nr; H.pl = rrPl(nr);
    }
    H.prev = null; H.ask = null; H.rs = false; H.fast = false; H.addF = null; H.lostF = null; H.delAsk = null; H.runsOpen = undefined;
    H.pv = hmPreview(H.pl); rrSave();
  };
  window.hmSay = function(k){
    const H = hmState(), pl = H.pl, st = H.step; if(!pl || !st || st.none || !H.run) return;
    const at = Date.now(); H.run.log.push({t: 's', g: st.g.map(x => [x.i, x.mo.k]), d: st.dir, a: k, at});
    hmApply(pl, st, k, at); H.fast = false; H.pv = pl.done ? null : hmPreview(pl);
    if(pl.obs !== 'gone' && hmLinkLive()) hmLinkMass(pl.obs);
    const l = hmLinkLive(); if(pl.done && pl.obs === 'gone' && l){ const n = whFocus(); H.ask = `The hole is gone. Remove the connection to ${whName(l.a === n ? l.b : l.a)}?`; }
    rrSave();
  };
  window.hmUndo = function(){
    const H = hmState(), r = H.run; if(!r || !r.log.length) return;
    const e = r.log.pop();
    if(e.t === 'lost' && e.row && Array.isArray(r.rows)){ r.rows.splice(Math.min(e.rowAt, r.rows.length), 0, e.row); H.ships = r.rows.map(x => ({...x})); hmSave(); }
    if(e.t === 'add' && Array.isArray(r.rows)){ const j = r.rows.map(x => x.fin && (x.fit || x.hull)).lastIndexOf(e.row && (e.row.fit || e.row.hull)); if(j >= 0) r.rows.splice(j, 1); H.ships = r.rows.map(x => ({...x})); hmSave(); }
    H.pl = rrPl(r); H.ask = null; H.rs = false; H.fast = false; H.addF = null; H.lostF = null; H.pv = H.pl.done ? null : hmPreview(H.pl);
    if(hmLinkLive()){ const said = r.log.filter(x => x.t === 's'); const v = said.length ? said[said.length - 1].a : r.mass0 || ''; if((H.link.mass || '') !== v) hmLinkMass(v); }
    rrSave();
  };
  window.hmReset = function(){
    const H = hmState(), pl = H.pl, r = H.run; H.back = []; H.fast = false; H.rs = false; H.prev = null; H.ask = null; H.addF = null; H.lostF = null; H.delAsk = null;
    if(pl && pl.obs && pl.obs !== 'gone') H.st = pl.obs; else if(hmLinkLive()) H.st = H.link.mass || 'stable';
    H.pl = null;
    if(r && pl && pl.done) H.run = null;   // a finished run stays in the list as it was
    else if(r){ r.log = []; r.st0 = H.st; rrSave(); }   // the same saved run, no steps until Show the steps
  };
  window.rrAddF = function(){
    const H = hmState(), a = H.addF, r = H.run; if(!a || !r || !H.pl) return;
    const s = hmShipOf(a.row); if(!s || s.bad) return;
    r.log.push({t: 'add', ship: rrShip({...s, fin: true}), at: a.at, row: {...a.row, fin: true}});
    r.rows = (Array.isArray(r.rows) ? r.rows : H.ships).concat([{...a.row, fin: true}]); H.ships = r.rows.map(x => ({...x})); hmSave();
    H.pl = rrPl(r); H.addF = null; H.lostF = null; H.fast = false; H.pv = hmPreview(H.pl); rrSave();
  };
  window.hmOpen = function(){
    const H = hmState(), n = whFocus(), ls = n === null ? [] : whLinksOf(n), keys = ls.map(l => whLinkKey(l.a, l.b));
    if(H.pl && H.run && keys.includes(H.run.link)){ hmPaint(); return; }
    const r = rrRead().filter(x => !x.done && keys.includes(x.link)).sort((a, b) => (b.upd || b.made) - (a.upd || a.made))[0];
    if(r) rrLoad(r);
    else if(!H.pl || !ls.includes(H.link)){ H.link = ls.find(l => hmLinkType(l, n).code) || ls[0] || null; H.pl = null; H.run = null; H.prev = null; H.ask = null; H.rs = false; hmFromLink(n); }
    hmPaint();
  };
  // ---- a ship lost (the owner: "add a backlog item to account for a ship being lost during the rolling/critting process so we dont have
  // to start from scratch in order to get accurate instructions."). If it jumped first, its step is answered first, then it's marked lost
  // ("then the user can select the new mass state, let the steps update and THEN mark it as lost."); lost before jumping, it comes out of the
  // step, and the rest of the step, if it jumped, waits for its answer; its pod, lost on the far side, can come home as a ship of its own
  window.hmApply = function(pl, st, obs, now){   // the page's, with lost ships left out of "stranded", a held part step cleared, a pod home leaving the run
    for(const x of st.g){ const s = pl.ships[x.i]; s.at = s.at === 'this' ? 'other' : 'this'; s.last[st.dir] = now; }
    let P = pl.P.filter(c => hmBoxSays(c, st.m, obs)).map(c => [c[0], c[1] - st.m, c[2], c[3]]); pl.reset = false;
    if(!P.length && obs !== 'gone'){ P = hmPoss(pl.M0, obs); pl.reset = true; }
    pl.P = P.length ? P : pl.P; pl.obs = obs; pl.hist.push({short: hmShortTxt(pl, st), obs}); pl.part = null;
    for(const s of pl.ships) if(s.pod && !s.lost && s.at === pl.fin){ s.lost = true; s.podHome = true; }
    const offs = pl.ships.filter(x => !x.lost && x.at !== pl.fin);
    if(obs === 'gone') pl.done = offs.length ? 'stranded' : pl.goal === 'roll' ? 'rolled' : 'closed';
  };
  window.hmDoneTxt = function(pl){
    const side = pl.fin === 'this' ? pl.here : pl.there, offs = pl.ships.filter(s => !s.lost && s.at !== pl.fin).map(s => s.name);
    return {rolled: `Rolled: the hole is gone and everyone is in ${side}.`, crit: `Crit: it says less than 10% and everyone is in ${side}.`,
      stranded: `The hole closed with ${offs.join(', ')} on the other side.`, closed: 'The hole closed (you wanted it open).'}[pl.done] || '';
  };
  const _stepH = hmStepHtml; window.hmStepHtml = (pl, st) => st.part ? _stepH(pl, st).replace(/ This can close it:[^<]*/, '') : _stepH(pl, st);   // already jumped: no order to give
  const sideName = (pl, at) => at === 'this' ? pl.here : pl.there;
  const RR_POD = {hull: 'Capsule'};   // the pod's mass: CCP's type data, as any hull (hmHullModes)
  window.rrLostHtml = function(){
    const H = hmState(), f = H.lostF, pl = H.pl; if(!f || !pl) return '';
    const st = H.step, s = f.i === null ? null : pl.ships[f.i], inStep = (i) => !!(st && !st.none && st.g.some(x => x.i === i));
    const rest = s && inStep(f.i) ? st.g.filter(x => x.i !== f.i) : [], far = !!(s && !s.pod && s.at !== pl.fin);
    const pod = far && f.pod === 'home' ? hmShipOf(RR_POD) : null, ok = s && (!far || f.pod !== 'home' || (pod && !pod.bad));
    const opts = [['', 'Pick the ship']].concat(pl.ships.map((x, i) => [i, x]).filter(([, x]) => !x.lost).map(([i, x]) => [String(i), `${x.name}${x.fin ? ' (finisher)' : ''} · in ${sideName(pl, x.at)}${inStep(i) ? ' · in this step' : ''}`]));
    return `<div class="hm-addf" role="group" aria-label="A ship was lost"><div class="wh-sub">A ship was lost</div>`
      + `<label class="wh-lnk wide">Which one <select data-hm-lf="i" aria-label="Which ship was lost">${whOptsHtml(opts, f.i === null ? '' : String(f.i))}</select></label>`
      + (s && inStep(f.i) ? `<div class="wh-note">${escapeHtml('It’s in this step. If it jumped before it was lost, answer the step first, then mark it lost.')}</div>` : '')
      + (rest.length ? `<label class="wh-lnk wide">The others in this step <select data-hm-lf="others" aria-label="The others in this step">${whOptsHtml([['keep', 'jumped: wait for Show Info'], ['new', 'didn’t jump: a new step']], f.others)}</select></label>` : '')
      + (far ? `<label class="wh-lnk wide">Its pod <select data-hm-lf="pod" aria-label="Its pod">${whOptsHtml([['home', 'comes home through the hole'], ['no', 'doesn’t (a clone jump, or it stays)']], f.pod)}</select></label>`
        + (f.pod === 'home' ? `<div class="wh-note">${escapeHtml(pod && !pod.bad ? `The pod (${hmT(Math.min(...pod.modes.map(m => m.m)))}) gets a step of its own, home.` : 'Working out the pod’s mass…')}</div>` : '') : '')
      + `<div class="wh-acts"><button type="button" class="mys-primary" data-hm="lfgo"${escapeHtml(ok ? '' : ' disabled')}>Mark lost</button><button type="button" data-hm="lfno">Cancel</button></div></div>`;
  };
  window.rrLost = function(){
    const H = hmState(), f = H.lostF, r = H.run, pl = H.pl; if(!f || !r || !pl || f.i === null) return;
    const i = f.i, s = pl.ships[i], st = H.step; if(!s || s.lost) return;
    const e = {t: 'lost', i, at: Date.now()};
    if(st && !st.none && st.g.some(x => x.i === i)){ const rest = st.g.filter(x => x.i !== i); e.part = f.others === 'keep' && rest.length ? rest.map(x => [x.i, x.mo.k]) : []; e.d = st.dir; }
    if(!s.pod && s.at !== pl.fin && f.pod === 'home'){ const c = hmShipOf(RR_POD); if(!c || c.bad) return; const lo = Math.min(...c.modes.map(m => m.m));
      e.pod = {name: `${s.name}’s pod`, label: `${s.label}’s pod`, est: false, modes: c.modes.filter(m => m.m === lo).map(m => ({k: 'cold', lab: 'pod', m: m.m}))}; }
    if(!s.pod && Array.isArray(r.rows)){   // the setup's list loses it too, so Change doesn't bring it back; Undo puts it back
      let j = -1; r.rows.forEach((x, k) => { const v = hmShipOf(x); if(v && !v.bad && v.label === s.label && !!x.fin === !!s.fin) j = k; });
      if(j >= 0){ e.row = {...r.rows[j]}; e.rowAt = j; r.rows.splice(j, 1); H.ships = r.rows.map(x => ({...x})); hmSave(); }
    }
    r.log.push(e); H.pl = rrPl(r); H.lostF = null; H.fast = false; H.pv = H.pl.done ? null : hmPreview(H.pl); rrSave();
  };
  const _click = hmClick;
  window.hmClick = function(b){
    const H = hmState(), d = b.dataset;
    if(d.hm === 'finnow'){ if(H.run && H.pl && d.hmF !== undefined){ H.run.log.push({t: 'free', i: Number(d.hmF)}); H.pl = rrPl(H.run); H.fast = false; H.pv = hmPreview(H.pl); rrSave(); } }
    else if(d.hm === 'add'){ if(H.ships.length < RR_MAX_SHIPS) H.ships.push(H.prev ? {hull: '', nw: true} : {hull: ''}); hmSave(); }   // added while carrying on a run: asks its side
    else if(d.hm === 'af'){ H.addF = H.addF ? null : {row: {hull: ''}, at: H.pl.fin}; H.lostF = null; }
    else if(d.hm === 'lf'){ H.lostF = H.lostF ? null : {i: null, pod: 'home', others: 'keep'}; H.addF = null; }
    else if(d.hm === 'lfno') H.lostF = null;
    else if(d.hm === 'lfgo') rrLost();
    else if(d.hm === 'afno') H.addF = null;
    else if(d.hm === 'afadd') rrAddF();
    else if(d.hm === 'runs') H.runsOpen = !runsOpen();
    else if(d.hmOpen){ const r = rrRead().find(x => x.id === d.hmOpen); if(r) rrLoad(r); }
    else if(d.hmDel) H.delAsk = H.delAsk === d.hmDel ? null : d.hmDel;
    else if(d.hm === 'delcur') H.delAsk = H.run && H.run.id;
    else if(d.whAsk === 'hm-del'){ rrDel(H.delAsk); H.delAsk = null; }
    else if(d.whAsk === 'hm-del-no') H.delAsk = null;
    else return _click(b);
    const f = d.hm || ''; hmPaint();
    const p = hmPop(), bs = p ? [...p.querySelectorAll('button')] : [], again = bs.find(x => f && x.dataset.hm === f && !x.disabled) || bs.find(x => x.dataset.hmSay) || bs.find(x => !x.disabled && (x.dataset.hm === 'go' || x.dataset.hm === 'add'));
    if(again) again.focus({preventScroll: true});
    return true;
  };
  const _change = hmChange;
  window.hmChange = function(t){
    const H = hmState(), d = t.dataset;
    if(d.hmAt !== undefined && H.ships[Number(d.hmAt)]){ H.ships[Number(d.hmAt)].at = t.value; hmPaint(); const p = hmPop(), e = p ? p.querySelector(`[data-hm-at="${d.hmAt}"]`) : null; if(e) e.focus({preventScroll: true}); return; }
    if(d.hmLf !== undefined && H.lostF){
      const f = H.lostF; if(d.hmLf === 'i') f.i = t.value === '' ? null : Number(t.value); else f[d.hmLf] = t.value;
      hmPaint(); const p = hmPop(), e = p ? p.querySelector(`[data-hm-lf="${d.hmLf}"]`) : null; if(e) e.focus({preventScroll: true}); return;
    }
    if(d.hmAf === undefined || !H.addF) return _change(t);
    const a = H.addF;
    if(d.hmAf === 'ship') a.row = t.value === 'hull' ? {hull: ''} : {fit: t.value.slice(4)};
    else if(d.hmAf === 'hull'){ const s = hmShipId(t.value); a.row = {hull: s ? s[1] : t.value.trim().slice(0, 40)}; }
    else if(d.hmAf === 'at') a.at = t.value;
    hmPaint(); const p = hmPop(), e = p ? p.querySelector(`[data-hm-af="${d.hmAf}"]`) : null; if(e) e.focus({preventScroll: true});
  };
  // the info text: 208 words, under the panel's 210 cap (check_subtext's INFO_ALL_MAX)
  if(typeof CARD_INFO !== 'undefined' && CARD_INFO['whmap#mass']) CARD_INFO['whmap#mass'] = [
    'Works out, step by step, how to crit a hole (under 10%) or roll it (close it) with your ships, leaving everyone on the side you choose.',
    '[The numbers] Each type’s total mass and mass per jump are CCP’s; a new hole’s total is within ±10% of it.',
    '[In, out, hot, cold] Out is toward the side you don’t finish on; in, toward the side you do. Mass counts as you press jump: hot is the MWD (or AB) on, cold off. Ships that can jump together are one step, then one look at Show Info. + Finisher adds a light ship, kept for the end.',
    '[Safety] A jump that could close the hole is shown only when everyone then ends on your side. Otherwise you see the odds of a ship stuck on the far side and, for a crit, of the hole closing on the way home. A safe plan over 30 minutes also offers a faster risky jump. Polarization: no ship jumps the same way twice within 5 minutes.',
    '[Ship lost] If it jumped, answer first; its pod can get a step home.',
    '[Saved runs] Kept in this browser until you delete them.',
    '[For reference] Nothing is sent to EVE. Answers set the connection’s Mass.'];
})();
