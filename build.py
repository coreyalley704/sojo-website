#!/usr/bin/env python3
# SOJO Church site builder — emits dist/ (multi-page) and preview.html (single-file, data URIs)
import os, re, base64, shutil, mimetypes

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SRC, 'out')
DIST = os.path.join(SRC, 'dist')

# ---------------------------------------------------------------- constants
ADDR1 = "325 McGill Ave NW, Suite 148"
ADDR2 = "Concord, NC 28027"
WAYF  = "The Kettle Room at Gibson Mill"

# Vision and mission — PC, Aug 2026. These supersede "Changing the world one person
# at a time" everywhere on the site.
VISION  = "A community with a cause"
MISSION = "Helping people know life, grow in peace, and go in purpose"
MOVE = "Sunday, September 6"
MAPS = "https://maps.google.com/?q=325+McGill+Ave+NW+Suite+148+Concord+NC+28027"

CC   = "https://sojo.churchcenter.com"
GIVE = CC + "/giving"
VISIT= CC + "/people/forms/484192"
# TODO(PC): replace with the real Discover SOJO event link. Until then this goes
# to the Church Center events list, where Discover SOJO is visible — never to the
# 90-Day Challenge event (3833678), which is what the old ID actually was.
DISC = CC + "/registrations/signups/3848051"   # Discover SOJO — real signup (PC, Aug 26)
DMORE = CC + "/registrations/signups/3848052"  # Discover More — real signup (PC, Aug 26)
GROUPS = CC + "/groups"
EVENTS = CC + "/registrations/events"
YT   = "https://www.youtube.com/c/SOJOChurch"
POD  = "https://www.buzzsprout.com/2369654"
FB   = "https://www.facebook.com/wearesojo.church/"
IG   = "https://www.instagram.com/sojo.church/"  # confirmed by PC, Aug 24 2026
LT   = "https://linktr.ee/wearesojo"
# TODO(PC): drop the real online-store URL here and every buy button on the site follows.
# Until that exists, buttons go to Church Center (a real, live page) and the page states
# plainly how to actually get a shirt. No button on this site is allowed to dead-end.
STORE = CC
STORE_LIVE = False
PHONE_D = "980-680-0958"
PHONE_H = "tel:+19806800958"
EMAIL_GENERIC = "audrie@sojourner.church"   # all general inquiries go to Audrie

# Hello Church texting — keyword-first bodies so auto-replies can match on the
# first word. Cross-platform sms: link form (iOS 8+ and Android both accept ?&body=).
def sms(keyword, message):
    from urllib.parse import quote
    return f"sms:+19804402850?&body={quote(keyword + ' - ' + message)}"  # Hello Church texting number (confirmed Aug 26)
SMS_JESUS   = sms("JESUS",   "I just prayed to follow Jesus. My name is ")
SMS_BAPTIZE = sms("BAPTIZE", "I want to be baptized. My name is ")
SMS_QUESTION= sms("QUESTION","I have a question about following Jesus. My name is ")
SMS_HELLO   = sms("HELLO",   "I'd like to talk with someone at SOJO. My name is ")

# Grouped navigation. Top level is a real link (works with no JS); the panel
# expands on hover or keyboard focus. Two of the five groups are named for the
# mission itself — GROW and GO — so the architecture teaches it.
NAV = [
    ("New Here",  "plan-a-visit.html", [
        ("Plan Your Visit",      "plan-a-visit.html"),
        ("Our New Home",         "new-home.html"),
        ("Watch &amp; Listen",   "watch.html"),
    ]),
    ("About",     "about.html", [
        ("Our Story",            "our-story.html"),
        ("Our Mission",          "mission.html"),
        ("Our Team",             "about.html"),
        ("Our Beliefs",          "beliefs.html"),
    ]),
    ("Next Gen",  "next-gen.html", [
        ("SOJO Kids",            "kids.html"),
        ("SOJO YTH",             "youth.html"),
        ("SOJO YA",              "next-gen.html#ya"),
    ]),
    ("Know",      "yada.html", [
        ("Yada &mdash; Knowing God", "yada.html"),
        ("God&rsquo;s Plan for Life","gods-plan.html"),
        ("Partner with Him",     "partner.html"),
        ("Baptism",              "baptism.html"),
    ]),
    ("Grow",      "next-steps.html", [
        ("Next Steps",           "next-steps.html"),
        ("Groups",               "groups.html"),
    ]),
    ("Go",        "serve.html", [
        ("Serve",                "serve.html"),
        ("Outreach &amp; Missions","missions.html"),
        ("SOJO Swag",            "swag.html"),
    ]),
]

FONTS = ("https://fonts.googleapis.com/css2?"
         "family=Big+Shoulders+Display:wght@300;400;500;600;700&"
         "family=Inter:wght@400;500;600;700&"
         "family=Roboto:wght@300;400;500&"
         "family=Caveat:wght@500;600&"
         "display=swap")

ICONS = {
 'fb':'<svg viewBox="0 0 24 24"><path d="M22 12a10 10 0 10-11.6 9.9v-7h-2.5V12h2.5V9.8c0-2.5 1.5-3.9 3.8-3.9 1.1 0 2.2.2 2.2.2v2.4h-1.2c-1.2 0-1.6.8-1.6 1.6V12h2.7l-.4 2.9h-2.3v7A10 10 0 0022 12z"/></svg>',
 'ig':'<svg viewBox="0 0 24 24"><path d="M12 2.2c3.2 0 3.6 0 4.9.1 1.2.1 1.8.2 2.2.4.6.2 1 .5 1.4.9.4.4.7.8.9 1.4.2.4.4 1 .4 2.2.1 1.3.1 1.7.1 4.9s0 3.6-.1 4.9c-.1 1.2-.2 1.8-.4 2.2-.2.6-.5 1-.9 1.4-.4.4-.8.7-1.4.9-.4.2-1 .4-2.2.4-1.3.1-1.7.1-4.9.1s-3.6 0-4.9-.1c-1.2-.1-1.8-.2-2.2-.4-.6-.2-1-.5-1.4-.9-.4-.4-.7-.8-.9-1.4-.2-.4-.4-1-.4-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.9c.1-1.2.2-1.8.4-2.2.2-.6.5-1 .9-1.4.4-.4.8-.7 1.4-.9.4-.2 1-.4 2.2-.4C8.4 2.2 8.8 2.2 12 2.2zm0 3.2A6.6 6.6 0 1018.6 12 6.6 6.6 0 0012 5.4zm0 10.9A4.3 4.3 0 1116.3 12 4.3 4.3 0 0112 16.3zm6.9-11.1a1.5 1.5 0 11-1.5-1.5 1.5 1.5 0 011.5 1.5z"/></svg>',
 'yt':'<svg viewBox="0 0 24 24"><path d="M23 7.5s-.2-1.6-.9-2.3c-.9-.9-1.9-.9-2.3-1C16.6 4 12 4 12 4s-4.6 0-7.8.2c-.4 0-1.4.1-2.3 1C1.2 5.9 1 7.5 1 7.5S.8 9.4.8 11.3v1.4C.8 14.6 1 16.5 1 16.5s.2 1.6.9 2.3c.9.9 2 .9 2.5 1 1.8.2 7.6.2 7.6.2s4.6 0 7.8-.2c.4 0 1.4-.1 2.3-1 .7-.7.9-2.3.9-2.3s.2-1.9.2-3.8v-1.4c0-1.9-.2-3.8-.2-3.8zM9.8 15.1V8.9l6 3.1-6 3.1z"/></svg>',
 'sp':'<svg viewBox="0 0 24 24"><path d="M12 2a10 10 0 100 20 10 10 0 000-20zm4.6 14.4a.62.62 0 01-.86.21c-2.35-1.44-5.3-1.76-8.79-.96a.62.62 0 11-.28-1.21c3.81-.87 7.08-.5 9.72 1.11.29.18.39.57.21.85zm1.23-2.74a.78.78 0 01-1.07.26c-2.69-1.65-6.79-2.13-9.97-1.17a.78.78 0 11-.45-1.49c3.63-1.1 8.15-.56 11.24 1.33.36.23.48.71.25 1.07zm.11-2.86C14.72 8.89 9.5 8.72 6.42 9.66a.93.93 0 11-.54-1.79c3.54-1.07 9.3-.87 12.96 1.3a.94.94 0 01-.96 1.61z"/></svg>',
 'lt':'<svg viewBox="0 0 24 24"><path d="M11 2h2v6.1l4.3-4.3 1.4 1.4L14.4 9.5H21v2h-6.6l4.3 4.3-1.4 1.4L13 12.9V22h-2v-9.1l-4.3 4.3-1.4-1.4 4.3-4.3H3v-2h6.6L5.3 5.2l1.4-1.4L11 8.1V2z"/></svg>',
}

# ---------------------------------------------------------------- helpers
# Portrait-orientation photos must never be cropped to a wide band on phones.
# Measure every image once at build time and tag the tall ones.
def _aspects():
    from PIL import Image as _I
    out = {}
    for root, _, files in os.walk(os.path.join(OUT, 'assets/img')):
        for f in files:
            if not f.endswith('.webp'): continue
            rel = os.path.relpath(os.path.join(root, f), os.path.join(OUT, 'assets/img'))
            try:
                w, h = _I.open(os.path.join(root, f)).size
                out[rel[:-5].replace(os.sep, '/')] = h / w
            except Exception:
                pass
    return out
ASPECT = _aspects()

def img(name, alt, cls="", extra=""):
    if ASPECT.get(name, 0) > 1.02 and 'portrait' not in cls:
        cls = (cls + ' tall').strip()
    return f'<img src="assets/img/{name}.webp" alt="{alt}" class="{cls}" loading="lazy" decoding="async" {extra}>'

def eager(name, alt, cls=""):
    if ASPECT.get(name, 0) > 1.02:
        cls = (cls + ' tall').strip()
    return f'<img src="assets/img/{name}.webp" alt="{alt}" class="{cls}" fetchpriority="high" decoding="async">'

def btn(label, href, kind="btn", ext=False):
    t = ' target="_blank" rel="noopener"' if ext else ''
    if href == VISIT:
        kind += " pyv-cta"
    return f'<a class="{kind}" href="{href}"{t}>{label}</a>'

# SOJO's YouTube uploads playlist. Embedding the *playlist* (not a video ID) means
# the newest upload is always first — the page updates itself every time you post.
YT_CHANNEL = "UCl0vhjkyMWlfSxOP8Tqsu3g"
YT_UPLOADS = "UU" + YT_CHANNEL[2:]
YT_EMBED = f"https://www.youtube-nocookie.com/embed/videoseries?list={YT_UPLOADS}&rel=0"
YT_PLAYLIST = f"https://www.youtube.com/playlist?list={YT_UPLOADS}"

def latest(label="This week's message from SOJO Church"):
    return (f'<div class="yframe"><iframe src="{YT_EMBED}" title="{label}" loading="lazy" '
            f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
            f'allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe></div>')

def testimony_section():
    """Giving stories. Emitted only when testimony-1.mp4 / testimony-2.mp4 exist
    in out/assets/video/ — the page never ships an empty player."""
    vids = [i for i in (1, 2)
            if os.path.exists(os.path.join(OUT, f'assets/video/testimony-{i}.mp4'))]
    if not vids:
        return ''
    frames = ''.join(
        f'<div class="vframe"><video controls preload="none" playsinline '
        f'poster="assets/img/testimony-{i}-poster.webp" '
        f'aria-label="A SOJO member shares their giving story">'
        f'<source src="assets/video/testimony-{i}.mp4" type="video/mp4"></video></div>'
        for i in vids)
    return ('<section class="sec dark grain"><div class="wrap">'
            '<p class="eyebrow">In their own words</p>'
            '<div class="split split-6535" style="align-items:end;margin-bottom:38px">'
            '<h2 class="display display-sm">What generosity<br>actually did</h2>'
            '<p class="lede">Not a theory and not a sermon &mdash; people from this church '
            'telling you what happened when they started giving.</p></div>'
            f'<div class="vgrid">{frames}</div>'
            '</div></section>')

VIDEO_SRC = 'assets/video/welcome.mp4' 
VIDEO_POSTER = 'assets/img/welcome-poster.webp'

def video(label="Welcome to SOJO"):
    return (f'<div class="vframe"><video controls preload="none" playsinline '
            f'poster="{VIDEO_POSTER}" aria-label="{label}">'
            f'<source src="{VIDEO_SRC}" type="video/mp4">'
            f'Your browser cannot play this video. '
            f'<a href="{VIDEO_SRC}">Download it instead.</a></video></div>')

def thread(movement, line):
    """The know/grow/go thread. Same mark on every page, never the same words."""
    return (f'<p class="thread"><span class="tx">'
            f'<span class="mv">{movement}</span>{line}</span></p>')

def gi(span, name, alt, label, note):
    return (f'<div class="{span}"><div class="gi-img">{img(name, alt)}</div>'
            f'<p class="gi-cap"><b>{label}</b>{note}</p></div>')

def rows(items):
    out = ['<div class="rows">']
    for i, (h, p, link) in enumerate(items, 1):
        l = f'<a class="link" href="{link[1]}"{" target=_blank rel=noopener" if link[2] else ""}>{link[0]} <span class="arw">→</span></a>' if link else ''
        out.append(f'<div class="row"><div class="num">{i:02d}</div><div class="rt"><div>'
                   f'<h3>{h}</h3><p>{p}</p></div>{l}</div></div>')
    out.append('</div>')
    return ''.join(out)

import json as _json
def faq_ld(items):
    import re as _re
    strip = lambda t: _re.sub(r'<[^>]+>', '', t).replace('&rsquo;', chr(8217)).replace('&ldquo;', chr(8220)).replace('&rdquo;', chr(8221)).replace('&mdash;', chr(8212)).replace('&middot;', chr(183)).replace('&amp;', '&')
    data = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":strip(q),"acceptedAnswer":{"@type":"Answer","text":strip(a)}} for q,a in items]}
    return '<script type="application/ld+json">' + _json.dumps(data) + '</script>'

def faq(items):
    out = ['<div class="faq">']
    for q, a in items:
        out.append(f'<details><summary>{q}</summary><div class="a">{a}</div></details>')
    out.append('</div>')
    return ''.join(out)

# ---------------------------------------------------------------- chrome
def header(active):
    CUR = ' aria-current="page"'
    def group(label, href, kids):
        items = ''.join(f'<a href="{h}">{n}</a>' for n, h in kids)
        on = any(h.split('#')[0] == active for _, h in kids) or href.split('#')[0] == active
        return (f'<div class="navgrp">'
                f'<a class="navtop" href="{href}"{CUR if on else ""}>{label}'
                f'<svg class="cv" viewBox="0 0 10 6" aria-hidden="true"><path d="M1 1l4 4 4-4" '
                f'fill="none" stroke="currentColor" stroke-width="1.4"/></svg></a>'
                f'<div class="navpanel"><div class="navpanel-in">{items}</div></div></div>')
    nav = ''.join(group(l, h, k) for l, h, k in NAV)
    CHEV = ('<svg class="mchev" viewBox="0 0 10 6" aria-hidden="true">'
            '<path d="M1 1l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>')
    mnav = ''.join(
        f'<details class="mgrp"><summary class="mgrp-h">{l}{CHEV}</summary>'
        + ''.join(f'<a href="{h}">{n}</a>' for n, h in k) + '</details>'
        for l, h, k in NAV) + '<div class="mgrp"><a class="mgrp-solo" href="give.html">Give</a></div>'

    return f'''
<div class="movebar" id="movebar"><div class="wrap">
  <span class="countpill" id="countpill">WE MOVE {MOVE.upper()}</span>
  <span>New home: <a href="new-home.html">{WAYF}</a> — {ADDR1}, {ADDR2}</span>
</div></div>
<header class="hdr">
  <div class="wrap hdr-in">
    <a class="brand" href="index.html" aria-label="SOJO Church home">
      <img src="assets/img/brand/stack-charcoal.webp" alt="SOJO Church" width="86" height="104">
    </a>
    <nav class="main" aria-label="Main">{nav}</nav>
    <div style="display:flex;gap:10px;align-items:center">
      <a class="btn hdr-give" href="give.html">Give</a>
      <button class="burger" aria-label="Menu" aria-expanded="false" id="burger"><span></span><span></span><span></span></button>
    </div>
  </div>
  <div class="mnav" id="mnav">{mnav}</div>
</header>'''

def footer():
    soc = ''.join(f'<a href="{u}" target="_blank" rel="noopener" aria-label="{n}">{ICONS[k]}</a>'
                  for k, n, u in [('fb','Facebook',FB),('ig','Instagram',IG),('yt','YouTube',YT),
                                  ('sp','Podcast',POD),('lt','Linktree',LT)])
    return f'''
<footer class="ftr grain">
  <div class="wrap">
    <div class="ftr-top">
      <div>
        <img class="logo" src="assets/img/brand/stack-cream.webp" alt="SOJO Church" width="86" height="104">
        <address class="addr-s">
          <strong style="color:var(--gold-bright);font-weight:500">{WAYF}</strong><br>
          {ADDR1}<br>{ADDR2}<br>
          <a href="{MAPS}" target="_blank" rel="noopener">Get directions →</a>
        </address>
        <div class="socials">{soc}</div>
      </div>
      <div>
        <h5>Sundays</h5>
        <ul>
          <li>9:00am &amp; 11:00am</li>
          <li><a href="plan-a-visit.html">Plan your visit</a></li>
          <li><a href="new-home.html">Find the room</a></li>
          <li><a href="watch.html">Watch online</a></li>
        </ul>
      </div>
      <div>
        <h5>Take a step</h5>
        <ul>
          <li><a href="next-steps.html">Next steps</a></li>
          <li><a href="partner.html">Follow Jesus</a></li>
          <li><a href="baptism.html">Baptism</a></li>
          <li><a href="next-gen.html">Next Gen</a></li>
          <li><a href="kids.html">SOJO Kids</a></li>
          <li><a href="youth.html">SOJO YTH</a></li>
          <li><a href="young-adults.html">SOJO YA</a></li>
          <li><a href="serve.html">Serve</a></li>
          <li><a href="missions.html">Outreach &amp; missions</a></li>
          <li><a href="swag.html">Swag</a></li>
          <li><a href="groups.html">Groups</a></li>
          <li><a href="give.html">Give</a></li>
        </ul>
      </div>
      <div>
        <h5>Talk to a human</h5>
        <ul>
          <li><a href="{SMS_HELLO}">Text us &mdash; a human replies</a></li>
          <li><a href="{PHONE_H}">Or call {PHONE_D}</a></li>
          <li><a href="mailto:{EMAIL_GENERIC}">{EMAIL_GENERIC}</a></li>
          <li><a href="{VISIT}" target="_blank" rel="noopener">Tell us you're coming</a></li>
          <li><a href="our-story.html">Our story</a></li>
          <li><a href="mission.html">Our mission</a></li>
          <li><a href="about.html">Our team</a></li>
          <li><a href="beliefs.html">Our beliefs</a></li>
          <li><a href="{EVENTS}" target="_blank" rel="noopener">Church calendar</a></li>
        </ul>
        <p class="tagline">A community with a cause.</p>
        <p class="mission-line">You were made to <b>know</b> Life and have it abundantly, <b>grow</b> in peace with God and people, and <b>go</b> in your anointed purpose to help bring heaven to earth.</p>
        <p style="margin-top:14px"><a href="mission.html" style="font-family:var(--f-label);font-size:.76rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--gold-bright);text-decoration:none">Our mission &rarr;</a></p>
      </div>
    </div>
    <div class="ftr-bot">
      <span>© 2026 SOJO Church · Concord, NC</span>
      <span>Sundays 9 &amp; 11am</span>
    </div>
  </div>
</footer>
<script>
(function(){{
  var b=document.getElementById('burger'), m=document.getElementById('mnav');
  if(b){{b.addEventListener('click',function(){{
    var o=m.classList.toggle('open'); b.setAttribute('aria-expanded',o?'true':'false');
    if(o){{m.style.maxHeight=(window.innerHeight-m.getBoundingClientRect().top)+'px';}}
  }});}}
  document.addEventListener('click', function(e){{
    var t = e.target.closest ? e.target.closest('.pyv-cta') : null;
    if (t && typeof window.showVisitPlanner === 'function') {{
      e.preventDefault(); window.showVisitPlanner();
    }}
  }});
  var pill=document.getElementById('countpill');
  if(pill){{
    var move=new Date(2026,8,6,9,0,0), now=new Date();
    var d=Math.ceil((move-now)/86400000);
    if(d>1) pill.textContent=d+' DAYS UNTIL WE MOVE';
    else if(d===1) pill.textContent='WE MOVE TOMORROW';
    else if(d===0) pill.textContent='TODAY — SEE YOU AT THE MILL';
    else {{ pill.textContent="WE'RE HOME"; }}
  }}
}})();
</script>'''

LAYOUT = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{fonts}" rel="stylesheet">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-F034W7H72Y"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-F034W7H72Y');</script>
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="assets/icons/favicon-32.png" type="image/png" sizes="32x32">
<link rel="icon" href="assets/icons/icon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="assets/icons/apple-touch-icon.png">
<meta name="theme-color" content="#BFAE86">
<script type="text/javascript">window.pyvAccountKey = 'Z84WYfwJ'; window.pyvDomain = 'https://lite.visitplanner.church'; var pyvs = document.createElement('script'); pyvs.async = true; pyvs.type = 'text/javascript'; pyvs.src = 'https://lite.visitplanner.church/embed/embed.js'; document.head.appendChild(pyvs);</script>
<link rel="stylesheet" href="assets/css/site.css">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{header}
<main id="main">
{body}
</main>
{footer}
</body>
</html>'''

LD = f'''<script type="application/ld+json">{{
"@context":"https://schema.org","@graph":[
{{"@type":"Church","@id":"https://sojo.church/#church","name":"SOJO Church",
"alternateName":"SOJO","url":"https://sojo.church/",
"description":"SOJO Church is a non-denominational church in Concord, NC meeting Sundays at 9 & 11am in The Kettle Room at Gibson Mill. A community with a cause: helping people know life, grow in peace, and go in purpose.",
"slogan":"A community with a cause",
"telephone":"+1-980-680-0958",
"foundingDate":"2017",
"founder":{{"@type":"Person","name":"Corey Alley","jobTitle":"Lead Pastor"}},
"address":{{"@type":"PostalAddress","streetAddress":"325 McGill Ave NW, Suite 148","addressLocality":"Concord","addressRegion":"NC","postalCode":"28027","addressCountry":"US"}},
"areaServed":["Concord NC","Kannapolis NC","Harrisburg NC","Charlotte NC","Cabarrus County"],
"sameAs":["{FB}","{IG}","{YT}","{POD}","{LT}"],
"openingHoursSpecification":[{{"@type":"OpeningHoursSpecification","dayOfWeek":"Sunday","opens":"09:00","closes":"12:30"}}],
"logo":"https://sojo.church/assets/icons/icon-512.png","image":"https://sojo.church/assets/img/social.jpg"}},
{{"@type":"WebSite","@id":"https://sojo.church/#website","url":"https://sojo.church/","name":"SOJO Church","publisher":{{"@id":"https://sojo.church/#church"}}}}
]}}</script>'''

BASE_URL = "https://sojo.church/"

KEYWORDS = {
    'index.html': 'church in Concord NC, SOJO Church, churches near me, Gibson Mill church, non-denominational church Concord, Sunday service Concord NC',
    'plan-a-visit.html': 'visit a church in Concord NC, plan your visit, first time church visit, what to wear to church, church near Gibson Mill',
    'new-home.html': 'Gibson Mill church, Kettle Room Gibson Mill, church on McGill Ave Concord, SOJO Church new location',
    'mission.html': 'church mission statement, know life grow in peace go in purpose, community with a cause, SOJO Church beliefs',
    'our-story.html': 'SOJO Church history, church plant Concord NC, Corey Alley pastor, church story',
    'next-gen.html': 'kids ministry Concord NC, youth group Concord NC, young adults ministry Concord, children church near me',
    'kids.html': 'kids ministry Concord NC, church nursery Concord, children ministry near me, SOJO Kids',
    'youth.html': 'youth group Concord NC, middle school youth group, high school ministry Concord, Wednesday youth night',
    'young-adults.html': 'young adults ministry Concord NC, college ministry Concord, 20s and 30s church group, young adult group near me',
    'about.html': 'about SOJO Church, Concord NC church staff, Corey Alley lead pastor, non-denominational church',
    'next-steps.html': 'get baptized Concord NC, join a church Concord, new believer class, discover SOJO',
    'groups.html': 'small groups Concord NC, church small group near me, grief support group Concord, divorce care Concord NC, recovery group church',
    'serve.html': 'volunteer at church Concord NC, serve team church, church volunteering near me',
    'missions.html': 'church missions Concord NC, local outreach Concord, church planting North Carolina, mission partners',
    'give.html': 'church giving, tithing, online giving church Concord NC, generosity challenge',
    'watch.html': 'church online Concord NC, watch sermons online, SOJO Church sermons, church podcast',
    'beliefs.html': 'what we believe SOJO Church, church beliefs Concord NC, doctrinal statement, statement of faith Concord church, Bible believing church near me',
    'swag.html': 'SOJO Church merch, church t-shirts Concord NC, SOJO swag',
    'yada.html': 'knowing God, yada Hebrew meaning, know God personally, experiential knowledge of God, relationship with God Concord NC',
    'gods-plan.html': 'God\'s plan for my life, abundant life John 10:10, purpose of life Bible, Psalm 1 meaning, way of Jesus',
    'partner.html': 'how to become a Christian, follow Jesus, salvation prayer, apprentice of Jesus, give my life to Jesus Concord NC',
    'baptism.html': 'get baptized Concord NC, water baptism meaning, believer\'s baptism, how to be baptized, baptism near me',
}

def page(slug, title, desc, body, active=None, ld=False):
    canon = BASE_URL if slug == 'index.html' else BASE_URL + slug
    kw = KEYWORDS.get(slug, KEYWORDS['index.html'])
    seo = (f'<link rel="canonical" href="{canon}">\n'
           f'<meta name="keywords" content="{kw}">\n'
           f'<meta property="og:url" content="{canon}">\n'
           f'<meta property="og:site_name" content="SOJO Church">\n'
           f'<meta property="og:locale" content="en_US">\n'
           f'<meta property="og:image" content="{BASE_URL}assets/img/social.jpg">\n'
           f'<meta property="og:image:width" content="1200">\n'
           f'<meta property="og:image:height" content="630">\n'
           f'<meta name="twitter:card" content="summary_large_image">\n'
           f'<meta name="twitter:image" content="{BASE_URL}assets/img/social.jpg">')
    html = LAYOUT.format(title=title, desc=desc, fonts=FONTS,
                         header=header(active or slug), body=body,
                         footer=footer(), ld=LD + '\n' + seo)
    return slug, html

# ---------------------------------------------------------------- pages
PAGES = []

# ============================== HOME =========================================
home = f'''
<section class="hero grain dark">
  <div class="hero-img">{eager('hero','SOJO Church gathered in worship on a Sunday morning')}</div>
  <div class="wrap hero-in">
    <p class="eyebrow">Concord, North Carolina · Sundays 9 &amp; 11am</p>
    <h1 class="display display-xl">
      <span class="script">You were</span>
      Made for<br>more
    </h1>
    <p class="lede lede-mission">You were made to <span class="mv">know</span> Life and have it
    abundantly, <span class="mv">grow</span> in peace with God and people, and
    <span class="mv">go</span> in your anointed purpose to help bring heaven to earth.</p>
    <div class="btns">
      {btn('Plan your first visit','plan-a-visit.html')}
      {btn('Watch a message','watch.html','btn btn-ghost')}
    </div>
    <div class="hero-meta">
      <span>Sundays <b>9 &amp; 11am</b></span>
      <span>From Sept 6 · <b>{WAYF}</b></span>
      <span><b>{ADDR1}</b></span>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="eyebrow">Our mission</p>
    <div class="split split-6535" style="align-items:end">
      <h2 class="display display-sm">Know life.<br>Grow in peace.<br>Go in purpose.</h2>
      <p class="lede">Three movements, and they run in that order. Everything we do fits under
      one of them &mdash; or we stop doing it.</p>
    </div>
    {rows([
      ("Know life",
       "Finding family. Finding community. And more than anything, finding Jesus among His people &mdash; and finding His plan for your life. Life is not an achievement you unlock; it is a Person you meet, and you almost never meet Him alone.",
       ("Read the whole thing","mission.html",False)),
      ("Grow in peace",
       "Peace with God first, then peace worked into you &mdash; in a group, through personal study and prayer, with people who have permission to ask you the hard question. Slow, on purpose, and impossible in a crowd.",
       ("Find a group","groups.html",False)),
      ("Go in purpose",
       "What the first two look like when they overflow &mdash; into your home, your church, your work, your friends and neighbors. And through the church, into service and giving, where your money does what it could never do alone.",
       ("Find your spot","serve.html",False)),
    ])}
    <div class="btns">{btn('How the mission works','mission.html')}</div>
  </div>
