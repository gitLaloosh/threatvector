// Opens Intel, picks the mock log folder, turns Intel on, then shows the MOCKUP bar. Scenes: the menu on a system (no Home yet), Home set
// with its route, centered on Home, you in Home, zoomed out, zoomed in, the hover, a phone's tooltip buttons.
(() => {
  const wait = (f, ms = 20000) => new Promise((res, rej) => { const t0 = Date.now(); const k = () => { let v; try{ v = f(); }catch(e){ v = null; } if(v) res(v); else if(Date.now() - t0 > ms) rej(new Error('timeout')); else setTimeout(k, 100); }; k(); });
  const HOME_ID = 30000736;   // KOG-TA, a few jumps from C-J6MT
  const idx = (id) => itGraphGet().at.get(id);
  window.HOscene = async (k) => {
    itRpMenuClose(false); itMapTip(-1); itm.pinned.clear();
    if(k !== 'none') { HO.id = k === 'here' ? 30000772 : HOME_ID; HO.route = k === 'route' || k === 'routeout' || k === 'phone' || k === 'center'; } else { HO.id = 0; HO.route = false; }
    hoCache.key = ''; hoSave(); hoRailPaint(); itMapRefresh(true); itMapLegend();
    await new Promise(r => setTimeout(r, 150));
    if(k === 'center'){ itMapCenter(false); for(let n = 0; n < 2; n++) itMapZoom(itm.W / 2, itm.H / 2, 1.6); hoCenter(); }
    if(k === 'routeout'){ for(let n = 0; n < 3; n++) itMapZoom(itm.W / 2, itm.H / 2, 0.5); }
    if(k === 'route' || k === 'menu' || k === 'tip' || k === 'here'){ for(let n = 0; n < 2; n++) itMapZoom(itm.W / 2, itm.H / 2, 1.6); }
    itMapDraw();
    if(k === 'none' || k === 'menu'){ const i = idx(HOME_ID); const p = HOpos(i); itRpMenuOpen(i, p[0] + 10, p[1] + 10); }
    if(k === 'here'){ const i = itm.home; const p = HOpos(i); itMapTip(i, p[0], p[1]); }
    if(k === 'phone'){ itm.pinned.add(30000774); itMapRefresh(true); itMapDraw(); }
    if(k === 'tip' || k === 'phone'){ const i = idx(30000774); const p = HOpos(i); itMapTip(i, p[0], p[1]); }
  };
  window.HOpos = (i) => [itm.Q[2 * i], itm.Q[2 * i + 1]];
  function bar(){
    const b = document.createElement('div'); b.id = 'hoBar';
    b.innerHTML = '<b>MOCKUP</b>' + [['none', 'Menu: no Home yet'], ['menu', 'Menu on Home'], ['route', 'Home + route'], ['center', 'Centered on Home'], ['tip', 'Hover'], ['routeout', 'Zoomed out'], ['here', 'You in Home'], ['phone', 'Phone tooltip']]
      .map(([k, t]) => `<button type="button" data-s="${k}">${t}</button>`).join('') + '<button type="button" class="ho-fold" data-s="fold" aria-label="Fold the bar">⇕</button>';
    b.addEventListener('click', (e) => { const s = e.target.closest('button') && e.target.closest('button').dataset.s; if(!s) return; if(s === 'fold'){ b.classList.toggle('fold'); return; } HOscene(s); });
    const css = document.createElement('style');
    css.textContent = '#hoBar{position:fixed; left:8px; bottom:8px; z-index:99; display:flex; flex-wrap:wrap; gap:6px; align-items:center; max-width:calc(100% - 16px); padding:6px 8px; background:#2a1e05; border:1px solid var(--amber); border-radius:6px; font:12px var(--sans); color:var(--amber);} #hoBar button{min-height:28px; padding:2px 8px;} #hoBar.fold button:not(.ho-fold){display:none;}';
    document.head.appendChild(css); document.body.appendChild(b);
    if(innerWidth < 600) b.classList.add('fold');
  }
  (async () => { try{
    const tab = await wait(() => document.querySelector('#tabBtnIntel')); tab.click();
    const f = await wait(() => document.querySelector('[data-it-act="folder"]')); f.click();
    const sw = await wait(() => { const l = document.querySelector('#intelSwLabel'); return l && document.querySelector('[data-it-me]:checked') ? l : null; });
    if(!document.querySelector('#intelSw').checked) sw.click();
    await wait(() => typeof itm !== 'undefined' && itm.el && itm.el.isConnected && itm.box.clientWidth > 0 && itm.D && itSysNamesReady());
    await new Promise(r => setTimeout(r, 800));
    try{ localStorage.removeItem('tvHome'); }catch(e){}
    bar(); hoRailPaint(); itMapDraw();
    window.__MKREADY = true;
  }catch(e){ window.__MKERR = String(e && e.stack || e); } })();
})();
