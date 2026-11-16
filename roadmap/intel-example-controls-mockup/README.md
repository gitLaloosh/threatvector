# Intel example controls mockup (research session, 2026-11-15)

Plan: `roadmap/intel-example-controls-plan.md` (build queue 055). The mockup is `Claude outputs/intel_example_controls_mockup.html`.

- `proto_exctl.js`: injected after the page's own script. Replaces `itExampleHtml`, `itExMapPic` and `itExPlace` while its MOCKUP box is on Proposed.
  - Proposed adds still copies of the zoom row, the search box, the filter column (Security on) and the slider row; makes the picture the live map's height; centres it in the part Near You doesn't cover; moves marker 3 to the bottom-left; fixes the phone Near You list's height.
  - Today calls the page's own functions.
- `build_exctl.py`: `python3 -I build_exctl.py <repo>/index.html proto_exctl.js intel_example_controls_mockup.html` (takes out the page's CSP, adds the script).
- `test_exctl.py`: `python3 -I test_exctl.py intel_example_controls_mockup.html shots` (45 checks at 1440 and 390, Today and Proposed; screenshots of `.itx` into `shots/`).

Built first on main e7f5a2b (v2026.11.15.3). The copy in `Claude outputs/` was rebuilt by the build session on main 43ca307 (v2026.11.16.3, after 058) for the 055 review, where all 45 checks still passed; it is the "Today" of that main. Run on a page built from 055 or later, its Today is no longer main's old example (the page's own functions now draw the controls). Made-up data only: the page's own `IT_EXAMPLE`.
