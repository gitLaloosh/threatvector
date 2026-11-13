// MOCKUP bar (not part of the design): open the list, fill Import with a made-up friend's export, reset.
// The friend's export overlaps your list: the same reports (one line each, yours kept), a newer crit report against your own value (a note),
// a part that completes (QDX → QDX-581), an ID you removed (stays removed: older), a system you removed (stays removed: older), a new system,
// one added by hand, one older than your 24 h, and one that isn't on the map.
window.__MKfriend = () => { const n = Date.now(), m = (x) => n - x * 60000, P = '<a pilot>';
  const L = (t, raw, k = 'intel', set) => ({t, k, raw, ...(set ? {set} : {}), n: 1});
  return JSON.stringify({tv: 'wormholes', v: 1, made: n, sys: [
    {id: 30000772, name: 'C-J6MT', t: m(5), sigs: [{sig: 'RZL-429', part: false, type: 'Z971', info: {cls: 'C1-3', life: 'lt1d', mass: 'critical', size: 'medium'}, t: m(5)}, {sig: 'MKV', part: true, type: '', info: {mass: 'critical'}, t: m(30)}],
     raws: [L(m(5), 'C-J6MT wh RZL crit now'), L(m(30), 'C-J6MT wh sig MKV crit'), L(m(60), 'C-J6MT wh rzl-429 z971 class 1-3 medium size less then 1 day less then 50% mass')]},
    {id: 30000780, name: 'RERZ-L', t: m(90), sigs: [{sig: 'QDX-581', part: false, type: 'N110', info: {life: 'eol'}, t: m(90)}],
     raws: [L(m(90), 'RERZ-L wormhole QDX-581 n110 eol'), L(m(200), 'RERZ-L wh sig QDX')]},
    {id: 30000796, name: 'EUU-4N', t: m(500), drNoId: false, sigs: [{sig: 'KLM-204', part: false, type: '', info: {size: 'small'}, dr: true, t: m(500)}, {sig: 'BKT-772', part: false, type: '', dr: true, t: m(600)}],
     raws: [L(m(500), 'EUU-4N drifter KLM-204 frig hole'), L(m(600), 'EUU-4N drifter hole BKT772')]},
    {id: 30000779, name: 'SHBF-V', t: m(420), sigs: [{sig: 'XYZ-123', part: false, type: 'H296', t: m(420)}], raws: [L(m(420), 'SHBF-V 2 wh XYZ-123 H296 and PQR-4 K162')]},
    {id: 30000771, name: '8G-2FP', t: m(45), sigs: [{sig: 'LMN', part: true, type: '', info: {cls: 'C3'}, t: m(45)}], raws: [L(m(45), `8G-2FP wh LMN C3 fresh ${P} Sabre`)]},
    {id: 30000786, name: 'L5-UWT', t: m(15), sigs: [{sig: 'ABC-123', part: false, type: 'C247', t: m(15)}], raws: [L(m(15), 'L5-UWT ABC-123 C247', 'hand', {sigs: [{sig: 'ABC-123', part: false, type: 'C247'}]})]},
    {id: 30000776, name: '4M-QXK', t: m(30 * 60), sigs: [], raws: [L(m(30 * 60), '4M-QXK wh')]},
    {id: 31000001, name: 'J990001', t: m(10), sigs: [], raws: [L(m(10), 'J990001 wh')]}]}, null, 0); };
(() => {
  const bar = document.createElement('div'); bar.className = 'mkbar';
  bar.innerHTML = '<b>MOCKUP</b><button type="button" data-mk="open">Open the Wormholes list</button><button type="button" data-mk="friend">Fill Import with a friend’s export</button><button type="button" data-mk="reset">Reset my list</button>';
  const openList = (then) => {
    const nv = document.querySelector('[data-it-nv="map"]'); if(nv && nv.offsetParent && nv.getAttribute('aria-pressed') !== 'true') nv.click();   // a phone: the map side
    setTimeout(() => { if(!itWhListShown()) itWhListOpen(true); if(then) setTimeout(then, 150); }, 120);
  };
  bar.addEventListener('pointerdown', (ev) => ev.stopPropagation(), true);   // the bar is not "outside the list"
  bar.addEventListener('click', (ev) => {
    const b = ev.target.closest('button'); if(!b) return;
    if(b.dataset.mk === 'open') openList();
    if(b.dataset.mk === 'friend') openList(() => { const p = itWhL.el; if(p.querySelector('[data-it-whxb="imp"]').getAttribute('aria-expanded') !== 'true') itWhBoxOpen(p, 'imp', true); const ta = p.querySelector('#itWhImp textarea'); ta.value = window.__MKfriend(); ta.scrollIntoView({block: 'nearest'}); });
    if(b.dataset.mk === 'reset') location.reload();
  });
  const st = document.createElement('style');
  st.textContent = `.mkbar{position:fixed; left:8px; bottom:8px; z-index:9999; display:flex; flex-wrap:wrap; gap:6px; align-items:center; max-width:calc(100vw - 16px); box-sizing:border-box; padding:6px 8px; border-radius:6px; background:#3a2a10; border:1px solid var(--amber); font:12px var(--sans); color:var(--heading);}
    .mkbar b{color:var(--amber); letter-spacing:.5px;} .mkbar button{font-size:12px; padding:4px 8px; min-height:30px;}`;
  document.head.appendChild(st); document.body.appendChild(bar);
})();
