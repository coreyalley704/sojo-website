"""
Planning Center reader for the Sunday page.

One job: pull the facts SOJO already keeps in Planning Center so nobody has to
retype them into a bulletin every week.

Auth is a Personal Access Token (App ID + Secret) over HTTP Basic. That token
can read every donation record the church has, so it lives in GitHub Actions
secrets and nowhere else. It must never appear in this repo, which is public.

Every reader here is defensive on purpose. A weekly build that dies because one
endpoint changed shape is worse than a build that ships last week's number and
says so in the log. Each function returns None on failure and the caller falls
back to whatever is in content.json.
"""

import base64
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.planningcenteronline.com"
UA = "sojo-sunday-page/1.0 (+https://sojo.church/sunday/)"
TIMEOUT = 30

# Sunday Services in SOJO's Planning Center. If the service type is ever
# renamed or rebuilt, this is the one number to change.
SERVICE_TYPE_ID = "1096515"


class PCOError(RuntimeError):
    pass


def _auth_header():
    app_id = os.environ.get("PCO_APP_ID", "").strip()
    secret = os.environ.get("PCO_SECRET", "").strip()
    if not app_id or not secret:
        raise PCOError(
            "PCO_APP_ID and PCO_SECRET are not set. Locally, export them in your "
            "shell. In GitHub, they are repository secrets. Never commit them."
        )
    raw = f"{app_id}:{secret}".encode()
    return "Basic " + base64.b64encode(raw).decode()


def get(path, params=None, _tries=3):
    """One GET against the PCO API. Retries on 429 and 5xx, then gives up."""
    url = API + path
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={
        "Authorization": _auth_header(),
        "User-Agent": UA,
        "Accept": "application/json",
    })
    for attempt in range(_tries):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            # 429 is PCO's rate limit and it tells you how long to wait.
            if e.code == 429 and attempt < _tries - 1:
                wait = int(e.headers.get("Retry-After", "3"))
                time.sleep(min(wait, 20))
                continue
            if 500 <= e.code < 600 and attempt < _tries - 1:
                time.sleep(2 ** attempt)
                continue
            body = e.read().decode("utf-8", "replace")[:400]
            raise PCOError(f"{e.code} on {path} — {body}") from None
        except urllib.error.URLError as e:
            if attempt < _tries - 1:
                time.sleep(2 ** attempt)
                continue
            raise PCOError(f"could not reach Planning Center: {e.reason}") from None
    raise PCOError(f"gave up on {path}")


def paged(path, params=None, cap=2000):
    """Walk every page of a collection. `cap` is a guard against a runaway loop."""
    params = dict(params or {})
    params.setdefault("per_page", 100)
    out, seen = [], 0
    while True:
        page = get(path, params)
        rows = page.get("data", [])
        out.extend(rows)
        seen += len(rows)
        token = page.get("meta", {}).get("next", {}).get("offset")
        if token is None or not rows or seen >= cap:
            return out
        params["offset"] = token


# ---------------------------------------------------------------- dates

def coming_sunday(today=None):
    """The Sunday this build is for. On a Sunday, that is today."""
    d = today or dt.date.today()
    return d + dt.timedelta(days=(6 - d.weekday()) % 7)


def last_complete_week(sunday):
    """
    Monday–Sunday, the last full week before the service.

    PC's giving week runs Monday through Sunday. For a page published on Sunday
    the 4th, "last week" is Mon the 21st through Sun the 27th — the most recent
    week that actually finished.
    """
    end = sunday - dt.timedelta(days=7)          # the previous Sunday
    start = end - dt.timedelta(days=6)           # that week's Monday
    return start, end


# ---------------------------------------------------------------- 1. Services

