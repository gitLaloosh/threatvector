"""Intel in one tab at a time (v2026.11.08.3, build queue 026; Project doc roadmap/intel-one-tab-plan.md).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/intel_one_tab_check.py [index.html]   -> 'FAILURES: N' (must be 0)

Two pages in one browser context (one origin: they share the Web Lock and the BroadcastChannel), each with intel_check.py's made-up
Chatlogs folder and its quiet R2Z2 stand-in. R2Z2 requests are counted per page. Checks:
  * A turns Intel on: B says "Intel is on in another tab." with Move Intel here, its switch is disabled (a click on it does nothing,
    its title says why), its profile mark and Intel tab dot show A's state, and B asks R2Z2 nothing;
  * Move Intel here in B: the folder permission asked from the click itself, then B runs, A stops and says "Intel moved to another
    tab." with Move Intel back here, its switch disabled; from then on only B asks R2Z2 (A's in-flight work stops);
  * the permission refused on Move Intel back here: A stays off with INTEL-02, B keeps running;
  * an alert (a hostile one jump away) sounds and notifies once, in the running tab only;
  * the same mark posted twice redraws nothing; a new count is drawn;
  * B (running) closed: A's line says the tab was closed, its switch is no longer disabled, its mark is off, nothing starts by itself;
  * a running tab that crashes (no pagehide): the other tab notices through locks.query() when it is shown again;
  * Intel turned on reads R2Z2 at once; a catch-up after a gap waits a random 0-10 s first (the owner: "Only after a gap");
  * no navigator.locks: Intel runs as before, with no line;
  * the Intel map: window resizes 1100 <-> 1300 px give no "ResizeObserver loop" error, and the map follows the new size;
  * 390 px: Move Intel here at least 44 px tall, no sideways scroll; no page errors.
"""
import sys, os, re, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SRC = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
exec(compile(SRC[:SRC.index('with sync_playwright() as p:')], 'intel_check', 'exec'))   # its folder stand-in, logs, ESI and R2Z2 routes

fails = 0
def check(ok, msg):
    global fails
    print(('ok   ' if ok else 'FAIL ') + msg)
    if not ok: fails += 1

