# Setting this up

Three parts. The first two take about twenty minutes and turn the weekly page
on. The third is optional and can wait.

---

## Part 1 — Put the files in the repo

Copy these into `coreyalley704/sojo-website`, keeping the paths:

```
sunday/build_sunday.py          the generator
sunday/pco.py                   the Planning Center reader
sunday/content.json             the week's words
sunday/template.html            the layout
sunday/art/                     header images
sunday/PROCESS.md               how it works
sunday/SETUP.md                 this file
standalone/sunday-admin/        the editor
.github/workflows/sunday.yml    the schedule
```

`standalone/sunday/` already exists and the build writes into it.

Commit and push.

> **Check one thing first.** Open `build.py`, find `REDIRECTS`, and make sure
> there is no `sunday` or `sunday-admin` key in it. `emit_redirects()` runs
> after `copy_standalone()` and would overwrite both pages with redirect stubs.

---

## Part 2 — Give it a Planning Center token

1. Go to **api.planningcenteronline.com/oauth/applications** while signed in as
   yourself.
2. Scroll to **Personal Access Tokens** → **New Personal Access Token**.
   Describe it `sojo-sunday-page`.
3. You get an **Application ID** and a **Secret**. The secret is shown once.

   🔒 **This token can read every donation record the church has.** It goes in
   exactly one place, below. Not in the repo — the repo is public. Not in an
   email. Not in a chat.

4. In GitHub: the repo → **Settings** → **Secrets and variables** → **Actions**
   → **New repository secret**. Add two:

   | Name | Value |
   |---|---|
   | `PCO_APP_ID` | the Application ID |
   | `PCO_SECRET` | the Secret |

5. Go to the **Actions** tab → **Sunday page** → **Run workflow**.

The first step is a check that reads all six Planning Center products and
reports on each one. Open the log and read it. You want six `ok` lines. Anything
else tells you exactly which product to look at.

That is it. From here the page rebuilds Thursday morning and again Sunday
morning, and anybody can run it by hand from that same tab.

---

## Part 3 — Direct save from the editor *(optional)*

Without this, the editor at **sojo.church/sunday-admin/** works completely — you
write, it keeps your work in the browser, and you press **Download
content.json** and put that file in the repo. That is a real workflow and it is
fine to stop here.

With it, **Save to the site** writes straight to the repo and the page rebuilds
on its own. Whoever writes the words never touches GitHub.

### What it needs

A small Cloudflare Worker holding two secrets: a GitHub token that can write to
one repo, and a password you give your team. The editor posts to it; it commits
`content.json`; the push triggers the Action.

1. **A fine-grained GitHub token.** github.com → Settings → Developer settings →
   Personal access tokens → Fine-grained tokens → Generate new.
   - Repository access: **only** `coreyalley704/sojo-website`
   - Permissions: **Contents → Read and write**. Nothing else.
   - Expiration: a year, and put a reminder in your calendar.

2. **A Worker.** Cloudflare → Workers & Pages → Create → Worker. Name it
   `sojo-sunday-save`. Paste in `sunday/save-worker.js`. Deploy.

3. **Its secrets.** Worker → Settings → Variables and Secrets. Add three, all as
   **Secret**:

   | Name | Value |
   |---|---|
   | `GITHUB_TOKEN` | the token from step 1 |
   | `EDIT_PASSWORD` | a password for your team |
   | `REPO` | `coreyalley704/sojo-website` |

4. **A subdomain.** Worker → Settings → Domains & Routes → Add → Custom Domain →
   `save.sojo.church`. Cloudflare gives you a DNS record; add it at GoDaddy.

   ⚠️ **At GoDaddy, only ever add records. Never delete one.** The existing
   records point the website and the church's email.

   ⚠️ **Do not point `sojo.church` itself at Cloudflare.** Only the subdomain.
   Moving the apex domain means moving the whole website, and there is no reason
   to take that risk for a save button.

5. **Turn it on in the editor.** In `standalone/sunday-admin/index.html`, near
   the top of the script:

   ```js
   var SAVE_ENDPOINT = 'https://save.sojo.church';
   ```

   Commit. The Save button starts working.

---

## Running it on your own machine

```bash
export PCO_APP_ID=...        # never commit these
export PCO_SECRET=...

python3 sunday/build_sunday.py --check      # test all six reads
python3 sunday/build_sunday.py              # build the next Sunday
python3 sunday/build_sunday.py 2026-10-11   # build a specific week
python3 sunday/build_sunday.py --offline    # no Planning Center at all
```

`--offline` is how you check a wording change without touching the API. Sign-up
tiles will drop, because their links cannot be resolved without Planning Center —
that is the safety behaviour working, not a bug.

---

## When something looks wrong

**The page did not update.** Actions tab → the last *Sunday page* run. If it is
red, the log says which step. If it is green and says "nothing changed this
run", then nothing did.

**A number looks wrong.** Run the check step and read the Giving line. Remember
the page includes pending ACH on purpose, which is what the Giving dashboard
shows.

**A tile disappeared.** Its sign-up is closed, archived or deleted in Planning
Center. That is the page protecting a guest from a dead link. Reopen the sign-up
or change what the tile points at.

**The order of service is wrong.** It is wrong in the Services plan. Fix it
there and re-run; do not patch it on the page, or the two will drift.
