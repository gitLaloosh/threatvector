# Mockup: the Intel map's "Activity (past hour)" Only filter

Made 2026-11-21 by the research session from `main` 991dd4a (v2026.11.21.2), for the plan `claude/roadmap/activity-filter-plan.md` (planning list E4; the owner 2026-11-20 [stated] "One filter, kind + minimum (Recommended)"; 2026-11-21 [stated] "Per kind, those defaults (Recommended)", "Round numbers 1–2000 (Recommended)", "No, use 065's colours (Recommended)", "Mockup yes, raise cap (Recommended)"). Sent to the owner as `activity_mockup.html`. Not queued.

**Archived 2026-11-26 with build queue 069's delivery** (v2026.11.26.1, branch `069-activity-filter`): the plan is `roadmap/activity-filter-plan.md`, the mockup `Claude outputs/activity_mockup.html`, built again from 991dd4a's index.html (its hooks fit that page, not today's: 065 and 068 have since replaced the two stand-ins with the real filters, LESSON #183).

## What it shows

- **A new Only filter "Activity (past hour)"**, last in the Only group, with its own icon (a pulse line) and settings button. Switched on the first time, its settings open.
- **Its settings** (058's panel): the kind as radios (Jumps · Ship + pod kills · NPC kills), an "At least [N]" stepper on round numbers (1 2 3 5 10 15 20 25 30 40 50 75 100 150 200 300 500 750 1000 1500 2000), a note, the match count. Each kind keeps its own number (defaults 50 / 1 / 200): switching kind brings back its number.
- **What matches:** systems whose count of the picked kind in the past hour is at least the number (a system missing from ESI's list counts as 0; J-space never matches, ESI has no counts there).
- **The Only line:** "at least 50 jumps in the past hour (1,262) · ESI 21:02"; "activity: no data yet" before a read.
- **The hover:** "140 jumps in the past hour (ESI, as of 21:02)" for the picked kind (065's Colour line says it when that Colour is on, so the build shows it once).
- **No numbers of its own on the map** (Q3): the counts in circles come from 065's Jumps / Kills (past hour) Colours.
- **Two inert stand-ins** in the Only group, "Region pick (065)" and "Sov hubs (068)", so the column holds the nine Only filters it will (they match nothing and aren't part of this item).
- MOCKUP box: Jumps ≥ 50, Jumps ≥ 500, Ship + pod ≥ 1, NPC ≥ 200, Zoomed out, No data yet, Off.

## Made up

Hourly counts for every k-space system, shaped like ESI's of 2026-11-21 (jumps: median about 16, a long tail; ship + pod kills in about 1 system in 10, mostly 1–3; NPC kills in about half of low-sec and null-sec), plus a few set by hand around C-J6MT (78-0R6 140 jumps, 6 ship + pod kills; SHBF-V 310 NPC kills; MSG-BZ 520 NPC kills; EUU-4N 220 jumps). The read time is 50 minutes before the page opens. No ESI read.

## Shortcuts the build must not copy

- Three hooks (`build_ac.py` PATCH, each found once): the `act` test in `itMapMatch`, the hover line, `itMpOpen` letting `act` in. A build writes each in place.
- `itMapStackBlank`, `itMapStackRead`, `itMapStKey`, `itMapOnlyHtml`, `itMpBodyHtml`, `itMpMake`, `itMapFilterSet` are wrapped; `IT_MAP_ONLY` / `IT_MAP_FILTERS` / `IT_MAP_PANEL_BTN` / `RS` are added to at run time.
- The counts are made up in `MKA.build`; the build takes them from 065's reader (kinds `jumps`, `kills`).
- The hover's "never twice" test names 065's Colours by stand-in keys (`mkjph` / `mkkph`); the build uses 065's real keys.
- The two stand-in filters are only there for the column's size.
- Two lines of mockup CSS (the kind row).

## Found

- **The phone column:** today's phone column (before 065's fix) holds all 16 buttons in a 6-row grid without overlap at 390 px (checked). 065's planned layout puts the Only group in one column of its own; with nine Only filters at 46 px that column is about 414 px, more than a phone map's room under the search box: 065's layout must let the Only group wrap to a second column (or the build of this item adds it). In the plan (section 4) for the build review.

## Files

- `build_ac.py <repo>/index.html out.html` (needs `mock.js` beside it: the repo's `roadmap/paths-to-you-mockup/mock.js`, unchanged, not copied here).
- `proto_ac.js`: the filter, the made-up counts, the stand-ins, the MOCKUP box. `boot_ac.js`: opens Intel, starts on Jumps ≥ 50 with the panel open.
- `test_ac.py out.html shots/`: 70 checks at 1440 and 390 px (the filter, its place, defaults, kinds and steps; the match equals the rule worked out apart; your system; no J-space; the Only line; the hover; the stepper; each kind's own number kept; focus kept; rarer kills; nothing at 2000; Jumps ≥ 500; no data, and data back worked out again; saved, bad values, an older stack; first switch-on opens the settings; the column with nine Only filters fits with nothing overlapping, 44 px on a phone; the panel fits; no sideways scroll; no page errors). All 70 passed 2026-11-21.
- check_pii (without the names list) on the mockup and scripts: only the page's own CCP login button image; names read by hand: invented only.

Run: `python3 -I build_ac.py <repo>/index.html activity_mockup.html && python3 -I test_ac.py activity_mockup.html shots`
