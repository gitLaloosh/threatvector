"""Run the checks a change needs, not all of them every time (v2026.10.30.2; the owner: "yep, do it").

    PYFA_SRC=/path/to/pyfa python3 -I tools/run_checks.py --tier fast                    # the quick lints (seconds)
    PYFA_SRC=/path/to/pyfa python3 -I tools/run_checks.py --tier area --area intel,layout  # + the page checks of those areas
    PYFA_SRC=/path/to/pyfa python3 -I tools/run_checks.py --tier calc [--area fit]          # + the pyfa chain + the calc page checks
    PYFA_SRC=/path/to/pyfa python3 -I tools/run_checks.py --tier all                     # everything
    PYFA_SRC=/path/to/pyfa python3 -I tools/run_checks.py --auto [--since OLD_COPY]   # the tier and areas picked from what changed
    python3 -I tools/run_checks.py --auto --plan [--since OLD_COPY]                    # only say what --auto would run
    python3 -I tools/run_checks.py --list            # the areas and their page checks
    python3 -I tools/run_checks.py --check-tags      # every page check has an area (a chain step)
    add --ledger to append the run to tools/check_ledger.md; --jobs N (default twice the cores, at most 6); an index.html path to check another copy
    python3 -I tools/run_checks.py --served [--all]  # build queue 027: the copy GitHub Pages serves (tools/publish.py), made in a
                                                     # scratch folder, through SERVED_CHECKS (--all: every page check)

Which tier (CLAUDE.md "Checks"): --auto (v2026.10.31.7, page unchanged) picks it from the changed lines and files
(tools/check_picker.py): a calculation change or one of its inputs -> calc (+ the areas that show it); page or Intel work ->
area with the areas touched; shared code, anything unmapped, or every 5th delivery -> all. Pick by hand only to run more.
The fast lints always run, now with the regression suite and the D-Scan parse tests (seconds; they load the page script the
way the chain does, so a start-up error can't wait for a calc run). Each page check has 5 minutes (SLOW: more), so a hung one
fails fast. A page check that fails is run again on its own once: passing then, it is reported as flaky (timing under load),
not as a pass. A check in the ledger's Quarantine table still runs, but its failure doesn't fail the run until its date passes
(at most 14 days; then it fails the run). Ends with "RUN CHECKS: N failed" (0 to deliver).
"""
import sys, os, re, time, subprocess, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # -I leaves this folder off the path; check_picker lives here
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
PC = os.path.join(ROOT, 'tools', 'page_checks')

