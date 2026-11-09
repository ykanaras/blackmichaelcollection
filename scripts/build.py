#!/usr/bin/env python3
"""Dependency-free static site builder. Edit content/*.json, then run this file."""
import json, shutil, re, html
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, quote
R=Path(__file__).resolve().parents[1]; D=R/'dist'
load=lambda name: json.loads((R/'content'/f'{name}.json').read_text())
S=load('site'); PRODUCTS=load('products'); EVENTS=load('events'); POSTS=load('posts')
E=lambda s: html.escape(str(s),quote=True)
PREVIEW=S.get('preview',True); BASE=S.get('siteUrl','').rstrip('/')
CATS={'minerals':'Mineral specimens','gemstones':'Loose gemstones','jewelry':'Fine jewelry'}
PHOTOS={'blue','purple','pale','green','long','pendant'}
def url_ok(u): return bool(u and urlparse(u).scheme=='https' and urlparse(u).netloc)
def slug_ok(v): return bool(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',v))
def validate():
 if not PREVIEW and not url_ok(BASE): raise ValueError('Set siteUrl to your public HTTPS domain before disabling preview.')
 for group in [PRODUCTS,POSTS,EVENTS]:
  seen=set()
  for item in group:
   if not slug_ok(item['slug']) or item['slug'] in seen: raise ValueError('Every entry needs a unique lowercase slug with hyphens.')
   seen.add(item['slug'])
 for image in S.get('editorialImages',{}).values():
  path=Path(image)
  if path.is_absolute() or '..' in path.parts or not str(path).startswith('assets/') or not (R/path).is_file(): raise ValueError('Editorial image must be a real relative file inside assets/')
 for p in PRODUCTS:
  if p['category'] not in CATS or p['status'] not in ['preview','available','sold']: raise ValueError('Invalid product category or status')
  if p.get('checkoutUrl') and not url_ok(p['checkoutUrl']): raise ValueError('Checkout URLs must use HTTPS')
  if p.get('price') is not None and (isinstance(p['price'],bool) or not isinstance(p['price'],(int,float)) or p['price']<=0): raise ValueError('Prices must be positive numbers or null')
  if p.get('checkoutUrl') and p.get('price') is None: raise ValueError('Add a price before adding checkout')
  if p.get('image'):
   path=Path(p['image'])
   if path.is_absolute() or '..' in path.parts or not (R/path).is_file(): raise ValueError('Product image must be a real relative file in assets/')
   if not str(path).startswith('assets/'): raise ValueError('Keep images in assets/')
  elif p.get('photo') not in PHOTOS: raise ValueError('Unknown preview photo')
  if not PREVIEW and p['status']!='preview':
   if not p.get('image'): raise ValueError('Live products need original product photos; replace screenshot previews.')
   if any('to be' in str(v).lower() for v in p.get('details',{}).values()): raise ValueError('Confirm product details before launch')
 for post in POSTS:
  datetime.strptime(post['date'],'%Y-%m-%d')
  for source in post.get('sources',[]):
   if not url_ok(source['url']): raise ValueError('Article sources must use HTTPS')
 for event in EVENTS:
  start=datetime.fromisoformat(event['start']); end=datetime.fromisoformat(event['end'])
  if not start.tzinfo or not end.tzinfo or end<=start: raise ValueError('Event times need UTC offsets and an end after the start')
  if event.get('url') and not url_ok(event['url']): raise ValueError('Event links must use HTTPS')
validate()
if D.exists(): shutil.rmtree(D)
D.mkdir();shutil.copytree(R/'assets',D/'assets');shutil.copytree(R/'content',D/'content')
PRODUCTS=[p for p in PRODUCTS if PREVIEW or p['status']!='preview']
PAGES=[]
MARK='<svg viewBox="0 0 48 64" fill="none" aria-hidden="true"><path d="M14 3h20l11 15v28L34 61H14L3 46V18Z M14 3l5 15h10l5-15M3 18h42M3 46h42M14 61l5-15h10l5 15M19 18v28M29 18v28M3 18l16 28M45 18 29 46M3 46l16-28M45 46 29 18" stroke="currentColor" stroke-width="1.2"/></svg>'
def brand(): return f'<a class="brand" href="index.html" aria-label="Black Michael Collection home">{MARK}<span class="brand-text">BLACK MICHAEL<small>COLLECTION</small></span></a>'
def photo(p,cls=''):
 if not p.get('image') and S.get('editorialImages',{}).get(p.get('photo')): p={**p,'image':S['editorialImages'][p['photo']]}
 if p.get('image'): return f'<img class="photo real {cls}" src="{E(p["image"])}" alt="{E(p.get("alt",p["name"]))}" loading="lazy" width="600" height="800">'
 return f'<div class="photo {E(p.get("photo","blue"))} {cls}" role="img" aria-label="{E(p.get("alt","Collection reference photograph"))}"></div>'
def pic(which):return photo({'photo':which})
def link(href,label,style='button'):return f'<a class="{style}" href="{E(href)}">{label} <span aria-hidden="true">↗</span></a>'
def intro(kicker,title,desc):return f'<div class="intro"><p class="eyebrow">{kicker}</p><h1>{title}</h1><p>{desc}</p></div>'
def note():return '<p class="note">Collection preview · Images are drawn from our supplied Instagram reference. These are examples of the collection, not confirmed live listings. Ask us about current availability.</p>' if PREVIEW else ''
def card(p,i=0):
 amount=f'${p["price"]:,.2f} USD' if p.get('price') else 'Details on request'
 status={'preview':'Collection preview','sold':'Sold','available':'Available'}[p['status']]
 return f'<article class="card" data-product data-name="{E(p["name"].lower())}" data-category="{p["category"]}" data-price="{p.get("price") or 1e15}" data-order="{i}"><a class="image-link" href="product-{p["slug"]}.html">{photo(p)}<span class="arrow" aria-hidden="true">↗</span></a><div class="meta"><span>{CATS[p["category"]]}</span><span>{status}</span></div><h3><a href="product-{p["slug"]}.html">{E(p["name"])}</a></h3><p class="price">{amount if p["status"]!="preview" else "Explore the piece"}</p></article>'
def jcard(p):return f'<article class="journal-card"><p class="eyebrow">{E(p["category"])}</p><h3><a href="journal-{p["slug"]}.html">{E(p["title"])}</a></h3><p>{E(p["description"])}</p>{link("journal-"+p["slug"]+".html","Read the story","textlink")}</article>'
def page(file,title,description,body,active='',schema=None,noindex=False):
 nav=''.join(f'<a href="{p}.html"'+(' aria-current="page"' if active==p else '')+f'>{label}</a>' for p,label in [('shop','Shop'),('about','Our story'),('events','Events'),('journal','Journal')])
 canonical=f'<link rel="canonical" href="{E(BASE+"/"+file)}"><meta property="og:url" content="{E(BASE+"/"+file)}">' if BASE else ''
 robots='noindex, nofollow' if PREVIEW or noindex else 'index, follow'
 schema=schema or {'@type':'WebPage','name':title,'description':description}
 schema={'@context':'https://schema.org',**schema}
 structured=json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')
 out=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{E(title)} | Black Michael Collection</title><meta name="description" content="{E(description)}"><meta name="robots" content="{robots}">{canonical}<meta property="og:title" content="{E(title)} | Black Michael Collection"><meta property="og:description" content="{E(description)}"><meta property="og:type" content="{'article' if schema.get('@type')=='BlogPosting' else 'website'}"><meta name="theme-color" content="#18231e"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/site.css"><script src="assets/site.js" defer></script><script type="application/ld+json">{structured}</script></head><body><a class="skip" href="#main">Skip to content</a><div class="topline">Gems · Mineral specimens · Fine jewelry</div><header class="header"><div class="wrap navwrap">{brand()}<button class="menu-toggle" aria-controls="mainnav" aria-expanded="false">Menu</button><nav id="mainnav" class="mainnav" aria-label="Main navigation">{nav}</nav><a class="nav-contact" href="contact.html">Inquire about a piece ↗</a></div></header><main id="main">{body}</main><footer class="footer"><div class="wrap"><div class="footer-grid"><div>{brand()}<p>Natural character. Considered selection.<br>Raw gems, mineral specimens and finished jewelry.</p><p>{E(S['location'])}</p></div><div><h3>Explore</h3><a href="minerals.html">Mineral specimens</a><a href="gemstones.html">Loose gemstones</a><a href="jewelry.html">Fine jewelry</a><a href="events.html">Upcoming events</a><a href="journal.html">The journal</a></div><div><h3>Connect</h3><a href="contact.html">Contact us</a><a href="{E(S['instagram'])}" target="_blank" rel="noopener">Instagram ↗</a><a href="faq.html">Questions & answers</a><a href="policies.html">Shipping & policies</a></div></div><div class="footer-bottom"><span>© {datetime.now().year} Black Michael Collection</span><span>{'Design preview · Product availability and terms to be confirmed' if PREVIEW else 'Selected for their individual character.'}</span></div></div></footer></body></html>'''
 (D/file).write_text(out);PAGES.append((file,noindex))
# Home
categories=''.join(f'<article class="category-card"><a href="{cat}.html">{pic(img)}<h3>{label}<span aria-hidden="true">↗</span></h3></a><p>{copy}</p></article>' for cat,label,img,copy in [('minerals','Mineral specimens','purple','Natural forms. Distinctive character. Pieces to collect.'),('gemstones','Loose gemstones','green','A world of color, waiting to be discovered.'),('jewelry','Fine jewelry','pendant','The beauty of a stone, made wearable.')])
body=f'''<section class="hero"><div class="wrap hero-grid"><div class="hero-copy"><p class="eyebrow">Black Michael Collection</p><h1>Earth’s artistry.<br><em>Exceptionally<br>collected.</em></h1><p class="lede">From remarkable mineral specimens to finished jewelry. Discover pieces with a character all their own.</p><div class="actions">{link('shop.html','Explore the collection','button light')}{link('about.html','Our approach','textlink')}</div></div><div class="hero-art">{pic('blue')}<span class="caption">A closer look / From the collection</span><span class="vertical">The beauty is in the details</span></div></div></section><div class="wrap"><div class="value-strip"><span>Direct & reputable sourcing</span><span>Raw beauty to finished jewelry</span><span>Based in Salt Lake City, Utah</span></div><section class="section"><div class="section-head"><div><p class="eyebrow">Find your fascination</p><h2>Three ways to collect.</h2></div>{link('shop.html','View all pieces','textlink')}</div><div class="grid">{categories}</div></section></div><section class="tinted section"><div class="wrap split"><div>{pic('pale')}</div><div class="copy"><p class="eyebrow">The Black Michael approach</p><h2>It begins with<br>the stone.</h2><p>Some pieces belong in a collection. Others become something you wear. Our interest begins with the individual character of each gem and mineral.</p><p>We source directly and through reputable sources, bringing together raw specimens, loose gems and finished luxury jewelry.</p><div class="principle"><span class="number">01</span> A considered selection</div><div class="principle"><span class="number">02</span> A conversation about the details</div><div class="principle"><span class="number">03</span> A piece that speaks to you</div><div class="actions">{link('about.html','Meet the collection','textlink')}</div></div></div></section><section class="wrap section"><div class="section-head"><div><p class="eyebrow">From the collection</p><h2>Worth a closer look.</h2></div>{link('shop.html','Explore all','textlink')}</div>{note()}<div class="grid four">{''.join(card(p,i) for i,p in enumerate(PRODUCTS) if p.get('featured'))}</div></section><section class="band"><div class="wrap"><div><p class="eyebrow" style="color:#bdb294">Beyond the screen</p><h2>Meet us in person.</h2><p>Explore the collection and talk stones at our next vendor event.</p></div>{link('events.html','Find upcoming events','button light')}</div></section><section class="wrap section"><div class="section-head"><div><p class="eyebrow">The journal</p><h2>For the curious collector.</h2></div>{link('journal.html','All stories','textlink')}</div><div class="grid">{''.join(jcard(p) for p in POSTS[:3])}</div></section>'''
page('index.html','Gems, Mineral Specimens & Fine Jewelry',S['description'],body,schema={'@type':'Organization','name':S['name'],'description':S['description'],'sameAs':[S['instagram']],**({'url':BASE} if BASE else {})})
# Collection landing pages, all with pre-rendered cards
for category in ['',*CATS]:
 title=CATS.get(category,'The collection')
 desc={'minerals':'Color, crystal form and natural character. Explore the mineral side of Black Michael Collection.','gemstones':'Explore loose gemstones and get to know the details behind each piece.','jewelry':'Distinctive stones, finished as jewelry. Discover the wearable side of the collection.'}.get(category,'Mineral specimens, loose gemstones and finished jewelry. Find the piece that speaks to you.')
 selected=[p for p in PRODUCTS if not category or p['category']==category]
 tabs=''.join(f'<a href="{c or "shop"}.html"'+(' aria-current="page"' if c==category else '')+f'>{l}</a>' for c,l in [('', 'All pieces'),*CATS.items()])
 options=''.join(f'<option value="{k}">{v}</option>' for k,v in CATS.items() if not category or k==category)
 body=f'<div class="wrap">{intro("Explore",title,desc)}<nav class="filter-tabs" aria-label="Collections">{tabs}</nav>{note()}<div class="tools"><div class="field"><label for="search">Search the collection</label><input type="search" id="search" placeholder="Search by name…"></div><div class="field"><label for="category">Category</label><select id="category"><option value="">All in this collection</option>{options}</select></div><div class="field"><label for="sort">Sort by</label><select id="sort"><option value="featured">Collection order</option><option value="name">Name A–Z</option><option value="price">Price: low to high</option></select></div></div><p id="result-count" class="results" aria-live="polite">{len(selected)} pieces</p><div class="grid" style="padding-bottom:65px">{"".join(card(p,i) for i,p in enumerate(selected))}</div><div id="no-results" class="empty" hidden><h2>No pieces found.</h2><p>Try another name or category.</p><button id="reset-search" class="button">Clear filters</button></div><noscript><p>All pieces are listed above. Search and sorting require JavaScript.</p></noscript></div>'
 page((category or 'shop')+'.html',title,desc,body,'shop')
for p in PRODUCTS:
 ispreview=p['status']=='preview'; inquiry='contact.html?piece='+quote(p['name'])
 cta=link(inquiry,'Ask about this piece')
 if p['status']=='available' and p.get('checkoutUrl'):
  cta=link(p['checkoutUrl'],'Buy securely')+f'<p class="status">Checkout is handled by our payment provider. Confirm delivery and purchase terms before paying.</p>'
 if p['status']=='sold': cta='<p class="note">This piece has sold.</p>'+link('contact.html','Ask about similar pieces')
 table=''.join(f'<tr><th scope="row">{E(k)}</th><td>{E(v)}</td></tr>' for k,v in p.get('details',{}).items())
 body=f'<div class="wrap"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="shop.html">Collection</a> / <a href="{p["category"]}.html">{CATS[p["category"]]}</a> / {E(p["name"])}</nav><div class="detail"><div>{photo(p)}<p class="status">{"Reference image from the supplied Instagram screenshot. Original photography will replace this preview." if ispreview else "Contact us for additional views or details."}</p></div><div><p class="eyebrow">{CATS[p["category"]]}</p><h1>{E(p["name"])}</h1><p class="description">{E(p["description"])}</p><p>{"Collection preview" if ispreview else (f"${p["price"]:,.2f} USD" if p.get("price") else "Price on request")}</p>{note() if ispreview else ""}<table class="details"><caption class="eyebrow" style="text-align:left">Piece details</caption>{table}</table>{cta}<p class="status"><a href="policies.html">Shipping & purchase information</a></p></div></div></div>'
 schema={'@type':'WebPage','name':p['name']}
 if not ispreview:
  schema={'@type':'Product','name':p['name'],'description':p['description'],'sku':p['slug'],'brand':{'@type':'Brand','name':S['name']},'image':BASE+'/'+p['image'] if BASE and p.get('image') else p.get('image','')}
  if p.get('price') and BASE: schema['offers']={'@type':'Offer','price':p['price'],'priceCurrency':'USD','url':BASE+'/product-'+p['slug']+'.html','availability':'https://schema.org/'+('OutOfStock' if p['status']=='sold' else 'InStock')}
 page('product-'+p['slug']+'.html',p['name'],p['description'],body,'shop',schema,ispreview)
# About
body=f'<div class="wrap">{intro("Our story","Drawn to the extraordinary.","A collection built around the beauty and individual character of gems and minerals.")}<section class="split section" style="padding-top:20px"><div>{pic("purple")}</div><div class="copy"><p class="eyebrow">Black Michael Collection</p><h2>From natural form<br>to a finished piece.</h2><p>Black Michael Collection brings together raw gems and mineral specimens alongside finished luxury jewelry. Based in Salt Lake City, Utah, we source gems directly and through reputable sources.</p><p>We see collecting and wearing as two ways of appreciating the same thing: a stone with character. Some pieces are compelling in their natural form. Others reveal a different presence when cut or set.</p><p>Whether you are exploring your first piece or looking for something specific, start a conversation with us about the collection.</p>{link("contact.html","Let’s talk stones","textlink")}</div></section><section class="section" style="padding-top:0"><div class="section-head"><h2>A closer conversation.</h2></div><div class="grid"><div><p class="eyebrow">01 / Selection</p><h3>What catches the eye.</h3><p>Explore the forms, colors and finished pieces that make up the collection.</p></div><div><p class="eyebrow">02 / Details</p><h3>What you want to know.</h3><p>Ask about a piece’s identity, dimensions, condition, sourcing information and documentation.</p></div><div><p class="eyebrow">03 / Connection</p><h3>Where we meet.</h3><p>Find us on Instagram or meet us at an upcoming vendor event.</p></div></div></section></div>'
page('about.html','Our Story',S['description'],body,'about')
# Events + individual pages, schema only for real supplied entries
now=datetime.now().astimezone(); upcoming=sorted([v for v in EVENTS if datetime.fromisoformat(v['end'])>=now],key=lambda v:v['start']);past=sorted([v for v in EVENTS if datetime.fromisoformat(v['end'])<now],key=lambda v:v['start'],reverse=True)
def event_card(v):
 dt=datetime.fromisoformat(v['start']);return f'<article class="event"><div class="event-date">{dt.strftime("%b")}<br>{dt.day}</div><div><p class="eyebrow">{E(v["city"])}</p><h3><a href="event-{v["slug"]}.html">{E(v["name"])}</a></h3><p>{E(v["venue"])} · {E(v.get("booth","Booth details to follow"))}</p><p>{dt.strftime("%B %d, %Y · %I:%M %p")} {E(v["timezoneLabel"])}</p></div>{link("event-"+v["slug"]+".html","Event details","button outline")}</article>'
empty=f'<div class="empty"><p class="eyebrow">Next appearance</p><h2>The next stop is<br>still to come.</h2><p>No upcoming appearances are posted yet. Follow us on Instagram for collection updates, or get in touch about where to see us next.</p>{link(S["instagram"],"Follow on Instagram","button outline")}</div>'
body=f'<div class="wrap">{intro("Meet us in person","The collection, out in the world.","Upcoming vendor events and opportunities to see the pieces up close.")}{"".join(event_card(v) for v in upcoming) or empty}{("<section class=section><h2>Past appearances</h2>"+"".join(event_card(v) for v in past)+"</section>") if past else ""}</div>'
page('events.html','Upcoming Gem & Mineral Events','Find upcoming Black Michael Collection vendor events and opportunities to explore gems, mineral specimens and jewelry in person.',body,'events')
for v in EVENTS:
 dt=datetime.fromisoformat(v['start']);end=datetime.fromisoformat(v['end'])
 body=f'<div class="wrap"><article class="article"><p class="eyebrow">Vendor event</p><h1>{E(v["name"])}</h1><p class="lead">{E(v["description"])}</p><h2>Visit us</h2><p>{E(v["venue"])}<br>{E(v["address"])}<br>{E(v["city"])}</p><p>{dt.strftime("%B %d, %Y %I:%M %p")} – {end.strftime("%B %d, %Y %I:%M %p")} {E(v["timezoneLabel"])}</p><p>{E(v.get("booth",""))}</p><p>{E(v.get("admission","Check the organizer’s information for admission details."))}</p>{link(v["url"],"Organizer information") if v.get("url") else ""}<p><a href="events.html">← All events</a></p></article></div>'
 schema={'@type':'Event','name':v['name'],'description':v['description'],'startDate':v['start'],'endDate':v['end'],'eventAttendanceMode':'https://schema.org/OfflineEventAttendanceMode','location':{'@type':'Place','name':v['venue'],'address':v['address']+', '+v['city']}}
 page('event-'+v['slug']+'.html',v['name'],v['description'],body,'events',schema)
# Journal
page('journal.html','The Journal — Gem & Mineral Collecting','Practical notes on choosing gemstones, building a mineral collection and visiting gem shows.',f'<div class="wrap">{intro("The journal","A little closer.<br>A little more curious.","Notes on gems, collecting and the stories we discover along the way.")}<div class="grid section" style="padding-top:20px">{"".join(jcard(p) for p in POSTS)}</div></div>','journal')
for p in POSTS:
 sections=''.join(f'<section><h2>{E(s["heading"])}</h2><p>{E(s["text"])}</p></section>' for s in p['sections'])
 sources='<div class="sources"><p>Further reading</p>'+''.join(f'<a href="{E(s["url"])}" rel="noopener" target="_blank">{E(s["label"])} ↗</a>' for s in p.get('sources',[]))+'</div>' if p.get('sources') else ''
 body=f'<div class="wrap"><article class="article"><p class="eyebrow">{E(p["category"])}</p><h1>{E(p["title"])}</h1><p class="status">Black Michael Collection · <time datetime="{p["date"]}">{datetime.strptime(p["date"],"%Y-%m-%d").strftime("%B %d, %Y")}</time></p><p class="lead">{E(p["description"])}</p>{sections}{sources}<div class="note">Have a question about a piece in the collection? <a href="contact.html">Get in touch.</a></div>{link("journal.html","Back to the journal","textlink")}</article></div>'
 page('journal-'+p['slug']+'.html',p['title'],p['description'],body,'journal',{'@type':'BlogPosting','headline':p['title'],'description':p['description'],'datePublished':p['date'],'author':{'@type':'Organization','name':S['name']},'publisher':{'@type':'Organization','name':S['name']}})
# Contact
email=S.get('email','')
body=f'<div class="wrap">{intro("Get in touch","Let’s talk stones.","Looking for a particular piece? Want another view or more details? Start a conversation.")}<div class="contact-grid"><form id="inquiry" data-email="{E(email)}"><div class="field"><label for="name">Your name</label><input id="name" name="name" autocomplete="name" required maxlength="100"></div><div class="field"><label for="email">Email address</label><input id="email" name="email" type="email" autocomplete="email" required maxlength="200"></div><div class="field"><label for="message">What caught your eye?</label><textarea id="message" name="message" required maxlength="4000" placeholder="Tell us about the piece or what you are looking for…"></textarea></div><p class="status">{"This opens a draft in your email app. Review and send it there." if email else "Prepare a message to paste into an Instagram DM. This form does not send or store your details."}</p><button class="button" type="submit">{"Prepare email" if email else "Copy inquiry message"} ↗</button><div id="form-status" class="form-status" role="status" aria-live="polite"></div><noscript><p>Please contact us directly on Instagram; the message composer needs JavaScript.</p></noscript></form><aside class="contact-aside"><p class="eyebrow">A direct conversation</p><h2>Find us on Instagram.</h2><p>See collection updates and send a direct message to @blackmichael_collection.</p>{link(S["instagram"],"Open Instagram","button outline")}<hr style="border:0;border-top:1px solid #cbd0c3;margin:30px 0"><p>{E(S["location"])}</p><p>Prefer to meet in person?</p>{link("events.html","View upcoming events","textlink")}</aside></div></div>'
page('contact.html','Contact Black Michael Collection','Ask about gems, mineral specimens, jewelry or upcoming events.',body)
faqs=[('What do you offer?','Raw gems and mineral specimens, loose gemstones and finished luxury jewelry.'),('Where are you based?',S['location']+'. You can also find upcoming vendor appearances on our Events page.'),('How do you source pieces?','We source directly and through reputable sources. Ask us what sourcing information is available for the specific piece you are considering.'),('Are the pictured pieces available?','Availability is specific to each piece. Collection previews are examples, not confirmed live inventory. Contact us to confirm a piece’s current status.'),('Can I request more photographs or documentation?','Yes. Contact us with the name of the piece and tell us which views or information would help you decide.'),('Can I buy online?','Where an item has a Buy securely link, it takes you to our payment provider. Otherwise, contact us to confirm availability, price and purchase arrangements.'),('What should I confirm before buying?','Confirm the description, dimensions, known treatments, condition, documentation, total price, delivery arrangements and return terms for your specific purchase.')]
page('faq.html','Frequently Asked Questions','Answers about Black Michael Collection, product inquiries, sourcing and purchasing.',f'<div class="wrap">{intro("Good to know","A few helpful answers.","Have a more specific question? We are happy to talk about an individual piece.")}<div class="faq section" style="padding-top:0">'+''.join(f'<details><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q,a in faqs)+'</div></div>')
policies=S.get('policies',{})
body='<div class="wrap"><article class="article"><p class="eyebrow">Purchase information</p><h1>Shipping & policies.</h1>'
for key,title,default in [('shipping','Shipping','Contact us before purchasing to confirm shipping availability, delivery timing, cost and any insurance or signature arrangements for your destination.'),('returns','Returns & purchase terms','Return, cancellation and refund terms have not yet been published here. Request the applicable written terms for your piece before paying.'),('privacy','Privacy','This static website does not use analytics, advertising trackers or customer accounts by default. The inquiry composer does not submit or store your information on this website. Copying a message uses your device clipboard. If you send it through Instagram or your email app, that service processes it under its own terms. Hosting providers may process technical request logs. External payment providers process checkout information on their own sites.')]:
 body+=f'<h2>{title}</h2><p>{E(policies.get(key) or default)}</p>'
body+='<p><a href="contact.html">Contact us with a question →</a></p></article></div>'
page('policies.html','Shipping, Returns & Privacy','Purchase and privacy information for Black Michael Collection.',body)
page('404.html','Page Not Found','This page could not be found.',f'<div class="wrap section"><p class="eyebrow">404</p><h1>A different kind<br>of hidden gem.</h1><p>We couldn’t find that page. Let’s get you back to the collection.</p>{link("shop.html","Explore the collection")}</div>',noindex=True)
# Logo concepts
body='<div class="wrap">'+intro('Brand directions','Two ways to make your mark.','Editable vector logo concepts are included in the source package. The Facet is used throughout this design.')+'<div class="logo-board section" style="padding-top:10px">'
for file,title,desc in [('logo-facet.svg','01 / The Facet','An emerald-cut symbol with a refined wordmark. The strongest fit for a brand spanning mineral specimens, gems and jewelry.'),('logo-monogram.svg','02 / The Collector','A circular BM monogram for a more traditional luxury identity. A useful direction for jewelry boxes, seals and social avatars.')]:
 body+=f'<article><p class="eyebrow">{title}</p><img src="assets/{file}" alt="{title} logo concept"><p>{desc}</p><a class="button light" href="assets/{file}" download>Download SVG</a></article>'
body+='</div></div>';page('brand-concepts.html','Logo Concepts','Two logo directions for Black Michael Collection.',body,noindex=True)
# Local owner helper is intentionally not linked from customer navigation.
editor=(R/'assets/editor.html').read_text();page('owner-editor.html','Content Editor','Prepare JSON updates for your GitHub repository.',editor,noindex=True)
# Metadata. No fabricated production domain or live offers.
if BASE:
 urls=''.join(f'<url><loc>{E(BASE+"/"+file)}</loc></url>' for file,noindex in PAGES if not noindex and not PREVIEW)
 (D/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+urls+'</urlset>')
(D/'robots.txt').write_text('User-agent: *\nDisallow: /\n' if PREVIEW else 'User-agent: *\nAllow: /\nDisallow: /owner-editor.html\nDisallow: /content/\n'+('Sitemap: '+BASE+'/sitemap.xml\n' if BASE else ''))
print(f'Built {len(PAGES)} HTML pages in {D}. Preview mode: {PREVIEW}')
