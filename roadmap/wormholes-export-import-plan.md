# Plan: the Wormholes list's Export and Import

Status: **BUILT** as v2026.11.13.2 (build queue 046, branch 046-wormholes-export-import; see "Built" at the end). Queued as 046 (2026-11-12, [stated] "queue it please"); all questions answered. Written 2026-11-12 by a research session from main 60d75f1 (v2026.11.12.6, after 045). **Build after 044**: this plan works on 044's store (signature IDs, details, Drifter per hole, raw lines, the per-ID removal mark added to 044 for this). Decisions marked **D** are the session's; the rest are the owner's, quoted.

Backlog: "Wormholes list: export and import" (areas/dscan-backlog-5.md, continued in -6).

## The owner's ask
- [stated] "plan a change to the wormholes list panel that allows you to export from and import to your wormhole list. import should have de-dupe/merge logic to ensure that any pre-existing holes are only added to and not duplicated or lose data."
- [stated] "each system will hold a list of the raw reports so make sure you're being careful about this bit." (on "the entry's time becomes the newer of the two")

## The owner's decisions (2026-11-12)
1. **Export copies JSON; nothing else.** [stated] "export - just copies json to the clipboard. it can be sent via discord, email, whatever. it's just json going to the clipboard." No file, no link.
2. **The JSON shows in a box inside the list panel, not a modal.** [stated] "copy can open a modal with the json already selected in an input box and they can either click copy or copy themselves with ctrl+c right?", then (a modal over the list would be a dialog on a dialog) [stated] "then just have the json live in a panel with a read only input and when you click export it expands to render the same thing the modal would have. problem solved."
3. **Export is a fixed label with Intel's chevron** (not an Export ↔ Close flip): [stated] "sounds good" to "a fixed "Export" label with Intel's chevron" (the site's expand/collapse rule, as decided for "EVE standings").
4. **Import gets its own box, built like Export's:** [stated] "this" to "A fixed "Import" button with Intel's chevron, next to Export, opens an empty editable box with an Import button. It works the same way as Export, just with a box you can type into. Two buttons, each with one job." (from his [stated] "why not handle it like the export but the input is not read only?")
5. **No probe scan in this list:** [stated] "the probe scan results are for the wormholes tab. it's for importing a list of signatures that exist in the hole." 044's D11 was then taken out of 044 ([stated] "we can remove that from 044"). The Import box takes this tool's JSON only.
6. **Names travel as placeholders (DLA 2.3(c)):** [stated] "just replace names with placeholders like <a pilot>". The leftover case (a pilot named exactly like a system or ship stays in the line), accepted: [stated] "which means we can't really prevent sharing their name if we ever pass that system or ship name and in the end, couldn't really be an enforceable breach of the DLA since it matches publicly accessible data through their own service."
7. **Your removals win:** [stated] "sounds good" to "your removal wins unless the imported report is newer than your removal, which is the same rule Intel lines follow now". The same per signature ID: [stated] "go with your recommendation" (044's × now records a removal mark, see 044's ADDED note).
8. **What you entered is never overwritten:** [stated] "i would default to not overwriting the user's own data because they may have entered some of it themselves", then his better idea, adopted: [stated] "compare the raw report text shapes to determine what's new and what's not? ... if the raw reports shapes match, any data that wasn't included in any of the reports would be user input unless i'm mistaken." and [stated] "even if we dont have timestamps, we can compare the raw lines." → provenance comes from the raw lines (D4, D5).
9. **A repeated report is one line with a count:** [stated] "ok" to "one line with the newest time and a count, "×2"".
10. **Mockup:** [stated] "A" (yes).

