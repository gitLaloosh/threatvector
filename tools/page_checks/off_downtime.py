"""Keep EVE's daily downtime out of a page check's way (page unchanged, the owner 2026-11-15: "go with option 1"; LESSON #168).

The page counts 11:00-12:00 UTC as EVE's daily downtime: from 10:56 the strip says it starts soon, and in that hour a failing ESI is
called the downtime ("EVE's daily downtime (11:00 UTC)") instead of "EVE's ESI is down". A check that reads the real clock passed or
failed by the time of day it ran. A check whose results the strip or ESI's words can change opens a copy of the page whose downtime
hour is 12 hours from now: the page's own code runs, only the hour moves, so nothing about the downtime shows while it runs (a check
takes minutes). Tests of the downtime itself set the page's clock near DT_HOUR (outage_check).

    from off_downtime import off_downtime, off_downtime_copy
    text, hour = off_downtime(page_text)      # the text with the hour moved, and the hour
    path = off_downtime_copy('/path/index.html')   # the same, written next to nothing of the repo's (a temp folder)
"""
import os, tempfile, time

DT_REAL = 'const SYS_DT_HOUR = 11,'   # the page's line; a check fails loudly if it changes (a moved hour must be moved here too)


def dt_hour(now=None):
    """12 hours from the current UTC hour, never 0: the page finds the hour on the same UTC day, so 4 minutes before 00:00 would be the
    day before (no "starts soon" to test). 1 instead keeps it 13 hours away. Either way the downtime and the 4 minutes before it are at
    least 11 hours from the run."""
    h = (time.gmtime(now if now is not None else time.time()).tm_hour + 12) % 24
    return h or 1


def off_downtime(text, hour=None):
    if text.count(DT_REAL) != 1:
        raise SystemExit(f'FAIL off_downtime: the page has no single {DT_REAL!r} (the downtime hour moved: update off_downtime.py)\nFAILURES: 1')
    h = dt_hour() if hour is None else hour
    return text.replace(DT_REAL, f'const SYS_DT_HOUR = {h},'), h


def off_downtime_copy(path, hour=None):
    text, _ = off_downtime(open(path, encoding='utf-8').read(), hour)
    out = os.path.join(tempfile.mkdtemp(prefix='offdt'), 'index.html')
    open(out, 'w', encoding='utf-8').write(text)
    return out