# Each page check and the areas whose changes it guards. A new page check must be added here (--check-tags fails otherwise).
AREAS = {
    'affiliation_check': ['pilot'], 'assumed_charge_check': ['fit', 'calc'], 'busy_check': ['pilot'],
    'card_width_check': ['layout'], 'charges_check': ['fit', 'calc'], 'damage_chart_check': ['myship', 'calc'],
    'dossier_check': ['pilot'], 'intel_example_check': ['intel', 'layout'], 'sso_check': ['system', 'layout'], 'sso_game_check': ['intel', 'system', 'layout'], 'sso_online_check': ['intel', 'system', 'layout'], 'sso_standings_check': ['system', 'intel', 'pilot', 'layout'], 'intel_folder_check': ['intel', 'layout'], 'intel_logs_check': ['intel'], 'intel_one_tab_check': ['intel', 'layout'], 'list_caps_check': ['pilot', 'system', 'layout'], 'dossier_kills_check': ['pilot'], 'dossier_pin_check': ['pilot', 'system'], 'kill_groups_check': ['intel', 'pilot', 'system'], 'fleet_hulls_check': ['intel', 'pilot', 'system', 'layout'], 'game_data_check': ['calc', 'fit', 'myship', 'pilot', 'system', 'intel', 'layout'], 'alert_sound_check': ['intel', 'layout'], 'fleet_fit_budget_check': ['pilot', 'system', 'intel'], 'budget_gauge_check': ['pilot', 'system', 'intel', 'layout'], 'scan_rail_check': ['system', 'layout'], 'system_activity_check': ['system', 'intel'], 'extension_check': ['pilot', 'extension'],
    'fight_strip_check': ['myship', 'calc'], 'fighter_application_check': ['fit', 'calc'], 'fighter_bay_check': ['fit', 'calc'],
    'fighter_bombs_check': ['fit', 'calc'], 'fighter_picks_check': ['myship', 'calc'], 'fighter_tile_check': ['myship', 'calc'],
    'fleet_kill_check': ['pilot', 'system'], 'region_names_check': ['intel', 'pilot', 'system'], 'header_check': ['layout', 'intel'],
    'intel_assess_check': ['intel', 'system'], 'intel_check': ['intel'], 'intel_kills_check': ['intel'], 'feed_down_check': ['intel', 'layout'], 'intel_layout_check': ['intel'],
    'intel_place_check': ['intel'], 'intel_words_check': ['intel'], 'intel_gates_check': ['intel'], 'intel_rows_check': ['intel'], 'intel_guard_check': ['intel'], 'intel_fleet_check': ['intel', 'pilot'], 'outside_links_check': ['pilot', 'intel', 'layout'], 'fleet_vs_check': ['pilot', 'system', 'myship'], 'last_kill_check': ['pilot'], 'layout_check': ['layout'], 'matchup_strip_check': ['myship', 'calc'],
    'mine_damage_check': ['myship', 'calc'], 'missile_picks_check': ['myship', 'calc'], 'missing_charges_check': ['fit', 'calc'], 'eft_mutation_check': ['fit', 'calc'],   # build queue 035
    'module_charges_check': ['fit', 'calc'], 'my_ship_check': ['myship'], 'my_ships_check': ['myship'], 'no_shift_check': ['layout'],
    'pilot_rows_check': ['system'], 'request_gates_check': ['intel', 'pilot'], 'ring_track_check': ['fit'], 'sa_size_check': ['system'],
    'scan_contacts_check': ['system'], 'shared_kill_check': ['pilot'], 'ship_class_check': ['fit', 'system'],
    'support_fighters_check': ['fit', 'calc'], 'system_analyzer_check': ['system'], 'ttk_why_check': ['myship', 'calc'],
    'ui_rules_check': ['layout'], 'unload_check': ['fit'], 'weakness_picks_check': ['myship', 'calc'],
    'zkb_outage_check': ['pilot'], 'zkb_slow_check': ['pilot', 'system'], 'outage_check': ['intel', 'layout', 'pilot', 'system'], 'profile_check': ['layout', 'myship', 'system', 'intel'], 'pilot_chip_check': ['intel'], 'intel_filters_check': ['intel', 'layout'], 'html_escape_check': ['intel', 'pilot', 'myship', 'fit', 'system'], 'logo_check': ['layout'], 'info_panels_check': ['layout', 'intel', 'system', 'pilot', 'myship', 'fit'],   # build queue 036
    'csp_check': ['intel', 'pilot', 'myship', 'fit', 'system', 'layout'], 'close_buttons_check': ['intel', 'pilot', 'layout'], 'intel_redraw_check': ['intel', 'layout'], 'intel_map_check': ['intel', 'layout'], 'intel_map_look_check': ['intel', 'layout'], 'intel_map_you_check': ['intel', 'layout'], 'wormhole_filter_check': ['intel', 'layout'], 'paths_to_you_check': ['intel', 'layout'], 'tag_only_check': ['intel'], 'wormhole_sig_check': ['intel', 'layout'], 'wormhole_share_check': ['intel', 'layout'],
}
NAMES = sorted({a for v in AREAS.values() for a in v})
# v2026.10.31.7: a page check gets 5 minutes, these more (their longest run under load, x1.5); a hung check fails fast
PAGE_TIMEOUT = 300
SLOW = {'intel_kills_check': 600, 'wormhole_filter_check': 900, 'wormhole_sig_check': 900, 'wormhole_share_check': 900, 'intel_map_look_check': 600, 'region_names_check': 600, 'zkb_slow_check': 600, 'outage_check': 900}
QUARANTINE_MAX_DAYS = 14
# build queue 027 (Project doc roadmap/page-publish-plan.md): the page checks run on the served copy before every pull request.
# The source-form checks (the PYFA CORE lock, the HTML-sink baseline, LESSON markers) read comments, so they stay on the source.
SERVED_CHECKS = ['csp_check', 'html_escape_check', 'intel_example_check', 'profile_check', 'sso_check', 'header_check']

