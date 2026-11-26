# Plan (BUILT, build queue 069): the Intel map's "Activity (past hour)" Only filter

**BUILT** 2026-11-26: v2026.11.26.1, branch `069-activity-filter` (see "Built" at the end).

Status: READY 2026-11-21 (research session, main 991dd4a, v2026.11.21.2). All questions answered 2026-11-21 (section 7); mockup sent (section 8). **QUEUED as build queue 069** 2026-11-21 ([stated] "yes"; `claude/build-queue/069-activity-filter.md`).
Planning list group E, E4 (`claude/roadmap/intel-later-filters-research.md`, section E4; born as 065's Q4, [stated] "Later, own item (Recommended)"). Answered 2026-11-20: [stated] "One filter, kind + minimum (Recommended)": one Only filter "Activity (past hour)", a kind (jumps / ship + pod kills / NPC kills) and a minimum N in its settings, like Security range. 2026-11-21: [stated] "plan E4".

**Build after 065** (not built yet: this plan is written against 065's plan, `claude/roadmap/live-map-filters-plan.md` L1, and the build review checks it against 065's real code), and after 066–068 if they're still waiting (same filter list, stack and `intel` info cap; 068 also adds an Only filter).

Panel review: not a fit (a small filter on data 065 already reads).

## 1. What ESI gives (checked live 2026-11-21 from threatvector.space in the owner's built-in browser)

- `GET /universe/system_jumps/`: `{system_id, ship_jumps}` for 4,918 systems (none with 0; J-space has none). Median 16, 75th percentile 43, 90th 124, 99th 617, max 3,112. At least 10: 3,142 systems; 50: 1,121; 100: 599; 200: 289; 500: 69. `Expires` 1 h after `Last-Modified`.
- `GET /universe/system_kills/`: `{system_id, ship_kills, pod_kills, npc_kills}` for 2,850 systems (none all-zero). Ship + pod kills in 493 systems: median 2, 90th percentile 9, max 211; at least 1: 493; 2: 300; 5: 111; 10: 47; 20: 22. NPC kills in 2,738: median 80, 90th 359, max 2,141; at least 50: 1,683; 100: 1,193; 200: 557; 500: 163. 1 h.
- 065 reads both (its L1 reader, kinds `jumps` and `kills`, memory only, once per `Expires`, only while something needs them); a system missing from a list counts as 0 (065's UNVERIFIED row, settled in 065's hand test).

## 2. What exists (main 991dd4a, plus 065's plan)

- **058's Only filters** (`IT_MAP_FILTERS`, `IT_MAP_ONLY`, matched in `itMapMatch` once per key), the settings panel `itMp` (Security range's: `itMpBodyHtml`, `RS` steppers), the Only line (`itMapOnlyHtml`), `tvMapStack`.
- **065 (queued):** the live reader (`jumps`, `kills`), the Colours "Jumps (past hour)" and "Kills (past hour)" (NPC kills as its setting `killNpc`), their hover lines ("N jumps in the past hour (ESI, as of HH:MM)"), the legend's "as of HH:MM", Region pick (an Only filter), the phone column by group.
- **068 (queued):** Sov hubs, an Only filter with kinds in its settings (ticks) and the match key holding whether data is there.
- The page's radio look (`.it-sov-k` radios, as in Distance's Jumps / Light years switch, 067).

## 3. What changes (proposed; section 7 can change it)

**A1. A new Only filter "Activity (past hour)"**, at the end of the Only group, its own icon. Only systems with at least N of the picked kind in the past hour.
- **Kind** (one at a time, radios): Jumps · Ship + pod kills · NPC kills.
- **Minimum** (`RS` stepper "At least [N]"), **one per kind, each kept** (switching kind brings back that kind's own minimum; Q1 answered). Defaults (Q1 answered): Jumps 50 (1,121 systems today), Ship + pod kills 1 (493), NPC kills 200 (557).
- **Steps** (Q2 answered): round numbers, 1 2 3 5 10 15 20 25 30 40 50 75 100 150 200 300 500 750 1000 1500 2000 (typed values snap to the nearest, as every `RS` does).
- Kept in `tvMapStack`: `act: {k: 'j' | 'sp' | 'npc', j: 50, sp: 1, npc: 200}` (safe both ways).
- It asks 065's reader for its kind's data while it's on and the map is shown (065's "only while needed" gains this filter). Data missing (not read yet, failed): nothing but your system matches, the Only line says "no data yet"; J-space systems never match (ESI has no data there).
- The match's key holds the settings, the read's time and whether there's data (068's lesson).

