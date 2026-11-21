# Mockup: Wormholes tab part 4 (Project doc claude/roadmap/wormholes-part4-plan.md, now roadmap/wormholes-part4-plan.md)

Made 2026-11-20 by a research session from `main` 995f6a0 (v2026.11.19.1). Sent to the owner as `wh_part4_mockup.html`.
Rebuilt by the build session 2026-11-20 from these scripts on 995f6a0's page (`git show 995f6a0:index.html`): 89 of 89 checks pass; committed
as `Claude outputs/wh_part4_mockup.html` with build queue 062 (v2026.11.20.2). The build's own code is in `index.html`; this prototype isn't it.

Round 2 (same day): pinned routes as compact rows with a security strip, after the owner's feedback:
- [stated] "this needs to more closely reflect the in-game routing."
- [stated] "we need to be able to pin multiple systems that the page will automatically calculate the route to each time we navigate another system/wormhole."
- [stated] "the example from wanderer reflects how to effectively represent multiple routes in a small space."

Other tools' screenshots are reference for what they do only; this is the page's own design.

The mockup is the real page with:
- made-up Intel around C-J6MT (the repo's runtime);
- a made-up chain of CCP's own wormhole systems, picked by class and effect: a C3 Pulsar (Home, locked), a C5 Wolf-Rayet (you're here) and a C2. Its k-space ends are C-J6MT, Tama and Rens;
- one connection at critical mass, one at end of life, one limited to medium ships;
- a made-up probe scan in the C5.

Everyone is invented ("Mk ..." / "Mockup ..."). Systems are EVE's public data.

    PYFA_SRC=<pyfa checkout at e5483f8> python3 -I gen_data_rt.py data_rt.js
    python3 -I build_rt.py <995f6a0's index.html> wh_part4_mockup.html   (mock.js, data_rt.js, proto_rt.js, boot_rt.js beside it)
    python3 -I test_rt.py wh_part4_mockup.html shots                (Playwright with /usr/bin/google-chrome: 1440 and 390 px)

## Files
- `mock.js`: the repo's `roadmap/paths-to-you-mockup/mock.js`, unchanged. It isn't copied here.
- `gen_data_rt.py`: writes `data_rt.js` (not kept: run it again), each effect's numbers per class from CCP's 36 effect beacons (pyfa's staticdata at e5483f8). The words table in it is this mockup's draft (the build's is in `tools/gen_wh_table.py`).
- `build_rt.py`: the page, the made-up data, and two hooks in `whDraw`: the route's glow under the connection lines, and the outlines and EXIT pill over the boxes.
- `proto_rt.js`: the prototype.
  - Shortcuts the build must not copy:
    - functions wrapped by name;
    - the route search as a copy of `itRpUpdate`'s order (the build shares one search, plan R1);
    - no jump bridges in the mockup's search;
    - the auto-add switch kept in memory (the build makes it a stored setting).
- `boot_rt.js`: turns Intel on, seeds the chain and four pins (Jita, Amarr, 1DQ1-A and the C2), opens Routes, and shows the MOCKUP bar. The bar's scenes:
  - Routes;
  - Hover a wormhole;
  - Hover a gate;
  - Long route (1DQ1-A, 40 jumps: its strip runs to two lines, three on a phone; the hover shows the last square);
  - Routes from here (from the C2);
  - Out in k-space (you jump out at Tama, and every row is worked out again);
  - Signatures by type;
  - Effect numbers (the C3 Pulsar);
  - Intel: list and ring;
  - Intel settings.
- `test_rt.py`: 89 checks, a fresh page per group.

## Results 2026-11-20 (round 2)
89 of 89 checks pass at 1440 and 390 px (after the Set destination button was taken out and the game's group order put in):
- the rows: Home, nearest highsec and nearest lowsec are always there, then the pins in the order pinned;
- 1DQ1-A: 40 jumps, the strip on two lines (the owner: [stated] "include an example with two rows of jumps in the route please").
- Jita: 5 jumps, 5 squares. The hole into Tama is round, the gates are square, and J-space squares are in the wormhole colour;
- hovering the hole: "J122515 → Tama · TUV-907 (K162) · end of life · 0.3 Tama · The Citadel", and the other squares dim;
- a hole with no recorded ID: system to system, with no "ID not known";
- no Set destination button: the rows are a reference (the owner: [stated] "get rid of the "set destination" button and we'll just show the route as it's represented in the panel.");
- pins: typed, from the map menu, removed with ×, and kept in this browser; the Shortest switch is kept too;
- a Dangerous status leaves the routes as they were;
- after the jump out at Tama: Jita 4, Home 2, and no "nearest lowsec" row while you're in lowsec;
- Routes from here, and back;
- Signatures by type in the game's order (the owner: [stated] "unscanned, wormhole, gas site, data site, relic site, asteroid belt, combat site, then the rest for now"; "asteroid belt" read as the page's Ore Site group), then the latest paste's order;
- the rest as round 1: effects, the Intel list and ring, the setting;
- 44 px on a phone: the strip is one target, scrubbed by a finger; no sideways scroll.

Known mockup gaps:
- The nearest highsec from the chain, and systems along the long route, show as "~id": the made-up data has names only for the systems it needs.
- Jita reads 1.0: the open security-rounding bug (backlog, "Security shown from a value rounded twice"); the build uses the page's own security text, so the fix carries over.

check_pii with the names list (fingerprint matched), on the mockup and these scripts: 0 problems. The one embedded image is the page's reviewed CCP login button.

## Design choices shown for the owner to judge
- **Type heading:** it sits over the name column. The icon column's heading holds Select all, so the name heading becomes "Type"; names sit inside their type anyway.
- **Effect numbers:** shown under the System panel's Effect line, not only in a hover.
- **EXIT pill:** to the right of the exit system, drawn only while you hover a row's square. A chain's k-space ends are its leaves.
- **Round squares** for jumps through a wormhole, so a hole doesn't rely on colour alone.
- **The Shortest switch** covers the whole list (off: Intel ⚙ → Routes' preference).
