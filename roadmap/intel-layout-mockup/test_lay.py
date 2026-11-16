"""Intel layout mockup checks (rounds 2-6b): python3 -I test_lay.py <page.html> <shots dir>. Fresh page per case; 1440 and 390 px."""
import sys, os, asyncio
from playwright.async_api import async_playwright
F, OUT = os.path.abspath(sys.argv[1]), sys.argv[2]; os.makedirs(OUT, exist_ok=True)
res = []
def ok(name, cond, extra=''): res.append((name, bool(cond))); print(('PASS ' if cond else 'FAIL ') + name, extra)
async def page(b, w):
    ctx = await b.new_context(viewport={'width': w, 'height': 1000 if w > 600 else 844}, bypass_csp=True, has_touch=w < 600)
    pg = await ctx.new_page(); pg.errs = []; pg.on('pageerror', lambda e: pg.errs.append(str(e)))
    await pg.goto('file://' + F); await pg.wait_for_function('window.__MKREADY || window.__MKERR', timeout=30000)
    await pg.evaluate("document.querySelector('.mk-bar') && document.querySelector('.mk-bar').classList.add('min')")
    await pg.evaluate("MKL.S.fl='bottom'; MKL.apply()"); await pg.wait_for_timeout(200)   # rounds 2-4 checks: the bar along the bottom (round 5's left sets its own)
    return ctx, pg
