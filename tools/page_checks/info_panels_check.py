"""Info panels: never a heading's capitals or spacing, and every bold lead drawn bold (build queue 036; Project doc
roadmap/info-panels-plan.md).

    python3 -I tools/page_checks/info_panels_check.py [index.html]   -> 'FAILURES: N' (must be 0)

The owner, 2026-11-11: "please check for unnecessary capitalization as well" (a screenshot of the profile's Standings panel drawn in
capitals: its info button sits inside the section heading .pp-pane .pp-sh, uppercase with .16em letter spacing, and .info-body set
neither, so the whole panel inherited both). Checks:
  * every info panel in the profile, on each of its tabs (EVE, Pilot, Fits, Intel), and every one on the page outside it: opened, the
    panel, its title and its paragraphs have text-transform none and letter-spacing normal;
  * the profile's Pilot tab holds the Standings panel (`side`), the EVE tab `side#sso`, `side#eve`, `side#online` and `intel#game`;
  * every CARD_INFO key drawn inside a made-up profile heading (`.pp-pane .pp-sh`, the worst case): the same;
  * every CARD_INFO key: no "**" left in the drawn text, one <b> per **…** pair (036's text has paragraphs with two or three leads), and
    the drawn text is CARD_INFO's with {card:…} filled and the ** taken out;
  * no page errors.
Mutants: the .info-body rule removed (the capitals come back), and the old one-lead infoParaHtml (literal ** in the text).
"""
import sys, os, re, pathlib, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
from playwright.sync_api import sync_playwright
HTML = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', 'index.html'))
PAGE = open(HTML, encoding='utf-8').read()
fails = 0
def check(ok, msg):
    global fails
    print(('OK   ' if ok else 'FAIL ') + msg)
    if not ok: fails += 1

# Each open panel under root: [key, where, [problems]]; a problem is a part with a case or spacing of its own.
STYLE = """(sel) => { const out = [];
  for(const root of document.querySelectorAll(sel)){
    for(const d of root.querySelectorAll('details.info-pop')){
      d.open = true;
      const body = d.querySelector('.info-body'), bad = [];
      for(const el of [body, body.querySelector('.info-head span'), ...body.querySelectorAll('p, summary')]){
        if(!el) continue;
        const cs = getComputedStyle(el);
        if(cs.textTransform !== 'none' || cs.letterSpacing !== 'normal') bad.push(`${el.tagName.toLowerCase()} ${cs.textTransform} ${cs.letterSpacing}`);
      }
      out.push([d.dataset.info, root.id || root.className, bad]);
      d.open = false;
    }
  }
  return out; }"""
# Every key drawn in a made-up profile heading: [key, style problems, text problems]
ALL = """() => { const pane = document.createElement('div'); pane.className = 'pp-pane'; const sh = document.createElement('div'); sh.className = 'pp-sh';
  pane.appendChild(sh); document.body.appendChild(pane); const out = [];
  for(const k of Object.keys(CARD_INFO)){
    sh.innerHTML = 'Heading ' + infoBtnHtml(k);
    const d = sh.querySelector('details.info-pop'); d.open = true;
    const body = d.querySelector('.info-body'), bad = [], txt = [];
    for(const el of [body, body.querySelector('.info-head span'), ...body.querySelectorAll('p, summary')]){
      const cs = getComputedStyle(el);
      if(cs.textTransform !== 'none' || cs.letterSpacing !== 'normal') bad.push(`${el.tagName.toLowerCase()} ${cs.textTransform} ${cs.letterSpacing}`);
    }
    const paras = CARD_INFO[k], pairs = paras.reduce((n, s) => n + (s.match(/\\*\\*[^*]+\\*\\*/g) || []).length, 0);
    const bs = body.querySelectorAll(':scope > p b, :scope > details.info-more b').length;
    if(body.textContent.includes('**')) txt.push('a literal ** in the text');
    if(bs !== pairs) txt.push(`${bs} bold, ${pairs} leads`);
    const want = paras.map(s => s.replace(/\\{card:([\\w.]+)\\}/g, (_, c) => cardName(c)).replace(/\\*\\*/g, '').replace(/^\\[([^\\]]+)\\]\\s+/, '$1'));
    const got = [...body.querySelectorAll(':scope > p, :scope > details.info-more')].map(e => e.textContent);
    if(JSON.stringify(got.slice(0, want.length)) !== JSON.stringify(want)) txt.push('text differs from CARD_INFO: ' + JSON.stringify(got).slice(0, 120));
    out.push([k, bad, txt]);
  }
  pane.remove(); return out; }"""

