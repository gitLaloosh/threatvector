import sys, json, asyncio
from playwright.async_api import async_playwright
async def main(path, out):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        res = {}
        for w in (1440, 390):
            pg = await b.new_page(viewport={'width': w, 'height': 1000}, bypass_csp=True)
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('file://' + path)
            await pg.wait_for_function('window.__MKREADY || window.__MKERR', timeout=60000)
            err = await pg.evaluate('window.__MKERR || null')
            await pg.wait_for_timeout(500)
            await pg.screenshot(path=f'{out}/today_{w}.png', full_page=False, clip=None)
            el = await pg.query_selector('#mkBar')
            await el.scroll_into_view_if_needed()
            await pg.screenshot(path=f'{out}/today_{w}.png')
            await pg.click('[data-mk-view="prop"]')
            await pg.wait_for_function('!window.__MKBUSY && window.__P.on && window.__P.pages > 0', timeout=60000)
            await pg.wait_for_timeout(500)
            await pg.screenshot(path=f'{out}/prop_{w}.png')
            await (await pg.query_selector('#pilotDossier')).scroll_into_view_if_needed()
            await pg.evaluate("document.getElementById('pilotDossier').scrollIntoView()")
            await pg.screenshot(path=f'{out}/prop_rows_{w}.png')
            await pg.click('[data-pd-mode="small"]')
            await pg.wait_for_timeout(300)
            await pg.evaluate("document.getElementById('pilotDossier').scrollIntoView()")
            await pg.screenshot(path=f'{out}/prop_small_{w}.png')
            await pg.click('[data-pd-mode="all"]')
            st = await pg.evaluate("({bar: document.getElementById('mkBar').innerText, sw: document.scrollingElement.scrollWidth, cw: document.documentElement.clientWidth})")
            await pg.click('[data-mk-rule="fleet"]')
            await pg.wait_for_function("!window.__MKBUSY && window.__P.rule === 'fleet'", timeout=90000)
            await pg.wait_for_timeout(500)
            await pg.screenshot(path=f'{out}/fleet_{w}.png')
            st2 = await pg.evaluate("document.getElementById('mkBar').innerText")
            res[w] = {'err': err, 'pageerrors': errs, 'prop': st, 'fleetrule': st2}
            await pg.close()
        await b.close()
        print(json.dumps(res, indent=1))
asyncio.run(main(sys.argv[1], sys.argv[2]))
