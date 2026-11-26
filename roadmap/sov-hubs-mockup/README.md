# Mockup: the Intel map's "Sov hubs" Only filter (sov fights coming up, hubs vulnerable)

Made 2026-11-21 by the research session from `main` e1ebe17 (v2026.11.21.1), for the plan `roadmap/sov-hubs-plan.md` (planning list E2; the owner 2026-11-21: [stated] "One filter, two kinds (Recommended)", "24 h fights, now for hubs (Recommended)", "Fight tags only, filter on (Recommended)", "Every 2 min, raise cap (Recommended)"). Sent to the owner as `sov_hubs_mockup.html`; built as build queue 068.

**Rebuilt 2026-11-25** by the build session for the archive (`Claude outputs/sov_hubs_mockup.html`) on `main` b1b9714 (v2026.11.25.1), the page before 068: hook 4 of `build_hb.py` follows 065's `IT_MP_KEYS` (itMpOpen no longer names Security range and Within N jumps itself); the rest is as made. Build it from a page before 068 only: on 068's page the filter exists already and the mockup would add it twice.

## Where the build differs (the build review, the plan's section 10)

- **The icon:** the mockup's flag was Sov holder's (065, built after the mockup); the build draws a hub of its own (B3). The owner also asked for the Wormholes filter's icon to be the game's wormhole shape.
- **Fights are read whichever kind is ticked**, and the match's key holds the minute (B2), so windows opening and fights entering their hours show within about a minute.
- **The window is said once** when Sov holder's colour is on too (B4).
- **Reads with Intel stopped:** none (B1); the Only line's "ESI HH:MM" says how old the list is.
- The panel's rows are the page's own `.it-mp-row` (a tick and its stepper side by side, wrapping), not the mockup's `mk-hk` rules.

## What it shows

- **A new Only filter "Sov hubs"**, right after Sov upgrades, with its own icon (a flag) and settings button.
- **Its settings** (058's panel, as Security range's): two kinds, each with a tick and an hours stepper: **Fight coming up** within [24] h (0–48; a started fight always counts) and **Vulnerable** opens [now] h (0 = now, up to 24); a short note; the panel's match count. Switched on the first time, the settings open.
- **What matches:** any ticked kind. A fight starting within its hours or already under way; a hub whose window is open now or opens within its hours. A hub in a fight has no window (as ESI).
- **The hover:** "Sov fight: hub defense, starts 21:55 EVE (in 6 h 05 min); defending Mockup Holdings [MKHD], score 60 / 40; nodes anywhere in this constellation" (or "under way since … (25 min)"), plus "Hub: no vulnerability window (in a fight)"; "Hub vulnerable 16:00–20:00 EVE (now, 1 h 20 min left)" or "(opens in 2 h 10 min)".
- **Tags:** "SOV 21:55" beside each fight in the window ("SOV now" once started), only while the filter is on and Fight coming up is ticked. A reported system's tag joins its report label; others get name + tag where there's room. Vulnerable hubs: hover only.
- **The Only line:** "a sov fight within 24 h (5) or a hub vulnerable now (413) · ESI 15:49"; "no data yet" before a read; "no kind ticked" with neither.
- **Kept:** `tvMapStack` gains `only.hub`, `hub: {fight, fightH, vuln, vulnH}` and `seen.hub`; a stack saved before this reads with Sov hubs off and the defaults; bad hours fall back.
- MOCKUP box: Defaults, Fights only, Fights 48 h, Vulnerable now, Vulnerable 4 h, Zoomed out, No data yet, Off.

## Made up

Six sov fights around C-J6MT (78-0R6 in 1 h 10, SHBF-V started 25 min ago, MSG-BZ in 6 h, EUU-4N in 3 h 20, 0UBC-R in 21 h 40, RERZ-L in 30 h, past the default window), three invented alliances ("Mockup Coalition", "Mockup Raiders", "Mockup Holdings"), and a 3- or 4-hour window for every nullsec system on the map, its start hour from the system's ID (about 1 in 8 vulnerable at once; live ESI had 376 of 2,706 on 2026-11-21). Times are relative to when the page opens. No ESI read.

## Shortcuts the build must not copy

- Five hooks (`build_hb.py` PATCH, each found once): the `hub` test in `itMapMatch`; the hover lines before the sov lines; the fight tags beside the map's labels (`__MKlab`) and in a report's label (`__MKftag`); `itMpOpen` letting `hub` in. A build writes each in place.
- `itMapStackBlank`, `itMapStackRead`, `itMapStKey`, `itMapOnlyHtml`, `itMpBodyHtml`, `itMpMake`, `itMapFilterSet` are wrapped; `IT_MAP_ONLY` / `IT_MAP_FILTERS` / `IT_MAP_PANEL_BTN` / `RS` are added to at run time. A build changes them in place.
- The data is made up in `MKH.build`; the build reads `/sovereignty/campaigns` through 065's reader and takes the windows from 065's `sov` store.
- **Found in the mockup:** the match's key must hold whether data is there (not only the read time), or a "no data" match outlives the data's return (the first try did; checked in `test_hb.py`).
- The tag reads "SOV 21:55", not the plan's "⚔ 21:55": the crossed swords aren't in every font, and on a canvas without them they fell back to a mark like the kill count's ✕ (seen in the sandbox's Chrome). Plan Q7, answered 2026-11-21: [stated] ""SOV 19:45" (Recommended)" (the build uses it as the mockup does).
- Two lines of mockup CSS (the kind rows); the MOCKUP scenes reset the filters by hand.

## Files

- `build_hb.py <repo>/index.html out.html`: the real page with made-up Intel; needs `mock.js` beside it (the repo's `roadmap/paths-to-you-mockup/mock.js`, unchanged, not copied here).
- `proto_hb.js`: the filter, the made-up data, the MOCKUP box. `boot_hb.js`: opens Intel, starts on Sov hubs with its defaults.
- `test_hb.py out.html shots/`: 83 checks at 1440 and 390 px (the filter, its place, button and defaults; the panel; the match equals the plan's rule worked out apart, your system kept; a started fight and one in 21 h match, one in 30 h doesn't; the Only line; the four hover cases; tags in and out of the window, "now", the EVE time; unticking Vulnerable; the stepper; 48 h, 0 h; nothing ticked; Vulnerable within 4 h; "now" shown for 0; no data, and data back worked out again; saved, bad values, an older stack; first switch-on opens the settings, off closes them; the panel fits; 24 px ticks on a phone; no sideways scroll; no page errors). All 83 passed 2026-11-21.
- check_pii (without the names list) on the mockup and scripts: only the page's own CCP login button image; names read by hand: invented only.

Run: `cp ../paths-to-you-mockup/mock.js . && python3 -I build_hb.py <repo>/index.html sov_hubs_mockup.html && python3 -I test_hb.py sov_hubs_mockup.html shots`
