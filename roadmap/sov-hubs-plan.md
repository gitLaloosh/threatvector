# Plan (BUILT, 068): the Intel map's "Sov hubs" Only filter (sov fights coming up, hubs vulnerable)

Status: **BUILT** as build queue 068, v2026.11.25.2, branch `068-sov-hubs` (the Built notes: section 11). DRAFT 2026-11-21 (research session, main e1ebe17, v2026.11.21.1). All questions answered 2026-11-21 (section 7); mockup sent (section 8). **QUEUED as build queue 068** 2026-11-21 ([stated] "yes"; `claude/build-queue/068-sov-hubs.md`). In build from 2026-11-25 (the build review's answers: section 10).
Planning list item E2 / 8 (`claude/roadmap/intel-planning-list.md`; research and answers: `claude/roadmap/intel-later-filters-research.md`, section E2). The owner: [stated] "structures of various types"; 2026-11-20 he picked all four kinds ("Sov fights coming up", "Sov hubs", "Structures you can dock at", "Your corp's own structures") with [stated] "Public only for now (Recommended)". So this plan covers the two public kinds; the two that need a new login permission stay in the backlog until he adds a permission. 2026-11-21: [stated] "ok plan it".

**Build after 065** (it needs 065's live-data reader and its `sov` store with each hub's vulnerability window), and after 066 and 067 if they're still waiting (same filter list, stack and `intel` info cap).

Panel review: not a fit (the facts are ESI's, checked live; the rest is the owner's call on the look).

## 1. What ESI gives (checked live 2026-11-21 from threatvector.space in the owner's built-in browser)

- **Sov fights:** `GET /sovereignty/campaigns` (no login). 23 campaigns today, all `event_type` `ihub_defense`, in 23 systems across 10 constellations, defended by 7 alliances, starting 0.7 to 41.9 hours from now. Each has `campaign_id`, `solar_system_id`, `constellation_id` ("the constellation in which the campaign will take place"), `structure_id`, `start_time`, `defender_id`, `defender_score`, `attackers_score` (all 0.6 / 0.4 today, before any started). The spec's `event_type` list also has `tcu_defense`, `station_defense` ("Defense Events") and `station_freeport` (a "Freeport Event", which carries `participants` instead of a defender). Cache 5 seconds (the spec's `x-server-cache-ttl` 5; `Expires` 5 s after `Last-Modified`). Rate group `sovereignty`, 600 per 15 min, **shared with `/sovereignty/systems`**.
- **Sov hubs:** in `/sovereignty/systems` (057 reads it; 065 keeps the rest). Every one of the 2,706 alliance-held systems has a `sovereignty_hub` with an `id`. 2,683 have a `vulnerability_window` (`start`, `end`), 3 to 18 hours long (most 3–5 h). 376 were vulnerable at the time of the check. **The 23 hubs with no window are exactly the 23 under a campaign** (the same systems). Each campaign's `structure_id` is that system's hub `id`, and its `defender_id` is the holding alliance (23 of 23).

## 2. What exists (main e1ebe17; find by name)

- **058's Only filters** (`IT_MAP_FILTERS`, `IT_MAP_ONLY`: `secr`, `near`, `reports`, `kills`, `wh`, `sov`), each matched in `itMapMatch` once per key, their settings panels `itMp` (Security range, Within N jumps) or their own (Sov upgrades' `sovOpen`, Wormholes' list), the Only line (`itMapOnlyHtml`), the stack `tvMapStack`.
- **Sov upgrades** (053): "Sov upgrades" is the name taken. Its panel's rows look (`.it-sov-k`, `.it-sov-n`) is the look for kinds with a tick each.
- **057's sov read** (`itSovRead`, `IT_SOV_URL`): one GET, kept in memory, once per `Expires`, retries 60 s / 120 s / 5 min. It keeps only the holder and the capital. **065 (queued)** turns it into one reader per kind (`sov`, `jumps`, `kills`) and keeps each hub's vulnerability window; 065's Sov holder hover shows the window in EVE time.
- **The map's labels** (`itMapLabels` `put` / `tags`) and the hover (`itMapTip`-side lines such as `sovTipHtml`).
- **The org cache** (`getOrg`, `orgCache`) for alliance names and tickers; `itJbAlName` asks once per alliance.
- **EVE time** shown as `HH:MM` (`ssoOnClock`, `toISOString().slice(11, 16)`).
- The page has no k-space constellation names (only region names), so the hover says "this constellation" rather than a name.

