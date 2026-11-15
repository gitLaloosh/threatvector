# Mockup: the Pilot Dossier read by fights

For `claude/roadmap/dossier-fights-plan.md` (the owner, 2026-11-14: "Yes, mockup first (Recommended)"). Made 2026-11-14 by the research session from `main` b5f0597 (v2026.11.13.3). Sent to the owner in chat as `dossier_fights_mockup.html`; goes to the repo's `Claude outputs/` with the build.

- `build_fights.py <repo>/index.html page.html`: the real page with one made-up pilot ("Mk Line Pilot", Mockup Coalition) whose newest 50 kills are a war weekend (a 31-pilot gang, then a 140-pilot battleship fleet) and whose small-gang and solo kills are older; 640 kills over about 18 months, 23 losses. No network, storage in memory, the page's CSP replaced. Needs `mock_fights.js`, `proto_fights.js`, `boot_fights.js` beside it.
- `mock_fights.js`: stand-in ESI and zKillboard. zKillboard's lists answer like the real API: each item the full killmail plus `zkb`, 200 a page, `/page/N/`. Fleets are expanded at load (the data stays small). Counts zKillboard requests and ESI killmail reads (`window.__MKC`).
- `proto_fights.js`: wraps the page's own `pdLoad`, `pdBuild`, `pdHtml`, `fetchKillmail`. A mockup bar above the dossier: **Today** (the page as it is) / **Proposed** (kill pages until 15 fights, a year or 3 pages; the list's killmails used without ESI; the heading line and "N fights" under Kills; the new `dossier` info line), and **Fight rule**: the Fleet tab rule as it is, or with "within 3 h".
- `boot_fights.js`: opens the Pilot Analyzer and draws Today.
- `snap.py page.html shots`: screenshots at 1440 and 390 (Today, Proposed, its rows, Small gang, the rule without the time window).
- `test_fights.py <abs path>`: at 1440 and 390, Proposed reads 1 page and 0 ESI killmails, Small gang has kills, a row's kills open, the info panel opens, no sideways scroll, no page errors (0 failed, 2026-11-14).
- Names: every pilot and group is invented ("Mk …", "Mockup …"); ship types and systems are EVE's public data. `check_pii` with the names list (fingerprint matched): 0 problems; the one embedded image is the page's own CCP login button.

Run: `python3 -I build_fights.py <repo>/index.html page.html && python3 -I test_fights.py "$PWD/page.html"`

**Built (build queue 049, 2026-11-15):** moved here from Project docs with the delivery. `Claude outputs/dossier_fights_mockup.html` was rebuilt by the build session from `main` 85e20cb (v2026.11.14.1, the page before 049, so Today still shows the old dossier and Proposed the prototype); `test_fights.py` on it: 0 failed. The prototype wraps the page before 049; built on the page after it, Today would show the delivered dossier.
