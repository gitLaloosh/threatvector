# Wormholes tab: "Mass", a map button that works out how to crit or roll a hole — plan

**Status: BUILT as build queue 070 (v2026.11.23.2, branch `070-hole-mass`, 2026-11-23); see "Built" at the end.** Queued 2026-11-23 (the owner: [stated] "Yes, queue it"); every question answered (section 10). Written against main 4c28fdd (v2026.11.22.1); check_plan_sources 0 problems, 7 UNVERIFIED rows for the hand test. Backlog: "Wormholes tab: a map button that works out how to crit or roll a hole" in dscan-backlog-9. Mockup: `Claude outputs/hole_mass_mockup.html` (scripts `roadmap/hole-mass-mockup/`, README there; `test_hm.py` 123 checks pass at 1440 / 390; check_pii 0 problems with the names list).

The owner, 2026-11-22: [stated] "build a button into the wormhole map that lets you calculate how to crit or roll a hole. should have a search with helper (like the add form does) for hole type. does it just need to know the hull you're flying or does it need a fit? either way, we want simple, clear steps that will allow you to quickly identify how best to reach the hole state that is desired."

## 1. His question: the hull, or the fit?

**The fit.** A hole loses the ship's mass at the moment you jump, and the fit changes that mass a lot. From CCP's data (SDE in pyfa v2.70.1, Sources):

| What's fitted | What it does to the mass that goes through |
|---|---|
| A propulsion module running when you jump | Adds 500 t (1MN AB / 5MN MWD), 5,000 t (10MN / 50MN), 50,000 t (100MN / 500MN), 500,000 t (10000MN / 50000MN) |
| Higgs Anchor rig (any size) | +100% mass |
| Zero-Point Mass Entangler (HIC module, running) | −80% mass |
| Armor plates | add their own mass (1600mm Steel Plates II: +3,750 t) |

So a hull alone gives the right number only for a ship with no plates, no Higgs Anchor and no ZPME, and it can't know which prop module you fit. Example (SDE): a Megathron hull is 98,400 t; with a 100MN MWD running, 148,400 t; with a Higgs Anchor too, about 296,800 t. Rolling depends on exactly these differences ("in cold, back hot").

The page already computes both numbers for a fit: PYFA CORE speed-calc (`pyfaShipSpeed`, ~6951) returns `mass` (no prop running) and `props[].mass` (each prop running), with plates, Higgs Anchor, ZPME, subsystems and modes. It doesn't hand them out yet: the fit's result has `alignTime` only (~18892). Plan: the fit result gets `mass: {base, boosted, secondaryBoosted}` beside `alignTime`. It's the same numbers, unrounded tonnes, so there's no new calculation.

**Decided (Q1, [stated] "Fits or a hull (Recommended)"):** ships come from **My Ships** (saved fits, exact) **or** a **typed hull** (an estimate: the hull's mass, plus a MWD of its size from `rigSize`, marked "hull only: plates, a Higgs Anchor or a ZPME change this").

**A ship's masses ("modes")**: each ship jumps at one of a few masses, and the steps pick one: **prop on** (the fit's prop module running; its own name, MWD or AB), **prop off**, and, for a fit with a Zero-Point Mass Entangler, **ZPME on** (ZPME running, prop off: CCP's data blocks a MWD while a ZPME runs, `ACTIVATION_BLOCK_EFFECTS` ~14526). The build gets each from the fit's own maths: `mass.base` and `mass.boosted` as above, and the ZPME mode by recomputing the fit with the ZPME's state on (`recomputeFitWithStates`), never a hand multiplier. A mode heavier than the hole's mass per jump is dropped for that hole ("only prop off fits this hole"); a ship with none left is "too heavy for this hole".

## 2. What the page already has

- **Each hole type's numbers:** `IT_WH_LIFE` (~31790, 061's `tools/gen_wh_table.py`) = {code: [lifetime min, total mass t, mass per jump t, mass regained t]} for 101 codes. It matches pyfa v2.70.1's SDE (gen_wh_table.py run 2026-11-22: "up to date"). K162 has none: its numbers are the other end's. The 8 small holes (A009 C008 E004 G008 L005 M001 Q003 Z006: 5,000 t a jump) regain 3,000,000 t.
- **The type helper:** the + Add form's type field is a `<datalist>` from `whTyOptsHtml(n)` (~34169): the linked system's statics first, then K162, then every code, each labelled "→ C3" etc. (`itWhDestTxt`). The new panel reuses it.
- **Mass words:** `IT_WH_INFO_TXT.mass` (~31807): stable "More than 50% of its mass remaining", reduced "Less than 50%", critical "Mass critical: less than 10% remaining". A connection keeps `mass` (and `life`, `size`) in `tvWormholes` (`st.links[]`). Each side's type is in `ends` (059).
- **Saved fits:** My Ships (`myShip.list`, `myShipBuild(rec)` → `{f}`) with module states (a ZPME saved as running counts).
- **Hull data:** `getType(typeId)` (~10742, ESI /universe/types, cached) gives `mass` and dogma attribute 1547 `rigSize` (1 small … 4 capital). Ship names → ids: `INTEL_SHIPS` (~26930).
- **Map toolbar:** `whShellHtml` (~34413): + Add, Share, ⚙, ⓘ, each opening a `.wh-pop` with `.wh-poph` and an `x-close`.

