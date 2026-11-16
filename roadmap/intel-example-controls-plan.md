# Intel example: the live map's controls, size and centring

**Status:** planned 2026-11-15 by a research session against `main` e7f5a2b (v2026.11.15.3, after 052). Mockup sent 2026-11-15. QUEUED as build queue 055 on 2026-11-15 ([stated] "yes"; `claude/build-queue/055-intel-example-controls.md`). Reviewed by the build session 2026-11-16 against main 43ca307 (section 12); IN BUILD on branch `055-intel-example-controls` (the owner: [stated] "1. yes, 2. yes").

Backlog: "BUG | Narrow–Moderate — Intel example: the map picture leaves out the filter column and the system search" (memory `areas/dscan-backlog-7.md`).

## 1. What and why

[stated] 2026-11-15: "intel tab's example content doesn't include the filters on the left side of the map or the system search. should accurately reflect changes made to the functioning map."

The Intel example (build queue 017; 052 moved it to the new layout) draws the map as a still picture (`itExMapPic`) with only two extras: a copy of Near You's rail button (`itExRailHtml`) and the legend. Everything else the live map shows is made inside `itMapMake` as one string, and the example never uses it. So 047's search box and 052's filter column and zoom row never reached the example. Nothing checks that the two match, so the next map change would drift the same way.

## 2. The owner's decisions

Asked 2026-11-15, answered [stated] "1. sure, 2. a, 3. yes, 4. no for now":

- **Q1 Mockup:** yes. Sent as `intel_example_controls_mockup.html`; scripts in Project docs `claude/roadmap/intel-example-controls-mockup/`.
- **Q2 What the example shows:** (a) everything the live map shows before you touch it:
  - the zoom row (+ − ⤢ ⌖);
  - the system search;
  - the filter column with Security on (a phone: folded behind its one button);
  - Near You's rail button (already there);
  - the legend (already there);
  - the slider row under the map ("Map: within" and the drag/zoom hint).
- **Q3 Size and centring:** yes. The picture is as tall as the live map and centred on you in the part Near You's list doesn't cover.
- **Q4 A sixth marker for the filters and search:** "no for now". The five notes (`IT_EX_NOTES`) and their wording stay as they are.

**Session decisions** (not asked; in the mockup for the owner to see):
- **D1 Marker 3 ("The map")** moves from the picture's top-left corner, where the search box now sits, to its bottom-left corner. Only its place changes, not its note.
- **D2 Near You stays open in the example** (wide: beside the rail; phone: under the picture) as 052 decided, though the live default is shut. Markers 2, 4 and 5 point into it.
- **D3 Found while planning, a bug on main:** at 390 px the example's Near You list has no height. Its rows don't show, and markers 2, 4 and 5 float over the legend (screenshot in the mockup's "Today"). Cause: `.itx-near` keeps `flex:1 1 0` from the wide rule inside a phone column whose height is auto. Fixed in this item (4.6). `intel_example_check` passed because a zero-height row still has a left edge for the marker to sit on.

## 3. Today (main e7f5a2b)

- `itExampleHtml` (~29270) builds, inside `itExSandbox`: `.it-map-box.itx-map` holding the `<img>` and `itExRailHtml()`, then Near You's column, `.it-map-leg` (`itExLegendHtml`), then the Feed's first 5 rows.
- `itExMapPic(w)` (~29306) draws a canvas `filter: 'sec'` at height `max(IT_MAP_MIN_H 380, min(560, w·0.72))`, centred on the whole width.
  - `itMapFree` (~29740) returns `[0, W]` for a canvas outside a box.
  - `itMapFitView` runs only when a report would be off the picture.
- CSS (~2508–2510) puts the example's rail at `top:8px` (no zoom row above it) and its Near You at `top:8px; bottom:8px`.
- The live map (`itMapMake` ~29773, `itMapRefresh` ~29800, `itMapCtlPlace` ~29704):
  - zoom row top right; the rail 8 px under it (`top:46px`; phone `112px`);
  - search top left (210 px; phone: full width under the zoom row);
  - filter column `.it-map-fb` down the left (phone: shut behind `.it-map-fcur`), rows from `itMapCtlPlace`;
  - under the box, `.it-map-leg` and `.it-map-row` (`rsHtml('mapReach')` + help text);
  - height: wide `min(720, max(520, w·0.5))`, phone `min(600, max(440, w·1.45))`.
- Measured in the mockup's Today: at 1440 the example picture is 560 px tall against about 640 px live (1288 px wide). At 390 it's 380 against 440. On a wide screen, systems on the right sit under Near You's list (K4-RFZ's label cut).

