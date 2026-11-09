#!/usr/bin/env python3
"""Validate generated navigation, local assets, semantics and structured data."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json,sys
D=Path(__file__).resolve().parents[1]/'dist'
errors=[]; pages=list(D.glob('*.html'))
class Inspect(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=[];self.h1=0;self.title=False;self.description=False;self.schema=False;self.buf='';self.schemas=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='h1':self.h1+=1
  if tag=='title':self.title=True
  if tag=='meta' and a.get('name')=='description':self.description=bool(a.get('content'))
  if 'id' in a:self.ids.append(a['id'])
  for attr in ['href','src']:
   if a.get(attr):self.links.append(a[attr])
  if tag=='script' and a.get('type')=='application/ld+json':self.schema=True;self.buf=''
  if tag=='img' and 'alt' not in a:errors.append('Image missing alt')
 def handle_data(self,data):
  if self.schema:self.buf+=data
 def handle_endtag(self,tag):
  if tag=='script' and self.schema:self.schemas.append(json.loads(self.buf));self.schema=False
for file in pages:
 p=Inspect();p.feed(file.read_text())
 if p.h1!=1:errors.append(f'{file.name}: expected one h1, got {p.h1}')
 if not p.title or not p.description:errors.append(f'{file.name}: missing title or description')
 if len(p.ids)!=len(set(p.ids)):errors.append(f'{file.name}: duplicate ids')
 if not p.schemas:errors.append(f'{file.name}: missing schema')
 for href in p.links:
  u=urlsplit(href)
  if u.scheme or u.netloc:continue
  if u.path and not (file.parent/unquote(u.path)).exists():errors.append(f'{file.name}: missing target {href}')
  if not u.path and u.fragment and u.fragment not in p.ids:errors.append(f'{file.name}: missing anchor {href}')
if errors:print('\n'.join(errors));sys.exit(1)
print(f'PASS: {len(pages)} HTML pages; local links/assets, one h1, unique ids, metadata, image alt attributes and valid JSON-LD.')
