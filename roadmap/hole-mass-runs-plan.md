# Wormholes tab, Mass: saved runs, + Finisher, and odds that say which way it closes — plan

**Status:** BUILT 2026-11-25 as v2026.11.25.1 (branch `072-hole-mass-runs`; see "Built" at the end). Was queued as 072 (2026-11-24, [stated] "your choice on the phone question, let's queue it."; `claude/build-queue/072-hole-mass-runs.md`). **Widened 2026-11-25 with a ship lost** ([stated] "include in 072"; section 6b, decision 13). All questions answered; check_plan_sources 0 problems, 4 UNVERIFIED rows for the hand test. Written against main a02d876 (v2026.11.24.1). Mockup `hole_mass_runs_mockup.html` (sent to the owner; scripts `claude/roadmap/hole-mass-runs-mockup/`, README there; `test_rr.py` 143 checks pass at 1440 and 390 px (99 before the ship-lost part); check_pii 0 problems besides the page's own reviewed EVE login button). Builds on 070 (plan `roadmap/hole-mass-plan.md` in the repo, with its Built notes). Backlog: `areas/dscan-backlog-9.md`, "Wormholes tab, Mass: "N% that it closes behind <ship>" doesn't say which way it would close".

## 1. What the owner asked

- [stated] 2026-11-24, the bug (with a screenshot of step 5, "Megathron out cold", reference only, not stored): "add a bug: % chance that it closes behind <ship> should clarify if it means close on the wrong side of the connection or if it would collapse the hole on the way back in rather than crit the hole."
- [stated] "plan it first and plan it with the ability to add a small ship at any point in the process as a "finisher" (like a buzzard or something that can be used for critting where it's a close call or risky w/ larger ships)."
- [stated] "we need to save a "rolling" or "critting" session in browser storage as well. i accidentally hit the "back" button on my browser earlier mid-session and lost my rolling state. not good. let's have it persist until it's manually deleted. even allow the ability to save multiple at once. so include this and re-evaluate."
- [stated] "your recommendation works for all questions" (section 3).
- **A ship lost** (2026-11-25): [stated] "add a backlog item to account for a ship being lost during the rolling/critting process so we dont have to start from scratch in order to get accurate instructions."; then, on a ship that jumped and then died: "then the user can select the new mass state, let the steps update and THEN mark it as lost. this way the current step updates w/ the new ships available."; on one lost before jumping, skip the answer and mark it lost: "correct. if you see a problem w/ that logic let me know"; a ship lost part way through a group step only leaves the step, which waits for its answer: "sounds good to me"; the pod coming home: "ok"; a replacement: "we will already support adding a ship mid-session, just ask which system it's being added in so that could handle the replacement ship question."; the finisher: "losing the finisher means finishing the session without it unless replaced."; no panel review ("ok, no panel for now."); "include in 072".

## 2. What main does today (a02d876)

- **One number for two outcomes.** `hmNext` (~36254) scores a step with `hmShare(P, need)` (~36187), the share of the holes still possible with at most `need` tonnes left. With everyone on the finish side, a group going out has `need` = the trip out plus every ship's lightest way back, minus the last way back for Roll only (~36283). So for Crit the one number covers both "the hole closes before everyone is back" (ships **stuck** on the far side) and "it closes as the last ship comes in" (everyone home, the hole **gone, not crit**). Coming in (~36266), Crit uses the group's whole mass, which lumps the same two. The pick ranks by that number. The words "N% that it closes behind <ship>" are in three notes (`hmRiskHtml` ~36432, `hmSlowHtml` ~36443, `hmFastHtml` ~36450) and the What's next list's "(risky: …)" (`hmBranchesHtml` ~36454).
- **The safe-mass line is wrong for Crit trips out.** `out()` sets `safe = Rmin − (need − m)`: Rmin minus the group's own way back, as if a light ship also had to carry the Megathron home. The owner's screenshot shows "No ship is light enough to be sure." beside "Send Thorax instead: safe". A lone ship going out and back cold is safe under about Rmin / 2. The same sentence is in the "No safe step left" note (`hmStepsBodyHtml` ~36480, which also says "add one with Change"). Coming in, a lighter ship isn't the answer at all (only the ships that are out can make that trip).
- **Adding a ship mid-run** is Change → + Ship → Carry on (`hmGo(true)` ~36494): a new run, so Undo stops there (`H.back` reset); the new ship always starts on 'this' side (`hmNew` ~36247); at most `WH_MASS_MAX` = 4 ships (~36163).
- **Finishers in Crit** only ever jump by "Send X instead" (`finOk`, which frees every finisher at once) or when nothing else can, since "less than 10% with everyone home" already ends a Crit run. The ship row's tick says "Finisher: waits until the hole is under 10%" (`hmShipRowHtml` ~36387), which is wrong for Crit.
- **A run lives only in memory** (`hmState` ~36174, `whS.hm`; `tvWhMass` keeps only the ship rows, `hmRead` ~36179). Leaving or reloading the page loses it (the owner lost one with the browser's back button). `hmOpen` (~36492) also drops a run (`H.pl = null`) when Mass is opened with a system in focus whose connections don't include the run's link. "This side" and here / there are relative to the system in focus when the run began.
- **A ship lost** has no action: the only way is Change → remove its row → Carry on (`hmGo(true)` ~36494), a new run (Undo stops there), and a ship new to the list on Carry on always starts on 'this' side (`hmNew` ~36247: `at: 'this'`), so a replacement on the far side is counted on the wrong side.
- **Found while planning:** the setup's connection list reads "to J102057 · D382 · mass mass <50%": `hmLinksHtml` (~36365) puts " · mass " before `IT_WH_INFO_TXT.mass[...][0]`, which already starts with "mass" / "crit". Fix it in this delivery (drop the extra word).
- **Found in the mockup:** a ship's masses arrive later (async); `hmShipOf` (~36237) repaints only when no run is shown, so the + Finisher row would never show its masses. Repaint while the add row is open too.

## 3. Decisions ([stated] "your recommendation works for all questions")

1. **The odds split in two**, named by side: "about 1 in 131 that it closes with Megathron stuck in J102057; about 1 in 4 that it closes on Megathron's jump in: everyone's home, but the hole is gone, not crit." Roll shows only the stuck part (closing on the last ship home is the goal there). When only the second part can happen: "no one can be left behind, but …".
2. **Stuck ranks first in Crit**; the collapse only breaks ties (then the total, then the lighter group). Roll is unchanged (its number is all stuck).
3. **+ Finisher**, always in the run's pinned line (beside Undo, Change, Start over), opens one ship row inline with Finisher implied.
4. **Its side is asked in that row:** "It's in [<finish system> (where you finish) | <other system>]", the finish side picked.
5. **Up to 5 ships** (the setup's + Ship too). Timed in the mockup with 5 ships and 6,400 possible holes: `hmNext` under 1 ms, a preview about 6 ms, a full redraw with three finishers about 230 ms (headless Chrome); the build times it on the page and says so in the pull request.
6. **A "Send X instead" per finisher**, lightest first; pressing one frees that ship only ("Buzzard (finisher, sent)" in the line); the others stay kept.
7. **Crit keeps offering** (never picks a finisher on its own), as the owner chose on 2026-11-23.
8. **Saving is automatic** after every change: an answer, Undo, an added finisher, Send X instead, Carry on, Start over, a ship lost.
9. **Undo goes back through the whole run**, past an added finisher and Carry on (replaces 070's "Undo stops at Carry on").
10. **No limit on saved runs**; when the browser refuses to save, a red warning that stands out (section 7, "The warning"; [stated] 2026-11-24, after the mockup: "Please make the "storage full" message into an actual warning that stands out.").
11. **Opening Mass on a connection that has an unfinished saved run resumes it** (the newest, when there are two); the Saved runs list is one press away.
12. **Mockup: yes** (sent).
13. **A ship lost** (2026-11-25, section 6b): a Ship lost button in the pinned line; if the ship jumped first, its step is answered first, then it's marked lost; lost before jumping, it's marked lost without an answer (the step wasn't made); lost part way through a group step, it leaves the step and the rest waits for its answer; its pod, lost on the far side, can come home as a step of its own; a replacement is a ship added mid-run with its side asked; a lost finisher isn't offered again unless one is added.

## 4. The odds (in `hmNext`)

Every candidate gets `risk` (as today), `stuck` and `col = risk − stuck`:
- **Everyone on the finish side, a group going out** (ships back lightest first, `mb` the heaviest of their ways back, `all` = out + every way back): Crit `risk = share(all)`, `stuck = share(all − mb)`; Roll `risk = stuck = share(all − mb)` (today's number).
- **Ships coming in:** all of them and Roll: `risk = stuck = share(pre)` (pre = the group less its heaviest, today's); all of them and Crit: `risk = share(m)`, `stuck = share(pre)`; part of them: `risk = stuck = share(m)` (closing on the last of the group strands the rest).
- **The pick:** risky groups by `stuck`, then `risk`, then the lighter group (Crit); the "faster" alternative (LESSON #178) sorts the same way. The step carries `lastIn`, the ship whose jump in would close it (going out: the group's ship with the heaviest way back; coming in: the heaviest).
- **Words** (one helper for the three notes): stuck part `"<odds> that it closes with <who> stuck in <the side you don't finish on>"`; gone part `"<odds> that it closes on <lastIn>'s jump in: everyone's home, but the hole is gone, not crit"`; joined with "; ". What's next: "(risky: about 1 in 47 stuck, 95% gone, not crit)". `hmRiskTxt` unchanged ("N%" from 50 %, else "about 1 in N").
- Checks the sum: `stuck + col` equals today's number for every step (the mockup checks it).

## 5. The safe mass

- Going out with everyone home: Crit `safe = Rmin / 2` ("A ship under 90,000 t (cold out and back) would be safe"); Roll `safe = Rmin` (its way back may close the hole). Rounded down to 100 t as today.
- When no finisher is offered: "… would be safe: add one with + Finisher."; the "No safe step left" note says "add one with + Finisher" (not Change).
- Coming in: no safe-mass sentence (only the ships that are out can make that trip).

## 6. + Finisher (the add row)

- In the pinned line: Undo · + Finisher · Change · Start over. + Finisher is off after the end of a run and at 5 ships (title "5 ships at most"); `aria-expanded` while its row is open.
- The row (`role="group"`, "Add a finisher"): the same ship picker as a setup row (Your fits, or Type a hull… with the hull list), its masses line (and "only … fits this hole" / "too heavy"), "It's in" (finish side picked), the line "It waits for the end like any finisher: you're offered it when the bigger ships have no safe trip.", Add (`.mys-primary`, off until its masses are known and one mode fits the hole) and Cancel.
- Add puts an `add` entry in the run's log (section 7) and the row into the setup's ship list (`tvWhMass`, with `fin`), so Change shows it. Undo takes both back.
- The setup row's tick reads "Finisher: kept for the end, offered when it's the safe choice" (today's "waits until the hole is under 10%" isn't true for Crit).
- Change → Carry on keeps working; a ship new to the list there **asks its side**: its setup row gets "It's in [<finish system> (where you finish) | <other system>]", the finish side picked (today it always starts on 'this' side). That is how a replacement for a lost ship is added ([stated] "just ask which system it's being added in"); the log's `carry` entry keeps it as `at0`. A ship new to the list is never matched to a lost ship or a pod of the same name.

## 6b. A ship lost (added 2026-11-25)

- **Ship lost**, in the pinned line: Undo · + Finisher · **Ship lost** · Change · Start over. Off after the end of a run and when no ship is left; `aria-expanded` while its row is open; opening it closes the + Finisher row and the other way round.
- **The row** (`role="group"`, "A ship was lost", the + Finisher row's look): "Which one [Pick the ship | Megathron · in J122515 · in this step | Megathron · in J122515 · in this step | Thorax (finisher) · in J101524]" (each ship not yet lost, with its side and whether it's in the step shown); Mark lost (`.mys-primary`, off until a ship is picked, and while the pod's mass is being worked out) and Cancel. Then, depending on the ship picked:
  - **In the step shown:** "It's in this step. If it jumped before it was lost, answer the step first, then mark it lost." (the owner's order: the answer counts its mass and moves it, then Lost takes it out).
  - **In a group step with others:** "The others in this step [jumped: wait for Show Info | didn't jump: a new step]", jumped picked (the owner: "sounds good to me" to the step keeping only the ships that jumped). Jumped: the step stays, without the lost ship, and waits for its answer (its mass is only theirs; a note under the step: "Part of this step: a ship in it was lost before it jumped, so only the ships that jumped are counted. Show Info on the hole, as for any step."). Didn't jump, or no one else in the step: the step wasn't made and the next one is worked out with the ships left.
  - **Off the finish side** (not a pod): "Its pod [comes home through the hole | doesn't (a clone jump, or it stays)]", comes home picked; then "The pod (N t) gets a step of its own, home." The pod is a ship in the run named "<ship>'s pod", one mode (its mass from CCP's type data for the Capsule through `hmHullModes('Capsule')`, as any typed hull: the capsule has no rig size, so no MWD mode), on the lost ship's side, with the lost ship's polarization times (UNVERIFIED: polarization per pilot, Sources). Its step is drawn like any other ("Megathron's pod in cold · J122515 → J101524 · N t"); once home it leaves the run ("Megathron's pod (home)" in the pinned line) and is never picked for a trip out.
- **Marked lost:** the ship stays in the run's list as "<ship> (lost)" (so the log's ship numbers stay right) and takes no part in any step, odds, safe mass, "Send X instead" or "stranded"; its setup row is removed (so Change doesn't bring it back; Undo puts it back). A lost finisher isn't offered again; the notes then say "add one with + Finisher" ([stated] "losing the finisher means finishing the session without it unless replaced."). Every ship lost: "No ships left: add one with + Finisher, or with Change."
- **The log:** `{t: 'lost', i, at, part, d, pod, row, rowAt}`: `part` = the ships of the step kept for their answer (`[[ship index, mode key], …]`, empty when the step wasn't made; only when the lost ship was in the step shown), `d` its direction, `pod` = the pod's ship (name, label, its one mode, a snapshot like an added ship), `row` / `rowAt` = the setup row removed. Replay sets `lost`, holds the part step (`pl.part`, cleared by the next answer), adds the pod. A part step is stored, not worked out again, since the step shown depends on the time (polarization).
- **A replacement:** a ship added mid-run with its side asked: the + Finisher row ("It's in") or Change → + Ship → Carry on (section 6: the new row asks "It's in").
- **`hmApply`** leaves lost ships out of "stranded" and moves a pod that reaches the finish side out of the run; **`hmDoneTxt`** leaves them out of "closed with … on the other side"; **`hmNext`** works only with ships not lost and returns the held part step as it is (risk 0: it has already jumped).

## 7. Saved runs

**Storage:** a new key `tvWhMassRuns` = `{v: 1, runs: [...]}`; `tvWhMass` unchanged. A run:
`{id, made, upd, link: <whLinkKey or ''>, mass0: <the connection's Mass at the start>, here: {id, name}, there: {id, name}, code, st0: <what it said at the start>, goal, fin: 'this'|'other' (relative to here), ships: [{name, label, est, fin, modes: [{k, lab, m}]}], rows: <the setup rows>, log: [...], done, obs, n}`.
- **The log, not the state:** `{t: 's', g: [[ship index, mode key], …], d: 'out'|'back', a: <answer>, at: <time>}` per answered step; `{t: 'add', ship, at: 'this'|'other', row}`; `{t: 'free', i}` (Send X instead); `{t: 'carry', ships}` (Change → Carry on; a new ship carries `at0`, its side); `{t: 'lost', i, at, part?, d?, pod?, row?, rowAt?}` (a ship lost, section 6b). Loading replays it from `st0` with `hmApply` (sides, polarization times, the possible holes and the steps list come back exactly; the mockup checks replay = live). A run is about 1–4 KB (the mockup's after three answers: under 4,000 characters), so no limit is needed. The masses are a snapshot: a saved fit changed or deleted later doesn't change a run under way.
- **here / there are system ids,** so reopening from the other end keeps the sides and names right.
- **When it saves:** after every change listed in decision 8 (`rrSave`: `upd`, `done`, `obs`, `n` refreshed, then the whole key written). A write the browser refuses (it throws `QuotaExceededError`, Sources) sets the warning line until the next save works.
- **The warning** (WH-01): the page's warning row (`.sa-warn`: the red "!" badge `.ewar-badge.danger`, one bold line `.warn-title`, one context line `ctxHtml`, subtext rule 3) in a red box (danger border and tint, like `.mys-confirm`), `role="alert"`, **inside the pinned line** so it stays in view while the steps scroll (at the top of the setup when no run is shown). Bold line: "This run isn't saved"; context line (40 characters, `CTX_MAX`): "Storage full: delete a saved run (WH-01)"; on hover the whole sentence: "This browser's storage is full, so this run will be lost if you leave or reload the page. Delete a saved run you don't need and this one is saved again. (WH-01)". Deleting another run tries the open run's save again at once, so the warning goes by itself when there's room.
- **WH-01 in `ERROR_CODES`** (new prefix; `tools/gen_errors_md.py` gets the group name "Wormholes tab"; ERRORS.md regenerated): title "A Mass run couldn't be saved"; where "{card:whmap} tab, the Mass panel (Crit or roll a hole)"; trigger "An answer, Undo, an added finisher or another change to a run, when the browser refused to keep it (its storage for this site is full). The run works until the page is closed."; check "Delete a saved run you don't need in Saved runs (the open run is then saved again), or free some of this site's storage."; why: the owner's two quotes (the lost run, and "make the "storage full" message into an actual warning that stands out"). INTEL-11 (a sov list couldn't be saved) is the same kind of error, shown as amber text; this one is a box because losing a run mid-roll costs more (the owner's call).
- **Undo** pops the last log entry and replays; the connection's Mass follows (the last answer left, or `mass0` with none). Undoing a `lost` puts its setup row back where it was (`row`, `rowAt`).
- **Start over** (asks first while steps were made, as today) clears that run's log and keeps it in the list until Show the steps reuses it. After the end of a run, Start over leaves the finished run as it is and Show the steps makes a new one. Show the steps on a different hole or "It says now" (Change, then changing those) makes a new run; the old one stays.
- **Opening Mass:** the newest unfinished run on one of the focus system's connections is opened; otherwise the setup as today. A run on another connection is no longer dropped: it's in the list.
- **The list:** "Saved runs (N)" with the page's chevron toggle (`it-whp-xb` + `IT_CHEV`, like What's next): open in the setup, folded while a run is shown. One row per run, newest first: "D382 · J101524 ↔ J102057 · crit · 5 steps · says less than 50% · 11:15" (finished: "rolled", "crit", "closed, ships stuck", "closed, not crit"; another day: "Nov 23 11:15"), with Open (or "open" for the run shown) and Delete. Delete asks first (`whAskHtml`): "Delete the saved run H296 · J101524 ↔ J122515? Its 2 steps are forgotten." [Delete] [Keep it].
- **A finished run** stays until deleted; its end note gets "Delete this run" (the same question).
- **A connection removed** later: the run stays, named by its systems; answers no longer set a Mass.
- **Two tabs:** each reads the latest copy when the panel opens and on the `storage` event (fired in the other tabs, not the one that wrote: Sources); the last change wins.
- **Safe both ways** (README "Stored browser data"): the older page never reads `tvWhMassRuns`; `tvWhMass` keeps its form (a 5th row is ignored by the older page's `hmRead`, which takes 4).

## 8. The words that change (all in the mockup)

- "No fully safe jump: about 1 in 131 that it closes with Megathron stuck in J102057; about 1 in 4 that it closes on Megathron's jump in: everyone's home, but the hole is gone, not crit. A ship under 90,000 t (cold out and back) would be safe. Thorax, Buzzard (finishers) are kept for the end. [Send Buzzard instead: safe, about 5–80+ steps, …] [Send Thorax instead: safe, …]"
- Roll: "No fully safe jump: about 1 in 30 that it closes with Megathron stuck in Rens. A ship under 186,200 t would be safe: add one with + Finisher."
- "No safe step left with these ships: the next jump out would close the hole with Megathron stuck in J102057." / "… can do the last trip safely: add one with + Finisher. Or leave it here: …"
- Ship lost: "A ship was lost" · "Which one" · "It's in this step. If it jumped before it was lost, answer the step first, then mark it lost." · "The others in this step: jumped: wait for Show Info / didn't jump: a new step" · "Its pod: comes home through the hole / doesn't (a clone jump, or it stays)" · "The pod (30 t) gets a step of its own, home." (the mockup's made-up pod mass) · "Part of this step: a ship in it was lost before it jumped, so only the ships that jumped are counted. Show Info on the hole, as for any step." · "No ships left: add one with + Finisher, or with Change." · pinned line "Megathron (lost)", "Megathron's pod (home)".
- "Safe but slow" button: "Send Megathron out cold instead (about 1 in N stuck); …"; "Faster, not safe:" + the split words.

## 9. UI rules it touches

- **One close button, one chevron:** the list uses the page's chevron toggle; no new close (Delete is a text button).
- **Warning rows** (subtext rule 3, `check_subtext.py`): the WH-01 warning is one bold line and one context line within `CTX_MAX`, the rest on hover; it carries its code (every error shown does: ERRORS.md).
- **Ask before forgetting** (059's `whAskHtml`): Delete and Start over ask; Undo doesn't (nothing is lost).
- **Phone / 44 px:** every new button is 44 px under 600 px. **Decided:** with four buttons the pinned line wraps to a 2 × 2 grid on a phone (as in the mockup), one row taller than today's single row. The other choice was + Finisher moved under the step; [stated] "your choice on the phone question": the research session picked the 2 × 2 grid, so + Finisher stays with the other run controls, as on a wide screen. **With Ship lost (2026-11-25) there are five:** a 3-column grid on a phone (two rows, as tall as the 2 × 2; labels on one line, 4 px side padding), and on a wide screen the button group may wrap (`.hm-sum .hm-sb` today is `flex:none`, so a fifth button ran past the panel's edge at 1440 px: it becomes `flex:0 1 auto; max-width:100%`). Both checked in the mockup.
- **No sideways scroll** at 390 px (checked); the panel's buttons stay inside it (checked).
- **Subtext:** the add row's one-line note is short; the rest is in the ⓘ.
- **Colour tokens only;** drawing cost: no timers added (the polarization repaint is 070's).
- **Page size:** about +9 KB of script with Ship lost (the mockup's prototype is 38 KB with its comments and the mock-only parts); well under the served ceiling (671,280 of 800,000 at a02d876).

## 10. Info text it touches

`CARD_INFO['whmap#mass']` (207 words today; cap 210, `INFO_ALL_MAX`). New wording (208 words, in the mockup; reworded 2026-11-25 to make room for Ship lost):
- "Works out, step by step, how to crit a hole (under 10%) or roll it (close it) with your ships, leaving everyone on the side you choose." (was "how to bring a hole under 10% (crit) or close it (roll) with the ships you pick")
- "[The numbers] Each type's total mass and mass per jump are CCP's; a new hole's total is within ±10% of it." (drops "the steps keep every total that fits what Show Info said", which is how it's built)
- "[In, out, hot, cold] Out is toward the side you don't finish on; in, toward the side you do. Mass counts as you press jump: hot is the MWD (or AB) on, cold off. Ships that can jump together are one step, then one look at Show Info. + Finisher adds a light ship, kept for the end." (was "Out is a jump to the side you don't want to finish on; in, to the side you do. The hole takes your ship's mass as you press jump: hot is the MWD (or AB) running, cold is off." and "a finisher waits until the hole says less than 10%")
- "[Safety] A jump that could close the hole is shown only when everyone then ends on your side. Otherwise you see the odds of a ship stuck on the far side and, for a crit, of the hole closing on the way home. A safe plan over 30 minutes also offers a faster risky jump. Polarization: no ship jumps the same way twice within 5 minutes."
- new "[Ship lost] If it jumped, answer first; its pod can get a step home."
- new "[Saved runs] Kept in this browser until you delete them."
- The ship row's tick label (section 6). `whmap` itself: no change. The Intel example: not touched.

## 11. Checks (for the build)

`tools/page_checks/wormhole_mass_check.py` grows:
- **Split:** for every step of its replays, `stuck + col` = the old number; Roll steps have `col = 0`; a Crit case where both are > 0 and one where only the collapse can happen; the words name the far side. Mutant: one share for both.
- **Stuck first:** a Crit position where the least total risk and the least stuck differ: the step is the least stuck. Mutant: sort by total.
- **Safe mass:** Crit out = Rmin / 2 (rounded), Roll out = Rmin, coming in: no sentence; never "No ship is light enough" beside a safe "Send X instead". Mutant: today's formula.
- **+ Finisher:** the row, its side default, Add off until masses, the log entry, the run's next step, Undo removes it; 5 ships at most. Mutant: a new ship always on 'this' side.
- **Per finisher:** two finishers → two buttons, lightest first; one sent frees only it. Mutant: one button frees all.
- **Saved runs:** replay = live (holes, answer, steps, sides, polarization) after random answers; reload resumes at the same step with Undo working; Undo past an add and a Carry on; Delete asks, Keep it keeps; a finished run stays; storage refused → the WH-01 box (red border, badge, code, inside the pinned line, still in view with the steps scrolled to the end), and deleting another run saves the open one and takes the warning away; the older `tvWhMass` reader still reads a 5-row list (first 4). Mutants: no save after an answer; Undo stops at Carry on.
- **The label:** "mass mass" never appears in the connection list.
- **A ship lost:** the row lists the ships not lost with their side and "in this step"; Mark lost off until one is picked; lost alone in its step on the finish side: no other question, the log entry, "(lost)", the next step doesn't use it, the setup list loses it, Undo puts both back; lost in a group step on the far side: both questions; "jumped" keeps the step with only the others (its mass theirs) and the note; answering it, the pod's step home; the pod home leaves the run; replay = live (ships, lost, sides, polarization, holes); Undo back to the part step; the last ship of a part step lost: the step wasn't made; a lost finisher: no "Send X instead", "add one with + Finisher"; every ship lost: "No ships left" and Ship lost off; a replacement added on Change while a run goes on asks its side and is carried on there, never matched to the lost ship; no page errors; the five buttons inside the panel at 1440 and 390 px. Mutants: a lost ship still in steps; the part step worked out again (all of the group counted); the pod left out; a new ship on Carry on always on the finish side; a new ship matched to a lost one of the same name.
- Timing: the panel's redraw with 5 ships and 3 finishers, reported in the pull request.
- Hand test: a real roll or crit in game: check the two numbers' meaning against what happens; leave mid-run with the browser's back button and come back; two saved runs at once; a Buzzard added at "less than 50%"; a ship lost (or one marked lost as a stand-in) after its jump and before it, with its pod coming home; the pod's mass shown against the Capsule's in game.

## 12. CCP's DLA

Your own runs, kept in this browser only; nothing sent anywhere. No clause touched (checked against `claude/reference/dla-planning-notes.md`'s list: no other players' data, no login, no requests).

## 13. Reuse, don't add (mockup piece → the page's)

| Mockup piece | Use in the build |
|---|---|
| `.hm-addf` box | the + Add form's `.wh-pop .wh-addf` grid where it fits, with `.hm-ship` for the picker (as the setup rows) |
| `.hm-runs` list, `.hm-rb` | first try My Fits' list (`.mys-list` / `.mys-row`); new on purpose only if those don't sit in the popover (no Wormholes list has per-row Open / Delete) |
| `.hm-end-acts` | `.wh-acts` |
| the WH-01 warning | `.sa-warn` + `.ewar-badge.danger` + `.warn-title` + `ctxHtml` (as the System Analyzer's warnings); the red box: `.mys-confirm`'s border and tint, as one shared rule rather than a second copy (`.hm-full` is the mockup's) |
| the phone 2 × 2 `.hm-sum .hm-sb` grid | a rule on the existing `.hm-sum .hm-sb` under 600 px |
| `rrDelAskHtml` | `whAskHtml` (as used) |
| the chevron toggle | `it-whp-xb` + `IT_CHEV` (as What's next) |
| `hmShipOf` copy | edit the page's own (one condition: the add row or the lost row open) |
| the Ship lost row | the + Finisher row's box (whatever the build uses for it), `whOptsHtml` selects in `.wh-lnk wide` labels, `.wh-acts`, `.mys-primary` |
| `.hm-sum .hm-sb` five buttons | the existing rule changed (`flex:0 1 auto; max-width:100%`), and under 600 px 3 columns with `padding-inline:4px; white-space:nowrap` on its buttons: no new class |
| the "It's in" select on a new setup row | the + Finisher row's "It's in" select (`whOptsHtml`) |
| `hmApply` / `hmDoneTxt` / `hmStepHtml` copies | edit the page's in place (lost ships left out, the part step, the pod home) |
| `hmNext` / notes copies | edit the page's functions in place; one words helper for the three notes |

## 14. Mockup shortcuts not to copy

See `claude/roadmap/hole-mass-runs-mockup/README.md`: page functions replaced by name instead of edited; made-up fits and hull masses; `itSysName` wrapped for Rens; the MOCKUP bar and scenes; the storage-full scene replaces `Storage.prototype.setItem`.

## Sources

Ship lost (2026-11-25): the pod's mass is CCP's type data for the Capsule (type 670, in the page's `INTEL_SHIPS`), read at run time through `getType` as for any typed hull, so no number is written here; the mockup's 30 t is made up.

| Fact | Source | Checked | Status |
|---|---|---|---|
| `localStorage.setItem` throws a QuotaExceededError when the value can't be stored | WHATWG HTML Living Standard, Web storage (https://html.spec.whatwg.org/multipage/webstorage.html), the standard itself, not a secondary source | 2026-11-24 | verified |
| The `storage` event fires in the other same-origin documents, not in the one that made the change | WHATWG HTML Living Standard, Web storage (https://html.spec.whatwg.org/multipage/webstorage.html), its "broadcast" steps: every Storage object except the one that changed | 2026-11-24 | verified |
| A jump that empties a hole still goes through; the hole closes behind that ship (the "gone, not crit" case) | Secondary: EVE University, as in 070's plan (`roadmap/hole-mass-plan.md` Sources) | 2026-11-22 | UNVERIFIED: the owner confirms from experience at the hand test |
| Show Info's three mass states, ±10% total, polarization 5 minutes | 070's plan Sources (secondary, UNVERIFIED there) | 2026-11-22 | UNVERIFIED: 070's hand test rows still to check in game |
| A ship destroyed leaves its pilot in a pod in the same system, and a pod can jump through a wormhole (adding its own mass) | No source read (no CCP page opened in this session) | 2026-11-25 | UNVERIFIED: the owner confirms at the hand test (a pod coming home through a hole, its mass shown) |
| Polarization is per pilot, so a pod keeps the lost ship's polarization times | No source read (a cautious choice: at worst the pod waits when it needn't) | 2026-11-25 | UNVERIFIED: the hand test (a pod jumping back within 5 minutes of its ship's jump the same way) |

## Built (2026-11-25, v2026.11.25.1, branch `072-hole-mass-runs`)

Reviewed against main 73ac137 (v2026.11.24.2; 042 hadn't touched the Mass code, only moved it about 58 lines). check_plan_sources: 0 problems, the 4 UNVERIFIED rows in the hand test; the two verified rows reopened in the WHATWG standard on 2026-11-25.

- **Two additions at the review** (the owner: "go"): (1) a save reads the stored list first and replaces only its own run by id (`hmRunSave`), so "the last change wins" per run and two tabs never drop each other's runs; (2) the `carry` log entry keeps the setup rows from before Carry on (`rows0`) and Undo puts them back, as `add` (`row`, `rowAt`) and `lost` do.
- **Names:** the mockup's `rr…` functions are the page's `hmRun…` (`hmRunsRead`, `hmRunsWrite`, `hmRunSave`, `hmRunShip`, `hmRunPl`, `hmRunApply`, `hmRunLoad`, `hmRunDel`, `hmRunsHtml`, `hmRunLabel`, `hmRunDelAskHtml`), plus `hmAddFin`, `hmLost`, `hmAddFHtml`, `hmLostHtml`, `hmErrHtml`, `hmRowShips`, `hmRowOnly`, `hmAtHtml`, `hmSideSelHtml`, `hmFarSide`, `hmRiskWords`, `hmRiskShort`, `hmSafeTxt`; 070's `hmMark` and `H.back` are gone (the log is the undo).
- **A run's ships carry `rk`** (their setup row's `hmKey`), so Ship lost finds its row by key, not by working out the row's masses again (the mockup matched labels through `hmShipOf`, which returns nothing until the masses are known after a reload). A pod has none.
- **A typed hole's run stays open** when Mass is closed and opened again (`hmOpen`: `!H.run.link`); 070 dropped it, and the mockup still did.
- **After a reload nothing is in focus** until a system is picked (the map then falls back to its first system), so a run resumes on opening Mass only once its system is in focus, as planned ("on one of the focus system's connections"); the Saved runs list is open in the setup, one press away. The check picks the system first.
- **CSS (Reuse, don't add):** WH-01 is the page's `.sa-warn` row; its box shares `.mys-confirm`'s danger border and tint in one rule (`.mys-confirm, .hm-pop .sa-warn`), so no `.hm-full`. The + Finisher and Ship lost rows are the setup's own `.wh-addf.hm-f` grid with one new class, `.hm-x` (its border and panel fill, so the row reads as one group between the pinned line and the steps). Saved runs is `.hm-runs`, new on purpose (My Fits' `.mys-row` is built around one main button and doesn't wrap a text line with Open / Delete); its buttons sit in `.wh-acts`. The end note's Delete is in `.wh-acts` (no `.hm-end-acts`). The phone grid and the wide wrap are rules on the existing `.hm-sum .hm-sb`; the 44 px rule gains `.hm-pop .wh-note button`.
- **Stuck first only changes the faster offer** (found at the build, section 11's "Stuck first" case): for the step chosen, the lightest ship alone, cold, has both the least total and the least stuck share (its out and back are both its lightest mode, and every other group carries at least that), so ranking by stuck or by the total picks the same step. Where they differ is the faster jump offered beside a slow safe plan (only groups at least twice as heavy as the safe step): on a made-up N766 at less than 50% with a Hauler, a Megathron and a Brick, stuck first offers 196,800 t (0.77% stuck, 25% in all) where the total would offer 190,000 t (0.86% stuck, 13% in all). The check tests that case; its mutant sorts the faster offer by the total.
- **Timing:** the panel's redraw with 5 ships and 3 finishers is 224 ms in headless Chromium (the mockup's 230 ms).
- **Also in this delivery:** the Wormholes tab's Beta tag removed (the owner, 2026-11-24: "remove "beta" tag from wormholes tab."; moved here from 068 / 069 on 2026-11-25).
