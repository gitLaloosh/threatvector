# Mass (crit or roll a hole) mockup

Plan: claude/roadmap/hole-mass-plan.md. Built 2026-11-22 from main 4c28fdd (v2026.11.22.1) and sent to the owner as hole_mass_mockup.html.

Files:
- build_hm.py: `python3 -I build_hm.py <4c28fdd's index.html> hole_mass_mockup.html` (puts in a CSP with no network, appends proto_hm.js and boot_hm.js).
- proto_hm.js: the prototype, appended after the page's own script: the Mass button and panel, the calculation (`hmPoss`, `hmNext` with groups of ships, `hmApply`,
  `hmPreview`), the step words (in / out by the finish side, hot / cold), the steps, the write-back to the connection, `CARD_INFO.whmass` and the `whmap` clause, the phone toolbar wrap (Q11).
- boot_hm.js: seeds a made-up chain (CCP's own wormhole systems picked by class: a C2 home with a B274 to Rens, a K162 from a C3 whose far
  side D382 is known, a K162 from a C5 whose far side isn't), opens the Wormholes tab and the panel, and shows the MOCKUP bar (scenes: Panel,
  Steps, After 3 jumps, Polarized, 2 Megathrons + Phobos, … after 3 steps, Phobos as finisher, … after 5 steps, Heron as finisher <50%, No safe jump, K162 asks, Crit it, Finish on the other side, Add a ship mid-way, Carry on, Typed hull, Rolled; Undo and Start over are in every scene with steps).
- test_hm.py: `python3 -I test_hm.py hole_mass_mockup.html [shots dir]` (Playwright with the system Chrome, no network; 1440 and 390 px; 123 checks).

Shortcuts not to copy into the build:
- `HM_FITS` stands in for My Ships: three made-up saved fits with their masses typed in (the Finisher tick is the row's `fin`) (Megathron with a Higgs Anchor, Phobos with a Higgs Anchor
  and a ZPME, Heron). The build reads each fit's masses from the page's fit maths (`pyfaShipSpeed` → the fit's new `mass` field; the ZPME mode
  by recomputing with its state on).
- `HM_HULLS` stands in for `getType` (ESI): ten hulls' mass and rigSize from CCP's SDE (pyfa v2.70.1). The build uses `getType` and `INTEL_SHIPS`.
- `whShellHtml`, `whPop` and `itSysName` are wrapped, and `CARD_INFO` / `CARD_NAMES` patched at load; `itSysName` only to name Rens without ESI.
- The panel's state is one object (`HM`), and its clicks and changes are caught with capture listeners on the document; the build uses `whS`
  and the Wormholes tab's own delegated handler.
- The answers' colours are inline styles; the build uses classes on the connection list's mass colours.
- The connection removal is written out here; the build calls the connection list's delete (one helper for both).

check_pii (names list copied in, fingerprint matched): 0 problems on the first build; the one embedded image is the reviewed EVE login button. Undo and Start over were added after it (code and button words only): run it again when the mockup goes into the repo.

Built (build queue 070, v2026.11.23.2, 2026-11-23): the mockup kept as sent (`Claude outputs/hole_mass_mockup.html`, built from 4c28fdd with these
files). The build differs from it where the plan's "Built" notes say: the holes still possible are boxes, not points (LESSON #177), so a few
numbers in its scenes (step counts, the safe mass) differ slightly from the page's.
