# Plan (BUILT, v2026.11.21.3, build queue 066): Intel map kill counts by who died (was: kill rings in the killers' standing colour)

Status: BUILT 2026-11-21 as build queue 066 (v2026.11.21.3; the Project doc `claude/roadmap/kill-rings-plan.md` until then; see "Built" at the end). READY 2026-11-20 (research session, main f70fdd5, v2026.11.20.1). Direction changed by the owner 2026-11-20 (section 2); all questions answered (Q1 colours: A); mockup sent (section 8). **QUEUED as build queue 066** 2026-11-20 ([stated] "queue it"; `claude/build-queue/066-kill-counts.md`).
Planning list item D / 2 (`claude/roadmap/intel-planning-list.md`; the owner: [stated] "plan D"). Backlog entry "Intel map: kill rings in the killers' standing colour" (dscan-backlog-6): [stated] 2026-11-13 "friendly kills and non-friendly kills represented by different colored rings on the map. have the ring match the standing color of the group doing the killing. if all three (neut, hostile and friendly have kills, show all three colors) maybe it has to be something similar to the differing wormhole types.", then "if there are multiple kills, find a way to represent the kill ratio when displaying those colors in the ring."

Panel review: not a fit (no outside facts; the look is the owner's eye).

## 1. What exists (main f70fdd5; find by name)

- **Kills reach the map through Near You.** `itKills` reads zKillboard's live feed (R2Z2) within the Feed's kill range; NPC-only kills are left out (`z.npc`), and a kill with no player attackers never reaches Near You (`if(att.length) itNearAdd`). `itAddKill` builds the entry: `e.pilots` = the player attackers, `e.kill.victim`, the value; `itKillSides` gives each a side.
- **A kill is a report on the map.** `itNearAdd` adds the attackers as pilots seen in the system (and, for a kill by friendlies only of a non-friendly victim, the victim as a sighting). `itMapReports` colours the system's one **report ring** from those pilots (any hostile → red; all friendly → blue; else neutral), sized by the non-friendly head count. So kills already make rings, mixed in with chat reports; nothing on the map shows which side won or lost.
- **What's kept per kill:** `st.kills` = `{t, id, v: victim side, isk}`. The victim's side is already there.
- **The label:** `itMapLabels`' `tags` adds an amber **"✕N"** after the name (every zoom: reports are always labelled). Hover: "✕ N kills here". Legend: "✕ kills".
- **Near You's kill badges and Paths to you's tags** (`itKillBadges`) are by who died (v.100): "Friendly lost" (`kf`, blue), "Hostile killed" (`kh`, red), "Neutral killed" (`kn`), with the ISK, in the order friendly, hostile, neutral.

## 2. The owner's direction (2026-11-20)

The first draft (a thin split ring outside the report ring, by who killed, arcs by share; Q1 [stated] "this works" to "the side with the most player attackers, a tie to the final blow"; Q2 [stated] "make that an option" for kills or ISK) was set aside when the owner asked [stated] "wait, maybe i've been approaching this the wrong way. the rings represent reports, never kills right now correct?" (answered: kills do make rings today, as reports; section 1), then [stated] "how would the map currently represent a system with 2 neuts, 5 hostiles and 3 friendlies killed?" (one red ring, "✕10", the split only in Near You), then [stated] "maybe instead of changing rings, we just represent the death count by standing? amber X [N] [N] [N]". ANSWERED 2026-11-20: [stated] "Yes, counts by who died (Recommended)", "Friendly, hostile, neutral (Recommended)" (order), "Yes, quick mockup (Recommended)".

So: **no new ring, no killers' side, no kills/ISK setting.** The superseded parts (K1 killers' side, K3 the kill ring, K8 the share setting) are not built.

## 3. What changes

**C1. Per system, the kills by who died:** `itMapReports` adds `kb: {f, h, n}` beside `kills`, counted from `st.kills`' `v` within "forget reports after" (an unknown side counts as neutral, as `itKillBadges` does). Worked out with the reports, never per draw (LESSON #120).

