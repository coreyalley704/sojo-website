#!/usr/bin/env python3
"""
Build the Sunday page.

    python3 sunday/build_sunday.py            # this coming Sunday
    python3 sunday/build_sunday.py 2026-10-04 # a specific service date
    python3 sunday/build_sunday.py --check    # test all six PCO reads, build nothing
    python3 sunday/build_sunday.py --offline  # build from content.json alone

Two inputs, one output.

    Planning Center  supplies the facts    — order of service, songs, giving
                                             numbers, sign-up links and dates,
                                             the weekly rhythm, groups, forms
    content.json     supplies the voice    — headline, lede, the pastor's notes,
                                             note prompts, invite text, artwork

Writes:
    standalone/sunday/index.html                 the live page
    standalone/sunday/archive/YYYY-MM-DD.html    that week, kept forever

`standalone/` is the source of truth. build.py's copy_standalone() copies it
into docs/ on every site build, which is why edits belong here and never in
docs/ directly.
"""

import datetime as dt
import html
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "standalone", "sunday")
ARCHIVE = os.path.join(OUT, "archive")
CONTENT = os.path.join(HERE, "content.json")
TEMPLATE = os.path.join(HERE, "template.html")
LIVE_TEMPLATE = os.path.join(HERE, "live_template.html")
LIVE_OUT = os.path.join(ROOT, "standalone", "live")

sys.path.insert(0, HERE)
import pco  # noqa: E402


# ---------------------------------------------------------------- helpers

def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def wrap(body, title, description, icon="sojo-mark.png"):
    """
    Put the page inside a real HTML document.

    The templates start at <title> because they are fragments. Without this
    they ship with no doctype, no <head>, no charset and — the one that
    actually breaks things — no viewport meta. A page with no viewport meta
    is laid out by phones at 980px and then scaled down to fit, which makes
    every word small and the whole thing feel like a desktop site squeezed
    onto a phone. For a page whose entire job is to be read off a phone in a
    chair, that single missing line is the difference between working and not.
    """
    cut = body.index("<title>")
    head, rest = body[:cut], body[cut:]
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">\n"
        f"<meta name=\"description\" content=\"{esc(description)}\">\n"
        "<meta name=\"theme-color\" content=\"#302E2A\">\n"
        f"<link rel=\"icon\" href=\"{esc(icon)}\">\n"
        f"<link rel=\"apple-touch-icon\" href=\"{esc(icon)}\">\n"
        + head.strip() + ("\n" if head.strip() else "")
        + rest.strip()
        + "\n</body>\n</html>\n"
    ).replace("</style>\n", "</style>\n</head>\n<body>\n", 1)


def load_content():
    with open(CONTENT, encoding="utf-8") as f:
        return json.load(f)


def ampm(iso):
    """'2026-10-14T22:30:00Z' -> '6:30pm', in Concord's time."""
    if not iso:
        return ""
    t = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    # America/New_York without pulling in a dependency: EDT from the second
    # Sunday in March to the first Sunday in November, EST otherwise.
    y = t.year
    mar = dt.datetime(y, 3, 8, 7, tzinfo=dt.timezone.utc)
    dst_start = mar + dt.timedelta(days=(6 - mar.weekday()) % 7)
    nov = dt.datetime(y, 11, 1, 6, tzinfo=dt.timezone.utc)
    dst_end = nov + dt.timedelta(days=(6 - nov.weekday()) % 7)
    off = -4 if dst_start <= t < dst_end else -5
    local = t + dt.timedelta(hours=off)
    h = local.hour % 12 or 12
    m = f":{local.minute:02d}" if local.minute else ""
    return f"{h}{m}{'am' if local.hour < 12 else 'pm'}"


def nice_date(iso):
    if not iso:
        return ""
    d = dt.date.fromisoformat(iso[:10])
    return f"{d:%a, %b} {d.day}"


