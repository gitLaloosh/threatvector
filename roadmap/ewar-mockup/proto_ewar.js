// MOCKUP prototype: "EWAR that tips an engagement" (claude/roadmap/ewar-plan.md), injected into the real page after the
// Fit Analyzer shows a threat and My Ship holds your fit. Wraps page functions; the page's own code draws everything.
// Phases: 0 today, 1 = A (tracking/guidance disruptors), 2 = A+B (+ neuts/nos), 3 = A+B+C (+ damps, lock range, ECM).
// Numbers: TDs, the capacitor (pyfa's simulation, the page's capSimPyfa with the neut/nos drains added), lock time and
// jam chance follow pyfa's formulas; resistances are left out (neither made-up hull has one).
(() => {
  const P = window.__ewarProto = {phase: 0, range: null};
  const host = () => document.querySelector('#fitAnalyzerResults .mys-switch-host');
  const tEst = () => { const h = host(); const tf = h && mysStripThreatF(h); return tf && tf.estimate; };
  const mEst = () => myShip.f && myShip.f.estimate;
  const ew = (kind) => ((tEst() || {}).ewarModules || []).filter(m => m.running && m.kind === kind);
  const rf = (m, d) => pyfaCalculateRangeFactor(m.rangeM, m.falloffM, d);
  const pct = (x) => `${x > 0 ? '+' : '−'}${Math.abs(Math.round(x))}%`;
  const km = (m) => dmgKm(m);
  const count = (mods) => mods.reduce((s, m) => s + m.qty, 0);
  const plural = (n, one, many) => `${n} ${n === 1 ? one : many}`;
  P.mark = () => { const me = mEst(); if(!me) return; me.application.__mine = true; for(const w of me.application.weapons) w.__mine = true; };

  // ---- A: tracking disruptors (pyfa Effect6424: turrets' trackingSpeed / maxRange / falloff, penalised, × range factor)
  P.td = (d) => {
    const g = {optimal: [], falloff: [], tracking: []};
    for(const m of ew('trackingDisruptor')){
      const f = rf(m, d);
      for(let i = 0; i < m.qty; i++){
        if(m.opticalBonusPct) g.optimal.push([1 + m.opticalBonusPct * f / 100, null]);
        if(m.falloffBonusPct) g.falloff.push([1 + m.falloffBonusPct * f / 100, null]);
        if(m.trackingSpeedBonusPct) g.tracking.push([1 + m.trackingSpeedBonusPct * f / 100, null]);
      }
    }
    return {optimal: pyfaCalculateMultiplier({default: g.optimal}), falloff: pyfaCalculateMultiplier({default: g.falloff}),
      tracking: pyfaCalculateMultiplier({default: g.tracking})};
  };
  // ---- C: dampeners on your lock range (pyfa Effect6422), ECM (Effect6470 + Fit.jamChance), lock time (calculateLockTime)
  P.lock0 = () => mEst().application.lockRange;
  P.lock = (d) => P.lock0() * pyfaCalculateMultiplier({default: ew('damp').flatMap(m => Array(m.qty).fill([1 + m.targetingRangeBonusPct * rf(m, d) / 100, null]))});
  const num = (v) => (v && typeof v === 'object') ? (v.value ?? v.boosted ?? v.base ?? 0) : (v || 0);
  P.jam = (d) => { const s = num(mEst().sensorStrength); let keep = 1;
    for(const m of ew('ecm')) for(let i = 0; i < m.qty; i++) keep *= 1 - Math.min(1, m.jamStrength * rf(m, d) / s);
    return 1 - keep; };
  P.lockTime = (scanRes, sig) => Math.min(40000 / scanRes / Math.asinh(sig) ** 2, 1800);
  // ---- B: neuts / nos into your capacitor simulation (pyfa addDrain), at the fight's range
  const capMemo = new Map();
  P.cap = (d) => {
    const key = Math.round(d); if(capMemo.has(key)) return capMemo.get(key);
    const ci = mEst().capacitor.simInputs, drains = ci.withoutBoosts.slice();
    let gjs = 0;
    for(const m of [...ew('neut'), ...ew('nos')]){
      const f = rf(m, d), cycMs = Math.round(m.capPerCycle / m.capPerSec * 1000);
      for(let i = 0; i < m.qty; i++){ if(f > 0) drains.push([cycMs, m.capPerCycle * f, 0, false, 0, false]); gjs += m.capPerSec * f; }
    }
    const r = Object.assign({gjs}, capSimPyfa(ci.capacity, ci.rechargeMs, drains));
    capMemo.set(key, r); return r;
  };
  const capT = (c) => c.stable ? null : (c.timeToEmptyExactSec ?? c.timeToEmptySec);
  const mmss = (s) => s === null ? 'stable' : `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, '0')}`;

  // ---- wraps
  // C (the owner, Q2): lock range always counts, for both ships; yours is the damped one
  const lockP = (p) => P.phase >= 3 && p && p.distance !== null && p.distance !== undefined;
  const origApp = pyfaApplicationMult;
  window.pyfaApplicationMult = function(w, p){
    if(w.__mine && p.distance !== null && p.distance !== undefined && P.phase >= 1 && w.kind === 'turret'){ const t = P.td(p.distance);
      w = Object.assign({}, w, {optimal: w.optimal * t.optimal, falloff: w.falloff * t.falloff, tracking: w.tracking * t.tracking}); }
    if(lockP(p)) p = Object.assign({}, p, {ignoreLockRange: false}, w.__mine ? {lockRange: P.lock(p.distance)} : {});
    return origApp(w, p);
  };
  const lockWrap = (orig) => function(app, x, p){
    if(!lockP(p)) return orig(app, x, p);
    return orig(app.__mine ? Object.assign({}, app, {lockRange: P.lock(p.distance)}) : app, x, Object.assign({}, p, {ignoreLockRange: false}));
  };
  window.pyfaGetDroneMult = lockWrap(pyfaGetDroneMult);
  window.pyfaGetFighterAbilityMult = lockWrap(pyfaGetFighterAbilityMult);
  window.pyfaProjectedPoint = lockWrap(pyfaProjectedPoint);
  const origDef = ttkDefense;
  window.ttkDefense = function(est){
    const d = origDef(est);
    if(P.phase >= 2 && est === mEst() && P.range !== null){ const t = capT(P.cap(P.range)); d.capSec = t === null ? Infinity : t; }
    return d;
  };
  const origMarks = dmgRangeMarks;
  window.dmgRangeMarks = function(app, est, xMax, mwdOff, who = 'their'){
    const mine = who === 'your';
    const r = origMarks(mine && P.phase >= 3 && P.range !== null ? Object.assign({}, app, {lockRange: P.lock(P.range)}) : app, est, xMax, mwdOff, who);
    if(!mine && P.phase >= 1){
      const add = (x, label, short) => { if(x > 0) r.zones.push({x, cat: 'disrupt', letter: EWAR_BADGE_LETTER.disrupt, label, short}); };
      const far = (a) => Math.max(0, ...a.map(m => m.rangeM));
      add(far(ew('trackingDisruptor')), 'Their tracking disruptor', 'TD');
      if(P.phase >= 3){ add(far(ew('damp')), 'Their dampener', 'damp'); add(far(ew('ecm')), 'Their ECM', 'ECM'); }
      r.zones.sort((a, b) => a.x - b.x);
    }
    if(mine && P.phase >= 3) for(const p of r.pins) if(/lock range/.test(p.label)) p.label = 'Your lock range (damped)';
    return r;
  };
  // the line under each chart
  P.lineMine = (d) => {
    const bits = [];
    const tds = ew('trackingDisruptor');
    if(P.phase >= 1 && tds.length){ const t = P.td(d);
      bits.push(`Their ${plural(count(tds), 'tracking disruptor', 'tracking disruptors')}: your optimal ${pct((t.optimal - 1) * 100)}, falloff ${pct((t.falloff - 1) * 100)}, tracking ${pct((t.tracking - 1) * 100)}`); }
    if(P.phase >= 3 && ew('damp').length) bits.push(`their dampener: your lock range ${km(P.lock(d))} (${km(P.lock0())} without)`);
    return bits.length ? `At ${km(d)}: ${bits.join(' · ')}` : '';
  };
  P.lineTheirs = (d) => {
    const bits = [];
    if(P.phase >= 2 && (ew('neut').length || ew('nos').length)){ const c = P.cap(d), c0 = mEst().capacitor;
      bits.push(`their neuts and nos drain ${Math.round(c.gjs)} GJ/s: your capacitor empties in ${mmss(capT(c))} (${mmss(c0.stable ? null : c0.timeToEmptyExactSec)} without them)`); }
    if(P.phase >= 3 && ew('ecm').length) bits.push(`their ECM: ${Math.round(P.jam(d) * 100)}% chance per cycle to jam you`);
    return bits.length ? `At ${km(d)}: ${bits.join(' · ')}` : '';
  };

  // ---- icon badges (the owner 2026-11-14: "what if we used the module's image from esi instead?", then "can we start with
  // the colored frame being less prominent than the ones in the fit card?"): the module's own icon on each chart badge and
  // key row, a faint category frame ('thin') or a category bar under it ('bar'); the letter stays underneath, in the
  // category colour, for when the image server doesn't answer.
  P.badgeStyle = 'thin';   // 'thin' | 'bar' | 'off' (today's letters)
  const KIND_RX = [[/scram/i, 'scram'], [/\bweb\b/i, 'web'], [/painter/i, 'paint'], [/\bneut\b/i, 'neut'], [/\bnos\b/i, 'nos'],
    [/tracking disruptor/i, 'trackingDisruptor'], [/dampener/i, 'damp'], [/\bECM\b/, 'ecm']];
  const CAT_VAR = {tackle: '--tank-armor', disrupt: '--tank-shield', drain: '--drain'};
  P.iconFor = (est, label) => {
    const k = (KIND_RX.find(([rx]) => rx.test(label)) || [])[1]; if(!k || !est) return null;
    const mods = (est.ewarModules || []).filter(m => m.running && m.kind === k).sort((a, b) => b.rangeM - a.rangeM);
    const it = mods.length && ((est.moduleStates || {}).items || []).find(i => i.name === mods[0].name);
    return it ? {id: it.typeId, name: mods[0].name} : null;
  };
  const NS = 'http://www.w3.org/2000/svg';
  P.iconize = (card) => {
    if(P.badgeStyle === 'off') return;
    const c = card._dmg, est = c.side === 'mine' ? mEst() : tEst(), svg = (card.querySelector('g.dmg-badge') || {}).ownerSVGElement;
    if(svg) for(const g of svg.querySelectorAll('g.dmg-badge')){
      const label = ((g.querySelector('title') || {}).textContent || '').split(':')[0], ic = P.iconFor(est, label);
      if(!ic) continue;
      const cat = [...g.classList].find(x => CAT_VAR[x]), col = `var(${CAT_VAR[cat]})`;
      const r = g.querySelector('rect'), t = g.querySelector('text');
      const cx = +r.getAttribute('x') + 8, y0 = +r.getAttribute('y');
      r.setAttribute('x', cx - 10); r.setAttribute('y', y0 - 4); r.setAttribute('width', 20); r.setAttribute('height', 20);
      r.style.fill = 'var(--panel)'; t.style.fill = col; t.setAttribute('y', +t.getAttribute('y') - 2);
      if(P.badgeStyle === 'thin'){ r.style.stroke = col; r.style.strokeOpacity = '0.5'; r.style.strokeWidth = '1'; }
      else { r.style.stroke = 'none';
        const bar = document.createElementNS(NS, 'rect'); bar.setAttribute('x', cx - 7); bar.setAttribute('y', y0 + 17); bar.setAttribute('width', 14); bar.setAttribute('height', 2); bar.setAttribute('rx', 1); bar.style.fill = col; g.appendChild(bar); }
      const img = document.createElementNS(NS, 'image');
      img.setAttribute('href', `https://images.evetech.net/types/${ic.id}/icon?size=32`); img.setAttribute('x', cx - 9); img.setAttribute('y', y0 - 3); img.setAttribute('width', 18); img.setAttribute('height', 18);
      g.appendChild(img); g.dataset.protoLabel = label;
      g.querySelector('title').textContent = `${ic.name} · ${g.querySelector('title').textContent}`;
    }
    for(const row of card.querySelectorAll('.dmg-ck-row')){
      const b = row.querySelector('.ewar-badge'); if(!b) continue;
      const label = (row.querySelector('.dmg-ck-l') || {}).textContent || '', ic = P.iconFor(est, label); if(!ic) continue;
      const cat = [...b.classList].find(x => CAT_VAR[x]), col = `var(${CAT_VAR[cat]})`;
      b.style.cssText = `background:var(--panel);padding:0;width:20px;height:20px;display:inline-flex;align-items:center;justify-content:center;box-sizing:border-box;color:${col};` +
        (P.badgeStyle === 'thin' ? `border:1px solid color-mix(in srgb, ${col} 50%, transparent);border-radius:3px;` : `border-bottom:2px solid ${col};border-radius:2px;`);
      b.innerHTML = `<img src="https://images.evetech.net/types/${ic.id}/icon?size=32" width="18" height="18" alt="${b.textContent}" style="display:block">`;
      row.dataset.protoLabel = label; row.title = ic.name;
    }
  };
  // the linked highlight: hovering or tapping a badge lights its key row, and the other way round
  P.highlight = (card, label) => {
    card.querySelectorAll('[data-proto-label]').forEach(e => {
      const on = e.dataset.protoLabel === label;
      if(e.tagName === 'g'){ const r = e.querySelector('rect'); r.style.strokeOpacity = on ? '1' : (P.badgeStyle === 'thin' ? '0.5' : ''); r.style.strokeWidth = on ? '2' : '1'; if(on && P.badgeStyle !== 'thin'){ r.style.stroke = 'var(--text)'; } else if(P.badgeStyle !== 'thin') r.style.stroke = 'none'; }
      else e.style.background = on ? 'var(--line-soft)' : '';
    });
  };
  document.addEventListener('mouseover', (e) => { const t = e.target.closest && e.target.closest('[data-proto-label]'); const card = t && t.closest('.dmg-card'); if(card) P.highlight(card, t.dataset.protoLabel); });
  const origDraw = dmgDraw;
  window.dmgDraw = function(card){
    origDraw(card);
    const c = card._dmg; if(!c || !c.f || !c.f.dmg) return;
    let el = card.querySelector('.proto-ewar-line');
    const txt = c.side === 'mine' ? P.lineMine(c.f.dmg.range) : P.lineTheirs(c.f.dmg.range);
    const anchor = card.querySelector('.dmg-ck-note');
    if(!el && anchor){ el = document.createElement('div'); el.className = 'proto-ewar-line'; anchor.closest('div').after(el); }
    if(el){ el.textContent = txt; el.hidden = !txt; }
    P.iconize(card);
  };
  // the Matchup's "why" panels
  const origM = mysMatchup;
  window.mysMatchup = function(tf, mf, st){
    P.range = st.range;
    const m = origM(tf, mf, st);
    if(!m || !P.phase) return m;
    const d = st.range, me = mEst(), te = tEst();
    if(P.phase >= 2 && (ew('neut').length || ew('nos').length)){ const c = P.cap(d);
      m.why.you.text.push(`Their ${plural(count(ew('neut')), 'neut', 'neuts')} and ${plural(count(ew('nos')), 'nos', 'nos')} at ${km(d)} drain ${Math.round(c.gjs)} GJ/s: your capacitor empties at ${mmss(capT(c))} (${mmss(me.capacitor.stable ? null : me.capacitor.timeToEmptyExactSec)} without them), and your repairers stop then. Nosferatu are counted in full, as pyfa does (it assumes you have more capacitor than them).`); }
    if(P.phase >= 3 && ew('ecm').length) m.why.you.text.push(`Their ECM: ${Math.round(P.jam(d) * 100)}% chance each cycle to jam you (your sensor strength ${Math.round(num(me.sensorStrength) * 10) / 10}). A jam stops your locks, not their damage, so the time above doesn't change.`);
    if(P.phase >= 3) m.why.you.text.push(`They lock you in ${P.lockTime(num(te.scanResolution), num(me.signatureRadius)).toFixed(1)} s.`);
    if(P.phase >= 1 && ew('trackingDisruptor').length){ const t = P.td(d);
      m.why.them.text.unshift(`Their ${plural(count(ew('trackingDisruptor')), 'tracking disruptor', 'tracking disruptors')} at ${km(d)}: your turrets' optimal ${pct((t.optimal - 1) * 100)}, falloff ${pct((t.falloff - 1) * 100)}, tracking ${pct((t.tracking - 1) * 100)}, counted in your damage.`); }
    if(P.phase >= 3){ m.why.them.text.push(`Their dampener cuts your lock range to ${km(P.lock(d))} (${km(P.lock0())} without it); past it you deal nothing. You lock them in ${P.lockTime(num(me.scanResolution), num(te.signatureRadius)).toFixed(1)} s.`); }
    return m;
  };
  P.redraw = () => { const h = host(); if(!h) return; const tf = mysStripThreatF(h); capMemo.clear(); mysFightSet(h, 'range', tf.dmg.range); };
  P.set = (ph, style) => { P.phase = ph; if(style) P.badgeStyle = style; P.redraw(); };
  const css = document.createElement('style');
  css.textContent = `.proto-ewar-line{margin:6px 0 0; font-size:12px; color:var(--text-dim); line-height:1.4}`;
  document.head.appendChild(css);
  P.mark();
})();
