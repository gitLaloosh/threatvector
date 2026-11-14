"""Tag-only Intel lines reach Near You (build queue 045, the Bubble bug: the owner, "bubbles tag doesn't show up in near you list, only in
feed"; at the build review "yes it gets its own row", "no - wormhole reports dont need near you rows by themselves.", and the Paths to you
tree "b": Bubble and the short wormhole badge on systems already in it, never as sources).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/tag_only_check.py [index.html]   -> 'FAILURES: N' (must be 0)

Uses intel_check.py's made-up folder, mocks and names (you in 1DQ1-A, alert range 3); every pilot and line is made up. Checks:
  * "<S1> bubbled", "<S2> gate camp", "<S3> ess" (no pilots): each system gets its own Near You row with its tag (Bubble, Camp, ESS),
    "reported by" its reporter, no hostile / neutral word, no amber edge, no analyze icon; the Feed still shows the tags;
  * "<S4> <hostile> sabre" then "<S4> bubbled": the row stays hostile (its word, its count, its amber edge) and gains the Bubble tag;
  * "<S5> clr" then "<S5> bubbled": a tag-only row (the newer word wins);
  * "<S6> wh" (a bare wormhole line): no Near You row;
  * no alert from a tag-only line (it.alerts counts only the hostile one); the profile's count unchanged by them;
  * the map: no ring for a tag-only system (not in itm.rep), S4 hostile;
  * the Paths to you tree: S4 a source with its Bubble tag in the tree, the tag-only systems never sources; the short WH badge on a
    system with a wormhole report (itPtTagsHtml);
  * S4's hostile report older than "forget reports after", its bubble still fresh: the row turns tag-only (no word), no ring, no source;
  * mutants, each must fail: the old early return; an alert from a tag line; a tag changing the row's word; a ring for a tag-only
    system; no demotion;
  * no page errors.
v2026.11.12.5 fails (no tag-only rows).
"""
import sys, os, json, time, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
_src = open(os.path.join(HERE, 'intel_check.py'), encoding='utf-8').read()
_src = _src[:_src.index('with sync_playwright() as p:')]
NS = {'__file__': os.path.join(HERE, 'intel_check.py'), '__name__': 'intel_check_prefix'}
exec(compile(_src, 'intel_check.py (first part)', 'exec'), NS)
globals().update({k: v for k, v in NS.items() if not k.startswith('__') and k not in ('check', 'fails')})
from playwright.sync_api import sync_playwright
check = NS['check']
PAGE = open(HTML, encoding='utf-8').read()

HOME = SYSID['1DQ1-A']
D0 = bfs(HOME)
near = sorted((s for s, v in D0.items() if 1 <= v <= 3), key=lambda s: (D0[s], s))
HOST = M.PILOTS[M.pick(98000003, 0)][0]

def start(b, html, errs):
    ctx = b.new_context(bypass_csp=True, viewport={'width': 1440, 'height': 1000})
    ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e))))
    ctx.add_init_script(FS); route(ctx)
    pg = ctx.new_page(); pg.goto('file://' + html)
    pg.evaluate("(s) => { localStorage.setItem('dscanSide', JSON.stringify(s)); localStorage.setItem('dscanIntel', JSON.stringify({channels: ['region.intel'], me: 95000001, range: 3, sound: true, notify: true, forget: 15})); }", SIDE)
    pg.reload(); pg.wait_for_timeout(400)
    setup_logs(pg); pg.eval_on_selector('#tabBtnIntel', 'b => b.click()'); pg.click('[data-it-act="folder"]'); pg.wait_for_timeout(300); pg.click('#intelSwLabel'); tick(pg)
    return ctx, pg

ROWS = """() => Object.fromEntries([...document.querySelectorAll('#itNearList > .it-nb')].map(r => [r.dataset.itSys, {
  tags: [...r.querySelectorAll('.tg .it-gtag, .tg .it-ess')].map(x => x.textContent.trim()), word: ((r.querySelector('.wl .st b') || {}).textContent || ''),
  who: ((r.querySelector('.wl .who') || {}).textContent || '').trim(), alert: r.classList.contains('alert'), an: !!r.querySelector('.it-an, [data-it-an]')}]))"""