def resolve_link(spec, data):
    """
    Turn a content.json link into a real URL.

    A link is written as {"signup": "wednesday night bible study"} or
    {"form": "connect card"} or {"url": "https://..."}. Names are matched
    against what Planning Center actually returns, so a sign-up that has been
    closed or deleted resolves to nothing and the caller drops the link rather
    than shipping a dead one.
    """
    if not spec:
        return None
    if spec.get("url"):
        return spec["url"]
    if spec.get("signup"):
        hit = (data.get("signups") or {}).get(spec["signup"].strip().lower())
        return hit["url"] if hit else None
    if spec.get("form"):
        hit = (data.get("forms") or {}).get(spec["form"].strip().lower())
        return hit["url"] if hit else None
    return None


# ---------------------------------------------------------------- sections

def render_flow(content, data):
    """
    The order of service, compact.

    Planning Center gives the sequence. content.json's `flow` block can rename
    an item, add a one-line description, or hide it — because PCO item titles
    are written for the production team ("Flow Moment", "Giving Talk") and the
    congregation needs different words.
    """
    plan = data.get("service")
    cfg = content.get("flow", {})
    overrides = {k.lower(): v for k, v in cfg.get("items", {}).items()}
    hide = {h.lower() for h in cfg.get("hide", [])}

    rows = []
    if plan and plan.get("flow"):
        for item in plan["flow"]:
            key = item["title"].lower()
            if key in hide:
                continue
            o = overrides.get(key, {})
            rows.append({
                "title": o.get("title", item["title"]),
                "detail": o.get("detail", ""),
                "_src": item["title"],      # the Planning Center title, for "after"
            })
    else:
        rows = [dict(r, _src=r["title"]) for r in cfg.get("fallback", [])]

    # Anything the church does that the Services plan does not carry. Communion
    # on a first Sunday is the standing example: it is on the Calendar and it
    # happens, but it has never been an item in the plan. "after" names the row
    # it follows; leave it off and the item goes last.
    for ins in cfg.get("insert", []):
        row = {"title": ins["title"], "detail": ins.get("detail", ""),
               "_src": ins["title"]}
        after = (ins.get("after") or "").lower()
        # Match on either the Planning Center title or the renamed one, so
        # "after": "Christ Be Magnified" still works once that row is displayed
        # as "Response".
        at = next((i for i, r in enumerate(rows)
                   if after in (r["_src"].lower(), r["title"].lower())),
                  len(rows) - 1)
        rows.insert(at + 1, row)

    # Songs collapse into one line under whichever row asked for them.
    # {{songs}} is the worship set — everything sung before the message.
    # {{songs_after}} is the response. Lumping them together puts the closing
    # song in the opening set, which is wrong on the page and wrong in the room.
    songs_all = (plan or {}).get("songs") or []
    flow_titles = [i["title"].lower() for i in (plan or {}).get("flow", [])]
    song_titles = [i["title"] for i in (plan or {}).get("flow", [])
                   if i.get("type") == "song"]
    try:
        msg_at = flow_titles.index("message")
    except ValueError:
        msg_at = len(flow_titles)
    before, after_songs = [], []
    for i, item in enumerate((plan or {}).get("flow", [])):
        if item.get("type") != "song":
            continue
        (before if i < msg_at else after_songs).append(item["title"])

    subs = {
        "{{songs}}": " · ".join(before or songs_all),
        "{{songs_after}}": " · ".join(after_songs),
        "{{songs_all}}": " · ".join(songs_all),
    }
    for r in rows:
        if r.get("detail") in subs:
            r["detail"] = subs[r["detail"]]

    out = []
    for i, r in enumerate(rows, 1):
        d = (f'\n        <p class="d">{esc(r["detail"])}</p>'
             if r.get("detail") else "")
        out.append(
            f'      <div class="fl"><span class="n">{i:02d}</span><div>'
            f'<span class="t">{esc(r["title"])}</span>{d}</div></div>'
        )
    return "\n\n".join(out)


