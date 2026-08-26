# SOJO Website Redesign — Handoff

**Built:** August 23, 2026 · **Target launch:** on or before Sunday, September 6

---

## What you're getting

- **Live clickable preview** — all 14 pages, desktop and mobile, real photos, real links.
- **`sojo-church-site.zip`** — the actual site. 14 HTML pages, one stylesheet, ~100 optimized images, your welcome film, and a self-updating YouTube embed. No WordPress, no Divi, no plugins, no theme license.

Plain HTML and CSS. It will load in under a second on a phone in a parking lot, which is exactly where people will be reading it on September 6.

---

## Bugs on the current site that this fixes

Four things live on sojo.church right now, worth knowing regardless of what you do with this redesign:

1. **The Instagram link is broken.** Every page links to `instagram.com/sojo.church`. Your actual account is `@wearesojo.church`. Dead on every page.
2. **The footer copyright says "City Church."** Not SOJO. All 14 pages.
3. **The footer and Plan A Visit still say 848 Union Street** — including on the "Our New Home" page, directly under the new address.
4. **The New Home page still asks people to respond by "May 24th, 2026."**

All four corrected. The Kettle Room address is now in the footer, the schema markup, and Plan A Visit.

---

## The 14 pages

| Page | Its one job |
|---|---|
| **Home** | Get a stranger to Sunday. Move info is section two, not buried. |
| **New Here** | Answer the nine questions that actually stop people from coming. |
| **Our New Home** | Your letter, the shell photos, the renderings, and step-by-step "how to find the room." |
| **Our Story** | Seven years in five rooms — living room, cafeteria, parking lot, Union Street, Gibson Mill. |
| **SOJO Kids** | Get a parent to relax. Four promises, then the rooms. |
| **SOJO Youth** | Get a student in the door and a parent comfortable. |
| **About** | Who we are, history summary, PC, the team. |
| **Next Steps** | Your two tracks, exactly as you laid them out. |
| **Mission** | Vision, the three movements, and how every ministry maps to one of them. |
| **Groups** | Your four kinds — Connect, Community, Care, Classes — plus how to join and lead. |
| **Serve** | The bigger-room ask, seven teams, Meals on Wheels. |
| **Give** | Why we give, what the Bible says, who and how much, when, five ways — plus the 90-Day Challenge. |
| **Watch** | Three ways in, then a nudge to come sit in the room. |
| **Swag** | Three marks, nine colorways, XS–3XL. |

**Structural change:** the old nav had five dropdowns and eighteen destinations. A first-time guest doesn't want eighteen choices. New nav is eight items, the first is "New Here," and **Mission** sits third. Our Story, Groups, and Serve live one click deep from About and Next Steps, plus the footer.

---

## Next Steps, built to your spec

**Track A — Finding your people.** Come to SOJO → Come back → Try five services → Discover SOJO (last Sunday of every month, right after second service, sign up in Church Center).

**Track B — Following Jesus.** Discover More (three-week virtual class, basic doctrine and discipleship) → Decide to follow Jesus → Get baptized → Join a group → Start serving.

The page frames them as parallel tracks, not a ranking — most people walk both at once. Generosity gets its own short section at the bottom as a third ladder.

---

## Where I told the truth on your behalf

Per your note, the site now says **yes, but not yet** about both the coffee shop and the permanent kids space — **early 2027** on both, stated plainly on the New Home FAQ, in your letter, in the gallery captions, and on Our Story. The homepage stat block now reads "2027 — Coffee shop & permanent kids space" instead of implying doors open seven days a week on day one.

This is the right call and it's also good marketing. A rendering that overpromises costs you more trust on September 7 than honesty costs you on August 24.

Every gallery image on Our New Home is now individually captioned — what room it is, and whether it's ready September 6 or phased later. **Please have Landace confirm my room labels on the renderings**; I described what I could see, but she'll know which render is which space.

---

## Brand guide compliance

After reading the Brand Guidelines PDF I corrected four things:

**1. Logo usage — this one mattered.** I had been using the two-toned lockup (charcoal SOJO + gold CHURCH) in the header and the cream/gold version in the footer. Page 14 of the guide lists mixed-color logos under **DON'T**. The site now uses solid charcoal on light backgrounds and solid cream on dark, exactly as the DO column specifies. The boxed SOJO icon is the favicon, which satisfies "don't use SOJO alone unboxed."

**2. Palette.** Swapped my sampled hexes for the official ones: Black `#302E2A`, Cream `#F5F0E6`, Gold `#BFAE86`, Blue `#92A29D`, Green `#A6A98E`, plus the expanded palette for greys and sand. I had invented a blue-grey "concrete" color for the mill sections — that's now the official brand **Blue**, which happens to be almost exactly the color of the mill floor. It carries black type rather than cream, because Blue is a light primary and cream on it fails contrast.

