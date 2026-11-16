# Plan: jump bridges on the Intel map, a setting (off by default) that counts them in the map's jumps

**Status: BUILT** 2026-11-16 by the build session as v2026.11.16.5 (branch `041-jump-bridges`, pull request for build queue 041; section "Built" below says where the build differs). First planned 2026-11-12 against `main` 1e22ec7 (v2026.11.12.3, 039's map); QUEUED as 041 that day ([stated] "Yes, queue it (Recommended)"; `claude/build-queue/041-jump-bridges.md`). **Re-planned 2026-11-16 by a research session against `main` 396fbd6 (v2026.11.16.2) plus 058's plan (`claude/roadmap/intel-map-stack-plan.md`) as if 058 were built**, and checked against 057's plan (`claude/roadmap/ansiblex-zones-plan.md`), which builds on this one. Build order (the owner, 2026-11-16): 058, then 055, then **041**, then 057. Hold: lifted 2026-11-14 ([stated] "Lift hold, cleaned list only") and again 2026-11-16 ([stated] "41 is no longer on hold"). All questions answered (2026-11-12 and 2026-11-16, below). Mockup rebuilt 2026-11-16 (`jump_bridges_mockup.html`; scripts in Project docs `claude/roadmap/jump-bridges-mockup/`, README there; 66 checks pass at 1440 / 390 px; check_pii 0 problems, names checked). check_plan_sources on this version: 0 problems (8 UNVERIFIED rows, for the build and the hand test; the 5 LY / one-per-system row couldn't be settled from here: CCP's ESI copy of type 35841 is blocked for the research session). Decisions marked **D** are the sessions', not his; he can change any at the build review. Backlog: "Intel map: jump bridges, a setting (off by default) that counts them in jumps" (memory `areas/dscan-backlog-5.md`).

## The owner's words
2026-11-12:
- [stated] "add jump bridges to the map (as a setting that can be toggled off and on). when turned on, jump ranges will be calculated using bridges. default setting will be off. will be more useful later on when we add a feature to plan routes."
- The look: his screenshot of EVE's in-game 2D map: bridges as solid curved lines, bright green (#00f000 measured), red (#e80000) for others → solid curves in the game's green; red: "Green only for now (Recommended)".
- [stated] "ideally i'd like to only have near you not use bridges but i wasn't sure how possible it was." Then the Feed: "Stargate, like Near You (Recommended)". → Near You, its alerts and the Feed stay by stargate (hostiles can't use your bridges); the bridges change only the map.
- A bridge mark on Near You / Feed rows: [stated] "no".
- Other tools' formats: [stated] "find out how other eve tools get their jump bridge data for alliances", "include rift", then "yes" (research note `claude/roadmap/jump-bridges-sources-research.md`).

2026-11-14 (hold lifted): [stated] "Lift hold, cleaned list only": he pastes one bridge per line in the `A » B` form; his alliance's 9-column table is NOT a format to add. His real list is alliance data: never in the repo, checks, mockups or Project docs (made-up systems only).

2026-11-16 (this re-plan; the build session's points, his picks):
- Merge into 057 or not: "Keep separate (Recommended)": two deliveries, planned to fit each other (section "Fits with other items").
- 058's Jumps colour and "Within N jumps" with the setting on: "Both count bridges (Recommended)": every number on the map agrees with the hover; the alert glow, the Near You fade, Paths to you and the kill range stay by stargate.
- Threat Vector's route and the switch: "Switch governs both; gates until 057 (Recommended)": switch off = stargates everywhere; on, the map counts bridges in 041 and Threat Vector's route stays by stargate until 057 adds bridges by zone.
- The `intel` info cap: "Raise to 670 (Recommended)" (covers 041 and 057).
- Mockup: "Yes, rebuild (Recommended)" on today's main with 058's mockup as the map model.

## What changed since the 2026-11-12 plan (for the build review)
- Main moved past 040, 043, 044, 045, 046, 047, 048, 049, 051, 052, 053, 054; 058 replaces `itm.filter`. The plan now names today's code.
- 043 (Paths to you) takes its sources from `itm.D` and the alert range but traces routes by stargate (`T.adj`): with bridges in `itm.D` the tree would lose systems. It moves to the stargate count (D9).
- 047 (route planner): the map's drawn route and the hover's "route:" line are Threat Vector's route (`itRpParNow()` → `itRp.par`, by stargate), not `itm.par`. So 041's "routes use bridges" became: the map's counts use bridges; the drawn route stays by stargate until 057 (the owner's pick); the route line says so (D11).
- 052: the Intel settings checkbox follows rule C; the filter column is down the map's left. 058: Colour / Only / View, `tvMapStack`, new fades.
- 053 left a hook for this item: `sovBridgeEnds()` returns `[]` (D10).
- The `itmap` info panel is gone; the sentence this item makes wrong is in `intel` [Jumps and your system].
- The box goes right after Routes (it was "after Shorthands"; Routes didn't exist): D12.

## What the code does today (main 396fbd6; find by name)
- `itGraphGet()` builds the stargate graph `{ids, at, adj}` from `INTEL_JUMPS` (CCP's stargates, k-space only). `itJumps(from, to)` is a breadth-first search on it, kept per origin. Its callers (the parser's gate pairs and `J(i)`, the gate role check, `itNeighbours`, `itShortSys`, the alert ring, the kill range, Near You, the gate tag, the Feed's note / sort / distance filter, "From Intel" notes) **stay as they are**.
- The map: `itMapTable()` (`T.adj`, the stargates); `itMapBfs(home)` sets `itm.D` and `itm.par`, called by `itMapRefresh` only when your system moves (and by the Intel example's `itExMapPic`). `itm.D` is read by: the reports shown (`itMapReports`, `≤ itm.reach`), the layout's reach (`itMapLayout`), `itMapDraw` (`on(i)`, the alert glow `D[i] <= it.set.range`, the fade `D[i] > near ? 0.45 : 1`, the circle's number in Jumps), `itMapFcol` 'jumps', labels, `itPtSources` / `itPtBuild` (Paths to you), the hover `itMapTip` (header "N jumps", "past Map: within", "past the Feed's kill range" `d > itKillRange()`), the wormholes (`itMapWh` live, inside "Map: within"), Threat Vector's route lines (`itRpTipHtml` compares its path with `itm.D[i]` as "shortest", `itRpBtnsHtml`, `itRpWhereHtml`, `itRpGo` needs `itm.D[i] > 0`), the search box's "N j", pinning (`itm.D[i] > 0`).
- 047: `itRpUpdate()` searches `T.adj` (stargates) for Threat Vector's route (`itRp.par`, keyed `itRp.key`); `itRpParNow()` returns it (or `itm.par` in the Intel example, `itRpAside`, and before it's worked out); `itMapRoute(i)` follows `itRpParNow()`; the hover's "route: A → … → you" line comes from it.
- 053: `sovBridgeEnds()` (`return []`, "build queue 041 fills this in from its Jump bridges list (both ends of each bridge): the Jump bridge kind"), read by `sovIndexKey()` (joined into the key) and `sovIndex()` (`SOV_ALN`, from 'bridges'); Sov's panel shows "from Jump bridges" for that kind.
- Settings: `itDefaults()` / `itReadSet()` / `itWriteSet()` (localStorage `dscanIntel`); `itSettingsHtml(numbered)`: …, `itRpBoxHtml(numbered)` (Routes, gear only), `itAliasBoxHtml()` (Shorthands, gear only), …. Shorthands (`itAliasBoxHtml`, `itAliases`) is the model: a textarea, each line ✓/✗ below it.
- 058 (as planned): `itm.colour` ('sec' | 'jumps' | 'region' | ''), `itm.only` with Within N (`itm.D[i]` 0..N), the match set `itMapMatch()` keyed into `itMapKey`; no Only filter on: today's fades (bright within Near You, 0.45 to "Map: within", faint past it); any on: matches bright anywhere, no distance fade on dots; marks (rings, alert glow, your pin) never fade; the alert glow half size zoomed out.
- `intel` info panel: 611 of 620 words on 396fbd6 (`check_subtext.py`); 058 takes it to 619.

## Where other tools get bridge lists (research 2026-11-12, `claude/roadmap/jump-bridges-sources-research.md`)
ESI has no route that lists an alliance's bridges (request open since 2018, no CCP reply). Tools use a pasted list (Dotlan, Vintel, SMT, EVE Toolkit, Eveeye), a character's structure-name search (neocom-desk; SMT moved off it as unreliable), or a director reading the corporation's structures (server-side). The pasted list stays this plan's only source (D5); change 2 reads the formats those tools use, so a list kept for one of them pastes as it is. ("Find my bridges" with an EVE login is a separate backlog item, on hold over CCP's stance on search.)

## Changes
1. **Settings box "Jump bridges"**, gear only (not in the numbered setup), **right after Routes** (D12): a checkbox **Use jump bridges on the map** (off by default; rule C's checkbox; the row 32 px, 44 px on a phone) with the count "(N bridges)", one help line, a textarea (one bridge per line, `IT_BRIDGE_MAX` = 12,000 characters) and the checked rows under it. Help line (a `.c` line, check_subtext's cap): "One per line: `1DQ1-A » 8QT-H4`, `A → B` or two names; the rest of the line is ignored. Kept in this browser only."
2. **Reading the list** (`itBridges()`, memoised on the text and `it.names`, like `itAliases`; exposes `rows`, `edges` (map indexes), `ends` (system ids), `key`):
   - On each line the known system names (1–3 words, longest first, any case); everything else ignored. **D8:** words of digits only (SMT's structure ids, 0 for unknown) are ignored like any non-name.
   - **D7:** on a line with a separator (» « → ← -> <- <-> ⇄ ↔ =>), the bridge is the last name before the first separator and the first name after it; other names on the line are ignored (a row copied from the game may carry more columns, its own system among them). Without a separator the line needs exactly two names.
   - Formats, each a case in the check: EVE's structure name "8G-2FP » 8EF-58 - Alliance bridge", also with other text around it; "A <-> B", "A ↔ B", "A ⇄ B", "A -> B", "A → B" (SMT), "A, B", "A B", two names separated by a tab (EVE Toolkit); SMT's export `StructureID A → B`, one line per direction.
   - Rows: ✓ "A ⇄ B · 3.02 LY": counted. ⚠ counted, with why: the same system on two lines ("one jump gate per system"), more than 5 LY apart ("an Ansiblex reaches 5"). **D1:** warn, don't drop. **D6:** the same two systems as an earlier line, either direction: not counted again and not an error: a dim row "A ⇄ B · same bridge as line N", no ✗; the count counts it once. ✗ not counted: fewer than two systems ("needs two systems (found only A)"), more than two with no separator, the same system twice, a system with no stargates.
   - Not read: a Dotlan list id or a URL (a new outside host for the CSP's connect-src and the request gates; the DLA on other players' data). Paste only.
3. **Storage:** `bridges` (text, cut at `IT_BRIDGE_MAX`) and `bridgesOn` (boolean, default false) in `dscanIntel`, read in `itReadSet` like `alias`. **D2:** same key as the other Intel settings (an older cached page in another tab drops keys it doesn't know when it writes: accepted, as for `alias`). Safe both ways: an older page ignores the two keys (and may drop them on its next save, losing the list: say so in the pull request); a missing key reads as off and empty. The Intel example's sandbox `it.set` has neither (off).
4. **`itJumps` and all its callers stay as they are** (Near You, alerts, the Feed and so the kill range, the parser, every gate check), with the setting on or off. **D3:** the kill range and the parser follow the Feed.
5. **The map's search** (`itMapBfs(home)`): always a stargate pass (`T.adj`) into **`itm.Dg`**; with the setting on and at least one counted bridge, a second pass over `itBridgeAdj()` (stargates plus the bridges, both ways, each list sorted by index so there's one route per system) into `itm.D` / `itm.par`; off, `itm.D = itm.Dg` and `itm.par` the stargate parents (today's arrays). `itm.jbKey` remembers what was searched; `itMapRefresh` re-runs the search and the layout when the setting or the list's key changes (as a reach change does), and `itMapKey` includes it. A list or setting change saves, redraws the rows and calls the refresh; no timers.
6. **What reads which count** (the owner, 2026-11-12 and 2026-11-16):
   - `itm.D` (bridges counted, setting on): the reports shown and their reach, labels, the layout's reach, gates "inside the reach", the hover's "N jumps" and "past Map: within", 058's **Jumps colour** (dots and the zoomed-in number) and **Within N jumps** ("Both count bridges"), the wormholes' "inside Map: within", the search box's "N j", pinning.
   - `itm.Dg` (stargates always): the alert-range glow, the fade past Near You's range (058 keeps it only while no Only filter is on), **Paths to you** (`itPtSources` and `itPtBuild`: hostiles can't use your bridges, and the tree is traced by stargate; **D9**), the hover's "past the Feed's kill range" line (**D9**), and Threat Vector's route comparison (D11).
   - In the Intel example the setting is off, so both are the same.
7. **Drawn while the setting is on** (not in Paths to you's view, which covers the map):
   - each counted bridge a solid curved line in the game's green, new token `--it-bridge` (#00f000), under the systems, faint past the reach; curved like the game's, so it never reads as a gate;
   - **D13:** a step of a drawn route that isn't a stargate pair is drawn as that bridge's curve in the route's colour (`itMapDraw`'s route loop). In 041 only the Intel example's / not-yet-worked-out fallback (`itm.par`) can have one; 057's route will, and needs nothing more for its drawing.
8. **The hover** (`itMapTip`), setting on, a system the bridges bring nearer: under the header, "1 of the 3 jumps by jump bridge · by stargate only 10 jumps" (counted along `itm.par`; "no route" when `itm.Dg` is −1), the first part in `--it-bridge`. **D11:** while the setting is on and Threat Vector's route is by stargate (until 057), the route line reads "route by stargate: …", and `itRpTipHtml` compares the route with the stargate count (`itm.Dg[i]`, "shortest by stargate"), so it never says "Threat Vector's route: 10 jumps (shortest 3)". 057 changes both when its route takes bridges (section "Fits with other items").
9. **Notes and legend for Jumps** (058's Colour): with the setting on, the filter's note "colour: jumps from your system, your jump bridges counted"; the legend "Jumps 0 … 10+ · your jump bridges counted · grey: no route"; its title "Jumps from your system, your jump bridges counted (Intel settings), 0 to 10 or more; grey: no route to you". Within N's panel note (058: "By stargate from your system, as Jumps from you counts.") with the setting on: "From your system, your jump bridges counted, as Jumps from you counts." Off: 058's words.
10. **053's hook** (**D10**): `sovBridgeEnds()` returns `itBridges().ends`: both ends of every counted bridge (✓ and ⚠, not ✗ or D6's repeat), system ids, unique, sorted; **whatever the switch** (the Sov filter's Jump bridge kind says which systems have a bridge; the switch is about counting jumps). Memoised with `itBridges()` (053's `sovIndexKey` joins it on every call: keep it the memo's array, or key it by `itBridges().key`).
11. **Lists unchanged:** Near You and the Feed show stargate jumps and no bridge mark ([stated] "no"); a system can read 3 jumps on the map's hover and 10 in Near You, and the hover says both.
12. **Not in this delivery:** the game's red bridges ("Green only for now"); Threat Vector's route over bridges (057, by zone); **D5:** reading bridges from ESI (a structure search needs a new login scope; reported unreliable; CCP's stance on search for discovery unsettled; see Sources and the separate "Find my bridges" item); a list from a URL or Dotlan; access lists and fuel / capacitor (the tool can't know them; 057 covers the capacitor zones for routes).

## Decisions (sessions')
D1 warn, don't drop. D2 `dscanIntel` keys. D3 kill range and parser follow the Feed. D5 no ESI. D6 a reverse line is the same bridge (dim row). D7 the pair around the separator. D8 digit-only words ignored. **New 2026-11-16:** D9 Paths to you and the kill-range line on the stargate count (hostiles can't use your bridges; Paths to you's tree is traced by stargate, so its sources must be too). D10 `sovBridgeEnds()` from the list whatever the switch. D11 while the route is by stargate the hover says "route by stargate" and compares with the stargate count. D12 the box right after Routes. D13 a non-gate route step drawn as its bridge's curve (generic, for 057). (D4 was dropped at the 2026-11-12 review: `itTravel` went.)

## Fits with other items (which builds what)
- **058 (stackable filters, built first):** 041 adds no filter state; it reads `itm.colour === 'jumps'` (not `itm.filter`) for the note and legend, and gives 058's Within N `itm.D` (bridges counted when on). The alert glow and Near You fade move to `itm.Dg` inside 058's new code. 058's checks that use `itm.D` for Within N stay true with the setting off.
- **055 (Intel example controls, built second):** no new map control from 041 (the box is in Intel settings), so 055's drift check needs nothing; the example's setting is off.
- **053:** change 10.
- **047:** Threat Vector's route is untouched in 041 (stargates; the owner: "gates until 057"); `itRpTipHtml`'s comparison and the route line as in change 8.
- **057 (Ansiblex zones, built after 041):** 041 builds the list (`itBridges()`), `itBridgeAdj()`, `itm.D` / `itm.Dg`, the curves and the generic bridge-step drawing (D13). 057 builds the zones, the sov read, the one-way `itJbOut` and adds it to `itRpUpdate`. To agree with this plan, 057's plan was updated 2026-11-16 (see its note at the top): (a) its route uses bridges only while 041's switch is on ([stated] "Switch governs both"); with it off, no sov read and stargate routes; (b) its status line says "Jump bridges (below)" (the box sits under Routes); (c) when its route can take bridges, the hover's "route by stargate:" goes back to "route:" and `itRpTipHtml` compares with the shortest over the graph the route searches (stargates plus the used directions), not `itm.Dg`; (d) its "itm.D untouched" stands: the map's counts are 041's (every counted bridge).

## Questions for the owner
None open: 2026-11-12 (the look, no row mark, Near You / alerts / Feed by stargate, green only, other tools' formats) and 2026-11-16 (keep separate, both count bridges, switch governs both with gates until 057, cap 670, mockup rebuilt).

## UI rules it touches
- **Checkbox (rule C, 052)** and the global textarea: no new kinds. Rows reuse Shorthands' ✓/✗ list; the ⚠ row in `--amber`; D6's row in `--text-dim`.
- **Subtext (check_subtext):** one short help line in the box; the rest in the `intel` ⓘ panel.
- **Phone:** the checkbox row 44 px (checked at 390 px); no sideways scroll at 1440 or 390 (checked).
- **Drawing cost (LESSON #120):** no timers; the bridges are drawn in the same draw (a few dozen curves); the search runs only when the setting, the list or your system changes.
- **Colour tokens:** one new, `--it-bridge` (#00f000, the game's).
- **Map controls (rule A) / panels (rule B):** none added.
- **058's legend (one colour line, a second for Only):** the Jumps line gains a few words ("· your jump bridges counted"); the build checks it still fits one line at 1440 and 390 px, and shortens it if not.
- **Intel example (017):** unchanged (setting off; no marker or note changes).
- **Page size:** code only (a few KB of source); served 598,971 bytes on 396fbd6 (`tools/publish.py --size`), ceiling 800,000.

## Info text it touches
- `intel` [Jumps and your system] (54 → 78 words): "Your system comes from your character's Local log, or from EVE with Use my game location on (whichever is newer). Jumps are by stargate; in a wormhole, from the system you came in through. The map's drawn route follows Intel settings → Routes; its jump counts are the shortest by stargate, plus your jump bridges with Use jump bridges on the map (green curves; the alert glow and Paths to you stay by stargate)."
- **The cap** ([stated] 2026-11-16 "Raise to 670 (Recommended)"): `check_subtext.py` `INFO_ALL_MAX_BY_KEY['intel']` 620 → 670, with his words in its comment. Count: 611 on 396fbd6, 619 after 058, about 643 after 041, about 663 after 057's +20. The build recounts.
- Not `CARD_INFO`, but text this item changes: the Jumps filter note, legend and title (change 9), Within N's panel note (change 9), the hover's route line (change 8).
- `IT_EX_NOTES`: none. The old plan's `itmap` line: gone with the panel.

## CCP's Developer License Agreement
Not touched in a way that needs a decision: no request to CCP's servers; the list is the user's own (their alliance's structures, pasted by them), kept in their browser, never sent or shared. Not other players' activity (2.3(c)).

## Checks
`intel_bridges_check.py` (new), made-up systems only (start from the mockup's `test_jb.py`):
- the formats in change 2 (structure-name tails, », →, ->, <->, ⇄, comma, space, tab), SMT's two-line form with ids (one bridge, D6's dim row, counted once, no one-per-system warning from it), a separator line with a third name (D7), a third name with no separator (✗), case, 3-word names, the same bridge again either direction, the same system twice, one system, unknown names, the one-per-system and 5 LY warnings;
- every `itJumps` caller gives the same answer on and off (Near You, alerts, Feed, kill range, parser, gate checks);
- `itm.D` shorter where a bridge helps, never longer than `itm.Dg`; `itm.Dg` equals the stargate count; off: `itm.D` equals `itm.Dg`;
- the glow and the Near You fade follow `itm.Dg`; Paths to you's sources and tree by stargate (a hostile 3 by bridge, 10 by gate, outside the alert range 4: not a source); the kill-range line by stargate;
- 058: Jumps colour and Within N count bridges on, not off; the legend and notes;
- the hover's line; "route by stargate:"; Threat Vector's route compared with `itm.Dg` (never "shortest 3" for a 10-jump stargate route);
- `sovBridgeEnds()`: both ends of ✓ and ⚠ rows, none from ✗ or the repeat, the same on and off; 053's Jump bridge kind lights those systems;
- the curves drawn on, none off; a non-gate route step drawn as a curve (D13, with a made-up `itm.par` fallback);
- the setting and list survive a reload; an old saved setting without the keys reads as off; the Intel example unchanged;
- 1440 and 390 px, no sideways scroll, no page errors.
Mutants: Near You or an alert counting a bridge; bridges counted on the map while off; Paths to you on `itm.D`; a reverse line shown as ✗; a separator line refused for a third name; `sovBridgeEnds()` empty while the switch is off.
Also: `check_subtext.py` (the new cap), `check_ui_rules.py`, `check_pii`, `run_checks.py --served`; 058's and 043's checks still pass.

## Hand test (owner)
Setup:
```
git fetch origin
git switch 041-jump-bridges
python3 -m http.server 8000
```
Open http://localhost:8000. Afterwards: Ctrl+C, then `git switch main`.
1. Intel settings (gear): the Jump bridges box sits under Routes. Paste your cleaned list (one `A » B` per line), tick "Use jump bridges on the map". The rows should all read ✓ (or ⚠ where a system is on two lines). Check a few systems' jump counts on the map's hover against EVE's autopilot with bridges allowed; Near You's numbers don't move.
2. In game, copy a few bridge rows (the structure browser, or the bridges on D-Scan) and paste them as they come: each should read as its bridge (settles the "A » B - name" and copied-row rows in Sources).
3. Colour by Jumps and turn on Within N jumps: both count your bridges; untick the setting: both go back to stargates. Paths to you and the amber glow don't change either way.
4. Sov upgrades: the Jump bridge kind lists your bridges' systems, with the setting on or off.
5. Check the 5 LY / one-per-system warnings against an Ansiblex's show info in game, if a row shows one (Sources).

## Mockup
`jump_bridges_mockup.html` (rebuilt 2026-11-16): the real page at main 396fbd6 with 058's stacked-filters prototype loaded as the map model (its MOCKUP rows still work), made-up Intel around C-J6MT (058's, plus hostiles in 8EF-58 and F39H-1) and a made-up list of 8 lines: 3 good, 1 counted with both warnings, 1 copied row with a third system (D7), 1 SMT line with an id (D8) and its reverse (D6's dim row), 2 refused. Opens coloured by Jumps with the setting on: on the map 8EF-58 is 3 jumps and F39H-1 2 (by stargate 10 and 11), Near You stays at 10 and 11; the MOCKUP box's "Jump bridges On / Off" and "Intel settings: Jump bridges box". 66 checks (`test_jb.py`) pass at 1440 and 390 px. Built by `build_jb.py` (058's nine hooks plus five for 041) with `proto_jb.js` and `boot_jb.js`; shortcuts the build must not copy are in its README. Commit it to `Claude outputs/`.

## Built (2026-11-16, the build session, v2026.11.16.5)
Built as planned on main 67a9828 (058 and 055 merged). Where the build differs or adds:
- **058's state is `itMapSt()` (`itm.st`)**, not `itm.colour`: the notes and legend read `itMapSt().colour` through 058's own builders (`itMapFLegHtml`, `itMapFLegTitle`, `itMpBodyHtml`), and the Jumps filter's note is `itMapFNote(f)` (also the button's title, set again when the count changes).
- **The match set's key** (`itMapMatch`, `itMt.key`) gains `itm.jbKey` (found at the review): without it, Within N and the "N match ›" chip's nearest-first order kept the old count after the setting or the list changed. The comment there no longer says "by stargate".
- **`itRpWhereHtml`'s "no gate route"** reads `itm.Dg` (the build's call: it means a stargate route). Not in the plan's list of readers; with bridges counted `itm.D` and `itm.Dg` are both −1 or neither in practice.
- **The 5 LY warning** compares the distance as shown (rounded up to 0.01, `itMapLyText`), so a row reading "5.00 LY" never warns; 057's zone 1 edge is the same 5.00.
- **The one-per-system wording** says "one jump bridge per system" (the plan's "one jump gate").
- **Names not loaded yet:** the rows say "Checked once the system names are loaded…" and the box asks for them (`itBridgeNamesLoad`, as Sov's paste); nothing is counted until they are in.
- **Typing:** the rows and the count are written in place on every input (`itBridgePaint`), the card isn't redrawn while the settings are in use (its own rule), and the map searches again only when what's counted changed (`itm.jbKey`). Long lists scroll inside the box (240 px).
- **D8** (digit-only words ignored) is kept, but no system's name is digits only, so it changes nothing today and has no mutant.
- **The check** (`intel_bridges_check.py`): the mock's names are one word, so the 3-word case isn't run; Near You's reach stops at the Feed's kill range (10), so the counts are checked on two bridges (to 9 and to 12 jumps out). 15 mutants, each fails.
- **Sources:** the three Ansiblex rows are now verified from CCP's data in pyfa's copy (type 35841); five stay UNVERIFIED (two for the hand test: the in-game name, a copied row; three about ESI's search, context only).
- **The mockup** was rebuilt by the build session exactly as made (396fbd6's page, the repo's 058 scripts; 66 of 66 checks) and committed as `Claude outputs/jump_bridges_mockup.html`, its scripts in `roadmap/jump-bridges-mockup/`.

## Sources
| Fact | Source | Checked | Status |
|---|---|---|---|
| Ansiblex bridges work in pairs, connecting the two systems | https://github.com/pyfa-org/Pyfa at e5483f8 (v2.70.0), `staticdata/fsd_built/types.*.json` and `typedogma.*.json`: CCP's SDE as pyfa ships it, type 35841, its description ("a matched pair of bridges provides a transport connection between two star systems"); first from https://wiki.eveuniversity.org/Ansiblex_Jump_Gate (secondary source: wiki) | 2026-11-16 (the build) | verified |
| Maximum jump range 5 LY; one jump gate per system | https://github.com/pyfa-org/Pyfa at e5483f8 (v2.70.0), `staticdata/fsd_built/types.*.json` and `typedogma.*.json`: CCP's SDE as pyfa ships it, type 35841: attribute 867 `jumpDriveRange` 5.0, and its description ("A maximum of one Jump Bridge may be deployed per system."); first from https://everef.net/types/35841 (secondary source) | 2026-11-16 (the build) | verified (only used for the rows' warnings) |
| Needs a sovereignty hub upgrade to run (so sov null only) | https://github.com/pyfa-org/Pyfa at e5483f8 (v2.70.0), `staticdata/fsd_built/types.*.json` and `typedogma.*.json`: CCP's SDE as pyfa ships it, type 35841, its description (its service module "may only be onlined in a system that contains a sovereignty hub with the Advanced Logistics Network upgrade active") | 2026-11-16 (the build) | verified (not used by the code; context only) |
| Ansiblex use costs capacitor by distance from the alliance capital (2026-09-15); live since Cradle of War, 2026-09-22 | https://www.eveonline.com/news/view/major-update-force-projection-revamped and https://www.eveonline.com/news/view/cradle-of-war-major-update-is-live (CCP) | 2026-11-12 | verified (why the map counts a bridge but can't say it's cheap; 057 covers zones) |
| No bridges in CCP's static data; the page's jumps are stargates only | `tools/jump_table_update.py` and `INTEL_JUMPS` in index.html (main 396fbd6) | 2026-11-16 | verified |
| ESI has no route listing jump bridges (request open since 2018, no CCP reply) | https://github.com/esi/esi-issues/issues/1084 (CCP's ESI issue tracker) | 2026-11-12 | verified (why the list is pasted) |
| The authenticated search /characters/{character_id}/search/ adds a structure category for structures the character can access | https://developers.eveonline.com/blog/simplify-esi-queries-by-using-search (CCP's developer blog) | 2026-11-12 | verified (context for D5) |
| Reading one structure needs esi-universe.read_structures.v1 and docking access; corporation structures need esi-corporations.read_structures.v1 and a Director | https://docs.esi.evetech.net/docs/scenarios/resolve_structure_ids.md (CCP's ESI docs) | 2026-11-12 | verified (why D5 leaves ESI out) |
| The search needs esi-search.search_structures.v1 | https://bitbucket.org/daimian/tripwire/issues/513/the-route-used-by-esisearch-is-no-longer (secondary source: Tripwire's issue tracker) | 2026-11-12 | UNVERIFIED: CCP's ESI spec in the owner's browser, before any ESI phase |
| CCP asks tools not to use /search as a workaround for discovery | https://github.com/esi/esi-issues/issues/616 (CCP's ESI issue tracker); a community member says the same on issue #1084 | 2026-11-12 | UNVERIFIED: read CCP's linked blog post before any ESI phase |
| ESI's structure search returns fewer results than expected (why SMT added a paste import) | https://forums.eveonline.com/t/smt-eve-map-tool/3845?page=12 (secondary source: SMT's author, citing esi-issues #108) | 2026-11-12 | UNVERIFIED: only context for D5 |
| List formats other tools read: SMT `StructureID A → B` one line per direction; EVE Toolkit "A » B - name", "A <-> B", tab-separated | https://forums.eveonline.com/t/smt-eve-map-tool/3845?page=12 (secondary source: SMT's author's forum post); https://github.com/mrdave80/eve-toolkit (secondary source: the project's README) | 2026-11-12 | verified as what those tools say they read (the formats are test cases, not CCP facts) |
| EVE's 2D map draws bridges as solid curved lines, green (#00f000) and red (#e80000) | the owner's in-game screenshot (live game, primary) | 2026-11-12 | verified (colours measured from the picture) |
| In-game bridge structures are named "A » B - name" | https://github.com/mrdave80/eve-toolkit and https://github.com/shawndibble/neocom-desk/pull/2512 (secondary source: other tools' docs; no CCP document found) | 2026-11-12 | UNVERIFIED: hand test step 2 (the parser reads any separator anyway) |
| What a bridge row copied from the structure browser or D-Scan carries | https://wiki.pleaseignore.com/training:smt (secondary source: wiki; says lines need reformatting for SMT) | 2026-11-12 | UNVERIFIED: hand test step 2 (D7 is why it shouldn't matter) |
