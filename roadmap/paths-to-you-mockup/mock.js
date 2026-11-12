// Mockup runtime (from claude/roadmap/map-look-mockup/mock.js): the real page fed made-up Intel; no network, storage in memory.
// Wormhole-mapping prototype, 2026-11-11: adds __MKlocal / __MKintel so the MOCKUP bar can write new Local and Intel lines.
// Paths-to-you round 4 (2026-11-12): R2Z2 answers MK.kills (made-up killmails), as the Intel example mockup's runtime does.
// (Repo copy: the log lines' byte-order mark is written '﻿' rather than the character itself; the same string.)
(() => {
  const MK = window.__MK = __MKDATA__;
  const memStore = () => { const m = new Map(); return {getItem: (k) => m.has(k) ? m.get(k) : null, setItem: (k, v) => { m.set(k, String(v)); }, removeItem: (k) => { m.delete(k); }, clear: () => m.clear(), key: (i) => [...m.keys()][i] ?? null, get length(){ return m.size; }}; };
  try{ Object.defineProperty(window, 'localStorage', {value: memStore(), configurable: true}); Object.defineProperty(window, 'sessionStorage', {value: memStore(), configurable: true}); }catch(e){ }
  try{ Object.defineProperty(window, 'indexedDB', {value: undefined, configurable: true}); }catch(e){ }
  localStorage.setItem('dscanSide', JSON.stringify(MK.side));
  localStorage.setItem('dscanIntel', JSON.stringify(MK.intel));
  const files = {};
  const enc = (t) => { const a = new Uint8Array(t.length * 2); for(let i = 0; i < t.length; i++){ const c = t.charCodeAt(i); a[2 * i] = c & 255; a[2 * i + 1] = c >> 8; } return a; };
  const write = (name, text) => { const old = files[name] ? files[name].bytes : new Uint8Array(0), add = enc(text), b = new Uint8Array(old.length + add.length); b.set(old); b.set(add, old.length); files[name] = {bytes: b, mtime: Date.now()}; };
  class FH { constructor(n){ this.kind = 'file'; this.name = n; } async getFile(){ const f = files[this.name]; return new File([f.bytes], this.name, {lastModified: f.mtime}); } }
  const dir = {kind: 'directory', name: 'Chatlogs', async *entries(){ for(const n of Object.keys(files)) yield [n, new FH(n)]; }, async queryPermission(){ return 'granted'; }, async requestPermission(){ return 'granted'; }};
  window.showDirectoryPicker = async () => dir;
  window.Notification = class { constructor(){ } static get permission(){ return 'denied'; } static requestPermission(){ return Promise.resolve('denied'); } };
  const prm = () => ({value: 1, setValueAtTime(){ }, exponentialRampToValueAtTime(){ }, linearRampToValueAtTime(){ }});
  window.AudioContext = window.webkitAudioContext = class { constructor(){ this.currentTime = 0; this.destination = {}; this.state = 'running'; } resume(){ return Promise.resolve(); }
    createOscillator(){ return {frequency: prm(), connect: (g) => g, start(){ }, stop(){ }, set type(v){ }}; } createBufferSource(){ return {buffer: null, connect: (g) => g, start(){ }, stop(){ }}; }
    createGain(){ return {gain: prm(), connect: (n) => n}; } decodeAudioData(){ return Promise.reject(new Error('no audio')); } };
  const pad = (n) => String(n).padStart(2, '0');
  const eve = (t) => { const d = new Date(t); return `${d.getUTCFullYear()}.${pad(d.getUTCMonth() + 1)}.${pad(d.getUTCDate())} ${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())}:${pad(d.getUTCSeconds())}`; };
  const fname = (chan, t, cid) => { const d = new Date(t); return `${chan}_${d.getUTCFullYear()}${pad(d.getUTCMonth() + 1)}${pad(d.getUTCDate())}_${pad(d.getUTCHours())}${pad(d.getUTCMinutes())}${pad(d.getUTCSeconds())}_${cid}.txt`; };
  const header = (chan, who, t) => ['', '', '        ---------------------------------------------------------------', '', '          Channel ID:      -12345678', `          Channel Name:    ${chan}`, `          Listener:        ${who}`, `          Session started: ${eve(t)}`, '        ---------------------------------------------------------------', '', ''].map(l => '﻿' + l + '\r\n').join('');
  const line = (t, who, msg) => `﻿[ ${eve(t)} ] ${who} > ${msg}\r\n`;
  const NOW = Date.now();
  const F_LOCAL = fname('Local', NOW - 7200e3, MK.me.id), F_INTEL = fname('region.intel', NOW - 7000e3, MK.me.id);
  write(F_LOCAL, header('Local', MK.me.name, NOW - 7200e3) + line(NOW - 7190e3, 'EVE System', `Channel changed to Local : ${MK.homeName}*`));
  write(F_INTEL, header('region.intel', MK.me.name, NOW - 7000e3) + line(NOW - 6990e3, 'EVE System', 'Channel MOTD: made-up channel for the mockup')
    + MK.reports.map(([ago, who, msg]) => line(NOW - ago * 1000, who, msg)).join(''));
  window.__MKlocal = (sys) => write(F_LOCAL, line(Date.now(), 'EVE System', `Channel changed to Local : ${sys}*`));
  window.__MKintel = (who, msg) => write(F_INTEL, line(Date.now(), who, msg));
  const json = (o, status = 200) => new Response(JSON.stringify(o), {status, headers: {'content-type': 'application/json'}});
  const sysName = (id) => MK.names[id] || ('~' + id);
  window.fetch = async (input, init) => {
    const url = typeof input === 'string' ? input : input.url, raw = init && init.body, body = typeof raw === 'string' ? (() => { try{ return JSON.parse(raw); }catch(e){ return null; } })() : null;
    let m;
    if(/esi\.evetech\.net/.test(url)){
      if(/\/universe\/names\//.test(url)) return json((body || []).map(id => (id >= 30000000 && id < 31000000) ? {id, name: sysName(id), category: 'solar_system'} : MK.orgs[id] ? {id, name: MK.orgs[id][1], category: MK.orgs[id][0]} : MK.byId[id] ? {id, name: MK.byId[id][0], category: 'character'} : MK.types[id] ? {id, name: MK.types[id][0], category: 'inventory_type'} : null).filter(Boolean));
      if(/\/universe\/ids\//.test(url)){ const ch = (body || []).map(n => MK.pilots[String(n).toLowerCase()]).filter(Boolean).map(id => ({id, name: MK.byId[id][0]})); return json(ch.length ? {characters: ch} : {}); }
      if(/\/characters\/affiliation\//.test(url)) return json((body || []).filter(id => MK.byId[id]).map(id => { const c = MK.byId[id][1], a = MK.orgs[c] && MK.orgs[c][3]; return Object.assign({character_id: id, corporation_id: c}, a ? {alliance_id: a} : {}); }));
      if((m = /\/corporations\/(\d+)\/?(\?|$)/.exec(url))){ const o = MK.orgs[m[1]]; return o ? json(Object.assign({name: o[1], ticker: o[2], member_count: 12}, o[3] ? {alliance_id: o[3]} : {})) : json({error: 'not found'}, 404); }
      if((m = /\/alliances\/(\d+)\/?(\?|$)/.exec(url))){ const o = MK.orgs[m[1]]; return o ? json({name: o[1], ticker: o[2]}) : json({error: 'not found'}, 404); }
      if((m = /\/characters\/(\d+)\/?(\?|$)/.exec(url))){ const p = MK.byId[m[1]]; return p ? json({name: p[0], corporation_id: p[1], birthday: '2015-03-01T00:00:00Z'}) : json({error: 'not found'}, 404); }
      if((m = /\/universe\/systems\/(\d+)\/?(\?|$)/.exec(url))) return json({system_id: Number(m[1]), name: sysName(m[1]), security_status: -0.3});
      if((m = /\/universe\/types\/(\d+)\/?(\?|$)/.exec(url))){ const t = MK.types[m[1]]; return t ? json({type_id: Number(m[1]), name: t[0], group_id: t[1], published: true, dogma_attributes: [], dogma_effects: []}) : json({error: 'not found'}, 404); }
      if((m = /\/universe\/groups\/(\d+)\/?(\?|$)/.exec(url))){ const g = MK.groups[m[1]]; return g ? json({group_id: Number(m[1]), name: g, category_id: 6, published: true, types: []}) : json({error: 'not found'}, 404); }
      if(/\/status\//.test(url)) return json({players: 1, server_version: String(MK.build), start_time: new Date(NOW - 86400e3).toISOString()});
      return json({error: 'not in the mockup'}, 404);
    }
    if(/r2z2\.zkillboard\.com/.test(url)){   // made-up kills (MK.kills by sequence number; the Intel example mockup's runtime)
      if(/sequence\.json/.test(url)) return json({sequence: MK.seq});
      const n = (/\/(\d+)\.json/.exec(url) || [])[1], k = (MK.kills || {})[n];
      if(!k) return new Response('', {status: 404, headers: {'access-control-allow-origin': '*'}});
      const t = (ago) => new Date(NOW - ago * 1000).toISOString().replace(/\.\d+Z$/, 'Z');
      return json({killmail_id: k.id, hash: k.hash, sequence_id: Number(n), uploaded_at: Math.floor((NOW - k.ago * 1000 + 30000) / 1000),
        esi: {killmail_id: k.id, killmail_time: t(k.ago), solar_system_id: k.sys, victim: k.victim, attackers: k.attackers}, zkb: k.zkb});
    }
    if(/zkillboard\.com/.test(url)) return json([]);
    throw new TypeError('the mockup makes no requests');
  };
})();