def cases(b, html):
    out, errs = [], []
    ctx, pg = start(b, html, errs)
    if not pg.evaluate("typeof itNearAdd === 'function'"): out.append('no Intel'); ctx.close(); return out, errs
    taken = set(pg.evaluate("[...it.near.keys()]"))   # intel_check's own lines already report some systems
    S1, S2, S3, S4, S5, S6 = [x for x in near if x not in taken][:6]
    h0 = pg.evaluate("itNearSum().h")
    t = time.time()
    W(pg, F_INTEL, line(t, 'Gate Watcher', f'{SYSNAME[S1]} bubbled') + line(t + 1, 'Gate Watcher', f'{SYSNAME[S2]} gate camp')
      + line(t + 2, 'Scout Alt', f'{SYSNAME[S3]} ess') + line(t + 3, 'Scout Alt', f'{SYSNAME[S4]} {HOST} sabre')
      + line(t + 4, 'Scout Alt', f'{SYSNAME[S5]} clr') + line(t + 5, 'Gate Watcher', f'{SYSNAME[S6]} wh'))
    tick(pg, 3200)
    a0 = pg.evaluate("(() => { it.alerted.clear(); return it.alerts || 0; })()")   # past the 30 s gap: a tag line about the hostile system must still not alert
    W(pg, F_INTEL, line(t + 6, 'Gate Watcher', f'{SYSNAME[S4]} bubbled') + line(t + 7, 'Gate Watcher', f'{SYSNAME[S5]} bubbled'))
    tick(pg, 3200)
    a1 = pg.evaluate("it.alerts || 0")
    R = pg.evaluate(ROWS)
    for s, tag, who in ((S1, 'Bubble', 'Gate Watcher'), (S2, 'Camp', 'Gate Watcher'), (S3, 'ESS', 'Scout Alt'), (S5, 'Bubble', 'Gate Watcher')):
        r = R.get(str(s))
        if not r: out.append(f'{SYSNAME[s]}: no Near You row (a tag-only line)'); continue
        if tag not in r['tags'] or r['word'] or r['alert'] or r['an'] or f'reported by {who}' not in r['who']:
            out.append(f'{SYSNAME[s]}: tags {r["tags"]}, word {r["word"]!r}, amber {r["alert"]}, analyze {r["an"]}, {r["who"]!r} (want {tag}, no word, no edge, no icon, reported by {who})')
    r4 = R.get(str(S4))
    if not r4 or 'Bubble' not in r4['tags'] or 'hostile' not in r4['word'] or not r4['alert']: out.append(f'{SYSNAME[S4]}: {r4} (want still hostile, its amber edge, plus Bubble)')
    if str(S6) in R: out.append(f'{SYSNAME[S6]}: a bare wormhole line made a Near You row')
    if a0 < 1 or a1 != a0: out.append(f'alerts: {a0} after the hostile line, {a1} after two tag lines (want the same)')
    fd = pg.evaluate("() => [...document.querySelectorAll('#itFeedList .it-fd')].filter(r => r.querySelector('.it-bub')).length")
    if fd < 3: out.append(f'the Feed: {fd} rows with a Bubble tag (want 3)')
    M2 = pg.evaluate("""(ids) => { itMapRefresh(true); const g = itGraphGet(); const rep = ids.map(id => { const r = itm.rep.get(g.at.get(id)); return r ? r.side : null; });
      itMapFilterSet('paths'); itMapRefresh(true); const src = itPtSources().map(i => g.ids[i]);
      const node = document.querySelector(`[data-pt="${g.at.get(ids[3])}"]`), ntags = node ? [...node.querySelectorAll('.pt-tags > *')].map(x => x.textContent) : null;
      const wh = itPtTagsHtml(undefined, Date.now(), ids[5]), sum = itNearSum().h;
      itMapFilterSet('sec'); return {rep, src, ntags, wh, sum}; }""", [S1, S2, S3, S4, S5, S6])
    if M2['rep'] != [None, None, None, 'hostile', None, None]: out.append(f'the map\'s reports: {M2["rep"]} (want only {SYSNAME[S4]}, hostile)')
    if S4 not in M2['src'] or any(s in M2['src'] for s in (S1, S2, S3, S5)): out.append(f'Paths to you sources: {[SYSNAME.get(x, x) for x in M2["src"]]} (want {SYSNAME[S4]}, no tag-only system)')
    if not M2['ntags'] or 'Bubble' not in M2['ntags']: out.append(f'the tree: {SYSNAME[S4]}\'s tags {M2["ntags"]} (want Bubble among them)')
    if '>WH<' not in M2['wh']: out.append(f'the tree: the short wormhole badge for {SYSNAME[S6]}: {M2["wh"][:120]!r}')
    if M2['sum'] - h0 != 1: out.append(f'the profile\'s count: {h0} before, {M2["sum"]} after (want one more: the hostile only)')
    # S4's hostile report past "forget reports after", its bubble still fresh: tag-only from then on
    D = pg.evaluate("""(id) => { const st = it.near.get(id), back = (it.set.forget + 1) * 60000;
      st.rt -= back; for(const k of ['pilots', 'ships', 'pairs']) if(Array.isArray(st[k])) st[k].forEach(x => x.t -= back); itRenderLists(); itMapRefresh(true);
      const g = itGraphGet(); itMapFilterSet('paths'); itMapRefresh(true); const src = itPtSources().map(i => g.ids[i]); itMapFilterSet('sec');
      return {kind: st.kind, ring: itm.rep.has(g.at.get(id)), src}; }""", S4)
    R2 = pg.evaluate(ROWS).get(str(S4))
    if D['kind'] != 'tag' or D['ring'] or S4 in D['src'] or not R2 or R2['word'] or 'Bubble' not in R2['tags']: out.append(f'{SYSNAME[S4]} after its hostiles expired: {D}, row {R2} (want tag-only: Bubble, no word, no ring, no source)')
    ctx.close()
    return out, errs