def service_plan(sunday):
    """
    The order of service for `sunday`, congregation-facing only.

    `service_position` is the filter that matters. PCO marks production cues
    "pre" and "post" — countdowns, announcement loops, green room notes. Only
    "during" items belong in front of a guest.
    """
    plans = get(
        f"/services/v2/service_types/{SERVICE_TYPE_ID}/plans",
        {"filter": "future", "order": "sort_date", "per_page": 8,
         "fields[Plan]": "dates,sort_date,series_title,title"},
    ).get("data", [])

    want = sunday.isoformat()
    plan = next((p for p in plans
                 if (p["attributes"].get("sort_date") or "").startswith(want)), None)
    if plan is None:
        return None

    items = paged(
        f"/services/v2/service_types/{SERVICE_TYPE_ID}/plans/{plan['id']}/items",
        {"include": "song"},
    )

    flow, songs = [], []
    for it in items:
        a = it["attributes"]
        if a.get("service_position") != "during":
            continue
        if a.get("item_type") == "header":
            continue
        entry = {
            "title": (a.get("title") or "").strip(),
            "type": a.get("item_type"),
            "note": (a.get("description") or "").strip(),
            # Length in seconds. This is what makes chapter markers possible on
            # the live page — the plan already knows how long everything runs.
            "length": int(a.get("length") or 0),
        }
        flow.append(entry)
        if a.get("item_type") == "song":
            songs.append(entry["title"])

    return {
        "plan_id": plan["id"],
        "series": plan["attributes"].get("series_title"),
        "title": plan["attributes"].get("title"),
        "flow": flow,
        "songs": songs,
    }


# ---------------------------------------------------------------- 2. Giving

def _donation_total(start, end):
    """
    Sum of donations received in [start, end], inclusive, in cents.

    Sums the rows rather than trusting a totals parameter, because the rows are
    the thing we can verify. Refunded and failed gifts are excluded; **pending
    ACH is included**, which is what the Giving dashboard shows. That difference
    is the whole reason last week's number once read $9,831 here and $9,712 in
    the office: filtering to settled-only silently drops every ACH gift that has
    not cleared, and ACH takes days.
    """
    rows = paged("/giving/v2/donations", {
        "where[received_at][gte]": start.isoformat(),
        "where[received_at][lte]": end.isoformat(),
        "fields[Donation]": "amount_cents,received_at,refunded,payment_status",
    })
    cents, count = 0, 0
    for d in rows:
        a = d["attributes"]
        if a.get("refunded"):
            continue
        if a.get("payment_status") == "failed":
            continue
        cents += int(a.get("amount_cents") or 0)
        count += 1
    return cents, count


def giving(sunday):
    wk_start, wk_end = last_complete_week(sunday)
    week_cents, week_n = _donation_total(wk_start, wk_end)

    # The calendar month that just finished, or the current one if the service
    # falls late enough in a month for that to be the more useful number.
    m_start = wk_end.replace(day=1)
    nxt = (m_start + dt.timedelta(days=32)).replace(day=1)
    m_end = min(nxt - dt.timedelta(days=1), sunday)
    month_cents, month_n = _donation_total(m_start, m_end)

    def money(c):
        return "${:,}".format(round(c / 100))

    return {
        "week_amount": money(week_cents),
        "week_gifts": week_n,
        "week_start": wk_start.isoformat(),
        "week_end": wk_end.isoformat(),
        "month_amount": money(month_cents),
        "month_gifts": month_n,
        "month_name": m_start.strftime("%B"),
        "asof": "Week of {} – {} · {} gifts in {}".format(
            wk_start.strftime("%b %-d"), wk_end.strftime("%b %-d"),
            month_n, m_start.strftime("%B")),
    }


# ---------------------------------------------------------------- 3. Sign-ups

def signups():
    """
    Open registrations, keyed by name so content.json can point at one by name
    instead of an ID nobody can read.

    Closed and archived sign-ups are dropped. That matters: the Candy Crawl
    sign-up was deleted out of Planning Center in September and the live page
    kept pointing at it for days. Anything this function does not return should
    not be linked.
    """
    rows = paged("/registrations/v2/signups",
                 {"filter": "unarchived", "include": "next_signup_time"})
    included = {}
    out = {}
    for r in rows:
        a = r["attributes"]
        if a.get("archived") or a.get("closed"):
            continue
        name = (a.get("name") or "").strip()
        out[name.lower()] = {
            "id": r["id"],
            "name": name,
            "url": a.get("new_registration_url"),
            "open": bool(a.get("open")),
        }
    return out


