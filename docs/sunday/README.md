# /sunday — the chair-tag order of service

Served at **sojo.church/sunday**. The NFC tags on the chairs point here and
never change; only the contents of this folder change, week to week.

## How it deploys

`build.py`'s `copy_standalone()` scans `standalone/` on disk and copies every
folder inside it straight into `docs/`. That happens *after* `docs/` is wiped
and *after* the unused-photo prune, so nothing here is at risk. Adding this
folder required no change to `build.py`.

One optional line, so the page appears in `sitemap.xml`:

```python
STANDALONE_SLUGS = ['hello', 'christmas', 'sunday']
```

Do **not** add a `sunday` key to `REDIRECTS`. `emit_redirects()` runs after
`copy_standalone()` and would overwrite this `index.html` with a stub.

## Updating it each week

Ask Claude. It reads the week's plan out of Planning Center Services, the
signup links out of Registrations, the weekly rhythm out of Calendar, the
group list out of Groups, and the sermon points out of that week's
`[TITLE]-Sermon-Outline` doc in Drive, and returns a new `index.html`.

Two things a human still owns:
- the headline and the framing copy, which no system stores
- the series artwork for the hero

## Things that will bite you

- **Change the date in `KEY_PREFIX`** in the script at the bottom every week.
  It namespaces the notes people type. Leave it and last Sunday's notes come
  back on their phones.
- **Keep images in this folder**, referenced relatively. An absolute
  `/assets/img/*.webp` path can be deleted by the prune step.
- **Nothing here can send email.** GitHub Pages is static. `FORM_ENDPOINT` at
  the top of the script takes a form service URL. Left empty, the send button
  says so honestly rather than pretending.
- **Never hand-edit `docs/sunday/`.** It is generated. Edit here.

## What is in the page

Order of service · message notes that save to the phone and ride along in the
email · this week's sign-ups · the weekly rhythm · groups with room · an
invite a friend share · phone, text and socials.

Analytics use the site's existing GA tag, so taps show up in the same place as
the rest of sojo.church.
