# Mockup: the Intel map's Wormholes filter (wormhole mapping, phase 1)

For build queue 040 (plan `claude/roadmap/wormholes-filter-plan.md`). Made 2026-11-12 by the research session from main 1e22ec7 (v2026.11.12.3). Sent to the owner as `wormholes_filter_mockup.html` (the real page with a MOCKUP bar bottom left).

- `build_whf.py <repo>/index.html <out.html>`: the real page, made-up Intel around C-J6MT ("Mk …" / "Mockup …" names), no network, storage in memory, the page's CSP replaced. Needs `mock.js`, `proto_whf.js` and `boot_wh.js` beside it. Far systems for the seeded reports (Jita, Amarr, Tama, 1DQ1-A, Amamake): ids checked against the page's own map table.
- `mock.js`: the map-look mockup's runtime plus `__MKlocal` / `__MKintel` (write new Local and Intel lines).
- `proto_whf.js`: the feature. Adds the sixth filter to IT_MAP_FILTERS and wraps itMapFcol, itMapDimmed, itMapDraw, itMapTip, itMapFLegHtml, itMapFLegTitle, itMapLegend, itMapFbtnsHtml, itNearTagsHtml, itFeedRowHtml. Store `tvWormholes` ({v, rep, gone, keepH}); seeds kept reports 0.7–30 h old. The list panel (add / remove / close). MOCKUP bar: post a "wormhole" line, Wormholes / Security filter, open the list.
- `boot_wh.js`: opens the Intel tab and turns Intel on.
- `test_whf.py <out.html> <shots dir>`: 51 checks at 1440 and 390 px (filter, badges, setting, live rings and the forget window, hover lines, the list button and panel, no sideways scroll, no page errors). All passed 2026-11-12.
- check_pii not re-run on these scripts (names read by hand: only "Mk …" / "Mockup …" and EVE's public system names).

Run: `python3 -I build_whf.py <repo>/index.html wormholes_filter_mockup.html && python3 -I test_whf.py wormholes_filter_mockup.html shots`

Moved into the repo with build queue 040 (2026-11-12); `Claude outputs/wormholes_filter_mockup.html` was rebuilt from main 1e22ec7 (the page before 040) by `build_whf.py`. The prototype is the mockup only: the page's own code (040) differs where the build review said (the words are intel keywords, hand-added wormholes only on the filter, the example sandboxed, the map's refresh key).
