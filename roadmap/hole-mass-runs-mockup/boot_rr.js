// Seeds a made-up chain (CCP's own wormhole systems picked by class), made-up saved fits and hull masses, opens the Wormholes tab and the
// Mass panel, and shows the MOCKUP bar. Home is a C2 (B274 to Rens), a K162 from a C3 whose far side is a D382 (less than 50%), a K162 from a C5.
(() => {
  const wait = (f, ms = 30000) => new Promise((res, rej) => { const t0 = Date.now(); const k = () => { let v; try{ v = f(); }catch(e){ v = null; } if(v) res(v); else if(Date.now() - t0 > ms) rej(new Error('timeout')); else setTimeout(k, 100); }; k(); });
  const sleep = (ms) => new Promise(r => setTimeout(r, ms));
  const RENS = 30002510;
  // made-up fits and hulls (masses invented for the mockup; the page works them out from the fit)
  const FITS = {mf1: ['Megathron', 'Higgs roller', 296800, 196800], mf3: ['Thorax', 'Finisher', 16300, 11300]};
  const HULLS = {buzzard: ['Buzzard', 1200], heron: ['Heron', 1150], capsule: ['Capsule', 30]};   // the capsule: no prop module, one mode
  function stubs(){
    const _sn = itSysName; window.itSysName = (id) => id === RENS ? 'Rens' : _sn(id);   // names come from ESI; the mockup has no network
    for(const [id, f] of Object.entries(FITS)) if(!myShip.list.some(r => r.id === id)) myShip.list.push({id, shipName: f[0], fitName: f[1], eft: 'mock-' + id, savedAt: '2026-11-24T00:00:00Z'});
    window.hmFitModes = async (rec) => { const f = FITS[rec.id]; return {name: f[0], label: `${f[0]} — ${f[1]}`, est: false, modes: [{k: 'hot', lab: 'MWD on', m: f[2]}, {k: 'cold', lab: 'prop off', m: f[3]}]}; };
    window.hmHullModes = async (name) => { const h = HULLS[String(name || '').trim().toLowerCase()]; if(!h) return {bad: true}; return {name: h[0], label: h[0], est: true, modes: (h[0] === 'Capsule' ? [] : [{k: 'hot', lab: 'MWD on', m: h[1] + 500}]).concat([{k: 'cold', lab: 'prop off', m: h[1]}])}; };
  }
  function seed(){
    const T = whTable(), pick = (cls, skip = 0) => { let n = 0; for(let i = 0; i < T.ids.length; i++) if(T.cls[i] === cls && /^J\d{6}$/.test(T.names[i]) && n++ === skip) return T.ids[i]; return null; };
    const A = pick('2', 3), C = pick('3', 5), E = pick('5', 2); window.RRJ = {A, C, E, RENS};
    const t0 = Date.now() - 50 * 60e3; [RENS, A, C, A, E, A].forEach((id, i) => whSeen(id, t0 + i * 4 * 60e3, false));
    const L = (a, b) => whLinkOf(a, b);
    whEndSet(L(A, RENS), A, 'RZL-429', 'B274'); whEndSet(L(A, RENS), RENS, 'TUV-907', 'K162');
    whEndSet(L(A, C), A, 'ABC-123', 'K162'); whEndSet(L(A, C), C, 'QRS-210', 'D382'); L(A, C).mass = 'reduced';
    whEndSet(L(A, E), A, 'MNO-118', 'K162'); whEndSet(L(A, E), E, 'XYZ-311', 'H296');
    const S = whState(); S.mk[A] = {st: 'home', tag: 'HOME', lock: true};
    whSave(); whMkSave(); whEndSave(); S.drawKey = '';
  }
  const H = () => hmState();
  const linkOf = (b) => whLinkOf(RRJ.A, b);
  let realSet = null;
  function reset(o = {}){
    if(realSet){ Storage.prototype.setItem = realSet; realSet = null; }
    if(!o.keep) try{ localStorage.removeItem('tvWhMassRuns'); }catch(e){}
    const h = H(); linkOf(RENS).mass = ''; linkOf(RRJ.C).mass = 'reduced'; linkOf(RRJ.E).mass = ''; whSave();
    whSelect(RRJ.A); whPopClose(); whPop('mass');   // (opening may pick up a saved run: the scene's own setup comes after)
    Object.assign(h, {run: null, pl: null, prev: null, ask: null, rs: false, fast: false, addF: null, lostF: null, delAsk: null, runsOpen: undefined, saveErr: false, back: []});
    h.ships = (o.ships || [{fit: 'mf1'}, {fit: 'mf1'}, {fit: 'mf3', fin: true}]).map(x => ({...x})); h.goal = o.goal || 'crit'; h.fin = o.fin || 'this'; h.open = true;
    h.link = linkOf(o.link || RRJ.C); hmFromLink(RRJ.A); if(o.st) h.st = o.st; hmPaint();
  }
  const ready = () => wait(() => H().ships.every(r => { const s = hmShipOf(r); return s && !s.bad; }));
  // answers as a real hole of total M would give them, until the step is risky (or n steps)
  async function play(M, until, n = 30){
    let R = M * ({fresh: 1, stable: 0.8, reduced: 0.45, critical: 0.08}[H().pl.obs] || 1);   // a hole that fits what it says now
    for(let k = 0; k < n; k++){ hmPaint(); const st = H().step; if(!st || st.none || H().pl.done || until(st)) break; R -= st.m; hmSay(hmSt(M, R)); }
    hmPaint();
  }
  async function critRisky(){ reset(); await ready(); hmGo(); await play(2000000, st => st.risk > 0); }
  const scenes = {
    async crit(){ await critRisky(); },
    async addf(){ await critRisky(); H().addF = {row: {hull: 'Buzzard'}, at: H().pl.fin}; hmPaint(); await wait(() => { const s = hmShipOf(H().addF.row); return s && !s.bad; }); hmPaint(); },
    async two(){ await scenes.addf(); rrAddF(); hmPaint(); },
    async undo(){ await scenes.two(); hmUndo(); hmPaint(); },
    async roll(){ reset({link: RENS, goal: 'roll', st: 'fresh', ships: [{fit: 'mf1'}]}); await ready(); hmGo(); await play(2050000, st => st.risk > 0); },
    async list(){
      reset({link: RENS, goal: 'roll', st: 'fresh', ships: [{fit: 'mf1'}, {fit: 'mf3'}]}); await ready(); hmGo(); await play(2050000, () => false, 40);   // rolled
      reset({keep: true, link: RRJ.E, ships: [{fit: 'mf1'}, {fit: 'mf3', fin: true}]}); await ready(); hmGo(); await play(3200000, () => false, 2);
      reset({keep: true}); await ready(); hmGo(); await play(2000000, st => st.risk > 0);
      const h = H(); h.run = null; h.pl = null; h.link = linkOf(RRJ.C); hmFromLink(RRJ.A); h.runsOpen = true; hmPaint();
    },
    async del(){ await scenes.list(); H().delAsk = rrRead().sort((a, b) => b.upd - a.upd)[1].id; hmPaint(); },
    async runs(){ await scenes.list(); const r = rrRead().sort((a, b) => b.upd - a.upd)[0]; rrLoad(r); H().runsOpen = true; hmPaint(); },
    async done(){ reset({link: RENS, goal: 'roll', st: 'fresh', ships: [{fit: 'mf1'}, {fit: 'mf3'}]}); await ready(); hmGo(); await play(2050000, () => false, 40); },
    async full(){   // storage "full" at today's size: the next answer doesn't fit; deleting the other run makes room
      reset({link: RENS, goal: 'roll', st: 'fresh', ships: [{fit: 'mf1'}, {fit: 'mf3'}]}); await ready(); hmGo(); await play(2050000, () => false, 4);
      reset({keep: true}); await ready(); hmGo(); await play(2000000, st => st.risk > 0);
      const cap = (localStorage.getItem('tvWhMassRuns') || '').length; realSet = Storage.prototype.setItem; const rs = realSet;
      Storage.prototype.setItem = function(k, v){ if(k === 'tvWhMassRuns' && String(v).length > cap) throw new DOMException('full', 'QuotaExceededError'); return rs.call(this, k, v); };
      H().runsOpen = false; hmSay(hmPossibleSays(H().pl, H().step)[0]); hmPaint(); },
    async lostrow(){ await critRisky(); H().lostF = {i: null, pod: 'home', others: 'keep'}; hmPaint(); },
    async group(){   // H296 says more than 50%: two Megathrons out together, answered; the step coming is both back in
      reset({link: RRJ.E, st: 'stable'}); await ready(); hmGo(); hmPaint(); hmSay('stable'); hmPaint();
      H().lostF = {i: 1, pod: 'home', others: 'keep'}; hmPaint(); await wait(() => { const s = hmShipOf({hull: 'Capsule'}); return s && !s.bad; }); hmPaint(); },
    async part(){ await scenes.group(); rrLost(); hmPaint(); },
    async replace(){   // a ship lost, then a replacement added on the far side with Change → + Ship (its side asked)
      await scenes.group(); H().lostF = {i: 1, pod: 'no', others: 'new'}; rrLost(); hmPaint();
      hmClick(document.querySelector('[data-hm=edit]'));
      hmClick(document.querySelector('[data-hm=add]')); const k = H().ships.length - 1; H().ships[k] = {hull: 'Buzzard', nw: true, at: H().prev.fin === 'this' ? 'other' : 'this'}; hmPaint();
      await wait(() => { const s = hmShipOf(H().ships[k]); return s && !s.bad; }); hmPaint(); },
    async lostfin(){ await critRisky(); H().lostF = {i: 2, pod: 'home', others: 'keep'}; rrLost(); hmPaint(); },
    async reload(){ await critRisky(); sessionStorage.setItem('rrReload', '1'); location.reload(); },
  };
  window.RRscene = async (k) => { switchTab('wh'); await scenes[k](); window.__RRSCENE = k; };
  function bar(){
    const b = document.createElement('div'); b.id = 'rrBar';
    b.innerHTML = '<b>MOCKUP</b>' + [['crit', 'Crit, no safe jump'], ['addf', '+ Finisher'], ['two', 'Two finishers'], ['undo', 'Undo the add'], ['roll', 'Roll, risky'], ['list', 'Saved runs'], ['runs', 'Saved runs (in a run)'], ['del', 'Delete a run'], ['done', 'Finished run'], ['full', 'Storage full'], ['lostrow', 'Ship lost'], ['group', 'Lost in a group step'], ['part', 'Part of a step + pod'], ['replace', 'Replacement ship'], ['lostfin', 'Finisher lost'], ['reload', 'Reload the page']]
      .map(([k, t]) => `<button type="button" data-s="${k}">${t}</button>`).join('') + '<button type="button" class="rr-fold" data-s="fold" aria-label="Fold the bar">⇕</button>';
    b.addEventListener('click', (e) => { const s = e.target.closest('button') && e.target.closest('button').dataset.s; if(!s) return; if(s === 'fold'){ b.classList.toggle('fold'); return; } RRscene(s); });
    const css = document.createElement('style');
    css.textContent = '#rrBar{position:fixed; left:8px; bottom:8px; z-index:99; display:flex; flex-wrap:wrap; gap:6px; align-items:center; max-width:calc(100% - 16px); padding:6px 8px; background:#2a1e05; border:1px solid var(--amber); border-radius:6px; font:12px var(--sans); color:var(--amber);} #rrBar button{min-height:28px; padding:2px 8px;} #rrBar.fold button:not(.rr-fold){display:none;}';
    document.head.appendChild(css); document.body.appendChild(b);
    if(innerWidth < 600) b.classList.add('fold');
  }
  (async () => { try{
    await wait(() => typeof whTable === 'function' && typeof hmState === 'function' && typeof rrRead === 'function' && document.readyState !== 'loading');
    stubs();
    const again = sessionStorage.getItem('rrReload'); sessionStorage.removeItem('rrReload');
    if(!again){ try{ localStorage.removeItem('tvWhMass'); localStorage.removeItem('tvWhMassRuns'); }catch(e){} }
    switchTab('wh'); whMake(); await wait(() => whS && whS.el);
    if(!again){ seed(); bar(); await RRscene('crit'); }
    else { const T = whTable(), pick = (cls, skip = 0) => { let n = 0; for(let i = 0; i < T.ids.length; i++) if(T.cls[i] === cls && /^J\d{6}$/.test(T.names[i]) && n++ === skip) return T.ids[i]; return null; };
      window.RRJ = {A: pick('2', 3), C: pick('3', 5), E: pick('5', 2), RENS}; bar(); whSelect(RRJ.A); whPop('mass'); await sleep(300); hmPaint(); window.__RRSCENE = 'reloaded'; }
    await sleep(300);
    window.__MKREADY = true;
  }catch(e){ window.__MKERR = String(e && e.stack || e); } })();
})();