## 3. What changes (proposed; the questions in section 7 can change it)

**H1. A fourth live kind in 065's reader: `camp`** (`/sovereignty/campaigns`). It reads only while the new filter is on and the map is shown, through `esiFetch` (kind `sov`, so the Lookup budgets gauge counts it with the sov reads), keeps the list in memory, retries as the others do. How often: Q5 (ESI's own cache is 5 s; the page sets its own floor). Fields kept: system, constellation, kind, start, defender, both scores (or the Freeport participants). Every 2 minutes while the filter is on (Q5 answered).

**H2. A new Only filter "Sov hubs"** (Q1), after Sov upgrades in the Only group, with its own icon. Two kinds, each with a tick, any ticked kind counts (as Sov upgrades' picks):
- **Fight coming up**: a campaign in that system starting within N hours, or already started (Q2).
- **Vulnerable**: its hub's vulnerability window open now, or opening within N hours (Q2).
- Settings panel in `itMp` (as Security range and Distance): one row per kind (tick, name, an hours stepper `RS`), the panel's match count. Kept in `tvMapStack` as `hub: {fight: true, fightH: 24, vuln: true, vulnH: 0}` (safe both ways, as 058's fields).
- **Time passing:** "within N hours" changes with the clock, not only with a read. The match is worked out again when a read lands and when the settings change (never per draw, LESSON #120), so it can be up to one read interval behind; the hover's times are worked out when it's shown.
- **The match's key** holds the settings, the read's time **and whether there is data** (found in the mockup: with the time alone, a "no data" match outlived the data's return).
- Switched on the first time, its settings open (as Security range's and Within N jumps'; `seen.hub`).

**H3. The hover** (with Sov hubs on): "Sov fight: hub defense, starts 19:45 EVE (in 4 h 06 min); defending <alliance> [TICKER], score 60 / 40; nodes anywhere in this constellation", or "under way since 19:45" once started. "Hub vulnerable 16:00–20:00 EVE (now, 1 h 20 min left)" or "(opens in 2 h 10 min)". A hub in a fight: "no vulnerability window (in a fight)". The other event kinds in words: "TCU defense", "station defense", "station freeport" (with the participants' alliances instead of a defender).

**H4. A tag beside matched systems** (Q3 answered): "SOV 19:45" beside a system with a fight coming up (the start in EVE time; "SOV now" once under way), only while the filter is on and Fight coming up is ticked, drawn with the map's other tags (`itMapLabels`): a reported system's tag joins its report label; others get name + tag where there's room. Vulnerable hubs get no tag (376 at once would crowd the map); their hover carries it. The text: Q7 answered, "SOV 19:45" (not "⚔"; see section 8).

**H5. The legend's second line** (058's Only line, Q14): "a sov fight within 24 h (23) or a hub vulnerable now (376) · ESI 15:39" (the counts across the map, for the ticked kinds; as the mockup). A failed or missing read: "no data yet", never "0"; nothing ticked: "no kind ticked".

**H6. Not in it:** structures you can dock at and your corp's structures (permissions, backlog); a fight mark drawn with the filter off (Q4 answered: not now); alerts or sounds for a fight starting; constellation shading.

## 4. UI rules it touches

- **Rule A** (map controls in the column, neutral look, 30 px / 44 px on a phone): one new button with its own icon. With 065 the phone column's Only group grows to 8; the mockup checks it at 390 px.
- **One stepper / one switch:** the hours use the page's `RS` stepper; the kinds' ticks the page's checkbox style.
- **Drawing cost** (LESSON #120): matched once per read and settings change; tags placed with the existing labels; no timers.
- **Colour tokens only:** Only filters dim the rest; the tag uses the label colour (no new colour).
- **Intel example:** its still filter column gains the button (`intel_example_check` catches a miss); markers and notes unchanged.

## 5. Info text it touches

- `intel` [Map]: the filter list gains "Sov hubs, fights coming up and vulnerable hubs (ESI)" (~10 words; the cap set by the build after 065–067).
- The new `RS` titles: "Sov fight: starting within N hours (0: started)" and "Vulnerable: now, or opening within N hours".

## 6. DLA and requests

- **2.5 (reasonable use):** one small read per interval (Q5) only while Sov hubs is on and the map is shown; at 2 minutes that's at most 7.5 reads per 15 min, beside 065's sov read (3 per 15 min), against the shared 600 per 15 min. Through `esiFetch` and its error limit.
- **2.2:** no data → "no data yet", nothing matched, never wrong times.
- **2.3(c):** public and about structures and alliances, not players; memory only.

## 7. Questions for the owner

1. **One filter or two:** one Only filter "Sov hubs" with two kinds (Fight coming up, Vulnerable) in its settings (recommended: one button, like Sov upgrades' picks), or two Only filters ("Sov fights", "Vulnerable hubs"). **ANSWERED** [stated] "One filter, two kinds (Recommended)".
2. **The time windows:** Fight coming up within 24 h by default (0–48; started fights always count), Vulnerable now by default (0 = now, up to 24 h ahead). Recommended as stated; or other defaults. **ANSWERED** [stated] "24 h fights, now for hubs (Recommended)".
3. **Tags on the map:** "⚔ 19:45" beside systems with a fight coming up while the filter is on (recommended), vulnerable hubs hover only; or tags for both; or no tags (hover only). **Q3 and Q4 ANSWERED together:** [stated] "Fight tags only, filter on (Recommended)".
4. **A fight mark with the filter off** (the ⚔ tag always drawn, like the ✕ kill counts, which means reading campaigns whenever the map is shown): recommended not now (the filter reads only while it's on).
5. **How often to read campaigns:** every 2 minutes while the filter is on (recommended: scores change during a fight, and ESI's cache is only 5 s), or every 5 minutes (as the sov read), or every minute. **Q5 and Q6 ANSWERED together:** [stated] "Every 2 min, raise cap (Recommended)".
6. **Info cap:** raise `intel`'s cap by ~10 words (recommended), or cut wording elsewhere.

7. **The tag's text** (from the mockup): the plan's "⚔ 19:45" relies on a crossed-swords character that isn't in every font; on a canvas without it, it fell back to a mark like the kill count's ✕ (the sandbox's Chrome). The mockup uses "SOV 19:45" (plain letters, the same look in every browser). Recommended: "SOV 19:45"; or "⚔ 19:45" (looks right where the font has it); or the filter's flag drawn as a small icon (more drawing code). **ANSWERED** [stated] ""SOV 19:45" (Recommended)".

## 8. Mockup (2026-11-21)

`sov_hubs_mockup.html` (sent to the owner; scripts `roadmap/sov-hubs-mockup/`, README there; built on main e1ebe17; `test_hb.py` 83 checks pass at 1440 and 390 px; check_pii: only the page's CCP login button image). Made-up fights around C-J6MT (one started, five coming, one past 24 h) and a window for every nullsec system. MOCKUP box: Defaults, Fights only, Fights 48 h, Vulnerable now, Vulnerable 4 h, Zoomed out, No data yet, Off. What it showed: the panel puts each kind's tick and stepper on one row on a computer; on a phone the stepper wraps under its tick and the panel scrolls (as the map's other panels do on a short map); the match-key point (H2); the tag's text (Q7, answered: "SOV 19:45"). Rebuilt for the archive 2026-11-25 on main b1b9714 (`Claude outputs/sov_hubs_mockup.html`; the README says what moved).

### Reuse, don't add

| Need | Reused | New (why) |
|---|---|---|
| The filter | 058's Only filters (`IT_MAP_FILTERS`, `IT_MAP_ONLY`, `IT_MAP_PANEL_BTN` with `IT_MAP_SET_ICON`) | the entry and its icon |
| Settings | 058's panel `itMp` (`itMpBodyHtml`, `itMpOpen`, `itMpChanged`, the count line) | a body for `hub`; `itMpOpen` lets `hub` in |
| Kinds' ticks | Sov upgrades' `.it-sov-k` rows, the page's checkbox | one row rule (tick + stepper side by side, wrapping) |
| Hours | `RS` / `rsHtml` with `show` / `read` | `RS.mapHubF`, `RS.mapHubV` |
| Saved | `tvMapStack` (`itMapStackBlank` / `Read`, `seen`) | `only.hub`, `hub`, `seen.hub` |
| Data | 065's live reader and its `sov` store (windows) | the `camp` kind |
| Tags | `itMapLabels` `put` and a report's label pieces | the tag piece |
| Hover | the map's hover lines (`itMapTip`) | the hub lines |
| Names | the org cache (`getOrg`) | none |

## 9. Checks (for the build)

- The `camp` reader: one GET per 2 minutes at most, only while Sov hubs is on and the map is shown, none otherwise; retries as 065's; memory only; stand-in answers in checks, never live.
- The match equals the rule worked out apart (any ticked kind; fights within their hours or started; windows open now or opening within their hours; a hub in a fight has none); your system kept; nothing ticked → nothing.
- The key: a settings change, a new read, and data going and coming back each work the match out again (the mockup's find) + a mutant (the key without the data flag).
- Hover: started, coming, vulnerable now, opening later, in a fight; the Freeport kind's participants in words.
- Tags: only fights in the window, only while on and ticked; "now" once started; a reported system's tag in its label.
- The Only line: the counts, "no data yet", "no kind ticked"; the stack (saved, bad hours, an older stack); first switch-on opens the settings.
- 390 px: the panel fits across and scrolls, ticks ≥ 24 px, no sideways scroll; the Intel example's still column has the button (`intel_example_check`).
- Mutants: started fights left out; the vulnerability window's end ignored (a closed window matches); tags drawn with the filter off.

## 10. Build review (2026-11-25, build session, main b1b9714, v2026.11.25.1)

Found at the review (the plan was written before 065 was built) and the owner's answers, 2026-11-25: [stated] "your recommendations are fine for all of those questions. while you're working on new icons, modify the wormhole filter button to use a wormhole icon too if you would."

- **B1. Reads with Intel stopped:** nothing on the page asks on a timer; the map asks from its redraws, which come every 10–30 s while Intel runs (the card's age refresh). With Intel stopped the map shows but nothing redraws it, so fights aren't read and tags and matches stay as they were until a press; the Only line's "ESI HH:MM" says how old the data is. Accepted (no clock of its own).
- **B2. Time passing:** fights are read whenever Sov hubs is on, whichever kind is ticked (the "in a fight, no window" line needs that list), and the match's key holds the minute, so windows opening and fights entering their hours rework within about a minute (one pass over the map at most once a minute, on the refreshes that happen).
- **B3. The icon:** the mockup's flag clashes with 065's Sov holder flag (the mockup predates 065): Sov hubs gets an icon of its own (a hub structure, drawn). And (the owner's addition) the Wormholes filter button gets a wormhole icon.
- **B4. The window once:** with Sov holder's colour on, its hover already has "vulnerable 16:00–20:00 EVE"; while Sov hubs is on, Sov hubs' line (with the countdown) replaces it.
- **B5. Not questions:** the sov read is wanted while Sov hubs is on (`itSovWanted`; the windows come from it); the `intel` info cap rises from 754 to the final count (Q6's answer); `intel_map_stack_check`'s hand-written defaults gain the new fields; the mockup is rebuilt on current main for the archive, its hooks moved where needed.

## 11. Built (v2026.11.25.2, 2026-11-25)

- **As planned:** the filter `hub` after Sov upgrades (`IT_MAP_FILTERS`, `IT_MAP_ONLY`, `IT_MAP_PANEL_BTN.hub`, `IT_MP_KEYS`); the reader `itCamp` / `itCampNeed` / `itCampRead` (`IT_CAMP_URL`, kind `sov`, `IT_CAMP_MS` 2 minutes, 065's retries), asked from `itMapLvAsk`; the match in `itMapMatch` (`itHubIx` once per read, `itHubFight`, `itHubVulnIn`, `itHubAt`); the settings (`itMpHubRowHtml`, `RS.mapHubF`, `RS.mapHubV`, the change handler's `data-it-mphk`); the hover (`itHubTipHtml`, `itHubFightHtml`, `itHubWhoHtml`); the tags (`itHubTags` in `itMapLabels`); the Only line (`itHubOnlyText`); `tvMapStack` `only.hub`, `hub`, `seen.hub` (`itMapStackBlank`, `itMapStackRead`, `itMapStKey`); the first switch-on opens the settings (`itMapFilterSet`).
- **Where it differs from the plan:**
  - B1-B4 above: no reads with Intel stopped; fights read whichever kind is ticked; `itHubKey` (settings, each list there or not, each read, the minute) in both `itMapMatch`'s key and `itMapKey`; the hub icon of its own drawing (LESSON #183); the window said once (`itMapLvTipHtml`'s line skipped while `itMapHubOn()`).
  - `itMapLvWant(k)` is true for `'sov'` and `'camp'` while Sov hubs is on (so `itSovWanted` follows), and `itMapLvAsk` asks for EVE's standings only when Sov holder's colour is on (Sov hubs alone needs none).
  - The Wormholes filter's icon is the game's wormhole shape `WH_SWIRL`, its definition moved before `IT_MAP_FILTERS` (the owner's addition).
  - The rows are the page's own `.it-mp-row` (a tick label and its stepper side by side, wrapping): no new CSS. Fight coming up's stepper shows hours (0 = started only, "under way" in the Only line); Vulnerable's shows "now" or "N h".
  - The hover also says "(ended)" for a window the read holds that has passed (the read's copy is up to 5 minutes old), "Hub windows: no data yet" before the sovereignty read, and the campaigns' own "no data yet" line with its reason.
  - A fight's tag also joins a wormhole-only label (its name added), and a fight system that is the focus keeps its tag.
  - The `intel` info cap: 765 (from 754), the final count.
- **Checks:** `tools/page_checks/sov_hubs_check.py` (new; at 1440 and 390 px; 12 mutants, each fails), a campaigns stand-in (`CAMP`) in `intel_check.py`; the filter lists in `intel_map_stack_check`, `live_map_filters_check`, `sov_upgrades_check`, `intel_map_look_check`, `paths_to_you_check`; `check_request_gates.py` lists `itCampRead` and `IT_CAMP_URL`.
- **Still to check by hand:** the Sources table's UNVERIFIED row (a fight under way stays listed).

## Sources

| Fact | Source | Checked | Status |
|---|---|---|---|
| `/sovereignty/campaigns`: no login; fields `campaign_id`, `solar_system_id`, `constellation_id`, `structure_id`, `start_time`, `defender_id`, `defender_score`, `attackers_score`, `participants`; `event_type` enum `tcu_defense`, `ihub_defense`, `station_defense`, `station_freeport`; group `sovereignty` 600/15m; cache 5 s | ESI's own spec, `https://esi.evetech.net/meta/openapi.json?compatibility_date=2026-11-19`, read live from threatvector.space in the owner's built-in browser, and a live answer of `GET https://esi.evetech.net/sovereignty/campaigns?compatibility_date=2026-11-19` (23 campaigns, all ihub_defense; Expires 5 s after Last-Modified) | 2026-11-21 | verified |
| Every alliance-held system has `sovereignty_hub.id`; `vulnerability_window` start/end on all but the hubs under a campaign (23 = the 23 campaign systems) | live answer of `GET https://esi.evetech.net/sovereignty/systems?compatibility_date=2026-05-19` beside the campaigns answer, from threatvector.space in the owner's built-in browser | 2026-11-21 | verified |
| A campaign's `structure_id` is its system's hub `id`; its `defender_id` is the holding alliance | live answers of `GET https://esi.evetech.net/sovereignty/campaigns?compatibility_date=2026-11-19` and `GET https://esi.evetech.net/sovereignty/systems?compatibility_date=2026-05-19` from threatvector.space in the owner's built-in browser (23 of 23) | 2026-11-21 | verified |
| A campaign stays in the list while its fight is under way (start time past) | none: every campaign today starts in the future | 2026-11-21 | UNVERIFIED: the hand test looks at the list while a fight is under way (expect it listed, start time past) |
| Command nodes spawn in the campaign's constellation | ESI's own spec, `https://esi.evetech.net/meta/openapi.json?compatibility_date=2026-11-19`: `constellation_id` is "the constellation in which the campaign will take place" | 2026-11-21 | verified (as worded by ESI) |