</section>

<section class="sec tint">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">Two minutes</p>
      <h2 class="display display-sm">Meet SOJO<br>before you<br>walk in</h2>
      <p class="lede">Press play. It is the fastest way to find out whether this is your kind of
      church without giving up a Sunday to find out.</p>
      <p>You will hear what we are about, see the people you would be sitting next to, and know what
      Sunday morning actually feels like before you ever park the car.</p>
      <div class="btns">{btn('Want to know what a Sunday looks like? Click here','plan-a-visit.html')}</div>
    </div>
    {video("Welcome to SOJO Church")}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="eyebrow">Where to go next</p>
    <h2 class="display display-sm">Four steps,<br>in order</h2>
    <div class="trio trio-4">
      <div>{img('greeting','Guests being welcomed in the SOJO lobby')}
        <h3>1 · Come for the first time</h3>
        <p>Show up on a Sunday. That is the entire first step &mdash; no sign-up, no dressing up,
        no knowing anybody.</p>
        <a class="link" href="plan-a-visit.html">Plan a visit <span class="arw">&rarr;</span></a></div>
      <div>{img('c-park','SOJO families together at a community gathering')}
        <h3>2 · Try 5</h3>
        <p>Five Sundays. Not to size up a stage &mdash; to meet the people. That is the part that
        actually changes anything.</p>
        <a class="link" href="next-steps.html">Why five <span class="arw">&rarr;</span></a></div>
      <div>{img('st-union-toddler','A meal being served at a SOJO gathering')}
        <h3>3 · Come to Discover SOJO</h3>
        <p>Last Sunday of every month, right after second service. A real meal, childcare, and every
        question you have got.</p>
        <a class="link" href="{DISC}" target="_blank" rel="noopener">Sign up <span class="arw">&rarr;</span></a></div>
      <div>{img('n-dan-teach','Pastor Dan teaching at SOJO Church')}
        <h3>4 · Attend Discover More</h3>
        <p>A three-week virtual class on basic doctrine and discipleship. What we believe, and what
        following Jesus actually looks like.</p>
        <a class="link" href="next-steps.html">See both tracks <span class="arw">&rarr;</span></a></div>
    </div>
  </div>
</section>

<section class="sec dark grain">
  <div class="wrap">
    <p class="eyebrow">From last Sunday</p>
    <div class="split split-6535" style="align-items:end;margin-bottom:38px">
      <h2 class="display display-sm">Hear the<br>latest message</h2>
      <p class="lede">Updates itself every week. Whatever we said on Sunday is right here by Monday.</p>
    </div>
    {latest()}
    <div class="btns">{btn('More messages','watch.html')}
      {btn('Listen to the podcast',POD,'btn btn-ghost',True)}</div>
  </div>
</section>

<section class="sec concrete grain columns sheen">
  <div class="wrap">
    <hr class="lane" style="margin-bottom:48px">
    <p class="eyebrow">The next chapter</p>
    <div class="split split-6535" style="align-items:end">
      <h2 class="display">We're<br><span class="gold">home</span></h2>
      <p class="lede">Same family. Same mission. A room twice the size &mdash; and on September 6
      we filled it.</p>
    </div>
    <div class="gal">
      <div class="g-half">{img('fs-worship-columns','The SOJO congregation worshipping among the original mill columns at the Kettle Room')}</div>
      <div class="g-half">{img('fs-communion-pass','Communion passed down the rows on the first Sunday at Gibson Mill')}</div>
      <div class="g-third">{img('fs-cafe-neon','The neon SOJO sign glowing on the brick wall of the cafe area')}</div>
      <div class="g-third">{img('fs-kids-checkin','A family welcomed at the SOJO Kids check-in on Sunday morning')}</div>
      <div class="g-third">{img('fs-couple-cross','A couple holding hands in worship with the cross in the window light')}</div>
    </div>
    <p class="figcap" style="margin-top:16px">First Sunday at the Kettle Room &middot; September 6, 2026.</p>
    <div class="bignums">
      <div class="bignum"><b>400+</b><span>Seats, up from 230</span></div>
      <div class="bignum"><b>2×</b><span>The space we have now</span></div>
      <div class="bignum"><b>400%</b><span>More room for kids &amp; youth</span></div>
      <div class="bignum"><b>2027</b><span>Coffee shop &amp; permanent kids space</span></div>
    </div>
    <div class="btns">{btn('Everything about the new home','new-home.html','btn')}
      {btn('Get directions',MAPS,'btn btn-ghost',True)}</div>
  </div>
</section>

<section class="sec">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">First things first</p>
      <h2 class="display display-sm">We're <span class="ul">glad</span><br>you're here</h2>
      <p class="lede">You don't have to dress up. You don't have to know anybody. You don't have to
      have your life figured out, your questions answered, or your past cleaned up.</p>
      <p>SOJO started in Corey and Betsy Alley's living room in 2017 with a simple conviction: a church
      shouldn't exist for itself. If we closed our doors tomorrow, our city should miss us — not just
      the people who show up on Sunday.</p>
      <p>Nine years in, that is still the whole thing. We are <strong>a community with a
      cause</strong> &mdash; and the cause is people. Helping them <strong>know life, grow in peace,
      and go in purpose</strong>.</p>
      <div class="stripe" aria-hidden="true"></div>
      <a class="link" href="about.html">Our story <span class="arw">→</span></a>
    </div>
    <div class="figure">
      {img('n-baptism-hug','A soaking-wet baptism hug at SOJO Church')}
      <p class="figcap">Fresh out of the tank · SOJO Church</p>
    </div>
  </div>
</section>

<section class="sec tint">
  <div class="wrap split">
    <div class="figure">{img('fs-hands-stage','Hands lifted toward the stage in worship at the Kettle Room')}</div>
    <div>
      <p class="eyebrow">Try five</p>
      <h2 class="display display-sm">Give us five<br>Sundays</h2>
      <p class="lede">Not to size up a stage. To meet the people.</p>
      <p>One visit tells you whether you like the music. Five tells you whether these are your people —
      and that's the part that actually changes anything. Church is more than a moment on a stage.
      It's a community you grow into.</p>
      <p>Our hope isn't that SOJO becomes a place you attend. It's that it becomes a place that feels
      like home.</p>
      <div class="btns">{btn("Plan your first Sunday",'plan-a-visit.html')}</div>
    </div>
  </div>
</section>

<section class="sec sand">
  <div class="wrap loc">
    <div>
      <p class="eyebrow">Find us Sunday</p>
      <p class="venue">{WAYF}</p>
      <p class="addr">{ADDR1}<br>{ADDR2}
        <span class="sub">Sundays at 9:00 &amp; 11:00am</span></p>
      <div class="btns">{btn('Get directions',MAPS,'btn',True)}
        {btn('How to find the room','new-home.html','btn btn-ghost')}</div>
    </div>
    <div class="figure">{img('millsign','The historic Gibson Mill sign in Concord, North Carolina')}
      <p class="figcap">Gibson Mill · Concord, NC</p></div>
  </div>
</section>
'''
PAGES.append(page('index.html', 'SOJO Church — Concord, NC | Sundays 9 & 11am',
    'You were made to know life, grow in peace, and go in purpose. SOJO Church — Sundays 9 & 11am at Gibson Mill, Concord NC.',
    home, active='index.html', ld=True))

# ============================== PLAN A VISIT =================================
visit = f'''
<section class="phero grain dark">
  <div class="phero-img">{eager('fs-family-arrive','A family walking in with a SOJO greeter on Sunday morning')}</div>
  <div class="wrap">
    <p class="crumb">New Here</p>
    <h1 class="display"><span class="script">There's a seat</span><br>at the table</h1>
    <p class="lede">Everything you need to know before Sunday — and nothing you don't.</p>
    {thread('Know','Life is a Person, and most people meet Him surrounded by other people. That is all a first Sunday is for &mdash; not a decision, just a room.')}
    <div class="btns">{btn("Tell us you're coming",VISIT,'btn',True)}
      {btn('Get directions',MAPS,'btn btn-ghost',True)}</div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="split split-6535">
      <div>
        <p class="eyebrow">The short version</p>
        <h2 class="display display-sm">Sundays at<br>9 &amp; 11am</h2>
        <p class="lede">We meet at {WAYF} — {ADDR1}, {ADDR2}.</p>
        <p>Park in the SOJO lot to your right as you come through the main Gibson Mill entrance and
        follow the signs. Our entrance is beside the City Club entrance, under the big SOJO Church
        sign. Head straight down the hall to the end. Somebody will be there.</p>
        <div class="stripe" aria-hidden="true"></div>
        <a class="link" href="new-home.html">See photos of the new space <span class="arw">→</span></a>
      </div>
      {video("Welcome to SOJO Church")}
    </div>
  </div>
</section>

<section class="sec tint">
  <div class="wrap">
    <p class="eyebrow">Honest answers</p>
    <h2 class="display display-sm">The things you're<br>actually wondering</h2>
    {faq([
      ("What do I wear?",
       "<p>Whatever you're comfortable in. Jeans and a t-shirt is the norm. If you want to dress up, great — nobody will think twice either way.</p>"),
      ("Where do I park?",
       f"<p>Come through the main Gibson Mill entrance and look right — SOJO parking is on that side, marked with our directional signs. First-time guest spots are up front. Our team will be outside in vests to help you find a spot and point you to the door.</p><p><a class='link' href='new-home.html'>See the Gibson Mill site map <span class='arw'>→</span></a></p>"),
      ("How do I actually get in the building?",
       "<p>Our entrance is right beside the City Club entrance — look for the large SOJO Church sign mounted at the top of the building. Once inside, walk straight down the hallway to the end. Guest Services will be waiting there.</p>"),
      ("How long is the service?",
       "<p>About 75 minutes. Doors open 30 minutes before each service, and there's coffee.</p>"),
      ("What happens in a service?",
       "<p>Live worship music, a message straight out of the Bible that connects to real life, and space to pray or talk with somebody if you want to. You will never be singled out, asked to stand, or put on the spot.</p>"),
      ("Will somebody make me give money?",
       "<p>No. There's an offering as part of the service because generosity is part of following Jesus — but it's for people who call SOJO home. As our guest, you're off the hook. Keep your wallet in your pocket.</p>"),
      ("What about my kids?",
       f"<p>SOJO Kids runs during both services, newborn through 5th grade. Every volunteer is background-checked and trained, and our secure check-in means only you can pick your child up. First-time families check in at the guest station just outside the SOJO Kids entrance.</p><p><a class='link' href='kids.html'>All about SOJO Kids <span class='arw'>→</span></a></p>"),
      ("I'm coming alone. Is that weird?",
       "<p>Not even slightly. A lot of people walk in by themselves the first time. Find the First-Time Guest table in the lobby and we'll take it from there.</p>"),
      ("I'm not sure what I believe.",
       "<p>Good — bring the questions. Doubt isn't a disqualifier here. Plenty of people at SOJO are still working it out, and nobody is going to corner you about it.</p>"),
    ])}
  </div>
</section>

<section class="sec">
  <div class="wrap split">
    <div class="figure">{img('c-dunked','A SOJO guest welcomed at the first-time guest table')}</div>
    <div>
      <p class="eyebrow">Your first Sunday</p>
      <h2 class="display display-sm">Find the<br>guest table</h2>
      <p class="lede">It's in the lobby. It's not a trap.</p>
      <p>A real person who wants to say hello, answer whatever you want to ask, and put a small gift in
      your hands. No sign-up sheet, no follow-up ambush, no standing up in front of the room.</p>
      <p>If you'd rather we know you're coming ahead of time, tell us — we'll look for you and have
      somebody meet you at the door.</p>
      <div class="btns">{btn("Tell us you're coming",VISIT,'btn',True)}
        {btn('Call or text us',PHONE_H,'btn btn-ghost')}</div>
    </div>
  </div>
</section>

<section class="sec dark grain center">
  <div class="wrap-narrow">
    <p class="script">Still deciding?</p>
    <h2 class="display display-sm">Watch one first</h2>
    <p class="lede">Every message goes online. Get a feel for it from your couch, then come see the room.</p>
    <div class="btns" style="justify-content:center">{btn('Watch a message','watch.html')}
      {btn('Listen to the podcast',POD,'btn btn-ghost',True)}</div>
  </div>
</section>
'''
PAGES.append(page('plan-a-visit.html', 'Plan Your Visit | SOJO Church, Concord NC',
    'What to expect on your first Sunday at SOJO Church in Concord, NC — parking, kids, '
    'what to wear, and how long the service lasts.', visit))

# ============================== NEW HOME =====================================
newhome = f'''
<section class="phero grain dark">
  <div class="phero-img">{eager('fs-worship-wide','Hands raised in worship at the Kettle Room with gold light through the mill windows')}</div>
  <div class="wrap">
    <p class="crumb">Our New Home</p>
    <h1 class="display"><span class="script">The next chapter</span><br>Gibson Mill</h1>
    <p class="lede">We're in. Sundays at 9 &amp; 11am in the Kettle Room.</p>
    {thread('Know &middot; Grow &middot; Go','One room where a stranger meets Life, a family gets formed, and a church gets sent. That is what we are building at the Mill.')}
    <div class="btns">{btn('Get directions',MAPS,'btn',True)}
      {btn('Plan your visit','plan-a-visit.html','btn btn-ghost')}</div>
  </div>
</section>

<section class="sec">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">A letter from Pastor Corey</p>
      <h2 class="display display-sm">He doesn't restore<br>things halfway</h2>
      <p class="lede">SOJO family — I've been dreaming about this moment for a long time.</p>
      <p>There is something deeply sacred about a community gathering in a historic space. A place that
      carried stories before us and will carry ours forward for generations.</p>
      <p>Scripture says it plainly: <em>be fruitful, multiply, fill the earth.</em> That's not just a
      command about land. It's a declaration about what God does with His people when they say yes.
      He restores. He expands. He takes what was worn down and breathes something new into it.
      That is our story.</p>
      <p>Here's what it means in real terms. We're moving into a space twice the size of what we have
      now. Our room grows from 230 seats to 400+. Our kids and youth spaces grow by 400% — safer, more
      beautiful, more intentional than anything we've had.</p>
      <p>Some of it lands on day one. Some of it doesn't. The permanent kids space and a fully built-out
      coffee shop are both targeted for early 2027 — a coffee shop open through the week, where somebody
      who has never set foot in a church finds us on a Wednesday afternoon. We're telling you the
      timeline honestly because you deserve that more than you deserve a nice rendering.</p>
      <p>I believe with everything in me that God put this in front of SOJO for a reason. So pray over
      it, then ask Him one question: <strong>what is my part in this?</strong></p>
      <p style="font-family:var(--f-script);font-size:1.9rem;color:var(--gold-deep);line-height:1.1;margin-top:28px">
      With faith and gratitude,<br>Pastor Corey</p>
    </div>
    <div class="figure figure-portrait">{img('pc','Pastor Corey Alley, Lead Pastor of SOJO Church','portrait')}
      <p class="figcap">Corey Alley · Lead Pastor</p></div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="eyebrow">September 6, 2026 · First Sunday</p>
    <div class="split split-6535" style="align-items:end">
      <h2 class="display display-sm">And then<br>we filled it</h2>
      <p class="lede">A hundred-year-old room, full again. Two services, every generation, communion
      passed hand to hand down the rows. This is what the whole build was for.</p>
    </div>
    <div class="gal gal-cap">
      {gi('g-half','fs-band','The SOJO worship team leading from the new stage at the Kettle Room','The worship team','Leading from the new stage, first service in the room.')}
      {gi('g-half','fs-sojo-lift','A man in a SOJO shirt with both arms lifted in worship','Both hands','No caption needed.')}
      {gi('g-third','fs-cafe-lounge','Couches and tables in the SOJO gathering space at Gibson Mill','The gathering space','Couches, tables, and room to actually sit down with somebody.')}
      {gi('g-third','fs-couple-pray','A couple with heads bowed in prayer during the service','Prayer in the rows','First prayers prayed in the new room.')}
      {gi('g-third','fs-communion-trays','Copper communion trays stacked on a table before the service','The table set','Communion, ready before the room filled.')}
    </div>
  </div>
</section>

<section class="sec concrete grain columns curtains sheen">
  <div class="wrap">
    <p class="eyebrow">August 2026 · The shell</p>
    <div class="split split-6535" style="align-items:end">
      <h2 class="display display-sm">This is what<br>it looked like<br><span class="gold">one month before</span></h2>
      <p class="lede">Bare brick. Columns painted over a dozen times. A hundred years of somebody
      else's work still on the ceiling. We're not covering that up — we're building inside it.</p>
    </div>
    <div class="gal gal-cap">
      {gi('g-wide','shell-wide','The empty mill floor at Gibson Mill with tall windows and painted steel columns','The worship room','Where the chairs go. Tall windows down the long wall, original steel columns left exactly where they are.')}
      {gi('g-half','shell-columns','Rows of steel columns down the length of the mill floor','Looking down the floor','The full length of the space, front to back. Every column is original to the mill.')}
      {gi('g-third','shell-lights','Original ceiling and hanging lights in the mill space','The ceiling','Original timber and hanging fixtures. We are keeping them.')}
      {gi('g-third','shell-windows','Tall curtained windows along the brick wall','The window wall','Daylight down one whole side. The curtains stay.')}
      {gi('g-third','shell-corridor','Warm lit corridor along the whitewashed brick wall','The hallway in','The walk from the main entrance. Follow it to the end and Guest Services meets you.')}
      {gi('g-half','shell-doorway','Looking through a doorway into the main mill floor','The doorway','First look into the room from the hall.')}
      {gi('g-half','shell-frame1','New wall framing going up in the future kids space','Kids and youth, framed','The build-out in progress. Permanent kids space targets early 2027.')}
    </div>
    <p class="figcap" style="margin-top:18px">Photographed August 2026. The framing you can see going
    up is the kids and youth build-out.</p>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="eyebrow">The plan</p>
    <div class="split split-6535" style="align-items:end">
      <h2 class="display display-sm">And this is<br>what it becomes</h2>
      <p class="lede">Same bones. Same brick. Chairs, sound, light, and four hundred people who
      didn't have a room big enough until now.</p>
    </div>
    <div class="gal gal-cap">
      {gi('g-half','r-room','Rendering of the new SOJO worship room','The worship room','400+ seats, up from 230. Ready September 6.')}
      {gi('g-half','r-lobby','Rendering of a gathering space with brick walls and long tables','Gathering space','Brick, daylight, long tables. Room to sit down with somebody after a service.')}
      {gi('g-third','r-cafe','Rendering of the café and coffee area','The café area','The fully built-out coffee shop is targeted for early 2027 — not open on day one.')}
      {gi('g-third','r-patio','Rendering of the building exterior with SOJO Church signage','Outside the door','Our signage on the mill brick. This is what you look for from the parking lot.')}
      {gi('g-third','r-deck','Rendering of the outdoor deck at Gibson Mill','Open air','Outdoor space at the Mill. Phased in after the move.')}
    </div>
    <p class="figcap" style="margin-top:18px">These are renderings, not photographs. Construction is
    ongoing and areas open in phases — the captions say which.</p>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="eyebrow">Getting there</p>
    <h2 class="display display-sm">How to find<br>the room</h2>
    <div class="split split-6535" style="margin-bottom:clamp(40px,5vw,64px);align-items:start">
      <div class="figure">{img('mill-map','Site map of Gibson Mill showing the SOJO parking areas and main entrance')}
        <p class="figcap">Gibson Mill site map &mdash; SOJO parking and the main entrance</p></div>
      <div>
        <p class="eyebrow" style="margin-top:0">Read the map</p>
        <p>Come in off McGill Avenue and you are looking at the whole property. <strong>SOJO parking
        is to your right</strong> as you come through the main entrance, and our team will be out
        there in vests pointing you in. First-time guest spots are up front.</p>
        <p>Our door sits beside the <strong>City Club entrance</strong>, under the large SOJO Church
        sign mounted at the top of the building. Inside, walk straight down the hallway to the end.</p>
        <p class="muted">Not sure? Roll your window down and ask anybody in a vest. That is
        literally their whole job on Sunday morning.</p>
        <div class="figure" style="margin-top:22px">{img('fs-parking-team','Three SOJO parking team members in yellow vests waving cars in')}
          <p class="figcap">The vest crew, ready to wave you in.</p></div>
      </div>
    </div>
    {rows([
      ("Put this in your GPS",
       f"{ADDR1}, {ADDR2}. If your map app is confused, search &ldquo;Gibson Mill Concord&rdquo; and head for the main entrance.",
       ("Open directions",MAPS,True)),
      ("Park to the right",
       "Come through the main Gibson Mill entrance and SOJO parking is primarily on your right. Follow the SOJO directional signs — our team is out there and will point you in.",
       None),
      ("Look for the sign beside City Club",
       "Our entrance sits right next to the City Club entrance, with the large SOJO Church sign mounted at the top of the building.",
       None),
      ("Walk straight to the end of the hall",
       "Once you're inside, keep going down the hallway to the end. Guest Services will meet you there and walk you wherever you need to go.",
       None),
      ("Kids check in just off the café",
       "Nursery is off the café area on your left as you come through the main doors. First-time families check in at the guest station outside the SOJO Kids entrance.",
       ("SOJO Kids details","kids.html",False)),
    ])}
  </div>
</section>

<section class="sec tint">
  <div class="wrap">
    <h2 class="display display-sm">Questions about<br>the move</h2>
    {faq([
      ("When is the first Sunday at Gibson Mill?",
       f"<p><strong>{MOVE}, 2026</strong> — services at 9 and 11am, same as always.</p>"),
      ("Are service times changing?",
       "<p>No. Sundays at 9:00 and 11:00am.</p>"),
      ("Is the kids space finished?",
       "<p>Not yet — and we'd rather tell you that than surprise you. The permanent SOJO Kids space is targeted for <strong>early 2027</strong>.</p><p>Until then we have a dedicated kids area right next door to the worship room, plus the nursery off the café area. It's safe, staffed, background-checked, and ready for your kid on day one. It's just temporary, and we'd rather you hear that from us than figure it out in the hallway.</p>"),
      ("What happens to the old building?",
       "<p>We finish well and we say thank you. Union Street held six years of baptisms, first visits, and answered prayers. We're not leaving it behind so much as carrying it with us.</p>"),
      ("Is there really a coffee shop?",
       "<p>Yes — but not yet. A fully built-out coffee shop is the plan, and we're targeting <strong>early 2027</strong>. It's a real commitment, not a maybe. It's just not something you'll be able to order from on September 6.</p><p>When it opens it'll be open through the week, not just Sundays. That's the whole point — we want somebody who'd never walk into a church on a Sunday to find us on a Wednesday afternoon instead.</p>"),
      ("How can I help?",
       f"<p>Two ways, and both matter. Serve on a Sunday team so the new room feels like home from day one, and give toward what it costs to finish the build. <a class='link' href='serve.html'>Find your spot <span class='arw'>→</span></a></p>"),
    ])}
  </div>
</section>

