import sys, os
from playwright.sync_api import sync_playwright
html = os.path.abspath('out/wh_tree_mockup.html')
M = """() => { const M = whS.M, L = []; for(const l of whS.st.links){ const a = M.P.get(l.a), b = M.P.get(l.b); if(a && b && !whAt(l.a) + !whAt(l.b) >= 1) L.push(Math.hypot(a.x - b.x, a.y - b.y)); } L.sort((a, b) => a - b); const xs = [...M.P.values()];
  return {mean: Math.round(L.reduce((a, b) => a + b, 0) / L.length), p90: Math.round(L[Math.floor(L.length * .9)]), max: Math.round(L[L.length - 1]), over: (() => { let o = 0; const P = [...M.P.values()]; for(let i = 0; i < P.length; i++) for(let j = i + 1; j < P.length; j++) if(Math.abs(P[i].x - P[j].x) < WH_NW && Math.abs(P[i].y - P[j].y) < WH_NH) o++; return o; })(), s: +M.cam.s.toFixed(2)}; }"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for w in (1440, 390):
        ph = w < 600; ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': 844 if ph else 900}, has_touch=ph, is_mobile=ph); pg = ctx.new_page()
        pg.goto('file://' + html); pg.wait_for_function('window.__MKREADY || window.__MKERR', timeout=90000)
        for al in ('mid', 'top'):
            for sc in ('s25n', 'bushy', 'arr'):
                pg.evaluate(f"TREE.align = '{al}'"); pg.evaluate(f"TRscene('{'s25n' if sc == 'arr' else sc}')"); pg.wait_for_timeout(200)
                if sc == 'arr': pg.evaluate("TRscene('arr')"); pg.wait_for_timeout(200)
                pg.evaluate("whFit()"); pg.wait_for_timeout(100)
                print(w, al, sc, pg.evaluate(M)); pg.screenshot(path=f'shots/{al}_{sc}_{w}.png')
        ctx.close()
    b.close()
