# Plan (BUILT, 067, v2026.11.24.1): the Intel map's "Within N jumps" becomes "Distance", in jumps or light years

Status: READY 2026-11-20 (research session, main e72ba18, v2026.11.20.2 plus the jump table update). All questions answered (section 2); mockup sent (section 8). **QUEUED as build queue 067** 2026-11-20 ([stated] "queue it"; `claude/build-queue/067-ly-distance.md`).
Planning list item E1 / 5 (`claude/roadmap/intel-planning-list.md`; research and answers: `claude/roadmap/intel-later-filters-research.md`, section E1). Backlog entry (dscan-backlog-7): [stated] "modify "within N jumps" filter to be "Distance: jumps / light years" … gives the user awareness of what systems are within jump range of them with cynos depending on type."

Build after 065 and 066 (all three change `itMapStackRead` and the `intel` Info text's cap).

Panel review: not a fit (the outside facts are CCP's data and the owner's confirmation; the rest is the page's own code).

## 1. What exists (main e72ba18; find by name)

- **The Only filter "Within N jumps"** (058): `IT_MAP_FILTERS` entry `near` ("only: systems this many stargate jumps from you or fewer"), matched in `itMapMatch` by `D[i] >= 0 && D[i] <= s.near.n` (your jump bridges counted while they're on). Its settings panel is `itMp` (`itMpBodyHtml('near')`: the stepper `RS.mapNear`, 1–30, and a note), opened beside the filter's settings button. The Only line (`itMapOnlyHtml`) says "within N jumps".
- **The stack** `tvMapStack`: `itMapStackBlank` has `near: {n: 5}`; `itMapStackRead` checks `near.n` (1–30). `itMapStKey` holds `s.near` whole, so new fields in it join the match's key with no change.
- **Light years:** `itMapLy(i, j)` (3D, from `INTEL_MAP.p3`); `itMapLyText` rounds up to 0.01. The hover already shows "N LY from <your system>".
- **Security:** `itMapSecT(i)`, the number the map shows, in tenths. Regions: `itMapTable().regions` / `.reg` (Pochven is there). Zarzakh (30100000) is not in the page's jump table today.
- **The page's one stepper** `RS` / `rsHtml` / `rsPaint` (typed on a computer, snapping to the nearest step; read-only on a phone); `RS.mapSecLo` / `mapSecHi` already use `show` / `read` for tenths.

## 2. The owner's answers

- 2026-11-16 (dscan-backlog-7): [stated] "A later item (Recommended)", "Shade systems in range (Recommended)" (not a ring: a circle on the 2D map of 3D space is inexact), "Type LY now, ship picker later (Recommended)", "Not for now (Recommended)" (not its own Colour).
- 2026-11-20: [stated] "Within N jumps → Distance (Recommended)" (one filter, a Jumps / LY switch in its settings); "Only where a jump can land (Recommended)" (high-sec, Pochven and Zarzakh left out, with a hover note); "Typed + quick picks (Recommended)"; "From you, mockup yes (Recommended)". The landing rules: [stated] "i can confirm".

- 2026-11-24, the build review (build session, main aa55779, v2026.11.23.3): [stated] "Add 7.5 LY pick (Recommended)" (Command Carriers, 3.75 LY base, found in pyfa v2.70.0's data; D5); "Raise to ~754 (Recommended)" (the `intel` cap, set from the final count; section 5); "Use that wording (Recommended)" for the note with jump bridges on (D1).

## 3. What changes

**D1. The name:** "Within N jumps" → **"Distance"**; note "only: systems within N stargate jumps of you, or N light years where a jump drive can land". With jump bridges on (`itMapFNote`, 057's second note; the build review): "only: systems within N jumps of you (jump bridges you can use counted), or N light years where a jump drive can land". Same button, icon and place. Its settings button's label "Distance: how far".

**D2. The stack:** `near: {n, mode: 'j' | 'ly', ly}`; `ly` in tenths of a LY, 1–200, default 70 (7.0 LY); `mode` default `'j'`. `itMapStackRead`: a missing or bad `mode` → `'j'`, a missing or bad `ly` → 70, `n` as today. An older page reading a newer stack ignores the two fields (safe both ways).

**D3. The match (`itMapMatch`, `near`):** Jumps as today. Light years: `itMapLy(i, home)` rounded up to 0.01 as `itMapLyText` shows it (so the hover and the filter never disagree) is `ly / 10` or less, and the system is landable. Your own system matches as today.

**D4. Landable:** not `itMapSecT(i) >= 5` (0.5 or higher, the number the map shows), not in Pochven, not Zarzakh (by ID, in case the jump table ever holds it). One small function beside `itMapSecT`, returning the reason ('high-sec' / 'Pochven' / 'Zarzakh' / '') for the hover.

**D5. Settings panel (`itMpBodyHtml('near')`):** a switch at the top, **Jumps / Light years** (radios, Sov upgrades' `.it-sov-k` look, through 065's `itMpRadHtml`; focus stays on the switch when the panel redraws). Jumps: today's body unchanged. Light years: the stepper `RS.mapLy` ("Within [7.0] LY", 0.1 steps, `show` `(v / 10).toFixed(1)`, `read` `Math.round(parseFloat(t) * 10)`, why "At least 0.1 LY" / "At most 20.0 LY"); quick picks **6 / 7 / 7.5 / 8 / 10 LY** (`.it-mp-q`, aria-pressed on the one equal to the value; titles "Titans, supercarriers", "Carriers, dreadnoughts, FAX", "Command carriers" (the build review), "Black Ops, Lancers", "Jump freighters, Rorqual", each "…, Jump Drive Calibration V"); note "Straight-line from your system, as the hover shows. Only where a jump drive can land: not high-sec, Pochven or Zarzakh. Quick picks: range at Jump Drive Calibration V."; the match count as today. The body is built again when the switch changes.

**D6. Hover** (with Distance on, in light years, not your system): in range and landable → "within jump range (7.0 LY)"; in range but not landable → "in range, but a jump drive can't land here (high-sec)" (or Pochven / Zarzakh). Out of range: nothing added (the "N LY from you" line is there already).

**D7. The Only line:** "within 7.0 LY (jump drive)" in light years; "within N jumps" as today.

**D8. Unchanged:** Jumps mode (bridges counted, the note about "Map: within"), every other filter, the Colour "Jumps", Paths to you, the Intel example (it shows the filter's name only in its column picture: the build checks `intel_example_check`).

Later (backlog, not this build): a ship picker (the owner: "ship picker later"); measuring from a system you pick (the owner: "From you"); light years as a Colour ("Not for now").

## 4. UI rules it touches

- **Colour not the only carrier:** the match is the map's usual bright / dim; the hover and the Only line say it in words.
- **One stepper:** `RS.mapLy` is the page's stepper (no new input); typed values snap to the nearest 0.1.
- **Phone:** the stepper is read-only there, so the quick picks carry it; the switch and quick picks are 28 px tall (the `.it-mp-q` buttons) and the panel fits 390 px (mockup checked).
- **Drawing cost** (LESSON #120): the match is worked out once per key (`itMapMatch`'s cache; `s.near` is in the key already); the LY per system once per match, not per draw.
- **Saved settings:** the stack only (`tvMapStack`), no new key.

## 5. Info text it touches

- `intel` [Map]: after "Only filters, any number, all must match (their settings beside them)" add "; Distance counts stargate jumps, or light years where a jump drive can land" (+13 words; the cap is raised in 062, 065 and 066; the build fits it after them). The build review: the cap was 741 of 741 (071); raised to the final count, about 754 ([stated] "Raise to ~754 (Recommended)").
- `RS.mapNear`'s title: "Within N jumps: …" → "Distance in jumps: systems this many stargate jumps from you or fewer". `RS.mapLy`'s title: "Distance: light years from your system, where a jump drive can land".
- The page checks that name the filter (`intel_map_stack_check`, `intel_map_look_check`, and `paths_to_you_check` (found at the build review): "Within N jumps") follow the new name.

## 6. DLA

- None new: the page's own map data (positions, security, regions); nothing read from ESI, nothing new stored but two fields in the existing stack.

## 7. Questions for the owner

None open (section 2). The owner saw the mockup and queued it as is ([stated] "queue it").

## 8. Mockup (2026-11-20)

`ly_distance_mockup.html` (sent to the owner; scripts `claude/roadmap/ly-distance-mockup/`, README there; built on main e72ba18; `test_ly.py` 73 checks pass at 1440 and 390 px; check_pii: only the page's CCP login button image). MOCKUP box: 5 jumps (today), 6 / 7 / 10 LY, Off. At 7 LY from C-J6MT, 186 systems match; at 10 LY, 313.

### Reuse, don't add

| Need | Reused | New (why) |
|---|---|---|
| Distance | `itMapLy`, `itMapLyText`'s rounding | none |
| The filter | `near` in `IT_MAP_FILTERS`, its button and panel (`itMp`) | the name and note |
| Saved | `tvMapStack` (`itMapStackBlank` / `Read`; `itMapStKey` already holds `near`) | two fields, `mode` and `ly` |
| Number entry | `RS` / `rsHtml` with `show` / `read` (as `mapSecLo`) | `RS.mapLy` |
| Quick picks | `.it-mp-q` (Security range's) | none |
| Switch | `.it-sov-k` radios (Sov upgrades') | none |
| Landable | `itMapSecT`, `itMapTable().regions` | one small function (high-sec, Pochven, Zarzakh's ID) |

## 9. Checks (for the build)

- In light years, the match equals the rule worked out apart (rounded-up LY ≤ the value, not 0.5+, not Pochven, not Zarzakh), for every system on the map; your system matches; the hover's LY and the filter agree for every system.
- Jumps mode matches exactly as before (bridges on and off).
- The stack: saved and read back; an older stack reads as Jumps with its N; bad values fall back; an older page reading the new stack works.
- The panel: the switch redraws the body and keeps focus; quick picks set the value and press one; an off-pick value presses none; the stepper shows tenths and snaps typed values; the count follows.
- The Only line and both hover lines; the Info text within its cap; 390 px: the panel fits, no sideways scroll.
- Mutants: the raw LY instead of the rounded one (a system shown as 7.00 LY left out); high-sec counted as landable (0.5 by the true security rather than the shown one); Pochven kept; Jumps mode changed.

## Built (build queue 067, v2026.11.24.1, branch `067-ly-distance`)

Built 2026-11-24 from main aa55779 (v2026.11.23.3). Where the build differs from the plan above:
- **Quick picks:** five, 6 / 7 / 7.5 / 8 / 10 LY (`IT_MP_LY_QUICK`); 7.5 for Command carriers (3.75 LY base in pyfa v2.70.0's data), the owner at the build review: [stated] "Add 7.5 LY pick (Recommended)".
- **The switch:** 065's `itMpRadHtml` (the `.it-sov-k` radios) in an `.it-mp-row` with role radiogroup (`itMpNearModeHtml`); no class of its own. The pressed quick pick is the one new CSS rule (`--tag-on`).
- **One rounding:** `itMapLyC` (hundredths, rounded up) is used by both `itMapLyText` and the filter (`itMapLyIn`), so the two can't drift; landable is `itMapNoLand` with `IT_MAP_NOLAND` (Pochven by region, Zarzakh by ID).
- **The note with jump bridges on** (`itMapFNote`, which the plan didn't cover): "only: systems within N jumps of you (jump bridges you can use counted), or N light years where a jump drive can land", the owner: [stated] "Use that wording (Recommended)".
- **Info cap:** `intel` 754 (the final count), [stated] "Raise to ~754 (Recommended)".
- **Mutants:** the plan's "raw LY instead of the rounded one" is equivalent for a range set in whole tenths (rounding up then comparing with a whole number of hundredths is the same test), so it could never fail; the check mutates rounding to the nearest instead, with a system just past a tenth in its world (LESSON #180). The "high-sec by the true security" mutant became 0.5 counted as landable (the page holds only the shown tenth since 063).
- **Checks:** `tools/page_checks/ly_distance_check.py` (new, 11 mutants; also checks that main's page reads the new stack). `paths_to_you_check` named the filter too.

## Sources

| Fact | Source | Checked | Status |
|---|---|---|---|
| Jump ranges by ship group (attribute 867 `jumpDriveRange`): Titan 3.0, Supercarrier 3.0, Carrier / Dreadnought / FAX 3.5, Black Ops / Lancer 4.0, Jump Freighter / Capital Industrial 5.0 LY | CCP's SDE, pyfa `staticdata/fsd_built` (typedogma, groups) at pyfa b79cd90 (https://github.com/pyfa-org/Pyfa) | 2026-11-20 | verified |
| Command Carrier group (Salvation, Simurgh, Gaia, Ymir): `jumpDriveRange` 3.75 LY, so 7.5 LY at Jump Drive Calibration V (the build review) | CCP's SDE, pyfa `staticdata/fsd_built` (typedogma attribute 867, groups) at pyfa e5483f8, v2.70.0 (https://github.com/pyfa-org/Pyfa); the other groups' values above read the same there | 2026-11-24 | verified |
| Jump Drive Calibration +20% range per level, so ×2 at V (6 / 7 / 8 / 10 LY) | CCP's SDE, pyfa `staticdata/fsd_built` at pyfa b79cd90 (https://github.com/pyfa-org/Pyfa): type 21611 `jumpDriveRangeBonus` 20 and its description | 2026-11-20 | verified |
| No jumping into 0.5 security or higher | CCP's article "Dreadnoughts & Jump Drives", https://www.eveonline.com/article/dreadnoughts-jump-drives | 2026-11-20 | verified: the owner, a player, confirmed it 2026-11-20 ([stated] "i can confirm") |
| Pochven and Zarzakh can't be jumped into | secondary: EVE University wiki "Pochven"; the owner's confirmation 2026-11-20 ([stated] "i can confirm") | 2026-11-20 | verified: the owner, a player, confirmed it (not a secondary source alone) |
| Zarzakh's system ID is 30100000 | a live ESI answer (https://esi.evetech.net) read from threatvector.space in the owner's built-in browser during this research; not in the page's jump table (checked in main e72ba18) | 2026-11-20 | verified |
