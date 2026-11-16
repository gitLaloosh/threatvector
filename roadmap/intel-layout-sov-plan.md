# Plan: the Intel tab's new layout, and a Sov upgrades map filter

**Status (2026-11-16):** planned by the research session against `main` 9459b35 (v2026.11.15.1). Mockup sent (round 6b). All questions answered (section 12): **two deliveries**, part 1 (layout, rules A–C, example) then part 2 (Sov upgrades). **Queued 2026-11-15** ([stated] "yes please"): part 1 as **052**, part 2 as **053**. **Part 1 BUILT** in v2026.11.15.3 (PR #57, merged 2026-11-16, main e7f5a2b; section 13). **Part 2 BUILT** in v2026.11.16.1 (build queue 053; section 14). Moved to the repo's `roadmap/` with part 2's delivery, with the mockup scripts in `roadmap/intel-layout-mockup/`.

Backlog: memory `areas/dscan-backlog-6.md`, "Intel map: sov upgrades filter with its own pick list" (all quotes and rounds are there). The later item "Intel map: the right-side panel toggles a Routes list" builds on this layout; it gets its own planning session.

## 1. Why

[stated] 2026-11-14: "i've got a list of sov upgrades that i'd like to be able to apply to the map like filters but i'd like to be able to pick and choose which ones so this will need to be similar to the wormhole filter in that it will have a settings panel. this also raises the question about how to handle multiple map filters that have settings panels (right now wormholes have to be on the far right to accommodate the list."

The owner asked for a design cycle on the whole tab first: "i'm wondering if the intel map needs to be more like the wormholes map. incorporate near you into a bigger map, place the feed below it. i'd like you to explore this and give me some options."

Six mockup rounds later, the result is:
- the map full width and taller;
- Near You as a panel inside the map, behind one button;
- the filters in a column down the map's left side, each filter with a panel getting its own panel button;
- the Feed below, full width;
- a new Sov upgrades filter on pasted lists.

## 2. The owner's decisions (in order)

- Layout A, filters with their own panel button, lists each on their own: "I like option A with filters having their own settings button (show/hide on hover) but show me an option that shows them above the filter's button. for sov lists, each list on it's own so it can be replaced or edited separately."
- Near You's button: "buttons should adhere to the styling of our other buttons. dont use the amber outline and text. we need an icon to denote the near you feed so give me some options. reduce the size of the button to match other buttons on the page (filters, center on me, etc) and reduce the width of the panel to match that change. we want the map to be the prominent feature when everything is collapsed. when you expand the "near you" list, the panel and any other buttons should still be present and clickable".
- Buttons follow the site's rules: "the buttons should match the design rules for the site. if those aren't clear enough, we can revisit that during this process." The rule was missing from CLAUDE.md; asked whether to write it, he said "sure" (section 6, rule A).
- Filters on the left: "i wonder if we should put filters on the left side and feeds on the right. ... with filters on the left, lists and settings would display to their right with the name line moved to the right of that?" → picked "Down the left".
- Panel style: "the two panels have different styles. sov upgrades has a lighter background. it's almost like they're opposites." → picked "Site panel style" (section 6, rule B).
- Checkboxes and radios: "can we treat radio buttons and checkboxes like text inputs with regard to colors?" Round 6 showed two checked looks; he picked "cyan tick, dark box" (section 6, rule C).
- Near You icon: "i need more options. one of those options should be an exclamation point or something that infers "alert"." He then sent a picture of a feed icon. Answer: "feed is the one, badge stays."
- Sov upgrades data and look:
  - "Paste now, ESI later" (an ESI read is a later item);
  - "Kind, level shown" (pick by kind; the level shows in the hover);
  - "Until replaced" (nothing expires);
  - cyno list = "Cyno beacons";
  - "Bright / dim";
  - "More kinds later" (name-only lists can be other kinds);
  - navigation from "The bridges paste (041)" (no second paste);
  - 041: "Lift hold, cleaned list only".

## 3. What the code does today (main 9459b35; find by name)

(Part 1 changed most of this; section 13 says what main has since e7f5a2b.)

**Layout:**
- `.it-top` holds the map column (`.it-mapcol`, the map in `itm.box`) beside Near You (`.it-nearcol`, `#itNearList`).
- The Feed (`.it-feedcol`) sits below.
- On a phone, a List | Map switch (`.it-nv`, `it.set.nearView`, saved in `dscanIntel`) shows one of the two.
- Map height in `itMapRefresh`:
  - wide: `max(IT_MAP_MIN_H, min(560, w·0.72))`;
  - phone: `min(460, max(320, w·1.1))`.
- `IT_NEAR_FLOOR` is `IT_MAP_MIN_H + 50`.

**Filter bar:**
- `.it-map-fb` is centred at the map's foot. It holds:
  - the name line `.it-map-fn` (shown with `.named` or on hover);
  - the phone's one-button `.it-map-fcur` (`itMapFbarOpen` opens the row);
  - the toolbar `.it-map-fbtns` (`itMapFbtnsHtml`, from `IT_MAP_FILTERS`).
- The Wormholes list button `button.it-whl` floats right of the bar. That's why Wormholes must be the last filter.
- The list itself `.it-whp` (`itWhListOpen`) is a dialog over the map, above the bar (`right:8px; bottom:56px`).
- `itm.fbBox` keeps labels off the bar. `itMapYouArrow` keeps the "you" arrow off it by assuming a bar at the foot.

**Map controls:**
- `.it-map-zoom` (+ − ⤢ ⌖, 30 px, neutral `rgba(18,23,28,.9)`, `--line` border, cyan on hover; 44 px on a phone).
- The route planner's search box `.it-rp-search` sits at the top left, hidden on Paths to you (048).
- The Wormholes chip `button.it-map-whn` sits at the bottom left.

**Controls styles:**
- Plain checkboxes and radios are the browser's own (white): 11 checkboxes, 4 radio groups (Intel channels, sound, Routes options, Drifter, the System Analyzer's source, …).
- Switches (`.mys-sw`, `.dmg-sw`) have their own rule.
- Action buttons are the global `button` (amber outline and text). A panel's main action is `.mys-primary` (amber fill).

