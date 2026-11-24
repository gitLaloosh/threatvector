# Mockup: Distance in jumps or light years (the Intel map's Only filter)

Made 2026-11-20 by the research session from `main` e72ba18 (v2026.11.20.2 plus the jump table update), for the plan `roadmap/ly-distance-plan.md` (planning list E1; the owner 2026-11-20: [stated] "Within N jumps → Distance (Recommended)", "Only where a jump can land (Recommended)", "Typed + quick picks (Recommended)", "From you, mockup yes (Recommended)"). Sent to the owner as `ly_distance_mockup.html`; queued as build queue 067.

**Built** in v2026.11.24.1 (build queue 067). At the build the mockup was rebuilt from main aa55779 (v2026.11.23.3, the page before 067) into `Claude outputs/ly_distance_mockup.html`: 73 of 73 checks passed. Two changes to the scripts for the repo: `build_ly.py` reads `mock.js` from `../paths-to-you-mockup/` when it isn't beside it, and `test_ly.py` uses Playwright's own Chromium when `/usr/bin/google-chrome` isn't there. The build differs from the mockup in one place: a fifth quick pick, 7.5 LY for Command carriers (the owner at the build review: "Add 7.5 LY pick (Recommended)"); the mockup keeps the four it was shown with.

## What it shows

- **The filter "Within N jumps" renamed "Distance"**, same button and place in the Only group. Its settings panel gains a switch at the top: **Jumps** (today's stepper and note, unchanged) / **Light years**.
- **Light years:** a stepper "Within [7.0] LY" (0.1 LY steps, 0.1 to 20.0; typed on a computer, read-only on a phone as every stepper), quick picks **6 / 7 / 8 / 10 LY** (each one's hover names the ships: Titans and supercarriers; carriers, dreadnoughts and FAX; Black Ops and Lancers; jump freighters and Rorqual, all at Jump Drive Calibration V), the picked one pressed; a short note; the panel's match count.
- **What matches:** every system whose straight-line distance from yours, rounded up to 0.01 as the hover shows it, is the LY or less, and a jump drive can land there: not 0.5 security or higher, not Pochven, not Zarzakh. Your own system always matches (as today).
- **The hover:** a matched system adds "within jump range (7.0 LY)"; a system in range where a jump drive can't land adds "in range, but a jump drive can't land here (high-sec / Pochven / Zarzakh)". The hover's own "N LY from you" is today's.
- **The Only line:** "within 7.0 LY (jump drive)" in place of "within 5 jumps".
- **Kept:** the switch, the LY and the jumps are kept with the map's filters (`tvMapStack`); a stack saved before this reads as Jumps, its N kept; a bad saved value falls back to Jumps, 7.0 LY.
- MOCKUP box: Distance 5 jumps (today), 6 LY, 7 LY, 10 LY, Off.

## Made up

The Intel reports and pilots are the shared `mock.js`'s (home C-J6MT). Nothing about distance is made up: the LY are the page's own `itMapLy` on the page's own map data.

## Shortcuts the build must not copy

- Two hooks (`build_ly.py` PATCH, each found once): the `near` test in `itMapMatch` calls `__MKnear`; the hover calls `__MKtip` before the sov lines. A build puts the test in `itMapMatch` itself and the line in the hover itself.
- `itMapStackBlank`, `itMapStackRead`, `itMapOnlyHtml`, `itMpBodyHtml`, `itMpMake` and `itMpPaint` are wrapped; a build changes them in place (and the filter's name and note in `IT_MAP_FILTERS`, `RS.mapLy` beside `RS.mapNear`).
- The landable test (`MKY.why`) reads the region's name "Pochven" and Zarzakh's ID; the build keeps one small table of the two (named once) beside `itMapSecT`.
- The mode switch reuses `.it-sov-k` labels (Sov upgrades' radio look) and the quick picks reuse `.it-mp-q` (Security range's); two lines of mockup CSS for the switch's row and the pressed quick pick.
- The MOCKUP box's scenes reset the filters by hand.

## Files

- `build_ly.py <repo>/index.html out.html`: the real page with made-up Intel; needs `mock.js` (the repo's `roadmap/paths-to-you-mockup/mock.js`, unchanged, not copied here). Build it from a page before 067 (`git show <commit before 067>:index.html`): its hooks are the old lines.
- `proto_ly.js`: the Distance filter's light years, the MOCKUP box. `boot_ly.js`: opens Intel, starts at 7 LY with the panel open.
- `test_ly.py out.html shots/`: 73 checks at 1440 and 390 px (the name; the panel and switch; 7 LY matches exactly the plan's rule worked out apart, nothing unlandable matches, home matches; the Only line; both hover lines; the hover's LY and the filter agree for every system on the map; quick picks set, press one only, match more at 10 LY; the stepper shows 10.0; 6.9 presses none; the panel count; saved, read back, bad values and an older stack; back to Jumps matches as today, focus kept, Only line back; the panel fits; on a phone the switch and quick picks are 24 px tall or more; no sideways scroll; no page errors).
- check_pii (without the names list) on the mockup and scripts: 1 problem, the page's own CCP login button image; names read by hand: invented only.

Run: `python3 -I build_ly.py <page before 067> ly_distance_mockup.html && python3 -I test_ly.py ly_distance_mockup.html shots`
