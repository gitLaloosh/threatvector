# Plan (READY): Intel map filters from live data: who holds each system, jumps and kills in the past hour, and a region pick

Status: BUILT 2026-11-23 (build queue 065, v2026.11.23.1). Was READY 2026-11-20 (research session, main f70fdd5, v2026.11.20.1). All questions answered 2026-11-20 (section 7). Mockup sent 2026-11-20 (section 8); Q9 (ring), Q10 (live colours skip the fades) and Q11 (More) answered, Region pick's Select all added. All questions answered. **QUEUED as build queue 065** 2026-11-20 ([stated] "yes"; `claude/build-queue/065-live-map-filters.md`).
Planning list item C (`claude/roadmap/intel-planning-list.md`, the owner: [stated] "plan c"). Backlog entries: "Intel map: a sovereignty filter (who holds each system)" (dscan-backlog-3), "Intel map: jumps in the past hour", "kills in the past hour", "region pick" (dscan-backlog-7). All build on 058's model (repo `roadmap/intel-map-stack-plan.md`; brief `roadmap/map-filter-model-panel.md` sections 2 and 7).

Panel review: not a fit. The ESI facts below were checked live, and the look is the owner's eye.

## 1. What ESI gives (checked live 2026-11-20 from threatvector.space in the owner's built-in browser)

| Data | Route | Answer | Cache | Login |
|---|---|---|---|---|
| Who holds each system | `GET /sovereignty/systems?compatibility_date=2026-05-19` (057 already reads it: `IT_SOV_URL`, `itSovRead`) | 5,485 systems: 2,705 held by one of 77 alliances, 2,666 by an NPC faction (21 factions), 114 unclaimed. An alliance claim carries `alliance_id`, `corporation_id`, `claimed_since`, `is_capital_system`, `development` (military, industrial and strategic levels plus `activity_defense_multiplier`), and `sovereignty_hub` with its `vulnerability_window` (start, end). No J-space. About 1.28 MB of JSON before compression. | `max-age=300`, `Expires` 5 min | none; rate group `sovereignty`, 600 per 15 min |
| Jumps in the past hour | `GET /universe/system_jumps/` | `{system_id, ship_jumps}` for 4,929 of the map's 5,268 systems (absent = 0); median 14, 90th percentile 114, max 2,708 | `Last-Modified` → `Expires` exactly 1 h | none |
| Kills in the past hour | `GET /universe/system_kills/` | `{system_id, ship_kills, pod_kills, npc_kills}` for 2,817 systems (absent = 0). Ship + pod kills in 466 systems (median 2, max 102); NPC kills in 2,707 (median 74, max 2,440) | 1 h, as above | none |
| Regions | none: the page's own `INTEL_MAP.reg` / `regions` (68 k-space regions) | | | |

Also seen: `/sovereignty/map` (`system_id` + `faction_id` / `alliance_id`, 8,490 rows incl. J-space, 1 h cache): not needed, since `/sovereignty/systems` has more.

## 2. What exists (main f70fdd5; find by name)

- **058's filter column** (`IT_MAP_FILTERS`, ~31013): Colour (one or none: `sec`, `jumps`, `region`), Only (stacked: `secr`, `near`, `reports`, `kills`, `wh`, `sov`), View (`paths`). State in `tvMapStack` (`itMapStackBlank`, `itMapStackRead`: known fields only). Matching in `itMapMatch`, one pass per key change (LESSON #120). Colour in `itMapColRaw` (Region's neighbour-distinct palette `itMapRegCol`). Legend `itMapLegend`. Settings panels per filter (`IT_MAP_PANEL_BTN`, the hover button 057 made show on or off).
- **057's sovereignty read** (`itSovRead` ~27484): one GET through `esiFetch` (kind `sov`), kept in memory, at most once per `Expires`, retries after 60 s, 120 s, then 5 min. It runs only while bridges need it (`itSovWanted`). It keeps only `alliance_id` and the capital, and drops the rest.
- **The Lookup budgets gauge** counts ESI calls by kind (off-limits text, unchanged).

## 3. What changes

