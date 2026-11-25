"""Checks for the Sov hubs mockup (python3 -I test_hb.py sov_hubs_mockup.html shots/), at 1440 and 390 px."""
import os, sys
from playwright.sync_api import sync_playwright
PAGE = 'file://' + os.path.abspath(sys.argv[1]); SHOTS = sys.argv[2]; os.makedirs(SHOTS, exist_ok=True)
fails, n = [], 0
def ok(c, what):
    global n; n += 1
    if not c: fails.append(what); print('FAIL', what)
# the plan's rule, worked out here apart from the mockup's own __MKhub: any ticked kind; fights starting within fightH (started count),
# hubs whose window is open now or opens within vulnH; your system kept off the list (the page always matches it)
RULE = """(() => { const s = itMapSt().hub, H = MKH, out = [];
  for(let i = 0; i < itGraphGet().ids.length; i++){ if(i === itm.home) continue;
    const f = H.fight.get(i), w = H.win.get(i);
    const a = s.fight && f && f.start - H.at <= s.fightH * 3600000, b = s.vuln && w && w.s - H.at <= s.vulnH * 3600000 && w.e > H.at;
    if(a || b) out.push(i); }
  return out; })()"""
MATCH = "(() => { const mt = itMapMatch(); return mt ? [...mt.list].sort((a, b) => a - b) : null; })()"
ONLY = "(itm.el.querySelector('.it-map-only') || {}).textContent || ''"
ix = lambda pg, name: pg.evaluate(f"itGraphGet().ids.findIndex(id => itSysName(id) === {name!r})")
with sync_playwright() as p:
    for w, h in [(1440, 900), (390, 844)]:
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = b.new_page(viewport={'width': w, 'height': h}, has_touch=w < 600, is_mobile=w < 600); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(PAGE); pg.wait_for_function('window.__MKREADY || window.__MKERR', timeout=60000)
        ok(not pg.evaluate('window.__MKERR'), f'{w}: boot {pg.evaluate("window.__MKERR")}')
        # the filter and its place
        ok(pg.evaluate("IT_MAP_FILTERS.findIndex(f => f.k === 'hub') === IT_MAP_FILTERS.findIndex(f => f.k === 'sov') + 1"), f'{w}: Sov hubs comes right after Sov upgrades')
        ok(pg.evaluate("IT_MAP_FILTERS.find(f => f.k === 'hub').name") == 'Sov hubs' and pg.evaluate("IT_MAP_ONLY.includes('hub')"), f'{w}: an Only filter named Sov hubs')
        ok(pg.evaluate("!!itm.el.querySelector('[data-it-mpn=\"hub\"]')"), f'{w}: it has its settings button')
        ok(pg.evaluate("JSON.stringify(itMapStackBlank().hub)") == '{"fight":true,"fightH":24,"vuln":true,"vulnH":0}', f'{w}: defaults: fights within 24 h, vulnerable now')
        ok(pg.evaluate("itMpShown() && itMp.k === 'hub'"), f'{w}: its settings panel is open')
        ok(pg.evaluate("[...itMp.el.querySelectorAll('[data-mk-hk]')].map(x => x.dataset.mkHk + ':' + x.checked).join()") == 'fight:true,vuln:true', f'{w}: both kinds ticked')
        # the match, by the rule
        m = pg.evaluate(MATCH); r = pg.evaluate(RULE)
        ok(m == r, f'{w}: defaults match the rule worked out apart ({len(m or [])} vs {len(r)})')
        ok(pg.evaluate("itMapMatched(itm.home)"), f'{w}: your system matches')
        rerz, shbf, ubc, msg = ix(pg, 'RERZ-L'), ix(pg, 'SHBF-V'), ix(pg, '0UBC-R'), ix(pg, 'MSG-BZ')
        ok(shbf in (m or []) and ubc in (m or []) and rerz not in (m or []), f'{w}: a started fight and one in 21 h match, one in 30 h does not')
        ok('a sov fight within 24 h (5)' in pg.evaluate(ONLY) and ' ·  · ' not in pg.evaluate(ONLY) and 'ESI ' in pg.evaluate(ONLY), f'{w}: Only line {pg.evaluate(ONLY)!r}')
        # the hover
        t = pg.evaluate(f"__MKtip({shbf})"); ok('under way since' in t and 'score 45 / 55' in t and 'no vulnerability window' in t, f'{w}: a started fight\'s hover {t[:90]!r}')
        t = pg.evaluate(f"__MKtip({ubc})"); ok('starts ' in t and ' EVE (in 21 h' in t and 'Mockup Raiders [MKRD]' in t, f'{w}: a coming fight\'s hover {t[:120]!r}')
        vnow = pg.evaluate("[...MKH.win].find(([i, x]) => x.s <= MKH.at && x.e > MKH.at)[0]")
        ok('left)' in pg.evaluate(f"__MKtip({vnow})") and 'Hub vulnerable' in pg.evaluate(f"__MKtip({vnow})"), f'{w}: a vulnerable hub\'s hover says how long is left')
        vlat = pg.evaluate("[...MKH.win].find(([i, x]) => x.s > MKH.at)[0]")
        ok('opens in' in pg.evaluate(f"__MKtip({vlat})"), f'{w}: a later window\'s hover says when it opens')
        ok(pg.evaluate("__MKtip(itm.home)") == '' or 'Hub' in pg.evaluate("__MKtip(itm.home)") or 'Sov' in pg.evaluate("__MKtip(itm.home)"), f'{w}: your own system\'s hover is the usual')
        # the tags: fights with no report get a labelled tag; reported ones carry it in their label
        ok(ubc in pg.evaluate("itm.labels.map(l => l[0])"), f'{w}: 0UBC-R (no report) is labelled with its tag')
        ok(len(pg.evaluate(f"__MKftag({msg}, 'x')")) == 1 and len(pg.evaluate(f"__MKftag({rerz}, 'x')")) == 0, f'{w}: tags only for fights in the window')
        ok(pg.evaluate(f"__MKftag({shbf}, 'x')[0].t") == 'SOV now', f'{w}: a started fight\'s tag says now')
        ok(pg.evaluate(f"/^SOV \\d\\d:\\d\\d$/.test(__MKftag({msg}, 'x')[0].t)"), f'{w}: a coming fight\'s tag gives its start in EVE time')
        pg.evaluate("itm.box.scrollIntoView({block:'start'})"); pg.wait_for_timeout(250)
        pg.screenshot(path=os.path.join(SHOTS, f'{w}_defaults.png'))
        # the kinds: unticking Vulnerable leaves fights only; the stepper widens the fight window
        pg.click('[data-mk-hk="vuln"]'); pg.wait_for_timeout(150)
        ok(pg.evaluate("itMapSt().hub.vuln") is False and pg.evaluate(MATCH) == pg.evaluate(RULE) and len(pg.evaluate(MATCH)) == 5, f'{w}: Vulnerable unticked: the 5 fights within 24 h')
        pg.evaluate("itMp.el.querySelector('[data-rs=\"mapHubF\"]').scrollIntoView({block:'center'})")
        pg.click('[data-rs="mapHubF"] [data-rs-d="1"]'); pg.wait_for_timeout(100)
        ok(pg.evaluate("itMapSt().hub.fightH") == 25, f'{w}: the fight stepper steps by an hour')
        pg.evaluate("itMapSt().hub.fightH = 48; itMpChanged()")
        ok(len(pg.evaluate(MATCH)) == 6 and rerz in pg.evaluate(MATCH), f'{w}: 48 h takes in the fight in 30 h')
        pg.evaluate("itMapSt().hub.fightH = 0; itMpChanged()")
        ok(pg.evaluate(MATCH) == [shbf], f'{w}: 0 h: only the started fight')
        pg.click('[data-mk-hk="fight"]'); pg.wait_for_timeout(150)
        ok(pg.evaluate(MATCH) == [] and 'no kind ticked' in pg.evaluate(ONLY), f'{w}: nothing ticked: nothing matches, the Only line says so')
        ok(pg.evaluate(f"__MKftag({msg}, 'x').length") == 0, f'{w}: no tags with Fight coming up unticked')
        pg.evaluate("MKH.scene('v4')")
        m4 = pg.evaluate(MATCH); ok(m4 == pg.evaluate(RULE), f'{w}: vulnerable within 4 h matches the rule')
        pg.evaluate("itMapSt().hub.vulnH = 0; itMpChanged()"); m0 = pg.evaluate(MATCH); pg.evaluate("itMapSt().hub.vulnH = 4; itMpChanged()")
        ok(len(m4) > len(m0) and set(m0) <= set(m4), f'{w}: within 4 h takes in more than now ({len(m4)} > {len(m0)})')
        ok(pg.evaluate("[...itMp.el.querySelectorAll('.rs-v')].map(x => x.value).join()") == '24,4', f'{w}: the steppers show 24 and 4')
        pg.evaluate("MKH.scene('vuln')")
        ok(pg.evaluate("itMp.el.querySelector('[data-rs=\"mapHubV\"] .rs-v').value") == 'now', f'{w}: 0 shows as now')
        # no data: nothing but you, said in words
        pg.evaluate("MKH.scene('nodata')")
        ok(pg.evaluate(MATCH) == [] and 'no data yet' in pg.evaluate(ONLY) and pg.evaluate(f"__MKtip({ubc})") == '', f'{w}: no data yet: nothing matches, no hover lines, the Only line says so')
        pg.evaluate("MKH.scene('both')")
        ok(pg.evaluate(MATCH) == pg.evaluate(RULE) and len(pg.evaluate(MATCH)) > 5, f'{w}: data back: the match is worked out again (not kept from no data)')
        # kept: saved and read back; bad values fall back; a stack from before has the defaults
        ok(pg.evaluate("(() => { const s = JSON.parse(localStorage.getItem(MAP_STACK_KEY)); return s.only.hub === true && s.hub.fightH === 24; })()"), f'{w}: saved')
        ok(pg.evaluate("(() => { const k = localStorage.getItem(MAP_STACK_KEY), s = JSON.parse(k); s.hub = {fight: false, fightH: 99, vuln: true, vulnH: -2}; localStorage.setItem(MAP_STACK_KEY, JSON.stringify(s)); const o = itMapStackRead(); localStorage.setItem(MAP_STACK_KEY, k); return o.hub.fight === false && o.hub.fightH === 24 && o.hub.vulnH === 0; })()"), f'{w}: bad hours fall back, a kind kept')
        ok(pg.evaluate("(() => { const k = localStorage.getItem(MAP_STACK_KEY), s = JSON.parse(k); delete s.hub; delete s.only.hub; localStorage.setItem(MAP_STACK_KEY, JSON.stringify(s)); const o = itMapStackRead(); localStorage.setItem(MAP_STACK_KEY, k); return o.only.hub === false && JSON.stringify(o.hub) === JSON.stringify(itMapStackBlank().hub); })()"), f'{w}: a stack saved before this reads with Sov hubs off, the defaults')
        # first switch-on opens its settings
        pg.evaluate("MKH.scene('off'); itMapSt().seen.hub = false; itMapFilterSet('hub')")
        ok(pg.evaluate("itMapSt().only.hub && itMpShown() && itMp.k === 'hub'"), f'{w}: switched on the first time, its settings open')
        pg.evaluate("itMapFilterSet('hub')")
        ok(pg.evaluate("!itMapSt().only.hub && !itMpShown()"), f'{w}: switched off, its settings close')
        # the panel fits; on a phone the ticks are big enough; no sideways scroll
        pg.evaluate("MKH.scene('both')"); pg.wait_for_timeout(200)
        bx = pg.evaluate("(() => { const r = itMp.el.getBoundingClientRect(); return [r.left, r.right, innerWidth]; })()")
        ok(bx[0] >= 0 and bx[1] <= bx[2] + 0.5, f'{w}: the panel fits across {bx}')
        ok(pg.evaluate("itMp.el.scrollHeight <= itMp.el.clientHeight || getComputedStyle(itMp.el).overflowY === 'auto'"), f'{w}: the panel shows all or scrolls')
        if w < 600:
            hs = pg.evaluate("[...itMp.el.querySelectorAll('[data-mk-hk]')].map(x => Math.round(x.closest('label').getBoundingClientRect().height))")
            ok(len(hs) == 2 and min(hs) >= 24, f'{w}: the kinds\' ticks at least 24 px tall {hs}')
            pg.evaluate("itm.box.scrollIntoView({block:'start'})"); pg.wait_for_timeout(200)
            pg.screenshot(path=os.path.join(SHOTS, f'{w}_panel.png'))
        else:
            pg.evaluate("MKH.scene('wide'); itm.box.scrollIntoView({block:'start'})"); pg.wait_for_timeout(250)
            pg.screenshot(path=os.path.join(SHOTS, f'{w}_wide.png'))
        ok(pg.evaluate("document.documentElement.scrollWidth <= innerWidth"), f'{w}: no sideways scroll')
        ok(not errs, f'{w}: no page errors {errs[:2]}')
        b.close()
print(f'{n - len(fails)} of {n} passed'); sys.exit(1 if fails else 0)