def render_giving(content, data):
    g = data.get("giving") or content.get("generosity", {}).get("fallback", {})
    ways = "\n".join(
        f'      <div><b>{esc(w["label"])}</b><span>{esc(w["text"])}</span></div>'
        for w in content.get("generosity", {}).get("ways", [])
    )
    return {
        "GIVING_WAYS": ways,
        "GIVING_WEEK": esc(g.get("week_amount", "")),
        "GIVING_MONTH": esc(g.get("month_amount", "")),
        "GIVING_MONTH_LABEL": esc(g.get("month_name", "This month")),
        "GIVING_ASOF": esc(g.get("asof", "")),
    }


ORDINAL = ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight"]


def render_follow(content):
    """
    The message outline, for somebody keeping their place during the sermon.

    This replaced the note-taking fields, which asked a person to type on a
    phone while being preached to — a thing almost nobody does. An outline
    asks nothing of them and still gives them somewhere to look. Each point
    is a heading, its references, and two lines; it is a handrail, not a
    transcript, and it should never be readable *instead of* listening.

    Returns three pieces so the template can place them, and empty strings on
    a week with no outline so the section collapses to its heading.
    """
    fa = content.get("follow_along") or {}
    pts = fa.get("points") or []
    if not pts:
        return "", "", ""
    rows = []
    for i, p in enumerate(pts):
        ref = p.get("refs", "")
        body = p.get("body", "")
        rows.append(
            '      <div class="fa-row">\n'
            '        <span class="n">{}</span>\n'
            '        <div>\n'
            '          <h3>{}</h3>\n'
            '{}'
            '{}'
            '        </div>\n'
            '      </div>'.format(
                esc(ORDINAL[i] if i < len(ORDINAL) else str(i + 1)),
                esc(p.get("title", "")),
                '          <span class="fa-ref">{}</span>\n'.format(esc(ref)) if ref else "",
                '          <p class="fa-b">{}</p>\n'.format(esc(body)) if body else "",
            ))
    points = '    <div class="fa">\n' + "\n".join(rows) + "\n    </div>"

    call = fa.get("call") or {}
    qs = call.get("questions") or []
    bits = ['      <p class="q">{}</p>'.format(esc(q)) for q in qs]
    if call.get("body"):
        bits.append('      <p>{}</p>'.format(esc(call["body"])))
    call_html = ""
    if bits:
        call_html = '    <div class="fa-call">\n' + "\n".join(bits) + "\n    </div>"
    if fa.get("refrain"):
        call_html += '\n    <p class="fa-refrain">{}</p>'.format(esc(fa["refrain"]))
    return points, call_html, esc(fa.get("lede", ""))


def render_study_guide(content, data):
    """
    The deeper-dive block under the note prompts.

    Some weeks carry a study guide and most will not, so this renders nothing
    at all when `study_guide` is absent. A Google Doc is linked by its export
    URL rather than its /edit URL: /edit asks a phone to open the Docs app and
    can land a guest on a sign-in screen, while /export?format=pdf hands them
    a file. Set `url` directly to override.
    """
    sg = content.get("study_guide") or {}
    url = (sg.get("url") or "").strip()
    doc = (sg.get("google_doc_id") or "").strip()
    if not url and doc:
        url = "https://docs.google.com/document/d/{}/export?format=pdf".format(doc)
    if not url:
        return ""
    title = sg.get("title") or "This week's study guide"
    body = sg.get("body") or ""
    label = sg.get("label") or "Download the study guide"
    return (
        '\n    <div class="guide">\n'
        '      <p class="eyebrow">Go Deeper</p>\n'
        '      <h3 class="display display-xs">{}</h3>\n'
        '      {}\n'
        '      <a class="link" href="{}">{} <span>&rarr;</span></a>\n'
        '    </div>'
    ).format(esc(title),
             "<p>{}</p>".format(esc(body)) if body else "",
             esc(url), esc(label))


def img_tag(cls, block):
    """
    An <img> only if there is actually an image.

    A week that has no artwork for a section used to ship <img src=""> , which
    a browser renders as a broken-image box with the alt text beside it — the
    one thing on the page that looks like a mistake rather than a choice. Some
    weeks simply have no art, and those weeks should just not have an image.
    """
    name = (block or {}).get("art") or ""
    if not name.strip():
        return ""
    return '<img class="{}" src="{}" alt="{}">'.format(
        cls, esc(name), esc((block or {}).get("art_alt", "")))


