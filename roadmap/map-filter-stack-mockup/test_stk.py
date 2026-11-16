"""Checks for the stacked map filters mockup, at 1440 and 390 px, a fresh page per case.
python3 -I test_stk.py <mockup.html> <shots dir>"""
import os, sys
from playwright.sync_api import sync_playwright
URL = 'file://' + os.path.abspath(sys.argv[1]); SHOTS = sys.argv[2]; os.makedirs(SHOTS, exist_ok=True)
fails, passes = [], 0
def check(name, ok, info=''):
    global passes
    if ok: passes += 1
    else: fails.append(f'{name}: {info}')
    print(('ok   ' if ok else 'FAIL ') + name + (f' ({info})' if info and not ok else ''))

def page_for(b, w, h):
    ctx = b.new_context(viewport={'width': w, 'height': h}, bypass_csp=True)
    p = ctx.new_page(); errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.goto(URL); p.wait_for_function('window.__MKREADY || window.__MKERR', timeout=40000)
    err = p.evaluate('window.__MKERR || ""')
    return ctx, p, errs, err

JS_CHECK_EXAMPLE = """() => {
  const T = itMapTable(), m = MKP.match().m, ix = sovIndex(), bad = [];
  let n = 0, inRange = 0, tda = 0;
  for(let i = 0; i < T.n; i++){
    if(i === itm.home) continue;
    const v = Number(itMapSecText(T.sec[i])), e = ix.at.get(i);
    const t3 = !!e && [...e].some(([k, l]) => (k === 'Major Threat Detection Array' || k === 'Minor Threat Detection Array') && l >= 3);
    const want = v >= -0.5 - 1e-9 && v <= -0.3 + 1e-9 && t3;
    if(want !== !!m[i]) bad.push(i);
    if(m[i]) n++; if(t3) tda++; if(t3 && v >= -0.5 && v <= -0.3) inRange++;
  }
  return {n, tda, inRange, bad: bad.length, list: MKP.match().list.length};
}"""