def quarantine():
    """The ledger's Quarantine table: {check: (why, since, until)} and the problems with it."""
    q, problems = {}, []
    try: text = open(os.path.join(ROOT, 'tools', 'check_ledger.md'), encoding='utf-8').read()
    except FileNotFoundError: return q, problems
    sec = text.split('## Quarantine', 1)[1].split('\n## ', 1)[0] if '## Quarantine' in text else ''
    for l in sec.splitlines():
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        if len(c) != 4 or c[0] in ('Check', '') or set(c[0]) <= set('-:'): continue
        name, why, since, until = c[0].strip('`'), c[1], c[2], c[3]
        try: d0, d1 = (datetime.date.fromisoformat(x) for x in (since, until))
        except ValueError: problems.append(f'{name}: dates must be YYYY-MM-DD ({since}, {until})'); continue
        if name not in AREAS: problems.append(f'{name}: not a page check')
        if (d1 - d0).days > QUARANTINE_MAX_DAYS: problems.append(f'{name}: quarantined {(d1 - d0).days} days, at most {QUARANTINE_MAX_DAYS}')
        if not why: problems.append(f'{name}: no reason given')
        q[name] = (why, d0, d1)
    return q, problems

def fast(html):
    q = lambda f: f'python3 -I tools/{f} {html}'
    return [   # (label, command, pass test on the last line); the same commands as the chain's steps
        ('every page check has an area', 'python3 -I tools/run_checks.py --check-tags', lambda l: l.endswith(' 0 problems')),
        # v2026.10.31.7: the page checks and the chain read pyfa's data from PYFA_SRC; an older checkout passes most of them quietly
        ('PYFA_SRC is the verified pyfa', 'python3 -I tools/run_checks.py --check-pyfa-src', lambda l: l.endswith(' 0 problems')),
        ('personal data (LESSON #90)', 'python3 -I tools/check_pii.py .', lambda l: bool(re.search(r' 0 problems($|[;( ])', l))),
        ('UI rules', q('check_ui_rules.py'), lambda l: l.endswith(' 0 problems')),
        ('CSP script hash (LESSON #145)', q('csp_hash.py') + ' --check', lambda l: l.endswith(': 0 problems')),
        ('CSP hash tool self-test', q('csp_hash.py') + ' --self-test', lambda l: l.endswith(': ok')),
        ('the site icons rendered (022)', 'python3 -I tools/render_icons.py --check', lambda l: l.endswith(' 0 problems')),
        ('no new unescaped HTML (LESSON #144)', q('check_html_sinks.py'), lambda l: l.endswith(' 0 problems')),
        ('HTML-sink lint self-test', q('check_html_sinks.py') + ' --self-test', lambda l: l.endswith(': ok')),
        ('the Intel example\'s made-up names (offline)', q('check_example_names.py'), lambda l: l.endswith(' 0 problems')),
        ('publish step self-test (027)', 'python3 -I tools/publish.py --self-test', lambda l: l.endswith(': 0 problems')),
        ('plan sources lint self-test (LESSON #147)', 'python3 -I tools/check_plan_sources.py --self-test', lambda l: l.endswith(': ok')),
        ('subtext rule', q('check_subtext.py'), lambda l: l.endswith(' 0 problems')),
        ('card names', q('check_card_names.py'), lambda l: l.endswith(' 0 problems')),
        ('zKillboard request gates', q('check_request_gates.py'), lambda l: l.endswith(' 0 problems')),
        ('changed-items list (GAME_DATA_PENDING)', q('check_game_data_pending.py'), lambda l: l.endswith(' 0 problems')),   # v2026.11.04.3
        # build queue 034 (LESSON #153): the patch-day report on made-up CCP data, a local stand-in for CCP's site (seconds, no network)
        ('the patch-day report (made-up CCP data)', f'python3 -I tools/independent_checks/check_sde_change_report.py {html}', lambda l: l.endswith(': 0 problems')),
        ('error codes and ERRORS.md', q('gen_errors_md.py'), lambda l: l.endswith('ERRORS.md is up to date')),
        ('LESSONS index', 'python3 -I tools/check_lessons_index.py', lambda l: l.endswith(' 0 problems')),
        # v2026.10.31.7: seconds, not part of the 40-minute chain's cost; they load the page script in a stub DOM (LESSON #36)
        ('regression suite', f'node regression_suite/run_regression.mjs {html}', lambda l: l.endswith('ALL PASS')),
        ('check picker (made-up edits)', 'python3 -I tools/check_picker.py --self-test', lambda l: l.endswith(' 0 problems')),
        ('D-Scan parse tests', f'node regression_suite/dscan_parse_tests.mjs {html}', lambda l: bool(re.fullmatch(r'(\d+)/\1 PASS', l))),
    ]