## 4. The change

**4.1 One builder per control, used by both** (so they can't drift):
- `itMapZoomHtml()`: the zoom row, taken out of `itMapMake`'s string.
- `itRpSearchHtml()` (exists).
- `itMapFbarHtml()` (exists).
- `itMapRailHtml()` (exists; the example keeps `itExRailHtml`'s pressed, badged form, or `itMapRailHtml` gains a still form).
- `itMapRowHtml()`: the slider row, taken out of `itMapMake`'s string.

`itMapMake` calls them, and the example calls the same ones.

**4.2 Still copies:**
- `itExStill(html)` strips every `id`, `aria-controls`, `aria-activedescendant` and `aria-haspopup`, and every hook the live code looks for:
  - `data-im-*`, `data-it-*` (as `itExampleHtml` already renames `data-it-sys` / `data-it-cap`) and `data-rs*`;
  - so no `#itRpSug` twin and no `rsPaint` / `itMapFbarPaint` / `itNearBtnPaint` reaching into the example.
- Every button and input gets `tabindex="-1"` (the body is already `inert`).
- The filter column shows Security pressed (`aria-pressed="true"`), with its name line filled but hidden as at rest (`opacity:0`) and the phone button showing Security's icon. A small pure helper sets these, the way `itMapFbarPaint` does on the live map.
- The slider's input shows `IT_EXAMPLE.mapReach`, read-only.

**4.3 The picture's height and centring:**
- `itMapH(w, phone)` holds the live formula, used by `itMapRefresh` and `itExMapPic` (`IT_MAP_MIN_H` stays only if something else uses it).
- `itExFill` measures the example's own controls before the picture is drawn: the filter column's right edge and Near You's left edge inside `.itx-map`. A phone has no list in the map.
- `itExMapPic(w, free, fbBox)` uses them:
  - **itMapFree:** returns the example's free part while the picture is drawn (a value set in the sandbox, e.g. `itm.free`, read first by `itMapFree`; never a global swap as the mockup does);
  - **labels:** `itMapDraw` takes the example's column box for `itm.fbBox`, so labels stay clear of the column as on the live map;
  - **fit:** the "a report is off the picture" test uses the free part.
- The cache key gains the free part.

**4.4 Places:**
- The example's rail and Near You take the live places: rail `top:46px` (phone 112px), Near You `top:46px` beside the rail on a wide screen.
- The `.itx-map .it-map-rail{top:8px}` and `.it-nearcol{top:8px}` overrides go.
- The filter column's rows (`--it-flr`) come from the same rule as `itMapCtlPlace`. Share it as `itMapFlRows(H, top, phone, n)`.

**4.5 Phone:** what the live phone shows at rest:
- zoom row (44 px);
- search full width under it;
- the column's one button (Security's icon) under that, with the rail level with it on the right;
- Near You's list under the picture (052), then the legend, the slider row with the phone's help line, and the Feed.

**4.6 The phone Near You fix (D3):** under 600 px, `.it-top.itx-top .it-nearcol > .itx-near{flex:none;}`.

**4.7 Marker 3 (D1):** `itExPlace` puts it 14 px in from the picture's bottom-left corner. It must not sit on the search box, the filter column or its phone button.

**4.8 Not changed:**
- `IT_EX_NOTES` and the example's other text;
- `IT_EXAMPLE`'s data;
- when the example shows (`itExAuto`, `dscanItExGone`);
- the sandbox's set-asides;
- the live map's behaviour (refactoring only).

## 5. Mockup

`intel_example_controls_mockup.html` (sent 2026-11-15) is the real page at e7f5a2b with `proto_exctl.js` after its script. Its MOCKUP box switches the example between Today (main as it is) and Proposed, at any width.

Scripts are in `claude/roadmap/intel-example-controls-mockup/`:
- `README.md`;
- `build_exctl.py <repo>/index.html proto_exctl.js <out>`;
- `test_exctl.py <out> [shots]`: 45 checks pass at 1440 and 390 px, Today and Proposed, with no page errors and no sideways scroll.

`check_pii` reported no names; its only flag was the SSO button image. The build commits the mockup to `Claude outputs/`.

Mockup shortcuts the build doesn't copy:
- it swaps `itMapFree` globally while drawing;
- labels can still pass under the filter column (4.3 fixes that);
- the zoom row is copied as text rather than from a shared builder.

## 6. UI rules it touches

- **Rule A (map control vs button):** the copies use the live classes, so they look the same. No new style.
- **Phone:** 44 px controls as live (inert copies, not targets); no sideways scroll at 390 and 320 px.
- **No button inside a button:** none added.
- **Colour tokens only:** no new colours.
- **Drawing cost (LESSON #120):**
  - the picture is drawn once per width (and free part), as today;
  - the one existing ResizeObserver stays;
  - no timers.
- **Rule C (checkbox/radio):** none in the copies.
- **One close button:** unchanged.
- **The README rule "Intel changes and the Intel example":** this item is that rule's catch-up. The new check (section 9) enforces it from now on.
- **CLAUDE.md:** the "Intel's example for new users" paragraph gains a sentence: the example's map carries still copies of the live map's controls from the same builders, and `intel_example_check` fails if the live map has one the example lacks.
- Also run `check_ui_rules.py` and `check_card_names.py`. Copies add buttons to the page, so if a count rule sees them, scope it past `.itx` and say so in the pull request.

## 7. Info text it touches

None:
- `CARD_INFO` doesn't describe the example;
- `IT_EX_INFO` ("See an example") is unchanged;
- `IT_EX_NOTES` is unchanged (Q4);
- note 3 ("The map: reports and kills around you; hover one for its route to you.") stays true.

Report "Info text: checked; none".

## 8. Stored data, DLA

- **Stored data:** none changes (no key read or written; `dscanItExGone` as today). Safe both ways.
- **DLA:** made-up pilots only, nothing asked of anyone, so no clause touched.

## 9. Checks

`intel_example_check.py`, at 1440 and 390 px:

**(a) Drift guard.** Build the live map's element (`itMapMake()`) in the check's page. Every child of its `.it-map-box` that shows at rest (not `canvas`, `[hidden]` or `[aria-hidden="true"]`: today zoom, rail, search, filter bar), and every sibling of the box in `.it-map` (legend, slider row), has a twin with the same class in the example.
- Mutant: drop the search from the example, and the check fails.

**(b) Still copies:**
- no `id` in `.itx`;
- no `data-im-*`, `data-it-ny`, `data-it-whl` or `data-rs`;
- nothing focusable;
- `document.querySelectorAll('#itRpSug').length` is at most 1;
- Security pressed.

**(c) Picture:**
- height equals `itMapH(w, phone)`;
- you are inside the free part (between the column and Near You on a wide screen).

**(d) Places:**
- the rail is under the zoom row and clear of the search box (both widths);
- Near You is level with the rail (wide);
- 390 px: the filter column is shut behind its button.

**(e) Phone Near You (D3):** `.itx-near` has height and its first row is visible at 390 px.
- Mutant: `flex:1 1 0` back, and the check fails.

**(f) Markers:**
- each is on its target;
- marker 3 is at the picture's bottom-left;
- marker 3 isn't on the search box, the column or its button.

**(g)** No sideways scroll at 390 and 320 px; no page errors.

Also re-run:
- `intel_layout_check.py`, `intel_map_layout_check.py`, `intel_map_check.py`, `intel_map_you_check.py`, `route_planner_check.py` (search box) and `paths_to_you_check.py` (live controls refactored);
- `check_ui_rules.py`, `check_subtext.py`, `check_card_names.py`, `check_example_names.py`;
- `run_checks.py --served` (`intel_example_check` is a served check).

## 10. Hand test (the owner)

Setup (the branch name is the queue item's; run `git status` first, since uncommitted changes can stop the switch):
```
git fetch origin
git switch NNN-short-name
git pull
python -m http.server 8000
```
On Windows use `py -m http.server 8000` if `python` isn't found. Open http://localhost:8000/; Ctrl+C stops the server. Back to main afterwards: `git switch main` then `git pull`.

1. Intel tab with nothing running yet, or Intel's ⓘ → "See an example". The example's map has:
   - the search box top left;
   - the filters down the left with Security lit;
   - + − ⤢ ⌖ top right with the Near You button under them;
   - the "Map: within" row under the legend.

   Compare it with your real map once Intel runs.
2. The example's map is about as tall as your real map. "YOU · 1DQ1-A" sits in the open part left of Near You's list, with no system label under the list or the filter column.
3. Marker 3 sits at the map's bottom-left corner, not on the search box.
4. Phone width (DevTools device view, 390 px):
   - the zoom row, the full-width search and the filters' one button on the map;
   - Near You's rows listed under the map, with markers 2, 4 and 5 on them;
   - no sideways scroll.
5. Nothing in the example can be clicked or tabbed to; the real map's search and filters still work as before.

## 11. Where to look (main e7f5a2b)

Line numbers are e7f5a2b's; on 43ca307 (after 053, 054 and 058) the example's functions sit about 80 lines lower and the map's about 95 lower. Every name below still exists.

- `IT_EX_NOTES` ~29172, `itExSandbox` ~29220, `itExampleHtml` ~29270, `itExRailHtml` ~29296, `itExMapPic` ~29306, `itExFill` ~29342, `itExPlace` ~29360;
- `itMapFbarHtml` / `itMapFbtnsHtml` ~29653, `itMapRailHtml` ~29676, `itMapCtlPlace` ~29704, `itMapFree` ~29740, `itMapFbarPaint` ~29748, `itMapMake` ~29773, `itMapRefresh` ~29800 (height ~29812);
- `itMapLayout` / `itMapFitView` ~29913–29972, `itMapDraw`'s `fbBox` ~30134, `itRpSearchHtml` ~31684, `rsHtml` ~31868;
- CSS: the example ~2500–2512, the map controls ~2667–2790, phone ~2900;
- `tools/page_checks/intel_example_check.py`.

## 12. Build review 2026-11-16 (build session, main 43ca307, v2026.11.16.3)

Reviewed against main after 053 (Sov upgrades), 054 (You follows the login) and 058 (the filters stacked). The owner's go-ahead: [stated] "1. yes, 2. yes" (1: add the legend fix below; 2: build).

- **The mockup still applies:** rebuilt from its scripts on 43ca307, all 45 checks of `test_exctl.py` pass at 1440 and 390 px. Its copied column is `itMapFbarHtml()`, so it already shows 058's three groups (Colour, Only, View) with their lines and 053's Sov upgrades; the panel buttons stay hidden, as at the live defaults (no Only filter on). 058's plan section 4.7 ("whichever builds second makes the example's column show the three groups") is met by the shared builder.
- **The drift guard's "at rest":** 058's match chip (`.it-map-mt`, `hidden` until an Only filter is on) and the legend's second line (only while an Only filter is on) are not at rest, so the example needs no twin of them.
- **Gap found, a bug on main since 058 (fixed in this item, the owner: "yes"):** 058 drew the example's picture with `itMapStackBlank()`, but `itExLegendHtml` runs in `itExSandbox`, which doesn't set `itm.st` aside, so the example's legend read the user's own stack. Reproduced: with Region + Only Kills saved, the example's legend said "Region · a colour each" and "Only 0 match · kills in Intel" over a picture coloured by Security. The copied filter column would have shown the user's picks too. **Fix:** `itExSandbox` sets `itm.st` (and the match set it keys, `itm.mt`) to `itMapStackBlank()` for everything the example draws, and puts them back after. `intel_example_check` saves a different stack first and checks the legend, the column and the picture; a mutant that drops the set-aside fails it. The Only line can name picked Sov upgrade kinds (CCP's names) but never a list's systems; the example now shows none of it.
- **Pressed state from one painter:** `itMapFbarPaint`'s marking (pressed buttons, the name line, the phone button's icon and count) becomes `itMapFbarMark(fb, st, paths)`, used by the live map and by the example's still copy, so 058's rules for what shows pressed can't drift either.
- **Line numbers** in section 11 moved (note there); no function the plan names was renamed.

## 13. Built (v2026.11.16.4, branch `055-intel-example-controls`, 2026-11-16)

Built as the plan says, with the review's legend fix (section 12). Where the build differs or adds:

- **One more builder:** `itMapMarkupHtml()` is the live map's whole markup (what `itMapMake` puts in). The drift guard reads the controls at rest from it rather than from the live element, whose state (a message, the match chip) depends on what the page is doing.
- **`itMapFbarMark(fb, stack)`** is `itMapFbarPaint`'s marking as a painter of any column (4.2's "small pure helper"); the live map calls it with its stack, the example with today's defaults.
- **Measuring:** `itExMeasure(f, col, w, h)` sets the copy's `--it-flr` (`itMapFlRows`) for the live height and measures the column box and Near You's left edge; `itExMapPic(w, free = [0, w], fb = null)` (the defaults keep the one-argument calls in `intel_map_stack_check` and `paths_to_you_check`). `itMapFree` reads `itm.exFree` first, `itMapDraw` starts `itm.fbBox` from `itm.exFb`, and `itMapFitView` counts the column when `itm.exFb` is set; both are set only inside the picture's draw. The free part is the live map's: from the left edge to Near You's list (the column is kept clear by the fit and the names, as live).
- **The live overlays left alone:** the picture's draw sets `itm.whp` and `itm.mtb` aside, so drawing the example no longer hides the live map's match chip or clears its wormhole pulses (it did since 058 whenever the example was drawn with an Only filter on).
- **The picture's box** gets the live height before the picture loads (`img.style.height`), so nothing jumps.
- `IT_MAP_MIN_H` is gone (nothing else used it).
- **Checks:** 055's cases in `intel_example_check.py` at 1440, 760, 390 and 320 px, plus nine mutants (section 9's list, the old rail place, a centring mutant at 760 too, and the user's stack); the centring case also requires you in the middle of the free part when the start view is used and every report clear of the column and Near You. Mutant lines are single lines with no leading space, since the served copy drops indentation. `intel_map_stack_check.py`'s example mutant moved to the sandbox's set-aside.
- **Results:** `run_checks.py --auto --ledger` picked `all` (the mockup in `Claude outputs/` is unmapped): 24 lints, the pyfa chain (its one notice: pyfa master's new commits, 0 steps failed) and 101 page checks, all passed; `--served` passed. Page size: source 952,801 → 955,044 bytes, served 603,259 → 604,212 bytes.

## Sources

Sources: none (no outside facts). Everything here is this project's own code at e7f5a2b and 43ca307 and the owner's decisions.
