# Plan: wormholes stand out on the Intel map's Wormholes filter

Status: **BUILT** as v2026.11.12.6 (build queue 045, branch 045-wormholes-standout; see "Built" at the end). Approved by the owner; queued as build queue 045 (2026-11-12). Written 2026-11-12 by a research session from main d227c9d (v2026.11.12.4, after 040). It changes only 040's Wormholes filter, so it doesn't wait for the Wormholes tab (roadmap/wormhole-mapping-plan.md, requirement 8, where it started).

## The owner's words
- [stated] "wormholes are getting lost in the chaos here. anything we can do to help them stand out more than other reports while on the wormholes filter for the map?" (with a screenshot of the map; not kept).
- Five options were offered. He asked "all four options together?" (yes, as a set), then [stated] "yes please" to a mockup of 1–4 with 5 as a toggle.
- Shown it: [stated] "that looks fantastic. keep all of it. 1-4 and the chip."
- Queue it on its own as the next number: [stated] "yes".

## What it does (the Wormholes filter only; every other filter unchanged)
1. **Everything else fades.**
   - Other reports' rings at 20% opacity, with no glow (shadowBlur 0). Their 12% fill drops to 3%.
   - The alert range's amber wash goes from .07 to .02.
   - A report in a system that has a wormhole keeps its full strength.
   - Labels only for wormholes and you. A report without a wormhole gets no label: no name, no count, no ✕, no CLEAR.
   - A route you hover still names the systems it passes, faint, as today.
2. **A bolder mark.**
   - Zoomed out: a filled disc (radius 6) in the hole's colour, with a glow (shadowBlur 14), a dark 1.5 px edge, and a 2 px ring at radius 10.5.
   - Zoomed in (the circles stage): a 3 px glowing ring at r + 4 around the system's circle, and a 1.5 px ring at r + 9.
   - A Drifter: hot pink with its outer ring dashed. This is 044's D15. Whichever of 044 and this item is built first changes `--it-wh-drifter` from #e4b5ff to #ff5fbf, and `itMapWhCol`'s fallback with it. That one also adds the dashed ring. The other one finds it done.
   - When 044 is built, its split ring (plain and Drifter in one system) applies to this mark's outer ring too.
