# Intel map: set a "Home" system, marked with a house — plan

Status: BUILT as build queue 071, v2026.11.23.3, branch `071-intel-home` (see "Built" at the end). Queued 2026-11-23 (the owner: [stated]
"yes"; `claude/build-queue/071-intel-home.md`); all questions answered (section 10). Backlog: memory areas/dscan-backlog-9.md, "Intel map: set
a "Home" system from the map, marked with a home icon". Mockup: `Claude outputs/home_mockup.html` (scripts in roadmap/intel-home-mockup/), built
from main de2f9d2 (v2026.11.23.1).

## 1. What he asked

[stated] 2026-11-22: "also add the ability to set a "home" system from the intel map. use something like the in-game "home" system icon
(just draw it yourself)." His screenshot of the in-game icon was reference only and isn't kept.

[stated] 2026-11-23 (the questions): which Home → "Intel's own Home (Recommended)"; what Home gives you → "Route to Home,Jumps from Home on
hover"; mockup → "Yes, mockup (Recommended)".

[stated] 2026-11-23, after the first mockup (which had a route toggle in the rail): "i would put the "home" button at the top to the left
of the "center on your system". it should "center on your home system"". So the house button moved to the top bar and centers the map on
Home; the route toggle went to Home's right-click menu (Q3).

So: one system the user picks as Home, kept in this browser, its own setting (not the Wormholes tab's Home status, not your current
system). It is marked on the map with a house we draw, the hover counts jumps from it, a button at the top centers the map on it, and
its menu shows the route there.

## 2. What the page already has