SHOWN = "(s)=>{const e=document.querySelector(s); if(!e) return false; const c=getComputedStyle(e); return c.visibility==='visible' && +c.opacity>0.5 && e.offsetWidth>0;}"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w in (1440, 390):
            for lay in ('today', 'a'):
                ctx, pg = await page(b, w)
                await pg.evaluate(f"MKL.S.lay='{lay}'; MKL.apply()"); await pg.wait_for_timeout(700)
                sw = await pg.evaluate('document.documentElement.scrollWidth - innerWidth')
                vis = await pg.evaluate("(()=>{const c=document.querySelector('#intelPanel .it-nearcol'), m=itm.box; return !!(c && m && m.offsetHeight>200 && (c.offsetHeight>30 || !!document.querySelector('.mk-rail [data-mk-ny]').offsetParent));})()")
                ok(f'{w} {lay}: no sideways scroll, the map and Near You (or its button) shown', sw <= 0 and vis, f'sw={sw}')
                if lay == 'a':
                    for rail in ('right', 'left'):
                        await pg.evaluate(f"MKL.S.rail='{rail}'; MKL.S.nyOpen=false; MKL.place()"); await pg.wait_for_timeout(250)
                        await pg.evaluate("itm.box.scrollIntoView({block:'center'})"); await pg.wait_for_timeout(150)
                        shut = await pg.evaluate("(()=>{const c=document.querySelector('#intelPanel .it-nearcol'), b=document.querySelector('.mk-rail [data-mk-ny]').getBoundingClientRect(), m=itm.box.getBoundingClientRect(); return getComputedStyle(c).display==='none' && b.width>=29 && b.top>=m.top && b.right<=m.right;})()")
                        ok(f'{w} a {rail}: shut, only the Near You button shows, inside the map', shut)
                        size = await pg.evaluate("(()=>{const b=document.querySelector('.mk-rail [data-mk-ny]').getBoundingClientRect(), z=document.querySelector('.it-map-zoom button').getBoundingClientRect(); return Math.abs(b.width-z.width)<=2 && Math.abs(b.height-z.height)<=2;})()")
                        ok(f'{w} a {rail}: the Near You button is the size of the zoom buttons', size)
                        clear = await pg.evaluate("(()=>{const r=document.querySelector('.mk-rail').getBoundingClientRect(); for(const e of document.querySelectorAll('.it-map-zoom button, .it-rp-search input, .it-rp-search')){ const q=e.getBoundingClientRect(); if(q.width && !(q.bottom<=r.top || q.top>=r.bottom || q.right<=r.left || q.left>=r.right)) return false; } return true;})()")
                        ok(f'{w} a {rail}: the buttons cover neither the zoom buttons nor the search box', clear)
                        await pg.click('.mk-rail [data-mk-ny]'); await pg.wait_for_timeout(300)
                        geo = await pg.evaluate("(()=>{const c=document.querySelector('#intelPanel .it-nearcol').getBoundingClientRect(), r=document.querySelector('.mk-rail').getBoundingClientRect(), m=itm.box.getBoundingClientRect(); return {inside: c.top>=m.top-1 && c.bottom<=m.bottom+1 && c.left>=m.left-1 && c.right<=m.right+1, right: c.right<=r.left+1, left: c.left>=r.right-1};})()")
                        ok(f'{w} a {rail}: open, the list sits inside the map beside the buttons', geo['inside'] and geo[rail == 'right' and 'right' or 'left'], str(geo))
                        hit = await pg.evaluate("""(()=>{ const at=(e)=>{const q=e.getBoundingClientRect(), h=document.elementFromPoint(q.left+q.width/2, q.top+q.height/2); return !!h && (h===e || e.contains(h));};
                          const fb=[...document.querySelectorAll('.it-map-fbtns [data-im-f], .it-map-fcur')].filter(e=>e.offsetParent)[0];
                          return {rail: at(document.querySelector('.mk-rail [data-mk-ny]')), zoom: [...document.querySelectorAll('.it-map-zoom button')].filter(e=>e.offsetParent).every(at), bar: !!fb && at(fb)}; })()""")
                        ok(f'{w} a {rail}: open, the buttons, zoom and filter bar stay clickable', all(hit.values()), str(hit))
                        await pg.screenshot(path=f'{OUT}/a_{rail}_open_{w}.png')
                        await pg.click('.mk-rail [data-mk-ny]'); await pg.wait_for_timeout(250)
                        ok(f'{w} a {rail}: pressed again, the list shuts', await pg.evaluate("getComputedStyle(document.querySelector('#intelPanel .it-nearcol')).display==='none'"))
                await pg.screenshot(path=f'{OUT}/{lay}_{w}.png'); ok(f'{w} {lay}: no page errors', not pg.errs, str(pg.errs[:2])); await ctx.close()
            # round 4: a filter's panel opens clear of an open Near You list (wide) / shuts Near You (phone)
            for rail in ('right', 'left'):
                ctx, pg = await page(b, w)
                await pg.evaluate(f"MKL.S.lay='a'; MKL.S.rail='{rail}'; MKL.S.nyOpen=true; MKL.apply()"); await pg.wait_for_timeout(500)
                await pg.evaluate("itm.box.scrollIntoView({block:'center'})")
                await pg.evaluate("itMapFilterSet('sov'); MKL.sovPanel(true)"); await pg.wait_for_timeout(400)
                if w > 600:
                    g = await pg.evaluate("""(()=>{ const ov=(a,b)=>!(a.right<=b.left||a.left>=b.right||a.bottom<=b.top||a.top>=b.bottom);
                      const p=document.querySelector('.mk-sp').getBoundingClientRect(), c=document.querySelector('#intelPanel .it-nearcol').getBoundingClientRect(), r=document.querySelector('.mk-rail').getBoundingClientRect(), f=document.querySelector('.it-map-fbtns').getBoundingClientRect(), m=itm.box.getBoundingClientRect();
                      return {nearYou: !ov(p,c), rail: !ov(p,r), aboveBar: p.bottom<=f.top+1, inMap: p.left>=m.left-1 && p.right<=m.right+1 && p.top>=m.top-1}; })()""")
                    ok(f'{w} {rail}: the Sov panel opens above the filter bar, clear of the Near You list and its buttons', all(g.values()), str(g))
                    await pg.evaluate("document.querySelector('.it-map-fbtns [data-im-f=wh]').click()"); await pg.wait_for_timeout(200)
                    await pg.evaluate("document.querySelector('.it-map-fbtns button.it-whl').click()"); await pg.wait_for_timeout(400)
                    g2 = await pg.evaluate("""(()=>{ const e=document.querySelector('.it-whp:not(.mk-sp)'); if(!e||e.hidden) return null; const p=e.getBoundingClientRect(), c=document.querySelector('#intelPanel .it-nearcol').getBoundingClientRect(); return !(p.right<=c.left||p.left>=c.right||p.bottom<=c.top||p.top>=c.bottom); })()""")
                    ok(f'{w} {rail}: the Wormholes list opens clear of the Near You list', g2 is False, str(g2))
                    await pg.screenshot(path=f'{OUT}/panels_{rail}_{w}.png')
                else:
                    ok(f'{w} {rail}: on a phone the Sov panel shuts Near You', await pg.evaluate("getComputedStyle(document.querySelector('#intelPanel .it-nearcol')).display==='none'"))
                ok(f'{w} {rail} panels: no page errors', not pg.errs, str(pg.errs[:2])); await ctx.close()
            for fp in ('beside', 'above'):
                ctx, pg = await page(b, w)
                await pg.evaluate(f"MKL.S.lay='a'; MKL.S.fp='{fp}'; MKL.apply()"); await pg.wait_for_timeout(500)
                await pg.evaluate("itm.box.scrollIntoView({block:'center'})")
                if w < 600: await pg.click('.it-map-fcur'); await pg.wait_for_timeout(250)
                ok(f'{w} {fp}: panel buttons hidden on a filter without a panel', not await pg.evaluate(SHOWN, 'button.it-whl') and not await pg.evaluate(SHOWN, '[data-mk-sb]'))
                for k, pbs, check in (('wh', 'button.it-whl', 'itWhListShown()'), ('sov', '[data-mk-sb]', "!!document.querySelector('.mk-sp') && !document.querySelector('.mk-sp').hidden")):
                    if w > 600:
                        await pg.hover(f'[data-im-f="{k}"]'); await pg.wait_for_timeout(250)
                        ok(f'{w} {fp}: hovering {k} shows its panel button', await pg.evaluate(SHOWN, pbs))
                    else:
                        if await pg.evaluate("getComputedStyle(document.querySelector('.it-map-fbtns')).display==='none'"): await pg.click('.it-map-fcur'); await pg.wait_for_timeout(250)
                        await pg.click(f'[data-im-f="{k}"]'); await pg.wait_for_timeout(250)
                        if not await pg.evaluate("!!document.querySelector('.it-map-fcur') && getComputedStyle(document.querySelector('.it-map-fbtns')).display!=='none'"):
                            await pg.click('.it-map-fcur'); await pg.wait_for_timeout(250)
                        ok(f'{w} {fp}: {k} on shows its panel button', await pg.evaluate(SHOWN, pbs))
                    if fp == 'above':
                        ab = await pg.evaluate(f"(()=>{{const p=document.querySelector('{pbs}').getBoundingClientRect(), f=document.querySelector('[data-im-f=\\"{k}\\"]').getBoundingClientRect(); return p.bottom<=f.top+1 && Math.abs((p.left+p.right)/2-(f.left+f.right)/2)<3;}})()")
                        ok(f'{w} above: {k} panel button sits above its filter', ab)
                        if w > 600:
                            await pg.evaluate("document.querySelector('.it-map-fb').classList.add('named')"); await pg.wait_for_timeout(250)
                            clr = await pg.evaluate(f"(()=>{{const n=document.querySelector('.it-map-fn').getBoundingClientRect(), p=document.querySelector('{pbs}').getBoundingClientRect(); return n.bottom<=p.top+1;}})()")
                            ok(f'{w} above: the filter name line clears the {k} panel button', clr)
                    else:
                        bs = await pg.evaluate(f"(()=>{{const p=document.querySelector('{pbs}').getBoundingClientRect(), f=document.querySelector('[data-im-f=\\"{k}\\"]').getBoundingClientRect(); return p.left>=f.right-1 && Math.abs(p.top-f.top)<8;}})()")
                        ok(f'{w} beside: {k} panel button sits right of its filter', bs)
                    await pg.click(pbs); await pg.wait_for_timeout(300)
                    ok(f'{w} {fp}: {k} panel opens', await pg.evaluate(check))
                    if k == 'wh': await pg.keyboard.press('Escape'); await pg.wait_for_timeout(200)
                await pg.screenshot(path=f'{OUT}/fp_{fp}_{w}.png')
                # sov lists: Edit shows the list's lines; Remove says what it would do; the map dims
                ok(f'{w} {fp}: Lists start shut', not await pg.evaluate("!!document.querySelector('.mk-sp [data-mk-ed]')"))
                await pg.click('[data-mk-lists]'); await pg.wait_for_timeout(200)
                await pg.click('[data-mk-ed="cy"]'); await pg.wait_for_timeout(200)
                n = await pg.evaluate("(document.querySelector('[data-mk-et]')||{value:''}).value.split('\\n').filter(Boolean).length")
                ok(f'{w} {fp}: Edit opens the cyno list with its lines', n >= 3, f'lines={n}')
                await pg.screenshot(path=f'{OUT}/edit_{fp}_{w}.png')
                await pg.click('[data-mk-rm="up"]'); await pg.wait_for_timeout(200)
                ok(f'{w} {fp}: Remove names the one list', 'Upgrades list only' in await pg.evaluate("document.querySelector('.mk-sp').textContent"))
                dim = await pg.evaluate("(()=>{let a=0,d=0; for(let i=0;i<itMapTable().n;i++){ if(itMapDimmed(i)) d++; else a++; } return [a,d];})()")
                ok(f'{w} {fp}: Sov upgrades dims systems without a picked upgrade', dim[0] > 3 and dim[1] > 100, str(dim))
                sw = await pg.evaluate('document.documentElement.scrollWidth - innerWidth'); ok(f'{w} {fp}: no sideways scroll', sw <= 0, f'sw={sw}')
                if fp == 'beside':   # round 2b: the three sov looks draw without errors, the key follows, a hover names the upgrades
                    await pg.evaluate("MKL.sovPanel(false)")
                    for look in ('dim', 'colour', 'marks'):
                        await pg.evaluate(f"MKL.S.look='{look}'; if('{look}'==='marks' && itMapGatePx()<26) itMapZoom(itm.W/2, itm.H/2, 30/itMapGatePx()); itMapDraw(); itMapLegend()")
                        await pg.wait_for_timeout(250)
                        leg = await pg.evaluate("(document.querySelector('.it-map-fleg, .it-map-leg')||document.body).textContent")
                        ok(f'{w} look {look}: the key says how sov upgrades look', 'Sov upgrades' in leg)
                        await pg.screenshot(path=f'{OUT}/look_{look}_{w}.png')
                    i = await pg.evaluate("(()=>{for(let i=0;i<itMapTable().n;i++) if(!itMapDimmed(i) && i!==itm.home) return i; return -1;})()")
                    await pg.evaluate(f"itMapTip({i}, 100, 100)")
                    ok(f'{w} hover names the sov upgrades', 'Sov upgrades:' in await pg.evaluate("itm.tip.textContent"))
                ok(f'{w} panels {fp}: no page errors', not pg.errs, str(pg.errs[:2])); await ctx.close()
            # round 5: filters down the left, feeds on the right
            ctx, pg = await page(b, w)
            await pg.evaluate("MKL.S.lay='a'; MKL.S.fl='left'; MKL.S.rail='left'; MKL.apply()"); await pg.wait_for_timeout(500)
            await pg.evaluate("itm.box.scrollIntoView({block:'center'})"); await pg.wait_for_timeout(200)
            ok(f'{w} left: Near You stays on the right', await pg.evaluate("itm.box.dataset.mkRail==='right' && document.querySelector('.mk-rail').getBoundingClientRect().left > itm.box.getBoundingClientRect().left + itm.box.getBoundingClientRect().width/2"))
            if w < 600: await pg.click('.it-map-fcur'); await pg.wait_for_timeout(250)
            col = await pg.evaluate("""(()=>{ const ov=(a,b)=>!(a.right<=b.left||a.left>=b.right||a.bottom<=b.top||a.top>=b.bottom);
              const f=document.querySelector('.it-map-fbtns').getBoundingClientRect(), m=itm.box.getBoundingClientRect(), q=document.querySelector('.it-rp-search').getBoundingClientRect(), r=document.querySelector('.mk-rail').getBoundingClientRect();
              const bs=[...document.querySelectorAll('.it-map-fbtns [data-im-f]')].map(e=>e.getBoundingClientRect());
              const z=[...document.querySelectorAll('.it-map-zoom button')].filter(e=>e.offsetParent).map(e=>e.getBoundingClientRect());
              return {leftEdge: f.left-m.left<=12, underSearch: f.top>=q.bottom-1, inMap: f.bottom<=m.bottom+1 && f.top>=m.top, tall: f.height>f.width, all: bs.every(b=>b.width>0 && b.bottom<=m.bottom), clear: !ov(f,r) && z.every(b=>!ov(f,b))}; })()""")
            ok(f'{w} left: the filters are a column at the map\'s left edge, under the search box, all inside the map, clear of the other buttons', all(col.values()), str(col))
            if w > 600:
                await pg.hover('[data-im-f="sov"]'); await pg.wait_for_timeout(300)
                g = await pg.evaluate("""(()=>{const p=document.querySelector('[data-mk-sb]').getBoundingClientRect(), f=document.querySelector('[data-im-f=sov]').getBoundingClientRect(), c=document.querySelector('.it-map-fbtns').getBoundingClientRect(); return p.left>=c.right && Math.abs(p.top-f.top)<4;})()""")
                ok(f'{w} left: hovering Sov shows its panel button to the right of the column, level with it', g and await pg.evaluate(SHOWN, '[data-mk-sb]'))
                await pg.evaluate("document.querySelector('.it-map-fb').classList.add('named')"); await pg.wait_for_timeout(300)
                n = await pg.evaluate("""(()=>{const n=document.querySelector('.it-map-fn').getBoundingClientRect(), c=document.querySelector('.it-map-fbtns').getBoundingClientRect(), f=document.querySelector(`.it-map-fbtns [data-im-f="${itm.filter}"]`).getBoundingClientRect(), r=document.querySelector('.mk-rail').getBoundingClientRect();
                  return {right: n.left>=c.right+32, level: Math.abs((n.top+n.bottom)/2-(f.top+f.bottom)/2)<3, clearRail: n.right<=r.left};})()""")
                ok(f'{w} left: the name line sits right of the panel buttons, level with the filter that is on', all(n.values()), str(n))
                await pg.click('.mk-rail [data-mk-ny]'); await pg.wait_for_timeout(300)
                hit = await pg.evaluate("""(()=>{ const at=(e)=>{const q=e.getBoundingClientRect(), h=document.elementFromPoint(q.left+q.width/2, q.top+q.height/2); return !!h && (h===e || e.contains(h));};
                  return [...document.querySelectorAll('.it-map-fbtns [data-im-f], .mk-rail [data-mk-ny], .it-map-zoom button')].filter(e=>e.offsetParent).every(at); })()""")
                ok(f'{w} left: with Near You open, every filter, the rail and zoom stay clickable', hit)
                await pg.evaluate("itMapFilterSet('sov'); MKL.sovPanel(true)"); await pg.wait_for_timeout(400)
                g = await pg.evaluate("""(()=>{ const ov=(a,b)=>!(a.right<=b.left||a.left>=b.right||a.bottom<=b.top||a.top>=b.bottom);
                  const p=document.querySelector('.mk-sp').getBoundingClientRect(), c=document.querySelector('#intelPanel .it-nearcol').getBoundingClientRect(), r=document.querySelector('.mk-rail').getBoundingClientRect(), f=document.querySelector('.it-map-fbtns').getBoundingClientRect(), sb=document.querySelector('[data-mk-sb]').getBoundingClientRect(), m=itm.box.getBoundingClientRect();
                  return {nearYou: !ov(p,c), rail: !ov(p,r), rightOfButtons: p.left>=sb.right, inMap: p.left>=m.left-1 && p.right<=m.right+1 && p.top>=m.top-1 && p.bottom<=m.bottom+1, nameHidden: getComputedStyle(document.querySelector('.it-map-fn')).visibility==='hidden'}; })()""")
                ok(f'{w} left: the Sov panel opens right of the panel buttons, inside the map, clear of Near You', all(g.values()), str(g))
                await pg.screenshot(path=f'{OUT}/left_sov_{w}.png')
                await pg.evaluate("MKL.sovPanel(false); itMapFilterSet('wh')"); await pg.wait_for_timeout(200)
                await pg.evaluate("document.querySelector('.it-map-fbtns button.it-whl').click()"); await pg.wait_for_timeout(400)
                g2 = await pg.evaluate("""(()=>{ const e=document.querySelector('.it-whp:not(.mk-sp)'); if(!e||e.hidden) return null; const p=e.getBoundingClientRect(), c=document.querySelector('#intelPanel .it-nearcol').getBoundingClientRect(), b=document.querySelector('.it-map-fbtns button.it-whl').getBoundingClientRect(); return {clear: p.right<=c.left, right: p.left>=b.right};})()""")
                ok(f'{w} left: the Wormholes list opens right of its button, clear of Near You', bool(g2) and all(g2.values()), str(g2))
            else:
                await pg.click('[data-im-f="sov"]'); await pg.wait_for_timeout(250)
                ok(f'{w} left: picking a filter shuts the column', await pg.evaluate("getComputedStyle(document.querySelector('.it-map-fbtns')).display==='none'"))
                await pg.click('.mk-rail [data-mk-ny]'); await pg.wait_for_timeout(250)
                await pg.click('.it-map-fcur'); await pg.wait_for_timeout(300)
                ok(f'{w} left: opening the filter column shuts Near You', await pg.evaluate("getComputedStyle(document.querySelector('#intelPanel .it-nearcol')).display==='none'"))
                ok(f'{w} left: Sov on shows its panel button in the column', await pg.evaluate(SHOWN, '[data-mk-sb]'))
                n = await pg.evaluate("""(()=>{const n=document.querySelector('.it-map-fn').getBoundingClientRect(), r=document.querySelector('.mk-rail').getBoundingClientRect(), c=document.querySelector('.it-map-fbtns').getBoundingClientRect(); return n.width===0 || (n.right<=r.left+1 && !(n.right>c.left && n.left<c.right && n.bottom>c.top && n.top<c.bottom));})()""")
                ok(f'{w} left: the name line covers neither the column nor the Near You button', n)
                await pg.click('.mk-rail [data-mk-ny]'); await pg.wait_for_timeout(300)
                ok(f'{w} left: opening Near You shuts the filter column', await pg.evaluate("!document.querySelector('.it-map-fb.open') && getComputedStyle(document.querySelector('#intelPanel .it-nearcol')).display!=='none'"))
                await pg.click('.it-map-fcur'); await pg.wait_for_timeout(250); await pg.click('[data-mk-sb]'); await pg.wait_for_timeout(300)
                g = await pg.evaluate("(()=>{const p=document.querySelector('.mk-sp').getBoundingClientRect(), m=itm.box.getBoundingClientRect(); return !document.querySelector('.mk-sp').hidden && p.left>=m.left && p.right<=m.right && p.bottom<=m.bottom+1;})()")
                ok(f'{w} left: the Sov panel opens inside the map', g)
                await pg.screenshot(path=f'{OUT}/left_sov_{w}.png')
            sw = await pg.evaluate('document.documentElement.scrollWidth - innerWidth'); ok(f'{w} left: no sideways scroll', sw <= 0, f'sw={sw}')
            ok(f'{w} left: no page errors', not pg.errs, str(pg.errs[:2])); await ctx.close()
            # round 6: Near You in the site's panel style; checkboxes and radios in the text field's colours; more icons; Jump bridge under Navigation
            ctx, pg = await page(b, w)
            await pg.evaluate("MKL.S.lay='a'; MKL.S.fl='left'; MKL.S.nyOpen=true; MKL.apply()"); await pg.wait_for_timeout(500)
            await pg.evaluate("itMapFilterSet('sov'); MKL.sovPanel(true)"); await pg.wait_for_timeout(300)
            if w > 600:
                bg = await pg.evaluate("(()=>{const c=getComputedStyle(document.querySelector('#intelPanel .it-nearcol')), p=getComputedStyle(document.querySelector('.mk-sp')), r=document.querySelector('#itNearList .it-nb'), v=getComputedStyle(document.body).getPropertyValue('--panel-2').trim(); const t=document.createElement('i'); t.style.color=v; document.body.appendChild(t); const v2=getComputedStyle(t).color; t.remove(); return {panel: c.backgroundColor===p.backgroundColor, border: c.borderTopColor===p.borderTopColor, rows: !r || getComputedStyle(r).backgroundColor===v2};})()")
                ok(f'{w} r6: the Near You panel matches the filter panels (background, border); its rows are the card colour', all(bg.values()), str(bg))
            CK = "(()=>{const c=document.querySelector('.mk-sp input[type=checkbox]:checked'), u=document.querySelector('.mk-sp input[type=checkbox]:not(:checked)'), sw=document.querySelector('input.mys-sw'); const g=(e)=>getComputedStyle(e); const bgv=(()=>{const t=document.createElement('i'); t.style.color='var(--bg)'; document.body.appendChild(t); const x=getComputedStyle(t).color; t.remove(); return x;})(); return {appearance: g(c).appearance==='none' && g(u).appearance==='none', unBg: g(u).backgroundColor===bgv, onBg: g(c).backgroundColor, bgv, sw: !sw || g(sw).width==='36px'};})()"
            t = await pg.evaluate(CK)
            ok(f'{w} r6 tick: checkboxes drawn by the site, unchecked dark like a field, checked box stays dark, switches untouched', t['appearance'] and t['unBg'] and t['onBg'] == t['bgv'] and t['sw'], str(t))
            await pg.evaluate("MKL.S.ck='fill'; document.body.dataset.mkCk='fill'"); await pg.wait_for_timeout(150)
            t = await pg.evaluate(CK)
            ok(f'{w} r6 fill: a checked box fills (not the dark field colour)', t['onBg'] != t['bgv'] and t['unBg'], str(t))
            ok(f'{w} r6: Jump bridge sits under Navigation, read from the Jump bridges list', await pg.evaluate("(()=>{const l=document.querySelector('.mk-sp [data-mk-k=jb]'); return !!l && /from Jump bridges/.test(l.closest('label').textContent);})()"))
            n = await pg.evaluate("(()=>{let k=0; for(const ic of ['radar','pin','rings','blip','alert','bang','pinbang','bell','signal','eye','feed']){ MKL.S.icon=ic; MKL.place(); if(document.querySelector('.mk-rail [data-mk-ny] svg path, .mk-rail [data-mk-ny] svg circle')) k++; } return k;})()")
            ok(f'{w} r6: all eleven Near You icons draw', n == 11, f'n={n}')
            ok(f'{w} r6: no page errors', not pg.errs, str(pg.errs[:2])); await ctx.close()
            # round 6b: the Intel example in layout A: all five markers shown, each on its target, no sideways scroll
            ctx, pg = await page(b, w)
            await pg.evaluate("MKL.S.lay='a'; MKL.S.fl='left'; MKL.apply(); itExOpen(true)"); await pg.wait_for_timeout(1500)
            ex = await pg.evaluate("""(()=>{ const f=document.querySelector('#intelPanel .itx'); if(!f) return null; const m=(n)=>f.querySelector(`[data-itx-mk="${n}"]`);
              const on=(n,el)=>{ const a=m(n); if(!a||a.hidden||!el) return false; const r=a.getBoundingClientRect(), q=el.getBoundingClientRect(); return r.right>q.left-20 && r.left<q.right+20 && r.bottom>q.top-20 && r.top<q.bottom+20; };
              const top=(n)=>{ const a=m(n).getBoundingClientRect(), h=document.elementFromPoint(a.left+a.width/2, a.top+a.height/2); return !!h && (h===m(n) || m(n).contains(h)); };
              return {m1: on(1, f.querySelector('.itx-feed .it-fd.rep')), m2: on(2, f.querySelector('.itx-near .it-nb')), m3: on(3, f.querySelector('.itx-map img[src]')), m4: on(4, f.querySelector('.itx-near .it-nb.alert')), m5: on(5, f.querySelector('.itx-near .it-kl')),
                above: [1,2,3,4,5].every(n=>getComputedStyle(m(n)).visibility==='visible') && +getComputedStyle(m(2)).zIndex > +getComputedStyle(f.querySelector('.it-nearcol')).zIndex, picture: !!f.querySelector('.itx-map img[src]'), phoneNote: !/switch .* to Map/.test(f.textContent)}; })()""")
            ok(f'{w} r6b: the Intel example shows all five markers on their targets (map picture drawn, no "switch to Map" note)', bool(ex) and all(ex.values()), str(ex))
            sw = await pg.evaluate('document.documentElement.scrollWidth - innerWidth'); ok(f'{w} r6b example: no sideways scroll', sw <= 0, f'sw={sw}')
            await pg.screenshot(path=f'{OUT}/example_{w}.png', full_page=True)
            ok(f'{w} r6b example: no page errors', not pg.errs, str(pg.errs[:2])); await ctx.close()
        await b.close()
    bad = [n for n, c in res if not c]; print(f'{len(res)} checks, {len(bad)} failed'); sys.exit(1 if bad else 0)
asyncio.run(main())
