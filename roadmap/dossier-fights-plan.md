# Pilot Dossier read by fights, not by its newest 50 kills: build plan (research, 2026-11-14)

> **BUILT as v2026.11.15.1** (build queue 049; see "Built" at the end). **QUEUED as 049** (2026-11-14, the owner: "Yes, queue it"; `claude/build-queue/049-dossier-fights.md`). All questions answered. Updated 2026-11-14 for killmails with thousands of attackers (section 4.7). Written by the research session from `main` b5f0597 (v2026.11.13.3). Line numbers are approximate; find things by name. Mockup: `Claude outputs/dossier_fights_mockup.html` (scripts: Project doc folder `claude/roadmap/dossier-fights-mockup/`). **Build review 2026-11-15 (main 85e20cb): section 13 corrects 4.5 and adds the owner's answers; where it and an earlier section differ, section 13 wins.**

## 1. Why (the owner, 2026-11-14)

- [stated] "[a pilot] is in a large alliance that sometimes has very large battles during a war. that means their newest 50 kills and 30 losses could be accounted for in two or three hulls over a weekend or a week. so you get nothing useful about the pilot when they're out roaming with a small gang between large alliance fleets." (His screenshot: All 50, Solo 0, Small gang 0, Fleet 50; 47 kills in one battleship hull, "usually 261" pilots; six hulls with losses and "no kills".)
- [stated] "propose a solution with our lookup budgets in mind."
- Today (`pdLoad`, ~12930; `PD_KILLS = 50, PD_LOSSES = 30`, ~12619): 2 zKillboard requests (kills list, losses list), then up to 80 ESI killmail reads (`fetchKillmail`), so the dossier sees the newest 50 kills whatever they were. The System Analyzer's pilot rows read the same 50/30 (`saPilotData`, ~23635).

## 2. What we found

- **zKillboard's lists already carry the whole killmail.** Each item of `/api/kills/…` and `/api/losses/…` is the ESI killmail plus a `zkb` object (hash, values, `npc`, `solo`, `awox`, `labels`), up to 200 per request, newest first; `/page/N/` reads further back (sources: rows Z1–Z4). The page already uses this for one caller: `saHullFitsFrom` (~23909, build queue 014 D2, the owner: "Yes, use them"). Everywhere else, `fetchKillmail` reads every killmail again from ESI. So the 80 ESI reads per pilot today are repeats of data the page already holds.
- **One page is 200 kills, and it's already paid for.** The dossier asks for the first page and then uses 50 of its 200.
- **The browser's stored data has no limit today.** `dscanCacheGet` only ignores an expired entry; nothing deletes one (no `.delete(`, no cursor sweep, ~9990). The `zkb` store keeps every list ever read (each up to 200 full killmails), and `killmails` keeps every killmail ever read. When a browser runs short of space it deletes **all** of a site's data at once, not just part of it (row B1), so the page should keep its own size in check.

## 3. Decisions (the owner, 2026-11-14)

- **Fight rule:** "Fleet tab rule (Recommended)": two kills are one fight when they share 2 player attackers, or 1 when either had only 1–2 (`fkGroupKills`, ~25839). Then Q1: "Add within 3 hours (Recommended)", and the pilot himself is left out of the shared count (section 4.1).
- **Read depth:** "15 fights, 3 pages (Recommended)": stop at 15 fights, a year back, or 3 kill pages, whichever comes first.
- **Storage:** "Trim kills + 50 MB cap (Recommended)".
- **Mockup:** "Yes, mockup first (Recommended)".
- **Q2, DLA 2.3(c):** "Yes, go ahead": up to a year of a pilot's public kills, read and kept only in the user's browser.
- **Q3, loading:** "Page 1 first (Recommended)".
- **Q4, System Analyzer rows:** "All of page 1 (Recommended)".
- **Q5, size stop:** "Stop over 20 MB (Recommended)".
- **Q6, losses a year back too:** [stated] "yes, do it" (2026-11-14), after the live check below.

## 4. What to build

