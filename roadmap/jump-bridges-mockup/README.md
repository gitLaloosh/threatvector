# Jump bridges mockup (build queue 041; plan roadmap/jump-bridges-plan.md)

Rebuilt 2026-11-16 by a research session on main 396fbd6 (v2026.11.16.2), with 058's stacked-filters prototype as the map model
([stated] "Yes, rebuild (Recommended)"). Replaces the 2026-11-12 mockup built on 039's map (its boot_map.js, mock.js and snap_jb.py
are gone). Everyone and every group is invented ("Mk ..." / "Mockup ..."); systems and ship types are EVE's public data; the structure
names and ids in the list are made up.

    git show 396fbd6:index.html > old/index.html
    python3 -I build_jb.py old/index.html <stk dir> jump_bridges_mockup.html
    python3 -I test_jb.py jump_bridges_mockup.html shots/

`<stk dir>` holds, unchanged: `proto_stk.js` and `boot_stk.js` (the repo's roadmap/map-filter-stack-mockup/) and `mock.js` (the repo's
roadmap/paths-to-you-mockup/mock.js). The hooks target the page as it was at 396fbd6 (before 058 was built), so the mockup is built from
that commit's index.html, not today's.

Committed with the build (pull request for build queue 041, v2026.11.16.5): the build session rebuilt it exactly so (396fbd6's page, the
repo's 058 scripts) and all 66 checks passed; the HTML is `Claude outputs/jump_bridges_mockup.html`.

## Files
- `build_jb.py`: 058's build_stk.py (its made-up Intel, sov list and wormholes, its nine hooks) plus two reports (8EF-58, F39H-1),
  Near You 12 / map 14 jumps, and five 041 hooks, each asserted to be found once: the alert glow and the Near You fade on `itm.Dg`,
  Paths to you's `itPtSources` / `itPtBuild` on `itm.Dg`, the hover's kill-range line on `itm.Dg`. Also 058's Within N note says
  "your jump bridges counted" while the setting is on.
- `proto_jb.js`: `itBridges()` (change 2: the pair around a separator, D7; digit-only words ignored, D8; the reverse line a dim repeat,
  D6; ✓ / ⚠ / ✗), `itBridgeAdj()`, `itMapBfs` (`itm.D` / `itm.par` with bridges while on, `itm.Dg` by stargate always),
  `sovBridgeEnds()` (053's hook, whatever the switch), the green curves (`--it-bridge` #00f000), the hover line and "route by
  stargate:", `itRpTipHtml` compared with `itm.Dg`, the Jumps note / legend / title, the settings box right after Routes.
- `boot_jb.js`: after 058's boot: a made-up list of 8 lines (EVE's structure name; SMT's arrow; SMT's export with an id and its
  reverse; a copied row with a third system; one with both warnings, 5.30 LY; two refused), the setting on, coloured by Jumps; the
  MOCKUP box's "Jump bridges On / Off" and "Intel settings: Jump bridges box".
- `test_jb.py`: 66 checks at 1440 and 390 px, a fresh page per size: the rows and count, D6-D8, the warnings, `sovBridgeEnds()` (9
  ends, on and off), the map 3 / 2 jumps vs stargate 10 / 11 with `itJumps` and Near You unchanged, D never longer than Dg, green
  drawn on and none off, the hover lines, the kill-range line by stargate, Paths to you's sources by stargate, the Jumps legend,
  058's Within 3 matching by bridge, off = stargates everywhere, the box right after Routes (32 / 44 px row, 8 rows, the repeat dim
  with no ✗), editing the list, stored in `dscanIntel`, no sideways scroll, no page errors.
- check_pii with the names list (fingerprint matched) on the mockup and these scripts: 0 problems (the page's CCP login button image
  is on the reviewed list).

## Shortcuts the build must not copy
- Function overrides by name (`itMapBfs`, `itMapDraw`, `itMapKey`, `itMapTip`, `itRpTipHtml`, `itMapFLegHtml`, `itMapFLegTitle`,
  `itSettingsHtml`, `sovBridgeEnds`) and a getter on the Jumps filter's note; the build writes these into the page's code.
- The five hooks fall back to `D` when `itm.Dg` isn't set (the Intel example draws before proto_jb.js loads); the build sets
  `itm.Dg` in `itMapBfs` every time.
- 058's own shortcuts (its README): its overrides and hooks, the stack in memory, popovers placed by hand.
- The list is re-read from `dscanIntel` at load because the page's `itReadSet` drops unknown keys; the build reads them there.
- Storage is in memory (mock.js), so a reload starts over.