def signup_times(ids):
    """Next occurrence for specific sign-ups, so the page can print a real date."""
    times = {}
    for sid in ids:
        try:
            data = get(f"/registrations/v2/signups/{sid}",
                       {"include": "next_signup_time"})
        except PCOError:
            continue
        for inc in data.get("included", []):
            if inc.get("type") == "SignupTime":
                times[sid] = inc["attributes"].get("starts_at")
    return times


# ---------------------------------------------------------------- 4. Calendar

def calendar_week(sunday, days=9):
    """
    What is on the church calendar between this Sunday and the next.

    Used for the weekly rhythm block and to catch the one-offs — a youth night
    at a ballpark instead of the usual room, a prayer night that moved.
    """
    end = sunday + dt.timedelta(days=days)
    rows = paged("/calendar/v2/event_instances", {
        "where[starts_at][gte]": sunday.isoformat(),
        "where[starts_at][lte]": end.isoformat(),
        "order": "starts_at",
        "include": "event",
    })
    out = []
    for r in rows:
        a = r["attributes"]
        out.append({
            "name": (a.get("name") or "").strip(),
            "starts_at": a.get("starts_at"),
            "ends_at": a.get("ends_at"),
            "location": a.get("location"),
            "url": a.get("church_center_url"),
        })
    return out


# ---------------------------------------------------------------- 5. Groups

def groups(limit=6):
    """Groups with room in them, for the 'find your people' list."""
    rows = paged("/groups/v2/groups", {"filter": "active", "order": "name"})
    out = []
    for g in rows:
        a = g["attributes"]
        if a.get("archived_at"):
            continue
        out.append({
            "name": (a.get("name") or "").strip(),
            "schedule": (a.get("schedule") or "").strip(),
            "url": a.get("public_church_center_web_url") or a.get("church_center_web_url"),
        })
    return [g for g in out if g["url"]][:limit]


# ---------------------------------------------------------------- 6. Forms

def forms():
    """People Forms, by name — the connect card and anything else worth linking."""
    rows = paged("/people/v2/forms", {"order": "name"})
    out = {}
    for f in rows:
        a = f["attributes"]
        if a.get("archived") or not a.get("active", True):
            continue
        name = (a.get("name") or "").strip()
        out[name.lower()] = {
            "id": f["id"],
            "name": name,
            "url": a.get("public_url") or a.get("url"),
        }
    return out


# ---------------------------------------------------------------- check

READERS = [
    ("Services",      lambda s: service_plan(s)),
    ("Giving",        lambda s: giving(s)),
    ("Sign-ups",      lambda s: signups()),
    ("Calendar",      lambda s: calendar_week(s)),
    ("Groups",        lambda s: groups()),
    ("Forms",         lambda s: forms()),
]


def check(sunday=None):
    """
    Hit every endpoint once and report. Run this first, and any time a build
    looks wrong — it tells you which of the six is the problem in one pass.
    """
    sunday = sunday or coming_sunday()
    print(f"Planning Center check — service date {sunday:%A, %B %-d, %Y}\n")
    bad = 0
    for name, fn in READERS:
        try:
            got = fn(sunday)
        except PCOError as e:
            print(f"  {name:<10} FAILED   {e}")
            bad += 1
            continue
        if got is None:
            print(f"  {name:<10} empty    nothing found for this date")
            bad += 1
            continue
        n = len(got) if isinstance(got, (list, dict)) else 1
        print(f"  {name:<10} ok       {n} item(s)")
        if name == "Giving":
            print(f"             {got['week_amount']} last week · "
                  f"{got['month_amount']} in {got['month_name']}")
        if name == "Services":
            print(f"             {len(got['flow'])} congregation-facing items, "
                  f"{len(got['songs'])} songs")
    print()
    if bad:
        print(f"{bad} of {len(READERS)} need attention. The build will fall back to "
              f"content.json for those.")
    else:
        print("All six reading cleanly.")
    return bad


if __name__ == "__main__":
    day = None
    if len(sys.argv) > 1:
        day = dt.date.fromisoformat(sys.argv[1])
    sys.exit(1 if check(day) else 0)
