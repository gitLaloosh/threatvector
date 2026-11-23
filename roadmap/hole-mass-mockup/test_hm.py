"""Checks for the Mass (crit or roll a hole) mockup: python3 -I test_hm.py hole_mass_mockup.html [shots dir]. A fresh page per width, 1440 and 390 px."""
import os, sys
from playwright.sync_api import sync_playwright
PAGE = 'file://' + os.path.abspath(sys.argv[1]); SHOTS = sys.argv[2] if len(sys.argv) > 2 else None
if SHOTS: os.makedirs(SHOTS, exist_ok=True)
fails, n = [], 0
def ok(c, what):
    global n; n += 1
    if not c: fails.append(what); print('FAIL', what)
def page(p, w, h):
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    pg = b.new_page(viewport={'width': w, 'height': h}, has_touch=w < 600, is_mobile=w < 600, bypass_csp=True); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(PAGE); pg.wait_for_function('window.__MKREADY || window.__MKERR', timeout=60000)
    ok(not pg.evaluate('window.__MKERR'), f'{w}: boot ' + str(pg.evaluate('window.__MKERR')))
    return b, pg, errs
def scene(pg, s, w):
    pg.evaluate(f"HMscene('{s}')"); pg.wait_for_timeout(350)
    if SHOTS: pg.evaluate("document.querySelector('.wh-box').scrollIntoView()"); pg.screenshot(path=os.path.join(SHOTS, f'{s}_{w}.png'))
