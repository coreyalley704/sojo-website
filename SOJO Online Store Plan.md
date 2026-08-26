# SOJO Online Store — The Plan (for when you're ready)

**Updated:** August 26, 2026 · A later project, mapped out now so it's a decision instead of a research assignment.

## The idea in one paragraph

You want people to buy SOJO swag online and have it shipped to their door without anyone at SOJO folding shirts or driving to the post office. That's **print-on-demand**: a storefront (where people browse and pay) connected to a print service (which prints each item when it's ordered and ships it drop-ship, straight to the buyer). Nothing is printed until somebody orders it — zero inventory, zero risk, zero garage full of medium tees.

## The recommended stack: Shopify + Printful

**Shopify** is the storefront — the cart, checkout, receipts, and a clean store page we link from sojo.church/swag. **Printful** is the print service — it holds your designs, prints on Bella+Canvas/Comfort Colors-quality blanks, and ships with your branding. The two connect with an official app in about ten minutes: you design products in Printful, they appear in Shopify automatically, and when someone orders, Printful just handles it. You never touch the order.

**Costs, honestly:**

| Piece | Cost |
|---|---|
| Shopify Starter plan | $5/month (a buy-button storefront — plenty for swag) |
| Shopify Basic (full store site) | $39/month — only if you outgrow Starter |
| Printful | $0/month — they take their cut per item printed |
| Per-item example | Printful prints a tee for ~$13–16; you list at $25–28; SOJO keeps the difference |
| Transaction fees | ~3% (standard card processing, unavoidable anywhere) |

**The margin math:** price items about $10 over Printful's cost and each shirt gives roughly $8–9 back to SOJO after fees. Or price at cost +$2 and treat swag as marketing, not fundraising. Decide which one swag *is* for SOJO before setting prices — that decision drives everything.

**The cheaper alternative (still on the table):** Printful's own free Quick Store — no Shopify, no monthly fee at all, slightly less polished checkout, no custom domain. It's the version we scoped earlier. Totally reasonable to start there and graduate to Shopify later; the designs move with you because they live in Printful either way.

## What has to exist before either version works

1. **Print-ready art from Pixel Painters.** This is the real blocker, not the technology. Each design needs a transparent PNG at **4000px+ wide, 300 DPI** (the web images we have are far too small to print). Ask for: the three tee marks, plus any logo lockups you'd put on hats/mugs — each as "print-ready transparent PNG."
2. **A products decision.** Start small: 3 tees, 1 hat, 1 mug, the tote. You can add drinkware/pouches in a week two.
3. **Real prices** (see margin math above).
4. **A card for billing** (Shopify's $5/month, if you go that route).

## Setup day, step by step (about 90 minutes total, and I drive most of it)

1. Create the Printful account (free) and upload the print-ready art.
2. Create products in Printful — pick garments, colors (match the brand: cream, charcoal, gold), placement, and mockups. Printful generates the product photos automatically.
3. Create the Shopify Starter account, connect the Printful app (one click, you approve it).
4. Products sync into Shopify; set prices; turn on payments (Shopify Payments — bank account, standard setup).
5. I take the store link, drop it into the site's `STORE` constant, and every swag button on sojo.church goes from "how to get one" to **Buy** — that part is a one-line change and two minutes of my time.
6. Order one test shirt to your house before announcing anything. Always.

## Questions to settle before setup day

Is swag fundraising or marketing (drives pricing)? Who owns the accounts and the card (you, Audrie, the church entity)? Do sales run through the church's books (talk to whoever does your bookkeeping — merch revenue is typically taxable unrelated-business income territory; worth a 10-minute conversation)? And does Pixel Painters have the art, or does it need to be commissioned?

**When you're ready, say "let's build the store" — bring the art files and 90 minutes, and we'll do the whole thing in one sitting the same way we did GitHub and Netlify.**
