# Jump bridge lines button mockup

Plan: roadmap/wormholes-part3-plan.md, "Built": the jump bridge lines button (build queue 059; the owner: "in 059"). Built from main cb9a995 (v2026.11.17.1) and committed as `Claude outputs/jump_bridge_lines_mockup.html`, 2026-11-17, after the owner's change: "button defaults to on when jump bridges are enabled. no need for the line through it, just shows off state when they're turned off".

Files:
- build_jbt.py: `python3 -I build_jbt.py <repo>/index.html jump_bridge_lines_mockup.html` (the real page with 041's made-up Intel: names, pilots, groups, reports, kills; the mock runtime `mock.js`, a copy of roadmap/paths-to-you-mockup/mock.js; takes the page's CSP out).
- boot_jbt.js: turns Intel on and pastes a made-up bridge list ("Mockup bridge").
- proto_jbt.js: adds the button to the zoom column, under ⌖ (shown only while "Use jump bridges on the map" is on; on by default; pressed off: the green curves and their hover go, the jumps still count bridges, a route's bridge step still drawn; kept in dscanIntel).
- test_jbt.py: `python3 -I test_jbt.py jump_bridge_lines_mockup.html` (Playwright, no network; 1440 and 390 px; 36 checks).

Everyone and every group in it is invented; systems and ship types are EVE's public data. It needs a page from before 059; on 059's page and later the real button is the design.
