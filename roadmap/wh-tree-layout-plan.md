# Wormholes map: a tree that stays together and reads easily

Status: BUILT 2026-11-26 (v2026.11.26.2, branch 073-wh-tree-layout; see "Built" at the end). REVISED 2026-11-26 by the build session at the build review (round 2), written against main 08011c2 (fc014ce v2026.11.26.1 plus the game-data list of #85; the Wormholes code is unchanged since 52063c1). Round 1 (the research session, 2026-11-26 01:15 PT) is replaced: at the review the owner asked for something its D2 / D7 did the opposite of (section 1). Answers in section 3; one item left to confirm (section 9). Mockup round 2 `Claude outputs/wh_tree_mockup.html`, scripts `roadmap/wh-tree-mockup/` (section 8). check_plan_sources 0 problems. Build queue 073 (`claude/build-queue/073-wh-tree-layout.md`).

## 1. What the owner asked

- [stated] 2026-11-25, with a screenshot of his own map (reference only, not kept): "we need to fix this so the tree is drawn efficiently and easy to read". His map: 7 systems, a locked Home you're in, two systems next to it, one more far off at the end of a long curve; the overview showed three more stacked well away from the rest.
- [stated] 2026-11-26, at the build review of round 1: "ideally, i'd like to be able to move a system w/out it automatically moving any others. other tools do a better job of drawing the tree within the visible area of the map and without the long extended connections that reach across the map. users should have flexibility to move any system they want w/out it screwing up the entire map."
- How he uses it, [stated] 2026-11-26: "generally, locked systems are going to fall under a couple of categories and i tend to set them off to the side so they're seen as being "outside of the big constantly changing tree of systems that are often deleted w/in 24hrs". those systems would be 1. home system in k-space, 2. commonly used systems in k-space that i want to set up auto routes for. this tells me if an exit is close to my organizations' space. 3. j-space home, 4. j-space targets or threats to watch out for."; "so most branches are going to start from the home system in j-space"; "if that's where i am starting. it can start elsewhere (like k-space after a death) but the route "from home j-space" is the most likely trafficked and growing branch."
- [stated] 2026-11-26, asking whether new systems are part of the bug: "is part of the issue that after the user moves that original branch, the page isn't grouping new systems near that branch? instead it goes back to an arbitrary starting point from the original system added when traversing from one system to another?" Yes (section 2).
- [stated] 2026-11-26: "if there isn't enough room in the visible space for a new system to be drawn, would it be better to auto zoom out a bit to make room in view for the new system?" (D9).

## 2. The cause (read in the code, reproduced with the page's own functions)

`whLayout(phone)` (~35325) lays the chain out as a tree from your first k-space entry (columns of 150 by rows of 64; a phone: top to bottom, 130 by 84). `whPlaces(phone)` (~35342) then puts each system you moved or locked where you put it (`whAt`, ~35084), and every other system **only if a neighbour of it has a saved place**: that neighbour's place plus the tree's offset (`.find(m => … P.has(m) && whAt(m))`). A system two or more jumps from anything you moved has no such neighbour, so it falls back to its plain tree place, worked out from the tree's start at the map's origin, whatever you moved. And each new hole re-spaces the tree's rows, so those fallback places move about too.

So: with Home locked off its tree place, Home's neighbours follow it and the rest stays at the origin (the screenshot); after you move a branch, a new hole straight off a moved system lands beside it but the next one, two jumps on, goes back to the origin, joined by a long line (the owner's question above). Reproduced on the real page: the mockup's "7 · today" and "25 · today" scenes (the longest connection 316 and 601 map units; a phone 430 and 1,236; 4 and 5 boxes on top of others in "25 · today").

**Rearrange as a tree doesn't cure it** while a system is locked (D34: Rearrange keeps locked systems where they are).

## 3. Decisions