def render_announcements(content, data):
    """
    The What's Next tiles.

    A tile whose link cannot be resolved is dropped entirely, not rendered
    dead. A bulletin that sends someone to a 404 is worse than one that is a
    tile shorter.
    """
    out, dropped = [], []
    for a in content.get("announcements", []):
        url = resolve_link(a.get("link"), data)
        if not url:
            dropped.append(a.get("title", "?"))
            continue
        out.append(
            f'      <a href="{esc(url)}">\n'
            f'        <span class="when">{esc(a.get("when", ""))}</span>\n'
            f'        <h3>{esc(a.get("title", ""))}</h3>\n'
            f'        <p>{esc(a.get("body", ""))}</p>\n'
            f'      </a>'
        )
    return "\n".join(out), dropped


def render_rhythm(content, data):
    """The weekly rhythm. Hand-kept — it changes a few times a year, not weekly."""
    return "\n".join(
        f'      <div><b>{esc(r["day"])}</b><span>{esc(r["time"])}</span>'
        f'<em>{esc(r["what"])}</em></div>'
        for r in content.get("rhythm", [])
    )


def render_groups(content, data, limit=None):
    """
    Groups. Planning Center first, content.json as the fallback — a hand-written
    list here beats an empty section if the Groups read fails.
    """
    rows = data.get("groups") or content.get("groups", {}).get("fallback", [])
    if limit:
        rows = rows[:limit]
    out = []
    for g in rows:
        sched = g.get("schedule") or g.get("when", "")
        out.append(
            f'      <a class="pw" href="{esc(g["url"])}">\n'
            f'        <span class="stackt"><span class="pw-n">{esc(g["name"])}</span>'
            f'<span class="pw-d">{esc(sched)}</span></span>'
            f'<span class="pw-go">&rarr;</span></a>'
        )
    out.append(
        '      <a class="pw" href="https://sojo.churchcenter.com/groups">\n'
        '        <span class="stackt"><span class="pw-n">See all groups</span>'
        '<span class="pw-d">Recovery, prayer, journaling, families, and more</span></span>'
        '<span class="pw-go">&rarr;</span></a>'
    )
    return "\n".join(out)


def build_chapters(content, data):
    """
    Chapter markers for the live page, from the plan's own item lengths.

    Returns (html, json) — the clickable list and the data the page ticks
    through. Renamed and hidden items follow the same rules as the printed
    order, so the two pages never disagree about what Sunday looks like.

    These are estimates. The plan says the message runs forty minutes; the
    message runs as long as it runs. The page presents them as estimates.
    """
    plan = data.get("service")
    cfg = content.get("flow", {})
    overrides = {k.lower(): v for k, v in cfg.get("items", {}).items()}
    hide = {h.lower() for h in cfg.get("hide", [])}

    chapters, at = [], 0
    if plan and plan.get("flow"):
        for item in plan["flow"]:
            key = item["title"].lower()
            dur = int(item.get("length") or 0)
            if key in hide:
                at += dur          # hidden from the page, still takes up time
                continue
            o = overrides.get(key, {})
            chapters.append({
                "t": at,
                "title": o.get("title", item["title"]),
                "detail": o.get("detail", ""),
                "_src": item["title"],
            })
            at += dur
    else:
        for r in cfg.get("fallback", []):
            chapters.append({"t": at, "title": r["title"], "detail": r.get("detail", "")})
            at += 300

    # Items the plan does not carry, placed the same way the printed order
    # places them. They inherit the start time of the row they follow, since
    # the plan gives them no length of their own.
    for ins in cfg.get("insert", []):
        after = (ins.get("after") or "").lower()
        at_i = next((i for i, c in enumerate(chapters)
                     if after in (c["title"].lower(),
                                  c.get("_src", "").lower())), len(chapters) - 1)
        chapters.insert(at_i + 1, {
            "t": chapters[at_i]["t"] if chapters else 0,
            "title": ins["title"],
            "detail": ins.get("detail", ""),
        })

    # Songs, resolved the same way the printed order resolves them.
    songs_before, songs_after = [], []
    msg_at = next((i for i, it in enumerate((plan or {}).get("flow", []))
                   if it["title"].lower() == "message"), 10 ** 9)
    for i, it in enumerate((plan or {}).get("flow", [])):
        if it.get("type") == "song":
            (songs_before if i < msg_at else songs_after).append(it["title"])
    subs = {"{{songs}}": " · ".join(songs_before),
            "{{songs_after}}": " · ".join(songs_after),
            "{{songs_all}}": " · ".join(songs_before + songs_after)}
    for c in chapters:
        if c["detail"] in subs:
            c["detail"] = subs[c["detail"]]

    def mmss(s):
        return f"{s // 60}:{s % 60:02d}"

    rows = []
    for c in chapters:
        d = (f'\n        <span class="d">{esc(c["detail"])}</span>'
             if c["detail"] else "")
        rows.append(
            f'      <button class="ch" type="button" data-at="{c["t"]}">'
            f'<span class="at">{mmss(c["t"])}</span><span>'
            f'<span class="t">{esc(c["title"])}</span>{d}</span></button>'
        )

    total = at
    return "\n".join(rows), json.dumps(
        [{"t": c["t"], "title": c["title"]} for c in chapters],
        ensure_ascii=False), total


