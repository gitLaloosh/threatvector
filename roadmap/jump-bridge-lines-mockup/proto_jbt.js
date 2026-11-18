// MOCKUP prototype: the Intel map's jump bridge lines button (build queue 059; the owner, 2026-11-17: "add a button to the map that toggles jump
// bridge visibility (not a filter, just a visibility toggle)", then his picks: "Zoom column", "Route step stays, hover off", "Remember; only
// while on", "Yes, mock it first"). One more map control in the zoom column after ⌖ (rule A: the zoom buttons' look, the pressed look the
// Wormholes tab's Select button already uses): shown only while "Use jump bridges on the map" is on and the list has bridges. On (pressed)
// by default, the lines drawn; off (the owner, 2026-11-17: "button defaults to on when jump bridges are enabled. no need for the line through
// it, just shows off state when they're turned off") = the green lines hidden; jump counts, Within N and Threat Vector's route still count the bridges, a route's bridge step is still drawn, and a
// bridge's hover is off. Kept as you left it (it.set.jbHide in dscanIntel, beside bridgesOn).
(function(){
  'use strict';
  const ICON = '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round">'
    + '<circle cx="3" cy="12" r="1.8" fill="currentColor" stroke="none"/><circle cx="13" cy="12" r="1.8" fill="currentColor" stroke="none"/><path d="M3.6 10.6Q8 1.5 12.4 10.6"/>'
    + '</svg>';
  const css = `.it-map-zoom button[data-im-z="jb"][aria-pressed="true"]{border-color:var(--cyan); color:var(--cyan); background:var(--tag-on);}
  .it-map-zoom button[data-im-z="jb"] svg{display:block; margin:auto;}
  #jbtBar{position:fixed; z-index:99999; left:50%; transform:translateX(-50%); bottom:8px; display:flex; flex-wrap:wrap; gap:6px; align-items:center; max-width:calc(100vw - 24px); box-sizing:border-box;
    padding:8px 10px; border:1px dashed var(--amber); border-radius:6px; background:#12171c; color:var(--text); font:12px var(--sans); box-shadow:0 6px 20px rgba(0,0,0,.6);}
  #jbtBar b{color:var(--amber);} #jbtBar button{min-height:28px; padding:0 9px; font-size:12px;} #jbtBar button[aria-pressed="true"]{background:var(--amber); color:#1b1306;}
  #jbtBar .n{flex:1 1 100%; color:var(--text-dim);} #jbtBar.fold > :not(.f){display:none;}
  @media (max-width:599px){ #jbtBar{left:8px; right:8px; transform:none;} #jbtBar button{min-height:36px;} }`;
  const hidden = () => !!(it.set && it.set.jbHide) && itBridgeOn();
  const z0 = itMapZoomHtml;
  window.itMapZoomHtml = function(){
    return z0().replace(/<\/div>$/, `<button type="button" data-im-z="jb" aria-pressed="true" aria-label="Jump bridge lines" hidden>${ICON}</button></div>`);
  };
  function paint(){
    const b = itm.el && itm.el.querySelector('[data-im-z="jb"]'); if(!b) return;
    const on = itBridgeOn(), shown = !hidden(), t = shown ? 'Jump bridge lines: on (press to hide them; bridges still count for jumps and routes)' : 'Jump bridge lines: off (press to show them)';
    if(b.hidden === on) b.hidden = !on;
    if(b.getAttribute('aria-pressed') !== String(shown)) b.setAttribute('aria-pressed', String(shown));   // on (pressed) by default whenever bridges are on
    if(b.title !== t) b.title = t;
  }
  const d0 = itMapDraw;
  window.itMapDraw = function(){
    paint();
    if(!hidden()) return d0.apply(this, arguments);
    const k = itm.jbKey; itm.jbKey = '';   // the page draws the bridges only while jbKey is set: hidden, the lines aren't drawn (a route's step is)
    try{ return d0.apply(this, arguments); } finally { itm.jbKey = k; }
  };
  const p0 = itMapPickBridge;
  window.itMapPickBridge = function(){ return hidden() ? -1 : p0.apply(this, arguments); };   // no hover on a line you can't see
  document.addEventListener('click', (ev) => {
    const b = ev.target.closest && ev.target.closest('[data-im-z="jb"]'); if(!b) return;
    ev.stopPropagation(); ev.preventDefault();   // the page's zoom handler would read it as Zoom out
    it.set.jbHide = !it.set.jbHide; itWriteSet();
    itm.hoverJb = -1; itMapTip(-1); itMapDraw(); paint();
  }, true);
  window.JBT = {paint, hidden, bar(){
    const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
    const b = document.createElement('div'); b.id = 'jbtBar'; b.setAttribute('role', 'toolbar'); b.setAttribute('aria-label', 'Mockup controls');
    b.innerHTML = '<b>MOCKUP</b><span>Use jump bridges on the map:</span><button type="button" data-j="on">On</button><button type="button" data-j="off">Off</button>'
      + '<button type="button" class="f" data-j="fold" aria-label="Fold the mockup bar">–</button>'
      + '<span class="n">The new button is in the zoom column, after ⌖: on whenever bridges are on; press it to turn the lines off (the Jumps colours and a route through a bridge stay). With the setting off it isn’t there.</span>';
    document.body.appendChild(b);
    const pb = () => { for(const x of b.querySelectorAll('[data-j="on"],[data-j="off"]')) x.setAttribute('aria-pressed', String((x.dataset.j === 'on') === !!it.set.bridgesOn)); };
    b.addEventListener('click', (ev) => { const x = ev.target.closest('[data-j]'); if(!x) return; const k = x.dataset.j;
      if(k === 'fold'){ b.classList.toggle('fold'); x.textContent = b.classList.contains('fold') ? '+' : '–'; return; }
      it.set.bridgesOn = k === 'on'; itWriteSet(); itMapRefresh(true); paint(); pb(); });
    pb(); paint();
  }};
})();
