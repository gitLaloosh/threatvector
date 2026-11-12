"""Pilot Dossier in the Pilot Analyzer (v2026.10.14.90; roadmap/pilot-dossier-plan.md, D1-D3, D7).

    PYFA_SRC=/path/to/pyfa python3 -I tools/page_checks/dossier_check.py [index.html]   -> 'FAILURES: N' (must be 0)

The real page with ESI and zKillboard answered from sa_mocks.py: "Vesna Dossier" has 45 kills in five hulls at set gang
sizes (players on the killmail; an NPC on every kill that mustn't count), weapons, wingmates, victims, hours and systems,
and 3 losses (Vedmak, Curse, a capsule). Every number the dossier shows is worked out again here, in Python, from the mock
(sa_mocks.DOSSIER_ENTRIES), not from the page:
  * the header (45 kills, 3 losses), the switch's counts (All / Solo / Small gang / Fleet), the solo / gang split;
  * per hull, newest first (build queue 037; the count only breaks a tie): kills, the losses line, the gang-size bar (solo / small / fleet shares), the median gang size,
    the weapon, the wingmates' hulls (top 3), what they killed (top 2 ship classes); the capsule isn't a hull;
  * the Small gang switch: only those kills, "N of M", newest first by their newest kill of that size; Fleet the same;
  * active hours in the browser's own time zone (the page runs in Asia/Tokyo here, UTC+9), its label; usual systems;
  * the hull used last is shown first; a row with a loss shows its loss; a row with none shows their alliance's common fit
    (one zKillboard request for its losses), said as not theirs; no hull dropdown any more (D7);
  * the kills list asked once (the Last Kill line and the dossier share it);
  * a ship typed in: that hull's losses as before, the dossier under it with that row selected;
  * a pilot with no kills or losses: PILOT-03, no dossier;
  * 037: "Rhea Recency" (an old busy Sabre, a Curse used yesterday in a small gang, a Vedmak): All runs Curse, Vedmak, Sabre and opens on
    the Curse; Solo runs by the newest solo kill (Vedmak 10 d, Curse 30 d, Sabre), its last-used column too; the page with the
    busiest-first sort, or with the last-used of any size in a gang size, fails it;
  * at 390 px nothing runs off the page; no page errors.
v2026.10.14.89 fails (no dossier); v2026.10.14.90 fails the "view on zKillboard" check (the fallback tab linked to killmail undefined).
"""
import sys, os, re, statistics, datetime, time, calendar, math
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..'))
from playwright.sync_api import sync_playwright
import sa_mocks as M
from pyfa_sde import gname

HTML = os.path.abspath(next((a for a in sys.argv[1:] if not a.startswith('--')), os.path.join(HERE, '..', '..', 'index.html')))
fails = 0
def check(ok, msg):
    global fails
    print(('OK   ' if ok else 'FAIL ') + msg); fails += not ok
