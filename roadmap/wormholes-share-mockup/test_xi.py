"""Checks for the Wormholes list Export / Import mockup. python3 -I test_xi.py <mockup.html> <shots dir>
Playwright (Chromium), bypass_csp (the mockup replaces the page's CSP), each case on a fresh page, 1440 and 390 px."""
import json, os, sys
from playwright.sync_api import sync_playwright
HTML, OUT = os.path.abspath(sys.argv[1]), sys.argv[2]
os.makedirs(OUT, exist_ok=True)
ok = bad = 0
def check(name, cond, info=''):
    global ok, bad
    if cond: ok += 1
    else: bad += 1; print('FAIL', name, info)
def page_for(b, w, h):
    ctx = b.new_context(viewport={'width': w, 'height': h}, bypass_csp=True)
    p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto('file://' + HTML); p.wait_for_function('window.__MKREADY === true || !!window.__MKERR', timeout=30000)
    p.wait_for_function('typeof itWhStore === "function" && it.names && itGraphGet().at.size > 0', timeout=30000)
    return ctx, p, errs
def open_list(p):
    p.click('[data-mk="open"]'); p.wait_for_selector('.it-whp:not([hidden])', timeout=5000)
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for (W, H, tag) in [(1440, 900, 'w'), (390, 844, 'p')]:
        # --- export
        ctx, p, errs = page_for(b, W, H)
        open_list(p)
        p.click('[data-it-whxb="exp"]')
        exp = p.eval_on_selector('#itWhExp textarea', 'e => e.value')
        sel = p.evaluate('() => { const t = document.activeElement; return t && t.matches("#itWhExp textarea") && t.selectionStart === 0 && t.selectionEnd === t.value.length; }')
        check(f'{tag} export selected', sel)
        o = json.loads(exp)
        check(f'{tag} export shape', o['tv'] == 'wormholes' and o['v'] == 1 and len(o['sys']) == 4, len(o['sys']))
        for nm in ['Mk Raider One', 'Mk Gate Watcher', 'Mk Scout Alt', 'MKRC', 'Raider', 'Watcher']:
            check(f'{tag} no name {nm}', nm not in exp)
        e4 = next(x for x in o['sys'] if x['id'] == 30000796)
        line = next(r['raw'] for r in e4['raws'] if 'XRT' in r['raw'])
        check(f'{tag} redacted line', line == 'EUU-4N wh XRT-331 <a pilot> Sabre <a pilot>', line)
        cj = next(x for x in o['sys'] if x['id'] == 30000772)
        check(f'{tag} hand line kind', any(r['k'] == 'hand' for r in cj['raws']) and not any('who' in r for r in cj['raws']))
        check(f'{tag} rzl line kept', any('rzl-429 z971 class 1-3 medium size less then 1 day less then 50% mass' in r['raw'] for r in cj['raws']), [r['raw'] for r in cj['raws']])
        check(f'{tag} chevron turned', p.get_attribute('[data-it-whxb="exp"]', 'aria-expanded') == 'true')
        exp2 = p.evaluate('() => { const o = itWhExportObj(); o.made = 0; return JSON.stringify(o); }'); exp3 = p.evaluate('() => { const o = itWhExportObj(); o.made = 0; return JSON.stringify(o); }')
        check(f'{tag} export stable', exp2 == exp3)
        p.click('[data-it-whcopy]'); p.wait_for_timeout(200)
        check(f'{tag} copy feedback', p.inner_text('[data-it-whcopy]') == 'Copied!' or 'Ctrl+C' in p.inner_text('#itWhExp .it-whp-bs'))
        p.screenshot(path=f'{OUT}/{tag}_export.png')
        # opening Import closes Export
        p.click('[data-it-whxb="imp"]')
        check(f'{tag} one box', p.is_hidden('#itWhExp') and p.is_visible('#itWhImp'))
        check(f'{tag} no sideways scroll', p.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'))
        check(f'{tag} no errors (export)', not errs, errs)
        ctx.close()
        # --- import the friend's export
        ctx, p, errs = page_for(b, W, H)
        p.click('[data-mk="friend"]'); p.wait_for_timeout(600)
        p.click('[data-it-whimp]'); p.wait_for_selector('.it-whp-prev:not([hidden])', timeout=3000)
        pv = p.inner_text('.it-whp-prev')
        check(f'{tag} preview counts', 'Adds 2 systems' in pv and 'adds to 2' in pv and 'already have 1' in pv, pv)
        check(f'{tag} preview skips', '1 older than your 24 h' in pv and '2 removed by you' in pv and '1 not a system on the map' in pv, pv)
        check(f'{tag} preview note', 'kept yours for 1' in pv, pv)
        before = p.evaluate('() => JSON.stringify(itWhStore().rep)')
        p.screenshot(path=f'{OUT}/{tag}_preview.png')
        p.click('[data-it-whcancel]')
        check(f'{tag} cancel changes nothing', p.evaluate('() => JSON.stringify(itWhStore().rep)') == before)
        p.click('[data-it-whimp]'); p.click('[data-it-whadd]'); p.wait_for_timeout(200)
        st = p.evaluate('() => itWhStore()')
        rep = st['rep']
        cj = rep['30000772']; rz = next(s for s in cj['sigs'] if s['sig'] == 'RZL-429')
        check(f'{tag} yours kept', rz.get('info', {}).get('mass') == 'stable', rz)
        check(f'{tag} note', (rz.get('note') or {}).get('v') == 'critical', rz)
        texts = [r['raw'] for r in cj['raws']]
        check(f'{tag} one line per report', len([t for t in texts if 'MKV' in t]) == 1 and len([t for t in texts if 'rzl-429 z971' in t]) == 1, texts)
        mkv = next(r for r in cj['raws'] if 'MKV' in r['raw'])
        check(f'{tag} repeat count max', mkv.get('n') == 2 and mkv.get('who') == 'Mk Gate Watcher', mkv)
        rr = rep['30000780']
        check(f'{tag} part completes', [s['sig'] for s in rr['sigs']] == ['QDX-581'] and rr['sigs'][0]['type'] == 'N110', rr['sigs'])
        eu = rep['30000796']
        check(f'{tag} removed ID stays removed', not any(s['sig'] == 'KLM-204' for s in eu['sigs']), eu['sigs'])
        check(f'{tag} removed system stays removed', '30000779' not in rep)
        check(f'{tag} new systems', '30000771' in rep and '30000786' in rep and rep['30000771']['who'] == '<a pilot>')
        check(f'{tag} old and unknown skipped', '30000776' not in rep and '31000001' not in rep)
        check(f'{tag} legacy kept', '30000458' in rep)
        check(f'{tag} entry time from newest line', cj['t'] == max(r['t'] for r in cj['raws']))
        # importing the same again changes nothing
        snap = json.dumps(rep, sort_keys=True)
        r2 = p.evaluate('() => { const rd = itWhImportRead(window.__MKfriend()); const r = itWhImportPlan(rd); return {out: r.out.length, same: r.same}; }')
        check(f'{tag} idempotent', r2['out'] == 0, r2)
        p.evaluate('() => itWhImportApply(window.__MKfriend())')
        check(f'{tag} idempotent store', json.dumps(p.evaluate('() => itWhStore().rep'), sort_keys=True) == snap)
        # the list shows the note and the shared line; screenshot
        p.evaluate('() => { itWhRawOpen.add(30000772); itWhListPaint(true); }')
        check(f'{tag} note shown', p.locator('.it-whp-rows .it-signote').count() == 1)
        check(f'{tag} shared line shown', p.locator('.it-whp-raws .it-whp-shared').count() >= 1)
        p.screenshot(path=f'{OUT}/{tag}_after.png')
        check(f'{tag} no sideways scroll 2', p.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'))
        check(f'{tag} no errors (import)', not errs, errs)
        ctx.close()
        # --- bad input
        ctx, p, errs = page_for(b, W, H)
        bads = p.evaluate("""() => ['', 'hello', '{"tv":"x","v":1}', '{"tv":"wormholes","v":2,"sys":[]}', 'x'.repeat(300000),
          JSON.stringify({tv: 'wormholes', v: 1, sys: [{id: 30000772, name: 'Jita', t: Date.now(), sigs: [], raws: []}]}),
          JSON.stringify({tv: 'wormholes', v: 1, sys: [{id: 30000771, name: '8G-2FP', t: Date.now() - 3 * 864e5, sigs: [], raws: [{t: Date.now() - 3 * 864e5, k: 'intel', raw: 'x'}]}]})
        ].map(t => { const r = itWhImportRead(t); if(r.err) return 'err'; const pl = itWhImportPlan(r); return pl.out.length ? 'ADDED' : 'none'; })""")
        check(f'{tag} bad inputs refused', all(x in ('err', 'none') for x in bads), bads)
        x = p.evaluate("""() => { const t = JSON.stringify({tv: 'wormholes', v: 1, sys: [{id: 30000771, name: '8G-2FP', t: Date.now() - 60000, sigs: [{sig: 'bad!', t: Date.now()}, {sig: 'ABC-123', type: 'ZZZZ', t: Date.now()}], raws: [{t: Date.now() - 60000, k: 'intel', raw: '<img src=x onerror=alert(1)> 8G-2FP wh'}]}]});
          const r = itWhImportApply(t); itWhListOpen(true); itWhListPaint(true); return {sigs: (itWhStore().rep[30000771] || {}).sigs, img: document.querySelectorAll('.it-whp img').length}; }""")
        check(f'{tag} bad sigs dropped, html inert', x['img'] == 0 and not x['sigs'], x)
        check(f'{tag} no errors (bad)', not errs, errs)
        ctx.close()
    b.close()
print(f'{ok} passed, {bad} failed')
sys.exit(1 if bad else 0)
