# Mockup: the Intel map's "Paths to you" mode

Made 2026-11-12 by the research session from main d227c9d (v2026.11.12.4), after the owner asked: "any chance you could mock up a mode for the galaxy map that just shows a tree view of paths to you from reported hostiles within the "near you" alert range? would basically just show possible paths to you in an easy to read structure in that short range." PLANNED 2026-11-12: roadmap/paths-to-you-plan.md; BUILT as v2026.11.12.5 (build queue 043). Sent to the owner as `paths_to_you_mockup.html` (the real page with a MOCKUP bar bottom left), now in `Claude outputs/`.

- `build_pt.py <repo>/index.html <out.html>`: the real page, made-up Intel around C-J6MT ("Mk …" / "Mockup …" names), no network, storage in memory, the page's CSP replaced. Needs `mock.js`, `proto_pt.js` and `boot_pt.js` beside it. System names: the map-look mockup's list (claude/roadmap/map-look-mockup/build_map.py).
- `mock.js`: the map mockups' runtime (roadmap/wormholes-filter-mockup/mock.js) plus made-up kills through a stand-in R2Z2 (MK.kills, as the Intel example mockup's). The page's "Kills may be missing" notice is the stand-in feed's (4 kills), not a problem. (Repo copy: the log lines' byte-order mark is written `'﻿'`, the same string.)
- `proto_pt.js`: the feature as prototyped. A seventh map filter "Paths to you" (tree icon). From itm.rep (itMapReports) it takes every hostile or neutral system within the range, and for each one every shortest gate route to you (a breadth-first search from it, as deep as its distance). Systems on several routes are drawn once.
  - Graph: top down (the owner, 2026-11-12: "give a top down orientation rather than horizontal? your system at the top"): one row per jump from you (only as far out as the farthest report), You at the top; curved gate lines with arrows up toward you, thicker where more pilots come through; hover or press a system to trace its routes (press keeps it, Esc or You clears).
  - Look (round 3, [stated] "can we try a second option that gets rid of the pills and is just borderless for each system? system name centered, relevant data below it."): Plain: no box, the name centred, what was reported centred under it, nothing under a system that's only on the way; the words sit on the map's background so lines pass behind them; your system underlined in cyan with YOU under it.
  - Round 4 ([stated] "lose the security status number (color already gives me what i need) and add badges for gate camps, ess and kills."): no security number anywhere in the tree (the name's colour; the hover still says it). A third line of badges, the page's own tags cut short: Camp, ESS, and kills per side. A system with kills and no report joins the tree from the kills alone.
  - Round 5 ([stated] "the wormhole filter button needs to be furthest right so it sits next to it's wormhole list button. also fix the orientation of the \"path to you\" filter button."): the filter goes before Wormholes; its icon is top down like the tree.
  It draws an overlay over the map's canvas inside the map box and wraps itMapDraw, itMapFLegHtml, itMapFLegTitle. MOCKUP bar: Paths / Security, post a new report (L5-UWT), jump to 8BA-RA.
- `boot_pt.js`: opens Intel, turns it on, on a phone switches Near You to the map, and picks the filter.
- `test_pt.py <out.html> <shots dir>`: 41 checks at 1440 and 390 px. All passed 2026-11-12 (the research session, and again from the repo copies at the build).
- The build differs from the mockup (the build review): the top line is the count only, the map's drag help stays under the box, the count is a 3 px tag in the kill tags' colours (the mockup's was round). See the plan's "Built" notes.

Run: `python3 -I build_pt.py <repo>/index.html paths_to_you_mockup.html && python3 -I test_pt.py paths_to_you_mockup.html shots`

## How it got here, round by round (the research session's notes, folded in from its Project copy with build queue 045)

The scripts above are the trimmed, decided version. Before the trim, the mockup offered choices the owner then decided:

- **Round 1** (2026-11-12, sent first): columns left to right, You on the right, scrolling; the phone defaulted to a List layout.
- **The choices the MOCKUP bar offered:** Range Alert (3) / Near You (6) (his words "near you alert range" fit either: Near You's is
  `nearRange` / `itNearReach`, Alert's `it.set.range`); Routes Every shortest / One each ("One each" used the map's own route,
  `itMapRoute`); Layout Graph / List; and, from round 3, Look Plain / Boxes.
- **List layout** (dropped): an indented tree from You at the top (the phone's default then), each row the system, its jumps and what was
  reported; a system reached two ways showed "N ways in" and was drawn under each (its branch "as above" the second time).
- **Round 2** ([stated] "can you modify it to give a top down orientation rather than horizontal? your system at the top (with pan and zoom
  rather than scrolling)"): Graph top down and the default on every width; pan and zoom like the map, + / − / Fit at the top right.
- **Round 3** (Look): Plain became the default, with the name and security centred at first; Boxes (round 2's boxed systems) stayed as
  the other choice until the owner picked Plain.
- **Round 4** (badges): Camp is Near You's camp tag, red from a report's camp words, orange from 2+ kills at one gate, the gate in its
  hover; ESS red when linked or hacking, white when only at it; kills per side, "N kill(s)" in the side's colour (blue a friendly lost,
  red a hostile killed, grey neutral), count and value in the hover.
- **The checks then:** 35 checks at 1440 and 390 px in round 5 (badges where Intel has them, no security number, the plain look, Boxes
  still there, top down, + / Fit, the wheel and a drag on a wide screen, a drag doesn't press a system, 9 gate lines, hover traces,
  Near You's range adding the 4-jump reports, G-EURJ's two routes against one, a new report joining, the List layout, a jump rebuilding
  it, Security hiding it, no sideways scroll, no page errors). check_pii with the names list on the mockup and its scripts: 0 problems
  (the page's own CCP login button is a reviewed image).
- **Trimmed** 2026-11-12 to the decided version (the owner's picks: the alert range, every shortest route, Graph + Plain only, a filter
  button): the Range / Routes / Layout / Look switches and the List layout came out of proto_pt.js; build_pt.py set the alert range to 4
  so G-EURJ's two routes show; test_pt.py was rewritten (41 checks, all passed).
