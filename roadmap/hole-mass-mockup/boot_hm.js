// Seeds a made-up chain (CCP's own wormhole systems picked by class), opens the Wormholes tab and the Mass panel, and shows the MOCKUP bar.
// Home is a C2 (B274 static to Rens), a K162 from a C3 (the far side's type D382 known), a K162 from a C5 (far side not known).
(() => {
  const wait = (f, ms = 30000) => new Promise((res, rej) => { const t0 = Date.now(); const k = () => { let v; try{ v = f(); }catch(e){ v = null; } if(v) res(v); else if(Date.now() - t0 > ms) rej(new Error('timeout')); else setTimeout(k, 100); }; k(); });
  const RENS = 30002510;
  function seed(){
    const T = whTable(), pick = (cls, skip = 0) => { let n = 0; for(let i = 0; i < T.ids.length; i++) if(T.cls[i] === cls && /^J\d{6}$/.test(T.names[i]) && n++ === skip) return T.ids[i]; return null; };
    const A = pick('2', 3), C = pick('3', 5), E = pick('5', 2); window.HMJ = {A, C, E, RENS};
    const t0 = Date.now() - 50 * 60e3; [RENS, A, C, A, E, A].forEach((id, i) => whSeen(id, t0 + i * 4 * 60e3, false));
    const L = (a, b) => whLinkOf(a, b);
    whEndSet(L(A, RENS), A, 'RZL-429', 'B274'); whEndSet(L(A, RENS), RENS, 'TUV-907', 'K162');
    whEndSet(L(A, C), A, 'ABC-123', 'K162'); whEndSet(L(A, C), C, 'QRS-210', 'D382'); L(A, C).mass = 'reduced';
    whEndSet(L(A, E), A, 'MNO-118', 'K162');
    const S = whState(); S.mk[A] = {st: 'home', tag: 'HOME', lock: true};
    whSave(); whMkSave(); whEndSave(); S.drawKey = '';
  }
  const linkOf = (b) => whLinkOf(HMJ.A, b);
  const answer = (...ks) => ks.forEach(k => { hmPaint(); hmSay(k); });
  const reset = (o = {}) => { HM.back = []; HM.prev = null; HM.ships = o.ships || [{fit: 'mf1'}, {fit: 'mf3'}]; HM.goal = o.goal || 'roll'; HM.fin = o.fin || 'this'; HM.open = true; HM.pl = null; HM.ask = null;
    linkOf(RENS).mass = ''; whSave(); whSelect(HMJ.A); whPopClose(); whPop('mass'); if(o.link){ HM.link = linkOf(o.link); HM.ty = ''; hmFromLink(HMJ.A); } if(o.st) HM.st = o.st; hmPaint(); };
  const scenes = {
    panel(){ reset(); },
    steps(){ reset({st: 'fresh'}); hmGo(); hmPaint(); },
    next(){ reset({st: 'fresh'}); hmGo(); answer('stable', 'stable', 'stable'); HM.pl.ships.forEach(s => { for(const d in s.last) if(s.last[d]) s.last[d] -= 6 * 60e3; }); hmPaint(); },
    pol(){ reset({st: 'fresh'}); hmGo(); answer('stable', 'stable', 'stable'); hmPaint(); },
    risky(){ reset({st: 'fresh', ships: [{fit: 'mf1'}]}); hmGo(); answer('stable', 'stable', 'stable', 'reduced', 'reduced', 'critical'); hmPaint(); },
    k162(){ reset({link: HMJ.E}); },
    crit(){ reset({link: HMJ.C, goal: 'crit', ships: [{fit: 'mf2'}, {fit: 'mf3'}]}); hmGo(); hmPaint(); },
    other(){ reset({st: 'fresh', fin: 'other', ships: [{fit: 'mf1'}, {fit: 'mf2'}]}); hmGo(); hmPaint(); },
    hull(){ reset({ships: [{hull: 'Typhoon'}, {fit: 'mf3'}]}); },
    group(){ reset({st: 'fresh', ships: [{fit: 'mf1'}, {fit: 'mf1'}, {fit: 'mf2'}]}); hmGo(); hmPaint(); },
    group3(){ scenes.group(); answer('stable', 'reduced', 'reduced'); HM.pl.ships.forEach(s => { for(const d in s.last) if(s.last[d]) s.last[d] -= 6 * 60e3; }); hmPaint(); },
    fin(){ reset({st: 'fresh', ships: [{fit: 'mf1'}, {fit: 'mf1'}, {fit: 'mf2', fin: true}]}); hmGo(); hmPaint(); },
    fin5(){ scenes.fin(); answer('stable', 'reduced', 'reduced', 'reduced', 'reduced'); HM.pl.ships.forEach(s => { for(const d in s.last) if(s.last[d]) s.last[d] -= 6 * 60e3; }); hmPaint(); },
    heron(){ reset({link: HMJ.C, ships: [{fit: 'mf1'}, {fit: 'mf3', fin: true}]}); hmGo(); hmPaint(); },
    addship(){ scenes.risky(); HM.prev = HM.pl; HM.pl = null; HM.ships.push({fit: 'mf2'}); hmPaint(); },
    carried(){ scenes.addship(); hmGo(true); hmPaint(); },
    rolled(){ reset({st: 'fresh', ships: [{fit: 'mf1'}, {fit: 'mf2'}]}); hmGo(); answer('stable', 'stable', 'stable', 'reduced', 'reduced', 'reduced', 'critical', 'gone'); hmPaint(); },
  };
  window.HMscene = (k) => { switchTab('wh'); scenes[k](); };
  function bar(){
    const b = document.createElement('div'); b.id = 'hmBar';
    b.innerHTML = '<b>MOCKUP</b>' + [['panel', 'Panel'], ['steps', 'Steps'], ['next', 'After 3 jumps'], ['pol', 'Polarized'], ['group', '2 Megathrons + Phobos'], ['group3', '… after 3 steps'], ['fin', 'Phobos as finisher'], ['fin5', '… after 5 steps'], ['heron', 'Heron as finisher, <50%'], ['risky', 'No safe jump'], ['k162', 'K162 asks'], ['crit', 'Crit it'], ['other', 'Finish on the other side'], ['addship', 'Add a ship mid-way'], ['carried', 'Carry on'], ['hull', 'Typed hull'], ['rolled', 'Rolled']]
      .map(([k, t]) => `<button type="button" data-s="${k}">${t}</button>`).join('') + '<button type="button" class="hm-fold" data-s="fold" aria-label="Fold the bar">⇕</button>';
    b.addEventListener('click', (e) => { const s = e.target.closest('button') && e.target.closest('button').dataset.s; if(!s) return; if(s === 'fold'){ b.classList.toggle('fold'); return; } HMscene(s); });
    const css = document.createElement('style');
    css.textContent = '#hmBar{position:fixed; left:8px; bottom:8px; z-index:99; display:flex; flex-wrap:wrap; gap:6px; align-items:center; max-width:calc(100% - 16px); padding:6px 8px; background:#2a1e05; border:1px solid var(--amber); border-radius:6px; font:12px var(--sans); color:var(--amber);} #hmBar button{min-height:28px; padding:2px 8px;} #hmBar.fold button:not(.hm-fold){display:none;}';
    document.head.appendChild(css); document.body.appendChild(b);
    if(innerWidth < 600) b.classList.add('fold');
  }
  (async () => { try{
    await wait(() => typeof whTable === 'function' && document.readyState !== 'loading');
    try{ localStorage.removeItem('tvWhMass'); }catch(e){}
    switchTab('wh'); whMake(); await wait(() => whS && whS.el);
    seed(); bar(); HMscene('panel');
    await new Promise(r => setTimeout(r, 400));
    window.__MKREADY = true;
  }catch(e){ window.__MKERR = String(e && e.stack || e); } })();
})();
