"""Intel's Wormholes list: a jump between k-space and J-space adds that k-space system's hole by itself (build queue 062, A1-A5; Project doc
roadmap/wormholes-part4-plan.md section 4; the owner: "when entering a wormhole from k-space, automatically add a wormhole to the wormhole list of the
intel map. when making this transition, the page already captures all of the needed information about the wormhole aside from the signature ID in
k-space. perhaps this should be toggled on/off in the intel settings"; Q8 "Switch, on", Q9 "Yes, same switch", Q10 "Yes", Q11 "No, separate").

Made-up jumps between CCP's own systems (the page's tables); no network. Checks:
  * k → J (not docked) adds k's entry: src 'you', the jump's time, jw naming the J system, its class (C1-C6 etc.); the row says
    "you jumped in → J… (C3 · Pulsar · statics …)" and its hover the effect's numbers;
  * an Intel report already there: merged (its IDs, who and lines kept, src kept), never replaced;
  * docked arrivals add nothing; J → J adds nothing; J → k adds the exit (jw.out);
  * the setting: in Intel settings beside "keep wormhole reports for", on by default and when missing (an older page's store), off adds
    nothing, kept in tvWormholes through a reload;
  * the k-space end's ID set on the Wormholes tab fills the entry (one way); removing either never removes the other;
  * an older page (f70fdd5) reads the store and drops jw when it saves; this page then shows the entry as a hand-added hole;
  * the Intel example (itWhAside) never adds;
  * mutants; no page errors.
"""
import sys, os, json, tempfile, subprocess
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
HTML = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith('--')), os.path.join(REPO, 'index.html')))
PAGE = open(HTML, encoding='utf-8').read()
OLD = 'f70fdd5'   # v2026.11.20.1, the last main before 062: never origin/main, which is this page once it's merged (LESSON #168)
fails = 0
def check(ok, msg):
    global fails
    print(('PASS ' if ok else 'FAIL ') + msg)
    if not ok: fails += 1

# k: two k-space systems the map knows; j: a C3 Pulsar and a C2 (CCP's own names, from the page's table)
SEED = """() => { const T = whTable(), g = itGraphGet(), pick = (f) => T.ids.find((id, i) => f(i));
  const j3 = pick(i => T.cls[i] === '3' && T.eff[i] === 'p' && /^J\\d{6}$/.test(T.names[i])), j2 = pick(i => T.cls[i] === '2' && /^J\\d{6}$/.test(T.names[i]));
  return {k1: g.ids[100], k2: g.ids[2000], j3, j2}; }"""
ST = "JSON.parse(localStorage.getItem('tvWormholes') || 'null')"

def start(b, html, errs, keep=False, w=1440):
    ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': 900})
    ctx.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
    pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + html)
    if not keep: pg.evaluate("localStorage.clear()"); pg.reload()
    pg.wait_for_timeout(300)
    return ctx, pg