def render_buttons(content, data, which):
    """A call-to-action pair. A button whose link will not resolve is dropped."""
    out = []
    for b in content.get("buttons", {}).get(which, []):
        url = resolve_link(b.get("link"), data)
        if not url:
            continue
        out.append(f'      <a class="{esc(b.get("style", "btn"))}" '
                   f'href="{esc(url)}">{esc(b["label"])}</a>')
    return "\n".join(out)


def render_notes(content):
    out = []
    for i, q in enumerate(content.get("note_prompts", []), 1):
        rows = 2 if len(q) < 60 else 3
        out.append(
            f'      <div class="noteblock">\n'
            f'        <span class="note-q">{esc(q)}</span>\n'
            f'        <textarea id="note{i}" rows="{rows}" '
            f'placeholder="Start typing&hellip;"></textarea>\n'
            f'      </div>'
        )
    return "\n".join(out), len(content.get("note_prompts", []))


def render_pastor(content, data):
    out = []
    for n in content.get("pastor_notes", []):
        url = resolve_link(n.get("link"), data)
        link = ""
        if url and n.get("link", {}).get("label"):
            link = (f'\n        <a class="link" href="{esc(url)}">'
                    f'{esc(n["link"]["label"])} <span>&rarr;</span></a>')
        out.append(
            f'      <div class="row"><span class="num">&mdash;</span><div class="rt">\n'
            f'        <h3>{esc(n["title"])}</h3>\n'
            f'        <p style="color:var(--ink)">{esc(n["body"])}</p>{link}\n'
            f'      </div></div>'
        )
    return "\n".join(out)


# ---------------------------------------------------------------- build

def gather(sunday, offline=False):
    """Read all six Planning Center products. Never fatal — log and carry on."""
    data, notes = {}, []
    if offline:
        return data, ["offline: Planning Center not contacted"]

    for label, key, fn in [
        ("Services",  "service",  lambda: pco.service_plan(sunday)),
        ("Giving",    "giving",   lambda: pco.giving(sunday)),
        ("Sign-ups",  "signups",  pco.signups),
        ("Calendar",  "calendar", lambda: pco.calendar_week(sunday)),
        ("Groups",    "groups",   pco.groups),
        ("Forms",     "forms",    pco.forms),
    ]:
        try:
            got = fn()
            if got:
                data[key] = got
                notes.append(f"{label}: ok")
            else:
                notes.append(f"{label}: empty — using content.json")
        except Exception as e:                       # noqa: BLE001
            notes.append(f"{label}: FAILED ({e}) — using content.json")
    return data, notes