MUTANTS = [
    ('the old early return', "(e.kind === 'info' && !itTagOnly(e))) return;", "e.kind === 'info') return;"),
    ('an alert from a tag line', "if(!tag && !e.history && !it.replay) itAlert(st, e);", "if(!e.history && !it.replay) itAlert(st, e);"),
    ('a tag changing the row\'s word', "if(tag && prev.kind !== 'tag' && st.rt !== undefined && st.rt >= keep){ st.kind = prev.kind; st.who = prev.who; }", ""),
    ('a ring for a tag-only system', "if(st.t < keep || itNearDemote(st, keep).kind === 'tag') continue;", "if(st.t < keep) continue;"),
    ('no demotion', "if(st.kind !== 'tag' && st.kind !== 'clear' && st.rt !== undefined && st.rt < keep && st.t >= keep)", "if(false)"),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out, errs = cases(b, HTML)
    for o in out: check(False, o)
    check(not out, 'tag-only lines in Near You, the map and the tree')
    check(not errs, f'no page errors {errs[:3]}')
    for name, old, new in MUTANTS:
        if PAGE.count(old) != 1: check(False, f'mutant "{name}": its line isn\'t in the page once'); continue
        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8', dir=os.path.dirname(HTML)) as f:
            f.write(PAGE.replace(old, new)); mp = f.name
        try:
            mo, me = cases(b, mp)
            check(bool(mo) or bool(me), f'mutant "{name}" fails ({(mo or me or ["nothing"])[0][:90]})')
        finally: os.unlink(mp)
    b.close()
print('FAILURES:', NS['fails'])
sys.exit(1 if NS['fails'] else 0)
