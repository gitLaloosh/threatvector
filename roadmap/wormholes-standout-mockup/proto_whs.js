// Wormholes standing out on the Intel map's Wormholes filter (requirement 8, roadmap/wormhole-mapping-plan.md; the owner: "wormholes are
// getting lost in the chaos here", then "yes please" to options 1-4 together with 5 as a toggle). Loaded before the page; build_whs.py's
// patches call itMapWhBold / itMapWhBoldCol from itMapDraw and itMapLabels. On the Wormholes filter only; window.__WHS = false shows today's look.
//  1. everything else faded (patches): other reports' rings ~20%, no glow, the alert range's wash lighter, their labels, counts, ✕ and CLEAR hidden
//  2. the mark bolder (here): a filled disc in its colour with a glow and a ring; a Drifter pink (#ff5fbf) with a dashed ring (044's choice)
//  3. a slow pulse on a hole reported in the last 30 minutes (here, on its own canvas over the map; none when the device asks for less motion)
//  4. the labels: a filled pill in the hole's colour, and every wormhole inside "Map: within" named (patches)
//  5. optional: a "N wormholes" chip that steps the view through them, nearest first (here; window.__WHS5)
// The build (045) made the pulse CSS (transform and opacity) and reads the colours from the tokens; this is the mockup as the owner saw it.
window.__WHS = true; window.__WHS5 = false;
let whsCol = null;
function itMapWhBoldCol(w){
  if(!whsCol){ const v = getComputedStyle(document.documentElement).getPropertyValue('--it-wh').trim(); whsCol = [v || '#a98bd8', '#ff5fbf']; }
  return whsCol[w && w.drifter ? 1 : 0];
}
function itMapWhBold(c, x, y, w, big, r){
  const col = itMapWhBoldCol(w), dr = !!(w && w.drifter);
  c.save();
  if(!big){
    c.shadowColor = col; c.shadowBlur = 14; c.fillStyle = col; c.globalAlpha = 0.95;
    c.beginPath(); c.arc(x, y, 6, 0, 6.283); c.fill();
    c.shadowBlur = 0; c.globalAlpha = 1; c.lineWidth = 1.5; c.strokeStyle = '#0c1014'; c.stroke();   // a dark edge keeps the disc apart from a dot under it
    c.strokeStyle = col; c.lineWidth = 2; c.setLineDash(dr ? [3, 2.5] : []);
    c.beginPath(); c.arc(x, y, 10.5, 0, 6.283); c.stroke();
  } else {
    c.shadowColor = col; c.shadowBlur = 14; c.strokeStyle = col; c.lineWidth = 3;
    c.beginPath(); c.arc(x, y, r + 4, 0, 6.283); c.stroke();
    c.shadowBlur = 0; c.lineWidth = 1.5; c.setLineDash(dr ? [4, 3] : []);
    c.beginPath(); c.arc(x, y, r + 9, 0, 6.283); c.stroke();
  }
  c.restore();
}
// ---- 3: the pulse, on a canvas of its own over the map (the map itself redraws only on change)
(() => {
  const calm = matchMedia('(prefers-reduced-motion: reduce)');
  let ov = null, chip = null, step = -1, last = 0;
  const on = () => typeof itm !== 'undefined' && itm.cv && itm.cv.isConnected && itm.cv.offsetParent && itm.filter === 'wh' && window.__WHS !== false;
  function overlay(){
    if(ov && ov.parentNode === itm.cv.parentNode) return ov;
    ov = document.createElement('canvas'); ov.className = 'whs-pulse'; ov.setAttribute('aria-hidden', 'true');
    itm.cv.parentNode.appendChild(ov); return ov;
  }
  function frame(t){
    requestAnimationFrame(frame);
    if(typeof itm === 'undefined' || !itm.cv) return;
    chipPaint(t);
    const live = on() && itm.whPulse && itm.whPulse.length && !calm.matches;
    if(!live){ if(ov && ov.dataset.on){ ov.getContext('2d').clearRect(0, 0, ov.width, ov.height); delete ov.dataset.on; } return; }
    const o = overlay(), dpr = window.devicePixelRatio || 1, cv = itm.cv, w = cv.clientWidth, h = cv.clientHeight;
    if(o.width !== Math.round(w * dpr) || o.height !== Math.round(h * dpr)){ o.width = Math.round(w * dpr); o.height = Math.round(h * dpr); o.style.width = w + 'px'; o.style.height = h + 'px'; }
    o.style.left = cv.offsetLeft + 'px'; o.style.top = cv.offsetTop + 'px'; o.dataset.on = '1';
    const c = o.getContext('2d'); c.setTransform(dpr, 0, 0, dpr, 0, 0); c.clearRect(0, 0, w, h);
    const base = itm.whBig ? itm.whBig + 9 : 10.5, ph = (t % 2200) / 2200;   // one slow ring out every 2.2 s
    for(const [i, wh] of itm.whPulse){
      const x = itm.Q[2 * i], y = itm.Q[2 * i + 1];
      c.strokeStyle = itMapWhBoldCol(wh); c.lineWidth = 2; c.globalAlpha = 0.75 * (1 - ph);
      c.beginPath(); c.arc(x, y, base + ph * 16, 0, 6.283); c.stroke();
    }
    c.globalAlpha = 1;
  }
  // ---- 5: "N wormholes": each press moves the view to the next one, nearest first (by gate jumps from you, then the rest)
  function list(){
    if(!itm.wh || !itm.wh.kept) return [];
    const D = itm.D || [];
    return [...itm.wh.kept.keys()].sort((a, b) => ((D[a] >= 0 ? D[a] : 1e4) - (D[b] >= 0 ? D[b] : 1e4)) || (itm.wh.kept.get(b).t - itm.wh.kept.get(a).t));
  }
  function chipPaint(t){
    if(t - last < 250) return; last = t;
    const show = on() && window.__WHS5 && itm.wh && itm.wh.kept.size > 0;
    if(!show){ if(chip) chip.hidden = true; return; }
    if(!chip || chip.parentNode !== itm.cv.parentNode){
      chip = document.createElement('button'); chip.type = 'button'; chip.className = 'whs-chip';
      chip.addEventListener('click', () => {
        const L = list(); if(!L.length) return;
        step = (step + 1) % L.length; const i = L[step], k = itm.view.k;
        itm.view = {k, tx: itm.W / 2 - itm.P[2 * i] * k, ty: itm.H / 2 - itm.P[2 * i + 1] * k}; itMapDraw();
        chip.dataset.at = String(i); last = 0;
      });
      itm.cv.parentNode.appendChild(chip);
    }
    chip.hidden = false;
    const L = list(), n = L.length, at = step >= 0 && step < n ? step : -1, ids = itGraphGet().ids;
    const txt = at < 0 ? `${n} wormhole${n === 1 ? '' : 's'} ›` : `${at + 1}/${n} · ${itSysName(ids[L[at]])} ›`;
    if(chip.textContent !== txt){ chip.textContent = txt; chip.title = at < 0 ? 'Show the nearest wormhole; press again for the next' : 'Next wormhole'; chip.setAttribute('aria-label', `${n} wormholes on the map: ${at < 0 ? 'show the nearest' : 'show the next'}`); }
  }
  requestAnimationFrame(frame);
  const st = document.createElement('style');
  st.textContent = `canvas.whs-pulse{position:absolute; pointer-events:none; z-index:2;}
    .whs-chip{position:absolute; left:10px; bottom:10px; z-index:3; min-height:32px; padding:0 12px; border-radius:16px; border:1px solid #a98bd8; background:rgba(169,139,216,.18); color:#e6edf3; font:700 12px system-ui, sans-serif; cursor:pointer;}
    .whs-chip:hover{background:rgba(169,139,216,.32);} .whs-chip[hidden]{display:none;}
    @media (max-width:599px){ .whs-chip{min-height:40px;} }
    .mkbar{position:fixed; left:8px; bottom:8px; z-index:9999; display:flex; flex-wrap:wrap; gap:6px; align-items:center; max-width:calc(100vw - 16px); box-sizing:border-box; padding:6px 8px; border-radius:6px; background:#3a2a10; border:1px solid #d99a3c; font:12px system-ui, sans-serif; color:#e6edf3;}
    .mkbar.folded > :not(b):not([data-mk="fold"]){display:none;} .mkbar b{color:#d99a3c; letter-spacing:.5px;}
    .mkbar button{font-size:12px; padding:4px 8px; min-height:30px;} .mkbar [aria-pressed="true"]{background:#d99a3c; color:#111;}`;
  document.head.appendChild(st);
  // ---- MOCKUP bar (not part of the design): the new look on and off, the chip on and off, the filter
  window.__WHS_BAR = () => {
    const bar = document.createElement('div'); bar.className = 'mkbar';
    bar.innerHTML = '<b>MOCKUP</b><button type="button" data-mk="fold" aria-expanded="true" title="Fold this bar away">–</button>'
      + '<button type="button" data-mk="look" aria-pressed="true">New look (1–4)</button><button type="button" data-mk="chip" aria-pressed="false">Count chip (5)</button>'
      + '<button type="button" data-mk="wh">Wormholes filter</button><button type="button" data-mk="sec">Security filter</button>';
    bar.addEventListener('click', (ev) => {
      const b = ev.target.closest('button'); if(!b) return; const k = b.dataset.mk;
      if(k === 'fold'){ const f = bar.classList.toggle('folded'); b.textContent = f ? '+' : '–'; b.setAttribute('aria-expanded', String(!f)); return; }
      if(k === 'look'){ window.__WHS = !(window.__WHS !== false); b.setAttribute('aria-pressed', String(window.__WHS)); }
      if(k === 'chip'){ window.__WHS5 = !window.__WHS5; b.setAttribute('aria-pressed', String(window.__WHS5)); step = -1; last = 0; }
      if(k === 'wh' || k === 'sec') itMapFilterSet(k);
      if(typeof itMapDraw === 'function') itMapDraw();
    });
    document.body.appendChild(bar);
    const go = () => { if(window.__MKREADY && typeof itm !== 'undefined' && itm.P){ setTimeout(() => itMapFilterSet('wh'), 300); } else setTimeout(go, 200); };
    go();
  };
})();
