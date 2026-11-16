# Ansiblex zones: can routes keep off bridges that cost capacitor? (research, 2026-11-16)

Research session, read-only. Question from the owner, 2026-11-16: "find out if we can use the recently implemented jump ansiblex changes to eve (specifically, how they work differently based on their range from the capital system) in order to generate routes that avoid using jump bridges outside of zone 1 if we're not jumping back into zone 1."

**Answer: yes.** CCP's rule and ESI give everything the page needs, and it needs no login. **PLANNED 2026-11-16:** all questions answered (below); plan `claude/roadmap/ansiblex-zones-plan.md`, mockup scripts `claude/roadmap/ansiblex-zones-mockup/`. Not queued. **BUILT** as build queue 057 (v2026.11.16.6): `roadmap/ansiblex-zones-plan.md`.

## How the zones work (CCP, live since 2026-09-22)
- A jump costs capacitor by ship class × the zone multiplier. The zone comes from the light-years between the **jump's endpoint** (the bridge you arrive at) and the **owning alliance's capital system**. How far apart the two bridges are doesn't matter.
- Zones: 1 = 0–5 LY ×0 (free) · 2 = 5.1–10 ×2 · 3 = 10.1–15 ×6 · 4 = 15.1–20 ×9 · 5 = 20.1+ ×15.
- Capacitor: 1250 TJ, about 200 TJ an hour, about 6.25 h from empty. Neuts and remote cap don't touch it.
- Base costs run from 1 TJ (capsules, shuttles, haulers, freighters, JFs) to 19 TJ (Marauders, Rorquals). Capitals can't use bridges. Rorquals, freighters and JFs can.
- Access: only pilots in the alliance that holds sov in the **starting** system. ACLs can no longer let outsiders in.
- Since patch 2026-10-13.1: a 30-day cooldown to change the capital (the dev blog had said 90; the patch notes win). An alliance that loses its capital waits 30 days for a new one, and until then **every jump costs as zone 5**.
- No route/autopilot or ESI change is listed in the patch notes. The game's own "Include Jump Bridges in Route" setting is not known to weigh zones (UNVERIFIED).

## What that means for routing
- The owner's rule ("avoid bridges outside zone 1 unless jumping back into zone 1") is the same as **"use a bridge only when the system you arrive in is within 5 LY of the capital"**. Because only the endpoint counts, that means **use free jumps only**.
- So a bridge is **one way for this rule**:
  - both ends in zone 1: usable both ways;
  - one end in zone 1: usable only toward that end (the trip home is free, the trip out costs);
  - neither end in zone 1: never used.
- A bridge reaches 5 LY at most, so a free jump can only start within about 10 LY of the capital.

