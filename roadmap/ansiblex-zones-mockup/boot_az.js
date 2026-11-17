// Opens Intel, picks the mock log folder, turns Intel on, reads the made-up sovereignty, fills the bridge list, shows the MOCKUP box.
(() => {
  const wait = (f, ms = 20000) => new Promise((res, rej) => { const t0 = Date.now(); const k = () => { let v; try{ v = f(); }catch(e){ v = null; } if(v) res(v); else if(Date.now() - t0 > ms) rej(new Error('timeout')); else setTimeout(k, 100); }; k(); });
  (async () => { try{
    const tab = await wait(() => document.querySelector('#tabBtnIntel')); tab.click();
    const f = await wait(() => document.querySelector('[data-it-act="folder"]')); f.click();
    const sw = await wait(() => { const l = document.querySelector('#intelSwLabel'); return l && document.querySelector('[data-it-me]:checked') ? l : null; });
    if(!document.querySelector('#intelSw').checked) sw.click();
    await wait(() => typeof itm !== 'undefined' && itm.el && itm.el.isConnected && itm.box.clientWidth > 0 && itm.D && itSysNamesReady());
    AZ.text = window.__MK.bridges;
    await AZ.read();
    await new Promise(r => setTimeout(r, 800));
    MKAZ.boot(); AZ.changed();
    // start zoomed in on you and the bridges (a few presses of +), so the curves read
    const h = itm.home, Q = itm.Q; if(h >= 0 && Q){ itMapZoom(Q[2 * h], Q[2 * h + 1], 4); const Q2 = itm.Q; itm.view.tx += itm.W * 0.45 - Q2[2 * h]; itm.view.ty += itm.H * 0.35 - Q2[2 * h + 1]; itMapDraw(); }
    window.__MKREADY = true;
  }catch(e){ window.__MKERR = String(e && e.stack || e); } })();
})();
