// MOCKUP bar (not part of the design): Today / With this plan, and more wormhole lines to post into Intel
window.__MKSCAN = ['RZL-429\tCosmic Signature\tWormhole\tUnstable Wormhole\t100.0%\t4.21 AU', 'MKV-118\tCosmic Signature\t\t\t23.4%\t11.02 AU',
  'NOP-907\tCosmic Signature\tWormhole\tUnstable Wormhole\t100.0%\t8.56 AU', 'ABC-552\tCosmic Signature\tData Site\tUnsecured Perimeter Comms Relay\t100.0%\t2.10 AU',
  'TUV-310\tCosmic Anomaly\tCombat Site\tSerpentis Hideaway\t100.0%\t5.33 AU'].join('\n');
(() => {
  const LINES = [['Mk Gate Watcher', 'RERZ-L wormhole QDX-581 n110 eol'], ['Mk Scout Alt', '8G-2FP wh lmn c3 fresh'], ['Mk Scout Alt', 'C-J6MT wh RZL crit now'],
    ['Mk Gate Watcher', 'SHBF-V wh pqr-417']];
  let k = 0;
  const bar = document.createElement('div'); bar.className = 'mkbar';
  const off = !!window.__SIGOFF;
  bar.innerHTML = `<b>MOCKUP</b><span class="mkseg"><button type="button" data-mk="today" aria-pressed="${off}">Today</button><button type="button" data-mk="plan" aria-pressed="${!off}">With this plan</button></span>
    <button type="button" data-mk="post"></button><button type="button" data-mk="raw">Show the lines as typed</button><button type="button" data-mk="scan">Fill a sample probe scan</button>`;
  const upd = () => { const b = bar.querySelector('[data-mk="post"]'); b.textContent = k < LINES.length ? `Post: “${LINES[k][1]}”` : 'All lines posted'; b.disabled = k >= LINES.length; };
  bar.addEventListener('click', (ev) => {
    const b = ev.target.closest('button'); if(!b) return;
    if(b.dataset.mk === 'today' && !off){ location.hash = 'today'; location.reload(); }
    if(b.dataset.mk === 'plan' && off){ location.hash = ''; location.reload(); }
    if(b.dataset.mk === 'post' && k < LINES.length){ window.__MKintel(LINES[k][0], LINES[k][1]); k++; upd(); }
    if(b.dataset.mk === 'scan'){   // made-up IDs; the same tab-separated cells as the game's probe scanner rows
      const nv = document.querySelector('[data-it-nv="map"]'); if(nv && nv.offsetParent && nv.getAttribute('aria-pressed') !== 'true') nv.click();   // a phone: the map side
      setTimeout(() => { if(!itWhListShown()) itWhListOpen(true); }, 100);
      setTimeout(() => { const d = document.querySelector('.it-whp-scan'); if(!d) return; d.open = true; d.querySelector('textarea').value = window.__MKSCAN; d.scrollIntoView({block: 'center'}); }, 350);
    }
    if(b.dataset.mk === 'raw') document.querySelectorAll('.it-fd .it-rawt[aria-expanded="false"]').forEach(x => x.click());
  });
  upd();
  const st = document.createElement('style');
  st.textContent = `.mkbar{position:fixed; left:8px; bottom:8px; z-index:9999; display:flex; flex-wrap:wrap; gap:6px; align-items:center; max-width:calc(100vw - 16px); box-sizing:border-box; padding:6px 8px; border-radius:6px; background:#3a2a10; border:1px solid var(--amber); font:12px var(--sans); color:var(--heading);}
    .mkbar b{color:var(--amber); letter-spacing:.5px;} .mkbar button{font-size:12px; padding:4px 8px; min-height:30px;} .mkseg{display:inline-flex; gap:4px;} .mkbar [aria-pressed="true"]{background:var(--amber); color:#111;}`;
  document.head.appendChild(st); document.body.appendChild(bar);
})();