**C2. The label's kill tag:** the amber ✕, then one count per standing with deaths, each in its colour, in the order friendly, hostile, neutral; a standing with none is left out. Colours: friendly `#4f8fe0` (`--side-friendly`), hostile `#f08b7e` (`.it-kl.kh`'s text), neutral `#b9c3ca` (the neutral ring grey) (Q1 answered: pair A; the first try, `.it-kl.kf`'s light blue `#8db8f2` beside the light neutral ring grey `#b9c3ca`, was too close: [stated] "the blue and white for friendlies and neuts are too close in color/shade. can we make them contrast a bit more?"): the mockup's three pairs, A `#4f8fe0` (`--side-friendly`) / `#b9c3ca` (default), B `#7dbbff` / `#6b7781`, C `#4f8fe0` / `#d4dbe0`, each at least 15 points of lightness apart. Each a piece of the label (`put` already places pieces 4 px apart and measures them for the label boxes). Example: 78-0R6 "✕ 3 5 2" (blue, red, grey).

**C3. Hover:** "✕ 10 kills here: 3 friendlies lost, 5 hostiles killed, 2 neutrals killed", each part in its colour (the words carry it, not only colour).

**C4. Legend:** "✕ kills by who died: friendly hostile neutral", the three words in their colours; its hover "Kills here within "forget reports after", by who died: friendlies lost, hostiles killed, neutrals killed".

**C5. Unchanged:** the rings, Near You's badges, Paths to you's tags (already by who died), the Only filter "Kills from Intel", the Intel example's markers and notes (its picture's labels show the new tag where its made-up kills are).

## 4. UI rules it touches

