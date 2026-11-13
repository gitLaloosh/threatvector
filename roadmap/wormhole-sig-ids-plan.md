# Plan (044): signature IDs in Intel's wormhole reports

Status: **BUILT** as v2026.11.13.1 (build queue 044, branch 044-wormhole-sig-ids; see "Built" at the end). Queued as 044 (2026-11-12, [stated] "yes" to "Should I queue signature IDs now?"); check_plan_sources: only its UNVERIFIED rows listed (for the build). Written 2026-11-12 by a research session from main d227c9d (v2026.11.12.4, after 040). Builds on 040 (roadmap/wormholes-filter-plan.md): the same store (`tvWormholes.rep`), list, badges and map labels. Decisions marked **D** are the session's, for review. **Changed 2026-11-12 (research session, before any build): D11 (probe scan paste) removed; D13 gains a per-ID removal mark** (see those items; the queue file had the same notes).

## The owner's ask
- [stated] "need the intel parser to be able to identify when someone reporting a wormhole also includes the ID of the cosmic signature and record that along w/ the wormhole. helps to know exactly what to scan when you get to the system it's in. important to note that someone might give a partial ID that's unique in the list of anomalies in that system."
- His screenshot of a real line (names left out here): "<system> wh rzl-429 z971 class 1-3 medium size less then 1 day less then 50% mass". Today the page shows the Wormhole tag and leaves "rzl-429 z971 size less day less mass" unplaced. It looks up "class" and "then" as pilots, finds real characters with those names, and shows them as pilot chips. It also reads "1-3" (from "class 1-3") as the start of a system's name and offers 1-3HWZ as the system.

## What the page does now (main d227c9d)
- `itParse` reads systems first (`itFindSystems`, including `itShortSys`, which takes any word with a digit or dash as the start of a null-sec name), then ships, keywords, filler, then looks up what's left as pilots.
- 040: a line with wh / wormhole / drifter (`IT_KW`) is a wormhole report. `itWhTake` keeps one entry per system (`st.rep[sys]`: time, reporter, drifter). Nothing else from the line is kept.

## The session's decisions (D1–D10), for review
- **D1 Only wormhole lines.** Everything below applies only to a line with a wormhole word. Every other line reads as today.
- **D2 Read before systems and pilots.** A new `itWhDetails(W, used)` runs first in `itParse` and marks the words it takes. The system reader and the pilot lookup never see them. A word that is exactly a system's name is left alone.
- **D3 Signature IDs:**
  - Whole IDs: `ABC-123`, also `abc123` (read as ABC-123).
  - Parts: `ABC-1`, `ABC-12`, `ABC-`, and the bare letters `ABC`.
  - Bare letters count only right after wh / wormhole / drifter / sig / signature, or right before or after a wormhole type. They never count when the word is an intel, filler or ship word, or a dragged-in name.
    The owner agreed to this rule and its cost (a 3-letter pilot name right after "wh" reads as an ID): [stated] "i think that's ok - if it becomes an issue we can address it later."
  - A part with a dash that starts a system's name ("ZXB-" for ZXB-VC) is left to the system reader.
  - A line can carry several IDs ("2 wh xyz-123 h296 and pqr-4 k162").
- **D4 Wormhole type:** a letter and three digits found in the type table, or K162. It is attached to the ID written beside it (or to the only ID in the line). It is shown as the code and where it leads: "Z971→C1", "N110→HS", "K162→exit". The table comes from CCP's SDE at the build. The mockup uses the EVE University wiki's table, the same one the Wormholes tab mockup uses.
- **D5 Words that describe the hole are never pilots or systems in a wormhole line:**
  - class + a number or range ("class 1-3", "class 5"), and c1–c6, c13;
  - size, life and mass words (medium, frig, eol, crit, reduced, less, then, than, day, hours…);
  - amounts like "50%" and "4h".
  - The class is kept with the hole, like life, mass and size (`info.cls`), and shown on the ID's tag when it has no type ("RZL C1-3"), else as its own tag. The owner: [stated] "yes" to saving it.
  - This fixes the screenshot's "class" / "then" pilots and the "1-3HWZ" guess.
