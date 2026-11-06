#!/usr/bin/env python3
"""Build the site: one pre-rendered page per language.

Every language used to be one page that JavaScript re-translated on click.
Search engines only ever saw the English text, so the Slovak, German, Czech and
Hungarian versions could not be found at all. Each language now gets its own
URL with the copy already in the markup:

    /            en
    /de/  /sk/  /cs/  /hu/

The template stays the single source: this reads it, swaps the text of every
[data-t] element for the chosen language, trims the dictionary down to that one
language and writes the file out as pure ASCII.
"""
import json, os, re, sys

D = os.path.dirname(os.path.abspath(__file__)) + '/'
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://suomii.vercel.app'

LANGS = ['en', 'de', 'sk', 'cs', 'hu']
CODE = {'en': 'EN', 'de': 'DE', 'sk': 'SK', 'cs': 'CZ', 'hu': 'HU'}
NAME = {'en': 'English', 'de': 'Deutsch', 'sk': 'Sloven\u010dina',
        'cs': '\u010ce\u0161tina', 'hu': 'Magyar'}
PATH = {'en': '/'}
PATH.update({l: '/%s/' % l for l in LANGS if l != 'en'})

# Who a visitor reaches, per language. 'default' is the Hungarian head office;
# a language listed here overrides it, so Slovakia can answer in Slovak.
# An empty string means "not published yet" and the row is simply left out.
CONTACT = {
    'default': {'phone': '+36 20 2636 777', 'email': ''},
    'sk':      {'phone': '',                'email': ''},   # Kornel Szabo - awaiting his details
    'de':      {'phone': '',                'email': ''},
    'cs':      {'phone': '',                'email': ''},
}


def contact(lang):
    c = dict(CONTACT['default'])
    c.update({k: v for k, v in CONTACT.get(lang, {}).items() if v})
    return c


def contact_block(lang, words):
    c, rows = contact(lang), []
    if c['phone']:
        rows.append('<div><dt class="lbl">%s</dt><dd><a href="tel:%s">%s</a></dd></div>'
                    % (words['f_phone'], c['phone'].replace(' ', ''), c['phone']))
    if c['email']:
        rows.append('<div><dt class="lbl">%s</dt><dd><a href="mailto:%s">%s</a></dd></div>'
                    % (words['f_email'], c['email'], c['email']))
    return '<dl class="contact__info">%s</dl>' % ''.join(rows)


def contact_lines(lang):
    c = contact(lang)
    out = []
    if c['phone']:
        out.append('<a href="tel:%s">%s</a>' % (c['phone'].replace(' ', ''), c['phone']))
    if c['email']:
        out.append('<a href="mailto:%s">%s</a>' % (c['email'], c['email']))
    return '<p class="foot__lines">%s</p>' % '<br>'.join(out)

src = open(D + 'suomii.template.html', encoding='utf-8').read()

# ---------------------------------------------------------------- photos ----
MANIFEST = REPO + '/img/manifest.json'
if not os.path.exists(MANIFEST):
    sys.exit('img/manifest.json missing - run python3 src/images.py')
imgs = json.load(open(MANIFEST))

# root-absolute: /de/ and friends must not look for /de/img/...
def url(rel):  return '/' + rel


def photos(out):
    for key, entry in imgs.items():
        out = out.replace('__SRC:%s__' % key, url(entry[0]['src']))
        out = out.replace('__BIG:%s__' % key, url(entry[-1]['src']))
        out = out.replace('__SET:%s__' % key,
                          ', '.join('%s %dw' % (url(e['src']), e['w']) for e in entry))
    left = re.findall(r'__(?:SRC|BIG|SET):[a-z0-9_]+__', out)
    if left:
        sys.exit('unknown photo keys: ' + ', '.join(sorted(set(left))))
    return out


# ---------------------------------------------------- the phrase book -------
# The template holds all five dictionaries; each built page keeps only its own.
T_BLOCK = re.search(r'  /\*T-START\*/\n(.*?)  /\*T-END\*/\n', src, re.S)
if not T_BLOCK:
    sys.exit('cannot find the T dictionary block')

PAIR = re.compile(r'([a-z0-9_]+):"((?:[^"\\]|\\.)*)"')


