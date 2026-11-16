// After 058's boot (boot_stk.js): pastes a made-up bridge list, turns "Use jump bridges on the map" on, colours by Jumps, and adds the
// jump-bridge rows to the MOCKUP box. Every line uses EVE's public system names only; the structure names and ids are made up.
(() => {
  const LIST = [
    '8G-2FP » 8EF-58 - Mockup Bridge',              // EVE's structure name, as the game names a bridge
    '4M-QXK → F39H-1',                              // SMT's arrow
    '1042000001 3AE-CP → EUU-4N',                   // SMT's export: a structure id first (D8: digits ignored)
    '1042000002 EUU-4N → 3AE-CP',                   // the same bridge's other direction (D6: a dim row, counted once)
    'SHBF-V » WF4C-8 - Mockup Bridge\tMockup Coalition\tC-J6MT',   // a row copied with more columns, another system among them (D7)
    'EUU-4N » 0TYR-T',                              // warnings: EUU-4N on two lines, more than 5 LY
    'RERZ-L Mockup Nowhere',                        // refused: one system
    'RERZ-L MSG-BZ 78-0R6',                         // refused: three names and no separator
  ].join('\n');
  const wait = (f, ms = 30000) => new Promise((res, rej) => { const t0 = Date.now(); const k = () => { let v; try{ v = f(); }catch(e){ v = null; } if(v) res(v); else if(Date.now() - t0 > ms) rej(new Error('timeout')); else setTimeout(k, 100); }; k(); });
  (async () => { try{
    await wait(() => window.__MKREADY);
    it.set.bridges = LIST; it.set.bridgesOn = true; itWriteSet();
    JB.relay();
    itMapFilterSet('jumps');
    const box = document.querySelector('.mk-box'), r = document.createElement('div');
    r.innerHTML = `<div class="r"><span>Jump bridges:</span><button type="button" data-mkj="on">On</button><button type="button" data-mkj="off">Off</button></div>`
      + `<div class="r"><button type="button" data-mkj="set">Intel settings: Jump bridges box</button></div>`
      + `<div class="mk-note">Made-up list of 8 lines (5 bridges: 3 good, 1 counted with warnings, 1 a repeat; 2 refused). Hover 8EF-58 or F39H-1: the map counts the bridge, Near You doesn't.</div>`;
    box.appendChild(r);
    const paint = () => { for(const b of r.querySelectorAll('[data-mkj="on"],[data-mkj="off"]')) b.setAttribute('aria-pressed', String((b.dataset.mkj === 'on') === !!it.set.bridgesOn)); };
    JB.boxPaint = paint; paint();
    r.addEventListener('click', (e) => {
      const t = e.target.closest('[data-mkj]'); if(!t) return; const k = t.dataset.mkj;
      if(k === 'on' || k === 'off'){ it.set.bridgesOn = k === 'on'; itWriteSet(); JB.relay(); const c = document.querySelector('[data-it-jbon]'); if(c) c.checked = it.set.bridgesOn; paint(); }
      if(k === 'set'){ if(!box.classList.contains('fold')){ const f = box.querySelector('[data-mkb="fold"]'); if(f) f.click(); } if(!it.pop){ const g = document.querySelector('.it-gear[data-it-act="gear"]'); if(g) g.click(); } setTimeout(() => { const b = document.querySelector('.it-jb'); if(b) b.scrollIntoView({block: 'center'}); }, 300); }
    });
    window.__JBREADY = true;
  }catch(e){ window.__JBERR = String(e && e.stack || e); } })();
})();
