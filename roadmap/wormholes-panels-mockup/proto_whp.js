// MOCKUP prototype: the Wormholes tab's panels behind icons (Project doc claude/roadmap/wormholes-panels-plan.md).
// Runs after the real page's script. Everything in the chain is made up: wormhole systems picked by position from CCP's own table (INTEL_WH),
// no pilots, no corporations. "Proposed" moves System's body into a rule-B panel behind one rail button at the map's top left;
// "Today" puts it back. The owner's answers (2026-11-15): Q1 top left, Q2 only working panels, Q3 a click opens System, Q4 remembered (tvWhPanels),
// Q5 a phone sheet beside the rail, Q6 mockup.
(function(){
  'use strict';
  const PK = 'tvWhPanels';
  const ICONS = {
    a: ['Ringed planet', '<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="9" cy="9" r="4.4"/><path d="M3.1 11.6C1.2 13.2.9 14.5 1.7 15c1.6 1 6.4-1 10.3-4.4 3.9-3.4 5.6-6.9 4-7.7-.7-.4-2 0-3.5 1"/></svg>'],
    b: ['Star and orbit', '<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="9" cy="9" r="2.6" fill="currentColor" stroke="none"/><circle cx="9" cy="9" r="6.6" stroke-dasharray="2.2 2"/><circle cx="14.2" cy="4.9" r="1.6" fill="currentColor" stroke="none"/></svg>'],
    c: ['Info card', '<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><rect x="2.2" y="2.6" width="13.6" height="12.8" rx="1.6"/><path d="M5.2 6.4h7.6M5.2 9.2h7.6M5.2 12h4.4"/></svg>']
  };
  const css = `
  body.whp .wh-panels{display:none !important;} .wh-rail[hidden]{display:none !important;}
  body.whp .wh-box .wh-rail{top:46px; left:8px; right:auto;}
  body.whp .wh-pnl{position:absolute; z-index:4; top:46px; left:44px; bottom:8px; width:340px; box-sizing:border-box; display:flex; flex-direction:column; gap:8px; overflow:auto;
    padding:10px 12px 12px; background:var(--panel); border:1px solid var(--line); border-radius:6px; box-shadow:0 8px 24px rgba(0,0,0,.5); scrollbar-width:thin;}   /* rule B */
  body.whp .wh-pnl[hidden]{display:none;}
  body.whp .wh-pnlh{display:flex; align-items:baseline; gap:8px; flex:none;} body.whp .wh-pnlh h3{margin:0; font:700 14px var(--sans); color:var(--heading);}
  body.whp .wh-pnl .wh-pnb{padding:0; order:0; max-height:none; overflow:visible; border:0;}
  body.whp .wh-gsel{left:44px;} body.whp .wh-box:has(.wh-pnl:not([hidden])) .wh-gsel{left:392px;}
  @media (max-width:899px){ body.whp .wh-box .wh-rail, body.whp .wh-pnl{top:90px;} body.whp .wh-gsel{top:90px;} }
  @media (max-width:599px){
    body.whp .wh-box .wh-rail{top:60px; left:8px;} body.whp .wh-box .wh-rail button{width:44px; height:44px; min-height:44px;}
    body.whp .wh-pnl{top:60px; left:60px; right:8px; bottom:8px; width:auto; padding:8px 10px 10px;}
    body.whp .wh-topl{top:auto; bottom:8px; left:8px; right:150px;} body.whp .wh-mini{top:auto; bottom:10px;}
    body.whp .wh-msg, body.whp .wh-gsel, body.whp .wh-box:has(.wh-pnl:not([hidden])) .wh-gsel{left:60px; top:60px; max-width:calc(100% - 128px);}
    body.whp .wh-box:has(.wh-pnl:not([hidden])) .wh-mini, body.whp .wh-box:has(.wh-pnl:not([hidden])) .wh-topl{display:none;}
  }
  #whpBar{position:fixed; z-index:99999; left:50%; transform:translateX(-50%); top:8px; display:flex; flex-wrap:wrap; gap:6px; align-items:center; max-width:calc(100vw - 24px); box-sizing:border-box;
    padding:8px 10px; border:1px dashed var(--amber); border-radius:6px; background:#12171c; color:var(--text); font:12px var(--sans); box-shadow:0 6px 20px rgba(0,0,0,.6);}
  #whpBar b{color:var(--amber); letter-spacing:.5px;} #whpBar button{min-height:28px; padding:0 9px; font-size:12px;} #whpBar button[aria-pressed="true"]{background:var(--amber); color:#1b1306;}
  #whpBar.fold > :not(.whp-fold){display:none;} @media (max-width:599px){ #whpBar{left:8px; right:8px; transform:none;} #whpBar button{min-height:36px;} }
  `;
  let mode = 'proposed', icon = 'a';
  const st = () => { try{ const o = JSON.parse(localStorage.getItem(PK) || 'null'); return o && o.v === 1 && o.open === 'sum' ? 'sum' : ''; }catch(e){ return ''; } };
  const save = (open) => { try{ localStorage.setItem(PK, JSON.stringify({v: 1, open})); }catch(e){ } };

  function seed(){   // a made-up chain: CCP's wormhole systems picked by position in the table, made-up statics and notes, no pilots
    if(localStorage.getItem('tvWhChain')) return;
    const T = whTable(), J = T.names.filter(n => /^J\d{6}$/.test(n)), pick = [40, 310, 655, 902, 1210, 1488, 1733, 2011].map(i => whIdOf(J[i % J.length])), th = whIdOf('Thera');
    const t0 = Date.now() - 3 * 3600e3, path = [pick[0], pick[1], pick[2], pick[1], pick[3], pick[4], pick[3], pick[5], pick[1], pick[6], th, pick[6], pick[7], pick[6], pick[1]];
    path.forEach((id, i) => whSeen(id, t0 + i * 60e3, false));
    const S = whState(); S.st.sys[pick[0]].statics = 'H296 D845'; S.st.sys[pick[0]].notes = 'made-up note'; S.st.sys[pick[1]].statics = 'N062';
    S.st.links.forEach((l, i) => { if(i === 0){ l.sig = 'ABC-123'; l.type = 'H296'; } if(i === 2) l.life = 'eol'; });
    S.mk[pick[0]] = {st: 'home', tag: 'HOME', lock: true}; S.mk[pick[4]] = {st: 'warning'};
    whSave(); whMkSave(); S.drawKey = '';
  }
  function ensure(){
    const S = whS; if(!S || !S.el) return null;
    const box = S.el.querySelector('.wh-box'); let rail = box.querySelector('.wh-rail'), pnl = box.querySelector('#whPnSum');
    if(!rail){
      rail = document.createElement('div'); rail.className = 'it-map-rail wh-rail'; rail.setAttribute('role', 'toolbar'); rail.setAttribute('aria-label', 'Map panels');
      rail.innerHTML = '<button type="button" data-whp-rp="sum" aria-controls="whPnSum" aria-pressed="false"></button>';
      pnl = document.createElement('section'); pnl.className = 'wh-pnl'; pnl.id = 'whPnSum'; pnl.setAttribute('aria-label', 'System'); pnl.hidden = true;
      pnl.innerHTML = '<div class="wh-pnlh"><h3>System</h3></div>';
      box.querySelector('.wh-panels').after(rail, pnl);
      rail.querySelector('button').addEventListener('click', () => open(pnl.hidden, true));
    }
    return {box, rail, pnl, btn: rail.querySelector('button')};
  }
  function paint(){
    const E = ensure(); if(!E) return;
    const body = whS.el.querySelector('[data-pnb="sum"]'), home = whS.el.querySelector('.wh-pn[data-pn="sum"]');
    if(mode === 'proposed'){ if(body.parentNode !== E.pnl) E.pnl.appendChild(body); if(body.hidden) body.hidden = false; }   // M.phoneInit (a phone's first draw) shuts every body: the plan drops it
    else if(body.parentNode !== home){ home.appendChild(body); body.hidden = home.querySelector('.wh-pnh').getAttribute('aria-expanded') !== 'true'; }
    E.rail.hidden = E.pnl.hidden = mode !== 'proposed';
    if(mode === 'proposed') E.pnl.hidden = st() !== 'sum' || !Object.keys(whS.st.sys).length;
    const on = !E.pnl.hidden, n = whFocus(), nm = n === null ? '' : whName(n);
    const t = `System${nm ? ': ' + nm : ''} (press to ${on ? 'hide' : 'show'} the panel)`;
    if(E.btn.title !== t){ E.btn.title = t; E.btn.setAttribute('aria-label', t); }
    if(E.btn.getAttribute('aria-pressed') !== String(on)) E.btn.setAttribute('aria-pressed', String(on));
    if(E.btn.dataset.icon !== icon){ E.btn.dataset.icon = icon; E.btn.innerHTML = ICONS[icon][1]; }
  }
  function open(want, fit){
    if(mode !== 'proposed') return;
    save(want ? 'sum' : ''); paint();
    if(want){ whS.pn = {}; whPanels(); }
    if(fit && whS.M && whS.M.cam) whDraw();
  }
  // the page's own functions, wrapped (classic-script globals): the panel's name and button follow every paint; Fit and centring use the uncovered part
  const oPanels = whPanels; whPanels = function(){ oPanels(); paint(); };
  const oFree = whFree;
  whFree = function(){
    if(mode !== 'proposed') return oFree();
    const v = whView(), box = whS.el.querySelector('.wh-box').getBoundingClientRect(), p = whS.el.querySelector('#whPnSum'), r = {l: 0, t: 48, r: v.w, b: v.h};
    if(p && !p.hidden){ const q = p.getBoundingClientRect(); if(q.width && v.w - (q.right - box.left + 4) >= 96) r.l = q.right - box.left + 4; }   // a phone's sheet: the whole map (as itMapFree under 96 px)
    return {...r, w: r.r - r.l, h: r.b - r.t};
  };
  // Q3: a click on a system opens System (a drag, Shift or the menu doesn't): the page's pointerup calls whSelect only for a click
  let fromMap = false;
  const oSel = whSelect; whSelect = function(id){ oSel(id); if(fromMap && mode === 'proposed' && st() !== 'sum') open(true, false); };
  function wire(){
    const box = whS && whS.el && whS.el.querySelector('.wh-box'); if(!box || box.dataset.whp) return; box.dataset.whp = '1';
    box.addEventListener('pointerup', (ev) => { fromMap = ev.target.matches('.wh-box > canvas:not(.wh-mini)') && !ev.shiftKey; setTimeout(() => { fromMap = false; }, 0); }, true);
  }
  function bar(){
    const b = document.createElement('div'); b.id = 'whpBar';
    b.innerHTML = '<b>MOCKUP</b><button type="button" data-whp-m="today">Today</button><button type="button" data-whp-m="proposed">Proposed</button>'
      + '<span>Icon:</span>' + Object.entries(ICONS).map(([k, v]) => `<button type="button" data-whp-i="${k}" title="${v[0]}">${k.toUpperCase()}</button>`).join('')
      + '<button type="button" data-whp-x title="Forget the remembered panel and the chain">Reset</button><button type="button" class="whp-fold" data-whp-f title="Fold">–</button>';
    document.body.appendChild(b);
    const sync = () => { b.querySelectorAll('[data-whp-m]').forEach(x => x.setAttribute('aria-pressed', String(x.dataset.whpM === mode))); b.querySelectorAll('[data-whp-i]').forEach(x => x.setAttribute('aria-pressed', String(x.dataset.whpI === icon))); };
    b.addEventListener('click', (ev) => {
      const x = ev.target.closest('button'); if(!x) return;
      if(x.dataset.whpM){ mode = x.dataset.whpM; document.body.classList.toggle('whp', mode === 'proposed'); paint(); whS.drawKey = ''; whPaint(true); }
      if(x.dataset.whpI){ icon = x.dataset.whpI; paint(); }
      if('whpX' in x.dataset){ localStorage.removeItem(PK); localStorage.removeItem('tvWhChain'); localStorage.removeItem('tvWhMarks'); location.reload(); }
      if('whpF' in x.dataset){ b.classList.toggle('fold'); x.textContent = b.classList.contains('fold') ? '+' : '–'; }
      sync();
    });
    sync();
  }
  const s = document.createElement('style'); s.textContent = css; document.head.appendChild(s);
  document.body.classList.add('whp');
  seed();
  document.getElementById('tabBtnWh').click();
  whMake(); wire(); paint(); whS.drawKey = ''; whPaint(true); bar();
  window.__whp = {open, paint, mode: () => mode};
})();
