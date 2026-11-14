# How the numbers are worked out

This was the "How effective HP and DPS are calculated" note at the bottom of every fit, one long paragraph. The owner
(2026-10-24): "At this point it's impossible to read and comprehend in that format. perhaps it needs to be it's own
document." It moved here in v2026.10.14.51, split into sections and brought up to date. The short version of each
section is behind the matching card's ⓘ button on the page (`CARD_INFO` in index.html). Since build queue 036
(v2026.11.11.3) the panels are short, and the detail they no longer carry is here: the cards' own sections below, then
who's in the system, sides and logging in with EVE, and Intel.

Everything follows pyfa (the verified version is in `tools/pyfa_core_manifest.json`). Where the tool deliberately
differs, it's listed in `DEVIATIONS.md`. **Treat every number as a ceiling, not a guarantee:** all skills are assumed
at level V, so a less-trained pilot with fewer damage modules hits softer and tanks less.

## Effective HP and resists (Resistance card)

- **Resist sources:** every source pyfa applies to the fit, with pyfa's own rules:
  - Damage Control, hardeners, amplifiers, membranes and resist rigs;
  - a Bastion Module and hardener scripts;
  - a Tactical Destroyer's Defense Mode;
  - the hull's own resist bonuses (special-edition hulls included);
  - Shield and Armor Compensation skills at V.
- **Stacking penalties** follow pyfa's groups:
  - hardeners, amplifiers and rigs penalize each other;
  - Damage Control, a Bastion Module and a Reactive Armor Hardener penalize each other in a separate group;
  - hull bonuses aren't penalized.
- **Reactive Armor Hardener:** simulated exactly as pyfa does by default, against an even 25% per type incoming
  profile, after every other resist source. Its real split depends on the incoming damage, which a killmail can't
  reveal.
- **Polarized weapons:** a fitted Polarized weapon sets every resist to 0%, as in the game.
- **Hit points:**
  - the hull's base HP;
  - plus plates, shield extenders, and Reinforced Bulkheads / Nanofiber Internal Structure (flat HP or a multiplier,
    whichever the module uses);
  - plus Trimark Armor Pump and Core Defense Field Extender rigs, minus other rigs' HP drawbacks;
  - plus Shield Management, Hull Upgrades and Mechanics at V.
- **Strategic Cruisers** (Tengu, Legion, Proteus, Loki): subsystems count like any other module. That includes flat
  shield and hull HP, and any hardener-style resist a Defensive subsystem carries.
- **EHP** is each layer's HP against an even mix of the four damage types.

## Repairs and Break Point (Resistance card, Repairs strip)

- **Sources:** a fitted Shield Booster, Armor Repairer or Hull Repairer, from the module's own repair amount and cycle
  time.
- **Armor and hull:** Repair Systems / Capital Repair Systems at V (25% faster cycling).
- **Shield Booster:** gets no skill bonus. Its required skill, Shield Operation, only speeds up passive shield
  regen, not the booster. This is a real asymmetry in the game, not an oversight.
- **Passive shield regen:** its peak (reached near 25% shield), 2.5 × shield HP ÷ recharge time.
- **Break Point:** the sustained DPS an attacker needs to outpace that layer's repair or regen. A dash means the layer
  has no repair module (pure buffer), not a missing number.
- **Ancillary Armor Repairer:** also shows a burst figure while its Nanite Repair Paste lasts, because its repair
  amount roughly triples then.
- **Ancillary Shield Booster:** its Cap Booster charges only change where the activation cost comes from, not the
  repair amount.

## DPS (Firepower card)

- **Turrets and launchers:** DPS is calculated per weapon.
  - First from the exact charge that weapon had loaded (the same killmail flag as the gun).
  - Only when a gun has no identifiable loaded charge, from a category-matched guess at spare ammo in cargo or the
    fleet hangar. Total and Weapon DPS then show a range, and the ammo is listed at the bottom of the card.
- **Other sources:** drones, fighters and fixed-damage weapons. Smartbombs cycle 25% faster with Energy Pulse Weapons
  at V.
- **Vorton Projector (EDENCOM):** trains on its own three-skill tree, not the turret skills, and is scored with that.
- **Drones:** only as many as the hull can have in space at once (the lower of max active drones and drone
  bandwidth), hardest-hitting first, not every drone in the bay.
- **Fighters** (carriers, supercarriers, FAXes): only as many squadrons as the hull's launch tubes and per-class
  (light / support / heavy) limits allow, hardest-hitting first, then support squadrons in the tubes left (webs
  first). Since v2026.10.14.66 you choose them in the Fighter bay: one square per squadron, and each type's
  abilities (the game's icons) on or off. A damage ability switched off adds nothing; a speed ability switched on
  makes the squadron faster in the fight, as pyfa's handler does. Since v2026.10.14.70 a support squadron's web (Dromi)
  slows the target in the fight, as pyfa's damage graph applies it; its neutralizer, ECM and warp disruption (Cenobite,
  Scarab, Siren) are shown on the EWAR / Misc card with the carrier's bonuses, not applied.
- **Skills, all at V:**
  - Turrets and missiles: damage and rate-of-fire skills (Surgical Strike / Rapid Firing, or Warhead Upgrades /
    Rapid Launch), plus the weapon-size and T2 Specialization skills.
  - Drones: damage-only skills (Drone Interfacing, the size skill or Sentry Drone Interfacing, racial Drone
    Specialization on T2 drones).
  - Fighters: damage-only skills (Fighters, Drone Interfacing's fighter bonus, Heavy Fighters, racial Fighter
    Specialization on T2 light squadrons).
  - Drones and fighters have no rate-of-fire skill.