def cases(b, path, out):
    """The cases the mutants must fail (run on the real page too). A failure appends to out; returns what was seen."""
    pg = b.new_page(bypass_csp=True, viewport={'width': 1440, 'height': 900}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:150]))
    pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith('file:') else r.abort())
    pg.goto(pathlib.Path(path).as_uri()); pg.wait_for_timeout(700)
    seen = {}
    for tab in ('eve', 'pilot', 'fit', 'intel'):
        pg.evaluate("(t) => openProfile(t)", tab); pg.wait_for_timeout(250)
        r = pg.evaluate(STYLE, [f'#ppPane-{tab}:not([hidden])'])   # the tab shown only
        keys = sorted({x[0] for x in r}); seen[tab] = keys
        for k, where, bad in r:
            if bad: out.append(f'profile {tab} tab, {k}: {bad[:2]}')
        pg.evaluate("() => closeProfile(false)"); pg.wait_for_timeout(100)
    r = pg.evaluate(STYLE, ['body']); seen['page'] = sorted({x[0] for x in r})
    for k, where, bad in r:
        if bad: out.append(f'page, {k}: {bad[:2]}')
    for k, bad, txt in pg.evaluate(ALL):
        if bad: out.append(f'{k} in a profile heading: {bad[:2]}')
        if txt: out.append(f'{k}: {txt[:2]}')
    if errs: out.append(f'page errors {errs[:2]}')
    pg.close()
    return seen

MUTANTS = [
    ('the .info-body rule removed', "\n    text-transform:none; letter-spacing:normal;}", "}"),
    ('one bold lead per paragraph (the old infoParaHtml)', "function infoBoldHtml(t){ return escapeHtml(t).replace(/\\*\\*([^*]+)\\*\\*/g, '<b>$1</b>'); }",
     "function infoBoldHtml(t){ const m = /^\\*\\*([^*]+)\\*\\*\\s*([\\s\\S]*)$/.exec(t); return m ? `<b>${escapeHtml(m[1])}</b> ${escapeHtml(m[2])}` : escapeHtml(t); }"),
]

with sync_playwright() as p:
    b = p.chromium.launch()
    out = []
    seen = cases(b, HTML, out)
    print('seen:', {k: len(v) for k, v in seen.items()})
    check('side' in seen.get('pilot', []), f'the Pilot tab has the Standings panel (side) {seen.get("pilot")}')
    check(seen.get('eve') and all(k in seen.get('eve', []) for k in ('side#sso', 'side#eve', 'side#online', 'intel#game')), f'the EVE tab has side#sso, side#eve, side#online, intel#game {seen.get("eve")}')
    check(not out, f'every panel: normal case and spacing, every lead bold, the text CARD_INFO\'s ({len(out)} problems: {out[:4]})')
    tmp = tempfile.mkdtemp(prefix='info_panels_mut_')
    for name_, a, bb in MUTANTS:
        if PAGE.count(a) != 1: check(False, f'mutant "{name_}": its text is in the page once ({PAGE.count(a)})'); continue
        path = os.path.join(tmp, 'index.html'); open(path, 'w', encoding='utf-8').write(PAGE.replace(a, bb))
        mo = []
        try: cases(b, path, mo)
        except Exception as e: mo.append(f'error {str(e)[:80]}')
        check(bool(mo), f'mutant "{name_}" fails the cases ({mo[:1]})')
    b.close()
print(f'FAILURES: {fails}')
sys.exit(1 if fails else 0)