| # | Decision | The owner |
|---|---|---|
| D1 | **Where a chain's tree starts:** the chain holding the system marked **Home** (the Wormholes status, `whHomes()`, one since 063) grows from Home, wherever you've put it, and comes first; a chain without Home grows from where you started it: your first k-space entry, as today (after a death, the k-space system you scanned out of). | [stated] "Home, else k-space entry (Recommended)"; "so most branches are going to start from the home system in j-space"; "it can start elsewhere (like k-space after a death)" |
| D2 | **Two kinds of system.** *Placed*: moved, locked, or pinned by a drag (D4); the page never moves one. *The tree*: every other system, laid out by the page; each grows from the **nearest placed system above it** in the tree (toward the chain's start), keeping its tree offset from it, however many jumps away; a chain's start with nothing placed above it sits at its tree place, every chain shifted with the first chain's start when that one is placed (so other chains sit beside Home's). | the owner's landmarks: "outside of the big constantly changing tree"; the bug in his question (section 1) |
| D3 | **No system on top of another:** placed systems never move; a tree system that would land on any box goes to the **nearest free row** (alternating; a phone: column), its branch after it. | [stated] "Nearest free row (Recommended)" |
| D4 | **A drag moves only what you drag** (during the drag and after): at the release, every other system the move would shift (the map laid out with the dragged systems where they were, then where you dropped them) is **pinned** where it was: a place of its own, as if you'd put it there. New holes then grow from what you dragged and from the pins. A pin is like a move: Rearrange drops it. | [stated] "ideally, i'd like to be able to move a system w/out it automatically moving any others"; "Auto-tidy, drag pins (Recommended)" |
| D5 | **The tree tidies itself:** holes added or deleted re-lay the tree (tree systems close gaps and make room); placed ones stay. | [stated] "Auto-tidy, drag pins (Recommended)" |
| D6 | **Direction:** left to right or top to bottom, whichever lets the whole tree fit the free part of the map at the larger zoom; the one in use is kept until the other fits **1.25 times** better (so one hole doesn't turn the tree over); Rearrange picks afresh. | [stated] "Pick the direction (Recommended)" |
| D7 | Rearrange as a tree: drops every place you moved and every pin, keeps locked ones (D34), picks the direction afresh, fits. | D34 kept |
| D8 | ~~Round 1's D7, the branch moves while you drag~~: replaced by D4. | — |
| D9 | **A new system you caused** (a jump into a new system; + Add) whose place is out of view: zoom out just enough to show it and the system it connects to together with what you see now, never under the **floor 0.7** (names readable; the zoom whPaint already treats as readable: a fit under 0.7 centres you at 0.9); at the floor, pan to the two (or to it alone if they don't fit). Never during a drag or a pinch: it waits for the release. An import, a shared link or a system added elsewhere doesn't move the view. Its place comes from the tree (D2), so "a free spot in view first" means: in view already, nothing moves. | [stated] "Small zoom, floor, pan (Recommended)" |
| D10 | This build session revises the plan and the mockup. | [stated] "This build session (Recommended)" |
| D11 | A mockup, before / after (round 1's D5; round 2 redone with D10). | [stated] "Yes, mockup (Recommended)" |
| D12 | Its own queue item, not with 069 (round 1's D6). | [stated] "Its own queue item (Recommended)"; queued on [stated] "Yes, queue it (Recommended)" |

## 4. What the mockup showed (round 2)

- **The parent centred on its children is the shortest layout** (round 1's tree, kept). Tried a parent level with its first child instead: longer lines everywhere (the 25-system map's longest connection 521 → 612; the bushy one 657 → 1,289). Kept centred.
- **The long lines left** are (a) a placed system far from the tree, by your choice: the target locked across the map (one line, as round 1 said: "the tree can't be tidy at both ends"), and the pins a drag leaves behind (D4: the dragged system's branch stays where it was, so its lines stretch back to it until the branch's holes die or you Rearrange); (b) a big branch's fan-out: a parent with many systems under it sits halfway along them.
- **The direction (D6) matters mostly on a phone.** Today's spacing (150 by 64) is about the shape of a wide map (~2:1), so a bushy tree fits about as well either way there and the tree stays left to right; a long chain is left to right. On a phone a long chain runs top to bottom and a bushy one left to right. A tree of 31 systems still fits a wide map only at zoom 0.34 either way: past ~15 systems at a readable zoom, a map is panned or zoomed whatever the layout.

## 5. The change (where to look)

1. **`whLayout(phone)`** (~35325): Home first in `order` (D1); return the tree's shape, not only places: each system's depth and row, its parent (`up`), each chain breadth-first, the number of rows and the deepest depth; the direction from `whTreeDir` (D6, a new small function: both fits against `whFree()`, the 1.25 rule, `M.dir` in memory, `M.dirNew` set by Rearrange). Only `whPlaces` calls it (checked 2026-11-26).
2. **`whPlaces(phone)`** (~35342), rewritten (D2, D3): placed systems at `whAt(n)` first; each chain in order, breadth-first: a tree system at its parent's final place plus the tree offset, a chain's start at its tree place plus the first chain's shift; each through **free()**, with **a grid** for the overlap test (cells of the box plus 8 units; the 9 cells around). The mockup's timing, 1,000 systems (`WH_SYS_MAX`): the grid 3.6 ms, a plain scan of every box 5.6 ms. Round 1 expected a scan to be far too slow; it isn't on a real map. The grid stays because on a crowded map (many pins in the tree's way) a scan's cost grows with the square of the boxes, and it's four lines.
3. **The drag (D4):** in `whWireMap`'s release for a move (~37214: `if(d.moved){ for(const n of d.from.keys()) … whS.st.pos[n] = …`): keep the dragged systems' places from before the drag (`d.was`, taken at pointerdown); after saving the new ones, lay out twice (`whPlaces` with the old places, then the new) and save a place for every other unplaced system whose place differs, at its old place; one `whSave`. A click (not moved) does nothing new. No change during the drag: only `d.from`'s systems move, as today.
4. **A new system's view (D9):** `whShowNew(n, nb)` (new): after `whPaint` has placed it. Set where they add one: `whSeen` (a jump into a system the map didn't have: `n` the new system, `nb` where you came from; replaces the plain `whCenter(me)` for that case only, the "you moved: brought into view" line stays for jumps between systems the map has) and `whAddForm` (`nb` its Linked to). Held in `whS.showNew` while `M.drag` or `M.pinch` and run at the release.
5. **Rearrange** (`whZoomBtn` 'arr', ~37172): unchanged but for `M.dirNew = true` (D6) and the ⚙ panel's note (section 7).
6. Nothing else moves: `whFit`, the overview (`whMiniDraw`), `whCenter`, line drawing, Share / Import (places are never shared: `whChainMerge` keeps yours), Remove.

**Stored data:** none new. `tvWhChain.pos` keeps its form (`{id: [x, y]}`) and now also holds the pins; an older page reads them as places you moved (safe both ways: upgrading reads the old places as placed; reverting reads the pins as moves). `tvWhMarks` unchanged.

**Cost (LESSON #120):** `whPlaces` runs only when `whPaint`'s key changes (never per frame); the drag's two extra layouts run once, at the release; `whTreeDir` is part of the layout.

## 6. UI rules it touches

- No new control, class, colour or token. Words change: the ⚙ panel's Rearrange note (section 7). The view moving by itself (D9): only for a system you caused, once, never during a gesture, never below the readable floor; the overview and ⤢ unchanged.
- Phone (390 px): the direction is chosen there too (D6); a free row is the next column when the tree runs top to bottom. Checked in the mockup: no sideways scroll; 44 px targets unchanged (no new control).
- The Intel example: not touched (the Wormholes tab isn't in it).
- **Reuse, don't add:** new functions `whTreeDir`, `whShowNew` (each with its reason in the pull request); the rest changes `whLayout`, `whPlaces` and the release in place. No CSS.

## 7. Info text it touches

`whmap` is at **410 of its 410 words** (2026-11-26; `check_subtext.py` counts words split on spaces). [Moving around], the same 410 words:
- "Drag to pan, the wheel or a pinch to zoom, drag a system to move it." → "Drag to pan, wheel or pinch to zoom, drag a system to move it alone." (−1)
- "⚙ → Rearrange as a tree puts them back; locked ones stay." → "⚙ → Rearrange as a tree starts over from Home; locked ones stay." (+1)
The build re-measures; over the cap: ask the owner. The ⚙ panel's note (not an info panel): "Puts every system back in the tree layout, dropping where you moved them; locked systems stay where they are." → "Lays the chain out again as a tree from Home (else where you came in), dropping where you moved them; locked systems stay where they are." `whmap#mass`: none. The code comment at ~35324 ("a tree from your k-space entry") → from Home, else your k-space entry. CLAUDE.md's Wormholes notes: a line for 073 (placed systems, pins, direction, the new-system view).

## 8. Checks

**Mockup round 2** (`roadmap/wh-tree-mockup/`, built from main 08011c2): `test_tree.py`, 82 checks at 1440 and 390 px, 82 pass; 8 of 8 mutants caught (a ninth, the scan instead of the grid, can't be told apart by timing and was dropped: section 5). The build's `tools/page_checks/wormhole_tree_check.py` comes from it (made-up chains from the page's table, a fresh page per group, both widths):
- today's bug shown (a connection over 300 units in the 7-system chain);
- 7 systems, Home locked: none on another; Home where it's locked; every connection one tree step; the tree starts at Home; Home's status off: the chain starts at the first k-space entry, the locked system stays;
- 25 systems (Home, a target and the k-space home locked and set aside, one moved, a loop, a chain scanned out of the k-space home): none on another; every placed one where it was; each tree system within a tree step of the one above it (at most two pushed further by free rows); the k-space chain beside the k-space home;
- a drag with real pointer events: during the drag and after the release nothing but the dragged system moves; its branch is pinned, systems it wouldn't shift aren't; a new hole off the dragged system grows beside it;
- holes come and go: placed systems stay, tree systems move (closed up), none on another;
- Rearrange: none on another, pins and moves dropped, locked kept;
- direction: a long chain left to right wide, top to bottom on a phone; a bushy one left to right; the 1.25 rule (kept on a wide map, turns on a phone);
- a new hole out of view: in view after, zoom never under 0.7, a small zoom out on a wide map; one arriving during a drag waits, then shows;
- 1,000 systems placed in under 50 ms; no sideways scroll; no page errors.
- **Mutants**, each must fail: today's one-hop placing; no free row; the tree not starting at Home; a system not following the placed one above it; a drag that pins nothing; the direction never chosen; a new system never brought into view; the view moved during a drag.
- Existing checks to re-run and read: `wormhole_menu_check.py`, `wormhole_tab_check.py` (a drag saves a place; Rearrange drops them: now also pins), `wormhole_home_check.py`, `wormhole_layout_check.py`, `wormhole_routes_check.py`.

**Hand test:** on your own map: the tree grows beside your locked J-space Home; your landmarks stay where you set them; drag one system: nothing else moves; jump into a new hole: it appears beside the system you came from, and the view zooms out a little if it's off screen; delete a dead branch: the tree closes up; ⚙ → Rearrange as a tree: a tidy tree from Home, the locked ones where they were.

## 9. Questions

- Round 1's Q1–Q5: answered 2026-11-25/26 (Q5's "Move while dragging" replaced by D4 at the review).
- Round 2, answered 2026-11-26: tree changes (D4, D5), a new system's view (D9), the direction (D6), who revises (D10).
- **To confirm:** the Routes panel's Home row follows the Home status (`whRtRows`), so with Home on your J-space home it shows the way to the J-space home, and your k-space home is a pinned route (system menu → Pin route) like your other k-space systems: the same search, without the Home label. (Nothing to build either way; a Home label for a k-space landmark would be a backlog item.)

## Sources

Sources: none (no outside facts). Everything here is the page's own code (main 08011c2), the owner's decisions and the mockup's results; the systems in the mockup are from the page's own table (`INTEL_WH`) and four k-space systems' names.

## Built (build queue 073, v2026.11.26.2, branch `073-wh-tree-layout`)

- As planned, D1 to D12. Section 9's item: the owner's "go" came after it was put to him; nothing was built for it.
- **Where the build differs from the plan:**
  - `whPaint`'s existing "you moved: brought into view" now waits for a drag or pinch to end, like D9's view. The release paints once if a view waited (`upNew`). Found while writing the page check: the mockup's `whSeen` wrapper put the camera back and hid it (LESSON #185).
  - `whTreePin` takes the dragged systems' places from the press (`M.drag.was`).
  - The page check has no "today's bug shown" case, because the page no longer places systems the old way. The mutant "a system not following the placed one above it (one jump only, as before 073)" stands in for it.
  - The ninth mutant (a scan instead of the grid) was dropped, as section 5 says.
- **Checks:** `tools/page_checks/wormhole_tree_check.py`, at 1440 and 390 px with real mouse drags: 0 failures, and all 8 mutants caught.
