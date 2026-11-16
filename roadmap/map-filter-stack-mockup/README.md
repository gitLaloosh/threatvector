# Mockup: the Intel map's filters stacked (prototype of the panel review's model)

Made 2026-11-16 by the research session from `main` 51207b6 (v2026.11.16.1, after 053), after the owner read the panel review brief (`claude/roadmap/map-filter-model-panel.md`): [stated] "since you provided recommendations, how about you build a prototype using them and i'll decide after." Sent to him as `stacked_filters_mockup.html` (the real page, made-up Intel and sov list, a MOCKUP box top right; on a phone bottom left, folded). Planned 2026-11-16 (`claude/roadmap/intel-map-stack-plan.md`); not queued.

**Decided 2026-11-16** (the owner's answers to Q1-Q21, recorded in the brief section 6 and in the plan `claude/roadmap/intel-map-stack-plan.md`): the MOCKUP box's defaults are his picks. Its other buttons show alternatives he turned down: Colour "Full", Region colours "Today", Matches "Brighter", Alert glow "Today", Wormholes "Thin rings".

## What it shows (the brief's recommendations, as built here)

- **The filter column in three groups**, split by thin lines:
  - **Colour** (one pressed, or none): Security, Jumps from you, Region.
  - **Only** (any number, each on or off): Security range, Within N jumps, Intel reports, Kills, Wormholes, Sov upgrades. Each keeps its settings while off. A condition with settings has a panel button beside it (as 052's).
  - **View**: Paths to you, as today; leaving it keeps the colour and the stack.
- **No colour** ([stated] 2026-11-16, after the second version, with screenshots of Region, Jumps and Security zoomed in: "my one remaining concern right now, is that i can't toggle anything "off". this isn't an easy view to read."): pressing the colour that is on turns colour off. Every system is a plain grey (`#56616b`), with no number in its circle; the legend's first line reads "No colour … press Security, Jumps or Region to colour them"; no colour button is pressed; the stack is kept. Pressing a colour turns it back on. A fifth hook in the page skips the circle's number.
- **Soft colour** ([stated] 2026-11-16, explaining the screenshots: "it's about the base color groups sort of washing out the other data but the off switch for color groups is welcome too."): MOCKUP box "Colour": Full (today's look) / Soft (default). Soft draws a system's colour mixed 45% toward the map's background when zoomed out, and zoomed in a dark disc tinted with the colour (38% colour) instead of a solid one, so rings, tags and labels stand out. A system your conditions match keeps the full, solid colour. A first try drew a dark circle with a coloured outline; it was dropped because a coloured outline reads as a report ring (a red one as hostiles): on this map a ring means a report. A sixth hook in the page draws the zoomed-in disc.
- **Smaller alert glow** ([stated] 2026-11-16: "can we make the yellow background circles for "within your alert range" a bit smaller? maybe try 50% of current diameter?"): MOCKUP box "Alert glow": Today / Half, zoomed out (default). Zoomed out, half the diameter; zoomed in, today's (r + 9) ([stated] after trying a zoomed-in r + 4.5: "i'm fine with today's diameter while zoomed in but want the new smaller diameter when zoomed out. it's much better."). A seventh hook in the page sets the glow's radius.
- **Settings buttons only while on** ([stated] 2026-11-16, after the first version: "quick note - disabling a filter (like security range) should hide the settings button for it."): a filter's settings button shows only while that filter is on or its panel is open, never on hover of a filter that is off (052 showed it on hover); switching a filter off shuts its panel. Applied to all four (Security range, Within N jumps, Wormholes, Sov upgrades). For the build: a change to 052's panel-button rule (CLAUDE.md "The Intel tab's layout"). With Wormholes off, its list (adding a hole by hand) opens only once the filter is on.
- **Combining:** every condition that is on must match; within one, any pick counts.
- **Brightness:** while any condition is on, a matching system is bright anywhere and the rest dim (0.16); the distance fade steps aside (the gate lines still fade past the reach). **Added after the first look** (not in the brief): zoomed out, a matching dot is also 1.6 px bigger, because three matches by brightness alone were hard to find at the starting zoom. MOCKUP box "Matches (a condition on)": Brighter / Brighter + bigger (default). After the owner saw no difference between the two ([stated] 2026-11-16 "i'm not seeing a difference when i toggle between "brighter' and "brighter + bigger""; it applied only zoomed out), zoomed in a match's disc is also drawn a quarter bigger; with no condition on there are no matches, so the row changes nothing (its label says so).
- **Colours:** only Colour by colours a dot; Kills and Wormholes no longer turn dots amber or lilac (their ✕ counts and rings show them).
- **Marks never fade:** report rings, the alert glow, your pin. Wormholes: see below (Q21).
- **Security range:** a panel with From / To steppers (0.1 steps, −1.0 to 1.0), quick High / Low / Null, both ends counted in either order, comparing the one-decimal number the map shows. **Within N jumps:** a stepper, 1 to 30.
- **Sov upgrades:** 053's panel and picks, plus a "Level" row of checkboxes 1, 2, 3 for the kinds that come in levels: any ticked level counts, none ticked = any level ([stated] 2026-11-16 Q10 "Exact level only", then "why not checkboxes so we can select more than one? the "at least" option ruled out filtering for only 1 and 2 for example."; earlier versions had "level N and up", then an exact-level stepper).
- **Legend:** a second line under the colour line, "Only 3 match · security -0.5 to -0.3 · Major Threat Detection Array, Minor Threat Detection Array level 3" (the count first so a phone never cuts it; it wraps). The colour line stays one line.
- **Match chip:** "3 match ›" bottom left; each press centres the next match, nearest first ("1 of 3 ›").
- **Phone:** the folded column button carries a neutral count of the conditions that are on.
- **Region colours:** MOCKUP box Today / Reserved (default). Reserved takes out the accent cyan, the kill amber and the two lilacs; the greedy colouring used 5 colours on this map.
- **Wormholes for Q21** ([stated] 2026-11-16: "there are only two wormholes in the mockup. can you add 12 with varying ranges and ages up to 24 hours and show it to me again so i can see how the treatment differs?"): 12 more made-up holes (`MKP.seedWh`, named MKW-01 to MKW-12, never on a named system), 2 to 28 jumps from you (some past "Map: within"), 4 min to 23.5 h old (three under 30 min), two Drifters, three added by hand; 14 in all with the two Intel reports. MOCKUP box "Wormholes only" (only the Wormholes filter on, every hole and you in view) and "Wormholes (Q21)": Thin rings / 045's bold + pulse (the default). **Q21 answered 2026-11-16** ([stated] "045's bold + pulse (Recommended)", "Off-filter rule (Recommended)", "Match chip replaces it (Recommended)"): with Wormholes on, the kept holes that match every filter that is on get 045's bold mark, the pulse (under 30 min) and the filled label; a kept hole that doesn't match keeps only the off-filter rule (fresh and inside "Map: within": thin rings; otherwise no wormhole mark), after the owner asked of Wormholes + Within 3 jumps "is this working as intended?" (every kept hole had kept its marks). The match chip steps through the holes. Two more hooks in the page.
- **MOCKUP box:** "Your example" (Security range −0.5 to −0.3 + Sov upgrades Threat Detection level 3, coloured by security, centred on you), "All off".

## Shortcuts the build must not copy

- Function overrides of the page's map code (`itMapFilterSet`, `itMapFbarPaint`, `itMapDimmed`, `itMapKey`, `itMapLegend`, `itMapDraw`, `itMapCtlPlace`, `sovOpen`, `sovPaint`, `sovChanged`, `itWhListOpen`, `itMapFbtnsHtml`); a build reworks `itm.filter`'s readers (the brief, section 3) instead.
- Nine hooks in the page (build_stk.py `PATCH`): the dot's opacity, the wormhole marks, the Sov hover, the bigger matching dot, the circle's number (none with no colour), the zoomed-in disc (soft colour), the alert glow's radius, 045's bold wormhole mark and its filled label (Q21's switch).
- The popovers aren't in `itMapPanel()`, so they don't take turns with Near You or count in `itMapFree`.
- The stack is kept in memory under `tvMapStackMock` (the mockup's storage is in memory); a build stores it under a new key, with the Sov level there, not in `tvSov` (053's reader drops unknown fields).
- The match set is worked out once a draw at most, and again only when its key changes; a build keys it into `itMapKey` and never re-tests per draw.

## Files

- `build_stk.py <repo>/index.html out.html`: the real page with made-up Intel around C-J6MT (the paths-to-you mockup's reports and kills, plus two wormhole reports), no network, storage in memory, the page's CSP replaced, nine hooks (each asserted to be found once). Needs `mock.js` beside it: the repo's `roadmap/paths-to-you-mockup/mock.js`, unchanged (not copied here, to save Project space).
- `proto_stk.js`: the model above.
- `boot_stk.js`: opens Intel, turns it on, makes up a sov list and 12 more wormholes from the mockup's own systems (`MKP.seedSov`, `MKP.seedWh`), adds the MOCKUP box.
- `test_stk.py out.html shots/`: 142 checks at 1440 and 390 px, a fresh page per case. They cover:
  - the column's groups and order;
  - nothing dims with no condition;
  - the example matches exactly the systems in −0.5..−0.3 with a Threat Detection Array at level 3, and some level-3 systems fall outside the range;
  - matches are bright (and bigger), the rest dim, and your system never dims;
  - the legend's "Only" line, with the count first, shown whole;
  - the chip's count, and it stepping nearest first;
  - the pressed buttons and the phone badge;
  - Kills never colouring amber;
  - a colour switch keeping the stack;
  - no colour (the pressed colour pressed again: plain grey, no colour button pressed, the stack kept, the legend says so; a colour pressed again colours the map);
  - Brighter + bigger changing the picture zoomed out and zoomed in;
  - the alert glow by default half the diameter zoomed out and today's zoomed in (r + 9); its switch changing the picture zoomed out and not zoomed in;
  - soft colour by default, matches keeping the full colour and the rest softened, and Full softening nothing;
  - Paths to you and back;
  - the Security range panel (opened the first time it's switched on, inside the map and right of the column, a close button, 0.1 steps, quick Null, Escape);
  - off keeping its setting, shutting its panel and hiding its settings button (also on hover, and for Sov);
  - Sov "Level" boxes: one ticked narrows, 1 + 2 stored as [1, 2] and named in the legend, none = any;
  - the reserved Region palette, and that its colouring fits;
  - the 14 wormholes (ages, distances, Drifters, by hand, all named), Wormholes only matching all 14, all bold with the fresh holes pulsing by default, Thin rings changing the picture with no pulse, Wormholes + Within 3 (matching holes bold, fresh holes in reach thin, the rest unmarked, the chip counting the holes), no pulse with Wormholes off;
  - no sideways scroll and no page errors.

  All 142 passed 2026-11-16 (after Q21).
- check_pii, with the names list from `claude/private/` (fingerprint matched), on the mockup and these scripts: 0 problems, names checked.

Run: `python3 -I build_stk.py <repo>/index.html stacked_filters_mockup.html && python3 -I test_stk.py stacked_filters_mockup.html shots`

**In the repo (build queue 058, 2026-11-16):** the build session rebuilt it on main 396fbd6 (v2026.11.16.2; the nine hooks still found once) with `mock.js` copied in beside these scripts from `roadmap/paths-to-you-mockup/`, and `test_stk.py` passed 142 of 142; the mockup is `Claude outputs/stacked_filters_mockup.html`. It shows the proposal over main as it was before the build, not the built page.