## The data the page needs
1. **The bridges.** 041's pasted list (one per line). There's still no ESI route for bridges (see `jump-bridges-sources-research.md`).
2. **Each system's 3D position and LY.** Already in the page (`itMapTable().p3`, `itMapLy`, CCP's 9.46e15 m light-year, from the map LY item v2026.11.04.1).
3. **The capital system and who holds sov.** **ESI `GET /sovereignty/systems`** (read in the owner's built-in browser, 2026-11-16, spec version 2026-08-18, served at compatibility date 2026-05-19, so it came with Equinox ESI):
   - public, no login, `access-control-allow-origin: *`, cached 5 minutes, rate-limit group `sovereignty` 600/15m;
   - answers only with a compatibility date of 2026-05-19 or later (404 with the page's 2025-08-26, and 404 under `/latest/`); `https://esi.evetech.net/sovereignty/systems?compatibility_date=2026-05-19` works as a plain GET (no header, so no preflight);
   - `{solar_systems: [{solar_system_id, claim: {alliance: {alliance_id, corporation_id, claimed_since, is_capital_system, sovereignty_hub{id, vulnerability_window}, development{activity_defense_multiplier, military/industrial/strategic_level}}} | {faction} | {unclaimed}}]}`;
   - live answer: 5,485 systems, 2,692 held by 74 alliances; **72 alliances flag exactly one capital, 2 flag none, none flag two**. About 1.27 MB of JSON, about 76 KB gzipped;
   - the old `/sovereignty/map` route is gone from the spec (only `/sovereignty/systems`, `/sovereignty/campaigns` and the corporation's sov-hub routes are left);
   - ESI notifications also have an `AllianceCapitalChanged` type (character notifications, needs a login scope; not needed for this).
   - From it, per bridge: the sov holder of the starting system (is the bridge usable by you at all?) → that alliance's capital → LY from the capital to the endpoint → zone.

## Where it plugs in (main 51207b6)
- 047's route planner (Threat Vector's route: `itRpUpdate`, its avoid rules) is the place for it. "EVE's route" can't apply it: the game plans with its own settings, and no ESI route reads or sets them.
- ESI's `POST /route/{origin}/{destination}` takes `connections` as `{from, to}` pairs, so **one-way** bridges can be passed. If any route ever uses ESI's planner, only the allowed directions get sent.
- 041 (jump bridges, hold lifted 2026-11-14, not built) treats each bridge as two-way (`itBridgeAdj`) for the map. Zone filtering needs a one-way list for routes.
- "Send this route" sets a waypoint on every system. Across a bridge, the game moves between two waypoints by its own route: the bridge if its "Include Jump Bridges in Route" is on, gates if it's off (UNVERIFIED: hand test).

## Edges
- **5.0–5.1 LY gap:** CCP's table goes "0 - 5" then "5.1 - 10". Whether 5.04 LY is zone 1 is not said (UNVERIFIED). Safe side: zone 1 only at ≤ 5.00 LY. The page already rounds LY **up** (the owner's rule), so a shown "5.01" correctly reads as outside.
- **No capital** (lost, 30-day wait): every jump costs as zone 5 → no free bridges. The route uses no bridges and says why.
- **A bridge in a system your alliance doesn't hold:** you can't use it at all (alliance-only access). Drop it from routes and mark its row in the list.
- **Sov changes:** read again when the cache expires (5 min) or on route planning, never sooner than `Expires`.
- **Capital changes are slow** (30-day cooldown), so a short cache is plenty.

## The owner's answers (2026-11-16)
1. Where: "Threat Vector's route only (Recommended)" (map counts as 041 plans).
2. Strictness: [stated] "A setting with a checkbox for each zone with only zone 1 turned on by default."
3. Your alliance: "Both: login, then sov (Recommended)".
4. Bridges you can't use: "Leave out + warn on row (Recommended)".
5. Zone 1 edge: "At 5.00 LY (Recommended)".
6. Show zones: "Bridge list rows (Recommended)", "Map bridge hover", "Route steps".
7. Checkboxes in "Route settings (Recommended)"; mockup "Yes, mockup (Recommended)".

## Sources
| Fact | Source | Checked | Status |
|---|---|---|---|
| Zones, multipliers, endpoint-to-capital rule, capacitor 1250 TJ, recharge, no neut/RCT, capitals out, alliance-only via start system's sov | https://www.eveonline.com/news/view/patch-notes-version-24-01 (CCP patch notes 2026-09-22.1) | 2026-11-16 | verified |
| Capital cooldown 30 days; lost capital → 30-day wait, every zone counts as 5 | https://www.eveonline.com/news/view/patch-notes-version-24-01 (CCP patch notes 2026-10-13.1) | 2026-11-16 | verified |
| Per-class TJ table; distance between bridges doesn't matter; worked examples (cost by the destination's zone) | https://www.eveonline.com/news/view/force-projection-ansiblex-capacitor-update (CCP dev blog) | 2026-11-16 | verified (the Rorqual row's zone 2/3 values don't follow the pattern; not used) |
| Outward costs more, returning to the centre costs much less | https://www.eveonline.com/news/view/major-update-force-projection-revamped (CCP) | 2026-11-16 | verified |
| `/sovereignty/systems` fields incl. `is_capital_system`; public; CORS; cache 300 s; group 600/15m; compatibility date ≥ 2026-05-19 (query form works); live counts | https://esi.evetech.net/meta/openapi.json?compatibility_date=2026-11-15 and live GETs, in the owner's built-in browser | 2026-11-16 | verified |
| 5.0–5.1 LY boundary; game autopilot and zones | none found | 2026-11-16 | UNVERIFIED: the plan's hand test steps 1 and 4 |
