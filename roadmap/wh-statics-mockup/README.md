# Statics on entry mockup

Plan: roadmap/wh-statics-plan.md (build queue 061). Built from main 513c1e6 (v2026.11.18.1) and sent to the owner as wh_statics_mockup.html, 2026-11-19;
rebuilt the same day by the build session into `Claude outputs/wh_statics_mockup.html` from 513c1e6's page (pyfa e5483f8, the manifest's commit:
CCP's numbers match b79cd90's for every wormhole type).

Files:
- gen_data_stc.py: writes data_stc.js (not kept: regenerate it): Wanderer's real statics by system ID (wanderer-industries/wanderer
  priv/repo/data/wormholeSystems.json at 4d4a035, MIT) and CCP's wormhole types' lifetime and masses (pyfa's SDE dump).
  `PYFA_SRC=<pyfa checkout> python3 -I gen_data_stc.py data_stc.js` (it reads Wanderer's file from /home/claude/ext/wanderer: edit the path).
- proto_stc.js: the prototype, appended after the page's own script. Wraps whStcHtml, whStcsHtml, whSumHtml, whDraw and whCnEditHtml;
  seeds a made-up chain (CCP's own wormhole systems picked by position; one with statics typed by you). A bar switches Today / Proposed.
- build_stc.py: `python3 -I build_stc.py <513c1e6's index.html> data_stc.js proto_stc.js wh_statics_mockup.html` (takes the page's CSP out).
  The prototype wraps 513c1e6's functions; on a page with 061 built it would wrap the built ones.
- test_stc.py: `python3 -I test_stc.py wh_statics_mockup.html [shots dir]` (Playwright, no network; 1440 and 390 px; 30 checks).

check_pii (names list copied in, fingerprint matched): 0 problems; the one embedded image is the reviewed EVE login button.