<section class="sec sand center">
  <div class="wrap-narrow">
    <p class="script">Mark the date</p>
    <h2 class="display display-sm">September 6<br>9 &amp; 11am</h2>
    <p class="venue" style="margin-top:22px">{WAYF}</p>
    <p class="lede" style="margin-top:0">{ADDR1} · {ADDR2}</p>
    <div class="btns" style="justify-content:center">{btn("Tell us you're coming",VISIT,'btn',True)}
      {btn('Get directions',MAPS,'btn btn-ghost',True)}</div>
  </div>
</section>
'''
PAGES.append(page('new-home.html', 'Our New Home — The Kettle Room at Gibson Mill | SOJO Church',
    f'SOJO Church moves to {WAYF} on {MOVE}, 2026. Parking, entrance, kids check-in and photos of the new space.', newhome))

# ============================== KIDS =========================================
kids = f'''
<section class="phero grain dark">
  <div class="phero-img">{eager('fs-kids-run','SOJO Kids running down the mill hallway with a leader, arms out like airplanes')}</div>
  <div class="wrap">
    <p class="crumb">Next Gen · SOJO Kids · Birth – 5th Grade · Sundays 9 &amp; 11am</p>
    <h1 class="display"><span class="script">Your kids are</span><br>the first thing<br>we think about</h1>
    <p class="lede">Safe, joyful, age-specific rooms during both services — so you can actually be present in yours.</p>
    {thread('Know','Long before your child can define any of this, she can know she is safe, loved, and wanted. That is where knowing Life starts.')}
    <div class="btns">{btn("Pre-register your kids",VISIT,'btn',True)}
      {btn('All of Next Gen','next-gen.html','btn btn-ghost')}</div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="eyebrow">Why parents relax here</p>
    <h2 class="display display-sm">Four promises<br>we keep</h2>
    {rows([
      ("Every volunteer is background-checked",
       "Screened, trained, and never alone with a child. No exceptions, no shortcuts, no &ldquo;we've known them forever&rdquo; workarounds.",
       None),
      ("Only you can pick them up",
       "Secure electronic check-in gives you a matching tag. No tag, no child. It's the least romantic thing about Sunday and the part we're most rigid about.",
       None),
      ("They'll want to come back",
       "Kids who like church make Sunday easier on everybody. Ours is loud in the right places and warm in all of them.",
       None),
      ("You get to worship",
       "That's the point of all of it. Your kid is cared for, so you get 75 uninterrupted minutes with God and other adults.",
       None),
    ])}
  </div>
</section>

<section class="sec tint">
  <div class="wrap">
    <p class="eyebrow">The rooms</p>
    <h2 class="display display-sm">Built for<br>their age</h2>
    <div class="trio">
      <div>{img('nursery','A volunteer caring for an infant in the SOJO nursery')}
        <h3>Nursery · 0–24 months</h3>
        <p>Loving, attentive volunteers in a calm, secure room. Comfort, care, and prayer over your
        little one. A home away from home.</p></div>
      <div>{img('kids2','Kids checking in at SOJO Kids')}
        <h3>Preschool · 2–4 years</h3>
        <p>Hands-on activities, interactive Bible stories, worship and play — built to match their
        energy, curiosity, and growing independence.</p></div>
      <div>{img('fs-kids-mat','SOJO Kids sitting together for the lesson in the new kids space')}
        <h3>Elementary · K–5th</h3>
        <p>High-energy worship, engaging teaching, and small groups where they build real friendships
        and start owning their own faith.</p></div>
    </div>
    <p class="muted" style="margin-top:34px;max-width:62ch">At Gibson Mill, our nursery is just off the
    café area to your left as you come through the main doors. Kids 4 and up meet in the main kids
    space next door to the worship room. For everyone's comfort, that environment is for fully
    potty-trained kids.</p>
  </div>
</section>

<section class="sec">
  <div class="wrap split">
    <div class="figure figure-portrait">{img('team-jillian-goodhew','Jillian Goodhew, SOJO Kids Director','portrait')}
      <p class="figcap">Jillian Goodhew &middot; SOJO Kids Director</p></div>
    <div>
      <p class="eyebrow">Meet the director</p>
      <h2 class="display display-sm">Jillian<br>Goodhew</h2>
      <p class="lede">The heartbeat of SOJO Kids.</p>
      <p>Jillian is relentless about one thing: that every child who walks through those doors feels
      known, loved, and excited to come back. She builds the environments, trains the leaders, and
      keeps the standard high — because your kids are worth it.</p>
      <p>Got a question about allergies, special needs, check-in, or anything else? Ask her directly.</p>
      <div class="btns">{btn('Call or text us',PHONE_H,'btn btn-ghost')}</div>
    </div>
  </div>
</section>

<section class="sec concrete grain columns sheen">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">When they age out</p>
      <h2 class="display display-sm">It keeps going<br>to thirty</h2>
      <p class="lede">After 5th grade comes <strong>SOJO YTH</strong> &mdash; 6th through 12th
      grade, Wednesdays 6&ndash;8pm. After that, <strong>SOJO YA</strong> for ages 18 to 30,
      Fridays 6&ndash;8pm with dinner at 8.</p>
      <p>The handoffs between environments are where most churches quietly lose people. We watch
      those on purpose.</p>
      <div class="btns">{btn('See all of Next Gen','next-gen.html')}
        {btn('SOJO YTH','youth.html','btn btn-ghost')}</div>
    </div>
    <div class="figure">{img('y-falcons','A SOJO YTH student between activities')}</div>
  </div>
</section>
'''
PAGES.append(page('kids.html', 'SOJO Kids | SOJO Church, Concord NC',
    'Safe, joyful kids ministry at SOJO Church in Concord, NC — nursery through 5th grade, '
    'background-checked volunteers and secure check-in during both Sunday services.',
    kids, active='next-gen.html'))

# ============================== YOUTH ========================================
youth = f'''
<section class="phero grain dark">
  <div class="phero-img">{eager('w-dark','SOJO YTH students worshipping together')}</div>
  <div class="wrap">
    <p class="crumb">Next Gen · SOJO YTH · 6th – 12th Grade · Wednesdays 6–8pm</p>
    <h1 class="display"><span class="script">Not a holding pen</span><br>A movement</h1>
    <p class="lede">Wednesday nights, 6 to 8. A place for students to figure out who they are, ask
    the hard stuff out loud, and find people worth walking with.</p>
    {thread('Grow','Peace with God is settled the day you say yes. Peace with yourself takes longer, and nobody grows through adolescence alone.')}
    <div class="btns">{btn('See what&rsquo;s coming up',EVENTS,'btn',True)}
      {btn('All of Next Gen','next-gen.html','btn btn-ghost')}</div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="eyebrow">Wednesdays &middot; 6&ndash;8pm &middot; 6th&ndash;12th grade</p>
    <h2 class="display display-sm">Five things<br>every Wednesday</h2>
    {rows([
      ("Worship that doesn't talk down to them",
       "Music students actually connect with, in a room where it's safe to mean it.",
       None),
      ("Teaching about their real life",
       "Straight out of Scripture, aimed at the pressure, anxiety, and identity questions they're carrying right now — not a sanitized version of adolescence.",
       None),
      ("Small groups, not rows",
       "Discipleship happens in circles. Students break into groups led by caring adults who provide guidance, encouragement, and accountability.",
       None),
      ("Actual fun",
       "Game nights, outreach projects, retreats. Faith and fun are not competing categories here.",
       None),
      ("Leaders you can trust",
       "Every leader is screened, background-checked, and trained. Every student is valued and encouraged to be exactly who they are.",
       None),
    ])}
  </div>
</section>

<section class="sec tint">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">The long game</p>
      <h2 class="display display-sm">What we're<br>praying for</h2>
      <p class="lede">By the time a student graduates, our prayer is that they leave with four things
      nobody can take from them.</p>
      <div class="bignums bignums-2">
        <div class="bignum"><b>01</b><span>A real relationship with Jesus</span></div>
        <div class="bignum"><b>02</b><span>A settled sense of who they are</span></div>
        <div class="bignum"><b>03</b><span>Peers and mentors who stay</span></div>
        <div class="bignum"><b>04</b><span>The confidence to serve and lead</span></div>
      </div>
    </div>
    <div class="figure figure-portrait">{img('n-girl-sing','A SOJO student leading worship','portrait')}</div>
  </div>
</section>

<section class="sec">
  <div class="wrap split">
    <div class="figure figure-portrait">{img('team-audrie-cash','Audrie Cash, SOJO YTH','portrait')}
      <p class="figcap">Audrie Cash &middot; SOJO YTH</p></div>
    <div>
      <p class="eyebrow">Meet the leader</p>
      <h2 class="display display-sm">Audrie<br>Cash</h2>
      <p>Audrie found SOJO in 2021 during a season of a lot of change, and got the support and
      encouragement her family needed. She plugged into kids ministry, got asked to help with youth,
      and fell in love with it — the students first, then their parents, then the whole community
      around them.</p>
      <p>If your student is nervous about walking in, tell her. She'll make sure they're not alone.</p>
      <div class="btns">{btn('Call or text us',PHONE_H,'btn btn-ghost')}</div>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">Seniors</p>
      <h2 class="display display-sm">May shouldn&rsquo;t be<br>a cliff</h2>
      <p class="lede">Second semester of senior year, we start walking you over to <strong>SOJO YA</strong>
      &mdash; Fridays, 6 to 8, dinner at 8.</p>
      <p>You do not have to pick. Keep coming Wednesday for as long as you want it and start showing
      up Friday too. The overlap is the whole point: we would rather you have two rooms for a
      semester than none the following fall, when half your friends leave for school and the other
      half start working.</p>
      <div class="btns">{btn('About SOJO YA','young-adults.html')}</div>
    </div>
    <div class="figure">{img('y-couch','SOJO students hanging out with their leader')}</div>
  </div>
</section>

<section class="sec dark grain center">
  <div class="wrap-narrow">
    <p class="script">Parents</p>
    <h2 class="display display-sm">Come with them<br>the first time</h2>
    <p class="lede">Meet the leaders, see the room, ask whatever you want. Then let them go.</p>
    <div class="btns" style="justify-content:center">{btn('Plan a visit','plan-a-visit.html')}
      {btn('Church calendar',EVENTS,'btn btn-ghost',True)}</div>
  </div>
</section>
'''
PAGES.append(page('youth.html', 'SOJO YTH | SOJO Church, Concord NC',
    'SOJO YTH — 6th through 12th grade, Wednesdays 6-8pm in Concord, NC. Worship, real teaching, '
    'small groups, and leaders who show up.', youth, active='next-gen.html'))

# ============================== ABOUT ========================================
team_members = [
    ('team-corey-alley','Corey Alley','Lead Pastor','corey@sojourner.church'),
    ('team-dan-conklin','Dan Conklin','Campus Pastor','dan@sojourner.church'),
    ('team-jillian-goodhew','Jillian Goodhew','Kids Ministry Director','jillian@sojourner.church'),
    ('team-audrie-cash','Audrie Cash','Youth Director','audrie@sojourner.church'),
    ('team-landace-alligood','Landace Alligood','Creative Arts Director','landace@sojourner.church'),
    ('team-wendy-martin','Wendy Martin','Guest Services','wendy@sojourner.church'),
]
# kyle@sojourner.church is live too — Kyle Winecoff joins the page once PC sends his role/photo.
team_html = ''.join(
    f'<div>{img(f,n)}<h4>{n}</h4><span>{r}</span>'
    f'<a class="team-mail" href="mailto:{e}">{e}</a></div>' for f, n, r, e in team_members)

about = f'''
<section class="phero grain dark">
  <div class="phero-img">{eager('hug','People embracing after a SOJO service')}</div>
  <div class="wrap">
    <p class="crumb">About SOJO</p>
    <h1 class="display"><span class="script">A community</span><br>with a <span class="gold">cause</span></h1>
    <p class="lede">And the cause is people.</p>
    {thread('Know &middot; Grow &middot; Go','Seven years, five rooms, a staff, and a move &mdash; all of it exists so people can know Life and have it abundantly, grow in peace, and go in purpose.')}
  </div>
</section>

<section class="sec">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">Who we are</p>
      <h2 class="display display-sm">A community<br>with a <span class="ul">cause</span></h2>
      <p class="lede">That is our vision in five words. The cause is people &mdash; and the mission
      is to help them <strong>know life, grow in peace, and go in purpose</strong>.</p>
      <p>Life is not an achievement you unlock; it is a Person you meet. Peace is not the absence of
      trouble; it is wholeness that holds when trouble comes. Purpose is not a job title; it is being
      sent. All three are found in the person and redeeming work of Jesus.</p>
      <p>We are a diverse community &mdash; multiethnic, multigenerational, from a lot of different
      starting points &mdash; who found something life-changing in common. Beyond anything, we want
      you to find it too.</p>
      <div class="btns">{btn('How the mission works','mission.html')}
        {btn('Our beliefs','beliefs.html','btn btn-ghost')}</div>
      <p>We say it like this: healthy, mission-driven, discipleship-focused. And we mean
      mission-driven literally &mdash; committed to our <em>here</em>, our <em>near</em>, and our
      <em>far</em>: schools, non-profits, local businesses, first responders, and beyond.</p>
    </div>
    <div class="figure">{img('n-friends-walk','Two SOJO women walking arm in arm at a community event','portrait')}
      <p class="figcap">Serving Cabarrus County</p></div>
  </div>
</section>

<section class="sec dark grain">
  <div class="wrap center">
    <p class="pull" style="margin-inline:auto">"We believe a church should not exist for itself.
    If we shut our doors, our community should miss us."</p>
    <p class="pull-attr">The conviction SOJO was built on</p>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="eyebrow">Our history</p>
    <h2 class="display display-sm">Living room<br>to Gibson Mill</h2>
    {rows([
      ("2017 — A living room in Concord",
       "SOJO started in Corey and Betsy Alley's living room in November 2017. The original idea was small house churches in apartment complexes.",
       None),
      ("2019 — A school cafeteria",
       "First public worship service on February 24, 2019, in the cafeteria at Weddington Hills Elementary. One-year anniversary March 8, 2020 — and then the world shut down.",
       None),
      ("2020 — An ice cream shop parking lot",
       "From May to November 2020 we held drive-in services at Papa Robb's. A scary season for the world, and honestly one of the most special seasons we've had as a church.",
       None),
      ("2020 — Downtown Concord",
       "The opportunity to relocate downtown came in October 2020. First services on Union Street, October 4, 2020. Six years of baptisms, first visits, and answered prayers followed.",
       None),
      ("2026 — Gibson Mill",
       f"On {MOVE}, 2026 we move into a historic mill — twice the space, 400+ seats, room for our kids and youth to grow, and a coffee shop open all week long.",
       ("Our new home","new-home.html",False)),
    ])}
    <div class="btns">{btn('Read the whole story','our-story.html','btn')}</div>
  </div>
</section>

<section class="sec tint">
  <div class="wrap split">
    <div class="figure figure-portrait">{img('pc','Pastor Corey Alley','portrait')}
      <p class="figcap">Corey Alley &middot; Lead Pastor</p></div>
    <div>
      <p class="eyebrow">Our pastor</p>
      <h2 class="display display-sm">Most people<br>call him PC</h2>
      <p class="lede">And you can too.</p>
      <p>Corey has had a radical transformation. He used to be a product of addiction and the lifestyle
      that surrounds it. He's carried deep hurt and real pain — and he still loves telling people about
      the love and purpose Jesus offers. He's one of the most real and relatable people you'll ever meet.</p>
      <p>He's married to Betsy, his greatest earthly love, going on twenty years. They have two
      daughters, Noel and Eden. He's a Central Cabarrus High School graduate with two degrees from UNCC
      and a master's from Liberty Seminary, and he's lived in Cabarrus County most of his life.</p>
      <p>He loves sports, camping, campfires, and fishing. He has a love-hate relationship with the
      Carolina Panthers and will tell you Cam Newton is the best quarterback to ever play the game.
      He is passionate about planting churches &mdash; here, near, and far.</p>
      <p>Mostly, he loves to laugh and make people feel seen and heard.</p>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="eyebrow">Our team</p>
    <h2 class="display display-sm">The people who<br>make Sunday happen</h2>
    <div class="team">{team_html}</div>
  </div>
</section>

<section class="sec sand center">
  <div class="wrap-narrow">
    <h2 class="display display-sm">Come see for<br>yourself</h2>
    <p class="lede">Reading about a church only gets you so far.</p>
    <div class="btns" style="justify-content:center">{btn('Plan your visit','plan-a-visit.html')}
      {btn("Tell us you're coming",VISIT,'btn btn-ghost',True)}</div>
  </div>
</section>
'''
PAGES.append(page('about.html', 'About SOJO Church | Concord, NC',
    'SOJO Church started in a living room in 2017. Our story, what we believe, and the team '
    'behind Sunday in Concord, NC.', about))

# ============================== NEXT STEPS ===================================
def track(letter, title, lede, items):
    rowhtml = ''.join(
        f'<div class="row"><div class="num">{i:02d}</div><div class="rt"><div>'
        f'<h3>{h}</h3><p>{p}</p></div>'
        + (f'<a class="link" href="{l[1]}"' + (' target="_blank" rel="noopener"' if l[2] else '') +
           f'>{l[0]} <span class="arw">&rarr;</span></a>' if l else '')
        + '</div></div>'
        for i, (h, p, l) in enumerate(items, 1))
    return f'''
<div class="track">
  <div class="track-head">
    <span class="track-letter">{letter}</span>
    <div>
      <h2 class="display display-sm">{title}</h2>
      <p class="lede" style="margin-bottom:0">{lede}</p>
    </div>
  </div>
  <div class="rows">{rowhtml}</div>
</div>'''

TRACK_A = track('A', 'Finding your<br>people', 
  'Belonging comes first. You do not have to believe everything to be welcome here.',
  [
    ("Come to SOJO",
     "That's it. That's the first step. Sunday at 9 or 11am, park in the SOJO lot at Gibson Mill, walk in. You don't have to sign up, dress up, or know anybody.",
     ("Plan your visit","plan-a-visit.html",False)),
    ("Come back",
     "The second Sunday is the one that matters. The first time you're taking it in; the second time you start recognizing faces. Nobody decides anything about a church on one visit.",
     None),
    ("Try five services",
     "Five Sundays is our honest ask. Not to evaluate a stage &mdash; to meet the people. Church is more than a moment up front; it's a community you grow into, and that takes more than one morning.",
     None),
    ("Come to Discover SOJO",
     "The <strong>last Sunday of every month</strong>, right after second service. A real meal, childcare for the little ones, some SOJO swag, and an honest conversation with our leaders about who we are, where we're going, and how we work together. Bring every question you've got. Sign up in the Church Center app.",
     ("Sign up in Church Center",DISC,True)),
  ])

TRACK_B = track('B', 'Following<br>Jesus',
  'The second track is not about fitting in. It is about becoming someone new.',
  [
    ("Take Discover More",
     "A three-week virtual class covering basic doctrine and discipleship &mdash; what we actually believe and what following Jesus actually looks like day to day. Three weeks, online, no prerequisites. Come with doubts; that's what it's for.",
     ("Register for Discover More",DMORE,True)),
    ("Decide to follow Jesus",
     "If you haven't made that call yet, this is the step. Not cleaning yourself up first, not understanding everything first &mdash; just saying yes to Him. Grace isn't a reward for people who got it together. It's the reason anybody ever does.",
     ("Talk to somebody today",SMS_HELLO,False)),
    ("Get baptized",
     "Baptism is going public with a private decision. It doesn't save you; it announces that Jesus already did. If you've said yes to Him and haven't been baptized, this one is yours.",
     ("Ask us about baptism",PHONE_H,False)),
    ("Join a group",
     "Faith grows in circles, not rows. A group is where church stops being a service you attend and becomes people who actually know you &mdash; who notice when you're gone and show up when it's bad.",
     ("Find a group","groups.html",False)),
    ("Start serving",
     "You were gifted on purpose. Kids, youth, worship, production, hospitality, outreach, finance, group leading &mdash; there's a spot with your name on it, and the new building needs more hands than the old one did.",
     ("See every team","serve.html",False)),
  ])

steps = f'''
<section class="phero grain dark">
  <div class="phero-img">{eager('n-kneel','SOJO members kneeling together in prayer')}</div>
  <div class="wrap">
    <p class="crumb">Next Steps</p>
    <h1 class="display"><span class="script">Two tracks,</span><br>one step<br>at a time</h1>
    <p class="lede">One track is about finding your people. The other is about following Jesus.
    Most people walk them at the same time &mdash; and nobody walks them fast.</p>
    {thread('Know &middot; Grow &middot; Go','Track A is how you come to know. Track B is how you grow and get sent. Nobody walks either one quickly, and you do not have to.')}
  </div>
</section>

<section class="sec">
  <div class="wrap tracks">
    {TRACK_A}
  </div>
</section>

<section class="sec tint">
  <div class="wrap tracks">
    {TRACK_B}
  </div>
</section>

<section class="sec concrete grain columns sheen">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">One more track</p>
      <h2 class="display display-sm">Nobody starts<br>at the top</h2>
      <p class="lede">Generosity has its own ladder, and you only ever have to take the next rung.</p>
      <p>Not giving anything &rarr; giving something &rarr; giving regularly &rarr; giving a
      percentage &rarr; the full tithe &rarr; giving beyond it. Wherever you are on that list,
      the only step that matters is the next one.</p>
      <div class="btns">{btn('How we think about giving','give.html')}</div>
    </div>
    <div class="figure">{img('sojo-generosity','A SOJO ministry partner receiving a giving check on stage')}</div>
  </div>
</section>

<section class="sec center">
  <div class="wrap-narrow">
    <p class="script">Not sure which step is yours?</p>
    <h2 class="display display-sm">Ask us</h2>
    <p class="lede">Call, text, or find somebody at the guest table on Sunday. That is genuinely
    what we are here for.</p>
    <div class="btns" style="justify-content:center">{btn(f'Call or text {PHONE_D}',PHONE_H,'btn')}
      {btn('Plan a visit','plan-a-visit.html','btn btn-ghost')}</div>
  </div>
</section>
'''
PAGES.append(page('next-steps.html', 'Next Steps | SOJO Church, Concord NC',
    'Your next steps at SOJO Church, Concord NC — visit, try five, Discover SOJO, Discover More, baptism, groups, and serving.', steps))

# ============================== MISSION ======================================
def movement(num, title, line, scripture, ref, paras, doing, photo, alt):
    body = ''.join(f'<p>{x}</p>' for x in paras)
    items = ''.join(f'<li>{x}</li>' for x in doing)
    return f'''
<div class="chapter">
  <div class="ch-head">
    <span class="ch-num">{num}</span>
    <div>
      <p class="ch-years">{line}</p>
      <h2 class="display display-sm">{title}</h2>
    </div>
  </div>
  <div class="split split-6535">
    <div class="ch-body">
      <p class="pull" style="font-size:clamp(1.3rem,2.6vw,1.9rem);max-width:30ch">&ldquo;{scripture}&rdquo;</p>
      <p class="pull-attr" style="margin-bottom:28px">{ref}</p>
      {body}
      <p class="kicker" style="margin-top:32px;display:block">What this looks like at SOJO</p>
      <ul class="doing">{items}</ul>
    </div>
    <div class="figure">{img(photo, alt)}</div>
  </div>
</div>'''

mission = f'''
<section class="phero grain dark">
  <div class="phero-img">{eager('k-hug','A SOJO volunteer holding a child after a service')}</div>
  <div class="wrap">
    <p class="crumb">Our Mission</p>
    <h1 class="display"><span class="script">We are</span><br>a community<br>with a <span class="gold">cause</span></h1>
    <p class="lede">And the cause is people. Helping them <strong>know life, grow in peace, and go
    in purpose</strong>.</p>
  </div>
</section>

<section class="sec">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">Vision and mission</p>
      <h2 class="display display-sm">Two sentences<br>that decide<br>everything</h2>
      <p class="lede">Our <strong>vision</strong> is who we are: a community with a cause.
      Our <strong>mission</strong> is what we do about it: help people know life, grow in peace,
      and go in purpose.</p>
      <p>Most churches have a statement on a wall that nobody can recite and nothing depends on.
      Ours is a filter. If a program, a Sunday, a budget line, or an announcement does not help
      somebody know, grow, or go, we stop doing it. That has cost us some good ideas.</p>
      <p>A church exists for the people not yet in the room. If we shut our doors tomorrow, our city
      should miss us &mdash; not just the people who show up on Sunday. That is what makes a cause a
      cause instead of a slogan.</p>
      <div class="stripe" aria-hidden="true"></div>
      <p class="muted">Underneath all of it sit two pictures from Scripture: <strong>Psalm 1</strong>,
      a tree planted by streams of water that bears fruit in season, and <strong>Ezekiel 47</strong>,
      a river running out from the temple that gets deeper the farther it goes and brings everything
      it touches to life. Formation over numbers. Depth before distance.</p>
    </div>
    <div class="figure">{img('w-dark2','A SOJO congregation with hands raised in worship')}</div>
  </div>
</section>

