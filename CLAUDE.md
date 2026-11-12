# Notes for AI assistants working on this repo

**This repository is public. Nothing personal goes in it (LESSON #90).** No real names (the
owner's, his characters', other players', corporations' or alliances' from his screenshots, logs
or pastes), no paths from his computer (`C:\Users\<name>\...`), no e-mail addresses, no keys or
tokens, no screenshots and no raw intel (chat lines, D-Scan or Local pastes). Refer to him as "the
owner". Test data is made up; real pastes and logs are read for their format only. A mockup shows
the real page with made-up data, and every picture embedded in a page is looked at and listed in
`tools/pii_reviewed_images.json`. `python3 -I tools/check_pii.py` refuses all of it (a chain step
and a git pre-commit hook: `git config core.hooksPath tools/git-hooks`); personal names it looks for
are in the git-ignored `tools/pii_terms.local.txt` on the owner's computer.
A build session's clone lacks it: copy it in from the Project first (build queue README, "The personal-data check's names list").

**The served copy** (build queue 027; Project doc roadmap/page-publish-plan.md): threatvector.space serves what
`tools/publish.py` makes from `main` (`.github/workflows/pages.yml`, on every merge): every tracked file as is except the mockups in
`Claude outputs/` (`NOT_SERVED`, page unchanged after v2026.11.08.4: served, they shared the site's browser storage), and index.html
without comments (the script through `tools/publish/strip_js.js`: acorn, a copy kept in `tools/publish/`, checked against npm in
the workflow; CSS and HTML comments by a small scanner; the CSP hash rewritten). The repo keeps the commented source; nothing in
`_site` is edited by hand. Error reports quote codes, not line numbers, so the two copies needn't line up.

**Never get the user's address blocked (LESSON #93).** zKillboard blocks an address that asks too fast
(its live feed: over 15 requests a second, for an hour). Every request to zKillboard goes through one
of two gates: `zkbFetch` (the API: starts 1 s apart, at most 3 in the air since v2026.11.06.4; a list zKillboard couldn't finish
is slow (ZKB-06), not down: asked once more 30 s later, `dscanZkbSlow`, LESSON #140) or `itR2Fetch` (the live feed, v2026.10.30.3: its
`itKillTurn` gate, at most 5 a second by the clock, waits timed in a worker; a stop for an hour at the first 429, kept in
localStorage for every copy of the page; a tripwire; LESSON #106). zKillboard's developer has said the limit will be cut
further if abuse continues, so stay at a third of it. The API's pause after a failure is kept in localStorage (`dscanZkbPause`,
v2026.10.31.2) so a reload waits it out too, and every Retry after a zKillboard failure is `zkbRetryHtml` (a countdown while paused). Test against a stand-in, never by provoking the real service. Never pace requests with a batch of timers:
a hidden tab fires them together. Every `fetch()` is listed in `tools/check_request_gates.py` (a chain
step); `tools/page_checks/request_gates_check.py` tests both gates with the timers bunched. Probing a
live service from the owner's machine counts against his address too.

Threat Vector (called D-Scan Analyzer until v2026.10.14.60, then EVE Threat Assessment (ETA) until v2026.11.06.2) is a
single-file tool (`index.html`) that estimates EVE Online ship stats from killmails and EFT fits. It is published at
https://threatvector.space (GitHub Pages from `main`, the `CNAME` file; build queue 013) from the repository
`gitLaloosh/threatvector` (renamed from `dscan-tool`). The saved-data names keep the old ones on purpose (localStorage
`dscan…`, IndexedDB `dscan-tool-cache`, `eta-intel`, `dscan-intel-sounds`), as do `dscan-tool-history/` and the extension's
`eta-*` menu IDs: users never see them, and renaming them would lose what's saved. The footer's source link is the one place the account name is written into the page (the owner, 2026-11-04: "Write the repo link in"); the page no longer
works it out from a github.io address. Its calculations must match **pyfa**
exactly, using primary sources only: pyfa's source code and CCP's SDE / live ESI.

Before any calculation work, check that pyfa hasn't moved:
`PYFA_SRC=/path/to/Pyfa python3 -I tools/pyfa_update_check.py` (add `--run` for
the full verification chain). See `PYFA_CORE.md`.

**The rule (`PYFA_CORE.md`):** code fenced `PYFA CORE BEGIN/END` in `index.html`
replicates pyfa and is fingerprint-locked (`tools/pyfa_core_manifest.json`). The
tool may change what goes INTO the pyfa calculation (module states, assumed
charges, drones) or how results are SHOWN, never how the calculation works.
Change a core section only to match pyfa, then re-verify and run
`node tools/check_pyfa_core.mjs --update`. Every deliberate difference from pyfa
is listed in `DEVIATIONS.md`; an unlisted difference is a bug.

**After an EVE patch** (v2026.11.04.3, build queue 008, Project doc roadmap/game-data-update-plan.md; the runbook is
roadmap/expansion-update-runbook.md): the page drops the item data kept in the browser when EVE's server version changes
(`gdVersionCheck`: ESI /status/ once per load, the first lookup waits 3 s at most, only the `types` / `groups` stores; "Item
data refreshing"). `tools/sde_change_report.py` lists what changed in CCP's data since the manifest's `pyfa.clientBuild`
and writes `GAME_DATA_PENDING`, the items changed and not yet checked against pyfa; fits and hulls using one say "Changed in
EVE's update:" (`gdNoteHtml`, `gdHullMarkHtml`, `gdHullNoteHtml`; never on Intel or page-wide). The pyfa update empties the
list (PYFA_CORE.md); `tools/check_game_data_pending.py` keeps it in the tools' form. `game_data_check.py`.

Before changing any calculation:

1. Read `LESSONS_LEARNED.md`, the catalog of mistakes already made here:
   its Index first (one line per entry, grouped by task), then the entries
   that apply. Follow its checklist **in order**: it's the definition of
   done, and the expected values are derived before any code is written.
   For page, Intel or process work, the matching Index groups are enough.
2. Use `tools/` (see `tools/README.md`):
   - `tools/pyfa_effects.py` runs pyfa's real effect handlers so you find all
     of them. Don't grep or regex `effects.py`.
   - `tools/independent_checks/` derives expected values without the tool's
     own tables. `tools/pyfa_fit_oracle.py` runs pyfa's handlers on a whole
     fit (hull, modules, charges, skills, mode) and is the reference for
     resistances; reuse it for any stat it covers.
3. Run `node regression_suite/run_regression.mjs index.html`. It must print
   ALL PASS. Add a constructed golden fit for every new mechanism.
4. Bump the version tag in `header.hero`: `vYYYY.MM.DD.N` is the delivery's own date (UTC)
   and its number that day, from 1 (`v2026.10.29.1`, then `.2`; the next day `.1`). Up to
   `v2026.10.14.104` the date never changed and N counted every delivery; users read that as an
   old build. Add a dated note to `dscan-tool-history/`.
   Exception: the pull requests `.github/workflows/jump-table.yml` opens (the stargate table, `INTEL_JUMPS`,
   when an EVE build changed a gate; `tools/jump_table_update.py`) change only that table and no version.
   The same for its "Game data" pull requests (v2026.11.04.3, `tools/sde_change_report.py`): they change only
   `GAME_DATA_PENDING`. After the owner merges one, work from the merged copy (he runs `git pull`).
5. Deliver on a branch, through a pull request the owner merges (the owner, 2026-11-03: "one builder with access to
   branch. the rest can read for planning purposes."; the build queue README's "Repo access: one builder, on branches").
   - Only the one build session with write access pushes. Research and planning sessions only read the repository.
   - Never push to `main` and never force-push: `main`'s ruleset requires a pull request, blocks force pushes and
     deletion, and merges by squash. One branch per queue item, named after it (`011-list-caps`), started from `main`
     after the previous pull request is merged (index.html is one file: parallel branches would conflict).
   - Commit and run the checks on the branch, then open a pull request into `main`. Its title is the Summary line: under
     72 characters, starting with the version (or "page unchanged" for tools and docs only). Its body is the
     Description's short bullets and the page-size line (step 6). No names, paths or intel channel names.
   - At the top of the body: any change under `.github/workflows/`, and any change to what the page keeps in users'
     browsers (localStorage keys, IndexedDB stores). Such a change must be safe both ways (the 012 review, 2026-11-04):
     the new page still reads what the older page wrote (upgrading is safe), and the older page still reads what the new
     page writes (reverting is safe; keep an existing key's form and put new data under a new key). Say both in the body.
   - The owner reads the diff and merges; GitHub Pages publishes only after his merge. The reply links the pull request.
   - A session without write access delivers as before: the files into the owner's folder, and a commit message in the
     reply (Summary + Description as above) for him to commit himself (the owner, 2026-10-30).
   After the last edit to index.html: `python3 -I tools/csp_hash.py --write` (v2026.11.07.3; the CSP names the script by hash).
6. Report both of index.html's gzipped sizes in every delivery: the source's (`gzip -9 -c index.html | wc -c`) and the
   served copy's (`tools/publish.py --size` prints both, without copying the site). The 800 KB ceiling (800,000 bytes) applies to the served copy since
   build queue 027 (the owner, 2026-11-08: "confirmed"; first "At 800 KB", 2026-11-03): past it, stop and ask the owner
   before delivering. The source's size has no ceiling.
   Before the pull request: `python3 -I tools/run_checks.py --served` (the served copy through SERVED_CHECKS).
7. Info text (build queue 036; the build queue README's "Info text stays true", the owner 2026-11-11: "we should implement a step in the
   delivery process that addresses whether changes will affect the accuracy of info text"): search `CARD_INFO` and `IT_EX_NOTES` for the
   words, labels and numbers your diff changes, and fix any line it makes wrong in the same pull request, by the panels' rules
   (`check_subtext.py`: the length cap; the test in the Project doc roadmap/info-panels-review.md: the open part says what the card shows
   and what to do with it, how it's built goes to METHODOLOGY.md). The pull request says `Info text: checked; changed: <keys>` or
   `Info text: checked; none`. Never the header's Lookup budgets gauge; the Intel example's tutorial text only to fix a wrong line.

**Error messages carry codes** (`ERRORS.md`). Every error the page writes ends
with a code such as `(ZKB-01)`, defined once in `ERROR_CODES` in `index.html`
(what triggers it, what to check, why it exists, the build and history doc).
A new error message gets a new code there (never reuse or renumber one; retire
it instead), shown with `withCode()` / `codedError()`. Then run
`python3 -I tools/gen_errors_md.py --write`. Owner reports quote the code: look it up in
`ERRORS.md` first.

**Outside text in HTML** (v2026.11.07.2, build queue 021; LESSON #144): text from outside the page (fit names, pilot, corporation
and alliance names, intel lines, pastes, links) goes into HTML only through `escapeHtml`, which escapes `& < > " '`; an attribute is
always double-quoted (`title="${escapeHtml(x)}"`). Escape once: never escape text that is already HTML. `html_escape_check.py`
feeds a harmless marker through every route and fails on anything out of place or escaped twice. Since v2026.11.07.3 (build
queue 023) `tools/check_html_sinks.py` holds it: a `${...}` in a template that builds HTML is `escapeHtml(...)`, a number, an
ALL_CAPS constant or a builder (a `...Html(` function or its `BUILDERS`); the rest that was there on 2026-11-07 is in
`tools/html_sinks_baseline.json`, which only shrinks (`--shrink`; adding to it needs the owner's OK in the pull request).

**The page's Content-Security-Policy** (v2026.11.07.3, build queue 023, the SSO plan's Phase 0 hardening; Project doc
roadmap/sso-hardening-plan.md; LESSON #145): a meta tag before the script allows only the page's one inline script, by its sha256,
and only the hosts the page uses (connect: ESI, login.eveonline.com, R2Z2, zKillboard; images: images.evetech.net, data:, blob:;
workers: blob:); `<meta name="referrer" content="no-referrer">`. So:
- **Run `python3 -I tools/csp_hash.py --write` after the last edit to index.html**, before committing (run_checks, the chain and
  the pre-commit hook run `--check`; a stale hash stops the live page from running at all). The tool hashes as the browser does
  (CRLF to LF first), so a Windows checkout is fine. A new host or directive is a change to `EXPECTED` in that tool.
- **No inline event handlers** (`onerror="..."`, `onclick="..."`): the policy refuses them. An image that may fail to load gets
  `data-imgfail="hide|remove|none|next|next-block|initials"` (one capturing listener at the top of the script); anything else uses
  `addEventListener`. No `eval`, `new Function` or string timers.
- **Page checks open the page with `bypass_csp=True`** (they need `eval` through `run_async`, modified copies and mutants);
  `tools/page_checks/csp_check.py` is the only one with the policy on, and it is where the policy is tested. A new page check
  uses `bypass_csp=True` too; never turn the policy off in csp_check.

**Log in with EVE** (v2026.11.08.1, build queue 024, SSO Phase 1; Project docs roadmap/sso-phase1-plan.md and roadmap/eve-sso-plan.md;
LESSON #147): CCP's black button is on the profile's EVE tab (since v2026.11.10.1, build queue 032), under the features' switches:
**choose before you go**, the one trip to EVE asks for exactly what's on (`ssoStart(ssoWant(), 'eve')`; EVE's page is all or cancel);
logged in, the tab shows the name, an "EVE login" tag and Log out; the typed pilot stays on the Pilot tab. CCP's PKCE recipe, no
server: no client secret anywhere, **no scope** at login with nothing picked. A switch turned on while logged in without its permission
waits ("Needs EVE's OK", the EVE lamp amber) for one Continue to EVE (`data-sso="eve-go"`); it turns off with SSO-07 only when a
trip comes back without it or ESI answers 403 (the owner, 032). So:
- **The login is optional.** Nothing may require it: typing a pilot, hand-kept Standings and EFT pastes all stay.
- **The address is cleaned before any request:** `SSO_RET` at the top of the script takes code/state/error out of the address
  (keeping other parameters and the hash) before `gdVersionCheck` or anything else asks anything; `ssoFinish` uses it after start-up.
- **Every request to login.eveonline.com goes through `ssoFetch`** (its host only, `credentials: 'omit'`, no cache, no referrer),
  called only from the functions in `SSO_SITES` in `tools/check_request_gates.py`; the host is written once, `const SSO_HOST`.
  Only JSON answers are read (`ssoJson`; an HTML error page is its status number). The endpoints come from CCP's metadata, never
  hard-coded.
- **Tokens:** the access token in memory only, sent only to ESI by esiFetch's auth branch (Phase 2); the refresh token and `{id,
  name}` in sessionStorage (`tvSsoRefresh`, `tvSsoWho`; `tvSsoPending` for the press; `tvSsoTab` since Phase 2), never localStorage.
  Log out revokes it and clears the pilot, and keeps the picks (`tvOnlineShow`, `tvEveStand`, `gameLoc`; the owner, 032); the revoke takes the app off EVE's authorized-apps list for that character (the owner's
  hand test, 2026-11-08: the list shows live logins only, the dev and live apps separately), so never say EVE "keeps" a permission
  after Log out. The link there (developers.eveonline.com/authorized-apps, through `leaveAsk`) shows only with a permission held
  ("EVE permissions:"). CCP has no logout page for apps: the player stays signed in on EVE's own site, so nothing may promise more. Another tab changing the pilot logs this tab out.
- **CCP's button image stays as CCP made it** (DLA 7.2; one of its four images, black large here): hover and focus are drawn on the
  `<button>` around it, never a filter, opacity or resize on the image.
- **The token is checked** (`ssoVerify`): the JWKS key its kid names, RS256 + RSA or ES256 + P-256 only; iss, aud (the Client ID and
  "EVE Online"), exp, sub `CHARACTER:EVE:<id>`. The Client ID comes from the origin (`SSO_APPS`: threatvector.space, the dev app at
  http://localhost:8000); any other origin shows the button disabled. Errors SSO-01..08 (06-08 Phase 2).
- **Never a live login in a check:** `tools/page_checks/sso_check.py` serves the page at both origins and answers for CCP with keys
  made per run; made-up tokens in the `madeUp…` form. The only live login is the owner's hand test on the dev app.
- **Phase 2, Use my game location** (v2026.11.08.4, build queue 028; Project doc roadmap/sso-phase2-plan.md; LESSON #150): a switch on
  the profile's EVE tab (`#ppSw-loc`, `it.set.gameLoc` in `dscanIntel`; Intel's box 3, `itGlHtml`, says whether it's on and opens the
  EVE tab). Without the permission it waits (above);
  `ssoStart(want, from)` asks for `esi-location.read_location.v1` plus what the tab holds and what's on (`ssoWant`; EVE gives a later
  login only what it asks for, the owner's hand test 2026-11-08, so every trip asks for all of `ssoWant()`, and the EVE tab says how many),
  never a ship scope (the owner: no feature may suggest the page knows the fit you fly unless it reads ship and fit from the game). The
  checks run only when the token's `scp` has it (a trip back without it: SSO-07, off). So:
  - **The token goes out only through `esiFetch(url, init, kind, {scope})`:** ESI URLs only, checked before `ssoAccess()`; only there
    Authorization, `X-Compatibility-Date: ESI_COMPAT` (a date ESI answered, never a future one) and `X-User-Agent` (`ESI_UA`). Outside
    that branch esiFetch still sends what it is given. `ssoAccess` is called only from esiFetch (check_request_gates).
  - **Renewal** (`ssoAccess`/`ssoRenew`): lazy, under a minute left, one at a time per tab; refresh_token + Client ID, no secret; a new
    refresh token saved first; invalid_grant ends the login (SSO-06); 429 waits Retry-After; else 30/60/120 s then 5 min. A duplicated
    tab (same `tvSsoTab` answered on the `tv-sso` channel) drops its copy without revoking.
  - **The checks** (`itGameLoc`): on Intel's tick only, in the tab holding Intel's lock, while it runs, when the login is Intel's You;
    never before `Expires` (5 s floor), twice as long under 25% of the group's tokens, Retry-After on 420/429; 401 stops it for good
    (SSO-08), 403 turns it off (SSO-07). Newer wins (`itMySys` = `itGlSys` or the log's, `it.me.logAt`); amber when they differ; kept in
    memory only (DLA 9.5); redrawn only when `itGlKey` changes (the checked time is its own span).
  - **The trip to EVE:** `sso.starting` / `sso.leaving` (never `busy`, which is only the return being checked); `pageshow` persisted
    undoes it ("nothing changed"); a load from the Back button within 10 minutes (Chrome couldn't keep the page) counts as Cancel at
    EVE (the owner: "i agree"); any other load drops `tvSsoPending` and starts nothing. Other tabs hear "away" before the page leaves,
    never only from pagehide, and a lock still held by a cached page doesn't turn "paused" into "on in another tab" (the hand test). `intelWasOn` in the pending entry restarts Intel after the return
    (Authorize or Cancel), never otherwise; a folder needing a click shows Allow reading, which then starts it; sound on adds "Click
    anywhere…" (`IT_WAKE_NOTE`). Other tabs say "Intel is paused while the other tab logs in with EVE." (`why: 'away'`, cleared by
    `{back: true}` or the tab running again).
  - **Intel's alerts start unchecked** for someone with no saved settings (`itDefaults`; saved values kept). Checks that test alerts seed
    `{sound: true, notify: true}`. **Intel stopped reading** (`itLostSound`): one built-in sound once per stop, sound on only.
  - Checked by `tools/page_checks/sso_game_check.py` (stand-in SSO and ESI location; never live).
- **Show when I'm online in EVE** (v2026.11.09.1, build queue 029; Project doc roadmap/sso-online-status-plan.md): a switch on the
  profile's EVE tab (`#ppSw-online`), `esi-location.read_online.v1` (`SSO_ON`) through the EVE tab's permission step
  (`ssoWant` adds it while `ssoOn.show`), the setting in localStorage `tvOnlineShow` (true/false). So:
  - **The portrait** (the owner: "A and C"): a dot on its top-right corner (`#profileOn`, `--st-online` / `--text-faint`) and the portrait
    greyed while logged off (`.pf[data-on="off"]`); nothing when off, logged out or without the permission (`ssoOnShown`). Log out
    stops the checks and keeps the switch (032; was "turns it off").
  - **One tab asks per character:** a Web Lock `tv-online:<id>` (queued; the tab running Intel takes it over with steal and asks on
    Intel's tick, `ssoOnTick`); every other holder has one timer (`ssoOnArm`). Let go before leaving for EVE's page and on pagehide; a
    hidden tab without Intel leaves the queue; a tab waiting 3 minutes without an answer takes over. The answer `{id, online, at}` goes out
    on the `tv-online` BroadcastChannel; a tab that opens asks for the last one (`{ask: id}`). Never before Expires, 60 s at least, twice as
    long under a quarter of the group's tokens; 420/429 Retry-After; 401 SSO-08 (never again), 403 SSO-07 (off). Memory only.
  - **Intel**, running as that character and logged off: "Your character is logged off in EVE." with Stop Intel (`ssoOnIntelHtml`), above
    the amber wake line; Intel never stops by itself. Drawn only when what it shows changes (`ssoOnKey`; the time is its own span).
  - Checked by `tools/page_checks/sso_online_check.py` (Phase 2's stand-ins plus ESI's /online/; never live).
- **Standings from EVE** (v2026.11.09.2, build queue 030, SSO Phase 3; Project doc roadmap/sso-phase3-standings-plan.md; LESSON #151): a
  switch on the profile's EVE tab, "Use my corporation's and alliance's EVE standings" (`#ppSw-stand`; what was read shows in the
  Pilot tab's Standings, `sideEveStHtml`), its two scopes (`SSO_SC`, `SSO_SA`; personal contacts are not read, the owner) through the
  EVE tab's permission step, the setting in localStorage `tvEveStand` (true/false). So:
  - **EVE decides while it's on** (`sideEveUse`, `sideEveSide` inside `sideOf`): your own groups friendly; above 0 friendly, below 0 hostile,
    0 or none neutral; in one list the pilot's entry, else his corporation's, else his alliance's; across the two lists **the alliance's**
    (the owner: "for now, alliance wins"), the disagreement said (amber, "Alliance +10 (corp −10)"). zKillboard's evidence is only a note
    beside neutrals. The typed lists are hidden (`.side-typed`) and unchanged in `dscanSide`; an NPC corporation, the switch off, not
    logged in or nothing read: today's `sideOf` exactly. Every `sideOf` caller passes the pilot's id (5th argument).
  - **Reads** (`sideEveNeed`, `sideEveFetchList` with esiFetch's auth branch): only when something needs sides (an Analyze, Intel's tick,
    the Fleet tab, the Pilot Analyzer's tag), never before Expires and 5 minutes apart; every X-Pages page, the pages read once more when
    their Last-Modified differ; both lists swapped in together. The first read in a tab is waited for, 10 s at most (`sideEveReady`).
    401 SSO-08 (never again), 403 with the permission SIDE-03 (that list skipped), without it SSO-07 (off), no answer or 5xx SIDE-04 (the
    copy in hand); 420/429 Retry-After. Memory only (DLA 9.5).
  - **A change redraws once** (`sideEveApplied`, by `sideEveKey`): the System Analyzer, the Fleet tab, the Pilot Analyzer's tag, and Intel's
    stored sides worked out again with Near You replayed from the Feed, no alert (`itSidesRework`, the owner: "Re-work + replay"; a typed-list
    edit does it too). Inside the Intel example's sandbox EVE's standings are never used.
  - Checked by `tools/page_checks/sso_standings_check.py` (stand-in SSO and ESI contacts routes; made-up groups; mutants).

**My Ship** (v2026.10.14.33, `roadmap/my-ship-plan.md`): the user's own fit, saved in
the browser (`localStorage` `dscanMyShip`: EFT text, module states, the switch; never the
numbers, which are recomputed from the text). Code: the `MY SHIP` block at the end of the
script; classes `mys-*` (`ms-*` means module state). Start-up code must survive the suites'
stub DOM (LESSON #36). Check: `tools/page_checks/my_ship_check.py`.

**UI rules** (v2026.10.29.7; approved by the owner from mockups, 2026-10-29; LESSON #101). One of each, site-wide:
- **Tag** (chips, pills, labels): 3-4px corners, never round; a faint fill (`--tag-fill`), no visible border at rest;
  hover/open `--tag-fill-hover` with `--accent-edge`; pressed `--tag-on`. Empty states: the same fill, dim text, no dashes.
  Cyan is the one accent.
- **Switch** (`.dmg-sw`, `input.mys-sw`): 36x20 track, 3px corners, square 14px knob; off faint, on `#1f6f80`. One named exception
  (v2026.10.30.2, the owner): the Intel switch (`#intelSw`) off is amber and breathes (none with reduced motion), so new users find it.
- **Slider**: the global `input[type=range]` style, a 4px track filled cyan to an upright 10x18 handle. The fill is
  `--p`, set by `rangeFillSet` (input events, new sliders, and code that sets `.value`/`.max` calls it). No local slider CSS.
- **Text field** (text, search, select, textarea): `--bg` fill, `--field-border`, 4px corners; hover
  `--field-border-hover`; focus a cyan border and the `--accent-ring` ring (never amber, never the browser's own);
  disabled 45%. 36px tall, 32px in filter bars; paste boxes stay monospace.
- **Intel lists** (v2026.10.30.1, the owner): the jump count first; system names in a column as wide as the widest system name
  (measured in the drawn font, `itSysWidths`); the region (build queue 038, `sysRegion`): in the Feed its own column after the system,
  as wide as the widest region name; in Near You (narrow beside the map) a line under the system (the owner at the build); rows on a phone
  show the system only; sentences elsewhere say "System (Region, N jumps)" (`sysBracket`); the left edge only means "within your alert range", in the "N near" colour
  (amber); no background highlighting; standing colours on words and names (neutral a bright grey). Intel channel names are
  shown only under the gear, never elsewhere (the owner: "security reasons"). `tools/page_checks/intel_layout_check.py`.
  A line naming several systems is placed after the name lookups, never before (LESSON #105; `intel_place_check.py`).
  Your profile (v2026.11.10.1, build queue 032; Project doc roadmap/profile-redesign-plan.md, mockup `Claude outputs/
  profile_redesign_mockup.html`, the owner's annunciator): one strip at the top right of four lamps, EVE, Pilot (portrait, name,
  its line), Fit and Intel (`PF_LAMP`), each a button opening its own tab of one panel (EVE, Pilot, Fits, Intel; `openProfile(tab)`,
  roving tabindex, the shared close button, focus back on the lamp); a lamp lights cyan when set, amber when it needs you, dark when
  off. "Use in assessments" is in the Fits tab (`#myShipUse`, the one switch). The Intel lamp: Off, Clear (cyan), "N near · Jj"
  (amber), "In system · N" (the Hostile red + pulse), Stopped (amber); N counts hostiles and neutrals (`itNearSum`, uncapped, "999+"
  above `PF_NUM_MAX`), the full sentence in its hover; the radar sweep runs only while Intel watches (transform only, none with reduced
  motion); the tokens --st-clear, --st-near, --st-in, the face --pf-*. The panel's banner says the one thing that needs doing.
  Writes only on change (`pfSame`). "Pilot rows up to" is in the System Analyzer's ⚙ (Local's results). "My Fit", never "My Ship",
  in what users read. `profile_check.py`.
  Intel's pilot chip (v2026.11.01.2, the owner's B2): standing (a tip only: standings aren't changed from a chip), name (Pilot
  Analyzer), corporation (logo + [TICKER]) and alliance (logo + <TICKER>) as separate parts; a group pressed filters the Feed by it
  (a filter chip since v2026.11.07.1; the search box stays the user's); hover: outline + dividers, the part under the pointer filled
  white; without hover the first tap shows the parts. `pilot_chip_check.py`.
  Feed filter chips (v2026.11.07.1, build queue 010; roadmap/near-you-height-plan.md "Additions"; mockup `Claude outputs/
  intel_filters_mockup.html`): pressing a system, corporation, alliance or ship (ship chips in the Feed, ship names in Near You's rows)
  adds a chip (`it.fl`, `itFlToggle`) on its own line under the filter bar ("Only" · chips · "Clear all" with 2+); pressed again
  removes it; a second system replaces the first; every chip and the typed text must match (`itFlMatch`; a kill matches a ship that
  died or killed). Near You is never filtered; the map reads the system chip (`itFlSys`). Chips aren't saved. Near You's kill badges
  add up their kills' ISK (zKillboard's values, `itIsk`). Near You's height (over 900 px): as tall as the map column, never under
  `IT_NEAR_FLOOR` (the map's smallest box + heading), the list scrolls inside (`contain: size`), "+N more systems below"
  (`itNearMore`, after a draw and on its scroll, never a timer); opening a row or a map press that keeps a route scrolls the list
  (`itNearShow`, never the page); a redraw keeps its scroll and focus. `intel_filters_check.py`.
  One close button (v2026.11.01.3): every info and settings panel (role="dialog") has the shared `button.x-close`, 32 px in its top
  right (44 px on a phone), at every width; Esc and a press outside still close, the focus back on the opener. Menus (⋮ fit actions,
  hull variants, slot menus, the My Fit picker on a wide window) have none. `check_ui_rules.py` (5), `close_buttons_check.py`.
  Drawing cost (v2026.11.01.4, LESSON #120): Intel's card is drawn only when what it shows changed (itQuickKey, then the built text
  compared) and only while it can be seen (itShown; drawn once on return); its ages move on their own timer (10 s / 30 s). Don't add
  writes to the page on a timer without the same compare. Endless animations: opacity or transform only. `intel_redraw_check.py`;
  measure with the Project's roadmap/perf-harness/ (before and after in one session).
  Layout D (v2026.10.31.6, the owner; Project doc roadmap/near-you-layout-d.md), both lists: line 1 jumps, the system (a button that
  filters the Feed only, never Near You), Near You's analyze icon (radar rings, always the System Analyzer), the tags, the time; Near
  You's kill badges on their own line, only when there are kills; then the toggle under the jumps and what was reported. No Assess
  column, no REPORT label; Clear, ESS (white at it, red linked), Bubble and camp are tags. A killmail's fleet size is drawn once
  (`fleetSizeHtml`, the dossier's). Check a layout with a busy row at every width (LESSON #113; `intel_layout_check.py`).
  v2026.10.31.7 (the owner's idea): the analyze icon has its own column right after the jumps, in Near You and on the Feed's reports
  (the whole system, not only that line; none on kill and clear rows); everything else starts after it, so a row without it has an
  empty cell. The jump column fits "88 Jumps" and In system (`--it-jw`). On a phone the icon sits under the jumps beside the toggle.
  Mockups size things the way the page does (LESSON #114).
  A word is a pilot only in its name's own capitals (one word typed by hand) or dragged in; report words (`IT_NOT_PILOT`) never
  otherwise (LESSON #111; `intel_words_check.py`).
  A pilot whose surname is a system's name (v2026.11.06.3, build queue 018; roadmap/intel-surname-system-plan.md): each whole system
  with the plain words beside it, 2-3 words, is looked up too (`p.stretch`, same batch); with 2+ systems a system inside a pilot's name
  is that pilot, checked before the ring (`itSysPilot`); a line whose only system is inside a pilot's name makes no report, only in the
  name's own capitals (or dragged in) and when the words beside it aren't a pilot alone (`itLonePilot`). `intel_place_check.py`.
  A pilot whose name has a filler word in it (v2026.11.06.5, build queue 020; roadmap/intel-filler-in-name-plan.md; LESSON #141):
  3-word stretches <plain> <filler> <plain> are looked up too (`p.fill`, same batch; no filler at an edge, no '*' inside) and read as
  one pilot only in the name's own capitals or dragged in (`itForce`). `intel_place_check.py`.
  A word before "gate" is read among the gates of the system the line is in (LESSON #112); one tag per Near You row for a gate:
  red "Camp · X gate" from a report, orange from 2+ kills at that gate, grey a gate with no camp words (`intel_gates_check.py`).
- **Intel's example for new users** (v2026.11.07.7, build queue 017; Project docs roadmap/intel-example-plan.md and
  roadmap/intel-example-build-review.md; mockup `Claude outputs/intel_example_mockup.html`): under the setup steps (and below the empty
  lists on a quiet start), a framed, `inert` example: the page's own Map (a picture, `itExMapPic`: the map's code on a canvas of its own,
  `itm` set aside and put back), Near You and the Feed's first 5 rows, drawn once from `IT_EXAMPLE` by the real builders inside
  `itExSandbox` (Intel's state, Standings and the map's pins set aside and put back; entries are history, so no alert); five markers placed
  after the draw and on a width change (`itExPlace`, one ResizeObserver), never a timer. Made-up pilots and groups with negative ids:
  nothing about them is asked of anyone (`itExOrg` answers itLogo / itTkHtml / itGrpTk with inline emblems); `tools/check_example_names.py`
  (offline lint; `--live` once by hand, the owner checks the tickers on zKillboard). Gone once a real report or kill arrives, remembered in
  `dscanItExGone` only while the folder is linked (`it.dir`); "See an example" in Intel's info panel brings it back with the shared close
  button. A browser without the folder picker gets an amber note above the steps (`itNoFsHtml`; Brave, by `navigator.brave` only, the
  flag's address as text); INTEL-01 says the same (`itNoFsText`). The switch stays off until a channel is ticked, and unticking the last
  one stops Intel (the owner, at the review). v2026.11.07.8 (the owner: "disable the on/off switch until a folder is chosen and at least one
  channel is checked"): `#intelSw` is disabled (`itSwLocked`, dimmed, no amber breathing) with a hover saying what's missing (`itSwTitle`);
  `itSwSync` keeps the box in step with `it.on` after a press. `intel_example_check.py`.
- **The chat-logs folder after a reload** (v2026.11.08.2, build queue 025; Project doc roadmap/intel-folder-permission-plan.md): Chrome
  asks again for a folder kept from an earlier visit, and asking needs a click, so the page keeps what the browser says (`it.perm`: none /
  prompt / granted / denied, `itPermRead`) and never asks on its own. `prompt`: step 1 "Needs your OK this visit" with **Allow reading**
  (`itAllowRead`, from the click; requestPermission is its first await) and Change…; `denied`: the blocked line. Steps 2 and 3 wait
  ("Waiting for the folder (1)", `itWaiting`) and say "No Local log" only after a read that found none (`it.read`). Look again
  (`itLookAgain`) on tab shown / focus and, while the setup card shows, every `IT_RESCAN_MS`: nothing while hidden, redrawn only when
  `itFoundKey` changed. A permission taken back while Intel runs: INTEL-02 (`itPermLostText`) with Allow reading in the error line
  (`itAllowNoteHtml`). `intel_folder_check.py` (a stand-in folder whose answers switch, and a stand-in store so a reload restores it).
  Which log is read (v2026.11.12.1, LESSON #158): per channel the one written to last (`getFile().lastModified` at each look), yours
  while written within `IT_LOG_MINE_MS`, the current one kept within `IT_LOG_SAME_MS`; a move reads the new end and skips what the old
  log gave (`itLineKey`); lines older than the last look are history. `intel_logs_check.py`.
- **Intel in one tab at a time** (v2026.11.08.3, build queue 026; Project doc roadmap/intel-one-tab-plan.md): a Web Lock (`IT_LOCK`,
  `tv-intel`) is held exactly while Intel runs (`itLockTake`, `itLockFree` in `itStop`); the switch asks for it only when free, and
  another tab's card says "Intel is on in another tab." with **Move Intel here** (`itMoveHere`: the folder permission from the press
  first, then `steal`); its switch is greyed out (the owner: the button is the only way). The tab that loses the lock stops
  (`itLockLost`: "Intel moved to another tab.", Move Intel back here). A BroadcastChannel (same name) carries the running tab's mark
  only when it changes (`itLockState` from `itHeaderSync`), "stopped" and "closed" (pagehide); a tab shown again asks and checks
  `locks.query()` (a crashed tab). Nothing starts by itself (the owner: "there is a switch for a reason"). No `navigator.locks`:
  as before. `itR2Fetch` drops a request that waited at the gate for a reader that stopped (LESSON #148). A catch-up after a gap waits
  a random 0-10 s first (`IT_CATCHUP_JITTER_MS`; not on start, the owner: "Only after a gap"). The map's ResizeObserver redraws on the
  next frame. `intel_one_tab_check.py`.
- **The logo** (v2026.11.07.4, build queue 022; Project doc roadmap/logo-header-plan.md; mockup `Claude outputs/logo_header_mockup.html`):
  R37 "Orbit Contact", inline left of the title in `.hero-title-row` (`.hero-brand`, `.hero-logo`, aria-hidden), 1.6em of the title's
  size, its T's top on the title's T's top (`--logo-nudge`, -0.19em / -0.16em under 600 px; re-tune if the title's font or size
  changes); colours by class from the tokens, no tile (the owner: "No tile"). Tab icon `favicon.svg` + `favicon-32.png`, home screen
  `apple-touch-icon.png`, rendered from `img/logo/` by `tools/render_icons.py` (standalone images: hex values of the tokens; the CSP's
  img-src has `'self'` for them). `logo_check.py`.
- **Standing icon** (v2026.10.30.4, the owner): one drawing site-wide, `standIcon` / `standMark` (EVE-style: a star for your
  corporation and alliance, + friendly, = neutral, − hostile); never drawn again elsewhere. Beside its own word it is decoration:
  `standIcon(k, true)` / `SIDE_MARK_BY_WORD` (LESSON #107).
- **Links out of the site** (v2026.10.31.3, the owner): a zKillboard link is `zkLinkHtml` (a "zK" icon in cyan, the colour of
  leaving the site), never "zKillboard ↗" text or a hand-written `target="_blank"`; every link that leaves the page asks first
  (`leaveAsk`), with "Don't ask again" per site and "Ask again" under Intel's gear. `outside_links_check.py` counts them.
- **Names in colour** (v2026.10.31.3, the owner): a system's name in its security colour (`sysNameHtml`, Intel's rule); a person's
  name in its standing's colour with its icon (`standNameHtml` / `std-n`), victims included. A dossier kill from the past 4 hours has
  its time in amber (`PD_RECENT_MS`).
- **What was asked for stays on screen** (v2026.11.01.5, LESSON #121): the Pilot Dossier draws the hull asked for (a pilot opened
  from the Fleet tab, a typed hull, a System Analyzer row) as its first row in every size, tagged On this kill / Lost on this kill /
  Asked for with its rank; the 8 used most recently follow (build queue 037: newest first, in a size by their newest kill in it); "Show N more hulls" is a button that draws every hull read. A Fleet-tab kill missing
  from zKillboard's list for the pilot is added from the killmail already open ("+ this one"). `dossier_pin_check.py`.
- **Kills grouped into fleets** (v2026.11.01.6, Project doc roadmap/kill-groups-impact.md §0, LESSON #122): the Fleet tab's kill picker
  (opened from Intel with 2+ kills) groups kills by shared player attackers: 2 shared pilots link two kills, 1 when either kill had
  1–2; chains are one fleet; victims and NPCs never link; "Not linked" last; biggest fleet first, newest kill first inside. Every
  group starts closed (a lone group open), headings with Intel's chevron stay pinned at the top of the list while their kills scroll
  (`top:-2px` over the list's padding); open groups are kept per set of kills. Only the picker: Intel, the analysis, `#fleet=` and
  the zKillboard budget don't change; no request. `kill_groups_check.py`; `check_ui_rules.py` (6) keeps list expanders on IT_CHEV.
  v2026.11.04.2 (roadmap/fleet-hulls-plan.md): each fleet heading shows its hulls (`fkGroupHulls`: each pilot once, in the ship from
  their newest kill; ships only, fkOpen's rule) as up to 4 icons + "+N more", the full list and "N of M pilots in ships" in its hover,
  none on Not linked or before the types are known; below a 930 px list (a container query) the hulls take their own line; on a phone
  only when open, 3. One Intel kill gets the list too ("1 kill in ...", an open Fleet 1; "NPCs" with no player); kills from a
  Pilot Dossier or a link don't. `fleet_hulls_check.py`.
- **Alert sounds** (v2026.11.01.8, Project doc roadmap/alert-sound-plan.md): two slots by jumps, Near You (1 jump to the alert range)
  and In system (0 jumps, kills too); five sounds made in code (Chime = the old sound exactly), or your own file (≤ 1 MB, ≤ 5 s,
  kept only in its own IndexedDB database `dscan-intel-sounds`, never the ESI cache); one master gain, loudness (volume/100)²; the
  notification is silent when the page's sound plays. No audio is made before a sound or a press. `alert_sound_check.py` (a stand-in
  AudioContext; generated tones only, never a real recording in the repo).
  A refused file's warning (INTEL-09/10) goes at the slot's next press (v2026.11.11.1, build queue 033): a built-in chosen, the list
  pressed or opened from the keys, "Your own file…", ▶ Test; taken off the page in place (`itSndMsgDrop`, `it.lastHtml = null`), never
  by a redraw, which would replace the list under the pointer (LESSON #152).
- **Intel map** (v2026.11.02.4, Project doc roadmap/intel-map-plan.md): layout B, the map beside Near You and the Feed below (a
  List | Map switch in Near You on a phone, `it.set.nearView`). `INTEL_MAP` (CCP position2D /1e14, security in hundredths, region)
  comes only from `tools/jump_table_update.py`, aligned to `INTEL_JUMPS` (its `jumps` = the jump table's md5; `gen_intel_tables.py`
  keeps it and says when it no longer fits). One canvas (`itm`), made once and moved into each card (`#itMapSlot`); drawn only when
  what it shows changed (`itMapRefresh`'s key), never while hidden. Reach ("Map: within" since 039): from Near You's reach to `IT_MAP_MAX` (the
  Feed's largest), following the Feed until set; Near You's reach is a setting (`nearRange`, alert range to the Feed's, default
  alert + 5). Rings: standing colour, gang size (1 / 2–10 / 11+). Routes: one per system (BFS, neighbours in index order), hover
  dashed, press kept. One stepper for every range (`RS`, `rsHtml`, `rsPaint`). `intel_map_check.py`.
  v2026.11.04.1 (roadmap/map-ly-hover-plan.md): `INTEL_MAP.p3` holds CCP's 3D positions (0.0001 LY, int24) for the hover's
  "N.NN LY from <you>" (`itMapLy`, `itMapLyText`: rounded UP to 0.01, the owner). Your system: a pin drawn last
  (`itMapPinDraw`), the only filled label (YOU · name), a 1.6 s beacon on its own canvas (`itMapBeacon`; first draw and a jump
  seen while Intel was in front, `it.me.sysAt`; none with reduced motion), the "You" edge arrow (`itMapYouArrow`); the
  crosshair centers at the same zoom (`itMapCenter`); a jump keeps the zoom and centers. `intel_map_you_check.py`.
  Build queue 039 (roadmap/map-look-plan.md, mockup `Claude outputs/map_look_mockup.html`; the owner: "is there any way to make it look
  more alike"): EVE's 2D map. Every system at CCP's position2D through `itMapXY` (one helper, so wormholes can be placed later), one
  scale, k = 1 the whole galaxy; only the reach pushed apart to `IT_MAP_GAP` (12 px) at the start zoom, through a grid (never pair by
  pair: 8-10 s at a 30-jump reach in the mockup); opens on you with a median gate `IT_MAP_START_GATE` (16 px; `itMapStartView`), ⤢ the
  reach (`itMapFitView`). Zoom stages by `itMapGatePx`: dots, circles with the security number (`itMapSecText`) from 34 px, names from
  80 px (`itm.stage`); gates between regions dotted; region names (`itMapRegionNames`) after the system names and giving way to them.
  The filter bar (`IT_MAP_FILTERS`, `itm.filter`, not saved; `itMapFcol`, `itMapDimmed`; scales `IT_MAP_JUMPS`, `IT_MAP_REGION` by
  `itMapRegCol`): its name line fades by one timeout per press; on a phone one 44 px button opens the row. The legend's filter line
  (`itMapFLegHtml`) is one line of one height for every filter, so Near You (as tall as the map's column) never moves. Past the reach:
  faint, no reports, but hover and press give routes (the owner: "yes"). `mapReach` reads "Map: within". `intel_map_look_check.py`.
  Build queue 043 (roadmap/paths-to-you-plan.md, mockup `Claude outputs/paths_to_you_mockup.html`): the filter Paths to you, just before
  Wormholes (always last, beside its list button `[data-it-whl]`): the galaxy's canvases hidden under an HTML overlay in `itm.box`
  (`itPt`, `itPtPaint`): a top-down tree of every shortest stargate route to you from each system with hostiles, neutrals or kills
  inside the alert range (`it.set.range`, never Near You's), each system a button; no security number; the count a 3 px tag (`.it-kl
  kh/kn`); Camp / ESS / kills from Near You's own rules in short form (`itEssTagHtml`, `itGateTagHtml(st, now, true)`,
  `itKillBadges(ks, 0, true)`). Written only when its text changes (from itMapDraw and itMapRefresh; ages on `it.drawNow`), never in
  the Intel example's picture (`itPtLive`: the live canvas only). `paths_to_you_check.py`.
- **Kills and losses in the system** (v2026.11.02.3, Project doc roadmap/system-activity-plan.md): one zKillboard request per
  system an hour (`/kills/systemID/<id>/pastSeconds/259200/`), then killmails from ESI newest first to the window or
  `SA_ACT_KM_MAX` (300). The system: an Intel Assess's, else ⚙ (`saSet`, localStorage dscanSaSet): your location from Intel or a
  typed gate system (SYS-03). Every group, corporation, pilot and hull counts its own kills (once, whole value) and losses; NPCs
  count for nobody; folds show none. Numbers that link out use `zkLinkHtml(url, what, text)`; inside a button they are text only.
  `system_activity_check.py`.
- **Ships on Scan** (v2026.11.02.2, Project doc roadmap/scan-rail-plan.md): the D-Scan's hulls in a rail left of Local's results
  (sticky, ~320 px; full width with no Local; stacked on a phone), by role from the ESI group (`SCAN_ROLES`); Cyno Capable and the
  cyno tag come from `CYNO_FIT` (tools/gen_cyno_table.py, never typed by hand). On grid ≤ `SCAN_GRID_KM`; a "-" is "no reading", its
  own count. One hover card (`#scanCard`), built when it opens, from the numbers the old per-type cards showed. No pilot is ever
  tied to a hull. `scan_rail_check.py`.
- **Fleet fits on request** (v2026.11.02.1, Project doc roadmap/fleet-fit-budget-plan.md): opening a fleet asks zKillboard nothing
  (fits from a share link or kept from the last hour load at once); Damage on the kill has its own column beside the ship; the Fit
  column has Load per row and Load all above it (Common fits above 10 pilots: one request per alliance-and-hull pair, victims in it
  get their own fit free; Own fits up to 10), its exact cost in its label. Load all keeps `FK_ZKB_RESERVE` (25) of `ZKB_BUDGET`,
  refused when counted (`zkbFetchNow` `o.reserve`, which can only lower the cap). Rows stay in damage order until all are in.
  v2026.11.04.5 (the owner: "retry should probably be the same Load and Load All buttons"): a failed lookup leaves the pilot unloaded
  with why on the row (`m.fail`, `fkFailShort`); no Retry in the head; Load and Load all count down on the button while zKillboard
  can't be asked (`zkbWaitMs`; the end redraws the tab, `data-zkb-redraw`), and "All loaded" only when every pilot is.
  v2026.11.04.6 (the owner): a row's countdown is only the time ("0:41", then "Load"), one width with Load (tabular digits).
  v2026.11.04.7 (the owner: "it's giving the impression that that tool just doesn't work"): the lookup that reached zKillboard and
  failed is red; the ones the pause held back (`notSent` on zkbFetchNow's error, `m.held`) say "Not sent", dim, why on hover (`fkFailSum`).
  v2026.11.06.4 (build queue 014, roadmap/zkb-slow-lists-plan.md; the owner: "would prevent dozens of rows with repetitive text"): what
  went wrong is an icon in its own column after Damage (`fkStHtml`, the one place its shape is drawn: red failed, amber slow, grey not
  sent; Fleet tab only, the shape and a site-wide rule wait for their own plan), its hover one short sentence with when to try again
  (`fkStWhy`), the summary head saying why once (`fkSumWhy`); workers claim a list so they spread over lists; common fits ask the
  week first (`pastSeconds/604800/` exactly, D1) and read whole killmails from the list (D2). `zkb_slow_check.py`,
  `fleet_fit_budget_check.py`, `fleet_vs_check.py`.
- **Lookup budgets** (v2026.11.04.4, Project doc roadmap/budget-gauge-plan.md; the owner: "have these numbers visible at all times"): the
  header's gauge beside the version tag (`#bgGauge`: zKill N/100, or "full" / "paused" m:ss; ESI ok, N errors, low or wait m:ss, from
  ESI's own headers; Kills only while Intel is on) and its panel (`#bgPop`: Used by, ESI by kind of lookup, the pause note; the shared
  close button). ESI only through `esiFetch(url, init, kind)`, which sends what it's given and reads the answer's headers
  (`ESI_KINDS`; check_request_gates); every zKillboard caller passes `{who}`. Kept in this browser: `dscanZkbWho` beside
  `dscanZkbBudget` (whose list of times keeps its old form), `dscanEsiUse` per minute per kind, saved at most once a second. One tick
  (`bgTick`) only while a countdown shows or the panel is open, never in a hidden tab; ZKB-01's text (`zkbUnavailableText`, matched by
  `ZKB_MSG_RX`) counts down wherever it is shown (`bgMsgSweep`). Amber when near, full, paused or stopped; never red.
  `budget_gauge_check.py`.
- **What's down, on every tab** (v2026.11.06.1, build queue 016; Project doc roadmap/outage-notices-plan.md section 7; mockup
  `Claude outputs/outage_notices_mockup.html`, scene "Kill feed can't be read"): the strip under the header (`#sysStrip`,
  `sysStripPaint`, `sysSituations`: one line per situation, the most important first, written only when its text changes; no close
  button, it goes when the cause does). 016 has one situation: zKillboard's kill feed can't be read (`itFeedDown`, INTEL-06): 3
  counted reads in a row with nothing the browser may read (`kf.blk`: sequence.json, or a read back's published kill; never a live
  kill file, LESSON #89), Intel on, the browser online; any readable answer clears it; never read since the page opened adds "or
  something in this browser blocking it". It also shows as Intel's Feed note (`.it-why`), "Kills down" in the gauge and on Intel's
  status line. Nothing extra is asked; the reader's pace is unchanged. `feed_down_check.py` (a real HTTPS stand-in, so the browser
  checks CORS itself). v2026.11.06.6 (build queue 015): the other lines, most important first: ESI down (`esiDown`: a lookup with no
  readable answer or 502/503/504, confirmed by one /status/, then /status/ once a minute only while down, `esiDownCheck`; only
  /status/ clears it; it takes over from the unreadable feed), EVE's daily downtime (`sysDowntime`: 4 minutes ahead of 11:00 UTC, one
  /status/ at 11:00, one clock timer `sysClockArm`), the zKillboard pause (ZKB-01's own text), the feed behind (`itFeedBehind`: fewer
  than `IT_FEED_SLOW_MIN` (40, the owner) kills in 15 minutes by R2Z2's uploaded_at, or a median age over 30 minutes, judged once
  the reader is at the newest; off after 5 minutes back). Each also as the Feed note (`itFeedWhy`), the status line and the gauge
  ("ESI down", "Kills slow"). A countdown in a line is a span.zkb-cd on the sweep; the line is rewritten only when its words change.
  v2026.11.06.6 (build queue 019, LESSON #140): a read-back keeps every readable kill; the unreadable ones are asked once more 6 s
  later, then, if published and sequence.json reads now, read past (`kf.skipped`); three all-skipped passes count as the feed down
  (`kf.allSkip`). `outage_check.py`.
- **Long lists stay in their box** (v2026.11.07.5, build queue 011; Project doc roadmap/list-caps-plan.md, mockup approved from
  list_caps_mockup.html): over 760 px the System Analyzer's Hostile and Neutral columns and the Ships on Scan rail are capped at the
  window (less 24 px) and scroll inside (`overscroll-behavior:auto`, LESSON #96); the columns' headings are sticky and "+N more groups
  below" (`saMore`, an empty `.sa-more` in the built markup, filled after a draw and on the column's scroll, never a timer); opening a
  group scrolls its column, never the page (`saShowGroup`); `saRender` keeps each column's scroll and the focus (`saFocusKey`). An
  opened group shows `SA_CORPS_SHOWN` (8) corporations, then "Show N more corporations" / "Show fewer" (`saCorpsMoreHtml`,
  `sa.corpsAll`). A corporation line is a grid: name, the ▲ and ▼ slots (`saActSlotHtml`, empty ones too), the count. `#scanCard`
  lives in `#saOut`, not the rail (`scanCardEl`, `scanCardPlace`: follows its row on any scroll, closes when the row leaves the
  rail's view). The dossier's kill rows past 10 scroll in a box exactly 10 rows + its sticky heading tall (`pdKlFit`, LESSON #146),
  "Show fewer" beside "Show 10 more"; its scroll survives `pdRender`. Show-more buttons there are amber (`.pdk-more`, `.sa-cmore`; v2026.11.07.6 also a corporation's "+N more" pilots `.sa-pilots .sa-link[data-more]` and the killmail's attackers `.lk-more`).
  760 px and under: unchanged. `list_caps_check.py`.
- **No time to kill for a whole fleet** (v2026.10.31.1, the owner: "given the fluidity of ranges in fleet battles ... we probably
  should not be giving a time to kill numbers"): a fleet's fits are guesses and each ship picks its own range, so the Fleet tab and
  the System Analyzer show what a fleet brings and how far it reaches, never how long you or they last (LESSON #108). One ship
  against one ship (the Matchup) keeps its numbers.
Checked by `tools/check_ui_rules.py` (chain) and `tools/page_checks/ui_rules_check.py`. Status colours (error, IN SYSTEM)
wait for the colour inventory (backlog).

When you find a new kind of mistake, add it to `LESSONS_LEARNED.md` (the next
unused number, and one line in its Index under the matching group:
`tools/check_lessons_index.py` checks it) and give the history doc a "Lesson
for future models" section. A lesson a later one overturns stays, marked
"Superseded by #n" at its top and in the Index. In code, mark the site
with a `// LESSON #n` comment that points at the entry.

**Checks: run what the change needs** (v2026.10.30.2, the owner: "yep, do it"; picked automatically since page-unchanged
v2026.10.31.7, the owner: "yes please" to the review's "choose the level from the changed files, not by hand").
`python3 -I tools/run_checks.py --auto` (with a .git folder: everything that differs from where the branch left `main`, committed or
not, `git merge-base HEAD origin/main`, so `git fetch origin` first; or `--since <a copy of main>` without one) runs the fast lints, then the tier `tools/check_picker.py` picks from the changed lines and files:
the engine, a PYFA CORE section or a calculation input (regression_suite/, the generators, the pyfa tools) -> `calc`; one
area's functions, CSS or info text -> `area` with those areas; shared code or anything unmapped -> `all`; every 5th delivery
-> `all`. `--plan` only says what it would run. Pick a tier by hand only to run more than it picks. When a section moves or a
new area gets its own prefix, update REGIONS / PREFIX / CSS in check_picker.py (its `--self-test`, a fast lint, says so).
Until 2026-11-08 `--auto` alone compared with the last commit, so once a branch's work was committed it ran only the lints (026); it
now says what it compared with on its second line. The CSP meta's script hash (it follows every edit) isn't a change of its own, and
git-ignored local files never count. `--plan` first when in doubt: a page change must pick page areas, not "fast" alone.
The fast lints include the regression suite, the D-Scan parse tests (seconds) and a check that PYFA_SRC is the verified pyfa commit (LESSON #116). A page check gets 5 minutes (`SLOW` for
more). A new page check gets its areas in `AREAS` (`--check-tags`, a chain step). A check that keeps failing under load gets
its cause fixed (LESSON #115); while that's under way it may go in the ledger's Quarantine table (a reason, at most 14 days;
an expired one fails the run). Run with `--ledger` and fill in "Caught" in `tools/check_ledger.md` before delivering; every 10
rows, review it with the owner (slow checks that never catch anything go to `all` only; repeat flakes get fixed). A new feature
still gets its own targeted check and mutants.

**How the numbers are worked out, for people:** `METHODOLOGY.md` (was the "How effective HP and DPS are
calculated" note on the page, removed in v2026.10.14.51); each card's short version is its ⓘ panel (`CARD_INFO`).
Change both when a calculation's assumptions change. Since build queue 036 (v2026.11.11.3) the panels are short (`check_subtext.py`:
85 words open, 210 in all, Intel 410), the detail is in METHODOLOGY.md (its Intel, Who's in the
system and Sides sections too), and nothing on the page links to it (build queue 037 took 036's footer link out, the owner: "i dont want that link displayed"). A paragraph may hold several `**Lead:**` parts (`infoBoldHtml`); a
panel never inherits a heading's case or spacing (`.info-body`; `info_panels_check.py`).

**After finishing any task,** check `todo-inbox/` for new requests the
owner wrote down while you were working: `new-bugs.txt` and
`new-backlog-items.txt`. If either file has entries, add each one to the bug
list or the backlog, then remove those entries from the text file and tell the
owner what you added. If both are empty, say nothing about it.

**Adding a backlog item or bug (when the owner asks).** The backlog is not in this repo. It lives in Claude's project memory for
this Project; new items go in the newest backlog file (`areas/dscan-backlog-3.md` today; `-2` is at its size cap), written with the memory tools in the
format `**Severity | Scope — Name** — [stated] "<the owner's words>"`, plus what's known and "Not started". Bugs go in the same
file, starting with `**BUG | …`. Never put the backlog in a repo file: the repo is public and the backlog quotes the owner.
**If you don't have the memory tools, say so and stop.** Tell the owner you can't add it to the backlog from here; don't write it
anywhere else.
Build queue: the Project docs folder `claude/build-queue/` holds prompts waiting to be built; read its README when the owner says to take the next item.
**Outside facts carry their source** (LESSON #147): the rule lives in the build queue README ("Facts from outside the project carry
their source"); `tools/check_plan_sources.py <plan.md>` enforces its shape. Planners and builders read it there.
**`todo-inbox/` is the owner's drop box.** Agents read it and empty it; agents never write new items into it.