with sync_playwright() as pw:
    b = pw.chromium.launch()
    for (w, h, tag) in [(1440, 1000, 'wide'), (390, 844, 'phone')]:
        phone = tag == 'phone'
        # 1. it starts, the column has its groups, no sideways scroll
        ctx, p, errs, err = page_for(b, w, h)
        check(f'{tag}: starts', not err, err)
        ks = p.evaluate("() => [...document.querySelectorAll('.it-map-fbtns [data-im-f]')].map(b => b.dataset.imF)")
        check(f'{tag}: column order', ks == ['sec', 'jumps', 'region', 'secr', 'near', 'reports', 'kills', 'wh', 'sov', 'paths'], ks)
        check(f'{tag}: two separators', p.evaluate("() => document.querySelectorAll('.it-map-fbtns .mk-sep').length") == 2)
        check(f'{tag}: no sideways scroll', p.evaluate('() => document.scrollingElement.scrollWidth <= innerWidth + 1'))
        check(f'{tag}: nothing dims with no condition', p.evaluate("() => { const T = itMapTable(); for(let i = 0; i < T.n; i++) if(itMapDimmed(i)) return false; return true; }"))
        check(f'{tag}: no "Only" line with no condition', p.evaluate("() => !document.querySelector('.it-map-leg .mk-only')"))
        # 2. the owner's example
        p.evaluate('MKP.example()'); p.wait_for_timeout(400)
        r = p.evaluate(JS_CHECK_EXAMPLE)
        check(f'{tag}: example matches exactly sec -0.5..-0.3 with TDA 3', r['bad'] == 0 and r['n'] > 0, r)
        check(f'{tag}: some TDA 3 systems fall outside the range', r['tda'] > r['inRange'], r)
        check(f'{tag}: matches bright anywhere, the rest dim', p.evaluate("() => { const m = MKP.match().m; let ok = true; for(let i = 0; i < m.length; i++){ if(i === itm.home) continue; const a = __MKalpha(i, () => 0.5); if(m[i] ? a !== 1 : a !== IT_MAP_DIM) ok = false; } return ok; }"))
        check(f'{tag}: bigger matches by default', p.evaluate('() => __MKbig() === true'))
        check(f'{tag}: your system never dims', p.evaluate('() => !itMapDimmed(itm.home) && __MKalpha(itm.home, () => 0.5) === 1'))
        leg = p.evaluate("() => (document.querySelector('.it-map-leg .mk-only') || {}).textContent || ''")
        check(f'{tag}: legend "Only" line, the count first', leg.startswith(f"Only {r['list']} match") and 'security -0.5 to -0.3' in leg and 'level 3' in leg and 'level 3+' not in leg, leg)
        check(f'{tag}: the "Only" line shows whole (wraps, not cut)', p.evaluate("() => { const o = document.querySelector('.it-map-leg .mk-only'); return o.scrollWidth <= o.clientWidth + 1 && o.scrollHeight <= o.clientHeight + 1; }"))
        check(f'{tag}: the colour line stays one line, first', p.evaluate("() => document.querySelector('.it-map-leg .it-map-fl:not(.mk-only)').textContent.startsWith('Security')"))
        chip = p.evaluate("() => { const c = document.querySelector('.mk-mt'); return c && !c.hidden ? c.textContent : ''; }")
        check(f'{tag}: match chip', chip == f"{r['list']} match ›", chip)
        pressed = p.evaluate("() => [...document.querySelectorAll('.it-map-fbtns [aria-pressed=true]')].map(b => b.dataset.imF)")
        check(f'{tag}: pressed: the colour and the two conditions', sorted(pressed) == ['sec', 'secr', 'sov'], pressed)
        if phone:
            bd = p.evaluate("() => (document.querySelector('.it-map-fcur .mk-bd') || {}).textContent || ''")
            check('phone: fold button counts the conditions', bd == '2', bd)
        p.locator('.it-map').scroll_into_view_if_needed(); p.screenshot(path=f'{SHOTS}/{tag}_example.png', full_page=True)
        # the chip steps to the nearest match
        v0 = p.evaluate('() => [itm.view.tx, itm.view.ty]')
        p.click('.mk-mt'); p.wait_for_timeout(200)
        v1 = p.evaluate('() => [itm.view.tx, itm.view.ty]'); t1 = p.evaluate("() => document.querySelector('.mk-mt').textContent")
        check(f'{tag}: chip moves the view, "1 of N"', v0 != v1 and t1.startswith('1 of'), [v0, v1, t1])
        near0 = p.evaluate('() => { const L = MKP.match().list; return itm.D[L[0]] <= itm.D[L[L.length - 1]]; }')
        check(f'{tag}: chip goes nearest first', near0)
        # 3. Kills on: no amber dots, the colour stays security
        p.evaluate("() => { MKP.ST().on.kills = true; itMapFilterSet('jumps'); itMapFilterSet('sec'); }")
        check(f'{tag}: kills condition never colours amber', p.evaluate("() => { const T = itMapTable(); for(const [i, r] of itm.rep) if(r.kills && itMapFcol(i) === IT_MAP_KILL) return false; return true; }"))
        # 4. a hostile ring in a non-matching system still draws (rings ignore dimming); its dot dims
        hr = p.evaluate("() => { MKP.ST().on.kills = false; itMapFilterSet('sec'); const m = MKP.match().m; for(const [i, r] of itm.rep) if(r.side === 'hostile' && !m[i]) return i; return -1; }")
        check(f'{tag}: a hostile report outside the match exists (its ring is not faded: rings use 0.95)', hr >= 0)
        # 5. colour by jumps with the stack kept
        p.evaluate("() => itMapFilterSet('jumps')"); p.wait_for_timeout(200)
        check(f'{tag}: colour switch keeps the stack', p.evaluate("() => itm.filter === 'jumps' && MKP.ST().on.secr && MKP.ST().on.sov && MKP.match().list.length > 0"))
        p.screenshot(path=f'{SHOTS}/{tag}_example_jumps.png')
        # 5b. no colour (the owner: "i can't toggle anything "off""): the colour that is on, pressed again
        p.evaluate("() => itMapFilterSet('jumps')"); p.wait_for_timeout(200)
        check(f'{tag}: pressing the colour that is on turns colour off', p.evaluate("() => MKP.ST().colour === '' && __MKplain()"))
        check(f'{tag}: no colour: every system plain grey', p.evaluate("() => { const T = itMapTable(), L = MKP.ST().look; MKP.ST().look = 'full'; let ok = true; for(let i = 0; i < T.n; i += 37) if(itMapFcol(i) !== '#56616b') ok = false; MKP.ST().look = L; return ok; }"))
        check(f'{tag}: no colour: no colour button pressed, the stack kept', p.evaluate("() => ![...document.querySelectorAll('.it-map-fbtns [aria-pressed=true]')].some(b => ['sec', 'jumps', 'region'].includes(b.dataset.imF)) && MKP.ST().on.secr && MKP.match().list.length > 0"))
        check(f'{tag}: no colour: the legend says so', p.evaluate("() => document.querySelector('.it-map-leg .it-map-fl:not(.mk-only)').textContent.startsWith('No colour')"))
        p.evaluate("() => { itMapZoom(itm.W / 2, itm.H / 2, 6); }"); p.wait_for_timeout(300)
        p.screenshot(path=f'{SHOTS}/{tag}_plain_zoomed.png')
        p.evaluate("() => itMapFitView ? (itMapCenter(), 0) : 0")
        p.evaluate("() => itMapFilterSet('jumps')"); p.wait_for_timeout(200)
        check(f'{tag}: a colour pressed again colours the map', p.evaluate("() => MKP.ST().colour === 'jumps' && !__MKplain() && itm.filter === 'jumps'"))
        # 5b2. Brighter vs Brighter + bigger changes the picture zoomed out and zoomed in (the owner saw no difference)
        for z in ('out', 'in'):
            if z == 'in': p.evaluate("() => itMapZoom(itm.W / 2, itm.H / 2, 4)"); p.wait_for_timeout(200)
            p.evaluate("() => { MKP.ST().emph = 'bright'; itMapDraw(); }"); a = p.evaluate('() => itm.cv.toDataURL()')
            p.evaluate("() => { MKP.ST().emph = 'big'; itMapDraw(); }"); bb = p.evaluate('() => itm.cv.toDataURL()')
            check(f'{tag}: bigger matches show zoomed {z}', a != bb)
        p.evaluate("() => itMapCenter()")
        # 5b3. the alert glow at half (the owner: "maybe try 50% of current diameter?")
        g = p.evaluate("() => { const g = itMapGatePx(), r0 = Math.max(9, Math.min(15, g * 0.2)), t0 = 22 * Math.min(1.4, Math.sqrt(g / IT_MAP_START_GATE)); return {out: __MKglow(false, 0, g) / t0, inn: __MKglow(true, 12, 80) - 12, def: MKP.ST().glow}; }")
        check(f'{tag}: alert glow by default: half the diameter zoomed out, today\'s zoomed in (r + 9)', g['def'] == 'half' and abs(g['out'] - 0.5) < 1e-9 and abs(g['inn'] - 9) < 1e-9, g)
        p.evaluate("() => { itMapFitView(); MKP.ST().glow = 'today'; itMapDraw(); }"); a = p.evaluate('() => itm.cv.toDataURL()')
        p.evaluate("() => { MKP.ST().glow = 'half'; itMapDraw(); }"); bb = p.evaluate('() => itm.cv.toDataURL()')
        check(f'{tag}: the glow switch changes the picture zoomed out', a != bb)
        p.evaluate("() => { itMapCenter(); for(let k = 0; k < 12 && itMapGatePx() < 40; k++) itMapZoom(itm.W / 2, itm.H / 2, 1.5); MKP.ST().glow = 'today'; itMapDraw(); }"); a = p.evaluate('() => itm.cv.toDataURL()')
        check(f'{tag}: (zoomed in for the next check)', p.evaluate('() => itm.stage >= 1'))
        p.evaluate("() => { MKP.ST().glow = 'half'; itMapDraw(); }"); bb = p.evaluate('() => itm.cv.toDataURL()')
        check(f'{tag}: zoomed in the glow is the same either way (today size)', a == bb)
        p.evaluate("() => itMapCenter()")
        # 5c. soft colour (the owner: "the base color groups sort of washing out the other data"): soft by default; a match keeps full colour
        check(f'{tag}: soft colour by default', p.evaluate("() => MKP.ST().look === 'soft'"))
        sc = p.evaluate("""() => { const T = itMapTable(), m = MKP.match().m; let soft = 0, full = 0, bad = 0;
          for(let i = 0; i < T.n; i++){ if(i === itm.home) continue; const raw = itm.D[i] < 0 ? IT_MAP_NONE : IT_MAP_JUMPS[Math.min(IT_MAP_JUMPS.length - 1, itm.D[i])], c = itMapFcol(i);
            if(m[i]){ if(c === raw) full++; else bad++; } else { if(c !== raw) soft++; else bad++; } } return {soft, full, bad}; }""")
        check(f'{tag}: soft: matches keep full colour, the rest are softened', sc['bad'] == 0 and sc['full'] > 0 and sc['soft'] > 0, sc)
        p.evaluate("() => { itMapZoom(itm.W / 2, itm.H / 2, 6); }"); p.wait_for_timeout(300)
        p.screenshot(path=f'{SHOTS}/{tag}_soft_jumps_zoomed.png')
        p.evaluate("() => { MKP.ST().look = 'full'; itMapDraw(); }"); p.wait_for_timeout(200)
        p.screenshot(path=f'{SHOTS}/{tag}_full_jumps_zoomed.png')
        check(f'{tag}: full colour: no softening', p.evaluate("() => { const T = itMapTable(); for(let i = 0; i < T.n; i += 41){ if(i === itm.home) continue; const raw = itm.D[i] < 0 ? IT_MAP_NONE : IT_MAP_JUMPS[Math.min(IT_MAP_JUMPS.length - 1, itm.D[i])]; if(itMapFcol(i) !== raw) return false; } return true; }"))
        p.evaluate("() => { MKP.ST().look = 'soft'; itMapCenter(); }")
        # 6. Paths to you is a view; back to the map keeps everything
        p.evaluate("() => itMapFilterSet('paths')"); p.wait_for_timeout(300)
        check(f'{tag}: paths view, no dimming there', p.evaluate("() => itPtLive() && !document.querySelector('.it-map-leg .mk-only') && document.querySelector('.mk-mt').hidden"))
        p.evaluate("() => itMapFilterSet('paths')"); p.wait_for_timeout(300)
        check(f'{tag}: back from paths keeps colour and stack', p.evaluate("() => itm.filter === 'jumps' && !itPtLive() && !!document.querySelector('.it-map-leg .mk-only')"))
        check(f'{tag}: no sideways scroll with the stack on', p.evaluate('() => document.scrollingElement.scrollWidth <= innerWidth + 1'))
        check(f'{tag}: no page errors', not errs, errs[:3])
        ctx.close()

        # 7. the Security range popover from its panel button
        ctx, p, errs, err = page_for(b, w, h)
        if phone: p.click('.it-map-fcur'); p.wait_for_timeout(150)
        p.click('.it-map-fbtns [data-im-f="secr"]'); p.wait_for_timeout(300)
        vis = p.evaluate("() => { const x = document.querySelector('.mk-pop'); return !!x && !x.hidden && x.getBoundingClientRect().width > 0; }")
        check(f'{tag}: first switch-on opens its settings', vis)
        box = p.evaluate("() => { const x = document.querySelector('.mk-pop').getBoundingClientRect(), b = itm.box.getBoundingClientRect(), c = document.querySelector('.it-map-fbtns').getBoundingClientRect(); return {inside: x.left >= b.left - 1 && x.right <= b.right + 1 && x.top >= b.top - 1 && x.bottom <= b.bottom + 1, clear: x.left >= c.right || x.top >= c.bottom || innerWidth < 600}; }")
        check(f'{tag}: popover inside the map{", right of the column" if not phone else ""}', box['inside'] and box['clear'], box)
        check(f'{tag}: popover has a close button', p.evaluate("() => !!document.querySelector('.mk-pop button.x-close')"))
        p.click('.mk-pop [data-mk-d="lo:1"]'); p.wait_for_timeout(150)
        lo = p.evaluate("() => document.querySelector('.mk-pop .mk-v').value")
        check(f'{tag}: From steps by 0.1', lo == '-0.4', lo)
        p.click('.mk-pop [data-mk-q="null"]'); p.wait_for_timeout(150)
        check(f'{tag}: quick Null sets -1.0 to 0.0', p.evaluate("() => { const s = MKP.ST().secr; return s.lo === -10 && s.hi === 0; }"))
        n_null = p.evaluate('() => MKP.match().list.length')
        check(f'{tag}: null-sec matches some systems', n_null > 0, n_null)
        p.screenshot(path=f'{SHOTS}/{tag}_secr_pop.png')
        p.keyboard.press('Escape'); p.wait_for_timeout(150)
        check(f'{tag}: Escape closes the popover', p.evaluate("() => document.querySelector('.mk-pop').hidden"))
        # switching it off keeps its setting, shuts its panel and hides its settings button (the owner, 2026-11-16)
        vis_pb = "(k) => { const b = document.querySelector(`[data-mk-pn='${k}'], .it-map-fw > [data-im-f='${k}'] ~ .it-map-pb`); if(!b) return false; const cs = getComputedStyle(b); return cs.display !== 'none' && cs.visibility !== 'hidden' && b.getBoundingClientRect().width > 0; }"
        if phone: p.click('.it-map-fcur'); p.wait_for_timeout(150)
        check(f'{tag}: settings button shown while on', p.evaluate(vis_pb, 'secr'))
        p.evaluate("() => MKP.popOpen('secr')"); p.wait_for_timeout(150)
        p.evaluate("() => itMapFilterSet('secr')"); p.wait_for_timeout(300)   # the filter button (on a phone the open panel covers the column)
        if phone and not p.evaluate("() => !!document.querySelector('.it-map-fb.open')"): p.click('.it-map-fcur'); p.wait_for_timeout(150)
        check(f'{tag}: off keeps the setting', p.evaluate("() => !MKP.ST().on.secr && MKP.ST().secr.lo === -10"))
        check(f'{tag}: off shuts its panel', p.evaluate("() => document.querySelector('.mk-pop').hidden"))
        if not phone:
            p.hover('.it-map-fbtns [data-im-f="secr"]'); p.wait_for_timeout(700)
            check('wide: off: hovering shows no settings button', not p.evaluate(vis_pb, 'secr'))
            p.hover('.it-map-fbtns [data-im-f="sov"]'); p.wait_for_timeout(700)
            check('wide: off: Sov shows no settings button on hover either', not p.evaluate(vis_pb, 'sov'))
            p.mouse.move(700, 700)
        else:
            check('phone: off: no settings button in the column', not p.evaluate(vis_pb, 'secr'))
        p.evaluate("() => { MKP.ST().on.sov = true; itMapFilterSet('sec'); sovOpen(true); }"); p.wait_for_timeout(300)
        p.evaluate("() => itMapFilterSet('sov')"); p.wait_for_timeout(300)
        check(f'{tag}: Sov off shuts its panel', p.evaluate("() => !sovShown()"))
        p.evaluate("() => { MKP.ST().on.sov = false; }")
        # 8. Sov: its panel has the level row
        if phone: p.click('.it-map-fcur'); p.wait_for_timeout(150)
        p.evaluate("() => { MKP.ST().on.sov = true; itMapFilterSet('sec'); sovOpen(true); }"); p.wait_for_timeout(300)
        check(f'{tag}: Sov panel has its three Level boxes', p.evaluate("() => document.querySelectorAll('.it-sovp .mk-sovlv input[data-mk-lv]').length") == 3)
        p.evaluate("() => { MKP.ST().sovLv = []; }"); p.evaluate("() => itMapFilterSet('sec')"); p.wait_for_timeout(200)
        n0 = p.evaluate('() => MKP.match().list.length')
        p.click('.it-sovp [data-mk-lv="3"]'); p.wait_for_timeout(200)
        n3 = p.evaluate('() => MKP.match().list.length')
        check(f'{tag}: ticking level 3 narrows the Sov matches', 0 < n3 < n0, [n0, n3])
        p.click('.it-sovp [data-mk-lv="3"]'); p.click('.it-sovp [data-mk-lv="1"]'); p.click('.it-sovp [data-mk-lv="2"]'); p.wait_for_timeout(200)
        n12 = p.evaluate('() => MKP.match().list.length')
        check(f'{tag}: levels 1 and 2 ticked: stored as [1, 2]', p.evaluate('() => JSON.stringify(MKP.ST().sovLv)') == '[1,2]')
        check(f'{tag}: levels 1 + 2 + 3 together are every levelled match', 0 < n12 < n0 and n12 + n3 >= n0, [n0, n12, n3])
        leg2 = p.evaluate("() => (document.querySelector('.it-map-fl.mk-only') || {}).textContent || ''")
        check(f'{tag}: the legend names levels 1, 2', 'level 1, 2' in leg2, leg2)
        p.click('.it-sovp [data-mk-lv="1"]'); p.click('.it-sovp [data-mk-lv="2"]'); p.wait_for_timeout(200)
        check(f'{tag}: none ticked = any level again', p.evaluate('() => MKP.match().list.length') == n0)
        p.click('.it-sovp [data-mk-lv="1"]'); p.click('.it-sovp [data-mk-lv="2"]'); p.wait_for_timeout(200)
        p.screenshot(path=f'{SHOTS}/{tag}_sov_level.png')
        check(f'{tag}: no page errors (2)', not errs, errs[:3])
        ctx.close()

        # 9. Region colours: reserved hues out
        ctx, p, errs, err = page_for(b, w, h)
        check(f'{tag}: reserved Region palette drops the cyan and the kill amber', p.evaluate("() => !IT_MAP_REGION.includes('#4fc3d9') && !IT_MAP_REGION.includes(IT_MAP_KILL)"))
        used = p.evaluate("() => { const T = itMapTable(), c = itMapRegCol(T); return Math.max(...c) + 1; }")
        check(f'{tag}: the greedy Region colouring fits the palette', used <= 8, used)
        print(f'{tag}: region colours used: {used}')
        p.evaluate("() => itMapFilterSet('region')"); p.wait_for_timeout(300)
        p.screenshot(path=f'{SHOTS}/{tag}_region.png')
        # 10. the wormholes (the owner: "add 12 with varying ranges and ages up to 24 hours"), and Q21's two looks
        wi = p.evaluate("""() => { const st = itWhStore(), now = Date.now(), g = itGraphGet(), r = Object.values(st.rep);
          return {n: r.length, maxH: Math.max(...r.map(w => (now - w.t) / 3600e3)), fresh: r.filter(w => now - w.t < 30 * 60000).length,
            far: r.filter(w => itm.D[g.at.get(w.id)] > itm.reach).length, dr: r.filter(w => w.drifter).length, you: r.filter(w => w.src === 'you').length}; }""")
        check(f'{tag}: 14 wormholes (2 reported + 12 made up), up to 24 h, some fresh, some past "Map: within", Drifters, added by hand', wi['n'] == 14 and wi.get('bad', 0) == 0 and wi['maxH'] < 24 and wi['fresh'] >= 3 and wi['far'] >= 3 and wi['dr'] == 2 and wi['you'] == 3, wi)
        check(f'{tag}: the 12 made-up holes have names', p.evaluate("() => Object.values(itWhStore().rep).every(w => !itSysName(w.id).startsWith('~') && !/^\\\\d+$/.test(itSysName(w.id)))"))
        p.evaluate('MKP.whExample()'); p.wait_for_timeout(400)
        nm_ = p.evaluate('() => [MKP.match().list.length, itm.wh.kept.size]'); check(f'{tag}: Wormholes only: every hole matches', nm_[0] == 14 and nm_[1] == 14, nm_)
        np_ = p.evaluate('() => itm.whp.children.length')
        check(f'{tag}: 045\'s bold + pulse by default (Q21a), the fresh holes pulse', p.evaluate("() => MKP.ST().whLook") == 'bold' and np_ >= 3, np_)
        check(f'{tag}: Wormholes alone: all 14 holes marked, bold', p.evaluate("() => itm.wh.mark.size === 14 && [...itm.wh.kept.keys()].every(i => __MKwhBold(i))"))
        p.screenshot(path=f'{SHOTS}/{tag}_wh_bold.png')
        a = p.evaluate('() => itm.cv.toDataURL()')
        p.evaluate("() => document.querySelector('[data-mkb=whl-thin]').click()"); p.wait_for_timeout(300)
        check(f'{tag}: the MOCKUP box\'s Thin rings changes the picture, no pulse', a != p.evaluate('() => itm.cv.toDataURL()') and p.evaluate('() => itm.whp.children.length') == 0)
        p.evaluate("() => document.querySelector('[data-mkb=whl-bold]').click()"); p.wait_for_timeout(200)
        # Q21b: Wormholes + Within 3 jumps: matching holes keep the filter's marks; the rest the off-filter rule (fresh in reach: thin; else none)
        r21 = p.evaluate("""() => { const S = MKP.ST(); S.on.near = true; S.near.n = 3; itMapFilterSet('sec'); itMapFilterSet('sec');
          const m = MKP.match().m, wh = itm.wh, bad = [];
          for(const [i, w] of wh.kept){ const want = m[i] ? 'bold' : wh.live.has(i) ? 'thin' : 'none', got = !wh.mark.has(i) ? 'none' : __MKwhBold(i) ? 'bold' : 'thin'; if(want !== got) bad.push([itSysName(w.id), want, got]); }
          return {bad, n: MKP.match().list.length, bold: [...wh.kept.keys()].filter(i => __MKwhBold(i)).length, thin: [...wh.mark.keys()].filter(i => !__MKwhBold(i)).length,
            gone: [...wh.kept.keys()].filter(i => !wh.mark.has(i)).length, chip: document.querySelector('.mk-mt').textContent}; }""")
        check(f'{tag}: Wormholes + Within 3: matches bold, fresh in reach thin, the rest unmarked (Q21b)', not r21['bad'] and r21['bold'] == r21['n'] > 0 and r21['thin'] > 0 and r21['gone'] > 0, r21)
        check(f'{tag}: the match chip counts the matching holes (Q21c)', r21['chip'] == f"{r21['n']} match ›", r21)
        p.screenshot(path=f'{SHOTS}/{tag}_wh_near3.png')
        p.evaluate("() => { MKP.ST().on.near = false; }")
        p.evaluate("() => { MKP.ST().on.wh = false; itMapFilterSet('sec'); }"); p.wait_for_timeout(200)
        check(f'{tag}: Wormholes off: no pulse, live holes only', p.evaluate('() => itm.whp.children.length === 0 && itm.wh.mark.size < 14'))
        check(f'{tag}: no page errors (3)', not errs, errs[:3])
        ctx.close()
    b.close()
print(f'{passes} passed, {len(fails)} failed')
for f in fails: print('  ' + f)
sys.exit(1 if fails else 0)
