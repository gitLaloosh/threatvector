"""The mockup at 1440 and 390: loads, Proposed reads 1 page and 0 ESI killmails, a row's kills open, the info panel opens,
no sideways scroll, no page errors.   python3 -I test_fights.py <abs path of the mockup>"""
import sys, asyncio
from playwright.async_api import async_playwright
async def main(path):
    fails = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w in (1440, 390):
            pg = await b.new_page(viewport={'width': w, 'height': 900}, bypass_csp=True)
            errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('file://' + path)
            await pg.wait_for_function('window.__MKREADY || window.__MKERR', timeout=60000)
            await pg.click('[data-mk-view="prop"]')
            await pg.wait_for_function('!window.__MKBUSY && window.__P.on && window.__P.pages > 0', timeout=60000)
            c = await pg.evaluate('({zkb: window.__MKC.zkb, esi: window.__MKC.esiKm, pages: window.__P.pages})')
            if c['esi'] != 0 or c['pages'] != 1: fails.append(f'{w}: {c}')
            small = await pg.evaluate("Number(document.querySelector('[data-pd-mode=small] b').textContent)")
            if not small: fails.append(f'{w}: no small-gang kills')
            await pg.click('.pd-exp')
            n = await pg.evaluate("document.querySelectorAll('.pd-kills .pdk:not(.pdk-h)').length")
            if not n: fails.append(f'{w}: no kills under the row')
            await pg.screenshot(path=f'shots/open_{w}.png')
            await pg.click('#pilotDossier .info-pop summary')
            if not await pg.evaluate("!!document.querySelector('#pilotDossier details.info-pop[open]')"): fails.append(f'{w}: info panel')
            sw = await pg.evaluate('document.scrollingElement.scrollWidth - document.documentElement.clientWidth')
            if sw > 0: fails.append(f'{w}: sideways scroll {sw}px')
            if errs: fails.append(f'{w}: {errs}')
            await pg.close()
        await b.close()
    print(f'{len(fails)} failed', *fails, sep='\n')
asyncio.run(main(sys.argv[1]))
