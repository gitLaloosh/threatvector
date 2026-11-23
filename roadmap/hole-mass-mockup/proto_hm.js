// MOCKUP prototype for the Wormholes tab's Mass panel (Project doc claude/roadmap/hole-mass-plan.md). Appended after the page's own script.
// Shortcuts not to copy into the build (see README.md): HM_FITS stands in for My Ships (the build reads each fit's masses from
// pyfaShipSpeed), HM_HULLS stands in for getType (ESI), whShellHtml / whPop / itSysName / CARD_INFO are wrapped or patched here, and the
// panel's state lives in one object (HM) instead of whS.
const HM_FITS = [   // made-up saved fits; masses as the page's fit maths would give them (hull mass from CCP's SDE; Higgs Anchor x2; ZPME x0.2)
  {id: 'mf1', name: 'Megathron', fit: 'Rolling Higgs', modes: [{k: 'hot', lab: 'MWD on', m: 296800}, {k: 'cold', lab: 'prop off', m: 196800}]},
  {id: 'mf2', name: 'Phobos', fit: 'Roller', modes: [{k: 'hot', lab: 'MWD on', m: 38000}, {k: 'cold', lab: 'prop off', m: 28000}, {k: 'zpme', lab: 'ZPME on', m: 5600}]},
  {id: 'mf3', name: 'Heron', fit: 'Light trip', modes: [{k: 'hot', lab: 'MWD on', m: 1650}, {k: 'cold', lab: 'prop off', m: 1150}]},
];
const HM_HULLS = {Heron: [1150, 1], Stratios: [9350, 2], Vexor: [11100, 2], Phobos: [14000, 2], Onyx: [15400, 2], Megathron: [98400, 3], Typhoon: [100600, 3],
  Paladin: [128000, 3], Orca: [150000, 3], Naglfar: [1260000, 4]};   // CCP's SDE (pyfa v2.70.1): mass in tonnes, rigSize