- **Colour not the only carrier:** the hover and legend say it in words; the order is fixed (friendly, hostile, neutral), the same as Near You.
- **Colour tokens:** the badge colours already in the page (`.it-kl` text colours) and the map's neutral ring grey.
- **Drawing cost** (LESSON #120): counted with the reports, keyed; the draw only writes the pieces.
- **Crowding:** a label with three numbers is wider (about 20 px more than "✕N"); the label placer already finds a free spot or forces reports in. The mockup's busy area round C-J6MT at three zooms looks no worse than today's.
- **Phone:** nothing new to press; checked at 390 px.
- **The Intel example** (055): its picture's kill label changes; markers and notes unchanged (`intel_example_check` should still pass).

## 5. Info text it touches

- `intel` [Map]: "…; ✕ counts kills." → "…; ✕ counts kills by who died: friendlies lost, hostiles killed, neutrals killed." (+7 words; the cap is raised in 062 and 065; the build fits it after them).

## 6. DLA

- None new: the same killmails and standings the page already reads; nothing stored.

## 7. Questions for the owner

1. **Friendly / neutral colours** for the counts (after the contrast remark): A `#4f8fe0` / `#b9c3ca` (recommended: the friendly ring's own token, the neutral ring's own grey), B `#7dbbff` / `#6b7781`, or C `#4f8fe0` / `#d4dbe0`. **ANSWERED** [stated] "go with A": friendly `#4f8fe0` (`--side-friendly`), neutral `#b9c3ca` (the neutral ring grey).

Everything else answered (section 2). Superseded: Q1–Q6 of the first draft (the ring, the killers' side rule, the kills/ISK option, the badge colour clash, the ✕N total, the mockup for the ring).

## 8. Mockup (2026-11-20)

`kill_counts_mockup.html` (sent to the owner; scripts `claude/roadmap/kill-counts-mockup/`, README there; built on main f70fdd5; `test_kc.py` 38 checks pass at 1440 and 390 px; check_pii: only the page's CCP login button image, names read by hand). Made-up kills in twelve systems round C-J6MT through the page's own Near You path, 78-0R6 being the owner's example; MOCKUP box Today / By who died and three zooms.

### Reuse, don't add

| Need | Reused | New (why) |
|---|---|---|
| Counts by who died | `st.kills`' `v` (kept since v.100), `itKillBadges`' rule (unknown → neutral) | `kb` on the report (one loop in `itMapReports`) |
| Label pieces | `itMapLabels`' `put` / `tags` pieces | none |
| Colours | `.it-kl.kh` text colour, `--side-friendly`, the map's neutral ring grey (pair A, chosen) | none |
| Legend / hover | the existing "✕ kills" entry and hover line, reworded | none |

## 9. Checks (for the build)

- `kb` from made-up kills: all friendlies lost; 3 / 5 / 2 (the owner's example); one standing only; kills older than "forget reports after" dropped; an unknown side counted as neutral.
- The label's pieces: ✕ then counts in order and colours (friendly and neutral at least 15 points of lightness apart); zeros left out; the label box measured with the new width (no overlap with a neighbour in `intel_map_check`'s label test).
- Hover words and legend entry; Near You's badges unchanged and agreeing.
- Mutants: the killers' side used instead of who died; the order changed; a zero count shown; the counts worked out per draw.

## Sources

Sources: none (no outside facts). Everything above is the page's own code on main f70fdd5 and the owner's words.

## Built (build queue 066, v2026.11.21.3, branch 066-kill-counts from main 991dd4a)

As planned (C1-C5), with these differences found at the build review (the owner's answers 2026-11-21):

- **The map's redraw key** (`itMapKey`) carried only each system's kill total, so a re-work of sides (`itSidesRework`, after an EVE standings change
  or a Standings edit) could change who died without a redraw. It now carries the three counts. Checked (`map_kill_counts_check.py` "key" + a mutant).
- **Info text** (`intel` [Map]): the panel was at its cap (675 of 675) and 065 hadn't raised it, so the plan's +7 words didn't fit. The owner: [stated]
  "Shorter wording + B frees room (Recommended)": "✕ counts kills by who died (friendly, hostile, neutral)." (+6), "(your chain's k-space ends too)"
  out with the removed-hole fix (-5), and "are faded" became "fade" (-1): 675.
- **Colours:** the label's counts take the map's own colour object (`C.kill`: `C.friendly` = `--side-friendly`, `#f08b7e`, `C.neutral` =
  `#b9c3ca`); the hover and legend use one new class, `.it-mkb.f/h/n`, the same three colours (the tooltip's `.friendly` / `.neutral` are
  other shades, so they weren't reused). The legend's words are `<i class="it-mkb …">` upright.
- **The hover** is `itMapKbTipHtml(r)` / `itMapKbPartsHtml(r)` (builders, for check_html_sinks).
- **Delivered with it** (the two "ALSO WITH THE NEXT DELIVERY AFTER 064" blocks): the removed-hole map bug, fixed as option B ([stated] "B: chains
  off Intel's map (Recommended)": 062's K1 loop in `itMapWh` is gone, so only Intel's own entries are drawn; your own k-space <-> J-space jumps still
  add one through `itWhJumpAdd`, which the list removes; `itWhByTxt` lost its chain branch), and the map search's list in five system boxes
  (`.sys-cb`, `sysCbBind` on first focus, `sysCbRowHtml`, which the System Analyzer's typed box now uses too; a pick fills the box, [stated] "Fill the box (Recommended)", and a name already typed in full acts on its first Enter as before (wormhole_tab_check caught the second Enter that filling alone needed); the shorthand box left out,
  [stated] "Leave it out (Recommended)"; [stated] "No mockup (Recommended)").
- **Checks:** `tools/page_checks/map_kill_counts_check.py` (new; plan section 9 and 9 mutants), `tools/page_checks/system_boxes_check.py` (new; 7
  mutants), `wormhole_filter_check.py`'s chain case rewritten for option B (its mutant puts the K1 loop back).
- **Mockup:** `Claude outputs/kill_counts_mockup.html`, rebuilt from main 991dd4a (the page before 066) by `roadmap/kill-counts-mockup/build_kc.py`.