<section class="sec tint">
  <div class="wrap chapters">

    {movement('01','Know life','Movement one','I came that they may have life, and have it abundantly.','John 10:10',
      ["Life is not an achievement you unlock. It is a Person you meet &mdash; and you almost never "
       "meet Him alone.",
       "<strong>Finding family.</strong> A lot of people walk through our doors without one, or "
       "carrying one that is hard to be around. The church is supposed to be the place where that "
       "gets answered &mdash; not with a program, but with people who save you a seat and notice "
       "when it is empty.",
       "<strong>Finding community.</strong> Somewhere a person knows your name, your kids' names, "
       "and what you are actually walking through this week. That is not a bonus feature of "
       "following Jesus. It is most of how He does it.",
       "<strong>And more than anything, finding Jesus among His people.</strong> He said where two "
       "or three gather, He is there. So the room is not the warm-up act for meeting Him &mdash; "
       "the room is often where it happens. You come looking for community and you run into Christ "
       "in the middle of it.",
       "<strong>Then finding His plan for your life.</strong> Because you were not an accident and "
       "your life is not filler. There is something He made you for, and knowing Him is where you "
       "start finding out what it is."],
      ["Sunday services at 9 and 11am &mdash; teaching straight out of the Bible, aimed at real life",
       "A First-Time Guest table with a real person, a real gift, and zero pressure",
       "Discover SOJO &mdash; a meal and an honest conversation, last Sunday of every month",
       "Baptism, and the conversations that lead there",
       "A coffee shop opening 2027, so somebody can find us on a Wednesday instead of a Sunday"],
      'greeting','Guests being welcomed in the SOJO lobby')}

    {movement('02','Grow in peace','Movement two','Since we have been justified by faith, we have peace with God through our Lord Jesus Christ.','Romans 5:1',
      ["Peace with God comes first, and it is not a mood. It is a standing. Settled, finished, "
       "bought. Everything else in this movement is learning to live like that is actually true.",
       "<strong>It grows in a group.</strong> This is the one we push hardest, because it is the "
       "one that cannot be scaled or skipped. Eight to twelve people around a table who know your "
       "actual week. You can attend a church for years and stay a stranger; you cannot sit at "
       "somebody's table for eight weeks and stay one.",
       "<strong>It grows in personal worship.</strong> The Bible on a Tuesday, not just from a "
       "stage on Sunday. Study that is yours. Prayer nobody else hears. Sunday is the meal you eat "
       "together; this is the food you learn to make at home.",
       "<strong>It grows through accountability.</strong> Somebody with standing permission to ask "
       "you the question you would rather dodge &mdash; and the relationship to make the answer "
       "safe. Almost nobody grows past a certain point without this, and almost nobody volunteers "
       "for it until they trust the room.",
       "<strong>And it grows because you want it.</strong> Peace with God is given. Peace <em>in</em> "
       "you is cultivated, and cultivation is slow. Psalm 1 does not describe someone who tried "
       "harder. It describes a tree planted somewhere, with roots first and fruit in season."],
      ["Groups &mdash; Connect, Community, Care, and Classes",
       "Discover More &mdash; three weeks, virtual, basic doctrine and discipleship",
       "Study and prayer rhythms you carry through the week, not just into the room",
       "Accountability inside a group, with people who earned the right to ask",
       "SOJO Kids, SOJO YTH and SOJO YA &mdash; Next Gen, birth through thirty"],
      'sojo-testimony','A SOJO member sharing her story before being baptized')}

    {movement('03','Go in purpose','Movement three','As the Father has sent me, even so I am sending you.','John 20:21',
      ["Purpose is not a fourth thing you add once the first two are handled. It is what the first "
       "two look like when they overflow. A person who knows life and is growing in peace starts "
       "leaking it &mdash; and it leaks into four places before it goes anywhere else.",
       "<strong>Home.</strong> The hardest congregation you will ever preach to, and the one that "
       "matters most. If it is not working at your kitchen table, it is not working.",
       "<strong>Church.</strong> Where you stop being a spectator. Peter calls all of us a royal "
       "priesthood &mdash; not a stage full of professionals and a room full of watchers.",
       "<strong>Work.</strong> Where you spend most of your waking hours, next to people who will "
       "never come to a service but will absolutely notice how you handle a bad quarter.",
       "<strong>Friends and neighbors.</strong> Your street, your group text, the people at "
       "practice. Here, near, and far starts with <em>here</em>.",
       "<strong>And through the church, two specific things.</strong> Finding a place to give back "
       "through <strong>service</strong> &mdash; there is a spot with your name on it and the new "
       "building needs more hands than the old one did. And <strong>giving to God</strong>, which "
       "is where money stops being about survival and starts being about impact. Your giving alone "
       "does something. Pooled with everybody else's it does something you could never do by "
       "yourself &mdash; a kids' wing, a coffee shop with the doors open all week, meals delivered "
       "on a Tuesday, churches planted across North Carolina. That is Ezekiel's river: it does not "
       "pool inside the temple, it runs out, and everything it touches lives."],
      ["Serving on a Sunday team &mdash; kids, youth, worship, production, hospitality",
       "Giving &mdash; and seeing what your money does pooled with everyone else's",
       "Outreach partnerships like Meals on Wheels and HellFighters of Concord",
       "Church planting partners across North Carolina and around the world",
       "Your home, your job site, and your street &mdash; the assignments nobody schedules"],
      'pray','SOJO volunteers praying with someone they were sent to')}

  </div>
</section>

<section class="sec concrete grain columns sheen">
  <div class="wrap">
    <hr class="lane" style="margin-bottom:48px">
    <p class="eyebrow">The filter</p>
    <div class="split split-6535" style="align-items:end">
      <h2 class="display display-sm">Everything we do,<br>and where it fits</h2>
      <p class="lede">If something on this list stopped serving one of the three movements, it would
      come off the list. That has happened before.</p>
    </div>
    {rows([
      ("Sunday morning &rarr; Know",
       "The front door. Clear enough to follow with no church background, warm enough to come back to, honest enough that nobody feels handled.",
       ("Plan a visit","plan-a-visit.html",False)),
      ("SOJO Kids &amp; Youth &rarr; Know and Grow",
       "Age-specific rooms so that children and students meet Jesus for themselves and start being formed early, instead of inheriting somebody else's faith.",
       ("SOJO Kids","kids.html",False)),
      ("Discover SOJO &rarr; Grow",
       "Last Sunday of every month, over a meal. Where belonging turns from a feeling into a decision.",
       ("Sign up",DISC,True)),
      ("Discover More &rarr; Grow",
       "Three weeks, virtual, basic doctrine and discipleship. Roots before fruit.",
       ("Both tracks","next-steps.html",False)),
      ("Groups &rarr; Grow",
       "Tables where formation actually happens. The part that cannot be scaled and cannot be skipped.",
       ("Find a group","groups.html",False)),
      ("Serving &rarr; Go",
       "Priesthood in plain clothes. You were gifted on purpose and pointed at somebody.",
       ("Find your spot","serve.html",False)),
      ("Missions &rarr; Go",
       "Here, near, and far. Concord and Gibson Village, church planting across North Carolina, and partners among the nations.",
       ("Here, near, far","missions.html",False)),
      ("Giving &rarr; Go",
       "Generosity is a formation practice that funds a sending mission. It sits on both ends of this list.",
       ("How we think about it","give.html",False)),
    ])}
  </div>
</section>

<section class="sec">
  <div class="wrap center">
    <p class="pull" style="margin-inline:auto">&ldquo;If we shut our doors, our community should
    miss us. Not just the people who come to SOJO on Sundays.&rdquo;</p>
    <p class="pull-attr">Pastor Corey Alley &middot; Lead Pastor</p>
  </div>
</section>

<section class="sec sand center">
  <div class="wrap-narrow">
    <p class="script">So &mdash; which one is yours?</p>
    <h2 class="display display-sm">Know, grow,<br>or go</h2>
    <p class="lede">Most people can tell within a few seconds which of the three they are standing
    in front of right now. Start there.</p>
    <div class="btns" style="justify-content:center">{btn('Come for the first time','plan-a-visit.html')}
      {btn('Find a group','groups.html','btn btn-ghost')}
      {btn('Start serving','serve.html','btn btn-ghost')}</div>
  </div>
</section>
'''
PAGES.append(page('mission.html', 'Our Mission | SOJO Church, Concord NC',
    'SOJO Church is a community with a cause: helping people know life, grow in peace, and go in purpose — and what those three movements mean.', mission))

# ============================== NEXT GEN =====================================
def env(num, name, ages, when, extra, lede, paras, details, cta, photo, alt, flip=False, anchor=''):
    body = ''.join(f'<p>{x}</p>' for x in paras)
    li = ''.join(f'<li><strong>{a}</strong> &mdash; {b}</li>' for a, b in details)
    fig = f'<div class="figure">{img(photo, alt)}</div>'
    txt = f'''<div class="ch-body">
      <p class="lede">{lede}</p>
      {body}
      <p class="kicker" style="margin-top:30px">The details</p>
      <ul class="partners">{li}</ul>
      {cta}
    </div>'''
    inner = (fig + txt) if flip else (txt + fig)
    aid = f' id="{anchor}"' if anchor else ''
    return f'''
<div class="chapter"{aid}>
  <div class="ch-head">
    <span class="ch-num">{num}</span>
    <div>
      <p class="ch-years">{ages}</p>
      <h2 class="display display-sm">{name}</h2>
    </div>
    <p class="when">{when}<span>{extra}</span></p>
  </div>
  <div class="split split-6535">{inner}</div>
</div>'''

nextgen = f'''
<section class="phero grain dark">
  <div class="phero-img">{eager('y-couch','Pastor Dan hanging out with SOJO YTH students')}</div>
  <div class="wrap">
    <p class="crumb">Next Gen</p>
    <h1 class="display"><span class="script">Birth to thirty</span><br>Next Gen</h1>
    <p class="lede">Three environments, three nights, one goal: that the next generation meets
    Jesus for themselves instead of inheriting somebody else&rsquo;s faith.</p>
    {thread('Know &middot; Grow','A two-year-old learns Life is safe before she can spell any of this. A middle schooler learns peace is possible. A twenty-four-year-old learns purpose is real. Same three words, three different rooms.')}
    <div class="btns">{btn('Plan your visit','plan-a-visit.html')}
      {btn('Call or text us',PHONE_H,'btn btn-ghost')}</div>
  </div>
</section>

<section class="sec-tight tint">
  <div class="wrap">
    <hr class="lane" style="margin-bottom:34px">
    <p class="eyebrow">When everybody meets</p>
    <div class="whenrow">
      <a href="#kids"><b>SOJO Kids</b><span>Birth &ndash; 5th grade</span><em>Sundays &middot; 9 &amp; 11am</em></a>
      <a href="#yth"><b>SOJO YTH</b><span>6th &ndash; 12th grade</span><em>Wednesdays &middot; 6&ndash;8pm</em></a>
      <a href="#ya"><b>SOJO YA</b><span>18&ndash;30 &middot; seniors 2nd semester</span><em>Fridays &middot; 6&ndash;8pm</em></a>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">Why we build it this way</p>
      <h2 class="display display-sm">Nobody inherits<br>a faith</h2>
      <p class="lede">A kid can grow up in a church and never once decide anything for themselves.
      We are trying very hard to make that impossible here.</p>
      <p>So each environment is built for the actual developmental stage in front of it &mdash; not
      a shrunk-down version of the adult service. A four-year-old needs movement and story. A
      fifteen-year-old needs somebody who will not flinch at the question. A twenty-four-year-old
      needs a table, a meal, and people who are also figuring out what they actually believe now
      that nobody is making them go.</p>
      <p>Every leader across all three is screened, background-checked, and trained. That is the
      floor, not the ceiling.</p>
      <p><strong>And we build the handoffs on purpose.</strong> Second semester of senior year, we
      start walking students from YTH into SOJO YA &mdash; Friday nights, with Wednesdays still open
      to them. The overlap is deliberate. Graduation is where churches lose people, and we would
      rather a senior have two rooms for a semester than none the following fall.</p>
    </div>
    <div class="figure">{img('n-kids-stage','SOJO Kids with their hands up during large group')}</div>
  </div>
</section>

<section class="sec tint" id="kids">
  <div class="wrap chapters">

    {env('01','SOJO Kids','Birth &ndash; 5th grade','Sundays','9 &amp; 11am',
      'Safe, joyful, age-specific rooms during both services &mdash; so you can actually be present in yours.',
      ["Every Sunday your child goes to a room built for exactly where they are. Nursery babies get "
       "calm and consistency. Preschoolers get movement, story, and play. Elementary kids get "
       "high-energy worship, real Bible teaching, and a small group where somebody knows their name.",
       "The safety piece is not marketing. Every volunteer is screened, trained, and "
       "background-checked, and secure electronic check-in means your tag has to match theirs. No "
       "tag, no child &mdash; including for grandparents, and we have had that conversation before."],
      [("Nursery","Birth &ndash; 24 months. Located just off the caf&eacute; area, left as you come through the main doors."),
       ("Preschool","2 &ndash; 4 years. Hands-on activities, interactive Bible stories, worship and play."),
       ("Lower Elementary","5 years &ndash; 1st grade. High-energy worship and small group time."),
       ("Upper Elementary","2nd &ndash; 5th grade. Deeper Scripture and discussion-based small groups."),
       ("First-time check-in","At the guest station outside the SOJO Kids entrance. Returning families use the self-service station by the nursery."),
       ("Director","Jillian Goodhew &mdash; ask her anything about allergies, special needs, or check-in.")],
      f'<div class="btns">{btn("More about SOJO Kids","kids.html")} {btn("Pre-register your kids",VISIT,"btn btn-ghost",True)}</div>',
      'kids','Elementary kids in a SOJO Kids small group', anchor='kids-env')}

    {env('02','SOJO YTH','6th &ndash; 12th grade','Wednesdays','6 &ndash; 8pm',
      'Middle and high school, Wednesday nights, two hours that students actually want to be at.',
      ["Doors open at six. Worship students connect with, teaching aimed at the pressure and "
       "identity questions they are carrying right now, and small groups led by adults who show up "
       "every single week &mdash; which is most of what a fifteen-year-old is actually testing for.",
       "It is loud in the right places. There are games. There is food more often than not. And "
       "there is space for the questions students will not ask at home yet."],
      [("When","Wednesdays, 6:00 &ndash; 8:00pm"),
       ("Who","6th through 12th grade &mdash; middle and high school together, splitting for small groups"),
       ("Worship","Music built for students, in a room where it is safe to mean it"),
       ("Teaching","Straight out of Scripture, aimed at the life they are actually living"),
       ("Small groups","Led by screened, background-checked, trained adults"),
       ("Leader","Audrie Cash &mdash; tell her if your student is nervous walking in and she will make sure they are not alone."),
       ("Seniors","In the second semester of senior year we start walking seniors over to SOJO YA on Friday nights. They keep Wednesdays as long as they want them.")],
      f'<div class="btns">{btn("More about SOJO YTH","youth.html")} {btn("Church calendar",EVENTS,"btn btn-ghost",True)}</div>',
      'g2-yth-mural','SOJO YTH students together at the SOJO missions mural', flip=True, anchor='yth')}

    {env('03','SOJO YA','Ages 18 &ndash; 30 &middot; and seniors from 2nd semester','Fridays','6 &ndash; 8pm, dinner at 8',
      'Young adults, Friday nights, and nobody eats alone afterward.',
      ["This is the season most people quietly leave church &mdash; not because they decided "
       "against Jesus, but because nobody made a place for the version of them that just moved out, "
       "started a job, ended a relationship, or stopped being made to go.",
       "So we made one. Friday nights, six to eight: worship, real teaching, and honest "
       "conversation about the things this decade actually hands you &mdash; work, money, dating, "
       "loneliness, and what you believe now that it is entirely your call.",
       "<strong>Then dinner at eight.</strong> Every week. That part is not an add-on; it is half "
       "the point. Whatever else is true about your Friday, you are not eating it alone."],
      [("When","Fridays, 6:00 &ndash; 8:00pm &mdash; dinner together at 8:00pm"),
       ("Who","Ages 18 &ndash; 30. College, working, single, married, still figuring it out."),
       ("High school seniors","Second semester of senior year, you are welcome here. Come to Friday and keep going to YTH on Wednesday &mdash; the overlap is on purpose."),
       ("What happens","Worship, teaching, and conversation that does not stay surface"),
       ("Dinner","Every week at 8. Come for the whole thing or just the table."),
       ("Bring somebody","Seriously. This is the easiest thing at SOJO to invite a friend to."),
       ("Cost","Free. The meal is on us.")],
      f'<div class="btns">{btn("Ask about SOJO YA",PHONE_H,"btn")} {btn("Find a group","groups.html","btn btn-ghost")}</div>',
      'sojo-teens','Young adults together at SOJO', anchor='ya')}

  </div>
</section>

<section class="sec concrete grain columns sheen">
  <div class="wrap">
    <hr class="lane" style="margin-bottom:48px">
    <p class="eyebrow">For parents</p>
    <div class="split split-6535" style="align-items:end">
      <h2 class="display display-sm">What we promise<br>you</h2>
      <p class="lede">The same four things across all three environments, every single week.</p>
    </div>
    {rows([
      ("Every leader is background-checked",
       "Screened, trained, and never alone with a minor. No exceptions, no shortcuts, no &ldquo;we have known them forever&rdquo; workarounds.",
       None),
      ("You will know what they were taught",
       "Ask any leader what the lesson was and you will get a real answer. We are not running a mystery box.",
       None),
      ("They will want to come back",
       "A kid or student who likes church makes the whole week easier on a family. We take that seriously as a design goal.",
       None),
      ("Nobody gets lost in the shuffle",
       "Birth to thirty is a long runway, and the handoffs are where churches lose people &mdash; especially graduation. That is why seniors start moving into SOJO YA in their second semester instead of falling off a cliff in May.",
       None),
    ])}
  </div>
</section>

<section class="sec sand center">
  <div class="wrap-narrow">
    <p class="script">One night, one Sunday</p>
    <h2 class="display display-sm">Just bring<br>them once</h2>
    <p class="lede">Sundays at 9 and 11 for kids. Wednesdays at 6 for students. Fridays at 6 for
    young adults, with dinner at 8.</p>
    <div class="btns" style="justify-content:center">{btn('Plan your visit','plan-a-visit.html')}
      {btn(f'Call or text {PHONE_D}',PHONE_H,'btn btn-ghost')}</div>
  </div>
</section>
'''
PAGES.append(page('next-gen.html', 'Next Gen | SOJO Church, Concord NC',
    'SOJO Next Gen — SOJO Kids (birth to 5th grade, Sundays 9 & 11am), SOJO YTH (6th-12th grade, '
    'Wednesdays 6-8pm) and SOJO YA (18-30, Fridays 6-8pm with dinner at 8).', nextgen))

# ============================== SOJO YA =====================================
ya = f'''
<section class="phero grain dark">
  <div class="phero-img">{eager('hug','Young adults embracing after a SOJO gathering')}</div>
  <div class="wrap">
    <p class="crumb">Next Gen &middot; SOJO YA &middot; Ages 18&ndash;30 &middot; Fridays 6&ndash;8pm</p>
    <h1 class="display"><span class="script">Nobody eats</span><br>alone on<br>Fridays</h1>
    <p class="lede">SOJO YA is for ages 18 to 30 &mdash; college, working, single, married, still
    figuring it out. Fridays 6 to 8, and dinner together at 8.</p>
    <div class="btns">{btn('Ask about this Friday',PHONE_H,'btn')}
      {btn('All of Next Gen','next-gen.html','btn btn-ghost')}</div>
  </div>
</section>

<section class="sec">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">Why this exists</p>
      <h2 class="display display-sm">The decade the<br>church loses people</h2>
      <p class="lede">Most people who leave church leave in this one &mdash; not because they
      decided against Jesus, but because nobody made a place for the version of them that just
      moved out, started a job, ended a relationship, or stopped being made to go.</p>
      <p>So we made one. Friday nights are worship, real teaching, and honest conversation about
      the things this decade actually hands you &mdash; work, money, dating, loneliness, and what
      you believe now that it is entirely your call.</p>
      <p><strong>Then dinner at eight, every week.</strong> That part is not an add-on; it is half
      the point. Whatever else is true about your Friday, you are not eating it alone.</p>
      {thread('Know &middot; Grow','This is where a lot of twenty-somethings find out the faith they inherited can actually be theirs &mdash; and find the people to build it with.')}
    </div>
    <div class="figure">{img('sojo-teens','SOJO young adults together in the lobby')}</div>
  </div>
</section>

<section class="sec tint">
  <div class="wrap">
    <p class="eyebrow">The details</p>
    <h2 class="display display-sm">Straight<br>answers</h2>
    {rows([
      ("When and where",
       f"Fridays, 6:00&ndash;8:00pm at {WAYF}, {ADDR1}, {ADDR2}. Dinner together at 8:00pm, on us.",
       ("Get directions",MAPS,True)),
      ("Who it&rsquo;s for",
       "Ages 18&ndash;30. College students, people working full time, married couples, single people, and everyone still deciding what they are. You do not need to bring anybody or know anybody.",
       None),
      ("High school seniors",
       "Second semester of senior year, you are welcome here &mdash; and you can keep Wednesdays at SOJO YTH as long as you want them. The overlap is on purpose: we would rather you have two rooms for a semester than none the following fall.",
       ("About SOJO YTH","youth.html",False)),
      ("What a Friday looks like",
       "Worship, teaching aimed at this decade of life, honest conversation, and a real dinner. Come for the whole thing or just come to the table at 8.",
       None),
      ("Cost",
       "Free, dinner included. Bring a friend &mdash; this is the easiest thing at SOJO to invite somebody to.",
       None),
    ])}
  </div>
</section>

<section class="sec concrete grain columns sheen">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">Beyond Friday</p>
      <h2 class="display display-sm">This is a<br>launch pad</h2>
      <p class="lede">YA is not meant to be an island for your twenties. It is where you build the
      faith and the friendships you carry into everything after.</p>
      <p>From here people join groups, lead SOJO Kids rooms, run cameras, go on mission trips, and
      show up early to set chairs. Purpose is not something YA graduates into later &mdash; it
      starts on a Friday.</p>
      <div class="btns">{btn('Find a group','groups.html')}
        {btn('Start serving','serve.html','btn btn-ghost')}</div>
    </div>
    <div class="figure">{img('g2-table','SOJO young adults sharing a meal together')}</div>
  </div>
</section>

<section class="sec sand center">
  <div class="wrap-narrow">
    <p class="script">Friday, 6pm</p>
    <h2 class="display display-sm">Come hungry</h2>
    <p class="lede">Show up once. Worst case, you get dinner out of it.</p>
    <div class="btns" style="justify-content:center">{btn(f'Call or text {PHONE_D}',PHONE_H,'btn')}
      {btn('Plan a Sunday visit','plan-a-visit.html','btn btn-ghost')}</div>
  </div>
</section>
'''
PAGES.append(page('young-adults.html', 'SOJO YA — Young Adults | SOJO Church, Concord NC',
    'SOJO YA — young adults 18 to 30 in Concord, NC. Fridays 6-8pm at Gibson Mill with dinner '
    'together at 8. High school seniors welcome from second semester.', ya, active='next-gen.html'))

# ============================== WHAT WE BELIEVE ==============================
def belief(num, title, text, refs):
    return f'''
<div class="row belief-row">
  <div class="num">{num:02d}</div>
  <div class="rt"><div>
    <h3>{title}</h3>
    <p class="believe"><span class="wb">We believe</span> {text}</p>
    <p class="refs">{refs}</p>
  </div></div>
</div>'''

BELIEFS = [
 ("God",
  "God is the Creator, Sovereign over creation. He eternally exists in three persons: the Father, "
  "the Son and the Holy Spirit. These three are co-equal and are one God.",
  "Genesis 1:1, 26&ndash;27; 3:22 &middot; Psalm 90:2 &middot; Matthew 28:19 &middot; 1 Peter 1:2 &middot; 2 Corinthians 13:14"),
 ("Jesus Christ",
  "Jesus is the Son of God. He is co-equal with the Father. We believe in the deity of our Lord "
  "Jesus Christ and His virgin birth. Jesus lived a sinless human life and offered Himself as the "
  "perfect sacrifice for the sins of all people by dying on a cross. He arose from the dead after "
  "three days to demonstrate His power over sin and death. He ascended to Heaven&rsquo;s glory and "
  "will return again to receive us into Heaven.",
  "Matthew 1:22&ndash;23 &middot; Isaiah 9:6 &middot; John 1:1&ndash;5; 14:10&ndash;30 &middot; Hebrews 4:14&ndash;15 &middot; 1 Corinthians 15:3&ndash;4 &middot; Romans 1:3&ndash;4 &middot; Acts 1:9&ndash;11 &middot; 1 Timothy 6:14&ndash;15 &middot; Titus 2:13"),
 ("The Holy Spirit",
  "the Holy Spirit is equal with the Father and the Son as God. He is present in the world to make "
  "men aware of their need for Jesus Christ. He lives in every Christian from the moment of "
  "salvation. He provides the Christian with power for living, understanding of spiritual truth, "
  "and guidance in doing what is right. The Christian seeks to live under His control daily.",
  "John 16:7&ndash;13; 14:16&ndash;17 &middot; 2 Corinthians 3:17 &middot; Acts 1:8 &middot; 1 Corinthians 2:12; 3:16 &middot; Ephesians 1:13; 5:18 &middot; Galatians 5:25"),
 ("The Bible",
  "the Bible is God&rsquo;s Word. Through the Bible God reveals Himself &mdash; His character and "
  "His will &mdash; to human beings. Penned by human authors under the supernatural guidance of the "
  "Holy Spirit, the Bible is truth and without error in what it intends to say. As such, the Bible "
  "is the supreme source of truth for what Christians believe and how we live. When properly "
  "understood and practiced, the Bible defines love and leads us to love God and people.",
  "Psalm 12:6 &middot; Psalm 119:105, 160 &middot; Proverbs 30:5 &middot; Matthew 22:37&ndash;40 &middot; 2 Timothy 1:13; 3:16 &middot; 2 Peter 1:20&ndash;21"),
 ("Humanity &amp; Sin",
  "human beings are made in the image of God &mdash; spiritually, volitionally and emotionally. As "
  "image-bearers of God, every person matters to God. We are God&rsquo;s supreme purpose for "
  "creation. Yet, because of Adam&rsquo;s sin, we are a fallen people. Human beings will always be "
  "bent toward fighting God. Sin separates mankind from God. Therefore, everyone needs a "
  "supernatural Savior.",
  "Genesis 1:27 &middot; Psalm 8:3&ndash;6 &middot; Isaiah 53:6 &middot; Isaiah 59:1&ndash;2 &middot; John 3:16 &middot; Romans 3:23"),
 ("Eternity",
  "Heaven and Hell are real. People were created to exist forever. We will either exist eternally "
  "separated from God by sin, or eternally with God through forgiveness and salvation. To be "
  "eternally separated from God is Hell. To be eternally in union with Him is eternal life. Heaven "
  "and Hell are real places.",
  "John 3:16 &middot; John 14:2&ndash;3 &middot; Romans 6:23 &middot; Romans 8:17&ndash;18 &middot; Revelation 20:15 &middot; 1 Corinthians 2:7&ndash;9"),
 ("Salvation",
  "salvation is a gift from God. Human beings can never put God in our debt so that He owes us "
  "salvation. Therefore, we are saved by grace through faith because Jesus paid sin&rsquo;s "
  "penalty on the cross.",
  "John 14:6; 1:12 &middot; Romans 5:1; 6:23 &middot; Ephesians 2:8&ndash;9 &middot; Titus 3:5 &middot; Galatians 3:26"),
 ("Baptism",
  "baptism is the public declaration that one is accepting Jesus Christ as Lord and Savior. "
  "Baptism was commanded by Jesus and practiced by the New Testament church. We believe one who "
  "has believed, confessed and repented should be baptized, in a timely act of obedience. Baptism "
  "represents both Christ&rsquo;s resurrection from the tomb and the resurrection of all believers "
  "yet to come.",
  "Matthew 28:18&ndash;20 &middot; Acts 2:37&ndash;38 &middot; Acts 8:35&ndash;39 &middot; Romans 6:4 &middot; Colossians 2:12 &middot; 1 Corinthians 12:13"),
 ("Marriage &amp; Gender",
  "that matrimony is a holy monogamous marriage between one man and one woman. This means that man "
  "and woman are two distinct genders willed by God their Creator in their respective beings, which "
  "reflect the image and nature of God.",
  "Genesis 2:24 &middot; Malachi 2:16 &middot; Matthew 19:4&ndash;6 &middot; Deuteronomy 22:5 &middot; Romans 1:26&ndash;27"),
]
BELIEF_ROWS = ''.join(belief(i+1, t, x, r) for i, (t, x, r) in enumerate(BELIEFS))

beliefs = f'''
<section class="phero grain dark">
  <div class="phero-img">{eager('bible','An open Bible at SOJO Church')}</div>
  <div class="wrap">
    <p class="crumb">About &middot; What We Believe</p>
    <h1 class="display"><span class="script">A closed hand</span><br>and an<br>open one</h1>
    <p class="lede">Some things we hold firm and do not budge. Everything else, we hold with an
    open hand &mdash; and a seat at the table for you to talk it through with us.</p>
  </div>