**L1. One live-data reader for the three routes** (README "Reuse before adding"). `itSovRead` is generalised into one reader per kind: `sov`, `jumps`, `kills`.
- It reads only while something needs it: 057's bridges for `sov`, or the filter that uses the data being on while the map is shown.
- It reads at most once per `Expires`, retries as 057 does, and keeps data in memory only (as 057's D2). No timer of its own: the map's redraws and `itSovNeed`-style calls ask.
- `sov` keeps per system: holder kind (alliance / faction / unclaimed), alliance and corp IDs, faction ID, capital, claimed since, development levels and ADM, vulnerability window. The bridge code reads the same store (one read serves both).
- A failed or missing read shows "no data yet" on the filter's legend line, and systems keep their plain grey: never "0".

**L2. Three new Colour options** (058's Colour group: one or none):
- **Sov holder** (Q1 answered: by standing first, a switch in its settings for one colour per alliance). **By standing** (the default): the holder's side from the page's own standings (`sideOf` with the holding corp and alliance, the same answer its pilots' chips get; `standKind` for the star of your own corp or alliance): your corp or alliance, friendly (`--side-friendly`), neutral, hostile (`--side-hostile`), then NPC-faction space in one muted colour and unclaimed plain. With no standings known (logged out, no typed lists) every alliance is neutral; the legend line says so. **Per alliance** (the switch): one colour per alliance from a neighbour-distinct palette like Region's (`itMapRegCol`'s method; reserved hues kept, 058 Q13). Hover (Q2 answered: both): holder name and ticker (org cache, asked once) with its logo, the corp, capital ★, held since, the development levels (military, industrial, strategic) and ADM, and the vulnerability window in EVE time.
- **Alliance logos on the map** ([stated] 2026-11-20 "can we incorporate the alliance's logo into this? like it is in game."; how the game places them: Q1b). The page already shows alliance logos from `images.evetech.net/alliances/{id}/logo` (pilot chips `itWhoHtml` ~29275, System Analyzer `sa-logo` ~24369), and the CSP's `img-src` allows that host. On the canvas they're drawn from plain `<img>` loads (`drawImage`), each logo loaded once and only for holders in view. That marks the live map's canvas as cross-origin, which nothing reads back. The one `toDataURL` (~30167) is the Intel example's own canvas, which keeps Security colouring, so it isn't affected; the build checks that the example never draws Sov holder. Where (Q1b): the owner sent a screenshot of the game's sovereignty view 2026-11-20 (reference only, not stored, per his 2026-11-12 rule). The game puts the holder's logo **inside each system's circle** when zoomed in, the circle ringed in the holder's colour, with the name and security beside it. So: **zoomed in, with Sov holder on, the holder's logo fills the system's circle** where Security and Jumps put their number today (058's zoomed-in circles). A second screenshot the same day, zoomed further in, shows the gate lines between two systems with the same holder drawn in that holder's colour, other lines plain: with Sov holder on, the map does the same (line colours worked out once per sov read, with the system colours). Zoomed out, colour only. The hover and a "holders in view" list in the legend carry the logo too. No logo over patches of held systems when zoomed out (Q1b answered: no, as in game). NPC-faction space: the faction's logo only if CCP's image server has one (UNVERIFIED), else no logo. A logo that hasn't loaded shows the ticker instead. Drawing cost: logos are drawn only for circles in view at the zoom where 058 draws numbers in circles; the logo per alliance is loaded once; colours and line colours are worked out once per sov read and settings change, never per draw (LESSON #120).
- **Jumps (past hour)**: a heat scale in steps sized to today's spread: 0 / 1–9 / 10–49 / 50–149 / 150–499 / 500+ (median 14). Zoomed in, the number in the circle as Jumps from you does. Hover: "N jumps in the past hour (ESI, as of HH:MM)".
- **Kills (past hour)** (Q3 answered: one filter): ship + pod kills by default: 0 / 1 / 2–4 / 5–19 / 20+ (median 2 among the 466 with any). NPC kills as the filter's own setting (two choices in its settings panel): 0 / 1–49 / 50–199 / 200–499 / 500+. The choice is kept in `tvMapStack` (a new field `killNpc`, safe both ways as `regions`). Hover: all three numbers.
- **Names beside today's filters:** 058 already has a Colour "Jumps" (jumps from you) and an Only "Kills" (kills Intel saw). The new ones are named "Jumps (past hour)" and "Kills (past hour)" in the column, with their own icons; the mockup shows them side by side for the owner to judge.
- The scales use colour tokens, kept clear of the reserved hues (058 Q13).

**L3. Region pick, a new Only filter:** "only systems in the regions you pick". Any pick counts, as with Sov kinds. Its settings panel is a list of the 68 regions with a box each, plus a search box (064's `sysSuggest` style, on region names) that narrows the list, "Clear", and a **Select all** box above the list ([stated] 2026-11-20 "can we add a checkbox to select all regions in the region picker?"): it ticks or unticks every region the list shows (all 68, or those a search leaves, then labelled "Select all shown"); some ticked shows a dash (indeterminate), which the page's checkbox style gains (it has no indeterminate look today) (Q5 answered: box per region + search; no right-click "Only this region" for now). The picks are kept in `tvMapStack` as a new field, `regions: [region names]`. Names rather than indices keep the field safe if CCP adds a region. An older page reading it ignores the field; an older page saving drops it (the user loses the picks only if the page is reverted). The build says so in the pull request, or keeps the picks under a key of their own if the owner prefers.

**L4. Activity as an Only filter:** "at least N jumps / kills in the past hour", as a range like Security range. Q4 answered: later, its own backlog item; not in this delivery.

**L5. Legend and match chip:** the second legend line (058 Q14) shows the active scale, plus "as of HH:MM" for the two hourly ones. The match chip counts Region pick like any Only filter.

**L6. The phone filter column** (BUG "the filter column on a phone is a jumble", dscan-backlog-7; Q6 answered: fixed in this delivery). With the four new buttons the column holds Colour 6 (Security, Jumps, Region, Sov holder, Jumps (past hour), Kills (past hour)), Only 7 (Security range, Within N jumps, Intel reports, Kills, Wormholes, Sov upgrades, Region pick) and View 1 (Paths to you). On a phone it's laid out by group (the build session's 058 suggestion): Colour with View under it (a line between) in one column, Only in a second, a line between the columns; each filter's settings button to the right of its filter in a narrow lane of its own, so nothing shifts when one shows. Group wrappers are `display:contents` on a wide map, so the desktop column is unchanged. The column's background made solid enough that map labels don't show through. The mockup shows it at 390 px.

## 4. UI rules it touches

- **Rule A** (map controls in the column, neutral look, 30 px / 44 px phone): four new buttons, each with its own icon (drawn in the mockup).
- **Colour tokens only:** the new scales as tokens; reserved hues kept (058 Q13).
- **Drawing cost** (LESSON #120): colours worked out once per data change (the key gains the reads' times), never per draw; no timers.
- **Phone:** 44 px; the column's jumble gets worse with four more (Q6).
- **One switch / one text field:** the region search reuses the page's text field.
- **The Intel example:** shows the live map's controls at rest (055), so its still filter column gains the four buttons (`intel_example_check` catches a miss). Its picture keeps Security colouring; markers and notes unchanged.

## 5. Info text it touches

- `intel` [Map] lists the filters: four new short entries, about 40 words. The panel is at 667 of 670 (part 4's raise is in 062); Q7 answered: raise the cap by about 40 (the build sets it from the final count, after 062's raise lands).
- The "Map: within" setting's hover (`mapReach.title`: "systems farther out are drawn faint") gains "(not with Sov holder, Jumps or Kills in the past hour)" or is reworded to match (Q10).
- The "Lookup budgets" gauge is off-limits and unchanged; it simply counts the new reads.

## 6. DLA and requests

- **2.5 (reasonable use):** each dataset is read at most once per its `Expires` (5 min for sov, 1 h for jumps and kills), only while a filter or the bridges need it, through `esiFetch` and its error limit. That's at most about 14 sov reads an hour while Sov holder is on, against a group limit of 600 per 15 minutes.
- **2.2 (CCP may remove data):** each filter degrades to "no data" and grey, never wrong colours.
- **2.3(c):** the data is public and aggregate (who holds space, traffic counts); nothing about a player is tracked or kept. Nothing is stored beyond memory.

## 7. Questions for the owner

1. **Sov holder colours:** one colour per alliance, like Region (neighbours differ; the 77 alliances can't all be told apart without the hover); or by your standings (yours, blue, red, neutral, NPC faction, unclaimed: the page's standing colours); or per alliance with a "by standing" switch in its settings. Recommended: the switch, default by standing. **ANSWERED** [stated] "Switch, default standing (Recommended)".
1b. **Alliance logos, "like it is in game":** from his screenshot, the logo inside each held system's circle when zoomed in, plus hover and legend (L2). Gate lines between two systems of the same holder in its colour, as the game does (recommended yes). Also one logo over each patch of held systems when zoomed out (the game doesn't; recommended no). **ANSWERED** [stated] "No (Recommended)".
2. **What the sov hover shows:** holder and ticker, capital and held since (always). Recommended: also the development levels and ADM, and the vulnerability window (both in the data already). **ANSWERED** [stated] "Show both (Recommended)".
3. **Kills (past hour):** one filter with Ships + pods (default) or NPC kills as its setting (recommended), or two filters. **ANSWERED** [stated] "One filter, NPC as setting (Recommended)".
4. **"At least N" activity filters** (Only, like Security range) for jumps and kills: recommended later, as its own item. **ANSWERED** [stated] "Later, own item (Recommended)".
5. **Region pick's panel:** a box per region with a search (recommended), or a search with chips only. Also a right-click "Only this region" on a system: recommended not now. **ANSWERED** [stated] "Box per region + search (Recommended)".
6. **The phone column jumble:** fold its fix into this delivery, since this adds four buttons to that column (recommended), or keep it separate. **ANSWERED** [stated] "Fold the fix in (Recommended)".
7. **`intel` info cap:** raise it by about 40 words (recommended), or cut wording elsewhere.
8. **Mockup:** yes (recommended: four new buttons and icons, three scales, a settings panel, the phone column).

Q7 and Q8 ANSWERED together: [stated] "Raise cap ~40, mockup yes (Recommended)".

## 8. Mockup (2026-11-20)

`live_map_filters_mockup.html` (sent to the owner; scripts in `claude/roadmap/live-map-filters-mockup/`, README there; built on main f70fdd5; `test_lm.py` 117 checks pass at 1440 and 390 px; check_pii: names checked, only the page's CCP login button image). It shows everything in section 3 with made-up alliances, logos and live data. What it showed that the plan didn't settle:

- **Q9. Ring or disc behind the logo.** The game rings each held system's circle in the holder's colour. 058 dropped a coloured outline for the soft colour because on this map **a ring means a report** (058's README: "a red one as hostiles"). In the mockup a reported system held by an alliance shows both: the report's ring outside and the holder's ring inside (78-0R6, MSG-BZ zoomed in). MOCKUP box "Logo circle": Ring (as in game) or Disc (the logo on a disc of the holder's colour, no coloured ring). Recommended: Disc, to keep 058's rule; Ring if the in-game look matters more. **ANSWERED** [stated] "ring" (NOT the recommendation): the holder's ring as in game; a report's ring stays outside it (as the mockup draws), so both read.
- **Q10. The fade past "Map: within".** 058 draws systems past the map's reach faint (`IT_MAP_FAINT` 0.22) whenever no Only filter is on. With Sov holder, Jumps or Kills (past hour) that hides most of what the data is for (territory and busy systems across the galaxy): zoomed out, almost nothing past 10 jumps reads. Options: keep the fade (as Security and Region do today); or these three colours skip the reach fade (only Only filters dim; the gates still fade). Recommended: skip it for the three live-data colours. The owner asked [stated] "any issue with just removing the fade outside of the feed range?"; answered (the faint step is the only sign that reports and names stop past "Map: within"; two steps today, 45% past Near You and 22% past Map: within; the session then suggested dropping only the 22% step for every colour). **ANSWERED** [stated] "ok, go with your choice for now.", quoting this recommendation: **Sov holder, Jumps (past hour) and Kills (past hour) skip both distance fades** (every system at full strength unless an Only filter dims it); the gates still fade past the reach; Security, Jumps from you and Region keep today's fades. While one of the three is on, the legend leaves out "faded: past Near You" and "faint: past Map: within". "For now": dropping the outer step for every colour stays open for later.
- **Soft colour a bit brighter** ([stated] 2026-11-20 "i know we went to softer colors, can we turn it up just a bit though?"): 058's soft colour (Q15) keeps 55% of a colour zoomed out (`itMapFcol`) and 38% in a zoomed-in disc (`itMapDraw`). The mockup tries 68% / 50% ("A bit up", its default) and 80% / 62% ("More") beside today's. It applies to every colour, so it changes Security, Jumps and Region too; matches and your system keep the full colour. Q11: which step (recommended: A bit up). **ANSWERED** [stated] "let's go with the "More" option on the colors." (80% / 62%; NOT the recommendation).
- Also seen, no question: the desktop column is now 16 rows with the two lines (fits a 661 px map in one column; a shorter map wraps to a second column, as 052 designed); the legend's colour line for Sov holder by standing is cut with "…" on a phone (its hover has it all, as 058's lines); the "In view" list is a third legend line.

### Reuse, don't add (README "Reuse before adding")

| Need | Reused | New (why) |
|---|---|---|
| Settings panels | 058's `itMp` (one at a time, placement, close, Escape); `IT_MAP_PANEL_BTN` + `IT_MAP_SET_ICON` | a body per filter in `itMpBodyHtml`; `itMapPanel`'s room per filter (Region pick's list is taller) |
| Region list rows, radios, Select all | 053's `.it-sov-k` / `.it-sov-n` / `.it-sov-from`; the page's checkbox style | an indeterminate (dash) look in the page's one checkbox rule |
| Region search | the page's text field | none (the search narrows rows; 064's dashless compare) |
| Per-alliance colours | `IT_MAP_REGION` and `itMapRegCol`'s greedy method | `itMapRegCol` generalised to any grouping (regions, alliances) instead of a copy |
| By standing | `sideOf` / `standKind`, `--side-friendly` / `--side-hostile` | a muted NPC-faction colour token |
| Logos | the logo URL `itWhoHtml` / `sa-logo` use | one in-memory logo cache (`Image` per alliance in view) |
| Legend | `itMapSwHtml`, 058's lines | the "In view" line |
| Phone column | 058's column and `itMapFlRows` | group wrappers (`display:contents` on a wide map); `itMapFlRows` counts filters and lines, not wrappers |
| Live data | 057's `itSovRead` | generalised to one reader per kind (L1), not three |

## 9. Checks (for the build)

- The reader: one GET per kind per `Expires`, none while not needed, the retry steps, the memory-only store; with stand-in ESI answers (made-up data), never live in checks.
- Colours: each scale's steps; absent = 0 for jumps and kills; faction / unclaimed / alliance for sov; "no data" before a read is grey, not 0.
- Region pick: Select all ticks every region shown (with a search, only those), unticks them, shows a dash when some are picked; any pick matches; stacked with Security range etc.; the field kept across reloads; an unknown region name dropped.
- Mutants: a missing system read as "no data" instead of 0; a reader that reads every draw; Region pick ignoring the stack.
- The Intel example's still column has the four new buttons (`intel_example_check`).
- Sov holder: by standing uses `sideOf` (a made-up friendly / hostile alliance in the stand-in lists); per alliance keeps neighbours apart; gate lines in the holder's colour only when both ends share a holder; logos only zoomed in; a logo not loaded shows the ticker.
- Q10: with Sov holder, Jumps (past hour) or Kills (past hour) on, a system past "Map: within" draws at full strength and the legend has no faded/faint entries; with Security it is faint as today + a mutant (the fade skipped for every colour).
- Phone column (390 px): Colour + View in one column, Only in the other, no overlap, nothing moves when a settings button shows (058's intel_map_stack_check phone part) + a mutant.

## Build review 2026-11-22 (build session, main 39dc6d3, v2026.11.21.3 + the secT data, PR #77)

What changed since the plan: 066 put the `intel` panel at exactly its cap (675 of 675; 062 had raised it to 675), so 065's ~40 words raise it again (Q7's answer covers it; set from the final count). 066 renamed the Only "Kills" to "Kills from Intel", so "Kills (past hour)" sits beside a name that already says where its kills come from. 057's reader runs only while Intel runs (`itSovWanted` needs `it.on`); the generalised reader asks while its filter is on and the map is shown (`itMapVisible`), and for the bridges as today. The served copy is 647,548 of 800,000 bytes.

The owner's answers at the review:
- **The sov field names** ([stated] "Fetch it once (Recommended)"): ESI's `/sovereignty/systems` and its OpenAPI description are refused to this session's fetch by ESI's robots rules, so the names come from a client generated from ESI's spec (a secondary source, in Sources below). They agree with what 057's code reads from the live answer (`solar_systems`, `claim.alliance.alliance_id`, `is_capital_system`). The code reads every field defensively (a field missing or of another type is left out of the hover, never an error), and the hand test checks the hover against the game.
- **The Lookup budgets panel** ([stated] "One: System activity (Recommended)"): jumps and kills are one new ESI kind, `activity` ("System activity"), in `ESI_KINDS`; sov stays `sov` ("Sovereignty"). The gauge's own text is unchanged.
- **The phone column** ([stated] "Yes, build the wrap now (Recommended)"): the Only group wraps into a second column when it is taller than the map's room, so 068 and 069 add their buttons without a new layout.
- **The three "with the next delivery" blocks** ([stated] "Extras first, separately (Recommended)"): 063's security fallback, the Wormholes menu's cut-off Remove question and removing every selected Wormholes system go as their own pull request (branch `065a-extras`) before 065. Their answers are in the 065 queue file.

## Built (build queue 065, v2026.11.23.1, branch `065-live-map-filters`)

As planned, with these choices made at the build (none changes what the owner picked):
- **One reader per kind:** 057's `itSovRead` now keeps every system's claim (`itSov.info`, `itSovClaim`: alliance, corporation, capital, held
  since, the three levels and ADM, the vulnerability window; every field read defensively, a missing one left out of the hover) beside the
  bridges' `sys` / `caps`; `itLvRead` reads the two hourly lists (`IT_LV_URL`, ESI kind `activity`). Both are asked from `itMapLvAsk`
  (itMapRefresh, a colour pressed, and a microtask after a draw so a map left open past an Expires asks again on its next draw), never on a
  timer; `check_request_gates.py` lists `itLvRead` and checks `IT_LV_URL`.
- **NPC faction space:** no logo is tried (the plan's UNVERIFIED faction logo row): it keeps today's disc and security number, the hover says
  "NPC faction space". A system missing from the sov answer says "no sovereignty listed".
- **Logos:** `images.evetech.net/alliances/{id}/logo?size=64` into a plain image per alliance, only once a circle needs it (zoomed in, the live
  map only); one that fails shows the ticker (the page's org cache). The legend's "In view" line and the hover use the 32 px logo in an `<img>`.
- **By standing:** `sideOf` on the holding alliance (`itSovSideOf`), redrawn when your standings change (`itSovSideKey`); with none set the
  legend adds "no standings set: every alliance neutral". Reading Sov holder by standing is a need for EVE's standings (`sideEveNeed`).
- **The column:** on a wide map a column too short for 16 rows wraps (as 052 designed); a 44 px gap between its columns keeps a filter's settings
  button off the next column's buttons (`intel_map_layout_check` now checks that instead of "right of the whole column"). On a phone the rows are
  44 px with no gap, so Colour and View fit beside Only on the 390 px map (447 px tall); each group wraps on its own when the map is shorter
  (`itMapFlSet`: Only's rows `--it-flr`, Colour's `--it-flc`).
- **Jumps (past hour)'s colours** (the owner at the hand test, 2026-11-22: "think we need to shift from greens and yellows to going from yellow to
  red. gray is none.", then "we dont need to match in-game brightness, but the contrast helps from yellow to red"): grey for none, then a dim
  yellow rising in brightness to a vivid red (`IT_MAP_JH`), so the busiest systems stand out most under the soft colour.
- **`itMapRegCol`** now uses a general greedy colouring (`itMapGreedy`), shared with per alliance; the regions' colours are unchanged.
- **Info text:** `intel` [Map] +41 words; its cap 716 (`check_subtext.py`). "Map: within"'s hover says the three live colours don't fade.
- **Checks:** new `live_map_filters_check.py` (20 mutants); `intel_check.py`'s ESI stand-in answers the two hourly lists (`LV`);
  `intel_map_stack_check`, `intel_map_look_check` and `intel_map_layout_check` follow the new column and soft colour.

## Sources

| Fact | Source | Checked | Status |
|---|---|---|---|
| `/sovereignty/systems` shape: `solar_systems[]` of `{solar_system_id, claim}`; `claim` has one of `alliance`, `faction` (`{faction_id}`) or `unclaimed` (boolean); `alliance` is `{alliance_id, corporation_id, claimed_since, is_capital_system, development, sovereignty_hub}`; `development` is `{military_level, industrial_level, strategic_level, activity_defense_multiplier}` (numbers); `sovereignty_hub` is `{id, vulnerability_window}`, the window `{start, end}` (strings), left out while the hub is in a campaign | secondary: the eve-esi-client-ts client generated from ESI's spec, https://raw.githubusercontent.com/steven-cmy/eve-esi-client-ts/HEAD/docs/SovereigntySystemsSolarsystemClaim.md (and SovereigntySystemsAlliance.md, SovereigntySystemsDevelopment.md, SovereigntySystemsFaction.md, SovereigntySystemsSovereigntyhub.md, SovereigntySystemsVulnerabilitywindow.md); backed by the page's own reader (`itSovRead`, built against the live answer 2026-11-16); ESI itself refused the fetch (robots) | 2026-11-22 | UNVERIFIED: the hand test hovers a held system and compares its levels, ADM and window with the game's sovereignty view |
| `/sovereignty/systems` fields (claim kinds, alliance fields incl. development and vulnerability window), counts, `max-age=300`, group `sovereignty` 600/15m, no login | live answer: `GET https://esi.evetech.net/sovereignty/systems?compatibility_date=2026-05-19` from threatvector.space in the owner's built-in browser | 2026-11-20 | verified |
| `/universe/system_jumps/`: `{system_id, ship_jumps}`, 4,929 rows, no J-space, 1 h between Last-Modified and Expires, no login | live answer: `GET https://esi.evetech.net/universe/system_jumps/?datasource=tranquility`, as above | 2026-11-20 | verified |
| `/universe/system_kills/`: `{system_id, ship_kills, pod_kills, npc_kills}`, 2,817 rows, no J-space, 1 h, no login | live answer: `GET https://esi.evetech.net/universe/system_kills/?datasource=tranquility`, as above | 2026-11-20 | verified |
| The numbers cover the past hour | live answer: Last-Modified to Expires is exactly 1 h on both (20:51:04 → 21:51:04, 20:40:45 → 21:40:45) | 2026-11-20 | UNVERIFIED: the window itself isn't stated by the answer; settle by comparing a quiet system's count with the in-game map's "jumps in the last hour" in the hand test |
| Alliance logos load from `https://images.evetech.net/alliances/{id}/logo?size=32` and the page's CSP allows them | the page's own code (`itWhoHtml`, `sa-logo`) and its CSP meta `img-src 'self' https://images.evetech.net data: blob:`, read live on threatvector.space | 2026-11-20 | verified |
| A system missing from the jumps / kills lists had 0 in that hour | live answer: no row with 0 appears (min 1) | 2026-11-20 | UNVERIFIED: the hand test looks at one missing system on the in-game map (expect 0) |