def txt(pg): return pg.evaluate("(document.querySelector('.hm-pop') || {}).innerText || ''").replace('\n', ' | ')
def nohscroll(pg): return pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
with sync_playwright() as p:
    for w, h in [(1440, 900), (390, 844)]:
        b, pg, errs = page(p, w, h)
        # the button and the panel
        btn = pg.evaluate("(() => { const b = document.querySelector('.wh-ctl [data-wh-pop=mass]'); if(!b) return null; const r = b.getBoundingClientRect(); return [r.width, r.height, b.getAttribute('aria-expanded'), b.title]; })()")
        ok(btn and btn[2] == 'true' and 'crit or roll' in btn[3], f'{w}: the Mass button beside Add and Share, open {btn}')
        ok(btn and (w > 600 or (btn[0] >= 44 and btn[1] >= 44)), f'{w}: 44 px on a phone {btn}')
        t = txt(pg)
        ok('to Rens · B274' in t and 'D382 · mass <50%' in t and 'K162' in t and 'Another hole' in t, f'{w}: the focus system\'s connections to pick from {t[:200]}')
        ok('2,000,000 t total (1.8–2.2 million, ±10%) · up to 375,000 t a jump' in t, f'{w}: the hole line from IT_WH_LIFE {t[:400]}')
        ok('296,800 t hot (MWD on) · 196,800 t cold' in t and '1,650 t hot (MWD on)' in t, f'{w}: each ship shows its masses')
        ok(pg.evaluate("document.querySelectorAll('.hm-pop .x-close[data-wh-popx]').length") == 1, f'{w}: one close button')
        ok(nohscroll(pg), f'{w}: no sideways scroll (panel)')
        scene(pg, 'panel', w)
        # steps: one at a time, answers, branches
        scene(pg, 'steps', w); t = txt(pg)
        ok('1. Megathron, Heron out hot · J101524 → Rens · 298,450 t' in t and 'Hot: MWD on when you press jump.' in t, f'{w}: the first step in words {t[:400]}')
        ok('B274 to Rens · roll it, finish in' in t and 'Change' in t, f'{w}: the setup folds to one line while steps run')
        ok(pg.evaluate("document.querySelectorAll('.hm-ans button').length") == 4, f'{w}: four answers')
        if w < 600: ok(pg.evaluate("[...document.querySelectorAll('.hm-ans button')].every(b => b.getBoundingClientRect().height >= 44)"), f'{w}: answers 44 px')
        ok(pg.evaluate("!document.getElementById('hmBr').hidden") and 'More than 50%: Megathron, Heron in hot' in t, f'{w}: What\'s next open with its branches {t[-300:]}')
        pg.click('[data-hm=br]'); pg.wait_for_timeout(150)
        ok(pg.evaluate("document.getElementById('hmBr').hidden && document.querySelector('[data-hm=br]').getAttribute('aria-expanded') === 'false'"), f'{w}: the chevron folds the branches')
        pg.click('[data-hm=br]'); pg.wait_for_timeout(150)
        pg.click('[data-hm-say=stable]'); pg.wait_for_timeout(200); t = txt(pg)
        ok('2. Megathron, Heron in hot · Rens → J101524' in t and 'Megathron, Heron out hot More than 50%' in t, f'{w}: an answer moves to the next step {t[:400]}')
        ok(pg.evaluate("whLinkOf(HMJ.A, HMJ.RENS).mass") == 'stable', f'{w}: the answer sets the connection\'s Mass (Q7)')
        scene(pg, 'next', w); t = txt(pg)
        ok('4. Megathron, Heron in hot' in t and 'Wait until' not in t and t.count('More than 50%:') == 0 and 'Less than 50%:' in t, f'{w}: only answers that can happen are branched {t[-250:]}')
        # Undo: takes the last answer back, the connection's Mass too; off with no answers
        ok(pg.evaluate("!document.querySelector('[data-hm=undo]').disabled"), f'{w}: Undo on after answers')
        pg.click('[data-hm-say=reduced]'); pg.wait_for_timeout(150)
        ok(pg.evaluate("whLinkOf(HMJ.A, HMJ.RENS).mass") == 'reduced', f'{w}: an answer set the Mass')
        pg.click('[data-hm=undo]'); pg.wait_for_timeout(150); t = txt(pg)
        ok('4. Megathron, Heron in hot' in t and pg.evaluate("whLinkOf(HMJ.A, HMJ.RENS).mass") == 'stable' and pg.evaluate("HM.pl.hist.length") == 3, f'{w}: Undo shows step 4 again, Mass as it was {t[:300]}')
        for _ in range(3): pg.click('[data-hm=undo]'); pg.wait_for_timeout(80)
        ok('1. Megathron, Heron out hot' in txt(pg) and pg.evaluate("document.querySelector('[data-hm=undo]').disabled"), f'{w}: back to step 1, Undo off')
        scene(pg, 'rolled', w); pg.click('[data-hm=undo]'); pg.wait_for_timeout(150); t = txt(pg)
        ok(pg.evaluate('HM.pl.hist.length') == 7 and '8. ' in t and pg.evaluate("!document.querySelector('.hm-fin') && !document.querySelector('[data-wh-ask=hmrm]')"), f'{w}: Undo after "It\'s gone" reopens the last step {t[:500]}')
        scene(pg, 'pol', w); t = txt(pg)
        ok('Wait until' in t and 'polarized' in t, f'{w}: polarization: the same way within 5 minutes waits {t[:600]}')
        # no safe step; adding a ship and carrying on
        scene(pg, 'risky', w); t = txt(pg)
        ok('no safe step left' in t.lower() and 'A ship under 119,200 t can do the last trip safely' in t and pg.evaluate("document.querySelectorAll('.hm-ans button').length") == 0, f'{w}: no safe step: says so, the safe mass, no answer buttons {t[:700]}')
        ok('3 earlier steps' in t, f'{w}: older jumps fold into a line')
        # Start over: asks while jumps were made, then back to the setup from what the hole says now
        scene(pg, 'next', w); pg.click('[data-hm=reset]'); pg.wait_for_timeout(150); t = txt(pg)
        ok('Start over? The 3 steps so far are forgotten' in t, f'{w}: Start over asks first {t[:300]}')
        pg.click('[data-wh-ask=hmrskeep]'); pg.wait_for_timeout(150)
        ok(pg.evaluate("(() => { const p = document.querySelector('.hm-pop').getBoundingClientRect(); return [...document.querySelectorAll('.hm-sum button')].every(b => { const r = b.getBoundingClientRect(); return r.left >= p.left && r.right <= p.right; }); })()"), f'{w}: Undo, Change and Start over fit inside the panel')
        ok(pg.evaluate("(() => { const b = document.querySelector('[data-hm=reset]').getBoundingClientRect(), p = document.querySelector('.hm-pop').getBoundingClientRect(); return b.top >= p.top && b.bottom <= p.bottom; })()"), f'{w}: Start over stays in view while the steps scroll')
        ok('4. Megathron, Heron in hot' in txt(pg), f'{w}: Keep going keeps the steps')
        pg.click('[data-hm=reset]'); pg.wait_for_timeout(100); pg.click('[data-wh-ask=hmrs]'); pg.wait_for_timeout(150); t = txt(pg)
        ok('Show the steps' in t and pg.evaluate("document.querySelector('[data-hm=st]').value") == 'stable' and pg.evaluate("document.querySelector('[data-hm-ship=\"0\"]').value") == 'fit:mf1', f'{w}: Start over: setup kept, it says now = the last answer {t[:200]}')
        scene(pg, 'rolled', w); pg.click('[data-hm=reset]'); pg.wait_for_timeout(150)
        ok('Show the steps' in txt(pg), f'{w}: Start over after the end: no question')
        # finisher: stays home while another safe step exists
        scene(pg, 'panel', w)
        pg.check('[data-hm-fin="1"]'); pg.wait_for_timeout(150)
        ok(pg.evaluate("HM.ships[1].fin === true && JSON.parse(localStorage.getItem('tvWhMass')).ships[1].fin === true"), f'{w}: the Finisher tick is kept with the ship row')
        pg.select_option('[data-hm-ship="1"]', 'fit:mf2'); pg.wait_for_timeout(150)
        ok(pg.evaluate("HM.ships[1].fin === true"), f'{w}: changing the ship keeps its Finisher tick')
        scene(pg, 'fin', w); t = txt(pg)
        ok('Phobos (finisher)' in t and '1. Megathron ×2 out hot' in t, f'{w}: the finisher stays home on step 1 {t[:400]}')
        scene(pg, 'fin5', w); t = txt(pg)
        ok('Phobos out' not in t.split('What’s next')[0] and 'Less than 10%: Phobos out cold, ZPME on' in t, f'{w}: the finisher waits for less than 10%, then goes with the ZPME {t[:900]}')
        ok(pg.evaluate("""(() => { HMscene('fin'); let bad = 0, used = 0;
            for(let k = 0; k < 40; k++){ const q = hmClone(HM.pl); const t = q.P[Math.floor(k * q.P.length / 40)]; let R = t[1], now = Date.now();
              for(let j = 0; j < 80; j++){ const st = hmNext(q, now); if(!st || st.none) break;
                if(st.g.some(x => q.ships[x.i].fin)) used++;
                if(st.risk === 0 && st.g.some(x => q.ships[x.i].fin) && q.ships.every(s => !s.fin || s.at === q.fin)){ const c = hmClone(q); c.ships = c.ships.map(s => s.fin ? {...s, modes: []} : s); const alt = hmNext(c, now); if(alt && !alt.none && alt.risk === 0) bad++; }
                R -= st.m; now += 6 * 60e3; hmApply(q, st, hmSt(t[0], R), now); if(q.done) break; } }
            window.__fin = {bad, used}; return bad === 0 && used > 0; })()"""), f'{w}: the finisher only goes when no safe step without it exists (40 holes) ' + str(pg.evaluate('window.__fin')))
        # a light finisher is kept for the end: the heavy ship's least risky trip, with the finisher offered
        scene(pg, 'heron', w); t = txt(pg)
        ok('1. Megathron out cold' in t and 'Heron (finisher) is kept for the end.' in t and 'Send Heron instead: safe, about' in t, f'{w}: before the end the finisher waits; the safe finisher trip is offered {t[:700]}')
        ok('A ship under 185,900 t would be safe.' in t, f'{w}: the safe mass is rounded down to 100 t {t[:700]}')
        pg.click('[data-hm=finnow]'); pg.wait_for_timeout(150); t = txt(pg)
        ok('1. Heron out hot' in t, f'{w}: Send Heron instead uses it {t[:400]}')
        pg.click('[data-hm=undo]'); pg.wait_for_timeout(150)
        ok('1. Megathron out cold' in txt(pg), f'{w}: Undo takes the choice back')
        scene(pg, 'addship', w); t = txt(pg)
        ok('Carry on (6 steps so far)' in t and 'Start over' in t, f'{w}: Change keeps the jumps so far {t[-200:]}')
        scene(pg, 'carried', w); t = txt(pg)
        ok(pg.evaluate("document.querySelector('[data-hm=undo]').disabled") and pg.evaluate("document.querySelector('[data-hm=undo]').textContent") == 'Undo', f'{w}: Carry on starts a new run: nothing to undo yet')
        ok('7. Phobos out hot · J101524 → Rens' in t, f'{w}: carrying on: the new ship takes the next trip {t[:600]}')
        # K162: asks the far side's type; no K162 in its list
        scene(pg, 'k162', w)
        ph = pg.evaluate("(document.querySelector('[data-hm=ty]') || {}).placeholder || ''")
        ok('K162: what’s the type on the other side' in ph, f'{w}: K162 with no far side asks {ph!r}')
        ok(pg.evaluate("!document.querySelector('#hmTyDl option[value=K162]') && document.querySelectorAll('#hmTyDl option').length > 90"), f'{w}: its list leaves K162 out')
        ok(pg.evaluate("document.querySelector('[data-hm=go]').disabled"), f'{w}: no steps until a type is known')
        pg.fill('[data-hm=ty]', 'h296'); pg.dispatch_event('[data-hm=ty]', 'change'); pg.wait_for_timeout(200); t = txt(pg)
        ok('H296 → C5 · 3,300,000 t total' in t and 'up to 2,000,000 t a jump' in t, f'{w}: a typed type fills the hole line {t[:500]}')
        # crit: never a step that can close it
        scene(pg, 'crit', w); t = txt(pg)
        ok('crit it' in t and '1. Phobos, Heron out hot' in t, f'{w}: crit from the D382 connection (less than 50%) {t[:400]}')
        ok(pg.evaluate("""(() => { let bad = 0; for(let k = 0; k < 40; k++){ const q = hmClone(HM.pl); const t = q.P[Math.floor(k * q.P.length / 40)]; let R = t[1], now = Date.now();
            for(let j = 0; j < 80; j++){ const st = hmNext(q, now); if(!st || st.none || st.risk > 0) break; R -= st.m; now += 6 * 60e3; const o = hmSt(t[0], R); if(o === 'gone'){ bad++; break; } hmApply(q, st, o, now); if(q.done) break; } } return bad; })()""") == 0,
           f'{w}: crit: no shown-as-safe step ever closes the hole (40 holes)')
        # roll: shown-as-safe steps never strand anyone
        ok(pg.evaluate("""(() => { HMscene('other'); const out = {stranded: 0, rolled: 0, stop: 0};
            for(const fin of ['this', 'other']){ HM.fin = fin; HM.st = 'fresh'; hmGo(false); for(let k = 0; k < 60; k++){ const q = hmClone(HM.pl); const t = q.P[Math.floor(k * q.P.length / 60)]; let R = t[1], now = Date.now();
              for(let j = 0; j < 80; j++){ const st = hmNext(q, now); if(!st || st.none || st.risk > 0){ out.stop++; break; } R -= st.m; now += 6 * 60e3; hmApply(q, st, hmSt(t[0], R), now); if(q.done){ out[q.done === 'rolled' ? 'rolled' : 'stranded']++; break; } } } }
            window.__sim = out; return out.stranded === 0 && out.rolled > 0; })()"""), f'{w}: roll, both finish sides: no stranding on safe steps ' + str(pg.evaluate('window.__sim')))
        scene(pg, 'other', w); t = txt(pg)
        ok('1. Megathron, Phobos in hot · J101524 → Rens' in t, f'{w}: finishing in Rens: the jump to Rens is "in" {t[:400]}')
        scene(pg, 'group', w); t = txt(pg)
        ok('1. Megathron ×2, Phobos out hot · J101524 → Rens · 631,600 t' in t, f'{w}: same ships and mode together in one step {t[:400]}')
        scene(pg, 'group3', w); t = txt(pg)
        ok('Megathron (cold) + Phobos (cold, ZPME on) out' in t, f'{w}: mixed modes counted per ship {t[:900]}')
        ok('This can close it: jump lightest first, Megathron (hot) last.' in t, f'{w}: a group that can close it says who goes last')
        scene(pg, 'other', w); t = txt(pg)
        ok('finish in Rens' in t, f'{w}: finish on the other side {t[:200]}')
        # typed hull: an estimate, marked
        scene(pg, 'hull', w); t = txt(pg)
        ok('150,600 t hot (MWD on) · 100,600 t cold · hull only' in t, f'{w}: a typed hull: hull + a MWD of its size, marked {t[:900]}')
        # rolled: done, asks before removing the connection
        scene(pg, 'rolled', w); t = txt(pg)
        ok('Rolled: the hole is gone and everyone is in J' in t and 'Remove the connection to Rens?' in t, f'{w}: rolled, and asks before removing {t[-300:]}')
        pg.click('[data-wh-ask=hmrm]'); pg.wait_for_timeout(250)
        ok(not pg.evaluate("whLinkOf(HMJ.A, HMJ.RENS)"), f'{w}: Remove takes the connection off the map')
        # kept in this browser; info text
        ok(pg.evaluate("JSON.parse(localStorage.getItem('tvWhMass')).ships.length") >= 1, f'{w}: ship rows kept (tvWhMass)')
        words = pg.evaluate("[CARD_INFO.whmass.join(' ').split(/\\s+/).length, CARD_INFO.whmass[0].split(/\\s+/).length, CARD_INFO.whmap.join(' ').split(/\\s+/).length]")
        ok(words[0] <= 210 and words[1] <= 85 and words[2] <= 410, f'{w}: info text within caps (whmass, its opening, whmap) {words}')
        ok(nohscroll(pg), f'{w}: no sideways scroll')
        ok(not errs, f'{w}: page errors {errs[:2]}')
        b.close()
print(f'{n - len(fails)} of {n} checks pass'); sys.exit(1 if fails else 0)
