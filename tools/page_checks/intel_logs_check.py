"""Intel watches the chat log that is still being written (2026-11-11; the owner: "intel reports are not being read. killmails do show on
the list but not chat log reports").

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/intel_logs_check.py [index.html]   -> 'FAILURES: N' (must be 0)

The cause: two of the owner's characters had a log of the same intel channel; his alt's started hours later and then went quiet (the alt
logged off), while his main's older log kept logging. The page watched the log that STARTED last (your own only if it started within an
hour of that), so it read the quiet one: "no lines yet". It now watches the log WRITTEN to last (its last-modified time), yours while it's
being written, and on moving to another log skips what the old one already gave. intel_check.py's made-up Chatlogs folder (its stand-in
keeps each file's last write time), made-up characters and lines only. Checks:
  * the owner's case: your main's log (started first, being written) and your alt's (started over an hour later, quiet for 10 minutes):
    the main's is watched, and its new line is read (a Feed row, a live report, not history), the status line no longer "no lines yet";
  * your main's log goes quiet while the alt's is written: the page moves to the alt's; a line both logs carry (the same time, who and
    text) is read once, the alt's new line once, as a live report;
  * mutants: the old pick (the log that started last) and the move without skipping what was read each fail;
  * no page errors.
"""
import sys, os, re, json, time, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SRC = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
exec(compile(SRC[:SRC.index('with sync_playwright() as p:')], 'intel_check', 'exec'))   # its folder stand-in, logs, ESI and R2Z2 routes

fails = 0
def check(ok, msg):
    global fails
    print(('ok   ' if ok else 'FAIL ') + msg)
    if not ok: fails += 1

PAGE = open(HTML, encoding='utf-8').read()
F_ALT_INTEL = fname('region.intel', NOW - 600, ALT)   # your alt joined the channel over an hour after your main (NOW - 7000)
WATCHED = "() => [...it.files.values()].map(f => f.name)"
ROWS = "(raw) => it.feed.filter(e => `${e.who} > ${e.raw}` === raw).map(e => !!e.history)"

def cases(html_path, out):
    c = b.new_context(bypass_csp=True, viewport={'width': 1440, 'height': 1000})
    c.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    c.add_init_script(FS); route(c)
    pg = c.new_page(); pg.goto('file://' + html_path)
    pg.evaluate("(s) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({channels: ['region.intel'], me: %d})); }" % MAIN, SIDE)
    pg.reload(); pg.wait_for_function("typeof it !== 'undefined' && it.loaded", timeout=10000); pg.wait_for_timeout(300)
    setup_logs(pg)
    W(pg, F_ALT_INTEL, header('region.intel', 'Your Alt', NOW - 600) + line(NOW - 590, 'Gate Watcher', 'E-VKJV Seren Ketter sabre'))
    pg.evaluate("(n) => { __fs.files[n].mtime = Date.now() - 600000; }", F_ALT_INTEL)   # the alt's log: quiet for 10 minutes
    pg.click('#tabBtnIntel'); pg.wait_for_timeout(200)
    pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(500)
    pg.click('#intelSwLabel'); tick(pg)
    # the owner's case: the main's log keeps logging
    t0 = int(time.time()); new1 = 'Lookout > 4X0-8B Rando Thirdparty'
    W(pg, F_INTEL, line(t0, 'Lookout', '4X0-8B Rando Thirdparty'))
    pg.evaluate("() => { it.lastScan = 0; }"); tick(pg)
    w, r1, stt = pg.evaluate(WATCHED), pg.evaluate(ROWS, new1), pg.inner_text('#intelPanel [data-it-status]')
    if w != [F_INTEL]: out.append(f'watched {w} (want the main\'s log)')
    if r1 != [False]: out.append(f'the main\'s new line {r1} (want one live row)')
    if 'no lines yet' in stt: out.append('the status line still says no lines yet')
    # the main's log goes quiet; the alt's is written: a line both carry, then the alt's own
    pg.evaluate("(n) => { __fs.files[n].mtime = Date.now() - 120000; }", F_INTEL)
    t1 = int(time.time()); new2 = 'Lookout > T5ZI-S Seren Ketter sabre'
    W(pg, F_ALT_INTEL, line(t0, 'Lookout', '4X0-8B Rando Thirdparty') + line(t1, 'Lookout', 'T5ZI-S Seren Ketter sabre'))
    pg.evaluate("() => { it.lastScan = 0; }"); tick(pg)
    w, r1, r2 = pg.evaluate(WATCHED), pg.evaluate(ROWS, new1), pg.evaluate(ROWS, new2)
    if w != [F_ALT_INTEL]: out.append(f'after the main went quiet, watched {w} (want the alt\'s log)')
    if r1 != [False]: out.append(f'the line both logs carry: {len(r1)} rows (want 1)')
    if r2 != [False]: out.append(f'the alt\'s new line {r2} (want one live row)')
    c.close()

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    errs = []
    out = []; cases(HTML, out)
    check(not out, f"the owner's case (an alt's later log gone quiet): the log still written is watched and read; the move to the alt's when the main's goes quiet reads the shared line once and the new one live ({out})")
    OLD_PICK = ("""    const L = byChan.get(ch) || [];
    for(const f of L){ try{ f.mod = (await f.handle.getFile()).lastModified || 0; }catch(e){ f.mod = 0; } }
    L.sort((a, b) => b.mod - a.mod || b.start - a.start);
    if(!L.length) continue;
    const top = L[0].mod, cur = it.files.get(ch), here = cur && L.find(f => f.name === cur.name);
    const mine = L.find(f => f.charId === it.set.me && f.mod >= top - IT_LOG_MINE_MS);
    want.set(ch, mine || (here && here.mod >= top - IT_LOG_SAME_MS ? here : L[0]));""",
                """    const L = (byChan.get(ch) || []).sort((a, b) => b.start - a.start);
    const mine = L.find(f => f.charId === it.set.me);
    const f = mine && mine.start >= (L[0] ? L[0].start - 3600000 : 0) ? mine : L[0];
    if(f) want.set(ch, f);""")
    NO_SKIP = ("        if(a) lines = lines.filter(l => l.t > a.t || (l.t === a.t && !a.keys.includes(itLineKey(l))));\n", "\n")
    tmp = tempfile.mkdtemp(prefix='intel_logs_mut_')
    for name_, (a_, b_) in (('the log that started last', OLD_PICK), ('the move without skipping what was read', NO_SKIP)):
        if PAGE.count(a_) != 1: check(False, f'mutant "{name_}": its text is in the page'); continue
        f = os.path.join(tmp, 'index.html'); open(f, 'w', encoding='utf-8').write(PAGE.replace(a_, b_, 1))
        out = []
        try: cases(f, out)
        except Exception as e: out.append(f'error {str(e)[:60]}')
        check(bool(out), f'mutant "{name_}" fails the case ({out[:1]})')
    check(not errs, f'no page errors {errs[:3]}')
    b.close()
print(f'\nFAILURES: {fails}')
sys.exit(1 if fails else 0)
