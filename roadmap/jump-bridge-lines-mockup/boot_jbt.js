// Opens Intel, picks the mock log folder, turns Intel on, pastes a made-up bridge list (EVE's public system names; the structure names made
// up), turns "Use jump bridges on the map" on and colours the map by Jumps; then shows the MOCKUP bar.
(() => {
  const LIST = ['8G-2FP » 8EF-58 - Mockup Bridge', '4M-QXK → F39H-1', '3AE-CP → EUU-4N', 'SHBF-V » WF4C-8 - Mockup Bridge'].join('\n');
  const wait = (f, ms = 30000) => new Promise((res, rej) => { const t0 = Date.now(); const k = () => { let v; try{ v = f(); }catch(e){ v = null; } if(v) res(v); else if(Date.now() - t0 > ms) rej(new Error('timeout')); else setTimeout(k, 100); }; k(); });
  (async () => { try{
    const tab = await wait(() => document.querySelector('#tabBtnIntel')); tab.click();
    const f = await wait(() => document.querySelector('[data-it-act="folder"]')); f.click();
    const sw = await wait(() => { const l = document.querySelector('#intelSwLabel'); return l && document.querySelector('[data-it-me]:checked') ? l : null; });
    if(!document.querySelector('#intelSw').checked) sw.click();
    await wait(() => typeof itm !== 'undefined' && itm.el && itm.el.isConnected && itm.box.clientWidth > 0 && itm.D && itSysNamesReady());
    await new Promise(r => setTimeout(r, 1000));
    it.set.bridges = LIST; it.set.bridgesOn = true; itWriteSet();
    itMapFilterSet('jumps'); itMapRefresh(true);
    JBT.bar();
    window.__MKREADY = true;
  }catch(e){ window.__MKERR = String(e && e.stack || e); } })();
})();