- **D5a Life, mass and size, kept when said plainly** ([stated] "if it's clear that is what is being communicated, store them."). They use the game's own steps:
  - life: "less than 1 day", "<1d" → under a day; "eol", "end of life", "less than 4h" → under 4 h; "less than 1h" → under an hour;
  - mass: "stable", ">50%" → over 50%; "reduced", "less than 50% mass", "half mass" → under 50%; "crit", "critical", "<10%" → under 10%;
  - size: small / medium / large / XL, only with "size", "sized", "hole" or "only" after the word ("medium size", "frig hole"), plus "xl" and "very large" alone.
  - Left out because they can mean a ship in the line rather than the hole: "fresh", "new", "frig", "caps" on their own.
  - If a line says two steps of one kind, the worse one is kept.
  - They go with the line's only signature. With no ID, or several, they go with the system's report.
  - A newer line's word replaces the old one; what it doesn't mention stays. For example, "RZL crit" changes RZL-429's mass and keeps its life and size.
  - Shown as small tags after the ID: "<1 day", "EOL <4h", "<1h", "mass >50%", "mass <50%", "crit <10%", "small", "medium", "large", "XL". Under 4 h, under 1 h and under 10% are red; under a day and under 50% are amber. Each tag's title gives the full meaning and the report's age.
- **D6 Kept with the report:**
  - Each system's entry gains `sigs`: up to 8, newest first, each with `{sig, part, type, info, t, who}`, and `info` (life, mass, size said with no single ID).
  - A part and the whole ID are the same signature: "QDX", then later "QDX-581", becomes QDX-581.
  - A part that fits two kept IDs is kept on its own, since two signatures can share their letters (ABC-123 and ABC-456).
  - A report with no ID keeps the IDs already there.
  - IDs older than the setting (24 h) drop off. Remove drops the system with its IDs.
