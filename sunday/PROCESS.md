# How the Sunday page builds itself

The page at **sojo.church/sunday** is not written each week. It is assembled
from two things:

| | Where it comes from | Who owns it |
|---|---|---|
| **The facts** | Planning Center, read live at build time | Whoever keeps PCO current |
| **The words** | `sunday/content.json`, edited at `/sunday/admin/` | Whoever writes for the church |

Nobody retypes a service order, a song list, a giving total, or a sign-up link.
If two systems hold the same fact, they eventually disagree, and the one on the
chair back is the one a guest believes.

---

## The weekly rhythm

| When | What happens | Who |
|---|---|---|
| **Tue–Wed** | The plan gets built in Planning Center Services. Sign-ups created. | Staff, as normal |
| **Thu 9:47am** | The Action rebuilds the page and commits it. Live in about two minutes. | Automatic |
| **Thu, by 5pm** | Somebody opens the page and reads it. Fixes wording at `/sunday/admin/`. | Comms |
| **Sun 6:47am** | The Action runs again, catching anything changed late. | Automatic |

Run it by hand any time from the repo's **Actions** tab → *Sunday page* →
**Run workflow**. There is a box for a specific service date if you want to
build a week ahead.

---

## What each Planning Center product supplies

### 1. Services — the order of service

Reads the plan whose date matches the coming Sunday, in the **Sunday Services**
service type.

The filter that matters is `service_position`. Planning Center marks each item
`pre`, `during`, or `post`. Countdowns, announcement loops and green-room notes
are `pre`/`post` — production cues, not congregation content. **Only `during`
items reach the page.**

Item titles in a plan are written for the band and the booth: *Flow Moment*,
*Giving Talk*, *Closing Announcements*. The `flow` block in `content.json`
renames those into words a guest understands, hides the ones that are pure
production, and adds one line of detail where it helps.

- `{{songs}}` expands to the worship set — every song before the message.
- `{{songs_after}}` is the response song.
- `insert` adds something the plan does not carry. **Communion is the standing
  example**: it is on the Calendar every first Sunday and it happens in the
  room, but it has never been an item in the plan.

> **Worth fixing at the source:** if Communion is in the service, it belongs in
> the Services plan so the band and production see it too. The `insert` is a
> patch for the page, not for the problem.

### 2. Giving — the generosity numbers

Two figures: the last **complete Monday–Sunday week**, and the month.

Both **include pending ACH**, which is what the Giving dashboard shows. This is
the one number that has caused real confusion: filtering to settled-only
silently drops every ACH gift that has not cleared, and ACH takes several days.
That is the whole reason a week once read **$9,831** on one screen and
**$9,712** on another. Refunded and failed gifts are excluded; pending is not.

The totals are summed from the donation rows rather than read from a totals
field, because the rows are the thing that can be checked by hand if anybody
ever doubts the number.

### 3. Registrations — the sign-ups

Every open, unarchived sign-up, keyed by name.

`content.json` links by **name**, never by ID:

```json
{ "signup": "wednesday night bible study" }
```

The build looks that name up fresh each week. **A sign-up that has been closed,
archived or deleted resolves to nothing, and the tile is dropped from the page
rather than rendered dead.** This is not theoretical — the Candy Crawl sign-up
was deleted out of Planning Center in September and the live page kept pointing
at it. Under this build, that tile would have quietly disappeared instead.

### 4. Calendar — the week ahead

Event instances between this Sunday and the next. Used to sanity-check the
weekly rhythm and to catch the one-offs: a youth night at a ballpark instead of
the usual room, a prayer night that moved.

> The Calendar is only as right as somebody made it. Youth has read 6:30pm there
> while actually meeting at 6:00. The page cannot know that; a person has to fix
> the Calendar.

### 5. Groups — find your people

Active, non-archived groups that have a public Church Center link. Groups
without a link are skipped, because a group nobody can join does not belong on
a page whose whole job is next steps.

If the Groups read fails, `content.json` carries a hand-written fallback list —
better than an empty section.

### 6. People (Forms) — the connect card

Active forms, by name, so `{"form": "connect card"}` resolves to whatever that
form's public URL is today.

---

## What happens when something fails

Nothing is fatal. Every read is wrapped; a failure logs and falls back to
`content.json`. A build that ships last week's number and says so in the log is
better than a build that dies and leaves the chairs pointing at nothing.

Before anything is published the Action checks the page:

- it exists and is not empty
- no `{{PLACEHOLDER}}` survived
- it is at least 20 KB — a page much smaller than that did not render

If any of those fail, **nothing is committed** and the previous week's page
stays up. A stale bulletin beats a broken one.

---

## The two rules that keep this working

**1. Never edit `docs/` by hand.** `build.py` wipes and regenerates it. Edit
`standalone/sunday/`, which `copy_standalone()` copies in on every site build.
The Action mirrors the one folder into `docs/` so the page goes live without
waiting for a full site build.

**2. Never add a `sunday` key to `REDIRECTS` in build.py.** `emit_redirects()`
runs *after* `copy_standalone()` and would overwrite the page with a redirect
stub.

---

## The archive

Every build also writes `standalone/sunday/archive/YYYY-MM-DD.html`. That week
stays at its own address forever, with every link still live — which is a better
record than a PDF, because a PDF's links are dead the moment it is made.
