"""Checks the Intel example controls mockup at 1440 and 390 px, Today and Proposed; saves screenshots into shots/.

Usage: python3 -I test_exctl.py <mockup.html> [shots dir]
"""
import os
import sys
from playwright.sync_api import sync_playwright

HTML = os.path.abspath(sys.argv[1])
SHOTS = sys.argv[2] if len(sys.argv) > 2 else 'shots'
os.makedirs(SHOTS, exist_ok=True)
fails = []


def check(ok, msg):
    print(('PASS ' if ok else 'FAIL ') + msg)
    if not ok:
        fails.append(msg)


PROBE = """() => {
  const f = document.querySelector('.itx'); if(!f) return null;
  const box = f.querySelector('.itx-map'), img = box.querySelector('img'), q = (s) => box.querySelectorAll(s).length;
  const vis = (s) => { const e = box.querySelector(s); if(!e) return false; const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && getComputedStyle(e).visibility !== 'hidden'; };
  const inBox = (s) => { const e = box.querySelector(s); if(!e) return false; const r = e.getBoundingClientRect(), b = img.getBoundingClientRect(); return r.left >= b.left - 1 && r.right <= b.right + 1 && r.top >= b.top - 1 && r.bottom <= b.bottom + 1; };
  const live = document.querySelectorAll('#itRpSug').length, ids = [...f.querySelectorAll('[id]')].map(e => e.id);
  const hooks = [...f.querySelectorAll('.itx-map [data-im-f], .itx-map [data-im-z], .itx-map [data-it-ny], .itx-map [data-it-whl], .itx [data-rs]')].length;
  const foc = [...f.querySelectorAll('button, input')].filter(e => e.tabIndex >= 0 && !e.closest('[inert]')).length;
  const pressed = [...box.querySelectorAll('.it-map-fbtns button[aria-pressed="true"]')].map(b => b.getAttribute('aria-label'));
  const nr = f.querySelector('.it-nearcol').getBoundingClientRect(), ir = img.getBoundingClientRect(), rail = box.querySelector('.it-map-rail').getBoundingClientRect(), zoom = box.querySelector('.it-map-zoom');
  const zr = zoom ? zoom.getBoundingClientRect() : null;
  const marks = [1,2,3,4,5].map(n => { const m = f.querySelector('[data-itx-mk="' + n + '"]'); return m && !m.hidden; });
  const nh = Math.round(f.querySelector('.itx-near').getBoundingClientRect().height);
  const m3 = f.querySelector('[data-itx-mk="3"]').getBoundingClientRect();
  const over = (sel) => { const e = box.querySelector(sel); if(!e) return false; const r = e.getBoundingClientRect(); return r.width > 0 && m3.left < r.right && m3.right > r.left && m3.top < r.bottom && m3.bottom > r.top; };
  return {zoom: q('.it-map-zoom'), search: q('.it-rp-search'), fb: q('.it-map-fb'), filters: q('.it-map-fbtns [aria-label]'), rail: q('.it-map-rail'), row: f.querySelectorAll('.it-map-row').length,
    zoomVis: vis('.it-map-zoom'), searchVis: vis('.it-rp-search'), colVis: vis('.it-map-fbtns'), curVis: vis('.it-map-fcur'),
    inside: ['.it-map-zoom', '.it-rp-search', '.it-map-rail'].every(inBox), h: Math.round(ir.height), w: Math.round(ir.width),
    nearBelowRail: zr ? rail.top >= zr.bottom - 1 : null, nearTop: Math.round(nr.top - ir.top), live, ids, hooks, foc, pressed, marks,
    m3search: over('.it-rp-search'), nh, railClear: (() => { const s = box.querySelector('.it-rp-search'); if(!s) return null; const a = s.getBoundingClientRect(); return rail.top >= a.bottom - 1 || rail.bottom <= a.top + 1; })(), m3col: over('.it-map-fbtns') || over('.it-map-fcur'), sw: document.documentElement.scrollWidth };
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    for w in (1440, 390):
        for mode in ('today', 'new'):
            errs = []
            pg = b.new_page(viewport={'width': w, 'height': 1100}, bypass_csp=True)
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto('file://' + HTML)
            pg.evaluate('() => localStorage.clear()')
            pg.reload()
            pg.wait_for_timeout(1500)
            if mode == 'today':
                pg.evaluate("() => window.__mkMode('today')")
            pg.wait_for_timeout(1500)
            r = pg.evaluate(PROBE)
            pg.query_selector('.itx').screenshot(path=f'{SHOTS}/{mode}_{w}.png')
            tag = f'{w} {mode}:'
            check(r is not None, f'{tag} example drawn')
            if r is None:
                continue
            check(not errs, f'{tag} no page errors {errs[:2]}')
            check(r['sw'] <= w, f'{tag} no sideways scroll ({r["sw"]})')
            check(all(r['marks']), f'{tag} all 5 markers shown {r["marks"]}')
            check(r['live'] == 0, f'{tag} the example adds no live map ids ({r["live"]} #itRpSug; ids {r["ids"][:5]})')
            if mode == 'today':
                check(r['zoom'] == 0 and r['search'] == 0 and r['fb'] == 0 and r['row'] == 0, f'{tag} as main today: no zoom, search, filters or slider row')
                continue
            check(r['zoom'] == 1 and r['search'] == 1 and r['fb'] == 1 and r['rail'] == 1 and r['row'] == 1, f'{tag} zoom, search, filter column, rail, slider row all there {r}')
            check(r['filters'] >= 7, f'{tag} every filter ({r["filters"]})')
            check(r['pressed'] == ['Security status'], f'{tag} Security pressed {r["pressed"]}')
            check(r['zoomVis'] and r['searchVis'] and r['inside'], f'{tag} zoom and search shown inside the picture')
            check(r['ids'] == [] and r['hooks'] == 0 and r['foc'] == 0, f'{tag} still copies: no ids {r["ids"]}, no hooks ({r["hooks"]}), nothing focusable ({r["foc"]})')
            check(r['nearBelowRail'], f'{tag} the rail under the zoom row')
            check(r['nh'] > 100, f'{tag} Near You\'s rows have height ({r["nh"]})')
            check(r['railClear'], f'{tag} the rail clear of the search box')
            check(not r['m3search'] and not r['m3col'], f'{tag} marker 3 clear of the search box and the filters')
            if w == 1440:
                check(r['colVis'] and not r['curVis'], f'{tag} filter column open, no phone button')
                check(r['h'] == min(720, max(520, round(r['w'] * 0.5))), f'{tag} live map height ({r["h"]} for {r["w"]})')
                check(abs(r['nearTop'] - 46) <= 1, f'{tag} Near You level with the rail ({r["nearTop"]})')
            else:
                check(r['curVis'] and not r['colVis'], f'{tag} phone: the column shut behind its button')
                check(r['h'] == min(600, max(440, round(r['w'] * 1.45))), f'{tag} live map height ({r["h"]} for {r["w"]})')
            pg.close()
    b.close()
print(f'{len(fails)} failed')
sys.exit(1 if fails else 0)