**Intel example** (setup screen):
- `itExRowsHtml` draws a static `.itx-top` (map picture `itExMapPic` beside Near You) and the Feed.
- Five markers (`itExPlace`): 1 a Feed report, 2 a Near You row, 3 the map, 4 an alert row, 5 a kill badge.
- `IT_EX_NOTE3_PHONE` ("switch {near} to Map …") replaces note 3 on a phone, where the example shows no map.

**Jump bridges (041, queued, not built):** `bridges` / `bridgesOn` in `dscanIntel`; `itBridges()` gives the bridge list (`edges`).

## 4. Part 1: the layout

**4.1 The map and the Feed.**
- The map takes the card's full width:
  - wide: height `min(720, max(520, w·0.5))`;
  - phone: height `min(600, max(440, w·1.45))`.
- The Feed stays below it, full width, unchanged.
- The List | Map switch goes: the map always shows and Near You lives in it. `nearView` stays in `dscanIntel` untouched, so a reverted page still reads it.
- `IT_NEAR_FLOOR` and the side-by-side sizing go.

**4.2 Near You, behind one button.**
- **The rail:** a column of map buttons (`.it-map-rail`, `role=toolbar`, "Map panels") under the zoom buttons at the top right, 8 px below them.
- **The button:**
  - It's in the map control style (rule A): 30 px (44 on a phone), the feed icon (`IT_FEED_ICON`, our own drawing: a small square in the bottom-left corner and three arcs; `currentColor`).
  - It carries a count badge: the number of Near You rows, top right. It turns amber (`--amber`, dark text) when a row is in your alert range.
  - Pressed, it uses `--tag-on`, with `aria-pressed`, `aria-controls` and a title "Near You: N systems[, some in your alert range] (press to show/hide the list)".
  - Today the rail holds only this button. The Routes list (its own plan) adds the next one.
- **Shut:** nothing else of Near You shows; the map comes first.
- **Open:** Near You's list (`.it-nearcol`, its heading and `#itNearList` as today) opens to the left of the rail:
  - wide: 320 px, from the rail's top to 8 px above the map's foot;
  - phone: the map's width less the rail.
  - The rail, the zoom buttons and the filters stay where they are and stay clickable.
  - Rows use the narrow form (tags on their own line under the system) as in the mockup's grid.
  - The "+N more systems below" line stays.
- Near You is a view, not a dialog: no close button, no Escape (the rail button shuts it; rule 5 covers info and settings panels).
- Remembered across visits (Q2, [stated] "remember"): `nearShown` (true/false) in `dscanIntel`, default shut. An older page drops the key when it saves its settings, which is harmless; the new page reads a missing key as shut.

