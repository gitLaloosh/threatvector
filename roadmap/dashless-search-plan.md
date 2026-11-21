# Plan: system names found without their "-", in every system box on every tab

Status: BUILT 2026-11-21 as build queue 064, v2026.11.21.2 (branch 064-dashless-search; see "Built" at the end). Was READY 2026-11-20 (research session, main f70fdd5, v2026.11.20.1). All questions answered (section 6): [stated] "1. just the feed search box, 2. your recommendation, 3. no mockup." QUEUED as build queue 064 2026-11-20 ([stated] "yes"; claude/build-queue/064-dashless-search.md).
Backlog: "Severity TBD | Narrow — Intel map: system search finds names typed without "-"" (project memory, dscan-backlog-7). The owner: [stated] 2026-11-16 "system search in intel map should be searchable without "-" and still hit. test for any conflicts if done this way.", then [stated] "just put a note in the backlog item to test for the collisions.", then widened [stated] 2026-11-20 "(should be the case in all system searches for all tabs)".

## 1. The collision count (done first, as asked)

Run 2026-11-20 in the owner's built-in browser on threatvector.space (v2026.11.20.1), over the page's own name lists: the 5,268 k-space names `itLoadNames()` reads from ESI, plus the 2,604 J-space names in `INTEL_WH.names` (7,872 in all).
- **0 collisions.** No two systems have the same name once dashes are dropped (case ignored), k-space and J-space together. 3,304 k-space names have a dash; 1 J-space name does.
- **No dashless full name is the start of another.** For every dashed k-space name, its dashless form matches exactly one system by "starts with".
- **More hits for short queries, as expected:** "4c" finds 2 systems by starts-with today and 4 dashless; "cj6" finds 0 today and 1 dashless (C-J6MT). A query typed **with** its dash must keep today's results exactly: "m-" finds 30 today, and would find 236 if its dash were dropped too. So a query that has a "-" is matched as today (section 2).

The count can change when CCP adds systems, so the page keeps a guard (C1) rather than relying on today's 0.

## 2. The rule

- **A query with a "-" in it:** matched exactly as today.
- **A query without one:** compared with each name's dashless form, so "1dq1a" finds 1DQ1-A and "cj6" finds C-J6MT. Suggestions keep today's order: names that start with it, then names that contain it, at most 8.
- **Exact-name boxes** (type a name, press Enter) accept the dashless form. If two systems ever shared one, the box doesn't pick: it says the name matches several systems and lists them. That can't happen today (section 1).

## 3. Where (the inventory, main f70fdd5)

Every place a user types a system name:

| # | Box | Tab | Today | In this plan |
|---|---|---|---|---|
| 1 | Map search "Search systems" (`itRpSearchBind` ~33175) | Intel | starts-with, then contains, 8 | yes |
| 2 | Routes → "Avoid" box (`itRpBind` ~33245) | Intel settings | exact (`byLower`) | yes |
| 3 | Wormholes list → Add (`itWhAddFull` ~31985, `itWhAdd` ~32847) | Intel map | exact | yes |
| 4 | "word = system" shorthand list (`itAliases` ~27311) | Intel settings | exact, the system side | yes |
| 5 | System Analyzer ⚙ → Typed system (`saSetChange` ~33855, `saActSystem` ~33660; suggestions from the browser's `<datalist id="saSysList">`) | System Analyzer | exact; the datalist matches as the browser does | yes (Q2 for its suggestions) |
| 6 | Wormholes tab + Add and "Add a system here" (`whIdOf` ~33934: J-names from CCP's table, then k-space) | Wormholes | exact | yes |
| 7 | 062's Routes "To" field (queued, not built) | Wormholes | (new) | yes: whichever of 062 and this lands second uses the shared helper |
| 8 | Feed search box (`itSearchText` ~29696: one text of raw line, system names, regions, ships, pilots, groups) | Intel | substring of that text | **yes** (Q1): the text also carries each system's dashless name, and a query without a "-" matches it |
| 9 | Pasted lists: Sov upgrades (`sovParse` ~32593), jump bridges (`itBridgeNames` ~27341) | Intel settings | exact | **no** (Q1): unchanged |
| 10 | Chat lines (`itFindSystems` ~27667, `itShortSys` ~27690: "ymjg" = YMJG-4) | Intel's reader | exact words; the letters before a dash (4+) | **no** (Q1): unchanged |

## 4. What changes

**C1. One helper for every box** (README "Reuse before adding"):
- `itLoadNames()` also builds `flat`: a map from each dashless lower-case name to its system ID, with J-space names from `whTable()` added. A dashless form two systems share maps to a list instead (the guard); the check counts them.
- `sysFind(text)` gives exact boxes their ID, or a list when the name is shared. It matches as today when the text has a "-", and dashless when it hasn't.
- `sysSuggest(text, n)` gives suggestion lists their IDs: starts-with, then contains, `n` at most, dashless only when the text has no "-".
- Boxes 1–7 call these instead of their own `byLower.get` / loops. `whIdOf` keeps its J-name table first.
- Box 8, the Feed search (Q1 yes): `itSearchText` adds each system's dashless name beside its name, and a query with no "-" also matches it. A query with a "-" matches the text as today. Pasted lists and the chat reader are unchanged.

**C2. The System Analyzer's suggestions (Q2: the recommendation):** the typed box drops the browser's `<datalist id="saSysList">` and uses the map search's own suggestion list: `sysSuggest`, the `.it-rp-search` list's look, its keys (arrows, Enter, Escape), `role="combobox"` / `aria-expanded` as there. The list's builder is shared with the map search, not copied (README "Reuse before adding"); the build splits it out of `itRpSearchBind` so both call it.

**C3. The checks:**
- A page check with made-up names covering: a dashless query finds the dashed system; a query with its dash keeps today's results exactly; starts-with stays ahead of contains; two made-up systems sharing a dashless form list both and pick neither; each box 1–7 resolves "1dq1a"-style input.
- Mutants: dashes dropped from a query that had one; a shared dashless form picking the first system.
- A one-time count over the real list (section 1) goes into the PR; the guard covers later builds.

## 5. What it touches

- **UI rules it touches:** the text fields stay the page's one text field. Box 5 gets the map search's list (its existing look, 44 px rows on a phone, keyboard as there; inside the System Analyzer's ⚙ panel it must not be cut off by the panel's edge: the build checks at 1440 and 390 px). Nothing new to draw. No mockup (owner's choice, Q3).
- **Info text it touches:** `intel` [Map] / route lines name the search box but not how it matches, so likely none. Searched `CARD_INFO` for "search", "type" and "system name" (main f70fdd5); the build re-checks against its diff. If a line is added, it's one sentence ("Names work with or without their dash").
- **The Intel example:** the search box there is a still copy (055), unaffected.
- **Stored browser data:** none (names stay cached under `sysnames:<md5>`; `flat` is built in memory).
- **Lookups and drawing cost:** none. `flat` is built once per name load (7,872 entries).
- **DLA:** none. **Panel review:** not a fit (small; a page check settles it).

## 6. Questions for the owner (all answered 2026-11-20: [stated] "1. just the feed search box, 2. your recommendation, 3. no mockup.")

- **Q1. Beyond the boxes where you type a name** (1–7, all in): should these follow too?
  - (8) The Feed search box: recommended yes, for system names only (a dashless system name finds its reports).
  - (9) Pasted Sov and jump bridge lists: recommended no. They're copied from the game or other tools with their dashes.
  - (10) Intel's reading of chat lines: recommended no for now. A dashless word in intel ("cj6mt") becoming a system is a parser change with its own false-match risk, so it would be its own item.
  - **ANSWERED: "just the feed search box"** → (8) yes; (9) and (10) unchanged.
- **Q2. System Analyzer's typed box:** use the map search's own suggestion list so dashless typing gets suggestions (recommended), or keep the browser's list and only accept a dashless name on Enter. **ANSWERED: "your recommendation"** (C2).
- **Q3. Mockup:** none (recommended: no new look), or one for box 5's suggestion list if Q2 is yes. **ANSWERED: "no mockup".**

## 7. Hand test (for the pull request)

1. Intel map search: "1dq1a" lists 1DQ1-A; "cj6" lists C-J6MT; "m-" lists what it does today.
2. Routes → Avoid: "1dq1a" + Avoid adds 1DQ1-A.
3. Intel's Wormholes list → Add, the shorthand list ("home = 1dq1a"), the Wormholes tab's + Add: each takes a dashless name.
4. System Analyzer ⚙ → Typed: typing "1dq1" shows 1DQ1-A in the page's own list; arrows and Enter pick it; at 390 px the list isn't cut off.
5. Feed search: "1dq1a" shows the reports in 1DQ1-A.
6. A pasted Sov or jump bridge list without dashes is still refused as today (unchanged by choice).

## Built (build queue 064, v2026.11.21.2, 2026-11-21)

Reviewed against main e1ebe17 (v2026.11.21.1). Where the build differs from the plan:
- **A scope per box** (found at the review): the plan put J-space names into the one shared map, but only the Wormholes tab's boxes can take a J-space system. `sysFind(text, scope)` / `sysSuggest(text, n, scope, ok)` take `'k'` (systems with stargates: boxes 1–5) or `'all'` (J-space too: box 6 and 062's Routes pin, built by then). Otherwise a stargate-only box could resolve a J-space name, and a short query such as "j1" would fill the map search's 8 places with names the map then drops. The dashless maps are built lazily per name load (`sysFlatK`, keyed on `it.names`, so the Intel example's names work too) and per table (`sysFlatJ`), not inside `itLoadNames()`.
- **`whIdOf` stays exact:** it also turns the Local log's system names into IDs (`whSeen`), which aren't typed. The typed Wormholes boxes go through `whNameIn` / `whNameMiss` and the Routes pin's own `sysFind`.
- **The shared list** is `sysComboBind(inp, ul, o)` (split out of `itRpSearchBind`; options `data-sys-pick`, ids per box). The System Analyzer's list sits in the flow under its box (`.sa-sys-row`, `.sa-sys-search`), outside the radio's label, so a press on a row can't click the radio, and the ⚙ panel (which scrolls on a phone) never cuts it off. Its rows show the system and its region. The plan said the map's list had 44 px rows on a phone; it didn't, so both lists get them now (`.it-rp-sug li`, under 600 px).
- **The Feed search:** `itSearchText(e, flat)` adds the dashless names only for a query without a "-", so a query with one sees exactly the old text.
- **Also in this delivery, the three Intel bugs seen in J-space** (the owner, 2026-11-21, flagged for the delivery after 063): the filter column's fix became "no map, only its message": while your system isn't known the box is `nomap` and shows only its message (no filter column, canvas, search, zoom or rail) and Near You is hidden (`.it-top:has(.it-map-box.nomap) .it-nearcol`). The canvas's own `hidden` had never worked (LESSON #176): after a pilot switch into J-space the old map and its YOU pin stayed under the message. The status line names a J-space system through `whName`. `itNoSysJ()`: "You're in J… and where you came in isn't known (link it on the Wormholes tab)" in Intel's line, the map's message and the System Analyzer's "My location" (the owner: "With the Wormholes tab hint (Recommended)", "Yes, same wording (Recommended)").
- **Checks:** `tools/page_checks/dashless_search_check.py` (areas intel, system, layout): the helpers against the old map-search code for queries with a "-", made-up names for the shared form, every box, the System Analyzer's list at 1440 and 390 px, the J-space lines and the empty map at both widths; 15 mutants.
- Info text: checked; none. Stored browser data: none.

## Sources

| Fact | Source | Checked | Status |
|---|---|---|---|
| 0 dashless collisions among 5,268 k-space + 2,604 J-space names; 3,304 k-space names with a dash, 1 J-space | live answer: the page's `itLoadNames()` (names from ESI `POST /universe/names`) and `INTEL_WH.names`, counted in the owner's built-in browser on threatvector.space | 2026-11-20 | verified |