const HM_PROP = {1: 500, 2: 5000, 3: 50000, 4: 500000};   // a MWD of the hull's size (massAddition, CCP's SDE)
const HM_SAYS = {stable: 'More than 50%', reduced: 'Less than 50%', critical: 'Less than 10%', gone: 'It’s gone'};
const HM_SAYS_COL = {stable: 'var(--text)', reduced: 'var(--amber)', critical: 'var(--danger)', gone: 'var(--text-dim)'};   // the connection list's mass colours
const HM_POL = 5 * 60e3;
const HM_SVG = '<svg width="15" height="15" viewBox="0 0 16 16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><ellipse cx="8" cy="10.5" rx="6" ry="3.5"/><path d="M8 1.5v6M5.5 5L8 7.5 10.5 5"/></svg>';
const HM = {back: [], rs: false, prev: null, link: null, ty: '', st: 'stable', goal: 'roll', fin: 'this', ships: [], pl: null, open: true, ask: null, msg: ''};
const hmT = (m) => Math.round(m).toLocaleString('en-US') + ' t';
function hmSt(M, R){ return R <= 0 ? 'gone' : R / M > 0.5 ? 'stable' : R / M > 0.1 ? 'reduced' : 'critical'; }
// what the hole could be: [total, remaining] pairs. Fresh: every total within ±10%; otherwise every share that fits what it says
function hmPoss(M0, st){
  const P = [];
  if(st === 'fresh'){ for(let i = 0; i <= 160; i++){ const M = M0 * (0.9 + 0.2 * i / 160); P.push([M, M]); } return P; }
  const b = {stable: [0.5, 1], reduced: [0.1, 0.5], critical: [0, 0.1]}[st];
  for(let i = 0; i <= 60; i++){ const M = M0 * (0.9 + 0.2 * i / 60); for(let j = 0; j < 61; j++) P.push([M, M * (b[0] + (b[1] - b[0]) * (j + 0.5) / 61)]); }
  return P;
}
function hmHole(code){ const L = IT_WH_LIFE[code]; return L ? {code, life: L[0], M0: L[1], J: L[2], regen: L[3], to: itWhDestTxt(code)[0]} : null; }
// the hole of a connection, seen from system n: a side's own type (not K162), else the other side's
function hmLinkType(l, n){ const o = l.a === n ? l.b : l.a, me = whSide(l, n), ot = whSide(l, o); const t = [me && me.type, ot && ot.type].find(x => x && x !== 'K162'); return {code: t || '', k162: !t && !!((me && me.type === 'K162') || (ot && ot.type === 'K162'))}; }
function hmShipOf(r){
  if(r.fit){ const f = HM_FITS.find(x => x.id === r.fit); return f ? {name: f.name, label: `${f.name} — ${f.fit}`, est: false, fin: !!r.fin, modes: f.modes} : null; }
  const h = HM_HULLS[r.hull]; if(!h) return null;
  return {name: r.hull, label: r.hull, est: true, fin: !!r.fin, modes: [{k: 'hot', lab: 'MWD on', m: h[0] + HM_PROP[h[1]]}, {k: 'cold', lab: 'prop off', m: h[0]}]};
}
// ---- the plan: every jump one step; one ship off the side you finish on at a time
function hmNew(){
  const n = whFocus(), l = HM.link, o = l ? (l.a === n ? l.b : l.a) : null, H = hmHole(HM.ty);
  const ships = HM.ships.map(hmShipOf).filter(Boolean).map(s => ({...s, modes: s.modes.filter(m => m.m <= H.J), at: 'this', last: {out: 0, back: 0}})).filter(s => s.modes.length);
  return {H, M0: H.M0, J: H.J, goal: HM.goal, fin: HM.fin, here: whName(n), there: o ? whName(o) : 'the other side', ships, P: hmPoss(H.M0, HM.st), obs: HM.st, hist: [], done: '', reset: false};
}
function hmShare(P, m){ let c = 0; for(const x of P) if(x[1] - m <= 0) c++; return c / P.length; }
// a step moves a group of ships the same way, then one Show Info (the owner: "any way to condense it to \"2 megathrons hot\" or \"1 hot one cold\"
// etc?"). st = {g: [{i, mo}] lightest first, dir, m (the group's mass), risk, need, wait, safe}
const hmCmp = (a, b) => { for(let k = 0; k < a.length; k++) if(a[k] !== b[k]) return a[k] - b[k]; return 0; };
function hmNext(pl, now){
  if(pl.done) return null;
  const D = pl.fin, P = pl.P, S = pl.ships, Rmin = Math.min(...P.map(x => x[1])), offs = S.map((s, i) => i).filter(i => S[i].at !== D);
  if(pl.goal === 'crit' && pl.obs === 'critical' && !offs.length){ pl.done = 'crit'; return null; }
  const lightest = (s) => Math.min(...s.modes.map(m => m.m)), light = Math.min(...S.map(lightest));
  const toward = D === 'this' ? 'back' : 'out', away = D === 'this' ? 'out' : 'back';
  const pol = (g, d) => Math.max(0, ...g.map(x => { const t = S[x.i].last[d]; return t && now - t < HM_POL ? t + HM_POL : 0; }));
  const combos = (idx) => idx.reduce((acc, i) => acc.flatMap(c => S[i].modes.map(mo => c.concat([{i, mo}]))), [[]]);   // a mode for each ship (3^4 at most)
  const sum = (g) => g.reduce((a, x) => a + x.mo.m, 0);
  const fin = (g) => g.some(x => S[x.i].fin) ? 1 : 0;   // the owner: "i'd like to protect the hic until it's needed. allow a ship to be marked as the finisher."
  const out = (b, dir) => { const g = b.g.slice().sort((x, y) => x.mo.m - y.mo.m); return {g, dir, m: sum(g), risk: b.risk, need: b.need, wait: pol(g, dir), safe: b.risk > 0 ? Math.max(0, Math.floor((Rmin - (b.need - sum(g))) / 100) * 100) : 0}; };   // safe: rounded down to 100 t
  if(offs.length){   // ships off the finish side come over: a part of them can't close the hole; all of them may (roll), the heaviest last
    let best = null;
    for(let mask = 1; mask < (1 << offs.length); mask++){
      const idx = offs.filter((i, k) => mask & (1 << k)), all = idx.length === offs.length;
      for(const g of combos(idx)){
        const m = sum(g), pre = m - Math.max(...g.map(x => x.mo.m)), close = all && pl.goal === 'roll';
        const risk = hmShare(P, close ? pre : m), keep = close ? P.reduce((a, x) => a + (x[1] - m <= 0 || x[1] - m > light ? 1 : 0), 0) : 0;   // after it: closed, or the next trip over still safe
        const k = [risk > 0 ? 1 : 0, risk, fin(g), all ? 0 : 1, -keep, -m]; if(!best || hmCmp(k, best.k) < 0) best = {g, k, risk, need: close ? pre : m};
      }
    }
    return out(best, toward);
  }
  // everyone on the finish side: the heaviest group that can't close the hole goes over (for Crit it, it must come back without closing it too)
  const C = [];
  for(let mask = 1; mask < (1 << S.length); mask++){
    const idx = S.map((s, i) => i).filter(i => mask & (1 << i));
    for(const g of combos(idx)){   // it must also be able to come back: cold, lightest first; for Roll it only the last one back may close it
      const back = g.map(x => lightest(S[x.i])), m = sum(g), need = m + back.reduce((a, b) => a + b, 0) - (pl.goal === 'roll' ? Math.max(...back) : 0); C.push({g, m, need, risk: hmShare(P, need), wait: pol(g, away), fin: fin(g)}); }
  }
  if(!C.length) return {none: true};
  // the finisher waits for the end: it goes once the hole says less than 10%, when nothing else can jump, or when you send it (finOk);
  // the owner: "shouldn't the heron be saved until the end in this case?"
  const finOk = pl.obs === 'critical' || pl.finOk, nf = C.filter(c => !c.fin), pool = finOk || !nf.length ? C : nf;
  pool.sort((a, b) => (a.risk > 0) - (b.risk > 0) || (a.risk > 0 ? a.risk - b.risk || a.m - b.m : a.fin - b.fin || b.m - a.m) || a.g.length - b.g.length);   // safe: no finisher first, then heaviest; risky: least risk first
  const best = pool[0], free = best.wait ? pool.find(c => c.risk === best.risk && c.fin <= best.fin && !c.wait && c.m >= best.m * 0.75) : null;   // a free group nearly as heavy beats a wait
  const st = out(free || best, away);
  if(pool !== C && st.risk > 0 && C.some(c => c.fin && c.risk === 0)) st.finAlt = true;   // the finisher could go safely instead: offered, not chosen
  return st;
}
function hmApply(pl, st, obs, now){
  for(const x of st.g){ const s = pl.ships[x.i]; s.at = s.at === 'this' ? 'other' : 'this'; s.last[st.dir] = now; }
  let P = pl.P.map(x => [x[0], x[1] - st.m]).filter(x => hmSt(x[0], x[1]) === obs); pl.reset = false;
  if(!P.length && obs !== 'gone'){ P = hmPoss(pl.M0, obs); pl.reset = true; }   // doesn't fit the numbers: start over from what it says now
  pl.P = P.length ? P : pl.P; pl.obs = obs; pl.hist.push({short: hmShortTxt(pl, st), dir: st.dir, m: st.m, risk: st.risk, obs});
  const offs = pl.ships.filter(x => x.at !== pl.fin);
  if(obs === 'gone') pl.done = offs.length ? 'stranded' : pl.goal === 'roll' ? 'rolled' : 'closed';
}
function hmClone(pl){ return {...pl, ships: pl.ships.map(s => ({...s, last: {...s.last}})), P: pl.P, hist: pl.hist.slice()}; }
function hmPossibleSays(pl, st){ const o = new Set(); for(const x of pl.P) o.add(hmSt(x[0], x[1] - st.m)); return ['stable', 'reduced', 'critical', 'gone'].filter(k => o.has(k)); }
// a quick run against a few holes it could be: how many jumps, and whether a risky trip may come
function hmPreview(pl){
  const P = pl.P.slice().sort((a, b) => a[1] - b[1]), picks = [P[0], P[P.length >> 1], P[P.length - 1]], runs = [];
  for(const t of picks){
    const q = hmClone(pl); let R = t[1], k = 0, risky = false, now = Date.now();
    for(; k < 80; k++){ const st = hmNext(q, now); if(!st || st.none) break; if(st.risk > 0) risky = true; R -= st.m; now = Math.max(now, st.wait) + 60e3; hmApply(q, st, hmSt(t[0], R), now); if(q.done) break; }
    runs.push({k: k + 1, risky, done: q.done});
  }
  const ks = runs.map(r => r.k);
  return {lo: Math.min(...ks), hi: Math.max(...ks), risky: runs.some(r => r.risky)};
}
// ---- words
// a group in words (the owner: "can we modify verbiage to say \"in hot\", \"in cold\", \"out hot\", \"out cold\" etc? ... seeing the word \"in\" or
// \"out\" helps them understand what the step is asking them to do and where they should be when doing it.", then "\"out\" would be the side you
// dont want to end up on."): out = jumping to the side you don't finish on, in = jumping to the side you finish on (Finish in); hot = the prop
// module on when you press jump, cold = off. By ship name, its modes counted ("Megathron ×2 (1 hot, 1 cold)").
function hmDirWord(pl, st){ const toward = pl.fin === 'this' ? 'back' : 'out'; return st.dir === toward ? 'in' : 'out'; }
function hmModeWord(mo){ return mo.k === 'hot' ? 'hot' : mo.k === 'zpme' ? 'cold, ZPME on' : 'cold'; }
function hmModeHow(mo){ return mo.k === 'hot' ? `hot: ${mo.lab} when you press jump` : mo.k === 'zpme' ? 'ZPME on, prop module off' : 'cold: prop module off'; }
function hmGroups(pl, st){
  const m = new Map();
  for(const x of st.g.slice().reverse()){ const nm = pl.ships[x.i].name; if(!m.has(nm)) m.set(nm, {nm, n: 0, modes: new Map()}); const e = m.get(nm); e.n++; const w = hmModeWord(x.mo); e.modes.set(w, (e.modes.get(w) || 0) + 1); }
  return [...m.values()];
}
function hmOneMode(st){ return new Set(st.g.map(x => x.mo.k)).size === 1; }
function hmWho(pl, st){ return hmGroups(pl, st).map(e => e.n > 1 ? `${e.nm} ×${e.n}` : e.nm).join(', '); }
function hmModesOf(e){ return e.modes.size === 1 ? (e.n > 1 ? `all ${[...e.modes.keys()][0]}` : [...e.modes.keys()][0]) : [...e.modes].map(([k, n]) => `${n} ${k}`).join(', '); }
function hmStepTxt(pl, st){
  const G = hmGroups(pl, st), one = hmOneMode(st), n = st.g.length, d = hmDirWord(pl, st);
  const names = G.map(e => `<b>${escapeHtml(e.n > 1 ? `${e.nm} ×${e.n}` : e.nm)}</b>${one ? '' : ` (${escapeHtml(hmModesOf(e))})`}`).join(one ? ', ' : ' and ');
  const what = one ? `<b>${d} ${escapeHtml(hmModeWord(st.g[0].mo))}</b>` : `<b>${d}</b>`;
  const from = st.dir === 'out' ? `${pl.here} → ${pl.there}` : `${pl.there} → ${pl.here}`;
  const how = [...new Set(st.g.map(x => hmModeHow(x.mo)))].join(' · ');
  const order = n > 1 && hmShare(pl.P, st.m) > 0 ? ` This can close it: jump lightest first, ${pl.ships[st.g[n - 1].i].name} (${hmModeWord(st.g[n - 1].mo)}) last.` : '';
  return `${names} ${what} <span class="d">· ${escapeHtml(from)} · ${escapeHtml(hmT(st.m))}</span><br><span class="d hm-how">${escapeHtml(how.charAt(0).toUpperCase() + how.slice(1) + '.' + order)}</span>`;
}
function hmShortTxt(pl, st){
  if(st.short) return st.short;
  const G = hmGroups(pl, st), d = hmDirWord(pl, st);
  return hmOneMode(st) ? `${hmWho(pl, st)} ${d} ${hmModeWord(st.g[0].mo)}` : `${G.map(e => `${e.n > 1 ? `${e.nm} ×${e.n}` : e.nm} (${hmModesOf(e)})`).join(' + ')} ${d}`;
}
function hmRiskTxt(r){ return r >= 0.5 ? `${Math.round(r * 100)}%` : `about 1 in ${Math.max(2, Math.round(1 / r))}`; }
function hmDoneTxt(pl){
  const side = pl.fin === 'this' ? pl.here : pl.there, offs = pl.ships.filter(s => s.at !== pl.fin).map(s => s.name);
  return {rolled: `Rolled: the hole is gone and everyone is in ${side}.`, crit: `Crit: it says less than 10% and everyone is in ${side}.`,
    stranded: `The hole closed with ${offs.join(', ')} on the other side.`, closed: 'The hole closed (you wanted it open).'}[pl.done] || '';
}
// ---- the panel
function hmLinksHtml(n){
  const ls = whLinksOf(n).map(l => { const o = l.a === n ? l.b : l.a, t = hmLinkType(l, n); return {l, o, t}; });
  const cur = HM.link ? whLinkKey(HM.link.a, HM.link.b) : '';
  return ls.map(r => { const k = whLinkKey(r.l.a, r.l.b), m = r.l.mass && IT_WH_INFO_TXT.mass[r.l.mass] ? ` · ${IT_WH_INFO_TXT.mass[r.l.mass][0]}` : '';
    return `<option value="${escapeHtml(k)}"${k === cur ? ' selected' : ''}>to ${escapeHtml(whName(r.o))} · ${escapeHtml(r.t.code || (r.t.k162 ? 'K162' : 'type not known'))}${escapeHtml(m)}</option>`; }).join('')
    + `<option value=""${cur ? '' : ' selected'}>Another hole (type it)</option>`;
}
function hmFormHtml(){
  const n = whFocus(), H = hmHole(HM.ty), l = HM.link, lt = l ? hmLinkType(l, n) : null, o = l ? (l.a === n ? l.b : l.a) : null;
  const needTy = !l || !lt.code;
  const hl = H ? `${escapeHtml(H.code)} → ${escapeHtml(H.to)} · ${escapeHtml(hmT(H.M0))} total (${escapeHtml((H.M0 * 0.9 / 1e6).toFixed(2).replace(/0$/, ''))}–${escapeHtml((H.M0 * 1.1 / 1e6).toFixed(2).replace(/0$/, ''))} million, ±10%) · up to ${escapeHtml(hmT(H.J))} a jump`
    + (H.regen ? ' · <b>this hole regains its mass: rolling it isn’t practical</b>' : '') : HM.ty ? `“${escapeHtml(HM.ty)}” isn’t a wormhole type the page knows.` : '';
  const k162 = l && !lt.code ? `K162: what’s the type on the other side (${escapeHtml(whName(o))})?` : 'Type';
  const ships = HM.ships.map((r, i) => {
    const s = hmShipOf(r), opts = HM_FITS.map(f => `<option value="fit:${f.id}"${r.fit === f.id ? ' selected' : ''}>${escapeHtml(f.name)} — ${escapeHtml(f.fit)}</option>`).join('');
    const ms = s ? s.modes.map(m => `${hmT(m.m)} ${m.k === 'hot' ? `hot (${m.lab})` : hmModeWord(m)}`).join(' · ') : '';
    const big = s && H ? s.modes.filter(m => m.m > H.J) : [];
    const warn = s && H ? (big.length === s.modes.length ? 'too heavy for this hole' : big.length ? `only ${s.modes.filter(m => m.m <= H.J).map(hmModeWord).join(' or ')} fits this hole` : '') : '';
    return `<div class="hm-ship" role="group" aria-label="${escapeHtml('Ship ' + (i + 1))}"><select data-hm-ship="${i}"${r.fit ? ' class="hm-w2"' : ''} aria-label="${escapeHtml('Ship ' + (i + 1))}"><optgroup label="My Ships">${opts}</optgroup><option value="hull"${r.fit ? '' : ' selected'}>Type a hull…</option></select>`
      + (r.fit ? '' : `<input type="text" data-hm-hull="${i}" value="${escapeHtml(r.hull || '')}" placeholder="Hull, e.g. Megathron" aria-label="Hull" list="hmHullDl" maxlength="40" spellcheck="false">`)
      + `<button type="button" class="x-close" data-hm-rm="${i}" aria-label="${escapeHtml('Remove ship ' + (i + 1))}" title="Remove">×</button>`
      + `<span class="wh-note hm-m">${escapeHtml(ms)}${s && s.est ? ' · <i>hull only: plates, a Higgs Anchor or a ZPME change this</i>' : ''}${warn ? ` · <b class="hm-w">${escapeHtml(warn)}</b>` : ''}</span>`
      + `<label class="wh-note hm-fk"><input type="checkbox" data-hm-fin="${i}"${r.fin ? ' checked' : ''}> Finisher: waits until the hole is under 10%</label></div>`;
  }).join('');
  const head = `<div class="wh-poph">Crit or roll a hole<span class="hm-hr">${infoBtnHtml('whmass')}<button type="button" class="x-close" data-wh-popx aria-label="Close" title="Close (Esc)">×</button></span></div>`;
  if(HM.pl){   // steps under way: the setup folds to one line, so the step is in view
    const pl = HM.pl;
    return head + `<div class="wh-note hm-sum"><span>${escapeHtml(pl.H.code)} to ${escapeHtml(pl.there)} · ${pl.goal === 'roll' ? 'roll it' : 'crit it'}, finish in ${escapeHtml(pl.fin === 'this' ? pl.here : pl.there)} · ${escapeHtml(pl.ships.map(s => s.name + (s.fin ? ' (finisher)' : '')).join(', '))}</span><span class="hm-sb"><button type="button" data-hm="undo"${HM.back.length ? '' : ' disabled'} title="Take the last answer back (as far back as step 1)">Undo</button><button type="button" data-hm="edit">Change</button><button type="button" data-hm="reset">Start over</button></span></div>`
      + (HM.rs ? whAskHtml(`Start over? The ${pl.hist.length} step${pl.hist.length === 1 ? '' : 's'} so far are forgotten; the hole starts from what it says now.`, [['hmrs', 'Start over'], ['hmrskeep', 'Keep going']]) : '')
      + `<div class="hm-steps" aria-live="polite">${hmStepsHtml()}</div>`;
  }
  return head + `<div class="wh-addf hm-f">`
    + `<label class="wh-lnk hm-wide">Hole <select data-hm="link" aria-label="Hole">${hmLinksHtml(n)}</select></label>`
    + (needTy ? `<span class="wh-ty hm-wide"><input type="text" data-hm="ty" value="${escapeHtml(HM.ty)}" placeholder="${escapeHtml(k162)}" aria-label="${escapeHtml(k162)}" maxlength="4" spellcheck="false" autocapitalize="characters" list="hmTyDl"><datalist id="hmTyDl">${whTyOptsHtml(n).replace(/<option value="K162"[^>]*><\/option>/, l && !lt.code ? '' : '$&')}</datalist></span>` : '')
    + `<div class="wh-note hm-wide hm-hl">${hl}</div>`
    + `<label class="wh-lnk">It says now <select data-hm="st" aria-label="What the hole says now">${[['fresh', 'Fresh (nothing through yet)'], ['stable', 'More than 50%'], ['reduced', 'Less than 50%'], ['critical', 'Less than 10%']].map(([v, t]) => `<option value="${v}"${HM.st === v ? ' selected' : ''}>${t}</option>`).join('')}</select></label>`
    + `<label class="wh-lnk">Goal <select data-hm="goal" aria-label="Goal"><option value="roll"${HM.goal === 'roll' ? ' selected' : ''}>Roll it (close it)</option><option value="crit"${HM.goal === 'crit' ? ' selected' : ''}>Crit it (under 10%, still open)</option></select></label>`
    + `<label class="wh-lnk hm-wide">Finish in <select data-hm="fin" aria-label="Finish in"><option value="this"${HM.fin === 'this' ? ' selected' : ''}>this side: ${escapeHtml(whName(n))}</option><option value="other"${HM.fin === 'other' ? ' selected' : ''}>the other side: ${escapeHtml(o ? whName(o) : 'the other side')}</option></select></label></div>`
    + `<div class="wh-sub">Ships</div>${ships}<datalist id="hmHullDl">${Object.keys(HM_HULLS).map(h => `<option value="${escapeHtml(h)}"></option>`).join('')}</datalist>`
    + `<div class="wh-acts">${HM.ships.length < 4 ? '<button type="button" data-hm="add">+ Ship</button>' : ''}${HM.prev ? `<button type="button" class="mys-primary" data-hm="goon"${HM.ships.some(hmShipOf) ? '' : ' disabled'}>Carry on (${HM.prev.hist.length} steps so far)</button><button type="button" data-hm="go">Start over</button>` : `<button type="button" class="mys-primary" data-hm="go"${H && !H.regen && HM.ships.some(hmShipOf) ? '' : ' disabled'}>Show the steps</button>`}</div>`;
}
function hmStepsHtml(){
  const pl = HM.pl, now = Date.now(), pv = HM.pv;
  const st0 = pl.done ? null : hmNext(pl, now), stuck = st0 && !st0.none && st0.risk >= 0.99;
  const head = `<div class="wh-sub">Steps${stuck ? ' · no safe step left' : pv ? ` · about ${pv.lo === pv.hi ? pv.lo : `${pv.lo}–${pv.hi}`}${pl.hist.length ? " more" : ""} step${pv.hi === 1 ? "" : "s"}${pv.risky ? ' · may need a risky trip' : ''}` : ''}</div>`;
  const old = Math.max(0, pl.hist.length - 3);   // the last three jumps; the earlier ones fold into a line
  const done = (old ? `<li class="hm-old">${old} earlier step${old === 1 ? '' : 's'}</li>` : '') + pl.hist.slice(old).map((h, k) => `<li value="${old + k + 1}"><span>${escapeHtml(h.short)}</span> <span class="hm-said" style="color:${HM_SAYS_COL[h.obs]}">${escapeHtml(HM_SAYS[h.obs])}</span></li>`).join('');
  let now_ = '';
  if(pl.done) now_ = `<div class="hm-now hm-fin">${escapeHtml(hmDoneTxt(pl))}</div>` + (HM.ask ? whAskHtml(HM.ask.q, [['hmrm', 'Remove'], ['hmkeep', 'Keep it']]) : '');
  else{
    const st = HM.st_ = hmNext(pl, now);
    if(!st || st.none) now_ = `<div class="hm-now">No ship here can jump this hole.</div>`;
    else if(st.risk >= 0.99) now_ = `<div class="hm-now">No safe step left with these ships: the next jump ${hmDirWord(pl, st)} would close the hole behind ${escapeHtml(hmWho(pl, st))}.</div>`
      + `<div class="wh-note hm-w">${st.safe > 0 ? `A ship under ${escapeHtml(hmT(st.safe))} can do the last trip safely: add one with Change.` : 'No ship is light enough to be sure.'} Or leave it here: it says ${escapeHtml(HM_SAYS[pl.obs].toLowerCase())}.</div>`;
    else{
      const wait = st.wait ? `<div class="wh-note hm-w">Wait until ${escapeHtml(new Date(st.wait).toTimeString().slice(0, 5))} first: ${escapeHtml(hmWho(pl, st))} jumped ${hmDirWord(pl, st)} less than 5 minutes ago (polarized).</div>` : '';
      const who = escapeHtml(hmWho(pl, st)), safe = st.safe > 0 ? `A ship under ${escapeHtml(hmT(st.safe))} would be safe.` : 'No ship is light enough to be sure.';
      let alt = '';
      if(st.finAlt){ const q = hmClone(pl); q.finOk = true; const pv2 = hmPreview(q), fn = pl.ships.filter(s => s.fin).map(s => s.name).join(', ');
        alt = ` ${escapeHtml(fn)} (finisher) is kept for the end. <button type="button" data-hm="finnow">Send ${escapeHtml(fn)} instead: safe, about ${pv2.lo === pv2.hi ? pv2.lo : `${pv2.lo}–${pv2.hi}`} steps</button>`; }
      const risk = st.risk > 0 ? `<div class="wh-note hm-w"><b>No fully safe jump:</b> ${escapeHtml(hmRiskTxt(st.risk))} that it closes behind ${who}. ${safe}${alt}</div>` : '';
      const says = hmPossibleSays(pl, st);
      const br = says.map(k => { const q = hmClone(pl); hmApply(q, st, k, now + 60e3); const nx = hmNext(q, now + 60e3);
        return `<li><span class="hm-said" style="color:${HM_SAYS_COL[k]}">${escapeHtml(HM_SAYS[k])}:</span> ${escapeHtml(q.done ? hmDoneTxt(q) : nx && !nx.none ? hmShortTxt(q, nx) + (nx.risk > 0 ? ` (risky: ${hmRiskTxt(nx.risk)})` : '') + (nx.wait ? ', after a wait' : '') : 'no safe step')}</li>`; }).join('');
      now_ = `${pl.reset ? '<div class="wh-note hm-w">That answer doesn’t fit these masses, so the steps start again from what it says now. Check the ships or the type.</div>' : ''}`
        + `<div class="hm-now"><span class="hm-n">${pl.hist.length + 1}.</span> ${hmStepTxt(pl, st)}</div>${wait}${risk}`
        + `<div class="wh-note">Then Show Info on the hole: what does it say?</div>`
        + `<div class="hm-ans">${['stable', 'reduced', 'critical', 'gone'].map(k => `<button type="button" data-hm-say="${k}"><i style="background:${HM_SAYS_COL[k]}"></i>${escapeHtml(HM_SAYS[k])}</button>`).join('')}</div>`
        + `<button type="button" class="it-whp-xb" data-hm="br" aria-expanded="${HM.open}" aria-controls="hmBr">${IT_CHEV}What’s next</button>`
        + `<ul class="hm-br" id="hmBr"${HM.open ? '' : ' hidden'}>${br}</ul>`;
    }
  }
  return head + (done ? `<ol class="hm-done">${done}</ol>` : '') + now_;
}
function hmPaint(){
  const p = whS.el && whS.el.querySelector('.wh-pop[data-pop="mass"]'); if(!p) return; const y = p.scrollTop; p.innerHTML = hmFormHtml(); p.scrollTop = y; hmSave();
  const nw = p.querySelector('.hm-now'); if(nw && nw.offsetParent === p){ const top = nw.offsetTop - 120; if(nw.offsetTop + 160 > p.scrollTop + p.clientHeight || top < p.scrollTop) p.scrollTop = Math.max(0, top); }
}
function hmSave(){ try{ localStorage.setItem('tvWhMass', JSON.stringify({v: 1, ships: HM.ships})); }catch(e){} }
function hmRead(){ try{ const o = JSON.parse(localStorage.getItem('tvWhMass') || 'null'); if(o && o.v === 1 && Array.isArray(o.ships)) HM.ships = o.ships.slice(0, 4); }catch(e){} }
function hmOpenOn(n){   // opened: the focus system's first connection with a type, its mass
  const ls = whLinksOf(n); HM.link = ls.find(l => hmLinkType(l, n).code) || ls[0] || null; HM.pl = null; HM.ask = null; hmFromLink(n);
}
function hmFromLink(n){ const l = HM.link; if(!l) return; const t = hmLinkType(l, n); HM.ty = t.code; HM.st = l.mass || 'stable'; }
// Start over (the owner: "needs to be a start over or reset button"): back to the setup, same hole, ships and goal; what it says now is
// what the last answer said (the connection's Mass when the panel was opened on one), so the next Show the steps starts from there
// Undo (the owner: "and a \"back\" button", then "let's change \"Back\" to \"Undo\""): takes the last answer back, as far as step 1 of this run: the step it answered is shown again, the connection's Mass as it was
function hmUndo(){
  const b = HM.back.pop(); if(!b) return;
  HM.pl = b.pl; HM.pl.obs = b.obs; HM.pl.done = b.done; HM.pl.reset = b.reset; HM.ask = null; HM.rs = false; HM.pv = hmPreview(HM.pl);
  if(HM.link && whState().st.links.includes(HM.link)){ HM.link.mass = b.link || ''; whSave(); whS.drawKey = ''; whPaint(true); }
}
function hmReset(){ const pl = HM.pl; HM.back = []; HM.rs = false; HM.prev = null; HM.ask = null; HM.pl = null; if(pl && pl.obs && pl.obs !== 'gone') HM.st = pl.obs; else if(HM.link) HM.st = HM.link.mass || 'stable'; }
function hmGo(carry){
  const H = hmHole(HM.ty); if(!H) return; const pl = hmNew(), pv = carry && HM.prev;
  if(pv){   // carry on: what the hole could be and the jumps so far stay; a ship kept keeps its side and its polarization
    pl.P = pv.P; pl.obs = pv.obs; pl.hist = pv.hist; const used = new Set();
    for(const s of pl.ships){ const k = pv.ships.findIndex((o, j) => !used.has(j) && o.label === s.label); if(k >= 0){ used.add(k); s.at = pv.ships[k].at; s.last = {...pv.ships[k].last}; } }
  }
  HM.pl = pl; HM.back = []; HM.prev = null;   // a new run (Show the steps, Start over, Carry on): Undo starts again from here
  HM.pv = hmPreview(pl); HM.ask = null;
}
function hmSay(k){
  const pl = HM.pl, st = HM.st_; if(!pl || !st || st.none) return;
  HM.back.push({pl: hmClone(pl), obs: pl.obs, done: pl.done, reset: pl.reset, link: HM.link ? HM.link.mass : null});   // Undo takes this answer back
  hmApply(pl, st, k, Date.now()); HM.pv = pl.done ? null : hmPreview(pl);
  if(HM.link && pl.obs !== 'gone'){ HM.link.mass = pl.obs; whSave(); whS.drawKey = ''; whPaint(true); }   // Q7: the connection's Mass follows
  if(pl.done && pl.obs === 'gone' && HM.link) HM.ask = {q: `The hole is gone. Remove the connection to ${HM.link.a === whFocus() ? whName(HM.link.b) : whName(HM.link.a)}?`};
}
// the page's own toolbar and pop, with the Mass button and its pop added (the build puts them in whShellHtml and whPop)
const _hmShell = whShellHtml;
whShellHtml = function(){
  return _hmShell().replace('<button type="button" class="it-map-clr wh-tb" data-wh-pop="share"',
    `<button type="button" class="it-map-clr wh-tb" data-wh-pop="mass" aria-expanded="false" title="Work out how to crit or roll a hole" aria-label="Crit or roll a hole">${HM_SVG}<span>Mass</span></button><button type="button" class="it-map-clr wh-tb" data-wh-pop="share"`)
    .replace('<div class="wh-pop" data-pop="set"', '<div class="wh-pop hm-pop" data-pop="mass" role="dialog" aria-label="Crit or roll a hole" hidden></div><div class="wh-pop" data-pop="set"');
};
const _hmPop = whPop;
whPop = function(k){ _hmPop(k); if(k === 'mass'){ const p = whS.el.querySelector('.wh-pop[data-pop="mass"]'); if(p && !p.hidden){ hmOpenOn(whFocus()); hmPaint(); } } };
document.addEventListener('click', (e) => {
  const p = e.target.closest('.wh-pop[data-pop="mass"]'); if(!p) return;
  const b = e.target.closest('button'); if(!b) return;
  const d = b.dataset;
  if(d.hm === 'add'){ HM.ships.push({hull: ''}); HM.pl = null; }
  else if(d.hmRm !== undefined){ HM.ships.splice(Number(d.hmRm), 1); HM.pl = null; }
  else if(d.hm === 'go') hmGo(false);
  else if(d.hm === 'goon') hmGo(true);
  else if(d.hm === 'br'){ HM.open = !HM.open; }
  else if(d.hm === 'undo') hmUndo();
  else if(d.hm === 'finnow'){ HM.back.push({pl: hmClone(HM.pl), obs: HM.pl.obs, done: HM.pl.done, reset: HM.pl.reset, link: HM.link ? HM.link.mass : null}); HM.pl.finOk = true; HM.pv = hmPreview(HM.pl); }   // Undo takes it back too
  else if(d.hm === 'reset'){ if(HM.pl.hist.length && !HM.pl.done) HM.rs = true; else hmReset(); }
  else if(d.whAsk === 'hmrs') hmReset();
  else if(d.whAsk === 'hmrskeep') HM.rs = false;
  else if(d.hm === 'edit'){ HM.prev = HM.pl.hist.length && !HM.pl.done ? HM.pl : null; HM.pl = null; HM.ask = null; }
  else if(d.hmSay) hmSay(d.hmSay);
  else if(d.whAsk === 'hmrm'){ const l = HM.link, o = l.a === whFocus() ? l.b : l.a; whS.st.links = whS.st.links.filter(x => x !== l); delete whS.ends[whLinkKey(l.a, l.b)]; whSave(); whEndSave(); whMsg(`Deleted 1 connection: to ${whName(o)}.`); HM.link = null; HM.ask = null; whS.drawKey = ''; whPaint(true); }
  else if(d.whAsk === 'hmkeep'){ HM.ask = null; }
  else return;
  e.stopPropagation(); hmPaint();
}, true);
document.addEventListener('change', (e) => {
  const t = e.target; if(!t.closest || !t.closest('.wh-pop[data-pop="mass"]')) return;
  const n = whFocus();
  if(['link', 'ty', 'st'].includes(t.dataset.hm)) HM.prev = null;   // another hole, or what it says now: a fresh start
  if(t.dataset.hm === 'link'){ HM.link = t.value ? whState().st.links.find(l => whLinkKey(l.a, l.b) === t.value) : null; HM.ty = ''; HM.st = 'stable'; hmFromLink(n); }
  else if(t.dataset.hm === 'ty'){ HM.ty = t.value.trim().toUpperCase(); }
  else if(t.dataset.hm === 'st') HM.st = t.value; else if(t.dataset.hm === 'goal') HM.goal = t.value; else if(t.dataset.hm === 'fin') HM.fin = t.value;
  else if(t.dataset.hmShip !== undefined){ const i = Number(t.dataset.hmShip), f = HM.ships[i] && HM.ships[i].fin; HM.ships[i] = t.value === 'hull' ? {hull: ''} : {fit: t.value.slice(4)}; if(f) HM.ships[i].fin = true; }
  else if(t.dataset.hmFin !== undefined){ const r = HM.ships[Number(t.dataset.hmFin)]; if(t.checked) r.fin = true; else delete r.fin; }
  else if(t.dataset.hmHull !== undefined){ const i = Number(t.dataset.hmHull), f = HM.ships[i] && HM.ships[i].fin; HM.ships[i] = {hull: (Object.keys(HM_HULLS).find(h => h.toLowerCase() === t.value.trim().toLowerCase()) || t.value.trim())}; if(f) HM.ships[i].fin = true; }
  else return;
  HM.pl = null; HM.ask = null; hmPaint();
}, true);
window.hmCarry = () => HM.prev;
// its info text (the build: CARD_INFO.whmass; whmap's cap raised for one clause)
CARD_NAMES.whmass = 'Crit or roll a hole';
CARD_INFO.whmass = [
  'Works out, step by step, how to bring a hole under 10% (crit) or close it (roll) with the ships you pick, leaving everyone on the side you choose.',
  '[The numbers] Each type’s total mass and mass per jump are CCP’s. A new hole’s total is within ±10% of it, so the steps keep every total that fits what Show Info has said.',
  '[In, out, hot, cold] Out is a jump to the side you don’t want to finish on; in, to the side you do. The hole takes your ship’s mass as you press jump: hot is the MWD (or AB) running, cold is off. Ships that can jump together are one step, then one look at Show Info; a finisher waits until the hole says less than 10%. A typed hull counts no plates, Higgs Anchor or ZPME.',
  '[Safety] A jump that could close the hole is shown only when everyone then ends on your side; if no safe one is left, you see the odds and how light a ship must be. Polarization: no ship jumps the same way twice within 5 minutes.',
  '[For reference] Nothing is sent to EVE. Picking a connection keeps its Mass up to date.'
];
CARD_INFO.whmap = CARD_INFO.whmap.map(p => p.startsWith('[Focus and adding]') ? p.replace('+ Add adds a system or connection by hand;', '+ Add adds a system or connection by hand; Mass works out how to crit or roll a hole;') : p);
// mockup only: k-space names without ESI (the page reads them from ESI)
const HM_KNAMES = {30002510: 'Rens', 30002813: 'Tama', 30000142: 'Jita'};
const _hmSysName = itSysName; itSysName = function(id){ return HM_KNAMES[id] || _hmSysName(id); };
const hmCss = document.createElement('style');
hmCss.textContent = `
  .hm-pop .wh-poph .hm-hr{display:inline-flex; gap:6px; align-items:center;}
  .hm-pop .hm-wide{grid-column:1/-1;}
  .hm-pop .hm-hl{line-height:1.45;} .hm-pop .hm-hl b, .hm-pop .hm-w b{color:var(--amber);}
  .hm-ship{display:grid; grid-template-columns:minmax(0, 1fr) minmax(0, 1fr) auto; gap:6px 8px; align-items:center;}
  .hm-ship .hm-w2{grid-column:1/3;} .hm-ship .x-close{grid-column:3;} .hm-ship .hm-m, .hm-ship .hm-fk{grid-column:1/-1;} .hm-ship .hm-fk{display:inline-flex; gap:6px; align-items:center;}
  .hm-sum{position:sticky; top:-10px; z-index:1; box-shadow:0 -10px 0 var(--panel-2); display:flex; gap:8px; align-items:center; justify-content:space-between; padding:6px 8px; background:var(--panel); border:1px solid var(--line); border-radius:6px;} .hm-sum{flex-wrap:wrap;} .hm-sum > span:first-child{flex:1 1 200px; min-width:0;} .hm-sum .hm-sb{display:inline-flex; flex-wrap:wrap; gap:6px; flex:none;}
  .hm-steps{display:flex; flex-direction:column; gap:8px;} .hm-steps:empty{display:none;}
  .hm-done{margin:0; padding-left:22px; font:12px var(--sans); color:var(--text-dim);} .hm-done li{margin:2px 0;} .hm-done .hm-old{list-style:none; margin-left:-22px;}
  .hm-said{font-weight:600;}
  .hm-now{font:14px/1.45 var(--sans); color:var(--heading); padding:8px 10px; background:var(--panel); border:1px solid var(--line); border-radius:6px;}
  .hm-now .hm-n{color:var(--cyan); font-weight:700;} .hm-now .d{color:var(--text-dim);} .hm-now .hm-how{font-size:12px;} .hm-now.hm-fin{color:var(--cyan); font-weight:600;}
  .hm-ans{display:grid; grid-template-columns:repeat(2, minmax(0, 1fr)); gap:6px;} .hm-ans button{display:inline-flex; gap:8px; align-items:center; justify-content:flex-start; min-height:36px;}
  .hm-ans i{width:8px; height:8px; border-radius:2px; flex:none;}
  .hm-br{margin:0; padding:0 0 0 18px; font:12px/1.6 var(--sans); color:var(--text);} .hm-br[hidden]{display:none;}
  .hm-pop button.it-whp-xb{align-self:flex-start;}
  .hm-f select{min-width:0; max-width:100%;}
  @media (max-width: 600px){ .hm-pop .hm-f{grid-template-columns:minmax(0, 1fr);} .wh-ctl{flex-wrap:wrap; justify-content:flex-end; left:8px;} .wh-ctl > *{flex:none;} .hm-ans button{min-height:44px;} .hm-ship{grid-template-columns:minmax(0, 1fr) minmax(0, 1fr) auto;} }
`;
document.head.appendChild(hmCss);
hmRead();
