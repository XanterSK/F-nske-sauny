#!/usr/bin/env python3
"""Build suomii.html: escape all non-ASCII, then inject the base64 images."""
import json, os, re, shutil, sys

D = os.path.dirname(os.path.abspath(__file__)) + '/'
REPO    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT = REPO + '/index.html'

src = open(D + 'suomii.template.html', encoding='utf-8').read()

# --- split off the <script> block: it needs \uXXXX, the rest needs &#NNN; ---
m = re.search(r'(<script>)(.*?)(</script>)', src, re.S)
if not m:
    sys.exit('no <script> block found')

head, js, tail = src[:m.start(2)], m.group(2), src[m.end(2):]

markup_esc = lambda s: ''.join(c if ord(c) < 128 else '&#%d;' % ord(c) for c in s)
js_esc     = lambda s: ''.join(c if ord(c) < 128 else '\\u%04x' % ord(c) for c in s)

out = markup_esc(head) + js_esc(js) + markup_esc(tail)

# --- wrap in a real document ---
# Without a doctype browsers fall into quirks mode, and without the viewport
# meta a phone lays the page out at ~980px and shrinks it. Both were missing.
STYLE_END = '</style>'
i = out.index(STYLE_END) + len(STYLE_END)
head_html, body_html = out[:i], out[i:]
out = ('<!DOCTYPE html>\n<html lang="en">\n<head>\n'
       '<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
       '<meta name="theme-color" content="#0f1f2e">\n'
       '<meta name="description" content="SUOMII - bespoke Finnish saunas, handmade in Hungary since 2005.">\n'
       + head_html + '\n</head>\n<body>' + body_html + '\n</body>\n</html>\n')

# --- photos: real files in img/, two widths each (see src/images.py) ---
MANIFEST = REPO + '/img/manifest.json'
if not os.path.exists(MANIFEST):
    sys.exit('img/manifest.json missing - run python3 src/images.py')
imgs = json.load(open(MANIFEST))

def small(key): return imgs[key][0]['src']
def big(key):   return imgs[key][-1]['src']
def srcset(key): return ', '.join('%s %dw' % (e['src'], e['w']) for e in imgs[key])

for key in imgs:
    out = out.replace('__SRC:%s__' % key, small(key))
    out = out.replace('__BIG:%s__' % key, big(key))
    out = out.replace('__SET:%s__' % key, srcset(key))
left_img = re.findall(r'__(?:SRC|BIG|SET):[a-z0-9_]+__', out)
if left_img:
    sys.exit('unknown photo keys: ' + ', '.join(sorted(set(left_img))))
# small assets kept in the repo (the logo): src/assets/logo.png -> __LOGO__
import base64
AS = D + 'assets/'
for f in sorted(os.listdir(AS)) if os.path.isdir(AS) else []:
    token = '__%s__' % os.path.splitext(f)[0].upper()
    if token not in out:
        sys.exit('template never uses ' + token)
    out = out.replace(token, base64.b64encode(open(AS + f, 'rb').read()).decode('ascii'))

left = re.findall(r'__[A-Z0-9_]+__', out)
if left:
    sys.exit('unfilled tokens: ' + ', '.join(sorted(set(left))))

assert out.isascii(), 'non-ASCII survived escaping'


# index.html at the repo root: Vercel serves it with no config at all
open(PROJECT, 'w', encoding='ascii').write(out)

print('built %.2f MB - pure ASCII, charset declared' % (len(out) / 1024 / 1024))
