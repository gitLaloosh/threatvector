// Prototype: the Pilot Dossier reads by fights. Wraps the page's own pdLoad / pdBuild / pdHtml / fetchKillmail; a mockup bar
// switches Today / Proposed and the fight rule. Proposed: zKillboard's kill pages until FIGHT_QUOTA fights, a year back or
// MAX_PAGES pages; every kill and loss on the pages read (not 50/30); each list item is already the killmail, so no ESI read.
(() => {
  const FIGHT_QUOTA = 15, MAX_PAGES = 3, YEAR = 365 * 864e5, GAP = 3 * 3600e3;
  const P = window.__P = {on: false, rule: 'time', pages: 0, stop: '', read: 0};
  const orig = {pdLoad, pdBuild, pdHtml, fetchKillmail, info: CARD_INFO.dossier.slice()};
  // Fights: two of the pilot's kills are one fight when they share 2 other player attackers (1 when either kill had only 1-2
  // others): the Fleet tab's rule (fkGroupKills) with the pilot himself left out, since he is on every one of his kills.
  // rule 'time': and only when the two kills are within GAP of each other. Fights are the chains.
  window.pdFightsOf = (kms, me, rule = P.rule) => {
    const n = kms.length, t = kms.map(km => Date.parse(km.killmail_time));
    const att = kms.map(km => [...new Set((km.attackers || []).map(a => a.character_id).filter(c => c && c !== me))]);
    const parent = kms.map((_, i) => i), find = (i) => { while(parent[i] !== i) i = parent[i] = parent[parent[i]]; return i; };
    const on = new Map();
    att.forEach((a, i) => { for(const c of a){ const l = on.get(c); if(l) l.push(i); else on.set(c, [i]); } });
    const shared = new Map();
    for(const ks of on.values()){
      if(rule === 'time') ks.sort((a, b) => t[a] - t[b]);
      for(let x = 0; x < ks.length; x++) for(let y = x + 1; y < ks.length; y++){
        const i = ks[x], j = ks[y];
        if(rule === 'time' && t[j] - t[i] > GAP) break;
        if(find(i) === find(j)) continue;
        const k = Math.min(i, j) * n + Math.max(i, j), c = (shared.get(k) || 0) + 1; shared.set(k, c);
        if(c >= (Math.min(att[i].length, att[j].length) <= 2 ? 1 : 2)) parent[find(i)] = find(j);
      }
    }
    const of = new Map(); kms.forEach((km, i) => of.set(km.killmail_id, find(i)));
    return {of, count: new Set(kms.map((_, i) => find(i))).size};
  };
  fetchKillmail = async (stub) => (P.on && stub && stub.attackers && stub.victim && stub.killmail_time)
    ? {killmail_id: stub.killmail_id, hash: stub.zkb && stub.zkb.hash, km: stub} : orig.fetchKillmail(stub);
  pdBuild = async (charId, kms) => {
    const d = await orig.pdBuild(charId, kms);
    if(P.on){ const f = pdFightsOf(kms.kills, charId); d.fightOf = f.of; d.nFights = f.count; }
    return d;
  };
  pdLoad = async function(character, statusEl, forceRefresh, quiet){
    if(!P.on) return orig.pdLoad.apply(this, arguments);
    const charId = character.id;
    Object.assign(pd, {charId, character, statusEl, want: null, mode: 'all'});
    if(!quiet) setStatus(statusEl, `Reading ${currentPilotName}'s kills and losses…`);
    const all = []; let page = 0, stop = '';
    for(;;){
      page++;
      const res = await zkbFetch(`${ZKB}/kills/characterID/${charId}/${page > 1 ? `page/${page}/` : ''}`, {who: 'Pilot Analyzer'});
      const list = await res.json(); all.push(...list);
      const oldest = list.length ? Date.parse(list[list.length - 1].killmail_time) : Date.now();
      if(list.length < 200){ stop = 'all their kills'; break; }
      if(Date.now() - oldest > YEAR){ stop = 'a year back'; break; }
      if(pdFightsOf(all, charId).count >= FIGHT_QUOTA){ stop = `${FIGHT_QUOTA} fights`; break; }
      if(page >= MAX_PAGES){ stop = `${MAX_PAGES} pages`; break; }
    }
    const kStubs = all.filter(k => Date.now() - Date.parse(k.killmail_time) <= YEAR);
    killStubCache.set(charId, kStubs);
    const lStubs = await fetchLossesStubs(charId, undefined, forceRefresh, {who: 'Pilot Analyzer'});
    const [kr, lr] = await Promise.all([analyzeChunks(kStubs, fetchKillmail, 4), analyzeChunks(lStubs, fetchKillmail, 3)]);
    const ok = (rs) => rs.filter(r => r && !r.error && r.km).map(r => r.km);
    const d = await pdBuild(charId, {kills: ok(kr), losses: ok(lr)});
    d.added = null; d.stubs = kStubs.length + lStubs.length;
    Object.assign(P, {pages: page, stop, read: kStubs.length});
    pd.pin = null; pd.allHulls = false; pd.extra = null; pd.d = d;
    Object.assign(pd, {kStubs, read: kStubs.length, older: [], open: null, shown: PD_SHOW_STEP, busy: false, failed: [], value: new Map()});
    for(const s of kStubs) if(s && s.zkb && s.zkb.totalValue) pd.value.set(s.killmail_id, s.zkb.totalValue);
    const top = pdRows(d, pd.mode)[0];
    pd.sel = top ? top.h.id : null;
    pdRender();
    return top ? top.h : null;
  };
  const fightTip = (k, f) => `${k} kill${k === 1 ? '' : 's'} from ${f} separate fight${f === 1 ? '' : 's'}: kills sharing 2 of their wingmates (1 for a kill with only 1 or 2)${P.rule === 'time' ? ' within 3 hours of each other' : ''} count as one fight`;
  const fights = (d, ks) => new Set(ks.map(k => d.fightOf.get(k.id))).size;
  pdHtml = (d) => {
    let h = orig.pdHtml(d);
    if(!P.on || !d.fightOf) return h;
    const yr = d.from && new Date(d.from).getFullYear() !== new Date(d.to).getFullYear();   // a span across a new year says the year
    const day = (t, y) => new Date(t).toLocaleDateString('en-US', y ? {month: 'short', day: 'numeric', year: 'numeric'} : {month: 'short', day: 'numeric'});
    const span = d.from ? `, ${day(d.from, yr)} – ${day(d.to)}` : '';
    const sub = `${d.nKills} kills in ${d.nFights} fights, ${d.nLosses} losses${span}`;
    const full = `Read from zKillboard until ${FIGHT_QUOTA} fights, a year back or ${MAX_PAGES} pages of 200 kills, whichever came first: stopped at ${P.stop}. ${d.nKills} kills in ${d.nFights} fights and ${d.nLosses} losses${span}.`;
    h = h.replace(/(<h3>[\s\S]*?<\/h3>)<span class="ctx"[^>]*>[^<]*<\/span>/, (m, h3) => h3 + ctxHtml(sub, '', full));
    h = h.replace(/data-pd-hull="(\d+)"([\s\S]*?)<span class="pd-n k">([\s\S]*?)<\/span>(\s*<span class="pd-gang">)/g, (m, id, mid, inner, tail) => {
      const hull = d.hulls.find(x => x.id === Number(id));
      const ks = hull ? (pd.mode === 'all' ? hull.kills : hull.kills.filter(k => k.size === pd.mode)) : [];
      const f = ks.length ? fights(d, ks) : 0;
      return `data-pd-hull="${id}"${mid}<span class="pd-n k">${inner}${f ? `<span class="mk-fights" title="${escapeHtml(fightTip(ks.length, f))}">${f} fight${f === 1 ? '' : 's'}</span>` : ''}</span>${tail}`;
    });
    return h;
  };
  const css = document.createElement('style');
  css.textContent = `.pd-n .mk-fights{display:block; font:400 11px var(--sans); color:var(--text-dim); margin-top:2px;}
    .mk-bar{display:flex; flex-wrap:wrap; gap:10px 16px; align-items:center; margin:0 0 12px; padding:10px 12px; border:1px dashed var(--line); border-radius:8px; font:400 12.5px var(--sans); color:var(--text-dim);}
    .mk-bar b{color:var(--heading); font-weight:600;} .mk-bar .pd-seg button{min-height:36px;}`;
  document.head.appendChild(css);
  window.__mkBar = () => {
    let bar = document.getElementById('mkBar');
    const dos = document.getElementById('pilotDossier');
    if(!bar){ bar = document.createElement('div'); bar.id = 'mkBar'; bar.className = 'mk-bar'; dos.parentNode.insertBefore(bar, dos); bar.addEventListener('click', window.__mkClick); }
    const seg = (name, opts, cur) => `<span class="pd-seg" role="group" aria-label="${name}">${opts.map(([v, l]) => `<button type="button" data-mk-${name}="${v}" aria-pressed="${cur === v}"${cur === v ? ' class="on"' : ''}>${l}</button>`).join('')}</span>`;
    const c = window.__MKC;
    bar.innerHTML = `<b>Mockup</b>${seg('view', [['today', 'Today'], ['prop', 'Proposed']], P.on ? 'prop' : 'today')}`
      + (P.on ? `<span>Fight rule</span>${seg('rule', [['fleet', 'Fleet tab rule'], ['time', '+ within 3 h']], P.rule)}` : '')
      + `<span>zKillboard requests <b>${c.zkb}</b> · ESI killmail reads <b>${c.esiKm}</b>${P.on ? ` · kill pages read <b>${P.pages}</b> (stopped at ${P.stop})` : ''}</span>`;
  };
  window.__mkRun = async () => {
    window.__MKC.zkb = 0; window.__MKC.esiKm = 0;
    killStubCache.clear(); lossStubCache.clear(); killmailCache.clear();
    CARD_INFO.dossier[0] = P.on
      ? `What they fly, from their zKillboard kills back to ${FIGHT_QUOTA} fights (a year at most) and 200 losses: one row per hull, last used first (in a gang size, by its newest kill there). A row shows their losses in it, or their alliance's (or corporation's) common fit, said as not theirs.`
      : orig.info[0];
    window.__MKBUSY = true;
    await pdLoad({id: window.__MK.me, name: window.__MK.meName}, document.getElementById('fitStatus'), false, false);
    setStatus(document.getElementById('fitStatus'), '');
    window.__MKBUSY = false;
    window.__mkBar();
  };
  window.__mkClick = (e) => {
    const v = e.target.closest('[data-mk-view]'), r = e.target.closest('[data-mk-rule]');
    if(window.__MKBUSY || (!v && !r)) return;
    if(v) P.on = v.dataset.mkView === 'prop';
    if(r) P.rule = r.dataset.mkRule;
    window.__mkBar(); window.__mkRun();
  };
})();
