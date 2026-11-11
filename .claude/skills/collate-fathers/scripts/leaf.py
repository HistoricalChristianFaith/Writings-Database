#!/usr/bin/env python3
"""Print-scan helper for adjudicators.

  leaf.py <wd> --find "a few words"        leaves whose OCR contains the words (letters-only match, OCR-tolerant)
  leaf.py <wd> --text LEAF                 print that leaf's OCR text
  leaf.py <wd> LEAF [x0 y0 x1 y1]          download the page image (cached) and write a crop (fractions 0-1;
                                           default = whole page) to <wd>/img/; prints the path to Read
"""
import os, re, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_cfg

wd = os.path.abspath(sys.argv[1]); cfg = load_cfg(wd); args = sys.argv[2:]
if args[0] == '--find':
    q = re.sub(r'[^a-z]', '', ' '.join(args[1:]).lower())
    hits = []
    for f in sorted(os.listdir(cfg['pages']), key=lambda f: int(f[1:-4])):
        t = re.sub(r'[^a-z]', '', open(os.path.join(cfg['pages'], f)).read().lower())
        if q in t:
            hits.append(f[:-4])
    if not hits and len(q) > 24:      # OCR noise: try halves
        for half in (q[:len(q) // 2], q[len(q) // 2:]):
            for f in os.listdir(cfg['pages']):
                if half in re.sub(r'[^a-z]', '', open(os.path.join(cfg['pages'], f)).read().lower()):
                    hits.append(f[:-4] + '(partial)')
    pn = cfg.get('page_numbers', {})
    print(' '.join(f"{h} (p.{pn.get(h.strip('n').split('(')[0], '?')})" for h in hits) or 'no hit')
    sys.exit()
if args[0] == '--text':
    print(open(os.path.join(cfg['pages'], f'n{int(args[1])}.txt')).read()); sys.exit()
leaf = int(args[0])
box = [float(v) for v in args[1:5]] if len(args) >= 5 else [0, 0, 1, 1]
imgdir = os.path.join(cfg['cache'], 'img_' + cfg['scan']); os.makedirs(imgdir, exist_ok=True)
src = os.path.join(imgdir, f'n{leaf}.jpg')
if not os.path.exists(src):
    url = f"https://archive.org/download/{cfg['scan']}/page/n{leaf}_w1600.jpg"
    req = urllib.request.Request(url, headers={'User-Agent': 'collate-fathers/1.0'})
    data = urllib.request.urlopen(req, timeout=120).read()
    open(src, 'wb').write(data)
from PIL import Image
im = Image.open(src); W, H = im.size
c = im.crop((int(box[0] * W), int(box[1] * H), int(box[2] * W), int(box[3] * H)))
if c.width > 1600:
    c = c.resize((1600, int(c.height * 1600 / c.width)))
out = os.path.join(wd, 'img', f'n{leaf}_' + '_'.join(f'{v:.2f}' for v in box) + '.jpg')
c.save(out, quality=88)
print(out)
