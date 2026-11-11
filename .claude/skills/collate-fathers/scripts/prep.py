#!/usr/bin/env python3
"""prep.py <work.html> [--vol npnf208] [--scan ARCHIVE_ID] [--name SLUG]

Identifies the fathers2 volume a work was imported from, downloads/caches the witnesses (CCEL volume .txt and ThML
.xml, an archive.org scan of the print with per-leaf OCR), locates the work's leaves in the scan, and writes
standardization/collate/<slug>/config.json. Prints the work dir path on the last line."""
import argparse, html, json, os, re, shutil, subprocess, sys, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

UA = {'User-Agent': 'collate-fathers/1.0'}


def fetch(url, dest, binary=True):
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return dest
    import time
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=300) as r, open(dest + '.part', 'wb') as fh:
                shutil.copyfileobj(r, fh)
            os.replace(dest + '.part', dest)
            return dest
        except Exception as e:
            if attempt == 3 or getattr(e, 'code', 500) in (403, 404):
                raise
            time.sleep(5 * (attempt + 1))


def detect_vol(path):
    hs = subprocess.check_output(['git', 'log', '--follow', '--diff-filter=A', '--format=%H', '--', path],
                                 text=True).split()
    if not hs:
        sys.exit('no git history for ' + path)
    first = hs[-1]
    # the path at that commit may differ (renames): ask git for it
    names = subprocess.check_output(['git', 'log', '--follow', '--name-only', '--format=', '--', path],
                                    text=True).split('\n')
    names = [n for n in names if n.strip()]
    old = names[-1] if names else path
    head = subprocess.check_output(['git', 'show', f'{first}:{old}'], text=True, errors='replace')[:3000]
    m = re.search(r'fathers2/((?:ANF|NPNF[12])-\d\d)/', head)
    if not m:
        sys.exit('Not a CCEL fathers2-mirror import (no "fathers2/<VOL>/" in the first version header). '
                 'This skill only covers that lineage.\n' + head[:400])
    v = m.group(1)
    code = v.replace('-', '').lower()            # ANF-05 -> anf05, NPNF2-08 -> npnf208
    return code, first, head


def ia_json(url):
    req = urllib.request.Request(url, headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=120))


def candidate_scans(code):
    series = 'anf' if code.startswith('anf') else code[:5]
    vol = int(code[-2:])
    if series == 'anf':
        q = 'title:(ante-nicene) AND mediatype:texts'
    else:
        q = 'title:(nicene) AND title:(post-nicene) AND mediatype:texts'
    url = ('https://archive.org/advancedsearch.php?q=' + urllib.parse.quote(q) +
           '&fl[]=identifier&fl[]=title&fl[]=volume&fl[]=date&rows=400&output=json')
    docs = ia_json(url)['response']['docs']
    out = []
    for d in docs:
        vf = str(d.get('volume', '')) + ' ' + d['identifier']
        nums = [int(x) for x in re.findall(r'\d+', vf)]
        if vol in nums or f'{vol:02d}' in d['identifier'] or f'{vol:04d}' in d['identifier']:
            out.append(d)
    return out