3. **A pulse on fresh holes.**
   - A hole reported less than 30 minutes ago sends out one slow ring every 2.2 s. The ring grows from the outer ring's radius by 16 px and fades out.
   - None when the device asks for reduced motion.
   - The build makes it a CSS animation: one absolutely placed ring per fresh hole, animating transform: scale and opacity. That follows the UI rule that endless animations use opacity and transform only (LESSON #120; the mockup drew it on a canvas each frame, which the build must not).
   - The rings are placed on each map draw, which already happens when the view moves. They are removed when the hole turns 30 minutes old: the map's key changes each minute with the age label (`itMapWhKey`). They are also removed on another filter and when the map is hidden.
4. **Labels.**
   - A wormhole's tag ("WH · 9 min", "DRIFTER · 5 h") is a filled pill in its colour, with dark text (#0c1014).
   - Every wormhole inside "Map: within" gets its name and pill where they fit, else the pill alone. Failing that, it gets no label. On this filter no wormhole label is ever forced over another label, the fresh (live) ones and reports included.
   - On this filter a label may sit over a faded system's dot. Only the wormholes' marks and your pin keep their room. A label may sit a step further out (24 px) when the near spots are taken.
   - Your "YOU · system" label is unchanged.
5. **The "N wormholes" chip.**
   - Bottom left of the map, on this filter, when at least one wormhole is kept.
   - It reads "7 wormholes ›". Each press moves the view (same zoom) to the next one, nearest by gate jumps first (then newest), and reads "2/7 · L5-UWT ›".
   - The count starts over when the filter is chosen again.
   - Title and aria-label: "N wormholes on the map: show the nearest" or "…: show the next".

## Mockup
roadmap/wormholes-standout-mockup/ (README there): `Claude outputs/wormholes_standout_mockup.html`, built by build_whs.py from main d227c9d (the build rebuilt it from 25d3ae2, the last page before 045). It has 10 patches to the page's own functions, each found exactly once, plus proto_whs.js (the mark, the pulse, the chip), and busy made-up Intel. The MOCKUP bar switches between today's look and the new one, and turns the chip on or off. snap_whs.py has 25 checks at 1440 and 390 px; all passed, with no page errors and no sideways scroll. The patches name the exact places in `itMapDraw` and `itMapLabels` to change.

## UI rules it touches
- **Colour tokens only:**
  - `--it-wh` for plain holes;
  - `--it-wh-drifter` (#ff5fbf, as 044) for Drifter;
  - the label text #0c1014 is the map's existing dark outline colour.
  - The chip uses `--it-wh` for its border and a `color-mix` tint for its fill.
  - Contrast to check at the build: #0c1014 on #a98bd8 and on #ff5fbf, and the chip's text on its tint.
- **Drawing cost (LESSON #120):** nothing is redrawn on a timer. The map still draws only when its key changes. The pulse is CSS (transform and opacity) and runs only while a fresh hole is in view on this filter. It stops with reduced motion.
- **Phone:** the chip is at least 44 px tall below 600 px. No sideways scroll at 390 px. The pulse rings and the chip never take a press meant for the map, except the chip itself (`pointer-events: none` on the rings).
- **One button style:** the chip is a plain button with the page's button focus ring. It is not a tag.
- **The legend's one line (LESSON #113):** the filter's legend line keeps its text. The swatch for Drifter turns pink with the token. The legend's title (`itMapFLegTitle`) gains "; a pulsing one was reported in the last 30 minutes".
- **The Intel example:** none expected. The example doesn't show the Wormholes filter. The build confirms with 017's check.
- **Page size:** a few hundred bytes.

## Info text it touches
- `intel` "[Map]" currently reads "…Wormholes: reported, kept 24 h; its list button edits them. …". Add after it: "On the Wormholes filter the rest fades, one reported in the last 30 minutes pulses, and the chip steps through them." Check the `intel` panel stays within its 410-word cap (`check_subtext.py`).
- No other panel names the Wormholes filter's look (searched `CARD_INFO` and `IT_EX_NOTES` for wormhole, Drifter and filter).

## Checks to build
Extend tools/page_checks/wormhole_filter_check.py:
- **On the Wormholes filter:**
  - a report with no wormhole is drawn at 20% and has no entry in `itm.labels`;
  - every wormhole in view and in reach has a label, or its pill alone, where there's room, and no two labels overlap;
  - a fresh hole has a pulse ring and an old one doesn't;
  - with reduced motion, no pulse;
  - the chip shows the count and steps nearest-first.
- **On the Security filter:** labels, rings and counts are the same as before the change, with no chip and no pulse.
- **Mutants:**
  - fade the reports on every filter;
  - force wormhole labels over others;
  - pulse a hole 40 minutes old;
  - show the chip on another filter.

## DLA
Nothing new is stored, shared or sent. It changes only how the map draws what 040 already keeps in this browser. No clause touched (claude/reference/dla-planning-notes.md).

## Sources
Sources: none (no outside facts). The colours, timings and rules are the owner's decisions, the earlier plans' (044 D15) and this project's code (index.html main d227c9d: `itMapDraw` ~29253, `itMapLabels` ~29392, `itMapWh` ~29571, `itMapWhKey`, `itMapWhCol`, `itMapFLegTitle`).

## Built (v2026.11.12.6, build queue 045, 2026-11-12)
Built from main 25d3ae2 (after 043, Paths to you, and the game-data PR #47); all 10 of the mockup's places still matched once. At the build review the owner set the order and scope: 045 before 044 ([stated] "yes"), and 045 takes the Bubble-tag bug flagged on 044 ([stated] "yes").

Where the build differs from the plan:
- **The pulse** is CSS rings in a layer over the canvas (`itMapWhPulse`, `.it-map-whp`), written only when their places change; none in the Paths to you tree, on another filter or with reduced motion (the JS leaves the layer empty and the CSS hides it).
- **The chip** (`itMapWhChipPaint`, `itMapWhChipNext`, `button.it-map-whn`) is drawn with the map, takes room from the labels like the filter bar, lifts above the bar when they would meet, and hides while a phone's filter row is open (the row spans the map's width on two lines). Its look is the mockup's rounded pill in the `--it-wh` tint, like the map's "you" button.
- **The Drifter colour** is read from the token everywhere (the prototype hard-coded it); on the other filters a Drifter's outer thin ring is dashed too (044 D15).
- **Info text:** [Map] gained the plan's sentence; to stay within 410 words two sentences moved to METHODOLOGY.md (it already had both): the copy button "to report a line read wrong", and "Intel runs in one tab at a time…" ([stated] "yes"). With the Bubble fix [Tags] gained "Bubble: a bubble not at a gate." The panel is at 399 words.
- **Also in this delivery, the Bubble-tag bug** ([stated] "bubbles tag doesn't show up in near you list, only in feed"): a line with no pilots whose news is a tag (Bubble, Camp / gate, at the ESS) now reaches Near You (`itTagOnly`, kind 'tag'): its own row when the system has none ([stated] "yes it gets its own row"), only its tag on a row that exists; never an alert, a map ring or a Paths to you source; a row whose real report expires while its tag is fresh turns tag-only (`itNearDemote`). A bare wormhole line still gets no row ([stated] "no - wormhole reports dont need near you rows by themselves."). The Paths to you tree gained Bubble and a short WH / DRIFTER badge on systems already in it ([stated] "b"); the tree's tags now come from Near You's entry for every system in it (`it.near`), so a tag-only system on a route shows its tag. Checked by the new tools/page_checks/tag_only_check.py.
- The wormhole_filter_check's far-system pixel test samples the zoomed-in circle (zoomed out, 045's disc covers the dot).
