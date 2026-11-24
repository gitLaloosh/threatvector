// Distance in light years (Project doc claude/roadmap/ly-distance-plan.md). The owner 2026-11-20: [stated] "Within N jumps → Distance
// (Recommended)", "Only where a jump can land (Recommended)", "Typed + quick picks (Recommended)", "From you, mockup yes (Recommended)";
// 2026-11-16: "Shade systems in range (Recommended)", "Type LY now, ship picker later (Recommended)". Shortcuts the build must not copy: README.md.
(() => {
  const L = window.MKY = {};
  // jump ranges at Jump Drive Calibration V: CCP's SDE (pyfa b79cd90), jumpDriveRange × (1 + 0.2 × 5)
  const QUICK = [[60, '6', 'Titans, supercarriers'], [70, '7', 'Carriers, dreadnoughts, FAX'], [80, '8', 'Black Ops, Lancers'], [100, '10', 'Jump freighters, Rorqual']];
  const ZARZAKH = 30100000;   // not in the page's jump table today (checked live 2026-11-20); kept out by ID if it ever is
  const lyOf = (i) => { const d = itMapLy(i, itm.home); return d === null ? null : Math.ceil(d * 100 - 1e-9) / 100; };   // as the hover shows it (itMapLyText)
  // where a jump drive can land: not 0.5 security or higher, not Pochven, not Zarzakh (CCP's 2006 article; the owner confirmed all three 2026-11-20)
  L.why = (i) => { const T = itMapTable(); if(itMapSecT(i) >= 5) return 'high-sec'; if(T.regions[T.reg[i]] === 'Pochven') return 'Pochven'; if(itGraphGet().ids[i] === ZARZAKH) return 'Zarzakh'; return ''; };
  // the stack's new fields (safe both ways: an older page ignores them, and saving drops them)
  const blank0 = itMapStackBlank, read0 = itMapStackRead;
  itMapStackBlank = function(){ const o = blank0(); o.near.mode = 'j'; o.near.ly = 70; return o; };
  itMapStackRead = function(){
    const o = read0(); let s = null; try{ s = JSON.parse(localStorage.getItem(MAP_STACK_KEY)); }catch(e){ s = null; }
    const n = s && s.near; if(n && typeof n === 'object'){ if(n.mode === 'ly') o.near.mode = 'ly'; if(Number.isInteger(n.ly) && n.ly >= 1 && n.ly <= 200) o.near.ly = n.ly; }
    return o;
  };
  // itMapStKey already holds s.near whole, so the new fields are in the match's key with no change
  // the filter's name and note
  const f = IT_MAP_FILTERS.find(x => x.k === 'near');
  f.name = 'Distance'; f.note = 'only: systems within N stargate jumps of you, or N light years where a jump drive can land';
  // the light years stepper: the page's stepper (typed on a computer; a phone uses the steppers and quick picks), in tenths of a LY
  RS.mapLy = {label: 'Within', unit: 'LY', title: () => 'Distance: light years from your system, where a jump drive can land', steps: () => itRangeList(1, 200), value: () => itMapSt().near.ly,
    set: (v) => { itMapSt().near.ly = v; }, why: (end) => end === 'lo' ? 'At least 0.1 LY' : 'At most 20.0 LY', aria: 'light years', show: (v) => (v / 10).toFixed(1), read: (t) => Math.round(parseFloat(t) * 10), after: () => itMpChanged()};
  // the match
  window.__MKnear = (i, D) => {
    const s = itMapSt().near;
    if(s.mode !== 'ly') return D[i] >= 0 && D[i] <= s.n;
    const d = lyOf(i); return d !== null && d <= s.ly / 10 + 1e-9 && !L.why(i);
  };
  // the Only line
  const only0 = itMapOnlyHtml;
  itMapOnlyHtml = function(){ const s = itMapSt(); let h = only0(); if(s.only.near && s.near.mode === 'ly') h = h.replace(/within \d+ jumps?/, `within ${(s.near.ly / 10).toFixed(1)} LY (jump drive)`); return h; };
  // the hover: in range or not, and why a system in range can't be landed in
  window.__MKtip = (i) => {
    const s = itMapSt(); if(!s.only.near || s.near.mode !== 'ly' || i === itm.home) return '';
    const d = lyOf(i); if(d === null || d > s.near.ly / 10 + 1e-9) return '';
    const w = L.why(i);
    return w ? `<br><span class="d">in range, but a jump drive can't land here (${w})</span>` : `<br><span class="d">within jump range (${(s.near.ly / 10).toFixed(1)} LY)</span>`;
  };
  // the settings panel
  const body0 = itMpBodyHtml;
  itMpBodyHtml = function(k){
    if(k !== 'near') return body0(k);
    const s = itMapSt().near, ly = s.mode === 'ly';
    const rad = (v, on, t) => `<label class="it-sov-k"><input type="radio" name="mkDist" value="${v}"${on ? ' checked' : ''}> <span>${t}</span></label>`;
    const head = `<div class="mk-dm">${rad('j', !ly, 'Jumps')}${rad('ly', ly, 'Light years')}</div>`;
    if(!ly) return head + body0(k);
    return head + `<div class="it-mp-row">${rsHtml('mapLy')}</div>`
      + `<div class="it-mp-q"><span>Quick:</span>${QUICK.map(([v, t, who]) => `<button type="button" data-mk-lyq="${v}" title="${escapeHtml(who)}, Jump Drive Calibration V" aria-pressed="${s.ly === v}">${t} LY</button>`).join('')}</div>`
      + '<div class="it-mp-note">Straight-line from your system, as the hover shows. Only where a jump drive can land: not high-sec, Pochven or Zarzakh. Quick picks: range at Jump Drive Calibration V.</div><div class="it-mp-cnt" role="status"></div>';
  };
  const paint0 = itMpPaint;   // the quick picks' pressed state follows the stepper (the body is built once per panel)
  itMpPaint = function(){ paint0(); if(!itMpShown() || itMp.k !== 'near') return; const v = itMapSt().near.ly; for(const x of itMp.el.querySelectorAll('[data-mk-lyq]')) x.setAttribute('aria-pressed', String(Number(x.dataset.mkLyq) === v)); };
  const make0 = itMpMake;
  itMpMake = function(){
    make0(); const p = itMp.el;
    p.addEventListener('change', (e) => { if(e.target.name !== 'mkDist') return; itMapSt().near.mode = e.target.value; itMp.built = ''; itMpChanged(); const r = p.querySelector('[name=mkDist]:checked'); if(r) r.focus({preventScroll: true}); });
    p.addEventListener('click', (e) => { const b = e.target.closest('[data-mk-lyq]'); if(!b) return; itMapSt().near.ly = Number(b.dataset.mkLyq); itMpChanged(); });
  };
  const css = document.createElement('style');
  css.textContent = `.it-mpp .mk-dm{display:flex; gap:12px; margin:0 0 6px;} .it-mpp .mk-dm .it-sov-k{flex:0 0 auto;}
    .it-mpp [data-mk-lyq][aria-pressed="true"]{background:color-mix(in srgb, var(--cyan) 18%, transparent);}`;
  document.head.appendChild(css);
  // scenes for the MOCKUP box
  L.zoomTo = (gpx) => { const i = itm.home; itMapZoom(itm.Q[2 * i], itm.Q[2 * i + 1], gpx / itMapGatePx()); itMapCenter(false); itMapDraw(); };
  L.scene = (k) => {
    itMapPanelClose(false);
    const s = itMapSt(); for(const o of IT_MAP_ONLY) s.only[o] = false; s.colour = 'sec';
    if(k === 'jumps'){ s.only.near = true; s.near.mode = 'j'; s.near.n = 5; }
    if(k === 'ly7'){ s.only.near = true; s.near.mode = 'ly'; s.near.ly = 70; }
    if(k === 'ly10'){ s.only.near = true; s.near.mode = 'ly'; s.near.ly = 100; }
    if(k === 'ly6'){ s.only.near = true; s.near.mode = 'ly'; s.near.ly = 60; }
    itMapStackSave(); itm.mtStep = -1; itMapFbarPaint(true); itMapLegend(); itMpPaint(); itMapDraw();
    L.zoomTo(k === 'ly10' ? 6 : 9);
    itMp.built = ''; if(k !== 'off') itMpOpen('near', false);
  };
  L.boot = () => {
    const d = document.createElement('div'); d.id = 'mkLy';
    const B = (a, t) => `<button type="button" ${a}>${t}</button>`;
    d.innerHTML = `<b>MOCKUP</b> <span class="mk-fold">${B('data-mk-sc="jumps"', 'Distance: 5 jumps (today)')}${B('data-mk-sc="ly6"', '6 LY')}${B('data-mk-sc="ly7"', '7 LY')}${B('data-mk-sc="ly10"', '10 LY')}${B('data-mk-sc="off"', 'Off')}</span>` + B('data-mk-fold', '▾');
    document.body.appendChild(d);
    const st = document.createElement('style');
    st.textContent = `#mkLy{position:fixed; right:8px; top:8px; z-index:99; background:#2a1d3a; border:1px solid #a98bd8; border-radius:6px; padding:6px 8px; font:12px system-ui; color:#eee; display:flex; flex-wrap:wrap; gap:4px 8px; align-items:center; max-width:min(460px, calc(100vw - 32px));}
      #mkLy button{font:12px system-ui; padding:2px 6px; border:1px solid #6d5a8a; border-radius:4px; background:#3a2a50; color:#eee; cursor:pointer; min-height:0;}
      #mkLy .mk-fold{display:contents;} #mkLy.folded .mk-fold{display:none;}
      @media (max-width: 599px){ #mkLy{top:auto; bottom:8px; left:8px; right:auto;} }`;
    document.head.appendChild(st);
    if(matchMedia('(max-width: 599px)').matches) d.classList.add('folded');
    d.addEventListener('click', (e) => { const b = e.target.closest('button'); if(!b) return; if(b.dataset.mkSc) L.scene(b.dataset.mkSc); if(b.dataset.mkFold !== undefined) d.classList.toggle('folded'); });
  };
})();
