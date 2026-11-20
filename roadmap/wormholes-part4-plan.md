# Plan: Wormholes tab part 4: Routes, plus the Signatures type sort, the k-space → J auto-add, hole effects and the entrance ring

Status: **BUILT 2026-11-20 as v2026.11.20.2** (build queue 062, branch `062-wormholes-tab-part4`; see "Built" at the end for where the build differs).
Written 2026-11-20 by a research session against main 995f6a0 (v2026.11.19.1, after 061); all questions answered 2026-11-20 (section 9; Q5's group order from the owner in game the same day). **Queued as 062** (2026-11-20, the owner: [stated] "queue it"). Mockup: `Claude outputs/wh_part4_mockup.html`, round 2 (pinned routes as rows with strips; scripts roadmap/wormholes-part4-mockup/, 89 checks pass at 1440 and 390 px after the Set destination button was taken out and the game's group order put in the same day). check_plan_sources: 0 problems (3 UNVERIFIED rows for the hand test).

The owner, 2026-11-20: [stated] "ok, re-plan on the routes feature and let's plan to include a fix for the bug regarding sorting signatures by type. also include The k-space → J auto-add to Intel's Wormholes list and we need to add any affects that the hole has. also include Your chain's k-space entrance ring on the Intel map"

Replaces part 4 (D28) of `roadmap/wormhole-mapping-plan.md` (that doc's own text is not edited). Backlog: "BUG Signatures list: no sort by type", "Intel map: entering J-space from k-space adds … automatically"; the entrance ring is D14 of the mapping plan, not built in 048.

Panel review: not a fit (the page's code and a test settle the routing; the look is the owner's eye; easy to undo).

## 1. What changed since D28 was written (2026-11-12, main a0a0141)
- **056** put the tab's panels behind map controls: a rail at the top left (`whRailHtml` ~34067, `.it-map-rail`), one button per working panel, `tvWhPanels` `{v: 1, open: 'sum' | ''}`. Routes gets the second button.
- **059** made Signatures and Connections sections of the System panel, per-end signature IDs (`tvWhEnds`, `whEndSet` ~33927), and said Local becomes a System panel section (part 5). The rail ends as System + Routes.
- **047** computes Threat Vector's route **locally** with CCP's cost rule (`itRpUpdate` ~32803; matched against ESI's POST /route on 40 routes at its review, 2026-11-13). So D28's ESI request for Safer / Less secure isn't needed: the whole route, holes included, can be worked out in the page.
- **041 / 057**: jump bridges and Ansiblex zones join that search (`itJbZones` ~27373, one-way per direction).
- **051** left "Routes from here" out of the system menu until this part (~34882).
- **061**: statics and CCP's hole lifetimes and masses (`IT_WH_LIFE`, `whStcOf`).
- The info panels are nearly full: `whmap` 332 of 340 words, `intel` 667 of 670 (Q15).

## 2. Routes (the Routes panel)
**R1 One local search, no request (the session's choice).** The map table's systems plus your chain's systems as extra nodes; edges: stargates, the bridge directions 057 lets you use, and every chain connection both ways. The same ordering as 047: fewest flagged systems on the way, then the cost, then the fewest jumps. One search per change of its key (R8), as `itRpUpdate` does today. The build should split the search out of `itRpUpdate` into one function both call, so the two never drift (README "Reuse before adding"). Works logged out; nothing sent to ESI. The jump count includes the hole jumps (the owner, 2026-11-12: [stated] "add the extra "jump" to the count provided to the user as the number of jumps").

**R2 Cost of a hole jump (the session's choice; the owner didn't object when it was put to him 2026-11-20).** Prefer shorter: 1, like a gate. Prefer safer / less secure: into a J-space system costs as into nullsec (047's `2p`). J-space is as lawless as null.

**ROUND 2 (2026-11-20, the owner's feedback on the first mockup) replaces R4–R7 and Q3/Q4's single route:**
- [stated] "this needs to more closely reflect the in-game routing."
- [stated] "we need to be able to pin multiple systems that the page will automatically calculate the route to each time we navigate another system/wormhole."
- [stated] "the game's routing doesn't work inside of wormholes so it's only meant to be a point of reference. the example from wanderer reflects how to effectively represent multiple routes in a small space."
- On how a wormhole step reads: [stated] "ID not known isn't useful in this case. dont include it. system to system is fine in the absence of sig ids. pilots bookmark the holes so they'll likely use their bookmarks to navigate the chain anyway. sig id is useful if it was recorded but not required."
- His answers: [stated] "1. your pick for now" (wormhole squares in the wormhole colour with a hole mark); "3. your pick is correct" (pins kept in this browser until removed); "4. right click on system in the map should be an option along with the other options you mentioned"; "5. as pinned"; "7. yes, rework the mockup"; then "1. correct" (strip hover only, no opening rows) and "2. separate for now" (the Wormholes tab's own pin list, not Intel's map pins).
- Other tools' screenshots are reference for what they do only; the design is the page's own.

**R3 From where.** By default from where you are (`whS.last`, k-space or J-space). The system menu gets **Routes from here**: it sets the start for every row and opens the Routes panel. The panel then shows a "From where you are" button to go back.

**R4 Pinned routes.**
- One row per pinned system, recalculated every time you move (a gate, a wormhole, a location change). One search from where you are serves every row.
- Pin by:
  - typing a system (a J-name, Thera or a k-space name, as + Add reads them: `whIdOf`) and pressing Pin;
  - the map's right-click menu ("Pin route" / "Unpin route");
  - pressing × on a row to unpin it.
- The quick rows are always there, above the pins:
  - Home (when a system has the Home status, Q3);
  - nearest highsec;
  - nearest lowsec;
  - a quick row for where you already are is left out.
- Order: the quick rows, then the pins as pinned.
- Kept in this browser under a new key `tvWhRoutes` `{v: 1, pins: [ids], short}`, at most 30 pins. Separate from Intel's map pins (`itm.pinned`), which stay as today: in memory, cleared on every move.

**R5 A row.**
- One line:
  - the destination's security (or its class tag in J-space) in the page's security colours;
  - its name (a button that sets the focus when it's on your chain);
  - "Home" / "nearest highsec" / "nearest lowsec" for the quick rows;
  - ⚠N when the route passes N flagged systems;
  - the jump count, hole jumps included;
  - × for pins.
- Under it, the strip: one square per jump, in the arriving system's security colour. A long route wraps onto more lines (about 25 squares a line in the 340 px panel, 16 on a phone).
  - J-space squares are in the wormhole colour (`--it-wh`).
  - A jump through a wormhole is a round square, so it doesn't rely on colour alone.
  - A flagged system has an amber underline.
- Hovering a square (focus by keyboard; on a phone, a finger along the strip, which is one 44 px target) shows one line and dims the row's other squares:
  - a gate: "0.7 Ishisomo · The Forge";
  - a wormhole: "J122515 → Tama · TUV-907 (K162) · end of life · 0.3 Tama · The Citadel". The ID and type appear only when they were recorded (never "ID not known"); the warnings are the connection's life, mass and size (Q1).
- "No route" rows say so.

**R6 On the chain map.** Nothing is drawn until you hover a square. While you do, that row's hole steps glow along the chain under the connection lines (`--cyan`), its systems are outlined, and the exit carries "EXIT · then N j to <to>". It's part of the draw key: nothing timed (LESSON #120).

**R7 The panel; no hand-off to EVE.**
- A second rail button (`data-wh-rp="rt"`) and its panel `#whPnRt`. One panel is open at a time. `tvWhPanels.open` gains `'rt'`; an older page reads it as shut, so it's safe both ways.
- At the top: "From …", the **Shortest** switch (on: the fewest jumps for every row; off: Intel ⚙ → Routes' preference), and the Pin field.
- **No Set destination, no hand-off.** The rows show the route as the panel draws it, for reference; nothing is sent to EVE from the Routes panel. The owner, 2026-11-20: [stated] "ok, just dont worry about setting the route from inside j-space then. get rid of the "set destination" button and we'll just show the route as it's represented in the panel." This replaces Q4's "pin it on Intel's map" and round 2's per-row Set destination.
  - Why, for the record: EVE's autopilot can't plot while you're in wormhole space (sources), and ESI only adds waypoints, from where you are. Intel's map clears its kept routes on every move (`itm.pinned.clear()` when `itm.home` moves, ~30682), so a pin set from inside the hole wouldn't survive the jump out. Two other ways were put to the owner and set aside: sending the gate part as waypoints from inside J-space (UNVERIFIED that the game keeps them; ESI answers 204 even when the game drops a destination, 047's hand test), and arming a send for when the page sees you reach the exit.
  - Out in k-space, the Intel map's own route and its Send (047) are there as today.

**R8 When it's worked out again.** When any of these change: you (your system), the start, the pins, Shortest, the chain's connections and their recorded IDs, Intel settings → Routes (preference, avoid options, the bridge zones), the flagged systems. All are part of one key. Never on a tick.

**R9 One set of route settings.** The k-space part follows Intel settings → Routes, the same settings as the Intel map's route. The panel names them in one line ("Prefer safer · avoiding camps, kills …: change in Intel ⚙ → Routes"), with no copy of the settings in the tab.

## 3. Signatures: sort by type (the BUG)
The owner, 2026-11-18: [stated] "need to be able to sort by type. this is actually the default in the game. unscanned items at the top, then scanned in the order provided".
- **S1** A new sort key `ty` in `WH_SG_SORTS` (~33888). The icon column's heading holds the Select all box (`whLHeadHtml`), so in the mockup the name column's heading becomes "Type" and sorts by it (names sit inside their type anyway). This is a design choice for the owner to judge in the mockup; `nm` stays readable in a stored sort.
  - Its order: rows with no group known yet first (the red × rows; [stated] "unscanned items at the top"), then by group in the game's own order (Q5 [stated] "The game's order"; the owner, from the game 2026-11-20: [stated] "unscanned, wormhole, gas site, data site, relic site, asteroid belt, combat site, then the rest for now. i dont have an example with every type right now."), then within a group by the paste's order.
    - So: Wormhole, Gas Site, Data Site, Relic Site, Ore Site, Combat Site, in one table (`WH_SG_TY_ORDER` or a field of `WH_SG_ICON`'s table), so a change is one line. "Asteroid belt" is read as the page's `Ore Site` group (the probe scanner's group for ore sites; the page has no "Asteroid Belt" group): UNVERIFIED, the owner's next in-game look.
    - A group the page doesn't list goes after Combat Site, alphabetical by group, then by the paste's order ([stated] "then the rest for now").
  - An older page reading `{k: 'ty'}` falls back to Age (`whSortRead`), so it's safe both ways.
- **S2** The paste's order. Each row gains `o`, its place in the latest paste that listed it; rows not in the latest paste go after, in their old order (Q7 [stated] "Latest paste (Recommended)"). It's saved under `tvWhSigs`; an older page drops the field when it next saves, and rows without `o` go after those with it. Today `whScanApply` (~34585) rebuilds the rows sorted by time then ID, and every row of one paste shares its time, so the order is lost.
- **S3** Type becomes the sort for everyone once (Q6 [stated] "Switch everyone once"): `tvWhSigs` gains `sv: 2`; a store without it gets `sort: {k: 'ty', d: 1}` and `sv: 2` on its first read, and after that the sort you pick is kept. Known edge: an older page's save drops `sv`, so after a revert and a return the switch happens once more. First-time users start on Type too.
- Connections list: unchanged.

## 4. Auto-add: jumping into J-space puts that k-space system's wormhole in Intel's Wormholes list
The owner, 2026-11-20: [stated] "when entering a wormhole from k-space, automatically add a wormhole to the wormhole list of the intel map. when making this transition, the page already captures all of the needed information about the wormhole aside from the signature ID in k-space. perhaps this should be toggled on/off in the intel settings but something to think about."
- **A1 Where.** In `whSeen` (~33980), at the k-space → J-space step that already adds both systems and the connection (not docked). The J → k step too: leaving a chain adds that k-space exit, under the same switch (Q9 [stated] "Yes, same switch (Recommended)"). The switch: in Intel settings beside "keep wormhole reports for", on by default (Q8 [stated] "Switch, on (Recommended)"); a new field of Intel's settings, read as on when missing, so an older page's save keeps the default.
- **A2 What it writes.** It merges into `tvWormholes`, as `itWhTake` (~31688) merges a report, never as `itWhAdd` (~32687), which replaces a whole entry and would drop its IDs.
  - `t` is the jump's time and `src: 'you'` (an older page shows "added by you").
  - `info.cls` is the J system's class where `IT_WH_CLS_RX` takes it (C1–C6, C13, Thera; a Drifter system: none).
  - A new field `jw: {j: <J system id>, t}` records which system you jumped into. The row's words are worked out from it when drawn: name, class, effect, statics. An older page drops the field, and the entry stays as a hand-added hole. Safe both ways.
  - Kept by Intel's "keep wormhole reports for" (24 h by default, 48 h at most), as every entry.
- **A3 The row.** "you jumped in → J123456 (C3 · Pulsar) · statics …", in place of "added by you". The hover gives the effect's numbers (E1).
- **A4** The k-space signature ID typed later on the Wormholes tab's connection end (`whEndSet`) fills the Intel entry's ID, one way, Wormholes tab → Intel (Q10 [stated] "Yes (Recommended)"). Removing one never removes the other (Q11 [stated] "No, separate (Recommended)").
- **A5** Export (046) shares it as one of your own holes (`src: 'you'`), without `jw`. The Intel example (`itWhAside`) never sees any of it.

## 5. Hole effects
The owner: [stated] "we need to add any affects that the hole has". Read here as the J system's effect (Black Hole, Cataclysmic Variable, Magnetar, Pulsar, Red Giant, Wolf-Rayet), with its numbers, wherever the page names the system. Confirmed: Q12 [stated] "Name and numbers (Recommended)".
- **E1 The data.** CCP's 36 effect beacons, "Class 1–6 <effect> Effects", group 920. Each lists the attributes it changes, e.g. Class 3 Pulsar: shield HP ×1.58, signature ×1.58, armor resonances +29%, capacitor recharge time ×0.71, neut/nos strength ×1.58. These come from pyfa's copy of CCP's data at the manifest's commit e5483f8 (sources).
  - `tools/gen_wh_table.py` writes them as a small table, `IT_WH_EFF_MOD`, about 1 KB.
  - The direction and words come from each effect's operation and the attribute it modifies, through a short hand-written words table. A resonance up is "armor resists worse", never "resist +29%".
  - The build checks the wording against the game's info window for one system (UNVERIFIED, hand test).
- **E2 Which strength.** `INTEL_WH` stores only the effect's letter, and the strength is assumed to follow the system's class. That doesn't hold for 25 shattered systems (all Wolf-Rayet) and 5 Drifter systems with an effect: the class of their beacon is UNVERIFIED. So `tools/jump_table_update.py` stores each system's beacon class number, read from the beacon's name, instead of guessing. That runs through the game-data workflow, because the build sandbox can't reach CCP's data.
- **E3 Where it shows.** The System panel's Effect line, with its numbers under it, one line each (the mockup's choice, for the owner to judge), the auto-added Intel row (A3), and the route's hole steps. Text only: the analyzers' fit numbers don't change.

## 6. Your chain's k-space ends on the Intel map (D14's ring)
The mapping plan's D14: "your chain's k-space ends get phase 1's wormhole ring" (not built in 048).
- **K1** `itMapWh` (~32195) adds a mark for every k-space system on your chain whose connection was seen within Intel's "keep wormhole reports for" (24 h by default; Q13 [stated] "Seen recently (Recommended)").
  - It's drawn like a live report: thin wormhole rings on every filter, and 045's bold mark with the Wormholes filter on.
  - It's one mark per system, merged with an Intel entry if there is one.
  - The hover says "On your chain → J123456 (C3 · Pulsar)".
- **K2** `itMapWhKey` covers it, so the map redraws only when the set changes. In J-space it sits under the "YOU · <entry>" pin. Never in the Intel example (`itWhAside`).

## 6b. Mockup and Reuse, don't add
Mockup `wh_part4_mockup.html` (2026-11-20, main 995f6a0; round 2 the same day; scripts roadmap/wormholes-part4-mockup/, README there). It shows:
- the Routes panel's pinned rows with their strips (hover a wormhole, hover a gate, Routes from here, out in k-space);
- a row's route on the chain map while you hover it;
- Signatures by type;
- a C3 Pulsar's numbers;
- Intel's Wormholes list with the auto-added holes, the ring at C-J6MT, and the Intel settings switch.

89 checks pass at 1440 and 390 px (round 2, with a 40-jump route to 1DQ1-A whose strip runs to two lines: [stated] "include an example with two rows of jumps in the route please"; then the Set destination button taken out, R7, and the game's group order put in, S1).

| Mockup piece | The build uses |
|---|---|
| `.rt-ty` field + Pin button | `.it-rp-add` (047's avoid-list add row) |
| `.rt-row` / `.rt-l1` row on `--panel-2` | Near You's row cards (`--panel-2` rows, 052) where they fit; else new on purpose |
| `.rt-strip` / `.rt-q` squares in `.it-sn s0–s10` | new on purpose: nothing on the page draws a route as squares; the colours are the page's own classes |
| `.rt-tip` hover line | the map's tooltip look (`.it-map-tip`) if it can sit in a panel; else new |
| `.rt-rm` small × button | the map's small controls (`.it-map-zoom` look) or `.it-whp-xb` for × |
| `.rt-short` switch | the page's one switch (CLAUDE.md UI rules) instead of the mockup's checkbox |
| `.rt-w` ⚠N | `.it-warn` |
| `.rt-eff` effect lines | one `.wh-kv` row per line (the panel's own label / value look) |
| `.rt-top` From line + button + switch | a flex row like `.it-rp-add`; no new class if one fits |
| the route icon `RT_ICON` | new on purpose: rule A gives each panel its own map control icon |
| `graph` / `search` | the search split out of `itRpUpdate` and shared (R1), not a copy |
| `#rtBar`, `RTscene`, the `whDraw` hooks | mockup only; not built |

## 7. UI rules it touches
- **Map controls (rule A)**: the Routes button is one more rail control (`.it-map-rail`), neutral, 30 px / 44 px on a phone, aria-pressed. Its panel is a view: no close button, no Escape (056).
- **One tag, one chevron, colour tokens**: the EXIT pill and step tags are `.it-gtag`; the route glow is `--cyan`, as the Intel map's route; no new colours.
- **Subtext**: the panel's settings line is short, the rest behind ⓘ (`check_subtext.py`).
- **Drawing cost** (LESSON #120): route and ring in the draw keys; nothing timed.
- **Phone**: the Routes panel is a sheet beside the rail like System's; 44 px buttons; each strip is one 44 px target, read by moving a finger along it (its squares are too small to be targets one by one); no sideways scroll at 390 px.
- **Not colour alone**: a jump through a wormhole is a round square, a flagged system has an underline, and every square's hover names its system and security.
- **Text fields and checkboxes**: the "To" field and the Intel setting use the global styles.
- **Intel example**: the ring and the auto-add never reach it (`itWhAside`), so its markers and notes don't change.
- No conflict found. Mockup: yes (Q14 [stated] "Yes, mockup (Recommended)").

## 8. Info text it touches
- `whmap`:
  - a new "[Routes]" paragraph: pinned rows worked out on every move, the quick rows, the strip and its hover (holes round), Shortest, a reference only (EVE can't plot from J-space), about 55 words;
  - "[Signatures]" gains the Type sort, about 8 words;
  - "[Focus and adding]" names the effect's numbers under the Effect line, about 5 words.
  - That's about 389 of 340: the cap is raised (Q15 [stated] "Raise the caps (Recommended)"; about 400, exact when the wording is written, `INFO_ALL_MAX_BY_KEY` in tools/check_subtext.py).
- `intel`:
  - "[Map]" Wormholes sentence: your chain's k-space ends are marked too;
  - "[Tags]" or the Wormholes list's words: jumping in adds the hole (the setting).
  - About 22 words, so about 689 of 670: the cap is raised to about 700 (Q15).
- `IT_EX_NOTES`: none.
- The build repeats the search against its diff (README "Info text stays true").

## 9. Questions for the owner (recommended first); ANSWERED 2026-11-20
Answers: Q1 "Use them, warn (Recommended)"; Q2 "Ignore statuses"; Q3 "Yes (Recommended)"; Q4 "Pin it on Intel's map (Recommended)" (superseded 2026-11-20: no hand-off to EVE, R7); Q5 "The game's order", then "I'll check in game", then the order itself (S1); Q6 "Switch everyone once"; Q7 "Latest paste (Recommended)"; Q8 "Switch, on (Recommended)"; Q9 "Yes, same switch (Recommended)"; Q10 "Yes (Recommended)"; Q11 "No, separate (Recommended)"; Q12 "Name and numbers (Recommended)"; Q13 "Seen recently (Recommended)"; Q14 "Yes, mockup (Recommended)"; Q15 "Raise the caps (Recommended)". The questions as asked:

Routes
- **Q1** Holes near their end (critical mass, end of life, small ships only): use every connection and warn on that step (Recommended) / leave out critical and end-of-life holes / a switch in the panel.
- **Q2** Systems you marked Dangerous or Target on the chain: count as flagged, like Intel's avoid options (Recommended) / ignore statuses.
- **Q3** A "Home" destination (the system with the Home status): yes (Recommended) / no.
- **Q4** Handing off the gate part (the game can't plot from J-space):
  - pin the destination on the Intel map, so when you come out at the exit, Intel's map already shows the route and you can send it to EVE from there (Recommended);
  - text only (D28's line);
  - also a "Send to EVE" from inside J-space (UNVERIFIED that the game takes waypoints there).

Signatures
- **Q5** Order between types: alphabetical by group: Combat, Data, Gas, Ore, Relic, Wormhole (Recommended until we know the game's) / the game's order (you tell us which comes first).
- **Q6** A sort you already chose (say Age): keep it (Recommended) / switch everyone to Type once.
- **Q7** "In the order provided" = the latest paste's order (Recommended) / the paste that first listed it.

Auto-add
- **Q8** The setting: a switch in Intel settings beside "keep wormhole reports for", on by default (Recommended) / off by default / no switch.
- **Q9** Leaving a chain into k-space adds that exit too: yes, same switch (Recommended) / only entering from k-space.
- **Q10** A k-space ID typed later on the Wormholes tab fills the Intel entry: yes (Recommended) / no.
- **Q11** Removing it from one list removes it from the other: no, they stay separate (Recommended) / yes.

Effects
- **Q12** What "effects" means:
  - the effect's name and its numbers as text, where the system shows (Recommended);
  - the name only;
  - also applied to fit numbers in the analyzers (its own later item: pyfa's handlers, PYFA_CORE).

Ring
- **Q13** Which of your chain's k-space systems get the ring: those whose connection you saw within "keep wormhole reports for" (Recommended) / only while you're in J-space / every one on the chain, always (the chain never expires).

Process
- **Q14** Mockup: yes (Recommended) / no.
- **Q15** Info caps: raise `whmap` to about 400 and `intel` to about 700 (Recommended; exact numbers when the wording is written) / cut other wording to fit.

## 10. Checks to build
- `wormhole_routes_check.py` (new):
  - the quick rows and the pins, in the order pinned;
  - the strip: one square per jump; holes round; J-space squares in the wormhole colour;
  - the hover line for a gate and for a hole, with the ID only when recorded;
  - routes through the chain then gates, a k-space start into J-space, a bridge used one way only;
  - every row worked out again after a jump (gate, hole, location), with one search;
  - no quick row for where you are;
  - pin by typing, by the map menu, × to unpin; `tvWhRoutes` kept and read by an older copy as nothing;
  - Shortest kept;
  - your statuses don't change a route (Q2);
  - no Set destination in the panel, and nothing sent to ESI from it;
  - Routes from here and back;
  - the map draws a row only while a square is hovered;
  - `tvWhPanels` `'rt'` read by an older copy as shut;
  - 1440 / 390 px: 44 px targets (the strip as one target), no sideways scroll, no page errors.
  - Mutants: hole edges one way only; the hole jumps not counted; one search per row instead of one for all; an "ID not known" text.
- `wormhole_sigs_check.py`: the Type order (unscanned first, then Wormhole, Gas, Data, Relic, Ore, Combat, then a group not listed, then paste order); a remembered Age sort switched to Type once and the next pick kept (Q6); an older page's rows (no `o`). Mutant: rows sorted by ID inside a group.
- `wormhole_tab_check.py` or a new `wormhole_autoadd_check.py`:
  - k → J adds and merges (IDs kept);
  - docked doesn't add;
  - the switch off adds nothing;
  - J → k adds the exit (Q9);
  - the switch read as on when missing (an older page's settings);
  - the Wormholes tab's k-space ID fills the Intel entry, and removing one leaves the other (Q10, Q11);
  - `jw` dropped by an older reader;
  - the example sees none of it.
  - Mutant: `itWhAdd` used in place of a merge.
- `wormhole_statics_check.py` (or new): the effect's words for each of the 36 beacons match the table; a shattered system uses its own beacon class. Mutant: the strength taken from the system's class.
- `wormhole_filter_check.py`: the chain's k-space ends ringed on every filter, bold with Wormholes on, none in the example. Mutant: a stale end ringed past Q13's limit.

## 11. Where to look (main 995f6a0)
- **Routes:** `itRpUpdate` ~32803 (the search to share), `itRpCost` ~32773, `itRpFlags` ~32782, `itJbZones` ~27373, `itMapPin` ~32715.
- **Wormholes tab:** `whRailHtml` ~34067, `whPnRead` / `whPnSet` (tvWhPanels), `whPanels` ~34796, `whDraw` ~34183, `whPaint` ~34155, `whMenuHtml` ~34892 (the "Routes from here" comment ~34882), `whLinksOf` ~33880, `tvWhEnds` / `whEnd`.
- **Signatures:** `WH_SG_SORTS` ~33888, `whSortRead` ~33893, `whSgRowRead`, `WH_SG_SORT` ~34416, `whSgListHtml` ~34437, `whListHtml` ~34385, `whScanApply` ~34585.
- **Auto-add:** `whSeen` ~33980, `itWhTake` ~31688, `itWhAdd` ~32687, `itWhRead` ~31504, `itWhEntryRead` ~31730, `itWhRowsHtml` ~32359, Intel settings' "keep wormhole reports for" ~29755.
- **Effects:** `WH_EFF` ~33738, `whEff` ~33783, `whSumHtml` ~34316, `tools/gen_wh_table.py`, `tools/jump_table_update.py` (mapSecondarySuns ~144).
- **Ring:** `itMapWh` ~32195, `itMapWhKey`, `itMapWhBold`, the marks loop in `itMapDraw` ~31080, `whEntry` / `whIntelSys` ~34007.

## 12. Page size
Served 636,231 bytes at 995f6a0 (ceiling 800,000). Expected: well under 15 KB gzipped (the effects table about 1 KB, the code a few KB).

## 13. DLA
Not touched in a new way. No new requests or data about other players: your own jumps, kept in this browser, shared only by your own Export, as 046 does today.

## Sources
| Fact | Source | Checked | Status |
|---|---|---|---|
| The autopilot can't plot a route while you're in wormhole space | https://support.eveonline.com/hc/en-us/articles/203273861-Can-t-set-route-to-destination (CCP support) | 2026-11-20 | verified |
| ESI's route cost rule (Shorter / Safer / Less secure, penalty) that 047's local search follows | https://developers.eveonline.com/docs/guides/route-calculation/ (CCP developer docs), as checked at 047's review | 2026-11-13 | verified (047's review; this plan reuses that code) |
| Effect beacons: 36 types "Class 1–6 <effect> Effects", group 920, each with its attributes (e.g. Class 3 Pulsar: shieldCapacityMultiplier 1.58, signatureRadiusMultiplier 1.58, armor resistance bonus 29, rechargeRateMultiplier 0.71, energyWarfareStrengthMultiplier 1.58) | https://github.com/pyfa-org/Pyfa/tree/e5483f8666ed2eda99c98985c59a29b07e3bb844/staticdata/fsd_built : types.0.json–types.5.json, typedogma.0.json–typedogma.2.json and dogmaattributes.0.json at e5483f8 (v2.70.0; pyfa's build of CCP's SDE, the manifest's commit) | 2026-11-20 | verified (CCP's data as pyfa ships it; the build session re-read Class 3 Pulsar, 2026-11-20) |
| The beacons' effects: e.g. systemArmorEmResistance modifies armorEmDamageResonance with operation 6, systemShieldHP shieldCapacity with operation 4 | https://github.com/pyfa-org/Pyfa/tree/e5483f8666ed2eda99c98985c59a29b07e3bb844/staticdata/fsd_built : dogmaeffects.0.json at e5483f8 (pyfa's build of CCP's SDE) | 2026-11-20 | verified; how each reads in the game's words is UNVERIFIED: hand test, a system's effect info window in the game against the page's line |
| Shattered (25, all Wolf-Rayet) and Drifter (5) systems carry an effect | the page's INTEL_WH at 995f6a0 (CCP's SDE build 3698585 via tools/jump_table_update.py) | 2026-11-20 | verified (project data from CCP's SDE) |
| Which beacon class those 30 systems use | none | 2026-11-20 | UNVERIFIED: the game-data workflow's run of the changed jump_table_update.py (mapSecondarySuns.effectBeaconTypeID → the beacon's name) |
| The game's Probe Scanner order when sorted by its type column: unscanned, Wormhole, Gas Site, Data Site, Relic Site, asteroid belt, Combat Site, then the rest | the owner, from the game: [stated] "unscanned, wormhole, gas site, data site, relic site, asteroid belt, combat site, then the rest for now" | 2026-11-20 | verified (the owner's in-game look) |
| The game's "asteroid belt" there is the page's `Ore Site` group | none (the owner: [stated] "i dont have an example with every type right now") | 2026-11-20 | UNVERIFIED: the owner's next in-game look with an ore site in the list |
| The Local log and EVE's location report J-space systems (tracking) | the owner's use of 048: [stated] "i've been navigating wormholes for a while with this" | 2026-11-14 | verified (the owner's use) |

## Built (2026-11-20, v2026.11.20.2, build queue 062)
Decided at the build review (2026-11-20): the 30 shattered / Drifter systems show their effect's name with no numbers until `INTEL_WH.effc`
arrives through the Jump table workflow's pull request ([stated] "1. recommended: no guessed numbers"); after the merge the build session starts
that workflow by hand ([stated] "2. sure.").

Where the build differs from the plan:
- **The auto-add's setting** is kept in `tvWormholes` (`auto`, beside `keepH`, the "keep wormhole reports for" it sits next to), not in Intel's own
  settings (`dscanIntel`). Read as on when missing; an older page's save drops it either way.
- **`jw`'s reader** checks the J-space ID range with literals, not `whIsJ`: it runs at start-up, before the Wormholes part of the script (LESSON #175).
- **Effects** are emitted as percent changes with the generator's own words table (`EFF_WORDS`; "Armor damage taken +29%" for a resonance), not the
  mockup's "(resists worse)" text; a beacon attribute without words stops `gen_wh_table.py`.
- **Bridges** in the Routes search come from the same `itJbZones` as Intel's route; no Routes case covers a bridge step.
- **The squares** are focusable spans, one tab stop a strip, the arrow keys (Home / End) stepping along it, not buttons. The hover line reuses
  `.it-map-tip`; the unpin × is `button.it-sigx`; the Pin field is `.it-rp-add` / `.it-rp-msg`; the Shortest switch is `input.mys-sw` in `label.mys-use`.
- **Info caps**: `whmap` 400, `intel` 675 (the wording came to those; Q15).
- **Checks**: `wormhole_routes_check.py` (plus an equivalence case: 047's route equal to f70fdd5's for several homes, flags and preferences),
  `wormhole_effects_check.py` (the 36 beacons derived from pyfa's data without the words table), `wormhole_autoadd_check.py`; Type and the chain's
  ends in `wormhole_sigs_check.py` and `wormhole_filter_check.py`.
