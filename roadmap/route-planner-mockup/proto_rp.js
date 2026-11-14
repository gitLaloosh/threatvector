// Route planner prototype (research session 2026-11-12, mockup only): a search box on the Intel map, a right-click menu on any system
// ("Set destination (EVE's route)" / "Set destination (Threat Vector's route)" / "Avoid this system"), the map's drawn route following
// Threat Vector's route (Intel settings: preference, security penalty, avoid options), the same choices as buttons in a pressed system's
// tooltip on a phone, and a "Routes" box in Intel settings. Nothing is sent: the mockup shows what would go to EVE.
(() => {
  const KEY = 'tvRoute', PREF = ['Shorter', 'Safer', 'LessSecure'];
  const PREF_NAME = {Shorter: 'Prefer shorter', Safer: 'Prefer safer', LessSecure: 'Prefer less secure'};
  const rp = window.rp = {set: null, key: '', par: null, f: null, len: null, flags: new Map(), menu: null, sel: -1, toastT: 0, sends: []};
  const DEF = {pref: 'Shorter', pen: 50, camp: true, bub: true, host: true, mine: true, list: []};
  try{ rp.set = Object.assign({}, DEF, JSON.parse(localStorage.getItem(KEY) || '{}')); }catch(e){ rp.set = Object.assign({}, DEF); }
  if(!PREF.includes(rp.set.pref)) rp.set.pref = 'Shorter';
  const save = () => { try{ localStorage.setItem(KEY, JSON.stringify(rp.set)); }catch(e){ } };
  const esc = (t) => escapeHtml(String(t));
  const ids = () => itGraphGet().ids;
  // ---- what the avoid options flag, per map index: reasons ['camp', 'bubble', 'hostiles', 'your list']
  function rpFlags(){
    const out = new Map(), g = itGraphGet(), now = Date.now(), keep = now - it.set.forget * 60000, add = (i, w) => { if(i === undefined) return; const a = out.get(i) || []; if(!a.includes(w)) a.push(w); out.set(i, a); };
    for(const st of it.near.values()){
      const i = g.at.get(st.sys); if(i === undefined || st.kind === 'clear') continue;
      if(rp.set.camp && /\bcamp\b/.test(itGateTagHtml(st, now))) add(i, 'camp');
      if(rp.set.bub && itBubTagHtml(st, now)) add(i, 'bubble');
      // the owner: "every report that has hostiles, neutrals, camps, bubbles, kills or ess" (every report Intel holds, not only within Map: within)
      if(rp.set.host){
        if(st.t >= keep && st.kind === 'seen'){ const L = itLive(st); if(!L.friendlyOnly){ const h = L.pilots.some(x => x.side === 'h') || (!L.pilots.length && !(L.count && L.countKind === 'neut')); add(i, h ? 'hostiles' : 'neutrals'); } }
        if((st.kills || []).some(x => x.t >= keep)) add(i, 'kills');
        if(itEssTagHtml(st, now)) add(i, 'ESS');
      }
    }
    if(rp.set.mine) for(const id of rp.set.list) add(g.at.get(id), 'your list');
    return out;
  }
  // ---- Threat Vector's route from your system to every system: fewest flagged systems on the way first (the destination never counts),
  // then the game's cost (CCP's route guide: Shorter 1 a jump; Safer / Less Secure: p = exp(0.15 x penalty), into null 2p, into low p or
  // 0.90, into high 0.90 or p). Security from the map table (hundredths; the plan stores a band from CCP's unrounded value instead).
  function rpCost(T, y){
    if(rp.set.pref === 'Shorter') return 1;
    const s = T.sec[y] / 100, p = Math.exp(0.15 * rp.set.pen);
    if(s <= 0) return 2 * p;
    if(s < 0.45) return rp.set.pref === 'Safer' ? p : 0.9;
    return rp.set.pref === 'Safer' ? 0.9 : p;
  }
  function rpPlan(){
    const home = itm.home; if(home < 0 || !itMapTable()) return false;
    const flags = rpFlags(), fk = [...flags].map(([i, w]) => i + w.join('')).sort().join(',');
    const key = `${home}|${rp.set.pref}|${rp.set.pen}|${fk}`;
    if(key === rp.key && rp.par) return false;
    const T = itMapTable(), n = T.n, f = new Int32Array(n).fill(1e9), c = new Float64Array(n).fill(Infinity), len = new Int32Array(n).fill(-1), par = new Int32Array(n).fill(-1), done = new Uint8Array(n);
    f[home] = 0; c[home] = 0; len[home] = 0;
    const h = [home], less = (a, b) => f[a] < f[b] || (f[a] === f[b] && (c[a] < c[b] - 1e-9 || (Math.abs(c[a] - c[b]) <= 1e-9 && len[a] < len[b])));
    const up = (k) => { while(k > 0){ const p = (k - 1) >> 1; if(!less(h[k], h[p])) break; [h[k], h[p]] = [h[p], h[k]]; k = p; } };
    const down = (k) => { for(;;){ const l = 2 * k + 1, r = l + 1; let m = k; if(l < h.length && less(h[l], h[m])) m = l; if(r < h.length && less(h[r], h[m])) m = r; if(m === k) break; [h[k], h[m]] = [h[m], h[k]]; k = m; } };
    while(h.length){
      const x = h[0], last = h.pop(); if(h.length){ h[0] = last; down(0); }
      if(done[x]) continue; done[x] = 1;
      const fx = f[x] + (x !== home && flags.has(x) ? 1 : 0);   // the owner: "keep my rule" (fewest flagged first, any detour length)
      for(const y of T.adj[x]){
        if(done[y]) continue;
        const cy = c[x] + rpCost(T, y);
        if(fx < f[y] || (fx === f[y] && (cy < c[y] - 1e-9 || (Math.abs(cy - c[y]) <= 1e-9 && len[x] + 1 < len[y])))){ f[y] = fx; c[y] = cy; len[y] = len[x] + 1; par[y] = x; h.push(y); up(h.length - 1); }
      }
    }
    Object.assign(rp, {key, par, f, len, flags});
    return true;
  }
  window.rpPlan = rpPlan;
  // the systems of Threat Vector's route to i, you first, i last (map indexes)
  function rpPath(i){ rpPlan(); const out = []; let x = i; while(x >= 0 && x !== itm.home){ out.push(x); x = rp.par[x]; } if(x !== itm.home) return null; out.push(itm.home); return out.reverse(); }
  window.rpPath = rpPath;
  window.rpWarnText = (i) => rpWarn(rpPath(i)).join('; ');
  // the map's drawn route and the tooltip's route list follow Threat Vector's route (jump numbers stay on stargates: itm.D)
  window.itMapRoute = function(i){ rpPlan(); const r = []; let x = i; while(x !== itm.home && x >= 0 && rp.par[x] >= 0){ r.push([x, rp.par[x]]); x = rp.par[x]; } return r; };
  const key0 = window.itMapKey;
  window.itMapKey = function(){ rpPlan(); return key0() + '|rp:' + rp.key; };
  // ---- the tooltip: the route's jumps when they differ from the shortest, what it couldn't avoid, the right-click hint; on a phone the buttons
  const touch = () => (typeof matchMedia === 'function' && (matchMedia('(hover: none)').matches || matchMedia('(max-width: 599px)').matches));
  function rpWarn(path){ if(!path) return []; return path.slice(1, -1).filter(x => rp.flags.has(x)).map(x => `${itSysName(ids()[x])} (${rp.flags.get(x).join(', ')})`); }
  const tip0 = window.itMapTip;
  window.itMapTip = function(i, x, y){
    tip0(i, x, y);
    const tip = itm.tip; tip.classList.remove('rp-act');
    if(i < 0 || tip.hidden) return;
    const d = itm.D[i], path = d > 0 ? rpPath(i) : null, gid = ids()[i];
    let h = '';
    if(path && path.length - 1 !== d) h += `<br><span class="rp-n">Threat Vector's route: <b>${path.length - 1} jumps</b> <span class="d">(shortest ${d})</span></span>`;
    const w = rpWarn(path);
    if(w.length) h += `<br><span class="rp-w">⚠ No route avoids all: passes ${esc(w.join(', '))}</span>`;
    if(rp.set.list.includes(gid)) h += `<br><span class="d">on your avoid list</span>`;
    if(d >= 0 && i !== itm.home){
      if(touch() && itm.pinned.has(gid)){ h += rpBtnsHtml(i, true); tip.classList.add('rp-act'); }
      else if(!touch()) h += `<br><span class="d">right-click: set destination</span>`;
    }
    if(h){ tip.insertAdjacentHTML('beforeend', h); const tw = tip.offsetWidth, th = tip.offsetHeight; tip.style.left = Math.max(4, Math.min(itm.W - tw - 6, x + 14)) + 'px'; tip.style.top = (y + th + 18 > itm.H ? Math.max(4, y - th - 12) : y + 14) + 'px'; }
  };
  function rpBtnsHtml(i, inTip){
    const gid = ids()[i], d = itm.D[i], path = d > 0 ? rpPath(i) : null, on = rp.set.list.includes(gid), can = d > 0;
    return `<div class="rp-btns${inTip ? ' rp-in-tip' : ''}" role="${inTip ? 'group' : 'menu'}" aria-label="${esc(itSysName(gid))}">`
      + `<button type="button" role="menuitem" data-rp-go="eve" data-rp-i="${i}"${can ? '' : ' disabled'}>Set destination <span>(EVE's route)</span></button>`
      + `<button type="button" role="menuitem" data-rp-go="tv" data-rp-i="${i}"${can ? '' : ' disabled'}>Set destination <span>(Threat Vector's route)</span>${path ? `<small>${path.length - 1} jumps${rpWarn(path).length ? ' · ⚠ ' + rpWarn(path).length + ' flagged' : ''}</small>` : ''}</button>`
      + `<button type="button" role="menuitem" class="rp-av" data-rp-av="${gid}"${i === itm.home ? ' disabled' : ''}>${on ? 'Stop avoiding' : 'Avoid this system'}</button></div>`;
  }
  // ---- the right-click menu
  function rpMenuOpen(i, x, y){
    rpMenuClose(); if(i < 0) return;
    const m = document.createElement('div'); m.className = 'rp-menu';
    m.innerHTML = `<div class="rp-mh"><b>${esc(itSysName(ids()[i]))}</b>${i === itm.home ? ' <span class="d">· you are here</span>' : itm.D[i] < 0 ? ' <span class="d">· no gate route</span>' : ''}</div>` + rpBtnsHtml(i, false);
    itm.box.appendChild(m); rp.menu = m;
    const mw = m.offsetWidth, mh = m.offsetHeight;
    m.style.left = Math.max(4, Math.min(itm.W - mw - 4, x)) + 'px'; m.style.top = Math.max(4, Math.min(itm.H - mh - 4, y)) + 'px';
    itMapTip(-1);
    const b = m.querySelector('button:not([disabled])'); if(b) b.focus({preventScroll: true});
  }
  function rpMenuClose(){ if(rp.menu){ rp.menu.remove(); rp.menu = null; } }
  window.rpMenuOpen = rpMenuOpen;
  // ---- the two actions: what would go to EVE (the mockup sends nothing)
  function rpToast(html, warn){
    let t = itm.box.querySelector('.rp-toast'); if(!t){ t = document.createElement('div'); t.className = 'rp-toast'; t.setAttribute('role', 'status'); itm.box.appendChild(t); }
    t.className = 'rp-toast' + (warn ? ' warn' : ''); t.innerHTML = html + '<button type="button" class="x-close" data-rp-tx aria-label="Close">×</button>'; t.hidden = false;
  }
  function rpGo(mode, i){
    rpMenuClose(); itMapTip(-1);
    const gid = ids()[i], name = itSysName(gid);
    if(mode === 'eve'){
      rp.sends.push({mode, n: 1, to: gid});
      rpToast(`<b>Destination set: ${esc(name)}</b><br><span class="d">EVE plans the route with your game's autopilot settings (Threat Vector's avoid options don't apply).</span><br><span class="mk">MOCKUP: 1 request, POST /ui/autopilot/waypoint (clear other waypoints, ${esc(name)}). The first time, EVE asks for the Waypoints permission.</span>`);
      return;
    }
    const path = rpPath(i); if(!path) return;
    const w = rpWarn(path), names = path.slice(1).map(x => itSysName(ids()[x]));
    rp.sends.push({mode, n: names.length, to: gid, warn: w.length});
    rpToast(`<b>Destination set: ${esc(name)}, ${names.length} jumps</b> <span class="d">· Threat Vector's route, ${esc(PREF_NAME[rp.set.pref].toLowerCase())}</span>`
      + (w.length ? `<br><span class="rp-w">⚠ No route avoids all: passes ${esc(w.join(', '))}</span>` : '')
      + `<br><span class="d">Every system is a waypoint, so EVE follows this route. With “Disable Autopilot at Each Waypoint” on, the autopilot stops at each.</span>`
      + `<br><span class="mk">MOCKUP: ${names.length} requests, one after another: ${esc(names.length > 8 ? [...names.slice(0, 4), '…', ...names.slice(-2)].join(' → ') : names.join(' → '))}</span>`, w.length > 0);
    if(!itm.pinned.has(gid)) itMapPin(gid);
  }
  function rpAvoid(gid){
    const k = rp.set.list.indexOf(gid);
    if(k >= 0) rp.set.list.splice(k, 1); else rp.set.list.push(gid);
    save(); rpMenuClose(); rpRefresh();
  }
  function rpRefresh(){ rp.key = ''; itMapRefresh(true); const box = document.querySelector('[data-rp-box]'); if(box) box.outerHTML = rpBoxHtml(); }
  window.rpRefresh = rpRefresh;
  // ---- the search box (top left of the map): suggestions as you type, like the game's map search
  function rpSearchMount(){
    if(!itm.box || itm.box.querySelector('.rp-search')) return;
    const f = document.createElement('div'); f.className = 'rp-search';
    f.innerHTML = `<input type="search" placeholder="Search systems" aria-label="Search systems" autocomplete="off" spellcheck="false" role="combobox" aria-expanded="false" aria-controls="rpSug" aria-autocomplete="list"><ul id="rpSug" class="rp-sug" role="listbox" hidden></ul>`;
    itm.box.appendChild(f);
    const inp = f.querySelector('input'), ul = f.querySelector('ul');
    let opts = [], cur = -1;
    const T = itMapTable(), g = itGraphGet();
    const show = () => {
      const q = inp.value.trim().toLowerCase(); cur = -1;
      if(!q || !it.names){ ul.hidden = true; inp.setAttribute('aria-expanded', 'false'); return; }
      const all = it.names.list, a = [], b = [];
      for(const nm of all){ if(nm.startsWith(q)) a.push(nm); else if(nm.includes(q)) b.push(nm); if(a.length >= 8) break; }
      opts = [...a.sort(), ...b.sort()].slice(0, 8).map(nm => it.names.byLower.get(nm)).filter(id => g.at.get(id) !== undefined);
      ul.innerHTML = opts.map((id, k) => { const i = g.at.get(id), d = itm.D[i]; return `<li role="option" id="rpo${k}" data-rp-pick="${id}"><span class="${itSecClass(id)}">${esc(itSysName(id))}</span> <span class="d">${esc(T.regions[T.reg[i]] || '')} · ${d === 0 ? 'you' : d < 0 ? 'no gate route' : d + ' j'}</span></li>`; }).join('') || '<li class="d" aria-disabled="true">No system by that name</li>';
      ul.hidden = false; inp.setAttribute('aria-expanded', 'true');
    };
    const mark = () => { [...ul.children].forEach((li, k) => li.classList.toggle('on', k === cur)); inp.setAttribute('aria-activedescendant', cur >= 0 ? 'rpo' + cur : ''); };
    inp.addEventListener('input', show);
    inp.addEventListener('keydown', (e) => {
      if(e.key === 'ArrowDown' && opts.length){ cur = Math.min(opts.length - 1, cur + 1); mark(); e.preventDefault(); }
      else if(e.key === 'ArrowUp' && opts.length){ cur = Math.max(0, cur - 1); mark(); e.preventDefault(); }
      else if(e.key === 'Enter' && opts.length){ rpPick(opts[Math.max(0, cur)]); e.preventDefault(); }
      else if(e.key === 'Escape'){ ul.hidden = true; inp.setAttribute('aria-expanded', 'false'); }
      else if((e.key === 'ContextMenu' || (e.key === 'F10' && e.shiftKey)) && rp.sel >= 0){ e.preventDefault(); rpMenuOpen(rp.sel, itm.Q[2 * rp.sel] + 10, itm.Q[2 * rp.sel + 1] + 10); }
    });
    ul.addEventListener('mousedown', (e) => { const li = e.target.closest('[data-rp-pick]'); if(li){ e.preventDefault(); rpPick(Number(li.dataset.rpPick)); } });
    function rpPick(id){
      const i = itGraphGet().at.get(id); if(i === undefined) return;
      inp.value = itSysName(id); ul.hidden = true; inp.setAttribute('aria-expanded', 'false'); rp.sel = i;
      const v = itm.view, gp = itMapGatePx(); if(gp < 40) v.k = Math.min(itm.kMax, v.k * 40 / Math.max(1, gp));
      v.tx = itm.W / 2 - itm.P[2 * i] * v.k; v.ty = itm.H / 2 - itm.P[2 * i + 1] * v.k;
      if(itm.D[i] > 0 && !itm.pinned.has(id)) itMapPin(id); else itMapDraw();
      itMapTip(i, itm.Q[2 * i], itm.Q[2 * i + 1]);
    }
    window.rpPick = rpPick;
  }
  // ---- the Routes box in Intel settings (not in the Intel example's numbered setup)
  function rpBoxHtml(){
    const s = rp.set, ck = (k, t) => `<label><input type="checkbox" data-rp-set="${k}"${s[k] ? ' checked' : ''}> ${t}</label>`;
    const rows = s.list.map(id => `<li>${esc(itSysName(id))} <button type="button" data-rp-av="${id}" aria-label="Remove ${esc(itSysName(id))}">Remove</button></li>`).join('');
    return `<div class="it-box rp-box" data-rp-box><div class="k">Routes</div>`
      + `<div class="rp-pref" role="radiogroup" aria-label="Route preference">${PREF.map(p => `<label><input type="radio" name="rpPref" value="${p}" data-rp-set="pref"${s.pref === p ? ' checked' : ''}> ${PREF_NAME[p]}</label>`).join('')}</div>`
      + `<label class="rp-pen">security penalty <input type="range" min="0" max="100" step="1" value="${s.pen}" data-rp-set="pen" aria-label="Security penalty"${s.pref === 'Shorter' ? ' disabled' : ''}> <b>${s.pen}</b></label>`
      + `<div class="rp-avk">avoid</div>${ck('camp', 'gate camps')}${ck('bub', 'bubbles')}${ck('host', 'systems with reported hostiles, neutrals, kills or ESS')}${ck('mine', 'systems on my avoid list')}`
      + `<ul class="rp-list">${rows || '<li class="d">Your avoid list is empty. Right-click a system on the map to add it.</li>'}</ul>`
      + `<form class="rp-add" autocomplete="off"><input type="text" name="sys" placeholder="System, e.g. 8BA-RA" aria-label="System to avoid" maxlength="40" spellcheck="false"><button type="submit">Avoid</button></form>`
      + `<div class="c">For the map's routes and “Set destination (Threat Vector's route)”. EVE's route uses your game settings.</div></div>`;
  }
  const set0 = window.itSettingsHtml;
  window.itSettingsHtml = function(numbered){ const h = set0(numbered); if(numbered) return h; const k = h.lastIndexOf('</div>'); return h.slice(0, k) + rpBoxHtml() + h.slice(k); };
  // ---- events
  document.addEventListener('click', (e) => {
    const go = e.target.closest('[data-rp-go]'); if(go){ e.preventDefault(); e.stopPropagation(); rpGo(go.dataset.rpGo, Number(go.dataset.rpI)); return; }
    const av = e.target.closest('[data-rp-av]'); if(av){ e.preventDefault(); e.stopPropagation(); rpAvoid(Number(av.dataset.rpAv)); return; }
    if(e.target.closest('[data-rp-tx]')){ const t = itm.box.querySelector('.rp-toast'); if(t) t.hidden = true; return; }
    if(rp.menu && !rp.menu.contains(e.target)) rpMenuClose();
  }, true);
  document.addEventListener('keydown', (e) => {
    if(!rp.menu) return;
    if(e.key === 'Escape'){ rpMenuClose(); e.stopPropagation(); }
    else if(e.key === 'ArrowDown' || e.key === 'ArrowUp'){ const bs = [...rp.menu.querySelectorAll('button:not([disabled])')], k = bs.indexOf(document.activeElement); const n = bs[(k + (e.key === 'ArrowDown' ? 1 : -1) + bs.length) % bs.length]; if(n) n.focus(); e.preventDefault(); }
  }, true);
  document.addEventListener('change', (e) => {
    const t = e.target.closest('[data-rp-set]'); if(!t) return;
    const k = t.dataset.rpSet;
    if(k === 'pref') rp.set.pref = t.value; else if(k === 'pen') rp.set.pen = Math.max(0, Math.min(100, Number(t.value) || 0)); else rp.set[k] = t.checked;
    save(); rpRefresh();
  });
  document.addEventListener('input', (e) => { const t = e.target.closest('[data-rp-set="pen"]'); if(t){ const b = t.parentNode.querySelector('b'); if(b) b.textContent = t.value; } });
  document.addEventListener('submit', (e) => {
    const f = e.target.closest('.rp-add'); if(!f) return; e.preventDefault();
    const v = f.sys.value.trim().toLowerCase(), id = it.names && it.names.byLower.get(v);
    if(!id){ f.sys.setCustomValidity('Not a known system'); f.sys.reportValidity(); f.sys.setCustomValidity(''); return; }
    if(!rp.set.list.includes(id)) rp.set.list.push(id); save(); rpRefresh();
  });
  // the map's own canvas: right-click opens the menu (a phone presses: the tooltip carries the buttons)
  const bind = () => {
    if(!itm.cv || itm.cv.__rp) return; itm.cv.__rp = true; rpSearchMount();
    itm.cv.addEventListener('contextmenu', (e) => { e.preventDefault(); const r = itm.cv.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top; rpMenuOpen(itMapPick(x, y), x, y); });
  };
  const draw0 = window.itMapDraw;
  window.itMapDraw = function(){ bind(); return draw0(); };
  // ---- styles (the page's tokens only)
  const css = document.createElement('style');
  css.textContent = `
  .rp-search{position:absolute; left:8px; top:8px; z-index:4; width:200px;}
  .rp-search input{width:100%; box-sizing:border-box; min-height:32px; background:var(--bg);}
  .rp-sug{list-style:none; margin:2px 0 0; padding:3px 0; border:1px solid #2c3842; border-radius:6px; background:var(--panel-2); box-shadow:0 8px 22px rgba(0,0,0,.5); max-height:260px; overflow:auto;}
  .rp-sug li{padding:5px 9px; font:400 12px/1.3 var(--sans); cursor:pointer; color:var(--text);} .rp-sug li.on, .rp-sug li:hover{background:#1d2731;}
  .it-map-box button.it-map-clr{top:46px;}
  .rp-menu{position:absolute; z-index:6; min-width:230px; padding:6px; border:1px solid #2c3842; border-radius:6px; background:var(--panel-2); box-shadow:0 8px 22px rgba(0,0,0,.55); font:400 12px/1.35 var(--sans); color:var(--text);}
  .rp-mh{padding:3px 6px 6px; border-bottom:1px solid var(--line); margin-bottom:4px;}
  .rp-btns{display:flex; flex-direction:column; gap:2px;}
  .rp-btns button{display:block; width:100%; text-align:left; min-height:30px; padding:4px 8px; border:0; border-radius:4px; background:transparent; color:var(--text); font:600 12px/1.3 var(--sans); cursor:pointer;}
  .rp-btns button span{font-weight:400; color:var(--text-dim);} .rp-btns button small{display:block; font:400 11px var(--sans); color:var(--text-dim);}
  .rp-btns button:hover:not([disabled]), .rp-btns button:focus-visible{background:#1d2731; outline:1px solid var(--cyan);}
  .rp-btns button[disabled]{opacity:.45; cursor:default;} .rp-btns .rp-av{border-top:1px solid var(--line); border-radius:0 0 4px 4px;}
  .it-map-tip.rp-act{pointer-events:auto; z-index:5;} .rp-in-tip{margin-top:6px;} .rp-in-tip button{min-height:44px; border:1px solid var(--line); margin-top:4px;}
  .rp-w{color:var(--amber);} .rp-n b{color:var(--heading);}
  .rp-toast{position:absolute; left:8px; right:8px; bottom:52px; z-index:5; padding:8px 30px 8px 10px; border:1px solid var(--cyan); border-radius:6px; background:rgba(18,23,28,.96); font:400 12px/1.4 var(--sans); color:var(--text);}
  .rp-toast.warn{border-color:var(--amber);} .rp-toast[hidden]{display:none;} .rp-toast .x-close{position:absolute; right:4px; top:4px;}
  .rp-toast .mk{color:#e4b5ff;}
  .rp-box .rp-pref{display:flex; flex-wrap:wrap; gap:4px 12px;} .rp-avk{margin-top:6px; color:var(--text-dim); font-size:12px;}
  .rp-pen input{vertical-align:middle; width:140px;} .rp-list{list-style:none; margin:6px 0; padding:0;} .rp-list li{display:flex; align-items:center; justify-content:space-between; gap:6px; font-size:12px; min-height:28px;}
  .rp-add{display:flex; gap:6px;} .rp-add input{flex:1; min-width:0;}
  @media (max-width: 599px){ .rp-search{top:60px; right:8px; width:auto;} .rp-search input{min-height:44px; font-size:16px;} .it-map-box button.it-map-clr{top:112px;} .rp-toast{bottom:60px;} .rp-list li{min-height:44px;} }
  `;
  document.head.appendChild(css);
})();
