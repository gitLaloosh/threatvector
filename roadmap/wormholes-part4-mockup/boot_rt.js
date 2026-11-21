// Opens Intel with the made-up log folder, seeds a made-up chain (CCP's own wormhole systems picked by class and effect), opens the
// Wormholes tab's Routes panel and shows the MOCKUP bar. Everything is made up; the chain's k-space ends are C-J6MT, Tama and Rens.
(() => {
  const wait = (f, ms = 30000) => new Promise((res, rej) => { const t0 = Date.now(); const k = () => { let v; try{ v = f(); }catch(e){ v = null; } if(v) res(v); else if(Date.now() - t0 > ms) rej(new Error('timeout')); else setTimeout(k, 100); }; k(); });
  const pick = (cls, eff, skip = 0) => { const T = whTable(); let n = 0; for(let i = 0; i < T.ids.length; i++) if(T.cls[i] === cls && T.eff[i] === eff && /^J\d{6}$/.test(T.names[i]) && n++ === skip) return T.ids[i]; return null; };
  const K = {cj: 30000772, tama: 30002813, rens: 30002510};
  const SCAN = [['TUV-907', 'Cosmic Signature', 'Wormhole', 'Unstable Wormhole', '100.0%'], ['KLM-552', 'Cosmic Signature', '', '', '0.0%'],
    ['QRS-210', 'Cosmic Signature', 'Data Site', 'Unsecured Perimeter Information Center', '100.0%'], ['XYZ-789', 'Cosmic Signature', 'Gas Site', 'Sizeable Perimeter Reservoir', '100.0%'],
    ['DEF-404', 'Cosmic Signature', '', '', '12.5%'], ['NOP-318', 'Cosmic Anomaly', 'Combat Site', 'Perimeter Ambush Point', '100.0%'],
    ['GHI-611', 'Cosmic Signature', 'Relic Site', 'Forgotten Perimeter Coronation Platform', '100.0%'], ['ABC-123', 'Cosmic Signature', 'Wormhole', 'Unstable Wormhole', '100.0%'],
    ['RST-777', 'Cosmic Signature', 'Data Site', 'Unsecured Perimeter Comms Relay', '62.0%']].map(r => [r[0], r[1], r[2], r[3], r[4], '4.2 AU'].join('\t')).join('\n');
  function seed(){
    const A = pick('3', 'p'), B = pick('5', 'w'), C = pick('2', '-', 7); window.RTJ = {A, B, C};
    const t0 = Date.now() - 50 * 60e3, path = [K.cj, A, B, K.tama, B, A, C, K.rens, C, A, B];
    path.forEach((id, i) => whSeen(id, t0 + i * 4 * 60e3, false));
    const S = whState(), L = (a, b) => whLinkOf(a, b);
    Object.assign(L(A, B), {mass: 'critical'}); Object.assign(L(B, K.tama), {life: 'eol'}); Object.assign(L(C, K.rens), {size: 'medium'});
    whEndSet(L(K.cj, A), K.cj, 'WXY-301', ''); whEndSet(L(K.cj, A), A, 'PQR-552', 'K162');
    whEndSet(L(A, B), A, 'MNO-118', 'H296'); whEndSet(L(A, B), B, 'ABC-123', 'K162');
    whEndSet(L(B, K.tama), B, 'TUV-907', 'K162'); whEndSet(L(B, K.tama), K.tama, 'RZL-429', '');
    /* the A side of A–C has no ID recorded (the owner: "sig id is useful if it was recorded but not required") */ whEndSet(L(A, C), C, 'HIJ-505', 'K162');
    whEndSet(L(C, K.rens), C, 'BCD-220', ''); whEndSet(L(C, K.rens), K.rens, 'EFG-913', '');
    S.mk[A] = {st: 'home', tag: 'HOME', lock: true};
    whSave(); whMkSave(); whEndSave();
    S.sg.sort = {k: 'ty', d: 1};   // Q6: Type for everyone once
    whScanApply(B, SCAN); whP3(B).res = null;
    S.drawKey = '';
    RT.pins = [30000142, 30002187, 30004759, C]; RT.key = '';   // pinned: Jita, Amarr, 1DQ1-A (a long route: its strip runs to two lines) and the C2
  }
  const hov = (rowSel, pick) => setTimeout(() => { const rows = [...document.querySelectorAll('#whPnRt .rt-row')], r = rows.find(rowSel); const qs = r ? [...r.querySelectorAll('.rt-q')] : []; const q = pick(qs); if(q) q.dispatchEvent(new PointerEvent('pointerover', {bubbles: true, pointerType: 'mouse'})); }, 400);
  const inChain = () => { if(whIsJ(whS.last)) return; whSeen(RTJ.B, Date.now(), false); };
  const scenes = {
    routes(){ inChain(); RT.from = null; switchTab('wh'); whSelect(RTJ.B); whPnSet('rt'); },
    hole(){ scenes.routes(); hov(r => /Jita/.test(r.textContent), qs => qs.find(q => q.classList.contains('hole'))); },
    gate(){ scenes.routes(); hov(r => /Jita/.test(r.textContent), qs => qs[qs.length - 1]); },
    long(){ scenes.routes(); hov(r => /1DQ1-A/.test(r.textContent), qs => qs[qs.length - 3]); setTimeout(() => { const r = [...document.querySelectorAll('#whPnRt .rt-row')].find(r => /1DQ1-A/.test(r.textContent)); if(r) r.scrollIntoView({block: 'center'}); }, 200); },
    here(){ inChain(); switchTab('wh'); whS.menu = RTJ.C; whMenuAct('route'); },
    out(){ RT.from = null; whSeen(K.tama, Date.now(), false); setTimeout(() => { switchTab('wh'); whSelect(K.tama); whPnSet('rt'); whS.pn = {}; whPaint(true); }, 100); },
    sigs(){ inChain(); switchTab('wh'); whS.secs.sigs = true; whPnSet('sum', true); whSelect(RTJ.B); setTimeout(() => { const e = document.querySelector('#whSec-sigs .wh-lt'); if(e) e.scrollIntoView({block: 'center'}); }, 250); },
    eff(){ inChain(); switchTab('wh'); whPnSet('sum', true); whSelect(RTJ.A); },
    intel(){ switchTab('intel'); setTimeout(() => { itWhListOpen(true); const g = itGraphGet(), i = g.at.get(K.cj); if(itm.Q && i !== undefined){ itm.view.tx += itm.W * 0.5 - itm.Q[2 * i]; itm.view.ty += itm.H * 0.3 - itm.Q[2 * i + 1]; itMapDraw(); } setTimeout(() => { const r = document.querySelector('.it-whp-rows'); if(r) r.scrollIntoView({block: 'end'}); }, 200); }, 300); },
    set(){ switchTab('intel'); setTimeout(() => { const g = document.querySelector('[data-it-act=gear]'); if(g && !it.pop) g.click(); setTimeout(() => { const c = document.querySelector('[data-rt-jw]'); if(c) c.scrollIntoView({block: 'center'}); }, 250); }, 300); },
  };
  window.RTscene = (k) => { scenes[k](); setTimeout(() => { if(whS){ whS.pn = {}; whS.drawKey = ''; } if(whTabNow() === 'wh') whPaint(true); }, 50); };
  function bar(){
    const b = document.createElement('div'); b.id = 'rtBar';
    b.innerHTML = '<b>MOCKUP</b><button type="button" data-s="routes">Routes</button><button type="button" data-s="hole">Hover a wormhole</button><button type="button" data-s="gate">Hover a gate</button><button type="button" data-s="long">Long route</button>'
      + '<button type="button" data-s="here">Routes from here</button><button type="button" data-s="out">Out in k-space</button><button type="button" data-s="sigs">Signatures by type</button><button type="button" data-s="eff">Effect numbers</button>'
      + '<button type="button" data-s="intel">Intel: list and ring</button><button type="button" data-s="set">Intel settings</button><button type="button" class="rt-fold" data-s="fold" aria-label="Fold the bar">⇕</button>';
    b.addEventListener('click', (e) => { const s = e.target.closest('button') && e.target.closest('button').dataset.s; if(!s) return; if(s === 'fold'){ b.classList.toggle('fold'); return; } RTscene(s); });
    document.body.appendChild(b);
    if(innerWidth < 600) b.classList.add('fold');
  }
  (async () => { try{
    const tab = await wait(() => document.querySelector('#tabBtnIntel')); tab.click();
    const f = await wait(() => document.querySelector('[data-it-act="folder"]')); f.click();
    const sw = await wait(() => { const l = document.querySelector('#intelSwLabel'); return l && document.querySelector('[data-it-me]:checked') ? l : null; });
    if(!document.querySelector('#intelSw').checked) sw.click();
    await wait(() => typeof itm !== 'undefined' && itm.el && itm.el.isConnected && itm.box.clientWidth > 0 && itm.D && itSysNamesReady());
    await new Promise(r => setTimeout(r, 600));
    seed(); bar();
    RTscene('routes');
    await new Promise(r => setTimeout(r, 600));
    window.__MKREADY = true;
  }catch(e){ window.__MKERR = String(e && e.stack || e); } })();
})();