def sh(cmd, timeout):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=ROOT, shell=True, capture_output=True, text=True, timeout=timeout)
        out = (p.stderr.strip() + '\n' + p.stdout.strip()).strip()   # stdout last: a warning on stderr can't hide the result line
    except subprocess.TimeoutExpired:
        out = f'TIMEOUT after {timeout} s'
    return out, time.time() - t0

def last(out): return (out.splitlines() or [''])[-1].strip()

def chain_notices(out):
    """pyfa_update_check's ATTENTION notices: the indented lines right after its 'ATTENTION:' heading, up to the first step line
    ('OK' / 'FAIL') or a blank line. Build queue 035: the old slice took the first 4 indented lines, so OK steps printed after
    two notices were counted as failed steps ('4 steps failed' for 2 notices, 034's run)."""
    if 'ATTENTION' not in out: return []
    got = []
    for l in out.split('ATTENTION', 1)[1].splitlines()[1:]:
        s = l.strip()
        if not l.startswith('  ') or not s or s.startswith(('OK ', 'FAIL')): break
        got.append(l)
    return got

def check_tags():
    files = {f[:-3] for f in os.listdir(PC) if f.endswith('_check.py')}
    problems = [f'{f}.py: no area in AREAS (tools/run_checks.py)' for f in sorted(files - AREAS.keys())]
    problems += [f'{f}: in AREAS but tools/page_checks/{f}.py is gone' for f in sorted(AREAS.keys() - files)]
    problems += [f'quarantine: {p}' for p in quarantine()[1]]
    for p in problems: print('PROBLEM', p)
    print(f'PAGE CHECK AREAS: {len(files)} page checks, {len(NAMES)} areas ({", ".join(NAMES)}); {len(problems)} problems')
    return 1 if problems else 0

