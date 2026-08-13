#!/usr/bin/env python3
"""Build suomii.html: escape all non-ASCII, then inject the base64 images."""
import json, re, shutil, sys

D = '/private/tmp/claude-501/-Users-sebastianchristenko-Downloads-Finske-sauny-Kornel/9de086df-84b4-4cbd-a56a-d1aa9d4cfec1/scratchpad/'
REPO    = '/Users/sebastianchristenko/Downloads/Finske sauny Kornel'
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

# charset must land inside the first 1024 bytes to be honoured
out = '<meta charset="utf-8">\n' + out

# --- inject images ---
imgs = json.load(open('/tmp/sauna_build/images.json'))
for key in imgs:
    token = '__%s__' % key.upper()
    if token not in out:
        sys.exit('template never uses ' + token)
    out = out.replace(token, imgs[key])
left = re.findall(r'__[A-Z0-9_]+__', out)
if left:
    sys.exit('unfilled tokens: ' + ', '.join(sorted(set(left))))

assert out.isascii(), 'non-ASCII survived escaping'

import os
open(D + 'suomii.html', 'w', encoding='ascii').write(out)

# index.html at the repo root: Vercel serves it with no config at all
shutil.copy(D + 'suomii.html', PROJECT)

# keep the editable source in the repo too
src = os.path.join(REPO, 'src')
os.makedirs(src, exist_ok=True)
shutil.copy(D + 'suomii.template.html', os.path.join(src, 'suomii.template.html'))
shutil.copy(D + 'build.py', os.path.join(src, 'build.py'))
print('built %.2f MB - pure ASCII, charset declared' % (len(out) / 1024 / 1024))
