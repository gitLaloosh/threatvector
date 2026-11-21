# Plan: the security the game shows, stored by the generator (the "rounded twice" bug)

Status: READY 2026-11-20 (research session, main f70fdd5, v2026.11.20.1). All questions answered (section 7); every in-game fact checked. QUEUED as build queue 063 2026-11-20 ([stated] "yes"; claude/build-queue/063-security-shown.md).
**BUILT 2026-11-21 as v2026.11.21.1** (build queue 063, branch `063-security-shown`; pull request 1 of 2: the generator, the page with the fallback,
the checks, and the "one Home only" Wormholes fix). See "Built" at the end for where the build differs from this plan.
Backlog: "BUG | Moderate — Security shown from a value rounded twice (the map's data stores hundredths)" (project memory, dscan-backlog-7).

## 1. The bug, in short

`tools/jump_table_update.py` stores each k-space system's security as `INTEL_MAP.sec`: CCP's value rounded to 3 decimals, then to hundredths (`jr(jr(v * 1000) / 1000 * 100)`, int8). The page then rounds that to tenths (`itMapSecT`). A value rounded twice can land on the other side of a tenth. 058 fixed the 0.45 line with 047's `band` (19 systems); every other edge is still wrong.

**Measured 2026-11-20** (the owner's built-in browser, on threatvector.space at v2026.11.20.1): ESI's unrounded `security_status` for every system whose stored value ends in 5 or sits between −0.04 and 0.04, 971 systems, against the page's own `itMapSecT`:
- **333 systems show a tenth the game doesn't** (143 above 0.0, 190 at 0.0 or below). Each is off by exactly 0.1. Examples: Jita 0.946 shows 1.0 (game 0.9), Juddi 0.649 shows 0.7 (game 0.6), XQS-GZ −0.551 shows −0.5 (game −0.6).
- No system changes band (high / low / null): 058's band line already holds that. So it's the number and the per-tenth colour, the Security range filter, the hover, the Wormholes tab's k-space line, and the Intel example.
- The 13 systems between 0.0 and 0.05 already show 0.1 (058's "never 0.0 above 0.0").

## 2. The rule the game uses

**Nearest tenth of CCP's unrounded value, except anything above 0.0 and below 0.05 shows 0.1.**

- All 7 of the owner's in-game screenshots (2026-11-16) match the nearest tenth of ESI's unrounded value, including two within 0.0004 of the halfway point:

| System | ESI security_status | Nearest tenth | In game (owner) | Map today |
|---|---|---|---|---|
| XQS-GZ (30000585) | −0.5513124 | −0.6 | −0.6 | −0.5 |
| 0LY-W1 (30000645) | −0.5500394 | −0.6 | −0.6 | −0.5 |
| B-E3KQ (30000307) | −0.2554699 | −0.3 | −0.3 | −0.2 |
| W2T-TR (30000617) | −0.0502633 | −0.1 | −0.1 | 0.0 |
| YPW-M4 (30000784) | −0.5424412 | −0.5 | −0.5 | (not read) |
| Helgatild (30002063) | 0.1518976 | 0.2 | 0.2 | 0.2 |
| Juddi (30000051) | 0.6491367 | 0.6 | 0.6 | 0.7 |

- The 0.0–0.05 rule: from a secondary source, used by the page since v.100 for names coloured from ESI (`itSecKey` / `itSecText`), and **checked 2026-11-20: Egbinger (0.0346) shows 0.1 in game** ([stated] "Egbinger is 0.1").
- **Two systems sit on the halfway point** as CCP stores them (float32): A2V6-6 −0.85000008 and A-5M31 −0.15000151. Nearest gives −0.9 and −0.2, but the game could show −0.8 and −0.1 if it rounds a shorter form of the number. Only the game can say. **A2V6-6 checked 2026-11-20: −0.9 in game** ([stated] "A2V6-6 is 0.9"; a nullsec system, so −0.9), as nearest predicts. **A-5M31 checked 2026-11-20: −0.2** ([stated] "A-5M31 is -0.2"), also as nearest predicts. Two more are close (2JJ-0E −0.6500063, KW-OAM −0.6499916) but not as close. See D4.

## 3. What changes

**C1. The generator stores the shown tenth** (`tools/jump_table_update.py`):
- New column `secT`: int8 tenths (−10…10), from CCP's unrounded `securityStatus` by the rule above, one function `shown_tenth(v)`. It replaces `sec`. `sec` and `band` are dropped (D2, D3).
- The `same_map` compare and the "how many systems changed security" count read `secT`. The first run after the change says in the pull request that the column changed form (every system's row "changes"), and lists the systems whose shown tenth changed (about 333) and the 7 sample systems with their unrounded values, so the owner can compare them with the table in section 2.
- **The tie guard (D4):** a system whose value is within 1e-5 of a halfway point (|10v − ⌊10v⌋ − 0.5| < 1e-5) must be in `SEC_CHECKED_IN_GAME`, a small table in the generator (system ID → the tenth the owner saw in game). Otherwise the run still writes the table with the nearest tenth and opens its pull request, with the system named at the top of the pull request's text as "to check in game" (changed at the build review 2026-11-20, the owner: [stated] "yes, the second.", over failing the run, which would also hold back that build's stargate changes); the owner checks it in game and the next delivery adds it to the table. It starts with A2V6-6 → −9 and A-5M31 → −2 (both checked by the owner in game 2026-11-20).
- `--self-test` (or the generator's own check in `tools/independent_checks/check_jump_table_update.py`) gets the rule's cases: 0.0346 → 1, 0.0 → 0, −0.0503 → −1, 0.4499 → 4, 0.45007 → 5, −0.55004 → −6, 0.94591 → 9, a value at a halfway point not in the table → the nearest tenth, named in the pull request's text as "to check in game" (D4).

**C2. The page reads it** (index.html):
- `itMapSecT(i)` returns `T.secT[i]` (`itMapTable()` decodes it as Int8Array, like `sec` today). The 058 band line and the rounding go.
- `itRpBand(T, i)`: from `secT`: ≤0 null, 1–4 low, ≥5 high (identical to 047's band; checked by C3's data check).
- **Names coloured from the table (Q1, [stated] "Read the table (Recommended)"):** `itSecKey` / `itSecText` / `itSecClass` take a k-space system's tenth from the table (`itMapSecT` through `itGraphGet().at`), and `itSecFetch` asks ESI only for systems the table doesn't hold (J-space, or anything new before the workflow's next update). The `sec:<id>` values already cached in IndexedDB are left alone. While the page has no `secT` (the fallback below), names keep asking ESI as today, so nothing gets worse in between. The Intel example's `it.sec` set-up (`itExSandbox`) does the same already.
- **Fallback until the data lands (D1):** while the page's INTEL_MAP has no `secT`, `itMapSecT` keeps today's code. The next page delivery after the data pull request removes it (a flag in that delivery's queue file).

**C3. The checks:**
- `tools/check_sec_shown.py`:
  - code: `.secT[` is read only in `itMapSecT` (`.sec[` only in the fallback, then nowhere);
  - data: when `secT` is present, the 7 owner samples (IDs → tenths in section 2) are pinned, every value is −10…10, and no system above 0.0 shows 0;
  - mutants: today's double rounding, and a reader outside `itMapSecT`.
- Page checks that read `T.sec` today must move to `secT` or to `itMapSecT`. Found by search: `intel_map_stack_check.py` (the "19 systems at 0.45" case, ~line 297: it becomes "the systems from CCP's list show their checked tenth", or the case is retired with a pinned sample). The build greps the rest: route_planner_check, intel_map_look_check, intel_map_layout_check, paths_to_you_check, wormhole_filter_check, tag_only_check, check_jump_table_update, tools/README.md, plus any made-up INTEL_MAP in a check.
- LESSON #170 gets a line: the root cause is fixed at the source; the page doesn't round security.

## 4. Delivery path (D1, Q2)

The build sandbox can't reach CCP's static data, but the "Jump table" workflow can (it runs twice a day, and by hand from the Actions tab).
1. **Pull request 1 (the build session):** C1's generator change, C2 with the fallback, C3's checks (they handle both forms). The page looks the same until step 2.
2. **After the merge:** the owner runs "Jump table" from the Actions tab (Run workflow, on main). It sees `secT` missing, rewrites INTEL_MAP and opens its own pull request with the list of changes. The owner merges it, and the page then shows the game's tenths.
3. **The next page delivery** removes the fallback (one flag line in its queue file).

Q2 asks whether he'd rather run the generator on his own computer in pull request 1's branch, so it all lands in one pull request.

## 5. Decisions made by this session (say if any is wrong)

- **D1. Two pull requests, a fallback in between:** see section 4.
- **D2. `sec` replaced by `secT`, not reused:** a leftover reader of `.sec[` then finds nothing and fails a check, instead of silently treating tenths as hundredths.
- **D3. `band` dropped:** with the shown tenth it's derivable exactly (0.45 ≤ v < 0.5 rounds to 5 = high; 0 < v < 0.05 shows 1 = low; v ≤ 0 shows ≤ 0 = null). The generator asserts derived band = `sec_band(v)` for every system before writing. It saves about 0.4 KB gzipped.
- **D4. A tie guard instead of a guessed rule** for values on a halfway point (C1), with the two found today checked in game. **Changed at the build review (2026-11-20):** an unchecked halfway value no longer fails the run; it takes the nearest tenth and is flagged at the top of the data pull request to check in game (the owner: [stated] "yes, the second.").

## 6. What it touches

- **UI rules it touches:** none of the layout rules. Colour tokens are unchanged (the per-tenth colours are the existing ones). 333 systems change number and tenth colour by one step; nothing moves. No mockup (owner's choice, Q3).
- **Info text it touches:** none. Searched `CARD_INFO` and `IT_EX_NOTES` for security, rounding, 0.45, hundredths and how system names are coloured (main f70fdd5): nothing describes how the map rounds or that names ask ESI. The build re-checks against its diff.
- **Lookups:** fewer ESI requests (one per k-space system shown, before). The header's Lookup budgets gauge counts what's asked, so it simply sees fewer; its text is off-limits and unchanged.
- **The Intel example:** reads security through `itMapSecT` (`itExSandbox`), so it follows. Markers unchanged.
- **Stored browser data:** none. INTEL_MAP lives in the page. `it.sec`'s `sec:<id>` values in IndexedDB (from ESI) are untouched.
- **Page size:** `sec` today is 7,024 bytes of base64 (5,156 gzipped), `band` 1,756 (393). Tenths compress better, so the estimate is 1.5–2.5 KB gzipped smaller (the build measures it).
- **DLA:** none (CCP's public static data, already used).
- **Panel review:** not a fit. CCP's data and the owner's screenshots settle it.

## 7. Questions for the owner (all answered 2026-11-20)

- **Q1. Names coloured from ESI:** Near You, the Feed, the dossier and other system names ask ESI once per system (`itSecFetch` → `itSecKey`) and already use this rule. With the table holding the game's tenth, k-space names could read the table instead: no ESI request, coloured at once. J-space keeps ESI. The cost: a change CCP makes reaches the page only when the workflow's pull request is merged. Recommended: yes, read the table for k-space. **ANSWERED: [stated] "Read the table (Recommended)"** (C2).
- **Q2. One pull request or two:** two, as section 4 (recommended), or he runs `python3 -I tools/jump_table_update.py index.html --write` on his computer in the branch so the data comes in pull request 1. **ANSWERED: [stated] "Two PRs (Recommended)"** (section 4).
- **Q3. Mockup:** none (recommended: nothing changes shape, only 333 numbers by 0.1), or a before/after list of systems. **ANSWERED: [stated] "No mockup (Recommended)"**: No mockup (owner's choice).

## 8. Hand test (for the pull request)

1. Done 2026-11-20: A2V6-6 −0.9, A-5M31 −0.2 (both in `SEC_CHECKED_IN_GAME`).
2. Done 2026-11-20: Egbinger 0.1.
3. After pull request 1 (before the data): the map and names look exactly as today.
4. After the data pull request: on the map, Jita shows 0.9, Juddi 0.6, XQS-GZ −0.6, W2T-TR −0.1, with the hover and Security range agreeing; Jita's name in Near You or the Feed in the 0.9 colour, with no ESI `universe/systems` request for it in the browser's network list; the route planner's Safer route unchanged (bands unchanged).

## Sources

| Fact | Source | Checked | Status |
|---|---|---|---|
| ESI `security_status` of the 16 systems in section 2 and the 971 edge systems (333 shown differently by `itMapSecT`) | live answer: ESI `GET https://esi.evetech.net/universe/systems/{id}/`, run from threatvector.space in the owner's built-in browser | 2026-11-20 | verified |
| The game shows the nearest tenth of the unrounded value (7 systems) | the owner's in-game screenshots, recorded in the backlog entry (2026-11-16), against the live ESI answer above | 2026-11-20 | verified (7 samples) |
| A value above 0.0 and below 0.05 shows as 0.1 | the owner, in game: "Egbinger is 0.1" (ESI 0.0346); also forums-archive.eveonline.com/topic/381013 (secondary: a player post quoting EVE University's wiki) | 2026-11-20 | verified (1 sample) |
| A2V6-6 (−0.85000008) shows −0.9 | the owner, in game: "A2V6-6 is 0.9" (nullsec, so −0.9) | 2026-11-20 | verified |
| A-5M31 (−0.15000151) shows −0.2 | the owner, in game: "A-5M31 is -0.2" | 2026-11-20 | verified |
| The static data's `securityStatus` equals ESI's `security_status` | `tools/jump_table_update.py` reads mapSolarSystems.jsonl's securityStatus | 2026-11-20 | UNVERIFIED: the data pull request lists the 7 samples' values; compare with section 2 |
| The "Jump table" workflow runs by hand and opens a pull request when INTEL_MAP changes | `.github/workflows/jump-table.yml` (workflow_dispatch; "Open a pull request"), main f70fdd5 | 2026-11-20 | verified (the repo's own file) |

## Built (2026-11-21, v2026.11.21.1, the build session)

Pull request 1 of the two (section 4). Where the build differs from the plan, or adds to it:

- **The tie guard's width.** The plan wrote it two ways: "within 1e-5 of a halfway point" (which would also catch 2JJ-0E, 6.3e-6 off, and
  KW-OAM, 8.4e-6, the two section 2 calls "close but not as close") and |10v − ⌊10v⌋ − 0.5| < 1e-5 (1e-6 in security units, which would miss
  A-5M31, 1.5e-6 off). Built: within **5e-6** (`SEC_TIE`): a value that reads x.x5000 at five decimals. That holds both checked systems and
  leaves 2JJ-0E and KW-OAM to the nearest tenth, as section 2 intends. A tie above 0.0 whose nearest is 0.1 isn't flagged (0.0 never shows).
- **D4 changed at the review** (the owner: [stated] "yes, the second."): an unchecked halfway value takes the nearest tenth and is named at
  the top of the data pull request ("to check in game"), instead of failing the run; C1 and D4 above say so.
- **The pull request's text** (C1): flagged halfway systems first; then the systems checked in game (`SEC_SAMPLES`: the 7 screenshots,
  Egbinger, A2V6-6, A-5M31) with CCP's unrounded value, the tenth written and the one seen in game ("differs" when CCP has changed one); then,
  folded, every system whose shown security changes, was → now (the old page's view worked out from `sec` + `band` by `old_shown`). The
  workflow's title stays "Jump table: stargates changed in EVE build N" (`.github/` not touched).
- **D3:** the generator asserts, for every system, that the shown tenth's band (`tenth_band`) equals `sec_band` of the unrounded value; a run
  that would break it stops. `pack_band` is gone; `unpack_band` stays to read an older page's band for the list.
- **C2:** `itMapTable` decodes `secT` when present (then no `sec` or `band`); `itMapSecT` returns `T.secT[i]`, else the 058 code (the fallback).
  `itRpBand` reads the band from `itMapSecT` when there is `secT`. Names: `itSecTab(id)` (the table's tenth for a k-space system it holds,
  else undefined) is read first by `itSecKey` / `itSecText`; `itSecFetch` and `sysNameHtml` skip ESI for those systems.
- **C3:** `check_sec_shown.py` checks both forms; with `secT` it pins 10 systems (the plan's 7 + Egbinger + the two halfway ones), and its
  self-test makes a copy of the page with a made-up `secT` for the mutants. `check_jump_table_update.py` converts a page from before 063 first,
  then runs its cases on the converted copy (so it passes before and after the data pull request); its made-up values are the page's
  hundredths nudged off a halfway point the way the old page rounded. Page checks made to read either form: `intel_map_look_check`,
  `intel_map_stack_check` (with `secT`: Jita 0.9 outside Security range 1.0–1.0; the fallback keeps the 19-systems case), `route_planner_check`.
  All four security-reading page checks were also run on a copy of the page with a made-up `secT` (`with_secT`), to stand for the page after the
  data pull request.
- **One Home only** (the queue file's block; the owner at the review: [stated] "2. yes to both, 3. sure, 4. sure."): `whHomes`,
  `whHomeOthersOff`, `whHomeLine`, `whHomeOne`; `whRtNb` (062's Routes neighbours, taken out of `whRtRows` so both use one); `whChainMerge`
  drops a shared Home when you have one; `whMsg(t, true)` keeps a line made before the tab is drawn. `wormhole_home_check.py` (new; also the
  names-from-the-table cases).
- **Still to do:** after the data pull request merges, the next page delivery removes the fallback (`itMapSecT`'s `sec` branch, `itRpBand`'s
  band and rounded-number branches, `itMapBand`, the fallback cases in the checks); a flag line goes into that delivery's queue file.