**3. Display typeface.** Moved from Oswald to **Big Shoulders Display**, which is a much closer web-licensed match to Hornesa FC's proportions. If Pixel Painters can license the real web fonts, it's a ten-minute swap in one file.

**4. Killed the monospace — you were right about this one.** I had used Lekton for every eyebrow, caption, figure label, price, and meta line on the site, set in wide-tracked uppercase. That's the machine-generated look, and the guide never asked for it: it lists Lekton as **H4 only**, a single heading level, not a system-wide label font. Every label on all fourteen pages is now **Inter** — the guide's secondary family — at real weight with the letter-spacing pulled down from 0.22em to about 0.06–0.09em. Same information, reads like branding instead of terminal output. Lekton stays defined in the stylesheet for genuine H4 use and is loaded nowhere else, which also drops a font request off every page.

**If the display face still isn't right,** say so and I'll swap it. Two alternatives closer to different parts of Hornesa's character: **Saira Extra Condensed** (narrower, slightly softer terminals) and **Fjalla One** (heavier, more grounded). It's one line in one file and every heading on the site follows.

I also put the mission statement verbatim in the footer: *"A community with a cause — helping people find life, purpose, and peace."*

The voice section of the guide is what I'd already been writing toward — warm not corporate, honest not performative, no insider church language, no guilt-driven messaging. Every page ends with a clear next step, which is the DO in your SEED framework.

---

## Vision and mission, woven through

"Changing the world one person at a time" is gone from every page. In its place:

- **Vision:** *A community with a cause.*
- **Mission:** *Helping people know life, grow in peace, and go in purpose.*

That phrasing now appears on the home page (its own section, with all three movements explained), in the About opening, in the footer under the logo, and on a dedicated **Mission** page that takes each movement in turn — the Scripture behind it, what it actually means, and what it looks like at SOJO in concrete terms.

The Mission page ends with a filter section mapping every single thing the church does to one of the three: Sunday → Know. Kids and Youth → Know and Grow. Discover SOJO, Discover More, Groups → Grow. Serving, Outreach, Carolina Movement, Giving → Go. I also tied in your Psalm 1 and Ezekiel 47 anchors — formation over numbers, depth before distance — because they're the picture underneath the whole thing.

---

## Groups, built to your four categories

1. **Connect Groups** — community and connection through common interests.
2. **Community Groups** — Scripture, praying for one another, going deeper with God and people.
3. **Care Groups** — SOJO Ink, SOJO Recovery, SOJO Grief Recovery, SOJO DivorceCare, each with its own honest description.
4. **Classes** — A Study in Genesis (Pastor Corey) and SOJO University (Pastor Dan).

Every browse button goes to Planning Center Groups at `sojo.churchcenter.com/groups`. Once you have the real group list — names, nights, neighborhoods, leaders — I can build a filterable directory instead of routing everything to the app.

---

## The welcome film and the self-updating sermon embed

Your welcome video is on three pages — the home page ("Meet SOJO before you walk in"), Plan A Visit, and Watch. It's shot vertical, so it sits in a portrait frame rather than a letterboxed widescreen box. I compressed it from 29MB to 7.2MB with no visible quality loss and generated a poster frame so it doesn't auto-download on mobile.

**The YouTube embed updates itself.** I found your channel ID (`UCl0vhjkyMWlfSxOP8Tqsu3g`) and embedded your *uploads playlist* rather than a single video. That means the newest thing you post is automatically what plays — on the home page and on Watch — with zero weekly maintenance from anybody. Post a message Sunday, it's on the site Sunday.

**Why you can't see it in the preview:** the preview page blocks third-party embeds for security, so the player can't render inside it. Unzip the site and open `watch.html` in any browser and it plays. Worth verifying once on the live site — if the uploads playlist won't embed, make a public "Messages" playlist on YouTube and send me its ID; it's a one-line change.

---

## The swag ordering dead-end — fixed, and here's the real answer

You were right, and it was my fault: the buy buttons pointed at a `tel:` link, which does nothing inside the preview. That's a dead end and dead ends are unacceptable on a page asking people to buy something.

Fixed now. The page has a **"How to get one"** section with three routes that all actually work today: grab one at the swag table Sunday, text us the mark/color/size and we'll hold it, or watch Church Center for drops.

**For a real online store, you have three options.** In my order of preference for you:

1. **Printful or Printify + a simple storefront.** Print-on-demand — no inventory, no boxes in your office, no leftover 3XLs. Margins are thinner but the operational cost is near zero, and for a church that matters more than margin.
2. **Square Online.** Free tier, dead simple, and if you already take card payments at the swag table you can run in-person and online off one system with one inventory count.
3. **Shopify.** Most powerful, ~$39/month. Only worth it if swag becomes a real revenue line rather than a mission tool.

Send me whichever URL you land on and every buy button on the site follows it — one line, one file.

---

## The phone number

I looked for your Hello Church number and **I can't reach it.** Hello Church's number lives behind their dashboard login, and there's no Hello Church code anywhere on the current sojo.church — I checked every page. Your public listings (Yelp, ChurchFinder, Yahoo Local) don't show a phone number either.

The only number published anywhere I can find is **980-680-0958**, which appears on your Youth page as Audrie's. That's what every "call or text" on the site currently uses. **Send me the Hello Church number and it changes in one line** — it's a single constant that every contact CTA on all fourteen pages reads from.

---

## Art direction

Per your note about reflecting the room, the design speaks the mill's own vocabulary rather than generic church-website decoration:

- **The brand Blue as the floor.** Official Blue `#92A29D` is, almost exactly, the color of that polished concrete. It's now a full section band on the home page, Our New Home, Kids, Next Steps, Groups and Give.
- **Column rhythm.** Faint vertical hairlines run across those bands at the spacing of the mill's steel columns.
- **Raking light.** A soft diagonal sheen, the way the windows throw light across that floor.
- **Curtain light** at the outer edges of the widest bands.
- **Painted floor markings.** The gold corner mark you see as a section marker, and the dashed lane stripe as a divider, are lifted straight off the deck.
- **Poured-concrete grain** — a fine tooth over a slow blotch — instead of flat color anywhere.

Type is still the design: giant condensed caps, a gold handwritten line for the heart moments, a gold underline on the one word carrying weight, hairline rules instead of boxes and cards.

---

## The parking map

Your Gibson Mill site map is now on Our New Home, with a plain-language "read the map" explainer beside it, and the Plan A Visit parking answer points at it.

**The file you sent is only 400×200 pixels**, so the labels are unreadable at any usable size on screen. Send me a higher-resolution version — 1600px wide or a PDF/vector — and I'll drop it straight in. If Gibson Mill can't supply one, I can redraw a simplified SOJO-branded version showing just what a guest needs: the McGill entrance, our lot, and our door.

---

## Five things I still need from you

1. **The Hello Church plugin.** I looked for it and **it is not on the live site.** The only third-party embed on sojo.church right now is the Church Center modal script; there's no Hello Church code on any page I pulled, including Plan A Visit. So either it was removed, it was never installed, or it lives in a WordPress plugin that isn't rendering. Send me the embed snippet or account details and I'll wire it into every Plan Your Visit CTA across all 13 pages — that's one change in one file. Until then those buttons go to your Church Center form.
2. **The Hello Church phone number**, per above — and **the contact email**. The current site lists `audrie@sojourner.church`, a different domain, so I wouldn't guess.
3. **A merch store URL** once you pick one from the three options above. Prices are placeholders ($28 / $25) — tell me the real ones.
4. **What We Believe.** No beliefs page exists on the current site and I didn't invent one. Real gap for a church site — a lot of people won't visit until they've read it. Send me your doctrinal statement.
5. **Group details.** The Groups page is live but generic, because I don't have your actual groups. Send me the list — names, nights, neighborhoods, leaders — and I'll build the real directory. Same for **Discover More**: I need the registration link and the next start date; it currently points at the general Church Center events page. And the **90-Day Challenge sign-up** currently reuses the Discover SOJO event ID — give me the right one.

Also worth deciding: I dropped **SOJO University**, **Tithe Challenge**, and the **outreach partner logo wall**. None serve a first-time guest and two looked dormant. Say the word if any should come back.

---

## Getting it live before September 6

**Option A — replace WordPress entirely (recommended).** Point sojo.church at any static host. Netlify, Cloudflare Pages, and GitHub Pages are free and all handle a site this size. Drag the unzipped folder in, update the DNS, done. Nothing to patch, nothing to break the week you're moving a church.

**Option B — keep WordPress, rebuild in Divi.** Slower, and you'd be reproducing by hand what already exists as working code.

**Option C — run it alongside.** Host at a subdomain, get eyes on it for a week, flip DNS the Friday before the move.

Whichever way: edit the existing Google Business Profile on September 1 — **never create a new listing** — and have somebody who has never been to the Mill pin-test Google, Apple, and Waze on Saturday night, September 5.

---

## To change something

The whole site generates from one Python file (`build.py`) and one stylesheet. Change a headline once, rebuild, every page updates. Tell me what to change and I'll rebuild it — faster than either of us hand-editing thirteen HTML files.