**A2. The Only line:** "at least 50 jumps in the past hour (1,121) · ESI 20:51". **The hover** (with the filter on): "N jumps in the past hour" for the picked kind (065's hover line when its Colour is on already says it; the filter adds it when that Colour is off, never twice).

**A3. Numbers on the map** (Q3 answered): none of its own. The circles' numbers come from 065's Colours (Jumps / Kills (past hour)), which can be on beside this filter (Colour + Only).

**A4. Not in it:** a maximum ("quiet systems": at most N), several kinds at once, alerts.

## 4. UI rules it touches

- **Rule A** (map controls in the column, 30 px / 44 px phone): one button with its own icon. With 065's Region pick, 068's Sov hubs and this, the Only group is 9. **Phone (found in the mockup):** today's phone grid holds all 16 buttons at 390 px without overlap (checked with two stand-ins), but 065's planned layout puts the Only group in a column of its own: 9 × 46 px ≈ 414 px, more than a phone map's room under the search box. 065's layout must let the Only group wrap to a second column, or this item's build adds that; the build review checks it against 065 as built.
- **One stepper / one switch:** `RS`; the kind as radios in the page's look.
- **Drawing cost:** matched once per key; no timers.
- **Intel example:** its still column gains the button (`intel_example_check`).

## 5. Info text it touches

- `intel` [Map]: "Activity (past hour), at least N jumps or kills (ESI)" (~9 words; cap set by the build after 065–068).
- `RS` title: "Activity: at least this many in the past hour (ESI's hourly counts)".

## 6. DLA and requests

- **2.5:** no new request: the two hourly reads 065 already makes, once per hour each, only while needed.
- **2.3(c):** aggregate public counts, nothing about a player; memory only.

## 7. Questions for the owner

1. **Minimums:** one per kind, each kept (recommended: switching from Jumps 50 to NPC kills brings back NPC's own 200), or one number shared by all kinds. Defaults Jumps 50, Ship + pod 1, NPC 200 (recommended, from today's spread), or others. **ANSWERED** [stated] "Per kind, those defaults (Recommended)".
2. **Steps:** round numbers 1–2000 (recommended: jumps reach 3,000 and kills stay small; one stepper covers both), or every number 1–100 then by 50s. **ANSWERED** [stated] "Round numbers 1–2000 (Recommended)".
3. **Numbers on the map:** none of its own; turn on Jumps / Kills (past hour) as the Colour to see them (recommended), or tag each matched system with its count (more labels). **ANSWERED** [stated] "No, use 065's colours (Recommended)".
4. **Mockup:** yes (a button, a panel with radios and a stepper, the phone column at 9 Only filters), or no (it's Security range's panel with a kind switch).
5. **Info cap:** raise `intel`'s cap by ~9 words (recommended), or cut wording elsewhere.

**Q4 and Q5 ANSWERED together:** [stated] "Mockup yes, raise cap (Recommended)".

## 8. Mockup (2026-11-21)

`activity_mockup.html` (sent to the owner; scripts `claude/roadmap/activity-mockup/`, README there; built on main 991dd4a; `test_ac.py` 70 checks pass at 1440 and 390 px; check_pii: only the page's CCP login button image). Made-up hourly counts for every k-space system, shaped like ESI's; two inert stand-in buttons for 065's Region pick and 068's Sov hubs so the column holds nine Only filters. MOCKUP box: Jumps ≥ 50, Jumps ≥ 500, Ship + pod ≥ 1, NPC ≥ 200, Zoomed out, No data yet, Off. Found: the phone column point (section 4).

### Reuse, don't add

| Need | Reused | New (why) |
|---|---|---|
| The filter | 058's Only filters (`IT_MAP_FILTERS`, `IT_MAP_ONLY`, `IT_MAP_PANEL_BTN` with `IT_MAP_SET_ICON`) | the entry and its icon |
| Settings | 058's panel `itMp` (`itMpBodyHtml`, `itMpOpen`, `itMpChanged`, the count line) | a body for `act`; `itMpOpen` lets `act` in |
| Kind | `.it-sov-k` radios (as 067's Distance switch) | one row rule (radios side by side, wrapping) |
| Minimum | `RS` / `rsHtml` with a steps list | `RS.mapAct` |
| Saved | `tvMapStack` (`itMapStackBlank` / `Read`, `seen`) | `only.act`, `act`, `seen.act` |
| Data | 065's reader (`jumps`, `kills`) and its hover lines | none |

## 9. Checks (for the build)

- The match equals the rule worked out apart for each kind (missing = 0; J-space never); your system kept; the per-kind minimums kept across kind switches and reloads.
- The key: settings, a new read, and data going and coming back each work the match out again + a mutant (the key without the data flag).
- No extra request: the filter on makes 065's reader read `jumps` or `kills` (only the picked kind's), once per `Expires`; off, no read for it.
- The hover once (not twice with 065's Colour on); the Only line; "no data yet".
- The stack: saved, a bad kind or an off-step number falls back, an older stack; first switch-on opens the settings.
- 390 px: the phone column with nine Only filters fits with nothing overlapping (section 4), the panel fits, 44 px; the Intel example's still column has the button.
- Mutants: `>` instead of `>=`; one shared minimum; a missing system read as "no data" instead of 0.

## Sources

| Fact | Source | Checked | Status |
|---|---|---|---|
| `/universe/system_jumps/`: `{system_id, ship_jumps}`, 4,918 rows, no zero rows, the spread above, 1 h between Last-Modified and Expires | live answer: `GET https://esi.evetech.net/universe/system_jumps/?datasource=tranquility` from threatvector.space in the owner's built-in browser | 2026-11-21 | verified |
| `/universe/system_kills/`: `{system_id, ship_kills, pod_kills, npc_kills}`, 2,850 rows, no all-zero rows, the spread above, 1 h | live answer: `GET https://esi.evetech.net/universe/system_kills/?datasource=tranquility`, as above | 2026-11-21 | verified |
| A system missing from either list had 0 in that hour | live answer: no row with 0 appears; repo `roadmap/live-map-filters-plan.md`, Sources, its row "A system missing from the jumps / kills lists had 0 in that hour": verified, the owner's hand test 2026-11-22 | 2026-11-21, settled at 065's hand test 2026-11-22 | verified |

## Built (2026-11-26, v2026.11.26.1, branch `069-activity-filter`)

Reviewed against main 52063c1 (v2026.11.25.2, after 065, 067, 068, 071 and 072); nothing to decide at the review (the owner: "yes").
- **As planned:** `IT_MAP_FILTERS` / `IT_MAP_ONLY` `act`, last in the Only group (after Region pick); `IT_ACT_STEPS`, `IT_ACT_KINDS`, `IT_ACT_DEF`;
  `itMapActOn`, `itActLv`, `itActCount`, `itActKey`, `itActIx`, `itActOnlyText`, `itActTipHtml`; `itMapLvWant` true for the picked kind's list
  only; `itMapFilterSet` opens the settings the first time (`seen.act`) and asks the reader; `itMpBodyHtml('act')` with 065's `itMpRadHtml`
  radios and `RS.mapAct`; `tvMapStack` `only.act`, `act`, `seen.act`; the key in both `itMapMatch` and `itMapKey`.
- **Where it differs:** the kind row reuses `.it-mp-row` (it already wraps), so no new CSS (the mockup's `.mk-ak` and the plan's "one row
  rule"). Switching kind doesn't rebuild the panel's body: `rsPaint` already shows that kind's own number, so focus stays where it was.
  The Only line's ESI time is the counts' own (Last-Modified, as 065's hover says "as of"), not the read's.
- **Found:** a filter panel's count was written only when a setting changed, so a list read after the panel opened (065's, 068's) left it
  stale; `itMapDraw` now writes it after working out the match (live map only, only when its words change).
- **Info text:** `CARD_INFO.intel` [Map] "Activity: at least N jumps or kills in the past hour" (11 words); the cap 776, from the final count.
  METHODOLOGY.md: Activity (past hour). The Intel example's notes: unchanged.
- **Checks:** `tools/page_checks/activity_filter_check.py` (13 mutants: `>` for `>=`, one shared minimum, a missing system as no data, the
  key without the data flag, the reader not asked, both lists read, the hover twice, ship + pod as ships only, the settings not opened, a
  bad kind and an off-step number kept, the stepper showing the jumps minimum, the panel's count not following a read); the hand-written
  filter lists in `intel_map_stack_check`, `live_map_filters_check` (rows 18), `sov_upgrades_check`, `intel_map_look_check` (16 phone
  buttons), `paths_to_you_check`.
- **The mockup** is archived as built on 991dd4a (`Claude outputs/activity_mockup.html`, scripts `roadmap/activity-mockup/`): its stand-ins
  for Region pick and Sov hubs are the real filters now.