def phrasebook():
    book = {}
    for lang in LANGS:
        m = re.search(r'\n    %s:\{' % lang, T_BLOCK.group(1))
        if not m:
            sys.exit('no %s dictionary' % lang)
        rest = T_BLOCK.group(1)[m.end():]
        end = rest.index('},\n') if '},\n' in rest else rest.index('}\n')
        book[lang] = dict(PAIR.findall(rest[:end]))
    keys = set(book['en'])
    for lang in LANGS:
        missing, extra = keys - set(book[lang]), set(book[lang]) - keys
        if missing or extra:
            sys.exit('%s: missing %s extra %s' % (lang, sorted(missing), sorted(extra)))
    return book


BOOK = phrasebook()

# every [data-t] element holds plain text, so a tag-level swap is enough
EL = re.compile(r'<(\w+)([^>]*\bdata-t="([a-z0-9_]+)"[^>]*)>(.*?)</\1>', re.S)


def translate(html, words):
    def one(m):
        tag, attrs, key, body = m.groups()
        if '<' in body:
            sys.exit('nested markup inside data-t="%s"' % key)
        return '<%s%s>%s</%s>' % (tag, attrs, words.get(key, body), tag)
    out, n = EL.subn(one, html)
    if n != html.count('data-t="'):
        sys.exit('translated %d of %d elements' % (n, html.count('data-t="')))
    return out


# ------------------------------------------------------------------ head ----
LD = {
    '@context': 'https://schema.org',
    '@type': 'HomeAndConstructionBusiness',
    '@id': SITE + '/#suomii',
    'name': 'SUOMII',
    'legalName': 'Suomi Sauna Kft.',
    'description': BOOK['en']['meta_desc'],
    'url': SITE + '/',
    'logo': SITE + '/icon-512.png',
    'image': SITE + '/og.jpg',
    'foundingDate': '2005',
    'founder': {'@type': 'Person', 'name': 'Timo Nakari'},
    'telephone': '+36202636777',
    'sameAs': ['https://www.instagram.com/suomi_sauna/'],
    'address': {'@type': 'PostalAddress', 'streetAddress': 'K\u00e1nai \u00fat 3/A',
                'addressLocality': 'Budapest', 'postalCode': '1112',
                'addressCountry': 'HU'},
    'location': [
        {'@type': 'Place', 'name': 'Showroom',
         'address': {'@type': 'PostalAddress', 'streetAddress': 'K\u00e1nai \u00fat 3/A',
                     'addressLocality': 'Budapest', 'postalCode': '1112',
                     'addressCountry': 'HU'}},
        {'@type': 'Place', 'name': 'Workshop',
         'address': {'@type': 'PostalAddress', 'streetAddress': 'V\u00e1llalkoz\u00f3k \u00fatja 7',
                     'addressLocality': 'Gy\u0151r\u00fajbar\u00e1t', 'postalCode': '9081',
                     'addressCountry': 'HU'}}],
    'areaServed': [{'@type': 'Country', 'name': n} for n in
                   ('Hungary', 'Slovakia', 'Austria', 'Germany', 'Czechia')],
    'knowsLanguage': ['en', 'de', 'sk', 'cs', 'hu'],
}

OG_LOCALE = {'en': 'en_GB', 'de': 'de_DE', 'sk': 'sk_SK', 'cs': 'cs_CZ', 'hu': 'hu_HU'}


def head(lang, words):
    alts = '\n'.join('<link rel="alternate" hreflang="%s" href="%s%s">' % (l, SITE, PATH[l])
                     for l in LANGS)
    return '\n'.join([
        '<title>%s</title>' % words['meta_title'],
        '<meta name="description" content="%s">' % words['meta_desc'],
        '<link rel="canonical" href="%s%s">' % (SITE, PATH[lang]),
        alts,
        '<link rel="alternate" hreflang="x-default" href="%s/">' % SITE,
        '<link rel="icon" href="/icon.svg" type="image/svg+xml">',
        '<link rel="icon" href="/favicon.ico" sizes="32x32">',
        '<link rel="apple-touch-icon" href="/icon-180.png">',
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="SUOMII">',
        '<meta property="og:title" content="%s">' % words['meta_title'],
        '<meta property="og:description" content="%s">' % words['meta_desc'],
        '<meta property="og:url" content="%s%s">' % (SITE, PATH[lang]),
        '<meta property="og:image" content="%s/og.jpg">' % SITE,
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta property="og:locale" content="%s">' % OG_LOCALE[lang],
        '<meta name="twitter:card" content="summary_large_image">',
        '<script type="application/ld+json">%s</script>' % json.dumps(LD, ensure_ascii=False),
    ])


