# Plan: J-space statics known the moment you enter a system

Status: **BUILT** as v2026.11.19.1 (build queue 061, branch 061-wh-statics; see "Built" below). Planned 2026-11-19 by a research session against main 513c1e6 (v2026.11.18.1). All of the owner's questions answered (Q1–Q8). **Queued as build queue 061** (`claude/build-queue/061-wh-statics.md`, 2026-11-19, the owner: "yes"). Research behind it: `claude/roadmap/wh-statics-research.md`. Mockup: `wh_statics_mockup.html` (scripts in `claude/roadmap/wh-statics-mockup/`).

The owner, 2026-11-19: "i need you to find a way for us to know what a j-space systems's statics are when the user enters one. i know what wanderer does it."

## 1. Decisions (the owner, 2026-11-19)
- **Q1 Source:** Wanderer's file, `priv/repo/data/wormholeSystems.json` (wanderer-industries/wanderer, MIT). To "whether Wanderer's file is the source": "yes".
- **Q2 Shown:** "similarly to the way they are in wanderer". Same functions, in this page's own style (his standing rule, 2026-11-12: other tools are reference for what a feature does, not for its look).
- **Q3 Updates:** "Check with game data (Recommended)": the scheduled game-data workflow compares Wanderer's file and opens a pull request when it changed.
- **Q4 Extras:** "Map box sorted by class (Recommended)", "Hover: mass and lifetime (Recommended)", "Statics first when typing a type (Recommended)". Not picked: statics in search results.
- **Q5 Mark:** "Small mark, yours replace (Recommended)".
- **Q6 Mockup:** "Yes, mockup (Recommended)". To the estimate of a few hours: "why would it take hours for the mockup? we're adding two values to the wormhole map." (It didn't.)
- **Q7 Info text cap:** "Raise the limit to 340 (Recommended)": the full sentence (section 6); `check_subtext.py` `INFO_ALL_MAX_BY_KEY['whmap']` 320 → 340, with his words in its comment.
- **Q8 Hover numbers:** "CCP's numbers (Recommended)": the hover shows CCP's SDE values; the build lists the 24 types where CCP and Wanderer differ (section 9) in the pull request so the owner can spot-check.

## 1b. Build review (2026-11-19, the build session, against main 77cf217)
The owner, to both recommendations below: "go with your recommendations". These replace the parts of D1, D7 and section 3 they name.
- **R1 Its own block, not a field of `INTEL_WH`.** `tools/jump_table_update.py` compares the whole `INTEL_WH` with its own rebuild (`same_wh = PW == NW`, line ~265 at 77cf217): a `stc` field in the page would make every twice-daily run report "wormhole table differs" and open a pull request that drops it. The statics also follow `INTEL_WH`'s system order, so a carried-over field would go wrong silently if CCP added or removed a wormhole system. So the statics are `INTEL_WH_STC`, in their own fenced block written only by `tools/gen_wh_statics.py`, carrying the fingerprint of the system list they follow (`sys`, the md5 of `INTEL_WH.sys`); the page uses them only while that matches (`whTable`), and `gen_wh_statics.py --check` fails when it doesn't. `jump_table_update.py` is unchanged.
- **R2 Statics in CCP's data: settled by the first run.** Neither CCP's static-data site nor ESI answers from the build sandbox, so the row "Statics aren't in CCP's SDE or ESI" can't be settled before building. The new workflow job writes the field names of one J-space record of CCP's `mapSolarSystems.jsonl` into its run summary; if they hold statics, the build session tells the owner.
- Checked at the review: Wanderer's 4d4a035 is still its newest commit (2026-11-15); the file has the same 2,604 IDs as `INTEL_WH` (5 Drifter names differ), 1–3 statics each, 43 codes, all in `IT_WH_TYPE`, no K162. At pyfa e5483f8 (the manifest's commit, which the build uses) CCP's numbers give the same 24 differing types as section 9; C247 960 / 2,000,000,000 / 375,000,000 / 0.

