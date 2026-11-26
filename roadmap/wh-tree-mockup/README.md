# Mockup: Wormholes map tree, round 2 (plan roadmap/wh-tree-layout-plan.md)

Round 1 was made 2026-11-26 by a research session from `main` 52063c1. Round 2 was made the same day by the build session at the build review, after the owner's answers (plan section 3), from `main` 08011c2. It replaces round 1's prototype, scenes and checks. The file `wh_tree_mockup.html` is sent to the owner and kept in the repo's `Claude outputs/`.

The real page runs with no network: the repo's `roadmap/paths-to-you-mockup/mock.js` is the runtime, with storage in memory. The chains are made up from CCP's own wormhole systems, picked by class from the page's table (never the owner's systems), plus four k-space names. `proto_tree.js` holds the new rules. No pilots, corporations or channels.

    python3 -I build_tree.py <repo>/index.html <repo>/roadmap/paths-to-you-mockup/mock.js wh_tree_mockup.html
    python3 -I test_tree.py wh_tree_mockup.html [--mutants build_tree.py <repo>/index.html <repo>/roadmap/paths-to-you-mockup/mock.js]

## Files
- `build_tree.py`: puts together the page, the runtime, the prototype and the boot script, and swaps the page's CSP for one with no network.
- `proto_tree.js`: the prototype. `TREE.mode` is 'new' or 'today' (the page's own `whLayout` / `whPlaces`).
  - It covers: the tree's shape (Home first); the direction (1.25 rule); placing (placed first, then each tree system from the nearest placed one above it, free rows on a grid); the drag pin (two layouts at the release); and the new-system view (zoom, floor 0.7, pan; held during a drag).
  - Shortcuts the build must not copy:
    - the functions are swapped by name;
    - the drag pin is extra canvas listeners (the build puts it in `whWireMap`'s release);
    - `whSeen` / `whAddForm` are wrapped to notice a new system (the build sets it where they add one).
  - Page steps inside the wrapped calls (LESSON #185): `whSeen` and `whAddForm` end in `whPaint`, whose "you moved: brought into view" re-centres on you. The wrapper's camera restore hides it, so the build re-checks it on the page.
- `boot_tree.js`: seeds a chain, opens the Wormholes tab and shows the MOCKUP bar. The scenes:
  - 7 · today / new: the shape of the owner's screenshot (a C4 Home, locked and set aside);
  - 25 · today / new: the J-space Home, the k-space home (Rens) and a target, all locked and set aside; branches; a loop; one moved system; a chain scanned out of the k-space home;
  - Drag one system: a scripted drag, then a new hole beyond the dragged system;
  - Holes come and go: a branch removed and two holes added;
  - Long chain / Bushy chain: the direction each width picks;
  - New hole out of view / …far out of view: a jump into a new hole (zoom, or pan at the floor);
  - Rearrange as a tree.
  - `TRbig()` builds 1,000 systems for the timing check.
- `test_tree.py`: 41 checks per width (82 at 1440 and 390 px), with a fresh page per group, and 8 mutants.
- `snap.py`, `cmp.py`: screenshots of the scenes; the comparison of a parent centred on its children with one level with its first child (plan section 4).

## Results 2026-11-26
82 of 82 checks pass. All 8 mutants are caught:
- today's one-hop placing;
- no free row;
- the tree not starting at Home;
- a system not following the placed one above it;
- a drag that pins nothing;
- the direction never chosen;
- a new system never brought into view;
- the view moved during a drag.

A ninth mutant, a scan of every box instead of the grid, was MISSED, and is dropped. On 1,000 systems the grid takes 3.6 ms and the scan 5.6 ms (2.0 and 3.1 ms with half of them pinned), so no realistic map separates them; the build keeps the grid for crowded maps (plan section 5).

check_pii: 0 problems.
