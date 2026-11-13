# Wormholes standing out on the Intel map (mockup, 2026-11-12)

Requirement 8 of roadmap/wormhole-mapping-plan.md. The owner: "wormholes are getting lost in the chaos here", then "yes please" to mocking options 1–4 together, with option 5 as a toggle. Shown it: "that looks fantastic. keep all of it. 1-4 and the chip." BUILT as v2026.11.12.6 (build queue 045; roadmap/wormholes-standout-plan.md, "Built").

`Claude outputs/wormholes_standout_mockup.html` is the real page (main d227c9d, v2026.11.12.4, after 040; rebuilt at the build from 25d3ae2, the last page before 045) with made-up, busy Intel around C-J6MT. That Intel has:
- hostiles with counts;
- clears and a neutral;
- 7 wormholes: fresh ones, two Drifters, one in a system with a hostile report, and older ones already in the store.

The MOCKUP bar has these buttons:
- **New look (1–4):** switches between the new look and today's.
- **Count chip (5):** shows or hides the chip.
- **Wormholes filter** and **Security filter:** switch between the two filters.

Everything changes on the Wormholes filter only.

1. **Everything else is faded.** Other reports' rings drop to 20%, with no glow. The alert range's amber wash is lighter. Labels are only for wormholes and you. Counts, ✕ and CLEAR are hidden. A report in a wormhole system keeps its strength.
2. **A bolder mark.** A filled disc in the hole's colour, with a glow, a dark edge and a ring. A Drifter is pink (#ff5fbf) with a dashed ring, as in 044. Zoomed in, it's a thick glowing ring around the circle and a second ring outside it.
3. **A pulse on fresh holes.** A hole reported in the last 30 minutes sends out one slow ring every 2.2 s. The pulse is drawn on its own canvas over the map, so the map isn't redrawn for it. There's no pulse when the device asks for reduced motion. (The build made it CSS rings, transform and opacity only.)
4. **Labels.** A wormhole's tag is a filled pill in its colour. Every wormhole inside "Map: within" gets its name and pill where they fit. Otherwise it gets the pill alone. Failing that, it gets no label, and a label is never drawn over another one. On this filter a label may sit over a faded system's dot, and may sit a step further out (24 px).
5. **"N wormholes" chip** (optional): bottom left. Each press moves the view to the next wormhole, nearest by jumps first. It reads "2/7 · L5-UWT ›".

## Files
- **build_whs.py:** applies the patches to index.html. There are 10, each found exactly once, or the build stops. The page has them since v2026.11.12.6, so run it on an older page: `git show 25d3ae2:index.html > old.html`.
- **proto_whs.js:** the bold mark, the pulse, the chip and the MOCKUP bar.
- **snap_whs.py:** screenshots and 25 checks at 1440 and 390 px. All passed, with no page errors and no sideways scroll (the research session, and again at the build).
- **mock.js and boot_wh.js:** the same files as in roadmap/wormholes-filter-mockup/.

Build: `python3 -I build_whs.py old.html wormholes_standout_mockup.html`, then `python3 -I snap_whs.py wormholes_standout_mockup.html shots/`.
