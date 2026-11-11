#!/usr/bin/env python3
"""merge.py <wd> [--review-prep]

Merges <wd>/packets/d*.json into <wd>/merged.json (checking every packet item is decided exactly once), then applies
any adversarial-review overrides from <wd>/review/r*.json and collects their structural findings into
<wd>/review/structural.json. Keeps manual entries already in merged.json under "markers".

--review-prep: also writes review inputs: review/q{K}.json (decisions without reasoning), review/sample{K}.json
(~25% random sample of non-custom decisions + all customs), review/after.html (preview build), review/BRIEF.md."""
import glob, json, os, random, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

wd = os.path.abspath(sys.argv[1]); prep = '--review-prep' in sys.argv
cfg = load_cfg(wd)
mp = os.path.join(wd, 'merged.json')
old = json.load(open(mp)) if os.path.exists(mp) else {}
M = {'body': {}, 'notes': {}, 'markers': old.get('markers', {}), 'hand': old.get('hand', {})}
ok = True
for p in sorted(glob.glob(os.path.join(wd, 'packets', 'p*.json'))):
    k = re.search(r'p(\d+)\.json$', p).group(1)
    P = json.load(open(p)); dp = os.path.join(wd, 'packets', f'd{k}.json')
    if not os.path.exists(dp):
        print('MISSING decisions', dp); ok = False; continue
    D = json.load(open(dp))
    ids = {b['id'] for b in P['body']}; keys = {n['key'] for n in P['notes']}
    mb, xb = ids - set(D.get('body', {})), set(D.get('body', {})) - ids
    mn, xn = keys - set(D.get('notes', {})), set(D.get('notes', {})) - keys
    if mb or xb or mn or xn:
        ok = False; print(f'packet {k}: undecided body {sorted(mb)} notes {sorted(mn)}; stray body {sorted(xb)} notes {sorted(xn)}')
    M['body'].update({i: v for i, v in D.get('body', {}).items() if i in ids})
    M['notes'].update({i: v for i, v in D.get('notes', {}).items() if i in keys})
# review overrides
structural, nover = [], 0
for r in sorted(glob.glob(os.path.join(wd, 'review', 'r*.json'))):
    R = json.load(open(r))
    for sect in ('body', 'notes'):
        for i, v in R.get('overrides', {}).get(sect, {}).items():
            if i in M[sect] and M[sect][i] != v:
                print(f'override {os.path.basename(r)} {sect} {i}: {M[sect][i]!r} -> {v!r}'); M[sect][i] = v; nover += 1
    structural += [dict(src=os.path.basename(r), **x) for x in R.get('structural', [])]
save_json(M, mp)
if structural or glob.glob(os.path.join(wd, 'review', 'r*.json')):
    save_json(structural, os.path.join(wd, 'review', 'structural.json'))
print(f"merged: {len(M['body'])} body, {len(M['notes'])} notes decisions; {nover} review overrides; {len(structural)} structural findings"
      + ('' if ok else '  -- INCOMPLETE'))

if prep:
    rv = os.path.join(wd, 'review'); os.makedirs(rv, exist_ok=True)
    random.seed(7)
    for p in sorted(glob.glob(os.path.join(wd, 'packets', 'p*.json'))):
        k = re.search(r'p(\d+)\.json$', p).group(1); P = json.load(open(p))
        q = {'body': {b['id']: M['body'].get(b['id']) for b in P['body']},
             'notes': {n['key']: M['notes'].get(n['key']) for n in P['notes']}, 'leaves': P['leaves']}
        save_json(q, os.path.join(rv, f'q{k}.json'))
        std = ('ccel', 'ours', 'thml')
        samp = {'body': [i for i, v in q['body'].items() if v not in std] + [i for i, v in q['body'].items() if v in std and random.random() < .25],
                'notes': [i for i, v in q['notes'].items() if v not in std] + [i for i, v in q['notes'].items() if v in std and random.random() < .25]}
        save_json(samp, os.path.join(rv, f'sample{k}.json'))
    subprocess.run([sys.executable, os.path.join(SKILL, 'scripts', 'build.py'), wd, os.path.join(rv, 'after.html')], check=True)
    b = open(os.path.join(SKILL, 'REVIEW_BRIEF.md')).read()
    b = b.replace('{WD}', wd).replace('{SCRIPTS}', os.path.join(SKILL, 'scripts')).replace('{SCAN}', cfg['scan'])
    open(os.path.join(rv, 'BRIEF.md'), 'w').write(b)
    print('review inputs written to', rv)