def phrases(s, k=8, n=6):
    body, _ = split_notes(s)
    t = re.sub(r'<sup>.*?</sup>', ' ', body)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
    ws = re.findall(r'[A-Za-z]+', t)
    step = max(1, (len(ws) - n) // (k + 1))
    mid = [''.join(w.lower() for w in ws[i:i + n]) for i in range(step, len(ws) - n, step)][:k]
    ends = [''.join(w.lower() for w in ws[i:i + n]) for i in (12, 30, len(ws) - 40, len(ws) - n - 2) if 0 <= i < len(ws) - n]
    return mid + ends


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('html'); ap.add_argument('--vol'); ap.add_argument('--scan'); ap.add_argument('--name')
    a = ap.parse_args()
    root = repo_root()
    path = os.path.relpath(os.path.abspath(a.html), root)
    os.chdir(root)
    code, first, head = detect_vol(path)
    if a.vol:
        code = a.vol
    print('volume:', code, '(first commit', first[:8] + ')')
    cache = os.path.join(collate_root(), '_cache', code)
    os.makedirs(cache, exist_ok=True)
    txt = fetch(f'https://ccel.org/ccel/s/schaff/{code}/cache/{code}.txt', os.path.join(cache, f'{code}.txt'))
    xml = fetch(f'https://ccel.org/ccel/schaff/{code}.xml', os.path.join(cache, f'{code}.xml'))
    for p in (txt, xml):
        if os.path.getsize(p) < 100000:
            sys.exit(f'download looks wrong (too small): {p}')
    s = open(path).read()
    ph = phrases(s)

    # ---- scan
    known = json.load(open(os.path.join(SKILL, 'known_scans.json')))
    scan = a.scan or known.get(code, {}).get('id')
    extra = []
    if not scan:
        print('discovering archive.org scans ...')
        best = []
        for d in candidate_scans(code)[:12]:
            ident = d['identifier']
            try:
                p = fetch(f'https://archive.org/download/{ident}/{ident}_djvu.txt', os.path.join(cache, f'{ident}_djvu.txt'))
            except Exception as e:
                print('  skip', ident, e); continue
            nt = re.sub(r'[^a-z]', '', open(p, errors='replace').read().lower())
            score = sum(1 for x in ph if x in nt)
            print(f'  {ident:45s} {d.get("date", "")[:4]} score {score}/{len(ph)}')
            best.append((score, ident))
        best.sort(reverse=True)
        if not best or best[0][0] < max(2, len(ph) // 3):
            sys.exit('no matching scan found; pass --scan <archive.org id>')
        scan = best[0][1]
        extra = [i for sc, i in best[1:] if sc >= max(2, len(ph) // 3)][:2]
        known[code] = {'id': scan, 'extra_ocr': extra}
        save_json(known, os.path.join(SKILL, 'known_scans.json'))
        print('chose', scan, 'extra OCR:', extra, '(saved to known_scans.json)')
    else:
        extra = known.get(code, {}).get('extra_ocr', [])
    for ident in extra:
        fetch(f'https://archive.org/download/{ident}/{ident}_djvu.txt', os.path.join(cache, f'{ident}_djvu.txt'))

    pages = os.path.join(cache, 'pages_' + scan)
    if not os.path.isdir(pages) or not os.listdir(pages):
        print('downloading per-leaf OCR for', scan, '...')
        dx = fetch(f'https://archive.org/download/{scan}/{scan}_djvu.xml', os.path.join(cache, f'{scan}_djvu.xml'))
        x = open(dx, errors='replace').read()
        os.makedirs(pages, exist_ok=True)
        for i, o in enumerate(x.split('<OBJECT ')[1:]):
            lines = [' '.join(html.unescape(w) for w in re.findall(r'<WORD[^>]*>(.*?)</WORD>', ln, re.S))
                     for ln in re.findall(r'<LINE>(.*?)</LINE>', o, re.S)]
            open(os.path.join(pages, f'n{i}.txt'), 'w').write('\n'.join(lines))
        os.remove(dx)
    pn = {}
    try:
        pj = ia_json(f'https://archive.org/download/{scan}/{scan}_page_numbers.json')
        pn = {str(p['leafNum']): p.get('pageNumber') for p in pj.get('pages', []) if p.get('pageNumber')}
    except Exception as e:
        print('no page_numbers.json:', e)

    # ---- locate the work's leaves
    nleaf = len(os.listdir(pages))
    leaf_norm = {i: re.sub(r'[^a-z]', '', open(os.path.join(pages, f'n{i}.txt')).read().lower()) for i in range(nleaf)}
    hits = sorted({i for x in ph for i, t in leaf_norm.items() if x[:30] in t})
    if hits:
        lo, hi = hits[0], hits[-1]
        # widen to first/last page of the work
        lo = max(0, lo - 2); hi = min(nleaf - 1, hi + 2)
    else:
        lo, hi = 0, nleaf - 1
    print(f'work appears on leaves n{lo}..n{hi} (phrase hits: {hits})')

    slug = a.name or re.sub(r'[^A-Za-z0-9]+', '_', os.path.splitext(path)[0]).strip('_')[-80:]
    wd = os.path.join(collate_root(), slug)
    os.makedirs(os.path.join(wd, 'img'), exist_ok=True)
    if not os.path.exists(os.path.join(wd, 'orig.html')):
        shutil.copy(path, os.path.join(wd, 'orig.html'))
    cfg = dict(html=path, vol=code, first_commit=first, txt=txt, xml=xml, scan=scan, pages=pages,
               extra_ocr=[os.path.join(cache, f'{i}_djvu.txt') for i in extra],
               leaf_lo=lo, leaf_hi=hi, page_numbers=pn, cache=cache, wd=wd)
    save_json(cfg, os.path.join(wd, 'config.json'))
    print(wd)


if __name__ == '__main__':
    main()