def cases(b, html, parts=('add', 'merge', 'skip', 'setting', 'end', 'reload', 'older', 'example')):
    out, errs = [], []
    ctx, pg = start(b, html, errs); ev = pg.evaluate
    S = ev(SEED); t0 = ev("Date.now()") - 3 * 3600e3
    if not all(S.values()): out.append(f'the seed needs two k-space systems, a C3 Pulsar and a C2: {S}')
    seen = lambda id, dt, docked=False: ev("([id, t, d]) => whSeen(id, t, d)", [id, t0 + dt * 60e3, docked])
    if 'add' in parts:
        seen(S['k1'], 0); seen(S['j3'], 1)
        w = (ev(ST) or {}).get('rep', {}).get(str(S['k1']))
        if not w or w.get('src') != 'you' or (w.get('jw') or {}).get('j') != S['j3'] or w.get('jw', {}).get('out') or (w.get('info') or {}).get('cls') != 'C3' or abs(w['t'] - (t0 + 60e3)) > 1:
            out.append(f'k → J adds the k-space entry (you, jw, C3, the jump\'s time): {w}')
        row = ev("(k) => { const d = document.createElement('div'); d.innerHTML = itWhRowsHtml(); const b = d.querySelector(`[data-it-whgo=\"${k}\"]`); const r = b && b.closest('.it-whp-r'); const by = r && r.querySelector('.it-whp-by'); return by ? [by.textContent, by.title] : null; }", S['k1'])
        name = ev("(j) => whName(j)", S['j3'])
        if not row or f'you jumped in → {name} (C3 · Pulsar' not in row[0] or not row[1].startswith('Pulsar: Shield HP +58%'): out.append(f'the row\'s words and its hover: {row}')
        seen(S['j2'], 2)
        if len(ev(ST)['rep']) != 1: out.append(f'J → J adds nothing: {list(ev(ST)["rep"])}')
        seen(S['k2'], 3)
        w2 = ev(ST)['rep'].get(str(S['k2']))
        if not w2 or (w2.get('jw') or {}).get('j') != S['j2'] or w2['jw'].get('out') is not True: out.append(f'J → k adds the exit (jw.out): {w2}')
        if 'you came out of' not in ev("(k) => itWhByTxt(itWhStore().rep[k])", S['k2']): out.append('the exit\'s words: "you came out of"')
    if 'merge' in parts:
        ev("() => { localStorage.clear(); itWhSt = null; whS = null; }"); pg.reload(); pg.wait_for_timeout(300)
        ev("""([k, t]) => { const st = itWhStore(); st.rep[k] = {id: k, t, who: 'Mk Scout', drifter: false, src: 'intel', sigs: [{sig: 'ABC-123', part: false, type: 'D845', t, who: 'Mk Scout'}],
          raws: [{t, who: 'Mk Scout', raw: 'mk line', k: 'intel'}]}; itWhSave(); }""", [S['k1'], t0])
        seen(S['k1'], 1); seen(S['j3'], 2)
        w = ev(ST)['rep'][str(S['k1'])]
        if [x['sig'] for x in w.get('sigs', [])] != ['ABC-123'] or w.get('who') != 'Mk Scout' or w.get('src') != 'intel' or len(w.get('raws', [])) != 1 or (w.get('jw') or {}).get('j') != S['j3']:
            out.append(f'a report there: merged, its IDs, who and lines kept: {w}')
    if 'skip' in parts:
        ev("() => { localStorage.clear(); itWhSt = null; whS = null; }"); pg.reload(); pg.wait_for_timeout(300)
        seen(S['k1'], 0); seen(S['j3'], 1, True)
        if (ev(ST) or {}).get('rep'): out.append('a docked arrival adds nothing')
    if 'setting' in parts:
        ev("() => { localStorage.clear(); itWhSt = null; whS = null; }"); pg.reload(); pg.wait_for_timeout(300)
        ev("() => { switchTab('intel'); itRender(true); }"); pg.wait_for_timeout(150)
        html_ = ev("itSettingsHtml(false)")
        if 'data-it-whauto checked' not in html_ or html_.find('data-it-whkeep') > html_.find('data-it-whauto'): out.append('the setting: on by default, right after "keep wormhole reports for"')
        ev("() => localStorage.setItem('tvWormholes', JSON.stringify({v: 1, rep: {}, gone: {}, keepH: 12}))"); ev("() => { itWhSt = null; }")
        if ev("itWhStore().auto") is not True: out.append('a store without the field (an older page\'s): on')
        ev("() => { const d = document.createElement('div'); d.innerHTML = itSettingsHtml(false); document.body.appendChild(d); d.id = 'mkSet'; }")
        ev("() => { const c = document.querySelector('#mkSet [data-it-whauto]'); c.checked = false; c.dispatchEvent(new Event('change', {bubbles: true})); }")
        if ev("itWhStore().auto") is not False:   # the settings' own change handler lives on Intel's card: press it there
            ev("() => { const c = document.querySelector('#tabIntel [data-it-whauto]'); if(c){ c.checked = false; c.dispatchEvent(new Event('change', {bubbles: true})); } }")
        if ev("itWhStore().auto") is not False or (ev(ST) or {}).get('auto') is not False: out.append('unticking it turns it off, kept in tvWormholes')
        seen(S['k1'], 0); seen(S['j3'], 1)
        if (ev(ST) or {}).get('rep'): out.append('off: a jump adds nothing')
        pg.reload(); pg.wait_for_timeout(300)
        if ev("itWhStore().auto") is not False: out.append('off is kept through a reload')
    if 'end' in parts:
        ev("() => { localStorage.clear(); itWhSt = null; whS = null; }"); pg.reload(); pg.wait_for_timeout(300)
        seen(S['k1'], 0); seen(S['j3'], 1)
        ev("([k, j]) => { const l = whState().st.links.find(l => (l.a === k && l.b === j) || (l.a === j && l.b === k)); whEndSet(l, k, 'XYZ-789', 'D845'); whEndSave(); }", [S['k1'], S['j3']])
        w = ev(ST)['rep'][str(S['k1'])]
        if [(x['sig'], x.get('type')) for x in w.get('sigs', [])] != [('XYZ-789', 'D845')]: out.append(f'the k-space end\'s ID fills the entry: {w.get("sigs")}')
        ev("([k, j]) => { const l = whState().st.links.find(l => (l.a === k && l.b === j) || (l.a === j && l.b === k)); whEndSet(l, j, 'QRS-456', ''); }", [S['k1'], S['j3']])
        if len(ev(ST)['rep'][str(S['k1'])].get('sigs', [])) != 1: out.append('the J-space end\'s ID doesn\'t go to the Intel entry')
        ev("(k) => itWhRemove(k)", S['k1'])
        if ev("([k, j]) => !!whState().st.links.find(l => (l.a === k && l.b === j) || (l.a === j && l.b === k))", [S['k1'], S['j3']]) is not True: out.append('removing the Intel entry leaves the chain')
        seen(S['k2'], 2); seen(S['j2'], 3)
        ev("([k, j]) => { const S = whState(); S.st.links = S.st.links.filter(l => !((l.a === k && l.b === j) || (l.a === j && l.b === k))); whSave(); }", [S['k2'], S['j2']])
        if str(S['k2']) not in ev(ST)['rep']: out.append('removing the chain\'s connection leaves the Intel entry')
    if 'reload' in parts:   # a store holding jw read at start-up (the setting's mutant found it: WH_LO not there yet)
        ev("() => { localStorage.clear(); itWhSt = null; whS = null; }"); pg.reload(); pg.wait_for_timeout(300)
        seen(S['k1'], 0); seen(S['j3'], 1); n0 = len(errs)
        pg.reload(); pg.wait_for_timeout(400)
        if len(errs) > n0 or ev("(k) => !!(itWhStore().rep[k] || {}).jw", S['k1']) is not True: out.append(f'a reload with jw kept: no error, jw read back {errs[n0:n0 + 1]}')
    if 'example' in parts:
        if ev("([k, j, t]) => { itWhAside = true; try{ return itWhJumpAdd(k, j, t, false); } finally { itWhAside = false; } }", [S['k1'], S['j2'], t0 + 600e3]) is not False: out.append('the Intel example never adds')
    ctx.close()
    if 'older' in parts:
        old = os.path.join(os.path.dirname(HTML), '.wh_old_062.html')
        try:
            open(old, 'w', encoding='utf-8').write(subprocess.check_output(['git', '-C', REPO, 'show', f'{OLD}:index.html']).decode('utf-8'))
            ctx, pg = start(b, html, errs); ev = pg.evaluate; t0 = ev("Date.now()") - 3600e3
            ev("([k, j, t]) => { whSeen(k, t, false); whSeen(j, t + 60e3, false); }", [S['k1'], S['j3'], t0])
            if not (ev(ST) or {}).get('rep', {}).get(str(S['k1']), {}).get('jw'): out.append('older: the new page should have written jw first')
            pg.goto('file://' + old); pg.wait_for_timeout(400)
            n = pg.evaluate("() => { const st = itWhStore(); const n = Object.keys(st.rep).length; itWhSave(); return n; }")
            if n != 1: out.append(f'the older page (f70fdd5) should read the entry: {n}')
            if 'jw' in pg.evaluate(ST)['rep'][str(S['k1'])]: out.append('the older page drops jw when it saves')
            pg.goto('file://' + html); pg.wait_for_timeout(300)
            if pg.evaluate("(k) => itWhByTxt(itWhStore().rep[k])", S['k1']) != 'added by you': out.append('back on this page: the entry as a hand-added hole')
            ctx.close()
        finally:
            if os.path.exists(old): os.unlink(old)
    return out, errs