# the folder's permission answer for Move Intel here, and whether the press was still live when it was asked
EXTRA = r"""(() => {
  __fs.asked = []; __fs.answer = 'granted';
  const pick = window.showDirectoryPicker;
  if(pick) window.showDirectoryPicker = async () => { const d = await pick(); d.requestPermission = async () => { __fs.asked.push(navigator.userActivation ? navigator.userActivation.isActive : null); return __fs.answer; }; return d; };
  window.__roErr = 0;
  window.addEventListener('error', (e) => { if(/ResizeObserver loop/.test(e.message || '')) window.__roErr++; });
})();"""
NOLOCKS = "(() => { try{ Object.defineProperty(navigator, 'locks', {value: undefined, configurable: true}); }catch(e){} })();"
ST = """() => { const q = (s) => document.querySelector(s), sw = q('#intelSw'), mv = q('#itNotes [data-it-act="move"]');
  return {on: it.on, other: it.other, why: it.lockWhy, notes: ((q('#itNotes') || {}).textContent || '').replace(/\\s+/g, ' ').trim(),
    move: mv ? mv.textContent : '', moveH: mv ? mv.getBoundingClientRect().height : 0, swDis: sw ? sw.disabled : null, swTitle: sw ? (sw.title || (sw.closest('label') || {}).title || '') : '',
    mark: (q('#profile') || {dataset: {}}).dataset.s, tab: (q('#tabBtnIntel') || {dataset: {}}).dataset.s, near: (q('#intelNearN') || {}).textContent || '',
    markTitle: (q('#intelNear') || {}).title || '', err: it.err, sw: document.documentElement.scrollWidth, vw: innerWidth}; }"""

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    errs = []
    R2 = {}   # page name -> R2Z2 requests
    def ctx_new(w=1440, nolocks=False):
        c = b.new_context(bypass_csp=True, viewport={'width': w, 'height': 1000})
        c.add_init_script(FS); c.add_init_script(EXTRA)
        if nolocks: c.add_init_script(NOLOCKS)
        route(c); return c
    def page(c, name, first=False):
        pg = c.new_page(); R2[name] = 0
        pg.on('pageerror', lambda e: errs.append(f'{name}: {e}'))
        pg.on('request', lambda r: R2.__setitem__(name, R2[name] + 1) if 'r2z2.zkillboard.com' in r.url else None)
        pg.goto('file://' + HTML)
        if first: pg.evaluate("(s) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.removeItem('dscanIntel'); }", SIDE); pg.reload()
        pg.wait_for_function("typeof it !== 'undefined' && it.loaded")
        setup_logs(pg); pg.click('#tabBtnIntel'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(400)
        if not pg.is_checked('[data-it-chan="region.intel"]'): pg.check('[data-it-chan="region.intel"]')
        if not pg.is_checked(f'[data-it-me="{MAIN}"]'): pg.check(f'[data-it-me="{MAIN}"]')
        pg.wait_for_timeout(200); return pg
    st = lambda pg: pg.evaluate(ST)

    c = ctx_new()
    A = page(c, 'A', first=True); B = page(c, 'B')
    t0 = time.time(); A.click('#intelSwLabel'); A.wait_for_function("it.on && it.kf && it.kf.seq !== null", timeout=8000); first_read = time.time() - t0
    A.wait_for_timeout(2500); B.wait_for_timeout(300)
    a, s = st(A), st(B)
    check(a['on'] and not s['on'] and s['other'], f'A runs Intel; B knows another tab does {a["on"]} {s["on"]} {s["other"]}')
    check(s['notes'].startswith('Intel is on in another tab.') and s['move'] == 'Move Intel here', f'B: "Intel is on in another tab." with Move Intel here {s["notes"]!r}')
    check(s['swDis'] is True and 'Intel is running in another tab' in s['swTitle'], f'B: the switch disabled, its title says why {s["swDis"]} {s["swTitle"]!r}')
    check(s['mark'] == a['mark'] and s['tab'] == a['tab'] and s['mark'] not in (None, 'off') and 'from your other Threat Vector tab' in s['markTitle'],
          f'B: its profile mark and tab dot show A\'s ({a["mark"]}/{a["tab"]} vs {s["mark"]}/{s["tab"]}); title {s["markTitle"]!r}')
    check(R2['A'] > 0 and R2['B'] == 0, f'only A asks R2Z2 {R2}')
    check(first_read < 4, f'turning Intel on reads R2Z2 at once (no wait on start: the owner, "Only after a gap") {first_read:.1f} s')
    B.evaluate("() => document.getElementById('intelSw').click()"); B.wait_for_timeout(500)
    check(not st(B)['on'] and st(A)['on'], 'a click on B\'s disabled switch starts nothing')

    # the same mark twice redraws nothing; a new count is drawn
    B.evaluate("() => { window.__draws = 0; new MutationObserver(() => window.__draws++).observe(document.getElementById('intelPanel'), {childList: true, subtree: true}); }")
    B.evaluate("() => { itLockHear({on: true, s: it.remote.s, n: it.remote.n}); itLockHear({on: true, s: it.remote.s, n: it.remote.n}); }"); B.wait_for_timeout(200)
    same = B.evaluate("() => window.__draws")
    B.evaluate("() => itLockHear({on: true, s: 'near', n: 4})"); B.wait_for_timeout(200)
    nb = st(B)
    check(same == 0 and nb['mark'] == 'near' and nb['near'] == '4 near', f'the same mark posted twice redraws nothing ({same} writes); a new one is drawn {nb["mark"]} {nb["near"]!r}')
    A.evaluate("() => { itLk.last = ''; itLockState(); }"); B.wait_for_timeout(300)   # back to A's real mark

    # Move Intel here (B)
    R2['A'] = R2['B'] = 0
    B.click('#itNotes [data-it-act="move"]'); B.wait_for_function("it.on", timeout=8000); B.wait_for_timeout(300); A.wait_for_timeout(300)
    a, s = st(A), st(B)
    asked = B.evaluate("() => __fs.asked")
    check(s['on'] and not a['on'] and asked and asked[-1] is True, f'Move Intel here: B runs, A stopped; the folder asked from the click itself {s["on"]} {a["on"]} {asked}')
    check(s['notes'].startswith('Intel moved here.'), f'B: "Intel moved here. The other tab stopped it." {s["notes"]!r}')
    check(a['notes'].startswith('Intel moved to another tab.') and a['move'] == 'Move Intel back here' and a['swDis'] is True,
          f'A: "Intel moved to another tab." with Move Intel back here, its switch disabled {a["notes"]!r} {a["move"]!r} {a["swDis"]}')
    R2['A'] = R2['B'] = 0; B.wait_for_timeout(4000)
    check(R2['A'] == 0 and R2['B'] > 0, f'after the move only B asks R2Z2 (A\'s in-flight work stopped) {R2}')
    B.wait_for_timeout(int(6000 - 4000 + 100)); s = st(B)
    check(not s['notes'].startswith('Intel moved here.'), f'B\'s "moved here" line goes after a few seconds {s["notes"]!r}')

    # refused on Move Intel back here
    A.evaluate("() => { __fs.answer = 'denied'; }")
    A.click('#itNotes [data-it-act="move"]'); A.wait_for_timeout(800)
    a, s = st(A), st(B)
    check(not a['on'] and s['on'] and '(INTEL-02)' in a['err'], f'the permission refused: A stays off with INTEL-02, B keeps running {a["on"]} {s["on"]} {a["err"][-60:]!r}')
    A.evaluate("() => { __fs.answer = 'granted'; it.err = ''; itRender(true); }")

    # one alert, in the running tab only
    for pg in (A, B): pg.evaluate("() => { __fs.beeps = 0; __fs.notes = []; }")
    for pg in (A, B): W(pg, F_INTEL, line(time.time(), 'Scout Alt', '8WA-Z6 Marrek Ketter sabre'))
    B.wait_for_timeout(5000)
    al = [pg.evaluate("() => [__fs.beeps, __fs.notes.length]") for pg in (A, B)]
    check(al[0] == [0, 0] and al[1][0] == 1 and al[1][1] == 1, f'an alert sounds and notifies once, in the running tab only [A, B] {al}')

    # B (running) closed: nothing starts by itself
    B.close(); A.wait_for_timeout(800)
    a = st(A)
    check(not a['on'] and not a['other'] and a['notes'] == 'The tab running Intel was closed, so Intel is off.' and a['swDis'] is False and a['mark'] == 'off',
          f'the running tab closed: A says so, its switch free, its mark off, nothing started {a}')
    R2['A'] = 0; A.wait_for_timeout(2500)
    check(R2['A'] == 0 and not st(A)['on'], f'nothing starts by itself afterwards {R2["A"]}')

    # a crash: A runs, C watches; A crashes without pagehide; C notices when shown again
    C = page(c, 'C')
    A.click('#intelSwLabel'); A.wait_for_function("it.on", timeout=8000); C.wait_for_timeout(800)
    check(st(C)['other'], 'C sees A running')
    try: A.goto('chrome://crash', timeout=3000)   # the renderer dies: no pagehide, no message
    except Exception: pass
    C.wait_for_timeout(800)
    C.evaluate("() => document.dispatchEvent(new Event('visibilitychange'))"); C.wait_for_timeout(500)
    cs = st(C)
    check(not cs['other'] and cs['notes'] == 'The tab running Intel was closed, so Intel is off.' and cs['swDis'] is False and not cs['on'],
          f'a crashed running tab: C notices when shown again, nothing starts {cs}')

    # staggered catch-up: a gap makes the next read-back wait 0-10 s first
    C.click('#intelSwLabel'); C.wait_for_function("it.on && it.kf && it.kf.seq !== null", timeout=8000); C.wait_for_timeout(1500)
    waits = C.evaluate("""async () => { const out = []; const real = itKillSeq;
      for(let i = 0; i < 6; i++){
        const kf = it.kf; await new Promise(r => { const w = () => kf.busy ? setTimeout(w, 50) : r(); w(); });
        kf.head = true; kf.lastGot = Date.now() - 120000; kf.seqAt = 0; kf.waitUntil = 0; kf.target = kf.seq - 1;
        itKillSeq = async () => kf.seq + 50;
        const t = Date.now(); await itKillPump();
        out.push([kf.head, Math.round(kf.waitUntil - t)]);
      }
      itKillSeq = real; return out; }""")
    ok_w = all(h is False and 0 <= w <= 10050 for h, w in waits) and len({w // 1000 for h, w in waits}) > 1 and any(w > 0 for h, w in waits)
    check(ok_w, f'a catch-up after a gap waits a random 0-10 s first [head, wait ms] {waits}')
    C.click('#intelSwLabel'); C.wait_for_timeout(300)

    # the Intel map: resizes give no ResizeObserver loop error, and the map follows
    C.click('#intelSwLabel'); C.wait_for_function("it.on", timeout=8000); C.wait_for_timeout(1500)
    shown = C.evaluate("() => !!(itm.box && itm.box.isConnected && itm.box.clientWidth > 0)")
    C.evaluate("() => { window.__roErr = 0; }")
    widths = []
    for i in range(6):
        C.set_viewport_size({'width': 1100 if i % 2 == 0 else 1300, 'height': 1000}); C.wait_for_timeout(350)
        widths.append(C.evaluate("() => [Math.round(itm.box.clientWidth), itm.W]"))
    ro = C.evaluate("() => window.__roErr")
    follows = all(abs(w - W) <= 2 for w, W in widths) and len({w for w, W in widths}) > 1
    check(shown and ro == 0 and follows, f'the Intel map: 6 resizes, no "ResizeObserver loop" error ({ro}); the map follows the new size {widths}')
    C.click('#intelSwLabel'); C.wait_for_timeout(300)
    c.close()

    # no navigator.locks: Intel runs as before, with no line
    c2 = ctx_new(nolocks=True)
    D = page(c2, 'D', first=True); E = page(c2, 'E')
    D.click('#intelSwLabel'); D.wait_for_function("it.on", timeout=8000)
    E.click('#intelSwLabel'); E.wait_for_function("it.on", timeout=8000); E.wait_for_timeout(500)
    d, e = st(D), st(E)
    check(d['on'] and e['on'] and not d['other'] and not e['other'] and 'another tab' not in d['notes'] + e['notes'],
          f'no navigator.locks: Intel runs in each tab as before, with no line {d["on"]} {e["on"]} {d["notes"]!r}')
    c2.close()

    # 390 px: the button's size, no sideways scroll
    c3 = ctx_new(w=390)
    F = page(c3, 'F', first=True); G = page(c3, 'G')
    F.click('#intelSwLabel'); F.wait_for_function("it.on", timeout=8000); G.wait_for_timeout(800)
    g = st(G)
    check(g['other'] and g['moveH'] >= 44 and g['sw'] <= g['vw'], f'390 px: Move Intel here {g["moveH"]:.0f} px tall, no sideways scroll ({g["sw"]} <= {g["vw"]})')
    c3.close()

    check(not errs, f'no page errors {errs[:3]}')
    b.close()

print(f'FAILURES: {fails}')
