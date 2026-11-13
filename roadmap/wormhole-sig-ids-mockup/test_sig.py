"""Signature IDs mockup checks, 1440 and 390 px: what the parser reads from each wormhole line, merging a part with the whole ID, the Feed,
Near You, the wormhole list and the map label; "Today" for comparison. python3 -I test_sig.py sig_mockup.html shots_sig/"""
import os, sys, time, json
from playwright.sync_api import sync_playwright
page_path, out = os.path.abspath(sys.argv[1]), sys.argv[2]
os.makedirs(out, exist_ok=True)
fails = []
def ok(c, what):
    print(('ok   ' if c else 'FAIL ') + what)
    if not c: fails.append(what)
SIGS = 'JSON.stringify(Object.fromEntries(Object.values(itWhStore().rep).map(w => [itSysName(w.id), (w.sigs || []).map(s => s.sig + (s.part ? "~" : "") + (s.type ? ":" + s.type : ""))])))'
PARSE = '''((m) => { const p = itParse(m, itMySys()); return JSON.stringify({whd: p.whd, sys: p.sys.map(s => itSysName(s.id)), left: p.W.filter((x, i) => !p.used[i]).map(x => x.w), runs: p.runs.map(r => r.map(i => p.W[i].w).join(' '))}); })'''
with sync_playwright() as p:
    b = p.chromium.launch()
    for W, H in ((1440, 1000), (390, 844)):
        ctx = b.new_context(viewport={'width': W, 'height': H}, bypass_csp=True, device_scale_factor=1)
        pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + page_path)
        pg.wait_for_function('window.__MKREADY || window.__MKERR', timeout=30000); time.sleep(4)
        ok(not pg.evaluate('window.__MKERR'), f'{W}: boot')
        if W > 600:   # the reader itself (once)
            cases = {
                'C-J6MT wh rzl-429 z971 class 1-3 medium size less then 1 day less then 50% mass': (['RZL-429'], 'Z971', 'C1-3'),
                'RERZ-L wh sig QDX': (['QDX'], '', ''),
                'SHBF-V 2 wh xyz-123 h296 and pqr-4 k162': (['XYZ-123', 'PQR-4'], 'H296', ''),
                'EUU-4N drifter hole BKT772': (['BKT-772'], '', ''),
                '8G-2FP wh lmn c3 fresh': (['LMN'], '', 'C3'),
                'RERZ-L wormhole QDX-581 n110 eol': (['QDX-581'], 'N110', ''),
            }
            INFO = {'C-J6MT wh rzl-429 z971 class 1-3 medium size less then 1 day less then 50% mass': {'life': 'lt1d', 'mass': 'reduced', 'size': 'medium', 'cls': 'C1-3'},
                    'RERZ-L wormhole QDX-581 n110 eol': {'life': 'eol'}, '8G-2FP wh lmn c3 fresh': {'cls': 'C3'}}
            for m, (sigs, typ, cls) in cases.items():
                r = json.loads(pg.evaluate(PARSE + f'({json.dumps(m)})'))
                d = r['whd'] or {'sigs': [], 'types': [], 'cls': ''}
                got = [s['sig'] for s in d['sigs']]
                ok(got == sigs and (not typ or d['sigs'][0]['type'] == typ) and d['cls'] == cls and not r['left'] and not r['runs'] and (d['sigs'][0].get('info') if d['sigs'] else None) == INFO.get(m),
                   f'reads “{m}” → {got} {[s["type"] for s in d["sigs"]]} {d["cls"]!r} {[s.get("info") for s in d["sigs"]]}; left {r["left"]}; pilot runs {r["runs"]}; systems {r["sys"]}')
            for m, want in [('X wh abc-123 <4h crit', {'life': 'eol', 'mass': 'critical'}), ('X wh abc-123 end of life', {'life': 'eol'}), ('X wh abc-123 frig hole', {'size': 'small'}), ('X wh abc-123 <1h', {'life': 'lt1h'}),
                            ('X wh abc-123 2 frigs on it', None), ('X wh abc-123 fresh', None), ('X wh abc-123 caps', None), ('X wh abc-123 >50% stable xl', {'mass': 'stable', 'size': 'xl'}),
                            ('X wh abc-123 reduced and crit', {'mass': 'critical'})]:
                r = json.loads(pg.evaluate(PARSE + f'({json.dumps(m.replace("X", "C-J6MT"))})'))
                got = r['whd']['sigs'][0].get('info') if r['whd'] and r['whd']['sigs'] else 'no sig'
                ok(got == want, f'life/mass/size only when plain: “{m}” → {got}')
            r = json.loads(pg.evaluate(PARSE + '("C-J6MT wh eol crit medium size")'))
            ok(r['whd']['info'] == {'life': 'eol', 'mass': 'critical', 'size': 'medium'} and not r['whd']['sigs'], f'no ID: kept with the report {r["whd"]["info"]}')
            r = json.loads(pg.evaluate(PARSE + '("C-J6MT rzl and class neuts")'))
            ok(r['whd'] is None, 'a line with no wormhole word reads as before (no IDs)')
            r = json.loads(pg.evaluate(PARSE + '("C-J6MT wh the bob")'))
            ok(not r['whd']['sigs'], 'an ordinary word after wh is not taken for an ID (“the”)')
        st = json.loads(pg.evaluate(SIGS))
        ok(st.get('C-J6MT') == ['MKV~', 'RZL-429:Z971'] and st.get('RERZ-L') == ['QDX~'] and st.get('SHBF-V') == ['XYZ-123:H296', 'PQR-4~:K162'], f'{W}: kept with the reports {st}')
        pg.evaluate('scrollTo(0, 0)'); pg.screenshot(path=f'{out}/{W}_1_intel.png', full_page=False)
        # more lines: a part grows into the whole ID; a part of a kept ID updates it
        for who, m in [['Mk Gate Watcher', 'RERZ-L wormhole QDX-581 n110 eol'], ['Mk Scout Alt', 'C-J6MT wh RZL crit now'], ['Mk Gate Watcher', 'SHBF-V wh pqr-417'], ['Mk Scout Alt', '8G-2FP wh lmn c3 fresh']]:
            pg.evaluate(f'window.__MKintel({json.dumps(who)}, {json.dumps(m)})')
        time.sleep(4)
        st = json.loads(pg.evaluate(SIGS))
        ok(st.get('RERZ-L') == ['QDX-581:N110'], f'{W}: the part QDX became QDX-581 ({st.get("RERZ-L")})')
        inf = json.loads(pg.evaluate('JSON.stringify(Object.fromEntries(Object.values(itWhStore().rep).map(w => [itSysName(w.id), (w.sigs || []).map(s => s.info || null)])))'))
        ok(inf.get('C-J6MT') == [{'life': 'lt1d', 'mass': 'critical', 'size': 'medium', 'cls': 'C1-3'}, {'mass': 'critical'}], f'{W}: “RZL crit” updated RZL-429’s mass, kept its life and size ({inf.get("C-J6MT")})')
        ok(inf.get('RERZ-L') == [{'life': 'eol'}], f'{W}: QDX-581 is EOL ({inf.get("RERZ-L")})')
        ok(st.get('C-J6MT') == ['RZL-429:Z971', 'MKV~'], f'{W}: “RZL” matched the kept RZL-429 ({st.get("C-J6MT")})')
        ok(st.get('SHBF-V') == ['PQR-417:K162', 'XYZ-123:H296'], f'{W}: PQR-4 became PQR-417, newest first ({st.get("SHBF-V")})')
        ok(st.get('8G-2FP') == ['LMN~'], f'{W}: a new system with a part ({st.get("8G-2FP")})')
        pg.evaluate('window.__MKintel("Mk Gate Watcher", "SHBF-V wh xyz-456")'); time.sleep(3)
        pg.evaluate('window.__MKintel("Mk Gate Watcher", "SHBF-V wh sig xyz")'); time.sleep(3)
        st = json.loads(pg.evaluate(SIGS))
        ok(st.get('SHBF-V', [])[:3] == ['XYZ~', 'XYZ-456', 'PQR-417:K162'] and 'XYZ-123:H296' in st.get('SHBF-V', []), f'{W}: “xyz” fits two kept IDs, so it is kept on its own ({st.get("SHBF-V")})')
        n = pg.locator('#tabIntel .it-sig').count()
        ok(n >= 6, f'{W}: ID tags shown in Intel ({n})')
        pg.locator('[data-mk="raw"]').click(); time.sleep(.5)
        pg.evaluate('document.querySelector("#tabIntel .it-fd").scrollIntoView({block: "start"})'); time.sleep(.3)
        pg.screenshot(path=f'{out}/{W}_2_feed.png')
        # the wormhole list and the map label
        opened = pg.evaluate('(() => { const b = document.querySelector("[data-it-whl]"); if(!b) return false; b.click(); return true; })()')
        time.sleep(.6)
        ok(opened and pg.locator('.it-whp-rows .it-sig').count() >= 5, f'{W}: the wormhole list shows the IDs')
        pg.evaluate('(() => { const r = document.querySelector(".it-whp-rows"); if(r) r.scrollIntoView({block: "center"}); })()'); time.sleep(.3)
        pg.screenshot(path=f'{out}/{W}_3_list.png')
        # Drifter per hole: two Drifter holes and a plain one in EUU-4N; a later plain report doesn't clear it
        dr = json.loads(pg.evaluate('JSON.stringify((w => [w.drifter, w.drN, (w.sigs || []).map(s => s.sig + (s.dr ? "!" : ""))])(Object.values(itWhStore().rep).find(w => itSysName(w.id) === "EUU-4N")))'))
        ok(dr == [True, 2, ['XRT-331', 'KLM-204!', 'BKT-772!']], f'{W}: EUU-4N keeps two Drifter holes and a plain one, still Drifter {dr}')
        lab = pg.evaluate('itMapWhLabel(Object.values(itWhStore().rep).find(w => itSysName(w.id) === "EUU-4N"))')
        ok(lab.startswith('DRIFTER ×2 XRT-331 +2 ·'), f'{W}: map label “{lab}”')
        kinds = pg.evaluate('itWhKinds(Object.values(itWhStore().rep).find(w => itSysName(w.id) === "EUU-4N")).length')
        ok(kinds == 2 and pg.evaluate('JSON.stringify(itWhKinds(Object.values(itWhStore().rep).find(w => itSysName(w.id) === "EUU-4N")).map(k => k.dash))') == '[false,true]', f'{W}: EUU-4N’s ring is split in two (plain solid, Drifter dashed)')
        pg.evaluate('itMapFilterSet && itMapFilterSet("wh")'); time.sleep(1)
        pg.evaluate('(() => { const nv = document.querySelector(\'[data-it-nv="map"]\'); if(nv && nv.offsetParent && nv.getAttribute("aria-pressed") !== "true") nv.click(); })()'); time.sleep(.5)
        pg.evaluate('document.querySelector(".it-map, #tabIntel canvas").scrollIntoView({block: "start"})'); time.sleep(.4)
        pg.screenshot(path=f'{out}/{W}_6_split_ring.png')
        pg.evaluate('window.__MKintel("Mk Scout Alt", "8G-2FP drifter")'); time.sleep(3)
        pg.evaluate('window.__MKintel("Mk Scout Alt", "8G-2FP wh")'); time.sleep(3)
        d8 = json.loads(pg.evaluate('JSON.stringify((w => [w.drifter, !!w.drNoId])(Object.values(itWhStore().rep).find(w => itSysName(w.id) === "8G-2FP")))'))
        ok(d8 == [True, True], f'{W}: a Drifter report with no ID stays after a plain “wh” {d8}')
        # one ID's × in the list
        pg.evaluate('(() => { const nv = document.querySelector(\'[data-it-nv="map"]\'); if(nv && nv.offsetParent && nv.getAttribute("aria-pressed") !== "true") nv.click(); })()'); time.sleep(.4)   # a phone: the map side
        if not pg.evaluate('itWhListShown()'): pg.evaluate('itWhListOpen(true)'); time.sleep(.4)
        for sig in ('KLM-204', 'BKT-772'):
            pg.locator(f'[data-it-whsrm$="|{sig}"]').first.click(); time.sleep(.5)
        dr = json.loads(pg.evaluate('JSON.stringify((w => [w.drifter, w.drN, (w.sigs || []).map(s => s.sig)])(Object.values(itWhStore().rep).find(w => itSysName(w.id) === "EUU-4N")))'))
        ok(dr == [False, 0, ['XRT-331']], f'{W}: removing both Drifter IDs leaves the plain one, no longer Drifter {dr}')
        ok('Removed BKT-772 from EUU-4N' in pg.locator('.it-whp-msg').inner_text(), f'{W}: the list says what was removed')
        # each system's raw reports, under a chevron like Near You's
        pg.evaluate('(() => { const nv = document.querySelector(\'[data-it-nv="map"]\'); if(nv && nv.offsetParent && nv.getAttribute("aria-pressed") !== "true") nv.click(); })()'); time.sleep(.3)
        if not pg.evaluate('itWhListShown()'): pg.evaluate('itWhListOpen(true)'); time.sleep(.4)
        raws = pg.evaluate('(itWhStore().rep[30000772].raws || []).map(r => r.raw)')
        ok(len(raws) == 3 and raws[0] == 'C-J6MT wh RZL crit now' and raws[1] == 'C-J6MT wh sig MKV crit' and 'rzl-429 z971 class 1-3' in raws[2], f'{W}: C-J6MT keeps its 3 lines as typed, newest first {raws}')
        tg = pg.locator('[data-it-whraw="30000772"]')
        RB = '(() => { const b = document.querySelector(\'[data-it-whraw="30000772"]\').closest(".it-whp-r").querySelector(".it-whp-raws"); return [!!b.offsetParent, b.innerText]; })()'
        ok(tg.get_attribute('aria-expanded') == 'false' and not pg.evaluate(RB)[0], f'{W}: closed at first')
        tg.click(); time.sleep(.4)
        vis, txt = pg.evaluate(RB)
        ok(pg.locator('[data-it-whraw="30000772"]').get_attribute('aria-expanded') == 'true' and vis and 'Mk Scout Alt' in txt and 'medium size less then 1 day' in txt, f'{W}: the chevron shows who sent each line and the line')
        pg.evaluate('document.querySelector(\'[data-it-whraw="30000772"]\').scrollIntoView({block: "start"})'); time.sleep(.3)
        pg.screenshot(path=f'{out}/{W}_3b_raw_open.png')
        ok(pg.evaluate('document.activeElement && document.activeElement.dataset.itWhraw === "30000772"'), f'{W}: focus stays on the chevron')
        pg.locator('[data-it-whraw="30000772"]').click(); time.sleep(.3)
        ok(pg.locator('[data-it-whraw="30000772"]').get_attribute('aria-expanded') == 'false', f'{W}: and closes again')
        # adding by hand with every property
        pg.evaluate('(() => { const nv = document.querySelector(\'[data-it-nv="map"]\'); if(nv && nv.offsetParent && nv.getAttribute("aria-pressed") !== "true") nv.click(); })()'); time.sleep(.3)
        if not pg.evaluate('itWhListShown()'): pg.evaluate('itWhListOpen(true)'); time.sleep(.4)
        F = '.it-whp-add '
        pg.fill(F + 'input[name=sys]', 'Tama'); pg.fill(F + 'input[name=sig]', 'ghi-123'); pg.fill(F + 'input[name=ty]', 'c247'); time.sleep(.2)
        ok(pg.locator(F + 'output[name=dest]').inner_text() == '→ C3', f'{W}: the type shows where it leads as you type ({pg.locator(F + "output[name=dest]").inner_text()})')
        pg.select_option(F + 'select[name=life]', 'eol'); pg.select_option(F + 'select[name=mass]', 'reduced'); pg.select_option(F + 'select[name=size]', 'large')
        pg.evaluate('document.querySelector(".it-whp-add").scrollIntoView({block: "center"})'); time.sleep(.2)
        pg.screenshot(path=f'{out}/{W}_4a_add_form.png')
        pg.locator(F + 'button[type=submit]').click(); time.sleep(.6)
        tama = json.loads(pg.evaluate('JSON.stringify((w => w && [w.src, (w.sigs || []).map(s => [s.sig, s.part, s.type, s.info || null, s.src || ""])])(itWhStore().rep[30002813]))'))
        ok(pg.evaluate('(itWhStore().rep[30002813].raws || [])[0].k') == 'you' and 'Tama GHI-123 c247 EOL <4h mass <50% large' == pg.evaluate('(itWhStore().rep[30002813].raws || [])[0].raw'), f'{W}: an add by hand leaves a line too')
        ok(tama == ['you', [['GHI-123', False, 'C247', {'life': 'eol', 'mass': 'reduced', 'size': 'large'}, 'you']]], f'{W}: added Tama with every property {tama}')
        ok(pg.locator(F + 'input[name=sig]').input_value() == '' and 'GHI-123, C247 → C3, EOL <4h, mass <50%, large' in pg.locator('.it-whp-msg').inner_text(), f'{W}: the form clears and says what it added (“{pg.locator(".it-whp-msg").inner_text()}”)')
        pg.fill(F + 'input[name=sys]', 'C-J6MT'); pg.fill(F + 'input[name=sig]', 'rzl'); pg.select_option(F + 'select[name=mass]', 'stable'); pg.locator(F + 'button[type=submit]').click(); time.sleep(.6)
        rz = json.loads(pg.evaluate('JSON.stringify((itWhStore().rep[30000772].sigs || []).filter(s => s.sig.startsWith("RZL")).map(s => [s.sig, s.info]))'))
        ok(rz == [['RZL-429', {'life': 'lt1d', 'mass': 'stable', 'size': 'medium', 'cls': 'C1-3'}]], f'{W}: “RZL” added by hand updated RZL-429’s mass only {rz}')
        pg.fill(F + 'input[name=sys]', 'Tama'); pg.fill(F + 'input[name=sig]', 'jkl-555'); pg.check(F + 'input[name=dr]'); pg.locator(F + 'button[type=submit]').click(); time.sleep(.6)
        ok(pg.evaluate('(itWhStore().rep[30002813].sigs || []).find(s => s.sig === "JKL-555").dr === true && itWhStore().rep[30002813].drifter === true && itWhKinds(itWhStore().rep[30002813]).length === 2'), f'{W}: Drifter ticked with an ID marks that hole; Tama’s ring splits')
        pg.fill(F + 'input[name=sys]', 'Tama'); pg.fill(F + 'input[name=sig]', '1234'); pg.locator(F + 'button[type=submit]').click(); time.sleep(.4)
        ok(pg.locator(F + 'input[name=sig]').get_attribute('aria-invalid') == 'true' and 'three letters' in pg.locator('.it-whp-msg').inner_text(), f'{W}: a bad ID is refused at its field')
        for v, hint in [('1-3', 'class C1-3'), ('c13', 'class C13'), ('hs', 'leads to HS'), ('Thera', 'leads to Thera'), ('k162', '→ exit')]:
            pg.fill(F + 'input[name=ty]', v); time.sleep(.1)
            ok(pg.locator(F + 'output[name=dest]').inner_text() == hint, f'{W}: “{v}” reads as “{pg.locator(F + "output[name=dest]").inner_text()}”')
        pg.fill(F + 'input[name=sys]', 'Tama'); pg.fill(F + 'input[name=sig]', 'mno-1'); pg.fill(F + 'input[name=ty]', '1-3'); pg.locator(F + 'button[type=submit]').click(); time.sleep(.6)
        mno = pg.evaluate('JSON.stringify((itWhStore().rep[30002813].sigs || []).find(s => s.sig === "MNO-1"))')
        ok('"cls":"C1-3"' in mno and '"part":true' in mno and pg.locator('.it-whp-rows .it-sig', has_text='MNO-1').first.inner_text().replace('\n', ' ').count('C1-3') == 1, f'{W}: a class typed by hand is kept and shown on the ID’s tag {mno}')
        pg.fill(F + 'input[name=sys]', 'Tama'); pg.fill(F + 'input[name=sig]', ''); pg.fill(F + 'input[name=ty]', 'c9'); pg.locator(F + 'button[type=submit]').click(); time.sleep(.4)
        ok(pg.locator(F + 'input[name=ty]').get_attribute('aria-invalid') == 'true', f'{W}: “c9” is refused')
        pg.fill(F + 'input[name=sig]', ''); pg.fill(F + 'input[name=ty]', 'x999'); pg.locator(F + 'button[type=submit]').click(); time.sleep(.4)
        ok(pg.locator(F + 'input[name=ty]').get_attribute('aria-invalid') == 'true' and 'isn’t a type or class' in pg.locator('.it-whp-msg').inner_text(), f'{W}: an unknown type is refused at its field')
        pg.fill(F + 'input[name=ty]', ''); pg.fill(F + 'input[name=sys]', '')
        ok(pg.evaluate('document.scrollingElement.scrollWidth <= innerWidth + 1'), f'{W}: no sideways scroll with the add form')
        # the probe scan, pasted into the list (you're in C-J6MT)
        pg.locator('[data-mk="scan"]').click(); time.sleep(.9)
        pg.screenshot(path=f'{out}/{W}_4_scan_pasted.png')
        pg.locator('[data-it-whscan]').click(); time.sleep(.6)
        st = json.loads(pg.evaluate(SIGS)); msg = pg.locator('.it-whp-msg').inner_text()
        ok(st.get('C-J6MT') == ['RZL-429:Z971', 'MKV-118', 'NOP-907'], f'{W}: the scan completed MKV → MKV-118 and added NOP-907 ({st.get("C-J6MT")}); “{msg}”')
        sc = json.loads(pg.evaluate('JSON.stringify((itWhStore().rep[30000772].sigs || []).map(s => [s.sig, s.scan && s.scan.in, s.src || ""]))'))
        ok(sc == [['RZL-429', True, ''], ['MKV-118', True, ''], ['NOP-907', True, 'scan']], f'{W}: each marked in the scan {sc}')
        pg.evaluate('document.querySelector(".it-whp-rows").scrollIntoView({block: "center"})'); time.sleep(.3)
        pg.screenshot(path=f'{out}/{W}_5_scan_done.png')
        pg.evaluate('window.__MKintel("Mk Gate Watcher", "C-J6MT wh sig ABC")'); time.sleep(3)
        r = pg.evaluate('itWhScanApply("ABC-552\\tCosmic Signature\\tWormhole\\tUnstable Wormhole\\t100.0%\\t2 AU\\nABC-913\\tCosmic Signature\\t\\t\\t10%\\t9 AU")')
        st = json.loads(pg.evaluate(SIGS))
        ok('ABC~' in st.get('C-J6MT', []) and 'Still a part' in r, f'{W}: a part fitting two scanned IDs stays a part (“{r}”)')
        gone = pg.evaluate('(itWhStore().rep[30000772].sigs || []).filter(s => s.scan && !s.scan.in).map(s => s.sig)')
        ok('RZL-429' in gone and 'ABC' not in gone and pg.locator('.it-sig.gone').count() >= 1, f'{W}: IDs missing from the newer scan are shown as maybe closed ({gone})')
        ok('Nothing in that looks like' in pg.evaluate('itWhScanApply("hello there")'), f'{W}: a paste that isn’t a scan says so')
        lab = pg.evaluate('itMapWhLabel(itWhStore().rep[Object.keys(itWhStore().rep).find(k => itSysName(Number(k)) === "SHBF-V")])')
        ok(lab.startswith('WH XYZ… +3 ·'), f'{W}: map label “{lab}”')
        ok(pg.evaluate('document.scrollingElement.scrollWidth <= innerWidth + 1'), f'{W}: no sideways scroll')
        ok(not errs, f'{W}: no page errors {errs[:3]}')
        # Today, for comparison
        pg.goto('about:blank'); pg.goto('file://' + page_path + '#today')
        pg.wait_for_function('window.__MKREADY || window.__MKERR', timeout=30000); time.sleep(4)
        pg.locator('[data-mk="raw"]').click(); time.sleep(.4)
        pg.evaluate('document.querySelector("#tabIntel .it-fd").scrollIntoView({block: "start"})'); time.sleep(.3)
        pg.screenshot(path=f'{out}/{W}_0_today.png')
        ctx.close()
    b.close()
print('FAILS:', len(fails)); [print(' -', f) for f in fails]
