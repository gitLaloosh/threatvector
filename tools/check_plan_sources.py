"""A plan's outside facts carry their sources (LESSON #147; the build queue README's rule "Facts from outside the project carry
their source", the owner 2026-11-08: "let's force planners to learn from it as well").

    python3 -I tools/check_plan_sources.py PLAN.md [PLAN2.md ...]   -> 'PLAN SOURCES: ... 0 problems' (exit 1 otherwise)
    python3 -I tools/check_plan_sources.py --self-test              -> made-up plans, good and bad (a fast lint in run_checks)

Plans live in the Project, not in this repo: the planning session runs this on its plan before queueing it, and the build session
runs it on the plan it takes, before its review (save the plan with project_read first). It checks the shape, not the truth: the
build session still opens every source at its review. It refuses:
  * a plan with no "## Sources" section (or one that doesn't say "Sources: none (no outside facts)");
  * a row of the Sources table without a source (a URL, a file path, or a named live answer) or without a date (YYYY-MM-DD),
    unless the row is marked UNVERIFIED with what would confirm it;
  * a row whose only source is a secondary one (a wiki, forum, blog, reddit, a third-party library) without the word "secondary"
    and without a primary source beside it;
  * outside the table, a line saying something is "from memory" or "I believe" / "I think", unless it is marked UNVERIFIED (a
    line quoting the owner, [stated], is his own words and is left alone).
The UNVERIFIED rows are listed, so the build session can put each one in the pull request's hand test.
"""
import re, sys

SECONDARY = re.compile(r'wiki|forum|reddit|blog|stackoverflow|medium\.com|crate|npm|pypi|github\.com/(?!esi|ccp)', re.I)
DATE = re.compile(r'\b20\d\d-\d\d-\d\d\b')
SOURCE = re.compile(r'https?://|`[^`]*[/.][^`]*`|\blive (answer|JWKS|response)\b|\bthe owner\b|claude/|tools/|\.py\b|\.md\b', re.I)
VAGUE = re.compile(r'\bfrom memory\b|\bI (believe|think)\b|\bprobably (is|uses|returns)\b', re.I)


def check(path):
    text = open(path, encoding='utf-8').read()
    bad, unverified = [], []
    m = re.search(r'^##\s+Sources\b.*?$(.*?)(?=^##\s|\Z)', text, re.M | re.S)
    if not m:
        if not re.search(r'Sources:\s*none\s*\(no outside facts\)', text, re.I):
            bad.append('no "## Sources" section (or "Sources: none (no outside facts)")')
        rows = []
    else:
        rows = [l for l in m.group(1).splitlines() if l.strip().startswith('|') and not re.match(r'^\|\s*-', l.strip())]
        rows = rows[1:] if rows and re.search(r'\bFact\b', rows[0], re.I) else rows
        if not rows and not re.search(r'none\s*\(no outside facts\)', m.group(1), re.I):
            bad.append('the Sources section has no rows')
    for r in rows:
        cells = [c.strip() for c in r.strip().strip('|').split('|')]
        fact = cells[0] if cells else r
        if re.search(r'UNVERIFIED', r):
            if not re.search(r'UNVERIFIED\**\s*[:(—-]\s*\S', r): bad.append(f'{fact[:60]!r}: UNVERIFIED without what would confirm it')
            unverified.append(fact[:80]); continue
        if not SOURCE.search(' '.join(cells[1:])): bad.append(f'{fact[:60]!r}: no source (a URL, a file, or a named live answer)')
        if not DATE.search(r): bad.append(f'{fact[:60]!r}: no date checked (YYYY-MM-DD)')
        src = ' '.join(cells[1:2])
        if SECONDARY.search(src) and not re.search(r'secondary', r, re.I): bad.append(f'{fact[:60]!r}: a secondary source not labelled "secondary"')
        if SECONDARY.search(src) and not re.search(r'https?://(?![^ ]*(wiki|forum|reddit|blog))', src) and not re.search(r'docs\.|live|primary|the owner', r, re.I):
            bad.append(f'{fact[:60]!r}: only a secondary source; add the provider\'s own, or mark it UNVERIFIED')
    for i, line in enumerate(text.splitlines(), 1):
        if VAGUE.search(line) and 'UNVERIFIED' not in line and '[stated]' not in line:   # a [stated] line is the owner's own words
            bad.append(f'line {i}: "{VAGUE.search(line).group(0)}" without UNVERIFIED')
    return bad, unverified


GOOD = """# p
## Sources
| Fact | Source | Checked | Status |
|---|---|---|---|
| Token sub is CHARACTER:EVE:<id> | https://docs.esi.evetech.net/docs/sso/validating_eve_jwt.html | 2026-11-08 | verified |
| A login with no scope works | none | - | **UNVERIFIED**: the owner's hand test |
"""
BAD = [('no Sources section', "# p\nThe sub is EVE:CHARACTER:id.\n"),
       ('no source', GOOD.replace('https://docs.esi.evetech.net/docs/sso/validating_eve_jwt.html', 'CCP')),
       ('no date', GOOD.replace('2026-11-08', 'recently')),
       ('secondary only', GOOD.replace('https://docs.esi.evetech.net/docs/sso/validating_eve_jwt.html', 'https://wiki.eveuniversity.org/SSO')),
       ('UNVERIFIED with no way to confirm', GOOD.replace("**UNVERIFIED**: the owner's hand test", 'UNVERIFIED')),
       ('from memory', GOOD + "\nThe revoke address is /v2/oauth/revoke, from memory.\n")]


def self_test():
    import tempfile, os
    d = tempfile.mkdtemp(); fails = []
    def run(text):
        p = os.path.join(d, 'p.md'); open(p, 'w').write(text); return check(p)[0]
    if run(GOOD): fails.append(f'a good plan refused: {run(GOOD)}')
    for name, text in BAD:
        if not run(text): fails.append(f'{name}: not refused')
    for f in fails: print('PLAN SOURCES SELF-TEST', f)
    print('PLAN SOURCES SELF-TEST: ' + ('ok' if not fails else f'{len(fails)} problems'))
    return 1 if fails else 0


def main(argv):
    if '--self-test' in argv: return self_test()
    paths = [a for a in argv if not a.startswith('--')]
    if not paths: print(__doc__); return 2
    total = 0
    for p in paths:
        bad, unv = check(p)
        for b in bad: print(f'PLAN SOURCES {p}: {b}')
        for u in unv: print(f'PLAN SOURCES {p}: UNVERIFIED (put it in the hand test): {u}')
        total += len(bad)
    print(f'PLAN SOURCES: {len(paths)} plan(s); {total} problems')
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
