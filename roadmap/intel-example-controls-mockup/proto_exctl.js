// Intel example: the live map's controls (research session, 2026-11-15). Injected after the page's own script by build_exctl.py.
// Proposed: the example's map picture carries still, inert copies of what the live map shows before you touch it (zoom buttons, the
// system search, the filter column with Security on and its phone button, the slider row under the legend), is as tall as the live map,
// and is centred on you in the part Near You's list doesn't cover. "Today" is the page as it is. Made-up data only (the page's IT_EXAMPLE).
(function(){
  const MK = {mode: 'new'};
  const exHtml0 = itExampleHtml, exPic0 = itExMapPic, exPlace0 = itExPlace;
  // In the build these become shared builders (itMapZoomHtml etc.) used by itMapMake too; the mockup copies itMapMake's zoom row
  const ZOOM = `<div class="it-map-zoom"><button type="button" data-im-z="in" title="Zoom in (or the mouse wheel)" aria-label="Zoom in">+</button><button type="button" data-im-z="out" title="Zoom out (or the mouse wheel)" aria-label="Zoom out">−</button><button type="button" data-im-z="fit" title="Back to the whole area" aria-label="Fit the map">⤢</button><button type="button" data-im-z="me" title="Center on your system" aria-label="Center on your system">${IT_MAP_CROSS}</button></div>`;
  // a still copy: no ids, no hooks the live map's code looks for, nothing focusable
  const still = (h) => h.replace(/\s(?:id|aria-controls|aria-activedescendant|aria-haspopup)="[^"]*"/g, '')
    .replace(/\sdata-(?:im-[a-z]+|it-[a-z-]+|rs(?:-d)?)(?:="[^"]*")?/g, '').replace(/<(button|input)\b/g, '<$1 tabindex="-1"');
  function ctlHtml(){
    const f0 = IT_MAP_FILTERS[0];
    const fb = itMapFbarHtml()
      .replace('<div class="it-map-fn" aria-hidden="true"></div>', `<div class="it-map-fn" aria-hidden="true"><b>${escapeHtml(f0.name)}</b> <span>${escapeHtml(f0.note)}</span></div>`)
      .replace('aria-haspopup="true"></button>', `aria-haspopup="true">${f0.icon}</button>`)
      .replace(`data-im-f="${f0.k}" `, `data-im-f="${f0.k}" data-mk-on `);
    return still(ZOOM + itRpSearchHtml() + fb).replace(/data-mk-on ([^>]*?)aria-pressed="false"/, '$1aria-pressed="true"');
  }
  function rowHtml(){
    const rs = still(rsHtml('mapReach')).replace('<input ', `<input value="${Number(IT_EXAMPLE.mapReach)}" readonly `);
    return `<div class="it-map-row"><span class="it-map-rs">${rs}</span><span class="it-map-help wide">drag to move · wheel to zoom</span><span class="it-map-help phone">two fingers move and zoom the map; one finger scrolls the page</span></div>`;
  }
  itExampleHtml = function(){
    if(MK.mode === 'today') return exHtml0();
    if(!itExShown()) return '';
    const phone = itExPhone(), key = phone ? 'p' : 'w';
    if(!itEx.html || itEx.htmlKey !== key){
      itEx.htmlKey = key;
      itEx.html = itExSandbox(() => {
        itFrozenNow = Date.now(); itAnCan = new Map();
        return `<div class="it-top ny-open itx-top itx-v2"><div class="it-mapcol"><div class="it-h"><h3>${escapeHtml(cardName('itmap'))}</h3><span class="ctx">around you, ${Number(IT_EXAMPLE.mapReach)} jumps</span></div>`
          + `<div class="it-mapwrap"><div class="it-map-box itx-map"><img alt="The example's map: reports and kills around 1DQ1-A">${ctlHtml()}${itExRailHtml()}</div>`
          + `<div class="it-nearcol"><div class="it-h"><h3>${escapeHtml(cardName('itnear'))}</h3><span class="ctx">last ${Number(IT_EXAMPLE.forget)} min, within ${Number(IT_EXAMPLE.nearRange)} jumps</span></div><div class="itx-near">${itExNearHtml()}</div></div></div>`
          + `<div class="it-map-leg">${itExLegendHtml()}</div>${rowHtml()}</div></div>`
          + `<div class="it-feedcol"><div class="it-h"><h3>${escapeHtml(cardName('itfeed'))}</h3><span class="ctx">first 5 rows</span></div><div class="itx-feed">${itExFeedHtml()}</div></div>`;
      }).replace(/ data-it-(sys|cap)="/g, ' data-itx-$1="');
    }
    return `<div class="itx" role="region" aria-label="Example: what Intel shows once it’s running">${itExCloseHtml()}<div class="itx-h"><span class="itx-tag">EXAMPLE</span><span class="itx-t">What Intel looks like once it’s running</span>${ctxHtml('made-up pilots on real systems')}</div>`
      + `<div class="itx-wrap"><div class="itx-body" inert>${itExRowsHtml()}</div>${itExMarksHtml()}</div>`
      + `<ol class="itx-notes">${itExNotesHtml()}</ol><div class="itx-foot">Your own reports replace this example as soon as the first one arrives.</div></div>`;
  };
  // the live map's height (itMapRefresh) and its free part (itMapFree): left of Near You's list (wide), past the filter column
  function liveH(w, phone){ return Math.round(phone ? Math.min(600, Math.max(440, w * 1.45)) : Math.min(720, Math.max(520, w * 0.5))); }
  itExMapPic = function(w){
    if(MK.mode === 'today') return exPic0(w);
    const phone = itExPhone(), key = `v2|${w}|${phone}|${itFontEpoch}`;
    if(itEx.map && itEx.mapKey === key) return itEx.map;
    const a = phone ? 56 : 44, b = phone ? w : w - 44 - 320 - 4, free0 = itMapFree;
    let url = null;
    itExSandbox(() => {
      const keep = {...itm}, T = itMapTable(), g = itGraphGet(), home = T ? g.at.get(IT_EXAMPLE.home) : undefined;
      if(home === undefined) return;
      const cv = document.createElement('canvas'), you = document.createElement('span'), dpr = window.devicePixelRatio || 1, h = liveH(w, phone);
      you.innerHTML = '<svg></svg>';
      itMapFree = () => [phone ? 0 : a, b];   // the build passes this in (the picture has no box to measure)
      try{
        Object.assign(itm, {cv, you, W: w, H: h, reach: IT_EXAMPLE.mapReach, home, hover: -1, rowHover: -1, pinned: new Set(), filter: 'sec'});
        cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr);
        itMapBfs(home); itMapLayout(); itm.rep = itMapReports();
        const v = itm.view, out = [...itm.rep.keys()].some(i => { const x = itm.P[2 * i] * v.k + v.tx, y = itm.P[2 * i + 1] * v.k + v.ty; return x < a + 30 || x > b - 40 || y < 40 || y > h - 30; });
        if(out){ itMapFree = () => [a, b]; itMapFitView(); }
        itMapDraw();
        url = cv.toDataURL('image/png');
      }finally{ itMapFree = free0; for(const k of Object.keys(itm)) if(!(k in keep)) delete itm[k]; Object.assign(itm, keep); }
    });
    itEx.map = url; itEx.mapKey = key;
    return url;
  };
  // after the picture: the filter column's rows as the live map works them out (itMapCtlPlace); marker 3 to the picture's bottom-left
  // corner (its top-left now holds the search box)
  itExPlace = function(f){
    if(MK.mode !== 'today'){
      const box = f.querySelector('.itx-map'), fb = box && box.querySelector('.it-map-fb'), bs = fb && fb.querySelector('.it-map-fbtns'), img = box && box.querySelector('img');
      if(bs && img){ const one = itExPhone() ? 46 : 34, rows = String(Math.min(bs.children.length, Math.max(3, Math.floor((img.clientHeight - 8 - fb.offsetTop - 8) / one)))); if(bs.style.getPropertyValue('--it-flr') !== rows) bs.style.setProperty('--it-flr', rows); }
    }
    exPlace0(f);
    if(MK.mode !== 'today'){
      const m = f.querySelector('[data-itx-mk="3"]'), img = f.querySelector('.itx-map img[src]'), W = f.querySelector('.itx-wrap');
      if(m && img && W){ const R = W.getBoundingClientRect(), r = img.getBoundingClientRect(); m.style.left = `${Math.round(r.left - R.left + 14)}px`; m.style.top = `${Math.round(r.bottom - R.top - 14)}px`; m.hidden = false; }
    }
  };
  const css = document.createElement('style');
  css.textContent = `
    /* the live map's places: the rail under the zoom row (a phone: under the search box, as live); Near You level with the rail */
    @media (min-width: 600px){ .it-top.itx-top.itx-v2 .itx-map .it-map-rail{top:46px;} .it-top.itx-top.itx-v2 .it-nearcol{top:46px; bottom:8px;} }
    @media (max-width: 599px){ .it-top.itx-top.itx-v2 .itx-map .it-map-rail{top:112px;}
      /* fix found 2026-11-15 (on main too): on a phone the example's Near You list had no height (flex:1 1 0 in a column of auto height) */
      .it-top.itx-top.itx-v2 .it-nearcol > .itx-near{flex:none;} }
    .itx-v2 .itx-map .it-map-fn{opacity:0;}
    #mkBox{position:fixed; z-index:9999; right:12px; bottom:12px; padding:8px 10px; border:1px dashed var(--amber); border-radius:6px; background:rgba(12,16,20,.96); font:400 12px var(--sans); color:var(--text);}
    #mkBox b{color:var(--amber); margin-right:6px;} #mkBox button{margin:0 0 0 4px; min-height:30px;} #mkBox button[aria-pressed="true"]{background:var(--amber); color:#0b0f13;}
    @media (max-width: 599px){ #mkBox{left:8px; right:8px; bottom:8px;} #mkBox button{min-height:44px;} }`;
  document.head.appendChild(css);
  const box = document.createElement('div'); box.id = 'mkBox';
  box.innerHTML = '<b>MOCKUP</b>Example: <button type="button" data-mk="today" aria-pressed="false">Today</button><button type="button" data-mk="new" aria-pressed="true">Proposed</button>';
  box.addEventListener('click', (e) => {
    const b = e.target.closest('[data-mk]'); if(!b || b.dataset.mk === MK.mode) return;
    MK.mode = b.dataset.mk; for(const x of box.querySelectorAll('[data-mk]')) x.setAttribute('aria-pressed', String(x === b));
    itEx.html = null; itEx.map = null; itEx.mapKey = ''; itRender(true);
  });
  document.body.appendChild(box);
  window.__mkMode = (m) => { const b = box.querySelector(`[data-mk="${m}"]`); if(b) b.click(); };
  // open on the Intel tab, where the example is
  const go = () => { itEx.html = null; itEx.map = null; itEx.mapKey = ''; const t = document.getElementById('tabBtnIntel'); if(t) t.click(); itRender(true); };   // the page drew the example before this script ran
  if(document.readyState === 'complete') setTimeout(go, 0); else addEventListener('load', go, {once: true});
})();