- The Intel map (`itm`): `itm.home` is *your* system (the Local log or game location), `itm.D` its jumps (`itMapBfs`, gates plus your bridges
  while they're on, `itBridgeAdj`), `itMapRoute(i)` the route to you, `itm.pinned` the kept routes (cleared when you move), `itMapPinDraw`
  your pin.
- The right-click menu (047): `itRpMenuOpen`, its buttons `itRpBtnsHtml(i, inTip)` (Send destination ×2, Avoid this system); on a phone the
  same buttons sit in the tooltip of a pressed (kept) system (`itRpTipHtml`), never on your own system.
- The top bar (`itMapZoomHtml`): + − ⤢ and Center on your system (`data-im-z="me"`, `itMapCenter`: your system in the middle of the
  part no panel covers, `itMapFreeX`), 30 px, 44 px on a phone (index.html line 2986); `.it-map-zoom button[hidden]` already hides.
  The Intel example draws the same bar (line 30277).
- The colour `--wh-st-home` (#4fc3d9): the Wormholes tab's Home status (051, D26).
- The word "Home" is already in the map's code for *your* system (`itm.home`). The build should name the new one so they don't mix: e.g.
  `itm.base` / `IT_HOME_KEY` (names for the build to choose).

## 3. The design (as in the mockup)

- **Set it.** Right-click any system → the menu ends with **Set as Home**; with a Home already set it reads **Set as Home (instead of
  KOG-TA)**; on Home itself, **Show the route to Home** and **Remove Home**. On a phone the same button ends the pressed system's tooltip buttons, and your own system's
  tooltip (which has no buttons today) gets it on its own (Q4).
- **The house.** A small cyan house (`--wh-st-home`), with a dark outline and a door, drawn on the canvas above Home's dot (zoomed in,
  above its circle). If you're in Home, it sits to the left of your pin. Drawn by us; no CCP art (section 9).
- **Hover.** Line 2 of every system's hover: "9 jumps from Home (KOG-TA)", or "no gate route from Home (KOG-TA)". On Home: "⌂ Your Home"
  in the house colour. The count uses the same graph as "jumps from you" (gates, plus your bridges while they're on).
- **Center on your Home.** A house button in the top bar, left of Center on your system, shown only while a Home is set. Pressed: the map
  moves (zoom kept) so Home is in the middle of the part no panel covers, as Center on your system does for you. Title "Center on your
  Home (KOG-TA)".
- **Route to Home.** Home's menu: **Show the route to Home** / **Hide the route to Home**. On: the route from you to Home is drawn as a kept
  route, solid, in the house colour, and stays when you move (unlike the map's own kept routes) and across reloads. Off (disabled, "(you
  are here)") while you're in Home. Off by default (Q5).
- **Legend.** While a Home is set, the legend adds "⌂ Home (KOG-TA)" in the house colour after "route to you", and "route to Home
  (kept)" with a cyan line while the route is shown.
- **Remove.** Remove Home in Home's menu clears it: the house, the hover line, the route, the legend entries and the top button go.

## 4. What it keeps

`localStorage` key `tvHome` (new; no clash in index.html): `{v: 1, id: <system id>, route: <bool>}`. Removed when Home is removed.

- Safe both ways: an older page never reads it; this page ignores anything that isn't `v: 1` with a positive whole id (checked in the
  mockup: a `v: 2` value and bad JSON are ignored). A Home that isn't in the map's graph is kept but not drawn.
- Reloads when another tab changes it (`storage` event, like `IT_RP_KEY`).
- Your own system only, in this browser; nothing about other players, nothing sent anywhere.

## 5. UI rules it touches

- **One close button / chevron / tag:** none added.
- **Standing icon:** the house is a new icon (the top button and the map's mark). No existing icon means "home"; Wormholes' Home is a
  coloured border, not an icon. One SVG for the button and the hover, one canvas drawing for the map, the same shape.
- **Colour tokens only:** `--wh-st-home`, read through `itMapCol` for the canvas; the outline is the map's own dark outline colour.
- **Drawing cost (LESSON #120):** one shape in the map's normal draw; no timer, no animation. Jumps from Home are one search over the graph,
  kept until Home or the bridges change.
- **Phone:** the top button 44 px (five buttons fit the bar at 390 px, checked); the tooltip's Home button the tooltip buttons' own size (44 px, checked); no sideways scroll at 390 px
  (checked).
- **No button inside a button:** none.
- **Intel's list layout:** Near You and the Feed don't change.
- **Intel example (017):** its markers and notes don't change. The build sets Home aside in `itExSandbox` (like `itWhSt`, `itRpAside`),
  so the example never draws the user's house, hover line, route or top button (LESSON #162).
- **Legend:** two entries while a Home is set (Q2), the legend's own `span` / `i.ln` look in the house colour; it already wraps on a phone
  (checked at 390 px).
- **Page size:** small (a few hundred bytes gzipped).

## 6. Info text it touches

`CARD_INFO.intel`, its [Map] paragraph, one sentence added:
"Set as Home (right-click): a house marks it, hovers count jumps from it, the top house button centers on it, its menu shows the route."
Intel's cap is 716 words (set from 065's final count) and it is at it. This sentence takes it to about 738: the cap is raised to the final count (Q1). `CARD_INFO.whmap` and
`IT_EX_NOTES`: none.

## 7. Build notes

- The menu: `itRpBtnsHtml` gets the Home button after Avoid (role `menuitem` in the menu, a plain button in the phone's group); its click goes
  through the menu's own handler and closes the menu like the others. `itRpTipHtml`'s `i === itm.home` early return keeps the Home button for
  a phone (the mockup wraps it).
- The hover: `itMapTip`, after `itMapJbTipHtml(i)`.
- The legend: `itMapLegend`, after the "route to you" entry; drawn again when Home or the route changes.
- The route: the kept routes' set adds Home while the toggle is on; the draw picks the house colour and a solid line for it. It is found
  and drawn exactly as a kept route is (the same path), only its colour differs.
- The top button: `itMapZoomHtml`, before `data-im-z="me"`, through the bar's own handler (a `data-im-z="home"` beside `me`); centering
  is `itMapCenter` with an index (Home's or yours), one function for both. Hidden in the example.
- The house: drawn in the map's draw just before your pin (`itMapPinDraw`'s place), so your pin stays on top.
- Jumps from Home: a search from Home over `T.adj` or `itBridgeAdj()` while `itm.jbKey`, cached by Home id and `jbKey`.
- Name the new state away from `itm.home` (section 2).

## 8. Checks (for the build)

The mockup's test_ho.py (72 checks at 1440 and 390 px) as the start, against the real page:
- Set as Home from the menu stores `{v:1, id, route:false}`, closes the menu, shows the top button (left of Center on your system); "(instead of …)" names the old Home;
  Remove Home clears storage, the hover line and the button.
- The hover's count against a plain search written again in the test; "no gate route from Home" on an unreachable system; "Your Home" on Home.
- The top button: Home in the middle of the free part after a press (within 2 px); Center on your system unchanged.
- The route item: Show / Hide, stored, kept after the map's own kept routes are cleared (a move); disabled while you're in Home.
- A phone: the tooltip buttons end with Set as Home; your own system's tooltip has the button; 44 px.
- The legend: Home's entry once set, the route line only while shown, both gone after Remove Home.
- Storage: unknown version and bad JSON ignored; another tab's change picked up.
- The Intel example draws no house, hover line or route with a Home stored.
- `check_subtext.py` (the new cap), `check_ui_rules.py`, `check_card_names.py`, the "nothing moves" check, no sideways scroll, no page
  errors, `check_pii` with the names list copied in.

## 9. CCP's DLA

- **2.3 / 9.5 (other players' information, privacy):** not touched: Home is the user's own pick of a system, kept in this browser only.
- **7.2 / 7.3 (CCP's marks):** the house is drawn by us (the owner: "just draw it yourself"); no CCP icon or image is copied or combined.
- **2.5 (request load):** no new requests.

## 10. The owner's answers (2026-11-23)

1. **Info cap:** [stated] "Raise to ~738 (Recommended)": the Intel cap in `check_subtext.py` (`INFO_ALL_MAX_BY_KEY['intel']`) set from the
   final count, with his words beside it as for the earlier raises.
2. **Legend:** [stated] "Add it while set (Recommended)".
3. **Route toggle:** [stated] "Home's menu (Recommended)": Show / Hide the route to Home in Home's right-click menu; the top button only centers.
4. **Phone, your own system:** [stated] "Yes, add it (Recommended)": its tooltip gets the Home buttons on their own.
5. **Route default:** [stated] "Off until shown (Recommended)".

## 11. Reuse, don't add (the mockup's pieces → the page's)

| Mockup piece | The page's own | New on purpose, and why |
|---|---|---|
| Set as Home / Remove Home | `itRpBtnsHtml`'s buttons, `.it-rp-av` (Avoid's look), `itRpRoleHtml`, the menu's handler | — |
| Phone: own system's button group | `.it-rp-btns.it-rp-intip`, `itRpGroupHtml` | — |
| Center on your Home button | `.it-map-zoom button` (its `[hidden]` rule too), `itMapZoomHtml`, `data-im-z` handler, `itMapCenter` | its icon (`HO_SVG`): no icon means home; `itMapCenter` takes an index |
| Show / Hide the route to Home | `itRpBtnsHtml`'s buttons, `.it-rp-av` | — |
| The house on the map | the canvas draw, `itMapCol`, the map's dark outline | `hoHouse`: no shape like it |
| Hover line | `.d` (dim) for the count | `.ho-tl` for "Your Home" (colour + icon); fold into a class the build already has if one fits |
| Jumps from Home | `itMapBfs`'s search, `itBridgeAdj`, `itMapTable` | a second search from Home (cached) |
| The route | the kept routes (`itm.pinned`'s path and draw) | a Home entry kept apart from `itm.pinned` so a move doesn't clear it |
| Storage | `IT_RP_KEY`'s pattern (try/catch, `storage` event) | `tvHome` |
| Legend entries | `itMapLegend`'s `span`, `i.ln` | `.ho-ln` colour on `i.ln` (or a `--wh-st-home` modifier the build names) |
| Info sentence | `CARD_INFO.intel` [Map] | — |

## Sources

Sources: none (no outside facts). The design rests on the owner's words and the page's own code (main de2f9d2).

## Built (v2026.11.23.3, branch `071-intel-home`, 2026-11-23)

Reviewed against main 9f4a587 (v2026.11.23.2): since de2f9d2 only the Wormholes tab and `whmap#mass` had changed, so sections 2 and 7 held.
Decided at the review, on top of the plan:

1. **"Hide all routes" and the top row.** It sits a fixed distance from the map's right edge (`right:148px`, 182 with the bridge lines
   button), which the plan didn't mention: a wide map moves it over for the house too (182, and 216 with both). On a phone, measured on main
   at 390 px (a 310 px map), it already covered the + button with four buttons (11 px) and 59 px of the row with the bridge lines button,
   so six would have covered 107 px. The owner ([stated] "go with your suggestion"): on a phone the top row holds only + − ⤢ ⌂ ⌖; the bridge
   lines button and Hide all routes (a 44 px icon, `IT_CLR_ICON`, its name in the title and aria-label, the Wormholes toolbar's `.wh-tb`
   pattern) go down the rail's column under Near You's button. LESSON #179.
2. The right-click menu's accessible name is the system's name alone (it was "X: send destination to EVE"; it holds Home's items now).
3. Home and its route setting are in `itMapKey` (`|ho:<id>.<0|1>`).
4. The route to Home is always the house colour, whatever is reported at Home (the mockup coloured it by the report, like any kept route).
5. Hide all routes doesn't clear the route to Home: Home's own menu item does (it is kept apart from `itm.pinned`).
6. The mockup was rebuilt from its scripts at de2f9d2 for `Claude outputs/` (72 of 72 of its checks pass).

Names in the build (section 2's "for the build to choose"): `itHo` (`{id, route}` and the jumps cache), `IT_HO_KEY` (`tvHome`), `itHoRead` /
`itHoSave`, `itHoIdx`, `itHoDist`, `itHoTipHtml`, `itHoBtnsHtml`, `itHoAct`, `itHoBtnPaint`, `itHoLegHtml`, `itHoDraw` / `itHoHouse`
(`itm.hoBox` keeps names off the house), `IT_HO_ICON` (the mockup's `HO_SVG`), `itHoAside` (set in `itExSandbox`); `.it-ho` and `.it-ho-ln`
(the mockup's `.ho-tl` / `.ho-ln`: no class already colours with `--wh-st-home` in a tip or the legend). `itMapCenter(draw, i)`.

The info sentence is the plan's, word for word: the Intel panel's final count is 741, the cap set to it (Q1's "about 738").

Checks: `tools/page_checks/intel_home_check.py` (new, areas intel + layout, SLOW 1200 s; 14 mutants); `route_planner_check.py` now reads the
menu's fourth item (Set as Home, on for your own system).