**4.3 Filters down the left.**
- **Column:** `.it-map-fb` becomes a column at the map's left edge, 8 px under the search box (on a phone, under the search box and the zoom row). It keeps its place on Paths to you, where the search box is hidden, so it never jumps.
- **Wrapping:** the toolbar is a grid that fills its rows top to bottom and wraps into a second column when the map is too short (a phone; more filters later). Rows = filters that fit between its top and the map's foot.
- **Phone:** the column is shut behind its one button (`.it-map-fcur`, as today's row). Picking a filter shuts it (as today). The open column and Near You's list take turns: opening one shuts the other.
- **Filter order:** free now that the list button no longer forces Wormholes to the end. Proposed: Security, Jumps, Regions, Reports, Kills, Wormholes, Sov upgrades (part 2), Paths to you.

**4.4 A panel button for each filter with a panel.**
- Wormholes keeps `button.it-whl`. Sov upgrades gets its own (part 2).
- **Wide:** a filter's panel button floats to the right of the column, level with its filter. It shows:
  - on hover or focus of the filter (a hover bridge across the gap, the 0.6 s grace as today);
  - while its filter is on;
  - while its panel is open.
  - Touch screens: only while the filter is on (no sticky hover after a tap; hover rules inside `@media (hover:hover)`).
- **Phone:** only the panel button of the filter that is on shows, inside the column beside its filter.
- **Style:** map control style (rule A).

**4.5 The name line.**
- `.it-map-fn` sits to the right of the panel buttons (wide), or to the right of the column (phone). It's level with the filter that is on, or with the column's one button when it's shut on a phone.
- It stops before the Near You rail or list; when there's no room beside the column (phone, two columns), it goes under it.
- It shows as today (`.named`, hover), and hides while a filter's panel is open, because the panel's heading names it.

**4.6 A filter's panel.**
- **Wide:** it opens to the right of the panel buttons, level with its filter, kept inside the map (top ≥ 8 px, bottom ≤ 8 px from the foot) and clear of Near You's list and rail.
  - Width: the Wormholes list 400 px, Sov upgrades 560 px, less if the room is less.
  - Max height: the map's height less 16 px.
- **Phone:** a sheet across the map (8 px each side) under the top buttons, down to 8 px above the foot. It shuts Near You (one at a time).
- Escape and the close button work as today. Opening one filter's panel shuts another's.
- Placement is computed on open, on resize and when Near You opens or shuts. No timers (LESSON #120).

**4.7 Things that assumed a bar at the foot.**
- `itMapYouArrow`: keep the arrow off every map control (the filter column and its panel buttons, the rail, the zoom row, the search box), not only off a bar at the foot.
- `itm.fbBox` (labels and region names give way to the bar): take the column's box, widened by a shown panel button.
- The Wormholes chip (045, bottom left): `itMapWhChipPaint` lifts it (`.up`) whenever it meets the bar side to side. With the column at the same left edge that's always true, so the test must check up and down too: lift it only when the column (or the phone's open column) really reaches it.
- Paths to you (043): the column and the rail stay above its overlay.

**4.8 Rules A–C (section 6) apply site-wide in this part.** The global checkbox and radio style changes every plain checkbox and radio on the site in one rule.

**4.9 The Intel example** (README "Intel changes and the Intel example"; the mockup shows it, MOCKUP box "Show the Intel example"):
- **Wide:** the example's map picture goes full width, with Near You's list open beside the feed button at the picture's top right (a static copy of the rail, pressed, with its badge), and the Feed below.
- **Phone:** the map picture (today the phone example shows no map), the feed button on it, Near You's list under the picture, then the Feed.
- **Markers:** 1 Feed report, 2 first Near You row, 3 the map picture (on a phone too), 4 an alert row, 5 a kill badge. Markers sit above the list (z-order).
- **Notes:** `IT_EX_NOTE3_PHONE` goes; note 3 is the same on a phone.
- 017's marker check covers it at 1440 and 390 px.

## 5. Part 2: the Sov upgrades filter

**5.1 The upgrade table.** `INTEL_SOV` is generated by `tools/gen_intel_tables.py` from CCP's static data (the same pyfa copy it reads for probes, 049):
- **Which types:** published types in groups 4768 "Sovereignty Hub Site Detection Upgrades", 4772 "Sovereignty Hub Service Infrastructure Upgrade", 4838 "Sovereignty Hub Colony Resources Management Upgrades" and 4839 "Sovereignty Hub System Effect Generator Upgrades" (Sources). Types named Placeholder or QA are left out.
- **Rows:** `[typeId, name, kind, level]`, where kind is the name less a trailing " 1"–" 3", and level is that number or null. About 45 rows, roughly 2 KB.
- **Never hand-typed:** a new upgrade from CCP arrives with the next table update.

**5.2 Kinds and groups in the panel** (the page's own grouping, kept in the page by kind name; a kind it doesn't know goes to Other):
- **Ratting:** Major Threat Detection Array, Minor Threat Detection Array.
- **Exploration:** Exploration Detector.
- **Mining:** the seven Prospecting Arrays (Tritanium, Pyerite, Mexallon, Isogen, Nocxium, Zydrine, Megacyte), in their own column on a wide screen.
- **Navigation:** shown as "Cyno beacon" (Cynosural Navigation), "Cyno jammer" (Cynosural Suppression) and "Jump bridge" (Advanced Logistics Network). CCP's name is in the hover.
- **Other:** Supercapital Construction Facilities, the four Stability Generators, Power Monitoring Division, Workforce Mecha-Tooling.
- Only kinds that appear in your lists are shown, each with its count of systems. Jump bridge shows when 041's list holds a bridge, marked "from Jump bridges".

**5.3 Pasting a list** (in the panel, "Paste a list", the textarea in the text field style):
- **Upgrade lines:** `System <- Upgrade, Upgrade` (his format):
  - The system is matched by name as in the rest of Intel (`it.names`, case-insensitive).
  - Each item, split on commas, trimmed, spaces collapsed, is matched case-insensitively to an `INTEL_SOV` name with its level ("Major Threat Detection Array 3").
  - A line is marked ✓, or ⚠ when an item isn't an upgrade name (naming it), or ✗ when the system isn't found (as the Shorthands and 041's boxes do).
- **Name-only lists:** a paste with no `<-` at all. Each line is a system name, and a select asks what they are: every kind without a level except Advanced Logistics Network (that list comes from 041). The default is "Cyno beacons (Cynosural Navigation)" ("More kinds later").
- **Bad lines:** a line without `<-` in an upgrade paste is ✗ ("no upgrades on this line"). The same system twice in one list merges, with a dim "also on line N".
- **Adding:** "Add as a new list" (`.mys-primary`) saves it. Lines with ✗ are kept in the text but not used.

**5.4 Lists, each on its own:**
- "Lists (N)" with `IT_CHEV`, shut by default.
- One row per list: "Upgrades · 86 systems · pasted today". The paste format shows in its hover.
- Each row has Edit, Replace and Remove (global buttons):
  - **Edit:** the list's text in a box, rows checked live under it, Cancel / Save.
  - **Replace:** the paste box, with the list's kind kept.
  - **Remove:** with Undo for 6 s.
- Lists from different pastes add up (a system in two lists has both). Nothing expires ("Until replaced").

**5.5 Picks.**
- A checkbox per kind (rule C), in the two-column grid.
- A new list's kinds start picked; your picks are saved.
- Pressing the filter with no lists opens its panel at the paste box.

**5.6 On the map** ("Bright / dim"):
- Systems with a picked kind stay bright; the rest dim, as Wormholes does (`itMapDimmed`). Your system never dims.
- The hover adds "Sov upgrades: Major Threat Detection Array 3, Cyno beacon" (every kind the system has, with its level).
- The key line under the map: "Sov upgrades · bright: <picked kinds> · hover a system for its upgrades".
- The filter: key `sov`, the shield-with-tick icon (mockup), name "Sov upgrades", note "systems with the upgrades you picked bright, the rest dimmed".
- Panel: role=dialog with `button.x-close` (rule 5), Escape closes it, and it's placed as in 4.6.

**5.7 Stored data.**
- A new key `tvSov`: `{v:1, lists:[{id, kind, text, at}], pick:[kind names]}`. `kind` is `''` for upgrade lines, or a kind name.
- Capped at 10 lists and 100,000 characters per list. The owner's upgrade list is about 500 lines.
- Read with try/catch; a bad value reads as empty.
- An older page never reads the key, so upgrading and reverting are both safe.
- Alliance data: the lists stay in this browser. They're never sent anywhere, never in an export or share link, never in a check or the repo.

**5.8 Jump bridge** reads 041's list (`itBridges().edges`: both ends of each bridge), whatever its "Use jump bridges on the map" switch says.
- If part 2 is built before 041, the kind simply doesn't show, and 041 adds the hook.
- A pasted line naming Advanced Logistics Network counts as Jump bridge too.

## 6. UI rules it touches

**New rules for CLAUDE.md "UI rules"** (part 1 writes them, with `check_ui_rules.py` cases):

- **A. Button vs map control** ([stated] "sure"):
  - **Buttons** (actions in panels and cards) are the global `button`: amber outline and text. One main action per panel is `.mys-primary` (amber fill).
  - **Map controls** (zoom, center on me, the filter buttons, the rail, panel buttons) are neutral, like `.it-map-zoom`:
    - `rgba(18,23,28,.9)` fill, `--line` border, cyan border on hover, `--tag-on` when pressed;
    - 30 px (filter buttons 32), 44 px on a phone;
    - never amber, except a count badge that means your alert range.
  - Check: no amber colour, border or fill in a map-control rule.
- **B. Panels over the map** ("Site panel style"):
  - Fill and edge: `--panel`, a 1 px `--line` border, 6 px corners, shadow `0 8px 24px rgba(0,0,0,.5)`, padding 10–12 px.
  - Heading: 14 px bold `--heading`.
  - Rows or cards inside: `--panel-2`.
  - This covers the Wormholes list, the Sov panel and Near You's list.
  - Check: those rules use `var(--panel)` and `var(--line)`; Near You's rows use `var(--panel-2)`.
- **C. Checkbox and radio** ("cyan tick, dark box"):
  - One global rule for every checkbox (switches `.mys-sw`, `.dmg-sw`, `[role=switch]` excepted) and radio: `appearance:none`, 16 px, `--bg` fill, 1 px `--field-border`, 3 px corners (radio round).
  - Hover: `--field-border-hover`.
  - Keyboard focus: cyan border and `--accent-ring`.
  - Disabled: 45%.
  - Checked: the border cyan, and a cyan tick (radio: a cyan dot) on the dark box.
  - The label row stays the tap area (44 px on a phone where it is today).
  - Check: the one rule exists; no other rule sets `appearance` or a fill on a checkbox or radio.

**Existing rules:**
- **Tag:** the count badge is not a tag (round, 15 px, on a button); tags unchanged.
- **Switch, slider:** unchanged. The switches stay out of rule C.
- **Text field:** the paste and edit boxes follow it (monospace, as paste boxes do).
- **Close button:** the Sov panel has `button.x-close`. Near You's list is a view toggled by its button (no dialog role).
- **Chevron:** "Lists (N)" and "Paste a list" use `IT_CHEV`.
- **Intel lists:** rows unchanged. Near You is still narrow (320 px), its region a line under the system. `intel_layout_check.py` is updated for the new layout.
- **Drawing cost** (LESSON #120): no timers; placement on open, resize and the card's own redraw. The badge updates with the list. The sov dimming is part of `itMapDraw`'s key (`itMapKey`), so picks redraw once.
- **Phone:**
  - 44 px targets (rail button, panel buttons, column button, the panel's rows and buttons);
  - no sideways scroll at 390 px (checked in the mockup);
  - one panel at a time.
- **Colour tokens only:** the feed icon is `currentColor`; badge `--amber`.
- **Page size:** served copy 583,626 bytes (gzip -9) on 9459b35, ceiling 800,000. Part 1 adds CSS and placement (a few KB); part 2 the table (about 2 KB) and the panel (a few KB).

## 7. Info text it touches

The `intel` panel has 599 words of its 600 cap (`check_subtext.py`, measured on 9459b35); its open part has 73 of 85.

- **Near You line, part 1:** "**{card:itnear}:** systems with …" becomes "**{card:itnear}** (the map's feed button): systems with reports or kills …" (the rest as today).
- **[Map], part 1, with the sov sentence in part 2:** "… ✕ counts kills. Filters (left) pick what it shows. Paths to you: routes from hostiles in your alert range, as a tree. Wormholes: reported, kept 24 h, edited and shared in its list; the rest fades, one reported in the last 30 minutes pulses, the chip steps through them. Sov upgrades: your pasted lists; picked ones stay bright. Systems past {card:itnear}'s range are faded."
- **[Privacy and tabs], part 2:** "… only wormhole reports and sov lists are kept after you close the page."
- **Total:** 607 words (open part 77 of 85). Q3, [stated] "raise it": part 1 raises `INFO_ALL_MAX_BY_KEY['intel']` in `check_subtext.py` from 600 to 620, with his words in the comment.
- **Intel example notes:** `IT_EX_NOTE3_PHONE` goes (part 1). Notes 1–5 keep their words.
- **Other panels:** none. The System Analyzer's and Damage cards' checkboxes change look only.

(As built in part 1, section 13: the Near You line and [Map] read a little differently; the `intel` panel is at 599 of 620 words, open part 73 of 85, on e7f5a2b. As built in part 2, section 14.)

## 8. CCP's Developer License Agreement

- **2.3(c), tracking players:** not touched. The sov lists describe an alliance's own structures, pasted by the user, kept in their browser only, never combined with other players' data or sent anywhere.
- **2.1:** the upgrade names come from CCP's static data inside the page, as the other tables do.
- **2.5:** no new ESI calls; an ESI read of hub upgrades is a later item ("Paste now, ESI later").
- **Branding:** none.

## 9. Checks

**Part 1:**
- `check_ui_rules.py` cases for rules A–C, each with a mutant.
- A page check `intel_map_layout_check.py` at 1440 and 390 px:
  - Near You shut shows only its button, the size of the zoom buttons; open, the list sits beside the rail inside the map, with every filter, the rail and zoom still clickable;
  - the filter column under the search box, clear of zoom and the rail, inside the map;
  - each panel button right of its filter (wide) or in the column (phone);
  - the name line level with the filter that is on, clear of the rail;
  - a panel opens right of the panel buttons, inside the map, clear of Near You;
  - phone: column and Near You take turns, a panel shuts Near You;
  - checkboxes drawn by the site, switches untouched;
  - no sideways scroll; no page errors.
- 017's example marker check at 1440 and 390 px.
- `intel_layout_check.py` updated.

**Part 2:** `sov_upgrades_check.py` with made-up lists only:
- an upgrade paste (✓ / ⚠ / ✗ rows);
- a name-only paste with its kind;
- Edit / Replace / Remove with Undo;
- picks dim the map and the hover names the upgrades;
- Jump bridge from a made-up 041 list;
- `tvSov` round-trip and a bad value read as empty;
- mutants: no level parsing; dimming ignoring the picks.

Also `gen_intel_tables.py --check`, `check_pii`, `check_subtext`. (As built: the script has no `--check`; its plain run, without `--write`, is the check.)

## 10. Hand test (owner)

1. Part 1:
   - Intel at full width: the map first, Near You behind the feed button (badge count, amber when something is in range). Open it: the buttons stay put and clickable.
   - Hover the filters: panel buttons and name line to the right.
   - Open the Wormholes list with Near You open: the two don't overlap.
   - On a phone: the column and Near You take turns.
   - Tick Drifter, an Intel channel and a Routes option: dark boxes with a cyan tick.
2. Part 2:
   - Paste the real upgrade list (alliance data: it stays in the browser): every line ✓, no ⚠. Paste the cyno list as Cyno beacons.
   - Pick kinds; hover a system for its upgrades and levels.
   - Replace and Remove one list, the other untouched.
   - With 041's list in, Jump bridge shows.
3. The UNVERIFIED rows below.

## 11. Mockup

`intel_layout_mockup.html` (rounds 1–6b), built from the real page by the scripts in `roadmap/intel-layout-mockup/` (README there; `build_lay.py`, `proto_lay.js`, `boot_lay.js`, `test_lay.py`; `mock.js` from the repo's `roadmap/paths-to-you-mockup/`).
- `test_lay.py`: 140 checks pass at 1440 and 390 px on 9459b35.
- `check_pii`: only the page's own login button image.
- Made-up sov data only.
- The build commits it to `Claude outputs/`. The mockup's Sov panel lists six Prospecting Arrays; the game has seven (Tritanium too), and the build follows the table.
- Part 1 (052) rebuilt it from these scripts against main 5eef655's page and committed it as `Claude outputs/intel_layout_mockup.html`.

## 12. Questions (all answered 2026-11-15: [stated] "1. two deliveries, 2. remember, 3. raise it")

- **Q1. Delivery split:** two deliveries. Part 1: the layout, rules A–C, the example, the Near You and [Map] info wording (without the sov sentence). Part 2: the Sov upgrades filter, the sov sentence in [Map], the privacy line. Part 2 builds after part 1.
- **Q2. Near You remembered open or shut:** yes (`nearShown`, 4.2).
- **Q3. The `intel` info cap:** raised to 620 (section 7).

## 13. Built: part 1 (052)

**v2026.11.15.3, PR #57 (https://github.com/gitLaloosh/threatvector/pull/57), merged 2026-11-16 03:58 UTC as main e7f5a2b; "Publish the site" green.** Built against main 5eef655.

**Build review decisions** (2026-11-15, [stated] "1. your choice is fine, 2. yes, 3. sure, 4. leave it shut"):
- R1 Paths to you re-fit (the bug flagged on 041, 050 and 052, [stated] "paths to you map mode should run "fit" every time the layout changes"): the fit key gained the tree's size (`G.cw|G.ch`) and Near You's state, so the tree re-fits when it grows or shrinks, but only while the view hasn't been zoomed or dragged by hand since the last fit (`itPt.hand`; the build session's choice, "your choice is fine"). The flags on 041's and 050's queue files were removed.
- R2 Centring (⌖, the first view, a jump, ⤢, a search pick, a Wormholes-list pick) uses the part of the map no panel covers (`itMapFree`, `itMapFreeX`; "yes").
- R3 Near You and a filter's panel take turns when both don't fit beside each other, by the room (`itMapRoomForBoth`, `IT_MAP_PANEL_MIN` 300 px), not by the window being a phone ("sure").
- R4 A map press leaves Near You shut ("leave it shut").

**Also delivered with it:** the Wormholes list's system names are buttons (`[data-it-whgo]`, "Show on the map") that do the search box's pick (`itRpPick`) in the part of the map the list doesn't cover; on a phone the list shuts first ([stated] "left click on system name re-centers map on that system containing the wormhole").

**Where the build differs from this plan:**
- Phone Near You: top 164 px (under the filter column's button, so it stays clickable), width the map's less 66 px, padding 8 px.
- `itMapFree` falls back to the whole width when the uncovered part is under 96 px (a phone with Near You open).
- Hide all routes moved left of the zoom buttons (a phone: top left); the route note sits at the foot.
- ⤢ (`itMapFitView`) and Paths to you's fit (`itPtFit`) no longer keep room for a bar at the foot; the tree fits between the filter column and the rail or Near You (foot 16 px).
- Info text: the Near You line reads "**{card:itnear} (feed button):** systems with reports or kills within its range (Intel settings), nearest first. Amber edge: within your alert range; …" (the plan's "**{card:itnear}** (the map's feed button):" put the colon outside the bold, which `intel_place_check` needs inside, and pushed the open part past 100 words). [Map] adds "(a name there shows it on the map)" after the Wormholes list. The `intel` panel: 599 of 620 words, open part 73 of 85.
- Checks: the re-fit case and a 760 px case (R3) are in `intel_map_layout_check.py` (1440 / 760 / 390 px, 5 mutants), not `paths_to_you_check`; the Intel checks' shared setups open Near You's panel (`nearShown: true`); `intel_map_you_check` shuts it.
- Fixed on the way: "+N more systems below" counted again when its line appears; an opened row's reports kept in view (`itNearShow` with the `.it-nbx`); a big gang's names were measured while the panel was shut (LESSON #169, `itNearCap`); the Intel example's marker 5 clamped at 320 px.

**For part 2 (053), what main has now:** placement is `itMapCtlPlace` (key-gated, `itm.ctlKey`; the filter, Near You, the panel, the map's size); a filter's panel button is `itMapPanelBtnHtml` / `IT_MAP_PANEL_BTN` in a `.it-map-fw` box; the Wormholes list is placed by `itWhListOpen` and `itMapCtlPlace` (`.pop` on the box hides the name line) and is the pattern for the Sov panel; `itMapRoomForBoth` decides take-turns with a 300 px panel minimum, so check it against the Sov panel's 560 px width; the filter order is Security, Jumps, Regions, Reports, Kills, Wormholes, Paths to you (Sov goes before Paths to you); CLAUDE.md's "The Intel tab's layout" paragraph describes it.

## 14. Built: part 2 (053)

**v2026.11.16.1, build queue 053, branch `053-sov-upgrades-filter`.** Built against main e7f5a2b (v2026.11.15.3).

**Build review decisions** (2026-11-15, the owner's answers to the review's five points; recorded in the queue file):
- Not in this delivery: the Wormholes tab's panels behind icons ([stated] "i've got a research session planning the feature we discussed so it can be removed from this delivery."); a research session plans it as its own item.
- B1 ([stated] "Yes, one shared path"): 052's placement, `itMapFree`, `itNearToggle` and take-turns handle whichever filter panel is open (`itMapPanel()`: `{k, el, min, w, room}`, `itMapPanelClose`), one at a time.
- B2 ([stated] "420 px, one column below"): the Sov panel sits beside Near You only with `SOV_PANEL_MIN` (420 px) of room (`itMapRoomForBoth(min)`); its picks are a grid of 240 px columns, two at its full 560 px, one below about 530 px.
- B3 ([stated] "Bright anywhere"): picked systems are bright anywhere on the map, past "Map: within" too, as Wormholes.
- B4 ([stated] "INTEL-11 when storage is full"): a new code, INTEL-11, in the panel when `tvSov` can't be written; the lists work for the visit.
- B5 ([stated] "Load names before checking"): the panel loads the system names (`sovNames` → `itLoadNames`) before a paste is checked ("Loading system names…", Add off); INTEL-03 when ESI can't give them.

**Sources checked at the build review** against the manifest's pyfa (e5483f8, v2.70.0), not only the plan's b79cd902: the four groups and the three descriptions as the table says; **44** published upgrades (the plan's "about 45"; the review's first count of 43 was a miscount). Unpublished types are left out by `published`, not by name: "Systemwide Modifier Upgrade B1" (87816) is unpublished and named neither Placeholder nor QA.

**Where the build differs from this plan:**
- The panel's top keeps 420 px of the map below it (the Wormholes list keeps 260): `itMapPanel().room`. Level with its filter, the Sov panel was cut off at 1440 px.
- The groups in the panel: Ratting, Exploration, Navigation and Other in the first column, Mining in the second (the mockup's columns); each group in the page's own order (`SOV_GROUPS`), CCP's for Other.
- The hover's "Sov upgrades: …" line shows on the Sov filter only (as the mockup did).
- "Paste a list" sits inside "Lists (N)" (the mockup's place); pressing the filter with no lists opens both. After Add the paste box shuts and the lists show.
- Edit opens under its row; Replace uses the paste box ("Replace: paste the new list; it takes the place of …", its kind kept, the kind select disabled).
- The check box shows every line for a short paste (12 lines or fewer), else only ⚠ / ✗ / repeated lines (at most 200), under a count ("4 ✓ · 1 ⚠ · 2 ✗ · 4 systems").
- A list's name: "Upgrades", or the kind's ("Cyno beacons", "Cyno jammers", "Gamma Stability Generator").
- Jump bridge: `sovBridgeEnds()` returns nothing until 041 fills it in (both ends of each bridge, as system ids); a pasted Advanced Logistics Network counts now.
- `gen_intel_tables.py` has no `--check`: its plain run is the check.
- Undo's 6 s is one `setTimeout` per Remove; when it ends with the focus on Undo, the focus goes to "Lists (N)".

**Info text:** [Map] gains "Sov upgrades: your pasted lists; picked ones stay bright." and [Privacy and tabs] reads "only wormhole reports and sov lists are kept after you close the page." METHODOLOGY.md's Intel section gains a Sov upgrades paragraph.

**Checks:** `tools/page_checks/sov_upgrades_check.py` (made-up lists on the mock map; 6 mutants: no level read, the dimming ignoring the picks, picked ones faint past the reach, two panels open at once, a full storage not said, a paste checked without names). `intel_map_layout_check.py`'s 760 px mutant follows `itMapRoomForBoth`'s new line.

## Sources

| Fact | Source | Checked | Status |
|---|---|---|---|
| The upgrade types, their IDs and groups: 4768 "Sovereignty Hub Site Detection Upgrades" (Major/Minor Threat Detection Array 1–3, Exploration Detector 1–3, Tritanium/Pyerite/Mexallon/Isogen/Nocxium/Zydrine/Megacyte Prospecting Array 1–3), 4772 "Sovereignty Hub Service Infrastructure Upgrade" (Cynosural Navigation 81615, Cynosural Suppression 81619, Advanced Logistics Network 81621, Supercapital Construction Facilities 81623), 4838 "Sovereignty Hub Colony Resources Management Upgrades" (Power Monitoring Division 1–3, Workforce Mecha-Tooling 1–3), 4839 "Sovereignty Hub System Effect Generator Upgrades" (Gamma/Plasma/Electric/Exotic Stability Generator); unpublished Placeholder and QA types in 4768 | CCP's static data as shipped in pyfa's repo, https://github.com/pyfa-org/Pyfa commit b79cd902 (2026-11-11), `staticdata/fsd_built/types.*.json` and `groups.0.json`; again at the build review at commit e5483f8 (v2.70.0, the manifest's) | 2026-11-15 | verified |
| A level is the name's trailing number (1–3); Cynosural Navigation / Suppression, Advanced Logistics Network, Supercapital Construction Facilities and the Stability Generators have none | same files, https://github.com/pyfa-org/Pyfa commit b79cd902 and e5483f8 | 2026-11-15 | verified |
| Cynosural Navigation enables a Pharolux cyno beacon, Cynosural Suppression a Tenebrex cyno jammer, Advanced Logistics Network an Ansiblex jump bridge | type descriptions of 81615, 81619, 81621 in the same files, https://github.com/pyfa-org/Pyfa commit b79cd902 and e5483f8 | 2026-11-15 | verified |
| `appearance: none` on a checkbox or radio removes the native look and keeps it working (state, label clicks); Baseline widely available since March 2022 | https://developer.mozilla.org/en-US/docs/Web/CSS/appearance (Mozilla's documentation of the CSS standard; the standard itself is CSS Basic User Interface Level 4) | 2026-11-15 | verified |
| The owner's pasted lists use CCP's type names exactly, with the level as a trailing number ("Major Threat Detection Array 3"), and `System <- …` lines | UNVERIFIED: his list wasn't stored or read for this plan (alliance data); confirm in the hand test (step 2: every line ✓, no ⚠) | 2026-11-15 | UNVERIFIED |
