// Live-data map filters (Project doc claude/roadmap/live-map-filters-plan.md, answered 2026-11-20): four new filters in 058's column,
// made-up live data, the phone column by group. Mockup shortcuts the build must not copy are listed in README.md.
(() => {
  // ---- made-up alliances: [name, ticker, standing, logo background, logo colour, logo shape]. Logos are invented emblems (data URLs);
  // the build loads https://images.evetech.net/alliances/{id}/logo?size=64 into a plain <img> (the CSP allows that host).
  const ALL = [
    ['Mockup Coalition', 'MKCO', 'yours', '#16345c', '#a9d4ff', 'star'],
    ['Mockup Raiders', 'MKRD', 'hostile', '#4a1414', '#ff9c7c', 'fang'],
    ['Mockup Northern Pact', 'MKNP', 'friendly', '#123f45', '#8fe3e0', 'chevron'],
    ['Mockup Lantern Guild', 'MKLG', 'friendly', '#3c3412', '#f2d36b', 'ring'],
    ['Mockup Black Tide', 'MKBT', 'hostile', '#1a1a24', '#d96a6a', 'wave'],
    ['Mockup Ember Syndicate', 'MKES', 'neutral', '#3d1d0c', '#ffb36b', 'triangle'],
    ['Mockup Quiet Hands', 'MKQH', 'neutral', '#24283a', '#c7cde8', 'diamond'],
    ['Mockup Deep Current', 'MKDC', 'neutral', '#0e2a33', '#6fc6a8', 'bars'],
    ['Mockup Iron Choir', 'MKIC', 'neutral', '#2b2b2b', '#d0d0d0', 'cross'],
    ['Mockup Far Reach', 'MKFR', 'neutral', '#1d2f16', '#b5e07a', 'arrow'],
    ['Mockup Glass Order', 'MKGO', 'neutral', '#2a1836', '#e0b8f0', 'hex'],
    ['Mockup Second Dawn', 'MKSD', 'neutral', '#3a2a10', '#ffe08a', 'sun'],
  ];
  const GLYPH = {
    star: '<path d="M32 12l5.9 12.6 13.8 1.6-10.2 9.4 2.8 13.6L32 42.4 19.7 49.2l2.8-13.6-10.2-9.4 13.8-1.6z"/>',
    fang: '<path d="M16 16h32L40 48 32 30 24 48z"/>',
    chevron: '<path d="M14 22l18 12 18-12v9L32 43 14 31zM14 34l18 12 18-12v7L32 53 14 41z"/>',
    ring: '<circle cx="32" cy="32" r="15" fill="none" stroke-width="7"/><circle cx="32" cy="32" r="4"/>',
    wave: '<path d="M10 30c7-8 14-8 22 0s15 8 22 0v9c-7 8-14 8-22 0s-15-8-22 0z"/>',
    triangle: '<path d="M32 12l20 38H12z"/>',
    diamond: '<path d="M32 10l20 22-20 22-20-22z"/>',
    bars: '<path d="M14 18h10v28H14zM27 12h10v40H27zM40 22h10v20H40z"/>',
    cross: '<path d="M27 10h10v17h17v10H37v17H27V37H10V27h17z"/>',
    arrow: '<path d="M12 34h26V22l16 12-16 12V38H12z"/>',
    hex: '<path d="M32 10l19 11v22L32 54 13 43V21z"/>',
    sun: '<circle cx="32" cy="32" r="10"/><path d="M30 8h4v10h-4zM30 46h4v10h-4zM8 30h10v4H8zM46 30h10v4H46z"/>',
  };
  const logoUrl = (a) => 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><rect width="64" height="64" fill="${a[3]}"/><g fill="${a[4]}" stroke="${a[4]}">${GLYPH[a[5]]}</g></svg>`);
  const ST = {yours: '#4f8fe0', friendly: '#8db8f2', neutral: '#a8b2b9', hostile: '#c65b4e', npc: '#7a6f58', none: '#56616b'};   // by standing (the page's side colours)
  const ST_WORD = {yours: 'your alliance', friendly: 'friendly', neutral: 'neutral', hostile: 'hostile'};
  const JP = ['#2a3640', '#2f5d63', '#3f8a83', '#6fb59a', '#b8d88a', '#f0f0b0'], JS = [0, 1, 10, 50, 150, 500];   // Jumps (past hour): 0 / 1–9 / 10–49 / 50–149 / 150–499 / 500+
  const KP = ['#2a3640', '#6b4a52', '#9a4f55', '#c65b4e', '#ef8f78'], KS = [0, 1, 2, 5, 20], KN = [0, 1, 50, 200, 500];   // Kills: ships + pods 0 / 1 / 2–4 / 5–19 / 20+; NPC 0 / 1–49 / 50–199 / 200–499 / 500+
  const NPC_REG = ['Curse', 'Great Wildlands', 'Stain', 'Syndicate', 'Outer Ring', 'Venal', 'Pochven'];
  const step = (v, S) => { let k = 0; while(k + 1 < S.length && v >= S[k + 1]) k++; return k; };
  const fmt = (v) => v >= 1000 ? (v / 1000).toFixed(v >= 10000 ? 0 : 1) + 'k' : String(v);
  const pad = (n) => String(n).padStart(2, '0');

  const L = window.MKL = {ALL, ST, ring: 'ring', logos: true, grouped: true, img: [], H: null, jumps: null, kills: null, cap: new Set(), dev: null, asOf: {}, edges: null, allCol: null, inView: '', logoDraws: 0, soft: 'more'};
  L.holderOf = (i) => L.H ? L.H[i] : -1;   // -2 NPC faction, -1 unclaimed, else the alliance's index
  L.standing = (h) => h >= 0 ? ALL[h][2] : h === -2 ? 'npc' : 'none';
  L.sovCol = (i) => { const h = L.holderOf(i); if(h === -2) return ST.npc; if(h < 0) return ST.none; return itMapSt().sovBy === 'alliance' ? L.allCol[h] : ST[ALL[h][2]]; };
  L.killN = (i) => { const k = L.kills[i]; return itMapSt().killNpc ? k[2] : k[0] + k[1]; };

  // ---- the made-up live data, from the page's own map table (deterministic)
  let seed = 20261120; const rnd = () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  const gauss = () => { let u = 0, v = 0; while(!u) u = rnd(); while(!v) v = rnd(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
  L.seed = () => {
    const T = itMapTable(), n = T.n, g = itGraphGet(), H = new Int16Array(n).fill(-2), sec = (i) => itMapSecT(i);
    const npcReg = new Set(NPC_REG.map(r => T.regions.indexOf(r)).filter(r => r >= 0));
    const nul = (i) => sec(i) <= 0 && !npcReg.has(T.reg[i]);
    for(let i = 0; i < n; i++) if(nul(i)) H[i] = -3;   // to be claimed
    const at = (nm) => g.at.get(it.names.byLower.get(nm.toLowerCase()));
    const seeds = [itm.home, at('MSG-BZ')];
    // the other alliances: spread over null-sec (farthest point first, on the flat map)
    const cand = []; for(let i = 0; i < n; i++) if(H[i] === -3) cand.push(i);
    const d2 = (a, b) => { const dx = T.xs[a] - T.xs[b], dy = T.ys[a] - T.ys[b]; return dx * dx + dy * dy; };
    while(seeds.length < ALL.length){ let best = -1, bd = -1; for(const i of cand){ let m = Infinity; for(const s of seeds) m = Math.min(m, d2(i, s)); if(m > bd){ bd = m; best = i; } } seeds.push(best); }
    // each claims outward by gate, taking turns (yours and the Raiders get a head start near you)
    const qs = seeds.map((s, k) => { H[s] = k; L.cap.add(s); return [s]; });
    for(let r = 0; r < 4; r++) for(const k of [0, 1]){ const nq = []; for(const i of qs[k]) for(const j of T.adj[i]) if(H[j] === -3){ H[j] = k; nq.push(j); } qs[k] = qs[k].concat(nq); }
    let busy = true;
    while(busy){ busy = false; qs.forEach((q, k) => { const nq = []; for(const i of q) for(const j of T.adj[i]) if(H[j] === -3){ H[j] = k; nq.push(j); } qs[k] = nq; if(nq.length) busy = true; }); }
    for(let i = 0; i < n; i++){ if(H[i] === -3) H[i] = -1; else if(H[i] >= 0 && !L.cap.has(i) && i !== itm.home && rnd() < 0.05) H[i] = -1; }   // a few unclaimed
    L.H = H;
    // per alliance: neighbour-distinct colours (Region's palette and method)
    const nb = ALL.map(() => new Set());
    for(let i = 0; i < n; i++) for(const j of T.adj[i]) if(H[i] >= 0 && H[j] >= 0 && H[i] !== H[j]){ nb[H[i]].add(H[j]); nb[H[j]].add(H[i]); }
    const c = new Array(ALL.length).fill(-1);
    for(const a of [...ALL.keys()].sort((p, q) => nb[q].size - nb[p].size)){ let k = 0; while([...nb[a]].some(b => c[b] === k)) k++; c[a] = k % IT_MAP_REGION.length; }
    L.allCol = c.map(k => IT_MAP_REGION[k]);
    // gate lines with the same holder at both ends, per alliance (worked out once per sov read)
    L.edges = ALL.map(() => []);
    for(let i = 0; i < n; i++) for(const j of T.adj[i]) if(j > i && H[i] >= 0 && H[i] === H[j]) L.edges[H[i]].push(i, j);
    // development levels, ADM, held since, vulnerability window
    L.dev = Array.from({length: n}, () => null);
    for(let i = 0; i < n; i++) if(H[i] >= 0){ const m = Math.floor(rnd() * 6), d = Math.floor(rnd() * 6), s = Math.floor(rnd() * 6), h = 15 + Math.floor(rnd() * 8);
      L.dev[i] = {m, i: d, s, adm: Math.min(6, 1 + (m + d + s) / 3.2 + rnd()).toFixed(1), since: new Date(Date.now() - (30 + rnd() * 900) * 86400e3).toISOString().slice(0, 10), vw: `${pad(h)}:00–${pad((h + 4) % 24)}:00`}; }
    // jumps and kills in the past hour (spreads like the live answers read 2026-11-20: jumps median ~14; ship+pod kills in ~9% of systems)
    const J = new Uint16Array(n), K = Array.from({length: n}, () => [0, 0, 0]);
    for(let i = 0; i < n; i++){
      const s = sec(i), mul = s >= 5 ? 3 : s > 0 ? 1.2 : 0.45;
      J[i] = rnd() < 0.06 ? 0 : Math.min(2700, Math.round(Math.exp(Math.log(14) + 1.35 * gauss()) * mul));
      if(rnd() < 0.085 * (s > 0 ? 0.9 : 1.2)){ const r = rnd(); K[i][0] = r < 0.4 ? 1 : r < 0.75 ? 2 + Math.floor(rnd() * 3) : r < 0.95 ? 5 + Math.floor(rnd() * 15) : 20 + Math.floor(rnd() * 60); K[i][1] = Math.floor(K[i][0] * rnd() * 0.7); }
      if(s <= 0 && rnd() < 0.75) K[i][2] = Math.round(Math.exp(Math.log(74) + 1.1 * gauss()));
    }
    for(const nm of ['78-0R6', 'MSG-BZ', 'SHBF-V']){ const i = at(nm); if(i !== undefined){ K[i] = [3 + (nm.length % 4), 2, 40]; J[i] = Math.max(J[i], 60); } }   // where the reports are
    L.jumps = J; L.kills = K;
    const t = new Date(Date.now() - 9 * 60e3), u = new Date(Date.now() - 20 * 60e3), hm = (d) => `${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())}`;
    L.asOf = {jumps: hm(t), kills: hm(u), sov: hm(new Date(Date.now() - 2 * 60e3))};
    L.img = ALL.map(a => { const im = new Image(); im.onload = () => { if(L.img.every(x => x.complete)) itMapDraw(); }; im.src = logoUrl(a); return im; });
  };

  // ---- the four filters in 058's column (Colour: one or none; Only: stacked)
  const IC = (p) => `<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${p}</svg>`;
  const NEW_C = [
    {k: 'sovh', g: 'colour', name: 'Sov holder', note: 'colour: who holds each system, by your standings or one colour per alliance; zoomed in, the holder’s logo',
      icon: IC('<path d="M4.5 16V2.5"/><path d="M4.5 3h9.5l-2.2 3.2L14 9.5H4.5" fill="currentColor"/>')},
    {k: 'jumph', g: 'colour', name: 'Jumps (past hour)', note: 'colour: ship jumps through each system in the past hour (ESI); zoomed in, the number',
      icon: IC('<circle cx="9" cy="9" r="6.5"/><path d="M5 9h7.2M9.8 6.4L12.4 9l-2.6 2.6"/>')},
    {k: 'killh', g: 'colour', name: 'Kills (past hour)', note: 'colour: ship and pod kills in each system in the past hour (ESI); NPC kills in its settings',
      icon: IC('<circle cx="9" cy="9" r="6.5"/><path d="M6.6 6.6l4.8 4.8M11.4 6.6l-4.8 4.8" stroke-width="2"/>')},
  ];
  const NEW_O = {k: 'regpick', g: 'only', name: 'Region pick', note: 'only: systems in the regions you pick',
    icon: IC('<path d="M2.5 4.6l4-2 5 2 4-2v10.8l-4 2-5-2-4 2z"/><path d="M6.5 2.6v10.8M11.5 4.6v10.8"/>')};
  IT_MAP_FILTERS.splice(IT_MAP_FILTERS.findIndex(f => f.k === 'region') + 1, 0, ...NEW_C);
  IT_MAP_FILTERS.splice(IT_MAP_FILTERS.findIndex(f => f.k === 'sov') + 1, 0, NEW_O);
  IT_MAP_COLOURS.push('sovh', 'jumph', 'killh'); IT_MAP_ONLY.push('regpick');
  const pb = (k, t) => () => `<button type="button" class="it-map-pb" data-it-mpn="${k}" aria-haspopup="dialog" aria-expanded="false" aria-label="${t}" title="${t}">${IT_MAP_SET_ICON}</button>`;
  IT_MAP_PANEL_BTN.sovh = pb('sovh', 'Sov holder: by standing or by alliance');
  IT_MAP_PANEL_BTN.killh = pb('killh', 'Kills (past hour): ships and pods or NPC kills');
  IT_MAP_PANEL_BTN.regpick = pb('regpick', 'Region pick: which regions');

  // the stack's new fields (a build: itMapStackBlank / itMapStackRead / itMapStKey; safe both ways, an older page ignores and drops them)
  const blank0 = itMapStackBlank, read0 = itMapStackRead, key0 = itMapStKey;
  itMapStackBlank = function(){ return Object.assign(blank0(), {sovBy: 'standing', killNpc: false, regions: []}); };
  itMapStackRead = function(){
    const o = read0(); let s = null; try{ s = JSON.parse(localStorage.getItem(MAP_STACK_KEY)); }catch(e){ s = null; }
    if(s && typeof s === 'object'){ if(s.sovBy === 'alliance') o.sovBy = 'alliance'; o.killNpc = s.killNpc === true;
      if(Array.isArray(s.regions)){ const R = itMapTable().regions; o.regions = [...new Set(s.regions.filter(r => typeof r === 'string' && R.includes(r)))]; } }   // an unknown region dropped
    return o;
  };
  itMapStKey = function(){ const s = itMapSt(); return key0() + JSON.stringify([s.sovBy, s.killNpc, s.regions]); };

  // the column in groups (L6): wrappers that are display:contents on a wide map (the desktop column as today), two columns on a phone
  const fbtns0 = itMapFbtnsHtml;
  itMapFbtnsHtml = function(){
    if(!L.grouped) return fbtns0();
    const sep = (t) => `<span class="it-map-fsep" aria-hidden="true" title="${escapeHtml(t)}"></span>`;
    const one = (f) => IT_MAP_PANEL_BTN[f.k] ? `<span class="it-map-fw">${itMapFbtnHtml(f)}${itMapPanelBtnHtml(f.k)}</span>` : itMapFbtnHtml(f);
    const grp = (g, lab) => `<div class="mk-fg mk-fg-${g}" role="group" aria-label="${lab}">${IT_MAP_FILTERS.filter(f => f.g === g).map(one).join('')}</div>`;
    return grp('colour', 'Colour: one at a time') + sep('Only: switch on any number; every one that is on must match') + grp('only', 'Only: any number') + sep('View') + grp('view', 'View');
  };
  window.__MKn = (bs) => bs.querySelectorAll('[data-im-f], .it-map-fsep').length;

  // soft colour turned up ([stated] 2026-11-20 "i know we went to softer colors, can we turn it up just a bit though?", then "let's go
  // with the "More" option on the colors."): 058 keeps 55% of a colour zoomed out (itMapFcol) and 38% in a zoomed-in disc; More is 80% / 62%
  // (a build changes the two numbers; the MOCKUP box keeps the other steps to compare)
  const SOFT = {today: [0.55, 0.38], up: [0.68, 0.5], more: [0.8, 0.62]};
  const mix0 = itMapMix;
  itMapMix = function(hex, keep){ const t = SOFT[L.soft] || SOFT.today; return mix0(hex, keep === 0.55 ? t[0] : keep === 0.38 ? t[1] : keep); };
  // colours
  const colRaw0 = itMapColRaw;
  itMapColRaw = function(i){
    const c = itMapSt().colour;
    if(c === 'sovh') return L.sovCol(i);
    if(c === 'jumph') return JP[step(L.jumps[i], JS)];
    if(c === 'killh') return KP[step(L.killN(i), itMapSt().killNpc ? KN : KS)];
    return colRaw0(i);
  };
  // Q10 ([stated] 2026-11-20 "ok, go with your choice for now."): Sov holder, Jumps (past hour) and Kills (past hour) skip the fades
  // past Near You and past "Map: within" (only Only filters dim); the gates still fade; Security, Jumps from you and Region as today
  const NOFADE = ['sovh', 'jumph', 'killh'];
  window.__MKnofade = () => !itMapPaths() && NOFADE.includes(itMapSt().colour);
  const legend0 = itMapLegend;
  itMapLegend = function(){ legend0(); if(!window.__MKnofade()) return; const leg = itm.el.querySelector('.it-map-leg'); for(const sp of leg.querySelectorAll(':scope > span')) if(/^(faded|faint): past/.test(sp.textContent)) sp.remove(); };
  // the holder's gate lines (1b: the game draws a line between two systems of one holder in its colour)
  window.__MKgates = (c, X, Y, on, big, W, H) => {
    if(itMapSt().colour !== 'sovh' || itMapPaths() || !L.edges) return;
    const mt = itm.mt, by = itMapSt().sovBy;
    c.save(); c.lineWidth = big ? 2 : 1.2;
    L.edges.forEach((E, h) => {
      if(!E.length) return;
      const col = by === 'alliance' ? L.allCol[h] : ST[ALL[h][2]];
      for(const lit of [true, false]){
        c.beginPath(); let any = false;
        for(let e = 0; e < E.length; e += 2){ const a = E[e], b = E[e + 1];
          if((X(a) < 0 && X(b) < 0) || (X(a) > W && X(b) > W) || (Y(a) < 0 && Y(b) < 0) || (Y(a) > H && Y(b) > H)) continue;
          const l = mt ? !!(mt.m[a] && mt.m[b]) : window.__MKnofade() || (on(a) && on(b)); if(l !== lit) continue;
          c.moveTo(X(a), Y(a)); c.lineTo(X(b), Y(b)); any = true; }
        if(any){ c.strokeStyle = col; c.globalAlpha = lit ? 0.75 : mt ? 0.12 : 0.3; c.stroke(); }
      }
    });
    c.restore();
  };
  // zoomed in: the holder's logo fills the circle, ringed in the holder's colour (MOCKUP: or on a disc of it)
  window.__MKcircle = (c, i, x, y, r, a, hit) => {
    if(itMapSt().colour !== 'sovh') return false;
    const h = L.holderOf(i); if(h < 0) return false;
    const col = L.sovCol(i), im = L.img[h], disc = L.ring === 'disc';
    c.save(); c.globalAlpha = a;
    c.fillStyle = disc ? col : '#0c1014'; c.beginPath(); c.arc(x, y, r, 0, 6.283); c.fill();
    const lr = disc ? r - 3 : r - 1.5;
    L.logoDraws++;
    if(L.logos && im && im.complete){ c.save(); c.beginPath(); c.arc(x, y, lr, 0, 6.283); c.clip(); c.drawImage(im, x - lr, y - lr, 2 * lr, 2 * lr); c.restore(); }
    c.lineWidth = disc ? 1.5 : 2; c.strokeStyle = disc ? '#0c1014' : col; c.beginPath(); c.arc(x, y, disc ? r : r - 1, 0, 6.283); c.stroke();
    if(L.cap.has(i)){ c.fillStyle = '#ffd76a'; c.font = `700 ${Math.round(r * 0.8)}px system-ui, sans-serif`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('★', x + r * 0.85, y - r * 0.85); }
    c.restore(); return true;
  };
  window.__MKnum = (c, i, x, y, col) => {
    if(col === 'sovh'){ const h = L.holderOf(i); if(h < 0) return false;
      if(!(L.logos && L.img[h] && L.img[h].complete)){ const f = c.font; c.font = `700 ${Math.max(7, Math.round(parseFloat(f.split(' ')[1]) * 0.62))}px system-ui, sans-serif`; c.fillText(ALL[h][1], x, y + 0.5); c.font = f; }   // a logo not loaded: the ticker
      return true; }
    if(col === 'jumph'){ c.fillText(fmt(L.jumps[i]), x, y + 0.5); return true; }
    if(col === 'killh'){ c.fillText(fmt(L.killN(i)), x, y + 0.5); return true; }
    return false;
  };
  // Region pick (L3): any pick counts
  let regKey = '', regSet = new Set();
  window.__MKreg = (i) => { const s = itMapSt(), k = s.regions.join('|'); if(k !== regKey){ const R = itMapTable().regions; regKey = k; regSet = new Set(s.regions.map(r => R.indexOf(r))); } return regSet.has(itMapTable().reg[i]); };

  // the hover's lines
  const logoTag = (h) => L.logos ? `<img src="${L.img[h].src}" width="16" height="16" alt="" style="vertical-align:-3px;border-radius:2px;margin-right:4px">` : '';
  window.__MKtip = (i) => {
    const col = itMapSt().colour;
    if(col === 'sovh'){
      const h = L.holderOf(i);
      if(h === -2) return '<br><span class="d">NPC faction space</span>';
      if(h === -1) return '<br><span class="d">unclaimed</span>';
      const a = ALL[h], d = L.dev[i], sw = ST_WORD[a[2]];
      return `<br>${logoTag(h)}<b>${escapeHtml(a[0])}</b> [${escapeHtml(a[1])}] <span class="${a[2] === 'hostile' ? 'hostile' : a[2] === 'neutral' ? 'd' : 'friendly'}">${sw}</span>${L.cap.has(i) ? ' · ★ capital' : ''}`
        + `<br><span class="d">held by ${escapeHtml(a[0] + ' Holding')} since ${d.since}</span>`
        + `<br><span class="d">Military ${d.m} · Industrial ${d.i} · Strategic ${d.s} · ADM ${d.adm}</span><br><span class="d">vulnerable ${d.vw} EVE</span>`;
    }
    if(col === 'jumph') return `<br>${L.jumps[i]} jump${L.jumps[i] === 1 ? '' : 's'} in the past hour <span class="d">(ESI, as of ${L.asOf.jumps} EVE)</span>`;
    if(col === 'killh'){ const k = L.kills[i]; return `<br>${k[0]} ship${k[0] === 1 ? '' : 's'} · ${k[1]} pod${k[1] === 1 ? '' : 's'} · ${k[2]} NPC killed in the past hour <span class="d">(ESI, as of ${L.asOf.kills} EVE)</span>`; }
    return '';
  };

  // the legend's colour line, its hover, the Only line
  const sw = (cols) => itMapSwHtml(cols);
  const leg0 = itMapFLegHtml, legT0 = itMapFLegTitle, only0 = itMapOnlyHtml;
  itMapFLegHtml = function(){
    if(itMapPaths()) return leg0();
    const s = itMapSt();
    if(s.colour === 'sovh') return s.sovBy === 'alliance' ? `<b>Sov holder</b> ${sw(L.allCol.filter((x, k, a) => a.indexOf(x) === k))} one per alliance ${sw([ST.npc])} NPC ${sw([ST.none])} unclaimed · as of ${L.asOf.sov} EVE`
      : `<b>Sov holder</b> ${sw([ST.yours])} yours ${sw([ST.friendly])} friendly ${sw([ST.neutral])} neutral ${sw([ST.hostile])} hostile ${sw([ST.npc])} NPC ${sw([ST.none])} unclaimed`;
    if(s.colour === 'jumph') return `<b>Jumps (past hour)</b> 0 ${sw(JP)} 500+ · as of ${L.asOf.jumps} EVE`;
    if(s.colour === 'killh') return s.killNpc ? `<b>NPC kills (past hour)</b> 0 ${sw(KP)} 500+ · as of ${L.asOf.kills} EVE` : `<b>Kills (past hour)</b> ships + pods 0 ${sw(KP)} 20+ · as of ${L.asOf.kills} EVE`;
    return leg0().replace('press Security, Jumps or Region', 'press a colour');
  };
  itMapFLegTitle = function(){
    const s = itMapSt();
    if(!itMapPaths() && s.colour === 'sovh') return s.sovBy === 'alliance' ? 'Who holds each system: one colour per alliance, neighbours differ; NPC faction space and unclaimed systems plain. From ESI, every 5 minutes while this is on.'
      : 'Who holds each system, by your standings (your corporation’s and alliance’s EVE contacts, else your typed lists): yours, friendly, neutral, hostile; NPC faction space; unclaimed. From ESI, every 5 minutes while this is on.';
    if(!itMapPaths() && s.colour === 'jumph') return 'Ship jumps through each system in the past hour, from ESI (once an hour); 0, 1–9, 10–49, 50–149, 150–499, 500 or more';
    if(!itMapPaths() && s.colour === 'killh') return s.killNpc ? 'NPC kills in each system in the past hour, from ESI; 0, 1–49, 50–199, 200–499, 500 or more' : 'Ships and pods killed in each system in the past hour, from ESI; 0, 1, 2–4, 5–19, 20 or more';
    return legT0();
  };
  itMapOnlyHtml = function(){
    let h = only0(); const s = itMapSt();
    if(s.only.regpick){ const rs = s.regions, t = rs.length ? 'in ' + (rs.length > 2 ? `${rs.slice(0, 2).join(', ')} +${rs.length - 2}` : rs.join(', ')) : 'no region picked';
      h = h.endsWith(' · ') ? h + escapeHtml(t) : h + ' · ' + escapeHtml(t); }
    return h;
  };
  // "holders in view" in the legend, with logos (written only when it changes; a build keys it to the view, not every draw)
  window.__MKdrawn = () => {
    const leg = itm.el && itm.el.querySelector('.it-map-leg'); if(!leg) return;
    let html = '';
    if(itMapSt().colour === 'sovh' && !itMapPaths() && L.H){
      const cnt = new Map(), Q = itm.Q, W = itm.W, H = itm.H;
      for(let i = 0; i < L.H.length; i++){ const h = L.H[i]; if(h < 0) continue; const x = Q[2 * i], y = Q[2 * i + 1]; if(x < 0 || y < 0 || x > W || y > H) continue; cnt.set(h, (cnt.get(h) || 0) + 1); }
      const top = [...cnt].sort((p, q) => q[1] - p[1]);
      if(top.length) html = '<b>In view</b> ' + top.slice(0, 5).map(([h, k]) => `<span class="mk-hv1" title="${escapeHtml(ALL[h][0])}: ${k} system${k === 1 ? '' : 's'}">${logoTag(h)}${escapeHtml(ALL[h][1])} <span class="d">${k}</span></span>`).join(' ') + (top.length > 5 ? ` <span class="d">+${top.length - 5}</span>` : '');
    }
    let el = leg.querySelector('.mk-hv');
    if(!html){ if(el) el.remove(); return; }
    if(!el){ el = document.createElement('div'); el.className = 'it-map-fl mk-hv'; const after = leg.querySelector('.it-map-only') || leg.querySelector('.it-map-fl'); after.after(el); }
    if(el._h !== html){ el.innerHTML = html; el._h = html; }
  };

  // ---- the settings panels (058's itMp: one at a time, beside its filter)
  const body0 = itMpBodyHtml;
  itMpBodyHtml = function(k){
    const s = itMapSt(), rad = (nm, v, on, t) => `<label class="it-sov-k"><input type="radio" name="${nm}" value="${v}"${on ? ' checked' : ''}> <span>${t}</span></label>`;
    if(k === 'sovh') return `<div class="it-mp-note">Colour each system by:</div>${rad('mkSovBy', 'standing', s.sovBy !== 'alliance', 'Your standings')}${rad('mkSovBy', 'alliance', s.sovBy === 'alliance', 'One colour per alliance')}`
      + '<div class="it-mp-note">Standings: your corporation’s and alliance’s EVE contacts, else your typed lists (Intel settings). Zoomed in, the holder’s logo fills each system’s circle. The hover names the holder.</div>';
    if(k === 'killh') return `<div class="it-mp-note">Count:</div>${rad('mkKill', 'ship', !s.killNpc, 'Ships and pods (players)')}${rad('mkKill', 'npc', s.killNpc, 'NPC kills (ratting)')}<div class="it-mp-note">From ESI, once an hour. Not the same as “Kills from Intel”, which counts the kills Intel saw.</div>`;
    if(k === 'regpick'){
      const T = itMapTable(), n = new Map(); for(let i = 0; i < T.n; i++) n.set(T.reg[i], (n.get(T.reg[i]) || 0) + 1);
      const mine = T.regions[T.reg[itm.home]], pick = new Set(s.regions);
      const rows = T.regions.map((r, k) => [r, n.get(k) || 0]).filter(x => x[1]).sort((a, b) => (b[0] === mine) - (a[0] === mine) || a[0].localeCompare(b[0]));
      return `<input type="search" class="mk-rq" placeholder="Search regions" aria-label="Search regions" autocomplete="off" spellcheck="false" maxlength="40">`
        + `<div class="it-mp-q"><button type="button" data-mk-rclr>Clear</button><span class="mk-rn"></span></div>`
        // [stated] 2026-11-20 "can we add a checkbox to select all regions in the region picker?": ticks or unticks every region the list shows
        // (all of them, or those the search leaves); part ticked shows as a dash (indeterminate)
        + `<label class="it-sov-k mk-rall"><input type="checkbox" data-mk-rall> <span class="mk-rall-t">Select all</span><span class="it-sov-n mk-rall-n"></span></label><div class="mk-rl" role="group" aria-label="Regions">`
        + rows.map(([r, c]) => `<label class="it-sov-k" data-mk-r="${escapeHtml(r.toLowerCase())}"><input type="checkbox" data-mk-reg="${escapeHtml(r)}"${pick.has(r) ? ' checked' : ''}> <span>${escapeHtml(r)}${r === mine ? ' <span class="it-sov-from">(yours)</span>' : ''}</span><span class="it-sov-n">${c}</span></label>`).join('')
        + '</div><div class="it-mp-cnt" role="status"></div>';
    }
    return body0(k);
  };
  const rnPaint = () => {
    const p = itMp.el, e = p && p.querySelector('.mk-rn'); if(!e) return;
    const n = itMapSt().regions.length; e.textContent = n ? `${n} picked` : 'none picked: nothing matches';
    const all = p.querySelector('[data-mk-rall]'); if(!all) return;
    const shown = [...p.querySelectorAll('[data-mk-r]')].filter(l => !l.hidden), on = shown.filter(l => l.querySelector('input').checked).length, q = !!p.querySelector('.mk-rq').value.trim();
    all.checked = !!shown.length && on === shown.length; all.indeterminate = on > 0 && on < shown.length; all.disabled = !shown.length;
    p.querySelector('.mk-rall-t').textContent = q ? 'Select all shown' : 'Select all'; p.querySelector('.mk-rall-n').textContent = String(shown.length);
  };
  const make0 = itMpMake;
  itMpMake = function(){
    make0();
    const p = itMp.el;
    p.addEventListener('change', (e) => {
      const t = e.target, s = itMapSt();
      if(t.name === 'mkSovBy'){ s.sovBy = t.value; itMpChanged(); }
      else if(t.name === 'mkKill'){ s.killNpc = t.value === 'npc'; itMpChanged(); }
      else if(t.dataset.mkRall !== undefined){
        const shown = [...p.querySelectorAll('[data-mk-r]')].filter(l => !l.hidden).map(l => l.querySelector('input'));
        for(const b of shown) b.checked = t.checked;
        const names = shown.map(b => b.dataset.mkReg);
        s.regions = t.checked ? [...new Set([...s.regions, ...names])] : s.regions.filter(r => !names.includes(r)); itMpChanged(); rnPaint(); }
      else if(t.dataset.mkReg !== undefined){ const r = t.dataset.mkReg; s.regions = t.checked ? [...new Set([...s.regions, r])] : s.regions.filter(x => x !== r); itMpChanged(); rnPaint(); }
    });
    p.addEventListener('input', (e) => { if(!e.target.classList.contains('mk-rq')) return; const q = e.target.value.trim().toLowerCase().replace(/[\s-]/g, '');
      for(const l of p.querySelectorAll('[data-mk-r]')) l.hidden = !!q && !l.dataset.mkR.replace(/[\s-]/g, '').includes(q); rnPaint(); });
    p.addEventListener('click', (e) => { if(e.target.closest('[data-mk-rclr]')){ itMapSt().regions = []; for(const b of p.querySelectorAll('[data-mk-reg]')) b.checked = false; itMpChanged(); rnPaint(); } });
  };
  const paint0 = itMpPaint;
  itMpPaint = function(){ paint0(); rnPaint(); };
  // Region pick's list is taller than 058's two panels: it asks for more room below its top (a build: itMapPanel's room per filter)
  const panel0 = itMapPanel;
  itMapPanel = function(){ const p = panel0(); if(p && p.k === 'regpick') p.room = Math.min(420, Math.max(240, itm.H - 60)); return p; };
  // Region pick switched on with no region picked: its panel opens (as Sov upgrades with nothing picked)
  const set0 = itMapFilterSet;
  itMapFilterSet = function(k){ set0(k); const s = itMapSt(); if(k === 'regpick' && s.only.regpick && !s.regions.length && itm.box && itm.box.isConnected) itMpOpen('regpick'); };

  // ---- the mockup's own CSS: the grouped phone column; the region list
  const css = document.createElement('style');
  css.textContent = `.mk-fg{display:contents;}
  .it-mpp .mk-rq{width:100%; box-sizing:border-box; margin:2px 0 6px;} .it-mpp .mk-rl{max-height:240px; overflow:auto; margin:4px 0; padding-right:4px;} .it-mpp .mk-rn{color:var(--text-dim); font-size:11.5px; margin-left:6px;} .it-mpp .mk-rall{padding-bottom:4px; margin-bottom:2px; border-bottom:1px solid var(--line);}
  /* a part-ticked box (Select all with some picked): a dash; the page's checkbox style has no indeterminate look yet (a build adds it there) */
  input[type=checkbox]:not(.mys-sw):not(.dmg-sw):not([role=switch]):indeterminate{border-color:var(--cyan);}
  input[type=checkbox]:not(.mys-sw):not(.dmg-sw):not([role=switch]):indeterminate::before{visibility:visible; width:8px; height:0; margin-top:0; border-width:0 0 2px 0; transform:none;}
  .it-map-leg .mk-hv{gap:8px;} .it-map-leg .mk-hv .d{color:var(--text-dim);}
  @media (max-width: 599px){
    .it-map-fb.open .it-map-fbtns.mk-g{display:grid; grid-template-columns:auto auto; grid-template-rows:auto 1fr; grid-auto-flow:row; column-gap:0; row-gap:0; align-items:start; background:rgba(12,16,20,.97);}
    .it-map-fbtns.mk-g .mk-fg{display:flex; flex-direction:column; gap:2px; align-items:flex-start; min-width:92px;}
    .it-map-fbtns.mk-g .mk-fg-colour{grid-column:1; grid-row:1;}
    .it-map-fbtns.mk-g .mk-fg-view{grid-column:1; grid-row:2; margin-top:4px; padding-top:4px; border-top:1px solid var(--line);}
    .it-map-fbtns.mk-g .mk-fg-only{grid-column:2; grid-row:1 / span 2; margin-left:2px; padding-left:4px; border-left:1px solid var(--line);}
    .it-map-fbtns.mk-g > .it-map-fsep{display:none;}
    .it-mpp .mk-rl{max-height:none;}
  }`;
  document.head.appendChild(css);

  // ---- rebuild the column with the new filters; scenes for the MOCKUP box
  L.remake = () => {
    const bs = itm.el && itm.el.querySelector('.it-map-fbtns'); if(!bs) return;
    bs.innerHTML = itMapFbtnsHtml(); bs.classList.toggle('mk-g', L.grouped);
    itm.ctlKey = null; itMapFbarPaint(false);
  };
  L.apply = () => { itMapStackSave(); itm.mtStep = -1; itMapFbarPaint(true); itMapLegend(); itMpPaint(); itMapDraw(); if(itm.rep && itm.D) itm.key = itMapKey(); };
  L.zoomTo = (gpx, at) => { const i = at === undefined ? itm.home : at; itMapZoom(itm.Q[2 * i], itm.Q[2 * i + 1], gpx / itMapGatePx()); itMapCenter(false); if(at !== undefined){ const v = itm.view; v.tx = itMapFreeX() - itm.P[2 * i] * v.k; v.ty = itm.H / 2 - itm.P[2 * i + 1] * v.k; } itMapDraw(); };
  L.scene = (k) => {
    itMapPanelClose(false);
    const s = itMapSt(); s.view = 'map'; for(const o of IT_MAP_ONLY) s.only[o] = false;
    const T = itMapTable(), mine = T.regions[T.reg[itm.home]];
    if(k === 'standing'){ s.colour = 'sovh'; s.sovBy = 'standing'; L.apply(); L.zoomTo(9); }
    if(k === 'zoomin'){ s.colour = 'sovh'; L.apply(); L.zoomTo(95); }
    if(k === 'alliance'){ s.colour = 'sovh'; s.sovBy = 'alliance'; L.apply(); L.zoomTo(5); }
    if(k === 'jumps'){ s.colour = 'jumph'; L.apply(); L.zoomTo(9); }
    if(k === 'jumpsin'){ s.colour = 'jumph'; L.apply(); L.zoomTo(60); }
    if(k === 'kills'){ s.colour = 'killh'; s.killNpc = false; L.apply(); L.zoomTo(9); }
    if(k === 'npc'){ s.colour = 'killh'; s.killNpc = true; L.apply(); L.zoomTo(9); }
    if(k === 'region'){ s.colour = 'sovh'; s.sovBy = 'standing'; s.only.regpick = true; s.regions = [mine]; L.apply(); L.zoomTo(5); itMpOpen('regpick'); }
    if(k === 'today'){ s.colour = 'sec'; s.sovBy = 'standing'; s.killNpc = false; s.regions = []; L.apply(); L.zoomTo(30); }
    MKL.boxPaint();
  };
  L.boxPaint = () => { const d = document.getElementById('mkLm'); if(!d) return;
    for(const b of d.querySelectorAll('[data-mk-ring]')) b.setAttribute('aria-pressed', String(b.dataset.mkRing === L.ring));
    for(const b of d.querySelectorAll('[data-mk-logo]')) b.setAttribute('aria-pressed', String((b.dataset.mkLogo === 'on') === L.logos));
    for(const b of d.querySelectorAll('[data-mk-soft]')) b.setAttribute('aria-pressed', String(b.dataset.mkSoft === L.soft));
    for(const b of d.querySelectorAll('[data-mk-col]')) b.setAttribute('aria-pressed', String((b.dataset.mkCol === 'grouped') === L.grouped)); };
  L.boot = () => {
    const d = document.createElement('div'); d.id = 'mkLm';
    const B = (a, t) => `<button type="button" ${a}>${t}</button>`;
    d.innerHTML = `<b>MOCKUP</b> <span class="mk-fold">`
      + B('data-mk-sc="standing"', 'Sov: standing') + B('data-mk-sc="zoomin"', 'Sov: zoomed in') + B('data-mk-sc="alliance"', 'Sov: per alliance')
      + B('data-mk-sc="jumps"', 'Jumps (hour)') + B('data-mk-sc="jumpsin"', 'Jumps zoomed in') + B('data-mk-sc="kills"', 'Kills (hour)') + B('data-mk-sc="npc"', 'NPC kills') + B('data-mk-sc="region"', 'Region pick') + B('data-mk-sc="today"', 'Reset')
      + `<span>Logo circle: ${B('data-mk-ring="ring"', 'Ring (as in game)')}${B('data-mk-ring="disc"', 'Disc')}</span>`
      + `<span>Logos: ${B('data-mk-logo="on"', 'Loaded')}${B('data-mk-logo="off"', 'Not loaded (tickers)')}</span>`
      + `<span>Soft colour: ${B('data-mk-soft="today"', 'Today')}${B('data-mk-soft="up"', 'A bit up')}${B('data-mk-soft="more"', 'More')}</span>`
      + `<span>Phone column: ${B('data-mk-col="grouped"', 'By group')}${B('data-mk-col="today"', 'Today')}</span></span>`
      + B('data-mk-fold', '▾');
    document.body.appendChild(d);
    const st = document.createElement('style');
    st.textContent = `#mkLm{position:fixed; right:8px; top:8px; z-index:99; background:#2a1d3a; border:1px solid #a98bd8; border-radius:6px; padding:6px 8px; font:12px system-ui; color:#eee; display:flex; flex-wrap:wrap; gap:4px 8px; align-items:center; max-width:min(560px, calc(100vw - 32px));}
      #mkLm button{font:12px system-ui; padding:2px 6px; border:1px solid #6d5a8a; border-radius:4px; background:#3a2a50; color:#eee; cursor:pointer; min-height:0;} #mkLm button[aria-pressed="true"]{background:#a98bd8; color:#1a1024;}
      #mkLm .mk-fold{display:contents;} #mkLm.folded .mk-fold{display:none;}
      @media (max-width: 599px){ #mkLm{top:auto; bottom:8px; left:8px; right:auto;} }`;
    document.head.appendChild(st);
    if(matchMedia('(max-width: 599px)').matches) d.classList.add('folded');
    d.addEventListener('click', (e) => {
      const b = e.target.closest('button'); if(!b) return;
      if(b.dataset.mkSc) L.scene(b.dataset.mkSc);
      if(b.dataset.mkRing){ L.ring = b.dataset.mkRing; itMapDraw(); }
      if(b.dataset.mkLogo){ L.logos = b.dataset.mkLogo === 'on'; itMapDraw(); }
      if(b.dataset.mkSoft){ L.soft = b.dataset.mkSoft; itMapDraw(); }
      if(b.dataset.mkCol){ L.grouped = b.dataset.mkCol === 'grouped'; L.remake(); }
      if(b.dataset.mkFold !== undefined) d.classList.toggle('folded');
      L.boxPaint();
    });
    L.boxPaint();
  };
})();