- **D7 Where they show** (a purple mono tag; a part has a dashed edge and ends in "…"; the title says it's part of an ID and who reported it):
  - the Feed line: its own IDs, types and class;
  - Near You's row: up to 2 kept IDs;
  - the Wormholes list: up to 4 on the row's second line, before "reported by…";
  - the map label: "WH PQR-417 +1 · 2h".
- **D8 Not copied anywhere else.** The probe scanner has no search box, so the ID is for reading and there is no copy button.
- **D9 Other lines stay as today.** "then", "than" and "class" are only taken in wormhole lines. The owner, asked whether to stop looking them up everywhere: [stated] "i dont think many people are going to state \"class\" outright. likely to use c1, c2, etc." The class is read from "c1"–"c6" and "c13" (D5), as well as from "class 1-3".
- **D11 Paste your probe scan: REMOVED 2026-11-12, not built.** The owner, shown D11 again: [stated] "oh, this was about being able to close the loop on sig IDs. we can remove that from 044. on reconsideration, it doesn't provide that much value. it's easy enough to find a sig id that contains the partial that was provided." So: no paste box, no scan reader, no in/not-in-scan marks, no "Found in your probe scan" IDs, no 12-ID limit (8 is the only limit), no "Your probe scan > …" raw lines. A probe scan paste belongs to the Wormholes tab's Signatures panel ([stated] "the probe scan results are for the wormholes tab. it's for importing a list of signatures that exist in the hole. later we'll add a lazy update that removes any anomalies or signatures that are no longer present and adds new ones."), planned with that tab.
- **D12 Drifter per hole** (the owner, on "Drifter is per system": [stated] "should we fix this?", then [stated] "some systems have more than one drifter hole as well" and [stated] "yes"):
  - Each ID carries its own Drifter mark (`dr`). An ID gets it when its line says drifter, or when its type is a Drifter type (B735, C414, R259, S877, V928). Once marked, it stays marked.
  - A Drifter report with no ID is kept as `drNoId` until it expires or the system is removed.
  - The system's `drifter` (040's field, which the badges and filter read) is true while any kept ID is a Drifter one or `drNoId` is set. A later plain "wh" report no longer clears it.
  - `drN` counts the system's Drifter holes; the map label shows "DRIFTER ×2" for two or more.
  - Older saved entries (040's `drifter` with no Drifter ID) count as a Drifter report with no ID.
  - A Drifter ID's tag is hot pink with a small "DR" mark (see D15).
- **D13 Remove one ID:** in the Wormholes list each ID gets a small × (a 44 px target on a phone). It removes that ID only, recomputes Drifter, and says "Removed BKT-772 from EUU-4N." Remove on the row still drops the whole system.
  - **Its removal mark** (added 2026-11-12, [stated] "go with your recommendation"): the × records when that ID was removed, in the entry's own field (e.g. `goneSig: {<sig>: t}`, pruned with the entry, the same 48 h limit as `gone`). An older line read again (after a reload) or a later import can't bring the ID back; only a report newer than the removal can, the same rule as 040's `gone` for a whole system. A part that matches the removed ID counts as it. The older page ignores the field (safe both ways). The planned Wormholes list export/import relies on it (roadmap/wormholes-export-import-plan.md in the Project).
- **D14 A split ring** ([stated] "we could have wormhole systems with more than one type show a ring w/ more than one color, couldn't we? like half purple and half another color?"):
  - On the map, both of a system's rings are shared between the kinds of hole kept there: plain (purple, solid), then Drifter (hot pink, dashed), clockwise from the top, with a small gap between the parts.
  - One kind gives whole rings, as today.
  - The legend says "split: both".
  - The drawing takes any number of colours, so a later kind (for example, a hole by where it leads) needs only another colour.
- **D15 Drifter's look** (the owner, shown a light-purple split ring: [stated] "these colors are too similar, what else ya got?"; shown white, hot pink, gold, lime and dashed purple: [stated] "let's do pink and dashed"):
  - The token `--it-wh-drifter` changes from #e4b5ff to hot pink #ff5fbf, as does `itMapWhCol`'s fallback. That colours the Drifter badge, tags, map label and legend swatch.
  - On the map, Drifter ring parts are dashed (2.2 on, 1.8 off), so they read apart by shape too.
  - Why pink: white is your system's pin, gold is next to the alert-range amber, and lime is next to the high-sec greens.
  - Contrast to check at the build: #ff5fbf on the panel and on the tag's 16% tint.
- **D16 Add by hand with every property** ([stated] "the ability to set all of these properties we're supporting through the add button"):
  - The list's Add form (040: system and Drifter) gains a second row: Sig ID (whole or a part), "Type or class", and Life, Mass and Size selects with the same steps as D5a.
  - "Type or class" ([stated] "if type isn't available, ppl might just provide a class or class range. do we need another input for that or just put it in type?", then [stated] "yes" to one field) takes:
    - a type the page knows (Z971, K162);
    - a class or range (C3, c13, 1-3, C1-3);
    - where it leads (HS, LS, NS, Thera, Pochven).
  - The hint beside it says how it was read ("→ C1", "class C1-3", "leads to HS", "not known"). Anything else is refused at that field.
  - The map label shows an ID's destination or class too: "WH RZL-429→C1 · 2h".
  - Everything but the system is optional.
  - With an ID: it is added to the system, or updates a kept one it matches (part or whole), keeping where that one came from. A new one is titled "added by you". Drifter ticked marks that ID.
  - With no ID: life, mass and size go with the system, and Drifter ticked is a Drifter mark with no ID.
  - Adding to a kept system keeps its IDs (040's add replaced the entry).
  - A bad ID or an unknown type is refused at its own field (aria-invalid, focus there) with a line saying why.
  - On success the form clears and says what it added: "Added Tama: kept 24 h from now: GHI-123, C247 → C3, EOL <4h, mass <50%, large."
  - Phones: 44 px fields, wrapping two per row.
- **D17 The raw reports with each system** ([stated] "let's have the rows for each system also preserve the raw report that lead to the wormhole being added. good for a few reasons, one being we can see the raw report in case something is parsed incorrectly. have it expand/collapse like intel's near you rows."):
  - Each Intel line that added or updated a system is kept with it as typed (`raws`: who, when, the line up to 400 characters). Up to 10 are kept, newest first, for as long as the system is kept. This is the same data the Feed already shows, kept 24 h in this browser only.
  - Adding by hand leaves a line too ("Added by you > Tama GHI-123 c247 EOL <4h…"), so the history is complete.
  - In the list, the row's chevron (Intel's `IT_CHEV` / `it-rawt`, under the jumps as in Near You) opens and closes the lines. Each line shows who sent it, the line and its age, in Intel's `.it-raw` style.
  - The chevron's label counts the lines, and focus stays on it.
  - Open rows stay open while the list repaints.
  - `.it-whp-raws[hidden]` must stay hidden: the mockup's first try let `display:flex` override `hidden`, and the check caught it.
- **D10 Phase 2 (the Wormholes tab):** a connection's signature ID and type come from these reports when the chain's systems match (later, with the tab's plan).

## Open questions for the owner
1. ~~Bare letters~~: answered 2026-11-12, see D3.
2. ~~Size, life and mass~~: answered 2026-11-12, see D5a.
3. ~~"then", "than", "class" in other lines~~: answered 2026-11-12, see D9.
4. ~~Paste the probe scan~~: removed 2026-11-12, see D11.

## UI rules it touches
- One new tag style (`.it-sig`, the `--it-wh` token, mono like other codes); `.it-gtag` sizing. No new controls.
- Feed and Near You rows: tags in the existing tag area; no sideways scroll at 390 px (checked).
- The list row: IDs at the start of line 2 so Remove stays on line 1.

## Info text it touches
- `intel` "[Wormholes]" (040's lines): add "With a signature ID (ABC-123, or a part like ABC) and a wormhole type (Z971), the report keeps them too; they show on the report, the list and the map."
- `itmap` legend: none.

## Checks to build
In intel_parse_check (or a new wormhole_sig_check.py), these lines must read exactly as listed, with no pilot runs and no unplaced words:
- the owner's line (RZL-429, Z971, C1-3, under a day, under 50% mass, medium);
- "wh sig QDX";
- two IDs with types;
- "drifter hole BKT772" (BKT-772);
- "wh lmn c3 fresh";
- "wormhole QDX-581 n110 eol".

It must also check that:
- a line without a wormhole word is unchanged;
- "wh the" gives no ID;
- a part with a dash that starts a system name stays a system;
- merges: part → whole; a part fitting two kept IDs is kept on its own; newest first; at most 8; expiry at the setting;
- life/mass/size only when plain: "<4h crit", "end of life", "frig hole", "<1h", ">50% stable xl", "reduced and crit" (the worse); and nothing from "2 frigs on it", "fresh", "caps";
- tags in the Feed, Near You, list and map label;
- Drifter per hole: two Drifter IDs and a plain one keep the system Drifter (`drN` 2, "DRIFTER ×2"); a Drifter report with no ID survives a later plain "wh"; removing both Drifter IDs with × leaves the plain one and clears Drifter; a mixed system gives two ring colours;
- removal marks: an ID removed with × doesn't come back from the same line read again or an older one (or its part), and does come back from a newer report; the mark survives a reload and is pruned at 48 h;
- adding by hand: every property saved; the type's destination shown while typing; updating a kept ID changes only what was set; Drifter with an ID; bad ID and unknown type refused at their fields; no sideways scroll at 390 px;
- the raw lines: each system keeps its lines newest first, up to 10; closed at first; the chevron opens and closes them with focus kept; an add by hand leaves a line;
- no probe scan paste anywhere (D11 removed);
- 1440 and 390 px; no page errors.

Mutants: run the reader after the systems; merge a part into the first of two matches; let an older line bring back a removed ID.

## Where to look (main d227c9d)
`itParse` (~26353), `itFindSystems` / `itShortSys` (~26295, ~26329), `IT_KW` (~26222), `IT_FILLER`, `itWhTake` (~29544), `itWhNear` / badge (~27983, ~29563), the Feed's wormhole tag (~28185), `itWhRowsHtml` (~29648), `itMapWhLabel` (~29585), the map's wormhole rings (~29333–29340), `itMapWhCol` (~29582), `itWhRemove` / `gone` (040's removal rule).

## Mockup
`sig_mockup.html` (sent 2026-11-12; in the repo as `Claude outputs/wormhole_sig_ids_mockup.html`):
- the real page (main d227c9d) with made-up Intel around C-J6MT, including the owner's line shape, with the reporter changed to a made-up name;
- made-up characters named "Class" and "Then" for "Today";
- the 18 patches the build would make to index.html, listed in build_sig.py's PATCHES;
- the new functions in proto_sig.js;
- a MOCKUP bar: "Today" / "With this plan", post 4 more lines, show the lines as typed, and fill in a sample probe scan (made-up IDs in the scanner's tab-separated rows). **The probe scan parts (the bar's sample scan, proto_sig.js's scan code and its checks) are out with D11:** the build ignores them; the mockup isn't rebuilt for that (the plan wins).

Scripts are in roadmap/wormhole-sig-ids-mockup/. test_sig.py ran 110 checks at 1440 and 390 px, all passed, with no page errors and no sideways scroll (again at the build, from main d227c9d).

## Sources
| Fact | Source | Checked | Status |
|---|---|---|---|
| Signature IDs are three letters, a dash and three digits ("ABC-123"), kept across downtime since Hyperion (2014) | https://forums-archive.eveonline.com/message/4941511 (secondary source: forum post quoting CCP's patch notes) | 2026-11-12 | UNVERIFIED: secondary only; settle from CCP's own patch notes page if it matters (the reader accepts the shape either way). In the owner's hand test at the build. |
| Players often give only the three letters of an ID | https://wiki.eveuniversity.org/Archive:Exploration_at_the_NSC and https://wiki.eveuniversity.org/User:Laz_orti (secondary source: wiki) | 2026-11-12 | UNVERIFIED: secondary only (a players' habit, which no CCP page states); the reader takes the three letters either way, and the owner's own line shows whole IDs |
| Two signatures in one system can share their letters (ABC-123 and ABC-456) | https://bitbucket.org/daimian/tripwire/issues/249/duplicate-signature-id-issue-233 (secondary source: Tripwire's issue tracker) | 2026-11-12 | verified (secondary) |
| Life steps (less than 1 day / 4 hours / 1 hour remaining), mass steps (more than 50% / less than 50% / less than 10% remaining) and sizes (small, medium, large, extra large) | https://wiki.eveuniversity.org/Wormholes (secondary source: wiki) | 2026-11-12 | UNVERIFIED: secondary only; settle from the game's own wormhole info text (the owner's hand test at the build: show info on a hole) |
| Wormhole type codes and where they lead (Z971 → C1, N110 → highsec, K162 the far end) | CCP's SDE as pyfa e5483f8 (v2.70.0) carries it: attribute 1381 `wormholeTargetSystemClass` on the types of group Wormhole, read by `tools/gen_wh_table.py` | 2026-11-13 | verified (primary). The wiki's table (https://wiki.eveuniversity.org/Wormhole_attributes, used by the mockup) differs: CCP's data adds R081 (C4), J492 (lowsec), X450 (nullsec) and I078, L687, O546, O753, R327 (Pochven), and gives C729 no fixed class ("?") |
| The parser order (systems, then ships, keywords, filler, pilots) and itShortSys's rule | `index.html` main d227c9d (~26295–26470) | 2026-11-12 | verified |
| 040 keeps one entry per system: time, reporter, drifter | `index.html` main d227c9d (~29544) | 2026-11-12 | verified |

(The probe scanner's row format row was dropped with D11, 2026-11-12; it moves to the Wormholes tab's plan when its Signatures panel is planned.)

## Built (v2026.11.13.1, build queue 044, 2026-11-13)
Built from main 60d75f1 (after 045, which took the Drifter colour and the dashed outer ring from D15, and the Bubble-tag bug). At the build review the owner added one thing: each kept line also stores what it set (`set`, the export/import plan's D4), [stated] "sure as long as it still works on the import/export."

Where the build differs from the plan:
- **The type table** is CCP's (`IT_WH_TYPE`, only `tools/gen_wh_table.py` writes it; a step of the pyfa update chain): 102 codes, see Sources. K162 is "exit"; C729 is "?" ("a destination CCP's data doesn't fix"); classes 10 and 11 are skipped. "class N-M" takes classes 1–6 and 13 only (the mockup took any one- or two-digit number).
- **The removal mark** (`goneSig`, at most 16 per system, 48 h): × sets it to the removed ID's newest report time. A line at or before it (the same line, an older one, a part of it, or another line in the same second) is skipped; a newer report brings the ID back and takes the mark away; adding the ID by hand does too. Most re-reads are already skipped by 040's rules (a line older than the entry, the same line again), so the mark mostly guards same-second lines and the coming import.
- **Each kept line** (`raws`, 10 newest first, kept for the newest 100 systems) stores `set`: the IDs it named with what it said of each, its system-level details and a Drifter-with-no-ID mark. A store that runs out of room keeps lines for the newest 20 systems and tries once more.
- **Reading back** (`itWhEntryRead`): every new field is checked on load (shape of IDs, known types and steps, times inside the keep window); anything else is dropped. An entry 040 wrote (`drifter` with no IDs) reads as a Drifter report with no ID (`drNoId`). `drifter` and `drN` are always worked out again (`itWhDrSet`), so the older page still reads the badge.
- **Adding by hand** goes through 040's `itWhAdd` (so the system is renewed to now and marked added by you) and then carries the kept IDs, details and lines over. As in 040, a system added to by hand shows on the Wormholes filter and in the list; Near You's badge stays for Intel's reports only.
- **The ×** is 44 × 44 px on a phone (the mockup's was 24 px wide).
- **Contrast** (D15): #ff5fbf is 6.6:1 on the panel and 5.2:1 on the tag's 16% tint.
- **Info text:** `intel` [Tags] gained "Wormhole: wh, wormhole, drifter, with any signature ID (ABC-123 or ABC) and type." (409 of 410 words); what is read and kept is in METHODOLOGY.md's Intel section ("Signature IDs and hole details").
- Checked by the new tools/page_checks/wormhole_sig_check.py (two made-up system names test the reader's order, as the test world's names don't look like an ID; four mutants).
