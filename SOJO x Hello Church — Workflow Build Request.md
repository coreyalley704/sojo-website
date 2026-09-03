# SOJO Church — Workflow Build Request for Hello Church

**From:** Pastor Corey Alley, SOJO Church, Concord NC
**Date:** August 26, 2026 (v2)
**Re:** Keyword texting workflows — website integration + live Sunday use
**Account:** SOJO Church (location u7Nk3mMR6bl4lJdgYze5) · Contact: Corey Alley

---

## 1. What we're trying to do (the big picture)

We just launched a new website (sojo.church), and we move into our new home at Gibson Mill on **Sunday, September 6**. The website walks people through a spiritual journey — knowing God, following Jesus, baptism — and at the decision points, the site's buttons open a **pre-written text to our Hello Church number**. The person adds their name and taps send.

The same keywords will be used **live on Sundays**: Pastor Corey will put a keyword on the screen ("Text JESUS to 980-440-2850") during altar calls and prayer moments — so a person in the room and a person on the website at midnight land in the same automated care journey.

Every one of these texts is a person at a spiritual turning point. The automation must respond **instantly and warmly**, hand them to a real human the same day, and then **walk with them daily** — every workflow below is a **combination of text AND email**, with a defined rhythm for each day.

## 2. The phone number (confirmed)

Our live texting number is **980-440-2850**. The website's buttons are now wired to it. All keywords and workflows below run on this number — if it ever changes again, tell Corey immediately so the website can be updated the same day.

## 3. The keywords

| Keyword | Meaning | Source |
|---|---|---|
| **JESUS** | "I just prayed to follow Jesus" | Website (Partner with Him + Baptism pages) + Sunday altar calls |
| **BAPTIZE** | "I want to be baptized" | Website (Baptism page) + Sundays |
| **QUESTION** | "I have a question about following Jesus" | Website + Sundays |
| **HELLO** | "I'd like to talk with someone at SOJO" | Website footer (every page) |
| **PRAY** | Prayer request | Sundays + website |

Match the keyword at the **start of the message or anywhere in the first line** — website messages arrive as e.g. "JESUS - I just prayed to follow Jesus. My name is Sarah."

## 4. Rules that apply to every workflow

1. **Instant SMS auto-reply** within seconds, 24/7, every keyword.
2. **Email capture:** if no email is on file, the flow asks by text ("So Pastor Corey can send you something each morning, what's your best email?") and saves it to the contact. If a person never gives an email, the email steps are skipped and the SMS steps still run.
3. **Internal alerts** on every trigger: email + push to assigned staff (Corey Alley on all; others listed per workflow).
4. **Tags:** `kw-jesus`, `kw-baptize`, `kw-question`, `kw-hello`, `kw-pray` plus per-flow tags below.
5. **Human override:** a manual staff reply in the conversation pauses the remaining automated *conversational* messages; the daily devotional rhythm (Workflow 1) continues unless a pastor stops it.
6. **Quiet hours:** scheduled sends 7:00am–8:30pm ET. Instant auto-replies are exempt (always immediate).
7. **Exit conditions:** replying STOP ends everything (standard compliance); a pastor can remove the tag to stop a journey manually.
8. **Sunday burst:** all keywords must keep sub-minute response under dozens of simultaneous texts (altar call on Sept 6).

---

## 5. WORKFLOW 1 — JESUS (salvation decision) · the 14-Day New Life Journey

**This is the flagship. Build it exactly as described.**

### Step-by-step flow

1. **Minute 0 (SMS, instant):** "This is the best text we've gotten all week — welcome to the family! 🎉 A pastor (a real one, not a robot) will reply personally today. While you wait: what's your first name, and did you pray that prayer today for the first time?"
2. **Minute 1 (internal):** urgent alert to Corey Alley + Wendy Martin (push + email). Tag `new-believer`. Add to pipeline stage **New Believer**.
3. **Minute 5 (SMS, if no email on file):** "One more thing — Pastor Corey wants to send you a short devotional each morning for your first two weeks. What's your best email?"
4. **Same day (human):** a pastor replies personally in the thread. This does NOT stop the daily journey below.
5. **That evening, 7:30pm (SMS):** "Before you sleep tonight, read this: John 1:1–14. It's the beginning of the story you just stepped into. Your 14-day journey with Pastor Corey starts tomorrow morning."

### The Daily Rhythm — Days 1–14 (two touches every day)

Each day for fourteen days, the person gets:

- **7:00am — EMAIL from Pastor Corey** (from Corey's name/address): a short devotional (~200 words, written by Corey) about the decision they made, built on that day's scripture, ending with the day's reading assignment and one question to carry.
- **8:00pm — SMS follow-up:** "How did the reading go?" plus that day's question, always ending with: **"How can we pray for you tonight?"** (Replies land in the inbox for a human to answer next morning.)

The 14-day scripture path (all readings CSB) — load these into the day slots:

| Day | Scripture | Theme | 8:00pm text (send verbatim) |
|---|---|---|---|
| 1 | John 1:1–14 | The Word became flesh — God came near | "Day 1: How did the reading go? What did it feel like to read that the Word 'became flesh and dwelt among us' — that God came to YOU first? How can we pray for you tonight?" |
| 2 | John 3:1–21 | Born again — what happened to you has a name | "Day 2: How did the reading go? Nicodemus came with questions at night — what's one question you're still carrying? How can we pray for you tonight?" |
| 3 | Psalm 1 | Planted by the stream — two ways to live | "Day 3: How did the reading go? A tree planted by water grows slow and strong — that's you now. What's one old 'path' you're leaving behind? How can we pray for you tonight?" |
| 4 | John 10:1–18 | The Shepherd — life in abundance | "Day 4: How did the reading go? Jesus said he came so you could have life 'in abundance.' Where do you need that most right now? How can we pray for you tonight?" |
| 5 | Luke 15:11–32 | The Father who runs | "Day 5: How did the reading go? The father RAN to his son. Did anything in that story feel like your story? How can we pray for you tonight?" |
| 6 | Romans 8:1–17 | No condemnation — adopted | "Day 6: How did the reading go? 'No condemnation' — none. Is there anything you're still condemning yourself for that God isn't? How can we pray for you tonight?" |
| 7 | Psalm 23 | The Shepherd walks with you | "Day 7: One week in — we're proud of you. How did the reading go? And we'd love to celebrate week one WITH you: Sunday, 9 & 11am, The Kettle Room at Gibson Mill. Can we save you a seat? How can we pray for you tonight?" |
| 8 | Matthew 6:5–15 | Learning to pray | "Day 8: How did the reading go? Try praying the prayer Jesus taught, slowly, in your own words. How did it feel? How can we pray for you tonight?" |
| 9 | Mark 1:14–20 | "Follow me" — apprenticeship begins | "Day 9: How did the reading go? They dropped their nets and learned a whole new life from Jesus. That's what following means — apprenticeship. What's one thing you want him to teach you? How can we pray for you tonight?" |
| 10 | Romans 6:1–11 | Buried and raised — baptism | "Day 10: How did the reading go? Buried with him, raised with him — that's what baptism acts out, and it's your next step. Want to talk about getting baptized at SOJO? Just say YES and a pastor will set it up. How can we pray for you tonight?" |
| 11 | Ephesians 2:1–10 | Grace — God's workmanship | "Day 11: How did the reading go? You are 'his workmanship' — made on purpose, for purpose. What might God be preparing you for? How can we pray for you tonight?" |
| 12 | Philippians 4:4–9 | Peace that guards you | "Day 12: How did the reading go? What's one worry you can hand to God tonight, right now, before you sleep? How can we pray for you tonight?" |
| 13 | Matthew 28:16–20 + Acts 1:8 | Sent — go in purpose | "Day 13: How did the reading go? Jesus sends every follower — starting right where you live. Who's one person in your life who needs to hear what happened to you? How can we pray for you tonight?" |
| 14 | Ezekiel 47:1–12 | The river gets deeper | "Day 14: You made it — two weeks of walking with Jesus. How did the reading go? The river only gets deeper from here. Your next step is our Discover More class (3 weeks, the basics, no question off limits): https://sojo.churchcenter.com/registrations/signups/3848052 — and if baptism is still waiting, let's set the date. We love you. How can we pray for you tonight?" |

**Along the way, the journey encourages each next step at the natural moment:** Sunday attendance on Day 7, prayer practice on Day 8, **baptism on Day 10** (a YES reply should alert a pastor and enroll them in Workflow 2), Discover More + baptism again on Day 14.

**Content note:** Pastor Corey will supply the 14 devotional email bodies (subject lines can be "Day 1 with Jesus: The Word Came Near," etc.). Please build the skeleton with placeholder bodies; we'll drop the final copy in.

**After Day 14:** move pipeline stage to "Journey complete"; notify Wendy Martin to make a personal call; stop automated sends.

---

## 6. WORKFLOW 2 — BAPTIZE

### Step-by-step flow

1. **Minute 0 (SMS, instant):** "YES. So glad you texted. A pastor will reply today to set up a short, easy conversation — your story, what baptism means, any questions — and get you the very next baptism date. What's your first name?"
2. **Minute 1 (internal):** alert Corey Alley + Dan Conklin (push + email). Tag `baptism-interest`. Auto-create task: "Schedule baptism conversation — [name]" due in 3 days.
3. **Minute 5 (SMS, if no email):** email-capture ask.
4. **Hour 1 (EMAIL):** "Everything about baptism at SOJO" — who/what/why/when/where/how (mirrors sojo.church/baptism.html), what to bring (dark clothes + a change; we bring the towel and the party).
5. **Day 2 (SMS, only if no pastor conversation logged):** "Still want to get you in the water! What's a good day this week for a 10-minute call with a pastor?"
6. **Day 4 (SMS, same condition):** "Not letting this one slide 🙂 — reply with a day and time and we'll make it work."
7. **Once the date is set (pastor triggers manually or via tag `baptism-scheduled`):**
   - **3 days before (EMAIL):** what the morning will look like, invite family and friends, service times, parking at Gibson Mill.
   - **Day before (SMS):** "Tomorrow's the day! Dark clothes + a change of clothes. We've got the towel. Bring everybody you love."
   - **Morning of, 7:30am (SMS):** "Today you go public. We could not be prouder of you. See you at the Kettle Room."
   - **Day after (EMAIL from Corey):** celebration letter — what baptism meant, what's next (Discover More link, groups), and a request to reply with their story in a few sentences.

---

## 7. WORKFLOW 3 — QUESTION

### Step-by-step flow

1. **Minute 0 (SMS, instant):** "So glad you asked — questions are how everybody gets here. A real person will text you back today. Ask us anything; nothing is off limits."
2. **Minute 1 (internal):** alert Corey Alley + Dan Conklin. Tag as asked.
3. **Hour 1 (EMAIL, if email on file):** "While you wait" — three short links: sojo.church/yada.html (knowing God), sojo.church/gods-plan.html (the story), sojo.church/beliefs.html (what we believe).
4. **Same day (human):** a pastor answers the actual question personally. **No automated answer attempts — ever.** People asking questions get a person.
5. **Day 3 (SMS, only if the human conversation went quiet):** "Still chewing on anything? We're here — and if it's easier to talk than text, a pastor will gladly call. Just say the word."
6. **No further automation.** Close the loop by tag when resolved.

---

## 8. WORKFLOW 4 — HELLO (general contact)

### Step-by-step flow

1. **Minute 0 (SMS, instant):** "Hey — you've reached a real church with real people, and one of us will text you back today. What can we help with?"
2. **Minute 1 (internal):** alert **Audrie Cash** (audrie@sojourner.church — all general inquiries route to Audrie) + Corey Alley.
3. **Same day (human):** Audrie replies and routes (kids questions → Jillian, youth → Audrie, baptism → Workflow 2, etc.).
4. **Day 2 (SMS, only if no human reply was possible):** "So sorry for the wait — we haven't forgotten you. You'll hear from us today." (And escalate the internal alert to Corey.)
5. **No drip beyond that.** This is a front-desk flow, not a journey.

---

## 9. WORKFLOW 5 — PRAY (prayer requests)

### Step-by-step flow

1. **Minute 0 (SMS, instant):** "We've got you. Your request is going to our prayer team right now — and if you'd like a pastor to follow up personally, just reply CALL ME."
2. **Minute 1 (internal):** route the request text to Corey + the prayer team distribution (Corey will supply the team list). Tag `prayer-request`.
3. **"CALL ME" branch:** urgent alert to Corey; task created for same-day pastoral call.
4. **Day 3 (SMS):** "We've been praying for you all week at SOJO. Any update on what you shared? We'd love to keep praying specifically."
5. **Day 7 (EMAIL, if email on file, from Corey):** a short pastoral note on God hearing prayer (Corey supplies the copy), and an invitation: "You don't have to carry this alone — Sundays, 9 & 11am, Gibson Mill."
6. **Sensitivity rule:** nothing promotional in this flow, ever. These messages carry grief, diagnoses, and marriages. Plain text, human tone, no graphics, no upsells.

---

## 10. Sunday real-time requirements

- Keywords respond **within seconds** under burst load (Sept 6 altar call may produce dozens of texts in two minutes).
- JESUS and BAPTIZE staff alerts must hit pastors' **phones** (push/SMS), not just inboxes, so we can find people in the room before they leave the building.
- Auto-replies fire 24/7; scheduled rhythm messages respect quiet hours (7:00am–8:30pm ET).

## 11. Testing checklist (we'll run this together before Sept 6)

1. Text all five keywords from an unknown phone → instant replies, correct tags, correct staff alerts.
2. Send the exact website format ("JESUS - I just prayed to follow Jesus. My name is Test") → keyword still matches.
3. Confirm email-capture ask fires and saves the address.
4. Fast-forward-test the Day 1 email + Day 1 8pm text on a test contact.
5. Confirm a YES reply on JESUS Day 10 alerts a pastor and enrolls Workflow 2.
6. Confirm a manual pastor reply pauses conversational automation but not the daily journey.
7. Corey runs the website buttons on sojo.church/partner.html and /baptism.html end-to-end.

## 12. What we need back from Hello Church

1. **The confirmed live texting number** — first, before anything else, so we can update the website.
2. Confirmation of what's doable on our current plan (especially the 14-day dual-channel journey), and anything that isn't.
3. A build timeline — **minimum for Sunday, September 6: the five instant auto-replies + staff alerts live.** The 14-day journey can follow the week after if needed.

Thank y'all. This system is the front door for people's biggest spiritual decisions — build it like it matters, because it does.

— PC (Corey Alley), Lead Pastor, SOJO Church