MUTANTS = [
    ('a replace in place of a merge', "  const n = old ? {...old} : {id: k, t, who: '', drifter: false, src: 'you', sigs: []};", "  const n = {id: k, t, who: '', drifter: false, src: 'you', sigs: []};", ('merge',)),
    ('docked arrivals added', "if(prev !== null && (j || jp) && !docked){", "if(prev !== null && (j || jp)){", ('skip',)),
    ('the switch ignored', "if(!st.auto || !(t >= now", "if(!(t >= now", ('setting',)),
    ('off by default', "keepH: 24, auto: true};", "keepH: 24, auto: false};", ('setting',)),
    ('the exit not added', "if(j !== jp) itWhJumpAdd(", "if(j && !jp) itWhJumpAdd(", ('add',)),
    ('a page with jw kept stops at start-up (WH_LO before it exists)', "jw.j >= 31000000 && jw.j < 32000000 && ok(", "whIsJ(jw.j) && ok(", ('reload',)),
    ('the end\'s ID not passed on', "  if(sig && !whIsJ(n)) itWhJumpSig(n, l.a === n ? l.b : l.a, sig, type);", "", ('end',)),
    ('added inside the Intel example', "  if(itWhAside || !itGraphGet().at.has(k) || !whIsJ(j)) return false;", "  if(!itGraphGet().at.has(k) || !whIsJ(j)) return false;", ('example',)),
]

if __name__ == '__main__':
    with sync_playwright() as p:
        b = p.chromium.launch()
        out, errs = cases(b, HTML)
        for o in out: check(False, o)
        check(not out, 'Auto-add: k → J and J → k, merged, docked and J → J skipped, the setting, the end\'s ID, the older page, the example')
        check(not errs, f'no page errors {errs[:3]}')
        for name, old, new, parts in MUTANTS:
            if PAGE.count(old) != 1: check(False, f'mutant "{name}": its line isn\'t in the page once'); continue
            with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f:
                f.write(PAGE.replace(old, new)); mp = f.name
            try:
                try: mo, me = cases(b, mp, parts)
                except Exception as e: mo, me = [f'the check stopped: {str(e).splitlines()[0]}'], []
                check(bool(mo) or bool(me), f'mutant "{name}" fails ({(mo or me or ["nothing"])[0][:90]})')
            finally: os.unlink(mp)
        b.close()
    print('FAILURES:', fails)
    sys.exit(1 if fails else 0)
