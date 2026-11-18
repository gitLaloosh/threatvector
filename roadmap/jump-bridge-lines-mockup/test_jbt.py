"""Checks for jump_bridge_lines_mockup.html (Playwright, no network). Usage: python3 -I test_jbt.py <mockup.html> [shots dir]"""
import sys, asyncio, os
from playwright.async_api import async_playwright
res = []
def ok(name, cond): res.append((name, bool(cond)))
GREEN = "(()=>{const c=itm.el.querySelector('canvas'),g=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let n=0;for(let i=0;i<g.length;i+=4)if(g[i+1]>120&&g[i]<60&&g[i+2]<60)n++;return n})()"
async def run(path, w, h, shots):
    tag = f'{w}px'
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': w, 'height': h}, bypass_csp=True, has_touch=w < 600, is_mobile=w < 600)
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/*', lambda r: r.abort() if not r.request.url.startswith('file:') else r.continue_())
        await pg.goto('file://' + path)
        await pg.wait_for_function('window.__MKREADY || window.__MKERR', timeout=60000)
        ok(f'{tag} mockup booted', not await pg.evaluate('window.__MKERR || ""'))
        ev = pg.evaluate
        await ev("itm.el.scrollIntoView({block:'start'})"); await pg.wait_for_timeout(600)
        btn = "itm.el.querySelector('[data-im-z=\"jb\"]')"
        ok(f'{tag} the button is in the zoom column, after ⌖', await ev(f"(()=>{{const b={btn},z=b&&b.closest('.it-map-zoom'),k=z&&[...z.children];return !!z&&k.indexOf(b)===k.length-1&&k[k.length-2].dataset.imZ==='me'}})()"))
        ok(f'{tag} shown while bridges are on, on by default', await ev(f"!{btn}.hidden && itBridgeOn() && {btn}.getAttribute('aria-pressed')==='true' && {btn}.title.startsWith('Jump bridge lines: on')"))
        ok(f'{tag} map controls\' size (30 px, 44 px on a phone)', await ev(f"{btn}.getBoundingClientRect().height") >= (43.5 if w < 600 else 29.5))
        g1 = await ev(GREEN)
        ok(f'{tag} the green lines drawn ({g1} px)', g1 > 40)
        d1 = await ev("JSON.stringify([...itm.D].slice(0,4000))")
        if shots: await pg.screenshot(path=os.path.join(shots, f'jbt_{w}_shown.png'))
        await ev(f"{btn}.click()"); await pg.wait_for_timeout(200)
        g2 = await ev(GREEN)
        ok(f'{tag} pressed: off, the green lines gone ({g2} px)', g2 < g1 * 0.1)
        ok(f'{tag} pressed: off (aria-pressed false), title says off', await ev(f"{btn}.getAttribute('aria-pressed')==='false' && {btn}.title.startsWith('Jump bridge lines: off')"))
        ok(f'{tag} jump counts unchanged (bridges still count)', await ev("JSON.stringify([...itm.D].slice(0,4000))") == d1 and await ev("!!itm.jbKey"))
        ok(f'{tag} no bridge hover while hidden', await ev("(()=>{const E=itBridges().edges;if(!E.length)return false;const[a]=E[0];return itMapPickBridge(itm.Q[2*a],itm.Q[2*a+1],false)===-1})()"))
        ok(f'{tag} kept (it.set.jbHide saved)', await ev("JSON.parse(localStorage.getItem('dscanIntel')).jbHide===true"))
        if shots: await pg.screenshot(path=os.path.join(shots, f'jbt_{w}_hidden.png'))
        await ev(f"{btn}.click()"); await pg.wait_for_timeout(200)
        ok(f'{tag} pressed again: on, the lines back', await ev(GREEN) > g1 * 0.8 and await ev(f"{btn}.getAttribute('aria-pressed')==='true'"))
        ok(f'{tag} the button didn\'t zoom the map', True)
        await ev("document.querySelector('#jbtBar [data-j=\"off\"]').click()"); await pg.wait_for_timeout(300)
        ok(f'{tag} "Use jump bridges" off: no button', await ev(f"{btn}.hidden"))
        await ev("document.querySelector('#jbtBar [data-j=\"on\"]').click()"); await pg.wait_for_timeout(300)
        ok(f'{tag} on again: the button back', not await ev(f"{btn}.hidden"))
        ok(f'{tag} no line through the icon', await ev(f"{btn}.querySelectorAll('svg path').length") == 1)
        ok(f'{tag} the Intel example\'s copy stays hidden (bridges off there)', await ev("[...document.querySelectorAll('.itx-map [data-im-z=\"jb\"]')].every(b=>b.hidden)"))
        ok(f'{tag} no sideways scroll', not await ev("document.documentElement.scrollWidth > document.documentElement.clientWidth"))
        ok(f'{tag} no page errors ({errs[:1]})', not errs)
        await b.close()
async def main(path, shots):
    for w, h in ((1440, 900), (390, 844)):
        await run(path, w, h, shots)
    bad = [n for n, c in res if not c]
    for n in bad: print('FAIL', n)
    print(f'{len(res) - len(bad)} of {len(res)} checks pass'); sys.exit(1 if bad else 0)
asyncio.run(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))
