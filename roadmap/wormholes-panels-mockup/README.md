# Wormholes panels mockup

Plan: roadmap/wormholes-panels-plan.md (build queue 056). Built first from main e7f5a2b (v2026.11.15.3) and sent to the owner as wormholes_panels_mockup.html, 2026-11-15; rebuilt at the build from main 42b016f (v2026.11.16.6), where its 68 checks still pass, and committed as `Claude outputs/wormholes_panels_mockup.html`. It needs a page from before 056 (it moves the old stacked panels' System body into its own panel); on 056's page and later the real panel is the design.

Files:
- proto_whp.js: the prototype, appended after the page's own script. Seeds a made-up chain once (wormhole systems picked by position from the page's own INTEL_WH table, made-up statics, a note, a home mark and a warning; no pilots or groups), opens the Wormholes tab, and in "Proposed" moves System's body into a rule-B panel behind one rail button at the map's top left (`.it-map-rail.wh-rail`), remembered in `tvWhPanels`. Wraps the page's `whPanels`, `whFree` and `whSelect` (classic-script globals) so the button follows the focus, Fit uses the uncovered part, and a click on a system opens System. The MOCKUP bar: Today / Proposed, icon A / B / C, Reset, – to fold.
- build_whp.py: `python3 -I build_whp.py <repo>/index.html proto_whp.js wormholes_panels_mockup.html` (takes the page's CSP out; tests use bypass_csp too).
- test_whp.py: `python3 -I test_whp.py wormholes_panels_mockup.html` (Playwright, no network; 1440, 760 and 390 px; 68 checks).
- snap_whp.py: `python3 -I snap_whp.py wormholes_panels_mockup.html <out dir>` (screenshots shut / open / today at 1440 and 390).
