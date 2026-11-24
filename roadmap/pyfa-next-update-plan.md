# pyfa update after v2.70.0: Synchronizer counting moves to the faction modules, CCP data 3687575 (PYFA_CORE.md process): build plan (written 2026-11-12)

> **BUILT** as v2026.11.24.2 (build queue 042, branch `042-pyfa-next-update`, pull request below; history doc
> `dscan-tool-history/2026-11-24_pyfa-2-70-1-update.html`). Pinned pyfa **v2.70.1** (`7e6b50c`), CCP data 3724492. See "Built" at the end.

> Written by the build session at the owner's request ([stated] 2026-11-12: "Plan the pyfa update."). **Queued as build queue 042** ([stated] 2026-11-12 "queue it"; `claude/build-queue/042-pyfa-next-update.md`, on hold until pyfa's next release). Read from the repo at `d227c9d` (main, v2026.11.12.4, 040). Find things by name; line numbers are approximate.
> Background: the repo's `PYFA_CORE.md` ("When pyfa or its data moves"), `roadmap/expansion-update-runbook.md` steps 7–10, the last update's plan `claude/roadmap/pyfa-2-70-update-plan.md` (035, BUILT as v2026.11.11.2) and its history doc `dscan-tool-history/2026-11-11_pyfa-2-70-update.html`.
> **Build review 2026-11-24** (the build session, main `a02d876`, v2026.11.24.1): the release is **v2.70.1** and carries more than this plan expected. Read the section "Build review (2026-11-24)" before the rest; where it and an older section disagree, it wins.