def build(sunday, offline=False):
    content = load_content()
    data, notes = gather(sunday, offline)

    with open(TEMPLATE, encoding="utf-8") as f:
        page = f.read()

    tiles, dropped = render_announcements(content, data)
    for d in dropped:
        notes.append(f"announcement dropped, link would not resolve: {d}")
    notes_html, note_count = render_notes(content)
    _follow = render_follow(content)   # (points, call, lede)

    hero = content.get("hero", {})
    invite = content.get("invite", {})
    swag = content.get("swag", {})

    fields = {
        "WEEK_ISO":        sunday.isoformat(),
        "WEEK_LONG":       f"{sunday:%B} {sunday.day}",
        "WEEK_SHORT":      f"{sunday:%B} {sunday.day}",
        "LABEL":           esc(content.get("label", "Sunday")),
        "HERO_EYEBROW":    esc(hero.get("eyebrow", "Welcome")),
        "HERO_HEADLINE":   hero.get("headline", ""),   # allows <span class="gold">
        "HERO_LEDE":       esc(hero.get("lede", "")),
        "HERO_ART_TAG":    img_tag("hero-art", hero),
        "HERO_ART":        esc(hero.get("art", "")),
        "HERO_ART_ALT":    esc(hero.get("art_alt", "")),
        "RUNTIME":         esc(content.get("runtime", "About 75 minutes")),
        "WELCOME_NOTE":    esc(content.get("welcome_note", "")),
        "FLOW":            render_flow(content, data),
        "FLOW_BUTTONS":    render_buttons(content, data, "flow"),
        "GROUP_BUTTONS":   render_buttons(content, data, "groups"),
        "NOTE_BLOCKS":     notes_html,
        "STUDY_GUIDE":     render_study_guide(content, data),
        "NOTE_COUNT":      str(note_count),
        "FOLLOW_TITLE":    esc((content.get("follow_along") or {}).get("title")
                               or "Where we are going this morning"),
        "FOLLOW_LEDE":     _follow[2],
        "FOLLOW_POINTS":   _follow[0],
        "FOLLOW_CALL":     _follow[1],
        "TILES":           tiles,
        "PASTOR_NOTES":    render_pastor(content, data),
        # The heading used to read "Two things worth saying out loud" no
        # matter how many notes were underneath it. A page that miscounts
        # its own contents is the kind of small wrongness people notice.
        "PASTOR_HEAD":     esc(content.get("pastor_head") or "{} worth saying out loud".format(
            {1: "One thing", 2: "Two things", 3: "Three things", 4: "Four things",
             5: "Five things"}.get(len(content.get("pastor_notes") or []), "A few things"))),
        "RHYTHM":          render_rhythm(content, data),
        "GROUPS":          render_groups(content, data),
        "INVITE_ART_TAG":  img_tag("seriesart", invite),
        "INVITE_ART":      esc(invite.get("art", "")),
        "INVITE_ART_ALT":  esc(invite.get("art_alt", "")),
        "INVITE_LEDE":     esc(invite.get("lede", "")),
        "INVITE_TEXT":     esc(invite.get("text", "")),
        "SWAG_ART":        esc(swag.get("art", "")),
        "SWAG_TITLE":      esc(swag.get("title", "")),
        "SWAG_BODY":       esc(swag.get("body", "")),
        "SWAG_URL":        esc(swag.get("url", "")),
        "LIVE_URL":        esc(content.get("live_url", "")),
        "CONNECT_URL":     esc(resolve_link(content.get("connect_card"), data)
                               or content.get("connect_card", {}).get("url", "")),
        "TRYFIVE_URL":     esc(resolve_link(content.get("try_five"), data)
                               or content.get("try_five", {}).get("url", "")),
        "FORM_ENDPOINT":   esc(content.get("email", {}).get("endpoint", "")),
        "FORM_KEY":        esc(content.get("email", {}).get("key", "")),
        "REPLY_TO":        esc(content.get("email", {}).get("reply_to", "")),
        "BUILT_AT":        dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }
    fields.update(render_giving(content, data))

    for k, v in fields.items():
        page = page.replace("{{" + k + "}}", v)

    leftover = re.findall(r"\{\{([A-Z_]+)\}\}", page)
    if leftover:
        notes.append("UNFILLED placeholders: " + ", ".join(sorted(set(leftover))))

    page = wrap(page, "SOJO Sunday",
                f"{content.get('label', 'Sunday')} at SOJO Church, "
                f"{sunday:%B} {sunday.day} — order of service, message notes, "
                f"and what’s next.")

    os.makedirs(ARCHIVE, exist_ok=True)
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    with open(os.path.join(ARCHIVE, f"{sunday.isoformat()}.html"), "w",
              encoding="utf-8") as f:
        f.write(page)

    # ---- the live page, for people who are not in the room ----
    if os.path.exists(LIVE_TEMPLATE):
        with open(LIVE_TEMPLATE, encoding="utf-8") as f:
            live = f.read()
        ch_html, ch_json, ch_total = build_chapters(content, data)
        lv = content.get("live", {})
        live_fields = dict(fields)
        live_fields.update({
            "CHAPTERS":         ch_html,
            "CHAPTER_DATA":     ch_json,
            "SERVICE_TIMES":    json.dumps(lv.get("service_times", ["09:00", "11:00"])),
            "SERVICE_SECONDS":  str(ch_total or 4500),
            "YT_CHANNEL":       esc(lv.get("youtube_channel_id", "")),
            "YT_REPLAY":        esc(lv.get("replay_video_id", "")),
            "GIVE_URL":         esc(lv.get("give_url", "https://sojo.churchcenter.com/giving")),
            "CHALLENGE_URL":    esc(lv.get("challenge_url", "https://sojo.church/give.html#challenge")),
        })
        for k, v in live_fields.items():
            live = live.replace("{{" + k + "}}", v)
        left = re.findall(r"\{\{([A-Z_]+)\}\}", live)
        if left:
            notes.append("live page UNFILLED: " + ", ".join(sorted(set(left))))
        live = wrap(live, "SOJO Live",
                    f"Watch SOJO Church live — {content.get('label', 'Sunday')}, "
                    f"{sunday:%B} {sunday.day}. Follow the order of service as it happens.")
        os.makedirs(LIVE_OUT, exist_ok=True)
        os.makedirs(os.path.join(LIVE_OUT, "archive"), exist_ok=True)
        with open(os.path.join(LIVE_OUT, "index.html"), "w", encoding="utf-8") as f:
            f.write(live)
        with open(os.path.join(LIVE_OUT, "archive", f"{sunday.isoformat()}.html"),
                  "w", encoding="utf-8") as f:
            f.write(live)
        for asset in ("sojo-seal.png", "sojo-mark.png"):
            src = os.path.join(OUT, asset)
            if os.path.exists(src):
                shutil.copy(src, os.path.join(LIVE_OUT, asset))
        notes.append(f"live page: {len(ch_json and json.loads(ch_json) or [])} chapters, "
                     f"service {ch_total // 60}:{ch_total % 60:02d}")

    # Artwork named in content.json has to travel with the page.
    for name in {hero.get("art"), invite.get("art"), swag.get("art")}:
        if not name:
            continue
        src = os.path.join(HERE, "art", name)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(OUT, name))
        elif not os.path.exists(os.path.join(OUT, name)):
            notes.append(f"MISSING artwork: {name} (put it in sunday/art/)")

    return notes


def main():
    args = [a for a in sys.argv[1:]]
    offline = "--offline" in args
    args = [a for a in args if not a.startswith("--")]
    sunday = dt.date.fromisoformat(args[0]) if args else pco.coming_sunday()

    if "--check" in sys.argv[1:]:
        return pco.check(sunday)

    print(f"Sunday page — {sunday:%A, %B %-d, %Y}\n")
    for line in build(sunday, offline):
        mark = "  !" if ("FAIL" in line or "MISSING" in line or
                         "UNFILLED" in line or "dropped" in line) else "   "
        print(f"{mark} {line}")
    print(f"\nwrote standalone/sunday/ and standalone/live/ (+ archive/{sunday.isoformat()}.html)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