</section>

<section class="sec">
  <div class="wrap split">
    <div>
      <p class="eyebrow">The closed hand</p>
      <h2 class="display display-sm">The essentials</h2>
      <p class="lede">On the primary beliefs of the historic Christian faith, we are firm. We do
      not budge.</p>
      <p>Who God is. Who Jesus is and what He did. What Scripture is. What we are, what went wrong,
      and how it gets made right. These are not SOJO&rsquo;s opinions &mdash; they are the faith
      Christians have confessed for two thousand years, and the nine statements below are where we
      stand.</p>
    </div>
    <div>
      <p class="eyebrow">The open hand</p>
      <h2 class="display display-sm">Everything else</h2>
      <p class="lede">On secondary beliefs, we hold our convictions with an open hand.</p>
      <p>How the end times unfold. Styles of worship. Questions of church practice and Christian
      liberty that faithful believers have read differently for centuries. We have convictions
      here too &mdash; but we will not break fellowship over them, and we would genuinely rather
      talk than win.</p>
      <p><strong>If you come from a different faith background, come.</strong> Bring the questions
      and the disagreements. Dialogue is not a threat to what we believe; it is one of the ways we
      love you.</p>
    </div>
  </div>
</section>

<section class="sec tint">
  <div class="wrap">
    <p class="eyebrow">SOJO doctrinal position</p>
    <h2 class="display display-sm">Nine things<br>we hold firm</h2>
    <div class="rows">{BELIEF_ROWS}</div>
    {thread('Know &middot; Grow','Doctrine is not trivia for insiders. Knowing who God actually is, is where knowing Life starts &mdash; and roots grow in solid ground.')}
  </div>
</section>

<section class="sec concrete grain columns sheen">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">Go deeper</p>
      <h2 class="display display-sm">Three weeks,<br>every question<br>welcome</h2>
      <p class="lede">Discover More is our three-week virtual class on basic doctrine and
      discipleship &mdash; everything on this page, unpacked, with room to push back.</p>
      <p>You do not have to agree with all nine statements to take it. You have to be curious.</p>
      <div class="btns">{btn('Register for Discover More',DMORE,'btn',True)}
        {btn('Both next-step tracks','next-steps.html','btn btn-ghost')}</div>
    </div>
    <div class="figure">{img('n-dan-teach','Pastor Dan teaching at SOJO Church')}</div>
  </div>
</section>

<section class="sec sand center">
  <div class="wrap-narrow">
    <p class="script">Still deciding what you believe?</p>
    <h2 class="display display-sm">Come anyway</h2>
    <p class="lede">This page is where we stand. It has never been the price of admission.</p>
    <div class="btns" style="justify-content:center">{btn('Plan your visit','plan-a-visit.html')}
      {btn(f'Talk it through &mdash; {PHONE_D}',PHONE_H,'btn btn-ghost')}</div>
  </div>
</section>
'''
PAGES.append(page('beliefs.html', 'What We Believe | SOJO Church, Concord NC',
    'The SOJO Church doctrinal position — nine essential beliefs we hold firm, held alongside an '
    'open hand on secondary matters and a genuine welcome for dialogue.', beliefs, active='about.html'))

# ============================== MISSIONS =====================================
# Partner lists come from PC's FY missions budget. Per-partner dollar amounts are
# deliberately NOT published — only the aggregate totals, which build trust
# without exposing allocations between partner churches.
def field(num, label, place, lede, paras, partners, photo=None, alt='', flip=False):
    """One mission ring. Photo is optional — we only show one where we actually
    have a photograph of that ring's work."""
    body = ''.join(f'<p>{x}</p>' for x in paras)
    def card(n, d, u):
        arrow = '<span class="pw-go">&#8599;</span>' if u else ''
        inner = f'<span class="pw-n">{n}{arrow}</span><span class="pw-d">{d}</span>'
        return (f'<a class="pw" href="{u}" target="_blank" rel="noopener">{inner}</a>'
                if u else f'<span class="pw pw-flat">{inner}</span>')
    li = ''.join(card(n, d, u) for n, d, u in partners)
    wall = ('<p class="kicker" style="margin-top:30px">Who we stand with</p>'
            f'<div class="pwall">{li}</div>')
    head = (f'<div class="ch-head"><span class="ch-num">{num}</span>'
            f'<div><p class="ch-years">{place}</p>'
            f'<h2 class="display display-sm">{label}</h2></div></div>')
    txt = f'<div class="ch-body"><p class="lede">{lede}</p>{body}</div>'
    if photo:
        fig = f'<div class="figure">{img(photo, alt)}</div>'
        inner = (fig + txt) if flip else (txt + fig)
        return f'<div class="chapter">{head}<div class="split split-6535">{inner}</div>{wall}</div>'
    return (f'<div class="chapter">{head}'
            f'<div class="split split-6535">{txt}<div>{wall}</div></div></div>')
    inner = (fig + txt) if flip else (txt + fig)
    return f'''
<div class="chapter">
  <div class="ch-head">
    <span class="ch-num">{num}</span>
    <div>
      <p class="ch-years">{place}</p>
      <h2 class="display display-sm">{label}</h2>
    </div>
    <p class="field-total">{total}<span>committed this year</span></p>
  </div>
  <div class="split split-6535">{inner}</div>
</div>'''

missions = f'''
<section class="phero grain dark">
  <div class="phero-img">{eager('outreach','SOJO Church volunteers serving the Concord community')}</div>
  <div class="wrap">
    <p class="crumb">Outreach &amp; Missions</p>
    <h1 class="display"><span class="script">Here.</span><br>Near.<br>Far.</h1>
    <p class="lede">A church that only gets deeper and never gets wider has misread the picture.
    Ezekiel&rsquo;s river does not pool inside the temple &mdash; it runs out, and everything it
    touches lives.</p>
    {thread('Go','This is why we go. Heaven comes to earth in specific places &mdash; a street in Concord, a new church in a small town, a child fed and known by name.')}
  </div>
</section>

<section class="sec">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">The approach</p>
      <h2 class="display display-sm">Three rings,<br>one river</h2>
      <p class="lede">We do not pick between loving our street and reaching the nations. We fund
      all three, on purpose, every year.</p>
      <p><strong>Here</strong> is Concord and Gibson Village &mdash; the neighbors we can drive to,
      the schools our kids attend, the first responders who answer our calls.</p>
      <p><strong>Near</strong> is North Carolina, and it is mostly church planting. New churches
      reach people existing churches never will, and we would rather help start one than protect
      our own attendance.</p>
      <p><strong>Far</strong> is the nations &mdash; partners who train leaders, feed and educate
      children, and go where we cannot, plus a fund so our own people can actually get on a plane.</p>
      <p>If we shut our doors tomorrow, our community should miss us. This page is where that stops
      being a slogan and starts being a line item.</p>
    </div>
    <div class="figure">{img('sojo-generosity','A SOJO ministry partner receiving a giving check on stage')}
      <p class="figcap">Generosity, handed to somebody who needed it</p></div>
  </div>
</section>

<section class="sec tint">
  <div class="wrap chapters">

    {field('01','Concord &amp;<br>Gibson Village','Here',
      'The neighbors we can drive to.',
      ["Our <em>here</em> is the block, not an abstraction. Food for families who run short before "
       "the month does. Bibles into hands that never had one. Care for people in recovery and "
       "people in crisis. Packing events where a few hundred of us do something with our hands "
       "instead of talking about it.",
       "Gibson Village is the neighborhood we just moved into &mdash; and moving in comes with "
       "obligations. We intend to be the kind of neighbor the Village would notice if we left."],
      [("One Can","Fighting hunger in Cabarrus County","https://your1can.org/"),
       ("Lifeline Charlotte Centre","Packing nutritious meals for hungry families here and around the world &mdash; from Suite 175, two doors down from us at Gibson Mill","https://lifeline.org/charlotte-centre"),
       ("Cases for a Cause","Suitcases, shoes and Christmas for children entering foster care","https://casesforacausenc.org/"),
       ("HellFighters of Concord","Reaching people the church usually misses","https://www.facebook.com/concordhellfightersministry/"),
       ("Central Cabarrus Bible Teaching Association","Teaching the Bible across our county","https://www.ccbta.net/"),
       ("Community Causes","Local schools, local businesses, and our first responders &mdash; the neighbors who hold this city together",None),
       ("Packing Events","Church-wide days packing meals and cases alongside One Can and Lifeline",None),
       ("Mission Events","Fundraisers that fill the tank for what comes next &mdash; here, near and far",None)],
      'm2-egghunt','Kids racing for eggs at the SOJO community egg hunt in Concord')}

    <div class="gal" style="margin-top:clamp(28px,4vw,44px)">
      <div class="g-third">{img('m2-cottoncandy','SOJO volunteers spinning cotton candy at a community outreach event')}</div>
      <div class="g-third">{img('m2-dad-basket','A dad and his daughter at the SOJO egg hunt')}</div>
      <div class="g-third">{img('m2-jesus-eggs','SOJO eggs and Jesus loves you toys ready for the hunt')}</div>
      <div class="g-third">{img('m2-prize-kids','Kids picking prizes at the SOJO outreach table')}</div>
    </div>

    {field('02','Churches we<br>help plant','Near',
      'Mostly North Carolina, and mostly church planting &mdash; because new churches reach people we never will.',
      ["A church that will not help start other churches has quietly decided it is the point. "
       "We are not the point.",
       "So a real share of what you give leaves this building and lands in rooms we will never sit "
       "in &mdash; a plant down the road in Concord, a coastal church in Shallotte, a ministry in "
       "Charlotte, a work all the way out in San Diego. Pastors we may only meet twice. That is "
       "not generosity leaking out. That is generosity working."],
      [("633 Church","A church plant right here in Concord",None),
       ("Grace City","Church planting partner","https://wearegracecity.com/"),
       ("Live Oaks Church","Shallotte, North Carolina","https://www.liveoaks.church/"),
       ("Plant Joy Ministries","Stephen Wagoner&rsquo;s ministry in Charlotte","https://www.facebook.com/PlantJoyMinistries/"),
       ("The Abbey","A church plant in San Diego, California",None),
       ("Send Network","The church planting network we plant through","https://www.namb.net/send-network/"),
       ("Cabarrus Baptist Association","Our local association","https://www.ccbta.net/")],
)}

    {field('03','The<br>Nations','Far',
      'One church planted every month &mdash; and a fund so our own people can go too.',
      ["Far is the ring most churches talk about and fewest actually fund. We fund it.",
       "Through <strong>The Timothy Initiative</strong> we are planting <strong>one church a "
       "month</strong> &mdash; twelve a year, in villages we will never visit, led by people we "
       "will never meet. TTI trains national leaders where they already live, so the church that "
       "gets planted is not a foreign import; it is somebody&rsquo;s neighbor.",
       "Add children fed, educated and known by name, and gospel work in places that never show up "
       "on a Sunday morning here. And a Mission Trip Fund on the books, because sending money is "
       "good and sending people changes both ends of the trip."],
      [("TTI &mdash; The Timothy Initiative","&ldquo;A church in every village, everywhere.&rdquo; Our giving plants one church a month",'https://ttiglobal.org/'),
       ("Jlife","Global gospel partnership","https://www.jlife.org/"),
       ("Compassion","Releasing children from poverty in Jesus&rsquo; name","https://www.compassion.com/"),
       ("Mission Trip Fund","So our own people can go, not just give",None)],
)}

  </div>
</section>

<section class="sec">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">Two doors down</p>
      <h2 class="display display-sm">Our neighbor<br>at the Mill</h2>
      <p class="lede">Lifeline Charlotte Centre packs meals for hungry families out of
      <strong>Suite 175 at Gibson Mill</strong>. Starting September 6, we are in Suite 148.</p>
      <p>Same hallway. A Christian meal-packing facility where anybody of any age or ability can
      show up and put food in a box that ends up in front of a hungry student, a refugee family, or
      a community digging out from a storm.</p>
      <p>We did not plan that. We are going to make the most of it.</p>
      <div class="btns">{btn('Lifeline Charlotte Centre','https://lifeline.org/charlotte-centre','btn',True)}
        {btn('Serve with us','serve.html','btn btn-ghost')}</div>
    </div>
    <div class="figure">{img('m-lifeline-group','SOJO Church gathered outside Lifeline Christian Mission at Gibson Mill')}
      <p class="figcap">SOJO at Lifeline &middot; Suite 175, Gibson Mill</p></div>
  </div>

  <div class="wrap" style="margin-top:clamp(40px,5vw,64px)">
    <div class="gal gal-cap">
      {gi('g-third','m-pack-orient','SOJO volunteers being briefed before a Lifeline meal packing session','Mix. Weigh. Seal. Ship.','Every packing day starts with a briefing and a look at who the food is going to.')}
      {gi('g-third','m-pack-line','SOJO volunteers packing rice and vegetable meals','On the line','Rice and veggies, weighed, sealed and boxed by hand.')}
      {gi('g-third','m-pack-pair','Two SOJO volunteers in hairnets at a packing event','Hairnets required','No skill needed. Show up, put one on, get to work.')}
    </div>
  </div>
</section>

<section class="sec concrete grain columns sheen">
  <div class="wrap">
    <hr class="lane" style="margin-bottom:48px">
    <p class="eyebrow">The whole picture</p>
    <div class="split split-6535" style="align-items:end">
      <h2 class="display display-sm">What it adds<br>up to</h2>
      <p class="lede">Every one of these is funded, on purpose, every year &mdash; before a single
      unbudgeted need walks through the door.</p>
    </div>
    <div class="bignums">
      <div class="bignum"><b>19</b><span>Partners we stand with</span></div>
      <div class="bignum"><b>12</b><span>Churches planted a year through TTI</span></div>
      <div class="bignum"><b>3</b><span>Rings &mdash; here, near, far</span></div>
      <div class="bignum"><b>1</b><span>City we start in</span></div>
    </div>
    <p style="margin-top:34px;max-width:64ch">Nobody at SOJO gives to a budget. But when you give
    here, a real share of it leaves this building on purpose &mdash; and one of those months,
    somewhere, a church starts that would not have.</p>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="eyebrow">Your part</p>
    <h2 class="display display-sm">Three ways<br>in</h2>
    {rows([
      ("Serve locally",
       "Meals on Wheels every Tuesday, HellFighters, packing events, and serve days across Concord and Gibson Village. You do not need a skill set. You need a calendar.",
       ("Find your spot","serve.html",False)),
      ("Give",
       "Every dollar of this page is funded by people who decided their money should do more than survive. Generosity is the engine under all three rings.",
       ("How we think about giving","give.html",False)),
      ("Go",
       "The Mission Trip Fund exists so cost is not the reason you stayed home. Ask us where the next team is headed.",
       (f"Call or text {PHONE_D}",PHONE_H,False)),
    ])}
  </div>
</section>

<section class="sec sand center">
  <div class="wrap-narrow">
    <p class="script">Here, near, and far</p>
    <h2 class="display display-sm">It all starts<br>with here</h2>
    <p class="lede">The nations are not more spiritual than your street. Start with the one in
    front of you.</p>
    <div class="btns" style="justify-content:center">{btn('Start serving','serve.html')}
      {btn('Give',GIVE,'btn btn-ghost',True)}</div>
  </div>
</section>
'''
PAGES.append(page('missions.html', 'Outreach &amp; Missions | SOJO Church, Concord NC',
    'SOJO Church funds missions here, near and far — Concord and Gibson Village, church planting '
    'across North Carolina, and partners among the nations.', missions))

# ============================== GROUPS =======================================
def gtype(letter, name, what, blurb, body, items, cta, photo, alt, flip=False):
    li = ''.join(
        f'<div class="row"><div class="num">&mdash;</div><div class="rt"><div>'
        f'<h3>{a}</h3><p>{b}</p></div></div></div>' for a, b in items) if items else ''
    fig = f'<div class="figure">{img(photo, alt)}</div>'
    txt = f'''<div>
      <p class="ch-years"><span class="gnum">{letter}</span>{what}</p>
      <h2 class="display display-sm">{name}</h2>
      <p class="lede">{blurb}</p>
      <p>{body}</p>
      {cta}
    </div>'''
    inner = (fig + txt) if flip else (txt + fig)
    return f'''
<div class="gtype">
  <div class="split split-6535">{inner}</div>
  {('<div class="rows">' + li + '</div>') if li else ''}
</div>'''

groups = f'''
<section class="phero grain dark">
  <div class="phero-img">{eager('g2-dinner','A SOJO group around a long dinner table')}</div>
  <div class="wrap">
    <p class="crumb">Groups</p>
    <h1 class="display"><span class="script">Faith grows in</span><br>circles,<br>not rows</h1>
    <p class="lede">A room of four hundred people can still be a room where nobody knows your name.
    Groups are how we fix that.</p>
    {thread('Grow','This is where you find a family. Peace with God is given in a moment. Peace with people gets built at a table, over months, with folks who know your actual week.')}
    <div class="btns">{btn('Browse groups in Church Center',GROUPS,'btn',True)}
      {btn('Not sure where to start?',PHONE_H,'btn btn-ghost')}</div>
  </div>
</section>

<section class="sec">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">Why groups</p>
      <h2 class="display display-sm">Sunday can&rsquo;t<br>do this part</h2>
      <p class="lede">You can attend a church for years and stay a stranger. You cannot sit at
      somebody&rsquo;s table for eight weeks and stay a stranger.</p>
      <p>This is where <strong>grow in peace</strong> actually happens. Prayer requests stop being
      generic. Somebody notices you were gone two weeks in a row. The meal train shows up when it
      goes bad. Every church says community matters; a group is the part where it costs you a
      Tuesday night.</p>
      <p>We run four different kinds, because people need different things at different times &mdash;
      and the one you need in a good year is not the one you need in a hard one.</p>
      <div class="btns">{btn('See all four kinds','#kinds','btn btn-ghost')}</div>
    </div>
    <div class="figure">{img('g2-mill-circle','A SOJO group praying in a circle at the mill')}
      <p class="figcap">A group praying together at the Mill</p></div>
  </div>
</section>

<section class="sec tint" id="kinds">
  <div class="wrap">
    <p class="eyebrow">Four kinds of groups</p>
    <h2 class="display display-sm">Find the one<br>that fits the<br>season you&rsquo;re in</h2>
  </div>

  <div class="wrap gtypes">

    {gtype('01','Connect Groups','Common interests',
      'Community and connection built around something you already love doing.',
      "Hiking, disc golf, moms of littles, motorcycles, board games, running, fishing, coffee. The "
      "point is not the activity &mdash; it is that friendship forms sideways, while you are both "
      "looking at something else. If walking into a Bible study feels like a lot, start here.",
      [], f'<div class="btns">{btn("Browse Connect Groups",GROUPS,"btn",True)}</div>',
      'g2-table','A SOJO Connect Group sharing a meal together')}

    {gtype('02','Community Groups','Scripture, prayer, depth',
      'Groups built around Scripture, praying for one another, and going deeper with God and people.',
      "This is the backbone. You open the Bible together, you pray for each other by name, and over "
      "a season you get honest. Most people who say SOJO became home for them can point at a "
      "Community Group as the reason.",
      [], f'<div class="btns">{btn("Browse Community Groups",GROUPS,"btn",True)}</div>',
      'g2-cfa','A SOJO Community Group praying over one of their own', flip=True)}

    {gtype('03','Care Groups','When life gets heavy',
      'Groups where people are cared for &mdash; and groups where people do the caring.',
      "Some seasons you need somebody to carry something with you. Some seasons you are the one "
      "doing the carrying. Both belong here, and neither one requires you to have it together first.",
      [("SOJO Ink",
        "Writing cards to people in our church. A quiet, powerful way to care for somebody you may never meet &mdash; and one of the easiest first steps in the whole church."),
       ("SOJO Recovery",
        "A group for people with hurts, hang-ups, and habits. No pretending required. PC has been open about his own story with addiction; nobody here is going to be shocked by yours."),
       ("SOJO Grief Recovery",
        "A group to help you mourn the loss of someone &mdash; or something. Grief is not only about funerals, and it does not run on anybody else's schedule."),
       ("SOJO Divorce Care",
        "A group aimed at helping people get through one of the most painful relationship hurts in life. Whatever the story is, you will not be judged for being in it.")],
      f'<div class="btns">{btn("Find a Care Group",GROUPS,"btn",True)} {btn("Talk to somebody first",SMS_HELLO,"btn btn-ghost")}</div>',
      'g2-candlelight','A SOJO Care Group gathered with candles')}

    {gtype('04','Classes','Taught by our leaders',
      'Real teaching from the people who lead this church.',
      "Sometimes you do not need a circle &mdash; you need somebody who has studied this to walk you "
      "through it. Classes run in terms and are open to anybody, whether SOJO is your church or not.",
      [("A Study in Genesis &mdash; Pastor Corey",
        "The book everything else is built on. Where life, peace, and purpose all start, and where they first go wrong."),
       ("SOJO University &mdash; Pastor Dan",
        "Foundational training for people who want to understand the faith they are living in, and lead others in it.")],
      f'<div class="btns">{btn("See current classes",GROUPS,"btn",True)}</div>',
      'n-dan-teach','Pastor Dan teaching a class at SOJO', flip=True)}

  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="eyebrow">What to expect</p>
    <h2 class="display display-sm">The honest<br>version</h2>
    {rows([
      ("It&rsquo;s smaller than you think",
       "Eight to twelve people, usually. Small enough that it matters whether you show up.",
       None),
      ("You will not be put on the spot",
       "Nobody is going to make you pray out loud or read a passage cold. You can sit and listen as long as you need to.",
       None),
      ("You don&rsquo;t need Bible knowledge",
       "Groups are full of people still figuring it out. Bringing a real question is worth more than bringing a right answer.",
       None),
      ("There is almost always food",
       "It is a SOJO group. Of course there is food.",
       None),
      ("Commitment is a season, not a life sentence",
       "Groups run in seasons. Try one; if it is not your fit, try another. Nobody is offended.",
       None),
    ])}
  </div>
</section>

<section class="sec concrete grain columns sheen">
  <div class="wrap">
    <hr class="lane" style="margin-bottom:48px">
    <p class="eyebrow">Getting in</p>
    <div class="split split-6535" style="align-items:end">
      <h2 class="display display-sm">Three ways<br>to start</h2>
      <p class="lede">Every group lives in Church Center &mdash; the same app you use for events and
      giving. Sign-up takes about a minute.</p>
    </div>
    {rows([
      ("Browse what&rsquo;s open in Church Center",
       "Every current group, when and where it meets, who leads it, and whether it has room. Filter by day, by type, or by part of town, then request to join right there.",
       ("Open Church Center Groups",GROUPS,True)),
      ("Tell us what you&rsquo;re looking for",
       "Not sure which one fits? Text us the part of town you are in, what nights work, and what season of life you are in. We will point you at two or three.",
       (f"Call or text {PHONE_D}",PHONE_H,False)),
      ("Come to Discover SOJO first",
       "The last Sunday of every month. Meet leaders, ask questions, and find out where the groups actually are before you commit to one.",
       ("Sign up",DISC,True)),
    ])}
  </div>
</section>

<section class="sec">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">Or lead one</p>
      <h2 class="display display-sm">You don&rsquo;t have to be<br>a Bible scholar</h2>
      <p class="lede">You have to be willing to open your calendar and care about people.</p>
      <p>We provide the training, the material, and a coach. You provide the room and the
      consistency. If a group has ever mattered to you, leading one is how somebody else gets that.</p>
      <p>Connect Groups especially need leaders &mdash; if you already do a thing every week, you are
      most of the way to leading one.</p>
      <div class="btns">{btn('Talk to us about leading',PHONE_H,'btn')}</div>
    </div>
    <div class="figure">{img('st-union-writing','SOJO members writing Scripture together')}</div>
  </div>
</section>