## 3. The panel (as in the mockup)

A new toolbar button **Mass** (between + Add and Share; title "Work out how to crit or roll a hole"; its own small icon, a hole with a downward arrow) opens a `.wh-pop` "Crit or roll a hole" with its ⓘ (`whmass`) and the close button:

1. **Hole** (Q6, [stated] "From connections (Recommended)"): a select of the connections of the system in focus ("to Rens · B274", "to J102057 · D382 · mass <50%", "to J122515 · K162"), plus "Another hole (type it)". Picking a connection fills the type and what it says now (the connection's `mass`; none recorded → More than 50%). The type is either side's own type that isn't K162 (`whSide`). A K162 with no known far side shows a type box asking "K162: what's the type on the other side (J122515)?", with the `whTyOptsHtml` list minus K162. "Another hole" shows the same box with K162 left in the list. Under it one line: "B274 → HS · 2,000,000 t total (1.8–2.2 million, ±10%) · up to 375,000 t a jump". For the 8 holes that regain mass it adds "this hole regains its mass: rolling it isn't practical" and no steps.
2. **It says now:** Fresh (nothing through yet) · More than 50% · Less than 50% · Less than 10%.
3. **Goal:** Roll it (close it) · Crit it (under 10%, still open). **Finish in** (Q3, [stated] "This side / other side (Recommended)"): "this side: J101524" · "the other side: Rens".
4. **Ships** (Q2, [stated] "Up to 4 (Recommended)"): one row each: a select (My Ships fits, or "Type a hull…" with a hull box listing ship names), a remove ×, and a line with its masses ("296,800 t hot (MWD on) · 196,800 t cold"), any "only … fits this hole" or "too heavy" warning, the hull-only note, and a **Finisher** tick ("Finisher: waits until the hole is under 10%"; [stated] 2026-11-22 "i'd like to protect the hic until it's needed. allow a ship to be marked as the finisher."). The summary line names it ("Phobos (finisher)"). "+ Ship" up to 4. The rows are kept in this browser (Q8, [stated] "In this browser (Recommended)", key `tvWhMass`).
5. **Show the steps** (`.mys-primary`). From then on the setup folds into one line ("B274 to Rens · roll it, finish in J101524 · Megathron, Heron" with Undo, Change and Start over) so the step stays in view, also on a phone.

**The steps** (Q5, [stated] "one at a time with branches expandable for a quick reference of what's about to be done."):
- **A step is a group of ships jumping the same way, then one look at Show Info** ([stated] 2026-11-22, after the mockup: "this is going to go through the jumps 1 ship at a time? any way to condense it to \"2 megathrons hot\" or \"1 hot one cold\" etc?"). Same ships with the same mode are counted ("Megathron ×2"); mixed modes are counted per ship ("Megathron (cold) + Phobos (cold, ZPME on) out").
- **The words** ([stated] "can we modify verbiage to say \"in hot\", \"in cold\", \"out hot\", \"out cold\" etc? jump over is obvious, question is direction and which modules should be on. seeing the word \"in\" or \"out\" helps them understand what the step is asking them to do and where they should be when doing it.", then [stated] "\"out\" would be the side you dont want to end up on."): **out** = a jump to the side you don't finish on, **in** = a jump to the side you finish on (so they follow Finish in: finishing on the other side, the first jump is "in"). **Hot** = the prop module running when you press jump, **cold** = off, "cold, ZPME on" for the HIC mode.
- a heading with the preview: "Steps · about 4–5 steps" (later "… more steps"; "· may need a risky trip" when a run against the possible holes reaches one; "· no safe step left");
- the steps so far, dim, each with what the hole said (in the connection list's mass colours); after three, the older ones fold into "3 earlier steps";
- **the step**, boxed: "4. **Megathron ×2, Phobos** **out hot** · J101524 → Rens · 631,600 t", and under it, small, which modules: "Hot: MWD on when you press jump." (or "Cold: prop module off.", "ZPME on, prop module off."). When the group can close the hole: "This can close it: jump lightest first, Megathron (hot) last.";
- when a ship in the group jumped the same way under 5 minutes ago: "Wait until 22:08 first: Megathron ×2, Phobos jumped in less than 5 minutes ago (polarized)." A free group at least 75% as heavy goes first instead of a wait;
- "Then Show Info on the hole: what does it say?" and four answer buttons (More than 50% / Less than 50% / Less than 10% / It's gone), 44 px on a phone;
- **What's next** (the page's chevron toggle, open by default): one line for each answer that can happen after this step, with the step that follows it ("Less than 50%: Megathron ×2, Phobos out hot, after a wait"; "It's gone: Rolled: …"). Answers that can't happen after this step aren't listed (their buttons stay, see "an answer that doesn't fit").
- **Undo** ([stated] 2026-11-22, after looking at the mockup: "and a \"back\" button", then "let's change \"Back\" to \"Undo\" - how many steps back can we take?"): takes the last answer back. The step it answered is shown again, with the ships' sides, polarization, what the hole could be and the preview as they were, and the connection's Mass goes back to what it was (unless the connection was removed). Pressed again it goes back further, **as far as step 1 of the current run, with no limit** (a copy of the steps before each answer; the possible-holes list is shared, not copied, so each copy is small). A run starts at Show the steps, Start over or Carry on: Carry on starts a new run, so Undo never brings back a ship list you changed. (The owner, on Undo stopping at Carry on: [stated] "your recommendation is fine here".) It's off before the first answer of a run. After "It's gone" it reopens the last step. No question (nothing is lost: the answer can be given again).
- **Start over** ([stated] 2026-11-22, after looking at the mockup: "needs to be a start over or reset button"): beside Undo and Change in the setup line, which stays pinned at the top of the panel while the steps scroll (also on a phone). With jumps made and the job not finished it asks first: "Start over? The 3 steps so far are forgotten; the hole starts from what it says now." [Start over] [Keep going] (`whAskHtml`). It goes back to the setup with the same hole, ships, goal and side, and **It says now** set to the last answer (so the next Show the steps starts from where the hole is). After the end (rolled, crit, closed) it goes straight back, with no question.
- **Change** reopens the setup. With jumps already made, it offers "Carry on (6 steps so far)" (keeps what the hole could be, the jumps and each kept ship's side and polarization: e.g. add a light ship for the last trip) or "Start over". Changing the hole or what it says now starts over.
- **Write back** (Q7, [stated] "Yes, update it (Recommended)"): when the panel was opened on a connection, each answer sets that connection's `mass`. "It's gone" ends with "The hole is gone. Remove the connection to Rens?" [Remove] [Keep it] (`whAskHtml`; Remove goes through the connection list's own delete).

Nothing is sent to EVE. It's for reference, like Routes.

## 4. The calculation

**The rules it uses** (Sources; the secondary ones are UNVERIFIED until the hand test):
- A new hole's total mass is anywhere within ±10% of the type's number (secondary).
- Each jump takes the ship's mass at the moment you press jump (secondary: since 2020). So "hot" means the prop module is running when you press jump.
- A jump that empties the hole still goes through, and the hole closes behind the ship (secondary).
- Show Info says more than 50% / less than 50% / less than 10% of the total remaining (the page's own words; secondary).
- Polarization: no second jump through the same hole in the same direction within 5 minutes (secondary).

**What it knows:** a list of the holes still possible, as pairs (total M, remaining R). Fresh: M across 0.9–1.1 × the type's total, R = M (about 200 values). Started from "less than 50%" etc.: every (M, R) whose share R/M fits that answer (about 200 × 200). Each jump of mass m takes m off every R. Each answer you give keeps only the pairs that would show that answer. This is plain arithmetic, so a check can replay it.

**Choosing the next step** (a group of ships, each with a mode; at most 4 ships × 3 modes, so every choice is tried):
- **Everyone on the finish side:** the heaviest group that **can't** close the hole for any total still possible goes out, **and that can come back**: coming back cold, lightest first, every jump but the last must still be unable to close it (for "Crit it", none may). Found in the mockup: without that, two Megathrons out together at "less than 10%" left no safe way home, since the first one back could close it on the second. Fewer ships win a tie.
- **Finisher** ([stated] 2026-11-23, with screenshots of a D382 at less than 50% where a Heron finisher was sent first, "about 81 steps": "shouldn't the heron be saved until the end in this case?"): the finisher **waits for the end game**. Going out, groups with a finisher aren't considered until the hole says less than 10% (or no other ship can jump at all). Before that, when the other ships have no fully safe trip, the step shows their least risky trip with its odds (Q4), and if the finisher could go safely it's offered, not chosen: "Heron (finisher) is kept for the end. [Send Heron instead: safe, about 81 steps]" (the count from the preview run with the finisher allowed). Pressing it allows the finisher for the rest of the run (Undo takes it back). From less than 10% on, safe groups without a finisher still come first, then the finisher (hot if safe, with the ZPME when only that is); among risky choices the least risky wins, finisher or not. Coming in, a part without the finisher comes first, so it comes in last.
- **A light finisher** (a Heron) can't close a hole quickly from less than 10%: its round trips carry little mass, so the preview may say many steps. A HIC (light out with the ZPME, heavy in with MWD, plates and a Higgs Anchor) is the ship for it; the panel doesn't judge the ship, it shows the count.
- **Ships off the finish side:** they come in. A part of them may only come in if it can't close the hole; all of them together may close it (Roll it), as long as the jumps before the last one can't: they jump lightest first, the heaviest last. Among the safe choices, the one that leaves the most possible holes where the next trip out is still safe or the hole is already closed (the simulation below).
- A jump that could close the hole is **allowed only if everyone then ends on the side you picked**; for "Crit it" none may close it.
- **Polarization:** when a ship in the group jumped the same way less than 5 minutes ago: "Wait until 21:14 first …", or a free group at least 75% as heavy goes first.
- **When no jump is fully safe** (Q4, [stated] "Show odds + safe mass (Recommended)"): the step shows the least risky jump (the lightest mode when risks tie) with "No fully safe jump: about 1 in 8 that it closes behind Megathron. A ship under 41,000 t would be safe." The "safe" mass is rounded down to 100 t. When even the least risky jump is certain to close it (every possible hole), no step is shown: "No safe step left with these ships: the next jump out would close the hole behind Megathron." plus "A ship under 119,200 t can do the last trip safely: add one with Change. Or leave it here: it says less than 10%."
- **Done:** "Rolled: the hole is gone, everyone is on this side", or "Crit: it says less than 10%, everyone is on this side". An answer that no possible hole fits ("that can't happen with these masses: check the ships or the type") starts over from what the hole says now.

**The preview** runs the same choices against three holes the answers so far still allow (the least, middle and most mass left), answering truthfully, and gives the range of jumps. It's redone after every answer.

**Simulation (this session, 2026-11-22, Python, one ship a step, before grouping; not in the repo):** B274 (2,000,000 t), 300 random holes in the ±10% range, rules as above.
- One Higgs battleship (200,000 / 300,000 t): with no risk allowed it never finishes. The last step always needs a jump out that could strand it.
- The same battleship plus a cruiser (12,000 / 17,000 t): 184 of 300 rolled with no risk at all. The rest need a risky last jump or a lighter ship.
- One plain battleship (100,000 / 150,000 t): 114 of 300 rolled with no risk.

So the honest answer often includes "bring something light for the last trip". This is why Q4 matters. The build session writes this simulation, with groups, into a page check (section 8). The mockup's checks run the grouped steps against 40 (crit) and 120 (roll, both sides) possible holes: no step shown as safe ever closes the hole on anyone.

## 5. What it keeps

- **`tvWhMass`** (new key, safe both ways): `{v: 1, ships: [{fit: <My Ships id>, fin?: true} | {hull: <name or type id>, fin?: true}]}` (Q8; `fin` = the Finisher tick, kept when the row's ship is changed). The steps themselves live only while the page is open.
- **The connection's `mass`** (Q7): the same field and values the connection's own Mass select writes (`stable` / `reduced` / `critical`), so nothing new in `tvWormholes`.

## 6. UI rules it touches

- **The Finisher tick** is the page's checkbox in a `.wh-note` label, as Share's include box (`data-wh-shinc`). **One close button** (`x-close` in `.wh-poph`), **popover reuse** (`.wh-pop`, `whPop`), **one text field look** (the + Add form's inputs), **the datalist helper** (reused, not a new list), **select** for state and goal (the page's selects), **44 px targets** on a phone for the answer buttons, **no horizontal scroll at 390 px** (the steps wrap; the ship rows stack).
- **Subtext rule:** the hole line and each step are one short line; the reasoning (the ±10% range, why this step) goes behind the panel's ⓘ.
- **Drawing cost:** no timer, except the polarization countdown, which is redrawn once a minute only while a wait is shown and the panel is open (LESSON #120: compare before redraw).
- **No button inside a button; colour tokens only;** the answer buttons use the mass colours the connection list already uses (`cm0`–`cm2`), with no new colours.
- **Page size:** small (one panel, the calculation about 150 lines). The served copy is 648,190 bytes against 800,000.
- **Intel example:** not touched (Wormholes tab only).
- **Phone toolbar (Q11, [stated] "Wrap to two rows (Recommended)").** On main at 390 px the map's control row already squeezes: + Add, Share and ⚙ are **39 px** wide (measured in the mockup on 4c28fdd, the 44 px rule missed today). A Mass button makes them 28 px. The mockup lets the row wrap on a phone (`.wh-ctl{flex-wrap:wrap; justify-content:flex-end}`), so every control is 44 × 44 in two rows; that also fixes today's 39 px. Decided: wrap (not Mass only in ⚙, not smaller buttons).
- **The form on a phone** is one column (`.wh-addf`'s two columns don't fit 390 px with these selects).

## 7. Info text it touches

- **New `CARD_INFO` key `whmass`** for the panel's ⓘ (about 120 words): what the numbers are, the ±10% range, hot / cold, "mass counts when you press jump", groups and the finisher ("a finisher waits until the hole says less than 10%"), polarization, "for reference: check Show Info after every jump", the hull-only estimate.
- **`whmap`** is at its cap (400 of 400 words, `INFO_ALL_MAX_BY_KEY`). It needs one clause in [Focus and adding]: "Mass works out how to crit or roll a hole." That's about 9 words, so the cap goes to about 410 (Q10, [stated] "Raise to ~410 (Recommended)"). Wording in the mockup (`CARD_INFO.whmass`, 5 paragraphs, within the 210-word cap and the 85-word opening).

## 8. Checks (for the build)

- A `wormhole_mass_check`, with made-up ships:
  - B274 fresh, one ship 100,000 / 150,000 t, roll: replaying the answers for M = 1.8 / 2.0 / 2.2 million follows the steps to "Rolled" with nobody stranded on any path where the panel showed no risk.
  - The risk shown matches the share of possible holes (a seeded run of 300).
  - "Crit it" never shows a step that can close the hole.
  - K162 with no far side asks for the type.
  - A ship over the jump limit is marked.
  - Polarization wait inside 5 minutes.
  - An impossible answer starts over.
  - A My Ships fit with a Higgs Anchor shows twice the hull mass.
  - 390 px: no sideways scroll, answer buttons ≥ 44 px.
- From the mockup's checks (`test_hm.py`), to carry over: 40 holes, "Crit it": no step shown as safe ever closes the hole; 60 holes × both finish sides, "Roll it": no step shown as safe ever leaves anyone on the wrong side; only answers that can happen are branched; polarization waits; no safe step → no answer buttons; Change → Carry on keeps the jumps; steps group ships ("Megathron ×2, Phobos out hot") and mixed modes are counted; a group that can close it says who goes last; the Finisher tick is kept (also when the row's ship changes), the finisher stays home on step 1 and waits for less than 10% (then goes with the ZPME), over 40 holes it never goes while a safe step without it exists, a Heron finisher at less than 50% gives the Megathron's least risky trip with "Send Heron instead" offered (pressing it uses the Heron, Undo takes it back), the safe mass is rounded down to 100 t; finishing on the other side, the first jump is "in"; Undo takes answers back one at a time (the Mass too, step 1 again, off with none, reopens the last step after It's gone, a new run after Carry on); Start over asks while jumps were made, Keep going keeps them, Start over returns to the setup with It says now = the last answer, no question after the end, the button stays in view while the steps scroll; K162 asks and its list leaves K162 out; Remove asks first.
- Mutants: no ±10% (assume the exact total), and the out-jump rule loosened (m ≤ R allowed).
- The fit's new `mass` field: the pyfa goldens' mass (PYFA CORE) match `pyfaShipSpeed`'s values.

## 9. CCP's DLA

No other player's information, no new ESI kind (hull types come through the existing `getType`). Nothing new to check in the digest beyond "how much the page asks CCP's servers": one cached type read per typed hull.

## 10. The owner's answers (2026-11-22)

- **Q1 Ships from:** [stated] "Fits or a hull (Recommended)".
- **Q2 How many:** [stated] "Up to 4 (Recommended)".
- **Q3 Finish on:** [stated] "This side / other side (Recommended)".
- **Q4 No fully safe jump:** [stated] "Show odds + safe mass (Recommended)".
- **Q5 Steps:** [stated] "one at a time with branches expandable for a quick reference of what's about to be done." (not either option as written: one at a time, plus the What's next list).
- **Q6 Opening it:** [stated] "From connections (Recommended)".
- **Q7 Write back:** [stated] "Yes, update it (Recommended)".
- **Q8 Ship rows:** [stated] "In this browser (Recommended)".
- **Q9 Mockup:** [stated] "Yes, mockup (Recommended)".
- **Q10 whmap cap:** [stated] "Raise to ~410 (Recommended)".
- **Panel review:** [stated] "Not now (Recommended)".
- **Undo's reach:** back to step 1 of the current run; Carry on and Start over begin a new run ([stated] "your recommendation is fine here").
- **Steps as groups, in / out / hot / cold:** [stated] "any way to condense it to \"2 megathrons hot\" or \"1 hot one cold\" etc?", "can we modify verbiage to say \"in hot\", \"in cold\", \"out hot\", \"out cold\" etc?", "\"out\" would be the side you dont want to end up on." (section 3).
- **Finisher:** [stated] "would people usually only use the hic with the entangler at the very end?", then "i'd like to protect the hic until it's needed. allow a ship to be marked as the finisher.", then (2026-11-23) "shouldn't the heron be saved until the end in this case?" → waits for less than 10%, offered before (sections 3 and 4).
- **Q11 The phone toolbar** (2026-11-23): [stated] "Wrap to two rows (Recommended)" (every control 44 × 44 in two rows on a phone; fixes today's 39 px too).

## 11. Reuse, don't add (the mockup's pieces → the page's)

| Mockup piece | The page's own | New on purpose, and why |
|---|---|---|
| Mass button | `.it-map-clr.wh-tb` + `data-wh-pop`, like + Add and Share | its icon (`HM_SVG`): no existing icon means mass |
| The panel | `.wh-pop`, `.wh-poph`, `x-close`, `whPop` / `whPopClose`, `infoBtnHtml` | — |
| Hole, It says now, Goal, Finish in | `.wh-addf` grid, `.wh-lnk` labels, the page's selects | — |
| Type box and its list | `.wh-ty`, `whTyOptsHtml` (a flag to leave K162 out) | — |
| Full-width field (`hm-wide`) | `.wh-ed .wide` does the same in the System panel: widen it to `.wh-addf` | — |
| Hole line, notes, section titles | `.wh-note`, `.wh-sub` | — |
| Ship row (`hm-ship`) | none fits (select + box + × + a line) | a small grid; the × is `x-close` |
| Masses' colours (`hm-said`) | the connection list's mass colours (`.wh-lr.cm0`–`cm2`'s `--lc`) | a class per answer, not inline styles as in the mockup |
| Setup line + Change (`hm-sum`) | `.wh-ctx`'s look is close (map overlay) | a boxed line in the panel |
| The step box (`hm-now`), done list (`hm-done`), answers (`hm-ans`), branches (`hm-br`) | none fits | new; the answers are the global `button` |
| What's next toggle | `button.it-whp-xb` + `IT_CHEV` (the page's one chevron) | — |
| Remove the connection? | `whAskHtml`; the delete in `whAskAct` (cn) | factor that delete into one helper both call |
| Show the steps / Carry on | `.mys-primary`, `.wh-acts` | — |
| Finisher tick; "Send … instead" | the page's checkbox in a `.wh-note` label (Share's include box); the global `button` | — |
| Undo, Start over and its question | the global `button`; `whAskHtml` | Undo keeps a copy of the steps before each answer (a list while the panel is open, emptied when a run starts) |
| The calculation | none | `hmPoss`, `hmNext` (groups), `hmApply`, `hmPreview`; the words `hmDirWord`, `hmModeWord`, `hmGroups` (names for the build to choose) |
| Ship masses | the fit's `pyfaShipSpeed` result (new `mass` field), `getType` for hulls, `INTEL_SHIPS` for names | — |
| Phone toolbar wrap | changes `.wh-ctl`'s phone rule | Q11: wrap |

Mockup shortcuts not to copy: in the mockup README.

## Built (build queue 070, v2026.11.23.2, branch `070-hole-mass`)

As planned, with these differences found or chosen at the build:
- **The holes still possible are boxes, not points** (LESSON #177). Section 4's points (161 fresh totals, 61 × 61 otherwise) let a real hole fall
  between them: the build's replay found a B274 of 2,037,288 t with 988 t left where the points said at least 1,200 t, so a Heron trip marked safe
  closed the hole on it. Each possibility is now a box `[total, left, half the box's width in total, in left]` (400 fresh, 80 × 80 otherwise,
  `hmPoss`), kept while any hole in it fits every answer (`hmBoxSays`); "safe" means no hole in any box could be closed, and the odds are the
  share of boxes that could. Timed at 6,400 boxes and four ships: under 100 ms per answer, so nothing needed spreading out.
- **The ship masses:** the fit result's `mass` is `{base, boosted, propModType, secondaryBoosted, secondaryPropModType}` in kg (the same values
  `alignTime` uses, from both the pyfa path and the fallback). The ZPME mode runs `estimateHpAndDps` on the saved fit with the ZPME `'active'`
  and every Propulsion Module `'online'` (the same engine `recomputeFitWithStates` calls, on a copy of the states, so the saved fit isn't changed);
  hot and cold use the ZPME `'online'` whatever the saved fit had. Pinned in the regression suite on two goldens (`massBaseT`, `massBoostedT`),
  derived with pyfa's own handlers (`tools/pyfa_fit_oracle.py`): the owner's Megathron 103,462.5 / 153,462.5 t, the buffer Dominix Navy Issue
  104,693.75 / 154,693.75 t (plates are lighter than the SDE's 3,750 t with the armor skill). Section 1's example: a battleship's MWD is the
  500MN (there is no 100MN MWD; the 100MN is an afterburner); the numbers stand.
- **Typed hulls** use Intel's ship names (`itShips`, English or Chinese) instead of a second map over `INTEL_SHIPS`.
- **Words the page reads:** the ship picker's group is "Your fits" (CLAUDE.md: "My Fit", never "My Ship"); the panel's ⓘ is `whmap#mass` (a
  variant of the Wormholes card, titled "How the crit and roll steps work"), so no new card name; a preview run still going after 80 steps shows
  "80+" (the mockup's "81" was the cap). Warnings use the page's `.it-warn`; the answers' colours are classes on the connection list's
  `cm0`–`cm2` (and `cmx` for It's gone); full-width fields reuse the System panel's `.wide` rule.
- **The polarization wait** is redrawn once when it ends (one timer, only while the panel is open, cleared on close), not once a minute.
- **`whmap`** is 410 words, the cap set to that count. **`whLinksDel`** is the one delete the System panel's list and the Mass panel call.
- **Also in this delivery:** the + Add form's Linked to bug (the owner, 2026-11-22). Opening + Add picked the right default; after an Add the form
  stayed open with its list unchanged, so from an empty map the second system went in loose too. `whAddLinkList` builds the list on opening and
  after every Add, by the same rule (the owner, at the review: [stated] "go with option A").
- **Checks:** `tools/page_checks/wormhole_mass_check.py` (the steps replayed against real holes: each ship of a step jumps lightest first and the
  hole closes behind the one that empties it; over 60 holes and both finish sides, plus holes at a box's edge; for a fresh hole the answers pin the
  total to an exact range, and every step marked safe must need less than any of those holes has left; ships that went out on a safe step must
  have a safe way back; the risk counted box by box; the finisher, polarization, an impossible answer, the words; saved fits' and hulls' masses
  with esi_from_sde; the panel; + Add's Linked to; a phone) and (then) 17 mutants, among them the plan's two and "points instead of boxes".
- **A safe plan that is slow** (found at the build: with a light ship that isn't the finisher, a reduced hole turned into many safe Heron trips,
  "about 49–80+ steps"; the owner at the review: [stated] "80 steps basically converts to 40 trips while waiting 5 minutes each round trip.", then
  [stated] "i agree" to offering both choices with the time; LESSON #178): the estimate gives the time too, a minute a step plus the polarization
  waits counted from each jump (`WH_MASS_STEP_MS`; a Heron alone: 80 steps, about 3 h 20 min). Over `WH_MASS_SLOW_MS` (30 minutes) the safe step
  offers `st.fast`, the least risky group at least twice as heavy, with its odds and the estimate taking the faster jumps (`hmPreview(pl, true)`);
  pressed (`H.fast`), that one step is the faster one with "Back to the safe way"; the next step is chosen as before. A preview run that strands
  someone isn't counted as steps. `whmap#mass` 207 words (the hull note moved to the row only, where it already was). 23 mutants.

## Sources

| Fact | Source | Checked | Status |
|---|---|---|---|
| Each hole type's total mass, mass per jump, lifetime and mass regained (IT_WH_LIFE); the page's table matches | CCP's SDE as shipped in pyfa's staticdata/fsd_built at tag v2.70.1 (https://github.com/pyfa-org/Pyfa, not a secondary source: CCP's own data file), attributes 1382–1385; tools/gen_wh_table.py run against it | 2026-11-22; again at the build 2026-11-23 | verified |
| Prop modules add 500 / 5,000 / 50,000 / 500,000 t (massAddition, attribute 796) by size | CCP's SDE in pyfa's staticdata/fsd_built at tag v2.70.1 (https://github.com/pyfa-org/Pyfa, not a secondary source: CCP's own data file), typedogma of every published Propulsion Module | 2026-11-22; again at the build 2026-11-23 | verified |
| Higgs Anchor +100% mass, Zero-Point Mass Entangler −80% (massBonusPercentage, attribute 1131); 1600mm Steel Plates II +3,750 t | CCP's SDE in pyfa's staticdata/fsd_built at tag v2.70.1 (https://github.com/pyfa-org/Pyfa, not a secondary source: CCP's own data file) | 2026-11-22; again at the build 2026-11-23 | verified |
| Hull masses (Megathron 98,400 t etc.) and rigSize (attribute 1547) | CCP's SDE in pyfa's staticdata/fsd_built at tag v2.70.1 (https://github.com/pyfa-org/Pyfa, not a secondary source: CCP's own data file), types.mass | 2026-11-22; again at the build 2026-11-23 | verified |
| Single-jump mass limits of C1–C6 holes were raised in 2021 (so older guides' 300,000 t figures are out of date) | CCP, https://www.eveonline.com/news/view/quality-of-life-updates (2021-03-17) | 2026-11-22 | verified |
| Show Info mass and lifetime messages were simplified and coloured in Legion (2025-09-09) | CCP, https://www.eveonline.com/news/view/patch-notes-version-23-01 | 2026-11-22 | verified (wording not given there) |
| The messages' thresholds: more than 50%, less than 50%, less than 10% remaining | Secondary: EVE University, https://wiki.eveuniversity.org/Wormhole_Community_Static_Rolling_Guide; the page's own IT_WH_INFO_TXT | 2026-11-22 | UNVERIFIED: the owner reads Show Info on a hole in game (hand test) |
| A new hole's total mass varies within ±10%, any value in the range | Secondary: EVE University (as above); EVE Online forum players, https://forums-archive.eveonline.com/topic/417768 | 2026-11-22 | UNVERIFIED: no CCP source found; the owner's experience or a roll in the hand test |
| Mass counts when you press jump, not on arrival (changed 2020) | Secondary: EVE Online forum players, https://forums.eveonline.com/t/changes-to-wh-mass/221528 | 2026-11-22 | UNVERIFIED: the owner confirms in game (prop module started before pressing jump) |
| The jump that empties a hole goes through and the hole closes behind the ship | Secondary: EVE University (as above) | 2026-11-22 | UNVERIFIED: the owner confirms from experience |
| Polarization: no second jump through the same hole in the same direction within 5 minutes | Secondary: EVE University, https://wiki.eveuniversity.org/Wormholes | 2026-11-22 | UNVERIFIED: the owner confirms in game |
| Cargo and drones in the bay don't add to the mass that goes through | none found | 2026-11-22 | UNVERIFIED: the owner confirms, or the panel says nothing about cargo |
| How fast the 8 small holes regain mass (attribute 1384's unit is kg; the rate isn't in the SDE) | CCP's SDE in pyfa's staticdata/fsd_built at tag v2.70.1 (https://github.com/pyfa-org/Pyfa, not a secondary source: CCP's own data file) | 2026-11-22 | UNVERIFIED: the panel only says "this hole regains its mass" for them, so no rate is needed |