def langmenu(lang):
    return ''.join(
        '<li><a href="%s" hreflang="%s"%s>%s<span class="code">%s</span></a></li>'
        % (PATH[l], l, ' aria-current="true"' if l == lang else '', NAME[l], CODE[l])
        for l in LANGS)


def langchips(lang):
    return ''.join(
        '<a href="%s" hreflang="%s"%s>%s</a>'
        % (PATH[l], l, ' aria-current="true"' if l == lang else '', CODE[l])
        for l in LANGS)


# ----------------------------------------------------------------- build ----
markup_esc = lambda s: ''.join(c if ord(c) < 128 else '&#%d;' % ord(c) for c in s)
js_esc = lambda s: ''.join(c if ord(c) < 128 else '\\u%04x' % ord(c) for c in s)


def render(lang):
    words = BOOK[lang]
    out = src

    # one dictionary instead of five
    out = (out[:T_BLOCK.start()]
           + '  var T = ' + json.dumps(words, ensure_ascii=False, sort_keys=True) + ';\n'
           + out[T_BLOCK.end():])

    out = out.replace('__HEAD__', head(lang, words))
    out = out.replace('__LANGMENU__', langmenu(lang))
    out = out.replace('__LANGCHIPS__', langchips(lang))
    out = out.replace('__CONTACTINFO__', contact_block(lang, words))
    out = out.replace('__FOOTCONTACT__', contact_lines(lang))
    out = out.replace('__LANGCODE__', CODE[lang])
    out = out.replace('__LANG__', lang)
    out = translate(out, words)

    # the <script> needs \uXXXX, the markup needs &#NNN;
    m = re.search(r'(<script>)(.*?)(</script>)', out, re.S)
    if not m:
        sys.exit('no <script> block found')
    out = markup_esc(out[:m.start(2)]) + js_esc(m.group(2)) + markup_esc(out[m.end(2):])

    STYLE_END = '</style>'
    i = out.index(STYLE_END) + len(STYLE_END)
    out = ('<!DOCTYPE html>\n<html lang="%s">\n<head>\n' % lang
           + '<meta charset="utf-8">\n'
           + '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
           + '<meta name="theme-color" content="#0f1f2e">\n'
           + out[:i] + '\n</head>\n<body>' + out[i:] + '\n</body>\n</html>\n')

    out = photos(out)

    left = re.findall(r'__[A-Z0-9_]+__', out)
    if left:
        sys.exit('unfilled tokens: ' + ', '.join(sorted(set(left))))
    assert out.isascii(), 'non-ASCII survived escaping'
    return out


total = 0
for lang in LANGS:
    html = render(lang)
    path = REPO + ('/index.html' if lang == 'en' else '/%s/index.html' % lang)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='ascii').write(html)
    total += len(html)
    print('  %-3s %-22s %6.1f KB' % (lang, PATH[lang], len(html) / 1024))

# ------------------------------------------------------- robots + sitemap ---
open(REPO + '/robots.txt', 'w').write(
    'User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % SITE)

urls = []
for lang in LANGS:
    alts = '\n'.join(
        '    <xhtml:link rel="alternate" hreflang="%s" href="%s%s"/>' % (l, SITE, PATH[l])
        for l in LANGS)
    urls.append('  <url>\n    <loc>%s%s</loc>\n%s\n'
                '    <xhtml:link rel="alternate" hreflang="x-default" href="%s/"/>\n'
                '  </url>' % (SITE, PATH[lang], alts, SITE))
open(REPO + '/sitemap.xml', 'w').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
    '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
    + '\n'.join(urls) + '\n</urlset>\n')

print('built %d pages, %.2f MB total - pure ASCII, sitemap and robots written'
      % (len(LANGS), total / 1024 / 1024))