def check_pyfa_src():
    """PYFA_SRC's git HEAD = the commit in tools/pyfa_core_manifest.json (the pyfa every number was verified against)."""
    import json
    want = json.load(open(os.path.join(ROOT, 'tools', 'pyfa_core_manifest.json'), encoding='utf-8'))['pyfa']['commit']
    src = os.environ.get('PYFA_SRC')
    if not src: print('PYFA_SRC: not set (page checks that need pyfa will fail); 0 problems'); return 0
    got = subprocess.run(['git', '-C', src, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    if got == want: print(f'PYFA_SRC: {src} is the verified commit {want[:7]}; 0 problems'); return 0
    print(f'PROBLEM PYFA_SRC {src} is at {got[:7] or "(not a git checkout)"}, not the verified {want[:7]} (tools/pyfa_core_manifest.json)')
    print('PYFA_SRC: 1 problem'); return 1

def version(html):
    m = re.search(r'class="build-tag"[^>]*>(v[\d.]+)<', open(os.path.join(ROOT, html), encoding='utf-8').read())
    return m.group(1) if m else '?'

def served(argv):
    """Make the served copy (tools/publish.py) in a scratch folder and run the served-copy checks against it."""
    import tempfile
    jobs = int(argv[argv.index('--jobs') + 1]) if '--jobs' in argv else min(6, 2 * (os.cpu_count() or 2))
    t0 = time.time(); failed, lines = [], []
    with tempfile.TemporaryDirectory(prefix='served-') as d:
        site = os.path.join(d, '_site'); html = os.path.join(site, 'index.html')
        out, dt = sh(f'python3 -I tools/publish.py --out {site}', 600)
        for l in out.splitlines(): lines.append('     ' + l)
        if last(out) != 'PUBLISH: ok':
            print('\n'.join(lines)); print('RUN CHECKS (served): 1 failed (publish)'); return 1
        steps = [('regression suite (served)', f'node regression_suite/run_regression.mjs --served {html}', lambda l: l.endswith('ALL PASS')),
                 ('D-Scan parse tests (served)', f'node regression_suite/dscan_parse_tests.mjs {html}', lambda l: bool(re.fullmatch(r'(\d+)/\1 PASS', l)))]
        for label, cmd, ok in steps:
            o, t = sh(cmd, 600); good = ok(last(o))
            lines.append(f'{"OK  " if good else "FAIL"} {label} ({t:.0f} s): {last(o)[:160]}')
            if not good: failed.append(label)
        want = sorted(AREAS) if '--all' in argv else SERVED_CHECKS
        def run(name): o, t = sh(f'python3 -I tools/page_checks/{name}.py {html}', SLOW.get(name, PAGE_TIMEOUT)); return name, o, t
        with ThreadPoolExecutor(max_workers=max(1, jobs)) as ex: res = list(ex.map(run, want))
        for name, o, t in res:
            if last(o) != 'FAILURES: 0': o, t = sh(f'python3 -I tools/page_checks/{name}.py {html}', SLOW.get(name, PAGE_TIMEOUT))
            good = last(o) == 'FAILURES: 0'
            lines.append(f'{"OK  " if good else "FAIL"} {name} (served, {t:.0f} s)' + ('' if good else f': {last(o)}'))
            if not good:
                failed.append(name); lines += ['     ' + l[:200] for l in o.splitlines() if l.startswith('FAIL ')][:6]
    for l in lines: print(l)
    print(f'served copy: {len(steps)} steps + {len(want)} page checks in {(time.time() - t0) / 60:.0f} min')
    print(f'RUN CHECKS (served): {len(failed)} failed' + (f' ({", ".join(failed)})' if failed else ''))
    return 1 if failed else 0

def main(argv):
    if '--check-tags' in argv: return check_tags()
    if '--check-pyfa-src' in argv: return check_pyfa_src()
    if '--served' in argv: return served(argv)
    if '--list' in argv:
        for a in NAMES: print(f'{a}: ' + ', '.join(k for k, v in sorted(AREAS.items()) if a in v))
        return 0
    def opt(name, default=None):
        return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else default
    tier = opt('--tier', 'fast')
    areas = [a for a in (opt('--area', '') or '').split(',') if a]
    jobs = int(opt('--jobs', str(min(6, 2 * (os.cpu_count() or 2)))))   # v2026.10.31.7: 6 browsers on 2 cores made timing flakes
    skip = {opt(x) for x in ('--tier', '--area', '--jobs', '--since')}
    html = next((a for a in argv if not a.startswith('--') and a not in skip), 'index.html')
    auto = '--auto' in argv
    if auto:   # v2026.10.31.7: from what changed (tools/check_picker.py)
        import check_picker
        tier, areas, why = check_picker.pick(ROOT, opt('--since'), AREAS, NAMES)
        print(f'AUTO: tier {tier}' + (f' --area {",".join(areas)}' if areas else ''))
        for n in check_picker.BASE_NOTE: print('  ' + n)   # 2026-11-08: what it compared with (main, not the last commit)
        for k, v in sorted(why.items()): print(f'  {k}: {v}')
        if '--plan' in argv: return 0
    bad = [a for a in areas if a not in NAMES]
    if tier not in ('fast', 'area', 'calc', 'all') or bad or (tier == 'area' and not areas):
        print(f'usage: --tier fast|area|calc|all, --area one or more of {",".join(NAMES)} (needed with --tier area)'); return 2
    t0 = time.time(); failed, flaky, lines = [], [], []
    for label, cmd, ok in fast(html):
        out, dt = sh(cmd, 600); good = ok(last(out))
        lines.append(f'{"OK  " if good else "FAIL"} {label} ({dt:.0f} s): {last(out)[:160]}')
        if not good: failed.append(label)
    if tier in ('calc', 'all'):
        out, dt = sh(f'python3 -I tools/pyfa_update_check.py --run', 3600)
        bad_steps = [l for l in out.splitlines() if l.strip().startswith('FAIL')]
        notices = chain_notices(out)   # what moved (build queue 035: was the first 4 indented lines, OK steps included)
        good = 'UP TO DATE' in out and not bad_steps and not notices and ' OK ' in out
        lines.append(f'{"OK  " if good else "FAIL"} the pyfa chain ({dt / 60:.0f} min): {len(bad_steps)} steps failed, {len(notices)} notices')
        lines += ['     notice: ' + l.strip()[:190] for l in notices] + ['     ' + l.strip()[:200] for l in bad_steps]
        if not good: failed.append('pyfa chain')
    want = sorted(AREAS) if tier == 'all' else sorted(k for k, v in AREAS.items() if set(v) & (set(areas) | ({'calc'} if tier == 'calc' else set())))
    env = '' if os.environ.get('PYFA_SRC') else '(PYFA_SRC not set: page checks that need pyfa will fail) '
    qr, _ = quarantine(); today = datetime.datetime.now(datetime.timezone.utc).date(); held = []
    tmo = lambda name: SLOW.get(name, PAGE_TIMEOUT)
    def run(name): out, dt = sh(f'python3 -I tools/page_checks/{name}.py {html}', tmo(name)); return name, out, dt
    with ThreadPoolExecutor(max_workers=max(1, jobs)) as ex: res = list(ex.map(run, want))
    for name, out, dt in res:
        if last(out) == 'FAILURES: 0': lines.append(f'OK   {name} ({dt:.0f} s)'); continue
        out2, dt2 = sh(f'python3 -I tools/page_checks/{name}.py {html}', tmo(name))   # once more, on its own
        if name in qr and last(out2) != 'FAILURES: 0':
            why_q, d0, d1 = qr[name]
            if today <= d1:   # quarantined: reported, not counted, until its date
                held.append(name); lines.append(f'QRNT {name}: {last(out2)} (quarantined until {d1}: {why_q})'); continue
            lines.append(f'     {name}: its quarantine ended {d1}')
        if last(out2) == 'FAILURES: 0':
            flaky.append(name); lines.append(f'FLKY {name}: {last(out)} under load, passed alone ({dt2:.0f} s)')
            lines += ['     ' + l[:200] for l in out.splitlines() if l.startswith('FAIL ')][:3]
        else:
            failed.append(name); lines.append(f'FAIL {name}: {last(out2)}')
            lines += ['     ' + l[:200] for l in out2.splitlines() if l.startswith('FAIL ') or 'Error' in l][:6]
    mins = (time.time() - t0) / 60
    for l in lines: print(l)
    run_desc = ('auto: ' if auto else '') + tier + (f' ({",".join(areas)})' if areas else '')
    print(f'{env}{version(html)}, tier {run_desc}: {len(fast(html))} lints{" + the pyfa chain" if tier in ("calc", "all") else ""} + {len(want)} page checks in {mins:.0f} min; {len(flaky)} flaky')
    if '--ledger' in argv:
        led = os.path.join(ROOT, 'tools', 'check_ledger.md')
        row = (f'| {datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d} | {version(html)} | {run_desc} | {len(want)} | {mins:.0f} | '
               f'{", ".join(failed) or "none"} | {", ".join(flaky + [f"{h} (quarantined, failed)" for h in held]) or "none"} | (fill in) |\n')
        with open(led, 'a', encoding='utf-8') as f: f.write(row)
        print(f'ledger: appended to tools/check_ledger.md; fill in "Caught" before delivering')
    print(f'RUN CHECKS: {len(failed)} failed' + (f' ({", ".join(failed)})' if failed else ''))
    return 1 if failed else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
