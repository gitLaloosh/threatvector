# Plan: the Intel map's "Paths to you" filter

**BUILT** as v2026.11.12.5 (build queue 043, branch `043-paths-to-you`). The build differs from this plan in these ways, all from the build review (2026-11-12):
1. **Info text** ([stated] "your suggestion is fine"): `intel` [Map] reads "The bottom bar picks what it shows; Paths to you draws the routes from hostiles in your alert range as a tree." To stay within the panel's 410 words, the hide-friendlies note left [Alerts] (now in METHODOLOGY.md's Near You part) and "(10 jumps unless you change it)" left [Kills] (METHODOLOGY.md already says it).
2. **The top line** ([stated] "sounds good"): "N systems with hostiles" (or "No hostiles within R jumps"), not item 8's longer line, which was cut off at most widths (205 px of a 369 px box at 905 px). The range stays in the legend line; the map's own drag help under the box stays visible (item 9 hid it).
3. **The count** ([stated] "good call"): a 3 px-corner tag in the kill tags' colours (`.it-kl kh` hostile, `kn` neutral), not the mockup's round pill (the tag rule: never round).
4. **Sources**: a hostile or neutral report, or kills, as item 2 says (the mockup took hostile and neutral only); never a clear.
5. **Wormholes** don't show in the tree (stargate routes only; the canvas with their rings is hidden under it); the tree has its own text compare, so `itMapKey` is unchanged.
6. **Drawing**: an HTML overlay (`itPt`, `itPtPaint`); the galaxy's canvases are hidden and not drawn while it's on. It is built from `itMapDraw` and, when the map's key didn't change, from `itMapRefresh`, and written only when its text changed; ages on the card's clock (`it.drawNow`).
7. **The Intel example's picture** borrows `itm` with its own canvas: `itPtLive` answers only for the live canvas, so drawing the picture never hides the tree.
8. **Shared rules**: `itEssTagHtml` (now Near You's too), `itGateTagHtml(st, now, true)` (Camp only, no grey gate tag, no "toward you"), `itKillBadges(ks, 0, true)` ("N kills").
9. **The check** (`paths_to_you_check.py`) jumps to a made-up area 11 jumps from the stand-ins' 1DQ1-A, whose surroundings have no loop to test "every shortest route" on.

Status: PLANNED 2026-11-12 by a research session from main d227c9d (v2026.11.12.4, after build queue 040). QUEUED as 043 ([stated] "add it to the queue"; `claude/build-queue/043-paths-to-you.md`). All of the owner's questions answered. Mockup: `Claude outputs/paths_to_you_mockup.html` (sent to the owner 2026-11-12, five rounds; scripts in Project docs `claude/roadmap/paths-to-you-mockup/`, README there). Line numbers are approximate (main d227c9d); find things by name.

Backlog: "Intel map: "Paths to you" mode (a tree of routes from hostiles near you)" (areas/dscan-backlog-5.md).

## The owner's decisions (2026-11-12)
- The ask: [stated] "any chance you could mock up a mode for the galaxy map that just shows a tree view of paths to you from reported hostiles within the "near you" alert range? would basically just show possible paths to you in an easy to read structure in that short range."
- Top down, pan and zoom: [stated] "can you modify it to give a top down orientation rather than horizontal? your system at the top (with pan and zoom rather than scrolling)"
- No boxes: [stated] "can we try a second option that gets rid of the pills and is just borderless for each system? system name centered, relevant data below it." Then [stated] "this is the one i want to go with" for "Graph with the Plain look": the List layout and the Boxes look are dropped.
- Badges, no security number: [stated] "lose the security status number (color already gives me what i need) and add badges for gate camps, ess and kills."
- The button: [stated] "the wormhole filter button needs to be furthest right so it sits next to it's wormhole list button. also fix the orientation of the "path to you" filter button."
- Range: [stated] "alert range" (Intel settings "Alert: within", `it.set.range`; not Near You's range).
- Routes: [stated] "every shortest route" (not the map's one route per system).
- Where: [stated] "filter button is fine for now." (a map filter, not a view of its own).

## What to build
1. **A seventh map filter, "Paths to you"** (`IT_MAP_FILTERS` ~29210), inserted **before** `wh`, so Wormholes stays last with its list button (`itMapFbtnsHtml` ~28993, `[data-it-whl]`) right after it. Note: "the gate routes from hostiles inside your alert range to you, as a tree". Icon: the mockup's top-down tree (`proto_pt.js` `ICON`: you, filled, at the top; three systems below; lines up to you). Not remembered across visits, like the other filters (the map starts on Security, 039).
2. **What's in the tree** (from `itm.rep`, `itMapReports` ~28968, so the time window, "hide friendlies" and the map's reach rules are Intel's own):
   - sources: every system whose report is hostile or neutral (`side` 'hostile' / 'neutral'), or that has kills, and is within the alert range (`itm.D[i] <= it.set.range`); a system with only kills joins from its kills;
   - for each source, **every shortest gate route** to you: a breadth-first search from the source over the map table's gates (`itMapTable().adj`), no deeper than its own distance; a system x is on a route when `itm.D[x] + d_source(x) === itm.D[source]`; a gate x→y is on it when both are and `itm.D[y] === itm.D[x] − 1` (`proto_pt.js` `build()`);
   - a system on several routes is drawn once (shared gates read as one trunk); the gates are stargates only (`itm.D`), as everywhere in Intel today.
3. **The layout: top down.** Your system at the top; one row per jump (rows only as far as the farthest source); each row placed under the systems it leads into (the average of their places, pushed apart to not overlap), row 1 spread under you; row labels "You", "1 jump", "2 jumps"… on the left. Curved gate lines from each system up to the nearer one, an arrowhead pointing toward you, thicker where more pilots come through (`1.4 + pilots / 3`, at most 5 px). Line colour the Hostile red (`--danger`) at low opacity.
4. **The look: plain.** No box, no border: the system name centred, in Intel's security colour (`.it-sn s0–s10`), **no security number** (the hover title keeps it: "C-J6MT (-0.3) · 2 jumps from you"). Under it, centred, what was reported: a count badge (red hostile, grey neutral) + the ships (or "hostiles" / "neutrals") + the age; nothing for a system that is only on the way; your system: "YOU" in cyan and the name underlined in cyan. The words sit on the map's background colour so the lines pass behind them.
5. **Badges** (a third centred line; the page's own tags, cut short):
   - **Camp**: Near You's camp tag (`itGateTagHtml` ~28003, inside `itNearTagsHtml` ~27975): red from a report's camp words, orange from 2+ kills at one gate; the word "Camp" only, the gate and why in its hover (the tag's own title). The grey "<gate> gate" tag (no camp words) is not shown;
   - **ESS**: `.it-ess` (linked / hacking, red) or `.it-essat` (only at it), as in Near You;
   - **Kills**: one per victim side, "N kill(s)" in `.it-kl kf/kh/kn` colours (friendly lost / hostile killed / neutral), the count and ISK (`itIsk`) in its hover; from the state's live kills (`st.kills` with `t` inside "forget reports after", as `itKillBadges` ~28119 counts them).
   - The build should share one helper for these with Near You (no second copy of the camp rule).
6. **Hover and press**: hovering (or focusing) a system lights its routes: every gate toward you and back toward what feeds it, for the sources whose routes go through it; the rest fades. Pressing keeps that light; pressing it again, pressing You, or Esc clears it. Each system is a `<button>` (keyboard reachable; a drag that moved never counts as a press).
7. **Pan and zoom, not scrolling** (the map's own rules, `itMapBind` ~29708): a mouse drags to move and the wheel zooms about the pointer (the page doesn't scroll over it); on touch, two fingers move and pinch, one finger scrolls the page. Top-right controls + / − / Fit (the map's `.it-map-zoom` style; 44 px on a phone). Fitted when shown and again when your system or the alert range changes or the box is resized; otherwise kept. Zoom 0.3–2.5; a phone fits at no less than 0.75, centred on you (a whole wide tree would be too small to read).
8. **Header and legend**: a context line top left inside the box: "N systems with hostiles within R jumps (your alert range) · drag to move · wheel to zoom" (phone: "two fingers move and zoom"), or "No hostiles within R jumps (your alert range)". The map's legend line (`itMapFLegHtml` / `itMapFLegTitle` ~29446): "Paths to you ■ hostile ■ neutral · within R jumps (your alert range) · lines point toward you".
9. **While it's on**: the map's own zoom buttons, the "you" arrow, "Hide all routes" and the drag help are hidden (the tree has its own); other filters are untouched; Security etc. bring the map back as it was.

## How to draw it (drawing cost, LESSON #120)
- The prototype draws an HTML/SVG overlay inside `itm.box` over the canvas (buttons for keyboard and hover titles, the page's tag classes reused); keep that or draw on the canvas, the build's call, but the systems must stay keyboard reachable.
- Built only from `itMapDraw`'s refreshes and only when its own key changes: the sources, their counts and sides, kills, camp/ESS tags, your system, the alert range and the box size. No timer of its own. Ages: rebuilt with Intel's existing age refresh (`itAgePeriod` ~28852), not every 2 s.
- Built only while the filter is on and the map is shown (`itMapVisible`); the overlay is hidden otherwise. Pan and zoom move one transform (no rebuild).
- The prototype's draw must never run before the map box exists: the owner hit "Cannot read properties of undefined (reading 'insertBefore')" in round 3 (fixed in the mockup by a guard).

## UI rules it touches (CLAUDE.md "UI rules", check_ui_rules)
- **Tags**: the badges are the page's existing tags (`.it-gtag.camp`, `.it-ess`, `.it-essat`, `.it-kl`), cut to a word; no new tag style. The count badge reuses the mockup's small round count (`pt-n`): the build should use an existing count style if one fits (open point for the build review, not a new rule).
- **Colours**: tokens only (`--danger`, `--cyan`, the security classes, the kill classes); the neutral grey matches the map's `neutral` colour (#b9c3ca, as `itMapDraw`'s `C.neutral`).
- **Map filter bar** (039, 040): seven buttons; on a phone the row wraps and Wormholes + its list button stay together (seen in the mockup at 390 px; 040's both-edges anchoring, LESSON #161).
- **Phone**: 44 px zoom buttons; no sideways page scroll at 390 px (checked); the map box is ~330 px tall there, so a big tree is panned with two fingers.
- **One chevron / close buttons**: none added. **Drawing cost**: above.
- **Intel example (017)**: no change: the example's picture shows no filter bar (`itMapYouArrow` note ~29117), so its markers and notes stay.

## Info text it touches
- `intel` "[Map]" (~3485): "… The bottom bar picks the colours." → add: "Paths to you shows the routes from hostiles in your alert range as a tree, you at the top." Keep it under check_subtext's cap (re-measure).
- The filter's own note (its button title and the legend line): as in item 1 and 8.
- None other (the [Tags] line already explains Camp and ESS).

## Stored data, requests, DLA
- Nothing stored (no new key; the filter isn't remembered). No requests (everything is Intel's own data already in the page). DLA: nothing new about other players beyond what Intel already shows, nothing kept or sent: no clause touched.

## Checks to build
`paths_to_you_check.py` (new; the mockup's `test_pt.py` is the starting list): seven filters with `paths` just before `wh` and the list button after `wh`; with made-up reports and kills, the systems drawn are exactly the sources in the alert range, the systems on their shortest routes and you; a system with two equally short routes gets both gates; top down (you above all); no security number; badges Camp / ESS / kills only where Intel has them; hover traces the right systems; + / − / Fit, wheel and drag (a drag presses nothing); a new report joins; a jump rebuilds from the new system; another filter hides it; no sideways scroll at 390 px; no page errors; redraws only when its key changes (count builds). Mutants: one route per system (the map's) instead of every shortest; Near You's range instead of the alert range; the security number back; Wormholes no longer last. Update `intel_map_look_check.py` / `wormhole_filter_check.py` where they count six filters.

## Where to look (main d227c9d)
`IT_MAP_FILTERS` ~29210, `itMapFbtnsHtml` ~28993, `itMapFilterSet` ~29011, `itMapReports` ~28968, `itMapDraw` ~29253, `itMapKey` ~29077, `itMapRefresh` ~29042, `itMapTable` ~28934, `itMapRoute` ~29202, `itMapLegend` / `itMapFLegHtml` / `itMapFLegTitle` ~29446–29466, `itMapBind` ~29708 (the map's pan/zoom rules), `itNearTagsHtml` ~27975, `itGateTagHtml` ~28003, `itKillBadges` / `IT_KILL_WORD` ~28116, `itLive` ~26953, `itAgo` ~27805, `itAgePeriod` ~28852, `.it-map-zoom` ~2661, `.it-map-fb` ~2689. Prototype: `claude/roadmap/paths-to-you-mockup/proto_pt.js` (`build()`, `draw()`, `tagsHtml()`, `bindView()`).

## Mockup
`paths_to_you_mockup.html` (the real page at main d227c9d, made-up Intel around C-J6MT, alert range set to 4 so G-EURJ's two routes show; made-up kills through a stand-in R2Z2, so the Feed's "Kills may be missing" notice is the stand-in's). MOCKUP bar: Paths to you / Security, post a report, jump to 8BA-RA. `test_pt.py`: 41 checks at 1440 and 390 px, all passed 2026-11-12; check_pii 0 problems with the names list (round 4; the final trim only removed code). The build session copies the HTML into the repo's `Claude outputs/` (rebuild with `build_pt.py` if needed).

## Panel review
Not a fit (the owner's eye judged the look; the routes are settled by code and the checks).

## Sources
Sources: none (no outside facts). Everything here is the project's own code (main d227c9d) and the owner's decisions.