## 2. Scope
- **D1 The table.** New `tools/gen_wh_statics.py` reads Wanderer's file (a path, or the raw file at a pinned commit) and writes the statics into the page as one more field of `INTEL_WH` (`stc`: the 43 codes once, then one short entry per system in `INTEL_WH`'s own order) so it rides the table the page already decodes in `whTable()`. Checks before writing (the tool refuses on any failure): the same 2,604 solarSystemIDs as `INTEL_WH`, matched by ID never by name (Drifter names differ: CCP "Liberated Barbican", Wanderer "Barbican"); 1–3 statics each; every code in `IT_WH_TYPE`; never K162. Only statics are taken: Wanderer's effects disagree with CCP's SDE on J005926 and J010569, so class and effect stay CCP's. The pinned commit and the file's SHA-256 go in the page beside the field (`INTEL_WH.stcSrc`) and in the tool's output. About 650 bytes gzipped.
- **D2 Yours, else the list's.** `whStcOf(n)` returns `{codes, src}`: the system's typed statics (`st.sys[n].statics`, tvWhChain, unchanged) if any, else the list's (`src: 'list'`). Nothing from the list is ever written to tvWhChain, to Share/Export or to an import: they're CCP-style reference data, like class. Every reader of `.statics` for display goes through it: the map box (`whDraw`, ~34182), the System panel (`whSumHtml`, ~34289), and the live re-draw while typing (~34925).
- **D3 The mark.** Under the chips, the page's own dim note, as Class does today ("from CCP's data" / "changed by you"): "from the community list (Wanderer) · type your own to replace them" for the list's, "typed by you" for yours. The Statics field stays empty for the list's (its placeholder unchanged), so typing replaces; clearing it brings the list's back. The map box doesn't carry the mark (no room in 112 × 48 map units; the panel is where you look closer). See the mockup.
- **D4 Class order.** Chips and the map box list statics by where they lead, in CCP's class-number order (Wanderer's `sortWHClasses`): C1–C6, high, low, null, Thera, shattered, Drifter, Pochven. Typed statics are shown in that order too (stored as typed).
- **D5 Hover: lifetime and mass.** The chip's title (`whStcHtml`, today "C247 leads to C3 space") adds CCP's numbers: "· up to 16 h · 2,000,000 t in all · 375,000 t per jump" (+ "· regains N t" where non-zero). From a new generated table `IT_WH_LIFE {code: [minutes, total t, per jump t, regen t]}` written by `tools/gen_wh_table.py` from the same SDE reader that writes `IT_WH_TYPE` (attributes `wormholeMaxStableTime`, `wormholeMaxStableMass`, `wormholeMaxJumpMass`, `wormholeMassRegeneration`; see Sources). A phone has no hover: the title is the page's existing pattern for chips; no new tap behaviour. **CCP's numbers and Wanderer's disagree** (section 9, Q8): of the hole types in both (about 100), 24 differ in lifetime, total mass or mass per jump, 9 of them codes that are someone's static (C008, E004, E587, G008, L005, M001, Q003, V898, Z006 total mass or lifetime; e.g. E587: CCP 16 h, Wanderer 48 h, changed by Wanderer on 2025-09-12 "Change lifetime for E587 from 16 to 48"; Q003: CCP 3,000,000 t in all, Wanderer 1,000,000 t). CCP's unit record for `wormholeMaxStableTime` says seconds, but its values only make sense as minutes (C247 960 = 16 h, as every source gives). The mockup shows CCP's, as Q8 decided.
- **D6 Statics first when typing a type.** The connection editor's Type field (`whCnEditHtml`, ~34453) and + Add's "Type or class" field (~34020, when "Linked to" names a J-space system) get a native suggestion list (`<datalist>`, as the System Analyzer's `saSysList` ~33655): the system's statics first (labelled "static → C3"), then K162, then every other code. Typing anything is still allowed and checked as today. Intel's wormhole report box (~31799) is unchanged.
- **D7 Updates.** A new job in `.github/workflows/jump-table.yml` (twice a day, after the game-data job): fetch Wanderer's file from its default branch, run `gen_wh_statics.py --check`; if the statics differ from the page's, open a pull request on branch `wh-statics/<wanderer short sha>` (never to main), its body listing the systems that changed (old → new codes) and the commit. If the branch exists, nothing to do. A failed fetch or a failed check leaves the page as is and the job fails visibly. Changes in Wanderer's other fields (effects, names, wanderers) don't count.
- **D8 Credit.** NOTICE.md "Credits" gets Wanderer (MIT, the file and commit; its licence text kept in `tools/gen_wh_statics.py`'s header as MIT asks). The page's footer is unchanged.

## 3. Where to look (main 513c1e6)
- `INTEL_WH` (~26764) and `whTable()` (~33748): add `stc` decoding there (one pass, kept in the table object).
- `whStcHtml` / `whStcsHtml` / `whStcKind` (~33785–33790): title text (D5), order (D4).
- `whSumHtml` (~34282, Statics label ~34289): chips from `whStcOf`, the note (D3).
- `whDraw` (~34148, statics at ~34182): read `whStcOf(n).codes` instead of `sy.statics`.
- Typing handler (~34925): an empty field shows the list's again with its note.
- `whCnEditHtml` (~34450) and the + Add form (~34016): the datalist (D6).
- `tools/gen_wh_table.py`: `IT_WH_LIFE` (D5). `tools/jump_table_update.py` writes `INTEL_WH`: `gen_wh_statics.py` must run after it and keep `stc` when the table is rewritten (or `jump_table_update.py` carries the field over); a check guards that a jump-table pull request can't drop the statics.
- `CARD_INFO.whmap` (~3840): section 6.

## 4. Stored data
No new key and no change to any stored form: the list lives in the page, typed statics stay where they are (tvWhChain `sys[id].statics`). An older page reading tvWhChain sees only typed statics, as today; this page reading an older one's data works unchanged. Share/Export/Import unchanged (typed statics only; the recipient's page has the same list).

## 5. Checks
- `tools/gen_wh_statics.py --check` in `run_checks.py`: the page's `stc` decodes to exactly the pinned file's statics for all 2,604 systems; the IDs match `INTEL_WH`; every code is in `IT_WH_TYPE`; mutants: a dropped system, an unknown code, a K162, a swapped Drifter name (must still match by ID).
- A page check (beside `wormhole_tab_check.py`): a J-space system with nothing typed shows the list's chips and the list note, and tvWhChain still holds `statics: ''`; typing replaces and the note says "typed by you"; clearing brings the list's back; a system with typed statics shows only those; chips and the map box are in class order (a system whose list has a higher class first, e.g. one with "N062 C247" order reversed); a chip's title has the lifetime and both masses for a known code and none for K162; the connection editor's suggestion list starts with the system's statics then K162; Share output carries no list statics. Mutants for each.
- `jump_table_update.py` dry run on the built page keeps `stc` (a check fails if a rewrite would drop it).
- The usual: check_ui_rules, check_subtext (section 6), check_pii, served size (+~1 KB).

## 6. Info text it touches
- `CARD_INFO.whmap` "[Focus and adding]": "class, effect, statics, notes, connections, signatures" → "class, effect, statics (a community list's until you type your own; hover one for its lifetime and mass), notes, connections, signatures". +15 words: 317 → 332 of the new 340 cap (Q7).
- `IT_EX_NOTES`: none (the Intel example has no Wormholes tab).
- NOTICE.md: Wanderer in Credits (D8).

## 7. UI rules it touches
- **Subtext rule** (check_subtext): the note is one short line under the chips, like Class's "from CCP's data"; the rest is in the info panel.
- **Colour tokens only:** chips keep their destination colours (`whStcKind`); the note is the page's `.wh-note`.
- **No new controls:** a native datalist on existing fields; no new button, chevron or close button.
- **Phone / 44 px:** nothing new to tap; the mockup was checked at 390 px (no sideways scroll). Hover details aren't reachable by touch, as every chip title today.
- **Drawing cost (LESSON #120):** the map box reads statics while drawing, as today; no new timers or redraws.
- **800 KB served ceiling:** about +1 KB (statics ~650 bytes, `IT_WH_LIFE` under 1 KB raw).
- No conflict found.

## 8. Reuse, don't add
| Mockup piece | Page's own |
|---|---|
| the note under the chips (`.wh-stcsrc`) | `.wh-note` as Class's note; the mockup's one-line `display:block` can be dropped if `.wh-note` already sits on its own line there |
| suggestion list | native `<datalist>`, as `saSysList` |
| chip title | `whStcHtml`'s title |
| class order | one helper beside `whStcKind`, used by chips and `whDraw` |
| mockup bar (`#stcBar`) | mockup only, not built |
New on purpose: `whStcOf` (one place that decides yours vs the list's), `IT_WH_LIFE`, `INTEL_WH.stc`, `tools/gen_wh_statics.py`, the workflow job.

## 9. Where CCP and Wanderer differ (for the pull request, Q8)
CCP's SDE (pyfa b79cd90) vs Wanderer's `wormholes.json` (4d4a035); * = a static somewhere. The build re-runs the comparison against the data it builds from and lists the result in the pull request.
- Total mass: A009, C008*, E004*, G008*, J492, L005*, M001*, Q003*, Z006*; I078, L687, O546 (also lifetime).
- Mass per jump: B041, B520, C140, C248 (also lifetime), C391, C729, M164, V898*, X450.
- Lifetime: E587* (CCP 16 h, Wanderer 48 h), K329, S199 (16 vs 24 h).

## 10. Hand test (for the owner)
Setup: `git fetch origin && git checkout <branch>`, then `python3 -m http.server 8000` in the repo, open http://localhost:8000; back with `git checkout main`.
1. Wormholes tab: jump into a J-space system (or + Add one): its statics show at once in the System panel with the community note, and on its map box in class order.
2. Compare with the game for two or three systems (the static holes you see in system). Any mismatch: note the system and the codes (UNVERIFIED row below).
3. Hover a static chip: lifetime and masses. Type your own statics: the note says typed by you; clear the field: the list's come back.
4. Edit a connection: the Type field suggests the system's statics first, then K162.
5. Share → text: no statics for systems where you typed none.

## Built (v2026.11.19.1, 2026-11-19, the build session)
- As section 1b: `INTEL_WH_STC` in its own block (`n`, `of` = FNV-1a of `INTEL_WH.sys`, `codes`, `stc`, `src` with the commit and sha256), 853 bytes
  gzipped; `whTable` uses it only while `n` and `of` match. `jump_table_update.py` unchanged.
- D2-D6 as planned: `whStcOf` (yours, else the list's), `whStcNoteHtml` / `WH_STC_NOTE` (the note sits on its own line in the label's flex column,
  so the mockup's `.wh-stcsrc` wasn't needed), `whStcPaint` (typing and saving), `whStcSort` / `WH_STC_ORD`, `whStcLifeTxt` / `IT_WH_LIFE` (101 codes),
  `whTyOptsHtml` (the connection editor and + Add, which follows "Linked to" through `whAddTyList`).
- D7: the job `wh-statics` runs beside the other two (not after them); Wanderer's newest commit from `git ls-remote`, checked as 40 hex
  characters, passed to the steps through `env`; a pull request on `wh-statics/<short commit>`; plus a report-only step (`--ccp-fields`, R2).
- The chain's lint `gen_wh_statics.py --check` checks the block alone and compares with the pinned file only where GitHub's raw files can be
  reached (not from the build session); the Action compares twice a day.
- Section 9 re-run at pyfa e5483f8: the same 24 types differ.
- Checks: `wormhole_statics_check.py` (12 mutants), `gen_wh_statics.py --check` / `--self-test` in the fast lints.

## Sources
| Fact | Source | Checked | Status |
|---|---|---|---|
| Wanderer's statics file: one record per J-space system with `solarSystemID`, `systemName`, `effectName`, `statics`, `wanderers` | wanderer-industries/wanderer `priv/repo/data/wormholeSystems.json`, commit 4d4a035 (the provider's own repository) | 2026-11-19 | verified |
| Wanderer loads that file at start-up and serves statics per system | wanderer-industries/wanderer `lib/wanderer_app/eve_data_service.ex` line 80, commit 4d4a035 | 2026-11-19 | verified |
| Wanderer shows statics on the map box sorted by destination class, in its info panel, with mass and lifetime on hover, and first in a signature's type picker | wanderer-industries/wanderer `assets/js/hooks/Mapper/components/map/components/SolarSystemNode/SolarSystemNodeDefault.tsx`, `helpers/sortWHClasses.ts`, `components/mapInterface/widgets/SystemInfo/SystemInfoContent/SystemInfoContent.tsx`, `components/ui-kit/WHClassView/WHClassView.tsx`, `components/mapRootContent/components/SignatureSettings/components/SignatureWormholeTypeSelect/SignatureWormholeTypeSelect.tsx`, commit 4d4a035 | 2026-11-19 | verified |
| Wanderer is under the MIT licence | https://github.com/wanderer-industries/wanderer/blob/4d4a035/LICENSE (not a secondary source: the provider's own repository) | 2026-11-19 | verified |
| The file covers the page's 2,604 INTEL_WH systems, 1–3 statics each, 43 codes all in IT_WH_TYPE | `priv/repo/data/wormholeSystems.json` (wanderer-industries/wanderer 4d4a035) compared in this session with `index.html` INTEL_WH and IT_WH_TYPE at main 513c1e6 | 2026-11-19 | verified |
| Wanderer's effects differ from CCP's on J005926 and J010569 | the same comparison (INTEL_WH effects come from CCP's SDE via tools/jump_table_update.py) | 2026-11-19 | verified |
| Statics agree with Pathfinder's table on 2,595 of 2,604 | exodus4d/pathfinder `export/csv/system_static.csv`, commit 62dc991, compared in this session | 2026-11-19 | verified (as those files' contents) |
| Wormhole types carry `wormholeMaxStableTime` (minutes), `wormholeMaxStableMass`, `wormholeMaxJumpMass`, `wormholeMassRegeneration` (kg) | CCP's SDE as shipped in pyfa-org/Pyfa `staticdata/fsd_built/` (typedogma, dogmaattributes), commit b79cd90, read with tools/pyfa_sde.py: e.g. Wormhole C247 (type 30691) 960 / 2,000,000,000 / 375,000,000 / 0 | 2026-11-19 | verified |
| The units: masses in kg; stable time in minutes | pyfa-org/Pyfa `staticdata/fsd_built/dogmaattributes.0.json` + `dogmaunits.0.json`, commit b79cd90: attributes 1383–1385 unit 2 (kg); 1382 unit 3, which CCP's record names seconds | 2026-11-19 | verified: the owner's hand test, 2026-11-20 ("all passed") |
| The statics are right in game | community data (Wanderer, Pathfinder; whtype.info cited in a Wanderer commit): secondary sources | 2026-11-19 | verified: the owner's hand test in game, 2026-11-20 ("all passed") |
| Statics aren't in CCP's SDE or ESI | EVE forums 2015 and 2021 (secondary sources), no ESI route found | 2026-11-19 | verified: the wh-statics job's runs of 2026-11-20 listed CCP's fields, checked in the owner's hand test ("all passed") |
| CCP's lifetimes and masses differ from Wanderer's on 24 types | pyfa-org/Pyfa `staticdata/fsd_built/` (b79cd90) vs wanderer-industries/wanderer `priv/repo/data/wormholes.json` (4d4a035), compared in this session | 2026-11-19 | verified (that they differ; which is right: UNVERIFIED: the owner's Q8) |
| Wanderer's raw file is reachable at raw.githubusercontent.com from GitHub Actions | GitHub's own documentation of raw file URLs (not a secondary source: GitHub's own); a live answer seen: the jump-table workflow's wh-statics job on GitHub Actions, https://github.com/gitLaloosh/threatvector/actions (2026-11-20) | 2026-11-19 | verified: the wh-statics job ran green twice on 2026-11-20 (04:00 and 19:15 UTC) |
