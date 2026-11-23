# Mockup: Intel map filters from live data (Sov holder, Jumps and Kills in the past hour, Region pick) and the phone column by group

Made 2026-11-20 by the research session from `main` f70fdd5 (v2026.11.20.1, after 058, 057 and 060), for the plan `roadmap/live-map-filters-plan.md` (all questions answered 2026-11-20; Q8 [stated] "Raise cap ~40, mockup yes (Recommended)"). Sent to the owner as `live_map_filters_mockup.html`: the real page with made-up Intel around C-J6MT and made-up live data, a MOCKUP box top right (on a phone bottom left, folded). Built as build queue 065.

The owner's two in-game screenshots of the sovereignty view (2026-11-20) were reference for what the game does only (his 2026-11-12 rule); nothing of them is stored here or in the mockup.

## What it shows

- **The column** gains four buttons, each with its own icon: Colour **Sov holder** (a flag), **Jumps (past hour)** (an arrow in a circle), **Kills (past hour)** (an ✕ in a circle), after Region; Only **Region pick** (a folded map), after Sov upgrades. Colour now has 6, Only 7, View 1. Settings buttons (058's, on hover; on a phone while on) for Sov holder, Kills (past hour) and Region pick; none for Jumps (past hour).
- **Sov holder, by standing** (Q1, the default): yours blue (`--side-friendly`), friendly light blue, neutral light grey, hostile red (`--side-hostile`), NPC faction space muted khaki, unclaimed plain grey (058's no-colour grey). Gate lines between two systems with the same alliance holder are drawn in its colour (Q1b, as in game), over the plain gates and under the bridges.
- **Sov holder, per alliance** (its settings: "One colour per alliance"): Region's palette and greedy method (reserved hues kept, 058 Q13); neighbouring holders always differ.
- **Zoomed in** (058's circles): the holder's logo fills the circle, ringed in the holder's colour (as in game); a capital has a small ★. NPC and unclaimed systems keep today's disc with the security number. The owner picked the ring ([stated] 2026-11-20 "ring"). MOCKUP box: "Logo circle: Ring (as in game) / Disc" (the logo on a disc of the holder's colour, no coloured ring), and "Logos: Not loaded (tickers)" (the ticker in the circle, as when a logo hasn't loaded).
- **Hover** (Q2): the logo, name, ticker and standing, ★ capital, the holding corporation and since when, Military / Industrial / Strategic levels and ADM, and the vulnerability window in EVE time.
- **Legend:** the colour line names the scale; for the hourly ones "as of HH:MM EVE". With Sov holder on, an "In view" line lists the top five holders in view with their logos and system counts (+N more).
- **Jumps (past hour):** 0 / 1–9 / 10–49 / 50–149 / 150–499 / 500+; zoomed in, the number in the circle (1.2k style past 999).
- **Kills (past hour):** ship + pod kills 0 / 1 / 2–4 / 5–19 / 20+; its settings switch to NPC kills 0 / 1–49 / 50–199 / 200–499 / 500+ (Q3). The note in its settings says it isn't Kills from Intel.
- **Region pick** (Q5): switched on with nothing picked, its list opens: a search box (dashes and spaces ignored), Clear with "N picked", a **Select all** box above the list ([stated] 2026-11-20 "can we add a checkbox to select all regions in the region picker?": ticks or unticks every region shown, "Select all shown" while a search narrows the list, a dash when some are picked; the page's checkbox style has no dash yet, so the mockup adds one), a box per region with its system count, your region first, then A–Z. Any pick counts; it stacks with every other Only filter; the legend's Only line names the regions ("in Insmother, Cloud Ring"; more than two: "+N").
- **The phone column by group** (Q6, the 058 bug): Colour with View under it (a line between) in one column, Only in the second, a line between the columns; each filter's settings button in a lane of its own beside it, so nothing moves when one shows; the column's background more solid. MOCKUP box "Phone column: By group / Today" shows today's jumble with the four new buttons for comparison. On a wide map the groups are `display:contents`: the desktop column is as today (16 rows with the two lines).
- **Soft colour turned up a bit** ([stated] 2026-11-20 "i know we went to softer colors, can we turn it up just a bit though?"): 058's soft colour keeps 55% of a colour zoomed out and 38% in a zoomed-in disc. MOCKUP box "Soft colour": Today (55% / 38%), A bit up (68% / 50%), More (80% / 62%, the default: [stated] "let's go with the "More" option on the colors."). It applies to every colour (Security, Jumps, Region and the new three); a match and your system keep the full colour as today.
- **No distance fade for the three live colours** (Q10, [stated] "ok, go with your choice for now."): with Sov holder, Jumps (past hour) or Kills (past hour) on, systems past Near You and past "Map: within" draw at full strength (only Only filters dim; the gates still fade), and the legend leaves out its faded / faint entries. Security, Jumps from you and Region keep today's fades.
- **MOCKUP box scenes:** Sov: standing (zoomed out), Sov: zoomed in, Sov: per alliance, Jumps (hour), Jumps zoomed in, Kills (hour), NPC kills, Region pick, Reset.

## Made up

- Twelve alliances "Mockup …" with invented emblem logos (data URLs: a shape on a colour, nothing from CCP's image server). Yours (Mockup Coalition) holds the area around C-J6MT; Mockup Raiders (on the hostile list) the area around MSG-BZ; the rest are spread over null-sec by gate from far-apart seeds. High- and low-sec and the NPC null regions (Curse, Great Wildlands, Stain, Syndicate, Outer Ring, Venal, Pochven) are NPC faction space; about 5% of held null-sec is unclaimed. Standings per alliance are fixed in the mockup (a build uses `sideOf` with the holder's corp and alliance).
- Jumps and kills per system with spreads like the live answers read 2026-11-20 (jumps median about 14; ship and pod kills in about 9% of systems; NPC kills mostly in null-sec); the three reported systems get some kills.
- Development levels, ADM, held since and the vulnerability window: random per system.
- System names: only the 54 names of the map-look mockup's list; other systems show as "~3000xxxx" (the mockup answers no other names).

## Shortcuts the build must not copy

- Function overrides of the page's code: `itMapStackBlank`, `itMapStackRead`, `itMapStKey`, `itMapFbtnsHtml`, `itMapColRaw`, `itMapFLegHtml`, `itMapFLegTitle`, `itMapOnlyHtml`, `itMpBodyHtml`, `itMpMake`, `itMpPaint`, `itMapFilterSet`, `itMapPanel`, `itMapLegend` (drops the faded / faint entries), `itMapMix` (the soft-colour step; a build changes the two numbers in `itMapFcol` and `itMapDraw`); and pushes into `IT_MAP_FILTERS`, `IT_MAP_COLOURS`, `IT_MAP_ONLY`, `IT_MAP_PANEL_BTN`. A build edits those in place.
- Ten hooks in the page (`build_lm.py` PATCH, each asserted to be found once): the holder's gate lines, the zoomed-in circle, the circle's number, the hover's lines, `itMpOpen`'s list of filters with settings, Region pick in `itMapMatch`, the column's row count (live map and the Intel example: the count of filters and lines, not the group wrappers), the "In view" line after a draw, and the dots' fade (Q10).
- The "In view" list is counted on every draw here; a build keys it to the view and the sov read (LESSON #120), and the gate lines per holder are worked out once per sov read (done so here: `MKL.edges`).
- The live data is made up at start, in memory; a build reads it through one reader per kind (plan L1).
- Region pick's room below its top is set by an `itMapPanel` wrapper; a build gives `itMapPanel` a room per filter.

## Files

- `build_lm.py <repo>/index.html out.html`: the real page with made-up Intel, no network, storage in memory, the page's CSP replaced, the hooks above. Needs `mock.js` beside it: `roadmap/paths-to-you-mockup/mock.js`, unchanged (not copied here).
- `proto_lm.js`: the four filters, the made-up data (`MKL.seed`), the panels, the grouped column, the MOCKUP box.
- `boot_lm.js`: opens Intel, turns it on, makes up the data, rebuilds the column, shows the box, starts on "Sov: standing".
- `test_lm.py out.html shots/`: 117 checks at 1440 and 390 px (the soft-colour steps, Q10, Region pick's Select all, the column's order, groups and settings buttons, Sov holder by standing and per alliance, logos and tickers, the hover, Jumps and Kills scales, Region pick, the phone column, no sideways scroll, no page errors). All 117 passed 2026-11-20 against f70fdd5.

Run (from the repo root, with `mock.js` copied beside `build_lm.py`): `python3 -I roadmap/live-map-filters-mockup/build_lm.py index.html "Claude outputs/live_map_filters_mockup.html" && python3 -I roadmap/live-map-filters-mockup/test_lm.py "Claude outputs/live_map_filters_mockup.html" /tmp/shots`
