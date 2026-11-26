# Wormholes map: landmarks don't turn the tree (073 follow-up)

Status: BUILT 2026-11-26 (v2026.11.26.3, branch 074-wh-tree-landmarks; see "Built" at the end). READY 2026-11-26 (the build session, at the owner's request), written against main c53ea11 (v2026.11.26.2). Backlog: BUG in `areas/dscan-backlog-10.md`. No mockup (the owner: "if you suggest one"; none suggested, the check's screenshots at 1440 and 390 px show the result). check_plan_sources 0 problems. **Queued as build queue 074** on 2026-11-26 (`claude/build-queue/074-wh-tree-landmarks.md`).

## 1. What the owner asked

- [stated] 2026-11-26, after 073 went live, with screenshots of his own map (reference only, not kept): his desktop tree ran top to bottom. He moved his landmarks and it read left to right, then "i just had it rearrange the tree and it reverted to top down. add a bug and we'll do a new iteration. with a planning session (unless you dont think we need one)."
- His answers 2026-11-26: "1. this session, 2. your recommendation, 3. if you suggest one." (planned by this session; count only the systems the page lays out; no mockup).

## 2. The cause (reproduced on the real page, main c53ea11, 1440 x 760)

`whTreeDir` (073's D6) works out each direction's fit from `whLayout`'s whole shape: every chain's rows and the deepest depth. A landmark the owner pins for routes (a k-space system, locked, connected to nothing) is a chain of its own. Each one adds a row and a half (a row and the gap after a chain), although it sits where he put it and takes no room in the tree.

His map's shape (J-space Home locked, 9 tree systems, three unconnected locked landmarks), with a free part of the map 1356 x 472:
- without the landmarks: rows 5, deepest 4, left to right;
- with them: rows 9.5, left to right fits worse, so top to bottom.

A reload starts from left to right, and the 1.25 rule can keep it there. Rearrange picks afresh, so it turns back.

## 3. Decisions

| # | Decision | The owner |
|---|---|---|
| F1 | The direction's fit counts only the chains with at least one system the page lays out (not placed: not moved, locked or pinned). A chain whose systems are all placed is left out of the fit. | "2. your recommendation" |
| F2 | Such a chain also takes no rows in the tree's layout, so a chain after it isn't pushed down by an empty band. Its systems stay where they were placed, as before. | the build session's reading of F1 (the same rule for the layout); nothing to decide |
| F3 | The direction is still picked on every width (no fixed left to right on a desktop). | "2. your recommendation" |
| F4 | No mockup. | "3. if you suggest one" (none suggested) |

## 4. The change (where to look)

1. **`whLayout(phone)`** (073, `// ---- the map (build queue 073`): while walking each chain, note whether any of its systems has no `whAt`. Only those chains get rows (`row`) and the gap after them, and count toward `maxd`. A fully placed chain's systems still get an entry in `dr` and `up` (`whPlaces` reads `A` for every system), placed at the current `row` without moving it on.
2. **`whTreeDir`**: unchanged. It reads `T.rows` and `T.maxd`, which now leave those chains out. With no laid-out system at all (everything placed), `rows` is 1 and `maxd` 0: the fit is harmless, and the direction stays as it is.
3. Nothing else: placed systems keep their places; `whPlaces`, the drag pin, the new-system view, Rearrange.

**Stored data:** none.
**Cost:** one flag per chain in the walk that's already there.

## 5. UI rules it touches

None: nothing new is drawn, and no control or text changes. The tree's direction on a map with unconnected landmarks is what changes (left to right on a desktop, as the owner expected).

## 6. Info text it touches

Info text: none. `whmap` doesn't describe the direction. CLAUDE.md's 073 line gets "(chains with a system the page lays out)" after "the direction by fit".

## 7. Checks

In `tools/page_checks/wormhole_tree_check.py`:
- a new seed: the 7-system chain plus three locked landmarks connected to nothing, set aside;
- at 1440 px: the direction is left to right, both on a fresh load and after Rearrange (`M.dirNew`, which picks afresh);
- the same chain without the landmarks gives the same direction (they don't change it);
- at 390 px: the long chain still top to bottom;
- every existing case unchanged.
- **Mutant:** the old rule, counting every chain, must fail.

**Hand test:** on your map, ⚙ → Rearrange as a tree: the tree runs left to right on a desktop and stays so after a reload and after another Rearrange. Your landmarks stay where you put them.

## 8. Questions

All answered 2026-11-26 (section 1).

## Sources

Sources: none (no outside facts). Everything here is the page's own code (main c53ea11), the owner's decisions and the reproduction.

## Built (build queue 074, v2026.11.26.3, branch `074-wh-tree-landmarks`)

- F1 to F3 as planned, in `whLayout`: a chain with no system the page lays out gets no rows and no depth.
- **Beyond the plan, found while building:** `whPlaces` took the shift that keeps other chains beside Home's from the first chain in the tree's order. With no Home set, a landmark (k-space, sorted first) could be that chain, and the tree then moved with it. The shift now comes from the first chain that has a system the page lays out.
- **Checks:** `wormhole_tree_check.py` gained the owner's shape with and without three unconnected landmarks. Rearrange gives the same direction with and without them (left to right at 1440 px); the landmarks stay put; with no Home they don't move the tree. Two new mutants (073's counting; the shift taken from a landmark), both caught. 0 failures, 10 of 10 mutants caught.
