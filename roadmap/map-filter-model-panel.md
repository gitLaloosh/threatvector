# Panel review: the Intel map's filters, stacked (brief)

**In the repo (build queue 058, 2026-11-16):** copied from the Project doc `claude/roadmap/map-filter-model-panel.md` by the build session; built as v2026.11.16.3 (`roadmap/intel-map-stack-plan.md`, its Built notes). Paths below that start `claude/roadmap/` are the Project's; the repo copies are under `roadmap/`. Line numbers are main e7f5a2b's (v2026.11.15.3).

**Status (2026-11-16, later):** **decided and planned, not queued.** The owner answered 21 questions on 2026-11-16 (the 13 below, plus questions from the prototype, the light-year idea and 045's Wormholes look); his answers and the build are in `claude/roadmap/intel-map-stack-plan.md`, which supersedes the open questions in this brief. Answers that differ from the panel's recommendation: Sov levels are ticked boxes, any ticked level counts (not "level N and up"); "Distance: jumps / light years" is a later item (section 6b); wormhole rings are not a never-fading mark (with Wormholes on, only matching holes get the filter's marks; the rest follow the off-filter rule). The prototype has been updated to match (142 checks pass). The rest of this brief is kept as the research record.

**Earlier status (2026-11-16):** research only, nothing decided. A 3-helper panel review (plus a critique round) run by a research session on 2026-11-15/16 against main e7f5a2b (v2026.11.15.3); 053 merged after it as v2026.11.16.1 (PR #58, main 51207b6), checked below. Not planned, not queued. The owner's 13 decisions (section 6) are open. **Prototype built 2026-11-16** ([stated] "since you provided recommendations, how about you build a prototype using them and i'll decide after."): `stacked_filters_mockup.html`, sent to the owner; scripts in `claude/roadmap/map-filter-stack-mockup/` (README there; 104 checks pass at 1440 / 390 px; check_pii 0 problems, names checked). A plan comes after his answers.

**The owner on the prototype:** [stated] 2026-11-16 "quick note - disabling a filter (like security range) should hide the settings button for it." → done in the prototype: a settings button shows only while its filter is on (or its panel is open), switching a filter off shuts its panel; all four (Security range, Within N jumps, Wormholes, Sov). For the build this changes 052's rule that a filter's panel button also shows on hover (CLAUDE.md "The Intel tab's layout").

[stated] 2026-11-16, with screenshots of Region, Jumps and Security zoomed in: "my one remaining concern right now, is that i can't toggle anything "off". this isn't an easy view to read.", then "it's about the base color groups sort of washing out the other data but the off switch for color groups is welcome too." → done in the prototype:
- **No colour:** pressing the colour that is on turns colour off (every system plain grey, no number in its circle; the stack kept).
- **Soft colour** (MOCKUP box "Colour": Full / Soft, Soft the default): zoomed out a system's colour is mixed 45% toward the background; zoomed in it's a dark disc tinted with the colour instead of a solid one, so rings, tags and labels stand out. A system your conditions match keeps the full, solid colour.
- A first try drew a coloured outline and was dropped: on this map a ring means a report, and a red outline read as hostiles.
- New questions for him: Soft as the default look for every colour; whether the map starts with no colour.

## 1. Why

- [stated] 2026-11-15: "i need the ability to have filters from some existing types work together. example: i want to see systems with threat detection array level 3 where system security level is N. what kinds of changes are we looking at? right now we can only apply filters of one type at a time. what i'm envisioning is an on/off state based on the settings for that filter so you can sort of stack them on top of each other."
- [stated] "i have a feeling there would be a fair amount of conflict between colors and highlighted vs faded states."
- [stated] "we would need to support numeric security status range in the filter. like -0.3 to -0.5"
- [stated] "it seems like this could be come a complicated mess so i would like to break things down to their basic form and figuring out how best to categorize them and allow the user to tailor the map contents to what is most helpful to them at that time."
- [stated] future filters to design around: "jumps in past hour, average pilots in space, my fleet, structures of various types. just as examples for them to consider as they do this evaluation"
- [stated] "3 helpers. do it"

## 2. Recommendation: four roles, one job per visual channel

- **Colour by** (pick one): Security, Jumps from you, Region. Later: jumps or kills in the past hour (numbers per system).
- **Show only** (conditions, switched on and off; each keeps its settings while off): security range, within N jumps, region pick, has an Intel report, has kills, has a kept wormhole, Sov kinds (053, with a level minimum later). Later: structure types (the same "kinds a system has" shape as Sov). Every condition that is on must match; inside one condition any pick counts (as Sov picks already do).
- **Marks** (always drawn, never faded by a condition): Intel report rings (hostile, neutral), the alert-range glow, your pin, wormhole rings, ✕ kill counts, routes. Later: fleet members (pilots in places, like your pin).
- **View:** Paths to you stays apart (it replaces the galaxy, `itPtLive`).
- **Not a filter:** 041's jump bridges stay a distance setting and lines on the map.

So: hue comes only from Colour by; Kills and Wormholes stop colouring dots (their ✕ counts and rings already say where). While any condition is on, brightness means "matches" only.

## 3. What it rests on (checked by the research session against main)

- Every system at 0.0 or below gets the same purple: `itMapSecClass` returns 0 for `s100 <= 0` (index.html, e7f5a2b, 29626). The security number shows only zoomed in (gate 34 px or more, 30080-30101). So the owner's −0.3 to −0.5 can't be shown by colour: it has to be a condition.
- Two meanings share almost the same fade: filtered out `IT_MAP_DIM` 0.16, past "Map: within" `IT_MAP_FAINT` 0.22 (29983, `alpha` 30045).
- Three filters set both colour and fade: Kills (amber dot + dim), Wormholes (lilac dot + dim), Intel reports (dim) (`itMapFcol` 30017-30024, `itMapDimmed` 30025-30031).
- Exact colour copies: `IT_MAP_REGION` (29982) holds the accent cyan #4fc3d9 (hover ring, chip ring, routes) and the kill amber #d99a3c; `IT_MAP_JUMPS[8]` is the null-sec purple #8f2f69 (29981, 29584).
- Report rings draw at 0.95 whatever `itMapDimmed` says (30111), except on the Wormholes filter, where the other reports fade (`IT_MAP_WH_FADE`, 30110; 045).
- The stepper `RS` takes its own `steps()` list and a `unit` override (31850-31868): two From/To steppers give a security range without a two-handle slider (one slider style, CLAUDE.md "UI rules").
- Shown value vs stored: security is stored in hundredths (Int8Array, 29595); `itMapSecText` rounds with `Math.round`, so −0.55 shows as −0.5 and −0.25 as −0.2 (30016; checked in node).
- The map redraws on hover (mouseleave → `itMapDraw`, 31799), so the stack's matches should be worked out once per change of the conditions (a `Uint8Array` folded into `itMapKey`, 29839), never per draw (LESSON #120).
- The one-line legend rule (CLAUDE.md 438) no longer protects anything: since 052 Near You's height comes from the map box (`--it-mh`, 29813) and the legend sits below the box (29779). A second line moves the Feed a little, not Near You.
- 053 as merged (51207b6): `tvSov` is read into a fresh object with only `v`, `lists`, `pick` (31460-31471) and saved from it (31475-31476). A field added to `tvSov` later would be read safely by the 053 page but erased when it saves. So the Sov level minimum belongs in the stack's own new key, not in `tvSov`.

## 4. Where the helpers disagreed, and the session's call

- **Which marks a condition may fade:** one helper faded unmatched rings except inside the alert range; two said hostile/neutral rings, the alert glow and the pin never fade. Call: never fade (a stack remembered from last night must not hide a 12-man gang 6 jumps out). This overrides 045's "the other reports step back" on the Wormholes filter, which the owner approved ("keep all of it"): his decision.
- **"Within N jumps" as a condition:** one kept it, one dropped it as "Map: within" again, one conceded low priority. Call: keep it. Matches are bright anywhere (the owner's "All of them, anywhere" for Wormholes, "Bright anywhere" for Sov), so "−0.3 to −0.5" alone lights all of null-sec; "Map: within" only fades.
- **Labels on matches:** one would label every match; another showed ~86 Sov systems would flood the map. Call: today's room-only labels.
- **Paths to you:** the rail or a View group in the filter column. Left to the mockup.

## 5. Unverified

- How the game rounds negative security (it may show −0.55 as −0.6, where the page shows −0.5). Settles in a hand test: compare a few systems with the game.
- Whether bright against 0.16 reads on 1.4–3 px dots at the starting zoom on a phone. **The prototype says not well enough:** three matches by brightness alone were hard to find, so it also draws a matching dot 1.6 px bigger when zoomed out (its MOCKUP box switches between the two).
- The per-frame cost of a stack (not measured; the perf harness wasn't run).
- The panel's own assumptions, not the owner's words: one colour at a time, and "every condition must match".
- Every future ESI filter (section 7).

## 6. The owner's decisions (open; the session's recommendation in brackets)

1. The four-role model: Colour by, Show only, Marks, View? [Yes.]
2. Every condition must match, any pick within one counts, no user-built OR/NOT? [Yes.]
3. Kills and Wormholes stop colouring dots? [Yes.]
4. While conditions are on, brightness means match only and the distance fade steps aside (the gate lines still fade past the reach)? [Yes.]
5. Matches bright anywhere, plus a "within N jumps" condition? [Yes.]
6. Hostile and neutral rings, the alert glow and your pin never fade, overriding 045 on the Wormholes filter? [Yes.]
7. Security range as From/To steppers comparing the shown 1-decimal value, inclusive, either order? [Yes.]
8. Sov "level N and up", stored in the stack's new key (not `tvSov`)? [Yes.]
9. Remember the stack between visits, with "2 on · 14 match" on the phone's filter button and in the legend? [Yes.]
10. A "14 match ›" chip that steps through matches nearest first (the wormholes chip made general)? [Yes.]
11. Reserve hues: cyan for focus, amber for alert, lilac/pink for wormholes; Region loses its cyan and amber? [Yes.]
12. A second legend line for the active conditions (a CLAUDE.md rule change)? [Yes.]
13. A mockup before the plan? [Yes.]

Also left out or deferred by the panel: "average pilots in space" (no ESI route found), "my fleet" (fleet boss only, DLA 2.3(c)), saved views (only if toggling proves slow), OR/NOT logic.

## 6b. DECIDED 2026-11-16: "Distance: jumps / light years" is a later item

The owner's answers (Q17-Q20 in `claude/roadmap/intel-map-stack-plan.md`): a later item, not this one; shade the systems in range (not a ring); type the LY now, a ship picker later; not its own "Colour by" for now. Filed in the backlog as its own item. The notes below are kept for that item.

[stated] 2026-11-16: "ok i'm liking this so far. make a note for now but let's decide on whether to include it before we're done with this session... modify "within N jumps" filter to be "Distance: jumps / light years" and allow the user to draw a ring around their location that reflects the specified distance in light years (ring, shading, whatever). gives the user awareness of what systems are within jump range of them with cynos depending on type."

- **What it would be:** the "Within N jumps" condition becomes "Distance", measured either in stargate jumps (as now) or in light years from your system, plus something drawn around you that shows the light-year reach.
- **What the page already has (checked, main 51207b6):** `INTEL_MAP.p3` holds CCP's 3D positions of every system (0.0001 LY), and the map hover already shows "N.NN LY from <you>" (`itMapLy`, `itMapLyText`, rounded up to 0.01; v2026.11.04.1, roadmap/map-ly-hover-plan.md; CLAUDE.md 439). So matching systems within N LY needs no new data.
- **A catch for the "ring":** the map is a 2D picture of 3D space, so the systems within N LY don't form a circle on it. A circle drawn at N LY would include some systems that are out of range and miss some that are in range. Shading or outlining the systems that really are within range (worked out from 3D distance) is exact; a ring could be offered as a rough guide only.
- **"Depending on type":** ship jump ranges (by hull class and skills) and the rules on where a jump drive can land are game rules from outside the project: a plan would take them from CCP's static data and docs, with sources. Not checked yet.
- **An earlier decision it extends:** when the LY hover was planned, [stated] 2026-11-02 "i'm just looking for the distance in LY (from the player's current system) to show up in the data seen on hover." (roadmap/map-ly-hover-plan.md: no range mode, no ship classes). This would add a range mode.
- **To settle with the owner:** include it in this item or a later one; light years only for the condition, or also a ship-type picker that sets the range; ring vs shading; whether it can be its own "Colour by" (distance as a scale).

## 7. Future filters: what ESI seems to offer (none verified)

CCP's ESI spec refused an automated read (esi.evetech.net swagger.json: robots_disallowed, tried 2026-11-15), so every row is UNVERIFIED until checked in CCP's API Explorer.

| Candidate | What it seems to be | Role it would take |
|---|---|---|
| Jumps in the past hour | public `/universe/system_jumps/`, all systems in one call | Colour by, or a range condition |
| Kills in the past hour (ship, pod, NPC) | public `/universe/system_kills/` | Colour by, or a range condition |
| Average pilots in space | no ESI route found; the in-game map only | none |
| My fleet | `/fleets/{fleet_id}/members/` (system, ship), scope `esi-fleets.read_fleet.v1`, reportedly fleet boss only | Marks |
| Structures by type | public structure ids; details need a login and docking access; corp structures need a role; sov structures public | Condition (kinds) |
| Wormhole space | per-system jump/kill statistics were removed from the API for wormholes | a "no data" state that isn't "doesn't match" |

## 8. Cost

Round 1: 142,946 + 146,182 + 153,045 = 442,173 tokens (the helpers' own counts). The critique round's count wasn't reported back; the total was likely about 600–700k.

## Sources

| Fact | Source | Checked | Status |
|---|---|---|---|
| `/universe/system_jumps/` exists, per system, last hour | apis.apievangelist.com, a secondary listing of the Universe API (not CCP's) | 2026-11-15 | UNVERIFIED: confirm the route and its window in CCP's API Explorer, https://developers.eveonline.com/api-explorer |
| `/universe/system_kills/` exists | CCP's developer blog, https://developers.eveonline.com/blog/removal-of-deprecated-versions-of-several-routes (primary for the route's existence) | 2026-11-15 | verified (route exists) |
| `/universe/system_kills/` covers the last hour | rubydoc Greeve Map::Kills, a secondary library doc | 2026-11-15 | UNVERIFIED: confirm the window in CCP's API Explorer |
| No ESI route for pilots in space per system | forums.eveonline.com/t/population-distribution-in-eve/256841, a secondary forum source; no route seen | 2026-11-15 | UNVERIFIED: confirm in CCP's API Explorer that no route exists |
| Fleet members carry `solar_system_id`, `ship_type_id`; scope `esi-fleets.read_fleet.v1`; fleet boss only | php-esi-lib docs and apis.io's copy of the spec, both secondary | 2026-11-15 | UNVERIFIED: confirm scope and who may read in CCP's API Explorer |
| Structure details need a login and docking access | forums.eveonline.com/t/…/145481, a secondary forum source | 2026-11-15 | UNVERIFIED: confirm in CCP's API Explorer |
| Wormhole jump/kill statistics removed from the API | evenews24.com/2014/05/06/tweetfleet-worm-hole-npc-kills-api-tweak, a secondary news source quoting a CCP developer | 2026-11-15 | UNVERIFIED: confirm in CCP's API Explorer that wormhole systems are absent from system_jumps / system_kills |
| How the game rounds negative security for display | not found | 2026-11-16 | UNVERIFIED: compare a few systems in game with the map's shown values (hand test) |
| `Math.round(-5.5)` is −5 in JavaScript | a live answer seen in the research session: `node -e "console.log(Math.round(-5.5))"` printed -5 | 2026-11-16 | verified |
