#!/usr/bin/env python3
"""
Manage the LinkedIn posts shown on the SATs home page (assets/data/linkedin-posts.json).
No rebuild is needed - the page reads the JSON file when it loads.

How to get a post's embed code (free, official):
  LinkedIn post  ->  "..." menu  ->  "Embed this post"  ->  copy the code  (it contains <iframe src="https://www.linkedin.com/embed/feed/update/...">)

  python3 _tools/linkedin.py add  '<paste the whole <iframe ...> code OR just the src URL>'  [--title "Short label"]
  python3 _tools/linkedin.py widget elfsight <APP-ID>      # LIVE feed via a widget service (account needed)
  python3 _tools/linkedin.py widget sociablekit <EMBED-ID>
  python3 _tools/linkedin.py widget off
  python3 _tools/linkedin.py list
  python3 _tools/linkedin.py remove 2        # remove the 2nd post (numbers come from `list`)
"""
import json, os, re, sys
PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'data', 'linkedin-posts.json')
data = json.load(open(PATH, encoding='utf-8'))
cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'

def save():
    json.dump(data, open(PATH, 'w', encoding='utf-8'), indent=2, ensure_ascii=False); open(PATH, 'a').write('\n')

if cmd == 'add':
    raw = sys.argv[2] if len(sys.argv) > 2 else ''
    m = re.search(r'src=["\']([^"\']+)["\']', raw)
    url = (m.group(1) if m else raw.strip()).replace('&amp;', '&')
    if not re.match(r'^https://www\.linkedin\.com/embed/feed/update/urn:li:[A-Za-z]+:\d+', url):
        sys.exit('That does not look like a LinkedIn embed link (expected https://www.linkedin.com/embed/feed/update/urn:li:...).')
    title = sys.argv[sys.argv.index('--title') + 1] if '--title' in sys.argv else 'SATs LinkedIn post'
    if any(p['embed'] == url for p in data['posts']):
        sys.exit('Already in the list.')
    data['posts'].insert(0, {'embed': url, 'title': title}); save(); print('Added. Posts now:', len(data['posts']))
elif cmd == 'widget':
    prov = sys.argv[2] if len(sys.argv) > 2 else 'off'
    if prov == 'off': data['widget'] = None; save(); print('Widget off.')
    else:
        if prov not in ('elfsight', 'sociablekit') or len(sys.argv) < 4 or not re.match(r'^[A-Za-z0-9_-]{4,64}$', sys.argv[3]):
            sys.exit('Usage: widget elfsight|sociablekit <ID>   |   widget off')
        data['widget'] = {'provider': prov, 'id': sys.argv[3]}; save(); print('Live widget set:', prov, sys.argv[3])
elif cmd == 'remove':
    i = int(sys.argv[2]) - 1; gone = data['posts'].pop(i); save(); print('Removed:', gone['title'])
else:
    if not data['posts']: print('No posts yet - the LinkedIn section shows the profile card only.')
    for n, p in enumerate(data['posts'], 1): print(f"{n}. {p['title']}  {p['embed']}")
