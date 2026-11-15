(() => {
  const wait = (f, ms = 15000) => new Promise((res, rej) => { const t0 = Date.now(); const k = () => { let v; try{ v = f(); }catch(e){ v = null; } if(v) res(v); else if(Date.now() - t0 > ms) rej(new Error('timeout')); else setTimeout(k, 100); }; k(); });
  (async () => { try{
    const tab = await wait(() => document.querySelector('#tabBtnPilot')); tab.click();
    document.getElementById('pilotName').value = window.__MK.meName;
    currentPilotName = window.__MK.meName;
    window.__mkBar();
    await window.__mkRun();
    window.__MKREADY = true;
  }catch(e){ window.__MKERR = String(e && e.stack || e); } })();
})();
