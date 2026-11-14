# Route planner: plan in tool, send to game — research note

Status: RESEARCH 2026-11-12 (research session, main d227c9d, v2026.11.12.4). Planned as `roadmap/route-planner-plan.md`; BUILT 2026-11-13 as v2026.11.13.3 (build queue 047). Backlog: "Route planner: plan in tool, send to game" ([[dscan-backlog-5]]).

## The owner's asks and decisions
- [stated] 2026-11-12: "find out if we can replicate or request a route specifically as the EVE client would build it given their set options (shortest, safest, etc.)"
- [stated] 2026-11-12: "I'd like the option to set it in game for convenience. seeing the route in the tool doesn't help much if i have to manually set 25+ systems to a route manually to match the tool's route."
- [stated] 2026-11-12 "both buttons" → **"Send this route"** (every system of the tool's route as a waypoint, in order, so the game flies exactly that route) **and "Plan in game"** (destination only; the game plans with the player's own settings, jump bridges included).
- The owner's game route settings panel (his screenshot, 2026-11-12; not stored): Autopilot active; Show route path in space; Prefer Shorter / Prefer Safer (0.5–1.0) / Prefer Less Secure (0.0–0.4); Security penalty slider (his: 50); **Include Jump Bridges in Route**; Avoid Systems Where Pod Killing has Recently Occurred; **Avoid Triglavian Minor Victory Systems** and **Avoid EDENCOM Systems** (two separate boxes); Avoid Systems on Your Avoidance List; Disable Autopilot at Each Waypoint (his: on); Clear All Waypoints; Manage route.

## Findings
1. **ESI can compute a route** (public, no login): `POST /route/{origin_system_id}/{destination_system_id}`, header `X-Compatibility-Date` (spec enum 2026-08-18; the route itself from 2025-09-30), JSON body `preference` (Shorter | Safer | LessSecure, default Shorter), `security_penalty` (integer 0–100, default 50), `avoid_systems` (≤1000 unique system ids), `connections` (≤1000 one-way `{from, to}` pairs, "like Jump Bridges"); answer `{"route": [system ids]}`; `x-cache-mode: not-cached`; rate limit group `routes`, 3600 tokens / 15 min. CCP: same algorithm as the client, routes "similar, though not identical". The page's ESI_COMPAT is 2025-08-26, so this call must send a later date (per request).
   - Live test 2026-11-12 from https://threatvector.space in the owner's built-in browser: Jita (30000142) → Amarr (30002187), penalty 50: Shorter 200 OK, 12 ids; Safer 200 OK, 35 ids. CORS allowed from our origin. Headers: `x-ratelimit-group: routes`, `x-ratelimit-limit: 3600/15m`, `x-ratelimit-used: 2` per call.
