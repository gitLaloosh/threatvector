# Plan: the Intel map's filters, stacked (Colour / Only / View, marks always on)

**In the repo (build queue 058, 2026-11-16):** copied from the Project doc `claude/roadmap/intel-map-stack-plan.md` by the build session and built as v2026.11.16.3 on branch `058-intel-map-stack`; the Built notes (section 12) say where the build differs from this plan. Project paths below (`claude/...`) have repo copies under `roadmap/` (the brief `roadmap/map-filter-model-panel.md`, the mockup's scripts `roadmap/map-filter-stack-mockup/`) and the mockup itself is `Claude outputs/stacked_filters_mockup.html`.

**Status (2026-11-16):** planned by the research session against `main` 51207b6 (v2026.11.16.1, after 053). Q1-Q21 answered (section 2). **Queued as 058** 2026-11-16 ([stated] "yes"; `claude/build-queue/058-intel-map-stack.md`). Mockup: `stacked_filters_mockup.html` (sent to the owner; scripts in Project docs `claude/roadmap/map-filter-stack-mockup/`, README there; 142 checks pass at 1440 / 390 px; check_pii 0 problems, names checked). Background, the panel review and the prototype's rounds: `claude/roadmap/map-filter-model-panel.md`.

## 1. Why

- [stated] 2026-11-15: "i need the ability to have filters from some existing types work together. example: i want to see systems with threat detection array level 3 where system security level is N. what kinds of changes are we looking at? right now we can only apply filters of one type at a time. what i'm envisioning is an on/off state based on the settings for that filter so you can sort of stack them on top of each other."
- [stated] "i have a feeling there would be a fair amount of conflict between colors and highlighted vs faded states."
- [stated] "we would need to support numeric security status range in the filter. like -0.3 to -0.5"
- [stated] "i would like to break things down to their basic form and figuring out how best to categorize them and allow the user to tailor the map contents to what is most helpful to them at that time."

## 2. The owner's decisions

From the prototype's rounds (2026-11-16):
- [stated] "quick note - disabling a filter (like security range) should hide the settings button for it."
- [stated] "my one remaining concern right now, is that i can't toggle anything "off". this isn't an easy view to read.", then "it's about the base color groups sort of washing out the other data but the off switch for color groups is welcome too."
- [stated] "can we make the yellow background circles for "within your alert range" a bit smaller? maybe try 50% of current diameter?", then "i'm fine with today's diameter while zoomed in but want the new smaller diameter when zoomed out. it's much better."

The question rounds (2026-11-16, his picks quoted):
- **Q1** four groups, Colour (one or none) / Only (stacked) / Marks (always drawn) / View: [stated] "Yes, four groups (Recommended)".
- **Q2** combining: [stated] "All must match (Recommended)": every Only filter that is on must match; within one, any pick counts; no user-built AND/OR.
- **Q3** Kills and Wormholes stop colouring dots: [stated] "Yes, stop colouring (Recommended)".
- **Q4** Paths to you: [stated] "Filter column, View group (Recommended)".
- **Q5** brightness while an Only filter is on means "matches" only: [stated] "Yes, match only (Recommended)".
- **Q6** [stated] "Bright anywhere + Within N (Recommended)".
- **Q7** hostile and neutral rings, the alert glow and your pin never fade, overriding 045 on the Wormholes filter: [stated] "Never fade (Recommended)".
- **Q8** [stated] "Brighter + bigger (Recommended)".
- **Q9** Security range: [stated] "Yes, as in the prototype (Recommended)".
- **Q10** Sov level: [stated] "Exact level only", then 2026-11-16 [stated] "why not checkboxes so we can select more than one? the "at least" option ruled out filtering for only 1 and 2 for example." → a box per level (1, 2, 3); any ticked level counts, none ticked means any level.
- **Q11** [stated] "Remember it (Recommended)".
- **Q12** match chip: [stated] "Keep it (Recommended)".
- **Q13** [stated] "Reserve them (Recommended)".
- **Q14** [stated] "Second line (Recommended)".
- **Q15** [stated] "Soft only (Recommended)".
- **Q16** [stated] "Security, soft colour (Recommended)".
- **Q17-Q20** "Distance: jumps / light years": [stated] "A later item (Recommended)", "Shade systems in range (Recommended)", "Type LY now, ship picker later (Recommended)", "Not for now (Recommended)". Not in this plan (its own backlog item).

- **Q21** 045's Wormholes look once Wormholes is an Only filter. To compare, [stated] 2026-11-16 "there are only two wormholes in the mockup. can you add 12 with varying ranges and ages up to 24 hours and show it to me again so i can see how the treatment differs?" (the mockup now has 14 holes and a Thin rings / 045's bold + pulse switch); [stated] "ok so the wormhole filter will show the older wormholes that fell off of the feed and near you." (yes: with Wormholes on, every kept hole; off, only fresh Intel holes inside "Map: within"); then, with a screenshot of Wormholes + Within 3 jumps, [stated] "is this working as intended?" (no: every kept hole kept its marks, matching or not, because the plan had listed wormhole rings among Q7's never-fading marks; Q7 as answered covers hostile and neutral rings, the alert glow and your pin only). His picks:
  - Q21a matching holes' look: [stated] "045's bold + pulse (Recommended)".
  - Q21b a kept hole that doesn't match every filter that is on: [stated] "Off-filter rule (Recommended)": fresh and inside "Map: within", thin rings as a report; otherwise no wormhole mark (its dot dims).
  - Q21c the "N wormholes ›" chip: [stated] "Match chip replaces it (Recommended)": with Wormholes alone on, the match chip steps through the holes, nearest first.

## 3. What main has (51207b6; find by name)

- One filter: `itm.filter` (default `'sec'`, not saved), set by `itMapFilterSet` (29804). Its readers: `itMapCtlPlace` key and name-line anchor (29744, 29754), `itMapFbarPaint` (29787), `itMapFcol` (30058), `itMapDimmed` (30066-30071), `itMapDraw`'s `itm.sov` (30078) and `alpha` (30088), the zoomed-in number (30141), labels' `whS` (30230), the legend (`itMapFLegHtml` 30285, `itMapFLegTitle` 30297), `itPtLive` (30320), the hover's Sov line (30547), `itMapWh`'s `mark` (31267), `itMapWhKey` (31269), the wormholes chip (31316), `sovMapKey` (31532), `sovChanged` (31607).
- `IT_MAP_FILTERS` order: sec, jumps, region, reports, kills, wh, sov, paths. Panel buttons: `IT_MAP_PANEL_BTN` (wh, sov), shown on hover too (CSS `.it-map-fw:hover > button.it-map-pb`, ~2785).
- Opacity: `IT_MAP_DIM` 0.16, `IT_MAP_FAINT` 0.22, 0.45 past Near You (29983, 30088). Alert glow radius `big ? r + 9 : 22 * …` (~30091).
- Security: hundredths in `T.sec` (Int8Array); shown with `itMapSecText` (30016); every system ≤ 0.0 has class 0 (`itMapSecClass`, 29626).
- 053: `tvSov` read into `{v, lists, pick}` only (31460-31476); `sovIndex().at` gives each system's kinds with their level; `sovTable().lv` the kinds that come in levels.
- Steppers: `RS` / `rsHtml` / `rsBind` (31850-31868, 32233).
- `intel` info panel: 611 of its 620 words (`check_subtext.py`, measured on 51207b6).

## 4. Build

**4.1 State, stored.** `itm.filter` goes. `itm.colour` (`'sec' | 'jumps' | 'region' | ''`), `itm.view` (`'map' | 'paths'`), `itm.only` (`{secr, near, reports, kills, wh, sov}` on/off) with their settings (`secr: {lo, hi}` in tenths, `near: {n}`, `sovLv` a list of the ticked levels, e.g. `[1, 2]`; empty = any). Saved under a new key `tvMapStack` `{v:1, colour, view, only, secr, near, sovLv}`; first visit `colour:'sec'`, all off (Q16); a bad value reads as the defaults (a `sovLv` entry outside 1-3 is dropped). An older page never reads it; this page never writes `tvSov` for it (053's reader drops unknown fields). Safe both ways (say so in the pull request).

**4.2 The filter column** (`IT_MAP_FILTERS` gains a group field):
- Colour: Security, Jumps from you, Region. One pressed; pressing the one that is on turns colour off.
- Only: Security range (new), Within N jumps (new), Intel reports, Kills, Wormholes, Sov upgrades. Each on/off; settings kept while off.
- View: Paths to you (Q4); leaving it keeps the colour and the stack.
- A thin `--line` separator between groups (`.it-map-fbtns` grid items).
- A settings button shows only while its filter is on or its panel is open; never on hover of an Only filter that is off; switching a filter off shuts its panel. Change 052's CSS rule and CLAUDE.md "The Intel tab's layout".
- The name line: anchored to the pressed colour button (or the View button in Paths to you); with no colour, "No colour · press Security, Jumps or Region to colour the systems again".
- Phone: the folded column button shows the colour's icon and a neutral count badge of Only filters on (rule A: never amber).

**4.3 The match set.** `itMapMatch()` builds one `Uint8Array` when its key changes (the Only settings, your system, the reports and kills, the kept and live wormholes, `sovIndexKey()` and picks); `itMapKey` includes it. Never tested per system per draw (LESSON #120). Tests, all that are on must pass:
- Security range: `Number(itMapSecText(T.sec[i]))` within [min(lo, hi), max(lo, hi)], both ends included (Q9).
- Within N: `itm.D[i]` 0..N (stargate, as Jumps from you).
- Intel reports: `itm.rep.has(i)` or a live wormhole report. Kills: kills in Intel. Wormholes: a kept hole.
- Sov: a picked kind; for a kind with levels and any level ticked, one of the ticked levels (Q10; within one filter any pick counts, as Q2).
- Your system always counts as matching (never dims).

**4.4 Drawing** (`itMapDraw`, `itMapFcol`, `itMapDimmed`):
- No Only filter on: today's distance fades (bright within Near You, 0.45 to "Map: within", faint past it).
- Any Only filter on: a match is bright anywhere, the rest `IT_MAP_DIM`; no distance fade on dots (Q5, Q6); gate lines still fade past the reach.
- Matches bigger (Q8): zoomed out the dot 1.6 px bigger; zoomed in the disc a quarter bigger.
- Only the colour colours a dot (Q3): `itMapFcol` loses its Kills and Wormholes branches; their legend lines go.
- Soft colour only (Q15): zoomed out a non-matching system's colour mixed 45% toward the background (`#0c1014`); zoomed in a dark disc tinted with the colour (38% colour) with today's dark edge, no coloured outline (a ring means a report). A match keeps the full, solid colour. The legend's swatches stay full.
- No colour: every system `#56616b` (soft rules apply), no number in its circle.
- Marks never fade (Q7): report rings at 0.95 always (045's `IT_MAP_WH_FADE` step-back goes), the alert glow, your pin.
- Wormholes (Q21): `itMapWh`'s `mark` = the live holes (as today) plus, with Wormholes on, the kept holes that match every Only filter that is on. A matching kept hole gets 045's look: `itMapWhBold`, the pulse under `IT_MAP_WH_FRESH_MS`, the filled label (today's `whF` / `whS` tests become "Wormholes on and this hole matches"). A kept hole that doesn't match: thin rings if live (fresh Intel, inside "Map: within"), else no wormhole mark. Labels' room: only matches and you while any Only filter is on (today's Wormholes rule, generalised), else today's.
- The "N wormholes ›" chip (`itMapWhChipPaint`, `itm.whn`) goes; the match chip does its job (Q21c), nearest first, then newest for holes.
- Alert glow: zoomed out half today's radius (`11 * …`); zoomed in today's (`r + 9`).
- Reserved colours (Q13): `IT_MAP_REGION` = `#5fbf7f, #d9687f, #c9c35a, #5f8fd9, #3f9f8f, #b08a6a, #8fa0b8, #9fbf4f` (no `#4fc3d9` cyan, `#d99a3c` amber, `#9b7bd8`/`#c98fd0` lilacs); the greedy colouring uses 5 on the current map.
- Paths to you: unchanged; conditions don't apply there; the chip and the "Only" line hide.

**4.5 Settings panels.** Security range and Within N jumps get panels like the Wormholes list and Sov panel: part of `itMapPanel()` (one at a time, take turns with Near You, `itMapFree`), rule B, `button.x-close`, Escape, placed by `itMapCtlPlace`.
- Security range: From / To steppers (0.1 steps, −1.0 to 1.0) in the `rs` look (not `rsBind`'s keys, or extend `RS`), quick High (0.5-1.0) / Low (0.1-0.4) / Null (−1.0-0.0) as global buttons, the note "Both ends count, in either order. It compares the number the map shows (one decimal).", and the match count.
- Within N jumps: a stepper 1-30, its note on "Map: within".
- The first time Security range or Within N is switched on, its panel opens.
- Sov panel: a "Level" row under the picks with three checkboxes, 1, 2, 3, in 053's pick look (`.it-sov-k`; 44 px on a phone); "none ticked: any level" beside them while none is ticked; for the kinds with levels only, the rest match as picked. Legend: "level 1, 2".

**4.6 Legend and chip.**
- Legend line 1: the colour's line (or "No colour"), one line as today.
- Legend line 2, only while an Only filter is on: "**Only** **3 match** · security −0.5 to −0.3 · Major Threat Detection Array, Minor Threat Detection Array level 3" (count first; wraps; Q14). Its hover: "Every condition that is on must match; inside one, any pick counts. Hostile and neutral rings, the alert glow and your pin never fade."
- The match chip "N match ›" (Q12), bottom left (clear of the column), map control style: each press centres the next match nearest first ("2 of 5 ›"), using `itMapFreeX`; "No system matches" disabled when none; hidden with no Only filter on and in Paths to you.

**4.7 The Intel example** draws the map with its own state: it shows today's defaults in soft colour, no Only filter. 055 (queued) copies the live map's controls into it; whichever builds second makes the example's column show the three groups (055's drift check catches it).

## 5. UI rules it touches

- **Rule A** (map controls neutral): the column, separators, chip and badge use the map-control look; the badge is neutral.
- **Rule B** (panels): the two new panels.
- **One slider style:** none added; steppers.
- **Close button:** the two new panels have `button.x-close`.
- **One-line legend (CLAUDE.md 438):** changed to "the filter line is one line; a second line lists the Only filters while any is on" (Q14). Since 052, Near You's height comes from the map box (`--it-mh`) and the legend sits below it, so nothing moves but the Feed.
- **052's panel-button rule:** changed (settings button only while on).
- **045 / 044 Wormholes filter look:** kept for the matching holes (Q21a); the other reports' step-back goes (Q7); the wormholes chip folds into the match chip (Q21c).
- **Drawing cost (LESSON #120):** the match set keyed, no timers.
- **Phone:** 44 px targets (panel steppers, quick buttons, chip); no sideways scroll at 390 px.
- **Intel example:** section 4.7.

## 6. Info text it touches

`CARD_INFO["intel"]` [Map] becomes (85 → 93 words; the panel 611 → 619 of 620):

"[Map] A ring's colour is the standing, its size the gang (solo, 2–10, 11+); ✕ counts kills. Filters (left): one colour (press it again for none); Only filters, any number, all must match (their settings beside them); Paths to you, routes from hostiles in your alert range as a tree. Matches stay bright, the rest dim; rings never fade; the chip steps through matches. Wormholes: reported, kept 24 h, edited and shared in its list (a name there shows it on the map). With no Only filter on, systems past {card:itnear}'s range are faded."

Q21 doesn't change the Wormholes sentence. The build re-counts with `check_subtext.py`. IT_EX_NOTES: none.

## 7. CCP's Developer License Agreement

Not touched: no new data, requests or storage of other players' information; the new key holds the user's own map settings in their browser.

## 8. Checks

- New `intel_map_stack_check.py` at 1440 and 390 px, made-up data only, from the mockup's `test_stk.py`:
  - groups and order;
  - colour off and back;
  - the owner's example matching exactly (security −0.5..−0.3 and a Threat Detection Array at level 3);
  - matches bright and bigger, the rest dim, your system never;
  - soft colour, with matches full;
  - Kills never amber;
  - rings never faded;
  - the alert glow half zoomed out and today's zoomed in;
  - the legend's second line, whole, count first;
  - the chip, nearest first;
  - Paths to you and back;
  - the panels (first switch-on, inside the map, close, Escape, take turns with Near You);
  - settings button hidden while off (also on hover);
  - wormholes: Wormholes alone, every kept hole bold, the fresh ones pulsing; with Within 3 jumps on too, matching holes bold, fresh holes in reach thin, the rest unmarked; the match chip counting the holes; no wormholes chip;
  - Sov levels: one ticked narrows, two ticked stored as `[1, 2]`, none = any, the legend names them;
  - `tvMapStack` round trip, a bad value read as defaults;
  - no sideways scroll, no page errors.

  Mutants: a non-matching kept hole still bold (Q21b), a test ignored (Kills still amber), OR instead of AND, the distance fade kept while filtering, a settings button shown on hover while off.
- Update the checks that use `itm.filter` / `itMapFilterSet` (045's chip and look are checked in `tools/page_checks/wormhole_filter_check.py`): `intel_map_check.py`, `intel_map_layout_check.py`, `intel_map_look_check.py`, `paths_to_you_check.py`, `sov_upgrades_check.py`, `tag_only_check.py`, `wormhole_filter_check.py`, `wormhole_share_check.py`, `wormhole_sig_check.py`.
- `check_ui_rules.py` (rule A on the chip and badge, rule B on the panels), `check_subtext.py`, `check_pii`, `run_checks.py --served`.

## 9. Hand test (owner)

Setup: `git fetch origin && git checkout 058-intel-map-stack` (the build's branch), then `python3 -m http.server 8000` in the repo and open http://localhost:8000. Back to main afterwards: `git checkout main`.

1. Intel map: Security in soft colour; reports and wormholes stand out. Press Security again: plain grey. Press Jumps: coloured.
2. Turn on Security range (its panel opens), set −0.5 to −0.3; turn on Sov upgrades, pick the Threat Detection kinds, tick Level 3; then tick 1 and 2 instead (3 off) and see the legend say "level 1, 2". The legend's second line and the chip count agree; the chip steps nearest first; hostile rings stay bright.
3. Compare a few systems' security in the game with the map's shown value at the ends of your range (−0.25, −0.55 kinds of values): the UNVERIFIED row below. Widened by the build (section 12): also a low-sec system stored as 0.45 (the map now shows 0.4, in the low-sec colour) and a few positive x.x5 values.
4. Turn Wormholes on alone: every kept hole bold, the fresh ones pulsing, older ones that left the Feed still there. Add Within 3 jumps: only the holes within 3 stay bold; a fresh one further out keeps thin rings; older ones further out lose their marks. The chip counts the matches.
5. Turn Security range off: its settings button disappears, also on hover. Reload: the stack is as you left it.
6. Phone width: the column button's count, the panels as sheets, no sideways scroll.

## 10. Mockup

`stacked_filters_mockup.html`, built from Project docs `claude/roadmap/map-filter-stack-mockup/` (`build_stk.py`, `proto_stk.js`, `boot_stk.js`, `test_stk.py`; `mock.js` from the repo's `roadmap/paths-to-you-mockup/`). Its MOCKUP box defaults are the decisions; its other buttons show alternatives turned down. It takes shortcuts the build must not copy (its README). The build commits it to `Claude outputs/`.

## 11. Page size

Served 590,418 bytes on 51207b6 (ceiling 800,000). Estimate: a few KB of code and CSS.


## 12. Built notes (build queue 058, 2026-11-16)

- **State in one object, `itm.st`** (`itMapSt()`), not `itm.colour` / `itm.view` / `itm.only`: `itm.view` is already the map's pan and zoom.
  The object is the stored form (`{v: 1, colour, view, only, secr, near, sovLv, seen}`); `seen` remembers that Security range / Within N have
  had their first switch-on, so the panel opens only that first time across visits. `itMapStackRead` checks each field on its own and falls back
  to the default for that field only. The Intel example uses `itMapStackBlank()`, never the stored stack.
- **Security, shown, from one function** (the owner at the review, 2026-11-16, "yes" to the session's recommendation): reading section 11's
  UNVERIFIED row against the data found that `INTEL_MAP.sec` is CCP's value rounded to hundredths and the map rounded it again: 19 low-sec systems
  at 0.449 showed 0.5 in the high-sec colour (the route planner, reading `INTEL_MAP.band`, was right). `itMapSecT(i)` (tenths) now settles the
  0.45 line by the band and every reader on the map goes through it (`itMapSecClass`, `itMapSecText`, the Paths tree, the hover, the Wormholes
  tab's `whSec`, the Intel example); `tools/check_sec_shown.py` (a fast lint) refuses any other reader of `.sec[` and runs the page's own function
  on every system against the band (5268 systems, 19 corrected; it fails on main). LESSON #170. The rest of the x.x5 edge (582 systems whose
  stored hundredth sits on a rounding edge) needs the generator to store the shown value: a backlog item, after the hand test.
- **Security range compares `itMapSecT`**, the corrected shown value, so "High" never matches those 19.
- **Labels** follow the mockup, not 4.4's last bullet: report labels stay while Only filters are on (Q7, rings never fade); only the
  wormhole-only labels need a match (or the focus).
- **The chip** reads "N match ›", then "k of N ›" while stepping; any filter press starts the count again (`itm.mtStep = -1`).
- **Sov's legend and hover:** 053's own legend line (`sovLegHtml`) went; the Only line names the picks and levels. The Sov hover line shows only
  while Sov is on.
- **intel_kills_check** was named in the review as a reader of the map filter: it isn't (it presses the Feed's `data-it-f`), so it is
  unchanged.
- **Checks:** `tools/page_checks/intel_map_stack_check.py` (new; 15 parts at 1440 and 390 px, a canvas `arc` record of each draw instead of
  pixel samples, 13 mutants) and the nine checks of section 8 updated (`intel_map_look_check` now expects soft colour and one Only filter at a
  time; `wormhole_filter_check` the match chip in place of the wormholes chip).

## Sources

| Fact | Source | Checked | Status |
|---|---|---|---|
| The game shows a negative security rounded the way `itMapSecText` does (e.g. −0.55 as −0.5, −0.25 as −0.2), so "the number the map shows" is the number the game shows | not found | 2026-11-16 | UNVERIFIED: compare a few systems in game with the map at the range's ends (hand test step 3) |
| 19 systems stored as 0.45 are below 0.45 in CCP's unrounded value (low-sec in the game) | `tools/check_sec_shown.py` run on the page's `INTEL_MAP` (`sec` against `band`, both from `tools/jump_table_update.py`, CCP's SDE) | 2026-11-16 | verified |