### 4.1 Fights
- `pdFights(kms, charId)` → `{of: Map(killmail_id → fight), count}`, from the killmails already read (no request).
- The rule is `fkGroupKills`'s, with two changes the mockup shows are needed:
  - **The pilot himself is left out** of the shared count. He is on every one of his own kills, so with him counted, every solo or duo kill links to every other.
  - **Within 3 hours** (Q1, decided): link two kills only when they are within 3 hours of each other (`PD_FIGHT_GAP_MS`). Without it, the same wingmates over a year chain into one "fight". In the mockup's made-up pilot, 18 Svipul kills over 11 months show as 1 fight and 477 battleship kills as 2, and reading goes on to the 3-page cap. With it: 12 Svipul kills, 5 fights; 117 battleship kills, 4 fights; 1 page read. (The mockup's "Fight rule" switch shows both.)
- **Big kills:** each kill keeps at most its 100 lowest player character ids for this (the trimmed form, 4.5). Two kills of the same big fleet share far more than 2 of those, so they still link; a kill of 100 or fewer keeps them all. Measured 2026-11-14 on 60 made-up kills of 2,000 attackers each, within an hour: 1 fight, 17 ms with 100 ids per kill (59 ms with all of them).
- Speed: count shared pilots only between kills within the time window (sort each pilot's kills by time and stop at the window), and skip pairs already in one fight. The mockup's 640 kills with fleets of 130–140 group in well under a second.

### 4.2 Pilot Analyzer: reading the kills
- Read zKillboard's kill pages newest first: page 1, then `/page/2/`, `/page/3/`, until any of these:
  - **15 fights** (`PD_FIGHTS = 15`) among the kills read;
  - the oldest kill on the page is **over a year old** (`PD_YEAR_MS`);
  - **3 pages** (`PD_PAGES = 3`, 600 kills);
  - a page of fewer than 200 (all their kills);
  - the page just read was **over 20 MB** of JSON (`PD_PAGE_BIG`, Q5; section 4.7).
- Keep the kills from the past year. Losses: **one page** (up to 200), as asked today, all of those **from the past year** used (not 30; Q6).
  - Why (live check 2026-11-14 in the owner's browser, the new logic injected into the live page, nothing saved): a real pilot with 100 losses in all had his whole loss history on page 1, back to 2017, so the heading read "Feb 16, 2017 – Nov 13" and hulls lost about 3,500 days ago (Tengu, Gila, Atron…) were listed. A busy pilot with a full page of 200 losses (all within nine months) was unchanged by the limit.
  - A hull lost only before that year and flown again shows "no loss of theirs" and its group's common fit, as any hull without a loss of theirs does today.
- Every request goes through `zkbFetch` (spacing, budget, pause, slow lists) with `who: 'Pilot Analyzer'`. **Page 1 first** (Q3, decided): draw the dossier from page 1 at once; if it needs more, read pages 2–3 after it, with "Reading older kills…" in the heading line meanwhile, and redraw once (keep the open row, the switch, the selected hull and the scroll of the kills box, as `pdRender` already does). A new pilot asked for meanwhile stops the reading (`pd.charId` check, as in `pdMore`).
- The kills list is kept in memory only today (`killStubCache`); keep it so. Each page also goes into the `zkb` store for an hour like other lists, but trimmed (4.5).
- `pd.read`, `pdKillsHtml`'s "in their newest N" and Show 10 more: the kills under a row now come from everything read; Show 10 more reads nothing new while the pages read hold more.

### 4.3 Use the killmail in zKillboard's list (no ESI read)
- `fetchKillmail(stub)`: when the item carries the killmail (`killmail_id`, `killmail_time`, `victim.ship_type_id`, an `attackers` array, and `zkb.hash`), return it as `{killmail_id, hash, km}` (km without `zkb`) and don't ask ESI. Otherwise read from ESI as today. Same test as `saHullFitsFrom`'s `whole()`, extended to attackers; move it into one shared helper.
- This covers the dossier, the System Analyzer rows, the Fleet tab's members' losses, Show 10 more and the Last kill line. A killmail asked for by id and hash alone (share links, Intel's R2Z2 picks) still reads ESI.
- ESI killmail reads per pilot: from up to 80 to 0. Names, types and systems are still looked up as today.

### 4.4 System Analyzer rows
- **All of page 1** (Q4, decided): up to 200 kills and 200 losses instead of 50/30, at no extra zKillboard request and no ESI killmail read. No extra pages here: a busy Local could take 20+ pilots × 3 pages.
- Their possible-ship rule (newest kill in that gang size) is unchanged; it simply sees more kills.

### 4.5 Stored data: trimmed kills, one cap
- **Trimmed kills** (one form for memory and storage, made as soon as a page arrives, so the full page can be dropped): `killmail_id`, `killmail_time`, `solar_system_id`; the victim's `character_id`, `corporation_id`, `alliance_id`, `ship_type_id`; **the pilot's own entry** (`ship_type_id`, `weapon_type_id`); **`n`**, the number of player attackers; **`hulls`**, the other players' hulls counted (`{type_id: count}`, for "flies with" and "With them"); **`ids`**, up to the 100 lowest player character ids (for fights, 4.1); and from `zkb` the hash and `totalValue`. The size no longer grows with the attackers (4.7). `pdKill`, the kills under a row and `saPilotData` read this form (a small adapter, so they read a full killmail the same way).
- **Trimmed losses:** the victim whole (its items are the fit), and of the attackers only the 20 the loss view shows (final blow first, then damage: `renderOtherAttackers`' own order and count) plus the total count. Today the loss view lists those 20 and the count; nothing else reads a loss's attackers.
- **Full killmails stay where they're needed:** the Fleet tab, share links, Intel and the victim card read the full killmail (`fetchKillmail` with a flag that refuses a trimmed copy; from ESI, kept as today under the numeric key).
- **Where:** trimmed copies go in the existing `killmails` store under a **string key** `l:<id>` (`{ts, data}` as today), so the older page, which reads numeric keys only, never sees one (revert-safe; README "Stored browser data"). No new store and no database version change (`DSCAN_CACHE_DB_VERSION` stays 2: a version bump would make the older page's `open(…, 2)` fail and run without its cache). Lists kept in `zkb` for the hour store their items trimmed the same way (kill lists as trimmed kills, loss lists as trimmed losses), including the System Analyzer's lists (`zkbCachedJson`), which today keep whole pages. **(Corrected at the build review: section 13, C1 and C2.)**
- **The cap: 50 MB** (`DSCAN_CACHE_CAP`) for the site's stored data (everything at threatvector.space is this page's, so the browser's figure for the site is the page's own):
  - once per page load, at idle (`requestIdleCallback`, else a few seconds after load), and after a dossier read: delete `zkb` entries past their hour, then, if `navigator.storage.estimate().usage` is over 50 MB, delete `killmails` entries oldest `ts` first until under 40 MB (the estimate is approximate, row B2, so a margin of 10 MB);
  - "used longest ago": `fetchKillmail` re-stamps an entry's `ts` when it's read, at most once a day per entry (no write on every read);
  - never touches `types`, `groups`, `orgs`, localStorage or the sounds database.
- Writes stay best-effort (`dscanCacheSet`): a full disk or a refused write is ignored, as today.
- **To measure in the build:** the page's storage usage after reading a pilot with big structure kills, and the trimmed sizes on real killmails (row B3). These numbers go in the pull request.

### 4.6 What the dossier shows (mockup)
- **Heading line:** "200 kills in 19 fights, 23 losses, Nov 19, 2025 – Nov 13". The year appears when the span crosses a new year (today's line drops it). Its hover: what was read and why it stopped ("Read from zKillboard until 15 fights, a year back or 3 pages of 200 kills, whichever came first: stopped at 15 fights. …").
- **Kills column:** the kill count as today, and under it "N fights" (small, dim) for the kills shown in that size. Its hover: "47 kills from 2 separate fights: kills sharing 2 of their wingmates (1 for a kill with only 1 or 2) within 3 hours of each other count as one fight". Nothing else changes: columns, switch counts (kills), order (037), the kills under a row, the footer.

### 4.7 Killmails with thousands of attackers (the owner, 2026-11-14)
- [stated] "some of these killmails could have a couple thousand pilots on a killmail for a structure."
- **A real one** (the owner's sample, a structure kill with 1,099 attackers, read from ESI in his built-in browser 2026-11-14, row B3): **196 KB** of JSON (about 178 bytes per attacker), **21 KB** compressed on the wire (gzip); the trimmed form above **1.8 KB** (0.8 KB compressed). Every attacker carried a character id; 141 had no `ship_type_id`; the victim (a structure) had no character and no items.
- **At 2,000 attackers** (a made-up killmail in ESI's shape, `/tmp/big.js` in the research session): about **374 KB** whole, **1.6 KB** trimmed. Trimming each attacker's fields instead (the first draft of this plan) would have kept about 240 KB, so the counts-and-ids form is the one that works.
- **A zKillboard page of 200 such kills is about 40 MB of JSON at 1,100 attackers each (about 4 MB on the wire), 75 MB at 2,000 (about 7–8 MB on the wire),** from the per-attacker size above; the wire size scales the sample's 9.5× compression (UNVERIFIED: the build measures a real big page). This already happens today: the dossier and the System Analyzer rows download page 1 whatever it holds, and the System Analyzer keeps the whole page in the `zkb` store for an hour. The plan makes it no worse for page 1 (trimmed on arrival, stored trimmed), but pages 2–3 could add two more such downloads.
- **Size stop** (Q5, decided: "Stop over 20 MB (Recommended)"): don't ask for page 2 or 3 when the page just read was over 20 MB of JSON (`PD_PAGE_BIG`; measured as the answer's text length before parsing), since a page that big is already one big fight's worth; the heading's hover says "stopped at a large page". At the owner's sample's size that's about 100 such kills on a page.
- Parsing such a page holds the full JSON in memory for a moment (`res.json()`); trim right after and keep only the trimmed form. Check the time to draw in the build (section 10).

## 5. Lookup budgets

| | zKillboard (100 per 10 min) | ESI killmail reads |
|---|---|---|
| Pilot Analyzer today | 2 (+1 for a common fit) | up to 80 |
| Pilot Analyzer, proposed | 2–4 (+1 for a common fit) | 0 |
| System Analyzer row today | 2 | up to 80 |
| System Analyzer row, proposed | 2 | 0 |

- The mockup's made-up pilot: 2 zKillboard requests and 0 ESI killmail reads (15 fights reached on page 1), against 2 and 73 today.
- Bigger answers: a page of 200 fleet kills is a large download (up to about 75 MB of JSON for 2,000-attacker structure kills, 4.7), and those are the slow lists (`claude/roadmap/zkb-slow-lists-plan.md`). The page already downloads these same pages today and then reads each killmail again from ESI, so the total download goes down.

## 6. UI rules it touches

- **Subtext:** the heading line stays one short line (`ctxHtml`); the details are in its hover and the ⓘ. `check_subtext` must pass.
- **New text in a cell:** "N fights" in `.pd-n` uses the existing dim colour token (`.pd-n span`), no new colour, no new control.
- **Phone (390 px):** checked in the mockup: the fights line sits under the count in the row's top right; no sideways scroll.
- **Drawing cost:** grouping runs once per read, not per redraw (keep `d.fightOf`); no timers.
- Intel example: not touched. No button inside a button; no new controls.
- No conflict found.

## 7. Info text it touches

- **`dossier`, first paragraph** (~3600), today: "What they fly, from their newest 50 kills and 30 losses on zKillboard: one row per hull, the one they used last first (in a gang size, by their newest kill in it). A row shows their own losses in it, or their alliance's (or corporation's) common fit, said as not theirs."
  - New (Q6 wording; the mockup has the earlier "(a year at most) and 200 losses"): "What they fly, from their zKillboard kills back to 15 fights and their losses, a year at most: one row per hull, last used first (in a gang size, by its newest kill there). A row shows their losses in it, or their alliance's (or corporation's) common fit, said as not theirs."
  - 52 words, the same as today: the `dossier` panel is at its cap (210 in all), so the new words replace old ones. `check_subtext` on a copy of the page with this line: 0 problems (2026-11-14). What a fight is goes in the "N fights" hover, not the panel.
- `dossier` "[The counts]" paragraph: "count those killmails" stays true.
- `pilots` "Possible ship": unchanged wording; the build re-reads it against the new numbers (Q4: all of page 1).
- Search `CARD_INFO` for "50 kills" / "30 losses" again in the build (the `side` panel's "last 50 kills" is a different feature and stays).

## 8. Questions (all answered 2026-11-14)

- **Q6. Losses a year back too** (asked after the live check, section 4.2): "yes, do it".

- **Q1. Fight rule over a year:** "Add within 3 hours (Recommended)".
- **Q2. DLA 2.3(c)** (`claude/reference/dla-planning-notes.md`): asked whether a dossier built from up to a year of a pilot's public kills, read and kept only in the user's browser (nothing on a server or shared), is within what he's comfortable with: "Yes, go ahead". (Not legal advice.)
- **Q3. Loading:** "Page 1 first (Recommended)".
- **Q4. System Analyzer rows:** "All of page 1 (Recommended)".
- **Q5. Size stop:** "Stop over 20 MB (Recommended)".

## 9. DLA

- **2.3(c):** the owner's answer to Q2 ("Yes, go ahead"). The data stays in the user's browser, with the 50 MB cap; nothing is sent or shared.
- **2.5 (reasonable use of CCP's servers):** ESI killmail reads go down (up to 80 per pilot → 0). No new ESI endpoint.
- No change to logins, tokens, money, branding or the footer.

## 10. Checks

- **New `tools/page_checks/dossier_fights_check.py`** (made-up data, stand-in zKillboard and ESI that count requests; never the real ones):
  - the mockup pilot: page 1 only, 15+ fights, 0 ESI killmail reads, Solo/Small gang filled;
  - a pilot whose 600 kills are all one fleet: stops at 3 pages; one with 130 kills: 1 page (fewer than 200);
  - a page whose oldest kill is over a year old: stops there; kills over a year old aren't counted;
  - losses: a loss page reaching back years keeps only the past year's (rows, heading span); a full page of recent losses is unchanged;
  - the fight rule: the pilot left out; 2 shared (1 for kills with 1–2 others); the 3-hour window;
  - a list item without attackers → read from ESI (fallback); a trimmed copy never used for a victim's fit;
  - page 1 first: the dossier is drawn before page 2 is asked for, then redrawn once; a new pilot meanwhile stops the reading;
  - System Analyzer rows: all of page 1 used, still 2 zKillboard requests per pilot;
  - big kills: a page of 200 kills with 2,000 attackers each: trimmed on arrival (each stored kill under 4 KB), fights still linked, the dossier drawn in under 2 s after the answer arrives, no page 2 when the page was over 20 MB, the loss view still lists its 20 attackers and the total;
  - mutants: whole killmails stored; all attackers' fields kept per attacker; pilot counted in shared pilots; no time window; 50/30 slices left in; ESI read despite a whole item.
- **Storage:** a stand-in IndexedDB over 50 MB → oldest-`ts` killmails deleted to under 40 MB; `types`/`groups`/`orgs` untouched; expired `zkb` entries deleted; the older page (b5f0597) opens the database and reads its own entries after the new page wrote trimmed ones.
- **Existing checks** that read 50/30 or the dossier: `dossier_check.py`, `dossier_pin_check.py`, `dossier_kills_check.py`, `sa_size_check.py`, `sa_mocks.py`, `system_analyzer_check.py`, `pilot_rows_check.py`, `fleet_fit_budget_check.py`, `check_request_gates.py`.
- The usual: `run_checks --auto` and `--served`, `check_subtext`, `check_ui_rules`, `csp_hash`, `check_pii` with the names list, the page size (served).

## 11. Hand test (owner)

(Branch and local-server commands come with the build session's reply.)
1. Pilot Analyzer, a pilot in a big alliance who has been in a war lately: the heading line says kills in N fights; Small gang and Solo have kills; the battle hull shows few fights for many kills.
2. Header gauge: zKill goes up by 2–4 for that pilot; ESI killmail reads stay near 0 (the gauge's breakdown).
3. Open a kill row's chevron, then a kill's fleet icon: the Fleet tab's victim card still shows the victim's fit (full killmail read).
4. Compare one list item with ESI for the same kill (DevTools): the attackers and victim match (row Z1).
5. A pilot who shot a big structure lately: the dossier still draws, and storage usage stays small after it (DevTools → Application → Storage).
6. DevTools → Application → Storage: usage after a few pilots; reload: the dossier comes from the hour's copy without new zKillboard requests.

## 12. Panel review

Doesn't fit: the owner made the main choices; the rest (zKillboard's answer, sizes, speed) is settled by code and measurement.

## 13. Build review (build session, 2026-11-15, main 85e20cb v2026.11.14.1)

Reviewed against main after 048 (the Wormholes tab): nothing it changed touches the dossier, `fetchKillmail`, the cache or the System Analyzer rows. `check_plan_sources`: 0 problems, 1 UNVERIFIED (B4, in the hand test). Z1–Z3 re-opened in zKillboard's code (`classes/Feed.php` `getJSON`, `public/api/api.json`), 2026-11-15: as written.

- **C1. Only a pilot's own lists are trimmed** (a gap in 4.5: "including the System Analyzer's lists (`zkbCachedJson`)"). Three System Analyzer features read every attacker of the killmails in their lists: `saEvidence` (group losses: which groups killed your side), `saSuggestions` (group kills: who shot alongside your side) and the system's kills and losses (`saActRead`). Trimmed to the pilot's own entry, or to a loss's 20 attackers, their counts would be wrong with no error. So: trimmed forms only for `/kills/characterID/…` and `/losses/characterID/…` (with or without `shipTypeID`), read by the dossier, the System Analyzer's pilot rows, the Last kill line, the loss view and the Fleet tab's members' fits. Group and system lists stay whole as today; `fetchKillmail` still uses a whole list item instead of an ESI read (4.3). A trimmed item carries a mark, so nothing takes it for a whole killmail (`saHullFitsFrom`'s `whole()` included).
- **C2. Trimmed lists in the `zkb` store under their own key** (`t:` + the list's address), so the older page, which reads the plain address, never gets a trimmed list (revert-safe). Trimmed copies per killmail under `l:<id>` (4.5 "Where") are left out: the lists hold them for the hour and are read again after it, so a second copy per kill would only add storage.
- **Q7. A pilot with nothing in the past year** (the year limit would leave his dossier empty; today he shows his newest 50 kills and 30 losses): the newest page is used as read, and the heading says nothing is from the past year. The owner, 2026-11-15: [stated] "your plan works".
- **Q8. The same year limit and fallback on the System Analyzer's rows** (4.4 didn't say): the owner, 2026-11-15: [stated] "your plan works".
- **Q9. Show 10 more after every page read is shown:** stops there and says every kill read is shown; no fourth page. The owner, 2026-11-15: [stated] "ok".
- **Q10. The probe bug riding with this delivery** (backlog dscan-backlog-6, "Intel: a probe dragged in from D-Scan is read as a pilot and a ship"): probes only for now (not bubbles, depots, cyno fields, wrecks). The owner, 2026-11-15: [stated] "probes only for now". Uses Intel's existing "probes" tag, so no mockup.
- Also in the build: the Last kill line's count of other attackers (NPCs included today) kept in the trimmed form as the total attackers.

## Built (build queue 049, v2026.11.15.1, 2026-11-15)

Built from section 13's corrections and answers. Where the build differs from sections 4-11:

- **Trimming and the store** (C1, C2): only a pilot's own lists are trimmed (`zkbPilotList`, read by the dossier, the System Analyzer's pilot rows through `saPilotData`, the Last kill line through `fetchKillsStubs` and the fits through `fetchLossesStubs`); kept in the `zkb` store under `t:` + the address; no per-killmail `l:<id>` copies. Trimmed items carry `tk` / `tl`. `fetchKillmail` returns a trimmed loss as the loss it is (never kept under its id), reads ESI for a trimmed kill, and uses a whole list item without ESI everywhere else (the group and system lists too).
- **The Last kill line** lists the newest kill's attackers, which a trimmed kill doesn't keep, so the first page's newest kill is also kept whole (in memory and in the `killmails` store, as an ESI read would). It counts every attacker, NPCs included, as before.
- **The loss view** (4.5's "the 20 the loss view shows"): nothing lists a loss's attackers; the 20 top attackers and the count are kept anyway, as planned.
- **Show 10 more** reads nothing; past the kills read it stops ("all N … read"); Try again reads from ESI only what zKillboard sent without its killmail (Q9).
- **The cap's deletion** runs at most once a page load (the browser's figure can lag behind a deletion); the size to delete is measured from the entries themselves.
- **Big pages:** a forced read of a 21.3 MB made-up page (70 kills of 2,000 attackers and 130 small kills) and its losses to the dossier drawn took about 3.1-3.3 s in `dossier_fights_check` on this machine, the stand-in's transfer included (section 10 asked for 2 s after the answer arrives; the answer's own transfer isn't separable there). Each stored kill under 4 KB (the largest about 1.2 KB).
- **The probe bug** (Q10): `INTEL_PROBES` (scanner, survey and interdiction probes; 11 names, from pyfa's SDE copy through `tools/gen_intel_tables.py`), matched in `itParse` before ships (`itProbesIn`), read as the probes tag; with or without the " I". Checked by `tools/page_checks/intel_probe_check.py`.
- **Also fixed:** `matchup_strip_check` (048's starting range moved to the optimal, so its 1.5 / 2.5 km step stayed inside the made-up threat's optimal and failed on main too); its step now goes into the falloff.
- Checks: `tools/page_checks/dossier_fights_check.py` (section 10's list, the cap and the older page; 7 mutants), the three dossier checks' wording. LESSON #166.

## Sources

| Fact | Source | Checked | Status |
|---|---|---|---|
| Z1. zKillboard's API list items are the ESI killmail plus a `zkb` object (npc, solo, awox, labels added) | `classes/Feed.php` `getJSON` (`Kills::getEsiKill($killID)`, then `$json['zkb'] = …`), https://github.com/zKillboard/zKillboard at 00e8cb30 (zKillboard's own code, not a secondary source) | 2026-11-14 | verified (code); live comparison in hand test step 4 |
| Z2. Up to 200 killmails per request, newest first | `public/api/api.json` ("return up to 200 killmails. Results are newest first and include the ESI killmail plus a zkb metadata object"); `classes/MongoFilter.php` line 11 (`min(200, …)`), zKillboard at 00e8cb30 (zKillboard's own code, not a secondary source) | 2026-11-14 | verified (code) |
| Z3. `/page/N/` path modifier, 1–100 | `public/api/api.json` form field `page` (`min` 1, `max` 100), zKillboard at 00e8cb30 (zKillboard's own code, not a secondary source) | 2026-11-14 | verified (code) |
| Z4. No date filter beyond 7 days (`pastSeconds` max 604800); `year` needs `month` | `public/api/api.json` fields `pastSeconds` (max 604800) and `year`/`month`, zKillboard at 00e8cb30 (zKillboard's own code, not a secondary source) | 2026-11-14 | verified (code) |
| Z5. Killmails under 5 minutes old are withheld from the API | `public/api/api.json` notes; `view/api.php` (`killmail_time … > time() - 300`), zKillboard at 00e8cb30 (zKillboard's own code, not a secondary source) | 2026-11-14 | verified (code) |
| Z6. API answers carry `Cache-Control: public, max-age=3600` | `view/api.php` line 73, zKillboard at 00e8cb30 (zKillboard's own code, not a secondary source) | 2026-11-14 | verified (code) |
| B1. A browser that evicts a site's best-effort data deletes all of it at once; writes over the quota fail with QuotaExceededError | https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria (MDN, documentation of the web standard) | 2026-11-14 | verified (documentation) |
| B2. `navigator.storage.estimate()` returns approximate `usage` and `quota` for the site | https://developer.mozilla.org/en-US/docs/Web/API/StorageManager/estimate (MDN) | 2026-11-14 | verified (documentation) |
| B3. A real structure killmail (the owner's sample, killmail 139700765): 1,099 attackers, 195,600 bytes of JSON, 20,564 gzip; trimmed form 1,835 bytes (848 gzip) | live answer: https://esi.evetech.net/killmails/139700765/ce43f787d7f02070bc4e386e8fa0d9f1dff2e2ce/ read in the owner's built-in browser, measured with JSON.stringify and CompressionStream | 2026-11-14 | verified (live answer) |
| B4. Size of a whole zKillboard page of such kills on the wire | UNVERIFIED: scaled from B3 (about 4 MB for 200 kills of 1,100 attackers); the build measures a real page for a pilot with structure kills (DevTools Network, transferred size) | — | UNVERIFIED |
