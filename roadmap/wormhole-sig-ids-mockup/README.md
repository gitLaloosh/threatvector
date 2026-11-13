# Signature IDs mockup (wormhole reports)

Plan: claude/roadmap/wormhole-sig-ids-plan.md (DRAFT, not queued). Built from main d227c9d (after 040). Sent to the owner as sig_mockup.html, 2026-11-12.

- build_sig.py: `python3 -I build_sig.py <repo>/index.html sig_mockup.html`. It applies PATCHES, the 18 changes the build would make to index.html, and injects mock.js, proto_sig.js (head), boot_wh.js and mk_sig.js.
- proto_sig.js: itWhDetails (the reader), itWhSigMerge, the tags; window.__SIGOFF = "Today".
- mk_sig.js: the MOCKUP bar.
- test_sig.py: `python3 -I test_sig.py sig_mockup.html shots_sig/` (Playwright, bypass_csp; 1440 and 390 px; 110 checks).
- mock.js, boot_wh.js: as the Wormholes filter mockup.

Everyone is made up ("Mk …", "Mockup …", and characters named "Class" and "Then" for "Today"). The owner's line shape is used with a made-up reporter.

## In the repo (build queue 044, 2026-11-13)

Copied here from the Project at the build, the files as they were (the plan is roadmap/wormhole-sig-ids-plan.md). mock.js and boot_wh.js are
the Wormholes filter mockup's, in roadmap/wormholes-filter-mockup/: copy them beside build_sig.py to build again. The mockup as the owner saw it
is `Claude outputs/wormhole_sig_ids_mockup.html`, built from main d227c9d. The build changed some of it: the probe scan paste (D11) was taken
out before the build, each ID got its own removal mark, every kept line its `set`, and the type table comes from CCP's data
(`tools/gen_wh_table.py`, which puts C729 at "?" where the mockup's wiki list had Pochven).
