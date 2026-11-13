(() => {
  const wait = (f, ms = 15000) => new Promise((res, rej) => { const t0 = Date.now(); const k = () => { let v; try{ v = f(); }catch(e){ v = null; } if(v) res(v); else if(Date.now() - t0 > ms) rej(new Error('timeout')); else setTimeout(k, 100); }; k(); });
  (async () => { try{
    const tab = await wait(() => document.querySelector('#tabBtnIntel')); tab.click();
    const f = await wait(() => document.querySelector('[data-it-act="folder"]')); f.click();
    const sw = await wait(() => { const l = document.querySelector('#intelSwLabel'); return l && document.querySelector('[data-it-me]:checked') ? l : null; });
    if(!document.querySelector('#intelSw').checked) sw.click();
    if(matchMedia('(max-width: 599px)').matches){ const nv = await wait(() => document.querySelector('[data-it-nv="map"]')); nv.click(); }
    await wait(() => typeof itm !== 'undefined' && itm.el && itm.el.isConnected && itm.box.clientWidth > 0 && itm.D);
    await new Promise(r => setTimeout(r, 1500)); itMapRefresh(true);
    // the MOCKUP bar (bottom left): what to try, and Intel settings
    const bar = document.createElement('div');
    bar.style.cssText = 'position:fixed;left:8px;bottom:8px;z-index:9999;max-width:min(520px,calc(100vw - 16px));padding:6px 10px;border:1px solid #e4b5ff;border-radius:6px;background:rgba(12,16,20,.95);color:#e4b5ff;font:600 12px/1.4 system-ui,sans-serif;display:flex;flex-wrap:wrap;gap:6px;align-items:center';
    bar.innerHTML = '<span>MOCKUP · search top left of the map · right-click a system (phone: press it) · routes follow Intel settings → Routes</span><button type="button" data-mk="set" style="min-height:30px;font:600 12px system-ui;background:#1d2731;color:#e4b5ff;border:1px solid #e4b5ff;border-radius:4px;padding:0 8px;cursor:pointer">Intel settings</button>';
    bar.addEventListener('click', (e) => { if(e.target.closest('[data-mk="set"]')){ const g = document.querySelector('#intelPanel .it-gear'); if(g){ g.click(); setTimeout(() => { const b = document.querySelector('[data-rp-box]'); if(b) b.scrollIntoView({block: 'center'}); }, 300); } } });
    document.body.appendChild(bar);
    window.__MKREADY = true;
  }catch(e){ window.__MKERR = String(e); } })();
})();