NAME = M.PILOTS[M.DOSSIER_PILOT][0]
TZ, TZ_H = 'Asia/Tokyo', 9
size = lambda n: 'solo' if n <= 1 else 'small' if n <= 10 else 'fleet'
E = M.DOSSIER_ENTRIES   # (hull, weapon, players, mates, victim, days, hour, system)
LOSS_HULLS = ['Vedmak', 'Curse']   # the capsule isn't a hull
KT = [M.KM[k]['killmail_time'] for k in reversed(M.DOSSIER_KILLS)]   # each entry's killmail time (E is newest first, the kills oldest first)
TNAME = {v: k for k, v in M.byname.items()}
LT = {TNAME[M.KM[k]['victim']['ship_type_id']]: M.KM[k]['killmail_time'] for k in M.DOSSIER_LOSSES}
def expect(mode):
    rows = {}
    for (hull, weapon, n, mates, victim, days, hour, system), t in zip(E, KT):
        r = rows.setdefault(hull, {'all': [], 'ks': [], 'ts': []})
        r['all'].append(n)
        if mode == 'all' or size(n) == mode:
            r['ks'].append((weapon, n, [mates[i % len(mates)] for i in range(n - 1)] if mates else [], victim)); r['ts'].append(t)
    for h in LOSS_HULLS: rows.setdefault(h, {'all': [], 'ks': [], 'ts': []})
    out = []
    for hull, r in rows.items():
        losses = LOSS_HULLS.count(hull)
        if mode != 'all' and not r['ks']: continue
        ks = r['ks']
        med = None if not ks else (lambda s: s[len(s) // 2] if len(s) % 2 else round((s[len(s) // 2 - 1] + s[len(s) // 2]) / 2))(sorted(k[1] for k in ks))
        mates = Counter(); [mates.update(set(k[2])) for k in ks]
        vic = Counter(gname(M.byname[k[3]]) for k in ks)
        top = lambda c, n: sorted(c.items(), key=lambda x: (-x[1], x[0]))[:n]
        out.append({'hull': hull, 'k': len(ks), 'of': len(r['all']), 'losses': losses, 'score': (len(r['all']) + losses) if mode == 'all' else len(ks),
                    'last': max(r['ts'] + ([LT[hull]] if mode == 'all' and hull in LT else [])),   # 037: in a size, their newest kill of that size
                    'med': med, 'w': ', '.join(w for w, _ in top(Counter(k[0] for k in ks), 2)),
                    'mates': ' · '.join(f'{h} {c}' for h, c in top(mates, 3)), 'vic': ' · '.join(f'{c} {n}' for c, n in top(vic, 2)),
                    'sz': [sum(1 for n in r['all'] if size(n) == s) for s in ('solo', 'small', 'fleet')]})
    return sorted(out, key=lambda r: (r['last'], r['score']), reverse=True)   # 037: newest first, the count only as a tie-break
ROWS = """() => [...document.querySelectorAll('#pilotDossier button.pd-row')].map(b => ({hull: b.querySelector('.pd-hull .nm').firstChild.textContent,
  sub: b.querySelector('.pd-hull .pd-sub').textContent, k: b.querySelector('.pd-n.k').textContent, gang: b.querySelector('.pd-gang > span:last-child').textContent,
  bar: [...b.querySelectorAll('.pd-gang .bar i')].map(i => Number(i.style.flexGrow || i.style.flex.split(' ')[0])),
  w: b.querySelector('.pd-w').textContent, f: b.querySelector('.pd-f').textContent, v: b.querySelector('.pd-v').textContent, sel: b.getAttribute('aria-pressed') === 'true'}))"""
def want_rows(mode):
    out = []
    for r in expect(mode)[:8]:
        out.append({'hull': r['hull'], 'sub': (f"{r['losses']} loss{'' if r['losses'] == 1 else 'es'} · fit from their losses" if r['losses'] else 'no loss of theirs'),
                    'k': f"{r['k']}" + ('' if mode == 'all' else f" of {r['of']}"), 'gang': f"usually {r['med']}" if r['med'] is not None else 'no kills',
                    'bar': r['sz'] if r['of'] else [], 'w': r['w'] or '—', 'f': r['mates'] or '—', 'v': r['vic'] or '—'})
    return out
def got_rows(pg): return [{k: v for k, v in r.items() if k != 'sel'} for r in pg.evaluate(ROWS)]
def idle(pg):
    pg.wait_for_function("() => !document.querySelector('#fitBtn').disabled && document.querySelector('#pilotBusy').hidden", timeout=120000); pg.wait_for_timeout(400)
def analyze(pg, name, ship=''):
    pg.click('#tabBtnPilot'); pg.fill('#pilotName', name); pg.fill('#manualShip', ship); pg.click('#fitBtn'); pg.wait_for_timeout(300); idle(pg)

with sync_playwright() as p:
    b = p.chromium.launch()
    errs = []
    def new_ctx(w):
        ctx = b.new_context(bypass_csp=True, viewport={'width': w, 'height': 1000}, timezone_id=TZ); ctx.on('page', lambda pg: pg.on('pageerror', lambda e: errs.append(str(e)))); M.route(ctx); return ctx
    ctx = new_ctx(1480)
    pg = ctx.new_page(); pg.goto('file://' + HTML)
    M.ZKB_CALLS.clear()
    analyze(pg, NAME)
    head = pg.evaluate("() => [document.querySelector('#pilotDossier .pd-head h3').textContent, document.querySelector('#pilotDossier .pd-head .ctx').textContent]")
    check(not pg.evaluate("() => document.querySelector('#pilotDossier').hidden") and head[0] == 'Pilot Dossier' and head[1].startswith(f'newest {len(E)} kills, 3 losses'), f'the dossier, from {len(E)} kills and 3 losses {head}')
    sizes = Counter(size(e[2]) for e in E)
    seg = pg.evaluate("() => [...document.querySelectorAll('#pilotDossier [data-pd-mode]')].map(b => [b.dataset.pdMode, b.querySelector('b').textContent, b.getAttribute('aria-pressed')])")
    check(seg == [['all', str(len(E)), 'true'], ['solo', str(sizes['solo']), 'false'], ['small', str(sizes['small']), 'false'], ['fleet', str(sizes['fleet']), 'false']],
          f"the switch: All / Solo / Small gang / Fleet with their kills (players on the killmail, the NPC not counted) {seg}")
    g, w = got_rows(pg), want_rows('all')
    check(g == w, "All: each hull, newest first: kills, losses, gang bar, usual size, weapon, wingmates, victims\n      page " + str(g) + "\n      want " + str(w))
    sel = [r['hull'] for r in pg.evaluate(ROWS) if r['sel']]
    st = pg.inner_text('#fitStatus')
    check(sel == [w[0]['hull']] and 'nor of their alliance' in st and not pg.query_selector('.hull-pick'), f"the hull used last ({w[0]['hull']}) shown first; no hull dropdown; no fit anywhere said so ({sel}, {st!r})")
    kl = [c[0] for c in M.ZKB_CALLS if f'/kills/characterID/{M.DOSSIER_PILOT}/' in c[0]]
    check(len(kl) == 1, f'the kills list asked once, for the Last Kill line and the dossier ({len(kl)})')
    # footer
    hrs = [0] * 24
    for k in M.DOSSIER_KILLS:
        t = datetime.datetime.strptime(M.KM[k]['killmail_time'], '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(hours=TZ_H)
        hrs[t.hour] += 1
    foot = pg.evaluate("() => [document.querySelector('#pilotDossier .pd-foot .k').textContent, [...document.querySelectorAll('#pilotDossier [data-pd=hours] i')].map(i => Number(i.dataset.pdH)), document.querySelector('[data-pd=systems]').textContent, document.querySelector('[data-pd=split]').textContent]")
    check(foot[0] == 'Active, your time (UTC+9)' and foot[1] == hrs, f"active hours in the browser's own time zone ({TZ}): {foot[0]!r}, {foot[1]} (want {hrs})")
    sysc = Counter(e[7] for e in E); [sysc.update([30004759]) for _ in range(3)]
    want_sys = ' · '.join(f'{M.SYSTEMS[s]} {n}' for s, n in sorted(sysc.items(), key=lambda x: -x[1])[:3])
    check(foot[2] == want_sys and foot[3] == f"{sizes['solo']} solo · {sizes['small']} small gang · {sizes['fleet']} fleet", f'usual systems {foot[2]!r} (want {want_sys!r}); the split {foot[3]!r}')
    # the switch
    for mode in ('small', 'fleet'):
        pg.click(f'#pilotDossier [data-pd-mode="{mode}"]'); pg.wait_for_timeout(200)
        g, w = got_rows(pg), want_rows(mode)
        check(g == w, f"{mode}: only those kills, 'N of M', newest first by them\n      page " + str(g) + "\n      want " + str(w))
    pg.click('#pilotDossier [data-pd-mode="all"]'); pg.wait_for_timeout(200)
    # a row with a loss: its loss
    pg.click('#pilotDossier [data-pd-hull="%d"]' % M.byname['Vedmak']); pg.wait_for_timeout(300); idle(pg)
    v = pg.evaluate("() => [document.querySelector('#fitStatus').textContent, document.querySelectorAll('#fitResults [role=tab]').length, !!document.querySelector('.pd-note'), [...document.querySelectorAll('#pilotDossier button.pd-row[aria-pressed=true]')].map(b => b.dataset.pdHull)]")
    check(v[0] == 'Showing the 1 most recent loss of Vedmak.' and v[1] == 1 and not v[2] and v[3] == [str(M.byname['Vedmak'])], f'a row with a loss: that loss {v}')
    # a row with none: their alliance's common fit, said as not theirs; one zKillboard request
    M.ZKB_CALLS.clear()
    pg.click('#pilotDossier [data-pd-hull="%d"]' % M.byname['Loki']); pg.wait_for_timeout(300); idle(pg)
    note = pg.evaluate("() => (document.querySelector('.pd-note > span:last-child') || {}).textContent || ''")
    dps = pg.evaluate("""() => { const t = document.querySelector('#fitResults .subtab-panel:not([style*="none"])'); if(!t) return null;
      const e = [...t.querySelectorAll('.estimate-stat')].find(x => x.innerText.toUpperCase().includes('TOTAL DPS')); return e ? e.innerText.replace(/\\s+/g, ' ') : null; }""")
    pin = round(M.PIN['Loki']['dpsFixed'])
    check(dps is not None and f'{pin:,}' in dps, f"the common fit's numbers are that golden Loki's (pinned {pin} DPS): {dps!r}")
    gl = [c[0] for c in M.ZKB_CALLS if '/losses/allianceID/%d/shipTypeID/%d/' % (M.THIRD, M.byname['Loki']) in c[0]]
    tabs = pg.evaluate("() => document.querySelectorAll('#fitResults [role=tab]').length")
    check("No loss of Vesna Dossier's in a Loki: showing Random Third Party's common Loki fit (2 of 2 of their losses), not their own." == note.strip() and len(gl) == 1 and tabs == 1,
          f'no loss of theirs: their alliance\'s common fit, said as not theirs, one zKillboard request ({note.strip()!r}, {len(gl)}, {tabs} tab)')
    # v2026.10.14.91 (the owner: "if you use the 'view on zkillboard' link, it does not work"): the tab's links are the
    # killmail its fit was read from, the newest of the variant's losses (zKillboard's newest-first order), said as theirs
    lk = max(M.FLEET_LOSSES[(M.THIRD, 'Loki')])
    row = pg.evaluate("""() => { const t = document.querySelector('#fitResults .subtab-panel:not([style*="none"])'); const a = t && t.querySelector('.lossrow a');
      return [a ? a.getAttribute('href') : null, t ? t.querySelector('.lossrow span').textContent : '', !!document.querySelector('#fitResults [data-action="share-link"]')]; }""")
    check(row[0] == f'https://zkillboard.com/kill/{lk}/' and row[1] == f"killmail {lk} · Random Third Party's loss, the newest of 2 with this fit" and row[2],
          f'no loss of theirs: "view on zKillboard" opens the loss its fit came from, the row says whose, the share link is offered {row}')
    # a ship typed in
    analyze(pg, NAME, 'Vedmak')
    t = pg.evaluate("() => [document.querySelector('#fitStatus').textContent, !document.querySelector('#pilotDossier').hidden, [...document.querySelectorAll('#pilotDossier button.pd-row[aria-pressed=true]')].map(b => b.dataset.pdHull)]")
    check(t == ['Showing the 1 most recent loss of Vedmak.', True, [str(M.byname['Vedmak'])]], f'a ship typed in: its losses as before, the dossier under it with that row selected {t}')
    # no history
    analyze(pg, M.PILOTS[M.SMALL_FROST[1]][0])
    n = pg.evaluate("() => [document.querySelector('#fitStatus').textContent, document.querySelector('#pilotDossier').hidden]")
    check('(PILOT-03)' in n[0] and 'kills or losses' in n[0] and n[1], f'no kills or losses: PILOT-03, no dossier {n}')
    ctx.close()
    # 037: hulls newest first ("Rhea Recency"), and the page with the old sort or the any-size last-used fails it
    PAGE = open(HTML, encoding='utf-8').read()
    def ago(k):   # the page's pdAgo, from the killmail's time
        m = max(0, (time.time() - calendar.timegm(time.strptime(M.KM[k]['killmail_time'], '%Y-%m-%dT%H:%M:%SZ'))) / 60)
        r = lambda x: int(math.floor(x + 0.5))
        return f'{max(1, r(m))} min' if m < 60 else f'{r(m / 60)} h' if m < 2880 else f'{r(m / 1440)} d'
    RK = M.HIST[M.RHEA]['kills']   # Sabre x10 (99..90 days), Curse solo (30), Vedmak solo (10), Curse small gang (1)
    SAB, CUR_SOLO, VED, CUR = ago(RK[9]), ago(RK[10]), ago(RK[11]), ago(RK[12])
    def rhea(url):
        ctx = new_ctx(1480); pg = ctx.new_page(); pg.goto(url); out = []
        analyze(pg, M.PILOTS[M.RHEA][0])
        last = lambda: pg.evaluate("() => [...document.querySelectorAll('#pilotDossier button.pd-row')].map(b => [b.querySelector('.pd-hull .nm').firstChild.textContent, b.querySelector('.pd-last').textContent, b.getAttribute('aria-pressed') === 'true'])")
        a = last()
        if [x[:2] for x in a] != [['Curse', CUR], ['Vedmak', VED], ['Sabre', SAB]]: out.append(f'All {a}')
        if [x[0] for x in a if x[2]] != ['Curse']: out.append(f'opened on {[x[0] for x in a if x[2]]}')
        pg.click('#pilotDossier [data-pd-mode="solo"]'); pg.wait_for_timeout(200); so = last()
        if [x[:2] for x in so] != [['Vedmak', VED], ['Curse', CUR_SOLO], ['Sabre', SAB]]: out.append(f'Solo {so}')
        pg.click('#pilotDossier [data-pd-mode="small"]'); pg.wait_for_timeout(200); sm = last()
        if [x[:2] for x in sm] != [['Curse', CUR]]: out.append(f'Small gang {sm}')
        ctx.close(); return out
    out = rhea('file://' + HTML)
    check(not out, f'newest first: All Curse {CUR}, Vedmak {VED}, Sabre {SAB} (the old busy hull lower down), opened on the Curse; Solo by the newest solo kill (Vedmak {VED}, Curse {CUR_SOLO}, Sabre {SAB}); Small gang Curse ({out})')
    import tempfile
    MUT = [('the busiest first', "  return rows.sort((a, b) => b.last - a.last || b.score - a.score);", "  return rows.sort((a, b) => b.score - a.score || b.last - a.last);"),
           ('last used at any size', "  return mode === 'all' ? Math.max(", "  return true ? Math.max(")]
    tmp = tempfile.mkdtemp(prefix='dossier_mut_')
    for name_, a_, b_ in MUT:
        if PAGE.count(a_) != 1: check(False, f'mutant "{name_}": its text is in the page'); continue
        f = os.path.join(tmp, 'index.html'); open(f, 'w', encoding='utf-8').write(PAGE.replace(a_, b_, 1))
        out = rhea('file://' + f)
        check(bool(out), f'mutant "{name_}" fails the newest-first case ({out[:1]})')
    # phone
    ctx = new_ctx(390); pg = ctx.new_page(); pg.goto('file://' + HTML)
    analyze(pg, NAME)
    over = pg.evaluate("() => [document.documentElement.scrollWidth, [...document.querySelectorAll('#pilotDossier *')].filter(e => { const r = e.getBoundingClientRect(); return e.checkVisibility() && r.width && (r.right > innerWidth + 1 || r.left < -1); }).map(e => e.className || e.tagName).slice(0, 5)]")
    check(over[0] <= 390 and not over[1], f'390 px: nothing runs off the page {over}')
    ctx.close()
    check(not errs, f'no page errors {errs[:3]}')
    b.close()
print(f'FAILURES: {fails}')
sys.exit(1 if fails else 0)