## What the page does now (main 60d75f1; 044 not built yet)
- `tvWormholes` (040, `IT_WH_KEY`): `{v: 1, rep: {<system id>: {id, t, who, drifter, src: 'intel' | 'you'}}, gone: {<system id>: t}, keepH}`; read back with checks by `itWhRead` (systems on the map, times inside the last 48 h, the hours one of `IT_WH_KEEP`, at most `IT_WH_MAX` 500), pruned by `itWhPrune`, saved by `itWhSave`; another tab's change arrives through the `storage` event.
- The list: `itWhListOpen` builds the panel (`.it-whp`, a dialog in the map's box: header with the shared `x-close`, the Add form, `.it-whp-msg`, `.it-whp-rows`), `itWhRowsHtml`, `itWhAdd`, `itWhRemove` (sets `gone`), closed by ×, Esc or a press outside.
- After 044 (its plan, claude/roadmap/wormhole-sig-ids-plan.md): each entry adds `sigs` (≤ 8: `{sig, part, type, info, dr, t, who}`), `info`, `drNoId`, `drN`, `raws` (≤ 10, newest first: `{t, who, raw, k: 'intel' | 'you'}`, de-duped on time + text; kept only for the newest 100 systems), and the per-ID removal mark (`goneSig`). Hand adds leave an "Added by you > …" line.

## The session's decisions (D1–D12)
- **D1 Where:** in the list panel, a row under the Add form: two buttons, **Export** and **Import**, each a fixed label with Intel's chevron (`IT_CHEV`, turned by `aria-expanded`, `aria-controls` on its box). Each opens its box under the row; opening one closes the other. Both boxes stay inside the panel (it already scrolls inside: `.it-whp` max-height). Nothing new on the map.
- **D2 Export box:** a read-only textarea (6 rows, mono, full width) with the JSON, made at the moment Export opens (so it's current), focused and all selected, plus a **Copy** button. Copy writes it to the clipboard and reads "Copied!" for 2 s; if the browser refuses, the text stays selected and the line under says "Press Ctrl+C (⌘C) to copy." (the copy-by-hand pattern of `itCopyShape`). A line above the box: "N systems, M signature IDs; names replaced with <a pilot>." Nothing is sent anywhere by the page.
- **D3 The format** (one version the Wormholes tab's Share reuses later; wormhole-mapping-plan D12/D13 adds `chain` beside `sys`):
  ```
  {"tv": "wormholes", "v": 1, "made": <ms>,
   "sys": [{"id": 30000772, "name": "C-J6MT", "t": <ms>, "drNoId": true?, "info": {...}?,
            "sigs": [{"sig": "RZL-429", "part": false, "type": "Z971", "info": {...}?, "dr": true?, "t": <ms>}],
            "raws": [{"t": <ms>, "k": "intel" | "hand", "raw": "<redacted line>", "set": {...}, "n": 1}]}]}
  ```
  - Only systems still inside your keep setting. Stable order (systems by id, lines newest first), so the same list exports the same text.
  - Left out: your `gone` / `goneSig` (removals don't travel: [stated] "only added to"), `keepH`, `src`, every reporter name (`who`), and the open/closed state of rows.
  - `set` on each line is what that line set (D4); `n` its repeat count (D6).
- **D4 Every kept line says what it set** (the owner's idea, decision 8). When a line is kept (Intel's `itWhTake`, 044's hand add), it also stores `set`: the signature IDs it named, each with the type, class, life, mass, size and Drifter mark that line gave, plus any system-level details and a Drifter-with-no-ID mark. Generated lines (hand adds) are never read back as text: their `set` is the record. This is the one change to 044's line object (`set` is a new field: the older page ignores it; 044 entries without it are read once with 044's reader, `itWhDetails`, to fill it in).
- **D5 Details are worked out from the lines** (the import's heart, and why nothing is lost or overwritten):
  - After a merge, each system's details (its IDs and their type / class / life / mass / size / Drifter, the system-level details, `drNoId`) are derived again from all its kept lines, oldest to newest.
  - **Your own lines win** (kind `hand` made in this browser, the 044 "Added by you" lines): for each detail, the newest of your own lines that set it decides.
  - Otherwise the newest report line that set it decides (as Intel lines do today: 044 D5a "a newer line's word replaces the old one").
  - **A detail with no line behind it** (an entry saved before 044, or one whose line went with the 10-line cap or expiry) is "source unknown": kept, never overwritten (decision 8's default), only filled in where it's empty.
  - **A newer report that disagrees with your own value** doesn't win; it becomes a **note** on that ID's tag: a small amber "!" with the title "A shared report, 20 min newer, says crit <10%" (`note: {k, v, t}`), so a worse life or mass is never hidden. The note goes when you change that detail yourself or remove the ID.
  - The Drifter mark stays once set (044 D12); a part becomes its whole ID by 044's merge (one match only); 044's 8-ID limit applies, newest first, and an ID you removed (`goneSig`) is never brought back by a line older than the removal.
  - The entry's `t`, `who` and `src` come from its newest line, together: never a newer time with an older reporter. For an imported newest line, `who` is "<a pilot>" and `src` stays `intel` (so the older page shows it as reported, D11); a new `via: 'import'` marks it.
- **D6 Two lines are the same report** when their redacted text matches, after making spaces and capitals the same (decision 8: no time window). Generated lines compare by kind + `set` instead of text.
  - Same report from both sides: one line; your copy is kept (it has the real names); its time is the newer of the two; its count `n` is the larger of the two (the same message seen in two logs isn't a repeat).
  - Within one side, the same text arriving again later is a repeat: `n` + 1, the newest time (decision 9). The list shows "×2" after the line's age.
  - Your redacted text is worked out on the fly for the compare; your stored line keeps its names.
  - A system that arrives with no lines (the sender's entry was saved before 044) gets one line, "<name> (shared list)" (kind `hand`, from the import), so its time still has a line behind it.
  - An imported line whose only IDs you removed (and that is older than the removal) is left out, and counted in the preview as "removed by you".
- **D7 Redaction on export (default-deny):** each line is read again by Intel's own reader (`itParse(raw, null)`, with 044's `itWhDetails` first), and rebuilt from its words (`W`): a word the reader placed (system, ship, keyword, count, filler, number, 044's signature / type / class / detail words) is kept; every other word, or run of words, becomes one `<a pilot>`. Tickers, corporations and alliances become `<a pilot>` too (itWords drops the brackets, so a ticker is an ordinary word). The reporter is never written. Hand lines (kind `hand`) carry only their `set` and the system name, rebuilt as text ("Tama GHI-123 C247 EOL <4h"), so they have no names to remove.
- **D8 Import box:** an empty editable textarea (6 rows, mono) with an **Import** button. Import reads and checks the text, then shows a **preview** in the box (nothing is changed yet):
  - "Adds 4 systems · adds to 2 (3 new IDs, 5 new lines) · already have 5 · kept yours for 1 (see the ! notes)"
  - "Skipped: 1 older than your 24 h · 1 removed by you · 1 not a system on the map · 2 lines over the limits"
  - buttons **Add to my list** and **Cancel**. Add merges against the store as it is at that press (another tab may have changed it; the merge is computed again), saves, repaints the list, map and badges (`itWhChanged`), clears the box and says what it did in `.it-whp-msg`.
  - Not this tool's JSON, a newer format version, or nothing new: one line saying so, nothing changed.
- **D9 Import checks everything** (the text is someone else's): at most 256 KB pasted; `tv` and `v` must match; systems only by id on the map (`itGraphGet().at`), with the name matching (else skipped, counted); times inside the last 48 h and not past now + 1 h; IDs `ABC-123` or a part (044's shapes); types and classes only ones the page knows; details only the known steps; text cut to 400 characters a line, `<a pilot>` the only name; at most 500 systems, 8 IDs, 10 lines each; unknown fields dropped. Everything shown is escaped (`escapeHtml`), and the HTML goes through the page's builders (check_html_sinks).
- **D10 Your keep setting and your removals** (decision 7): an imported system whose newest line is older than your keep setting is skipped; one you removed (`gone`) comes back only if its newest imported line is newer than the removal; likewise each ID against `goneSig`.
- **D11 Stored data, safe both ways** (README "Stored browser data"): no new key. New fields only: `set` and `n` on lines, `note` on IDs, `via` on entries. The older page (040's reader) keeps five fields per entry and drops the rest on its next save, as 044 already accepts; a reverted page shows an imported hole as "reported by <a pilot>".
- **D12 The 10-line cap** keeps a line still backing a current detail (the newest that set each detail); it drops the oldest lines that back nothing. 044's newest-100-systems rule for lines still applies; the preview counts lines that won't fit.

## UI rules it touches
- **One chevron (CLAUDE.md UI rule 6, `check_ui_rules.py` rule 6):** Export and Import use `IT_CHEV` leading, no arrow glyph, turned 180° by `aria-expanded="true"`; fixed labels (the owner's decision 3). Raise rule 6's chevron count minimum by two.
- **One text field / button style:** the textareas use the global field style (widths only); Copy, Import, Add to my list and Cancel are the page's plain buttons.
- **No button inside a button; no new close button:** the boxes close with their own chevron button; the panel keeps its one `x-close`.
- **The list's own rules (040):** Esc and a press outside still close the whole list; a press inside a box doesn't. Focus: opening a box moves focus into it (Export: the textarea, selected; Import: the textarea); closing returns it to its button. The list repaint (`itWhListPaint`) never rewrites the boxes, and never while focus is inside one.
- **Subtext:** the line above each box is one short line; anything longer goes in the info panel (`check_subtext.py`).
- **Phone:** buttons and textareas at least 44 px tall below 600 px; the two buttons share one row (wrap if needed); no sideways scroll at 390 px.
- **Drawing cost (LESSON #120):** no timers; the JSON is built once per open; the preview once per press.
- **Colour tokens only:** the note's "!" uses `--amber`.
- **Intel example:** none: the example doesn't open the Wormholes list.
- **Page size:** estimated 3–5 KB of source, about 1–2 KB gzipped served (UNVERIFIED: measure at the build); served 520,741 bytes before (60d75f1 not re-measured since 043's 520,741).

## Info text it touches
- `intel` "[Map]" today: "Wormholes: reported, kept 24 h; its list button edits them." → "Wormholes: reported, kept 24 h; its list button edits them, and Export / Import share them as text (names left out)."
- `intel` "[Privacy and tabs]" today: "Nothing from your logs leaves the browser except the words looked up on ESI; only wormhole reports are kept after you close the page." → "Nothing from your logs leaves the browser except the words looked up on ESI, and what you copy with the wormhole list's Export (names left out); only wormhole reports are kept after you close the page."
- Check the `intel` panel stays within its 410-word cap (`check_subtext.py`, `INFO_ALL_MAX_BY_KEY`); 044's [Tags] line is added first.

## DLA (claude/reference/dla-planning-notes.md)
- **2.3(c)** (other players' information): the export carries no character, corporation or alliance names (D7), and nothing is sent by the page: the user copies the text and shares it himself. The owner's decision 6 settles the leftover case. Not legal advice.
- **9.5** (privacy): still nothing stored outside the user's browser; imported data lands in the same browser store under the same 48 h limit.
- No change to requests to CCP's servers (the redaction reads lines with the page's own reader; no lookups), money, marks or notices.

## Checks to build
A new `tools/page_checks/wormhole_share_check.py` (or in `wormhole_filter_check.py`), at 1440 and 390 px, no page errors, no sideways scroll:
- **Export:** the box opens with the JSON selected; Copy fills the clipboard (granted) and says Copied; refused, the text stays selected with the Ctrl+C line; no reporter name and no made-up pilot name appears anywhere in the JSON (default-deny: a line with a pilot, a ticker in brackets, a two-word name, a pilot after "wh"); systems, ships, signature IDs, types and detail words survive; the same store exports the same text twice.
- **Round trip:** export A, clear, import into an empty list: the same systems, IDs, details and line texts (redacted); importing the same text again changes nothing ("already have N").
- **Merge:** two browsers' lists with overlapping systems: one line per report (your copy kept, names intact), counts by max across sides; a part on one side completes to the whole ID from the other; Drifter stays; an ID you removed stays removed against an older line and comes back with a newer one; a system you removed likewise; a hand value of yours survives a newer shared report, which shows as the "!" note; a report-only detail takes the newer report; a detail with no line (040-era entry) is kept; the 10-line cap keeps every line backing a detail.
- **Checks:** wrong `tv`, newer `v`, a 300 KB paste, an unknown system, a mismatched name, a time 3 days old, a time in the future, a bad ID, an unknown type, HTML in a line (`<img onerror>`): each refused or skipped and counted, nothing run, nothing saved.
- **Preview:** counts right; Cancel changes nothing; Add recomputes against a store another tab changed in between (storage event).
- **UI:** chevrons turn with aria-expanded; one box at a time; Esc / outside press close the list; focus moves and returns; 44 px on a phone.
- Mutants: merge by time window instead of text; keep theirs over yours; drop a line that backs a detail; write `who`; let an older line bring back a removed ID.

## Where to look (main 60d75f1; 044's names from its plan)
`IT_WH_KEY`, `itWhBlank`, `itWhRead` (~29776), `itWhPrune`, `itWhSave`, `itWhTake`, `itWhChanged`, `itWhListOpen` (the panel's HTML and its click/submit handlers), `itWhListPaint`, `itWhRowsHtml`, `itWhAdd`, `itWhRemove`, the `storage` listener (search `e.key === IT_WH_KEY`), `itParse` / `itWords` (~26286) / `IT_FILLER` (~26269) / `IT_NOT_PILOT`, `itCopyShape` (the copy-by-hand pattern, ~28430), `IT_CHEV`, `.it-whp*` CSS (~2718–2742); after 044: `itWhDetails`, `itWhSigMerge`, `itWhRawAdd`, `itWhDrSet`, `itWhSigHtml`, `goneSig`.

## Mockup
`wormholes_share_mockup.html` (sent 2026-11-12; in the repo as `Claude outputs/wormholes_share_mockup.html`), scripts in roadmap/wormholes-share-mockup/ (README there):
- the real page (main 60d75f1) with 044's list as a stand-in (proto_sig044.js: from claude/roadmap/wormhole-sig-ids-mockup/, the probe scan left out, 044's removal mark added; 14 of build_sig.py's patches, plus one so the store reads 044's fields back), and this plan's Export / Import (proto_xi.js, 2 patches);
- your list already in the browser (made-up): a value you entered (RZL-429 mass >50%), a repeated report (×2), a part (QDX), an ID you removed (KLM-204), an entry saved before 044 (9N-0HF), a system you removed (SHBF-V), and a line with a made-up pilot and ticker (to show the redaction);
- the MOCKUP bar: open the list, fill Import with a made-up friend's export (the same reports, a newer "crit" report against your value, QDX-581 completing your part, your removed ID and system in older reports, a new system, one added by hand, one older than 24 h, one not on the map), reset.
- test_xi.py: 82 checks at 1440 and 390 px, all passed, no page errors, no sideways scroll (redaction, selection, one box at a time, preview counts, Cancel, the merge rules, importing twice, bad input and HTML refused). check_pii: 0 problems (names list checked; the page's own login button is the only embedded image).
- Where the mockup is simpler than the plan: Intel's own new lines don't get `set` written at the time (it's read back with 044's reader, D4's fallback); an imported system's stored IDs with no line behind them aren't used to fill empty details (D5's "source unknown" fill). The build follows the plan.

## Sources
Sources: none (no outside facts). Everything here is the owner's decisions and this project's code (index.html main 60d75f1, the functions named above) and plans (044's plan and queue file, the Wormholes tab plan, the build-queue README, the DLA digest).

## Built (v2026.11.13.2, build queue 046, 2026-11-13)
Built from main a0a0141 (044 merged, PR #50). At the build review the owner settled one question: an imported hole acts like one of your own Intel reports (rings on every filter inside the map's reach and Near You's badge while it's newer than "forget reports after"), [stated] "i think so. would you disagree?", with its hover titles saying "from a shared list, reported by <a pilot>" ([stated] "I agree").

Where the build differs from the plan:
- **The system names load first** (`itLoadNames`, cached after the first visit): the redaction needs them to tell a system from a name; on failure the box shows the names error (INTEL-03's text). Both Export and Import wait for them.
- **The redaction reads a line whole:** a "<a pilot>" already in a line (a shared line exported again) is read as one word the reader can't place, so the same line redacts to the same text every time (the mockup's split by placeholder lost "sig MKV crit" after it, found by the round-trip check).
- **Your own lines keep 044's order:** among your own lines (Intel's and yours by hand) the newest still decides, as 044 does live; a shared line takes a detail only from an older report, never from a line you added by hand (a newer shared report that disagrees becomes the "!" note). So an import never changes a detail your own lines decided.
- **Line kinds:** your hand lines stay `you`; someone else's hand lines are stored as `shared` ("Added by someone (shared list)"); every imported line carries `via: 'import'` and `who` "<a pilot>". Hand lines travel as `hand` and are rebuilt from what they set on both sides, never taken as text.
- **What an export holds with no line behind it** (IDs or details the sender kept from before 044, or whose line the cap dropped) travels as one "<name> (shared list)" line with what it set, so every detail in the store has a line.
- **Details are worked out again only for systems the import adds to;** nothing else in your list changes.
- **Repeats** (decision 9) also fold your own Intel lines: the same words again later are one line, "×N" after its age.
- **Info text:** `intel` [Map] "its list button edits them" → "its list edits and shares them" (410 of 410 words); [Privacy and tabs] unchanged (still true: the page never sends the export; you copy it). The detail is in METHODOLOGY.md's Intel section.
- **check_ui_rules rule 6** counts the two new chevron buttons by their class (`it-whp-xb`).
- Checked by the new tools/page_checks/wormhole_share_check.py (two browsers: A's lines through Intel's made-up folder, B's own list; five mutants).
