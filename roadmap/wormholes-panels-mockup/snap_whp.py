"""Screenshots of the mockup: python3 -I snap_whp.py <mockup.html> <out dir>  (Playwright, bypass_csp, no network)."""
import sys, os
from playwright.sync_api import sync_playwright
html, out = os.path.abspath(sys.argv[1]), sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h, touch in ((1440, 900, False), (390, 844, True)):
        ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': h}, has_touch=touch, is_mobile=touch, device_scale_factor=1)
        ctx.route('**/*', lambda r: r.continue_() if r.request.url.startswith('file:') else r.abort())
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + html); pg.wait_for_timeout(900)
        pg.screenshot(path=f'{out}/{w}_shut.png')
        pg.click('[data-whp-rp]'); pg.wait_for_timeout(300); pg.screenshot(path=f'{out}/{w}_open.png')
        pg.click('[data-whp-m="today"]'); pg.wait_for_timeout(300); pg.screenshot(path=f'{out}/{w}_today.png')
        print(w, 'errors:', errs[:3])
        ctx.close()
    b.close()
