// Mockup runtime: the real page fed one made-up pilot's zKillboard lists (each item the full killmail plus zkb, as zKillboard's API
// answers), ESI killmails, names, types and groups. No network; storage in memory. Counts the requests for the mockup bar.
(() => {
  const MK = window.__MK = __MKDATA__;
  const C = window.__MKC = {zkb: 0, esiKm: 0};
  const memStore = () => { const m = new Map(); return {getItem: (k) => m.has(k) ? m.get(k) : null, setItem: (k, v) => { m.set(k, String(v)); }, removeItem: (k) => { m.delete(k); }, clear: () => m.clear(), key: (i) => [...m.keys()][i] ?? null, get length(){ return m.size; }}; };
  try{ Object.defineProperty(window, 'localStorage', {value: memStore(), configurable: true}); Object.defineProperty(window, 'sessionStorage', {value: memStore(), configurable: true}); }catch(e){ }
  try{ Object.defineProperty(window, 'indexedDB', {value: undefined, configurable: true}); }catch(e){ }
  const NOW = Date.now(), iso = (ago) => new Date(NOW - ago * 1000).toISOString().replace(/\.\d+Z$/, 'Z');
  const ty = (n) => Number(Object.keys(MK.types).find(id => MK.types[id][0] === n));
  const ALLY = 99200001, HOST = 99300001;
  const mine = (id, j) => ({character_id: id, corporation_id: 98200001 + (j % 3), alliance_id: ALLY});
  const host = (j) => ({character_id: 95200000 + j, corporation_id: 98300001 + (j % 2), alliance_id: HOST});
  const zkb = (id, isk, n, solo) => ({locationID: 40000000 + id % 1000, hash: id.toString(16).padStart(40, '0'), fittedValue: isk * 0.6, droppedValue: isk * 0.3,
    destroyedValue: isk * 0.7, totalValue: isk, points: 1, npc: false, solo, awox: false, labels: ['pvp', solo ? 'solo' : n >= 10 ? '#:10+' : n >= 5 ? '#:5+' : '#:2+']});
  // kills, newest first; each killmail built once
  const KM = new Map(), KL = [], LL = [];
  MK.kills.forEach(([ago, sys, hull, vship, fleet, gang], i) => {
    const id = 130000000 - i, att = [Object.assign(mine(MK.me, 0), {ship_type_id: ty(hull), weapon_type_id: ty(hull), final_blow: true, damage_done: 3000})];
    if(fleet){ const [n, base, mix] = fleet; for(let j = 0; j < n - 1; j++) att.push(Object.assign(mine(95100000 + base + j, j), {ship_type_id: ty(mix[j % mix.length]), final_blow: false, damage_done: 200})); }
    if(gang) gang.forEach(([cid, s], j) => att.push(Object.assign(mine(cid, j), {ship_type_id: ty(s), final_blow: false, damage_done: 900})));
    const v = Object.assign(host(i % 400), {ship_type_id: ty(vship), damage_taken: 9000, items: []});
    const km = {killmail_id: id, killmail_time: iso(ago), solar_system_id: sys, victim: v, attackers: att};
    KM.set(id, km); KL.push(Object.assign({}, km, {zkb: zkb(id, [8e6, 42e6, 96e6, 310e6, 21e6][i % 5], att.length, att.length === 1)}));
  });
  MK.losses.forEach(([ago, sys, ship, n], i) => {
    const id = 120000000 - i, att = [];
    for(let j = 0; j < n; j++) att.push(Object.assign(host(500 + i * 10 + j), {ship_type_id: ty(['Sabre', 'Muninn', 'Cheetah', 'Hurricane', 'Ishtar'][j % 5]), final_blow: j === 0, damage_done: 1500}));
    const km = {killmail_id: id, killmail_time: iso(ago), solar_system_id: sys, victim: Object.assign(mine(MK.me, 0), {ship_type_id: ty(ship), damage_taken: 8000, items: []}), attackers: att};
    KM.set(id, km); LL.push(Object.assign({}, km, {zkb: zkb(id, 60e6, n, n === 1)}));
  });
  const nameOf = (id) => {
    if(id === MK.me) return MK.meName;
    if(MK.wing[id]) return MK.wing[id];
    if(id >= 95200000 && id < 95300000) return `Mk Hostile ${id - 95200000}`;
    if(id >= 95100000 && id < 95200000) return `Mk Fleet ${id - 95100000}`;
    return null;
  };
  const json = (o, status = 200) => new Response(JSON.stringify(o), {status, headers: {'content-type': 'application/json'}});
  window.fetch = async (input, init) => {
    const url = typeof input === 'string' ? input : input.url, raw = init && init.body, body = typeof raw === 'string' ? (() => { try{ return JSON.parse(raw); }catch(e){ return null; } })() : null;
    let m;
    if(/esi\.evetech\.net/.test(url)){
      if(/\/universe\/names\//.test(url)) return json((body || []).map(id => MK.sys[id] ? {id, name: MK.sys[id][0], category: 'solar_system'} : MK.orgs[id] ? {id, name: MK.orgs[id][1], category: MK.orgs[id][0]} : nameOf(id) ? {id, name: nameOf(id), category: 'character'} : MK.types[id] ? {id, name: MK.types[id][0], category: 'inventory_type'} : null).filter(Boolean));
      if(/\/universe\/ids\//.test(url)) return json((body || []).some(n => String(n).toLowerCase() === MK.meName.toLowerCase()) ? {characters: [{id: MK.me, name: MK.meName}]} : {});
      if(/\/characters\/affiliation\//.test(url)) return json((body || []).map(id => ({character_id: id, corporation_id: id === MK.me ? MK.meCorp : 98200002, alliance_id: ALLY})));
      if((m = /\/killmails\/(\d+)\/\w+\/?(\?|$)/.exec(url))){ C.esiKm++; const k = KM.get(Number(m[1])); return k ? json(k) : json({error: 'not found'}, 404); }
      if((m = /\/corporations\/(\d+)\/?(\?|$)/.exec(url))){ const o = MK.orgs[m[1]]; return o ? json(Object.assign({name: o[1], ticker: o[2], member_count: 120}, o[3] ? {alliance_id: o[3]} : {})) : json({error: 'not found'}, 404); }
      if((m = /\/alliances\/(\d+)\/?(\?|$)/.exec(url))){ const o = MK.orgs[m[1]]; return o ? json({name: o[1], ticker: o[2]}) : json({error: 'not found'}, 404); }
      if((m = /\/characters\/(\d+)\/?(\?|$)/.exec(url))){ const n = nameOf(Number(m[1])); return n ? json({name: n, corporation_id: MK.meCorp, birthday: '2017-03-01T00:00:00Z', security_status: -3}) : json({error: 'not found'}, 404); }
      if((m = /\/universe\/systems\/(\d+)\/?(\?|$)/.exec(url))){ const s = MK.sys[m[1]]; return json({system_id: Number(m[1]), name: s ? s[0] : 'N' + m[1], security_status: s ? s[1] : -0.3}); }
      if((m = /\/universe\/types\/(\d+)\/?(\?|$)/.exec(url))){ const t = MK.types[m[1]]; return t ? json({type_id: Number(m[1]), name: t[0], group_id: t[1], published: true, dogma_attributes: [], dogma_effects: []}) : json({error: 'not found'}, 404); }
      if((m = /\/universe\/groups\/(\d+)\/?(\?|$)/.exec(url))){ const g = MK.groups[m[1]]; return g ? json({group_id: Number(m[1]), name: g, category_id: 6, published: true, types: []}) : json({error: 'not found'}, 404); }
      if(/\/status\//.test(url)) return json({players: 1, server_version: '1', start_time: new Date(NOW - 86400e3).toISOString()});
      return json({error: 'not in the mockup'}, 404);
    }
    if(/zkillboard\.com/.test(url)){
      C.zkb++;
      const page = Number((/\/page\/(\d+)\//.exec(url) || [])[1] || 1), slice = (l) => l.slice((page - 1) * 200, page * 200);
      if(/\/kills\/characterID\/(\d+)\//.test(url)) return json(slice(KL));
      if((m = /\/losses\/characterID\/\d+\/shipTypeID\/(\d+)\//.exec(url))) return json(LL.filter(k => k.victim.ship_type_id === Number(m[1])).slice(0, 200));
      if(/\/losses\/characterID\/(\d+)\//.test(url)) return json(slice(LL));
      return json([]);
    }
    throw new TypeError('the mockup makes no requests');
  };
})();