2. **The page can compute it itself** (offline, no ESI budget, can add Intel-based avoids and 041's bridges): Dijkstra over INTEL_JUMPS with CCP's guide's per-jump cost into the next system: Shorter 1.0; with `p = exp(0.15 × security_penalty)`: Safer: sec ≤ 0.0 → 2p, sec < 0.45 → p, else 0.90; LessSecure: sec ≤ 0.0 → 2p, sec < 0.45 → 0.90, else p. Catch: INTEL_MAP.sec is rounded to hundredths (tools/jump_table_update.py line 143), so systems near 0.0 / 0.45 can land in the wrong band → store a 3-band class (null/low/high from unrounded securityStatus) at table build time. Tie-breaking may differ from the client.
3. **"Send this route" / "Plan in game"**: `POST /ui/autopilot/waypoint?add_to_beginning=&clear_other_waypoints=&destination_id=` (all three required; destination may be a system, station or structure), scope `esi-ui.write_waypoint.v1` (registered on both SSO apps, claude/reference/eve-sso-apps.md, so no portal change; turning it on = one more "Continue to EVE", like 029/030), answer 204, rate limit group `ui`, 900 tokens / 15 min. Send this route = first system with clear_other_waypoints=true, the rest appended (add_to_beginning=false) one request at a time, awaiting each, so they land in order; each leg is one jump, so the game has no other path (session's reasoning; hand test confirms, incl. a system on the avoidance list). Plan in game = one request with the destination and clear_other_waypoints=true.
4. **What can't be read from the game:** the spec has no route that reads the player's route settings, avoidance list or current route (paths under /ui are waypoint + four openwindow routes only). So the tool's own route uses settings the user sets in the tool.
5. **Copying the game's options in the tool:** preference + penalty: yes (finding 2). Include Jump Bridges: only once 041 has a list (ON HOLD). Pod-kill avoidance: needs per-system recent pod kills (source and window UNVERIFIED). Triglavian minor victory / EDENCOM systems: needs the system lists (no ESI source per a forum reply, secondary; SDE UNVERIFIED). Avoidance list: our own list only.

## To settle at planning
- Where the route UI lives (map From/To? ties to the jump planner item and 041's itBridgeAdj); whether the tool's route uses the in-page replica, ESI's route, or both (ESI as a cross-check while building).
- Button notes: "Disable Autopilot at Each Waypoint" stops at every system on Send this route; Plan in game may differ from the tool's line (bridges, avoid list).
- Tokens per waypoint call (ui group; routes cost 2 each); any client cap on waypoints; what ESI answers when the character is offline; waypoint order under fast sequential calls.
- Whether the route's id list includes the origin (check `route[0]` in the hand test).
- DLA: own character's UI only, nothing stored server-side (read claude/reference/dla-planning-notes.md at planning).
- Mockup (UI change) and panel review (likely not a fit: the spec and a hand test settle it).

## Sources
| Fact | Source | Checked | Status |
|---|---|---|---|
| POST /route path, body fields, limits, enums, defaults, response, not-cached, rate limit routes 3600/15m, compat 2025-09-30 | CCP ESI spec https://esi.evetech.net/meta/openapi.json?compatibility_date=2026-11-12 (version 2026-08-18), read in the owner's built-in browser | 2026-11-12 | verified |
| Route call works from threatvector.space (CORS), 2 tokens per call, Jita→Amarr Shorter 12 / Safer 35 ids | live answer seen by the session in the owner's built-in browser | 2026-11-12 | verified |
| POST /ui/autopilot/waypoint parameters, scope, 204, rate limit ui 900/15m | same CCP ESI spec | 2026-11-12 | verified |
| No ESI route reads route settings, avoidance list or current route | same CCP ESI spec (paths list) | 2026-11-12 | verified |
| ESI route rewritten (Go, GET→POST), same algorithm as the client, "similar, though not identical" | CCP developer blog https://developers.eveonline.com/blog/route-to-the-future-upgrading-the-route-route (2025-09-30) | 2026-11-12 | verified |
| Cost functions (exp(0.15 × penalty), thresholds 0.0 / 0.45, 0.90) | https://developers.eveonline.com/docs/guides/route-calculation/ (CCP's developer site, community-written docs: secondary), backed at the 047 build review by ESI's POST /route on 40 routes (all the cheapest by this rule with the unrounded band) | 2026-11-13 | verified |
| The client's route options list | the owner's screenshot of his game client | 2026-11-12 | verified |
| Each one-jump waypoint leg forces the game's path, even with the avoidance list | session's reasoning | 2026-11-12 | UNVERIFIED: hand test with a waypoint on the avoidance list |
| ESI's answer when the character is offline; any waypoint cap; tokens per waypoint call | not in the spec | 2026-11-12 | UNVERIFIED: hand test |
| Pod-kill window ("last 24 hours") | EVE University wiki https://wiki.eveuniversity.org/Star_Map (secondary) | 2026-11-12 | UNVERIFIED: settle at planning from CCP's own text or the client |
| No ESI source for Triglavian/EDENCOM systems | EVE forums https://forums.eveonline.com/t/is-there-api-saying-system-is-occupied-by-triglavians/280422 (secondary) | 2026-11-12 | UNVERIFIED: check the SDE at planning |
