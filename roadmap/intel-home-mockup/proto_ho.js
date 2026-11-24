// MOCKUP prototype: the Intel map's own Home (Project doc claude/roadmap/intel-home-plan.md). Appended after the page's own script.
// The owner 2026-11-22: "also add the ability to set a \"home\" system from the intel map. use something like the in-game \"home\" system icon
// (just draw it yourself)"; 2026-11-23: [stated] "Intel's own Home (Recommended)", "Route to Home,Jumps from Home on hover", "Yes, mockup
// (Recommended)". Shortcuts not to copy (README): itRpBtnsHtml, itRpTipHtml and itMapZoomHtml are wrapped here, the clicks are caught with capture
// listeners, and the draw / hover / route lines are hooks added by build_ho.py.
const HO_KEY = 'tvHome';
const HO = {id: 0, route: false};
// the house: a roof and a body with a door, drawn by us (no CCP art); 16 px in the rail button
const HO_SVG = '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><path d="M2.5 7.5L8 2.5l5.5 5"/><path d="M4 6.5V13.5h8V6.5"/><path d="M6.8 13.5v-3.2h2.4v3.2"/></svg>';
function hoRead(){ try{ const o = JSON.parse(localStorage.getItem(HO_KEY) || 'null'); if(o && o.v === 1 && Number.isInteger(o.id) && o.id > 0){ HO.id = o.id; HO.route = !!o.route; } }catch(e){} }
function hoSave(){ try{ if(HO.id) localStorage.setItem(HO_KEY, JSON.stringify({v: 1, id: HO.id, route: HO.route})); else localStorage.removeItem(HO_KEY); }catch(e){} }
function hoIdx(){ if(!HO.id) return -1; const i = itGraphGet().at.get(HO.id); return i === undefined ? -1 : i; }
// jumps from Home: one search over the same graph the map counts "jumps from you" on (gates, and your bridges while they're on), kept
// until Home or the bridges change
let hoCache = {key: '', D: null};
function hoDist(){
  const h = hoIdx(); if(h < 0) return null;
  const key = HO.id + '|' + (itm.jbKey || ''); if(hoCache.key === key) return hoCache.D;
  const T = itMapTable(), adj = itm.jbKey ? itBridgeAdj() : T.adj, D = new Int16Array(T.n).fill(-1), q = [h]; D[h] = 0;
  for(let k = 0; k < q.length; k++){ const x = q[k]; for(const y of adj[x]) if(D[y] < 0){ D[y] = D[x] + 1; q.push(y); } }
  hoCache = {key, D}; return D;
}
// the hover's line
window.__MKhomeTip = (i) => {
  const h = hoIdx(); if(h < 0) return '';
  if(i === h) return `<br><span class="ho-tl">${HO_SVG} Your Home</span>`;
  const D = hoDist(), d = D ? D[i] : -1, nm = itSysName(HO.id);
  return `<br><span class="d">${escapeHtml(d < 0 ? `no gate route from Home (${nm})` : `${d} jump${d === 1 ? '' : 's'} from Home (${nm})`)}</span>`;
};
// the route to Home: shown as a kept route (solid, in the Home colour) while the rail button is on; kept across moves
window.__MKhomeRoute = () => HO.id && HO.route ? [HO.id] : [];
window.__MKhomeId = () => HO.route ? HO.id : 0;
// the house on the map: above the system's dot (zoomed in, above its circle); when you're in Home, to the left of your pin
window.__MKhomeDraw = (c, X, Y, big, r) => {
  const i = hoIdx(); if(i < 0) return;
  const s = big ? 15 : 12, here = i === itm.home, x = X(i) - (here ? (big ? r + 12 : 13) : 0), base = here ? Y(i) + s * 0.45 : Y(i) - (big ? r + 3 : 5);
  hoHouse(c, x, base, s);
};
function hoHouse(c, x, base, s){   // base: the bottom of the house, centred on x
  const w = s * 0.78, hb = s * 0.5, top = base - s, col = itMapCol('--wh-st-home', '#4fc3d9');
  c.save(); c.lineJoin = 'round';
  c.beginPath(); c.moveTo(x - s * 0.55, base - hb); c.lineTo(x, top); c.lineTo(x + s * 0.55, base - hb); c.lineTo(x + w / 2, base - hb); c.lineTo(x + w / 2, base); c.lineTo(x - w / 2, base); c.lineTo(x - w / 2, base - hb); c.closePath();
  c.lineWidth = 3.5; c.strokeStyle = '#0c1014'; c.stroke();
  c.shadowColor = 'rgba(0,0,0,.5)'; c.shadowBlur = 5; c.fillStyle = col; c.fill(); c.shadowBlur = 0;
  c.fillStyle = '#0c1014'; c.fillRect(x - s * 0.1, base - hb * 0.62, s * 0.2, hb * 0.62);   // the door
  c.restore();
}
// the legend, while a Home is set (the owner 2026-11-23: "Add it while set (Recommended)"): the house, and the route's line while it's shown
window.__MKhomeLeg = () => hoIdx() < 0 ? '' : `<span class="ho-tl">${HO_SVG}Home (${escapeHtml(itSysName(HO.id))})</span>` + (HO.route ? '<span><i class="ln ho-ln"></i>route to Home (kept)</span>' : '');
// the right-click menu (and a phone's tooltip buttons): Set as Home on any system, Remove Home on Home
function hoBtnHtml(i, inTip){
  const gid = itGraphGet().ids[i], role = inTip ? '' : ' role="menuitem"';
  if(gid === HO.id){   // on Home: its route (kept across moves) and Remove
    const here = i === itm.home;
    return `<button type="button"${role} class="it-rp-av" data-it-home="rt"${here ? ' disabled' : ''}>${HO.route ? 'Hide' : 'Show'} the route to Home${here ? ' <span>(you are here)</span>' : ''}</button>`
      + `<button type="button"${role} class="it-rp-av" data-it-home="off">Remove Home</button>`;
  }
  return `<button type="button"${role} class="it-rp-av" data-it-home="set" data-it-home-id="${Number(gid)}">Set as Home${HO.id ? ` <span>(instead of ${escapeHtml(itSysName(HO.id))})</span>` : ''}</button>`;
}
const _hoBtns = itRpBtnsHtml;
itRpBtnsHtml = function(i, inTip){ return _hoBtns(i, inTip).replace(/<\/div>$/, hoBtnHtml(i, inTip) + '</div>'); };
// a phone: your own system's tooltip has no buttons today (no route to send), so it gets the Home button on its own
const _hoTipRp = itRpTipHtml;
itRpTipHtml = function(i){
  const r = _hoTipRp(i);
  if(i < 0 || i !== itm.home || itRpAside || !itRpTouch()) return r;
  return {h: r.h + `<div class="it-rp-btns it-rp-intip" role="group" aria-label="${escapeHtml(itSysName(itGraphGet().ids[i]))}">${hoBtnHtml(i, true)}</div>`, act: true};
};
// the top bar: a house button left of "Center on your system" (the owner 2026-11-23: "i would put the "home" button at the top to the
// left of the "center on your system". it should "center on your home system""), shown while a Home is set
const _hoZoom = itMapZoomHtml;
itMapZoomHtml = function(){ return _hoZoom().replace('<button type="button" data-im-z="me"', `<button type="button" data-it-home-go title="Center on your Home" aria-label="Center on your Home" hidden>${HO_SVG}</button><button type="button" data-im-z="me"`); };
function hoRailPaint(){
  const b = itm.box && itm.box.querySelector('[data-it-home-go]'); if(!b) return;
  b.hidden = hoIdx() < 0;
  const nm = HO.id ? itSysName(HO.id) : '';
  b.title = b.hidden ? 'Center on your Home' : `Center on your Home (${nm})`; b.setAttribute('aria-label', b.title);
}
function hoCenter(){
  const h = hoIdx(); if(h < 0 || !itm.P) return;
  const v = itm.view; v.tx = itMapFreeX() - itm.P[2 * h] * v.k; v.ty = itm.H / 2 - itm.P[2 * h + 1] * v.k;   // as itMapCenter, on Home
  itMapTip(-1); itMapDraw();
}
function hoSet(id){ HO.id = id; hoCache.key = ''; if(!id) HO.route = false; hoSave(); hoRailPaint(); itRenderLists(); itMapRefresh(true); itMapLegend(); itMapDraw(); }
document.addEventListener('click', (e) => {
  const b = e.target.closest && e.target.closest('[data-it-home], [data-it-home-go]'); if(!b) return;
  e.preventDefault(); e.stopPropagation();
  if(b.dataset.itHomeGo !== undefined){ hoCenter(); return; }
  if(b.dataset.itHome === 'rt'){ itRpMenuClose(); HO.route = !HO.route; hoSave(); itMapTip(-1); itMapLegend(); itMapDraw(); return; }
  if(b.dataset.itHome === 'set'){ itRpMenuClose(); hoSet(Number(b.dataset.itHomeId)); }
  else if(b.dataset.itHome === 'off'){ itRpMenuClose(); hoSet(0); }
}, true);
// its info line (the build: CARD_INFO.intel [Map], cap raised a little)
CARD_INFO.intel = CARD_INFO.intel.map(p => p.startsWith('[Map]') ? p.replace(/\.?\s*$/, '. Set as Home (right-click): a house marks it, hovers count jumps from it, the top house button centers on it, its menu shows the route.') : p);
const hoCss = document.createElement('style');
hoCss.textContent = `.it-map-tip .ho-tl{color:var(--wh-st-home); font-weight:600; display:inline-flex; gap:4px; align-items:center;} .it-map-tip .ho-tl svg{display:inline-block;}
  .it-map-leg .ho-tl{color:var(--wh-st-home); display:inline-flex; gap:3px; align-items:center;} .it-map-leg i.ln.ho-ln{background:var(--wh-st-home);}`;
document.head.appendChild(hoCss);
hoRead();