<section class="sec sand center">
  <div class="wrap-narrow">
    <p class="script">One table</p>
    <h2 class="display display-sm">Is all it takes</h2>
    <div class="btns" style="justify-content:center">{btn('Find a group',GROUPS,'btn',True)}
      {btn('Back to next steps','next-steps.html','btn btn-ghost')}</div>
  </div>
</section>
'''
PAGES.append(page('groups.html', 'Groups | SOJO Church, Concord NC',
    'Four kinds of groups at SOJO Church in Concord, NC — Connect Groups, Community Groups, '
    'Care Groups (SOJO Ink, Recovery, Grief Recovery, DivorceCare) and Classes.',
    groups, active='groups.html'))

# ============================== SERVE ========================================
serve = f'''
<section class="phero grain dark">
  <div class="phero-img">{eager('pray','SOJO volunteers praying with someone')}</div>
  <div class="wrap">
    <p class="crumb">Serve</p>
    <h1 class="display"><span class="script">You were gifted</span><br>on purpose</h1>
    <p class="lede">"The greatest among you will be your servant." — Jesus, Matthew 23:11</p>
    {thread('Go','Serving is the other way people find a family here. You show up for a team, and six months later they are the ones showing up for you.')}
    <div class="btns">{btn('Find your spot',PHONE_H,'btn')}</div>
  </div>
</section>

<section class="sec">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">Why it matters right now</p>
      <h2 class="display display-sm">A bigger room<br>needs more hands</h2>
      <p class="lede">On September 6 we walk into a space twice the size of the one we're leaving.
      Twice the doors to hold open. Twice the kids to check in. Twice the first-time guests who
      decide in the first ninety seconds whether this place is for them.</p>
      <p>That's not a staffing problem. That's an invitation.</p>
      <p>Serving isn't filling a slot on a chart. It's the fastest way to stop attending a church and
      start belonging to one — you meet people, you grow, and you get to watch God use something you're
      actually good at.</p>
      <div class="btns">{btn('Say yes',PHONE_H,'btn')}</div>
    </div>
    <div class="figure">{img('welcome','SOJO people connecting after a Sunday service')}</div>
  </div>
</section>

<section class="sec tint">
  <div class="wrap">
    <p class="eyebrow">Where you could land</p>
    <h2 class="display display-sm">Seven teams,<br>one mission</h2>
    {rows([
      ("SOJO Kids",
       "Sunday classrooms, check-in support, event help. Background check required — no exceptions.",
       ("About SOJO Kids","kids.html",False)),
      ("SOJO YTH &amp; SOJO YA",
       "Wednesday-night small group leaders and chaperones for students, plus hosts and cooks for Friday-night young adults. Background check required for anyone with students.",
       ("About Next Gen","next-gen.html",False)),
      ("Worship &amp; Production",
       "Vocalists, instrumentalists, sound, cameras, lights, slides. If you're musical or you like being behind the scenes, there's room.",
       None),
      ("Hospitality",
       "Greeters, coffee bar, parking team. You'd be shocked how much of somebody's first impression rides on one person being genuinely glad they came.",
       None),
      ("Outreach &amp; Missions",
       "Food drives, mission trips, local partnerships. Meeting tangible needs in Jesus' name — here, near, and far.",
       None),
      ("Finance Team",
       "Behind the scenes stewardship — budgeting, giving records, offering. Background check required.",
       None),
      ("Group Leaders",
       "Lead a table. Training and support provided; you don't have to be a Bible scholar, you have to care about people.",
       ("Find a group",GROUPS,True)),
    ])}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="eyebrow">In the community</p>
    <h2 class="display display-sm">Here, near,<br>and far</h2>
    <div class="split split-6535" style="margin-top:34px">
      <div>
        <h3 class="display display-xs">Meals on Wheels</h3>
        <p>Delivering hot meals every Tuesday to seniors and neighbors living with disabilities in
        Cabarrus County. More than a meal — it's a wellness check and, for a lot of folks, the only
        face they'll see that day. You need dependable transportation and to arrive by 10:30am at
        342 Penny Lane, Concord. Weekly, biweekly, or monthly — your call.</p>
        <h3 class="display display-xs" style="margin-top:34px">HellFighters of Concord</h3>
        <p>A local partnership reaching people the church usually misses. Ask us about it.</p>
        <div class="btns">{btn('Ask about outreach',PHONE_H,'btn btn-ghost')}</div>
      </div>
      <div class="figure">{img('n-pc-preach','Pastor Corey preaching at SOJO')}</div>
    </div>
  </div>
</section>

<section class="sec dark grain center">
  <div class="wrap-narrow">
    <p class="script">One of those yeses</p>
    <h2 class="display display-sm">Could be yours</h2>
    <p class="lede">Tell us you're in and we'll help you find the spot that actually fits.</p>
    <div class="btns" style="justify-content:center">{btn(f'Call or text {PHONE_D}',PHONE_H,'btn')}</div>
  </div>
</section>
'''
PAGES.append(page('serve.html', 'Serve at SOJO | SOJO Church, Concord NC',
    'Find your place to serve at SOJO Church in Concord, NC — kids, youth, worship, hospitality, '
    'outreach and more.', serve, active='next-steps.html'))

# ============================== GIVE =========================================
CHALLENGE = CC + "/registrations/events/3833678"   # TODO(PC): confirm the 90-Day Challenge sign-up event

give = f'''
<section class="phero grain dark">
  <div class="phero-img">{eager('n-worship-dark','The SOJO congregation worshipping with hands raised')}</div>
  <div class="wrap">
    <p class="crumb">Giving</p>
    <h1 class="display"><span class="script">Generosity isn&rsquo;t about<br>what God wants from you</span><br>It&rsquo;s what He<br>wants <span class="gold">for</span> you</h1>
    <p class="lede">That is the whole reframe. Giving is not a bill the church sends you. It is a
    door God holds open.</p>
    {thread('Go','This is why we give. Money is how a church goes places its people cannot personally stand: a kids&rsquo; wing, a meal on a Tuesday, a church planted in a town you will never visit.')}
    <div class="btns">{btn('Give now',GIVE,'btn btn-gold',True)}
      {btn('Take the 90-day challenge','#challenge','btn btn-ghost')}</div>
  </div>
</section>

<section class="sec-tight tint">
  <div class="wrap">
    <hr class="lane" style="margin-bottom:30px">
    <p class="eyebrow">On this page</p>
    <div class="jump">
      <a href="#why">Why we give</a>
      <a href="#what">What the Bible says</a>
      <a href="#who">Who gives &amp; how much</a>
      <a href="#when">When to give</a>
      <a href="#how">How to give</a>
      <a href="#challenge">The 90-day challenge</a>
    </div>
  </div>
</section>

<section class="sec" id="why">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">Part one · Why we give</p>
      <h2 class="display display-sm">It was never<br>about the money</h2>
      <p class="lede">Jesus talked about money more than He talked about heaven. Not because He
      needed any of it &mdash; because He knew what it does to us.</p>
      <p>Money is the most honest thing about you. Your bank statement is a spiritual document; it
      records what you actually trust, not what you say you believe. That is why Jesus went after it
      so directly. He wasn't fundraising. He was performing surgery.</p>
      <p>So we give for three reasons, and none of them is a budget.</p>
      <p><strong>It frees us.</strong> Generosity loosens the grip that stuff has on a person. You
      cannot serve two masters, and giving is how you find out which one currently has you.</p>
      <p><strong>It changes us.</strong> Trust is a muscle. Giving is one of the only places you can
      exercise it with something that actually costs you.</p>
      <p><strong>It reaches people.</strong> Kids ministry, students, outreach across Cabarrus County,
      and a building with the doors open. Your giving shows up in somebody's worst week as a meal,
      a room, or a person who came.</p>
      <div class="stripe" aria-hidden="true"></div>
      <p class="pull" style="font-size:clamp(1.4rem,2.8vw,2.1rem)">&ldquo;Where your treasure is,
      there your heart will be also.&rdquo;</p>
      <p class="pull-attr">Matthew 6:21</p>
    </div>
    <div class="figure">{img('sojo-generosity','A SOJO ministry partner receiving a giving check on stage')}
      <p class="figcap">Generosity, handed to somebody who needed it</p></div>
  </div>
</section>

<section class="sec tint" id="what">
  <div class="wrap">
    <p class="eyebrow">What giving is, biblically</p>
    <h2 class="display display-sm">Four words the<br>Bible actually uses</h2>
    <p class="lede">&ldquo;Giving&rdquo; is a flat English word for four different things in
    Scripture. They are not interchangeable, and knowing the difference takes a lot of the
    confusion out.</p>
    {rows([
      ("Firstfruits &mdash; giving off the top",
       "&ldquo;Honor the Lord with your wealth, with the firstfruits of all your crops&rdquo; (Proverbs 3:9). Israel brought the first of the harvest, not the leftovers, before they knew how the rest of the season would go. Firstfruits is a statement about who you think provides.",
       None),
      ("The tithe &mdash; the first tenth",
       "&ldquo;A tenth of the produce of the land&hellip; belongs to the Lord; it is holy&rdquo; (Leviticus 27:30). Abraham tithed before the Law existed (Genesis 14). Jacob pledged it before there was a temple (Genesis 28). Jesus assumed His hearers did it (Matthew 23:23). Ten percent is the historic starting line, not the finish line.",
       None),
      ("Offerings &mdash; giving beyond the tenth",
       "The tabernacle and the temple were both funded by freewill offerings above the tithe (Exodus 35, 1 Chronicles 29). This is where generosity stops being obedience and starts being imagination.",
       None),
      ("Alms &mdash; giving straight to need",
       "&ldquo;Whoever is generous to the poor lends to the Lord&rdquo; (Proverbs 19:17). Jesus assumed it: &ldquo;<em>when</em> you give to the needy&rdquo; (Matthew 6:2), not <em>if</em>. Some of your giving should never pass through an institution at all.",
       None),
    ])}
    <p class="muted" style="margin-top:36px;max-width:64ch">Two more things the New Testament makes
    plain: giving is worship, not transaction (Philippians 4:18 calls it &ldquo;a fragrant
    offering&rdquo;), and it is voluntary. &ldquo;Each of you should give what you have decided in
    your heart to give, not reluctantly or under compulsion, for God loves a cheerful giver&rdquo;
    (2 Corinthians 9:7). Nobody at SOJO is going to check your math.</p>
  </div>
</section>

<section class="sec" id="who">
  <div class="wrap">
    <p class="eyebrow">Who gives &mdash; and how much</p>
    <h2 class="display display-sm">The honest<br>answer</h2>
    <div class="split split-6535">
      <div>
        <p class="lede">Everyone who calls SOJO home. And if you are visiting, not you &mdash; you are
        our guest. Keep your wallet in your pocket.</p>
        <p>Here is the part churches usually fumble. Giving is <strong>for followers of Jesus</strong>,
        because it is a discipleship practice, not a membership fee. If you are still figuring out
        what you believe, you are genuinely off the hook. Come, eat, ask hard questions, take your
        time.</p>
        <p>For those who do follow Him, the New Testament never repeals the tithe and never turns it
        into a tax. It does something harder: it raises the bar and removes the ceiling. Paul's
        instruction is proportional (&ldquo;in keeping with your income&rdquo; &mdash; 1 Corinthians
        16:2), planned, regular, and cheerful. The Macedonians in 2 Corinthians 8 gave beyond their
        means and had to <em>beg</em> for the privilege.</p>
        <p>So the number we teach is <strong>ten percent, first, off the top</strong> &mdash; not as
        a law you'll be judged by, but as the historic benchmark that keeps generosity from drifting
        into whatever happens to be left over. Almost nobody starts there. That is completely fine.
        You are not behind; you are on a ladder.</p>
      </div>
      <div class="figure">{img('family','A SOJO family together on a Sunday morning')}</div>
    </div>

    <p class="eyebrow" style="margin-top:56px">The generosity ladder</p>
    {rows([
      ("Not giving anything","Acknowledge the invitation. That is a real step, and it counts.",None),
      ("Give something","Any amount. The first gift is the hardest one you will ever make and the most important.",None),
      ("Give regularly","Build the habit. Consistency forms you far more than size does.",None),
      ("Give a percentage","Commit to a set share of your income instead of whatever is left at the end of the month.",None),
      ("Give the full tithe","Ten percent, first. Trust Him with the first slice rather than the last.",None),
      ("Give beyond it","Sacrificially, on purpose, to bless people who cannot repay you.",None),
    ])}
    <p class="muted" style="margin-top:28px;max-width:62ch">Find the rung you are on. Take the next
    one. That is the entire strategy.</p>
  </div>
</section>

<section class="sec tint" id="when">
  <div class="wrap split">
    <div class="figure figure-portrait">{img('n-pc-cross','Pastor Corey praying before the cross','portrait')}</div>
    <div>
      <p class="eyebrow">When to give</p>
      <h2 class="display display-sm">Rhythm beats<br>impulse</h2>
      <p class="lede">&ldquo;On the first day of every week, each one of you should set aside a sum
      of money in keeping with your income&rdquo; (1 Corinthians 16:2).</p>
      <p>Notice what Paul builds in: a <strong>set day</strong>, a <strong>set proportion</strong>,
      and a decision made <strong>ahead of time</strong> instead of in the moment. Generosity that
      depends on how you feel on a given Sunday will always lose to whatever else came up that week.</p>
      <p><strong>First, not last.</strong> Firstfruits means the gift comes off the top, before the
      bills line up and make their case. If it waits until the end, it will not survive the month.</p>
      <p><strong>Weekly or per paycheck.</strong> Match the rhythm to how you actually get paid.
      Recurring giving is not laziness &mdash; it is a decision you only have to make once, honored
      automatically every time after.</p>
      <p><strong>Plus the unplanned.</strong> Keep room for the moment a need lands in front of you.
      Some of the best giving you ever do will never appear on a statement.</p>
      <div class="btns">{btn('Set up recurring giving',GIVE,'btn',True)}</div>
    </div>
  </div>
</section>

<section class="sec" id="how">
  <div class="wrap">
    <p class="eyebrow">How to give</p>
    <h2 class="display display-sm">Five ways,<br>pick one</h2>
    {rows([
      ("Online, one time or recurring",
       "The simplest way and the one we recommend. Debit, credit, or bank draft. Set it and forget it, or give as you go.",
       ("Give now",GIVE,True)),
      ("In the Church Center app",
       "Same giving, on your phone, alongside groups and event sign-ups. Search &ldquo;Church Center&rdquo; in your app store and find SOJO Church.",
       ("Open Church Center",CC,True)),
      ("In the room on Sunday",
       "Cash or check during the offering. Guests, this one is not for you.",
       None),
      ("Stock, crypto, or a donor-advised fund",
       "Non-cash giving is tax-smart and often lets people give more than they thought possible without touching their bank account. Appreciated assets in particular can go further than cash.",
       ("Ask us how",PHONE_H,False)),
      ("Toward missions &mdash; here, near and far",
       "Nineteen partners, funded every year &mdash; hunger and foster care in Concord, church plants from here to San Diego, and, through The Timothy Initiative, <strong>one new church planted every month</strong>. Every partner is named on the Outreach page.",
       ("See every partner","missions.html",False)),
      ("Toward the new building",
       f"We are finishing out Gibson Mill &mdash; construction and outfitting both, with the permanent kids space and the coffee shop targeted for early 2027. If you want your giving pointed at the room our city walks into, say so.",
       ("Our new home","new-home.html",False)),
    ])}
  </div>
</section>

{testimony_section()}

<section class="sec concrete grain columns sheen" id="challenge">
  <div class="wrap">
    <hr class="lane" style="margin-bottom:48px">
    <p class="eyebrow">Part two · Practicing Generosity</p>
    <div class="split split-6535" style="align-items:end">
      <h2 class="display">The <span class="gold">90-day</span><br>challenge</h2>
      <p class="lede">A discipleship journey into trust, freedom, and joy. Ninety days of learning
      to live with open hands before God.</p>
    </div>
    <p class="lede" style="margin-top:40px"><strong>This is not a fundraising campaign.</strong>
    It is an invitation to become more like Jesus.</p>
    <p style="max-width:64ch">Generosity is not something a few people happen to be naturally good
    at. It is something followers of Jesus <em>practice</em> &mdash; and practices are what form us.
    In <em>Practicing the Way</em>, John Mark Comer makes the case that spiritual practices shape who
    we are becoming. In <em>The Treasure Principle</em>, Randy Alcorn reframes money through an
    eternal lens: what we do with our resources reveals what we trust and love most.</p>
    <p style="max-width:64ch">Put those together and you get a simple, uncomfortable truth.
    <strong>Generosity is a practice that reorders the heart toward God and His Kingdom.</strong>
    When it becomes a practice, it stops being about pressure and starts being about freedom.</p>
    <div class="btns">{btn('Take the challenge',CHALLENGE,'btn btn-gold',True)}</div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="eyebrow">How the 90 days work</p>
    <h2 class="display display-sm">Four moves</h2>
    {rows([
      ("Pray and ask the Lord",
       "Before you pick a number, ask Him for one. This is the step people skip, and it is the step that makes the other three mean anything.",
       None),
      ("Read the book",
       "<em>The Treasure Principle</em> by Randy Alcorn. We give a copy away free to everybody who signs up &mdash; it has helped millions of believers find the joy of an eternal perspective, and it is short enough to actually finish.",
       ("Sign up and get the book",CHALLENGE,True)),
      ("Take the challenge",
       "Ninety days of consistent, intentional giving at the level God put in front of you. Long enough to become a rhythm instead of a mood.",
       ("Start the 90 days",GIVE,True)),
      ("See what generosity does",
       "In you. Through you. Beyond you. Then decide what you want the next ninety days to look like.",
       None),
    ])}
  </div>
</section>

<section class="sec tint">
  <div class="wrap">
    <p class="eyebrow">Pick your starting line</p>
    <h2 class="display display-sm">Everyone&rsquo;s journey<br>is different</h2>
    <p class="lede">The invitation is the same. The step is not.</p>
    <div class="trio">
      <div>
        <h3 style="margin-top:0">Start giving</h3>
        <p>I want to begin trusting God through the practice of generosity. Whether it is your
        first gift ever or your first consistent one, every step of obedience matters.</p>
        <a class="link" href="{GIVE}" target="_blank" rel="noopener">Give my first gift <span class="arw">&rarr;</span></a>
      </div>
      <div>
        <h3 style="margin-top:0">Increase my giving</h3>
        <p>I want to take another step toward becoming a tither. If you have been giving
        occasionally, this is the season to grow into consistency and move toward the first ten
        percent.</p>
        <a class="link" href="{GIVE}" target="_blank" rel="noopener">Increase my gift <span class="arw">&rarr;</span></a>
      </div>
      <div>
        <h3 style="margin-top:0">Legacy giving</h3>
        <p>I want to give beyond the tithe. Having established the ten percent, I want to invest
        over and above it to expand God's Kingdom and leave something lasting.</p>
        <a class="link" href="{PHONE_H}">Talk to us <span class="arw">&rarr;</span></a>
      </div>
    </div>
    <p class="pull" style="margin-top:64px;max-width:26ch">We don&rsquo;t give <em>to</em> a church.
    We give <em>through</em> one.</p>
    <p class="pull-attr">In me · Through me · Beyond me</p>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <h2 class="display display-sm">Straight<br>answers</h2>
    {faq([
      ("Is this about the church needing money?",
       "<p>No. This journey is about discipleship and trust, not pressure. If the only thing that changed in ninety days was our bank balance, we would consider it a failure.</p>"),
      ("What if I'm struggling financially?",
       f"<p>Then generosity should never be fear-driven, and we mean that. If money is genuinely tight, we would rather pray with you and help you build a plan than take your last twenty dollars. Call or text us at {PHONE_D} &mdash; that conversation stays between us.</p>"),
      ("Why recurring giving?",
       "<p>Because it turns generosity into a steady practice instead of a sporadic action. You make the decision once, prayerfully, instead of re-litigating it every Sunday against whatever else came up that week.</p>"),
      ("Is generosity only about giving to the church?",
       "<p>No. Generosity is a way of life &mdash; your time, your table, your attention, your money. Giving through the church is one meaningful way we practice it together, and Scripture also calls us to give directly to people in need.</p>"),
      ("Where does my money actually go?",
       "<p>Ministry and staff, kids and students, outreach across Cabarrus County, and the building at Gibson Mill. If you want a detailed breakdown, ask &mdash; we will show you.</p>"),
      ("Can I designate my gift?",
       "<p>Yes. You can give toward general ministry or toward the new building specifically. Both options are in the online giving form.</p>"),
      ("Is my gift tax-deductible?",
       "<p>Yes. SOJO Church is a registered nonprofit and you will receive an annual giving statement. For anything involving stock, crypto, or a donor-advised fund, talk to your tax advisor &mdash; and talk to us, because we can usually make it simpler than you expect.</p>"),
    ])}
  </div>
</section>

<section class="sec sand center">
  <div class="wrap-narrow">
    <p class="script">Wherever you are on the ladder</p>
    <h2 class="display display-sm">Take the<br>next rung</h2>
    <div class="btns" style="justify-content:center">{btn('Give now',GIVE,'btn',True)}
      {btn('Take the 90-day challenge',CHALLENGE,'btn btn-ghost',True)}</div>
  </div>
</section>
'''
PAGES.append(page('give.html', 'Giving | SOJO Church, Concord NC',
    'Why we give, what the Bible says about giving, five ways to give at SOJO Church — and the 90-Day Practicing Generosity Challenge.',
    give, active='give.html'))

# ============================== WATCH ========================================
# Sermon slider: the YouTube IFrame API reads the uploads playlist right in the
# visitor's browser (no server, no API key), then builds thumbnail tiles that
# swap videos into the player. If the API can't load, the plain embed still works.
WATCH_JS = '''
<script>
(function(){
  var tag=document.createElement('script');tag.src='https://www.youtube.com/iframe_api';
  document.head.appendChild(tag);
  var player;
  window.onYouTubeIframeAPIReady=function(){
    player=new YT.Player('ytiframe',{events:{onReady:build}});
  };
  function build(){
    var tries=0,t=setInterval(function(){
      var ids=(player.getPlaylist&&player.getPlaylist())||[];tries++;
      if(ids.length||tries>25){clearInterval(t);render(ids);}
    },400);
  }
  function render(ids){
    var s=document.getElementById('yslider');if(!s||!ids.length)return;
    ids.slice(0,12).forEach(function(id,i){
      var b=document.createElement('button');b.type='button';
      b.className='yslide'+(i===0?' on':'');
      b.setAttribute('aria-label','Play message '+(i+1));
      b.innerHTML='<img loading="lazy" alt="" src="https://i.ytimg.com/vi/'+id+'/hqdefault.jpg"><span class="yplay" aria-hidden="true">&#9654;</span>';
      b.addEventListener('click',function(){
        player.playVideoAt(i);
        var on=s.querySelector('.yslide.on');if(on)on.classList.remove('on');
        b.classList.add('on');
        document.getElementById('ytiframe').scrollIntoView({behavior:'smooth',block:'center'});
      });
      s.appendChild(b);
    });
    s.hidden=false;
  }
})();
</script>'''

watch = f'''
<section class="phero grain dark">
  <div class="phero-img">{eager('n-worship-duo','SOJO worship leaders singing together')}</div>
  <div class="wrap">
    <p class="crumb">Watch &amp; Listen</p>
    <h1 class="display"><span class="script">Why wait</span><br>for Sunday</h1>
    <p class="lede">Every message, online, free, whenever you want it.</p>
    {thread('Know','You can start getting to know Life from your couch. You just cannot finish there &mdash; abundant life has other people in it.')}
    <div class="btns">{btn('Watch on YouTube',YT,'btn',True)}
      {btn('Listen to the podcast',POD,'btn btn-ghost',True)}</div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="eyebrow">Newest first</p>
    <div class="split split-6535" style="align-items:end;margin-bottom:38px">
      <h2 class="display display-sm">This week&rsquo;s<br>message</h2>
      <p class="lede">Missed Sunday, or want to hear it again? The most recent message is always
      right here.</p>
    </div>
    <div class="yframe yframe-sm"><iframe id="ytiframe" src="{YT_EMBED}&amp;enablejsapi=1"
      title="This week's message from SOJO Church" loading="lazy"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe></div>
    <div class="yslider" id="yslider" aria-label="Recent messages" hidden></div>
    {WATCH_JS}
    <div class="btns">{btn('All messages on YouTube',YT_PLAYLIST,'btn',True)}
      {btn('Listen to the podcast',POD,'btn btn-ghost',True)}</div>
  </div>
</section>

<section class="sec tint">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">Start here</p>
      <h2 class="display display-sm">Two minutes<br>on who we are</h2>
      <p class="lede">If you only watch one thing on this site, watch this one.</p>
      <p>It is the short version of everything else on these pages &mdash; who SOJO is, what we are
      for, and what you would actually walk into on a Sunday morning.</p>
      <div class="btns">{btn('Plan your visit','plan-a-visit.html')}</div>
    </div>
    {video("Welcome to SOJO Church")}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="eyebrow">Three ways in</p>
    <h2 class="display display-sm">However you<br>take it in</h2>
    {rows([
      ("Watch the service",
       "Full Sunday services and individual messages on YouTube. Subscribe and you'll know the moment a new one is up.",
       ("YouTube",YT_PLAYLIST,True)),
      ("Listen on the drive",
       "The SOJO podcast — same messages, in your ears, on Apple Podcasts, Spotify, or wherever you listen.",
       ("Podcast",POD,True)),
      ("Follow along all week",
       "Instagram and Facebook for what's happening between Sundays, and Linktree for whatever we're pointing at this week.",
       ("Instagram",IG,True)),
    ])}
  </div>
</section>

<section class="sec">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">Online is a start</p>
      <h2 class="display display-sm">But a screen<br>can't hug you</h2>
      <p class="lede">Watch as long as you need to. Then come sit in the room.</p>
      <p>You can learn a lot about a church from a video. You can't learn whether these are your
      people until you're standing next to them. When you're ready, we'll be at the guest table
      looking for you.</p>
      <div class="btns">{btn('Plan your visit','plan-a-visit.html')}</div>
    </div>
    <div class="figure">{img('k-worship','SOJO Kids worshipping in their own room')}</div>
  </div>
