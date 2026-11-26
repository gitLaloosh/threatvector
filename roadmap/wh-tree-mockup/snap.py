import sys, os, json
from playwright.sync_api import sync_playwright
html = os.path.abspath(sys.argv[1]); outd = sys.argv[2]; scenes = sys.argv[3].split(',')
GEO = """() => { const M = whS.M, P = [...M.P.entries()], o = [];
  for(let i = 0; i < P.length; i++) for(let j = i + 1; j < P.length; j++){ const a = P[i][1], b = P[j][1]; if(Math.abs(a.x - b.x) < WH_NW && Math.abs(a.y - b.y) < WH_NH) o.push([whName(P[i][0]), whName(P[j][0])]); }
  let mx = 0; for(const l of whS.st.links){ const a = M.P.get(l.a), b = M.P.get(l.b); if(a && b) mx = Math.max(mx, Math.hypot(a.x - b.x, a.y - b.y)); }
  return {n: P.length, over: o.length, maxLink: Math.round(mx), dir: M.dir, s: +M.cam.s.toFixed(2), pinned: TREE.pinned, last: TREE.last}; }"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for w in (1440, 390):
        ph = w < 600
        ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': 844 if ph else 900}, has_touch=ph, is_mobile=ph)
        pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + html); pg.wait_for_function('window.__MKREADY || window.__MKERR', timeout=90000)
        print(w, 'err', pg.evaluate('window.__MKERR'))
        for s in scenes:
            pg.evaluate(f"TRscene('{s}')"); pg.wait_for_timeout(500)
            print(w, s, pg.evaluate(GEO))
            pg.screenshot(path=f'{outd}/{s}_{w}.png')
        print(w, 'page errors', errs[:3]); ctx.close()
    b.close()
