#!/usr/bin/env python3
"""Resize the chosen photos and cache them as base64 for build.py.

The photo library is git-ignored, so this runs only on a machine that has it.
Note: the LA PANCA folder name contains a NON-BREAKING SPACE (\xa0), not a
normal space - that silently broke every shell glob until we caught it.
"""
import base64, json, os, subprocess, sys

LIB   = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'CABIN DESIGNS')
CACHE = '/tmp/sauna_build/images.json'

# key -> (path relative to CABIN DESIGNS, max edge px, jpeg quality)
MAIN = {
    'hero':    ('CLASSIC/Classic PR red ceder.jpeg',   0,    68),  # 0 = keep native size
    'atelier': ('SPECIAL/Special Lights.jpeg',         1400, 64),
    'classic': ('CLASSIC/Classic GB red ceder.jpeg',   1250, 64),
    'lapanca': ('LA\xa0PANCA/Panca PG2.jpeg',          1250, 64),
    'massivo': ('MASSIVO/Massivo wood burning.jpeg',   1250, 64),
    'dal':     ('DAL/Dal hidden stove.jpeg',           1250, 64),
    'tom':     ('TOM/Tom red ceder4.jpeg',             1250, 64),
}

# three more shots per design, for the gallery in the detail window
EXTRA = {
    'classic': ['CLASSIC/Classic red ceder3.jpeg',
                'CLASSIC/Classic pool alder120.jpeg',
                'CLASSIC/Classic radiata pine.jpeg'],
    'lapanca': ['LA\xa0PANCA/Panca Schön2.jpeg',
                'LA\xa0PANCA/Panca PG3.jpeg',
                'LA\xa0PANCA/Panca BA.jpeg'],
    'massivo': ['MASSIVO/Massivo bench.jpeg',
                'MASSIVO/Massivo München.jpeg',
                'MASSIVO/Massivo Fuchs.jpeg'],
    'dal':     ['DAL/Dal white.jpeg',
                'DAL/Dal step.jpeg',
                'DAL/Dal rounded bench.jpeg'],
    'tom':     ['TOM/Tom Lights.jpeg',
                'TOM/Tom Finger Ceiling.jpeg',
                'TOM/Tom Black Glass.jpeg'],
}


def encode(rel, edge, quality):
    src = os.path.join(LIB, rel)
    if not os.path.exists(src):
        sys.exit('missing photo: ' + rel)
    tmp = '/tmp/sauna_build/_t.jpg'
    cmd = ['sips']
    if edge:
        cmd += ['-Z', str(edge)]
    cmd += ['-s', 'format', 'jpeg', '-s', 'formatOptions', str(quality), src, '--out', tmp]
    subprocess.run(cmd, check=True, capture_output=True)
    return base64.b64encode(open(tmp, 'rb').read()).decode()


def main():
    os.makedirs('/tmp/sauna_build', exist_ok=True)
    out = {}
    for key, (rel, edge, q) in MAIN.items():
        out[key] = encode(rel, edge, q)
    for design, rels in EXTRA.items():
        for n, rel in enumerate(rels, 1):
            out['%s_x%d' % (design, n)] = encode(rel, 1000, 60)
    json.dump(out, open(CACHE, 'w'))
    total = sum(len(v) for v in out.values()) / 1024 / 1024
    print('cached %d images, %.2f MB of base64 -> %s' % (len(out), total, CACHE))


if __name__ == '__main__':
    main()