</section>
'''
PAGES.append(page('watch.html', 'Watch &amp; Listen | SOJO Church, Concord NC',
    'Watch SOJO Church services and messages online, or listen to the podcast anywhere you get '
    'your podcasts.', watch))


# ============================== SWAG =========================================
def way(f, name, hexv):
    return (f'<div class="way"><div class="shot">{img("swag/"+f, name+" SOJO tee")}</div>'
            f'<div class="nm"><span class="dot" style="background:{hexv}"></span>{name}</div></div>')

SIZES = ('<p class="sizeline">Sizes ' +
         ' · '.join(['XS','S','M','L','XL','2XL','3XL']) + '</p>')

swag_page = f'''
<section class="phero grain dark">
  <div class="phero-img">{eager('shell-corridor','The mill corridor at Gibson Mill')}</div>
  <div class="wrap">
    <p class="crumb">Swag</p>
    <h1 class="display"><span class="script">Wear it into</span><br>the week</h1>
    <p class="lede">A shirt is a small thing. It's also the only sermon most people in Concord
    will read on a Tuesday.</p>
    {thread('Go','Going in your anointed purpose sometimes looks like a shirt in a grocery store. You are the only sermon some people in Concord will read this week.')}
    <div class="btns">{btn('How to get one','#order','btn')}</div>
  </div>
</section>

<section class="sec">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">Why we make it</p>
      <h2 class="display display-sm">You're a<br>walking <span class="ul">front door</span></h2>
      <p class="lede">Somebody at your gym, your job site, your kid's practice is going to read the
      front of your shirt and ask about it. That's the whole point.</p>
      <p>We didn't design these to look churchy. We designed them so you'd actually wear them —
      washed-out earth tones, heavyweight cotton, a mark that reads as a brand instead of a billboard.
      If it lives in the back of your drawer, it isn't doing its job.</p>
      <p>Every dollar over cost goes back into the room at Gibson Mill.</p>
    </div>
    <div class="figure">{img('swag/tee-inset-charcoal','SOJO Church tee in charcoal')}</div>
  </div>
</section>

<section class="sec tint">
  <div class="wrap">
    <p class="eyebrow">The collection</p>
    <h2 class="display display-sm">The tees:<br>three marks,<br>nine colorways</h2>

    <div class="drops">

      <div class="drop">
        <div class="drop-head"><h3>The Inset</h3><span class="price">$28 · TEE</span></div>
        <p>The full wordmark with CHURCH set inside the letterforms. The loudest of the three, and
        the one people ask about most.</p>
        <div class="ways">
          {way('tee-inset-charcoal','Charcoal','#4E4D49')}
          {way('tee-inset-mauve','Mauve','#937070')}
          {way('tee-inset-mint','Mint','#C3CFCB')}
        </div>
        {SIZES}
      </div>

      <div class="drop">
        <div class="drop-head"><h3>The Block</h3><span class="price">$28 · TEE</span></div>
        <p>SOJO reversed out of a solid charcoal square. Clean, graphic, reads from across a parking
        lot.</p>
        <div class="ways">
          {way('tee-block-bone','Bone','#DED9D3')}
          {way('tee-block-sage','Sage','#A4A693')}
          {way('tee-block-grey','Grey','#A7A49E')}
        </div>
        {SIZES}
      </div>

      <div class="drop">
        <div class="drop-head"><h3>Left Chest</h3><span class="price">$25 · TEE</span></div>
        <p>Small stacked mark over the heart. For the folks who want to wear it Monday through
        Friday without explaining themselves every time.</p>
        <div class="ways">
          {way('tee-chest-slate','Slate','#96A19D')}
          {way('tee-chest-tan','Tan','#B6AA8D')}
          {way('tee-chest-celery','Celery','#CBC797')}
        </div>
        {SIZES}
      </div>


    </div>

    <hr class="lane" style="margin:clamp(56px,7vw,96px) 0 clamp(44px,5vw,64px)">
    <p class="eyebrow">Beyond the tee</p>
    <h2 class="display display-sm">Carry it, wear it,<br>drink out of it</h2>

    <div class="drops">

      <div class="drop">
        <div class="drop-head"><h3>Headwear</h3><span class="price">$28</span></div>
        <p>The Concord badge on a soft-crown dad hat, and the stacked mark on a structured snapback.
        One goes with everything; the other goes with a hoodie.</p>
        <div class="ways ways-3">
          {way('sw-dadhat','Dad Hat &middot; Bone','#E6E2DA')}
          {way('sw-snapback','Snapback &middot; Black','#2B2B2D')}
        </div>
        <p class="sizeline">One size &middot; Adjustable</p>
      </div>

      <div class="drop">
        <div class="drop-head"><h3>Drinkware</h3><span class="price">$30 BOTTLE &middot; $26 TUMBLER</span></div>
        <p>Insulated stainless with the Concord badge. The bottle holds cold all day; the tumbler is
        the one that ends up on your desk and never comes home.</p>
        <div class="ways ways-3">
          {way('sw-bottle-black','Bottle &middot; Black','#26262A')}
          {way('sw-bottle-white','Bottle &middot; White','#F2F2F2')}
          {way('sw-tumbler','Tumbler &middot; White','#F4F4F4')}
        </div>
        <p class="sizeline">Bottle 24oz &middot; Tumbler 20oz &middot; Hand wash</p>
      </div>

      <div class="drop">
        <div class="drop-head"><h3>Everyday carry</h3><span class="price">$22 TOTE &middot; $16 NOTEBOOK &middot; $14 POUCH</span></div>
        <p>Heavyweight canvas tote with navy handles, a hardcover notebook with the gold mark and an
        elastic band, and a zip pouch that holds pens, cords, or everything currently loose in your
        bag. Groceries, sermon notes, and the Discover More class, covered.</p>
        <div class="ways ways-3">
          {way('sw-tote','Canvas Tote &middot; Natural','#E4DCC4')}
          {way('sw-notebook','Notebook &middot; Black','#1F1F21')}
          {way('sw-pouch','Zip Pouch &middot; Natural','#EFEAE0')}
        </div>
        <p class="sizeline">Tote 15&times;16in &middot; Notebook A5, lined &middot; Pouch 9&times;5in</p>
      </div>

      <div class="drop">
        <div class="drop-head"><h3>The Polo</h3><span class="price">$38</span></div>
        <p>Left-chest mark on a performance polo. Built for the serve teams, the golf tournament, and
        anybody who has to look put together on a Tuesday.</p>
        <div class="ways ways-3">
          {way('sw-polo','Polo &middot; Black','#232326')}
        </div>
        <p class="sizeline">Sizes S &middot; M &middot; L &middot; XL &middot; 2XL &middot; 3XL</p>
      </div>

    </div>
  </div>
</section>

<section class="sec concrete grain columns sheen" id="order">
  <div class="wrap">
    <hr class="lane" style="margin-bottom:48px">
    <p class="eyebrow">How to get one</p>
    <div class="split split-6535" style="align-items:end">
      <h2 class="display display-sm">Three ways,<br>all of them<br>simple</h2>
      <p class="lede">The full online store is coming. Until it lands, here is exactly how to get a
      shirt this week &mdash; no account, no minimum, no waiting on shipping.</p>
    </div>
    {rows([
      ("Grab one Sunday at the Mill",
       "The swag table is in the lobby before and after both services. Try it on, pick your size, walk out wearing it. Cash, card, or tap.",
       ("Plan your visit","plan-a-visit.html",False)),
      ("Text us and we&rsquo;ll set it aside",
       f"Send the mark, the color, and the size to {PHONE_D}. We will hold it at the guest table with your name on it and you can pay when you pick it up.",
       (f"Text {PHONE_D}",PHONE_H,False)),
      ("Watch Church Center",
       "New drops, restocks, and pre-orders get posted in the Church Center app alongside events and giving. It is also where the online store will live when it opens.",
       ("Open Church Center",CC,True)),
    ])}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="eyebrow">The details</p>
    <h2 class="display display-sm">Straight<br>answers</h2>
    {faq([
      ("What's the fit like?",
       "<p>Unisex, true to size, slightly relaxed through the body. If you like a boxier fit, size up one. Sizes run XS through 3XL — and we stock the big sizes, not just the ones on the poster.</p>"),
      ("Will it shrink?",
       "<p>Pre-shrunk cotton. Wash cold, tumble low and it'll hold. Hot dryer is how you turn a large into a medium.</p>"),
      ("Do you have kids' sizes?",
       "<p>Not yet. It's on the list — tell us if you want them and it moves up the list.</p>"),
      ("Where does the money go?",
       "<p>Cost of the shirt comes off the top. Everything past that goes into finishing the room at Gibson Mill. Nobody's making a margin here.</p>"),
      ("Can I get one if I've never been to SOJO?",
       "<p>Yes. And then you should come see the room you're advertising.</p>"),
    ])}
  </div>
</section>

<section class="sec sand center">
  <div class="wrap-narrow">
    <p class="script">One more thing</p>
    <h2 class="display display-sm">Wear it<br>somewhere new</h2>
    <p class="lede">The shirt doesn't do anything hanging in your closet. Put it on and go somewhere
    people don't know you yet.</p>
    <div class="btns" style="justify-content:center">{btn('How to get one','#order','btn')}
      {btn('Plan a visit','plan-a-visit.html','btn btn-ghost')}</div>
  </div>
</section>
'''
PAGES.append(page('swag.html', 'SOJO Swag | SOJO Church, Concord NC',
    'SOJO Church swag — tees in nine colorways, hats, insulated drinkware, a canvas tote, '
    'a notebook and a polo. Grab one Sunday at Gibson Mill.', swag_page))


# ============================== OUR STORY ====================================
def chapter(num, years, title, lede, paras, gal, place):
    body = ''.join(f'<p>{x}</p>' for x in paras)
    return f'''
<div class="chapter">
  <div class="ch-head">
    <span class="ch-num">{num}</span>
    <div>
      <p class="ch-years">{years}</p>
      <h2 class="display display-sm">{title}</h2>
    </div>
  </div>
  <div class="ch-body">
    <p class="lede">{lede}</p>
    {body}
    <p class="ch-place">{place}</p>
  </div>
  <div class="gal gal-cap ch-gal">{gal}</div>
</div>'''

story_page = f'''
<section class="phero grain dark">
  <div class="phero-img">{eager('st-drivein-crowd','SOJO Church meeting in a gravel parking lot during 2020')}</div>
  <div class="wrap">
    <p class="crumb">Our Story</p>
    <h1 class="display"><span class="script">Seven years,</span><br>five rooms</h1>
    <p class="lede">A living room. A school cafeteria. An ice cream shop parking lot. A downtown
    storefront. And now a hundred-year-old mill.</p>
    {thread('Know &middot; Grow &middot; Go','Five rooms, and the same thing happening in every one of them: people meeting Life, being formed by Him, and getting sent from Him.')}
    <p class="muted" style="max-width:60ch">God has never once given us the room we asked for.
    He keeps giving us the one we needed next.</p>
  </div>
</section>

<section class="sec">
  <div class="wrap chapters">

    {chapter('01','November 2017','A living room<br>in Concord',
      'Before there was a church, there were two people and a couch.',
      ["Corey and Betsy Alley started SOJO in their living room in November 2017. The plan was small "
       "on purpose: house churches inside apartment complexes, reaching people who would never drive "
       "to a church building.",
       "There was no stage, no band, no budget. There was a conviction — that a church shouldn't exist "
       "for itself, and that if it closed its doors, the city around it should notice."],
      f"""{gi('g-wide','st-livingroom','SOJO Church gathered in the Alley living room in 2017','2017 · The living room','Where it started. No stage, no band, no budget — just people in a house.')}""",
      'The Alley living room · Concord, NC')}

    {chapter('02','2018 – March 2020','New Life,<br>then a school<br>cafeteria',
      'Before Weddington Hills there was New Life Church — and then twenty-five people who decided to go together.',
      ["The living room outgrew the living room. We gathered at <strong>New Life Church</strong> while "
       "the thing took shape: worship in a fellowship hall, folding chairs, a serving window along "
       "one wall.",
       "Then came the decision. <strong>Twenty-five people moved from New Life to Weddington Hills "
       "Elementary as a group</strong> — not a launch team assembled on paper, but a room full of "
       "folks who had already been doing this together and said yes to doing it somewhere harder.",
       "First public service in the school cafeteria: <strong>February 24, 2019</strong>. Folding "
       "chairs on checkered tile. A rolling stage under a school mural. Setup crew in at 6am, "
       "tear-down finished before the custodian locked up.",
       "The one-year anniversary landed on March 8, 2020. Nobody in that room knew it would be the "
       "last Sunday there. A week later the world shut down and we never got to go back."],
      f"""{gi('g-half','st-newlife','SOJO gathered for worship at New Life Church','New Life Church','Worship in a fellowship hall while the thing took shape.')}
      {gi('g-half','st-the25','The twenty-five people who moved together to Weddington Hills Elementary','The twenty-five','The group that moved from New Life to Weddington Hills together. This is the church before it looked like one.')}
      {gi('g-half','st-union-setup','SOJO Church meeting in the cafeteria at Weddington Hills Elementary','The cafeteria','Folding chairs, a school mural, a rolling stage. Set up and torn down every single Sunday.')}
      {gi('g-half','st-drivein-tailgate','Preaching from the cafeteria stage with hands raised in the room','Sunday morning','Hands up in a lunchroom. Nobody cared what the room was.')}
      {gi('g-third','st-union-toddler','A boy being served food at a SOJO gathering','Always food','Some things have not changed in nine years.')}
      {gi('g-third','st-drivein-crowd','SOJO members together in matching That SOJO Life shirts','That SOJO Life','The early crew, in the first shirts we ever printed.')}
      {gi('g-third','st-school-food','A meal shared at an early SOJO gathering','The table','Before there was a building there was a table.')}""",
      'New Life Church, then Weddington Hills Elementary · Concord, NC')}
    {chapter('03','May – November 2020','An ice cream shop<br>parking lot',
      "Drive-in church at Papa Robb's. Gravel, lawn chairs, a truck bed for a pulpit.",
      ["PC preached standing in the back of a pickup with his phone in one hand. People worshipped "
       "from car roofs, tailgates, and folding chairs in the grass. The sound came through FM radio "
       "and a couple of speakers that never quite behaved.",
       "It was a scary season for the world. It is still, hands down, one of the most special seasons "
       "this church has ever had. Nobody came to a parking lot in July because the room was nice. "
       "They came because they needed each other."],
      f"""{gi('g-third','st-union-worship','Pastor Corey preaching outdoors with his phone raised in 2020','The pulpit','A truck bed, a wired mic, and a phone for notes.')}
      {gi('g-third','st-union-room','A man worshipping while standing on a car roof at drive-in church','On the roof','Church happened wherever you could stand.')}
      {gi('g-third','st-school-preach','A family sitting on a tailgate during drive-in church','The tailgate','Sunday best, on a truck bed, in a gravel lot.')}
      {gi('g-wide','st-union-preach','Families gathered in the gravel lot for drive-in church','The parking lot','Lawn chairs, kids on hips, ninety degrees. They kept coming.')}""",
      "Papa Robb's · Concord, NC")}

    {chapter('04','October 2020 – August 2026','848 Union Street.<br>Six years.',
      'The first building SOJO ever got to call its own.',
      ["We walked into a bare downtown storefront in October 2020 — concrete floors, black "
       "pipe-and-drape, cables taped down by hand. Before the first service, people wrote Scripture "
       "straight onto the walls in marker. Psalm 133. Romans 5:8. <em>Unless the Lord builds the "
       "house.</em> Then we painted over it and built on top of it.",
       "But the bare room is only year one, and it is not the part that matters. <strong>Six years "
       "happened in there.</strong> The chairs filled in. A kids wing appeared where storage used "
       "to be. Students who walked in during sixth grade left for college. People got baptized in a "
       "portable tank in front of everybody they knew.",
       "Babies were dedicated. Marriages got put back together. Somebody walked in on the worst week "
       "of their life and walked out with people. That is what a building is actually for, and none "
       "of it shows up in a photograph of an empty room.",
       "We are not leaving Union Street behind. We are carrying it with us."],
      f"""{gi('g-half','st-drivein-preach','Worship in front of the hand-painted wall at Union Street','Year one · Unless the Lord builds the house','Psalm 127, painted across the front wall by hand before the room was finished.')}
      {gi('g-half','st-school-wide','A volunteer running cables to set up for Sunday','Year one · Six a.m.','Somebody taped these cables down every single week until the room was finally ours.')}
      {gi('g-third','st-union-baptism','Church members writing Scripture on the wall before it was painted','Year one · Writing on the walls','Before we painted, people wrote Scripture onto the drywall. It is still under there.')}
      {gi('g-third','st-drivein-worship','The congregation gathered in the Union Street room','The room fills in','Bare concrete and every chair we owned — and then we needed more chairs.')}
      {gi('g-third','st-school-food','A toddler walking down the hallway at SOJO','Kids grew up here','A hallway a whole generation learned to walk down.')}
      {gi('g-half','k-tunnel','A child running through a tunnel of cheering volunteers','Later years · The tunnel','What a Sunday morning became once there were enough of us to make one.')}
      {gi('g-half','n-baptism-joy','A man celebrated in the baptism tank at SOJO','Later years · The tank','Baptisms in a portable tank, in front of everybody they knew.')}
      {gi('g-third','sojo-dedication','A family dedicating their newborn at SOJO','Later years · Dedications','Babies handed back to God in the same room their parents got found in.')}
      {gi('g-third','sojo-testimony','A SOJO member reading her testimony out loud','Later years · Stories out loud','People telling the truth about their lives into a microphone.')}
      {gi('g-third','y-sing','SOJO students leading worship','Later years · The next ones','Students who showed up in sixth grade, leading worship by twelfth.')}""",
      '848 Union Street S · Concord, NC')}

  </div>
</section>

<section class="sec concrete grain columns sheen">
  <div class="wrap">
    <div class="chapter">
      <div class="ch-head">
        <span class="ch-num">05</span>
        <div>
          <p class="ch-years">September 2026</p>
          <h2 class="display display-sm">A hundred-year-old<br>mill</h2>
        </div>
      </div>
      <div class="ch-body">
        <p class="lede">{MOVE}, 2026 — first Sunday at {WAYF}.</p>
        <p>Twice the space. Four hundred seats instead of two hundred thirty. Kids and youth rooms
        four times the size. And, by early 2027, a coffee shop with the doors open all week — so
        somebody who'd never walk into a church on Sunday can find us on a Wednesday afternoon.</p>
        <p>Same brick somebody else laid a century ago. Same conviction we started with in that
        living room. We just keep needing bigger rooms.</p>
        <p class="ch-place">325 McGill Ave NW, Suite 148 · Concord, NC 28027</p>
      </div>
      <div class="gal gal-cap ch-gal">
        {gi('g-half','shell-wide','The mill floor before build-out, August 2026','August 2026','The room as it stands today. Photographed, not rendered.')}
        {gi('g-half','r-room','Rendering of the new SOJO worship room','The plan','A rendering of the same room, with the chairs in.')}
      </div>
    </div>
  </div>
</section>

<section class="sec center">
  <div class="wrap-narrow">
    <p class="script">Chapter six</p>
    <h2 class="display display-sm">Hasn't been<br>written yet</h2>
    <p class="lede">Every room on this page started with somebody deciding to show up once.</p>
    <div class="btns" style="justify-content:center">{btn('Plan your visit','plan-a-visit.html')}
      {btn('See the new home','new-home.html','btn btn-ghost')}</div>
  </div>
</section>
'''
PAGES.append(page('our-story.html', 'Our Story | SOJO Church, Concord NC',
    'Seven years of SOJO Church in Concord, NC — from a living room in 2017 to a school cafeteria, '
    'a drive-in parking lot, six years on Union Street, and now Gibson Mill.',
    story_page, active='about.html'))

# ============================== KNOW: YADA ===================================
yada_page = f'''
<section class="phero grain dark">
  <div class="phero-img">{eager('n-worship-dark','Hands raised in worship in a dark room at SOJO Church')}</div>
  <div class="wrap">
    <p class="crumb">Know &middot; Part One</p>
    <h1 class="display"><span class="script">To be</span><br>Known all the<br>way <span class="gold">through</span></h1>
    <p class="lede">The Bible has a word for knowing that goes deeper than facts.
    It&rsquo;s the difference between knowing <em>about</em> God and actually knowing him.</p>
  </div>
</section>

