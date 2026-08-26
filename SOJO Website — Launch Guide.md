# SOJO Website — Launch Guide

**Updated:** August 24, 2026 · **Move date:** Sunday, September 6

This is the complete list of what I still need from you, how to show the site to people this week, and the exact steps to take it live.

---

## 1. Links and info I still need

Every one of these is a one-line change once you send it. In priority order:

**Links that fix known gaps**

1. **Discover SOJO registration link.** The old site's event (3833678) turned out to be the 90-Day Challenge registration, so right now Discover SOJO buttons go to the general Church Center events list. Send the correct event link from Church Center.
2. **Discover More registration link** and the next start date. Currently also points at the events list.
3. **Confirm the 90-Day Challenge event** really is `sojo.churchcenter.com/registrations/events/3833678` — that's what all Challenge buttons use.
4. **Merch store URL** (Printful/Printify, Square, or Shopify — your pick) plus real prices. Swag buttons currently route to "how to get one" instructions.
5. **633 Church** — website or Facebook page (your Concord plant partner).
6. **The Abbey** (San Diego) — website.
7. **CAB Bible** — website or page.

**Info that fixes known placeholders**

8. **The right contact email.** Old site listed `audrie@sojourner.church` — a different domain — so every contact CTA uses 980-680-0958.
9. **The Hello Church / church phone number** — confirm 980-680-0958 is right for "call or text," or give me the number you want public.
10. **Nursery ages** — your Kids page says 0–24 months (preschool 2–4); your Gibson Mill FAQ says nursery through 3, SOJO Kids at 4+. Pick one.

**Files**

11. **The two giving testimony videos** — drop `0C5A0049.MP4` and `0C5A9510.MP4` into the SOJO Church folder on your computer (Website Redesign subfolder is fine). The give page section is built and appears automatically once I encode them.
12. **Higher-resolution Gibson Mill parking map** (current one is 400×200 — labels unreadable). Or say the word and I'll draw a clean SOJO-branded version.
13. **Partner logos** (optional — the partner wall works without them). Ask each partner for their media kit.
14. **Web font files** from Pixel Painters for Hornesa FC and Travail Acharné (optional — the stand-ins are close).

**Verifications**

15. Have **Landace confirm the room labels** on the New Home rendering captions.
16. After go-live, **check the YouTube embed plays** on the home and Watch pages. If the uploads playlist won't embed, make a public "Messages" playlist on YouTube and send me its ID.

---

## 2. Showing people the site right now

You have two ways today, no hosting needed:

**A. The preview link.** Your clickable preview at claude.ai is private to you until you share it — open it, use the share menu, and send the link to Betsy, the staff, or anyone. All 18 pages work; the only things that don't run inside the preview are the YouTube embed and the Visit Planner popup (both are wired and work on the real site).

**B. The real files.** Unzip `sojo-church-site.zip` from your Website Redesign folder and double-click `index.html`. The full site opens in your browser — videos, YouTube embed and all. Works on any computer; you can AirDrop the folder to someone.

**Best option for staff review is actually step 1 of going live** — see below. Netlify gives you a real temporary URL (like `sojo-preview.netlify.app`) you can text to anyone, in about three minutes, free.

---

## 3. Taking it live — the exact steps

**Recommended host: Netlify (free tier is plenty for this site).** Cloudflare Pages is an equally good alternative; the steps are nearly identical.

**Step 1 — Put the site up on a temporary URL (3 minutes, do this today)**
1. Unzip `sojo-church-site.zip` so you have a folder.
2. Go to **app.netlify.com/drop** and create a free account.
3. Drag the unzipped folder onto the page. Done — you get a URL like `random-name.netlify.app`.
4. Rename it something friendly (Site settings → Change site name → `sojo-church`) and share `sojo-church.netlify.app` with staff for review. This is your staging site from now on.

**Step 2 — Test on the temp URL**
Click every nav item on a phone and a laptop. Play the welcome video. Confirm the YouTube message plays and the "Tell us you're coming" buttons open the Hello Church visit planner popup.

**Step 3 — Connect sojo.church (do this when you're ready to flip)**
1. In Netlify: **Domain management → Add a domain → sojo.church.**
2. Netlify shows you DNS records to set. Log in **wherever sojo.church is registered** (GoDaddy, Namecheap, or possibly through Mission Support — check with them if unsure) and update the records as shown — typically an A record for `sojo.church` and a CNAME for `www`.
3. Wait for DNS to propagate (minutes to a few hours). HTTPS/SSL is automatic and free.
4. **Don't cancel the WordPress hosting until after the flip is confirmed** — the old site keeps serving until DNS moves.

**Timing recommendation:** flip DNS the **Friday before September 6** (Sept 4), so the new address, map links, and planner are what everyone sees on move weekend — with the temp URL fully reviewed the week before.

**Step 4 — The first week live**
1. **Google Search Console** (search.google.com/search-console): verify sojo.church and submit `https://sojo.church/sitemap.xml`. Biggest single SEO lever.
2. **September 1:** EDIT the existing Google Business Profile to the new address — never create a new listing.
3. **Saturday night, Sept 5:** have somebody who's never been to the Mill pin-test Google Maps, Apple Maps, and Waze.
4. Update the link in your Instagram bio, Linktree, Facebook, and email footers.

**Making changes after launch:** tell me what to change, I rebuild, you drag the new folder onto Netlify (Deploys → drag and drop). Two minutes, zero risk — every deploy can be rolled back with one click.