## When to build
- **Decided 2026-11-12:** wait for pyfa's next release ([stated] "wait for release"). Don't build against master.
- pyfa's newest **release** is still **v2.70.0** (`e5483f86`). The three changes below are on pyfa's **master only** (`41b0629`, `a2c7b8e`, `b79cd90`); no v2.70.1 or later is tagged yet (checked 2026-11-12).
- 035's rule, picked by the owner: "pin the newest release at build time … **Never pin master**". The owner's own pyfa (the hand test's reference, `ownerPyfa`) is a release build, so a master pin couldn't be compared with it.
- **Recommended: build this when pyfa tags its next release** (expected to carry these three commits; whatever else it carries is found by the build's own dry run, step 2). Until then the page stays on v2.70.0 with its two TEMPORARY rows in DEVIATIONS.md.
- Option: pin master `b79cd90` now. Not recommended: no release to compare with, and master can still change.
- The builder runs `git ls-remote --tags https://github.com/pyfa-org/Pyfa` first and names the release it pinned in the pull request.

## What changed in pyfa after v2.70.0
1. **`41b0629`** (2026-11-10 21:00 +0100) "Apply faction bonus to synchronizers even if source module is offline": the nine rig counting effects went from `passive` to `offline`.
2. **`a2c7b8e`** (2026-11-11 07:54 +0100) "Do not consider mutated items as part of faction item bonus": a new design.
   - Each faction module's own effect (Effect12963–12966, 12989–12993, `rigSet…BonusModAddSetRigGroup`; `type = 'offline'`, a new `runTime = 'earliest'`) adds the module's `rigSet…Module` value to the `rigSet…Bonus` attribute of every fitted module in the group 'Rig Synchronizer'.
   - The rig's counting effect (12969, 12982, 12984, 12985, 13000, 13006, 13008, 13012, 13016) now reads its **own** `rigSet…Bonus` instead of summing over the fit: `count = module.getModifiedItemAttr('rigSetDreadGuristasBonus', 0)`, then raises the rig's attributes by ±count as before.
   - pyfa's fit calculation gains the run time `earliest` (`eos/saveddata/fit.py`, `eos/gamedata.py`).
   - Why mutated modules stop counting: a mutated module's effects are its **abyssal** type's (`mutatedMixin._mutaInit`), and no abyssal type carries a writer effect (0 of the 609 carriers, checked 2026-11-12).
   - Net rule: **every** matching faction module counts, offline included; a **mutated** one never counts.
3. **`b79cd90`** (2026-11-11 12:25 +0100) "Update static data": CCP client build **3682781 → 3687575**. What matters to the tool:
   - **Vengeance** (11365): `shipBonus2AF` 3 → **−5** (Effect4901 `shipMissileSpeedBonusAF2`: launcher `speed` per Amarr Frigate level, so the rate of fire goes from 15% slower to 25% faster at V).
   - **47 boosters** renamed "Expired …" and unpublished (ids 96542–96593): `PYFA_REMOVED_IMPLANT_IDS` changes.
   - 8 Supply Depots / Caches (72850–72853, 73012–73015) lose `disallowAssistance`: not read by the page.
   - Attribute display names and French text: not read by the page.
   - The page already lists build 3687575's 48 changed items (Vengeance + the 47 boosters) in `GAME_DATA_PENDING` (PR #40). This update empties it.

## What moves (dry run 2026-11-12, build session, scratch copy of `d227c9d`, PYFA_SRC = master `b79cd90`, OLD_PYFA_SRC = v2.70.0)
Report mode only; nothing written to the repo. The build's own run (step 2) replaces this.

| Step | Result |
|---|---|
| `gen_sync_table.py` | **refuses**, 9 problems: "effect 13008/13012/… reads a rigSet...Bonus attribute -- pyfa now counts through them (its master a2c7b8e): rebuild this table" (the guard 035 put in for exactly this) |
| `gen_resist_table.py` | **crashes**: `AssertionError: unexpected value expression (-a:rigSetDreadGuristasBonus)` (Effect13012's new form) |
| `gen_module_state_tables.py` | `EFFECT_STATE_TYPE` differs: 12963–12966, 12989–12993 new, `o` (offline) |
| `gen_implant_table.py` | `PYFA_REMOVED_IMPLANT_IDS` differs (the 47 expired boosters) |
| hull damage, weapon range, speed, EWAR, projected, cyno, mode, Intel tables | up to date |
| `refresh_golden_fixtures.py` | **0 of 281 fits change**; `shared_types.json` unchanged (no golden has a Vengeance; the Synchronizer goldens' fixtures carry no counter values that moved) |

## What to build
1. **The Synchronizer section (`synchronizer-rigs`, PYFA CORE), redesigned to master's model.**
   - The table carries both halves:
     - **writers**: faction module effect → (the rig attribute it adds to, `rigSet…Bonus`; the module's attribute it adds, `rigSet…Module`);
     - **rigs**: rig effect → (the `rigSet…Bonus` it reads; `[[rigAttr, sign, default], …]` as today).
   - Generated by `tools/gen_sync_table.py` from pyfa's handlers, never typed by hand. Its guard flips: it now refuses the v2.70.0 shape (a rig handler summing over `fit.modules`) and any writer that targets anything but the group 'Rig Synchronizer'.
   - `pyfaSyncRigTypes`: count = the sum over fitted modules **whose type carries a writer effect** of their `rigSet…Module` value, **in any state** (offline included: the writers are `offline` effects). A mutated module is read as its abyssal type (killmails already are), so it carries no writer and doesn't count. Then raise the rig's attributes as today.
   - `minState` goes from the row (every writer is `offline`). Keep the probe that confirms it, so a later pyfa change to the writers' type fails the generator.
   - `gen_resist_table.py` (and any generator meeting a rig counting effect) skips them as before: `pyfa_effects.counting_effects` learns the new handler form (`count = module.getModifiedItemAttr('rigSet…Bonus', 0)`).
   - The writer effects (`EFFECT_STATE_TYPE` `o`) are carried by the new table only. Check that no generic table also applies them, so they don't add twice.
2. **The paste reader:** a pasted mutated faction module (pyfa's mutation export, `eft_mutation_check.py`) is already marked mutated (`mutated` ~line 13130). With this update it **doesn't count** toward a Synchronizer: give the counter the reader's mark, or read it as pyfa does (its abyssal type). Pick whichever keeps `fitType` single-sourced.
3. **DEVIATIONS.md:** delete both TEMPORARY Synchronizer rows (mutated module on a killmail; pasted `/OFFLINE`). The tool then matches the release in both cases. A module the user sets offline in the module list now **counts** (pyfa: offline effects run in every state).
4. **Regenerate** every table with `--write`: the sync table, `EFFECT_STATE_TYPE`, `PYFA_REMOVED_IMPLANT_IDS`, and whatever the release adds.
5. **Golden fits:**
   - `ishtar_constructed_guristas_sync_hardener_offline` **moves**: the offline hardener now counts. Re-pin it from `pyfa_fit_oracle.py` with a note.
   - New constructed goldens, each against `pyfa_fit_oracle.py`:
     - a Synchronizer with every matching module offline (count = all of them);
     - a pasted fit with a **mutated** faction module and its Synchronizer (count excludes it);
     - a **Vengeance** with rocket or light missile launchers (the new −5% per level).
   - `caracal_constructed_caldari_sync_two` and the other Ishtar goldens should not move; if they do, explain.
6. **Empty `GAME_DATA_PENDING`** to the release's client build (PYFA_CORE.md step 5; `check_game_data_pending.py`). If CCP's newest build is already past it, run `sde_change_report.py --pyfa $PYFA_SRC --write` afterwards.
7. **The manifest's `pyfa` block**:
   - Fill in version, commit, clientBuild, dataDumped, verifiedOn and `ownerPyfa`.
   - Run `check_pyfa_core.mjs --update` for every re-locked section.
   - Update PYFA_CORE.md's `synchronizer-rigs` row and its "re-verified" line, and the tools/README.md rows for `gen_sync_table.py` and `eft_mutation_check.py`.
8. **History doc** `dscan-tool-history/2026-11-NN_pyfa-<version>-update.html`, the 2026-11-11 one's shape: what changed in pyfa, effect on the tool, what was done, "For the owner".

## Checks
- `PYFA_SRC=<release> python3 -I tools/pyfa_update_check.py --run` **before changing anything**, kept for the history doc; then the full chain green after.
- The Synchronizer goldens and the two mutants of 035 updated to the new model.
- New mutants, each must fail:
  - offline modules not counted (v2.70.0's rule);
  - a mutated module counted;
  - a writer applied twice (the table and a generic table).
- `eft_mutation_check.py`: a pasted mutated faction module no longer changes the Synchronizer's damage (today it does, as v2.70.0).
- The usual delivery: CLAUDE.md's steps, both page sizes (the served copy under 800,000 bytes), `run_checks.py --served`, `check_pii` with the names list, the version/summary/description snippet.

## UI rules it touches
None: numbers change, no controls, text or layout. **No mockup** (no UI change). The "Changed in EVE's update" note stops showing on the Vengeance and the 47 boosters once the list is empty.

## Info text it touches
- `CARD_INFO`: none (no panel names the Synchronizer rule; checked 2026-11-12).
- `IT_EX_NOTES`: none.
- METHODOLOGY.md "Synchronizer rigs" (not an info panel), new wording: "…for every matching faction module fitted, online or offline (…); its drawbacks don't change. … A mutated faction module doesn't count, as in pyfa (a killmail names only its abyssal type, which has no counter)."
- The code comments that name v2.70.0's rule (~5418, 13086–13093, 13740–13775) follow.

## DLA clauses
None: no other players' information, no new requests to CCP's servers, no branding.

## For the owner (goes in the pull request and the history doc)
- Update your own pyfa to the pinned release. Help → About must show it and its EVE data build before you compare screenshots (LESSON #10).
- Hand test:
  - in the Fit Analyzer, paste a Synchronizer fit with two matching faction modules, one set **offline** in pyfa: the tool and pyfa agree (both count it);
  - the same fit with one faction module **mutated** (exported from pyfa with "Mutated attributes" on): both leave it out;
  - a Vengeance with launchers: DPS equal to pyfa;
  - the "Changed in EVE's update" note gone on a Vengeance.

## Build review (2026-11-24)
By the build session, against main `a02d876` (v2026.11.24.1) and pyfa **v2.70.1** (`7e6b50c`), the first release after v2.70.0. `pyfa_update_check.py --run` was run against it before any change (output kept for the history doc).

**The release carries 14 commits** (`git log e5483f8..v2.70.1`): the three this plan named, plus:
- **`820d0d8` "Update static data & drifter mod effects":** CCP client build **3724492** (not 3687575; the page's `GAME_DATA_PENDING` was at 3714173, so 042 empties it to 3724492). The four 'Vigilant' Drifter modules' active effects were rewritten: each now multiplies the module's **own** attribute, which the module's passive effect then applies (Effect13048 the Overdrive Injector's `implantBonusVelocity`, early; 13049 the Shield Boost Amplifier's `shieldBoostMultiplier`; 13050 the Drone Navigation Computer's `speedFactor`, penalized; 13051 the Cap Recharger's `capacitorRechargeRateMultiplier`, post-assignment). The page still applies the old rule (`SPEED_EFFECTS` 13048, `PROJ_DRONE_EFFECTS` 13050, `SIEGE_FAMILY_REMOTE_REP_EFFECTS` 13049, `SHIP_CAP_ATTR_EFFECTS` 13051). Seen: `drake_constructed_vigilant_aberrant_active` cap recharge, tool 309.375 s, pyfa 300.0 s. The speed and projected generators now drop 13048 and 13050 as "self …, overheat, not modelled": a misreading (they are active-state bonuses), fixed in this build.
- **`b05457a` "Fix edge-cases around sansha synchronizer":** pyfa now runs rigs and subsystems before other modules in each pass (`eos/saveddata/fit.py`), because they change attributes other modules' own effects read (pyfa's example: propulsion modules' overheat bonuses). The page doesn't model overheat; checked with the oracle once it has the order.
- `5f0190c` darkness weather stacking penalty: the page doesn't model weather. `6a1e868` a conversions file (two renamed drones): the page keeps no rename list. `30a4b0a` / `ac23acc` pyfa's saved-fit events, `5af4b95` matplotlib: pyfa's app only.

**Two gaps in the project's own tools, found by the review:**
- **`tools/pyfa_fit_oracle.py` runs only `early`, `normal`, `late`.** The Synchronizer writers are `earliest`, so the oracle counts no modules and every Synchronizer golden "differs" in the dry run (`ishtar_constructed_guristas_sync_one`, `_three`, `_hardener_offline`, `caracal_constructed_caldari_sync_two`: resists, drone DPS, shield HP, lock range, missile range). Those figures are the oracle's, not pyfa's. Fixed first: the `earliest` pass and pyfa's rigs-and-subsystems-first order.
- **`tools/pyfa_sde.py` `pyfa_removed_types` counts only published boosters.** In data 3724492 the 47 expired boosters are unpublished, and pyfa's `db_update.py` keeps only published rows (its `processEveTypes` also unpublishes names starting "Expired "), so pyfa can't load them. Regenerated as is, `PYFA_REMOVED_IMPLANT_IDS` would lose all 47. Fixed: the removed set follows `db_update.py`'s publish rules.

**The owner's answers (2026-11-24):** "Whole release (Recommended)": pin v2.70.1 and match all of it, the four Vigilant modules included, each with a constructed golden; "Inside 042 (Recommended)": the oracle and generator fixes go in this pull request, first; "Yes, add a Vigilant step (Recommended)" to the hand test.

**Added to "What to build":** (0) the oracle's `earliest` pass and rigs-first order, and the removed-boosters rule, before anything that relies on them; (9) the four Vigilant effects modelled as pyfa does (the active bonus folded into the module's own attribute before its passive applies it), the generators' classification fixed so a self-modification that a passive effect of the same module reads isn't called overheat; goldens for each of the four, active and inactive.
**Added to "For the owner":** Help → About shows v2.70.1 and EVE data 3724492; a Drake (or any hull) with a 'Vigilant' Vital Cap Recharger active: recharge time equal to pyfa's.

## Sources
| Fact | Source | Checked | Status |
|---|---|---|---|
| pyfa's newest release tag is v2.70.0 (`e5483f86`); nothing newer is tagged | pyfa's own repository: `git ls-remote --tags https://github.com/pyfa-org/Pyfa` (live answer seen by the build session) | 2026-11-12 | verified (superseded 2026-11-24: v2.70.1 is tagged) |
| master after v2.70.0 is `41b0629`, `a2c7b8e`, `b79cd90` with the titles and dates above | pyfa's own repository: `git log e5483f8..b79cd90` (https://github.com/pyfa-org/Pyfa/commits/master) | 2026-11-12 | verified |
| `41b0629` changes the nine counting effects from `passive` to `offline` | https://github.com/pyfa-org/Pyfa/commit/41b0629247a4cbef96d4a2a4473d874263031e69 (pyfa's own repository, read with `git show`) | 2026-11-12 | verified |
| `a2c7b8e`: writers Effect12963–12966, 12989–12993 (`offline`, `earliest`) add `rigSet…Module` to the Synchronizers' `rigSet…Bonus`; the rigs' effects read `rigSet…Bonus`; fit.py runs `earliest` first | https://github.com/pyfa-org/Pyfa/commit/a2c7b8e485fa6e7d6b4a498a2b8ae8f14cdbfd55 and `eos/effects.py` ~44000–44660, `eos/saveddata/fit.py` ~1069 at `b79cd90` (pyfa's own code) | 2026-11-12 | verified |
| A mutated module's effects are its abyssal type's | pyfa's own code: `eos/saveddata/mutatedMixin.py` `_mutaInit` ~line 57 and `eos/saveddata/module.py` (`self.item.effects`) at `b79cd90` | 2026-11-12 | verified |
| 609 types carry a writer effect, none abyssal | pyfa's data at `b79cd90`: `staticdata/fsd_built/typedogma.*.json` and `types.*.json` (counted by the build session) | 2026-11-12 | verified |
| `b79cd90` ships client build 3687575 | pyfa's data: `staticdata/phobos/metadata.0.json` at `b79cd90` | 2026-11-12 | verified |
| Vengeance (11365) `shipBonus2AF` (485) 3 → −5; Effect4901 applies it to launcher `speed` per Amarr Frigate level | pyfa's data `typedogma.0.json` diff `e5483f8..b79cd90`; pyfa's code `eos/effects.py` Effect4901 at `b79cd90` | 2026-11-12 | verified |
| The 47 boosters 96542–96593 renamed "Expired …", unpublished; Supply Depots/Caches lose attribute 854 | pyfa's data diff `e5483f8..b79cd90` (`types.*.json`, `typedogma.2.json`) | 2026-11-12 | verified |
| The dry-run results in "What moves" | the repo's own `tools/gen_*.py` and `tools/refresh_golden_fixtures.py` at `d227c9d`, run by the build session against master `b79cd90` (live answer) | 2026-11-12 | verified (the build's run replaces them) |
| pyfa's next release carries these three commits and data 3687575 (or newer) | pyfa's own repository: `git ls-remote --tags https://github.com/pyfa-org/Pyfa` (v2.70.1 = `7e6b50c`), `git log e5483f8..v2.70.1` (14 commits, the three included), `staticdata/phobos/metadata.0.json` at v2.70.1 (client_build 3724492) | 2026-11-24 | verified |
| v2.70.1's `820d0d8` rewrites Effect13048–13051 to multiply the module's own `implantBonusVelocity` / `shieldBoostMultiplier` / `speedFactor` / `capacitorRechargeRateMultiplier` | pyfa's own code: `git show 820d0d8 -- eos/effects.py`, `eos/effects.py` ~44790–44860 at v2.70.1 | 2026-11-24 | verified |
| v2.70.1's `b05457a` runs rigs and subsystems before other modules | pyfa's own code: `git show b05457a -- eos/saveddata/fit.py` at v2.70.1 | 2026-11-24 | verified |
| pyfa's database keeps only published types and unpublishes names starting "Expired "; types 96542 and 96593 are unpublished in v2.70.1's data | pyfa's own code `db_update.py` `processEveTypes` ~line 161–200 at v2.70.1; pyfa's data `staticdata/fsd_built/types.*.json` at v2.70.1 (read by the build session) | 2026-11-24 | verified |
| The oracle runs only `early`, `normal`, `late` | the repo's own `tools/pyfa_fit_oracle.py` ~line 345 at `a02d876` | 2026-11-24 | verified |
| The Vigilant Drake's cap recharge: tool 309.375 s, pyfa 300.0 s | the repo's own `tools/independent_checks/compare_fit_stats.py` at `a02d876` against v2.70.1 (live answer) | 2026-11-24 | verified |

## Built (2026-11-24, v2026.11.24.2)
Where the build differs from the plan above (the "Build review" section is the scope the owner approved):
- **The release is v2.70.1**, data 3724492: everything above plus the 'Vigilant' Drifter modules and rigs-first, as the Build review says.
- **The oracle and the removed boosters were fixed first** (LESSON #181): `pyfa_fit_oracle.py` runs `earliest` and sorts rigs and
  subsystems first; `pyfa_sde.pyfa_db_published` ports `db_update.py`'s publish rules, so `PYFA_REMOVED_IMPLANT_IDS` holds every
  implant and booster pyfa lacks (1,292; none of the 177 before dropped) and the generator's pool gains the 16 'AIR ... Booster'
  boosters (three booster effects).
- **Synchronizers:** two tables, `SYNC_WRITER_EFFECTS` and `SYNC_RIG_EFFECTS` (not one table with both halves); the rig's own
  `rigSet...Bonus` value is added too. `pyfa_effects.sync_effects` finds both; `counting_effects` stays for the guard. The paste
  reader's mark reaches the counter as `options.mutated` (through `parsed.mutated`, the Fit Analyzer's input and `chgEngineOptions`),
  so `fitType` stays single-sourced.
- **The mutated golden is a killmail** (a Mutated Drone Damage Amplifier, 60482, the abyssal type a killmail names): the oracle can't
  read a pasted mutated item without its mutaplasmid. The paste case is `eft_mutation_check.py` (the mutated paste equals the plain
  paste on a page copy with no faction-module effect), with a mutant that drops the mark.
- **The Vigilant modules:** a new PYFA CORE section `self-active` (`SELF_ACTIVE_EFFECTS`, `tools/gen_self_active_table.py`,
  `pyfaSelfActiveDogma`; the engine's `selfActiveParts` splits a module's active copies from the rest where its passives are read).
  Each module fits once per ship (`maxTypeFitted` 1). Goldens: the Drake active (re-pinned) and online, a Rifter's injector and a
  Vexor's computer, each active and online. `gen_speed_table.py` now tells overheat, self-active and Synchronizer self rows apart.
- **A 035 bug** (LESSON #182): its 13049 row sat in a table read only for siege modules, so the active amplifier never reached the
  page; the Drake's 86 HP/s was the tool's own number. `compare_fit_stats.py` (through `compare_implants.oracle_values`) now
  compares shield reps with an amplifier (10 goldens).
- **Mutants run by hand** (none kept as code, as in 035): the rig table emptied, offline not counted, a writer twice, the Vengeance's
  old bonus, and SELF_ACTIVE_EFFECTS without 13049 (caught by the widened comparison).
- No mockup, no UI change. Info text: checked; none.