<section class="sec">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">The word</p>
      <h2 class="display display-sm">Yada</h2>
      <p class="lede">In Hebrew, the language most of the Old Testament was written in,
      the word for &ldquo;know&rdquo; is <strong>yada</strong> (&#1497;&#1464;&#1491;&#1463;&#1506;). And it almost never means
      &ldquo;has the right information.&rdquo;</p>
      <p>Yada is knowing by <strong>experience</strong>. It&rsquo;s how a farmer knows his land, how a
      craftsman knows the grain of the wood, how a husband knows his wife. It&rsquo;s knowledge you
      can only get by being close &mdash; over time, through seasons, with your hands in it.
      Genesis uses this exact word for the deepest intimacy two humans can share.</p>
      <p>So when the prophets say God wants to be <em>known</em>, they are not asking you to pass
      a theology quiz. You can memorize somebody&rsquo;s biography and never once sit at their
      table. God is after the table.</p>
      <p class="pull" style="margin-top:34px">&ldquo;Let the one who boasts, boast in this: that he
      understands and knows me.&rdquo;</p>
      <p class="pull-attr">Jeremiah 9:24, CSB</p>
    </div>
    <div class="figure">
      {img('candles','Candlelight at a SOJO Church prayer night')}
      <p class="figcap">Prayer night &middot; SOJO Church</p>
    </div>
  </div>
</section>

<section class="sec tint">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">Why it matters</p>
      <h2 class="display display-sm">Jesus defined<br>eternal life &mdash;<br>and it&rsquo;s this</h2>
      <p class="pull" style="margin-top:10px">&ldquo;This is eternal life: that they may know you, the only
      true God, and the one you have sent &mdash; Jesus Christ.&rdquo;</p>
      <p class="pull-attr">John 17:3, CSB</p>
      <p>Read that again slowly. Jesus didn&rsquo;t define eternal life as a place you go when you
      die. He defined it as a <strong>relationship you can start now</strong>. Knowing God &mdash;
      yada-knowing him &mdash; is not the homework you do to get the life. It <em>is</em> the life.</p>
      <p>That&rsquo;s why religion by itself leaves people empty. Rules without relationship is a
      biography without a friendship. God told Israel plainly what he was after: &ldquo;I desire...
      the knowledge of God more than burnt offerings&rdquo; (Hosea 6:6). He still does.</p>
    </div>
    <div class="figure">
      {img('w-bright','The SOJO congregation in worship on a Sunday morning')}
      <p class="figcap">Sunday morning &middot; SOJO Church</p>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="eyebrow">Where to start</p>
    <h2 class="display display-sm" style="margin-bottom:34px">Knowing starts<br>with showing up</h2>
    {rows([
      ("Get close", "Yada-knowledge only happens near. Be in the room &mdash; Sundays at 9 &amp; 11am. Worship is not a performance you watch; it&rsquo;s a table you pull up to.", ("Plan a visit","plan-a-visit.html",False)),
      ("Read his story", "Start with the Gospel of John &mdash; one chapter a day for three weeks. Don&rsquo;t study it like a textbook. Read it like you&rsquo;re getting to know someone.", None),
      ("Talk to him honestly", "Prayer isn&rsquo;t a script. Tell God the true thing, even if the true thing is &ldquo;I&rsquo;m not sure you&rsquo;re there.&rdquo; He has never once been scared off by honesty.", None),
    ])}
    <div class="btns" style="margin-top:40px">{btn('Next: God&rsquo;s plan for life','gods-plan.html')}
    {btn('Talk to a human',SMS_HELLO,'btn btn-ghost')}</div>
  </div>
</section>
{thread('know','Knowing God is not step one of the life. It is the life.')}
'''
PAGES.append(page('yada.html', 'Yada — Knowing God | SOJO Church, Concord NC',
    'Yada — the Hebrew word for knowing God by experience, not just information. '
    'Why Jesus defined eternal life as knowing God, and where to start.',
    yada_page, active='yada.html'))

# ============================== KNOW: GOD'S PLAN =============================
plan_page = f'''
<section class="phero grain dark">
  <div class="phero-img">{eager('greeting','The SOJO family gathered outside under the We Are mural')}</div>
  <div class="wrap">
    <p class="crumb">Know &middot; Part Two</p>
    <h1 class="display"><span class="script">From the beginning,</span><br>a plan to bring<br>us <span class="gold">home</span></h1>
    <p class="lede">The Bible is not a rulebook with a story stuck on. It&rsquo;s one story &mdash;
    God making a good world, losing it to us, and refusing to give up on getting it back.</p>
  </div>
</section>

<section class="sec">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">Genesis &middot; The garden</p>
      <h2 class="display display-sm">Made for<br>partnership</h2>
      <p class="lede">Page one of the Bible says you were made <strong>in the image of God</strong> &mdash;
      and then given a job.</p>
      <p>Eden isn&rsquo;t just a nice backyard. In Genesis, the garden is the place where God&rsquo;s
      space and our space <strong>overlap</strong> &mdash; heaven and earth in the same address. And humans
      aren&rsquo;t the audience. God plants the garden and then hands Adam the work: &ldquo;to work it
      and watch over it&rdquo; (Genesis 2:15). Partners. Co-workers. Gardeners of a world God
      called <em>very good</em>.</p>
      <p>Then Genesis 3. We decided we&rsquo;d rather define good and evil ourselves than trust the
      One who knows. The partnership broke, and we walked east, out of the garden. Every ache
      you&rsquo;ve ever felt for a world that works &mdash; that&rsquo;s homesickness.</p>
      <p>But watch what God does next. He doesn&rsquo;t walk away. The whole Torah is God coming
      <em>after</em> his people &mdash; calling Abraham and making him a promise that bends history:
      &ldquo;all the peoples on earth will be blessed through you&rdquo; (Genesis 12:3). One family,
      chosen to carry the rescue to everybody.</p>
    </div>
    <div class="figure">
      {img('k-bibles','Kids reading their Bibles on the floor at SOJO Church')}
      <p class="figcap">The story &middot; Genesis to now</p>
    </div>
  </div>
</section>

<section class="sec tint">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">Psalm 1 &middot; Two ways to live</p>
      <h2 class="display display-sm">The tree by<br>the stream</h2>
      <p class="pull" style="margin-top:10px">&ldquo;He is like a tree planted beside flowing streams
      that bears its fruit in its season, and its leaf does not wither.&rdquo;</p>
      <p class="pull-attr">Psalm 1:3, CSB</p>
      <p>The songbook of the Bible opens with a choice between two ways. One way looks free but
      dries up. The other looks slow &mdash; roots, seasons, delight in God&rsquo;s instruction &mdash; and
      ends up <strong>alive</strong>. Planted, not potted. Fruitful, not frantic.</p>
      <p>This psalm is one of SOJO&rsquo;s anchor texts, because it tells the truth about formation:
      God&rsquo;s plan for your life is not a lightning strike. It&rsquo;s a tree. It grows the way trees
      grow &mdash; slowly, deeply, and on purpose.</p>
    </div>
    <div class="figure">
      {img('n-girl-sing','Three generations of one family worshiping together at SOJO Church')}
      <p class="figcap">Rooted &middot; SOJO Church</p>
    </div>
  </div>
</section>

<section class="sec dark grain">
  <div class="wrap">
    <p class="eyebrow">Through the lens of Jesus</p>
    <div class="split split-6535" style="align-items:end">
      <h2 class="display display-sm">The Way back<br>to the garden</h2>
      <p class="lede">Every thread of the story pulls tight in one person.</p>
    </div>
    <p style="max-width:62ch;margin-top:26px">Jesus is what the plan was always moving toward &mdash;
    God&rsquo;s space and our space overlapping again, this time in a person. He lived the truly
    human life we couldn&rsquo;t, died the death our rebellion earned, and walked out of the grave
    to start the new creation early. When they asked him about the plan, he didn&rsquo;t hand out a
    map. He said, &ldquo;I am the way, the truth, and the life&rdquo; (John 14:6).</p>
    <p class="pull" style="margin-top:30px">&ldquo;I have come so that they may have life and have it
    in abundance.&rdquo;</p>
    <p class="pull-attr" style="color:var(--gold-bright)">John 10:10, CSB</p>
    <p style="max-width:62ch">Abundant life. Not a bigger version of the life you already have &mdash;
    the life you were <em>made</em> for. God&rsquo;s plan for your life is not a secret you have to
    decode. It&rsquo;s a Person you get to follow.</p>
    <div class="btns" style="margin-top:38px">{btn('Next: Partner with him','partner.html')}
    {btn('Start at part one: Yada','yada.html','btn btn-ghost')}</div>
  </div>
</section>
{thread('know','The plan was never rules. The plan was always coming home.')}
'''
PAGES.append(page('gods-plan.html', 'God&rsquo;s Plan for Life | SOJO Church, Concord NC',
    'From the garden of Genesis to Psalm 1 to Jesus — God&rsquo;s plan to redeem humanity, '
    'the way of Jesus, and the abundant life you were made for.',
    plan_page, active='gods-plan.html'))

# ============================== KNOW: PARTNER ================================
partner_page = f'''
<section class="phero grain dark">
  <div class="phero-img">{eager('n-dan-teach','The SOJO family kneeling and praying over one another')}</div>
  <div class="wrap">
    <p class="crumb">Know &middot; Part Three</p>
    <h1 class="display"><span class="script">Your move:</span><br>Partner<br>with <span class="gold">him</span></h1>
    <p class="lede">Jesus never once asked anybody to admire him from a distance.
    His invitation was two words long: <strong>&ldquo;Follow me.&rdquo;</strong></p>
  </div>
</section>

<section class="sec">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">Apprenticeship</p>
      <h2 class="display display-sm">Following is<br>a trade you<br>learn</h2>
      <p class="lede">In Jesus&rsquo; world, a disciple wasn&rsquo;t a fan or a student taking notes.
      A disciple was an <strong>apprentice</strong>.</p>
      <p>An apprentice moves in with the work. You&rsquo;re with the master, you watch his hands,
      you copy his moves, and slowly &mdash; over years, not weekends &mdash; you start to do what he
      does. That&rsquo;s the actual shape of the Christian life: <strong>be with Jesus, become like
      Jesus, do what Jesus did.</strong></p>
      <p>That&rsquo;s also exactly what our whole mission means. <strong>Know</strong> him &mdash; the
      being-with. <strong>Grow</strong> in peace &mdash; the becoming-like. <strong>Go</strong> in purpose
      &mdash; the doing-what-he-did. Know, grow, go isn&rsquo;t a church slogan. It&rsquo;s apprenticeship
      to Jesus, in order.</p>
    </div>
    <div class="figure">
      {img('g2-table','A SOJO group sharing a meal around a table')}
      <p class="figcap">Learning the trade &middot; SOJO Church</p>
    </div>
  </div>
</section>

<section class="sec tint">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">Becoming a Christian</p>
      <h2 class="display display-sm">What actually<br>happens</h2>
      <p class="lede">Not a formula. Not a transaction. A covenant &mdash; and it starts with grace.</p>
      <p>You cannot earn this. &ldquo;For you are saved by grace through faith... it is God&rsquo;s
      gift &mdash; not from works&rdquo; (Ephesians 2:8&ndash;9). The rescue was accomplished by Jesus
      on the cross and out of the empty tomb. Your part is to receive it and reorient your
      whole life around it. The Bible uses two words for that:</p>
      <p><strong>Repent</strong> &mdash; which doesn&rsquo;t mean grovel; it means <em>turn around</em>.
      Change direction. Stop walking your way and start walking his. And <strong>believe</strong>
      &mdash; not &ldquo;agree the facts are true,&rdquo; but <em>trust him with your weight</em>, the way
      you trust a chair by sitting in it.</p>
      <p class="pull" style="margin-top:30px">&ldquo;If you confess with your mouth, &lsquo;Jesus is
      Lord,&rsquo; and believe in your heart that God raised him from the dead, you will be
      saved.&rdquo;</p>
      <p class="pull-attr">Romans 10:9, CSB</p>
    </div>
    <div class="figure">
      {img('n-couple-pray','A man praying during a service at SOJO Church')}
      <p class="figcap">The turn &middot; SOJO Church</p>
    </div>
  </div>
</section>

<section class="sec dark grain">
  <div class="wrap">
    <p class="eyebrow">Ready?</p>
    <div class="split split-6535" style="align-items:end">
      <h2 class="display display-sm">A prayer<br>to start</h2>
      <p class="lede">There&rsquo;s nothing magic about these exact words &mdash; God is listening to
      your heart, not grading your grammar. But if you&rsquo;re ready, pray something like this
      and mean it:</p>
    </div>
    <p class="pull" style="margin-top:34px;max-width:56ch">&ldquo;Jesus, I believe you are who you said
    you are. I&rsquo;ve been walking my own way, and I&rsquo;m turning around. Forgive me. I trust
    what you did on the cross for me. Be my Lord, be my teacher &mdash; I&rsquo;m yours. Teach me
    your way. Amen.&rdquo;</p>
    <p style="max-width:60ch;margin-top:26px">If you just prayed that &mdash; welcome home. Heaven is
    louder about this than you are (Luke 15:7). <strong>Don&rsquo;t keep it a secret.</strong> Text us
    right now so we can walk with you &mdash; the button below starts the message, you just add
    your name and hit send.</p>
    <div class="btns" style="margin-top:34px">
      {btn('I prayed this &mdash; text us','SMSJESUS')}
      {btn('I have questions','SMSQUESTION','btn btn-ghost')}
      {btn(f'Or call {PHONE_D}',PHONE_H,'btn btn-ghost')}
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="eyebrow">What happens after you text</p>
    <h2 class="display display-sm" style="margin-bottom:34px">We walk with you.<br>Here&rsquo;s the path.</h2>
    {rows([
      ("A real person texts you back", "Usually the same day. Not a robot pretending to be a pastor &mdash; a pastor. We&rsquo;ll celebrate with you and answer whatever&rsquo;s on your mind.", None),
      ("Discover More", "Our three-week class on the basics of following Jesus &mdash; doctrine and discipleship, no question off limits. It&rsquo;s the best next room to be in.", ("Ask about the next class",'SMSQUESTION',False)),
      ("Get baptized", "The public yes. Jesus was baptized, and he asks his apprentices to be. It&rsquo;s the next page of this story &mdash; literally.", ("Read about baptism","baptism.html",False)),
    ])}
  </div>
</section>
{thread('know','You don&rsquo;t clean up to come to him. You come to him, and he does the rest.')}
'''
partner_page = partner_page.replace('SMSJESUS', SMS_JESUS).replace('SMSQUESTION', SMS_QUESTION)
PAGES.append(page('partner.html', 'Partner with Him — Becoming a Follower of Jesus | SOJO Church',
    'What it means to become a Christian: apprenticeship to Jesus, grace, repentance, belief — and a prayer to start. We walk with you.',
    partner_page, active='partner.html'))

# ============================== KNOW: BAPTISM ================================
BAPTISM_FAQ = [
      ("Do I need to get my life together first?", "No. Baptism isn&rsquo;t a trophy for the finished &mdash; it&rsquo;s a starting line for the forgiven. Come as you are; that&rsquo;s the only way anyone has ever come."),
      ("I was baptized as a baby. Does that count?", "We&rsquo;re grateful for every family that honored God that way. But what we practice is believer&rsquo;s baptism &mdash; your own yes, made when it&rsquo;s yours to make. Many people baptized as infants choose to be baptized again as their own decision. We&rsquo;d love to talk it through with you."),
      ("Can my kids be baptized?", "If your child is asking about baptism, that&rsquo;s worth taking seriously. A pastor will sit down with you and them &mdash; no pressure either way &mdash; and help discern whether they&rsquo;re ready or whether we wait and keep watering."),
      ("What do I wear?", "Dark, comfortable clothes you don&rsquo;t mind soaking, and bring a full change. We provide the towel."),
      ("Will I have to speak in front of everyone?", "No speech required. We&rsquo;ll ask you one question &mdash; &ldquo;Is Jesus your Lord?&rdquo; &mdash; and you say yes. The water does the rest of the talking."),
      ("What if I&rsquo;m nervous?", "Everybody is. It lasts four seconds, and you will replay it for the rest of your life. Worth it."),
    ]

baptism_page = f'''
<section class="phero grain dark">
  <div class="phero-img">{eager('baptism','Pastors praying over someone at the SOJO baptism tank')}</div>
  <div class="wrap">
    <p class="crumb">Know &middot; Part Four</p>
    <h1 class="display"><span class="script">Buried and raised:</span><br><span class="gold">Baptism</span></h1>
    <p class="lede">Knowing him. His plan. Your yes. Baptism is where all three go public &mdash;
    the oldest announcement in the church, made with water.</p>
  </div>
</section>

<section class="sec">
  <div class="wrap split split-6535">
    <div>
      <p class="eyebrow">What it means</p>
      <h2 class="display display-sm">The public yes</h2>
      <p class="pull" style="margin-top:10px">&ldquo;We were buried with him by baptism into death, in
      order that... we too may walk in newness of life.&rdquo;</p>
      <p class="pull-attr">Romans 6:4, CSB</p>
      <p>Everything the last three pages said, baptism <em>says</em> &mdash; out loud, in front of
      your people. Going under the water: the old you, buried with Jesus. Coming up: the new
      you, raised with him. It&rsquo;s a funeral and a birth in about four seconds.</p>
      <p>Be clear on this: <strong>the water doesn&rsquo;t save you &mdash; grace does.</strong> Baptism is
      the wedding ring, not the marriage. But Jesus was baptized himself, and he told his
      followers to baptize every new apprentice (Matthew 28:19). If he&rsquo;s your Lord, it&rsquo;s
      not really a question of <em>whether</em>. Just <em>when</em>.</p>
    </div>
    <div class="figure">
      {img('pray','A baptism moment at the SOJO tank')}
      <p class="figcap">At the tank &middot; SOJO Church</p>
    </div>
  </div>
</section>

<section class="sec tint">
  <div class="wrap">
    <p class="eyebrow">The details</p>
    <h2 class="display display-sm" style="margin-bottom:34px">Who, what, why,<br>when, where, how</h2>
    {rows([
      ("Who", "Anyone who has decided to follow Jesus. That&rsquo;s the one requirement &mdash; not perfection, not a theology degree, not a waiting period. Kids who are asking about it: we&rsquo;d love to talk with you and your family first.", None),
      ("What", "Full immersion &mdash; all the way under, the way Jesus did it in the Jordan. It&rsquo;s a symbol you act out with your whole body: buried with him, raised with him.", None),
      ("Why", "Because Jesus asked (Matthew 28:19), because it declares in public what happened in private, and because you&rsquo;ll never forget it &mdash; and neither will the people watching.", None),
      ("When", "We baptize regularly at Sunday services, and September 6 at Gibson Mill opens a brand-new tank in a brand-new room. Tell us you&rsquo;re ready and we&rsquo;ll get you the very next date.", None),
      ("Where", "Sunday mornings at The Kettle Room at Gibson Mill — 325 McGill Ave NW, Suite 148, Concord. In front of your church family, which is the whole point.", ("Find the room","new-home.html",False)),
      ("How", "Text us with the button below. A pastor sits down with you for a short, easy conversation — your story, what baptism means, any questions. Then Sunday: bring dark clothes and a change; we bring the towel and the party.", None),
    ])}
  </div>
</section>

<section class="sec dark grain">
  <div class="wrap">
    <p class="eyebrow">Take the step</p>
    <div class="split split-6535" style="align-items:end">
      <h2 class="display display-sm">The water&rsquo;s<br>ready</h2>
      <p class="lede">One text starts it. The message is already written &mdash; add your name and
      hit send, and a pastor will reply, usually the same day.</p>
    </div>
    <div class="btns" style="margin-top:36px">
      {btn('I want to be baptized','SMSBAPTIZE')}
      {btn('I just prayed to follow Jesus','SMSJESUS','btn btn-ghost')}
      {btn(f'Or call {PHONE_D}',PHONE_H,'btn btn-ghost')}
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <p class="eyebrow">Honest questions</p>
    <h2 class="display display-sm" style="margin-bottom:30px">Asked all<br>the time</h2>
    {faq(BAPTISM_FAQ)}
    {faq_ld(BAPTISM_FAQ)}
  </div>
</section>
{thread('know','Four seconds of water. A whole life of new.')}
'''
baptism_page = baptism_page.replace('SMSBAPTIZE', SMS_BAPTIZE).replace('SMSJESUS', SMS_JESUS)
PAGES.append(page('baptism.html', 'Baptism | SOJO Church, Concord NC',
    'Who, what, why, when, where and how to be baptized at SOJO Church in Concord, NC — '
    'and one text that starts it.',
    baptism_page, active='baptism.html'))


# ============================== 404 ==========================================
notfound_body = f'''
<section class="sec dark grain" style="min-height:72vh;display:flex;align-items:center">
  <div class="wrap">
    <p class="eyebrow">Well, this is awkward</p>
    <h1 class="display"><span class="script">Lost?</span><br>This page<br>moved <span class="gold">on</span></h1>
    <p class="lede" style="max-width:52ch">The page you were looking for isn&rsquo;t here &mdash; maybe the
    link was old, maybe a typo. Either way, you&rsquo;re not lost: everything worth finding is one
    click away.</p>
    <div class="btns" style="margin-top:34px">
      {btn('Take me home','index.html')}
      {btn('Plan a visit','plan-a-visit.html','btn btn-ghost')}
      {btn('This week&rsquo;s message','watch.html','btn btn-ghost')}
    </div>
    <p style="margin-top:30px;max-width:52ch">Looking for something specific and can&rsquo;t find it?
    <a href="{SMS_HELLO}">Text us</a> &mdash; a human will point you the right way.</p>
  </div>
</section>
'''
NOTFOUND = page('404.html', 'Page Not Found | SOJO Church',
    'That page moved on — but SOJO Church is right here. Sundays 9 & 11am at Gibson Mill, Concord NC.',
    notfound_body, active='index.html')

# ---------------------------------------------------------------- emit

def _verify(pages):
    import glob as _g
    have = set()
    for f in _g.glob(os.path.join(OUT, 'assets/img/**/*.webp'), recursive=True):
        have.add(os.path.relpath(f, os.path.join(OUT, 'assets/img'))[:-5].replace(os.sep, '/'))
    bad = []
    for slug, html in pages:
        for m in re.findall(r'src="assets/img/([^"]+)\.webp"', html):
            if m not in have: bad.append((slug, m))
    if bad:
        raise SystemExit('MISSING IMAGES: ' + repr(sorted(set(bad))))
    print('image refs: all resolve')

def build_dist():
    if os.path.exists(DIST): shutil.rmtree(DIST)
    shutil.copytree(OUT, DIST)
    ico = os.path.join(DIST, 'assets/icons/favicon.ico')
    if os.path.exists(ico): shutil.copy(ico, os.path.join(DIST, 'favicon.ico'))
    for slug, html in PAGES + [NOTFOUND]:
        with open(os.path.join(DIST, slug), 'w', encoding='utf-8') as f:
            f.write(html)
    used = set()
    for _, html in PAGES:
        used.update(re.findall(r'assets/img/([^"]+\.webp)', html))
    pruned = 0
    for root, _, files in os.walk(os.path.join(DIST, 'assets/img')):
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), os.path.join(DIST, 'assets/img')).replace(os.sep, '/')
            if f.endswith('.webp') and rel not in used and not rel.startswith('brand/'):
                os.remove(os.path.join(root, f)); pruned += 1
    urls = ''.join(
        f'<url><loc>{BASE_URL if slug=="index.html" else BASE_URL+slug}</loc>'
        f'<changefreq>weekly</changefreq>'
        f'<priority>{"1.0" if slug=="index.html" else "0.8"}</priority></url>'
        for slug, _ in PAGES)
    with open(os.path.join(DIST, 'sitemap.xml'), 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                + urls + '</urlset>')
    with open(os.path.join(DIST, 'robots.txt'), 'w') as f:
        ai_bots = ['GPTBot','OAI-SearchBot','ChatGPT-User','ClaudeBot','Claude-Web',
                   'anthropic-ai','Google-Extended','Gemini-Deep-Research','PerplexityBot',
                   'Perplexity-User','Applebot-Extended','meta-externalagent','CCBot',
                   'Bytespider','Amazonbot','DuckAssistBot','cohere-ai','YouBot']
        blocks = ''.join(f'User-agent: {b}\nAllow: /\n\n' for b in ai_bots)
        f.write('# SOJO Church — everyone welcome, crawlers included.\n'
                'User-agent: *\nAllow: /\n\n' + blocks +
                'Sitemap: ' + BASE_URL + 'sitemap.xml\n')
    # llms.txt — a plain-language site guide for AI assistants (llmstxt.org convention)
    llms = f"""# SOJO Church

> SOJO Church is a non-denominational Christian church in Concord, North Carolina.
> Sundays at 9:00am & 11:00am in The Kettle Room at Gibson Mill, 325 McGill Ave NW,
> Suite 148, Concord, NC 28027. Vision: "A community with a cause." Mission: helping
> people know life, grow in peace, and go in purpose. Lead Pastor: Corey Alley ("PC").
> Founded 2017. Call or text: 980-680-0958.

Key facts
- Service times: Sundays 9:00am and 11:00am
- Location: The Kettle Room at Gibson Mill, 325 McGill Ave NW, Suite 148, Concord, NC 28027 (moved September 6, 2026)
- Style: come as you are; casual dress; about 75 minutes; kids ministry at both services
- Kids: SOJO Kids (birth-5th grade, Sundays) · Youth: SOJO YTH (6th-12th, Wednesdays 6-8pm) · Young adults: SOJO YA (18-30, Fridays 6-8pm)
- Beliefs: historic Christian faith, non-denominational; firm on essentials, open-handed dialogue on secondary matters

Pages
- [Home]({BASE_URL}): service times, location, what to expect
- [Plan a Visit]({BASE_URL}plan-a-visit.html): first-visit guide, parking, kids check-in
- [Our New Home]({BASE_URL}new-home.html): Gibson Mill move, directions
- [Our Mission]({BASE_URL}mission.html): know life, grow in peace, go in purpose
- [Our Story]({BASE_URL}our-story.html): 2017 living room to Gibson Mill
- [Our Beliefs]({BASE_URL}beliefs.html): doctrinal positions
- [Our Team]({BASE_URL}about.html): staff and leadership
- [Yada - Knowing God]({BASE_URL}yada.html): knowing God experientially
- [God's Plan for Life]({BASE_URL}gods-plan.html): the Bible's story, abundant life
- [Partner with Him]({BASE_URL}partner.html): becoming a follower of Jesus
- [Baptism]({BASE_URL}baptism.html): who, what, why, when, where, how
- [Next Steps]({BASE_URL}next-steps.html): Discover SOJO, Discover More
- [Groups]({BASE_URL}groups.html): connect, community, care groups and classes
- [Next Gen]({BASE_URL}next-gen.html): kids, youth, young adults
- [Serve]({BASE_URL}serve.html): volunteer teams
- [Outreach & Missions]({BASE_URL}missions.html): here, near, far
- [Give]({BASE_URL}give.html): giving and the 90-day generosity challenge
- [Watch]({BASE_URL}watch.html): messages online
- [SOJO Kids]({BASE_URL}kids.html): birth-5th grade, Sundays
- [SOJO YTH]({BASE_URL}youth.html): 6th-12th grade, Wednesdays 6-8pm
- [SOJO YA]({BASE_URL}young-adults.html): ages 18-30, Fridays 6-8pm
- [SOJO Swag]({BASE_URL}swag.html): church merch
"""
    with open(os.path.join(DIST, 'llms.txt'), 'w') as f:
        f.write(llms)
    print(f'dist/ → {len(PAGES)} pages ({pruned} unused photos pruned) + sitemap + robots')

def datauri(path):
    mt = mimetypes.guess_type(path)[0] or 'application/octet-stream'
    with open(path, 'rb') as f:
        return f'data:{mt};base64,' + base64.b64encode(f.read()).decode()

def build_preview():
    """Single-file clickable prototype: all pages inlined, hash routed, images as data URIs."""
    css = open(os.path.join(OUT, 'assets/css/site.css'), encoding='utf-8').read()
    uris = {}
    d = os.path.join(OUT, 'assets/img')
    for root, _, files in os.walk(d):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, os.path.join(OUT, 'assets')).replace(os.sep, '/')
            uris['assets/' + rel] = datauri(full)

    def inline(html):
        # the welcome film is too large to base64 into a single page; the preview
        # shows its poster frame in the real layout instead.
        html = re.sub(
            r'<iframe[^>]*youtube-nocookie[^>]*>\s*</iframe>',
            ('<div class="ytph"><span class="vplay"></span>'
             '<span class="ytph-t">This week\u2019s message</span>'
             '<span class="ytph-s">The live YouTube player sits here. This preview blocks '
             'third-party embeds, so it cannot render inside this page \u2014 open watch.html '
             'from the downloaded site in any browser and it plays. It is wired to SOJO\u2019s '
             'uploads playlist, so it always shows your newest video with no weekly updating.'
             '</span></div>'),
            html, flags=re.S)
        html = re.sub(
            r'<video[^>]*poster="([^"]+)"[^>]*>.*?</video>',
            lambda m: ('<img src="' + m.group(1) + '" alt="Welcome to SOJO Church">'
                       '<div class="vshade"></div><div class="vplay"></div>'
                       '<div class="vnote">Welcome film &middot; plays on the live site</div>'),
            html, flags=re.S)
        for k, v in uris.items():
            html = html.replace('src="' + k + '"', 'src="' + v + '"')
        return html

    views = []
    for slug, html in PAGES:
        m = re.search(r'<main id="main">(.*?)</main>', html, re.S)
        body = inline(m.group(1))
        # internal links → hash routes
        body = re.sub(r'href="([a-z0-9\-]+\.html)(#[a-z0-9\-]+)?"', r'href="#\1"', body)
        views.append(f'<div class="view" data-view="{slug}" hidden>{body}</div>')

    hdr = inline(header('index.html'))
    ftr = inline(footer())
    hdr = re.sub(r'href="([a-z0-9\-]+\.html)(#[a-z0-9\-]+)?"', r'href="#\1"', hdr)
    ftr = re.sub(r'href="([a-z0-9\-]+\.html)(#[a-z0-9\-]+)?"', r'href="#\1"', ftr)

    return f'''<title>SOJO Church Redesign</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<style>{css}
.view[hidden]{{display:none}}
</style>
<a class="skip" href="#main">Skip to content</a>
<div id="chrome-top">{hdr}</div>
<main id="main">{''.join(views)}</main>
{ftr}
<script>
(function(){{
  var views=[].slice.call(document.querySelectorAll('.view'));
  function show(slug){{
    var found=false;
    views.forEach(function(v){{
      var on=v.dataset.view===slug; v.hidden=!on; if(on) found=true;
    }});
    if(!found) views[0].hidden=false;
    document.querySelectorAll('nav.main a').forEach(function(a){{
      var h=a.getAttribute('href')||'';
      if(h.slice(1)===slug) a.setAttribute('aria-current','page'); else a.removeAttribute('aria-current');
    }});
    var m=document.getElementById('mnav'); if(m) m.classList.remove('open');
    window.scrollTo(0,0);
  }}
  function route(){{ show((location.hash||'#index.html').slice(1)); }}
  window.addEventListener('hashchange',route); route();
}})();
</script>'''

if __name__ == '__main__':
    _verify(PAGES)
    build_dist()
    prev = build_preview()
    with open(os.path.join(SRC, 'preview.html'), 'w', encoding='utf-8') as f:
        f.write(prev)
    print('preview.html', round(len(prev.encode())/1024/1024, 2), 'MB')