- **Damage modules and rigs:** Gyrostabilizer, Magnetic Field Stabilizer, Heat Sink, Ballistic Control System, Drone
  Damage Amplifier, the rate-of-fire rigs, Bay Loading Accelerator and Warhead Calefaction Catalyst rigs, and Sentry
  Damage Augmentor rigs on sentries. Each is stacking-penalized against its own kind.
- **Synchronizer rigs** (EVE's Fractured Skies, pyfa v2.70.0): each of its bonuses grows by one (a percentage point for
  most) for every matching faction module fitted and online (Imperial Navy, Caldari Navy, Federation Navy, Republic Fleet,
  Dark Blood, True Sansha, Dread Guristas, Shadow Serpentis, Domination); its drawbacks don't change. Its weapon damage joins the same penalized
  chain as the damage modules above; its drone damage joins the Drone Damage Amplifiers'. A mutated faction module seen
  on a killmail can't be counted (the killmail doesn't say what it was made from).
- **Hull bonuses:** the hull's role and skill bonuses at V (a Vexor's hybrid damage, a Drake's kinetic missiles). On a
  Strategic Cruiser the bonus comes from the fitted Offensive subsystem instead.
- **Siege-type modules:**
  - **Bastion Module** (Marauders): doubles turret and launcher rate of fire while running.
  - **Siege Module** (Dreadnoughts): a much larger flat damage bonus. Turrets get damage only; launchers get damage
    and rate of fire.
  - **Industrial Core** (Rorqual / Orca / Porpoise): doesn't affect turrets or launchers. While running it adds a
    large stacking-penalized drone damage bonus (+100% on a Capital Industrial Core II), boosts and speeds up local
    shield boosters, and multiplies scan resolution.
  - **Triage Module** (Carriers): no effect on weapon damage or rate of fire.
  - All four run by default and immobilize the ship while running, so a fitted one shows 0 m/s. Siege, Triage and
    Industrial Core also multiply mass by 10, which shows in align time.
- **Bombs:** a bomb's damage over the launcher's cycle and its long reactivation delay, as pyfa counts it.
- **Volley:** one shot from every weapon, drone and fighter at once, exactly as pyfa's Volley. It's the instant alpha,
  not a sustained rate, so it ignores different cycle times.

## Weapon range (Firepower card's weapon rows)

- **Turrets:** optimal + falloff with the loaded ammo, Sharpshooter / Trajectory Analysis at V. A Vorton Projector
  uses Vorton Arc Extension instead.
- **Missiles:** the flight range as pyfa computes it: flight time plus the ship-radius bonus, flown in whole seconds,
  with acceleration, measured from the ship's surface, capped for auto-targeting missiles. Hover it for the two
  possible distances. Missile Projection / Missile Bombardment at V.
- **Bonuses included:** the hull's or subsystem's range bonuses, Tracking Enhancers and Computers (with a loaded
  Optimal Range or Tracking Speed script), Missile Guidance Enhancers and Computers (with their scripts), range rigs,
  a Bastion Module, and a Tactical Destroyer's Sharpshooter Mode. All stacking-penalized as pyfa does.
- **What range is not:** this is how far a weapon reaches. How much of its damage *lands* at a distance depends on
  the target's signature and speed; that is on the Damage Application card (pyfa's damage graph).
- **Not shown:** weapons only resolved through the cargo-ammo guess, and drones, whose engagement range is up to
  their pilot.

## Module states (Fit card)

- **When bonuses apply:** as in pyfa, only in the state that turns them on. A hardener, repairer, weapon or
  propulsion module needs to be running; most other modules only need to be online. Only running modules use
  capacitor.
- **Default states:** a killmail doesn't say what was running, so every module starts running if the game allows
  it, with these limits:
  - one propulsion module at a time (the fastest);
  - only as many Command Bursts or similar as the hull permits;
  - cloaks, Micro Jump Drives and Field Generators, a Signature Suppressor's burst, Entosis Links, Capital Sensor
    Arrays, an Assault Damage Control's burst, a cynosural field (a lit one immobilises the ship; a fitted one isn't
    necessarily lit) and a Heavy Interdictor's Zero-Point Mass Entangler (it pins the ship in place, and a Heavy
    Interdictor runs it only once tackled) start online, not running;
  - the siege family (Bastion, Siege, Triage, Industrial Core) runs, by the general rule.
