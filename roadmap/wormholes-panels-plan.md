# Plan: the Wormholes tab's panels behind icons, as on Intel's map

**Status (2026-11-15):** planned by a research session against `main` e7f5a2b (v2026.11.15.3, 052 built). All questions answered (section 9). Mockup sent (`wormholes_panels_mockup.html`). **Queued as 056** (`claude/build-queue/056-wormholes-panels.md`, [stated] "1. A, 2. yes"); build after 053 (the Sov upgrades filter) merges, and re-check section 8 then. check_plan_sources: 0 problems. Sources: none (no outside facts).

**BUILT 2026-11-17: v2026.11.17.1, branch 056-wormholes-panels** (reviewed against main 42b016f, v2026.11.16.6). See "Built" at the end for where the build differs.

Backlog: memory `areas/dscan-backlog-7.md`, "Wormholes tab: panels behind icons, as on Intel's new map". [stated] 2026-11-15: "add a backlog item to be delivered with the next build that updates the wormholes tab to reflect the design choices made for the intel tab's new map with the panels on the side with icons that expand rather than always showing fully expanded panels." Moved out of 053 for its own plan: [stated] "should i have a research session plan this before we proceed? just so we dont muddy up the build process?"

## 1. What main has (e7f5a2b; find by name)

**Wormholes tab panels** (048, the `// ==== WORMHOLES TAB` module):
- `WH_PANELS` (~32390): `sum` System, `sigs` Signatures, `route` Routes, `local` Local. `WH_LATER` (~32391): "Comes in a later part of the beta." in the last three.
- `whPanelsHtml` (~32595) builds each as `section.wh-pn[data-pn]`: a header button `.wh-pnh[data-wh-pn]` (aria-expanded; `.wh-pnc` holds the focused system's name on System) over its body `.wh-pnb[data-pnb]`. System open, the rest shut.
- `.wh-panels` (CSS ~3271): absolute, top 46, left 8, bottom 8, width 340, scrolls; a section's look is `--panel-2` at 95%, 8 px corners, a lighter shadow, a 12 px uppercase header. **Not rule B.** Below 900 px top 90. Phone (~3306): a 4-tab bar at the foot, one body opening upward as a sheet (max-height 62%); `M.phoneInit` shuts every body on a phone's first draw (D23: "the map starts clear").
- The header click (`whWire` ~32982) toggles one body (a phone: one at a time). **Open/shut is not stored.**
- `whPanels` (~32829) writes System's body (`whSumHtml`) when its HTML changed and no field in it has focus, and the name in `.wh-pnc`. It runs on every `whPaint`, shut or not.
- `whFree` (~32649): Fit, ⌖ and "bring you into view" aim at the part no panel covers: the left edge moves past the panel column (narrower than 60% of the map), else the foot moves above the sheet.
- A click on a system: the canvas's pointerup (`up` in `whWire`, ~33069) calls `whSelect(d.hit)` only when the press didn't move and wasn't Shift. `whSelect` is also called by the system menu (`whMenuOpen` ~32909), + Add, Add a system here and the System panel's connection names.

**Other things on the map:**
- `.wh-ctl` (top 8, right 8): `.it-map-zoom` + − ⤢ ⌖ Select, `+ Add` (`.it-map-clr`), the gear (Wormholes settings), ⓘ (`whmap`). Phone: one row across the top, 44 px, + and − hidden.
- `.wh-topl` (top 8, left 8, right 300): the "you're in …" line; below 900 px top 52 across the width; phone bottom 52 (above the tab bar), hidden while a sheet is open.
- `.wh-gsel` (top 46, left 8; phone top 60): "N selected · …".
- `.wh-mini`, the overview (D5a): bottom right, 200 × 150 (`whMiniDraw`); phone top 60 right 10, 132 × 96 (moved up because the tab bar has the foot). `whFit` fits again above it when a system would land under it.
- `.wh-msg` (the toast, bottom centre; phone top 60 left 8). `.wh-pop` (Add, settings: top 52, right 8, 480 wide, z 6; phone a sheet). `.wh-smenu` (051's system menu at the pointer), `.wh-hmenu` (Add a system here).
- Chain `tvWhChain`, marks `tvWhMarks` (both rebuilt from known fields by the older page's readers, so neither can carry a new field safely).

**Intel's model (052; CLAUDE.md "The Intel tab's layout", rules A–C):**
- The rail `.it-map-rail` (role toolbar, "Map panels"), 8 px under the zoom buttons at the top right, 30 px buttons (44 phone) in the map control look (rule A).
- Near You's button: `IT_FEED_ICON`, a count badge, `aria-pressed`, `aria-controls`, a title naming it and "press to show/hide".
- The panel opens beside the rail (320 px, from the rail's top to 8 px above the foot; phone: the map's width less the rail), in the site panel style (rule B); a view, not a dialog (no close button, no Escape); shut by default, remembered (`nearShown`).
- Centring uses the uncovered part (`itMapFree`, the whole width when under 96 px); placement without timers (LESSON #120).

The Wormholes map is its own code: it calls none of `itMapCtlPlace`, `itMapFree`, `itNearToggle`, `itMapRoomForBoth`. It shares only CSS classes (`.it-map-zoom`, `.it-map-clr`, and with this plan `.it-map-rail`).

## 2. What changes

**2.1 The rail, top left** (Q1, [stated] "Top left, where panels are now"): `<div class="it-map-rail wh-rail" role="toolbar" aria-label="Map panels">` in `.wh-box` (rule A by reuse of `.it-map-rail`; `.wh-rail` only positions it: `left:8px; right:auto`).
- Wide: top 46 (8 px under the "you're in" line). Below 900 px, where that line drops under the button row (top 52): top 90.
- Phone: top 60 (under the 44 px button row), left 8, 44 px buttons. The global phone rule `.it-map-rail{top:112px}` is Intel's: `.wh-box .wh-rail` must win over it.

**2.2 One button, System** (Q2, [stated] "Only working panels"): Signatures, Routes and Local each add their own button when their part is built (one panel open at a time from then on: opening one shuts the other).
- `button[data-wh-rp="sum"]`, `aria-controls="whPnSum"`, `aria-pressed`, title and aria-label "System: <focused system> (press to show the panel)" / "(press to hide the panel)", written only when the name or the state changes (as `itNearBtnPaint`).
- No badge (rule A's one amber is the alert-range count; System has no count).
- **Icon: A, the ringed planet** ([stated] "1. A"; over B, a star with a dashed orbit, and C, an info card). Our own drawing, 18 px, `currentColor`; the SVG is `ICONS.a` in `roadmap/wormholes-panels-mockup/proto_whp.js`; the build copies it as `WH_SYS_ICON`.

**2.3 The panel** (rule B): `section.wh-pnl#whPnSum` (aria-label "System"; no dialog role), `--panel`, 1 px `--line`, 6 px corners, shadow `0 8px 24px rgba(0,0,0,.5)`, padding `10px 12px 12px`, scrolls inside; heading `h3` "System" 14 px bold `--heading` (no name in it: the body's first line names the system, and the button's hover does); System's body (`whSumHtml`, `[data-pnb="sum"]`) inside, unchanged.
- Wide: right of the rail: top 46, left 44, width 340 (today's), down to 8 px above the foot. Below 900 px: top 90. No clash with the overview (bottom right) or the button row (top right).
- "N selected" (`.wh-gsel`) moves right of the rail (left 44), and right of the open panel while it shows (left 392, `.wh-box:has(.wh-pnl:not([hidden])) .wh-gsel`).
- Phone (Q5, [stated] "Sheet beside the rail"): top 60, left 60, right 8, down to 8 px above the foot (the map's width less the rail, as Near You on a phone). While it's open the overview and the "you're in" line hide. The 4-tab bar goes; with the foot free, the overview goes back to the bottom right (bottom 10) and the "you're in" line to the bottom left (bottom 8, right 150, clear of the overview). The toast and "N selected" sit right of the rail (left 60, top 60). The body's phone-tab rules (order, max-height, border) don't apply inside the panel.
- A view, not a dialog: no close button, no Escape; its button shuts it (as Near You). The owner asked about a close button after seeing the mockup, then: [stated] "nevermind, i see you just click on the icon again" (offered: the site's ×, a collapse chevron, or a stronger pressed look; none taken).
- Popovers (Add, settings) and the menus stay above it (z 6–8) as today; they don't shut it.

**2.4 A click on a system opens System** (Q3, [stated] "Yes, a click opens it"): only the map's own click, the `whSelect(d.hit)` in the canvas's pointerup (not a drag, not Shift, not in Select mode). The system menu, + Add, Add a system here and the panel's connection names set the focus without opening it (the last one is inside the open panel anyway). Only the button shuts it. A press on empty space changes nothing.

**2.5 Remembered** (Q4, [stated] "As you left it"): a new key `tvWhPanels` `{v: 1, open: 'sum' | ''}`, read with try/catch; a bad or missing value = shut. Shut the first time, then as you left it on every width (D23's "a phone starts with the map clear" becomes "shut the first time"; `M.phoneInit` goes). An older page never reads the key (its stacked panels show as they always did); `tvWhChain` and `tvWhMarks` keep their form. Safe both ways; say both in the pull request.

**2.6 Drawing cost** (LESSON #120): no timers. `whPanels` writes System's body only while the panel is open; opening it clears `S.pn` and writes once. The button's title only when it changes. Placement is CSS only (no measuring); `whFree` measures the panel's box only on a fit or a centre, as today. Opening or shutting the panel doesn't move the view (as Near You); ⤢ then fits in the uncovered part.

**2.7 `whFree`:** the left edge moves to 4 px right of the open panel (as today's rule for the column); when that leaves under 96 px (a phone's sheet), the whole map (as `itMapFree`). `whFit`'s overview rule stays.

**2.8 What goes:** `.wh-panels`, `.wh-pn`, `.wh-pnh`, `.wh-pnc` in a header, the phone tab bar and its rules (`.wh-box:has(.wh-pnb:not([hidden])) .wh-topl` becomes the `.wh-pnl` version), the three later sections, `WH_LATER` (nothing else uses it; check), `M.phoneInit`. `WH_PANELS` can stay as the list later parts add to, or go; the build's choice.

## 3. UI rules it touches

- **Rule A (map controls):** the rail and its button reuse `.it-map-rail` (`rgba(18,23,28,.9)`, `--line`, cyan hover, `--tag-on` pressed, 30 / 44 px). `check_ui_rules.py` (7) already covers `.it-map-rail`; add `.wh-rail` to its `MAPCTL` so an amber in the positioning rule is caught.
- **Rule B (panels over the map):** the System panel moves to the site panel style; `check_ui_rules.py` (8) gains `.wh-pnl` (`--panel`, `--line`). A visible change (darker fill, 6 px corners, a 14 px heading instead of 12 px uppercase), following the rule.
- **Rule C:** no checkboxes added.
- **Close button / Escape:** none on the panel (a view, Near You's precedent). The popovers keep theirs.
- **One chevron:** the panel has none (the ▾ headers go).
- **Phone:** 44 px rail button; the sheet leaves the rail and the button row clickable (checked in the mockup); no sideways scroll at 390 px.
- **Colour tokens only:** the icon is `currentColor`.
- **Drawing cost:** 2.6.
- **Page size:** served 590,418 bytes (gzip -9) on e7f5a2b, ceiling 800,000; this change is a few hundred bytes either way.
- **Intel example:** untouched (Wormholes tab only).
- **DLA:** not touched (nothing new stored about anyone, no request).

## 4. Info text it touches

`whmap` is at 206 of its 210 words (`check_subtext.py`'s default cap; measured on e7f5a2b: 50 / 56 / 59 / 41). Only "[Focus and adding]" changes (59 → 61 words; total 208):

> [Focus and adding] Click a system for the System panel (its button, top left, shows or hides it): class, effect, statics, notes, connections. Right-click it (press and hold on a phone) for its menu: a status (the border's colour), a tag, Lock, Copy the name, Remove. + Add adds a system or connection by hand; right-click empty space adds one there.

The colour key (`whLegendHtml`), "[Moving around]" ("The overview in the corner" stays true on a phone too, now at the bottom right) and "[Kept]": unchanged. Other panels: none. The build re-counts against its own diff (README "Info text stays true").

## 5. Checks

- `wormhole_tab_check.py`: its "panel" part opens System by its rail button before filling fields (Playwright fills only visible fields); the "Signatures, Routes and Local" line goes (no such sections now). Its phone part: no tab bar.
- `wormhole_menu_check.py`: opens System before reading `[data-pnb="sum"]` (or its setup stores `tvWhPanels` open).
- New `wormhole_layout_check.py` (made-up chain only), at 1440, 760 and 390 px, a fresh page each (the mockup's `test_whp.py` is the starting point: 68 checks):
  - shut by default: no stacked panels, no tab bar; one rail button at the map's left edge, under the "you're in" line (phone: under the button row), the zoom buttons' size and fill;
  - pressed: the panel right of the rail, inside the map, in the site panel style, clear of the button row and the overview; every map control's centre still hits that control (`elementFromPoint`); `aria-pressed`;
  - ⤢ with the panel open fits the chain right of it (wide);
  - remembered across a reload; pressed again it shuts and that is kept; a bad `tvWhPanels` reads as shut;
  - a drag on a system leaves it shut; a click on a system focuses it and opens System; the system menu doesn't open it;
  - 760: the rail and the panel under the "you're in" line;
  - 390: the sheet right of the rail, the overview and the line hidden while it's open, the overview at the bottom right when shut;
  - no sideways scroll; no page errors.
  - Mutants, each must fail: open by default; `whFree` ignoring the panel; not remembered; a click not opening it; the menu opening it; the phone sheet over the rail; `M.phoneInit` kept (a phone shutting what was remembered open).
- `check_ui_rules.py` (7) `.wh-rail`, (8) `.wh-pnl`, each with a mutant (an amber rail; a `--panel-2` panel).
- `check_subtext.py` (whmap ≤ 210), `check_pii`, `run_checks.py --served`.

## 6. Hand test (owner)

1. Wormholes tab, at full width: the map clear, one button at the top left under the "you're in" line. Press it: System opens beside it; zoom, Add, gear, ⓘ and the overview still work. Reload: still open. Press it again: shut; reload: still shut.
2. Click a system: System opens on it. Drag a system: nothing opens. Right-click a system: its menu, the panel as it was. ⤢ with the panel open: the chain fits beside it.
3. A phone: the sheet beside the rail; the overview and "you're in" line at the bottom when it's shut.

## 7. Mockup

`wormholes_panels_mockup.html` (sent 2026-11-15): the real page (main e7f5a2b) with `proto_whp.js` after its script; a made-up chain (wormhole systems picked by position from CCP's own table, made-up statics, a note and marks, no pilots or groups). The MOCKUP bar: Today / Proposed, the icon A / B / C, Reset (forgets the remembered panel and the chain), – to fold.
- Scripts: `roadmap/wormholes-panels-mockup/` (README there): `proto_whp.js`, `build_whp.py`, `test_whp.py`, `snap_whp.py`.
- `test_whp.py`: 68 checks at 1440, 760 and 390 px, all pass; no page errors; no sideways scroll.
- `check_pii` (names list copied in, fingerprint matched): names clean; only the page's own CCP login button image is flagged, as expected.
- The build commits the mockup to `Claude outputs/` and these scripts to `roadmap/wormholes-panels-mockup/`.

## 8. Re-check after 053 merges

053 changes Intel's `itMapCtlPlace`, `itMapFree` and `itNearToggle` to handle whichever filter panel is open. This plan calls none of them, so the re-check is narrow: `.it-map-rail`'s CSS (reused here) and its phone rule (`top:112px`, which `.wh-box .wh-rail` overrides); `check_ui_rules.py` (7) and (8) as 053 leaves them (it adds the Sov panel to rule B); CLAUDE.md's "The Intel tab's layout" paragraph; line numbers.

## 9. The owner's answers (2026-11-15)

- Q1 rail side: [stated] "Top left, where panels are now" (over the session's recommendation of top right, as Intel). The panel opens to the rail's right, where the panels are today; no clash with the overview.
- Q2 which buttons: [stated] "Only working panels (Recommended)".
- Q3 a click on a system: [stated] "Yes, a click opens it (Recommended)" (over the build session's suggestion "no").
- Q4 remembered: [stated] "As you left it (Recommended)".
- Q5 phone: [stated] "Sheet beside the rail (Recommended)".
- Q6 mockup: [stated] "Yes, mockup (Recommended)".
- Close button: none ([stated] "mockup doesn't show a button to collapse or close the panel after it's opened", then "nevermind, i see you just click on the icon again").
- Icon and queueing: [stated] "1. A, 2. yes" → the ringed planet; queued as 056.

## Sources

Sources: none (no outside facts). Everything above is the project's own code (index.html at main e7f5a2b), CLAUDE.md, its checks and the owner's decisions.

## Built (2026-11-17, v2026.11.17.1, build queue 056)

Reviewed against main 42b016f (v2026.11.16.6: 053, 054, 058, 055, 041 and 057 had landed). The Wormholes module was unchanged since e7f5a2b apart from `whSec` (058); Intel's rail CSS and its phone `top:112px` as section 8 expected; Intel's code finds its rail only inside its own map box. The mockup rebuilt on 42b016f passed its 68 checks.

Where the build differs:
- **An empty map shows no button** (the plan didn't say; asked at the build review, [stated] "A": hidden until the map has a system, as the stacked panels were hidden before). The panel is shut on an empty map too, whatever `tvWhPanels` says.
- **Select mode:** a click on a system focuses it without opening System (section 2.4's "not in Select mode"; the mockup's wrapper opened it there).
- **`WH_PANELS` and `WH_LATER` went** (2.8 left `WH_PANELS` to the build): the next part adds its button to `whRailHtml` and opening one shuts the other.
- **Names:** `whRailHtml` (the rail and the panel), `whPnRead` / `whPnSet` (the key), `S.open` (read once in `whMake`).
- **"N selected" below 900 px** moves to top 90 with the rail (the mockup's rule), clear of the "you're in" line at top 52.
- **`wormhole_menu_check.py`'s press-and-hold case** now puts the finger on the menu's Home item first (`LP_AT`): with the phone's tab bar gone the system sat lower, the finger landed in the gap between two items, and the LESSON #167 mutant passed. It now also fails if no item is under the finger. Its setup stores `tvWhPanels` open on the wide map (the phone's full chain stays shut: the sheet would cover the system).
- **`wormhole_layout_check.py`** adds to section 5's list: the empty map; Esc doesn't shut the panel; opening it moves nothing; the body isn't written while shut (LESSON #120) and shows the focus once opened; Select mode and + Add leave it shut; a `tvWhPanels` of another version is shut; and two more mutants (the menu opening it at 390 too; the rail on an empty map).
- **check_ui_rules (7) and (8):** no mutant harness exists for them; an amber rail and a `--panel-2` panel were each run by hand on copies and caught.
- **Docs:** CLAUDE.md's Wormholes tab paragraph and rule B's list; METHODOLOGY.md's Wormholes section (tvWhPanels).
- **The mockup** was rebuilt from its scripts on 42b016f (it moves the old stacked panels' body, so it needs a page from before 056).
