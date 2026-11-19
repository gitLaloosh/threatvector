"""Checks wh_statics_mockup.html at 1440 and 390 px (Playwright, no network). Usage: python3 -I test_stc.py wh_statics_mockup.html [shots dir]"""
import asyncio, sys, os, json
from playwright.async_api import async_playwright
P, F = 0, []
def ok(name, cond):
    global P
    if cond: P += 1
    else: F.append(name); print('FAIL', name)
async def run(path, w, h, shots):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': w, 'height': h}, bypass_csp=True, has_touch=(w < 600), is_mobile=(w < 600))
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith('file:') else r.abort())
        await pg.goto('file://' + os.path.abspath(path)); await pg.wait_for_timeout(2500)
        ev = pg.evaluate
        tag = f'{w}px'
        # list system (no typed statics): chips from the list, in class order, with the note
        n = await ev("(() => { const T = whTable(), J = T.names.filter(x => /^J\\d{6}$/.test(x)); return whIdOf(J[655 % J.length]); })()")
        exp = await ev(f"MOCK_STATICS[{n}]")
        chips = await ev("[...document.querySelectorAll('#whPnSum [data-wh-stc] .wh-sc')].map(e => e.textContent.split(' ')[0])")
        ok(f'{tag} list chips shown', sorted(chips) == sorted(exp.split()))
        ranks = await ev("[...document.querySelectorAll('#whPnSum [data-wh-stc] .wh-sc')].map(e => e.textContent.split(' ')[0])")
        ok(f'{tag} note says list', 'community list' in (await ev("(document.querySelector('#whPnSum [data-stc-src]')||{}).textContent || ''")))
        ok(f'{tag} field stays empty', (await ev("document.querySelector('#whPnSum [data-f=\"statics\"]').value")) == '')
        t = await ev("(document.querySelector('#whPnSum [data-wh-stc] .wh-sc')||{}).title || ''")
        ok(f'{tag} hover has lifetime and mass', ' h · ' in t and 't per jump' in t)
        # nothing saved from the list
        ok(f'{tag} list not saved', (await ev(f"JSON.parse(localStorage.getItem('tvWhChain')).sys['{n}'].statics")) == '')
        if shots: await pg.screenshot(path=f'{shots}/list_{w}.png')
        # typing replaces, clearing brings the list back
        await pg.fill('#whPnSum [data-f="statics"]', 'u210'); await pg.wait_for_timeout(150)
        chips = await ev("[...document.querySelectorAll('#whPnSum [data-wh-stc] .wh-sc')].map(e => e.textContent.split(' ')[0])")
        ok(f'{tag} typed replaces', chips == ['U210'])
        ok(f'{tag} note says typed', 'typed by you' in (await ev("document.querySelector('#whPnSum [data-stc-src]').textContent")))
        await pg.fill('#whPnSum [data-f="statics"]', ''); await pg.wait_for_timeout(150)
        chips = await ev("[...document.querySelectorAll('#whPnSum [data-wh-stc] .wh-sc')].map(e => e.textContent.split(' ')[0])")
        ok(f'{tag} clearing shows list again', sorted(chips) == sorted(exp.split()))
        # typed system: yours win
        await pg.click('#stcBar [data-m="typed"]'); await pg.wait_for_timeout(300)
        chips = await ev("[...document.querySelectorAll('#whPnSum [data-wh-stc] .wh-sc')].map(e => e.textContent.split(' ')[0])")
        ok(f'{tag} typed system shows yours', chips == ['D845'])
        # enter a new system: statics at once
        await pg.click('#stcBar [data-m="enter"]'); await pg.wait_for_timeout(400)
        m = await ev("whS.last"); exp2 = await ev(f"MOCK_STATICS[whS.last] || ''")
        chips = await ev("[...document.querySelectorAll('#whPnSum [data-wh-stc] .wh-sc')].map(e => e.textContent.split(' ')[0])")
        ok(f'{tag} entered system has statics', exp2 and sorted(chips) == sorted(exp2.split()))
        if shots: await pg.screenshot(path=f'{shots}/enter_{w}.png')
        # class order: a system with two statics to different places
        order = await ev("""(() => { const R = {c1:1,c2:2,c3:3,c4:4,c5:5,c6:6,hs:7,ls:8,ns:9,th:12,c13:13,dr:14,po:25}; for(const [id, v] of Object.entries(MOCK_STATICS)){ const c = v.split(' '); if(c.length > 1 && R[IT_WH_TYPE[c[0]]] > R[IT_WH_TYPE[c[1]]]) return [Number(id), v]; } })()""")
        await ev(f"whSeen({order[0]}, Date.now(), false); whS.drawKey = ''; whSelect({order[0]})"); await pg.wait_for_timeout(300)
        chips = await ev("[...document.querySelectorAll('#whPnSum [data-wh-stc] .wh-sc')].map(e => e.textContent.split(' ')[0])")
        ok(f'{tag} class order', chips == order[1].split()[::-1] or chips[0] == order[1].split()[1])
        # a connection's type suggestions: statics first
        here = await ev("whS.sel")
        await ev("(() => { const r = document.querySelector('#whPnSum .wh-cnw [data-wh-lr]'); if(r) r.click(); })()"); await pg.wait_for_timeout(100)
        await ev("(() => { const b = document.querySelector('#whPnSum .wh-cnw [data-wh-la=\"edit\"]'); if(b) b.click(); })()"); await pg.wait_for_timeout(150)
        dl = await ev("[...document.querySelectorAll('#stcTyDl option')].slice(0, 4).map(o => o.value)")
        mine = await ev(f"MOCK_STATICS[{here}] || ''")
        ok(f'{tag} type list: statics first then K162', len(dl) >= 2 and sorted(dl[:len(mine.split())]) == sorted(mine.split()) and dl[len(mine.split())] == 'K162')
        if shots: await pg.screenshot(path=f'{shots}/type_{w}.png')
        # Today: unchanged page
        await pg.click('#stcBar [data-m="today"]'); await pg.wait_for_timeout(200)
        await ev(f"whSelect({n})"); await pg.wait_for_timeout(200)
        ok(f'{tag} today: no list chips', (await ev("document.querySelectorAll('#whPnSum [data-wh-stc] .wh-sc').length")) == 0)
        ok(f'{tag} no sideways scroll', (await ev("document.documentElement.scrollWidth <= window.innerWidth + 1")))
        ok(f'{tag} no page errors', not errs) or print(errs[:3])
        await b.close()
async def main():
    path = sys.argv[1]; shots = sys.argv[2] if len(sys.argv) > 2 else None
    if shots: os.makedirs(shots, exist_ok=True)
    for w, h in ((1440, 900), (390, 844)): await run(path, w, h, shots)
    print(f'{P} passed, {len(F)} failed')
    sys.exit(1 if F else 0)
asyncio.run(main())
