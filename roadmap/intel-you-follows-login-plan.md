# Intel settings: "You" follows your EVE login while Use my game location is on

**Status:** planned 2026-11-15 by a research session against `main` 491ecad (v2026.11.15.2). **Queued as 054** 2026-11-15 ([stated] "ok queue it"; `claude/build-queue/054-intel-you-follows-login.md`). Build **after 052** ([stated] "after 052"). No mockup (owner's choice: [stated] "no mockup"). Sources: none (no outside facts). **Built** 2026-11-16 as v2026.11.16.2 on branch `054-intel-you-follows-login` (from `main` 51207b6); see "Built" at the end.

Backlog: "Intel settings: "You" follows your EVE login while Use my game location is on" (dscan-backlog-5, 2026-11-12).

## 1. Why

[stated] 2026-11-12: "currently if i log into the tool and turn on "use my game location", should we disable the radio buttons in intel settings for who to track? i noticed some weird behavior with this the other day and forgot to log it."

What the code does today (491ecad):
- Intel's "You" is `it.me`, looked up from the radio pick `it.set.me` among the characters with a Local log in the folder (`itScan` ~27172: `it.me = it.set.me ? it.chars.get(it.set.me) || null : null`). Radios: `itCharsHtml` (~29019), in `itSettingsHtml`'s box 3 "You" (~29034), click handler ~31779.
- Use my game location applies only while the picked character is the login (`itGlWho` ~28240). Pick another and it stops quietly, with an amber line (`itGlWarnHtml` ~28294 in Intel; the same words in `eveFeatLine('loc')` ~24485 on the EVE tab).
- Three problems:
  1. Picking another character turns game location off with only a warning line.
  2. Changing the radio doesn't reset `itGl` (the last game reading), so switching back can briefly reuse an old system.
  3. A logged-in character with no Local log in the folder isn't in `it.chars`, so it can't be picked and game location never applies.

## 2. Decisions (the owner's)

- **D1. While logged in with Use my game location on, the radios go; the EVE tab's row shows instead.** [stated] 2026-11-12: "when logged in and use my location is turned on, use the same style and message as in the eve tab the profile (replaces any list of radio buttons). only see radio buttons when you're not logged in w/ use my location enabled."
- **D2. The row is the lamp and the status line only, no switch.** [stated] 2026-11-12: "only the light and status line. let's keep the setting controls inside of the eve settings panel."
- **D3. The "Game location: … · Set on your profile's EVE tab" line (`itGlHtml`'s `.it-gl-sub`) goes in every state.** [stated] 2026-11-12: "i am leaning no but what do you think?", then "unless you see a reason to keep it for any reason." after the session recommended dropping it.
- **D4. No mockup.** [stated] 2026-11-15: "no mockup" (the row already exists on the EVE tab; this plan gives before/after in words, section 5).
- **D5. Login ended (SSO-06 `sso.lost`) with the switch on: keep the row, reading "Paused: log in again".** [stated] 2026-11-15: "your choice works" (the session's recommendation: otherwise "You" quietly jumps back to the saved pick while the user thinks EVE is tracking them).
- **D6. Logged in, no Local log for that character: "You" works from EVE's location alone, with a dim line "No Local log for <name>: your system comes from EVE only".** [stated] 2026-11-15: "your choice works".
- **D7. Game location's error messages (`itGl.msg`: SSO-07, SSO-08 with Log in again) also show under Intel's row** (as well as on the EVE tab). [stated] 2026-11-15: "your choice works".
- **D8. Build after 052.** [stated] 2026-11-15: "after 052" (052 restyles the radios, rule C, and moves the Intel tab's layout).
- Research session's calls (not asked; the build review can raise them): the "your login isn't You" warning is removed in Intel and on the EVE tab (nothing can trigger it any more); the saved radio pick `it.set.me` is never changed by this (it comes back on Log out or the switch off).

## 3. What to build

### 3.1 Who "You" is: one function

- New `itFollowLogin()`: true when `it.set.gameLoc` is on and either `sso.who` is set, or `sso.lost` with `side.rec.pilot` (the login ended; the pilot stays, `ssoLost` ~24768). Its character: `sso.who` when set, else `side.rec.pilot` (`{id, name}`).
- New `itMeResolve()` replaces the one-line `it.me = …` in `itScan` (~27172) and is also called when the login or the switch changes (below):
  - following the login: `it.chars.get(id)` when that character has a Local log; else a stand-in `{id, name, sys: '', noLog: true}` (no `st`, no `file`);
  - otherwise: `it.set.me` as today.
- `itScan`'s pick of which channel log to watch (~27158, `f.charId === it.set.me`) uses the resolved character's id, so your own client's log is preferred for the login's character.
- The Local-log read in `itTick` (~27233, `itReadFile(it.me.st, …)`) skips a stand-in (no `st`). `itLogSys` returns null for it, so `itMySys` uses the game location alone (`itGlSys`), which already needs `itGl.at > (it.me.logAt || 0)`: with no log, `logAt` is 0, so any game answer is used.
- When the resolved character changes (login, Log out, `ssoLost`, the switch, a Local log appearing for the stand-in on a rescan), do what the radio handler does today (~31779): `it.lastScan = 0; it.alerted = new Map();`, plus `itGlReset()`, then `itRender()`. This fixes problem 2. Hook points: `ssoFinish` / `ssoEnd` / `ssoLost` (they already call `renderSidePanel`), `itGlToggle`, `itGlGranted`, and the end of `itScan`. Compare the old and new id so nothing redraws when it didn't change (LESSON #120). **Superseded at the build review (section 10, gap 1): one `itMeSync()` from `renderSidePanel` and the end of `itScan`.**
- `itGlWho` (~28240) and `whLocOn` (~32377) then hold whenever the switch is on and logged in (the resolved `it.me` is the login by construction); keep their `sso.who` test (a lost login asks nothing).
- `ssoOnIntelHtml` (~25117, "Your character is logged off in EVE.") already compares `it.me` with `sso.who`; it now shows for the login's character while following. No change needed beyond the resolve.

### 3.2 The "You" box

`itSettingsHtml` box 3 (~29034):
- **Following the login (D1, D5):** no radios. One row in the EVE tab's own style: `pp-led` lamp + the feature's name "Use my game location" (`SSO_FEAT_NAME.loc`) + its ⓘ (`intel#game`) + the status line from `eveFeatLine('loc', pfModel().F.loc, pfModel())` (~24485), drawn by the same pieces as `eveFeatHtml` (~24524) **without the switch** (D2). The checked time stays in its own span (`data-it-glat`, written by `itGlTimePaint`). Then `itGl.msg` with Log in again (D7), and, for a stand-in, the dim D6 line (`ctxHtml`, under 40 characters where it can be: "No Local log for <name>: your system comes from EVE only" is longer: put it as the row's second dim line, not as subtext under a heading; check_subtext decides).
- Easiest: split `eveFeatHtml` into the row's head (`eveFeatRowHtml(k, m, {sw: false})`) so the EVE tab and Intel draw the same markup; the EVE tab passes `sw: true`.
- **Otherwise:** the radios as today (`itCharsHtml`), with 052's look.
- **Every state:** `itGlHtml`'s `.it-gl-sub` line ("Game location: … · Set on your profile's EVE tab", the `gl-open` button) goes (D3). `itGlWarnHtml` goes (no longer reachable). The `gl-open` action handler and `.it-gl-sub` CSS go if nothing else uses them (grep).
- The EVE tab's `eveFeatLine('loc')` loses its first branch (the "Your EVE login is X, not Y" warning, ~24489). Its other lines stay: "Intel is on in another tab", "Needs EVE's OK…", "Paused: log in again", "Game: X, the same as your Local log", "Game: X (newer, used) · your Local log still says Y", "From your EVE login, while Intel runs".
- `itGlKey` (~28242) gains the resolved id and the stand-in flag, so the box redraws when they change.
- The Intel status line (`itStatusLine` ~29071, "<name> in <system>") needs nothing: the stand-in has a name, and an unknown system already reads "an unknown system".

### 3.3 Stored data

None changes. `it.set.me` and `it.set.gameLoc` keep their form in `dscanIntel`; the resolve happens in memory. Safe both ways: an older page reads the same settings and shows its radios.

## 4. UI rules it touches

- **One switch:** no new switch; Intel's row has none (D2), the EVE tab keeps the only one.
- **Status not by colour alone:** the lamp always comes with its status words (`eveFeatLine`'s `t`).
- **Subtext rule / check_subtext:** the D6 line is a status line in a row, not subtext under a heading; keep it one line where possible; run `check_subtext.py`.
- **Colour tokens:** reuse `pp-led` / `pp-fs` `data-l` states; no new colours.
- **Phone (390 px):** the row wraps like the EVE tab's; no sideways scroll; the Log in again button 44 px.
- **052's rules (built first):** rule C (radio look) still applies to the radios in the other state; rule B (panels over the map) doesn't touch Intel's settings.
- **Intel example (017):** the setup screen draws `itSettingsHtml(true)` (~29354); the example itself runs logged out with its own `it.me` (~29189), so its numbered "You" box keeps its radios. Check 017's marker check still passes; no marker or note change expected.
- **Drawing cost (LESSON #120):** the box redraws only when `itGlKey` changes; the checked time moves in its own span.

## 5. Before and after (in words, D4)

- **Logged in, switch on, the login has a Local log.** Before: radios (both characters), the "Game location: Tama, from EVE · Set on your profile's EVE tab" line. After: one row, lamp lit, "Use my game location ⓘ", "Game: Tama, the same as your Local log · checked 12:04:31 UTC".
- **Logged in, switch on, another character was picked.** Before: radios with the alt picked, amber "Your EVE login is Main, not Alt: log in as Alt, or pick Main as You." and no location read. After: the same row as above; Intel follows Main; the alt pick is kept for later.
- **Logged in, switch on, no Local log for the login.** Before: radios without the login (or "No Local log in this folder…"), game location never used. After: the row ("From your EVE login, while Intel runs", then "Game: Tama · checked …") and the dim line "No Local log for Main: your system comes from EVE only".
- **Login ended, switch on.** After: the row, amber, "Paused: log in again", plus the SSO-08/SSO-06 message with Log in again when there is one.
- **Logged out (Log out pressed), or switch off.** Radios, as today, the old pick back; no "Game location" line.

## 6. Info text it touches

- `CARD_INFO["intel#game"]` [What it needs] (~3681): "Your EVE login in the tab running Intel, as the character you picked as You, and EVE's OK to read your location (…)" → "Your EVE login in the tab running Intel and EVE's OK to read your location (…). While it's on, Intel follows the logged-in character: Intel settings' You shows its status instead of the list." Keep the cap (`check_subtext.py`).
- `CARD_INFO.intel` [Jumps and your system] (~3661): reads true as is ("from your character's Local log, or from EVE with Use my game location on"); check after the build.
- Search `CARD_INFO` and `IT_EX_NOTES` for "pick", "as You", "Game location" before the pull request (README "Info text stays true").

## 7. Checks

Extend `tools/page_checks/sso_game_check.py` (it already has MAIN / ALT logs, a stand-in SSO and the location answers):
- Logged in + switch on: the "You" box has no `[data-it-me]` radios and has the row (lamp, name, status line, no `input[type=checkbox]`); the "Game location: …" line is gone.
- ALT picked, then logged in as MAIN with the switch on: You = MAIN, location requests go out (today's ~397 case, "the login's character isn't You: an amber line, no request", becomes "Intel follows the login, requests go"); after Log out, ALT is picked again (`it.set.me` unchanged).
- Switching the pick back and forth no longer reuses an old `itGl.sys` (problem 2): after a resolve change the first status shows no system until a fresh answer.
- Login with no Local log (a third made-up character): the row shows, the dim "No Local log for …" line shows, the map/status take the game's system.
- `ssoLost` with the switch on: the row stays, amber "Paused: log in again"; no requests.
- SSO-08 / SSO-07 messages show under Intel's row and on the EVE tab.
- Logged out or switch off: radios back, no row, no "Game location" line.
- 390 px: no sideways scroll; Log in again ≥ 44 px.
- Mutants: the radios still drawn while following; `it.me` from `it.set.me` while following (requests stop on the ALT pick); no `itGlReset` on a resolve change; the stand-in read as a Local log (throws or reads `st`).
- Also re-run `sso_online_check.py` ("another character as You: no line": with the switch off it still holds; add a case with the switch on: You follows the login, so the logged-off line shows for it), `intel_one_tab_check.py`, `wormhole_tab_check.py` (`whLocOn`), `intel_example_check.py`, `check_subtext.py`, `check_ui_rules.py`.

## 8. Hand test (the owner)

Setup (branch name is the queue item's):
```
git fetch origin
git checkout NNN-short-name
python3 -m http.server 8000
```
Open http://localhost:8000 (the dev app's address). Back to main afterwards: `git checkout main`.

1. Log in with EVE, Use my game location on, Intel on. Intel ⚙ → You: one row with the lamp and its status, no list, no "Game location" line.
2. Log out: the list is back with your old pick. Pick your alt, log in as your main again: the row is back and Intel follows your main (status line names the game's system).
3. Log in as a character that hasn't logged into the game since the folder's last 2 days (no Local log): the row shows "No Local log for <name>…", and the map follows the game's location once it answers.
4. Turn the switch off on the EVE tab: the list is back.
5. Phone width (390 px, the browser's device view): the row wraps cleanly, no sideways scroll.

## 9. Where to look

`itScan` (~27120–27175), `itTick` (~27222–27240), `itGl*` (~28230–28320), `itCharsHtml` / `itSettingsHtml` (~29019–29060), the `data-it-me` handler (~31779), `eveFeatLine` / `eveFeatHtml` (~24485–24530), `pfModel`, `ssoFinish` (~24806), `ssoEnd` (~24850), `ssoLost` (~24768), `ssoLogout` (~24870), `whLocOn` (~32377), `ssoOnIntelHtml` (~25117), `CARD_INFO["intel#game"]` (~3679). Line numbers are at 491ecad; 052 will move them.

## 10. Build review, 2026-11-16 (against main 51207b6, v2026.11.16.1; ANSWERED by the owner 2026-11-16)

Done by a build session that couldn't get write access, so it stopped after the review; the next build session took it from here, found `main` unchanged (51207b6) and the line numbers below still right, and put the four gaps to the owner. `check_plan_sources` 0 problems. 052 and 053 moved line numbers only: the functions the plan names are all still there and work as the plan describes (now: `eveFeatLine` 24557, `eveFeatHtml` 24596, `ssoLost` 24840, `ssoFinish` 24878, `ssoEnd` 24922, `ssoLogout` 24942, `ssoInit` ~24971, `ssoTabInit` ~25022, `ssoOnIntelHtml` 25189, `itScan` 27191 (the `it.me = …` line 27246), `itTick` 27296, `itGl*` 28313–28390, `itCharsHtml` 29102, `itSettingsHtml` 29117, `itStatusLine` 29154, the `data-it-me` handler 32323, `whLocOn` 32921, `CARD_INFO["intel#game"]` 3742). The Intel example check still runs logged out and picks the `[data-it-me]` radios, so its markers aren't touched.

Four gaps, put to the owner with these proposals; he took all four (2026-11-16, the question dialog, each "(Recommended)" option):
1. **Hook points miss two login changes:** a reload with a saved login (`ssoInit` restores `sso.who`) and the copied-tab drop in `ssoTabInit` (sets `sso.who = null` without `ssoEnd`). Proposal: one `itMeSync()` (resolve, compare the id, reset only on a change) called from `renderSidePanel` (every login path ends there) and at the end of `itScan`, instead of separate hooks. The second build session added: `renderSidePanel`'s first line runs before its "panel open" test, and both switch paths (`itGlToggle`, `itGlGranted`) end in it. **Answer: "Yes, one itMeSync()".**
2. **The D6 line before the folder is read:** with no folder chosen or not read yet, every login looks log-less. Proposal: show "No Local log for <name>…" only once `it.read`. **Answer: "Only once the folder is read".**
3. **Intel's warning names the Local log for a log-less You:** index.html ~29445 "Your system isn't known yet (it's read from your Local log when you jump), so no jumps and no alerts until then." Proposal for a stand-in only: "Your system isn't known yet (it comes from EVE once it answers), so no jumps and no alerts until then."; unchanged otherwise. **Answer: "Yes, that wording".**
4. **Info text:** `CARD_INFO["intel#game"]`'s first paragraph says "the line under the box shows both, in amber"; with Intel's Game location line gone (D3) that points at nothing. Proposal: "the status line shows both, in amber". Plus section 6's [What it needs] change as planned. **Answer: "Yes, "the status line"".**

Hand test setup (use these, not section 8's): `git status`, `git fetch origin`, `git switch 054-intel-you-follows-login`, `git pull`, `python -m http.server 8000` (Windows: `py -m http.server 8000`), open `http://localhost:8000/`; Ctrl+C stops it; afterwards `git switch main`, `git pull`.

Hand test step 3, as the owner can run it ([stated] 2026-11-16: "i do not have a character without a local log."): copy his `Chatlogs` folder (e.g. `Documents\Chatlogs-054-test`); in the copy only, delete the `Local_*.txt` files ending in the test character's id; Intel ⚙ → Chat logs folder → Change… to the copy; log in with EVE as that character, Use my game location on, Intel on. Pass: the row with "No Local log for <name>…", and the status line and map take the system he's in in game (undock or jump to see it move). Then Change… back to the real folder and delete the copy. The copied channel logs don't grow, which doesn't matter here; the automated check covers the same case with a made-up character.

## Built (v2026.11.16.2, 2026-11-16)

As planned with the four answers in section 10. Where the build differs from sections 3–7:
- **One `itMeSync(scan)`** (gap 1) instead of the hook list in 3.1: from `renderSidePanel` (through `pfTry`, since it runs before Intel's part
  of the script exists), the end of `itScan` and the end of Intel's start-up load (a login restored before Intel's settings were read). A
  change (by id, and the stand-in flag) resets `itGl`, `it.alerted` and, outside a scan, `it.lastScan`, then one `itRender()`; a scan's call
  leaves the redraw to its caller. The radio handler goes through it too, so a new pick also drops the old game answer (problem 2).
- **`ssoLost` sets `sso.lost` before `ssoEnd()`**: otherwise any redraw in between saw "not following" and flipped You to the pick and back,
  resetting the alert memory twice.
- **The stand-in** is kept while its id stays the login's (so `sysAt` survives a redraw); `itTick` reads a Local log only when `it.me.st` exists.
- **Gap 3's wording** also goes into the map's empty line ("Your system isn't known yet (it comes from EVE once it answers).") for a stand-in.
- **The row:** `eveFeatHtml(k, m, {intel: true, more})` with small builders (`eveFeatAttrHtml`, `eveFeatNameHtml`, `eveFeatMoreHtml`,
  `eveFeatSwHtml`) so `check_html_sinks` passes (its baseline shrank 1507 → 1506); the name is a span (no label for a switch that isn't there),
  `data-it-glrow` instead of `data-feat`, the message from `itGlMsgHtml` (its Log in again works inside Intel). The state colours of `.pp`
  also apply under `.it-gl`. `itYouListHtml`, `itNoSysText`, `itNoSysWarnHtml`, `itGlNoLogHtml` are new.
- **Removed:** `itGlWarnHtml`, `.it-gl-sub`, the `gl-open` action, `eveFeatLine('loc')`'s "Your EVE login is X, not Y" branch.
- **Info text:** `intel#game` (gap 4 and section 6); METHODOLOGY.md's Intel section got one sentence. `CARD_INFO.intel` reads true as is.
- **Checks:** `sso_game_check.py`'s `follow_case` (ALT picked then login, the old answer dropped, the requests, `ssoLost`, Log out, a third made-up
  character with no Local log, the folder not read, the EVE wording, the switch off) and 6 mutants; D7 and 390 px cases; `gl_on` now goes through
  `itGlToggle`; it gets 15 minutes in `run_checks.py`'s SLOW. `sso_online_check.py`: the switch on makes the logged-off line follow the login.
  `intel_logs_check.py`: its mutant quotes `itScan`'s new line (`meId`).

## Sources

Sources: none (no outside facts). The location read, its scope and its timing were built and sourced in build queue 028 (roadmap/sso-phase2-plan.md); this plan changes only which character it applies to and how Intel's settings show it.
