# Intel map Home mockup

Plan: roadmap/intel-home-plan.md (build queue 071). Built 2026-11-23 from main de2f9d2 (v2026.11.23.1) and sent to the owner as home_mockup.html;
rebuilt from these scripts at the build (v2026.11.23.3) into `Claude outputs/home_mockup.html`.

Files:
- build_ho.py: `python3 -I build_ho.py <de2f9d2's index.html> home_mockup.html`. Reads mock.js beside it: copy the repo's
  roadmap/paths-to-you-mockup/mock.js there (unchanged; not kept in this folder) for the made-up Intel around C-J6MT, puts in a CSP with no network, adds hooks to the page's own code
  (each found once: the hover's line, the legend, the kept routes' set, the kept route's colour and solid line, the house drawn before your pin), and
  appends proto_ho.js and boot_ho.js.
- proto_ho.js: the prototype: `tvHome` storage, `hoDist` (jumps from Home over the graph the map counts on), the hover line, the house
  (`hoHouse`, drawn on the canvas by us), Set as Home / Remove Home in the right-click menu and a phone's tooltip buttons (your own system's
  tooltip on a phone gets the Home button on its own), Show / Hide the route to Home in Home's menu, the top bar's Center on your Home button
  (`hoRailPaint`, `hoCenter`; left of Center on your system, the owner 2026-11-23), the legend's Home entries (`__MKhomeLeg`), the Intel
  [Map] info sentence.
- boot_ho.js: opens Intel with the mock folder and shows the MOCKUP bar. Scenes: Menu: no Home yet, Menu on Home, Home + route, Centered on Home, Hover,
  Zoomed out, You in Home, Phone tooltip. Home is KOG-TA (30000736), 10 jumps by gate from C-J6MT; "You in Home" sets C-J6MT.
- test_ho.py: `python3 -I test_ho.py home_mockup.html [shots dir]` (Playwright with the system Chrome, no network; 1440 and 390 px;
  72 checks). Jumps from Home are checked against a plain search written again in the test.

Shortcuts not to copy into the build:
- `itRpBtnsHtml`, `itRpTipHtml` and `itMapZoomHtml` are wrapped (string replaces); the build writes the button into
  them.
- The clicks are caught with one capture listener on the document; the build uses the map's own delegated handlers (`data-it-rp-*`, the
  top bar's `data-im-z`). `hoCenter` copies `itMapCenter`; the build gives `itMapCenter` an index.
- The hover line, the route set, the route colour and the house are hooks (`window.__MKhome*`) put in by build_ho.py; the build writes them
  into `itMapTip`, the kept routes' set, the route draw and the map draw.
- The Intel example isn't touched here: the build sets Home aside in `itExSandbox` like `itWhSt` and `itRpAside`.
- No `storage` event: the build reloads Home when another tab changes `tvHome`, like `IT_RP_KEY`.

What the build did differently (2026-11-23, the review): the phone's top row and "Hide all routes" (the mockup kept 059's top-left place, which
already covered the + button on a 390 px screen); the route to Home is the house colour even with a report at Home (the mockup coloured it by
the report); the menu's accessible name is the system's name alone. See the plan's Built notes.

check_pii (names list copied in, fingerprint matched): 0 problems on the five scripts and the rebuilt mockup.
