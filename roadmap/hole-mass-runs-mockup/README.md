# Mass panel: saved runs, + Finisher, split odds — mockup

Plan: claude/roadmap/hole-mass-runs-plan.md. Built 2026-11-24 from main a02d876 (v2026.11.24.1) and sent to the owner as hole_mass_runs_mockup.html; Ship lost added 2026-11-25 (plan section 6b) and re-sent.

Files:
- build_rr.py: `python3 -I build_rr.py <a02d876's index.html> hole_mass_runs_mockup.html` (a CSP with no network; appends proto_rr.js and boot_rr.js).
- proto_rr.js: the prototype, after the page's own script. Replaces by name: `hmNext` (odds split, stuck first, safe mass, a finisher freed per ship), the three notes and What's next (`hmRiskHtml`, `hmFinAltHtml`, `hmSlowHtml`, `hmFastHtml`, `hmBranchesHtml`), `hmStepsBodyHtml` (no-safe-step note, Delete this run), `hmSumHtml` (+ Finisher), `hmPanelHtml` (the add row, Saved runs), `hmGo` / `hmSay` / `hmUndo` / `hmReset` / `hmOpen` (the saved log), `hmClick` / `hmChange` (new buttons and fields), `hmShipOf` (repaint for the add row), `hmLinksHtml` (the "mass mass" label), `hmShipRowHtml` (the Finisher label), `hmAddBtnHtml` (5 ships), `hmApply` / `hmDoneTxt` / `hmStepHtml` (lost ships, the part step, the pod home); adds `rrLostHtml` / `rrLost` (Ship lost), the "It's in" select on a ship added on Change while a run goes on, and `rrRead` / `rrWrite` / `rrSave` / `rrPl` / `rrApply` / `rrLoad` / `rrDel` / `rrAddF` and `tvWhMassRuns`; `CARD_INFO['whmap#mass']` (208 words).
- boot_rr.js: seeds a made-up chain (CCP's own wormhole systems picked by class: a C2 home with a B274 to Rens, a K162 from a C3 whose far side is a D382 at less than 50%, a K162 from a C5 whose far side is an H296), made-up saved fits (Megathron "Higgs roller" 296,800 / 196,800 t, Thorax "Finisher" 16,300 / 11,300 t) and hull masses (Buzzard, Heron, and a 30 t Capsule for the pod: made up), opens the Wormholes tab and the Mass panel, and shows the MOCKUP bar (scenes: Crit, no safe jump; + Finisher; Two finishers; Undo the add; Roll, risky; Saved runs; Saved runs (in a run); Delete a run; Finished run; Storage full; Ship lost; Lost in a group step; Part of a step + pod; Replacement ship; Finisher lost; Reload the page).
- test_rr.py: `python3 -I test_rr.py hole_mass_runs_mockup.html [shots dir]` (Playwright with the system Chrome, no network; 1440 and 390 px; 143 checks, including a real page reload that resumes the run, replay = live, the WH-01 storage warning, and a ship lost alone, part way through a group step with its pod coming home, the finisher lost and a replacement on the far side).

Shortcuts not to copy into the build:
- Page functions are replaced by name (`window.hmNext = …`); the build edits them in place, with one words helper for the three notes.
- `FITS` / `HULLS` stand in for My Fits and `getType` (ESI): invented masses. The build keeps 070's `hmFitModes` / `hmHullModes`.
- `itSysName` is wrapped to name Rens without ESI.
- The Storage full scene replaces `Storage.prototype.setItem` with a fake limit (today's size), so a bigger save fails and deleting the other run makes room; the build catches the real error in its one save helper.
- The new CSS (`.hm-runs`, `.hm-addf`, `.hm-end-acts`, the phone grid on `.hm-sum .hm-sb`) is the mockup's; the plan's "Reuse, don't add" table says what to use instead.
- The Capsule's 30 t is invented; the build gets the pod's mass from CCP's type data (`hmHullModes('Capsule')`).
- The reload scene sets a sessionStorage flag so the boot doesn't wipe the saved runs; the page has no such flag.

check_pii (names list copied in, fingerprint matched): 0 problems besides the page's own EVE login button (already in tools/pii_reviewed_images.json).

Built 2026-11-25 as build queue 072 (v2026.11.25.1): the mockup is `Claude outputs/hole_mass_runs_mockup.html`, rebuilt from these files against a02d876's index.html; the page's own code is in index.html's Mass block (the `hm…` functions, plan's Built notes).
