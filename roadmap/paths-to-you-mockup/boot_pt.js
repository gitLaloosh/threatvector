(() => {
  const wait = (f, ms = 15000) => new Promise((res, rej) => { const t0 = Date.now(); const k = () => { let v; try{ v = f(); }catch(e){ v = null; } if(v) res(v); else if(Date.now() - t0 > ms) rej(new Error('timeout')); else setTimeout(k, 100); }; k(); });
  (async () => { try{
    const tab = await wait(() => document.querySelector('#tabBtnIntel')); tab.click();
    const f = await wait(() => document.querySelector('[data-it-act="folder"]')); f.click();
    const sw = await wait(() => { const l = document.querySelector('#intelSwLabel'); return l && document.querySelector('[data-it-me]:checked') ? l : null; });
    if(!document.querySelector('#intelSw').checked) sw.click();
    if(matchMedia('(max-width: 599px)').matches){ const nv = await wait(() => document.querySelector('[data-it-nv="map"]')); nv.click(); }
    await wait(() => typeof itm !== 'undefined' && itm.el && itm.el.isConnected && itm.box.clientWidth > 0 && itm.D);
    await new Promise(r => setTimeout(r, 1500)); itMapRefresh(true); itMapFilterSet('paths');
    window.__MKREADY = true;
  }catch(e){ window.__MKERR = String(e); } })();
})();
