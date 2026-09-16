#!/usr/bin/env python3
"""Resize the chosen photos into img/ and write img/manifest.json.

Every photo used on the site is written at two widths so phones download the
small one. The photo library is git-ignored, so this runs only on a machine
that has it; img/ and the manifest are committed, so the build works anywhere.

Note: the LA PANCA folder name contains a NON-BREAKING SPACE (\xa0), not a
normal space - that silently broke every shell glob until we caught it.
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB  = os.path.join(ROOT, 'CABIN DESIGNS')
OUT  = os.path.join(ROOT, 'img')

# key -> (path inside CABIN DESIGNS, [widths], jpeg quality)
PHOTOS = {
    'hero':    ('CLASSIC/Classic PR red ceder.jpeg', [900, 1800], 60),
    'atelier': ('SPECIAL/Special Lights.jpeg',       [900, 1800], 58),

    'classic': ('CLASSIC/Classic GB red ceder.jpeg', [700, 1400], 60),
    'lapanca': ('LA\xa0PANCA/Panca PG2.jpeg',        [700, 1400], 60),
    'massivo': ('MASSIVO/Massivo wood burning.jpeg', [700, 1400], 60),
    'dal':     ('DAL/Dal hidden stove.jpeg',         [700, 1400], 60),
    'tom':     ('TOM/Tom red ceder4.jpeg',           [700, 1400], 60),

    # three more shots per design, for the gallery in the detail window
    'classic_x1': ('CLASSIC/Classic red ceder3.jpeg',    [700, 1200], 58),
    'classic_x2': ('CLASSIC/Classic pool alder120.jpeg', [700, 1200], 58),
    'classic_x3': ('CLASSIC/Classic radiata pine.jpeg',  [700, 1200], 58),
    'lapanca_x1': ('LA\xa0PANCA/Panca Schön2.jpeg',      [700, 1200], 58),
    'lapanca_x2': ('LA\xa0PANCA/Panca PG3.jpeg',         [700, 1200], 58),
    'lapanca_x3': ('LA\xa0PANCA/Panca BA.jpeg',          [700, 1200], 58),
    'massivo_x1': ('MASSIVO/Massivo bench.jpeg',         [700, 1200], 58),
    'massivo_x2': ('MASSIVO/Massivo München.jpeg',       [700, 1200], 58),
    'massivo_x3': ('MASSIVO/Massivo Fuchs.jpeg',         [700, 1200], 58),
    'dal_x1':     ('DAL/Dal white.jpeg',                 [700, 1200], 58),
    'dal_x2':     ('DAL/Dal step.jpeg',                  [700, 1200], 58),
    'dal_x3':     ('DAL/Dal rounded bench.jpeg',         [700, 1200], 58),
    'tom_x1':     ('TOM/Tom Lights.jpeg',                [700, 1200], 58),
    'tom_x2':     ('TOM/Tom Finger Ceiling.jpeg',        [700, 1200], 58),
    'tom_x3':     ('TOM/Tom Black Glass.jpeg',           [700, 1200], 58),

    # references: delivered saunas, indoor and outdoor
    'ref1': ('OUTDOOR/Outdoor Pool.jpeg',            [600, 1200], 58),
    'ref2': ('SPECIAL/Special Bp.jpeg',              [600, 1200], 58),
    'ref3': ('OUTDOOR/Outdoor Balaton.jpeg',         [600, 1200], 58),
    'ref4': ('OUTDOOR/Outdoor hotel red ceder.jpeg', [600, 1200], 58),
    'ref5': ('OUTDOOR/Outdoor Larch.jpeg',           [600, 1200], 58),
    'ref6': ('SPECIAL/Special Banya.jpeg',           [600, 1200], 58),
}

# already-square portrait cropped by hand, next to the source
LOCAL = {
    'timo': (os.path.join(ROOT, 'src', 'portraits', 'timo.jpg'), [220], 72),
}


def resize(src, dst, width, quality):
    subprocess.run(['sips', '-Z', str(width), '-s', 'format', 'jpeg',
                    '-s', 'formatOptions', str(quality), src, '--out', dst],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest, total = {}, 0

    jobs = [(k, os.path.join(LIB, rel), w, q) for k, (rel, w, q) in PHOTOS.items()]
    jobs += [(k, path, w, q) for k, (path, w, q) in LOCAL.items()]

    for key, src, widths, quality in jobs:
        if not os.path.exists(src):
            sys.exit('missing photo: ' + src)
        entry = []
        for w in widths:
            name = '%s-%d.jpg' % (key, w)
            dst = os.path.join(OUT, name)
            resize(src, dst, w, quality)
            total += os.path.getsize(dst)
            entry.append({'src': 'img/' + name, 'w': w})
        manifest[key] = entry

    with open(os.path.join(OUT, 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
    print('wrote %d files, %.1f MB into img/' % (sum(len(v) for v in manifest.values()), total / 1024 / 1024))


if __name__ == '__main__':
    main()
