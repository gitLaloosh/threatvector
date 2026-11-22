# Mockup: kill counts by who died on the Intel map's labels

Made 2026-11-20 by the research session from `main` f70fdd5 (v2026.11.20.1), for the plan `roadmap/kill-counts-plan.md` (Project doc `claude/roadmap/kill-rings-plan.md` until build queue 066; the owner's direction 2026-11-20: [stated] "maybe instead of changing rings, we just represent the death count by standing? amber X [N] [N] [N]", then "Yes, counts by who died (Recommended)", "Friendly, hostile, neutral (Recommended)", "Yes, quick mockup (Recommended)"). Sent to the owner as `kill_counts_mockup.html`; built as build queue 066 (v2026.11.21.3). The mockup in `Claude outputs/kill_counts_mockup.html` was rebuilt by the build session from `main` 991dd4a (the page before 066), so its "Today" is the page as it was.

## What it shows

- **The label's kill tag:** an amber ✕, then one count per who died, each in its standing's colour: friendlies lost (blue), hostiles killed (red `#f08b7e`), neutrals killed (grey), in Near You's badge order; a standing with no deaths is left out. Today's "✕N" is kept for comparison (MOCKUP box "Kill label: Today / By who died").
- **Friendly / neutral contrast** ([stated] 2026-11-20 "the blue and white for friendlies and neuts are too close in color/shade. can we make them contrast a bit more?"; the first try, light blue `#8db8f2` beside light grey `#b9c3ca`, differed by 4 points of lightness): MOCKUP box "Friendly / neutral": A the friendly token `#4f8fe0` (`--side-friendly`, the friendly ring) beside the light neutral ring grey `#b9c3ca` (lightness 59 vs 78, the default); B a bright blue `#7dbbff` beside a dim grey `#6b7781` (74 vs 49); C `#4f8fe0` beside a near-white grey `#d4dbe0` (59 vs 87). The owner picked A ([stated] "go with A").
- **Hover:** "✕ 10 kills here: 3 friendlies lost, 5 hostiles killed, 2 neutrals killed", each part in its colour.
- **Legend:** "✕ kills by who died: friendly hostile neutral", the words in their colours.
- **Rings unchanged.** Near You's badges show the same counts (the kills go through the page's own `itNearAdd`).
- **Zoom:** Out / Middle / In (labels show at every zoom; the busy area round C-J6MT shows the crowding at each).

## Made up

Kills in twelve named systems round C-J6MT, through the page's own Near You path: 78-0R6 is the owner's example (3 friendlies lost, 5 hostiles killed, 2 neutrals killed); others have one, two or all three standings, one with 22 kills. Pilots "Mk Pilot N" with invented corporations; sides set directly. System names: the map-look mockup's list (others show as "~3000xxxx").

## Shortcuts the build must not copy

- `itMapReports` is wrapped to add `kb: {f, h, n}`; a build adds it inside `itMapReports` (from `st.kills`' `v`, already kept).
- Three hooks (`build_kc.py` PATCH, each found once): the label's kill piece in `itMapLabels`' `tags`, the hover's kill line, the legend's "✕ kills" entry. They match the page before 066 only.
- Made-up kill entries built by hand (`MKK.seed`); sides set directly instead of `itKillSides`.

## Files

- `build_kc.py <repo>/index.html out.html`: the real page with made-up Intel; needs `mock.js` beside it (the repo's `roadmap/paths-to-you-mockup/mock.js`, unchanged, not copied here). Build it from a page before 066 (e.g. `git show 991dd4a:index.html`).
- `proto_kc.js`: the kill counts, the made-up kills, the MOCKUP box. `boot_kc.js`: opens Intel, makes up the kills, zooms to the middle.
- `test_kc.py out.html shots/`: 38 checks at 1440 and 390 px (the owner's example counts, the three colour pairs and their lightness apart by 15 points or more, total kept, pieces and colours in order, a zero left out, hover words, legend, Near You agrees, labelled at three zooms, Today kept, no sideways scroll, no page errors). All 38 passed 2026-11-20 (after the colour pairs).
- check_pii on the mockup and scripts: names read by hand: invented only ("Mk Pilot N", "Mockup …").

Run: `python3 -I build_kc.py <a page before 066> kill_counts_mockup.html && python3 -I test_kc.py kill_counts_mockup.html shots`
