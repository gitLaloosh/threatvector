// MOCKUP prototype: J-space statics known on entry (Project doc claude/roadmap/wh-statics-plan.md).
// Runs after the real page's script (main 513c1e6). Statics are Wanderer's real list (wanderer-industries/wanderer, MIT,
// priv/repo/data/wormholeSystems.json at 4d4a035); mass and lifetime are CCP's own wormhole types (pyfa's SDE dump).
// The chain is made up: wormhole systems picked by position from CCP's table (INTEL_WH), no pilots, no corporations.
// "Proposed": (1) a system's statics are yours if you typed any, else the list's, with a small note saying where they're from;
// (2) the map box lists where they lead in class order; (3) a static's hover adds lifetime and mass; (4) typing a connection's
// type offers the system's statics first, then K162, then the rest. "Today" is the real page as built.
(function(){
  'use strict';
  let mode = 'proposed';
  const on = () => mode === 'proposed';
  // where a hole leads, in Wanderer's order (its sortWHClasses: CCP's class number): C1-C6, high, low, null, Thera, shattered, Drifter, Pochven
  const ORD = {c1: 1, c2: 2, c3: 3, c4: 4, c5: 5, c6: 6, hs: 7, ls: 8, ns: 9, th: 12, c13: 13, dr: 14, po: 25};
  const rank = (c) => c === 'K162' ? 99 : ORD[IT_WH_TYPE[c]] || 98;
  const sortCodes = (v) => String(v || '').split(' ').filter(Boolean).sort((a, b) => rank(a) - rank(b) || a.localeCompare(b)).join(' ');
  const listOf = (n) => (whIsJ(n) && MOCK_STATICS[n]) || '';
  const typed = (n) => { const s = whS && whS.st.sys[n]; return s ? s.statics : ''; };
  const num = (x) => Number(x).toLocaleString('en-US');
  function detail(code){   // CCP's own numbers for the type: lifetime (minutes), total mass, mass per jump, regeneration (tonnes)
    const i = MOCK_WHINFO[code]; if(!i) return '';
    return [`up to ${i[0] % 60 ? (i[0] / 60).toFixed(1) : i[0] / 60} h`, `${num(i[1])} t in all`, `${num(i[2])} t per jump`, i[3] ? `regains ${num(i[3])} t` : ''].filter(Boolean).join(' · ');
  }
  const css = `
  .wh-stcsrc{display:block; margin-top:2px;}
  #stcBar{position:fixed; z-index:99999; left:50%; transform:translateX(-50%); top:8px; display:flex; flex-wrap:wrap; gap:6px; align-items:center; max-width:calc(100vw - 24px); box-sizing:border-box;
    padding:8px 10px; border:1px dashed var(--amber); border-radius:6px; background:#12171c; color:var(--text); font:12px var(--sans); box-shadow:0 6px 20px rgba(0,0,0,.6);}
  #stcBar b{color:var(--amber); letter-spacing:.5px;} #stcBar button{min-height:28px; padding:0 9px; font-size:12px;} #stcBar button[aria-pressed="true"]{background:var(--amber); color:#1b1306;}
  #stcBar.fold > :not(.stc-fold){display:none;} @media (max-width:599px){ #stcBar{left:8px; right:8px; transform:none;} #stcBar button{min-height:44px;} }
  `;
  const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  // ---- (3) the chip's hover: where it leads (today), then CCP's lifetime and mass
  const oStc = whStcHtml;
  whStcHtml = function(code){
    const h = oStc(code); if(!on() || code === 'K162') return h;
    const d = detail(code); return d ? h.replace(/title="([^"]*)"/, (m, t) => `title="${t} · ${escapeHtml(d)}"`) : h;
  };
  // ---- (2) chips in class order (Wanderer's order), for typed statics and the list's alike
  const oStcs = whStcsHtml;
  whStcsHtml = function(v){ return oStcs(on() ? sortCodes(v) : v); };
  // ---- (1) the System panel: yours if typed, else the list's, with the note (the page's own "from CCP's data" note, as Class has)
  const NOTE_LIST = 'from the community list (Wanderer) · type your own to replace them', NOTE_YOU = 'typed by you';
  const srcNote = (n) => !on() || !whIsJ(n) ? '' : typed(n) ? `<span class="wh-note wh-stcsrc" data-stc-src>${escapeHtml(NOTE_YOU)}</span>`
    : listOf(n) ? `<span class="wh-note wh-stcsrc" data-stc-src>${escapeHtml(NOTE_LIST)}</span>` : '';
  const oSum = whSumHtml;
  whSumHtml = function(n){
    let h = oSum(n); if(!on() || !whIsJ(n)) return h;
    const own = typed(n), eff = own || listOf(n);
    return h.replace(/<span class="wh-stc" data-wh-stc>[\s\S]*?<\/span><span class="wh-note" data-wh-bad/, () => `<span class="wh-stc" data-wh-stc>${whStcsHtml(eff)}</span>${srcNote(n)}<span class="wh-note" data-wh-bad`);
  };
  // typing in the field: today's handler draws the typed chips; an empty field shows the list's again
  document.addEventListener('input', (e) => {
    const f = e.target; if(!on() || !f.matches || !f.matches('[data-f="statics"]')) return;
    const ed = f.closest('[data-wh-ed]'), n = Number(ed && ed.dataset.whEd); if(!n) return;
    const box = ed.querySelector('[data-wh-stc]'), v = whStatics(f.value).ok;
    box.innerHTML = whStcsHtml(v || listOf(n));
    const old = ed.querySelector('[data-stc-src]'); if(old) old.remove();
    const t = document.createElement('template'); t.innerHTML = v ? `<span class="wh-note wh-stcsrc" data-stc-src>${escapeHtml(NOTE_YOU)}</span>` : srcNote(n); if(t.content.firstChild) box.after(t.content.firstChild);
  });
  // ---- (1)+(2) the map box: draw with the list's statics where none are typed, in class order (only while drawing; nothing saved)
  const oDraw = whDraw;
  whDraw = function(){
    if(!on() || !whS) return oDraw.apply(this, arguments);
    const keep = [];
    for(const [id, s] of Object.entries(whS.st.sys)){ const n = Number(id), v = s.statics || listOf(n); if(v){ keep.push([s, s.statics]); s.statics = sortCodes(v); } }
    try{ return oDraw.apply(this, arguments); } finally { for(const [s, v] of keep) s.statics = v; }
  };
  // ---- (4) a connection's type: the system's statics first, then K162, then the rest (the browser's own suggestion list on the field)
  const oCnEd = whCnEditHtml;
  whCnEditHtml = function(c, r){
    const h = oCnEd(c, r); if(!on()) return h;
    const n = c.n, mine = sortCodes(typed(n) || listOf(n)).split(' ').filter(Boolean), rest = Object.keys(IT_WH_TYPE).filter(x => x !== 'K162' && !mine.includes(x)).sort();
    const opt = (code, lab) => `<option value="${escapeHtml(code)}" label="${escapeHtml(lab)}"></option>`;
    const dl = `<datalist id="stcTyDl">` + mine.map(x => opt(x, `static → ${itWhDestTxt(x)[0]}`)).join('') + opt('K162', 'exit of a hole from the other side')
      + rest.map(x => opt(x, `→ ${IT_WH_TYPE[x] === 'exit' ? 'exit' : itWhDestTxt(x)[0]}`)).join('') + '</datalist>';
    return h.replace('data-wh-le="type"', 'data-wh-le="type" list="stcTyDl"').replace(/<\/div>$/, dl + '</div>');
  };

  // ---- made-up chain: CCP's wormhole systems picked by position; one with statics typed by you, the rest from the list
  const T0 = Date.now() - 3 * 3600e3;
  let PICK = null;
  function picks(){ if(PICK) return PICK; const T = whTable(), J = T.names.filter(x => /^J\d{6}$/.test(x)); PICK = [40, 310, 655, 902, 1210, 1488, 1733].map(i => whIdOf(J[i % J.length])); return PICK; }
  function seed(){
    if(localStorage.getItem('tvWhChain')) return;
    const p = picks(), path = [p[0], p[1], p[2], p[1], p[3], p[4], p[3], p[5], p[6]];
    path.forEach((id, i) => whSeen(id, T0 + i * 60e3, false));
    const S = whState(); S.st.sys[p[0]].statics = 'D845';   // typed by you (on purpose not the list's, to show yours win)
    S.st.links.forEach((l, i) => { if(i === 0){ l.sig = 'ABC-123'; l.type = 'H296'; } });
    S.mk[p[0]] = {st: 'home', tag: 'HOME', lock: true};
    whSave(); whMkSave(); S.drawKey = '';
  }
  function openSys(id){ if(whS.open !== 'sum') whPnSet('sum', true); whSelect(id); }
  function bar(){
    const b = document.createElement('div'); b.id = 'stcBar';
    b.innerHTML = '<b>MOCKUP</b><span>Statics on entry:</span><button type="button" data-m="today" aria-pressed="false">Today</button><button type="button" data-m="proposed" aria-pressed="true">Proposed</button>'
      + '<button type="button" data-m="list">A system from the list</button><button type="button" data-m="typed">One you typed</button><button type="button" data-m="enter">Enter a new system</button>'
      + '<button type="button" data-m="reset">Reset</button><button type="button" class="stc-fold" data-m="fold" aria-label="Fold the bar">⇕</button>';
    b.addEventListener('click', (e) => {
      const m = e.target.closest('button') && e.target.closest('button').dataset.m; if(!m) return;
      if(m === 'fold'){ b.classList.toggle('fold'); return; }
      if(m === 'today' || m === 'proposed'){ mode = m; b.querySelectorAll('[data-m="today"],[data-m="proposed"]').forEach(x => x.setAttribute('aria-pressed', String(x.dataset.m === m))); whS.drawKey = ''; whPaint(true); return; }
      if(m === 'list'){ openSys(picks()[2]); return; }
      if(m === 'typed'){ openSys(picks()[0]); return; }
      if(m === 'enter'){ const T = whTable(), J = T.names.filter(x => /^J\d{6}$/.test(x)), id = whIdOf(J[(2222 + Math.floor(Math.random() * 300)) % J.length]);
        whSeen(id, Date.now(), false); whS.drawKey = ''; openSys(id); return; }
      if(m === 'reset'){ for(const k of ['tvWhChain', 'tvWhMarks', 'tvWhSigs', 'tvWhEnds', 'tvWhSecs', 'tvWhPanels']) localStorage.removeItem(k); location.reload(); }
    });
    document.body.appendChild(b);
  }
  function start(){
    seed(); bar();
    switchTab('wh');
    setTimeout(() => { const S = whState(); S.drawKey = ''; openSys(picks()[2]); }, 300);
  }
  if(document.readyState === 'complete') setTimeout(start, 50); else window.addEventListener('load', () => setTimeout(start, 50));
})();
