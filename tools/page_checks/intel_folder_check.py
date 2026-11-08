"""Intel: the chat-logs folder after a reload (v2026.11.08.2, build queue 025; Project doc roadmap/intel-folder-permission-plan.md).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/intel_folder_check.py [index.html]   -> 'FAILURES: N' (must be 0)

Chrome 122+ asks again for a folder kept from an earlier visit ("Allow this time" / "Allow on every visit" / "Don't allow"), may take a
one-time grant back while the tab is in the background, and asks only from a click. The real page with intel_check.py's made-up Chatlogs
folder, whose permission answers are switched here (queryPermission / requestPermission: prompt, granted, denied; reading can be made to
throw NotAllowedError), and a stand-in for Intel's IndexedDB store so a reload restores the folder as the browser does (the stand-in's own flags are kept in
window.name, which survives a reload: its storage flags didn't always, here). Checks:
  * chosen: the folder read, both characters listed, nothing waiting;
  * reload, "prompt": step 1 "Needs your OK this visit" with Allow reading, Change… and the one short line; steps 2 and 3 "Waiting for
    the folder (1)"; never "No Local log"; Allow reading asks from the click itself (the page's activation is live) and then lists the
    characters; reload with "granted": nothing asked, the characters there;
  * reload, "denied": the blocked line and Change…, no Allow reading;
  * read with no Local log: the real "No Local log in this folder from the last 2 days" text, only then;
  * Intel off, the setup card shown: a Local log added after load is found when the tab is shown again, and within one look-again
    (15 s); while the tab is hidden nothing is read or drawn; with nothing new, nothing is redrawn;
  * Intel on and the permission taken back: INTEL-02 with Allow reading in the Intel card, the profile mark "not working"; Allow
    reading brings it back; reading that starts throwing NotAllowedError mid-run does the same;
  * 390 px: Allow reading at least 44 px tall, no sideways scroll; no page errors.
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

# the folder's answers, switched by the check; and Intel's IndexedDB store, kept across a reload ('dir' = this page's stand-in folder)
EXTRA = r"""(() => {
  __fs.asked = []; __fs.answer = null; __fs.block = false; __fs.reads = 0;
  const nm = () => { try{ return JSON.parse(window.name || '{}'); }catch(e){ return {}; } }, nmSet = (k, v) => { const o = nm(); o[k] = v; window.name = JSON.stringify(o); };
  window.__fsNm = nmSet;
  if(nm().perm) __fs.perm = nm().perm;
  const real = window.indexedDB, kv = new Map();
  const req = (v) => { const r = {result: v}; setTimeout(() => r.onsuccess && r.onsuccess()); return r; };
  const db = {objectStoreNames: {contains: () => true}, createObjectStore(){},
    transaction(){ return {objectStore(){ return {
      get(k){ if(k !== 'dir') return req(kv.get(k)); const r = {}; window.__fsDirP.then((d) => { r.result = nm().saved ? d : undefined; r.onsuccess && r.onsuccess(); }); return r; },
      put(v, k){ if(k === 'dir') nmSet('saved', 1); else kv.set(k, v); return req(undefined); }}; }}; }};
  const fake = {open(name, v){ if(name !== 'eta-intel') return real.open(name, v); const r = {}; setTimeout(() => { r.result = db; r.onsuccess && r.onsuccess(); }); return r; },
    deleteDatabase: (n) => real.deleteDatabase(n)};
  Object.defineProperty(window, 'indexedDB', {value: fake, configurable: true});   // a read-only attribute: replaced, not assigned
  const pick = window.showDirectoryPicker;
  window.__fsDirP = !pick ? Promise.resolve(undefined) : pick().then((d) => {
    window.__fsDir = d;
    d.queryPermission = async () => __fs.perm;
    d.requestPermission = async () => { __fs.asked.push(navigator.userActivation ? navigator.userActivation.isActive : null); if(__fs.answer) __fs.perm = __fs.answer; return __fs.perm; };
    const e0 = d.entries;
    d.entries = function(){ __fs.reads++; if(__fs.block || __fs.perm !== 'granted') throw new DOMException('not allowed', 'NotAllowedError'); return e0.call(this); };
    return d;   // the restored folder waits for this (no race with the page's first read)
  });
})();"""
ST = """() => { const q = (s) => document.querySelector(s), box = [...document.querySelectorAll('#intelPanel .it-setup .it-box')];
  const t = (i) => box[i] ? box[i].textContent.replace(/\\s+/g, ' ').trim() : '';
  const al = q('#intelPanel [data-it-act="allow"]');
  return {b1: t(0), b2: t(1), b3: t(2), wait2: box[1] ? box[1].classList.contains('it-wait') : null, allow: !!al, allowH: al ? al.getBoundingClientRect().height : 0,
    me: [...document.querySelectorAll('[data-it-me]')].map(c => c.closest('label').textContent.trim()), perm: it.perm, read: it.read, err: it.err,
    notes: (q('#itNotes') || {}).textContent || '', noteAllow: !!q('#itNotes [data-it-act="allow"]'), mark: (q('#profile') || {dataset: {}}).dataset.s,
    sw: document.documentElement.scrollWidth, vw: innerWidth}; }"""
DRAWS = "() => { window.__draws = 0; new MutationObserver(() => window.__draws++).observe(document.getElementById('intelPanel'), {childList: true, subtree: true}); }"

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    errs = []
    def ctx_new(w=1440):
        c = b.new_context(bypass_csp=True, viewport={'width': w, 'height': 1000})
        c.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
        c.add_init_script(FS); c.add_init_script(EXTRA); route(c); return c
    def perm(pg, v, answer=None):
        pg.evaluate("([v, a]) => { __fsNm('perm', v); __fs.perm = v; __fs.answer = a; }", [v, answer])
    def reload(pg, v):
        pg.evaluate("(v) => __fsNm('perm', v)", v); pg.reload(); pg.wait_for_function("typeof it !== 'undefined' && it.loaded"); pg.wait_for_timeout(300)
        setup_logs(pg); pg.click('#tabBtnIntel'); pg.wait_for_timeout(300)
        # the stand-in folder lives in the page, so its files are written after the page's own first read: look again (as on focus)
        pg.evaluate("() => window.dispatchEvent(new Event('focus'))"); pg.wait_for_timeout(500)
    c = ctx_new(); pg = c.new_page(); pg.goto('file://' + HTML)
    pg.evaluate("(s) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.removeItem('dscanIntel'); }", SIDE); pg.reload(); pg.wait_for_timeout(500)
    setup_logs(pg); pg.click('#tabBtnIntel'); pg.wait_for_timeout(200)
    # ---- chosen ----
    pg.click('#intelPanel [data-it-act="folder"]'); pg.wait_for_timeout(500)
    s = pg.evaluate(ST)
    check(s['perm'] == 'granted' and s['read'] and s['me'] == ['Your Alt 8WA-Z6', 'Your Main 1DQ1-A'] and not s['wait2'] and not s['allow'],
          f"chosen: the folder read, both characters listed, nothing waiting {s['me']}")
    pg.check('[data-it-chan="region.intel"]'); pg.check(f'[data-it-me="{MAIN}"]'); pg.wait_for_timeout(100)
    # ---- reload with "prompt" (Allow this time on the last visit) ----
    reload(pg, 'prompt'); s = pg.evaluate(ST)
    check(s['perm'] == 'prompt' and 'Needs your OK this visit.' in s['b1'] and s['allow'] and 'Change…' in s['b1'] and 'Pick Allow on every visit to skip this' in s['b1'],
          f"reload, prompt: step 1 asks for your OK with Allow reading, Change… and its line ({s['b1'][:90]!r})")
    check(s['wait2'] and 'Waiting for the folder (1).' in s['b2'] and 'Waiting for the folder (1).' in s['b3'] and 'No Local log' not in s['b3'] and not s['me'],
          f"reload, prompt: steps 2 and 3 wait for the folder, no \"No Local log\" ({s['b3'][:70]!r})")
    n0 = pg.evaluate("__fs.asked.length")
    check(n0 == 0, f'reload, prompt: nothing asked without a click ({n0})')
    pg.evaluate("__fs.answer = 'granted'"); pg.click('#intelPanel .it-setup [data-it-act="allow"]'); pg.wait_for_timeout(500)
    s = pg.evaluate(ST); asked = pg.evaluate("__fs.asked")
    check(asked == [True] and s['perm'] == 'granted' and s['me'] == ['Your Alt 8WA-Z6', 'Your Main 1DQ1-A'] and not s['allow'] and not s['wait2'],
          f"Allow reading: asked from the click (activation {asked}), then the characters listed")
    reload(pg, 'granted'); s = pg.evaluate(ST)
    check(pg.evaluate("__fs.asked.length") == 0 and s['me'] == ['Your Alt 8WA-Z6', 'Your Main 1DQ1-A'] and not s['allow'],
          'reload, granted (Allow on every visit): nothing asked, the characters there')
    # ---- denied ----
    reload(pg, 'denied'); s = pg.evaluate(ST)
    check('The browser is blocking this folder for this site.' in s['b1'] and 'Change…' in s['b1'] and not s['allow'] and 'No Local log' not in s['b3'],
          f"reload, denied: the blocked line and Change…, no Allow reading ({s['b1'][:80]!r}; {pg.evaluate("[window.name, !!window.__fsDir, it.perm, it.loaded]")})")
    # ---- read, no Local log ----
    perm(pg, 'granted'); pg.evaluate("() => { for(const k of Object.keys(__fs.files)) if(/^Local_/.test(k)) delete __fs.files[k]; }")
    pg.evaluate("async () => { it.chars = new Map(); await itScan(); itRender(true); }"); pg.wait_for_timeout(200)
    s = pg.evaluate(ST)
    check('No Local log in this folder from the last 2 days.' in s['b3'] and 'Log Chat to File' in s['b3'], f"read with no Local log: the real \"nothing found\" ({s['b3'][:90]!r})")
    # ---- Intel off, the setup card shown: look again ----
    reload(pg, 'granted'); pg.evaluate("() => { for(const k of Object.keys(__fs.files)) if(/^Local_/.test(k)) delete __fs.files[k]; }")
    pg.evaluate("async () => { it.chars = new Map(); await itScan(); itRender(true); }"); pg.wait_for_timeout(200)
    pg.evaluate(DRAWS)
    pg.evaluate("() => { Object.defineProperty(document, 'hidden', {configurable: true, get: () => true}); __fs.reads = 0; }")
    W(pg, F_LOCAL_MAIN, header('Local', 'Your Main', NOW - 7200) + line(NOW - 60, 'EVE System', 'Channel changed to Local : 1DQ1-A*'))
    pg.wait_for_timeout(16500)
    hid = pg.evaluate("() => [__fs.reads, window.__draws, [...document.querySelectorAll('[data-it-me]')].length]")
    check(hid == [0, 0, 0], f'hidden: nothing read or drawn on the look-again timer {hid}')
    pg.evaluate("() => { delete document.hidden; document.dispatchEvent(new Event('visibilitychange')); }"); pg.wait_for_timeout(600)
    s = pg.evaluate(ST)
    check(s['me'] == ['Your Main 1DQ1-A'], f"shown again: the Local log added meanwhile is found {s['me']}")
    W(pg, F_LOCAL_ALT, header('Local', 'Your Alt', NOW - 100) + line(NOW - 90, 'EVE System', 'Channel changed to Local : 8WA-Z6*'))
    pg.wait_for_timeout(16500); s = pg.evaluate(ST)
    check(s['me'] == ['Your Alt 8WA-Z6', 'Your Main 1DQ1-A'], f"setup card shown: a new Local log found within one look-again (15 s) {s['me']}")
    # itBuildAt builds the card's text; with nothing new the look-again doesn't even build it (the page's own compare would hide a redraw)
    pg.evaluate("() => { window.__builds = 0; const f = window.itBuildAt; window.itBuildAt = function(){ window.__builds++; return f.apply(this, arguments); }; }")
    d0 = pg.evaluate("window.__draws"); pg.wait_for_timeout(16500); d1 = pg.evaluate("[window.__draws, window.__builds]")
    check(d1 == [d0, 0], f'nothing new: the look-again neither redraws nor rebuilds the card ({d0} -> {d1})')
    # ---- Intel on, the permission taken back ----
    pg.click('#intelSwLabel'); pg.wait_for_timeout(2600)
    on = pg.evaluate("it.on")
    perm(pg, 'prompt'); pg.evaluate("() => window.dispatchEvent(new Event('focus'))"); pg.wait_for_timeout(600)
    s = pg.evaluate(ST)
    check(on and '(INTEL-02)' in s['err'] and s['noteAllow'] and s['mark'] == 'broken', f"Intel on, the permission taken back (seen on focus): INTEL-02 with Allow reading, the mark not working ({s['err'][:70]!r}, {s['mark']})")
    pg.evaluate("__fs.answer = 'granted'"); pg.click('#itNotes [data-it-act="allow"]'); pg.wait_for_timeout(2800)
    s = pg.evaluate(ST)
    check(not s['err'] and s['mark'] != 'broken' and pg.evaluate("__fs.asked.slice(-1)[0]") is True, f"Allow reading in the Intel card: reading again, the error gone ({s['mark']})")
    pg.evaluate("() => { __fs.block = true; it.lastScan = 0; }")
    for _ in range(12):
        pg.wait_for_timeout(500)
        if pg.evaluate("it.err"): break
    s = pg.evaluate(ST)
    check('(INTEL-02)' in s['err'] and s['perm'] == 'prompt' and s['noteAllow'], f"reading starts failing mid-run (NotAllowedError): INTEL-02 with Allow reading ({s['err'][:60]!r})")
    pg.evaluate("() => { __fs.block = false; }")
    c.close()
    # ---- phone ----
    c = ctx_new(390); pg = c.new_page(); pg.goto('file://' + HTML); pg.wait_for_timeout(400)
    setup_logs(pg); pg.click('#tabBtnIntel'); pg.wait_for_timeout(200); pg.click('#intelPanel [data-it-act="folder"]')
    pg.wait_for_function("it.perm === 'granted' && JSON.parse(window.name || '{}').saved === 1")
    reload(pg, 'prompt'); s = pg.evaluate(ST)
    check(s['allow'] and s['allowH'] >= 44 and s['sw'] <= s['vw'], f"390 px: Allow reading {s['allowH']:.0f} px tall, no sideways scroll ({s['perm']}, {s['b1'][:60]!r})")
    c.close()
    check(not errs, f'no page errors {errs[:3]}')
    b.close()
print(f'\nFAILURES: {fails}')
sys.exit(1 if fails else 0)
