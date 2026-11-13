# Wormholes list: Export and Import (mockup, 2026-11-12)

Plan: claude/roadmap/wormholes-export-import-plan.md (all questions answered, not queued). Built from main 60d75f1 (v2026.11.12.6, after 045). Sent to the owner as `wormholes_share_mockup.html`.

## Files
- **build_xi.py:** `python3 -I build_xi.py <repo>/index.html wormholes_share_mockup.html`. It applies PATCHES to index.html, each found exactly once or the build stops: 14 of 044's list patches (from claude/roadmap/wormhole-sig-ids-mockup/build_sig.py; the probe scan, ring and colour patches left out), one so the store reads 044's fields back, and this plan's two (the Export / Import row and its clicks). It injects mock.js, the SEED list, proto_sig044.js and proto_xi.js in the head, and boot_wh.js and mk_xi.js before `</body>`.
- **mock.js and boot_wh.js:** not kept here; take them from the repo's `roadmap/wormholes-standout-mockup/` (the same files as the Wormholes filter mockups).
- **proto_sig044.js:** a stand-in for build queue 044 (signature IDs, details, Drifter per hole, raw lines, the Add form, the per-ID removal mark), copied from 044's mockup with the probe scan left out. Not this plan's design.
- **proto_xi.js:** this plan: the redaction (D7), what each line set (D4), the export (D3), the checks on import (D9), the merge worked out from the lines (D5, D6, D10, D12), the preview (D8) and the two boxes (D1, D2).
- **mk_xi.js:** the MOCKUP bar: open the list, fill Import with a made-up friend's export, reset (a reload brings back the seeded list).
- **test_xi.py:** `python3 -I test_xi.py wormholes_share_mockup.html shots/` (Playwright, bypass_csp, each case on a fresh page; 1440 and 390 px). 82 checks, all passed, no page errors, no sideways scroll.

Everyone is made up ("Mk …", "Mockup …", the ticker MKRC). check_pii: 0 problems with the names list (the page's own login button is the only embedded image).

## In the repo (build queue 046, 2026-11-13)

Copied here from the Project at the build, the files as they were (the plan is roadmap/wormholes-export-import-plan.md). mock.js and boot_wh.js
are in roadmap/wormholes-standout-mockup/: copy them beside build_xi.py to build again (from main 60d75f1; test_xi.py passed its 82 checks again
at the build). The mockup as the owner saw it is `Claude outputs/wormholes_share_mockup.html`. The build differs from it where the plan's "Built"
notes say (the real 044 underneath, names loaded first, the redaction reading a line whole, your own Intel lines keeping 044's order, a shared
line for what an export holds with no line behind it).
