# Mockup: Threat Vector's route by Ansiblex zone (Project doc claude/roadmap/ansiblex-zones-plan.md)

Made 2026-11-16 by a research session from `main` 51207b6 (v2026.11.16.1). Sent to the owner as `ansiblex_zones_mockup.html`.
The real page with made-up Intel around C-J6MT, a made-up ESI sovereignty answer (Mockup Coalition holds the area, capital
8G-2FP; Mockup Raiders hold SHBF-V, 0UBC-R, RERZ-L, 9N-0HF, capital SHBF-V) and four made-up bridge lines. Everyone and every
group is invented ("Mk ..." / "Mockup ..."); systems and ship types are EVE's public data.

    python3 -I build_az.py <repo>/index.html ansiblex_zones_mockup.html   (mock.js, proto_az.js, boot_az.js beside it)
    python3 -I test_az.py ansiblex_zones_mockup.html shots                 (Playwright: 1440 and 390 px)

- `mock.js`: the repo's `roadmap/paths-to-you-mockup/mock.js`, unchanged (not copied here, to save Project space).
- `build_az.py`: the page, the data, two hooks in `itMapDraw` (the bridges drawn before the routes; a route's bridge step as a curve).
- `proto_az.js`: the prototype. **041 isn't built, so it carries a stand-in Jump bridges box** (reads "A » B" lines only).
  Shortcuts the build must not copy: function wraps by name (`itRpUpdate`, `itMapTip`, `itRpTipHtml`, `itRpSubHtml`,
  `itRpBoxHtml`, `itRpRefresh`), `T.adj` swapped during `itRpUpdate`, `itm.D` swapped during `itRpTipHtml` (for "(shortest N)"),
  the sov answer faked in `fetch`, the zones in memory.
- `boot_az.js`: opens Intel, reads the made-up sov, fills the list, zooms in on you, shows the MOCKUP box (logged in / out,
  capital lost, you in C-J6MT / F39H-1, Intel settings).
- Bridge distances measured with the page's own `itMapLy`: 8G-2FP ⇄ 8EF-58 3.01 LY (zone 1 both ways); 4M-QXK ⇄ F39H-1 4.96
  (F39H-1 6.01 LY from the capital: out zone 2, home zone 1); 3AE-CP ⇄ EUU-4N 1.07 (both zone 2); SHBF-V ⇄ WF4C-8 4.12 (⚠ Raiders).
- Results 2026-11-16: 58 of 58 checks pass (`test_az.py`): zones and use per row; route to 8EF-58 3 jumps by the free bridge
  (10 by gates, `itm.D` unchanged); F39H-1 by gates until zone 2 is ticked; from F39H-1 home in 1 jump; logged out a two-alliance
  bridge left out and your own still used; capital lost → all zone 5, none used; bridge hover and route step lines; the menu's
  "3 jumps · 1 by jump bridge"; zone rows 44 px on a phone; no sideways scroll; no page errors.
- check_pii with the names list (fingerprint matched) on the mockup and these scripts: names clean; only the page's CCP login
  button image flagged (expected; reviewed in the repo's list).
- **Rebuilt 2026-11-16 for 041's re-plan** (plan section "Since 041's re-plan"; [stated] "yes please"): the stand-in box sits right
  after Routes (041 D12); its "Use jump bridges on the map" governs the route (off: stargate routes, rows without zones (D7), the
  status says so); "(shortest N)" over the route's own graph; status lines name "the Jump bridges box" (the settings grid can put it
  beside Routes, so no "below"). 74 of 74 checks pass (16 new: the switch off and on, the box after Routes, no "Threat Vector's
  route" line when the route is the shortest). check_pii rerun without the names list (only code changed, no names added): only
  the login button image.
- **In the repo since build queue 057** (v2026.11.16.6; the owner at the build review: "Commit as approved (Recommended)"): the
  mockup in `Claude outputs/ansiblex_zones_mockup.html` is the one he approved, built again by these scripts from 51207b6's page,
  so it shows 041's stand-in box and none of 057's later changes (the map's counts, the 70% bridge colour). Build it with
  `mock.js` copied in beside these scripts from `roadmap/paths-to-you-mockup/`.
