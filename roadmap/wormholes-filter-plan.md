# Plan: the Intel map's Wormholes filter (wormhole mapping, phase 1)

Status: planned 2026-11-12 by a research session from main 1e22ec7 (v2026.11.12.3, build queue 039's map); **queued as 040** (2026-11-12, [stated] "Yes, queue it (Recommended)"; claude/build-queue/040-wormholes-filter.md). check_plan_sources: 0 problems. Mockup: `wormholes_filter_mockup.html` (sent to the owner 2026-11-12; see "Mockup").

Backlog: "Intel map: Wormholes filter (wormhole mapping PHASE 1)" (memory areas/dscan-backlog-5.md). Phases 2–4 (your own jumps, the chain view, sharing) are in claude/roadmap/wormhole-mapping-plan.md (a draft; its D-list is for those phases).

## The owner's decisions
- [stated] 2026-11-12: "before we do, we'll take what we've learned and plan a new filter for the latest intel map for wormholes. we'll consider this phase 1 of a multi-step process."
- Words (2026-11-08): wormholes are reported as "wh", "wormhole", "drifter"; capture only that one exists in a system; kept across reloads; retention in settings. 2026-11-11: "Default 24 h, a setting (Recommended)".
- Reach: "All of them, anywhere (Recommended)": with the filter on, every kept wormhole report lights up wherever it is.
- Other filters: [stated] "Show newly reported as you would intel reports on the jump count filter (drop off the map and feed like other reports and kills) but the difference being that they're retained for 24hrs in the browser and those are used by the wormhole filter."
- [stated] "add a wormhole badge to intel as well."
- [stated] 2026-11-12: "add a panel to manage the list (manually add/remove wormholes from the list in browser storage - for any added manually, they'll be retained 24hrs or whatever the setting is, from the time they were manually added). this way you can remove wormholes that you find to have gone critical and collapsed. accessing the list can be done by hovering the wormhole button on the map. doing so will show another icon (floating to the right of the wormhole filter button) that accesses the list. close can be done by clicking outside the list or clicking the x on the panel it's housed in."
- Your own entry/exit systems: "Phase 2 (Recommended)". Mockup: "Yes, mockup first (Recommended)"; then "looks good. write the plan".

## What the page does today (main 1e22ec7)
- A line with a system and no pilots ("RERZ-L wh on the sun") gets kind 'info' (itKind ~26860). itReportNear (~26878) returns early for 'info', so it never reaches it.near: it shows on the Feed only, and no map filter draws it (checked in the mockup: it.near held only the two pilot reports).
- Every report is forgotten after "forget reports after" (it.set.forget, IT_FORGET ~25969, stored in `dscanIntel`), in memory only.
- 039's filter bar: IT_MAP_FILTERS (~29163), itMapFbarHtml / itMapFbtnsHtml (~28948), itMapFbarPaint / itMapFbarOpen / itMapFilterSet (~28954–28975), itMapFcol / itMapDimmed (~29175), itMapDraw (~29201), itMapFLegHtml / itMapFLegTitle (~29376), itMapLegend (~29389), itMapTip (~29397). The filter isn't remembered (Security on every visit).

## What to build
1. **Wormhole store.** A new localStorage key `tvWormholes`: `{v: 1, rep: {<systemId>: {id, t, who, drifter, src}}, gone: {<systemId>: t}, keepH}`. A key of its own, so older pages ignore it and `dscanIntel` keeps its form (README "Stored browser data": safe both ways). Read back with checks: known system ids only, numbers in range, `keepH` one of the choices, at most 500 entries.
2. **Taking reports.** Where Intel takes a line (not a timer over it.feed as the mockup does): a non-kill line with a system and a whole word "wh", "wormhole" or "drifter" stores/refreshes `rep[system]` (t = the line's time, who = the reporter, drifter = the word "drifter", src 'intel'). It doesn't change the line's own kind or alerts. Skip it if `gone[system]` is at or after the line's time (removed by hand), or if the stored one is newer.
3. **The setting.** "keep wormhole reports for" 1, 2, 4, 8, 12, 24 (default), 48 h, a `<select>` beside "forget reports after" in Intel's settings box ("Range and alerts", ~28436), saved in `tvWormholes.keepH`. Entries older than the window are dropped on read; anything past 48 h is deleted from storage.
4. **The sixth filter, "Wormholes"** (IT_MAP_FILTERS, last; a wormhole-swirl icon as in the mockup): kept systems in `--wh` (Drifter in its lighter shade), the rest dimmed, as "Intel reports" does. Kept systems are bright anywhere, past "Map: within" too (the owner: "All of them, anywhere"): itMapDraw's alpha needs a case for them (the mockup redraws them on top instead). Each gets "WH · 3 h" / "DRIFTER · 6 h" on its left (the page writes names on the right), with a dark backing for contrast. Legend filter line (one line): "Wormholes ▪ reported ▪ Drifter · last 24 h · dim: none"; its title explains.
5. **Other filters.** A wormhole report inside "forget reports after" and "Map: within" draws a wormhole ring (two rings in `--wh`) with "WH · 5 min" on its left; it goes when the forget window ends, like other reports. Legend: a "wormhole reported (WH)" entry. Hover (itMapTip): "Wormhole · reported by X, 3 h ago" (or "added by you"); the "nothing reported" line is dropped for a live one, and the "reports aren't shown here" line under the Wormholes filter for a kept far one.
6. **The badge.** "Wormhole" / "Drifter WH" (`.it-gtag` with a new class on `--wh`) in the Feed row's tag place (`.ftg`, itFeedRowHtml ~28124) and in Near You's tags (itNearTagsHtml ~27939) when a shown report is a wormhole one; its title says who and when, and that it's kept for the filter.
7. **The list.** A list button (`data-whf-list`, a list icon) right after the Wormholes button, floating to its right outside the toolbar's box. Shown on hovering or focusing the Wormholes button (hidden again 0.6 s after the pointer leaves, so it can be reached), on its own hover/focus, while its panel is open, and always while the Wormholes filter is on (a phone has no hover; there it sits in the opened filter row). Pressing it opens a panel (role="dialog", "Wormhole list") inside the map box above the filter bar, right-aligned (full width less 8 px on a phone); on a phone the filter row closes as it opens.
   - Head: "Wormholes" · "kept 24 h, in this browser only" · the shared `button.x-close`.
   - Add: a text field (System), a Drifter checkbox, Add. The name must be a system on the map (it.names; wormhole systems come in phase 2): else "“X” isn’t a system on the map". Added by hand = `src 'you'`, `t` = now, so it's kept the setting's hours from then; adding a kept one renews it. A status line says what happened.
   - Rows, newest first: jumps from you, system, the badge, "reported by X · 5 min ago · gone in 24 h" (or "added by you"), Remove. Remove deletes it and sets `gone[system]` to its time, so the same Intel line can't bring it back (a newer one can).
   - Close: ×, Esc, or a press outside (not on the list button); focus back on the list button (on a phone, the filter button). The rows refresh while open (ages), never while a field in it has focus.

## UI rules it touches
- One tag style (`.it-gtag`), one close button (`button.x-close`, 32 px, 44 px on a phone; check_ui_rules 5, close_buttons_check), the filter bar's 32/44 px buttons, text field and checkbox styles as the page's.
- Colour tokens only: a new `--wh` (#a98bd8) and a Drifter shade (#e4b5ff in the mockup) as a token too; the label backing as a token or the map's existing panel colour.
- Drawing cost (LESSON #120): drawn inside itMapDraw; no timer redraws; the list's age refresh only while it's open, as text, with a compare.
- 039's legend rule: the filter line stays one line (Near You's height doesn't move).
- Phone: 44 px, no sideways scroll at 390 px (mockup checked); the list button in the opened row.
- Menus vs dialogs: the panel is a dialog (form inside), so it has the close button.
- Intel example (017): the example's map draws the filter bar? (29070: the example keeps markers off the bar.) A sixth button widens the bar: check the markers at 1440 and 390.
- Page size: small (no data table). Served 510,858 of 800,000 at 1e22ec7.

## Info text it touches
- `intel` "[Map]": add "Wormholes: systems where Intel mentioned a wormhole (wh, wormhole, drifter), kept 24 h (a setting); the list button beside it adds or removes one." Keep within the panel's length cap (check_subtext).
- Intel settings: the new select's title. The Feed/Near You badge title.
- Off-limits as always: the Lookup budgets gauge; the example's tutorial text except to correct it.

## CCP's Developer License Agreement
2.3(c) (claude/reference/dla-planning-notes.md): the store keeps, for up to 48 h in this browser, which system a wormhole was reported in and **who reported it** (another player's name from the user's own intel channel). Nothing leaves the browser. The digest says storing other players' activity over time needs the owner's decision. **Decided 2026-11-12:** "Keep the name (Recommended)": the reporter's name stays in the 24 h store (hover and list say "reported by X"), in this browser only, never sent anywhere.

## Checks to build
`wormhole_filter_check.py` (new): wh / wormhole / drifter lines stored with the right flags, "whatever" or "whiskey" not; the filter's colours and dimming (a kept far report bright); other filters draw the live ring and drop it after the forget window; the badge on the Feed and Near You; the setting changes what's kept and survives a reload; the list button shows on hover/focus and with the filter on, the panel adds (unknown names refused), removes (and the same line doesn't bring it back), closes by ×, Esc and outside press with focus back; 1440 and 390 px, no sideways scroll, no page errors; stored data read safely (a bad `tvWormholes` is ignored). Mutants: the filter not dimming; removal not setting `gone`; kept reports limited to "Map: within".

## Mockup
`wormholes_filter_mockup.html` (sent 2026-11-12): the real page (main 1e22ec7) with made-up Intel around C-J6MT ("Mk …" / "Mockup …" names) and kept reports in Tama, Amamake and 1DQ1-A (ids checked against the page's own map table). MOCKUP bar: post a "wormhole" line, flip Wormholes / Security, open the list. 51 checks passed at 1440 and 390 px, no page errors, no sideways scroll. check_pii not re-run on the new scripts (names read by hand). Its scripts are in Project docs `claude/roadmap/wormholes-filter-mockup/` (README, proto_whf.js, build_whf.py, mock.js, boot_wh.js, test_whf.py): the build session rebuilds the HTML from main and commits it to `Claude outputs/`. When the item is done, the plan and that folder move to the repo's `roadmap/` (README "Finishing an item", 2026-11-12).

## Build review (2026-11-12, the build session, main 1e22ec7)
The plan matches main (039's names and lines). The owner's answers at the review:
- **The words are intel keywords** ([stated] "Keywords (Recommended)"): "wh", "wormhole", "drifter" go into `IT_KW` (like ESS, bubble, camp), so they're never looked up as pilots unless dragged in (real characters can be named "Drifter" or "Wormhole"). Step 2 reads the keyword (`p.kw`), not the raw text; the Feed badge reads it from the entry.
- **Hand-added wormholes: the Wormholes filter and the list only** ([stated] "Wormholes filter only (Recommended)"): step 5's live ring and step 6's badge are for what Intel reported (`src 'intel'`), never `src 'you'`.
- **"drifter" alone counts** ([stated] "Drifter alone counts"), as decided 2026-11-08, though a line about the Drifter NPC battleships ("drifters on gate") is kept as a Drifter WH too.
Fixed in the build (not in the plan above):
- The Intel example: `itExSandbox` sets the store aside (an empty one inside), so the example's lines never write to `tvWormholes` and its map and Near You never show the user's wormholes.
- `itMapRefresh`'s key includes the kept systems and each WH label's text, so a label's age and a report's end redraw the map through the existing refreshes, with no new timer (LESSON #120).
- The WH labels give way like the names (`itm.nameBoxes`, the filter bar's box), not drawn over them.
- `gone` entries are dropped after 48 h, like `rep`.
- Timed at the largest settings (LESSON #160): 500 kept, 48 h, the map's full reach, zoomed out to the galaxy.

## Sources
Sources: none (no outside facts). Everything here is the page's own code (main 1e22ec7) or the owner's decisions.