- **Implants and boosters** on the killmail or in the paste are in every number, as in pyfa. Booster side effects are
  off (pyfa's default).
- **Changing states:** switch any module off, online or active on the Fit card and every number recalculates. The
  game's rules still apply: one propulsion module running at a time, Bastion blocks the Micro Jump Drive, and so on.
  A drone square puts drones in space or takes them back. The reset icon puts every module and drone back to its
  default state, and the fit's own charges. A rack's ⋯ sets every module in it active, online or off and unloads that
  rack's charges. A charge the fit doesn't have is marked not on board, and so is the card while one is loaded.
- **Tactical Destroyer modes:** a mode is a built-in ship state, not a fitted item, so a killmail can't show which one
  was on and all three are computed. Every mode effect comes from pyfa's own handlers. Sharpshooter is shown first
  because it changes DPS (Primary on the Anhinga, pyfa's default too).

## The Charges list (Fit card, Charges)

- **The two numbers** each charge changes on this fit, when every copy holds it, skills at V: a weapon's or bomb's DPS
  and range; a Capacitor Booster's injection and the capacitor; an Ancillary Shield Booster's clip and the capacitor;
  an Ancillary Armor Repairer's repair with and without paste; a script's effect on your weapons, sensors or target; a
  Command Burst charge's buffs; a probe's bubble.
- **Order:** charges on board first (loaded, then cargo); the rest are marked not on board, best first. The chips
  filter by damage type (weapons and bombs) and, on a fit with more than one module that takes charges, by module.
- **Loading:** a click loads every copy; a drag onto one module loads that one, onto the ring's middle every module that
  takes it. Capacitor Boosters, Ancillary Shield Boosters and Ancillary Armor Repairers take one charge for all their
  copies, so a drop on one loads them all.
- **Unloading:** an unloaded weapon or bomb launcher goes online (EVE can't run it with no charge) and does no damage;
  loading a charge makes it active again. Any other module keeps its state and works as it does with no charge: a
  Capacitor Booster injects nothing, an Ancillary Shield Booster runs on capacitor, a scripted module works as the plain
  module. Charges in cargo don't refill a module you unloaded.

## Navigation & Targeting card

- **Speed:** top speed with the fastest propulsion module running (assumed, as in a fight); the line under it with it
  off. **Align time:** without the propulsion module, with it on in the line under it. Both as pyfa: skills at V,
  plates, rigs, the hull's bonuses.
- **Signature radius:** without the MWD; the line under it with the MWD running (its signature bloom).
- **Drone control range:** base + skills (Drone Avionics, Advanced Drone Avionics at V) + Drone Link Augmentors + hull
  bonus + boosters; hover the line for the parts.
- **Targeting range, scan resolution and sensor strength:** skills at V and fitted Sensor Boosters, Signal Amplifiers,
  a Bastion and similar modules, as pyfa.

## Capacitor (Capacitor card)

- **State:** pyfa's capacitor simulation: every running module on its real cycle for 6 hours, staggered, Capacitor
  Boosters injecting when needed. Stable shows the % it settles at; otherwise how long until it's empty.
- **Best case:** a running Capacitor Booster injects and a running Ancillary Shield Booster has charges. Their icons
  sit by the ring; the Ancillary Shield Booster's icon switches to out of charges. A pasted fit with no charges anywhere
  gets none.
- **The ring:** green (50% and up) through amber to red when it runs out. Its hover gives the in-game fitting window's
  figure (pyfa's EVE stability value).
- **Net cap rate** is the simple average (peak recharge − drain + injection); the state comes from the simulation, so
  the two can disagree.
- **Drain resistance:** a fitted Capacitor Battery cuts incoming neutralizers and nosferatu by that much; the EWAR card's
  own neutralizer figures assume an unresisted target.

## EWAR / Misc card

- **Chips:** one per module type: T tackle (scrams, points, webs, bubbles), D disruption (ECM, dampeners, weapon
  disruptors, target painters, burst jammers and projectors), C capacitor warfare (neutralizers, nosferatu), B command
  bursts. Ranges are optimal + falloff, skills at V, with the hull's, subsystems' and rigs' bonuses.
- **Support fighters** in space get one chip per squadron type (a Dromi's web, a Siren's warp disruption, a Cenobite's
  neutralizer, a Scarab's ECM), each for one squadron with the carrier's bonuses. Only the web counts in the Damage
  Application card and the times, as pyfa's damage graph does; the rest is shown, as module neutralizers are.
- **Misc (!):** what changes the fight outside its stats: a cynosural field, Micro Jump Drives and Field Generators, an
  Interdiction Nullifier, a PANIC.

## Weaknesses card

- **Least resisted:** the damage type that gets through its resists best, averaged over shield, armor and hull by how
  many hit points each layer has (resists as fitted, skills at V). The title says whose weaknesses these are: the
  threat's, or yours (Your Weaknesses, in My Fit Perspective and on Viewing My Fit).
- **Capacitor drains:** its capacitor runs out with every running module cycling, even at best case (a fitted Capacitor
  Booster or Ancillary Shield Booster on charges). No charges: a booster with none loaded and none in cargo (pasted fits
  only). No paste: an Ancillary Armor Repairer with no Nanite Repair Paste loaded or in cargo (pasted fits only), so no
  3x boost.
- **Without your ship:** the ammo and drone type for each weapon system that hits that weakness hardest; a turret system
  that can't deal it falls back to the next weakest type.
- **Missiles:** the best ammo for each launcher, and how much of its damage lands on this ship's signature and speed,
  MWD (or afterburner) off and on, with skills at V; your rigs and modules aren't known. Under 50% is amber; the tile
  counts the launchers landing 95% or more.
- **Fighters:** the T2 light fighter, heavy fighter and bomber of that damage type, and how much of each one's damage
  lands, as pyfa applies it at this ship (fighters fly to it): its signature and speed with its MWD (or afterburner) off
  and on, and its resistance to fighter missiles (a heavy fighter's torpedoes are built for capitals: a smaller ship
  takes a tenth). Skills at V and no carrier bonus; abilities as pyfa sets them, with the bomber's bomb on.
- **With your ship** (your fit saved and Use in assessments on): your own ammo, drones and fighters against it, best
  first by how long it lasts with that loaded (damage by type against its resists, layer by layer, minus its repairs
  while its capacitor lasts; the rest of your fit as it is). Only what's aboard counts; fighters get one pick per class
  (light, heavy), in that class's squadrons, with their abilities as set in the Fighter bay. The DPS is pyfa's applied
  DPS at the range and movement set on the Damage Application card. In My Fit Perspective, the same for their ammo
  against you.

## The fight (Damage Application card, Matchup and its strip)

- **Damage applied:** pyfa's damage graph, at one distance and one movement for each ship, with the attacker's own
  webs (modules, drones and support fighters), target painters and scram applied (pyfa's default). Resists aren't counted there; lock range is ignored.
- **A weapon with no charge loaded** (v2026.10.14.67): charted with the charge aboard that kills you fastest at this
  fight (the one the Weaknesses picks name first), marked "Assumed loaded" on the card and in the Matchup's hover.
  The Firepower card shows every charge aboard as a range.
- **Fighters** (v2026.10.14.64): each damage ability of each squadron in space (Attack and Missiles; bombs are off by
  default, as in pyfa), pyfa's `getFighterAbilityMult`. A bomb switched on in the Fighter bay (v2026.10.14.71) lands
  anywhere, no lock needed, at min(1, your signature / its explosion radius). The others:
  - a squadron at least as fast as you follows you and has its full range; a slower one is put at the carrier's
    centre and hits only within its ability's range of it (Attack: optimal + falloff; Missiles: a hard limit). Its
    speed is pyfa's, with its MWD ability off (pyfa's default; the owner 2026-10-25), after skills (Light Fighters,
    Drone Navigation), hull bonuses, Drone Navigation Computers, Fighter Support Units and rigs; switched on in the
    Fighter bay (v2026.10.14.66), the MWD, afterburner or evasive maneuvers adds its own speed bonus, stacking-
    penalized with the computers as in pyfa;
  - then the explosion maths of missiles against your signature and speed;
  - superiority fighters' missiles deal 5% to a ship, heavy fighters' torpedoes 10% to anything that isn't a
    capital or freighter (the target ship's anti-fighter / anti-capital missile resistance; a hull without it has the
    attribute's default). The raw DPS on the Firepower card is pyfa's raw number (full damage); its hover says so.
- **Movements** (in-game names, for both ships):
  - **Stopped:** speed 0.
  - **Approach:** straight at the other ship (no transversal), at the chosen share of top speed.
  - **Orbit:** at 90° to the line of sight, at the chosen share of top speed.
  - **Keep at Range:** straight away from the other ship at the other's closing speed (its speed when it
    approaches, 0 otherwise), up to its own top speed, so the distance holds; pyfa's graph gets that speed, at 180°.
    Not offered inside the other ship's scram or web range, or when the other ship closes faster than it can fly;
    chosen and then no longer possible, it's marked amber.
- **What the chart marks** (v2026.10.14.54): their EWAR that reaches you, shaded from 0 out to its range with the
  EWAR / Misc card's letters and colours: **T** their warp scrambler and furthest web (the same inputs pyfa's graph
  applies), **D** their furthest target painter, **C** their furthest running neutralizer and nosferatu (each module's
  optimal range). Darker where two reach. Numbered pins mark their lock range and drone control range. The x axis
  prints their tackle distances and your range, the y axis the DPS there. While a slider is dragged the y axis only
  grows; it fits again on release. Markers are presentation only; the lines are pyfa's.
- **Your card** (v2026.10.14.55, My Ship Perspective): the same chart for your guns on them: your ship as the attacker,
  the threat as the target with its fit's own speed and signature (its prop module as it runs), your webs, painters
  and scram applied, the same fight. Its number is the board's "DPS applied to them".
- **The range** (v2026.10.14.56) runs to whichever ship reaches farther (weapons, drone control range, a fighter
  ability's range from the carrier's centre (v2026.10.14.64), or 1.25 × its default range), on both cards and the
  strip; with no ship saved, to the threat's reach.
- **Where it starts** (v2026.11.14.1, build queue 048; the owner: "we should have set it to their optimal range."): at the optimal of the
  threat's weapon group with the most raw DPS (its highest-DPS weapon): turrets and sentry drones their optimal alone; missiles their flight;
  Vorton projectors and smartbombs their range; mobile drones only, or nothing that deals damage, 10 km. Reset goes back there.
- **One fight:** the strip under the Matchup and the card's Adjust panel set the same values, and both perspectives
  use them. The chart is a snapshot at that distance, as pyfa's graph: it doesn't play the fight out over time.
- **They last / you last** (not a pyfa number): damage by type against each layer's resists, shield then armor then
  hull, minus that layer's local repairs and the shield's peak passive regen, with the repairs stopping when pyfa's
  capacitor simulation runs dry. An Ancillary Shield Booster on charges (v2026.10.14.57) doesn't need the capacitor:
  it reps for a clip (an X-Large with Navy Cap Booster 400s: 9 cycles, 45 s), reloads for 60 s, and repeats while
  charges last (loaded plus hold), then stops. An Ancillary Armor Repairer with Nanite Repair Paste (v2026.10.14.61)
  repairs 3x for its clip (8 cycles; a Medium with Repair Systems V: 72 s) from when the armor starts taking damage,
  reloads for 60 s with no repair, repeats while paste lasts, then repairs its plain amount; it needs the capacitor
  either way. A killmail with no paste seen assumes a full clip. "holds" means the damage never gets through.
  - Not used, kept here so it can be brought back: pyfa's "factor in reload" average for an ASB, its rate x
    (clip x cycle) / (clip x cycle + reload) for the whole fight (84 HP/s instead of 196 for an X-Large with
    Navy Cap Booster 400s). It hides the reload gap, which is where a ship running an ASB usually breaks.
  - **Why** (v2026.10.14.58): hover a time on the board (tap it on a phone) for a sentence or two from the same
    steps: layers with no repairer together ("With no armor or hull repairer, the rest goes in 21 s."), and for a
    layer with one, what its repairers were doing when it broke: an ASB reloading ("21 s into your X-Large Ancillary
    Shield Booster's first reload"), out of charges ("then has nothing left to load"), the capacitor run dry, or still
    repairing ("even with ..."). Clock times (1:06) count from the start of the fight.

## Who's in the system (System Analyzer, Pilot Analyzer, Fleet tab)

- **Local and D-Scan:** paste the Local member list (in the Local window, select the members and press Ctrl+C) and, if
  you have one, your D-Scan. Local lists everyone in the system, in space or docked; the D-Scan shows only ships within
  about 14 AU of you. Each name is looked up on ESI (its corporation and alliance) and sorted by your Standings.
- **Pilot rows:** up to the "pilot rows up to" number of hostile + neutral pilots (15 unless you change it, at most 30,
  in the System Analyzer's settings) is a small gang, one row per pilot; more is shown by group. Groups shows the
  columns for a small gang too. Each pilot is 2 zKillboard requests (kills and losses, kept for an hour), 15 pilots at a
  time. A row opens that pilot in the Pilot Analyzer, on that hull, its dossier on the same gang size.
- **Possible ship,** for a gang size: from their newest 50 kills and 30 losses, as the Pilot Dossier. Auto picks each
  pilot's size from how many of their alliance (or corporation, without one) are in Local; an NPC corporation counts as
  solo. The ship is the hull of their newest kill in that size (All: their newest kill or loss); a ship of theirs
  from the last 30 days that's on your D-Scan comes first. No kill in that size: the newest ship they were seen in
  within 30 days, else the hull they lost most.
- **Kills and losses in the system:** one zKillboard request per system an hour, then the killmails from ESI, newest
  first, 300 at most (zKillboard lists 1,000); the hours chosen run from 1 to 72. Each group, corporation, pilot and
  hull counts its own kills and losses; folded rows show none.
- **Hostile from lately:** zKillboard's list of your alliance's (or corporation's) losses in the past 7 days (one
  request, kept for an hour) and the newest 50 of those killmails from ESI; every attacking pilot's alliance (or
  corporation, without one) counts.
- **Affiliation:** one zKillboard request per pilot after the analysis' own, kept an hour; corporation lookups are kept
  an hour, names and tickers a week. Kills, losses and ISK destroyed are zKillboard's totals.
- **Pilot Dossier:** each killmail is read from ESI and kept. Hulls are listed newest first (in a gang size, by their newest kill in it), the count only breaking a tie; the 8
  used most recently follow the one asked for; Show N more
  hulls shows every hull read, with no new request. Gang size counts the players on the killmail (anyone who joined in
  counts). Weapons seen: the weapon each killmail credits them with; Flies with: the other players' hulls on those
  kills; Kills mostly: what they killed, by ship class; Active: the hours of their kills in your own time zone; Usual
  systems: where their kills and losses were. The kills under a row show 10 at a time; Show 10 more reads older kills
  from ESI once those are shown (no new zKillboard request).
- **Fleet tab fits:** each fit by the Pilot Analyzer's rule for a chosen hull: their newest loss in that hull; none,
  their alliance's (or corporation's) most common fit for it, said as not theirs; none, fit unknown (the bare hull, no
  DPS). Load asks zKillboard once (twice when it also needs their alliance's). Load all with Common fits (the choice
  above 10 pilots) asks once per alliance and hull (this week's losses first, all of them when the week has fewer than
  2), and a pilot who is a victim in that list gets their own loss from it; Own fits (up to 10) asks per pilot. Answers
  are kept an hour; Load all stops with 25 of the page's 100 lookups per 10 minutes left for the rest of the page and
  carries on by itself when older requests age out. Rows stay in damage order until every pilot is in, then sort once:
  the pilot whose dossier you came from first, then by DPS. Damage, its share and the final blow come from the
  killmail (no request). A fleet's main weapon is the one doing the most DPS on each fit.

## Sides and logging in with EVE (Standings, the profile's EVE tab)

- **Standings lists:** your pilot's corporation and alliance are looked up again each time you analyze Local, so a
  change of corporation is picked up. Friendly and hostile lists take full names, one at a time or one per line; a
  ticker in < > or [ ] after a name is ignored; adding a group to one list takes it off the other. Suggested
  friendlies are one zKillboard request, kept for an hour. Everything here is saved in this browser only.
- **The login:** Threat Vector uses CCP's login for apps with no server of its own (no secret anywhere). Each feature
  on the EVE tab needs its own permission from EVE: Use my game location (your character's location), Show when I'm
  online in EVE (whether it's in the game), Use my corporation's and alliance's EVE standings (their contacts). EVE's
  page lists what the trip asks for, and you agree to all of it or cancel; Continue to EVE asks again for everything you
  have on. While a feature uses the login, it is renewed in this tab about every 20 minutes. Log out ends the login and
  its permissions with EVE, so Threat Vector leaves your list of apps on EVE's site.
- **EVE standings in use:** they decide in the System Analyzer, Intel, the Fleet tab and the Pilot Analyzer.

## Intel

- **Start:** in EVE, Settings → Chat → Log Chat to File. On the page: choose the Chatlogs folder, tick your intel
  channels, then turn on the switch (amber while Intel is off). Intel settings hold the ranges, the time a report stays,
  the sounds and your own shorthands.
- **How a line is read:** systems, ship names (English or Chinese), counts (+5, x2) and words like clr and nv; the rest
  is looked up on ESI as pilot names and coloured by your Standings. One word typed by hand is a pilot only in the
  name's own capitals, and report words like linked, drag, hot or kill only when dragged in from chat. A word it can't
  place stays plain text, never guessed. A report about the ESS tags the system in Near You: white when someone is at
  it, red when they're linked to it; a bubble that isn't a gate camp is a tag too. A line whose only news is such a tag (a
  bubble, a camp or a gate, at the ESS, with no pilots: build queue 045) adds the tag to the system's row in Near You, or gives
  the system a row of its own showing the tag and who reported it: no hostile or neutral word, no alert, no ring on the map, and
  never a start of Paths to you; it never changes what a row was reported as. A bare wormhole line gets no row. When a line names two systems,
  they're placed where the line says they are ("on Y gate", "→ Y"), else in the one within range, else the nearer; the
  other shows as a note. The copy button on a line copies its shape, names replaced, to report a line read wrong.
- **Gates and camps:** a short name before "gate" ("T5Z gate") is read among the gates of the system the line is in. A
  report that places them on a gate and says camp, bubble, drag, smartbomb or that the gate is hot tags the system with
  a red Camp tag and the gate. Two kills at one gate in the time set, with no such report, tag it in orange (zKillboard
  places each kill at the nearest stargate). A grey tag is a gate named with no camp words. "toward you": that gate
  leads closer to you. Your own shorthands (word = system) go in Intel settings; 4 or more letters before a system's
  dash ("ymjg") read as that system when only one has them.
- **Kills:** while Intel is on, zKillboard's live feed of every kill (about 20 small requests a minute), kept within the
  Feed's kill range (10 jumps unless you change it), no NPC kills. A kill near you shows in Near You with who was there
  and alerts like a report within your alert range. A kill (or a badge in Near You) opens in the Fleet tab: the victim
  and who killed them; a badge for several kills lists them there to pick from, grouped into fleets: kills that share 2
  pilots (1 when a kill had only 1 or 2 attackers) are one fleet, the biggest first; victims never link kills. The line
  under the title says when a kill was last read.
- **Near You and alerts:** everyone and every ship reported in a system in the time set (15 minutes unless you change
  it), until someone reports it clear; hide friendlies, in Intel settings, leaves out systems with only friendlies. With sounds or notifications turned on in Intel settings (both start off), a
  hostile or neutral within your alert range plays a sound and notifies, once per system every 30 seconds; friendlies
  never alert. Two sounds: Near You (1 jump up to your alert range) and In system (your own system, kills too), each one
  of five or your own file (MP3, WAV or OGG, up to 1 MB, kept only in this browser, played at most 5 seconds), with one
  volume; ▶ Test plays it. The desktop notification stays silent when the page plays its sound. With the Feed's
  Distance set, a report beyond both it and your alert range stays out of Near You. The profile's Intel lamp shows "N
  near" or "In system" from any tab.
- **Map:** New Eden as EVE's own 2D map draws it: every system at CCP's flat-map place (the position the in-game 2D map
  uses), one scale across and down, opening centred on you with a typical stargate about 16 px long. Only the systems
  within the map's reach are nudged apart, to at least 12 px at that zoom, each staying close to its own place. Zoom out
  for the whole galaxy, in for the game's circles with each system's security (from a gate about 34 px long) and their
  names (from about 80 px); gates between two regions are dotted and region names are written in spaced capitals, yours
  in white. The bar at the bottom of the map picks the colours: Security status, Jumps from you (0 to 10 or more; grey
  with no gate route), Region (two regions joined by a gate never share a colour), Intel reports or Kills from Intel (the
  rest dimmed), Paths to you (below) or Wormholes; it opens on Security status every visit. A ring marks a system with a report: its colour is
  the standing (hostile red, neutral grey, friendly blue), its size the gang (solo, 2–10, 11 or more); ✕ counts its
  kills. Hover a system, or a row in Near You or the Feed, for its route to you; press it to keep the route (past the
  map's reach too). Drag or two
  fingers move it, the wheel or a pinch zooms it (over the map the wheel zooms instead of scrolling the page); on a
  phone, List | Map in Near You switches between the two. Near You's range (Intel settings): from your alert range to
  the Feed's kill range, alert + 5 unless you set it. Map: within, under the map: from Near You's range up to the Feed's
  largest kill range (30); it follows the Feed's range until you change it, and reports and names show only within it.
  Systems past Near You's range are faded, past the map's reach fainter still; past the Feed's range a system's kills
  aren't read. A route is the shortest one by stargates (one for each system,
  always the same); jump bridges, cynos, filaments and wormholes aren't in CCP's data.
- **Paths to you** (build queue 043): the bar's filter just before Wormholes. In place of the galaxy it draws the stargate routes
  to you from every system with hostiles, neutrals or kills inside your alert range (not Near You's range), as a tree: your
  system at the top, one row per jump. Every shortest route counts, so a system reached two equally short ways has both
  gates; a system on several routes is drawn once, and a gate's line is thicker where more pilots come through it, with an
  arrow toward you. Under each name: the count, the ships (or "hostiles" / "neutrals") and how long ago; then Camp, ESS and
  kills, the same rules as Near You's tags (the gate, who and the ISK in their hover), and since build queue 045 Bubble and a
  short WH / DRIFTER badge (a wormhole Intel read within "forget reports after"); a tag never adds a system to the tree. No security number: the name's
  colour carries it, its hover the number. Hover or press a system to light its routes, toward you and back to what feeds
  it; press it again, press your system or Esc to clear. Drag or two fingers move it, the wheel or a pinch zooms it;
  + / − / Fit at its top right. It's built from what Intel already has, nothing is asked of anyone, and it's drawn again
  only when what it shows changes.
- **Routes and setting your destination** (build queue 047): the map's drawn route and its tooltip's route list follow Threat
  Vector's route, from Intel settings → Routes; every jump count (Near You, alerts, the Feed, Jumps from you, Paths to you, the
  tooltip's "N jumps") stays the shortest by stargate. The route passes the fewest flagged systems it can, however long the detour,
  then costs what EVE's own route would (CCP's route guide, developers.eveonline.com/docs/guides/route-calculation/: Prefer shorter 1
  a jump; Prefer safer and Prefer less secure with p = exp(0.15 × the security penalty): into null sec 2p, into low sec p or 0.90,
  into high sec 0.90 or p), then has the fewest jumps. Null, low and high come from CCP's unrounded security (0.0 or below, below
  0.45, the rest), not the map's rounded number: 19 systems show 0.45 and are low sec. Compared with ESI's own route on 40 routes at
  the build (every one the cheapest by this rule). Flagged: a gate camp, a bubble, hostiles, neutrals, a kill or the ESS reported
  within "forget reports after" (each a setting), and your avoid list; the destination and your own system never count; a clear
  report flags nothing. Send destination to EVE (EVE's route) sends EVE the destination only, and EVE plans the route with your game's
  settings (jump bridges and your game's avoidance list included); Send destination to EVE (Threat Vector's route) sends every system as a
  waypoint, in order, one at a time, so EVE flies that route (with Disable Autopilot at Each Waypoint on, it stops at each). Both use
  your EVE login with the Waypoints permission; a send that fails stops there, and the waypoints already sent stay in EVE. EVE
  answers OK while your character is logged off but the game drops the destination, so with Show when I'm online in EVE saying
  you're logged off nothing is sent (Retry sends, in case that is a minute behind), and otherwise the note says to send it in the game.
  EVE doesn't share your game's avoidance list with apps, so Threat Vector's route can pass through a system on it (as a waypoint the
  game keeps it); put those systems on Threat Vector's avoid list too.
- **Wormholes** (build queue 040): a line that says wh, wormhole or drifter (intel words, never looked up as pilots) with a
  system keeps that system as a wormhole (a Drifter one with drifter), with the line's time and who sent it, in this
  browser only (localStorage `tvWormholes`; nothing is sent anywhere), for 24 hours unless you change "keep wormhole
  reports for" in Intel settings (1 to 48 hours; anything older than 48 hours is deleted). The map's last filter,
  Wormholes, colours every kept one anywhere in New Eden, past the map's reach too, and dims the rest; on the other filters
  a wormhole Intel read within "forget reports after" and the map's reach gets two thin rings and "WH · age", like a
  report. Feed rows and Near You show a Wormhole (or Drifter WH) badge. On the Wormholes filter (build queue 045) the rest
  steps back: other reports' rings at 20% with no glow, the alert range's wash lighter, labels only for wormholes and you
  (a wormhole's tag a filled pill, its name where it fits, never over another label); each wormhole a filled disc with a
  ring (zoomed in, a glowing ring around its circle), a Drifter hot pink with its outer ring dashed; one reported in the last
  30 minutes sends out a slow ring every 2.2 seconds (none when the device asks for less motion); and "N wormholes ›" at the
  bottom left moves the view to each in turn, nearest by gate jumps first, then newest. The list button beside Wormholes adds a system by
  hand (kept the set hours from then; shown only on the filter and in the list) or removes one; a removed one isn't
  brought back by the same line read again, only by a newer one.
- **Signature IDs and hole details** (build queue 044): in a wormhole line only, a reader runs before the system and pilot
  readers and takes what describes the hole, so none of it is looked up as a pilot or guessed as a system ("class",
  "then", "1-3" in "class 1-3"). A word that is exactly a system's name stays a system, and so does a part like "ZXB-4"
  when a system's name starts with it. It takes:
  - **Signature IDs:** whole ("RZL-429", "rzl429") or a part ("RZL-4", "RZL-"). Three bare letters count only right after
    wh / wormhole / drifter / sig / signature, or beside a wormhole type, and never when they are an intel, filler or ship
    word or a dragged-in name (so a three-letter pilot right after "wh" reads as an ID: the owner accepted that).
  - **The type** ("Z971") and where it leads: from CCP's data, each wormhole type's target system class
    (`wormholeTargetSystemClass`), written into the page by `tools/gen_wh_table.py`. K162 is the far end of a hole opened
    from the other side ("exit"); a type whose class CCP's data doesn't fix shows "?". A type goes with the ID written
    beside it, else with the only ID in the line.
  - **The class** ("class 1-3", "c5").
  - **Life, mass and size**, only when said plainly, in the game's own steps: life under a day, under 4 hours (EOL) or
    under an hour; mass over 50%, under 50% or under 10% (critical); size small, medium, large or XL. "Fresh", "new",
    "frig" or "caps" on their own are left out, because they can mean a ship in the line rather than the hole. Two steps of
    one kind in a line: the worse.

  Each system keeps up to 8 IDs, newest first, each with its type, class, details, Drifter mark and who reported it. An
  ID past "keep wormhole reports for" is dropped. A part joins the kept ID it starts (and a whole ID its part); a part that
  fits two kept IDs is kept on its own. A later line about one ID ("RZL crit") changes only what it says. Drifter is per
  hole: every ID in a line with "drifter" is a Drifter hole. The system stays a Drifter one while any Drifter hole, or a
  Drifter report with no ID, is kept, and the map's label counts them ("DRIFTER ×2"). A system with both kinds gets split
  rings, and on the Wormholes filter its disc (zoomed out) or glowing ring (zoomed in) is split too, with its own report's ring
  moved outside the wormhole's marks so the two don't sit on each other. The tags show on the Feed's line, on Near You's row (Intel reports only), in the list and on the map's label.
  In the list, × beside an ID removes it, and Drifter with it. The ID keeps a removal mark (for 48 hours), so the same line
  read again, an older one, or another line in the same second can't bring it back; a newer report does. Each system also
  keeps its last 10 lines as typed (for the newest 100 systems), with who sent them and what each set, under a chevron in
  its row. The Add form takes every property; adding one by hand leaves an "Added by you" line. The same words arriving again
  later are one line with a count ("×2").
- **Export and Import** (build queue 046): two buttons under the list's Add form. **Export** shows your list as text (JSON), selected,
  with a Copy button; the page sends it nowhere. It holds only the systems inside "keep wormhole reports for", their IDs and details,
  and their lines as typed, with every name replaced by "<a pilot>": each line is read again by Intel's own reader, and only the
  words it places (systems, ships, counts, keywords, signature IDs, types, the words describing the hole) are kept; anything else,
  a pilot, a corporation or a ticker, becomes "<a pilot>". The reporter is never written, nor your removals or settings. Lines you
  added by hand travel as what they set. **Import** reads someone's export (this tool's format only, at most 256 KB; systems on the
  map with matching names, times inside the last 48 hours, IDs, types and details the page knows) and shows what it would add before
  anything changes; "Add to my list" merges it. Two lines are the same report when their words match once names are replaced, so the
  same report from both lists is one line (yours kept, with its names). Details are worked out again from all of a system's lines:
  your own lines decide as Intel does (the newest that says it); a shared report fills in what yours don't say and replaces an older
  report, but never a value you set by hand: a newer shared report that disagrees shows as "!" beside the ID. A value with no line
  behind it is kept. A system or ID you removed comes back only with a report newer than the removal. A line that still decides a
  detail is kept when a system has more than 10. Imported holes count like Intel's reports (their hover says "from a shared list").
- **Your system and jumps:** your system comes from your character's Local log, or from EVE with Use my game location
  on, whichever is newer. Jumps are gate jumps from EVE's published stargate data (no jump bridges or wormholes); the
  table is checked against each new EVE build every day.
- **Buttons:** a pilot's name opens them in the Pilot Analyzer, in their ship when the line says it. Press a system,
  corporation, alliance or ship to show only it in the Feed; the chips under the filters say what's on (× removes one;
  press it again for everything). Near You itself is never filtered; beside the map it scrolls, and the count below says
  how many systems are out of view. A kill badge there shows its kills' value together. The radar icon beside a system
  in Near You sends its pilots and ships to the System Analyzer; Restore my paste puts yours back.
- **Privacy, the folder and tabs:** nothing from your logs leaves the browser except the words looked up on ESI, and
  nothing is kept after you close the page. Chrome or Edge read the folder once you allow it, and ask again on a later
  visit: Allow this time (this visit only; Chrome may also take it back while the tab is in the background, which stops
  Intel reading), Allow on every visit (no more questions) or Don't allow. Until you answer, step 1 shows Allow reading
  and steps 2 and 3 wait for the folder. The logs are read every 2 seconds, also in a hidden tab. Intel runs in one tab
  at a time: another tab shows it's on and can take it over with Move Intel here.

## Wormholes (the Wormholes tab)

- **What's recorded** (v2026.11.14.1, build queue 048): each reading of your system, from your Local log ("Channel changed to Local") or from EVE
  with Use my game location on, the newer winning as in Intel. A change of system with a wormhole system on either side is a connection, from the
  system you were last in: the game never says which hole you took, but J-space has no gates. A change where EVE's answer says you're docked
  (a jump clone, a pod death) adds the system and no connection; the Local log can't tell, so such a jump read only from the log draws a
  connection you can delete. Two hole jumps between two readings show as one connection.
- **Systems:** CCP's static data (the SDE): every system with an ID from 31,000,000 to 31,999,999, its class from the system, else its
  constellation, else its region (only the five Drifter systems carry their own), its effect from its secondary sun's effect beacon
  (Black Hole, Cataclysmic Variable, Magnetar, Pulsar, Red Giant, Wolf-Rayet). Statics aren't in the SDE: you type them, and each is coloured
  by where its type leads (the same table as Intel's wormhole reports).
- **Intel in a hole:** jumps are counted from your chain's nearest k-space system (where you came in), since there are no gates to count from.
- **Kept:** in this browser only (tvWhChain), until you remove it; nothing expires.
